"""Verification-only dense active-set refinement; NEVER used for economic scoring."""
import numpy as np


def wrap_allocator(original):
    def polished(mu,held,d,B,L,beta,kappa,gamma,cap,**kwargs):
        w=original(mu,held,d,B,L,beta,kappa,gamma,cap,**kwargs)
        mu,h,dd,b,k=map(lambda x:np.asarray(x,dtype=float),(mu,held,d,beta,kappa))
        caps=np.broadcast_to(np.asarray(cap,dtype=float),w.shape)
        M=np.asarray(B)@np.asarray(L);Q=gamma*(np.diag(dd)+M@M.T)
        target=float(kwargs.get('beta_target',0.))
        fixed=(w==h)|(w==-caps)|(w==caps);free=~fixed
        if not free.any():return w
        indices=np.where(free)[0];q=Q[np.ix_(free,free)];bf=b[free]
        rhs=mu[free]-Q[np.ix_(free,fixed)]@w[fixed]-k[free]*np.sign(w[free]-h[free])
        if np.max(np.abs(bf),initial=0)>1e-15:
            A=np.block([[q,bf[:,None]],[bf[None,:],np.zeros((1,1))]])
            sol=np.linalg.solve(A,np.r_[rhs,target-b[fixed]@w[fixed]])
            refined=w.copy();refined[free]=sol[:-1];nu=sol[-1]
        else:
            refined=w.copy();refined[free]=np.linalg.solve(q,rhs);nu=0.
        grad=mu-Q@refined-nu*b
        # Do not permit any region changes, constraint violations or large KKT residual.
        assert np.all(np.sign(refined[free]-h[free])==np.sign(w[free]-h[free])),'wrong trade region'
        assert np.all(np.abs(refined)<=caps+1e-12),'polished cap'
        assert abs(b@refined-target)<1e-10,'polished beta'
        assert np.max(np.abs(grad[free]-k[free]*np.sign(refined[free]-h[free])),initial=0)<1e-12,'polished stationarity'
        nt=(w==h)&(np.abs(w)<caps)
        assert np.all(np.abs(grad[nt])<=k[nt]+1e-12),'polished no-trade KKT'
        up=(w==caps)&(w!=h);dn=(w==-caps)&(w!=h)
        assert np.all((grad-k*np.sign(w-h))[up]>=-1e-12),'polished upper KKT'
        assert np.all((grad-k*np.sign(w-h))[dn]<=1e-12),'polished lower KKT'
        return refined
    return polished

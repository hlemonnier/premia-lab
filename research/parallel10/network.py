"""Stable directed residual lag regressions and the own-history matched control."""
import numpy as np
from .core import BasePolicy,ew_level,design,cap_increment


def correlation(A,B):
    a=A-A.mean(0);b=B-B.mean(0)
    sx=np.maximum(np.sqrt(np.mean(a*a,0)),1e-8);sy=np.maximum(np.sqrt(np.mean(b*b,0)),1e-8)
    return (a.T@b/len(a))/(sx[:,None]*sy[None,:]),sx,sy


class NetworkPolicy(BasePolicy):
    def forecast(self,returns_history,characteristics_history):
        R,X,base,S=self.inputs(returns_history,characteristics_history);T,N=R.shape
        z=np.zeros((T,N));z[1:]=np.clip(S['u'][1:]/np.sqrt(S['d'][:-1]),-6,6)
        x=ew_level(z,5);out=np.array(base,copy=True);own=np.zeros(N);B=np.zeros((N,N));xm=np.zeros(N)
        for t in range(505,T):
            if (t-505)%126==0:
                labels=np.arange(t-504,t);A=x[labels-1];Y=z[labels]
                rho,sx,sy=correlation(A,Y);r1,_,_=correlation(A[:252],Y[:252]);r2,_,_=correlation(A[252:],Y[252:])
                threshold=3/np.sqrt(504);valid=(r1*r2>0)&(np.abs(rho)>threshold)
                shrink=np.sign(rho)*np.maximum(np.abs(rho)-threshold,0);slopes=shrink*sy[None,:]/sx[:,None]
                slopes=np.where(valid,slopes,0);own=np.clip(np.diag(slopes),-.25,.25)
                np.fill_diagonal(slopes,0);np.fill_diagonal(rho,0)
                if N>5:
                    scores=np.where(valid,np.abs(rho),0.);np.fill_diagonal(scores,0.)
                    kth=np.partition(scores,N-5,axis=0)[N-5];slopes=np.where(scores>=kth[None,:],slopes,0)
                B=slopes*np.minimum(1.,.25/np.maximum(np.sum(np.abs(slopes),axis=0),1e-30))[None,:]
                xm=A.mean(0)
                self.records.append(dict(target_row=t,last_label=t-1,edges=int(np.count_nonzero(B)),own=int(np.count_nonzero(own)),maximum_cross_L1=float(np.abs(B).sum(0).max()),self_edges=float(np.diag(B).max(initial=0))))
            normalized=(x[t-1]-xm)*own
            if self.mode=='N':normalized=normalized+(x[t-1]-xm)@B
            extra=np.sqrt(S['d'][t-1])*normalized
            D=np.column_stack([np.ones(N),design(X,S['beta'],t-1,self.cfg)])
            extra-=D@np.linalg.solve(D.T@D/N+1e-8*np.eye(28),D.T@extra/N)
            out[t,:N]+=cap_increment(extra,base[t,:N])
        self.forecast_output=out;return out

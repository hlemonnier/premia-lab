"""The frozen GLS learner with only the matured response treatment changed."""
import numpy as np
from model_f import engine as E
from .core import BasePolicy


class RobustPolicy(BasePolicy):
    def forecast(self,returns_history,characteristics_history):
        R,X,base,S=self.inputs(returns_history,characteristics_history);T,N=R.shape;cfg=self.cfg
        beta=S['beta'];market=S['market'];state=E._RiskState(N,26,cfg)
        grams=[np.zeros((27,27)),np.zeros((27,27))];moments=[np.zeros(27),np.zeros(27)];masses=[0.,0.]
        decays=(2**(-1/1008),2**(-1/252));out=np.array(base,copy=True);pairs=0;ones=np.ones(N)
        clipped=total=dates_scaled=0
        for t in range(65,T):
            u=t-1
            while state.upto<u:state.absorb(R,X,state.upto)
            L,d=state.model();L=L/np.sqrt(cfg['factor_risk_scale']);L=np.sqrt(base[u,N+1:])[:,None]*L
            D=np.hstack([E.basis(X[u-1],cfg['feature_clip']),E._zcol(beta[u],cfg['feature_clip'])[:,None]])
            y=R[u]-beta[u]*market[u];M=D[:,:26]@L;sigma=np.sqrt(d+np.sum(M*M,axis=1));scaled=y/sigma
            clipped+=int(np.sum(np.abs(scaled)>3));total+=N
            if self.mode=='R':y=sigma*np.clip(scaled,-3,3)
            else:
                a=min(1.,3/max(float(np.sqrt(np.mean(scaled*scaled))),1e-30));y=y*a;dates_scaled+=int(a<1)
            V=np.column_stack([ones,D,y]);Vi=V/d[:,None];Mi=M/d[:,None]
            pV=[redacted-email](np.eye(26)+M.T@Mi,M.T@Vi);normalizer=float(np.sum(pV[:,0]))
            if not np.isfinite(normalizer) or normalizer<=0:raise RuntimeError('nonpositive precision')
            projected=pV[:,1:]-pV[:,0,None]*(np.sum(pV[:,1:],axis=0)/normalizer)[None,:]
            g=D.T@projected[:,:27]/N;g=.5*(g+g.T);h=D.T@projected[:,27]/N;pairs+=1
            for k,dec in enumerate(decays):grams[k]=dec*grams[k]+g;moments[k]=dec*moments[k]+h;masses[k]=dec*masses[k]+1
            if t<253 or pairs<126:continue
            coef=[]
            for k in range(2):
                g=grams[k]/masses[k];v=moments[k]/masses[k];floor=1e-12*max(float(np.diag(g).mean()),1e-12)
                coef.append(np.linalg.solve(g+cfg['ridge']*np.diag(np.maximum(np.diag(g),floor)),v))
            combined=coef[0].copy();combined[:13]=.5*coef[0][:13]+.5*coef[1][:13]
            Dnew=np.hstack([E.basis(X[t-1],cfg['feature_clip']),E._zcol(beta[t],cfg['feature_clip'])[:,None]])
            out[t,:N]=.5*S['f2'][t]+.5*(Dnew@combined)
            if (t-253)%126==0:self.records.append(dict(target_row=t,last_label=u,covariance_last_row=u-1,clipped_stock_fraction=clipped/total,date_scaling_count=dates_scaled))
        self.forecast_output=out;return out

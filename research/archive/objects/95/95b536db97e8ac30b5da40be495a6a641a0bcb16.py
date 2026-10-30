"""Cross-factor surprise dynamics, with a diagonal-only matched control."""
import numpy as np
from model_f import engine as E
from .core import BasePolicy,ew_level,cap_increment


class FactorVARPolicy(BasePolicy):
    def forecast(self,returns_history,characteristics_history):
        R,X,base,S=self.inputs(returns_history,characteristics_history);T,N=R.shape
        z=np.zeros((T,26));z[1:]=np.clip(S['f'][1:]/np.sqrt(S['q'][:-1]),-6,6);x=ew_level(z,21)
        surprise=np.zeros((T,26))
        for s in range(1,T-1):
            D=E.basis(X[s-1],self.cfg['feature_clip']);mu=np.linalg.solve(D.T@D/N+1e-10*np.eye(26),D.T@base[s,:N]/N)
            surprise[s]=(S['f'][s]-mu)/np.sqrt(S['q'][s-1])
        out=np.array(base,copy=True);B=np.zeros((26,26));xm=np.zeros(26);ym=np.zeros(26)
        for t in range(505,T):
            if (t-505)%21==0:
                labels=np.arange(t-504,t);A=x[labels-1];Y=surprise[labels]
                xm=A.mean(0);ym=Y.mean(0);A=A-xm;Y=Y-ym
                gram=A.T@A/504;h=A.T@Y/504;ridge=np.maximum(np.diag(gram),1e-8)
                B=np.linalg.solve(gram+np.diag(ridge),h) if self.mode=='V' else np.diag(np.diag(h)/(np.diag(gram)+ridge))
                self.records.append(dict(target_row=t,last_label=t-1,coefficient_norm=float(np.linalg.norm(B))))
            factor_delta=((x[t-1]-xm)@B+ym)*np.sqrt(S['q'][t-1]);extra=E.basis(X[t-1],self.cfg['feature_clip'])@factor_delta
            out[t,:N]+=cap_increment(extra,base[t,:N])
        self.forecast_output=out;return out

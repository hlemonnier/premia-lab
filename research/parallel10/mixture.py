"""Loss-trained shrunk forecast mixing, not a reward-trained trading agent."""
import numpy as np
from .core import BasePolicy,marginal


class MixturePolicy(BasePolicy):
    def forecast(self,returns_history,characteristics_history):
        R,X,base,S=self.inputs(returns_history,characteristics_history);T,N=R.shape
        out=np.array(base,copy=True);slow=S['f2'];pure=2*base[:,:N]-slow
        numerator=denominator=0.;decay=2**(-1/1008);count=0;weight=.5
        for t in range(254,T):
            label=t-1;a=pure[label]-slow[label];b=R[label]-S['beta'][label]*S['market'][label]-slow[label]
            weights=1/marginal(label-1,X,S,self.cfg) if self.mode=='M' else np.ones(N);weights/=weights.mean()
            numerator=decay*numerator+float(np.mean(weights*a*b));denominator=decay*denominator+float(np.mean(weights*a*a));count+=1
            if count>=504 and (t-757)%21==0:
                weight=float(np.clip(.5*(numerator/max(denominator,1e-20)+.5),.25,.75))
                self.records.append(dict(target_row=t,last_label=label,training_pairs=count,weight=weight))
            # Preserve exact baseline arithmetic until the first fitted update.
            if count>=504:out[t,:N]=(1-weight)*slow[t]+weight*pure[t]
        self.forecast_output=out;return out

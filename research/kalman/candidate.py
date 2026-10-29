"""K: causal Gaussian random-walk premium filter with fixed noise calibration.

Only the GLS half of GC's forecast changes. Process noise is derived from the
registered scalar steady-state gain, not selected against portfolio performance.
No smoothing or maximum-likelihood search over the provided history occurs.
"""
from __future__ import annotations
import numpy as np
from research.gcorr.correlation_reference import CandidatePolicy as CorrelationPolicy
from research.estimation.likelihood import likelihoods,symmetric_pinv


def kalman_forecast(R,X,baseline,cfg):
    T,N=np.shape(R);out=baseline[:,:N].copy();records=[];eye=np.eye(27)
    mean=np.zeros(27);P=None;noise_sum=np.zeros(27);mass=0.;decay=2.**(-1./1008.)
    half_lives=np.r_[np.full(13,504.),np.full(14,1008.)]
    gain=1.-2.**(-1./half_lives);process_ratio=gain*gain/(1.-gain)
    postvar=np.zeros((T,27));processvar=np.zeros((T,27));coefficients=np.zeros((T,27));pairs=0
    for t,G,h,D in likelihoods(R,X,baseline,cfg):
        B=N*G;b=N*h;C,rank=symmetric_pinv(B)
        measurement=np.maximum(np.diag(C),1e-12)
        if P is None:P=np.diag(measurement)/.1
        noise_sum=decay*noise_sum+measurement;mass=decay*mass+1.
        q=(noise_sum/mass)*process_ratio
        predicted=P+np.diag(q);prior_precision=np.linalg.solve(predicted,eye)
        prior_precision=.5*(prior_precision+prior_precision.T)
        total=prior_precision+B;total=.5*(total+total.T)
        P=np.linalg.solve(total,eye);P=.5*(P+P.T)
        mean=P@(prior_precision@mean+b);pairs+=1
        ev=np.linalg.eigvalsh(P)
        if ev.min()<=0 or not np.isfinite(mean).all():raise RuntimeError('invalid filter posterior')
        if t>=253 and pairs>=126:out[t]=.5*baseline[t,:N]+.5*(D@mean)
        postvar[t]=np.diag(P);processvar[t]=q;coefficients[t]=mean
        if t==65 or t==T-1 or (t-253)%126==0:
            records.append(dict(target_row=t,last_label=t-1,covariance_last_row=t-2,
                                training_pairs=pairs,rank=rank,posterior_min_eigenvalue=float(ev.min()),
                                coefficient_norm=float(np.linalg.norm(mean)),posterior_diagonal=np.diag(P).tolist(),
                                process_diagonal=q.tolist()))
    if not np.isfinite(out).all():raise RuntimeError('nonfinite Kalman forecast')
    return out,records,dict(posterior_diagonal=postvar,process_diagonal=processvar,coefficients=coefficients)


class CandidatePolicy(CorrelationPolicy):
    def forecast(self,returns_history,characteristics_history):
        base=super().forecast(returns_history,characteristics_history);n=np.shape(returns_history)[1]
        alpha,self.learner_records,self.diagnostic_arrays=kalman_forecast(
            returns_history,characteristics_history,base[:,:n+27],self.cfg)
        self.forecast_output=np.hstack([alpha,base[:,n:]])
        return self.forecast_output

"""Frozen characteristic-peer residual learner; research only.

P adds own/peer EW5/21 residual dynamics; O is the own-only attribution control.
PS, only conditionally admitted by the plan, relabels graph nodes as a placebo.
All training responses have matured before a forecast is produced.
"""
from __future__ import annotations
import numpy as np
from gls_alpha import CandidatePolicy as GLS
from model_f import engine as E
from research.relations.graph import PeerGraph

class CandidatePolicy(GLS):
    def __init__(self,mode='P'):
        super().__init__()
        if mode not in ('P','O','PS'):raise ValueError('unknown peer alpha mode')
        self.mode=mode
    def forecast(self,returns_history,characteristics_history):
        base=super().forecast(returns_history,characteristics_history)
        R=np.ascontiguousarray(returns_history,dtype=np.float64);X=characteristics_history
        T,N=R.shape;beta,m=E.causal_betas(R,self.cfg['beta_window'])
        graph=PeerGraph();p=2 if self.mode=='O' else 4
        gram=np.zeros((p,p));moment=np.zeros(p);mass=0.;pairs=0
        decay=2.**(-1./1008.);ah=np.power(2.,-1./np.array([5.,21.]))
        sums=np.zeros((N,2));masses=np.zeros(2);previous=None
        output=base.copy();records=[];fraction=0.;max_projection=0.
        increment=np.zeros((T,N));own_signal=np.zeros((T,N));peer_signal=np.zeros((T,N))
        shuffle=np.roll(np.arange(N),N//2);inv=np.argsort(shuffle)
        for s in range(max(0,T-1)):
            if s:
                # Training response s is observed now; previous feature row is s-1.
                response=R[s]-beta[s]*m[s]-base[s,:N]
                gram=decay*gram+previous.T@previous/N
                moment=decay*moment+previous.T@response/N
                mass=decay*mass+1.;pairs+=1
                D=E.basis(X[s-1],self.cfg['feature_clip'])
                e=R[s]-beta[s]*m[s];e=e-e.mean()
                f=np.linalg.solve(D.T@D/N+1e-10*np.eye(26),D.T@e/N)
                resid=e-D@f
                sums=ah[None,:]*sums+resid[:,None];masses=ah*masses+1.
            own=sums/np.maximum(masses,1.)[None,:]
            if self.mode!='O':
                W=graph.at(X,s)
                peer=W@own if self.mode=='P' else (W@own[shuffle])[inv]
                raw=np.hstack([own,peer]);peer_signal[s+1]=peer[:,1]
            else:raw=own
            features=E._standardize(np.ascontiguousarray(raw),4.)
            Dnow=np.hstack([E.basis(X[s],self.cfg['feature_clip']),E._zcol(beta[s+1],4.)[:,None]])
            features=features-Dnow@np.linalg.solve(Dnow.T@Dnow/N+1e-8*np.eye(27),Dnow.T@features/N)
            max_projection=max(max_projection,float(np.max(np.abs(Dnow.T@features/N),initial=0.)))
            target=s+1
            if pairs>=252:
                coef=np.linalg.solve(gram/mass+np.eye(p),moment/mass)
                extra=.5*(features@coef)
                rms=float(np.sqrt(np.mean(extra*extra)));ref=float(np.sqrt(np.mean(base[target,:N]**2)))
                scale=min(1.,.2*ref/max(rms,1e-30));extra*=scale
                increment[target]=extra;output[target,:N]+=extra
                fraction=max(fraction,float(np.sqrt(np.mean(extra*extra)))/max(ref,1e-30))
                if (target-253)%126==0:
                    records.append(dict(target_row=target,last_label=s,last_feature=s-1,training_pairs=pairs,coef=coef.tolist(),cap_scale=scale))
            own_signal[target]=own[:,1];previous=features
        self.relation_records=records
        self.relation_diagnostics={**graph.diagnostics,'max_alpha_fraction':fraction,'max_design_projection':max_projection}
        self.diagnostic_arrays=dict(increment=increment,own_ew21=own_signal,peer_ew21=peer_signal)
        self.forecast_output=output
        if not np.isfinite(output).all():raise RuntimeError('nonfinite peer forecast')
        return output

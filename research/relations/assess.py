"""Declared peer-model comparisons and explanatory diagnostics, no new fitted policy."""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import json,sys,argparse
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.common import harness as H
from research.relations.graph import PeerGraph
from model_f import engine as E
from model_f.config import CONFIG

def sharpe(r):return float(np.sqrt(252)*r.mean()/r.std())
def ic_by_day(pred,y):
    p=pred-pred.mean(1,keepdims=True);r=y-y.mean(1,keepdims=True)
    den=np.sqrt(np.sum(p*p,1)*np.sum(r*r,1))
    return np.divide(np.sum(p*r,1),den,out=np.zeros(len(p)),where=den>1e-30)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    models=['G','P','O','V','VG'];summaries={m:json.load(open(a.work/'runs'/m/'summary.json')) for m in models}
    rows={m:np.load(a.work/'runs'/m/'rows.npy') for m in models}
    net=np.column_stack([rows[m][:,0]-rows[m][:,1] for m in models]);N=len(net)
    contrasts=[('P-G',1,0),('V-G',3,0),('P-O',1,2),('V-VG',3,4)]
    observed=np.sqrt(252)*net.mean(0)/net.std(0);boot={}
    for block in (21,63,126):
        rng=np.random.default_rng(20261105);b=np.empty((3000,5))
        for j in range(len(b)):
            starts=rng.integers(0,N,size=int(np.ceil(N/block)))
            idx=((starts[:,None]+np.arange(block))%N).ravel()[:N];v=net[idx]
            b[j]=np.sqrt(252)*v.mean(0)/v.std(0)
        result={}
        for name,i,k in contrasts:
            dif=b[:,i]-b[:,k];obs=float(observed[i]-observed[k])
            result[name]=dict(observed=obs,interval95=np.quantile(dif,[.025,.975]).tolist(),centered_one_sided_p=float((1+np.sum((dif-obs)>=obs))/(len(b)+1)))
        ps=np.array([result[c]['centered_one_sided_p'] for c in ('P-G','V-G')]);order=np.argsort(ps);adj=np.empty(2);adj[order]=np.minimum(1.,np.maximum.accumulate(ps[order]*np.array([2,1])))
        for i,c in enumerate(('P-G','V-G')):result[c]['holm_two_primaries']=float(adj[i])
        boot[str(block)]=result
    R,X,c=H.load_data(a.source,a.work);R=np.ascontiguousarray(R);beta,market=E.causal_betas(R)
    T,n=R.shape;lo,hi=253,T-1;y=R[lo:hi]-beta[lo:hi]*market[lo:hi,None]
    forecasts={m:np.load(a.work/'runs'/m/'forecast.npy',mmap_mode='r') for m in ['G','P','O']}
    predictive={}
    for m,f in forecasts.items():
        pred=f[lo:hi,:n];ic=ic_by_day(pred,y)
        predictive[m]=dict(mse=float(np.mean((pred-y)**2)),mean_daily_ic=float(ic.mean()),ic_information_ratio=float(np.sqrt(252)*ic.mean()/ic.std()))
    inc=forecasts['P'][lo:hi,:n]-forecasts['O'][lo:hi,:n]
    predictive['P_minus_O_incremental_ic']=float(ic_by_day(inc,y-forecasts['G'][lo:hi,:n]).mean())
    # Residual-risk proxies; all predictions use previous-day published states.
    graph=PeerGraph();state=E._RiskState(n,26,CONFIG)
    prev_d=np.full(n,CONFIG['variance_floor']);prev_v=prev_d.copy();prev_g=prev_d.copy()
    qlike=[];comove=[];kinship=[]
    for s in range(1,T-1):
        b=E._window_beta(R[:s],CONFIG['beta_window']);D=E.basis(X[s-1]);e=R[s]-b*R[s].mean();e-=e.mean()
        f=np.linalg.solve(D.T@D/n+1e-10*np.eye(26),D.T@e/n);u=e-D@f;u2=u*u
        if s>=253:
            qlike.append([float(np.mean(np.log(prev_v/prev_d)+u2*(1/prev_v-1/prev_d))),float(np.mean(np.log(prev_g/prev_d)+u2*(1/prev_g-1/prev_d)))])
            W=graph.at(X,s-1)
            # Equal-stock normalized cross-sectional covariance, not a time-series Pearson correlation.
            comove.append([float(e@(W@e)/max(float(e@e),1e-30)),float(u@(W@u)/max(float(u@u),1e-30))])
        state.absorb(R,X,s);_,d=state.model();W=graph.at(X,s)
        peer=W@d;v=d*np.clip(.5+.5*peer/d,.75,1.5);vg=d*np.clip(.5+.5*d.mean()/d,.75,1.5)
        if s>=252:
            dd=d-d.mean();pp=peer-peer.mean();kinship.append(float(dd@pp/max(float(np.sqrt(dd@dd*(pp@pp))),1e-30)))
        prev_d,prev_v,prev_g=d,v,vg
    qlike=np.array(qlike);comove=np.array(comove)
    diagnostic=dict(variance_qlike_change_V=float(qlike[:,0].mean()),variance_qlike_change_VG=float(qlike[:,1].mean()),
        contemporaneous_peer_covariance_ratio_market_residual=float(comove[:,0].mean()),contemporaneous_peer_covariance_ratio_factor_residual=float(comove[:,1].mean()),
        mean_cross_sectional_d_peer_d_correlation=float(np.mean(kinship)),label='Explanatory observed-sample proxies, not hidden generator variances or causal network evidence')
    decision={}
    for primary,control in [('P','O'),('V','VG')]:
        p,g=summaries[primary],summaries['G'];gains=[u['net_sharpe']-v['net_sharpe'] for u,v in zip(p['stages'],g['stages'])]
        halves=[u['net_sharpe']-v['net_sharpe'] for u,v in zip(p['halves'],g['halves'])]
        cond=dict(full_gain=p['net_sharpe']-g['net_sharpe']>=.005,two_stages=sum(v>0 for v in gains)>=2,both_halves=all(v>0 for v in halves),stage_floor=min(gains)>=-.05,beta=abs(p['beta'])<.18 and p['beta']<=g['beta']+.01,matched_control=p['net_sharpe']-summaries[control]['net_sharpe']>=.002)
        decision[primary]=dict(conditions=cond,stage_gains=gains,half_gains=halves,economic_shortlist=all(cond.values()))
    result=dict(summaries=summaries,bootstrap=boot,prediction_diagnostics=predictive,risk_graph_diagnostics=diagnostic,decisions=decision)
    H.write_json(a.work/'ASSESSMENT.json',result);np.savez_compressed(a.work/'diagnostic_days.npz',qlike=qlike,comovement=comove)
    print(json.dumps(dict(decisions=decision,prediction=predictive,diagnostics=diagnostic),indent=2),flush=True)
if __name__=='__main__':main()

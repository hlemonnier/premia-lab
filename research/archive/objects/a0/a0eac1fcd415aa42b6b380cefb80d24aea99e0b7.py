"""Fixed two-candidate assessment; no fitting, policy search, or revised thresholds.

Uncertainty is conditional on already exposed development data, not a new
holdout. Gaussian factor loss uses the unscaled covariance of estimated factor
returns (undoing the allocator's deliberate 0.3 factor-risk discount).
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import harness as H
import numpy as np
from model_f import engine as E
from model_f.config import CONFIG


def corr(cov):
    sd=np.sqrt(np.maximum(np.diag(cov),1e-16))
    c=cov/sd[:,None]/sd[None,:]
    np.fill_diagonal(c,1.)
    return .5*(c+c.T)


def block_bootstrap(rows):
    names=['gls','correlation'];base=rows['F'][:,0]-rows['F'][:,1]
    nets=np.stack([rows[n][:,0]-rows[n][:,1] for n in names]);T=len(base)
    sr=lambda a:np.sqrt(252)*np.mean(a,axis=-1)/np.std(a,axis=-1)
    observed=sr(nets)-sr(base);result={};rng=np.random.default_rng(20261102)
    for block in (21,63,126):
        vals=np.empty((3000,2));k=0
        while k<3000:
            m=min(64,3000-k)
            starts=rng.integers(0,T,size=(m,math.ceil(T/block)))
            idx=((starts[:,:,None]+np.arange(block))%T).reshape(m,-1)[:,:T]
            bs=sr(base[idx])
            for j in range(2):vals[k:k+m,j]=sr(nets[j][idx])-bs
            k+=m
        ps=(1+np.sum(vals-observed[None,:]>=observed[None,:],axis=0))/3001
        order=np.argsort(ps);adjusted=np.empty(2);running=0.
        for rank,j in enumerate(order):
            running=max(running,(2-rank)*ps[j]);adjusted[j]=min(1.,running)
        result[str(block)]={name:dict(delta=float(observed[j]),
            interval_95=np.quantile(vals[:,j],[.025,.975]).tolist(),
            positive_fraction=float(np.mean(vals[:,j]>0)),
            centered_one_sided_p=float(ps[j]),holm_two_candidates_p=float(adjusted[j]))
            for j,name in enumerate(names)}
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    R,X,cost=H.load_data(a.source,a.work);R=np.ascontiguousarray(R,dtype=np.float64)
    names=['F','gls','correlation'];root=a.work/'runs'
    rows={n:np.load(root/n/'rows.npy') for n in names}
    forecasts={n:np.load(root/n/'forecast.npy',mmap_mode='r') for n in names}
    summaries={n:json.load(open(root/n/'summary.json')) for n in names}
    T,N=R.shape
    alpha_error=float(np.max(np.abs(forecasts['correlation'][:,:N]-forecasts['F'][:,:N])))
    gls_risk_error=float(np.max(np.abs(forecasts['gls'][:,N:]-forecasts['F'][:,N:])))
    beta,market=E.causal_betas(R,CONFIG['beta_window'])
    ic={n:[] for n in ['F','gls']};mse={n:[] for n in ['F','gls']}
    factor_loss=[];state=E._RiskState(N,26,CONFIG);diagonal_error=0.
    for u in range(1,T-1):
        D=E.basis(X[u-1],CONFIG['feature_clip'])
        b=E._window_beta(R[:u],CONFIG['beta_window'])
        e=R[u]-b*R[u].mean();e=e-e.mean()
        f=np.linalg.solve(D.T@D/N+1e-10*np.eye(26),D.T@e/N)
        if u>=253:
            # State currently includes only source observations through u-1.
            S=state.S2/state.wF
            v=forecasts['F'][u,N+1:]
            A=np.sqrt(v);Sf=A[:,None]*S*A[None,:]
            alt=forecasts['correlation'][u,N+27:].reshape(26,26)
            C=.5*corr(Sf)+.5*alt
            diag=np.maximum(np.diag(Sf),0.);sd=np.sqrt(diag)
            Sc=sd[:,None]*C*sd[None,:]
            diagonal_error=max(diagonal_error,float(np.max(np.abs(np.diag(Sc)-diag)/np.maximum(diag,1e-16))))
            jitter=1e-12*max(float(diag.mean()),1e-16)
            losses=[]
            for mat in [Sf,Sc]:
                mat=mat+jitter*np.eye(26)
                sign,logdet=np.linalg.slogdet(mat)
                if sign<=0: raise RuntimeError('diagnostic covariance not positive')
                losses.append(float([redacted-email](mat,f)))
            factor_loss.append(losses)
            y=R[u]-beta[u]*market[u];yc=y-y.mean()
            for n in ic:
                pred=forecasts[n][u,:N];pc=pred-pred.mean()
                den=float(np.linalg.norm(pc)*np.linalg.norm(yc))
                ic[n].append(float(pc@yc/den) if den>0 else 0.)
                mse[n].append(float(np.mean((pred-y)**2)))
        state.absorb(R,X,u)
    loss=np.array(factor_loss);dl=loss[:,1]-loss[:,0]
    dd=np.arange(253,T-1)
    diagnostics=dict(correlation_alpha_exact_error=alpha_error,gls_factor_risk_exact_error=gls_risk_error,
        factor_marginal_variance_max_relative_error=diagonal_error,
        covariance_loss_delta=float(dl.mean()),covariance_loss_stages=[float(dl[(dd>=lo)&(dd<hi)].mean())
            for lo,hi in [(253,2016),(2016,3024),(3024,3779)]],alpha={})
    for n in ic:
        vals=np.array(ic[n]);diagnostics['alpha'][n]=dict(mean_ic=float(vals.mean()),
          ic_sharpe=float(np.sqrt(252)*vals.mean()/vals.std()),mse=float(np.mean(mse[n])))
    np.savez_compressed(a.work/'diagnostic_daily.npz',factor_loss=loss,ic_F=np.array(ic['F']),
                        ic_gls=np.array(ic['gls']),mse_F=np.array(mse['F']),mse_gls=np.array(mse['gls']))
    bootstrap=block_bootstrap(rows);gate={};b=summaries['F']
    for n in ['gls','correlation']:
        s=summaries[n]
        stage=[a['net_sharpe']-bb['net_sharpe'] for a,bb in zip(s['stages'],b['stages'])]
        halves=[a['net_sharpe']-bb['net_sharpe'] for a,bb in zip(s['halves'],b['halves'])]
        tests=dict(gain=s['net_sharpe']-b['net_sharpe']>=.005,
             both_halves=all(v>0 for v in halves),two_stages=sum(v>0 for v in stage)>=2,
             no_large_stage_decline=min(stage)>=-.05,
             beta=abs(s['beta'])<.18 and s['beta']<=b['beta']+.01,
             timing=s['rebalance_ms']<100 and s['forecast_projected_hours_century']<1,
             covariance_loss=bool(dl.mean()<0) if n=='correlation' else True)
        gate[n]=dict(tests=tests,development_pass=all(tests.values()),
                     stage_deltas=stage,half_deltas=halves)
    result=dict(summaries=summaries,diagnostics=diagnostics,bootstrap=bootstrap,
                shortlist=gate,main_changed=False)
    H.write_json(a.work/'ASSESSMENT.json',result);print(json.dumps(result,indent=2),flush=True)
    assert alpha_error==0 and gls_risk_error==0
    assert diagonal_error<1e-8

if __name__=='__main__':main()

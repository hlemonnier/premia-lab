"""Fixed analysis of both registered primary candidates, including losing runs.

Never changes a model, seed, split, threshold, or score. QLIKE diagnostics use
estimated squared residuals/factors, not the generator's latent variance.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/wave4'))
import run_wave4 as W


def sharpe(x):
    return np.sqrt(252)*np.mean(x,axis=0)/np.std(x,axis=0)


def holm(p):
    p=np.asarray(p);order=np.argsort(p);q=np.zeros_like(p);running=0.
    for rank,j in enumerate(order):
        running=max(running,(len(p)-rank)*p[j]);q[j]=min(1.,running)
    return q


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--prior',type=Path,required=True);a=ap.parse_args();out=a.work/'results'
    names=('C','F');data={n:np.load(out/f'{n}_rows.npy') for n in ('B0','H','C','F','I','T')}
    data['R1']=np.load(a.prior/'R1_rows.npy')
    stats={n:W.summarize(r) for n,r in data.items()}
    net={n:r[:,0]-r[:,1] for n,r in data.items()};base=net['H']
    n=len(base);observed=np.array([sharpe(net[m])-sharpe(base) for m in names]);tests={}
    rng=np.random.default_rng(20261031)
    for block in (21,63,126):
        draws=np.empty((3000,len(names)))
        for b in range(3000):
            starts=rng.integers(0,n,size=int(np.ceil(n/block)))
            idx=((starts[:,None]+np.arange(block))%n).ravel()[:n]
            bs=sharpe(base[idx])
            for j,m in enumerate(names):draws[b,j]=sharpe(net[m][idx])-bs
        np.save(out/f'bootstrap_{block}_deltas.npy',draws)
        p=(1+np.sum(draws-observed>=observed,axis=0))/(len(draws)+1)
        adjusted=holm(p);tests[str(block)]={}
        for j,m in enumerate(names):
            tests[str(block)][m]={'difference':float(observed[j]),'interval95':np.quantile(draws[:,j],[.025,.975]).tolist(),
                                 'positive_fraction':float(np.mean(draws[:,j]>0)),'centered_one_sided_p':float(p[j]),'holm_p':float(adjusted[j])}
    dates=np.arange(253,253+n);stage_masks=[(dates>=lo)&(dates<hi) for lo,hi in ((253,2016),(2016,3024),(3024,3779))]
    gates={};qlike={}
    for m in ('C','F','I','T'):
        qlike[m]={}
        for component in ('specific','factor'):
            q=np.load(out/f'{m}_{component}_qlike.npy')
            qlike[m][component]={'mean':float(q.mean()),'stages':[float(q[mask].mean()) for mask in stage_masks]}
    for m in names:
        details=json.loads((out/f'{m}.json').read_text())
        stage_delta=np.array([stats[m]['stages'][j]['net_sharpe']-stats['H']['stages'][j]['net_sharpe'] for j in range(3)])
        half_delta=[stats[m]['halves'][j]['net_sharpe']-stats['H']['halves'][j]['net_sharpe'] for j in range(2)]
        cert=details['solver_status'];component='specific' if m=='C' else 'factor'
        requirements={
            'gain_at_least_0.005':stats[m]['net_sharpe']-stats['H']['net_sharpe']>=.005,
            'two_stages_improve':int(np.sum(stage_delta>0))>=2,
            'no_stage_decline_over_0.05':bool(np.all(stage_delta>=-.05)),
            'beta':abs(stats[m]['beta'])<.18 and stats[m]['beta']<=stats['H']['beta']+.01,
            'timing':details['rebalance_ms']<100 and details['forecast_hours_per_century']<1,
            'proxy_qlike_improves':qlike[m][component]['mean']<0,
            'finite_no_ruin':bool(np.isfinite(data[m]).all() and np.min(data[m][:,0])>-1),
            'certificates':all(s in ('ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal') for s in cert),
        }
        e2e_path=a.work/'checks'/f'market_{m}.json'
        requirements['market_causality_e2e']=json.loads(e2e_path.read_text())['passed'] if e2e_path.exists() else False
        strong={
            'both_halves_positive':all(d>0 for d in half_delta),
            'all_bootstrap_lower_positive':all(tests[str(b)][m]['interval95'][0]>0 for b in (21,63,126)),
            'all_holm_below_005':all(tests[str(b)][m]['holm_p']<.05 for b in (21,63,126)),
        }
        gates[m]={'requirements':requirements,'stage_deltas':stage_delta.tolist(),'half_deltas':half_delta,
                  'development_pass':all(requirements.values()),'strong_requirements':strong,
                  'promotion_pass':all(requirements.values()) and all(strong.values())}
    res={'statistics':stats,'bootstrap':tests,'qlike':qlike,'gates':gates,
         'combination_allowed':all(g['development_pass'] for g in gates.values()),
         'scope':'Exposed development data; two-test Holm is not project-wide selection correction.'}
    W.save_json(out/'assessment.json',res)
    print(json.dumps({'scores':{n:s['net_sharpe'] for n,s in stats.items()},'gates':gates,'bootstrap63':tests['63'],'qlike':qlike}),flush=True)

if __name__=='__main__':main()

"""Observed saved-ledger opportunity diagnostics; see prospective PLAN.md."""
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
STAGES = {"full": (253,3779), "discovery": (253,2015),
          "validation": (2016,3023), "audit": (3024,3779)}
PAIRS = [("beta_feat","fr_beta"), ("decor_beta","fr_beta"),
         ("fr_beta_phi03_x5","C09_engine")]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def metrics(a):
    day, net, gross, fee, market = a
    out = {}
    for stage,(lo,hi) in STAGES.items():
        k = (day>=lo)&(day<hi)
        n, g, c, m = net[k],gross[k],fee[k],market[k]
        mc = m-m.mean()
        ns = float(np.sqrt(252)*n.mean()/n.std())
        gs = float(np.sqrt(252)*g.mean()/g.std())
        out[stage] = {"n":int(k.sum()), "net_sharpe":ns, "gross_sharpe":gs,
            "unchanged_holdings_fee_removal_sharpe_gain":gs-ns,
            "net_mean_ann_pct":float(25200*n.mean()),
            "gross_mean_ann_pct":float(25200*g.mean()),
            "net_vol_ann_pct":float(100*np.sqrt(252)*n.std()),
            "gross_vol_ann_pct":float(100*np.sqrt(252)*g.std()),
            "fee_ann_pct":float(25200*c.mean()),
            "net_beta":float(mc@(n-n.mean())/(mc@mc))}
    return out


def main():
    manifest=json.loads((HERE/'input_manifest.json').read_text())
    root=Path(manifest['root'])
    for e in manifest['files']:
        p=root/e['path']
        assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'], str(p)
    earlier=[]
    earlier_root=Path(manifest['earlier_metadata_root'])
    for e in manifest['earlier_metadata_files']:
        p=earlier_root/e['path']
        assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'], str(p)
        if p.name=='summary.json':
            d=json.loads(p.read_text())
            earlier.append({'path':e['path'],'candidate':d['configuration'],
                'metrics':d['metrics'],'score_slice':d['score_slice'],'status':d['status']})
    (HERE/'earlier_reported_results.json').write_text(json.dumps(earlier,indent=2)+'\n')
    ledgers={}
    for e in manifest['files']:
        if not e['path'].endswith('.npy'): continue
        p=root/e['path']; a=np.load(p,allow_pickle=False)
        assert a.shape==(5,3526) and np.isfinite(a).all(), str(p)
        assert np.array_equal(a[0],np.arange(253,3779)), str(p)
        assert np.max(np.abs(a[1]-(a[2]-a[3])))<=1e-12, str(p)
        ledgers[p.stem.removeprefix('net_')]=a
    v=ledgers['fr_beta_phi03_x5']
    for name,a in ledgers.items():
        assert np.max(np.abs(a[4]-v[4]))<=1e-12, name
    summaries={k:metrics(vv) for k,vv in ledgers.items()}
    complement={}
    x=v[1]; xc=x-x.mean()
    for name,a in ledgers.items():
        y=a[1]; yc=y-y.mean(); slope=float(xc@yc/(xc@xc))
        r=y-slope*x
        complement[name]={"net_corr_with_v2":float(np.corrcoef(x,y)[0,1]),
            "slope_on_v2":slope,"intercept_ann_pct":float(25200*r.mean()),
            "residual_vol_ann_pct":float(100*np.sqrt(252)*r.std()),
            "intercept_over_residual_vol":float(np.sqrt(252)*r.mean()/r.std()) if r.std()>1e-15 else None}
    blends={}
    for an,bn in PAIRS:
        a,b=ledgers[an],ledgers[bn]
        sa,sb=a[1].std(),b[1].std()
        # Common scale gives each risk-normalized leg .5*V2 full net volatility.
        # It affects levels, not Sharpe. Both scales contain future information.
        ka,kb=.5*x.std()/sa,.5*x.std()/sb
        h=a.copy(); h[1:4]=ka*a[1:4]+kb*b[1:4]
        equal=a.copy(); equal[1:4]=.5*a[1:4]+.5*b[1:4]
        blends[an+'__'+bn]={"descriptive_not_executed":True,
            "net_corr":float(np.corrcoef(a[1],b[1])[0,1]),
            "net_variance_ratio_a_over_b":float(sa*sa/(sb*sb)),
            "hindsight_risk_equalizing_coefficients":[float(ka),float(kb)],
            "net_gross_fee_identity_error":float(np.max(np.abs(h[1]-h[2]+h[3]))),
            "hindsight_equal_risk":metrics(h),"fixed_raw_half_half":metrics(equal)}
    decay=2**(-1/63)
    q=np.zeros(len(x)); accum=mass=0.
    for i,g in enumerate(v[2]):
        q[i]=accum/mass if mass else np.nan
        accum=decay*accum+g*g; mass=decay*mass+1
    k=np.arange(len(x))>=126
    cuts=np.quantile(q[k],np.arange(6)/5)
    group=np.full(len(x),-1,dtype=int)
    group[k]=np.searchsorted(cuts[1:-1],q[k],side='right')
    buckets={}
    for j in range(5):
        idx=group==j
        buckets[str(j+1)]={"n":int(idx.sum()),"lagged_second_moment_mean":float(q[idx].mean()),
            "realized_gross_second_moment":float(np.mean(v[2,idx]**2)),
            "net_mean_ann_pct":float(25200*v[1,idx].mean()),
            "gross_mean_ann_pct":float(25200*v[2,idx].mean()),
            "fee_ann_pct":float(25200*v[3,idx].mean()),
            "net_vol_ann_pct":float(100*np.sqrt(252)*v[1,idx].std()),
            "net_sharpe":float(np.sqrt(252)*v[1,idx].mean()/v[1,idx].std())}
    with (HERE/'v2_lagged_risk_diagnostic.csv').open('w',newline='') as f:
        wr=csv.writer(f); wr.writerow(['day','net','gross','fee','lagged_ew63_gross_squared_return','hindsight_quintile'])
        for i in range(len(x)): wr.writerow([int(v[0,i]),v[1,i],v[2,i],v[3,i],q[i],int(group[i]+1)])
    result={'pinned_source':manifest['pinned_commit'], 'ledgers_verified':len(ledgers),
        'input_manifest_sha256':sha(HERE/'input_manifest.json'),
        'plan_sha256':sha(HERE/'PLAN.md'),'script_sha256':sha(Path(__file__)),
        'command':'python evidence/v2_score_opportunity_20261028/readback.py',
        'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
        'summaries':summaries,'descriptive_complementarity':complement,
        'reference_blends':blends,'v2_lagged_risk_buckets':{'burnin_observations':126,
        'half_life':63,'hindsight_quintile_boundaries':cuts.tolist(),'buckets':buckets}}
    (HERE/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'verified':len(ledgers),'v2':summaries['fr_beta_phi03_x5'],
        'reference_blends':blends,'v2_lagged_risk_buckets':buckets},indent=2))


if __name__=='__main__': main()

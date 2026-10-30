"""Independent full-path saved-output accounting. See ACTUAL_READBACK_PLAN.md."""
import argparse
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
REPO=HERE.parent.parent
DATA=REPO.parent/'v2-original-input/extracted/Quant Research Take-Home'
FROOT=REPO/'evidence/v2_score_forecast_20261028/actual_001'
VROOT=REPO/'evidence/v2_score_overlay_20261028/actual_001'
STAGES={'full':(253,3779),'discovery':(253,2015),'validation':(2016,3023),'audit':(3024,3779)}
INPUTS={}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def note(path):
    p=Path(path);INPUTS[str(p)]={'bytes':p.stat().st_size,'sha256':sha(p)}
    return p


def jload(path):return json.loads(note(path).read_text())


def frame(path):return pd.read_csv(note(path),float_precision='round_trip')


def array_sha(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def load_arrays(path):
    if path.is_dir():
        names={'forecast':'forecast','targets':'targets','decision_indices':'indices','rows':'rows','earning_indices':'days'}
        return {key:np.load(note(path/(name+'.npy')),allow_pickle=False) for key,name in names.items()}
    return np.load(note(path),allow_pickle=False)


def maximum(a,b):return float(np.max(np.abs(np.asarray(a)-np.asarray(b)),initial=0))


def metrics(rows):
    day,g,c,gross,m=rows.T;result={}
    for label,(lo,hi) in STAGES.items():
        k=(day>=lo)&(day<hi);net=g[k]-c[k];market=m[k];mc=market-market.mean()
        result[label]={'n':int(k.sum()),'net_sharpe':float(np.sqrt(252)*net.mean()/net.std()),
            'gross_sharpe':float(np.sqrt(252)*g[k].mean()/g[k].std()),
            'net_return_ann_pct':float(25200*net.mean()),'net_vol_ann_pct':float(100*np.sqrt(252)*net.std()),
            'cost_ann_pct':float(25200*c[k].mean()),'net_beta':float(mc@(net-net.mean())/(mc@mc)),
            'mean_gross':float(gross[k].mean()),'worst_gross_daily_return':float(g[k].min())}
    return result


def account(target,R,costs):
    assert target.shape==(3527,1000) and np.isfinite(target).all()
    idx=np.arange(252,3779)
    previous=np.vstack([np.zeros((1,1000)),target[:-1]])
    g=np.einsum('ij,ij->i',previous,R[idx])
    assert np.all(g>-1)
    drift=previous*(1+R[idx])/(1+g[:,None])
    fees=np.abs(target-drift)@costs;fees[0]=0
    return np.column_stack([idx,g,fees,np.abs(target).sum(axis=1),R[idx].mean(axis=1)])[1:]


def read_csv_rows(folder,overlay):
    d=frame(folder/'daily.csv')
    names=['return_index','gross_return','full_cost','closing_target_gross','market_return'] if overlay else ['day','gross_return','cost','target_gross','market']
    a=d[names].to_numpy()
    assert a.shape==(3526,5) and np.array_equal(a[:,0],np.arange(253,3779))
    assert np.isfinite(a).all() and maximum(d['net_return'],a[:,1]-a[:,2])<=1e-12
    return a


def reconcile_summary(calc,expected,overlay):
    keys={'net_sharpe':'net_sharpe','gross_sharpe':'gross_sharpe','net_return_ann_pct':'net_return_ann_pct',
        'net_vol_ann_pct':'net_vol_ann_pct','cost_ann_pct':'cost_ann_pct','net_beta':'net_beta','mean_gross':'mean_gross'} if overlay else {
        'net_sharpe':'sharpe','net_return_ann_pct':'annual_net_return_pct','net_vol_ann_pct':'annual_vol_pct',
        'cost_ann_pct':'annual_cost_pct','net_beta':'beta','mean_gross':'mean_gross'}
    differences={stage:{k:float(calc[stage][k]-expected[stage][v]) for k,v in keys.items()} for stage in STAGES}
    assert max(abs(v) for s in differences.values() for v in s.values())<=1e-10
    return differences


def check_records(folder,summary,overlay,cap,target):
    d=frame(folder/'decisions.csv');assert len(d)==3527
    assert np.array_equal(d['decision_index'].to_numpy(),np.arange(252,3779))
    status=d['certificate_status' if overlay else 'certificate']
    assert status.isin(['ok','ok_after_recovery']).all()
    assert np.abs(target).max()<=cap+1e-12 and np.abs(target).sum(axis=1).max()<=5+1e-12
    assert all(summary['checks'].values())
    return {'certificates':status.value_counts().to_dict(),'max_abs_weight':float(np.abs(target).max()),
        'max_gross':float(np.abs(target).sum(axis=1).max())},d


def check_moments(metadata,virtual,R,power):
    sums={63:0.,1008:0.};mass={63:0.,1008:0.};errors=[]
    for j,row in enumerate(metadata.itertuples(index=False)):
        g=0. if j==0 else float(virtual[j-1]@R[252+j])
        if j:
            for h in sums:
                sums[h]=2**(-1/h)*sums[h]+g*g;mass[h]=2**(-1/h)*mass[h]+1
        q={h:sums[h]/mass[h] if mass[h] else 0. for h in sums}
        ratio=max(q[1008],1e-12)/max(q[63],1e-12)
        a=1. if j<63 else float(np.clip(ratio**power,.5,2))
        assert row.earned_observations==j
        errors.append(max(abs(g-row.virtual_gross_return),abs(q[63]-row.q63),abs(q[1008]-row.q1008),abs(a-row.multiplier)))
    assert max(errors)<=1e-12
    return max(errors)


def bootstrap(series,base):
    n=len(base);out={k:{} for k in series if k!='V2'}
    for length in (21,63,126):
        rng=np.random.default_rng(20261027)
        starts=rng.integers(0,n-length+1,size=(2000,(n+length-1)//length))
        ix=(starts[:,:,None]+np.arange(length)).reshape(2000,-1)[:,:n]
        b=base[ix];bs=np.sqrt(252)*b.mean(axis=1)/b.std(axis=1)
        for k,v in series.items():
            if k=='V2':continue
            a=v[ix];diff=np.sqrt(252)*a.mean(axis=1)/a.std(axis=1)-bs
            lo,hi=np.quantile(diff,[.025,.975])
            out[k][str(length)]={'lo':float(lo),'hi':float(hi),'draws':2000,'seed':20261027}
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--joint-folder',type=Path)
    ap.add_argument('--f1-arrays',type=Path)
    ap.add_argument('--f2-arrays',type=Path)
    ap.add_argument('--f1-ledger-only',action='store_true')
    args=ap.parse_args();assert not args.out.exists()
    for p in (FROOT/'verification.json',FROOT/'status.json',VROOT/'results.json'):
        assert p.exists(),str(p)
    reference=jload(REPO/'evidence/v2_followup_review_20261028/replay_V2_002/input_hashes.json')
    for name in ('returns.csv','characteristics.csv','costs.csv'):
        assert sha(note(DATA/name))==reference[name]
    source_records={}
    source_specs=[('forecast',FROOT,'clean','source_sha256'),('overlay',VROOT,'source','sha256')]
    if args.joint_folder:
        source_specs.append(('joint',args.joint_folder.parent,'source','sha256'))
        assert sha(note(args.joint_folder.parent/'prototype.py'))==sha(note(FROOT/'executed_prototype.py'))
        assert sha(note(args.joint_folder.parent/'overlay.py'))==sha(note(VROOT/'overlay.py'))
    for label,folder,subdir,key in source_specs:
        manifest=jload(folder/'source_manifest.json')
        assert manifest['commit']=='ce3fe4e76271709422165d6f24e2fbecd9d0fe07'
        for rel,digest in manifest[key].items():
            assert sha(note(folder/subdir/rel))==digest
            assert sha(REPO.parent/'v2-followup-snapshot'/rel)==digest
        source_records[label]=manifest
    R=np.ascontiguousarray(pd.read_csv(DATA/'returns.csv',index_col='day').to_numpy(np.float64))
    costs=pd.read_csv(DATA/'costs.csv',index_col='stock')['cost'].to_numpy(np.float64)
    results={};series={};virtuals={};baseline_rows=None
    for label,folder in [('V2',FROOT/'baseline_V2'),('F1',FROOT/'F1_base'),('F2',FROOT/'F2_base')]:
        if label=='F1' and args.f1_ledger_only:
            note(folder/'arrays.npz')
            rows=read_csv_rows(folder,False);summary=jload(folder/'summary.json');calc=metrics(rows)
            assert maximum(rows[:,4],R[np.arange(253,3779)].mean(axis=1))<=1e-12
            d=frame(folder/'decisions.csv');assert len(d)==3527
            assert np.array_equal(d['decision_index'],np.arange(252,3779))
            assert d['certificate'].isin(['ok','ok_after_recovery']).all()
            assert np.isfinite(d.select_dtypes(include=[np.number]).to_numpy()).all()
            assert d['max_abs_weight'].max()<=.05+1e-12 and d['target_gross'].max()<=5+1e-12
            assert all(summary['checks'].values())
            results[label]={'performance':calc,'accounting_max_error':None,
                'stock_level_accounting_status':'BLOCKED: original target NPZ truncated; no rejected-policy rerun',
                'summary_differences':reconcile_summary(calc,summary['performance'],False),
                'constraints':{'source':'saved scalar decision records, not independent target-array reconstruction',
                    'certificates':d['certificate'].value_counts().to_dict(),'max_abs_weight':float(d['max_abs_weight'].max()),
                    'max_gross':float(d['target_gross'].max())},'runtime_ms':summary['observed_rebalance_ms']}
            series[label]=rows[:,1]-rows[:,2]
            continue
        override=args.f1_arrays if label=='F1' else args.f2_arrays if label=='F2' else None
        saved=load_arrays(override or folder/'arrays.npz')
        target=saved['targets'];assert np.array_equal(saved['decision_indices'],np.arange(252,3779))
        rows=read_csv_rows(folder,False);rebuilt=account(target,R,costs)
        assert maximum(rows,rebuilt)<=1e-12
        assert maximum(rows[:,1:],saved['rows'][:,:4])<=1e-12
        summary=jload(folder/'summary.json');calc=metrics(rows)
        assert array_sha(target)==summary['targets_sha256']
        assert array_sha(saved['forecast'])==summary['forecast_sha256']
        constraints,_=check_records(folder,summary,False,.05,target)
        results[label]={'performance':calc,'accounting_max_error':maximum(rows,rebuilt),
            'summary_differences':reconcile_summary(calc,summary['performance'],False),
            'constraints':constraints,'runtime_ms':summary['observed_rebalance_ms'],
            'target_sha256':array_sha(target),'forecast_sha256':summary['forecast_sha256']}
        series[label]=rows[:,1]-rows[:,2]
        if label in ('V2','F2'):virtuals[label]=target.copy()
        if label=='V2':baseline_rows=rows.copy()
    overlays=[('fixed_one',VROOT/'fixed_one','V2',0.),('VTvol',VROOT/'VTvol','V2',.5),('VTvar',VROOT/'VTvar','V2',1.)]
    if args.joint_folder:overlays.append(('F2_VTvol',args.joint_folder,'F2',.5))
    for label,folder,base,power in overlays:
        summary=jload(folder/'summary.json');ids=jload(folder/'array_hashes.json')
        metadata=frame(folder/'decisions.csv');virtual=virtuals[base]
        assert array_sha(virtual)==ids['virtual_targets']==summary['virtual_targets_sha256']
        assert ids['forecast']==summary['forecast_sha256']==results[base]['forecast_sha256']
        target=(metadata['multiplier'].to_numpy()[:,None]*virtual)*metadata['aggregate_gross_scale'].to_numpy()[:,None]
        assert array_sha(target)==ids['actual_targets']
        rows=read_csv_rows(folder,True);rebuilt=account(target,R,costs)
        assert maximum(rows,rebuilt)<=1e-12
        assert maximum(rows[:,2],metadata['actual_fee'].to_numpy()[1:])<=1e-12
        constraints,_=check_records(folder,summary,True,.10,target)
        moment_error=check_moments(metadata,virtual,R,power)
        calc=metrics(rows)
        results[label]={'performance':calc,'accounting_max_error':maximum(rows,rebuilt),
            'summary_differences':reconcile_summary(calc,summary['performance'],True),
            'moment_clock_max_error':moment_error,'constraints':constraints,
            'runtime_ms':summary['instrumented_rebalance_ms_mean'],
            'target_sha256':array_sha(target),'virtual_target_source':base}
        if label=='fixed_one':
            assert maximum(rows,baseline_rows)<=1e-8
            results[label]['baseline_cross_replay_max_error']=maximum(rows,baseline_rows)
        else:series[label]=rows[:,1]-rows[:,2]
    intervals=bootstrap(series,series['V2'])
    for label,s in results.items():
        delta=s['performance']['full']['net_sharpe']-results['V2']['performance']['full']['net_sharpe']
        s['sharpe_difference_vs_v2']=delta
        s['numerical_score_improvement']=delta>1e-8
        s['beta_runtime_solvent_eligible']=(abs(s['performance']['full']['net_beta'])<.2 and s['runtime_ms']<100 and s['performance']['full']['worst_gross_daily_return']>-1)
        if label in intervals:s['paired_intervals']=intervals[label]
    # Verify already reported overlay bootstrap intervals independently.
    for label in ('VTvol','VTvar'):
        report=jload(VROOT/label/'summary.json')['paired_sharpe_intervals_vs_fixed_one']
        for length in ('21','63','126'):
            for end in ('lo','hi'):assert abs(report[length][end]-intervals[label][length][end])<=1e-10
    result={'scope':'Independent saved-output accounting, not a new strategy run',
        'plan_sha256':sha(HERE/'ACTUAL_READBACK_PLAN.md'),'source_sha256':sha(Path(__file__)),
        'command_argv':sys.argv,'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,
        'platform':platform.platform(),'results':results,'source_identity_records':source_records,
        'forecast_actual_strict_verification':jload(FROOT/'verification.json'),
        'forecast_actual_original_status':jload(FROOT/'status.json'),
        'causal_disposition':'Original mixed-layout numerical failures remain distinct from separate canonical-layout checks; source and check admission is a root decision, not inferred from a score improvement.',
        'inputs':INPUTS}
    if args.f2_arrays and args.f2_arrays.is_dir():
        result['F2_repaired_artifact_verification']=jload(args.f2_arrays.parent/'verification.json')
        result['F2_repaired_artifact_manifest']=jload(args.f2_arrays.parent/'verified_array_manifest.json')
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:{'sharpe':v['performance']['full']['net_sharpe'],'delta':v['sharpe_difference_vs_v2'],
        'fee_ann_pct':v['performance']['full']['cost_ann_pct'],'beta':v['performance']['full']['net_beta'],
        'accounting_error':v['accounting_max_error']} for k,v in results.items()},indent=2))


if __name__=='__main__':main()

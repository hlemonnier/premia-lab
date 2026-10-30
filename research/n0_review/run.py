"""Execute fixed N0 review scenarios with the original unmodified scorer."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,time
from pathlib import Path
from collections import Counter
import numpy as np
from gls_alpha import CandidatePolicy as G
from research.parallel10.network import NetworkPolicy
from research.parallel10 import harness as H
from research.n0_review.diagnostics import ReviewPolicy


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--prior',type=Path,required=True);p.add_argument('--job',required=True);a=p.parse_args()
    R,X,c=H.load_data(a.source,a.work);score=H.load_score(a.source);S={p.stem:np.load(p,mmap_mode='r') for p in (a.work/'shared').glob('*.npy')}
    label=a.job;cost=1.;sleeve=.05
    if label=='N0':pol=NetworkPolicy('N0')
    elif label=='trace':pol=ReviewPolicy(shared=S)
    elif label in ('D1','D5'):
        order=json.loads((a.work/'concentration.json').read_text())['source_order']
        pol=ReviewPolicy(removal='fixed',excluded=order[:1 if label=='D1' else 5],shared=S)
    elif label=='DC':pol=ReviewPolicy(removal='causal',shared=S)
    else:
        kind,condition=label.split('_');pol=G() if kind=='G' else NetworkPolicy('N0',S)
        if condition=='s0':sleeve=0.
        else:cost=float(condition[1:])
    pol.sleeve=sleeve;c=np.asarray(c)*cost;start=time.perf_counter()
    f,w,rows,seconds,econ=H.exercise(pol,R,X,c,score)
    dest=a.work/'runs'/label;dest.mkdir(parents=True,exist_ok=True)
    for k,v in [('forecast',f),('targets',w),('rows',rows)]:np.save(dest/f'{k}.npy',v)
    result=H.summary(rows);result.update(job=label,sleeve=sleeve,fee_multiplier=cost,forecast_seconds=seconds,wall_seconds=time.perf_counter()-start,cashflow_error=float(np.max(np.abs(rows[:,:4]-econ))),certificates=dict(Counter(x['status'] for x in pol.certificates)))
    if label=='N0':result['archived_row_error']=float(np.max(np.abs(rows[:,:4]-np.load(a.prior/'evidence/runs/N0/rows.npy')[:,:4])))
    if label=='trace':
        result['original_forecast_error']=float(np.max(np.abs(f-np.load(a.work/'runs/N0/forecast.npy',mmap_mode='r'))))
        result['original_weight_error']=float(np.max(np.abs(w-np.load(a.work/'runs/N0/targets.npy',mmap_mode='r'))))
        result['original_row_error']=float(np.max(np.abs(rows[:,:4]-np.load(a.work/'runs/N0/rows.npy')[:,:4])))
        energy=np.sum(pol.raw[253:3779]**2,axis=0);order=np.argsort(-energy,kind='stable');total=float(energy.sum())
        active=pol.fit_own!=0;selected=active.sum(0);both=active[1:]&active[:-1];union=active[1:]|active[:-1]
        concentration=dict(source_order=order.tolist(),energy=energy.tolist(),top1_share=float(energy[order[:1]].sum()/total),top5_share=float(energy[order[:5]].sum()/total),ever_selected=int(np.count_nonzero(selected)),selection_count=selected.tolist(),positive_slopes=int(np.sum(pol.fit_own>0)),negative_slopes=int(np.sum(pol.fit_own<0)),consecutive_jaccard=np.divide(both.sum(1),union.sum(1),out=np.zeros(len(both)),where=union.sum(1)>0).tolist(),same_sign_continued=int(np.sum(both&(np.sign(pol.fit_own[1:])==np.sign(pol.fit_own[:-1])))),continued_count=int(both.sum()))
        H.write_json(a.work/'concentration.json',concentration);np.savez_compressed(dest/'trace.npz',**pol.trace);np.save(dest/'raw.npy',pol.raw)
    if hasattr(pol,'records'):H.write_json(dest/'records.json',pol.records)
    H.write_json(dest/'summary.json',result);print(json.dumps(result),flush=True)
    assert result['cashflow_error']<=1e-10
    assert all(x['status']=='ok' for x in pol.certificates)
    assert result['rebalance_ms']<100
    for key in ('archived_row_error','original_forecast_error','original_weight_error','original_row_error'):
        if key in result:assert result[key]<=1e-10,(key,result[key])
if __name__=='__main__':main()

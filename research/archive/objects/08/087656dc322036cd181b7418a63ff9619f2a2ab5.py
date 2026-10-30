"""Prespecified N0 frozen-review analysis; no forecast or strategy selection code."""
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd
from research.parallel10 import harness as H


def sharpe(x):return float(math.sqrt(252)*np.mean(x)/np.std(x))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,type=Path);ap.add_argument('--work',required=True,type=Path)
    a=ap.parse_args();runs=a.work/'runs';checks=[]
    names=['G','N0','trace','G_s0','N0_s0','G_f2','N0_f2','G_f3','N0_f3','D1','D5','DC']
    rows={s:np.load(runs/s/'rows.npy') for s in names};summary={s:json.loads((runs/s/'summary.json').read_text()) for s in names}
    net={s:r[:,0]-r[:,1] for s,r in rows.items()};n=len(net['G'])
    for s in names:
        x=net[s];m=rows[s][:,3]
        beta=float(np.sum((x-x.mean())*(m-m.mean()))/np.sum((m-m.mean())**2))
        checks.append(dict(name=s+' independent Sharpe',error=abs(sharpe(x)-summary[s]['net_sharpe']),passed=abs(sharpe(x)-summary[s]['net_sharpe'])<1e-12))
        checks.append(dict(name=s+' independent beta',error=abs(beta-summary[s]['beta']),passed=abs(beta-summary[s]['beta'])<1e-12))
    concentration=json.loads((a.work/'concentration.json').read_text());trace=np.load(runs/'trace/trace.npz')
    stock_names=pd.read_csv(a.source/'returns.csv',nrows=0).columns[1:].tolist()
    energy=np.asarray(concentration['energy']);order=concentration['source_order'];active=trace['own']!=0
    sources=[]
    for i in order:
        if energy[i]==0:continue
        fits=np.flatnonzero(active[:,i]);signs=np.sign(trace['own'][fits,i])
        sources.append(dict(index=i,stock=stock_names[i],raw_energy_share=float(energy[i]/energy.sum()),fit_count=int(len(fits)),positive_fits=int(np.sum(signs>0)),negative_fits=int(np.sum(signs<0)),first_target=int(505+126*fits.min()),last_target=int(505+126*fits.max()),mean_selected_slope=float(trace['own'][fits,i].mean())))
    pd.DataFrame(sources).to_csv(a.work/'source_concentration.csv',index=False)
    R=np.load(a.work/'inputs/R.npy',mmap_mode='r');c=np.load(a.work/'inputs/cost.npy')
    stock_pnls={}
    for s in ('G','N0'):
        w=np.load(runs/s/'targets.npy',mmap_mode='r');prev=np.asarray(w[:-1]);ret=np.asarray(R[253:len(R)-1]);gross=np.einsum('ij,ij->i',prev,ret)
        drift=prev*(1+ret)/(1+gross)[:,None]
        per_stock=prev*ret-c*np.abs(np.asarray(w[1:])-drift)
        error=float(np.max(np.abs(per_stock.sum(1)-net[s])))
        checks.append(dict(name=s+' stock contribution reconciliation',error=error,passed=error<1e-10));stock_pnls[s]=per_stock
    delta=stock_pnls['N0']-stock_pnls['G'];annual=252*delta.mean(0);contribution_order=np.argsort(-annual);absolute_order=np.argsort(-np.abs(annual))
    pd.DataFrame({'stock':stock_names,'index':np.arange(len(c)),'annual_net_return_difference':annual,'positive_order':np.argsort(contribution_order)+1}).to_csv(a.work/'executed_stock_attribution.csv',index=False)
    contribution=dict(total_annual_net_difference=float(annual.sum()),top_positive5_sum=float(annual[contribution_order[:5]].sum()),top_absolute5_sum=float(annual[absolute_order[:5]].sum()),positive_sum=float(annual[annual>0].sum()),negative_sum=float(annual[annual<0].sum()),top_positive=[{'stock':stock_names[i],'annual_net_difference':float(annual[i])} for i in contribution_order[:10]],top_negative=[{'stock':stock_names[i],'annual_net_difference':float(annual[i])} for i in contribution_order[-10:][::-1]])
    contrasts=[('N0','G'),('N0_s0','G_s0'),('N0_f2','G_f2'),('N0_f3','G_f3'),('D1','G'),('D5','G'),('DC','G')]
    observed=np.asarray([sharpe(net[x])-sharpe(net[y]) for x,y in contrasts]);bootstrap={};rng=np.random.default_rng(20261030)
    daily=np.asarray([net[x] for x in sorted(net)]);indexes={s:i for i,s in enumerate(sorted(net))};ia=np.array([indexes[x] for x,y in contrasts]);ib=np.array([indexes[y] for x,y in contrasts])
    # Shared circular date blocks preserve the paired nature of all contrasts.
    for block in (21,63,126):
        draws=[]
        for rep in range(3000):
            starts=rng.integers(0,n,int(np.ceil(n/block)));ix=((starts[:,None]+np.arange(block))%n).ravel()[:n]
            v=daily[:,ix];sr=np.sqrt(252)*v.mean(1)/v.std(1);draws.append(sr[ia]-sr[ib])
        draws=np.asarray(draws);p=(1+np.sum(draws-observed>=observed,axis=0))/3001
        ix=np.argsort(p);adj=np.empty(7);adj[ix]=np.minimum(1.,np.maximum.accumulate((7-np.arange(7))*p[ix]))
        bootstrap[str(block)]=[dict(candidate=x,reference=y,gain=float(observed[j]),ci95=np.quantile(draws[:,j],[.025,.975]).tolist(),centered_one_sided_p=float(p[j]),holm_7=float(adj[j])) for j,(x,y) in enumerate(contrasts)]
    block_deleted=[]
    for start in range(0,n,252):
        ix=np.ones(n,dtype=bool);ix[start:min(start+252,n)]=False
        block_deleted.append(dict(start_source_row=253+start,end_source_row_exclusive=253+min(start+252,n),gain=sharpe(net['N0'][ix])-sharpe(net['G'][ix])))
    decision=dict(reproduction=True,no_sleeve_gain=float(observed[1]),double_fee_gain=float(observed[2]),triple_fee_gain=float(observed[3]),top1_removal_gain=float(observed[4]),causal_largest_removal_gain=float(observed[6]),continue_to_release_review=bool(all(observed[j]>0 for j in (0,1,2,3,4,6))),main_promotion=False)
    result=dict(summary=summary,concentration=concentration,top_sources=sources[:15],executed_contributions=contribution,bootstrap=bootstrap,deleted_date_blocks=block_deleted,checks=checks,decision=decision,method_note='All results are from exposed development data. Full-path source-ranking deletions are hindsight diagnostics, not causal candidate-selection rules. Bootstrap inference is post-selection and does not cover the original research search.')
    H.write_json(a.work/'ASSESSMENT.json',result)
    for x,y in contrasts:print(x,summary[x]['net_sharpe'],'delta',sharpe(net[x])-sharpe(net[y]),flush=True)
    print('Concentration',concentration['top1_share'],concentration['top5_share'],concentration['ever_selected'])
    print('Top sources',sources[:5]);print('Decision',decision)
    assert all(v['passed'] for v in checks)
if __name__=='__main__':main()

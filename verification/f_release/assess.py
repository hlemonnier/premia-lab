"""Independent arithmetic and fixed statistical checks; no model search."""
from pathlib import Path
import json
import numpy as np
from runner import write
WORK=None;OLD=None

def sr(x): return float(np.sqrt(252)*np.mean(x)/np.std(x))
def beta(x,m):
    return float(np.dot(m-m.mean(),x-x.mean())/np.dot(m-m.mean(),m-m.mean()))
def evaluate():
    data={}
    for name in ('F','B0','H','R1','T','C'):
        p=WORK/'results'/f'{name}_rows.npy'
        if not p.exists():p=OLD/f'{name}_rows.npy'
        if not p.exists():p=OLD/f'{name}_rows.npy'
        data[name]=np.load(p)
    n=len(data['F']); days=np.arange(253,253+n);net={k:v[:,0]-v[:,1] for k,v in data.items()}
    result={'note':'All rows are exposed development data. New seed is a numerical sensitivity, not new evidence or a replacement of frozen Wave6 tests.','metrics':{},'paired_bootstrap':{},'subperiods':{},'annual_blocks':[],'leave_block_out':{}}
    for name,x in net.items():
        eq=np.r_[1,np.cumprod(1+x)];draw=eq/np.maximum.accumulate(eq)-1
        roll=[beta(x[s:s+252],data[name][s:s+252,3]) for s in range(n-251)]
        result['metrics'][name]={'net_sharpe':sr(x),'beta':beta(x,data[name][:,3]),'mean_ann':float(x.mean()*252),'vol_ann':float(x.std()*np.sqrt(252)),
            'annual_fees':float(data[name][:,1].mean()*252),'max_drawdown_net_proxy':float(draw.min()),'worst_net_day':float(x.min()),
            'rolling_252_beta_min':float(min(roll)),'rolling_252_beta_max':float(max(roll)),'rolling_252_beta_over_point2_fraction':float(np.mean(np.array(roll)>.2)),
            'zero_fee_fixed_positions_sharpe':sr(data[name][:,0]),'full_sample_market_residual_sharpe_descriptive_only':sr(x-beta(x,data[name][:,3])*data[name][:,3])}
        masks=[(days>=253)&(days<2016),(days>=2016)&(days<3024),(days>=3024)&(days<3779),np.arange(n)<n//2,np.arange(n)>=n//2]
        result['subperiods'][name]=[sr(x[m]) for m in masks]
    comps=['B0','H','R1','T'];arr=np.column_stack([net['F']]+[net[k] for k in comps]);rng=np.random.default_rng(20261101)
    for L in (21,63,126):
        draws=[]
        for _ in range(5000):
            starts=rng.integers(0,n,size=int(np.ceil(n/L)));idx=((starts[:,None]+np.arange(L))%n).ravel()[:n]
            a=arr[idx];s=np.sqrt(252)*a.mean(0)/a.std(0);draws.append(s[0]-s[1:])
        draws=np.array(draws);result['paired_bootstrap'][str(L)]={}
        for j,k in enumerate(comps):
            delta=sr(net['F'])-sr(net[k]);q=np.quantile(draws[:,j],[.025,.975])
            result['paired_bootstrap'][str(L)][k]={'observed_gain':delta,'interval95':q.tolist(),'fraction_positive_not_future_probability':float(np.mean(draws[:,j]>0)),
                'centered_one_sided_p_uncorrected':float((1+np.sum(draws[:,j]-delta>=delta))/5001)}
    for i,start in enumerate(range(0,n,252)):
        stop=min(n,start+252);mask=np.ones(n,bool);mask[start:stop]=False
        result['annual_blocks'].append({'block':i+1,'start_source':int(days[start]),'end_source_exclusive':int(days[stop-1]+1),'days':stop-start,
           'sharpe':{k:sr(x[start:stop]) for k,x in net.items() if k in ('F','B0','H','T')},
           'F_minus_H_net_sum':float(np.sum(net['F'][start:stop]-net['H'][start:stop]))})
        for k in comps:result['leave_block_out'].setdefault(k,[]).append(sr(net['F'][mask])-sr(net[k][mask]))
    # Single fixed tail-removal sensitivity. Not a valid deployable rule.
    largest=np.argsort(np.abs(net['F']-net['H']))[-10:];keep=np.ones(n,bool);keep[largest]=False
    result['tail_sensitivity']={'removed_count':10,'selected_by':'largest absolute paired F-H daily net difference, diagnostic only','gain_F_H_excluding':sr(net['F'][keep])-sr(net['H'][keep]),'source_rows':days[largest].tolist()}
    for name in ('F_fee2','B0_fee2','F_fee3','B0_fee3'):
        p=WORK/'results'/f'{name}.json'
        if p.exists():result.setdefault('fee_replays',{})[name]=json.loads(p.read_text())
    prior=json.loads((OLD/'assessment.json').read_text())
    result['prior_promotion_assessment']=prior
    write(WORK/'results/independent_assessment.json',result)
    print(json.dumps({'metrics':result['metrics'],'bootstrap63':result['paired_bootstrap']['63'],'leave_out_range':{k:[min(v),max(v)] for k,v in result['leave_block_out'].items()}}),flush=True)
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    WORK=a.work;OLD=WORK/'prior';evaluate()

"""Run the frozen N0 policy on a small, independently generated demonstration.

This generator is NOT the original private market and does not reproduce the
reported 1.55 Sharpe. Its score is a software demonstration, not a new result.
"""
from __future__ import annotations
import os
for _k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ.setdefault(_k,'1')
import argparse,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from model_n0 import N0Policy

def generate_market(days:int=800,stocks:int=64,seed:int=20261030):
    if days<254 or stocks<2:raise ValueError('Use at least 254 days and 2 stocks.')
    rng=np.random.default_rng(seed)
    x=np.empty((days,stocks,13),dtype=np.float64);x[0]=rng.normal(size=(stocks,13))
    for t in range(1,days):x[t]=.985*x[t-1]+np.sqrt(1-.985**2)*rng.normal(size=(stocks,13))
    coefficients=np.linspace(-.00008,.00008,13)
    market=rng.normal(.00005,.004,size=(days,1))
    errors=rng.normal(0,.008,size=(days,stocks))
    returns=market+errors
    for t in range(1,days):returns[t]+=x[t-1]@coefficients
    costs=np.linspace(.0002,.0008,stocks)
    return returns,x,costs

def replay(returns,characteristics,trading_costs):
    r=np.asarray(returns,dtype=np.float64);x=np.asarray(characteristics,dtype=np.float64);c=np.asarray(trading_costs,dtype=np.float64)
    if r.ndim!=2 or x.shape!=(*r.shape,13) or c.shape!=(r.shape[1],):raise ValueError('Incompatible shapes.')
    if len(r)<254 or not all(np.isfinite(a).all() for a in (r,x,c)) or (c<0).any():raise ValueError('Invalid histories/costs.')
    policy=N0Policy();tic=time.perf_counter();f=policy.forecast(r,x);forecast_seconds=time.perf_counter()-tic
    positions=np.zeros(r.shape[1]);weights=[];gross=[];fees=[];latencies=[]
    for observed_day in range(252,len(r)-1):
        earned=float(positions@r[observed_day])
        if earned<=-1:raise RuntimeError('Portfolio ruin on the demonstration path.')
        drifted=positions*(1+r[observed_day])/(1+earned)
        tic=time.perf_counter()
        target=np.asarray(policy.rebalance(drifted,f[observed_day+1],r[:observed_day+1],x[:observed_day+1],c))
        latencies.append(time.perf_counter()-tic)
        fee=0. if observed_day==252 else float(c@np.abs(target-drifted))
        weights.append(target.copy());gross.append(earned);fees.append(fee);positions=target
    gross=np.asarray(gross);fees=np.asarray(fees)
    return dict(forecasts=f,positions=np.asarray(weights),gross_returns=gross,costs=fees,net_returns=gross-fees,
                forecast_seconds=forecast_seconds,rebalance_ms=1000*float(np.mean(latencies)),
                provenance='independent_demo_generator_not_private_benchmark')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--days',type=int,default=800);p.add_argument('--stocks',type=int,default=64);p.add_argument('--seed',type=int,default=20261030);a=p.parse_args()
    result=replay(*generate_market(a.days,a.stocks,a.seed));net=result['net_returns'][1:];vol=float(net.std())
    out={'source':result['provenance'],'days':a.days,'stocks':a.stocks,'demo_net_sharpe':float(np.sqrt(252)*net.mean()/vol) if vol else None,
         'forecast_seconds':result['forecast_seconds'],'average_rebalance_ms':result['rebalance_ms'],
         'max_gross_exposure':float(np.abs(result['positions']).sum(1).max()),
         'warning':'This is not the private benchmark, an untouched holdout, or evidence of expected returns.'}
    print(json.dumps(out,indent=2,allow_nan=False))
if __name__=='__main__':main()

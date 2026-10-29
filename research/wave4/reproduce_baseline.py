"""Portable rerun of the original-scorer V3 baseline; no new model or tuning."""
import argparse
from pathlib import Path
import numpy as np
import run_wave4 as W


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    a=p.parse_args()
    out=a.work/'results';out.mkdir(parents=True,exist_ok=True)
    score=W.load_score(a.source)
    R,X,cost=W.load_inputs(score,a.source,a.work)
    rows,seconds=score.run(W.V3,R,X,cost)
    stats=W.summarize(rows)
    stats['forecast_seconds']=seconds
    stats['baseline_absolute_error']=abs(stats['net_sharpe']-W.EXPECTED)
    np.save(out/'B0_rows.npy',rows)
    np.save(a.work/'cache/f2.npy',W.V3.POLICY.forecast_output)
    W.save_json(out/'B0_portable_reproduction.json',stats)
    print(stats,flush=True)
    assert stats['baseline_absolute_error']<1e-9,'V3 baseline does not reproduce'


if __name__=='__main__':main()

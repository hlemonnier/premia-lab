"""Read the fixed actual candidate ledgers; no new policy or parameter search."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent


def sharpe(x, axis=0):
    return np.sqrt(252) * np.mean(x, axis=axis) / np.std(x, axis=axis)


def main():
    paths = {"V2": ROOT / "actual_001/baseline_V2", "F1": ROOT / "actual_001/F1_base",
             "F2": ROOT / "actual_001/F2_base"}
    frames = {k: pd.read_csv(p / "daily.csv") for k, p in paths.items()}
    baseline_days = frames["V2"].day.to_numpy()
    assert np.array_equal(baseline_days, np.arange(253, 3779))
    for f in frames.values():
        assert np.array_equal(f.day.to_numpy(), baseline_days)
        assert np.isfinite(f.to_numpy()).all()
        assert np.max(np.abs(f.net_return - f.gross_return + f.cost)) <= 1e-12
    matrix = np.column_stack([frames[k].net_return.to_numpy() for k in paths])
    scores = sharpe(matrix)
    result = {"n": len(matrix), "variants": list(paths), "net_sharpes": scores.tolist(),
              "differences_vs_V2": (scores - scores[0]).tolist(), "bootstrap": {}}
    for block in (21, 63, 126):
        rng = np.random.default_rng(20261027)
        samples = []
        for _ in range(2000):
            starts = rng.integers(0, len(matrix) - block + 1, size=int(np.ceil(len(matrix) / block)))
            index = (starts[:, None] + np.arange(block)).ravel()[:len(matrix)]
            s = sharpe(matrix[index])
            samples.append(s - s[0])
        samples = np.asarray(samples)
        result["bootstrap"][str(block)] = {"draws": 2000, "seed": 20261027,
                    "method": "paired moving-block percentile; legal final start included",
                    "interval_95": np.quantile(samples, [.025, .975], axis=0).T.tolist(),
                    "fraction_positive": np.mean(samples > 0, axis=0).tolist()}
    result["summaries"] = {k: json.loads((p / "summary.json").read_text()) for k, p in paths.items()}
    (ROOT / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "summaries"}, indent=2))


if __name__ == "__main__":
    main()

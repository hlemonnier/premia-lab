# Root independent actual accounting readbacks

Both commands executed with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
MKL_NUM_THREADS=1`, on CPU 0. They use the same independently accepted source
SHA256 `c3da767a7240ecabec9f5c00bb83c7b0e843209badcf91336701d5ee1fbd4d5b`.
No policy is imported, executed, refit or selected by this script.

Data argument for both commands:
`/workspace/scratch/a83c191d516f/v2-original-input/extracted/Quant Research Take-Home`.
Reference argument for both commands:
`evidence/v2_score_joint_20261028/actual_001/joint_F2_VTvol/daily.csv`.

## Standalone readback, exit 0

`taskset -c 0 python evidence/v2_score2_root_20261029/actual_readback.py` with the
`--data` and `--reference` arguments above, plus:

```text
--candidate baseline=evidence/v2_score2_execution_20261029/actual_001/baseline
--candidate E1=evidence/v2_score2_execution_20261029/actual_001/E1
--candidate E2=evidence/v2_score2_execution_20261029/actual_001/E2
--candidate F3=evidence/v2_score2_forecast_20261029/actual_001/F3_VTvol
--candidate M0=evidence/v2_score2_review_20261029/m1/actual_001/M0
--candidate M1=evidence/v2_score2_review_20261029/m1/actual_001/M1
--out evidence/v2_score2_root_20261029/standalone_readback_001.json
```

Original stdout/stderr are preserved next to the result. Result SHA256:
`af16207ccedc0cb380e332041f4d90260dd1af75db21d0fdb195c6db30c57926`.
Maximum reconstructed gross-return/fee/gross-exposure/market error: `6.94e-18`.

## Selected joint readback, exit 0

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 0 \
python evidence/v2_score2_root_20261029/actual_readback.py \
  --data '/workspace/scratch/a83c191d516f/v2-original-input/extracted/Quant Research Take-Home' \
  --reference evidence/v2_score_joint_20261028/actual_001/joint_F2_VTvol/daily.csv \
  --candidate joint_E2_M1=evidence/v2_score2_joint_20261029/actual_001/E2_M1 \
  --candidate M1=evidence/v2_score2_review_20261029/m1/actual_001/M1 \
  --out evidence/v2_score2_root_20261029/joint_readback_001.json \
  > evidence/v2_score2_root_20261029/joint_readback_001.stdout.log \
  2> evidence/v2_score2_root_20261029/joint_readback_001.stderr.log
```

Result SHA256:
`565c895d63e2dc7ee2e511bb47514c09fd08da841b6111c6b6cb5b007bb25e6f`.
Joint score: `1.444733300556666`. Maximum joint accounting error: `5.20417e-18`.
The script verifies original input hashes and each consumed array's declared
file SHA256, raw-array SHA256, dtype and shape before reconstructing economics.

The paired 63-day fixed-policy interval for the Sharpe difference is
`[0.04512627884817285, 0.19414854892191136]` versus the prior leader and
`[0.007364008651822686, 0.02975074739930807]` versus M1. These are descriptive
development-history intervals, not correction for research selection or a fresh
confirmation sample. Block lengths 21 and 126 are retained in the same JSON.

For portable reruns, substitute the original input directory and choose a new
`--out`; never overwrite these original results. See `EVIDENCE_RESTORATION.md`
for omitted large arrays and preserved executable snapshots.

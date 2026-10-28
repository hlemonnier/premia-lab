import json, os, pathlib, subprocess, sys, time
root = pathlib.Path(__file__).resolve().parent
env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONPATH="/tmp/v2-allocator-review-deps")
cmd = [sys.executable, "/workspace/scratch/a83c191d516f/v2-review-snapshot/research/v2/test_allocator.py"]
versions = subprocess.run([sys.executable, "-c", "import sys,numpy,scipy,cvxpy,clarabel,json;print(json.dumps(dict(python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,cvxpy=cvxpy.__version__,clarabel=clarabel.__version__)))"], env=env, capture_output=True, text=True)
t0=time.perf_counter()
r=subprocess.run(cmd, env=env, capture_output=True, text=True)
(root/"stdout.txt").write_text(r.stdout)
(root/"stderr.txt").write_text(r.stderr)
result=dict(command=cmd, environment={k:env[k] for k in ["OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","PYTHONPATH"]}, versions=json.loads(versions.stdout) if versions.returncode==0 else {"error": versions.stderr}, exit_code=r.returncode, elapsed_seconds=time.perf_counter()-t0, supplied_pass_lines=r.stdout.count("PASS "), supplied_fail_lines=r.stdout.count("FAIL "))
(root/"result.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
sys.exit(r.returncode)

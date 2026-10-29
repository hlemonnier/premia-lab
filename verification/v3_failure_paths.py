"""Run the allocator failure-path checks (verification/v2_failure_paths.py) against handoff_v3's copies.

model_v3.engine and model_v3.allocator are byte copies of model_v2's; this wrapper makes the
existing checks import the v3 modules instead, so the evidence is about the shipped files.
python verification/v3_failure_paths.py
"""
import os, runpy, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
import model_v3, model_v3.engine, model_v3.allocator  # noqa: E402,E401

sys.modules["model_v2"] = model_v3
sys.modules["model_v2.engine"] = model_v3.engine
sys.modules["model_v2.allocator"] = model_v3.allocator
assert sys.modules["model_v2.allocator"].__file__.endswith(os.path.join("model_v3", "allocator.py"))
sys.argv = [os.path.join(ROOT, "verification", "v2_failure_paths.py")] + sys.argv[1:]
sys.path.insert(0, os.path.join(ROOT, "verification"))
runpy.run_path(sys.argv[0], run_name="__main__")

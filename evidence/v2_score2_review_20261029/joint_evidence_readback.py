"""Independent saved-evidence audit; no policy import or execution."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
from execution_evidence_readback import declared_fixture


HERE = Path(__file__).resolve().parent
POLICY = HERE.parent / "v2_score2_joint_20261029"
RUN = POLICY / "synthetic_001"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def raw(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def maxerr(a, b):
    return float(np.max(np.abs(np.asarray(a)-np.asarray(b)), initial=0.0))


def run():
    result_path = RUN / "result.json"
    assert sha(result_path) == "f23fa2a55efaf9bbf6c8b120bfdeded7daec33ac961baef17dc68082410fdbe5"
    result = json.loads(result_path.read_text())
    source_review = json.loads((HERE / "joint_source_review.json").read_text())
    assert result["all_passed"] and all(v["pass"] for v in result["checks"].values())
    assert result["source_sha256"] == source_review["source_sha256"]
    for name, expected in result["source_sha256"].items():
        assert sha(POLICY / name) == sha(RUN / ("executed_"+name)) == expected
    for name, expected in result["baseline_source_sha256"].items():
        assert sha(RUN / "source" / name) == expected
    artifacts = json.loads((RUN / "artifact_manifest.json").read_text())
    for name, expected in artifacts.items():
        assert sha(RUN / name) == expected, name
    arrays, summaries, manifests = {}, {}, {}
    verified_arrays = 0
    for path in sorted(RUN.glob("*/array_manifest.json")):
        name = path.parent.name
        arrays[name] = {}
        manifests[name] = json.loads(path.read_text())
        summaries[name] = json.loads((path.parent / "summary.json").read_text())
        assert summaries[name]["all_passed"] and all(summaries[name]["checks"].values())
        for key, spec in manifests[name].items():
            f = path.parent / spec["path"]
            a = np.load(f, allow_pickle=False)
            assert list(a.shape) == spec["shape"] and str(a.dtype) == spec["dtype"]
            assert sha(f) == spec["file_sha256"] and raw(a) == spec["array_sha256"]
            assert spec["readback_exact"]
            arrays[name][key] = a
            verified_arrays += 1
    default_r, default_x, default_c = declared_fixture()
    assert [raw(a) for a in (default_r, default_x, default_c)] == json.loads((RUN / "input_manifest.json").read_text())["array_sha256"]
    toy_r = np.array([[0,0,0],[-.01,.03,.005],[.02,-.01,.01],[-.03,.01,.02],
                      [.01,.01,.01],[-.02,0,.01],[.005,-.007,.012],[0,0,0]])
    known = {"known_netting_reversals", "forced_outer_cap"}
    ordinary = arrays["E2_M1"]
    trimmed = arrays["joint_trimmed"]
    for key in ("targets", "inner_targets", "virtual_targets"):
        expected = raw(ordinary[key])
        assert summaries["E2_M1"]["decision_hashes"][key] == expected
        assert summaries["joint_trimmed"]["decision_hashes"][key] == expected
        assert np.array_equal(ordinary[key][-1], trimmed["final_"+key])
    assert np.array_equal(ordinary["rows"][:, :4], trimmed["rows"][:, :4])
    assert np.array_equal(ordinary["forecast"], trimmed["forecast"])
    observed = {}
    for name, saved in arrays.items():
        r, x, c = default_r, default_x, default_c
        if name == "joint_future":
            r, x = r.copy(), x.copy()
            r[360:] = -.6*r[360:] + .0007
            x[360:] = np.flip(x[360:], axis=1)+.2
        elif name == "joint_prefix":
            r, x = r[:361], x[:361]
        elif name == "joint_zero_returns":
            r = np.zeros_like(r)
        elif name.startswith("extreme_"):
            r, x, c = declared_fixture(128)
        elif name in known:
            r, x, c = toy_r, np.zeros((8,3,13)), np.array([.001,.002,.003])
        assert [raw(a) for a in (r,x,c)] == summaries[name]["input_array_sha256"]
        # The reduced-recording case is bound to full saved paths by the three
        # independent stream hashes checked above; use that equivalent path.
        books = ordinary if name == "joint_trimmed" else saved
        target, inner, virtual = (books[k] for k in ("targets", "inner_targets", "virtual_targets"))
        idx = saved["decision_indices"]
        start = 0 if name in known else 252
        assert np.array_equal(idx, np.arange(start,len(r)-1))
        assert len(saved["rows"]) == len(idx)-1
        earning = r[idx[1:]]
        gross = np.sum(target[:-1]*earning, axis=1)
        held = target[:-1]*(1+earning)/(1+gross[:,None])
        fee = np.sum(np.abs(target[1:]-held)*c, axis=1)
        reconstructed = np.column_stack((gross, fee, np.abs(target[1:]).sum(axis=1), earning.mean(axis=1)))
        actual_error = maxerr(reconstructed,saved["rows"][:,:4])
        inner_gross = np.sum(inner[:-1]*earning, axis=1)
        inner_held = inner[:-1]*(1+earning)/(1+inner_gross[:,None])
        inner_fee = np.sum(np.abs(inner[1:]-inner_held)*c, axis=1)
        records = list(csv.DictReader((RUN / name / "decisions.csv").open()))
        assert float(records[0]["actual_fee"]) == float(records[0]["inner_fee"]) == 0
        inner_fee_error = maxerr(inner_fee,[float(v["inner_fee"]) for v in records[1:]])
        virtual_returns = np.r_[0.,np.sum(virtual[:-1]*earning,axis=1)]
        virtual_error = maxerr(virtual_returns,saved["virtual_returns"])
        independent_controller = []
        for j in range(len(idx)):
            q = {}
            for horizon in (63,1008):
                weights = 2.**(-np.arange(j-1,-1,-1)/horizon)
                q[horizon] = float(weights@(virtual_returns[1:j+1]**2)/weights.sum()) if j else 0.
            a = 1. if j < 63 else float(np.clip(np.sqrt(max(q[1008],1e-12)/max(q[63],1e-12)),.5,2.))
            independent_controller.append([q[63],q[1008],a])
        controller_error = maxerr(independent_controller,saved["controller_trace"])
        sleeve = 0. if name in ("standalone_E2","M0_E2","extreme_standalone_E2") else .05
        proposed = inner+sleeve/inner.shape[1]
        scale = np.minimum(1.,5/np.maximum(np.abs(proposed).sum(axis=1),1e-300))
        target_error = maxerr(target,proposed*scale[:,None])
        assert max(actual_error,inner_fee_error,virtual_error,controller_error,target_error) <= 1e-12
        observed[name] = {"decisions":len(idx),"earning_rows":len(idx)-1,
            "actual_accounting_max_error":actual_error,"inner_fee_max_error":inner_fee_error,
            "virtual_return_max_error":virtual_error,"explicit_weight_controller_max_error":controller_error,
            "target_formula_max_error":target_error,"gross_cap_count":int((scale<1).sum()),
            "trimmed_path_bound_to_full_three_book_hashes": name == "joint_trimmed"}
    base = arrays["standalone_E2"]
    m0 = arrays["M0_E2"]
    for key in ("forecast","targets","inner_targets","virtual_targets","virtual_returns","controller_trace"):
        assert np.array_equal(base[key],m0[key])
    assert np.array_equal(base["rows"][:,:4],m0["rows"][:,:4])
    for base_name,joint_name in (("standalone_E2","E2_M1"),("extreme_standalone_E2","extreme_joint")):
        a,b=arrays[base_name],arrays[joint_name]
        assert np.array_equal(a["targets"],b["inner_targets"])
        for key in ("forecast","virtual_targets","virtual_returns","controller_trace"):
            assert np.array_equal(a[key],b[key])
    for name,nf,nt,nr in (("joint_future",361,108,107),("joint_prefix",361,108,107),("joint_restart",420,167,166)):
        case=arrays[name]
        assert np.array_equal(ordinary["forecast"][:nf],case["forecast"][:nf])
        assert np.array_equal(ordinary["rows"][:nr,:4],case["rows"][:nr,:4])
        for key in ("targets","inner_targets","virtual_targets","virtual_returns","controller_trace"):
            assert np.array_equal(ordinary[key][:nt],case[key][:nt])
    assert observed["forced_outer_cap"]["gross_cap_count"] == observed["forced_outer_cap"]["decisions"]
    assert np.array_equal(arrays["forced_outer_cap"]["inner_targets"],np.full_like(arrays["forced_outer_cap"]["inner_targets"],4.99/3))
    report={"reviewer":"score2_challenge","decision":"accepted_for_root_actual_release",
        "required_changes":[],"scope_sha256":sha(HERE/"JOINT_REVIEW_SCOPE.md"),
        "source_review_sha256":sha(HERE/"joint_source_review.json"),"audit_script_sha256":sha(__file__),
        "fixture_reconstruction_source_sha256":sha(HERE/"execution_evidence_readback.py"),
        "synthetic_result_sha256":sha(result_path),"source_sha256":result["source_sha256"],
        "summary_checks":len(result["checks"]),"workflow_checks":sum(len(v["checks"]) for v in summaries.values()),
        "artifact_files_verified":len(artifacts),"atomic_arrays_verified":verified_arrays,
        "independent_workflow_reconstruction":observed,"temporal_inner_M0_trimmed_identities_exact":True,
        "limitations":["No policy was executed by this audit.","Runtime observation equivalence is verified on the prospective synthetic path; the century gate remains outstanding.","The one actual joint economic run still requires the source-bound root release."]}
    (HERE/"joint_synthetic_review.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("decision","summary_checks","workflow_checks","artifact_files_verified","atomic_arrays_verified")},indent=2))
    print("Maximum actual accounting discrepancy:",max(v["actual_accounting_max_error"] for v in observed.values()))
    print("Maximum explicit-weight controller discrepancy:",max(v["explicit_weight_controller_max_error"] for v in observed.values()))


if __name__ == "__main__":
    run()

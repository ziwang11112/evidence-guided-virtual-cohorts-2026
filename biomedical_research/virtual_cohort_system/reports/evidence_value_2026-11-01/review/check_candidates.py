"""Independent static review only: no candidate import or row generation."""
from pathlib import Path
import ast
import hashlib
import json
import math
from datetime import datetime, timezone
from cohort_harness.__main__ import validate_bundle
from cohort_harness.lifecycle import _checks

UNIT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def audit(arm):
    bundle = UNIT / "bundles" / arm
    candidate = bundle / "candidates" / "initial"
    assert not (candidate / "freeze.json").exists()
    assert not (bundle / "executions").exists()
    task = read(bundle / "task.json")
    evidence = read(bundle / "evidence.json")
    spec = read(candidate / "model_spec.json")
    assert (candidate / "evidence.json").read_bytes() == (bundle / "evidence.json").read_bytes()
    assert task["mode"] == "whole_cohort" and task["n_rows"] == 3000
    assert task["budget"]["revisions"] == 0
    contract = validate_bundle(bundle, candidate)
    assert contract["route"] == "program" and not contract["generator_executed"]
    _checks(candidate)
    for artifact in read(bundle / "registry.json")["artifacts"]:
        assert digest(bundle / artifact["path"]) == artifact["sha256"]
    tree = ast.parse((candidate / "generator.py").read_text(encoding="utf-8"))
    imports = sorted(alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names)
    assert imports == ["numpy", "pandas"]
    assert not any(isinstance(node, ast.ImportFrom) for node in ast.walk(tree))
    forbidden = {"open", "eval", "exec", "compile", "__import__"}
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in forbidden for node in ast.walk(tree))
    p = spec["parameters"]
    assert p["n_rows"] == 3000
    differences = []
    if arm == "A":
        assert evidence["items"] == [] and evidence["sources"] == []
        assert p["probability_g1"] == .75
        assert all(not ref["evidence_ids"] and ref["assumption_ids"] for ref in spec["parameter_provenance"].values())
        limitations = ["No numerical source evidence; all x/y parameters are explicitly unsupported prior choices.", "Zero association and equal group laws are assumptions, not evidence-derived conclusions."]
    else:
        if arm == "B":
            mx, sx = p["x_group_mean"], p["x_group_sd"]
            a, b, sr = p["y_group_intercept"], p["y_group_x_slope"], p["y_group_residual_sd"]
            target_p = p["target_g_probability"]
        elif arm == "C":
            mx, sx = p["x_group_mean"], p["x_group_sd"]
            a, b, sr = p["y_group_intercept"], p["y_group_slope"], p["y_group_residual_sd"]
            target_p = p["group_probability"]
        else:
            mx, sx = p["x_mean_by_g"], p["x_sd_by_g"]
            a, b, sr = p["y_intercept_by_g"], p["y_slope_by_g"], p["residual_sd_by_g"]
            target_p = p["g_probability"]
        assert target_p == .75
        supplied = {item["id"]: item["estimate"] for item in evidence["items"]}
        ps = supplied["E_G_MEAN"]
        weights = (1-ps, ps)
        mean_x = sum(w*m for w,m in zip(weights,mx))
        mean_y_group = [a[k]+b[k]*mx[k] for k in range(2)]
        mean_y = sum(w*m for w,m in zip(weights,mean_y_group))
        second_x = sum(weights[k]*(sx[k]**2+mx[k]**2) for k in range(2))
        second_y = sum(weights[k]*(b[k]**2*sx[k]**2+sr[k]**2+mean_y_group[k]**2) for k in range(2))
        cross_xy = sum(weights[k]*(b[k]*sx[k]**2+mx[k]*mean_y_group[k]) for k in range(2))
        model = {
            "E_G_MEAN": ps, "E_G_SD": math.sqrt(ps*(1-ps)),
            "E_X_MEAN": mean_x, "E_X_SD": math.sqrt(second_x-mean_x**2),
            "E_Y_MEAN": mean_y, "E_Y_SD": math.sqrt(second_y-mean_y**2),
            "E_COV_G_X": ps*mx[1]-ps*mean_x,
            "E_COV_G_Y": ps*mean_y_group[1]-ps*mean_y,
            "E_COV_X_Y": cross_xy-mean_x*mean_y,
        }
        if arm in "CD":
            for k in range(2):
                model.update({f"E_G{k}_X_MEAN":mx[k],f"E_G{k}_X_SD":sx[k],f"E_G{k}_Y_INTERCEPT":a[k],f"E_G{k}_Y_SLOPE":b[k],f"E_G{k}_RESIDUAL_SD":sr[k]})
        assert set(model) == set(supplied)
        for key, value in model.items():
            error = abs(value-supplied[key])
            assert error < 1e-12
            differences.append({"evidence_id":key,"independent_declared_model_functional":value,"supplied_functional":supplied[key],"absolute_difference":error})
        if arm == "B":
            limitations = ["Common conditional slope and equal group covariance are explicitly assumed; pooled moments do not identify them.", "Gaussian x and residual laws, residual independence and threshold behavior are unsupported completions."]
        else:
            limitations = ["Group-specific conditional first and second moments are supported by this artificial packet.", "Gaussian shapes, full residual independence and threshold behavior remain assumptions; conditional moments do not identify a complete joint distribution."]
    limits = limitations + ["All rows are fictional; no biomedical or clinical validity follows.", "Static source algebra and interface validation do not establish runtime output accuracy.", "Permitted-input provenance is based on packet/artifact inspection and constructor declarations; this review is not an independent audit of every tool access or a secure access boundary.", "Three sampling seeds will not measure uncertainty in model choices or repeat independent scientific authoring."]
    files = {q.relative_to(candidate).as_posix():digest(q) for q in sorted(candidate.rglob("*")) if q.is_file() and "__pycache__" not in q.parts}
    result = {
        "decision":"approved", "independent":True,
        "reviewer_id":"/root/ev_candidate_review", "builder_id":f"/root/ev_builder_{arm.lower()}",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "candidate_files":files,
        "scope":"Static interface, admitted-evidence algebra, provenance and code/spec correspondence; no hidden reference, row generation, execution, selection or scientific modification.",
        "contract":contract, "checks_artifact_binding":"passed", "registered_source_hashes":"passed",
        "imports":imports,"manual_code_spec_correspondence":"passed",
        "review_script_sha256":digest(Path(__file__)),
        "independent_source_algebra":differences,
        "findings":limits,
        "required_repairs":[], "scientific_accuracy":"not_assessed"
    }
    destination = UNIT / "review" / f"{arm}_CANDIDATE.json"
    with destination.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,indent=2,allow_nan=False)
        handle.write("\n")
    return {"arm":arm,"decision":"approved","files":len(files),"source_functionals_checked":len(differences),"review_sha256":digest(destination)}

if __name__ == "__main__":
    print(json.dumps([audit(arm) for arm in "ABCD"],indent=2))

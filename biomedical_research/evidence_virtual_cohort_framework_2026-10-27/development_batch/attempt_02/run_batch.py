"""Immutable retrospective batch. Does not import or execute any generator."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import runpy
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import statsmodels

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[2]
PAPER = BASE / "obesity_paper_replay_2026-10-27"
MASKED = BASE / "obesity_masked_completion_2026-10-27"
KEYS = ["person_id", "month"]
VARIABLES = ["pfs", "gng", "dd100", "dd1000"]
CONTRASTS = ["month_3_minus_0", "month_6_minus_0", "month_9_minus_0", "month_12_minus_0", "month_12_minus_3"]
PAIRS = [(x, y) for i, x in enumerate(VARIABLES) for y in VARIABLES[i + 1:]]
EXPECTED = [("baseline_pearson", f"{x}__{y}") for x, y in PAIRS]
EXPECTED += [(f"{v}_time_reml", t) for v in ["weight", *VARIABLES] for t in CONTRASTS]
EXPECTED += [("pooled_standardized_reml", x) for x in VARIABLES]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(clean(value), stream, indent=2, allow_nan=False)
        stream.write("\n")


def check_hash(path, expected):
    if sha(path) != expected:
        raise ValueError(f"Hash mismatch: {path}")


def local(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Manifest path escaped source root")
    return path


def original_verification():
    """Verify source bytes before loading any patient table or analysis module."""
    files = {}
    def manifest(path, root):
        obj = read(path)
        files[str(path)] = sha(path)
        for name, expected in obj["files"].items():
            p = local(root, name)
            check_hash(p, expected)
            files[str(p)] = expected
        return obj
    paper = manifest(PAPER / "evaluation_freeze.json", PAPER)
    if paper["seeds"] != list(range(271001, 271021)):
        raise ValueError("Unexpected frozen synthetic seeds")
    for version in ("initial", "final"):
        run = PAPER / "runs" / version
        lock = manifest(run / "execution_lock.json", run)
        check_hash(run / "engine/run_generation.py", lock["driver_sha256"])
    masked = manifest(MASKED / "freeze.json", MASKED)
    for label in ("reference", "analysis_module"):
        rec = masked[label]
        check_hash(rec["path"], rec["sha256"])
        files[rec["path"]] = rec["sha256"]
    config = read(ROOT / "config.json")
    check_hash(PAPER / "paper_analysis.py", config["source_analysis_sha256"])
    check_hash(PAPER / "evaluation/real.csv", config["reference_sha256"])
    results = PAPER / "evaluation/comparison"
    cache = manifest(results / "evaluation_manifest.json", results)
    check_hash(PAPER / "evaluation_freeze.json", cache["input_freeze_sha256"])
    if masked["m"] != 20 or set(masked["cases"]) != set(config["cases"]):
        raise ValueError("Unexpected completion inventory")
    registry = [{"dataset_id": "reference", "kind": "reference", "method": "reference", "case": "unmasked", "draw": None, "path": str(PAPER / "evaluation/real.csv")}]
    for case in config["cases"]:
        entry = masked["cases"][case]
        registry.append({"dataset_id": f"missing_only/{case}", "kind": "missing_only", "method": "missing_only", "case": case, "draw": None, "path": str(MASKED / entry["masked"]), "targets": str(MASKED / entry["targets"])})
        if set(entry["outputs"]) != set(config["methods"]):
            raise ValueError("Completion method inventory changed")
        for method in config["methods"]:
            paths = entry["outputs"][method]
            if len(paths) != 20 or len(set(paths)) != 20:
                raise ValueError("Completion count is not 20")
            for draw, relative in enumerate(paths, 1):
                registry.append({"dataset_id": f"completion/{case}/{method}/{draw:02d}", "kind": "completion", "method": method, "case": case, "draw": draw, "path": str(MASKED / relative), "masked": str(MASKED / entry["masked"]), "targets": str(MASKED / entry["targets"])})
    for seed in paper["seeds"]:
        registry.append({"dataset_id": f"full_synthetic/{seed}", "kind": "full_synthetic", "method": "frozen_final_program", "case": "full_generation", "draw": seed, "path": str(PAPER / "runs/final/samples" / f"cohort_{seed}.csv")})
    if len(registry) != 144 or len({x["dataset_id"] for x in registry}) != 144:
        raise ValueError("Dataset inventory is not exactly 144")
    for rec in registry:
        rec["sha256"] = files.get(rec["path"], sha(rec["path"]))
        if rec["sha256"] != sha(rec["path"]):
            raise ValueError("Dataset hash changed")
    generated = [r["sha256"] for r in registry if r["kind"] == "full_synthetic"]
    if len(set(generated)) != 20:
        raise ValueError("Synthetic cohorts are not 20 unique tables")
    return files, registry


def freeze():
    files, registry = original_verification()
    own = {name: sha(ROOT / name) for name in ["run_batch.py", "test_batch.py", "config.json", "README.md"]}
    write_new(ROOT / "freeze.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "scope": "Known-results retrospective development only", "source_files": files, "implementation_files": own, "registry": registry, "runtime": runtime()})
    print(json.dumps({"frozen_datasets": len(registry), "verified_source_files": len(files)}))


def runtime():
    return {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__, "statsmodels": statsmodels.__version__}


def verify():
    frozen = read(ROOT / "freeze.json")
    for p, expected in frozen["source_files"].items():
        check_hash(p, expected)
    for p, expected in frozen["implementation_files"].items():
        check_hash(ROOT / p, expected)
    if runtime() != frozen["runtime"]:
        raise ValueError("Runtime differs from batch freeze")
    return frozen


def affected(record):
    return record["analysis"] == "pfs_time_reml" or (record["analysis"] == "pooled_standardized_reml" and record["term"] == "pfs")


def index_records(records, expected=EXPECTED):
    index = {}
    for r in records:
        key = (r["analysis"], r["term"])
        if key in index:
            raise ValueError(f"Duplicate analysis key {key}")
        index[key] = r
    if set(index) != set(expected):
        raise ValueError("Analysis key inventory mismatch")
    return index


def valid(record):
    return record.get("status") == "ok" and all(record.get(k) is not None and math.isfinite(record[k]) for k in ["estimate", "se", "ci_low", "ci_high"]) and record["se"] > 0 and record["ci_low"] <= record["ci_high"]


def safe_failure(error):
    # Pandas equality exceptions can include entire clinical-value arrays.
    return f"{type(error).__name__}: dataset contract or analysis execution failed; value-bearing exception text suppressed"


def safe_record(record):
    record = copy.deepcopy(record)
    status = record.get("status", "")
    if status.startswith("fit_failed:"):
        record["status"] = ":".join(status.split(":", 2)[:2])
        record["exception_detail_suppressed"] = True
    return record


def ci_state(record):
    if not valid(record):
        return "unavailable"
    if record["ci_low"] > 0:
        return "positive"
    if record["ci_high"] < 0:
        return "negative"
    return "uncertain"


def compare(record, reference):
    answer = {"ci_state": ci_state(record), "reference_ci_state": ci_state(reference), "reference_estimate": reference.get("estimate"), "reference_se": reference.get("se"), "reference_ci_low": reference.get("ci_low"), "reference_ci_high": reference.get("ci_high"), "comparison_status": "unavailable"}
    if valid(record) and valid(reference):
        error = record["estimate"] - reference["estimate"]
        answer.update(comparison_status="ok", signed_error=error, absolute_error=abs(error), error_in_reference_se=error / reference["se"], se_ratio=record["se"] / reference["se"], ci_state_agreement=ci_state(record) == ci_state(reference), point_sign_agreement=bool(np.sign(record["estimate"]) == np.sign(reference["estimate"])))
    return answer


def unchanged_inputs(reference, candidate):
    if not reference[KEYS].equals(candidate[KEYS]):
        raise ValueError("Preservation control key/order mismatch")
    pd.testing.assert_frame_equal(reference.drop(columns="pfs"), candidate.drop(columns="pfs"), check_exact=True)
    pd.testing.assert_frame_equal(reference.loc[reference.month.eq(0)], candidate.loc[candidate.month.eq(0)], check_exact=True)


def copy_controls(reference_records, reference_frame, candidate):
    unchanged_inputs(reference_frame, candidate)
    return [dict(copy.deepcopy(r), computation="copied_after_exact_input_preservation_check") for r in reference_records if not affected(r)]


def pool_group(records, kind, pooler, expected_m=20):
    if kind != "completion" or not all(affected(r) for r in records):
        raise ValueError("Rubin pooling is restricted to PFS-affected completion outcomes")
    if len({(r["analysis"], r["term"]) for r in records}) != 1:
        raise ValueError("Pooling attempted across analysis keys")
    if len(records) != expected_m or not all(valid(r) for r in records):
        return {"status": "incomplete_arm", "m_expected": expected_m, "m_valid": sum(valid(r) for r in records), "estimate": None, "se": None, "ci_low": None, "ci_high": None}
    return pooler([r["estimate"] for r in records], [r["se"] for r in records])


def load_modules():
    sys.path.insert(0, str(MASKED / "custodian"))
    evaluator = runpy.run_path(str(MASKED / "custodian/evaluate.py"))
    evaluator["verify_freeze"](read(MASKED / "freeze.json"), MASKED)
    analysis = runpy.run_path(str(PAPER / "paper_analysis.py"))
    return analysis, evaluator


def classify(record, item):
    family = "exploratory_proxy" if record["analysis"] == "pooled_standardized_reml" else "paper_replay"
    exposure = "unprovided_baseline_relationship" if record["analysis"] == "baseline_pearson" else ("source_marginal_constrained_trajectory" if record["analysis"].endswith("_time_reml") else "unprovided_exploratory_proxy")
    influence = ("PFS_affected" if affected(record) else "unchanged_preservation_control") if item["kind"] in {"completion", "missing_only"} else "not_a_completion"
    return {"analysis_family": family, "generation_evidence_role": exposure, "completion_role": influence, "evidence_status": "retrospective_development", "original_analysis_role": record.get("role")}


def execute(smoke=False):
    frozen = verify()
    dest = ROOT / ("smoke" if smoke else "results")
    if dest.exists():
        raise FileExistsError(f"Refusing to overwrite {dest}")
    dest.mkdir()
    write_new(dest / "execution_start.json", {"freeze_sha256": sha(ROOT / "freeze.json"), "utc": datetime.now(timezone.utc).isoformat(), "mode": "smoke" if smoke else "full", "runtime": runtime()})
    started = time.perf_counter()
    analysis, evaluator = load_modules()
    reference_frame = pd.read_csv(PAPER / "evaluation/real.csv", float_precision="round_trip")
    reference_records = [dict(r, computation="fresh_frozen_function") for r in analysis["analyze"](reference_frame, include_exploratory=True)]
    reference = index_records(reference_records)
    registry = frozen["registry"]
    if smoke:
        registry = [r for r in registry if r["kind"] in {"reference", "missing_only"} or (r["kind"] == "completion" and r["draw"] == 1) or (r["kind"] == "full_synthetic" and r["draw"] == 271001)]
    rows, failures, missing = [], [], {}
    for i, item in enumerate(registry, 1):
        try:
            frame = pd.read_csv(item["path"], float_precision="round_trip")
            analysis["validate_input"](frame)
            if item["kind"] == "reference":
                records = copy.deepcopy(reference_records)
            elif item["kind"] == "full_synthetic":
                records = [dict(r, computation="fresh_frozen_function") for r in analysis["analyze"](frame, include_exploratory=True)]
            else:
                targets = pd.read_csv(item["targets"], float_precision="round_trip")
                if item["kind"] == "completion":
                    evaluator["assert_mask_contract"](reference_frame, pd.read_csv(item["masked"], float_precision="round_trip"), targets)
                    evaluator["validate_completion"](Path(item["masked"]), Path(item["targets"]), Path(item["path"]))
                else:
                    evaluator["assert_mask_contract"](reference_frame, frame, targets)
                records = copy_controls(reference_records, reference_frame, frame)
                records += [dict(r, computation="fresh_frozen_function") for r in analysis["time_trajectory"](frame, "pfs")]
                records += [dict(r, computation="fresh_frozen_function") for r in analysis["pooled_associations"](frame) if r["term"] == "pfs"]
            current = index_records(records)
        except Exception as error:
            reason = safe_failure(error)
            failures.append({"dataset_id": item["dataset_id"], "reason": reason})
            current = {key: {"analysis": key[0], "term": key[1], "estimate": None, "se": None, "ci_low": None, "ci_high": None, "status": "dataset_failed", "failure": reason} for key in EXPECTED}
        for key in EXPECTED:
            record = safe_record(current[key])
            row = {k: item[k] for k in ["dataset_id", "kind", "method", "case", "draw", "sha256"]}
            row.update(record)
            row.update(classify(record, item))
            row.update(compare(record, reference[key]))
            rows.append(row)
            if item["kind"] == "missing_only":
                missing[(item["case"], key)] = row
            if not valid(record):
                failures.append({"dataset_id": item["dataset_id"], "analysis": key[0], "term": key[1], "reason": record.get("status")})
        if i % 10 == 0 or i == len(registry):
            print(f"Processed {i}/{len(registry)} datasets", flush=True)
    pooled = []
    if not smoke:
        for case in read(ROOT / "config.json")["cases"]:
            for method in read(ROOT / "config.json")["methods"]:
                for key in [k for k in EXPECTED if affected({"analysis": k[0], "term": k[1]})]:
                    selected = [r for r in rows if r["kind"] == "completion" and r["case"] == case and r["method"] == method and (r["analysis"], r["term"]) == key]
                    p = {"case": case, "method": method, "analysis": key[0], "term": key[1], **pool_group(selected, "completion", evaluator["pool_rubin"])}
                    p.update(compare(p, reference[key]))
                    baseline = missing[(case, key)]
                    p["missing_only_absolute_error"] = baseline.get("absolute_error")
                    p["absolute_error_improvement_over_missing_only"] = baseline["absolute_error"] - p["absolute_error"] if p["comparison_status"] == "ok" and baseline["comparison_status"] == "ok" else None
                    pooled.append(p)
    if len(rows) != len(registry) * 35:
        raise AssertionError("Output denominator changed")
    verify()
    df = pd.DataFrame(clean(rows))
    df.to_csv(dest / "all_results.csv", index=False)
    if not smoke:
        pd.DataFrame(clean(pooled)).to_csv(dest / "completion_pooled.csv", index=False)
        summary = []
        for key in EXPECTED:
            group = [r for r in rows if r["kind"] == "full_synthetic" and (r["analysis"], r["term"]) == key]
            good = [r for r in group if r["comparison_status"] == "ok"]
            summary.append({"analysis": key[0], "term": key[1], "generation_evidence_role": group[0]["generation_evidence_role"], "n_expected": 20, "n_valid": len(good), "mean_absolute_error_valid": float(np.mean([r["absolute_error"] for r in good])) if good else None, "min_estimate_valid": min([r["estimate"] for r in good], default=None), "max_estimate_valid": max([r["estimate"] for r in good], default=None), "ci_state_agreement_n": sum(r["ci_state_agreement"] for r in good), "agreement_denominator": 20, "uncertainty_scope": "Descriptive Monte Carlo range only; one frozen generator, no new participants"})
        pd.DataFrame(summary).to_csv(dest / "full_synthetic_summary.csv", index=False)
    report = {"status": "complete" if not failures and all(valid(r) for r in pooled) else "complete_with_failures", "mode": "smoke" if smoke else "full", "dataset_count": len(registry), "analysis_rows": len(rows), "paper_replay_rows": sum(r["analysis_family"] == "paper_replay" for r in rows), "exploratory_proxy_rows": sum(r["analysis_family"] == "exploratory_proxy" for r in rows), "completion_rows": sum(r["kind"] == "completion" for r in rows), "completion_preservation_control_rows": sum(r["kind"] == "completion" and r["completion_role"] == "unchanged_preservation_control" for r in rows), "completion_affected_rows": sum(r["kind"] == "completion" and r["completion_role"] == "PFS_affected" for r in rows), "pooled_completion_rows": len(pooled), "pooling_failures": sum(not valid(r) for r in pooled), "analysis_failures": sum(not valid(r) for r in rows), "failures": failures, "elapsed_seconds": time.perf_counter() - started, "runtime": runtime(), "freeze_sha256": sha(ROOT / "freeze.json"), "computation_counts": df.computation.value_counts(dropna=False).to_dict() if "computation" in df else {}, "interpretation": ["Retrospective development expansion on previously evaluated data; no confirmatory evidence.", "29 unchanged completion outputs are preservation controls, not generation success.", "Only 6 affected completion outcomes are Rubin-pooled; all 20 synthetic cohorts remain separate.", "Six full-generation baseline relationships lacked supplied covariances; 25 trajectories were constrained by source marginals; four proxies are separate exploratory analyses.", "Uncertain confidence intervals do not establish a true null or statistical equivalence.", "Exact observed-data reference is available but has native missingness and sampling uncertainty.", "No inferential confidence interval is computed over correlated outcomes or masks.", "Normal-Wald mixed-model intervals do not exactly reproduce unspecified SAS denominator-df methods.", "Rubin large-complete-sample approximation does not certify proper MI or calibrated coverage.", "No generators rerun, source records changed, outcome-driven tuning, or patient rows exported."]}
    write_new(dest / "summary.json", report)
    write_new(dest / "output_manifest.json", {"freeze_sha256": sha(ROOT / "freeze.json"), "files": {p.name: sha(p) for p in dest.iterdir() if p.is_file()}})
    print(json.dumps({k: report[k] for k in ["status", "dataset_count", "analysis_rows", "pooled_completion_rows", "analysis_failures", "elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "verify", "smoke", "run"])
    args = parser.parse_args()
    if args.action == "freeze":
        freeze()
    elif args.action == "verify":
        print(json.dumps({"status": "verified", "datasets": len(verify()["registry"])}))
    else:
        execute(smoke=args.action == "smoke")

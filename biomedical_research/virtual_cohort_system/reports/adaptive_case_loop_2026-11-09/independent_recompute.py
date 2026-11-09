"""Postclosure arithmetic audit; no generator/provider/evaluator imports or refits.

Importing this module performs no file access. The explicit CLI switch runs only
after AUTHOR_CLOSED.json exists. Original clinical-reference files are never read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PRIMARY = {
    "K02-HDL-BMI": "mg/dL per 5 kg/m^2",
    "K02-TC-BMI": "mg/dL per 5 kg/m^2",
    "K02-LIPID-RESIDUAL": "1",
}
MARGINAL_UNITS = {"age": "year", "bmi": "kg/m^2",
                  "total_cholesterol": "mg/dL", "hdl_cholesterol": "mg/dL"}
DIAGNOSTICS = {
    **{f"{col}.{stat}": unit for col, unit in MARGINAL_UNITS.items()
       for stat in ("mean", "sd_sample", "q10", "q50", "q90")},
    "total_cholesterol.conditional_rms": "mg/dL",
    "hdl_cholesterol.conditional_rms": "mg/dL",
    "sex.F_fraction": "1",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_child(root, relative):
    require(isinstance(relative, str) and relative, "Missing artifact path")
    parts = relative.split("/")
    require(not any(p in {"", ".", ".."} or any(c in p for c in "\\:\x00") for p in parts),
            "Unsafe artifact path")
    path = root.joinpath(*parts)
    require(path.resolve().is_relative_to(root.resolve()), "Artifact escapes root")
    require(not any(p.is_symlink() or getattr(p, "is_junction", lambda: False)()
                    for p in (path, *path.parents)), "Linked artifact rejected")
    return path


def closure_gate(root):
    closure_path = root / "AUTHOR_CLOSED.json"
    require(closure_path.is_file(), "Author closure is required before data/report access")
    closure = read(closure_path)
    require(closure.get("status") == "author_finished_no_further_revision", "Author is not closed")
    protocol = read(root / "PROTOCOL.json")
    bundle = Path(closure["bundle"])
    require(bundle.resolve() == Path(protocol["bundle"]).resolve(), "Closure bundle differs from protocol")
    actual = set()
    for path in bundle.rglob("*"):
        require(not path.is_symlink() and not getattr(path, "is_junction", lambda: False)(),
                "Linked closed artifact")
        if path.is_file():
            actual.add(path.relative_to(bundle).as_posix())
    require(actual == set(closure["files"]), "Closed artifact inventory changed")
    for relative, expected in closure["files"].items():
        require(sha(safe_child(bundle, relative)) == expected, "Closed artifact changed: " + relative)
    return closure, protocol, bundle


def calculate(frame, expected_rows):
    """Independent linear algebra and moments in the frozen K02 coordinates."""
    columns = ["id", "age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol"]
    require(list(frame.columns) == columns and len(frame) == expected_rows, "Delivered shape differs")
    require(frame["id"].notna().all() and not frame["id"].duplicated().any(), "Invalid identifiers")
    require(frame["sex"].isin(["F", "M"]).all(), "Invalid sex token")
    numeric = frame[["age", "bmi", "total_cholesterol", "hdl_cholesterol"]].to_numpy(dtype=float)
    require(np.isfinite(numeric).all() and (numeric[:, 0] >= 18).all()
            and (numeric[:, 1:] > 0).all(), "Invalid eligibility or nonfinite data")
    age, bmi, tc, hdl = numeric.T
    tc, hdl = tc * 38.67, hdl * 38.67
    sex_f = frame["sex"].eq("F").to_numpy(dtype=float)
    x = np.column_stack((np.ones(len(frame)), (age - 50) / 10, sex_f, (bmi - 25) / 5))
    rank = int(np.linalg.matrix_rank(x))
    values = {key: None for key in PRIMARY}
    residuals = {}
    eps = np.finfo(float).eps
    for name, y, endpoint in (("total_cholesterol", tc, "K02-TC-BMI"),
                               ("hdl_cholesterol", hdl, "K02-HDL-BMI")):
        values[name + ".conditional_rms"] = None
        if rank == 4:
            coefficient = np.linalg.lstsq(x, y, rcond=None)[0]
            residual = y - x @ coefficient
            rms = float(np.sqrt(np.mean(residual ** 2)))
            values[name + ".conditional_rms"] = rms if math.isfinite(rms) else None
            # The frozen estimator treats a constant response as uncomputable.
            if np.ptp(y) != 0 and np.isfinite(coefficient).all() and np.isfinite(residual).all():
                values[endpoint] = float(coefficient[3])
                resolution = 16 * eps * max(x.shape) * max(float(np.linalg.norm(y)), np.finfo(float).tiny)
                if np.isfinite(resolution) and np.linalg.norm(residual) > resolution:
                    residuals[name] = residual
    if len(residuals) == 2:
        correlation = float(np.corrcoef(residuals["total_cholesterol"], residuals["hdl_cholesterol"])[0, 1])
        if math.isfinite(correlation) and abs(correlation) <= 1 + 256 * eps:
            values["K02-LIPID-RESIDUAL"] = float(np.clip(correlation, -1, 1))
    for name, y in (("age", age), ("bmi", bmi), ("total_cholesterol", tc), ("hdl_cholesterol", hdl)):
        values[name + ".mean"] = float(np.mean(y))
        values[name + ".sd_sample"] = float(np.std(y, ddof=1))
        for q in (0.1, 0.5, 0.9):
            values[name + ".q" + str(int(q * 100))] = float(np.quantile(y, q, method="linear"))
    values["sex.F_fraction"] = float(np.mean(sex_f))
    require(set(values) == set(PRIMARY) | set(DIAGNOSTICS), "Independent endpoint coverage differs")
    values = {key: value if value is not None and math.isfinite(value) else None
              for key, value in values.items()}
    return values, rank


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-postclosure", action="store_true")
    args = parser.parse_args()
    require(args.run_postclosure, "Explicit --run-postclosure is required")
    closure, protocol, bundle = closure_gate(ROOT)
    require({r["id"]: r["analysis_unit"] for r in protocol["required_analyses"]} == PRIMARY,
            "Primary protocol differs")
    require({r["id"]: r["unit"] for r in protocol["required_diagnostics"]} == DIAGNOSTICS,
            "Diagnostic protocol differs")
    report_path = ROOT / "EVALUATION.json"
    report = read(report_path)
    require(report["closure_sha256"] == sha(ROOT / "AUTHOR_CLOSED.json"), "Report closure binding differs")
    rows = report["runs"]
    require(len(rows) == len(closure["runs"]) and {r["run_id"] for r in rows} == set(closure["runs"]),
            "Report omitted, duplicated or added a run")
    expected_slots = {(c, seed) for c in closure["candidates"] for seed in protocol["seeds"]}
    require({(r["candidate"], r["seed"]) for r in rows} == expected_slots,
            "Scheduled candidate/seed coverage differs")
    checks, run_audits, failed_runs, unavailable = [], [], [], []
    output_hashes = {}
    for row in rows:
        run = safe_child(bundle, "executions/" + row["run_id"])
        receipt = read(run / "execution.json")
        require((row["candidate"], row["seed"], row["status"]) ==
                (receipt["candidate"], receipt["limits"]["seed"], receipt["status"]), "Execution identity differs")
        for relative, expected in receipt["files"].items():
            require(sha(safe_child(run, relative)) == expected, "Execution artifact hash changed")
        expected = {}
        for category, contract in (("analyses", PRIMARY), ("diagnostics", DIAGNOSTICS)):
            endpoint_rows = row[category]
            require(len(endpoint_rows) == len(contract)
                    and {r["id"]: r["unit"] for r in endpoint_rows} == contract,
                    "All 3 analyses and 23 diagnostics must remain explicit for every run")
            expected.update({r["id"]: r for r in endpoint_rows})
        if row["status"] != "success":
            require(all(r["value"] is None for r in expected.values()), "Failed execution has computed endpoints")
            failed_runs.append({"run_id": row["run_id"], "status": row["status"]})
            continue
        path = run / "output/generated.csv"
        digest = sha(path)
        require(digest == row["output_sha256"] == receipt["files"]["output/generated.csv"], "Output binding differs")
        output_hashes[row["run_id"]] = digest
        frame = pd.read_csv(path, dtype={"id": "string", "sex": "string"},
                            float_precision="round_trip", keep_default_na=False, na_values=[""])
        computed, rank = calculate(frame, protocol["rows_per_output"])
        run_audits.append({"run_id": row["run_id"], "candidate": row["candidate"], "seed": row["seed"],
                           "route": receipt["route"], "n_rows": len(frame), "design_rank": rank})
        for name, value in computed.items():
            reported = expected[name]
            if value is None:
                passed = reported["value"] is None and reported["status"] == "unavailable"
                difference = tolerance = None
                unavailable.append({"run_id": row["run_id"], "id": name})
            else:
                require(isinstance(reported["value"], (int, float)) and not isinstance(reported["value"], bool)
                        and math.isfinite(reported["value"]), "Nonfinite or missing reported endpoint")
                difference = abs(value - reported["value"])
                tolerance = 1e-9 * max(1.0, abs(reported["value"]))
                passed = reported["status"] == "computed" and difference <= tolerance
            checks.append({"run_id": row["run_id"], "id": name, "absolute_difference": difference,
                           "tolerance": tolerance, "passed": bool(passed)})
    closure_gate(ROOT)
    finite_differences = [r["absolute_difference"] for r in checks if r["absolute_difference"] is not None]
    result = {
        "scope": "Independent formulas on previously generated local outputs after author closure; no generation, provider imports, original reference files or patient-level refits.",
        "evaluation_sha256": sha(report_path), "closure_sha256": sha(ROOT / "AUTHOR_CLOSED.json"),
        "script_sha256": sha(Path(__file__)), "protocol_sha256": sha(ROOT / "PROTOCOL.json"),
        "checks": len(checks), "passed": sum(r["passed"] for r in checks),
        "max_absolute_difference": max(finite_differences, default=None),
        "output_sha256": output_hashes, "run_audits": run_audits, "failed_runs": failed_runs,
        "unavailable_generated_endpoints": unavailable, "comparisons": checks,
        "tolerance_role": "Floating-point arithmetic verification only; no biological equivalence or success threshold.",
    }
    with (ROOT / "RECOMPUTATION.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k: result[k] for k in ("checks", "passed", "max_absolute_difference", "failed_runs")}, indent=2))
    if result["checks"] != result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

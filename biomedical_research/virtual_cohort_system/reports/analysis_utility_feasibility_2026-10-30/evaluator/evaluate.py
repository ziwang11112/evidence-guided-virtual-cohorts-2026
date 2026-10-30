"""Controller-only CLI; every target CSV read occurs after verify_manifest passes."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

from analysis import (PRIMARY, PROJECT, points, evaluate_reference, evaluate_generated,
                      compare_points, summarize_residual_draws, validate_design)
from gates import absolute, read_json, require, sha256, verify_manifest

OUTCOMES = {"nhanes_insulin": "fasting_insulin_uU_ml", "pns_hba1c": "hba1c_pct"}


def table(path):
    return pd.read_csv(path, float_precision="round_trip")


def _ids(frame):
    require("row_id" in frame and frame.row_id.notna().all() and frame.row_id.is_unique,
            "Missing or duplicate record IDs")
    return frame.set_index("row_id")


def load_nhanes_design(config):
    """Read design columns only into analysis; never use outcome/domain to filter.

    The established XPORT reader internally decodes a source file in full. Its
    returned frame is immediately restricted to allowlisted design columns;
    no source outcome column is retained, summarized, or used for eligibility.
    GLU supplies the official fasting weight also checked against reference INS.
    """
    spec = importlib.util.spec_from_file_location("m10_preparation_reader", config["prepare_reader_path"])
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(PROJECT))
    spec.loader.exec_module(module)
    demo = module.read_xport_exact_zero(config["demo_path"])[["SEQN", "SDMVSTRA", "SDMVPSU"]].copy()
    fasting = module.read_xport_exact_zero(config["fasting_design_path"])[["SEQN", "WTSAF2YR"]].copy()
    for frame in (demo, fasting):
        require(frame.SEQN.notna().all() and frame.SEQN.is_unique, "Raw design SEQN failure")
    full = fasting.merge(demo, on="SEQN", how="left", validate="one_to_one")
    # Weight eligibility only, preserving children, excluded adults and missing-target rows.
    full = full.loc[np.isfinite(full.WTSAF2YR)&full.WTSAF2YR.gt(0)].copy()
    full = full.set_index("SEQN").rename(columns={"SDMVSTRA": "stratum", "SDMVPSU": "psu", "WTSAF2YR": "weight"})
    full = full[["stratum", "psu", "weight"]]
    validate_design(full)
    return full


def load_case(case, config):
    observed_raw = table(config["observed_path"])
    observed = points.normalize_visible(observed_raw, case)
    reference = _ids(table(config["reference_path"]))
    require(observed.index.equals(reference.index), "Reference ID order differs from frozen observed input")
    outcome = reference[OUTCOMES[case]]
    if case == "nhanes_insulin":
        full_design = load_nhanes_design(config)
        weights = reference.WTSAF2YR
        ids = reference.SEQN
        require(ids.is_unique and ids.notna().all() and ids.isin(full_design.index).all(), "Eligible/full-design mapping invalid")
        require(np.array_equal(weights.to_numpy(), reference.WTSAF2YR_GLU.to_numpy()), "Prepared INS/GLU weights disagree")
        for source, target in [("SDMVSTRA", "stratum"), ("SDMVPSU", "psu"), ("WTSAF2YR", "weight")]:
            require(np.array_equal(reference[source].to_numpy(), full_design.loc[ids, target].to_numpy()), "Prepared/reference full design mismatch")
        result = evaluate_reference(observed, outcome, weights, case, full_design, ids)
    else:
        expected = _ids(observed_raw)
        require(reference.drop(columns=[OUTCOMES[case]]).equals(expected), "PNS reserved observed cells changed")
        weights_frame = _ids(table(config["weights_path"]))
        mapping = _ids(table(config["id_mapping_path"]))
        require(observed.index.equals(weights_frame.index) and observed.index.equals(mapping.index), "PNS weight/mapping ID order mismatch")
        weights = weights_frame.peso_lab
        result = evaluate_reference(observed, outcome, weights, case)
    return observed_raw, observed, weights, result


def _failure_endpoints(reference_points, error):
    return {key: {"status": "nonestimable", "tier": item["tier"],
                  "reason": f"Entire generated analysis failed: {type(error).__name__}: {error}"}
            for key, item in reference_points.items()}


def execute_after_gate(manifest, gate):
    """Private controller service called only after the CLI's full release gate."""
    cases = {case: load_case(case, config) for case, config in manifest["cases"].items()}
    report = {"schema_version": "m10-analysis-results-1", "created_utc": datetime.now(timezone.utc).isoformat(),
              "gate": gate, "primary_family": list(PRIMARY),
              "interpretation": {"primary_question": "Same prespecified analysis of generated and reserved real outcomes",
                                 "comparisons": "Scientific-unit magnitude errors and point-direction agreement",
                                 "clinical_conclusions": "No clinical supported/absent-effect/equivalence category; no substantive margins prespecified",
                                 "residual_draws": "Monte Carlo only, not independent constructions or biological uncertainty",
                                 "construction_selection": "All four independent final constructions retained; no best-of-two"},
              "reference": {case: data[3] for case, data in cases.items()}, "constructions": []}
    primary_rows = []
    for construction in manifest["constructions"]:
        case = construction["case_id"]
        observed_raw, observed, weights, reference = cases[case]
        record = {"construction_id": construction["construction_id"], "case_id": case, "draws": []}
        for output in construction["outputs"]:
            # Recheck before parse in case external files changed after gate completion.
            require(sha256(output["path"]) == output["sha256"], "Output changed after gate")
            try:
                generated = table(output["path"])
                require(generated.drop(columns=[OUTCOMES[case]]).equals(observed_raw), "Generated observed columns/rows changed")
                values = _ids(generated)[OUTCOMES[case]]
                analyzed = evaluate_generated(observed, values, weights, case)
                status = "estimated"
                failure = None
            except (ValueError, KeyError, np.linalg.LinAlgError) as error:
                status, failure = "failed", f"{type(error).__name__}: {error}"
                analyzed = {"weighted": _failure_endpoints(reference["weighted"], error)}
                if case == "pns_hba1c":
                    analyzed["unweighted_sensitivity"] = _failure_endpoints(reference["unweighted_sensitivity"], error)
            comparison = {"weighted": compare_points(reference["weighted"], analyzed["weighted"])}
            if case == "pns_hba1c":
                comparison["unweighted_sensitivity"] = compare_points(reference["unweighted_sensitivity"], analyzed["unweighted_sensitivity"])
            draw = {"seed": output["seed"], "run_id": output["run_id"], "output_sha256": output["sha256"],
                    "status": status, "failure": failure, "analysis": analyzed, "comparison": comparison}
            record["draws"].append(draw)
            for name in PRIMARY:
                primary_rows.append({"construction_id": record["construction_id"], "case_id": case, "seed": output["seed"],
                                     "endpoint": name, **comparison["weighted"][name]})
        record["residual_summary"] = {"weighted": summarize_residual_draws([d["analysis"]["weighted"] for d in record["draws"]])}
        if case == "pns_hba1c":
            record["residual_summary"]["unweighted_sensitivity"] = summarize_residual_draws([d["analysis"]["unweighted_sensitivity"] for d in record["draws"]])
        record["distinct_output_contents"] = len({o["sha256"] for o in construction["outputs"]})
        report["constructions"].append(record)
    return report, pd.DataFrame(primary_rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    manifest, gate = verify_manifest(args.manifest)
    if args.verify_only:
        print(json.dumps(gate, indent=2))
        return 0
    require(bool(args.output), "--output is required for evaluation")
    output = absolute(args.output)
    require(not output.exists(), "Output directory already exists; do not overwrite an evaluation")
    # Gate completion is recorded before the first target parse. Failures remain visible.
    output.mkdir(parents=True)
    (output/"release_gate.json").write_text(json.dumps(gate, indent=2)+"\n", encoding="utf-8")
    try:
        # Opaque rehash avoids a reference changed after verification being interpreted.
        for binding in manifest["bindings"]:
            require(sha256(binding["path"]) == binding["sha256"], "Frozen binding changed after release gate")
        report, rows = execute_after_gate(manifest, gate)
        (output/"aggregate_report.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        rows.to_csv(output/"primary_endpoint_comparison.csv", index=False)
    except Exception as error:
        (output/"evaluation_failure.json").write_text(json.dumps({"status": "failed", "error_type": type(error).__name__, "message": str(error)}, indent=2)+"\n", encoding="utf-8")
        raise
    print(json.dumps({"status": "complete", "constructions": 4, "draws": 12, "primary_rows": len(rows), "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Freeze the 46-check descriptive paired-drift table before new generation.

Reads only the expressly permitted historical source-only aggregate portfolio.
Does not run any generator, read participant rows, or interpret the gate as a CI.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_gate(portfolio):
    rows = []
    for item in portfolio["checks"]:
        definition = item["definition"]
        sd = item["summary"]["generator_seed_draw_sd"]
        if sd is None or sd < 0:
            raise ValueError("Missing or negative historical generator-seed SD")
        outcome_dependent = "tg_mg_dl" in json.dumps(definition["operator"])
        rows.append({
            "check_id": definition["check_id"], "context_id": definition["context_id"],
            "kind": "TG-dependent" if outcome_dependent else "input-only",
            "historical_generator_seed_draw_sd": sd,
            "paired_absolute_limit": 3 * sd,
            "comparison": "exact equality" if sd == 0 else "absolute difference <= limit",
            "reported_value": definition["reported_value"],
            "operator": definition["operator"],
            "historical_context_input_sha256": definition["context_input_sha256"],
            "historical_mean": item["summary"]["mean"],
            "historical_mean_signed_discrepancy": item["summary"]["mean_signed_discrepancy"],
        })
    assert len(rows) == 46
    assert sum(r["kind"] == "input-only" for r in rows) == 12
    assert sum(r["kind"] == "TG-dependent" for r in rows) == 34
    assert len({r["check_id"] for r in rows}) == 46
    return {"schema_version": 1, "rule": "Every minus/plus same-seed difference versus zero must be within 3 times the historical M5 s1_final generator_seed_draw_sd, separately for all 46 checks and all three scheduled seeds. Zero SD requires exact numeric equality. No rounding or tolerance is added.",
            "interpretation": "Descriptive Monte Carlo-scale screen; not source admissibility, sampling uncertainty, clinical confidence, statistical equivalence, or an equivalence-test margin.",
            "source_seeds": [78101, 78102, 78103], "probe_seeds": [78201, 78202, 78203],
            "reference_label": "zero", "alternative_labels": ["minus", "plus"],
            "materiality": {"cells_male_age_bmi": [[40,23],[40,27],[60,23],[60,27]],
                            "statistic": "maximum absolute plus-minus analytic conditional mean gap over the four fixed cells",
                            "threshold_mg_dl": 5, "known_pre_run": True,
                            "interpretation": "Construction magnitude, not clinical importance or independent empirical discovery."},
            "table2": {"rule": "Report arithmetic and geometric interpretations, absolute discrepancies, and same-seed changes. No new numerical acceptance margin is inferred.",
                       "reported_kind": "reported_other; arithmetic/geometric ambiguity unresolved"},
            "checks": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--historical", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    expected = "work/structure-robustness-2026-10-28/source_feedback/s1_final_portfolio.json"
    if not a.historical.as_posix().lower().endswith(expected.lower()):
        raise ValueError("Historical read is restricted to the approved source portfolio")
    if a.out.exists():
        raise FileExistsError("Frozen gate is immutable; use an explicit reviewed amendment")
    result = make_gate(json.loads(a.historical.read_text(encoding="utf-8")))
    result["historical_source_portfolio_sha256"] = sha256(a.historical)
    result["historical_source_portfolio_path"] = a.historical.resolve().as_posix()
    result["freeze_script_sha256"] = sha256(__file__)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"gate_path": str(a.out), "sha256": sha256(a.out), "checks": 46, "input_only": 12, "TG_dependent": 34}))


if __name__ == "__main__":
    main()

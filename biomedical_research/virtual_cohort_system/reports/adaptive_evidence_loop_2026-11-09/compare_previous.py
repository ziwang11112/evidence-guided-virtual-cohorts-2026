"""Describe all five reference-bearing endpoints across two closed development runs."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / "adaptive_case_loop_2026-11-09"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    rows = []
    evaluations = []
    bindings = []
    for directory in (PREVIOUS, ROOT):
        closure = read(directory / "AUTHOR_CLOSED.json")
        if closure["status"] != "author_finished_no_further_revision":
            raise ValueError("Both authors must be closed")
        result = read(directory / "EVALUATION.json")
        closure_sha = hashlib.sha256((directory / "AUTHOR_CLOSED.json").read_bytes()).hexdigest()
        if result["closure_sha256"] != closure_sha:
            raise ValueError("Evaluation was not bound to this closure")
        bindings.append({"unit": directory.name, "closure_sha256": closure_sha,
                         "evaluation_sha256": hashlib.sha256((directory / "EVALUATION.json").read_bytes()).hexdigest()})
        chosen = [x for x in result["stages"] if x["selected_final"]]
        if len(chosen) != 1 or chosen[0]["candidate"] != closure["final_candidate"]:
            raise ValueError("Selected candidate mismatch")
        evaluations.append(chosen[0])
    old, new = evaluations
    for category in ("analyses", "diagnostics"):
        for before in old[category]:
            if before["reference_value"] is None:
                continue
            after = next(x for x in new[category] if x["id"] == before["id"])
            if after["reference_value"] != before["reference_value"]:
                raise ValueError("Reference changed")
            a, b, ref = before["mean"], after["mean"], before["reference_value"]
            rows.append({"id": before["id"], "unit": before["unit"],
                         "previous_selected": a, "current_selected": b,
                         "existing_sample_reference": ref,
                         "previous_seed_range": [before["seed_min"], before["seed_max"]],
                         "current_seed_range": [after["seed_min"], after["seed_max"]],
                         "change_in_absolute_point_difference":
                             abs(b-ref)-abs(a-ref) if a is not None and b is not None else None})
    if len(rows) != 5:
        raise ValueError("Expected all five reference-bearing endpoints")
    result = {"comparison": "Selected final data from two closed development runs",
              "previous_unit": PREVIOUS.name, "current_unit": ROOT.name,
              "previous_candidate": old["candidate"], "current_candidate": new["candidate"],
              "input_bindings": bindings,
              "endpoints": rows,
              "interpretation": "Descriptive comparison only. Different author sessions, source choices, model structures, feedback interfaces and seeds; no causal attribution to a single change. Absolute difference is a descriptive distance to a sample estimate, not a clinical utility threshold."}
    (ROOT / "PREVIOUS_COMPARISON.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

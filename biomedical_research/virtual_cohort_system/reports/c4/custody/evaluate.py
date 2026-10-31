"""C4 custodian-only fixed endpoint evaluator; never imports candidate programs.

Only run after all method selections are sealed. This reads existing final tables;
it does not generate observations. The source contract is not candidate feedback.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mean(values):
    return math.fsum(values) / len(values)


def sample_covariance(left, right):
    a, b = mean(left), mean(right)
    return math.fsum((x - a) * (y - b) for x, y in zip(left, right)) / (len(left) - 1)


def read_table(path, required_rows):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["row_id", "x", "y", "z"]:
            raise ValueError("Expected columns in exact order row_id,x,y,z")
        rows = list(reader)
    if len(rows) != required_rows:
        raise ValueError(f"Expected {required_rows} rows")
    ids = [row["row_id"] for row in rows]
    if any(not value for value in ids) or len(set(ids)) != len(ids):
        raise ValueError("Row identifiers must be nonempty and unique")
    columns = {key: [float(row[key]) for row in rows] for key in ("x", "y", "z")}
    if not all(math.isfinite(v) for values in columns.values() for v in values):
        raise ValueError("All measurements must be finite")
    return columns


def estimates(columns):
    x, y, z = (columns[key] for key in ("x", "y", "z"))
    xx, yy, zz = (sample_covariance(v, v) for v in (x, y, z))
    xy, xz, yz = (sample_covariance(a, b) for a, b in ((x, y), (x, z), (y, z)))
    determinant = xx * zz - xz * xz
    residual_x = xx - xz * xz / zz if zz > 0 else -1.0
    residual_y = yy - yz * yz / zz if zz > 0 else -1.0
    if min(xx, yy, zz, determinant, residual_x, residual_y) <= 0:
        raise ValueError("Nonpositive variance, singular predictor covariance, or degenerate residual")
    answer = {
        "adjusted_x_coefficient": (xy * zz - yz * xz) / determinant,
        "adjusted_z_coefficient": (yz * xx - xy * xz) / determinant,
        "partial_correlation_xy_given_z": (xy - xz * yz / zz) / math.sqrt(residual_x * residual_y),
    }
    if not all(math.isfinite(value) for value in answer.values()):
        raise ValueError("Nonfinite endpoint estimate")
    return answer


def sign(value):
    return "positive" if value > 0 else "negative" if value < 0 else "zero"


def error_band(error, policy):
    for band in policy["absolute_error_bands"]:
        if error <= band["upper_inclusive"]:
            return band["label"]
    return policy["above_all_bands_label"]


def evaluate(table, case_id, selection_seal):
    """Return every fixed endpoint under every compatible precommitted world."""
    contract_path = HERE / "evaluate_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if case_id not in contract["cases"]:
        raise ValueError("Unknown case ID")
    if not Path(selection_seal).is_file():
        raise ValueError("A controller selection-seal artifact must exist before reveal")
    result = {
        "schema_version": "c4-heldout-evaluation-v1",
        "case_id": case_id,
        "table_sha256": sha256(table),
        "selection_seal_sha256": sha256(selection_seal),
        "evaluation_contract_sha256": sha256(contract_path),
        "evaluator_sha256": sha256(__file__),
        "n_rows_required": contract["n_rows"],
        "direction_is_separate_from_error_utility": True,
        "all_precommitted_worlds_reported": True,
        "not_clinical_utility": True,
    }
    try:
        estimated = estimates(read_table(table, contract["n_rows"]))
        result["status"] = "ok"
        result["estimates"] = estimated
        result["worlds"] = {}
        for world_id, world in contract["cases"][case_id]["worlds"].items():
            metrics = {}
            for endpoint, truth in world["truth"].items():
                error = estimated[endpoint] - truth
                absolute_error = abs(error)
                entry = {
                    "estimate": estimated[endpoint], "truth": truth,
                    "signed_error": error, "absolute_error": absolute_error,
                    "squared_error": error * error,
                    "estimated_direction": sign(estimated[endpoint]),
                    "truth_direction": sign(truth),
                    "direction_matches": sign(estimated[endpoint]) == sign(truth),
                }
                if endpoint == contract["primary_endpoint"]:
                    policy = contract["primary_scoring"]
                    entry["engineering_fidelity_band"] = error_band(absolute_error, policy)
                    entry["numerical_utility_score"] = 1.0 / (1.0 + (absolute_error / policy["utility_scale"]) ** 2)
                metrics[endpoint] = entry
            result["worlds"][world_id] = metrics
        primary_errors = [v[contract["primary_endpoint"]]["absolute_error"] for v in result["worlds"].values()]
        result["primary_worst_world_absolute_error"] = max(primary_errors)
        result["primary_world_error_range"] = [min(primary_errors), max(primary_errors)]
    except (ValueError, KeyError, TypeError, OverflowError, ZeroDivisionError) as error:
        result["status"] = "invalid_table"
        result["error"] = str(error)
        result["estimates"] = None
        result["worlds"] = {
            world_id: {"truth": world["truth"], "absolute_error": None,
                       "squared_error": None, "numerical_utility_score": 0.0,
                       "engineering_fidelity_band": "invalid", "direction_matches": None}
            for world_id, world in contract["cases"][case_id]["worlds"].items()
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["task_a", "task_b"], required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--selection-seal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = evaluate(args.table, args.case, args.selection_seal)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status": payload["status"], "case_id": args.case, "output": str(args.output)}))


if __name__ == "__main__":
    main()

"""Cross-check reporting against independent postrun calculations; no generation."""
import csv
import datetime
import hashlib
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parent.parent
project = root.parent.parent
hashes = {}


def h(path):
    value = hashlib.sha256(path.read_bytes()).hexdigest()
    hashes[path.relative_to(project).as_posix()] = value
    return value


def read(path):
    h(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows(path):
    h(path)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def key(row):
    return row["case"], row["candidate"], row["seed"], row["world"], row["endpoint"]


def close(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12), (a, b)


main = read(root / "review/POSTRUN_AUDIT.json")
assert main["status"] == "PASS"
all_rows = rows(root / "results/all_table_endpoints.csv")
all_lookup = {key(r): r for r in all_rows}
independent = {key(r): r for r in rows(root / "review/POSTRUN_ENDPOINTS.csv")}
selected = rows(root / "results/selected_policy_endpoints.csv")
assert len(selected) == 81
policies = {"retain_initial", "minloss", "protected_gate"}
seen = set()
for row in selected:
    assert row["policy"] in policies and row["candidate"] == "c0"
    slot = (row["policy"], key(row))
    assert slot not in seen
    seen.add(slot)
    assert {k: v for k, v in row.items() if k != "policy"} == all_lookup[key(row)]
assert seen == {(p, k) for p in policies for k in independent if k[1] == "c0"}

receipt = read(root / "results/EVALUATION_RECEIPT.json")
for entry in receipt["per_table_evaluations"]:
    result = read(root / entry["path"])
    assert result["status"] == "ok"
    slot = result["slot"]
    worst = []
    for world, endpoints in result["worlds"].items():
        for name, record in endpoints.items():
            own = independent[(slot["case"], slot["candidate"], str(slot["seed"]), world, name)]
            close(result["estimates"][name], own["estimate"])
            for field in ("estimate", "truth", "signed_error", "absolute_error", "squared_error"):
                close(record[field], own[field])
            for field in ("estimated_direction", "truth_direction"):
                assert record[field] == own[field]
            assert record["direction_matches"] == (own["direction_matches"] == "True")
            if name == "adjusted_x_coefficient":
                assert record["engineering_fidelity_band"] == own["engineering_fidelity_band"]
                close(record["numerical_utility_score"], own["numerical_utility_score"])
                worst.append(float(own["absolute_error"]))
    close(result["primary_worst_world_absolute_error"], max(worst))
    close(result["primary_world_error_range"][0], min(worst))
    close(result["primary_world_error_range"][1], max(worst))

for row in rows(root / "results/aggregate_results.csv"):
    own = [r for r in independent.values() if r["candidate"] == "c0" and all(r[k] == row[k] for k in ("case", "world", "endpoint"))]
    close(row["truth"], own[0]["truth"])
    if row["endpoint"] == "adjusted_x_coefficient":
        close(row["mean_numerical_utility_score"], math.fsum(float(r["numerical_utility_score"]) for r in own) / 3)
    else:
        assert row["mean_numerical_utility_score"] == ""
    assert row["engineering_fidelity_bands"].split("|") == [r["engineering_fidelity_band"] for r in own]
    assert row["source_numeric_all_test_seeds_pass"] == row["source_protected_all_test_seeds_pass"] == "True"

tables = rows(root / "review/POSTRUN_TABLES.csv")
assert len(tables) == 54 and len({r["table_sha256"] for r in tables}) == 18
test = [r for r in tables if r["phase"] == "test"]
assert len(test) == 24 and len({r["table_sha256"] for r in test}) == 6
narrative_paths = [root / "results/RESULTS.md", project / "docs/C4_REVISION_ACCEPTANCE_RESULTS_2026-10-31.md"]
for path in narrative_paths:
    h(path)
result = {"status": "PASS", "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "selected_policy_rows_checked": 81, "per_table_json_results_checked": 24,
          "aggregate_utility_band_and_source_flags_checked": 27,
          "generation_files": 54, "unique_generation_contents": 18,
          "final_files": 24, "unique_final_contents": 6,
          "narrative_review": "Manual narrative review recorded separately in POSTRUN_REVIEW.md and bound to the hashes here",
          "input_hashes": hashes}
with (root / "review/POSTRUN_REPORTING_AUDIT.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps({k: v for k, v in result.items() if k != "input_hashes"}, indent=2))

"""Independent stdlib audit of existing C4 artifacts; never executes generators."""
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT.parent.parent
OUT = ROOT / "review"
HASHES = {}
DIFFS = {"source_estimates": 0.0, "source_losses": 0.0,
         "endpoint_covariance_vs_residual": 0.0, "custodian_endpoints": 0.0,
         "custodian_aggregates": 0.0, "analytical_truth": 0.0}


def h(path):
    path = path.resolve()
    assert path.is_relative_to(PROJECT)
    result = hashlib.sha256(path.read_bytes()).hexdigest()
    HASHES[path.relative_to(PROJECT).as_posix()] = result
    return result


def read(path):
    h(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def close(a, b, category):
    assert math.isfinite(a) and math.isfinite(b)
    difference = abs(a - b)
    DIFFS[category] = max(DIFFS[category], difference)
    assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), (category, a, b)


def when(value):
    return dt.datetime.fromisoformat(value)


def direction(value):
    return "positive" if value > 0 else "negative" if value < 0 else "zero"


def mean(values):
    return math.fsum(values) / len(values)


def dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def covariance_endpoints(s):
    # Solve the two normal equations by eliminating x, then back-substitution.
    xx, yy, zz = s[0][0], s[1][1], s[2][2]
    xy, xz, yz = s[0][1], s[0][2], s[1][2]
    residual_z_variance = zz - xz * xz / xx
    assert min(xx, yy, zz, residual_z_variance) > 0
    beta_z = (yz - xz * xy / xx) / residual_z_variance
    beta_x = (xy - xz * beta_z) / xx
    rx_var, ry_var = xx - xz * xz / zz, yy - yz * yz / zz
    assert min(rx_var, ry_var) > 0
    partial = (xy - xz * yz / zz) / math.sqrt(rx_var * ry_var)
    return {"adjusted_x_coefficient": beta_x, "adjusted_z_coefficient": beta_z,
            "partial_correlation_xy_given_z": partial}


def analyze_table(path):
    h(path)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["row_id", "x", "y", "z"]
        records = list(reader)
    assert len(records) == 4000 and len({r["row_id"] for r in records}) == 4000
    assert all(r["row_id"] for r in records)
    columns = [[float(r[name]) for r in records] for name in ("x", "y", "z")]
    assert all(math.isfinite(v) for col in columns for v in col)
    averages = [mean(col) for col in columns]
    centered = [[v - avg for v in col] for col, avg in zip(columns, averages)]
    s = [[dot(a, b) / 3999 for b in centered] for a in centered]
    stats = {"mean:" + n: averages[i] for i, n in enumerate(("x", "y", "z"))}
    stats.update({"sd:" + n: math.sqrt(s[i][i]) for i, n in enumerate(("x", "y", "z"))})
    for i, j in ((0, 1), (1, 2), (0, 2)):
        stats["correlation:" + ("x", "y", "z")[i] + "," + ("x", "y", "z")[j]] = s[i][j] / math.sqrt(s[i][i] * s[j][j])
    x, y, z = centered
    x_on_z, y_on_z, z_on_x = dot(x, z) / dot(z, z), dot(y, z) / dot(z, z), dot(z, x) / dot(x, x)
    rx = [a - x_on_z * b for a, b in zip(x, z)]
    ry = [a - y_on_z * b for a, b in zip(y, z)]
    rz = [a - z_on_x * b for a, b in zip(z, x)]
    assert min(dot(rx, rx), dot(ry, ry), dot(rz, rz)) > 0
    residual = {"adjusted_x_coefficient": dot(rx, y) / dot(rx, rx),
                "adjusted_z_coefficient": dot(rz, y) / dot(rz, rz),
                "partial_correlation_xy_given_z": dot(rx, ry) / math.sqrt(dot(rx, rx) * dot(ry, ry))}
    covariance = covariance_endpoints(s)
    for endpoint in residual:
        close(residual[endpoint], covariance[endpoint], "endpoint_covariance_vs_residual")
    return stats, residual


reveal = read(ROOT / "REVEAL_GATE.json")
assert h(ROOT / "REVEAL_GATE.json") == "bea5626274935be637964e38e4cd971152fe0c69df9e04e2f0df24fe5272e2f1"
assert reveal["decision"] == "reveal_and_evaluate" and "c4_design_critique" in reveal["allowed_agents"]
assert reveal["author_may_receive_hidden_feedback"] is False and reveal["generation_or_revision_allowed"] is False
commitment = read(ROOT / "TASK_COMMITMENT.json")
assert reveal["task_commitment_sha256"] == h(ROOT / "TASK_COMMITMENT.json")
for rel, expected in {**commitment["visible_artifacts"], **commitment["hidden_artifacts"]}.items():
    assert h(ROOT / rel) == expected
contract = read(ROOT / "custody/evaluate_contract.json")
plan = read(ROOT / "method/plan.json")
pool = read(ROOT / "method/pool.json")
selection = read(ROOT / "method/selection.json")
manifest = read(ROOT / "TEST_OUTPUT_MANIFEST.json")
assert reveal["selection_sha256"] == manifest["selection_sha256"] == h(ROOT / "method/selection.json")
assert reveal["test_outputs_manifest_sha256"] == h(ROOT / "TEST_OUTPUT_MANIFEST.json")
assert reveal["test_completed_receipt_sha256"] == h(ROOT / "test_COMPLETED.json")
assert pool["plan_sha256"] == selection["plan_sha256"] == h(ROOT / "method/plan.json")
assert selection["pool_sha256"] == h(ROOT / "method/pool.json")
for name, expected in plan["engine"].items():
    path = ROOT / "method/controller.py" if name == "controller.py" else PROJECT / "cohort_harness" / name
    assert h(path) == expected
for snapshot in ("PREEXECUTION_METADATA_AUDIT.json", "POOL_BINDINGS.json"):
    old = read(OUT / snapshot)
    for rel, expected in old["bound_public_artifacts"].items():
        assert h(ROOT / rel) == expected, rel

sources = {case: read(ROOT / "visible" / case / "source_contract.json") for case in plan["cases"]}
freeze_times = {"initial": [], "retention": []}
for case, entries in pool["cases"].items():
    bundle = ROOT / "b" / case
    for i, entry in enumerate(entries):
        candidate = bundle / "candidates" / entry["name"]
        frozen = read(candidate / "freeze.json")
        assert entry["freeze_sha256"] == h(candidate / "freeze.json")
        for rel, expected in frozen["commitments"].items():
            assert h(bundle / rel) == expected
        freeze_times["initial" if i == 0 else "retention"].append(when(frozen["created_utc"]))
        for filename in ("generator.py", "model_spec.json", "evidence.json"):
            assert h(candidate / filename) == h(bundle / "candidates/c0" / filename)
        if i:
            assert frozen["revision"]["kind"] == "retain" and frozen["revision_index"] == 1
            assert frozen["parent"]["candidate"] == "candidates/c0"
            assert frozen["parent"]["sha256"] == h(bundle / "candidates/c0/freeze.json")
            assert h(candidate / "initial_source_feedback.json") == h(ROOT / "author/feedback" / (case + ".json"))

gates = {phase: read(ROOT / (phase.upper() + "_GATE.json")) for phase in ("feedback", "election", "test")}
phase_records = {}
source_rows = []
table_records = []
test_analyses = {}
phase_times = {}
expected_ids = {case: set() for case in plan["cases"]}
for phase, seeds in plan["seeds"].items():
    release = read(ROOT / ("RELEASE_" + phase + ".json"))
    expected_release = {"approved_by": "root", "decision": "authorized", "phase": phase,
                        "plan_sha256": h(ROOT / "method/plan.json")}
    if phase != "feedback":
        expected_release["pool_sha256"] = h(ROOT / "method/pool.json")
    if phase == "test":
        expected_release["selection_sha256"] = h(ROOT / "method/selection.json")
    assert release == expected_release
    assert gates[phase]["release_sha256"] == h(ROOT / ("RELEASE_" + phase + ".json"))
    assert gates[phase]["hidden_access_allowed"] is False
    phase_records[phase] = []
    begins, ends = [], []
    for case, entries in pool["cases"].items():
        for index, entry in enumerate(entries[:1] if phase == "feedback" else entries):
            for seed in seeds:
                run_id = f"{phase[0]}_{case}_{index}_{seed}"
                expected_ids[case].add(run_id)
                run = ROOT / "b" / case / "executions" / run_id
                receipt = read(run / "execution.json")
                assert receipt["status"] == "success" and receipt["generator_executed"] is True
                assert receipt["limits"]["seed"] == seed and receipt["candidate"] == "candidates/" + entry["name"]
                assert receipt["candidate_freeze_sha256"] == entry["freeze_sha256"]
                assert receipt["process"]["returncode"] == 0 and receipt["process"]["host_timeout"] is False
                actual_files = {p.relative_to(run).as_posix() for p in run.rglob("*") if p.is_file()} - {"execution.json"}
                assert actual_files == set(receipt["files"])
                for rel, expected in receipt["files"].items():
                    assert h(run / rel) == expected
                candidate = ROOT / "b" / case / receipt["candidate"]
                for name in ("generator.py", "model_spec.json"):
                    assert h(run / "input" / name) == h(candidate / name)
                assert h(run / "input/task.json") == h(ROOT / "b" / case / "task.json")
                assert h(run / "input/worker.py") == plan["engine"]["_worker.py"]
                report = read(ROOT / "stats" / (run_id + ".json"))
                assert report["candidate"] == entry and report["phase"] == phase and report["case"] == case
                assert report["candidate_index"] == index and report["seed"] == seed and report["status"] == "success"
                assert report["execution_sha256"] == h(run / "execution.json")
                assert report["table_sha256"] == h(run / "output/generated.csv")
                assert report["source_sha256"] == plan["cases"][case]["source_sha256"]
                stats, endpoints = analyze_table(run / "output/generated.csv")
                squared = []
                protected, numeric = True, True
                assert [c["id"] for c in report["checks"]] == sources[case]["source_check_order"]
                for original, declared in zip(report["checks"], sources[case]["source_checks"]):
                    estimate = stats[declared["id"]]
                    error = (estimate - declared["target"]) / declared["tolerance"]
                    passed = abs(estimate - declared["target"]) <= declared["tolerance"]
                    close(estimate, original["estimate"], "source_estimates")
                    close(error, original["normalized_error"], "source_losses")
                    close(error * error, original["squared_error"], "source_losses")
                    assert passed == original["within_band"]
                    squared.append(error * error)
                    numeric = numeric and passed
                    if declared["kind"] == "correlation":
                        protected = protected and passed
                    source_rows.append({"phase": phase, "case": case, "candidate": entry["name"], "seed": seed,
                        "check_id": declared["id"], "estimate": estimate, "reference": declared["target"],
                        "normalized_error": error, "within_band": passed})
                loss = mean(squared)
                close(loss, report["full_source_error"], "source_losses")
                assert report["fixed_denominator"] == len(squared)
                assert report["protected_pass"] == protected and report["numeric_pass"] == numeric
                phase_records[phase].append(report)
                table_records.append({"phase": phase, "case": case, "candidate_index": index,
                    "candidate": entry["name"], "seed": seed, "source_loss": loss,
                    "numeric_pass": numeric, "protected_pass": protected, "table_sha256": report["table_sha256"]})
                if phase == "test":
                    test_analyses[(case, entry["name"], seed)] = (endpoints, report)
                begins.append(when(receipt["created_utc"]))
                ends.append(when(receipt["created_utc"]) + dt.timedelta(seconds=receipt["elapsed_seconds"]))
    completed = read(ROOT / (phase + "_COMPLETED.json"))
    assert completed["scheduled_slots"] == completed["computed_slots"] == len(phase_records[phase])
    assert completed["status_counts"] == {"success": len(phase_records[phase])}
    assert completed["aggregate_digest_sha256"] == canonical(phase_records[phase])
    assert completed["plan_sha256"] == h(ROOT / "method/plan.json")
    assert completed["release_sha256"] == h(ROOT / ("RELEASE_" + phase + ".json"))
    phase_times[phase] = {"first_start": min(begins), "last_recorded_end": max(ends)}
    assert when(gates[phase]["created_utc"]) < min(begins)

assert len(table_records) == 54 and len(source_rows) == 459
for case, expected in expected_ids.items():
    assert {p.name for p in (ROOT / "b" / case / "executions").iterdir()} == expected
assert {p.stem for p in (ROOT / "stats").glob("*.json")} == set.union(*expected_ids.values())
assert canonical(phase_records["feedback"]) == pool["feedback_sha256"]
assert canonical(phase_records["election"]) == selection["election_sha256"]
assert when(commitment["frozen_at_utc"]) < min(freeze_times["initial"])
assert max(freeze_times["initial"]) < when(gates["feedback"]["created_utc"])
assert phase_times["feedback"]["last_recorded_end"] < min(freeze_times["retention"])
assert max(freeze_times["retention"]) < when(gates["election"]["created_utc"])
assert phase_times["election"]["last_recorded_end"] < when(gates["test"]["created_utc"])
assert phase_times["test"]["last_recorded_end"] < when(manifest["created_utc"]) <= when(reveal["created_utc"])
assert gates["test"]["selection_sha256"] == h(ROOT / "method/selection.json")
assert gates["test"]["election_receipt_sha256"] == h(ROOT / "election_COMPLETED.json")

for case in plan["cases"]:
    rows = [r for r in table_records if r["phase"] == "election" and r["case"] == case]
    losses = [mean([r["source_loss"] for r in rows if r["candidate_index"] == i]) for i in range(4)]
    eligible = [all(r["protected_pass"] for r in rows if r["candidate_index"] == i) for i in range(4)]
    minimum = min(range(4), key=lambda i: (losses[i], i))
    admissible = [i for i in range(1, 4) if eligible[i] and losses[i] < losses[0]]
    protected = min(admissible, key=lambda i: (losses[i], i)) if admissible else 0
    assert minimum == protected == selection["cases"][case]["minloss"] == selection["cases"][case]["protected_gate"] == selection["cases"][case]["retain_initial"] == 0
    assert eligible == selection["cases"][case]["protected_eligible"] == [True] * 4
    for observed, recorded in zip(losses, selection["cases"][case]["mean_losses"]):
        close(observed, recorded, "source_losses")

manifest_slots = set()
for entry in manifest["entries"]:
    key = (entry["case"], entry["candidate"], entry["seed"])
    assert key not in manifest_slots
    manifest_slots.add(key)
    assert entry["table_sha256"] == h(ROOT / entry["table_path"])
    assert entry["diagnostic_sha256"] == h(ROOT / entry["diagnostic_path"])
    assert entry["selected_by"] == (["retain_initial", "minloss", "protected_gate"] if entry["candidate_index"] == 0 else [])
assert manifest_slots == set(test_analyses) and len(manifest_slots) == 24
assert len({r["table_sha256"] for r in manifest["entries"]}) == manifest["unique_table_contents"] == 6
for case in plan["cases"]:
    for phase in ("election", "test"):
        for seed in plan["seeds"][phase]:
            assert len({r["table_sha256"] for r in table_records if r["case"] == case and r["phase"] == phase and r["seed"] == seed}) == 1

truths, truth_rows = {}, []
for case, description in contract["cases"].items():
    for world, law in description["worlds"].items():
        covariance = law["covariance"]
        # Verify admitted moments in every world, not only the reported endpoint.
        for check in sources[case]["source_checks"]:
            ids = [("x", "y", "z").index(v) for v in check["columns"]]
            actual = law["means"][ids[0]] if check["kind"] == "mean" else math.sqrt(covariance[ids[0]][ids[0]]) if check["kind"] == "sd" else covariance[ids[0]][ids[1]] / math.sqrt(covariance[ids[0]][ids[0]] * covariance[ids[1]][ids[1]])
            close(actual, check["target"], "analytical_truth")
        xx, yy, zz = (covariance[i][i] for i in range(3))
        xy, xz, yz = covariance[0][1], covariance[0][2], covariance[1][2]
        assert xx > 0 and xx * yy - xy * xy > 0
        assert xx * yy * zz + 2 * xy * xz * yz - xx * yz * yz - yy * xz * xz - zz * xy * xy > 0
        truths[(case, world)] = covariance_endpoints(covariance)
        for endpoint, value in truths[(case, world)].items():
            close(value, law["truth"][endpoint], "analytical_truth")
            truth_rows.append({"case": case, "world": world, "endpoint": endpoint, "derived_truth": value})
gap = abs(truths[("task_b", "compatible_world_1")][contract["primary_endpoint"]] - truths[("task_b", "compatible_world_2")][contract["primary_endpoint"]])
close(gap, contract["task_b_identification_separation"]["primary_truth_absolute_difference"], "analytical_truth")
close(gap / 2, contract["task_b_identification_separation"]["any_single_estimate_minimum_possible_worst_world_absolute_error"], "analytical_truth")

endpoint_rows = []
for (case, candidate, seed), (estimates, report) in test_analyses.items():
    for world in contract["cases"][case]["worlds"]:
        for endpoint, estimate in estimates.items():
            truth = truths[(case, world)][endpoint]
            error = estimate - truth
            primary = endpoint == contract["primary_endpoint"]
            band = "not_prespecified_for_secondary"
            utility = None
            if primary:
                band = next((b["label"] for b in contract["primary_scoring"]["absolute_error_bands"] if abs(error) <= b["upper_inclusive"]), contract["primary_scoring"]["above_all_bands_label"])
                utility = 1 / (1 + (abs(error) / contract["primary_scoring"]["utility_scale"]) ** 2)
            endpoint_rows.append({"case": case, "candidate": candidate, "seed": seed, "world": world,
                "endpoint": endpoint, "estimate": estimate, "truth": truth, "signed_error": error,
                "absolute_error": abs(error), "squared_error": error * error,
                "estimated_direction": direction(estimate), "truth_direction": direction(truth),
                "direction_matches": direction(estimate) == direction(truth), "engineering_fidelity_band": band,
                "numerical_utility_score": utility, "table_sha256": report["table_sha256"]})
assert len(endpoint_rows) == 108

# Only after completing the independent arithmetic, compare the custodian's outputs.
receipt = read(ROOT / "results/EVALUATION_RECEIPT.json")
assert receipt["additional_generation_runs"] == receipt["candidate_code_imports"] == 0
assert when(receipt["completed_utc"]) > when(reveal["created_utc"])
assert receipt["evaluation_contract_sha256"] == h(ROOT / "custody/evaluate_contract.json")
assert receipt["evaluator_sha256"] == h(ROOT / "custody/evaluate.py")
assert receipt["adapter_sha256"] == h(ROOT / "results/evaluate_committed_tables.py")
for rel, expected in receipt["aggregate_artifacts"].items():
    assert h(ROOT / "results" / rel) == expected
for item in receipt["per_table_evaluations"]:
    assert h(ROOT / item["path"]) == item["sha256"]
    evaluated = read(ROOT / item["path"])
    assert evaluated["table_sha256"] == item["table_sha256"]
    assert evaluated["selection_seal_sha256"] == h(ROOT / "method/selection.json")

def csv_rows(path):
    h(path)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def key(row):
    return row["case"], row["candidate"], int(row["seed"]), row["world"], row["endpoint"]


independent = {key(r): r for r in endpoint_rows}
custodian = csv_rows(ROOT / "results/all_table_endpoints.csv")
assert len(custodian) == len(independent) == 108
for row in custodian:
    own = independent[key(row)]
    for field in ("estimate", "truth", "signed_error", "absolute_error", "squared_error"):
        close(float(row[field]), own[field], "custodian_endpoints")
    for field in ("estimated_direction", "truth_direction", "engineering_fidelity_band", "table_sha256"):
        assert row[field] == own[field]
    assert (row["direction_matches"] == "True") == own["direction_matches"]
    if own["numerical_utility_score"] is not None:
        close(float(row["numerical_utility_score"]), own["numerical_utility_score"], "custodian_endpoints")

aggregate = csv_rows(ROOT / "results/aggregate_results.csv")
assert len(aggregate) == 27
for row in aggregate:
    own = [r for r in endpoint_rows if r["candidate"] == "c0" and all(r[k] == row[k] for k in ("case", "world", "endpoint"))]
    assert len(own) == int(row["distinct_seed_tables"]) == 3 and row["selected_candidate"] == "c0"
    for field, values in {"mean_estimate": [r["estimate"] for r in own],
        "mean_signed_error": [r["signed_error"] for r in own],
        "mean_absolute_error": [r["absolute_error"] for r in own],
        "mean_squared_error": [r["squared_error"] for r in own]}.items():
        close(float(row[field]), mean(values), "custodian_aggregates")
    close(float(row["minimum_estimate"]), min(r["estimate"] for r in own), "custodian_aggregates")
    close(float(row["maximum_estimate"]), max(r["estimate"] for r in own), "custodian_aggregates")
    close(float(row["maximum_absolute_error"]), max(r["absolute_error"] for r in own), "custodian_aggregates")
    assert int(row["direction_matches_count"]) == sum(r["direction_matches"] for r in own)

primary_summary = []
for case, world in truths:
    own = [r for r in endpoint_rows if r["case"] == case and r["world"] == world and r["candidate"] == "c0" and r["endpoint"] == contract["primary_endpoint"]]
    primary_summary.append({"case": case, "world": world, "truth": own[0]["truth"],
        "estimates": [r["estimate"] for r in own], "mean_absolute_error": mean([r["absolute_error"] for r in own]),
        "absolute_error_range": [min(r["absolute_error"] for r in own), max(r["absolute_error"] for r in own)],
        "direction_matches": sum(r["direction_matches"] for r in own),
        "bands": [r["engineering_fidelity_band"] for r in own]})

summary = {"status": "PASS", "scope": "independent existing-artifact numerical and commitment audit",
    "completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "generator_imports_or_executions": 0,
    "scientific_runs": 54, "source_statistic_comparisons": 459, "all_source_checks_pass": all(r["within_band"] for r in source_rows),
    "test_files": 24, "unique_test_contents": 6, "analytical_reference_values_checked": 9,
    "test_endpoint_world_comparisons": 108, "custodian_aggregate_rows_checked": 27,
    "all_policies_select_c0_both_tasks": True, "distinct_models_per_task": 1,
    "maximum_absolute_numerical_differences": DIFFS, "primary_endpoint_summary": primary_summary,
    "task_b_primary_truth_gap": gap, "task_b_minimum_possible_worst_world_absolute_error": gap / 2,
    "phase_times": {p: {k: v.isoformat() for k, v in values.items()} for p, values in phase_times.items()},
    "chronology_check": "recorded commitment, freeze, phase, selection-bound test release, manifest, reveal and evaluation chronology consistent",
    "chronology_limit": "hashes and recorded timestamps establish workflow consistency, not independent proof of every filesystem read or an adversarial security boundary",
    "primary_conclusion": "nondiscriminating identical-model pool; no incremental selector benefit established",
    "input_hash_count": len(HASHES)}


def write_json(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def write_csv(name, rows):
    with (OUT / name).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


write_csv("POSTRUN_SOURCE_CHECKS.csv", source_rows)
write_csv("POSTRUN_ENDPOINTS.csv", endpoint_rows)
write_csv("POSTRUN_TRUTH_CHECKS.csv", truth_rows)
write_csv("POSTRUN_TABLES.csv", table_records)
write_json("POSTRUN_INPUT_HASHES.json", HASHES)
write_json("POSTRUN_AUDIT.json", summary)
print(json.dumps(summary, indent=2))

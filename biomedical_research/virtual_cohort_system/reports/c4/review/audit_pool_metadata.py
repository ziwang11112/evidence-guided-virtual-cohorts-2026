"""Independent pool/feedback metadata audit; no candidate imports or custody access."""
import datetime
import hashlib
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parent.parent
hashes = {}


def hashfile(path):
    path = path.resolve()
    assert path.is_relative_to(root) and not path.is_relative_to(root / "custody")
    result = hashlib.sha256(path.read_bytes()).hexdigest()
    hashes[path.relative_to(root).as_posix()] = result
    return result


def read(path):
    hashfile(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


pool = read(root / "method/pool.json")
plan = read(root / "method/plan.json")
assert pool["plan_sha256"] == hashfile(root / "method/plan.json")
assert pool["labeled_candidates"] == 8 and pool["distinct_generator_spec_pairs"] == 2
reports = []
summary = {}
for case in ("task_a", "task_b"):
    bundle = root / "b" / case
    base = bundle / "candidates/c0"
    source = read(root / "visible" / case / "source_contract.json")
    packet_path = root / "author/feedback" / (case + ".json")
    packet = read(packet_path)
    assert packet["task"] == case and packet["phase"] == "initial_source_feedback_only"
    assert len(packet["reports"]) == 3
    assert [r["seed"] for r in packet["reports"]] == plan["seeds"]["feedback"]
    for report in packet["reports"]:
        report_name = report["run_id"] + ".json"
        report_path = root / "stats" / report_name
        assert read(report_path) == report
        assert packet["report_hashes"][report_name] == hashfile(report_path)
        assert report["phase"] == "feedback" and report["case"] == case
        assert report["candidate"] == plan["cases"][case]["initial"]
        assert report["source_sha256"] == hashfile(root / "visible" / case / "source_contract.json")
        run = bundle / "executions" / report["run_id"]
        receipt = read(run / "execution.json")
        assert report["execution_sha256"] == hashfile(run / "execution.json")
        assert report["table_sha256"] == hashfile(run / "output/generated.csv")
        assert receipt["status"] == report["status"] == "success"
        assert receipt["limits"]["seed"] == report["seed"]
        assert receipt["candidate_freeze_sha256"] == hashfile(base / "freeze.json")
        assert [c["id"] for c in report["checks"]] == source["source_check_order"]
        for checked, expected in zip(report["checks"], source["source_checks"]):
            error = (checked["estimate"] - expected["target"]) / expected["tolerance"]
            assert math.isclose(checked["normalized_error"], error, rel_tol=1e-14, abs_tol=1e-15)
            assert math.isclose(checked["squared_error"], error * error, rel_tol=1e-14, abs_tol=1e-15)
            assert checked["within_band"] is (abs(checked["estimate"] - expected["target"]) <= expected["tolerance"])
        assert report["numeric_pass"] is True and report["protected_pass"] is True
        assert report["fixed_denominator"] == len(source["source_checks"])
        assert math.isclose(report["full_source_error"], sum(c["squared_error"] for c in report["checks"]) / len(source["source_checks"]), rel_tol=1e-14, abs_tol=1e-15)
        reports.append(report)
    assert [e["name"] for e in pool["cases"][case]] == ["c0", "c1", "c2", "c3"]
    for entry in pool["cases"][case]:
        candidate = bundle / "candidates" / entry["name"]
        freeze = read(candidate / "freeze.json")
        assert entry["freeze_sha256"] == hashfile(candidate / "freeze.json")
        assert entry["generator_sha256"] == hashfile(candidate / "generator.py")
        assert entry["spec_sha256"] == hashfile(candidate / "model_spec.json")
        for rel, expected in freeze["commitments"].items():
            assert hashfile(bundle / rel) == expected, (case, entry["name"], rel)
        for name in ("generator.py", "model_spec.json", "evidence.json"):
            assert hashfile(candidate / name) == hashfile(base / name)
        if entry["name"] != "c0":
            assert freeze["parent"] == {"candidate": "candidates/c0", "receipt_path": "candidates/c0/freeze.json", "sha256": hashfile(base / "freeze.json")}
            assert freeze["revision_index"] == 1 and freeze["revision"]["kind"] == "retain"
            assert hashfile(candidate / "initial_source_feedback.json") == hashfile(packet_path)
            binding = read(candidate / "feedback_binding.json")
            assert binding["packet_sha256"] == hashfile(packet_path)
            assert binding["controller_report_hashes_verbatim"] == packet["report_hashes"]
            assert read(candidate / "revision.json") == freeze["revision"]
    assert {p.name for p in (bundle / "executions").iterdir()} == {r["run_id"] for r in packet["reports"]}
    summary[case] = {"labels": 4, "distinct_generator_spec_evidence_triples": 1,
                     "retained_proposals": 3, "source_checks_passed": sum(len(r["checks"]) for r in packet["reports"])}

aggregate = hashlib.sha256(json.dumps(reports, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
assert aggregate == pool["feedback_sha256"]
result = {"status": "PASS", "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "scope": "public pool lineage and feedback metadata; no candidate import/execution or custody access",
          "pool_sha256": hashfile(root / "method/pool.json"), "cases": summary,
          "source_feedback_runs": 6, "election_or_test_runs": 0,
          "primary_interpretation": "nondiscriminating identical-model pool; cannot establish incremental selector benefit",
          "bound_public_artifacts": hashes}
output = root / "review/POOL_BINDINGS.json"
with output.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps({"status": "PASS", "pool_sha256": result["pool_sha256"], "cases": summary,
                  "public_artifacts": len(hashes)}))

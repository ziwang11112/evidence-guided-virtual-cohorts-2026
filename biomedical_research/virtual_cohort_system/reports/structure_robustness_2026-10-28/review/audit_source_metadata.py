"""Audit aggregate source feedback and receipt metadata; never opens CSV rows."""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import statistics


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "agent_bundle"


def read(path):
    if Path(path).suffix.lower() != ".json":
        raise ValueError("This audit reads JSON metadata only")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    if Path(path).suffix.lower() != ".json":
        raise ValueError("This audit hashes JSON metadata only")
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def close(left, right):
    assert math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)


def input_only(definition):
    operator = definition["operator"]
    return (operator["kind"] in {"mean", "sd"} and operator.get("column") in {"age", "bmi"}
            and not any(row["column"] == "tg_mg_dl" for row in operator["selection"]))


def main():
    protocol = read(ROOT / "protocol.json")
    anchor = read(ROOT / "protocol_commitment.json")
    plan = read(ROOT / "structure_plan_commitment.json")
    assert plan["plan_sha256"] == sha(BUNDLE / "STRUCTURE_PLAN.json")
    assert plan["protocol_sha256"] == sha(ROOT / "protocol.json")
    schedules = protocol["source_seeds"]
    assert schedules == [76101, 76102, 76103]
    freeze_times = {stage: [] for stage in ["initial", "final"]}
    execution_times = {stage: [] for stage in ["initial", "final"]}
    replay_times = {stage: [] for stage in ["initial", "final"]}
    portfolios = {}
    reports = {}
    source_receipts = []
    diagnostics = []
    for structure in protocol["structures"]:
        for stage in ["initial", "final"]:
            name = f"{structure}_{stage}"
            candidate = BUNDLE / "candidates" / name
            frozen = read(candidate / "freeze.json")
            freeze_times[stage].append(timestamp(frozen["created_utc"]))
            if stage == "initial":
                assert plan["candidate_freezes"][structure] == sha(candidate / "freeze.json")
            portfolio = read(ROOT / "source_feedback" / f"{name}_portfolio.json")
            portfolios[(structure, stage)] = portfolio
            assert len(portfolio["checks"]) == 46
            assert [r["seed"] for r in portfolio["schedule"]] == schedules
            assert sum(input_only(c["definition"]) for c in portfolio["checks"]) == 12
            for check in portfolio["checks"]:
                values = [r["value"] for r in check["runs"]]
                assert [r["seed"] for r in check["runs"]] == schedules
                assert all(r["status"] == "approximate" for r in check["runs"])
                s = check["summary"]
                close(s["mean"], statistics.mean(values))
                close(s["minimum"], min(values)); close(s["maximum"], max(values))
                close(s["generator_seed_draw_sd"], statistics.stdev(values))
                for run in check["runs"]:
                    close(run["difference"], run["value"] - check["definition"]["reported_value"])
                diagnostics.append({"structure": structure, "stage": stage,
                                    "input_only": input_only(check["definition"]), **check})
            for schedule in portfolio["schedule"]:
                replay_id = schedule["replay_id"]
                path = BUNDLE / "source_replays" / replay_id / "replay.json"
                assert sha(path) == schedule["sha256"]
                report = read(path)
                reports[(structure, stage, schedule["seed"])] = report
                assert report["status"] == "success"
                assert report["limits"]["seed"] == schedule["seed"]
                assert report["parent"]["candidate"] == f"candidates/{name}"
                assert report["parent"]["freeze.json_sha256"] == sha(candidate / "freeze.json")
                replay_times[stage].append(timestamp(report["created_utc"]))
                assert len(report["contexts"]) == 2
                for context in report["contexts"]:
                    assert context["generation_link_verified"] is True
                    receipt_path = path.parent / context["child_bundle"] / "executions/replay/execution.json"
                    assert sha(receipt_path) == context["execution_sha256"]
                    receipt = read(receipt_path)
                    assert receipt["status"] == "success" and receipt["generator_executed"] is True
                    assert receipt["limits"]["seed"] == schedule["seed"]
                    assert receipt["files"]["output/generated.csv"] == context["generated_sha256"]
                    assert all(c["generation_link_verified"] is True and
                               c["generated_sha256"] == context["generated_sha256"] for c in context["checks"])
                    execution_times[stage].append(timestamp(receipt["created_utc"]))
                    source_receipts.append({"replay_id": replay_id, "context": context["id"],
                                            "execution_sha256": sha(receipt_path),
                                            "generated_sha256_from_receipt": context["generated_sha256"]})
        pair = read(ROOT / "source_feedback" / f"{structure}_paired.json")
        assert pair["initial"] == portfolios[(structure, "initial")]
        assert pair["revised"] == portfolios[(structure, "final")]
        for comparison in pair["comparisons"]:
            key = comparison["definition"]["check_id"]
            left = next(c for c in pair["initial"]["checks"] if c["definition"]["check_id"] == key)
            right = next(c for c in pair["revised"]["checks"] if c["definition"]["check_id"] == key)
            changes = [abs(y["difference"]) - abs(x["difference"]) for x, y in zip(left["runs"], right["runs"])]
            assert comparison["paired_changes"] == [{"seed": seed, "change_in_absolute_discrepancy": v}
                                                     for seed, v in zip(schedules, changes)]
            close(comparison["paired_summary"]["mean_change_in_absolute_discrepancy"], statistics.mean(changes))

    assert timestamp(anchor["created_utc"]) <= min(freeze_times["initial"])
    assert max(freeze_times["initial"]) <= timestamp(plan["created_utc"]) <= min(execution_times["initial"])
    assert max(replay_times["initial"]) <= min(freeze_times["final"])
    assert max(freeze_times["final"]) <= min(execution_times["final"])
    retained_hash_matches = 0
    for structure in ["s2", "s3"]:
        assert portfolios[(structure, "initial")]["checks"] == portfolios[(structure, "final")]["checks"]
        for seed in schedules:
            first = reports[(structure, "initial", seed)]
            final = reports[(structure, "final", seed)]
            for a, b in zip(first["contexts"], final["contexts"]):
                assert a["id"] == b["id"] and a["generated_sha256"] == b["generated_sha256"]
                assert a["checks"] == b["checks"]
                retained_hash_matches += 1

    audit = {"status": "passed", "scope": "source_aggregate_and_receipt_metadata_only",
             "source_replays": len(reports), "source_context_executions": len(source_receipts),
             "checks_per_candidate": 46, "input_only_per_candidate": 12, "TG_dependent_per_candidate": 34,
             "retained_output_hash_matches": retained_hash_matches,
             "retained_per_seed_diagnostic_matches": 2 * 3 * 46,
             "structure_plan_commitment_sha256": sha(ROOT / "structure_plan_commitment.json"),
             "source_phase_first_execution_utc": min(execution_times["initial"]).isoformat(),
             "initial_source_last_report_utc": max(replay_times["initial"]).isoformat(),
             "final_source_first_execution_utc": min(execution_times["final"]).isoformat(),
             "final_source_last_report_utc": max(replay_times["final"]).isoformat(),
             "row_tables_read": False, "generators_executed": False, "target_results_read": False,
             "limitation": "Checks compare aggregate reports and receipt hashes; operators were not recomputed from row tables by this independent audit.",
             "source_receipts": source_receipts, "diagnostics": diagnostics}
    (ROOT / "review/source_diagnostic_review.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    lines = ["# Complete source diagnostic audit", "",
             "All values are source replay summaries. Ranges are min–max across three fixed generator seeds, not confidence intervals.",
             "Initial/final values are identical for s2 and s3. Input-only checks test fixed covariate construction, not TG generation.", ""]
    for is_input, title in [(False, "34 TG-dependent diagnostics"), (True, "12 fixed-input diagnostics")]:
        lines.extend(["## " + title, "", "| Diagnostic (original units) | Reported | S1 initial | S1 final | S2 retained | S3 retained |",
                      "|---|---:|---:|---:|---:|---:|"])
        for check in portfolios[("s1", "initial")]["checks"]:
            if input_only(check["definition"]) != is_input:
                continue
            definition = check["definition"]; key = definition["check_id"]
            cells = []
            for identity in [("s1", "initial"), ("s1", "final"), ("s2", "final"), ("s3", "final")]:
                summary = next(c for c in portfolios[identity]["checks"] if c["definition"]["check_id"] == key)["summary"]
                cells.append(f"{summary['mean']:.6g} [{summary['minimum']:.6g}, {summary['maximum']:.6g}]")
            lines.append("| " + key + " (" + definition["operator"]["unit"] + ") | " +
                         f"{definition['reported_value']:.6g}" + " | " + " | ".join(cells) + " |")
        lines.append("")
    (ROOT / "review/COMPLETE_SOURCE_DIAGNOSTICS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: v for k, v in audit.items() if k not in {"source_receipts", "diagnostics"}}, indent=2))


if __name__ == "__main__":
    main()

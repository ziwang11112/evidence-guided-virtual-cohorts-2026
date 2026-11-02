"""One finite real-OS software fixture; no clinical release or source fit.

Only package admission is substituted with the builder's existing invented
fixture. Execution, runtime inspection, bwrap, ledger, guards and collectors
are real. The release's other-case commitments/evaluator are inert test data.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
SCALE = HERE.parents[1]
PROJECT = SCALE.parents[1]
INTEGRATION = SCALE / "production_integration"
for path in (PROJECT, INTEGRATION, INTEGRATION / "k01_sources", INTEGRATION / "campaign_control"):
    sys.path.insert(0, str(path))
import campaign_control as control
import test_combined_integration as fixture
import bundle_assembly as assembly
import case_execution as runner
import k01_sources as source

ROOT = Path("D:/Codex/home/tmp/vc_live_guarded_20261102_v1")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open("xb") as handle:
        handle.write(source.encoded(value))


def review(value):
    return {"decision": "approved", "independent": True,
            "reviewer_id": "/root/context_bridge_review", "producer_id": "/root/context_bridge_build",
            "reviewed_utc": datetime.now(timezone.utc).isoformat(), "approved_sha256": value,
            "reason": "Independent review of builder-authored invented fixture/generator only; root-authorized finite software smoke, never clinical approval"}


def prepare(inputs):
    state, compiled, package, authoring, spec = inputs
    ROOT.mkdir(parents=True, exist_ok=False)
    bundle = ROOT / "bundle"
    assembly.prepare_bundle("K01", "A01", bundle, {
        "curator_id": "/root/context_bridge_review", "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "reason": "Invented software inputs only; no clinical construction", "package_sha256": assembly.package_digest(package)})
    candidate = bundle / "candidates/invented"
    candidate.mkdir(parents=True)
    plan = assembly.build_bridge_plan(package, "A01", "initial", spec, authoring)
    declaration = source.build_declaration(compiled, {c: authoring["context_assumption_ids"][c] for c in source.SOURCE_CONTEXTS}, model_spec=spec)
    declaration["review"] = review(source.declaration_digest(declaration))
    for name, value in {"model_spec.json": spec, "evidence.json": compiled["evidence"],
                        "context_authoring.json": authoring, source.bridge.PLAN: plan,
                        source.DECLARATION: declaration,
                        "checks.json": {"scope": "fixture_only", "records": [{"name": "invented",
                            "status": "not_computable", "detail": "No generation before this smoke"}], "artifacts": []}}.items():
        write(candidate / name, value)
    (candidate / "generator.py").write_bytes((HERE / "generator_fixture.py").read_bytes())
    (candidate / "decision.md").write_text("Invented finite real-runtime software fixture, no clinical model.\n", encoding="utf-8")
    source.lifecycle.freeze_candidate(bundle, candidate)
    source.bridge.prepare(bundle, "invented")
    write(ROOT / "binding_requests.json", source.bridge.binding_requests(bundle, "invented"))
    write(ROOT / "PLAN.json", {"kind": "invented_guarded_runtime_smoke", "producer": "/root/context_bridge_build",
          "reviewer": "/root/context_bridge_review", "trials": plan["trials"], "limits": plan["execution_limits"],
          "generator_sha256": sha(candidate / "generator.py"), "script_sha256": sha(__file__),
          "freeze_sha256": sha(candidate / "freeze.json"), "binding_requests_sha256": sha(ROOT / "binding_requests.json"),
          "actual_source_fit_calls": 0, "clinical_rows": 0, "planned_invented_rows": 25000,
          "attempts": 5, "retry_permitted": False, "execution_started": False})
    print(json.dumps({"prepared": str(ROOT), "plan_sha256": sha(ROOT / "PLAN.json"), "generator_sha256": sha(candidate / "generator.py")}, indent=2))


def execute():
    bundle = ROOT / "bundle"
    plan_record = source.lifecycle.read_json(ROOT / "PLAN.json")
    if sha(__file__) != plan_record["script_sha256"]:
        raise ValueError("Smoke script changed after preparation")
    requests = source.bridge.binding_requests(bundle, "invented")
    supplied = source.lifecycle.read_json(ROOT / "context_reviews.json")
    source.bridge.seal(bundle, "invented", supplied)
    evaluator = ROOT / "invented_evaluator.py"
    evaluator.write_text("# Inert software-fixture identity; never called or imported.\n", encoding="utf-8")
    paths = sorted(control._required_runtime_paths(), key=str) + [evaluator.resolve()]
    artifacts = [{"path": str(p), "sha256": sha(p)} for p in paths]
    cases = {}
    for case in control.CASES:
        cases[case] = {}
        for field in control.CASE_BINDINGS:
            path = ROOT / (case + "_" + field + ".json")
            write(path, {"invented_software_commitment_only": case + field})
            cases[case][field] = sha(path)
            artifacts.append({"path": str(path.resolve()), "sha256": sha(path)})
    manifest = {"schema_version": 1, "kind": "wave_a_global_clinical_release",
        "campaign_id": "INVENTED_REAL_OS_SOFTWARE_SMOKE_NOT_CLINICAL", "status": "released",
        "released_utc": "2026-11-02T00:00:00Z", "ledger_directory": str((ROOT / "ledger").resolve()),
        "designated_evaluator": {"path": str(evaluator.resolve()), "sha256": sha(evaluator)},
        "schedule_sha256": control.digest(control.fixed_schedule()), "cases": cases, "artifacts": artifacts, "review": {}}
    # This is deliberately marked invented test scaffolding, not an attestation
    # that these dummy case commitments received a clinical release review.
    manifest["review"] = fixture.review(control.release_digest(manifest))
    ledger = control.CampaignLedger.create(ROOT / "ledger", manifest)
    ledger.begin_construction("K01", "A01", "invented-real-os-software-smoke")
    ledger.bind_stage("K01", "A01", "initial", bundle, "invented", derivation_mode="inline_deterministic")
    ledger.begin_bridge("K01", "A01", "initial")
    guarded = runner.execute_case_stage(bundle, "invented", ledger.directory, "K01", "A01", "initial")
    reports = []
    for trial in guarded["trials"]:
        if trial["role"] == "source" and trial["trial_status"] == "success" and trial["guard_status"] == "valid":
            reports.append(source.collect_descriptives(bundle, "invented", trial["trial_id"]))
    finished = ledger.finish_bridge("K01", "A01", "initial")
    packet = ledger.deliver_source_feedback("K01", "A01")
    decision = "retain" if finished["payload"]["status"] == "success" else "stop"
    ledger.decide_final("K01", "A01", decision, "Finite invented smoke: retain valid stage or stop, never retry")
    ledger.close_constructor("K01", "A01", "Software smoke closed; no clinical release")
    summary = {"kind": "actual_wsl_bwrap_invented_guarded_runtime_smoke", "plan_sha256": sha(ROOT / "PLAN.json"),
        "status": finished["payload"]["status"], "guards": guarded, "ledger_snapshot": ledger.snapshot(),
        "source_reports": len(reports), "source_descriptive_items": sum(len(r["checks"]) for r in reports),
        "source_packet_sha256": packet["packet_sha256"], "source_only_feedback": packet["source_only"],
        "actual_source_parameter_fits": 0, "clinical_rows_generated": 0, "measured_target_reads": 0,
        "retry_count": 0, "global_clinical_release": False}
    write(ROOT / "RESULT.json", summary)
    print(json.dumps({"status": summary["status"], "source_reports": len(reports), "source_descriptive_items": summary["source_descriptive_items"],
                      "result_sha256": sha(ROOT / "RESULT.json"), "actual_process_boundary": True}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"prepare", "execute"}:
        raise ValueError("Choose prepare or execute exactly once")
    with pytest.MonkeyPatch.context() as patch:
        invented_inputs = fixture.inputs.__wrapped__(patch)
        if sys.argv[1] == "prepare":
            prepare(invented_inputs)
        else:
            execute()

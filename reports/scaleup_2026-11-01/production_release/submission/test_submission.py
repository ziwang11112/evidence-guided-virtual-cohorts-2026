"""New submission tests: invented metadata; no generator import or execution."""
import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import submission as s
sys.path.insert(0, str(s.INTEGRATION / "k01_sources"))
from test_k01_sources import invented_state


def review(value, *, producer="invented-actor"):
    return {"decision": "approved", "independent": True, "reviewer_id": "invented-independent-reviewer", "producer_id": producer,
            "reviewed_utc": "2026-11-02T00:00:00Z", "reason": "Invented fixture approval only", "approved_sha256": value}


@pytest.fixture
def setup(tmp_path, monkeypatch):
    state = invented_state()
    compiled = s.k01_sources._compile(state)
    package = {"case_id": "K01", "design_sha256": state["design_sha256"], "request_files": {"task_template.json": s.encoded(state["task"])},
               "source_files": {s.k01_sources.ARTIFACT: state["packet_bytes"]}, "evidence": compiled["evidence"], "templates": compiled["source_context_templates"],
               "registrations": compiled["registration_requirements"], "task": state["task"], "target_id": s.k01_sources.TARGET,
               "target_descriptor": {"population": state["task"]["population"], "n_rows": 5000, "measurement": "Invented target protocol"}, "target_metadata": {"invented": True}}
    monkeypatch.setattr(s.assembly, "load_package", lambda case: copy.deepcopy(package))
    monkeypatch.setattr(s.k01_sources, "compile_committed", lambda: copy.deepcopy(compiled))
    bundle = tmp_path / "b"
    s.assembly.prepare_bundle("K01", "A01", bundle, {"curator_id": "invented", "reviewed_utc": "2026-11-02", "reason": "Invented admission", "package_sha256": s.assembly.package_digest(package)})
    receipt = s.assembly.verify_bundle_inputs(bundle)
    monkeypatch.setattr(s, "_input", lambda path: (bundle, receipt, copy.deepcopy(package)))
    ledger = SimpleNamespace(release_sha256="a" * 64, bind_stage=lambda *a, **kw: {"invented": True})
    record = {"construction": {"construction_id": "invented-actor"}, "decision": None, "feedback": None, "stages": {}}
    monkeypatch.setattr(s, "_authorization", lambda *a: (ledger, record))
    contexts = {c["id"]: {"population": c["recipe"]["population"], "n_rows": 5000, "measurement": c["recipe"]["measurement"]["description"], "inputs": {}} for c in package["templates"]}
    contexts[package["target_id"]] = {**package["target_descriptor"], "inputs": {}}
    spec = {"parameters": {"active_context": package["target_id"], "contexts": contexts}, "assumptions": [{"id": "invented", "description": "Invented scientific context"}],
            "parameter_provenance": {n: {"evidence_ids": [], "assumption_ids": ["invented"], "derivation": "Invented fixture"} for n in ("active_context", "contexts")}}
    authoring = {"context_assumption_ids": {c: ["invented"] for c in contexts}, "context_varying_parameters": [], "descriptive_proxies": {}}
    authored = tmp_path / "authored"
    authored.mkdir()
    (authored / "generator.py").write_text('raise RuntimeError("Must never be host imported")\ndef generate(observed, specification, seed):\n    raise RuntimeError("Must never run")\n', encoding="utf-8")
    for name, value in {"model_spec.json": spec, "context_authoring.json": authoring, "checks.json": {"scope": "source_only", "records": [{"name": "not_executed", "status": "not_computable", "detail": "No generator imported or run"}], "artifacts": []}}.items():
        (authored / name).write_bytes(s.encoded(value))
    (authored / "decision.md").write_text("Invented open scientific choice; no fit", encoding="utf-8")
    return bundle, authored, package, record


def test_exact_authored_files_packaged_without_import_or_fabricated_approval(setup):
    bundle, authored, package, _ = setup
    request = s.prepare_submission(bundle, authored, "invented-actor", "initial", "invented-ledger")
    candidate = bundle / "candidates/initial"
    assert (candidate / "generator.py").read_bytes() == (authored / "generator.py").read_bytes()
    assert (candidate / "evidence.json").read_bytes() == s.encoded(package["evidence"])
    assert s._read(candidate / s.k01_sources.DECLARATION)["review"] is None
    assert not (candidate / "freeze.json").exists()
    assert request["binding"]["generator_imported_or_executed"] is False


def test_no_freeze_without_real_independent_review_then_seal(setup):
    bundle, authored, _, _ = setup
    request = s.prepare_submission(bundle, authored, "invented-actor", "initial", "invented-ledger")
    with pytest.raises((ValueError, TypeError)):
        s.freeze_prepared(bundle, "initial", "invented-ledger", None)
    assert not (bundle / "candidates/initial/freeze.json").exists()
    requests = s.freeze_prepared(bundle, "initial", "invented-ledger", review(request["submission_sha256"]), k01_declaration_review=review(request["k01_declaration_sha256"]))
    with pytest.raises(ValueError):
        s.seal_prepared(bundle, "initial", "invented-ledger", {})
    actual = {c: {"binding_review": review(r["binding_sha256"]), "supplement_review": None, "proxy_reviews": {}} for c, r in requests.items()}
    sealed = s.seal_prepared(bundle, "initial", "invented-ledger", actual)
    assert sealed["executed"] is False
    assert not list(bundle.rglob("execution.json"))


def test_mutation_after_preparation_invalidates_review_request(setup):
    bundle, authored, _, _ = setup
    s.prepare_submission(bundle, authored, "invented-actor", "initial", "invented-ledger")
    path = bundle / "candidates/initial/decision.md"
    path.write_text("Changed after packaging", encoding="utf-8")
    with pytest.raises(ValueError, match="payload changed"):
        s.review_requests(bundle, "initial")


@pytest.mark.parametrize("bad", ["extra_file", "false_computed_check", "generator_signature"])
def test_invalid_submission_rejected_before_candidate_write(setup, bad):
    bundle, authored, _, _ = setup
    if bad == "extra_file":
        (authored / "generated.csv").write_text("id\nmade-up\n", encoding="utf-8")
    elif bad == "false_computed_check":
        checks = s._read(authored / "checks.json"); checks["records"][0]["status"] = "pass"
        (authored / "checks.json").write_bytes(s.encoded(checks))
    else:
        (authored / "generator.py").write_text("def generate(observed):\n    return None\n", encoding="utf-8")
    with pytest.raises(ValueError):
        s.prepare_submission(bundle, authored, "invented-actor", "initial", "invented-ledger")
    assert not (bundle / "candidates/initial").exists()


def test_preview_allowlist_is_selected_inputs_not_project_or_s01(setup, tmp_path):
    bundle, _, _, _ = setup
    result = s.render_agent_packet(bundle, "unassigned-preview", "initial", tmp_path / "preview", preview=True)
    assert result["preview_only"] is True
    assert all(not any(x in name for x in ("registry", "INPUT_ASSEMBLY", "statistical_reference", "private", "ledger")) for name in result["allowlist"])
    prompt = (tmp_path / "preview/AGENT_PROMPT.md").read_text(encoding="utf-8")
    assert "PREVIEW ONLY" in prompt and "No desired target signs" in prompt


def test_s01_exact_source_prefix_and_wrapper_without_execution():
    for case_id in ("K01", "K02"):
        raw = s.s01_source(case_id)
        original = (s.assembly._case(case_id) / "implementation/statistical_reference.py").read_bytes()
        assert raw.startswith(original)
        tree = ast.parse(raw.decode("utf-8"))
        assert len([n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "generate"]) == 1
        assert b'return sample(fitted["parameters"], active' in raw


def test_actual_authorization_logic_rejects_wrong_actor_and_unreleased_code(monkeypatch):
    record = {"construction": {"construction_id": "invented-actor"}, "closed": None, "decision": None, "feedback": None, "stages": {}}
    manifest = {"artifacts": [{"path": str(Path(s.__file__).resolve()), "sha256": s.lifecycle.sha256(s.__file__)}]}
    fake = SimpleNamespace(manifest=manifest, snapshot=lambda: {"state": {"wave_closed": None, "reveal": None, "constructors": {"K01:A01": record}}})
    monkeypatch.setattr(s.control.CampaignLedger, "open", lambda *a: fake)
    with pytest.raises(ValueError, match="Actor differs"):
        s._authorization("invented", "K01", "A01", "initial", "other-actor")
    s._authorization("invented", "K01", "A01", "initial", "invented-actor")
    manifest["artifacts"] = []
    with pytest.raises(ValueError, match="actual global release"):
        s._authorization("invented", "K01", "A01", "initial", "invented-actor")


def test_revision_feedback_reverification_rejects_target_inventory(monkeypatch):
    reports = [{"trial_id": "target-2101", "context_id": s.control.TARGETS["K01"], "role": "target", "reports": []}]
    monkeypatch.setattr(s.control, "_verify_stage", lambda *a: {"invented": True})
    monkeypatch.setattr(s.control, "_source_reports", lambda *a: reports)
    record = {"feedback": {}, "stages": {"initial": {"bundle": "invented", "candidate": "initial", "result": {"verified": {"invented": True}}}}}
    with pytest.raises(ValueError, match="source-only inventory"):
        s._feedback(None, record, "K01", "A01")


def test_s01_operand_provenance_and_no_host_derivation(setup, tmp_path, monkeypatch):
    bundle, _, package, _ = setup
    receipt = s.assembly.verify_bundle_inputs(bundle)
    receipt["constructor"] = "S01"
    monkeypatch.setattr(s, "_input", lambda path: (bundle, receipt, package))
    case = tmp_path / "invented_reference"
    case.mkdir()
    (case / "REFERENCE_INPUT_VIEW.json").write_bytes(s.encoded({"normalized_source_constraints": [{"evidence_id": "MIND_K01_age_mean", "value": 65.0}]}))
    monkeypatch.setattr(s.assembly, "_case", lambda case_id: case)
    monkeypatch.setattr(s, "s01_source", lambda case_id: b'raise RuntimeError("Never host import or fit")\ndef generate(observed, specification, seed):\n    raise RuntimeError("Never run in packaging")\n')
    result = s.prepare_s01_authoring(bundle, "invented-actor", "invented-ledger", tmp_path / "reference_submission")
    spec = s._read(tmp_path / "reference_submission/model_spec.json")
    assert spec["parameter_provenance"]["normalized_source_constraints"]["evidence_ids"] == ["MIND_K01_age_mean"]
    assert spec["parameter_provenance"]["contexts"]["evidence_ids"] == []
    assert result["fit_performed"] is False and result["sample_performed"] is False


def test_feedback_packet_precedes_decision_and_does_not_assume_revision(setup, tmp_path, monkeypatch):
    bundle, authored, _, record = setup
    s.prepare_submission(bundle, authored, "invented-actor", "initial", "invented-ledger")
    record["decision"] = None
    calls = []
    monkeypatch.setattr(s, "_authorization", lambda ledger, case, constructor, phase, actor: (calls.append(phase) or None, record))
    monkeypatch.setattr(s, "_feedback", lambda *a: ("b" * 64, {"source_feedback/packet.json": s.encoded({"source_only": True, "target_feedback": False, "reports": []})}))
    result = s.render_feedback_packet(bundle, "invented-actor", tmp_path / "decision_packet", "invented-ledger")
    assert calls == ["feedback"] and result["decision_already_made"] is False and result["revision_authorized"] is False
    assert result["source_feedback_packet_sha256"] == "b" * 64
    assert all("target_logs" not in p and "ledger" not in p for p in result["allowlist"])
    prompt = (tmp_path / "decision_packet/AGENT_PROMPT.md").read_text(encoding="utf-8")
    assert "Choose `retain`, `revise`, or `stop`" in prompt and "Do not create a revised model" in prompt
    assert record["decision"] is None

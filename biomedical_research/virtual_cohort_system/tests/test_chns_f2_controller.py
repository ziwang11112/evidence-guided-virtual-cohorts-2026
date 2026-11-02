"""Controller routing over invented metadata and mocked adapters; no data generation."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest


MODULE = Path(__file__).resolve().parents[1] / "reports/chns_admission_2026-11-01/f2/controller/chns_f2_controller.py"
spec = importlib.util.spec_from_file_location("chns_f2_controller", MODULE)
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(controller.strict._json(value), encoding="utf-8")


def reference(root, name):
    return {"path": name, "sha256": controller.sha256(root / name)}


def approve_candidate(root, slot, *, declined=()):
    directory = root / "candidates" / slot
    review = {"schema_version": 1, "decision": "approved", "reviewer_id": "invented_reviewer",
              "builder_id": "invented_builder", "independent": True, "reviewed_utc": "2026-11-01T00:00:00Z",
              "reason": "Invented controller fixture only.", "release_sha256": controller.sha256(root / "F2_RELEASE.json"),
              "candidate_files": {name: controller.sha256(directory / name) for name in controller.lifecycle._files(directory)
                                  if name not in {controller.CANDIDATE_REVIEW, controller.BINDING}},
              "declined_interpretations": [{"id": key, "reason": "Artificial applicability declination."} for key in declined]}
    write(directory / controller.CANDIDATE_REVIEW, review)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    root = tmp_path / "invented_bundle"
    root.mkdir()
    task = {"schema_version": 1, "task_id": "artificial-controller-test", "mode": "whole_cohort",
            "population": "Invented metadata, not a biomedical population", "row_id": "row_id", "n_rows": 3000,
            "columns": [{"name": "row_id", "kind": "string", "unit": "1", "role": "identifier", "nullable": False}] +
                       [{"name": name, "kind": "number", "unit": "1", "role": "generated", "nullable": False}
                        for name in ("age", "female", "bmi", "glucose", "hba1c")],
            "information_policy": {"mode": "published_evidence", "excluded_cohorts": [], "allowed_tools": []},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 1}}
    write(root / "task.json", task)
    for name in ("PROTOCOL.md", "analysis_plan.json", "BUILDER_BRIEF.md"):
        (root / name).write_text("Invented fixture metadata only.", encoding="utf-8")
    source = root / "template"
    source.mkdir()
    write(source / "evidence.json", {"invented": "No actual study facts."})
    write(source / controller.strict.legacy.PLAN, {"invented": "Fixed strict semantics."})
    write(source / controller.strict.FILE, {"invented": "Unknown weights remain unavailable."})
    assumption = {"id": "A_artificial", "description": "Explicitly invented applicability assumption."}
    interpretations = [{"id": "artificial_pearson", "kind": "invented_mock_only"},
                       {"id": "artificial_spearman", "kind": "invented_mock_only"}]
    policy = {"schema_version": 1, "strict_recipe_sha256": controller.sha256(source / controller.strict.legacy.PLAN),
              "strict_semantics_sha256": controller.sha256(source / controller.strict.FILE),
              "required_assumptions": [assumption], "conditional_interpretations": interpretations}
    write(root / "FEEDBACK_POLICY.json", policy)
    release = {"schema_version": 1, "status": "released", "task_sha256": controller.sha256(root / "task.json"),
               "evidence_sha256": controller.sha256(source / "evidence.json"), "controller_sha256": controller.sha256(MODULE),
               "engine_sha256": controller.engine_hashes(), "schedule": deepcopy(controller.SCHEDULE),
               "limits": deepcopy(controller.LIMITS), "protocol": reference(root, "PROTOCOL.md"),
               "analysis_plan": reference(root, "analysis_plan.json"), "builder_brief": reference(root, "BUILDER_BRIEF.md"),
               "feedback_policy": reference(root, "FEEDBACK_POLICY.json")}
    review = {"schema_version": 1, "decision": "approved", "reviewer_id": "invented_independent_reviewer",
              "coordinator_id": "invented_coordinator", "independent": True, "reviewed_utc": "2026-11-01T00:00:00Z",
              "reason": "Invented release, not actual F2 approval.", "approved_release": deepcopy(release)}
    write(root / "review.json", review)
    release["independent_review"] = reference(root, "review.json")
    write(root / "F2_RELEASE.json", release)
    for construction in controller.CONSTRUCTIONS:
        for stage in controller.STAGES:
            slot = construction + "_" + stage
            directory = root / "candidates" / slot
            directory.mkdir(parents=True)
            for name in ("evidence.json", controller.strict.legacy.PLAN, controller.strict.FILE):
                (directory / name).write_bytes((source / name).read_bytes())
            (directory / "generator.py").write_text("# Artificial placeholder: never executed.\n", encoding="utf-8")
            write(directory / "model_spec.json", {"assumptions": [assumption]})
            write(directory / controller.conditional.FILE, {"builder_id": "invented_builder", "interpretations": interpretations})
            approve_candidate(root, slot)
    calls, failures = [], set()

    def freeze(bundle, candidate, parent_receipt=None, revision=None):
        calls.append(("freeze", candidate, parent_receipt, revision))
        directory = Path(bundle) / candidate
        record = {"candidate": candidate, "route": "generated.csv" if (directory / "generated.csv").exists() else "generator.py"}
        controller.execution._write(directory / "freeze.json", record)
        return record

    monkeypatch.setattr(controller.lifecycle, "freeze_candidate", freeze)
    monkeypatch.setattr(controller.lifecycle, "verify_candidate", lambda bundle, candidate: controller.read_json(Path(bundle) / candidate / "freeze.json"))

    def run(bundle, candidate, run_id, seed, runtime=None, **limits):
        calls.append(("run", run_id, seed, limits))
        folder = Path(bundle) / "executions" / run_id
        folder.mkdir(parents=True)
        receipt = {"candidate": candidate, "status": "failed" if seed in failures else "success", "limits": {"seed": seed, **limits}}
        controller.execution._write(folder / "execution.json", receipt)
        return receipt

    monkeypatch.setattr(controller.execution, "run_candidate", run)
    monkeypatch.setattr(controller.execution, "verify_execution", lambda bundle, run_id: controller.read_json(Path(bundle) / "executions" / run_id / "execution.json"))
    for module, label in ((controller.strict, "strict"), (controller.conditional, "conditional")):
        def preflight(bundle, candidate, label=label):
            calls.append((label + "_preflight", candidate))
            return {"mock": True}

        def collect(bundle, candidate, run_id, feedback_id, *, strict_feedback_id=None, module=module, label=label):
            calls.append((label + "_collect", run_id))
            if label == "conditional":
                assert strict_feedback_id == run_id
                assert (Path(bundle) / controller.strict.FOLDER / run_id / "feedback.json").is_file()
            folder = Path(bundle) / module.FOLDER / feedback_id
            folder.mkdir(parents=True)
            report = {"candidate": candidate, "run_id": run_id, "mock": label, "no_scientific_calculation": True}
            controller.execution._write(folder / "feedback.json", report)
            return report

        def verify(bundle, feedback_id, *, candidate=None, run_id=None, strict_feedback_id=None, module=module, label=label):
            calls.append((label + "_verify", run_id))
            report = controller.read_json(Path(bundle) / module.FOLDER / feedback_id / "feedback.json")
            assert report["candidate"] == candidate and report["run_id"] == run_id
            return report

        monkeypatch.setattr(module, "preflight", preflight)
        monkeypatch.setattr(module, "collect_feedback", collect)
        monkeypatch.setattr(module, "verify_feedback", verify)
    monkeypatch.setattr(controller.strict.legacy, "collect_feedback", lambda *a, **k: pytest.fail("No legacy feedback fallback"))
    return root, calls, failures


def test_released_gate_and_document_hash_precede_any_stage_mutation(setup):
    root, calls, _ = setup
    release = controller.read_json(root / "F2_RELEASE.json")
    release["status"] = "pending_review"
    write(root / "F2_RELEASE.json", release)
    with pytest.raises(ValueError, match="not been released"):
        controller.freeze_stage(root, "C1", "initial")
    assert not (root / controller.FOLDER).exists() and not calls
    release["status"] = "released"
    write(root / "F2_RELEASE.json", release)
    (root / "PROTOCOL.md").write_text("Changed after review.", encoding="utf-8")
    with pytest.raises(ValueError, match="Released document changed"):
        controller.freeze_stage(root, "C1", "initial")
    assert not calls


def test_explicit_routing_fixed_three_seeds_and_no_extra_generation(setup):
    root, calls, _ = setup
    controller.freeze_stage(root, "C1", "initial")
    report = controller.run_stage(root, "C1", "initial")
    assert [call[2] for call in calls if call[0] == "run"] == [1701, 1702, 1703]
    assert all(call[3] == controller.LIMITS for call in calls if call[0] == "run")
    for seed in controller.SEEDS:
        run_id = f"C1_initial_s{seed}"
        order = [call[0] for call in calls if len(call) > 1 and call[1] == run_id]
        assert order == ["run", "strict_collect", "strict_verify", "conditional_collect", "conditional_verify"]
    assert report["aggregate_objective"] is None and len(report["results"]) == 3
    assert controller.revision_feedback(root, "C1") == report


def test_failed_seed_consumes_slot_and_all_three_results_remain(setup):
    root, calls, failures = setup
    failures.add(1702)
    controller.freeze_stage(root, "C1", "initial")
    report = controller.run_stage(root, "C1", "initial")
    assert [row["execution_status"] for row in report["results"]] == ["success", "failed", "success"]
    assert report["results"][1]["strict_feedback"] is None
    assert ("strict_collect", "C1_initial_s1702") not in calls
    with pytest.raises(ValueError, match="already consumed"):
        controller.run_stage(root, "C1", "initial")
    assert len([call for call in calls if call[0] == "run"]) == 3
    assert len(controller.revision_feedback(root, "C1")["results"]) == 3


def test_revision_requires_complete_bound_round_and_schedule_caps_at_twelve(setup):
    root, calls, _ = setup
    revision = {"kind": "revise", "reason": "Artificial bounded revision.", "addressed_findings": [], "remaining_limitations": []}
    with pytest.raises((ValueError, OSError)):
        controller.freeze_stage(root, "C1", "revised", revision=revision)
    assert not (root / controller.FOLDER / "C1_revised").exists()
    for construction in controller.CONSTRUCTIONS:
        controller.freeze_stage(root, construction, "initial")
        controller.run_stage(root, construction, "initial")
        directory = root / "candidates" / f"{construction}_revised"
        (directory / controller.REVISION_FEEDBACK).write_bytes(
            (root / controller.FOLDER / f"{construction}_initial/feedback_round.json").read_bytes())
        approve_candidate(root, f"{construction}_revised")
        controller.freeze_stage(root, construction, "revised", revision=revision)
        controller.run_stage(root, construction, "revised")
    assert len([call for call in calls if call[0] == "run"]) == 12
    for construction, stage in (("C3", "initial"), ("C1", "revised_again"), ("C2", "revised")):
        with pytest.raises(ValueError):
            controller.freeze_stage(root, construction, stage, revision=revision)
    revised = [call for call in calls if call[0] == "freeze" and call[2] is not None]
    assert [call[2] for call in revised] == ["candidates/C1_initial/freeze.json", "candidates/C2_initial/freeze.json"]


@pytest.mark.parametrize("changed", ["recipe", "assumption", "unreviewed_code"])
def test_candidate_cannot_choose_feedback_meaning_or_skip_independent_review(setup, changed):
    root, calls, _ = setup
    directory = root / "candidates/C1_initial"
    if changed == "recipe":
        write(directory / controller.strict.legacy.PLAN, {"invented": "Different statistic."})
        approve_candidate(root, "C1_initial")
    elif changed == "assumption":
        write(directory / "model_spec.json", {"assumptions": [{"id": "A_artificial", "description": "Different interpretation."}]})
        approve_candidate(root, "C1_initial")
    else:
        (directory / "generator.py").write_text("# Changed after independent review.\n", encoding="utf-8")
    with pytest.raises(ValueError):
        controller.freeze_stage(root, "C1", "initial")
    assert not (root / controller.FOLDER).exists() and not calls


def test_documented_proxy_declination_and_direct_table_limit_are_explicit(setup):
    root, calls, _ = setup
    directory = root / "candidates/C1_initial"
    (directory / controller.conditional.FILE).unlink()
    (directory / "generator.py").unlink()
    (directory / "generated.csv").write_text("Invented placeholder; mocked lifecycle, no rows decoded.\n", encoding="utf-8")
    approve_candidate(root, "C1_initial", declined=("artificial_pearson", "artificial_spearman"))
    controller.freeze_stage(root, "C1", "initial")
    report = controller.run_stage(root, "C1", "initial")
    assert report["monte_carlo_replication"] == "not_available_direct_table_reused"
    assert not any(call[0].startswith("conditional_") for call in calls)
    assert len([call for call in calls if call[0] == "strict_collect"]) == 3


def test_interrupted_stage_cannot_retry_or_unlock_revision(setup, monkeypatch):
    root, _, _ = setup
    controller.freeze_stage(root, "C1", "initial")
    monkeypatch.setattr(controller.execution, "run_candidate", lambda *a, **k: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        controller.run_stage(root, "C1", "initial")
    with pytest.raises(ValueError, match="already consumed"):
        controller.run_stage(root, "C1", "initial")
    with pytest.raises((ValueError, OSError)):
        controller.revision_feedback(root, "C1")


@pytest.mark.parametrize("changed", ["result", "summary"])
def test_initial_feedback_tampering_blocks_revision_round(setup, changed):
    root, _, _ = setup
    controller.freeze_stage(root, "C1", "initial")
    controller.run_stage(root, "C1", "initial")
    path = root / controller.FOLDER / "C1_initial/feedback_round.json"
    report = controller.read_json(path)
    if changed == "result":
        report["results"][0]["feedback_status"] = "invented_alteration"
    else:
        report["aggregate_objective"] = 0.1
    write(path, report)
    with pytest.raises(ValueError, match="changed"):
        controller.revision_feedback(root, "C1")

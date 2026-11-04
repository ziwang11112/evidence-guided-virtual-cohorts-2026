"""Focused controller tests: mocked executor only, zero scientific rows."""
import importlib.util
import json
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("core_runner_tests_target", HERE / "runner.py")
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


FLAGS = dict(approved=True, scientific_code_spec_consistency=True,
             finite_moments_supported=True, source_semantics_reviewed=True,
             target_results_used=False, reviewer_id="independent-reviewer")


@pytest.fixture
def env(tmp_path, monkeypatch):
    root = tmp_path / "unit"
    root.mkdir()
    monkeypatch.setattr(r, "ROOT", root)
    write(root / "RUNTIME_PREFLIGHT.json", {"scope": "Mock-only runtime metadata"})
    write(root / "ENDPOINT_CONTRACT.json", {"scope": "Mock-only endpoint metadata"})
    (root / "evaluator.py").write_text("# Mock evaluator; never executed\n", encoding="utf-8")
    provider = tmp_path / "provider.py"
    provider.write_text("# Test provider is never imported\n", encoding="utf-8")
    authors = {}
    for name, case in (("C01", "CHNS2009"), ("C02", "CHNS2009"),
                       ("E01", "ENSANUT2018"), ("E02", "ENSANUT2018")):
        bundle = tmp_path / name
        bundle.mkdir()
        task = {"schema_version": 1, "task_id": name, "mode": "whole_cohort", "population": "Invented controller fixture",
                "row_id": "row_id", "n_rows": 3000,
                "columns": [{"name": "row_id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
                            {"name": "x", "kind": "number", "unit": "1", "role": "generated", "nullable": False}],
                "information_policy": {"mode": "published_evidence", "excluded_cohorts": [], "allowed_tools": ["literature.search", "literature.fetch"]},
                "budget": {"source_queries": 8, "source_downloads": 4, "revisions": 1}}
        write(bundle / "task.json", task)
        write(bundle / "registry.json", {"artifacts": []})
        write(bundle / "SEARCH_LEDGER.json", {"actions": []})
        write(bundle / "gateway/session/state.json", {"usage": {"queries": 0, "downloads": 0}})
        profile = tmp_path / (name + "_profile.json")
        write(profile, {"case_id": case, "information_condition": "open_evidence", "analysis_ids": ["test"]})
        authors[name] = {"bundle": str(bundle), "case_id": case, "profile": str(profile), "provider": str(provider)}
    p = {"authors": authors, "trial_seeds": {"initial": 8100, "revision": 8110},
         "final_seeds": [8101, 8102, 8103], "limits": {"timeout_seconds": 30, "memory_mb": 1536, "output_bytes": 20000000, "log_bytes": 100000},
         "max_physical_executions": 20, "max_feedback_revisions": 1}
    write(root / "PROTOCOL.json", p)
    calls = []
    flags = {"fail_execution": False, "fail_semantic": False, "fail_provider": False}

    def freeze(bundle, candidate, parent_receipt=None, revision=None):
        folder = Path(bundle) / candidate
        if parent_receipt:
            parent = r.READ(parent_receipt)
            result = {"candidate": candidate, "revision_index": 1,
                      "parent": {"candidate": parent["candidate"], "receipt_path": parent["candidate"] + "/freeze.json", "sha256": r.SHA(parent_receipt)}}
        else:
            result = {"candidate": candidate, "revision_index": 0, "parent": None}
        result["route"] = "generated.csv" if (folder / "generated.csv").exists() else "generator.py"
        r.WRITE(folder / "freeze.json", result)
        return result

    def execute(bundle, candidate, run_id, seed, **limits):
        calls.append((str(bundle), candidate, run_id, seed))
        if flags["fail_execution"]:
            raise RuntimeError("Invented backend unavailable")
        path = Path(bundle) / "executions" / run_id
        (path / "output").mkdir(parents=True)
        # Empty bytes only: no generator code executes and no rows are produced.
        (path / "output/generated.csv").write_bytes(b"")
        route = "generated.csv" if (Path(bundle) / candidate / "generated.csv").exists() else "generator.py"
        receipt = {"candidate": candidate, "status": "success", "limits": {"seed": seed},
                   "route": route, "generator_executed": route == "generator.py"}
        r.WRITE(path / "execution.json", receipt)
        return receipt

    def semantic(*args):
        if flags["fail_semantic"]:
            raise RuntimeError("Invented semantic failure")
        return {"status": "complete", "checks": [], "source_population_replay": False}

    def provider(*args):
        if flags["fail_provider"]:
            raise RuntimeError("Invented provider failure")
        return {"analyses": [], "diagnostics": [], "n": 0}

    monkeypatch.setattr(r.lifecycle, "freeze_candidate", freeze)
    monkeypatch.setattr(r.lifecycle, "verify_candidate", lambda b, c: r.READ(Path(b) / c / "freeze.json"))
    monkeypatch.setattr(r.semantic, "preflight", lambda *a: {"checks": []})
    monkeypatch.setattr(r.semantic, "collect_feedback", semantic)
    monkeypatch.setattr(r.execution, "run_candidate", execute)
    monkeypatch.setattr(r.execution, "verify_execution", lambda b, run: r.READ(Path(b) / "executions" / run / "execution.json"))
    monkeypatch.setattr(r, "generated_statistics", provider)

    class Env:
        def candidate(self, author="C01", name="initial", route="generator.py"):
            folder = Path(authors[author]["bundle"]) / "candidates" / name
            folder.mkdir(parents=True)
            (folder / route).write_bytes(b"" if route == "generated.csv" else b"# Unexecuted test-only artifact\n")
            review = tmp_path / f"{author}_{name}_review.json"
            write(review, {**FLAGS, "candidate": "candidates/" + name,
                           "candidate_files": {route: r.SHA(folder / route)}})
            return review

        def start(self, author="C01", route="generator.py"):
            review = self.candidate(author, route=route)
            r.freeze(author, "candidates/initial", review=review, external_author_id="external-" + author)
            return r.Session(author)

        def decision(self, s, name="initial"):
            candidate = "candidates/" + name
            path = tmp_path / (s.author + "_decision.json")
            action = "revise" if name != "initial" else "retain" if s.selected("attempt") else "initial_final"
            write(path, {"author_id": s.author, "candidate": candidate, "action": action, "reason": "Fixture decision",
                         "feedback_hashes": {f["run_id"]: f["feedback"]["sha256"] for f in s.selected("feedback")}})
            review = tmp_path / (s.author + "_final_review.json")
            write(review, {**FLAGS, "candidate_freeze_sha256": r.SHA(s.bundle / candidate / "freeze.json"), "decision_sha256": r.SHA(path)})
            s.decide(path, review)
            return path, review

        def revision(self, s):
            review = self.candidate(s.author, "revised")
            return s.freeze("candidates/revised", "candidates/initial",
                {"kind": "revise", "reason": "Fixture repair", "addressed_findings": [], "remaining_limitations": []}, review)

    result = Env()
    result.calls, result.flags, result.authors, result.root, result.tmp = calls, flags, authors, root, tmp_path
    return result


def test_freeze_requires_bound_independent_review(env):
    review = env.candidate()
    with pytest.raises(ValueError, match="review required"):
        r.freeze("C01", "candidates/initial", external_author_id="external-C01")
    s = r.Session("C01")
    bad = r.READ(review)
    bad["candidate_files"]["generator.py"] = "0" * 64
    write(review, bad)
    with pytest.raises(ValueError, match="stale"):
        s.freeze("candidates/initial", review=review)
    assert not s.selected("freeze") and not env.calls


def test_retain_after_revision_trial_still_draws_three_fresh_finals(env):
    s = env.start()
    with pytest.raises(ValueError, match="Decision required"):
        s.deliver()
    first = s.trial("candidates/initial")
    s.feedback(first["run_id"])
    env.revision(s)
    second = s.trial("candidates/revised", "revision")
    s.feedback(second["run_id"])
    env.decision(s, "initial")  # The initial law may be retained after revision trial.
    s.deliver()
    assert len(env.calls) == 5
    assert [c[3] for c in env.calls] == [8100, 8110, 8101, 8102, 8103]
    assert all(c[1] == "candidates/initial" for c in env.calls[2:])
    assert s.status()["closed"]
    with pytest.raises(ValueError):
        s.trial("candidates/initial")
    with pytest.raises(ValueError):
        s.feedback(first["run_id"])
    with pytest.raises(ValueError):
        s.deliver()


def test_single_direct_revision_and_no_second_construction(env):
    s = env.start()
    review = env.candidate("C01", "other")
    with pytest.raises(ValueError, match="one candidate"):
        s.freeze("candidates/other", review=review)
    with pytest.raises(ValueError, match="initial trial"):
        s.freeze("candidates/other", "candidates/initial", {}, review)
    out = s.trial("candidates/initial")
    s.feedback(out["run_id"])
    env.revision(s)
    with pytest.raises(ValueError, match="one candidate"):
        s.freeze("candidates/other", "candidates/initial", {}, review)
    assert len(s.selected("freeze")) == 2


def test_failed_attempt_charged_without_retry(env):
    s = env.start()
    env.flags["fail_execution"] = True
    result = s.trial("candidates/initial")
    assert result["status"] == "adapter_error" and len(s.selected("attempt")) == 1
    with pytest.raises(ValueError, match="Slot consumed"):
        s.trial("candidates/initial")
    env.revision(s)
    s.trial("candidates/revised", "revision")
    env.decision(s, "revised")
    s.deliver()
    assert len(env.calls) == 5 and s.status()["finals"] == 3
    assert all(x["status"] == "adapter_error" for x in s.selected("result"))


def test_acquisition_closed_but_unrelated_drafts_allowed(env):
    s = env.start()
    write(s.bundle / "drafts/later.json", {"note": "Unrelated working draft"})
    assert s.verify()
    write(s.bundle / "gateway/session/state.json", {"usage": {"queries": 1, "downloads": 0}})
    with pytest.raises(ValueError, match="acquisition inputs changed"):
        s.verify()
    assert not env.calls


def test_feedback_failure_keeps_success_and_binding_required(env):
    s = env.start()
    result = s.trial("candidates/initial")
    env.flags.update(fail_semantic=True, fail_provider=True)
    event = s.feedback(result["run_id"])
    data = r.READ(event["feedback"]["path"])
    assert data["semantic_status"] == data["generated_status"] == "error"
    assert s.selected("result")[0]["status"] == "success"
    assert s.selected("result")[0]["table"]["sha256"] == r.SHA(s.bundle / "executions" / result["run_id"] / "output/generated.csv")
    env.decision(s)
    s.deliver()
    assert len(env.calls) == 4 and s.status()["closed"]


def test_unbudgeted_execution_directory_rejected(env):
    s = env.start()
    (s.bundle / "executions/unreserved").mkdir(parents=True)
    with pytest.raises(ValueError, match="Unbudgeted"):
        s.verify()


def test_all_four_closure_required_and_postclosure_mutation_rejected(env):
    s = env.start()
    s.abandon("Fixture terminal failure")
    with pytest.raises((ValueError, FileNotFoundError)):
        r.seal_batch()
    for name in ("C02", "E01", "E02"):
        r.abandon(name, "No deliverable fixture", external_author_id="external-" + name)
    closed = r.seal_batch()
    assert closed["physical_attempts"] == 0 and closed["scheduled_final_slots"] == 12
    assert r.closure_gate() == closed
    record = s.folder / "events/0002.json"
    data = r.READ(record)
    data["reason"] = "Changed closure"
    write(record, data)
    with pytest.raises(ValueError, match="commitments changed"):
        r.closure_gate()


def test_protocol_changes_rejected_before_next_attempt(env):
    s = env.start()
    p = r.READ(env.root / "PROTOCOL.json")
    p["limits"]["memory_mb"] = 1024
    write(env.root / "PROTOCOL.json", p)
    with pytest.raises(ValueError, match="commitment changed"):
        s.trial("candidates/initial")
    assert not env.calls


def test_decision_cannot_ignore_feedback_or_bind_stale_review(env):
    s = env.start()
    result = s.trial("candidates/initial")
    with pytest.raises(ValueError, match="feedback"):
        env.decision(s)
    s.feedback(result["run_id"])
    path = env.tmp / "bad_decision.json"
    write(path, {"author_id": s.author, "candidate": "candidates/initial", "action": "retain",
                 "reason": "Test", "feedback_hashes": {}})
    review = env.tmp / "bad_review.json"
    write(review, {**FLAGS, "candidate_freeze_sha256": r.SHA(s.bundle / "candidates/initial/freeze.json"), "decision_sha256": r.SHA(path)})
    with pytest.raises(ValueError, match="bind every"):
        s.decide(path, review)
    assert not s.selected("decision")


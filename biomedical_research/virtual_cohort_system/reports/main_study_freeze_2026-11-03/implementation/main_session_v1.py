"""Bounded main-study execution; no target reference reader or model launcher.

Authors are dispatched externally with fresh contexts. This controller records
their identity, commits submissions, charges attempts before execution, and
uses the existing isolated executor and semantic-feedback v1. Analytic source
calculations are retained/reviewed separately; target rows never masquerade as
source-population replay. Hashes are procedural commitments, not signatures.
"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from cohort_harness import execution, lifecycle, semantic_feedback_v1 as semantic
from cohort_harness.contracts import require, validate_task

BUDGET = {"exploratory_attempts": 2, "final_attempts": 3,
          "total_attempts": 5, "rows": 3000,
          "trial_seeds": [5201, 5202], "final_seeds": [5101, 5102, 5103]}
SHA = lifecycle.sha256
READ = lifecycle.read_json
WRITE = execution._write


def now():
    return datetime.now(timezone.utc).isoformat()


def inside(root, value):
    path = Path(value)
    path = path if path.is_absolute() else Path(root) / path
    require(".." not in path.parts, "Traversal rejected")
    require(not any(lifecycle._link(p) for p in [path, *path.parents]), "Linked path rejected")
    path = path.resolve()
    require(path.is_relative_to(Path(root).resolve()), "Path outside session")
    return path


def bound(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": SHA(path)}


def verify_bound(value):
    require(SHA(value["path"]) == value["sha256"], "Bound artifact changed: " + value["path"])


def initialize(root, profile, provider, *, author_id, dependencies=()):
    root = Path(root).absolute()
    require(not any(lifecycle._link(p) for p in [root, *root.parents]), "Linked root")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    require(not (root / "session").exists(), "Session exists")
    require(not any(root.rglob("freeze.json")) and not any(root.rglob("execution.json")), "Cannot adopt old runs")
    task = READ(root / "bundle/task.json")
    validate_task(task)
    require(task["mode"] == "whole_cohort" and task["n_rows"] == BUDGET["rows"], "Expected 3000-row whole cohort")
    require(not (root / "bundle/observed.csv").exists(), "No individual input")
    require(task["budget"] == {"source_queries": 0, "source_downloads": 0, "revisions": 1}, "New intake not admitted")
    config = READ(profile)
    require(config["information_condition"] in {"E0", "E1"}, "Unknown condition")
    require(config["case_id"] in {"CHNS2009", "ENSANUT2018"}, "Unknown case")
    require(config["source_numeric_mode"] == "reviewed_analytic_only", "No new source replay adapter")
    require(not any(k in config for k in ("reference", "reference_summary", "target_results")), "Reference forbidden in author profile")
    require(config["budget"] == BUDGET, "Profile budget mismatch")
    require(config["analysis_ids"] and len(config["analysis_ids"]) == len(set(config["analysis_ids"])), "Analysis IDs missing/duplicate")
    require(author_id and config["constructor_kind"] in {"agent", "statistical"}, "Missing constructor identity")
    (root / "session/events").mkdir(parents=True)
    (root / "session/snapshots").mkdir()
    files = [Path(profile), Path(provider), Path(__file__),
             *sorted((PROJECT / "cohort_harness").glob("*.py")),
             *sorted(p for p in (root / "bundle").rglob("*") if p.is_file()),
             *map(Path, dependencies)]
    bindings = []
    for i, source in enumerate(dict.fromkeys(p.resolve() for p in files)):
        snapshot = root / "session/snapshots" / f"{i:03d}_{source.name}"
        shutil.copyfile(source, snapshot)
        bindings.append({**bound(source), "snapshot": str(snapshot.relative_to(root))})
    contract = {"kind": "main_session_v1", "root": str(root), "author_id": author_id,
                "profile": str(Path(profile).resolve()), "provider": str(Path(provider).resolve()),
                "case_id": config["case_id"], "information_condition": config["information_condition"],
                "constructor_kind": config["constructor_kind"], "analysis_ids": config["analysis_ids"],
                "budget": BUDGET, "bindings": bindings, "created_utc": now(),
                "feedback_engine": "semantic_feedback_v1", "source_numeric_mode": config["source_numeric_mode"],
                "target_reference_access": "not_supplied", "author_tool_isolation": "procedural_only"}
    WRITE(root / "session/contract.json", contract)
    return Session(root).status()


class Session:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.folder = inside(self.root, "session")
        self.bundle = inside(self.root, "bundle")
        self.contract = READ(self.folder / "contract.json")
        require(self.contract["root"] == str(self.root) and self.contract["kind"] == "main_session_v1", "Session identity changed")
        require(self.contract["budget"] == BUDGET, "Budget changed")

    def events(self):
        result, previous = [], SHA(self.folder / "contract.json")
        for i, path in enumerate(sorted((self.folder / "events").glob("*.json")), 1):
            event = READ(path)
            require(path.name == f"{i:04d}.json" and event["index"] == i and event["previous_sha256"] == previous, "Ledger damaged")
            result.append(event)
            previous = SHA(path)
        return result

    def selected(self, kind):
        return [e for e in self.events() if e["kind"] == kind]

    def add(self, kind, **data):
        events = self.events()
        previous = self.folder / "events" / f"{len(events):04d}.json" if events else self.folder / "contract.json"
        value = {"index": len(events)+1, "kind": kind, "created_utc": now(), "previous_sha256": SHA(previous), **data}
        WRITE(self.folder / "events" / f"{len(events)+1:04d}.json", value)
        return value

    def verify(self):
        for binding in self.contract["bindings"]:
            verify_bound(binding)
            require(SHA(inside(self.root, binding["snapshot"])) == binding["sha256"], "Snapshot changed")
        for event in self.events():
            if event["kind"] == "freeze":
                lifecycle.verify_candidate(self.bundle, event["candidate"])
                require(SHA(self.bundle / event["candidate"] / "freeze.json") == event["freeze_sha256"], "Freeze changed")
            for key in ("decision", "review", "feedback"):
                if isinstance(event.get(key), dict) and "sha256" in event[key]:
                    verify_bound(event[key])
            if event["kind"] == "activation":
                verify_bound(event["release"])
                validate_release(READ(event["release"]["path"]))
            if event["kind"] == "result" and event.get("receipt"):
                verify_bound(event["receipt"])
                execution.verify_execution(self.bundle, event["run_id"])
        return True

    def activate(self, release_path):
        with self.lock():
            require(not self.selected("activation"), "Session already activated")
            release = READ(release_path)
            validate_release(release)
            slots = [s for s in release["constructions"] if s["id"] == self.contract["author_id"]]
            require(len(slots) == 1 and Path(slots[0]["session_root"]).resolve() == self.root and
                    slots[0]["contract_sha256"] == SHA(self.folder / "contract.json"), "Session not in release")
            return self.add("activation", release=bound(release_path))

    @contextmanager
    def lock(self):
        path = self.folder / "operation.lock"
        with path.open("x", encoding="utf-8") as stream:
            stream.write(now())
        try:
            self.verify()
            yield
        finally:
            path.unlink()

    def status(self):
        self.verify()
        attempts = self.selected("attempt")
        return {"case_id": self.contract["case_id"], "condition": self.contract["information_condition"],
                "attempts": len(attempts), "trials": sum(e["purpose"] == "trial" for e in attempts),
                "finals": sum(e["purpose"] == "final" for e in attempts), "closed": bool(self.selected("closed")),
                "budget": BUDGET}

    def dispatch(self, external_id):
        with self.lock():
            require(len(self.selected("activation")) == 1, "Independent campaign release required")
            require(isinstance(external_id, str) and external_id and not self.selected("dispatch"), "One actual external dispatch only")
            return self.add("dispatch", external_id=external_id, constructor_id=self.contract["author_id"],
                            note="Actual external invocation; constructor identity is distinct from orchestration task ID")

    def freeze(self, candidate):
        with self.lock():
            require(self.selected("dispatch") and not self.selected("science_closed"), "Scientific construction not open")
            directory, relative = lifecycle._candidate(self.bundle, candidate)
            require(not (directory / "generated.csv").exists(), "This main allocation uses stochastic programs")
            uptake = READ(directory / "numerical_uptake.json")
            require(isinstance(uptake.get("records"), list), "Explicit numerical uptake records required")
            ids = [r["operation_id"] for r in uptake["records"]]
            require(len(ids) == len(set(ids)), "Duplicate uptake operation")
            require(all(r["use"] in {"model_constraint", "analytic_check", "context_only", "declined"} for r in uptake["records"]), "Invalid uptake status")
            require((directory / "mathematical_properties.md").read_text(encoding="utf-8").strip(), "Mathematical properties record required")
            gates = semantic.preflight(self.bundle, relative)
            require(all(r["semantic_status"] == "unavailable" for r in gates["checks"]), "Target cannot replay source population")
            lifecycle.freeze_candidate(self.bundle, relative)
            return self.add("freeze", candidate=relative, freeze_sha256=SHA(directory / "freeze.json"))

    def _frozen(self, candidate):
        directory, relative = lifecycle._candidate(self.bundle, candidate)
        require(any(e["candidate"] == relative and e["freeze_sha256"] == SHA(directory / "freeze.json") for e in self.selected("freeze")), "Not session frozen")
        lifecycle.verify_candidate(self.bundle, relative)
        return relative

    def _run(self, candidate, purpose, seed):
        require(len(self.selected("activation")) == 1, "Campaign not activated")
        require(not self.selected("closed"), "Session closed")
        relative = self._frozen(candidate)
        attempts = self.selected("attempt")
        require(len(attempts) < BUDGET["total_attempts"], "Total attempt cap")
        if purpose == "trial":
            require(not self.selected("science_closed"), "Trials end at science closure")
            require(seed in BUDGET["trial_seeds"], "Invalid trial seed")
            require(sum(e["purpose"] == "trial" for e in attempts) < 2, "Two total exploratory attempts exhausted")
        else:
            closed = self.selected("science_closed")
            require(len(closed) == 1 and closed[0]["candidate"] == relative, "Final configuration not selected")
            require(seed in BUDGET["final_seeds"], "Invalid final seed")
        require(not any(e["purpose"] == purpose and e["seed"] == seed for e in attempts), "Slot consumed; no retry")
        run_id = f"a{len(attempts)+1:02d}_{purpose}_{seed}"
        intent = self.add("attempt", candidate=relative, purpose=purpose, seed=seed, run_id=run_id)
        try:
            result = execution.run_candidate(self.bundle, relative, run_id, seed)
            return self.add("result", attempt_index=intent["index"], run_id=run_id, status=result["status"],
                            receipt=bound(self.bundle / "executions" / run_id / "execution.json"), error=result.get("error"))
        except Exception as error:
            self.add("result", attempt_index=intent["index"], run_id=run_id, status="adapter_error", receipt=None,
                     error={"type": type(error).__name__, "message": str(error)})
            raise

    def trial(self, candidate, seed):
        with self.lock():
            return self._run(candidate, "trial", seed)

    def trial_feedback(self, run_id):
        with self.lock():
            matches = [e for e in self.selected("attempt") if e["run_id"] == run_id and e["purpose"] == "trial"]
            require(len(matches) == 1, "Feedback only from exploratory trial")
            require(not any(e["run_id"] == run_id for e in self.selected("feedback")), "Feedback already produced")
            receipt = execution.verify_execution(self.bundle, run_id)
            require(receipt["status"] == "success", "No statistics from failed run")
            candidate = matches[0]["candidate"]
            semantic_id = "main_" + run_id
            strict = semantic.collect_feedback(self.bundle, candidate, run_id, semantic_id)
            require(all(r["calculation"] is None for r in strict["checks"]), "Target-as-source comparison rejected")
            spec = importlib.util.spec_from_file_location("main_generated_only", self.contract["provider"])
            provider = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(provider)
            generated = provider.evaluate_generated(self.bundle, candidate, run_id, Path(self.contract["profile"]))
            require(set(generated) <= {"analyses", "diagnostics", "quality", "n"}, "Provider returned undeclared/reference fields")
            for key in ("analyses", "diagnostics"):
                require(all(set(row) <= {"id", "value", "unit", "status", "n", "rank", "reason"} for row in generated[key]), "Reference fields in generated statistics")
            require(sorted(r["id"] for r in generated["analyses"]) == sorted(self.contract["analysis_ids"]), "Analysis coverage mismatch")
            path = self.folder / f"feedback_{run_id}.json"
            WRITE(path, {"kind": "generated_only_main_feedback", "run_id": run_id,
                         "semantic_feedback_v1": strict, "generated": generated,
                         "scope": "Own generated table; no target reference and no source-population replay"})
            return self.add("feedback", run_id=run_id, feedback=bound(path))

    def close_science(self, candidate, decision, review):
        """Review certifies artifact/finite-moment readiness, never favorable fit."""
        with self.lock():
            require(not self.selected("science_closed"), "Already selected final")
            relative = self._frozen(candidate)
            decision, review = inside(self.root, decision), inside(self.root, review)
            choice, audit = READ(decision), READ(review)
            freeze_sha = SHA(self.bundle / relative / "freeze.json")
            require(choice["author_id"] == self.contract["author_id"] and choice["candidate"] == relative, "Wrong author decision")
            require(choice["action"] in {"initial_final", "retain", "revise"} and choice["reason"], "Invalid decision")
            require(audit["candidate_freeze_sha256"] == freeze_sha and audit["decision_sha256"] == SHA(decision), "Review unbound")
            require(audit["reviewer_id"] not in {self.contract["author_id"], self.selected("dispatch")[0]["external_id"]}, "Independent reviewer required")
            require(audit["status"] == "ready" and audit["finite_moments_checked"] is True and audit["numerical_uptake_checked"] is True,
                    "Implementation/scientific audit not ready")
            require(audit["target_results_used"] is False, "Target-directed review forbidden")
            require(not any(e["purpose"] == "final" for e in self.selected("attempt")), "Cannot select after final output")
            return self.add("science_closed", candidate=relative, decision=bound(decision), review=bound(review))

    def deliver(self):
        with self.lock():
            selected = self.selected("science_closed")
            require(len(selected) == 1 and not self.selected("closed"), "Final stage unavailable")
            used = {e["seed"] for e in self.selected("attempt") if e["purpose"] == "final"}
            for seed in BUDGET["final_seeds"]:
                if seed in used:
                    continue
                try:
                    self._run(selected[0]["candidate"], "final", seed)
                except Exception:
                    latest = self.selected("attempt")[-1]
                    require(latest["purpose"] == "final" and latest["seed"] == seed and
                            any(e["attempt_index"] == latest["index"] for e in self.selected("result")), "Uncharged failure")
            return self.add("closed", status="all_final_slots_consumed", final_attempts=3)

    def abandon(self, reason):
        """Keep an unsuccessful construction in the completion denominator."""
        with self.lock():
            require(not self.selected("closed") and bool(reason), "Already closed or missing reason")
            return self.add("closed", status="construction_failed", reason=reason,
                            final_attempts=sum(e["purpose"] == "final" for e in self.selected("attempt")))


def validate_release(release):
    require(release["execution_enabled"] is True and release["kind"] == "main_study_release_v1", "Campaign not released")
    require(release["budget"] == BUDGET and release["maximum_total_attempts"] == 120, "Release budget changed")
    verify_bound(release["independent_review"])
    review = READ(release["independent_review"]["path"])
    require(review["status"] == "ready" and review["target_results_used_for_binding"] is False, "Independent release review not ready")
    for binding in release["artifacts"]:
        verify_bound(binding)
    payload = {k: v for k, v in release.items() if k not in {"independent_review", "execution_enabled"}}
    import hashlib
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    require(review["release_payload_sha256"] == digest, "Review not bound to release")
    require(len(release["constructions"]) == 24 and len({s["id"] for s in release["constructions"]}) == 24, "Full24allocation required")
    counts = {(c, e, k): 0 for c in ("CHNS2009", "ENSANUT2018") for e in ("E0", "E1") for k in ("agent", "statistical")}
    for slot in release["constructions"]:
        contract_path = Path(slot["session_root"]) / "session/contract.json"
        require(SHA(contract_path) == slot["contract_sha256"], "Release session binding changed")
        contract = READ(contract_path)
        require(contract["author_id"] == slot["id"] and contract["budget"] == BUDGET, "Wrong session identity or budget")
        counts[tuple(contract[k] for k in ("case_id", "information_condition", "constructor_kind"))] += 1
    require(all(n == (5 if k[2] == "agent" else 1) for k, n in counts.items()), "Release allocation changed")
    return True


def require_campaign_closed(release):
    """Called before the reference evaluator opens any clinical measurements."""
    validate_release(release)
    slots = release["constructions"]
    require(len(slots) == 24 and len({s["id"] for s in slots}) == 24, "Expected all 24 constructors")
    counts = {(c, e, k): 0 for c in ("CHNS2009", "ENSANUT2018") for e in ("E0", "E1") for k in ("agent", "statistical")}
    result = []
    for slot in slots:
        session = Session(slot["session_root"])
        require(SHA(session.folder / "contract.json") == slot["contract_sha256"], "Campaign contract changed")
        session.verify()
        require(session.contract["author_id"] == slot["id"], "Constructor identity mismatch")
        key = tuple(session.contract[k] for k in ("case_id", "information_condition", "constructor_kind"))
        counts[key] += 1
        require(len(session.selected("closed")) == 1, "All cases/conditions must close before evaluation")
        result.append(session.status())
    require(all(n == (5 if key[2] == "agent" else 1) for key, n in counts.items()), "Allocation changed")
    return result

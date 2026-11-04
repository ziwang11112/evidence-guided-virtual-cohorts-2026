"""Bounded four-author core workflow. No reference reader or model launcher.

Protocol fields:
 authors: {ID: {bundle, case_id, provider, profile, dependencies?: [absolute paths]}}
 trial_seeds: {initial: int, revision: int}; final_seeds: [int, int, int]
 limits: {timeout_seconds, memory_mb, output_bytes, log_bytes}
 max_physical_executions: 20; max_feedback_revisions: 1
 Optional dependencies: [absolute paths], source_acquisition: {max_originals: 4}.

Source acquisition ends at first freeze (or terminal abandonment), not first
trial. Immutable inputs include root files existing then and the complete
sources/, gateway/ and input/ trees. Future draft/candidate/output writes are
outside that input manifest. Gateway use after closure changes its audit/state
and is rejected on the next verification; this is procedural, not OS isolation.

Decision JSON: author_id, candidate ("candidates/NAME"), action
("retain", "revise"), reason, feedback_hashes {run_id: digest}.
Review JSON: approved, scientific_code_spec_consistency, finite_moments_supported,
source_semantics_reviewed all true; target_results_used false; reviewer_id
distinct from author/external_author_id; candidate_freeze_sha256 and
decision_sha256. Additional review/decision fields are allowed.
Freeze review uses the same Boolean/identity fields, candidate and candidate_files
{relative_name: SHA256} for every pre-freeze candidate file, instead of freeze/
decision hashes. Keep that review outside the candidate. Every freeze requires it.

Source semantic-v1 comparisons may be qualified approximate comparisons under
declared source/measurement/transport assumptions. They are not source-population
replay. Unsupported checks stay unavailable. No legacy collector fallback.
Direct authored rows are permitted; their scheduled seeds label validation slots,
not new random draws. Repeated fixed-table deliveries must not be counted as
independent generated cohorts.
"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import argparse
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness import execution, lifecycle, semantic_feedback_v1 as semantic
from cohort_harness.contracts import require, validate_task

SHA = lifecycle.sha256
READ = lifecycle.read_json
WRITE = execution._write


def now():
    return datetime.now(timezone.utc).isoformat()


def bound(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": SHA(path)}


def verify_bound(record):
    require(SHA(record["path"]) == record["sha256"], "Bound artifact changed: " + record["path"])


def clean_path(root, relative):
    path = Path(root).joinpath(*lifecycle.safe_relative(relative))
    require(not any(lifecycle._link(p) for p in [path, *path.parents]), "Linked path rejected")
    require(path.resolve().is_relative_to(Path(root).resolve()), "Path escapes root")
    return path


def protocol():
    p = READ(ROOT / "PROTOCOL.json")
    require(len(p["authors"]) == 4 and len(set(p["authors"])) == 4, "Exactly four authors required")
    counts = {case: sum(a["case_id"] == case for a in p["authors"].values())
              for case in ("CHNS2009", "ENSANUT2018")}
    require(counts == {"CHNS2009": 2, "ENSANUT2018": 2}, "Two authors per fixed case required")
    require(len({str(Path(a["bundle"]).resolve()) for a in p["authors"].values()}) == 4,
            "Authors need distinct bundles")
    require(set(p["trial_seeds"]) == {"initial", "revision"}, "Two named trial slots required")
    seeds = list(p["trial_seeds"].values()) + p["final_seeds"]
    require(len(p["final_seeds"]) == 3 and len(seeds) == len(set(seeds)) == 5 and
            all(type(seed) is int and seed >= 0 for seed in seeds), "Distinct scheduled seeds required")
    require(p["max_physical_executions"] == 20 and p["max_feedback_revisions"] == 1, "Batch budget changed")
    execution._limits(**p["limits"], seed=0)
    return p


def control_files(p):
    files = {Path(__file__).resolve(), ROOT / "PROTOCOL.json",
             ROOT / "RUNTIME_PREFLIGHT.json", ROOT / "evaluator.py",
             ROOT / "ENDPOINT_CONTRACT.json"}
    files.update(PROJECT.joinpath("cohort_harness").glob("*.py"))
    files.add(PROJECT / "cohort_harness/_vendor/literature_gateway.py")
    for a in p["authors"].values():
        files.update(Path(a[k]).resolve() for k in ("provider", "profile"))
        files.update(Path(f).resolve() for f in a.get("dependencies", []))
    files.update(Path(f).resolve() for f in p.get("dependencies", []))
    return sorted(files, key=str)


def ensure_control():
    p = protocol()
    path = ROOT / "CONTROL.json"
    expected = {"kind": "core_workflow_control_v1", "files": [bound(f) for f in control_files(p)]}
    if not path.exists():
        try:
            WRITE(path, expected)
        except FileExistsError:
            pass
    require(READ(path) == expected, "Protocol or controller/dependency commitment changed")
    return p


def input_snapshot(bundle):
    """No candidate, output, target or draft read."""
    files = {p for p in bundle.iterdir() if p.is_file()}
    for folder in ("sources", "gateway", "input"):
        base = bundle / folder
        if base.exists():
            for p in base.rglob("*"):
                clean_path(bundle, p.relative_to(bundle).as_posix())
                if p.is_file():
                    files.add(p)
    require(not any(p.name.endswith(".lock") or p.name == "lock" for p in files), "Acquisition operation remains open")
    return {p.relative_to(bundle).as_posix(): SHA(clean_path(bundle, p.relative_to(bundle).as_posix()))
            for p in sorted(files, key=str)}


def initialize(author, external_author_id):
    p = ensure_control()
    require(author in p["authors"] and isinstance(external_author_id, str) and external_author_id.strip(),
            "Actual fresh external author identity required")
    folder = ROOT / "sessions" / author
    require(not folder.exists(), "Session already initialized; never replace it")
    spec = p["authors"][author]
    bundle = lifecycle._bundle(spec["bundle"])
    task = READ(bundle / "task.json")
    validate_task(task)
    for key, name in (("task_sha256", "task.json"), ("request_sha256", "request.json")):
        if key in spec:
            require(SHA(bundle / name) == spec[key], "Prospective author input changed: " + name)
    require(task["mode"] == "whole_cohort" and task["n_rows"] == 3000, "Fixed whole-cohort task required")
    require(not (bundle / "observed.csv").exists(), "No participant input")
    require(task["budget"] == {"source_queries": 8, "source_downloads": 4, "revisions": 1}, "Acquisition/revision budget changed")
    require(not (bundle / "executions").exists() or not any((bundle / "executions").iterdir()), "Cannot adopt old executions")
    require(not any((bundle / "candidates").rglob("freeze.json")) if (bundle / "candidates").exists() else True,
            "Cannot adopt old frozen candidates")
    lifecycle._registry(bundle)
    registry = READ(bundle / "registry.json")
    original_ids = {r["source_id"] for r in registry["artifacts"] if not r["source_id"].startswith("search-")}
    require(len(original_ids) <= p.get("acquisition", {}).get("per_author_originals_and_downloads", 4), "Original-source cap exceeded")
    require((bundle / "SEARCH_LEDGER.json").is_file(), "Search ledger required before acquisition closes")
    state = READ(bundle / "gateway/session/state.json")
    require(state["usage"]["queries"] <= 8 and state["usage"]["downloads"] <= 4, "Gateway budget exceeded")
    snapshot = input_snapshot(bundle)
    folder.mkdir(parents=True)
    (folder / "events").mkdir()
    WRITE(folder / "inputs.json", {"files": snapshot, "root_files": [x for x in snapshot if "/" not in x],
          "protected_trees": ["sources", "gateway", "input"], "acquisition_closed_utc": now(),
          "original_source_ids": sorted(original_ids), "scope": "No source acquisition after this commitment"})
    WRITE(folder / "contract.json", {"kind": "core_workflow_author_v1", "author_id": author,
          "external_author_id": external_author_id, "case_id": spec["case_id"], "bundle": str(bundle),
          "control_sha256": SHA(ROOT / "CONTROL.json"), "inputs_sha256": SHA(folder / "inputs.json"),
          "created_utc": now()})
    return Session(author)


class Session:
    def __init__(self, author):
        self.p = ensure_control()
        require(author in self.p["authors"], "Unknown author")
        self.author = author
        self.spec = self.p["authors"][author]
        self.bundle = lifecycle._bundle(self.spec["bundle"])
        self.folder = ROOT / "sessions" / author
        self.contract = READ(self.folder / "contract.json")
        require(self.contract["author_id"] == author and self.contract["bundle"] == str(self.bundle), "Session identity changed")

    def events(self):
        events = []
        previous = SHA(self.folder / "contract.json")
        for i, path in enumerate(sorted((self.folder / "events").glob("*.json")), 1):
            e = READ(path)
            require(path.name == f"{i:04d}.json" and e["index"] == i and e["previous_sha256"] == previous, "Ledger damaged")
            events.append(e)
            previous = SHA(path)
        return events

    def selected(self, kind):
        return [e for e in self.events() if e["kind"] == kind]

    def add(self, kind, **data):
        events = self.events()
        previous = self.folder / "events" / f"{len(events):04d}.json" if events else self.folder / "contract.json"
        e = {"index": len(events)+1, "kind": kind, "created_utc": now(),
             "previous_sha256": SHA(previous), **data}
        WRITE(self.folder / "events" / f"{e['index']:04d}.json", e)
        return e

    def verify(self):
        ensure_control()
        require(self.contract["control_sha256"] == SHA(ROOT / "CONTROL.json"), "Control binding changed")
        require(self.contract["inputs_sha256"] == SHA(self.folder / "inputs.json"), "Input manifest changed")
        manifest = READ(self.folder / "inputs.json")
        current = {name: SHA(clean_path(self.bundle, name)) for name in manifest["root_files"]}
        for folder in manifest["protected_trees"]:
            base = self.bundle / folder
            if base.exists():
                for path in base.rglob("*"):
                    clean_path(self.bundle, path.relative_to(self.bundle).as_posix())
                    if path.is_file():
                        current[path.relative_to(self.bundle).as_posix()] = SHA(path)
        require(current == manifest["files"], "Frozen source/task/acquisition inputs changed")
        events = self.events()
        attempts = [e for e in events if e["kind"] == "attempt"]
        require(len(attempts) <= 5 and len({e["run_id"] for e in attempts}) == len(attempts), "Invalid attempt inventory")
        actual = {p.name for p in (self.bundle / "executions").iterdir() if p.is_dir()} if (self.bundle / "executions").exists() else set()
        require(actual <= {e["run_id"] for e in attempts}, "Unbudgeted execution directory")
        freezes = self.selected("freeze")
        require(len(freezes) <= 2 and sum(e["stage"] == "initial" for e in freezes) <= 1 and
                sum(e["stage"] == "revision" for e in freezes) <= 1, "Candidate family budget exceeded")
        for e in events:
            if e["kind"] == "freeze":
                receipt = lifecycle.verify_candidate(self.bundle, e["candidate"])
                require(SHA(self.bundle / e["candidate"] / "freeze.json") == e["freeze_sha256"], "Freeze changed")
                if e["stage"] == "initial":
                    require(receipt["revision_index"] == 0 and receipt["parent"] is None, "Initial lineage changed")
                else:
                    initial = next(f for f in freezes if f["stage"] == "initial")
                    require(receipt["revision_index"] == 1 and receipt["parent"] == {
                        "candidate": initial["candidate"], "receipt_path": initial["candidate"] + "/freeze.json",
                        "sha256": initial["freeze_sha256"]}, "Revision lineage changed")
            for key in ("feedback", "decision", "review", "unverified_receipt"):
                if key in e:
                    verify_bound(e[key])
            if e["kind"] == "result" and e.get("receipt"):
                verify_bound(e["receipt"])
                receipt = execution.verify_execution(self.bundle, e["run_id"])
                a = next(x for x in attempts if x["index"] == e["attempt_index"])
                require(receipt["candidate"] == a["candidate"] and receipt["limits"]["seed"] == a["seed"], "Execution identity changed")
                if e.get("table"):
                    verify_bound(e["table"])
        return True

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

    def open_science(self):
        require(not self.selected("decision") and not self.selected("closed"), "Scientific author phase closed")

    def _family(self, stage):
        matches = [e for e in self.selected("freeze") if e["stage"] == stage]
        require(len(matches) == 1, "Frozen family stage unavailable")
        return matches[0]

    def freeze(self, candidate, parent=None, revision=None, review=None):
        with self.lock():
            self.open_science()
            directory, relative = lifecycle._candidate(self.bundle, candidate)
            require(not any(e["candidate"] == relative for e in self.selected("freeze")), "Candidate already frozen")
            stage = "initial" if parent is None else "revision"
            require(not any(e["stage"] == stage for e in self.selected("freeze")), "Only one candidate per family stage")
            require(review is not None, "Independent pre-freeze review required")
            review_path = Path(review).resolve()
            require(not review_path.is_relative_to(directory.resolve()), "Review must be outside candidate")
            audit = READ(review_path)
            self._review_flags(audit)
            require(audit["candidate"] == relative and audit["candidate_files"] == {
                name: SHA(directory / name) for name in lifecycle._files(directory)}, "Pre-freeze review is stale")
            if stage == "initial":
                require(not self.selected("freeze") and revision is None, "Second independent construction forbidden")
                parent_receipt = None
            else:
                initial = self._family("initial")
                _, parent_relative = lifecycle._candidate(self.bundle, parent)
                require(parent_relative == initial["candidate"] and relative != parent_relative and revision is not None, "Direct revision of initial required")
                require(any(e["stage"] == "initial" for e in self.selected("attempt")), "Feedback revision requires initial trial")
                self._resolved_trials(require_feedback=True)
                parent_receipt = self.bundle / parent_relative / "freeze.json"
            gates = semantic.preflight(self.bundle, relative)
            receipt = lifecycle.freeze_candidate(self.bundle, relative, parent_receipt=parent_receipt, revision=revision)
            require(receipt["revision_index"] == (0 if stage == "initial" else 1), "Unexpected revision index")
            return self.add("freeze", candidate=relative, stage=stage,
                            freeze_sha256=SHA(directory / "freeze.json"), semantic_preflight=gates,
                            output_route=receipt["route"],
                            review=bound(review_path))

    def _review_flags(self, review):
        require(all(review.get(key) is True for key in ("approved", "scientific_code_spec_consistency",
                "finite_moments_supported", "source_semantics_reviewed")) and review.get("target_results_used") is False,
                "Scientific consistency review incomplete")
        require(review.get("reviewer_id") and review["reviewer_id"] not in {self.author, self.contract["external_author_id"]},
                "Independent reviewer identity required")

    def _resolved_trials(self, require_feedback):
        for a in self.selected("attempt"):
            results = [r for r in self.selected("result") if r["attempt_index"] == a["index"]]
            require(len(results) == 1, "Unresolved reserved attempt; no retry")
            if a["purpose"] == "trial" and results[0]["status"] == "success" and require_feedback:
                require(any(f["run_id"] == a["run_id"] for f in self.selected("feedback")), "Review every successful trial's feedback")

    def _run(self, candidate, purpose, stage, seed):
        require(not self.selected("closed"), "Author terminally closed")
        attempts = self.selected("attempt")
        require(len(attempts) < 5, "Five physical attempts exhausted")
        require(not any(a["purpose"] == purpose and a["seed"] == seed for a in attempts), "Slot consumed; no retry")
        if purpose == "trial":
            self.open_science()
            require(candidate == self._family(stage)["candidate"], "Trial candidate differs from stage family")
            require(sum(a["purpose"] == "trial" for a in attempts) < 2, "Two trial attempts exhausted")
        else:
            decisions = self.selected("decision")
            require(len(decisions) == 1 and decisions[0]["candidate"] == candidate, "Final selection required")
        lifecycle.verify_candidate(self.bundle, candidate)
        run_id = self.author.lower() + "_" + stage + "_" + str(seed)
        intent = self.add("attempt", purpose=purpose, stage=stage, seed=seed, candidate=candidate, run_id=run_id, charged=True)
        record = {"attempt_index": intent["index"], "run_id": run_id, "receipt": None, "table": None}
        try:
            receipt = execution.run_candidate(self.bundle, candidate, run_id, seed, **self.p["limits"])
            record.update(status=receipt["status"], error=receipt.get("error"),
                          adapter_reported_status=receipt["status"], adapter_reported_error=receipt.get("error"),
                          receipt=bound(self.bundle / "executions" / run_id / "execution.json"))
            verified = execution.verify_execution(self.bundle, run_id)
            require(verified["candidate"] == candidate and verified["limits"]["seed"] == seed, "Wrong execution receipt")
            record.update(output_route=verified["route"],
                          generator_executed=verified.get("generator_executed"),
                          seed_role="fixed_table_validation_slot" if verified["route"] == "generated.csv"
                          else "program_sampling_input_independence_not_certified")
            if receipt["status"] == "success":
                record["table"] = bound(self.bundle / "executions" / run_id / "output/generated.csv")
        except Exception as exc:
            if record["receipt"] is not None:
                # Preserve the exact failed receipt bytes without treating them
                # as a verified execution or preventing terminal failure closure.
                record["unverified_receipt"] = record["receipt"]
                record["receipt"] = None
            record["table"] = None
            record.update(status="adapter_error", error={"type": type(exc).__name__, "message": str(exc)})
        return self.add("result", **record)

    def trial(self, candidate, stage="initial"):
        with self.lock():
            require(stage in self.p["trial_seeds"], "Unknown trial slot")
            _, relative = lifecycle._candidate(self.bundle, candidate)
            return self._run(relative, "trial", stage, self.p["trial_seeds"][stage])

    def feedback(self, run_id):
        with self.lock():
            self.open_science()
            attempts = [a for a in self.selected("attempt") if a["run_id"] == run_id and a["purpose"] == "trial"]
            require(len(attempts) == 1 and not any(f["run_id"] == run_id for f in self.selected("feedback")), "Only one feedback record per trial")
            attempt = attempts[0]
            results = [r for r in self.selected("result") if r["attempt_index"] == attempt["index"]]
            require(len(results) == 1 and results[0]["status"] == "success", "Feedback needs successful verified trial")
            receipt = execution.verify_execution(self.bundle, run_id)
            require(receipt["status"] == "success", "Failed execution cannot supply feedback")
            report = {"run_id": run_id, "candidate": attempt["candidate"], "reference_read": False,
                      "scope": "Own generated cohort; qualified source discrepancies are not source-population replay"}
            try:
                report["semantic_feedback_v1"] = semantic.collect_feedback(self.bundle, attempt["candidate"], run_id, run_id + "_source")
                report["semantic_status"] = "complete"
            except Exception as exc:
                report.update(semantic_status="error", semantic_error=type(exc).__name__ + ": " + str(exc))
            try:
                report["generated"] = generated_statistics(self, run_id)
                report["generated_status"] = "complete"
            except Exception as exc:
                report.update(generated_status="error", generated_error=type(exc).__name__ + ": " + str(exc))
            path = self.folder / ("feedback_" + run_id + ".json")
            WRITE(path, report)
            return self.add("feedback", run_id=run_id, feedback=bound(path))

    def decide(self, decision, review):
        with self.lock():
            self.open_science()
            require(any(a["purpose"] == "trial" and a["stage"] == "initial" for a in self.selected("attempt")),
                    "Initial trial must resolve before final decision")
            if any(f["stage"] == "revision" for f in self.selected("freeze")):
                require(any(a["purpose"] == "trial" and a["stage"] == "revision" for a in self.selected("attempt")),
                        "Frozen revision trial must resolve before final decision")
            self._resolved_trials(require_feedback=True)
            decision, review = Path(decision).resolve(), Path(review).resolve()
            d, r = READ(decision), READ(review)
            require(d["author_id"] == self.author and d.get("reason"), "Wrong/missing author decision")
            chosen = [f for f in self.selected("freeze") if f["candidate"] == d["candidate"]]
            require(len(chosen) == 1, "Select an existing frozen family")
            expected = "revise" if chosen[0]["stage"] == "revision" else "retain"
            require(d["action"] == expected, "Decision action/candidate mismatch")
            expected_feedback = {f["run_id"]: f["feedback"]["sha256"] for f in self.selected("feedback")}
            require(d["feedback_hashes"] == expected_feedback, "Decision must bind every actual feedback report")
            self._review_flags(r)
            require(r["candidate_freeze_sha256"] == chosen[0]["freeze_sha256"] and r["decision_sha256"] == SHA(decision),
                    "Review must bind selected freeze and decision")
            return self.add("decision", candidate=d["candidate"], action=d["action"], decision=bound(decision), review=bound(review))

    def deliver(self):
        with self.lock():
            require(not self.selected("closed"), "Author terminally closed")
            decisions = self.selected("decision")
            require(len(decisions) == 1, "Decision required before final draws")
            self._resolved_trials(require_feedback=True)
            used = {a["seed"] for a in self.selected("attempt") if a["purpose"] == "final"}
            for seed in self.p["final_seeds"]:
                if seed not in used:
                    self._run(decisions[0]["candidate"], "final", "final", seed)
            return self.add("closed", status="final_slots_consumed", reason="All three final slots consumed")

    def abandon(self, reason):
        with self.lock():
            require(not self.selected("closed") and isinstance(reason, str) and reason.strip(), "Terminal closure needs a reason")
            # A crash reservation is recorded as terminally unresolved, never retried.
            for a in self.selected("attempt"):
                if not any(r["attempt_index"] == a["index"] for r in self.selected("result")):
                    self.add("result", attempt_index=a["index"], run_id=a["run_id"], status="interrupted_unresolved",
                             receipt=None, table=None, error={"message": reason})
            return self.add("closed", status="construction_failed", reason=reason)

    def status(self):
        self.verify()
        return {"author_id": self.author, "case_id": self.spec["case_id"],
                "attempts": len(self.selected("attempt")), "trials": sum(a["purpose"] == "trial" for a in self.selected("attempt")),
                "finals": sum(a["purpose"] == "final" for a in self.selected("attempt")),
                "decision": bool(self.selected("decision")), "closed": bool(self.selected("closed"))}


def generated_statistics(session, run_id):
    """Provider entrypoint deliberately bypasses obsolete E0/E1 profile checks."""
    profile = READ(session.spec["profile"])
    require(profile["case_id"] == session.spec["case_id"] and profile["information_condition"] == "open_evidence", "Wrong case profile")
    require(not any(k in profile for k in ("reference", "reference_summary", "target_results")), "Reference profile forbidden")
    receipt = execution.verify_execution(session.bundle, run_id)
    require(receipt["status"] == "success", "Generated statistics need success")
    task = READ(session.bundle / "task.json")
    frame = lifecycle.read_table(session.bundle / "executions" / run_id / "output/generated.csv", task, output=True)
    spec = importlib.util.spec_from_file_location("core_provider_" + session.author, session.spec["provider"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.generated_statistics(frame)
    require(set(result) <= {"analyses", "diagnostics", "quality", "n"}, "Provider returned undeclared fields")
    require(len(result["analyses"]) == len(profile["analysis_ids"]) and
            {r["id"] for r in result["analyses"]} == set(profile["analysis_ids"]), "Analysis coverage mismatch")
    for category in ("analyses", "diagnostics"):
        require(all(set(r) <= {"id", "value", "unit", "status", "n", "rank", "reason"} for r in result[category]),
                "Reference fields forbidden in generated statistics")
    return result


def freeze(author, candidate, *, parent=None, revision=None, review=None, external_author_id=None):
    folder = ROOT / "sessions" / author
    s = Session(author) if folder.exists() else initialize(author, external_author_id)
    return s.freeze(candidate, parent, revision, review)


def abandon(author, reason, *, external_author_id=None):
    folder = ROOT / "sessions" / author
    s = Session(author) if folder.exists() else initialize(author, external_author_id)
    return s.abandon(reason)


def batch_state():
    p = ensure_control()
    result = {}
    total = 0
    for author in p["authors"]:
        s = Session(author)
        require(not (s.folder / "operation.lock").exists(), "Author operation still open")
        s.verify()
        require(len(s.selected("closed")) == 1 and s.events()[-1]["kind"] == "closed", "All four authors must terminally close")
        total += len(s.selected("attempt"))
        result[author] = {"status": s.status(), "files": {
            f.relative_to(s.folder).as_posix(): SHA(f) for f in sorted(s.folder.rglob("*")) if f.is_file()}}
    require(total <= p["max_physical_executions"], "Global physical attempt budget exceeded")
    return {"kind": "core_workflow_batch_closure_v1", "protocol_sha256": SHA(ROOT / "PROTOCOL.json"),
            "control_sha256": SHA(ROOT / "CONTROL.json"), "physical_attempts": total,
            "scheduled_final_slots": 12, "authors": result, "reference_read": False}


def seal_batch():
    state = batch_state()
    WRITE(ROOT / "BATCH_CLOSURE.json", state)
    return state


def closure_gate(path=None):
    path = Path(path) if path else ROOT / "BATCH_CLOSURE.json"
    committed = READ(path)
    require(committed == batch_state(), "Closed author/input/output commitments changed")
    return committed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["freeze", "trial", "feedback", "decide", "deliver", "abandon", "status", "seal", "gate"])
    parser.add_argument("--author")
    parser.add_argument("--candidate")
    parser.add_argument("--parent")
    parser.add_argument("--revision", type=Path)
    parser.add_argument("--external-author-id")
    parser.add_argument("--stage", choices=["initial", "revision"], default="initial")
    parser.add_argument("--run-id")
    parser.add_argument("--decision", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--reason")
    args = parser.parse_args()
    if args.action == "seal":
        result = seal_batch()
    elif args.action == "gate":
        result = closure_gate()
    else:
        require(args.author is not None, "--author required")
        if args.action == "freeze":
            result = freeze(args.author, args.candidate, parent=args.parent,
                revision=READ(args.revision) if args.revision else None, review=args.review,
                external_author_id=args.external_author_id)
        elif args.action == "abandon":
            result = abandon(args.author, args.reason, external_author_id=args.external_author_id)
        else:
            s = Session(args.author)
            if args.action == "trial":
                result = s.trial(args.candidate, args.stage)
            elif args.action == "feedback":
                result = s.feedback(args.run_id)
            elif args.action == "decide":
                result = s.decide(args.decision, args.review)
            else:
                result = getattr(s, args.action)()
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()


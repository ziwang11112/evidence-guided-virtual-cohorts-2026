"""Small append-only adaptive session; scientific code runs only through WSL.

The coordinator dispatches the real author externally. This module records those
dispatches, freezes their files, budgets attempts, and returns bound feedback.
Hashes detect accidental/stale mutation; they are not host-adversary signatures.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HARNESS = Path(__file__).resolve().parents[3]
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))
from cohort_harness import execution, lifecycle, semantic_feedback_v1 as semantic
from cohort_harness.contracts import require, validate_task

BUDGET = {"scientific_authors": 1, "scientific_review_rounds": 2,
          "revision_cycles": 1, "initial_trial_executions": 2,
          "revision_trial_executions": 2, "total_table_attempts": 10,
          "trial_max_rows": 3000, "delivery_rows": 3000,
          "delivery_seeds": [3101, 3102, 3103]}


def write(path, data):
    execution._write(Path(path), data)


def now():
    return datetime.now(timezone.utc).isoformat()


def inside(root, value):
    path = Path(value)
    path = path if path.is_absolute() else root / path
    require(".." not in path.parts, "Path traversal rejected")
    for part in [path, *path.parents]:
        require(not lifecycle._link(part), "Links and junctions rejected")
    path = path.resolve()
    require(path.is_relative_to(root), "Mutation outside new session root rejected")
    return path


def initialize(root, bundle, profile, evaluator, *, author_id,
               diagnostic_ids=None, analysis_ids=None, dependencies=()):
    root = Path(root).absolute()
    for part in [root, *root.parents]:
        require(not lifecycle._link(part), "Links and junctions rejected")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    bundle = inside(root, bundle)
    require(not (root / "session").exists(), "Session already initialized")
    require(not any(root.rglob("freeze.json")) and not any(root.rglob("execution.json")),
            "New session cannot adopt old frozen candidates or execution receipts")
    task = lifecycle.read_json(bundle / "task.json")
    validate_task(task)
    require(task["mode"] == "whole_cohort" and task["n_rows"] == BUDGET["delivery_rows"],
            "Main bundle must be a 3000-row whole-cohort task")
    require(not (bundle / "observed.csv").exists(), "Raw individual input forbidden")
    profile_data = lifecycle.read_json(profile)
    if "budgets" in profile_data:
        expected = {"fresh_constructors": 1, "author_phases": 2, "initial_trials": 2,
                    "revision_trials": 2, "delivery_per_stage": 3,
                    "delivery_seeds": BUDGET["delivery_seeds"], "max_total_tables": 10,
                    "rows_per_table": 3000, "retrieval_queries": task["budget"]["source_queries"],
                    "retrieval_documents": task["budget"]["source_downloads"]}
        require(profile_data["budgets"] == expected, "Profile/session/task budget mismatch")
    diagnostic_ids = diagnostic_ids or profile_data.get("required_diagnostic_ids")
    analysis_ids = analysis_ids or profile_data.get("required_analysis_ids")
    require(bool(author_id) and bool(diagnostic_ids) and bool(analysis_ids), "Missing session identity/coverage")
    require(len(set(diagnostic_ids)) == len(diagnostic_ids) and
            len(set(analysis_ids)) == len(analysis_ids), "Duplicate coverage IDs")
    folder = root / "session"
    folder.mkdir()
    (folder / "events").mkdir()
    (folder / "snapshots").mkdir()
    (folder / "feedback").mkdir()
    # Include source code actually used, not merely a version label.
    files = [Path(profile).resolve(), Path(evaluator).resolve(), Path(__file__).resolve(),
             *sorted((HARNESS / "cohort_harness").glob("*.py")),
             *[Path(p).resolve() for p in dependencies],
             *[Path(profile_data[key]).resolve() for key in ("reference_summary", "analysis_definitions") if key in profile_data]]
    bindings = {}
    for index, source in enumerate(dict.fromkeys(files)):
        require(source.is_file(), "Snapshot source missing: " + str(source))
        target = folder / "snapshots" / f"{index:03d}_{source.name}"
        shutil.copyfile(source, target)
        bindings[str(source)] = {"sha256": lifecycle.sha256(source),
                                 "snapshot": str(target.relative_to(root).as_posix())}
    contract = {"schema_version": 1, "kind": "adaptive_generation_session",
                "created_utc": now(), "root": str(root), "bundle": str(bundle.relative_to(root).as_posix()),
                "task_id": task["task_id"], "task_sha256": lifecycle.sha256(bundle / "task.json"),
                "author_id": author_id, "profile": str(Path(profile).resolve()),
                "evaluator": str(Path(evaluator).resolve()), "feedback_engine": "semantic_feedback_v1",
                "diagnostic_ids": sorted(diagnostic_ids), "analysis_ids": sorted(analysis_ids),
                "retrieval_limits": {"query": task["budget"]["source_queries"], "document": task["budget"]["source_downloads"]},
                "budget": BUDGET, "bindings": bindings,
                "reference_role": "declared development input; consistency is not independent validation"}
    write(folder / "contract.json", contract)
    return Session(root).status()


class Session:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.folder = inside(self.root, "session")
        self.contract = lifecycle.read_json(self.folder / "contract.json")
        require(self.contract["root"] == str(self.root), "Session root changed")
        require(self.contract["budget"] == BUDGET, "Budget contract changed")
        self.bundle = inside(self.root, self.contract["bundle"])

    @contextmanager
    def lock(self):
        path = self.folder / "operation.lock"
        try:
            stream = path.open("x", encoding="utf-8")
        except FileExistsError as error:
            raise ValueError("Session busy; inspect a stale lock before resuming") from error
        try:
            stream.write(now())
            stream.close()
            self.verify_bindings()
            yield
        finally:
            stream.close()
            path.unlink()

    def events(self):
        events = []
        previous = lifecycle.sha256(self.folder / "contract.json")
        for index, path in enumerate(sorted((self.folder / "events").glob("*.json")), 1):
            require(path.name == f"{index:04d}.json", "Event ledger has a gap")
            event = lifecycle.read_json(path)
            require(event["index"] == index and event["previous_sha256"] == previous,
                    "Event ledger binding changed")
            events.append(event)
            previous = lifecycle.sha256(path)
        return events

    def add(self, kind, **data):
        events = self.events()
        previous = self.folder / "events" / f"{len(events):04d}.json" if events else self.folder / "contract.json"
        event = {"index": len(events) + 1, "created_utc": now(), "kind": kind,
                 "previous_sha256": lifecycle.sha256(previous), **data}
        write(self.folder / "events" / f"{len(events)+1:04d}.json", event)
        return event

    def verify_bindings(self):
        require(lifecycle.sha256(self.bundle / "task.json") == self.contract["task_sha256"], "Task changed")
        for source, binding in self.contract["bindings"].items():
            require(lifecycle.sha256(source) == binding["sha256"], "Frozen implementation/profile changed: " + source)
            require(lifecycle.sha256(inside(self.root, binding["snapshot"])) == binding["sha256"], "Snapshot changed")
        self.events()

    def selected(self, kind):
        return [e for e in self.events() if e["kind"] == kind]

    def status(self):
        self.verify_bindings()
        attempts = self.selected("attempt")
        return {"task_id": self.contract["task_id"], "budget": BUDGET,
                "attempts": len(attempts), "initial_trials": sum(e["phase"] == "initial" and e["purpose"] == "trial" for e in attempts),
                "revision_trials": sum(e["phase"] == "revision" and e["purpose"] == "trial" for e in attempts),
                "deliveries": sum(e["purpose"] == "delivery" for e in attempts),
                "author_dispatches": len(self.selected("author_dispatch")),
                "scientific_review_rounds": len(self.selected("feedback")),
                "revision_decisions": len(self.selected("decision")),
                "results": self.selected("result")}

    def dispatch(self, phase, external_task_id, note=""):
        with self.lock():
            require(phase in {"initial", "revision"}, "Unknown author phase")
            require(not any(e["phase"] == phase for e in self.selected("author_dispatch")), "Author phase already dispatched")
            require(external_task_id == self.contract["author_id"], "External dispatch must use the one declared author ID")
            if phase == "revision":
                require(any(e["stage"] == "initial" for e in self.selected("feedback")), "Actual initial feedback required before revision dispatch")
                require(any(e["stage"] == "initial" for e in self.selected("handback")), "Record actual feedback handback before revision dispatch")
            return self.add("author_dispatch", phase=phase, external_task_id=external_task_id,
                            author_id=self.contract["author_id"], note=note)

    def handback(self, stage, external_task_id):
        with self.lock():
            require(stage in {"initial", "final"}, "Unknown feedback stage")
            require(not any(e["stage"] == stage for e in self.selected("handback")), "Feedback already handed back")
            require(external_task_id == self.contract["author_id"], "Feedback handback must use the one declared author ID")
            report = self.verify_feedback(stage)
            event = next(e for e in self.selected("feedback") if e["stage"] == stage)
            return self.add("handback", stage=stage, external_task_id=external_task_id,
                            feedback_sha256=event["feedback_sha256"], note="Coordinator records actual delivery to external author")

    def retrieval(self, kind, artifact_or_query, outcome):
        with self.lock():
            require(kind in {"query", "document"}, "Unknown retrieval kind")
            require(sum(e["retrieval_kind"] == kind for e in self.selected("retrieval")) < self.contract["retrieval_limits"][kind], "Retrieval budget exhausted")
            return self.add("retrieval", retrieval_kind=kind, artifact_or_query=artifact_or_query, outcome=outcome)

    def probe(self):
        with self.lock():
            try:
                result = execution._runtime_manifest(execution.DEFAULT_RUNTIME)
                return self.add("runtime_probe", status="available", runtime=result)
            except Exception as error:
                self.add("runtime_probe", status="unavailable", error=str(error))
                raise

    def _bundle_candidate(self, bundle, candidate):
        bundle = self.bundle if bundle is None else inside(self.root, bundle)
        task = lifecycle.read_json(bundle / "task.json")
        validate_task(task)
        require(task["mode"] == "whole_cohort" and not (bundle / "observed.csv").exists(), "Only whole-cohort bundles without individual input")
        candidate = candidate if str(candidate).startswith("candidates/") else "candidates/" + execution._name(str(candidate))
        directory, relative = lifecycle._candidate(bundle, candidate)
        return bundle, directory, relative, task

    def freeze(self, candidate, *, stage="trial", bundle=None):
        with self.lock():
            require(stage in {"trial", "initial", "final"}, "Unknown freeze stage")
            bundle, directory, relative, task = self._bundle_candidate(bundle, candidate)
            require(task["n_rows"] <= BUDGET["trial_max_rows"], "Trial row budget exceeded")
            require(not (directory / "generated.csv").exists(), "This stochastic pilot requires a program; copies are not independent draws")
            if stage != "trial":
                require(bundle == self.bundle and not any(e.get("stage") == stage for e in self.selected("freeze")), "Delivery candidate already frozen or wrong bundle")
            semantic.preflight(bundle, relative)
            parent, revision = None, None
            if stage == "final":
                decisions = self.selected("decision")
                require(len(decisions) == 1, "Final freeze requires the author's one revision/retention decision")
                initial = next(e for e in self.selected("freeze") if e["stage"] == "initial")
                parent = initial["candidate"] + "/freeze.json"
                revision = decisions[0]["decision"]
            frozen = lifecycle.freeze_candidate(bundle, relative, parent, revision)
            return self.add("freeze", stage=stage, bundle=str(bundle.relative_to(self.root).as_posix()),
                            candidate=relative, freeze_sha256=lifecycle.sha256(directory / "freeze.json"),
                            revision_index=frozen["revision_index"])

    def _phase(self, phase):
        require(phase in {"initial", "revision"}, "Unknown phase")
        require(any(e["phase"] == phase for e in self.selected("author_dispatch")), "Actual author dispatch must be recorded first")
        if phase == "initial":
            require(not any(e["stage"] == "initial" for e in self.selected("feedback")), "Initial phase is closed")
        else:
            require(any(e["stage"] == "initial" for e in self.selected("feedback")), "Revision requires actual initial feedback")
            require(not any(e["stage"] == "final" for e in self.selected("feedback")), "Final phase is closed")

    def _run(self, bundle, candidate, seed, purpose, phase, stage=None, context="target"):
        self._phase(phase)
        bundle, directory, candidate, task = self._bundle_candidate(bundle, candidate)
        frozen = lifecycle.verify_candidate(bundle, candidate)
        require(frozen["route"] == "generator.py", "Only isolated program executions are authorized")
        require(any(e["candidate"] == candidate and e["bundle"] == str(bundle.relative_to(self.root).as_posix())
                    and e["freeze_sha256"] == lifecycle.sha256(directory / "freeze.json") for e in self.selected("freeze")), "Candidate was not frozen in this session")
        attempts = self.selected("attempt")
        require(len(attempts) < BUDGET["total_table_attempts"], "Total table-attempt budget exhausted")
        if purpose == "trial":
            require(sum(e["purpose"] == "trial" and e["phase"] == phase for e in attempts) < BUDGET[phase + "_trial_executions"], "Phase trial budget exhausted")
            require(task["n_rows"] <= BUDGET["trial_max_rows"], "Trial row budget exceeded")
            require(not any(e["purpose"] == "delivery" and e["phase"] == phase for e in attempts), "Trials must precede stage delivery")
        else:
            require(seed in BUDGET["delivery_seeds"] and task["n_rows"] == BUDGET["delivery_rows"], "Delivery seed/row contract mismatch")
            require(not any(e["stage"] == stage and e["seed"] == seed for e in attempts if e["purpose"] == "delivery"), "Delivery slot already attempted; no hidden retries")
        run_id = f"a{len(attempts)+1:02d}_{phase}_{seed}"
        event = self.add("attempt", purpose=purpose, phase=phase, stage=stage, seed=seed, context=context,
                         rows=task["n_rows"], bundle=str(bundle.relative_to(self.root).as_posix()), candidate=candidate,
                         freeze_sha256=lifecycle.sha256(directory / "freeze.json"), run_id=run_id)
        # Reservation is written BEFORE the isolated call: errors consume budget.
        try:
            result = execution.run_candidate(bundle, candidate, run_id, seed)
            receipt = bundle / "executions" / run_id / "execution.json"
            return self.add("result", attempt_index=event["index"], run_id=run_id,
                            status=result["status"], execution_sha256=lifecycle.sha256(receipt),
                            error=result.get("error"), elapsed_seconds=result.get("elapsed_seconds"))
        except Exception as error:
            self.add("result", attempt_index=event["index"], run_id=run_id,
                     status="adapter_error", error={"type": type(error).__name__, "message": str(error)},
                     execution_sha256=None)
            raise

    def trial(self, candidate, seed, *, phase="initial", bundle=None, context="target"):
        with self.lock():
            return self._run(bundle, candidate, seed, "trial", phase, context=context)

    def deliver(self, stage):
        with self.lock():
            require(stage in {"initial", "final"}, "Unknown delivery stage")
            selected = [e for e in self.selected("freeze") if e["stage"] == stage]
            require(len(selected) == 1, "Freeze stage candidate before delivery")
            used = {e["seed"] for e in self.selected("attempt") if e["purpose"] == "delivery" and e["stage"] == stage}
            remaining = [seed for seed in BUDGET["delivery_seeds"] if seed not in used]
            require(bool(remaining), "All delivery slots already attempted; no retries")
            results = []
            for seed in remaining:
                try:
                    result = self._run(None, selected[0]["candidate"], seed, "delivery",
                                       "initial" if stage == "initial" else "revision", stage)
                except Exception:
                    # An adapter exception is already retained and charged. Continue
                    # the remaining declared seeds, never repeat the failed one.
                    latest = self.selected("attempt")[-1]
                    matching = [e for e in self.selected("result") if e["attempt_index"] == latest["index"]]
                    if latest["seed"] != seed or not matching:
                        raise
                    result = matching[-1]
                results.append(result)
            return results

    def _feedback_run(self, attempt):
        results = [e for e in self.selected("result") if e["attempt_index"] == attempt["index"]]
        result = results[-1] if results else {"status": "interrupted_or_unresolved", "error": "Attempt reservation retained without completion record", "execution_sha256": None}
        if result["status"] == "success":
            return self._evaluate(attempt)
        if result["execution_sha256"] is not None:
            bundle = inside(self.root, attempt["bundle"])
            require(lifecycle.sha256(bundle / "executions" / attempt["run_id"] / "execution.json") == result["execution_sha256"], "Failed execution receipt changed")
        unavailable = lambda ids: [{"id": item, "status": "unavailable", "value": None,
                                   "reason": "Generation attempt did not complete successfully"} for item in ids]
        return {"run_id": attempt["run_id"], "seed": attempt["seed"], "candidate": attempt["candidate"],
                "status": result["status"], "error": result.get("error"),
                "execution_sha256": result["execution_sha256"], "freeze_sha256": attempt["freeze_sha256"],
                "semantic_feedback_v1": None,
                "reference_evaluation": {"diagnostics": unavailable(self.contract["diagnostic_ids"]),
                                         "analyses": unavailable(self.contract["analysis_ids"])}}

    def _evaluate(self, attempt):
        bundle = inside(self.root, attempt["bundle"])
        run_id, candidate = attempt["run_id"], attempt["candidate"]
        receipt = execution.verify_execution(bundle, run_id)
        require(receipt["status"] == "success", "Feedback requires a successful verified execution")
        require(receipt["candidate_freeze_sha256"] == attempt["freeze_sha256"], "Attempt freeze binding changed")
        result = next(e for e in self.selected("result") if e["attempt_index"] == attempt["index"])
        require(lifecycle.sha256(bundle / "executions" / run_id / "execution.json") == result["execution_sha256"], "Execution receipt changed since attempted run")
        feedback_id = "session_" + run_id
        path = bundle / semantic.FOLDER / feedback_id / "feedback.json"
        strict = (semantic.verify_feedback(bundle, feedback_id, candidate=candidate, run_id=run_id)
                  if path.exists() else semantic.collect_feedback(bundle, candidate, run_id, feedback_id))
        spec = importlib.util.spec_from_file_location("adaptive_reference_evaluator", self.contract["evaluator"])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        evaluation = module.evaluate(bundle, candidate, run_id, Path(self.contract["profile"]))
        for key, expected in (("diagnostics", "diagnostic_ids"), ("analyses", "analysis_ids")):
            values = evaluation[key]
            ids = list(values) if isinstance(values, dict) else [r["id"] for r in values]
            require(sorted(ids) == self.contract[expected], "Incomplete or duplicate " + key + " coverage")
        return {"run_id": run_id, "seed": attempt["seed"], "candidate": candidate, "status": "success",
                "execution_sha256": lifecycle.sha256(bundle / "executions" / run_id / "execution.json"),
                "generated_table_sha256": lifecycle.sha256(bundle / "executions" / run_id / "output/generated.csv"),
                "freeze_sha256": lifecycle.sha256(bundle / candidate / "freeze.json"),
                "semantic_feedback_sha256": lifecycle.sha256(path), "semantic_feedback_v1": strict,
                "reference_evaluation": evaluation}

    def feedback(self, stage):
        with self.lock():
            require(stage in {"initial", "final"}, "Unknown feedback stage")
            require(not any(e["stage"] == stage for e in self.selected("feedback")), "Review stage already consumed")
            attempts = [e for e in self.selected("attempt") if e["purpose"] == "delivery" and e["stage"] == stage]
            require(sorted(e["seed"] for e in attempts) == BUDGET["delivery_seeds"], "Feedback requires all three delivery attempts")
            report = {"schema_version": 1, "kind": "adaptive_aggregate_feedback", "stage": stage,
                      "task_id": self.contract["task_id"], "contract_sha256": lifecycle.sha256(self.folder / "contract.json"),
                      "reference_role": self.contract["reference_role"],
                      "uncertainty_policy": "Reference sampling uncertainty is retained per statistic; three generation draws are conditional variation, not independent validation.",
                      "runs": [self._feedback_run(a) for a in attempts], "created_utc": now()}
            path = self.folder / "feedback" / (stage + ".json")
            write(path, report)
            self.add("feedback", stage=stage, feedback_path=str(path.relative_to(self.root).as_posix()),
                     feedback_sha256=lifecycle.sha256(path))
            return report

    def trial_feedback(self, run_id):
        with self.lock():
            attempts = [e for e in self.selected("attempt") if e["run_id"] == run_id and e["purpose"] == "trial"]
            require(len(attempts) == 1, "Not a session trial")
            path = self.folder / "feedback" / (run_id + ".json")
            require(not path.exists(), "Trial feedback already retained")
            result = self._feedback_run(attempts[0])
            write(path, result)
            self.add("trial_feedback", run_id=run_id, feedback_path=str(path.relative_to(self.root).as_posix()), feedback_sha256=lifecycle.sha256(path))
            return result

    def decision(self, decision):
        with self.lock():
            require(any(e["phase"] == "revision" for e in self.selected("author_dispatch")), "Record revision dispatch before decision")
            require(not self.selected("decision"), "One revision/retention decision only")
            lifecycle._revision(decision)
            initial = next(e for e in self.selected("feedback") if e["stage"] == "initial")
            self.verify_feedback("initial")
            return self.add("decision", author_id=self.contract["author_id"], decision=decision,
                            based_on_feedback_sha256=initial["feedback_sha256"])

    def verify_feedback(self, stage):
        self.verify_bindings()
        event = next(e for e in self.selected("feedback") if e["stage"] == stage)
        path = inside(self.root, event["feedback_path"])
        require(lifecycle.sha256(path) == event["feedback_sha256"], "Aggregate feedback hash changed")
        report = lifecycle.read_json(path)
        require(report["contract_sha256"] == lifecycle.sha256(self.folder / "contract.json"), "Feedback contract changed")
        attempts = [e for e in self.selected("attempt") if e["purpose"] == "delivery" and e["stage"] == stage]
        require(report["runs"] == [self._feedback_run(e) for e in attempts], "Feedback no longer matches verified execution and recomputed statistics")
        return report

    def verify(self):
        self.verify_bindings()
        for event in self.selected("freeze"):
            bundle = inside(self.root, event["bundle"])
            lifecycle.verify_candidate(bundle, event["candidate"])
            require(lifecycle.sha256(bundle / event["candidate"] / "freeze.json") == event["freeze_sha256"], "Session freeze changed")
        for event in self.selected("feedback"):
            self.verify_feedback(event["stage"])
        attempts = {e["index"]: e for e in self.selected("attempt")}
        for event in self.selected("result"):
            if event["execution_sha256"] is not None:
                attempt = attempts[event["attempt_index"]]
                bundle = inside(self.root, attempt["bundle"])
                require(lifecycle.sha256(bundle / "executions" / attempt["run_id"] / "execution.json") == event["execution_sha256"], "Execution result hash changed")
                execution.verify_execution(bundle, attempt["run_id"])
        for event in self.selected("trial_feedback"):
            require(lifecycle.sha256(inside(self.root, event["feedback_path"])) == event["feedback_sha256"], "Trial feedback hash changed")
        return self.status()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "probe", "dispatch", "handback", "retrieval", "freeze", "trial", "deliver", "feedback", "trial-feedback", "decision", "verify", "status"])
    parser.add_argument("--root", required=True)
    parser.add_argument("--bundle")
    parser.add_argument("--profile")
    parser.add_argument("--evaluator")
    parser.add_argument("--coverage", help="JSON with diagnostic_ids and analysis_ids")
    parser.add_argument("--dependency", action="append", default=[])
    parser.add_argument("--author-id")
    parser.add_argument("--external-task-id")
    parser.add_argument("--candidate")
    parser.add_argument("--stage", choices=["trial", "initial", "final"])
    parser.add_argument("--phase", choices=["initial", "revision"], default="initial")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--run-id")
    parser.add_argument("--context", default="target")
    parser.add_argument("--decision-json")
    parser.add_argument("--retrieval-kind", choices=["query", "document"])
    parser.add_argument("--artifact-or-query")
    parser.add_argument("--outcome")
    args = parser.parse_args(argv)
    try:
        if args.action == "init":
            coverage = lifecycle.read_json(args.coverage) if args.coverage else {}
            result = initialize(args.root, args.bundle, args.profile, args.evaluator, author_id=args.author_id,
                                diagnostic_ids=coverage.get("diagnostic_ids"), analysis_ids=coverage.get("analysis_ids"), dependencies=args.dependency)
        else:
            session = Session(args.root)
            if args.action in {"probe", "status", "verify"}:
                result = getattr(session, args.action)()
            elif args.action == "dispatch":
                result = session.dispatch(args.phase, args.external_task_id)
            elif args.action == "handback":
                result = session.handback(args.stage, args.external_task_id)
            elif args.action == "retrieval":
                result = session.retrieval(args.retrieval_kind, args.artifact_or_query, args.outcome)
            elif args.action == "freeze":
                result = session.freeze(args.candidate, stage=args.stage or "trial", bundle=args.bundle)
            elif args.action == "trial":
                result = session.trial(args.candidate, args.seed, phase=args.phase, bundle=args.bundle, context=args.context)
            elif args.action in {"deliver", "feedback"}:
                result = getattr(session, args.action)(args.stage)
            elif args.action == "trial-feedback":
                result = session.trial_feedback(args.run_id)
            else:
                result = session.decision(lifecycle.read_json(args.decision_json))
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except Exception as error:
        print(json.dumps({"status": "error", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

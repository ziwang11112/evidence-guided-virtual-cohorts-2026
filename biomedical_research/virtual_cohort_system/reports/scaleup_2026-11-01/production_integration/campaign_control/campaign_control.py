"""Finite Wave A control ledger; no fitting, generation, or target-table access.

Receipts are append-only procedural commitments, not signatures or a host sandbox.
The trusted runtime boundary re-verifies actual frozen bridge/case artifacts.
"""
from __future__ import annotations

from contextlib import contextmanager
import copy
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


class ControlError(ValueError):
    pass


CONSTRUCTORS = ("A01", "A02", "A03", "A04", "A05", "S01")
CASES = ("K01", "K02")
STAGES = ("initial", "final")
SOURCES = {
    "K01": (("source_mind_china_2019", 3101), ("source_ayele_dire_dawa_2017", 3102)),
    "K02": tuple(zip(("malawi_rural_men", "malawi_urban_men", "uganda_men",
                        "malawi_rural_women", "malawi_urban_women", "uganda_women"), range(3101, 3107))),
}
TARGETS = {"K01": "target_haalsi_pooled_poc", "K02": "target_turkana_adults"}
LIMITS = {"timeout_seconds": 60, "memory_mb": 1024, "output_bytes": 2000000, "log_bytes": 10000}
CASE_BINDINGS = ("scientific_commitment_sha256", "constructor_packet_sha256", "task_template_sha256", "budget_contract_sha256")
PARENT_FIELDS = ("candidate", "freeze_sha256", "task_sha256", "plan_sha256", "generator_sha256",
                 "model_spec_sha256", "common_spec_sha256", "evidence_sha256")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ControlError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash(value: Any) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _text(value: Any) -> bool:
    return type(value) is str and bool(value.strip())


def _same(left: Any, right: Any, message: str) -> None:
    _require(canonical(left) == canonical(right), message)


def stage_trials(case: str, constructor: str, stage: str) -> list[dict]:
    _require(case in CASES and constructor in CONSTRUCTORS and stage in STAGES, "Unknown case/constructor/stage")
    source = [{"id": f"{case}_{constructor}_{stage}_{context}", "context_id": context,
               "seed": seed, "n_rows": 5000} for context, seed in SOURCES[case]]
    target = [{"id": f"{case}_{constructor}_{stage}_target_{seed}", "context_id": TARGETS[case],
               "seed": seed, "n_rows": 5000} for seed in (2101, 2102, 2103)]
    return source + target


def fixed_schedule() -> dict:
    return {
        "schema_version": 1, "wave": "A", "cases": list(CASES), "constructors": list(CONSTRUCTORS),
        "stages": list(STAGES), "rows_per_trial": 5000, "execution_limits": LIMITS.copy(),
        "trials": {case: {constructor: {stage: stage_trials(case, constructor, stage) for stage in STAGES}
                          for constructor in CONSTRUCTORS} for case in CASES},
        "per_case_reserved": {"K01": {"source_slots": 24, "source_rows": 120000, "target_slots": 36, "target_rows": 180000},
                              "K02": {"source_slots": 72, "source_rows": 360000, "target_slots": 36, "target_rows": 180000}},
        "per_case_maximum_new": {"K01": {"source_slots": 22, "source_rows": 110000, "target_slots": 33, "target_rows": 165000},
                                 "K02": {"source_slots": 66, "source_rows": 330000, "target_slots": 33, "target_rows": 165000}},
        "s01_final_policy": "retain_or_stop_never_revise",
        "separate_analytic_jobs": "unavailable_no_reviewed_isolated_adapter",
        "derivation_modes": ["fixed_parameters", "inline_deterministic"],
        "feedback_packets_per_constructor": 1, "target_feedback_policy": "none",
        "reveal_requires_both_cases_all_twelve_constructors_closed": True,
    }


def release_digest(manifest: dict) -> str:
    return digest({key: value for key, value in manifest.items() if key != "review"})


def _required_runtime_paths() -> set[Path]:
    integration = Path(__file__).resolve().parent.parent
    return {Path(__file__).resolve(), integration/"case_execution.py", integration/"bundle_assembly.py",
            integration/"k01_sources"/"k01_sources.py", integration.parent/"bridge"/"context_bridge.py"}


def validate_release(manifest: dict) -> None:
    expected = {"schema_version", "kind", "campaign_id", "status", "released_utc", "ledger_directory", "designated_evaluator", "schedule_sha256", "cases", "artifacts", "review"}
    _require(type(manifest) is dict and set(manifest) == expected, "Global release fields differ")
    _require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1
             and manifest["kind"] == "wave_a_global_clinical_release" and manifest["status"] == "released",
             "An actual global clinical release manifest is required")
    _require(_text(manifest["campaign_id"]) and _text(manifest["released_utc"]), "Release identity/time required")
    ledger_directory = Path(manifest["ledger_directory"])
    _require(ledger_directory.is_absolute() and ledger_directory.resolve() == ledger_directory, "One resolved absolute ledger directory required")
    _require(manifest["schedule_sha256"] == digest(fixed_schedule()), "Frozen schedule commitment differs")
    _require(type(manifest["cases"]) is dict and set(manifest["cases"]) == set(CASES), "Both Wave A cases required")
    for binding in manifest["cases"].values():
        _require(type(binding) is dict and set(binding) == set(CASE_BINDINGS)
                 and all(_hash(binding[key]) for key in CASE_BINDINGS), "Exact case commitments required")
    artifacts = manifest["artifacts"]
    _require(type(artifacts) is list and bool(artifacts), "Reviewed code/design artifacts required")
    paths, hashes = set(), set()
    for item in artifacts:
        _require(type(item) is dict and set(item) == {"path", "sha256"} and _hash(item["sha256"]), "Invalid artifact binding")
        path = Path(item["path"])
        _require(path.is_absolute() and path.resolve() == path and path not in paths, "Unique resolved absolute artifact paths required")
        _require(path.suffix.lower() in {".py", ".json", ".md", ".txt"}
                 and not any(part.lower() in {"private_data", "private_documents", "private_sources"} for part in path.parts),
                 "Release verification accepts code/design metadata only, never private target files")
        _require(path.is_file() and _file_hash(path) == item["sha256"], "Released artifact bytes changed")
        paths.add(path); hashes.add(item["sha256"])
    _require(_required_runtime_paths() <= paths, "Required controller/runtime code commitment omitted")
    evaluator = manifest["designated_evaluator"]
    _require(type(evaluator) is dict and set(evaluator) == {"path","sha256"}
             and Path(evaluator["path"]).suffix.lower() == ".py" and evaluator in artifacts,
             "One designated release-bound Python evaluator required")
    _require(all(value in hashes for case in manifest["cases"].values() for value in case.values()),
             "Case commitments must be bound code/design artifacts")
    review = manifest["review"]
    review_fields = {"decision", "independent", "reviewer_id", "producer_id", "reviewed_utc", "reason", "approved_sha256"}
    _require(type(review) is dict and set(review) == review_fields and review["decision"] == "approved"
             and review["independent"] is True, "External independent release approval required")
    _require(all(_text(review[key]) for key in ("reviewer_id", "producer_id", "reviewed_utc", "reason"))
             and review["reviewer_id"].strip().casefold() != review["producer_id"].strip().casefold(), "Distinct release reviewer/producer required")
    _require(review["approved_sha256"] == release_digest(manifest), "Release approval commitment differs")


def _modules():
    """Load fixed reviewed application modules, never a submitted generator."""
    integration = Path(__file__).resolve().parent.parent
    scale = integration.parent
    project = scale.parent.parent
    for path in (project, integration, scale/"bridge", integration/"k01_sources"):
        if str(path) not in sys.path: sys.path.insert(0, str(path))
    bridge = importlib.import_module("context_bridge")
    case_execution = importlib.import_module("case_execution")
    sources = importlib.import_module("k01_sources")
    for module, path in ((bridge, scale/"bridge"/"context_bridge.py"),
                         (case_execution, integration/"case_execution.py"),
                         (sources, integration/"k01_sources"/"k01_sources.py")):
        _require(Path(module.__file__).resolve() == path.resolve(), "Runtime module path differs")
    return bridge, case_execution, sources


def _inspect(bundle: str, candidate: str) -> dict:
    bridge, _, _ = _modules()
    state = bridge.preflight(bundle, candidate)
    return {"bundle": str(state["root"].resolve()), "candidate": state["relative"],
            "parent": bridge._parent_binding(state), "plan": copy.deepcopy(state["plan"])}


def _verify_stage(bundle: str, candidate: str, case: str) -> dict:
    bridge, runner, _ = _modules()
    report = bridge.verify(bundle, candidate)
    guards = runner.verify_case_stage(bundle, candidate, case)
    inspected = _inspect(bundle, candidate)
    _same(guards["parent"], inspected["parent"], "Case guard parent differs")
    return {"parent": inspected["parent"], "bridge": report, "guards": guards}


def _source_reports(bundle: str, candidate: str, case: str, verified: dict) -> list[dict]:
    bridge, _, sources = _modules()
    state = bridge.preflight(bundle, candidate)
    destination = bridge._destination(state["root"], state["relative"])
    records = {record["trial_id"]: record for record in verified["bridge"]["trials"]}
    guard_records = {record["trial_id"]: record for record in verified["guards"]["trials"]}
    result = []
    for trial in state["plan"]["trials"]:
        if trial["context_id"] == TARGETS[case]: continue
        record, guard = records.get(trial["id"]), guard_records.get(trial["id"])
        entry = {"trial_id": trial["id"], "context_id": trial["context_id"], "role": "source",
                 "status": "unavailable", "reports": []}
        if record and guard and record["status"] == "success" and record["generation_link_verified"] and guard["guard_status"] == "valid":
            child = bridge._child_root(destination, trial["context_id"])
            # Use module constants rather than presuming a storage folder name.
            semantic_path = child/bridge.semantic.FOLDER/trial["id"]/"feedback.json"
            entry["reports"].append({"kind": "semantic_v1", "path": str(semantic_path), "sha256": _file_hash(semantic_path)})
            if case == "K01":
                report = sources.verify_descriptives(bundle, candidate, trial["id"])
                path = sources._report_path(state, trial["id"])/"feedback.json"
                _require(report["scope"] == "source_feedback_only", "Non-source descriptive report")
                entry["reports"].append({"kind": "k01_descriptives", "path": str(path), "sha256": _file_hash(path)})
            else:
                path = child/bridge.supplement.FOLDER/trial["id"]/"feedback.json"
                entry["reports"].append({"kind": "context_feedback_v1", "path": str(path), "sha256": _file_hash(path)})
            entry["status"] = "verified_source_feedback"
        else:
            entry["reason"] = "source_execution_or_guard_not_successful"
        result.append(entry)
    return result


def _validate_plan(plan: dict, case: str, constructor: str, stage: str) -> None:
    expected = stage_trials(case, constructor, stage)
    _same(sorted(plan["trials"], key=lambda x: x["id"]), sorted(expected, key=lambda x: x["id"]), "Bridge schedule differs from fixed campaign slots")
    _same(plan["execution_limits"], LIMITS, "Bridge execution limits differ")
    wanted = {context: "source" for context, _ in SOURCES[case]}; wanted[TARGETS[case]] = "target"
    contexts = plan["contexts"]
    _require(len(contexts) == len(wanted) and {c["id"] for c in contexts} == set(wanted), "Bridge context inventory differs")
    for context in contexts:
        _require(context["role"] == wanted[context["id"]], "Bridge context role differs")
        if context["role"] == "target":
            _require(context["feedback_policy"] == "none", "Target feedback is forbidden")
        else:
            _require(context["feedback_policy"] in {"semantic_v1", "semantic_v1_plus_supplement"}, "Source semantic feedback required")
    n = len(SOURCES[case])
    _same(plan["budget"], {"source_attempts": n, "source_rows": 5000*n, "target_attempts": 3, "target_rows": 15000}, "Bridge stage budget differs")


def _fresh_state() -> dict:
    return {"constructors": {f"{case}:{constructor}": {"construction": None, "stages": {}, "feedback": None,
             "decision": None, "closed": None} for case in CASES for constructor in CONSTRUCTORS},
            "wave_closed": None, "reveal": None}


def _apply(state: dict, event: dict) -> None:
    kind, payload = event["kind"], event["payload"]
    if kind == "wave_closed": state["wave_closed"] = payload; return
    if kind == "target_reveal": state["reveal"] = payload; return
    construction = state["constructors"][payload["key"]]
    if kind == "construction_started": construction["construction"] = payload
    elif kind == "stage_bound": construction["stages"][payload["stage"]] = {**payload, "intent": None, "result": None}
    elif kind == "stage_intent": construction["stages"][payload["stage"]]["intent"] = {**payload, "event_sha256": event["event_sha256"]}
    elif kind == "stage_finished": construction["stages"][payload["stage"]]["result"] = payload
    elif kind == "source_feedback_delivered": construction["feedback"] = payload
    elif kind == "final_decision": construction["decision"] = payload
    elif kind == "constructor_closed": construction["closed"] = payload
    else: raise ControlError("Unknown ledger event")


class CampaignLedger:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory).resolve()
        self.manifest = json.loads((self.directory/"release.json").read_text(encoding="utf-8"))
        _require(Path(self.manifest["ledger_directory"]) == self.directory, "Release is bound to a different ledger directory")
        self.release_sha256 = digest(self.manifest)
        self._read()

    @classmethod
    def create(cls, directory: str | Path, manifest: dict) -> "CampaignLedger":
        validate_release(manifest)
        path = Path(directory).resolve()
        _require(path == Path(manifest["ledger_directory"]), "Release permits exactly one ledger directory")
        path.mkdir(parents=True, exist_ok=False)
        (path/"events").mkdir()
        (path/"release.json").write_bytes(canonical(manifest))
        (path/".lock").write_bytes(b"0")
        return cls(path)

    @classmethod
    def open(cls, directory: str | Path) -> "CampaignLedger":
        return cls(directory)

    @contextmanager
    def _locked(self):
        with (self.directory/".lock").open("r+b") as handle:
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise ControlError("Ledger is busy; no action was reserved") from error
            try: yield
            finally:
                handle.seek(0)
                if os.name == "nt": msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _read(self) -> tuple[dict, list[dict]]:
        _require({p.name for p in self.directory.iterdir()} == {"release.json", "events", ".lock"}, "Unexpected ledger file")
        _same(json.loads((self.directory/"release.json").read_text(encoding="utf-8")), self.manifest, "Ledger release changed")
        validate_release(self.manifest)
        state, events, previous = _fresh_state(), [], self.release_sha256
        for index, path in enumerate(sorted((self.directory/"events").iterdir())):
            _require(path.name == f"{index:06d}.json" and path.is_file(), "Ledger sequence gap or unexpected file")
            event = json.loads(path.read_text(encoding="utf-8"))
            _require(set(event) == {"sequence", "previous_sha256", "utc", "kind", "payload", "event_sha256"}, "Event schema differs")
            _require(type(event["sequence"]) is int and event["sequence"] == index and event["previous_sha256"] == previous,
                     "Ledger chain differs")
            _require(event["event_sha256"] == digest({k:v for k,v in event.items() if k != "event_sha256"}), "Ledger event digest differs")
            _apply(state, event); events.append(event); previous = event["event_sha256"]
        return state, events

    def _append(self, kind: str, payload: dict, events: list[dict]) -> dict:
        event = {"sequence": len(events), "previous_sha256": events[-1]["event_sha256"] if events else self.release_sha256,
                 "utc": datetime.now(timezone.utc).isoformat(), "kind": kind, "payload": payload}
        event["event_sha256"] = digest(event)
        with (self.directory/"events"/f"{len(events):06d}.json").open("xb") as output:
            output.write(canonical(event)); output.flush(); os.fsync(output.fileno())
        return copy.deepcopy(event)

    def _construction(self, state: dict, case: str, constructor: str, *, work: bool = True) -> tuple[str, dict]:
        _require(case in CASES and constructor in CONSTRUCTORS, "Unknown reserved constructor")
        key = f"{case}:{constructor}"
        if work:
            _require(state["wave_closed"] is None and state["reveal"] is None and state["constructors"][key]["closed"] is None,
                     "Scientific inventory is closed")
        return key, state["constructors"][key]

    def begin_construction(self, case: str, constructor: str, construction_id: str) -> dict:
        with self._locked():
            state, events = self._read(); key, record = self._construction(state, case, constructor)
            _require(record["construction"] is None and _text(construction_id), "Construction already started or ID missing")
            _require(all(c["construction"] is None or c["construction"]["construction_id"] != construction_id
                         for c in state["constructors"].values()), "Scientific construction ID reused")
            return self._append("construction_started", {"key": key, "construction_id": construction_id,
                "arm": "statistical_reference" if constructor == "S01" else "agent", "case_bindings": self.manifest["cases"][case]}, events)

    def bind_stage(self, case: str, constructor: str, stage: str, bundle: str | Path, candidate: str,
                   *, derivation_mode: str = "fixed_parameters") -> dict:
        with self._locked():
            state, events = self._read(); key, record = self._construction(state, case, constructor)
            _require(record["construction"] is not None and stage in STAGES and stage not in record["stages"], "Stage unavailable or already bound")
            _require(derivation_mode in {"fixed_parameters", "inline_deterministic"}, "Separate analytic jobs are UNAVAILABLE without reviewed isolated adapter")
            if stage == "initial": _require(record["decision"] is None, "Initial construction already closed")
            else: _require(constructor != "S01" and record["decision"] is not None and record["decision"]["decision"] == "revise", "Changed final not authorized")
            inspected = _inspect(str(Path(bundle).resolve()), candidate)
            _validate_plan(inspected["plan"], case, constructor, stage)
            parent = inspected["parent"]
            _require(set(parent) == set(PARENT_FIELDS) and all(_hash(parent[k]) for k in PARENT_FIELDS if k != "candidate"), "Invalid actual parent commitment")
            if stage == "final":
                initial = record["stages"]["initial"]["parent"]
                _require(parent["task_sha256"] == initial["task_sha256"] and parent["evidence_sha256"] == initial["evidence_sha256"], "Revision changed shared task/evidence bytes")
                _require((parent["generator_sha256"], parent["model_spec_sha256"]) !=
                         (initial["generator_sha256"], initial["model_spec_sha256"]), "Unchanged scientific bytes must retain, not resample")
            for other in state["constructors"].values():
                for old in other["stages"].values():
                    _require((inspected["bundle"], inspected["candidate"]) != (old["bundle"], old["candidate"]), "Candidate path already reserved in another stage")
            return self._append("stage_bound", {"key": key, "stage": stage, **inspected, "derivation_mode": derivation_mode}, events)

    def begin_bridge(self, case: str, constructor: str, stage: str) -> dict:
        with self._locked():
            state, events = self._read(); key, record = self._construction(state, case, constructor)
            entry = record["stages"].get(stage)
            _require(entry is not None and entry["intent"] is None and entry["result"] is None, "Stage unavailable or already consumed")
            _require(record["decision"] is None if stage == "initial" else
                     record["decision"] is not None and record["decision"]["decision"] == "revise",
                     "Stage execution is closed by the final decision")
            _same(_inspect(entry["bundle"], entry["candidate"]), {k:entry[k] for k in ("bundle","candidate","parent","plan")}, "Frozen stage changed")
            return self._append("stage_intent", {"key": key, "stage": stage, "parent": entry["parent"],
                "source_slots_debited": len(SOURCES[case]), "target_slots_debited": 3,
                "scheduled_rows_debited": (len(SOURCES[case])+3)*5000,
                "rule": "Whole stage allocation is nonretryable; actual dispatched/output counts are separate"}, events)

    def verify_dispatch(self, case: str, constructor: str, stage: str, bundle: str | Path, candidate: str) -> dict:
        state, _ = self._read(); _, record = self._construction(state, case, constructor)
        entry = record["stages"].get(stage)
        _require(entry is not None and entry["intent"] is not None and entry["result"] is None, "Durable open stage intent required")
        inspected = _inspect(str(Path(bundle).resolve()), candidate)
        _same(inspected, {k:entry[k] for k in ("bundle","candidate","parent","plan")}, "Dispatch differs from consumed stage binding")
        return self._authorization(case, constructor, stage, entry)

    def _authorization(self, case: str, constructor: str, stage: str, entry: dict) -> dict:
        authorization = {"release_sha256": self.release_sha256, "stage_intent_sha256": entry["intent"]["event_sha256"],
                         "case": case, "constructor": constructor, "stage": stage,
                         "parent_binding": entry["parent"], "planned_trials": stage_trials(case, constructor, stage)}
        return {**authorization, "authorization_sha256": digest(authorization)}

    def finish_bridge(self, case: str, constructor: str, stage: str) -> dict:
        with self._locked():
            state, events = self._read(); key, record = self._construction(state, case, constructor)
            entry = record["stages"].get(stage)
            _require(entry is not None and entry["intent"] is not None and entry["result"] is None, "No unfinished consumed stage")
            try:
                _same(_inspect(entry["bundle"], entry["candidate"]), {k:entry[k] for k in ("bundle","candidate","parent","plan")}, "Frozen stage changed")
                verified = _verify_stage(entry["bundle"], entry["candidate"], case)
                _same(verified["parent"], entry["parent"], "Verified parent differs")
                _same(verified["guards"]["authorization"], self._authorization(case,constructor,stage,entry),
                      "Guard receipt is not bound to this ledger stage intent")
                _same([verified["guards"][name] for name in ("case_id","constructor","stage")],
                      [case,constructor,stage], "Guard stage identity differs")
                planned = {t["id"] for t in stage_trials(case, constructor, stage)}
                _require({r["trial_id"] for r in verified["bridge"]["trials"]} <= planned, "Unexpected verified trial")
                success = verified["bridge"]["completion_committed"] and verified["bridge"]["all_planned_trials_successful"] and verified["guards"]["all_guards_valid"] and verified["guards"]["all_slots_successful"]
                payload = {"key": key, "stage": stage, "status": "success" if success else "failed_or_interrupted",
                           "verified": verified, "verification_sha256": digest(verified), "error_type": None}
            except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
                payload = {"key": key, "stage": stage, "status": "verification_failed", "verified": None,
                           "verification_sha256": None, "error_type": type(error).__name__}
            return self._append("stage_finished", payload, events)

    def deliver_source_feedback(self, case: str, constructor: str) -> dict:
        with self._locked():
            state, events = self._read(); key, record = self._construction(state, case, constructor)
            initial = record["stages"].get("initial")
            _require(initial is not None and initial["result"] is not None and record["feedback"] is None and record["decision"] is None,
                     "Exactly one initial feedback delivery after stage completion")
            if initial["result"]["verified"] is None:
                reports = [{"trial_id": t["id"], "context_id": t["context_id"], "role": "source", "status": "unavailable",
                            "reason": "stage_verification_failed", "reports": []} for t in stage_trials(case, constructor, "initial") if t["context_id"] != TARGETS[case]]
            else:
                verified = _verify_stage(initial["bundle"], initial["candidate"], case)
                _same(verified, initial["result"]["verified"], "Verified stage artifacts changed before feedback")
                reports = _source_reports(initial["bundle"], initial["candidate"], case, verified)
            wanted = {(t["id"],t["context_id"]) for t in stage_trials(case,constructor,"initial") if t["context_id"] != TARGETS[case]}
            _require(len(reports) == len(wanted) and {(r["trial_id"],r["context_id"]) for r in reports} == wanted
                     and all(r["role"] == "source" for r in reports), "Feedback is not exact source-only inventory")
            packet = {"key": key, "source_only": True, "target_feedback": False, "reports": reports}
            packet["packet_sha256"] = digest(packet)
            self._append("source_feedback_delivered", packet, events)
            return copy.deepcopy(packet)

    def decide_final(self, case: str, constructor: str, decision: str, reason: str) -> dict:
        with self._locked():
            state, events = self._read(); key, record = self._construction(state, case, constructor)
            _require(record["construction"] is not None and record["decision"] is None and decision in {"retain","revise","stop"} and _text(reason), "One final decision required")
            _require(all(s["intent"] is None or s["result"] is not None for s in record["stages"].values()), "Finish consumed stage before deciding")
            if decision != "stop":
                _require(record["feedback"] is not None, "Source feedback opportunity must precede retain/revise")
            if decision == "retain":
                initial = record["stages"].get("initial")
                _require(initial is not None and initial["result"] is not None and initial["result"]["status"] == "success",
                         "Retention requires whole-stage verified success")
            if constructor == "S01":
                initial = record["stages"].get("initial")
                valid = initial is not None and initial["result"] is not None and initial["result"]["status"] == "success"
                _require(decision == ("retain" if valid else "stop"), "S01 must retain valid initial or stop; never revise")
            return self._append("final_decision", {"key": key, "decision": decision, "reason": reason}, events)

    def close_constructor(self, case: str, constructor: str, reason: str) -> dict:
        with self._locked():
            state, events = self._read(); key, record = self._construction(state, case, constructor)
            _require(record["decision"] is not None and _text(reason), "Final decision and closure reason required")
            _require(all(s["intent"] is None or s["result"] is not None for s in record["stages"].values()), "Finish or record interrupted stage before closure")
            inventory = self._final_inventory(case, constructor, record)
            return self._append("constructor_closed", {"key": key, "reason": reason, "decision": record["decision"]["decision"],
                "final_inventory": inventory, "final_inventory_sha256": digest(inventory)}, events)

    def _final_inventory(self, case: str, constructor: str, record: dict) -> list[dict]:
        decision = record["decision"]["decision"]
        source_stage = "initial" if decision == "retain" else "final"
        entry = record["stages"].get(source_stage)
        result = None if entry is None else entry["result"]
        verified = None if result is None else result["verified"]
        observed = {} if verified is None else {r["trial_id"]:r for r in verified["bridge"]["trials"]}
        original = stage_trials(case,constructor,source_stage)
        inventory = []
        for final, old in zip(stage_trials(case,constructor,"final"), original, strict=True):
            actual = observed.get(old["id"])
            inventory.append({"trial": final, "role": "target" if final["context_id"] == TARGETS[case] else "source",
                "disposition": "retained_alias" if decision == "retain" else "changed_final" if entry else "not_run",
                "alias_of": old["id"] if decision == "retain" else None,
                "parent": None if entry is None else entry["parent"],
                "verified_trial": copy.deepcopy(actual),
                "stage_status": "not_run" if result is None else result["status"],
                "scientific_pass": "not_assessed"})
        return inventory

    def close_wave_a(self) -> dict:
        with self._locked():
            state, events = self._read()
            _require(state["wave_closed"] is None and all(c["closed"] is not None for c in state["constructors"].values()),
                     "All twelve constructors across BOTH Wave A cases must close")
            inventory = {key: value["closed"] for key,value in state["constructors"].items()}
            return self._append("wave_closed", {"cases": list(CASES), "closed_inventory": inventory,
                "closed_inventory_sha256": digest(inventory), "final_target_slots": len(CASES)*len(CONSTRUCTORS)*3,
                "reserved_initial_and_final_target_slots": sum(x["target_slots"] for x in fixed_schedule()["per_case_reserved"].values()),
                "failures_and_unrun_slots_retained": True}, events)

    def authorize_target_reveal(self, evaluator_code_sha256: str) -> dict:
        with self._locked():
            state, events = self._read()
            _require(state["wave_closed"] is not None and state["reveal"] is None, "Closed BOTH-case inventory required; reveal is single-use")
            _require(evaluator_code_sha256 == self.manifest["designated_evaluator"]["sha256"], "Only the designated release-bound evaluator may reveal targets")
            payload = {"release_sha256": self.release_sha256, "closed_inventory_sha256": state["wave_closed"]["closed_inventory_sha256"],
                       "evaluator_code_sha256": evaluator_code_sha256, "cases": list(CASES), "target_data_read_by_controller": False}
            event = self._append("target_reveal", payload, events)
            return {**payload, "reveal_receipt_sha256": event["event_sha256"]}

    def reserve_analytic_job(self, *args, **kwargs):
        raise ControlError("Separate analytic jobs are UNAVAILABLE until a reviewed isolated adapter exists")

    def snapshot(self) -> dict:
        state, events = self._read()
        debits = {case: {"source_slots":0,"target_slots":0,"source_rows":0,"target_rows":0} for case in CASES}
        actual = {case: {"verified_attempt_records":0,"verified_generated_tables":0,"verification_failed_stages":0} for case in CASES}
        for key, construction in state["constructors"].items():
            case = key.split(":")[0]
            for stage in construction["stages"].values():
                if stage["intent"]:
                    for role in ("source","target"):
                        n = stage["intent"][role+"_slots_debited"]
                        debits[case][role+"_slots"] += n; debits[case][role+"_rows"] += 5000*n
                result = stage["result"]
                if result and result["verified"]:
                    trials = result["verified"]["bridge"]["trials"]
                    actual[case]["verified_attempt_records"] += len(trials)
                    actual[case]["verified_generated_tables"] += sum(bool(t["generation_link_verified"]) for t in trials)
                elif result: actual[case]["verification_failed_stages"] += 1
        return {"release_sha256":self.release_sha256,"ledger_head_sha256":events[-1]["event_sha256"] if events else self.release_sha256,
                "stage_allocation_debits":debits,"actual_observed_counts":actual,"separate_analytic_jobs":0,
                "state":copy.deepcopy(state),"security_scope":"Procedural local ledger; not signatures, host sandbox or clinical validation"}


def verify_dispatch(ledger_path, case, constructor, stage, bundle, candidate) -> dict:
    return CampaignLedger.open(ledger_path).verify_dispatch(case,constructor,stage,bundle,candidate)

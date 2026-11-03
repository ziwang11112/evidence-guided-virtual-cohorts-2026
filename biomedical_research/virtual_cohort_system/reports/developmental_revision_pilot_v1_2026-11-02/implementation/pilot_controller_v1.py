"""Bounded developmental pilot ledger; no author scheduler or reference access.

Existing source bridges remain source-only. Targets execute the frozen parent
outside each bridge inventory. Hashes are procedural commitments, not signatures.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import copy
import hashlib
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
PROJECT = Path(__file__).resolve().parents[3]
REVISION_DIRECTORY = PROJECT / "work/evidence_revision_v1_2026-11-02/implementation"
RUNTIME_DIRECTORY = PROJECT / "work/scaleup_2026-11-01/production_release/runtime"
for directory in (PROJECT, REVISION_DIRECTORY, RUNTIME_DIRECTORY):
    sys.path.insert(0, str(directory))
import revision_controller_v1 as source
import runtime_check
import support_selection_v1 as support_engine

bridge, execution, lifecycle = source.bridge, source.execution, source.lifecycle
require, exact_keys, read_json, sha256 = source.require, source.exact_keys, source.read_json, source.sha256
CONSTRUCTORS = ("A01", "A02")
VERSIONS = ("initial", "self_review", "source_feedback")
BRANCHES = VERSIONS[1:]
BASELINE_FILES = {"generator.py", "model_spec.json", "evidence.json", "decision.md",
                  "analysis_evidence.json", "evidence_use_v1.json", "scientific_validity_v1.json",
                  "context_bridge_v1.json", "qualified_plan_v1.json", "support_selection_v1.json"}
RELEASE_KEYS = {"schema_version", "kind", "ledger_directory", "protocol", "artifacts",
                "engine_sha256", "runtime_identity", "source_contexts", "target_context",
                "source_seeds", "target_seeds", "n_rows", "execution_limits", "author_allowance",
                "evaluator", "evaluation", "review", "support_contract", "required_qualified_checks", "initial_packet"}
PRIVATE_REFERENCE_KEYS = {"reference_report", "independent_reference_report"}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def engine_hashes():
    return {"pilot_controller_v1.py": sha256(__file__), "runtime_check.py": sha256(runtime_check.__file__),
            "support_selection_v1.py": sha256(support_engine.__file__),
            **{"revision/" + k: v for k, v in source._engines().items()},
            **{"bridge/" + k: v for k, v in bridge._engines().items()}}


def release_digest(release):
    return digest({k: v for k, v in release.items() if k != "review"})


def _binding(binding, *, read=True):
    exact_keys(binding, {"path", "sha256"}, where="file binding")
    path = Path(binding["path"])
    require(path.is_absolute() and path.resolve() == path and ".." not in path.parts,
            "Binding needs a resolved absolute path")
    require(isinstance(binding["sha256"], str) and len(binding["sha256"]) == 64 and
            all(c in "0123456789abcdef" for c in binding["sha256"]), "Invalid SHA256")
    if read:
        require(path.is_file() and not path.is_symlink(), "Bound regular file missing")
        require(sha256(path) == binding["sha256"], "Bound file changed: " + str(path))
    return path


def _review(value, approved_sha256):
    bridge.supplement._review(value, approved_sha256)


def _initial_packet(release):
    manifest = read_json(_binding(release["initial_packet"]))
    exact_keys(manifest, {"schema_version", "kind", "task", "evidence", "registry", "files"}, where="initial packet")
    require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1 and
            manifest["kind"] == "pilot_initial_author_packet", "Initial packet schema differs")
    for key in ("task", "evidence", "registry"):
        _binding(manifest[key])
    require(isinstance(manifest["files"], list) and manifest["files"], "Initial packet input bindings required")
    for binding in manifest["files"]:
        path = _binding(binding)
        require(path.suffix.casefold() in {".json", ".md", ".txt", ".py"}, "Initial packet admits metadata/code only")
    require(len({b["path"] for b in manifest["files"]}) == len(manifest["files"]), "Duplicate initial packet input")
    require(all(manifest[key] in manifest["files"] for key in ("task", "evidence", "registry")), "Initial task/evidence/registry omitted")
    return manifest


def support_assessment(bundle, candidate, release):
    """Recompute declaration assessment and bind the reviewed executable inputs."""
    state = bridge.preflight(bundle, candidate)
    contract_path = _binding(release["support_contract"])
    contract = read_json(contract_path)
    exact_keys(contract, {"required_contexts", "required_checks", "definition_ids"}, where="support contract")
    expected = [*release["source_contexts"], release["target_context"]]
    require(set(contract["required_contexts"]) == set(expected), "Support contract contexts differ")
    declaration = state["directory"] / "support_selection_v1.json"
    evidence = read_json(state["directory"] / "evidence.json")
    assessment = support_engine.assess_support_selection(read_json(declaration),
        required_contexts=expected, required_checks=contract["required_checks"], known_provenance={
            "evidence": [i["id"] for i in evidence["items"]],
            "assumption": [a["id"] for a in state["spec"]["assumptions"]],
            "definition": contract["definition_ids"]})
    return {"schema_version": 1, "kind": "pilot_support_assessment", "parent": bridge._parent_binding(state),
            "declaration_sha256": sha256(declaration), "support_contract_sha256": sha256(contract_path),
            "support_engine_sha256": sha256(support_engine.__file__), "assessment": assessment}


def planned_slots(release):
    slots = []
    for constructor in CONSTRUCTORS:
        for version in VERSIONS:
            for role, contexts, seeds in (("source", release["source_contexts"], release["source_seeds"]),
                                          ("target", [release["target_context"]], release["target_seeds"])):
                for context_id in contexts:
                    for seed in seeds:
                        run_id = execution._name(f"{constructor}_{version}_{context_id}_{seed}")
                        slots.append({"constructor": constructor, "version": version, "role": role,
                                      "context_id": context_id, "run_id": run_id, "seed": seed,
                                      "n_rows": release["n_rows"], "bundle": None, "candidate": None,
                                      "status": "pending", "output_sha256": None,
                                      "execution_sha256": None, "error": None})
    require(len({s["run_id"].casefold() for s in slots}) == 72, "Pilot slot collision")
    return slots


def validate_release(release):
    exact_keys(release, RELEASE_KEYS, where="pilot release")
    require(type(release["schema_version"]) is int and release["schema_version"] == 1 and
            release["kind"] == "developmental_revision_pilot_release", "Wrong pilot release")
    path = Path(release["ledger_directory"])
    require(path.is_absolute() and path.resolve() == path, "One resolved ledger path required")
    require(type(release["n_rows"]) is int and release["n_rows"] == 3000, "Pilot uses 3000 rows")
    contexts = release["source_contexts"]
    require(isinstance(contexts, list) and len(contexts) == 3, "Three source contexts required")
    identifiers = [execution._name(x) for x in [*contexts, release["target_context"]]]
    require(len({x.casefold() for x in identifiers}) == 4, "Context IDs must be distinct")
    for key in ("source_seeds", "target_seeds"):
        seeds = release[key]
        require(isinstance(seeds, list) and len(seeds) == 3 and len(set(seeds)) == 3 and
                all(type(x) is int and 0 <= x < 2**32 for x in seeds), "Three distinct uint32 seeds required")
    exact_keys(release["execution_limits"], {"timeout_seconds", "memory_mb", "output_bytes", "log_bytes"}, where="limits")
    execution._limits(**release["execution_limits"], seed=0)
    bridge._same(release["author_allowance"], {"candidate_bytes": 1048576, "generator_bytes": 65536, "schema_returns": 2},
                 "Pilot author artifact allowances differ")
    bridge._same(release["engine_sha256"], engine_hashes(), "Released engine bytes changed")
    _binding(release["protocol"])
    _binding(release["runtime_identity"])
    _binding(release["evaluator"])
    _binding(release["support_contract"])
    _initial_packet(release)
    required = release["required_qualified_checks"]
    require(isinstance(required, list) and len(required) == 4, "Four qualified relationships required")
    for check in required:
        exact_keys(check, {"context_id", "check_id"}, where="required qualified check")
        require(check["context_id"] in contexts, "Qualified check must belong to source context")
        source.text(check["check_id"], "qualified check ID")
    require(len({(c["context_id"], c["check_id"]) for c in required}) == 4 and
            {c["context_id"] for c in required} == set(contexts), "Required relationships must cover all source contexts")
    require(isinstance(release["artifacts"], list) and release["artifacts"], "Public release artifacts required")
    paths = [_binding(a) for a in release["artifacts"]]
    require(len(paths) == len(set(paths)), "Duplicate public artifact")
    require(isinstance(release["evaluation"], dict), "Frozen evaluation metadata required")
    for key, value in release["evaluation"].items():
        if isinstance(value, dict) and set(value) == {"path", "sha256"}:
            _binding(value, read=key not in PRIVATE_REFERENCE_KEYS)
    _review(release["review"], release_digest(release))
    planned_slots(release)


def _empty_state():
    return {"versions": {f"{a}/{v}": {} for a in CONSTRUCTORS for v in VERSIONS},
            "packets": {}, "decisions": {}, "scientific_freeze": None, "closed": None, "authorization": None}


def _apply(state, event):
    kind, payload = event["kind"], event["payload"]
    if kind in {"registered", "sources_intent", "sources_closed", "targets_intent", "targets_closed", "aborted"}:
        state["versions"][payload["key"]][kind] = payload
        if kind == "sources_closed":
            state["versions"][payload["key"]]["source_report_event"] = {"sequence": event["sequence"], "event_sha256": event["event_sha256"]}
    elif kind in {"packet_intent", "packet_delivered"}:
        state["packets"].setdefault(payload["key"], {})[kind] = payload
    elif kind == "decision":
        state["decisions"][payload["key"]] = payload
    elif kind in {"target_attempt", "target_error"}:
        state["versions"][payload["key"]].setdefault(kind, {})[payload["run_id"]] = payload
    elif kind in {"scientific_freeze", "closed", "authorization"}:
        state[kind] = {**payload, "event_sha256": event["event_sha256"]}
    else:
        raise ValueError("Unknown pilot event")


class PilotController:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.release = read_json(self.directory / "release.json")
        require(Path(self.release["ledger_directory"]) == self.directory, "Ledger directory mismatch")
        self.release_sha256 = digest(self.release)
        self._read()

    @classmethod
    def create(cls, directory, release):
        validate_release(release)
        path = Path(directory).resolve()
        require(path == Path(release["ledger_directory"]), "Release permits one ledger path")
        path.mkdir(parents=True, exist_ok=False)
        (path / "events").mkdir()
        (path / "packets").mkdir()
        execution._write(path / "release.json", release)
        (path / ".lock").write_bytes(b"0")
        (path / ".execution.lock").write_bytes(b"0")
        return cls(path)

    @classmethod
    def open(cls, directory):
        return cls(directory)

    @contextmanager
    def _locked(self):
        with self._file_lock(".lock"):
            yield

    @contextmanager
    def _execution_lock(self):
        # Recovery cannot close a live phase while dispatch is outside ledger lock.
        with self._file_lock(".execution.lock"):
            yield

    @contextmanager
    def _file_lock(self, filename):
        with (self.directory / filename).open("r+b") as handle:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                yield
            finally:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _read(self):
        names = {p.name for p in self.directory.iterdir()}
        require({"release.json", "events", "packets", ".lock", ".execution.lock"} <= names and
                names <= {"release.json", "events", "packets", ".lock", ".execution.lock", "evaluation", "independent_evaluation"},
                "Unexpected ledger artifact")
        bridge._same(read_json(self.directory / "release.json"), self.release, "Release changed")
        validate_release(self.release)
        state, events, previous = _empty_state(), [], self.release_sha256
        for index, path in enumerate(sorted((self.directory / "events").iterdir())):
            require(path.name == f"{index:06d}.json" and path.is_file() and not path.is_symlink(), "Ledger sequence gap")
            event = read_json(path)
            exact_keys(event, {"sequence", "previous_sha256", "utc", "kind", "payload", "event_sha256"}, where="event")
            require(type(event["sequence"]) is int and event["sequence"] == index and event["previous_sha256"] == previous,
                    "Ledger chain changed")
            require(event["event_sha256"] == digest({k: v for k, v in event.items() if k != "event_sha256"}), "Event changed")
            _apply(state, event)
            events.append(event)
            previous = event["event_sha256"]
        expected_packets = {key.replace("/", "_") for key in state["packets"]}
        require({p.name for p in (self.directory / "packets").iterdir()} <= expected_packets, "Unreserved branch packet")
        require(state["authorization"] is not None or not (names & {"evaluation", "independent_evaluation"}),
                "Evaluation artifacts appeared before authorization")
        return state, events

    def _append(self, kind, payload, events):
        event = {"sequence": len(events), "previous_sha256": events[-1]["event_sha256"] if events else self.release_sha256,
                 "utc": datetime.now(timezone.utc).isoformat(), "kind": kind, "payload": payload}
        event["event_sha256"] = digest(event)
        with (self.directory / "events" / f"{len(events):06d}.json").open("xb") as output:
            output.write(canonical(event)); output.flush(); os.fsync(output.fileno())
        return event

    def _key(self, constructor, version):
        require(constructor in CONSTRUCTORS and version in VERSIONS, "Unknown pilot slot")
        return f"{constructor}/{version}"

    def _open_science(self, state):
        require(state["scientific_freeze"] is None, "Scientific inventory is frozen")

    def _slots(self, constructor, version, role=None):
        return [s for s in planned_slots(self.release) if s["constructor"] == constructor and s["version"] == version
                and (role is None or s["role"] == role)]

    def _inspect(self, bundle, candidate, constructor, version):
        state = bridge.preflight(bundle, candidate)
        allowance = self.release["author_allowance"]
        require((state["directory"] / "generator.py").stat().st_size <= allowance["generator_bytes"] and
                sum((state["directory"] / f).stat().st_size for f in lifecycle._files(state["directory"])) <= allowance["candidate_bytes"],
                "Candidate output byte allowance exceeded")
        planned = [{"id": s["run_id"], "context_id": s["context_id"], "seed": s["seed"], "n_rows": s["n_rows"]}
                   for s in self._slots(constructor, version)]
        bridge._same(state["plan"]["trials"], planned, "Candidate schedule differs from pilot")
        bridge._same(state["plan"]["execution_limits"], self.release["execution_limits"], "Candidate limits differ")
        roles = {c["id"]: c["role"] for c in state["plan"]["contexts"]}
        bridge._same(roles, {**{c: "source" for c in self.release["source_contexts"]}, self.release["target_context"]: "target"},
                     "Candidate contexts differ")
        target = next(c for c in state["plan"]["contexts"] if c["role"] == "target")
        require(target["feedback_policy"] == "none", "Pilot target source-feedback policy must be none")
        phase = source.verify_source_phase(bundle, candidate)
        return state, phase

    def _support(self, support, bundle, candidate):
        exact_keys(support, {"assessment", "review"}, where="support binding")
        _binding(support["assessment"])
        actual = support_assessment(bundle, candidate, self.release)
        bridge._same(read_json(support["assessment"]["path"]), actual, "Support assessment is stale or unbound")
        require(actual["assessment"]["status"] == "declaration_checks_pass", "Support declarations failed")
        _review(support["review"], support["assessment"]["sha256"])

    def _registration(self, record, constructor, version):
        registered = record["registered"]
        state, phase = self._inspect(registered["bundle"], registered["candidate"], constructor, version)
        bridge._same(bridge._parent_binding(state), registered["parent"], "Registered candidate changed")
        self._support(registered["support"], registered["bundle"], registered["candidate"])
        _binding(registered["provenance"]["author_trace"])
        return state, phase

    def register_version(self, constructor, version, bundle, candidate, support, provenance):
        with self._locked():
            state, events = self._read(); self._open_science(state)
            key = self._key(constructor, version); record = state["versions"][key]
            require(not record, "Version already registered or disposed")
            inspected, phase = self._inspect(bundle, candidate, constructor, version)
            require(phase["status"] == "ready", "Registration requires an unattempted source phase")
            self._support(support, bundle, candidate)
            exact_keys(provenance, {"actor_id", "context_id", "packet_sha256", "author_turns", "scientific_opportunities",
                                   "model_calls", "output_tokens", "schema_returns", "author_trace", "common_correction"},
                       where="author provenance")
            for field in ("actor_id", "context_id"):
                source.text(provenance[field], field)
            require(provenance["model_calls"] is None and provenance["output_tokens"] is None,
                    "Unexposed model calls/tokens must remain unknown")
            require(type(provenance["schema_returns"]) is int and 0 <= provenance["schema_returns"] <= 2,
                    "Schema-only return allowance exceeded")
            opportunities = 1 + int(version == "initial" and provenance["common_correction"] is not None)
            require(type(provenance["scientific_opportunities"]) is int and provenance["scientific_opportunities"] == opportunities,
                    "Scientific opportunity count differs")
            require(type(provenance["author_turns"]) is int and provenance["author_turns"] >= opportunities,
                    "Observed author turns required")
            _binding(provenance["author_trace"])
            for other in state["versions"].values():
                if "registered" in other:
                    require(other["registered"]["provenance"]["context_id"] != provenance["context_id"], "Author context reused")
            frozen = inspected["frozen"]
            if version == "initial":
                require(provenance["packet_sha256"] == self.release["initial_packet"]["sha256"], "Wrong initial author packet")
                initial_packet = _initial_packet(self.release)
                for label, path in (("task", inspected["root"] / "task.json"),
                                    ("evidence", inspected["directory"] / "evidence.json"),
                                    ("registry", inspected["root"] / "registry.json")):
                    require(sha256(path) == initial_packet[label]["sha256"], "Initial " + label + " differs from approved packet")
                correction = provenance["common_correction"]
                if correction is None:
                    require(frozen["parent"] is None and frozen["revision_index"] == 0, "Undeclared initial correction")
                else:
                    exact_keys(correction, {"rejected_candidate", "reason"}, where="common correction")
                    source.text(correction["reason"], "correction reason")
                    require(frozen["revision_index"] == 1 and frozen["parent"] is not None and
                            frozen["parent"]["candidate"] == correction["rejected_candidate"], "Only one common correction allowed")
                    rejected_bridge = bridge._destination(inspected["root"], correction["rejected_candidate"])
                    require(not (rejected_bridge / "attempts").exists(), "Common correction must precede source execution")
                require(not (inspected["root"] / "executions").exists() or not any((inspected["root"] / "executions").iterdir()),
                        "Initial author bundle already contains target executions")
            else:
                decision = state["decisions"].get(key)
                require(decision is not None and decision["decision"]["action"] in {"retain", "revise"}, "Branch decision required")
                packet = self._verify_packet(state, key)
                require(provenance["packet_sha256"] == packet["packet_sha256"] and provenance["common_correction"] is None,
                        "Branch input/correction differs")
                initial = state["versions"][f"{constructor}/initial"]["registered"]
                require(str(inspected["root"]) == initial["bundle"] and frozen["parent"] is not None and
                        frozen["parent"]["candidate"] == initial["candidate"] and
                        frozen["parent"]["sha256"] == initial["parent"]["freeze_sha256"], "Branches must independently parent accepted initial")
                require(frozen["revision"]["kind"] == decision["decision"]["action"], "Retain/revise disagrees with scientific bytes")
                require(sha256(inspected["root"] / "task.json") == initial["parent"]["task_sha256"] and
                        sha256(inspected["directory"] / "evidence.json") == initial["parent"]["evidence_sha256"], "Branch task/evidence changed")
            identity = (str(inspected["root"]), inspected["relative"])
            require(all("registered" not in r or (r["registered"]["bundle"], r["registered"]["candidate"]) != identity
                        for r in state["versions"].values()), "Candidate reused in another version")
            payload = {"key": key, "bundle": identity[0], "candidate": identity[1], "parent": bridge._parent_binding(inspected),
                       "support": copy.deepcopy(support), "provenance": copy.deepcopy(provenance)}
            return self._append("registered", payload, events)

    def _runtime(self):
        return runtime_check.verify(_binding(self.release["runtime_identity"]))

    def _collect_sources(self, record, constructor, version):
        inspected, phase = self._registration(record, constructor, version)
        by_id = {t["trial_id"]: t for t in phase["trials"]}
        slots = self._slots(constructor, version, "source")
        destination = bridge._destination(inspected["root"], inspected["relative"])
        for slot in slots:
            child = bridge._child_root(destination, slot["context_id"])
            slot.update(bundle=str(child), candidate=bridge.CHILD)
            trial = by_id.get(slot["run_id"])
            if trial is None:
                slot.update(status="not_run", error={"type": "phase_aborted", "message": "Reserved source phase ended without this dispatch; no retry"})
                continue
            slot.update(status=trial["status"], output_sha256=trial.get("generated_table_sha256"),
                        execution_sha256=trial.get("execution_sha256"))
            output = child / "executions" / slot["run_id"] / "output/generated.csv"
            receipt = child / "executions" / slot["run_id"] / "execution.json"
            if output.is_file():
                slot["output_sha256"] = sha256(output)
            if receipt.is_file():
                slot["execution_sha256"] = sha256(receipt)
            outcome = destination / "attempts" / slot["run_id"] / "outcome.json"
            slot["error"] = read_json(outcome)["error"] if outcome.exists() else {"type": "interrupted", "message": "Attempt has no outcome"}
        packet = source.source_feedback_packet(inspected["root"], inspected["relative"])
        eligibility = self._source_eligibility(inspected, phase, slots, packet)
        return {"slots": slots, "phase": phase, "feedback_sha256": packet["packet_sha256"], "feedback": packet, "eligibility": eligibility,
                "bridge_artifacts": bridge._inventory(destination),
                "controller_artifacts": bridge._inventory(source._controller_root(inspected))}

    def _support_counts(self, inspected, bundle, run_id, context_id):
        contract = read_json(_binding(self.release["support_contract"]))
        declaration = read_json(inspected["directory"] / "support_selection_v1.json")
        task = read_json(Path(bundle) / "task.json")
        output = Path(bundle) / "executions" / run_id / "output/generated.csv"
        try:
            frame = lifecycle.read_table(output, task, output=True)
            result = support_engine.check_retained_frame(frame, context_id=context_id, declaration=declaration,
                                                         required_checks=contract["required_checks"])
        except (OSError, ValueError, TypeError, KeyError) as error:
            result = {"status": "unavailable", "row_count": None, "mutated_or_filtered": False,
                      "error": {"type": type(error).__name__, "message": str(error)[:2000]}}
        return {"run_id": run_id, "output_sha256": sha256(output), "report": result}

    def _source_eligibility(self, inspected, phase, slots, packet):
        reasons, support_reports, coverage = [], [], []
        if phase["status"] != "complete" or len(slots) != 9 or any(s["status"] != "success" for s in slots):
            reasons.append("All nine source executions and the source phase must complete successfully")
        reports = {r["trial_id"]: r for r in packet["packet"]["reports"]}
        for slot in slots:
            if slot["output_sha256"] is not None:
                counts = self._support_counts(inspected, slot["bundle"], slot["run_id"], slot["context_id"])
                support_reports.append(counts)
                if counts["report"]["status"] != "pass" or counts["report"]["row_count"] != slot["n_rows"]:
                    reasons.append("Retained source support/eligibility failed: " + slot["run_id"])
            qualified = (reports.get(slot["run_id"], {}).get("qualified_feedback") or {}).get("checks", [])
            for required in self.release["required_qualified_checks"]:
                if required["context_id"] != slot["context_id"]:
                    continue
                matches = [q for q in qualified if q["id"] == required["check_id"]]
                available = len(matches) == 1 and matches[0]["status"] == "available"
                coverage.append({"run_id": slot["run_id"], "check_id": required["check_id"], "available": available})
                if not available:
                    reasons.append("Required qualified comparison unavailable: " + slot["run_id"] + "/" + required["check_id"])
        return {"target_eligible": not reasons, "reasons": reasons, "qualified_coverage": coverage,
                "support_checks": support_reports, "source_point_fit_required": False}

    def dispatch_sources(self, constructor, version):
        with self._execution_lock():
            return self._dispatch_sources(constructor, version)

    def _dispatch_sources(self, constructor, version):
        with self._locked():
            state, events = self._read(); self._open_science(state)
            key = self._key(constructor, version); record = state["versions"][key]
            require("registered" in record and "sources_intent" not in record and "aborted" not in record, "Source allocation unavailable")
            _, phase = self._registration(record, constructor, version)
            require(phase["status"] == "ready", "Unexpected source execution before intent")
            self._runtime()
            self._append("sources_intent", {"key": key, "slots_debited": 9, "rows_debited": 27000,
                                           "parent": record["registered"]["parent"]}, events)
        registration = record["registered"]
        try:
            source.dispatch_sources(registration["bundle"], registration["candidate"])
        except Exception:
            # All source failures remain in existing source artifacts. Never retry.
            return self._finish_sources(constructor, version)
        return self._finish_sources(constructor, version)

    def finish_sources(self, constructor, version):
        with self._execution_lock():
            return self._finish_sources(constructor, version)

    def _finish_sources(self, constructor, version):
        with self._locked():
            state, events = self._read(); self._open_science(state)
            key = self._key(constructor, version); record = state["versions"][key]
            require("sources_intent" in record and "sources_closed" not in record, "No open source allocation")
            return self._append("sources_closed", {"key": key, **self._collect_sources(record, constructor, version)}, events)

    def _packet_files(self, registered):
        root, candidate = Path(registered["bundle"]), Path(registered["bundle"]) / registered["candidate"]
        frozen = lifecycle.verify_candidate(root, candidate)
        registry = read_json(root / "registry.json")
        files = {"task.json": (root / "task.json").read_bytes(),
                 "registry.json": bridge._bytes({"artifacts": registry["artifacts"][:frozen["registry_snapshot"]["artifact_count"]]}),
                 "requirements/protocol.md": _binding(self.release["protocol"]).read_bytes(),
                 "requirements/support_contract.json": _binding(self.release["support_contract"]).read_bytes()}
        for index, binding in enumerate(_initial_packet(self.release)["files"]):
            path = _binding(binding)
            files[f"original_inputs/{index:03d}_{path.name}"] = path.read_bytes()
        for name in frozen["commitments"]:
            if name.startswith("sources/"):
                files[name] = (root / name).read_bytes()
        for name in sorted(BASELINE_FILES):
            if (candidate / name).is_file():
                files["initial/" + name] = (candidate / name).read_bytes()
        return files

    def _numerical_packet(self, initial):
        registered = initial["registered"]
        feedback = source.source_feedback_packet(registered["bundle"], registered["candidate"])
        return {"source_feedback": feedback, "source_eligibility": initial["sources_closed"]["eligibility"]}

    def deliver_branch_packet(self, constructor, branch):
        with self._execution_lock():
            return self._deliver_branch_packet(constructor, branch)

    def _deliver_branch_packet(self, constructor, branch):
        require(branch in BRANCHES, "Only revision branches receive packets")
        with self._locked():
            state, events = self._read(); self._open_science(state)
            key = self._key(constructor, branch)
            require(not state["versions"][key] and key not in state["packets"], "Branch packet allocation consumed")
            initial = state["versions"][f"{constructor}/initial"]
            require("sources_closed" in initial and "aborted" not in initial, "Closed initial sources required")
            current = self._collect_sources(initial, constructor, "initial")
            bridge._same(current, {k: v for k, v in initial["sources_closed"].items() if k != "key"}, "Initial source results changed")
            self._append("packet_intent", {"key": key}, events)
        folder = self.directory / "packets" / key.replace("/", "_")
        folder.mkdir()
        files = self._packet_files(initial["registered"])
        for name, content in files.items():
            destination = folder / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
        numeric = branch == "source_feedback"
        feedback_sha256 = None
        if numeric:
            feedback = self._numerical_packet(initial)
            feedback_sha256 = feedback["source_feedback"]["packet_sha256"]
            execution._write(folder / "initial_source_feedback.json", feedback)
        manifest = {"schema_version": 1, "constructor": constructor, "branch": branch,
                    "initial_freeze_sha256": initial["registered"]["parent"]["freeze_sha256"],
                    "numerical_feedback": numeric, "source_feedback_sha256": feedback_sha256,
                    "files": bridge._inventory(folder)}
        execution._write(folder / "manifest.json", manifest)
        result = {"key": key, "directory": str(folder), "manifest": manifest, "packet_sha256": digest(manifest)}
        with self._locked():
            state, events = self._read(); self._open_science(state)
            require("packet_delivered" not in state["packets"][key] and not state["versions"][key], "Branch changed during packet construction")
            self._append("packet_delivered", result, events)
        self._verify_packet(self._read()[0], key)
        return {k: v for k, v in result.items() if k != "key"}

    def _verify_packet(self, state, key):
        delivery = state["packets"].get(key, {}).get("packet_delivered")
        require(delivery is not None, "No delivered branch packet")
        constructor, branch = key.split("/")
        initial_record = state["versions"][f"{constructor}/initial"]
        initial = initial_record["registered"]
        folder = self.directory / "packets" / key.replace("/", "_")
        require(delivery["directory"] == str(folder), "Packet directory changed")
        expected_files = {name: bridge._hash_bytes(content) for name, content in self._packet_files(initial).items()}
        feedback_sha256 = None
        if branch == "source_feedback":
            feedback = self._numerical_packet(initial_record)
            feedback_sha256 = feedback["source_feedback"]["packet_sha256"]
            expected_files["initial_source_feedback.json"] = bridge._hash_bytes(bridge._bytes(feedback))
        manifest = {"schema_version": 1, "constructor": constructor, "branch": branch,
                    "initial_freeze_sha256": initial["parent"]["freeze_sha256"], "numerical_feedback": branch == "source_feedback",
                    "source_feedback_sha256": feedback_sha256, "files": expected_files}
        bridge._same(delivery["manifest"], manifest, "Packet input role or bindings changed")
        require(delivery["packet_sha256"] == digest(manifest), "Packet digest changed")
        bridge._same(read_json(folder / "manifest.json"), manifest, "Packet manifest changed")
        bridge._same(bridge._inventory(folder), {**expected_files, "manifest.json": sha256(folder / "manifest.json")}, "Packet files changed")
        return delivery

    def record_branch_decision(self, constructor, branch, decision):
        require(branch in BRANCHES, "Branch decision required")
        with self._locked():
            state, events = self._read(); self._open_science(state)
            key = self._key(constructor, branch)
            require(key not in state["decisions"] and not state["versions"][key], "Branch choice is closed")
            packet = self._verify_packet(state, key)
            exact_keys(decision, {"action", "packet_sha256", "reason", "addressed_findings", "remaining_limitations"}, where="branch decision")
            require(decision["action"] in {"retain", "revise", "stop"} and decision["packet_sha256"] == packet["packet_sha256"], "Decision packet/action differs")
            source.text(decision["reason"], "decision reason")
            for field in ("addressed_findings", "remaining_limitations"):
                require(isinstance(decision[field], list) and all(isinstance(v, str) and v.strip() for v in decision[field]), "Text findings required")
            return self._append("decision", {"key": key, "decision": copy.deepcopy(decision)}, events)

    def abort_version(self, constructor, version, reason):
        with self._execution_lock():
            return self._abort_version(constructor, version, reason)

    def _abort_version(self, constructor, version, reason):
        source.text(reason, "abort reason")
        with self._locked():
            state, events = self._read(); self._open_science(state)
            key = self._key(constructor, version); record = state["versions"][key]
            require("aborted" not in record and "registered" not in record, "Only unregistered versions can be aborted")
            keys = [key]
            if version == "initial":
                keys += [f"{constructor}/{b}" for b in BRANCHES]
                require(all(not state["versions"][k] and k not in state["decisions"] and k not in state["packets"] for k in keys[1:]),
                        "Cannot abort initial after branches start")
            result = None
            for item in keys:
                result = self._append("aborted", {"key": item, "reason": reason}, events)
                events.append(result)
            return result

    def _inventory(self, state, *, check_targets=True):
        slots = []
        for constructor in CONSTRUCTORS:
            for version in VERSIONS:
                key = f"{constructor}/{version}"; record = state["versions"][key]
                planned = self._slots(constructor, version)
                decision = state["decisions"].get(key)
                if "aborted" in record or (decision and decision["decision"]["action"] == "stop"):
                    status = "aborted" if "aborted" in record else "stopped"
                    reason = record["aborted"]["reason"] if status == "aborted" else decision["decision"]["reason"]
                    for s in planned:
                        s.update(status=status, error={"type": status, "message": reason})
                    slots.extend(planned); continue
                if "registered" in record:
                    self._registration(record, constructor, version)
                    if version in BRANCHES:
                        self._verify_packet(state, key)
                    if "sources_closed" in record:
                        current = self._collect_sources(record, constructor, version)
                        bridge._same(current, {k: v for k, v in record["sources_closed"].items() if k != "key"}, "Closed source allocation changed")
                        targets = self._slots(constructor, version, "target")
                        if not current["eligibility"]["target_eligible"]:
                            for target in targets:
                                target.update(bundle=record["registered"]["bundle"], candidate=record["registered"]["candidate"],
                                              status="not_run", error={"type": "source_ineligible", "message": "; ".join(current["eligibility"]["reasons"])})
                        planned = current["slots"] + targets
                    if check_targets and "targets_closed" in record:
                        targets = self._collect_targets(record, constructor, version)
                        bridge._same(targets, record["targets_closed"]["slots"], "Closed target allocation changed")
                        bridge._same(self._target_artifacts(record, constructor, version), record["targets_closed"]["artifacts"],
                                     "Retained target failure artifacts changed")
                        bridge._same(self._target_support(record, constructor, version), record["targets_closed"]["support_checks"],
                                     "Retained target support counts changed")
                        planned = [s for s in planned if s["role"] == "source"] + targets
                slots.extend(planned)
        return slots

    def _scientific_annotations(self, state):
        annotations = {}
        for key, record in state["versions"].items():
            registered = record.get("registered")
            decision = state["decisions"].get(key)
            reason = record.get("aborted", {}).get("reason")
            if reason is None and decision and decision["decision"]["action"] == "stop":
                reason = decision["decision"]["reason"]
            analysis = None
            source_reports = []
            if registered:
                path = Path(registered["bundle"]) / registered["candidate"] / "analysis_evidence.json"
                analysis = {"path": str(path), "sha256": sha256(path)}
                if "source_report_event" in record:
                    path = self.directory / "events" / f"{record['source_report_event']['sequence']:06d}.json"
                    source_reports.append({"path": str(path), "sha256": sha256(path)})
            annotations[key] = {"candidate_binding": None if registered is None else {k: registered[k] for k in ("bundle", "candidate", "parent")},
                                "analysis_evidence": analysis,
                                "support_assessment": None if registered is None else registered["support"]["assessment"],
                                "source_feedback": source_reports, "source_feedback_format": "pilot_source_closure_event_v1",
                                "unavailable_reason": (reason or "Version not admitted") if registered is None else
                                                      (None if source_reports else "Source phase has not closed")}
        return annotations

    def freeze_scientific_inventory(self):
        with self._execution_lock():
            return self._freeze_scientific_inventory()

    def _freeze_scientific_inventory(self):
        with self._locked():
            state, events = self._read(); self._open_science(state)
            for key, record in state["versions"].items():
                decision = state["decisions"].get(key)
                disposed = "aborted" in record or (decision and decision["decision"]["action"] == "stop")
                require(disposed or ("registered" in record and "sources_closed" in record), "Every version needs closed sources or an explicit failure")
                if key.split("/")[1] in BRANCHES and not disposed:
                    require(decision is not None, "Branch decision missing")
                require("targets_intent" not in record, "Target execution preceded freeze")
                if "registered" in record:
                    root = Path(record["registered"]["bundle"])
                    require(not (root / "executions").exists() or not any((root / "executions").iterdir()), "Unexpected parent execution before freeze")
            for key, packet in state["packets"].items():
                if "packet_delivered" in packet:
                    self._verify_packet(state, key)
            slots = self._inventory(state, check_targets=False)
            payload = {"slots": slots, "inventory_sha256": digest(slots), "state_sha256": digest(state),
                       "release_sha256": self.release_sha256, "scientific_annotations": self._scientific_annotations(state),
                       "packet_artifacts": bridge._inventory(self.directory / "packets")}
            return self._append("scientific_freeze", payload, events)

    def _verify_scientific_freeze(self, state):
        freeze = state["scientific_freeze"]
        require(freeze is not None and freeze["release_sha256"] == self.release_sha256, "Scientific freeze missing")
        before = copy.deepcopy(state)
        before.update(scientific_freeze=None, closed=None, authorization=None)
        for record in before["versions"].values():
            record.pop("targets_intent", None); record.pop("targets_closed", None)
            record.pop("target_attempt", None); record.pop("target_error", None)
        require(digest(before) == freeze["state_sha256"], "Scientific decisions changed after freeze")
        slots = self._inventory(before, check_targets=False)
        require(digest(slots) == freeze["inventory_sha256"], "Scientific inventory changed")
        bridge._same(slots, freeze["slots"], "Frozen source inventory differs")
        bridge._same(self._scientific_annotations(state), freeze["scientific_annotations"], "Scientific report bindings changed")
        bridge._same(bridge._inventory(self.directory / "packets"), freeze["packet_artifacts"], "Retained packet artifacts changed")
        for key, packet in state["packets"].items():
            if "packet_delivered" in packet:
                self._verify_packet(state, key)
        self._verify_parent_runs(state)
        return freeze

    def _verify_parent_runs(self, state):
        allowed = {}
        for key, record in state["versions"].items():
            if "registered" not in record:
                continue
            root = record["registered"]["bundle"]
            allowed.setdefault(root, set())
            if "targets_intent" in record:
                allowed[root].update(record.get("target_attempt", {}))
        for root, names in allowed.items():
            folder = Path(root) / "executions"
            if folder.exists():
                require(all(p.is_dir() and not p.is_symlink() and p.name in names for p in folder.iterdir()),
                        "Unplanned or unauthorized parent target run")

    def _target_directory(self, record, run_id):
        return Path(record["registered"]["bundle"]) / "executions" / run_id

    def _target_artifacts(self, record, constructor, version):
        return {s["run_id"]: bridge._inventory(self._target_directory(record, s["run_id"]))
                for s in self._slots(constructor, version, "target") if self._target_directory(record, s["run_id"]).exists()}

    def _target_support(self, record, constructor, version):
        inspected = bridge.preflight(record["registered"]["bundle"], record["registered"]["candidate"])
        return [self._support_counts(inspected, record["registered"]["bundle"], s["run_id"], s["context_id"])
                for s in self._slots(constructor, version, "target")
                if (self._target_directory(record, s["run_id"]) / "output/generated.csv").is_file()]

    def _collect_targets(self, record, constructor, version):
        registered = record["registered"]
        inspected, _ = self._registration(record, constructor, version)
        target_root = bridge._child_root(bridge._destination(inspected["root"], inspected["relative"]), self.release["target_context"])
        bridge._same(read_json(target_root / "task.json"), inspected["task"], "Parent is not the sealed target task")
        bridge._same(read_json(target_root / bridge.CHILD / "model_spec.json"), inspected["spec"], "Parent is not the sealed target model")
        require(sha256(target_root / bridge.CHILD / "generator.py") == registered["parent"]["generator_sha256"], "Target generator differs")
        slots = self._slots(constructor, version, "target")
        for slot in slots:
            slot.update(bundle=registered["bundle"], candidate=registered["candidate"])
            directory = self._target_directory(record, slot["run_id"])
            path = directory / "execution.json"
            output = directory / "output/generated.csv"
            if not path.exists():
                error = record.get("target_error", {}).get(slot["run_id"])
                slot.update(status="error" if error else "interrupted" if slot["run_id"] in record.get("target_attempt", {}) else "not_run",
                            error=error["error"] if error else {"type": "phase_aborted", "message": "Reserved target allocation ended without a complete receipt; no retry"})
                slot["output_sha256"] = sha256(output) if output.is_file() else None
                continue
            try:
                receipt = execution.verify_execution(registered["bundle"], slot["run_id"])
            except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
                slot.update(status="error", execution_sha256=sha256(path),
                            output_sha256=sha256(output) if output.is_file() else None,
                            error={"type": "execution_verification_failed", "message": str(error)[:2000]})
                continue
            require(receipt["candidate"] == registered["candidate"] and
                    receipt["candidate_freeze_sha256"] == registered["parent"]["freeze_sha256"] and receipt["route"] == "generator.py",
                    "Target execution candidate differs")
            bridge._same(receipt["limits"], execution._limits(**self.release["execution_limits"], seed=slot["seed"]), "Target execution seed/limits differ")
            slot.update(status=receipt["status"], execution_sha256=sha256(path),
                        output_sha256=sha256(output) if output.is_file() else None, error=receipt["error"])
            if slot["status"] == "success":
                counts = self._support_counts(inspected, registered["bundle"], slot["run_id"], slot["context_id"])
                if counts["report"]["status"] != "pass" or counts["report"]["row_count"] != slot["n_rows"]:
                    slot.update(status="failed", error={"type": "target_support_failure", "message": canonical(counts["report"]).decode()})
        return slots

    def dispatch_targets(self, constructor, version):
        with self._execution_lock():
            return self._dispatch_targets(constructor, version)

    def _dispatch_targets(self, constructor, version):
        with self._locked():
            state, events = self._read(); freeze = self._verify_scientific_freeze(state)
            key = self._key(constructor, version); record = state["versions"][key]
            require(state["closed"] is None and "registered" in record and "sources_closed" in record and
                    "targets_intent" not in record, "Target allocation unavailable or consumed")
            require(record["sources_closed"]["eligibility"]["target_eligible"], "Source gate prohibits target execution")
            self._registration(record, constructor, version)
            for slot in self._slots(constructor, version, "target"):
                require(not self._target_directory(record, slot["run_id"]).exists(), "Target run appeared before authorization")
            self._runtime()
            self._append("targets_intent", {"key": key, "slots_debited": 3, "rows_debited": 9000,
                                           "scientific_freeze_sha256": freeze["event_sha256"], "parent": record["registered"]["parent"]}, events)
        registered = record["registered"]
        for slot in self._slots(constructor, version, "target"):
            with self._locked():
                state, events = self._read(); self._verify_scientific_freeze(state)
                require(state["closed"] is None and state["authorization"] is None and
                        "targets_closed" not in state["versions"][key], "Target allocation was closed")
                self._append("target_attempt", {"key": key, "run_id": slot["run_id"], "seed": slot["seed"], "parent": registered["parent"]}, events)
            try:
                execution.run_candidate(registered["bundle"], registered["candidate"], slot["run_id"], slot["seed"],
                                        runtime=execution.DEFAULT_RUNTIME, **self.release["execution_limits"])
            except Exception as error:
                with self._locked():
                    state, events = self._read()
                    self._append("target_error", {"key": key, "run_id": slot["run_id"],
                                                 "error": {"type": type(error).__name__, "message": str(error)[:2000]}}, events)
        return self._finish_targets(constructor, version)

    def finish_targets(self, constructor, version):
        with self._execution_lock():
            return self._finish_targets(constructor, version)

    def _finish_targets(self, constructor, version):
        with self._locked():
            state, events = self._read(); self._verify_scientific_freeze(state)
            key = self._key(constructor, version); record = state["versions"][key]
            require(state["closed"] is None and "targets_intent" in record and "targets_closed" not in record,
                    "No open target allocation")
            return self._append("targets_closed", {"key": key, "slots": self._collect_targets(record, constructor, version),
                                                    "artifacts": self._target_artifacts(record, constructor, version),
                                                    "support_checks": self._target_support(record, constructor, version)}, events)

    def close_targets(self):
        with self._locked():
            state, events = self._read(); freeze = self._verify_scientific_freeze(state)
            require(state["closed"] is None, "Pilot already closed")
            for record in state["versions"].values():
                require("registered" not in record or not record["sources_closed"]["eligibility"]["target_eligible"] or
                        "targets_closed" in record, "Target allocation remains open")
            slots = self._inventory(state)
            require(len(slots) == 72 and all(s["status"] != "pending" for s in slots), "Closed inventory omits slots")
            payload = {"schema_version": 1, "kind": "developmental_pilot_closed_inventory", "status": "closed", "scientific_closed": True,
                       "release_sha256": self.release_sha256, "scientific_freeze_sha256": freeze["event_sha256"],
                       "inventory_sha256": digest(slots), "slots": slots,
                       "scientific_annotations": freeze["scientific_annotations"]}
            self._append("closed", payload, events)
            return payload

    def _verify_closed(self, state):
        freeze = self._verify_scientific_freeze(state)
        closed = state["closed"]
        require(closed is not None and closed["scientific_freeze_sha256"] == freeze["event_sha256"] and
                closed["release_sha256"] == self.release_sha256, "Pilot is not closed")
        slots = self._inventory(state)
        require(len(slots) == 72 and all(s["status"] != "pending" for s in slots) and digest(slots) == closed["inventory_sha256"],
                "Closed inventory changed")
        bridge._same(slots, closed["slots"], "Closed slots differ")
        bridge._same(closed["scientific_annotations"], freeze["scientific_annotations"], "Closed scientific annotations changed")
        return {k: v for k, v in closed.items() if k != "event_sha256"}

    def authorize_evaluation(self, evaluator_sha256):
        with self._locked():
            state, events = self._read(); closed = self._verify_closed(state)
            require(state["authorization"] is None and evaluator_sha256 == self.release["evaluator"]["sha256"], "Evaluator not authorized or authorization consumed")
            authorization = {"release_sha256": self.release_sha256, "inventory_sha256": closed["inventory_sha256"],
                             "scientific_freeze_sha256": closed["scientific_freeze_sha256"], "evaluator_sha256": evaluator_sha256}
            return self._append("authorization", authorization, events)

    def verify_evaluation(self, evaluator_sha256):
        state, _ = self._read(); closed = self._verify_closed(state)
        authorization = state["authorization"]
        require(authorization is not None and evaluator_sha256 == self.release["evaluator"]["sha256"] and
                authorization["evaluator_sha256"] == evaluator_sha256 and
                authorization["release_sha256"] == self.release_sha256 and authorization["inventory_sha256"] == closed["inventory_sha256"] and
                authorization["scientific_freeze_sha256"] == closed["scientific_freeze_sha256"], "Evaluation authorization differs")
        return {**closed, "authorization": authorization}

    def verify(self):
        state, _ = self._read()
        if state["scientific_freeze"] is not None:
            self._verify_scientific_freeze(state)
        if state["closed"] is not None:
            self._verify_closed(state)
        return {"release_sha256": self.release_sha256, "state": state, "slots": self._inventory(state)}

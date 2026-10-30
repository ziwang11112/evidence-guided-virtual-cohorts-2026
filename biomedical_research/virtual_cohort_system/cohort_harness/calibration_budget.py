"""Bundle-global calibration reservations with an append-only event ledger.

Reserve a whole worst-case session before creating trials or dispatching work.
Reservations are charged permanently: finishing with smaller actual usage, or
failing, never refunds them. Only the reserving Python process may finish a
session. Pending sessions and interrupted writes cannot recover or auto-rerun.

An exclusive operation lock serializes readers and writers. A failed mutation
retains its lock; immutable events and an atomic head checkpoint fail closed on
partial commits. Files are flushed before atomic installation (write-through on
Windows, directory fsync on POSIX). Hashes detect retained-artifact inconsistency;
they are not signatures against an administrator rewriting the entire ledger.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets

from .contracts import ContractError, _hash, exact_keys, require, text, validate_task
from .lifecycle import _bundle, _path, read_json, safe_relative, sha256

DIRECTORY = "calibration_budget"
MAX_COUNTER = 2**31 - 1
_COUNTERS = {"sessions", "trials", "executions", "reserved_seconds"}
_PROCESS_NONCE = secrets.token_hex(32)
_MAX_FILE_BYTES = 131_072


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _envelope(payload):
    return {"payload": payload, "sha256": _digest(payload)}


def _counter(value, label, minimum=0):
    require(type(value) is int and minimum <= value <= MAX_COUNTER,
            f"{label} must be an integer in [{minimum}, {MAX_COUNTER}]")


def _counts(value, label, *, positive, session=False):
    exact_keys(value, _COUNTERS, where=label)
    for key, number in value.items():
        _counter(number, label + "." + key, 1 if positive else 0)
    if session:
        require(value["sessions"] == 1, label + ".sessions must be 1")
    return copy.deepcopy(value)


def _binding(value):
    require(type(value) is dict and bool(value), "Session binding must be a nonempty object")

    def check(item, depth=0):
        require(depth <= 8, "Binding nesting exceeds limit")
        if type(item) is dict:
            require(len(item) <= 128, "Binding object exceeds limit")
            for key, entry in item.items():
                text(key, "binding key")
                require(len(key) <= 128, "Binding key exceeds limit")
                if key.endswith("_sha256"):
                    _hash(entry)
                check(entry, depth + 1)
        elif type(item) is list:
            require(len(item) <= 128, "Binding list exceeds limit")
            for entry in item:
                check(entry, depth + 1)
        elif type(item) is str:
            require(len(item) <= 4096, "Binding text exceeds limit")
        elif item is None or type(item) is bool:
            pass
        elif type(item) is int:
            require(abs(item) <= 2**53 - 1, "Binding integer exceeds exact JSON range")
        elif type(item) is float:
            require(math.isfinite(item), "Binding numbers must be finite")
        else:
            raise ContractError("Binding must contain only bounded JSON values")

    check(value)
    require(len(_canonical(value)) <= 16_384, "Binding exceeds byte limit")
    return copy.deepcopy(value)


def _session_id(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value),
            "Session ID must be a simple portable name")
    safe_relative(value)
    return value


def _owner():
    return {"pid": os.getpid(), "nonce": _PROCESS_NONCE}


def _check_owner(value):
    exact_keys(value, {"pid", "nonce"}, where="session owner")
    _counter(value["pid"], "owner PID", 1)
    _hash(value["nonce"])


def _sync_directory(directory):
    if os.name != "nt":
        descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _install(temporary, destination, *, replace):
    if os.name == "nt":
        # MoveFileEx without REPLACE_EXISTING provides an exclusive atomic
        # install. WRITE_THROUGH requests completion before returning.
        import ctypes
        from ctypes import wintypes
        move = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
        move.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD)
        move.restype = wintypes.BOOL
        if not move(str(temporary), str(destination), 0x8 | (0x1 if replace else 0)):
            raise ctypes.WinError(ctypes.get_last_error())
    elif replace:
        os.replace(temporary, destination)
    else:
        os.link(temporary, destination)  # Atomic and never overwrites an event.
        temporary.unlink()
    _sync_directory(destination.parent)


def _write_atomic(directory, name, value, *, replace=False):
    destination = _path(directory, name, file=False)
    temporary = _path(directory, "." + name + "." + secrets.token_hex(8) + ".tmp", file=False)
    data = _canonical(value) + b"\n"
    require(len(data) <= _MAX_FILE_BYTES, "Budget artifact exceeds byte limit")
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    _install(temporary, destination, replace=replace)


@contextmanager
def _operation(directory, operation):
    lock = _path(directory, ".operation.lock", file=False)
    payload = _canonical({"owner": _owner(), "operation": operation})
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise ContractError("Concurrent or interrupted budget operation; recovery is unsupported") from error
    # A crash while writing the lock also leaves the budget safely blocked.
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    _sync_directory(directory)
    guard = {"dirty": False}

    def release():
        require(_path(directory, ".operation.lock").read_bytes() == payload,
                "Budget operation lock changed")
        lock.unlink()
        _sync_directory(directory)

    try:
        yield guard
    except BaseException:
        if not guard["dirty"]:
            release()  # Ordinary rejected requests do not poison the budget.
        raise
    else:
        release()


def _read_envelope(directory, name):
    path = _path(directory, name)
    require(0 < path.stat().st_size <= _MAX_FILE_BYTES, "Invalid budget artifact size")
    value = read_json(path)
    exact_keys(value, {"payload", "sha256"}, where="budget hash envelope")
    _hash(value["sha256"])
    require(value["sha256"] == _digest(value["payload"]), "Budget artifact hash mismatch")
    return value["payload"], value["sha256"]


def _location(bundle):
    root = _bundle(bundle)
    directory = _path(root, DIRECTORY, file=False)
    require(directory.is_dir(), "Create the bundle-global calibration budget first")
    return root, directory


def _read_state(root, directory):
    entries = {entry.name for entry in directory.iterdir()}
    require(entries == {"config.json", "head.json", "events", ".operation.lock"},
            "Budget directory inventory changed or initialization was interrupted")
    for name in entries:
        _path(directory, name, file=False)
    event_dir = _path(directory, "events", file=False)
    require(event_dir.is_dir(), "Budget event directory missing")
    config, config_hash = _read_envelope(directory, "config.json")
    exact_keys(config, {"schema_version", "kind", "task_sha256", "limits", "refunds"}, where="budget config")
    require(type(config["schema_version"]) is int and config["schema_version"] == 1 and
            config["kind"] == "bundle_global_calibration_budget" and config["refunds"] is False,
            "Invalid budget config identity or refund policy")
    _hash(config["task_sha256"])
    require(config["task_sha256"] == sha256(_path(root, "task.json")), "Budget task.json binding changed")
    limits = _counts(config["limits"], "budget limits", positive=True)
    head, _ = _read_envelope(directory, "head.json")
    exact_keys(head, {"config_sha256", "event_count", "last_event_sha256"}, where="budget head")
    require(head["config_sha256"] == config_hash, "Budget config binding changed")
    _counter(head["event_count"], "event count")
    _hash(head["last_event_sha256"])
    files = sorted(event_dir.iterdir(), key=lambda path: path.name)
    require(len(files) == head["event_count"], "Budget event inventory differs from head")
    reserved, used = ({key: 0 for key in _COUNTERS} for _ in range(2))
    sessions, ids, pending, previous = {}, set(), None, config_hash
    for index, path in enumerate(files, 1):
        name = f"{index:08d}.json"
        require(path.name == name, "Budget events must be contiguous and append-only")
        event, event_hash = _read_envelope(event_dir, name)
        common = {"schema_version", "kind", "sequence", "previous_sha256", "config_sha256",
                  "session_id", "created_utc"}
        require(isinstance(event, dict) and event.get("kind") in {"reserve", "finish"}, "Invalid budget event kind")
        extra = {"reservation", "binding", "owner"} if event["kind"] == "reserve" else {
            "status", "usage", "reservation_sha256"}
        exact_keys(event, common | extra, where="budget event")
        require(type(event["schema_version"]) is int and event["schema_version"] == 1 and
                type(event["sequence"]) is int and event["sequence"] == index,
                "Budget event version or sequence changed")
        require(event["config_sha256"] == config_hash and event["previous_sha256"] == previous,
                "Budget event hash chain changed")
        text(event["created_utc"], "budget event time")
        identifier = _session_id(event["session_id"])
        if event["kind"] == "reserve":
            require(pending is None, "Budget contains overlapping pending sessions")
            require(identifier.casefold() not in ids, "Budget session ID reused")
            reservation = _counts(event["reservation"], "reservation", positive=True, session=True)
            binding = _binding(event["binding"])
            _check_owner(event["owner"])
            for key in _COUNTERS:
                reserved[key] += reservation[key]
                require(reserved[key] <= limits[key], "Budget reservations exceed global limits")
            sessions[identifier] = {"status": "pending", "reservation": reservation, "binding": binding,
                                    "reservation_sha256": event_hash, "owner": event["owner"]}
            ids.add(identifier.casefold())
            pending = identifier
        else:
            require(pending == identifier, "Budget finish does not match pending session")
            record = sessions[identifier]
            require(event["reservation_sha256"] == record["reservation_sha256"], "Budget finish reservation changed")
            require(event["status"] in {"completed", "failed"}, "Invalid finished session status")
            usage = _counts(event["usage"], "usage", positive=False, session=True)
            for key in _COUNTERS:
                require(usage[key] <= record["reservation"][key], "Actual usage exceeds reservation")
                used[key] += usage[key]
            record.update(status=event["status"], usage=usage, finish_sha256=event_hash)
            pending = None
        previous = event_hash
    require(previous == head["last_event_sha256"], "Budget head does not match final event")
    return {"config_sha256": config_hash, "task_sha256": config["task_sha256"], "limits": limits,
            "reserved": reserved, "used": used, "remaining": {key: limits[key] - reserved[key] for key in _COUNTERS},
            "sessions": sessions, "pending": pending, "event_count": head["event_count"],
            "last_event_sha256": previous, "refunds": False}


def _append(directory, state, event):
    index = state["event_count"] + 1
    _counter(index, "event count", 1)
    payload = {"schema_version": 1, "sequence": index, "config_sha256": state["config_sha256"],
               "previous_sha256": state["last_event_sha256"],
               "created_utc": datetime.now(timezone.utc).isoformat(), **event}
    envelope = _envelope(payload)
    _write_atomic(_path(directory, "events", file=False), f"{index:08d}.json", envelope)
    _write_atomic(directory, "head.json", _envelope({"config_sha256": state["config_sha256"],
                  "event_count": index, "last_event_sha256": envelope["sha256"]}), replace=True)


def create_budget(bundle, limits):
    """Create the one permanent budget for a bundle; an existing one cannot reset."""
    limits = _counts(limits, "budget limits", positive=True)
    root = _bundle(bundle)
    validate_task(read_json(_path(root, "task.json")))
    directory = _path(root, DIRECTORY, file=False)
    try:
        directory.mkdir()
    except FileExistsError as error:
        raise ContractError("Bundle calibration budget already exists; reset is forbidden") from error
    with _operation(directory, "create") as guard:
        guard["dirty"] = True
        directory.joinpath("events").mkdir()
        config = _envelope({"schema_version": 1, "kind": "bundle_global_calibration_budget",
                            "task_sha256": sha256(_path(root, "task.json")), "limits": limits, "refunds": False})
        _write_atomic(directory, "config.json", config)
        _write_atomic(directory, "head.json", _envelope({"config_sha256": config["sha256"],
                      "event_count": 0, "last_event_sha256": config["sha256"]}))
        return _read_state(root, directory)


def get_budget(bundle):
    """Verify the complete ledger; pending sessions are visible but block new work."""
    root, directory = _location(bundle)
    with _operation(directory, "inspect"):
        return _read_state(root, directory)


def reserve_session(bundle, session_id, reservation, binding):
    """Durably charge a whole session before returning permission to dispatch it."""
    session_id = _session_id(session_id)
    reservation = _counts(reservation, "reservation", positive=True, session=True)
    binding = _binding(binding)
    root, directory = _location(bundle)
    with _operation(directory, "reserve") as guard:
        state = _read_state(root, directory)
        require(state["pending"] is None, "A pending session blocks new work; recovery is unsupported")
        require(session_id.casefold() not in {name.casefold() for name in state["sessions"]}, "Session ID already used")
        require(all(reservation[key] <= state["remaining"][key] for key in _COUNTERS), "Global calibration budget exhausted")
        guard["dirty"] = True
        _append(directory, state, {"kind": "reserve", "session_id": session_id,
                                  "reservation": reservation, "binding": binding, "owner": _owner()})
        return _read_state(root, directory)["sessions"][session_id]


def finish_session(bundle, session_id, status, usage):
    """Record actual usage without refund; another process cannot finish a lease."""
    session_id = _session_id(session_id)
    require(status in {"completed", "failed"}, "Finished status must be completed or failed")
    usage = _counts(usage, "usage", positive=False, session=True)
    root, directory = _location(bundle)
    with _operation(directory, "finish") as guard:
        state = _read_state(root, directory)
        require(state["pending"] == session_id, "Session is not the pending reservation")
        record = state["sessions"][session_id]
        require(record["owner"] == _owner(), "Pending session belongs to another process; recovery is unsupported")
        require(all(usage[key] <= record["reservation"][key] for key in _COUNTERS), "Actual usage exceeds reservation")
        guard["dirty"] = True
        _append(directory, state, {"kind": "finish", "session_id": session_id, "status": status,
                                  "usage": usage, "reservation_sha256": record["reservation_sha256"]})
        return _read_state(root, directory)["sessions"][session_id]

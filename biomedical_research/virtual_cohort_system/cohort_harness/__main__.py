"""Inspect, freeze, retrieve permitted evidence, and explicitly execute candidates.

Validation remains static. Only the execute command invokes the configured
execution adapter; it never falls back to running Agent code in this process.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import pandas as pd

from .contracts import validate_task, validate_input, validate_output, validate_evidence, validate_spec
from .lifecycle import freeze_candidate, verify_candidate, read_json, read_table, validate_program
from .source_checks import run_source_checks


def read(path):
    return read_json(path)


def candidate_path(bundle, name):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name):
        raise ValueError("Use a simple candidate name")
    return Path(bundle).resolve() / "candidates" / name


def validate_bundle(bundle, candidate):
    bundle, candidate = Path(bundle).resolve(), Path(candidate).resolve()
    task = read(bundle / "task.json")
    validate_task(task)
    if task["mode"] == "whole_cohort":
        if (bundle / "observed.csv").exists():
            raise ValueError("Whole-cohort mode must not supply observed.csv")
        observed = None
    else:
        observed = load_table(bundle / "observed.csv", task)
    validate_input(observed, task)
    ids = validate_evidence(read(candidate / "evidence.json"), task)
    validate_spec(read(candidate / "model_spec.json"), ids)
    program, rows = candidate / "generator.py", candidate / "generated.csv"
    if program.is_file() == rows.is_file():
        raise ValueError("Submit exactly one route: generator.py or generated.csv")
    if program.is_file():
        validate_program(program)
    if rows.is_file():
        output = load_table(rows, task)
        validate_output(observed, output, task)
    return {"contract": "valid", "route": "program" if program.is_file() else "direct_rows",
            "generator_executed": False, "scientific_validity": "not_assessed"}


def load_table(path, task):
    return read_table(path, task)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    demo = subs.add_parser("demo", help="Create a new invented mechanical fixture")
    demo.add_argument("--destination", required=True)
    execute = subs.add_parser("execute", help="Run a frozen candidate through the explicit execution adapter")
    execute.add_argument("--bundle", required=True)
    execute.add_argument("--candidate", required=True)
    execute.add_argument("--run-id", required=True)
    execute.add_argument("--seed", required=True, type=int)
    execute.add_argument("--runtime", required=True, help="Trusted runtime configuration JSON")
    execute.add_argument("--timeout-seconds", type=int, default=30)
    execute.add_argument("--memory-mb", type=int, default=1024)
    execute.add_argument("--output-bytes", type=int, default=20_000_000)
    execution_verify = subs.add_parser("verify-execution", help="Verify recorded execution commitments")
    execution_verify.add_argument("--bundle", required=True)
    execution_verify.add_argument("--run-id", required=True)
    for name in ("validate", "source-checks", "freeze", "verify"):
        command = subs.add_parser(name)
        command.add_argument("--bundle", required=True)
        command.add_argument("--candidate", required=True)
        if name == "freeze":
            command.add_argument("--parent")
            command.add_argument("--revision", help="Path to explicit revision JSON")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            from .demo import make_demo
            result = {"created": str(make_demo(args.destination)), "scope": "invented_fixture_only"}
        elif args.command == "execute":
            from .execution import run_candidate
            bundle = Path(args.bundle).resolve()
            result = run_candidate(bundle, candidate_path(bundle, args.candidate), args.run_id, args.seed,
                                   runtime=read(args.runtime), timeout_seconds=args.timeout_seconds,
                                   memory_mb=args.memory_mb, output_bytes=args.output_bytes)
        elif args.command == "verify-execution":
            from .execution import verify_execution
            result = verify_execution(Path(args.bundle).resolve(), args.run_id)
        else:
            bundle = Path(args.bundle).resolve()
            candidate = candidate_path(bundle, args.candidate)
            if args.command == "verify":
                result = verify_candidate(bundle, candidate)
            elif args.command == "validate":
                result = validate_bundle(bundle, candidate)
            elif args.command == "source-checks":
                validate_bundle(bundle, candidate)
                if (candidate / "freeze.json").exists():
                    raise ValueError("Frozen candidate cannot receive new reports; create a new candidate")
                result = run_source_checks(bundle, candidate)
                report = candidate / "source_check_report.json"
                with report.open("x", encoding="utf-8") as out:
                    json.dump(result, out, indent=2, allow_nan=False)
                    out.write("\n")
                result = {"report": str(report), "sha256": hashlib.sha256(report.read_bytes()).hexdigest(), **result}
            else:
                validate_bundle(bundle, candidate)
                if bool(args.parent) != bool(args.revision):
                    raise ValueError("Parent and revision must be supplied together")
                parent = candidate_path(bundle, args.parent) / "freeze.json" if args.parent else None
                result = freeze_candidate(bundle, candidate, parent_receipt=parent,
                                          revision=read(args.revision) if args.revision else None)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 2 if args.command == "execute" and result.get("status") in {"failed", "timeout", "error"} else 0
    except (ValueError, KeyError, TypeError, OSError, pd.errors.ParserError) as exc:
        print(json.dumps({"status": "error", "type": type(exc).__name__, "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

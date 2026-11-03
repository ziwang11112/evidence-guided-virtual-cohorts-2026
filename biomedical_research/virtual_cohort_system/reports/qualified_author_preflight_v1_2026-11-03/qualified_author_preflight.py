"""Read-only author check of bindings, aliases, mappings and operators.

Only four named JSON inputs are read by the CLI. The in-memory API calls the
released pure alias/mapping/operator contracts, never their lifecycle entrypoints.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

# Importing this utility must not create bytecode beside released code.
sys.dont_write_bytecode = True
PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))
HELPER_PATH = PROJECT / "work/evidence_revision_v1_2026-11-02/implementation/qualified_relationships_v1.py"
_module_spec = importlib.util.spec_from_file_location("_qualified_preflight_contracts", HELPER_PATH)
qualified = importlib.util.module_from_spec(_module_spec)
_module_spec.loader.exec_module(qualified)
contracts, semantic = qualified.contracts, qualified.semantic
require = contracts.require
PLAN = "qualified_plan_v1.json"
FILES = ("task.json", "evidence.json", "model_spec.json", PLAN)
LIMITATIONS = [
    "Only authored bindings, declaration shape, aliases, mappings and evidence-bound operators are checked.",
    "No source authenticity, faithful extraction, population reconstruction, moments, support, or transport proof.",
    "No independent review, approval, freeze, bridge, generator import/execution, sampling, or table access.",
    "Bridge/evidence-use consistency, strict semantics, source coverage, evidence registry, frozen bindings, receipts and scientific review remain unchecked.",
]
BAD = object()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dependency_fingerprints():
    paths = [Path(__file__), HELPER_PATH, Path(contracts.__file__), Path(semantic.__file__),
             Path(qualified.source_checks.__file__)]
    return {str(path.resolve()): digest(path) for path in paths}


def _index(rows, field):
    require(isinstance(rows, list), "Metadata collection must be a list")
    indexed = {}
    for row in rows:
        require(isinstance(row, dict), "Metadata entry must be an object")
        contracts.text(row[field], field)
        require(row[field] not in indexed, "Duplicate metadata ID: " + row[field])
        indexed[row[field]] = row
    return indexed


def _pointer(value):
    return str(value).replace("~", "~0").replace("/", "~1")


def preflight_metadata(task, evidence, spec, plan, *, source_paths=None):
    """Inspect dictionaries without changing them. Paths label findings only.

    This is an early check of the parent authored declaration. Derived bindings
    must be exactly {}, and no independent-review object is accepted or made.
    """
    paths = source_paths or {name: "memory:" + name for name in FILES}
    findings, summaries = [], []

    def attempt(code, pointer, operation, hint, context=None, check=None, file=PLAN):
        try:
            return operation()
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            findings.append({"code": code, "context_id": context, "check_id": check,
                             "source_path": paths[file], "json_pointer": pointer,
                             "message": str(error), "metadata_remediation_hint": hint})
            return BAD

    def root_contract():
        contracts.exact_keys(plan, {"schema_version", "contexts"}, where="qualified parent plan")
        require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid qualified parent plan")
        require(isinstance(plan["contexts"], dict) and bool(plan["contexts"]), "Qualified contexts must be a nonempty object")

    root_state = attempt("input_structure", "", root_contract, "Correct the qualified-plan JSON structure before rechecking.")
    inputs = [(task, "columns", "name", "task.json"), (evidence, "items", "id", "evidence.json"),
              (spec, "assumptions", "id", "model_spec.json")]
    state = [attempt("input_structure", "/" + key, lambda obj=obj, key=key, field=field: _index(obj[key], field),
                     "Use a list of uniquely identified metadata objects.", file=file) for obj, key, field, file in inputs]
    if root_state is not BAD and all(value is not BAD for value in state):
        base_columns, items, known = state
        known = set(known)
        for context_id, declaration in plan["contexts"].items():
            pointer = "/contexts/" + _pointer(context_id)
            before = len(findings)
            summary = {"context_id": context_id, "checks": []}
            summaries.append(summary)

            def context_shape():
                qualified._exact(declaration, "schema_version bindings context_role context_id population measurement source_ids assumption_ids column_aliases checks", "qualified declaration")
                require(type(declaration["schema_version"]) is int and declaration["schema_version"] == 1, "Invalid qualified schema")
                require(declaration["context_id"] == context_id and declaration["context_role"] == "source", "Qualified context label mismatch")
                require(isinstance(declaration["checks"], list) and 1 <= len(declaration["checks"]) <= 16, "Declare one to sixteen qualified checks")

            if attempt("context_structure", pointer, context_shape, "Use the released qualified declaration schema.", context_id) is BAD:
                summary["status"] = "failed"
                continue
            attempt("authored_bindings", pointer + "/bindings",
                    lambda: require(declaration["bindings"] == {}, "Authored qualified plan must leave derived bindings exactly {}"),
                    "Use an empty object {}; the controller derives bindings after freeze and seal.", context_id)

            alias_state = attempt("column_aliases", pointer + "/column_aliases",
                                  lambda: qualified._alias_contract(declaration["column_aliases"], base_columns, known),
                                  "Declare unique one-step native aliases of original numeric generated columns with existing assumption IDs.", context_id)
            for index, check in enumerate(declaration["checks"]):
                at = pointer + "/checks/" + str(index)
                check_id = check.get("id") if isinstance(check, dict) else None
                row = {"check_id": check_id, "status": "blocked"}
                summary["checks"].append(row)
                check_before = len(findings)

                def check_contract():
                    qualified._exact(check, "id evidence_id semantic_check_id operator source_relation measurement_mapping", "qualified check")
                    require(check["evidence_id"] in items, "Unknown qualified evidence ID")
                    return items[check["evidence_id"]]

                item = attempt("check_metadata", at, check_contract,
                               "Use the released check schema and an existing evidence ID.", context_id, check_id)
                if item is BAD:
                    row["status"] = "failed"
                    continue
                mapping, operator = check["measurement_mapping"], check["operator"]

                def mapping_contract():
                    if operator is None:
                        require(mapping == {"kind": "identity"}, "Unavailable operator cannot apply a mapping")
                        return base_columns
                    require(isinstance(operator, dict), "Operator must be an object or null")
                    require(isinstance(mapping, dict), "Measurement mapping must be explicit")
                    return qualified._mapping_contract(mapping, operator, alias_state[0], items, known)

                if alias_state is not BAD:
                    hint = "Match input/output names to the retained unit-evidence variables. If they name the same generated measurement, declare its native alias with an existing measurement assumption and use that alias as input; do not change evidence or scientific constants merely to pass."
                    mapped = attempt("measurement_mapping", at + "/measurement_mapping", mapping_contract, hint, context_id, check_id)
                    if mapped is not BAD and operator is not None:
                        def operator_contract():
                            qualified._operator_contract(operator, item, mapped)
                            origins = dict(alias_state[1])
                            if mapping["kind"] != "identity":
                                origins[mapping["output_column"]] = origins[mapping["input_column"]]
                            operands = semantic._variables(operator)
                            require(len({origins[name] for name in operands}) == len(operands), "Distinct operator operands cannot alias the same generated column")
                        attempt("operator_contract", at + "/operator", operator_contract,
                                "Preserve the declared source functional, variables, adjustment set and units; disclose unavailable information.", context_id, check_id)

                if len(findings) > check_before:
                    row["status"] = "failed"
                elif alias_state is not BAD:
                    row["status"] = "metadata_checks_passed"
            summary["status"] = "failed" if len(findings) > before else "metadata_checks_passed"
    rows = [row for summary in summaries for row in summary["checks"]]
    return {"schema_version": 1, "kind": "qualified_author_metadata_preflight_v1",
            "status": "failed" if findings else "metadata_checks_passed", "findings": findings,
            "contexts": summaries, "counts": {"contexts_visited": len(summaries), "checks_visited": len(rows),
            "checks_passed": sum(row["status"] == "metadata_checks_passed" for row in rows),
            "checks_failed": sum(row["status"] == "failed" for row in rows),
            "checks_blocked": sum(row["status"] == "blocked" for row in rows), "findings": len(findings)},
            "scientific_validity": "not_assessed", "lifecycle_approval": "not_assessed", "limitations": LIMITATIONS[:]}


def load_metadata(bundle, candidate):
    """Read exactly the four allowed JSON files; no candidate traversal."""
    require(isinstance(candidate, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", candidate) is not None, "Use a candidate name, not a path")
    root = Path(bundle).resolve(strict=True)
    directory = root / "candidates" / candidate
    paths = {name: (root if name == "task.json" else directory) / name for name in FILES}
    payload, hashes = [], {}
    for name, path in paths.items():
        require(path.resolve(strict=True).is_relative_to(root), "Metadata path escapes the bundle")
        raw = path.read_bytes()
        hashes[str(path.resolve())] = hashlib.sha256(raw).hexdigest()
        payload.append(json.loads(raw.decode("utf-8-sig")))
    return payload, {name: str(path.resolve()) for name, path in paths.items()}, hashes


def preflight(bundle, candidate):
    payload, paths, hashes = load_metadata(bundle, candidate)
    report = preflight_metadata(*payload, source_paths=paths)
    report.update(input_sha256=hashes, dependency_sha256=dependency_fingerprints())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    try:
        report = preflight(args.bundle, args.candidate)
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "input_error", "message": str(error), "lifecycle_approval": "not_assessed"}))
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Static, source-bound provenance-review scaffold. Never executes candidate code.

Prepared before inspecting model outputs. Do not use --run until the controller
explicitly reports that all twenty construction attempts are finished and the
CONSTRUCTION_CLOSURE.json is sealed. Without --run this script reads no packet,
candidate, closure or response files.

The machine ledger is an aid for independent review, not a scientific verdict.
An author's provenance label, a numeric match and a static dictionary read each
have different evidential meanings; none verifies an assumption or transport.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


UNIT = Path(__file__).resolve().parent
ARTIFACTS = ("model_spec.json", "generator.py", "decision_record.json")
CASES = {"PNS": "PNS", "pns": "PNS", "lipids": "LIPID", "LIPID": "LIPID", "lipid": "LIPID"}
CLASSIFICATION_KEYS = ("classification", "provenance_class", "provenance_type", "type", "status", "kind", "basis")
PATH_KEYS = ("path", "paths", "json_path", "json_paths", "parameter_path", "parameter_paths", "model_spec_path", "model_spec_paths", "actual_json_path", "parameter", "name")
SOURCE_KEYS = ("source", "sources", "source_id", "source_ids", "source_pointer", "source_pointers", "source_ref", "source_refs", "source_reference", "source_references", "evidence", "evidence_id", "evidence_ids", "evidence_refs", "citation", "citations", "provenance")
ESTIMAND_KEYS = ("applicable_estimands", "requested_estimands", "estimands", "estimand", "analysis_id", "analysis_ids", "applicability")
ASSUMPTION_KEYS = ("assumptions", "unverified_assumptions", "bridge_assumptions", "transfer_assumptions", "limitations")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def beneath(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes allowed root: {path}")
    return resolved


def bound_read(path: Path, expected_hash: str, root: Path) -> bytes:
    path = beneath(path, root)
    raw = path.read_bytes()
    if sha(raw) != expected_hash:
        raise ValueError(f"Sealed artifact hash mismatch: {path.name}")
    return raw


def pointer(tokens: tuple[str, ...]) -> str:
    return "/" + "/".join(t.replace("~", "~0").replace("/", "~1") for t in tokens) if tokens else ""


def flatten(value: Any, tokens: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    if isinstance(value, dict):
        return [row for key, child in value.items() for row in flatten(child, tokens + (str(key),))]
    if isinstance(value, list):
        return [row for index, child in enumerate(value) for row in flatten(child, tokens + (str(index),))]
    return [(tokens, value)]


def strings(value: Any) -> list[str]:
    return [v for _, v in flatten(value) if isinstance(v, str)]


def field_values(record: dict, names: tuple[str, ...]) -> dict:
    return {name: record[name] for name in names if name in record}


def normalize_declared_path(raw: str) -> tuple[str, ...] | None:
    """Parse common JSON/dot path notation without evaluating expressions."""
    text = raw.strip()
    if text.startswith("/"):
        tokens = [p.replace("~1", "/").replace("~0", "~") for p in text.split("/")[1:]]
    else:
        text = re.sub(r"\[['\"]([^'\"]+)['\"]\]", r".\1", text)
        text = re.sub(r"\[(\d+)\]", r".\1", text)
        text = text.removeprefix("$.").removeprefix("$")
        if re.search(r"[\[\]\(\)\s]", text):
            return None
        tokens = [t for t in text.split(".") if t]
    # Declarations may address the returned object or the execution wrapper.
    while tokens and tokens[0] in {"spec", "model_spec", "model"}:
        tokens.pop(0)
    return tuple(tokens) if tokens else None


def resolve(value: Any, tokens: tuple[str, ...]) -> tuple[bool, Any]:
    current = value
    try:
        for token in tokens:
            current = current[int(token)] if isinstance(current, list) else current[token]
    except (KeyError, IndexError, TypeError, ValueError):
        return False, None
    return True, current


def declarations(decision: Any) -> tuple[list[dict], list[str]]:
    warnings = []
    if not isinstance(decision, dict):
        return [], ["decision_record is not a JSON object"]
    records = decision.get("parameter_provenance")
    if isinstance(records, list):
        converted = [r if isinstance(r, dict) else {"unparsed_record": r} for r in records]
        return converted, warnings
    if isinstance(records, dict):
        warnings.append("parameter_provenance is an object; keys retained as declared paths")
        return [{"path": k, **(v if isinstance(v, dict) else {"unparsed_record": v})} for k, v in records.items()], warnings
    return [], ["No parameter_provenance array found; all specification leaves require manual mapping"]


def ast_code_reads(code: str) -> dict:
    """Observe AST references only. Does not import, compile or run candidate code."""
    try:
        tree = ast.parse(code, filename="sealed_generator.py")
    except SyntaxError as error:
        return {"status": "syntax_error", "error": str(error), "reads": [], "numeric_literals": [], "limitations": ["Code could not be parsed"]}
    generate = next((n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "generate"), None)
    if generate is None or len(generate.args.args) < 2:
        return {"status": "generate_signature_unresolved", "reads": [], "numeric_literals": [], "limitations": ["Second positional generate argument not identified"]}
    spec_arg = generate.args.args[1].arg
    aliases: dict[str, tuple[str, ...]] = {spec_arg: ()}
    conflicting_aliases: set[str] = set()

    def access(node: ast.AST) -> tuple[str, ...] | None:
        if isinstance(node, ast.Name):
            return aliases.get(node.id)
        if isinstance(node, ast.Subscript):
            base = access(node.value)
            if base is not None and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, (str, int)):
                return base + (str(node.slice.value),)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get" and node.args:
            base = access(node.func.value)
            key = node.args[0]
            if base is not None and isinstance(key, ast.Constant) and isinstance(key.value, (str, int)):
                return base + (str(key.value),)
        return None

    # Scope-aware helper-call/data-flow analysis is intentionally not claimed.
    # Only aliases in generate are propagated; conflicting assignments are dropped.
    assignments = [n for n in ast.walk(generate) if isinstance(n, (ast.Assign, ast.AnnAssign))]
    for _ in range(len(assignments) + 1):
        changed = False
        for node in assignments:
            value = access(node.value) if node.value is not None else None
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if value is None:
                continue
            for target in targets:
                if not isinstance(target, ast.Name) or target.id in conflicting_aliases:
                    continue
                if target.id in aliases and aliases[target.id] != value:
                    conflicting_aliases.add(target.id)
                    aliases.pop(target.id, None)
                    changed = True
                elif target.id not in aliases:
                    aliases[target.id] = value
                    changed = True
        if not changed:
            break
    reads, seen = [], set()
    for node in ast.walk(generate):
        if not isinstance(node, (ast.Subscript, ast.Call)):
            continue
        path = access(node)
        kind = "static_key_reference"
        if path is None and isinstance(node, ast.Subscript):
            path = access(node.value)
            kind = "dynamic_key_reference"
        elif path is None and isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            path = access(node.func.value)
            kind = "dynamic_get_reference"
        if path is None or not path or path[0] != "model":
            continue
        record = {"model_path": pointer(path[1:]), "kind": kind, "line": node.lineno,
                  "column": node.col_offset, "source": (ast.get_source_segment(code, node) or "")[:240]}
        key = (record["model_path"], record["kind"], record["line"], record["column"])
        if key not in seen:
            reads.append(record)
            seen.add(key)
    literals = [{"value": node.value, "line": node.lineno, "column": node.col_offset,
                 "meaning": "not classified; may be mathematical, implementation or scientific"}
                for node in ast.walk(tree) if isinstance(node, ast.Constant)
                and isinstance(node.value, (int, float)) and not isinstance(node.value, bool)]
    return {"status": "parsed_without_execution", "spec_argument": spec_arg,
            "reads": sorted(reads, key=lambda r: (r["line"], r["column"])), "numeric_literals": literals,
            "conflicting_aliases": sorted(conflicting_aliases),
            "limitations": ["Static reference is not proof that a parameter affects returned data or a requested estimand",
                            "No scope-complete alias, helper-call, branching, loop or symbolic influence analysis",
                            "Missing references do not prove non-use; ancestor/dynamic references require manual inspection",
                            "Numeric code literals are unclassified candidates for manual inspection, not automatic violations"]}


def code_usage(path: tuple[str, ...], code_index: dict) -> dict:
    p = pointer(path)
    exact = [r for r in code_index["reads"] if r["model_path"] == p and r["kind"] == "static_key_reference"]
    parent = [r for r in code_index["reads"] if p.startswith(r["model_path"] + "/") and r["kind"] == "static_key_reference"]
    dynamic = [r for r in code_index["reads"] if r["kind"] != "static_key_reference" and (p == r["model_path"] or p.startswith(r["model_path"] + "/"))]
    if exact:
        status = "direct_static_reference_observed"
    elif dynamic:
        status = "dynamic_reference_possible_requires_review"
    elif parent:
        status = "ancestor_object_read_requires_review"
    else:
        status = "no_reference_observed_not_proof_unused"
    return {"status": status, "actual_effect_on_output_verified": False, "references": exact or dynamic or parent}


def evidence_index(evidence: dict) -> dict:
    identifiers = []
    for path, value in flatten(evidence):
        if path and path[-1] in {"id", "curator_source_id", "doi", "source_id", "source_doi"} and isinstance(value, str):
            identifiers.append({"identifier": value, "json_pointer": pointer(path), "source_context_pointer": pointer(path[:-1])})
    # Columnar tables preserve records; recover IDs for citation resolution only.
    def walk(obj: Any, path: tuple[str, ...] = ()) -> None:
        if isinstance(obj, dict):
            if obj.get("format") == "column_order_then_rows" and "id" in obj.get("columns", []):
                i = obj["columns"].index("id")
                for n, row in enumerate(obj["rows"]):
                    identifiers.append({"identifier": str(row[i]), "json_pointer": pointer(path + ("rows", str(n), str(i))),
                                        "source_context_pointer": pointer(path + ("rows", str(n)))})
            for k, v in obj.items():
                walk(v, path + (str(k),))
        elif isinstance(obj, list):
            for n, v in enumerate(obj):
                walk(v, path + (str(n),))
    walk(evidence)
    return {"identifiers": identifiers, "numeric_evidence_leaves": [{"json_pointer": pointer(p), "value": v} for p, v in flatten(evidence) if isinstance(v, (int, float)) and not isinstance(v, bool)]}


def source_matches(declared: dict, index: dict) -> list[dict]:
    joined = "\n".join(strings(declared))
    matches = []
    for entry in index["identifiers"]:
        ident = entry["identifier"]
        # Boundary matching is locational help only, never source/parameter verification.
        if ident and re.search(r"(?<![A-Za-z0-9_])" + re.escape(ident) + r"(?![A-Za-z0-9_])", joined):
            matches.append({**entry, "match_type": "exact_source_identifier_mentioned",
                            "operator_population_unit_adjustment_alignment_verified": False})
    return matches


def declaration_paths(record: dict, model: dict) -> list[dict]:
    candidates = []
    for raw in strings(field_values(record, PATH_KEYS)):
        parsed = normalize_declared_path(raw)
        if parsed is None:
            candidates.append({"declared": raw, "resolved": False, "reason": "path_not_parsed"})
            continue
        found, value = resolve(model, parsed)
        candidates.append({"declared": raw, "resolved": found, "model_path": pointer(parsed),
                           "tokens": list(parsed), "value": value if found else None})
    return candidates


def audit_candidate(record: dict, case: str, task: dict, evidence: dict, packet_hashes: dict) -> dict:
    construction_id = record["construction_id"]
    base = {"construction_id": construction_id, "case": case, "model_config": record.get("model_config"),
            "context": record.get("context"), "status": record["status"], "packet_hashes": packet_hashes,
            "independent_scientific_review_status": "pending_manual_static_review"}
    if record["status"] == "failed":
        return {**base, "failure_reason": record.get("failure_reason"), "parameters": [],
                "note": "Failed construction remains in denominator; no successful model inferred"}
    relative = Path(record["candidate_path"])
    if relative.is_absolute():
        raise ValueError("candidate_path must be unit-relative")
    candidate = beneath(UNIT / relative, UNIT / "candidates")
    content = {}
    for filename in ARTIFACTS:
        expected = record["files"].get(filename)
        if not isinstance(expected, str):
            raise ValueError(f"Missing sealed hash for {construction_id}/{filename}")
        raw = bound_read(candidate / filename, expected, UNIT / "candidates")
        content[filename] = raw.decode("utf-8-sig") if filename.endswith(".py") else json.loads(raw.decode("utf-8-sig"))
    wrapper = content["model_spec.json"]
    if not isinstance(wrapper, dict) or set(wrapper) != {"task", "model"} or wrapper["task"] != task or not isinstance(wrapper["model"], dict):
        raise ValueError(f"Candidate wrapper/task mismatch: {construction_id}")
    model = wrapper["model"]
    decision = content["decision_record.json"]
    records, warnings = declarations(decision)
    code = ast_code_reads(content["generator.py"])
    e_index = evidence_index(evidence)
    rows, covered = [], set()
    for i, declaration in enumerate(records):
        paths = declaration_paths(declaration, model)
        resolved = [p for p in paths if p["resolved"]]
        sources = field_values(declaration, SOURCE_KEYS)
        usage = []
        for path in resolved:
            tokens = tuple(path["tokens"])
            usage.append({"model_path": path["model_path"], **code_usage(tokens, code)})
            for child, _ in flatten(path["value"], tokens):
                covered.add(child)
        rows.append({"record_id": f"{construction_id}:declared:{i}", "declaration_index": i,
                     "parameter_paths": paths, "declared_classification": field_values(declaration, CLASSIFICATION_KEYS),
                     "independent_classification": "not_yet_verified",
                     "classification_basis": "Author label retained separately; independent source/operator/derivation audit required",
                     "declared_sources": sources, "source_identifier_matches": source_matches(sources, e_index),
                     "applicable_estimands_declared": field_values(declaration, ESTIMAND_KEYS),
                     "applicable_estimands_independently_verified": [], "code_usage": usage,
                     "declared_assumptions": field_values(declaration, ASSUMPTION_KEYS),
                     "unverified_items": ["Source population/measurement/operator/adjustment/scale/unit alignment",
                                          "Algebraic derivation and all dependence or transport assumptions",
                                          "Whether referenced parameter influences generated output and requested estimands"],
                     "original_declaration": declaration})
    undeclared = []
    for path, value in flatten(model):
        if path not in covered:
            undeclared.append({"model_path": pointer(path), "value": value,
                               "leaf_type": type(value).__name__, "scientific_parameter_status": "requires_review_may_be_metadata",
                               "independent_classification": "not_yet_verified", "code_usage": code_usage(path, code),
                               "unverified_items": ["No resolved parameter_provenance record covers this leaf", "Scientific role and source mapping require manual review"]})
    return {**base, "candidate_path": str(relative), "artifact_hashes": {f: record["files"][f] for f in ARTIFACTS},
            "warnings": warnings, "parameters": rows, "uncovered_specification_leaves": undeclared,
            "requested_estimands_declarations": decision.get("requested_estimands") if isinstance(decision, dict) else None,
            "code_static_index": code,
            "manual_review_required": True}


def markdown_report(ledger: dict) -> str:
    lines = ["# Parameter provenance: static review scaffold", "", "This is an unverified machine-assisted ledger. Author labels are declarations, not independent findings. No generator was imported or executed, and no raw response or hidden reasoning was read.", "",
             f"Closure SHA256: `{ledger['closure_sha256']}`. Attempts: {len(ledger['constructions'])}. Status counts: `{json.dumps(ledger['status_counts'], ensure_ascii=False)}`.", "",
             "Independent review must classify each scientific parameter as source-reported, algebra-derived, assumed, mixed, contradictory or unresolved; preserve any difference from the author's own label. An algebra-derived designation requires checking the formula and source operator. Source-reported values transported to a different population remain dependent on transfer assumptions. Exact numeric equality alone does not verify provenance.", ""]
    for construction in ledger["constructions"]:
        lines += [f"## {construction['construction_id']}", "", f"Case: {construction['case']}; status: {construction['status']}.", ""]
        if construction["status"] == "failed":
            lines += [f"Failure retained: {construction.get('failure_reason')}", ""]
            continue
        lines += [f"Declared parameter records: {len(construction['parameters'])}; uncovered specification leaves: {len(construction['uncovered_specification_leaves'])}. All independent provenance classifications remain pending.", "",
                  "| Record | Resolved parameter path | Author class | Static code observation | Source identifiers |", "|---|---|---|---|---|"]
        for row in construction["parameters"]:
            cells = [row["record_id"], ", ".join(p["model_path"] for p in row["parameter_paths"] if p["resolved"]) or "unresolved",
                     json.dumps(row["declared_classification"], ensure_ascii=False),
                     "; ".join(u["status"] for u in row["code_usage"]) or "unresolved",
                     ", ".join(m["identifier"] for m in row["source_identifier_matches"]) or "unresolved"]
            lines.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cells) + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Use only after explicit controller construction-complete signal")
    parser.add_argument("--closure", type=Path, default=UNIT / "CONSTRUCTION_CLOSURE.json")
    parser.add_argument("--output", type=Path, default=UNIT / "provenance_review")
    args = parser.parse_args()
    if not args.run:
        print("Scaffold only; no candidate, packet, closure or response files read. Await controller construction-complete signal before --run.")
        return
    closure_path = beneath(args.closure, UNIT)
    if closure_path.name != "CONSTRUCTION_CLOSURE.json":
        raise ValueError("Only the planned construction-closure file is admitted")
    raw = closure_path.read_bytes()
    closure = json.loads(raw.decode("utf-8-sig"))
    records = closure["records"]
    if len(records) != 20 or len({r["construction_id"] for r in records}) != 20:
        raise ValueError("Closure must account for twenty unique construction attempts")
    if any(r["status"] not in {"sealed", "failed"} for r in records):
        raise ValueError("Construction still in progress or unsupported closure status")
    # Fixed packet files alone are allowed here. No directory search or raw-capture traversal.
    manifest_path = UNIT / "packets/ASSEMBLY_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    packets = {}
    for case in ("PNS", "LIPID"):
        entries = {Path(f["path"]).name: f for f in manifest["cases"][case]["files"]}
        packet = {}
        hashes = {}
        for filename in ("task.json", "requested_analyses.json", "evidence.json"):
            entry = entries[filename]
            data = bound_read(UNIT / "packets" / case / filename, entry["sha256"], UNIT / "packets")
            packet[filename] = json.loads(data.decode("utf-8-sig"))
            hashes[filename] = entry["sha256"]
        packets[case] = {"objects": packet, "hashes": hashes}
    constructions = []
    for record in records:
        case = CASES.get(record["case_id"])
        if case is None:
            raise ValueError("Unknown case in closure")
        packet = packets[case]
        if record.get("task_sha256") != packet["hashes"]["task.json"]:
            raise ValueError(f"Closure task hash mismatch: {record['construction_id']}")
        constructions.append(audit_candidate(record, case, packet["objects"]["task.json"], packet["objects"]["evidence.json"], packet["hashes"]))
    ledger = {"schema_version": 1, "status": "static_ledger_pending_independent_review",
              "closure_sha256": sha(raw), "review_script_sha256": sha(Path(__file__).read_bytes()),
              "allowed_candidate_artifacts": list(ARTIFACTS), "raw_responses_read": False,
              "candidate_code_executed": False, "author_labels_independently_verified": False,
              "status_counts": dict(Counter(r["status"] for r in records)), "constructions": constructions}
    output = beneath(args.output, UNIT)
    output.mkdir(parents=True, exist_ok=True)
    for filename in ("static_parameter_provenance.json", "STATIC_PARAMETER_PROVENANCE.md"):
        if (output / filename).exists():
            raise ValueError(f"Refusing to overwrite existing review artifact: {filename}")
    json_dump(output / "static_parameter_provenance.json", ledger)
    (output / "STATIC_PARAMETER_PROVENANCE.md").write_text(markdown_report(ledger), encoding="utf-8", newline="\n")
    print(json.dumps({"status": ledger["status"], "constructions": len(constructions), "status_counts": ledger["status_counts"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()

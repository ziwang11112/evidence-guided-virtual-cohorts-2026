"""Target-free review helpers, never a scientific-validity certificate.

No generator imports/execution, expression eval, network, clinical targets, or
case-specific numerical rules occur here. Static warnings are intentionally
incomplete. A model-proposed contract is a declaration, not verified evidence.
"""
from __future__ import annotations

import ast
import copy
import json
import math
from dataclasses import dataclass, field
from typing import Any

MAX_CODE_BYTES = 200_000
MAX_AST_NODES = 30_000
MAX_CONTRACT_BYTES = 100_000
MAX_ITEMS = 40
MAX_TEXT = 2_000


def _arr(items, maximum=MAX_ITEMS):
    return {"type": "array", "items": items, "maxItems": maximum}


def _obj(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


_TEXT = {"type": "string", "maxLength": MAX_TEXT}
_ID = {"type": "string", "minLength": 1, "maxLength": 200}
_IDS = _arr(_ID)
_BASIS = {"type": "string", "enum": ["reported", "derived", "assumed", "unresolved"]}
_DEPENDENCY = _obj({"parameter": _ID, "basis": _BASIS, "source_ids": _IDS,
                    "source_operator": _TEXT, "source_adjustment": _IDS,
                    "support": _TEXT, "uncertainty": _TEXT, "code_locator": _TEXT})
REVIEW_CONTRACT_SCHEMA = _obj({
    "schema_version": {"type": "integer", "enum": [1]},
    "mathematical_review": _arr(_obj({
        "variable": _ID, "support": _TEXT,
        "moment_assessment": {"type": "string", "enum": ["finite_claim", "infinite_claim", "unresolved"]},
        "justification": _TEXT, "code_locator": _TEXT, "source_ids": _IDS})),
    "physiological_review": {"type": "string", "minLength": 1, "maxLength": MAX_TEXT},
    "physiological_rules": _arr(_obj({
        "rule_id": _ID, "coefficients": {"type": "object", "minProperties": 1,
            "maxProperties": MAX_ITEMS, "additionalProperties": {"type": "number"}},
        "operator": {"type": "string", "enum": ["le", "ge", "eq"]},
        "bound": {"type": "number"}, "atol": {"type": "number", "minimum": 0},
        "rtol": {"type": "number", "minimum": 0, "maximum": 1},
        "basis": {"type": "string", "enum": ["reported", "derived", "assumed"]},
        "source_ids": _IDS, "rationale": _TEXT})),
    "joint_analyses": _arr(_obj({
        "analysis_id": _ID, "variables": _IDS, "adjustment": _IDS,
        "operator": _TEXT, "dependencies": _arr(_DEPENDENCY)})),
})


def _schema_errors(value, schema, path="contract"):
    errors = []
    typ = schema.get("type")
    valid_type = {
        "object": lambda x: type(x) is dict,
        "array": lambda x: type(x) is list,
        "string": lambda x: type(x) is str,
        "number": lambda x: type(x) in (int, float) and math.isfinite(x),
        "integer": lambda x: type(x) is int,
    }.get(typ, lambda _: False)
    if not valid_type(value):
        return [f"{path}: expected {typ} (finite JSON numbers only)"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: unsupported value")
    if typ == "object":
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: missing")
        if len(value) > schema.get("maxProperties", MAX_ITEMS + 20):
            errors.append(f"{path}: too many properties")
        if len(value) < schema.get("minProperties", 0):
            errors.append(f"{path}: too few properties")
        for key, item in value.items():
            if type(key) is not str or len(key) > 200:
                errors.append(f"{path}: invalid property name")
                continue
            if key in props:
                errors += _schema_errors(item, props[key], path + "." + key)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}.{key}: unexpected property")
            elif type(schema.get("additionalProperties")) is dict:
                errors += _schema_errors(item, schema["additionalProperties"], path + "." + key)
    elif typ == "array":
        if len(value) > schema.get("maxItems", MAX_ITEMS):
            errors.append(f"{path}: too many items")
        for i, item in enumerate(value[:MAX_ITEMS + 1]):
            errors += _schema_errors(item, schema["items"], f"{path}[{i}]")
    elif typ == "string":
        if len(value) > schema.get("maxLength", MAX_TEXT) or len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: invalid text length")
    elif typ in ("number", "integer"):
        if value < schema.get("minimum", -math.inf) or value > schema.get("maximum", math.inf):
            errors.append(f"{path}: out of allowed range")
    return errors


def _columns(task):
    if type(task) is not dict or type(task.get("columns")) is not list:
        raise ValueError("Task columns must be a list")
    names = []
    generated = []
    for col in task["columns"]:
        if type(col) is not dict or type(col.get("name")) is not str:
            raise ValueError("Each task column needs a name")
        name = col["name"]
        if name in names:
            raise ValueError("Duplicate task column")
        names.append(name)
        if col.get("role") != "identifier" and col.get("kind", "number") in ("number", "integer"):
            generated.append(name)
    if not names:
        raise ValueError("No task columns")
    return names, generated


def validate_contract(contract: dict, task: dict) -> dict:
    """Validate bounded declaration structure; source correctness stays unverified.

    task.requested_analysis_ids optionally names the known requested analyses.
    Missing IDs are reported as incomplete coverage, never inferred as success.
    """
    errors, warnings = [], []
    try:
        serialized = json.dumps(contract, allow_nan=False, ensure_ascii=False).encode("utf-8")
        if len(serialized) > MAX_CONTRACT_BYTES:
            return {"valid": False, "status": "invalid", "errors": ["Contract byte limit exceeded"], "warnings": [], "coverage": {}}
        errors += _schema_errors(contract, REVIEW_CONTRACT_SCHEMA)
    except (TypeError, ValueError, OverflowError, RecursionError):
        return {"valid": False, "status": "invalid", "errors": ["Contract must be finite bounded JSON"], "warnings": [], "coverage": {}}
    try:
        names, expected_math = _columns(task)
    except ValueError as exc:
        errors.append(str(exc))
        names, expected_math = [], []
    if errors:
        return {"valid": False, "status": "invalid", "errors": errors, "warnings": [], "coverage": {}}
    known = set(names)
    if not contract["physiological_review"].strip():
        errors.append("physiological_review: nonblank scope or unresolved/inapplicable rationale required")
    for section, id_key in [("mathematical_review", "variable"), ("physiological_rules", "rule_id"), ("joint_analyses", "analysis_id")]:
        ids = [x[id_key] for x in contract[section]]
        if len(ids) != len(set(ids)):
            errors.append(section + ": duplicate identifiers")
    for entry in contract["mathematical_review"]:
        if entry["variable"] not in known:
            errors.append("mathematical_review: unknown task variable " + entry["variable"])
        for key in ("support", "justification", "code_locator"):
            if not entry[key].strip():
                errors.append(entry["variable"] + ": nonblank " + key + " required, including an explanation when unresolved")
    for rule in contract["physiological_rules"]:
        for name in rule["coefficients"]:
            if name not in known:
                errors.append(rule["rule_id"] + ": unknown coefficient variable " + name)
        if not any(rule["coefficients"].values()):
            errors.append(rule["rule_id"] + ": identically zero rule is not an informative physiological check")
        if rule["basis"] == "reported" and not rule["source_ids"]:
            errors.append(rule["rule_id"] + ": reported rule requires source_ids")
        if rule["basis"] == "assumed":
            warnings.append(rule["rule_id"] + ": author-assumed rule, not certified physiological truth")
    for analysis in contract["joint_analyses"]:
        for name in analysis["variables"] + analysis["adjustment"]:
            if name not in known:
                errors.append(analysis["analysis_id"] + ": unknown target variable " + name)
        if len(analysis["variables"]) != len(set(analysis["variables"])) or len(analysis["adjustment"]) != len(set(analysis["adjustment"])):
            errors.append(analysis["analysis_id"] + ": duplicate variables or adjustment entries")
        if not analysis["dependencies"]:
            warnings.append(analysis["analysis_id"] + ": dependencies not supplied; identification not assessed")
        for dep in analysis["dependencies"]:
            if dep["basis"] == "reported" and not dep["source_ids"]:
                errors.append(analysis["analysis_id"] + "/" + dep["parameter"] + ": reported dependency requires source_ids")
            if dep["basis"] in ("assumed", "unresolved"):
                warnings.append(analysis["analysis_id"] + "/" + dep["parameter"] + ": joint analysis depends on " + dep["basis"] + " information")
            elif not dep["source_operator"].strip() or not dep["support"].strip():
                warnings.append(analysis["analysis_id"] + "/" + dep["parameter"] + ": source/operator applicability incompletely stated")
            if set(dep["source_adjustment"]) != set(analysis["adjustment"]) and dep["basis"] in ("reported", "derived"):
                warnings.append(analysis["analysis_id"] + "/" + dep["parameter"] + ": source and requested adjustment sets differ; a transport/derivation justification is needed")
    requirements = task.get("analysis_requirements")
    if requirements is not None:
        if type(requirements) is not list or len(requirements) > MAX_ITEMS:
            errors.append("task.analysis_requirements must be a bounded list")
            requirements = []
        seen = set()
        for req in requirements:
            if type(req) is not dict or type(req.get("analysis_id")) is not str or type(req.get("variables")) is not list or type(req.get("adjustment")) is not list or type(req.get("operator")) is not str:
                errors.append("Malformed task.analysis_requirements entry")
                continue
            if req["analysis_id"] in seen:
                errors.append("Duplicate task analysis requirement")
            seen.add(req["analysis_id"])
            if any(type(x) is not str or x not in known for x in req["variables"] + req["adjustment"]):
                errors.append("Unknown variable in task analysis requirement")
                continue
            matches = [a for a in contract["joint_analyses"] if a["analysis_id"] == req["analysis_id"]]
            for declaration in matches:
                if set(req["variables"]) != set(declaration["variables"]):
                    errors.append(req["analysis_id"] + ": declared variables do not match request")
                if set(req["adjustment"]) != set(declaration["adjustment"]):
                    errors.append(req["analysis_id"] + ": declared adjustment set does not match request")
                if req["operator"] != declaration["operator"]:
                    errors.append(req["analysis_id"] + ": declared operator does not match request")
    expected = task.get("requested_analysis_ids")
    if expected is None and requirements is not None:
        expected = [r["analysis_id"] for r in requirements if type(r) is dict and type(r.get("analysis_id")) is str]
    if expected is not None and (type(expected) is not list or any(type(x) is not str for x in expected) or len(expected) != len(set(expected))):
        errors.append("task.requested_analysis_ids must be unique strings")
        expected = None
    present = [a["analysis_id"] for a in contract["joint_analyses"]]
    math_present = [a["variable"] for a in contract["mathematical_review"]]
    coverage = {
        "mathematical_variables_declared": math_present,
        "mathematical_variables_not_declared": sorted(set(expected_math) - set(math_present)),
        "physiological_rule_count": len(contract["physiological_rules"]),
        "physiological_review": contract["physiological_review"],
        "physiology_coverage": "author_selected_rules_only" if contract["physiological_rules"] else "not_assessed",
        "analyses_declared": present,
        "analyses_without_dependencies": [a["analysis_id"] for a in contract["joint_analyses"] if not a["dependencies"]],
        "analyses_not_declared": sorted(set(expected) - set(present)) if expected is not None else None,
        "analysis_coverage": "complete_declarations_only" if expected is not None and set(expected).issubset(present) else "incomplete" if expected is not None else "expected_analyses_not_supplied",
    }
    return {"valid": not errors, "status": "invalid" if errors else "valid", "errors": errors,
            "warnings": warnings, "coverage": coverage,
            "verification_boundary": "Declaration consistency only; source extraction, biological meaning, mathematical proof and population transfer are not certified."}


@dataclass
class _Info:
    const: float | None = None
    normal: bool = False
    heavy: dict[int, float | None] = field(default_factory=dict)
    caps: tuple[int, ...] = ()
    unknown: bool = False


def _combine(a, b, left=1.0, right=1.0):
    out = _Info(normal=a.normal or b.normal, caps=tuple(sorted(set(a.caps + b.caps))), unknown=a.unknown or b.unknown)
    for info, factor in [(a, left), (b, right)]:
        for key, weight in info.heavy.items():
            val = None if weight is None or factor is None else weight * factor
            if key in out.heavy:
                old = out.heavy[key]
                val = None if old is None or val is None else old + val
            out.heavy[key] = val
    out.heavy = {k: v for k, v in out.heavy.items() if v != 0.0}
    if a.const is not None and b.const is not None and left is not None and right is not None:
        val = left * a.const + right * b.const
        out.const = val if math.isfinite(val) else None
    return out


class _Scanner:
    def __init__(self, tree):
        self.tree = tree
        self.env = {}
        self.findings = []
        self.unsupported = set()
        self.aliases = {}

    def add(self, code, node, detail, sources=(), severity="review"):
        finding = {"code": code, "line": getattr(node, "lineno", None), "severity": severity,
                   "detail": detail, "dependency_lines": sorted(set(sources)), "proof": False}
        finding["expression"] = ast.unparse(node)[:300]
        if finding not in self.findings:
            self.findings.append(finding)

    @staticmethod
    def name(node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def expr(self, node):
        if node is None:
            return _Info(unknown=True)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            try:
                return _Info(const=float(node.value)) if math.isfinite(node.value) else _Info(unknown=True)
            except (ValueError, OverflowError):
                return _Info(unknown=True)
        if isinstance(node, ast.Name):
            return copy.deepcopy(self.env.get(node.id, _Info(unknown=True)))
        if isinstance(node, ast.UnaryOp):
            value = self.expr(node.operand)
            if isinstance(node.op, ast.USub):
                return _combine(_Info(const=0), value, 1, -1)
            return value
        if isinstance(node, ast.BinOp):
            a, b = self.expr(node.left), self.expr(node.right)
            if isinstance(node.op, ast.Add):
                return _combine(a, b)
            if isinstance(node.op, ast.Sub):
                return _combine(a, b, 1, -1)
            if isinstance(node.op, ast.Mult):
                if a.const is not None:
                    return _combine(_Info(const=0), b, 0, a.const)
                if b.const is not None:
                    return _combine(a, _Info(const=0), b.const, 0)
                return _combine(a, b, None, None)
            if isinstance(node.op, ast.Div) and b.const not in (None, 0):
                return _combine(a, _Info(const=0), 1 / b.const, 0)
            out = _combine(a, b, None, None)
            out.unknown = True
            return out
        if isinstance(node, ast.Subscript):
            return self.expr(node.value)
        if isinstance(node, ast.Call):
            func = self.name(node.func)
            func = self.aliases.get(func, func)
            args = [self.expr(x) for x in node.args]
            kwargs = {x.arg: self.expr(x.value) for x in node.keywords if x.arg}
            first = args[0] if args else _Info(unknown=True)
            if func in ("normal", "standard_normal", "multivariate_normal"):
                return _Info(normal=True)
            if func == "lognormal":
                return _Info(heavy={node.lineno: 1.0})
            if func in ("clip",):
                lo = args[1] if len(args) > 1 else kwargs.get("a_min", kwargs.get("min", _Info()))
                hi = args[2] if len(args) > 2 else kwargs.get("a_max", kwargs.get("max", _Info()))
                if lo.const is not None and hi.const is not None and lo.const <= hi.const:
                    self.add("FINITE_LITERAL_CLIP", node, "Finite literal clipping was recognized locally. This is a model choice, not a proof that all returned variables have acceptable tails.", first.heavy, "information")
                    return _Info(caps=tuple(sorted(set(first.caps + (node.lineno,)))))
                self.add("UNRESOLVED_CLIP_BOUNDS", node, "Clipping bounds could not both be resolved as finite literals; do not assume this certifies a bounded output.", first.heavy)
                first.unknown = True
                return first
            if func in ("exp", "expm1"):
                if first.heavy:
                    positive = [k for k, v in first.heavy.items() if v is None or v > 0]
                    if positive:
                        self.add("EXP_OF_HEAVY_TAINT", node,
                            "An exponential depends positively or with unresolved sign on a lognormal/exponentiated-normal-like expression. Inspect exact support, coefficients, dependence and any subsequent clipping; positive exponential-of-lognormal terms can lack finite moments. This heuristic is not a divergence proof.", positive)
                    else:
                        self.add("NEGATIVE_HEAVY_EXPONENT", node,
                            "Recognized heavy-tainted terms have negative coefficients in this local exponential; the usual positive exponential-of-lognormal warning does not follow. Other terms and whole-law validity remain unproved.", first.heavy, "information")
                    return _Info(heavy={node.lineno: 1.0}, caps=first.caps, unknown=True)
                if first.caps:
                    self.add("EXP_AFTER_LITERAL_CLIP", node,
                        "Exponential input is locally clipped at recognized finite bounds. Review cap dependence, units and downstream operations; no population-moment certificate is issued.", first.caps, "information")
                    return _Info(caps=first.caps, unknown=first.unknown)
                if first.normal:
                    return _Info(heavy={node.lineno: 1.0})
                if first.const is not None and first.const < 700:
                    value = math.exp(first.const) - (1 if func == "expm1" else 0)
                    return _Info(const=value)
                return _Info(unknown=True)
            if func in ("log", "log1p") and first.heavy:
                return _Info(normal=True, caps=first.caps, unknown=True)
            if func in ("array", "asarray", "copy", "astype", "reshape", "ravel", "round"):
                return first if args else self.expr(node.func.value) if isinstance(node.func, ast.Attribute) else _Info(unknown=True)
            out = _Info(unknown=True)
            for value in args + list(kwargs.values()):
                out = _combine(out, value, None, None)
            if func:
                self.unsupported.add(func)
            return out
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            out = _Info()
            for child in node.elts:
                out = _combine(out, self.expr(child), None, None)
            return out
        if isinstance(node, ast.IfExp):
            return _combine(self.expr(node.body), self.expr(node.orelse), None, None)
        return _Info(unknown=True)

    def assign(self, target, value):
        if isinstance(target, ast.Name):
            self.env[target.id] = copy.deepcopy(value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for sub in target.elts:
                self.assign(sub, value)

    def statements(self, body):
        for node in body:
            if isinstance(node, ast.ImportFrom):
                for entry in node.names:
                    self.aliases[entry.asname or entry.name] = entry.name
            elif isinstance(node, ast.Assign):
                val = self.expr(node.value)
                for target in node.targets:
                    self.assign(target, val)
                    if isinstance(target, ast.Name) and isinstance(node.value, (ast.Name, ast.Attribute)):
                        rhs = self.name(node.value)
                        self.aliases[target.id] = self.aliases.get(rhs, rhs)
            elif isinstance(node, ast.AnnAssign):
                self.assign(node.target, self.expr(node.value))
            elif isinstance(node, ast.AugAssign):
                val = self.expr(ast.BinOp(left=node.target, op=node.op, right=node.value))
                self.assign(node.target, val)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                old = copy.deepcopy(self.env)
                self.statements(node.body)
                self.env = old
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                self.unsupported.add("control_flow_not_proven")
                # Single bounded static traversal; this is not path-sensitive execution.
                before = copy.deepcopy(self.env)
                self.statements(node.body)
                after = copy.deepcopy(self.env)
                self.env = before
                self.statements(getattr(node, "orelse", []))
                other = copy.deepcopy(self.env)
                merged = {}
                for key in set(before) | set(after) | set(other):
                    merged[key] = _combine(after.get(key, before.get(key, _Info(unknown=True))),
                                           other.get(key, before.get(key, _Info(unknown=True))), None, None)
                self.env = merged
                for handler in getattr(node, "handlers", []):
                    self.statements(handler.body)
                self.statements(getattr(node, "finalbody", []))
            elif isinstance(node, (ast.Expr, ast.Return)):
                self.expr(node.value)


def inspect_program(code: str) -> dict:
    """Bounded static hints only. Absence of warnings is never a safety proof."""
    limitations = ["No program execution or target-data access.",
        "Heuristic, intraprocedural approximate dataflow; arbitrary Python, nonlinear transforms, custom helpers, branches and rejection laws are not formally verified.",
        "No warning does not prove finite moments, valid support, correct source extraction or physiological validity.",
        "A local warning may precede later clipping or be unreachable; inspect actual returned laws and dependencies before a mathematical conclusion."]
    if type(code) is not str or len(code.encode("utf-8")) > MAX_CODE_BYTES:
        return {"status": "unavailable", "findings": [], "limitations": limitations, "reason": "Code missing or byte limit exceeded"}
    try:
        tree = ast.parse(code)
        if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
            raise ValueError("AST node limit exceeded")
        scanner = _Scanner(tree)
        scanner.statements(tree.body)
    except (SyntaxError, ValueError, RecursionError, MemoryError, OverflowError) as exc:
        return {"status": "unavailable", "findings": [], "limitations": limitations, "reason": type(exc).__name__}
    warnings = [f for f in scanner.findings if f["severity"] == "review"]
    return {"status": "heuristic_review_required" if warnings else "no_pattern_detected_not_certified",
            "findings": scanner.findings, "unresolved_function_names": sorted(scanner.unsupported),
            "limitations": limitations, "mathematical_validity": "not_certified"}


def inspect_trial(frame, contract: dict, task: dict) -> dict:
    """Inspect existing generated trial rows, never executes candidate code.

    Tolerance for sum(coefficient*column) op bound is
    atol + rtol*max(abs(bound), abs(sum(coefficient*column))). Nonfinite rows
    are unavailable, never silently counted as satisfying a rule.
    """
    validation = validate_contract(contract, task)
    if not validation["valid"]:
        return {"status": "invalid_contract", "contract_validation": validation}
    result = {"status": "checked", "contract_validation": validation,
              "mathematical_review": {"status": "author_claims_not_certified", "declarations": contract["mathematical_review"]},
              "joint_relations": {"status": "declarations_only_not_target_validated", "analyses": contract["joint_analyses"], "coverage": validation["coverage"]},
              "physiology": {"status": "evaluated" if contract["physiological_rules"] else "not_assessed", "rules": [],
                   "author_review": contract["physiological_review"],
                   "scope": "Only the Agent-declared inequalities on this finite trial. Source correctness, universal support and clinical relevance are unverified."}}
    try:
        import numpy as np
        n = len(frame)
        columns = list(frame.columns)
        if n < 1 or len(columns) != len(set(columns)):
            raise ValueError("Empty table or duplicate columns")
    except Exception as exc:
        result["status"] = "unavailable"
        result["physiology"]["status"] = "unavailable"
        result["physiology"]["reason"] = type(exc).__name__
        return result
    result["rows"] = n
    for rule in contract["physiological_rules"]:
        base = {"rule_id": rule["rule_id"], "basis": rule["basis"], "source_ids": rule["source_ids"],
                "operator": rule["operator"], "coefficients": rule["coefficients"], "bound": rule["bound"],
                "atol": rule["atol"], "rtol": rule["rtol"], "rationale": rule["rationale"], "n_rows": n,
                "unit_verification": "Coefficients, bound and tolerances are Agent-declared. Numerical evaluation does not verify dimensional conversions or biological meaning."}
        try:
            arrays = [np.asarray(frame[name]) for name in rule["coefficients"]]
            if any(x.dtype.kind not in ("i", "u", "f") for x in arrays):
                raise ValueError("Rule columns must have genuine numeric, non-boolean dtype")
            arrays = [x.astype(float) for x in arrays]
            if any(x.shape != (n,) for x in arrays):
                raise ValueError("Non-vector column")
            with np.errstate(all="ignore"):
                lhs = np.zeros(n, dtype=float)
                finite = np.ones(n, dtype=bool)
                for (name, coefficient), array in zip(rule["coefficients"].items(), arrays):
                    finite &= np.isfinite(array)
                    lhs += coefficient * array
                tolerance = rule["atol"] + rule["rtol"] * np.maximum(abs(rule["bound"]), np.abs(lhs))
                difference = lhs - rule["bound"]
                finite &= np.isfinite(lhs) & np.isfinite(tolerance) & np.isfinite(difference)
                if rule["operator"] == "le":
                    signed_violation = difference
                elif rule["operator"] == "ge":
                    signed_violation = -difference
                else:
                    signed_violation = np.abs(difference)
                excess = np.maximum(signed_violation[finite] - tolerance[finite], 0)
                count = int(np.count_nonzero(excess > 0))
            valid_n = int(finite.sum())
            base.update(status="evaluated" if valid_n == n else "partly_unavailable" if valid_n else "unavailable",
                        evaluated_rows=valid_n, nonfinite_or_arithmetic_unavailable_rows=n-valid_n,
                        violating_rows=count, violation_fraction=count/valid_n if valid_n else None,
                        max_violation_beyond_tolerance=float(excess.max()) if valid_n else None,
                        passes_this_trial=bool(valid_n == n and count == 0))
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            base.update(status="unavailable", reason=type(exc).__name__, passes_this_trial=False)
        result["physiology"]["rules"].append(base)
    if any(r["status"] != "evaluated" for r in result["physiology"]["rules"]):
        result["physiology"]["status"] = "partly_unavailable"
    # Fails closed if an implementation mistake leaks a NaN/infinity into JSON.
    json.dumps(result, allow_nan=False)
    return result

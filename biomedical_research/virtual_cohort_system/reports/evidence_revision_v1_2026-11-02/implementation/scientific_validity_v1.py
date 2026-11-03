"""Conservative analytical moment checks for a small, declared stochastic AST.

This module neither executes nor certifies generator Python.  A passing moment
check still needs independent code/law correspondence and analysis-condition
review.  There is deliberately no empirical tail test or universal proof claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import math
from typing import Any


VERSION = "scientific_validity_v1"
REPORT_VERSION = "scientific_validity_report_v1"
PASS, FAIL, UNRESOLVED = "pass", "fail", "unresolved"


class DeclarationError(ValueError):
    """A malformed or out-of-domain declaration; never an accepted law."""


@dataclass(frozen=True)
class Node:
    op: str
    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)
    children: tuple["Node", ...] = ()
    name: str = ""
    source: str = ""
    weights: tuple[Fraction, ...] = ()


@dataclass(frozen=True)
class Traits:
    real: bool
    below: bool = False
    above: bool = False
    nonnegative: bool = False
    nonpositive: bool = False
    constant: Fraction | None = None
    nonzero_possible: bool = False
    roots: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Proof:
    status: str
    reason: str


def _number(value: Any, path: str) -> Fraction:
    if type(value) not in (int, float):
        raise DeclarationError(f"{path}: expected a finite number, excluding bool")
    try:
        finite = math.isfinite(value)
    except (OverflowError, ValueError):
        finite = False
    if not finite:
        raise DeclarationError(f"{path}: nonfinite or out-of-range number")
    # Interpret the shortest decimal representation exactly.  This also avoids
    # rounding a gamma threshold multiplication onto the wrong side of one.
    return Fraction(str(value))


def _json_guard(value: Any, depth: int = 0, budget: list[int] | None = None) -> None:
    if budget is None:
        budget = [12000]
    budget[0] -= 1
    if depth > 64 or budget[0] < 0:
        raise DeclarationError("declaration exceeds depth/size limits")
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise DeclarationError("JSON object keys must be strings")
            _json_guard(item, depth + 1, budget)
    elif type(value) is list:
        for item in value:
            _json_guard(item, depth + 1, budget)
    elif type(value) in (int, float):
        _number(value, "numeric value")
    elif type(value) is not str:
        raise DeclarationError("only JSON objects, arrays, strings and finite numbers are accepted")


def _keys(obj: dict, expected: set[str], path: str) -> None:
    if set(obj) != expected:
        raise DeclarationError(f"{path}: expected keys {sorted(expected)}")


def _name(value: Any, path: str) -> str:
    if type(value) is not str or not value or len(value) > 200:
        raise DeclarationError(f"{path}: expected a nonempty string of at most 200 characters")
    return value


def _parse(raw: Any, source: str, path: str, in_mixture: bool = False) -> Node:
    if type(raw) is not dict or type(raw.get("op")) is not str:
        raise DeclarationError(f"{path}: expected a law object with string op")
    op = raw["op"]
    params = {
        "constant": ("value",), "normal": ("mean", "sd"),
        "lognormal": ("log_mean", "log_sd"), "gamma": ("shape", "scale"),
        "uniform": ("lower", "upper"), "bernoulli": ("p",),
        "discrete_uniform": ("lower", "upper"),
    }
    if op in params:
        names = params[op]
        _keys(raw, {"op", *names}, path)
        vals = [_number(raw[k], f"{path}.{k}") for k in names]
        a, b = vals[0], vals[1] if len(vals) == 2 else Fraction(0)
        if op in ("normal", "lognormal") and b < 0:
            raise DeclarationError(f"{path}: standard deviation must be nonnegative")
        if op == "gamma" and (a <= 0 or b <= 0):
            raise DeclarationError(f"{path}: gamma shape and scale must be strictly positive")
        if op in ("uniform", "discrete_uniform") and a > b:
            raise DeclarationError(f"{path}: lower must not exceed upper")
        if op == "discrete_uniform" and (a.denominator != 1 or b.denominator != 1):
            raise DeclarationError(f"{path}: discrete uniform bounds must be integer-valued")
        if op == "bernoulli" and not 0 <= a <= 1:
            raise DeclarationError(f"{path}: Bernoulli p must be between zero and one inclusive")
        return Node(op, a, b, source=source)
    if op == "ref":
        _keys(raw, {"op", "name"}, path)
        if in_mixture:
            raise DeclarationError(f"{path}: mixture branches cannot reference external variables")
        return Node(op, name=_name(raw["name"], f"{path}.name"))
    if op in ("affine", "clip", "exp"):
        names = {"op", "input"}
        if op == "affine":
            names |= {"scale", "shift"}
        if op == "clip":
            names |= {"lower", "upper"}
        _keys(raw, names, path)
        child = _parse(raw["input"], source, f"{path}.input", in_mixture)
        if op == "affine":
            a, b = _number(raw["scale"], path), _number(raw["shift"], path)
        elif op == "clip":
            a, b = _number(raw["lower"], path), _number(raw["upper"], path)
            if a > b:
                raise DeclarationError(f"{path}: clip lower must not exceed upper")
        else:
            a = b = Fraction(0)
        return Node(op, a, b, (child,), source=source)
    if op in ("sum", "product"):
        key = "terms" if op == "sum" else "factors"
        _keys(raw, {"op", key}, path)
        items = raw[key]
        if type(items) is not list or not 1 <= len(items) <= 64:
            raise DeclarationError(f"{path}.{key}: expected 1 to 64 expressions")
        return Node(op, children=tuple(_parse(x, source, f"{path}.{key}[{i}]", in_mixture)
                                      for i, x in enumerate(items)), source=source)
    if op == "mixture":
        _keys(raw, {"op", "components"}, path)
        items = raw["components"]
        if type(items) is not list or not 1 <= len(items) <= 64:
            raise DeclarationError(f"{path}: expected 1 to 64 mixture components")
        weights, children = [], []
        for i, item in enumerate(items):
            if type(item) is not dict:
                raise DeclarationError(f"{path}.components[{i}]: expected an object")
            _keys(item, {"weight", "law"}, path)
            weight = _number(item["weight"], path)
            if weight < 0:
                raise DeclarationError(f"{path}: mixture weights must be nonnegative")
            weights.append(weight)
            children.append(_parse(item["law"], source, f"{path}.components[{i}].law", True))
        if sum(weights) <= 0:
            raise DeclarationError(f"{path}: at least one mixture weight must be positive")
        return Node(op, children=tuple(children), weights=tuple(weights), source=source)
    # An unknown operation is opaque, not an executable extension point.
    return Node("unsupported", name=op, source=source)


def _refs(node: Node) -> set[str]:
    return ({node.name} if node.op == "ref" else set()).union(*(_refs(c) for c in node.children))


def _constant(value: Fraction) -> Traits:
    return Traits(True, True, True, value >= 0, value <= 0, value, value != 0)


class _Engine:
    def __init__(self, variables: dict[str, Node], independence: list[frozenset[str]]):
        self.variables = variables
        self.independence = independence

    @lru_cache(maxsize=12000)
    def traits(self, node: Node) -> Traits:
        op, a, b = node.op, node.a, node.b
        if op == "unsupported":
            return Traits(False)
        if op == "ref":
            return self.traits(self.variables[node.name])
        if op == "constant":
            return _constant(a)
        roots = frozenset({node.source})
        if op == "normal":
            return _constant(a) if b == 0 else Traits(True, nonzero_possible=True, roots=roots)
        if op == "lognormal":
            # A point mass exp(log_mean) is bounded even if machine exp overflows.
            return Traits(True, True, b == 0, True, False, None, True,
                          frozenset() if b == 0 else roots)
        if op == "gamma":
            return Traits(True, True, False, True, False, None, True, roots)
        if op == "bernoulli":
            if a in (0, 1):
                return _constant(a)
            return Traits(True, True, True, True, False, None, True, roots)
        if op in ("uniform", "discrete_uniform"):
            return (_constant(a) if a == b else
                    Traits(True, True, True, a >= 0, b <= 0, None, True, roots))
        children = [self.traits(c) for c in node.children]
        if op == "mixture":
            children = [t for w, t in zip(node.weights, children) if w > 0]
        if not all(t.real for t in children):
            return Traits(False)
        all_roots = frozenset().union(*(t.roots for t in children))
        if op == "affine":
            t = children[0]
            if a == 0:
                return _constant(b)
            if t.constant is not None:
                return _constant(a * t.constant + b)
            return Traits(True, t.below if a > 0 else t.above,
                          t.above if a > 0 else t.below,
                          b >= 0 and (t.nonnegative if a > 0 else t.nonpositive),
                          b <= 0 and (t.nonpositive if a > 0 else t.nonnegative),
                          None, b == 0 and t.nonzero_possible, all_roots)
        if op == "clip":
            if a == b:
                return _constant(a)
            return Traits(True, True, True, a >= 0, b <= 0, None,
                          a > 0 or b < 0, all_roots)
        if op == "exp":
            t = children[0]
            return Traits(True, True, t.above, True, False, None, True, all_roots)
        if op == "sum":
            if all(t.constant is not None for t in children):
                return _constant(sum(t.constant for t in children))
            return Traits(True, all(t.below for t in children), all(t.above for t in children),
                          all(t.nonnegative for t in children), all(t.nonpositive for t in children),
                          roots=all_roots)
        if op == "product":
            if any(t.constant == 0 for t in children):
                return _constant(Fraction(0))
            if all(t.constant is not None for t in children):
                return _constant(math.prod(t.constant for t in children))
            bounded = all(t.below and t.above for t in children)
            nonnegative = all(t.nonnegative for t in children)
            return Traits(True, bounded or nonnegative, bounded, nonnegative, roots=all_roots)
        if op == "mixture":
            if all(t.constant is not None and t.constant == children[0].constant for t in children):
                return _constant(children[0].constant)
            return Traits(True, all(t.below for t in children), all(t.above for t in children),
                          all(t.nonnegative for t in children), all(t.nonpositive for t in children),
                          None, any(t.nonzero_possible for t in children), roots)
        return Traits(False)

    def independent(self, children: tuple[Node, ...]) -> bool:
        roots = [self.traits(c).roots for c in children]
        active = [r for r in roots if r]
        if len(active) < 2:
            return True
        if any(left & right for i, left in enumerate(active) for right in active[i + 1:]):
            return False
        union = frozenset().union(*active)
        # Separate pairwise declarations do not imply mutual independence.
        return any(union <= group for group in self.independence)

    def _mixture(self, node: Node, parameter: Any, mgf: bool) -> Proof:
        proofs = [(self.mgf(c, parameter) if mgf else self.moment(c, parameter))
                  for w, c in zip(node.weights, node.children) if w > 0]
        if any(p.status == FAIL for p in proofs):
            return Proof(FAIL, "A positive-weight mixture component has a divergent required moment.")
        if all(p.status == PASS for p in proofs):
            return Proof(PASS, "Every positive-weight component has the required finite moment.")
        return Proof(UNRESOLVED, "At least one positive-weight mixture component is unresolved.")

    @lru_cache(maxsize=12000)
    def moment(self, node: Node, order: int) -> Proof:
        t = self.traits(node)
        if not t.real:
            return Proof(UNRESOLVED, "Unsupported composition; real-valuedness and moments are unproved.")
        if t.below and t.above:
            return Proof(PASS, "Bounded real support implies finite absolute polynomial moments.")
        if node.op == "ref":
            return self.moment(self.variables[node.name], order)
        if node.op in ("normal", "lognormal", "gamma", "uniform", "constant", "bernoulli", "discrete_uniform"):
            return Proof(PASS, f"{node.op} has finite positive integer absolute moments.")
        if node.op == "affine":
            return self.moment(node.children[0], order)
        if node.op == "exp":
            return self.mgf(node.children[0], Fraction(order))
        if node.op == "mixture":
            return self._mixture(node, order, False)
        if node.op == "sum":
            proofs = [self.moment(c, order) for c in node.children]
            if all(p.status == PASS for p in proofs):
                return Proof(PASS, "A finite sum of L^p variables is L^p; independence is unnecessary.")
            if sum(p.status == FAIL for p in proofs) == 1 and all(p.status != UNRESOLVED for p in proofs):
                return Proof(FAIL, "Adding only finite L^p terms cannot remove one non-L^p term.")
            ts = [self.traits(c) for c in node.children]
            same_sign = all(x.nonnegative for x in ts) or all(x.nonpositive for x in ts)
            if same_sign and any(p.status == FAIL for p in proofs):
                return Proof(FAIL, "Same-sign summands cannot cancel a divergent absolute moment.")
            return Proof(UNRESOLVED, "Possible cancellation or dependence prevents a sum-moment conclusion.")
        if node.op == "product":
            proofs = [self.moment(c, order) for c in node.children]
            if self.independent(node.children):
                if all(p.status == PASS for p in proofs):
                    return Proof(PASS, "Independent factors have finite required absolute moments.")
                if any(p.status == FAIL for p in proofs) and all(self.traits(c).nonzero_possible for c in node.children):
                    return Proof(FAIL, "Independent nonzero factors preserve a divergent absolute moment.")
            stronger = [self.moment(c, order * len(node.children)) for c in node.children]
            if all(p.status == PASS for p in stronger):
                return Proof(PASS, "Holder's inequality proves a finite product moment without independence.")
            return Proof(UNRESOLVED, "Product moments need stronger marginal moments or explicit independence.")
        return Proof(UNRESOLVED, "No supported rule establishes the required absolute moment.")

    @lru_cache(maxsize=12000)
    def mgf(self, node: Node, coefficient: Fraction) -> Proof:
        """Check E exp(coefficient * X), without evaluating exp numerically."""
        t = self.traits(node)
        if not t.real:
            return Proof(UNRESOLVED, "Unsupported exponential composition.")
        if coefficient == 0 or (coefficient > 0 and t.above) or (coefficient < 0 and t.below):
            return Proof(PASS, "The exponent is bounded above, so its exponential is integrable.")
        op = node.op
        if op == "ref":
            return self.mgf(self.variables[node.name], coefficient)
        if op == "normal":
            return Proof(PASS, "A normal variable has a finite moment-generating function at every real argument.")
        if op == "lognormal":
            return Proof(FAIL, "A nondegenerate lognormal has infinite E[exp(t X)] for every t > 0.")
        if op == "gamma":
            if coefficient * node.b < 1:
                return Proof(PASS, "Gamma exponential moment is finite because coefficient * scale < 1.")
            return Proof(FAIL, "Gamma exponential moment diverges because coefficient * scale >= 1.")
        if op == "affine":
            return self.mgf(node.children[0], coefficient * node.a)
        if op == "mixture":
            return self._mixture(node, coefficient, True)
        if op == "sum":
            proofs = [self.mgf(c, coefficient) for c in node.children]
            if self.independent(node.children):
                if any(p.status == FAIL for p in proofs):
                    return Proof(FAIL, "Independent exponential factors preserve a divergent exponential moment.")
                if all(p.status == PASS for p in proofs):
                    return Proof(PASS, "Explicit independence factors the finite exponential moments.")
            directional_bounds = [self.traits(c).below if coefficient > 0 else self.traits(c).above
                                  for c in node.children]
            if all(directional_bounds) and any(p.status == FAIL for p in proofs):
                return Proof(FAIL, "Other exponent terms are bounded below in this direction and cannot cancel divergence.")
            stronger = [self.mgf(c, coefficient * len(node.children)) for c in node.children]
            if all(p.status == PASS for p in stronger):
                return Proof(PASS, "Holder's inequality proves integrability without independence.")
            return Proof(UNRESOLVED, "Exponential sum needs stronger marginal bounds or explicit mutual independence.")
        if op == "exp":
            child = node.children[0]
            # exp(normal) is exactly lognormal, including affine-normal inputs.
            if self._nondegenerate_normal(child):
                return Proof(FAIL, "Exponentiating a nondegenerate normal gives a lognormal with no positive MGF.")
        return Proof(UNRESOLVED, "No supported analytical rule establishes this exponential moment.")

    def _nondegenerate_normal(self, node: Node) -> bool:
        if node.op == "ref":
            return self._nondegenerate_normal(self.variables[node.name])
        if node.op == "normal":
            return node.b > 0
        if node.op == "affine":
            return node.a != 0 and self._nondegenerate_normal(node.children[0])
        return False


def _validated(manifest: Any) -> tuple[dict[str, Node], list[frozenset[str]], list[dict]]:
    _json_guard(manifest)
    if type(manifest) is not dict:
        raise DeclarationError("manifest must be an object")
    _keys(manifest, {"schema_version", "variables", "independence", "analyses"}, "manifest")
    if manifest["schema_version"] != VERSION:
        raise DeclarationError(f"schema_version must be {VERSION}")
    raw_variables = manifest["variables"]
    if type(raw_variables) is not dict or not raw_variables:
        raise DeclarationError("variables must be a nonempty object")
    variables = {_name(k, "variable name"): _parse(v, k, f"variables.{k}")
                 for k, v in raw_variables.items()}
    refs = {name: _refs(node) for name, node in variables.items()}
    done, visiting = set(), set()
    def visit(name: str) -> None:
        if name not in variables:
            raise DeclarationError(f"unknown variable reference: {name}")
        if name in visiting:
            raise DeclarationError(f"cyclic variable reference: {name}")
        if name in done:
            return
        visiting.add(name)
        for dep in refs[name]:
            visit(dep)
        visiting.remove(name)
        done.add(name)
    for name in variables:
        visit(name)
    @lru_cache(maxsize=12000)
    def expanded_depth(node: Node) -> int:
        if node.op == "ref":
            depth = 1 + expanded_depth(variables[node.name])
        else:
            depth = 1 + max((expanded_depth(c) for c in node.children), default=0)
        if depth > 64:
            raise DeclarationError("expanded law exceeds the 64-node depth limit")
        return depth
    for node in variables.values():
        expanded_depth(node)
    raw_groups = manifest["independence"]
    if type(raw_groups) is not list:
        raise DeclarationError("independence must be an array of mutually independent source-block groups")
    groups = []
    for raw in raw_groups:
        if type(raw) is not list or len(raw) < 2 or any(type(x) is not str for x in raw):
            raise DeclarationError("independence groups must contain at least two distinct source-block names")
        group = frozenset(raw)
        if len(group) != len(raw) or any(x not in variables or refs[x] for x in group):
            raise DeclarationError("independence groups must name distinct variable definitions without refs")
        groups.append(group)
    analyses = manifest["analyses"]
    if type(analyses) is not list or not analyses:
        raise DeclarationError("analyses must be a nonempty array")
    ids = set()
    for analysis in analyses:
        if type(analysis) is not dict:
            raise DeclarationError("each analysis must be an object")
        ident = _name(analysis.get("id"), "analysis.id")
        kind = _name(analysis.get("kind"), "analysis.kind")
        if ident in ids:
            raise DeclarationError("analysis IDs must be unique")
        ids.add(ident)
        if kind == "ols":
            _keys(analysis, {"id", "kind", "outcome", "predictors"}, f"analysis.{ident}")
            _name(analysis["outcome"], "outcome")
            names = analysis["predictors"]
            if type(names) is not list or not names or any(type(x) is not str for x in names):
                raise DeclarationError("OLS predictors must be a nonempty array of variable names")
            names = [analysis["outcome"], *names]
        elif kind == "pearson":
            _keys(analysis, {"id", "kind", "variables"}, f"analysis.{ident}")
            names = analysis["variables"]
            if type(names) is not list or len(names) != 2 or any(type(x) is not str for x in names):
                raise DeclarationError("Pearson variables must contain exactly two names")
        else:
            continue
        if any(x not in variables for x in names):
            raise DeclarationError(f"analysis.{ident}: unknown variable")
    return variables, groups, analyses


def _analysis_stub(analysis: dict) -> dict:
    kind = analysis.get("kind", "unknown")
    condition = "positive_variances" if kind == "pearson" else "nonsingular_predictor_moment_matrix"
    return {"id": analysis.get("id", "unknown"), "kind": kind, "status": UNRESOLVED,
            "second_moment_status": UNRESOLVED, "required_moments": [],
            "independent_review_required": ["code_correspondence", condition,
                                             "uncertainty_procedure_conditions_if_used"]}


def assess_law(manifest: Any) -> dict:
    """Return a JSON-safe report; malformed/unsupported input never gets a pass.

    Analysis ``second_moment_status`` concerns only finite declared-law second
    moments.  Full ``status`` remains unresolved unless a moment failure is
    proven, since this function cannot perform the independent scientific review.
    """
    report = {"schema_version": REPORT_VERSION, "scope": "declared_law_only",
              "manifest_valid": False, "status": UNRESOLVED, "errors": [], "analyses": []}
    try:
        variables, groups, analyses = _validated(manifest)
    except (DeclarationError, RecursionError) as error:
        report["errors"].append(str(error) or "declaration recursion limit exceeded")
        if type(manifest) is dict and type(manifest.get("analyses")) is list:
            report["analyses"] = [_analysis_stub(a) for a in manifest["analyses"]
                                  if type(a) is dict and type(a.get("id")) is str
                                  and type(a.get("kind")) is str]
        return report
    report["manifest_valid"] = True
    engine = _Engine(variables, groups)
    for analysis in analyses:
        result = _analysis_stub(analysis)
        if analysis["kind"] not in ("ols", "pearson"):
            result["reason"] = "Unsupported analysis kind; its mathematical requirements were not checked."
            report["analyses"].append(result)
            continue
        names = ([analysis["outcome"], *analysis["predictors"]] if analysis["kind"] == "ols"
                 else analysis["variables"])
        for name in dict.fromkeys(names):
            proof = engine.moment(variables[name], 2)
            result["required_moments"].append({"variable": name, "order": 2,
                                                "status": proof.status, "reason": proof.reason})
        statuses = [x["status"] for x in result["required_moments"]]
        result["second_moment_status"] = (FAIL if FAIL in statuses else
                                            PASS if all(x == PASS for x in statuses) else UNRESOLVED)
        if result["second_moment_status"] == FAIL:
            result["status"] = FAIL
            report["status"] = FAIL
        report["analyses"].append(result)
    return report

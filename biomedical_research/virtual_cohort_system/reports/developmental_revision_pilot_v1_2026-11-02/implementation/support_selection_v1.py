"""Declaration arithmetic and retained-frame reporting, never a proof of a generator.

No generator imports, sampling, patient-data access, or numerical source fitting.
Actual code/law support and scientific provenance need independently bound review.
"""

from dataclasses import dataclass
from fractions import Fraction
import re


SCHEMA_VERSION = "support_selection_v1"
_NUMBER = re.compile(r"[+-]?(?:\d+/\d+|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\Z")
_ROUTES = {"direct_eligible_joint", "conditional_joint", "transformed_variable_model"}
_PROVENANCE_KINDS = {"evidence", "assumption", "definition"}


class DeclarationError(ValueError):
    """Invalid declaration or release-owned check contract."""


def _object(value, path):
    if not isinstance(value, dict):
        raise DeclarationError(f"{path}: expected an object")
    return value


def _keys(value, required, optional, path):
    _object(value, path)
    missing = set(required) - set(value)
    extra = set(value) - set(required) - set(optional)
    if missing or extra:
        raise DeclarationError(f"{path}: missing keys {sorted(missing)}; unknown keys {sorted(extra)}")


def _text(value, path):
    if not isinstance(value, str) or not value.strip():
        raise DeclarationError(f"{path}: expected nonempty text")
    return value


def _list(value, path):
    if not isinstance(value, list):
        raise DeclarationError(f"{path}: expected an array")
    return value


def _ids(value, path):
    values = [_text(item, path) for item in _list(value, path)]
    if len(values) != len(set(values)):
        raise DeclarationError(f"{path}: duplicate IDs")
    return set(values)


def _number(value, path):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise DeclarationError(f"{path}: use an integer or exact decimal/rational string, not a float")
    literal = str(value)
    if len(literal) > 256 or not _NUMBER.fullmatch(literal):
        raise DeclarationError(f"{path}: invalid exact number")
    # Bound exponent spelling to keep malformed metadata from allocating huge integers.
    if "e" in literal.lower() and abs(int(literal.lower().split("e")[1])) > 10000:
        raise DeclarationError(f"{path}: exponent exceeds metadata arithmetic limit")
    try:
        return Fraction(literal)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise DeclarationError(f"{path}: invalid exact number") from exc


@dataclass(frozen=True)
class _Domain:
    lower: Fraction | None
    upper: Fraction | None
    lower_closed: bool
    upper_closed: bool

    def json(self):
        return {"lower": None if self.lower is None else str(self.lower),
                "upper": None if self.upper is None else str(self.upper),
                "lower_closed": self.lower_closed, "upper_closed": self.upper_closed}

    def affine(self, scale, shift):
        if scale == 0:
            return _Domain(shift, shift, True, True)
        lo = None if self.lower is None else scale * self.lower + shift
        hi = None if self.upper is None else scale * self.upper + shift
        if scale < 0:
            return _Domain(hi, lo, self.upper_closed, self.lower_closed)
        return _Domain(lo, hi, self.lower_closed, self.upper_closed)

    def subset_of(self, required):
        if required.lower is not None:
            if self.lower is None or self.lower < required.lower:
                return False
            if self.lower == required.lower and self.lower_closed and not required.lower_closed:
                return False
        if required.upper is not None:
            if self.upper is None or self.upper > required.upper:
                return False
            if self.upper == required.upper and self.upper_closed and not required.upper_closed:
                return False
        return True

    def contains(self, value):
        return ((self.lower is None or value > self.lower or
                 (self.lower_closed and value == self.lower)) and
                (self.upper is None or value < self.upper or
                 (self.upper_closed and value == self.upper)))


def _domain(value, path):
    _keys(value, {"lower", "upper", "lower_closed", "upper_closed"}, set(), path)
    for key in ("lower_closed", "upper_closed"):
        if not isinstance(value[key], bool):
            raise DeclarationError(f"{path}.{key}: expected a boolean")
    lo = None if value["lower"] is None else _number(value["lower"], path + ".lower")
    hi = None if value["upper"] is None else _number(value["upper"], path + ".upper")
    if (lo is None and value["lower_closed"]) or (hi is None and value["upper_closed"]):
        raise DeclarationError(f"{path}: infinite endpoints must be open")
    if lo is not None and hi is not None:
        if lo > hi or (lo == hi and not (value["lower_closed"] and value["upper_closed"])):
            raise DeclarationError(f"{path}: empty or reversed interval")
    return _Domain(lo, hi, value["lower_closed"], value["upper_closed"])


def _provenance(value, known, path):
    refs = _list(value, path)
    if not refs:
        raise DeclarationError(f"{path}: at least one provenance reference is required")
    seen = set()
    for ref in refs:
        _keys(ref, {"kind", "id"}, set(), path)
        kind, identity = _text(ref["kind"], path), _text(ref["id"], path)
        if kind not in known or identity not in known[kind]:
            raise DeclarationError(f"{path}: unknown provenance {kind}:{identity}")
        if (kind, identity) in seen:
            raise DeclarationError(f"{path}: duplicate provenance reference")
        seen.add((kind, identity))


def _stage(value, path):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DeclarationError(f"{path}: expected a nonnegative integer stage")
    return value


def _mapping(value, path, *, provenance_required=True):
    required = {"kind", "variable", "scale", "shift"}
    if provenance_required:
        required.add("provenance")
    _keys(value, required, set(), path)
    if value["kind"] != "affine":
        raise DeclarationError(f"{path}: only explicitly specified affine native mappings are supported")
    return (_text(value["variable"], path + ".variable"),
            _number(value["scale"], path + ".scale"),
            _number(value["shift"], path + ".shift"))


def _check(value, path):
    _keys(value, {"id", "variable", "domain"}, {"native_view", "native_mapping"}, path)
    _text(value["id"], path + ".id")
    _text(value["variable"], path + ".variable")
    if "native_view" in value:
        _text(value["native_view"], path + ".native_view")
        if "native_mapping" not in value:
            raise DeclarationError(f"{path}: native_view requires a release-owned native_mapping")
        required_mapping = _mapping(value["native_mapping"], path + ".native_mapping", provenance_required=False)
        if required_mapping[0] != value["variable"]:
            raise DeclarationError(f"{path}: required native mapping variable differs from check variable")
    elif "native_mapping" in value:
        raise DeclarationError(f"{path}: native_mapping requires native_view")
    return _domain(value["domain"], path + ".domain")


def _context(value, known, path):
    _keys(value, {"final_supports", "native_views", "selection", "transformations", "derivations"}, set(), path)
    supports = {}
    for variable, record in _object(value["final_supports"], path + ".final_supports").items():
        _text(variable, path + ".final_supports")
        _keys(record, {"domain", "provenance"}, set(), path + ".final_supports." + variable)
        supports[variable] = _domain(record["domain"], path + ".final_supports." + variable + ".domain")
        _provenance(record["provenance"], known, path + ".final_supports." + variable)
    if not supports:
        raise DeclarationError(f"{path}: final_supports must not be empty")
    mappings = {}
    for identity, record in _object(value["native_views"], path + ".native_views").items():
        _text(identity, path + ".native_views")
        mapping = _mapping(record, path + ".native_views." + identity)
        if mapping[0] not in supports:
            raise DeclarationError(f"{path}.native_views.{identity}: unknown final-support variable")
        _provenance(record["provenance"], known, path + ".native_views." + identity)
        mappings[identity] = mapping

    selection = value["selection"]
    _keys(selection, {"route", "exclusion_implementation", "conditioning_event", "description", "provenance"}, set(), path + ".selection")
    if selection["route"] not in _ROUTES:
        raise DeclarationError(f"{path}.selection: unknown route")
    conditional = selection["route"] == "conditional_joint"
    expected = "joint_conditioning" if conditional else "not_claimed"
    if selection["exclusion_implementation"] != expected:
        raise DeclarationError(f"{path}.selection: clipping/transformation is not joint exclusion; this route requires {expected}")
    if conditional:
        event = selection["conditioning_event"]
        _keys(event, {"description", "stage"}, set(), path + ".selection.conditioning_event")
        _text(event["description"], path + ".selection.conditioning_event.description")
        _stage(event["stage"], path + ".selection.conditioning_event.stage")
    elif selection["conditioning_event"] is not None:
        raise DeclarationError(f"{path}.selection: a nonconditional route must not claim a conditioning event")
    _text(selection["description"], path + ".selection.description")
    _provenance(selection["provenance"], known, path + ".selection.provenance")

    transforms = {}
    for item in _list(value["transformations"], path + ".transformations"):
        _keys(item, {"id", "kind", "variable", "stage", "role", "atom_effect", "description", "provenance"}, set(), path + ".transformations")
        identity = _text(item["id"], path + ".transformations.id")
        if identity in transforms:
            raise DeclarationError(f"{path}.transformations: duplicate transform ID")
        if item["kind"] not in {"clip", "winsorize", "round", "censor", "affine", "other"}:
            raise DeclarationError(f"{path}.transformations.{identity}: unknown transform kind")
        if item["variable"] not in supports:
            raise DeclarationError(f"{path}.transformations.{identity}: unknown final-support variable")
        if item["role"] not in {"law_construction", "measurement", "processing"}:
            raise DeclarationError(f"{path}.transformations.{identity}: a variable transform cannot be declared eligibility exclusion")
        if item["atom_effect"] not in {"none", "possible", "creates", "unknown"}:
            raise DeclarationError(f"{path}.transformations.{identity}: declare the atom effect")
        _stage(item["stage"], path + ".transformations." + identity + ".stage")
        _text(item["description"], path + ".transformations." + identity + ".description")
        _provenance(item["provenance"], known, path + ".transformations." + identity)
        transforms[identity] = item
    if selection["route"] == "transformed_variable_model" and not transforms:
        raise DeclarationError(f"{path}: transformed_variable_model must disclose a transformation")

    derivation_ids = set()
    for item in _list(value["derivations"], path + ".derivations"):
        _keys(item, {"id", "claim", "applicable_stage", "transform_effects", "description", "provenance"}, set(), path + ".derivations")
        identity = _text(item["id"], path + ".derivations.id")
        if identity in derivation_ids:
            raise DeclarationError(f"{path}.derivations: duplicate derivation ID")
        derivation_ids.add(identity)
        if item["claim"] not in {"exact_final_law", "approximation", "initialization"}:
            raise DeclarationError(f"{path}.derivations.{identity}: unknown claim")
        stage = _stage(item["applicable_stage"], path + ".derivations." + identity)
        effects = _object(item["transform_effects"], path + ".derivations." + identity + ".transform_effects")
        subsequent = {name for name, tr in transforms.items() if tr["stage"] > stage}
        if set(effects) - subsequent:
            raise DeclarationError(f"{path}.derivations.{identity}: effects must name known subsequent transforms")
        if any(effect not in {"preserved", "invalidated", "unresolved"} for effect in effects.values()):
            raise DeclarationError(f"{path}.derivations.{identity}: unknown transform effect")
        if item["claim"] == "exact_final_law":
            if set(effects) != subsequent or any(effect != "preserved" for effect in effects.values()):
                raise DeclarationError(f"{path}.derivations.{identity}: exact final-law identity is invalidated or unresolved after a subsequent transform")
        _text(item["description"], path + ".derivations." + identity + ".description")
        _provenance(item["provenance"], known, path + ".derivations." + identity)
    return supports, mappings


def assess_support_selection(declaration, *, required_contexts, required_checks,
                             known_provenance, context_sets=None):
    """Check strict declarations and exact interval arithmetic, not actual law support.

    Release owns required_contexts/checks and known_provenance (see schema document).
    context_sets optionally cross-checks task/spec/evidence/bridge context ID arrays.
    Return JSON-safe diagnostics. Even a passing report needs independent code review.
    """
    report = {"schema_version": SCHEMA_VERSION, "status": "declaration_checks_fail",
              "law_support_verified": False,
              "actual_code_law_support": "independent_review_required",
              "independent_review_binding_owner": "controller",
              "source_point_fit_required": False, "issues": [], "checks": []}
    try:
        contexts = _ids(required_contexts, "release.required_contexts")
        if not contexts:
            raise DeclarationError("release.required_contexts: must not be empty")
        _keys(known_provenance, _PROVENANCE_KINDS, set(), "release.known_provenance")
        known = {kind: _ids(known_provenance[kind], "release.known_provenance." + kind)
                 for kind in _PROVENANCE_KINDS}
        if context_sets is not None:
            _keys(context_sets, {"task", "spec", "evidence", "bridge"}, set(), "release.context_sets")
            for name, ids in context_sets.items():
                if _ids(ids, "release.context_sets." + name) != contexts:
                    raise DeclarationError(f"release.context_sets.{name}: context IDs differ from release")
        _keys(declaration, {"schema_version", "contexts"}, set(), "declaration")
        if declaration["schema_version"] != SCHEMA_VERSION:
            raise DeclarationError("declaration.schema_version: unsupported schema")
        if set(_object(declaration["contexts"], "declaration.contexts")) != contexts:
            raise DeclarationError("declaration.contexts: IDs must exactly match all release contexts")
        if set(_object(required_checks, "release.required_checks")) != contexts:
            raise DeclarationError("release.required_checks: IDs must exactly match all release contexts")
    except (DeclarationError, TypeError) as exc:
        report["issues"].append({"scope": "contract", "message": str(exc)})
        return report

    for context_id in sorted(contexts):
        try:
            supports, mappings = _context(declaration["contexts"][context_id], known, "contexts." + context_id)
            check_ids = set()
            checks = _list(required_checks[context_id], "release.required_checks." + context_id)
            if not checks:
                raise DeclarationError(f"release.required_checks.{context_id}: at least one required check is required")
            for check in checks:
                required = _check(check, "release.required_checks." + context_id)
                if check["id"] in check_ids:
                    raise DeclarationError(f"release.required_checks.{context_id}: duplicate check ID")
                check_ids.add(check["id"])
                variable = check["variable"]
                if variable not in supports:
                    raise DeclarationError(f"contexts.{context_id}: missing final support for {variable}")
                mapped = supports[variable]
                if "native_view" in check:
                    view = check["native_view"]
                    if view not in mappings:
                        raise DeclarationError(f"contexts.{context_id}: missing required native mapping {view}")
                    mapped_variable, scale, shift = mappings[view]
                    if mapped_variable != variable:
                        raise DeclarationError(f"contexts.{context_id}: native mapping variable differs from required check")
                    expected = _mapping(check["native_mapping"], "release.required_native_mapping", provenance_required=False)
                    if mappings[view] != expected:
                        raise DeclarationError(f"contexts.{context_id}: authored native mapping differs from release-owned exact mapping")
                    mapped = mapped.affine(scale, shift)
                passed = mapped.subset_of(required)
                report["checks"].append({"context_id": context_id, "check_id": check["id"],
                                         "status": "pass" if passed else "fail",
                                         "basis": "declared_interval_arithmetic",
                                         "mapped_declared_support": mapped.json(),
                                         "required_domain": required.json()})
                if not passed:
                    report["issues"].append({"scope": context_id,
                                             "message": f"{check['id']}: mapped declared support violates required domain"})
        except (DeclarationError, TypeError) as exc:
            report["issues"].append({"scope": context_id, "message": str(exc)})
    if not report["issues"]:
        report["status"] = "declaration_checks_pass"
    return report


def check_retained_frame(frame, *, context_id, declaration, required_checks):
    """Count required-domain violations in retained values; never filter or mutate.

    Call only after declaration assessment and binding. Accept a DataFrame or mapping
    of column sequences. Values use their stored decimal spelling for Fraction checks.
    This reports the retained table; it cannot establish population-law support.
    Invalid check metadata raises DeclarationError, rather than silently omitting it.
    """
    try:
        context = declaration["contexts"][context_id]
        context_checks = required_checks[context_id]
    except (KeyError, TypeError) as exc:
        raise DeclarationError("runtime context is missing from declaration or required checks") from exc
    context_checks = _list(context_checks, "required_checks")
    if not context_checks:
        raise DeclarationError("at least one required runtime check is required")
    result = {"schema_version": "support_selection_runtime_v1", "context_id": context_id,
              "status": "pass", "mutated_or_filtered": False,
              "population_law_support_verified": False, "row_count": None,
              "checks": [], "issues": []}
    columns, scheduled = {}, []
    for variable, record in _object(context["final_supports"], "final_supports").items():
        _keys(record, {"domain", "provenance"}, set(), "final_supports." + variable)
        declared = _domain(record["domain"], "final_supports." + variable + ".domain")
        scheduled.append(({"id": "declared_support:" + variable, "variable": variable},
                          declared, "declared_final_support"))
    check_ids, runtime_mappings = set(), {}
    for check in context_checks:
        _check(check, "required_check")
        if check["id"] in check_ids:
            raise DeclarationError("duplicate required runtime check ID")
        check_ids.add(check["id"])
        if "native_view" in check:
            try:
                record = context["native_views"][check["native_view"]]
            except KeyError as exc:
                raise DeclarationError("missing required native mapping") from exc
            actual = _mapping(record, "native_view")
            expected = _mapping(check["native_mapping"], "required_native_mapping", provenance_required=False)
            if actual != expected:
                raise DeclarationError("authored native mapping differs from release-owned exact mapping")
            runtime_mappings[check["id"]] = actual
        scheduled.append((check, _check(check, "required_check"), "required_domain"))
    for check, required, role in scheduled:
        variable = check["variable"]
        scale, shift = Fraction(1), Fraction(0)
        if "native_view" in check:
            _, scale, shift = runtime_mappings[check["id"]]
        if variable not in columns:
            try:
                columns[variable] = list(frame[variable])
            except (KeyError, TypeError):
                result["issues"].append(f"missing or unreadable retained column: {variable}")
                result["status"] = "fail"
                continue
        values = columns[variable]
        if result["row_count"] is None:
            result["row_count"] = len(values)
        elif result["row_count"] != len(values):
            result["issues"].append("retained column lengths differ")
            result["status"] = "fail"
        invalid, outside = 0, 0
        for value in values:
            try:
                if value is None or isinstance(value, bool):
                    raise ValueError("not a numeric value")
                point = Fraction(str(value))
            except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                invalid += 1
                continue
            if not required.contains(scale * point + shift):
                outside += 1
        passed = bool(values) and not invalid and not outside
        result["checks"].append({"check_id": check["id"], "check_role": role, "variable": variable,
                                 "native_view": check.get("native_view"), "total_rows": len(values),
                                 "invalid_or_nonfinite": invalid, "outside_required_domain": outside,
                                 "within_required_domain": len(values) - invalid - outside,
                                 "status": "pass" if passed else "fail"})
        if not passed:
            result["status"] = "fail"
    if not result["checks"]:
        result["status"] = "fail"
        result["issues"].append("no required checks were evaluated")
    return result

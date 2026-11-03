"""Analytical counterexamples and finite alternatives; no generated patient rows."""
import copy
import json
import math

import pytest

from scientific_validity_v1 import assess_law


def ref(name):
    return {"op": "ref", "name": name}


def exp(node):
    return {"op": "exp", "input": node}


def affine(node, scale=1, shift=0):
    return {"op": "affine", "input": node, "scale": scale, "shift": shift}


def normal(sd=1, mean=0):
    return {"op": "normal", "mean": mean, "sd": sd}


def lognormal(sd=1):
    return {"op": "lognormal", "log_mean": 0, "log_sd": sd}


def gamma(scale=1, shape=2):
    return {"op": "gamma", "shape": shape, "scale": scale}


def mixture(*pairs):
    return {"op": "mixture", "components": [{"weight": w, "law": law} for w, law in pairs]}


def manifest(law, extra=None, groups=None, kind="pearson"):
    variables = {"x": normal(), "y": law, **(extra or {})}
    analysis = ({"id": "analysis", "kind": "ols", "outcome": "y", "predictors": ["x"]}
                if kind == "ols" else {"id": "analysis", "kind": kind, "variables": ["x", "y"]})
    return {"schema_version": "scientific_validity_v1", "variables": variables,
            "independence": groups or [], "analyses": [analysis]}


def outcome(value):
    report = assess_law(value)
    json.dumps(report, allow_nan=False)
    return report["analyses"][0]["second_moment_status"]


@pytest.mark.parametrize("kind", ["ols", "pearson"])
def test_positive_exponential_lognormal_fails(kind):
    value = manifest(exp(affine(ref("bmi"), 0.01, -1000)), {"bmi": lognormal()}, kind=kind)
    report = assess_law(value)
    assert report["analyses"][0]["second_moment_status"] == "fail"
    assert report["status"] == "fail"
    assert report["scope"] == "declared_law_only"


@pytest.mark.parametrize("coefficient,expected", [(0, "pass"), (-0.1, "pass"), (0.1, "fail")])
def test_lognormal_link_sign(coefficient, expected):
    assert outcome(manifest(exp(affine(lognormal(), coefficient)))) == expected


def test_degenerate_lognormal_is_finite_even_at_extreme_location():
    law = {"op": "lognormal", "log_mean": 100000, "log_sd": 0}
    assert outcome(manifest(exp(law))) == "pass"


@pytest.mark.parametrize("law", [
    {"op": "bernoulli", "p": 0.6}, {"op": "bernoulli", "p": 0},
    {"op": "bernoulli", "p": 1},
    {"op": "discrete_uniform", "lower": 18, "upper": 90},
    {"op": "discrete_uniform", "lower": 2, "upper": 2},
])
def test_exact_bounded_discrete_primitives(law):
    report = assess_law(manifest(exp(law)))
    assert report["analyses"][0]["second_moment_status"] == "pass"
    assert report["analyses"][0]["status"] == "unresolved"


@pytest.mark.parametrize("law", [
    {"op": "bernoulli", "p": -0.01}, {"op": "bernoulli", "p": 1.01},
    {"op": "bernoulli", "p": True},
    {"op": "discrete_uniform", "lower": 18.5, "upper": 90},
    {"op": "discrete_uniform", "lower": 90, "upper": 18},
    {"op": "discrete_uniform", "lower": 18, "upper": False},
])
def test_bounded_discrete_domains_fail_closed(law):
    report = assess_law(manifest(law))
    assert not report["manifest_valid"]
    assert report["analyses"][0]["second_moment_status"] == "unresolved"


@pytest.mark.parametrize("scale,expected", [(0.49, "pass"), (0.5, "fail"), (0.51, "fail")])
def test_gamma_exponential_second_moment_strict_threshold(scale, expected):
    assert outcome(manifest(exp(gamma(scale)))) == expected


def test_gamma_decimal_threshold_uses_exact_declared_decimal_product():
    assert outcome(manifest(exp(affine(gamma(0.1), 5)))) == "fail"
    assert outcome(manifest(exp(affine(gamma(0.1), math.nextafter(5.0, 0.0))))) == "pass"


@pytest.mark.parametrize("shape,scale", [(0, 1), (-1, 1), (1, 0), (1, -1)])
def test_gamma_parameter_domains(shape, scale):
    report = assess_law(manifest(exp(gamma(scale, shape))))
    assert not report["manifest_valid"]
    assert report["analyses"][0]["second_moment_status"] == "unresolved"
    assert report["errors"]


@pytest.mark.parametrize("law", [normal(), lognormal(), gamma(),
                                 {"op": "uniform", "lower": -3, "upper": 4}])
def test_polynomial_primitives_have_finite_moments(law):
    # The same reference is repeated: these factors must not be treated as independent.
    polynomial = {"op": "product", "factors": [ref("z"), ref("z"), ref("z")]}
    assert outcome(manifest(polynomial, {"z": law})) == "pass"


def test_normal_exponential_is_finite_but_its_positive_exponential_is_not():
    assert outcome(manifest(exp(affine(normal(), 9, 10)))) == "pass"
    assert outcome(manifest(exp(exp(affine(normal(), 9, 10))))) == "fail"


def test_bounded_transform_resolves_infinite_moments_but_not_unknown_realness():
    clipped = {"op": "clip", "lower": 0, "upper": 100, "input": exp(lognormal())}
    assert outcome(manifest(clipped)) == "pass"
    clipped["input"] = {"op": "unreviewed_python", "body": "raise RuntimeError()"}
    assert outcome(manifest(clipped)) == "unresolved"


def test_truncation_and_clipping_are_not_silently_interchanged():
    assert outcome(manifest({"op": "truncated_normal", "lower": 0, "upper": 1})) == "unresolved"


def test_positive_weight_divergent_component_fails_and_zero_weight_does_not():
    assert outcome(manifest(mixture((0.999999, normal()), (0.000001, exp(lognormal()))))) == "fail"
    assert outcome(manifest(mixture((3, normal()), (0, exp(lognormal()))))) == "pass"
    assert outcome(manifest(mixture((1, normal()), (2, gamma())))) == "pass"


def test_mixture_exponential_checks_each_branch():
    law = exp(mixture((1, gamma(0.4)), (1, gamma(0.5))))
    assert outcome(manifest(law)) == "fail"


@pytest.mark.parametrize("law", [mixture((0, normal())), mixture((-1, normal()), (2, normal())),
                                 mixture((1, ref("x")))])
def test_invalid_mixture_declarations_are_not_accepted(law):
    report = assess_law(manifest(law))
    assert not report["manifest_valid"]
    assert report["status"] == "unresolved"


def test_divergent_sum_cancellation_remains_unresolved():
    law = {"op": "sum", "terms": [ref("z"), affine(ref("z"), -1)]}
    # This deliberately supported-small checker does not algebraically simplify X-X.
    assert outcome(manifest(law, {"z": exp(lognormal())})) == "unresolved"


def test_same_sign_divergent_sum_and_finite_perturbation_fail():
    assert outcome(manifest({"op": "sum", "terms": [exp(lognormal()), exp(lognormal())]})) == "fail"
    assert outcome(manifest({"op": "sum", "terms": [exp(lognormal()), normal()]})) == "fail"


def test_exponential_sum_requires_independence_for_gamma_threshold_factorization():
    law = exp({"op": "sum", "terms": [ref("g1"), ref("g2")]})
    extra = {"g1": gamma(0.4), "g2": gamma(0.4)}
    assert outcome(manifest(law, extra)) == "unresolved"
    assert outcome(manifest(law, extra, [["g1", "g2"]])) == "pass"


def test_pairwise_independence_does_not_establish_mutual_independence():
    law = exp({"op": "sum", "terms": [ref("a"), ref("b"), ref("c")]})
    extra = {name: gamma(0.4) for name in "abc"}
    assert outcome(manifest(law, extra, [["a", "b"], ["b", "c"], ["a", "c"]])) == "unresolved"
    assert outcome(manifest(law, extra, [["a", "b", "c"]])) == "pass"


def test_repeated_reference_never_becomes_independent():
    law = exp({"op": "sum", "terms": [ref("g"), ref("g")]})
    # The correct second moment diverges; this conservative checker may leave it unresolved.
    assert outcome(manifest(law, {"g": gamma(0.4), "unused": gamma()}, [["g", "unused"]])) == "unresolved"


def test_positive_lognormal_exponent_plus_negative_dependent_term_is_unresolved():
    exponent = {"op": "sum", "terms": [ref("z"), affine(ref("z"), -1)]}
    assert outcome(manifest(exp(exponent), {"z": lognormal()})) == "unresolved"


def test_independent_normal_noise_cannot_repair_lognormal_exponential():
    exponent = {"op": "sum", "terms": [ref("z"), ref("noise")]}
    extra = {"z": lognormal(), "noise": normal()}
    assert outcome(manifest(exp(exponent), extra)) == "unresolved"
    assert outcome(manifest(exp(exponent), extra, [["z", "noise"]])) == "fail"


def test_nonnegative_exponent_terms_cannot_cancel_lognormal_divergence():
    exponent = {"op": "sum", "terms": [lognormal(), gamma()]}
    assert outcome(manifest(exp(exponent))) == "fail"


def test_product_uses_holder_without_independence_and_factorization_with_it():
    law = {"op": "product", "factors": [ref("a"), ref("b")]}
    extra = {"a": exp(gamma(0.4)), "b": exp(gamma(0.4))}
    assert outcome(manifest(law, extra)) == "unresolved"
    assert outcome(manifest(law, extra, [["a", "b"]])) == "pass"
    extra["a"] = exp(lognormal())
    assert outcome(manifest(law, extra, [["a", "b"]])) == "fail"


def test_zero_product_has_finite_moments():
    assert outcome(manifest({"op": "product", "factors": [{"op": "constant", "value": 0},
                                                            exp(lognormal())]})) == "pass"


@pytest.mark.parametrize("value", [True, False, float("nan"), float("inf"), -float("inf"), "1"])
def test_malformed_numbers_fail_closed(value):
    report = assess_law(manifest(normal(sd=value)))
    assert report["status"] == "unresolved"
    assert not report["manifest_valid"]
    assert report["analyses"][0]["second_moment_status"] == "unresolved"
    json.dumps(report, allow_nan=False)


def test_unknown_operation_and_analysis_are_unresolved():
    assert outcome(manifest({"op": "power", "input": normal(), "exponent": 2})) == "unresolved"
    assert outcome(manifest(normal(), kind="spearman")) == "unresolved"


@pytest.mark.parametrize("mutation", [
    lambda m: m["variables"].update(y=ref("missing")),
    lambda m: m["variables"].update(y=ref("y")),
    lambda m: m["variables"]["y"].update(extra=1),
    lambda m: m["independence"].append(["x", "x"]),
    lambda m: m["variables"].update(y={"op": "uniform", "lower": 2, "upper": 1}),
    lambda m: m["analyses"].append(copy.deepcopy(m["analyses"][0])),
])
def test_malformed_structures_fail_closed(mutation):
    value = manifest(normal())
    mutation(value)
    assert not assess_law(value)["manifest_valid"]
    assert outcome(value) == "unresolved"


def test_analysis_results_are_separate_and_finite_moments_do_not_certify_rank():
    value = manifest(exp(lognormal()))
    value["analyses"] += [{"id": "constant_predictor", "kind": "ols", "outcome": "x", "predictors": ["c"]},
                          {"id": "constant_pearson", "kind": "pearson", "variables": ["x", "c"]}]
    value["variables"]["c"] = {"op": "constant", "value": 0}
    report = assess_law(value)
    assert [a["second_moment_status"] for a in report["analyses"]] == ["fail", "pass", "pass"]
    assert [a["status"] for a in report["analyses"]] == ["fail", "unresolved", "unresolved"]
    assert "nonsingular_predictor_moment_matrix" in report["analyses"][1]["independent_review_required"]
    assert "positive_variances" in report["analyses"][2]["independent_review_required"]


def test_deep_reference_graph_fails_closed_and_input_is_unchanged():
    value = manifest(normal())
    for i in range(70):
        value["variables"][f"v{i}"] = ref(f"v{i + 1}") if i < 69 else normal()
    before = copy.deepcopy(value)
    report = assess_law(value)
    assert not report["manifest_valid"]
    assert value == before

"""Pure numeric-controller tests; no generator or biomedical outcome execution."""
import copy

import pytest

from cohort_harness.calibration import _score, _search


def plan(max_trials=12):
    return {"parameters": [{"name": "a", "lower": -2, "upper": 2, "step": 1}],
            "optimizer": {"max_trials": max_trials, "shrink": .5, "min_step_fraction": .01,
                          "target_loss": 0},
            "constraints": [{"context_id": "source", "check_id": "mean", "scale": 2,
                             "scale_reason": "Invented fixed scale"}]}


def transcript(p, objective):
    search = _search(p, {"a": 0})
    records, proposal = [], next(search)
    while True:
        loss = objective(proposal["a"])
        records.append((proposal, loss))
        try:
            proposal = search.send(loss)
        except StopIteration as stop:
            return records, stop.value


def test_recovers_negative_value_with_fixed_direction_order():
    records, reason = transcript(plan(), lambda a: (a+1)**2)
    assert [r[0]["a"] for r in records] == [0, 1, -1]
    assert reason == "target_loss"


def test_initial_evaluation_consumes_budget_and_can_be_infeasible():
    records, reason = transcript(plan(1), lambda a: None)
    assert len(records) == 1 and reason == "max_trials"


def test_infeasible_point_is_not_false_zero_loss():
    records, reason = transcript(plan(), lambda a: None if a == 0 else (a-2)**2)
    assert reason == "target_loss" and records[-1][0]["a"] == 2


def test_ties_do_not_move_incumbent_and_clipping_has_no_duplicate_trials():
    p = plan(40)
    p["parameters"][0]["step"] = 3
    records, reason = transcript(p, lambda a: 1)
    values = [r[0]["a"] for r in records]
    assert values[:3] == [0, 2, -2]
    assert len(values) == len(set(values))
    assert reason == "minimum_step"
    assert all(-2 <= x <= 2 for x in values)


def report(seed, value=4, status="computed"):
    return {"limits": {"seed": seed}, "contexts": [{"id": "source", "checks": [
        {"id": "mean", "value": value, "reported_value": 2, "status": status}]}]}


def test_objective_is_mean_squared_standardized_errors_not_squared_mean():
    result = _score([report(1, 4), report(2, 0)], plan())
    assert result["feasible"] and result["loss"] == 1
    assert [c["scaled_error"] for c in result["constraints"]] == [1, -1]


@pytest.mark.parametrize("failed", [report(2, status="not_computable"), report(2, float("inf")),
                                    {"limits": {"seed": 2}, "contexts": [{"id": "source", "checks": []}]}])
def test_undefined_constraints_remain_in_diagnostics_and_invalidate_whole_trial(failed):
    result = _score([report(1), failed], plan())
    assert result["loss"] is None and result["feasible"] is False
    assert len(result["constraints"]) == 2
    assert result["constraints"][1]["status"] == "unavailable"


def test_error_overflow_makes_infeasible_instead_of_nonfinite_json():
    p = copy.deepcopy(plan())
    p["constraints"][0]["scale"] = 1e-300
    result = _score([report(1, 1e300)], p)
    assert result["loss"] is None


def test_subnormal_step_cannot_leave_search_in_infinite_duplicate_loop():
    p = plan(10)
    p["parameters"][0].update(lower=0, upper=5e-324, step=5e-324)
    records, reason = transcript(p, lambda a: 1)
    assert len(records) <= 10 and reason in {"minimum_step", "numerical_step_limit", "max_rounds"}


def test_rounds_are_bounded_even_when_tiny_steps_round_to_existing_vectors():
    p = plan(4)
    p["parameters"][0].update(lower=1e20, upper=1e20+1e10, step=1)
    p["optimizer"].update(shrink=1-2**-53, min_step_fraction=1e-20)
    search = _search(p, {"a": 1e20})
    assert next(search) == {"a": 1e20}
    with pytest.raises(StopIteration) as stop:
        search.send(1)
    assert stop.value.value in {"max_rounds", "numerical_step_limit"}

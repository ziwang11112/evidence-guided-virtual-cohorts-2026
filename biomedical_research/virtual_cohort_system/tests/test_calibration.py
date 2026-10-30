"""Invented arithmetic with a MOCK backend; these tests do not establish isolation.

The fake backend independently evaluates fixture algebra. Candidate Python is
never imported or executed on the host. Actual isolation has a separate CLI smoke.
"""
import copy
import math

import numpy as np
import pandas as pd
import pytest

from cohort_harness import calibration as cal, calibration_budget as budget, execution
from cohort_harness.lifecycle import read_json, sha256, verify_candidate
from examples.m12_calibration import EXPECTED, REFERENCE, budget_limits, build_fixture, write


@pytest.fixture
def box(tmp_path_factory):
    # Short physical names avoid MAX_PATH failures in nested replay bundles.
    return tmp_path_factory.mktemp("c")


def prepared(box, *, trials=None, incompatible=False, noncomputable=False, limits=None):
    root, candidate, plan = build_fixture(box / "b", incompatible, noncomputable)
    if trials is not None:
        plan["optimizer"]["max_trials"] = trials
    budget.create_budget(root, budget_limits(plan) if limits is None else limits)
    return root, candidate, plan


def mocked_backend(monkeypatch, *, failing_seeds=(), on_dispatch=None):
    """A separately written algebraic stub, not a sandbox or generator test."""
    calls = []
    monkeypatch.setattr(execution, "_runtime_manifest", lambda _: {"mocked": True})

    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        request = read_json(cwd / "input/request.json")
        seed = request["seed"]
        parameters = read_json(cwd / "input/model_spec.json")["parameters"]
        calls.append((seed, parameters.copy()))
        if on_dispatch:
            on_dispatch(seed, parameters)
        task = read_json(cwd / "input/task.json")
        observed = execution.read_table(cwd / "input/observed.csv", task)
        # Fixture arithmetic is explicit here; generator.py is never loaded.
        sign = 1 if seed % 2 else -1
        residual = np.tile([-1.0, 1.0], len(observed) // 2 + 1)[:len(observed)]
        y = (parameters["intercept"] + parameters["slope"] * observed.x.astype(float)
             + parameters["z_effect"] * observed.z.astype(float) + parameters["noise_scale"] * sign * residual)
        observed.assign(y=y).to_csv(cwd / "output/generated.csv", index=False)
        failed = seed in failing_seeds
        write(cwd / "output/worker_report.json", {"status": "failed" if failed else "completed", "generator_started": True})
        stdout_path.write_text("MOCK backend: invented arithmetic; no isolation claim", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return {"returncode": 1 if failed else 0, "host_timeout": False, "logs": {}}

    monkeypatch.setattr(execution, "_capture", capture)
    return calls


def recommit(session, result):
    """Adversarial retained-manifest edit; semantic verification must still fail."""
    result["files"] = {p.relative_to(session).as_posix(): sha256(p) for p in session.rglob("*")
                       if p.is_file() and p != session / "result.json"}
    write(session / "result.json", result)


def test_literal_reference(box):
    root, candidate, _ = build_fixture(box / "b")
    reference = pd.read_csv(root / "sources/reference.csv")
    assert list(reference.itertuples(index=False, name=None)) == REFERENCE
    assert reference.groupby("z").size().to_dict() == {0: 8, 1: 4}
    assert reference.groupby("z").x.mean().tolist() == [0, 0]
    design = np.column_stack([np.ones(12), reference.x, reference.z])
    assert np.linalg.matrix_rank(design) == 3
    # Independent normal equations, rather than the harness least-squares call.
    beta = np.linalg.solve(design.T @ design, design.T @ reference.y.to_numpy())
    assert beta == pytest.approx([3, 2, 2])
    residual = reference.y - design @ beta
    assert design.T @ residual == pytest.approx([0, 0, 0], abs=1e-12)
    assert residual.tolist() == pytest.approx([-1, 1] * 6)
    assert reference.y.mean() == pytest.approx(11 / 3)
    assert reference.y.std(ddof=1) == pytest.approx(math.sqrt(212 / 33))
    assert pd.read_csv(candidate / "cov.csv").columns.tolist() == ["id", "x", "z"]
    assert not (candidate / "source_check_report.json").exists()


def test_fit(box, monkeypatch):
    root, candidate, plan = prepared(box)
    before = {name: sha256(root / name) for name in ["task.json", "observed.csv", "candidates/p/freeze.json",
                                                    "candidates/p/generator.py", "candidates/p/model_spec.json"]}
    plan_copy = copy.deepcopy(plan)
    calls = mocked_backend(monkeypatch)
    result = cal.run_calibration(root, candidate, "s", plan)
    assert result == cal.verify_calibration(root, "s")
    assert result["status"] == "fit_threshold_met" and result["stop_reason"] == "target_loss"
    assert len(result["trials"]) == 20
    assert result["selected_trial"] == 19
    assert result["trials"][19]["parameters"] == EXPECTED
    assert result["replay"]["feasible"] and result["replay"]["loss"] < 1e-20
    assert len(calls) == 42 and result["usage"]["executions"] == 42
    assert all(p["z_effect"] == 2 for _, p in calls)
    assert all(len(t["fit"]["constraints"]) == 6 for t in result["trials"])
    assert plan == plan_copy
    assert before == {name: sha256(root / name) for name in before}
    verify_candidate(root, candidate)
    child = root / "cal/s/t0019/candidates/t"
    assert sha256(child / "generator.py") == sha256(candidate / "generator.py")
    spec = read_json(child / "model_spec.json")
    assert spec["parameter_provenance"]["z_effect"] == read_json(candidate / "model_spec.json")["parameter_provenance"]["z_effect"]
    assert read_json(child / "calibration_trial.json")["value_origin"] == "calibrated_trial"
    state = budget.get_budget(root)
    assert state["reserved"]["trials"] == 25 and state["used"]["trials"] == 20
    assert state["remaining"]["trials"] == 0 and state["pending"] is None


def test_initial_counts(box, monkeypatch):
    root, candidate, plan = prepared(box, trials=1)
    calls = mocked_backend(monkeypatch)
    result = cal.run_calibration(root, candidate, "s", plan)
    assert len(result["trials"]) == 1 and result["stop_reason"] == "max_trials"
    assert result["selected_trial"] == 0 and result["status"] == "fit_threshold_not_met"
    assert [seed for seed, _ in calls] == [101, 102, 201, 202]


def test_incompatible(box, monkeypatch):
    root, candidate, plan = prepared(box, incompatible=True)
    mocked_backend(monkeypatch)
    result = cal.run_calibration(root, candidate, "s", plan)
    assert len(result["trials"]) == 3 and result["status"] == "fit_threshold_not_met"
    assert all(t["fit"]["feasible"] and len(t["fit"]["constraints"]) == 8 for t in result["trials"])
    # For any mean m: ((m-11/3)^2+(m-17/3)^2)/4 >= 1/2.
    assert all(t["fit"]["loss"] >= 0.5 for t in result["trials"])


def test_undefined(box, monkeypatch):
    root, candidate, plan = prepared(box, noncomputable=True)
    calls = mocked_backend(monkeypatch)
    result = cal.run_calibration(root, candidate, "s", plan)
    assert result["status"] == "no_feasible_trial" and result["selected_trial"] is None
    assert result["replay"] is None and len(calls) == 6
    for trial in result["trials"]:
        assert not trial["fit"]["feasible"] and trial["fit"]["loss"] is None
        assert len(trial["fit"]["constraints"]) == 6
        undefined = [c for c in trial["fit"]["constraints"] if c["status"] != "computed"]
        assert len(undefined) == 2 and {c["check_id"] for c in undefined} == {"beta"}


def test_fit_failure(box, monkeypatch):
    root, candidate, plan = prepared(box, trials=2)
    calls = mocked_backend(monkeypatch, failing_seeds={102})
    result = cal.run_calibration(root, candidate, "s", plan)
    assert len(calls) == 4 and result["selected_trial"] is None
    assert result["status"] == "no_feasible_trial"
    for trial in result["trials"]:
        assert trial["fit"]["loss"] is None and len(trial["fit"]["constraints"]) == 6
        assert [c["status"] for c in trial["fit"]["constraints"]] == ["computed"] * 3 + ["unavailable"] * 3


def test_replay_never_selects(box, monkeypatch):
    root, candidate, plan = prepared(box, trials=2)
    plan["optimizer"]["target_loss"] = 1.5  # Met by trial 1 before both replay failures.
    seals = []

    def inspect(seed, parameters):
        if seed in plan["replay_seeds"]:
            seal = read_json(root / "cal/s/selection.json")
            seals.append(copy.deepcopy(seal))
            assert seal["selected_trial"] == 1 and parameters["intercept"] == 1.5

    calls = mocked_backend(monkeypatch, failing_seeds={201, 202}, on_dispatch=inspect)
    result = cal.run_calibration(root, candidate, "s", plan)
    assert [seed for seed, _ in calls] == [101, 102, 101, 102, 201, 202]
    assert seals[0] == seals[1]
    assert result["selected_trial"] == 1
    assert result["trials"][1]["fit"]["loss"] < result["trials"][0]["fit"]["loss"]
    assert result["status"] == "fit_threshold_met" and result["replay"]["feasible"] is False
    assert result["replay"]["loss"] is None


@pytest.mark.parametrize("case", ["overlap", "duplicate", "unknown", "boolean", "bounds", "step", "nan", "scale",
                                  "drop", "duplicate_check", "rule", "field", "trials", "undefined"])
def test_plan_reject(box, monkeypatch, case):
    root, candidate, plan = prepared(box, trials=1)
    if case == "overlap": plan["replay_seeds"] = [101]
    elif case == "duplicate": plan["fit_seeds"] = [101, 101]
    elif case == "unknown": plan["parameters"][0]["name"] = "unknown"
    elif case == "boolean": plan["parameters"][0]["step"] = True
    elif case == "bounds": plan["parameters"][0]["lower"] = 2
    elif case == "step": plan["parameters"][0]["step"] = 0
    elif case == "nan": plan["parameters"][0]["upper"] = float("nan")
    elif case == "scale": plan["constraints"][0]["scale"] = 0
    elif case == "drop": plan["constraints"].pop()
    elif case == "duplicate_check": plan["constraints"].append(copy.deepcopy(plan["constraints"][0]))
    elif case == "rule": plan["optimizer"]["method"] = "arbitrary_search"
    elif case == "field": plan["optimizer"]["secret_rule"] = True
    elif case == "trials": plan["optimizer"]["max_trials"] = 0
    else: plan["noncomputable"] = "drop"
    monkeypatch.setattr(execution, "run_candidate", lambda *a, **k: pytest.fail("rejected plan dispatched"))
    with pytest.raises(ValueError):
        cal.run_calibration(root, candidate, "s", plan)
    assert not (root / "cal/s").exists()
    assert budget.get_budget(root)["reserved"]["sessions"] == 0


def test_budget_before_dispatch(box, monkeypatch):
    limits = {"sessions": 1, "trials": 1, "executions": 3, "reserved_seconds": 90}
    root, candidate, plan = prepared(box, trials=1, limits=limits)
    monkeypatch.setattr(execution, "run_candidate", lambda *a, **k: pytest.fail("budget rejection dispatched"))
    with pytest.raises(ValueError, match="budget exhausted"):
        cal.run_calibration(root, candidate, "s", plan)
    assert not (root / "cal/s").exists()


def test_parent_tamper(box, monkeypatch):
    root, candidate, plan = prepared(box, trials=1)
    program = candidate / "generator.py"
    program.write_text(program.read_text() + "\n# changed fixed structure\n", encoding="utf-8")
    monkeypatch.setattr(execution, "run_candidate", lambda *a, **k: pytest.fail("tampered parent dispatched"))
    with pytest.raises(ValueError):
        cal.run_calibration(root, candidate, "s", plan)
    assert budget.get_budget(root)["reserved"]["sessions"] == 0


@pytest.mark.parametrize("case", ["proposal", "loss", "chosen", "stop", "seal", "generator", "output"])
def test_recommitted_tamper(box, monkeypatch, case):
    root, candidate, plan = prepared(box, trials=2)
    mocked_backend(monkeypatch)
    result = cal.run_calibration(root, candidate, "s", plan)
    session = root / "cal/s"
    if case == "proposal":
        result["trials"][1]["parameters"]["intercept"] = 4
        write(session / "t0001/trial.json", result["trials"][1])
    elif case == "loss":
        result["trials"][1]["fit"]["loss"] = 0
        write(session / "t0001/trial.json", result["trials"][1])
    elif case == "chosen": result["selected_trial"] = 0
    elif case == "stop": result["stop_reason"] = "target_loss"
    elif case == "seal":
        selection = read_json(session / "selection.json")
        selection["selected_trial"] = 0
        write(session / "selection.json", selection)
    else:
        relative = "t0000/candidates/t/generator.py" if case == "generator" else (
            "t0000/source_replays_v2/f0/contexts/s/bundle/executions/replay/output/generated.csv")
        path = session / relative
        path.write_bytes(path.read_bytes() + b"\n")
    recommit(session, result)
    with pytest.raises(ValueError):
        cal.verify_calibration(root, "s")


def test_interrupt_stays_reserved(box, monkeypatch):
    root, candidate, plan = prepared(box, trials=2)
    monkeypatch.setattr(cal.replay, "run_source_replay", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("invented interruption")))
    with pytest.raises(RuntimeError, match="invented interruption"):
        cal.run_calibration(root, candidate, "s", plan)
    state = budget.get_budget(root)
    assert state["pending"] == "s" and state["remaining"]["trials"] == 0
    assert (root / "cal/s/intent.json").exists() and not (root / "cal/s/result.json").exists()
    with pytest.raises(ValueError, match="pending session"):
        cal.run_calibration(root, candidate, "other", plan)


def test_search_edges():
    plan = {"parameters": [{"name": "p", "lower": 0, "upper": 1, "step": 1}],
        "optimizer": {"max_trials": 9, "shrink": 0.5, "min_step_fraction": 0.3, "target_loss": 0}}
    search = cal._search(plan, {"p": 1})
    values = [next(search)["p"]]
    while True:
        try:
            values.append(search.send(1)["p"])
        except StopIteration as stop:
            assert stop.value == "minimum_step"
            break
    assert values == [1, 0, 0.5]  # Clipped duplicates never consume another trial.

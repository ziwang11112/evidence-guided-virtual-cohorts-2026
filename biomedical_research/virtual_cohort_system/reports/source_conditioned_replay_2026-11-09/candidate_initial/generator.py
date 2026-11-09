"""Declared donor-transport model; executed only by the isolated harness worker."""
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _bounded_beta(rng, n, mean, sd, bounds):
    lower, upper = bounds
    m = (mean - lower) / (upper - lower)
    v = (sd / (upper - lower)) ** 2
    k = m * (1.0 - m) / v - 1.0
    if not (0.0 < m < 1.0 and k > 0.0):
        raise ValueError("Invalid declared beta moments")
    return lower + (upper - lower) * rng.beta(m * k, (1.0 - m) * k, n)


def _quota_categories(rng, n, weights, z_bmi, z_age, tilt_bmi, tilt_age):
    """One finite quota assignment, no rejection/retry or outcome-based selection.

    Counts approximate the specified marginal probabilities. Every positive
    category receives at least one slot. Nonreference categories are assigned
    in declared order by weighted Gumbel ranking without replacement. Remaining
    rows take the reference category. This is a declared joint-law assumption,
    not a recovered multinomial conditional model.
    """
    weights = np.asarray(weights, dtype=float)
    probabilities = weights / weights.sum()
    positive = np.flatnonzero(probabilities > 0.0)
    if n < len(positive):
        raise ValueError("Context too small for declared category support")
    expected = n * probabilities
    counts = np.floor(expected).astype(int)
    counts[positive] = np.maximum(counts[positive], 1)
    remainder = n - int(counts.sum())
    if remainder > 0:
        priority = np.argsort(-(expected - np.floor(expected)), kind="stable")
        for index in priority[:remainder]:
            counts[index] += 1
    elif remainder < 0:
        # n is at least the number of positive categories. A single transfer
        # from the largest cell suffices for these frozen sampling contexts.
        donor = int(np.argmax(counts))
        if counts[donor] + remainder < 1:
            raise ValueError("Cannot allocate declared category quotas")
        counts[donor] += remainder
    assignments = np.zeros(n, dtype=int)
    available = np.ones(n, dtype=bool)
    for category in range(1, len(weights)):
        count = int(counts[category])
        if count == 0:
            continue
        eligible = np.flatnonzero(available)
        score = (rng.gumbel(size=len(eligible))
                 + tilt_bmi[category] * z_bmi[eligible]
                 + tilt_age[category] * z_age[eligible])
        chosen = eligible[np.argsort(-score, kind="stable")[:count]]
        assignments[chosen] = category
        available[chosen] = False
    return assignments


def _group(rng, n, group, parameters, source_context):
    anchors = parameters["groups"][group]
    settings = parameters["distribution"]
    if source_context:
        age = _bounded_beta(rng, n, anchors["age_mean"], anchors["age_sd"],
                            settings["source_age_bounds"])
    else:
        target_age = parameters["target_law"]["age"]
        age = (target_age["lower"] + (target_age["upper"] - target_age["lower"])
               * rng.beta(target_age["alpha"], target_age["beta"], n))
    bmi = _bounded_beta(rng, n, anchors["bmi_mean"], anchors["bmi_sd"],
                        settings["bmi_bounds"])
    z_bmi = (bmi - anchors["bmi_mean"]) / anchors["bmi_sd"]
    z_age = ((age - parameters["conditional_means"]["age_center"])
             / parameters["conditional_means"]["nuisance_age_scale_years"])
    result = {"age": age, "sex": np.full(n, anchors["sex"]), "bmi": bmi}
    shifts_tc = np.zeros(n)
    shifts_hdl = np.zeros(n)
    for name, nuisance in parameters["nuisance_definitions"].items():
        if name == "parity" and anchors["sex"] == "M":
            continue
        weights = np.asarray(anchors["nuisance_weights"][name], dtype=float)
        categories = _quota_categories(rng, n, weights, z_bmi, z_age,
                                        nuisance["tilt_bmi"], nuisance["tilt_age"])
        labels = np.asarray(nuisance["categories"])
        result[name] = labels[categories]
        probabilities = weights / weights.sum()
        for outcome, shifts in (("tc", shifts_tc), ("hdl", shifts_hdl)):
            effects = np.asarray(nuisance["effects_" + outcome], dtype=float)
            shifts += effects[categories] - float(probabilities @ effects)
        for level in range(1, len(labels)):
            result[name + "_" + str(level)] = (categories == level).astype(int)
    means = parameters["conditional_means"]
    m_tc = (anchors["tc_level"] + anchors["reported_bmi_tc"] * z_bmi
            + means["age_tc"] * (age - means["age_center"]) + shifts_tc)
    m_hdl = (anchors["hdl_level"] + anchors["reported_bmi_hdl"] * z_bmi
             + means["age_hdl"] * (age - means["age_center"]) + shifts_hdl)
    m_nonhdl = m_tc - m_hdl
    if not (np.isfinite(m_tc).all() and np.isfinite(m_hdl).all()
            and (m_hdl > 0.0).all() and (m_nonhdl > 0.0).all()):
        raise ValueError("Conditional concentration mean outside declared positive support")
    noise = parameters["individual_variation"]
    q = noise["component_correlation"]
    common = rng.uniform(-np.sqrt(3.0), np.sqrt(3.0), n)
    independent_h = rng.uniform(-np.sqrt(3.0), np.sqrt(3.0), n)
    independent_n = rng.uniform(-np.sqrt(3.0), np.sqrt(3.0), n)
    u_h = np.sqrt(abs(q)) * common + np.sqrt(1.0 - abs(q)) * independent_h
    u_n = np.sign(q) * np.sqrt(abs(q)) * common + np.sqrt(1.0 - abs(q)) * independent_n
    hdl = m_hdl * (1.0 + noise["cv_hdl"] * u_h)
    nonhdl = m_nonhdl * (1.0 + noise["cv_nonhdl"] * u_n)
    result["total_cholesterol"] = hdl + nonhdl
    result["hdl_cholesterol"] = hdl
    return pd.DataFrame(result)


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort program accepts no individual input")
    task = json.loads(Path("/input/task.json").read_text(encoding="utf-8"))
    parameters = spec["parameters"]
    n = task["n_rows"]
    population = task["population"]
    rng = np.random.default_rng(seed)
    source_groups = parameters["context_populations"]
    if population in source_groups:
        group = source_groups[population]
        frame = _group(rng, n, group, parameters, True)
        source_sd = frame["bmi"].std(ddof=1)
        if not (np.isfinite(source_sd) and source_sd > 0.0):
            raise ValueError("Source BMI sample standard deviation is undefined")
        frame["bmi_z"] = (frame["bmi"] - frame["bmi"].mean()) / source_sd
    elif population == parameters["target_population"]:
        target = parameters["target_law"]
        groups = list(parameters["groups"])
        assignment = rng.choice(len(groups), size=n, p=target["group_probabilities"])
        pieces = []
        for index, group in enumerate(groups):
            positions = np.flatnonzero(assignment == index)
            if len(positions) == 0:
                continue
            part = _group(rng, len(positions), group, parameters, False)
            part.index = positions
            pieces.append(part)
        frame = pd.concat(pieces).sort_index()
    else:
        raise ValueError("Population is outside the frozen source/target declaration")
    frame["id"] = ["virtual_" + str(i + 1).zfill(5) for i in range(n)]
    ordered_columns = [column["name"] for column in task["columns"]]
    if not set(ordered_columns).issubset(frame.columns):
        raise ValueError("Output schema is outside the frozen generation design")
    return frame.loc[:, ordered_columns].reset_index(drop=True)

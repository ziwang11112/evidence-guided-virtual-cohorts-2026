"""Harness sampler for a frozen statistical-reference model specification.

No fitting, files, retrieval, source/ref reads, trial search or dispatch. This
module is copied unchanged as generator.py after build_spec and review. It was
not invoked during comparator preparation: all tests used analytic moments.
"""
import math
from statistics import NormalDist

import numpy as np
import pandas as pd


_NORMAL = NormalDist()
_CONTINUOUS = ("age", "bmi", "glucose", "hba1c")


def _cdf(values):
    return np.asarray([0.5 * math.erfc(-float(x) / math.sqrt(2)) for x in np.asarray(values).flat]).reshape(np.shape(values))


def _ppf(values):
    values = np.asarray(values, dtype=float)
    if not np.isfinite(values).all() or np.any(values <= 0) or np.any(values >= 1):
        raise ValueError("CDF endpoint/overflow; no clipping or redraw")
    return np.asarray([_NORMAL.inv_cdf(float(x)) for x in values.flat]).reshape(values.shape)


def _positive_transform(m, z):
    kind = m["kind"]
    if kind in {"lognormal", "shifted_lognormal"}:
        return m.get("offset", 0.0) + np.exp(m["mu"] + m["sigma"] * z)
    if kind == "truncated_lognormal":
        a = 0.0 if m["low"] == 0 else _NORMAL.cdf((math.log(m["low"]) - m["mu"]) / m["sigma"])
        b = _NORMAL.cdf((math.log(m["high"]) - m["mu"]) / m["sigma"])
        out = np.exp(m["mu"] + m["sigma"] * _ppf(a + (b - a) * _cdf(z)))
        if np.any(out <= m["low"]) or np.any(out >= m["high"]):
            raise ValueError("Truncated margin hit/exceeded support in floating point; no repair")
        return out
    raise ValueError("Unsupported positive marginal")


def validate_parameters(p):
    if p.get("family") != "sourcewise_positive_gaussian_copula_v1" or p.get("arm") not in {"E0", "E1"}:
        raise ValueError("Wrong frozen statistical family/condition")
    if p.get("case_id") not in {"CHNS2009", "ENSANUT2018"} or p.get("n_rows") != 3000:
        raise ValueError("Unbound case or row count")
    expected_count = 3 if p["case_id"] == "CHNS2009" else 1
    if len(p["components"]) != expected_count:
        raise ValueError("Wrong number of fixed donor contexts")
    expected_units = {"row_id": "identifier", "age": "year", "female": "1", "bmi": "kg/m^2",
                      "glucose": "mmol/L" if p["case_id"] == "CHNS2009" else "mg/dL", "hba1c": "%"}
    if p["units"] != expected_units:
        raise ValueError("Output units changed")
    matrices = []
    for component in p["components"]:
        names = component["variable_order"]
        if set(names) != {"age", "female", "bmi", "glucose", "hba1c"} or len(names) != 5:
            raise ValueError("Unbound variable order")
        r = np.asarray(component["latent_correlation"], dtype=float)
        if r.shape != (5, 5) or not np.isfinite(r).all() or not np.allclose(r, r.T, atol=1e-12) or not np.allclose(np.diag(r), 1, atol=1e-12) or np.linalg.eigvalsh(r).min() <= 0:
            raise ValueError("Invalid latent correlation")
        sex_i = names.index("female")
        if np.max(np.abs(np.delete(r[sex_i], sex_i))) > 1e-12:
            raise ValueError("Frozen reference requires independent binary sex")
        pp = component["marginals"]["female"]["probability"]
        if not 0 < pp < 1:
            raise ValueError("Invalid source sex fraction")
        indices = [names.index(x) for x in _CONTINUOUS]
        matrices.append(r[np.ix_(indices, indices)])
    if p["case_id"] == "CHNS2009":
        expected = {"kind": "equal_source_mixture", "component_probabilities": [1 / 3] * 3,
                    "age": {"kind": "discrete_uniform", "minimum": 35, "maximum": 74},
                    "sex": "component_source_Bernoulli_fraction"}
    else:
        expected = {"kind": "one_source_with_exact_target_design", "component_probabilities": [1.0],
                    "age_bands": [[25, 40], [40, 55], [55, 70], [70, 80]],
                    "rows_per_age_sex_cell": 375, "sex_categories": [0, 1]}
        g = p["components"][0]["marginals"]["glucose"]
        if g["kind"] != "truncated_lognormal" or g["low"] != 0.0 or g["high"] != 126.0:
            raise ValueError("ENSANUT glucose support must be built into the frozen margin")
    if p["transport"] != expected:
        raise ValueError("Fixed target transport rule changed")
    return matrices


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This reference has no participant input")
    if type(seed) is not int or not 0 <= seed <= 2 ** 32 - 1:
        raise ValueError("Seed must be an unsigned 32-bit integer")
    p = spec["parameters"]
    matrices = validate_parameters(p)
    n = p["n_rows"]
    rng = np.random.default_rng(seed)
    age = np.empty(n, dtype=np.int64)
    female = np.empty(n, dtype=np.int64)
    values = np.empty((n, 3), dtype=float)
    if p["case_id"] == "CHNS2009":
        donor = rng.integers(0, 3, n)
        for k, component in enumerate(p["components"]):
            indices = np.flatnonzero(donor == k)
            z = rng.standard_normal((len(indices), 4)) @ np.linalg.cholesky(matrices[k]).T
            age[indices] = 35 + np.floor(40 * _cdf(z[:, 0])).astype(np.int64)
            female[indices] = (rng.random(len(indices)) < component["marginals"]["female"]["probability"]).astype(np.int64)
            for j, name in enumerate(_CONTINUOUS[1:]):
                values[indices, j] = _positive_transform(component["marginals"][name], z[:, j + 1])
    else:
        cell_size = 375
        u = np.empty(n, dtype=float)
        offset = 0
        for band, (low, high) in enumerate(p["transport"]["age_bands"]):
            for sex in (0, 1):
                ix = slice(offset, offset + cell_size)
                age[ix] = rng.integers(low, high, cell_size)
                female[ix] = sex
                # Random latent position within each discrete age's CDF mass.
                u[ix] = band / 4 + (age[ix] - low + rng.random(cell_size)) / (4 * (high - low))
                offset += cell_size
        order = rng.permutation(n)
        age, female, u = age[order], female[order], u[order]
        za = _ppf(u)
        r = matrices[0]
        link = r[1:, 0]
        conditional = r[1:, 1:] - np.outer(link, link)
        z_rest = za[:, None] * link + rng.standard_normal((n, 3)) @ np.linalg.cholesky(conditional).T
        component = p["components"][0]
        for j, name in enumerate(_CONTINUOUS[1:]):
            values[:, j] = _positive_transform(component["marginals"][name], z_rest[:, j])
    if not np.isfinite(values).all() or np.any(values <= 0):
        raise ValueError("Invalid positive output; no clipping, repair or redraw")
    low, high = (35, 74) if p["case_id"] == "CHNS2009" else (25, 79)
    if np.any(age < low) or np.any(age > high):
        raise ValueError("Invalid integer age; no clipping or redraw")
    if p["case_id"] == "ENSANUT2018" and np.any(values[:, 1] >= 126):
        raise ValueError("Glucose selection violation; no row dropping")
    return pd.DataFrame({"row_id": [f"S01-{p['case_id']}-{p['arm']}-{seed}-{i:05d}" for i in range(n)],
                         "age": age, "female": female, "bmi": values[:, 0],
                         "glucose": values[:, 1], "hba1c": values[:, 2]})

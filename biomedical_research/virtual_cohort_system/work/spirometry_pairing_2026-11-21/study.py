"""Common scientific operators for two sex-specific FEV1/FVC distributions."""
from bisect import bisect_left
import importlib.util
from pathlib import Path

import numpy as np
from scipy.special import ndtri

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = HERE / "private"
# Reuse the archived general hashing, closure, and fixed-prediction comparison functions.
GRIP = HERE.parent / "bilateral_grip_transfer_2026-11-21"
_math_spec = importlib.util.spec_from_file_location("archived_pairing_math", GRIP / "science.py")
_math = importlib.util.module_from_spec(_math_spec)
_math_spec.loader.exec_module(_math)
canonical, gain_bounds, read, seal, sha, status = (
    _math.canonical, _math.gain_bounds, _math.read, _math.seal, _math.sha, _math.status)

SEXES = ("F", "M")
SEEDS = (48211, 48221, 48239)
N = 4096
USES = ("mean_individual_ratio_pct", "ratio_of_means_pct", "below_070_pct", "within_sex_pearson")
MARGINS = dict(zip(USES, (2.0, 2.0, 5.0, 0.05), strict=True))


def named(values):
    return {name: float(value) for name, value in zip(USES, values, strict=True)}


def grids(n=N):
    z = ndtri((np.arange(n) + .5) / n)
    def column(center, sd):
        raw = np.exp(np.sqrt(np.log1p((sd / center) ** 2)) * z)
        return center + sd * (raw - raw.mean()) / raw.std()
    result = []
    for cell in read(HERE / "MARGINAL_SOURCE.json")["cells"]:
        x = column(cell["fev1_mean"], cell["fev1_sd"])
        y = column(cell["fvc_mean"], cell["fvc_sd"])
        assert np.all((0 < x) & (x <= y)) and np.all(np.diff(y) > 0)
        result.append((cell["sex"], x, y))
    assert tuple(c[0] for c in result) == SEXES
    return result


def validate_order(order, size):
    a = np.asarray(order)
    if a.shape != (size,) or a.dtype.kind not in "iu" or not np.array_equal(np.sort(a), np.arange(size)):
        raise ValueError("Expected one complete integer permutation per sex")
    return a


def project(x, y, proposal):
    """Closest remaining eligible rank while assigning the largest FEV1 first."""
    raw = validate_order(proposal, len(x))
    if np.all(x <= y[raw]):
        return raw.copy()
    remaining = list(range(len(y)))
    fitted = np.empty_like(raw)
    mins = np.searchsorted(y, x, side="left")
    for i in range(len(x) - 1, -1, -1):
        floor = bisect_left(remaining, mins[i])
        if floor == len(remaining):
            raise ValueError("No feasible assignment for the given marginals")
        rank = raw[i]
        hi = bisect_left(remaining, rank, lo=floor)
        if hi == len(remaining) or (hi > floor and rank - remaining[hi-1] <= remaining[hi] - rank):
            hi -= 1
        fitted[i] = remaining.pop(hi)
    assert np.all(x <= y[fitted])
    return fitted


def comparator(groups, seed, joint):
    rng = np.random.default_rng(seed)
    joint_rows = {r["sex"]: r for r in read(HERE / "JOINT_SOURCE.json")["cells"]} if joint else {}
    result, latent = [], {}
    for sex, x, y in groups:
        if joint:
            cx, cy = x.std()/x.mean(), y.std()/y.mean()
            param = np.log1p(joint_rows[sex]["pearson"] * cx * cy) / np.sqrt(np.log1p(cx*cx) * np.log1p(cy*cy))
            rho = np.clip(param, -1., 1.)
            z = ndtri((np.arange(len(x))+.5)/len(x))
            score = rho*z + np.sqrt(1-rho*rho)*rng.normal(size=len(x))
            order = np.argsort(np.argsort(score, kind="stable"), kind="stable")
            latent[sex] = {"unclipped":float(param), "used":float(rho)}
        else:
            remaining = list(range(len(y)))
            floor = np.searchsorted(y, x, side="left")
            order = np.empty(len(x), dtype=int)
            for i in range(len(x)-1, -1, -1):
                first = bisect_left(remaining, floor[i])
                order[i] = remaining.pop(rng.integers(first, len(remaining)))
        result.append(order)
    return np.stack(result), latent


def moments(x, y):
    return np.column_stack((x, y, x/y, (x/y < .70).astype(float), x*x, y*y, x*y))


def from_moments(two, allow_constant=False):
    """Both virtual and measured rows use the same sex-standardized estimator."""
    two = np.asarray(two)
    if two.shape != (2, 7):
        raise ValueError("Two sex groups with seven moments each are required")
    mx, my, mr, low, xx, yy, xy = two.T
    vx, vy = xx-mx*mx, yy-my*my
    tolerance = 32 * np.finfo(float).eps
    valid = (vx > tolerance * xx) & (vy > tolerance * yy)
    if not valid.all() and not allow_constant:
        raise ValueError("Within-sex correlation is undefined in a constant group")
    correlation = np.mean((xy-mx*my)/np.sqrt(vx*vy)) if valid.all() else np.nan
    return np.array([100*mr.mean(), 100*mx.mean()/my.mean(), 100*low.mean(),
                     correlation])


def score(groups, orders):
    avgs = []
    for (_, x, y), order in zip(groups, orders, strict=True):
        ids = validate_order(order, len(x))
        avgs.append(moments(x, y[ids]).mean(axis=0))
    return from_moments(avgs)


def fit(groups, raw):
    final = np.stack([project(x, y, order) for (_, x, y), order in zip(groups, raw, strict=True)])
    invalid = [np.count_nonzero(x > y[o]) for (_,x,y),o in zip(groups,raw,strict=True)]
    n = sum(len(x) for _,x,_ in groups)
    assert all(np.all(x <= y[o]) for (_,x,y),o in zip(groups,final,strict=True))
    return final, {"raw_invalid_rows":int(sum(invalid)), "changed_pairs":int(np.count_nonzero(raw != final)),
                   "final_invalid_rows":0, "rows":n}


def target_grids(frame):
    out = []
    for sex in SEXES:
        g = frame[frame.sex == sex]
        prob = (np.arange(N) + .5) / N
        def q(column):
            order = np.argsort(column, kind="stable")
            c = np.cumsum(g.w.to_numpy()[order])
            return column[order][np.searchsorted(c, prob * c[-1], side="left")]
        out.append((sex, q(g.x.to_numpy()), q(g.y.to_numpy())))
    return out

"""One A-only, conditionally independent statistical law. No file or reference access."""
from dataclasses import dataclass
from math import exp, inf, log, pi, sqrt

import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import log_ndtr, ndtr, ndtri


BANDS = [("<12", 0.0, 12.0), ("12 to <14", 12.0, 14.0), (">=14", 14.0, inf)]
K = log(15.0)
LOG_SQRT_2PI = log(2.0 * pi) / 2.0


def tilted_normal_moments(t, p):
    log_phi = -t * t / 2.0 - LOG_SQRT_2PI
    below = exp(log_phi - log_ndtr(t))
    above = exp(log_phi - log_ndtr(-t))
    mean_z = (1.0 - p) * above - p * below
    variance_z = 1.0 + t * mean_z - mean_z * mean_z
    if variance_z <= 0:
        raise ValueError("Conditional log-ferritin variance is infeasible")
    return mean_z, variance_z


@dataclass(frozen=True)
class Band:
    weight: float
    lo: float
    hi: float
    first_shape: float
    second_shape_or_scale: float
    p: float
    mu: float
    sigma: float
    t: float

    def draw(self, rng, n):
        if self.hi == inf:
            hb = self.lo + rng.gamma(self.first_shape, self.second_shape_or_scale, n)
        else:
            hb = self.lo + (self.hi - self.lo) * rng.beta(self.first_shape, self.second_shape_or_scale, n)
        u = rng.random(n)
        below = u < self.p
        z = np.empty(n)
        tiny = np.nextafter(0.0, 1.0)
        low_cdf = np.maximum(tiny, ndtr(self.t) * (u[below] / self.p))
        upper_survival = np.maximum(tiny, ndtr(-self.t) * ((1.0 - u[~below]) / (1.0 - self.p)))
        z[below], z[~below] = ndtri(low_cdf), -ndtri(upper_survival)
        fe = np.exp(self.mu + self.sigma * z)
        if not ((hb >= self.lo) & (hb < self.hi) & (hb > 0) & (fe > 0) & np.isfinite(fe)).all():
            raise ValueError("Draw failed support checks")
        if not np.array_equal(below, fe < 15.0):
            raise ValueError("A sampled ferritin threshold status changed in conversion")
        return hb, fe

    def log_fe_cdf(self, y):
        z = (y - self.mu) / self.sigma
        if y < K:
            return self.p * ndtr(z) / ndtr(self.t)
        return 1.0 - (1.0 - self.p) * ndtr(-z) / ndtr(-self.t)

    def integrate(self, transform, below_only=False):
        def integrate_side(low, high, mass, tail_mass):
            def integrand(z):
                return exp(-z * z / 2.0 - LOG_SQRT_2PI) * transform(self.mu + self.sigma * z)
            return (mass / tail_mass) * quad(integrand, low, high, epsabs=2e-12, epsrel=2e-12)[0]
        lower = integrate_side(-inf, self.t, self.p, ndtr(self.t))
        if below_only:
            return lower
        return lower + integrate_side(self.t, inf, 1.0 - self.p, ndtr(-self.t))


def fit(tables):
    rows = tables["table_2"]["rows"]
    if len(rows) != len(BANDS):
        raise ValueError("Wrong Hb band count")
    n_total = sum(r["n"] for r in rows)
    bands = []
    for r, (label, lo, hi) in zip(rows, BANDS, strict=True):
        if r["Hb_band"] != label:
            raise ValueError("Unexpected Hb band")
        p = r["depleted"] / r["n"]
        shifted_mean, sd = r["hb_mean"] - lo, r["hb_sd"]
        if hi == inf:
            first, second = (shifted_mean / sd) ** 2, sd * sd / shifted_mean
        else:
            fraction = shifted_mean / (hi - lo)
            concentration = fraction * (1 - fraction) / (sd / (hi - lo)) ** 2 - 1
            first, second = fraction * concentration, (1 - fraction) * concentration
        if min(first, second) <= 0 or not 0 < p < 1:
            raise ValueError("Infeasible source band parameters")
        mean_y, sd_y = log(r["ferritin_gm"]), log(r["ferritin_gsd"])

        def equation(t):
            mean_z, variance_z = tilted_normal_moments(t, p)
            return (mean_z - t) / sqrt(variance_z) - (mean_y - K) / sd_y

        t = brentq(equation, -8.0, 8.0, xtol=1e-13)
        sigma = sd_y / sqrt(tilted_normal_moments(t, p)[1])
        bands.append(Band(r["n"] / n_total, lo, hi, first, second, p, K - sigma * t, sigma, t))
    cases = [[rows[0]["depleted"], rows[0]["n"] - rows[0]["depleted"]],
             [sum(r["depleted"] for r in rows[1:]), sum(r["n"] - r["depleted"] for r in rows[1:])]]
    if cases != tables["table_1"]["counts"]:
        raise ValueError("The two source tables disagree on threshold counts")
    return bands


def draw(bands, seed, n):
    rng = np.random.default_rng(seed)
    memberships = rng.choice(len(bands), size=n, p=[b.weight for b in bands])
    hb, fe = np.empty(n), np.empty(n)
    for index, band in enumerate(bands):
        keep = memberships == index
        hb[keep], fe[keep] = band.draw(rng, int(keep.sum()))
    return pd.DataFrame({"hb_g_dl": hb, "ferritin_ug_l": fe})


def population(bands, source):
    """Integrate the fitted law; validate the fit separately from finite draws."""
    expected_uv, previous = 0.0, 0.0
    diagnostics = []
    for band, row in zip(bands, source["table_2"]["rows"], strict=True):
        mass = band.integrate(lambda y: 1.0)
        p = band.integrate(lambda y: 1.0, below_only=True)
        mean_y = band.integrate(lambda y: y)
        variance_y = band.integrate(lambda y: (y - mean_y) ** 2)
        a, b = band.first_shape, band.second_shape_or_scale
        if band.hi == inf:
            hb_mean, hb_sd = band.lo + a * b, sqrt(a) * b
        else:
            hb_mean = band.lo + (band.hi - band.lo) * a / (a + b)
            hb_sd = (band.hi - band.lo) * sqrt(a * b / ((a + b) ** 2 * (a + b + 1)))
        actual = [mass, p, hb_mean, hb_sd, exp(mean_y), exp(sqrt(variance_y))]
        want = [1, row["depleted"] / row["n"], row["hb_mean"], row["hb_sd"], row["ferritin_gm"], row["ferritin_gsd"]]
        np.testing.assert_allclose(actual, want, atol=2e-10, rtol=2e-10)
        diagnostics.append(dict(zip(["mass", "p_depleted", "hb_mean", "hb_sd", "ferritin_gm", "ferritin_gsd"], actual)))
        u = previous + band.weight / 2.0
        v = band.integrate(lambda y: sum(b.weight * b.log_fe_cdf(y) for b in bands))
        expected_uv += band.weight * u * v
        previous += band.weight
    low, other = bands[0], bands[1:]
    fe_low_other = sum(b.weight * b.p for b in other)
    fe_high_other = sum(b.weight * (1 - b.p) for b in other)
    odds = (low.p * fe_high_other) / ((1.0 - low.p) * fe_low_other)
    return {"rank": 12.0 * expected_uv - 3.0, "odds_ratio": odds, "groups": diagnostics}

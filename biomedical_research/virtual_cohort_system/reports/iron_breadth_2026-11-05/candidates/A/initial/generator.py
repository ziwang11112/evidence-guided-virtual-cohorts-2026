"""Sample continuous Hb and raw ferritin from the declared joint model."""

import numpy as np
import pandas as pd


# S1 Table III counts. The three integer low-ferritin counts reproduce the
# rounded percentages as well as the combined S1 Table IV cells.
_BAND_COUNTS = np.array([53, 205, 1413])
_LOW_PROB = np.array([50, 123, 331]) / _BAND_COUNTS
_FERRITIN_GM = np.array([1.3, 5.9, 22.3])
_RANK_KNOTS = np.array([0, 0.05, 0.25, 0.5, 0.75, 0.95, 1])
_HB_KNOTS = np.array([
    [5.5, 7.5, 8.6, 9.2, 9.65, 9.94, 10.0],
    [10.0, 10.2, 10.85, 11.38, 11.72, 11.95, 12.0],
    [12.0, 12.2, 12.7, 13.25, 13.9, 14.85, 17.0],
])
_HIGH_LOG_EXCESS = 0.85
_MAX_LOG_DEFICIT = np.log(15.0 / 0.1)


def _source_curves():
    """Continuous piecewise-linear depletion probability and mean log gap."""
    prob_edges = [0.993]
    gap_edges = [2.8]
    for probability, ferritin_gm in zip(_LOW_PROB, _FERRITIN_GM):
        left = prob_edges[-1]
        right = 2.0 * probability - left
        prob_edges.append(right)
        # U is uniform within each source Hb band. Integrate u * p(u).
        mean_rank_if_low = (left / 2.0 + (right - left) / 3.0) / probability
        mean_gap = (np.log(15.0 / ferritin_gm)
                    + (1.0 - probability) * _HIGH_LOG_EXCESS) / probability
        gap_edges.append(gap_edges[-1] + (mean_gap - gap_edges[-1])
                         / mean_rank_if_low)
    return np.array(prob_edges), np.array(gap_edges)


def _draw_hb(n, rng, depletion_weight, prob_edges):
    """Sample the Hb marginal after applying the low-ferritin weight."""
    acceptance = 1.0 - (1.0 - depletion_weight) * _LOW_PROB
    mass = _BAND_COUNTS * acceptance
    band = rng.choice(3, size=n, p=mass / mass.sum())
    uniform = rng.random(n)
    left = prob_edges[band]
    slope = prob_edges[band + 1] - left
    # Density of the reweighted Hb rank is proportional to w0 + w1 * u.
    w0 = 1.0 - (1.0 - depletion_weight) * left
    w1 = -(1.0 - depletion_weight) * slope
    rhs = uniform * acceptance[band]
    rank = 2.0 * rhs / (w0 + np.sqrt(w0 * w0 + 2.0 * w1 * rhs))
    hb = np.empty(n)
    for index, knots in enumerate(_HB_KNOTS):
        rows = band == index
        hb[rows] = np.interp(rank[rows], _RANK_KNOTS, knots)
    return hb, band, rank


def generate(n, rng, context):
    """Return ordered Hb and ferritin columns for a specified population."""
    if context not in ("zhu_source", "target"):
        raise ValueError("Unknown population context")
    weight = 1.0 if context == "zhu_source" else 2.0 / 3.0
    prob_edges, gap_edges = _source_curves()
    hb, band, rank = _draw_hb(n, rng, weight, prob_edges)
    source_p = prob_edges[band] + rank * (prob_edges[band + 1] - prob_edges[band])
    low_p = weight * source_p / (1.0 - (1.0 - weight) * source_p)
    low = rng.random(n) < low_p
    ferritin = np.empty(n)

    gap = gap_edges[band[low]] + rank[low] * np.diff(gap_edges)[band[low]]
    fraction = gap / _MAX_LOG_DEFICIT
    deficit = _MAX_LOG_DEFICIT * rng.beta(5.0 * fraction, 5.0 * (1.0 - fraction))
    ferritin[low] = 15.0 * np.exp(-deficit)
    surplus = rng.gamma(1.6, _HIGH_LOG_EXCESS / 1.6, size=np.count_nonzero(~low))
    ferritin[~low] = 15.0 * np.exp(surplus)

    if context == "target":
        # For a fraction of rows the Hb draw has other determinants, represented
        # by an independent draw from the same target Hb marginal.
        independent = rng.random(n) < 0.2
        hb[independent] = _draw_hb(np.count_nonzero(independent), rng, weight,
                                   prob_edges)[0]
    return pd.DataFrame({"hb_g_dl": hb, "ferritin_ug_l": ferritin})

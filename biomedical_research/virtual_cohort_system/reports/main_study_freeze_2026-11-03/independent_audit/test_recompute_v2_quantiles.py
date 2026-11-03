"""Deterministic invented-array tests for the prescribed weighted quantiles.

No clinical or generated artifact is read. The primary engine/provider is not
imported. Fraction supplies an independently implemented exact-binary summation
oracle; the second local oracle transcribes the pinned cutoff specification.
Comparisons are exact selected values, never tolerances or adjacent ranks.
"""
from fractions import Fraction
import unittest

import numpy as np

import recompute_v2 as audit


def fraction_prefixes(values, weights):
    """Correctly round each exact sum of the supplied binary row weights."""
    pairs = sorted((float(value), index, float(weight))
                   for index, (value, weight) in enumerate(zip(values, weights))
                   if weight > 0)
    total = Fraction(0)
    cumulative = []
    ordered_values = []
    for value, _, weight in pairs:
        total += Fraction.from_float(weight)
        cumulative.append(float(total))
        ordered_values.append(value)
    return ordered_values, cumulative


def exact_binary_oracle(values, weights, probability):
    ordered, cumulative = fraction_prefixes(values, weights)
    threshold = float(probability) * cumulative[-1]
    return next((value for value, mass in zip(ordered, cumulative)
                 if mass >= threshold), ordered[-1])


def pinned_cutoff_oracle(values, weights, probability):
    """Local specification oracle; never imports the original implementation."""
    values = np.asarray(values, dtype=np.float64)
    weights = np.asarray(weights, dtype=np.float64)
    keep = weights > 0
    values, weights = values[keep], weights[keep]
    order = np.argsort(values, kind="stable")
    values, weights = values[order], weights[order]
    prefixes = []
    subtotal = 0.0
    correction = 0.0
    for weight in weights:
        updated = subtotal + weight
        if abs(subtotal) >= abs(weight):
            correction += (subtotal - updated) + weight
        else:
            correction += (weight - updated) + subtotal
        subtotal = updated
        prefixes.append(subtotal + correction)
    threshold = float(probability) * prefixes[-1]
    index = int(np.searchsorted(prefixes, threshold, side="left"))
    return float(values[min(index, len(values) - 1)])


class WeightedQuantileV2Tests(unittest.TestCase):
    def check_fixture(self, values, weights, probabilities):
        for probability in probabilities:
            with self.subTest(probability=probability):
                expected = exact_binary_oracle(values, weights, probability)
                self.assertEqual(pinned_cutoff_oracle(values, weights, probability), expected)
                self.assertEqual(audit.inverse_weighted_quantile(values, weights, probability), expected)

    def test_exact_3000_quota_weights_decimal_cutoffs(self):
        # These are the actual quota-weight bytes, without rescaling by sum().
        values = np.arange(3000, dtype=np.float64)
        weights = np.full(3000, 1.0 / (8.0 * 375), dtype=np.float64)
        self.check_fixture(values, weights, (0.0, 0.1, 0.5, 0.9, 1.0))
        self.check_fixture(values[::-1], weights[::-1], (0.1, 0.5, 0.9))

    def test_equal_weight_boundary_and_immediate_neighbors(self):
        values = np.arange(3000, dtype=np.float64)
        weights = np.full(3000, 1.0 / (8.0 * 375), dtype=np.float64)
        _, cumulative = fraction_prefixes(values, weights)
        probabilities = []
        for index in (299, 1499, 2699):
            q = cumulative[index] / cumulative[-1]
            probabilities.extend((np.nextafter(q, 0.0), q, np.nextafter(q, 1.0)))
        self.check_fixture(values, weights, probabilities)

    def test_uneven_demographic_cells_keep_original_weight_scale_and_order(self):
        # All eight nonempty cells; exactly 3000 invented observations overall.
        counts = np.array([231, 283, 347, 389, 419, 433, 457, 441])
        self.assertEqual(int(counts.sum()), 3000)
        cells = np.repeat(np.arange(8), counts)
        weights = 1.0 / (8.0 * counts[cells])
        # Coprime modular ordering deterministically interleaves cell weights.
        values = ((np.arange(3000) * 37) % 3000).astype(np.float64)
        _, cumulative = fraction_prefixes(values, weights)
        probabilities = [0.0, 0.1, 0.5, 0.9, 1.0]
        for index in (299, 1499, 2699):
            q = cumulative[index] / cumulative[-1]
            probabilities.extend((np.nextafter(q, 0.0), q, np.nextafter(q, 1.0)))
        self.check_fixture(values, weights, probabilities)
        self.check_fixture(values[::-1], weights[::-1], (0.1, 0.5, 0.9))

    def test_ties_retain_sorted_original_row_masses(self):
        counts = np.array([231, 283, 347, 389, 419, 433, 457, 441])
        cells = np.repeat(np.arange(8), counts)
        weights = 1.0 / (8.0 * counts[cells])
        values = (((np.arange(3000) * 37) % 3000) // 7).astype(np.float64)
        self.check_fixture(values, weights, (0.0, 0.1, 0.5, 0.9, 1.0))
        self.check_fixture(values[::-1], weights[::-1], (0.1, 0.5, 0.9))

    def test_zero_mass_and_simple_left_inverse(self):
        values = np.array([-100.0, 9.0, 1.0, 3.0, 100.0])
        weights = np.array([0.0, 0.1, 0.4, 0.5, 0.0])
        self.check_fixture(values, weights, (0.0, 0.4, 0.5, 0.9, 1.0))
        self.assertEqual(audit.inverse_weighted_quantile(values, weights, 0.4), 1.0)
        self.assertEqual(audit.inverse_weighted_quantile(values, weights, 0.5), 3.0)


if __name__ == "__main__":
    unittest.main()

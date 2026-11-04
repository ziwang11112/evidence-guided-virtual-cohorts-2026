"""Only invented deterministic math: no generate(), RNG, fitting or HRS draws."""
import unittest
import numpy as np
from generator import _gamma_parameters, _linear, _random_covariance, _softmax


class AnalyticHelpers(unittest.TestCase):
    def test_softmax_reference_and_overflow(self):
        np.testing.assert_allclose(_softmax(np.array([[0., 0., 0.], [0., np.log(2), np.log(3)]])),
                                   [[1/3, 1/3, 1/3], [1/6, 2/6, 3/6]])
        p = _softmax(np.array([[2000., 2001., 2002.]]))
        np.testing.assert_allclose(p, _softmax(np.array([[0., 1., 2.]])))
        self.assertTrue(np.isfinite(p).all())

    def test_gamma_mean_and_variance(self):
        mean = np.array([2., 3., 8.])
        phi = 0.4
        shape, scale = _gamma_parameters(mean, phi)
        np.testing.assert_allclose(shape * scale, mean)
        np.testing.assert_allclose(shape * scale ** 2, phi * mean ** 2)
        with self.assertRaises(ValueError):
            _gamma_parameters(mean, 0)

    def test_covariance_uses_sd_not_other_variance(self):
        parameters = {'intercept_sd': {'value': 2.}, 'slope_sd': {'value': 3.},
                      'correlation': {'value': -0.25},
                      'printed_intercept_variance': {'value': 999.}}
        covariance = _random_covariance(parameters)
        np.testing.assert_array_equal(covariance, [[4., -1.5], [-1.5, 9.]])
        self.assertGreater(np.linalg.eigvalsh(covariance).min(), 0)
        age = np.array([-1., 0., 2.])
        design = np.column_stack([np.ones(3), age])
        np.testing.assert_allclose(np.diag(design @ covariance @ design.T), 4 - 3*age + 9*age**2)

    def test_linear_by_named_terms(self):
        features = {'(Intercept)': np.ones(3), 'age60': np.array([-1., 0., 2.]),
                    'hba1c_U65': np.array([-2., 0., 0.])}
        features['age60:hba1c_U65'] = features['age60'] * features['hba1c_U65']
        coefficients = {'(Intercept)': {'estimate': 0.5}, 'age60': {'estimate': 2.},
                        'hba1c_U65': {'estimate': 3.}, 'age60:hba1c_U65': {'estimate': -2.}}
        np.testing.assert_allclose(_linear(features, coefficients), [-11.5, 0.5, 4.5])


if __name__ == '__main__':
    unittest.main(verbosity=2)

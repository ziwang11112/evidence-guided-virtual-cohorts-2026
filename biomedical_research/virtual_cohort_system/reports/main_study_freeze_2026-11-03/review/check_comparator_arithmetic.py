"""Independent deterministic toy integration; never fit an actual case or sample."""
from pathlib import Path
import hashlib
import json
import math
import sys

import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr, ndtri

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "comparator"))
import moment_reference as mr
import generator


def run():
    # Direct density integration is independent of the implementation's closed
    # truncated-moment expression and uses fixed invented distribution inputs.
    mu, sigma, lower, upper = 1.4, .35, 1.0, 8.0
    m = {"kind": "truncated_lognormal", "mu": mu, "sigma": sigma, "low": lower, "high": upper}
    a, b = (math.log(lower) - mu) / sigma, (math.log(upper) - mu) / sigma
    mass = ndtr(b) - ndtr(a)
    def density(x):
        z = (math.log(x) - mu) / sigma
        return math.exp(-z*z/2) / (x * sigma * math.sqrt(2*math.pi) * mass)
    first = quad(lambda x: x*density(x), lower, upper, epsabs=1e-11, epsrel=1e-11)[0]
    second = quad(lambda x: x*x*density(x), lower, upper, epsabs=1e-11, epsrel=1e-11)[0]
    actual = mr.marginal_moments(m)
    assert np.allclose(actual, [first, second-first*first], atol=1e-10, rtol=0)
    # Cov(g(Z1), Z2) = rho E[Z1*g(Z1)] for correlated normal inputs.
    rho = .37
    def integrand(z):
        value = math.exp(mu + sigma*ndtri(ndtr(a) + mass*ndtr(z)))
        return z*value*math.exp(-z*z/2)/math.sqrt(2*math.pi)
    independent_cov = rho*quad(integrand, -8, 8, epsabs=1e-10, epsrel=1e-10, limit=100)[0]
    normal = {"kind": "normal", "mean": 0.0, "sd": 1.0}
    actual_cov = mr.pair_covariance(m, normal, rho, 128)
    assert abs(actual_cov-independent_cov) < 1e-9
    # This invokes only the deterministic marginal transform on fixed toy nodes,
    # never generator.generate, a RNG or a biomedical table constructor.
    z = np.array([-3., -1., 0., .5, 2.])
    sampler_transform = generator._positive_transform(m, z)
    moment_transform = mr._transform(m, z)
    assert np.allclose(sampler_transform, moment_transform, atol=1e-12, rtol=0)
    assert np.all(sampler_transform > lower) and np.all(sampler_transform < upper)
    report = {"status": "passed", "checks": ["truncated_moments_match_independent_density_integrals", "truncated_normal_covariance_matches_independent_conditional_identity", "sampler_and_analytic_transform_match_on_fixed_toy_nodes", "strict_support_on_fixed_toy_nodes"], "actual_case_fit": False, "generator_generate_called": False, "clinical_rows_or_target_reports_read": False,
              "source_file_sha256": {n: hashlib.sha256((ROOT / "comparator" / n).read_bytes()).hexdigest() for n in ("moment_reference.py", "generator.py")}}
    (ROOT / "review/COMPARATOR_ARITHMETIC_CHECK.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))

if __name__ == "__main__":
    run()

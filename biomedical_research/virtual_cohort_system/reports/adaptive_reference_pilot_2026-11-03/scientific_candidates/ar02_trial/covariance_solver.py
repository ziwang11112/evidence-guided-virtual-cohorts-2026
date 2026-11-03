"""Retained 2026-11-03 after the identical inline deterministic calculation.

No random draws, sampled persons, synthetic tables, or generator execution.
Use --core-rho .40 to reproduce ar01; --core-rho .28 for ar02.
Reads the retained marginal analytic_fit.json and prints derived values only.
The first inline attempt lacked numerical clipping and failed bracketing;
the successful inline calculation added the probability clipping below.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.special import ndtr, ndtri
from scipy.optimize import brentq
from numpy.polynomial.hermite import hermgauss

parser = argparse.ArgumentParser()
parser.add_argument('--core-rho', type=float, required=True)
args = parser.parse_args()
candidate = Path(__file__).parent
fit = json.loads((candidate/'analytic_fit.json').read_text())
ref = json.loads((candidate.parent.parent/'input/reference_summary.json').read_text())
x, w = hermgauss(64)
x = x*np.sqrt(2)
w = w/np.sqrt(np.pi)
weights = w[:, None]*w[None, :]


def quantile(z, mu, sigma, low, high):
    a = ndtr((np.log(low)-mu)/sigma)
    b = ndtr((np.log(high)-mu)/sigma)
    probability = np.clip(a+(b-a)*ndtr(z), 1e-15, 1-1e-15)
    return np.clip(np.exp(mu+sigma*ndtri(probability)), low, high)


def cross_moment(component, rho):
    g = fit['glucose_components'][component*2:component*2+2]
    h = fit['hba1c_components'][component*2:component*2+2]
    glucose = quantile(x[:, None], *g, 2.5, 25)
    hba1c = quantile(rho*x[:, None]+np.sqrt(1-rho*rho)*x[None, :],
                      *h, 3.5, 16)
    return float((weights*glucose*hba1c).sum())


p = fit['p_high']
g_mean = fit['expected_glucose_mean_sd_cdfs'][0]
h_mean = fit['expected_hba1c_mean_sd_cdfs'][0]
g_var = ref['diagnostics']['marginal']['glucose']['sd']**2
age_var = ref['diagnostics']['marginal']['age']['sd']**2
needed_covariance = ref['estimands']['E2']['coefficient']*(
    g_var-fit['glucose_age_slope']**2*age_var)
rho1 = brentq(lambda rho: (1-p)*cross_moment(0, args.core_rho)
               +p*cross_moment(1, rho)-g_mean*h_mean-needed_covariance,
               .01, .99)
print(json.dumps({'copula_correlations':[args.core_rho, rho1],
                  'expected_baseline_covariance':needed_covariance}, indent=2))

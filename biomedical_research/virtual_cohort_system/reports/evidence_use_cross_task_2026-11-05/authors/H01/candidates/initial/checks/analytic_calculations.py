"""Deterministic source arithmetic and quadrature only; never generates cohort rows."""
import json
import math
from pathlib import Path
import numpy as np
from scipy.special import ndtr, roots_jacobi

BUNDLE = Path(__file__).resolve().parent

def calculations(order):
    lower, upper, mean_b, sd_b = 12.0, 65.0, 28.01, 5.0
    width = upper - lower
    fraction = (mean_b-lower)/width
    concentration = (mean_b-lower)*(upper-mean_b)/(sd_b**2)-1
    alpha, beta = fraction*concentration, (1-fraction)*concentration
    nodes, weights = roots_jacobi(order, beta-1, alpha-1)
    weights = weights/weights.sum()
    bmi = lower + width*(nodes+1)/2
    # Source marginal Pearson covariance scale, NOT an adjusted source slope.
    gamma = .23*.73/12.4
    glucose_bmi = .0240*18.0
    glucose_female = -.2472*18.0
    hba_bmi = .0125-gamma*glucose_bmi
    hba_female = .023-gamma*glucose_female
    coef = np.array([.01, hba_female, hba_bmi, gamma])
    e1 = np.zeros(4)
    e2 = np.zeros((4, 4))
    eg = 0.0
    eg2 = 0.0
    xg = np.zeros(4)
    # Quadrature nodes are deterministic weighted integration abscissae;
    # no identifier, fictional person, random number or output table exists.
    for low_a, high_a in [(25,39),(40,54),(55,69),(70,79)]:
        for age in range(low_a, high_a+1):
            for female in [0,1]:
                mass = 1/(8*(high_a-low_a+1))
                X = np.stack([np.ones(order), np.full(order, age-50),
                              np.full(order, female-.5), bmi-mean_b], axis=1)
                mu = 94+.18*(age-50)+glucose_female*(female-.5)+glucose_bmi*(bmi-mean_b)
                lo, hi = -mu/10, (126-mu)/10
                plo = np.exp(-lo**2/2)/math.sqrt(2*math.pi)
                phi = np.exp(-hi**2/2)/math.sqrt(2*math.pi)
                normalizer = ndtr(hi)-ndtr(lo)
                delta = (plo-phi)/normalizer
                mg = mu+10*delta
                vg = 100*(1+(lo*plo-hi*phi)/normalizer-delta**2)
                w = weights*mass
                e1 += np.sum(w[:,None]*X,axis=0)
                e2 += X.T@(w[:,None]*X)
                xg += np.sum((w*mg)[:,None]*X,axis=0)
                eg += np.sum(w*mg)
                eg2 += np.sum(w*(vg+mg**2))
    projected_glucose = np.linalg.solve(e2,xg)
    mean_predictors = np.r_[e1[1:], eg-94]
    raw_cross = np.empty((4,4))
    raw_cross[:3,:3] = e2[1:,1:]
    raw_cross[:3,3] = xg[1:]-94*e1[1:]
    raw_cross[3,:3] = raw_cross[:3,3]
    raw_cross[3,3] = eg2-188*eg+94**2
    covariance = raw_cross-np.outer(mean_predictors,mean_predictors)
    mh = 5.45+coef@mean_predictors
    vh = coef@covariance@coef+.35**2
    gh_cov = covariance[3,:]@coef
    return {
        "quadrature_order": order,
        "bmi_beta_alpha": float(alpha), "bmi_beta_beta": float(beta),
        "bmi_concentration": float(concentration),
        "source_marginal_glucose_hba1c_slope_pp_per_mg_dl": gamma,
        "source_reciprocal_glucose_on_hba1c_slope_mg_dl_per_pp": .23*12.4/.73,
        "reported_crude_slope_product": .13*.38,
        "reported_r_squared": .23**2,
        "source_scale_implied_crude_forward_ratio_to_reported": (.23*.73/12.4)/.13,
        "hba1c_conditional_bmi_coefficient_pp_per_kg_m2": hba_bmi,
        "hba1c_conditional_female_coefficient_pp": hba_female,
        "glucose_projection_raw_intercept_age_female_bmi": projected_glucose.tolist(),
        "model_implied_Q1_age10": .10,
        "model_implied_Q2_bmi5": 5*(hba_bmi+gamma*projected_glucose[3]),
        "model_implied_Q3_bmi5": 5*hba_bmi,
        "model_implied_glucose_mean": float(eg),
        "model_implied_glucose_sd": float(math.sqrt(eg2-eg**2)),
        "model_implied_hba1c_mean": float(mh),
        "model_implied_hba1c_sd": float(math.sqrt(vh)),
        "model_implied_glucose_hba1c_pearson": float(gh_cov/math.sqrt((eg2-eg**2)*vh)),
        "hba1c_global_lower_bound": float(5.45-.01*25+hba_bmi*(12-mean_b)-gamma*94-abs(hba_female)/2-1.05),
    }

if __name__ == '__main__':
    result = {"scope":"Source arithmetic and deterministic model integration; no random draws, cohort tables, target observations, candidate execution, or validation.",
              "runs":[calculations(128), calculations(256)]}
    (BUNDLE/'analytic_outputs.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

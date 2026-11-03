"""Deterministic summary fitting only: no RNG, cohort, or generator execution.

The retained script fits analytic distribution moments/CDFs and finite Gaussian
quadrature integrals to the explicitly supplied CHNS development summaries.
Integration nodes are numerical quadrature nodes, never synthetic participants.
"""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from scipy.optimize import least_squares
from scipy.special import ndtr, ndtri
from numpy.polynomial.hermite_e import hermegauss

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent.parent
REF = json.loads((BUNDLE / "input/reference_summary.json").read_text(encoding="utf-8-sig"))
EVIDENCE = json.loads((BUNDLE / "input/compiled_evidence.json").read_text(encoding="utf-8-sig"))
M = REF["diagnostics"]["marginal"]


def write_json(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def moments(mus, sigmas, weights):
    mus, sigmas, weights = map(np.asarray, (mus, sigmas, weights))
    mean = np.sum(weights * np.exp(mus + 0.5 * sigmas**2))
    second = np.sum(weights * np.exp(2 * mus + 2 * sigmas**2))
    return float(mean), float(second - mean**2)


def mixture_tuple(x):
    p, mu0, s0, dmu, s1 = x
    return np.array([mu0, mu0 + dmu]), np.array([s0, s1]), np.array([1-p, p])


def fit_margin(var):
    target = M[var]
    q = np.array([target["q10"], target["median"], target["q90"]])
    def residual(x):
        mus, sigmas, weights = mixture_tuple(x)
        mean, variance = moments(mus, sigmas, weights)
        cdfs = np.sum(weights * ndtr((np.log(q)[:, None]-mus)/sigmas), axis=1)
        return np.r_[(mean-target["mean"])/target["sd"],
                     (math.sqrt(variance)-target["sd"])/target["sd"],
                     cdfs-np.array([0.1, 0.5, 0.9])]
    x0 = [0.08, math.log(target["median"]*0.985), 0.115 if var == "glucose" else 0.065, 0.53, 0.25]
    fit = least_squares(residual, x0,
                        bounds=([0.005, math.log(3), 0.025, 0.05, 0.05],
                                [0.25, math.log(7), 0.30, 1.2, 0.65]),
                        xtol=1e-13, ftol=1e-13, gtol=1e-13, max_nfev=2500)
    mus, sigmas, weights = mixture_tuple(fit.x)
    return {"log_means": mus.tolist(), "log_sds": sigmas.tolist(), "probabilities": weights.tolist()}, {
        "success": bool(fit.success), "function_evaluations": int(fit.nfev),
        "max_absolute_scaled_residual": float(np.max(np.abs(residual(fit.x)))),
        "residual_definition": "mean and SD residuals divided by supplied individual SD; then three CDF residuals at supplied quantiles",
        "residual_vector": residual(fit.x).tolist(),
        "mean_variance": list(moments(mus, sigmas, weights))}


AGE_VALUES = np.arange(35, 75)
AGE_X = (AGE_VALUES - M["age"]["mean"]) / M["age"]["sd"]
AGE_BIN = np.digitize(AGE_VALUES, [39, 53, 68])
AGE_BIN_MASS = np.array([0.09, 0.40, 0.40, 0.11])


def age_probs(lam):
    raw = np.exp(lam[0]*AGE_X + lam[1]*AGE_X**2)
    return np.array([raw[j] * AGE_BIN_MASS[b] / np.sum(raw[AGE_BIN == b]) for j, b in enumerate(AGE_BIN)])


age_fit = least_squares(lambda lam: np.array([np.dot(age_probs(lam), AGE_X),
                                             np.dot(age_probs(lam), AGE_X**2)-1]),
                        [0.0, -0.25], xtol=1e-14, ftol=1e-14, gtol=1e-14)
ap = age_probs(age_fit.x)
age_edges = np.r_[-np.inf, ndtri(np.cumsum(ap)[:-1]), np.inf]
female_p = M["female"]["mean"]
female_edge = ndtri(female_p)
bmi_s = math.sqrt(math.log1p((M["bmi"]["sd"]/M["bmi"]["mean"])**2))
bmi_mu = math.log(M["bmi"]["mean"])-0.5*bmi_s**2
glucose, gfit = fit_margin("glucose")
hba1c, hfit = fit_margin("hba1c")
gm, gs, gw = map(np.array, (glucose["log_means"], glucose["log_sds"], glucose["probabilities"]))
hm, hs, hw = map(np.array, (hba1c["log_means"], hba1c["log_sds"], hba1c["probabilities"]))
gmean, gvar = moments(gm, gs, gw)
hmean, hvar = moments(hm, hs, hw)


def pair_weights(q):
    return np.array([[1-gw[1]-hw[1]+q, hw[1]-q], [gw[1]-q, q]])


def gh_cov(q, rho):
    exy = np.exp(gm[:, None]+hm[None, :]+0.5*(gs[:, None]**2+hs[None, :]**2)+rho*gs[:, None]*hs[None, :])
    return float(np.sum(pair_weights(q)*exy)-gmean*hmean)


def make_rank_integral(order):
    nodes, weights = hermegauss(order)
    weights = weights / math.sqrt(2*math.pi)
    quadrature_weights = weights[:, None]*weights[None, :]
    def integral(q, rho):
        zg = nodes[:, None]
        zh = rho*zg+math.sqrt(1-rho*rho)*nodes[None, :]
        answer = 0.0
        pw = pair_weights(q)
        for i in range(2):
            fg = np.sum(gw * ndtr((gm[i]+gs[i]*zg[:, :, None]-gm)/gs), axis=2)
            for j in range(2):
                fh = np.sum(hw * ndtr((hm[j]+hs[j]*zh[:, :, None]-hm)/hs), axis=2)
                answer += pw[i, j]*np.sum(quadrature_weights*fg*fh)
        return float(12*answer-3)
    return integral


rank64 = make_rank_integral(64)
qmax = min(gw[1], hw[1])
qmin = max(0, gw[1]+hw[1]-1)
def gh_residual(x):
    q = qmin+(qmax-qmin)*x[0]
    return [gh_cov(q, x[1])/math.sqrt(gvar*hvar)-REF["diagnostics"]["joint"]["pearson"],
            rank64(q, x[1])-REF["diagnostics"]["joint"]["spearman"]]
gh_fit = least_squares(gh_residual, [0.7, 0.25], bounds=([0.001, -0.7], [0.999, 0.95]),
                       xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=500)
qjoint = qmin+(qmax-qmin)*gh_fit.x[0]
rho_gh = gh_fit.x[1]


def age_lognormal_cov(mu, sigma, rho):
    mean = np.exp(mu+sigma*sigma/2)
    shifted_prob = np.diff(ndtr(age_edges-rho*sigma))
    return float(mean*(np.dot(AGE_VALUES, shifted_prob)-M["age"]["mean"]))


def female_lognormal_cov(mu, sigma, rho):
    return float(np.exp(mu+sigma*sigma/2)*(ndtr(female_edge-rho*sigma)-female_p))


def bmi_lognormal_cov(mu, sigma, rho):
    return float(np.exp(bmi_mu+bmi_s*bmi_s/2+mu+sigma*sigma/2)*np.expm1(rho*bmi_s*sigma))


def mixture_cov(fun, mus, sigmas, weights, rho):
    return float(sum(w*fun(m, s, rho) for m, s, w in zip(mus, sigmas, weights)))


# Underdetermined relationships are declared assumptions, not absent evidence.
ASSUMED_RHOS = {"age_female": 0.0, "age_bmi": -0.08, "female_bmi": 0.04,
                "female_glucose": 0.04, "female_hba1c": 0.03, "bmi_glucose": 0.20}


def covariance_and_correlations(x):
    rag, rah, rbh = x
    r = np.eye(5)
    for a, b, value in [(0,1,0.0),(0,2,-0.08),(0,3,rag),(0,4,rah),
                        (1,2,0.04),(1,3,0.04),(1,4,0.03),(2,3,0.20),(2,4,rbh),(3,4,rho_gh)]:
        r[a,b] = r[b,a] = value
    cv = np.diag([M["age"]["sd"]**2, female_p*(1-female_p), M["bmi"]["sd"]**2, gvar, hvar])
    entries = [(0,1,0.0), (0,2,age_lognormal_cov(bmi_mu,bmi_s,r[0,2])),
               (1,2,female_lognormal_cov(bmi_mu,bmi_s,r[1,2])),
               (3,4,gh_cov(qjoint,rho_gh))]
    for idx, mus, sigmas, weights in [(3,gm,gs,gw),(4,hm,hs,hw)]:
        entries += [(0,idx,mixture_cov(age_lognormal_cov,mus,sigmas,weights,r[0,idx])),
                    (1,idx,mixture_cov(female_lognormal_cov,mus,sigmas,weights,r[1,idx])),
                    (2,idx,mixture_cov(bmi_lognormal_cov,mus,sigmas,weights,r[2,idx]))]
    for a,b,value in entries:
        cv[a,b]=cv[b,a]=value
    return cv,r


def projections(cv):
    outputs=[]
    for inds,term in [([0,1,2],2),([0,1,3],3),([1,2,3,0],0)]:
        beta=np.linalg.solve(cv[np.ix_(inds,inds)], cv[inds,4])
        outputs.append(float(beta[inds.index(term)]))
    return np.array(outputs)


target_e=np.array([REF["estimands"][k]["coefficient"] for k in ["E1","E2","E3"]])
dependence_fit=least_squares(lambda x:(projections(covariance_and_correlations(x)[0])-target_e)/[0.05,0.4,0.008],
                            [0.28,0.30,0.36], bounds=([-0.75,-0.75,-0.75],[0.75,0.75,0.75]),
                            ftol=1e-13,xtol=1e-13,gtol=1e-13,max_nfev=500)
covariance, correlation=covariance_and_correlations(dependence_fit.x)
eigenvalues=np.linalg.eigvalsh(correlation)
assert eigenvalues.min()>0, "Latent correlation matrix must be positive definite"
chol=np.linalg.cholesky(correlation)
rank96=make_rank_integral(96)(qjoint,rho_gh)

parameters={
    "n_rows":3000,
    "age_distribution":{"values":AGE_VALUES.tolist(),"probabilities":ap.tolist(),"latent_normal_edges":age_edges[1:-1].tolist()},
    "female_probability":float(female_p),
    "female_latent_threshold":float(female_edge),
    "bmi_lognormal":{"log_mean":float(bmi_mu),"log_sd":float(bmi_s)},
    "glucose_mixture":glucose,
    "hba1c_mixture":hba1c,
    "mixture_indicator_probabilities":pair_weights(qjoint).ravel().tolist(),
    "latent_order":["age","female","bmi","glucose","hba1c"],
    "latent_correlation":correlation.tolist(),
    "latent_cholesky":chol.tolist(),
    "assumed_latent_correlations":ASSUMED_RHOS
}
assumptions=[
    {"id":"A_SAMPLE_PLUGIN","description":"Use supplied selected CHNS sample summaries as plug-in development constraints. They are estimates with sampling/selection uncertainty, not population truth. No confidence interval is used as an acceptance band, weighting precision, or p-value target. Generated draws do not encode their full uncertainty."},
    {"id":"A_AGE","description":"Discrete maximum-entropy shape within age bins 35-38,39-52,53-67,68-74 with masses 0.09,0.40,0.40,0.11; fit shared linear/quadratic exponential tilt to supplied age mean/SD. The bin masses are assumptions compatible with supplied integer quantiles, not recovered empirical counts."},
    {"id":"A_MARGINS","description":"BMI has one lognormal law fitted to mean/SD. Glucose and HbA1c each have a two-lognormal marginal fitted by deterministic moments/CDF equations to five supplied summaries. Positive support and finite moments follow for these finite lognormal mixtures. Distribution family and unsupplied tail behavior remain assumptions."},
    {"id":"A_DEPENDENCE","description":"A Gaussian latent vector couples age, female, BMI and within-component biomarker variation. Two correlated mixture indicators produce additional glucose/HbA1c upper-tail association; indicators are independent of the Gaussian vector. Components are statistical heterogeneity, not diagnosed diabetes or a causal mechanism. Rank and Pearson correlations are distinct fitted constraints."},
    {"id":"A_NUISANCE","description":"Unknown latent correlations are age/female 0, age/BMI -0.08, female/BMI 0.04, female/glucose 0.04, female/HbA1c 0.03, BMI/glucose 0.20. These are explicit regularizing scenario choices, not inferred independence or evidence-derived signs. Female=1 means latent Z_female is below its threshold; positive latent correlations therefore imply lower continuous-variable values among females."},
    {"id":"A_OLS","description":"Fit remaining three latent correlations jointly to the three supplied differently adjusted OLS projections using analytic covariances. This does not concatenate externally reported separate regressions into a structural equation, and the projections are not causal effects."},
    {"id":"A_IID","description":"Generate 3000 IID selected-population rows and unique artificial identifiers. No observed participant values, community clusters, survey weights, family structure, treatments, missingness process, or diagnostic disease category are reconstructed. Evidence uncertainty is distinct from draw variation."},
    {"id":"A_MEASUREMENT","description":"Generate continuous serum glucose and HbA1c values in task units without rounding or a serum/plasma conversion. Reference assay context is retained; no equivalence to external plasma measurements or external HbA1c assays is claimed."}
]
def prov(eids,aids,derivation):return {"evidence_ids":eids,"assumption_ids":aids,"derivation":derivation}
all_ref_eids=[e["id"] for e in EVIDENCE["items"] if e["source_id"]=="CHNS_DEV_REF"]
provenance={
 "n_rows":prov([], ["A_IID"],"Task-prescribed 3000 synthetic rows."),
 "age_distribution":prov(["REF_age_mean","REF_age_sd","REF_age_q10","REF_age_median","REF_age_q90"],["A_AGE","A_SAMPLE_PLUGIN"],"Deterministic maximum entropy exponential tilt, with retained producer derive_spec.py; finite 35-74 support."),
 "female_probability":prov(["REF_female_mean"],["A_SAMPLE_PLUGIN"],"Bernoulli probability equals supplied female sample mean; its SD and binary quantiles are dependent consequences."),
 "female_latent_threshold":prov(["REF_female_mean"],["A_DEPENDENCE"],"Inverse standard-normal CDF of female_probability; threshold orientation explicitly declared."),
 "bmi_lognormal":prov(["REF_bmi_mean","REF_bmi_sd"],["A_MARGINS","A_SAMPLE_PLUGIN"],"s=sqrt(log(1+(sd/mean)^2)); mu=log(mean)-s^2/2. Quantiles retained as approximate diagnostic constraints, not exact fitting targets."),
 "glucose_mixture":prov(["REF_glucose_mean","REF_glucose_sd","REF_glucose_q10","REF_glucose_median","REF_glucose_q90"],["A_MARGINS","A_SAMPLE_PLUGIN","A_MEASUREMENT"],"Two-component positive lognormal mixture; analytic mean/variance and CDF equalities solved deterministically, no rows."),
 "hba1c_mixture":prov(["REF_hba1c_mean","REF_hba1c_sd","REF_hba1c_q10","REF_hba1c_median","REF_hba1c_q90"],["A_MARGINS","A_SAMPLE_PLUGIN","A_MEASUREMENT"],"Two-component positive lognormal mixture; analytic mean/variance and CDF equalities solved deterministically, no rows."),
 "mixture_indicator_probabilities":prov(["REF_glucose_hba1c_pearson","REF_glucose_hba1c_spearman"],["A_DEPENDENCE","A_SAMPLE_PLUGIN"],"Four joint indicator cell probabilities in (G0,H0),(G0,H1),(G1,H0),(G1,H1) order. Joint high-component probability and within-component normal correlation fit Pearson analytically and Spearman by 64x64 Gaussian quadrature, checked at 96x96."),
 "latent_order":prov([], ["A_DEPENDENCE"],"Bookkeeping order defining the Gaussian latent correlation and Cholesky arrays."),
 "latent_correlation":prov(["REF_E1","REF_E2","REF_E3","REF_glucose_hba1c_pearson","REF_glucose_hba1c_spearman"],["A_DEPENDENCE","A_NUISANCE","A_OLS","A_SAMPLE_PLUGIN"],"Gaussian correlation matrix: six explicit nuisance choices; GH fitted with indicator covariance; age/G, age/H and BMI/H fit jointly to analytic OLS projections. See retained derivation and fit_report.json; no row-level optimization."),
 "latent_cholesky":prov(["REF_E1","REF_E2","REF_E3","REF_glucose_hba1c_pearson","REF_glucose_hba1c_spearman"],["A_DEPENDENCE","A_NUISANCE","A_OLS"],"Numerical lower Cholesky factor of positive-definite latent_correlation, for generator execution only."),
 "assumed_latent_correlations":prov([], ["A_NUISANCE"],"Explicit underidentified scenario settings, preserved for review. These are not reported estimates.")
}
spec={"parameters":parameters,"assumptions":assumptions,"parameter_provenance":provenance}
report={
 "method":"Deterministic analytic moments, CDF equations, covariance projection algebra, and Gaussian quadrature; zero RNG calls and zero synthetic rows.",
 "source":"input/reference_summary.json; supplied CHNS development sample n=6631, not independent validation",
 "limits":"Finite normal quadrature is a numerical approximation. Optimizer convergence and algebraic fit do not identify a unique population law or validate transport. No source-population simulation or generator execution was performed.",
 "age":{"probability_sum":float(sum(ap)),"mean":float(ap@AGE_VALUES),"sd":float(math.sqrt(ap@((AGE_VALUES-M['age']['mean'])**2))),"bin_masses_assumed":AGE_BIN_MASS.tolist(),"tilt_coefficients":age_fit.x.tolist()},
 "bmi":{"mean":M["bmi"]["mean"],"sd":M["bmi"]["sd"],"q10":float(math.exp(bmi_mu+bmi_s*ndtri(.1))),"median":float(math.exp(bmi_mu)),"q90":float(math.exp(bmi_mu+bmi_s*ndtri(.9)))},
 "glucose":gfit,"hba1c":hfit,
 "joint":{"optimizer_success":bool(gh_fit.success),"residual_vector":gh_residual(gh_fit.x),"pearson":float(gh_cov(qjoint,rho_gh)/math.sqrt(gvar*hvar)),"spearman_quadrature64":rank64(qjoint,rho_gh),"spearman_quadrature96":rank96,"quadrature_order_difference":float(rank96-rank64(qjoint,rho_gh)),"q11":float(qjoint),"within_component_latent_rho":float(rho_gh)},
 "analytic_projections":dict(zip(["E1","E2","E3"],projections(covariance).tolist())),
 "covariance_order":["age","female","bmi","glucose","hba1c"],"covariance":covariance.tolist(),
 "latent_correlation_eigenvalues":eigenvalues.tolist(),
 "retrieval":{"queries":[],"new_documents":[],"count_queries":0,"count_new_documents":0,"overlap":"CHNS development summaries are one sample; all Jansen rows one Lifelines cohort; source audit reconciles the same reported external results rather than adding studies."}
}
write_json("model_spec.json",spec)
write_json("evidence.json",EVIDENCE)
write_json("fit_report.json",report)
print(json.dumps({"candidate":HERE.name,"marginal_fit_max_residual":{"glucose":gfit["max_absolute_scaled_residual"],"hba1c":hfit["max_absolute_scaled_residual"]},"joint":report["joint"],"analytic_projections":report["analytic_projections"],"min_latent_eigenvalue":float(eigenvalues.min()),"rows_generated":0},indent=2))

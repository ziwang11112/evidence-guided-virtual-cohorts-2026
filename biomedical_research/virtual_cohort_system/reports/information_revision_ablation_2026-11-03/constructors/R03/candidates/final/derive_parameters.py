"""Deterministic population-moment derivation. No RNG, cohorts, or generator imports.

Input is the explicitly admitted CHNS development summary. Integrals are normal
distribution identities and adaptive scalar quadrature; no Monte Carlo points.
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import least_squares, root
from scipy.special import ndtr, ndtri

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent.parent
REF = json.loads((BUNDLE / "input/reference_summary.json").read_text(encoding="utf-8-sig"))
M = REF["diagnostics"]["marginal"]


def mixture_stats(theta):
    p, mu0, s0, mu1, s1 = theta
    w = np.array([1-p, p])
    mu = np.array([mu0, mu1])
    sigma = np.array([s0, s1])
    mean = np.sum(w*np.exp(mu+sigma*sigma/2))
    var = np.sum(w*np.exp(2*mu+2*sigma*sigma))-mean*mean
    return float(mean), float(np.sqrt(var))


def mixcdf(x, theta):
    p, m0, s0, m1, s1 = theta
    return (1-p)*ndtr((np.log(x)-m0)/s0)+p*ndtr((np.log(x)-m1)/s1)


def fit_margin(name, initial):
    target = M[name]
    def residual(theta):
        mean, sd = mixture_stats(theta)
        return np.array([(mean-target['mean'])/target['sd'],
                         (sd-target['sd'])/target['sd'],
                         mixcdf(target['q10'], theta)-.1,
                         mixcdf(target['median'], theta)-.5,
                         mixcdf(target['q90'], theta)-.9])
    opt = least_squares(residual, initial,
                        bounds=([.008, math.log(2), .015, math.log(6), .015],
                                [.25, math.log(7), .4, math.log(18), .65]),
                        xtol=1e-13, ftol=1e-13, gtol=1e-13, max_nfev=3000)
    assert opt.success
    return opt.x, {'residual': residual(opt.x).tolist(), 'nfev': int(opt.nfev),
                   'optimization_success': bool(opt.success)}


g, fit_g = fit_margin('glucose', [.08, math.log(5.1), .12, math.log(9), .3])
h, fit_h = fit_margin('hba1c', [.06, math.log(5.45), .07, math.log(8.5), .24])

# Maximum entropy within four age bands, keeping probabilities fixed at
# F(38)=.09,F(52)=.49,F(67)=.89. These leave each admitted quantile inside
# a mass interval; endpoints are modeling assumptions, not observed counts.
ages = np.arange(35,75,dtype=float)
age_bands = [(35,38,.09),(39,52,.4),(53,67,.4),(68,74,.11)]
def age_prob(theta):
    x = (ages-M['age']['mean'])/M['age']['sd']
    exponent = theta[0]*x+theta[1]*x*x
    prob = np.zeros(40)
    for lo, hi, mass in age_bands:
        ix = (ages>=lo)&(ages<=hi)
        weights = np.exp(exponent[ix]-np.max(exponent[ix]))
        prob[ix] = mass*weights/weights.sum()
    return prob
def age_equations(theta):
    probs=age_prob(theta)
    return [(probs@ages-M['age']['mean'])/M['age']['sd'],
            (probs@((ages-M['age']['mean'])**2)-M['age']['sd']**2)/M['age']['sd']**2]
age_opt = root(age_equations,[0,0])
assert age_opt.success
ap = age_prob(age_opt.x)
cuts = np.r_[-np.inf, ndtri(np.cumsum(ap)[:-1]), np.inf]
amean, avar = float(ap@ages), float(ap@((ages-ap@ages)**2))

bmi_sigma = float(np.sqrt(np.log1p((M['bmi']['sd']/M['bmi']['mean'])**2)))
bmi_mu = float(np.log(M['bmi']['mean'])-bmi_sigma*bmi_sigma/2)

def bvn(a,b,rho):
    # Plackett's identity. Deterministic scalar integral, including rho=0.
    return float(ndtr(a)*ndtr(b)+quad(
        lambda r: np.exp(-(a*a-2*r*a*b+b*b)/(2*(1-r*r)))/(2*np.pi*np.sqrt(1-r*r)),
        0,rho,epsabs=2e-11,epsrel=2e-11)[0])

def component(theta):
    return np.array([1-theta[0],theta[0]]), np.array([theta[1],theta[3]]), np.array([theta[2],theta[4]])
gw,gm,gs = component(g)
hw,hm,hs = component(h)
gmeans=np.exp(gm+gs*gs/2)
hmeans=np.exp(hm+hs*hs/2)
gmean,gsd=mixture_stats(g)
hmean,hsd=mixture_stats(h)

def label_joint(q):
    return np.array([[1-g[0]-h[0]+q,h[0]-q],[g[0]-q,q]])

def gh_moments(q,rho0,rho1):
    weights=label_joint(q)
    cross=0.
    rankcross=0.
    for i in range(2):
        for j in range(2):
            rho = rho0 if i==0 and j==0 else rho1
            cross += weights[i,j]*gmeans[i]*hmeans[j]*np.exp(rho*gs[i]*hs[j])
            for k in range(2):
                for l in range(2):
                    a=(gm[i]-gm[k])/np.sqrt(gs[i]**2+gs[k]**2)
                    b=(hm[j]-hm[l])/np.sqrt(hs[j]**2+hs[l]**2)
                    r=rho*gs[i]*hs[j]/np.sqrt((gs[i]**2+gs[k]**2)*(hs[j]**2+hs[l]**2))
                    rankcross+=weights[i,j]*gw[k]*hw[l]*bvn(a,b,r)
    return (cross-gmean*hmean)/(gsd*hsd), 12*rankcross-3

ref_r=REF['diagnostics']['joint']
def gh_residual(v):
    pr,sr=gh_moments(q,v[0],v[1])
    return [pr-ref_r['pearson'],sr-ref_r['spearman']]
q=float(min(g[0],h[0]))
gh_opt=least_squares(gh_residual,[.2,.9],
    bounds=([-.5,-.5],[.95,.98]),
    xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=1000)
rgh0,rgh1=map(float,gh_opt.x)
pearson,spearman=gh_moments(q,rgh0,rgh1)
covgh=pearson*gsd*hsd

def cov_age_lognormal(mu,sigma,rho):
    shifted=ndtr(cuts[1:]-rho*sigma)-ndtr(cuts[:-1]-rho*sigma)
    return float(np.exp(mu+sigma*sigma/2)*(ages@shifted-amean))

def cov_age_mix(theta,rho):
    ww,mm,ss=component(theta)
    return sum(ww[i]*cov_age_lognormal(mm[i],ss[i],rho) for i in range(2))

def cov_bmi_mix(theta,rho):
    ww,mm,ss=component(theta)
    return float(sum(ww[i]*M['bmi']['mean']*np.exp(mm[i]+ss[i]**2/2)*np.expm1(bmi_sigma*ss[i]*rho) for i in range(2)))

# Two unreported latent correlations are declared assumptions. Sex is
# independent by explicit construction; therefore conditioning on sex has
# no effect on the population OLS covariance calculations.
rab=-.05
rbg=.20
covab=cov_age_lognormal(bmi_mu,bmi_sigma,rab)
covbg=cov_bmi_mix(g,rbg)

def population_cov(v):
    rag,rah,rbh=v
    ag=cov_age_mix(g,rag)
    ah=cov_age_mix(h,rah)
    bh=cov_bmi_mix(h,rbh)
    return np.array([[avar,covab,ag,ah],
                     [covab,M['bmi']['sd']**2,covbg,bh],
                     [ag,covbg,gsd**2,covgh],
                     [ah,bh,covgh,hsd**2]])

def estimands(v):
    c=population_cov(v)
    e1=np.linalg.solve(c[np.ix_([0,1],[0,1])],c[[0,1],3])[1]
    e2=np.linalg.solve(c[np.ix_([0,2],[0,2])],c[[0,2],3])[1]
    e3=np.linalg.solve(c[:3,:3],c[:3,3])[0]
    return np.array([e1,e2,e3])

target_e=np.array([REF['estimands'][x]['coefficient'] for x in ['E1','E2','E3']])
e_opt=least_squares(lambda v:(estimands(v)-target_e)/[.05,.4,.01],[.2,.3,.4],
        bounds=([-.7,-.7,-.7],[.7,.7,.9]),xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=1000)
rag,rah,rbh=map(float,e_opt.x)
corr=np.array([[1,rab,rag,rah],[rab,1,rbg,rbh],[rag,rbg,1,rgh0],[rah,rbh,rgh0,1]])
corr_broad=corr.copy()
corr_broad[2,3]=corr_broad[3,2]=rgh1
eig=np.linalg.eigvalsh(corr)
eig_broad=np.linalg.eigvalsh(corr_broad)
assert eig.min()>0 and eig_broad.min()>0

derived = {
 'scope':'deterministic_population_moment_derivation_only_no_rows',
 'retrieval':{'queries':[],'urls':[],'new_documents':[]},
 'age':{'values':ages.astype(int).tolist(),'probabilities':ap.tolist(),'entropy_tilt':age_opt.x.tolist(),
        'assumed_band_probabilities':age_bands,'mean':amean,'sd':math.sqrt(avar)},
 'female_probability':M['female']['mean'],
 'bmi':{'log_mean':bmi_mu,'log_sd':bmi_sigma},
 'glucose':{'mixture_parameters':g.tolist(),'fit':fit_g},
 'hba1c':{'mixture_parameters':h.tolist(),'fit':fit_h},
 'joint':{'glycemic_label_probabilities':label_joint(q).ravel().tolist(),
          'gaussian_order':['age','bmi','glucose','hba1c'],
          'gaussian_correlation':corr.tolist(),'gaussian_correlation_broad':corr_broad.tolist(),
          'eigenvalues':eig.tolist(),'eigenvalues_broad':eig_broad.tolist(),
          'pearson':pearson,'spearman_continuous':spearman,
          'estimands':dict(zip(['E1','E2','E3'],estimands(e_opt.x).tolist())),
          'population_covariance':population_cov(e_opt.x).tolist()},
 'limits':['No cohort was created or generator imported/executed.',
           'Optimization fits disclosed sample summaries, not population truth.',
           'Mixture labels are latent distributional components, not diabetes diagnosis.',
           'Female independence, residual age-BMI and BMI-glucose correlations remain assumptions.',
           'Continuous HbA1c approximates a released measurement whose ties affect rank estimates.',
           'External source-context replay was not available.']}
(HERE/'derivation_result.json').write_text(json.dumps(derived,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'mixture_g':g.tolist(),'mixture_h':h.tolist(),'fit_g':fit_g,'fit_h':fit_h,
    'pearson':pearson,'spearman':spearman,'e':derived['joint']['estimands'],
    'corr':corr.tolist(),'corr_broad':corr_broad.tolist(),'eigenvalues':eig.tolist(),
    'eigenvalues_broad':eig_broad.tolist()},indent=2))

"""Deterministic formulas and quadrature only; never creates synthetic people.

Fits declared distribution functionals to the supplied CHNS sample summaries.
Gauss-Hermite integration uses two mathematical axes, not five-variable rows.
No RNG, candidate import, generate call, or cohort output occurs here.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares, root, brentq
from scipy.special import ndtr, ndtri, softmax
from numpy.polynomial.hermite import hermgauss

HERE = Path(__file__).resolve().parent
REF = json.loads((HERE.parents[1] / 'input' / 'reference_summary.json').read_text(encoding='utf-8'))
M = REF['diagnostics']['marginal']

# Maximum entropy integer-age marginal, bounded by the task.
ages = np.arange(35, 75, dtype=float)
features = np.array([(ages-53)/10, ((ages-53)/10)**2,
                     (ages <= 38).astype(float), (ages <= 52).astype(float),
                     (ages <= 67).astype(float)])
age_target = np.array([(M['age']['mean']-53)/10,
    (M['age']['sd']**2+(M['age']['mean']-53)**2)/100, .09, .49, .89])
ar = root(lambda t: features @ softmax(t @ features)-age_target, np.zeros(5))
assert ar.success
ap = softmax(ar.x @ features)
age_mean = ages @ ap
age_var = ((ages-age_mean)**2) @ ap
cuts = np.r_[-np.inf, ndtri(np.cumsum(ap)[:-1]), np.inf]

# A common latent class produces upper-tail concordance without requiring
# Pearson and rank correlations to be the same number.
def unpack(t):
    p = t[0]
    return p, [np.array(t[1:5]), np.array(t[5:9])]

def marginal(par, p):
    mu = par[[0,2]]
    sig = par[[1,3]]
    w = np.array([1-p,p])
    means = np.exp(mu+sig*sig/2)
    mean = w @ means
    second = w @ np.exp(2*mu+2*sig*sig)
    return mean, np.sqrt(second-mean*mean), means

def cdf(x, par, p):
    mu = par[[0,2]]
    sig = par[[1,3]]
    return (1-p)*ndtr((np.log(x)-mu[0])/sig[0])+p*ndtr((np.log(x)-mu[1])/sig[1])

def margin_loss(t):
    p, pars = unpack(t)
    residuals = []
    for key, par in zip(['glucose','hba1c'],pars):
        ref=M[key]
        mean, sd, _ = marginal(par,p)
        residuals.extend([(mean-ref['mean'])/0.03,(sd-ref['sd'])/0.03])
        residuals.extend((cdf(np.array([ref['q10'],ref['median'],ref['q90']]),par,p)
                          -np.array([.1,.5,.9]))/.01)
    return residuals

mr=least_squares(margin_loss,[.06,np.log(5.1),.12,np.log(10),.25,
                              np.log(5.45),.07,np.log(8.5),.23],
    bounds=([.015,np.log(4.5),.04,np.log(7),.05,np.log(5),.025,np.log(7),.05],
            [.15,np.log(5.6),.25,np.log(16),.7,np.log(6),.15,np.log(14),.7]),
    max_nfev=1500,xtol=1e-12,ftol=1e-12,gtol=1e-12)
p,pars=unpack(mr.x)
pg,ph=pars
mg,sg,mcg=marginal(pg,p)
mh,sh,mch=marginal(ph,p)
bm=M['bmi']['mean']
bs=M['bmi']['sd']
bsig=np.sqrt(np.log1p((bs/bm)**2))
bmu=np.log(bm)-bsig*bsig/2
w=np.array([1-p,p])

def age_lognormal_cov(mu,sig,rho):
    conditional_probability=np.diff(ndtr(cuts-rho*sig))
    return np.exp(mu+sig*sig/2)*(ages @ conditional_probability-age_mean)

def age_mixture_cov(par,rho):
    return sum(w[k]*age_lognormal_cov(par[2*k],par[2*k+1],rho) for k in range(2))

def bmi_mixture_cov(par,rho):
    means=np.exp(par[[0,2]]+.5*par[[1,3]]**2)
    return bm*np.sum(w*means*np.expm1(bsig*par[[1,3]]*rho))

def joint_cov(rhos):
    within=np.exp(pg[[0,2]]+ph[[0,2]]+.5*(pg[[1,3]]**2+ph[[1,3]]**2)
                  +np.array(rhos)*pg[[1,3]]*ph[[1,3]])
    return w@within-mg*mh

# Fixed nodes are quadrature nodes for expectations, never synthetic draws.
def rank_correlation(rhos,order=48):
    x,weight=hermgauss(order)
    x=x*np.sqrt(2)
    weights=np.outer(weight,weight)/np.pi
    total=0.0
    for k in range(2):
        zg=x[:,None]
        zh=rhos[k]*zg+np.sqrt(1-rhos[k]**2)*x[None,:]
        g=np.exp(pg[2*k]+pg[2*k+1]*zg)
        h=np.exp(ph[2*k]+ph[2*k+1]*zh)
        total+=w[k]*np.sum(weights*cdf(g,pg,p)*cdf(h,ph,p))
    return 12*total-3

# Two unidentified covariate associations fixed as explicit assumptions.
rab=-.05
rbg=.20
cab=age_lognormal_cov(bmu,bsig,rab)
cbg=bmi_mixture_cov(pg,rbg)

def functionals(t,order=48):
    rag,rah,rbh,r0,r1=t
    cag=age_mixture_cov(pg,rag)
    cah=age_mixture_cov(ph,rah)
    cbh=bmi_mixture_cov(ph,rbh)
    cgh=joint_cov([r0,r1])
    var=np.array([[age_var,cab,cag],[cab,bs*bs,cbg],[cag,cbg,sg*sg]])
    cov=np.array([cah,cbh,cgh])
    e1=np.linalg.solve(var[:2,:2],cov[:2])[1]
    e2=np.linalg.solve(var[np.ix_([0,2],[0,2])],cov[[0,2]])[1]
    e3=np.linalg.solve(var,cov)[0]
    pearson=cgh/(sg*sh)
    rank=rank_correlation([r0,r1],order)
    return np.array([e1,e2,e3,pearson,rank])

targets=np.array([REF['estimands'][k]['coefficient'] for k in ['E1','E2','E3']]
    +[REF['diagnostics']['joint']['pearson'],REF['diagnostics']['joint']['spearman']])
scale=np.array([.02,.04,.004,.04,.04])
dr=least_squares(lambda t:(functionals(t)-targets)/scale,
    [.12,.30,.35,.22,.55],bounds=([-.7,-.7,-.7,-.7,-.7],[.7,.7,.7,.95,.95]),
    max_nfev=300,xtol=1e-11,ftol=1e-11,gtol=1e-11)
rag,rah,rbh,r0,r1=dr.x
correlations=[]
for r in [r0,r1]:
    correlations.append(np.array([[1,rab,rag,rah],[rab,1,rbg,rbh],
                                  [rag,rbg,1,r],[rah,rbh,r,1]]))
eigenvalues=[np.linalg.eigvalsh(c).tolist() for c in correlations]
assert min(min(e) for e in eigenvalues)>0

parameters={'n_rows':3000,'age_values':ages.astype(int).tolist(),
 'age_probabilities':ap.tolist(),'female_probability':M['female']['mean'],
 'bmi_log_mean':float(bmu),'bmi_log_sd':float(bsig),'high_component_probability':float(p),
 'glucose_log_parameters':pg.tolist(),'hba1c_log_parameters':ph.tolist(),
 'latent_correlations':[c.tolist() for c in correlations]}
report={'scope':'deterministic distribution mathematics only; no synthetic rows or generator execution',
 'method':'maximum entropy age; lognormal BMI; common-class two-lognormal glycemia mixture; analytic covariances and two-dimensional Gauss-Hermite rank integral',
 'assumptions':{'age_CDF_at_38_52_67':[.09,.49,.89],
                'latent_age_bmi_correlation':rab,'latent_bmi_glucose_correlation':rbg,
                'female_independent':True,'mixture_class_independent_of_covariates':True},
 'age_solver_success':bool(ar.success),'marginal_solver_success':bool(mr.success),
 'dependence_solver_success':bool(dr.success),'mixture_scaled_residuals':margin_loss(mr.x),
 'predicted_marginals':{},'functionals_order48':functionals(dr.x).tolist(),
 'functionals_order80':functionals(dr.x,80).tolist(),'reference_functionals':targets.tolist(),
 'correlation_eigenvalues':eigenvalues,
 'limits':'Not a source replay, finite cohort result, independent validation, uncertainty estimate, or identified population law. Calibration to explicit reference summaries is descriptive.'}
for key,par in zip(['glucose','hba1c'],pars):
    mm,ss,comp=marginal(par,p)
    report['predicted_marginals'][key]={'mean':float(mm),'sd':float(ss),
      'q10':brentq(lambda x:cdf(x,par,p)-.1,.1,50),
      'median':brentq(lambda x:cdf(x,par,p)-.5,.1,50),
      'q90':brentq(lambda x:cdf(x,par,p)-.9,.1,50),
      'component_means':comp.tolist()}
report['predicted_marginals']['age']={'mean':float(age_mean),'sd':float(np.sqrt(age_var))}
report['predicted_marginals']['bmi']={'mean':bm,'sd':bs,
   'q10':float(np.exp(bmu+bsig*ndtri(.1))), 'median':float(np.exp(bmu)),
   'q90':float(np.exp(bmu+bsig*ndtri(.9)))}
(HERE/'derived_parameters.json').write_text(json.dumps(parameters,indent=2,allow_nan=False)+'\n',encoding='utf-8')
(HERE/'analytic_report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,allow_nan=False))

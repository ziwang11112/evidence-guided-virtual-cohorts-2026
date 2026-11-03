"""Deterministic population-rank quadrature, no random draws or cohort rows.

Evaluates distribution integrals on fixed Gauss-Hermite nodes, discrete ages,
and the exact rounded biomarker support. Does not call or import generator.py.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.special import ndtr, ndtri
from scipy.optimize import brentq
from numpy.polynomial.hermite import hermgauss

parser=argparse.ArgumentParser()
parser.add_argument('--nodes',type=int,default=48)
parser.add_argument('--core',type=float)
args=parser.parse_args()
base=Path(__file__).parent
spec=json.loads((base/'quadrature_input_spec.json').read_text(encoding='utf-8'))['parameters']
calc=json.loads((base/'analytic_fit.json').read_text(encoding='utf-8'))
ref=json.loads((base.parent.parent/'input/reference_summary.json').read_text(encoding='utf-8'))
p=spec['mixture_probability']; prob=np.array([1-p,p])
ages=np.asarray(spec['age']['values'])-spec['age']['mean']; ageweights=np.asarray(spec['age']['probabilities'])
xb,wb=hermgauss(40);xb=xb*np.sqrt(2);wb=wb/np.sqrt(np.pi)
bmi=np.clip(np.exp(spec['bmi']['log_mu']+spec['bmi']['log_sigma']*xb),*spec['bmi']['support'])
bg=spec['glucose_age_slope'];ha=spec['hba1c_age_slope'];hb=spec['hba1c_bmi_slope']
gshifts=bg*ages;hshifts=(ha*ages[:,None]+hb*(bmi-spec['bmi']['mean'])[None,:]).ravel()
hw=(ageweights[:,None]*wb[None,:]).ravel()

def cdf(values,component,kind):
    config=spec[kind];mu=config['log_mu'][component];sd=config['log_sigma'][component];lo,hi=config['baseline_support']
    a=ndtr((np.log(lo)-mu)/sd);b=ndtr((np.log(hi)-mu)/sd)
    z=(np.log(np.clip(values,lo,hi))-mu)/sd
    return np.clip((ndtr(z)-a)/(b-a),0,1)

def marginal_cdf(values,kind):
    shifts,weights=(gshifts,ageweights) if kind=='glucose' else (hshifts,hw)
    return sum(prob[k]*(cdf(values[:,None]-shifts[None,:],k,kind)@weights) for k in range(2))

rankmaps={}
for kind,low,high,step in [('glucose',2.0,25.5,.01),('hba1c',2.0,18.5,.1)]:
    support=np.arange(round(low/step),round(high/step)+1)*step
    upper=marginal_cdf(support+step/2,kind);lower=marginal_cdf(support-step/2,kind)
    mass=upper-lower;mid=(upper+lower)/2
    rankmaps[kind]=(support,mid,float((1-np.sum(mass**3))/12))

def quantile(z,k,kind):
    cfg=spec[kind];mu=cfg['log_mu'][k];sd=cfg['log_sigma'][k];lo,hi=cfg['baseline_support']
    a=ndtr((np.log(lo)-mu)/sd);b=ndtr((np.log(hi)-mu)/sd)
    return np.clip(np.exp(mu+sd*ndtri(np.clip(a+(b-a)*ndtr(z),1e-15,1-1e-15))),lo,hi)

x,w=hermgauss(args.nodes);x=x*np.sqrt(2);w=w/np.sqrt(np.pi);weights=w[:,None]*w[None,:]
def cross(k,rho):
    g=quantile(x[:,None],k,'glucose')
    h=quantile(rho*x[:,None]+np.sqrt(1-rho*rho)*x[None,:],k,'hba1c')
    return float(np.sum(weights*g*h))

wantcov=calc['expected_baseline_covariance'];gmean=calc['expected_glucose_mean_sd_cdfs'][0];hmean=calc['expected_hba1c_mean_sd_cdfs'][0]
def broad_rho(core):
    return brentq(lambda r:prob[0]*cross(0,core)+prob[1]*cross(1,r)-gmean*hmean-wantcov,.001,.999)

def spearman(core):
    rhos=[core,broad_rho(core)];total=0.0
    for k,rho in enumerate(rhos):
        g=quantile(x,k,'glucose')
        h=quantile(rho*x[:,None]+np.sqrt(1-rho*rho)*x[None,:],k,'hba1c')
        subtotal=0.0
        for age,aw in zip(ages,ageweights):
            g_round=np.round(g+bg*age,spec['measurement_decimals']['glucose'])
            gm=np.interp(g_round,*rankmaps['glucose'][:2])
            h_round=np.round(h[:,:,None]+ha*age+hb*(bmi-spec['bmi']['mean'])[None,None,:],spec['measurement_decimals']['hba1c'])
            hm=np.interp(h_round,*rankmaps['hba1c'][:2])
            subtotal+=aw*np.sum(weights*gm[:,None]*(hm@wb))
        total+=prob[k]*subtotal
    return float((total-.25)/np.sqrt(rankmaps['glucose'][2]*rankmaps['hba1c'][2]))

target=ref['diagnostics']['joint']['spearman']
original=spearman(spec['copula_correlations'][0])
core=args.core if args.core is not None else brentq(lambda r:spearman(r)-target,-.1,.4,xtol=.0002)
result={'method':'deterministic Gaussian quadrature on distribution nodes, no sampling or synthetic rows',
        'normal_nodes_per_axis':args.nodes,'bmi_nodes':40,'age_points':40,
        'current_core_rho':spec['copula_correlations'][0],'current_expected_spearman':original,
        'target_spearman':target,'proposed_core_rho':float(core),
        'proposed_broad_rho':float(broad_rho(core)),'proposed_expected_spearman':spearman(core),
        'rounding':'discrete mid-distribution ranks and their exact marginal rank variances'}
print(json.dumps(result,indent=2))

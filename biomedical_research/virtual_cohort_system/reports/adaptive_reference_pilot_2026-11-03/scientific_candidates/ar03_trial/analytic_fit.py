"""Deterministic distribution calculations only; no sampling or cohort rows."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import root, least_squares
from scipy.special import ndtr, ndtri
from numpy.polynomial.hermite import hermgauss

BASE=Path(__file__).parent
ref=json.loads((BASE.parent.parent/'input/reference_summary.json').read_text())
m=ref['diagnostics']['marginal']
age=np.arange(35,75,dtype=float)
features=np.column_stack([(age-53)/10,((age-53)/10)**2,(age<=38),(age<=52),(age<=67)])
age_mu=m['age']['mean']; age_var=m['age']['sd']**2
target=np.array([(age_mu-53)/10,(age_var+(age_mu-53)**2)/100,.09,.49,.89])
def probs(theta):
    z=features@theta; z-=z.max(); p=np.exp(z);return p/p.sum()
sol=root(lambda t: probs(t)@features-target,np.zeros(5))
ap=probs(sol.x)
bmi_mu=m['bmi']['mean']; bmi_sd=m['bmi']['sd']
bmi_sig=np.sqrt(np.log1p((bmi_sd/bmi_mu)**2));bmi_logmu=np.log(bmi_mu)-bmi_sig**2/2
q,w=hermgauss(24); q=q*np.sqrt(2);w=w/np.sqrt(np.pi)
bmi=np.exp(bmi_logmu+bmi_sig*q)
vb=bmi_sd**2;vg=m['glucose']['sd']**2;vh=m['hba1c']['sd']**2
bg=ref['estimands']['E2']['coefficient'];bb=ref['estimands']['E1']['coefficient'];ba=ref['estimands']['E3']['coefficient']
cov=ref['diagnostics']['joint']['pearson']*np.sqrt(vg*vh)
ga=(cov-bg*vg)/(ba*age_var)
ha=ba+bg*ga
shifts_g=ga*(age-age_mu);weights_g=ap
shifts_h=(ha*(age-age_mu)[:,None]+bb*(bmi-bmi_mu)[None,:]).ravel();weights_h=(ap[:,None]*w[None,:]).ravel()

def moments(mu,sig,lo,hi):
    a=(np.log(lo)-mu)/sig;b=(np.log(hi)-mu)/sig;den=ndtr(b)-ndtr(a)
    vals=[np.exp(k*mu+k*k*sig*sig/2)*(ndtr(b-k*sig)-ndtr(a-k*sig))/den for k in (1,2)]
    return vals
def cdf(x,mu,sig,lo,hi):
    a=(np.log(lo)-mu)/sig;b=(np.log(hi)-mu)/sig
    z=(np.log(np.clip(x,lo,hi))-mu)/sig
    return np.clip((ndtr(z)-ndtr(a))/(ndtr(b)-ndtr(a)),0,1)
def calc(params,p,var,shifts,weights,bounds):
    mu0,s0,mu1,s1=params;lo,hi=bounds
    z0=moments(mu0,s0,lo,hi);z1=moments(mu1,s1,lo,hi)
    mean=(1-p)*z0[0]+p*z1[0]; variance=(1-p)*z0[1]+p*z1[1]-mean*mean+weights@(shifts**2)
    qs=[m[var][x] for x in ['q10','median','q90']]
    fs=[weights@((1-p)*cdf(x-shifts,mu0,s0,lo,hi)+p*cdf(x-shifts,mu1,s1,lo,hi)) for x in qs]
    return np.r_[mean,np.sqrt(variance),fs]
def objective(x):
    p=x[0]
    out=[]
    for par,v,s,wgt,bnd in [(x[1:5],'glucose',shifts_g,weights_g,[2.5,25]),(x[5:9],'hba1c',shifts_h,weights_h,[3.5,16])]:
        vals=calc(par,p,v,s,wgt,bnd)
        out.extend((vals-np.r_[m[v]['mean'],m[v]['sd'],.1,.5,.9])/np.array([.02,.04,.015,.015,.015]))
    return out
x0=[.07,np.log(5.13),.12,np.log(10),.25,np.log(5.48),.065,np.log(8.5),.2]
fit=least_squares(objective,x0,bounds=([.02,np.log(4),.03,np.log(6.5),.06,np.log(4.8),.025,np.log(6.5),.06],[.16,np.log(6),.25,np.log(16),.7,np.log(6.0),.15,np.log(13),.6]),max_nfev=700)
x=fit.x
result={'method':'deterministic analytic moments/CDF integration; no random sampling, no synthetic rows','success':bool(fit.success),'loss':float(np.sum(fit.fun**2)),'age_values':age.astype(int).tolist(),'age_probabilities':ap.tolist(),'age_moments':[float(ap@age),float(np.sqrt(ap@(age-age_mu)**2))],'bmi_logmu':bmi_logmu,'bmi_logsigma':bmi_sig,'p_high':x[0],'glucose_components':x[1:5].tolist(),'hba1c_components':x[5:9].tolist(),'glucose_age_slope':ga,'hba1c_age_slope':ha,'hba1c_bmi_slope':bb,'expected_glucose_mean_sd_cdfs':calc(x[1:5],x[0],'glucose',shifts_g,weights_g,[2.5,25]).tolist(),'expected_hba1c_mean_sd_cdfs':calc(x[5:9],x[0],'hba1c',shifts_h,weights_h,[3.5,16]).tolist()}
(BASE/'analytic_fit.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['age_values','age_probabilities']},indent=2))

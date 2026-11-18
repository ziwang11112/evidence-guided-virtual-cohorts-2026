"""Post-construction arithmetic audit; no Agent program or sampled cohort execution."""
from pathlib import Path
import json, math
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import norm

W=Path(__file__).resolve().parent
e=json.loads((W/'SOURCE_EXTRACTION.json').read_text(encoding='utf8'))
c=e['collapsed_counts']; n=sum(c.values())
p_h=(c['both_low']+c['only_hb_low'])/n
p_f=(c['both_low']+c['only_ferritin_low'])/n
joint=c['both_low']/n
h,f=norm.ppf(p_h),norm.ppf(p_f)

def joint_at(rho):
    return quad(lambda z:norm.pdf(z)*norm.cdf((f-rho*z)/math.sqrt(1-rho*rho)),
                -math.inf,h,epsabs=1e-12,epsrel=1e-12)[0]

rho=brentq(lambda r:joint_at(r)-joint,0,.99,xtol=1e-14)
q=joint_at(.35)
q4=joint_at(.4)
out={'scope':'Source-only arithmetic audit of declared Gaussian-copula implications; no target calibration, new generator run, or synthetic table.',
 'source_probabilities':{'low_hb':p_h,'low_ferritin':p_f,'both_low':joint},
 'source_crude_odds_ratio':c['both_low']*c['neither_low']/(c['only_hb_low']*c['only_ferritin_low']),
 'gaussian_family_assumption':{'joint_count_fitted_latent_rho':rho,'implied_spearman':6/math.pi*math.asin(rho/2),
                            'quadrature_joint_probability':joint_at(rho)},
 'assumed_rho_0_35_with_source_margins':{'joint_probability':q,
   'odds_ratio':q*(1-p_h-p_f+q)/((p_h-q)*(p_f-q)),
   'spearman':6/math.pi*math.asin(.35/2)},
 'assumed_rho_0_40_with_source_margins':{'joint_probability':q4,
   'odds_ratio':q4*(1-p_h-p_f+q4)/((p_h-q4)*(p_f-q4)),
   'spearman':6/math.pi*math.asin(.4/2)},
 'qualification':'The implied continuous rank coefficient is conditional on the Agent-chosen Gaussian copula; it is not reported by Zhu2010 or identified by the four cells alone.',
 'target_reference_read':False,'additional_generator_runs':0}
(W/'LAW_IMPLICATION_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps(out))

"""Independent algebraic checks of diagnoses; no cohorts or generator imports."""
from pathlib import Path
import hashlib, json, math
import numpy as np
from scipy.optimize import brentq
from scipy.special import gammaincc, gamma
from scipy.integrate import quad
from scipy.stats import norm

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
WORKSPACE=PROJECT.parents[1]

def read(p):return json.loads(Path(p).read_bytes())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    checks=[]
    def close(name,a,b,tol=1e-10):
        error=abs(float(a)-float(b));assert error<=tol,(name,a,b,error)
        checks.append({'name':name,'recomputed':float(a),'recorded':float(b),'absolute_difference':error,'tolerance':tol})
    gly=read(HERE/'GLYCEMIA_AUDIT.json'); iron=read(HERE/'IRON_LIPID_AUDIT.json')
    hpath=WORKSPACE/'evcUseH03/candidates/initial/model_spec.json'
    p=read(hpath)['parameters']; g=p['glucose']; h=p['hba1c']
    # Enumerate the prescribed discrete age support, not any observed records.
    bands=p['design']['age_bands'];ages=np.concatenate([np.arange(lo,hi+1) for lo,hi in bands])
    weights=np.concatenate([np.full(hi-lo+1,1/len(bands)/(hi-lo+1)) for lo,hi in bands])
    am=weights@ages;av=weights@((ages-am)**2)
    ra=np.arange(h['reference_age_range'][0],h['reference_age_range'][1]+1)
    rm=np.mean(ra);rv=np.mean((ra-rm)**2)
    bvar=p['bmi']['sd']**2;gv=g['sd']**2;fv=.25
    ga,gb,gf=[g[k] for k in ['age_slope','bmi_slope','female_slope']]
    meanvar=ga*ga*av+gb*gb*bvar+gf*gf*fv
    innovation=gv-meanvar
    concentration=(g['mean']*(g['upper']-g['mean'])-meanvar)/innovation-1
    rgmean=g['mean']+ga*(rm-am)
    rinnovation=(rgmean*(g['upper']-rgmean)-ga*ga*rv-gb*gb*bvar-gf*gf*fv)/(concentration+1)
    refvar=((h['reference_upper_quantile']-h['reference_mean'])/h['normal_quantile_z'])**2
    ha,hb,hf=[h[k] for k in ['age_slope','bmi_total_slope','female_total_slope']]
    def moments(c):
        residual=refvar-(ha+c*ga)**2*rv-hb*hb*bvar-hf*hf*fv-c*c*rinnovation
        total=residual+(ha+c*ga)**2*av+hb*hb*bvar+hf*hf*fv+c*c*innovation
        cov=(ha+c*ga)*ga*av+hb*gb*bvar+hf*gf*fv+c*innovation
        return residual,total,cov
    # Solve the unsquared correlation equation numerically, independently of
    # the audited quadratic coefficient solver. Bracket endpoints both have
    # valid positive variances; this is a mathematical check, not calibration.
    f=lambda c:moments(c)[2]/math.sqrt(gv*moments(c)[1])-h['marginal_glucose_correlation']
    assert moments(0)[0]>0 and moments(.02)[0]>0
    c=brentq(f,0,.02,xtol=1e-15);res,var,cov=moments(c)
    audit=gly['H03_variance_budget']
    close('H03 age variance',av,audit['age_variance'])
    close('H03 conditional glucose slope',c,audit['law_coefficients']['conditional_glucose_per_mg_dL'])
    close('H03 total HbA1c SD',math.sqrt(var),audit['whole_design_hba1c_sd'])
    close('H03 conditional variance',res,audit['hba1c_conditional_variance'])
    close('H03 glucose correlation',cov/math.sqrt(gv*var),.23)
    close('H03 BMI partial slope per5',5*(hb-c*gb),audit['law_coefficients']['Q3_bmi5'])
    # Reweighted threshold table then independent-pair mixture; no measurements.
    counts=np.array([[173.,85.],[331.,1082.]])
    source=counts/counts.sum();weighted=counts*np.array([2/3,1.])[None,:];weighted/=weighted.sum()
    target=.8*weighted+.2*np.outer(weighted.sum(axis=1),weighted.sum(axis=0))
    odds=lambda x:x[0,0]*x[1,1]/(x[0,1]*x[1,0])
    ia=iron['deterministic_checks_completed']['iron_source_counts_and_frozen_transforms']
    for n,val in [('source_OR',odds(source)),('A_reweighting_OR',odds(weighted)),('A_target_OR',odds(target)),
                  ('A_target_joint_probability',target[0,0]),('B_target_joint_probability',source[0,0])]:close('iron '+n,val,ia[n])
    # Exact within-sex covariances of the L03 multivariate lognormal law.
    lpath=WORKSPACE/'evcUseL03/candidates/initial/model_spec.json';l=read(lpath)['parameters']
    names=l['biomarker_order'];m=np.array([l['marginal_moments'][x]['mean'] for x in names]);s=np.array([l['marginal_moments'][x]['sd'] for x in names])
    r=np.array([l['female_to_male_geometric_ratios'][x] for x in names]);pf=l['female_probability']
    f1=1-pf+pf*r;f2=1-pf+pf*r*r
    v=np.log((1+(s/m)**2)*f1*f1/f2);mu=np.log(m/f1)-v/2
    R=np.eye(3)
    for i,j,key in [(0,1,'bmi_tc'),(0,2,'bmi_hdl'),(1,2,'tc_hdl')]:R[i,j]=R[j,i]=2*np.sin(np.pi*l['copula_spearman'][key]/6)
    latent=R*np.sqrt(np.outer(v,v));within=np.zeros((3,3));prob=0
    for flag,weight in [(0,1-pf),(1,pf)]:
        loc=mu+flag*np.log(r);means=np.exp(loc+v/2)
        within+=weight*np.outer(means,means)*np.expm1(latent)
        prob+=weight*norm.cdf((loc[2]-loc[1])/math.sqrt(v[2]+v[1]-2*latent[1,2]))
    residual=within[1:,1:]-np.outer(within[1:,0],within[0,1:])/within[0,0]
    la=iron['deterministic_checks_completed']['L03_exact_model_projection']
    close('L03 HDL slope per5',within[0,2]/within[0,0]*38.67*5,la['HDL_BMI_per5_mg_dL'])
    close('L03 TC slope per5',within[0,1]/within[0,0]*38.67*5,la['TC_BMI_per5_mg_dL'])
    close('L03 adjusted residual correlation',residual[0,1]/math.sqrt(residual[0,0]*residual[1,1]),la['residual_Pearson'])
    close('L03 HDL>TC probability',prob,iron['deterministic_checks_completed']['all_lipid_law_margins_and_order_support']['L03']['P_HDL_gt_TC_mixture'])
    # Numerically integrate Gamma density to independently check the truncated
    # moment identity used by the HRS quadrature, with two invented parameter sets.
    for alpha,theta,knot in [(6,.7,6.5),(35,.17,6.5)]:
        for j in range(3):
            numeric=quad(lambda x:x**(alpha+j-1)*np.exp(-x/theta)/(gamma(alpha)*theta**alpha),knot,np.inf,epsabs=1e-11,epsrel=1e-11)[0]
            formula=theta**j*gamma(alpha+j)/gamma(alpha)*gammaincc(alpha+j,knot/theta)
            close(f'HRS truncated Gamma identity {alpha} moment{j}',numeric,formula,1e-9)
    out={'status':'PASS_INDEPENDENT_ALGEBRA_CHECKS','scope':'Different root implementation of H03 unsquared equation, iron contingency transformations, L03 covariance projection and HRS truncated-moment identity. Not an independent re-fit of clinical data or all HRS integration dimensions.',
         'checks':checks,'count':len(checks),'new_tables':0,'clinical_rows_read':0,'generator_imports':0,'frozen_files_modified':False,
         'inputs':[{'path':str(f.relative_to(PROJECT)) if f.is_relative_to(PROJECT) else 'local_archive/'+str(f.relative_to(WORKSPACE)).replace('\\','/'),'sha256':digest(f)} for f in [hpath,lpath,HERE/'GLYCEMIA_AUDIT.json',HERE/'IRON_LIPID_AUDIT.json',HERE/'HRS_DETERMINISTIC_AUDIT.json']]}
    (HERE/'INDEPENDENT_CHECK.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':out['status'],'checks':len(checks),'maximum_abs_difference':max(x['absolute_difference'] for x in checks)}))

if __name__=='__main__':main()

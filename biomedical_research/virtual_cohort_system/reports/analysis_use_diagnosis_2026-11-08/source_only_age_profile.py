"""Source-only age-profile moment sensitivity; no sampling or generator import.

Uses original Pani Table 1 XML, cross-checks the admitted H03 evidence packet,
and computes scalar mixture moments under a stated normal-within-age assumption.
All outputs are diagnostics, never a candidate or a fitted/revised generator.
"""
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from statistics import NormalDist
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
BUNDLE = WORKSPACE / 'evcUseH03'
SOURCE_HASH = 'fac9d24329896a04d65a0f5858c64238365c01bc0b9616e64ee5bc00271c64f6'
FILES = {
    'original_pani_xml': BUNDLE / f'sources/gateway/{SOURCE_HASH}.xml',
    'admitted_evidence': BUNDLE / 'candidates/initial/evidence.json',
    'H03_retained_specification': BUNDLE / 'candidates/initial/model_spec.json',
    'H03_retained_generator_static_identity_only': BUNDLE / 'candidates/initial/generator.py',
    'task': BUNDLE / 'task.json',
}

def provenance(path):
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def extract_source():
    assert provenance(FILES['original_pani_xml'])['sha256'] == SOURCE_HASH
    original=ET.parse(FILES['original_pani_xml'])
    table=next(t for t in original.findall('.//table-wrap') if t.findtext('label')=='Table 1')
    evidence=json.loads(FILES['admitted_evidence'].read_text(encoding='utf-8'))
    source=next(s for s in evidence['sources'] if s['id']=='PMC2551641')
    assert source['artifacts'][0]['sha256']==SOURCE_HASH
    items={r['id']:r for r in evidence['items']}
    rows=[]
    for i,row in enumerate(table.findall('./table/tbody/tr')):
        cells=[''.join(c.itertext()).strip() for c in row.findall('td')]
        assert len(cells)==10
        mean=float(cells[8].split('±')[0].strip())
        se=float(cells[8].split('±')[1].strip())
        quantile=float(cells[9])
        mid='E_h_ref_mean' if i==3 else f'E_nh_mean_{i}'
        qid='E_h_ref_q' if i==3 else f'E_nh_q_{i}'
        assert items[mid]['estimate']==mean
        assert items[qid]['estimate']==quantile
        assert items[mid]['uncertainty']['kind']=='se'
        assert items[mid]['uncertainty']['value']==se
        assert items[qid]['q']==0.975
        assert items[mid]['source_id']==items[qid]['source_id']=='PMC2551641'
        rows.append({'source_age_label':cells[0], 'source_reported_n':int(cells[7].replace(',','')),
                     'mean':mean,'mean_SE_not_used_as_SD':se,'q975':quantile,
                     'evidence_ids':[mid,qid],'original_locator':f'Table 1 row {i+1}; NHANES nondiabetic mean±SE and 97.5th-percentile columns',
                     'mean_locator':items[mid]['locator'],'quantile_locator':items[qid]['locator']})
    assert len(rows)==8
    return rows,source

def age_weights(bands):
    # These are exact support weights, not participant rows or random draws.
    year_mass={age:Fraction(1,len(bands)*(hi-lo+1))
               for lo,hi in bands for age in range(lo,hi+1)}
    def group(age):
        if age<40:return 0
        if age>=70:return 7
        return 1+(age-40)//5
    weights=[sum((mass for age,mass in year_mass.items() if group(age)==g),Fraction(0)) for g in range(8)]
    assert sum(weights)==1
    mean=sum(Fraction(age)*mass for age,mass in year_mass.items())
    variance=sum((Fraction(age)-mean)**2*mass for age,mass in year_mass.items())
    return weights,float(mean),float(variance)

def mixture(means, variances, weights):
    mean=math.fsum(w*m for w,m in zip(weights,means))
    within=math.fsum(w*v for w,v in zip(weights,variances))
    between=math.fsum(w*(m-mean)**2 for w,m in zip(weights,means))
    total=within+between
    raw2=math.fsum(w*(v+m*m) for w,m,v in zip(weights,means,variances))
    assert abs(total-(raw2-mean*mean))<1e-13
    return {'mean':mean,'within_age_variance':within,'between_age_variance':between,
            'total_variance':total,'total_SD':math.sqrt(total),'between_age_fraction_of_variance':between/total,
            'second_moment_identity_absolute_error':abs(total-(raw2-mean*mean))}

def h03_algebra(p, age_mean, age_variance):
    # Independent scalar implementation of the retained law's moment equations.
    # No import, call, or evaluation of candidate code occurs.
    b,g,h=p['bmi'],p['glucose'],p['hba1c']
    vb=b['sd']**2; vf=0.25; vg=g['sd']**2
    ga,gb,gf=g['age_slope'],g['bmi_slope'],g['female_slope']
    lo,hi=h['reference_age_range']; ar=(lo+hi)/2; var_ar=((hi-lo+1)**2-1)/12
    explained_g=ga*ga*age_variance+gb*gb*vb+gf*gf*vf
    residual_g=vg-explained_g
    concentration_plus_one=(g['mean']*(g['upper']-g['mean'])-explained_g)/residual_g
    g_ref=g['mean']+ga*(ar-age_mean)
    explained_g_ref=ga*ga*var_ar+gb*gb*vb+gf*gf*vf
    residual_g_ref=(g_ref*(g['upper']-g_ref)-explained_g_ref)/concentration_plus_one
    ref_var=((h['reference_upper_quantile']-h['reference_mean'])/h['normal_quantile_z'])**2
    ha,hb,hf=h['age_slope'],h['bmi_total_slope'],h['female_total_slope']
    rho=h['marginal_glucose_correlation']; da=age_variance-var_ar
    v0=ref_var+ha*ha*da
    v1=2*ha*ga*da
    v2=ga*ga*da+residual_g-residual_g_ref
    c0=ha*ga*age_variance+hb*gb*vb+hf*gf*vf
    c1=vg-gb*gb*vb-gf*gf*vf
    qa=c1*c1-rho*rho*vg*v2
    qb=2*c0*c1-rho*rho*vg*v1
    qc=c0*c0-rho*rho*vg*v0
    discriminant=qb*qb-4*qa*qc
    assert discriminant>0
    roots=[(-qb-math.sqrt(discriminant))/(2*qa),(-qb+math.sqrt(discriminant))/(2*qa)]
    valid=[]
    for c in roots:
        variance=v0+v1*c+v2*c*c
        cov=c0+c1*c
        residual=ref_var-((ha+c*ga)**2*var_ar+hb*hb*vb+hf*hf*vf+c*c*residual_g_ref)
        if variance>0 and residual>0 and abs(cov/math.sqrt(vg*variance)-rho)<1e-12:
            valid.append((c,variance,residual,cov))
    assert len(valid)==1
    c,variance,residual,cov=valid[0]
    age_part=(ha+c*ga)**2*age_variance
    bmi_part=hb*hb*vb; sex_part=hf*hf*vf; glucose_part=c*c*residual_g
    assert abs(variance-(residual+age_part+bmi_part+sex_part+glucose_part))<1e-13
    return {'mean':h['reference_mean']+(ha+c*ga)*(age_mean-ar), 'variance':variance,'SD':math.sqrt(variance),
            'reference_age50_54_variance':ref_var,'conditional_glucose_coefficient':c,
            'variance_decomposition':{'linear_age_mean':age_part,'BMI_mean':bmi_part,'sex_mean':sex_part,
                                      'glucose_conditional_noise_transmitted':glucose_part,'HbA1c_conditional_noise':residual},
            'marginal_glucose_correlation_identity':cov/math.sqrt(vg*variance),
            'meaning':'Analytic marginal moments of the unchanged retained H03 law; not a proposed fit or a measured target.'}

def main():
    rows,source=extract_source()
    spec=json.loads(FILES['H03_retained_specification'].read_text(encoding='utf-8'))
    task=json.loads(FILES['task'].read_text(encoding='utf-8'))
    p=spec['parameters'];bands=p['design']['age_bands']
    assert bands==[[25,39],[40,54],[55,69],[70,79]]
    assert p['design']['rows_per_cell']==375 and task['n_rows']==3000
    assert all(f'{lo}-{hi}' in task['population'] for lo,hi in bands)
    weights,age_mean,age_variance=age_weights(bands)
    z=NormalDist().inv_cdf(0.975)
    means=[r['mean'] for r in rows]
    variances=[((r['q975']-r['mean'])/z)**2 for r in rows]
    w=[float(x) for x in weights]
    for i,r in enumerate(rows):
        r['design_weight_fraction']=str(weights[i]);r['design_weight']=w[i]
        r['normal_assumption_SD'] = math.sqrt(variances[i])
        r['normal_assumption_variance'] = variances[i]
    refmean=means[3];refvar=variances[3]
    variants={
      'single50_54_anchor_repeated':mixture([refmean]*8,[refvar]*8,w),
      'eight_means_with_constant50_54_variance':mixture(means,[refvar]*8,w),
      'eight_implied_variances_with_constant50_54_mean':mixture([refmean]*8,variances,w),
      'full_eight_pair_profile':mixture(means,variances,w),
    }
    h03=h03_algebra(p,age_mean,age_variance)
    full=variants['full_eight_pair_profile']
    full['weighted_within_variance_contributions']=[w[i]*variances[i] for i in range(8)]
    full['weighted_between_variance_contributions']=[w[i]*(means[i]-full['mean'])**2 for i in range(8)]
    contrast={'full_profile_minus_repeated_anchor_SD':full['total_SD']-math.sqrt(refvar),
              'full_profile_minus_H03_SD':full['total_SD']-h03['SD'],
              'full_profile_minus_H03_variance':full['total_variance']-h03['variance'],
              'full_profile_minus_H03_mean':full['mean']-h03['mean']}
    result={
      'schema_version':1,'created_date':'2026-11-08','status':'completed deterministic source-only sensitivity; not a candidate',
      'question':'Does using every admitted Pani age-band mean/97.5th-percentile pair itself raise HbA1c dispersion under the declared equal-band age design?',
      'source':{'identifier':'PMC2551641','doi':'10.2337/dc08-0577','table':'Table 1; NHANES nondiabetic columns',
                'population_and_measurement':source,'packet_vs_original_all16_values_match':True},
      'source_rows':rows,
      'design':{'age_bands':bands,'sex_age_cell_count':8,'equal_probability_per_age_band':0.25,
                'within_band_age_rule':'Uniform inclusive integer ages, an existing H03 modeling assumption; the task supplies quotas but not within-band year weights.',
                'weights_source':'Declared task equal age-band quotas plus existing within-band uniform assumption; no measured target weights or source counts used.',
                'age_mean':age_mean,'age_variance':age_variance,'source_counts_used_for_weighting':False},
      'method':{'normal_quantile_z':z,'within_age_formula':'sigma_g = (q97.5_g - mean_g)/Phi^-1(.975), solely under a normal-within-source-age-group approximation.',
                'mixture_formula':'mean=sum(w_g mean_g); variance=sum(w_g sigma_g^2)+sum(w_g (mean_g-overall_mean)^2).',
                'no_extra_predictor_variance_added':'The source age-group variance is marginal over sex, BMI and glucose within that age group. No extra sex/BMI/glucose explained variance is added to this full-profile calculation.',
                'variant_purpose':'Four fixed descriptive decompositions distinguish changing means from changing implied within-age variance; no variant is selected or fitted.'},
      'sensitivity_variants':variants,
      'unchanged_H03_analytic_law':h03,
      'contrasts':contrast,
      'interpretation':('The full age profile increases dispersion relative to repeating only the50-54 anchor with no age variation, but produces lower total SD than the unchanged H03 law. Therefore unused age-profile information does not, under this approximation and declared grid, establish a route to increasing H03 dispersion. It changes age-pattern assumptions and the allocation of variance; it does not identify a corrected cohort law.'),
      'limitations':['A mean and one upper quantile do not identify the true within-age SD. Normal shape is an explicit sensitivity assumption, not a recovered source parameter; reported mean SEs were verified but never converted to individual SDs.',
                     'Source estimates are rounded, survey weighted NHANES summaries. The calculation uses equal task age-band weights and uniform years, not original survey weights or source age counts; it is not a source replay.',
                     'Source age>=70 includes ages above79, whereas the task stops at79. Applying that source bin to70-79 requires an unsupported within-bin transport assumption.',
                     'US source selection, assays, calendar, sex/covariate composition and diabetes/fasting restrictions differ from the Mexican task. Mean/quantile transfer is unvalidated.',
                     'The profile covers only HbA1c-age marginal moments. It does not specify HbA1c joint relations with BMI, sex or glucose, adjusted regressions, tails beyondq97.5, or a sampling program.',
                     'H03 contrast is a comparison of two mathematical assumptions, not an accuracy comparison against measured target data; no target results were read by this script.'],
      'actual_checks':['Verified original XML SHA256 against the admitted source artifact hash.','Cross-checked all8 NHANES means and all8 quantiles against their admitted evidence IDs; also verified all8 reported SE labels/values.','Derived8 profile weights exactly from declared equal bands and uniform integer age support; weights sum to1.','Checked total-variance result against second-raw-moment identity for every fixed decomposition.','Independently derived unchanged H03 marginal mean/variance using scalar covariance algebra; checked signed correlation and variance-budget identities.','No candidate imports, generator calls, RNG, row sampling, raw clinical tables, target aggregate lookup or writes outside the new diagnosis unit.'],
      'provenance':[dict(role=k,**provenance(v)) for k,v in FILES.items()]+[dict(role='this_calculation',**provenance(Path(__file__).resolve()))],
      'next_step':'Independent arithmetic/source review only. Preserve the frozen H03 candidate and closed delivery batch; do not build a replacement generator or choose dispersion to approach a known target.'
    }
    (HERE/'AGE_PROFILE_SENSITIVITY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'full_profile':full,'H03_law':h03,'contrasts':contrast},indent=2))

if __name__=='__main__':main()

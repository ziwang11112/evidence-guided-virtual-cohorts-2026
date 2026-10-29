"""Construct source-only candidate artifacts. NEVER imports or calls a generator.

Covariate construction and algebraic specification preparation are permitted;
all TG simulation is reserved for the controller's isolated execution adapter.
"""
from pathlib import Path
import ast
import copy
import hashlib
import json
import math
import shutil
import sys

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.stats import gamma, lognorm

P = Path(__file__).resolve().parent
PROJECT = P.parents[2]
sys.path.insert(0, str(PROJECT))
from cohort_harness.contracts import validate_evidence, validate_spec, validate_input
from cohort_harness.lifecycle import validate_program
from cohort_harness.source_replay import _check_metadata, _input_task


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


TASK = json.loads((P / 'task.json').read_text(encoding='utf-8-sig'))
REGISTRY = json.loads((P / 'registry.json').read_text(encoding='utf-8-sig'))
EVIDENCE = {'schema_version': 1, 'sources': [], 'items': []}
for sid, identifier, population, measurement, cohorts in [
    ('oh2019', 'Oh, Sung, Chun 2019; doi:10.1186/s12944-019-1134-0; PMC6911291.1, sole current version in admitted metadata',
     'Healthy Twin Study, Korea: 2672 adults/family members, 1029 men and 1643 women; excludes treatment with dyslipidemia or diabetes medication. Family and twin structure; calendar descriptions differ between abstract and methods.',
     'At least 12-hour overnight fast; EDTA plasma; Roche Cobas 6000. mg/dL. Glycerol correction not explicitly reported; equivalence to old target assay is assumed, not verified.', ['Healthy Twin Study Korea']),
    ('bansal2007', 'Bansal et al. JAMA 2007;298:309-316; doi:10.1001/jama.298.3.309; admitted publisher-text snapshot',
     "Women's Health Study initially healthy US women aged at least 45, enrolled 1992-1995; fasting subset 20118 (self-reported >=8 hours). Only fasting descriptive data used.",
     'EDTA plasma; enzymatic TG assay corrected for endogenous glycerol; Hitachi 917 with Roche reagents/calibrators; mg/dL. Old-target-assay equivalence remains a transport assumption.', ["Women's Health Study"]),
]:
    EVIDENCE['sources'].append(dict(id=sid, identifier=identifier, population=population, measurement=measurement, cohort_ids=cohorts,
        artifacts=[{'path': x['path'], 'sha256': x['sha256']} for x in REGISTRY['artifacts'] if x['source_id'] == sid]))


def item(eid, source, locator, variables, kind, estimate, unit, selection, applicability, uncertainty=None, adjustment=None, **extra):
    obj = dict(id=eid, source_id=source, locator=locator, variables=variables, kind=kind, estimate=estimate,
               unit=unit, uncertainty=uncertainty or {'kind': 'not_reported'}, adjustment=adjustment or [],
               selection=selection, applicability=applicability)
    obj.update(extra)
    EVIDENCE['items'].append(obj)
    return eid


SHARED_ASSUMPTIONS = [
    {'id': 'A_shared_source_interpretation', 'description': 'The same admitted Oh PMC6911291.1 and Bansal publisher snapshot, extraction, source populations, measurement mapping and diagnostic definitions are used for all structures and revisions. Statistics from each paper share participants; source seeds and repeated tables are not independent clinical evidence. No target outcome evidence is available.'},
    {'id': 'A_oh_context', 'description': 'Oh source context has 160320 synthetic rows: 60 times each published sex count. Within each sex, age and BMI are generated separately from maximum-entropy discrete marginal distributions constrained by Table 1 mean/SD and Table 2 stratum counts. Assumed age support 18..85 years and BMI grid 14..45 at 0.05 spacing. Entropy is relative to a uniform grid within each reported stratum. Quantile allocation and independent fixed-seed permutations approximate independence of age and BMI conditional on sex. The joint distribution, tails and family links are unreported; independence is a working approximation, not a discovered fact.'},
    {'id': 'A_bansal_context', 'description': 'Bansal fasting context has 80472 synthetic women (4 times 20118). Age is 45 plus a gamma distribution with excess mean 9.5 and SD 7.2, rounded to integer years and capped at 120 solely to satisfy task support. BMI is lognormal with arithmetic mean 25.9 and SD 5.0. Deterministic stratified marginal quantiles are independently permuted using the one fixed context seed. Age-BMI dependence, hormone use, medication and other risk factors are unknown. TG tertile-specific age/BMI summaries are diagnostics only and are not used to construct covariates conditional on an assigned TG outcome.'},
    {'id': 'A_source_measurement', 'description': 'All source rows use legacy_proxy and checks use identity mg/dL mapping. Bansal explicitly corrected endogenous glycerol, supporting a glycerol-blanked proxy; Oh reports Cobas 6000 but not glycerol blanking, so its equivalence is weaker and assumed. Both used EDTA plasma, whereas target is fasting serum LBXTLG. Neither source proves equivalence to the exact old NHANES assay. This uncertainty remains common to all structures.'},
    {'id': 'A_assay_transfer', 'description': 'The task-supplied forward equation 12.45 + 1.022 * legacy_proxy TG is applied only to unblanked_2021_2023 rows. It is measurement context, not target-population association evidence. The point equation is treated deterministically because no coefficient covariance is supplied here. It does not establish interchangeability or alter age/BMI/sex biology; backward sensitivity is controlled elsewhere.'},
    {'id': 'A_quantile', 'description': 'Bansal does not report its quantile interpolation convention. Source replay uses explicitly typed linear (Hyndman-Fan type 7) sample quantiles as an approximation, retaining reported 81, 115 and 169 mg/dL without converting them.'},
    {'id': 'A_bins', 'description': 'Continuous TG is compared with Oh thresholds 150, 200 and 500 mg/dL. Oh Table 1 says >500 while prose says 500 and up; a continuous draw has zero exact-threshold mass. For Bansal integer-labeled tertiles and quintiles, half-unit boundaries 90.5/147.5 and 73.5/98.5/132.5/184.5 approximate rounding to reported integer mg/dL. Cumulative proportions are derived from published counts; these preserve every category count without pretending the bins are exact quantile probabilities.'},
    {'id': 'A_oh_ols', 'description': 'Oh Table 3 reports age/sex-adjusted simple linear BMI regression. The source replay estimates ordinary unweighted OLS TG~age+sex+BMI with intercept; sex is coded 1 male, 2 female and the BMI coefficient is invariant to reference coding. Family weighting/correlation and exact analysis details are unavailable, so this is approximate. Table 4 additionally adjusted metabolic model, Table 5 mixed lifestyle model, and Table 6 co-twin estimands are not substituted for Table 3.'},
    {'id': 'A_oh_table2', 'description': 'Oh Table 2 TG summaries have no explicit arithmetic/geometric label and methods mention geometric averages. Count-weighted BMI strata reconstruct 141.5937/97.2021 and age strata 141.6062/97.2153 mg/dL, supporting an arithmetic reading but not resolving contradictory wording. They are retained as reported_other with no arithmetic replay. Only qualitative shape motivates assumptions; no summary is relabeled as a verified conditional arithmetic mean.'},
    {'id': 'A_unmeasured', 'description': 'The generator has only age, sex and BMI as biological predictors. Missing medication, hormonal, diet, alcohol, diabetes, ancestry and family variables are integrated into individual residual variation or a latent state without claiming their actual values or conditional independence in real populations. Neither a nonsignificant result nor an absent association is evidence of zero.'},
    {'id': 'A_transport', 'description': 'A common age/sex/BMI law is transported from selected Korean families and initially healthy middle-aged US women to fasting US adults aged 20-79. Cohort, era, exclusion criteria and covariate support differ. No cohort label or opaque ID is used to switch biological laws, and target covariate frequencies are not calibration outcomes. This is an assumption-dependent virtual distribution, not individual recovery, causal identification or validated inferential utility.'},
    {'id': 'A_monte_carlo', 'description': 'The source covariates and biological parameters are fixed. Seeds 76101,76102,76103 vary individual residual and, in s3, latent-state draws only. Their spread is Monte Carlo variation, not evidence uncertainty. Large source contexts reduce simulation noise but rare >500 events, especially women, remain noisy. Target draw schedule is 76201..76205; builder does not execute it.'},
]

OH = {
    1: dict(n=1029, age=(43.9,13.6), bmi=(24.4,3.1), tg=(141.6,107.7), tg_counts=[704,130,185,10], age_counts=[127,360,212,154,176], bmi_counts=[63,263,288,382,33], age_tg=[143,147.5,140.6,143.5,128.1], bmi_tg=[91.8,109.4,141.4,165.3,220.5]),
    2: dict(n=1643, age=(43.3,12.7), bmi=(23.0,3.2), tg=(97.2,61.0), tg_counts=[1401,131,110,1], age_counts=[152,633,380,250,228], bmi_counts=[264,633,352,346,48], age_tg=[78.1,80.7,89.4,127.8,135.3], bmi_tg=[73.8,86.5,100.9,126.7,127.3]),
}


def filt(column, op, value):
    return {'column': column, 'op': op, 'value': value}


def operator(kind, unit, selection=None, **fields):
    return dict(kind=kind, unit=unit, selection=selection or [], missing_policy='error', **fields)


def replay_check(eid, op, assumptions=None, reason='Compare the retained source statistic with the same statistic from verified generator output under the declared approximate source covariates.'):
    return dict(id=eid.lower(), evidence_id=eid, status='approximate', operator=op, assumption_ids=assumptions or [], reason=reason)


OH_CHECKS, BANSAL_CHECKS, UNREPLAYED = [], [], []
for sex, d in OH.items():
    sex_label = 'male' if sex == 1 else 'female'
    selection = f'Oh full analytic sample, sex={sex} ({sex_label}), n={d["n"]}; untreated with dyslipidemia/diabetes medication.'
    sf = [filt('sex','eq',sex)]
    for variable, source_label, unit in [('age','Age','years'),('bmi','BMI','kg/m^2'),('tg_mg_dl','TG','mg/dL')]:
        values = d['tg' if variable == 'tg_mg_dl' else variable]
        for kind, val in zip(['mean','sd'], values):
            eid = item(f'E_oh_{sex_label}_{variable}_{kind}', 'oh2019', f'Table 1 {source_label}, {sex_label}; column explicitly Mean/S.D.; Results Subject characteristics', [variable], kind,val,unit,selection,
                       'Arithmetic mean or individual sample SD as explicitly labeled in Table 1 and narrative; SD is not SE. Covariate summaries describe source input, TG summaries constrain marginal distribution.')
            OH_CHECKS.append(replay_check(eid,operator(kind,unit,sf,column=variable)))
    for threshold, count in zip([150,200,500], np.cumsum(d['tg_counts'])[:3]):
        eid=item(f'E_oh_{sex_label}_tg_below_{threshold}', 'oh2019','Table 1 TG category counts and Results TG levels and other factors', ['tg_mg_dl'],'proportion',int(count)/d['n'],'1',selection,
                 f'Derived cumulative proportion from counts {d["tg_counts"]}; numerator {int(count)} / denominator {d["n"]}. Continuous boundary approximation and >500/500+ discrepancy declared.')
        OH_CHECKS.append(replay_check(eid,operator('proportion','1',sf,event=filt('tg_mg_dl','lt',threshold)),['A_bins']))
    for variable in ['age','bmi']:
        for k,value in enumerate(d[variable+'_tg']):
            eid=item(f'E_oh_{sex_label}_{variable}_stratum_{k+1}_tg', 'oh2019',f'Table 2, {variable} stratum {k+1}, {sex_label}', ['tg_mg_dl',variable],'reported_other',value,'mg/dL',selection+f' Published {variable} stratum {k+1}.',
                     'Summary type not resolved: methods mention geometric averages; count-weighted arithmetic reading reconstructs Table 1. Not replayed as an arithmetic mean.',statistic_name='TG stratum summary; arithmetic/geometric ambiguity')
            UNREPLAYED.append((eid,'A_oh_table2','No geometric-mean operator; arithmetic summary type is not established unambiguously. Retained rather than substituted.'))

eid=item('E_oh_bmi_age_sex_slope','oh2019','Table 3, BMI row; title explicitly says simple linear regression, sex and age adjusted',['tg_mg_dl','bmi'],'ols_coefficient',6.813,'mg/dL per kg/m^2','Full untreated analytic sample, men and women, n=2672.',
         'Conditional linear association, not a marginal Pearson/Spearman correlation or causal effect.',{'kind':'ci','low':5.853,'high':7.774,'level':.95},['age','sex'])
OH_CHECKS.append(replay_check(eid,operator('ols_coefficient','mg/dL per kg/m^2',outcome='tg_mg_dl',predictors=['age','sex','bmi'],term='bmi',include_intercept=True),['A_oh_ols']))
for eid,loc,val,unc,adjust,reason in [
    ('E_oh_metabolic_bmi','Table 4 BMI',4.385,{'kind':'ci','low':3.406,'high':5.363,'level':.95},['sex','age','fasting_glucose','hdl','ldl','alcohol'],'Additional measured metabolic covariates and their joint distribution are unavailable.'),
    ('E_oh_mixed_bmi','Table 5 BMI',6.91,{'kind':'se','value':.89},['age','sex','diet','physical_activity','drinking','audit','smoking','family_random_effect'],'Mixed model and lifestyle covariates unavailable; SE 0.89 is not individual TG SD.'),
    ('E_oh_cotwin_bmi','Table 6 BMI',9.94,{'kind':'ci','low':3.42,'high':16.46,'level':.95},['cotwin_pair','age','sex','fasting_glucose','hdl','ldl','body_fat','carbohydrate','alcohol'],'Selected monozygote co-twin design cannot be reconstructed from independent rows.'),
]:
    item(eid,'oh2019',loc,['tg_mg_dl','bmi'],'reported_other',val,'mg/dL per kg/m^2','Analysis-specific sample and model as described in locator.',reason,unc,adjust,statistic_name='Published adjusted BMI coefficient with unavailable design/covariates')
    UNREPLAYED.append((eid,'A_oh_ols',reason))

BS='Bansal fasting women, >=45 years, self-reported >=8 hours since meal, n=20118; initially healthy US women.'
for kind,q,val,label in [('quantile',.25,81,'q25'),('median',None,115,'median'),('quantile',.75,169,'q75')]:
    extras={'method':'not_reported'}
    fields={'column':'tg_mg_dl','method':'linear'}
    if q is not None:
        extras['q']=q
        fields['q']=q
    eid=item('E_bansal_'+label,'bansal2007','Results L201 fasting median (IQR) 115 (81-169)', ['tg_mg_dl'],kind,val,'mg/dL',BS,'Reported quantiles, not mean/SD. Interpolation convention unreported.',**extras)
    BANSAL_CHECKS.append(replay_check(eid,operator(kind,'mg/dL',**fields),['A_quantile']))
for var, value in [('age',.18),('bmi',.33)]:
    eid=item(f'E_bansal_spearman_{var}','bansal2007','Table 2 fasting column (L132/L226); Methods L192', ['tg_mg_dl',var],'spearman_correlation',value,'1',BS,
             'Marginal unweighted Spearman rank correlation. Not a conditional slope; depends on source joint covariate distribution and residual law. Replayed with average-tie ranks.')
    BANSAL_CHECKS.append(replay_check(eid,operator('spearman_correlation','1',x=var,y='tg_mg_dl')))
for scheme,counts,bounds in [('tertile',[6590,6802,6726],[90.5,147.5]),('quintile',[3915,3981,4133,4052,4037],[73.5,98.5,132.5,184.5])]:
    for k,(count,bound) in enumerate(zip(np.cumsum(counts),bounds),1):
        eid=item(f'E_bansal_{scheme}_cum{k}','bansal2007',f'Table {1 if scheme=="tertile" else 4}, fasting {scheme} counts', ['tg_mg_dl'],'proportion',int(count)/20118,'1',BS,
                 f'Derived from published category counts {counts}, cumulative numerator {int(count)}/20118. These are observed fractions, not exact theoretical {scheme} probabilities.')
        BANSAL_CHECKS.append(replay_check(eid,operator('proportion','1',event=filt('tg_mg_dl','lt',bound)),['A_bins']))
for k,sel in enumerate([[filt('tg_mg_dl','lt',90.5)],[filt('tg_mg_dl','ge',90.5),filt('tg_mg_dl','lt',147.5)],[filt('tg_mg_dl','ge',147.5)]],1):
    for var,unit,means,sds in [('age','years',[53.1,54.8,55.6],[6.9,7.3,7.2]),('bmi','kg/m^2',[24.2,25.9,27.6],[4.1,5.0,5.1])]:
        for kind, values in [('mean',means),('sd',sds)]:
            eid=item(f'E_bansal_tertile{k}_{var}_{kind}','bansal2007',f'Table 1 fasting TG tertile {k}, {var} mean(SD), L121/L124', [var],kind,values[k-1],unit,BS+f' Conditional on published TG tertile {k}.',
                     'Covariate distribution conditional on TG group; this is not the mean TG conditional on covariates. Checked on generated outcome groups; source covariates were not preassigned outcome strata.')
            BANSAL_CHECKS.append(replay_check(eid,operator(kind,unit,sel,column=var),['A_bins']))
for var,unit,values in [('age','years',[54.5,7.2]),('bmi','kg/m^2',[25.9,5.0])]:
    for kind,value in zip(['mean','sd'],values):
        eid=item(f'E_bansal_{var}_{kind}','bansal2007','Table 1 fasting All column, L121/L124',[var],kind,value,unit,BS,'Published marginal source-covariate summary; SD is individual spread, not SE.')
        BANSAL_CHECKS.append(replay_check(eid,operator(kind,unit,column=var)))
item('E_bansal_assay','bansal2007','Laboratory Methods L182-183',[],'contextual',None,'',BS,'EDTA plasma, enzymatic TG corrected for endogenous glycerol. Day-to-day assay reproducibility is not population TG SD.')
item('E_oh_assay','oh2019','Clinical examination: blood tests',[],'contextual',None,'','Oh full analytic sample.','Minimum 12-hour fast, EDTA plasma, Cobas 6000; glycerol blanking unreported.')


def entropy_marginal(grid, groups, counts, target_mean, target_sd, repeats):
    """Covariate-only maximum entropy distribution, constrained by summaries."""
    group_weights=np.asarray(counts,dtype=float)/sum(counts)
    x=(grid-target_mean)/target_sd
    def prob(theta):
        logits=theta[0]*x+theta[1]*x*x
        ans=np.zeros(len(grid))
        for j,w in enumerate(group_weights):
            ix=groups==j
            z=logits[ix]
            ex=np.exp(z-z.max())
            ans[ix]=w*ex/ex.sum()
        return ans
    def residual(theta):
        p=prob(theta)
        return np.array([p@x,p@(x*x)-1])
    fit=least_squares(residual,[0.,-.5],xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=1000)
    if np.max(np.abs(residual(fit.x)))>1e-8:
        raise ValueError('Covariate moment constraints were not solved')
    probabilities=prob(fit.x)
    rows=[]
    for j,count in enumerate(counts):
        ix=groups==j
        conditional=probabilities[ix]/group_weights[j]
        cdf=np.cumsum(conditional)
        u=(np.arange(count*repeats)+.5)/(count*repeats)
        rows.append(grid[ix][np.searchsorted(cdf,u)])
    return np.concatenate(rows), {'lambda':fit.x.tolist(),'max_scaled_moment_error':float(np.max(np.abs(residual(fit.x))))}


def contexts():
    rng=np.random.default_rng(76001)
    oh=[]
    fit_details={}
    for sex,d in OH.items():
        agegrid=np.arange(18,86,dtype=float)
        agegroups=np.searchsorted([30,40,50,60],agegrid,side='right')
        bmigrid=np.round(np.arange(14,45.001,.05),2)
        bmigroups=np.searchsorted([20,23,25,30],bmigrid,side='right')
        age,afit=entropy_marginal(agegrid,agegroups,d['age_counts'],*d['age'],60)
        bmi,bfit=entropy_marginal(bmigrid,bmigroups,d['bmi_counts'],*d['bmi'],60)
        n=len(age)
        oh.append(pd.DataFrame({'record_id':[f'oh{sex}_{i:06d}' for i in range(n)],'age':rng.permutation(age).astype(int),'sex':sex,'bmi':rng.permutation(bmi),'tg_assay':'legacy_proxy'}))
        fit_details[str(sex)]={'age':afit,'bmi':bfit}
    oh=pd.concat(oh,ignore_index=True)
    n=20118*4
    u=(np.arange(n)+.5)/n
    excess_mean,excess_sd=9.5,7.2
    age=np.minimum(np.rint(45+gamma.ppf(u,a=(excess_mean/excess_sd)**2,scale=excess_sd**2/excess_mean)),120).astype(int)
    bmi_sigma=math.sqrt(math.log1p((5/25.9)**2))
    bmi=lognorm.ppf(u,s=bmi_sigma,scale=25.9/math.exp(.5*bmi_sigma*bmi_sigma))
    bansal=pd.DataFrame({'record_id':[f'whs_{i:06d}' for i in range(n)],'age':rng.permutation(age),'sex':2,'bmi':rng.permutation(bmi),'tg_assay':'legacy_proxy'})
    detail={'construction_seed':76001,'purpose':'Covariate-only source reconstruction; no generator or TG outcome is calculated.','oh_entropy_fits':fit_details,'summaries':{}}
    for label,frame in [('oh',oh),('bansal',bansal)]:
        child=copy.deepcopy(TASK)
        child['n_rows']=len(frame)
        validate_input(frame,child)
        detail['summaries'][label]={'rows':len(frame),'by_sex':{str(sex):part[['age','bmi']].agg(['mean','std','min','max']).to_dict() for sex,part in frame.groupby('sex')}}
    return oh,bansal,detail


GENERATOR_COMMON='''import numpy as np


def _measurement(legacy, observed, p):
    regime = observed["tg_assay"].to_numpy()
    valid = (regime == "legacy_proxy") | (regime == "unblanked_2021_2023")
    if not np.all(valid):
        raise ValueError("Unknown measurement regime")
    result = observed.copy(deep=True)
    assay = p["assay"]
    result["tg_mg_dl"] = np.where(regime == "unblanked_2021_2023", assay["intercept"] + assay["slope"] * legacy, legacy)
    return result


'''

GENERATOR_S1=GENERATOR_COMMON+'''def generate(observed, spec, seed):
    """Positive additive conditional arithmetic mean with multiplicative noise."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    reference = p["reference"]
    m = np.asarray(reference["tg_mean"])[sex]
    m = m + p["bmi_slope"] * (bmi - np.asarray(reference["bmi_mean"])[sex])
    m = m + np.asarray(p["age_slope"])[sex] * (age - np.asarray(reference["age_mean"])[sex])
    regular = p["positive_mean"]
    m = regular["floor"] + regular["width"] * np.logaddexp(0, (m - regular["floor"]) / regular["width"])
    cv = np.asarray(p["residual_cv"])[sex]
    variance = np.log1p(cv * cv)
    legacy = m * np.exp(rng.normal(size=len(observed)) * np.sqrt(variance) - .5 * variance)
    return _measurement(legacy, observed, p)
'''

GENERATOR_S2=GENERATOR_COMMON+'''def generate(observed, spec, seed):
    """Nonlinear multiplicative log-location model with saturation."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    reference = p["reference"]
    dx = bmi - np.asarray(reference["bmi_mean"])[sex]
    w = p["bmi_saturation_width"]
    log_location = np.log(np.asarray(p["reference_median"])[sex])
    log_location += np.asarray(p["log_bmi_slope"])[sex] * w * np.tanh(dx / w)
    female_age = p["female_age"]
    transition = 1 / (1 + np.exp(-(age - female_age["midpoint"]) / female_age["width"]))
    age_effect = np.where(sex == 1, female_age["amplitude"] * (transition - female_age["source_center"]), p["male_log_age_slope"] * (age - reference["age_mean"][0]))
    log_location += age_effect
    log_sd = np.asarray(p["residual_log_sd"])[sex]
    legacy = np.exp(log_location + log_sd * rng.normal(size=len(observed)))
    return _measurement(legacy, observed, p)
'''

GENERATOR_S3=GENERATOR_COMMON+'''def generate(observed, spec, seed):
    """Age/BMI-dependent latent state with separate gamma TG components."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    reference = p["reference"]
    eta = np.asarray(p["state_intercept"])[sex].copy()
    eta += np.asarray(p["state_bmi_slope"])[sex] * (bmi - np.asarray(reference["bmi_mean"])[sex])
    eta += np.asarray(p["state_age_slope"])[sex] * (age - np.asarray(reference["age_mean"])[sex])
    probability = np.exp(-np.logaddexp(0, -eta))
    state = (rng.random(len(observed)) < probability).astype(int)
    means = np.asarray(p["component_mean"])[sex, state]
    cv = np.asarray(p["component_cv"])[sex, state]
    shape = 1 / (cv * cv)
    legacy = rng.gamma(shape, means / shape)
    return _measurement(legacy, observed, p)
'''


def make_spec(sid):
    reference={'tg_mean':[141.6,97.2],'tg_sd':[107.7,61.0],'age_mean':[43.9,43.3],'age_sd':[13.6,12.7],'bmi_mean':[24.4,23.0],'bmi_sd':[3.1,3.2]}
    params={'structure_id':sid,'reference':reference,'assay':{'intercept':12.45,'slope':1.022}}
    assumptions=copy.deepcopy(SHARED_ASSUMPTIONS)
    prov={
        'structure_id':{'evidence_ids':[],'assumption_ids':['A_structure'],'derivation':'Prespecified scientific sensitivity structure; no probability or ranking among structures.'},
        'reference':{'evidence_ids':[f'E_oh_{sex}_{var}_{kind}' for sex in ['male','female'] for var in ['tg_mg_dl','age','bmi'] for kind in ['mean','sd']],'assumption_ids':['A_transport'],'derivation':'Reported Oh sex-specific marginal moments. They are centering and spread anchors, not individual conditional values. Order is male, female.'},
        'assay':{'evidence_ids':[],'assumption_ids':['A_assay_transfer','A_source_measurement'],'derivation':'Task-supplied technical equation; not counted as an approved biological evidence source.'},
    }
    def par(name,val,eids,aids,why):
        params[name]=val
        prov[name]={'evidence_ids':eids,'assumption_ids':aids,'derivation':why}
    if sid=='s1':
        assumptions.append({'id':'A_structure','description':'s1 assumes an additive conditional arithmetic TG mean with one BMI slope, sex-specific linear age slopes, a soft positive floor, and mean-one independent lognormal individual noise. Constant residual CV within sex permits heteroskedastic absolute TG. It imposes no age-BMI interaction on the arithmetic-mean scale away from the floor. Linear age slopes and all transport are assumptions; neither source identifies the full conditional law.'})
        par('bmi_slope',6.813,['E_oh_bmi_age_sex_slope'],['A_oh_ols','A_structure'],'Copy the reported reduced age/sex-adjusted slope as an approximate conditional arithmetic-mean slope, not the fully adjusted or co-twin coefficient.')
        par('age_slope',[-.2,1.6],['E_oh_male_age_stratum_1_tg','E_oh_male_age_stratum_5_tg','E_oh_female_age_stratum_1_tg','E_oh_female_age_stratum_5_tg','E_bansal_spearman_age'],['A_oh_table2','A_structure'],'Chosen mild male decrease and female increase in mg/dL/year reflect reported sex-specific age shapes; not obtained by replacing marginal Spearman with a coefficient. The female linear slope smooths the stronger middle-age transition.')
        cvs=[]
        for i in range(2):
            v=(6.813*reference['bmi_sd'][i])**2+(params['age_slope'][i]*reference['age_sd'][i])**2
            cvs.append(math.sqrt((reference['tg_sd'][i]**2-v)/(reference['tg_mean'][i]**2+v)))
        par('residual_cv',cvs,[f'E_oh_{sex}_tg_mg_dl_{kind}' for sex in ['male','female'] for kind in ['mean','sd']],['A_oh_context','A_structure'],'Analytic independent-covariate variance decomposition: Var(mu)=bBMI^2 Var(BMI)+bAge^2 Var(age); CV^2=(reportedTGVar-Var(mu))/(reportedMean^2+Var(mu)). Soft floor and approximate covariates prevent an exact marginal guarantee. This is algebra from source summaries, not a generator execution or fitted source result.')
        par('positive_mean',{'floor':15.,'width':8.},[],['A_structure'],'Assumed smooth positive regularization floor+width*log(1+exp((linearMean-floor)/width)); avoids negative means at unsupported covariate extremes. It is not a TG truncation or observed lower bound.')
    elif sid=='s2':
        assumptions.append({'id':'A_structure','description':'s2 assumes additive effects on log TG, which are multiplicative on TG: a bounded tanh BMI response, a smooth female age transition, a slight linear male age effect, and sex-specific normal log residuals. This permits age-BMI interaction on the arithmetic scale and BMI saturation; it changes the functional scale and age shape relative to s1. Transition parameters are phenomenological, not inferred menopause status.'})
        medians=[reference['tg_mean'][i]/math.sqrt(1+(reference['tg_sd'][i]/reference['tg_mean'][i])**2) for i in range(2)]
        par('reference_median',medians,[f'E_oh_{sex}_tg_mg_dl_{kind}' for sex in ['male','female'] for kind in ['mean','sd']],['A_structure'],'Moment-equivalent lognormal marginal median m/sqrt(1+(sd/m)^2), used as a log-location anchor. This does not assert source TG is exactly lognormal or that a marginal median equals a conditional median.')
        par('log_bmi_slope',[6.813/141.6,6.813/97.2],['E_oh_bmi_age_sex_slope'],['A_structure'],'Local log-scale linearization beta/m at each sex-specific source mean; not a reported log slope. Saturation deliberately makes the global OLS coefficient a diagnostic rather than an identity.')
        par('bmi_saturation_width',10.,['E_oh_female_bmi_stratum_4_tg','E_oh_female_bmi_stratum_5_tg'],['A_oh_table2','A_structure'],'Assumed 10 kg/m^2 tanh width. Female highest BMI categories suggest a possible plateau but do not identify its location or establish saturation in men.')
        par('female_age',{'amplitude':.58,'midpoint':50.,'width':6.5,'source_center':.34},['E_oh_female_age_stratum_1_tg','E_oh_female_age_stratum_3_tg','E_oh_female_age_stratum_4_tg','E_oh_female_age_stratum_5_tg','E_bansal_spearman_age'],['A_oh_table2','A_structure'],'Assumed smooth transition suggested by female age strata: log amplitude .58, midpoint 50, width 6.5; .34 approximates its source-population average. Not a hormone measurement or causal menopause effect.')
        par('male_log_age_slope',-.0014,['E_oh_male_age_stratum_1_tg','E_oh_male_age_stratum_5_tg'],['A_oh_table2','A_structure'],'Small negative local log-age trend chosen from the qualitatively flatter male profile; no source says this is a conditional coefficient.')
        par('residual_log_sd',[.65,.49],[f'E_oh_{sex}_tg_mg_dl_{kind}' for sex in ['male','female'] for kind in ['mean','sd']]+['E_bansal_q25','E_bansal_q75'],['A_structure'],'Chosen below sex-specific total moment-equivalent log SDs to reserve dispersion for covariates; Bansal IQR implies total log spread about log(169/81)/(2*0.67449). These are fixed approximations, not SEs or source-fitted estimates.')
    else:
        assumptions.append({'id':'A_structure','description':'s3 assumes an unobserved two-state metabolic mixture. Age/BMI change logistic state membership, while each sex/state has a gamma TG distribution with fixed component mean and CV. Conditional mean, variance and tail probability thus change together and saturate with state probability. Components do not identify actual diagnoses, medication, or latent people; this discrete heterogeneity is an assumption compatible in principle with skewed TG and metabolic clustering, not demonstrated by the papers.'})
        means=[[100.,280.],[75.,200.]]
        cvs=[[.4,.5],[.3,.4]]
        state_intercept=[]; state_bmi=[]; state_age=[]
        for i in range(2):
            low,high=means[i]
            prob=(reference['tg_mean'][i]-low)/(high-low)
            grad=(high-low)*prob*(1-prob)
            b=6.813/grad
            a=[-.2,1.6][i]/grad
            v=(b*reference['bmi_sd'][i])**2+(a*reference['age_sd'][i])**2
            state_intercept.append(math.log(prob/(1-prob))*math.sqrt(1+math.pi*v/8))
            state_bmi.append(b);state_age.append(a)
        par('component_mean',means,[f'E_oh_{sex}_tg_mg_dl_mean' for sex in ['male','female']]+['E_bansal_q25','E_bansal_q75'],['A_structure'],'Assumed sex-specific low/elevated component means in mg/dL, chosen to straddle published distributions without assigning participants to observed disease classes.')
        par('component_cv',cvs,[f'E_oh_{sex}_tg_mg_dl_sd' for sex in ['male','female']],['A_structure'],'Assumed gamma component CVs. Total dispersion also includes mixture separation and changing state composition; component CVs are not published subgroup SDs.')
        par('state_bmi_slope',state_bmi,['E_oh_bmi_age_sex_slope'],['A_structure'],'Local probability-link linearization 6.813/[(high-low)*p0*(1-p0)], p0=(reportedMean-low)/(high-low); actual marginal OLS after mixing and covariates need not equal this local derivative.')
        par('state_age_slope',state_age,['E_oh_male_age_stratum_1_tg','E_oh_male_age_stratum_5_tg','E_oh_female_age_stratum_1_tg','E_oh_female_age_stratum_5_tg'],['A_oh_table2','A_structure'],'Analogous local derivatives for assumed arithmetic age trends -.2/1.6 mg/dL/year. Logistic saturation yields nonlinear age/BMI response and interactions.')
        par('state_intercept',state_intercept,[f'E_oh_{sex}_tg_mg_dl_mean' for sex in ['male','female']],['A_oh_context','A_structure'],'Analytic logistic-normal approximation: logit(p0)*sqrt(1+pi*v/8), with v=bBMI^2 Var(BMI)+bAge^2 Var(age). This approximate intercept adjustment reserves source covariate heterogeneity. No generator or replay was run to choose it.')
    return dict(parameters=params,assumptions=assumptions,parameter_provenance=prov)


def main():
    for sid in ['s1','s2','s3']:
        if (P/'candidates'/f'{sid}_initial').exists():
            raise RuntimeError('Initial candidate already exists; construction is one-time and will not overwrite it')
    oh,bansal,context_detail=contexts()
    shared=P/'shared_source_definition'
    shared.mkdir(exist_ok=False)
    oh.to_csv(shared/'oh.csv',index=False,float_format='%.6f',lineterminator='\n')
    bansal.to_csv(shared/'bansal.csv',index=False,float_format='%.6f',lineterminator='\n')
    write(shared/'ctx.json',context_detail)
    write(shared/'evidence.json',EVIDENCE)
    write(shared/'sa.json',SHARED_ASSUMPTIONS)
    recipe={'schema_version':1,'contexts':[
        dict(id='oh',population=EVIDENCE['sources'][0]['population'],reason='Use sex-specific published marginal age/BMI summaries and stratum frequencies; assess all feasible TG moment, category and reduced-slope evidence on one common approximate population.',assumption_ids=['A_shared_source_interpretation','A_oh_context','A_source_measurement','A_monte_carlo'],measurement={'mode':'identity','description':'legacy_proxy output is source mg/dL; Oh assay equivalence is explicitly assumed, especially because glycerol blanking is unreported.'},input={'path':'source_contexts/oh.csv','sha256':digest(shared/'oh.csv'),'origin':'declared_source_covariates'},checks=OH_CHECKS),
        dict(id='bansal',population=EVIDENCE['sources'][1]['population'],reason='Use fasting female marginal age/BMI summaries, without fabricating their unreported joint association or assigning TG tertiles to inputs. Check marginal TG and reverse-conditional covariate summaries together.',assumption_ids=['A_shared_source_interpretation','A_bansal_context','A_source_measurement','A_monte_carlo'],measurement={'mode':'identity','description':'legacy_proxy output is source mg/dL; endogenous glycerol correction supports but does not prove equivalence to old target method.'},input={'path':'source_contexts/bansal.csv','sha256':digest(shared/'bansal.csv'),'origin':'declared_source_covariates'},checks=BANSAL_CHECKS),
    ]}
    write(shared/'source_replay.json',recipe)
    unavailable={'schema_version':1,'checks':[dict(id=eid.lower(),evidence_id=eid,status='not_computable',table=None,operator=None,assumption_ids=[aid],reason=reason) for eid,aid,reason in UNREPLAYED]}
    write(shared/'source_checks.json',unavailable)
    plan={
        'schema_version':1,'created_by':'scientific_generation_agent','state':'initial construction; no generator or source replay executed by builder',
        'source_seed_schedule':[76101,76102,76103],'target_draw_schedule':[76201,76202,76203,76204,76205],
        'feedback_schedule':'Controller freezes all three initial candidates before any source replay; returns complete source-only feedback for all structures together; at most one parent-linked revise/retain per structure. All final structures are evaluated; no source-score winner selection.',
        'shared_definition':{'evidence_sha256':digest(shared/'evidence.json'),'source_replay_sha256':digest(shared/'source_replay.json'),'source_assumptions_sha256':digest(shared/'sa.json'),'source_context_sha256':{'oh':digest(shared/'oh.csv'),'bansal':digest(shared/'bansal.csv')},'oh_rows':len(oh),'bansal_rows':len(bansal),'oh_checks':len(OH_CHECKS),'bansal_checks':len(BANSAL_CHECKS),'unreplayed_statistics':len(UNREPLAYED)},
        'families':[
            {'id':'s1','name':'Additive conditional arithmetic mean with lognormal individual noise','scientific_difference':'One raw-scale BMI slope and sex-specific linear age slopes; constant residual CV. Effects add in arithmetic mean, so BMI slope remains constant away from positive regularization.','source_compatible_in_principle':'Oh reduced slope and sex-specific moments directly anchor the local mean and residual variance. Female age increase and positive skew can accommodate the Bansal location/rank summaries without treating their marginal correlations as conditional coefficients.','assumption_limits':'Linear age response, no raw-mean interaction, distribution transport and independent source covariates are not identified by the sources. Positive floor affects unsupported low-mean combinations.','planned_diagnostic_tradeoffs':'Raw-scale OLS may agree while TG quantile asymmetry, rare tails or female age-TG rank correlation and tertile ages disagree; increasing CV changes both tail mass and rank associations.'},
            {'id':'s2','name':'Saturating multiplicative log-location model with smooth female age transition','scientific_difference':'BMI enters a bounded nonlinear function of log TG; female age enters a sigmoid. Arithmetic-scale BMI effects depend on age/sex and saturate at high BMI.','source_compatible_in_principle':'Positive skew, Table 2 qualitative female age transition and high-BMI flattening, plus Bansal fasting quantiles motivate this alternative. Source moment-equivalent medians and approximate local slope anchor it.','assumption_limits':'The plateau width and age transition are unreported; they are not measured menopausal state. One lognormal family may miss observed extreme tail/category counts. Marginal-to-conditional centering is approximate.','planned_diagnostic_tradeoffs':'May better represent age curvature and TG quantiles while changing raw-scale BMI OLS, sex-specific SDs and high-BMI extrapolation. Same source diagnostics expose these tradeoffs without selecting endpoints.'},
            {'id':'s3','name':'Latent elevated-TG state mixture with gamma components','scientific_difference':'Age/BMI alter state membership instead of a single continuous TG location; conditional dispersion and tails change with mixture composition, and mean response saturates.','source_compatible_in_principle':'Source TG spread, skew and metabolic clustering permit latent heterogeneity; two gamma states can represent low and elevated ranges while using the same moment and local-slope anchors. This is compatibility in principle only, not evidence that two biological classes exist.','assumption_limits':'State prevalence/components are not identified by aggregate source statistics. State is not a diagnosis. Analytic logistic-normal centering is approximate and can leave mean/slope discrepancies.','planned_diagnostic_tradeoffs':'Could reproduce moderate/high category fractions while distorting median/IQR, rare extreme tail or age/BMI distributions inside TG tertiles. Rank relationships may differ even with similar marginal moments.'},
        ],
        'uncertainty':'Fixed-source, fixed-covariate, fixed-parameter scenarios do not give calibrated probabilities over scientific structures. Missing source joint distributions remain unknown. Source numerical agreement will not establish target validity or causal or individual recovery claims.'
    }
    write(P/'STRUCTURE_PLAN.json',plan)
    evidence_ids=validate_evidence(EVIDENCE,TASK)
    for sid,program in [('s1',GENERATOR_S1),('s2',GENERATOR_S2),('s3',GENERATOR_S3)]:
        directory=P/'candidates'/f'{sid}_initial'
        directory.mkdir(parents=True)
        (directory/'source_contexts').mkdir()
        for name in ['evidence.json','source_replay.json','source_checks.json','sa.json','ctx.json']:
            shutil.copyfile(shared/name,directory/name)
        for name in ['oh','bansal']:
            shutil.copyfile(shared/(name+'.csv'),directory/'source_contexts'/(name+'.csv'))
        spec=make_spec(sid)
        validate_spec(spec,evidence_ids)
        write(directory/'model_spec.json',spec)
        (directory/'generator.py').write_text(program,encoding='utf-8')
        validate_program(directory/'generator.py')
        syntax=ast.parse(program)
        imports=[node.module for node in ast.walk(syntax) if isinstance(node,ast.ImportFrom)]+[alias.name for node in ast.walk(syntax) if isinstance(node,ast.Import) for alias in node.names]
        assert imports==['numpy']
        assert not any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'open','eval','exec','compile','__import__'} for node in ast.walk(syntax))
        assert 'record_id' not in program
        for context in recipe['contexts']:
            _input_task(directory,context,TASK,20_000_000)
            for check in context['checks']:
                _check_metadata(check,{e['id']:e for e in EVIDENCE['items']},{a['id'] for a in spec['assumptions']},context['assumption_ids'])
        report={'scope':'static_source_only','generator_executed':False,'source_replay_executed':False,'candidate':f'{sid}_initial','checks':['Evidence/specification contracts','Generator AST and three-positional-argument ABI','Only numpy imported; no file/network entry points and no ID-dependent biological calculation in submitted AST','Source covariate-only column order/types/unique IDs and hashes','Source replay operator/evidence kind/unit/assumption references','Same shared source bytes across initial structures by construction'],'limits':'Static checks do not verify runtime behavior, observed-value preservation at execution, source numerical agreement or target validity. No generator was imported or called.'}
        write(directory/'static.json',report)
        write(directory/'checks.json',{'scope':'source_only','records':[{'name':'static_contract_and_boundary','status':'pass','detail':'See bound static.json. No generator execution occurred.'},{'name':'source_numerical_compatibility','status':'not_computable','detail':'Awaiting the controller fixed-seed source replay after all initial candidates are frozen; no numeric agreement claim.'},{'name':'target_validation','status':'not_computable','detail':'Target outcomes/evaluation unavailable to builder and never accessed.'}],'artifacts':[{'path':'static.json','sha256':digest(directory/'static.json')},{'path':'ctx.json','sha256':digest(directory/'ctx.json')}]})
        family=next(f for f in plan['families'] if f['id']==sid)
        decision=f'''# {sid}: initial scientific decision

{family['name']}. {family['scientific_difference']}

{family['source_compatible_in_principle']} This is a rationale for proposing the structure, not a numerical compatibility finding. No generator has been executed by this builder.

The evidence and source replay recipe are identical across all three candidates. Oh Table 1 values are arithmetic marginal means and individual SDs; Table 3 is the age/sex-adjusted BMI slope. Table 4, mixed-model Table 5 (SE, not SD), and co-twin Table 6 are different estimands and remain unreplayed. Table 2 summary type is ambiguous and remains reported_other. Bansal fasting evidence includes original quantiles (convention unreported), actual cumulative category fractions, marginal Spearman correlations and covariate means/SDs conditional on generated TG groups. None is silently substituted for a conditional TG regression coefficient.

Source reconstruction uses only published covariate marginals and explicit independence/shape assumptions. It never supplies an outcome or a source TG tertile assignment to a row. All source-context and check assumption descriptions are fixed; shared source/measurement caveats are in sa.json. The legacy_proxy mapping is particularly uncertain for Oh because glycerol blanking is unspecified. The target assay equation is task-provided technical context and is applied after biological generation.

Limits: {family['assumption_limits']} {family['planned_diagnostic_tradeoffs']} Published uncertainty is retained in evidence but is not treated as calibrated parameter uncertainty. The seed varies individual draws only.

Stopping rule: freeze this initial candidate together with the other two, then await all three controller source-only portfolios at seeds 76101, 76102, 76103. At most one retain/revise decision per structure follows; all final structures remain in the evaluation schedule. Source discrepancies are reported, not automatically optimized away, and no model is selected from target feedback. Static tests have passed as recorded in checks.json; they do not establish runtime or scientific correctness.
'''
        (directory/'decision.md').write_text(decision,encoding='utf-8')
    print(json.dumps({'created':['s1_initial','s2_initial','s3_initial'],'source_rows':{'oh':len(oh),'bansal':len(bansal)},'replay_checks':len(OH_CHECKS)+len(BANSAL_CHECKS),'unreplayed':len(UNREPLAYED),'generator_executed':False}))


if __name__=='__main__':
    main()

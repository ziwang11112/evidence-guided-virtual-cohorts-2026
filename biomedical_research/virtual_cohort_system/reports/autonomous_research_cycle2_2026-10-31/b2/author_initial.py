"""Author static candidate artifacts only. Never import or call generator.py."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import math

B = Path(__file__).resolve().parent
C = B / 'candidates' / 'initial'
C.mkdir(parents=True, exist_ok=True)
if (C / 'freeze.json').exists():
    raise RuntimeError('Initial candidate is frozen; authoring cannot overwrite it.')

def read(name):
    return json.loads((B / name).read_text(encoding='utf-8-sig'))

def write(name, obj):
    p = C / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

task = read('task.json')
panel = read('SOURCE_PANEL_SPEC.json')
ev = read('evidence_template.json')
items = {x['id']: x for x in ev['items']}
value = lambda name: items[name]['estimate']

assumptions = [
 ('A_DOMAIN', 'The computational domain is integer age 18-95, female coded 0/1, positive BMI and HbA1c, and positive fasting glucose strictly below 126 mg/dL. Age support is an author-imposed finite approximation, not an inferred source inclusion criterion. All values describe already-selected eligible individuals; no records of excluded people are generated.'),
 ('A_TARGET_ALLOCATION', 'The target has the required 250 people in each age-band by sex cell. Ages are uniform integers within each prescribed band, independently of subsequent residuals. Equal allocation and within-band uniformity are analytical design choices, not Mexican population frequencies.'),
 ('A_LIFELINES_POPULATION', 'Reconstruct the admitted Lifelines eligible Western-European GWAS source with independent sex Bernoulli(0.597) and rounded normal age with mean 55.5 and SD 9.9, rejecting ages outside 18-95. Actual source age limits and age-sex dependence are unknown. The finite support is assumed, includes ages outside target bounds, and may omit older people; oldest-family-member selection is represented only through the published age moments. Reported n=2921 is not the Monte Carlo size.'),
 ('A_PANI_POPULATION', 'Reconstruct Pani NHANES 2001-2004 adults age>=25 without reported diabetes and FPG<126. Approximate age-band probabilities by the published unweighted counts [1037,330,322,261,198,283,198,641]/3270, not survey population weights. Ages are uniform integers below 70. In the open-ended >=70 band assume age=70+geometric(p=0.15)-1, rejecting ages above 95; 95 is an explicit computational cap, not the published upper age. Sex is independent Bernoulli(0.5), an assumption without source calibration. No Pani FOS data are pooled.'),
 ('A_COVARIATE_SHAPE', 'BMI and glucose have a shared conditional bivariate normal residual law. Conditional means change by +0.04 kg/m^2 BMI and +0.12 mg/dL glucose per year and by +0.5 kg/m^2 BMI and -1.0 mg/dL glucose for female=1. These dependence coefficients are author assumptions, not published estimates. Reference means and total SDs are from Lifelines. Positive BMI and 0<glucose<126 are enforced by joint residual rejection conditional on age and sex; this slightly perturbs untruncated moments and projections.'),
 ('A_JOINT_PROJECTION', 'Set BMI-glucose residual correlation after age and sex to 0.30, which is unidentified by the admitted evidence. Derive two simultaneous HbA1c coefficients from the two separate Jansen Table 2 age/sex-adjusted projections using the declared residual covariance matrix. This is a conditional Gaussian algebraic identification assumption, not concatenation of published coefficients or a causal identification result. Other correlations would yield different structural coefficients.'),
 ('A_SHARED_AGE_SEX', 'Use Pani NHANES adjusted age coefficient 0.010 percentage points/year as a shared conditional linear age term across all contexts. Set the direct conditional female term to zero as an unidentifiable working assumption; this does not infer Jansen sex coding or claim no biological sex association. Age-sex interactions and nonlinear conditional age effects are omitted. Pani older marginal means suggest that linearity may be inadequate.'),
 ('A_HBA_RESIDUAL', 'Assume independent homoscedastic normal HbA1c residuals. Derive variance as published Lifelines HbA1c SD^2 minus model-implied explained variance in the untruncated reference population, using the stated covariance and age/sex assumptions. Positive HbA1c is enforced by residual rejection. The resulting residual variation is individual stochastic variation, not uncertainty in regression coefficients, mean estimates, or transport.'),
 ('A_LEVEL_LINKAGE', 'A context may differ in one HbA1c reference level while all conditional slopes and residual laws are shared. Lifelines uses its published HbA1c mean 5.6 at the published reference age 55.5 and female fraction 0.597. Pani uses its 50-54 age-band mean 5.40 at assumed mean age 52 and female fraction 0.5. The latter anchor interprets the published weighted stratum mean under assumed within-band covariates. No other Pani age-band mean is used to repair the curve.'),
 ('A_TARGET_TRANSPORT', 'Target covariate mechanisms, residual covariance, residual HbA1c variation and conditional slopes are transported without Mexican recalibration from the shared source rule. The target takes exactly the Pani reference HbA1c level (5.40 at age 52), because a nondiabetic multi-ancestry US source is the chosen level anchor; geographical/ancestry similarity is not established. Lifelines supplies otherwise missing covariate dispersion. This hybrid transport is a scenario, not an estimated Mexican distribution. No target values or target-only scientific repair are used.'),
 ('A_SELECTION_MEASUREMENT', 'Selection on no reported diagnosis, valid measurements and fasting glucose is treated as already conditioned in the source summaries. The target serum assay is assumed numerically comparable to source plasma at fixed units, with no learned conversion; actual serum/plasma, fasting-duration, assay, ancestry, GWAS selection, pregnancy/lactation, standing-route and missingness differences are unresolved. Lifelines excluded significant anemia whereas the target has no verified anemia exclusion. No measured medication exclusion or unknown older-woman pregnancy/lactation status is invented. Unmeasured anemia/erythrocyte and medication effects are absorbed into a transported residual law, an unverified simplification.'),
 ('A_SOURCE_ESTIMATOR', 'All source checks use unweighted 6000-row Monte Carlo statistics on an assumed source reconstruction. Pani complex survey weights/design and Table2 complete analysis detail are not reconstructed. Checks are approximate projection diagnostics, not original-estimator replication. Published Table1 SEs are retained as evidence uncertainty and never converted to individual SDs. Jansen Table2 printed interval levels remain unknown.'),
 ('A_UNCERTAINTY', 'One fixed parameter scenario is committed. Published rounding, unspecified Jansen interval confidence levels, Pani survey SEs, residual covariance, age support, nonlinear effects, assay and population transport remain evidence/model uncertainty; no probability distribution for that uncertainty is identified. Controller seeds change individuals only. Source agreement cannot validate Mexican target analyses or causal effects.'),
 ('A_IMPLEMENTATION', 'All five scientific variables are generated from the active aggregate context using the controller-supplied seed. Fictional identifiers encode context, seed and row number only. Rejection sampling rather than boundary clipping enforces positivity/glucose eligibility. No empirical moments are imposed on a realized draw, no fitted sample coefficients are computed, and no external data are read by the generator.')
]

reference = {
 'age_mean': value('J_T1_age_mean_task'), 'age_sd': value('J_T1_age_sd_task'),
 'female_probability': value('J_T1_female_proportion_derived'),
 'bmi_mean': value('J_T1_bmi_mean_task'), 'bmi_sd': value('J_T1_bmi_sd_task'),
 'glucose_mean': value('J_T1_glucose_mean_mg_dL_derived'), 'glucose_sd': value('J_T1_glucose_sd_mg_dL_derived'),
 'hba1c_mean': value('J_T1_hba1c_mean_pct'), 'hba1c_sd': value('J_T1_hba1c_sd_pct')
}
dependence = {'bmi_per_year': 0.04, 'bmi_female_shift': 0.5,
              'glucose_per_year': 0.12, 'glucose_female_shift': -1.0,
              'bmi_glucose_residual_correlation': 0.30}
hba_rule = {
 'bmi_projection_age_sex_adjusted': value('J_T2_bmi_slope_task_derived'),
 'glucose_projection_age_sex_adjusted': value('J_T2_glucose_slope_task_derived'),
 'conditional_age_per_year': value('P_NHANES_age_slope'),
 'conditional_female_shift': 0.0,
 'coefficient_rule': 'solve the two distinct projection equations under the common assumed residual covariance',
 'residual_rule': 'positive square root of reference HbA1c variance minus common model explained variance',
 'residual_distribution': 'independent normal, reject HbA1c<=0'
}
contexts = {}
contexts['target'] = {k: copy.deepcopy(task[k]) for k in ['population', 'n_rows', 'columns']}
contexts['target']['inputs'] = {
 'age_distribution': {'kind': 'balanced_age_sex', 'bands': [[25,39],[40,54],[55,69],[70,79]], 'per_sex_per_band': 250},
 'female_probability': 0.5,
 'hba1c_anchor': {'age': 52.0, 'female_probability': 0.5, 'mean': 5.40}
}
for sid in ['lifelines','pani']:
    descriptor = next(c for c in panel['contexts'] if c['id'] == sid)
    columns = copy.deepcopy(task['columns'])
    columns[1]['minimum'] = 18 if sid == 'lifelines' else 25
    columns[1]['maximum'] = 95
    if sid == 'lifelines':
        pop = descriptor['published_population'] + ' Monte Carlo reconstruction: assumed rounded normal age on 18-95 and independent female probability 0.597; 6000 fictional rows, not source IPD.'
        inputs = {'age_distribution': {'kind':'rounded_normal','mean':55.5,'sd':9.9,'minimum':18,'maximum':95},
                  'female_probability':0.597, 'hba1c_anchor': {'age':55.5,'female_probability':0.597,'mean':5.6}}
    else:
        pop = descriptor['published_population'] + ' Monte Carlo reconstruction: assumed age support 25-95, published unweighted age-band count proportions used as approximate mixture probabilities, truncated geometric age tail >=70, and independent female probability 0.5; unweighted calculations are not the complex survey estimator; 6000 fictional rows, not source IPD.'
        inputs = {'age_distribution': {'kind':'age_band_mixture', 'bands':[[25,39],[40,44],[45,49],[50,54],[55,59],[60,64],[65,69],[70,95]],
                                      'unweighted_counts':[1037,330,322,261,198,283,198,641], 'last_band_geometric_probability':0.15},
                  'female_probability':0.5, 'hba1c_anchor': {'age':52.0,'female_probability':0.5,'mean':5.4}}
    contexts[sid] = {'population':pop,'n_rows':6000,'columns':columns,'inputs':inputs}

parameters = {'active_context':'target','contexts':contexts,'reference_moments':reference,
              'covariate_dependence':dependence,'hba1c_rule':hba_rule,
              'simulation':{'maximum_rejection_rounds':10000}}
prov = {
 'active_context': {'evidence_ids':[], 'assumption_ids':['A_IMPLEMENTATION'], 'derivation':'Only this selector changes across controller-created child specifications.'},
 'contexts': {'evidence_ids':['J_T1_age_mean_task','J_T1_age_sd_task','J_T1_female_proportion_derived','J_T1_hba1c_mean_pct','P_NHANES_hba1c_age_50_54_mean'],
              'assumption_ids':['A_DOMAIN','A_TARGET_ALLOCATION','A_LIFELINES_POPULATION','A_PANI_POPULATION','A_LEVEL_LINKAGE','A_TARGET_TRANSPORT','A_SELECTION_MEASUREMENT'],
              'derivation':'Target population/schema/count are copied from task. Source descriptions preserve published selection. Lifelines age and sex use Table1. Pani age-band counts are original Table1 counts in normalized_quantities.json; their use as mixture weights, within-band shapes, sex probability and age-52 anchor are assumptions. Pani>=70 extends to95. Target uses the same Pani anchor without target-derived repair.'},
 'reference_moments': {'evidence_ids':['J_T1_age_mean_task','J_T1_age_sd_task','J_T1_female_proportion_derived','J_T1_bmi_mean_task','J_T1_bmi_sd_task','J_T1_glucose_mean_mg_dL_derived','J_T1_glucose_sd_mg_dL_derived','J_T1_hba1c_mean_pct','J_T1_hba1c_sd_pct'],
                       'assumption_ids':['A_LIFELINES_POPULATION','A_COVARIATE_SHAPE','A_HBA_RESIDUAL','A_TARGET_TRANSPORT'],
                       'derivation':'Published Table1 marginal means/SDs and rounded female complement; glucose uses fixed18.0 conversion. Use published percent HbA1c5.6/0.3, not alternate rounded IFCC representation. Treat as nominal untruncated population moments for variance algebra, subject to small sampling/truncation differences.'},
 'covariate_dependence': {'evidence_ids':[], 'assumption_ids':['A_COVARIATE_SHAPE','A_JOINT_PROJECTION'],
                          'derivation':'Age/sex effects and residual correlation0.30 are explicit scientifically unidentified choices. They are neither extracted coefficients nor consequences of absent evidence.'},
 'hba1c_rule': {'evidence_ids':['J_T2_bmi_slope_task_derived','J_T2_glucose_slope_task_derived','P_NHANES_age_slope','J_T1_hba1c_sd_pct'],
                'assumption_ids':['A_JOINT_PROJECTION','A_SHARED_AGE_SEX','A_HBA_RESIDUAL','A_LEVEL_LINKAGE','A_TARGET_TRANSPORT'],
                'derivation':'For conditional residual variances vB,vG and covariance c, betaB=(pB-pG*c/vB)/(1-c*c/(vB*vG)), betaG=(pG-pB*c/vG)/(1-c*c/(vB*vG)). These satisfy two separate age/sex-adjusted projections in the assumed untruncated joint distribution. Add the separately transported Pani conditional age coefficient and assumed zero direct sex coefficient; determine independent HbA1c residual variance by reference variance decomposition.'},
 'simulation': {'evidence_ids':[], 'assumption_ids':['A_IMPLEMENTATION'], 'derivation':'A technical cap prevents unbounded rejection loops; it is not a biological parameter or a data-dependent tuning rule.'}
}
write('model_spec.json', {'parameters':parameters,'assumptions':[{'id':a,'description':d} for a,d in assumptions], 'parameter_provenance':prov})
(C/'evidence.json').write_bytes((B/'evidence_template.json').read_bytes())
(C/'fixed_source_panel.json').write_bytes((B/'SOURCE_PANEL_SPEC.json').read_bytes())

generator = '''"""Shared aggregate-evidence joint model; the controller alone executes generate."""
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = specification["parameters"]
    active = p["active_context"]
    context = p["contexts"][active]
    inp = context["inputs"]
    n = context["n_rows"]
    rng = np.random.default_rng(seed)
    maximum_rounds = p["simulation"]["maximum_rejection_rounds"]
    age_law = inp["age_distribution"]
    if age_law["kind"] == "balanced_age_sex":
        ages, sexes = [], []
        for lo, hi in age_law["bands"]:
            for sex in (0, 1):
                m = age_law["per_sex_per_band"]
                ages.append(rng.integers(lo, hi + 1, size=m))
                sexes.append(np.full(m, sex, dtype=np.int64))
        age = np.concatenate(ages)
        female = np.concatenate(sexes)
        if len(age) != n:
            raise ValueError("Balanced design and declared row count disagree")
        permutation = rng.permutation(n)
        age, female = age[permutation], female[permutation]
    else:
        female = rng.binomial(1, inp["female_probability"], n)
        if age_law["kind"] == "rounded_normal":
            age = np.empty(n, dtype=np.int64)
            remaining = np.arange(n)
            for _ in range(maximum_rounds):
                draws = np.rint(rng.normal(age_law["mean"], age_law["sd"], len(remaining))).astype(np.int64)
                accepted = (draws >= age_law["minimum"]) & (draws <= age_law["maximum"])
                age[remaining[accepted]] = draws[accepted]
                remaining = remaining[~accepted]
                if len(remaining) == 0:
                    break
            if len(remaining):
                raise RuntimeError("Age rejection cap exceeded")
        elif age_law["kind"] == "age_band_mixture":
            weights = np.asarray(age_law["unweighted_counts"], dtype=float)
            bands = age_law["bands"]
            labels = rng.choice(len(bands), n, p=weights / weights.sum())
            age = np.empty(n, dtype=np.int64)
            for j, (lo, hi) in enumerate(bands):
                remaining = np.flatnonzero(labels == j)
                if j != len(bands) - 1:
                    age[remaining] = rng.integers(lo, hi + 1, len(remaining))
                else:
                    for _ in range(maximum_rounds):
                        draws = lo + rng.geometric(age_law["last_band_geometric_probability"], len(remaining)) - 1
                        accepted = draws <= hi
                        age[remaining[accepted]] = draws[accepted]
                        remaining = remaining[~accepted]
                        if len(remaining) == 0:
                            break
                    if len(remaining):
                        raise RuntimeError("Open age-band rejection cap exceeded")
        else:
            raise ValueError("Unknown aggregate age distribution")

    ref, dep, rule = p["reference_moments"], p["covariate_dependence"], p["hba1c_rule"]
    age_variance = ref["age_sd"] ** 2
    sex_variance = ref["female_probability"] * (1 - ref["female_probability"])
    da, df = dep["bmi_per_year"], dep["bmi_female_shift"]
    ga, gf = dep["glucose_per_year"], dep["glucose_female_shift"]
    vb = ref["bmi_sd"] ** 2 - da ** 2 * age_variance - df ** 2 * sex_variance
    vg = ref["glucose_sd"] ** 2 - ga ** 2 * age_variance - gf ** 2 * sex_variance
    rho = dep["bmi_glucose_residual_correlation"]
    if vb <= 0 or vg <= 0 or abs(rho) >= 1:
        raise ValueError("Invalid reference conditional covariance")
    sb, sg = np.sqrt(vb), np.sqrt(vg)
    cov = rho * sb * sg
    pb, pg = rule["bmi_projection_age_sex_adjusted"], rule["glucose_projection_age_sex_adjusted"]
    beta_b = (pb - pg * cov / vb) / (1 - rho ** 2)
    beta_g = (pg - pb * cov / vg) / (1 - rho ** 2)
    beta_a, beta_f = rule["conditional_age_per_year"], rule["conditional_female_shift"]
    total_age = beta_a + beta_b * da + beta_g * ga
    total_sex = beta_f + beta_b * df + beta_g * gf
    explained = (total_age ** 2 * age_variance + total_sex ** 2 * sex_variance
                 + beta_b ** 2 * vb + beta_g ** 2 * vg + 2 * beta_b * beta_g * cov)
    residual_variance = ref["hba1c_sd"] ** 2 - explained
    if residual_variance <= 0:
        raise ValueError("Reference variance decomposition is not positive")
    mean_b = ref["bmi_mean"] + da * (age - ref["age_mean"]) + df * (female - ref["female_probability"])
    mean_g = ref["glucose_mean"] + ga * (age - ref["age_mean"]) + gf * (female - ref["female_probability"])
    bmi, glucose = np.empty(n), np.empty(n)
    remaining = np.arange(n)
    glucose_max = next(c["maximum"] for c in context["columns"] if c["name"] == "glucose")
    for _ in range(maximum_rounds):
        z_b, z_g = rng.normal(size=(2, len(remaining)))
        b = mean_b[remaining] + sb * z_b
        g = mean_g[remaining] + sg * (rho * z_b + np.sqrt(1 - rho ** 2) * z_g)
        accepted = (b > 0) & (g > 0) & (g <= glucose_max)
        bmi[remaining[accepted]], glucose[remaining[accepted]] = b[accepted], g[accepted]
        remaining = remaining[~accepted]
        if len(remaining) == 0:
            break
    if len(remaining):
        raise RuntimeError("Biomarker eligibility rejection cap exceeded")

    anchor = inp["hba1c_anchor"]
    anchor_b = ref["bmi_mean"] + da * (anchor["age"] - ref["age_mean"]) + df * (anchor["female_probability"] - ref["female_probability"])
    anchor_g = ref["glucose_mean"] + ga * (anchor["age"] - ref["age_mean"]) + gf * (anchor["female_probability"] - ref["female_probability"])
    mean_h = (anchor["mean"] + beta_a * (age - anchor["age"])
              + beta_f * (female - anchor["female_probability"])
              + beta_b * (bmi - anchor_b) + beta_g * (glucose - anchor_g))
    hba1c = np.empty(n)
    remaining = np.arange(n)
    for _ in range(maximum_rounds):
        h = mean_h[remaining] + rng.normal(0, np.sqrt(residual_variance), len(remaining))
        accepted = h > 0
        hba1c[remaining[accepted]] = h[accepted]
        remaining = remaining[~accepted]
        if len(remaining) == 0:
            break
    if len(remaining):
        raise RuntimeError("HbA1c positivity rejection cap exceeded")
    frame = pd.DataFrame({"row_id": [f"fictional_{active}_{seed}_{i+1:06d}" for i in range(n)],
                          "age": age, "female": female, "bmi": bmi, "glucose": glucose, "hba1c": hba1c})
    return frame[[c["name"] for c in context["columns"]]]
'''
(C/'generator.py').write_text(generator, encoding='utf-8')

domain_columns = copy.deepcopy(task['columns'])
domain_columns[1]['minimum'], domain_columns[1]['maximum'] = 18, 95
plan = {'schema_version':1, 'model_domain':{'columns':domain_columns, 'assumption_ids':['A_DOMAIN'],
       'description':'One shared joint model over declared integer age18-95; target25-79, Lifelines18-95, Pani25-95. The source upper/lower age bounds are explicit approximations; continuous biomarkers retain positive supports and selected glucose<126.'}, 'contexts':[]}
for context_panel in panel['contexts']:
    sid = context_panel['id']
    folder = 'source_contexts/' + sid
    child = copy.deepcopy(task)
    for k in ['population','n_rows','columns']:
        child[k] = contexts[sid][k]
    write(folder+'/task.json', child)
    source_assumptions = ['A_DOMAIN', 'A_LIFELINES_POPULATION' if sid=='lifelines' else 'A_PANI_POPULATION',
                         'A_COVARIATE_SHAPE','A_JOINT_PROJECTION','A_SHARED_AGE_SEX','A_HBA_RESIDUAL',
                         'A_LEVEL_LINKAGE','A_SELECTION_MEASUREMENT','A_SOURCE_ESTIMATOR','A_UNCERTAINTY']
    checks = []
    for ch in context_panel['checks']:
        reason = ('Uses the assumed source age/sex distribution and shared Gaussian conditional rule; nominal Lifelines moments/projections are population inputs, while finite sampling, integer ages and eligibility truncation can change realized statistics. Unknown source support, family selection and row-specific regression n remain unresolved.' if sid=='lifelines'
                  else 'Uses an unweighted assumed NHANES age-band mixture, independent assumed sex composition, transported Lifelines covariate dispersion and shared linear conditional rule. Original survey weights/PSU/strata are unavailable. Only the 50-54 mean anchors the Pani level; the other seven means diagnose linear age and transport assumptions, including the likely older-age plateau discrepancy. The >=70 reconstruction extends through95.')
        checks.append({'id':ch['id'],'evidence_id':ch['evidence_id'],'status':'approximate',
                       'operator':copy.deepcopy(ch['operator']),'assumption_ids':source_assumptions[1:], 'reason':reason})
    write(folder+'/whole_cohort_feedback.json', {'schema_version':1,'population':child['population'],
         'measurement':{'mode':'identity','description':'Generated age years, BMI kg/m^2, glucose mg/dL and HbA1c percent are passed unchanged to fixed operators. Published units are normalized in admitted evidence; identity here does not verify assay, plasma/serum or survey-estimator equivalence.'},
         'assumption_ids':source_assumptions,'checks':checks})
    plan['contexts'].append({'id':sid,'task_path':folder+'/task.json','feedback_path':folder+'/whole_cohort_feedback.json'})
write('source_context_plan.json',plan)

# Deterministic algebra on reported moments and declared assumptions, not simulations.
r, d, h = reference, dependence, hba_rule
vs = r['female_probability']*(1-r['female_probability'])
va = r['age_sd']**2
vb = r['bmi_sd']**2-d['bmi_per_year']**2*va-d['bmi_female_shift']**2*vs
vg = r['glucose_sd']**2-d['glucose_per_year']**2*va-d['glucose_female_shift']**2*vs
cv = d['bmi_glucose_residual_correlation']*math.sqrt(vb*vg)
bb = (h['bmi_projection_age_sex_adjusted']-h['glucose_projection_age_sex_adjusted']*cv/vb)/(1-d['bmi_glucose_residual_correlation']**2)
bg = (h['glucose_projection_age_sex_adjusted']-h['bmi_projection_age_sex_adjusted']*cv/vg)/(1-d['bmi_glucose_residual_correlation']**2)
ta = h['conditional_age_per_year']+bb*d['bmi_per_year']+bg*d['glucose_per_year']
tf = h['conditional_female_shift']+bb*d['bmi_female_shift']+bg*d['glucose_female_shift']
rv = r['hba1c_sd']**2-(ta**2*va+tf**2*vs+bb**2*vb+bg**2*vg+2*bb*bg*cv)
assert vb>0 and vg>0 and rv>0
algebra = {'kind':'deterministic_parameter_algebra_not_generated_data','bmi_residual_variance':vb,
           'glucose_residual_variance':vg,'bmi_glucose_residual_covariance':cv,
           'derived_conditional_bmi_coefficient':bb,'derived_conditional_glucose_coefficient':bg,
           'conditional_age_coefficient':h['conditional_age_per_year'],'hba1c_residual_sd':math.sqrt(rv),
           'implied_untruncated_bmi_projection':bb+bg*cv/vb,
           'implied_untruncated_glucose_projection':bg+bb*cv/vg,
           'implied_marginal_hba1c_age_slope_given_fixed_sex_mix':ta,
           'limitations':'Algebra assumes independent age and sex and an untruncated joint Gaussian residual structure. It is not execution, sample fitting or source feedback.'}
write('parameter_algebra.json',algebra)

(C/'transfer_linkage.md').write_text(f'''# Shared source-to-target rule

All contexts call one program with one model specification. Only active_context changes. Common parameters include conditional BMI/glucose age-sex effects, their residual covariance, the HbA1c conditional age/sex effects, the two algebraically derived simultaneous biomarker effects, and the residual HbA1c law. Contexts differ only in declared age/sex sampling and one source HbA1c level anchor. Target and Pani use the identical level anchor. No target-only fitted coefficient exists.

Jansen Table1 identifies nominal Lifelines marginal means and individual SDs, but not the joint distribution. With author-assumed age/sex effects and age-sex independence, residual BMI and glucose variances are the marginal variances minus explained age/sex variances. Residual correlation0.30 fixes the otherwise unidentified covariance. Jansen Table2 provides pB and pG from two different regressions. We solve pB=betaB+betaG*c/vB and pG=betaG+betaB*c/vG, obtaining betaB={bb:.10g} %/(kg/m^2) and betaG={bg:.10g} %/(mg/dL). These are derived model quantities conditional on assumptions, not reported multivariable coefficients. They are not causal effects.

Pani NHANES supplies the conditional age term0.010 %/year, which is transported to the common equation; the unreported direct sex term is set to0 as an explicit simplification. The common HbA1c residual SD is {math.sqrt(rv):.10g}%, obtained by decomposing Lifelines published variance0.3^2 under this cross-source equation and assumed covariance. It is not Pani SE multiplied by sqrt(n). Lifelines HbA1c uses mean5.6 at its age55.5/female0.597 reference. Pani uses Table1 mean5.40 for ages50-54, interpreting the assumed mean age as52 and sex fraction as0.5. All other Pani means are feedback diagnostics; their older-age plateau is not imposed as a hidden target curve.

The target adopts Pani's level anchor without a Mexico offset, shared conditional age term and shared source conditional biomarker/residual mechanisms. Its exact design quotas replace source demographic frequencies; uniform within-band target ages are an assumption. The target therefore has different overall biomarker means even when the common conditional rule is unchanged. This common rule is a hybrid evidence scenario, not an estimated Mexican cohort.

Lifelines uses an assumed18-95 rounded-normal support, not an asserted source age range. Pani uses published unweighted age-band counts only as approximate mixture probabilities, uniform ages in closed bands and a truncated geometric tail70-95. Survey weighting is not recreated. Neither source uses the target's balanced quotas. Unknown source age-sex dependence, anemia, medications, ancestry, fasting duration, assay and standing measurement selection are unresolved. Source plasma and target serum are assumed comparable in mg/dL; unit conversion alone does not establish that. HbA1c assay calibration is assumed to permit common percent units, but no equivalence validation is claimed.

Liu's univariate equation is retained only as context, and Jansen Table3 is quarantined. Pani/Liu NHANES overlap prevents independent-replication claims. Fixed source feedback assesses assumed source-population projections. It does not validate target transport, causal interpretation, disease prevalence or use in place of measurements. Model/evidence/transport uncertainty is not represented by repeated individual draws.
''', encoding='utf-8')

(C/'decision.md').write_text('''# Initial scientific decision

Commit one parsimonious joint Gaussian residual model conditioned on already eligible adults. The model synthesizes all five scientific columns and uses the exact target allocation. It combines source marginal information and separate projection constraints through explicit covariance assumptions. The shared conditional rule, source reconstruction and source-to-target linkage are detailed in model_spec.json and transfer_linkage.md; parameter_algebra.json contains deterministic parameter algebra only.

The main scientific choice is a positive residual BMI-glucose correlation of0.30, with mild assumed age and sex effects on these biomarkers. This makes Jansen's two separate adjusted projections informative about two conditional effects without treating them as one published multivariable equation. The author-chosen correlation and covariate slopes are not identified by the sources. Pani's adjusted age coefficient is shared, while its50-54 stratum mean fixes the non-Lifelines HbA1c location. No source SE is used as an individual SD. The printed Jansen interval bounds are retained without a confidence level; alternative unit representations count as one quantity.

The linear age rule is deliberately inspectable. Pani's older-age means flatten while a positive conditional linear age term and mildly increasing covariates imply a continuing marginal increase. This is a known scientific tension, not a concealed fit success. Fixed feedback will report all eight Pani means and the adjusted age term. The source summaries do not identify whether nonlinearity, survey covariate structure, selection, or transport explains the difference. Do not add arbitrary age-band corrections merely to force agreement.

All11 Lifelines and9 Pani checks are declared approximate and retain the exact fixed operators, including sample SD(ddof=1) and the original adjustment sets. They are computationally defined under stated source approximations. Before controller execution no numerical source check is computable; no source run or local simulation has occurred. Static source hashes, panel identity, candidate syntax and algebra are checked and bound in checks.json. Source supports include18-95 for Lifelines and25-95 for Pani; the latter does not truncate the>=70 band at79.

The target's Mexico population, serum measurement, no verified anemia/medication exclusion, pregnancy/lactation routing, 8-12-hour fast, and standing-route restrictions differ from the source contexts. No empirical adjustment for these differences is available. Transferring a US HbA1c level and Western-European covariate dispersion is explicitly provisional. Normality, homoscedasticity, direct sex neutrality, age linearity and residual dependence require scientific sensitivity assessment beyond this single initial scenario. Generated rows are fictional; additional seeds do not create evidence or clinical validity.

Stopping decision: freeze this initial model before any source execution, with no locally generated records and no target feedback. Await the single controller-verified source-only feedback opportunity. Source agreement, structural validation and a successful freeze are distinct outcomes.
''', encoding='utf-8')

# Static artifact checks only: no importlib, exec, generator call, random draws or tables.
syntax = ast.parse((C/'generator.py').read_text(encoding='utf-8'))
functions = [n for n in syntax.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
assert len(functions)==1 and functions[0].name=='generate' and isinstance(functions[0],ast.FunctionDef)
args = functions[0].args
assert len(args.args)+len(args.posonlyargs)==3 and args.vararg is None and args.kwarg is None and not args.kwonlyargs
assert (C/'evidence.json').read_bytes()==(B/'evidence_template.json').read_bytes()
registry = read('registry.json')
for source in ev['sources']:
    for artifact in source['artifacts']:
        assert digest(B/artifact['path'])==artifact['sha256']
        assert any(x['source_id']==source['id'] and x['path']==artifact['path'] and x['sha256']==artifact['sha256'] and x['screening']=='approved' for x in registry['artifacts'])
known = {a for a,_ in assumptions}
assert set(prov)==set(parameters)
for entry in prov.values():
    assert set(entry['assumption_ids'])<=known and set(entry['evidence_ids'])<=set(items)
ids=[]
for cp in panel['contexts']:
    recipe=json.loads((C/f"source_contexts/{cp['id']}/whole_cohort_feedback.json").read_text())
    assert len(recipe['checks'])==len(cp['checks'])
    for expected, actual in zip(cp['checks'],recipe['checks']):
        for field in ['id','evidence_id','operator']:
            assert expected[field]==actual[field]
        ids.append(actual['id'])
assert len(ids)==20 and len(set(ids))==20 and len(ev['items'])==32
aux = ['fixed_source_panel.json','source_context_plan.json','transfer_linkage.md','parameter_algebra.json']
for sid in ['lifelines','pani']:
    aux += [f'source_contexts/{sid}/task.json',f'source_contexts/{sid}/whole_cohort_feedback.json']
audit = {'kind':'static_authoring_audit','generator_executed':False,'generated_rows':0,
         'evidence_items':32,'fixed_checks':20,
         'checks':['Exact evidence-template byte identity','All four source artifact hashes match approved registry','One synchronous top-level generate with three positional parameters by AST only','Parameter provenance covers each top-level parameter and valid IDs','All20 panel IDs/evidence IDs/operators copied exactly','Positive conditional covariance and HbA1c residual variance by deterministic parameter algebra'],
         'input_hashes':{'task.json':digest(B/'task.json'),'evidence_template.json':digest(B/'evidence_template.json'),'SOURCE_PANEL_SPEC.json':digest(B/'SOURCE_PANEL_SPEC.json'),'registry.json':digest(B/'registry.json')},
         'candidate_hashes':{x:digest(C/x) for x in ['generator.py','model_spec.json','evidence.json']+aux},
         'scope':'Static schema/identity/parameter algebra only; no source result, target result or numerical sample validation.'}
write('static_audit.json',audit)
aux.append('static_audit.json')
write('checks.json',{'scope':'source_only','records':[
 {'name':'static_authoring_audit','status':'pass','detail':'Actual byte, registry, AST, provenance, fixed-panel and deterministic parameter-algebra checks are recorded in the bound static_audit.json. The submitted generator was never imported or called.'},
 {'name':'numerical_source_validation','status':'not_computable','detail':'No controller source execution has yet occurred. All20 approximate recipes are prospective; there are no generated tables, computed source statistics or numerical source-validation claims.'},
 {'name':'target_transport_validation','status':'not_computable','detail':'No target records or outcomes are supplied or inspected. Source feedback cannot resolve transport, residual covariance, nonlinear age effects or survey/assay differences.'}],
 'artifacts':[{'path':x,'sha256':digest(C/x)} for x in aux]})
print(json.dumps({'candidate':str(C),'source_check_count':20,'evidence_item_count':32,'local_generated_rows':0,'algebra':algebra},indent=2))

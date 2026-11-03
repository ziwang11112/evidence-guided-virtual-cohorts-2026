"""Read permitted summary feedback and retain model. No cohorts or generator import."""
import hashlib
import json
import math
import statistics
from pathlib import Path
from scipy.special import ndtri

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'mixture_initial01'
ROOT=HERE.parents[2]
INPUT=ROOT/'session/feedback/initial.json'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def write(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for file in OLD.iterdir():
    if file.is_file() and file.name!='freeze.json':
        (HERE/file.name).write_bytes(file.read_bytes())
(HERE/'initial_feedback.json').write_bytes(INPUT.read_bytes())
feedback=read(INPUT)
assert feedback['stage']=='initial'
assert [x['seed'] for x in feedback['runs']]==[4101,4102,4103]
maps=[]
for run in feedback['runs']:
    assert run['status']=='success'
    assert run['semantic_feedback_v1']['n_computable']==30
    assert run['semantic_feedback_v1']['output_link_verified']
    a=run['analysis_feedback']
    assert a['n']==3000
    maps.append({r['id']:r for r in a['analyses']+a['diagnostics']})
    assert len(maps[-1])==30

spec=read(HERE/'model_spec.json')['parameters']
ref=read(HERE.parent.parent/'input/reference_summary.json')
records=[]
for name in maps[0]:
    vals=[m[name]['value'] for m in maps]
    target=maps[0][name]['reference']
    if name in ['bmi_q10','bmi_median','bmi_q90']:
        q={'bmi_q10':.1,'bmi_median':.5,'bmi_q90':.9}[name]
        anchor=math.exp(spec['bmi_log_mean']+spec['bmi_log_sd']*float(ndtri(q)))
        interpretation='Known lognormal-family quantile approximation plus finite-cohort variation; retained, not mislabeled entirely as noise.'
    elif name=='female_sd':
        p=spec['female_probability'];anchor=math.sqrt(p*(1-p))
        interpretation='Binary dispersion follows prevalence; ddof=1 and finite-cohort prevalence fluctuations differ from population SD.'
    else:
        anchor=target
        interpretation='Working population functional anchored to disclosed sample estimate; finite-cohort discrepancy does not independently establish structural bias.'
    record={'id':name,'reference':target,'working_model_population':anchor,
            'structural_anchor_minus_reference':anchor-target,
            'seed_values':dict(zip(['4101','4102','4103'],vals)),
            'mean':statistics.mean(vals),'range':[min(vals),max(vals)],
            'sd_across_three_draws':statistics.stdev(vals),
            'mean_minus_reference':statistics.mean(vals)-target,
            'interpretation':interpretation}
    if name.endswith('_mean'):
        variable=name[:-5]
        sd=ref['diagnostics']['marginal'][variable]['sd']
        if variable=='female':sd=math.sqrt(spec['female_probability']*(1-spec['female_probability']))
        record['conditional_model_mean_sd_single_cohort']=sd/math.sqrt(3000)
        record['conditional_model_mean_sd_three_independent_cohort_average']=sd/math.sqrt(9000)
    records.append(record)

decision={
 'reason':'Retain the pre-feedback scientific law. All three isolated initial deliveries succeeded, all 30 diagnostics were reviewed, and the three coefficient/correlation means remain close to deterministic working population anchors. E2 varies in both directions around the anchor, consistent with finite-cohort tail sensitivity; the reference CR1 interval is not a synthetic-cohort predictive interval. BMI q90 has a known small lognormal-family discrepancy, which is reported rather than optimized away against three fixed seeds. No new evidence justifies changing the unidentified mixture/copula, sex or covariate assumptions, and no additional trial is needed for a no-op.',
 'kind':'retain',
 'addressed_findings':[
  'All 3 initial runs contain 3000 rows, all 30 statistics are computable and output-linked, and no nonpositive glycemia or duplicate measurement rows were reported.',
  'All 30 statistic values for seeds 4101/4102/4103 are recorded in initial_feedback_review.json with mean, range and descriptive three-draw SD. These are conditional synthetic draws, not independent clinical evidence.',
  'E1/E2/E3 mean differences from supplied reference are +0.000437619, -0.00515281 and -0.000160498. Both positive and negative differences occur across seeds, and deterministic model projections equal their working anchors.',
  'E2 ranges 0.358685 to 0.427418. Preserve this observed variability; do not tune a reference interval membership, p-value, favorable seed or realized slope.',
  'Pearson and Spearman mean differences are -0.00377472 and -0.00388626. Their distinct operators remain distinct; continuous-population rank approximation is still explicit.',
  'BMI q90 has working-population value 28.1768318 versus reference 28.1009570 (structural approximation +0.0758747 kg/m^2); three-draw mean discrepancy +0.128193 also includes conditional variation. BMI median population approximation is +0.0348397 kg/m^2. Retain these small family limitations instead of claiming all discrepancies are noise.',
  'Age q10/median/q90 are 39/53/68 in each initial draw; binary quantiles match. Female mean is above reference in two draws and slightly below in one; no independent evidence supports changing prevalence or unmeasured sex dependencies.',
  'No numerical external source-context replay was available or claimed. Actual initial aggregate feedback and earlier trial feedback are bound, while generator, specification and evidence are unchanged.'
 ],
 'remaining_limitations':[
  'The CHNS summaries are disclosed development sample estimates; calibration agreement cannot establish population recovery or independent validation.',
  'Reference coefficient CR1 intervals and repeated synthetic-draw variability concern different uncertainties. Three draws give a weak descriptive variance estimate and do not calibrate model, source or transport uncertainty.',
  'Female independence, fixed age-BMI/BMI-glucose latent couplings, nested broad-component labels, state-specific Gaussian copulas and tail shapes remain explicit underidentified assumptions.',
  'BMI quantiles only approximately follow the reference because the lognormal family matches mean and SD. Continuous glycemic measurements do not reconstruct reference rounding or ties.',
  'External studies have different populations, exclusions, assays/specimens, weights and adjustment sets. Source context checks remain not_computable and no unit relation proves transport.',
  'Causal effects, treatment, disease labels, individual risk, sex-specific or subgroup analyses, extreme tails and national representativeness are unassessed.'
 ]}
write('final_author_decision.json',decision)
(ROOT/'FINAL_AUTHOR_DECISION.json').write_text(json.dumps(decision,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
review={
 'scope':'permitted_initial_feedback_and_deterministic_model_anchors_only',
 'source_feedback':'initial_feedback.json','source_feedback_sha256':sha(HERE/'initial_feedback.json'),
 'candidate':'mixture_final01','parent_candidate':'mixture_initial01','decision':'retain',
 'scientific_files_unchanged':{name:sha(HERE/name)==sha(OLD/name) for name in ['generator.py','model_spec.json','evidence.json']},
 'records':records,
 'run_quality':[{'seed':r['seed'],'n':r['analysis_feedback']['n'],'quality':r['analysis_feedback']['quality']} for r in feedback['runs']],
 'uncertainty_caution':'Three-draw SD and model mean SD describe conditional synthetic generation, not independent validation, reference sampling, structural or transport uncertainty.',
 'optional_final_phase_trials_requested':0,
 'new_retrieval_queries':[],'new_retrieval_documents':[],
 'local_generator_imported_or_executed':False,'local_rows_produced':0}
write('initial_feedback_review.json',review)
checks=read(HERE/'checks.json')
checks['records'].append({'name':'all_initial_feedback_review','status':'pass',
  'detail':'All 30 statistics on three fixed initial seeds reviewed with full actual feedback bound. Scientific law retained, no phase-final trial requested; finite-cohort variation distinguished from known BMI family approximation and unassessed structural uncertainty.'})
for name in ['initial_feedback.json','initial_feedback_review.json','final_author_decision.json']:
    checks['artifacts'].append({'path':name,'sha256':sha(HERE/name)})
write('checks.json',checks)
(HERE/'decision.md').write_text('''# Final scientific decision: retain

The final candidate is mixture_final01. Retain generator.py, model_spec.json and evidence.json byte-for-byte from mixture_initial01; the change is truthful feedback binding and the final decision record. Full initial feedback, all 30 per-statistic reviews, earlier trial4201 feedback and the deterministic producer scripts remain in this candidate. No additional final-phase trial is requested.

All three initial fixed-seed deliveries succeeded with 3000 valid rows, 30 computed statistics, no nonpositive glucose/HbA1c and no duplicate measurement rows. The three-draw E1/E2/E3 means differ from the disclosed reference by +0.000438, -0.005153 and -0.000161. E2 spans 0.358685-0.427418; this spread is retained rather than corrected against fixed seeds. The reference CR1 confidence interval describes a different uncertainty and is not a predictive interval for synthetic draws. Pearson and Spearman means differ by -0.003775 and -0.003886. No coefficient p-value or favorable-seed rule is used.

The known BMI family approximation remains explicit: population q90 is 28.1768 versus sample reference 28.1010, and population median is 23.4588 versus 23.4240. The observed mean q90 discrepancy of +0.1282 includes that approximation and conditional variability. We do not claim every discrepancy is noise. Other calibrated working population moments follow the admitted sample estimates mathematically, but neither that fit nor three finite draws identifies the full joint law or verifies population recovery.

Scientific structure remains two overlapping positive lognormal mixtures for glucose and HbA1c with nested broad labels, stronger glycemic latent association in broad states, a discrete entropy age distribution, a mean/SD-matched lognormal BMI margin and a Bernoulli female margin. Label nesting, female independence, weak age-BMI and BMI-glucose latent couplings, Gaussian copulas and continuous assay representation remain modeling assumptions. Positive support and finite lognormal moments are established by the chosen mathematical family; clinical tail validity is not established. The retained derivation scripts use deterministic equations and integration only; no synthetic rows were produced locally.

The evidence package is preserved. Bao plasma Pearson, MIND serum Spearman, differently adjusted Jansen projections and Pani weighted age evidence retain their source contexts. The restored age evidence was considered; no absence of age evidence is claimed. The NGSP unit relation changes representation but does not establish serum/plasma, assay or target-population equivalence. External source-context replay remains not_computable.

The full reasons and remaining limitations are in final_author_decision.json and the root FINAL_AUTHOR_DECISION.json. Reference sample uncertainty, structural ambiguity and transport uncertainty are separate from conditional synthetic variation. Clinical decisions, diagnosis, causal effects, sex-specific/subgroup analyses, extreme tails and national prevalence remain unassessed.

Requested final delivery: fixed seeds 4101, 4102 and 4103. Same seed and unchanged scientific bytes should reproduce initial numerical output; this is a documented no-op, not an improved model claim. No new retrieval, paid API, scientific subagent or local generator execution occurred.
''',encoding='utf-8')
print(json.dumps({'candidate':HERE.name,'requested_stage':'final_delivery','decision':decision['kind'],
  'scientific_files_unchanged':review['scientific_files_unchanged'],'reviewed_statistic_count':len(records),
  'root_decision':str(ROOT/'FINAL_AUTHOR_DECISION.json')},indent=2))

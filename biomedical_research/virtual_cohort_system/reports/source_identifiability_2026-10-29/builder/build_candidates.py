"""Build source-only candidate artifacts. Never import or execute a generator."""
from pathlib import Path
import ast
import copy
import csv
import hashlib
import json
import math
import shutil
import sys

BUNDLE = Path(__file__).resolve().parent
PROJECT = BUNDLE.parents[2]
ANCHOR = PROJECT / 'work/structure-robustness-2026-10-28/agent_bundle/candidates/s1_final'
FEEDBACK = PROJECT / 'work/structure-robustness-2026-10-28/source_feedback/s1_final_portfolio.json'
PLAN = BUNDLE.parent / 'design/BUILDER_PLAN.md'
sys.path.insert(0, str(PROJECT))
from cohort_harness.__main__ import validate_bundle


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


GENERATOR = '''import math
import numpy as np


def _normal_cdf(values):
    root_two = math.sqrt(2.0)
    return np.fromiter((0.5 * (1.0 + math.erf(float(v) / root_two)) for v in values), dtype=float, count=len(values))


def _measurement(legacy, observed, p):
    regime = observed["tg_assay"].to_numpy()
    valid = (regime == "legacy_proxy") | (regime == "unblanked_2021_2023")
    if not np.all(valid):
        raise ValueError("Unknown measurement regime")
    result = observed.copy(deep=True)
    assay = p["assay"]
    result["tg_mg_dl"] = np.where(regime == "unblanked_2021_2023", assay["intercept"] + assay["slope"] * legacy, legacy)
    return result


def generate(observed, spec, seed):
    """Shared lognormal anchor, with a bounded male conditional-density interaction."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    reference = p["reference"]
    m = np.asarray(reference["tg_mean"])[sex]
    m = m + np.asarray(p["bmi_slope"])[sex] * (bmi - np.asarray(reference["bmi_mean"])[sex])
    m = m + np.asarray(p["age_slope"])[sex] * (age - np.asarray(reference["age_mean"])[sex])
    regular = p["positive_mean"]
    m = regular["floor"] + regular["width"] * np.logaddexp(0, (m - regular["floor"]) / regular["width"])
    cv = np.asarray(p["residual_cv"])[sex]
    variance = np.log1p(cv * cv)
    z = rng.normal(size=len(observed))
    legacy = m * np.exp(z * np.sqrt(variance) - .5 * variance)

    d = p["density_interaction"]
    sign = d["sign"]
    if sign == 0:
        return _measurement(legacy, observed, p)
    if sign not in (-1, 1):
        raise ValueError("Unknown density-interaction sign")
    ap, an = d["age_positive"], d["age_negative"]
    bp, bn = d["bmi_positive"], d["bmi_negative"]
    ha = d["age_positive_weight"] * ((age >= ap[0]) & (age <= ap[1])).astype(float) - ((age >= an[0]) & (age <= an[1])).astype(float)
    hb = d["bmi_positive_weight"] * ((bmi >= bp[0]) & (bmi < bp[1])).astype(float) - ((bmi >= bn[0]) & (bmi < bn[1])).astype(float)
    yp, yn = d["tg_positive"], d["tg_negative"]
    active = (sex == 0) & (ha != 0) & (hb != 0) & (legacy > yp[0]) & (legacy < yn[1])
    if not np.any(active):
        return _measurement(legacy, observed, p)
    u = _normal_cdf(z[active])
    log_location = np.log(m[active]) - .5 * variance[active]
    sigma = np.sqrt(variance[active])
    amount = sign * d["delta"] * ha[active] * hb[active]
    low = np.full(len(u), yp[0], dtype=float)
    high = np.full(len(u), yn[1], dtype=float)
    for _ in range(d["inverse_cdf_steps"]):
        mid = .5 * (low + high)
        base_cdf = _normal_cdf((np.log(mid) - log_location) / sigma)
        kernel_cdf = np.clip((mid - yp[0]) / (yp[1] - yp[0]), 0.0, 1.0) - np.clip((mid - yn[0]) / (yn[1] - yn[0]), 0.0, 1.0)
        cdf = base_cdf + amount * kernel_cdf
        below = cdf < u
        low = np.where(below, mid, low)
        high = np.where(below, high, mid)
    legacy[active] = .5 * (low + high)
    return _measurement(legacy, observed, p)
'''

anchor = read(ANCHOR / 'model_spec.json')
params = anchor['parameters']
task = read(BUNDLE / 'task.json')
assert task['budget'] == {'source_queries': 0, 'source_downloads': 0, 'revisions': 0}
assert task['mode'] == 'enrichment'
counts = {'male_n': 0, 'age_positive': 0, 'age_negative': 0, 'bmi_positive': 0, 'bmi_negative': 0}
with (ANCHOR / 'source_contexts/oh.csv').open(newline='', encoding='utf-8-sig') as handle:
    for row in csv.DictReader(handle):
        if int(row['sex']) != 1:
            continue
        a, b = int(row['age']), float(row['bmi'])
        counts['male_n'] += 1
        counts['age_positive'] += 35 <= a <= 44
        counts['age_negative'] += 55 <= a <= 64
        counts['bmi_positive'] += 22 <= b < 24
        counts['bmi_negative'] += 26 <= b < 28
assert counts == {'male_n': 61740, 'age_positive': 18693, 'age_negative': 9103, 'bmi_positive': 14851, 'bmi_negative': 10388}
wa = counts['age_negative'] / counts['age_positive']
wb = counts['bmi_negative'] / counts['bmi_positive']
cv = params['residual_cv'][0]
variance = math.log1p(cv * cv)
sigma = math.sqrt(variance)


def analytic_mean(a, b):
    # Closed-form anchor equation for the positivity certificate, not a generator call.
    m = params['reference']['tg_mean'][0] + params['bmi_slope'][0] * (b - params['reference']['bmi_mean'][0]) + params['age_slope'][0] * (a - params['reference']['age_mean'][0])
    floor, width = params['positive_mean']['floor'], params['positive_mean']['width']
    return floor + width * math.log1p(math.exp((m - floor) / width))


means = [analytic_mean(64, 22), analytic_mean(35, 28)]
corners = []
for m in means:
    for y in (70, 120, 140, 190):
        z = (math.log(y) - math.log(m) + .5 * variance) / sigma
        corners.append({'mu_mg_dl': m, 'y_mg_dl': y, 'density': math.exp(-.5*z*z) / (y*sigma*math.sqrt(2*math.pi))})
d_min = min(x['density'] for x in corners)
# The design literal is frozen; recomputation checks rather than retunes it.
delta = 0.07077021813077161
assert math.isclose(delta, .8*50*d_min, rel_tol=1e-13, abs_tol=1e-15)
cells = []
for a, ha in ((40, wa), (60, -1.0)):
    for b, hb in ((23, wb), (27, -1.0)):
        diff = -140*delta*ha*hb
        cells.append({'age': a, 'bmi': b, 'sex': 1, 'hA': ha, 'hB': hb, 'E_plus_minus_E_minus_mg_dl': diff, 'absolute_difference_mg_dl': abs(diff)})
assert max(c['absolute_difference_mg_dl'] for c in cells) >= 5
certificate = {
    'scope': 'source_only_analytic_no_generator_execution',
    'anchor_code_sha256': sha(ANCHOR / 'generator.py'),
    'anchor_spec_sha256': sha(ANCHOR / 'model_spec.json'),
    'source_covariates_sha256': sha(ANCHOR / 'source_contexts/oh.csv'),
    'source_marginal_counts': counts,
    'hA_formula': '(9103/18693)*I(35<=age<=44)-I(55<=age<=64)',
    'hB_formula': '(10388/14851)*I(22<=BMI<24)-I(26<=BMI<28)',
    'hT_formula': 'I(70<=TG<=120)/50-I(140<=TG<=190)/50',
    'hT_integral': 0,
    'hT_first_moment_mg_dl': -70,
    'marginal_centering': {'age_numerator': wa*counts['age_positive']-counts['age_negative'], 'bmi_numerator': wb*counts['bmi_positive']-counts['bmi_negative']},
    'sigma': sigma,
    'mu_bounds_mg_dl': means,
    'density_corner_evaluations': corners,
    'density_min': d_min,
    'safety_fraction': .8,
    'delta': delta,
    'density_ratio_lower_bound': .2,
    'density_ratio_upper_bound': 1.8,
    'positivity_derivation': 'Anchor mean is monotone in age/BMI on compact support. Log lognormal density is concave jointly in log(y),log(mu); its minimum on each enclosing rectangle occurs at a vertex. |hA*hB|<=1 and |hT|<=1/50. The design delta=.8*50*d_min therefore gives .2*f0<=f_sign<=1.8*f0 within kernel support and f_sign=f0 outside. Floating point values summarize this symbolic bound, not a sampled grid minimum.',
    'population_invariance_derivation': 'For the declared product male age-BMI law, E[hA]=E[hB]=0. Integrating f0+sign*delta*hA*hB*hT over either covariate cancels the perturbation for every value of the other covariate and TG. Full age-TG and BMI-TG laws, their stratum distributions, TG marginal, and linear OLS cross-moments stay unchanged. Female laws are identical. The finite permuted source file is not an exact product law; finite replay checks are required.',
    'finite_context_status': 'Marginal centering verified; empirical independence and finite replay equivalence not asserted.',
    'conditional_mean_contrast_formula': 'E_plus-E_minus=-140*delta*hA*hB',
    'materiality_cells': cells,
    'materiality_statistic': 'maximum absolute analytical conditional mean difference over the four declared male cells',
    'materiality_threshold_mg_dl': 5.0,
    'materiality_value_mg_dl': max(c['absolute_difference_mg_dl'] for c in cells),
    'materiality_interpretation': 'Engineering model-separation threshold, not a clinical difference, sampling CI, or a desired target association.',
    'inverse_cdf_steps': 40,
    'bisection_final_interval_width_mg_dl': 120/(2**40),
    'bisection_scope': 'Analytic interval bound apart from floating-point CDF evaluation. No numerical generator test was run.',
    'source_seeds': [78101,78102,78103],
    'probe_seeds': [78201,78202,78203],
}

semantic = {
    'scope': 'source_only_semantic_supplement_from_verified_replay_outputs',
    'status': 'definitions_only_not_computed',
    'context': 'oh',
    'outcome': 'tg_mg_dl',
    'unit': 'mg/dL',
    'measurement': 'identity legacy_proxy',
    'missing_policy': 'error',
    'methods': [
        {'id': 'arithmetic', 'formula': 'sum(TG)/n', 'status': 'sensitivity_interpretation'},
        {'id': 'geometric', 'formula': 'exp(sum(log(TG))/n)', 'requires': 'all TG strictly positive', 'status': 'sensitivity_interpretation'}
    ],
    'source_estimator': 'not_resolved_arithmetic_or_geometric',
    'boundary_assumption': 'Age <=29,30-39,40-49,50-59,>=60. BMI half-open <20,[20,23),[23,25),[25,30),>=30 resolves printed adjacent-bin endpoint ambiguity as an explicit approximation, not an exact source definition.',
    'groups': [],
    'reporting': 'For each label, seed, sex, stratum and both methods, report n, estimate, printed source value, signed/absolute discrepancy and paired difference versus zero. Retain all 40 sex/stratum/interpretation diagnostics. Bind verified replay/candidate/output hashes. Current declarative harness operators do not compute geometric means; do not label this supplement an exact harness source check.',
    'other_unreplayed_evidence': 'Oh Table4/Table5/Table6 additional-adjustment, mixed/family and co-twin estimands remain unassessed with missing design/covariates. The apparent FBS Table2 anomaly remains unresolved. Neither missing operators nor estimator ambiguity removes evidence.'
}
age_bins = [(None,30),(30,40),(40,50),(50,60),(60,None)]
bmi_bins = [(None,20),(20,23),(23,25),(25,30),(30,None)]
vals = {
    ('age',1):[143,147.5,140.6,143.5,128.1], ('age',2):[78.1,80.7,89.4,127.8,135.3],
    ('bmi',1):[91.8,109.4,141.4,165.3,220.5], ('bmi',2):[73.8,86.5,100.9,126.7,127.3]
}
for variable, bins in [('age',age_bins),('bmi',bmi_bins)]:
    for sex in (1,2):
        for k, (lo,hi) in enumerate(bins,1):
            semantic['groups'].append({'id':f'oh_{"male" if sex==1 else "female"}_{variable}_stratum_{k}', 'evidence_id':f'E_oh_{"male" if sex==1 else "female"}_{variable}_stratum_{k}_tg', 'sex':sex, 'variable':variable, 'lower_inclusive':lo, 'upper_exclusive':hi, 'reported_value':vals[(variable,sex)][k-1]})

lineage = {
    'anchor': 'structure-robustness-2026-10-28/agent_bundle/candidates/s1_final',
    'code_sha256': sha(ANCHOR/'generator.py'),
    'spec_sha256': sha(ANCHOR/'model_spec.json'),
    'evidence_sha256': sha(ANCHOR/'evidence.json'),
    'source_recipe_sha256': sha(ANCHOR/'source_replay.json'),
    'historical_source_feedback_sha256': sha(FEEDBACK),
    'new_study_scope': 'Synthetic covariate-only probe; three independent initial candidates. No revisions and no prior target outcome access.',
    'anchor_status': 'Source-conditioned anchor, not a validated winner; all existing source mismatches remain bound in baseline_source_feedback.json.',
    'zero_equivalence': 'The scientific parameters, arithmetic/softplus/lognormal operations and RNG normal draw sequence are retained exactly from the anchor; structure_id is metadata only. Static code comparison, not executed-output equivalence.'
}

tree = ast.parse(GENERATOR)
imports = [node.names[0].name for node in tree.body if isinstance(node, ast.Import)]
assert imports == ['math','numpy']
generate_defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'generate']
assert len(generate_defs) == 1 and len(generate_defs[0].args.args) == 3
assert 'open(' not in GENERATOR and 'record_id' not in GENERATOR
static = {
    'status': 'pass',
    'scope': 'static syntax, allowed imports, top-level signature, source counts, fixed-parameter algebra and certificate only; no generator import or call',
    'imports': imports,
    'generate_positional_arguments': [a.arg for a in generate_defs[0].args.args],
    'no_file_network_identifier_access_in_code': True,
    'source_marginal_counts_match_design': True,
    'fixed_delta_matches_certificate': True,
    'materiality_max_at_least_5_mg_dl': True,
    'source_replay_execution': 'not_performed',
    'generator_runtime_validation': 'not_performed',
    'independent_review': 'controller_pending_after_freeze',
}

updates = {
    'A_shared_source_interpretation': 'All zero/minus/plus labels use identical admitted Oh PMC6911291.1 and Bansal publisher snapshot, evidence bytes, source covariates, replay recipes, measurement mapping and semantic definitions. Summaries share study participants; repeated rows/seeds are not independent clinical evidence. No real target outcomes are available.',
    'A_transport': 'This task appends TG to a synthetic age/sex/BMI grid only. It makes no target-population validity claim. The two source contexts retain their distinct population/selection/measurement limitations. The source-derived biological law is applied uniformly without cohort/assay/ID selectors; any use outside a reported source population remains an unverified transport assumption.',
    'A_monte_carlo': 'Fixed source covariates and scientific parameters; source seeds78101,78102,78103 and synthetic probe seeds78201,78202,78203 vary individual residual draws. The paired inverse-CDF uses the same original normal draw without new RNG draws. Source seed variation is Monte Carlo variation, not source-study confidence, structural uncertainty or population-transfer uncertainty. All three labels and scheduled seeds are retained.',
    'A_structure': 'The base f0 is the s1_final additive conditional arithmetic mean with sex-specific BMI/linear age slopes, smooth positive floor and mean-one lognormal residual. zero uses exactly f0. minus/plus add a compact male density interaction described in A_density_interaction. This changes age-BMI-TG three-way dependence under an explicitly assumed product source covariate law while preserving both bivariate outcome laws in population. It is a sensitivity construction, not a reported mechanism.'
}
new_assumptions = [
    {'id':'A_baseline_lineage','description':'The exact historical source-only anchor code/spec/evidence/recipe hashes and actual source-feedback report are bound. This anchor has documented source mismatches, including Bansal quartiles and age Spearman; invariance preserves rather than repairs them. No winning or clinically valid status is inferred.'},
    {'id':'A_density_interaction','description':'f_t=f0+t*delta*hA(age)*hB(BMI)*hT(TG) for men only. Compact bases are zero outside declared interior source-support regions and marginally centered using fixed source covariates. Integral(hT)=0 ensures per-person normalization. Independent source age/BMI makes both age-TG and BMI-TG laws invariant; finite independently permuted source rows are not exactly a product law. Unknown real-source dependence and missing covariates remain limitations. Sign labels denote density directions only; no desired outcome sign or target coefficient is supplied.'},
    {'id':'A_density_positivity','description':'delta is the fixed pre-execution design value .07077021813077161, obtained as .8*50 times the analytically endpoint-certified minimum male f0 density on the compact support. The bound gives .2*f0<=f_t<=1.8*f0 on kernel support and equality elsewhere. Certificate includes complete formulas/corners; this is not a grid-minimum claim or a source-estimated amplitude.'},
    {'id':'A_inverse_cdf','description':'Use the anchor normal draw to define its uniform CDF value; invert F0+t*delta*hA*hB*H on[70,190] with40bisectionsteps using stdlib math.erf and NumPy. All other rows retain their baseline draw exactly. Analytic final interval width120/2^40 is separate from ordinary floating-point error; no runtime success is claimed before isolated execution.'},
    {'id':'A_materiality','description':'Prespecified analytical materiality is max absolute E_plus(TG|age,BMI,sex=1)-E_minus over age40/60 and BMI23/27, at least5mg/dL. Fixed parameters give max9.907830538308025mg/dL at60/27. Not every cell must exceed5. This is a diagnostic model-separation threshold, not clinical importance, inferential certainty or a desired target regression sign.'},
    {'id':'A_semantic_coverage','description':'Oh Table2 age/BMI values remain unresolved arithmetic/geometric evidence. semantic_metrics.json declares both interpretations and explicit interval approximations, to be computed only from verified source replay output. Both bivariate distributions are invariant under the product population regardless of estimator interpretation, but anchor discrepancies and finite-context deviations remain. Other adjusted/family estimands remain unassessed; lack of operators does not remove them.'},
]

for label, sign in [('zero',0),('minus',-1),('plus',1)]:
    dest = BUNDLE/'candidates'/label
    if dest.exists():
        raise RuntimeError(f'Refuse to replace existing candidate {dest}')
    dest.mkdir(parents=True)
    shutil.copy2(ANCHOR/'evidence.json', dest/'evidence.json')
    shutil.copy2(ANCHOR/'source_replay.json', dest/'source_replay.json')
    shutil.copytree(ANCHOR/'source_contexts', dest/'source_contexts')
    shutil.copy2(FEEDBACK, dest/'baseline_source_feedback.json')
    shutil.copy2(PLAN, dest/'builder_plan.md')
    spec = copy.deepcopy(anchor)
    spec['parameters']['structure_id'] = 'source_density_interaction'
    spec['parameters']['density_interaction'] = {
        'sign':sign, 'delta':delta, 'safety_fraction':.8,
        'age_positive':[35,44], 'age_negative':[55,64], 'age_positive_weight':wa,
        'bmi_positive':[22,24], 'bmi_negative':[26,28], 'bmi_positive_weight':wb,
        'tg_positive':[70,120], 'tg_negative':[140,190], 'inverse_cdf_steps':40
    }
    for assumption in spec['assumptions']:
        if assumption['id'] in updates:
            assumption['description'] = updates[assumption['id']]
    spec['assumptions'].extend(copy.deepcopy(new_assumptions))
    spec['parameter_provenance']['structure_id'] = {'evidence_ids':[], 'assumption_ids':['A_structure','A_density_interaction'], 'derivation':'Three fixed sensitivity labels share one anchor and one compact interaction family; no model probabilities or target-result ranking.'}
    spec['parameter_provenance']['density_interaction'] = {'evidence_ids':[], 'assumption_ids':['A_density_interaction','A_density_positivity','A_inverse_cdf','A_materiality','A_baseline_lineage','A_semantic_coverage'], 'derivation':'All bounds, bands, materiality threshold and safety fraction were specified before execution. Source-only marginal counts set compact centering fractions; analytic endpoint positivity sets fixed delta. Sign is the only numerical difference among the three specifications. Parameters are scientific sensitivity assumptions, not estimated source coefficients or uncertainty.'}
    write(dest/'model_spec.json', spec)
    (dest/'generator.py').write_text(GENERATOR, encoding='utf-8')
    write(dest/'analytic_certificate.json', certificate)
    write(dest/'semantic_metrics.json', semantic)
    write(dest/'baseline_lineage.json', lineage)
    write(dest/'static.json', static)
    (dest/'decision.md').write_text(f'''# {label}: independent initial source-only candidate

Use the fixed density-interaction sign {sign} with delta {delta!r}; retain the historical s1_final anchor scientific parameters. No source/statistical fitting or generator call occurred during building. All three labels will be retained; there is no selected winner and no desired target answer.

The compact interaction changes male three-way age-BMI-TG dependence while its zero marginal covariate integrals preserve the complete age-TG and BMI-TG population laws under declared source independence. Female laws are unchanged. This applies inside reconstructed source support and preserves both possible Oh Table2 mean interpretations, rather than ignoring unreplayed evidence. Finite source files approximate a product law; numerical invariance still requires complete verified replay.

The frozen certificate proves normalization/positivity and max analytical plus-minus conditional mean difference9.907830538308025mg/dL at male age60/BMI27. The predeclared max-over-four-cells threshold is5mg/dL, not clinical/inferential certainty. Common-uniform inversion has40steps and requires no new random draws. No observed value, identifier or row order/count determines biological parameters.

Historical source feedback is bound unchanged. The anchor's Bansal quantiles76.68495/111.58464/162.29614 versus81/115/169, age Spearman.14405 versus.18, and male TG<150.66472 versus.684159 illustrate unresolved source discrepancies. Numerical non-distinguishability does not establish substantive source compatibility, population validity or an individual recovery claim.

Source seeds78101..78103 and synthetic covariate-probe seeds78201..78203 are controller-run after all three freezes and independent review. No real target outcomes are part of this task. The separate controller numerical gate is descriptive; source-seed SD is not a sampling SE, probability of correctness or calibration weight. Both arithmetic/geometric Table2 audits remain explicitly alternative interpretations; unsupported full-adjustment/family estimands remain unassessed.

Task revisions budget is0. This is an independent initial candidate with no parent. No local generator execution/fallback is authorized. Static contracts, source-count algebra and artifact binding can pass without numerical generator or scientific validity. Execution-backed source review and the final interpretation remain pending.
''', encoding='utf-8')
    contract_result = validate_bundle(BUNDLE, dest)
    write(dest/'contract_validation.json', contract_result)
    artifacts = ['analytic_certificate.json','semantic_metrics.json','baseline_lineage.json','baseline_source_feedback.json','builder_plan.md','static.json','contract_validation.json']
    checks = {'scope':'source_only', 'records':[
        {'name':'static_contract_validation','status':'pass','detail':'Harness validate_bundle returned valid program contract without importing/executing generator; result bound.'},
        {'name':'source_counts_and_analytic_certificate','status':'pass','detail':'Counted permitted frozen source covariates and evaluated explicit lognormal endpoint formulas; normalization, positivity and fixed max-cell materiality derivations retained. No generator call.'},
        {'name':'static_program_review','status':'pass','detail':'Parsed AST/signature/imports and reviewed file/network/identifier absence. Only math/NumPy imported; actual isolated-runtime behavior remains untested.'},
        {'name':'historical_source_feedback_review','status':'pass','detail':'Actual s1_final source portfolio bound with all46 diagnostics and remaining discrepancies. Historical source agreement is not new-model numerical validation.'},
        {'name':'current_source_replay','status':'not_computable','detail':'No generator execution or source replay performed by builder. Controller will execute frozen candidates under complete fixed schedule.'},
        {'name':'semantic_supplement','status':'not_computable','detail':'Both arithmetic and geometric Table2 metric definitions frozen; calculations await verified source output. Unsupported additional-adjustment/family estimands remain unassessed.'},
        {'name':'probe_or_target_validation','status':'not_computable','detail':'Synthetic probe execution pending; no real target outcomes available or used. Synthetic separation is not clinical validation.'},
    ], 'artifacts':[{'path':f,'sha256':sha(dest/f)} for f in artifacts]}
    write(dest/'checks.json', checks)
    assert sha(dest/'evidence.json') == sha(ANCHOR/'evidence.json')
    assert sha(dest/'source_replay.json') == sha(ANCHOR/'source_replay.json')
    print(json.dumps({'candidate':label, 'contract':contract_result, 'generator_sha256':sha(dest/'generator.py'), 'spec_sha256':sha(dest/'model_spec.json')}))

print(json.dumps({'scope':'artifact_build_and_static_validation_only','generator_executed':False,'delta':delta,'materiality_cells':cells,'certificate_sha256':sha(BUNDLE/'candidates/zero/analytic_certificate.json')}))

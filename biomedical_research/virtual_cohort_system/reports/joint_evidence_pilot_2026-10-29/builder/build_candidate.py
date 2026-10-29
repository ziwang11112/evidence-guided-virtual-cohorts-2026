"""Construct a candidate from admitted source evidence; never run its generator."""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys

P = Path(r'${PROJECT_ROOT}')
B = P / 'work/joint-evidence-pilot-2026-10-29/agent_bundle'
BASE = B / 'candidates/baseline'
C = B / 'candidates/joint_evidence'
C.mkdir(exist_ok=True)
assert not (C / 'freeze.json').exists(), 'Never rewrite a frozen candidate'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(name, value):
    (C / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


evidence = read(BASE / 'evidence.json')
spec = read(BASE / 'model_spec.json')
registry = read(B / 'registry.json')['artifacts']
source = next(x for x in evidence['sources'] if x['id'] == 'Mikkelsen2023_Tromso7')
source['artifacts'] = [dict(path=x['path'], sha256=x['sha256']) for x in registry if x['source_id'] == source['id']]
source['identifier'] += '; exact Supplementary Table 1 DOCX and its curator-verified cell extraction admitted in this bundle; PMC version 1 metadata retained'
source['population'] += '; Supplementary Table 1 gives 10,143 women and 9,583 men for main models; main-text Results gives 9,341 men. The inconsistency is retained and not resolved by selecting a preferred count.'

# Read exact published cells, retaining all 30 values and all 28 nonreference CIs.
table = read(B / 'sources/Mikkelsen2023_supplement_tables.json')[0]
age_labels = ['40-49', '50-59', '60-69', '70-79', '80+']
bmi_labels = ['lt25', '25to29_9', 'ge30']
cells = {}
sex = None
bmi = None
in_joint = False
for row_number, row in enumerate(table, 1):
    if row[0].startswith('Women'):
        sex, in_joint = 2, False
    elif row[0].startswith('Men'):
        sex, in_joint = 1, False
    if row[1].startswith('BMI <25'):
        bmi, in_joint = 0, True
    elif row[1].startswith('BMI 25-29.9'):
        bmi, in_joint = 1, True
    elif row[1].startswith('BMI ≥30'):
        bmi, in_joint = 2, True
    elif row[1] and row[1] != 'BMI by age' and not row[1].startswith('BMI '):
        in_joint = False
    label = re.sub(r'\s+', '', row[2])
    if in_joint and label in age_labels:
        age_index = age_labels.index(label)
        estimate = float(row[3])
        if row[4] == 'Reference':
            uncertainty = {'kind': 'not_reported'}
        else:
            low, high = map(float, re.findall(r'\d+\.\d+', row[4]))
            uncertainty = {'kind': 'ci', 'low': low, 'high': high, 'level': 0.95}
        cells[(sex, age_index, bmi)] = (estimate, uncertainty, row_number, row[4])
assert len(cells) == 30
assert sum(v[1]['kind'] == 'ci' for v in cells.values()) == 28
assert cells[(2, 0, 1)][:2] == (1.24, {'kind': 'ci', 'low': 1.23, 'high': 1.28, 'level': 0.95})

adjustment = ['time_since_last_meal', 'physical_activity', 'education', 'smoking', 'lipid_lowering_medication', 'recent_exercise', 'recent_alcohol']
joint_ids = []
for sex in (1, 2):
    for a, age_label in enumerate(age_labels):
        for b, bmi_label in enumerate(bmi_labels):
            estimate, uncertainty, row_number, ci_text = cells[(sex, a, b)]
            item_id = f'E_tromso_s{sex}_age{age_label.replace("-", "_").replace("+", "plus")}_bmi{bmi_label}_RD'
            joint_ids.append(item_id)
            evidence['items'].append({
                'id': item_id, 'source_id': source['id'],
                'locator': f'Supplementary Table 1, {"Men" if sex == 1 else "Women"}, BMI {bmi_label}, age {age_label}; exact extracted table 1 row {row_number}; RD and 95% CI columns',
                'variables': ['tg_mg_dl', 'age', 'bmi'],
                'kind': 'reported_other',
                'statistic_name': 'Back-transformed adjusted log-TG coefficient (relative difference) versus same-sex age40-49/BMI<25 reference',
                'estimate': estimate, 'unit': '1', 'uncertainty': uncertainty,
                'adjustment': adjustment,
                'selection': f'Tromso7 age40+; serum TG <=10 mmol/L and nonmissing; {"men, Supplement S1 n=9583 (main Results n=9341)" if sex == 1 else "women n=10143"}; age {age_label}, BMI {bmi_label}; common same-sex age40-49/BMI<25 reference.',
                'applicability': 'Reported point and CI retained exactly, including the female age40-49/BMI25-29.9 value 1.24 [1.23,1.28]. The two reference values 1 are coding conventions with no reported sampling CI. These are adjusted ratios of exponentiated log-TG predictions, not unadjusted arithmetic means or raw-TG regression slopes. Unitless ratios require no mmol/L-to-mg/dL conversion. Adjustment list follows the supplementary footnote and Figure3 caption; men do not have education/drug coefficient rows and Figure2 describes these as women-only, so exact male adjustment remains ambiguous. All cells share a cohort and reference; joint coefficient covariance is unavailable. Nonfasting-to-fasting, conditional-to-marginal, serum/assay and Norway-to-US transport are unverified. No CI for a ratio-of-ratios is computed by treating the cells as independent.'
            })

for item in evidence['items']:
    if item['id'] == 'E_tromso_joint_coefficients_missing_context':
        item['locator'] = 'Historical M7 retrieval limitation, resolved in current bundle by exact Supplementary Table 1 DOCX and curator-verified table extraction'
        item['applicability'] = 'Historical context only: the previous attempt lacked the 28 nonreference joint ratios. The current candidate separately records all 30 exact joint cells and 28 CIs. Source main-text n=9341 men versus supplement/Figure2 n=9583 remains unresolved. Male education/drug adjustment ambiguity and missing shared-reference covariance remain. Supplement recovery resolves the missing-table gap; it does not supply a target conditional distribution.'
    elif item['id'].startswith('E_CPAR_'):
        item['applicability'] = item['applicability'].replace('This item updates the evidence record only; generator and model specification are retained.', 'This item supplies qualitative context only in this candidate. No per-SD conversion, effect ratio or age-54 numerical modifier is used; the numerical interaction departure comes solely from the independently admitted Tromso joint table.')

ratios = [[[cells[(s, a, b)][0] for b in range(3)] for a in range(5)] for s in (1, 2)]
spec['parameters']['structure_id'] = 's1_tromso_interaction'
spec['parameters']['joint_interaction'] = {
    'age_knots': [44.5, 54.5, 64.5, 74.5, 84.5],
    'bmi_knots': [22.5, 27.5, 32.5],
    'relative_differences': ratios,
    'transfer_fraction': 1.0,
}
replacement_assumptions = {
    'A_shared_source_interpretation': 'Oh PMC6911291.1, Bansal admitted publisher snapshot, China-PAR admitted main XML and Tromso PMC10308115 version1 main XML/exact supplement are the permitted scientific sources. Repeated publications, table cells sharing one reference, overlapping China-PAR subcohorts and replay seeds are not independent clinical evidence. No target outcome or target analysis result was supplied to the builder.',
    'A_source_measurement': 'Existing Oh/Bansal source replay rows use legacy_proxy and identity mg/dL mapping. Bansal explicitly corrected endogenous glycerol; Oh Cobas6000 glycerol blanking is unreported. Both use EDTA plasma, while the target contract represents fasting serum TG. Tromso uses nonfasting serum TG measured by Cobas8000 c702; its dimensionless log-scale interaction contrast is transported without changing the legacy_proxy assay definition. Exact source-to-target assay equivalence remains unverified.',
    'A_transport': 'The target contract is US noninstitutionalized fasting adults aged40-79. Existing main effects originate in selected Korean families and initially healthy US women; the interaction departure originates in Tromso Norway adults40+ sampled nonfasting. Selection, ancestry, era, age support and missing covariates differ. This is an assumption-dependent virtual distribution, not individual recovery, causal identification, proven measurement savings or validated inference. No cohort name, opaque identifier, row order or row count enters the biological mean.',
    'A_monte_carlo': 'Source covariate CSVs and biological parameters are fixed. Controller source seeds80201,80202,80203 and target seeds80101,80102,80103 vary individual residual draws only; they quantify Monte Carlo variation, not evidence, structural or transport uncertainty. The builder does not execute these schedules or use resulting outputs for parameter tuning.',
    'A_structure': 'Let g(a,b) be the inherited positive arithmetic mean including its soft floor for the selected sex. The new legacy mean is g(a,b0)*g(a0,b)/g(a0,b0)*exp(D(a,b)), with a0=44.5 and b0=22.5 from the first interpolation knots. This preserves inherited curves along the reference-age and reference-BMI lines, and replaces the baseline log cross-ratio with the source surface rather than adding another interaction to it. Individual noise remains independent mean-one lognormal with constant within-sex CV. Existing numerical parameters are fixed; published marginal moments, other conditional anchors and the pooled BMI coefficient are not claimed to be preserved.',
    'A_s1_revision': 'Historical baseline main-effect coefficients and CV are retained numerically, including female BMI slope 5.2 and the variance-weighted male slope 9.557309727577666. This pilot neither repeats that earlier source-conditioned revision nor retunes those values. The original moment derivation described the additive baseline; after replacing its log interaction, marginal mean/SD identities are no longer guaranteed.',
}
for assumption in spec['assumptions']:
    if assumption['id'] in replacement_assumptions:
        assumption['description'] = replacement_assumptions[assumption['id']]
spec['assumptions'].extend([
    {'id': 'A_joint_estimand_bridge', 'description': 'For each sex, D(a,b)=logR(a,b)-logR(a,b0)-logR(a0,b)+logR(a0,b0), where R is the published adjusted log-TG back-transformed coefficient and a0/b0 denotes age40-49/BMI<25. Replace the inherited positive mean g log cross-ratio by D: m=g(a,b0)*g(a0,b)/g(a0,b0)*exp(D). Thus the legacy-scale mean cross-ratio equals exp(D), while inherited positive curves are preserved at reference age/BMI; absolute source means/main effects are not substituted. Within this generator constant within-sex lognormal residual variance makes conditional geometric and arithmetic ratios coincide on the latent legacy_proxy scale only. The nonzero-intercept affine unblanked assay map does not preserve that equality or log cross-ratio. Constant source log dispersion, stability after integrating missing adjustment variables, and nonfasting-to-fasting transport are unverified bridge assumptions; male adjustment ambiguity remains.'},
    {'id': 'A_joint_continuity', 'description': 'Treat source age bands as represented by44.5,54.5,64.5,74.5,84.5 years and BMI bands as represented by22.5,27.5,32.5 kg/m^2. These are chosen numerical support points, not observed stratum means; especially BMI<25, BMI>=30 and age80+ are open-ended. Apply bilinear interpolation to D and clamp D at boundary knots. This is continuous with derivative changes at knots, not a smooth spline. Clamping concerns the interaction only; inherited curves g(a,b0) and g(a0,b) continue globally, an additional extrapolation assumption. The source categorical estimates identify neither this within-bin trajectory nor continuation of those reference-line curves.'},
    {'id': 'A_joint_transfer', 'description': 'Fix transfer_fraction=1 before any source replay or target output: full transfer of the extracted interaction departure is one interpretable sensitivity scenario, not an estimated optimal or calibrated transport weight. Retain observed departures in both sexes; the male interaction P=.32 does not prove zero. Do not add a separate China-PAR per-SD attenuation, since its normalization and longitudinal-to-cross-sectional mapping are unresolved. Existing main effects/CV/assay coefficients remain fixed; no source or target output-based tuning occurs in this pilot.'},
    {'id': 'A_joint_uncertainty', 'description': 'All28 published nonreference CIs are retained as source uncertainty for their own joint ratios. They are not independent and share a reference. Joint covariance is unreported, so no valid uncertainty distribution for D or for the transported surface is constructed. Point-surface replay seeds address residual Monte Carlo variation only. The exact female age40-49/BMI25-29.9 CI asymmetry and inconsistent male sample counts/adjustment descriptions are retained without correction.'},
])
spec['parameter_provenance']['structure_id'] = {'evidence_ids': joint_ids, 'assumption_ids': ['A_structure', 'A_joint_estimand_bridge', 'A_joint_transfer'], 'derivation': 'One source-based structural modification: replace the inherited positive mean log cross-ratio by the joint-table interaction surface, retaining reference-age/reference-BMI positive mean curves. This is a sensitivity scenario with no probability or performance ranking.'}
spec['parameter_provenance']['joint_interaction'] = {'evidence_ids': joint_ids, 'assumption_ids': ['A_joint_estimand_bridge', 'A_joint_continuity', 'A_joint_transfer', 'A_joint_uncertainty', 'A_transport'], 'derivation': 'relative_differences holds exact supplementary RD points in male/female, age ascending, BMI ascending order. Form logR-logR[:,BMIref]-logR[ageRef,:]+logR[ageRef,BMIref]. Age/BMI knots and full-transfer weight1 are explicit assumptions. No individual-CI weighting or independent-error propagation is used.'}
spec['parameter_provenance']['residual_cv']['derivation'] += ' These inherited CV values are held fixed after replacing the log interaction; the new candidate does not claim that the old baseline moment formula remains exact.'
spec['parameter_provenance']['bmi_slope']['derivation'] += ' This historical source-only baseline choice is retained without new fitting; interaction-adjusted effective BMI effects now vary by age/BMI and no exact pooled coefficient preservation is claimed.'

generator = '''import numpy as np


def _measurement(legacy, observed, p):
    regime = observed["tg_assay"].to_numpy()
    valid = (regime == "legacy_proxy") | (regime == "unblanked_2021_2023")
    if not np.all(valid):
        raise ValueError("Unknown measurement regime")
    result = observed.copy(deep=True)
    assay = p["assay"]
    result["tg_mg_dl"] = np.where(regime == "unblanked_2021_2023", assay["intercept"] + assay["slope"] * legacy, legacy)
    return result


def _joint_log_departure(age, bmi, sex, settings):
    """Bilinear source interaction surface; clamped at assumed support knots."""
    ages = np.asarray(settings["age_knots"], dtype=float)
    bmis = np.asarray(settings["bmi_knots"], dtype=float)
    logs = np.log(np.asarray(settings["relative_differences"], dtype=float))
    departure = logs - logs[:, :, :1] - logs[:, :1, :] + logs[:, :1, :1]
    a = np.clip(age, ages[0], ages[-1])
    b = np.clip(bmi, bmis[0], bmis[-1])
    ai = np.clip(np.searchsorted(ages, a, side="right") - 1, 0, len(ages) - 2)
    bi = np.clip(np.searchsorted(bmis, b, side="right") - 1, 0, len(bmis) - 2)
    wa = (a - ages[ai]) / (ages[ai + 1] - ages[ai])
    wb = (b - bmis[bi]) / (bmis[bi + 1] - bmis[bi])
    lower = (1 - wb) * departure[sex, ai, bi] + wb * departure[sex, ai, bi + 1]
    upper = (1 - wb) * departure[sex, ai + 1, bi] + wb * departure[sex, ai + 1, bi + 1]
    return settings["transfer_fraction"] * ((1 - wa) * lower + wa * upper)


def _baseline_positive_mean(age, bmi, sex, p):
    """Inherited conditional mean, used only for the two reference-line curves."""
    reference = p["reference"]
    m = np.asarray(reference["tg_mean"])[sex]
    m = m + np.asarray(p["bmi_slope"])[sex] * (bmi - np.asarray(reference["bmi_mean"])[sex])
    m = m + np.asarray(p["age_slope"])[sex] * (age - np.asarray(reference["age_mean"])[sex])
    regular = p["positive_mean"]
    m = regular["floor"] + regular["width"] * np.logaddexp(0, (m - regular["floor"]) / regular["width"])
    return m


def generate(observed, spec, seed):
    """Replace the legacy mean log interaction, preserving reference-line curves."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    joint = p["joint_interaction"]
    reference_age = joint["age_knots"][0]
    reference_bmi = joint["bmi_knots"][0]
    age_curve = _baseline_positive_mean(age, reference_bmi, sex, p)
    bmi_curve = _baseline_positive_mean(reference_age, bmi, sex, p)
    reference_mean = _baseline_positive_mean(reference_age, reference_bmi, sex, p)
    m = age_curve * bmi_curve / reference_mean
    m = m * np.exp(_joint_log_departure(age, bmi, sex, joint))
    cv = np.asarray(p["residual_cv"])[sex]
    variance = np.log1p(cv * cv)
    legacy = m * np.exp(rng.normal(size=len(observed)) * np.sqrt(variance) - .5 * variance)
    return _measurement(legacy, observed, p)
'''
(C / 'generator.py').write_text(generator, encoding='utf-8')
write('evidence.json', evidence)
write('model_spec.json', spec)
shutil.copy2(BASE / 'source_replay.json', C / 'source_replay.json')
(C / 'source_contexts').mkdir(exist_ok=True)
for name in ('oh.csv', 'bansal.csv'):
    shutil.copy2(BASE / 'source_contexts' / name, C / 'source_contexts' / name)

unsupported = []
for evidence_id in joint_ids + [x['id'] for x in evidence['items'] if x['id'].startswith('E_CPAR_')]:
    is_joint = evidence_id in joint_ids
    unsupported.append({'id': 'unreplayed_' + evidence_id, 'evidence_id': evidence_id,
        'status': 'not_computable', 'table': None, 'operator': None,
        'assumption_ids': ['A_joint_estimand_bridge', 'A_joint_uncertainty'] if is_joint else [],
        'reason': 'The supplied operators do not compute adjusted exponentiated log-TG coefficients or shared-reference interaction contrasts. Adjustment covariates, source conditional log variance and joint coefficient covariance are unavailable. Do not relabel these as arithmetic means/raw OLS or claim verified replay of this source.' if is_joint else 'Adjusted longitudinal mixed-effects per-SD BMI estimand is unsupported; normalization denominator and repeated-measure covariates are unavailable. No coefficient transfer or replay is claimed.'})
write('source_checks.json', {'schema_version': 1, 'checks': unsupported})

decision = '''# Joint-evidence structural pilot

The candidate replaces the inherited legacy TG mean's log interaction with an age-by-BMI departure from the exact Tromso supplementary joint table. For each sex, let R be the reported adjusted back-transformed log-TG coefficient, with reference age 40-49 and BMI<25. Define D(a,b)=logR(a,b)-logR(a,b0)-logR(a0,b)+logR(a0,b0). Let g(a,b) be the baseline positive arithmetic mean including its soft floor. The new positive legacy mean is m(a,b)=g(a,b0)*g(a0,b)/g(a0,b0)*exp(D(a,b)), with numerical reference a0=44.5 and b0=22.5. At reference age or BMI, D is zero and the corresponding inherited mean curve is preserved exactly. The total legacy mean log cross-ratio is D, rather than D plus the inherited model's own log interaction. Source age/BMI main effects are removed before transfer; the total mean does not reproduce the full Tromso ratio table because its reference-line curves remain inherited.

Before any freeze, execution or result access, scientific review identified that the initial overlay draft g*exp(D) would add D to the arithmetic baseline's already nonzero log cross-ratio. The builder selected the replacement formula above for clearer source-estimand alignment. The superseded unexecuted draft is preserved outside the final candidate in builder/drafts/overlay_reviewdraft. This was an algebraic review correction, not an output-selected model revision.

D is bilinearly interpolated at ages 44.5,54.5,64.5,74.5,84.5 and BMI 22.5,27.5,32.5, with boundary clamping. Those representative values are assumptions, especially for open-ended bins. The reference-line curves continue globally even where D is clamped; this extrapolation is also assumed. Transfer fraction 1 is fixed before any replay; no sweep or output-based tuning is planned. Both sexes retain their observed interaction departures. All existing numerical main-effect, level, regularization, residual CV and assay parameters are unchanged, although the structural replacement can change conditional means away from the reference lines, marginal moments and effective BMI coefficients. China-PAR remains qualitative context; its per-SD coefficients do not set a numerical parameter.

The full source adjustment footnote is recorded, with unresolved male education/medication ambiguity, male n9583 in the supplement versus n9341 in main Results, and female age40-49/BMI25-29.9 RD1.24 CI[1.23,1.28] retained exactly. The30 joint cells have28 nonreference CIs and one shared reference per sex. Their covariance is unknown; no independent weighting, ratio-of-ratios CI or posterior uncertainty is fabricated.

The source outcome is nonfasting log serum TG. The generator's constant within-sex lognormal residual variance makes its own conditional geometric and arithmetic ratios equal on the latent legacy_proxy scale, before assay mapping. The unblanked output uses a nonzero-intercept affine map, which does not preserve these ratios or the log cross-ratio. The corresponding legacy-scale property in the source and stability after marginalizing missing adjustment covariates are assumptions. Fasting, laboratory, population, medication, selection and age-support transport remain unresolved. This interaction replacement is a source-informed sensitivity scenario, not a calibrated target effect or causal model.

The intended uses—age association, nonlinear BMI response, and age/BMI/sex subgroups—now have a model capable of age-dependent BMI shape. Absolute subgroup levels, within-bin trajectories, source-to-target transport and inferential validity remain assumption-dependent or unassessed. Added evidence does not establish target analytical accuracy, p-values or clinical utility.

Actual checks are limited to admitted-source extraction/parameter traceability, contracts and static program logic. The builder never imports or executes the generator. Existing Oh/Bansal source contexts and replay definitions are unchanged and can diagnose trade-offs after the controller freezes the candidate. Exact adjusted joint ratios and China-PAR mixed-effects coefficients are explicitly not computable by the available replay operators. Controller source seeds80201-80203 and target seeds80101-80103 are fixed; generated output is not used to tune parameters. Stop after this one candidate; no freeze or target-result inspection is performed by the builder.
'''
(C / 'decision.md').write_text(decision, encoding='utf-8')
write('revision.json', {'reason': 'Newly admitted exact joint source table resolves prior missing-coefficient gap and motivates one bounded interaction departure without target feedback.', 'kind': 'revise', 'addressed_findings': ['Constant within-sex BMI effect in inherited model excludes age-dependent BMI departures.', 'All30 exact Tromso joint ratio points and28 intervals are now available with original estimand context.'], 'remaining_limitations': ['Unsupported adjusted-log-ratio replay and missing source joint covariance.', 'Nonfasting/adjustment/measurement/population transport and assumed interpolation support.', 'No target-outcome-informed parameter fitting or demonstrated analytical utility.']})

# Preserve the three requested estimands; update evidence coverage without claiming calibration.
old_map = read(BASE / 'analysis_evidence.json')
map_assumptions = ['A_shared_source_interpretation', 'A_source_measurement', 'A_transport', 'A_unmeasured', 'A_structure', 'A_oh_table2', 'A_oh_ols', 'A_monte_carlo', 'A_joint_estimand_bridge', 'A_joint_continuity', 'A_joint_transfer', 'A_joint_uncertainty']
gap_text = {
    'estimand': ('Published adjusted joint log ratios are neither the requested working age coefficient, curvature functional nor raw arithmetic subgroup means.', 'The chosen interaction departure addresses only one structural component; target analytical results are unvalidated.'),
    'population': ('Korean families, initially healthy US women, Norwegian adults40+ and Chinese longitudinal cohorts differ from the task population of US adults40-79.', 'Population transport and age restriction are assumptions.'),
    'measurement': ('Nonfasting Tromso serum, fasting source plasma, assay/glycerol handling and target fasting context differ.', 'Time-since-meal adjustment does not establish fasting or assay equivalence.'),
    'selection': ('Tromso excludes TG>10mmol/L and had65%attendance; medication/health/family selections differ among the other sources.', 'Selection can change conditional relationships and residual tails.'),
    'conditioning': ('The exact joint table resolves prior missing ratios but reports category contrasts conditional on extra covariates; category centers and within-bin trajectories are not measured.', 'Bilinear interpolation and integrating unmeasured covariates remain assumptions.'),
    'adjustment': ('Source models include extra lifestyle/metabolic covariates. Male Tromso education/drug adjustment remains inconsistent across supplement rows, footnote and figure descriptions.', 'Source adjusted effects need not equal a reduced age/sex/BMI model.'),
    'scale': ('Tromso ratios concern exponentiated log-TG predictions. China-PAR per-SD mixed-effects scaling remains unresolved. Oh strata have arithmetic/geometric ambiguity.', 'Constant within-sex residual log variance is an explicit legacy-scale model bridge, not established source evidence; the affine unblanked assay map breaks ratio equality.'),
    'joint_distribution': ('The inherited legacy log cross-ratio is replaced with D; reference-age and reference-BMI positive mean curves and residual CV remain inherited. Their global continuation is assumed.', 'The total legacy mean cross-ratio is exp(D), but total source joint ratios are not reproduced because main-effect curves differ. Complete source/target laws remain unidentified.'),
    'uncertainty': ('All28 Tromso CIs are retained, but shared-reference covariance, transport and interpolation uncertainty are unavailable. Sample-count and exact CI anomalies are retained.', 'No posterior surface, contrast CI or inferential calibration is claimed; replay seeds measure only Monte Carlo variation.'),
}
analyses = []
for old in old_map['analyses']:
    old_ids = [x['evidence_id'] for x in old['evidence_links'] if x['evidence_id'].startswith(('E_oh_', 'E_bansal_', 'E_CPAR_'))]
    link_ids = list(dict.fromkeys(old_ids + joint_ids))
    gaps = [{'id': old['id'] + '_' + dimension, 'dimension': dimension, 'description': texts[0], 'consequence': texts[1], 'assumption_ids': map_assumptions} for dimension, texts in gap_text.items()]
    analyses.append({
        'id': old['id'], 'estimand': old['estimand'], 'assessment': 'partial',
        'rationale': 'The requested use is unchanged. Exact Tromso joint cells now supply a numerical surface replacing the inherited legacy mean log cross-ratio, with original reference-age/reference-BMI positive curves retained. This resolves the missing-table gap and permits age-dependent nonlinear BMI behavior; it does not identify the requested target functional. Full transfer, interpolation, global reference-curve continuation and legacy-scale estimand mapping are assumptions; no source/target output has been used for tuning.',
        'assumption_ids': map_assumptions,
        'evidence_links': [{'evidence_id': eid, 'relation': 'component', 'comparisons': {d: 'declared_difference' for d in ['estimand', 'population', 'measurement', 'selection', 'conditioning', 'adjustment', 'scale']}, 'assumption_ids': map_assumptions, 'rationale': 'Exact adjusted joint log-TG ratio supplies a numerical interaction-shape component; it is not a direct report of the target functional.' if eid in joint_ids else 'Inherited source statistic is retained in its original estimand and contributes only partial main-effect, spread or qualitative context; no silent scale conversion is made.'} for eid in link_ids],
        'gaps': gaps,
        'actions': [{'id': old['id'] + '_future_evidence', 'gap_ids': [x['id'] for x in gaps], 'tool': 'none', 'request': 'A future matched fasting source would need raw and log conditional age/BMI/sex effects, within-bin distributions, adjustment details, joint coefficient covariance and assay context to resolve these gaps.', 'status': 'unavailable', 'reason': 'This fixed local-source pilot has zero search/download budget. The already admitted exact supplement is used; no future retrieval or prior failed retrieval is claimed as a current action.'}],
    })
write('analysis_evidence.json', {'schema_version': 1, 'analyses': analyses})

# These are source-evidence algebra/static checks, not generator evaluations.
sys.path.insert(0, str(P))
from cohort_harness.__main__ import validate_bundle
from cohort_harness.lifecycle import _checks, _registry
from cohort_harness.source_checks import run_source_checks
from cohort_harness.source_replay import _check_metadata, _input_task
validation = validate_bundle(B, C)
_registry(B)
plan = read(C / 'source_replay.json')
source_evidence = {x['id']: x for x in evidence['items']}
assumptions = {x['id'] for x in spec['assumptions']}
source_context_counts = {}
for context in plan['contexts']:
    assert set(context['assumption_ids']) <= assumptions
    for check in context['checks']:
        _check_metadata(check, source_evidence, assumptions, context['assumption_ids'])
    _, context_task = _input_task(C, context, read(B / 'task.json'), 20_000_000)
    source_context_counts[context['id']] = context_task['n_rows']
tree = ast.parse(generator)
generate_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'generate')
assert len(generate_node.args.args) == 3
assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {'open', 'eval', 'exec'} for n in ast.walk(tree))
assert all(spec['parameters'][k] == v for k, v in read(BASE / 'model_spec.json')['parameters'].items() if k != 'structure_id')
factors = []
for s in range(2):
    grid = []
    for a in range(5):
        row = []
        for b in range(3):
            v = ratios[s][a][b] / (ratios[s][a][0] * ratios[s][0][b]) * ratios[s][0][0]
            log_v = math.log(ratios[s][a][b]) - math.log(ratios[s][a][0]) - math.log(ratios[s][0][b]) + math.log(ratios[s][0][0])
            assert math.isclose(math.exp(log_v), v, rel_tol=1e-14)
            if a == 0 or b == 0:
                assert abs(log_v) < 1e-14
            row.append(v)
        grid.append(row)
    factors.append(grid)

report = {'scope': 'source_evidence_algebra_and_static_contract_only',
    'contract_validation': validation, 'source_registry_hashes_verified': True,
    'source_replay_metadata_and_covariates_validated': True, 'source_context_rows': source_context_counts,
    'full_replay_plan_attempt': 'Initial _plan call stopped because freeze.json is absent. No freeze or generator execution was attempted. Subsequent checks called _check_metadata and _input_task only; freeze-dependent replay-plan verification remains for controller.',
    'source_replay_contexts_unchanged': all(sha(C / p) == sha(BASE / p) for p in ['source_replay.json', 'source_contexts/oh.csv', 'source_contexts/bansal.csv']),
    'exact_joint_cells': len(cells), 'nonreference_confidence_intervals': 28,
    'original_numeric_parameters_unchanged_except_structure_id': True,
    'crossratio_factors_male_female_age_by_bmi': factors,
    'reference_age_and_bmi_zero_departure': True,
    'mean_structure_algebra_review': 'With D(a,b0)=D(a0,b)=0, m=g(a,b0)*g(a0,b)/g(a0,b0)*exp(D) gives m(a,b0)=g(a,b0), m(a0,b)=g(a0,b), and m(a,b)*m(a0,b0)/(m(a,b0)*m(a0,b))=exp(D). This is a symbolic identity on the legacy scale, not a host generator evaluation; affine unblanked measurement does not preserve it.',
    'superseded_overlay_review': 'Unfrozen/unexecuted initial overlay draft preserved under builder/drafts/overlay_reviewdraft. Algebraic review identified D_total=D_baseline+D_source; the builder replaced it with the reference-line construction before any output access.',
    'generator_imported': False, 'generator_executed': False,
    'observed_preservation_review': 'Static review: generate reads age/sex/BMI/assay; _measurement deep-copies the supplied DataFrame and assigns only tg_mg_dl. No sorting, index reset or row assignment occurs. No runtime behavior or output validity is claimed.',
    'read_boundary': 'Admitted source/task/model/context files only. No source_replays, executions, custodian, target outcomes or target reports read.',
    'analysis_evidence_map': {'requested_uses_preserved': [x['id'] for x in analyses], 'assessment': 'partial', 'new_joint_ratio_links_per_use': 30},
    'input_sha256': {name: sha(C / name) for name in ['evidence.json', 'model_spec.json', 'generator.py', 'source_replay.json', 'source_checks.json', 'analysis_evidence.json']}}
write('static_validation.json', report)
source_checks = run_source_checks(B, C)
assert len(source_checks['checks']) == 36
assert all(x['status'] == 'not_computable' for x in source_checks['checks'])
write('unsupported_source_check_result.json', source_checks)
write('checks.json', {'scope': 'source_only', 'records': [
    {'name': 'contract_and_source_recipe', 'status': 'pass', 'detail': 'validate_bundle, registry hash verification and source_replay._check_metadata/_input_task ran successfully. Initial full _plan stopped for missing freeze.json, as preserved in static report; freeze-dependent verification remains for controller. Program was parsed only; neither generator nor replay was executed.'},
    {'name': 'exact_source_traceability_and_crossratio', 'status': 'pass', 'detail': 'Parsed30 exact admitted joint cells and28 CIs; source-derived interaction factors agree with independent ratio algebra and are zero in log units at reference age/BMI. Symbolic reference-line construction replaces, rather than overlays, legacy-scale log cross-ratio. All inherited numerical scientific parameters except structure label remain fixed.'},
    {'name': 'program_preservation_static_review', 'status': 'pass', 'detail': 'AST signature accepted and code reviewed: observed DataFrame is deep-copied; only tg_mg_dl is assigned. This is static review, not generated-output validation.'},
    {'name': 'unsupported_joint_and_longitudinal_estimands', 'status': 'not_computable', 'detail': 'Actual source-check runner retained36 noncomputable checks:30 adjusted log-TG ratios and6 longitudinal per-SD coefficients. No replacement estimands or arithmetic-means checks were invented.'},
    {'name': 'runtime_scientific_validity', 'status': 'not_computable', 'detail': 'No builder generator execution, source replay, target evaluation or tuning. Controller freeze/execution and separate evaluation remain outstanding.'}],
    'artifacts': [{'path': name, 'sha256': sha(C / name)} for name in ['static_validation.json', 'unsupported_source_check_result.json']]})
_checks(C)
print(json.dumps({'candidate': str(C), 'contract': validation, 'source_cells': 30, 'noncomputable_checks': 36, 'generator_executed': False}, indent=2))

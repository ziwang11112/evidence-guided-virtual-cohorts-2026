"""Source-only declaration/retain build. Never imports or executes generator.py."""
from pathlib import Path
import copy
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from cohort_harness.lifecycle import read_json, sha256, _checks, _revision
from cohort_harness.analysis_evidence import validate_analysis_evidence, summarize_analysis_evidence

E = ROOT / 'work/analysis-evidence-gap-2026-10-29'
BUNDLE = E / 'agent_bundle'
BASE = BUNDLE / 'candidates/baseline'
NEW = BUNDLE / 'candidates/evidence_augmented'
RESEARCH = E / 'research'


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def main():
    assert not (BASE / 'freeze.json').exists(), 'Baseline already frozen; do not change map.'
    assert not NEW.exists(), 'New candidate exists; do not overwrite.'
    task = read_json(BUNDLE / 'task.json')
    evidence = read_json(BASE / 'evidence.json')
    spec = read_json(BASE / 'model_spec.json')
    registry = read_json(BUNDLE / 'registry.json')
    research = read_json(RESEARCH / 'candidate_evidence.json')
    baseline_hashes = {n: sha256(BASE / n) for n in ['generator.py', 'model_spec.json', 'evidence.json']}
    original_items = {v['id']: v for v in evidence['items']}
    assumptions = ['A_shared_source_interpretation', 'A_source_measurement', 'A_transport',
                   'A_unmeasured', 'A_structure', 'A_oh_table2', 'A_oh_ols', 'A_monte_carlo']
    population = 'US noninstitutionalized adults aged 40-79 satisfying this task eligibility; no target outcomes available to the builder.'
    measurement = 'Fasting serum TG in mg/dL, task legacy_proxy glycerol-blanked measurement context; exact source equivalence is an assumption.'
    selection = 'Task eligible complete observed age/sex/BMI rows, morning examination and 8.5 to <24 hours fasting; no outcome-dependent subgroup boundary chosen by builder.'

    def make_analysis(aid, kind, description, exposures, conditioning, adjustment, unit, scale, refs, rationale, statistic_name=None):
        estimand = dict(description=description, kind=kind, outcome='tg_mg_dl', exposures=exposures,
                        conditioning=conditioning, adjustment=adjustment, unit=unit, scale=scale,
                        population=population, measurement=measurement, selection=selection)
        if statistic_name:
            estimand['statistic_name'] = statistic_name
        gap_text = {
            'estimand': ('Source components do not directly report the requested directed conditional functional.',
                         'Matching a marginal correlation, stratum summary or a different coefficient does not identify this estimand.'),
            'population': ('Selected Korean families and initially healthy US women differ from the current 40-79 population; inherited A_transport text describes a broader 20-79 scope.',
                           'Transport and restriction to current ages remain unverified; unchanged inherited wording is not a scope-equivalence claim.'),
            'measurement': ('Fasting duration, plasma/serum matrix and endogenous-glycerol handling differ or are incompletely reported.',
                            'Measurement correspondence cannot be assumed to preserve all conditional associations.'),
            'selection': ('Source medication exclusions, health selection, family sampling, age range and participant response differ.',
                          'Selection may change both conditional relationships and observed subgroup mixtures.'),
            'conditioning': ('Separate age/sex and BMI/sex summaries do not report TG jointly conditional on age, BMI and sex; reverse TG-tertile covariate summaries have the opposite conditioning direction.',
                             'Subgroup conclusions can vary between models compatible with the available component statistics.'),
            'adjustment': ('Available statistics have absent, different or more extensive adjustment than the requested use; some needed covariates are unavailable.',
                           'A conditional effect in a published model need not equal the reduced age/sex/BMI model effect.'),
            'scale': ('Spearman association, reported ambiguous stratum summaries, arithmetic means and regression coefficients represent different scales/functionals.',
                      'No rank correlation, geometric summary or other estimand is converted silently to the requested effect.'),
            'joint_distribution': ('The baseline literature does not identify the full joint TG/age/BMI/sex law or subgroup residual distribution.',
                                   'The inherited additive mean and residual assumptions remain responsible for unreported joint behavior.'),
            'interaction': ('Age-by-BMI-by-sex effect modification and BMI curvature are not jointly identified by the original sources.',
                            'The inherited structural restrictions remain assumptions rather than evidence of absent interaction.'),
            'uncertainty': ('Parameter covariance, joint-cell uncertainty and uncertainty from transport/model structure are unavailable.',
                            'Repeated generated rows or seeds do not constitute clinical evidence precision.')
        }
        gaps = [dict(id=f'{aid}_{dim}', dimension=dim, description=desc, consequence=consequence,
                     assumption_ids=assumptions) for dim, (desc, consequence) in gap_text.items()]
        links = []
        for ref in refs:
            item = original_items[ref]
            comp = dict(estimand='declared_difference', population='declared_difference', measurement='unknown',
                        selection='declared_difference', conditioning='declared_difference',
                        adjustment='declared_match' if set(item['adjustment']) == set(adjustment) else 'declared_difference',
                        scale='declared_match' if item['unit'] == unit and item['kind'] != 'reported_other' else 'declared_difference')
            links.append(dict(evidence_id=ref, relation='component', comparisons=comp,
                              assumption_ids=assumptions,
                              rationale='Original baseline evidence component only. ' + item['applicability']))
        return dict(id=aid, estimand=estimand, assessment='partial',
                    rationale='This map was constructed after the bounded literature retrieval, not as a preregistered search decision. This baseline map links ORIGINAL baseline evidence only. ' + rationale,
                    assumption_ids=assumptions, evidence_links=links, gaps=gaps,
                    actions=[dict(id=f'{aid}_future_evidence', gap_ids=[g['id'] for g in gaps], tool='none',
                                  request='Obtain a matched fasting 40-79 source reporting the requested age/sex/BMI conditional functional with adjustment, measurement, joint-cell context and parameter covariance.',
                                  status='unavailable', reason='The current bundle permits approved local sources but no new literature action: source_queries=0 and source_downloads=0. Six external source-only queries were already completed before map construction; their execution is recorded in the audit log, not claimed by this action.')])

    age_refs = [f'E_oh_{sex}_age_stratum_{j}_tg' for sex in ['male', 'female'] for j in range(1, 6)]
    age_refs += ['E_bansal_spearman_age', 'E_bansal_tertile1_age_mean', 'E_bansal_tertile3_age_mean']
    bmi_refs = [f'E_oh_{sex}_bmi_stratum_{j}_tg' for sex in ['male', 'female'] for j in range(1, 6)]
    bmi_refs += ['E_oh_bmi_age_sex_slope', 'E_bansal_spearman_bmi']
    joint_refs = [f'E_oh_{sex}_tg_mg_dl_mean' for sex in ['male', 'female']]
    joint_refs += [f'E_oh_{sex}_{var}_stratum_{j}_tg' for sex in ['male', 'female'] for var in ['age', 'bmi'] for j in [1, 5]]
    joint_refs += ['E_oh_bmi_age_sex_slope', 'E_bansal_spearman_age', 'E_bansal_spearman_bmi']
    manifest = dict(schema_version=1, analyses=[
        make_analysis('adjusted_age_association', 'ols_coefficient',
                      'Age coefficient in the working arithmetic-scale regression TG ~ age + sex + BMI among eligible adults aged 40-79; this map does not define a survey-weighted estimator.',
                      ['age'], [], ['sex', 'bmi'], 'mg/dL per year', 'Conditional age association in a linear working model, not a causal effect.', age_refs,
                      'Age-stratum TG summaries, marginal Spearman age correlation and age conditional on TG groups do not identify the age coefficient adjusted for sex and BMI.'),
        make_analysis('bmi_curvature', 'reported_other',
                      'Departure from a linear BMI relationship in the conditional arithmetic TG mean after accounting for age and sex.',
                      ['bmi'], [], ['age', 'sex'], 'mg/dL', 'Arithmetic-mean BMI response shape; no unreported quadratic coefficient is supplied.', bmi_refs,
                      'A pooled adjusted BMI slope and separate BMI strata constrain components but do not uniquely identify conditional curvature.',
                      'BMI curvature in conditional arithmetic TG mean'),
        make_analysis('joint_age_bmi_sex_conditional_means', 'mean',
                      'Arithmetic mean TG in joint age-by-BMI subgroups within each sex, or at specified joint age/BMI/sex values, among eligible adults aged 40-79.',
                      [], ['age', 'bmi', 'sex'], [], 'mg/dL', 'Conditional arithmetic TG mean on the original measurement scale.', joint_refs,
                      'Sex marginals and one-dimensional strata do not identify the age-by-BMI-by-sex subgroup mean surface.')
    ])
    validate_analysis_evidence(manifest, task, evidence, spec)
    write(BASE / 'analysis_evidence.json', manifest)
    shutil.copytree(BASE, NEW)
    shutil.copy2(NEW / 'checks.json', NEW / 'inherited_checks.json')
    shutil.copy2(NEW / 'decision.md', NEW / 'inherited_decision.md')
    shutil.copy2(NEW / 'revision.json', NEW / 'inherited_revision.json')
    audit = NEW / 'research_audit'
    audit.mkdir()
    for n in ['candidate_evidence.json', 'source_artifact_manifest.json', 'retrieval_log.md', 'evidence_gap_map.md', 'supplement_retry_log.jsonl']:
        shutil.copy2(RESEARCH / n, audit / n)

    augmented = copy.deepcopy(evidence)
    rsrc = {s['source_id']: s for s in research['sources']}
    for sid, filename in [('Mikkelsen2023_Tromso7', 'PMC10308115.xml'), ('Zhang2026_ChinaPAR', 'PMC13491077.xml')]:
        matches = [a for a in registry['artifacts'] if a['source_id'] == sid and a['path'] == 'sources/' + filename]
        assert len(matches) == 1 and matches[0]['screening'] == 'approved'
        a = matches[0]
        assert sha256(BUNDLE / a['path']) == a['sha256']
        s = rsrc[sid]
        augmented['sources'].append(dict(id=sid, identifier=s['citation'] + ' DOI ' + s['doi'] + '; primary URL ' + s['primary_url'] + '; retrieved XML ' + s['retrieved_xml_url'],
            population=s['population'] + '. ' + s['cohort'] + '. ' + s['design'],
            measurement=json.dumps(s['measurement'], ensure_ascii=False),
            cohort_ids=['Tromso7 2015-2016 Norway'] if sid.startswith('Mikkelsen') else ['China-PAR', 'China MUCA', 'InterASIA China', 'CIMIC China'],
            artifacts=[dict(path=a['path'], sha256=a['sha256'])]))
    cpar = rsrc['Zhang2026_ChinaPAR']
    slope_ids = []
    cpar_adjustment = ['age', 'area', 'region', 'subcohort', 'survey_year', 'education', 'smoking', 'alcohol_drinking', 'physical_activity', 'diet_score', 'glucose', 'systolic_blood_pressure']
    for x in cpar['statistics']:
        if x['kind'] != 'regression_coefficient':
            continue
        sid = 'E_' + x['id']
        slope_ids.append(sid)
        augmented['items'].append(dict(id=sid, source_id='Zhang2026_ChinaPAR', locator=x['locator'],
            variables=['tg_mg_dl', 'bmi'], kind='reported_other',
            statistic_name='Adjusted longitudinal mixed-effects TG coefficient per 1-SD BMI', estimate=x['estimate'],
            unit='mg/dL per 1-SD BMI', uncertainty=dict(kind='ci', low=x['uncertainty']['lower'], high=x['uncertainty']['upper'], level=0.95),
            adjustment=cpar_adjustment,
            selection=f"China-PAR {x['sex']}, {x['age_stratum']}; 83,487 participants total, 217,239 repeated measurements; sex totals 32,822 men/50,665 women; age-stratum n unreported in main table. Before/after age-54 equality convention not resolved.",
            applicability='Raw fasting TG mixed-effects association, not ordinary cross-sectional OLS or an age coefficient. Common-versus-stratum/sex BMI SD normalization is unresolved; no per-kg/m^2 conversion or multiplier is used. Table 3 main Pinteraction column compares sexes; superscript c indicates before/after age interaction P<0.05 for both sexes. No interaction coefficient or covariance extracted. Adjustment extends beyond task covariates, source age strata extend beyond 40-79, and longitudinal-to-cross-sectional/measurement/selection/transport differences remain unresolved. This item updates the evidence record only; generator and model specification are retained.'))
    tromso_ids = ['E_tromso_age_bmi_interaction_context', 'E_tromso_joint_coefficients_missing_context']
    augmented['items'].extend([
        dict(id=tromso_ids[0], source_id='Mikkelsen2023_Tromso7', locator='Results 3.2.3; Methods 2.4-2.5',
             variables=['tg_mg_dl', 'age', 'bmi', 'sex'], kind='contextual', estimate=None, unit='', uncertainty=dict(kind='not_reported'),
             adjustment=['time_since_last_meal', 'physical_activity', 'education', 'smoking', 'lipid_lowering_medication', 'recent_exercise', 'recent_alcohol'],
             selection='Tromso7, age 40+; 20,963 descriptive participants; missing TG or TG >10 mmol/L excluded.',
             applicability='Sex-specific log-TG age-category by BMI-category interaction test: women P<0.001; men P=0.32. These P values are retained textually, not encoded as an effect or exact bound. The latter does not establish zero interaction. Outcome was nonfasting serum TG in mmol/L; 7+ self-reported hours was the fasting comparator. Back-transformed coefficients are adjusted relative log-scale effects, not unadjusted arithmetic means. No fasting transport or interaction magnitude is inferred.'),
        dict(id=tromso_ids[1], source_id='Mikkelsen2023_Tromso7', locator='Supplementary Table 1 referenced in Results 3.2.2-3.2.3; Figure 3; Figure 2 caption; exposed XML media metadata',
             variables=['tg_mg_dl', 'age', 'bmi', 'sex'], kind='contextual', estimate=None, unit='', uncertainty=dict(kind='not_reported'), adjustment=[],
             selection='Five age bands (40-49,50-59,60-69,70-79,80+) by three BMI bands (<25,25-29.9,>=30), separately by sex; reference age40-49/BMI<25.',
             applicability='The 28 nonreference joint adjusted log-TG ratios and 95% CIs are NOT extracted: public supplement retrieval failed; no Figure 3 digitization performed. Supplement metadata path ec58/10308115/fac328bf60fe/Table_1.DOCX, declared size 686738 bytes, is not a successful retrieval. Main results report 9,341 men; Figure 2 caption reports 9,583; both report 10,143 women. Figure 2 describes education/medication as women-only; exact final joint-model implementation requires the missing supplement. Shared-reference covariance, arithmetic subgroup levels, uncertainty and fasting equivalence remain unavailable. Empty adjustment list here means the contextual record does not encode a verified coefficient adjustment set, not that the study was unadjusted.')
    ])
    write(NEW / 'evidence.json', augmented)
    new_manifest = copy.deepcopy(manifest)
    aug_items = {i['id']: i for i in augmented['items']}
    for analysis in new_manifest['analyses']:
        aid = analysis['id']
        analysis['rationale'] = ('Post-retrieval evidence-augmented declaration, not preregistration. Primary model RETAINED without numerical change. '
            'New China-PAR longitudinal standardized-BMI effects and Tromso contextual joint-interaction evidence narrow the missing-evidence description but do not directly identify this requested target functional. '
            'Assessment remains partial; new source items are not added to any parameter provenance. ' + analysis['rationale'])
        selected = slope_ids + tromso_ids
        for eid in selected:
            item = aug_items[eid]
            comparisons = dict(estimand='declared_difference', population='declared_difference', measurement='declared_difference',
                selection='declared_difference', conditioning='declared_difference', adjustment='unknown' if eid.endswith('missing_context') else 'declared_difference', scale='declared_difference')
            analysis['evidence_links'].append(dict(evidence_id=eid, relation='component', comparisons=comparisons,
                assumption_ids=assumptions, rationale=item['applicability']))
        additions = {
            'population': ' New cohorts are Norwegian and Chinese; the China-PAR age strata include ages outside 40-79.',
            'measurement': ' Tromso is nonfasting; time adjustment does not establish fasting equivalence. China-PAR used a 10-hour fast but exact assay/matrix equivalence and glycerol correction remain unresolved.',
            'estimand': ' China-PAR reports BMI coefficients, not the requested age coefficient, curvature parameter or joint arithmetic means. Tromso test P values are not coefficients.',
            'conditioning': ' China-PAR before/after54 slopes lack joint subgroup intercepts; Tromso 28 ratios remain unavailable.',
            'adjustment': ' New studies condition on additional lifestyle/metabolic variables that cannot be directly represented by age/sex/BMI alone; final Tromso covariate implementation is incompletely verified.',
            'scale': ' China-PAR per-SD BMI denominator (common versus stratum/sex-specific) is unresolved; no conversion to raw BMI slope. Tromso back-transformed log effects are not arithmetic means.',
            'selection': ' China-PAR excluded major baseline chronic disease and required follow-up lipids; Tromso excluded TG>10 mmol/L and had 65% attendance.',
            'joint_distribution': ' Neither retrieved source supplies a fully identified reduced conditional TG distribution for current observed predictors.',
            'interaction': ' Published interaction evidence argues against treating absent source terms as proven zero; retained model restrictions are still assumptions. No new interaction magnitude is inserted.',
            'uncertainty': ' China-PAR coefficient CIs are within-source sampling uncertainty, not transport uncertainty; before/after covariance is unavailable. Tromso subgroup CIs and shared-reference covariance are unextracted.'
        }
        for gap in analysis['gaps']:
            gap['description'] += additions[gap['dimension']]
        analysis['actions'][0]['request'] += ' Specifically retrieve the original Tromso Table_1.DOCX and clarify China-PAR BMI z-score denominator, stratum sample sizes, coefficient covariance and adjusted estimand before any quantitative transfer.'
        analysis['actions'][0]['reason'] += ' Public supplement retries were exhausted; exact results and failures are bound in research_audit/retrieval_log.md. No action record is labelled completed.'
    validate_analysis_evidence(new_manifest, task, augmented, spec)
    write(NEW / 'analysis_evidence.json', new_manifest)
    revision = dict(kind='retain', reason='RETAIN: add audited source evidence and analytical-use gap declarations; no quantitative change. Generator.py and model_spec.json remain byte-identical to baseline.',
        addressed_findings=[
            'Original age/BMI marginals, reverse-conditionals and pooled associations do not identify adjusted age effects, BMI curvature or age-by-BMI-by-sex conditional means; baseline map records these limits after retrieval rather than as preregistration.',
            'Added six exact China-PAR longitudinal mixed-effects per-SD BMI TG estimates and their reported 95% CIs, retaining the native scale and adjustment.',
            'Added contextual Tromso interaction evidence and explicit unavailability of 28 subgroup coefficients; no bounded P value is encoded as an effect estimate.',
            'Public source retrieval log and source artifacts are hash-bound; new evidence does not enter parameter_provenance or trigger coefficient tuning.'
        ], remaining_limitations=[
            'China-PAR BMI standardization denominator is unresolved; no raw-BMI slope calibration is justified. Repeated-measure coefficients, omitted adjustment covariates and age-range differences prevent automatic cross-sectional transfer.',
            'Tromso nonfasting adjusted log-TG ratios are not available and would not be unadjusted arithmetic subgroup means; conflicting male model n and final covariate implementation remain unresolved.',
            'Original source measurement, selection, joint-distribution, residual, curvature, interaction and transport assumptions remain; inherited A_transport names ages20-79 whereas the current map/task explicitly names40-79.',
            'No new numerical source replay, generation, target analysis or target-validation claim. Static validation checks representation and references only.'
        ])
    _revision(revision)
    write(NEW / 'revision.json', revision)
    (NEW / 'decision.md').write_text('''# RETAIN — evidence record expanded, quantitative model unchanged

The bounded source-only search found useful joint/conditional evidence, but it does not justify a calibrated numerical update to this generator. `generator.py` and `model_spec.json` are byte-identical to baseline. The six new China-PAR coefficients remain reported mixed-effects associations per 1-SD BMI; the unresolved common-versus-stratum normalization is not replaced by a target SD. Tromso contributes contextual interaction evidence only: its 28 subgroup ratios/intervals could not be retrieved, and no P-value bound is treated as an effect.

All three declared uses remain partially supported: adjusted age association, BMI curvature, and age-by-BMI-by-sex conditional arithmetic means. Additional fasting/nonfasting, log/arithmetic, adjustment, selection, covariance, age-support and transport gaps are explicit. Published evidence is not absent; a complete target conditional distribution is still unestablished. Existing assumptions are referenced without editing the inherited specification; its broader 20-79 transport wording is flagged while the current map describes40-79.

The baseline evidence map was constructed AFTER the literature retrieval using only the original baseline items. It is not a preregistered search decision. Both maps are submitter declarations, not evidence-sufficiency scores. The updated source records do not alter parameter provenance. Retaining a model is a decision against unsupported coefficient transfer, not a validation of the inherited restrictions.

Research artifacts and actual static check outputs are bound in `checks.json`. Inherited source-only artifacts were copied for provenance; their historical checks were not rerun or adopted as newly performed checks. No target outcomes were supplied or inspected. Candidate validation may read the permitted observed-input table only for its contract. No generation, source replay, target analysis or freeze was performed by this builder. Parent review and freeze remain outstanding.
''', encoding='utf-8')
    integrity = dict(scope='source_only_static', generator_executed=False, frozen=False,
        baseline_before=baseline_hashes,
        baseline_after={n: sha256(BASE / n) for n in baseline_hashes},
        augmented={n: sha256(NEW / n) for n in baseline_hashes},
        preserved=dict(generator=(BASE/'generator.py').read_bytes()==(NEW/'generator.py').read_bytes(),
                       model_spec=(BASE/'model_spec.json').read_bytes()==(NEW/'model_spec.json').read_bytes(),
                       original_evidence_prefix=augmented['sources'][:len(evidence['sources'])]==evidence['sources'] and augmented['items'][:len(evidence['items'])]==evidence['items']),
        original_source_count=len(evidence['sources']), new_source_count=len(augmented['sources']),
        original_item_count=len(evidence['items']), new_item_count=len(augmented['items']),
        added_slope_count=len(slope_ids), added_contextual_count=len(tromso_ids),
        revision_contract='passed', assumptions_changed=False, parameter_provenance_changed=False,
        boundary='Only admitted source files, inherited baseline and task contracts inspected; no target table or evaluation results accessed. Observed.csv not manually inspected.')
    assert all(integrity['preserved'].values())
    assert integrity['baseline_before']==integrity['baseline_after']
    write(audit / 'retention_integrity.json', integrity)
    write(audit / 'baseline_analysis_summary.json', summarize_analysis_evidence(manifest, task, evidence, spec))
    write(audit / 'augmented_analysis_summary.json', summarize_analysis_evidence(new_manifest, task, augmented, spec))
    checks = dict(scope='source_only', records=[
        dict(name='retention_bytes_and_original_evidence', status='pass', detail='Compared generator/spec bytes across candidates, rechecked baseline originals and preserved original evidence as an unchanged prefix; see retention_integrity.json. No generator import/execution.'),
        dict(name='analysis_manifest_api_validation', status='pass', detail='Ran validate_analysis_evidence and summarize_analysis_evidence for both maps using strict read_json. These assess declarations/references only, not scientific validity.'),
        dict(name='new_source_registration_hashes', status='pass', detail='Verified both new XML artifacts against curator-approved registry entries and byte hashes; primary source numbers remain native mixed-effects per-SD coefficients.'),
        dict(name='retain_revision_schema', status='pass', detail='Validated kind=retain revision with current lifecycle revision validator; generator/spec unchanged. No freeze performed.'),
        dict(name='bounded_primary_source_extraction', status='pass', detail='Actual six-query retrieval/extraction and supplement failures are recorded in copied research audit logs; six exact source coefficients/CIs plus two contextual records added. No inferred joint ratios.'),
        dict(name='new_numerical_compatibility', status='not_computable', detail='No generator execution or new source replay performed; evidence expansion alone does not establish improved source or target fit.'),
        dict(name='target_validation', status='not_computable', detail='No target outcomes or target feedback accessed; target validity remains unassessed.')
    ], artifacts=[dict(path=p.relative_to(NEW).as_posix(), sha256=sha256(p)) for p in sorted(audit.iterdir()) if p.is_file()])
    write(NEW / 'checks.json', checks)
    _checks(NEW)
    print(json.dumps(integrity, indent=2))


if __name__ == '__main__':
    main()

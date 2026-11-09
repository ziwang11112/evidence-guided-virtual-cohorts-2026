"""Close a verified unit and write aggregate reports; never reads patient/reference rows."""
from pathlib import Path
import collections, datetime, json, statistics
import act

HERE = Path(__file__).resolve().parent
def read(p): return act.read(p)

def main():
    protocol = read(HERE / 'PROTOCOL.json'); bundle = Path(protocol['bundle'])
    source = read(HERE / 'INITIAL_SOURCE_FEEDBACK.json')
    independent_source = read(HERE / 'INITIAL_SOURCE_INDEPENDENT.json')
    independent_target = read(HERE / 'TARGET_INDEPENDENT.json')
    if independent_source['status'] != 'verified' or independent_target['status'] != 'verified':
        raise ValueError('Independent numerical verification not complete')
    seal = read(HERE / 'AUTHOR_SEALED.json')
    if seal['decision'] != 'retain' or len(seal['candidate_freezes']) != 1:
        raise ValueError('This report is for the actual retained one-stage outcome only')
    summary = []
    for evidence_id in sorted({r['evidence_id'] for r in source['records']}):
        rows = [r for r in source['records'] if r['evidence_id']==evidence_id]
        values = [r['generated'] for r in rows if r['status']=='computed']
        summary.append({'evidence_id': evidence_id, 'reported':rows[0]['reported'],
            'reported_ci':rows[0]['reported_uncertainty'], 'computed_repeats':len(values),
            'mean':statistics.mean(values), 'min':min(values), 'max':max(values),
            'max_abs_difference':max(abs(v-rows[0]['reported']) for v in values)})
    target_records, diagnostic_records, use_records, execution_hashes = [], [], [], {}
    for seed in protocol['target_seeds']:
        run = 'initial_target_'+str(seed)
        path = HERE/'actions'/(run+'_generated.result.json')
        response = read(path)
        if response['result']['status']!='success': raise ValueError('Failed analysis retained; report explicitly')
        result = response['result']['result']['result']
        target_records += [dict(seed=seed, **r) for r in result['analyses']]
        diagnostic_records += [dict(seed=seed, **r) for r in result['diagnostics']]
        use = read(HERE/'actions'/(run+'_analysis_use.result.json'))['result']['result']['result']
        use_records.append({'seed':seed,'status':use['status'],'coverage':use['evidence_coverage']['analyses'],
                            'coherence':use['coherence'],'quality':result['quality']})
        execution_hashes[run]=act.sha(bundle/'executions'/run/'execution.json')
    target_summary=[]
    for identifier in [r['id'] for r in protocol['required_analyses']]:
        rows=[r for r in target_records if r['id']==identifier]
        if not all(r['status']=='computed' for r in rows): raise ValueError('Unavailable target analysis must be explicitly handled')
        values=[r['value'] for r in rows]
        target_summary.append({'id':identifier,'unit':rows[0]['unit'],'values':values,
                               'mean':statistics.mean(values),'min':min(values),'max':max(values)})
    result={'schema_version':1,'scope':'source_consistency_and_generated_only_analysis',
        'decision':'retain_initial_no_scientific_revision','source_evaluations':12,'source_rows_per_evaluation':8000,
        'source_groups':4,'source_family':'Soares2019 MEIRU','source_numeric_projections':24,
        'strict_source_semantic_counts':source['strict_semantic_counts'],'source_summary':summary,
        'target_scenario_tables':3,'target_rows_per_table':3000,'target_analysis_calculations':9,
        'target_diagnostic_calculations':len(diagnostic_records),'target_summary':target_summary,
        'target_analysis_records':target_records,'target_diagnostic_records':diagnostic_records,
        'target_use_records':use_records,'execution_receipt_hashes':execution_hashes,
        'independent_source_verification':independent_source['summary'],
        'independent_target_verification':independent_target['summary'],
        'new_clinical_cohorts':0,'reference_data_reads':0,'new_source_downloads':0,'new_discovery_requests':0,
        'calibration_objective_evaluations':0,'unused_source_slots':12,'unused_target_slots':3,
        'limitations':['The same conditional mean structure contains the source slopes; reproducing them is an implementation/source-law consistency check.',
                       'Source SD convention and estimator weighting remain unresolved; numerical projections are assumption-dependent.',
                       'Target demographics, nuisance joint law and source transport remain assumed; no target reference was evaluated.',
                       'Individual dispersion and residual coupling remain unvalidated. Seed variation is not epistemic or transport uncertainty.',
                       'Retaining a candidate does not demonstrate revision benefit, and no comparator superiority was tested.']}
    act.write(HERE/'RESULTS.json',result)
    finish=act.dispatch('finish_retained_initial',{'kind':'finish','final_candidate':'candidates/initial',
        'reason':'Retained after complete source-only feedback and independent recomputation; all three sealed target-scenario outputs analyzed. Source-consistency development only, with no clinical reference or superiority claim.'})
    if finish['status']!='success':raise ValueError('Session did not finish')
    final_session=act.session.verify_session(bundle)
    act.write(HERE/'FINAL_SESSION.json',final_session)
    state=read(HERE/'STATE.json')
    state.update(phase='completed_independently_verified_retained_source_only_model',
                 source_evaluations=12,target_executions=3,target_generated_rows=9000,
                 source_numeric_projections=24,target_analysis_calculations=9,
                 final_decision='retain_initial',clinical_reference_reads=0,
                 generated_target_tables_read=3,
                 new_target_reads_field_interpretation='Clinical reference reads only; generated target-scenario reads are recorded separately.',
                 new_target_reads=False,new_downloads=0,next='Integrate source-replay capability and its limits; further target validation requires a separate admissible protocol.',
                 updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (HERE/'STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    lines=['# Source-conditioned replay: completed result',
           '', '9 November 2026. **The source-to-generator link now runs numerically.** One fresh scientific author constructed a shared source/target generative law, twelve source-law tables supplied all 24 planned numerical relation checks, and the retained generator subsequently delivered three target-scenario tables supporting all nine requested analysis calculations. Independent recomputation verified both stages.',
           '', '**Scope:** developmental source consistency and generated-data analysis, with zero new clinical cohorts and zero reference-outcome reads. This is not a new patient-validation study, a measured gain in target accuracy, or evidence that feedback improved the model.',
           '', '## What was implemented',
           '', 'The new additive `whole_cohort_source_replay_v1` adapter invokes the same frozen program and specification in separately declared source populations. Each source task carries the variables required by its published model. It verifies the sampled BMI standardization before applying the full adjustment model. Strict semantic availability remains separate from an explicitly assumed numerical projection. No clinical slope, level, residual SD or sign was supplied by the host controller.',
           '', 'The author chose four sex/site strata from Soares2019, bounded age and BMI laws, source-informed categorical nuisance margins, and a shared conditional HDL/non-HDL construction with total cholesterol as their sum. All eight reported BMI coefficients enter both source and target branches. Nuisance effects/dependence, residual CV/coupling, approximate level mappings and target mixture are visible assumptions. The target law accepts no individual observations. Positive finite-moment components arise structurally; there is no clipping, rejection search or fitted-outcome selection.',
           '', 'This unit used one fresh scientific constructor, independent infrastructure/scientific review and a separate numerical verifier. Those reviewers are development checks, not a required multi-agent scientific method. The generator ran only through the existing isolated WSL/bubblewrap worker. The author process itself was not OS-isolated.',
           '', '## Source checks',
           '', 'Four source contexts × three fixed seeds × 8,000 rows produced 12 successful tables. All eight primary coefficients were retained, giving 24 computed assumed-lane projections. All 24 strict semantic checks remain unavailable because the paper does not fully resolve weighting and BMI standardization. Numeric replay does not silently certify those missing definitions.',
           '', '| Source relation | Published coefficient | Generated three-draw mean | Generated range |',
           '|---|---:|---:|---:|']
    for row in summary:
        lines.append(f"| {row['evidence_id'].replace('soares2019_','').replace('_',' ')} | {row['reported']:.4f} | {row['mean']:.4f} | {row['min']:.4f} to {row['max']:.4f} |")
    lines += ['', 'Units are mmol/L per BMI SD; replay uses the generated source-sample SD under a declared convention. Published CIs are retained in the figure/JSON and are not acceptance thresholds or person-level SDs. All 24 projections preserve the reported direction; some individual draws fall outside the printed source CI. No draw is excluded. Maximum absolute point discrepancy is 0.0179768 for TC and 0.00811677 for HDL.',
              '', '![Source relationships](figures/source_relationships.png)',
              '', 'The independent verifier rebuilt categorical indicators and standardized BMI, checked full/nuisance rank, and used QR and Frisch–Waugh–Lovell residualization. All 12 runs and 24 coefficients agreed with the primary implementation; maximum absolute estimator difference was 5.89e-15. This verifies arithmetic, not validity of the assumed source law.',
              '', '## Author decision and sealed downstream analyses',
              '', 'After reviewing every source result and the independent audit, the author retained the initial candidate. No new evidence or implementation defect justified changing the scientific law. The unused revision was not exercised. The decision, candidate freeze and all source-report hashes were sealed before any target-scenario generation. All three predeclared target seeds were then executed and analyzed.',
              '', '| Requested analysis | Three-draw mean | Draw range | Unit |',
              '|---|---:|---:|---|']
    for row in target_summary:
        lines.append(f"| {row['id']} | {row['mean']:.6f} | {row['min']:.6f} to {row['max']:.6f} | {row['unit']} |")
    lines += ['', 'Each table has 3,000 complete generated rows. The BMI coefficients adjust for age and sex; the residual correlation adjusts both lipids for age, sex and BMI. All nine requested calculations and 69 descriptive calculations completed. Independent QR/FWL recomputation verified all three tables and nine primary values. Every target table passed the declared row/schema, numerical, full-rank and positive-component checks, with no duplicate measurement rows or HDL>TC violations. No post-generation filtering was used.',
              '', '**These are outputs of the assumed target scenario, not matches against a newly observed target.** Their three-draw ranges describe Monte Carlo variation only. For every table, the two BMI association use-contract assessments are declared partial support; K02-LIPID-RESIDUAL is unassessed with no direct evidence links. The source regression adjusts more variables than the requested age/sex target model, and the target mixture is not empirically identified.',
              '', '## What remains underidentified',
              '', 'An analytic check frozen before generation held all BMI slopes unchanged while varying the assumed HDL/non-HDL component-noise correlation. The implied TC/HDL correlation at fixed source covariates changed from roughly −0.46 to +0.87. This is a model scenario, not another simulated patient experiment, and it is not the pooled target residual correlation. It illustrates why correct slopes alone do not establish a useful joint distribution.',
              '', '![Joint dependence sensitivity](figures/joint_assumption_sensitivity.png)',
              '', 'Changing the unresolved BMI SD convention also changes the raw-unit slopes. Both the source-stratum and pooled descriptive-SD conversions are retained in the frozen analytic sensitivity artifact. These alternatives are not fitted to target outcomes. Measurement correspondence, source selection, nuisance coding and transport continue to require substantive review.',
              '', '## Implementation review, failures and budget',
              '', 'The new adapter and existing semantic tests passed 68 checks, including real isolated execution on invented fixtures. Independent review caught a unit-validation bypass in the new assumed lane before biomedical execution; it was fixed with regression coverage. Review also corrected a revised-submit wrapper type and made interrupted source attempts visible in summary accounting. Documentation was aligned with the actual quota/Gumbel nuisance sampler. These are pre-experiment repairs; frozen old modules and historical receipts were unchanged.',
              '', 'There were no failed biomedical executions or uncomputed planned numeric projections. Strict unavailability is retained as a limitation, not counted as success. Actual scientific budget: one initial construction, zero revisions, 12/24 source evaluations, 3/6 target tables, zero calibration-objective evaluations, zero new searches/downloads. All 96,000 source-law rows and 9,000 target-scenario rows are synthetic numerical draws, not additional empirical participants. Repeated seeds and four strata do not create four independent clinical studies.',
              '', '## Decision and manuscript use',
              '', '**Keep the source-conditioned interface and the simpler retained construction.** This unit supports an auditable capability claim: a scientific Agent can choose a generator that operationalizes study-specific continuous relations, executes the declared source analyses, and yields whole virtual cohorts for downstream analysis while exposing unsupported assumptions. The source-slope agreement is largely expected from the chosen conditional-mean structure and is not a method-superiority result.',
              '', 'Integrate this as a development/capability result alongside the unchanged earlier clinical-utility results. Do not promote it into a new transport validation or a feedback-benefit claim. The next scientific evidence need is information on conditional variability, joint dependence and intended target-population composition; additional draws from this frozen model cannot identify them. A new clinical-reference evaluation needs its own admissible, unexposed protocol.',
              '', 'Reproducible records: [protocol](PROTOCOL.json), [scientific review](SCIENTIFIC_CANDIDATE_REVIEW.md), [source feedback](INITIAL_SOURCE_FEEDBACK.json), [independent source audit](INITIAL_SOURCE_INDEPENDENT.json), [author seal](AUTHOR_SEALED.json), [independent downstream audit](TARGET_INDEPENDENT.json), [aggregate results](RESULTS.json). Individual tables and original third-party sources remain local.']
    (HERE/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'status':final_session['status'],'source_checks':24,'target_primary_checks':9,'target_diagnostics':len(diagnostic_records),'decision':'retain'}))

if __name__=='__main__':main()

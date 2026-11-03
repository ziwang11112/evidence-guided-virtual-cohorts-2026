"""Descriptive extraction of frozen aggregate outputs; no rows or analysis engines."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parents[1]
P = U.parents[1]
R = json.loads((U / 'final_evaluation/RESULTS.json').read_text())
A = json.loads((U / 'independent_audit/RESULTS.json').read_text())
I = json.loads((U / 'publication/UPTAKE_INVENTORY.json').read_text())
IDS = {'CHNS2009': ['E1', 'E2', 'E3'], 'ENSANUT2018': ['Q1_age10', 'Q2_bmi5', 'Q3_bmi5']}
LABELS = {
    'CHNS2009': {'E1': 'BMI, adjusted for age and sex', 'E2': 'Glucose, adjusted for age and sex', 'E3': 'Age, adjusted for sex, BMI and glucose'},
    'ENSANUT2018': {'Q1_age10': 'Age, adjusted for sex, BMI and glucose', 'Q2_bmi5': 'BMI, adjusted for age and sex', 'Q3_bmi5': 'BMI, adjusted for age, sex and glucose'},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ep(c, key):
    return next(x for x in c['endpoints'] if x['id'] == key)


RESULT_SHA = sha(U / 'final_evaluation/RESULTS.json')
MATCHED = A.get('status') == 'matched' and A.get('result_sha256') == RESULT_SHA
STATUS = 'arithmetic_matched_descriptive_interpretation' if MATCHED else 'provisional_pending_matching_independent_audit'
ARMS = []
for case, ends in IDS.items():
    for condition in ['E0', 'E1']:
        cs = [c for c in R['construction_summaries'] if c['case_id'] == case and c['information_condition'] == condition and c['constructor_kind'] == 'agent']
        for key in ends:
            es = [ep(c, key) for c in cs]
            signs = collections.Counter(s for e in es for s in e['seed_directions'])
            ARMS.append({
                'case_id': case, 'information_condition': condition, 'endpoint': key,
                'constructor_count': len(cs),
                'constructor_mean_effect_range': [min(e['mean_effect'] for e in es), max(e['mean_effect'] for e in es)],
                'constructor_mean_absolute_discrepancy_range': [min(e['mean_absolute_discrepancy'] for e in es), max(e['mean_absolute_discrepancy'] for e in es)],
                'all_final_seed_effect_range': [min(e['seed_effect_range'][0] for e in es), max(e['seed_effect_range'][1] for e in es)],
                'seed_direction_counts': dict(signs), 'final_seed_endpoint_count': sum(e['available_values'] for e in es),
                'interpretation': 'Descriptive min/max/count extraction from all five constructor summaries; no inferential interval or clinical replication interpretation.',
            })

ACTIONS = {kind: dict(collections.Counter(c['action'] for c in I['constructions'] if c['constructor_kind'] == kind)) for kind in ['agent', 'statistical']}
UPTAKE = []
for c in I['constructions']:
    UPTAKE.append({k: c[k] for k in ['constructor_id', 'case', 'arm', 'constructor_kind', 'closed_status', 'candidate', 'action', 'operation_use_counts']} | {
        'operations': [{'operation_id': o['operation_id'], 'use': o['use']} for o in c['operations']]})
TOTALS = []
for case in IDS:
    for kind in ['agent', 'statistical']:
        counts = collections.Counter()
        cs = [c for c in I['constructions'] if c['case'] == case and c['constructor_kind'] == kind and c['arm'] == 'E1']
        for c in cs:
            counts.update(c['operation_use_counts'])
        TOTALS.append({'case_id': case, 'constructor_kind': kind, 'information_condition': 'E1', 'constructions': len(cs), 'operation_use_counts': dict(counts)})

CLAIMS = [
    {'id': 'C1', 'status': 'supported_descriptive', 'claim': 'All 24 constructions and all 72 scheduled final slots completed; all 72 successful table contents were distinct.', 'limit': 'Operational completion and arithmetic agreement do not establish clinical validity, source reconstruction or transport.'},
    {'id': 'C2', 'status': 'supported_descriptive', 'claim': 'E1 had smaller constructor-averaged absolute discrepancy for five of six prespecified endpoints; CHNS BMI discrepancy increased.', 'limit': 'Unlike endpoints are not pooled or independent confirmations. No significance test, universal benefit or causal evidence-use mechanism is established.'},
    {'id': 'C3', 'status': 'supported_descriptive', 'claim': 'Direction agreement coexisted with magnitude mismatch: ENSANUT E1 age means were above and BMI means below their sample references.', 'limit': 'Reference intervals provide uncertainty context, not acceptance margins. Seed variation is conditional on fixed laws.'},
    {'id': 'C4', 'status': 'supported_descriptive', 'claim': 'CHNS E1 conditional-age results varied across authors, including a negative mean and two negative seeds for A03.', 'limit': 'This relationship was not directly supplied by the CHNS packet; the arm-average decrease in discrepancy does not establish uniform recovery.'},
    {'id': 'C5', 'status': 'supported_descriptive', 'claim': 'Statistical and Agent constructions had endpoint-specific ordering; statistical E1 CHNS glucose and ENSANUT conditional BMI had smaller discrepancies than every corresponding Agent.', 'limit': 'One fixed statistical specification per arm versus five Agent contexts, with different uptake, cannot establish broad method superiority.'},
    {'id': 'C6', 'status': 'supported_process', 'claim': 'Seven Agent retain, thirteen Agent initial_final and four statistical initial_final decisions occurred; no feedback-driven scientific revision occurred.', 'limit': 'Retention after feedback is not a revision gain; analytic drafting without executed feedback is not a correction-loop experiment.'},
    {'id': 'C7', 'status': 'supported_process', 'claim': 'E1 authors documented constraints, analytic checks or contextual use for all admitted relational operations.', 'limit': 'Operation counts are not independent evidence counts. Checks and constraints use assumed source contexts and do not establish source replay or transport.'},
    {'id': 'X1', 'status': 'unsupported', 'claim': 'The virtual cohorts are equivalent to or clinically interchangeable with the references.', 'limit': 'No equivalence design or margin exists, the references are uncertain, and discrepancy or interval position does not define clinical acceptance.'},
    {'id': 'X2', 'status': 'unsupported', 'claim': 'The Agent discovered a causal biological mechanism, or extra evidence causally produced the discrepancy changes.', 'limit': 'Regressions and assumption-completed laws are not causal identification; the arms contain distinct authored models and uptake decisions.'},
    {'id': 'X3', 'status': 'unsupported', 'claim': 'These are untouched external confirmations or independent clinical replications.', 'limit': 'Both target families were researcher-exposed, source evidence overlaps, and repeated generated tables are fixed-law simulations.'},
    {'id': 'X4', 'status': 'unsupported', 'claim': 'The Agent generally outperforms statistical synthesis or E1 improves every author and endpoint.', 'limit': 'Comparison is asymmetric and endpoint ordering is mixed; CHNS BMI and conditional age supply explicit counterexamples.'},
    {'id': 'X5', 'status': 'unsupported', 'claim': 'Exploratory feedback demonstrated a beneficial scientific model revision.', 'limit': 'No construction made a feedback-to-scientific-revision decision.'},
]

FRAMING = [
    'In two researcher-exposed development families, the frozen evidence-guided whole-cohort procedure completed all 24 constructions and all 72 fixed final slots. Additional available relational information was associated with smaller constructor-averaged absolute discrepancy for five of six prespecified regression coefficients, while the CHNS BMI projection showed a larger discrepancy. These were descriptive comparisons against uncertain selected-sample references.',
    'The results support a feasibility and limitations account of explicit evidence use and assumption-dependent joint-law construction. Author variability, systematic coefficient shifts and conditional-regression counterexamples limit claims of reliable target recovery. They do not support clinical interchangeability, universal improvement, causal mechanism discovery or general Agent superiority.',
    'The four statistical constructions provide fixed, asymmetric comparisons. Endpoint-specific results and different numerical uptake must remain visible; no favorable author, seed, endpoint or case is selected for a general performance claim.',
    'There was no feedback-driven scientific revision: seven Agent constructions retained their original model after feedback, thirteen finalized their initial model without exploratory feedback, and all four statistical constructions finalized their initial model. This allocation therefore evaluates completed constructions and information conditions, not gains from an iterative correction loop.',
]

LIMITS = [
    'CHNS: 95% community-cluster CR1-t intervals for the selected unweighted sample; no national survey or known-population interpretation.',
    'ENSANUT: 399-attempt empirical cluster-resampling stability bands under an equal-cell standard; not national confidence intervals.',
    'Reference intervals are not equivalence margins or acceptance thresholds. Positions relative to them are descriptive only.',
    'Three fixed final seeds characterize simulation under each fixed law, not source-estimation, structural or transport uncertainty, and not additional clinical observations.',
    'No inferential interval or hypothesis test for information contrasts was added.',
    'Five author contexts are not a random sample of all authors or laws; matching A01 labels across arms do not establish a paired design.',
    'The two researcher-exposed development families and overlapping evidence do not provide untouched independent confirmation.',
]

COUNTEREXAMPLES = [
    {'id': 'CE1', 'case_id': 'CHNS2009', 'endpoint': 'E1', 'description': 'Larger E1 arm discrepancy.', 'E0': 0.02037954115369707, 'E1': 0.03155742004126274, 'E1_minus_E0': 0.011177878887565669},
    {'id': 'CE2', 'constructor_id': 'CHNS2009_E1_A03', 'endpoint': 'E3', 'description': 'Negative mean and two negative final seeds despite a positive reference interval.', 'mean': -0.00050934048274624, 'reference': 0.008107035072072662},
    {'id': 'CE3', 'case_id': 'ENSANUT2018', 'endpoint': 'Q1_age10', 'description': 'Every E1 Agent final-seed coefficient exceeded the reference-band upper bound; band position is descriptive, not an acceptance threshold.', 'reference_band_upper': 0.08218524233916669},
    {'id': 'CE4', 'case_id': 'ENSANUT2018', 'endpoints': ['Q2_bmi5', 'Q3_bmi5'], 'description': 'All five E1 Agent constructor means for each endpoint were below the corresponding reference-band lower bound, despite positive final-seed directions; individual seed positions can differ.'},
    {'id': 'CE5', 'description': 'Statistical E1 discrepancies were smaller than every corresponding Agent for CHNS glucose and ENSANUT conditional BMI; larger than every Agent for ENSANUT age.', 'CHNS_glucose_statistical_discrepancy': 0.012021417276057619, 'CHNS_glucose_Agent_arm_discrepancy': 0.024079198100703313, 'ENSANUT_conditional_BMI_statistical_discrepancy': 0.007939960121776552, 'ENSANUT_conditional_BMI_Agent_arm_discrepancy': 0.025649331631140568, 'ENSANUT_age_statistical_discrepancy': 0.07668012355304475, 'ENSANUT_age_Agent_arm_discrepancy': 0.024670383036047308},
]

sources = ['final_evaluation/RESULTS.json', 'independent_audit/RESULTS.json', 'publication/UPTAKE_INVENTORY.json', 'cases/CHNS2009/case_card.json', 'cases/CHNS2009/evaluation.json', 'cases/CHNS2009/source_operations.json', 'cases/ENSANUT2018/case_card.json', 'cases/ENSANUT2018/E1_source_operations.json']
provenance = [{'path': str(U / x), 'sha256': sha(U / x)} for x in sources]
methods = P / 'manuscript/MAIN_STUDY_METHODS_2026-11-03.md'
provenance.append({'path': str(methods), 'sha256': sha(methods)})
out = {
    'schema_version': 'main_result_interpretation_v1', 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': STATUS, 'provisional': not MATCHED,
    'scope': 'Independent descriptive extraction and claim audit of existing aggregate outputs only; no raw patient/generated rows, new models, fitting, revision, selection, experiments or hypothesis tests.',
    'release_sha256': R['release_sha256'], 'result_sha256': RESULT_SHA, 'independent_audit': A, 'provenance': provenance,
    'completion': {k: R[k] for k in ['planned_constructions', 'scheduled_final_slots', 'successful_executions', 'complete_analysis_slots', 'unique_successful_table_contents']},
    'focal_references': {c: {e: R['references'][c][e] for e in es} for c, es in IDS.items()},
    'endpoint_labels': LABELS, 'all_six_prespecified_agent_information_contrasts': R['agent_information_contrasts'],
    'all_24_construction_summaries': R['construction_summaries'], 'descriptive_agent_arm_ranges_and_directions': ARMS,
    'all_four_statistical_references': R['statistical_references'], 'statistical_comparison_limit': R['statistical_comparison_note'],
    'author_decisions': ACTIONS, 'E1_operation_totals': TOTALS, 'all_24_evidence_uptake_classifications': UPTAKE,
    'evidence_count_interpretation': I['interpretation'], 'strongest_supported_claims_and_audit': CLAIMS,
    'explicit_counterexamples': COUNTEREXAMPLES, 'recommended_manuscript_framing': FRAMING, 'uncertainty_limits': LIMITS,
}
(U / 'publication/RESULT_INTERPRETATION.json').write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

lines = ['# Main-study result interpretation and claim audit', '', '**Status: ' + ('independent arithmetic matched' if MATCHED else 'provisional pending matching independent audit') + '.** Descriptive scientific interpretation only.', '',
    f'The independent audit reports {A["checks"]} checks, {A["numeric_statistics_compared"]} numeric comparisons and maximum numerical difference {A["maximum_numeric_difference"]}, with zero errors and zero unavailable slots. Its result hash matches the current result (`{RESULT_SHA}`). This verifies retained-output arithmetic and frozen aggregate mapping, not clinical validity or a new patient-level reanalysis.', '',
    'All 24 constructions and all 72 scheduled final slots are represented: 72 successful executions, 72 complete analyses and 72 distinct successful table contents. Only aggregate outputs and frozen metadata were used. No row table was inspected and no new experiment, hypothesis test, model fitting, revision or selection was performed.', '',
    '## Prespecified information contrasts', '',
    "For each endpoint, E1 minus E0 compares arm means of each constructor's mean absolute discrepancy over three fixed final seeds. Each Agent arm contains five constructors, all complete. A negative difference indicates a smaller discrepancy from the sample-reference point estimate. It does not establish equivalence, clinical interchangeability, significance or causal mechanism. Information-condition E1 and CHNS endpoint E1 are distinct labels.", '',
    '| Case / endpoint | Coefficient | Unit | E0 discrepancy | E1 discrepancy | E1 − E0 |', '|---|---|---|---:|---:|---:|']
for c in R['agent_information_contrasts']:
    lines.append(f'| {c["case_id"]} / {c["endpoint"]} | {LABELS[c["case_id"]][c["endpoint"]]} | {c["unit"]} | {c["arms"]["E0"]["mean_constructor_mean_absolute_discrepancy"]!r} | {c["arms"]["E1"]["mean_constructor_mean_absolute_discrepancy"]!r} | {c["E1_minus_E0_mean_absolute_discrepancy"]!r} |')
lines += ['', 'Five of six contrasts favored E1 descriptively. CHNS BMI is the counterexample among the prespecified endpoints: discrepancy increased by 0.011177878887565669 percentage points per kg/m². Unlike coefficients are not pooled; five of six is not an independence claim or a hypothesis test. Distinct authors and their completion/transport assumptions contribute to the information conditions, so this comparison does not isolate an algorithmic component.', '',
    '## Sample references and uncertainty', '', '| Case / endpoint | Reference coefficient | Reference lower | Reference upper | Unit |', '|---|---:|---:|---:|---|']
for case, ends in IDS.items():
    for key in ends:
        e = R['references'][case][key]
        lines.append(f'| {case} / {key} | {e["value"]!r} | {e["interval"]["lower"]!r} | {e["interval"]["upper"]!r} | {e["unit"]} |')
lines += ['', 'CHNS intervals are 95% community-cluster CR1-t intervals for the selected, unweighted age-35–74 analytical sample. ENSANUT bands come from the prespecified 399-attempt cluster-resampling stability procedure for the age-25–79 equal-cell analytical standard; they are not national confidence intervals. All six reference intervals are positive, but remain uncertain sample estimates. They are neither population constants nor equivalence/acceptance bounds.', '',
    'ENSANUT scales age per 10 years, BMI per 5 kg/m² and glucose per 10 mg/dL where applicable. CHNS uses raw age/BMI scales and glucose in mmol/L. Selection and measurement rules also differ; cross-case effects must not be pooled.', '',
    '## Direction, magnitude and author variability', '', '| Case / endpoint | Arm | Range of five constructor means | Range of five constructor mean absolute discrepancies | Positive / negative seed coefficients |', '|---|---|---|---|---|']
for x in ARMS:
    lines.append(f'| {x["case_id"]} / {x["endpoint"]} | {x["information_condition"]} | {x["constructor_mean_effect_range"][0]!r} to {x["constructor_mean_effect_range"][1]!r} | {x["constructor_mean_absolute_discrepancy_range"][0]!r} to {x["constructor_mean_absolute_discrepancy_range"][1]!r} | {x["seed_direction_counts"].get("positive", 0)} / {x["seed_direction_counts"].get("negative", 0)} of 15 |')
lines += ['', 'These ranges include all five authors; 15 final seeds per arm are conditional simulations, not clinical replications. Ranges are not confidence intervals and do not propagate source-estimation, structural or transport uncertainty. Author labels reused across arms do not define a paired comparison.', '',
    'CHNS E1 BMI means were 0.012399970129407514–0.04575656720989321, all below the reference 0.05494608227224506. Every E1 BMI seed was positive, so direction agreement did not prevent worse aggregate magnitude discrepancy. E1 glucose means varied from 0.36336253385170453 to 0.41418940890722056 against 0.4020933879135471, despite the smaller arm discrepancy.', '',
    'CHNS E1 conditional-age means ranged from −0.00050934048274624 to 0.007393436157991897 against 0.008107035072072662. A03 retained a negative mean and two negative final seeds. The arm-average decrease in discrepancy therefore did not imply uniform directional recovery. The CHNS packet did not supply this conditional age relationship; Pani was absent from both conditions. Each modeled age value remains an assumption-dependent consequence.', '',
    'All ENSANUT E1 Agent final-seed focal coefficients were positive. E1 age means were 0.0977687165339455–0.1024516279586996 against 0.07513235976455014; every final age seed exceeded the reference-band upper bound 0.08218524233916669. BMI means were 0.05645919759096775–0.06251504411793557 before glucose adjustment and 0.02499659222497035–0.04209058466452136 after adjustment, against 0.08364283892711358 and 0.05663753525952589. All five constructor means for each BMI endpoint were below its reference-band lower bound. Interval position describes mismatch and does not define a pass/fail rule or test the arm contrast.', '',
    'Source-analogous CHNS BMI/glucose and ENSANUT age/BMI projections were available under E1, with target values withheld. ENSANUT conditional BMI (Q3) was not supplied or algebraically identified by the packet. Its smaller E1 discrepancy is not discovery of a relationship or evidence of mediation: completion and transport assumptions determine the joint conditional projection.', '',
    '## Statistical references and asymmetric comparison', '',
    'Every statistical construction and focal endpoint is shown below. Statistical values are over three seeds; Agent values are arm means over five constructors. One fixed statistical specification per case/condition versus five independently authored Agent models is a descriptive, asymmetric comparison, not a general superiority experiment.', '',
    '| Statistical constructor / endpoint | Statistical mean coefficient | Statistical discrepancy | Agent arm discrepancy |', '|---|---:|---:|---:|']
for c in R['statistical_references']:
    for e in c['endpoints']:
        contrast = next(x for x in R['agent_information_contrasts'] if x['case_id'] == c['case_id'] and x['endpoint'] == e['id'])
        av = contrast['arms'][c['information_condition']]['mean_constructor_mean_absolute_discrepancy']
        lines.append(f'| {c["constructor_id"]} / {e["id"]} | {e["mean_effect"]!r} | {e["mean_absolute_discrepancy"]!r} | {av!r} |')
lines += ['', 'Under E1, statistical CHNS glucose discrepancy was 0.012021417276057619, below every corresponding Agent discrepancy (arm mean 0.024079198100703313). Statistical ENSANUT conditional-BMI discrepancy was 0.007939960121776552, also below every corresponding Agent discrepancy (arm mean 0.025649331631140568). Conversely, statistical ENSANUT E1 age had mean −0.0015477637884946105 and discrepancy 0.07668012355304475, larger than every corresponding Agent discrepancy (arm mean 0.024670383036047308). These are endpoint-specific orderings for the delivered constructions.', '',
    'Numerical uptake also differed: ENSANUT E1 Agents constrained two Jansen projections and the Pani age projection; the statistical specification constrained only the two Jansen projections, keeping the Pani age slope and eight age-band quantities as context because source individual dispersion, source age law and original survey weighting were unbound. This describes different evidence-use decisions; it does not identify the cause of performance differences.', '',
    '## Evidence use and absence of scientific revision', '',
    'All E0 constructions had zero admitted relational operations. E1 operation counts are declared, reviewed uses, not independent evidence counts or weights. An analytic check need not match its source value, and a constraint remains qualified by the assumed source-context law.', '',
    '| Constructor | Model constraints | Analytic checks | Context only | Declined classification | Decision |', '|---|---:|---:|---:|---:|---|']
for c in I['constructions']:
    if c['arm'] == 'E1':
        v = c['operation_use_counts']
        lines.append(f'| {c["constructor_id"]} | {v["model_constraint"]} | {v["analytic_check"]} | {v["context_only"]} | {v["declined"]} | {c["action"]} |')
lines += ['', 'CHNS A01/A02/A04 constrained both Jansen projections, checked Bao Pearson and retained MIND Spearman as context. A03 constrained MIND Spearman and checked both Jansen projections plus Bao Pearson. A05 constrained Jansen BMI and MIND Spearman, checking Jansen glucose and Bao Pearson. The statistical specification constrained all four. ENSANUT Agents constrained three projections each; A02/A03/A05 checked all eight Pani age-band means, while A01/A04 kept all eight as context. No record used the explicit `declined` classification, although context-only records can explain declining numerical use.', '',
    'Across all 24 constructions, seven Agent decisions were `retain`, thirteen Agent decisions were `initial_final`, and four statistical decisions were `initial_final`. Every selected candidate was the initial candidate. No feedback-driven scientific revision occurred. Retention after feedback cannot substantiate revision gains, and unexecuted analytic drafting is not a feedback-to-revision experiment.', '',
    'The cases share Jansen/Lifelines evidence and measurement guidance. Within-source margins, projections and converted units are not independent replications; Pani age slope and bands share one study. Source estimator uncertainty is not individual dispersion, and unit conversion adds no independent evidence. Source-to-target selection, assays, serum/plasma, ancestry and distributional assumptions remain unresolved. Target-table source replay was unavailable.', '',
    '## Claim audit and recommended manuscript framing', '', '| Claim | Assessment |', '|---|---|']
for c in CLAIMS:
    lines.append(f'| {c["claim"]} | {c["status"]}: {c["limit"]} |')
lines += ['', 'Recommended Results/Discussion wording:', '']
for s in FRAMING:
    lines += [s, '']
lines += ['Retain all six contrasts, every constructor, all four statistical references, the CHNS BMI/age counterexamples and ENSANUT direction/magnitude mismatch. The 27 CHNS and 28 ENSANUT diagnostics remain in the common aggregate evaluation; focal contrasts do not establish whole-distribution recovery. Both target families were previously exposed to researchers; fresh author contexts do not restore untouched validation. Arithmetic agreement is separate from scientific and clinical validation.', '',
    '## Complete constructor ledger', '', 'Each entry is copied from the frozen summaries: mean coefficient, actual range over seeds 5101/5102/5103, mean absolute discrepancy, and seed signs in that order. Ranges are not confidence intervals. No favorable author or seed is selected. The companion JSON retains full numeric precision and operation classifications.', '']
for case in IDS:
    lines += ['### ' + case, '', '| Constructor / endpoint | Mean coefficient | Final-seed range | Mean absolute discrepancy | Seed directions |', '|---|---:|---|---:|---|']
    for c in R['construction_summaries']:
        if c['case_id'] != case:
            continue
        for e in c['endpoints']:
            directions = ', '.join('+' if s == 'positive' else '-' if s == 'negative' else s for s in e['seed_directions'])
            lines.append(f'| {c["constructor_id"]} / {e["id"]} | {e["mean_effect"]!r} | {e["seed_effect_range"][0]!r} to {e["seed_effect_range"][1]!r} | {e["mean_absolute_discrepancy"]!r} | {directions} |')
    lines.append('')
lines += ['## Provenance', '', f'Frozen release SHA-256: `{R["release_sha256"]}`. Result SHA-256: `{RESULT_SHA}`. Independent audit code SHA-256: `{A["audit_code_sha256"]}`. The companion JSON records source hashes, copies all six contrasts/all 24 summaries, and binds the audit status.', '',
    'Inputs: `final_evaluation/RESULTS.json`; `independent_audit/RESULTS.json`; `publication/UPTAKE_INVENTORY.json`; frozen case cards and operator metadata; `manuscript/MAIN_STUDY_METHODS_2026-11-03.md`. No source acquisition or patient-level analysis was performed.', '']
(U / 'publication/RESULT_INTERPRETATION.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'status': STATUS, 'provisional': not MATCHED, 'constructions': len(R['construction_summaries']), 'contrasts': len(R['agent_information_contrasts']), 'statistical_references': len(R['statistical_references']), 'actions': ACTIONS}, indent=2))

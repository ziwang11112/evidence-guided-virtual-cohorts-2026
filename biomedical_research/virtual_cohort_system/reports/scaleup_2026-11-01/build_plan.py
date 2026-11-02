"""Build a non-executable prospective inventory; never run scientific code."""
from pathlib import Path
import hashlib
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name('campaign_plan.json')
assert not OUT.exists(), 'Preserve the existing plan; create an explicit revision.'
SEEDS = [2101, 2102, 2103]
TOPICS = ['adiposity_glycemia', 'lipids_metabolism', 'measured_renal_biomarkers', 'inflammatory_or_hematological']
cohorts = [dict(cohort_slot=f'K{i+1:02d}', intended_topic=topic, wave='A' if i < 2 else 'B', actual_case_id=None,
                study_family=None, admission_status='unassigned', reference_exposure_status='unassessed',
                evidence_packet=None, task_contract=None, analysis_plan=None, authorized_release=None)
           for i, topic in enumerate(TOPICS)]
slots = []
for cohort in cohorts:
    for arm, constructions in [('agent_evidence_guided', [f'A{i:02d}' for i in range(1, 6)]),
                               ('statistical_reference', ['S01'])]:
        for construction in constructions:
            for stage in ['initial', 'final']:
                for seed in SEEDS:
                    slots.append(dict(slot_id=f"{cohort['cohort_slot']}_{construction}_{stage}_{seed}",
                                      cohort_slot=cohort['cohort_slot'], wave=cohort['wave'], method_arm=arm,
                                      construction_id=construction, stage=stage, seed=seed, rows=5000,
                                      evidence_access='case_admitted_external_packet_only',
                                      status='planned_not_released', candidate_hash=None,
                                      execution_id=None, output_hash=None, retained_from=None))
counts = Counter(s['method_arm'] for s in slots)
waves = Counter(s['wave'] for s in slots)
assert len(slots) == len({s['slot_id'] for s in slots}) == 144
assert counts == {'agent_evidence_guided': 120, 'statistical_reference': 24}
assert waves == {'A': 72, 'B': 72}
plan = dict(
    campaign_id='biomedical_scaleup_2026-11-01', campaign_status='design_only', execution_enabled=False,
    design_sha256=hashlib.sha256((ROOT/'docs/SCALED_EXPERIMENT_CAMPAIGN_2026-11-01.md').read_bytes()).hexdigest(),
    entry_regime='whole_cohort_no_individual_input', cohorts=cohorts, slots=slots,
    budget=dict(new_candidate_family_ceiling=6, new_primary_study_deep_read_ceiling=12,
                cohorts=4, minimum_intended_distinct_study_families=3,
                agent_constructions_per_cohort=5, statistical_constructions_per_cohort=1,
                source_feedback_rounds_per_construction=1, seeds=SEEDS, rows_per_table=5000,
                max_agent_design_feedback_turns=40, target_table_slots=144,
                primary_analyses_per_cohort=3, maximum_secondary_analyses_per_cohort=2,
                extra_simulation_calibration_calls=0,
                download_budget_policy='Preserve existing cumulative 500 MiB and single-file 200 MiB ceilings; verify ledger before acquisition.',
                paid_api=False, training=False, hpc=False, new_scheduler=False,
                hard_start_cutoff='2026-11-14 America/Chicago'),
    required_release=['all_case_ids_resolved', 'exposure_and_overlap_review', 'applicable_evidence_admitted',
                      'scientific_use_criteria_frozen', 'reference_arm_specified', 'case_adapters_reviewed',
                      'campaign_orchestrator_reviewed', 'global_contracts_frozen', 'separate_target_access_gate'],
    retention_policy='Unchanged final scientific bytes link to initial outputs; no duplicate execution or independent-evidence credit.',
    wave_gate='Stop expansion if neither A case meets its prospectively defined quantitative-use bundle, or interpretation is invalidated; no retrospective threshold.',
    counting_policy='Cohorts, authoring contexts, model identities, fit instances, seed draws, slot labels and unique output hashes remain separate.',
    counts=dict(planned_cohorts=4, admitted_cohorts=0, planned_agent_constructions=20,
                planned_statistical_constructions=4, maximum_statistical_fit_instances=8,
                planned_candidate_stages=48, planned_slots=144,
                attempted_slots=0, successful_slots=0, failed_slots=0, not_run_slots=144,
                retained_aliases=0, unique_outputs=0),
    scope='Planning inventory only. No cohort is admitted, no runner is implemented by this file, and no generator or evaluator may execute from it.')
OUT.write_bytes((json.dumps(plan, indent=2)+'\n').encode('utf-8'))
print(json.dumps({'plan':str(OUT), 'execution_enabled':False, 'counts':plan['counts'], 'wave_slots':dict(waves)}))

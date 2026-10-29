"""Compact existing declarations and run static validation, never execution/freeze."""
from pathlib import Path
import concurrent.futures
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from cohort_harness.lifecycle import read_json, sha256, _checks, _revision
from cohort_harness.analysis_evidence import summarize_analysis_evidence

E = ROOT / 'work/analysis-evidence-gap-2026-10-29'
BUNDLE = E / 'agent_bundle'
NEW = BUNDLE / 'candidates/evidence_augmented'
AUDIT = NEW / 'research_audit'


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


task = read_json(BUNDLE / 'task.json')
spec = read_json(NEW / 'model_spec.json')
original_joint_refs = {
    'E_oh_male_tg_mg_dl_mean', 'E_oh_female_tg_mg_dl_mean',
    'E_oh_male_age_stratum_3_tg', 'E_oh_female_age_stratum_3_tg',
    'E_oh_male_bmi_stratum_3_tg', 'E_oh_female_bmi_stratum_3_tg',
    'E_oh_bmi_age_sex_slope'
}
summaries = {}
for name in ['baseline', 'evidence_augmented']:
    p = BUNDLE / 'candidates' / name
    evidence = read_json(p / 'evidence.json')
    items = {x['id']: x for x in evidence['items']}
    manifest = read_json(p / 'analysis_evidence.json')
    for analysis in manifest['analyses']:
        gaps = {g['dimension']: g for g in analysis['gaps']}
        if 'estimand' in gaps:
            gaps['joint_distribution']['description'] += ' ' + gaps['estimand']['description'] + ' ' + gaps['interaction']['description']
            analysis['gaps'] = [g for g in analysis['gaps'] if g['dimension'] not in ['estimand', 'interaction']]
        aid = analysis['id']
        if aid == 'joint_age_bmi_sex_conditional_means':
            retained = [l for l in analysis['evidence_links'] if l['evidence_id'] in original_joint_refs or l['evidence_id'].startswith(('E_CPAR_', 'E_tromso_'))]
            present = {l['evidence_id'] for l in retained}
            template = next(l for l in analysis['evidence_links'] if l['evidence_id'].startswith('E_oh_') and 'stratum' in l['evidence_id'])
            import copy
            for eid in sorted(original_joint_refs - present):
                entry = copy.deepcopy(template)
                entry['evidence_id'] = eid
                retained.append(entry)
            analysis['evidence_links'] = retained
        if name == 'evidence_augmented':
            analysis['evidence_links'] = [l for l in analysis['evidence_links'] if not (
                (aid in ['adjusted_age_association', 'joint_age_bmi_sex_conditional_means'] and l['evidence_id'].startswith('E_CPAR_') and l['evidence_id'].endswith('_overall')) or
                (aid == 'adjusted_age_association' and l['evidence_id'] == 'E_tromso_joint_coefficients_missing_context') or
                (aid == 'bmi_curvature' and l['evidence_id'].startswith('E_tromso_')))]
        for link in analysis['evidence_links']:
            item = items[link['evidence_id']]
            if item['source_id'] == 'Zhang2026_ChinaPAR':
                link['rationale'] = 'Native longitudinal per-SD BMI association; a component only. Shared gaps cover scaling, adjustment, transport and the different requested functional. No parameter update.'
            elif item['source_id'] == 'Mikkelsen2023_Tromso7':
                link['rationale'] = 'Contextual joint-model information only; no extracted arithmetic subgroup effect or calibrated interaction magnitude. Shared gaps remain unresolved.'
            elif item['kind'] == 'reported_other':
                link['rationale'] = 'Original baseline stratum evidence only; arithmetic/geometric ambiguity and one-dimensional conditioning remain unresolved under A_oh_table2.'
            elif item['kind'] == 'spearman_correlation':
                link['rationale'] = 'Original marginal rank correlation; it is not an adjusted slope or a joint conditional mean.'
            elif item['variables'] == ['age']:
                link['rationale'] = 'Original age summary conditional on TG group; the conditioning direction is opposite to the requested TG relationship.'
            elif item['kind'] == 'ols_coefficient':
                link['rationale'] = 'Original pooled age/sex-adjusted BMI slope; it does not identify age slopes, curvature or joint mean levels.'
            else:
                link['rationale'] = 'Original sex-specific TG marginal mean; it supplies a component but not the requested joint conditional mean.'
        for action in analysis['actions']:
            action['gap_ids'] = [g['id'] for g in analysis['gaps']]
    write(p / 'analysis_evidence.json', manifest)
    summary = summarize_analysis_evidence(manifest, task, evidence, spec)
    summaries[name] = dict(analyses=len(manifest['analyses']), links=sum(len(a['evidence_links']) for a in manifest['analyses']),
                           gaps=sum(len(a['gaps']) for a in manifest['analyses']), actions=sum(len(a['actions']) for a in manifest['analyses']))
    write(AUDIT / ('baseline_analysis_summary.json' if name == 'baseline' else 'augmented_analysis_summary.json'), summary)


def validate(name):
    command = [sys.executable, '-m', 'cohort_harness', 'validate', '--bundle', str(BUNDLE), '--candidate', name]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    return dict(candidate=name, command=command, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(validate, ['baseline', 'evidence_augmented']))
report = dict(scope='source_only_static_validation', results=results, declarations=summaries,
              generator_executed=False, source_replay_performed=False, freeze_performed=False,
              observation_scope='CLI contract validation reads permitted observed-input columns only; no row analysis or target outcomes.')
write(AUDIT / 'candidate_cli_validation.json', report)
assert all(x['exit_code'] == 0 for x in results), report
for name in ['generator.py', 'model_spec.json']:
    assert (BUNDLE/'candidates/baseline'/name).read_bytes() == (NEW/name).read_bytes()
assert not (NEW/'freeze.json').exists()
assert not (BUNDLE/'candidates/baseline/freeze.json').exists()
_revision(read_json(NEW/'revision.json'))
checks = read_json(NEW/'checks.json')
checks['records'] = [r for r in checks['records'] if r['name'] != 'candidate_cli_validation']
checks['records'].append(dict(name='candidate_cli_validation', status='pass',
    detail='Both current cohort_harness validate CLI calls exited0 and reported valid program contracts, generator_executed=false and scientific_validity=not_assessed. Results bound in research_audit/candidate_cli_validation.json.'))
checks['artifacts'] = [dict(path=p.relative_to(NEW).as_posix(), sha256=sha256(p)) for p in sorted(AUDIT.iterdir()) if p.is_file()]
write(NEW/'checks.json', checks)
_checks(NEW)
print(json.dumps(report, indent=2))

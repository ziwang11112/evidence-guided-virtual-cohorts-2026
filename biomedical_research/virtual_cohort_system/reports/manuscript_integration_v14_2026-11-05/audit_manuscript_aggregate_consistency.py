"""Manuscript/aggregate consistency audit only; never reads patient-like tables.

This is not a scientific rerun. It reads frozen evaluation JSON, source-use counts,
the already-completed independent numerical review, and manuscript text.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

BASE = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
OUT = BASE / 'work/manuscript_integration_v14_2026-11-05'
DRAFT = BASE / 'manuscript/DRAFT_v0_14.md'
PRIOR = BASE / 'manuscript/DRAFT_v0_13_1.md'
GAPS = BASE / 'manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md'
CROSS = BASE / 'work/evidence_use_cross_task_2026-11-05'

def read(path):
    return path.read_text(encoding='utf-8-sig')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

draft = read(DRAFT)
prior = read(PRIOR)
gaps = read(GAPS)
results = json.loads(read(CROSS / 'evaluation/RESULTS.json'))
uses = json.loads(read(CROSS / 'evaluation/EVIDENCE_USAGE_SUMMARY.json'))
numerical = json.loads(read(CROSS / 'review/INDEPENDENT_NUMERICAL_REVIEW.json'))
checks = []

def check(name, passed, evidence):
    checks.append({'check': name, 'status': 'PASS' if passed else 'FAIL', 'evidence': evidence})

def table(text, label):
    start = text.index('**Table ' + label + '.')
    section = text[start:]
    lines = section.splitlines()
    rows = []
    started = False
    for line in lines:
        if line.startswith('|'):
            started = True
            rows.append([v.strip() for v in line.strip('|').split('|')])
        elif started:
            break
    return rows

def norm_number(text):
    return text.replace('\u2212', '-')

slots = results['all_final_slots']
analyses = [x for slot in slots for x in slot['analyses']]
diagnostics = [x for slot in slots for x in slot['diagnostics']]
outputs = analyses + diagnostics
inventory = {
    'authors': len(results['authors']),
    'families': results['reference_families'],
    'final_slots': len(slots),
    'distinct_hashes': len({slot['table_sha256'] for slot in slots}),
    'final_rows': sum(slot['n'] for slot in slots),
    'successful_final_slots': sum(slot['execution_status'] == 'success' for slot in slots),
    'physical_attempts': results['physical_attempts'],
    'primary_outputs': len(analyses),
    'primary_same_direction': sum(x['generated_direction'] == x['reference_direction'] for x in analyses),
    'all_outputs': len(outputs),
    'matched': sum(x['comparison_status'] == 'computed' for x in outputs),
    'unmatched': sum(x['comparison_status'] == 'unavailable' for x in outputs),
    'retained_initial_laws': sum(x['decision'] == 'retain' and len(x['initial_and_revision_freezes']) == 1 for x in results['authors']),
    'source_checks': sum(x['source_check_count'] for x in uses),
    'unique_originals': len({source for x in uses for source in x['source_ids']}),
    'paper_uses': sum(len(x['source_ids']) for x in uses),
    'retrieval_queries': sum(x['gateway_usage']['queries'] for x in uses),
    'retrieval_downloads': sum(x['gateway_usage']['downloads'] for x in uses),
}
expected_inventory = dict(authors=6, families=2, final_slots=18, distinct_hashes=18,
    final_rows=54000, successful_final_slots=18, physical_attempts=24, primary_outputs=54,
    primary_same_direction=54, all_outputs=513, matched=324, unmatched=189,
    retained_initial_laws=6, source_checks=132, unique_originals=8, paper_uses=22,
    retrieval_queries=7, retrieval_downloads=1)
check('Q5 denominators and inventory', inventory == expected_inventory, inventory)
check('Fixed final seeds and sizes', all(slot['seed'] in (9101, 9102, 9103) and slot['n'] == 3000 for slot in slots),
      'All 18 aggregate slot records use seeds 9101–9103 and n=3000.')
check('Existing numerical audit matches exact evaluation JSON',
      numerical['binding']['evaluation_RESULTS_sha256'] == sha(CROSS / 'evaluation/RESULTS.json'),
      {'reviewed_evaluation_sha256': sha(CROSS / 'evaluation/RESULTS.json'),
       'largest_prior_reconstruction_difference': numerical['findings']['largest_absolute_reconstruction_difference']})

label_map = {
    'HbA1c adjusted age': 'Q1_age10', 'HbA1c BMI': 'Q2_bmi5',
    'HbA1c glucose-adjusted BMI': 'Q3_bmi5', 'HDL BMI': 'K02-HDL-BMI',
    'TC BMI': 'K02-TC-BMI', 'TC–HDL residual correlation': 'K02-LIPID-RESIDUAL'}
unit_map = {'Q1_age10': 'pp / 10 years', 'Q2_bmi5': 'pp / 5 kg/m²', 'Q3_bmi5': 'pp / 5 kg/m²',
            'K02-HDL-BMI': 'mg/dL / 5 kg/m²', 'K02-TC-BMI': 'mg/dL / 5 kg/m²', 'K02-LIPID-RESIDUAL': 'dimensionless'}
summary_by_key = {(x['author_id'], x['endpoint']): x for x in results['all_author_endpoint_summaries']}
row_checks = []
for row in table(draft, 'S3')[2:]:
    label, author, unit, reference, mean, span = row
    key = (author, label_map[label])
    s = summary_by_key[key]
    displayed = [norm_number(reference), norm_number(mean)] + norm_number(span).split('–')
    expected = [format(x, '.6f') for x in [s['reference']['value'], s['slot_mean'], *s['slot_range']]]
    passed = displayed == expected and unit == unit_map[key[1]]
    row_checks.append({'author': author, 'endpoint': key[1], 'status': 'PASS' if passed else 'FAIL',
                       'displayed': displayed, 'expected': expected, 'units': unit})
check('All 18 Table S3 rows and native units', len(row_checks) == 18 and all(x['status'] == 'PASS' for x in row_checks), row_checks)

s4 = {row[0]: row for row in table(draft, 'S4')[2:]}
source_rows = []
for use in uses:
    row = s4[use['author']]
    source_rows.append({'author': use['author'], 'paper_uses': int(row[2]),
                       'source_checks': int(row[3]),
                       'matches': int(row[2]) == len(use['source_ids']) and int(row[3]) == use['source_check_count']})
check('All six Table S4 author inventories and total',
      all(x['matches'] for x in source_rows) and s4['Total'][2:] == ['22', '132'], source_rows)

for label in ('2', '3'):
    same = table(prior, label) == table(draft, label)
    check('Historical Table ' + label + ' preserved', same, 'Headers, row order, labels, units and every displayed number identical to v0.13.1.')
check('Historical Tables S1/S2 retained', table(prior, 'S1') == table(draft, 'S1') and table(prior, 'S2') == table(draft, 'S2'),
      'All Q4 summary and source inventory rows retained; captions now explicitly label Q4.')

references = {int(n): line for n, line in re.findall(r'^(\d+)\. (.+)$', draft, re.M)}
prior_refs = {int(n): line for n, line in re.findall(r'^(\d+)\. (.+)$', prior, re.M)}
check('References 1–24 preserved; 25–28 added', list(references) == list(range(1, 29)) and all(references[n] == prior_refs[n] for n in range(1, 25)),
      {str(n): references[n] for n in range(25, 29)})

images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', draft)
figure_files = [{'alt': alt, 'path': rel, 'exists': (DRAFT.parent / rel).is_file(),
                 'sha256': sha(DRAFT.parent / rel) if (DRAFT.parent / rel).is_file() else None} for alt, rel in images]
check('Figure links and numbering', len(images) == 8 and all(x['exists'] for x in figure_files)
      and re.findall(r'^\*\*Figure ([\w]+)\.', draft, re.M) == ['1', '2', '3', '4', '5', '6', '7', 'S1'], figure_files)
local_links = [target for target in re.findall(r'\]\(([^)]+)\)', draft) if not re.match(r'[a-z]+://', target)]
missing_links = [target for target in local_links if not (DRAFT.parent / target.split('#', 1)[0]).exists()]
check('All manuscript local artifact links resolve', not missing_links, {'links_checked': len(local_links), 'missing': missing_links})

tc = summary_by_key['L01', 'K02-TC-BMI']['reference']['interval']
check('TC reference interval crosses zero and is retained', tc['lower'] < 0 < tc['upper']
      and '−3.7535 to 15.1197' in draft and 'HC3 assumption-conditional sensitivity intervals' in draft,
      {'lower': tc['lower'], 'upper': tc['upper'], 'kind': tc['kind']})

dispersion = []
for author, diag_id in [('H02', 'hba1c.sd_population'), ('H02', 'q1_residual_rms'),
                        ('H03', 'hba1c.sd_population'), ('H03', 'q1_residual_rms'),
                        ('L02', 'total_cholesterol.sd_sample')]:
    values = [d for slot in slots if slot['author_id'] == author for d in slot['diagnostics'] if d['id'] == diag_id]
    mean = sum(d['value'] for d in values) / len(values)
    ref = values[0]['reference']['value']
    dispersion.append({'author': author, 'diagnostic': diag_id, 'mean_4dp': format(mean, '.4f'), 'reference_4dp': format(ref, '.4f'),
                       'present': format(mean, '.4f') in draft and format(ref, '.4f') in draft})
check('Reported H02/H03/L02 dispersion tradeoffs match aggregate diagnostics', all(x['present'] for x in dispersion), dispersion)

manual_checks = [
    ('Claim and version separation', 'Q1 main information contrast, Q2 supplied-summary reconstruction, Q3 HRS published-model reconstruction, Q4 bounded open retrieval, Q5 curated/optional-retrieval cross-task study and the preceding analytical sensitivity remain separate. Q5 L01–L03 are explicitly distinguished from Q2 literature-arm labels.'),
    ('Adjustment sets and operators', 'Section 4.7 and Table S3 state full age adjustment, reduced/full BMI adjustment, age/sex lipid slopes and same-row age/sex/BMI residual Pearson correlation. HbA1c population SD, lipid sample SD and residual RMS are distinguished. No marginal correlation is represented as a residual effect.'),
    ('Directions, uncertainty and mean-versus-spread interpretation', '54/54 is a descriptive point-direction count, not an accuracy rate or 54 clinical confirmations. TC crossing zero, unavailable residual-correlation interval, non-equivalence meaning of reference bands, seed-only uncertainty and H03/L02 tradeoffs are explicit.'),
    ('Evidence use and feedback limits', 'All six retained initial laws; 132 unavailable source checks are not counted as passed constraints or failed generators. Numerical parameter use is distinguished from numerical source replay. No revision gain, feedback quality benefit or retrieval benefit is claimed.'),
    ('Contribution and novelty', 'The proposed contribution is an inspectable evidence-to-joint-law-to-data workflow using established statistical families. Related LLM construction systems are acknowledged. No first/priority claim, new universal sampler, universal quality superiority or component-causal improvement claim is made.'),
    ('Objective preserved', 'Whole-cohort generation remains central; enrichment is a supporting mode and missing-cell completion remains unevaluated. Scenario-use limits are explicitly attached to current cross-task outputs rather than made a permanent narrowing of the method objective.'),
    ('Lipid originals and corrections', 'References 25–27 are the three lipid originals; reference 28 is the Agongo correction. The Greiner author-name correction is attached to reference 25. The source/code review identifies the Agongo waist/hip/citation changes and distinguishes geometric means, arithmetic moments and rural Spearman correlations.'),
    ('Gap checklist fairness', 'The checklist says the empirical unit is complete, supports a scoped methods/capability draft and conditions future experiments on stronger claims. It does not make a new benchmark, retuning exposed targets, numerical source replay or feedback improvement mandatory. Scientific author review, venue/format and author declarations remain legitimate writing/submission items.'),
]
for name, finding in manual_checks:
    check(name, True, finding)

bound_sources = [DRAFT, PRIOR, GAPS, CROSS / 'RESULTS.md', CROSS / 'evaluation/RESULTS.json',
                CROSS / 'evaluation/EVIDENCE_USAGE_SUMMARY.json', CROSS / 'review/INDEPENDENT_NUMERICAL_REVIEW.json',
                CROSS / 'review/INDEPENDENT_NUMERICAL_REVIEW.md', CROSS / 'review/SOURCE_AND_CODE_REVIEW.md',
                BASE / 'manuscript/CROSS_TASK_RESULTS_INSERT_2026-11-05.md']
report = {
    'schema_version': 'independent_draft_review_v14_v1',
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'reviewer': '/root/v14_scientific_review',
    'status': 'PASS' if all(x['status'] == 'PASS' for x in checks) else 'FAIL',
    'artifact': {'path': str(DRAFT), 'sha256': sha(DRAFT)},
    'scope': 'Independent manuscript content/numerical transcription review against frozen aggregate summaries. No patient or generated row tables read; no scientific tests, cohort generation, fits, reference reruns, web literature audit or PDF visual review performed.',
    'findings': [],
    'checks': checks,
    'source_bindings': {str(p.relative_to(BASE)): sha(p) for p in bound_sources},
    'limitations': ['Existing numerical audit supplies the 513-output recomputation evidence; this review does not repeat that audit.',
                    'Figure captions, numbering, aggregate roles and file links were checked. Root owns rendered-PDF/figure visual QA.',
                    'PASS supports a scientifically scoped reading draft, not clinical validation, submission acceptance or completed author declarations.']
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'INDEPENDENT_DRAFT_REVIEW.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
md = [
    '# Independent draft review — v0.14', '',
    '**' + report['status'] + '.** No blocking numerical-transcription or scientific-claim inconsistency was found in the inspected draft.', '',
    'Reviewed artifact: `manuscript/DRAFT_v0_14.md`',
    'SHA-256: `' + sha(DRAFT) + '`', '',
    'The review read manuscript text and frozen aggregate records only. It did not read patient or generated row tables, run scientific tests, generate cohorts, refit references, audit new literature, or inspect the PDF. The existing independent numerical review is bound to the exact evaluation JSON checked here.', '',
    '| Check | Result |', '|---|---|'
]
md += ['| ' + x['check'] + ' | ' + x['status'] + ' |' for x in checks]
md += ['', 'All 18 Table S3 author–analysis rows match the evaluation JSON at six displayed decimals, including reference, mean, minimum, maximum and units. All six source-use rows and their total match the evidence-use inventory. The aggregate inventory is six authors, two requests, 18 distinct final tables, 54,000 fictional final rows, 24 physical attempts, 54 same-direction primary outputs, 513 total outputs, 324 matched references and 189 generated-only diagnostics. Eight originals supply 22 author–paper uses; 132 source checks remain unavailable, and all six laws were retained.', '',
       'Historical Tables 2 and 3 have identical headers, row order, labels, units and displayed numbers to v0.13.1. Historical supplementary rows and references 1–24 are retained. References 25–28 provide the three lipid originals and Agongo correction. Figure 1–7 and S1 files and every local manuscript link resolve.', '',
       'The prose preserves the TC reference interval crossing zero, different reference-interval meanings, no residual-correlation interval, seed-only uncertainty, and the H03/L02 effect-versus-dispersion tradeoffs. It does not infer a general accuracy rate, clinical replication, source replay, feedback improvement, universal superiority or novelty priority from these results. The broader whole-cohort objective remains intact.', '',
       'The gap checklist is fair for a methods/capability draft: new experiments are conditional on stronger quantitative, component-causal, uncertainty or automation-efficiency claims. It does not reopen exposed targets or invent mandatory new experiments. Author review, venue/format selection and declarations remain writing/submission work.', '',
       'The machine-readable companion retains every check, all 18 row comparisons, exact source hashes and figure hashes. Root separately owns rendered-artifact visual QA. This PASS concerns the reviewed reading draft, not clinical validation or submission readiness.', '']
(OUT / 'INDEPENDENT_DRAFT_REVIEW.md').write_text('\n'.join(md), encoding='utf-8')
print(json.dumps({'status': report['status'], 'draft_sha256': sha(DRAFT), 'checks': len(checks),
                  'failed_checks': [x['check'] for x in checks if x['status'] != 'PASS'],
                  'reports': [str(OUT / 'INDEPENDENT_DRAFT_REVIEW.md'), str(OUT / 'INDEPENDENT_DRAFT_REVIEW.json')]}, indent=2))

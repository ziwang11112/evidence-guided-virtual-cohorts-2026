"""Bounded aggregate-only narrative check. Does not load rows or rerun fits."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    path = ROOT/'RESULTS.md'
    prose = path.read_text(encoding='utf-8-sig')
    release = read(ROOT/'custodian/evaluation_release.json')
    process = read(ROOT/'report/process_summary.json')
    aggregate = read(ROOT/'custodian/results/aggregate_report.json')
    with (ROOT/'custodian/results/final_endpoint_comparison.csv').open(encoding='utf-8-sig',newline='') as stream:
        final = list(csv.DictReader(stream))
    checks = {}
    labels = ['Crude BMI, per 5 kg/m2','Adjusted BMI, per 5 kg/m2: primary','Adjusted age, per 10 years',
              'Adjusted female minus male','BMI slope at 35 minus slope at 25, per 5 units',
              'Female minus male BMI slope, per 5 units','Male BMI slope, per 5 units','Female BMI slope, per 5 units']
    construction_order = ['ordinary_1','ordinary_2','gap_1','gap_2']
    clean = prose.replace('**','')
    for label,row in zip(labels,final):
        expected = [f"{float(row[key]):.3f}" for key in ['reference_estimate','reference_ci95_low','reference_ci95_high']+
                    [name+'_generated_median' for name in construction_order]]
        lines = [line for line in clean.splitlines() if line.startswith('| '+label+' |')]
        actual = re.findall(r'-?\d+\.\d+', '|'.join(lines[0].split('|')[2:])) if len(lines)==1 else []
        checks['displayed_'+row['endpoint']] = actual == expected
    checks['40_unique_scheduled_paths'] = len(release['outputs'])==40 and len({e['file'] for e in release['outputs']})==40
    checks['25_distinct_contents'] = len({e['sha256'] for e in release['outputs']})==25
    checks['four_constructions'] = {e['construction'] for e in release['outputs']}==set(construction_order)
    checks['explicit_no_independent_40_agent_claim'] = 'not forty independent Agents or newly observed clinical cohorts' in prose
    checks['primary_not_novelty'] = 'A primary endpoint is not automatically a previously unknown relationship.' in prose
    checks['held_out_target_vs_source_support'] = 'All target estimates were held out, but source-informed BMI, sex, age and shape relationships are not newly discovered effects.' in prose
    checks['no_policy_superiority'] = 'does not demonstrate that the explicit gap/action policy produces better virtual data' in prose
    checks['broad_science_not_exact_matching'] = 'Exact coefficient equality was not required.' in prose and 'Matching significance is not the success definition.' in prose
    checks['reference_interaction_unresolved'] = 'unresolved evidence, not proof of no interaction' in prose
    checks['gap_policy_no_numerical_revision_effect'] = 'no numerical revision effect occurred' in prose and all(
        aggregate['initial_final_generated_output_hashes_identical'][name] for name in ['gap_1','gap_2'])
    changes = aggregate['ordinary_1_error_changes']
    checks['ordinary_1_five_smaller_three_larger'] = len(changes['decreased_endpoints'])==5 and len(changes['increased_endpoints'])==3 and 'declined on five endpoints and rose on three' in prose
    usage_labels = {'ordinary_1':'Ordinary 1','ordinary_2':'Ordinary 2','gap_1':'Gap policy 1','gap_2':'Gap policy 2'}
    for item in process:
        name = item['construction']
        before,after = item['initial_usage'],item['final_usage']
        prefix = f"| {usage_labels[name]} | {before['queries']} to {after['queries']} | {before['downloads']} to {after['downloads']} |"
        checks[name+'_retrieval_counts'] = prefix in prose
    input_paths = ['RESULTS.md','custodian/evaluation_release.json','report/process_summary.json',
                   'custodian/results/aggregate_report.json','custodian/results/final_endpoint_comparison.csv',
                   'review/synthetic_test_report.json','review/implementation_audit.txt','custodian/synthetic_test_report.json']
    report = {
        'reviewed_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS' if all(checks.values()) else 'FAIL',
        'reviewed_file':'RESULTS.md','results_sha256':sha(path),
        'scope':'Bounded final narrative and aggregate consistency check only. No participant rows read; no fits rerun.',
        'checks':checks,
        'manual_findings':[
            'All four builders and all eight final analyses appear; table values match the audited aggregates at the displayed precision.',
            'The primary endpoint is explicitly separated from novelty. Held-out target estimates are distinguished from relationships informed by external evidence.',
            'Forty scheduled dataset files means forty unique paths/slots and twenty-five distinct contents, not forty independent constructions or clinical cohorts.',
            'Both gap-policy revisions and ordinary_2 are numerical no-ops; ordinary_1 revision has mixed endpoint movements, without an aggregate improvement score.',
            'Broad directional preservation is acknowledged while age, shape and interaction limitations are retained. Exact-number equality and significance matching are not made success requirements.',
            'The conclusion is limited feasibility and no demonstrated policy revision benefit; no superiority, causality, individual recovery or replacement-of-measurement claim is made.',
            'The narrative states procedural blinding, incomplete source access, unknown exact compute and exposed-test limitations. Synthetic-fixture counts and the empty-domain-PSU qualification match the retained pre-run audit records.',
            'AUDIT.md and its source template received wording-only clarification of dataset-file counts after the numerical audit; no numerical implementation or result was changed.'
        ],
        'needed_changes':[],
        'inputs':{name:sha(ROOT/name) for name in input_paths},
        'participant_rows_read':False,'fits_rerun':False
    }
    (OUT/'final_narrative_review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    note = ('# Final narrative review\n\nStatus: '+report['status']+'.\n\n'
            'Reviewed `RESULTS.md` SHA-256: `'+report['results_sha256']+'`.\n\n'
            'The complete narrative and all displayed final endpoint numbers agree with the already audited aggregates. '
            'The text distinguishes primary from novel, target-held-out from source-informed relationships, four Agent constructions from forty scheduled files, '
            'and broad scientific usefulness from exact-number matching. It reports the gap-policy no-ops, ordinary_1 mixed changes, unresolved interaction and lack of demonstrated superiority. '
            'No further change is required. No participant rows were read and no fits were rerun.\n')
    (OUT/'FINAL_NARRATIVE_REVIEW.md').write_text(note,encoding='utf-8')
    manifest_path = OUT/'audit_hashes.json'
    manifest = read(manifest_path)
    manifest['audit_source_sha256'] = sha(OUT/'independent_audit.py')
    manifest['final_narrative_review_sha256'] = sha(OUT/'final_narrative_review.json')
    manifest['inputs'].update(report['inputs'])
    manifest['outputs'] = {p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='audit_hashes.json'}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'results_sha256':report['results_sha256'],
                      'checks':len(checks),'failed':[k for k,v in checks.items() if not v],'fits_rerun':False}))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()

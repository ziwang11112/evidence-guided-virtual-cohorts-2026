"""Verify review arithmetic and artifact bindings; never fit or generate a cohort."""
from pathlib import Path
import csv
import hashlib
import json
import re
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

units = {
    'PNS': ('pns_evidence_content_control_2026-11-16', 'residual_correlation', 78.6),
    'IRON': ('iron_evidence_content_control_2026-11-16', 'odds_ratio', 46.8),
}
profiles, inputs, primary = [], {}, {}
for case, (folder, endpoint, displayed) in units.items():
    f = ROOT / 'work' / folder / 'analysis' / 'arm_results.csv'
    inputs[str(f.relative_to(ROOT)).replace('\\', '/')] = sha(f)
    with f.open(encoding='utf-8-sig', newline='') as h:
        rows = list(csv.DictReader(h))
    idx = {(r['arm'], r['estimand']): r for r in rows}
    for metric in dict.fromkeys(r['estimand'] for r in rows):
        s, j = idx[('SUMMARY', metric)], idx[('JOINT', metric)]
        a = float(s['author_mean_absolute_reference_difference'])
        b = float(j['author_mean_absolute_reference_difference'])
        profiles.append({
            'case': case, 'estimand': metric,
            'summary_estimate': float(s['author_mean']),
            'joint_estimate': float(j['author_mean']),
            'summary_discrepancy': a, 'joint_discrepancy': b,
            'relative_reduction_percent': 100 * (a - b) / a if a else None,
            'interpretation': 'closer' if b < a else ('farther' if b > a else 'equal'),
        })
    row = next(r for r in profiles if r['case'] == case and r['estimand'] == endpoint)
    assert round(row['relative_reduction_percent'], 1) == displayed
    assert all(int(r['planned_authors']) == 3 and int(r['available_authors']) == 3 for r in rows)
    primary[case] = row

manifest_path = ROOT / 'work/manuscript_integration_v33_2026-11-17/DELIVERY_MANIFEST.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))['files']
changed = []
for name, record in manifest.items():
    f = ROOT / name
    if not f.is_file() or sha(f) != record['sha256']:
        changed.append(name)
assert not changed, changed

links = []
for name in ('REVIEW.md', 'NEXT_EXPERIMENTS.md'):
    f = HERE / name
    for link in re.findall(r'\]\(([^)]+)\)', f.read_text(encoding='utf-8')):
        if '://' in link or link.startswith('#'):
            continue
        target = (f.parent / link.split('#')[0]).resolve()
        links.append({'file': name, 'target': link, 'exists': target.is_file()})
assert all(x['exists'] for x in links), links

with (HERE / 'RECOMPUTED_CLAIM_PROFILE.csv').open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(profiles[0]))
    w.writeheader()
    w.writerows(profiles)

receipt = {
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Review of existing aggregate evidence; root-authored arithmetic, not an external or patient-level replication.',
    'new_agent_constructions': 0, 'new_generated_tables': 0,
    'new_patient_fits': 0, 'paid_api_calls': 0, 'new_dataset_downloads': 0,
    'v33_delivery_files_checked': len(manifest), 'changed_v33_delivery_files': changed,
    'input_sha256': inputs, 'primary_recomputed': primary,
    'full_profile_rows': len(profiles), 'local_link_checks': links,
    'not_checked': ['All historical units', 'Fresh patient-level recomputation', 'All LLMSynthor branches or releases', 'KMGen full implementation'],
    'source_checks': {
        'LLMSynthor_readme_blob': '8d7c16fd22a55567e5453675a1249c4c05ddb311',
        'LLMSynthor': 'https://arxiv.org/html/2505.14752v4',
        'GSim': 'https://proceedings.mlr.press/v267/holt25b.html',
        'KMGen_official_abstract': 'https://proceedings.mlr.press/v340/jiang26a.html',
        'KDD_Research': 'https://kdd2027.kdd.org/research-track-call-for-papers/',
        'KDD_AI4Sciences': 'https://kdd2027.kdd.org/ai4sciences-track-call-for-papers/',
    },
    'artifact_sha256': {n: sha(HERE / n) for n in ['REVIEW.md', 'NEXT_EXPERIMENTS.md', 'verify_review.py', 'RECOMPUTED_CLAIM_PROFILE.csv']},
}
(HERE / 'AUDIT_RECEIPT.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'v33_files_unchanged': len(manifest), 'local_links_ok': len(links), 'profiles': len(profiles), 'primary': primary}, ensure_ascii=False, indent=2))

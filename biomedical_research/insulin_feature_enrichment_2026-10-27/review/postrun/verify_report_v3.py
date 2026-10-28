"""Presentation-only follow-up; no evaluation or generation execution."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
a, b = ROOT/'results/report_v2', ROOT/'results/report_v3'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
with (a/'scientific_interpretation.csv').open(encoding='utf-8', newline='') as f:
    old = list(csv.DictReader(f))
with (b/'scientific_interpretation.csv').open(encoding='utf-8', newline='') as f:
    new = list(csv.DictReader(f))
assert len(old) == len(new) == 8
assert all(all(row[key] == revised[key] for key in row) for row,revised in zip(old,new))
assert all(row.get('evidence_role') for row in new)
assert (a/'correlations.json').read_bytes() == (b/'correlations.json').read_bytes()
assert (a/'initial_v1_analyses.png').read_bytes() == (b/'initial_v1_analyses.png').read_bytes()
old_text, new_text = [(p/'ALL_ANALYSES.md').read_text(encoding='utf-8') for p in (a,b)]
numeric_rows = [line for line in old_text.splitlines() if line.startswith('| ') and '[' in line and not line.startswith('| Question')]
assert len(numeric_rows) == 8 and all(line in new_text for line in numeric_rows)
assert 'Labels below were finalized in postrun review from the frozen source/model provenance.' in new_text
assert all(row['evidence_role'] in new_text for row in new)
results = (ROOT/'RESULTS.md').read_text(encoding='utf-8')
assert 'Generated ratios in this report are obtained by exponentiating the median log-effect estimate' in results
prior = json.loads((OUT/'audit_results.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/path) == digest for path,digest in prior['audit_snapshot_result_hashes'].items())
assert sha(ROOT/'freeze_v1/outputs_freeze.json') == 'aee9d3b44df52b59a754cdcfd88629eddf414f4e8b2c7e23c4ce102ba271f4c4'
assert all(sha(ROOT/r['path']) == r['sha256'] for r in prior['hash_checks'])
payload = {'utc':datetime.now(timezone.utc).isoformat(), 'status':'PASS',
           'all_existing_csv_cells_exact':True, 'existing_csv_cells_checked':sum(len(row) for row in old),
           'endpoint_role_labels':8, 'all_eight_rounded_numerical_markdown_rows_unchanged':True,
           'correlation_file_byte_identical':True, 'png_byte_identical':True,
           'ratio_definition_explicit_in_RESULTS':True, 'all_prior_snapshot_and_frozen_hashes_rechecked':True,
           'interpretation_read':'RESULTS.md', 'report_v3_sha256':{p.name:sha(p) for p in b.iterdir() if p.is_file()},
           'results_md_sha256':sha(ROOT/'RESULTS.md')}
(OUT/'report_v3_checks.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload))

"""Index audit records; record counts are NOT experiment or replication counts."""
from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent

def printable(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)

rows = []
inputs = {}
for filename, key in [('HISTORY_AUDIT.json', 'units'), ('PRIMARY_AUDIT.json', 'units'), ('RECENT_AUDIT.json', 'records')]:
    path = HERE / filename
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    inputs[filename] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'audit_records': len(data[key])}
    for item in data[key]:
        row = {'audit_partition': filename.removesuffix('.json')}
        for name in ['id', 'report_paths', 'input_setting', 'actual_scale', 'comparison', 'strongest_supported_finding', 'numeric_support', 'counterresults', 'inference_scope', 'strength_grade', 'paper_role']:
            assert name in item, (filename, item.get('id'), name)
            row[name] = printable(item[name])
        rows.append(row)
with (HERE / 'ALL_UNIT_INDEX.csv').open('w', encoding='utf-8-sig', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
manifest = {
    'scope': 'All assigned virtual-biomedical-data report lineages, October 25 to November 9, 2026; no patient rows or new generation.',
    'inputs': inputs, 'audit_records': len(rows),
    'count_warning': 'Audit records include setup, engineering, diagnosis, reused outputs and overlapping milestone summaries. This is not a count of independent experiments, cohorts or successful replications.',
    'index_sha256': hashlib.sha256((HERE / 'ALL_UNIT_INDEX.csv').read_bytes()).hexdigest(),
}
(HERE / 'INDEX_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'audit_records': len(rows), 'partitions': {k:v['audit_records'] for k,v in inputs.items()}}))

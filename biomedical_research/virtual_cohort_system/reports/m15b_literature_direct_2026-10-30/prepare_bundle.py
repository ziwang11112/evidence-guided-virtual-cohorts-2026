"""Prepare metadata and full source artifacts only; never create biomedical row values."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

RUN = Path(__file__).resolve().parent
PROJECT = RUN.parent.parent
sys.path.insert(0, str(PROJECT))
from cohort_harness.contracts import validate_task
from cohort_harness.lifecycle import _registry


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)


bundle = RUN / 'visible/bundle'
bundle.mkdir(parents=True, exist_ok=True)
columns = [
    {'name': 'sample_id', 'kind': 'string', 'unit': '', 'role': 'identifier', 'nullable': False},
    {'name': 'race', 'kind': 'category', 'unit': '', 'role': 'observed', 'nullable': False, 'categories': ['White', 'Black']},
    {'name': 'sex', 'kind': 'category', 'unit': '', 'role': 'observed', 'nullable': False, 'categories': ['male', 'female']},
    {'name': 'age', 'kind': 'number', 'unit': 'years', 'role': 'observed', 'nullable': False, 'minimum': 20, 'maximum': 56},
    {'name': 'bmi', 'kind': 'number', 'unit': 'kg/m^2', 'role': 'observed', 'nullable': False, 'minimum': 0},
    {'name': 'urate', 'kind': 'number', 'unit': 'mg/dL', 'role': 'generated', 'nullable': False, 'minimum': 0},
]
task = {
    'schema_version': 1, 'task_id': 'M15B1_literature_enabled_direct_urate_2026_10_30',
    'mode': 'enrichment', 'population': 'Finite 200-person US adult benchmark: ages20-56, non-Hispanic White/Black, male/female, self-reported no professional diabetes diagnosis; equal 50-per-stratum allocation. Not nationally representative.',
    'row_id': 'sample_id', 'n_rows': 200, 'columns': columns,
    'information_policy': {'mode': 'published_evidence',
        'excluded_cohorts': ['NHANES', 'National Health and Nutrition Examination Survey'],
        'allowed_tools': ['read_visible_files', 'apply_patch_literal_submission',
                          'literature.search', 'literature.fetch', 'literature.list-supplements', 'literature.fetch-supplement']},
    'budget': {'source_queries': 23, 'source_downloads': 9, 'revisions': 2},
}
validate_task(task)
write_new(bundle/'task.json', task)
admission = PROJECT/'work/m15b_admission_2026-10-30/private/source'
inputs = [
    ('PMC8236402', 'PMC8236402.cached-original.fullText.xml', 'f3f4c658fe8ef90fb92ebc283f0dc4ddf87d0af81c10b127b734e2ce10f608a3'),
    ('PMC4208749', 'PMC4208749.fullText.xml', '26ce9cb66838e047d8c9c161668cd56ba8d87826a4c4950208699000612f3bcc'),
]
registry = {'artifacts': []}
for source_id, filename, expected in inputs:
    raw = (admission/filename).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected
    dest = bundle/'sources'/f'{source_id}.xml'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as stream:
        stream.write(raw)
    root = ET.fromstring(raw)
    # Full, unredacted textual conversion; original XML retains exact cell/section layout.
    lines = [x.strip() for x in root.itertext() if x.strip()]
    txt = '\n'.join(lines) + '\n'
    text_path = bundle/'sources'/f'{source_id}.txt'
    write_new(text_path, txt)
    for file in (dest, text_path):
        registry['artifacts'].append({'source_id': source_id, 'path': file.relative_to(bundle).as_posix(),
            'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'origin': 'curator', 'screening': 'approved'})
write_new(bundle/'registry.json', registry)
_registry(bundle)
write_new(RUN/'visible/SEED_PROVENANCE.md', '''# Seed source provenance

Two complete original articles were retrieved or reused and independently checked by the controller's admission reviewer. You are receiving full originals, not the old marginal-only M15-A excerpt. Extract and select your evidence yourself. No source statistic is reserved as a hidden test.

- PMC8236402: Yun2021, DOI10.1038/s41366-021-00810-9; original cached JATS reused, verified hash.
- PMC4208749: Sun2014, DOI10.1371/journal.pone.0089696; original JATS retrieved once from EuropePMC.

Both use Bogalusa. Do not count them as independent cohorts. They differ in survey periods and disease/treatment/fasting selection. The full Sun text contains an incidental pediatric NHANES comparison. Its seed admission is an explicit controller-reviewed exception to the conservative general name screen: the original study's underlying data are Bogalusa, and the referenced comparison is not the reserved2021-2023 adult target. Record that exposure; do not adopt those incidental NHANES findings as generation constraints. Never silently bypass a gateway rejection for other sources.

The .txt files are full, unredacted itertext conversions for convenience; XML is authoritative for table boundaries. All quantities and individual participant SDs are allowed inputs. Missing relationships remain missing; the sources do not identify every feature of the desired joint law. An acquired file and a cited statistic are different kinds of provenance.

Admission usage: one metadata search; two failed article browser opens; one successful new fulltext download; one original reused from cache. There are two deeply inspected primary papers so far. Remaining gateway limits are23queries/9downloads, with at most six additional deeply read primary originals across the entire construction/revision loop. These limits include failed requests and fetch metadata lookups according to the adapter. Controller-assisted access would use the same remaining overall budget.
''')
checks = {'scope':'source_only', 'records':[{'name':'initial_scientific_checks', 'status':'not_computable',
    'detail':'No candidate or source diagnostic has been run yet. Replace with truthful actual records; computed checks require bound artifacts.'}], 'artifacts':[]}
write_new(RUN/'visible/templates/checks_initial.json', checks)
write_new(RUN/'visible/templates/model_spec.json', {'parameters':{},'assumptions':[],'parameter_provenance':{}})
write_new(RUN/'visible/templates/revision.json', {'reason':'REPLACE_WITH_ACTUAL_REASON','kind':'retain','addressed_findings':[], 'remaining_limitations':[]})
print(json.dumps({'task_valid':True,'registered_source_artifacts':len(registry['artifacts']), 'target_rows_created':False,'bundle':str(bundle)}))

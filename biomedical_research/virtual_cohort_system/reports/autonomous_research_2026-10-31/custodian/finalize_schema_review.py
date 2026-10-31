"""Finalize metadata-only unsuccessful access audit; makes no network requests."""
from pathlib import Path
import hashlib
import json

base = Path(__file__).resolve().parent
contract_path = base.parent / 'admission' / 'SCHEMA_ACCESS_CONTRACT.json'
contract_bytes = contract_path.read_bytes()
contract = json.loads(contract_bytes.decode('utf-8-sig'))
contract_hash = hashlib.sha256(contract_bytes).hexdigest()
assert contract_hash == 'ac44b2f2485dfa8ce162f11d1557134ea7c9689f8660c026e7c067a6d808829d'
ledger = base / 'private' / 'download_attempts.json'
attempts = json.loads(ledger.read_text(encoding='utf-8'))
assert len(attempts) == 2
assert not (base / 'private' / 'Data set Int J Obesity.xlsx').exists()
# Codes observed in the corresponding urllib HTTPError tool outputs.
for entry, code in zip(attempts, [401, 403], strict=True):
    entry['http_status'] = code
    entry['workbook_bytes_saved'] = 0
ledger.write_text(json.dumps(attempts, indent=2), encoding='utf-8')

meta = {
    'scope': 'Metadata-only schema admission; no target workbook acquired or inspected',
    'date': '2026-10-31',
    'contract_sha256': contract_hash,
    'candidate': contract['candidate'],
    'dataset_doi': contract['doi'],
    'dataset_version_id': contract['version_id'],
    'file_id': contract['file_id'],
    'filename_from_official_api': 'Data set Int J Obesity.xlsx',
    'license_from_prior_official_api_admission': 'CC0-1.0',
    'expected_bytes_from_official_api': contract['expected_bytes'],
    'expected_md5_from_official_api': contract['expected_md5'],
    'observed_workbook_bytes': None,
    'workbook_bytes_saved': 0,
    'observed_workbook_md5': None,
    'observed_workbook_sha256': None,
    'download_attempt_limit': 2,
    'download_attempts': attempts,
    'access_status': 'attempt_budget_exhausted_no_workbook',
    'sheets': None,
    'headers': None,
    'row_count': None,
    'column_count': None,
    'one_row_per_person': 'not_verified',
    'longitudinal_field_semantics': 'not_verified',
    'metadata_sources': [
        'https://datadryad.org/api/v2/versions/22266/files',
        'https://datadryad.org/dataset/doi:10.5061/dryad.8q0p192'
    ],
    'public_route_discovery': 'Official landing-page HTML was filtered to download hyperlinks; article abstract and dataset-description text were not emitted.',
    'methods_source_doi': '10.1038/s41366-018-0076-3',
    'methods_access': [
        {'url': 'https://www.nature.com/articles/s41366-018-0076-3', 'status': 'HTTP 200 Client Challenge; no Methods section'},
        {'url': 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=10.1038/s41366-018-0076-3&format=json', 'status': 'Identifier not found in PMC'},
        {'operation': 'web find Methods in exact Nature article', 'status': 'Identity-provider redirect inaccessible; no article text returned'}
    ],
    'semantic_admission': {
        'age': {'ready': False, 'column': None, 'unit': None},
        'sex': {'ready': False, 'column': None, 'coding': None},
        'BMI': {'ready': False, 'column': None, 'unit': 'kg/m^2 described in prior original-abstract admission only; workbook not verified'},
        'fasting_plasma_glucose': {'ready': False, 'column': None, 'unit': None, 'fasting_protocol': None, 'assay': None},
        'HbA1c': {'column': None, 'unit_scale': None, 'assay': None}
    },
    'selection': {'recruitment_dates': None, 'site_primary_methods_verified': False, 'baseline_diabetes_definition': None, 'fasting_glucose_exclusion_threshold': None, 'other_exclusions': None},
    'clinical_target_definable_from_admitted_material': False,
    'decision': 'No schema admission; age/sex/BMI/FPG semantic readiness and clinical target definition remain unverified.',
    'exposure_audit': 'Prior admission report contained original-abstract cohort/sex counts and proposed estimands. Counts were not retained or used. No participant rows, numerical target effects, result tables, or target-data summaries were produced in this step.',
    'new_primary_papers': 0,
    'installations': 0,
    'target_analyses': 0,
    'generation_runs': 0,
    'uncertainty_calculations': 0,
    'state_mutated': False,
    'environment': {'python': '3.12.10', 'openpyxl': '3.1.5'},
    'population_truth_note': 'No cohort statistics are treated as population truth; no inference is produced.'
}
target = base / 'SCHEMA_METADATA.json'
target.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'metadata_path': str(target), 'contract_sha256': contract_hash, 'download_attempts': len(attempts), 'workbook_bytes_saved': 0, 'schema_ready': False}, indent=2))

"""Contract-bound metadata inspection. Never emits or summarizes participant cells."""
from pathlib import Path
import hashlib
import json
import sys
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
import openpyxl

BASE = Path(__file__).resolve().parent
CONTRACT = BASE.parent / 'admission' / 'SCHEMA_ACCESS_CONTRACT.json'
EXPECTED_CONTRACT_SHA256 = 'ac44b2f2485dfa8ce162f11d1557134ea7c9689f8660c026e7c067a6d808829d'
assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest() == EXPECTED_CONTRACT_SHA256
contract = json.loads(CONTRACT.read_text(encoding='utf-8-sig'))
private = BASE / 'private'
private.mkdir(parents=True, exist_ok=True)
raw = private / 'Data set Int J Obesity.xlsx'
ledger = private / 'download_attempts.json'
attempts = json.loads(ledger.read_text()) if ledger.exists() else []
limit = contract['limits']['target_workbook_bytes_max']
if not raw.exists():
    if len(attempts) >= contract['limits']['target_workbook_download_attempts_max']:
        raise RuntimeError('Download attempt limit exhausted')
    # Public route discovered in the official dataset page after API attempt 1 returned 401.
    download_url = contract['download_url'] if not attempts else 'https://datadryad.org/downloads/file_stream/76808'
    entry = {'attempt': len(attempts) + 1, 'url': download_url, 'status': 'started'}
    attempts.append(entry)
    ledger.write_text(json.dumps(attempts, indent=2), encoding='utf-8')
    try:
        request = urllib.request.Request(download_url, headers={'User-Agent': 'MetadataSchemaCustodian/1.0'})
        with urllib.request.urlopen(request, timeout=45) as response:
            length = response.headers.get('Content-Length')
            if length is not None and int(length) > limit:
                raise RuntimeError('Content-Length exceeds limit')
            payload = response.read(limit + 1)
            if len(payload) > limit:
                raise RuntimeError('Body exceeds limit')
            entry['http_status'] = response.status
            entry['final_url'] = response.url
        entry['bytes'] = len(payload)
        entry['md5'] = hashlib.md5(payload).hexdigest()
        entry['sha256'] = hashlib.sha256(payload).hexdigest()
        assert entry['bytes'] == contract['expected_bytes'], 'Size mismatch'
        assert entry['md5'] == contract['expected_md5'], 'MD5 mismatch'
        raw.write_bytes(payload)
        entry['status'] = 'complete_verified'
    except Exception as exc:
        entry['status'] = 'failed'
        entry['error_type'] = type(exc).__name__
        if hasattr(exc, 'code'):
            entry['http_status'] = exc.code
        raise
    finally:
        ledger.write_text(json.dumps(attempts, indent=2), encoding='utf-8')
payload = raw.read_bytes()
assert len(payload) == contract['expected_bytes']
assert hashlib.md5(payload).hexdigest() == contract['expected_md5']
workbook = openpyxl.load_workbook(raw, read_only=True, data_only=False)
meta = {
    'scope': 'Metadata/header and row-count inspection only; no participant values returned or summarized',
    'contract_sha256': EXPECTED_CONTRACT_SHA256,
    'dataset_doi': contract['doi'],
    'version_id': contract['version_id'],
    'file_id': contract['file_id'],
    'download_url': contract['download_url'],
    'license': 'CC0-1.0 (previously admitted official Dryad API metadata)',
    'raw_file': 'custodian/private/' + raw.name,
    'bytes': len(payload),
    'md5': hashlib.md5(payload).hexdigest(),
    'sha256': hashlib.sha256(payload).hexdigest(),
    'download_attempt_count': len(attempts),
    'python_version': sys.version.split()[0],
    'openpyxl_version': openpyxl.__version__,
    'sheets': [],
    'defined_names': [{'name': key, 'definition': item.attr_text} for key, item in workbook.defined_names.items()],
    'properties': {'title': workbook.properties.title, 'subject': workbook.properties.subject,
                   'description': workbook.properties.description, 'keywords': workbook.properties.keywords},
}
for sheet in workbook.worksheets:
    first_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=False), ())
    meta['sheets'].append({
        'name': sheet.title,
        'visibility': sheet.sheet_state,
        'max_row_including_header': sheet.max_row,
        'max_column': sheet.max_column,
        'rows_below_header_by_dimension': max(sheet.max_row - 1, 0),
        'headers': [{'column': cell.column, 'header': cell.value} for cell in first_row],
    })
workbook.close()
# Count structural worksheet row nodes only. No cell-value text is parsed or returned here.
ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
with zipfile.ZipFile(raw) as z:
    meta['worksheet_structure'] = []
    for name in z.namelist():
        if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
            root = ET.fromstring(z.read(name))
            rows = root.findall('.//' + ns + 'sheetData/' + ns + 'row')
            meta['worksheet_structure'].append({
                'part': name,
                'row_nodes_including_header': len(rows),
                'row_nodes_below_header': sum(1 for row in rows if int(row.attrib['r']) > 1),
                'last_row_index': max((int(row.attrib['r']) for row in rows), default=0),
            })
    meta['metadata_part_names'] = [name for name in z.namelist() if name.startswith('docProps/') or 'comment' in name.lower()]
target = BASE / 'SCHEMA_METADATA.json'
target.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(meta, indent=2, ensure_ascii=False))

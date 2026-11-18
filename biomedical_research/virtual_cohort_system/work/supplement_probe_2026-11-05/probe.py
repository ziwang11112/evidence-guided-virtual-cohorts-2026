"""One fixed source probe; never writes to the old gateway or experiment."""
from pathlib import Path
import hashlib
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT.parents[3] / 'evcRepE01'
FILENAME = '12889_2019_6698_MOESM3_ESM.doc'
URL = ('https://pmc-oa-opendata.s3.amazonaws.com/PMC6458679.1/'
       + FILENAME + '?md5=6b96852aaaff8f5a96a3c03080009212')
MD5 = '6b96852aaaff8f5a96a3c03080009212'
CONFIG_SHA = '5fdc114451ebb91cb877a4f1baf6f46135ab36da73b85f0572b6c8399cb44676'
REQUEST_SHA = '4215c82b6a9396783270879e92c3e96f4607818bf88a342922b0cb090cfc9a0d'
XML_SHA = 'e36df343e42bf6e96a6c392fd5f3409a0eaa612a6f4797c1e626ba7917d327fb'
MANIFEST_SHA = '342f7f01a0284129bbd0732ab1415906dd880953059b3b7ce10906cea483e563'
LIMIT = 8 * 1024 * 1024

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def frozen_hashes():
    # Never inspect row contents: hash source/task/config/session bytes only.
    files = [BUNDLE / name for name in ('task.json', 'request.json', 'registry.json',
             'gateway/config.json', 'gateway/session/state.json', 'gateway/session/audit.jsonl')]
    files += list((BUNDLE / 'sources').rglob('*'))
    files += list((BUNDLE / 'gateway/session/approved').rglob('*'))
    return {str(p.relative_to(BUNDLE)).replace('\\', '/'): sha(p.read_bytes())
            for p in files if p.is_file()}

def verify_parent():
    require(sha((ROOT / 'SCIENCE_REQUEST.json').read_bytes()) == REQUEST_SHA, 'Science request changed')
    require(sha((BUNDLE / 'gateway/config.json').read_bytes()) == CONFIG_SHA, 'Original config changed')
    state = json.loads((BUNDLE / 'gateway/session/state.json').read_text(encoding='utf-8'))
    require(state['config_sha256'] == CONFIG_SHA, 'Original state/config mismatch')
    events = [json.loads(line) for line in (BUNDLE / 'gateway/session/audit.jsonl').read_bytes().splitlines()]
    raw = {}
    for key, expected, ext, size in [('xml', XML_SHA, 'xml', 122768),
                                      ('manifest', MANIFEST_SHA, 'json', 1357)]:
        rel = f'approved/{expected}.{ext}'
        content = (BUNDLE / 'gateway/session' / rel).read_bytes()
        require(len(content) == size and sha(content) == expected, 'Parent artifact changed')
        artifact = {'session_relative_path': rel, 'sha256': expected, 'bytes': size}
        require(any(e.get('type') == 'artifact_approved' and e.get('status') == 'accepted'
                    and e.get('config_sha256') == CONFIG_SHA and e.get('artifact') == artifact
                    for e in events), 'Missing original approval event')
        require((BUNDLE / 'sources/gateway' / f'{expected}.{ext}').read_bytes() == content,
                'Registered parent copy differs')
        raw[key] = content
    tree = ET.fromstring(raw['xml'])
    hrefs = []
    for e in tree.iter():
        if e.tag.rsplit('}', 1)[-1] in ('supplementary-material', 'inline-supplementary-material'):
            hrefs += [v for child in e.iter() for k, v in child.attrib.items()
                      if k.rsplit('}', 1)[-1] == 'href' and v == FILENAME]
    require(len(hrefs) == 1, 'Exact supplementary-material link not unique')
    manifest = json.loads(raw['manifest'])
    require(manifest['pmcid'] == 'PMC6458679' and manifest['version'] == 1, 'Parent version mismatch')
    expected_s3 = URL.replace('https://pmc-oa-opendata.s3.amazonaws.com/', 's3://pmc-oa-opendata/')
    matches = [u for u in manifest['media_urls'] if u.split('?')[0].split('/')[-1] == FILENAME]
    require(matches == [expected_s3], 'Manifest object/checksum mismatch')
    return frozen_hashes()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect prohibited')

def detect_format(raw):
    if raw.startswith(bytes.fromhex('d0cf11e0a1b11ae1')):
        return 'OLE_compound_document'
    if raw.lstrip().startswith(b'{\\rtf'):
        return 'RTF'
    if raw.startswith(b'PK\x03\x04'):
        return 'ZIP_container_requires_inspection'
    raise ValueError('Unrecognized document magic')

def check_payload(raw, content_type, content_length):
    require(0 < len(raw) <= LIMIT, 'Response size limit')
    require(content_length is None or int(content_length) == len(raw), 'Incomplete response')
    require(content_type.split(';')[0].lower() in {
        'application/msword', 'application/octet-stream', 'binary/octet-stream', 'application/rtf',
        'text/rtf', 'application/vnd.ms-word'}, 'Unexpected response content type')
    require(hashlib.md5(raw).hexdigest() == MD5, 'Manifest checksum failed')
    return detect_format(raw)

def download():
    before = verify_parent()
    receipt_path = ROOT / 'ACQUISITION_RECEIPT.json'
    reservation = {'status': 'attempt_reserved', 'http_attempts': 1, 'attempt_limit': 1,
                   'byte_limit': LIMIT, 'url': URL, 'created_utc': datetime.now(timezone.utc).isoformat(),
                   'old_gateway_support': 'unsupported_supplement_format',
                   'science_request_sha256': REQUEST_SHA, 'frozen_before': before}
    # Exclusive persistent reservation prevents retry or quota reset on a second run.
    with receipt_path.open('x', encoding='utf-8') as f:
        json.dump(reservation, f, indent=2)
    start = time.monotonic()
    try:
        opener = urllib.request.build_opener(NoRedirect())
        req = urllib.request.Request(URL, headers={'User-Agent': 'EvidenceSourceProbe/1.0',
                                                  'Accept-Encoding': 'identity'})
        with opener.open(req, timeout=30) as response:
            require(response.geturl() == URL and response.status == 200, 'Unexpected response URL/status')
            length = response.headers.get('Content-Length')
            require(length is None or 0 < int(length) <= LIMIT, 'Declared response size limit')
            require(response.headers.get('Content-Encoding', 'identity') == 'identity', 'Encoded response rejected')
            raw = response.read(LIMIT + 1)
            reservation.update(bytes_received=len(raw), sha256=sha(raw),
                               content_type=response.headers.get('Content-Type', ''),
                               content_length=length, md5=hashlib.md5(raw).hexdigest())
        fmt = check_payload(raw, reservation['content_type'], length)
        target = ROOT / 'local_source' / FILENAME
        target.parent.mkdir(exist_ok=True)
        with target.open('xb') as f:
            f.write(raw)
        reservation.update(status='verified_download_only', detected_format=fmt, local_path=str(target))
    except Exception as e:
        reservation.update(status='failed', error_type=type(e).__name__, error=str(e))
        raise
    finally:
        reservation['elapsed_seconds'] = round(time.monotonic() - start, 3)
        reservation['frozen_after'] = frozen_hashes()
        reservation['frozen_unchanged'] = before == reservation['frozen_after']
        write_json(receipt_path, reservation)
    print(json.dumps({k: reservation[k] for k in ('status', 'bytes_received', 'sha256',
                                                 'detected_format', 'frozen_unchanged')}))

def screen_text(text):
    import importlib.util
    sys.dont_write_bytecode = True
    cfg = json.loads((BUNDLE / 'gateway/config.json').read_text(encoding='utf-8'))
    path = ROOT.parents[1] / 'cohort_harness/_vendor/literature_gateway.py'
    spec = importlib.util.spec_from_file_location('probe_original_screen', path)
    gateway = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = gateway
    spec.loader.exec_module(gateway)
    # Pure screening only: no Session, preparation or source registration.
    gateway.Screen(cfg).check(text)

if __name__ == '__main__':
    require(sys.argv[1:] == ['download'], 'Only command: download')
    download()

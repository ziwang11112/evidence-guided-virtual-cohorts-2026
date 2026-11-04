"""Prepare exact allowlisted public payload. No network write or Git operation."""
from pathlib import Path
import base64
import csv
import hashlib
import json
import posixpath
import re
from urllib.parse import unquote, urlsplit

R = Path(__file__).resolve().parent
P = R.parents[1]
W = P.parents[1]
CHECKOUT = P.parent / 'github_virtual_cohort_2026-10-27'
PREFIX = 'biomedical_research/virtual_cohort_system/'
UNIT = R.name
DEST = PREFIX + 'reports/' + UNIT + '/'
SHA = lambda b: hashlib.sha256(b).hexdigest()
READ = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
SECRET = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{30,})\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
LINK = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')
TOP = [
 'RESULTS.md', 'PROTOCOL.json', 'PROTOCOL_v0_acquisition.json', 'PROTOCOL_DEPENDENCY_AMENDMENT.json',
 'CONTROL.json', 'BATCH_CLOSURE.json', 'ENDPOINT_CONTRACT.json', 'STATE.json', 'STATE_before_completion.json',
 'RUNTIME_PREFLIGHT.json', 'ROOT_CONTROL_REVIEW.json', 'RUNNER_INDEPENDENT_REVIEW.md',
 'RUNNER_REUSE_AUDIT.md', 'PROTOCOL_REVIEW.md', 'EVALUATOR_INDEPENDENT_REVIEW.md',
 'EVALUATOR_V1_BUG_DIAGNOSIS.json', 'EVALUATOR_V2_CORRECTION.json', 'EVALUATOR_V2_INDEPENDENT_REVIEW.md',
 'INDEPENDENT_NUMERICAL_AUDIT.md', 'SCIENTIFIC_INTERPRETATION_REVIEW.md', 'REPORT_AND_FIGURE_REVIEW.md',
 'SOURCE_PROPOSAL_REVIEW_E02_ADDENDUM.md', 'E01_PREFREEZE_MECHANICAL_REPAIR.json',
 'runner.py', 'evaluator.py', 'evaluator_v2.py', 'independent_numerical_audit.py',
 'test_runner.py', 'test_runner_independent_review.py', 'test_evaluator.py', 'test_evaluator_v2.py',
 'prepare_batch.py', 'build_result_display.py', 'PUBLIC_SCOPE.md', 'export_public.py',
]
for author in ('C01', 'C02', 'E01', 'E02'):
    TOP += [f'SOURCE_PROPOSAL_REVIEW_{author}.md', f'{author}_INITIAL_STATIC_REVIEW.json',
            f'{author}_FINAL_DECISION_REVIEW.json']
RELS = TOP + [
 'evaluation/RESULTS.json', 'evaluation/ALL_ENDPOINTS.csv', 'evaluation/EVALUATION_COMPLETED.json',
 'evaluation_v2/RESULTS.json', 'evaluation_v2/ALL_ENDPOINTS.csv', 'evaluation_v2/EVALUATION_COMPLETED.json',
 'evaluation_v2/independent_numerical_audit/RESULTS.json',
 'evaluation_v2/independent_numerical_audit/AUDIT_COMPLETED.json',
 'display/PRIMARY_SUMMARY.csv', 'display/DIAGNOSTIC_SUMMARY.csv', 'display/ALL_DIAGNOSTICS.md',
 'display/primary_analyses.png', 'display/primary_analyses.svg', 'display/primary_analyses.pdf',
 'display/DISPLAY_MANIFEST.json',
]
mapping = {DEST + n: R / n for n in RELS}
for aid in ('C01', 'C02', 'E01', 'E02'):
    bundle = W / ('evcRep' + aid)
    for name in ('generator.py', 'model_spec.json', 'evidence.json', 'source_semantics_v1.json',
                 'whole_cohort_feedback.json', 'checks.json', 'decision.md', 'freeze.json'):
        mapping[DEST + f'authors/{aid}/' + name] = bundle / 'candidates/initial' / name
    for name in ('task.json', 'request.json', 'FINAL_DECISION.json', 'FEEDBACK_RESPONSE.md'):
        mapping[DEST + f'authors/{aid}/' + name] = bundle / name
mapping[PREFIX + 'docs/CURRENT_RESEARCH_FOCUS.md'] = P / 'docs/CURRENT_RESEARCH_FOCUS.md'
mapping['README.md'] = R / 'ROOT_README.md'

audit = READ(R / 'evaluation_v2/independent_numerical_audit/RESULTS.json')
assert audit['status'] == 'PASS'
for directory, marker, output_key in (
    ('evaluation', 'EVALUATION_COMPLETED.json', 'outputs'),
    ('evaluation_v2', 'EVALUATION_COMPLETED.json', 'outputs')):
    for name, digest in READ(R / directory / marker)[output_key].items():
        assert SHA((R / directory / name).read_bytes()) == digest, name
assert SHA((R/'evaluation_v2/RESULTS.json').read_bytes()) == audit['evaluation_outputs']['RESULTS.json']
available = set(mapping) | {p.relative_to(CHECKOUT).as_posix() for p in CHECKOUT.rglob('*')
                            if p.is_file() and '.git' not in p.relative_to(CHECKOUT).parts}
rewrites = []
def rewrite(raw, target):
    text = raw.decode('utf-8-sig')
    def sub(match):
        label, value = match.groups()
        value = value.strip('<>')
        url = urlsplit(value)
        if url.scheme in ('https','http','mailto') or value.startswith('#'):
            return match.group(0)
        assert not url.scheme and not url.netloc and not value.startswith('/'), (target, value)
        path = re.sub(r'(^|/)work/', r'\1reports/', unquote(url.path))
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(target), path))
        if resolved not in available and '/reports/' in '/'+resolved:
            suffix = ('/'+resolved).split('/reports/',1)[1]
            matches = [p for p in available if p.endswith('/reports/'+suffix)]
            if len(matches) == 1: resolved = matches[0]
        assert resolved in available, (target, value, resolved)
        new = posixpath.relpath(resolved, posixpath.dirname(target))
        if url.query: new += '?'+url.query
        if url.fragment: new += '#'+url.fragment
        if ' ' in new: new = '<'+new+'>'
        if new != value: rewrites.append({'path':target,'old':value,'new':new})
        return label+'('+new+')'
    return LINK.sub(sub,text).encode('utf-8')

entries = []
records = []
for target, path in sorted(mapping.items()):
    assert path.is_file(), path
    raw = path.read_bytes()
    assert len(raw) < 2_000_000, (target, len(raw))
    assert path.suffix in ('.md','.json','.py','.csv','.png','.svg','.pdf'), target
    public = rewrite(raw,target) if path.suffix == '.md' else raw
    if path.suffix not in ('.png','.pdf'):
        text = public.decode('utf-8-sig')
        assert not SECRET.search(text), target
        if path.suffix != '.py':
            assert '<article ' not in text and '<!DOCTYPE article' not in text, target
        if path.suffix == '.csv':
            fields = next(csv.reader(text.splitlines()))
            assert ('endpoint' in fields or 'diagnostic' in fields), (target,fields)
        entry = {'path':target,'mode':'100644','type':'blob','content':text}
    else:
        assert (path.suffix == '.png' and public.startswith(b'\x89PNG')) or (path.suffix == '.pdf' and public.startswith(b'%PDF-'))
        assert path.name in ('primary_analyses.png','primary_analyses.pdf')
        entry = {'path':target,'mode':'100644','type':'blob','content_base64':base64.b64encode(public).decode('ascii')}
    entries.append(entry)
    records.append({'path':target,'source':str(path),'source_sha256':SHA(raw),'public_sha256':SHA(public),'bytes':len(public)})
manifest = {'scope':'Allowlisted original code/prose, scientific specifications, metadata and aggregate results only',
            'file_count':len(records),'total_bytes':sum(x['bytes'] for x in records),'files':records,
            'markdown_link_rewrites':rewrites,'clinical_or_generated_rows_included':False,
            'full_third_party_originals_included':False,'independent_numeric_audit_status':audit['status']}
(R/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
(R/'PUBLIC_PAYLOAD.json').write_text(json.dumps(entries,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'files':len(records),'bytes':manifest['total_bytes'],'rewritten_links':len(rewrites),'manifest_sha256':SHA((R/'PUBLIC_MANIFEST.json').read_bytes())}))

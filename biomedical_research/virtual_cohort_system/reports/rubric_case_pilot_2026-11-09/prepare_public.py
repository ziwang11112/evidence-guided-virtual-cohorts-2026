"""Export an audited, aggregate-only pilot; never upload source originals or rows."""
from pathlib import Path
import base64
import hashlib
import importlib.util
import json
import posixpath
import re
import sys

sys.dont_write_bytecode = True
UNIT = Path(__file__).resolve().parent
PROJECT = UNIT.parents[1]
MIRROR = PROJECT.parent / 'github_virtual_cohort_2026-10-27'
PREFIX = 'biomedical_research/virtual_cohort_system/'
BASE = 'c56b4db8a5d57155ebc1070e30f91c4b38edff7f'
REL = UNIT.relative_to(PROJECT).as_posix()
spec = importlib.util.spec_from_file_location('public_helpers', PROJECT / 'work/manuscript_v16_2026-11-05/prepare_public_v16.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    head, tree = h.read_tree(MIRROR)
    assert head == BASE and not h.git(MIRROR, 'status', '--porcelain').strip()
    assert h.git(MIRROR, 'ls-remote', 'origin', 'refs/heads/main').decode().split()[0] == head
    sys.path.insert(0, str(UNIT))
    import runner
    runner.closure_gate()
    review = json.loads((UNIT / 'INDEPENDENT_RESULT_REVIEW.json').read_bytes())
    assert review['decision'] == 'PASS_AGGREGATE_REPORTING'
    for path, digest in review['bound_files'].items():
        assert sha((UNIT / path).read_bytes()) == digest, path
    names = ['PROTOCOL.json', 'CURATED_INPUTS.json', 'ENDPOINT_CONTRACT.json', 'AUTHOR_DISPATCH.json',
        'EVALUATION_SPEC.md', 'REUSE_NOTES.md', 'PRE_AUTHOR_AMENDMENT.md',
        'DESIGN_LOCK.v0.json', 'DESIGN_LOCK.json', 'DESIGN_REVIEW.json', 'DESIGN_REVIEW.md',
        'IMPLEMENTATION_REVIEW.json', 'IMPLEMENTATION_REVIEW.md', 'IMPLEMENTATION_REVIEW_BLOCKED_v0.json',
        'IMPLEMENTATION_REVIEW_BLOCKED_v0.md', 'IMPLEMENTATION_FIX_RECORD.json', 'BATCH_LOCK.json', 'BATCH_CLOSURE.json',
        'runner.py', 'evaluate.py', 'test_runner.py', 'test_evaluate.py', 'prepare_public.py',
        'EVALUATION.json', 'EVALUATION.md', 'EVALUATION_STARTED.json', 'EVALUATION_COMPLETED.json',
        'INDEPENDENT_RESULT_REVIEW.json', 'INDEPENDENT_RESULT_REVIEW.md', 'independent_recompute.py', 'RECOMPUTATION.json',
        'PROCESS_REVIEW.json', 'PROCESS_REVIEW.md',
        'RESULTS.md', 'STATE.json', 'plot_results.py', 'primary_analyses.png', 'primary_analyses.pdf']
    names += [p.relative_to(UNIT).as_posix() for d in ('common','skills','rubrics') for p in (UNIT/d).rglob('*.md')]
    for author in runner.AUTHORS:
        names += [f'bundles/{author}/{n}' for n in ('REQUEST.md','task.json','request.json','registry.json')]
        if author[1] != 'A': names.append(f'bundles/{author}/TASK_RUBRIC.md')
        if author[0] == 'L': names.append(f'bundles/{author}/input/population_metadata.json')
        names += [f'bundles/{author}/output/{n}' for n in sorted(runner.OUTPUT_FILES)]
    paths = [REL + '/' + n for n in names]
    def dest(rel):
        return PREFIX + rel.replace('work/', 'reports/', 1)
    index_dest = dest(REL + '/PUBLIC_EXPORT_INDEX.json')
    available = set(tree) | {dest(x) for x in paths} | {index_dest}
    rows, checked, rewrites, payload = [], [], [], {}
    for rel in paths:
        raw = (PROJECT / rel).read_bytes()
        prepared = raw
        if rel.endswith('.md'):
            def local_link(match):
                original=match.group(1).strip('<>').lstrip('/')
                absolute=Path(original)
                local=absolute.resolve().relative_to(PROJECT.resolve()).as_posix()
                relative=posixpath.relpath(local,posixpath.dirname(rel))
                rewrites.append({'local_document':rel,'local_link':original,'public_relative':relative})
                return ']('+relative+')'
            prepared=re.sub(r'\]\((<?/?[A-Za-z]:[/\\][^\n)]+)\)',local_link,raw.decode('utf8')).encode('utf8')
        data = h.rewrite_markdown(prepared, rel, dest(rel), available, rewrites, checked) if rel.endswith('.md') else raw
        # Original local paths in audit documents become project-relative public derivatives.
        if not rel.endswith(('.png','.pdf')):
            data = data.replace(str(PROJECT).replace('\\','/').encode() + b'/', b'')
            data = data.replace(str(PROJECT).replace('/','\\').encode() + b'\\', b'')
            assert not re.search(rb'(?<![A-Za-z])[A-Za-z]:[\\/]', data), rel
            assert not re.search(rb'(?i)(?:sk-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{20,})', data), rel
        oid = h.git_blob(data)
        h.atomic_write(UNIT/'public_transport'/oid, data)
        payload[oid] = data
        rows.append({'path':dest(rel),'local':rel,'local_sha256':sha(raw),'public_sha256':sha(data),
            'git_blob_sha':oid,'bytes':len(data),'transport_file':'public_transport/'+oid,
            'same_as_base':tree.get(dest(rel))==oid})
    index = {'scope':'Original code, prompts, authored generators/specifications, provenance and scalar results. No real/generated participant tables or full third-party sources.',
        'hash_scope':'Bindings retain local-original hashes; this index maps path/link derivatives to public bytes. Source originals and isolated receipts remain local. This is not a packaged model API launcher.',
        'base_head':head,'files':[{k:r[k] for k in ('path','local','local_sha256','public_sha256','bytes')} for r in rows]}
    data=(json.dumps(index,indent=2)+'\n').encode();h.atomic_write(UNIT/'PUBLIC_EXPORT_INDEX.json',data)
    oid=h.git_blob(data);payload[oid]=data;h.atomic_write(UNIT/'public_transport'/oid,data)
    rows.append({'path':index_dest,'local':REL+'/PUBLIC_EXPORT_INDEX.json','local_sha256':sha(data),'public_sha256':sha(data),
        'git_blob_sha':oid,'bytes':len(data),'transport_file':'public_transport/'+oid,'same_as_base':tree.get(index_dest)==oid})
    manifest={'base_head':head,'files':rows,'relative_links_checked':len(checked),'rewrites':rewrites}
    h.atomic_write(UNIT/'PUBLIC_MANIFEST.json',(json.dumps(manifest,indent=2)+'\n').encode())
    entries,blobs=[],{}
    for row in rows:
        if row['same_as_base']: continue
        oid=row['git_blob_sha'];entries.append({'path':row['path'],'mode':'100644','type':'blob','sha':oid})
        if oid in blobs or oid in set(tree.values()): continue
        data=payload[oid];chunks=[]
        for i,offset in enumerate(range(0,len(data),7200)):
            name=f'{oid}-{i:03d}.txt';h.atomic_write(UNIT/'transport_chunks'/name,base64.b64encode(data[offset:offset+7200]));chunks.append(name)
        blobs[oid]={'chunks':chunks,'encoded_length':4*((len(data)+2)//3)}
    transport={'base':head,'tree':h.git(MIRROR,'rev-parse','HEAD^{tree}').decode().strip(),'entries':entries,'blobs':blobs}
    h.atomic_write(UNIT/'TRANSPORT.json',json.dumps(transport).encode())
    receipt={'status':'PASS_PUBLIC_PLAN','files':len(rows),'bytes':sum(r['bytes'] for r in rows),
        'new_objects':len(blobs),'links_checked':len(checked),'participant_tables':0,
        'manifest_sha256':sha((UNIT/'PUBLIC_MANIFEST.json').read_bytes())}
    h.atomic_write(UNIT/'PUBLIC_EXPORT_QA.json',(json.dumps(receipt,indent=2)+'\n').encode())
    print(json.dumps(receipt))


if __name__=='__main__': main()

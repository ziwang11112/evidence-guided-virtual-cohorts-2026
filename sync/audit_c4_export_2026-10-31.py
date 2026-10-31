"""Exact C4 final export. Metadata checks only; never run scientific code.

Prepared during execution. No paths are selected or copied until a separately
recorded root final release supplies exact source/destination hashes. Run:
  python -B final_export.py prepare --release ROOT_FINAL_EXPORT_RELEASE.json
  python -B final_export.py prepare --release ROOT_FINAL_EXPORT_RELEASE.json --apply
  python -B final_export.py audit --export CHECKOUT --workspace WORKSPACE

Release schema:
 {"status":"root_authorized_final_export", "prior_head":HEAD,
  "custody_export_authorized":false, "readme_append":"reviewed paragraph",
  "files":[{"source":"workspace/relative/path", "destination":"repo/path",
    "sha256":"original file hash", "classification":"authored_or_aggregate",
    "transformations":[], "aggregate_csv_columns":["if applicable"]}],
  "omissions":["specific deliberately absent payload/dependency"]}
Custody files additionally require truth_revealed=true, completed_test_slots=24,
and custody_release={source,sha256} binding a separately issued root reveal gate.
This script records authorization; hashes are not cryptographic signatures.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess

HEAD = '6d11f45b09904260a8ef0959b3984a1b74476f82'
PROJECT = 'biomedical_research/virtual_cohort_system'
SOURCE = PROJECT + '/work/c4/'
CASE = PROJECT + '/reports/c4/'
MANIFEST = 'sync/C4_EXPORT_MANIFEST_2026-10-31.json'
AUDIT = 'sync/C4_EXPORT_AUDIT_2026-10-31.json'
SCRIPT = 'sync/audit_c4_export_2026-10-31.py'
BOUNDARY = 'docs/C4_EXPORT_2026-10-31.md'
FORBIDDEN = {'executions', 'qa', '__pycache__', 'raw', 'downloads', 'history'}
SECRET_PATTERNS = {
    'github_token': r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})',
    'provider_key': r'\bsk-[A-Za-z0-9_-]{20,}',
    'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'aws_access_key': r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b',
}
BOUNDARY_TEXT = '''# C4 bounded final export

This record concerns two explicitly artificial tasks. It does not establish
clinical utility, published-evidence validity or general policy superiority.
All policy choices, candidate versions and adverse findings belong in the
released report. Individual fictional tables remain local.

The curated mapping is `virtual_cohort_system/work/c4/` to
`virtual_cohort_system/reports/c4/`. Scientific code, JSON and frozen recipe
bytes remain unchanged. Only explicitly recorded Markdown navigation changes
are permitted in the new project result document. Original paths/hashes remain
provenance references, not promises that omitted execution payloads are present.
Original relative `work/` dependencies must be reconstructed in a separate
working copy before any separately authorized execution; this export does not
authorize reruns or hidden-information feedback to an author.

The final manifest records the exact released sources, original/export hashes,
navigation transformations, custody-release gate and exclusions. The audit is a
file/metadata check, not a rerun of generation, tests, selection or evaluation.
Hidden fictional truth/evaluator files are eligible only after a separate root
release confirms all 24 test commitments and truth reveal. Generated execution
trees, test fixture directories, row tables, state/history, secrets and machine
identity-bearing JUnit files are excluded. The root README is the only possible
historical edit; every other previously tracked blob must remain byte-identical.
'''

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode()

def safe(root, name):
    path = root/name
    if Path(name).is_absolute() or '..' in Path(name).parts or path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError('Unsafe path: '+name)
    return path

def git(root, *args):
    return subprocess.check_output(['git',*args],cwd=root)

def personal_rows(obj):
    if isinstance(obj,dict):
        if {'row_id','x','y','z'} <= set(obj) and all(not isinstance(obj[k],(dict,list)) for k in ('row_id','x','y','z')):
            return True
        return any(personal_rows(v) for v in obj.values())
    return isinstance(obj,list) and any(personal_rows(v) for v in obj)

def inspect_record(record, raw):
    name=record['destination']; suffix=Path(name).suffix
    if FORBIDDEN & set(Path(name).parts) or Path(name).name in {'STATE.json','STATE_HISTORY.jsonl'}:
        raise ValueError('Excluded payload path: '+name)
    if '/method/qa' in name.lower():
        raise ValueError('Excluded generated test fixture: '+name)
    if suffix not in {'.py','.json','.md','.csv','.txt','.log','.png','.pdf','.svg'}:
        raise ValueError('Unreleased file type: '+name)
    if suffix in {'.png','.pdf','.svg'}:
        return
    text=raw.decode('utf-8-sig')
    for rule,pattern in SECRET_PATTERNS.items():
        if re.search(pattern,text):
            raise ValueError(rule+': '+name)
    if re.search(r'\bDESKTOP-[A-Za-z0-9]+\b|/(?:home|Users)/[A-Za-z0-9_.-]+/',text):
        raise ValueError('Machine identity requires explicit privacy adjudication: '+name)
    if suffix=='.py':
        ast.parse(text)  # Never import submitted/controller/evaluator code.
    elif suffix=='.json':
        if personal_rows(json.loads(text)):
            raise ValueError('Possible individual rows: '+name)
    elif suffix=='.csv':
        reader=csv.DictReader(io.StringIO(text)); rows=list(reader)
        if reader.fieldnames!=record.get('aggregate_csv_columns') or personal_rows(rows):
            raise ValueError('Unreviewed aggregate CSV schema: '+name)
    elif suffix in {'.txt','.log'}:
        if not name.startswith(CASE+'method/') or not re.fullmatch(r'\.+\s+\[100%\]\s+\d+ passed in [\d.]+s\s*',text):
            raise ValueError('Only a clean final mock-test summary is permitted: '+name)

def c4_metadata(root, manifest, fail):
    """Check released aggregate commitments only, never resolve execution paths."""
    case=root/CASE; verified=0; omitted=0
    records={x['destination']:x for x in manifest['files']}
    def read(name): return json.loads(safe(case,name).read_bytes())
    def digest(obj): return sha(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
    def bind(name,expected,label,optional=False,project=False):
        nonlocal verified,omitted
        destination=(PROJECT+'/' if project else CASE)+name
        path=safe(root,destination)
        if not path.is_file():
            if optional: omitted+=1; return
            fail('metadata_binding_absent',binding=label,path=destination); return
        record=records.get(destination)
        actual=record['source_sha256'] if record and record['transformations'] else sha(path.read_bytes())
        verified+=1
        if actual!=expected: fail('metadata_binding_mismatch',binding=label,path=destination)
    commitment=read('TASK_COMMITMENT.json'); admission=read('SOURCE_ADMISSION.json')
    bind('TASK_ADMISSION.md',commitment['admission_document_sha256'],'task_admission')
    for name,expected in {**commitment['visible_artifacts'],**commitment['hidden_artifacts']}.items(): bind(name,expected,'task_commitment')
    bind('TASK_COMMITMENT.json',admission['commitment_sha256'],'source_admission')
    for name,expected in admission['visible_artifacts'].items(): bind(name,expected,'admitted_visible')
    plan=read('method/plan.json'); pool=read('method/pool.json'); selection=read('method/selection.json')
    pre=read('PREEXECUTION_BINDINGS.json')
    for name,key in [('PROTOCOL.md','protocol_sha256'),('TASK_COMMITMENT.json','task_commitment_sha256'),
                     ('SOURCE_ADMISSION.json','source_admission_sha256'),('method/plan.json','plan_sha256'),
                     ('method/controller.py','controller_sha256'),('method/test_log.txt','test_log_sha256')]: bind(name,pre[key],'preexecution')
    for task,entries in pool['cases'].items():
        bind('b/'+task+'/task.json',plan['cases'][task]['task_sha256'],'planned_task')
        bind('visible/'+task+'/source_contract.json',plan['cases'][task]['source_sha256'],'planned_source')
        for item in entries:
            for name,key in [('freeze.json','freeze_sha256'),('generator.py','generator_sha256'),('model_spec.json','spec_sha256')]:
                bind('b/'+task+'/candidates/'+item['name']+'/'+name,item[key],'frozen_pool')
    for obj,label in [(pool,'pool'),(selection,'selection')]: bind('method/plan.json',obj['plan_sha256'],label)
    bind('method/pool.json',selection['pool_sha256'],'selection')
    rows_by_phase={}; total_checks=0; expected_stats=set()
    for phase,prefix in [('feedback','f'),('election','e'),('test','t')]:
        rows=[]; release=read('RELEASE_'+phase+'.json'); receipt=read(phase+'_COMPLETED.json')
        bind('method/plan.json',release['plan_sha256'],phase+'_release')
        bind('method/plan.json',receipt['plan_sha256'],phase+'_receipt')
        bind('RELEASE_'+phase+'.json',receipt['release_sha256'],phase+'_receipt')
        if phase!='feedback': bind('method/pool.json',release['pool_sha256'],phase+'_release')
        if phase=='test': bind('method/selection.json',release['selection_sha256'],'test_release')
        for task,entries in pool['cases'].items():
            for index,item in enumerate(entries[:1] if phase=='feedback' else entries):
                for seed in plan['seeds'][phase]:
                    name=f'stats/{prefix}_{task}_{index}_{seed}.json'; expected_stats.add(CASE+name); row=read(name); rows.append(row)
                    if row['phase']!=phase or row['case']!=task or row['seed']!=seed or row['candidate']!=item:
                        fail('source_diagnostic_identity',file=name)
                    if len(row['checks'])!=commitment['source_checks_per_case'][task] or row['fixed_denominator']!=len(row['checks']):
                        fail('source_diagnostic_denominator',file=name)
                    total_checks+=len(row['checks'])
                    bind('method/plan.json',row['plan_sha256'],'diagnostic_plan')
                    bind('visible/'+task+'/source_contract.json',row['source_sha256'],'diagnostic_source')
        if len(rows)!=receipt['scheduled_slots'] or len(rows)!=receipt['computed_slots'] or digest(rows)!=receipt['aggregate_digest_sha256']:
            fail('phase_aggregate_commitment',phase=phase)
        rows_by_phase[phase]=rows
    actual_stats={name for name in records if name.startswith(CASE+'stats/')}
    if actual_stats!=expected_stats: fail('incomplete_source_diagnostic_export')
    if digest(rows_by_phase['feedback'])!=pool['feedback_sha256'] or digest(rows_by_phase['election'])!=selection['election_sha256']:
        fail('feedback_or_election_seal')
    gate=read('REVEAL_GATE.json'); outputs=read('TEST_OUTPUT_MANIFEST.json')
    for name,key in [('method/selection.json','selection_sha256'),('TASK_COMMITMENT.json','task_commitment_sha256'),
                     ('TEST_OUTPUT_MANIFEST.json','test_outputs_manifest_sha256'),('test_COMPLETED.json','test_completed_receipt_sha256')]: bind(name,gate[key],'reveal_gate')
    if not gate['all_test_outputs_committed'] or gate['test_table_count']!=24 or len(outputs['entries'])!=24:
        fail('reveal_gate_test_commitments')
    table_hashes=set()
    for entry in outputs['entries']:
        bind(entry['diagnostic_path'],entry['diagnostic_sha256'],'test_output_diagnostic')
        row=read(entry['diagnostic_path'])
        if row['table_sha256']!=entry['table_sha256']: fail('recorded_test_table_hash')
        table_hashes.add(entry['table_sha256'])
    if len(table_hashes)!=gate['unique_test_table_contents']: fail('recorded_unique_table_count')
    receipt=read('results/EVALUATION_RECEIPT.json')
    for name,key in [('results/evaluate_committed_tables.py','adapter_sha256'),('custody/evaluate.py','evaluator_sha256'),
                     ('custody/evaluate_contract.json','evaluation_contract_sha256'),('REVEAL_GATE.json','reveal_gate_sha256')]: bind(name,receipt[key],'evaluation_receipt')
    for name,expected in receipt['aggregate_artifacts'].items(): bind('results/'+name,expected,'evaluation_aggregate')
    for entry in receipt['per_table_evaluations']: bind(entry['path'],entry['sha256'],'per_table_evaluation')
    report=read('results/REPORT_MANIFEST.json')
    for name,expected in report['files'].items():
        target=name if (case/name).is_file() else 'results/'+name
        bind(target,expected,'report_manifest')
    pool_review=read('review/POOL_BINDINGS.json')
    for name,expected in pool_review['bound_public_artifacts'].items(): bind(name,expected,'pool_review',optional=True)
    postrun=read('review/POSTRUN_INPUT_HASHES.json')
    for name,expected in postrun.items():
        if name.startswith('work/c4/'): bind(name[len('work/c4/'):],expected,'independent_input',optional=True)
        elif name.startswith('cohort_harness/'): bind(name,expected,'independent_engine',optional=True,project=True)
    for name in ['CLOSEOUT.json','review/FINAL_BINDINGS.json']:
        if (case/name).is_file():
            obj=read(name)
            for field in ['files','bindings']:
                for target,expected in obj.get(field,{}).items():
                    if isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected): bind(target,expected,name)
            for target,expected in obj.get('project_relative_files',{}).items(): bind(target,expected,name,project=True)
            for target,expected in obj.get('artifact_sha256',{}).items():
                if target.startswith('work/c4/'): bind(target[len('work/c4/'):],expected,name)
                else: bind(target,expected,name,project=True)
            if 'root_report' in obj: bind(obj['root_report']['path'],obj['root_report']['sha256'],name,project=True)
    return {'verified':verified,'deliberately_omitted_payload_bindings':omitted,'source_diagnostic_files':len(expected_stats),
            'source_statistic_entries':total_checks,'test_slots':len(outputs['entries']),'recorded_unique_test_contents':len(table_hashes)}

def prepare(args):
    workspace=args.workspace.resolve(strict=True); root=args.export.resolve(strict=True)
    release_raw=args.release.read_bytes(); release=json.loads(release_raw)
    assert release['status']=='root_authorized_final_export' and release['prior_head']==HEAD
    assert release['export_script_sha256']==sha(Path(__file__).read_bytes()), 'Export script differs from the reviewed release'
    assert git(root,'rev-parse','HEAD').decode().strip()==HEAD
    assert not git(root,'status','--porcelain'), 'Final preparation requires the clean expected checkout'
    tracked=set(git(root,'ls-files').decode().splitlines())
    hidden=any('/custody/' in x['source'] for x in release['files'])
    if hidden:
        assert release.get('custody_export_authorized') is True and release.get('truth_revealed') is True
        assert release.get('completed_test_slots')==24
        gate=release['custody_release']
        assert gate['source'].startswith(SOURCE) and '/custody/' not in gate['source']
        assert sha(safe(workspace,gate['source']).read_bytes())==gate['sha256']
        assert any(x['source']==gate['source'] and x['sha256']==gate['sha256'] for x in release['files'])
    records=[]; pending={}
    for item in release['files']:
        name=item['destination']; source=item['source']
        assert source.startswith(SOURCE) or source.startswith(PROJECT+'/docs/'), source
        assert (name==source.replace(SOURCE,CASE,1) if source.startswith(SOURCE) else name==source)
        assert name not in tracked and name not in pending and not (root/name).exists(), name
        assert not FORBIDDEN & set(Path(source).parts), source
        raw=safe(workspace,source).read_bytes(); assert sha(raw)==item['sha256'], source
        inspect_record(item,raw)
        transformations=item.get('transformations',[])
        if transformations:
            assert source.startswith(PROJECT+'/docs/') and source.endswith('.md')
            assert transformations==[['](../work/c4/','](../reports/c4/']]
        out=raw
        for old,new in transformations:
            out=out.replace(old.encode(),new.encode())
        record={**item,'source_sha256':sha(raw),'source_bytes':len(raw),
                'export_sha256':sha(out),'export_bytes':len(out),'transformations':transformations}
        records.append(record); pending[name]=out
    support={SCRIPT:Path(__file__).read_bytes(),BOUNDARY:BOUNDARY_TEXT.encode()}
    for name in support:
        assert name not in tracked and name not in pending and not (root/name).exists()
    readme=None
    if release.get('readme_append'):
        original=git(root,'show',HEAD+':README.md')
        assert (root/'README.md').read_bytes()==original
        out=original+b'\n'+release['readme_append'].strip().encode()+b'\n'
        readme={'prior_sha256':sha(original),'export_sha256':sha(out),'append':release['readme_append']}
        pending['README.md']=out
    pending.update(support)
    expected=sorted(set(pending)|{MANIFEST,AUDIT})
    manifest={'schema_version':1,'status':'prepared_for_root_review_no_stage_commit_or_push','prior_head':HEAD,
        'root_final_release':release,'root_final_release_sha256':sha(release_raw),'files':records,
        'generated_support':{name:{'sha256':sha(raw),'bytes':len(raw)} for name,raw in support.items()},
        'intentional_readme_append':readme,'expected_delta':expected,'omissions':release.get('omissions',[])}
    print(json.dumps({'mode':'apply' if args.apply else 'plan_only','released_source_files':len(records),
                      'new_files':len(expected)-bool(readme),'historical_edits':int(bool(readme))}))
    if not args.apply:
        return
    for name,raw in pending.items():
        path=safe(root,name); path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
    safe(root,MANIFEST).write_bytes(encoded(manifest))
    audit(args)
    # Local command input only: this script never invokes git add, commit or push.
    (args.release.parent/'STAGED_PATHS.txt').write_text('\n'.join(expected)+'\n',encoding='utf-8')

def audit(args):
    workspace=args.workspace.resolve(strict=True); root=args.export.resolve(strict=True)
    manifest_raw=safe(root,MANIFEST).read_bytes(); manifest=json.loads(manifest_raw)
    findings=[]; old_count=0; frozen_bindings=0
    def fail(rule,**detail): findings.append({'rule':rule,**detail})
    expected=set(manifest['expected_delta']); allowed={'README.md'} if manifest['intentional_readme_append'] else set()
    actual=set(git(root,'diff','--name-only',HEAD).decode().splitlines())
    actual.update(git(root,'ls-files','--others').decode().splitlines()); actual.add(AUDIT)
    if actual!=expected: fail('unexpected_delta',missing=sorted(expected-actual),unexpected=sorted(actual-expected))
    if git(root,'rev-parse','HEAD').decode().strip()!=HEAD: fail('head_changed')
    for entry in git(root,'ls-tree','-rz',HEAD).split(b'\0'):
        if not entry: continue
        metadata,name_raw=entry.split(b'\t',1); _,kind,object_id=metadata.decode().split(); name=name_raw.decode()
        if name in allowed: continue
        path=safe(root,name)
        if os.name=='nt': path=Path('\\\\?\\'+str(path))
        raw=path.read_bytes(); old_count+=1
        if kind!='blob' or hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()!=object_id:
            fail('historical_blob_changed',file=name)
    for record in manifest['files']:
        path=safe(root,record['destination']); raw=path.read_bytes(); source=safe(workspace,record['source']).read_bytes()
        if sha(source)!=record['source_sha256'] or sha(raw)!=record['export_sha256']: fail('file_binding',file=record['destination'])
        try: inspect_record(record,raw)
        except Exception as error: fail('privacy_or_schema',file=record['destination'],detail=str(error))
        out=source
        for old,new in record['transformations']: out=out.replace(old.encode(),new.encode())
        if out!=raw: fail('unrecorded_transform',file=record['destination'])
        if path.name=='freeze.json' and '/candidates/' in record['destination']:
            frozen=json.loads(raw); bundle=path.parents[2]
            for name,digest in frozen['commitments'].items():
                target=safe(bundle,name); frozen_bindings+=1
                if not target.is_file() or sha(target.read_bytes())!=digest: fail('frozen_recipe_binding',file=record['destination'],binding=name)
            snapshot=frozen['registry_snapshot']
            registry=json.loads(safe(bundle,snapshot['path']).read_bytes())['artifacts'][:snapshot['artifact_count']]
            actual=sha(json.dumps(registry,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
            if actual!=snapshot['sha256']: fail('frozen_registry_snapshot',file=record['destination'])
            present={p.relative_to(bundle).as_posix() for p in path.parent.rglob('*') if p.is_file() and p.name!='freeze.json'}
            if present!=set(frozen['candidate_files']): fail('frozen_candidate_file_set',file=record['destination'])
    for name,record in manifest['generated_support'].items():
        if sha(safe(root,name).read_bytes())!=record['sha256']: fail('support_file_binding',file=name)
    if allowed:
        record=manifest['intentional_readme_append']; original=git(root,'show',HEAD+':README.md')
        expected_readme=original+b'\n'+record['append'].strip().encode()+b'\n'
        if sha(original)!=record['prior_sha256'] or (root/'README.md').read_bytes()!=expected_readme:
            fail('readme_append_binding')
    metadata_checks=c4_metadata(root,manifest,fail)
    result={'status':'PASS' if not findings else 'FAIL','prior_head':HEAD,'manifest_sha256':sha(manifest_raw),
        'delta_files':len(expected),'new_files':len(expected)-len(allowed),'intentional_historical_edits':sorted(allowed),
        'historical_blobs_byte_preserved':old_count,'source_files_verified':len(manifest['files']),
        'frozen_recipe_bindings_verified':frozen_bindings,'metadata_checks':metadata_checks,'scientific_execution_or_tests_performed':False,
        'generated_tables_read':False,'staging_commit_push_performed':False,'findings':findings}
    safe(root,AUDIT).write_bytes(encoded(result)); print(json.dumps(result,indent=2)); assert not findings

def main():
    here=Path(__file__).resolve()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['prepare','audit'])
    parser.add_argument('--workspace',type=Path,default=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16'))
    parser.add_argument('--export',type=Path,default=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/github_virtual_cohort_2026-10-27'))
    parser.add_argument('--release',type=Path)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if args.mode=='prepare':
        if args.release is None: parser.error('prepare requires an exact final root release')
        prepare(args)
    else:
        audit(args)

if __name__=='__main__': main()

"""Audit the combined C3 export; never run science, generators, or tests."""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess

MANIFEST = 'sync/C3_COMPLETED_SOURCE_EXPORT_MANIFEST_2026-10-31.json'
AUDIT = 'sync/C3_COMPLETED_SOURCE_EXPORT_AUDIT_2026-10-31.json'
CASE = 'biomedical_research/virtual_cohort_system/reports/c3s'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--export', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--local-receipt', type=Path)
    args = parser.parse_args()
    root, workspace = args.export.resolve(strict=True), args.workspace.resolve(strict=True)
    # Import only our earlier metadata verifier's helper definitions, never project code.
    helper_path = root/'sync/audit_c3_source_preparation_export_2026-10-31.py'
    spec = importlib.util.spec_from_file_location('c3_export_metadata_helpers', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    sha, canonical_sha, safe = helper.sha, helper.canonical_sha, helper.safe
    raw_manifest = (root/MANIFEST).read_bytes()
    manifest = json.loads(raw_manifest)
    findings, missing_bindings, machine_paths, csv_schemas = [], [], [], {}
    counters = {'json':0, 'python':0, 'markdown':0, 'aggregate_csv':0, 'figures':0,
                'raw_bindings':0, 'canonical_bindings':0, 'trial_record_hashes':0}
    def flag(rule, **detail):
        findings.append({'rule':rule, **detail})
    def git(*values):
        return subprocess.check_output(['git',*values],cwd=root)
    def read(path):
        return json.loads(path.read_bytes())
    def binding(path,digest,label):
        counters['raw_bindings'] += 1
        if not path.is_file() or sha(path.read_bytes()) != digest:
            flag('binding_mismatch', binding=label)
    def canonical_binding(obj,digest,label,ensure_ascii=True):
        counters['canonical_bindings'] += 1
        if canonical_sha(obj,ensure_ascii) != digest:
            flag('canonical_binding_mismatch', binding=label)
    before = manifest['prior_head']
    historical_updates={x['destination']:x for x in manifest.get('intentional_historical_updates',[])}
    if set(historical_updates) != {'README.md'}:
        flag('unexpected_historical_update_authorization')
    if git('rev-parse','HEAD').decode().strip() != before:
        flag('head_changed')
    expected = set(manifest['expected_delta'])
    phase2 = {x['destination'] for x in manifest['files']}|{MANIFEST,AUDIT}
    prior = {x['destination'] for x in manifest['preserved_preparation_files']}
    if phase2 != set(manifest['expected_phase2_delta']) or expected != phase2|prior or phase2&prior:
        flag('manifest_sets_inconsistent')
    actual = set(git('diff','--name-only',before).decode().splitlines())
    actual.update(git('ls-files','--others').decode().splitlines())
    actual.add(AUDIT)
    if actual != expected:
        flag('unexpected_delta',missing=sorted(expected-actual),unexpected=sorted(actual-expected))
    old_count, unchanged_count, old_names = 0,0,set()
    for entry in git('ls-tree','-rz',before).split(b'\0'):
        if not entry:
            continue
        meta,name_raw = entry.split(b'\t',1)
        _,kind,object_id = meta.decode().split()
        name = name_raw.decode()
        old_names.add(name)
        if kind != 'blob':
            flag('unexpected_nonblob',file=name)
            continue
        path = safe(root,name)
        if os.name == 'nt':
            path=Path('\\\\?\\'+str(path))
        if not path.is_file():
            flag('historical_file_missing',file=name)
            continue
        raw=path.read_bytes()
        old_count += 1
        if name in historical_updates:
            original=git('show',before+':'+name)
            record=historical_updates[name]
            if record['prior_git_blob']!=object_id or record['prior_sha256']!=sha(original):
                flag('historical_update_prior_binding',file=name)
            continue
        if hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()!=object_id:
            flag('historical_bytes_changed',file=name)
        else:
            unchanged_count+=1
    if old_names & expected != set(historical_updates):
        flag('historical_path_overwrite',files=sorted((old_names&expected)-set(historical_updates)))
    for record in manifest['preserved_preparation_files']:
        binding(root/record['destination'],record['sha256'],'preserved_preparation:'+record['destination'])
    for record in manifest['files']:
        name=record['destination']
        path=safe(root,name)
        raw=path.read_bytes()
        source=safe(workspace,record['source']).read_bytes()
        if sha(raw)!=record['export_sha256'] or len(raw)!=record['export_bytes']:
            flag('export_hash_or_size_mismatch',file=name)
        if sha(source)!=record['source_sha256'] or len(source)!=record['source_bytes']:
            flag('source_changed_since_release',file=name)
        transformed=source
        for old,new in record['transformations']:
            transformed=transformed.replace(old.encode(),new.encode())
        if transformed!=raw:
            flag('unrecorded_transform',file=name)
        if path.suffix in {'.py','.json'} and source!=raw:
            flag('code_or_json_changed',file=name)
        if {'executions','outputs','__pycache__','raw','history'}&set(Path(name).parts) or path.name in {'STATE.json','STATE_HISTORY.jsonl','intent.json'}:
            flag('forbidden_payload',file=name)
        if path.suffix not in {'.md','.py','.json','.csv','.png','.pdf','.svg'}:
            flag('unapproved_extension',file=name)
        if path.suffix in {'.png','.pdf','.svg'}:
            counters['figures']+=1
            continue
        text=raw.decode('utf-8-sig')
        for rule,pattern in helper.SECRET_PATTERNS.items():
            if re.search(pattern,text):
                flag(rule,file=name)
        if re.search(r'\bDESKTOP-[A-Za-z0-9]+\b',text):
            flag('machine_hostname',file=name)
        if re.search(r'[A-Za-z]:[\\/]+(?:Users|AIR-|Codex)|/(?:home|Users)/',text):
            machine_paths.append(name)
        if path.suffix=='.json':
            counters['json']+=1
            if helper.possible_individual_records(json.loads(text)):
                flag('possible_individual_measurement_record',file=name)
        elif path.suffix=='.py':
            counters['python']+=1
            ast.parse(text)
        elif path.suffix=='.md':
            counters['markdown']+=1
        elif path.suffix=='.csv':
            rows=list(csv.DictReader(io.StringIO(text)))
            counters['aggregate_csv']+=1
            csv_schemas[name]={'row_count':len(rows),'columns':list(rows[0]) if rows else []}
            contract_flags = path.name=='output_contracts.csv' and len(rows)==24 and all(
                row[field] in {'True','False'} for row in rows for field in
                ['rows6000','unique_ids','no_missing','age','female','bmi','glucose','hba1c'])
            if helper.possible_individual_records(rows) and not contract_flags:
                flag('possible_individual_csv',file=name)
        if record['classification']=='selected_recipe_short_source_summary' and len(raw)>2000:
            flag('non_summary_source_payload',file=name)

    case=root/CASE
    authorization=read(case/'POSTRUN_ANALYSIS_AUTHORIZATION.json')
    structures={}
    for structure in ['linear','alternative']:
        base=case/structure
        session=base/'source_calibration/s'
        result=read(session/'result.json')
        receipt=read(case/(structure+'_COMPLETED.json'))
        release=read(session/'release.json')
        selection=read(session/'selection.json')
        auth=authorization['complete_results'][structure]
        binding(session/'result.json',receipt['result_sha256'],structure+':receipt_result')
        binding(session/'result.json',auth['sha256'],structure+':authorized_result')
        binding(case/(structure+'_COMPLETED.json'),auth['receipt_sha256'],structure+':authorized_receipt')
        if result['scope']!='source_fit_only_no_target_validation' or result['selected_trial']!=26 or receipt['selected_trial']!=26:
            flag('wrong_session_scope_or_selection',structure=structure)
        if result['binding']!={**release['binding'],'release_sha256':canonical_sha(release)}:
            flag('result_release_binding',structure=structure)
        for name,key in [('plan.json','plan_sha256'),('criteria.json','criteria_sha256')]:
            canonical_binding(read(session/name),result['binding'][key],structure+':'+name)
        canonical_binding(result['engines'],result['binding']['engines_sha256'],structure+':engines')
        trials=result['trials']
        if [t['index'] for t in trials]!=list(range(37)) or len(selection['fit_record_hashes'])!=37:
            flag('trial_transcript_incomplete',structure=structure)
        for trial,digest in zip(trials,selection['fit_record_hashes']):
            raw=(json.dumps(trial,indent=2,ensure_ascii=False)+'\n').encode()
            counters['trial_record_hashes']+=1
            if sha(raw)!=digest:
                flag('retained_trial_record_hash',structure=structure,index=trial['index'])
            if len(trial['parameters'])!=5 or not all(type(v) in {float,int} for v in trial['parameters'].values()):
                flag('non_scalar_trial_parameters',structure=structure,index=trial['index'])
            if len(trial['fit']['constraints'])!=20:
                flag('missing_trial_aggregate_checks',structure=structure,index=trial['index'])
        if set(result['replay'])!={'0','26'}:
            flag('missing_baseline_or_selected_replay',structure=structure)
        for key,records in result['replay'].items():
            if [r['seed'] for r in records]!=[19111,19123] or any(len(r['score']['constraints'])!=20 for r in records):
                flag('incomplete_unused_seed_aggregate_checks',structure=structure,trial=key)
        trialdir=session/'t0026'
        binding(trialdir/'trial.json',selection['fit_record_hashes'][26],structure+':selected_trial_record')
        if read(trialdir/'trial.json')!=trials[26]:
            flag('selected_trial_record_differs',structure=structure)
        bundle=trialdir/'bundle'
        frozen=read(bundle/'candidates/t/freeze.json')
        binding(bundle/'candidates/t/freeze.json',selection['selected_freeze_sha256'],structure+':selected_freeze')
        for name,digest in frozen['commitments'].items():
            binding(bundle/name,digest,structure+':selected_commitment:'+name)
        snapshot=frozen['registry_snapshot']
        canonical_binding(read(bundle/'registry.json')['artifacts'][:snapshot['artifact_count']],snapshot['sha256'],structure+':selected_registry',False)
        available={p.relative_to(bundle).as_posix() for p in (bundle/'candidates/t').rglob('*') if p.is_file() and p.name!='freeze.json'}
        if available!=set(frozen['candidate_files']):
            flag('selected_recipe_incomplete',structure=structure)
        included_hashes=0
        for name,digest in result['files'].items():
            path=safe(session,name)
            if path.is_file():
                binding(path,digest,structure+':result_inventory:'+name)
                included_hashes+=1
        # Original hashes are retained even for intentionally omitted generated files.
        missing_bindings.append({'structure':structure,'result_inventory_count':len(result['files']),
            'included_inventory_files_verified':included_hashes,'deliberately_omitted_count':len(result['files'])-included_hashes})
        budget=base/'calibration_budget'
        config,head=read(budget/'config.json'),read(budget/'head.json')
        events=[read(budget/'events/00000001.json'),read(budget/'events/00000002.json')]
        for name,envelope in [('config',config),('head',head),('event1',events[0]),('event2',events[1])]:
            canonical_binding(envelope['payload'],envelope['sha256'],structure+':budget:'+name)
        if not (events[0]['payload']['previous_sha256']==config['sha256'] and
                events[1]['payload']['previous_sha256']==events[0]['sha256'] and
                events[1]['payload']['status']=='completed' and
                head['payload']['event_count']==2 and head['payload']['last_event_sha256']==events[1]['sha256']):
            flag('budget_chain_incomplete',structure=structure)
        if events[1]['payload']['usage']!=result['usage'] or receipt['usage']!=result['usage']:
            flag('budget_usage_disagrees',structure=structure)
        structures[structure]={'trial_count':len(trials),'selected_trial':26,'checks_per_trial':20,
            'unused_seed_checks':80,'complete_usage':result['usage'],'result_inventory_hashes':len(result['files'])}

    analysis=case/'analysis/audit_v1'
    output_manifest=read(analysis/'OUTPUT_HASH_MANIFEST.json')
    for name,digest in output_manifest['files'].items():
        binding(safe(analysis,name),digest,'independent_output:'+name)
    inputs=read(analysis/'INPUT_HASH_MANIFEST.json')
    input_bindings_checked=0
    source_root=(workspace/'biomedical_research/virtual_cohort_system').as_posix()+'/'
    for name,record in inputs['inputs'].items():
        normalized=name.replace('\\','/')
        if normalized.startswith(source_root):
            relative=normalized[len(source_root):]
            if relative.startswith('work/c3s/'):
                destination=CASE+'/'+relative[len('work/c3s/'):]
            elif relative.startswith('work/autonomous_research_cycle2_2026-10-31/'):
                destination='biomedical_research/virtual_cohort_system/reports/'+relative[len('work/'):]
            else:
                destination='biomedical_research/virtual_cohort_system/'+relative
            path=safe(root,destination)
            if path.is_file():
                binding(path,record['sha256'],'independent_input:'+destination)
                input_bindings_checked+=1
    binding(case/'analysis/independent_audit.py',inputs['script_sha256'],'independent_analysis_code')
    binding(case/'analysis/finalize_audit.py',inputs['finalization_script_sha256'],'independent_report_code')
    final_review=read(case/'review/FINAL_REVIEW_BINDINGS.json')
    for name,digest in final_review['files'].items():
        binding(safe(case,name),digest,'final_review:'+name)
    for name,digest in final_review['project_relative_files'].items():
        destination='biomedical_research/virtual_cohort_system/'+name
        record=next(x for x in manifest['files'] if x['destination']==destination)
        if record['source_sha256']!=digest:
            flag('reviewed_original_document_binding',file=destination)
    closeout=read(case/'CLOSEOUT.json')
    for name,digest in closeout['bindings'].items():
        binding(safe(case,name),digest,'root_closeout:'+name)
    if closeout['status']!='complete_with_tradeoffs' or closeout['future_target_data_access'] or closeout['further_scientific_execution_authorized_in_this_unit']:
        flag('unexpected_closeout_scope')
    if closeout['project_report']['sha256']!=next(x['source_sha256'] for x in manifest['files'] if
            x['destination']=='biomedical_research/virtual_cohort_system/'+closeout['project_report']['path']):
        flag('closeout_original_report_binding')
    qa=read(analysis/'QA.json')
    if qa['status']!='PASS' or qa['check_count']!=len(qa['checks']) or qa['failed_checks'] or qa['visual_review']['status']!='PASS':
        flag('independent_audit_status_or_visual_receipt')

    audit={'status':'PASS' if not findings else 'FAIL','scope':'Combined C3 exact export delta; metadata/file verification only.',
        'prior_head':before,'manifest_sha256':sha(raw_manifest),'expected_delta_file_count':len(expected),
        'new_file_count':len(expected)-len(historical_updates),
        'phase2_file_count':len(phase2),'preserved_preparation_files':len(prior),
        'historical_tracked_blobs_checked':old_count,'historical_tracked_blobs_byte_preserved':unchanged_count,
        'intentional_historical_tracked_edits':list(historical_updates),
        'checked':counters,'structures':structures,'aggregate_csv_schemas':csv_schemas,
        'omitted_generated_file_bindings':missing_bindings,'machine_specific_path_references':machine_paths,
        'independent_input_manifest':{'original_bindings':inputs['input_count'],
            'available_export_bindings_verified':input_bindings_checked,
            'omitted_bindings_preserved_without_reading_payloads':inputs['input_count']-input_bindings_checked},
        'independent_audit_status':qa['status'],'independent_audit_check_count':qa['check_count'],
        'visual_review_receipt':qa['visual_review'],
        'privacy_scope':'Exact root-released authored/aggregate allowlist; excluded intent/runtime/user paths and all cohort/execution payloads; recognizable record and credential screening.',
        'all_code_and_json_byte_preserved':not any(x['rule']=='code_or_json_changed' for x in findings),
        'scientific_execution_performed':False,'scientific_tests_rerun':False,'individual_tables_read':False,
        'commit_or_push_performed':False,'findings':findings,'expected_delta':sorted(expected)}
    raw=(json.dumps(audit,indent=2,ensure_ascii=False)+'\n').encode()
    (root/AUDIT).write_bytes(raw)
    if args.local_receipt:
        args.local_receipt.write_bytes(raw)
    print(json.dumps({k:audit[k] for k in ['status','expected_delta_file_count','new_file_count','phase2_file_count','preserved_preparation_files',
        'historical_tracked_blobs_byte_preserved','intentional_historical_tracked_edits','checked','machine_specific_path_references','findings']},indent=2))
    raise SystemExit(bool(findings))

if __name__=='__main__':
    main()

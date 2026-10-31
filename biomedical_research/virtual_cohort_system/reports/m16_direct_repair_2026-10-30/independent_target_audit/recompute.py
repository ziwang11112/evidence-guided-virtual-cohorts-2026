"""Post-release independent numerical comparison, reusing an independently authored formula implementation.

No canonical evaluator import. No rows or fits until explicit --execute and
release/output hash checks. This is a second computation, not new target feedback.
"""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,io,json,math
from datetime import datetime

HERE=Path(__file__).resolve().parent
R=HERE.parent
INDEPENDENT_SHA256='e2cd4b3cc7720c3d2bc42f5e67dae9c67595534091f1fe0631683f16fc1398da'
BUILDERS=('b1','b2','b3')
CHECKS=('all_builders_closed','preauthorship_verified','feedback_binding_verified',
        'source_exposure_verified','preservation_verified','budgets_verified','independent_code_review_complete')
SCIENCE_FILES=('evidence.json','model_spec.json','audit/construction.json','audit/revision_plan.json')
KEY_MAP={f'global_{k}':f'global.{k}' for k in ('bmi','age','curvature','interaction')}
KEY_MAP.update({f'{stat}_{race}_{sex}':f'group.{race}.{sex}.{stat}'
 for race in ('White','Black') for sex in ('male','female') for stat in ('reverse','mean','sd','median','q90')})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    def pairs(items):
        answer={}
        for key,value in items:
            if key in answer:raise ValueError('Duplicate JSON key')
            answer[key]=value
        return answer
    def invalid(value):raise ValueError('Nonfinite JSON constant: '+value)
    return json.loads(Path(p).read_text(encoding='utf-8-sig'),object_pairs_hook=pairs,parse_constant=invalid)
def rows(raw):
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):raise ValueError('Invalid header')
    result=list(reader)
    if any(None in row or None in row.values() for row in result):raise ValueError('Malformed CSV row')
    return result
def load_independent():
    p=HERE/'frozen_independent.py'
    original=R.parent/'m15b_literature_direct_2026-10-30/independent_target_audit/audit.py'
    if sha(p)!=INDEPENDENT_SHA256 or sha(p)!=sha(original):raise ValueError('Independent arithmetic copy differs')
    spec=importlib.util.spec_from_file_location('m16_independent_frozen',p)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
def exact_records(records,key,expected,label):
    keys=[key(record) for record in records]
    if len(keys)!=len(set(keys)) or set(keys)!=set(expected):
        raise ValueError('Incomplete or duplicate '+label)
def verify_csv_integrity(released,directory):
    """Independently flatten the documented canonical JSON, check both CSVs exactly.

    This checks serialization integrity, not scientific arithmetic. CSV bool/None
    spellings deliberately match Python's ordinary csv.DictWriter contract.
    """
    expected=[]
    for candidate in released['candidate_comparisons']:
        for record in candidate['estimands']:
            flat={'builder':candidate['builder'],'stage':candidate['stage']}
            flat.update({k:v for k,v in record.items() if k not in ('measured','generated')})
            for role in ('measured','generated'):
                flat.update({role+'_'+k:record[role][k] for k in
                             ('value','n','n_complete','rank','n_parameters','status','reason','sign')})
            expected.append(flat)
    files=[('estimands.csv',expected,['builder','stage','estimand']),
           ('initial_final_changes.csv',released['initial_final_changes'],['builder','estimand'])]
    result={}
    for filename,wanted,empty_header in files:
        path=Path(directory)/filename
        raw=path.read_bytes();reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
        actual=list(reader)
        fields=list(wanted[0]) if wanted else empty_header
        if reader.fieldnames!=fields or len(actual)!=len(wanted):raise ValueError('CSV/JSON shape mismatch: '+filename)
        for index,(a,b) in enumerate(zip(actual,wanted)):
            text={key:'' if value is None else str(value) for key,value in b.items()}
            if a!=text:raise ValueError(f'CSV/JSON value mismatch: {filename} row {index}')
        result[filename]={'sha256':hashlib.sha256(raw).hexdigest(),'rows':len(actual),'status':'PASS'}
    return result
def compare_results(implementation,reference,observed,tables,released):
    checks=[];diffs=[]
    def check(a,b,label):
        if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):
            delta=abs(float(a)-float(b));diffs.append(delta)
            ok=math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-9)
        else:ok=a==b
        if not ok:raise ValueError('Independent disagreement: '+label)
        checks.append(label)
    def estimate(ind,canon,label):
        for a,b in [('value','value'),('n','n'),('complete_n','n_complete'),('matrix_rank','rank')]:
            check(ind[a],canon[b],label+'.'+a)
        # Independent engine uses one failure label plus reason; canonical engine
        # uses typed failure labels. Preserve originals, compare success/failure.
        if ind['status'] not in ('ok','failure') or canon['status'] not in ('ok','rank_deficient','nonfinite','insufficient_n','numerical_failure'):
            raise ValueError('Unknown estimate status: '+label)
        check(ind['status']=='ok',canon['status']=='ok',label+'.successful')
    if set(tables)!=set(BUILDERS):raise ValueError('All scheduled builders required')
    exact_records(released['reference_estimands'],lambda r:r['estimand'],KEY_MAP,'reference endpoints')
    exact_records(released['builder_outcomes'],lambda r:r['builder'],BUILDERS,'builder outcomes')
    expected_stages={(bid,stage) for bid,stages in tables.items() for stage in stages}
    exact_records(released['candidate_comparisons'],lambda r:(r['builder'],r['stage']),expected_stages,'candidate stages')
    expected_changes={(bid,key) for bid,stages in tables.items() if set(stages)=={'initial','final'} for key in KEY_MAP}
    exact_records(released['initial_final_changes'],lambda r:(r['builder'],r['estimand']),expected_changes,'initial-final changes')
    exact_records(released['reference_sensitivity']['summaries'],lambda r:r['estimand'],
                  [k for k in KEY_MAP if k.startswith('global_')],'PSU endpoints')
    truth=implementation.estimate_table(reference)
    for canon in released['reference_estimands']:
        estimate(truth[KEY_MAP[canon['estimand']]],canon,'reference.'+canon['estimand'])
    outcomes={r['builder']:r for r in released['builder_outcomes']}
    independent_tables={};preservation={}
    for bid,stages in tables.items():
        if not stages:continue
        initial=stages.get('initial') or stages['final'];final=stages.get('final') or initial
        preserve=implementation.validate_identity_and_covariates(observed,reference,initial,final)
        preservation[bid]=preserve
        if 'initial' in stages and 'final' in stages:
            check(preserve['changed_urate_rows'],outcomes[bid]['changed_urate_rows'],bid+'.changed_rows')
        for stage,table in stages.items():
            independent_tables[(bid,stage)]=implementation.estimate_table(table)
    if len(released['candidate_comparisons'])!=len(independent_tables):raise ValueError('Candidate count differs')
    for candidate in released['candidate_comparisons']:
        bid,stage=candidate['builder'],candidate['stage']
        values=independent_tables[(bid,stage)]
        exact_records(candidate['estimands'],lambda r:r['estimand'],KEY_MAP,'candidate endpoints')
        for pair in candidate['estimands']:
            key=KEY_MAP[pair['estimand']]
            estimate(values[key],pair['generated'],bid+'.'+stage+'.'+key)
            estimate(truth[key],pair['measured'],bid+'.'+stage+'.measured.'+key)
            a,b=values[key]['value'],truth[key]['value']
            check(None if a is None or b is None else a-b,pair['difference_generated_minus_measured'],bid+'.'+stage+'.delta.'+key)
    for change in released['initial_final_changes']:
        bid=change['builder'];key=KEY_MAP[change['estimand']]
        ri=independent_tables[(bid,'initial')][key]['value'];rf=independent_tables[(bid,'final')][key]['value'];t=truth[key]['value']
        check(None if ri is None or t is None else ri-t,change['initial_difference'],bid+'.initial_delta.'+key)
        check(None if rf is None or t is None else rf-t,change['final_difference'],bid+'.final_delta.'+key)
        d=None if None in (ri,rf,t) else abs(rf-t)-abs(ri-t)
        check(d,change['change_in_absolute_difference_final_minus_initial'],bid+'.change.'+key)
        cd=change['change_in_absolute_difference_final_minus_initial']
        check(None if cd is None else 'lower' if cd<0 else 'higher' if cd>0 else 'unchanged',
              change['direction'],bid+'.change_direction.'+key)
    psu=implementation.reference_psu_sensitivity(reference)
    deletions={(d['stratum'],d['psu']):d for d in psu['deletions']}
    for summary in released['reference_sensitivity']['summaries']:
        key=KEY_MAP[summary['estimand']];own=psu['ranges'][key]
        exact_records(summary['deletions'],lambda d:(str(d['omitted_stratum']),str(d['omitted_psu'])),deletions,'PSU deletions')
        estimate(own['full'],summary['full_estimate'],'psu.full.'+key)
        check(len(reference),summary['n_full'],'psu.n_full.'+key)
        for a,b in [('minimum','range_min'),('maximum','range_max'),('omitted_psu_groups','omitted_psu_group_count'),
                    ('finite_deletions','finite_deletion_count'),('failed_deletions','failed_deletion_count'),
                    ('rank_failed_deletions','rank_failure_count'),
                    ('finite_deletion_sign_stable_with_full','finite_deletion_sign_stable_with_full'),
                    ('all_deletions_sign_stable_with_full','all_deletions_sign_stable_with_full')]:
            check(own[a],summary[b],'psu.'+key+'.'+a)
        for d in summary['deletions']:
            own_d=deletions[(str(d['omitted_stratum']),str(d['omitted_psu']))]
            estimate(own_d['estimates'][key],d,'psu.deletion.'+key)
            check(own_d['omitted_n'],d['n_omitted'],'psu.omitted_n')
            check(own_d['remaining_n'],d['n_retained'],'psu.remaining_n')
    return {'status':'PASS','comparison_count':len(checks),'maximum_absolute_numeric_difference':max(diffs,default=0),
            'preservation':preservation,'reference_estimands':truth,
            'candidate_estimands':[{'builder':k[0],'stage':k[1],'estimands':v} for k,v in independent_tables.items()],
            'reference_psu_sensitivity':psu,'reference_outcomes_not_returned_to_builders':True}
def safe_child(root,name):
    if not isinstance(name,str) or not name or '\\' in name or ':' in name or any(p in ('','.','..') for p in name.split('/')):
        raise ValueError('Unsafe relative path')
    target=(Path(root)/name).resolve()
    if not target.is_relative_to(Path(root).resolve()):raise ValueError('Escaped path')
    return target
def verify_public_release(release_path,released,run=R):
    """Independent procedural/hash gate. Never opens the reference file.

    Closure/review assertions remain controller claims, not OS isolation or
    cryptographic authorization. No canonical evaluator/lifecycle import.
    """
    run=Path(run).resolve();release=read(release_path)
    if release.get('schema_version')!=1 or release.get('kind')!='m16_target_evaluation_release' or release.get('evaluation_authorized') is not True:
        raise ValueError('Actual released evaluation required')
    if any(release.get('controller_checks',{}).get(k) is not True for k in CHECKS):raise ValueError('Controller review incomplete')
    if released.get('release_manifest_sha256')!=sha(release_path):raise ValueError('Released result binding differs')
    reference=release['reference'];refpath=Path(reference['path']).resolve()
    if set(reference)!={'path','sha256'} or not refpath.is_relative_to(run/'private'):
        raise ValueError('Invalid private reference binding')
    def binding(item):
        if set(item)!={'path','sha256'}:raise ValueError('Invalid binding schema')
        path=Path(item['path']).resolve();digest=item['sha256']
        if path==refpath or (path.exists() and refpath.exists() and path.samefile(refpath)):
            raise ValueError('Premature reference binding access')
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('Invalid digest')
        if sha(path)!=digest:raise ValueError('Public hash mismatch: '+str(path))
        return path
    fixed={'protocol':run/'PROTOCOL.md','controller':run/'controller.py',
           'evaluator':run/'evaluation_code/evaluator.py','estimands':run/'evaluation_code/frozen_m15b_estimands.py',
           'self_checker':run.parent.parent/'cohort_harness/self_consistency.py','prelaunch':run/'prelaunch.json'}
    for role,path in fixed.items():
        if Path(release[role]['path']).resolve()!=path:raise ValueError('Noncanonical '+role+' path')
        binding(release[role])
    if released.get('evaluator_sha256')!=release['evaluator']['sha256'] or released.get('frozen_estimands_sha256')!=release['estimands']['sha256']:
        raise ValueError('Released code identity differs')
    pre=read(fixed['prelaunch'])
    if pre.get('reference')!=reference or release.get('reference_weight_column')!='WTMEC2YR' or pre.get('reference_weight_column')!='WTMEC2YR':
        raise ValueError('Prelaunch reference/native weight mismatch')
    if not pre.get('files') or not pre.get('engine_files'):raise ValueError('Prelaunch commitments missing')
    for name,digest in pre['files'].items():binding({'path':str(safe_child(run,name)),'sha256':digest})
    for name,digest in pre['engine_files'].items():
        if not Path(name).is_absolute() or Path(name).suffix!='.py':raise ValueError('Invalid engine binding')
        binding({'path':name,'sha256':digest})
    if [b.get('id') for b in release.get('builders',[])]!=list(BUILDERS):raise ValueError('Scheduled builders differ')
    shared_task=shared_x=None
    for builder in release['builders']:
        bid=builder['id'];bundle=Path(builder['bundle_path']).resolve()
        if bundle!=run/'visible'/bid/'bundle':raise ValueError('Noncanonical bundle')
        for filename,field in [('task.json','task_sha256'),('observed.csv','observed_sha256')]:
            p=bundle/filename;binding({'path':str(p),'sha256':builder[field]})
            if pre['files'].get(p.relative_to(run).as_posix())!=builder[field]:raise ValueError('Task/X not precommitted')
        task=read(bundle/'task.json');semantics={k:v for k,v in task.items() if k!='task_id'}
        if not task.get('task_id'):raise ValueError('Task identity absent')
        if shared_x is None:shared_task,shared_x=semantics,builder['observed_sha256']
        if semantics!=shared_task or builder['observed_sha256']!=shared_x:raise ValueError('Different task/X')
        prefix=pre['registry_prefixes'][bid]
        if read(bundle/'registry.json')['artifacts'][:len(prefix)]!=prefix:raise ValueError('Registry seed changed')
        if builder.get('status')=='failed':
            binding(builder['failure_record'])
            if 'final' in builder:raise ValueError('Failed builder has final')
        elif builder.get('status')!='complete' or 'initial' not in builder or 'final' not in builder:
            raise ValueError('Builder not closed')
        for stage in ('initial','final'):
            if stage not in builder:continue
            entry=builder[stage]
            if entry['candidate']!='candidates/'+stage:raise ValueError('Wrong scheduled stage')
            cp=safe_child(bundle,entry['candidate']);binding({'path':str(cp/'freeze.json'),'sha256':entry['freeze_sha256']})
            binding({'path':str(cp/'generated.csv'),'sha256':entry['table_sha256']})
            current=read(cp/'freeze.json');seen=set()
            while True:
                candidate=current['candidate'];part=candidate.split('/')[-1]
                if candidate not in ('candidates/initial','candidates/revision1','candidates/final') or candidate in seen:
                    raise ValueError('Invalid candidate ancestry')
                seen.add(candidate);directory=safe_child(bundle,candidate)
                if current.get('route')!='generated.csv':raise ValueError('Nonliteral route')
                for name,digest in current['commitments'].items():binding({'path':str(safe_child(bundle,name)),'sha256':digest})
                if current['commitments'].get('task.json')!=builder['task_sha256'] or current['commitments'].get('observed.csv')!=builder['observed_sha256']:
                    raise ValueError('Freeze task/X mismatch')
                if candidate==entry['candidate'] and current['commitments'].get(candidate+'/generated.csv')!=entry['table_sha256']:
                    raise ValueError('Freeze table mismatch')
                pc=run/'commitments'/bid/(part+'.json');digest=sha(pc);record=read(pc)
                if part==stage and entry['preauthoring']!={'path':str(pc),'sha256':digest}:
                    # Path spelling may differ between Windows forward/back slashes.
                    if Path(entry['preauthoring']['path']).resolve()!=pc or entry['preauthoring']['sha256']!=digest:
                        raise ValueError('Preauthoring binding differs')
                if record.get('builder')!=bid or record.get('candidate')!=candidate or record.get('generated_exists') is not False or record.get('prelaunch_sha256')!=release['prelaunch']['sha256']:
                    raise ValueError('Preauthoring scope differs')
                if set(record.get('files',{}))!=set(SCIENCE_FILES):raise ValueError('Preauthoring science files differ')
                if sha(directory/'audit/preauthoring_commitment.json')!=digest or current['commitments'].get(candidate+'/audit/preauthoring_commitment.json')!=digest:
                    raise ValueError('Preauthoring receipt copy differs')
                for name,digest in record['files'].items():
                    binding({'path':str(safe_child(directory,name)),'sha256':digest})
                    if current['commitments'].get(candidate+'/'+name)!=digest:raise ValueError('Preauthoring freeze mismatch')
                earlier=datetime.fromisoformat(record['created_utc'].replace('Z','+00:00'));later=datetime.fromisoformat(current['created_utc'].replace('Z','+00:00'))
                if earlier.tzinfo is None or later.tzinfo is None or earlier>later:raise ValueError('Invalid preauthoring chronology')
                if part=='initial':
                    if current.get('parent') is not None or current.get('revision_index')!=0:raise ValueError('Invalid initial ancestor')
                    if sha(directory/'freeze.json')!=builder['initial']['freeze_sha256']:raise ValueError('Initial ancestor differs')
                    break
                parent=current['parent'];p=safe_child(bundle,parent['receipt_path'])
                binding({'path':str(p),'sha256':parent['sha256']})
                previous=read(p)
                if previous.get('revision_index')!=current.get('revision_index')-1:raise ValueError('Revision order differs')
                current=previous
    if not isinstance(reference['sha256'],str) or len(reference['sha256'])!=64 or any(c not in '0123456789abcdef' for c in reference['sha256']):raise ValueError('Invalid reference digest')
    return release
def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true');parser.add_argument('--release',required=True,type=Path)
    parser.add_argument('--results',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(argv)
    if not args.execute:parser.error('No execution without explicit post-release flag')
    if args.output.exists():raise ValueError('Audit output already exists')
    released=read(args.results);release=verify_public_release(args.release,released)
    csv_integrity=verify_csv_integrity(released,args.results.parent)
    module=load_independent()
    tables={};obs=None
    for builder in release['builders']:
        b=Path(builder['bundle_path']);op=b/'observed.csv'
        if sha(op)!=builder['observed_sha256']:raise ValueError('Observed changed')
        parsed=rows(op.read_bytes())
        if obs is not None and parsed!=obs:raise ValueError('Different observations')
        obs=parsed;tables[builder['id']]={}
        for stage in ('initial','final'):
            if stage not in builder:continue
            entry=builder[stage];cp=b/entry['candidate'];p=cp/'generated.csv'
            if sha(cp/'freeze.json')!=entry['freeze_sha256'] or sha(p)!=entry['table_sha256']:
                raise ValueError('Candidate changed')
            tables[builder['id']][stage]=rows(p.read_bytes())
    refpath=Path(release['reference']['path']);raw=refpath.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=release['reference']['sha256']:raise ValueError('Reference changed')
    reference=rows(raw)
    base={'sample_id','race','sex','age','bmi','urate'}
    required=base|{'SDMVSTRA','SDMVPSU'}
    if not reference or not required<=set(reference[0])<=required|{'SEQN','WTMEC2YR'}:raise ValueError('Native reference schema differs')
    result=compare_results(module,reference,obs,tables,released)
    result['aggregate_csv_integrity']=csv_integrity
    result.update(release_sha256=sha(args.release),released_results_sha256=sha(args.results),
                  wrapper_sha256=sha(__file__),independent_implementation_sha256=sha(HERE/'frozen_independent.py'))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps({k:result[k] for k in ('status','comparison_count','maximum_absolute_numeric_difference')}))
if __name__=='__main__':main()

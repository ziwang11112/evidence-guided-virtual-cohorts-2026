"""M8 amended release guard and evaluator. Import does not read target data."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,pathlib,sys
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from survey_analysis import evaluate,validate_invented
HERE=pathlib.Path(__file__).resolve().parent
CUSTODIAN=HERE.parents[1]/'analysis-evidence-gap-2026-10-29'/'custodian'
PROJECT_ROOT=HERE.parents[2]
VISIBLE=CUSTODIAN.parent/'visible'/'nhanes_tg_f'
def digest(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def write(p,o): pathlib.Path(p).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def require(ok,message):
    if not ok: raise ValueError(message)

def verify_amendment(c):
    anchor=c['evaluation_amendment']; path=pathlib.Path(anchor['path']).resolve()
    require(path==HERE/'protocol_amendment.json','Unexpected evaluator amendment path')
    require(digest(path)==anchor['sha256'],'Evaluator amendment changed')
    amendment=read(path)
    required={'analysis_protocol.json','survey_analysis.py','evaluate_committed.py','test_evaluator.py'}
    require(required.issubset(amendment['amended_files']),'Incomplete evaluator amendment')
    for name,value in amendment['amended_files'].items():
        require(pathlib.Path(name).name==name,'Invalid amendment file name')
        require(digest(HERE/name)==value,f'Amended evaluator file changed: {name}')
    for entry in amendment['original_files']:
        require(digest(HERE/entry['path'])==entry['sha256'],'Original evaluator provenance changed')
    return {'path':str(path),'sha256':anchor['sha256']}

def verify_preload(commitment_path):
    c=read(commitment_path)
    require(c.get('authorize_target_evaluation') is True,'Explicit controller authorization required')
    require(c.get('all_candidates_and_seeds_committed') is True,'All candidates and seeds must be committed')
    verify_amendment(c)
    require(digest(CUSTODIAN/'custodian_lock.json')==c['custodian_lock_sha256'],'Custodian lock mismatch')
    lock=read(CUSTODIAN/'custodian_lock.json')
    for name,value in lock['files'].items(): require(digest(CUSTODIAN/name)==value,f'Custodian anchor changed: {name}')
    require(digest(VISIBLE/'input_hashes.json')==lock['visible_input_hashes_sha256'],'Visible manifest changed')
    for name,value in read(VISIBLE/'input_hashes.json')['files'].items(): require(digest(VISIBLE/name)==value,f'Visible input changed: {name}')
    d=c['evaluation_design']; require(digest(d['path'])==d['sha256'],'Evaluation design changed')
    design=read(d['path']); protocol=read(HERE/'analysis_protocol.json')
    variants=design['variants']; seeds=design['seeds']
    require(variants==protocol['campaign']['variants'] and seeds==protocol['campaign']['seeds'],'Campaign differs from prespecified variants/seeds')
    expected={(v,int(s)) for v in variants for s in seeds}; outputs=c['outputs']
    require(len(outputs)==len(expected) and {(o['variant'],int(o['seed'])) for o in outputs}==expected,'Incomplete or duplicated variant-seed grid')
    candidates=c['candidate_commitments']; expected_candidates={(v,s) for v in variants for s in ['initial','final']}
    require(len(candidates)==len(expected_candidates) and {(x['variant'],x['stage']) for x in candidates}==expected_candidates,'Candidate coverage mismatch')
    for item in candidates: require(digest(item['path'])==item['sha256'],'Candidate commitment changed')
    for item in outputs: require(digest(item['path'])==item['sha256'],'Generated table changed')
    builder=c['builder_observed']; require(digest(builder['path'])==builder['sha256'],'Builder covariates changed')
    guard=c['controller_guard']; require(digest(guard['path'])==guard['sha256'],'Controller guard changed')
    # The verified controller guard imports the project harness from this root.
    if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0,str(PROJECT_ROOT))
    spec=importlib.util.spec_from_file_location('m8_controller_guard',guard['path'])
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    result=getattr(module,guard['function'])(pathlib.Path(commitment_path).resolve())
    require(isinstance(result,dict) and result.get('status')=='passed','Controller provenance guard failed')
    # Byte-hash verification is permitted after gate; no hidden table parsed here.
    require(digest(CUSTODIAN/'design_with_hidden_outcome.csv')==lock['hidden_table_sha256'],'Hidden reference changed')
    return c,result
def prepare_outputs(c):
    observed=pd.read_csv(VISIBLE/'observed.csv'); builder=pd.read_csv(c['builder_observed']['path'])
    require(set(observed.columns).issubset(builder.columns),'Missing observed columns')
    pd.testing.assert_frame_equal(builder[observed.columns],observed,check_dtype=False,check_exact=True)
    require(builder.record_id.is_unique,'Duplicate builder IDs')
    extra=set(builder.columns)-set(observed.columns)
    require(extra.issubset({'tg_assay'}),'Undeclared builder column')
    if 'tg_assay' in builder: require(builder.tg_assay.eq('legacy_proxy').all(),'Assay metadata mismatch')
    prepared=[]
    for entry in c['outputs']:
        require(digest(entry['path'])==entry['sha256'],'Generated table changed before parsing')
        table=pd.read_csv(entry['path'])
        require(list(table.columns)==list(builder.columns)+['tg_mg_dl'],'Output schema mismatch')
        pd.testing.assert_frame_equal(table[builder.columns],builder,check_dtype=False,check_exact=True)
        require(np.isfinite(table.tg_mg_dl).all() and table.tg_mg_dl.gt(0).all(),'Invalid generated target')
        prepared.append((entry,table.set_index('record_id').tg_mg_dl))
    return prepared
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--commitment',required=True,type=pathlib.Path)
    args=parser.parse_args(); c,guard=verify_preload(args.commitment); prepared=prepare_outputs(c)
    validation=validate_invented(); out=HERE/'results'; out.mkdir(exist_ok=False)
    write(out/'release_receipt.json',{'release_utc':datetime.now(timezone.utc).isoformat(),'commitment_sha256':digest(args.commitment),'custodian_lock_sha256':c['custodian_lock_sha256'],'evaluation_amendment':c['evaluation_amendment'],'all_outputs_validated_before_hidden_parse':True,'controller_guard':guard,'invented_validation':validation})
    full=pd.read_csv(CUSTODIAN/'design_with_hidden_outcome.csv')
    ref=evaluate(full,full.loc[full.eligible.eq(1)].set_index('record_id').LBXTR,reference=True)
    write(out/'reference_analyses.json',ref); rows=[]; unavailable=[]
    for entry,values in prepared:
        generated=evaluate(full,values,reference=False)
        for endpoint,stats in generated.items():
            target=ref[endpoint]
            if 'estimate' not in target or 'estimate' not in stats:
                unavailable.append({'variant':entry['variant'],'seed':entry['seed'],'endpoint':endpoint,'reference':target,'generated':stats}); continue
            rows.append({'variant':entry['variant'],'seed':entry['seed'],'endpoint':endpoint,**stats,'reference_estimate':target['estimate'],'reference_ci_low':target['ci_low'],'reference_ci_high':target['ci_high'],'reference_point_direction':target['point_direction'],'reference_ci_direction':target['ci_direction'],'point_direction_agrees':stats['point_direction']==target['point_direction'],'signed_error':stats['estimate']-target['estimate'],'absolute_error':abs(stats['estimate']-target['estimate'])})
    pd.DataFrame(rows).to_csv(out/'endpoint_comparison.csv',index=False)
    write(out/'nonestimable.json',unavailable)
    write(out/'interpretation.json',{'reference_uncertainty':'Survey Taylor-linearized 95% t intervals, no model/transport uncertainty included','generated_uncertainty':'Point estimates only; seeds represent simulation variation','direction':'Directions of positive means/proportions are tautological, so direction agreement is meaningful for association/curvature/ordered contrast endpoints only.','geometric':'Cell estimate is mean-logTG; exp_estimate/mean_mg_dl is geometric mean. Ordered log contrast exponentiates to geometric-mean ratio.','threshold':'Reserved evaluation-only diagnostics, calculated for both synthetic and reference values only after authorized release; excluded from source fitting and never returned to the builder for tuning. Untruncated reference Wald CIs may cross probability bounds; flags retained.','limits':read(HERE/'analysis_protocol.json')['comparison']['limits']})
    write(out/'result_hashes.json',{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps({'status':'complete','results_folder':str(out),'outputs':len(prepared)}))
if __name__=='__main__': main()

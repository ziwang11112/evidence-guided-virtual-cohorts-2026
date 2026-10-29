"""Frozen evaluator; only root authorizes a complete committed structure/seed grid.

The controller guard verifies full candidate trees, successful execution receipts,
candidate/seed/table linkage and predeclared grid. This evaluator independently
anchors custody and output bytes and validates every generated table before any
hidden table is parsed. Importing this module loads no participant data.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,pathlib
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from survey_analysis import evaluate,validate_invented
HERE=pathlib.Path(__file__).resolve().parent
VISIBLE=HERE.parent/'visible'/'nhanes_tg_l'
def digest(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def write(p,o): pathlib.Path(p).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def require(condition,message):
    if not condition: raise ValueError(message)

def verify_preload(commitment_path):
    c=read(commitment_path)
    require(c.get('authorize_target_evaluation') is True,'Root authorization required')
    require(c.get('all_structures_and_seeds_committed') is True,'All structures and seeds must be committed')
    require(digest(HERE/'custodian_lock.json')==c['custodian_lock_sha256'],'Custodian lock mismatch')
    lock=read(HERE/'custodian_lock.json')
    for name,value in lock['files'].items(): require(digest(HERE/name)==value,f'Custodian anchor changed: {name}')
    require(digest(VISIBLE/'input_hashes.json')==lock['visible_input_hashes_sha256'],'Visible manifest changed')
    for name,value in read(VISIBLE/'input_hashes.json')['files'].items(): require(digest(VISIBLE/name)==value,f'Visible input changed: {name}')
    for name,value in read(HERE/'methods_freeze.json')['files'].items(): require(digest(HERE/name)==value,f'Frozen method changed: {name}')
    structures=c['structures']; seeds=c['seeds']; outputs=c['outputs']
    require(len(structures)>=2 and len(set(structures))==len(structures),'At least two unique prespecified structures required')
    require(len(seeds)>=2 and len(set(seeds))==len(seeds),'At least two unique prespecified seeds required')
    expected={(s,int(seed)) for s in structures for seed in seeds}
    require(len(outputs)==len(expected),'Output count must equal complete grid')
    require({(o['structure'],int(o['seed'])) for o in outputs}==expected,'Missing, extra or duplicate structure-seed output')
    candidates=c['candidate_commitments']
    candidate_grid={(s,stage) for s in structures for stage in ['initial','final']}
    require(len(candidates)==len(candidate_grid) and {(x['structure'],x['stage']) for x in candidates}==candidate_grid,'Initial/final candidate coverage mismatch')
    for item in candidates: require(digest(item['path'])==item['sha256'],'Candidate commitment changed')
    for item in outputs: require(digest(item['path'])==item['sha256'],'Generated table changed')
    builder=c['builder_observed']; require(digest(builder['path'])==builder['sha256'],'Builder covariate input changed')
    guard=c['controller_guard']; require(digest(guard['path'])==guard['sha256'],'Controller guard code changed')
    spec=importlib.util.spec_from_file_location('committed_controller_guard',guard['path'])
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    guard_result=getattr(module,guard['function'])(pathlib.Path(commitment_path).resolve())
    require(isinstance(guard_result,dict) and guard_result.get('status')=='passed','Controller provenance verification failed')
    # This is a byte-level integrity read only, after successful provenance gate.
    require(digest(HERE/'design_with_hidden_outcome.csv')==lock['hidden_table_sha256'],'Hidden table anchor mismatch')
    return c,guard_result

def prepare_outputs(c):
    observed=pd.read_csv(VISIBLE/'observed.csv')
    builder=pd.read_csv(c['builder_observed']['path'])
    require(set(observed.columns).issubset(builder.columns),'Builder covariate mapping missing base columns')
    pd.testing.assert_frame_equal(builder[observed.columns],observed,check_dtype=False,check_exact=True)
    require(builder.record_id.is_unique,'Builder row IDs not unique')
    extra=set(builder.columns)-set(observed.columns)
    require(extra.issubset({'tg_assay'}),'Undeclared extra builder covariate')
    if 'tg_assay' in extra: require(builder.tg_assay.eq('unblanked_2021_2023').all(),'Target assay metadata mismatch')
    prepared=[]
    for entry in c['outputs']:
        require(digest(entry['path'])==entry['sha256'],'Generated table changed before parse')
        table=pd.read_csv(entry['path'])
        require(list(table.columns)==list(builder.columns)+['tg_mg_dl'],'Generated output schema mismatch')
        pd.testing.assert_frame_equal(table[builder.columns],builder,check_dtype=False,check_exact=True)
        require(np.isfinite(table.tg_mg_dl).all() and table.tg_mg_dl.gt(0).all(),'Generated TG nonpositive or nonfinite')
        prepared.append((entry,table.set_index('record_id').tg_mg_dl))
    return prepared

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--commitment',required=True,type=pathlib.Path)
    args=parser.parse_args(); c,guard_result=verify_preload(args.commitment)
    prepared=prepare_outputs(c); validation=validate_invented()
    results=HERE/'evaluation'; results.mkdir(exist_ok=False)
    write(results/'release_receipt.json',{'release_utc':datetime.now(timezone.utc).isoformat(),'commitment_path':str(args.commitment.resolve()),'commitment_sha256':digest(args.commitment),'custodian_lock_sha256':c['custodian_lock_sha256'],'protocol_sha256':digest(HERE/'analysis_protocol.json'),'guard_result':guard_result,'invented_validation':validation,'all_outputs_validated_before_hidden_table_parse':True})
    full=pd.read_csv(HERE/'design_with_hidden_outcome.csv')
    native_reference=full.loc[full.eligible.eq(1)].set_index('record_id').LBXTLG
    reference={}; rows=[]; unavailable=[]
    for scale_name in ['native','cdc_backward_auxiliary']:
        values=native_reference if scale_name=='native' else -12.19+0.9785*native_reference
        if not values.gt(0).all():
            unavailable.append({'measurement_scale':scale_name,'structure':'reference','reason':'Nonpositive calibrated value; unchanged domain cannot be analyzed on log scale'})
            continue
        ref=evaluate(full,values,reference=True); reference[scale_name]=ref
        for entry,native_values in prepared:
            gen=native_values if scale_name=='native' else -12.19+0.9785*native_values
            if not gen.gt(0).all():
                unavailable.append({'measurement_scale':scale_name,'structure':entry['structure'],'seed':entry['seed'],'reason':'Nonpositive calibrated value; no truncation or record deletion'})
                continue
            measured=evaluate(full,gen,reference=False)
            for endpoint,stats in measured.items():
                target=ref[endpoint]
                rows.append({'measurement_scale':scale_name,'structure':entry['structure'],'seed':entry['seed'],'endpoint':endpoint,**stats,'reference_estimate':target['estimate'],'reference_ci_low':target['ci_low'],'reference_ci_high':target['ci_high'],'reference_point_direction':target['point_direction'],'reference_ci_direction':target['ci_direction'],'point_direction_agrees':stats['point_direction']==target['point_direction'],'signed_error':stats['estimate']-target['estimate'],'absolute_error':abs(stats['estimate']-target['estimate'])})
    write(results/'reference_analyses.json',reference)
    comparison=pd.DataFrame(rows); comparison.to_csv(results/'endpoint_comparison.csv',index=False)
    summaries=[]
    for (scale_name,endpoint),group in comparison.groupby(['measurement_scale','endpoint'],sort=True):
        summaries.append({'measurement_scale':scale_name,'endpoint':endpoint,'expected_outputs':len(c['outputs']),'estimable_outputs':len(group),'all_outputs_estimable':len(group)==len(c['outputs']),'point_directions':sorted(group.point_direction.unique().tolist()),'all_generated_same_point_direction':group.point_direction.nunique()==1,'point_direction_agreement_count':int(group.point_direction_agrees.sum()),'all_generated_match_reference_point_direction':bool(group.point_direction_agrees.all()) and len(group)==len(c['outputs']),'reference_point_direction':group.reference_point_direction.iloc[0],'reference_ci_direction':group.reference_ci_direction.iloc[0],'estimate_min':float(group.estimate.min()),'estimate_max':float(group.estimate.max()),'absolute_error_min':float(group.absolute_error.min()),'absolute_error_max':float(group.absolute_error.max())})
    write(results/'direction_robustness.json',summaries)
    write(results/'nonestimable_sensitivities.json',unavailable)
    write(results/'report_notes.json',{'all_structures':c['structures'],'all_seeds':c['seeds'],'outputs_evaluated':len(prepared),'primary':['adjusted_age_per10','bmi_curvature_second_difference'],'secondary':['raw_bmi_curvature_second_difference','adjusted_bmi_per5','adjusted_female_vs_male','bmi_sex_interaction'],'curvature':'Full-domain quadratic projection contrast; exponentiated log contrast is a ratio of ratios. Raw contrast is identity scale mg/dL.','reference_uncertainty':'Design-based 95% t confidence intervals; occupied-domain PSU minus stratum df. Full positive-weight design including zero out-of-domain score contributions.','generated_uncertainty':'Point estimates only; seed variation is simulation sensitivity, structures are assumptions, neither is clinical-evidence or transport uncertainty.','calibration':'Fixed CDC backward equation applied to every table; coefficient uncertainty not propagated; auxiliary only.','interpretation_limits':['temporal replication within same survey program','no equivalence or absence from nonsignificance','no individual recovery or causal interpretation','no post-evaluation builder revision']})
    write(results/'result_hashes.json',{p.name:digest(p) for p in sorted(results.iterdir()) if p.is_file()})
    print(json.dumps({'status':'complete','results':str(results),'outputs':len(prepared)}))

if __name__=='__main__': main()

"""Verify technical repair bindings; endpoint use is restricted to masks.

Main full-frame read uses an explicit non-outcome whitelist. A separately
authorized endpoint-only read computes presence/finite/physical-support masks;
no endpoint magnitudes, associations or distribution summaries are emitted.
Hashes raw files as opaque bytes and consumes aggregate amendment records.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import pyreadstat

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def csv(p,cols):return pd.read_csv(p,usecols=cols,dtype={'id':str},float_precision='round_trip')

def main():
    checks={}
    def check(name,condition):
        checks[name]=bool(condition)
        assert checks[name],name
    frozen=read(ROOT/'preaccess_freeze.json')
    check('all_19_preaccess_files_unchanged',len(frozen['files'])==19 and all(digest(ROOT/p)==h for p,h in frozen['files'].items()))
    original=ROOT/'custodian/acquisition'; corrected=ROOT/'custodian/acquisition_corrected'
    receipt=read(original/'private/acquisition_receipt.json')
    amend=read(corrected/'private/technical_amendment.json')
    check('original_acquisition_outputs_unchanged',all(digest(v['path'])==v['sha256'] for v in receipt['outputs'].values()))
    check('original_raw_bytes_unchanged',all(digest(original/'private/raw'/f"{v['component']}.xpt")==v['sha256'] for v in receipt['downloads']))
    check('amendment_original_receipt_binding',digest(amend['original_receipt']['path'])==amend['original_receipt']['sha256'])
    check('repair_code_and_transform_binding',all(digest(amend[k]['path'])==amend[k]['sha256'] for k in ['repair_script','unchanged_frozen_transform']))
    check('corrected_outputs_match_amendment',amend['status']=='complete' and all(digest(v['path'])==v['sha256'] for v in amend['outputs'].values()))
    check('amendment_same_original_freeze',amend['gate']['freeze_manifest_sha256']==digest(ROOT/'preaccess_freeze.json')==amend['postrepair_frozen_gate']['freeze_manifest_sha256'])
    check('no_declared_scientific_changes',amend['scientific_changes']==[])
    demo_cols=['SEQN','WTMEC2YR','SDMVSTRA','SDMVPSU']
    demo,_=pyreadstat.read_xport(original/'private/raw/DEMO_J.xpt',usecols=demo_cols)
    mask=np.isfinite(demo.WTMEC2YR)&demo.WTMEC2YR.gt(0)&np.isfinite(demo.SDMVSTRA)&np.isfinite(demo.SDMVPSU)
    expected=demo.loc[mask,demo_cols].sort_values('SEQN').reset_index(drop=True)
    frame_cols=['id',*demo_cols,'RIDAGEYR','RIAGENDR','RIDRETH3','BMXBMI','DXAEXSTS']
    frame=csv(corrected/'private/full_frame.csv',frame_cols)
    check('corrected_design_keys_and_weights_exact',np.array_equal(frame[demo_cols].to_numpy(),expected.to_numpy(),equal_nan=True))
    check('corrected_full_design_positive_weights_only',len(frame)==8704 and frame.WTMEC2YR.gt(0).all())
    check('corrected_full_design_strata_psus',frame.SDMVSTRA.nunique()==15 and len(set(zip(frame.SDMVSTRA,frame.SDMVPSU)))==30)
    protocol=read(ROOT/'protocol.json'); allowed=protocol['observed_columns']
    oldobs=csv(original/'generator_input/observed.csv',allowed)
    newobs=csv(corrected/'generator_input/observed.csv',allowed)
    oldkeys=csv(original/'private/full_frame.csv',['id','SEQN'])
    before=oldobs.merge(oldkeys,on='id',how='left',validate='one_to_one').sort_values('SEQN')
    after=newobs.merge(frame[['id','SEQN']],on='id',how='left',validate='one_to_one').sort_values('SEQN')
    check('same_exact_eligible_participant_set_after_repair',len(after)==842 and np.array_equal(before.SEQN.to_numpy(),after.SEQN.to_numpy()))
    check('same_exact_generator_covariates_after_repair',np.array_equal(before[[c for c in allowed if c!='id']].to_numpy(),after[[c for c in allowed if c!='id']].to_numpy(),equal_nan=True))
    # Validate all non-outcome eligibility conditions independently on every selected row.
    selected=newobs[['id']].merge(frame,on='id',how='left',validate='one_to_one')
    check('selected_rows_meet_frozen_covariate_scan_rules',selected.RIDAGEYR.between(20,59).all() and selected.RIAGENDR.isin([1,2]).all() and selected.RIDRETH3.isin([3,4]).all() and selected.BMXBMI.between(18.5,35).all() and selected.DXAEXSTS.eq(1).all())
    check('observed_covariates_correspond_exactly_to_full_frame',np.array_equal(newobs.age,selected.RIDAGEYR) and np.array_equal(newobs.bmi,selected.BMXBMI) and np.array_equal(newobs.male,selected.RIAGENDR.eq(1).astype(int)))
    check('fixed_domain_counts_disjoint',int(newobs.bmi.lt(30).sum())==612 and int(newobs.bmi.ge(30).sum())==230)
    endpoint=pd.read_csv(corrected/'private/full_frame.csv',usecols=['DXDTOPF'],float_precision='round_trip').DXDTOPF
    endpoint_finite=np.isfinite(endpoint)
    endpoint_physical=endpoint.between(0,100)
    check('endpoint_presence_and_physical_integrity_only',not np.isinf(endpoint).any() and (endpoint.isna()|endpoint_physical).all())
    del endpoint
    domain=(np.isfinite(frame.WTMEC2YR)&frame.WTMEC2YR.gt(0)&np.isfinite(frame.SDMVSTRA)&np.isfinite(frame.SDMVPSU)&frame.RIDAGEYR.between(20,59)&frame.RIAGENDR.isin([1,2])&frame.RIDRETH3.isin([3,4])&np.isfinite(frame.BMXBMI)&frame.BMXBMI.between(18.5,35)&frame.DXAEXSTS.eq(1)&endpoint_finite)
    check('exact_ordered_domain_membership_with_endpoint_finite_mask',frame.loc[domain,'id'].tolist()==newobs.id.tolist())
    check('exact_disjoint_domain_partition_with_endpoint_finite_mask',int((domain&frame.BMXBMI.lt(30)).sum())==612 and int((domain&frame.BMXBMI.ge(30)).sum())==230 and int(domain.sum())==842)
    check('exact_input_whitelist',list(newobs.columns)==allowed and 'SEQN' not in newobs.columns and not any(c.startswith('DX') for c in newobs.columns))
    deployment=read(ROOT/'deployment_manifest.json')
    check('deployment_uses_corrected_whitelist_artifact',Path(deployment['observed_path']).resolve()==(corrected/'generator_input/observed.csv').resolve() and deployment['observed_sha256']==digest(corrected/'generator_input/observed.csv'))
    check('four_frozen_deployments',len(deployment['deployments'])==4)
    for entry in deployment['deployments']:
        identity=next(m for m in protocol['models'] if (m['builder'],m['candidate'])==(entry['builder'],entry['candidate']))
        bundle=Path(entry['bundle']); candidate=bundle/'candidates'/entry['candidate']
        name=entry['builder']+'_'+entry['candidate']
        check(name+'_frozen_science_unchanged',digest(candidate/'generator.py')==identity['generator_sha256'] and digest(candidate/'model_spec.json')==identity['spec_sha256'] and digest(candidate/'freeze.json')==entry['deployment_freeze_sha256'])
        check(name+'_corrected_observed_copy',digest(bundle/'observed.csv')==deployment['observed_sha256'])
    result=dict(status='pass',scope='Weight/design/covariate/scan and identity checks; separately root-authorized endpoint presence/finite/physical-support masks only. No endpoint magnitudes, associations or distribution summaries exposed or analyzed.',
        checks=checks,counts=dict(checks=len(checks),full_frame=8704,strata=15,nested_psus=30,observed=842,primary=612,extension=230,scientific_candidates=4,scheduled_agent_tables=12,scheduled_reference_tables=4),
        endpoint_completeness='Independently recomputed exact ordered domain membership using authorized Boolean endpoint masks; no magnitudes or outcome analysis',
        bindings=dict(preaccess_sha256=digest(ROOT/'preaccess_freeze.json'),technical_amendment_sha256=digest(corrected/'private/technical_amendment.json'),repair_script_sha256=amend['repair_script']['sha256'],corrected_observed_sha256=digest(corrected/'generator_input/observed.csv')))
    (HERE/'correction_binding_review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

"""Eligibility/measurement QC only. Does not compute target distributions or models."""
from __future__ import annotations
import hashlib,json,pathlib,platform,sys,urllib.request,uuid
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import pyreadstat,scipy
HERE=pathlib.Path(__file__).resolve().parent
VISIBLE=HERE.parent/'visible'/'nhanes_tg_f'
def digest(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def write(p,obj): pathlib.Path(p).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
def main():
    assert not (HERE/'preparation_receipt.json').exists(),'Already prepared'
    freeze=json.loads((HERE/'protocol_freeze.json').read_text())
    for name,value in freeze['files'].items(): assert digest(HERE/name)==value,f'Method changed: {name}'
    protocol=json.loads((HERE/'analysis_protocol.json').read_text())
    for folder in ['raw','documentation']: (HERE/folder).mkdir(exist_ok=True)
    VISIBLE.mkdir(parents=True,exist_ok=True); provenance=[]
    urls=protocol['official_documentation']+[f'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles/{n}.xpt' for n in protocol['selection']['files']]
    for url in urls:
        name=url.rsplit('/',1)[-1]; folder='raw' if name.endswith('.xpt') else 'documentation'; path=HERE/folder/name
        with urllib.request.urlopen(url,timeout=90) as response: raw=response.read(); resolved=response.url
        path.write_bytes(raw)
        if folder=='raw': assert raw.startswith(b'HEADER RECORD'),f'Not XPORT: {name}'
        provenance.append({'requested_url':url,'resolved_url':resolved,'downloaded_utc':now(),'bytes':len(raw),'sha256':digest(path),'path':str(path.relative_to(HERE))})
        write(HERE/'download_hash_log.json',provenance)
    frames={n:pyreadstat.read_xport(str(HERE/'raw'/f'{n}.xpt'),encoding='WINDOWS-1252')[0] for n in protocol['selection']['files']}
    demo,bmi,tg,fast=[frames[n] for n in ['DEMO_F','BMX_F','TRIGLY_F','FASTQX_F']]
    for frame in frames.values(): assert frame.SEQN.is_unique and frame.SEQN.notna().all()
    assert len(tg)==3581 and tg.WTSAF2YR.notna().all(),'Official weight codebook mismatch'
    assert len(fast)==9835 and int(fast.PHDSESN.eq(0).sum())==4589,'Official morning-session codebook mismatch'
    merged=tg[['SEQN','WTSAF2YR','LBXTR','LBDTRSI']].merge(demo[['SEQN','RIDAGEYR','RIAGENDR','RIDSTATR','SDMVSTRA','SDMVPSU']],on='SEQN',how='left',validate='one_to_one',indicator='demo_join').merge(bmi[['SEQN','BMXBMI']],on='SEQN',how='left',validate='one_to_one',indicator='bmi_join').merge(fast[['SEQN','PHAFSTHR','PHAFSTMN','PHDSESN']],on='SEQN',how='left',validate='one_to_one',indicator='fast_join')
    assert merged.demo_join.eq('both').all()
    paired=np.isfinite(merged.LBXTR)&np.isfinite(merged.LBDTRSI)
    assert np.allclose(merged.loc[paired,'LBXTR']*.01129,merged.loc[paired,'LBDTRSI'],atol=.00051,rtol=0),'Unit conversion QC failed'
    design=np.isfinite(merged[['WTSAF2YR','SDMVSTRA','SDMVPSU']]).all(axis=1)&merged.WTSAF2YR.gt(0)
    full=merged.loc[design].copy().reset_index(drop=True)
    adult=full.RIDAGEYR.between(40,79)&full.RIDSTATR.eq(2)&full.RIAGENDR.isin([1,2])
    fasting_hours=full.PHAFSTHR+full.PHAFSTMN/60
    fasting=np.isfinite(fasting_hours)&fasting_hours.ge(8.5)&fasting_hours.lt(24)&full.PHDSESN.eq(0)
    good_bmi=np.isfinite(full.BMXBMI)&full.BMXBMI.gt(0); good_tg=np.isfinite(full.LBXTR)&full.LBXTR.gt(0)
    domain=adult&fasting&good_bmi&good_tg; full['eligible']=domain.astype(int)
    assert int(domain.sum())>0,'No eligible participants: stop before releasing empty input'
    indices=np.random.default_rng(20261029).permutation(np.flatnonzero(domain))
    full['record_id']=''; full.loc[indices,'record_id']=[uuid.uuid4().hex for _ in indices]
    full=full.drop(columns=['demo_join','bmi_join','fast_join','LBDTRSI'])
    full.to_csv(HERE/'design_with_hidden_outcome.csv',index=False)
    observed=full.loc[indices,['record_id','RIDAGEYR','RIAGENDR','BMXBMI']].rename(columns={'RIDAGEYR':'age','RIAGENDR':'sex','BMXBMI':'bmi'}).reset_index(drop=True)
    observed[['age','sex']]=observed[['age','sex']].astype(int)
    observed['tg_assay']='legacy_proxy'
    observed.to_csv(VISIBLE/'observed.csv',index=False)
    support=full[['SDMVSTRA','SDMVPSU']].drop_duplicates(); ds=full.loc[domain,['SDMVSTRA','SDMVPSU']].drop_duplicates()
    assert support.groupby('SDMVSTRA').size().ge(2).all()
    counts={'raw_file_rows':{n:len(f) for n,f in frames.items()},'positive_fasting_weights':int(tg.WTSAF2YR.gt(0).sum()),'zero_fasting_weights':int(tg.WTSAF2YR.eq(0).sum()),'negative_fasting_weights':int(tg.WTSAF2YR.lt(0).sum()),'positive_weight_design_rows':len(full),'positive_weight_missing_design':int((merged.WTSAF2YR.gt(0)&~design).sum()),'adult40_79_valid_demographics':int(adult.sum()),'adult_invalid_fasting_or_session':int((adult&~fasting).sum()),'adult_fasting_invalid_bmi':int((adult&fasting&~good_bmi).sum()),'adult_fasting_valid_bmi_invalid_tg':int((adult&fasting&good_bmi&~good_tg).sum()),'eligible_complete_rows':len(observed),'full_design_strata':int(support.SDMVSTRA.nunique()),'full_design_PSUs':len(support),'domain_strata':int(ds.SDMVSTRA.nunique()),'domain_PSUs':len(ds),'nominal_domain_df':len(ds)-int(ds.SDMVSTRA.nunique()),'unit_conversion_check':'passed using official mg/dL-to-mmol/L factor and rounding tolerance','target_statistics_computed':False,'outcome_rows_released':False}
    assert counts['negative_fasting_weights']==0
    write(VISIBLE/'preparation_counts.json',counts)
    metadata={'case_id':protocol['case_id'],'n_rows':len(observed),'mode':'enrichment','row_id':'record_id','observed_file':'observed.csv','observed_schema':[{'name':'record_id','kind':'string','role':'identifier'},{'name':'age','kind':'integer','unit':'years','role':'observed'},{'name':'sex','kind':'category','categories':[1,2],'mapping':{'1':'male','2':'female'},'role':'observed'},{'name':'bmi','kind':'number','unit':'kg/m^2','role':'observed'}],'optional_constant_assay_column':{'name':'tg_assay','value':'legacy_proxy'},'generated_column':{'name':'tg_mg_dl','unit':'mg/dL','finite_positive':True},'population':'NHANES 2009-2010 fasting morning MEC adults age40-79; positive fasting subsample weights and complete BMI/reference TG.','requirements':['Preserve all observed cells and row order; append finite positive tg_mg_dl.','Use approved non-NHANES source evidence only; target-containing pooled publications excluded.','No custodian inspection, outcome-table fetch, record linkage, or prior target result reading.','Freeze both candidates and all seeds before target release; no post-release tuning.'],'protocol_sha256':digest(HERE/'analysis_protocol.json'),'measurement_note':'measurement_note.md','boundary':'Procedural role boundary; not OS isolation or protection against model pretraining.','classification':'Audit-limited unused temporal holdout within NHANES; not independent study.'}
    metadata['observed_schema'].append({'name':'tg_assay','kind':'category','categories':['legacy_proxy'],'role':'observed'})
    metadata['assay_token_limitation']='legacy_proxy is the inherited generator compatibility token; exact target is NHANES2009-2010 glycerol-blanked Roche Modular P. Mapping to the legacy source model is an explicit measurement approximation, not equivalence.'
    write(VISIBLE/'task_metadata.json',metadata)
    note='''# Measurement-only target context\n\nTarget: reference-method serum triglycerides, LBXTR in TRIGLY_F, NHANES 2009-2010. Units are mg/dL. The enzymatic Roche Modular P method includes glycerol blanking. The official conversion to mmol/L is multiplication by 0.01129. Generate native mg/dL values; no later-cycle assay conversion is applied.\n\nThe analysis domain uses age40-79, morning examination, positive WTSAF2YR and food fast at least 8.5 and below 24 hours; complete observed BMI and reference TG. Age40+ was chosen from source applicability before target outcomes were downloaded or inspected. Standard biochemistry-profile TG is a different measurement and is not the reference. Nonfasting source evidence requires an explicit transport assumption.\n\n[CDC TRIGLY_F measurement and analytic notes](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles/TRIGLY_F.htm). This link establishes measurement metadata only; builders must use this supplied excerpt rather than retrieve target data or use target-derived relationship evidence. No target means, distributions, signs or coefficients are disclosed.\n'''
    (VISIBLE/'measurement_note.md').write_text(note,encoding='utf-8')
    (VISIBLE/'README.md').write_text('''# Covariate-only target input\n\nobserved.csv contains opaque randomized IDs, age (years), sex (1 male; 2 female) and BMI (kg/m^2). The reference outcome column, survey design, weights and SEQN mapping remain custodial. Append positive finite tg_mg_dl without changing observed values or row order. The preserved tg_assay column equals legacy_proxy, the inherited-generator compatibility token. Exact measurement context is glycerol-blanked NHANES2009-2010; this proxy token is an explicit approximation, not assay equivalence.\n\nThis is an audit-limited unused period within NHANES, not an independent study or a strict safeguard against LLM pretraining. Use no NHANES-derived construction evidence. Cohort eligibility and all public hypotheses were fixed without target outcome analysis. The source-informed age40-79 domain does not resolve transport from nonfasting source measurements to fasting target measurements.\n\nThe reserved evaluator includes main age/BMI relations, quadratic curvature, all 12 sex by age by BMI cells, ordered BMI-group contrasts and a target-only threshold diagnostic. It presumes no desired directions. Both evidence variants and all three seeds must be frozen before any target result is released. No post-release revision is permitted.\n''',encoding='utf-8')
    write(VISIBLE/'public_analysis_protocol.json',protocol)
    write(VISIBLE/'input_hashes.json',{'created_utc':now(),'files':{p.name:digest(p) for p in sorted(VISIBLE.iterdir()) if p.is_file() and p.name!='input_hashes.json'}})
    write(HERE/'preparation_receipt.json',{'completed_utc':now(),'protocol_sha256':digest(HERE/'analysis_protocol.json'),'protocol_freeze_sha256':digest(HERE/'protocol_freeze.json'),'hidden_table_sha256':digest(HERE/'design_with_hidden_outcome.csv'),'visible_input_hashes_sha256':digest(VISIBLE/'input_hashes.json'),'download_hash_log_sha256':digest(HERE/'download_hash_log.json'),'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'pyreadstat':pyreadstat.__version__},'target_analyses_run':False})
    names=['setup_protocol.py','analysis_protocol.json','protocol_freeze.json','novelty_audit.json','survey_analysis.py','evaluate_committed.py','prepare_case.py','validate_methods.py','preparation_receipt.json','download_hash_log.json','method_validation.json','preparation_amendment.json','protocol_freeze_attempt1.json','preparation_receipt_attempt1.json']
    write(HERE/'custodian_lock.json',{'frozen_utc':now(),'files':{n:digest(HERE/n) for n in names},'hidden_table_sha256':digest(HERE/'design_with_hidden_outcome.csv'),'visible_input_hashes_sha256':digest(VISIBLE/'input_hashes.json'),'release_requires_controller_guard':True,'target_analyses_run':False})
    print(json.dumps({'status':'prepared_no_outcome_analysis','visible_folder':str(VISIBLE),'n':len(observed),'protocol_sha256':digest(HERE/'analysis_protocol.json'),'custodian_lock_sha256':digest(HERE/'custodian_lock.json')}))
if __name__=='__main__': main()

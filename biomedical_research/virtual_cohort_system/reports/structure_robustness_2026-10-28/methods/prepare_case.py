"""Custodian preparation: eligibility QC only, never outcome distributions or fitting."""
from __future__ import annotations
import hashlib,json,pathlib,platform,sys,urllib.request,uuid
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import pyreadstat,scipy
HERE=pathlib.Path(__file__).resolve().parent
VISIBLE=HERE.parent/'visible'/'nhanes_tg_l'
def digest(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def write(p,o): pathlib.Path(p).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()

def main():
    assert not (HERE/'preparation_receipt.json').exists(), 'Preparation already exists'
    freeze=json.loads((HERE/'protocol_freeze.json').read_text())
    for name,value in freeze['files'].items(): assert digest(HERE/name)==value
    methods=json.loads((HERE/'methods_freeze.json').read_text())
    for name,value in methods['files'].items(): assert digest(HERE/name)==value
    protocol=json.loads((HERE/'analysis_protocol.json').read_text())
    (HERE/'raw').mkdir(exist_ok=True); (HERE/'documentation').mkdir(exist_ok=True)
    VISIBLE.mkdir(parents=True,exist_ok=True)
    provenance=[]
    urls=protocol['official_documentation']+[f'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/{n}.xpt' for n in ['DEMO_L','BMX_L','TRIGLY_L']]
    for url in urls:
        name=url.rsplit('/',1)[-1]; folder='raw' if name.endswith('.xpt') else 'documentation'
        path=HERE/folder/name
        with urllib.request.urlopen(url,timeout=120) as response:
            raw=response.read(); resolved=response.url
        path.write_bytes(raw)
        if folder=='raw': assert raw.startswith(b'HEADER RECORD'), f'Not an XPORT file: {name}'
        provenance.append({'requested_url':url,'resolved_url':resolved,'downloaded_utc':now(),'bytes':len(raw),'sha256':digest(path),'path':str(path.relative_to(HERE))})
    write(HERE/'data_provenance.json',provenance)
    demo=pyreadstat.read_xport(str(HERE/'raw'/'DEMO_L.xpt'),encoding='WINDOWS-1252')[0]
    bmi=pyreadstat.read_xport(str(HERE/'raw'/'BMX_L.xpt'),encoding='WINDOWS-1252')[0]
    tg=pyreadstat.read_xport(str(HERE/'raw'/'TRIGLY_L.xpt'),encoding='WINDOWS-1252')[0]
    assert len(tg)==3996 and tg.WTSAF2YR.eq(0).sum()==635 and tg.WTSAF2YR.gt(0).sum()==3361 and tg.WTSAF2YR.isna().sum()==0, 'Weight codebook validation failed'
    assert len(demo)==11933, 'Demography codebook validation failed'
    for frame in [demo,bmi,tg]: assert frame.SEQN.is_unique and frame.SEQN.notna().all()
    merged=tg[['SEQN','WTSAF2YR','LBXTLG','LBDTRSI']].merge(demo[['SEQN','RIDAGEYR','RIAGENDR','RIDSTATR','SDMVSTRA','SDMVPSU']],on='SEQN',how='left',validate='one_to_one',indicator='demo_join').merge(bmi[['SEQN','BMXBMI']],on='SEQN',how='left',validate='one_to_one',indicator='bmi_join')
    assert merged.demo_join.eq('both').all(), 'TG to DEMO join failure'
    # Unit consistency, missingness and positivity are permitted QC; no outcome summaries.
    paired=np.isfinite(merged.LBXTLG)&np.isfinite(merged.LBDTRSI)
    assert np.allclose(merged.loc[paired,'LBXTLG']*0.01129,merged.loc[paired,'LBDTRSI'],atol=.00051,rtol=0), 'Unit conversion mismatch'
    good_design=np.isfinite(merged[['WTSAF2YR','SDMVSTRA','SDMVPSU']]).all(axis=1)&merged.WTSAF2YR.gt(0)
    full=merged.loc[good_design].copy().reset_index(drop=True)
    adult=full.RIDAGEYR.between(20,79)&full.RIDSTATR.eq(2)&full.RIAGENDR.isin([1,2])
    good_bmi=np.isfinite(full.BMXBMI)&full.BMXBMI.gt(0)
    good_tg=np.isfinite(full.LBXTLG)&full.LBXTLG.gt(0)
    domain=adult&good_bmi&good_tg; full['eligible']=domain.astype(int)
    indices=np.random.default_rng(20261028).permutation(np.flatnonzero(domain))
    full['record_id']=''; full.loc[indices,'record_id']=[uuid.uuid4().hex for _ in indices]
    full=full.drop(columns=['demo_join','bmi_join','LBDTRSI'])
    full.to_csv(HERE/'design_with_hidden_outcome.csv',index=False)
    observed=full.loc[indices,['record_id','RIDAGEYR','RIAGENDR','BMXBMI']].rename(columns={'RIDAGEYR':'age','RIAGENDR':'sex','BMXBMI':'bmi'}).reset_index(drop=True)
    observed[['age','sex']]=observed[['age','sex']].astype(int)
    observed.to_csv(VISIBLE/'observed.csv',index=False)
    support=full[['SDMVSTRA','SDMVPSU']].drop_duplicates(); dom_support=full.loc[domain,['SDMVSTRA','SDMVPSU']].drop_duplicates()
    assert support.SDMVSTRA.nunique()==15 and len(support)==30 and support.groupby('SDMVSTRA').size().eq(2).all()
    counts={'raw_file_rows':{'DEMO_L':len(demo),'BMX_L':len(bmi),'TRIGLY_L':len(tg)},'fasting_weight_positive':int(tg.WTSAF2YR.gt(0).sum()),'fasting_weight_zero':int(tg.WTSAF2YR.eq(0).sum()),'fasting_weight_missing':int(tg.WTSAF2YR.isna().sum()),'positive_weight_valid_design_rows':len(full),'positive_weight_missing_design_rows':int((merged.WTSAF2YR.gt(0)&~good_design).sum()),'TG_to_DEMO_unmatched':int(merged.demo_join.ne('both').sum()),'TG_to_BMI_unmatched':int(merged.bmi_join.ne('both').sum()),'adult_20_79_valid_demographic_rows':int(adult.sum()),'adult_invalid_or_missing_BMI':int((adult&~good_bmi).sum()),'adult_invalid_or_missing_TG':int((adult&~good_tg).sum()),'eligible_complete_rows':len(observed),'full_design_strata':int(support.SDMVSTRA.nunique()),'full_design_PSUs':len(support),'domain_strata':int(dom_support.SDMVSTRA.nunique()),'domain_PSUs':len(dom_support),'nominal_domain_df':len(dom_support)-int(dom_support.SDMVSTRA.nunique()),'native_reference_unit_check':'LBXTLG*0.01129 equals LBDTRSI within rounding tolerance','outcome_values_distributions_or_associations_released':False}
    write(VISIBLE/'preparation_counts.json',counts)
    metadata={'case_id':protocol['case_id'],'n_rows':len(observed),'mode':'enrichment','row_id':'record_id','observed_file':'observed.csv','observed_schema':[{'name':'record_id','kind':'string','role':'identifier'},{'name':'age','kind':'integer','unit':'years','role':'observed'},{'name':'sex','kind':'category','categories':[1,2],'mapping':{'1':'male','2':'female'},'role':'observed'},{'name':'bmi','kind':'number','unit':'kg/m^2','role':'observed'}],'generated_column':{'name':'tg_mg_dl','kind':'number','unit':'mg/dL','strictly_positive':True,'nullable':False},'population':'NHANES August 2021-August 2023 positive-weight fasting subsample, MEC-examined adults 20-79 with positive BMI and reference-method TG. Entire TG column hidden.','purpose':'Compare source-evidence-compatible generator structures for adjusted age relation and full-domain BMI curvature; no desired sign.','requirements':['Preserve every observed cell and row order; append positive finite tg_mg_dl.','Use approved non-NHANES source evidence only. Measurement documentation is permitted metadata, not target relationship evidence.','Do not inspect custodian, fetch outcome tables, link public records or inspect prior target results.','Freeze all structures and all seeds before any target evaluation.'],'measurement_note':'measurement_note.md','protocol_sha256':digest(HERE/'analysis_protocol.json'),'information_boundary':'Procedural only, not OS isolation.'}
    write(VISIBLE/'task_metadata.json',metadata)
    (VISIBLE/'measurement_note.md').write_text('''# Target measurement metadata\n\nThe target is reference-method fasting serum triglycerides in mg/dL, measured in the NHANES August 2021-August 2023 morning-examination subsample. Qualifying fasting is at least 8 and less than 24 hours. The required variable is LBXTLG in TRIGLY_L, not the standard biochemistry-profile triglyceride variable.\n\nCDC documents a change to a non-glycerol-blanked method and a new instrument for this collection period. The official measurement comparison equations are:\n\n- Forward: new-method TG (mg/dL) = 12.45 + 1.022 × old-method TG (mg/dL).\n- Backward: old-method TG (mg/dL) = -12.19 + 0.9785 × new-method TG (mg/dL).\n\nCDC reports coefficient intervals for the method comparison, but these equations are not population age/BMI/sex relationships. They do not establish assay interchangeability or justify modifying a target relationship to match a desired sign. Native LBXTLG units are the generation target; source-to-target assay transfer must be recorded as a modeling decision. The custodian also prespecifies a separate backward-calibration sensitivity.\n\nSource: [CDC TRIGLY_L analytic notes](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/TRIGLY_L.htm). This excerpt is a measurement-only allowance. Builders must not follow the page into outcome data or use NHANES-derived population association studies.\n''',encoding='utf-8')
    (VISIBLE/'README.md').write_text('''# Covariate-only target input\n\nobserved.csv contains only opaque IDs, age, sex (1 male; 2 female), and BMI. Append tg_mg_dl while preserving every input cell and row order. Use the supplied measurement note for target assay context. The complete reference TG column, survey weights, design variables and SEQN mapping remain custodial. No reference mean, distribution, association or fitted endpoint has been computed or released.\n\nThis is a fresh-period temporal replication within NHANES, not a wholly independent external cohort. The main intended analyses are the BMI/sex-adjusted age coefficient in natural-log TG and the age/sex-adjusted full-domain quadratic BMI contrast, with raw-TG curvature as a secondary scale check. No direction is presumed. All structures and seeds must be frozen before evaluation. NHANES-derived construction evidence, target linkage and prior target outcome results are excluded. This is a procedural holdout, not OS isolation.\n''',encoding='utf-8')
    write(VISIBLE/'input_hashes.json',{'created_utc':now(),'files':{p.name:digest(p) for p in sorted(VISIBLE.iterdir()) if p.is_file()}})
    write(HERE/'preparation_receipt.json',{'completed_utc':now(),'protocol_sha256':digest(HERE/'analysis_protocol.json'),'protocol_freeze_sha256':digest(HERE/'protocol_freeze.json'),'methods_freeze_sha256':digest(HERE/'methods_freeze.json'),'hidden_table_sha256':digest(HERE/'design_with_hidden_outcome.csv'),'visible_input_hashes_sha256':digest(VISIBLE/'input_hashes.json'),'provenance_sha256':digest(HERE/'data_provenance.json'),'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'pyreadstat':pyreadstat.__version__},'target_analyses_run':False})
    write(HERE/'custodian_lock.json',{'frozen_utc':now(),'files':{name:digest(HERE/name) for name in ['analysis_protocol.json','protocol_freeze.json','methods_freeze.json','survey_analysis.py','evaluate_committed.py','prepare_case.py','preparation_receipt.json','fresh_overlap_inventory.json','data_provenance.json']},'hidden_table_sha256':digest(HERE/'design_with_hidden_outcome.csv'),'visible_input_hashes_sha256':digest(VISIBLE/'input_hashes.json'),'release_requires_controller_guard':True,'target_analyses_run':False})
    print(json.dumps({'status':'prepared_no_outcome_analysis','visible_folder':str(VISIBLE),'counts':counts,'protocol_sha256':digest(HERE/'analysis_protocol.json'),'custodian_lock_sha256':digest(HERE/'custodian_lock.json')}))

if __name__=='__main__': main()

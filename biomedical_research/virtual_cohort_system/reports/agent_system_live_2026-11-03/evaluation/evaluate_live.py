"""Final developmental comparison. Refuses target reads until both authors close."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, platform, sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import pyreadstat
import scipy
from generated_diagnostics import analyze_generated
from comparison_core import analyze_reference,independently_check,comparison

HERE=Path(__file__).resolve().parent
LIVE=HERE.parent
P=HERE.parents[2]
sys.path.insert(0,str(P))
from cohort_harness import execution,lifecycle
PROTOCOL_SHA='4e95e8e32bf4e33b18502ea6051481400cf6ef4886acade990184119284dc7d0'
DEFINITION_SHA='52333d983959caf54c136540c4b31109c634358f078b7360ffa76ca070408d6a'
SEEDS=[7301,7302,7303]

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def closure_gate(path):
    assert sha(LIVE/'PROTOCOL.json')==PROTOCOL_SHA
    assert sha(HERE/'EVALUATION_DEFINITION.json')==DEFINITION_SHA
    definition=read(HERE/'EVALUATION_DEFINITION.json')
    assert sha(HERE/'generated_diagnostics.py')==definition['generated_diagnostics']['sha256']
    protocol=read(LIVE/'PROTOCOL.json');closure=read(path)
    assert closure['protocol_sha256']==PROTOCOL_SHA and set(closure['requests'])=={'A','B'}
    rows=[];inventories={}
    for key in ('A','B'):
        item=closure['requests'][key]
        assert item['author_closed'] is True
        bundle=Path(protocol['bundles'][key]);session=LIVE/'sessions'/key
        initial=item['initial_candidate'];final=item['final_candidate']
        initial_receipt=lifecycle.verify_candidate(bundle,initial)
        final_receipt=lifecycle.verify_candidate(bundle,final)
        assert initial_receipt['revision_index']==0 and initial_receipt['parent'] is None
        decision=(bundle/item['decision_file']).resolve()
        assert decision.is_relative_to(bundle.resolve()) and sha(decision)==item['decision_sha256']
        choice=read(decision)['choice'];assert choice==item['choice'] and choice in {'retain','revise'}
        if choice=='retain':
            assert final==initial,'Retained outputs must explicitly reuse the frozen initial candidate'
        else:
            assert final_receipt['revision_index']==1 and final_receipt['parent']['candidate']==initial
            assert final_receipt['parent']['sha256']==sha(bundle/initial/'freeze.json')
        reservations=list(session.glob('*_reserved.json'))
        assert 1<=len(reservations)<=8
        reserved={read(p)['run_id']:read(p) for p in reservations}
        assert len(reserved)==len(reservations)
        actual_runs={p.name for p in (bundle/'executions').iterdir() if p.is_dir()}
        assert actual_runs<=set(reserved),'Unbudgeted physical execution directory'
        for run_id,event in reserved.items():
            assert event['charged'] is True
            assert (session/(run_id+'_result.json')).exists(),'Unresolved reserved attempt'
        assert set(item['delivery_runs'])=={'initial','final'}
        for stage in ('initial','final'):
            ids=item['delivery_runs'][stage];assert len(ids)==3 and len(set(ids))==3
            for seed,run_id in zip(SEEDS,ids):
                assert run_id in reserved and reserved[run_id]['seed']==seed
                expected_candidate=initial if stage=='initial' else final
                record=read(session/(run_id+'_result.json'))
                assert record['candidate']==expected_candidate
                result={'request':key,'stage':stage,'seed':seed,'run_id':run_id,
                        'candidate':expected_candidate,'status':record['status'],'error':record.get('error'),
                        'execution_status':record.get('execution_status'),
                        'aliased_initial':stage=='final' and run_id in item['delivery_runs']['initial'],
                        'table':None,'execution_receipt_sha256':None,'table_sha256':None}
                if record['status']=='success':
                    receipt=execution.verify_execution(bundle,run_id)
                    assert receipt['status']=='success' and receipt['candidate']==expected_candidate
                    assert receipt['limits']['seed']==seed
                    table=bundle/'executions'/run_id/'output/generated.csv'
                    assert sha(table)==record['table_sha256']
                    result.update(table=str(table),table_sha256=sha(table),
                                  execution_receipt_sha256=sha(bundle/'executions'/run_id/'execution.json'))
                rows.append(result)
        inventories[key]={'reserved_attempts':len(reservations),'execution_directories':len(actual_runs),
                          'choice':choice,'initial_freeze_sha256':sha(bundle/initial/'freeze.json'),
                          'final_freeze_sha256':sha(bundle/final/'freeze.json'),'decision_sha256':sha(decision)}
    assert len(rows)==12 and sum(x['reserved_attempts'] for x in inventories.values())<=16
    return definition,rows,inventories


def independent_selection(frames):
    """Separate linkage/derivation expression; no change to the frozen population definition."""
    b=frames['biomarker_09.sas7bdat'].rename(columns={'IDind':'id'})
    e=frames['pexam_00.sas7bdat'].rename(columns={'IDind':'id','WAVE':'wave'})
    s=frames['surveys_pub_12.sas7bdat'].rename(columns={'Idind':'id'})
    m=frames['mast_pub_12.sas7bdat'].rename(columns={'Idind':'id'})
    merged=b.loc[b.wave.eq(2009)].merge(s.loc[s.wave.eq(2009)],on=['id','wave'],validate='one_to_one')
    merged=merged.merge(m,on='id',validate='many_to_one').merge(e.loc[e.wave.eq(2009)],on=['id','wave'],validate='one_to_one')
    height=np.where(merged.CLN_HT.eq(9),np.nan,merged.HEIGHT)
    weight=np.where(merged.CLN_WT.eq(9),np.nan,merged.WEIGHT)
    ok=np.isfinite(height)&np.isfinite(weight)&(height>0)&(weight>0)
    bmi=np.full(len(merged),np.nan);bmi[ok]=weight[ok]/np.square(height[ok]*.01)
    bmi[(~np.isfinite(bmi))|(bmi<=0)]=np.nan
    values=pd.DataFrame({'age':merged.age,'female':merged.GENDER.map({1:0,2:1}),
                        'bmi':bmi,'glucose':merged.GLUCOSE,'hba1c':merged.HbA1c,'survey_commid':merged.commid})
    required=['age','female','bmi','glucose','hba1c']
    keep=values.age.ge(35)&values.age.le(74)&values.female.notna()&np.isfinite(values[required]).all(axis=1)
    return values.loc[keep].reset_index(drop=True)


def run(closure_path):
    definition,slots,inventory=closure_gate(closure_path)
    oldplan=Path(definition['metadata_only_original_plan']['path'])
    oldengine=Path(definition['original_pure_linkage_engine']['path'])
    assert sha(oldplan)==definition['metadata_only_original_plan']['sha256']
    assert sha(oldengine)==definition['original_pure_linkage_engine']['sha256']
    private=P/'work/chns_admission_2026-11-01/private_data'
    for item in definition['reference_files']:assert sha(private/item['file'])==item['sha256']
    # The exclusive receipt is written only after complete frozen-generation verification.
    read_receipt={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'exposed development only',
        'closure_sha256':sha(closure_path),'protocol_sha256':PROTOCOL_SHA,'definition_sha256':DEFINITION_SHA,
        'code_sha256':{name:sha(HERE/name) for name in ('evaluate_live.py','comparison_core.py','generated_diagnostics.py')},
        'inventories':inventory,'all_authors_closed':True,'reference_files':definition['reference_files']}
    write(HERE/'REFERENCE_READ_RECEIPT.json',read_receipt)
    frames={}
    for item in definition['reference_files']:
        frames[item['file']],_=pyreadstat.read_sas7bdat(str(private/item['file']),usecols=item['columns'],user_missing=False)
    plan=read(oldplan);engine=load_module(oldengine,'frozen_chns_selection')
    reference,quality=engine.prepare_reference_frames(frames,plan)
    alternate=independent_selection(frames)
    columns=['age','female','bmi','glucose','hba1c','survey_commid']
    pd.testing.assert_frame_equal(reference[columns].sort_values(columns).reset_index(drop=True),
        alternate[columns].sort_values(columns).reset_index(drop=True),rtol=1e-12,atol=1e-12,check_dtype=False)
    refs={key:analyze_reference(reference,key) for key in ('A','B')}
    independent={'linkage':'PASS: separate linkage order and BMI/eligibility derivation',
                 'reference':{key:independently_check(reference,refs[key],key,reference=True) for key in refs},'generated':[]}
    # Compare all original declared E1/E2/E3 coefficients against frozen old helper, without rerunning its campaign.
    for item in plan['estimands']:
        old=engine._fit(reference,item,plan,True)
        request='A' if item['id']=='E1' else 'B'
        if item['id']=='E2':continue # Different predictor set; not one of the new two analyses.
        current=refs[request]['coefficients'][item['term']]
        np.testing.assert_allclose([current['value'],current['standard_error'],current['lower'],current['upper']],
            [old['coefficient'],old['interval']['standard_error'],old['interval']['lower'],old['interval']['upper']],rtol=1e-8,atol=1e-10)
    for slot in slots:
        path=slot.pop('table')
        slot['analysis']=None;slot['comparison']=None
        if path is not None:
            data=pd.read_csv(path,dtype={'person_id':'string'},float_precision='round_trip')
            assert len(data)==3000
            analysis=analyze_generated(data,slot['request'])
            check=independently_check(data,analysis,slot['request'])
            independent['generated'].append({'run_id':slot['run_id'],'stage':slot['stage'],**check})
            slot.update(analysis=analysis,comparison=comparison(refs[slot['request']],analysis))
    report={'schema_version':1,'kind':'closed_live_agent_development_comparison',
            'protocol_sha256':PROTOCOL_SHA,'definition_sha256':DEFINITION_SHA,'closure_sha256':sha(closure_path),
            'reference':refs,'reference_quality':quality,'inventories':inventory,'slots':slots,
            'independent_recomputation':independent,
            'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
                        'scipy':scipy.__version__,'pyreadstat':pyreadstat.__version__},
            'limitations':['Previously exposed development sample, not new independent confirmation.',
               'Three draws per stage measure conditional Monte Carlo variation, not three clinical cohorts.',
               'Synthetic HC3 intervals exclude source, model and transport uncertainty.',
               'Reference CR1-t intervals concern the selected unweighted community-clustered sample.',
               'No equivalence claim, composite success score or target-informed model modification.']}
    write(HERE/'REPORT.json',report)
    print(json.dumps({'reference_n':len(reference),'slots':len(slots),'inventory':inventory,
                      'reference_recomputation':independent['reference']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--closure',type=Path,required=True)
    args=parser.parse_args();run(args.closure)

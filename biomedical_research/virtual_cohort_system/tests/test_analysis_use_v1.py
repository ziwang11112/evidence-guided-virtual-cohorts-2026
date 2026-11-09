"""Invented rows and declarations; no patient, target, network or model access."""
from copy import deepcopy
import json

import numpy as np
import pandas as pd
import pytest

from cohort_harness import analysis_use_v1 as use
from cohort_harness.contracts import ContractError
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256
from test_whole_cohort_feedback import _example, execute_direct, frame, write
from test_analysis_evidence import direct_manifest


def prepared(tmp_path, *, freeze=True, edit=None):
    root = _example.prepare(tmp_path/'b', n_rows=8); candidate = root/'candidates/initial'
    task = read_json(root/'task.json')
    for name in ('z','w'):
        task['columns'].append({'name':name,'kind':'number','unit':'x_unit','role':'generated','nullable':False})
    write(root/'task.json',task); write(root/'request.json',{'purpose':'Invented use only'})
    data = frame(); data['x']=np.arange(8,dtype=float); data['w']=1.; data['z']=data['x']+1
    (candidate/'generator.py').unlink()
    data[[c['name'] for c in task['columns']]].to_csv(candidate/'generated.csv',index=False)
    manifest=direct_manifest(); manifest['analyses'][0]['evidence_links'][0]['evidence_id']='E_y_mean'
    contract={'schema_version':1,'analyses':[{'id':a['id'],'estimand':deepcopy(a['estimand'])} for a in manifest['analyses']],
              'coherence_rules':[
                  {'id':'order_xz','operator':{'kind':'order','left':'x','right':'z','unit':'x_unit','tolerance':0.},
                   'measurement_interpretation':'Invented exact quantities',
                   'basis':{'kind':'algebraic','reference':'Fixture definition','locator':'z=x+w and w=1'}},
                  {'id':'sum_z','operator':{'kind':'sum','total':'z','components':['x','w'],'unit':'x_unit','tolerance':0.},
                   'measurement_interpretation':'Invented exact quantities',
                   'basis':{'kind':'task','reference':'Fixture request','locator':'z=x+w'}}]}
    (root/'input').mkdir(); write(root/use.CONTRACT,contract)
    plan={'schema_version':1,'use_contract_sha256':sha256(root/use.CONTRACT),
          'rules':[{'id':r['id'],'applicability':'applicable','reason':'Exact invented quantities',
                    'assumption_ids':['A_fixture']} for r in contract['coherence_rules']]}
    if edit: edit(root,candidate,manifest,plan,contract)
    write(candidate/use.EVIDENCE_PLAN,manifest); write(candidate/use.PLAN,plan)
    if freeze: freeze_candidate(root,candidate)
    return root,candidate


def analyze(root,candidate):
    execute_direct(root,candidate)
    return use.analyze(root/'executions/run01/output/generated.csv',root/'task.json',root/'request.json')


def test_actual_direct_execution_coverage_and_bindings(tmp_path):
    root,candidate=prepared(tmp_path)
    result=analyze(root,candidate)
    assert result['status']=='computed'
    assert result['evidence_coverage']['requested_id_and_estimand_coverage']=='exact_pinned_contract'
    assert result['evidence_coverage']['assessment_origin']=='submitter_declaration'
    assert result['scientific_validity']=='not_certified'
    assert result['bindings']['coherence_plan_sha256']==sha256(candidate/use.PLAN)
    assert result['bindings']['output_sha256']==sha256(root/'executions/run01/output/generated.csv')
    for row in result['coherence']:
        assert row['n_total']==row['n_evaluated']==row['n_satisfying']==8
        assert row['n_violating']==row['n_unknown']==0
        assert row['assessment']=='observed_consistent'
        assert row['basis_authenticated'] is False


def test_preflight_does_not_read_rows(tmp_path,monkeypatch):
    root,candidate=prepared(tmp_path,freeze=False)
    def forbidden(*args,**kwargs): pytest.fail('No row read allowed')
    monkeypatch.setattr(use.lc,'read_table',forbidden)
    monkeypatch.setattr(use,'calculate_rule',forbidden)
    assert use.preflight(root,candidate)['status']=='ready'


@pytest.mark.parametrize('change',['missing_id','duplicate_id','altered_adjustment','altered_unit','altered_measurement'])
def test_exact_requested_use_coverage(tmp_path,change):
    def edit(root,candidate,manifest,plan,contract):
        a=manifest['analyses'][0]
        if change=='missing_id': a['id']='other_use'
        elif change=='duplicate_id': manifest['analyses'].append(deepcopy(a))
        elif change=='altered_adjustment': a['estimand']['adjustment']=['x']
        elif change=='altered_unit': a['estimand']['unit']='other_unit'
        else: a['estimand']['measurement']='Changed measurement definition'
    root,candidate=prepared(tmp_path,freeze=False,edit=edit)
    assert use.preflight(root,candidate)['status']=='validation_error'


@pytest.mark.parametrize('change',['missing_rule','duplicate_rule','contract_hash','unknown_assumption','empty_reason','invalid_applicability'])
def test_author_plan_errors_are_structured(tmp_path,change):
    def edit(root,candidate,manifest,plan,contract):
        if change=='missing_rule': plan['rules'].pop()
        elif change=='duplicate_rule': plan['rules'].append(deepcopy(plan['rules'][0]))
        elif change=='contract_hash': plan['use_contract_sha256']='0'*64
        elif change=='unknown_assumption': plan['rules'][0]['assumption_ids']=['unknown']
        elif change=='empty_reason': plan['rules'][0]['reason']=''
        else: plan['rules'][0]['applicability']='passed'
    root,candidate=prepared(tmp_path,edit=edit)
    result=analyze(root,candidate)
    assert result['status']=='validation_error'
    assert result['coherence'] is None and result['errors']
    assert result['output_link_verified'] is True


def test_missing_plan_reported_without_forging_success(tmp_path):
    root,candidate=prepared(tmp_path,freeze=False)
    (candidate/use.PLAN).unlink(); freeze_candidate(root,candidate)
    result=analyze(root,candidate)
    assert result['status']=='validation_error'
    assert result['bindings']['coherence_plan_sha256'] is None


@pytest.mark.parametrize('change',['units','self_order','duplicate_component','self_component','negative_tolerance','infinite_tolerance','boolean_tolerance'])
def test_invalid_host_rules_halt(tmp_path,change):
    root,candidate=prepared(tmp_path,freeze=False)
    c=read_json(root/use.CONTRACT); op=c['coherence_rules'][0]['operator']
    if change=='units': op['right']='y'
    elif change=='self_order': op['right']='x'
    elif change=='duplicate_component': c['coherence_rules'][1]['operator']['components']=['x','x']
    elif change=='self_component': c['coherence_rules'][1]['operator']['components']=['x','z']
    elif change=='negative_tolerance': op['tolerance']=-1
    elif change=='infinite_tolerance': op['tolerance']=float('inf')
    else: op['tolerance']=True
    # Invalid JSON constants are deliberately written only in the fixture.
    (root/use.CONTRACT).write_text(json.dumps(c),encoding='utf8')
    with pytest.raises((ContractError,ValueError)):
        use.preflight(root,candidate)


def rule(kind='order',applicability='applicable',tolerance=0.):
    op={'kind':kind,'unit':'invented','tolerance':tolerance}
    op.update({'left':'x','right':'z'} if kind=='order' else {'total':'z','components':['x','w']})
    return {'id':'fixture','operator':op,'applicability':applicability,'reason':'Declared test scope',
            'assumption_ids':[],'measurement_interpretation':'Invented exact quantities',
            'basis':{'kind':'task','reference':'Fixture','locator':'Definition'}}


@pytest.mark.parametrize('applicability',['applicable','unresolved','not_applicable'])
def test_order_counts_and_applicability_separate(applicability):
    data=pd.DataFrame({'x':[0.,2.,4.,np.nan,5.,1e308], 'z':[1.,2.,3.,1.,np.inf,-1e308]})
    r=use.calculate_rule(data,rule(applicability=applicability))
    assert (r['n_total'],r['n_evaluated'],r['n_missing'],r['n_nonfinite'],r['n_arithmetic_nonfinite'])==(6,3,1,1,1)
    assert r['n_violating']==1 and r['n_satisfying']==2 and r['n_unknown']==3
    assert r['max_violation']==1 and r['violation_fraction_evaluated']==pytest.approx(1/3)
    assert r['assessment']==('contradicted' if applicability=='applicable' else applicability)
    assert not any(k in r for k in ('rows','row_ids','records'))


def test_sum_absolute_tolerance_and_boundary():
    data=pd.DataFrame({'x':[1.,1.,1.],'w':[1.,1.,1.],'z':[2.25,1.75,2.5]})
    r=use.calculate_rule(data,rule(kind='sum',tolerance=.25))
    assert r['n_violating']==1 and r['n_satisfying']==2
    assert r['max_violation']==.5


def test_missing_column_and_all_missing_never_pass():
    for data in (pd.DataFrame({'x':[1.]}),pd.DataFrame({'x':[np.nan],'z':[1.]})):
        r=use.calculate_rule(data,rule())
        assert r['assessment']=='unresolved' and r['n_evaluated']==0
        assert r['max_violation'] is None


@pytest.mark.parametrize('artifact',['output','freeze','candidate'])
def test_integrity_tampering_halts(tmp_path,artifact):
    root,candidate=prepared(tmp_path); execute_direct(root,candidate)
    path={'output':root/'executions/run01/output/generated.csv','freeze':candidate/'freeze.json',
          'candidate':candidate/use.PLAN}[artifact]
    path.write_bytes(path.read_bytes()+b'\n')
    with pytest.raises(ContractError):
        use.analyze(root/'executions/run01/output/generated.csv',root/'task.json',root/'request.json')


def test_target_path_never_opened_and_foreign_input_rejected(tmp_path,monkeypatch):
    root,candidate=prepared(tmp_path); execute_direct(root,candidate)
    sentinel=root/'target.json'; sentinel.write_text('DO NOT READ',encoding='utf8')
    original=use.lc.read_json
    def guard(path,*args,**kwargs):
        assert str(path)!=str(sentinel)
        return original(path,*args,**kwargs)
    monkeypatch.setattr(use.lc,'read_json',guard)
    assert use.analyze(root/'executions/run01/output/generated.csv',root/'task.json',root/'request.json')['status']=='computed'
    with pytest.raises(ContractError):
        use.analyze(sentinel,root/'task.json',root/'request.json')

"""New controlled development task; copy source-only baseline, never old outputs."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.request_intake import prepare_request
from cohort_harness import lifecycle

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f: json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False); f.write('\n')

def main():
    old = WORKSPACE/'evcAdaptiveL02'
    bundle = WORKSPACE/'evcUseR02'
    closed = read(PROJECT/'work/adaptive_evidence_loop_2026-11-09/AUTHOR_CLOSED.json')
    task = read(old/'task.json')
    task['task_id'] = 'analysis-use-coherence-development-2026-11-09'
    task['budget'] = {'source_queries':32,'source_downloads':32,'revisions':1}
    task['information_policy']['allowed_tools'] = sorted(set(task['information_policy']['allowed_tools']+['analysis_use_v1']))
    request = read(old/'request.json')
    request = {'schema_version':1,'purpose':'Controlled development of scientific-use evidence coverage and cross-variable coherence: underlying same-specimen lipid concentration scenarios, with no explicit assay-error model. Keep all requested analyses; no target-effect calibration or clinical-accuracy evaluation in this unit.',
               'analyses':request['analyses'],'task':task}
    prepare_request(request,bundle)
    registry=[]; history=[]
    for item in read(old/'registry.json')['artifacts']:
        source=old/item['path']
        if sha(source)!=item['sha256'] or closed['files'].get(item['path'])!=item['sha256']:
            raise ValueError('Previously admitted source changed')
        relative=item['path'].replace('sources/web_evidence_v1/','sources/curated/inherited_web_v1/')
        dest=bundle/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        registry.append({**item,'path':relative,'origin':'curator'})
        history.append({'source_id':item['source_id'],'path':relative,'original_path':item['path'],'sha256':item['sha256'],'previous_origin':item['origin'],'new_role':'previously acquired approved artifact; no new download'})
    (bundle/'registry.json').write_text(json.dumps({'artifacts':registry},indent=2)+'\n',encoding='utf8')
    (bundle/'input').mkdir()
    if sha(old/'input/population_metadata.json')!=closed['files']['input/population_metadata.json']:
        raise ValueError('Historical methods metadata changed')
    shutil.copyfile(old/'input/population_metadata.json',bundle/'input/population_metadata.json')
    write(bundle/'input/source_admission_history.json',history)
    shutil.copytree(old/'skills',bundle/'skills')
    source=old/'candidates/initial';dest=bundle/'candidates/baseline';dest.mkdir(parents=True)
    names=['generator.py','model_spec.json','evidence.json','decision.md','checks.json','deterministic_math.json','whole_cohort_feedback.json','source_semantics_v1.json','descriptive_feedback_v1.json']
    baseline={}
    for name in names:
        if sha(source/name)!=closed['files']['candidates/initial/'+name]:raise ValueError('Original baseline changed')
        shutil.copyfile(source/name,dest/name);baseline[name]=sha(dest/name)
    original_baseline=dict(baseline)
    evidence_path=dest/'evidence.json'
    evidence=read(evidence_path)
    for source_item in evidence['sources']:
        for artifact in source_item['artifacts']:
            artifact['path']=artifact['path'].replace('sources/web_evidence_v1/','sources/curated/inherited_web_v1/')
    evidence_path.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    baseline['evidence.json']=sha(evidence_path)
    for name in ('source_semantics_v1.json','descriptive_feedback_v1.json'):
        declaration=read(dest/name)
        if declaration['evidence_sha256']!=original_baseline['evidence.json']:raise ValueError('Original binding mismatch')
        declaration['evidence_sha256']=baseline['evidence.json']
        (dest/name).write_text(json.dumps(declaration,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        baseline[name]=sha(dest/name)
    write(bundle/'input/provenance_only_rebinding.json',{'original_files':original_baseline,'current_files':baseline,
        'path_mapping':{'sources/web_evidence_v1/':'sources/curated/inherited_web_v1/'},
        'changes':'evidence artifact locations and two evidence hash bindings only; scientific values, law and assumptions unchanged; source bytes unchanged; historical manifests remain original provenance, not new-session approvals.'})
    write(bundle/'input/baseline_commitments.json',{'source_unit':'adaptive_evidence_loop_2026-11-09','candidate':'candidates/baseline','files':baseline,'note':'Original scientific law and source statistics, with provenance-only artifact-path and evidence-hash rebinding documented separately; no old outcomes or reference results. New use/coherence sidecars may be added; copied files remain unchanged in baseline.'})
    population=task['population']
    measurement='Underlying same-specimen lipid concentration scenarios; source-assay transfer remains an explicit assumption; no independent assay-error model is specified.'
    (bundle/'input/INTERPRETATION_NOTE.md').write_text('# Interpretation for this development task\n\nThe use_contract and current request define underlying, same-specimen concentration scenarios without an explicit assay-error model. The copied population metadata and historical decision record describe the earlier measured-data context and remain unchanged provenance. This new use claim governs this exercise; it is not proof that earlier recorded-value violations were biological impossibilities. Adopting measured source moments for an underlying concentration law is an explicit, unvalidated source-assay-to-latent transfer assumption. No observation-error distribution is supplied or inferred from a marginal biological SD. Retain source uncertainty and every generated row. The component rule is not a requested correlation or slope.\n',encoding='utf8')
    analyses=[]
    for identifier,outcome in [('K02-HDL-BMI','hdl_cholesterol'),('K02-TC-BMI','total_cholesterol')]:
        analyses.append({'id':identifier,'estimand':{'description':'Unweighted OLS with intercept, age, F/M sex and BMI; report 5 times the BMI coefficient after multiplying lipid values by 38.67.',
             'kind':'ols_coefficient','outcome':outcome,'exposures':['bmi'],'conditioning':[],'adjustment':['age','sex'],
             'scale':'Raw lipid mg/dL per 5 kg/m^2 BMI','unit':'mg/dL per 5 kg/m^2','population':population,'measurement':measurement,
             'selection':'All generated adult rows with complete finite age, sex, BMI and lipid values; no post-generation exclusion.'}})
    analyses.append({'id':'K02-LIPID-RESIDUAL','estimand':{'description':'Pearson correlation of paired TC and HDL residuals after separate unweighted OLS on intercept, age, F/M sex and BMI, using the same eligible rows.',
         'kind':'reported_other','statistic_name':'partial_pearson_correlation','outcome':'hdl_cholesterol','exposures':['total_cholesterol'],'conditioning':[],
         'adjustment':['age','sex','bmi'],'scale':'Pearson correlation of adjusted residuals','unit':'1','population':population,'measurement':measurement,
         'selection':'All generated adult rows with complete finite age, sex, BMI and both lipid values; no post-generation exclusion.'}})
    basis=read(HERE/'RULE_BASIS.json')
    contract={'schema_version':1,'analyses':analyses,'coherence_rules':[{'id':'lipid_component_order',
         'operator':{'kind':'order','left':'hdl_cholesterol','right':'total_cholesterol','unit':'mmol/L','tolerance':0.0},
         'measurement_interpretation':measurement,
         'basis':{'kind':'algebraic','reference':basis['component_definition_url'],'locator':'Total cholesterol includes HDL cholesterol; same-specimen underlying concentrations, equal units. See input/rule_basis.json for source and noisy-assay qualifications.'}}]}
    write(bundle/'input/use_contract.json',contract);shutil.copyfile(HERE/'RULE_BASIS.json',bundle/'input/rule_basis.json')
    lifecycle._registry(bundle)
    old_protocol=read(PROJECT/'work/adaptive_evidence_loop_2026-11-09/PROTOCOL.json')
    protocol={'unit':HERE.name,'bundle':str(bundle),'purpose':request['purpose'],'seeds':[9601,9602,9603],'rows_per_output':3000,
       'candidate_cap':2,'execution_cap':6,'analysis_adapters':['generated','analysis_use'],
       'baseline_science':baseline,'baseline_candidate':'candidates/baseline','primary_check':'Declared component consistency: raw violating count, complete/missing denominator, magnitude, applicability; retain every output.',
       'required_analyses':old_protocol['required_analyses'],'required_diagnostics':old_protocol['required_diagnostics'],
       'collateral_changes':'All three scientific analyses and 23 diagnostics, plus all source feedback. Descriptive changes only; no equivalence margin or target-accuracy claim.',
       'author_freedom':'Choose whether/how to revise scientific construction, retrieve more evidence, or retain/stop. No repair algorithm, coefficient, desired association sign or clinical reference supplied.',
       'source_review':'Audit source extraction, rule applicability and evidence-use declarations; no coordinator-selected scientific parameters.',
       'interpretation_change':'Underlying same-specimen concentrations govern this new exercise. Copied historical measured-assay metadata are provenance, not the new product definition. Source measured moments to underlying-law transfer is assumed; this does not diagnose all prior observed-value violations as biological impossibilities.',
       'stopping_rule':'At most baseline plus one optional revised candidate, all three fixed seeds per submitted stage. No target comparison, no extra case or iteration in this unit.',
       'interpretation':'Controlled development repair, not a new clinical validation, broad agent advantage or benefit of a rubric versus an adequate ordinary instruction.',
       'privacy':'Individual tables and full sources stay local. Original code/docs and aggregates may be published.'}
    write(HERE/'PROTOCOL.json',protocol)
    write(HERE/'STATE.json',{'phase':'prepared_awaiting_review','bundle':str(bundle),'reference_access':'none','executions':0})
    print(json.dumps({'bundle':str(bundle),'source_artifacts':len(registry),'baseline_scientific_files':len(baseline)}))

if __name__=='__main__':main()

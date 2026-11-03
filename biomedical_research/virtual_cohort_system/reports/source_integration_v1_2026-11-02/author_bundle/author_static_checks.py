"""Metadata and declared-law checks only. Never imports the candidate program."""
from pathlib import Path
import ast
import hashlib
import json
import math
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
C = ROOT / 'candidates' / 'initial'
P = ROOT.parent / 'biomedical_research' / 'virtual_cohort_system'
sys.path.insert(0, str(P))
sys.path.insert(0, str(P / 'work' / 'evidence_revision_v1_2026-11-02' / 'implementation'))
from cohort_harness.contracts import validate_task, validate_evidence, validate_spec, exact_keys
from cohort_harness.lifecycle import read_json, validate_program
from cohort_harness.analysis_evidence import summarize_analysis_evidence
from evidence_use_v1 import assess_evidence_use
from scientific_validity_v1 import assess_law
from qualified_relationships_v1 import _alias_contract, _mapping_contract, _operator_contract

def load(name): return read_json(C / name)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name, obj):
    (C/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n',encoding='utf-8')

task=read_json(ROOT/'task.json'); evidence=load('evidence.json'); spec=load('model_spec.json')
validate_task(task); ids=validate_evidence(evidence,task); validate_spec(spec,ids)
validate_program(C/'generator.py')
assert sha(C/'evidence.json') == 'a10a223af16f040d34fa82a5d183128c8e40396cc009ffb92395b715b386a648'
assert evidence == read_json(ROOT/'input'/'compiled_evidence.json')
analysis=summarize_analysis_evidence(load('analysis_evidence.json'),task,evidence,spec)
bridge=load('context_bridge_v1.json'); qualified=load('qualified_plan_v1.json')
strict_ids=[x['id'] for c in bridge['contexts'] if c['recipe'] for x in c['recipe']['checks']]
use=assess_evidence_use(load('evidence_use_v1.json'),evidence,spec,recipe_check_ids=strict_ids)
laws={c:assess_law(law) for c,law in load('scientific_validity_v1.json')['context_laws'].items()}
assert all(report['manifest_valid'] for report in laws.values())
assert all(a['second_moment_status']=='pass' for report in laws.values() for a in report['analyses'])
known={a['id'] for a in spec['assumptions']}; items={i['id']:i for i in evidence['items']}
parameters=spec['parameters']; contexts=parameters['contexts']
assert set(bridge['shared_parameters']) == set(parameters)-{'active_context','contexts'}
varying={v['name'] for v in bridge['context_varying_parameters']}
assert all(set(d)=={'population','n_rows','measurement','inputs'} and set(d['inputs'])==varying for d in contexts.values())
assert parameters['active_context']=='T' and contexts['T']['population']==task['population'] and contexts['T']['n_rows']==3000
assert bridge['trials']==[{'id':n,'context_id':c,'seed':s,'n_rows':contexts[c]['n_rows']} for n,c,s in [('srcJ','J',23011),('srcB','B',23012),('srcM','M',23013),('dormantT','T',23999)]]
assert bridge['budget']=={'source_attempts':3,'source_rows':3000,'target_attempts':1,'target_rows':3000}
assert bridge['execution_limits']=={'timeout_seconds':60,'memory_mb':1536,'output_bytes':4000000,'log_bytes':20000}
qualified_results=[]
for context in bridge['contexts']:
    cid=context['id']; descriptor=contexts[cid]
    if cid=='T':
        assert context['feedback_policy']=='none' and context['recipe'] is context['semantics'] is context['supplement'] is None
        continue
    assert context['feedback_policy']=='semantic_v1' and context['supplement'] is None
    recipe=context['recipe']; semantic=context['semantics']; declaration=qualified['contexts'][cid]
    exact_keys(recipe,{'schema_version','population','measurement','assumption_ids','checks'},where='author recipe static check')
    assert recipe['population']==descriptor['population']==declaration['population']
    assert recipe['measurement']=={'mode':'identity','description':descriptor['measurement']}
    assert declaration['measurement']==descriptor['measurement']
    assert set(context['assumption_ids']) <= set(recipe['assumption_ids']) <= known
    assert declaration['bindings']=={}
    assert semantic['evidence_sha256']==semantic['recipe_sha256']==''
    strict={s['id']:s for s in recipe['checks']}
    assert set(strict)=={b['check_id'] for b in semantic['bindings']}
    for check in recipe['checks']:
        exact_keys(check,{'id','evidence_id','status','operator','assumption_ids','reason'},where='author strict check')
        assert check['status']=='not_computable' and check['operator'] is None
    for binding in semantic['bindings']:
        exact_keys(binding,{'check_id','evidence_id','source_locator','definition_status','source_operator','weights','transform','source_variable_units','source_n','uncertainty_role','reason'},where='author semantic binding')
        assert binding['evidence_id']==strict[binding['check_id']]['evidence_id']
        assert binding['source_locator']==items[binding['evidence_id']]['locator']
        assert binding['definition_status']==binding['weights']==binding['uncertainty_role']=='not_reported'
        assert binding['source_operator'] is None and binding['source_variable_units']=={} and binding['source_n']=={'status':'not_reported'} and binding['transform']=='identity'
    columns,origins=_alias_contract(declaration['column_aliases'],{c['name']:c for c in task['columns']},known)
    for check in declaration['checks']:
        mapped=_mapping_contract(check['measurement_mapping'],check['operator'],columns,items,known)
        _operator_contract(check['operator'],items[check['evidence_id']],mapped)
        assert check['id']!=check['semantic_check_id'] and check['semantic_check_id'] in strict
        assert check['source_relation']['assumed_weights']=='equal'
        qualified_results.append({'id':check['id'],'status':'metadata_valid','context':cid,'operator_and_native_units':'validated_without_rows'})

dep=parameters['dependence']; q=dep['bmi_glucose_latent_correlation']; k=dep['shared_bmi_residual_loading']
domain=[]
for cid,descriptor in contexts.items():
    c=descriptor['inputs']; values=c['age_values']; probs=c['age_probabilities']
    assert len(values)==len(probs) and len(set(values))==len(values) and all(type(v) is int for v in values)
    assert all(p>0 for p in probs) and math.isclose(sum(probs),1,rel_tol=0,abs_tol=1e-12)
    assert 0<c['female_probability']<1 and len(values)>1
    assert all(c[x]>0 for x in ('bmi_log_sd','glucose_log_sd','hba1c_log_sd'))
    r=dep['jansen_restricted_latent_correlation'] if c['dependence_rule']=='restricted' else dep['bao_latent_correlation']+(dep['mind_latent_correlation']-dep['bao_latent_correlation'])*(c['glucose_log_sd']-dep['bao_glucose_log_sd'])/(dep['mind_glucose_log_sd']-dep['bao_glucose_log_sd'])
    residual=1-r*r-k*k
    assert abs(q)<1 and residual>0
    assert (min(values),max(values))=={'J':(18,81),'B':(20,80),'M':(61,80),'T':(35,74)}[cid]
    assert c['glucose_upper_clip']==(6.999 if cid=='J' else None)
    domain.append({'context':cid,'age_min':min(values),'age_max':max(values),'age_mass_sum':sum(probs),
      'female_probability':c['female_probability'],'latent_rho':r,'hba1c_residual_variance':residual,
      'domain_status':'pass','population_rank_status':'author_argument_requires_independent_review'})

# AST inventory is syntax/read-only inspection, not behavioral certification.
tree=ast.parse((C/'generator.py').read_text())
imports=[n.names[0].name for n in ast.walk(tree) if isinstance(n,ast.Import)]
assert imports==['numpy','pandas']
report={'schema_version':1,'scope':'source_only_metadata_and_declared_law_no_rows',
 'generator_imported':False,'generator_executed':False,'random_sampling':False,'numerical_source_diagnostics':False,
 'evidence_bytes_preserved':True,'input_hashes':{name:sha(C/name) for name in ['evidence.json','generator.py','model_spec.json','analysis_evidence.json','evidence_use_v1.json','scientific_validity_v1.json','context_bridge_v1.json','qualified_plan_v1.json','context_eligibility.json','decision.md']},
 'contracts':{'task_evidence_model':'pass','program_abi_syntax':'pass','initial_cli_validate':{'contract':'valid','route':'program','generator_executed':False,'scientific_validity':'not_assessed'}},
 'analysis_evidence':analysis,'evidence_use':use,'declared_laws':laws,'qualified_operator_metadata':qualified_results,
 'bridge_metadata':'author_static_shape_schedule_and_placeholder_checks_passed; official frozen preflight not run',
 'checker_development_corrections':['First author_static_checks invocation stopped with TypeError because exact_keys requires keyword where. Checker call signatures were corrected; no generator import or row calculation occurred.', 'Controller technical review clarified qualified declaration bindings must be exactly empty objects at author submission. Placeholders corrected before submission; scientific values unchanged.'],
 'parameter_domains':domain,'ast_import_inventory':imports,
 'limitations':['No independent code/law review performed by this author.', 'Moment proofs concern declared laws only and do not certify code correspondence, full rank of a sample, transport or uncertainty.',
 'Official bridge preflight and full qualified preparation require controller freeze/review/bindings and were not run.',
 'No generator import/execution, source table, source diagnostic, target table or target statistic was produced.']}
save('author_static_report.json',report)
save('checks.json',{'scope':'source_only','records':[
 {'name':'candidate_contract','status':'pass','detail':'Actual CLI validate returned valid/program, generator_executed false; pure schema and ABI checks also passed. Bound report records the inputs and scope.'},
 {'name':'declared_second_moments','status':'pass','detail':'Actual assess_law ran on four declared contexts; all 12 planned analysis second-moment checks pass. Full scientific status remains unresolved pending independent code/rank review.'},
 {'name':'evidence_and_operator_metadata','status':'pass','detail':'Actual evidence-use, analysis-evidence, native qualified alias/mapping/operator metadata and schedule/domain checks passed without tables. Every admitted item is represented.'},
 {'name':'source_statistics','status':'not_computable','detail':'No generator was imported or executed and no source diagnostic was run. Strict checks remain unavailable; qualified comparisons await controller-authorized execution.'},
 {'name':'frozen_bridge_and_qualified_preparation','status':'not_computable','detail':'Full preparation requires independent review/freeze/child hashes owned by controller. This author created no approval or freeze artifact.'},
 {'name':'target_validity','status':'not_computable','detail':'No target dispatch/data/results are permitted. Transport, age/sex effects and target composition are unsupported assumptions.'}],
 'artifacts':[{'path':'author_static_report.json','sha256':sha(C/'author_static_report.json')}]})
print(json.dumps({'status':'metadata_static_checks_passed','moment_checks':12,'scientific_status':'unresolved_independent_review_required',
 'qualified_operator_metadata_checks':len(qualified_results),'generator_imported':False,'sampling':False,
 'evidence_raw_sha256':sha(C/'evidence.json'),'report_sha256':sha(C/'author_static_report.json')},indent=2))

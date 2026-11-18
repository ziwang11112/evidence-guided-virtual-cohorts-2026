"""Create the bounded application task; contains no fitted biological law."""
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
R=Path(__file__).resolve().parent
OLD=R.parent/'request_only_repeatability_2026-11-11'
def write(name,text):
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
def dump(name,obj):write(name,json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
now=datetime.now(timezone.utc).isoformat()
old=json.loads((OLD/'PLAN.json').read_text(encoding='utf-8'))
limits=dict(old['limits']);limits.update(total_usd_cap=8.0,max_executions=2,max_runs=2,max_candidates=2,diagnostic_seed=63001)
plan=dict(schema_version=1,created_utc=now,status='bounded_new_construction_pending_independent_review',
    model=old['model'],limits=limits,common_instructions_path='policies/common.txt',
    evidence_paths=['TASK_EVIDENCE.md','PUBLISHED_TABLE1.json'],evaluation_seeds=[64001,64003,64007],
    episodes=[dict(episode_id='LIFESTYLE_A'+str(i),case_id='lifestyle',arm='workflow',task_path='tasks/LIFESTYLE.json',request_path='requests/LIFESTYLE.txt',policy_path='policies/workflow.txt',constructor_repeat=i) for i in [1,2]])
dump('PLAN.json',plan)
task=json.loads((OLD/'tasks/LIPID.json').read_text(encoding='utf-8'))
task.update(task_id='LIFESTYLE_LEA2020_SOURCE_RECONSTRUCTION',n_rows=1226,
    population='Fictional complete measurements for 1226 Turkana adults older than 18 years, including pastoralist, rural nonpastoralist and urban nonpastoralist lifestyles; original Lea2020 study is permitted evidence. No observed individual records are supplied.')
task['columns']=[dict(name='id',kind='string',unit='',role='identifier',nullable=False),
    dict(name='age',kind='number',unit='years',role='generated',nullable=False,minimum=18),
    dict(name='sex',kind='category',unit='',role='generated',nullable=False,categories=['F','M']),
    dict(name='lifestyle',kind='category',unit='',role='generated',nullable=False,categories=['pastoralist','rural_nonpastoralist','urban_nonpastoralist'])]+[
    dict(name=n,kind='number',unit=u,role='generated',nullable=False,minimum=0) for n,u in [('bmi','kg/m2'),('total_cholesterol','mg/dL'),('hdl_cholesterol','mg/dL')]]
task['information_policy']['excluded_cohorts']=['evidence-guided-virtual-cohorts-2026','virtual_cohort_system']
task['budget']=dict(source_queries=20,source_downloads=16,revisions=1)
dump('tasks/LIFESTYLE.json',task)
common=(OLD/'policies/common.txt').read_text(encoding='utf-8')
common=common.replace('The user has not provided papers, extracted statistics, individual measurements or a fitted model.', 'The user supplies approved published aggregate evidence and a study citation. No real participant measurements, previous project generators or newly calculated reference results are provided. The original Lea2020 study and its published results ARE allowed evidence for this source-rich reconstruction task.')
common=common.replace('6 candidate submissions and 6 trial executions','2 candidate submissions and 2 trial executions')
common+='\nThe task requires complete measurements in all seven columns; do not generate missing cells. Use age strictly above 18 and positive biomarkers. Mathematical distributions must have finite first and second moments. Record physiological assumptions and any HDL-above-TC issue rather than silently hiding it. The host does not supply a probability law or numerical relationship. A trial checks generated data only; a finalization without trial is allowed and will be disclosed. At most one revised immutable candidate is available, including interface repair.\n'
write('policies/common.txt',common)
write('policies/workflow.txt',(OLD/'policies/workflow.txt').read_text(encoding='utf-8'))
write('requests/LIFESTYLE.txt','''Generate a new fictional whole cohort for the lifestyle analyses in Lea et al. 2020 (Science Advances, DOI 10.1126/sciadv.abb1430, PMC7577730). No individual observations are inputs. Use the supplied published evidence and retrieve any useful additional literature through your tools. All scientific structure and values are your decisions, with their sources or assumptions recorded.

Deliver an executable stochastic generator for exactly 1226 complete rows in the contract order: id, age, sex, lifestyle, bmi, total_cholesterol, hdl_cholesterol. All three lifestyle groups and both sexes must be analysable; do not invent a separate unrequested category. The source demography is internally inconsistent; state your approach without accessing participant records. Complete virtual biomarker measurement is an explicit task choice; it does not reproduce the original study's missingness or give 1226 new clinical observations.

Intended analyses are visible: for each of BMI/TC/HDL, standardize by the pooled available-case sample mean and SD, fit outcome ~ three-level lifestyle + age in years + sex, and report rural-minus-pastoralist, urban-minus-pastoralist and urban-minus-rural contrasts. Also fit lifestyle-by-sex interaction (2 df Gaussian ML LRT, nominal .05) and retain all sex-specific age-adjusted contrasts on that same pooled outcome scale. There are 9 additive and 18 sex-specific contrasts. The main use is preserving scientific patterns and effect magnitudes, not exact per-person recovery or a mandatory p-value. A known published nonsignificant finding does not imply exactly zero effect.

You may search, inspect source methods/tables, construct a model, run generated-only checks, and choose whether to revise. The final output should support the whole requested analysis suite with one selected law. Source evidence is allowed, but new real-data results and earlier project outputs are unavailable for tuning. Explain important assumptions and the origin of numerical choices concisely. Do not merely promise to generate later: submit and finalize your law within the budget.
''')
dump('TARIFF_VERIFICATION.json',dict(checked_utc=now,provider='OpenAI',model='gpt-6.1-sol',
    urls=['https://developers.openai.com/api/docs/models/gpt-6.1-sol','https://developers.openai.com/api/docs/pricing','https://developers.openai.com/api/docs/guides/function-calling'],
    verified_model_rates=old['model'],account_balance_known=False,note='Official current documentation read by root in this turn; rates are estimates, not an invoice; authenticated nonpaid availability GET stored separately.'))
dump('ANALYSIS_TEST_RECEIPT.json',dict(recorded_utc=now,command='python -B -X utf8 -m unittest discover -s work/lifestyle_application_2026-11-11 -p test_analysis.py -v',passed=6,failed=0,
    execution_observed='All 6 tests passed in 0.102 seconds; no rerun. Invented fixtures only.',
    files={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['analysis_operator.py','test_analysis.py']}))
dump('STATE.json',dict(updated_utc=now,status='preflight_preparation',real_lifestyle_outcomes_read=False,paid_calls=0,final_tables=0,next='independent preflight; freeze; two fresh Agent episodes; final draw; shared analysis; independent recomputation'))
print('Prepared protocol inputs; no API or real-data analysis')

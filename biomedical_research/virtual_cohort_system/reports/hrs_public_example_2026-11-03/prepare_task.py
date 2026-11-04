from pathlib import Path
import json, sys
U=Path(__file__).resolve().parent; P=U.parents[1]
sys.path.insert(0,str(P))
from cohort_harness.contracts import validate_task

def main():
    cols=[]
    def col(name,kind,unit,role='generated',**kw):
        cols.append(dict(name=name,kind=kind,unit=unit,role=role,nullable=False,**kw))
    col('id','string','visit_identifier','identifier')
    col('subject_id','string','synthetic_subject_identifier')
    col('visit_time','integer','year',minimum=0,maximum=6)
    col('baseline_age','number','year',minimum=50,maximum=100)
    col('age','number','year',minimum=50,maximum=106)
    col('age60','number','decade_from_age_60',minimum=-1,maximum=4.6)
    col('sex','category','category',categories=['female','male'])
    col('race','category','category',categories=['white','black'])
    col('educ','category','category',categories=['College','HS','LessThanHS'])
    col('cses','number','source_childhood_SES_scale')
    col('hba1c','number','%',minimum=0)
    col('mem_s','number','source_standardized_memory_scale')
    task={'schema_version':1,'task_id':'Filshtein_HRS_recipient_example_2026-11-03','mode':'whole_cohort',
          'population':'HRS published recipient-stage model: 11509 synthetic subjects represented by exported age/sex/race cells, four balanced visits at0/2/4/6years. Source conditional summaries and author-reported analysis are permitted input; no source individual records. This represents the supplied HRS scientific law, not an untouched population validation.',
          'row_id':'id','n_rows':46036,'columns':cols,
          'information_policy':{'mode':'published_evidence','excluded_cohorts':[],
          'allowed_tools':['admitted_source_read','analytic_calculation','invented_input_check','isolated_final_generation']},
          'budget':{'source_queries':0,'source_downloads':0,'revisions':0}}
    validate_task(task)
    b=U/'bundle'; b.mkdir(exist_ok=True)
    out=b/'task.json'
    if out.exists():
        assert json.loads(out.read_text())==task,'Existing task differs; preserve original.'
    else: out.write_text(json.dumps(task,indent=2)+'\n')
    state=U/'STATE.json'
    if not state.exists():state.write_text(json.dumps({'phase':'implementation','execution_released':False,'final_seeds':[6101,6102,6103],'final_attempts_allowed':6,'final_attempts_spent':0,'patient_source_records_read':False},indent=2)+'\n')
    print(json.dumps({'task':str(out),'columns':len(cols),'rows':task['n_rows']}))
if __name__=='__main__':main()

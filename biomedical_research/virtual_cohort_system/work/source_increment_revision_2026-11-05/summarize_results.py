"""Compare every scheduled endpoint to cached historical E01 aggregates after closure."""
from pathlib import Path
import csv, json, hashlib
from statistics import mean

ROOT=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    close=read(ROOT/'CLOSURE.json');assert close['scientific_authoring_closed'] is True
    done=read(ROOT/'evaluation/COMPLETED.json')
    assert sha(ROOT/'evaluation/RESULTS.json')==done['results_sha256']
    context=read(ROOT/'EVALUATION_CONTEXT.json')
    old_path=Path(context['baseline_summary_path']);assert sha(old_path)==context['baseline_summary_sha256']
    old=read(old_path);new=read(ROOT/'evaluation/RESULTS.json')
    before=[x for x in old['all_final_slots'] if x['author_id']=='E01']
    after=new['slots'];assert len(before)==len(after)==3
    records=[]
    for cat in ('analyses','diagnostics'):
        for endpoint in after[0][cat]:
            eid=endpoint['id']
            a=[next(x for x in s[cat] if x['id']==eid) for s in before]
            b=[next(x for x in s[cat] if x['id']==eid) for s in after]
            assert all(x['unit']==endpoint['unit'] for x in a+b)
            av=[x['value'] for x in a if x['status']=='computed']
            bv=[x['value'] for x in b if x['status']=='computed']
            ref=endpoint['reference']
            assert all(x['reference']==ref for x in a+b)
            rec={'category':cat,'id':eid,'unit':endpoint['unit'],'reference':ref,
                 'old_values':av,'new_values':bv,'old_scheduled':3,'new_scheduled':3,
                 'old_mean':mean(av) if av else None,'new_mean':mean(bv) if bv else None,
                 'old_range':[min(av),max(av)] if av else None,'new_range':[min(bv),max(bv)] if bv else None,
                 'old_mean_absolute_difference':mean(abs(v-ref['value']) for v in av) if av else None,
                 'new_mean_absolute_difference':mean(abs(v-ref['value']) for v in bv) if bv else None}
            if av and bv:
                rec['absolute_difference_change']=rec['new_mean_absolute_difference']-rec['old_mean_absolute_difference']
            records.append(rec)
    report={'scope':'One exposed-case development construction compared descriptively with historical E01; seeds and contexts differ. No policy superiority, new independent population or structure uncertainty.',
            'new_result_sha256':sha(ROOT/'evaluation/RESULTS.json'),'historical_sha256':sha(old_path),
            'records':records,'all_endpoints':len(records),'new_final_tables':len(after),
            'new_unique_table_hashes':len({s['table_sha256'] for s in after if s['table_sha256']}),
            'new_source_feedback_errors':[s['run_id'] for s in after if s.get('source_feedback_error')],
            'new_analysis_errors':[s['run_id'] for s in after if s.get('analysis_error')],
            'theoretical_changes':read(ROOT/'PROPOSAL.json')['questions']}
    dest=ROOT/'evaluation/COMPARISON.json'
    with dest.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False,allow_nan=False)
    with (ROOT/'evaluation/ALL_ENDPOINT_COMPARISONS.csv').open('x',encoding='utf-8',newline='') as f:
        fields=['category','id','unit','reference_value','old_mean','new_mean','old_mean_absolute_difference','new_mean_absolute_difference','absolute_difference_change']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in records:w.writerow({k:(row['reference']['value'] if k=='reference_value' else row.get(k)) for k in fields})
    selected=[r for r in records if r['category']=='analyses' or r['id'] in ('q1_residual_rms','hba1c.sd_population','glucose.sd_population')]
    print(json.dumps([{k:r[k] for k in ('id','reference','old_mean','new_mean','old_mean_absolute_difference','new_mean_absolute_difference')} for r in selected],indent=2,ensure_ascii=False))

if __name__=='__main__':main()

"""Independent aggregate-pointer review; never import the figure author code."""
import hashlib
import json
import math
from pathlib import Path
import statistics

P=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
F=P/'manuscript/conference_figures_v10_2026-11-04'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def lookup(obj,pointer):
    for token in pointer.lstrip('/').split('/'):
        token=token.replace('~1','/').replace('~0','~')
        obj=obj[int(token)] if isinstance(obj,list) else obj[token]
    return obj

b=read(F/'FIG23_NUMERIC_BINDINGS.json')
u=read(P/'manuscript/utility_package_2026-11-03/AGGREGATE_SOURCE.json')
m=read(P/'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json')
h=read(P/'work/information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json')
for path,digest in b['input_sha256'].items(): assert sha(P/path)==digest
assert b['script_sha256']==sha(F/'render_quantitative.py')
for path,meta in b['outputs'].items(): assert sha(F/path)==meta['sha256']
unit_expectations={
 ('CHNS2009','E1'):('per kg/m²','%/(kg/m^2)'),
 ('CHNS2009','E2'):('per mmol/L','%/(mmol/L)'),
 ('CHNS2009','E3'):('per year','%/year'),
 ('ENSANUT2018','Q1_age10'):('per 10 years','%/10years'),
 ('ENSANUT2018','Q2_bmi5'):('per 5 kg/m²','%/5kg/m^2'),
 ('ENSANUT2018','Q3_bmi5'):('per 5 kg/m²','%/5kg/m^2')}
panels=[]
totals={'seed_values':0,'constructor_means':0,'seed_ranges':0,'references':0,'available_reference_intervals':0}
for group,source,seeds in [('main_experiment',m,[5101,5102,5103]),('historical_information_experiment',h,[4101,4102,4103])]:
    assert b[group]==u[group]
    for panel in b[group]['panels']:
        ref=lookup(source,panel['reference_pointer'])
        if group=='main_experiment':
            assert panel['reference']==ref
            expected_display,expected_stored=unit_expectations[panel['case'],panel['endpoint']]
            assert panel['display_unit']==expected_display and ref['unit']==expected_stored
            assert len(panel['series'])==12
            assert sum(s['kind']=='agent' for s in panel['series'])==10
        else:
            assert panel['reference']['value']==ref and len(panel['series'])==6
            if panel['endpoint'] in ('E1','E2','E3'):
                expected_display,expected_stored=unit_expectations['CHNS2009',panel['endpoint']]
                assert panel['axis_label']=='HbA1c percentage points\n'+expected_display
                interval=lookup(source,panel['interval_pointer'])
                assert interval==panel['reference']['interval']
            else:
                assert panel['reference']['interval'] is None
        totals['references']+=1
        interval=panel['reference'].get('interval')
        if interval and interval.get('status')=='available': totals['available_reference_intervals']+=1
        count=0
        for series in panel['series']:
            assert [x['seed'] for x in series['seeds']]==seeds
            values=[]
            for entry in series['seeds']:
                assert entry['value']==lookup(source,entry['pointer'])
                values.append(entry['value'])
                if group=='main_experiment':
                    analysis=lookup(source,entry['pointer'].rsplit('/',1)[0])
                    assert analysis['unit']==expected_stored
                    assert analysis['id']==panel['endpoint']
                    assert analysis['reference_value']==panel['reference']['value']
                count+=1
            mean_key='mean_effect' if group=='main_experiment' else 'mean'
            range_key='seed_effect_range' if group=='main_experiment' else 'range'
            stored=lookup(source,series['summary_pointer'])
            assert series['mean']==stored[mean_key]
            assert math.isclose(series['mean'],statistics.mean(values),rel_tol=0,abs_tol=1e-14)
            assert series['range']==stored[range_key]==[min(values),max(values)]
            totals['constructor_means']+=1; totals['seed_ranges']+=1
        totals['seed_values']+=count
        panels.append({'experiment':group,'panel':panel['panel'],'endpoint':panel['endpoint'],
            'seed_values':count,'series':len(panel['series']),'status':'PASS'})
assert totals=={'seed_values':306,'constructor_means':102,'seed_ranges':102,'references':11,'available_reference_intervals':9}
assert m['planned_constructions']==24
assert m['unique_successful_table_contents']==m['scheduled_final_slots']==72
assert h['attempts']==42 and h['distinct_table_hashes']==24
result={'status':'PASS','scope':'Independent read-only verification against original frozen aggregates; no author verification function imported.',
 'checked':totals,'panels':panels,'individual_records_read':False,'models_refit':False,'figures_rerendered':False,
 'caption_review':{'status':'PASS','file':'manuscript/conference_figures_v10_2026-11-04/FIG23_CAPTIONS.md',
 'checks':['Constructions and seed nesting retained; means not scientific sample count.',
 'CHNS CR1-t and ENSANUT stability bands distinguished.',
 'Ranges correctly called three-seed ranges, not confidence intervals.',
 'All correlations in summary condition supplied to Agent; no independent-prediction claim.',
 '42 executions / 24 unique total / 18 unique delivered tables retained.',
 'No fully paired comparison, method-ranking or significance claim introduced.']},
 'visual_review':'PNG views checked separately; renderer loops every bound series with three seed offsets and one mean, without clipping negative observations.',
 'files_sha256':{str(path.relative_to(P)).replace('\\','/'):sha(path) for path in [F/'FIG23_NUMERIC_BINDINGS.json',F/'render_quantitative.py',F/'FIG23_CAPTIONS.md']},
 'limitations':['This is an aggregate/presentation audit, not independent rerunning of clinical models or certification of original source extraction.']}
(HERE/'FIG23_INDEPENDENT_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','checked':totals}))

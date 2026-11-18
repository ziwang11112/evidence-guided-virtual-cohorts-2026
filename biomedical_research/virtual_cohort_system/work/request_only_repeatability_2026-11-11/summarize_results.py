"""Summarize all frozen outputs after closure; no fitted scores or author changes."""
from pathlib import Path
import json
import statistics

ROOT = Path(__file__).resolve().parent
METRICS = {
    'PNS': [('bmi_sbp','BMI–SBP'),('bmi_dbp','BMI–DBP'),('residual_correlation','Residual SBP–DBP'),
            ('sbp.sd_population','SBP SD'),('dbp.sd_population','DBP SD'),('sbp_below_dbp_fraction','SBP < DBP fraction')],
    'lipids': [('K02-TC-BMI','BMI–TC'),('K02-HDL-BMI','BMI–HDL'),('K02-LIPID-RESIDUAL','Residual TC–HDL'),
               ('total_cholesterol.sd_sample','TC SD'),('hdl_cholesterol.sd_sample','HDL SD'),('hdl_above_total_fraction','HDL > TC fraction')],
}


def fmt(x):
    return 'unavailable' if x is None else f'{x:.4f}'


def main():
    plan=json.loads((ROOT/'PLAN.json').read_text(encoding='utf-8'))
    assert len(plan['episodes'])==12 and all((ROOT/'episodes'/p['episode_id']/'OUTCOME.json').is_file()for p in plan['episodes'])
    e=json.loads((ROOT/'EVALUATION.json').read_text(encoding='utf-8'))
    assert e['counts']['episodes']==12 and e['counts']['final_slots']==36
    lookup={(r['episode_id'],r['analysis_id']):r for r in e['summaries']}
    groups=[]
    for case,metrics in METRICS.items():
        for metric,label in metrics:
            for arm in ['ordinary','workflow']:
                rows=[r for r in e['summaries']if r['case_id']==case and r['arm']==arm and r['analysis_id']==metric]
                assert len(rows)==3
                values=[r['mean']for r in rows if r['mean']is not None]
                ref=rows[0]['reference']['value']
                groups.append({'case':case,'analysis_id':metric,'label':label,'arm':arm,'constructors_assigned':3,
                               'constructors_with_estimate':len(values),'constructor_mean':statistics.mean(values)if values else None,
                               'constructor_min':min(values)if values else None,'constructor_max':max(values)if values else None,
                               'reference_value':ref,'mean_abs_difference_of_constructor_means':statistics.mean(abs(v-ref)for v in values)if values and ref is not None else None})
    text=['# Complete repeatability aggregate tables','',
          'Every assigned constructor is retained. Group means below average available constructor means, not independent patients; availability is reported explicitly. Ranges span constructors. See the primary figures for individual simulation seeds. These are descriptive developmental comparisons with previously exposed sample references.','',
          f"Final-table slots: {e['counts']['successful_tables']} delivered, {e['counts']['failed_tables']} failed, {e['counts']['unavailable_tables']} unavailable / 36 planned. Model calls: {e['counts']['model_calls']}. Known tariff cost: USD{e['costs']['known_tariff_usd']:.7f}; accounted cost: USD{e['costs']['accounted_usd']:.7f}.",'']
    for case,metrics in METRICS.items():
        text += [f'## {case}: every constructor','', '| Constructor | '+ ' | '.join(label for _,label in metrics)+' |',
                 '|---|'+'---:|'*len(metrics)]
        rows=sorted([p for p in plan['episodes']if p['case_id']==case],key=lambda p:(p['arm']!='ordinary',p['constructor_repeat']))
        for p in rows:
            text.append('| '+p['episode_id']+' | '+' | '.join(fmt(lookup[(p['episode_id'],m)]['mean'])for m,_ in metrics)+' |')
        refs=[lookup[(rows[0]['episode_id'],m)]['reference']['value']for m,_ in metrics]
        text += ['| Existing sample reference | '+' | '.join(fmt(v)for v in refs)+' |','']
        units=[lookup[(rows[0]['episode_id'],m)]['unit']for m,_ in metrics]
        text += ['Units in column order: '+ '; '.join(units)+'.','',
                 'Blood-pressure SD uses the saved population-SD convention; lipid SD uses the saved sample-SD convention. Fractions are proportions, not percentages. A reference zero is not asserted unless present in the pinned reference.','']
    text += ['## Descriptive policy profiles','',
             '| Case | Analysis | Policy | Available authors | Mean | Author range | Reference | Mean absolute difference |',
             '|---|---|---|---:|---:|---|---:|---:|']
    for r in groups:
        text.append(f"| {r['case']} | {r['label']} | {r['arm']} | {r['constructors_with_estimate']}/3 | {fmt(r['constructor_mean'])} | {fmt(r['constructor_min'])}–{fmt(r['constructor_max'])} | {fmt(r['reference_value'])} | {fmt(r['mean_abs_difference_of_constructor_means'])} |")
    text += ['','No cross-analysis composite score, post hoc equivalence tolerance or pooled clinical success rate is defined. Direction agreement alone does not establish analytical usefulness.','',
             '## Construction and resources','',
             '| Constructor | Terminal status | Selected | Calls | Queries | Downloads | Candidates | Trials | Known USD | Unknown calls |',
             '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for o in e['episodes']:
        u=o.get('tool_usage')or{}
        text.append(f"| {o['episode_id']} | {o['status']} | {o.get('selected_candidate')or 'none'} | {o['calls_reserved']} | {u.get('queries','NA')} | {u.get('downloads','NA')} | {u.get('candidates','NA')} | {u.get('executions','NA')} | {o['known_tariff_cost_usd']:.7f} | {o['unknown_usage_calls']} |")
    text += ['','Candidate/seed counts do not measure independent clinical evidence. A v001 selection is retention of the first submitted program; trial success is not scientific source or target validation.','']
    (ROOT/'AGGREGATE_TABLES.md').write_text('\n'.join(text),encoding='utf-8')
    (ROOT/'SUMMARY_STATS.json').write_text(json.dumps({'counts':e['counts'],'costs':e['costs'],'group_profiles':groups},indent=2),encoding='utf-8')
    print(json.dumps({'profiles':len(groups),'constructors':12,'all_planned_slots':36}))


if __name__=='__main__':
    main()

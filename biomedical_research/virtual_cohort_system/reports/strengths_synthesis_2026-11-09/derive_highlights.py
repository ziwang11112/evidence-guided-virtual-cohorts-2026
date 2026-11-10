"""Descriptive synthesis from frozen aggregates; no row access or new evaluation."""
from pathlib import Path
import csv, hashlib, json, statistics

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    primary=PROJECT/'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json'
    d=read(primary);rows=[]
    for contrast in d['agent_information_contrasts']:
        case,endpoint=contrast['case_id'],contrast['endpoint']
        row={'case':case,'endpoint':endpoint,'unit':contrast['unit']}
        for arm in ('E0','E1'):
            constructors=[c for c in d['construction_summaries'] if c['case_id']==case and c['information_condition']==arm and c['constructor_kind']=='agent']
            agent=[next(e for e in c['endpoints'] if e['id']==endpoint) for c in constructors]
            assert len(agent)==5 and all(e['complete'] for e in agent)
            expected=contrast['arms'][arm]['mean_constructor_mean_absolute_discrepancy']
            actual=statistics.mean(e['mean_absolute_discrepancy'] for e in agent)
            assert abs(actual-expected)<1e-12
            reference=next(c for c in d['statistical_references'] if c['case_id']==case and c['information_condition']==arm)
            fixed=next(e for e in reference['endpoints'] if e['id']==endpoint)['mean_absolute_discrepancy']
            row.update({arm+'_agent_mad':actual,arm+'_statistical_mad':fixed,
                        arm+'_agent_relative_mad_reduction_vs_this_fixed_spec':1-actual/fixed,
                        arm+'_authors_lower_mad_than_fixed_spec':sum(e['mean_absolute_discrepancy']<fixed for e in agent),
                        arm+'_author_count':len(agent),
                        arm+'_constructor_mean_min':min(e['mean_effect'] for e in agent),
                        arm+'_constructor_mean_max':max(e['mean_effect'] for e in agent)})
        row['E1_relative_mad_reduction_vs_E0']=1-row['E1_agent_mad']/row['E0_agent_mad']
        rows.append(row)
    with (HERE/'MAIN_COMPARISONS.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    temporal=PROJECT.parent/'obesity_temporal_prediction_2026-10-25/results/compact_comparison.csv'
    with temporal.open(encoding='utf-8-sig') as f:prediction=list(csv.DictReader(f))
    result={'scope':'Retrospective descriptive synthesis of frozen aggregate estimates; no new patient analysis or generator execution.',
        'source_sha256':{str(primary):sha(primary),str(temporal):sha(temporal)},
        'main_comparisons':rows,
        'descriptive_tallies':{
            'E1_lower_Agent_discrepancy_than_E0':sum(r['E1_agent_mad']<r['E0_agent_mad'] for r in rows),
            'E0_Agent_arm_lower_than_this_fixed_statistical_spec':sum(r['E0_agent_mad']<r['E0_statistical_mad'] for r in rows),
            'E1_Agent_arm_lower_than_this_fixed_statistical_spec':sum(r['E1_agent_mad']<r['E1_statistical_mad'] for r in rows),
            'endpoint_denominator':len(rows)},
        'temporal_prediction_compact_rows':prediction,
        'interpretation':['Ratios are per-endpoint descriptive reductions in sample-reference discrepancy, not accuracy, equivalence or clinical significance.',
                          'Information arms contain different authors. Five Agent laws versus one fixed statistical law per arm is an asymmetric comparison.',
                          'The E0 statistical specification completes unprovided within-source dependence by independence; mixing source components can still induce dependence. These comparisons do not establish superiority over general statistical generation.',
                          'Temporal source information was rich, outcome-conditioned summaries computed from 128 real training records, not literature-only evidence.',
                          'No ranking is pooled across units, old method versions, cohorts or repeated seeds.']}
    (HERE/'DERIVED_HIGHLIGHTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['descriptive_tallies']))
    print(json.dumps([{k:v for k,v in row.items() if k in ['case','endpoint','E1_relative_mad_reduction_vs_E0','E0_authors_lower_mad_than_fixed_spec','E1_authors_lower_mad_than_fixed_spec']} for row in rows],indent=2))

if __name__=='__main__':main()

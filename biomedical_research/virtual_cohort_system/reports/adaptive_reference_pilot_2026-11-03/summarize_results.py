"""Report all declared analyses and diagnostics; no generator import or execution."""
from pathlib import Path
import json, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

U=Path(__file__).resolve().parent
P=U.parents[1]
R=P.parents[1]/'evcAR'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    reports={k:load(R/'session/feedback'/f'{k}.json') for k in ('initial','final')}
    stats={}; slots=[]
    for stage,report in reports.items():
        for run in report['runs']:
            slots.append({'stage':stage,'run_id':run['run_id'],'seed':run['seed'],'status':run['status']})
            if run['status']!='success':continue
            for row in run['reference_evaluation']['analyses']+run['reference_evaluation']['diagnostics']:
                s=stats.setdefault(row['id'],{'reference':row['reference'],'reference_interval':row.get('reference_interval'), 'initial':[], 'final':[]})
                s[stage].append({'seed':run['seed'],'value':row['value'],'difference':row['difference']})
    for sid,s in stats.items():
        for stage in ('initial','final'):
            v=[r['value'] for r in s[stage] if r['value'] is not None]
            s[stage+'_summary']={'n_valid':len(v),'mean':float(np.mean(v)) if v else None,'min':min(v) if v else None,'max':max(v) if v else None,
                'mean_absolute_reference_difference':float(np.mean([abs(x-s['reference']) for x in v])) if v else None}
        ini={r['seed']:r for r in s['initial']}
        s['paired_changes']=[{'seed':r['seed'],'change':r['value']-ini[r['seed']]['value'],
            'absolute_reference_difference_change':abs(r['difference'])-abs(ini[r['seed']]['difference'])}
            for r in s['final'] if r['seed'] in ini and r['value'] is not None and ini[r['seed']]['value'] is not None]
    events=[load(x) for x in sorted((R/'session/events').glob('*.json'))]
    results=[e for e in events if e['kind']=='result']; attempts=[e for e in events if e['kind']=='attempt']
    hashes=[hashlib.sha256((R/a['bundle']/'executions'/a['run_id']/'output/generated.csv').read_bytes()).hexdigest() for a in attempts if (R/a['bundle']/'executions'/a['run_id']/'output/generated.csv').exists()]
    summary={'status':'all_deliveries_reported','reference_role':'exposed developmental input','fresh_scientific_constructions':1,
        'attempts':len(attempts),'successful_executions':sum(e['status']=='success' for e in results),'unique_output_hashes':len(set(hashes)),
        'delivery_slots':slots,'rows_per_table':3000,'execution_elapsed_seconds':sum(e.get('elapsed_seconds',0) for e in results),
        'statistics':stats,'author_decision':load(U/'FINAL_AUTHOR_DECISION.json'),
        'inference':'Seed ranges are conditional generation variation, not confidence intervals or independent clinical evidence. All 30 supplied reference statistics remain development inputs.'}
    (U/'COMPLETE_RESULTS.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    display=['E1','E2','E3','glucose_sd','hba1c_sd','glucose_hba1c_pearson','glucose_hba1c_spearman','bmi_mean']
    labels=['BMI–HbA1c adjusted coefficient','Glucose–HbA1c adjusted coefficient','Age–HbA1c adjusted coefficient','Glucose individual SD','HbA1c individual SD','Glucose–HbA1c Pearson','Glucose–HbA1c Spearman','BMI mean']
    fig,axes=plt.subplots(2,4,figsize=(14,7.2))
    for ax,key,label in zip(axes.flat,display,labels):
        s=stats[key];ax.axhline(s['reference'],color='#bc6c25',lw=1.5,label='Exposed reference')
        ci=s['reference_interval']
        if ci and ci.get('status')=='available':ax.axhspan(ci['lower'],ci['upper'],color='#bc6c25',alpha=.12)
        for j,(a,b) in enumerate(zip(s['initial'],s['final'])):
            offset=(j-1)*.10
            ax.plot([offset,1+offset],[a['value'],b['value']],color='#aab6bf',lw=.9,zorder=1)
            ax.scatter(offset,a['value'],c='#3565a8',s=38,zorder=3)
            ax.scatter(1+offset,b['value'],c='#138678',s=38,zorder=3)
        ax.set_xticks([0,1],['Initial','Final']);ax.set_xlim(-.4,1.4);ax.set_title(label,fontsize=10)
        ax.grid(axis='y',alpha=.2);ax.ticklabel_format(axis='y',style='plain',useOffset=False)
    fig.suptitle('Adaptive Agent generation: paired deliveries after reference feedback',fontsize=15,y=.99)
    fig.text(.5,.012,'Each point is one 3,000-row draw; same seeds paired. Orange bands: real-reference coefficient 95% CIs only.\nAll reference summaries informed construction. This is developmental consistency, not independent validation.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.065,1,.96]);fig.savefig(U/'analysis_use_profile.png',dpi=170);fig.savefig(U/'analysis_use_profile.svg');plt.close(fig)
    lines=['# Adaptive reference-assisted whole-cohort pilot: complete results','',
        'One fresh scientific Agent chose the generative structure and parameters, used deterministic numerical calculations and isolated trial feedback, and revised the same construction. The coordinator provided the full declared reference/evidence package, execution tools and fixed analysis definitions; it did not write scientific coefficients or alter scientific code.',
        '',f"Actual execution: {len(attempts)} attempts, {sum(e['status']=='success' for e in results)} successes, {len(set(hashes))} distinct output tables, 3,000 virtual rows each. These are repeated draws from one scientific construction, not independent clinical cohorts. All source patients and generated individual tables remain local.",
        '', '## Scientific result', '',
        '| Statistic | Exposed CHNS reference | Initial mean [3-seed range] | Final mean [3-seed range] |',
        '|---|---:|---:|---:|']
    for sid in display:
        s=stats[sid]
        def fmt(stage):
            q=s[stage+'_summary'];return f"{q['mean']:.6g} [{q['min']:.6g}, {q['max']:.6g}]"
        lines.append(f"| {sid} | {s['reference']:.6g} | {fmt('initial')} | {fmt('final')} |")
    lines+=['','![Paired analysis profile](analysis_use_profile.png)','',
        'The complete 30-statistic, seed-level results and paired changes are in COMPLETE_RESULTS.json. No global accuracy score or post-hoc equivalence threshold is used. Improved rank agreement does not imply improvement of every statistic; all losses remain visible. Reference intervals characterize the real-sample regression estimates; they are not intervals for means, equivalence bounds or synthetic-model uncertainty.',
        '',
        'The paired rank-correlation discrepancy decreased in all three seeds: mean absolute reference difference 0.060879 to 0.014325. All three regression mean absolute discrepancies increased slightly: E1 0.005164 to 0.005265, E2 0.023061 to 0.023507, E3 0.0003103 to 0.0003320. E2 absolute discrepancy increased in every paired seed. This is a targeted improvement with trade-offs, not global improvement or statistical proof of superiority.',
        '', '## What changed and what this establishes','',
        'The Agent selected a bounded two-component biomarker mixture with age and BMI shifts and component-specific copula dependence. Marginal distributions and regression shifts were derived from explicitly supplied CHNS sample summaries under stated simplifying assumptions. After persistent excess rank association across initial deliveries, the Agent changed component dependence while preserving its analytical covariance target, checked the consequence numerically, and froze a final version before paired delivery evaluation.',
        '',
        'This run supports operation of an actual author/tool/feedback/revision loop and a specific reference-assisted data-use case. Its numerical targets come from CHNS reference summaries; external papers provide qualified context here. It does not establish external-literature-only reconstruction, independent target validity, superiority to conventional statistical synthesis, benefits of multiple Agents, or population-wide recovery.',
        '', '## Unresolved assumptions and failures','',
        '- Covariate independence, absence of a female biomarker term, mixture membership, tail bounds and measurement rounding are assumptions. They do not support untested subgroup, causal, tail-risk or clinical claims.',
        '- Deterministic quadrature convergence is approximate numerical evidence, not a rigorous error certificate. More synthetic rows do not resolve evidence or structural uncertainty.',
        '- The first dependence adjustment did not demonstrate empirical rank improvement under different trial seeds; both trial results were retained. Subsequent persistent three-seed discrepancy informed the final change.',
        '- Initial ar02 freezing failed on mixed text encoding. A coordinator encoding-only repair left mojibake in inherited prose; the failed step and frozen imperfect artifact remain recorded in AR02_ENCODING_REPAIR.json. Scientific code/parameters were unaffected; later author text uses UTF-8.',
        '- Original trial covariance calculation was first executed inline; its reproducible solver was retained in a later candidate. This provenance gap is reported rather than retroactively editing the frozen first trial.',
        '- Automatic approval review rejected deletion of two mocked-test temporary directories with the reason "blocked by policy". They remain local and are excluded from public export.',
        '', '## Scope and next decision','',
        'Keep this bounded pilot closed after independent recomputation. The next discriminating experiment is the already described information comparison: what changes when complete real-reference summaries are not explicitly provided, with research questions and ordinary Agent tools still available. This pilot must not be silently pooled into that later experiment or compared to older literature-only runs as a controlled superiority test.',
        '', '## All supplied statistics','', '| ID | Reference | Initial mean | Final mean |', '|---|---:|---:|---:|']
    for sid,s in stats.items():lines.append(f"| {sid} | {s['reference']:.8g} | {s['initial_summary']['mean']:.8g} | {s['final_summary']['mean']:.8g} |")
    (U/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ('attempts','successful_executions','unique_output_hashes','execution_elapsed_seconds')},indent=2))
if __name__=='__main__':main()

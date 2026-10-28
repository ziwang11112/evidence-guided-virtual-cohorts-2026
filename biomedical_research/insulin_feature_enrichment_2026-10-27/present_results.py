"""Describe every frozen analysis, without selecting models or changing scores."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LABELS = {
 'overall_bmi_per_5':'Overall BMI association (per 5 kg/m²)',
 'adjusted_bmi_per_5':'Adjusted BMI association (per 5 kg/m²)',
 'adjusted_age_per_10':'Adjusted age association (per 10 years)',
 'adjusted_sex_comparison':'Adjusted female–male contrast',
 'upper_minus_lower_bmi_slope_per_5':'Upper–lower BMI slope contrast',
 'sex_difference_bmi_slope_per_5':'Female–male BMI slope difference',
 'sex_reference_bmi_slope_per_5':'Male BMI slope (per 5 kg/m²)',
 'sex_comparison_bmi_slope_per_5':'Female BMI slope (per 5 kg/m²)',
}

# Interpretation labels derived from the frozen source/model provenance; these
# do not alter the prespecified fits, endpoint inclusion, or numerical results.
ROLES = {
 'overall_bmi_per_5':'External-evidence consistency and target magnitude transport',
 'adjusted_bmi_per_5':'Transport of evidence-informed common BMI slope',
 'adjusted_age_per_10':'Transport of assumed age interpolation (A1/A2)',
 'adjusted_sex_comparison':'Challenge to zero direct sex-effect assumption (A4)',
 'upper_minus_lower_bmi_slope_per_5':'Challenge to linear BMI assumption (A3)',
 'sex_difference_bmi_slope_per_5':'Challenge to absent BMI-by-sex interaction (A4)',
 'sex_reference_bmi_slope_per_5':'Male subgroup transport under common slope',
 'sex_comparison_bmi_slope_per_5':'Female subgroup transport under common slope',
}


def state(r):
    lo, hi = r['ci95_low_log_scale'], r['ci95_high_log_scale']
    if lo is None or hi is None: return 'unavailable'
    if lo > 0: return 'positive'
    if hi < 0: return 'negative'
    return 'interval includes zero'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evaluation',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    ev=json.loads(Path(args.evaluation).read_text(encoding='utf-8'))
    out=Path(args.output)
    if out.exists(): raise FileExistsError('Preserve previous report')
    out.mkdir(parents=True)
    refs={r['endpoint']:r for r in ev['reference']['endpoints']}
    models=list(dict.fromkeys(r['model_revision'] for r in ev['generated']))
    table=[]
    for model in models:
        draws=[r for r in ev['generated'] if r['model_revision']==model]
        for endpoint, ref in refs.items():
            selected=[next(t for t in d['endpoints'] if t['endpoint']==endpoint) for d in draws]
            points=np.array([r['estimate_log_scale'] for r in selected])
            counts={s:sum(state(r)==s for r in selected) for s in ['positive','negative','interval includes zero','unavailable']}
            table.append({'model':model,'endpoint':endpoint,'question':LABELS[endpoint],'evidence_role':ROLES[endpoint],
              'reference_log_estimate':ref['estimate_log_scale'],
              'reference_ci_low':ref['ci95_low_log_scale'],'reference_ci_high':ref['ci95_high_log_scale'],
              'reference_ratio':ref['exp_estimate'],'reference_ratio_low':ref['exp_ci95_low'],
              'reference_ratio_high':ref['exp_ci95_high'],'reference_state':state(ref),
              'generated_median_log_estimate':float(np.median(points)),
              'generated_min_log_estimate':float(points.min()),'generated_max_log_estimate':float(points.max()),
              'generated_median_ratio':float(np.exp(np.median(points))),
              'generated_min_ratio':float(np.exp(points.min())),'generated_max_ratio':float(np.exp(points.max())),
              'draw_count':len(points),**{'draws_'+k.replace(' ','_'):v for k,v in counts.items()}})
    df=pd.DataFrame(table)
    df.to_csv(out/'scientific_interpretation.csv',index=False)
    description={
        'reference_correlations':ev['reference']['descriptive_correlations'],
        'models':{m:{key:{'median':float(np.median([d['descriptive_correlations'][key] for d in ev['generated'] if d['model_revision']==m])),
                        'min':float(min(d['descriptive_correlations'][key] for d in ev['generated'] if d['model_revision']==m)),
                        'max':float(max(d['descriptive_correlations'][key] for d in ev['generated'] if d['model_revision']==m))}
                     for key in ev['reference']['descriptive_correlations']} for m in models},
        'interpretation':'A draw range is Monte Carlo variation, not a confidence or prediction interval. Endpoints are correlated and cannot be counted as independent replicated studies.'}
    (out/'correlations.json').write_text(json.dumps(description,indent=2)+'\n',encoding='utf-8')
    lines=['# Prespecified scientific-analysis comparison','',
       'All effects below are on the natural-log insulin scale. Ratios and their reference survey intervals are provided in the accompanying aggregate CSV. No equivalence margin or binary method-success threshold was specified.',
       '', 'The reference interval reflects the survey analysis. Generated ranges describe repeated draws from a fixed Agent-authored generator; they do not include all model, source, or transport uncertainty. Matching sign or interval state alone is not proof of equal effects.',
       '', 'The generated_median_ratio CSV field is exp(median(log-effect)), not the arithmetic median of the exponentiated draws. Endpoint evidence-role annotations were finalized from the frozen provenance after evaluation and do not change the numerical analyses.', '']
    for model in models:
        lines+=['## '+model,'','| Question | Real estimate [95% survey interval] | Generated median [draw min, max] | Real interval state | Generated positive / unresolved / negative draws |','|---|---|---|---|---|']
        for r in [r for r in table if r['model']==model]:
            lines.append(f"| {r['question']} | {r['reference_log_estimate']:.3f} [{r['reference_ci_low']:.3f}, {r['reference_ci_high']:.3f}] | {r['generated_median_log_estimate']:.3f} [{r['generated_min_log_estimate']:.3f}, {r['generated_max_log_estimate']:.3f}] | {r['reference_state']} | {r['draws_positive']} / {r['draws_interval_includes_zero']} / {r['draws_negative']} |")
        lines.append('')
    lines+=['## Evidence roles','',
       'Labels below were finalized in postrun review from the frozen source/model provenance. No endpoint was removed or rescored. Target answers were withheld, but some synthetic patterns are already encoded from the Agent-selected external evidence or explicit assumptions.',
       '', '| Question | Evidence/assumption role |','|---|---|']
    lines += ['| '+LABELS[k]+' | '+ROLES[k]+' |' for k in refs]
    lines+=['','## Interpretation limits','',
       '- Reproduction of relationships already encoded from Agent-selected external evidence is consistency, not independent biological discovery. The coordinator supplied no numerical biological relation.',
       '- Reserved target-specific analyses test transfer under a specified model. Explicit structural assumptions may determine some synthetic patterns.',
       '- A reference interval overlapping zero does not establish absence of association. A synthetic-only confident result is not new empirical confirmation.',
       '- Same people and repeated stochastic generation draws are not additional independent patients or studies.',
       '- Report failures and mismatches alongside preserved conclusions; do not rank models by a chosen favourable endpoint.','']
    (out/'ALL_ANALYSES.md').write_text('\n'.join(lines),encoding='utf-8')
    for model in models:
        sub=df[df.model==model].reset_index(drop=True)
        fig,ax=plt.subplots(figsize=(11,6.3))
        y=np.arange(len(sub))
        ax.axvline(0,color='#aaaaaa',linewidth=.8)
        for i,r in sub.iterrows():
            ax.plot([r.reference_ci_low,r.reference_ci_high],[i-.12,i-.12],color='#505a66',linewidth=2)
            ax.scatter(r.reference_log_estimate,i-.12,color='#505a66',s=34,zorder=3)
            ax.plot([r.generated_min_log_estimate,r.generated_max_log_estimate],[i+.12,i+.12],color='#008579',linewidth=3)
            ax.scatter(r.generated_median_log_estimate,i+.12,color='#008579',s=32,zorder=3)
        ax.set_yticks(y,sub.question)
        ax.invert_yaxis()
        ax.set_xlabel('Effect on natural-log insulin scale; see each row for contrast units')
        ax.set_title('Real analyses and Agent-enriched analyses',loc='left',fontweight='bold')
        ax.plot([],[],color='#505a66',marker='o',label='Real estimate and 95% survey interval')
        ax.plot([],[],color='#008579',marker='o',label='Generated median and min–max across draws')
        fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.66,.095),fontsize=8,frameon=False)
        ax.spines[['top','right']].set_visible(False)
        fig.text(.02,.018,'Generated draw ranges are not confidence intervals. One construction; a single survey cohort.',fontsize=8,color='#505a66')
        fig.tight_layout(rect=(0,.13,1,1))
        fig.savefig(out/(model+'_analyses.png'),dpi=180)
        fig.savefig(out/(model+'_analyses.pdf'))
        plt.close(fig)
    print(json.dumps({'output':str(out.resolve()),'models':models,'all_endpoints':len(table)}))


if __name__=='__main__': main()

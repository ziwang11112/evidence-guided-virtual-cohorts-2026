"""Describe every declared result; this script never modifies a candidate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
import numpy as np
import pandas as pd

E=Path(__file__).resolve().parent
R=E/'evaluation/results'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    table=pd.read_csv(R/'endpoint_comparison.csv')
    reference=read(R/'reference_analyses.json')
    intent=read(E/'pilot_intent.json')
    primary=['adjusted_age_per10','bmi_curvature_second_difference']
    summaries={}
    for name in intent['variants']:
        rows=table[table.variant.eq(name)]
        endpoints={}
        for endpoint in reference:
            x=rows[rows.endpoint.eq(endpoint)].sort_values('seed')
            if len(x)==0:
                endpoints[endpoint]={'status':'nonestimable','reference':reference[endpoint]}
                continue
            estim=x.estimate.to_numpy()
            directional=endpoint.startswith('ordered_') or endpoint in list(reference)[:7]
            endpoints[endpoint]={
                'reference':reference[endpoint],
                'generated_estimates':dict(zip(x.seed.astype(str),map(float,estim))),
                'generated_mean':float(estim.mean()),'generated_min':float(estim.min()),
                'generated_max':float(estim.max()),
                'direction_agrees_count':int(x.point_direction_agrees.sum()) if directional else None,
                'direction_comparison_meaningful':directional,
                'reference_interval_excludes_zero':reference[endpoint]['ci_direction']!='interval_includes_zero',
                'all_seed_points_inside_reference_CI':bool(((estim>=reference[endpoint]['ci_low'])&(estim<=reference[endpoint]['ci_high'])).all()),
                'warning':'Reference intervals are marginal survey intervals, not synthetic model uncertainty or simultaneous inference.'}
        summaries[name]=endpoints
    # Keep paired changes in each endpoint's own units, without a mixed-scale total.
    paired=[]
    for endpoint in reference:
        x=table[table.endpoint.eq(endpoint)]
        for seed in intent['target_seeds']:
            before=x[x.variant.eq('baseline')&x.seed.eq(seed)]
            after=x[x.variant.eq('joint_evidence')&x.seed.eq(seed)]
            if len(before)!=1 or len(after)!=1:continue
            a=before.iloc[0];b=after.iloc[0]
            paired.append({'endpoint':endpoint,'seed':seed,'scale':a['scale'],
                'change_in_estimate':float(b.estimate-a.estimate),
                'change_in_absolute_error':float(b.absolute_error-a.absolute_error),
                'baseline_direction_agrees':bool(a.point_direction_agrees),
                'revised_direction_agrees':bool(b.point_direction_agrees),
                'direction_comparison_meaningful':not endpoint.startswith('cell_')})
    out={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'descriptive_sealed_temporal_holdout_pilot',
        'input_hashes':{p.name:sha(p) for p in [R/'endpoint_comparison.csv',R/'reference_analyses.json',R/'nonestimable.json']},
        'primary_endpoints':primary,'variants':summaries,'paired_changes':paired,
        'nonestimable':read(R/'nonestimable.json'),
        'limits':['Same NHANES study, new locally reserved period; not a distinct external cohort.',
                  'Three seeds measure generator randomness, not evidence or transport uncertainty.',
                  'Source/model difference pilot; not a matched-information ordinary-Agent comparison.',
                  'No improvement threshold, winner selection or post-target tuning.',
                  'Positive cell means/proportions are not directional scientific successes.',
                  'Paired absolute error is secondary diagnostics, not required individual-data identity.']}
    with (R/'pilot_summary.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,allow_nan=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.2))
    for ax,endpoint,title in zip(axes,primary,['Adjusted age association','BMI curvature']):
        ref=reference[endpoint]
        ax.axvline(0,color='#b9bec7',lw=1)
        ax.errorbar(ref['estimate'],2,xerr=[[ref['estimate']-ref['ci_low']],[ref['ci_high']-ref['estimate']]],
                    fmt='s',color='#202b3a',capsize=4,label='Real data: survey 95% CI')
        for level,(name,color) in enumerate([('baseline','#6a7c93'),('joint_evidence','#127f70')]):
            ss=summaries[name][endpoint]
            values=list(ss['generated_estimates'].values())
            ax.scatter(values,np.full(len(values),1-level),color=color,s=45,alpha=.85)
        ax.set_yticks([2,1,0],['Real reference','Baseline: 3 draws','Joint evidence: 3 draws'])
        ax.set_title(title);ax.set_xlabel('Log-TG scale');ax.set_ylim(-.5,2.5)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Frozen generator comparison on a reserved public-data period',fontsize=13)
    fig.text(.02,.01,'Dots: fixed-model generator draws, not confidence intervals. BMI curvature is a quadratic second difference.',fontsize=8)
    fig.tight_layout(rect=[0,.06,1,.94])
    fig.savefig(R/'primary_conclusions.png',dpi=180)
    fig.savefig(R/'primary_conclusions.svg')
    print(json.dumps({name:{ep:{k:summaries[name][ep][k] for k in ['generated_mean','generated_min','generated_max','direction_agrees_count','all_seed_points_inside_reference_CI']} for ep in primary} for name in intent['variants']},indent=2))

if __name__=='__main__':main()

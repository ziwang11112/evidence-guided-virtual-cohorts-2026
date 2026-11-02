"""Re-render existing aggregate results only; no participant reads or model fits."""
from __future__ import annotations
import csv
import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
INPUTS = {
    'm17': ('work/m17b_whole_cohort_2026-10-31/custodian/results/evaluation.json',
            'e7326021f3419a0a57360fbc4a4ccd4b5e78286122bb4021b77141a259417d16'),
    'ens': ('work/autonomous_research_cycle2_2026-10-31/analysis/results/aggregate.json',
            '58ff17bdebec666aa270d68d92fcfadedcbd3bc7878bd19acfd2d66ee407e3ed'),
    'chns': ('work/chns_admission_2026-11-01/f2/evaluation_results/REPORT.json',
             '55c307e230d1d59eded5d5af0dd15b0ca376d8a2b045cb00621c5b0e5409794f'),
    'chns_inventory': ('work/chns_admission_2026-11-01/f2/FINAL_INVENTORY.json',
                       'ec117431c6297146cbcbe7f34027d2e4af3c3dadda40116cd8eacade33759aea'),
}
ENDPOINTS = {
    'm17': [
        ('adjusted_bmi', 'Adjusted BMI', 'Urate: mg/dL per 5 kg/m²'),
        ('adjusted_age', 'Adjusted age', 'Urate: mg/dL per 10 years'),
        ('adjusted_sex', 'Female contrast', 'Urate: mg/dL'),
        ('bmi_curvature', 'BMI curvature', 'Urate: mg/dL, fixed second difference'),
        ('bmi_sex_interaction', 'BMI × sex', 'Urate: mg/dL slope difference per 5 kg/m²'),
        ('male_bmi', 'Male BMI', 'Urate: mg/dL per 5 kg/m²'),
        ('female_bmi', 'Female BMI', 'Urate: mg/dL per 5 kg/m²'),
        ('reverse_urate', 'Reverse urate projection', 'BMI: kg/m² per mg/dL urate'),
    ],
    'ens': [
        ('Q1_age10', 'Q1 · Age, full model', 'HbA1c: percentage points per 10 years'),
        ('Q2_bmi5', 'Q2 · BMI, without glucose', 'HbA1c: percentage points per 5 kg/m²'),
        ('Q3_bmi5', 'Q3 · BMI, with glucose', 'HbA1c: percentage points per 5 kg/m²'),
        ('Q2_minus_Q3_bmi5', 'Q2 − Q3 · Coefficient change', 'HbA1c: percentage points per 5 kg/m²'),
    ],
    'chns': [
        ('E1', 'E1 · BMI adjusted for age/sex', 'HbA1c: percentage points per kg/m²'),
        ('E2', 'E2 · Glucose adjusted for age/sex', 'HbA1c: percentage points per mmol/L'),
        ('E3', 'E3 · Age, full model', 'HbA1c: percentage points per year'),
    ],
}
META = {
    'm17': dict(name='NHANES · M17-B · urate | historical implementation', n=320, rows_per_table=320,
                builders=['b1','b2'], labels=['B1','B2'], stage='final',
                seeds=[17111,17112,17113],
                uncertainty='HC3 95% reference intervals',
                detail='8 locked analyses; selected quota sample; all 6 unique virtual tables'),
    'ens': dict(name='ENSANUT · cycle 2 · glycemia | historical implementation', n=6931, rows_per_table=2000,
                builders=['construction_1','construction_2'], labels=['A','B'], stage='final',
                seeds=[18203,18211,18223],
                uncertainty='Empirical stability bands — not confidence intervals',
                detail='3 primary questions + prespecified coefficient-change companion; all 6 unique tables'),
    'chns': dict(name='CHNS · F2 · glycemia | semantic-feedback v1', n=6631, rows_per_table=3000,
                builders=['C1','C2'], labels=['C1','C2'], stage='revised',
                seeds=[1701,1702,1703],
                uncertainty='Community-clustered CR1/t 95% reference intervals',
                detail='3 primary associations; selected complete cases; all 6 unique virtual tables'),
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_inputs():
    found={}
    for key,(relative,expected) in INPUTS.items():
        path=PROJECT/relative
        assert digest(path)==expected, f'Frozen aggregate changed: {relative}'
        found[key]=json.loads(path.read_text(encoding='utf-8-sig'))
    return found

def extract(data):
    rows=[]
    inventories={}
    for case,meta in META.items():
        source=data[case]
        if case=='m17':
            raw=source['generated']
            entries=[dict(builder=e['builder'],stage=e['stage'],seed=e['seed'],sha=e['sha256'],
                          status=e['status'],n=e['n'],values=e['endpoints']) for e in raw]
        elif case=='ens':
            raw=source['scheduled_results']
            entries=[dict(builder=e['builder'],stage=e['stage'],seed=e['seed'],sha=e['output_sha256'],
                          status=e['status'],n=e['analysis']['n'],values=e['analysis']['questions']) for e in raw]
        else:
            hashes={(e['construction'],e['stage'],e['seed']):e['generated_sha256']
                    for e in data['chns_inventory']['slots']}
            entries=[dict(builder=e['construction'],stage=e['stage'],seed=e['seed'],
                          sha=hashes[(e['construction'],e['stage'],e['seed'])],status=e['status'],
                          n=e['analysis']['n'],values=e['analysis']['estimands']) for e in source['slots']]
        assert len(entries)==12 and all(e['status'] in ['ok','success'] for e in entries)
        assert len({(e['builder'],e['stage'],e['seed']) for e in entries})==12
        final=[e for e in entries if e['stage']==meta['stage']]
        initial={(e['builder'],e['seed']):e for e in entries if e['stage']=='initial'}
        assert len(final)==6 and len(initial)==6
        assert {e['builder'] for e in final}==set(meta['builders'])
        assert len({e['sha'] for e in final})==6
        assert len({e['sha'] for e in entries})==6
        for e in final:
            old=initial[e['builder'],e['seed']]
            assert e['sha']==old['sha'] and e['values']==old['values'], 'Retention mismatch'
            assert e['n']==meta['rows_per_table']
        for builder in meta['builders']:
            assert sorted(e['seed'] for e in final if e['builder']==builder)==meta['seeds']
        assert source['reference']['n']==meta['n']
        inventories[case]=[dict(builder=e['builder'],seed=e['seed'],sha256=e['sha'],rows=e['n'])
                           for e in sorted(final,key=lambda x:(x['builder'],x['seed']))]
        for endpoint,label,unit in ENDPOINTS[case]:
            if case=='m17':
                ref=source['reference']['endpoints'][endpoint]
                estimate,lower,upper=ref['estimate'],ref['ci95_lo'],ref['ci95_hi']
            elif case=='ens':
                estimate=source['reference']['questions'][endpoint]
                band=source['reference_stability']['bands'][endpoint]
                lower,upper=band['lower'],band['upper']
            else:
                ref=source['reference']['estimands'][endpoint]
                assert ref['status']=='computed' and ref['interval']['status']=='available'
                estimate,lower,upper=ref['coefficient'],ref['interval']['lower'],ref['interval']['upper']
            for e in sorted(final,key=lambda x:(x['builder'],x['seed'])):
                entry=e['values'][endpoint]
                value=entry['estimate'] if case=='m17' else entry['coefficient'] if case=='chns' else entry
                assert all(math.isfinite(x) for x in [value,estimate,lower,upper])
                rows.append(dict(case=case,endpoint=endpoint,label=label,unit=unit,builder=e['builder'],
                                 seed=e['seed'],generated=value,reference=estimate,reference_lower=lower,
                                 reference_upper=upper,reference_band=meta['uncertainty'],
                                 reference_n=meta['n'],generated_rows=e['n'],output_sha256=e['sha']))
    assert len(rows)==90 and len({(r['case'],r['endpoint']) for r in rows})==15
    assert len({r['output_sha256'] for r in rows})==18
    return rows,inventories

def plot_case(case,rows,output_dir=HERE):
    meta=META[case]
    specs=ENDPOINTS[case]
    ncols=4 if case!='chns' else 3
    nrows=math.ceil(len(specs)/ncols)
    fig,axes=plt.subplots(nrows,ncols,figsize=(17,3.6*nrows+2),squeeze=False)
    palette=['#167B83','#C66B37']
    for ax,(endpoint,label,unit) in zip(axes.flat,specs):
        subset=[r for r in rows if r['case']==case and r['endpoint']==endpoint]
        ref=subset[0]
        ax.axvspan(ref['reference_lower'],ref['reference_upper'],color='#E4E8ED',zorder=0)
        ax.axvline(ref['reference'],color='#293341',lw=1.5,zorder=1)
        ax.axvline(0,color='#929AA6',lw=.7,ls=':',zorder=0)
        for i,builder in enumerate(meta['builders']):
            points=sorted([r for r in subset if r['builder']==builder],key=lambda r:r['seed'])
            assert len(points)==3
            for j,point in enumerate(points):
                ax.scatter(point['generated'],1-i+(j-1)*.13,s=42,
                           color=palette[i],marker=['o','s','^'][j],zorder=3,
                           edgecolors='white',linewidths=.5)
        ax.set_ylim(-.45,1.45)
        ax.set_yticks([1,0],meta['labels'])
        ax.set_title(label,loc='left',fontsize=12,fontweight='bold',pad=12)
        ax.set_xlabel(unit,fontsize=9,labelpad=8)
        ax.tick_params(labelsize=10)
        ax.ticklabel_format(style='plain',axis='x',useOffset=False)
        ax.locator_params(axis='x',nbins=4)
        ax.grid(axis='x',color='#EEF0F3',linewidth=.7,zorder=0)
        ax.spines[['top','right','left']].set_visible(False)
        ax.spines['bottom'].set_color('#C6CDD5')
        ax.tick_params(axis='y',length=0)
    for ax in list(axes.flat)[len(specs):]: ax.axis('off')
    fig.suptitle(meta['name'],x=.035,y=.97,ha='left',fontsize=21,fontweight='bold',color='#223247')
    fig.text(.035,.907 if nrows==2 else .865,
             f"No individual input  |  reference n = {meta['n']:,}  |  {meta['detail']}",
             fontsize=10,color='#526173')
    handles=[Line2D([0],[0],color='#293341',lw=1.5,label='Measured-reference estimate'),
             Patch(facecolor='#E4E8ED',label=meta['uncertainty'])]
    handles += [Line2D([0],[0],marker=m,color='none',markerfacecolor='#667384',markersize=6,
                       label=f"Seed {meta['seeds'][i]}") for i,m in enumerate(['o','s','^'])]
    fig.legend(handles=handles,loc='lower left',bbox_to_anchor=(.03,.043),ncol=5,frameon=False,fontsize=9)
    fig.text(.035,.024,'The same virtual table was used for all displayed analyses. Seed variation is not evidence uncertainty; band membership is not equivalence.',fontsize=9,color='#526173')
    fig.subplots_adjust(left=.055,right=.98,top=.83 if nrows==2 else .72,bottom=.19 if nrows==2 else .29,wspace=.34,hspace=.82)
    for extension in ['png','svg']:
        fig.savefig(output_dir/f'{case}_analytical_reuse.{extension}',dpi=180,facecolor='white')
    plt.close(fig)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replot',action='store_true',help='Render only the published aggregate points; no original workspace needed.')
    parser.add_argument('--output-dir',type=Path,help='Replot destination; defaults to the adjacent preview directory.')
    args=parser.parse_args()
    if args.replot:
        manifest=json.loads((HERE/'ATLAS_MANIFEST.json').read_text(encoding='utf-8'))
        point_path=HERE/'analytical_reuse_points.json'
        assert digest(point_path)==manifest['outputs'][point_path.name], 'Aggregate points changed'
        rows=json.loads(point_path.read_text(encoding='utf-8'))
        assert len(rows)==90 and len({r['output_sha256'] for r in rows})==18
        output_dir=(args.output_dir or HERE/'preview').resolve()
        assert output_dir!=HERE, 'Replot into a separate directory to preserve the audited release'
        output_dir.mkdir(parents=True,exist_ok=True)
        for case in META: plot_case(case,rows,output_dir)
        print('Replotted all 3 case panels from the released 90 aggregate points.')
        return
    if args.output_dir:
        parser.error('--output-dir requires --replot')
    data=load_inputs()
    rows,inventory=extract(data)
    with (HERE/'analytical_reuse_points.csv').open('w',encoding='utf-8',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (HERE/'analytical_reuse_points.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for case in META: plot_case(case,rows)
    assert all(digest(PROJECT/relative)==expected for relative,expected in INPUTS.values())
    outputs=['analytical_reuse_points.csv','analytical_reuse_points.json']+[f'{c}_analytical_reuse.{e}' for c in META for e in ['png','svg']]
    manifest={
        'scope':'retrospective re-render of frozen aggregates; no new scientific experiment',
        'input_sha256':{relative:h for relative,h in INPUTS.values()},
        'unique_tables':18,'scheduled_initial_final_labels':36,'constructors':6,'cases':3,
        'case_specific_display_quantities':15,'generated_estimates':90,
        'virtual_rows':sum(e['rows'] for values in inventory.values() for e in values),
        'reference_case_observations':sum(m['n'] for m in META.values()),
        'retention_verified':True,'pooled_effect_or_accuracy_score':None,
        'new_model_fits':0,'new_generations':0,'participant_files_read':False,
        'inventory':inventory,'method_versions_differ':True,
        'outputs':{name:digest(HERE/name) for name in outputs},
        'script_sha256':digest(Path(__file__)),
    }
    assert manifest['virtual_rows']==31920 and manifest['reference_case_observations']==13882
    (HERE/'ATLAS_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Rendered 3 complete case panels: 18 unique tables, 15 quantities, 90 existing generated estimates; no new science.')

if __name__=='__main__': main()

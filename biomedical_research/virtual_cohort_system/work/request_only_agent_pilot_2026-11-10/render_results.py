"""Plot completed aggregate evaluation only; never imports pilot/runtime code.

python render_results.py --evaluation-complete-confirmed-by-root
The only scientific/cost input read is this unit's completed EVALUATION.json.
No candidate program, generated table, reference file, API or credential is read.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARMS = [('ordinary','Ordinary','#2474B5'),('workflow','Workflow','#C56A21')]
CASES = ['PNS','lipids']
PRIMARY = {
    'PNS':[('bmi_sbp','BMI–SBP association'),('bmi_dbp','BMI–DBP association'),
           ('residual_correlation','SBP–DBP residual correlation')],
    'lipids':[('K02-HDL-BMI','BMI–HDL association'),('K02-TC-BMI','BMI–TC association'),
              ('K02-LIPID-RESIDUAL','TC–HDL residual correlation')],
}
SECONDARY = {
    'PNS':[('sbp.sd_population','SBP marginal SD'),('dbp.sd_population','DBP marginal SD'),
           ('sbp_below_dbp_fraction','SBP < DBP fraction')],
    'lipids':[('total_cholesterol.sd_sample','TC marginal SD'),('hdl_cholesterol.sd_sample','HDL marginal SD'),
              ('hdl_above_total_fraction','HDL > TC fraction')],
}
MARKERS = ['o','s','^','v','P','X']


def finite(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)


def number(x,digits=4):
    return format(x,f'.{digits}g') if finite(x) else 'unavailable'


def money(x):
    return f'${x:.4f}' if finite(x) else 'unavailable'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def validate(payload):
    summaries=payload['summaries']
    episodes=payload['episodes']
    slots=payload['slots']
    assert isinstance(summaries,list) and isinstance(episodes,list) and isinstance(slots,list)
    assert len(episodes)==4 and len(slots)==12, 'Expected all four closed episodes and twelve final slots'
    assert len({x['episode_id'] for x in episodes})==4
    assert len({(x['episode_id'],x['seed']) for x in slots})==12
    assert {x['status'] for x in slots}<={'success','failed','unavailable'}
    for case in CASES:
        for arm,_,_ in ARMS:
            rows=[x for x in summaries if x['case_id']==case and x['arm']==arm]
            assert len({x['episode_id'] for x in rows})==1, 'One initial constructor per case/arm required'
            for key,_ in PRIMARY[case]+SECONDARY[case]:
                entries=[x for x in rows if x['analysis_id']==key]
                assert len(entries)==1, 'Missing or duplicate endpoint summary'
                row=entries[0]
                values=row['values']
                assert len(values)==3 and len({v['seed'] for v in values})==3
                good=[v['value'] for v in values if finite(v.get('value'))]
                assert len(good)==row['available_seeds']
                for v in values:
                    assert v.get('value') is None or finite(v['value'])
                    assert v.get('value') is None or v['status']=='success'
                if good:
                    assert math.isclose(sum(good)/len(good),row['mean'],rel_tol=1e-12,abs_tol=1e-12)
                    assert min(good)==row['minimum'] and max(good)==row['maximum']
                else:
                    assert row['mean'] is None and row['minimum'] is None and row['maximum'] is None
    return {(x['case_id'],x['arm'],x['analysis_id']):x for x in summaries}


def interval(reference):
    uncertainty=reference.get('uncertainty') or {}
    low,high=uncertainty.get('lower'),uncertainty.get('upper')
    if uncertainty.get('status')=='available' and finite(low) and finite(high) and low<=high:
        return low,high
    return None


def interval_name(reference):
    u=reference.get('uncertainty') or {}
    if not interval(reference):
        return 'interval unavailable'
    kind=str(u.get('kind','')).lower()
    if 'hc3' in kind:
        level=u.get('nominal_level')
        prefix=f'{level*100:g}% ' if finite(level) else ''
        return prefix+'HC3 sensitivity interval'
    if 'resampl' in kind or 'bootstrap' in kind:
        return 'row-resampling stability range'
    return 'supplied reference interval'


def make_figure(index,endpoints,outcomes,output,stem,title):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator

    seeds=sorted({v['seed'] for row in index.values() for v in row['values']})
    seed_markers={s:MARKERS[i%len(MARKERS)] for i,s in enumerate(seeds)}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,
                         'axes.labelsize':10,'svg.fonttype':'none','savefig.facecolor':'white'})
    fig,axes=plt.subplots(2,3,figsize=(16.8,9.2))
    fig.subplots_adjust(left=.115,right=.972,bottom=.17,top=.83,wspace=.46,hspace=.58)
    fig.suptitle(title,x=.065,y=.969,ha='left',fontsize=21,fontweight='bold',color='#192B42')
    fig.text(.065,.921,'Two cases · one fresh constructor per arm and case · three independent final evaluation seeds',
             fontsize=11,color='#516070')
    pns_outcomes=[o for o in outcomes.values() if o['episode_id'].startswith('PNS_')]
    if pns_outcomes and all(o['status']=='input_byte_limit' and not o.get('selected_candidate') for o in pns_outcomes):
        fig.text(.065,.884,'PNS: neither arm delivered a final generator before reaching the input-byte limit; no generated estimates are plotted.',
                 fontsize=10.5,color='#6A596F')
    panel_metadata=[]
    for r,case in enumerate(CASES):
        for c,(key,label) in enumerate(endpoints[case]):
            ax=axes[r,c]
            rows=[index[(case,arm,key)] for arm,_,_ in ARMS]
            reference=rows[0]['reference']
            if reference!=rows[1]['reference']:
                raise ValueError('Arms have different reference metadata')
            bounds=[]
            labels=[]
            for row,(arm,arm_label,color),y in zip(rows,ARMS,[2,1]):
                good=[v for v in row['values'] if finite(v.get('value'))]
                labels.append(f'{arm_label} ({len(good)}/3)')
                values=[v['value'] for v in good]
                bounds.extend(values)
                if values:
                    ax.plot([min(values),max(values)],[y,y],color=color,alpha=.3,lw=5,
                            solid_capstyle='round',zorder=2)
                    for v in good:
                        k=seeds.index(v['seed'])
                        jitter=(k-(len(seeds)-1)/2)*.055
                        ax.scatter(v['value'],y+jitter,marker=seed_markers[v['seed']],s=51,
                                   facecolors=color,edgecolors='white',linewidths=.7,zorder=4,clip_on=False)
                    text=f'mean {number(row["mean"])}; range {number(min(values))}–{number(max(values))}'
                else:
                    outcome=outcomes[row['episode_id']]
                    if outcome['status']=='input_byte_limit' and not outcome.get('selected_candidate'):
                        text='No final generator delivered\nInput-byte limit reached'
                    else:
                        text='unavailable; no successful estimate'
                ax.text(0,y-.26,text,transform=ax.get_yaxis_transform(),fontsize=8.3,color='#516070')
            value=reference.get('value')
            supplied=interval(reference)
            if finite(value):
                bounds.append(value)
                if supplied:
                    bounds.extend(supplied)
                    ax.plot(supplied,[0,0],color='#3C4651',lw=1.6,zorder=2)
                    ax.vlines(supplied,-.07,.07,color='#3C4651',lw=1.1)
                ax.scatter(value,0,marker='D',s=48,facecolors='#202A35',edgecolors='white',linewidths=.6,zorder=4,clip_on=False)
            ref_text='reference '+number(value)+' · '+interval_name(reference)
            ax.text(0,-.28,ref_text,transform=ax.get_yaxis_transform(),fontsize=8.1,color='#516070')
            labels.append('Reference')
            ax.set_yticks([2,1,0],labels)
            ax.set_ylim(-.52,2.4)
            ax.tick_params(axis='y',length=0,pad=8)
            ax.grid(axis='x',color='#DDE3E9',linewidth=.7,zorder=0)
            for spine in ['top','right','left']:
                ax.spines[spine].set_visible(False)
            ax.spines['bottom'].set_color('#B2BDC8')
            ax.set_title(('PNS' if case=='PNS' else 'Lipids')+' | '+label,loc='left',pad=16,fontweight='bold')
            unit=rows[0]['unit']
            if unit=='1':unit='Pearson r' if 'correlation' in label else 'Fraction of rows'
            ax.set_xlabel(unit,labelpad=8)
            ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
            if bounds:
                lo,hi=min(bounds),max(bounds)
                pad=(hi-lo)*.14 if hi>lo else max(abs(lo)*.15,.1)
                if 'fraction' in key:
                    ax.set_xlim(0,max(hi*1.14,.01 if hi==0 else .0001))
                else:
                    ax.set_xlim(lo-pad,hi+pad)
                if lo<0<hi:
                    ax.axvline(0,color='#A1ABB5',ls=':',lw=.9,zorder=1)
            else:
                ax.set_xlim(0,1)
                ax.set_xticks([])
            panel_metadata.append({'case_id':case,'analysis_id':key,'unit':rows[0]['unit'],
                'reference_interval_label':interval_name(reference),
                'available_seeds':{row['arm']:row['available_seeds'] for row in rows}})
    seed_handles=[Line2D([],[],marker=seed_markers[s],linestyle='None',markerfacecolor='#657080',
                         markeredgecolor='white',markersize=7,label=f'Seed {s}') for s in seeds]
    fig.legend(handles=seed_handles,loc='lower left',bbox_to_anchor=(.059,.082),ncol=len(seeds),frameon=False,fontsize=10)
    fig.text(.065,.061,'Colored bars: seed minimum–maximum, not confidence intervals. Black diamonds: stored reference estimates.',
             fontsize=10,color='#516070')
    fig.text(.065,.033,'References were previously exposed at project level. This descriptive pilot does not establish arm superiority or transport validity.',
             fontsize=9.5,color='#516070')
    files=[]
    for extension in ['png','svg','pdf']:
        path=output/(stem+'.'+extension)
        fig.savefig(path,dpi=190 if extension=='png' else None)
        files.append(path)
    plt.close(fig)
    return files,panel_metadata


def escape(value):
    return html.escape(str(value),quote=True)


def table(headers,rows):
    return '<table><thead><tr>'+''.join('<th>'+escape(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join('<td>'+escape(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'


def render_html(payload,index,output,source_hash):
    mapping={x['episode_id']:(x['case_id'],x['arm']) for x in payload['summaries']}
    episodes={x['episode_id']:x for x in payload['episodes']}
    episode_rows=[]
    arm_rows=[]
    for case in CASES:
        for arm,label,color in ARMS:
            eid=next(e for e,pair in mapping.items() if pair==(case,arm))
            outcome=episodes[eid]
            slots=[s for s in payload['slots'] if s['episode_id']==eid]
            counts=Counter(s['status'] for s in slots)
            usage=outcome.get('tool_usage') or {}
            episode_rows.append([eid,'selected' if outcome.get('selected_candidate') else 'none selected',outcome['status'],
                f'{counts["success"]}/{len(slots)}',counts['failed'],counts['unavailable'],outcome['calls_reserved'],
                usage.get('executions','unavailable'),money(outcome['known_tariff_cost_usd']),
                money(outcome['accounted_usd']),outcome.get('unknown_usage_calls','unavailable')])
    for arm,label,color in ARMS:
        ids=[e for e,pair in mapping.items() if pair[1]==arm]
        outcomes=[episodes[e] for e in ids]
        slots=[s for s in payload['slots'] if s['episode_id'] in ids]
        counts=Counter(s['status'] for s in slots)
        arm_rows.append([label,f'{sum(bool(o.get("selected_candidate")) for o in outcomes)}/{len(outcomes)}',
            f'{counts["success"]}/{len(slots)}',counts['failed'],counts['unavailable'],
            sum(o['calls_reserved'] for o in outcomes),money(sum(o['known_tariff_cost_usd'] for o in outcomes)),
            money(sum(o['accounted_usd'] for o in outcomes)),sum(o.get('unknown_usage_calls',0) for o in outcomes)])
    main_rows=[]
    reference_notes=[]
    for case in CASES:
        for key,label in PRIMARY[case]:
            for arm,arm_label,_ in ARMS:
                row=index[(case,arm,key)]
                seed_text='; '.join(f'{v["seed"]}: {number(v.get("value"))}' for v in row['values'])
                main_rows.append([case,label,arm_label,row['unit'],seed_text,number(row['mean']),
                    number(row['reference'].get('value')),number(row.get('mean_absolute_reference_difference'))])
            ref=index[(case,'ordinary',key)]['reference']
            reference_notes.append('<details><summary>'+escape(case+' / '+label+' — '+interval_name(ref))+
                '</summary><pre>'+escape(json.dumps(ref.get('uncertainty'),ensure_ascii=False,indent=2))+'</pre></details>')
    cost_note='Known cost is a usage-derived tariff estimate, not an invoice. Accounted cost retains conservative reservations for unknown usage; it is not additional spending.'
    content='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Request-only pilot: scientific aggregates</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><style>
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#243346;background:#f6f8fb;margin:0;padding:36px}
main{max-width:1480px;margin:auto}h1{font-size:30px;margin-bottom:8px}h2{font-size:22px;margin-top:34px}
p{max-width:1100px;line-height:1.6;color:#536274}.note{border-left:4px solid #8d70ad;padding:12px 18px;background:#eee9f4}
img{width:100%;background:white;border:1px solid #dbe2ea;border-radius:9px}table{border-collapse:collapse;background:white;min-width:100%;font-size:13px}
th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid #e0e6ec}th{background:#e8eef5;white-space:nowrap}
.scroll{overflow-x:auto;margin:16px 0}a{color:#226eaa}details{margin:8px 0;padding:10px;background:white}pre{white-space:pre-wrap;font-size:12px}
.hash{font:12px ui-monospace,monospace;overflow-wrap:anywhere}footer{margin-top:30px;color:#657183;font-size:12px}
</style><main><h1>Request-only pilot: scientific aggregates</h1>
<p>Ordinary and workflow policies began with the same case request and no prepared papers or scientific parameter values. Each case has one constructor per policy. Final seed points are repeated draws from each selected law, not independent authoring replications.</p>
<p class="note">Read each endpoint in its own units. The figures and tables do not combine endpoint errors into a score or support a superiority claim. Seed ranges are simulation variation, not confidence intervals or transport uncertainty.</p>
<h2>Six primary estimands</h2><img src="PRIMARY_ENDPOINTS.svg" alt="Six endpoint panels comparing ordinary and workflow seed estimates with stored references">
<p><a href="PRIMARY_ENDPOINTS.png">PNG</a> · <a href="PRIMARY_ENDPOINTS.pdf">PDF</a> · <a href="PRIMARY_ENDPOINTS.svg">SVG</a></p>
<div class="scroll">'''
    content+=table(['Case','Endpoint','Arm','Unit','Individual seeds','Seed mean','Reference','Mean absolute reference difference'],main_rows)+'</div>'
    content+='<h2>Reference uncertainty</h2><p>The original stored uncertainty definitions are reproduced below. PNS row-resampling stability and lipid HC3 sensitivity intervals have different interpretations. Missing uncertainty stays unavailable.</p>'+''.join(reference_notes)
    content+='<h2>Secondary dispersion and component diagnostics</h2><img src="SECONDARY_DIAGNOSTICS.svg" alt="Marginal standard deviations and component violations across seeds and available references">'
    content+='<p><a href="SECONDARY_DIAGNOSTICS.png">PNG</a> · <a href="SECONDARY_DIAGNOSTICS.pdf">PDF</a> · <a href="SECONDARY_DIAGNOSTICS.svg">SVG</a>. Component diagnostics are descriptive; no additional filtering or clinical acceptance cutoff is introduced.</p>'
    content+='<h2>Delivery and cost by policy</h2><p>'+escape(cost_note)+'</p><div class="scroll">'
    content+=table(['Policy','Selected / episodes','Successful / final slots','Failed slots','Unavailable slots','Model calls reserved','Known tariff USD','Accounted USD','Unknown-usage calls'],arm_rows)+'</div>'
    content+='<h2>Episode detail</h2><div class="scroll">'+table(['Episode','Candidate delivery','Stop status','Successful / slots','Failed','Unavailable','Model calls','Diagnostic executions','Known tariff USD','Accounted USD','Unknown-usage calls'],episode_rows)+'</div>'
    content+='<h2>Limitations recorded by the evaluator</h2><ul>'+''.join('<li>'+escape(x)+'</li>' for x in payload.get('limitations',[]))+'</ul>'
    content+='<footer>Input: completed EVALUATION.json only. No raw/generated row files or candidate programs were loaded.<p class="hash">Evaluation SHA256: '+source_hash+'</p></footer></main></html>'
    path=output/'SCIENTIFIC_AGGREGATES.html'
    path.write_text(content,encoding='utf-8')
    return path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--evaluation-complete-confirmed-by-root',action='store_true',required=True)
    parser.add_argument('--replace-own-derived-artifacts',action='store_true')
    args=parser.parse_args()
    source=ROOT/'EVALUATION.json'
    if not source.is_file():
        raise SystemExit('Completed EVALUATION.json does not exist; no figures produced.')
    raw=source.read_bytes()
    payload=json.loads(raw)
    index=validate(payload)
    output=ROOT/'figures'
    output.mkdir(exist_ok=True)
    if any(output.iterdir()):
        manifest=output/'FIGURE_MANIFEST.json'
        if not args.replace_own_derived_artifacts or not manifest.is_file():
            raise SystemExit('Existing figures require explicit --replace-own-derived-artifacts and their manifest.')
        previous=json.loads(manifest.read_text(encoding='utf-8'))
        if previous['evaluation_sha256']!=digest(raw):
            raise SystemExit('Evaluation changed; refusing to replace existing derived artifacts.')
        if {p.name for p in output.iterdir()}!=set(previous['files'])|{'FIGURE_MANIFEST.json'}:
            raise SystemExit('Figure directory contains unrecognized files; refusing replacement.')
        if any(digest((output/name).read_bytes())!=value for name,value in previous['files'].items()):
            raise SystemExit('Prior derived file changed; refusing replacement.')
    outcomes={o['episode_id']:o for o in payload['episodes']}
    primary,primary_meta=make_figure(index,PRIMARY,outcomes,output,'PRIMARY_ENDPOINTS','Final generated-law scientific estimands')
    secondary,secondary_meta=make_figure(index,SECONDARY,outcomes,output,'SECONDARY_DIAGNOSTICS','Dispersion and component diagnostics')
    page=render_html(payload,index,output,digest(raw))
    files=primary+secondary+[page]
    metadata={'created_utc':datetime.now(timezone.utc).isoformat(),'input':'EVALUATION.json',
      'evaluation_sha256':digest(raw),'data_reads':'completed aggregate evaluation only',
      'primary_panels':primary_meta,'secondary_panels':secondary_meta,
      'seed_ranges_are_confidence_intervals':False,'aggregate_performance_score':None,
      'files':{p.name:digest(p.read_bytes()) for p in files}}
    (output/'FIGURE_MANIFEST.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'rendered','evaluation_sha256':digest(raw),'files':[p.name for p in files]}))


if __name__=='__main__':
    main()

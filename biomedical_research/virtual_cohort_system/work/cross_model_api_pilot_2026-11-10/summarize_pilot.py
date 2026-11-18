"""Render captured API costs and already-frozen endpoint summaries; no model calls."""
from pathlib import Path
import json
import hashlib
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

U=Path(__file__).resolve().parent
ORDER=['OA_ASTRA','DS_PRO','CL_FABLE','GE_CARBON','OA_SOL']
NAMES=['GPT-6\nAstra','DeepSeek\nV4 Pro','Claude\nFable 5.2','Gemini 4\nCarbon','GPT-6.1\nSol']
COLORS=['#3057A5','#9A6532','#A24E6D','#7762AC','#4E8BBC']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)

def main():
    import execute_pilot as host
    host.evaluation_gate()
    report=read(U/'EVALUATION.json')
    done=read(U/'EVALUATION_COMPLETED.json')
    assert done['files']['EVALUATION.json']==sha(U/'EVALUATION.json')
    plan=read(U/'RUN_PLAN.json')
    cost=[]
    for folder in sorted((U/'calls').iterdir()):
        r=read(folder/'receipt.json') if (folder/'receipt.json').exists() else {}
        reservation=read(folder/'reservation.json')
        cost.append({'call_id':folder.name,'provider':reservation['provider'],'config':reservation['config'],
            'requested_model':r.get('requested_model'),'returned_model':r.get('returned_model'),
            'status':r.get('status','interrupted'),'artifact_status':r.get('artifact_status'),
            'usage':r.get('usage'),'usage_raw':r.get('usage_raw'),
            'tariff_estimate_usd':r.get('tariff_cost_usd'),
            'reservation_usd':reservation['reserved_usd'],
            'elapsed_seconds':r.get('elapsed_seconds'),'receipt_sha256':sha(folder/'receipt.json') if r else None})
    totals={}
    for provider in plan['provider_caps_usd']:
        rows=[r for r in cost if r['provider']==provider]
        totals[provider]={'calls':len(rows),'usage_cost_known_calls':sum(r['tariff_estimate_usd'] is not None for r in rows),
            'tariff_estimate_usd':sum(r['tariff_estimate_usd'] or 0 for r in rows),
            'unknown_usage_reserved_usd':sum(r['reservation_usd'] for r in rows if r['tariff_estimate_usd'] is None),
            'api_status_counts':dict(Counter(r['status'] for r in rows))}
    write(U/'PILOT_COSTS.json',{'basis':'captured provider usage and frozen published tariffs; not invoice; DeepSeek peak estimate',
        'provider_totals':totals,'known_tariff_total_usd':sum(t['tariff_estimate_usd'] for t in totals.values()),
        'unknown_usage_reserved_usd':sum(t['unknown_usage_reserved_usd'] for t in totals.values()),'calls':cost})
    fig,axes=plt.subplots(2,3,figsize=(14.2,8.0),layout='constrained')
    panels=[('PNS','bmi_sbp','BMI–systolic pressure','mmHg per 5 kg/m²'),
            ('PNS','bmi_dbp','BMI–diastolic pressure','mmHg per 5 kg/m²'),
            ('PNS','residual_correlation','Blood-pressure residual dependence','Pearson r'),
            ('lipids','K02-TC-BMI','BMI–total cholesterol','mg/dL per 5 kg/m²'),
            ('lipids','K02-HDL-BMI','BMI–HDL cholesterol','mg/dL per 5 kg/m²'),
            ('lipids','K02-LIPID-RESIDUAL','Lipid residual dependence','Pearson r')]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    for panel,(ax,(case,endpoint,title,unit)) in enumerate(zip(axes.flat,panels)):
        rows=[r for r in report['construction_summaries'] if r['case_id']==case and r['id']==endpoint]
        assert len(rows)==10
        ref=rows[0]['reference'];unc=ref.get('uncertainty',{})
        if unc.get('status')=='available' and 'lower' in unc and 'upper' in unc:
            ax.axhspan(unc['lower'],unc['upper'],color='#B8BEC8',alpha=.27,zorder=0)
        ax.axhline(ref['value'],color='#232C3A',lw=1.25,ls='--',zorder=1)
        for i,config in enumerate(ORDER):
            chosen=sorted([r for r in rows if r['model_config']==config],key=lambda r:r['context'])
            for offset,row,marker in zip([-.13,.13],chosen,['o','s']):
                if row['seed_mean'] is None:
                    ax.text(i+offset,.96,'0/3',transform=ax.get_xaxis_transform(),ha='center',va='top',rotation=90,fontsize=8,color=COLORS[i])
                    continue
                value=row['seed_mean'];lo,hi=row['seed_range']
                ax.errorbar(i+offset,value,yerr=[[value-lo],[hi-value]],fmt=marker,
                    color=COLORS[i],markersize=6,capsize=3,lw=1.1,zorder=3)
                if row['available_seeds']<3:
                    ax.annotate(str(row['available_seeds'])+'/3',(i+offset,value),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
        ax.set_xticks(range(5),NAMES,fontsize=9)
        ax.set_title(chr(65+panel)+'. '+title,loc='left',fontweight='bold',fontsize=11)
        ax.set_ylabel(unit,fontsize=10)
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.17)
        ax.set_axisbelow(True)
        ax.set_xlim(-.55,4.55)
    fig.suptitle('Scientific analyses of evidence-built virtual cohorts',fontsize=16,fontweight='bold')
    fig.supxlabel('Each circle / square: one construction; point = available-draw mean, whisker = range (3 draws planned; shortfalls labeled n/3).\nDashed line: real-data reference. Gray band: supplied reference interval where available. Developmental comparison.',fontsize=10)
    for suffix in ['png','pdf','svg']:
        path=U/('SCIENTIFIC_RESULTS.'+suffix)
        if path.exists():raise FileExistsError(path)
        fig.savefig(path,dpi=200,bbox_inches='tight')
    plt.close(fig)
    write(U/'SUMMARY_ARTIFACTS.json',{'evaluation_sha256':sha(U/'EVALUATION.json'),
        'files':{name:sha(U/name) for name in ['PILOT_COSTS.json','SCIENTIFIC_RESULTS.png','SCIENTIFIC_RESULTS.pdf','SCIENTIFIC_RESULTS.svg']}})
    print(json.dumps({'provider_totals':totals,'complete_endpoint_slots':report['complete_endpoint_slots']}))

if __name__=='__main__':main()

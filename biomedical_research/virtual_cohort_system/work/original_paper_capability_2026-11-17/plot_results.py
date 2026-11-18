"""Render the complete closed-batch analysis profile; no model/row processing."""
from pathlib import Path
import json, hashlib, html
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
LABELS={'bmi_sbp':'BMI association with SBP','bmi_dbp':'BMI association with DBP','residual_correlation':'SBP–DBP residual dependence',
 'odds_ratio':'Anemia / iron-depletion association','joint_prevalence':'Both markers below threshold','spearman':'Hb–ferritin rank dependence',
 'sbp.sd_population':'SBP dispersion','dbp.sd_population':'DBP dispersion','sbp_below_dbp_fraction':'SBP below DBP',
 'low_hb_fraction':'Low hemoglobin prevalence','low_ferritin_fraction':'Low ferritin prevalence'}
UNITS={'bmi_sbp':'mmHg per 5 kg/m² BMI','bmi_dbp':'mmHg per 5 kg/m² BMI','residual_correlation':'Residual Pearson r',
 'odds_ratio':'Odds ratio (log scale)','joint_prevalence':'Fraction','spearman':'Spearman r',
 'sbp.sd_population':'mmHg (population SD)','dbp.sd_population':'mmHg (population SD)',
 'sbp_below_dbp_fraction':'Fraction','low_hb_fraction':'Fraction','low_ferritin_fraction':'Fraction'}
PRIMARY={'PNS':['bmi_sbp','bmi_dbp','residual_correlation'],'IRON':['odds_ratio','joint_prevalence','spearman']}
DIAGNOSTICS={'PNS':['sbp.sd_population','dbp.sd_population','sbp_below_dbp_fraction'],'IRON':['low_hb_fraction','low_ferritin_fraction']}

def main():
    qa=json.loads((ROOT/'analysis/CLOSEOUT_QA.json').read_text());assert qa['status']=='pass'
    df=pd.read_csv(ROOT/'analysis/author_results.csv');cost=json.loads((ROOT/'analysis/COSTS.json').read_text())
    (ROOT/'figures').mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
    files={}
    for name,groups,title in [('primary_analyses',PRIMARY,'Original papers → Agent-authored cohorts → scientific analyses'),
                              ('diagnostics',DIAGNOSTICS,'Companion diagnostics: dispersion, prevalence and physiological order')]:
        fig,axes=plt.subplots(2,3,figsize=(13.4,8))
        for row,case in enumerate(['PNS','IRON']):
            color='#355DB5' if case=='PNS' else '#8A5BA8'
            for col in range(3):
                ax=axes[row,col]
                if col>=len(groups[case]):ax.axis('off');continue
                key=groups[case][col];g=df[(df.case_id==case)&(df.estimand==key)].sort_values('episode_id')
                assert len(g)==3
                ref=float(g.reference.iloc[0]);ax.axhline(ref,color='#202F43',linestyle='--',linewidth=1.3,label='Measured reference')
                for i,r in enumerate(g.itertuples(),1):
                    if r.available_seeds>0:
                        ax.plot([i,i],[r.seed_min,r.seed_max],color=color,linewidth=2)
                        ax.scatter([i],[r.seed_mean],s=50,color=color,edgecolor='white',linewidth=.7,zorder=4)
                    else:ax.text(i,.06,'unavailable',ha='center',rotation=90,transform=ax.get_xaxis_transform(),fontsize=8)
                if key=='odds_ratio':ax.set_yscale('log')
                ax.set_xticks([1,2,3],['Author 1','Author 2','Author 3']);ax.set_xlim(.6,3.4)
                ax.set_ylabel(UNITS[key]);ax.set_title(case+' · '+LABELS[key]+f'\nMeasured reference: {ref:.3g}',fontsize=10,pad=9)
                ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
                if key=='sbp_below_dbp_fraction' and (g.seed_max==0).all() and ref==0:
                    ax.set_ylim(-.0005,.006);ax.set_yticks([0,.002,.004,.006])
                    ax.text(.5,.52,'No ordering violations\nin 27,000 final BP rows',transform=ax.transAxes,ha='center',va='center',fontsize=10,color='#475569')
        fig.suptitle(title,fontsize=16,y=.99)
        fig.text(.5,.015,'Points: construction means; segments: three fixed-seed ranges, not confidence intervals. Dashed line: measured reference.\nAll scheduled authors are retained. Reference samples were previously exposed to the project.',ha='center',fontsize=9,color='#64748B')
        fig.tight_layout(rect=(0,.065,1,.95))
        for ext in ['png','svg','pdf']:
            path=ROOT/'figures'/f'{name}.{ext}';fig.savefig(path,dpi=180,bbox_inches='tight',facecolor='white')
            files[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        plt.close(fig)
    table=df[['case_id','episode_id','estimand','available_seeds','seed_mean','seed_min','seed_max','reference','mean_discrepancy']].copy()
    table['estimand']=table.estimand.map(LABELS)
    svgs=[]
    for name in ['primary_analyses','diagnostics']:
        s=(ROOT/'figures'/f'{name}.svg').read_text(encoding='utf-8');svgs.append(s[s.index('<svg'):])
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Original-paper capability · KDD</title>
<style>body{font:16px/1.6 system-ui;background:#f5f6fa;color:#182b49;margin:0}main{max-width:1400px;margin:auto;padding:32px 4vw}.card{background:white;padding:24px;border:1px solid #dfe4ed;border-radius:12px;margin:22px 0}h1{font-size:32px;line-height:1.2}.muted{color:#64748b}svg{width:100%;height:auto}table{border-collapse:collapse;font-size:13px;width:100%}th,td{padding:9px;border-bottom:1px solid #dfe4ed;text-align:right;white-space:nowrap}th{background:#edf1fa}td:nth-child(-n+3){text-align:left}.scroll{overflow:auto}a{color:#355db5}.note{border-left:4px solid #8a5ba8;padding-left:16px}</style>
<main><p class="muted">17 November 2026 · Original-paper capability · KDD first paper</p><h1>Can the Agent read a paper and author a useful scientific generator?</h1>
<p>Two existing cases, three fresh constructors per case. Each receives the complete original-paper entry point and scientific request, with optional screened literature search. No curator-written numerical packet or target answer is supplied.</p>
<section class="card"><h2>What to read first</h2><p>Each dot is one Agent-authored model averaged over three final seeds. The dashed line is the existing measured-sample reference. Small differences are encouraging for that particular analysis; they do not certify clinical equivalence or transport.</p>
<p class="note">This is a known-paper reading and modeling test. Source selection remains researcher-provided, and the reference families were already exposed. The source/code audit and full result interpretation accompany the figures.</p></section>'''
    page+=f'<section class="card"><p><b>{qa["successful_slots"]}/18</b> final tables executed; <b>{cost["api_calls"]}</b> model calls; estimated tariff cost <b>${cost["known_tariff_cost_usd"]:.3f}</b>. This is token-tariff accounting, not a billing invoice.</p></section>'
    page+='''<section class="card"><h2>What the experiment found</h2>
<p><b>Blood pressure:</b> all three authors reproduce approximately the adjusted BMI associations: SBP effects 3.40–3.80 versus reference 3.52; DBP effects 2.29–2.40 versus 2.26 mmHg per 5 kg/m². Residual correlation and pressure dispersion remain higher than the sample reference.</p>
<p><b>Iron status:</b> the positive association is retained, but its strength is weaker: odds ratios 6.35–7.14 versus 17.79. Joint prevalence and rank correlation also remain lower. A useful source constraint does not identify the whole target distribution.</p>
<p>No clinical equivalence margin was fitted to these outcomes. The results describe which particular analyses look useful and where discrepancies remain.</p></section>
<section class="card"><h2>What the Agent actually authored</h2>
<p>All three BP authors extracted the original correlation matrix and derived an age/BMI partial covariance. All three iron authors collapsed eight source-table rows into a two-by-two table and distinguished crude from adjusted odds. Each chose supplementary searches, a probability law and numeric assumptions, wrote the generator, inspected one trial and kept its first candidate.</p>
<p>The runner samples the Agent’s program. The coordinator did not supply a numerical evidence card or fill in the scientific relationships. This supports original-paper interpretation and model authorship; it does not test a revision advantage.</p>
<p class="note">One author received a same-target-family search preview with study identity and demographics, then explicitly excluded it. The preview did not include the evaluated effect values. This exposure remains in the audit; screening is not a guarantee of source independence.</p></section>'''
    page+='<section class="card">'+svgs[0]+'</section><section class="card">'+svgs[1]+'</section>'
    page+='<section class="card"><h2>Complete scientific profile</h2><p>Discrepancy is absolute log-OR difference for the odds ratio and absolute native-scale difference for all other endpoints. Seeds are within-construction repetitions.</p><div class="scroll">'+table.to_html(index=False,float_format=lambda x:f'{x:.4f}',border=0)+'</div></section>'
    page+='<p>Read the <a href="../RESULTS.md">full interpretation</a>, <a href="../SOURCE_MODEL_AUDIT.md">source-to-code audit</a>, and <a href="../PROTOCOL.md">frozen protocol</a>.</p></main></html>'
    report=ROOT/'report';report.mkdir(exist_ok=True);(report/'index.html').write_text(page,encoding='utf-8',newline='\n')
    files['report/index.html']=hashlib.sha256((report/'index.html').read_bytes()).hexdigest()
    binding=ROOT/'FIGURE_BINDINGS.json'
    if binding.exists() and not (ROOT/'FIGURE_BINDINGS.initial.json').exists():
        (ROOT/'FIGURE_BINDINGS.initial.json').write_bytes(binding.read_bytes())
    with binding.open('w',encoding='utf-8') as f:json.dump({'source':'analysis/author_results.csv','source_sha256':hashlib.sha256((ROOT/'analysis/author_results.csv').read_bytes()).hexdigest(),'all_primary_panels':6,'all_diagnostic_panels':5,'artifacts':files},f,indent=2)
    print(json.dumps({'primary_panels':6,'diagnostic_panels':5,'author_endpoint_rows':len(df)}))

if __name__=='__main__':main()

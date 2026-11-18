"""Aggregate-only figures and an offline HTML reading report."""
import html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from common import *

NAMES={'bmi':'BMI','total_cholesterol':'Total cholesterol','hdl_cholesterol':'HDL cholesterol'}
CNAMES={'rural_minus_pastoralist':'Rural − pastoralist','urban_minus_pastoralist':'Urban − pastoralist','urban_minus_rural':'Urban − rural'}
BLUE='#355DB5'; PURPLE='#8A5BA8'; GREY='#667085'; INK='#172B4D'

def label(stream):
    if stream in ['R_A','R_B']:return 'Real − real' if stream=='R_A' else 'Real resample'
    return stream.replace('LIFESTYLE_','').replace('_s',' / ')

def color(stream):
    return GREY if stream in ['R_A','R_B'] else (BLUE if 'A1_' in stream else PURPLE)

def interval(ax,row,y,prefix):
    get=lambda k:float(row[prefix+k])
    ax.plot([get('q025'),get('q975')],[y,y],color=color(row['stream']),linewidth=1.1,alpha=.8)
    ax.plot([get('q25'),get('q75')],[y,y],color=color(row['stream']),linewidth=3.4,solid_capstyle='round')
    ax.scatter([get('median')],[y],s=23,color=color(row['stream']),edgecolor='white',linewidth=.6,zorder=4)

def savefig(fig,name,files):
    for ext in ['png','svg','pdf']:
        target=HERE/'figures'/f'{name}.{ext}'
        fig.savefig(target,dpi=180,bbox_inches='tight',facecolor='white')
        files[str(target.relative_to(HERE))]=sha(target)
    plt.close(fig)

def main():
    review=read(HERE/'INDEPENDENT_REVIEW.json');assert review['status']=='pass'
    df=pd.read_csv(HERE/'CONTRAST_SUMMARIES.csv');sd=pd.read_csv(HERE/'SD_SUMMARIES.csv')
    pref=read(HERE/'PREFLIGHT.json');run=read(HERE/'RUN_RESULT.json')
    assert run['status']=='complete' and run['computed']==12000
    virtual=pref['virtual_ids'];roles=['R_A']+virtual
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'axes.labelcolor':INK,'text.color':INK,'xtick.color':GREY,'ytick.color':INK,
        'svg.fonttype':'none','pdf.fonttype':42})
    (HERE/'figures').mkdir(exist_ok=True);files={}
    fig,axes=plt.subplots(3,3,figsize=(15,10.8),sharey=True)
    for ti,t in enumerate(TRAITS):
        local=df[df.trait==t];xmin=min(0,float(local.signed_q025.min()));xmax=max(0,float(local.signed_q975.max()))
        margin=(xmax-xmin)*.07
        for ci,c in enumerate(CONTRASTS):
            ax=axes[ti,ci];g=local[local.contrast==c].set_index('stream',drop=False)
            ref=g.loc['R_A']
            ax.axvspan(ref.signed_q025,ref.signed_q975,color='#E8ECF2',alpha=.85,zorder=0)
            ax.axvline(0,color='#9BA7B6',linestyle='--',linewidth=.8)
            for y,role in enumerate(roles):interval(ax,g.loc[role],y,'signed_')
            ax.set_xlim(xmin-margin,xmax+margin);ax.set_ylim(6.6,-.6)
            ax.set_yticks(range(7),[label(r) for r in roles],fontsize=8)
            ax.set_title(NAMES[t]+' · '+CNAMES[c],fontsize=10,pad=12)
            unit='kg/m²' if t=='bmi' else 'mg/dL'
            ax.set_xlabel('Difference in adjusted contrast ('+unit+')',fontsize=9)
            ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
            ax.text(.01,1.02,f'n = {EXPECTED_N[t]:,}',transform=ax.transAxes,fontsize=8,color=GREY)
    fig.suptitle('Scientific comparisons at matched sample size and group composition',fontsize=17,y=.995)
    handles=[Line2D([0],[0],color=GREY,marker='o',label='Real − real'),Line2D([0],[0],color=BLUE,marker='o',label='Author A1: all three saved tables'),
        Line2D([0],[0],color=PURPLE,marker='o',label='Author A2: all three saved tables')]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,-.005),ncol=3,frameon=False,fontsize=9)
    fig.text(.5,.035,'Dots: median; thick lines: middle 50%; thin lines: middle 95% of 500 empirical resamples.\nGray band: real–real 95% range. These ranges are not clinical acceptance margins.',ha='center',fontsize=9,color=GREY)
    fig.tight_layout(rect=(0,.08,1,.965));savefig(fig,'matched_scientific_contrasts',files)
    fig,axes=plt.subplots(1,3,figsize=(14,4.6),sharey=True)
    for ax,t in zip(axes,TRAITS):
        g=sd[sd.trait==t].set_index('stream',drop=False)
        for y,role in enumerate(['R_B']+virtual):interval(ax,g.loc[role],y,'sd_')
        observed=float(g.loc['R_B'].original_sd)
        ax.axvline(observed,color=INK,linestyle='--',linewidth=1)
        ax.set_yticks(range(7),[label(r) for r in ['R_B']+virtual],fontsize=8);ax.set_ylim(6.6,-.6)
        ax.set_title(NAMES[t]+f' · n = {EXPECTED_N[t]:,}',fontsize=11)
        ax.set_xlabel('Sample SD ('+('kg/m²' if t=='bmi' else 'mg/dL')+')',fontsize=9)
        ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
    fig.suptitle('Dispersion remains a separate scientific diagnostic',fontsize=16)
    fig.text(.5,.01,'Dashed line: original measured-sample SD. Resampling ranges condition on each fixed empirical table.',ha='center',fontsize=9,color=GREY)
    fig.tight_layout(rect=(0,.055,1,.92));savefig(fig,'matched_dispersion',files)
    table=df.copy()
    table['trait']=table.trait.map(NAMES);table['contrast']=table.contrast.map(CNAMES);table['stream']=table.stream.map(label)
    columns=['trait','contrast','stream','original_real','original_other','signed_mean','signed_q025','signed_q975','absolute_mean']
    table=table[columns].rename(columns={'original_real':'Original real effect','original_other':'Original other effect',
        'signed_mean':'Mean matched difference','signed_q025':'Difference 2.5%','signed_q975':'Difference 97.5%',
        'absolute_mean':'Mean absolute difference'})
    svg1=(HERE/'figures/matched_scientific_contrasts.svg').read_text(encoding='utf-8')
    svg2=(HERE/'figures/matched_dispersion.svg').read_text(encoding='utf-8')
    source_note='Same frozen analysis, all nine contrasts; two Agent-authored laws and six saved cohorts. No new generation or target-based revision.'
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Matched-size scientific analysis · KDD evidence</title><style>
body{margin:0;background:#f5f6fa;color:#172b4d;font:16px/1.6 system-ui,sans-serif}main{max-width:1450px;margin:auto;padding:36px 4vw}h1{font-size:32px;line-height:1.2}h2{font-size:23px}.card{background:white;border:1px solid #dfe4ed;border-radius:12px;padding:22px;margin:22px 0}.muted{color:#667085}.metrics{display:flex;gap:16px;flex-wrap:wrap}.metrics div{background:#edf1fa;padding:12px 22px;border-radius:8px}svg{width:100%;height:auto}.scroll{overflow:auto}table{border-collapse:collapse;font-size:13px;width:100%}td,th{padding:9px;border-bottom:1px solid #e0e5ed;text-align:right;white-space:nowrap}th{background:#edf1fa}td:first-child,td:nth-child(2),td:nth-child(3){text-align:left}a{color:#355db5}.note{border-left:4px solid #8a5ba8;padding:8px 18px}footer{font-size:13px;color:#667085}
</style><main><p class="muted">17 November 2026 · Existing-data validation · KDD first paper</p><h1>Can virtual cohorts support the same scientific analyses?</h1><p>'''+html.escape(source_note)+'''</p><div class="metrics"><div><b>500</b> resamples per setting</div><div><b>12,000</b> analyzed samples</div><div><b>9</b> prespecified contrasts</div><div><b>0</b> new Agent calls</div></div>
<section class="card"><h2>How to read the comparison</h2><p>Each row compares an age/sex-adjusted group contrast with an independently resampled real reference. The gray band shows the differences between two real resamples. Blue and purple rows show all three saved tables from each Agent author.</p><p>A small difference is encouraging for that analysis. The gray band provides empirical sampling context; it is not an equivalence margin, independent cohort validation or an estimate of all scientific uncertainty.</p></section>
<section class="card">'''+svg1+'''</section><section class="card"><h2>Variability must also be checked</h2><p>A table can reproduce an adjusted contrast while underrepresenting individual variability. Standard deviations are therefore shown separately, in the original measurement units.</p>'''+svg2+'''</section>
<section class="card"><h2>What is held constant</h2><p>Real available-case sizes are BMI 1,189; total cholesterol 400; HDL 405. Each virtual resample uses exactly the corresponding six lifestyle-by-sex cell counts. Age and biomarker outcomes are not forced to match. The original six virtual tables each have 1,226 rows.</p><p class="note">Resamples come from the same empirical pools. Household/site clustering is unavailable in the bound adapter. This is a source-rich reconstruction with an already exposed reference, not a prospective population-transfer test.</p></section>
<section class="card"><h2>Complete numerical profile</h2><p>All effects and differences are in kg/m² for BMI and mg/dL for cholesterol. Original unmatched estimates remain visible.</p><div class="scroll">'''+table.to_html(index=False,float_format=lambda x:f'{x:.3f}',border=0)+'''</div></section>
<footer><p>Independent raw-outcome QR replays and complete aggregate recomputation passed. See <a href="../RESULTS.md">scientific interpretation</a>, <a href="../INDEPENDENT_REVIEW.json">numeric review</a> and <a href="../PROTOCOL.md">protocol</a>. Participant-level records and resampled rows are not included in this report.</p></footer></main></html>'''
    (HERE/'report').mkdir(exist_ok=True);(HERE/'report/index.html').write_text(page,encoding='utf-8')
    files['report/index.html']=sha(HERE/'report/index.html')
    write_new(HERE/'FIGURE_BINDINGS.json',dict(source_files={n:sha(HERE/n) for n in ['CONTRAST_SUMMARIES.csv','SD_SUMMARIES.csv']},
        contrast_panels=9,contrast_rows=63,dispersion_panels=3,dispersion_rows=21,display='all six saved tables; no favorable selection',artifacts=files))
    print(json.dumps(dict(artifacts=len(files),contrast_panels=9,dispersion_panels=3)))

if __name__=='__main__':main()

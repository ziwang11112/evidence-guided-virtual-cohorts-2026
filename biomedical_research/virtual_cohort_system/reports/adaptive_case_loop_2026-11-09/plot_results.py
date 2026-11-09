"""All requested scientific analyses and two available scale comparisons."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent

def main():
    data=json.loads((ROOT/'EVALUATION.json').read_text())
    panels=[('analyses','K02-HDL-BMI','Adjusted BMI–HDL','mg/dL per 5 kg/m²'),
            ('analyses','K02-TC-BMI','Adjusted BMI–total cholesterol','mg/dL per 5 kg/m²'),
            ('analyses','K02-LIPID-RESIDUAL','Residual lipid correlation','Pearson r'),
            ('diagnostics','total_cholesterol.sd_sample','Total cholesterol dispersion','Sample SD (mg/dL)'),
            ('diagnostics','hdl_cholesterol.sd_sample','HDL dispersion','Sample SD (mg/dL)')]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,3,figsize=(12,6.6),layout='constrained')
    colors=['#3366B5','#8D60B5','#DC884C']
    for ax,(cat,key,title,unit) in zip(axes.flat,panels):
        ref=None
        for i,stage in enumerate(data['stages']):
            x=next((r for r in stage[cat] if r['id']==key),None)
            if x is None or x['mean'] is None:
                ax.text(i,.03,'unavailable',ha='center',transform=ax.get_xaxis_transform(),fontsize=8)
                continue
            ref=x['reference_value']
            ax.errorbar(i,x['mean'],yerr=[[x['mean']-x['seed_min']],[x['seed_max']-x['mean']]],
                        fmt='o',color=colors[i%len(colors)],capsize=4,markersize=7,lw=1.7)
            interval=x['reference_interval']
            if i==0 and interval and interval.get('lower') is not None and interval.get('upper') is not None:
                ax.axhspan(interval['lower'],interval['upper'],color='#C8CCD5',alpha=.14,zorder=0)
        if ref is not None:ax.axhline(ref,color='#4B5260',linestyle='--',lw=1.3,label='Existing real sample')
        ax.set_title(title,loc='left',weight='bold',fontsize=11)
        ax.set_ylabel(unit)
        ax.set_xticks(range(len(data['stages'])),['Primary (retained)' if s['selected_final'] else 'Sensitivity' for s in data['stages']])
        ax.set_xlim(-.5,max(.5,len(data['stages'])-.5));ax.grid(axis='y',alpha=.17)
    axes.flat[-1].axis('off')
    axes.flat[-1].text(0,1,'READING THE FIGURE',va='top',weight='bold',fontsize=12,color='#263349')
    axes.flat[-1].text(0,.86,'Dots: mean across scheduled draws\nWhiskers: seed min–max, not clinical CI\nDashed: existing sample reference\nShading: supplied coefficient sensitivity\ninterval, not an equivalence margin\n\nAll requested analyses are shown.\nOne author · one developmental case\nNo target results in the author feedback.',va='top',linespacing=1.7,color='#4B5260')
    fig.suptitle('Scientific analyses of Agent-generated cohorts',fontsize=16,weight='bold')
    fig.savefig(ROOT/'scientific_analyses.png',dpi=190)
    fig.savefig(ROOT/'scientific_analyses.pdf')

if __name__=='__main__':main()

"""All five reference-bearing endpoints from two closed development runs."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent

def main():
    data = json.loads((ROOT/'EVALUATION.json').read_text(encoding='utf8'))
    comparison = json.loads((ROOT/'PREVIOUS_COMPARISON.json').read_text(encoding='utf8'))
    current = next(s for s in data['stages'] if s['selected_final'])
    panels = [
        ('analyses', 'K02-HDL-BMI', 'Adjusted BMI-HDL association', r'mg/dL per 5 kg/m$^2$'),
        ('analyses', 'K02-TC-BMI', 'Adjusted BMI-total cholesterol', r'mg/dL per 5 kg/m$^2$'),
        ('analyses', 'K02-LIPID-RESIDUAL', 'Residual lipid correlation', 'Pearson r'),
        ('diagnostics', 'total_cholesterol.sd_sample', 'Total cholesterol dispersion', 'Sample SD (mg/dL)'),
        ('diagnostics', 'hdl_cholesterol.sd_sample', 'HDL dispersion', 'Sample SD (mg/dL)')]
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                         'axes.spines.top':False, 'axes.spines.right':False, 'pdf.fonttype':42})
    fig, axes = plt.subplots(2,3,figsize=(12,6.6),layout='constrained')
    colors = ['#8D60B5', '#3366B5']
    for panel, (ax, (category,key,title,unit)) in enumerate(zip(axes.flat,panels)):
        item = next(x for x in comparison['endpoints'] if x['id']==key)
        report = next(x for x in current[category] if x['id']==key)
        interval = report['reference_interval']
        if interval and interval.get('lower') is not None and interval.get('upper') is not None:
            ax.axhspan(interval['lower'],interval['upper'],color='#C8CCD5',alpha=.22,zorder=0)
        for i, prefix in enumerate(('previous','current')):
            value = item[prefix+'_selected']; lo,hi = item[prefix+'_seed_range']
            if value is None:
                ax.text(i,.03,'unavailable',ha='center',transform=ax.get_xaxis_transform(),fontsize=8)
                continue
            ax.errorbar(i,value,yerr=[[value-lo],[hi-value]],fmt='o',color=colors[i],
                        capsize=4,markersize=7,lw=1.7)
            ax.annotate(f'{value:.2f}',(i,value),xytext=(8,8),textcoords='offset points',
                        fontsize=9,color=colors[i],weight='bold')
        ax.axhline(item['existing_sample_reference'],color='#4B5260',linestyle='--',lw=1.3)
        ax.set_title(f'{chr(97+panel)}  {title}',loc='left',weight='bold',fontsize=11)
        ax.set_ylabel(unit); ax.set_xticks([0,1],['Previous run','Current run'])
        ax.set_xlim(-.45,1.6); ax.grid(axis='y',alpha=.17)
    key = axes.flat[-1]; key.axis('off')
    key.text(0,1,'HOW TO READ',va='top',weight='bold',fontsize=12,color='#263349')
    key.text(0,.87,'Dots: selected-model mean, three draws\nWhiskers: seed range, not clinical CI\nDashed line: existing real-sample estimate\nShading: supplied coefficient interval;\nnot an equivalence margin\n\nBoth authors selected before comparison.\nAll five comparable endpoints are shown.\nDifferent models and evidence choices:\nthis does not isolate a feature effect.',
             va='top',linespacing=1.7,color='#4B5260')
    fig.suptitle('Final-data analyses across two development runs',fontsize=16,weight='bold')
    fig.savefig(ROOT/'scientific_analyses.png',dpi=190)
    fig.savefig(ROOT/'scientific_analyses.pdf')

if __name__=='__main__': main()

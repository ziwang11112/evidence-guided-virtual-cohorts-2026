"""Plot actual source projections and separately labelled analytic assumptions."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    feedback = read(HERE / 'INITIAL_SOURCE_FEEDBACK.json')
    bundle = Path(read(HERE / 'PROTOCOL.json')['bundle'])
    sensitivity = read(bundle / 'candidates/initial/analytic_sensitivity.json')
    destination = HERE / 'figures'
    destination.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    groups = [('source_main', 'Rural women'), ('source_alt1', 'Rural men'),
              ('source_alt2', 'Urban women'), ('source_alt3', 'Urban men')]
    colors = ['#3159B8', '#8A5DBA', '#DA824B']
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))
    for ax, outcome, label in zip(axes, ['TC', 'HDL'], ['Total cholesterol', 'HDL cholesterol']):
        for i, (context, group_label) in enumerate(groups):
            records = sorted([r for r in feedback['records'] if r['context_id']==context and r['check_id'].endswith('_'+outcome)], key=lambda x:x['replay_id'])
            original = records[0]
            ci = original['reported_uncertainty']
            ax.plot([ci['low'], ci['high']], [i, i], color='#8D929F', lw=3, solid_capstyle='round')
            ax.plot(original['reported'], i, marker='D', color='#283342', ms=6, zorder=4)
            for j, row in enumerate(records):
                if row['status']=='computed':
                    ax.scatter(row['generated'], i+(j-1)*.14, s=35, color=colors[j], edgecolor='white', linewidth=.6, zorder=5)
        ax.set_yticks(range(4), [g[1] for g in groups]);ax.invert_yaxis()
        ax.set_title(label, loc='left', fontweight='bold', pad=12)
        ax.set_xlabel('Adjusted BMI coefficient\n(mmol/L per BMI SD; replay uses sample SD)')
        ax.grid(axis='x', color='#E4E7ED', lw=.7);ax.set_axisbelow(True)
        ax.set_ylim(3.5,-.5)
    legend = [Line2D([], [], color='#8D929F', lw=3, marker='D', markerfacecolor='#283342', markeredgecolor='#283342', label='Published estimate and 95% CI')]
    legend += [Line2D([], [], marker='o', linestyle='None', color=c, label='Generated draw '+str(i+1)) for i,c in enumerate(colors)]
    fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,.10),ncol=4,frameon=False,fontsize=9)
    fig.suptitle('Declared source relationships become executable checks', x=.065, ha='left', fontsize=14, fontweight='bold', y=.98)
    fig.text(.065,.035,'12 source-law tables; 8,000 rows each. Full nuisance adjustment. Published SD convention unresolved; replay is assumption-dependent.\nPublished CIs describe source estimation; three draws show Monte Carlo variation and are not independent studies.',fontsize=8.5,color='#535D6B')
    fig.subplots_adjust(left=.13,right=.98,top=.86,bottom=.32,wspace=.48)
    for ext in ('png','svg','pdf'):fig.savefig(destination/('source_relationships.'+ext),dpi=180,facecolor='white')
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7.3,4.5))
    palette = ['#3159B8','#8A5DBA','#DA824B','#4B5368']
    for row,color,(_,label) in zip(sensitivity['records'],palette,groups):
        vals=row['component_coupling_sensitivity_at_source_level_anchors']
        ax.plot([r['assumed_component_error_correlation_q'] for r in vals],
                [r['implied_fixed_covariate_TC_HDL_correlation'] for r in vals],marker='o',color=color,label=label)
    ax.axhline(0,color='#A2A7B0',lw=.8);ax.set_xticks([-.75,0,.75]);ax.set_ylim(-.65,1)
    ax.set_xlabel('Assumed HDL / non-HDL component-noise correlation')
    ax.set_ylabel('Implied TC / HDL correlation\nat fixed covariates and source-level anchors')
    ax.grid(color='#E7E9EF',lw=.7);ax.set_axisbelow(True)
    ax.set_title('The same BMI slopes allow different joint dependence',loc='left',fontweight='bold',pad=14)
    ax.legend(frameon=False,fontsize=8,ncol=2,loc='lower right')
    fig.text(.14,.035,'Analytic scenario calculation, not generated target results or clinical evidence.\nMean slopes remain unchanged; residual coupling is not identified by the adopted slope evidence.',fontsize=8.5,color='#535D6B')
    fig.subplots_adjust(left=.15,right=.97,top=.86,bottom=.26)
    for ext in ('png','svg','pdf'):fig.savefig(destination/('joint_assumption_sensitivity.'+ext),dpi=180,facecolor='white')
    plt.close(fig)
    print(json.dumps({'figures':6,'source':'INITIAL_SOURCE_FEEDBACK.json and frozen analytic_sensitivity.json','reference_access':False}))

if __name__=='__main__':main()

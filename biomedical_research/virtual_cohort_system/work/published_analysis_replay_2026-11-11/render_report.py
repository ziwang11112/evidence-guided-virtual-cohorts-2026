"""Render aggregate-only fixed-analysis report. Never opens individual-level files."""
from pathlib import Path
import hashlib
import html
import json
import re
from datetime import datetime, timezone

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
FIG = HERE / 'figures'
PAIRS = [('bmi__total_cholesterol', 'BMI – total cholesterol'),
         ('bmi__hdl_cholesterol', 'BMI – HDL'),
         ('total_cholesterol__hdl_cholesterol', 'Total cholesterol – HDL')]
ORDER = [f'LIPID_{arm}_R{i}' for arm in ['BASE', 'WORKFLOW'] for i in [1, 2, 3]]
LABELS = {f'LIPID_{arm}_R{i}': f'{label} {i}' for arm, label in [('BASE', 'Ordinary'), ('WORKFLOW', 'Workflow')] for i in [1, 2, 3]}
COLORS = {'BASE': '#316CB0', 'WORKFLOW': '#7F54AF'}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def esc(x):
    return html.escape(str(x))

def fmt(x, digits=4):
    return '不可用' if x is None else f'{x:.{digits}f}'

def point(record, pair, field='r'):
    return next(x[field] for x in record['analyses'] if x['pair'] == pair)

def summarize(records, pair):
    vals = [point(r, pair) for r in records if r['status'] == 'computed']
    vals = [float(x) for x in vals if x is not None]
    return dict(n=len(vals), mean=float(np.mean(vals)) if vals else None,
                low=min(vals) if vals else None, high=max(vals) if vals else None)

def save_figure(fig, name):
    fig.savefig(FIG/f'{name}.svg', bbox_inches='tight')
    fig.savefig(FIG/f'{name}.png', dpi=160, bbox_inches='tight')
    plt.close(fig)

def inline_svg(name):
    s = (FIG/f'{name}.svg').read_text(encoding='utf-8')
    return s[s.index('<svg'):]

def main():
    src = HERE/'ANALYSIS.json'
    if not src.exists():
        raise SystemExit('ANALYSIS.json is not available; no placeholder results produced.')
    data = json.loads(src.read_text(encoding='utf-8'))
    records = data['records']
    assert len(records) == 25, 'Expected all 25 planned tables, including failures.'
    assert len({r['id'] for r in records}) == 25
    assert all({a['pair'] for a in r['analyses']} == {p for p,_ in PAIRS} for r in records)
    real = [r for r in records if r['role'] == 'real_reference']
    assert len(real) == 1
    real = real[0]
    groups = {e:[r for r in records if r['episode'] == e] for e in ORDER}
    assert all(len(v) == 3 for v in groups.values()), 'Initial constructors must retain all three seeds.'
    assert all(r['role'] == 'initial' for g in groups.values() for r in g)
    repairs = [r for r in records if r['role'] not in ['initial','real_reference']]
    assert len(repairs) == 6
    repair_ids = list(dict.fromkeys(r['episode'] for r in repairs))
    assert len(repair_ids) == 2
    all_groups = {**groups, **{e:[r for r in repairs if r['episode'] == e] for e in repair_ids}}
    summaries = {e:{p:summarize(g,p) for p,_ in PAIRS} for e,g in all_groups.items()}
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'svg.fonttype':'none','axes.titleweight':'bold',
                         'axes.labelcolor':'#283449','text.color':'#283449','axes.edgecolor':'#ABB5C4'})
    fig, axes = plt.subplots(1,3,figsize=(16,4.6),sharey=True)
    for ax,(pair,label) in zip(axes,PAIRS):
        rv=point(real,pair)
        ax.axvline(0,color='#D9DFE8',lw=1,zorder=0)
        if rv is not None: ax.axvline(rv,color='#636B78',lw=1.8,ls='--',label='Real sample')
        for i,e in enumerate(ORDER):
            color=COLORS['BASE' if '_BASE_' in e else 'WORKFLOW']
            st=summaries[e][pair]
            if st['n']:
                ax.plot([st['low'],st['high']],[i,i],color=color,lw=2,alpha=.6)
                for j,r in enumerate(sorted(groups[e],key=lambda r:r['seed'])):
                    v=point(r,pair)
                    if v is not None: ax.scatter(v,i+(j-1)*.13,s=23,c=color,alpha=.75,zorder=3)
                ax.scatter(st['mean'],i,marker='D',s=40,c=color,edgecolors='white',linewidths=.7,zorder=4)
            else: ax.text(0,i,'Unavailable',va='center',ha='center',color='#697487')
        ax.set_xlim(-1,1); ax.set_xticks([-1,-.5,0,.5,1]); ax.grid(axis='x',alpha=.16)
        ax.set_title(label,pad=14); ax.set_xlabel('Age/sex-adjusted residual Pearson r')
        ax.set_yticks(range(6),[LABELS[e] for e in ORDER]); ax.set_ylim(5.55,-.55)
        ax.text(.5,1.025,f'Real sample: {fmt(rv,3)}',transform=ax.transAxes,ha='center',color='#636B78',fontsize=9)
    fig.suptitle('Same analysis, different input data',fontsize=16,y=1.04)
    fig.text(.5,-.015,'Circles: all three fixed draws. Diamonds: their means. Horizontal spans: draw ranges, not confidence intervals.',ha='center',fontsize=10)
    fig.tight_layout(w_pad=2.0)
    save_figure(fig,'fixed_analysis_pairs')

    fig,axes=plt.subplots(1,7,figsize=(18,3.15))
    matrices={}
    for ax,e in zip(axes,['REAL']+ORDER):
        mat=np.eye(3)
        for (i,j),(pair,_) in zip([(0,1),(0,2),(1,2)],PAIRS):
            value=point(real,pair) if e=='REAL' else summaries[e][pair]['mean']
            mat[i,j]=mat[j,i]=np.nan if value is None else value
        matrices[e]=mat.tolist()
        im=ax.imshow(mat,vmin=-1,vmax=1,cmap='RdBu_r')
        ax.set_title('Real sample' if e=='REAL' else LABELS[e],fontsize=10,pad=10)
        ax.set_xticks(range(3),['BMI','TC','HDL'],fontsize=9)
        ax.set_yticks(range(3),['BMI','TC','HDL'],fontsize=9)
        for i in range(3):
            for j in range(3):
                v=mat[i,j]
                cell='NA' if np.isnan(v) else ('~0.00' if abs(v)<.005 else f'{v:.2f}')
                ax.text(j,i,cell,ha='center',va='center',
                        fontsize=9,color='white' if np.isfinite(v) and abs(v)>.57 else '#202634')
        for spine in ax.spines.values():spine.set_visible(False)
    fig.subplots_adjust(left=.035,right=.94,top=.78,bottom=.18,wspace=.55)
    cbax=fig.add_axes([.956,.24,.008,.46]);fig.colorbar(im,cax=cbax,ticks=[-1,0,1],label='r')
    fig.suptitle('The same three-variable relationship matrix',fontsize=15,y=.99)
    fig.text(.5,.025,'Virtual matrices average three draws. Same scale [-1, 1]; diagonal: identities; ~0.00: absolute mean below 0.005 (rounding only).',ha='center',fontsize=10)
    save_figure(fig,'relationship_matrices')

    headers=['构造','分析','有效 seed','平均 r','seed 范围','真实参照 r','平均 r − 参照','绝对差']
    def summary_rows(eps):
        rows=[]
        for e in eps:
            for pair,label in PAIRS:
                st=summaries[e][pair];ref=point(real,pair)
                diff=st['mean']-ref if st['mean'] is not None and ref is not None else None
                vals=[LABELS.get(e,e),label,f"{st['n']}/3",fmt(st['mean']),
                      f"[{fmt(st['low'])}, {fmt(st['high'])}]",fmt(ref),fmt(diff),fmt(abs(diff)) if diff is not None else '不可用']
                rows.append('<tr>'+''.join(f'<td>{esc(v)}</td>' for v in vals)+'</tr>')
        return ''.join(rows)
    def table(heads,body,cls=''):
        return f'<div class="table-scroll"><table class="{cls}"><thead><tr>'+''.join(f'<th>{esc(h)}</th>' for h in heads)+'</tr></thead><tbody>'+body+'</tbody></table></div>'
    rawrows=[]
    for r in records:
        for a in r['analyses']:
            vals=[r['id'],r['role'],r['seed'] if r['seed'] is not None else '—',r['status'],
                  r.get('counts',{}).get('retained_rows','—'),a['pair'],fmt(a['r'],6),fmt(a['r_squared'],6)]
            rawrows.append('<tr>'+''.join(f'<td>{esc(v)}</td>' for v in vals)+'</tr>')
    countrows=[]
    for r in records:
        c=r.get('counts',{})
        vals=[r['id'],c.get('input_rows','—'),c.get('retained_rows','—'),
              json.dumps(c.get('exclusions',{}),ensure_ascii=False),c.get('hdl_above_tc_retained_rows','—'),r.get('reason','')]
        countrows.append('<tr>'+''.join(f'<td>{esc(v)}</td>' for v in vals)+'</tr>')
    nreal=real.get('counts',{}).get('retained_rows','不可用')
    ngens=sorted({r['counts']['retained_rows'] for r in records if r['role']!='real_reference' and 'counts' in r})
    failures=[r for r in records if r['status']!='computed']
    usable=sum(a['r'] is not None for r in records for a in r['analyses'])
    failure_html='' if not failures else '<div class="warning"><strong>不可用输入已保留</strong><ul>'+''.join(f'<li>{esc(r["id"])}: {esc(r.get("reason","未计算"))}</li>' for r in failures)+'</ul></div>'
    links=[('PROTOCOL.md','冻结方案'),('TURKANA_ADMISSION.md','原文与字段核查'),('ANALYSIS.json','完整聚合结果'),
           ('PAIR_RESULTS.csv','75 项估计 CSV'),('INDEPENDENT_RECOMPUTE.json','独立复算记录'),('INDEPENDENT_REVIEW.md','独立审查'),
           ('HRS_SCOPE_AUDIT.md','HRS 案例范围审查'),('replay_analysis.py','相同分析算子'),('render_report.py','报告生成脚本')]
    linkhtml=' · '.join(f'<a href="{path}">{esc(label)}</a>' for path,label in links if (HERE/path).exists())
    initial_table=table(headers,summary_rows(ORDER))
    repair_table=table(headers,summary_rows(['LIPID_BASE_R2']+repair_ids))
    overview_rows=[]
    for pair,label in PAIRS:
        ms=[summaries[e][pair]['mean'] for e in ORDER if summaries[e][pair]['mean'] is not None]
        rv=point(real,pair)
        note='保留全部数值，逐项解释'
        if ms and rv is not None and pair=='bmi__total_cholesterol' and all(v>rv for v in ms):
            note='六个构造均比这份真实参照更强'
        elif ms and rv is not None and pair=='total_cholesterol__hdl_cholesterol' and all(0<v<rv for v in ms):
            note='六个构造保留正向，但强度均低于参照'
        elif pair=='bmi__hdl_cholesterol':
            note='五个构造稳定负向；Workflow 2 接近零，seed 跨零'
        vals=[label,fmt(rv,3),f'[{fmt(min(ms),3)}, {fmt(max(ms),3)}]' if ms else '不可用',note]
        overview_rows.append('<tr>'+''.join(f'<td>{esc(v)}</td>' for v in vals)+'</tr>')
    overview_table=table(['分析关系','真实样本 r','六个构造平均 r 的跨度','本轮观察'],''.join(overview_rows))
    w2=summaries['LIPID_WORKFLOW_R2']['bmi__hdl_cholesterol']
    full_table=table(['表 ID','角色','seed','状态','分析人数','变量对','r','r²'],''.join(rawrows),'raw-estimates')
    count_table=table(['表 ID','输入行','保留行','互斥排除计数','保留 HDL>TC 行','不可用原因'],''.join(countrows))
    document=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>只换数据，同一分析｜虚拟队列的科学用途</title><style>
:root{{--ink:#202D45;--muted:#66748B;--line:#DAE1EB;--blue:#316CB0;--purple:#7F54AF;--paper:#F5F7FB}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:Segoe UI,Microsoft YaHei,Arial,sans-serif;line-height:1.65}}main{{max-width:1260px;margin:auto;padding:40px 28px 70px}}h1{{font-size:36px;line-height:1.25;letter-spacing:-1px;margin:14px 0}}h2{{font-size:23px;margin:0 0 14px}}h3{{font-size:17px}}p{{margin:10px 0}}.eyebrow{{color:var(--blue);font-size:13px;font-weight:700;letter-spacing:1px}}.lead{{font-size:19px;max-width:950px}}.muted,figcaption{{color:var(--muted)}}section{{background:white;border:1px solid var(--line);border-radius:14px;margin-top:24px;padding:26px}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}}.stat{{background:white;border-top:3px solid var(--blue);padding:15px 18px;border-radius:7px}}.stat b{{display:block;font-size:27px}}.stat span{{font-size:13px;color:var(--muted)}}.flow{{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:22px 0;font-size:17px}}.flow span{{padding:10px 15px;background:#EEF2FA;border-radius:8px}}.flow .operator{{background:#F0EAF6;color:#65418C}}figure{{margin:18px 0 8px}}.figure-scroll{{overflow-x:auto}}.figure-scroll svg{{width:100%;height:auto;display:block;min-width:760px}}.matrix svg{{min-width:1100px}}figcaption{{font-size:13px;margin-top:12px}}.cols{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}.callout{{padding:14px 18px;background:#F3F0F8;border-left:4px solid var(--purple);margin:16px 0}}.warning{{padding:15px;background:#FFF4E8;border-left:4px solid #C17A29}}a{{color:var(--blue)}}.table-scroll{{overflow:auto;margin:14px 0}}table{{border-collapse:collapse;width:100%;font-size:13px;white-space:nowrap}}th,td{{padding:9px 11px;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}}th{{background:#EEF2F7}}th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){{text-align:left}}tbody tr:hover{{background:#F7F9FC}}details{{margin-top:16px}}summary{{font-weight:600;cursor:pointer;color:var(--blue);padding:8px 0}}footer{{font-size:12px;color:var(--muted);margin-top:25px;overflow-wrap:anywhere}}.tag{{font-size:12px;display:inline-block;border:1px solid #C8D3E2;border-radius:20px;padding:3px 10px;margin-right:7px}}@media(max-width:700px){{main{{padding:24px 14px}}h1{{font-size:28px}}section{{padding:18px}}.stats{{grid-template-columns:1fr 1fr}}.cols{{grid-template-columns:1fr}}}}@media print{{body{{background:white}}main{{padding:0}}section{{break-inside:avoid;border-radius:0}}.figure-scroll svg{{min-width:0}}.table-scroll{{overflow:visible}}details:not([open])> :not(summary){{display:none}}a{{color:inherit}}}}
</style></head><body><main>
<div class="eyebrow">固定分析 · 现有数据复用 · 2026-11-11</div><h1>只换数据，同一分析</h1>
<p class="lead">真实与 Agent 虚拟数据，都先去除年龄、性别的线性关系，再比较 BMI、总胆固醇和 HDL 之间的相关结构。</p>
<p class="muted">本轮复用 Lea 等（2020）补充材料中的一个分析算子，运行全部现有构造。没有新生成、重新训练、目标调参或新增 API 费用。</p>
<div class="stats"><div class="stat"><b>{nreal}</b><span>真实文件本次保留人数</span></div><div class="stat"><b>6 × 3</b><span>初始构造 × 已有随机种子表</span></div><div class="stat"><b>2 × 3</b><span>既有依赖修复 × 随机种子表</span></div><div class="stat"><b>{usable} / 75</b><span>可计算估计 / 预定估计</span></div></div>
<div class="flow"><span>真实表 / 冻结虚拟表</span>→<span class="operator">相同筛选 · 相同年龄/性别调整</span>→<span>同一相关矩阵</span></div>{failure_html}
<section><h2>1. 替换数据后，三条关系怎样变化？</h2>
{overview_table}<p>这次结果支持部分关联方向的保留，同时显示关系强度并未全部保留。Workflow 2 的 BMI–HDL 平均 r 为 {fmt(w2['mean'],5)}，三个 draw 范围 [{fmt(w2['low'],5)}, {fmt(w2['high'],5)}]；不能只凭平均值的负号称它复现了稳定负向关系。</p>
<p>每一行代表一个独立的初始构造，每个圆点是一张已有虚拟表。菱形是该构造三个 seed 的平均值；灰色竖线是本次真实样本参照。</p>
<figure class="figure-scroll">{inline_svg('fixed_analysis_pairs')}<figcaption>横向越接近灰线，表示这一项样本统计更接近；不是临床通过标准。线段是三个生成 draw 的最小–最大范围，不是置信区间。普通 Agent 用蓝色，workflow 用紫色，全部结果均保留。</figcaption></figure>
<div class="cols"><div><h3>怎么读 r？</h3><p>r &gt; 0 表示年龄、性别调整后，两项指标倾向同向变化；r &lt; 0 表示反向变化。越接近 0，线性关联越弱。这不是因果效应。</p></div><div><h3>什么叫分析有用？</h3><p>看替换数据是否改变关系方向和强弱，以及因此产生的科学解释。本报告提供完整数值，不用事后挑选的阈值把整张表判为“好”或“坏”。</p></div></div>
<details><summary>查看全部 18 行初始构造汇总、范围和差值</summary>{initial_table}</details></section>
<section><h2>2. 同一份表，是否保留共同的关系结构？</h2><p>三条关系放回同一个矩阵，观察整体结构。所有面板使用相同 −1 到 1 的颜色范围。虚拟面板是各构造三个 draw 的相关系数均值，未合并个体记录。</p>
<figure class="figure-scroll matrix">{inline_svg('relationship_matrices')}<figcaption>红色为正相关，蓝色为负相关；对角线的 1 是变量与自身的恒等相关，不是生成质量得分。</figcaption></figure></section>
<section><h2>3. 已有数学修复，单独列示</h2><p>下面是同一初始构造 LIPID_BASE_R2 与其两个已完成修复版本。它们是依赖分支，不是两个新独立构造；修复数学尾部不预先等于科学关系改善。本轮没有再次修订它们。</p>{repair_table}</section>
<section><h2>4. 本轮到底复现到哪一层？</h2><div class="cols"><div><h3>保持相同</h3><ul><li>年龄 &gt;18、五项可用且有限、F/M 编码及正值要求。</li><li>三个生物指标中心化/SD 标准化；截距 + 连续年龄 + 性别的 OLS。</li><li>三对残差 Pearson r 和 r²；TC–HDL 不额外调整 BMI。</li><li>两类输入仅做字段映射与已记录的血脂单位转换。</li></ul></div><div><h3>明确边界</h3><ul><li>这是按 Methods 重实现的三指标子分析；未获得原作者分析脚本，也不是完整十指标矩阵。</li><li>共同完整病例是本次固定选择，原文未交代逐对/共同缺失处理。</li><li>原孕期、访谈与极端值排除无法完整重建；不冒称相同原始分析样本。</li><li>既有目标已经暴露，本轮是冻结数据的开发性再分析，不是新队列确认。</li></ul></div></div>
<div class="callout">真实参照人数为 {nreal}；虚拟表本次保留人数集合为 {esc(', '.join(map(str,ngens)))}。样本量不同；更多虚拟行不会自动增加临床证据。这里没有总体真值、因果、显著性或临床等效声明。</div>
<details><summary>查看全部 75 项预定估计（包括不可用项）</summary>{full_table}</details>
<details><summary>查看每张表的实际人数与排除记录</summary>{count_table}</details></section>
<section><h2>5. 可追溯材料</h2><p>{linkhtml}</p><p>原文：<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/">Lea et al., Science Advances 2020</a>；<a href="https://gurven.anth.ucsb.edu/sites/default/files/sitefiles/papers/lea%20et%20al.%202020%20supplement.pdf">补充材料第 7 页，Correlations between measures</a>。</p><p class="muted">HTML 内嵌全部图像，可以离线阅读。只包含汇总结果，不包含真实或虚拟个体记录。</p></section>
<footer>聚合源 SHA256：{sha(src)}<br>报告由 render_report.py 从 ANALYSIS.json 生成；绘图不会读取或执行任何生成器，也不会读取患者表。</footer>
</main></body></html>'''
    (HERE/'index.html').write_text(document,encoding='utf-8')
    audit=dict(created_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha(src),
               html_sha256=sha(HERE/'index.html'),renderer_sha256=sha(__file__),
               planned_tables=25,all_input_records=len(records),planned_estimates=75,
               rendered_detail_rows=len(rawrows),computed_estimates=usable,failed_tables=[r['id'] for r in failures],
               initial_order=ORDER,initial_group_counts={e:len(g) for e,g in groups.items()},
               repair_order=repair_ids,summary_statistics=summaries,matrices=matrices,
               patient_tables_opened=False,generated_tables_opened=False,new_generation=False,
               figures={f.name:sha(f) for f in sorted(FIG.iterdir()) if f.suffix in ['.png','.svg']},
               full_browser_preview=False)
    (HERE/'REPORT_BUILD.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'html':str(HERE/'index.html'),'detail_rows':len(rawrows),'computed':usable}))

if __name__=='__main__':
    main()

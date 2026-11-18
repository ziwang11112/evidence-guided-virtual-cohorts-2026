"""Author an editable current-runtime architecture; no experiment execution."""
from pathlib import Path
import xml.etree.ElementTree as ET

P = Path(__file__).resolve().parents[2]
ASSET = P / 'docs/report-assets-2026-11-11'
ASSET.mkdir(parents=True, exist_ok=True)
QA = Path(__file__).resolve().parent / 'qa'
QA.mkdir(exist_ok=True)
BLUE, PURPLE, ORANGE = '#4169a8', '#8862ad', '#c17936'
INK, MUTED = '#26364b', '#627187'
g = ET.Element('mxGraphModel', adaptiveColors='auto', page='1', pageWidth='1100', pageHeight='550',
               background='#ffffff', grid='0', defaultLabelBackgroundColor='#ffffff')
root = ET.SubElement(g, 'root')
ET.SubElement(root, 'mxCell', id='0')
ET.SubElement(root, 'mxCell', id='1', parent='0')

def node(i, value, x, y, w, h, style=''):
    c = ET.SubElement(root, 'mxCell', id=i, parent='1', vertex='1', value=value,
        style='html=1;whiteSpace=wrap;fontFamily=Microsoft YaHei;fontSize=16;fontColor='+INK+';'+style)
    ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), attrib={'as':'geometry'})
    return i

def text(i, value, x,y,w,h, size=14, color=INK, bold=False, align='left'):
    return node(i,value,x,y,w,h,
        f'text;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};spacing=0;')

def box(i,value,x,y,w,h,color,fill):
    return node(i,value,x,y,w,h,f'rounded=1;arcSize=14;strokeWidth=1.5;strokeColor={color};fillColor={fill};spacing=9;')

def edge(i,s,t,color=BLUE,dashed=False,label='',both=False):
    c=ET.SubElement(root,'mxCell',id=i,parent='1',edge='1',source=s,target=t,value=label,
        style=f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={color};strokeWidth=1.6;endArrow=block;endFill=1;jettySize=auto;fontFamily=Microsoft YaHei;fontSize=12;fontColor={color};labelBackgroundColor=#ffffff;'+
        ('dashed=1;dashPattern=5 4;' if dashed else '')+('startArrow=block;startFill=1;' if both else ''))
    ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})

node('canvas','',0,0,1100,550,'strokeColor=none;fillColor=#ffffff;')
text('title','从研究需求到可分析的虚拟人群',26,14,850,34,24,INK,True)
text('subtitle','Agent 决定科学模型；程序执行抽样；真实参照用于冻结后的独立评估',28,52,1030,24,14,MUTED)
box('build_lane','',25,90,1050,280,'#d9e3ef','#f7f9fc')
box('eval_lane','',25,393,1050,124,'#dce1e8','#fafbfd')
edge('stage_transition','build_lane','eval_lane','#9caabe')
text('build_label','构造与工具循环',43,102,190,25,15,BLUE,True)

box('request','<b>研究需求</b><br><span style="font-size:13px">人群 · 指标 · 分析问题</span>',43,185,150,72,BLUE,'#ffffff')
box('agent','<b>科研 Agent</b><br><span style="font-size:13px">选择证据、结构与参数</span><br><span style="font-size:12px">GPT API · 工具调用</span>',250,171,180,98,PURPLE,'#f0ebf7')
box('literature','<b>检索 / 阅读原文</b><br><span style="font-size:12px">Europe PMC · 分节与表格</span>',250,104,180,49,BLUE,'#edf3fb')
box('law','<b>生成器</b><br><span style="font-size:13px">模型规格 + Python</span>',505,185,150,72,PURPLE,'#ffffff')
box('sampling','<b>隔离抽样</b><br><span style="font-size:13px">WSL / bubblewrap</span>',720,185,155,72,ORANGE,'#fff8ef')
box('trial','<b>试生成数据</b><br><span style="font-size:13px">表格 + 统计诊断</span>',930,185,125,72,ORANGE,'#ffffff')
box('checks','<b>分布 · 回归 · 联合关系检查</b><br><span style="font-size:12px">后续复查版另接入：数学性质 / 生理规则 / 依赖依据</span>',505,296,550,53,ORANGE,'#fff8ef')
edge('request_agent','request','agent')
edge('literature_loop','agent','literature',BLUE,both=True)
edge('agent_law','agent','law',PURPLE)
edge('law_sampling','law','sampling',PURPLE)
edge('sampling_trial','sampling','trial',ORANGE)
edge('trial_checks','trial','checks',ORANGE)
edge('optional_revision','checks','agent',PURPLE,True)
text('revise_label','自行判断：保留 / 改写',264,310,218,25,13,PURPLE)
root.find("mxCell[@id='revise_label']").set('style', root.find("mxCell[@id='revise_label']").get('style')+'fillColor=#f7f9fc;')

text('evaluation_label','选定版本并关闭全部会话后 · 独立评估，不回传目标结果',43,402,990,25,14,BLUE,True)
box('freeze','<b>冻结生成器</b><br><span style="font-size:12px">版本与哈希</span>',43,437,160,57,PURPLE,'#ffffff')
box('final','<b>最终虚拟人群</b><br><span style="font-size:12px">预定种子 · 多次抽样</span>',260,437,170,57,ORANGE,'#fff8ef')
box('analysis','<b>相同科学分析</b><br><span style="font-size:12px">回归效应 · 残差相关 · 分布</span>',505,437,210,57,BLUE,'#edf3fb')
box('utility','<b>分析用途与限制</b><br><span style="font-size:12px">真实样本参照 · 独立复算</span>',780,437,275,57,BLUE,'#ffffff')
edge('freeze_final','freeze','final',PURPLE)
edge('final_analysis','final','analysis',ORANGE)
edge('analysis_utility','analysis','utility',BLUE)
text('trace','全程留痕：来源原文与版本 · 提示和工具调用 · 模型代码 · 检查与决策 · 运行哈希与种子',28,525,1044,20,12,MUTED)

out=ASSET/'architecture.drawio'
ET.ElementTree(g).write(out, encoding='utf-8', xml_declaration=False)
print(out)

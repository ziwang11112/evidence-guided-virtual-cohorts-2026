"""Editable architecture of the implemented pairing sensitivity experiment."""
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1] / 'manuscript/kdd_draft_v55_2026-11-25'
OUT = PAPER / 'figures/analysis-conditioned-generation.drawio'
NAVY = '#18314D'
BLUE = '#3D6EA8'
ORANGE = '#BA663C'
MUTED = '#5D6A7A'

mxfile = ET.Element('mxfile', host='app.diagrams.net')
diagram = ET.SubElement(mxfile, 'diagram', name='Analysis-specific generation', id='method')
graph = ET.SubElement(diagram, 'mxGraphModel', grid='0', page='0', pageWidth='1660', pageHeight='800', background='#FFFFFF', adaptiveColors='none')
root = ET.SubElement(graph, 'root')
ET.SubElement(root, 'mxCell', id='0')
ET.SubElement(root, 'mxCell', id='1', parent='0')


def node(key, label, x, y, w, h, style=''):
    base = 'html=1;whiteSpace=wrap;fontFamily=Arial;fontSize=24;fontColor='+NAVY+';strokeColor=none;fillColor=none;align=left;verticalAlign=middle;'
    cell = ET.SubElement(root, 'mxCell', id=key, value=label, style=base+style, vertex='1', parent='1')
    ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), attrib={'as':'geometry'})
    return key


def label(key, text, x, y, w, h=35, color=NAVY, size=24, bold=False, align='left'):
    return node(key, text, x,y,w,h, f'fontColor={color};fontSize={size};fontStyle={1 if bold else 0};align={align};')


def box(key, x,y,w,h, fill='#FFFFFF', stroke='#D5DCE5', radius=8):
    return node(key,'',x,y,w,h,f'rounded=1;arcSize={radius};fillColor={fill};strokeColor={stroke};strokeWidth=1.5;')


def edge(key, a,b, color=BLUE, label_text='', style=''):
    cell = ET.SubElement(root,'mxCell', id=key, value=label_text, edge='1', parent='1',source=a,target=b,
        style=f'html=1;edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=block;endFill=1;strokeColor={color};strokeWidth=2.3;fontFamily=Arial;fontSize=20;fontColor={MUTED};labelBackgroundColor=#FFFFFF;'+style)
    ET.SubElement(cell,'mxGeometry', relative='1', attrib={'as':'geometry'})


def line(key,a,b,color=BLUE):
    edge(key,a,b,color,style='edgeStyle=none;endArrow=none;strokeWidth=2.2;')


def pairing(prefix, y, permutation, color):
    label(prefix+'x','X values',685,y-38,110,30,size=22,align='center')
    label(prefix+'y','Y values',855,y-38,110,30,size=22,align='center')
    for i in range(4):
        a=node(prefix+'x'+str(i),str(i+1),714,y+i*28,45,24,f'rounded=1;arcSize=20;align=center;fontSize=18;fillColor=#E4EDF7;fontColor={BLUE};')
        b=node(prefix+'y'+str(i),str(i+1),886,y+i*28,45,24,f'rounded=1;arcSize=20;align=center;fontSize=18;fillColor=#F7E9E0;fontColor={ORANGE};')
    for i,j in enumerate(permutation):
        line(prefix+'link'+str(i),prefix+'x'+str(i),prefix+'y'+str(j),color)


# Three regions separate the user's contract, the two authored programs and the evaluator.
label('input-title','Research inputs',20,12,285,42,size=29,bold=True)
label('agent-title','Scientific agent',355,12,640,42,size=29,bold=True)
label('eval-title','Independent execution &amp; checks',1100,12,540,42,size=29,bold=True)

box('inputs',20,75,285,575,fill='#F5F7FA')
label('request-title','Research question',43,97,235,35,size=24,bold=True)
label('request','Who crosses a<br>screening threshold?',43,144,235,75,size=25)
label('request-meta','Population<br>Measurements + units',43,235,235,70,size=22,color=MUTED)

box('source-card',43,334,235,125,fill='#FFFFFF')
label('source-title','Original article',60,345,200,32,size=23,bold=True)
for i,width in enumerate([165,135,175]):
    node('article-line'+str(i),'',60,391+i*17,width,4,'fillColor=#CED8E4;')
label('contract','Registered test',43,489,235,34,size=23,bold=True)
label('contract-values','Columns + strata<br>Source checks<br>Useful-change margin',43,532,240,95,size=23,color=MUTED)

box('author-region',345,75,700,575,fill='#F0F5FB',stroke='#CDDCEC')
box('initial',370,105,650,220,stroke='#BCCFE5')
label('initial-title','Author the first program',392,119,590,38,size=25,bold=True)
label('initial-actions','Extract reported values<br>Choose a pairing law<br>Write executable code',392,174,252,109,size=23)
pairing('a',200,[0,1,2,3],BLUE)

box('alternative',370,414,650,212,fill='#FFFAF6',stroke='#DFC2AD')
label('alternative-title','Construct a consequential alternative',392,426,595,37,size=25,bold=True,color='#96502D')
label('alternative-actions','Same column values<br>Same source constraints<br>Another pairing program',392,481,257,108,size=23)
pairing('b',505,[2,0,3,1],ORANGE)
edge('initial-to-alternative','initial','alternative',color=ORANGE,label_text='Initial code + same article + requested analysis')
edge('input-to-author','inputs','initial')

box('verifier',1095,75,545,282,fill='#F5F7FA')
label('freeze','Freeze both programs',1117,93,490,36,size=25,bold=True)
label('isolation','Isolated runs · three common seeds',1117,137,490,34,size=23,color=MUTED)
node('sep-check','',1117,184,499,2,'fillColor=#D5DCE5;')
label('check-title','Recompute from the generated rows',1117,201,490,34,size=23,bold=True)
label('check-items','Exact columns and valid pairing<br>Published statistics and physical ordering',1117,246,493,72,size=23)
edge('initial-to-check','initial','verifier')
node('check-junction','',1064,264,5,5,'shape=ellipse;fillColor='+ORANGE+';')
edge('alternative-to-check','alternative','check-junction',color=ORANGE,style='endArrow=none;')
edge('alternative-check-entry','check-junction','verifier',color=ORANGE)

box('analysis',1095,410,545,240,fill='#FFFFFF',stroke='#AABBCF')
label('analysis-title','Run the same scientific analysis',1117,429,490,36,size=25,bold=True)
box('estimate-a',1117,485,233,58,fill='#EAF1F9',stroke='#C2D2E5')
label('estimate-a-text','Estimate A',1124,496,219,35,size=25,bold=True,color=BLUE,align='center')
box('estimate-b',1383,485,233,58,fill='#FAEDE4',stroke='#DFC2AD')
label('estimate-b-text','Estimate B',1390,496,219,35,size=25,bold=True,color=ORANGE,align='center')
label('analysis-decision','Does the change exceed the<br>prespecified scientific margin?',1117,565,490,65,size=24)
edge('check-to-analysis','verifier','analysis',label_text='Both pass source checks')

box('deliverable',345,703,700,83,fill='#FFFFFF',stroke='#CDDCEC')
label('deliverable-text','Authored programs + provenance<br>Source values, derivations and assumptions',365,711,660,65,size=23)
edge('authored-deliverables','alternative','deliverable',color=ORANGE)
box('validation',1095,703,545,83,fill='#F5F7FA')
label('validation-text','Measured-data validation<br>Same estimator after model freeze',1117,712,500,63,size=23)
edge('analysis-to-validation','analysis','validation',color=MUTED,style='dashed=1;')
label('scope','Pairing schematic',670,650,350,30,size=19,color=MUTED,align='right')
label('footer-input','Investigator-defined test conditions',20,671,290,60,size=21,color=MUTED)

OUT.parent.mkdir(parents=True,exist_ok=True)
ET.indent(mxfile)
ET.ElementTree(mxfile).write(OUT,encoding='utf-8',xml_declaration=True)
print(OUT)

# A second editable figure shows the broader whole-record construction interface.
mxfile = ET.Element('mxfile', host='app.diagrams.net')
diagram = ET.SubElement(mxfile,'diagram',name='Evidence to analyzable records',id='system')
graph = ET.SubElement(diagram,'mxGraphModel',grid='0',page='0',pageWidth='1660',pageHeight='580',background='#FFFFFF',adaptiveColors='none')
root = ET.SubElement(graph,'root')
ET.SubElement(root,'mxCell',id='0')
ET.SubElement(root,'mxCell',id='1',parent='0')
label('input-title','Research inputs',20,12,285,42,size=29,bold=True)
label('model-title','Agent-authored scientific model',355,12,700,42,size=29,bold=True)
label('output-title','Execution and scientific use',1110,12,535,42,size=29,bold=True)

box('inputs',20,75,285,448,fill='#F5F7FA')
label('request-title','Requested analysis',40,95,250,35,size=24,bold=True)
label('request-items','Population<br>Measurements + units<br>Intended estimator',40,142,250,108,size=23)
node('input-divider','',40,270,245,2,'fillColor=#D5DCE5;')
label('source-title','Published evidence',40,291,250,35,size=24,bold=True)
label('source-items','Article or retrieved<br>scientific sources',40,335,250,70,size=23)
label('observations','Observed variables<br>when available',40,442,250,67,size=22,color=MUTED)

box('model',345,75,710,448,fill='#F0F5FB',stroke='#CDDCEC')
label('align','Read each statistic in its study context',365,93,668,36,size=25,bold=True)
label('context','Population · measurement · adjustment · scale',365,135,668,34,size=22,color=MUTED)

box('marginal',365,194,202,184,stroke='#BCCFE5')
label('marginal-title','Distributions',380,207,175,32,size=23,bold=True)
for i,h in enumerate([15,35,61,77,61,35,15]):
    node('hist'+str(i),'',388+i*22,335-h,16,h,f'fillColor={BLUE};')
label('marginal-detail','Shape + variation',375,340,182,29,size=20,align='center')

box('dependence',587,194,230,184,stroke='#BCCFE5')
label('dependence-title','Joint structure',602,207,200,32,size=23,bold=True)
node('age','Age',666,250,70,36,'rounded=1;arcSize=20;fillColor=#E2EBF7;fontSize=20;align=center;')
node('x','X',611,309,60,36,'rounded=1;arcSize=20;fillColor=#E2EBF7;fontSize=20;align=center;')
node('y','Y',734,309,60,36,'rounded=1;arcSize=20;fillColor=#F7E9E0;fontSize=20;align=center;')
edge('age-x','age','x',style='edgeStyle=none;strokeWidth=1.7;')
edge('age-y','age','y',style='edgeStyle=none;strokeWidth=1.7;')
edge('x-y','x','y',color=ORANGE,style='edgeStyle=none;strokeWidth=1.7;')

box('parameters',837,194,198,184,stroke='#BCCFE5')
label('parameter-title','Parameters',847,207,180,32,size=22,bold=True)
label('parameter-lines','Source values<br>Derivations<br>Assumptions',849,253,177,106,size=21)

box('sampler',365,415,670,85,fill='#FFFFFF',stroke='#AABBCF')
label('sampler-text','Executable sampling program + provenance<br>Reported, derived and assumed quantities',385,425,630,65,size=24)
edge('inputs-model','inputs','model')

box('executor',1105,75,535,448,fill='#F5F7FA')
label('executor-title','Run the authored program',1127,93,490,36,size=25,bold=True)
label('execution','Isolation · schema · seeds · output records',1127,135,490,34,size=22,color=MUTED)
box('table',1145,197,455,134,fill='#FFFFFF',stroke='#CBD5E2')
label('table-title','Virtual individual measurements',1157,207,427,30,size=23,bold=True)
for i in range(3):
    for j in range(6):
        node('data'+str(i)+'-'+str(j),'',1161+j*68,251+i*23,54,11,'fillColor='+(['#B7CDE4','#D6E2EF','#E5BEA7'][j%3])+';')
label('table-note','Schematic rows',1405,335,196,27,size=18,color=MUTED,align='right')
box('source-check',1127,386,222,115,fill='#FFFFFF',stroke='#CBD5E2')
label('source-check-text','Replay selected<br>source statistics',1140,406,196,68,size=24)
box('analysis',1370,386,248,115,fill='#FFFFFF',stroke='#CBD5E2')
label('analysis-text','Run the requested<br>scientific analysis',1382,406,225,68,size=24)
edge('program-execution','model','executor')
label('optional-questions','Model choices shown schematically',355,535,660,30,size=20,color=MUTED)
label('reference','Measured reference evaluated after model freeze',1105,535,535,32,size=21,color=MUTED)

OUT = PAPER/'figures/evidence-to-analysis-system.drawio'
ET.indent(mxfile)
ET.ElementTree(mxfile).write(OUT,encoding='utf-8',xml_declaration=True)
print(OUT)

"""Native draw.io mechanism figure, grounded in the closed 4 November case.

Draw.io exports embed this original XML. Placeholder table cells are not records.
The highlighted matrix entries are actual Agent-authored values; see trace audit.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
C = dict(ink='#182647', blue='#4169B1', violet='#8264B5', coral='#D97762',
         slate='#778394', line='#CCD3E1', pb='#F1F5FC', pv='#F5F2FA', pc='#FCF2ED', white='#FFFFFF')
model = ET.Element('mxGraphModel', dict(dx='1260', dy='600', grid='1', gridSize='10',
    page='0', pageScale='1', math='0', shadow='0', adaptiveColors='none'))
root = ET.SubElement(model, 'root')
ET.SubElement(root,'mxCell',id='0'); ET.SubElement(root,'mxCell',id='1',parent='0')

def box(k,t,x,y,w,h,fill='white',stroke='line',size=22,extra=''):
    style=('rounded=0;whiteSpace=wrap;html=1;fontFamily=Arial;align=center;verticalAlign=middle;'
           f'fontSize={size};fontColor={C["ink"]};strokeWidth=1.4;spacing=4;'
           f'fillColor={C.get(fill,fill)};strokeColor={C.get(stroke,stroke)};'+extra)
    a=ET.SubElement(root,'mxCell',id=k,value=t,style=style,vertex='1',parent='1')
    ET.SubElement(a,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})

def txt(k,t,x,y,w,h,size=22,color='ink',extra=''):
    box(k,t,x,y,w,h,'none','none',size,f'align=left;spacing=0;fontColor={C.get(color,color)};'+extra)

def edge(k,s,t,color='slate',arrow=True,dashed=False):
    a=ET.SubElement(root,'mxCell',id=k,source=s,target=t,parent='1',edge='1',style=(
        'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;'
        f'strokeColor={C[color]};endArrow={"block" if arrow else "none"};endFill=1;'
        + ('dashed=1;dashPattern=5 4;' if dashed else '')))
    ET.SubElement(a,'mxGeometry',relative='1',attrib={'as':'geometry'})

def route(k,pts,color='slate',dashed=False):
    for i,(x,y) in enumerate(pts): box(f'{k}p{i}','',x-.1,y-.1,.2,.2,'none','none',1)
    for i in range(len(pts)-1): edge(f'{k}e{i}',f'{k}p{i}',f'{k}p{i+1}',color,i==len(pts)-2,dashed)

def rule(k,x,y,w,color='line'): box(k,'',x,y,w,1.4,color,'none',1)

def paper(k,x,y):
    box(k,'',x,y,38,48,'white','blue')
    for j,w in enumerate([25,25,19]): rule(k+str(j),x+7,y+13+j*10,w,'blue')

def robot(x,y):
    box('bot','',x,y,40,30,'pv','violet',extra='rounded=1;arcSize=30;')
    box('eye1','',x+8,y+9,5,5,'violet','none',extra='ellipse;')
    box('eye2','',x+27,y+9,5,5,'violet','none',extra='ellipse;')
    rule('mouth',x+12,y+22,17,'violet')
    box('ant','',x+19,y-8,2,8,'violet','none')

# No title banner: panel headings and the manuscript caption carry the context.
txt('a','<b>a</b>  Request and evidence',10,10,320,34,25)
txt('b','<b>b</b>  Agent-authored model',365,10,500,34,25)
txt('c','<b>c</b>  Execution and use',925,10,330,34,25)
rule('ar',10,51,310);rule('br',365,51,505);rule('cr',925,51,320)

box('request','Chinese adults, 35–74<br><b>Age · Sex · BMI · Glucose · HbA1c</b>',10,70,310,85,'pb','none',21)
paper('p1',28,185); paper('p2',48,199);paper('p3',68,213)
txt('search','Search → review',125,202,195,30,22)
route('input',[(165,155),(165,180)],'blue')
route('extract',[(165,263),(165,289)],'blue')
box('ev','',10,290,310,155,'white','blue')
txt('evh','Hainan study · male stratum',25,301,280,29,21,'blue')
rule('evr',25,339,280)
txt('evo','Glucose ↔ HbA1c',25,351,280,28,23)
txt('evv','Spearman ρ<sub>s</sub> = <b>0.44</b>',25,391,280,35,25)
txt('evcontext','Unit: 1 · Unadjusted<br>Uncertainty: not reported',10,455,310,48,19,'slate')

# Concrete scientific decisions, represented by an actual numerical conversion.
robot(368,91)
txt('law','Sex-stratified Gaussian copula',425,83,440,45,25,'violet')
box('convert','r<sub>GH</sub> = 2 sin(πρ<sub>s</sub>/6) = <b>0.457</b>',365,153,505,65,'pv','none',27)
route('map',[(320,367),(343,367),(343,185),(365,185)],'blue')
route('toR',[(615,218),(615,245)],'violet')

# Selected entries only: cells without values are deliberately not a full R.
txt('matrix-title','R<sub>male</sub>  (selected entries)',386,246,330,32,22)
labels=['A','B','G','H']; x0=431; y0=318; cell=45
for i,l in enumerate(labels):
    txt('col'+l,l,x0+i*cell,y0-32,cell,28,21,extra='align=center;')
    txt('row'+l,l,x0-40,y0+i*cell,30,cell,21,extra='align=center;')
    for j in range(4):
        fill='white'; value='·'
        if i==j: value='1';fill='pb'
        if (i,j) in [(1,2),(2,1)]:value='.25';fill='pc'
        if (i,j) in [(2,3),(3,2)]:value='.457';fill='pv'
        box(f'r{i}{j}',value,x0+j*cell,y0+i*cell,cell,cell,fill,'line',18)
txt('derived','Derived G–H',645,331,215,29,21,'violet')
txt('assumed','Assumed B–G',645,385,215,29,21,'coral')
txt('spd','R ≻ 0',645,439,210,35,27,'violet')
txt('moment-audit','Finite-moment audit',645,480,215,27,19,'slate')

# Actual sampling mechanics: compact equations correspond to generator.py.
box('sample','',925,70,320,153,'white','blue')
txt('sample-h','Sample with a fixed seed',940,80,290,30,22,'blue')
txt('sample-z','z = ε Cholesky(R)<sup>T</sup>',940,122,290,33,25)
txt('sample-x','x<sub>j</sub> = floor<sub>j</sub> + exp(μ<sub>j</sub> + σ<sub>j</sub>z<sub>j</sub>)',940,172,290,33,21)
route('modelrun',[(870,185),(925,185)],'violet')

headers=['Age','Sex','BMI','G','H']; tw=60; tx=934; ty=268
for j,h in enumerate(headers):
    box('th'+str(j),h,tx+j*tw,ty,tw,32,'pb','line',19)
    for i in range(3):box(f'd{i}{j}','···',tx+j*tw,ty+32+i*28,tw,28,'white','line',20)
route('table',[(1085,223),(1085,262)],'blue')
txt('tablecaption','Whole-cohort virtual table',931,390,310,30,22,'blue')
route('analysis',[(1085,420),(1085,443)],'blue')
txt('models','H ~ BMI + Age + Sex<br>H ~ BMI + G + Age + Sex',925,453,320,60,22)

# Checks return information to the author, not a hand-written target coefficient.
rule('bottomrule',10,536,1235)
box('checks','Statistics · semantic_feedback_v1',690,562,555,43,'pb','none',23)
box('decision','Retain / revise',365,562,250,43,'pv','none',23)
route('runchecks',[(1245,147),(1258,147),(1258,583),(1245,583)],'blue')
route('decide',[(690,583),(615,583)],'violet')
route('revision',[(365,583),(330,583),(330,109),(365,109)],'violet',True)
txt('example','Worked implementation',10,566,310,35,22,'slate')

out=HERE/'fig1-agent-framework.drawio'
ET.ElementTree(model).write(out,encoding='utf-8',xml_declaration=True)
ids=[a.get('id') for a in model.iter('mxCell')]
assert len(ids)==len(set(ids))
print(out)

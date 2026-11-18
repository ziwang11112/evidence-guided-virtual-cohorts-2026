"""Editable draw.io overview: scientific choices, execution and analyzable outputs."""
from pathlib import Path
import xml.etree.ElementTree as E
W=Path(__file__).resolve().parent;P=W.parents[1]
OUT=P/'manuscript/paper_figures_v33_2026-11-17/fig1-request-to-data.drawio'
INK='#25334A';BLUE='#4169AA';PURPLE='#7861AA';COPPER='#BE6D42';GRAY='#7D899B'
mx=E.Element('mxfile',host='app.diagrams.net',type='device')
dia=E.SubElement(mx,'diagram',name='Scientific model authorship',id='overview33')
mod=E.SubElement(dia,'mxGraphModel',dx='1280',dy='660',grid='1',gridSize='10',page='0',pageWidth='1280',pageHeight='660',adaptiveColors='auto')
root=E.SubElement(mod,'root');E.SubElement(root,'mxCell',id='0');E.SubElement(root,'mxCell',id='1',parent='0')
counter=0
def shape(x,y,w,h,label='',fill='#FFFFFF',stroke='#D8DFE9',extra='',size=20,color=INK,bold=False,id=None):
 global counter
 counter+=1; ident=id or f'n{counter}'
 style=f'rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.4;fontFamily=Helvetica;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};spacing=5;'+extra
 c=E.SubElement(root,'mxCell',id=ident,value=label,style=style,vertex='1',parent='1')
 E.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
 return ident
def text(x,y,w,h,label,size=20,color=INK,bold=False,align='left'):
 return shape(x,y,w,h,label,fill='none',stroke='none',extra=f'shape=text;align={align};verticalAlign=middle;',size=size,color=color,bold=bold)
def line(x1,y1,x2,y2,col=GRAY,width=1.5,dash=False):
 global counter
 counter+=1
 c=E.SubElement(root,'mxCell',id=f'l{counter}',style=f'html=1;endArrow=none;strokeColor={col};strokeWidth={width};'+('dashed=1;' if dash else ''),edge='1',parent='1')
 g=E.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
 E.SubElement(g,'mxPoint',x=str(x1),y=str(y1),attrib={'as':'sourcePoint'})
 E.SubElement(g,'mxPoint',x=str(x2),y=str(y2),attrib={'as':'targetPoint'})
def edge(source,target,label='',dash=False,color=BLUE):
 global counter
 counter+=1
 c=E.SubElement(root,'mxCell',id=f'e{counter}',value=label,style=f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;defaultLabelBackgroundColor=page;endArrow=block;endFill=1;strokeColor={color};strokeWidth=2;fontFamily=Helvetica;fontSize=17;fontColor={color};'+('dashed=1;' if dash else ''),edge='1',parent='1',source=source,target=target)
 E.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})

text(15,6,235,42,'01  Request',25,bold=True)
text(275,6,650,42,'02  Scientific model authorship',25,bold=True)
text(1005,6,265,42,'03  Scientific use',25,bold=True)
request=shape(20,135,205,414,fill='#F7F8FB',id='request')
text(35,150,175,35,'Population',21,bold=True)
for x in [58,103,148]:
 shape(x,198,18,18,fill='#CBD4E2',stroke='none',extra='ellipse;')
 shape(x-6,220,30,32,fill='#CBD4E2',stroke='none')
text(35,269,175,30,'Measurements',21,bold=True)
for i,label in enumerate(['Age','BMI','…']):shape(34+i*58,310,51,33,label,fill='#FFFFFF',size=17)
text(35,357,174,54,'Individual records<br>optional',17,color=GRAY)
line(35,432,210,432,'#D8DFE9',1)
text(33,451,178,50,'Intended analyses',20,bold=True)
text(33,499,178,34,'Regression • joint risk',17)

workspace=shape(265,75,700,355,fill='#F5F7FC',stroke='#8AA3C8',id='agent')
text(287,87,620,37,'Scientific Agent',26,color=BLUE,bold=True)
evidence=shape(285,145,200,220,id='evidence')
model=shape(515,145,200,220,id='model')
program=shape(745,145,200,220,id='program')
for x,lab in [(293,'Interpret evidence'),(523,'Compose a joint law'),(753,'Author generator')]:text(x,150,184,37,lab,19,bold=True,align='center')
for j,(tag,color) in enumerate([('Study conditions',BLUE),('Reported statistic',COPPER),('Missing relation',PURPLE)]):
 shape(302+j*3,199+j*43,166,36,tag,fill=['#EEF3FB','#FBF1EA','#F1EDF8'][j],stroke='none',size=17,color=color)
text(297,329,176,25,'Read • compare • derive',16,color=GRAY,align='center')
n1=shape(542,208,43,43,'X₁',fill='#E9EFF9',stroke=BLUE,extra='ellipse;',size=19)
n2=shape(646,208,43,43,'X₂',fill='#E9EFF9',stroke=BLUE,extra='ellipse;',size=19)
n3=shape(594,278,43,43,'Y',fill='#F0EAF7',stroke=PURPLE,extra='ellipse;',size=19)
edge(n1,n3,color=GRAY);edge(n2,n3,color=GRAY);line(586,228,646,228,PURPLE,2,True)
text(530,329,170,25,'Structure + parameters',16,color=GRAY,align='center')
shape(783,203,124,99,fill='#F6F3FA',stroke='#CCBDDF',extra='shape=note;size=15;')
text(798,213,87,34,'Sampler',18,color=PURPLE,bold=True,align='center')
for i,w in enumerate([67,49,58]):shape(804,258+i*11,w,3,fill='#AA96C4',stroke='none')
text(758,329,174,25,'Executable joint model',16,color=GRAY,align='center')
text(283,384,215,26,'Parameter origins',18,color=INK,bold=True)
for x,label,col,bg in [(507,'Reported',BLUE,'#E9EFF9'),(646,'Derived',COPPER,'#F9EDE5'),(785,'Assumed',PURPLE,'#EEE8F6')]:shape(x,381,124,31,label,fill=bg,stroke='none',size=17,color=col)
edge(request,evidence)
edge(evidence,model)
edge(model,program)

table=shape(1005,145,255,220,fill='#F9FAFC',id='table')
text(1016,153,233,33,'Virtual cohort',22,bold=True,align='center')
shape(1025,205,215,30,fill='#DDE6F3',stroke='none',extra='rounded=0;')
for i,lab in enumerate(['ID','X₁','X₂','Y']):text(1027+i*53,205,53,30,lab,16,color=BLUE,bold=True,align='center')
for r in range(3):
 shape(1025,237+r*29,215,27,fill='#FFFFFF' if r%2==0 else '#F0F3F8',stroke='none',extra='rounded=0;')
 for j in range(4):shape(1040+j*52,247+r*29,22,4,fill='#BAC6D9' if j<3 else '#B7A1CF',stroke='none')
text(1017,329,233,26,'Records + model + origins',16,color=GRAY,align='center')
edge(program,table,'run')

analysis=shape(1005,444,255,153,fill='#FFFFFF',stroke='#CABEDB',id='analysis')
text(1017,453,231,35,'Same scientific analysis',20,color=PURPLE,bold=True,align='center')
line(1130,499,1130,570,'#AEB8C6',1,True)
for y,x1,x2,cx,col in [(513,1062,1118,1090,INK),(538,1069,1125,1099,PURPLE),(562,1103,1190,1141,GRAY)]:
 line(x1,y,x2,y,col,2)
 shape(cx-4,y-4,8,8,fill=col,stroke='none',extra='rounded=0;')
text(1189,505,59,25,'Real',13,color=INK)
text(1189,530,61,26,'Virtual',13,color=PURPLE)
edge(table,analysis,'analyze',color=PURPLE)

tools=shape(285,489,660,108,fill='#F7F8FA',stroke='#CDD4DF',id='tools')
text(299,497,160,28,'Numerical tools',18,bold=True)
text(464,497,459,28,'Search / read  ·  Isolated sampling  ·  Checks',17)
text(302,544,620,31,'Available actions: inspect feedback, retain or revise',18,color=GRAY,align='center')
edge(tools,workspace,'tool results',True,GRAY)
text(20,609,1240,32,'Agent decisions are recorded.  Frozen records are evaluated.  A new request may lead to a new model.',20,color=GRAY,align='center')

OUT.write_bytes(E.tostring(mx,encoding='utf-8',xml_declaration=False))
print(OUT)

"""Original evidence-guided Agent framework, native editable draw.io artwork.

Illustrative symbols contain no invented participant values or empirical curves.
The Python writer emits XML; draw.io exports embed that XML into SVG/PDF/PNG.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
COL = dict(navy='#182647', blue='#4169B1', violet='#8264B5', coral='#D97762',
           slate='#778394', line='#CCD3E1', pale_blue='#F1F5FC',
           pale_violet='#F5F2FA', pale_coral='#FCF2ED', white='#FFFFFF')
model=ET.Element('mxGraphModel',dict(dx='1300',dy='720',grid='1',gridSize='10',
    page='0',pageScale='1',math='0',shadow='0',adaptiveColors='none'))
root=ET.SubElement(model,'root')
ET.SubElement(root,'mxCell',{'id':'0'})
ET.SubElement(root,'mxCell',{'id':'1','parent':'0'})

def node(key,label,x,y,w,h,fill='white',stroke='line',size=20,bold=False,extra=''):
    color=lambda c:COL.get(c,c)
    style=('rounded=1;arcSize=10;whiteSpace=wrap;html=1;fontFamily=Arial;'
           f'fontSize={size};fontColor={COL["navy"]};align=center;verticalAlign=middle;'
           f'strokeWidth=1.3;spacing=6;fillColor={color(fill)};strokeColor={color(stroke)};'
           f'fontStyle={1 if bold else 0};'+extra)
    c=ET.SubElement(root,'mxCell',{'id':key,'value':label,'style':style,'vertex':'1','parent':'1'})
    ET.SubElement(c,'mxGeometry',{'x':str(x),'y':str(y),'width':str(w),'height':str(h),'as':'geometry'})
    return key

def text(key,label,x,y,w,h,size=20,bold=False,color='navy',align='left'):
    return node(key,label,x,y,w,h,'none','none',size,bold,
                f'align={align};fontColor={COL.get(color,color)};spacing=0;')

def edge(key,source,target,color='slate',dash=False,label='',arrow='block'):
    c=ET.SubElement(root,'mxCell',{'id':key,'value':label,
        'style':('edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;'
                 f'endArrow={arrow};endFill=1;strokeWidth=2.0;strokeColor={COL[color]};'
                 'fontFamily=Arial;fontSize=18;labelBackgroundColor=#FFFFFF;'
                 f'fontColor={COL[color]};'+('dashed=1;dashPattern=5 4;' if dash else '')),
        'edge':'1','source':source,'target':target,'parent':'1'})
    ET.SubElement(c,'mxGeometry',{'relative':'1','as':'geometry'})

def line(key,x1,y1,x2,y2,color='line',width=1.3):
    # A decorative segment is a narrow rectangle, not a graph connector.
    node(key,'',min(x1,x2),min(y1,y2),max(abs(x2-x1),width),max(abs(y2-y1),width),
         color,'none',extra='rounded=0;')

def routed(key,points,color='slate',dash=False):
    # Invisible connection anchors keep arrows in gutters, never across labels.
    # Each segment is a native mxGraph edge; no special ports or waypoints.
    for i,(x,y) in enumerate(points):
        node(f'{key}-anchor{i}','',x-0.1,y-0.1,.2,.2,'none','none',1)
    for i in range(len(points)-1):
        edge(f'{key}-segment{i}',f'{key}-anchor{i}',f'{key}-anchor{i+1}',color,dash,
             arrow='block' if i==len(points)-2 else 'none')

def document(key,x,y,scale=1):
    node(key,'',x,y,40*scale,50*scale,'white','blue',extra='rounded=0;')
    for j,l in enumerate((25,25,18)):
        line(key+str(j),x+8*scale,y+(14+10*j)*scale,x+(8+l)*scale,y+(14+10*j)*scale,'blue',1.6)

def robot(x,y):
    node('robot-head','',x,y,37,27,'pale_violet','violet',extra='arcSize=25;')
    node('robot-eye1','',x+8,y+8,5,5,'violet','none',extra='ellipse;')
    node('robot-eye2','',x+24,y+8,5,5,'violet','none',extra='ellipse;')
    line('robot-mouth',x+12,y+20,x+26,y+20,'violet',1.5)
    line('robot-antenna',x+19,y-8,x+19,y,'violet',1.5)
    node('robot-tip','',x+16,y-12,6,6,'coral','none',extra='ellipse;')

# Three visual zones; the reference image informs hierarchy, not our mechanism.
text('heading-a','<b>a</b>  Research context',20,12,260,35,25,True)
text('heading-b','<b>b</b>  Scientific Agent',300,12,500,35,25,True)
text('heading-c','<b>c</b>  Data &amp; scientific use',965,12,300,35,25,True)
robot(865,18)
node('left-zone','',20,65,250,585,'pale_violet','none')
node('center-zone','',290,65,650,585,'pale_blue','none')
node('right-zone','',960,65,305,585,'pale_coral','none')

node('request','',36,82,218,143,'white','line')
text('request-title','Research request',50,95,190,28,22,True)
text('request-body','Target population<br>Variables and units<br>Intended analyses',50,133,190,76,20)

node('evidence','',36,247,218,236,'white','line')
document('paper-a',58,266,.82);document('paper-b',81,276,.82);document('paper-c',104,286,.82)
text('source-title','Published<br>studies',149,274,94,55,21,True)
text('source-values','Means &amp; relations<br>Subgroups &amp; models',50,345,190,51,19)
line('evidence-divider',50,403,240,403)
text('source-context','Population &amp; measures<br>Adjustment sets<br>Reported uncertainty',50,413,190,61,17)

node('optional','<b>Optional information</b><br>Observed covariates<br>or permitted summaries',36,507,218,117,'white','line',20)

# Qualify: both curated and retrieved source packets are legitimate inputs.
node('qualify','',310,82,610,143,'white','blue')
node('badge1','1',324,94,30,30,'blue','none',20,True,extra='fontColor=#FFFFFF;ellipse;')
text('q-title','Acquire &amp; qualify evidence',365,93,530,32,23,True)
text('q-left','Use supplied evidence<br>or search missing relations',330,133,265,51,19)
text('q-right','Interpret study conditions<br>Choose each finding\'s role',620,133,275,51,20)
node('reported','Reported',333,190,165,25,'pale_blue','none',17)
node('derived','Derived',520,190,165,25,'pale_violet','none',17)
node('assumed','Assumed',707,190,165,25,'pale_coral','none',17)

# Model: dependency sketch is not a biological causal graph.
node('author','',310,250,610,220,'white','violet')
node('badge2','2',324,262,30,30,'violet','none',20,True,extra='fontColor=#FFFFFF;ellipse;')
text('m-title','Author a joint data model',365,260,530,32,23,True)
text('m-subtitle','Select distributions, dependencies and numerical parameters',330,299,560,28,19)
node('bmi','BMI',337,341,90,40,'pale_violet','violet',18,True)
node('glucose','Glucose',337,410,90,40,'pale_violet','violet',18,True)
node('hba1c','HbA1c',468,375,85,40,'pale_blue','blue',18,True)
edge('b-y','bmi','hba1c','violet',False,arrow='none')
edge('g-y','glucose','hba1c','violet',False,arrow='none')
edge('b-g','bmi','glucose','coral',True,arrow='none')
text('rho-label','Assumed r',338,376,97,26,16,False,'coral')
text('observed-operation','Observed numerical operation',580,339,315,27,19,True)
text('projection-label','Separate adjusted projections',580,371,315,25,19)
text('projection-eq','c<sub>B</sub> = θ<sub>B</sub> + θ<sub>G</sub> r s<sub>G</sub> / s<sub>B</sub>',580,402,315,28,20)
text('projection-note','+ declared covariance → joint coefficients',580,434,315,25,17,False,'violet')

# Execution and author decision are separate roles, not an invented training loss.
node('execute','',310,503,277,122,'white','blue')
node('badge3','3',324,516,30,30,'blue','none',20,True,extra='fontColor=#FFFFFF;ellipse;')
text('execute-title','Execute &amp; inspect',365,515,207,30,22,True)
text('execute-body','Sample virtual records<br>Calculate allowed statistics<br>Check semantics &amp; moments',329,553,239,60,18)
node('review','',632,503,288,122,'white','violet')
node('badge4','4',646,516,30,30,'violet','none',20,True,extra='fontColor=#FFFFFF;ellipse;')
text('review-title','Agent decision',688,515,214,30,22,True)
text('review-body','Inspect model diagnostics<br><b>Retain</b> or <b>revise</b>',650,557,250,55,19)

# Output table schematic uses typographic placeholders, never fabricated values.
node('output','',980,82,265,233,'white','coral')
text('output-title','Virtual data products',996,95,233,32,21,True)
headers=['Age','BMI','Glucose','HbA1c']
for j,label in enumerate(headers):
    x=994+j*59
    node('h'+str(j),label,x,143,59,31,'pale_coral','line',15,True,extra='rounded=0;spacing=0;')
    for k in range(3):
        node(f'cell{j}_{k}','· · ·',x,174+k*25,59,25,'white','line',17,extra='rounded=0;spacing=0;')
text('table-note','Whole cohort / enrichment',995,259,235,25,17,False,'slate')
text('record-note','+ generator &amp; documented<br>evidence / assumptions',995,283,235,30,15,False,'slate')

node('analysis','',980,353,265,130,'white','coral')
text('analysis-title','Scientific analyses',995,365,235,30,22,True)
text('analysis-body','Regression &amp; subgroups<br>Nonlinear effects<br>Longitudinal models',995,406,235,61,18)
node('reference','<b>Evaluation reference</b><br>Real sample / published model',980,529,265,96,'white','line',20)

# Graph arrows summarize implemented roles across explicitly different settings.
routed('request-q',[(254,153),(310,153)])
routed('evidence-q',[(254,300),(281,300),(281,200),(310,200)],'blue')
routed('optional-model',[(254,561),(282,561),(282,440),(310,440)],'slate')
routed('q-model',[(615,225),(615,250)],'blue')
routed('model-execute',[(455,470),(455,503)],'blue')
routed('execute-review',[(587,564),(632,564)],'blue')
routed('review-model',[(780,503),(780,470)],'violet',True)
text('revision-label','optional revision',791,476,126,23,15,False,'violet')
routed('review-data',[(920,563),(950,563),(950,193),(980,193)],'violet')
routed('data-analysis',[(1112,315),(1112,353)],'coral')
routed('reference-analysis',[(1112,529),(1112,483)],'slate')

text('role-note','Agent: scientific decisions    |    Tools: retrieval, calculation &amp; sampling',300,673,660,28,18,False,'slate')
text('legend-dash','Study-qualified evidence',24,673,250,28,17,False,'slate')
text('host-note','Host-dispatched workflow',984,673,260,28,17,False,'slate')

out=HERE/'fig1-agent-framework.drawio'
ET.ElementTree(model).write(out,encoding='utf-8',xml_declaration=True)
ids=[n.get('id') for n in model.iter('mxCell')]
assert len(ids)==len(set(ids))
assert all(n.find('mxGeometry') is not None for n in model.iter('mxCell') if n.get('edge')=='1')
print(out)

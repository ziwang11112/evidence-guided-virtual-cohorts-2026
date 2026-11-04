"""Author the original method schematic as native draw.io XML; no data are read."""
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
model = ET.Element('mxGraphModel', {'dx':'980','dy':'420','grid':'1','gridSize':'10',
    'page':'0','pageScale':'1','math':'0','shadow':'0','adaptiveColors':'auto'})
root = ET.SubElement(model, 'root')
ET.SubElement(root, 'mxCell', {'id':'0'})
ET.SubElement(root, 'mxCell', {'id':'1','parent':'0'})

def box(key, label, x, y, width=140, height=80, fill='#F5F7FA', stroke='#B3BEC9'):
    style = ('rounded=1;arcSize=10;whiteSpace=wrap;html=1;fontFamily=Arial;'
             'fontSize=13;fontColor=#243543;align=center;verticalAlign=middle;'
             f'spacing=8;strokeWidth=1;fillColor={fill};strokeColor={stroke};')
    cell = ET.SubElement(root,'mxCell',{'id':key,'value':label,'style':style,'vertex':'1','parent':'1'})
    ET.SubElement(cell,'mxGeometry',{'x':str(x),'y':str(y),'width':str(width),'height':str(height),'as':'geometry'})

def edge(key, source, target, label='', dashed=False):
    style = ('edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;'
             'endFill=1;strokeWidth=1.4;strokeColor=#687785;fontFamily=Arial;'
             'fontSize=12;fontColor=#465664;labelBackgroundColor=#FFFFFF;')
    if dashed: style += 'dashed=1;dashPattern=4 3;'
    cell = ET.SubElement(root,'mxCell',{'id':key,'value':label,'style':style,
        'edge':'1','source':source,'target':target,'parent':'1'})
    ET.SubElement(cell,'mxGeometry',{'relative':'1','as':'geometry'})

box('papers','<b>Published studies</b><br>Populations<br>Measures and statistics',40,40,height=80)
box('request','<b>Research request and permitted inputs</b><br>Population, variables and intended analyses<br>Optional observations or summaries',220,40,width=320,height=80)
box('reference','<b>Evaluation reference</b><br>Real sample or<br>published model',760,40,height=80,fill='#FBF5EA',stroke='#C9B994')

box('qualify','<b>1. Qualify evidence</b><br>Units / adjustment<br>Applicability',40,160,height=90)
box('author','<b>2. Agent models</b><br>Law + parameters<br>Assumptions',220,160,height=90,fill='#E4F1EF',stroke='#00857D')
box('sample','<b>3. Execute</b><br>Sample from law<br>Inspect statistics',400,160,height=90,fill='#E9F2F8',stroke='#1678A6')
box('data','<b>4. Deliver data</b><br>Virtual table<br>Evidence record',580,160,height=90,fill='#E9F2F8',stroke='#1678A6')
box('analysis','<b>5. Scientific use</b><br>Run analyses<br>Assess utility',760,160,height=90,fill='#FBF5EA',stroke='#C9B994')

box('roles','<b>Evidence status</b><br>Reported / derived / assumed',40,300,width=140,height=60,fill='#FFFFFF')
box('review','<b>Agent reviews</b><br>Retain or revise',400,300,height=60,fill='#E4F1EF',stroke='#00857D')
box('worked','<b>Observed scientific operation</b><br>Separately adjusted study projections<br>converted into joint-model parameters',580,300,width=320,height=60,fill='#FFFFFF')

for args in [('p-q','papers','qualify'),('r-a','request','author'),
             ('q-a','qualify','author'),('a-s','author','sample'),('s-d','sample','data'),
             ('d-e','data','analysis'),('ref-e','reference','analysis')]: edge(*args)
edge('s-review','sample','review','optional',True)
edge('review-author','review','author','',True)
edge('q-roles','qualify','roles')

HERE.mkdir(parents=True,exist_ok=True)
out = HERE/'fig1-method.drawio'
ET.ElementTree(model).write(out,encoding='utf-8',xml_declaration=True)
parsed = ET.parse(out)
ids = [n.attrib['id'] for n in parsed.iter('mxCell')]
assert len(ids)==len(set(ids))
assert all(n.find('mxGeometry') is not None for n in parsed.iter('mxCell') if n.get('edge')=='1')
print(out)

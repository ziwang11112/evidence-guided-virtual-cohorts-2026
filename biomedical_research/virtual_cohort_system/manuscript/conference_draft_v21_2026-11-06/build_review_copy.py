"""Generate the KDD AI for Sciences working copy from the v0.21 manuscript.

All numerical displays are pre-existing figure PDFs. This script copies those
assets, typesets the source Markdown and records their hashes.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
M = HERE.parent
SOURCE = M / 'DRAFT_v0_21.md'
MAIN_STEMS = ['fig1-system-architecture.drawio', 'fig1-agent-method.drawio', 'fig3-iron-utility',
              'fig2-evidence-results', 'fig3-cross-task']
SUPPLEMENT_STEMS = ['fig4-summary-results', 'figS1-open-retrieval',
                    'figS3-dispersion', 'figS4-analysis-use',
                    'figS5-prospective-wave', 'fig2-hrs-comparison']
FILES = MAIN_STEMS + SUPPLEMENT_STEMS
MAIN_TABLES = 2
SUPPLEMENT_TABLES = 7
(HERE / 'figures').mkdir(exist_ok=True)
figure_sources = []

def tex_escape(text):
    replacements = {'\\':r'\textbackslash{}','{':r'\{','}':r'\}',
        '&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_',
        '~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(replacements.get(c,c) for c in text)

def inline(text):
    # Protect inline formatting before escaping ordinary text. Local supporting
    # artifacts remain readable labels; external source links remain clickable.
    tokens = []
    def hold(value):
        tokens.append(value)
        return f'ZZTOKEN{len(tokens)-1}ZZ'
    def code(m): return hold(r'\texttt{'+tex_escape(m.group(1))+'}')
    text=re.sub(r'`([^`]+)`',code,text)
    text=re.sub(r'\$([^$\n]+)\$', lambda m:hold(r'\('+m.group(1)+r'\)'), text)
    def link(m):
        label,url=m.groups()
        if re.match(r'https?://',url):
            return hold(r'\href{'+tex_escape(url)+'}{'+inline(label)+'}')
        return label
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
    text=re.sub(r'\*\*([^*]+)\*\*',lambda m:hold(r'\textbf{'+inline(m.group(1))+'}'),text)
    text=re.sub(r'\*([^*]+)\*',lambda m:hold(r'\emph{'+inline(m.group(1))+'}'),text)
    text=tex_escape(text)
    # Numeric ranges and slash-separated study terms need legal wrap points
    # in the native ACM columns. These controls leave the printed text intact.
    text=re.sub(r'(?<=\w)([–/])(?=\w)',lambda m:m.group(1)+r'\allowbreak{}',text)
    for i,value in reversed(list(enumerate(tokens))):
        text=text.replace(f'ZZTOKEN{i}ZZ',value)
    return text

lines=SOURCE.read_text(encoding='utf-8').splitlines()
title=lines[0].removeprefix('# ')
body=[]
i=1
figure_count=table_count=0
refs=False
supplementary=False
while i<len(lines):
    line=lines[i].strip()
    if (not line or i < 5 and not line.startswith('## ')):
        i+=1;continue
    if line.startswith('## '):
        heading=line[3:]
        if heading=='Supplementary results':
            supplementary=True
            if refs:
                body += [r'\end{enumerate}',r'\endgroup'];refs=False
            body += [r'\clearpage',r'\appendix',r'\section*{Supplementary results}',r'\setcounter{figure}{0}',r'\renewcommand{\thefigure}{S\arabic{figure}}',r'\setcounter{table}{0}',r'\renewcommand{\thetable}{S\arabic{table}}']
        elif heading=='References':
            body += [r'\clearpage',r'\section*{References}',r'\begingroup',r'\begin{enumerate}']
            refs=True
        elif heading=='Supporting materials and reproducibility':
            body += [r'\section*{'+inline(heading)+'}']
        elif heading=='Abstract':
            body.append(r'\begin{abstract}')
            i+=1
            while i<len(lines) and not lines[i].startswith('## '):
                if lines[i].strip():body.append(inline(lines[i]))
                i+=1
            body += [r'\end{abstract}', r'\maketitle']
            continue
        else:
            heading=re.sub(r'^\d+\.\s*','',heading)
            body.append(r'\section{'+inline(heading)+'}')
        i+=1;continue
    if line.startswith('### '):
        heading=re.sub(r'^\d+\.\d+\.\s*','',line[4:])
        body.append((r'\subsection*{' if supplementary else r'\subsection{')+inline(heading)+'}')
        i+=1;continue
    if line=='$$':
        if not supplementary:
            raise ValueError('The case-specific regression derivation belongs in the supplement.')
        block=[];i+=1
        while i<len(lines) and lines[i].strip()!='$$':
            block.append(lines[i]);i+=1
        if not block or i==len(lines):
            raise ValueError('Incomplete display mathematics in the manuscript.')
        body.append('\n'.join([r'\[',*block,r'\]']))
        i+=1;continue
    if line.startswith('```'):
        raise ValueError('Use prose for the method and display mathematics for the worked example.')
    if re.match(r'\*\*Table (?:S)?\d+\.',line):
        caption=line
        table_count+=1
        display_id = ('S'+str(table_count-MAIN_TABLES)) if supplementary else str(table_count)
        if not line.startswith('**Table '+display_id+'.'):
            raise ValueError(f'Expected caption Table {display_id}; received {line[:60]}')
        caption=re.sub(r'^\*\*Table (?:S)?\d+\.\s*','',caption)
        caption=caption.replace('**','')
        i+=1
        while i<len(lines) and not lines[i].strip():i+=1
        rows=[]
        while i<len(lines) and lines[i].lstrip().startswith('|'):
            cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[:\- ]+',c) for c in cells): rows.append(cells)
            i+=1
        assert rows and all(len(x)==len(rows[0]) for x in rows)
        n=len(rows[0])
        # A full-width table is a display choice, not a numerical transformation.
        spec='@{}'+''.join('>{\\raggedright\\arraybackslash}X' for _ in range(n))+'@{}'
        if display_id == '1' and n == 2:
            spec=r'@{}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}X@{}'
        table_env='table*'
        table_placement='tp'
        body += [r'\begin{'+table_env+'}['+table_placement+']',r'\caption{'+inline(caption)+'}',r'\label{tab:'+str(table_count)+'}',
                 r'\centering\small',
                 r'\renewcommand{\arraystretch}{1.12}',r'\begin{tabularx}{\textwidth}{'+spec+'}',r'\toprule']
        for j,row in enumerate(rows):
            body.append(' & '.join(inline(c) for c in row)+r' \\')
            if j==0:body.append(r'\midrule')
        body += [r'\bottomrule',r'\end{tabularx}',r'\end{'+table_env+'}']
        continue
    match=re.match(r'!\[([^\]]*)\]\(([^)]+)\)',line)
    if match:
        figure_count+=1
        figure_path = Path(match.group(2)).with_suffix('.pdf')
        fname = figure_path.name
        expected = FILES[figure_count - 1] + '.pdf'
        if fname != expected:
            raise ValueError(f'Figure {figure_count}: expected {expected}, found {fname}')
        source_pdf = M / figure_path
        expected_directory = {1:'paper_figures_v21_2026-11-06', 2:'paper_figures_v20_2026-11-06', 3:'paper_figures_v19_2026-11-06'}.get(figure_count)
        if expected_directory and figure_path.parent.name != expected_directory:
            raise ValueError(f'Figure {figure_count} must use {expected_directory}, found {figure_path}')
        if not source_pdf.exists():
            raise FileNotFoundError(source_pdf)
        shutil.copyfile(source_pdf, HERE/'figures'/fname)
        figure_sources.append(source_pdf)
        assert (HERE/'figures'/fname).exists(),fname
        i+=1
        while i<len(lines) and not lines[i].strip():i+=1
        cap=lines[i].strip()
        assert re.match(r'\*\*Figure (?:S)?\d+\.',cap),cap
        display_id = str(figure_count) if figure_count<=len(MAIN_STEMS) else 'S'+str(figure_count-len(MAIN_STEMS))
        if not cap.startswith('**Figure '+display_id+'.'):
            raise ValueError(f'Expected caption Figure {display_id}; received {cap[:50]}')
        cap=re.sub(r'^\*\*Figure (?:S)?\d+\.\s*','',cap).replace('**','')
        figure_width = r'0.93\textwidth' if figure_count in (10,11) else r'\textwidth'
        figure_env='figure*'
        figure_placement='tp'
        body += [r'\begin{'+figure_env+'}['+figure_placement+']',r'\centering',
                 r'\includegraphics[width='+figure_width+r']{figures/'+fname+'}',
                 r'\caption{'+inline(cap)+'}',r'\Description{'+inline(match.group(1))+'}',r'\label{fig:'+str(figure_count)+'}',r'\end{'+figure_env+'}']
        i+=1;continue
    if refs:
        assert re.match(r'^\d+\. ',line),line
        body.append(r'\item '+inline(re.sub(r'^\d+\. ','',line)))
    else:
        body.append(inline(line)+'\n')
    i+=1
if refs:body += [r'\end{enumerate}',r'\endgroup']
assert figure_count==len(FILES) and table_count==MAIN_TABLES+SUPPLEMENT_TABLES


# Submit wide displays in reading order before the columns in which they are
# discussed. The ACM class can otherwise hold the final two figures until
# the end of the main body even when preceding pages have space.
def section_anchor(n):
    lines=[i for i,v in enumerate(body) if v.startswith(r'\section{')]
    return lines[n-1]

for stem in MAIN_STEMS:
    image = next(j for j,v in enumerate(body) if 'figures/'+stem+'.pdf' in v)
    start = max(j for j in range(image) if body[j].startswith(r'\begin{figure*}'))
    end = next(j for j in range(image,len(body)) if body[j] == r'\end{figure*}')+1
    position=FILES.index(stem)
    if position==0:
        anchor=section_anchor(1)
    elif position==1:
        anchor=section_anchor(3)
    elif position==2:
        anchor=section_anchor(4)
    elif position==3:
        anchor=section_anchor(5)
    else:
        results=section_anchor(5)
        subheadings=[j for j in range(results,start) if body[j].startswith(r'\subsection{')]
        anchor=subheadings[1] if len(subheadings)>1 else results
    if anchor >= start:
        continue
    block = body[start:end]
    del body[start:end]
    body[anchor:anchor] = block

design_cap = next(j for j,v in enumerate(body) if v==r'\label{tab:2}')
design_start = max(j for j in range(design_cap) if body[j].startswith(r'\begin{table*}'))
design_end = next(j for j in range(design_cap,len(body)) if body[j]==r'\end{table*}')+1
design_anchor = max(j for j in range(section_anchor(3),section_anchor(4)) if body[j].startswith(r'\subsection{'))
design_block = body[design_start:design_end]
del body[design_start:design_end]
body[design_anchor:design_anchor] = design_block

preamble=r'''\PassOptionsToClass{balance=false}{acmart}
\documentclass[sigconf,review]{acmart}
\settopmatter{printacmref=false}
\setcopyright{none}
\acmDOI{}
\acmISBN{}
\acmConference[KDD AI for Sciences working draft]{KDD AI for Sciences working draft}{}{}
\renewcommand\footnotetextcopyrightpermission[1]{}
\usepackage{tabularx}
\usepackage{amsmath}
\emergencystretch=1.5em
\begin{document}
\title{TITLE}
\author{Author details pending confirmation}
\affiliation{\institution{Affiliation pending confirmation}\city{ }\country{ }}
\ccsdesc[500]{Computing methodologies~Modeling and simulation}
\ccsdesc[300]{Applied computing~Life and medical sciences}
\keywords{Synthetic cohorts, biomedical evidence, scientific agents, epidemiology}
'''.replace('TITLE',inline(title))
tex = preamble+'\n\n'.join(body)+'\n\\end{document}\n'
blocked_identifiers = ('D:/AIR-', 'D:\\AIR-')
if any(identifier.lower() in tex.lower() for identifier in blocked_identifiers):
    raise ValueError('A source identity or workspace path reached the review TeX')
(HERE/'paper.tex').write_text(tex,encoding='utf-8')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
manifest = {
    'source_markdown': SOURCE.name, 'source_sha256': digest(SOURCE),
    'format': 'acmart [sigconf,review], single-blind layout with authorship placeholder',
    'figures': [{'source': str(p.relative_to(M)).replace('\\','/'),
                 'file': p.name, 'sha256':digest(p)} for p in figure_sources],
    'figure_count':figure_count, 'table_count':table_count,
    'main_figure_count':len(MAIN_STEMS), 'supplementary_figure_count':len(SUPPLEMENT_STEMS), 'main_table_count':MAIN_TABLES,
    'supplementary_table_count':table_count-MAIN_TABLES, 'new_patient_analysis':False,
    'review_copy':'Retain research text and public links. Author metadata require confirmation.',
    'local_supporting_links':'Rendered as labels, with the cited artifacts accessible in the full Markdown.',
    'source_tex_sha256':digest(HERE/'paper.tex'),
}
(HERE/'BUILD_INPUTS.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(HERE/'overleaf_v21.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
    for p in [HERE/'paper.tex', HERE/'OVERLEAF_README.md',
              *(HERE/'figures'/(stem+'.pdf') for stem in FILES)]:
        archive.write(p,p.relative_to(HERE).as_posix())
print(f'Built {figure_count} figures and {table_count} tables from {SOURCE.name}.')

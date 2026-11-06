"""Generate the anonymous ACM review copy from the v0.17 editorial source.

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
SOURCE = M / 'DRAFT_v0_17.md'
FILES = ['fig1-agent-framework.drawio', 'fig2-hrs-comparison', 'fig3-cross-task',
         'fig2-evidence-results', 'fig4-summary-results', 'figS1-open-retrieval',
         'figS3-dispersion', 'figS4-analysis-use', 'figS5-prospective-wave']
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
    if (not line or line.startswith(('Working conference-style draft', 'Working conference draft', 'Working manuscript', 'Conference-style', 'Conference manuscript'))):
        i+=1;continue
    # The research Markdown retains public access details and release notes.
    if line.startswith('The [public repository]'):
        line = "The supplementary results preserve the study designs, estimators, source inventories, implementation incidents and numerical audits."
    if re.search(r'author[/,].*funding.*declar', line, flags=re.I):
        line = re.split(r'(?i)(?:author/affiliation|author, affiliation|author and affiliation)',line)[0].strip()
        if not line:
            i += 1
            continue
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
    if line.startswith('```'):
        block=[];i+=1
        while i<len(lines) and not lines[i].startswith('```'):
            block.append(lines[i]);i+=1
        body += [r'\noindent\begin{minipage}{\columnwidth}',r'\begin{lstlisting}',*block,r'\end{lstlisting}',r'\end{minipage}']
        i+=1;continue
    if re.match(r'\*\*Table (?:S)?\d+\.',line):
        caption=line
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
        n=len(rows[0]); table_count+=1
        # A full-width table is a display choice, not a numerical transformation.
        spec='@{}'+''.join('>{\\raggedright\\arraybackslash}X' for _ in range(n))+'@{}'
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
        if not source_pdf.exists():
            raise FileNotFoundError(source_pdf)
        shutil.copyfile(source_pdf, HERE/'figures'/fname)
        figure_sources.append(source_pdf)
        assert (HERE/'figures'/fname).exists(),fname
        i+=1
        while i<len(lines) and not lines[i].strip():i+=1
        cap=lines[i].strip()
        assert re.match(r'\*\*Figure (?:S)?\d+\.',cap),cap
        cap=re.sub(r'^\*\*Figure (?:S)?\d+\.\s*','',cap).replace('**','')
        figure_width = r'\textwidth'
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
assert figure_count==9 and table_count==8


# Put each wide main figure into the float queue at the start of its section.
# The section titles are allowed to change with the editorial source.
for stem in FILES[:4]:
    image = next(j for j,v in enumerate(body) if 'figures/'+stem+'.pdf' in v)
    start = max(j for j in range(image) if body[j].startswith(r'\begin{figure*}'))
    end = next(j for j in range(image,len(body)) if body[j] == r'\end{figure*}')+1
    if stem == FILES[0]:
        anchor = max(j for j in range(start) if body[j].startswith(r'\section{'))
    else:
        anchor = max(j for j in range(start) if body[j].startswith(r'\subsection{'))
    block = body[start:end]
    del body[start:end]
    body[anchor:anchor] = block

preamble=r'''\documentclass[sigconf,anonymous,review]{acmart}
\settopmatter{printacmref=false}
\setcopyright{none}
\acmDOI{}
\acmISBN{}
\acmConference[KDD review draft]{KDD review draft}{}{}
\renewcommand\footnotetextcopyrightpermission[1]{}
\usepackage{tabularx}
\usepackage{listings}
\emergencystretch=1.5em
\lstset{basicstyle=\ttfamily\small,breaklines=true,columns=fullflexible,keepspaces=true,showstringspaces=false}
\begin{document}
\title{TITLE}
\author{Anonymous Author(s)}
\ccsdesc[500]{Computing methodologies~Modeling and simulation}
\ccsdesc[300]{Applied computing~Life and medical sciences}
\keywords{Synthetic cohorts, biomedical evidence, scientific agents, longitudinal reconstruction}
'''.replace('TITLE',inline(title))
tex = preamble+'\n\n'.join(body)+'\n\\end{document}\n'
blocked_identifiers = ('ziwang11112','evidence-guided-virtual-cohorts-2026',
                       'DRAFT_v0_', 'D:/AIR-', 'D:\\AIR-')
if any(identifier.lower() in tex.lower() for identifier in blocked_identifiers):
    raise ValueError('A source identity or workspace path reached the review TeX')
(HERE/'paper.tex').write_text(tex,encoding='utf-8')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
manifest = {
    'source_markdown': SOURCE.name, 'source_sha256': digest(SOURCE),
    'format': 'acmart [sigconf, anonymous, review]; two-column body and appendix',
    'figures': [{'source': str(p.relative_to(M)).replace('\\','/'),
                 'file': p.name, 'sha256':digest(p)} for p in figure_sources],
    'figure_count':figure_count, 'table_count':table_count,
    'main_figure_count':4, 'supplementary_figure_count':5, 'main_table_count':1,
    'supplementary_table_count':7, 'new_data_analysis':False,
    'review_copy':'Omit identifying project links and internal publication-status prose; retain scientific statements and external citations.',
    'local_supporting_links':'Rendered as labels, with the cited artifacts accessible in the full Markdown.',
    'source_tex_sha256':digest(HERE/'paper.tex'),
}
(HERE/'BUILD_INPUTS.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(HERE/'overleaf_v17.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
    for p in [HERE/'paper.tex', HERE/'OVERLEAF_README.md',
              *(HERE/'figures'/(stem+'.pdf') for stem in FILES)]:
        archive.write(p,p.relative_to(HERE).as_posix())
print(f'Built {figure_count} figures and {table_count} tables from {SOURCE.name}.')

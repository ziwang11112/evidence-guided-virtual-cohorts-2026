"""Build a two-column LaTeX reading copy from the reviewed Markdown draft.

This is an article-class reading format, not an official conference template.
Only prose and existing original figure PDFs are consumed; no data analysis.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil

HERE = Path(__file__).resolve().parent
M = HERE.parent
SOURCE = M/'DRAFT_v0_11.md'
FIGDIR = M/'visual_redesign_v11_2026-11-04'
FILES = ['fig1-agent-framework.drawio','fig2-evidence-results','fig3-summary-results',
         'fig4-longitudinal-use','fig5-analysis-use']
HERE.mkdir(parents=True,exist_ok=True)
(HERE/'figures').mkdir(exist_ok=True)
for stem in FILES:
    shutil.copyfile(FIGDIR/(stem+'.pdf'),HERE/'figures'/(stem+'.pdf'))

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
    for i,value in reversed(list(enumerate(tokens))):
        text=text.replace(f'ZZTOKEN{i}ZZ',value)
    return text

lines=SOURCE.read_text(encoding='utf-8').splitlines()
title=lines[0].removeprefix('# ')
body=[]
i=1
figure_count=table_count=0
refs=False
while i<len(lines):
    line=lines[i].strip()
    if not line or line.startswith('Working conference-style draft'):
        i+=1;continue
    if line.startswith('## '):
        heading=line[3:]
        if heading=='References':
            body += [r'\clearpage',r'\section*{References}',r'\begingroup\small',r'\begin{enumerate}',r'\setlength{\itemsep}{3pt}']
            refs=True
        elif heading=='Abstract':
            body.append(r'\begin{abstract}')
            i+=1
            while i<len(lines) and not lines[i].startswith('## '):
                if lines[i].strip():body.append(inline(lines[i]))
                i+=1
            body.append(r'\end{abstract}')
            continue
        else:
            heading=re.sub(r'^\d+\.\s*','',heading)
            body.append(r'\section{'+inline(heading)+'}')
        i+=1;continue
    if line.startswith('### '):
        heading=re.sub(r'^\d+\.\d+\.\s*','',line[4:])
        body.append(r'\subsection{'+inline(heading)+'}')
        i+=1;continue
    if line.startswith('```'):
        block=[];i+=1
        while i<len(lines) and not lines[i].startswith('```'):
            block.append(lines[i]);i+=1
        body += [r'\begin{lstlisting}',*block,r'\end{lstlisting}']
        i+=1;continue
    if re.match(r'\*\*Table \d+\.',line):
        caption=line
        caption=re.sub(r'^\*\*Table \d+\.\s*','',caption)
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
        body += [r'\begin{table*}[t]',r'\caption{'+inline(caption)+'}',r'\label{tab:'+str(table_count)+'}',
                 r'\centering\fontsize{8}{9.5}\selectfont',r'\setlength{\tabcolsep}{4pt}',
                 r'\renewcommand{\arraystretch}{1.12}',r'\begin{tabularx}{\textwidth}{'+spec+'}',r'\toprule']
        for j,row in enumerate(rows):
            body.append(' & '.join(inline(c) for c in row)+r' \\')
            if j==0:body.append(r'\midrule')
        body += [r'\bottomrule',r'\end{tabularx}',r'\end{table*}']
        continue
    match=re.match(r'!\[([^\]]*)\]\(([^)]+)\)',line)
    if match:
        figure_count+=1
        fname=Path(match.group(2)).name.removesuffix('.svg')+'.pdf'
        assert (HERE/'figures'/fname).exists(),fname
        i+=1
        while i<len(lines) and not lines[i].strip():i+=1
        cap=lines[i].strip()
        assert re.match(r'\*\*Figure \d+\.',cap),cap
        cap=re.sub(r'^\*\*Figure \d+\.\s*','',cap).replace('**','')
        figure_width = r'0.92\textwidth' if figure_count == 5 else r'\textwidth'
        body += [r'\begin{figure*}[t]',r'\centering',
                 r'\includegraphics[width='+figure_width+r']{figures/'+fname+'}',
                 r'\caption{'+inline(cap)+'}',r'\label{fig:'+str(figure_count)+'}',r'\end{figure*}']
        i+=1;continue
    if refs:
        assert re.match(r'^\d+\. ',line),line
        body.append(r'\item '+inline(re.sub(r'^\d+\. ','',line)))
    else:
        body.append(inline(line)+'\n')
    i+=1
if refs:body += [r'\end{enumerate}',r'\endgroup']
assert figure_count==5 and table_count==3

preamble=r'''\documentclass[10pt,twocolumn]{article}
\pdfvariable minorversion=7
\usepackage[letterpaper,margin=0.72in,columnsep=0.24in]{geometry}
\usepackage{fontspec}
\IfFontExistsTF{Times New Roman}{\setmainfont{Times New Roman}}{\setmainfont{TeX Gyre Termes}}
\IfFontExistsTF{Arial}{\setsansfont{Arial}}{\setsansfont{TeX Gyre Heros}}
\IfFontExistsTF{Courier New}{\setmonofont{Courier New}}{\setmonofont{TeX Gyre Cursor}}
\usepackage{graphicx,booktabs,tabularx,array,caption,listings}
\usepackage[colorlinks=true,linkcolor=black,urlcolor=blue,citecolor=black]{hyperref}
\captionsetup{font=small,labelfont=bf,skip=5pt}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,columns=fullflexible,
  keepspaces=true,showstringspaces=false,frame=single,framerule=0.2pt,xleftmargin=2pt,xrightmargin=2pt}
\raggedbottom
\setlength{\parindent}{1em}
\setlength{\parskip}{0pt}
\setlength{\textfloatsep}{10pt plus 2pt minus 2pt}
\setlength{\dbltextfloatsep}{10pt plus 2pt minus 2pt}
\renewcommand{\topfraction}{0.95}
\renewcommand{\dbltopfraction}{0.95}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.75}
\renewcommand{\dblfloatpagefraction}{0.75}
\setcounter{dbltopnumber}{2}
\emergencystretch=1.5em
\title{TITLE}
\author{\small Working research draft --- 4 November 2026}
\date{}
\begin{document}
\maketitle
\begingroup\footnotesize\noindent This is a two-column reading copy, not an official conference submission format.\par\endgroup
'''.replace('TITLE',inline(title))
(HERE/'paper.tex').write_text(preamble+'\n\n'.join(body)+'\n\\end{document}\n',encoding='utf-8')
manifest={'source_markdown':str(SOURCE.relative_to(M)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'format':'two-column article-class reading copy; not official venue formatting',
          'figures':[{ 'name':stem+'.pdf','sha256':hashlib.sha256((HERE/'figures'/(stem+'.pdf')).read_bytes()).hexdigest()} for stem in FILES],
          'figure_count':figure_count,'table_count':table_count,'new_data_analysis':False,
          'local_supporting_links_in_pdf':'displayed as labels; source Markdown retains clickable artifact links',
          'source_tex_sha256':hashlib.sha256((HERE/'paper.tex').read_bytes()).hexdigest()}
(HERE/'BUILD_INPUTS.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'figures':figure_count,'tables':table_count,'tex':str(HERE/'paper.tex')}))

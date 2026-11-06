"""Generate the single-column methods development edition from the v0.24 manuscript.

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
SOURCE = M / 'DRAFT_v0_24.md'
MAIN_STEMS = ['fig1-agent-loop.drawio', 'fig1-agent-method.drawio', 'fig3-iron-utility',
              'fig2-evidence-results', 'fig3-cross-task']
SUPPLEMENT_STEMS = ['fig4-summary-results', 'figS1-open-retrieval',
                    'figS3-dispersion', 'figS4-analysis-use',
                    'figS5-prospective-wave', 'fig2-hrs-comparison']
FILES = MAIN_STEMS + SUPPLEMENT_STEMS
MAIN_TABLES = 3
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
    text=re.sub(r'(?<=\w)([–/])(?=[\w−-])',lambda m:m.group(1)+r'\allowbreak{}',text)
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
            body += [r'\FloatBarrier',r'\appendix',r'\section*{Supplementary results}',r'\setcounter{figure}{0}',r'\renewcommand{\thefigure}{S\arabic{figure}}',r'\setcounter{table}{0}',r'\renewcommand{\thetable}{S\arabic{table}}']
        elif heading=='References':
            body += [r'\clearpage',r'\section*{References}',r'\begingroup',r'\begin{enumerate}[label=\arabic*.,leftmargin=2.1em,itemsep=.2em,parsep=0pt]']
            refs=True
        elif heading=='Supporting materials and reproducibility':
            body += [r'\section*{'+inline(heading)+'}']
        elif heading=='Abstract':
            body.append(r'\begin{abstract}')
            i+=1
            while i<len(lines) and not lines[i].startswith('## '):
                if lines[i].strip():body.append(inline(lines[i]))
                i+=1
            body += [r'\end{abstract}']
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
        # A breakable table keeps each caption with the necessary rows. The
        # headers repeat on following pages in the long supplementary tables.
        spec='@{}'+''.join('>{\\raggedright\\arraybackslash}X' for _ in range(n))+'@{}'
        if display_id in ('1','2') and n==2:
            width='0.26' if display_id=='1' else '0.40'
            spec=r'@{}>{\raggedright\arraybackslash}p{'+width+r'\linewidth}>{\raggedright\arraybackslash}X@{}'
        if n>=5:
            # Analysis names are longer than the numeric columns.
            weights = [1.35] + [(n-1.35)/(n-1)]*(n-1)
            spec='@{}'+''.join(r'>{\hsize='+f'{w:.6f}'+r'\hsize\linewidth=\hsize\raggedright\arraybackslash}X' for w in weights)+'@{}'
        table_id = 'tab:' + str(table_count)
        header = ' & '.join(r'\textbf{'+inline(value)+'}' for value in rows[0])+r' \\'
        body += [r'\begingroup',r'\small',r'\renewcommand{\arraystretch}{1.22}',
                 r'\begin{xltabular}{\linewidth}{'+spec+'}',
                 r'\caption{'+inline(caption)+'}'+r'\label{'+table_id+r'} \\',
                 r'\toprule',header,r'\midrule',r'\endfirsthead',
                 r'\multicolumn{'+str(n)+r'}{l}{\small Table \thetable\ continued}\\',
                 r'\toprule',header,r'\midrule',r'\endhead',
                 r'\bottomrule',r'\endfoot']
        body.extend(' & '.join(inline(c) for c in row)+r' \\' for row in rows[1:])
        body += [r'\end{xltabular}',r'\endgroup']
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
        expected_directory = {1:'paper_figures_v24_2026-11-06', 2:'paper_figures_v20_2026-11-06', 3:'paper_figures_v19_2026-11-06'}.get(figure_count)
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
        figure_width = r'\linewidth'
        figure_env='figure'
        figure_placement='htbp'
        body += [r'\begin{'+figure_env+'}['+figure_placement+']',r'\centering',
                 r'\includegraphics[width='+figure_width+r']{figures/'+fname+'}',
                 r'\caption{'+inline(cap)+'}',r'\label{fig:'+str(figure_count)+'}',r'\end{'+figure_env+'}']
        i+=1;continue
    if refs:
        assert re.match(r'^\d+\. ',line),line
        body.append(r'\item '+inline(re.sub(r'^\d+\. ','',line)))
    else:
        body.append(inline(line)+'\n')
    i+=1
if refs:body += [r'\end{enumerate}',r'\endgroup']
assert figure_count==len(FILES) and table_count==MAIN_TABLES+SUPPLEMENT_TABLES


preamble=r'''\documentclass[11pt,letterpaper]{article}
\usepackage[left=0.91in,right=0.91in,top=0.92in,bottom=0.95in,headheight=14pt,headsep=15pt]{geometry}
\usepackage{fontspec}
\usepackage{libertinus}
\usepackage{microtype,graphicx,amsmath,array,booktabs,xltabular}
\usepackage{caption}
\usepackage[section]{placeins}
\usepackage{titlesec,enumitem,fancyhdr}
\usepackage[dvipsnames]{xcolor}
\definecolor{ink}{HTML}{253044}
\definecolor{accent}{HTML}{43537C}
\usepackage[unicode,colorlinks=true,urlcolor=accent,linkcolor=accent]{hyperref}
\hypersetup{pdftitle={TITLE}, pdfauthor={}}
\setcounter{secnumdepth}{2}
\titleformat{\section}{\sffamily\Large\bfseries\color{ink}}{\thesection}{.65em}{}
\titleformat{\subsection}{\sffamily\large\bfseries\color{ink}}{\thesubsection}{.65em}{}
\titlespacing*{\section}{0pt}{2.2ex plus .4ex minus .1ex}{.9ex}
\titlespacing*{\subsection}{0pt}{1.7ex plus .3ex minus .1ex}{.6ex}
\captionsetup{font=small,labelfont={bf,color=ink},labelsep=period,justification=raggedright,singlelinecheck=false}
\setlength{\parindent}{0pt}
\setlength{\parskip}{.45em plus .08em minus .03em}
\setlength{\LTpre}{.9em}
\setlength{\LTpost}{.9em}
\setlength{\LTcapwidth}{\textwidth}
\setlength{\textfloatsep}{16pt plus 4pt minus 2pt}
\setlength{\intextsep}{12pt plus 3pt minus 1pt}
\setcounter{topnumber}{3}
\renewcommand\topfraction{.85}
\renewcommand\bottomfraction{.7}
\renewcommand\textfraction{.12}
\renewcommand\floatpagefraction{.68}
\renewenvironment{abstract}{\small\par\noindent{\sffamily\bfseries\color{ink}Abstract}\quad\ignorespaces}{\par\medskip}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\sffamily\color{accent}Evidence-guided virtual cohorts}
\fancyhead[R]{\small\sffamily\color{accent}Methods development draft}
\fancyfoot[R]{\small\sffamily\thepage}
\renewcommand\headrulewidth{0.25pt}
\raggedbottom
\emergencystretch=1em
\begin{document}
\thispagestyle{plain}
{\sffamily\footnotesize\color{accent}\bfseries METHODS DEVELOPMENT DRAFT\quad\textbar\quad NOVEMBER 2026\par}
\vspace{.7em}
{\raggedright\sffamily\bfseries\fontsize{24}{29}\selectfont\color{ink}TITLE\par}
\vspace{.5em}
{\small Author and affiliation details pending confirmation\par}
\vspace{.7em}
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
    'format': 'article [11pt,letterpaper], single-column methods development edition',
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
with zipfile.ZipFile(HERE/'overleaf_v24.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
    for p in [HERE/'paper.tex', HERE/'OVERLEAF_README.md',
              *(HERE/'figures'/(stem+'.pdf') for stem in FILES)]:
        archive.write(p,p.relative_to(HERE).as_posix())
print(f'Built {figure_count} figures and {table_count} tables from {SOURCE.name}.')

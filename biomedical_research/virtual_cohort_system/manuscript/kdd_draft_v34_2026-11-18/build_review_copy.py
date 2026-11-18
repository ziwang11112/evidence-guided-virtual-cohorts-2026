from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
M = HERE.parent
SOURCE = M / 'DRAFT_v0_34.md'
main_text, appendix_text = SOURCE.read_text(encoding="utf-8").split("## Supplementary results", 1)
def stems(text):
    paths = re.findall(r"^!\[[^\]]*\]\(([^)]+)\)", text, re.M)
    return [Path(p).stem for p in paths]
MAIN_STEMS, SUPPLEMENT_STEMS = stems(main_text), stems(appendix_text)
FILES = MAIN_STEMS + SUPPLEMENT_STEMS
MAIN_TABLES = len(re.findall(r"^\*\*Table \d+\.", main_text, re.M))
SUPPLEMENT_TABLES = len(re.findall(r"^\*\*Table S\d+\.", appendix_text, re.M))
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
    def code(m):
        escaped = tex_escape(m.group(1))
        for sep in [r'\_', '/', '-']:
            escaped = escaped.replace(sep, sep+r'\allowbreak{}')
        return hold(r'\texttt{'+escaped+'}')
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
            body += [r'\clearpage',r'\onecolumn',r'\raggedbottom',r'\appendix',r'\section*{Supplementary results}',r'\setcounter{figure}{0}',r'\renewcommand{\theHfigure}{S\arabic{figure}}',r'\renewcommand{\thefigure}{S\arabic{figure}}',r'\setcounter{table}{0}',r'\renewcommand{\theHtable}{S\arabic{table}}',r'\renewcommand{\thetable}{S\arabic{table}}']
        elif heading=='References':
            body += [r'\FloatBarrier',r'\section*{References}',r'\begingroup\small',r'\renewcommand{\labelenumi}{[\arabic{enumi}]}',r'\begin{enumerate}\setlength{\itemsep}{.12em}']
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
        if supplementary:
            body.append(r'\Needspace{8\baselineskip}')
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
        if display_id == '1' and n == 3:
            spec=r'@{}>{\raggedright\arraybackslash}Xrr@{}'
        if display_id == '1' and n == 2:
            spec=r'@{}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}X@{}'
        table_env='table' 
        table_placement='H' if supplementary else 't' 
        body += [r'\begin{'+table_env+'}['+table_placement+']',r'\caption{'+inline(caption)+'}',r'\label{tab:'+str(table_count)+'}',
                 r'\centering\small',
                 r'\renewcommand{\arraystretch}{1.12}',r'\begin{tabularx}{\linewidth}{'+spec+'}',r'\toprule']
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
        display_id = str(figure_count) if figure_count<=len(MAIN_STEMS) else 'S'+str(figure_count-len(MAIN_STEMS))
        if not cap.startswith('**Figure '+display_id+'.'):
            raise ValueError(f'Expected caption Figure {display_id}; received {cap[:50]}')
        cap=re.sub(r'^\*\*Figure (?:S)?\d+\.\s*','',cap).replace('**','')
        figure_width = r'0.88\textwidth' if supplementary else r'\textwidth' 
        figure_env='figure' if supplementary else 'figure*' 
        figure_placement='H' if supplementary else 't' 
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



def queue_wide_float(label, section):
    marker = next(i for i,v in enumerate(body) if v == label)
    start = next(i for i in range(marker, -1, -1) if body[i].startswith((r'\begin{figure*}', r'\begin{table*}')))
    end = next(i for i in range(marker,len(body)) if body[i] in (r'\end{figure*}', r'\end{table*}')) + 1
    block = body[start:end]
    del body[start:end]
    target = body.index(section)
    body[target:target] = block

queue_wide_float(r'\label{fig:2}', r'\section{Can the Agent build the model from an original paper?}')
queue_wide_float(r'\label{fig:3}', r'\section{What changes when only the data change?}')


preamble=r'''\PassOptionsToClass{balance=false}{acmart}
\documentclass[sigconf,anonymous,nonacm]{acmart}
\settopmatter{printacmref=false,printfolios=true}
\setcopyright{none}
\acmDOI{}
\acmISBN{}
\acmConference[KDD working manuscript]{KDD working manuscript}{}{}
\renewcommand\footnotetextcopyrightpermission[1]{}
\usepackage{tabularx,float,placeins,needspace}
\usepackage{amsmath}
\emergencystretch=1.5em
\begin{document}
\title{TITLE}
\author{Anonymous author(s)}
\affiliation{\institution{Anonymous institution}\country{}}
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
    'format': 'ACM sigconf, anonymous KDD working edition with one-column supplement',
    'figures': [{'source': str(p.resolve().relative_to(M.parent)).replace('\\','/'),
                 'file': p.name, 'sha256':digest(p)} for p in figure_sources],
    'figure_count':figure_count, 'table_count':table_count,
    'main_figure_count':len(MAIN_STEMS), 'supplementary_figure_count':len(SUPPLEMENT_STEMS), 'main_table_count':MAIN_TABLES,
    'supplementary_table_count':table_count-MAIN_TABLES, 'new_patient_analysis':False,
    'review_copy':'Retain research text and public links. Author metadata require confirmation.',
    'local_supporting_links':'Rendered as labels, with the cited artifacts accessible in the full Markdown.',
    'source_tex_sha256':digest(HERE/'paper.tex'),
}
(HERE/'BUILD_INPUTS.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(HERE/'overleaf_v34.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
    for p in [HERE/'paper.tex', HERE/'OVERLEAF_README.md',
              *(HERE/'figures'/(stem+'.pdf') for stem in FILES)]:
        archive.write(p,p.relative_to(HERE).as_posix())
print(f'Built {figure_count} figures and {table_count} tables from {SOURCE.name}.')

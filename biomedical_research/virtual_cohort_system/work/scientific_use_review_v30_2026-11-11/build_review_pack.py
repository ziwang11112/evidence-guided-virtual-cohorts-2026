"""Build an aggregate-only, four-page biomedical collaborator packet.

Reads audited estimates, not patient or synthetic individual records. Never runs a
generator, fits a reference, invokes a model, or sends the packet to a person.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import zipfile
from xml.sax.saxutils import escape

import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
OUT = PROJECT / 'deliverables/Biomedical_Use_Review_v30_2026-11-11'
PDF = OUT / '01_REVIEW_BRIEF.pdf'
ZIP = OUT.with_suffix('.zip')
INK = colors.HexColor('#243247')
BLUE = colors.HexColor('#356C9E')
PURPLE = colors.HexColor('#8064A6')
PALE = colors.HexColor('#F1F4F8')
GRAY = colors.HexColor('#58677B')
RULE = colors.HexColor('#CFD7E3')

sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    audit_path = HERE / 'NUMERICAL_USE_AUDIT.json'
    audit = json.loads(audit_path.read_text(encoding='utf8'))
    assert audit['status'] == 'pass' and not audit['issues']
    for rel, expected in audit['input_hashes'].items():
        assert sha(PROJECT / rel) == expected, rel
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'optional').mkdir(exist_ok=True)
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')
    styles = {
        'title': ParagraphStyle('title', fontName='Arial-Bold', fontSize=23, leading=28, textColor=INK, spaceAfter=14),
        'h1': ParagraphStyle('h1', fontName='Arial-Bold', fontSize=17, leading=21, textColor=INK, spaceAfter=11),
        'h2': ParagraphStyle('h2', fontName='Arial-Bold', fontSize=11, leading=15, textColor=BLUE, spaceBefore=10, spaceAfter=6),
        'body': ParagraphStyle('body', fontName='Arial', fontSize=9.7, leading=14.2, textColor=INK, spaceAfter=8),
        'small': ParagraphStyle('small', fontName='Arial', fontSize=8.1, leading=11.5, textColor=GRAY, spaceAfter=7),
        'cell': ParagraphStyle('cell', fontName='Arial', fontSize=8.2, leading=11, textColor=INK),
        'header': ParagraphStyle('header', fontName='Arial-Bold', fontSize=8.2, leading=11, textColor=INK),
        'kicker': ParagraphStyle('kicker', fontName='Arial-Bold', fontSize=9, leading=12, textColor=BLUE, spaceAfter=10),
    }
    story = []
    def p(text, style='body'):
        story.append(Paragraph(text, styles[style]))
    def table(rows, widths, ref_last=False):
        converted = [[Paragraph(escape(str(c)), styles['header' if i == 0 else 'cell']) for c in row]
                     for i, row in enumerate(rows)]
        t = Table(converted, colWidths=widths, repeatRows=1, hAlign='LEFT')
        commands = [('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PALE),
                    ('LINEBELOW',(0,0),(-1,0),0.6,RULE),('LINEBELOW',(0,-1),(-1,-1),0.6,RULE),
                    ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                    ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]
        if ref_last:
            commands.append(('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#FFF4E9')))
        t.setStyle(TableStyle(commands))
        story.extend([t, Spacer(1,9)])
    records = audit['summary_records']
    index = {(r['author'], r['analysis_id']): r for r in records}
    def r(author, endpoint): return index[(author, endpoint)]
    def m(author, endpoint): return r(author,endpoint)['mean']
    def rf(author, endpoint): return r(author,endpoint)['reference']['value']
    def f(x, n=3): return 'not available' if x is None else f'{x:.{n}f}'
    def interval(author,endpoint):
        item = r(author,endpoint)['reference'].get('interval', {})
        if item.get('lower') is None or item.get('upper') is None:
            return f(rf(author,endpoint))
        return f'{f(rf(author,endpoint))} [{f(item["lower"])}, {f(item["upper"])}]'
    def meanrange(author,endpoint):
        item = r(author,endpoint)
        return f'{f(item["mean"])} [{f(item["minimum"])}, {f(item["maximum"])}]'

    p('BIOMEDICAL COLLABORATOR REVIEW  |  11 NOVEMBER 2026', 'kicker')
    p('Which scientific uses do these virtual data support?', 'title')
    p('A short review of two completed examples accompanying manuscript v0.30. The question is whether the generated data are useful for <b>specified exploratory analyses</b>, and what restrictions a biomedical researcher should know.')
    p('What the method does', 'h2')
    p('A researcher specifies a population, variables and intended analyses. An Agent finds published studies, chooses a joint statistical model, writes a sampling program and records the sources and assumptions. Numerical tools generate the fictional records and apply the requested analyses. The examples here use <b>no target individual-level training records</b>.')
    p('What we would like you to judge', 'h2')
    table([
        ['Case', 'Why it is included', 'What to assess'],
        ['A. Glycemia\nTwo constructions', 'A recurring BMI-coefficient change when glucose is added to the analysis.', 'Is the association interpretation useful? What does the reduced HbA1c spread limit?'],
        ['B. Paired lipids\nSix constructions', 'A complete set of generated associations with weaker joint dependence and HDL spread.', 'Which exploratory uses remain informative, and which require better joint information?'],
    ], [104,190,198])
    p('These complementary cases were chosen for interpretation, not to estimate a project-wide success rate. Every constructor and primary analysis within each case is retained. Later repairs are shown separately; they are not new independent constructions.')
    p('How to read the comparisons', 'h2')
    p('Real-sample estimates are uncertain references, not known population values. Generated entries summarize three draws from each fixed generator. Their ranges are <b>not confidence intervals</b>. Both reference contexts were already exposed during project development. Numerical agreement alone does not certify a use, and a mismatch can matter differently for different uses.')
    p('Please read pages 2-4, then fill in <b>02_REVIEW_FORM.md</b>. No coding is required. The optional full manuscript supplies additional context. There is no preferred positive answer or requested numerical acceptance threshold.')
    p('Prepared from existing aggregate results with AI assistance. No external biomedical feedback has yet been collected. This packet contains no real or generated individual records, full third-party papers, credentials or internal reviewer answers.', 'small')
    story.append(PageBreak())

    p('CASE A  |  GLYCEMIA', 'kicker')
    p('A reproducible adjustment pattern, with incomplete variation', 'h1')
    p('<b>Target context.</b> The comparison uses 6,931 selected ENSANUT 2018 participants aged 25-79, no reported previous diabetes diagnosis, an 8-12-hour recorded fast and fasting serum glucose below 126 mg/dL. The analysis assigns equal mass to eight age/sex cells; it is not a national population estimate. Medication and anemia exclusions were not verified. Generated cohorts contain 3,000 fictional individuals per draw.')
    p('<b>Intended use.</b> Explore age/BMI associations with HbA1c and how adding glucose changes the BMI coefficient in the same data. A coefficient change is an associational result; it does not establish causal mediation or a direct biological effect.')
    rows = [['Analysis and adjustment', 'Real-sample reference [band]', 'E01 mean [draw range]', 'E02 mean [draw range]']]
    for ep, label in [('Q1_age10','Age: sex, BMI, glucose\nHbA1c pp per 10 years'),
                      ('Q2_bmi5','BMI: age, sex\nHbA1c pp per 5 kg/m2'),
                      ('Q3_bmi5','BMI: age, sex, glucose\nHbA1c pp per 5 kg/m2')]:
        rows.append([label,interval('E01',ep),meanrange('E01',ep),meanrange('E02',ep)])
    table(rows,[153,119,110,110])
    p('pp = HbA1c percentage points. Reference brackets are the saved empirical cluster-resampling stability bands, not equivalence margins. Generated brackets span three seed estimates. These are six tables from two laws, not six independent clinical cohorts.', 'small')
    p('The useful observed pattern', 'h2')
    p(f'Adding glucose reduces the mean BMI coefficient from <b>{f(m("E01","Q2_bmi5"),5)} to {f(m("E01","Q3_bmi5"),5)}</b> for E01 and from <b>{f(m("E02","Q2_bmi5"),5)} to {f(m("E02","Q3_bmi5"),5)}</b> for E02. All six generated tables retain this attenuation. Both conditional age coefficients are higher than the real-sample point estimate.')
    p('The same data have lower HbA1c variation', 'h2')
    table([
        ['Diagnostic, HbA1c pp', 'Sample reference', 'E01', 'E02'],
        ['Total HbA1c SD',f(rf('E01','hba1c.sd_population')),f(m('E01','hba1c.sd_population')),f(m('E02','hba1c.sd_population'))],
        ['Adjusted residual RMS',f(rf('E01','q1_residual_rms')),f(m('E01','q1_residual_rms')),f(m('E02','q1_residual_rms'))],
    ], [210,100,91,91])
    p('<b>Interpretation to review:</b> these data can illustrate the specified conditional-association pattern. The observed spread discrepancy does not establish calibrated power calculations, prediction intervals, individual heterogeneity or diagnostic thresholds. Those uses need separate assessment.')
    p('Source context matters: both authors used Taiwanese HbA1c evidence whose age range, fasting and adjustment conditions differ from this selected Mexican analysis. Those bridges remain explicit assumptions. Selected source and methodological links are in 03_CONTEXT_AND_SOURCES.md.', 'small')
    story.append(PageBreak())

    p('CASE B  |  PAIRED LIPIDS', 'kicker')
    p('Complete analyses reveal where joint information is weak', 'h1')
    p('<b>Target context.</b> Adults aged at least 18 in the Turkana 2018-2019 study context; demographic and lifestyle mixture was left for the Agent to specify. The 397-person complete-case sample is a project-defined reference. Original methods measured TC and HDL using EDTA venous blood and CardioChek Plus; nonfasting participants were retained. The source study included different lifestyle settings.')
    p('<b>Intended use.</b> Explore age/sex-adjusted BMI associations with total cholesterol (TC) and HDL, and the Pearson correlation of the two residuals after adjustment for age, sex and BMI. All six authors and all primary analyses are retained below.')
    author_order = [f'LIPID_{a}_R{i}' for a in ('BASE','WORKFLOW') for i in (1,2,3)]
    endpoints = ['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL','total_cholesterol.sd_sample','hdl_cholesterol.sd_sample']
    rows = [['Constructor','TC slope','HDL slope','Residual r','TC SD','HDL SD']]
    for author in author_order:
        label = author.replace('LIPID_BASE_R','Ordinary ').replace('LIPID_WORKFLOW_R','Workflow ')
        rows.append([label,*[f(m(author,e)) for e in endpoints]])
    rows.append(['Sample reference',*[f(rf(author_order[0],e)) for e in endpoints]])
    table(rows,[122,74,74,74,74,74], ref_last=True)
    p('Entries are three-draw means. Slopes: mg/dL per 5 kg/m2 BMI. SD: mg/dL. r: dimensionless. The exact means, draw ranges and reference bands are in 04_ANALYSIS_ESTIMATES.csv. Ordinary and workflow are both Agent implementations, not real versus synthetic data.', 'small')
    p('What the complete profiles show', 'h2')
    p('All six generated means have weaker residual TC-HDL dependence and lower HDL SD than the sample reference. Their positive TC point slopes do not establish a known population direction: the reference slope interval includes zero. These observations matter for studying the two lipids jointly, even when each regression can be computed.')
    unstable = r('LIPID_WORKFLOW_R2','K02-HDL-BMI')
    p('Workflow 2 illustrates instability near zero. Its three HDL slopes are <b>'+', '.join(f(x,4) for x in unstable['values'])+f'</b>, averaging <b>{f(unstable["mean"],4)}</b>. A negative average therefore does not mean every generated draw preserves the reference direction.')
    p('Measured endpoints and model consistency', 'h2')
    p('A model that sets TC = HDL + positive non-HDL enforces ordering within an ideal concentration model. It does not itself specify assay error or the covariance of measured outputs. One retained workflow law produced a single HDL-above-TC row; no row was removed. Whether such a construction is appropriate depends on the intended measured endpoint.')
    p('Ordinary 2 also had a mathematical tail defect in its initial ideal law despite finite saved tables. Both completed repairs are shown on the next page. Initial profiles must not be mistaken for the current unrepaired state of that law.', 'small')
    story.append(PageBreak())

    p('FOLLOW-UP AND REVIEW DECISIONS', 'kicker')
    p('What the completed repair changed', 'h1')
    p('The same Ordinary 2 lipid law was reviewed independently under ordinary and structured checking policies. Both repaired its divergent ideal TC moments. These two branches depend on one starting law; they are not additional independent constructors. Neither repair was selected because it was closer to the real reference.')
    rows = [['Version','TC slope','HDL slope','Residual r','TC SD','HDL SD']]
    for author,label in [('LIPID_BASE_R2','Initial Ordinary 2'),('R04_GENERIC','Ordinary review'),('R04_STRUCTURED','Structured review')]:
        rows.append([label,*[f(m(author,e)) for e in endpoints]])
    rows.append(['Sample reference',*[f(rf('LIPID_BASE_R2',e)) for e in endpoints]])
    table(rows,[122,74,74,74,74,74],ref_last=True)
    p('The TC coefficient moves closer to the reference point, residual dependence is essentially unchanged, and dispersion agreement does not improve. Mathematical validity and scientific usefulness are separate properties. The full paired study preserves all other retained laws and results in manuscript Section 5.11/S23.')
    p('Five questions for your biomedical judgment', 'h2')
    questions = [
        '<b>Use:</b> For each of the six requested analyses, would you use the virtual data for the stated exploratory purpose, restrict the use, decline, or need more information?',
        '<b>Biology and measurement:</b> What population, fasting, assay, treatment or adjustment assumption most changes that decision?',
        '<b>Variation:</b> Which use remains informative despite the reported dispersion/dependence mismatch, and which does not?',
        '<b>Wording:</b> Which manuscript conclusion overstates the scientific support, and how would you rewrite it?',
        '<b>Next evidence:</b> What single addition would change your judgment? Is it necessary, optional, or unnecessary for the proposed use?',
    ]
    for i,q in enumerate(questions,1): p(f'{i}. {q}')
    p('Please return the blank form or annotate this brief. Name any author-specific exception. No human response has been filled in, and negative or uncertain judgments will be retained. This is qualitative collaborator interpretation, not a scored experiment or a clinical-validity certificate.', 'small')
    p('Sources and reproducibility', 'h2')
    p('The packet contains exact aggregate estimates, primary/methods source links and an optional unchanged v0.30 reading draft. The source hash manifest supports document integrity. All patient-level and generated individual records, complete third-party articles, raw API logs and internal review keys remain outside this packet.', 'small')

    def decorate(canvas, doc):
        canvas.setTitle('Biomedical scientific-use review - v0.30')
        canvas.setAuthor('Research team - reviewer preparation')
        canvas.setStrokeColor(RULE)
        canvas.line(54,42,558,42)
        canvas.setFont('Arial',7.6); canvas.setFillColor(GRAY)
        canvas.drawString(54,29,'Aggregate-only collaborator brief | No external biomedical response collected')
        canvas.drawRightString(558,29,f'{doc.page} / 4')
    doc = SimpleDocTemplate(str(PDF), pagesize=(612,792), leftMargin=60,rightMargin=60,
                            topMargin=48,bottomMargin=55)
    doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
    with fitz.open(PDF) as rendered:
        assert len(rendered) == 4, f'Expected four pages; got {len(rendered)}'
        text = '\n'.join(page.get_text() for page in rendered)
        assert '\ufffd' not in text
        (HERE / 'BRIEF_EXTRACTED_TEXT.txt').write_text(text,encoding='utf8')

    shutil.copyfile(HERE / 'REVIEWER_QUESTIONS.md',OUT / '02_REVIEW_FORM.md')
    with (OUT / '04_ANALYSIS_ESTIMATES.csv').open('w',encoding='utf8',newline='') as stream:
        fields = ['study','constructor','analysis_id','role','unit','mean','draw_min','draw_max','draws',
                  'sample_reference','reference_lower','reference_upper','reference_interpretation',
                  'reference_uncertainty_status','reference_uncertainty_reason']
        writer = csv.DictWriter(stream,fieldnames=fields); writer.writeheader()
        for item in records:
            reference = item.get('reference') or {}
            band = reference.get('interval') or reference.get('uncertainty') or {}
            band_status = band.get('status', 'unavailable')
            band_reason = band.get('reason') or ''
            if band_status == 'unavailable':
                band_interpretation = 'Uncertainty unavailable: ' + (band_reason or 'not supplied')
            else:
                band_interpretation = band.get('meaning') or band.get('kind') or reference.get('interpretation','')
            writer.writerow(dict(zip(fields,[item['study'],item['author'],item['analysis_id'],item['role'],item['unit'],
                item['mean'],item['minimum'],item['maximum'],len(item['values']),reference.get('value',''),
                band.get('lower',''),band.get('upper',''),band_interpretation,band_status,band_reason])))
    with (OUT / '05_BLANK_ANALYSIS_DECISIONS.csv').open('w',encoding='utf8',newline='') as stream:
        writer = csv.writer(stream); writer.writerow(['case','analysis','decision','author_specific_exception','reason_or_restriction'])
        for case,ids in [('A glycemia',['Age-HbA1c adjusted for sex/BMI/glucose','BMI-HbA1c adjusted for age/sex','BMI-HbA1c additionally adjusted for glucose']),
                         ('B lipids',['BMI-TC adjusted for age/sex','BMI-HDL adjusted for age/sex','TC-HDL residual dependence'])]:
            for a in ids: writer.writerow([case,a,'','',''])
    context = '''# Context, sources and inspection limits

This packet asks for qualitative biomedical interpretation of two deliberately complementary existing cases. It is not a clinical validation study or a blinded comparison. All constructors and requested analyses within each selected case are retained. No response has been collected and no one was contacted during preparation.

## Source context

- [Huang et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8038122/): a source used by both glycemia constructors. The reviewed Methods and Table 1 concern Taiwanese participants aged 30-70, nonuniversal fasting and age/sex adjustment. Transfer to the selected Mexican analysis adds assumptions. This source does not supply its fully adjusted target coefficients.
- [Schisterman, Cole and Platt](https://pmc.ncbi.nlm.nih.gov/articles/PMC2744485/): methodological context for adjustment and intermediates. Coefficient attenuation alone is not causal mediation. No causal graph for this project is established by this citation.
- [Lea et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/) and [original supplement](https://gurven.anth.ucsb.edu/sites/default/files/sitefiles/papers/lea%20et%20al.%202020%20supplement.pdf): target measurement context, not input evidence for the lipid constructors. EDTA venous blood; TC/HDL measured with CardioChek Plus; LDL calculated; nonfasting participants retained. The project's 397-person complete-case residual analysis is not the paper's original lifestyle estimand.

The narrow source review inspected primary Methods/Table 1 for Huang, original supplementary lipid methods for Lea, and accessible methodological sections/abstract for Schisterman. It did not re-read every construction source or quantify assay error. Full third-party papers are not redistributed. Exact construction sources, scientific choices and the larger historical record are described in the optional manuscript.

## Results and uncertainty

Case A uses the frozen Q4 ENSANUT E01/E02 constructions: two laws, six tables and 18 primary seed estimates. Case B uses all six initial lipid laws: eighteen tables and 54 primary seed estimates. The two R04 repairs add six dependent tables and 18 primary seed estimates; they are shown separately. Seeds and generated rows are not new clinical observations.

ENSANUT references use the specified equal-eight-cell analytical population and saved empirical cluster-resampling stability bands. Lipid slopes retain the saved HC3 conditional-sensitivity intervals; the TC interval includes zero. No residual-correlation interval is invented. Clinical references were already exposed at project level. None of these bands is an equivalence margin or a guarantee about a future population.

The initial Ordinary 2 tail defect was repaired by both later policies. One retained Workflow 1 row had HDL above TC; it is not removed. Whether an ideal component construction adequately represents the measured assay is a question for interpretation, not settled by the arithmetic identity.

## Packet contents

Read 01_REVIEW_BRIEF.pdf, then use 02_REVIEW_FORM.md or the blank six-row CSV. 04_ANALYSIS_ESTIMATES.csv contains analysis-level summaries, including supplementary spread/coherence diagnostics; it contains no individual measurements. optional/PAPER_v0_30.pdf is the unchanged full reading draft. Author metadata remain draft placeholders.

No raw or generated individual records, full third-party articles, credentials, raw API logs or host-only answers are included. Do not describe this packet as a completed human review. The separately stored local audit verifies aggregate arithmetic and input hashes; it does not certify biomedical validity.
'''
    (OUT / '03_CONTEXT_AND_SOURCES.md').write_text(context,encoding='utf8')
    (OUT / '00_START_HERE.txt').write_text('Biomedical scientific-use review, manuscript v0.30\n\nStart with 01_REVIEW_BRIEF.pdf (4 pages).\nThen fill 02_REVIEW_FORM.md or 05_BLANK_ANALYSIS_DECISIONS.csv.\n03_CONTEXT_AND_SOURCES.md explains measurements and references.\n04_ANALYSIS_ESTIMATES.csv contains exact aggregate values and ranges.\nThe full manuscript is optional/PAPER_v0_30.pdf.\n\nPurpose: qualitative judgment of specific exploratory analyses, not AI architecture, clinical approval, or a scored user study.\nAll responses are blank. The research team has not contacted a reviewer.\nNo patient-level or generated individual tables are included.\n',encoding='utf8')
    shutil.copyfile(PROJECT / 'manuscript/methods_draft_v30_2026-11-11/paper.pdf',OUT / 'optional/PAPER_v0_30.pdf')
    members = sorted([p for p in OUT.rglob('*') if p.is_file() and p.name != 'PACKAGE_MANIFEST.json'])
    expected = {'00_START_HERE.txt','01_REVIEW_BRIEF.pdf','02_REVIEW_FORM.md','03_CONTEXT_AND_SOURCES.md',
                '04_ANALYSIS_ESTIMATES.csv','05_BLANK_ANALYSIS_DECISIONS.csv','optional/PAPER_v0_30.pdf'}
    assert {p.relative_to(OUT).as_posix() for p in members} == expected
    manifest = {'version':'v0.30-scientific-use-brief', 'review_responses_collected':0,
        'contains_individual_records':False,'new_model_calls':0,'new_generated_tables':0,
        'files':[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in members]}
    (OUT / 'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in [*members,OUT / 'PACKAGE_MANIFEST.json']: archive.write(p,p.relative_to(OUT).as_posix())
    with zipfile.ZipFile(ZIP) as archive:
        assert set(archive.namelist()) == expected | {'PACKAGE_MANIFEST.json'}
        for item in manifest['files']:
            assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']
    for rel,expected_hash in audit['input_hashes'].items(): assert sha(PROJECT / rel) == expected_hash,rel
    receipt = {'status':'built_pending_independent_packet_and_visual_review','pdf':str(PDF),'pdf_pages':4,
               'pdf_sha256':sha(PDF),'zip':str(ZIP),'zip_sha256':sha(ZIP),'members':sorted(expected),
               'aggregate_summary_rows':len(records),'audit_sha256':sha(audit_path),
               'new_API_calls':0,'new_generation':0,'human_contacts':0,'responses_collected':0}
    (HERE / 'PACKAGE_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt,indent=2))

if __name__ == '__main__': main()

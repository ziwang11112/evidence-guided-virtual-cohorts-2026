"""Build a short, aggregate-only scientific-use review package from frozen results.

No patient rows, synthetic rows, model calls, generator execution or refitting.
"""
from pathlib import Path
import csv, hashlib, json, shutil, statistics, zipfile
from xml.sax.saxutils import escape
import fitz
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

HERE=Path(__file__).resolve().parent; P=HERE.parents[1]
L=P/'work/lifestyle_application_2026-11-11'
OUT=P/'deliverables/Biomedical_Use_Review_v31_2026-11-11'
PREV=P/'deliverables/Biomedical_Use_Review_v30_2026-11-11'
PDF=OUT/'01_REVIEW_BRIEF.pdf'; ZIP=OUT.with_suffix('.zip')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
put=lambda p,s:p.write_text(s,encoding='utf-8')
dump=lambda p,s:put(p,json.dumps(s,indent=2,ensure_ascii=False)+'\n')
OUT.mkdir(parents=True,exist_ok=True);(OUT/'optional').mkdir(exist_ok=True)
data=json.loads((L/'ANALYSIS_RESULTS.json').read_text())['results']
real=next(x for x in data if x['kind']=='real_reference')
traits=['bmi','total_cholesterol','hdl_cholesterol']; names=['BMI','TC','HDL']
cs=['rural_minus_pastoralist','urban_minus_pastoralist','urban_minus_rural']
labels=['Rural - pastoralist','Urban - pastoralist','Urban - rural']
protected=[P/'manuscript/DRAFT_v0_31.md',P/'manuscript/methods_draft_v31_2026-11-11/paper.pdf',P/'manuscript/methods_draft_v31_2026-11-11/overleaf_v31.zip',
 L/'ANALYSIS_RESULTS.json',L/'ANALYSIS_CONTRASTS.csv',L/'PROTOCOL.md',L/'SOURCE_METHODS.md',L/'RESULTS.md',
 L/'review/INDEPENDENT_NUMERICAL_REVIEW.json',L/'review/A1_CODE_AUDIT.md',L/'review/A2_CODE_AUDIT.md',
 L/'review/CONSTRUCTION_CODE_REVIEW_CORRECTION.json']
protected += list(PREV.rglob('*'))
for ep in ['LIFESTYLE_A1','LIFESTYLE_A2']:
    protected.extend((L/f'episodes/{ep}/candidates/v001').glob('*'))
bindings={p.relative_to(P).as_posix():sha(p) for p in protected if p.is_file()}
receipt=HERE/'INPUT_BINDINGS.json'
if receipt.exists():
    assert json.loads(receipt.read_text())['hashes']==bindings
else:dump(receipt,{'hashes':bindings,'patient_rows_read':False})

def rows(d,t):return {x['contrast']:x for x in d['analysis']['contrasts'] if x['stratum']=='pooled' and x['trait']==t}
def vals(ep,t,c,key):return [rows(d,t)[c][key] for d in data if d.get('episode_id')==ep]
def cell(v):return f'{statistics.mean(v):.3f} [{min(v):.3f}, {max(v):.3f}]'
def rc(t,c,key='raw_'):
    r=rows(real,t)[c]
    return f'{r[key+"estimate"]:.3f} [{r[key+"lower"]:.3f}, {r[key+"upper"]:.3f}]'

# A human-readable aggregate ledger; never individual observations.
primary=[]
for t in traits:
 for c in cs:
  for d in data:
   r=rows(d,t)[c]
   primary.append(dict(dataset_id=d['dataset_id'],author=d.get('episode_id','REFERENCE'),seed=d.get('seed',''),trait=t,contrast=c,n=r['n'],
      raw_estimate=r['raw_estimate'],raw_lower=r['raw_lower'],raw_upper=r['raw_upper'],raw_unit=r['raw_unit'],
      standardized_estimate=r['estimate'],standardized_lower=r['lower'],standardized_upper=r['upper']))
def export(name,records):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
export('04_PRIMARY_ESTIMATES.csv',primary)
diagnostics=[]
for d in data:
 for x in d['analysis']['trait_status']:
  lr=next(y for y in d['analysis']['interactions'] if y['trait']==x['trait'])
  diagnostics.append(dict(dataset_id=d['dataset_id'],trait=x['trait'],n=x['n'],sample_sd=x['sample_sd'],
                          interaction_p=lr['p_value'],sex_specific_branch=lr['selects_sex_specific']))
export('05_SCALE_AND_BRANCHES.csv',diagnostics)
shutil.copyfile(L/'ANALYSIS_CONTRASTS.csv',OUT/'optional/ALL_189_CONTRASTS.csv')
shutil.copyfile(P/'manuscript/methods_draft_v31_2026-11-11/paper.pdf',OUT/'optional/MANUSCRIPT_v0_31.pdf')
for old,new in [('01_REVIEW_BRIEF.pdf','EARLIER_GLYCEMIA_LIPID_BRIEF.pdf'),('03_CONTEXT_AND_SOURCES.md','EARLIER_CONTEXT_AND_SOURCES.md'),('04_ANALYSIS_ESTIMATES.csv','EARLIER_ANALYSIS_ESTIMATES.csv')]:
    shutil.copyfile(PREV/old,OUT/'optional'/new)

put(OUT/'00_START_HERE.txt','''BIOMEDICAL SCIENTIFIC-USE REVIEW | manuscript v0.31 | 11 November 2026

Start with 01_REVIEW_BRIEF.pdf (four pages, about 15 minutes), then respond in
02_REVIEW_FORM.md. The question is what the generated data could usefully support,
and which assumptions need changing. A positive verdict is not expected.

04_PRIMARY_ESTIMATES.csv contains all 63 additive estimates (9 analyses x 7 datasets).
05_SCALE_AND_BRANCHES.csv contains all 21 sample/SD/interaction diagnostics.
03_CONTEXT_AND_SOURCES.md explains the evidence and exact analysis choices.
06_PARAMETER_ORIGINS.md maps selected assumptions to the analyses they can affect.

Optional: full v0.31 manuscript; all 189 pooled/sex-specific contrasts; the earlier
glycemia/lipid review brief with its full aggregate estimates and source context.
The older brief uses different tasks and sample definitions and is historical.
It has not been silently updated to the lifestyle task.

This ZIP contains aggregate estimates and original review materials only. There
are no real/generated individual records, full third-party articles, credentials
or raw model conversations. No coding is needed; ask for a precise missing item
if these summaries are insufficient. Nothing has been sent to a reviewer.

Feedback is qualitative domain interpretation, not a scored user study.
All response fields are intentionally blank. AI-assisted preparation is disclosed.
''')
put(OUT/'02_REVIEW_FORM.md','''# Scientific-use review: lifestyle-labelled virtual cohorts

Please read the four-page brief. We seek biomedical judgment about a specific
data use, not a positive evaluation of the Agent architecture. Original findings
were permitted input. This is a reconstruction application, not a new discovery.
Reviewer (optional): ______   Expertise (optional): ______   Date: ______

## 1. What could you use these tables for?

Choose for each row: **useful / useful with a named restriction / not useful /
cannot assess**. State the precise purpose, and distinguish A1/A2 if needed.
Consider all comparisons, not only the closest one. No acceptance threshold is prescribed.

| Analysis | Decision and proposed use | Restriction or reason |
|---|---|---|
| Adjusted lifestyle differences in BMI | | |
| Adjusted lifestyle differences in total cholesterol | | |
| Adjusted lifestyle differences in HDL | | |
| Lifestyle-by-sex differences and sex-specific analysis | | |

Could the generated records help you develop or test an analysis, explore a
scientific scenario, or design a subsequent real-data study? What further evidence
would each proposed use need? Distinguish running the analysis correctly from
obtaining evidence about a real population.

Response: ______________________________________________________________

## 2. Which modeling assumption most changes your judgment?

Select one and explain which analysis it affects. You may identify another issue.

- Lifestyle categories combine geography, subsistence and diet; age/sex adjustment
  does not separate their individual causal effects.
- Published descriptive BMI percentage differences are used as approximate
  marginal mean ratios, rather than supplied adjusted regression coefficients.
- Pastoralist HDL spread is extended to other lifestyles; TC magnitudes and
  biomarker dependence contain explicit assumptions.
- The generator uses positive HDL and non-HDL components. The actual measurements
  were CardioChek outputs; the model does not simulate assay error.
- Virtual measurements are complete; real lipid data have substantially fewer
  measured participants. Reasons for missingness were not modeled.

Response: ______________________________________________________________

## 3. Is the analysis implementation appropriate for this use?

The same function fits lifestyle + age + sex, obtains all three contrasts, and
checks two lifestyle-by-sex terms. It uses a per-trait available sample, pooled
outcome scaling and a Gaussian ML likelihood-ratio test. The paper's original
analysis script was unavailable. All additive and sex-specific results are saved.

What should be changed, if anything, and why would it alter the scientific use?
Is heteroscedasticity or a different adjustment set important for your proposed use?

Response: ______________________________________________________________

## 4. Check these candidate conclusions

For each, mark **supported / needs qualification / unsupported / uncertain** and
rewrite if needed. These are proposed statements, not expected answers.

1. The generated records preserve the principal observed urban BMI pattern in
   this source-rich reconstruction application.
2. Generated urban-versus-pastoralist TC is positive, but magnitude and spread
   do not fully match the selected real sample.
3. The present evidence does not show that a nonsignificant HDL contrast is
   biological equivalence, nor that the complete joint lipid distribution is recovered.
4. Source/assumption records make model choices inspectable, but do not themselves
   show that the virtual observations can replace newly collected measurements.

Response: ______________________________________________________________

## 5. One next step that would change your decision

Name one missing fact, analysis, source, or experiment. Explain the decision it
would change and classify it **necessary / useful but optional / unnecessary for
the stated use**. A narrower interpretation can be an adequate answer.

Response: ______________________________________________________________

No additional work needed for my proposed use (if applicable): _______________
Other concerns or a use we have missed: ____________________________________

All responses remain blank until a human reviewer supplies them. Please return
the form or annotate the brief; no patient data or API credentials are required.
''')
put(OUT/'03_CONTEXT_AND_SOURCES.md','''# Context, methods and sources

This package accompanies manuscript v0.31. It adds the completed lifestyle case
to the earlier glycemia/lipid materials. It is a root-led summary of recorded
source/code audits and completed results, not a new independent source review.

## Source study and population

Lea et al. (2020), *Urbanization and market integration have strong, nonlinear
effects on cardiometabolic health in the Turkana*.
[Original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/),
[DOI](https://doi.org/10.1126/sciadv.abb1430),
[supplementary methods](https://gurven.anth.ucsb.edu/sites/default/files/sitefiles/papers/lea%20et%20al.%202020%20supplement.pdf).

Locators: main Methods, Data filtering and processing; Testing for lifestyle
effects on measured biomarkers (models 1-2); Figure 2A; Tables 1-2; supplement
measurement and lifestyle definitions, pp. 3-8. Full articles are not bundled.
The recorded source audit could not recover the original S1/S2 spreadsheets or
author analysis script. No missing coefficients were inferred from their filenames.

Pastoralists combine Turkana-county location, pastoral subsistence and daily milk
consumption. Rural nonpastoralists are the remaining Turkana-county residents;
urban nonpastoralists are Laikipia-county residents. These are observational,
composite categories, not randomized interventions. BMI is kg/m2; TC/HDL are mg/dL
measured with venous EDTA blood and CardioChek Plus, not automatically fasting
central-laboratory values. The generation law is an ideal component model and
does not recover separate assay errors.

Published demographic cells total 1,360, while the reported sample is 1,226.
Both Agents rescaled the published cells under explicit assumptions. The source
Table 2 counts (BMI 1,198; TC and HDL 406 each) differ from this evaluation's
eligible available-case counts (1,189; 400; 405). The released file has 1,226 rows;
strict age >18 excludes nine. No fresh cohort was acquired for this evaluation.

## Inputs and scientific authorship

Each fresh GPT Agent received the research request, original-study evidence,
audited published aggregates, and access to search/read tools. Each searched
twice, read the original and an additional paper, authored a sampling program,
examined one generated-data trial, and retained the initial law. All three final
seeds per law were sampled after closure. No new real-reference coefficient or
old project generator was given to the author; the original published findings
were legal inputs. Source-rich reconstruction is therefore the interpretation.

A1's additional source: [PMC7347104](https://pmc.ncbi.nlm.nih.gov/articles/PMC7347104/).
The prior audit verified reported variability ratios as qualitative context,
not signed Turkana conditional coefficients. A2's additional source:
[Lee et al., rural Kenyan populations](https://pmc.ncbi.nlm.nih.gov/articles/PMC6435188/).
Its raw Maasai female/male HDL difference supplied a unit-converted numerical
anchor, but treating it as a conditional coefficient remains an assumption.

## Fixed analysis

Each trait uses age >18 and observed, finite, positive outcome values. The same
implementation is applied to the real reference and all six generated tables.
Outcome scaling uses that dataset's eligible pooled sample mean and sample SD.
One three-category OLS fit adjusts for age and sex; all three pairwise contrasts
use its full covariance. Raw units are retained alongside standardized effects.
A Gaussian ML LRT checks two added lifestyle-by-sex terms, at nominal p<0.05.
All nine additive and all eighteen sex-specific contrasts are retained per dataset.
Sex-specific fits use the same pooled scaling. Exploratory BH adjustment over
nine additive tests is not the original paper's eleven-outcome testing family.

These are explicit Methods-guided choices, not verified original-script details.
Conventional OLS intervals condition on the sample/model. Generated intervals do
not quantify source, structural or transport uncertainty. Three seeds per law
measure draw variation; two authors are not six independent clinical studies.

## Prior cases in optional/

The earlier brief contains the full selected ENSANUT pair and six lipid authors.
Its lipid residual correlation additionally adjusts for BMI and uses a different
case selection. The lifestyle task uses separate available-case outcomes. Do not
interchange their denominators or call the aggregate package a pooled validation.

## Verification record

The lifestyle experiment's prior independent recomputation checked 189 contrasts
and 21 LRTs (5,846 checks; 4,690 numerical comparisons; largest difference
8.52e-13). It checked arithmetic and artifact integrity, not clinical validity.
Both frozen laws have positive conditional means, finite first/second moments
and positive HDL/non-HDL construction under the declared support. These are
law-specific properties, not evidence that their joint distribution is correct.
This packet exports existing reviewed aggregates only. No human domain feedback
has yet been collected. Original frozen files and manuscript remain unchanged.
''')
put(OUT/'06_PARAMETER_ORIGINS.md','''# Selected modeling decisions: why the generated relationships appear

This is an analysis aid assembled from the two frozen specifications and their
recorded code/source audits. It is not an exhaustive parameter inventory, a
confidence ranking, or a causal explanation of the observed discrepancies.
REPORTED, DERIVED and ASSUMED describe origins, not validated accuracy.

| Quantity | Recorded origin and Agent choice | What to review |
|---|---|---|
| Pastoralist BMI | Published mean 19.99 kg/m2 and SD 2.14. Both laws use these anchors. | Suitability of the source subset and applying its summary to generated demographics. |
| Lifestyle BMI means | Published descriptive differences 9.69% and 8.43% are interpreted as approximate marginal mean ratios. Urban mean 21.927031; rural about 20.2223. These are not reported adjusted regression coefficients. | Whether this interpretation is adequate for the intended adjusted analysis. |
| HDL spread | Published pastoralist mean/SD 72.69/14.72 mg/dL. A1 sets every group marginal SD to 14.72; A2 derives pastoral residual variance and reuses that residual SD across groups. | Extension from one lifestyle group to the others and its effect on variability and subgroup analyses. |
| TC group means | A1 combines HDL with non-HDL; its baseline non-HDL is reported LDL 60.89 plus an assumed 15 mg/dL remainder. A2 also uses a 148.58 TC baseline. Both introduce assumed lifestyle offsets; A1 implies TC means 148.58/150.98/163.58, A2 uses 148.58/150.08/163.58 mg/dL. | The qualitative urban increase is sourced; its numerical size, rural offset and component remainder are not newly measured target effects. |
| Sex effect on HDL | A1 assumes 4 mg/dL. A2 uses 3.87 mg/dL, numerically tied to 0.1 mmol/L times 38.67 from a raw external Maasai sex difference. | Raw external group difference is not a validated conditional coefficient in this population. |
| Age effects, interactions and joint dependence | Mostly explicit numerical assumptions. Positive lognormal innovations and TC=HDL+non-HDL are scientific modeling choices, not extracted full joint evidence. | Could these assumptions change the intended analysis despite plausible marginal values? |
| Demographic allocation | Printed age/sex/lifestyle cells rescaled from 1,360 to 1,226. Age bounds and treatment of the printed age-bin ambiguity are declared assumptions. | Whether the target mixture and support are sufficiently specified for the proposed use. |

A1 accounts for variance of the conditional mean when setting multiplicative
noise to its chosen group marginal SD. A2 uses group-specific additive residual
SD represented through lognormal sampling. This is a real implementation
difference, although both retain substantial assumptions.

The prior review records a small BMI derivation discrepancy for A1 (+0.000545
kg/m2) and A2 (-0.00000489). An early review narrative misattributed the larger
one; the correction is preserved. No generator, output or scientific result was
changed. These discrepancies do not explain the substantive lipid findings.

Questions for the domain reader: Which extension is defensible for exploratory
analysis? Which needs a better source or a sensitivity range? Which makes a
specific use uninformative? Please avoid ranking by the origin label alone.
''')

# Four-page reading guide, with the existing exact-data figure.
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
INK=colors.HexColor('#26364F'); BLUE=colors.HexColor('#345B86'); LIGHT=colors.HexColor('#F0F3FA'); GRAY=colors.HexColor('#58677B')
styles={k:ParagraphStyle(k,fontName='Arial-Bold' if k in ['title','h1','h2','kicker','th'] else 'Arial',fontSize=size,leading=lead,textColor=INK,spaceAfter=space) for k,size,lead,space in
        [('title',23,28,15),('h1',18,23,12),('h2',11,15,6),('kicker',8.7,12,9),('body',9.6,14,8),('small',8,11,6),('cell',8.1,11,0),('th',8.1,11,0)]}
styles['kicker'].textColor=BLUE;styles['small'].textColor=GRAY
story=[]
def p(s,style='body'):story.append(Paragraph(s,styles[style]))
def table(rr,widths):
    t=Table([[Paragraph(escape(str(c)),styles['th' if i==0 else 'cell']) for c in row] for i,row in enumerate(rr)],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#CCD5E3')),('LINEBELOW',(0,-1),(-1,-1),.6,colors.HexColor('#CCD5E3')),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]))
    story.extend([t,Spacer(1,9)])
p('BIOMEDICAL SCIENTIFIC-USE REVIEW  |  v0.31  |  11 NOVEMBER 2026','kicker')
p('Can these virtual cohorts support a useful analysis?','title')
p('A short review of a completed lifestyle application. Please judge <b>specific research uses and assumptions</b>. You do not need to assess the AI architecture or read the full manuscript. Suggested first pass: 15 minutes.')
p('What was generated','h2')
p('Two fresh GPT Agents constructed seven-column tables: identifier, age, sex, lifestyle group, BMI, total cholesterol (TC) and HDL. Each authored its own sampling program from the original study, published aggregates and additional literature. A numerical worker sampled three final tables per law: <b>six complete cohorts of 1,226 fictional people</b>.')
p('What the Agent and host each did','h2')
table([['Actor','Actual work'],['Researcher / host','Specify intended population, variables, analyses and tools; fix the common evaluation.'],['Scientific Agent','Search/read studies; choose demographic and conditional relationships, parameters, joint model and checks; retain or revise its law.'],['Numerical tools','Execute that law in isolation; apply the same analysis to measured and virtual records after author closure.']],[124,368])
p('The use being examined','h2')
p('Can a researcher use these records to explore age/sex-adjusted differences among pastoralist, rural nonpastoralist and urban nonpastoralist groups? We retain <b>all nine</b> BMI/TC/HDL contrasts, all sex-specific outputs and interaction tests. The original paper was allowed input, so this examines reconstruction for scientific use, not discovery of an unknown relationship.')
p('What the reference means','h2')
p('The real file is an observational sample, not a known population truth. Its eligible measured n is 1,189 for BMI, 400 for TC and 405 for HDL. Generated outcomes are complete (n=1,226 each). No new real-reference coefficients were provided to the constructing Agents. The original analysis code was unavailable; both data types receive one Methods-guided reimplementation.')
p('Read pages 2-4, then use <b>02_REVIEW_FORM.md</b>. The optional folder contains earlier glycemia/lipid examples, full aggregates and the current manuscript. All materials here are summaries; no participant-level records or full third-party papers are included. Prepared with AI assistance. No human biomedical verdict has been collected.','small')
story.append(PageBreak())
p('01  |  SAME ANALYSIS, DIFFERENT DATA','kicker')
p('What the lifestyle contrasts look like','h1')
story.append(Image(str(P/'manuscript/paper_figures_v31_2026-11-11/fig3-lifestyle-raw.png'),width=480,height=528))
p('Age/sex-adjusted group contrasts in original units. Navy is the real sample with 95% OLS intervals; purple/orange are three draws per law. Draw ranges are <b>not</b> confidence intervals. All groups and outcomes are shown. Wide or overlapping reference intervals do not establish equivalence.','small')
story.append(PageBreak())
p('02  |  INTERPRET THE RESULTS IN CONTEXT','kicker')
p('Useful patterns and unresolved differences','h1')
rr=[['Trait / contrast','Real estimate [95% CI]','A1 mean [range]','A2 mean [range]']]
for t,name in zip(traits,names):
 for c,label in zip(cs,labels):rr.append([name+' / '+label,rc(t,c),cell(vals('LIFESTYLE_A1',t,c,'raw_estimate')),cell(vals('LIFESTYLE_A2',t,c,'raw_estimate'))])
table(rr,[128,124,120,120])
p('BMI: kg/m2. TC and HDL: mg/dL. The same six final tables underlie every row. The exact per-draw effects and standardized counterparts are in 04_PRIMARY_ESTIMATES.csv.','small')
p('<b>BMI:</b> the urban-minus-pastoralist contrast is 1.882 kg/m2 in the reference and 1.700-2.251 across generated draws. The source already described the BMI differences; preservation is useful reconstruction, not new biological discovery.')
p('<b>TC:</b> the urban-minus-pastoralist direction is retained, but raw magnitudes are lower. Standardized contrasts appear closer partly because virtual variability is smaller. Rural lipid point contrasts are weakly reconstructed; their real intervals include zero, so the true population difference is uncertain.')
p('<b>HDL:</b> all three reference intervals include zero. One generated table (A1, seed 64001) selects a sex-specific branch (LRT p=0.02457), unlike the reference; all resulting estimates are retained. Similar nonsignificance is not biological equivalence.')
ds=[['Spread / branch','Real sample','Six virtual draws']]
for t,name in zip(traits,names):
 ref=next(x for x in real['analysis']['trait_status'] if x['trait']==t)
 v=[next(x for x in d['analysis']['trait_status'] if x['trait']==t)['sample_sd'] for d in data if d['kind']!='real_reference']
 ds.append([name+' sample SD',f'{ref["sample_sd"]:.2f}',f'{min(v):.2f}-{max(v):.2f}'])
table(ds,[180,134,178])
p('Smaller virtual p-values can follow from larger usable n and lower spread. They are not extra clinical evidence. Group differences are observational; age/sex adjustment does not identify causal effects of changing lifestyle.','small')
story.append(PageBreak())
p('03  |  CHECK THE SCIENTIFIC CHOICES','kicker')
p('What came from evidence, and what was assumed?','h1')
table([['Model choice','Recorded basis','Question for the reviewer'],
 ['BMI group means','Pastoralist mean/SD plus published percentage differences, interpreted approximately as marginal mean ratios.','Is that enough for the intended adjusted group comparison?'],
 ['HDL variability','Pastoralist SD anchor; A1 extends marginal SD, A2 extends residual SD to other groups.','Does this extension limit subgroup or heterogeneity uses?'],
 ['TC contrasts and dependence','Qualitative source pattern with assumed numerical differences, dispersion and latent dependence.','Which missing joint or conditional evidence would matter most?'],
 ['Positive lipid components','Both Agents use TC = HDL + positive non-HDL; no assay-error simulation.','Is an ideal component model appropriate for the measurement or use?'],
 ['Lifestyle / demographics','Composite geography/subsistence/diet categories; inconsistent printed cell totals rescaled by each Agent.','Which population or composition assumptions need clarification?']],[110,205,177])
p('Three decisions we need from you','h2')
p('<b>1. Scientific use:</b> Which analyses could these records support, with what restrictions? Consider analysis development, scenario exploration or planning later real-data work; these uses still require your specific judgment.')
p('<b>2. Main weakness:</b> Which measurement, adjustment or modeling assumption would most change that decision? The exact unit conversions, source locators and selected parameter origins are in files 03 and 06.')
p('<b>3. Next evidence:</b> Name one necessary addition, if any, and the decision it would change. An interpretation correction may be more useful than a new model or larger synthetic sample.')
p('The two Agent laws share a GPT family and supplied evidence. Three draws per law show conditional sampling variation, not independent clinical replication or calibrated model uncertainty. The existing study family was previously exposed during development.','small')
p('The earlier glycemia and paired-lipid brief in optional/ supplies complementary use cases, not additional validation of these lifestyle effects. Review every construction within the case you assess; the package does not present a project-wide success rate.','small')
p('<b>Return:</b> comments in 02_REVIEW_FORM.md or annotations on this brief. Negative, restricted and uncertain judgments are equally useful. No coding is needed.','body')

def footer(c,doc):
    c.saveState();c.setFont('Arial',8);c.setFillColor(GRAY)
    c.drawString(60,27,'Scientific-use review | aggregate evidence | v0.31')
    c.drawRightString(552,27,str(doc.page));c.restoreState()
doc=SimpleDocTemplate(str(PDF),pagesize=(612,792),leftMargin=60,rightMargin=60,topMargin=43,bottomMargin=45,
                      title='Biomedical scientific-use review: lifestyle-labelled virtual cohorts',author='Research project; AI-assisted preparation')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
with fitz.open(PDF) as pdf:
    assert len(pdf)==4, len(pdf)
    extracted='\n'.join(p.get_text() for p in pdf)
    put(HERE/'BRIEF_TEXT.txt',extracted)
    render=HERE/'qa';render.mkdir(exist_ok=True)
    for i,page in enumerate(pdf,1):page.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(render/f'page-{i}.png')

for rel,h in bindings.items():assert sha(P/rel)==h,rel
members=sorted(x for x in OUT.rglob('*') if x.is_file() and x.name!='PACKAGE_MANIFEST.json')
manifest={'version':'0.31','status':'built_pending_packet_review','pdf_pages':4,'patient_rows_included':False,'generated_rows_included':False,
          'human_review_collected':False,'files':{x.relative_to(OUT).as_posix():{'sha256':sha(x),'bytes':x.stat().st_size} for x in members}}
dump(OUT/'PACKAGE_MANIFEST.json',manifest)
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for f in sorted(OUT.rglob('*')):
        if f.is_file():z.write(f,OUT.name+'/'+f.relative_to(OUT).as_posix())
dump(HERE/'BUILD.json',{'pdf_sha256':sha(PDF),'zip_sha256':sha(ZIP),'pages':4,'members':len(members)+1,'primary_records':len(primary),'diagnostics':len(diagnostics),'old_files_preserved':len(bindings),'new_api_calls':0,'new_patient_fits':0})
print(json.dumps({'pages':4,'primary_records':len(primary),'diagnostics':len(diagnostics),'zip_bytes':ZIP.stat().st_size}))

"""Version presentation only; preserve the scientific v0.11 prose and tables."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parent
P=R.parents[1]; M=P/'manuscript'
F=M/'paper_figures_v12_2026-11-04'
B=M/'conference_draft_v12_2026-11-04';B.mkdir(exist_ok=True)
old=(M/'DRAFT_v0_11.md').read_text(encoding='utf-8')
captions={
1:('A worked evidence-to-generator implementation.',
'The completed whole-cohort case connects a reviewed study result to actual model parameters and sampling operations. The Agent selects a sex-stratified Gaussian copula and converts the Hainan male glucose–HbA1c Spearman coefficient 0.44 to latent correlation 0.457. The matrix shows selected entries only: A/B/G/H denote age/BMI/glucose/HbA1c; dots omit other entries, and the BMI–glucose value 0.25 is an explicit assumption. With standard-normal noise ε, Cholesky sampling and the displayed shifted-lognormal transform generate BMI, glucose and HbA1c; age uses a separate bounded-integer transform. The table cells are schematic placeholders. Positive-definiteness and finite-moment audits precede execution; runtime statistics and semantic_feedback_v1 inform the retain-or-revise decision. This instance retained its model after 11 approximate comparisons and 23 unavailable checks per execution. Search, evidence review and fresh-context construction were host-dispatched stages. The figure illustrates an implemented construction, not a mandatory copula for all requests or a demonstrated revision gain.'),
2:('External evidence and six scientific analyses.',
'All six coefficients use native units and the indicated adjustment sets. E0 supplies basic/marginal evidence; E1 adds relational evidence. Each Agent condition contains five independently authored generators, ordered A01–A05; each statistical condition contains one prescribed generator. Dots show three final seed estimates, open diamonds constructor means, and vertical segments seed min–max ranges. Author labels do not pair E0 and E1. Dashed lines denote selected-sample reference estimates; gray regions are CHNS 95% community-cluster CR1-t intervals or ENSANUT cluster-resampling stability bands. Neither is a within-generator seed interval or an equivalence margin. All 24 constructions, 72 tables and 216 coefficient estimates appear. Additional evidence lowers mean absolute reference discrepancy for five endpoints, while CHNS BMI worsens; endpoint-specific contrasts are reported in the text. The reference populations were exposed during development.'),
3:('Supplied summaries become jointly analyzable data.',
'The five panels show three adjusted regression coefficients and the glucose–HbA1c Pearson and Spearman correlations. L01–L03 use literature evidence; R01–R03 additionally receive 30 target summaries and metadata. Dots are all three final seed statistics, diamonds constructor means and thin segments seed ranges. Labels denote independently authored generators, not paired versions. Dashed lines mark reference summaries available to R; gray bands are the available 95% community-cluster CR1-t intervals for regression references. No correlation interval is supplied. All six constructors, 18 distinct delivery tables and 90 statistics are shown once; retained initial/final outputs are identical. Closer R agreement demonstrates supplied-information reconstruction, not prediction of hidden reference results or a revision benefit.'),
4:('Longitudinal analysis of reconstructed cohorts.',
'Panels show the interactions of memory-score change per decade with HbA1c splines below and at or above 6.5%. Blue circles are Agent-generated and violet squares published-law reconstruction estimates for three fixed seeds; bars are all 12 stored model-conditional 95% Wald intervals. Dashed lines mark supplied source coefficients and solid lines mark zero; source standard errors are not plotted. Each table has 11,509 synthetic subjects at four visits (46,036 records). Both constructions receive source-model exports and method code. The negative lower-branch interaction is retained; upper-branch point estimates and significance decisions vary. All 16 effects, the high-HbA1c spread discrepancy and three invalid initial comparator attempts remain in the supporting record. This is source-rich reconstruction, not independent clinical confirmation.'),
5:('Analysis-specific usefulness and an unresolved joint dependence.',
'Panels (a–d) show all primary-model nonintercept effects and (e–g) all secondary-model effects. Blue points are three fixed 3,000-person draws with conditional 95% HC3-t intervals. Gray dashed lines and bands are exposed CHNS reference estimates and 95% community-cluster CR1-t intervals; solid lines mark zero. All effects retain native units (pp: HbA1c percentage points), with shared limits for matching predictors. Generated intervals omit source, structural and transport uncertainty; overlap is not equivalence. Panel (h) displays two pre-generation analytical scenarios: latent BMI–glucose correlations 0.10 and 0.40 imply conditional BMI coefficients +0.03422 and −0.01095 while leaving marginal laws, other bivariate laws and the secondary projection unchanged. The delivered model used 0.25. These are not new draws, a fitted curve or a causal intervention. Retained initial/final stages alias the same three tables.')}
new=old.replace('visual_redesign_v11_2026-11-04','paper_figures_v12_2026-11-04')
new=new.replace('Working conference-style draft v0.11','Working conference-style draft v0.12')
lines=new.splitlines()
for i,line in enumerate(lines):
    if line.startswith('Working conference-style draft'):
        lines[i]='Working conference-style draft v0.12 — 4 November 2026. Native-unit scientific figures and a concrete implementation overview; the scientific body, tables and results remain unchanged.'
    m=re.match(r'\*\*Figure (\d+)\.',line)
    if m:
        k=int(m[1]);title,body=captions[k]
        lines[i]=f'**Figure {k}. {title}** {body}'
new='\n'.join(lines)+'\n'
(M/'DRAFT_v0_12.md').write_text(new,encoding='utf-8')
def scientific_body(s):
    return '\n'.join(x for x in s.splitlines() if not (x.startswith('Working conference-style draft') or x.startswith('![') or re.match(r'\*\*Figure \d+\.',x)))
assert scientific_body(old)==scientific_body(new)
src=(M/'conference_draft_v11_2026-11-04'/'build_reading_copy.py').read_text(encoding='utf-8')
src=src.replace('DRAFT_v0_11.md','DRAFT_v0_12.md').replace('visual_redesign_v11_2026-11-04','paper_figures_v12_2026-11-04')
src=src.replace("figure_width = r'0.92\\textwidth' if figure_count == 5 else r'\\textwidth'", "figure_width = r'0.98\\textwidth' if figure_count == 5 else r'\\textwidth'")
(B/'build_reading_copy.py').write_text(src,encoding='utf-8')
record={'scientific_body_identical':True,'tables_and_references_identical':True,
    'old_sha256':hashlib.sha256((M/'DRAFT_v0_11.md').read_bytes()).hexdigest(),'new_sha256':hashlib.sha256((M/'DRAFT_v0_12.md').read_bytes()).hexdigest(),
    'changes':['version note','five figure paths','five figure captions'],
    'new_experiments':False,'new_patient_analysis':False}
(R/'DRAFT_CHANGE_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(record)

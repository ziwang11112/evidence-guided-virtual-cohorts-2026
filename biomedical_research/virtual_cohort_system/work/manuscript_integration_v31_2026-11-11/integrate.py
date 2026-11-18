"""Integrate completed, audited application results; never generate or refit data."""
from pathlib import Path
import hashlib,json,re,shutil
import pandas as pd

I=Path(__file__).resolve().parent;P=I.parents[1];M=P/'manuscript'
L=P/'work/lifestyle_application_2026-11-11';Q=P/'work/published_analysis_replay_2026-11-11'
B=M/'methods_draft_v31_2026-11-11';F=M/'paper_figures_v31_2026-11-11'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):p.write_text(s,encoding='utf-8')
def dump(p,x):put(p,json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def replace_once(s,a,b):
    assert s.count(a)==1,(a[:80],s.count(a));return s.replace(a,b,1)
I.mkdir(exist_ok=True);B.mkdir(exist_ok=True);F.mkdir(exist_ok=True)
assert not (M/'DRAFT_v0_31.md').exists(),'Do not overwrite a revised edition'
preserve=[M/'DRAFT_v0_30.md',*(M/'methods_draft_v30_2026-11-11').glob('*')]
for unit in [L,Q]:
    preserve.extend(p for p in unit.glob('*') if p.suffix in {'.json','.csv','.md','.py'})
    preserve.extend((unit/'review').glob('*.json'))
    preserve.extend((unit/'report').glob('*'))
    preserve.extend((unit/'figures').glob('*'))
bindings={p.relative_to(P).as_posix():sha(p) for p in preserve if p.is_file()}
dump(I/'REVISION_FACTS.json',dict(version='0.31',base_version='0.30',preserved_inputs=bindings,new_api_calls=0,new_generated_tables=0,new_patient_analyses=0,public_sync=False))
s=(M/'DRAFT_v0_30.md').read_text(encoding='utf-8')
s=s.replace('Methods working draft v0.30','Methods working draft v0.31',1)
# Insert the new scientific-use application first; update existing cross-references once.
s=re.sub(r'\bFigure (\d+)\b',lambda m:'Figure '+str(int(m[1])+1 if int(m[1])>=3 else int(m[1])),s)
s=re.sub(r'(?<=### 5\.)(\d+)(?=\.)',lambda m:str(int(m[1])+1),s)
s=re.sub(r'(?<=Section 5\.)(\d+)\b',lambda m:str(int(m[1])+1),s)
abstract='''Biomedical researchers need jointly measured variables that may be inaccessible or were never collected together. Published studies provide partial statistical evidence, but using those findings in a new analysis requires a joint model. We develop a scientific-Agent workflow that turns a population, variables and research questions into virtual biomedical cohorts without target individual-level training records. The Agent retrieves or receives studies, interprets their measurement and analysis conditions, authors a joint sampling program, and records scientific sources and assumptions. We evaluate the resulting data by holding the analysis procedure fixed and changing its input. In a source-rich lifestyle application, two fresh Agents produced six complete cohorts. The adjusted urban-versus-pastoralist BMI difference was 1.882 kg/m² in the real sample and 1.700-2.251 across virtual draws. Total-cholesterol elevation was retained, while rural lipid contrasts and dispersion were less well reproduced. Separate request-only experiments used no prepared papers: all twelve ordinary and workflow-guided GPT sessions delivered generators, with variable analytical agreement and no consistent policy advantage. Glycemia experiments retained conditioning patterns, and additional relationship evidence reduced discrepancy in five of six coefficients. Inspectable source-to-code records and reusable checks exposed assumptions and supported specific mathematical repairs without a general revision benefit. These results demonstrate autonomous evidence-to-data construction and analysis-specific uses of the generated records. The permitted information, uncertainty and limitations remain part of each data product; validity for inference in unfamiliar populations is not established.'''
a=s.index('## Abstract\n');b=s.index('\n## 1. Introduction',a)
s=s[:a]+'## Abstract\n\n'+abstract+'\n'+s[b:]
anchor='The scientific question is which analyses the generated records can support.'
s=replace_once(s,anchor,'''Our evaluation holds a biomedical analysis fixed and substitutes generated records for the measured sample. A concrete application asks for a cohort with lifestyle groups so that a researcher can run the original study's age- and sex-adjusted biomarker comparisons. We distinguish this source-rich reconstruction, which permits published findings from that study, from request-only construction, where the Agent must discover evidence without a prepared bibliography. The two settings assess different practical uses of the same generation procedure.

'''+anchor)
s=s.replace('Second, it evaluates the resulting records for multivariable regressions, conditioning patterns, threshold co-occurrence and dependence across distinct tasks and information conditions, retaining both agreements and failures.','Second, it evaluates the resulting records by applying matched scientific-analysis procedures to measured and virtual data, including lifestyle contrasts, multivariable regressions, conditioning patterns, threshold co-occurrence and dependence, retaining both agreements and failures.')
s=s.replace('The latest controller directly launches captured GPT API sessions','The request-only controller directly launches captured GPT API sessions',1)
s=s.replace('Table 4 and Supplements S17 and S20-S23 identify','Table 4 and Supplements S17 and S20-S25 identify',1)
# Do not imply the request-only input restriction applies to the new application.
s=replace_once(s,'Candidate programs run in a network-disabled worker', '''The source-rich lifestyle application uses the same API, retrieval and isolated-sampling machinery with a new task and evaluator. It additionally supplies the original study and permitted published aggregates. Both authors can search for missing information; the Agent still chooses the scientific law and numerical assumptions. The host does not replace unavailable source statistics with fits to the real reference. This declared evidence allowance differs from the request-only comparison rather than being an unreported relaxation of its protocol.

Candidate programs run in a network-disabled worker''')
s=replace_once(s,'| Q4: open-retrieval replication |','''| Lifestyle application | Original study and published aggregates, plus Agent-chosen retrieval; no participant records or newly fitted reference results | 2 fresh GPT authors; 6 complete tables of 1,226 | Nine adjusted lifestyle contrasts, sex-specific counterparts, interaction and scale diagnostics; source-rich reconstruction; S24 |
| Existing-table analysis reuse | Existing frozen records; no new author or generation | 18 initial tables from 6 laws, plus 6 tables from 2 dependent repairs | Three age/sex-adjusted biomarker correlations; all data passed to the same operator; S25 |
| Q4: open-retrieval replication |''')
methods='''### 4.4. Source-rich lifestyle application

Two fresh Agent contexts received the Lea et al. (2020) study [32], an audited account of its published evidence, the printed age/sex/lifestyle counts, and a visible request for BMI, total cholesterol (TC) and HDL analyses. They could search additional publications through the same Europe PMC/PMC tools. Each selected its own demographic construction, conditional relationships, numerical values and joint law. The host fixed the output schema, eligibility, analysis procedure and budget, but supplied no new real-data fits or old project generators. The original paper's findings were legitimate inputs. This is reconstruction of a specified scientific use, not transfer from entirely independent evidence.

The task requested 1,226 complete virtual records with seven columns: identifier, age, sex, three-level lifestyle, BMI, TC and HDL. Lipids use mg/dL and age eligibility is strictly greater than 18. The printed demographic counts total 1,360, unlike the reported recruitment of 1,226; the Agents were told about the discrepancy and documented their own rescaling assumptions. Complete virtual measurement is a task choice, not reconstruction of the original missingness. Both used gpt-6.1-sol/high/default and had the same ceiling of two candidates, two generated-only trials and at most one revision. Both histories closed before sampling three final seeds per law and computing the new reference contrasts. Full model identity, requests, responses, tools and costs were retained.

We reimplemented the original Methods rather than unavailable author code. For each trait separately, the same function selects eligible, observed, positive finite values, standardizes by that dataset's pooled sample mean and SD, and regresses the outcome on lifestyle, age in years and sex. One three-category fit provides all three pairwise lifestyle contrasts, including their full covariance. A Gaussian maximum-likelihood likelihood-ratio test compares the additive model with two lifestyle-by-sex terms (nominal p<0.05). All nine additive and eighteen sex-specific contrasts remain visible regardless of branch; sex-specific fits use the same pooled scale. These choices resolve details not fully specified in the source prose. The nine-contrast exploratory BH family is not the paper's original 11-outcome correction. Raw-unit contrasts, obtained using the same dataset's outcome SD, are reported alongside standardized effects.

The real release has 1,226 rows; the predefined age rule excludes nine. Available-case n is 1,189 for BMI, 400 for TC and 405 for HDL. The six virtual tables each have 1,226 complete records. Accordingly, generated p-values and intervals are conditional on a different usable sample size and assumed distribution. They cannot be read as additional clinical evidence. The protocol compares direction, effect magnitude, scale and branch behavior without a post-hoc pass threshold. The real sample is an uncertain observational reference, and the previously exposed study family is not a new independent validation cohort. Supplement S24 preserves complete outputs and source limitations.

### 4.5. Reusing existing records in a common correlation analysis

A separate analysis-only unit applied the same age/sex-adjusted Pearson procedure from the source's supplementary Methods [32] to existing real and virtual records. It included all six initial lipid constructions and three saved draws each, plus two already completed dependent repairs with three draws each. No generator was changed or executed. The fixed rule retained age>18 and common complete BMI/TC/HDL records; it left 396 real participants. This differs from the earlier age/sex/BMI-adjusted lipid residual analysis and from the lifestyle application's per-trait case selection. All three pairwise correlations and all 24 virtual tables were retained. Supplement S25 reports these separately from new construction, with no pooled quality score or independence claim.

'''
s=replace_once(s,'## 5. Results\n',methods+'## 5. Results\n')
results='''### 5.1. Can virtual cohorts reproduce a lifestyle analysis when only the data change?

Both Agents delivered a seven-column cohort law, independently read the permitted study and chose an additional publication, inspected one generated-data trial, and retained their first candidate. The programs included lifestyle-dependent conditional means and dispersion, age and sex terms, and stochastic paired biomarkers. Both selected bounded age distributions and lognormal innovations with finite moments. They independently constructed TC as HDL plus a positive non-HDL component; no host-authored group coefficient or target-based correction was inserted. The demographic and conditional relationships not identified by the publications remained explicit assumptions.

With the same age/sex-adjusted analysis applied to real and virtual data, the principal urban BMI pattern was preserved (Figure 3). The urban-minus-pastoralist contrast was 1.882 kg/m² in the reference, with a 95% interval of 1.368-2.397, compared with 1.700-2.251 across all six generated draws. Urban-minus-rural BMI was also positive in every draw. The corresponding standardized TC contrast was 0.475 in the reference and three-draw means of 0.451 and 0.496 for the two constructions. In raw units, however, the TC contrast was 20.342 mg/dL versus 13.732-18.907. Lower virtual TC variability partly explains why standardized agreement looks stronger than raw-scale agreement.

The same generated tables did not preserve every contrast. Rural-minus-pastoralist TC and HDL point estimates were attenuated or reversed; the real reference intervals already include zero, so these are descriptive discrepancies rather than established differences from a known population effect. All three reference HDL intervals include zero. Five generated tables likewise had all three nominal intervals include zero, while A1/seed64001 produced a positive urban-minus-rural HDL contrast and selected the sex-specific interaction branch. The reference selected no interaction branch. Virtual TC SDs were 31.85-34.06 mg/dL versus 42.81, and HDL SDs were 14.40-15.10 versus 20.23. Complete standardized results and this branch exception appear in S24.

![All nine lifestyle contrasts in original measurement units](paper_figures_v31_2026-11-11/fig3-lifestyle-raw.pdf)

**Figure 3. Hold the analysis fixed and replace its input data.** Every panel shows the three age/sex-adjusted lifestyle contrasts for one biomarker. Navy diamonds and bars are the real sample estimates and 95% OLS t intervals. Purple and orange points are the three predeclared draws for each of two Agent-authored laws; their ranges indicate sampling variation, not confidence intervals. All nine additive contrasts are shown in original units. The reference has 1,189/400/405 eligible measured records for BMI/TC/HDL; each virtual table has 1,226 complete records. Differences in precision do not measure scientific validity. The original paper was permitted generation evidence, whereas newly fitted reference results were withheld until both authors closed. This is a Methods-guided reconstruction of three outcomes, not unchanged author-code execution, the complete original study or an independent target test. Figure S8 shows the same comparisons in standardized units; Table S24 retains the interaction exception and scale diagnostics.

This application demonstrates that the Agent-generated data can be used in a recognizable biomedical analysis while preserving important parts of its pattern. It does not establish that every relationship is recovered, that revision helped, or that source-rich input outperforms request-only input: the latter studies also differ in variables, requests and generators. All seven datasets yielded the 189 predefined contrasts and 21 interaction tests, independently recomputed to a maximum numerical difference of 8.52e-13. The two author sessions used 31 API calls at an estimated tariff cost of USD0.375. Repeated seeds remain nested within two constructions, not six independent studies.

'''
s=replace_once(s,'### 5.2. Can generated cohorts support the requested scientific analyses?',results+'### 5.2. Can generated cohorts support the requested scientific analyses?')
s=replace_once(s,'## 6. Discussion\n','''## 6. Discussion

The lifestyle application makes the data product directly assessable: an existing biomedical analysis receives a different input table. Its urban BMI result is interpretable in kg/m², and the TC comparison shows why raw and standardized scales should be examined together. The ability to run the analysis and retain a useful pattern is a concrete outcome; smaller virtual p-values are not. The source-rich setting also clarifies what the result can establish. The original paper contributes legitimate constraints, while incomplete conditional and joint quantities remain model commitments. Matching those permitted findings is reconstruction, not a new biological discovery. Request-only experiments answer the complementary question of whether the Agent can obtain and use evidence without that supplied starting point.

''')
s=replace_once(s,'## Limitations and Ethical Considerations\n','''## Limitations and Ethical Considerations

The new lifestyle application has two constructors under one GPT configuration and an already exposed study family. Published source findings were allowed, original analysis code and supplemental numerical workbooks were unavailable, and the task requested complete measurements despite substantial real-data lipid missingness. We explicitly chose the common regression, case-selection and scaling rules and retained all branches. The source population's demographic inconsistency and unreported conditional effects remain assumptions in the two laws. This study therefore supports a specified reconstruction use, not general inference, new-population validation or a controlled estimate of the benefit of source-rich evidence. The separate correlation reuse analysis uses old tables and does not increase the number of independent constructions or clinical populations.

''')
# Supplement tables are built from audited aggregate records, not patient rows.
summary=json.loads((L/'PRIMARY_SUMMARY.json').read_text())['summary']
data=json.loads((L/'ANALYSIS_RESULTS.json').read_text())['results']
label={'bmi':'BMI','total_cholesterol':'TC','hdl_cholesterol':'HDL'}
contrast={'rural_minus_pastoralist':'Rural - pastoralist','urban_minus_pastoralist':'Urban - pastoralist','urban_minus_rural':'Urban - rural'}
def primary_table(raw=False):
    prefix='raw_' if raw else ''
    rows=['| Trait / contrast | Real estimate [95% CI] | A1 mean [draw range] | A2 mean [draw range] |','|---|---:|---:|---:|']
    for x in summary:
        v=[f"{x[prefix+'estimate']:.3f} [{x[prefix+'lower']:.3f}, {x[prefix+'upper']:.3f}]"]
        for ep in ['LIFESTYLE_A1','LIFESTYLE_A2']:
            a=x['constructors'][ep][prefix+'estimate'];v.append(f"{a['mean']:.3f} [{a['minimum']:.3f}, {a['maximum']:.3f}]")
        rows.append('| '+label[x['trait']]+' / '+contrast[x['contrast']]+' | '+' | '.join(v)+' |')
    return '\n'.join(rows)
supp='''

### S24. Lifestyle application: evidence allowance, all contrasts and analysis branches

The source-rich task was frozen before launching two fresh API contexts. The authorized initial packet contained an audited source summary and printed Table 1 demographic counts from Lea et al. [32]; source text was treated as evidence, not tool instructions. The paper's published findings were legitimate generation inputs. No participant row, old generator or newly computed reference coefficient was supplied. Additional retrieval used the same Europe PMC/PMC gateway as the request-only runtime. Both authors independently searched twice, read the original study and one further primary article, authored a program/specification and inspected one generated-only trial. A1 made 16 API calls and A2 15, with a combined recorded tariff estimate of USD0.3746075 and no unknown-usage calls. Both selected their first law. Source section reads and tool actions are not additional authors or independent evidence items.

The two programs generated age, sex and lifestyle jointly from their own rescaling of the published demographic cells, with bounded age distributions. Conditional arithmetic means included lifestyle, age, sex and small lifestyle-by-sex terms; paired lognormal innovations generated positive BMI and lipid components. Both selected TC=HDL+positive non-HDL, yielding zero HDL>TC rows in all six final draws. The selected parameter support and covariance matrices give finite first and second moments. These properties concern implementation coherence, not validation of the assumed scientific relationships. The API-submitted program text and specification values match the frozen candidates.

The main article reports 1,226 participants, but its displayed demographic cells sum to 1,360 and leave an age-bin boundary ambiguous. Each author rescaled the printed cells and documented its assumption. Neither consulted individual counts to repair the source. Published pastoralist BMI/HDL summaries and descriptive BMI percentage differences informed some parameters; numerous age/sex effects, TC differences, dispersion and latent correlations were explicit assumptions. The original S1/S2 spreadsheet retrieval did not succeed, and no unverified spreadsheet coefficients were supplied. A negligible BMI arithmetic approximation is recorded with its corrected author attribution in the audit; frozen outputs were not changed.

The final law identities were closed before three fresh seeds (64001, 64003, 64007) per author. All six complete tables have 1,226 rows. The real file's 1,226 rows lose nine under the fixed age>18 rule; no additional discretionary outlier filtering or HDL/TC-based deletion is used. Outcome-specific available-case counts are 1,189, 400 and 405. The common operator standardizes on each outcome's eligible pooled sample, fits the three-category age/sex-adjusted model, and obtains all three contrasts with their full covariance. Its Gaussian maximum-likelihood interaction test has two added terms; all sex-specific fits retain the pooled outcome scale. The exploratory nine-additive-test BH correction is not the original 11-outcome family and is not used to declare data equivalence.

**Table S22. All nine standardized lifestyle contrasts.** Each author entry averages three final draws; brackets show their full range. Reference brackets are conditional 95% OLS t intervals. Standardization uses each dataset's own outcome SD; these intervals and ranges describe different sources of variation.

'''+primary_table()+'''

**Table S23. The same contrasts in raw units.** BMI is kg/m²; TC and HDL are mg/dL. The operator is unchanged; each standardized effect is multiplied by that dataset's scaling SD. All contrasts remain present, including rural lipid discrepancies.

'''+primary_table(True)+'''

![All lifestyle contrasts in standardized outcome units](paper_figures_v31_2026-11-11/figS8-lifestyle-standardized.pdf)

**Figure S8. Standardized view of the complete lifestyle analysis.** The same records, estimates and plotting conventions as Figure 3 are used, with effects divided by each dataset's pooled outcome SD. This view can appear closer when virtual variation is lower; the raw-unit main figure and Table S23 retain that distinction. No overlap rule or retrospective equivalence margin is applied.

**Table S24. All lifestyle sample, scale and interaction diagnostics.** The same three outcome checks are retained for every table. A nominal interaction p<0.05 marks the source-style sex-specific branch; all pooled and sex-specific estimates remain in the complete export irrespective of selection. Virtual intervals condition on a fixed law and do not quantify uncertainty in evidence or transport.

| Dataset | Trait | n | SD in raw units | Interaction p | Selected branch |
|---|---|---:|---:|---:|---|
'''
for d in data:
    did='Reference' if d['kind']=='real_reference' else d['dataset_id'].replace('LIFESTYLE_','')
    for t in d['analysis']['trait_status']:
        v=next(x for x in d['analysis']['interactions'] if x['trait']==t['trait'])
        supp+=f"| {did} | {label[t['trait']]} | {t['n']} | {t['sample_sd']:.3f} | {v['p_value']:.5f} | {'Sex-specific' if v['selects_sex_specific'] else 'Additive'} |\n"
supp+='''
All 189 contrasts and 21 interaction tests were independently recalculated with a separate positional CSV parser and statsmodels QR/contrast/likelihood implementation. The audit compared 4,690 numerical values within 5,846 checks; maximum absolute difference was 8.52e-13. The [full aggregate export](../work/lifestyle_application_2026-11-11/ANALYSIS_CONTRASTS.csv) retains all 18 sex-specific contrasts per dataset in addition to the nine additive results. The [protocol](../work/lifestyle_application_2026-11-11/PROTOCOL.md), [complete results](../work/lifestyle_application_2026-11-11/RESULTS.md) and [independent recomputation](../work/lifestyle_application_2026-11-11/review/INDEPENDENT_NUMERICAL_REVIEW.json) define the exact interpretation and preserve the no-op decisions. A pre-API documentation hash race was rejected before any paid dispatch and recorded before stable inputs were rebound; it changed neither the scientific packet nor the task or budget. These local audits have not yet been newly synchronized to public GitHub.

### S25. Fixed correlation analysis on existing real and virtual records

The separate analysis-only reuse unit applied one age/sex-adjusted Pearson function to all preselected frozen tables. It did not execute or revise a generator. Three pairs were retained: BMI-TC, BMI-HDL and TC-HDL. The real sample comprised 396 common-complete adults under age>18, versus the older lipid reference's different age/case/conditioning definition. This source-Methods-guided subanalysis does not reproduce the full ten-biomarker matrix or establish agreement with unchanged author code. Every pair in all six initial constructions and both already completed dependent repairs was retained.

**Table S25. Complete existing-table correlation reuse.** Entries are means and ranges across each law's three saved draws. The reference is one selected real sample, not a known population coefficient. Repairs are dependent on their existing starting law. These age/sex-only correlations must not be substituted for the older age/sex/BMI-adjusted lipid residual correlation.

| Existing law / role | BMI-TC | BMI-HDL | TC-HDL |
|---|---:|---:|---:|
'''
q=pd.read_csv(Q/'PAIR_RESULTS.csv')
pairs=['bmi__total_cholesterol','bmi__hdl_cholesterol','total_cholesterol__hdl_cholesterol']
for ep in q.episode.drop_duplicates():
    g=q[q.episode==ep];vals=[]
    for pair in pairs:
        v=g[g.pair==pair].r;assert len(v) in [1,3]
        vals.append(f'{v.iloc[0]:.3f}' if len(v)==1 else f'{v.mean():.3f} [{v.min():.3f}, {v.max():.3f}]')
    supp+='| '+str(ep)+' / '+str(g.role.iloc[0]).replace('_',' ')+' | '+' | '.join(vals)+' |\n'
supp+='''
The initial-law means overstate the sample BMI-TC correlation (0.185-0.314 versus 0.070) and understate TC-HDL correlation (0.121-0.363 versus 0.498). BMI-HDL means range from -0.147 to approximately -0.0005 versus -0.117; one near-zero law changes sign between draws. Dependent repairs do not remove these magnitude differences. A separate covariance/Schur-complement implementation verified all 75 correlations and their squared values, with maximum absolute difference 1.33e-15. The [complete reuse report](../work/published_analysis_replay_2026-11-11/RESULTS.md) preserves all 24 virtual tables, the common analysis definition, exclusions and uncertainty interpretation. It is a developmental comparison of existing records, not additional independent construction or a new clinical validation family.
'''
s=s.rstrip()+supp+'\n'
put(M/'DRAFT_v0_31.md',s)
for name in ['build_review_copy.py','compile_review.py','verify_review_copy.py','OVERLEAF_README.md']:
    content=(M/'methods_draft_v30_2026-11-11'/name).read_text(encoding='utf-8')
    content=content.replace('v0.30','v0.31').replace('v0_30','v0_31').replace('v30','v31')
    if name=='build_review_copy.py':content=content.replace("'S22.', 'S23.'","'S22.', 'S23.', 'S24.', 'S25.'")
    put(B/name,content)
dump(I/'STATE.json',dict(status='draft_integrated_pending_figures_build_review',version='0.31',new_api_calls=0,new_generated_tables=0,new_patient_analyses=0,public_sync=False))
print(json.dumps(dict(new_draft=str(M/'DRAFT_v0_31.md'),preserved_files=len(bindings),supplements=25)))

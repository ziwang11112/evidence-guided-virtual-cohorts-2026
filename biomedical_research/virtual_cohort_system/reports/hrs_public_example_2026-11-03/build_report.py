"""Write an analysis-use report from the complete, reviewed aggregate table."""
from pathlib import Path
import json

U=Path(__file__).resolve().parent
data=json.loads((U/'summary/AGGREGATE_RESULTS.json').read_text())
effects={(r['arm'],r['term']):r for r in data['fixed_effects']}
diagnostics={(r['arm'],r['metric']):r for r in data['distributions']}
def span(r):return f"{r['mean_estimate']:.5f} [{r['min_estimate']:.5f}, {r['max_estimate']:.5f}]"
def f(v):return f'{v:.5f}'
text=['# HRS published-example results: complete longitudinal virtual cohorts',
'', '3 November 2026 (America/Chicago). All numerical values below come from retained aggregate files.', '',
'## What was tested','',
'A fresh scientific Agent received the original published HRS aggregate model exports and method code, a whole-cohort task and the intended analysis. It produced its own executable recursive model and parameter/evidence record. The comparator reconstructs the published recipient-stage law. No HRS participant records were used. This is a source-rich reconstruction case: the analysis coefficients were legitimate inputs, so this case evaluates implementation and analysis preservation, not discovery of unseen relationships.', '',
'Each delivered table has **11,509 synthetic subjects and four visits at 0,2,4,6 years: 46,036 rows**. The task includes conditional demographics, childhood socioeconomic status, education, Gamma-distributed HbA1c, a two-branch HbA1c spline, interactions with age, and correlated subject random intercepts/slopes for memory. The same native R/lme4 model evaluates all outputs.', '',
'## Complete accounting and implementation correction','',
'The original allocation produced six tables: three Agent tables and three attempted published-law reconstructions. All three initial comparator tables were invalid because our CRLF-sensitive metadata parser silently overwrote the seven HbA1c coefficient/SE pairs with same-named terms from later model sections. The initial root/source preflight assessment was therefore insufficient and was explicitly overturned. These are our implementation failures; they are not evidence against the published method.', '',
'A separately documented technical recovery replaced only those seven pairs and their source locators from the original text. The generator program remained byte-identical. Independent model-specific extraction, LF/CRLF and malformed-section checks preceded three additional comparator attempts. No Agent model or table was regenerated. The original six attempts and all failed records remain intact.', '',
f"**Total physical generations: {data['counts']['total_physical_generations']}; invalid initial comparator tables: 3; valid comparison tables: {data['counts']['valid_comparison_tables']}.** Six delivered tables contain 276,216 synthetic visit rows in total, but represent repeated draws from two constructions, not six independent studies or additional clinical observations.", '',
'See [initial protocol](PROTOCOL.md), [recovery protocol](recovery_v1/PROTOCOL.md), [incident](recovery_v1/INCIDENT_AND_CORRECTION.md) and [frozen recovery](recovery_v1/RELEASE.json).','',
'## The two prespecified longitudinal relationships','',
'Values are the mean of three fixed seeds, with the observed seed range in brackets. Source values are the more precise published model exports; ranges are Monte Carlo summaries, not confidence intervals for a population parameter.','',
'| Analysis coefficient | Exported source | Agent mean [range] | Corrected published law mean [range] |',
'|---|---:|---:|---:|']
for term in ['age60:hba1c_U65','age60:hba1c_O65']:
    a=effects['agent',term];n=effects['native',term]
    text.append(f"| `{term}` | {a['exported_coefficient']:.6f} | {span(a)} | {span(n)} |")
text += ['',
'The Agent retains the negative below-threshold HbA1c–age relationship in all three seeds. The above-threshold interaction is positive in all three Agent draws, but its magnitude is higher than the supplied coefficient; one Agent draw has a synthetic-model Wald interval excluding zero although the source interval includes zero. Exact significance decisions are therefore not preserved across every draw. All seed-specific estimates, SEs and intervals are retained.', '',
'The corrected comparator has negative above-threshold point estimates in these three draws, with intervals including zero. This weak relationship therefore does not have a stable point-sign across the two implementations. Both use essentially the same published family; three draws and different random-effect sampling implementations do not establish an accuracy ranking.', '',
'![Two focal relationships](figures/focal_longitudinal_relationships.png)', '',
'## All 16 fixed effects','',
'| Term | Exported source | Agent mean [range] | Corrected published law mean [range] |',
'|---|---:|---:|---:|']
for term in [r['term'] for r in data['fixed_effects'] if r['arm']=='agent']:
    a=effects['agent',term];n=effects['native',term]
    text.append(f"| `{term}` | {a['exported_coefficient']:.6f} | {span(a)} | {span(n)} |")
text += ['', '![All fixed effects](figures/all_16_fixed_effects.png)', '',
'[Every seed and its SE/interval](summary/fixed_effects_all_seeds.csv) and [all signed/absolute discrepancy summaries](summary/fixed_effects_summary.csv) are available. We do not combine unlike coefficients into a single winner score.', '',
'## Distribution quality and the original-study reference','',
'The complete 27-field baseline comparison is retained in [all-seed diagnostics](summary/distributions_all_seeds.csv) and [summaries](summary/distributions_summary.csv). These include every applicable HRS Table2 distribution field, categorical counts and percentages. Key biomarker checks are shown here:', '',
'| Diagnostic | Paper original | Paper synthetic (5000-draw average) | Agent three-draw mean | Corrected published-law mean |',
'|---|---:|---:|---:|---:|']
for metric in ['baseline_age_mean','baseline_age_sd','hba1c_mean','hba1c_sd','hba1c_below_mean','hba1c_below_sd','hba1c_above_mean','hba1c_above_sd','baseline_mem_s_mean','baseline_mem_s_sd']:
    a=diagnostics['agent',metric];n=diagnostics['native',metric]
    text.append(f"| `{metric}` | {f(a['original_reference'])} | {f(a['published_synthetic_reference'])} | {f(a['mean_estimate'])} | {f(n['mean_estimate'])} |")
text += ['',
'The Agent closely reproduces the supplied simulation law, including its limitations. The upper-HbA1c subgroup has much narrower spread than the original reported cohort, while approaching the original paper\'s synthetic-data spread. Analysis preservation and complete empirical distribution recovery are therefore separate outcomes. The synthetic-law agreement does not erase the original-sample mismatch.', '',
'## Verification and interpretation','',
f"All {data['counts']['computed_fits']} retained comparison fits returned the 16 specified fixed effects; {data['counts']['gls_passes']} independent GLS checks passed. R fits retain optimizer, warnings, singularity, variance components and input hashes. Python independently recomputes fixed coefficients and SE conditional on fitted variances; this is not an independent REML-optimizer validation.", '',
'This case adds a concrete capability result to the manuscript: the evidence-guided workflow can construct an entirely virtual longitudinal cohort with conditional variables, repeated observations, interactions and correlated individual effects, and that data product supports the corresponding published scientific analysis. It complements the earlier cross-sectional and variable-enrichment work.', '',
'The case does not establish a new simulation family, superior statistical accuracy, automatic literature search, lower human effort, population transport, causal effects, or replacement of actual measurements. The Agent selected the already published family; its use of the printed variance column instead of squared rounded SDs is disclosed. Both arms use the same rich source information. Only three draws per construction were run, versus 5000 in the original study, and balanced synthetic visits differ from the source\'s 43,500 observed visits.', '',
'## Decision','',
'Include this as a published-example reconstruction and longitudinal-capability result. Preserve the parser incident and all outputs. The bounded experiment and technical recovery are closed: no further tuning or favorable-seed search. Continue manuscript integration around usable evidence-guided data, with the original upper-tail mismatch and conditional-uncertainty limits stated explicitly.', '',
'Original reference: [Filshtein et al., Proof of concept example for use of simulation to allow data pooling despite privacy restrictions](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/). Published code is pinned to [6708e43](https://github.com/powerepilab/Sim_for_data_pooling/tree/6708e43d5e342fa76d57b31d5a6d0bfcc2979539). Third-party originals and all row-level tables stay local.','']
(U/'RESULTS.md').write_text('\n'.join(text),encoding='utf-8')
print('Wrote aggregate-derived RESULTS.md')

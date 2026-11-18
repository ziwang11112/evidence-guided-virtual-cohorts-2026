"""Close one completed experiment from sealed aggregate artifacts; no model calls or generation."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv, hashlib, json, math

W=Path(__file__).resolve().parent
P=W.parents[1]
def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj): p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def require(value,message):
    if not value: raise RuntimeError(message)

require(not (W/'RUNNING.lock').exists(),'Run remains active')
require(not (W/'CLOSEOUT_QA.json').exists(),'Closeout already exists')
cc=read(W/'CONSTRUCTION_CLOSURE.json')
ec=read(W/'EXECUTION_CLOSURE.json')
slots=read(W/'analysis/SLOT_ACCOUNTING.json')
details=read(W/'analysis/details.json')
arm_rows=read(W/'analysis/arm_results.json')
author_rows=read(W/'analysis/author_results.json')
seed_rows=read(W/'analysis/seed_results.json')
refs=read(W/'analysis/REFERENCE_USED.json')['PNS']
costs=read(W/'analysis/COSTS.json')
review=read(W/'PROGRAM_INSPECTION.json')
arms=['BASE','SUMMARY','JOINT']
names={'BASE':'Base evidence','SUMMARY':'Base + marginal summaries','JOINT':'Base + summaries + joint block'}
keys=['residual_correlation','bmi_sbp','bmi_dbp','sbp.sd_population','dbp.sd_population']
labels={'residual_correlation':'Residual correlation','bmi_sbp':'BMI–SBP slope (mmHg / 5 kg/m²)',
        'bmi_dbp':'BMI–DBP slope (mmHg / 5 kg/m²)','sbp.sd_population':'SBP SD (mmHg)',
        'dbp.sd_population':'DBP SD (mmHg)'}
A={(r['arm'],r['estimand']):r for r in arm_rows}
B={(r['id'],r['estimand']):r for r in author_rows}
S={(r['id'],str(r['seed']),r['estimand']):r['value'] for r in seed_rows}
receipts={r['id']:read(W/'calls'/r['id']/'receipt.json') for r in cc['rows']}
require(len(cc['rows'])==9 and len(details)==27 and slots['successful_tables']==27,'Slot mismatch')
require({r['id'] for r in review['constructions']}==set(receipts),'Incomplete program inspection')
require(all(r['program_inspected'] and r['finite_relevant_moments'] for r in review['constructions']),'Incomplete law review')
protected={}
for r in cc['rows']:
    folder=W/'candidates'/r['id'];seal=read(folder/'SEAL.json')
    require(sha(folder/'SEAL.json')==r['seal_sha256'],'Seal hash mismatch')
    require(sha(W/'calls'/r['id']/'receipt.json')==seal['api_receipt_sha256']==r['call_receipt_sha256'],'API receipt mismatch')
    for name,h in seal['files'].items():
        require(sha(folder/name)==h,'Frozen candidate modified')
        protected[(folder/name).relative_to(P).as_posix()]=h

quality={
    'successful_tables':len(details),
    'fictional_rows_total':sum(x['statistics']['quality']['n'] for x in details),
    'unique_table_hashes':len({x['generated_sha256'] for x in details}),
    'duplicate_measurement_rows':sum(x['statistics']['quality']['duplicate_measurement_rows'] for x in details),
    'component_violation_count':sum(x['statistics']['quality']['component_violation_count'] for x in details),
    'nonpositive_counts':{k:sum(x['nonpositive_counts'][k] for x in details) for k in ['bmi','sbp','dbp']},
    'rank_values':sorted({x['statistics']['quality']['design_rank'] for x in details}),
    'any_row_filtering':any(x['statistics']['quality']['row_filtering'] for x in details)
}
require(quality['unique_table_hashes']==27,'Repeated delivered tables')
require(quality['rank_values']==[4] and not quality['any_row_filtering'],'Rank or filtering issue')
for x in details:
    folder=W/'executions'/x['id']/str(x['seed'])
    r=read(folder/'execution.json')
    require(r['isolation']=='WSL/bubblewrap only; no fallback' and not r['target_reference_read'],'Isolation/reference mismatch')
    require(sha(folder/'output/generated.csv')==x['generated_sha256'],'Generated table changed')
with (W/'figures/PLOTTED_VALUES.csv').open(encoding='utf8',newline='') as f: plotted=list(csv.DictReader(f))
for r in plotted:
    k=r['kind']
    if k=='sample_reference': expected=refs[r['panel']]['value']
    elif k=='draw': expected=S[(r['id'],r['seed'],r['panel'])]
    elif k=='constructor_mean': expected=B[(r['id'],r['panel'])]['seed_mean']
    elif k=='receipt_tariff_cost': expected=receipts[r['id']]['tariff_cost_usd']
    else: raise RuntimeError('Unknown plot kind')
    require(math.isclose(float(r['value']),expected,abs_tol=1e-12,rel_tol=1e-12),'Plot value mismatch')
coverage=dict(Counter(r['kind'] for r in plotted))
require(coverage=={'sample_reference':5,'draw':135,'constructor_mean':45,'receipt_tariff_cost':9},'Incomplete plotted profile')
summary_error=A['SUMMARY','residual_correlation']['author_mean_absolute_reference_difference']
joint_error=A['JOINT','residual_correlation']['author_mean_absolute_reference_difference']
reduction=1-joint_error/summary_error
contrast={'primary':'JOINT versus SUMMARY mean absolute residual-correlation difference',
          'summary_mae':summary_error,'joint_mae':joint_error,
          'absolute_reduction':summary_error-joint_error,'relative_reduction':reduction,
          'uncertainty':'descriptive, three independent construction calls per arm in one exposed case; no inferential interval'}
write(W/'analysis/PRIMARY_CONTRAST.json',contrast)
write(W/'analysis/QUALITY_AND_HASHES.json',quality)
write(W/'INSPECTED_PROGRAM_HASHES.json',protected)
main_table='| Analysis | Existing sample reference | Base | + summaries | + joint block |\n| --- | ---: | ---: | ---: | ---: |\n'
error_table='| Analysis | Base MAE | + summaries MAE | + joint block MAE |\n| --- | ---: | ---: | ---: |\n'
for k in keys:
    main_table+='| '+labels[k]+' | '+f"{refs[k]['value']:.4f}"+' | '+' | '.join(f"{A[a,k]['author_mean']:.4f}" for a in arms)+' |\n'
    error_table+='| '+labels[k]+' | '+' | '.join(f"{A[a,k]['author_mean_absolute_reference_difference']:.4f}" for a in arms)+' |\n'
author_table='| Construction | Residual r | Residual-r MAE | BMI–SBP | BMI–DBP | SBP SD | DBP SD | Estimated USD |\n| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n'
for name in sorted(receipts):
    vals=[B[name,k]['seed_mean'] for k in keys]
    cells=[vals[0],B[name,'residual_correlation']['mean_absolute_reference_difference'],*vals[1:]]
    author_table+='| '+name+' | '+' | '.join(f'{v:.4f}' for v in cells)+f" | {receipts[name]['tariff_cost_usd']:.5f} |\n"

report=f"""# PNS evidence-content control — completed result

16 November 2026 local; closeout UTC {datetime.now(timezone.utc).isoformat()}.

**Adding the same paper's joint correlation block improved the requested residual-dependence analysis; adding its marginal summaries alone did not.** The benefit was specific: BMI slopes did not improve. This completes the frozen bounded comparison; no further construction or tuning is scheduled by this report.

## What was run

One already exposed PNS case, three evidence conditions, three fresh GPT constructions per condition, three fixed sampling seeds per construction. All **9 constructions and 27 tables** succeeded. Each table contains 3,000 entirely virtual people; the 81,000 rows are Monte Carlo outputs, not 81,000 independent empirical observations. A program-writing Agent chose each population law and its parameters. The host provided approved source information, enforced the interface and executed the program in isolation.

The existing base packet was identical. SUMMARY added one Burkina Faso paper's population/measurement context and univariate moments. JOINT added exactly six reported same-sample pairwise correlations to that same packet. No source-derived partial correlation or target parameter was put in either prompt. The baseline already contained INTERSALT relationship information and Beijing raw covariance context: SUMMARY is a **marginal-only increment**, not a wholly relationship-free condition.

This follows the previous PNS two-arm result but uses nine fresh authors and one additional source, not the previous two-source augmented packet. Existing source retrieval was reused. This unit does not test autonomous search or compare our workflow with an ordinary Agent.

## Full scientific result

Entries below are averages of each constructor's three saved draws, then equally averaged across the three constructors. They are not statistics fitted to pooled synthetic rows.

{main_table}

The frozen primary endpoint is average absolute difference, computed **per saved draw**, averaged within construction, then across constructions:

{error_table}

For residual correlation, SUMMARY MAE was **{summary_error:.6f}** and JOINT MAE was **{joint_error:.6f}**, a descriptive **{100*reduction:.2f}% reduction**. Base MAE was {A['BASE','residual_correlation']['author_mean_absolute_reference_difference']:.6f}. The JOINT group's mean r of 0.7251 partly averages under- and over-shoots; its difference of about 0.008 from the reference must **not** replace the preregistered MAE of about 0.035.

All three joint-informed constructions had lower residual-r MAE than each of the three summary-only constructions in this small run. JOINT_3 overshot the reference, while JOINT_1 and JOINT_2 undershot. The six source correlations did not remove transport uncertainty.

SBP dispersion was closer on average. BMI–SBP MAE increased from 0.3396 in SUMMARY to 0.5091 in JOINT, and BMI–DBP MAE was 0.7378 versus 0.7550. All nine DBP slope means remained above the sample reference. DBP SD remained below it. Thus this result supports a targeted dependence benefit, not uniform improvement of the table or all its scientific analyses.

## Every construction

{author_table}

Full draw-level results, including seed minima and maxima, are in [analysis/seed_results.csv](analysis/seed_results.csv) and [analysis/author_results.csv](analysis/author_results.csv). There were no discarded authors, replacement calls, seed searches, row trimming or post-evaluation model edits.

## What the Agent actually did

All three JOINT authors independently derived the external paper's age/BMI-adjusted residual correlation, approximately 0.788, from its reported correlation matrix. The source transformation is ordinary projection algebra, not a new statistical estimator, and it does not include sex adjustment.

- JOINT_1 documented the source projection and chose an explicit target innovation correlation of 0.70 as a transport assumption.
- JOINT_2 independently documented the same source projection, also chose 0.70, and built bounded paired innovations with a covariate-dependent common support scale.
- JOINT_3 assembled the source covariance blocks in its sampler and computed the Schur complement there. It then used a conditional Student-t construction and physiological support restrictions.
- All six BASE/SUMMARY authors chose nominal innovation correlation 0.55 as an assumption informed by older raw-correlation context. They did not derive the missing adjusted dependence from marginal moments.
- All nine retained INTERSALT's converted BMI anchors, 3.877 and 2.9835 mmHg per 5 kg/m², under stated transport assumptions. This helps explain why the added dependency block did not systematically repair the BMI slopes, although it does not establish causal mediation.

The source-only answer and desired target value were not hand-entered by the root task. The root did curate the evidence cards and mask fields. This contribution should therefore be described as an **evidence-content intervention on Agent construction**, not a fully automatic source-admission achievement.

Conditional rejection, nonlinear age terms and heterogeneous residual scales mean an innovation parameter need not equal the final regression-residual correlation or slope. That is why the saved datasets were actually analyzed rather than substituting declared model numbers for results.

## Implementation and verification

- Requested and returned model: **gpt-6.1-sol**, high reasoning, nine fresh contexts, no tools, no retries or revisions in this diagnostic.
- Estimated construction cost **USD {costs['author_tariff_usd']:.7f}**, under the USD3 ceiling. This is usage valued at the stored tariff, not an invoice, and excludes earlier source retrieval and development.
- Input tokens {costs['author_usage']['input']:,}; cached input tokens {costs['author_usage']['cached']:,}; output tokens {costs['author_usage']['output']:,}, including {costs['author_usage']['reasoning']:,} reasoning tokens. Reasoning tokens are not added again to output.
- Every program/specification was sealed before sampling; all constructions closed before final execution. Generation ran only in WSL/bubblewrap with no host fallback.
- All **162 endpoint calculations** agreed with the separate QR implementation, maximum absolute difference **8.62e-14**. This is independent numerical implementation, not a second external scientific reviewer.
- Full code and model declarations of all nine programs were inspected. Their released variables are bounded, so relevant moments are finite. No generator was changed as a result of inspection.
- All 27 table hashes are distinct. No duplicate measurement rows, nonpositive BMI/BP, SBP below DBP or rank-deficient design was observed. These checks do not certify every clinical feature of the generated people.
- All **770 existing files** in the previous closed PNS experiment remained unchanged.
- The figure includes all 135 saved-draw scientific values, 45 construction means, five reference values and nine costs; all **194 plotted values** reconcile with the closed outputs. PNG was visually inspected for legibility and clipping.

The reference is an already exposed weighted complete-case PNS laboratory-substudy estimate. It is neither an exact population truth nor a new protected confirmation. Authors were not given its results. No real-patient refit or new dataset download occurred.

## Interpretation for the paper

Supported wording:

> In a frozen developmental PNS comparison, adding a same-source joint correlation block improved the residual-dependence analysis beyond adding that paper's marginal summaries. Agents independently translated the block into conditional covariance reasoning, while improvements did not extend uniformly to regression slopes.

The experiment strengthens the link **requested scientific analysis → relevant missing relation → source evidence → Agent-authored joint law → analysis of virtual data**. It supplies a control against the simpler explanation that any extra paper or extra marginal summaries would have produced the same observed benefit.

What it does not establish:

1. A general effect across diseases, target populations or model families. This is one selected, previously positive and exposed case with three construction calls per arm.
2. Novelty of conditional covariance algebra or information supplied by correlation matrices.
3. That the full six-correlation composition, rather than the new raw SBP–DBP correlation alone, is the uniquely active ingredient. This pilot compares the complete joint block.
4. Token-length/attention equivalence: JOINT necessarily contains additional informative numbers. Prompt and call ceilings are common, but payload lengths differ.
5. Clinical equivalence, target-population identification, universal synthetic-data suitability, retrieval-policy superiority or feedback benefit.
6. That the synthetic table can replace measurements of individual participants.

## Decision and next work

**Complete this unit and retain the targeted positive result with the full mixed profile.** Do not retune the exposed PNS laws or add paid calls to improve its slopes. Use the result as the evidence-content-control subsection beside the artificial composition experiment and the scientific-use examples. A proposed insertion is provided separately; v0.32 has not been silently overwritten.

For a broader conference claim, the remaining substantive gap is repeatability of the same evidence-to-analysis mechanism in a separately admitted case with usable conditional evidence. The lipid source investigation remains closed at admission failure. A new case must be chosen on evidence/operator availability before target-performance inspection; this report does not authorize or launch another search or batch. The earlier matched-size lifestyle sampling diagnostic remains **planned, not run**.

## Artifacts

- [Frozen protocol](PROTOCOL.md), [source audit](SOURCE_AUDIT.md), [freeze receipt](GENERATION_FREEZE.json).
- [Program inspection](PROGRAM_INSPECTION.json), [inspected hashes](INSPECTED_PROGRAM_HASHES.json).
- [Independent recomputation](analysis/INDEPENDENT_RECOMPUTATION.json), [complete slot accounting](analysis/SLOT_ACCOUNTING.json), [costs](analysis/COSTS.json).
- [Complete result figure](figures/evidence_content_control.png), [vector PDF](figures/evidence_content_control.pdf), [editable SVG](figures/evidence_content_control.svg).
- [Closeout quality checks](CLOSEOUT_QA.json).

All generated rows, raw API exchanges and third-party source material remain local. No GitHub synchronization occurred in this unit.
"""
(W/'RESULTS.md').write_text(report,encoding='utf8')
insert=f"""# Proposed manuscript insert — evidence content control

Placement: after the developmental PNS joint-evidence follow-up. This is an addition for the next planned revision, not a replacement of frozen v0.32.

## Joint evidence, rather than additional marginal summaries

To distinguish the benefit of additional joint information from that of adding a paper's general descriptive information, we froze a three-condition follow-up on the existing PNS case. Three fresh Agent constructions per condition received either the historical packet, that packet augmented with one external study's population description and univariate summaries, or the same augmented packet plus six reported same-sample pairwise correlations. The model, task, construction interface and call ceilings were common. Agents chose their own scientific laws; the prompts supplied neither the derived source partial correlation nor the PNS result. Each frozen law produced three tables of 3,000 people, and the same analysis operator was applied to all 27 tables.

Adding marginal summaries left the residual-correlation MAE essentially unchanged (base 0.1632; summaries 0.1633), whereas adding the joint block reduced it to 0.0350 ({100*reduction:.1f}% relative reduction versus summaries). Every joint-informed construction had lower residual-correlation MAE than every summary-only construction in this run. All three joint-informed authors independently derived an approximately 0.788 age/BMI-adjusted source correlation; two chose a transported innovation correlation of 0.70, while the third used the derived source covariance. The same augmentation did not improve BMI slopes: SBP-slope MAE was 0.3396 versus 0.5091 and DBP-slope MAE 0.7378 versus 0.7550 for summaries versus the joint block. The complete endpoint profile is shown in the accompanying figure.

These results demonstrate a specific analytical benefit of adding relevant joint information in this developmental case. They do not identify which individual element of the joint block caused the benefit, establish an autonomous retrieval advantage, or constitute independent target-population validation. The case and its reference had already been exposed; the follow-up was selected after a prior favorable result. Three seeds quantify within-construction sampling variation, not additional independent Agent constructions. Source covariance projection is standard algebra, and the source adjustment excludes sex. Population and measurement transport remain assumptions.

**Figure caption.** Evidence-content control for the PNS developmental case. Panels show residual BP correlation, both BMI–BP slopes, both BP standard deviations and construction cost. Faint circles represent all three fixed draws from each of three constructions per condition; diamonds are construction means. Dashed lines indicate existing measured-sample references, not exact population truths or equivalence thresholds. The two augmented conditions include the same external paper, population context and marginal statistics; the joint condition additionally contains its six reported correlations. Full profiles include outcomes that did not improve. Costs use the stored API tariff and exclude earlier source retrieval.
"""
(W/'MANUSCRIPT_INSERT.md').write_text(insert,encoding='utf8')
write(W/'CLOSEOUT_QA.json',{
    'completed_utc':datetime.now(timezone.utc).isoformat(),'passed':True,
    'scope':'post-closure integrity, coverage and plotting reconciliation; no extra model or generator run',
    'programs_inspected':9,'sealed_candidate_files_unchanged':len(protected),
    'numerical_recomputation':read(W/'analysis/INDEPENDENT_RECOMPUTATION.json'),
    'old_input_check':read(W/'analysis/OLD_INPUT_CHECK.json'),
    'quality':quality,'plot_values_checked':len(plotted),'plot_coverage':coverage,
    'visual_review':'root viewed PNG; legible, complete panels and legend, no visible clipping',
    'primary_contrast':contrast,'api_cost':costs,
    'manuscript_v032_modified':False,'github_synced':False,'new_automation':False})
state=read(W/'STATE.json')
state.update({'status':'completed','updated_utc':datetime.now(timezone.utc).isoformat(),
    'actual_constructors':9,'successful_final_tables':27,'estimated_author_cost_usd':costs['author_tariff_usd'],
    'independent_endpoint_comparisons':162,'all_constructors_code_inspected':True,
    'decision':'stop bounded unit; targeted residual-dependence benefit with no slope improvement',
    'next':'use result in next planned manuscript integration; no automatic search, tuning or paid batch',
    'result':'RESULTS.md','manuscript_insert':'MANUSCRIPT_INSERT.md',
    'trigger':'foreground user continuation; not a scheduled run','new_automation':False})
write(W/'STATE.json',state)
print(json.dumps({'completed':True,'relative_primary_reduction':reduction,
    'quality':quality,'plot_values_checked':len(plotted),'estimated_usd':costs['author_tariff_usd']}))


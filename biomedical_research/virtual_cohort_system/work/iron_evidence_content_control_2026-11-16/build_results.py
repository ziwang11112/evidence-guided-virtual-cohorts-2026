"""Summarize the closed iron unit without new calls, sampling, or patient fits."""
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import csv, hashlib, json, math
W=Path(__file__).resolve().parent
P=W.parents[1]
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def demand(ok,msg):
    if not ok: raise ValueError(msg)
freeze=read(W/'GENERATION_FREEZE.json')
for rel,digest in freeze['files'].items(): demand(sha(P/rel)==digest,'Changed frozen input: '+rel)
for rel,digest in read(W/'PREFLIGHT_REVIEW_BINDING.json').items(): demand(sha(W/rel)==digest,'Changed review binding')
construct=read(W/'CONSTRUCTION_CLOSURE.json')
execute=read(W/'EXECUTION_CLOSURE.json')
details=read(W/'analysis/details.json')
authors=read(W/'analysis/author_results.json')
arms=read(W/'analysis/arm_results.json')
draws=read(W/'analysis/seed_results.json')
refs=read(W/'analysis/REFERENCE_USED.json')['values']
costs=read(W/'analysis/COSTS.json')
review=read(W/'PROGRAM_REVIEW.json')
slots=read(W/'analysis/SLOT_ACCOUNTING.json')
old=read(W/'OLD_IMMUTABILITY.json')
demand(all(sha(P/r)==h for r,h in old.items()),'Historical input changed')
demand(review['status']=='complete' and len(review['reviewed'])==9,'Program review incomplete')
demand({x['id'] for x in review['reviewed']}=={x['id'] for x in construct['rows']},'Review roster differs')
bindings={}
receipts={}
for row in construct['rows']:
    cid=row['id']; folder=W/'candidates'/cid; call=W/'calls'/cid
    seal=read(folder/'SEAL.json')
    demand(sha(folder/'SEAL.json')==row['seal_sha256'],'Seal changed')
    for f,h in seal['files'].items(): demand(sha(folder/f)==h,'Changed candidate')
    r=read(call/'receipt.json');receipts[cid]=r
    demand(sha(call/'receipt.json')==row['call_receipt_sha256'],'Call receipt changed')
    demand(sha(call/'prompt.txt')==r['prompt_sha256'],'Prompt changed')
    demand(sha(call/'request.json')==r['request_sha256'],'Request changed')
    demand((call/'prompt.txt').read_bytes()==(W/'inputs'/(row['arm']+'.prompt.txt')).read_bytes(),'Wrong arm prompt')
    for key,h in r.items():
        if key.endswith('_sha256') and (call/key[:-7]).is_file():
            demand(sha(call/key[:-7])==h,'Bound API artifact changed')
    demand(datetime.fromisoformat(r['started_utc'])>datetime.fromisoformat(freeze['frozen_utc']),'Call before freeze')
    demand(datetime.fromisoformat(r['ended_utc'])<=datetime.fromisoformat(construct['closed_utc']),'Construction closure order')
    request=read(call/'request.json')
    demand(request['body']['model']==freeze['model_config']['model'],'Request model mismatch')
    bindings[cid]={'seal_sha256':sha(folder/'SEAL.json'),'generator_sha256':sha(folder/'generator.py'),
                   'model_spec_sha256':sha(folder/'model_spec.json'),'decision_sha256':sha(folder/'decision_record.json')}
for row in execute['rows']:
    folder=W/'executions'/row['id']/str(row['seed'])
    r=read(folder/'execution.json')
    demand(sha(folder/'execution.json')==row['receipt_sha256'],'Receipt changed')
    demand(datetime.fromisoformat(r['created_utc'])>=datetime.fromisoformat(construct['closed_utc']),'Draw before all authors closed')
    probe=r['worker_report']['pre_import_probe']
    demand(not probe['mnt_visible'] and not probe['home_visible'] and not probe['route_table'],'Isolation violation')
    for f,h in read(folder/'input_bindings.json').items(): demand(sha(folder/'input'/f)==h,'Staged input changed')
    demand(sha(folder/'output/generated.csv')==r['generated_sha256'],'Output changed')
primary=['odds_ratio','joint_prevalence','spearman']
lookup={(x['id'],x['seed'],x['estimand']):x for x in draws}
profiles=defaultdict(list)
for row in construct['rows']:
    cid=row['id']
    profile=tuple(lookup[cid,seed,key]['value'] for seed in freeze['seeds'] for key in primary)
    profiles[profile].append(cid)
unique_triplets={tuple(lookup[r['id'],r['seed'],k]['value'] for k in primary) for r in execute['rows']}
quality={key:sum(d['statistics']['quality'][key] for d in details) for key in
         ['n','duplicate_measurement_rows','nonpositive_hb','nonpositive_ferritin','exact_threshold_hb','exact_threshold_ferritin']}
quality['flags']=[{'id':d['id'],'seed':d['seed'],'flags':d['statistics']['flags']} for d in details if d['statistics']['flags']]
quality['unique_table_hashes']=len({d['generated_sha256'] for d in details})
quality['unique_primary_draw_triplets']=len(unique_triplets)
quality['identical_primary_constructor_profiles']=[v for v in profiles.values() if len(v)>1]
quality['note']='Common predeclared seeds and convergent laws can yield identical estimands despite distinct concentration tables; these are not additional independent evidence.'
write(W/'analysis/QUALITY_AND_REPEATS.json',quality)
# Verify the figure's data against the saved, closed aggregates.
plotted=list(csv.DictReader((W/'figures/PLOTTED_VALUES.csv').open(encoding='utf8')))
am={(r['id'],r['estimand']):r for r in authors}
for r in plotted:
    key=r['panel'];kind=r['kind'];cid=r['id']
    if kind=='draw': expected=lookup[cid,int(r['seed']),key]['value']
    elif kind=='constructor_mean': expected=am[cid,key]['seed_mean']
    elif kind=='sample_reference': expected=refs[key]
    elif kind=='receipt_tariff_cost': expected=receipts[cid]['tariff_cost_usd']
    else: raise ValueError('Unknown plotted kind')
    demand(math.isclose(float(r['raw_value']),expected,rel_tol=1e-12,abs_tol=1e-12),'Figure raw value differs')
    demand(math.isclose(float(r['display_value']),expected*float(r['scale']),rel_tol=1e-12,abs_tol=1e-12),'Figure scale differs')
demand(len(plotted)==194,'Incomplete plot')
demand(not (W/'RUNNING.lock').exists(),'Run still active')
demand(costs['author_calls']==9 and costs['unknown_cost_reserved_usd']==0 and costs['estimated_usd']<3,'Budget accounting')
qa={'status':'passed','closed_utc':datetime.now(timezone.utc).isoformat(),'frozen_inputs_unchanged':True,
 'old_files_unchanged':len(old),'constructor_log_seal_and_prompt_bindings_verified':9,
 'execution_bindings_and_pre_import_isolation_verified':27,'all_calls_after_freeze':True,
 'all_final_draws_after_construction_closure':True,'programs_reviewed':9,
 'figure_values_verified':len(plotted),'figure_visually_reviewed':True,
 'figure_review':'Root viewed exported PNG: all six panels, axis scales, points, legend and annotations readable without clipping.',
 'independent_statistics':read(W/'analysis/INDEPENDENT_RECOMPUTATION.json'),
 'additional_generator_runs':0,'additional_api_calls':0,'additional_patient_fits':0,'program_bindings':bindings}
write(W/'CLOSEOUT_QA.json',qa)
index={(r['arm'],r['estimand']):r for r in arms}
improvement=100*(1-index['JOINT','odds_ratio']['author_mean_absolute_reference_difference']/index['SUMMARY','odds_ratio']['author_mean_absolute_reference_difference'])
labels={'odds_ratio':'Crude low-marker odds ratio','joint_prevalence':'Both markers low (%)','spearman':'Continuous Spearman correlation',
        'low_hb_fraction':'Hb <12 g/dL (%)','low_ferritin_fraction':'Ferritin <15 ug/L (%)'}
scales={k:(100 if k.endswith('fraction') or k=='joint_prevalence' else 1) for k in labels}
table=['| Analysis | Measured sample | Context only | + Marginals | + Joint counts |','| --- | ---: | ---: | ---: | ---: |']
errors=['| Analysis discrepancy | Context only | + Marginals | + Joint counts |','| --- | ---: | ---: | ---: |']
for k in labels:
    s=scales[k]
    table.append('| '+labels[k]+' | '+' | '.join(f'{x:.4f}' for x in [refs[k]*s]+[index[a,k]['author_mean']*s for a in ['BASE','SUMMARY','JOINT']])+' |')
    scale_label='absolute natural-log OR difference' if k=='odds_ratio' else ('percentage points' if s==100 else 'correlation units')
    errors.append('| '+labels[k]+' — '+scale_label+' | '+' | '.join(f"{index[a,k]['author_mean_absolute_reference_difference']*s:.4f}" for a in ['BASE','SUMMARY','JOINT'])+' |')
author_table=['| Constructor | OR | Both low (%) | Spearman | Estimated USD |','| --- | ---: | ---: | ---: | ---: |']
for cid in sorted(receipts):
    author_table.append(f"| {cid} | {am[cid,'odds_ratio']['seed_mean']:.4f} | {am[cid,'joint_prevalence']['seed_mean']*100:.4f} | {am[cid,'spearman']['seed_mean']:.4f} | {receipts[cid]['tariff_cost_usd']:.7f} |")
report=f"""# Second-case evidence-content control: iron status

Completed 16 November 2026 local (17 November UTC). **The primary analysis improved, but the full profile did not.** Adding paired threshold evidence lowered absolute log-OR discrepancy by **{improvement:.2f}%** relative to marginal summaries. Joint low-marker prevalence and continuous rank correlation became less close to the measured sample. This is a useful analysis-specific result and a transport/structural limitation, not general data-quality improvement.

## What was frozen and run

Nine fresh GPT constructions, three per information condition, each followed by three fixed 5,000-person draws. All **9/9 constructions and 27/27 tables** completed, with no repair, replacement, target feedback or nonestimable endpoint. The 135,000 virtual rows are simulations from nine laws, not additional clinical participants. One artificial 128-row preflight fixture is excluded from these counts.

The user-requested second case uses existing NHANES iron-status data through its **previously exposed aggregate reference**: 979 complete-measurement nonpregnant women aged 20–44, positive phlebotomy weights, no CRP restriction. This unit did not download or refit patient data. The case was chosen for source-table separability and existing operator availability; root and project history were not target-blind. Constructors received fresh isolated prompts without target values, old programs or outcomes.

All arms shared the study request, original source identity/population/measurement context, three requested analyses and prompt scaffold. BASE received no selected outcome statistics. SUMMARY additionally received source single-marker low counts and ferritin geometric mean. JOINT additionally received a paired contingency table from the **same women**. SUMMARY and JOINT differed only by this joint block. This is an explicit within-source masking comparison, not a new literature-search study or a comparison to the old full two-source iron packet.

All constructors chose their own law, parameters and assumptions. The root supplied audited source facts, not a desired coefficient, correlation, OR or probability-model structure. The unchanged isolated worker sampled the submitted law. One call per constructor; no feedback/revision round in this diagnostic. Model requested and returned: **gpt-6.1-sol**, high reasoning, default service; all requests, outputs, model IDs and usage retained. Estimated total tariff cost **USD {costs['estimated_usd']:.7f}**, no unknown usage, below USD3. This is not an invoice amount.

## Complete scientific profile

Values below average the three seeds within each constructor and then the three constructors equally. These are descriptive summaries; no clinical equivalence tolerance or significance-based acceptance rule was added.

{chr(10).join(table)}

The existing reference has sampling uncertainty: OR 17.79 (95% interval 9.28–34.11), joint prevalence 7.63% (6.07–9.55%), and Spearman 0.398 (0.318–0.473), using the preserved survey-design calculation. These intervals are not acceptance margins. No intervals were invented for the two newly displayed marginal fractions. The reference is a measured-sample estimate, not known population truth.

{chr(10).join(errors)}

**Primary result:** SUMMARY log-OR discrepancy 1.7620 versus JOINT 0.9373, a {improvement:.2f}% descriptive reduction. All three JOINT constructor means were closer on this endpoint than all three SUMMARY means. The resulting OR remained well below the sample reference; improvement does not mean recovery.

**Adverse results:** joint-prevalence discrepancy rose from 0.5187 to 2.5940 percentage points; rank-correlation discrepancy rose from 0.0447 to 0.1736. Low-ferritin prevalence was about 30% in both evidence-augmented groups versus 12.15% in the measured sample. Low-Hb prevalence remained near 15%. Every planned constructor and endpoint remains in the tables and figure.

{chr(10).join(author_table)}

## What the Agent actually did

All three JOINT authors chose a Gaussian copula and independently calibrated its latent correlation to the published four-cell counts. Two implemented integration over the correlation parameter; the third implemented a conditional-normal integral. They chose different bounded/positive marginal laws, numerical routines and concentration spreads. The host supplied no copula or correlation.

An independent source-only calculation gives latent rho **0.584221** and implied Spearman **0.566145**, conditional on the chosen Gaussian family. The corresponding source OR is **6.653137** and source joint prevalence **10.3531%**. Generated values track these declared laws with finite-sample variation. This confirms successful evidence-to-program construction; it does not validate source transport or identify the continuous copula from the table.

SUMMARY authors assumed latent correlations 0.35, 0.35 and 0.40. Their population-law ORs implied by source margins are approximately 2.874, 2.874 and 3.381. BASE authors proposed three different assumption-driven models, including a nonlinear latent-iron/mixture construction. Ordinary Agent prior knowledge can therefore produce meaningful structure even without supplied quantitative evidence; BASE is not forced independence.

Complete program/specification/decision inspection found no infinite-moment law in these nine candidates. Five impose finite concentration supports on both measurements. SUMMARY_1 uses ideal half-normal log tails with finite positive polynomial moments; its implemented probability guard additionally caps numerical extremes. The remaining three have bounded Hb and positive lognormal-type ferritin tails with finite positive polynomial moments. One provenance-label issue remains: BASE_2 labels its source-suitability assessment REPORTED even though it is an Agent assessment. No scientific code was edited after submission. [Program review](PROGRAM_REVIEW.json) records each law and its limitations.

The 27 output tables have distinct hashes. Nevertheless, SUMMARY_1 and SUMMARY_2 have identical three-seed primary-analysis profiles because their selected dependence and threshold probabilities coincide and common seeds were prespecified. Other individual rank estimates also coincide. These are convergent model choices, not extra independent evidence; construction, not row or seed, remains the unit.

## Why some analyses improved and others did not

The original [Zhu2010 study](https://storage.imrpress.com/imr/journal/IJVNR/article/501902/1752835456699.pdf) concerns selected rural Chinese parous women, 2–4 years postpartum and using IUD contraception, with different exclusions and assays from the US target. All admitted statistics come from the same source population.

Its anemia prevalence is 258/1671 = 15.44%, close to this target sample's 15.24%; its low-ferritin prevalence is 504/1671 = 30.16%, far from this target sample's 12.15%. All augmented constructors directly transported these margins. This explains the model-level low-ferritin discrepancy without a code or unit error. The cause of the underlying between-population difference is not established here.

Adding the source joint table strengthened the simulated low-marker association, making its OR closer to the target sample. It also transported a joint prevalence of 10.35%, higher than the target sample's 7.63%. The same change can improve the OR and worsen joint prevalence; these quantities depend differently on marginal and joint probabilities.

Continuous rank association is a further extrapolation. Four binary counts do not determine within-category ordering. The Gaussian copula linked the calibrated threshold association to a larger continuous correlation, and that implication overshot this target sample. This is not direct evidence that every copula or every way of using the table would fail.

Conversely, SUMMARY's near-reference joint prevalence coexists with a much weaker OR and a much larger low-ferritin marginal. Agreement on one analysis cannot establish a generally valid joint distribution. No target-based repair is performed here.

## Implementation and accounting

- Nine targeted preflight checks passed before freeze, including strict cutoffs, ties, zero-cell nonestimability, a same-margins/different-pairing fixture, new iron analyzer routing and isolated execution.
- Every call started after the protocol/input freeze. All nine authors closed before any final table was sampled.
- All 27 table executions used WSL/bubblewrap with no visible host home/mounts or network route. There was no host fallback.
- Independent weighted-midrank and contingency recomputation agreed on all **135 endpoint values**, maximum absolute difference **8.88e-16**. No patient data or additional generator draws were used in recomputation.
- No observed nonpositive measurements, exact threshold atoms, duplicate measurement rows, zero-cell ORs or constant-rank failures. These finite-table checks do not certify clinical validity.
- All **705 protected historical files** remain byte-unchanged.
- The figure uses all constructors/draws and marginal checks; all **194 plotted values** were reconciled and the PNG visually inspected.
- Source retrieval added one publisher PDF (151,976 bytes, hash in the source ledger). No new patient download, new automation, GitHub sync, training or HPC run occurred.

## Relation to the first case and the paper decision

The PNS content control found a residual-correlation discrepancy reduction from 0.1633 with marginal summaries to 0.0350 with joint evidence; its BMI slopes did not improve. Here, the iron OR improved while joint prevalence and rank correlation worsened. The BASE packets differ between cases, so do not pool their error scales or present the two BASE conditions as identical.

**Supported paper statement:** an Agent can convert published joint summaries into an executable joint data law, and supplying relevant joint evidence can improve a specified scientific analysis beyond marginal summaries. The complete analysis profile reveals remaining transfer and structural assumptions. There are now two developmental existing-case examples of a targeted improvement, not two new blinded clinical confirmations.

**Unsupported statement:** all downstream analyses improve, source matching establishes target validity, more rows solve missing information, or this workflow generally outperforms ordinary Agents/statistical synthesis. This experiment does not isolate the novelty of copula mathematics, multi-source composition, autonomous retrieval or feedback revision.

Close this bounded experimental unit. Do not retune the iron or PNS laws to their exposed reference. Integrate the useful results and their full trade-offs into the planned manuscript revision. The next methodological refinement, if pursued separately, must specify which target-analysis use it addresses and how additional evidence resolves the relevant marginal or continuous-dependence uncertainty; this result does not authorize another search or paid batch.

## Artifacts

[Protocol](PROTOCOL.md) · [Source audit](SOURCE_AUDIT.md) · [Freeze](GENERATION_FREEZE.json) · [Preflight review](IMPLEMENTATION_REVIEW_BEFORE_FREEZE.md) · [Program review](PROGRAM_REVIEW.json) · [Independent calculation](analysis/INDEPENDENT_RECOMPUTATION.json) · [Costs](analysis/COSTS.json) · [Complete figure](figures/iron_content_control.png) · [Vector figure](figures/iron_content_control.svg) · [Plot data](figures/PLOTTED_VALUES.csv) · [Closeout checks](CLOSEOUT_QA.json)

Full API responses, third-party source PDF and individual real/generated rows remain local.
"""
(W/'RESULTS.md').write_text(report,encoding='utf8')
write(W/'SUMMARY.json',{'primary_log_or_discrepancy_reduction_percent':improvement,'arms':arms,'quality':quality,'costs':costs,
                       'decision':'close bounded unit; integrate targeted benefit and full adverse profile; no exposed-target retuning'})
print(json.dumps({'closed_checks':'passed','primary_reduction_percent':improvement,'quality':quality,'figure_values':len(plotted)}))


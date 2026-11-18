"""Post-closure reporting and source-to-code audit; never calls a model or generator."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import json, hashlib, re
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def markdown(p,text):
    with p.open('x',encoding='utf-8',newline='\n') as f: f.write(text)

qa=read(ROOT/'analysis/CLOSEOUT_QA.json')
assert qa['status']=='pass' and qa['successful_slots']==18
cost=read(ROOT/'analysis/COSTS.json')
rows=read(ROOT/'analysis/author_results.json')
closed=read(ROOT/'CONSTRUCTION_CLOSURE.json')
assert all(x['candidate_id']=='v001' for x in closed['episodes'])

# Tool-history accounting uses delivered tool results, not private model reasoning.
traces=[];incidents=[]
for ep in sorted((ROOT/'episodes').iterdir()):
    outcome=read(ep/'OUTCOME.json'); counts=Counter();original=[];supplements=[];excluded=[]
    for a in sorted((ep/'tool_actions').iterdir()):
        q=read(a/'request.json');r=read(a/'result.json');counts[q['name']]+=1
        if q['name']=='read_provided_paper': original.append(q['arguments'])
        if q['name']=='read_source':
            supplements.append({'action':a.name,'source_id':q['arguments']['source_id'],
                                'section':q['arguments'].get('section'),'status':r.get('status','content_returned'),
                                'complete':r.get('complete'),'result_sha256':sha(a/'result.json')})
        if r.get('status') in ['rejected','selection_required']:
            excluded.append({'action':a.name,'tool':q['name'],'status':r['status'],'reason':r.get('reason')})
        for hit in r.get('hits',[]):
            preview=hit.get('abstract_preview','');title=hit.get('title','')
            if re.search(r'National Health and Nutrition|Brazilian Health Survey|National Health Survey|NHANES|ENSANUT',title+' '+preview,re.I):
                incidents.append({'episode_id':ep.name,'action':a.name,'hit_id':hit['hit_id'],
                    'pmcid':hit.get('pmcid'),'doi':hit.get('doi'),'title':title,
                    'result_sha256':sha(a/'result.json'),'preview_chars':len(preview),
                    'preview_scope':'source identity/methods/demographic preview; review separately; not an automatic leakage verdict'})
    traces.append({'episode_id':ep.name,'model':cost['requested_models'][0],
        'calls':outcome['calls_receipted'],'estimated_tariff_usd':outcome['known_tariff_cost_usd'],
        'tool_counts':dict(counts),'original_reads':original,'supplement_reads':supplements,
        'tool_usage':outcome['tool_usage'],'rejections_and_version_selection':excluded,
        'selected_candidate':outcome['selected_candidate'],'revisions':outcome['tool_usage']['candidates']-1,
        'candidate_sha256':{n:sha(ep/'candidates/v001'/n) for n in ['generator.py','model_spec.json','notes.json']}})
write(ROOT/'audit/TRACE_SUMMARY.json',traces)
write(ROOT/'audit/SEARCH_PREVIEW_REVIEW.json',{'reviewer':'root post-closure review of delivered results',
    'flagged_previews':incidents,
    'same_target_family_incident':{'episode_id':'P1_PNS_A2','action':'action_0011','hit_id':'hit_0002_006',
       'pmcid':'PMC8030866','doi':'10.1111/jch.13292',
       'exposed':'PNS2013/Brazilian Health Survey identity, n=59402, 56% female, ages18-100, measurement/design and qualitative topic',
       'requested_target_estimates_in_returned_preview':False,
       'author_action':'explicitly identified and excluded in selected notes; no subsequent read_source of this hit or PMCID',
       'interpretation':'Preserve exposure. No visible use does not prove absence of influence. Not a clean holdout.'},
    'other_flags':'PNS_A1 saw a Chile survey preview (different family) and NHANES2011-2020 cardiovascular-model preview; PNS_A2 saw a Mexican2018-2019 survey preview. None was opened or used as a declared parameter source. These are not the evaluated target estimands; retain their delivered-text hashes.',
    'screening_changes_in_this_batch':False})

# Independent deterministic recomputation of the Agent's derivations (not new sampling).
R=np.array([[1,-.17],[-.17,1.]])
s=np.array([.21,.12]);d=np.array([.02,.16]);inv=np.linalg.inv(R)
v_s=1-s@inv@s;v_d=1-d@inv@d
derived={'source_partial_r_age_bmi':float((.78-s@inv@d)/np.sqrt(v_s*v_d)),
         'source_residual_sd_sbp':float(18.22*np.sqrt(v_s)),
         'source_residual_sd_dbp':float(10.98*np.sqrt(v_d)),
         'bmi_sbp_per5_fully_adjusted_source':5*.75,
         'bmi_dbp_per5_fully_adjusted_source':5*.44,
         'iron_collapsed_cells':[173,85,331,1082],
         'iron_crude_or':173*1082/(85*331),
         'iron_source_joint_fraction':173/1671,
         'iron_source_anemia_given_low_ferritin':173/504,
         'iron_source_anemia_given_not_low_ferritin':85/1167,
         'interpretation':'Source algebra only; no claim these are target estimands or that source-only partialling includes sex.',
         'new_generator_runs':0}
write(ROOT/'audit/SOURCE_DERIVATION_RECHECK.json',derived)

reviews={
'P1_PNS_A1':{
 'structure':'Shifted-gamma BMI; age/sex-dependent pressure means; joint lognormal DBP and positive pulse pressure with pointwise moment/covariance mapping.',
 'checked':['Original Tables2/3 SDs and correlation entries match the XML; Tables5/6 BMI coefficients0.75/0.44 and adjustment sets retained.',
 'Agent independently derived age/BMI partial covariance and residual SD; setting0.788/17.6/10.8 is rounded and explicitly transported, not a reported sex-adjusted target result.',
 'Source BMI slopes multiplied by5, yielding3.75/2.20; code also includes chosen age curvature and sex-age terms, so requested OLS need not equal these inputs.',
 'Returned ELSA-Brasil PMC10752922 Methods and Tables1-3 support the recorded categorical gamma contrasts; they are not substituted for continuous OLS coefficients.',
 'Returned Mexico PMC5344187 v2 Methods/Results support the different measurement, exclusions, sex-specific BMI moments and approximate association context.',
 'Code implements declared gamma and conditional lognormal formulas without final-sample rescaling.'],
 'unresolved':['Source treatment/partnership/age selection differs from the target.','Target age, BMI, sex distribution and mean-function choices remain assumed.','Age/BMI partial correlation does not fully identify the requested sex-adjusted residual law.']},
'P1_PNS_A2':{
 'structure':'Shifted-lognormal BMI; shifted-lognormal DBP plus positive pulse pressure; transported residual covariance.',
 'checked':['Original Tables2/3/5/6 extraction agrees with original XML, including fully adjusted source slopes and raw versus partial-correlation distinction.',
 'Chosen DBP slope2.35 is explicitly assumed between related source projections; not falsely reported as an exact source estimate.',
 'The source covariance derivation is algebraically valid for age/BMI partialling, not for all target covariates.',
 'Mexico PMC5344187 v2 and Brazil screening PMC7455292 actual returned Methods/Results support recorded broad context; volunteer BMI27.3 SD4.5 and meanage54.5 are not used as exact target moments.',
 'Code implements declared conditional moments and positive pressure ordering; no target fitting or sample recentering observed.',
 'A target-family search preview reached the author and was explicitly excluded; preserve the exposure incident.'],
 'unresolved':['Demographic and target-lab selection law unobserved.','Marginal-to-conditional and treatment/measurement transport assumptions.','Source preview exclusion does not prove absence of contextual influence.']},
'P1_PNS_A3':{
 'structure':'Beta-distributed adult age, shifted-gamma BMI, ELSA-inspired pressure levels and original-paper slopes, positive DBP/pulse-pressure joint law.',
 'checked':['Original covariance/table extraction and age/BMI residual derivation match source and independent algebra.',
 'ELSA-Brasil PMC7433850 Table1 sex-specific BP/BMI moments and sample counts match the returned table; Methods specify civil servants35-74 and last-two BP readings.',
 'Vitoria PMC4541693 Methods/Results contain n272, age44 SD14 and selected sampling; used for qualitative age context, not exact national inference.',
 'Marginal ELSA BP means are turned into conditional intercepts with the approximation explicitly declared.',
 'Code matches the chosen means, lower-shift gamma, covariance and positive pulse law; no sample-wide calibration observed.'],
 'unresolved':['Civil-servant marginal moments do not uniquely determine conditional target levels.','Age curvature, older-female interaction and demographics are assumptions.','Source partial-correlation transfer remains uncertain.']},
'P1_IRON_A1':{
 'structure':'Canadian ferritin lognormal marginal plus a chosen truncated-normal Hb mixture linked by a lower-tail Clayton copula; copula parameter solved from source crude OR.',
 'checked':['Original eight TableIV rows aggregate to173/85/331/1082; code computes the crude OR from these counts. Adjusted TableV OR6.448 is explicitly not substituted.',
 'Agent recognizes conflicting ferritin units and broad geometric intervals; does not turn these intervals into individual SDs or use folate-B12 r0.16 as Hb-ferritin correlation.',
 'Canadian PMID36788041 actual returned abstract supports premenopausal GM33.8 and ferritin<15 prevalence16%; assay/pregnancy/overlap uncertainties are disclosed.',
 'NZ PMC10611866 returned Methods/Table2 support HemoCue fingerprick Hb and arithmetic subgroup means/SD. Agent correctly converts g/L to g/dL and avoids adopting CRP-adjusted ferritin as raw.',
 'Code derives lognormal spread from GM/prevalence, solves the population Clayton OR and samples iid rows; Hb mixture/coplanar family are explicitly assumptions.',
 'Bounded Hb and lognormal ferritin have finite relevant moments; the tiny endpoint guard is numerical protection, not outcome calibration.'],
 'unresolved':['Chinese crude OR is transported unchanged across population/confounding differences.','NZ mixture weights/means are chosen, not measured target demographics.','Threshold OR does not identify Spearman or the Clayton family.','Canadian ferritin source is abstract-only.']}}
for ep,record in reviews.items():
    record.update(episode_id=ep,reviewer='root source/code review, not external biomedical adjudication',
                  candidate_sha256=next(t['candidate_sha256'] for t in traces if t['episode_id']==ep),
                  science_edits_after_submission=False)
    write(ROOT/'audit'/f'{ep}.json',record)

trace_table='| Session | Model calls | Literature queries | Download attempts charged | Candidates / trials | Estimated USD |\n|---|---:|---:|---:|---:|---:|\n'
for t in traces:
    x=t['tool_usage'];trace_table+=f"| {t['episode_id']} | {t['calls']} | {x['queries']} | {x['downloads']} | {x['candidates']} / {x['executions']} | {t['estimated_tariff_usd']:.4f} |\n"
result_table='| Case / analysis | Author 1 mean | Author 2 mean | Author 3 mean | Measured sample reference |\n|---|---:|---:|---:|---:|\n'
orders={'PNS':['bmi_sbp','bmi_dbp','residual_correlation','sbp.sd_population','dbp.sd_population','sbp_below_dbp_fraction'],
        'IRON':['odds_ratio','joint_prevalence','spearman','low_hb_fraction','low_ferritin_fraction']}
for case,keys in orders.items():
    for k in keys:
        rr=sorted([r for r in rows if r['case_id']==case and r['estimand']==k],key=lambda r:r['episode_id'])
        result_table+=f"| {case} / {k} | "+' | '.join(f"{r['seed_mean']:.5f}" for r in rr)+f" | {rr[0]['reference']:.5f} |\n"

audit='''# Original-paper to model: source and implementation audit

17 November 2026 (America/Chicago). Root performed this source/code review using original materials, delivered tool results and all six immutable programs. Numerical analysis was separately recomputed with an independent implementation. This is not an external clinical adjudication or a validated confidence score.

## What the Agent actually did

All six fresh sessions accessed the original paper, chose additional searches, authored an executable generator plus parameters and provenance, inspected one generated-only trial, and retained their first candidate. Three original-paper BP constructors reconstructed an age/BMI partial covariance from the original correlation matrix. All three iron constructors independently collapsed the original eight-category table to a two-by-two table and distinguished crude from adjusted odds. These source derivations were not supplied in the task or by a coordinator-written numerical packet.

The coordinator supplied a known original-paper entry point, target-population/schema definition, analysis definitions, general model requirements, tools and budget. This demonstrates paper interpretation/model authorship from that entry point. It is not unaided discovery of the anchor study. The final records are sampled by the program written by the Agent; there is no host-authored scientific parameter template. The Agent chooses the probability law and numeric assumptions, and deterministic isolated tools execute it.

'''+trace_table+'''
Download counters are the adapter's charged attempts, including screened/failed full-text requests; they are not counts of distinct usable papers. Full tool paths, byte hashes and delivered source parts are in `audit/TRACE_SUMMARY.json`. Each candidate has one immutable version, one trial, and three subsequent final seeds. Therefore this experiment does not estimate a revision benefit.

## Source interpretation and composition

**Blood pressure.** The original [Burkina Faso study](https://doi.org/10.1136/bmjopen-2024-089374) supplies arithmetic SDs, a Pearson correlation matrix, and fully adjusted BMI coefficients. All three Agents correctly distinguish the raw SBP/DBP correlation from the age/BMI partial correlation they calculate. The latter is approximately0.788; source residual SDs are approximately17.6/10.8mmHg. It does not include sex adjustment. All authors explicitly mark transfer to a different age range, treatment-inclusive population, measurement protocol and smaller adjustment set as an assumption. Supplementary Mexican/Brazilian papers are actually retrieved, not merely named in the final notes. PNS_A1's gamma-regression overweight contrasts are context, not mislabelled as continuous BMI coefficients. PNS_A3 uses sex-specific ELSA marginal means as conditional anchors and discloses this approximation.

**Iron status.** The original [Zhu study](https://doi.org/10.1024/0300-9831/a000014) has eight rows split by folate/B12/ferritin status. Each author recovers173/85/331/1082, crude OR6.65314, and distinguishes TableV's adjusted OR6.448. Each also recognizes inconsistent ferritin unit labels and broad intervals around geometric means, and does not substitute folate/B12 correlation for Hb/ferritin. Supplemental Canadian summaries change the marginal ferritin assumptions rather than blindly carrying over the Chinese deficiency prevalence. Access to the Canadian source is abstract-level; its population and measurement applicability are not certified. A1 additionally uses New Zealand Hb data; A3 reads Dutch donor methods as qualitative mechanism context. Neither paper identifies the target joint law.

`audit/SOURCE_DERIVATION_RECHECK.json` records the independent arithmetic. These checks establish traceable extraction and algebra, not clinical portability or automatic source certification. The exact wording of confidence/interval labels remains the original source's ambiguity, not repaired evidence.

## Model choices and remaining assumptions

| Session | Actual model choice | Most consequential unresolved choice |
|---|---|---|
| PNS A1 | Gamma BMI; joint lognormal DBP and positive pulse pressure | Demographic law and covariance/fully adjusted slope transport |
| PNS A2 | Lognormal BMI; DBP shifted by30 plus positive pulse pressure | Marginal/conditional and selection transport; incidental preview |
| PNS A3 | Beta age; gamma BMI; ELSA pressure anchors; positive pulse pressure | Marginal source levels used as conditional intercepts |
| Iron A1 | Hb mixture, ferritin lognormal, Clayton copula solved from OR | Unmeasured Hb mixture and copula-dependent rank relationship |
| Iron A2 | Two store components, inflammation, Hb hinge response | Assumed5% background anemia; transferred crude OR |
| Iron A3 | Lognormal stores, inflammation/other anemia, saturating Hb response | Source stratum anemia risks transferred; assumed continuous law |

All selected programs match the declared major scientific structure and parameters on code inspection. The BP construction uses positive DBP and positive pulse pressure, so SBP>DBP structurally; all27000 final BP rows satisfy this. Bounded age and gamma/lognormal BMI have finite relevant moments; conditional pressure means are linear in BMI with bounded age terms and fixed finite conditional variances. Iron A1 has bounded Hb/lognormal ferritin; A2/A3 use finite lognormal mixtures and lower-truncated normal Hb. Inspection finds no version of the earlier infinite-mean construction here. This is mathematical inspection of the particular selected laws, not proof of biomedical realism for every tail.

No selected program reads target data or performs realized-sample moment forcing, seed selection or target-based correction. Algebraic root finding in the iron models calibrates a probability law to the chosen source constraints before sampling, which is legitimate source fitting. Some notes describe a numerical root as unique; a general uniqueness proof is not supplied and is not claimed in this report. Six distinct program hashes and18 distinct final table hashes are retained. No scientific code was edited after submission.

## Delivered-source exposure

The conservative screen was imperfect. PNS_A2 received an incomplete search preview for [DOI10.1111/jch.13292](https://doi.org/10.1111/jch.13292), identifying the2013 Brazilian survey, n59402,56%women, ages18–100, methods and the qualitative obesity/BP question. The author explicitly excluded it and did not open it. The delivered preview did not contain the evaluated BMI coefficients or residual correlation. There is no visible use as a parameter source, but absence of visible use does not prove no influence. Retain the author and flag; do not replace it. PNS_A1 also received an NHANES2011–2020 cardiovascular-model preview and a different Chilean survey preview, and PNS_A2 received a Mexican survey preview; none was opened or declared as an adopted source. Exact delivered-result hashes are retained.

The API authors never received the local target records, aggregate answer files or final target-comparison feedback. This narrower statement is supported. A claim of perfectly target-free literature exposure is not. Both target families were already exposed at project level in any event.

## Decision

The feasibility gap was real and is now addressed: these Agents read original tables, compose useful statistics, choose differing laws, write code and deliver analyzable cohorts without host-filled relationships. This does not make every generated relationship accurate. The blood-pressure slopes are promising in this closed batch; iron dependence and prevalence remain materially discrepant. Preserve both as the capability and its current boundary. No additional repair or construction is authorized by this completed protocol.
'''
markdown(ROOT/'SOURCE_MODEL_AUDIT.md',audit)

results='''# P1 results: original papers to analyzable virtual cohorts

17 November2026, America/Chicago. Status: closed after all six scheduled construction sessions and18 final tables. No replacement author, target-feedback revision, new dataset, training or HPC was used.

**Main finding:** with an original-paper entry point, the Agent itself can extract and compose numerical evidence, choose a scientific probability law and deliver a runnable whole-cohort generator. In this batch the generated BP data support approximately the same age/sex-adjusted BMI associations as the measured reference. Iron-state associations are positive but substantially weaker; source fidelity does not establish target fidelity.

## Frozen experiment and actual execution

Two existing cases, three fresh GPT sessions each, one final law per session and three final seeds17121/17123/17127. The BP schema has six columns and3000 rows; the iron schema has three columns and5000 rows. No target individual inputs are supplied. The final inventory is18 tables and72000 virtual rows, not72000 independent real participants or18 independent modeling decisions. The inferential replication unit is the construction/session within a case; final seeds only describe sampling from that fixed law.

The Agent receives the research request, output contract, exact desired analyses and access to a complete original XML or PDF-text paper. It may search additional literature, decide how to model the data, submit code and parameters, run a generated-only inspection, and revise once if needed. All six chose to retain their first model after one trial. Root added an original-paper reader and estimator routing, audited the interface, and froze the implementation, prompts, source bytes and analysis definitions before any paid construction. Root supplied no numerical evidence card, target slope, target mean, residual correlation or preferred generator family.

All six candidates and their histories were sealed before the final draws and target comparisons. The same established analysis estimators are used for generated data and the existing measured references. These are already exposed sample estimates, not known population truth or fresh clinical holdouts. No equivalence margin was chosen after observing the results.

## Complete result profile

Values below are means of the three fixed-seed results per author. The complete33 author-endpoint and99 seed-endpoint records, including all diagnostics, are retained in `analysis/`. Fractions are on0–1 scale. BP slopes are mmHg per5kg/m² BMI adjusted for age and sex; iron OR uses Hb<12g/dL and raw ferritin<15ug/L.

'''+result_table+'''
### What the analyses support

- **BP associations:** author means for BMI–SBP are3.402–3.804 versus reference3.524; BMI–DBP2.285–2.402 versus2.260. This supports approximate reproduction of these associations under the specified analysis, not a formal equivalence conclusion or intervention effect.
- **BP joint dependence and spread:** residual correlation0.772–0.781 exceeds reference0.717. SBP SD19.566–20.003 exceeds18.192; DBP SD11.472–11.569 exceeds11.094. All BP records respect SBP>DBP. Useful slopes do not imply the whole joint distribution is recovered.
- **Iron associations:** OR6.348–7.141 versus17.790 preserves a positive association but materially understates its strength. All authors calibrate to the same source crude OR6.653; this is a transparent source-transfer assumption, not evidence that the target OR should equal it.
- **Other iron analyses:** joint-low prevalence4.673–5.847% versus7.630%, rank correlation0.197–0.329 versus0.398, low-Hb prevalence8.807–11.727% versus15.240%, and low-ferritin prevalence15.680–18.513% versus12.153%. The common threshold constraint does not determine these other analyses. Supplemental marginal evidence and different model families do not remove their uncertainty.

No binary overall dataset-quality pass is assigned. The measured references have sampling uncertainty; proximity is encouraging for a specific analysis, while persistent larger discrepancies remain visible. The preceding P0 matched-size real–real diagnostic concerns the lifestyle case and is not silently transferred as an acceptance threshold for these BP/iron tasks.

## Evidence and code findings

All three BP authors recover the original covariance matrix and derive an age/BMI partial covariance instead of simply naming a paper. All three iron authors correctly collapse an eight-row table, distinguish crude from adjusted OR, and flag source unit/interval ambiguities. They then choose different supplementary literature and assumptions. The final programs implement these decisions. The [source/model audit](SOURCE_MODEL_AUDIT.md) links the literal sources, transformations and remaining assumptions.

One same-target-family search preview reached PNS_A2, containing study identity/demographics and a qualitative topic but not the requested target estimates. It was explicitly excluded by the author; exposure remains recorded. Other historical-survey previews are also retained. No target dataset or aggregate answer file was sent to the API. This experiment therefore tests controlled original-paper modeling capability with imperfect source screening, not pristine unseen-population performance.

## Validation and cost

'''+f'''- All18 final isolated executions succeeded; zero missing analysis slots.
- All99 endpoint values agree with the separately implemented QR/count/rank computation; maximum absolute difference7.55e-14. This verifies numerical implementation, not biological truth.
- {qa['old_files_unchanged']} prior protected files are unchanged; all frozen current inputs and candidate bindings verify.
- Model requested/returned:`gpt-6.1-sol`;142 calls; estimated token-tariff costUSD{cost['known_tariff_cost_usd']:.7f}; zero unknown-usage calls. This is recorded tariff accounting, not an invoice. The precommitted maximum wasUSD24.
- All model prompts, responses, tool calls, code/spec/notes, hashes and execution receipts remain local. Final individual virtual rows and full third-party texts are not public-report contents.

'''+trace_table+'''
## KDD contribution and next decision

This experiment supports the **Agent's actual evidence interpretation and model authorship**, in addition to the earlier fixed-packet composition controls and P0 same-analysis utility context. The useful claim is an evidence-to-analyzable-data capability with analysis-specific successes and traceable assumptions. It does not establish workflow superiority, revision benefit, all-analysis utility, human-level extraction accuracy, or reliable new-population transport.

The next bounded item remains P2: inspect a faithful LLMSynthor comparison in a compatible information/output setting and run it only after the adaptation and analysis are specified. Do not keep tuning these six generators against the now-known reference. A cross-model extension is conditional on what P2 can resolve, rather than expanding models/data by default. The unchanged v0.33 manuscript has a [prepared insertion](MANUSCRIPT_INSERT.md); no new reading edition is silently substituted.

Artifacts: [offline visual report](report/index.html), [protocol](PROTOCOL.md), [source/model audit](SOURCE_MODEL_AUDIT.md), `analysis/author_results.csv`, `analysis/seed_results.csv`, `analysis/COSTS.json`, `audit/TRACE_SUMMARY.json`.
'''
markdown(ROOT/'RESULTS.md',results)

markdown(ROOT/'MANUSCRIPT_INSERT.md','''# Proposed P1 manuscript insertion — not yet merged into v0.33

## Original-paper interpretation and scientific model authorship

We tested whether the Agent could construct a joint generator directly from a research request and an original-paper entry point, without a coordinator-written numerical evidence packet. Three fresh GPT sessions were run for each of two existing biomedical cases. Agents could inspect the complete original paper, search additional literature, author code and parameters, inspect a generated-only trial, and revise once. All six retained their first candidate. Models and complete histories were sealed before three prespecified final draws and reference evaluation. The coordinator did not populate scientific relationships or revise the selected programs.

The Agents performed substantive evidence interpretation. In the blood-pressure case, all three extracted a published correlation matrix and derived an age/BMI partial covariance, while explicitly identifying missing sex adjustment and population-transfer assumptions. In the iron case, all three collapsed eight published folate/B12/ferritin categories into a two-by-two anemia–iron-depletion table and distinguished the resulting crude odds ratio from a separately reported adjusted odds ratio. They also recognized inconsistent ferritin unit and interval labels. Additional searches informed marginal assumptions. The selected models included positive-pressure constructions for blood pressure and, for iron status, a Clayton copula, a latent-store mixture with a hinge response, or a saturating response with inflammatory and other-anemia components. These are Agent-authored choices, not coordinator-provided model templates.

All18 final tables executed successfully. Using the same prespecified scientific analyses, construction-average BMI–SBP coefficients were3.40–3.80mmHg per5kg/m², compared with3.52 in the measured sample; corresponding DBP coefficients were2.29–2.40 versus2.26. However, BP residual dependence was0.772–0.781 versus0.717, and both BP dispersions were higher. Iron odds ratios were6.35–7.14 versus17.79, with joint-low prevalence4.67–5.85% versus7.63% and rank correlation0.197–0.329 versus0.398. Thus, original-paper modeling can preserve useful scientific associations without recovering all aspects of the target joint distribution. The three draws within a construction measure simulation variation, not independent modeling evidence.

These are developmental, previously exposed reference families. The test supplies the anchor-paper identity; it does not evaluate unaided discovery. One constructor received a same-target-family search preview with demographics and qualitative subject matter, then explicitly excluded it; requested reference estimates were not present in that preview. Local target measurements/results were never supplied to the constructors. This exposure and all unsuccessful aspects are retained. The experiment does not estimate a revision effect or a causal advantage over the earlier fixed-packet arms. It adds direct evidence of interpretation, composition and model authorship to the controlled evidence-content and same-analysis utility studies.

## Figures and placement

Use `figures/primary_analyses.pdf` for the six prespecified analyses and `figures/diagnostics.pdf` for the full five companion diagnostics. Each point is one construction's three-seed mean; segments are the observed seed range, not confidence intervals. The dashed line is the previously exposed measured-sample reference. Place this capability section after the workflow and before the evidence-content controls, or as a focused subsection of the main experimental results. Retain all three authors and all analyses.

The paper's supported arc remains: a scientific request defines the desired data and analyses; the Agent interprets and combines evidence into an executable joint law; the resulting data support some useful analyses, with remaining unsupported relationships traced to explicit assumptions. P1 closes the curator-written-packet capability gap. It does not replace the remaining compatible published-method comparison.
''')

files=[ROOT/'RESULTS.md',ROOT/'SOURCE_MODEL_AUDIT.md',ROOT/'MANUSCRIPT_INSERT.md']+list((ROOT/'audit').glob('*.json'))
write(ROOT/'REPORT_BINDINGS.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
   'frozen_protocol_sha256':sha(ROOT/'PROTOCOL.md'),'construction_closure_sha256':sha(ROOT/'CONSTRUCTION_CLOSURE.json'),
   'all_science_retained':True,'reviewer':'root plus separately implemented numerical recomputation',
   'files':{p.relative_to(ROOT).as_posix():sha(p) for p in files}})
print(json.dumps({'source_code_audits':len(list((ROOT/'audit').glob('P1_*.json'))),'sessions':len(traces),'report_rows':len(rows)}))

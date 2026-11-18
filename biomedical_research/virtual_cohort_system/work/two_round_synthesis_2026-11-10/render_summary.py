from pathlib import Path
import json,html
U=Path(__file__).resolve().parent
NAMES={'OA_SOL':'GPT Sol','OA_ASTRA':'GPT Astra','DS_PRO':'DeepSeek','CL_FABLE':'Claude Fable','GE_CARBON':'Gemini Carbon'}
def fmt(x,d=3):return 'unavailable' if x is None else f'{x:.{d}f}' if isinstance(x,(float,int)) else str(x)
def main():
 v=json.loads((U/'SYNTHESIS.json').read_text());c=v['counts'];ss=v['analysis_summaries'];alignment=json.loads((U/'ROUND_ALIGNMENT_AUDIT.json').read_text())
 tables=[]
 for case,ids,title in [('PNS',['bmi_sbp','bmi_dbp','residual_correlation'],'Blood pressure'),('lipids',['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL'],'Lipids')]:
  rows=[a for a in v['attempts'] if a['kind']=='initial' and a['case_id']==case and a['complete_analysis_tables']==3];tables += [f'### {title}','', '| Construction | Model | BMI–first outcome | BMI–second outcome | Residual correlation |','|---|---|---:|---:|---:|']
  for a in rows:
   values=[next(r['seed_mean'] for r in ss if r['round']==a['round'] and r['version_id']==a['version_id'] and r['analysis_id']==eid) for eid in ids]
   tables.append('| '+a['round']+' / '+a['version_id']+' | '+NAMES[a['model_config']]+' | '+' | '.join(fmt(x) for x in values)+' |')
  refs=[next(r['reference_value'] for r in ss if r['case_id']==case and r['analysis_id']==eid) for eid in ids]
  tables.append('| Existing sample reference | — | '+' | '.join(fmt(x) for x in refs)+' |');tables.append('')
 failed=[a for a in v['attempts'] if a['kind']=='initial' and a['complete_analysis_tables']==0]
 failures=['| Attempt | API / execution result |','|---|---|']+['| '+a['round']+' / '+a['version_id']+' | '+a['api_status']+'; '+a['law_delivery']+' |' for a in failed]
 md='''# Two-round synthesis: parameter provenance and scientific analyses

The combined result is not that all Agents copy the same numbers. They consistently turn fixed source packets into executable joint models, but must complete different unreported parts of those models. Most checked mathematical constructions implement their stated assumptions coherently. Agreement with real analyses then varies by the particular estimand and by the source, conditioning and population bridges used.

## Scope and counting

This synthesis uses only the two completed API pilots dated 2026-11-10. Both are **whole-cohort generation with no target individual covariates supplied**: blood pressure in the PNS context and lipids in the Turkana study context. It is not a summary of every earlier biomedical experiment or proof of missing-cell/column recovery. The evidence packets, initial task instructions, reference snapshot and shared statistical engines match across these rounds. Sources and measurements were not newly reauthenticated; this audit checks the existing admitted packets and captured artifacts.

- 32 API requests: 28 initial construction attempts and four dependent reviews of two fixed Sol parents.
- 21 complete initial API artifacts; 20 initial generators delivered analyzable tables. One complete DeepSeek artifact failed at execution.
- Four reviews: three exact code/specification no-ops and one changed age-distribution program. These do not create four new independent authors.
- 96 scheduled evaluation table slots: 72 successful files, three execution failures and 21 unavailable-candidate slots. These contain 63 distinct file hashes. Six additional diagnostic tables were used in round two.
- Seeds describe sampling from a fixed model. Unique files, unique program/specification pairs and mathematically distinct probability laws are different quantities; none is a count of independent clinical studies.
- Total known usage-derived tariff estimate across both pilots: $14.14412666, with $0.21840852 still reserved for unknown usage. No new API calls, generation or real-patient analysis were performed for this synthesis.

## What comes from sources, and what the Agent adds

| Requested analysis | Admitted source information | Additional construction needed | What the combined results show |
|---|---|---|---|
| BMI–SBP/DBP regression | INTERSALT 0.7754 / 0.5967 mmHg per kg/m², with additional sodium/potassium/alcohol adjustment and centre-level pooling | Fivefold unit conversion is algebraic; equality after changing adjustment, age range, measurement and population is assumed | Most laws adopt 3.877 / 2.9835 per five BMI units. R2 Astra instead adds an explicit assumed omitted-adjustment contribution, producing 4.677 / 3.5835 as model-law slopes. Generated estimates follow the completed law with sampling variation, not a guaranteed target effect |
| SBP–DBP residual correlation | No compatible conditional residual correlation. Beijing marginal SBP, DBP and pulse-pressure SDs permit a raw covariance calculation | Conditional covariance requires a mean/covariate model; direct rho values, error-factor structures and covariance subtraction encode additional assumptions | All nine delivered PNS initial constructions have mean residual correlation below the existing sample reference; their internal choices are materially different |
| BMI–TC/HDL adjusted regression | Obirikorang rural unadjusted Spearman anchors 0.212 and −0.100; other sources provide margins or differently defined regressions | Rank-to-latent-copula mapping, raw margin transformations, sex/age conditioning and population transport; these do not directly identify requested raw adjusted slopes | Some laws leave scalar estimands unknown and provide a projection recipe; others choose additive effects. A source rank must never be displayed as the target regression coefficient |
| TC–HDL residual correlation | Rural source TC–HDL Spearman 0.106, plus marginal moments; no matched target adjusted residual Pearson correlation | Residual dependence emerges from the complete joint model. Conditional versus pooled copulas and component decompositions matter | All eleven delivered lipid initial constructions lie below the existing sample reference. Claude C2's zero HDL–non-HDL error correlation induces TC–HDL residual correlation about 0.381; zero is not its requested endpoint |
| Dispersion / age tails | Some sources report marginal means/SDs; these are not conditional residual SDs, coefficient SEs, or transport uncertainty | Variance subtraction, distributional shape, target composition, and support limits | Dispersion is not universally too small. R2 Sol_B SBP SD exceeds its sample reference. Feedback repaired one extreme age tail using an explicitly assumed cap of 100, not newly acquired evidence |

Each parameter is therefore labelled with **multiple provenance components when appropriate**: reported anchor, algebra under a model, and unverified assumptions. These are not mutually exclusive classes or calibrated confidence scores. A numerically derived value can still depend strongly on an assumed population or conditioning bridge.

## The reproducible pattern and its limits

Across the 20 data-delivering initial constructions, all mean residual correlations fall below their case's existing sample reference:

- PNS: nine initial constructions, approximately **0.375–0.608**, versus **0.717** in the sample reference.
- Lipids: eleven initial constructions, approximately **0.097–0.382**, versus **0.512**.

This supports a repeated descriptive pattern within two fixed tasks and shared evidence packets. It is not twenty independent datasets, a universal LLM bias, or proof that all gaps are caused by conditional independence. Structural alternatives, source transfer, demographic assumptions and reference uncertainty remain possible contributors. Gemini produced no usable initial artifact and cannot be assigned a scientific dependence result.

![Residual dependence](figures/residual_dependence.png)

## Separate the declared model from its generated sample

For statically validated final-law functionals, the ledger explicitly separates:

`generated estimate − sample reference = (generated estimate − completed-law value) + (completed-law value − sample reference)`.

This is an arithmetic decomposition, not causal attribution. The first term includes finite-sample fluctuation; the second combines scientific scenario choices, transport and sample-reference differences. A model coefficient is not automatically the requested estimand after selection, truncation, nonlinear transformation or omitted conditioning. Unknown model-law values are left missing, not inferred backwards from generated or target results.

PNS provides the cleanest examples. Its additive laws often imply the source-scaled slopes exactly, yet target applicability is unverified. R1 Astra C2 illustrates why innovation and regression-residual correlations differ when a nonlinear age component remains in linear residuals. R2 Astra illustrates an explicitly assumed adjustment bridge changing the requested coefficient.

![Source, law and analysis](figures/source_model_analysis.png)

## All delivered initial analysis results

Each number is a mean across the three prespecified seeds of one construction, not an independent-study estimate or confidence interval. PNS outcomes are SBP then DBP, with slopes in mmHg per 5 kg/m². Lipid outcomes are TC then HDL, with slopes in mg/dL per 5 kg/m². Complete seed ranges, reference uncertainty and failures are in the machine-readable ledger.

'''+ '\n'.join(tables)+'''
## Failures and corrections retained

'''+ '\n'.join(failures)+'''

Three distinct issues must remain separate:

1. **Implementation failure:** R2 PNS_DS indexes a DataFrame with column descriptor dictionaries and raises `TypeError: unhashable type: 'dict'`. Its abstract law can be coherent while no table is delivered.
2. **Unsupported mathematical claim:** R1 LIPID_DS_PRO_C2 positivity-rejects proposal errors. Its pre-rejection coefficients and covariance do not establish the claimed exact final-law slopes or residual correlation. The observed numerical discrepancy alone does not determine how much the rejection changes the estimands.
3. **Unverified scientific bridge:** most other audited core formulas are internally coherent, but marginal/rank evidence does not uniquely identify target conditional relationships. Internal arithmetic correctness does not settle transportability.

**Audit erratum:** the earlier review incorrectly criticized R1 LIPID_OA_ASTRA_C1 for using Greiner `.rows` paths. The frozen packet actually uses `format`, `columns`, and `rows`, not `records`. All sixteen pointer occurrences resolve, and all twelve named statistic IDs match. That criticism is withdrawn in the alignment audit. Original frozen files and numerical results remain unchanged; the correction must not be counted as an Agent error.

## What the review branches add

Only the R2 lipid feedback branch changed its data-generating program. Its age support changed to a beta distribution on [18,100]. At matched evaluation seeds, all non-age fields remained exactly identical. Maximum ages changed from about 198, 226 and 300 to 96, 98 and 99; HDL > TC remained 34/9,000 rows and scientific lipid estimates barely changed. The age cap is an explicit additional assumption. This is a local secondary repair, not improvement on the prespecified component-consistency endpoint or new evidence for joint relationships. Three no-op branches preserve their parents and remain visible in the full ledger. There are only two paired parents. Concurrent requests dispatched feedback before ordinary review in both cases, so the intended branch-order counterbalancing was not achieved; this deviation does not change the frozen prompts or parent assignments.

## How to read scientific usefulness

A source-aligned relation, a coherent model law, a successful implementation, and agreement with a target sample answer different questions. This synthesis does not merge them into a single pass score. PNS reference intervals describe conditional IID row-resampling stability, not national design-based confidence. Lipid coefficient intervals use conditional HC3 sensitivity assumptions; the TC interval is broad and includes zero. The lipid residual interval is unavailable. Seed ranges are not confidence or transport-uncertainty intervals, and no post-hoc equivalence margin is used.

The most defensible next focus is **analysis-specific evidence sufficiency and the Agent's completion of unreported joint structure**. The records now show where a useful relation is anchored, where algebra is valid only under a completed model, and where a free assumption materially changes the analysis. The current provenance labels describe these dependencies; their ability to predict new-target error has not been prospectively validated. No additional experimental arm or model call is started by this synthesis.

## Files

- [Interactive index](index.html): choose a construction, inspect all analyses, and read its core parameter provenance.
- [Attempt ledger](ATTEMPTS.csv): all 32 calls, status, lineage and costs.
- [Analysis results](ANALYSIS_RESULTS.csv): all 192 endpoint summaries, including diagnostics and failures.
- [Parameter sources](PARAMETER_SOURCES.csv): source anchors, transformations, assumptions, operators and code/specification locators.
- [Seed results](SEED_RESULTS.csv): all 576 scheduled endpoint-by-seed rows.
- [Validated-law decomposition](LAW_REFERENCE_DECOMPOSITION.csv): only rows with a statically supported numerical law functional.
- [PNS parameter audit](PNS_PARAMETER_MAP.md), [lipid parameter audit](LIPID_PARAMETER_MAP.md), [round alignment and erratum](ROUND_ALIGNMENT_AUDIT.md).
- [Complete structured synthesis](SYNTHESIS.json).

All material is an audit of previously completed experiments. Raw patient data, raw API transcripts and synthetic row-level tables are not copied into this synthesis package.
'''
 (U/'RESULTS_SUMMARY.md').write_text(md,encoding='utf-8')
 data=json.dumps(v,ensure_ascii=False,allow_nan=False).replace('</','<\\/')
 page=r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Two rounds · Evidence, models, analyses</title><style>
:root{--ink:#202d43;--blue:#315b96;--muted:#657084;--line:#dfe4ed;--pale:#f3f5fa}*{box-sizing:border-box}body{margin:0;background:#f7f8fb;color:var(--ink);font:15px/1.6 system-ui,Segoe UI,sans-serif}main{max-width:1260px;margin:40px auto;padding:0 26px}h1{font-size:36px;line-height:1.2;max-width:900px}h2{font-size:23px;margin:0 0 15px}p{max-width:1000px}a{color:var(--blue)}header small{letter-spacing:2px;text-transform:uppercase;color:var(--blue)}section{background:white;border:1px solid var(--line);border-radius:12px;padding:26px;margin:22px 0}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.card{background:white;border:1px solid var(--line);border-radius:10px;padding:18px}.card b{display:block;font-size:27px}.card span,.muted{color:var(--muted)}.note{background:var(--pale);border-left:3px solid #8463a5;padding:12px 16px}.fig{width:100%;height:auto}select,input{padding:10px;border:1px solid #bdc7d6;border-radius:6px;background:white;color:var(--ink);max-width:100%}.filters{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}.table{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}th{background:#f0f3f8;white-space:nowrap}td.num{white-space:nowrap;font-variant-numeric:tabular-nums}details{border:1px solid var(--line);border-radius:8px;margin:12px 0;padding:14px}summary{cursor:pointer;font-weight:650}.tag{display:inline-block;padding:2px 8px;background:#edf1f8;color:#3c5279;border-radius:4px;font-size:12px;margin-right:4px}dl{display:grid;grid-template-columns:180px 1fr;gap:8px 14px}dt{font-weight:600}dd{margin:0;overflow-wrap:anywhere}.pre{white-space:pre-wrap;font-family:ui-monospace,Consolas,monospace;font-size:12px;max-height:250px;overflow:auto}.links{display:flex;gap:18px;flex-wrap:wrap}footer{color:var(--muted);font-size:12px;margin:30px 0}@media(max-width:700px){main{padding:0 12px}h1{font-size:28px}.cards{grid-template-columns:1fr 1fr}section{padding:16px}dl{grid-template-columns:1fr}dt{margin-top:10px}}
</style><main><header><small>Completed experiments · retrospective synthesis</small><h1>What is sourced, what is assumed,<br>and which analyses follow?</h1><p>Two fixed biomedical tasks. The Agent turns published summaries into a complete joint model. This index separates source anchors, mathematical implications, delivered data and comparison with existing sample references.</p></header><div class="cards"><div class="card"><b>28</b><span>initial construction attempts</span></div><div class="card"><b>20</b><span>initial generators delivered data</span></div><div class="card"><b>2</b><span>fixed biomedical cases</span></div><div class="card"><b>4</b><span>dependent review branches</span></div></div><section><h2>The combined finding</h2><p>Every delivered initial construction has lower residual correlation than its case's existing sample reference: PNS <b>0.375–0.608 vs 0.717</b>; lipids <b>0.097–0.382 vs 0.512</b>. The mechanisms differ: assumed errors, covariance subtraction, copula bridges and component decompositions.</p><p class="note">This is a repeated pattern within two shared evidence packets, not 20 independent clinical replications or a universal model ranking. Parameters can simultaneously be source-reported, algebra-derived and assumption-dependent.</p><img class="fig" src="figures/residual_dependence.png" alt="Residual correlations across both rounds"></section><section><h2>Inspect a construction</h2><p class="muted">All calls remain available, including incomplete responses, execution failures and unchanged review branches.</p><div class="filters"><label>Case <select id="case"><option value="">Both cases</option><option>PNS</option><option>lipids</option></select></label><label>Round <select id="round"><option value="">Both rounds</option><option>R1</option><option>R2</option></select></label><label>Construction <select id="pick"></select></label></div><div id="selected"></div></section><section><h2>Source → completed model → generated analysis</h2><p>For statically validated laws, the source-scaled coefficient and the completed-model coefficient are shown separately. Missing numerical law values remain unavailable; sample estimates are never used to manufacture a claimed exact law.</p><img class="fig" src="figures/source_model_analysis.png" alt="Source model and generated coefficient comparison"><p class="note">R2 Astra explicitly adds an assumed adjustment bridge. The different model coefficient is mathematically coherent, but its target applicability is unverified.</p></section><section><h2>Failures, changes and one audit correction</h2><ul><li>R2 DeepSeek PNS: output-column indexing error; coherent abstract law, no delivered table.</li><li>R1 DeepSeek lipid C2: positivity rejection invalidates its claim that proposal coefficients are exact final-law estimands.</li><li>R2 feedback: one age-tail revision; unchanged HDL ordering and nearly unchanged lipid analyses. Three reviews retained the original code/specification. Only two paired parents were tested; both cases dispatched feedback first, so planned order counterbalancing was not achieved.</li><li>The old criticism of Astra C1's Greiner <code>.rows</code> locators was an audit mistake. All 16 pointers resolve in the frozen packet. The correction is retained separately.</li></ul></section><section><h2>Full results and audit files</h2><div class="links"><a href="RESULTS_SUMMARY.md">Read the full synthesis</a><a href="ATTEMPTS.csv">All calls</a><a href="PARAMETER_SOURCES.csv">Parameter sources</a><a href="ANALYSIS_RESULTS.csv">All analysis results</a><a href="SEED_RESULTS.csv">Seed-level results</a><a href="LAW_REFERENCE_DECOMPOSITION.csv">Law/reference decomposition</a><a href="ROUND_ALIGNMENT_AUDIT.md">Alignment and erratum</a></div><p class="muted">72 successful evaluation files contain 63 different hashes. Repeated seeds and retained branches do not add independent studies. Existing references are uncertain samples; no equivalence threshold or global quality-pass score is imposed.</p></section><footer>No new API calls, generation or patient-data analysis were run for this summary. Source packets and historical results were audited retrospectively. Core parameter coverage is not an exhaustive audit of every demographic setting.</footer></main><script id="data" type="application/json">__DATA__</script><script>
const d=JSON.parse(document.getElementById('data').textContent);const byId=x=>document.getElementById(x);let visible=[];
function text(tag,t,cls){let e=document.createElement(tag);e.textContent=t??'unavailable';if(cls)e.className=cls;return e}function show(x){return x==null?'unavailable':typeof x==='number'?Number(x.toPrecision(6)).toString():typeof x==='object'?JSON.stringify(x,null,2):String(x)}
function addPair(dl,k,val){dl.append(text('dt',k),text('dd',show(val),typeof val==='object'?'pre':''))}
function refresh(){const old=byId('pick').value;visible=d.attempts.filter(a=>(!byId('case').value||a.case_id===byId('case').value)&&(!byId('round').value||a.round===byId('round').value));byId('pick').replaceChildren(...visible.map(a=>{let e=document.createElement('option');e.value=a.round+'|'+a.version_id;e.textContent=a.round+' · '+a.version_id+' · '+a.law_delivery;return e}));if(visible.some(a=>a.round+'|'+a.version_id===old))byId('pick').value=old;render()}
function render(){const a=visible.find(x=>x.round+'|'+x.version_id===byId('pick').value);const root=byId('selected');root.replaceChildren();if(!a)return;root.append(text('h3',a.version_id));let intro=text('p',a.requested_model+' · '+a.kind+' · '+a.api_status+' · '+a.complete_analysis_tables+'/3 tables have complete analyses'+(a.review_disposition?' · '+a.review_disposition:''));root.append(intro);if(a.parent_version_id)root.append(text('p','Shared parent: '+a.parent_version_id+'. This review is not a new independent construction.','note'));
let w=text('div','', 'table'),t=document.createElement('table'),head=document.createElement('tr');['Analysis / unit','Generated mean [seed range]','Validated model-law value','Existing sample reference','Law assessment'].forEach(x=>head.append(text('th',x)));t.append(head);d.analysis_summaries.filter(r=>r.round===a.round&&r.version_id===a.version_id).forEach(r=>{let tr=document.createElement('tr');[r.analysis_id+' / '+r.unit,r.seed_mean==null?'unavailable':show(r.seed_mean)+' ['+show(r.seed_min)+', '+show(r.seed_max)+']',show(r.validated_population_value),show(r.reference_value),r.claim_validation_status].forEach((x,i)=>tr.append(text('td',x,i>0&&i<4?'num':'')));t.append(tr)});w.append(t);root.append(w);root.append(text('p','Generated ranges reflect three seeds, not clinical confidence or transport uncertainty. An unavailable law value is not evidence of an invalid law.','muted'));
const m=a.provenance_record;if(!m.parameters.length)root.append(text('p','No complete scientific artifact: no parameter choices are imputed from a truncated or missing response.','note'));m.parameters.forEach(p=>{let box=document.createElement('details'),s=text('summary',p.name);box.append(s);let tags=document.createElement('p');p.provenance_components.forEach(c=>tags.append(text('span',c,'tag')));box.append(tags);let dl=document.createElement('dl');[['Implemented input',p.value],['Operator / unit',p.unit],['Source IDs',p.source_ids],['Reported source anchor',p.source_reported_value],['Source population / statistic',p.source_operator],['Transformation',p.transformation],['Unverified bridges',p.transport_assumptions],['Final-law interpretation',p.mathematical_note],['Analyses affected',p.analysis_ids],['Code / evidence locators',p.locators]].forEach(([k,val])=>addPair(dl,k,val));box.append(dl);root.append(box)});if(m.review_change)root.append(text('p','Review change: '+show(m.review_change),'note'));let lim=document.createElement('details');lim.append(text('summary','Scope and remaining assumptions'));let ul=document.createElement('ul');(m.limitations||[]).forEach(x=>ul.append(text('li',x)));lim.append(ul);root.append(lim)}
byId('case').onchange=refresh;byId('round').onchange=refresh;byId('pick').onchange=render;refresh();
</script></html>'''
 (U/'index.html').write_text(page.replace('__DATA__',data),encoding='utf-8')
 print(json.dumps({'report':'RESULTS_SUMMARY.md','interactive_index':'index.html','working_initials':c['working_initial_laws']}))
if __name__=='__main__':main()

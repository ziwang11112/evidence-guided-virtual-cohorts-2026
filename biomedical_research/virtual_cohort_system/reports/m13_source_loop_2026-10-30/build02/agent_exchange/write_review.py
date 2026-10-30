"""Write a review of actual permitted source feedback; no generator execution."""
from pathlib import Path
import json

B=Path(__file__).resolve().parent.parent
E=B/'agent_exchange'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
m=read(E/'review_metrics.json')
recipe=read(B/'candidates/initial/source_replay_v2.json')
evidence_ids=[check['evidence_id'] for context in recipe['contexts'] for check in context['checks']]
evidence_ids+=['G_SEE','T_full_bmi_ge25']
decision={
 'choice':'retain_structure',
 'rationale':'Retain selected trial 8 as a provisional development candidate and do not use the remaining session for an unsupported structural expansion. The fixed engineering fit loss fell from0.6950506982 to0.6237954002 (10.25%), with9 of18 constraints improved and9 worsened by mean absolute per-draw error. This is a compromise: Thai context mean scaled squared error worsened0.62139 to0.70277 while Gallagher improved0.78713 to0.52508. Independent replay loss0.70643 confirms persistent discrepancies, not target benefit. The admitted summaries do not identify a study/device correction, different Thai/Japanese effects at identical allowed covariates, conditional tail law or age/BMI dependence; another flexible structure would add assumptions to chase this same reconstructed population. Preserve the selected numerical parameters and their adverse trade-offs for a frozen downstream evaluation, not as a validated biomedical model.',
 'evidence_ids':evidence_ids,
 'addressed_constraints':[x['constraint'] for x in m['constraint_summaries']],
 'remaining_limits':[
  'Thai women remain too strongly related to BMI: replay Pearson0.90437-0.90623 versus0.77, SD9.63424-9.70092 versus8.4, and pooled BMI coefficient2.02521-2.02942 versus1.648. These persistent discrepancies are not explained away as Monte Carlo noise.',
  'Gallagher male inverse-BMI interaction remains43.9447-82.0497 versus154 and Asian inverse-BMI interaction55.0391-62.2290 versus95. Male-age interaction is0.04571-0.05062 versus0.034. Original regression design and all constraints remain intact.',
  'Sources overlap internally and differ in population, device, site and selection. Identity DXA transport and one Asian indicator for Thai and Japanese participants remain unverified; coefficient SE/covariance is unavailable.',
  'Source BMI shapes, threshold subgroup allocation, adult/lower-BMI support and the fixed latent age-BMI correlation0.15 are reconstruction assumptions. The corrected Thai prevalence is feasible, not identified. Nonlinear mean projections depend on these choices.',
  'Beta conditional residual law, endpoint mean regularization and sex-specific desired SDs are assumptions. Fitted SDs can absorb mean misspecification and source covariate approximation; they do not estimate demonstrated sex-specific biological residual variation.',
  'Nine trials exhausted the session before convergence was established. target_loss0 is exact-agreement stopping, not a clinical equivalence threshold. Two fresh seeds use the same source rows and assess simulation repeatability only.',
  'Counts use mean(abs(draw-reference)), not abs(mean(draw)-reference); both happen to give9 improvements here, but individual values differ under sign cancellation. No matched baseline evaluation exists on replay seeds23101/23102 in this session.',
  'For the non-Asian qualification/primary domain, the bridge weights are zeroed by asian=0, so the conditional mean function is unchanged. Numerical fitting changes sex-specific conditional dispersion. No target outcome or clinical-use advantage has been assessed.',
  'A future prespecified, independently reserved target evaluation can estimate task-specific transport error against real measurements and analyses. It cannot establish universal validity, recover individual truth, infer causal effects, or confer measurement savings solely from source fit.'
 ]}
assert set(decision)=={'choice','rationale','evidence_ids','addressed_constraints','remaining_limits'}
known={x['id'] for x in read(B/'candidates/initial/evidence.json')['items']}
assert set(evidence_ids)<=known and len(decision['addressed_constraints'])==18
(E/'review_decision.json').write_text(json.dumps(decision,indent=2)+'\n',encoding='utf-8')

intro='''# Source-only review: retain structure

Retain selected trial **t0008** as a provisional development candidate, with its limitations and adverse trade-offs. Do not spend the remaining scientific session on a structural expansion unsupported by these two sources. No frozen file was edited and no generator was imported or executed during this review.

The controller completed 9 feasible numerical trials and 40 isolated executions. Selection used fit seeds 13101/13102 before replay seeds 23101/23102. I read the locked plan, result, selection, selected generator/specification and all four selected-trial source replay reports. Their report hashes match the recorded result bindings; all 18 checks in each report are computed and generation-linked. This review uses supplied verified feedback, rather than independently rerunning the entire verifier.

Selected parameters are `bridge_male` 0.50→0.75, `bridge_female` 0.50→0.25, `residual_sd_male` 4.31→4.81 pp, and `residual_sd_female` 4.31→3.81 pp. Published equation coefficients, conditional family, source rows, covariate assumptions and measurement mapping remain unchanged. Fit loss decreased **0.695051→0.623795 (10.25%)**. The stop was `max_trials`; `fit_threshold_not_met` means the exact zero target was not reached, not failed clinical equivalence. The selected replay loss is **0.706431**. There is no baseline result at the replay seeds, so comparing this number with the initial fit loss would confound parameter changes with seeds.

All 18 source constraints are shown below. Mean values summarize the two fit seeds; replay gives the two fresh values as a range. The final column compares **mean(abs(draw − reported))**, in the statistic's units, on common fit seeds. It is not abs(mean(draw) − reported). Body-fat mean/SD and intercept are in percent or percentage points; BMI, age, sex and inverse-BMI coefficients retain the exact units and adjustment sets in evidence.json and the original source estimator. T denotes Thai DEVELOPMENT and G the full Gallagher composition.

| Constraint | Reported | Initial fit mean | Selected fit mean | Selected replay range | Fit mean absolute error, initial→selected |
|---|---:|---:|---:|---:|---:|
'''
rows=[]
for x in m['constraint_summaries']:
    label=x['constraint'].replace('thai_development/','T: ').replace('gallagher_full/','G: ')
    a=x['initial_fit'];s=x['selected_fit'];v=x['selected_replay']['values']
    arrow='improved' if x['fit_mae_improved'] else 'worsened'
    rows.append(f"| {label} | {x['reported']:.6g} | {a['mean_value']:.6g} | {s['mean_value']:.6g} | {min(v):.6g}–{max(v):.6g} | {a['mean_absolute_draw_error']:.6g}→{s['mean_absolute_draw_error']:.6g} ({arrow}) |")
conclusion='''

There are **9 improved and 9 worsened constraints** by mean absolute draw error: only 3 of 10 Thai checks improve, versus 6 of 8 Gallagher checks. The Thai context's mean scaled squared error worsens **0.621390→0.702771**; Gallagher improves **0.787127→0.525076**. These are correlated diagnostics under fixed engineering scales, not independent evidence or a likelihood. The replay context scores are 0.754642 and 0.646167 respectively.

The clearest gains are the Thai male mean and male coefficient, plus Gallagher intercept, inverse-BMI, sex and age terms. The slight Thai male SD improvement accompanies a worse male BMI correlation. Thai female mean, SD and BMI correlation all worsen. The pooled Thai intercept, BMI slope and age slope also worsen. Gallagher Asian inverse-BMI and male-age interactions worsen; male inverse-BMI improves slightly but remains far below154 on both fresh draws. The lower fitted female residual SD does not establish smaller biological residual variation: it participates in a compromise with mean curvature and reconstructed BMI tails, while the resulting female SD and correlation remain too large.

Sign cancellation matters even though both improvement-count definitions happen to yield9 here. For Gallagher Asian-age, fit mean absolute draw error is **0.002752→0.002189**, whereas absolute error of the seed mean is **0.002147→0.001054**. Initial Gallagher male-age has mean absolute draw error **0.003923**, but seed-mean absolute error only **0.000911**; selected error is **0.013697** by either definition. On fresh replay the Gallagher age error is **0.001140** by mean absolute draw error versus **0.000555** by seed-mean absolute error. Per-seed values and both definitions are retained in review_metrics.json.

Persistent Thai female and Gallagher interaction discrepancies exceed the observed between-seed fluctuations and expose an inadequate simultaneous source fit under this construction. They may reflect source conflict, the shared Thai/Japanese indicator, cross-device transport, mean misspecification, or unreported source covariate distributions. Their causes cannot be uniquely separated here. The corrected Thai BMI threshold distribution is compatible with published margins, but its broad female lower tail, within-threshold shape, allocation and age/BMI copula remain assumptions; inverse-BMI projections depend on them. A source or device identifier would violate the allowed scientific input set, and additional flexible interactions would be assumptions rather than recovered evidence. Retention therefore preserves an inspectable, imperfect candidate; it does not endorse source adequacy or prove that no useful model exists.

For `asian=0`, both bridge adjustments vanish. Thus the selected non-Asian conditional mean function is exactly the initial one; the fitted sex-specific dispersion changes. A later frozen, prespecified evaluation against independently reserved real measurements can assess this candidate's errors and downstream analytical performance in that particular target domain. It cannot be replaced by these source checks, by the invented qualification grid, or by repeated simulation seeds. No current target benefit, individual recovery, causal validity, general uncertainty calibration or measurement savings is established. If later target results are used to choose another model, a new independent evaluation would be required for that changed model.

Decision and traceability: review_decision.json contains exactly the requested five fields and references all18 existing context/check identifiers and existing evidence IDs. review_metrics.py records the permitted-report arithmetic; review_metrics.json retains all seed values, both error definitions, context scores and source report hashes. Source evidence anchors remain Thai Table1, Table2 and Results/Table4; Gallagher p696 DXA Equation1; and the full-cohort Thai BMI-threshold paragraph following Table1. No additional evidence retrieval occurred.
'''
(E/'review_response.md').write_text(intro+'\n'.join(rows)+conclusion,encoding='utf-8')
print(json.dumps({'choice':decision['choice'],'addressed_constraints':len(decision['addressed_constraints']),
                  'evidence_references_valid':True,'outputs':['review_decision.json','review_response.md']},indent=2))

"""Summarize already independently recomputed outcomes; no new experiment."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    review=read(R/'review/INDEPENDENT_NUMERICAL_REVIEW.json');assert review['status']=='pass'
    final=read(R/'FINAL_TABLES.json')
    old=read(R.parent/'request_only_repeatability_2026-11-11/FINAL_TABLES.json')
    mapping={x['pair_id']:x['old_episode_id'] for x in read(R/'_host_only/IMPORT_MAPPING.json')['pairs']}
    original={(s['episode_id'],s['seed']):s for s in old['slots']}
    same=[];phys=[]
    for s in final['slots']:
        a=original[(mapping[s['episode_id'][:3]],s['seed'])]
        same.append({'episode_id':s['episode_id'],'seed':s['seed'],
            'equal_saved_table_sha256':s['generated_sha256']==a['generated_sha256'],
            'initial_sha256':a['generated_sha256'],'final_sha256':s['generated_sha256']})
        phys.append({'episode_id':s['episode_id'],'seed':s['seed'],
            'initial_count':a['statistics']['quality']['component_violation_count'],
            'final_count':s['statistics']['quality']['component_violation_count'],
            'meaning':'SBP<DBP' if s['case_id']=='PNS' else 'HDL>TC'})
    costs={arm:{'calls':sum(x['calls'] for x in review['costs'] if x['episode_id'].endswith(arm)),
       'known_tariff_usd':sum(x['known_tariff_usd'] for x in review['costs'] if x['episode_id'].endswith(arm))} for arm in ['GENERIC','STRUCTURED']}
    primary=[x for x in review['initial_comparisons'] if x['pair_id'] in ['R04','R07']]
    claims=[
      'Review Agents in both arms found and repaired an actual mathematical tail defect and a possible output-rounding failure, without new target feedback.',
      'The structured policy did not demonstrate an overall scientific-analysis advantage over generic review in this unit. Both arms selected two revised programs and ten retained programs.',
      'Only R04 changed the final numerical data. Both R07 revised programs reproduce the same three saved tables byte for byte, so their legitimate robustness repair is not an observed analysis-quality improvement.',
      'In R04, TC-BMI slope moves toward the historical sample reference under both revisions, more under structured review, but remains substantially larger. Residual correlation and lipid dispersion do not show a consistent improvement.',
      'The component-order repair in R04 structured is a support-level property of its idealized concentration model. Original R04 already had zero observed violations in these seeds; thus this is not an observed violation-count reduction.',
      'R08 retains one HDL>TC occurrence in seed54003 in both arms, as in the initial table. Across all blood-pressure tables SBP<DBP remains zero. These diagnostics are common fixed checks, not the variable number of Agent-declared rules.',
      'No new empirical residual-covariance constraint was established for the revised laws. Better mathematical validity and more explicit provenance do not resolve source-to-target transport or missing joint information.'
    ]
    out={'status':'complete','created_utc':datetime.now(timezone.utc).isoformat(),
      'source_code_audit_sha256':sha(R/'review/CODE_SOURCE_CHANGE_AUDIT.json'),
      'numerical_review_sha256':sha(R/'review/INDEPENDENT_NUMERICAL_REVIEW.json'),
      'evaluation_sha256':sha(R/'EVALUATION.json'),
      'all_saved_hash_comparisons':same,'equal_initial_final_table_count':sum(x['equal_saved_table_sha256'] for x in same),
      'total_final_tables':len(same),'common_physiological_checks':phys,'costs':costs,
      'total_calls':sum(x['calls'] for x in review['costs']),
      'total_known_tariff_usd':sum(x['known_tariff_usd'] for x in review['costs']),
      'unknown_usage_calls':sum(x['unknown_usage_calls'] for x in review['costs']),
      'changed_program_comparisons':primary,'interpretation':claims,
      'limits':['Two historically exposed clinical contexts; this is a developmental paired repair experiment.','The clinical references are sample estimates, not known population truths.','Three saved seeds per program are within-construction repeats, not independent Agent constructions.','Literal exposure search found zero new flags; it cannot certify absence of all source overlap or model prior knowledge.','One realized episode per arm per starting law; no universal ranking of review policies.'],
      'recommendation':'Retain the mathematical/physiological review as a documented reliability facility, with its unknown states and provenance limitations. Do not claim it repaired underidentified joint relations or improved final scientific utility generally. Do not regenerate on these revealed targets.'}
    with (R/'review/INDEPENDENT_INTERPRETATION.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,ensure_ascii=False)
    lines=['# Independent interpretation of the scientific-check revision experiment','',
      '**The checks found real defects; their repair did not produce a broad improvement in scientific analysis quality.**','',
      'The independent source/code audit was frozen before opening the numerical comparisons. Independent arithmetic then passed13,419 checks over72 final and36 initial saved tables, with maximum discrepancy9.33e-14. No model calls, generator runs or clinical reference fits were repeated.','',
      '| Comparison | Initial | Generic review | Structured review | Historical sample reference |','|---|---:|---:|---:|---:|']
    for metric in ['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL','total_cholesterol.sd_sample','hdl_cholesterol.sd_sample']:
        g=next(x for x in primary if x['episode_id']=='R04_GENERIC' and x['analysis_id']==metric)
        s=next(x for x in primary if x['episode_id']=='R04_STRUCTURED' and x['analysis_id']==metric)
        lines.append(f"| R04 {metric} | {g['initial_mean']:.4f} | {g['final_mean']:.4f} | {s['final_mean']:.4f} | {g['reference']:.4f} |")
    lines += ['', 'Lipid BMI slopes are mg/dL per5 kg/m²; lipid SDs are mg/dL. These are three-seed means, not independent participants or population ground truth.','',
      'Both R04 arms replace an infinite-moment ideal TC law with a finite-moment law. Structured review additionally models TC as positive HDL plus non-HDL. Its TC-BMI estimate is closer to the sample reference, but residual correlation remains about0.36 versus0.51 and both lipid SDs remain low. This supports a genuine validity repair, not a general joint-quality improvement.','',
      'Both R07 arms move rounding before pressure-pair acceptance. Every saved output is unchanged, proving that the rare failure branch was not encountered in these seeds. The structured version removes a retry cap, exchanging a capped failure for theoretically unbounded loop time.','',
      'Twenty episodes explicitly retained v000. Including R07,66 of72 final tables have exactly the initial table hash. R08 has one HDL>TC row in seed54003 in each arm, unchanged from the original. The two appearances are the same reused output, not independent failures.','',
      f"Generic review used{costs['GENERIC']['calls']} calls (${costs['GENERIC']['known_tariff_usd']:.6f}); structured review used{costs['STRUCTURED']['calls']} calls (${costs['STRUCTURED']['known_tariff_usd']:.6f}). Total343 calls cost $4.873132 in recorded tariffs, with zero unknown usage. This excludes historical construction cost and is not an invoice reconciliation.",'',
      'Keep the reliability checks and analysis-level provenance, but describe their scope honestly. The unit establishes that Agent-directed review can detect and repair particular code/law problems. It does not establish structured-review superiority or solve missing conditional dependence. No further target-driven edits or regeneration are warranted on this revealed unit.']
    with (R/'review/INDEPENDENT_INTERPRETATION.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    print(json.dumps({'same_initial_hash':out['equal_initial_final_table_count'],'total':len(same),
      'interpretation_sha256':sha(R/'review/INDEPENDENT_INTERPRETATION.json'),
      'numerical_review_sha256':out['numerical_review_sha256'],'costs':costs}))
if __name__=='__main__':main()

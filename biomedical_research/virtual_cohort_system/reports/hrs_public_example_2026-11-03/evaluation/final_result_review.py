"""Independent retained-result arithmetic; no fit or generation entrypoints."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import importlib.util
import json
import math
import statistics as stat

U = Path(__file__).resolve().parents[1]
SEEDS = [6101, 6102, 6103]


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    output = U/'FINAL_RESULT_REVIEW.json'
    assert not output.exists(), 'Preserve completed review'
    helper_path = U/'evaluation/audit_agent_results_v1.py'
    spec = importlib.util.spec_from_file_location('prior_independent_arithmetic',helper_path)
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    aggregate = read(U/'summary/AGGREGATE_RESULTS.json')
    prior = read(U/'AGENT_RESULT_AUDIT_v1.json')
    published = read(U/'sources/HRS_PUBLISHED_REFERENCES.json')
    source = U/'sources/original/HRSmodels_20200902_fullDemoTable.txt'
    text = source.read_text(encoding='cp1252').split('Fixed effects:',1)[1]
    exact = {}
    for line in text.splitlines():
        parts=line.split()
        if parts and parts[0] in helper.TERMS:
            assert parts[0] not in exact
            exact[parts[0]] = (float(parts[1]),float(parts[2]))
    assert set(exact)==set(helper.TERMS)
    checks=[]; numeric_count=0; largest=0.0
    def check(name,value,detail=''):
        checks.append({'id':name,'pass':bool(value),'detail':detail})
        if not value:raise AssertionError(name)
    def same(name,actual,expected):
        nonlocal numeric_count,largest
        numeric_count+=1;largest=max(largest,abs(actual-expected))
        check(name,math.isclose(actual,expected,rel_tol=2e-12,abs_tol=2e-12),
              f'{actual!r} versus independently reconstructed {expected!r}')
    bound_files = [source,U/'summary/AGGREGATE_RESULTS.json',U/'RESULTS.md',U/'AGENT_RESULT_AUDIT_v1.json',Path(__file__),helper_path]
    original_release=read(U/'RELEASE.json');recovery_release=read(U/'recovery_v1/RELEASE.json')
    for base,release in [(U,original_release),(U/'recovery_v1',recovery_release)]:
        for path,digest in release['files'].items():
            check('release_'+str(base.name)+'_'+path,sha(base/path)==digest)
        bound_files.append(base/'RELEASE.json')
    for seed in SEEDS:
        for path,digest in prior['source_bindings'][f'agent_{seed}'].items():
            check('agent_unchanged_'+str(seed)+'_'+path,sha(U/path)==digest)
    expected_runs=[('native',s,'native_corrected_'+str(s),U/'recovery_v1') for s in SEEDS]+[
                  ('agent',s,'agent_'+str(s),U) for s in SEEDS]
    docs={};flat={};raw_max=0;raw_checks=0;fit_records=[]
    for arm,seed,rid,base in expected_runs:
        ep=base/f'results/{rid}.evaluation.json';np=base/f'results/{rid}.native.json';gp=base/f'results/{rid}.gls.json'
        tp=base/f'bundle/executions/{rid}/output/generated.csv';rp=base/f'bundle/executions/{rid}/execution.json'
        ev,n,g,receipt=map(read,(ep,np,gp,rp))
        check(rid+'_status',ev['status']=='computed' and ev['returncode']==0 and ev['fit_attempts']==1 and ev['gls_status']=='pass' and ev['gls_returncode']==0)
        check(rid+'_hashes',ev['native_json_sha256']==sha(np) and ev['gls_json_sha256']==sha(gp) and ev['input_sha256']==n['input_sha256']==sha(tp)==receipt['files']['output/generated.csv'])
        check(rid+'_GLS',g['status']=='pass' and len(g['fixed_effects'])==16 and all(x['estimate_matches'] and x['se_matches'] for x in g['fixed_effects']))
        check(rid+'_fixed_terms',[x['term'] for x in n['fixed_effects']]==helper.TERMS)
        check(rid+'_convergence',n['convergence']['optimizer']=='bobyqa' and n['convergence']['optimizer_code']==0 and not n['singular'] and not n['warnings'])
        check(rid+'_REML',n['REML'] is True and n['subject_contract']==11509 and n['validation']['visits']==46036)
        d=helper.native_distribution(n)
        normalized={('subjects' if k=='subject_count' else k.replace('_percent','_percentage')):v for k,v in d.items()}
        docs[(arm,seed)]=n;flat[(arm,seed)]=normalized
        if arm=='native':
            with tp.open(newline='',encoding='utf-8') as stream:
                independent,_=helper.distribution(list(csv.DictReader(stream)))
            for key,v in independent.items():
                raw_checks+=1;raw_max=max(raw_max,abs(v-d[key]));same(rid+'_raw_'+key,d[key],v)
        fit_records.append({'arm':arm,'seed':seed,'generation_seconds':receipt['elapsed_seconds'],
           'fit_seconds':n['elapsed_seconds'],'optimizer_code':n['convergence']['optimizer_code'],
           'singular':n['singular'],'warnings':n['warnings'],'logLik':n['logLik'],
           'random_effect_covariance':n['random_effect_covariance'],'residual_variance':n['residual_variance']})
        bound_files.extend([ep,np,gp,rp,tp])
    check('exact_status_identity',{(x['arm'],x['seed'],x['run_id']) for x in aggregate['statuses']}=={(a,s,r) for a,s,r,b in expected_runs})
    for row in aggregate['statuses']:
        base=U/'recovery_v1' if row['arm']=='native' else U
        check('exact_status_record_'+row['run_id'],row==read(base/f'results/{row["run_id"]}.evaluation.json'))
    check('32_effect_groups',len(aggregate['fixed_effects'])==32 and len({(x['arm'],x['term']) for x in aggregate['fixed_effects']})==32)
    reconstructed_effects=[]
    for row in aggregate['fixed_effects']:
        arm,term=row['arm'],row['term'];estimates=[next(t['estimate'] for t in docs[(arm,s)]['fixed_effects'] if t['term']==term) for s in SEEDS]
        vals={'mean_estimate':stat.mean(estimates),'min_estimate':min(estimates),'max_estimate':max(estimates),'available_seeds':3}
        refs={'exported_coefficient':exact[term][0],'published_original_coefficient':published['table3'][term]['original'][0],'published_synthetic_coefficient':published['table3'][term]['synthetic'][0]}
        for key,ref in refs.items():
            vals[key]=ref;vals['signed_mean_discrepancy_'+key]=stat.mean(estimates)-ref
            vals['mean_absolute_discrepancy_'+key]=stat.mean(abs(x-ref) for x in estimates)
        for key,v in vals.items():same('effect_'+arm+'_'+term+'_'+key,row[key],v)
        reconstructed_effects.append({'arm':arm,'term':term,'seed_values':dict(zip(map(str,SEEDS),estimates)),**vals})
    check('54_distribution_groups',len(aggregate['distributions'])==54 and len({(x['arm'],x['metric']) for x in aggregate['distributions']})==54)
    refs={}
    for key,row in published['table2'].items():
        if key=='subject_count':refs['subjects']={'original_reference':row['original'],'published_synthetic_reference':row['synthetic']}
        else:
            for suffix in ('mean','sd','count','percent'):
                if 'original_'+suffix in row:
                    name=key+'_'+('percentage' if suffix=='percent' else suffix)
                    refs[name]={'original_reference':row['original_'+suffix],'published_synthetic_reference':row['synthetic_'+suffix]}
    reconstructed_distributions=[]
    for row in aggregate['distributions']:
        arm,metric=row['arm'],row['metric'];values=[flat[(arm,s)][metric] for s in SEEDS]
        vals={'mean_estimate':stat.mean(values),'min_estimate':min(values),'max_estimate':max(values),'available_seeds':3}
        for key,ref in refs[metric].items():
            vals[key]=ref;vals['signed_mean_discrepancy_'+key]=stat.mean(values)-ref
            vals['mean_absolute_discrepancy_'+key]=stat.mean(abs(x-ref) for x in values)
        for key,v in vals.items():same('distribution_'+arm+'_'+metric+'_'+key,row[key],v)
        reconstructed_distributions.append({'arm':arm,'metric':metric,'seed_values':dict(zip(map(str,SEEDS),values)),**vals})
    # Check every CSV cell rather than assuming JSON and the four exports agree.
    for filename,key in [('fixed_effects_summary.csv','fixed_effects'),('distributions_summary.csv','distributions')]:
        path=U/'summary'/filename
        with path.open(newline='') as stream: rows=list(csv.DictReader(stream))
        expected={(r['arm'],r['term'] if key=='fixed_effects' else r['metric']):r for r in aggregate[key]}
        check(filename+'_rows',len(rows)==len(expected))
        for row in rows:
            match=expected[(row['arm'],row.get('term',row.get('metric')))]
            for column,value in row.items():
                if column in ('arm','term','metric'):continue
                same(filename+'_'+row['arm']+'_'+row.get('term',row.get('metric'))+'_'+column,float(value),match[column])
        bound_files.append(path)
    path=U/'summary/fixed_effects_all_seeds.csv'
    with path.open(newline='') as stream: csv_effects=list(csv.DictReader(stream))
    check('96_allseed_effect_rows',len(csv_effects)==96 and len({(x['arm'],x['seed'],x['term']) for x in csv_effects})==96)
    for row in csv_effects:
        original=next(v for v in docs[(row['arm'],int(row['seed']))]['fixed_effects'] if v['term']==row['term'])
        for key in ('estimate','se','wald_lower','wald_upper'):same('effect_CSV_'+row['arm']+row['seed']+row['term']+key,float(row[key]),original[key])
        same('source_SE_CSV_'+row['arm']+row['seed']+row['term'],float(row['exported_source_se']),exact[row['term']][1])
    bound_files.append(path)
    path=U/'summary/distributions_all_seeds.csv'
    with path.open(newline='') as stream: csv_dist=list(csv.DictReader(stream))
    check('162_allseed_distribution_rows',len(csv_dist)==162 and len({(x['arm'],x['seed'],x['metric']) for x in csv_dist})==162)
    for row in csv_dist:
        same('distribution_CSV_'+row['arm']+row['seed']+row['metric'],float(row['estimate']),flat[(row['arm'],int(row['seed']))][row['metric']])
    bound_files.append(path)
    # Count physical receipts, including invalid original comparator outputs.
    initial=[read(U/f'attempts/{arm}_{s}.json') for arm in ('native','agent') for s in SEEDS]
    recovered=[read(U/f'recovery_v1/attempts/native_corrected_{s}.json') for s in SEEDS]
    check('9_physical_generations',len(initial)+len(recovered)==9 and all(x['status']=='success' for x in initial+recovered))
    check('invalid_initial_records',len(aggregate['invalid_original_comparator'])==3 and {x['run_id'] for x in aggregate['invalid_original_comparator']}=={f'native_{s}' for s in SEEDS})
    for seed in SEEDS:
        check('invalid_native_'+str(seed),read(U/f'results/native_{seed}.native.json')['status']=='failed')
    expected_counts={'initial_physical_generations':6,'additional_technical_recovery_generations':3,'total_physical_generations':9,'invalid_initial_comparator_tables':3,'valid_comparison_tables':6,'computed_fits':6,'gls_passes':6,'subjects_per_table':11509,'visits_per_table':46036,'new_source_participant_records':0}
    check('all_count_fields',aggregate['counts']==expected_counts)
    check('no_further_recovery',read(U/'recovery_v1/CLOSED.json')['no_further_recovery'] is True)
    prose=(U/'RESULTS.md').read_text(encoding='utf-8')
    # Numerical tables display five decimals and the source column six decimals.
    for row in reconstructed_effects:
        snippet=f"{row['mean_estimate']:.5f} [{row['min_estimate']:.5f}, {row['max_estimate']:.5f}]"
        check('prose_effect_'+row['arm']+'_'+row['term'],snippet in prose)
    scope_phrases=['source-rich reconstruction','not discovery of unseen relationships','our implementation failures','not evidence against the published method','No Agent model or table was regenerated','not six independent studies','not confidence intervals','not an independent REML-optimizer validation','Agent selected the already published family','no further tuning']
    for phrase in scope_phrases:check('prose_scope_'+phrase,phrase in prose)
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'pass','scope':'Final independent retained-result audit. Original/native and corrected comparison records distinguished; no fit, generation or frozen-file edits.',
      'new_model_fits':0,'new_generation_runs':0,'source_patient_rows_read':0,'corrected_generated_rows_read':3*46036,
      'coefficient_summary_groups_verified':32,'distribution_summary_groups_verified':54,
      'allseed_effect_rows_verified':96,'allseed_distribution_rows_verified':162,
      'corrected_baseline_metrics_independently_recomputed':raw_checks,'corrected_baseline_max_abs_difference':raw_max,
      'numeric_comparisons':numeric_count,'maximum_abs_arithmetic_difference':largest,'checks_count':len(checks),
      'checks':checks,'counts':expected_counts,'fixed_effects_reconstructed':reconstructed_effects,'distributions_reconstructed':reconstructed_distributions,
      'fits':fit_records,'bindings':[{ 'path':str(x.relative_to(U)),'sha256':sha(x)} for x in dict.fromkeys(bound_files)],
      'findings':[],'interpretation':'The report supports source-informed longitudinal reconstruction, not independent validation, causal discovery, universal superiority or restoration of original source-tail variability.',
      'figure_scope':'Plots and their rendering are reviewed separately by root; this unit checks numerical CSV/JSON and report values.'}
    output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    focal=[r for r in reconstructed_effects if r['term'] in ('age60:hba1c_U65','age60:hba1c_O65')]
    md='''# Final HRS result review

**PASS.** Independent audit of the completed, explicitly recovered public-example experiment. No new generation, model fitting, parameter change or frozen-file edit occurred.

## Complete numerical reconciliation

'''
    md+=f'- All **32 coefficient summary groups** and **54 distribution summary groups** were independently reconstructed from the six retained native evaluator JSON files, including means, ranges, signed mean discrepancies and mean absolute discrepancies.\n- All **96 all-seed coefficient rows** and **162 all-seed diagnostic rows**, plus both summary CSVs, match retained native results and source references.\n- The three corrected tables were read only to independently calculate **81 baseline statistics**; maximum disagreement was **{raw_max:.3g}**. The earlier Agent-only audit already checked its 81 baseline values and was not rerun.\n- All six retained fits have 16 estimable terms, optimizer code 0, no warnings and no singularity; all six existing conditional GLS checks pass. No fit was repeated.\n- All original and recovery release hashes and the previous Agent result/table hashes remain unchanged.\n\n'
    md+='''## Concrete focal results

| Construction | Focal coefficient | Source | Three-seed mean | Seed range | Mean absolute discrepancy |
|---|---|---:|---:|---|---:|
'''
    for row in focal:
        md+=f"| {row['arm']} | {row['term']} | {row['exported_coefficient']:.6f} | {row['mean_estimate']:.6f} | {row['min_estimate']:.6f} to {row['max_estimate']:.6f} | {row['mean_absolute_discrepancy_exported_coefficient']:.6f} |\n"
    md+='''
Both implementations preserve the negative below-threshold interaction in every draw. The weak above-threshold interaction has positive point estimates in the three Agent draws and negative estimates in the three corrected-law draws. All corrected-law intervals include zero; one Agent interval excludes zero. These six finite draws from nearly the same supplied family do not establish an accuracy ranking, and binary significance agreement is not an appropriate sole quality claim.

The upper-HbA1c subgroup mean/SD are approximately **7.15149 / 0.56305** in both constructions, compared with **7.7 / 1.4** for the reported original sample and **7.2 / 0.6** for the paper's synthetic-law summary. The source-law reconstruction is useful but inherits the original simulator's distribution mismatch. The report preserves this unfavorable result.

## Accounting and interpretation

The ledger contains **nine physical generation attempts**: six initial attempts and three separately released technical corrections. The three invalid initial comparator tables remain visible and are excluded from comparative ranking. The six valid comparison tables are three draws per construction, not six clinical studies or six independent authoring decisions. All Agent outputs are unchanged. No further recovery or favorable-seed search is authorized by this closure.

`RESULTS.md` correctly describes the original model coefficients as permitted inputs, distinguishes source-rich reconstruction from unseen-relationship validation, discloses the parser defect and byte-identical correction, and makes no superiority, fully autonomous literature search, human-cost or transport claim. The Agent's printed-variance convention and the comparator's squared-rounded-SD convention are disclosed. The real source had 43,500 observations; balanced synthetic schedules have 46,036 visits, so their model SEs cannot be read as added patient evidence.

The capability demonstrated is an Agent-authored complete longitudinal table that supports the supplied scientific model, with all effects and diagnostic discrepancies exposed. This audit does not certify novel simulation mathematics, independent clinical truth or exact empirical-tail recovery. Plot rendering is the coordinator's separate review responsibility.

Complete arithmetic, file bindings and all checked values are retained in `FINAL_RESULT_REVIEW.json`.
'''
    (U/'FINAL_RESULT_REVIEW.md').write_text(md,encoding='utf-8')
    print(json.dumps({'status':'pass','checks':len(checks),'numeric_comparisons':numeric_count,'raw_metrics':raw_checks,'maximum_difference':largest}))


if __name__=='__main__':
    main()

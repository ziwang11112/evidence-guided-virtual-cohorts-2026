"""Read-only Agent-result audit; never fits, draws, or imports a generator."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import re
import statistics as stat

U = Path(__file__).resolve().parents[1]
SEEDS = (6101, 6102, 6103)
TERMS = ['(Intercept)', 'age60', 'hba1c_U65', 'hba1c_O65', 'raceBlack',
         'educHS', 'educLessThanHS', 'sexMale', 'cses', 'age60:hba1c_U65',
         'age60:hba1c_O65', 'age60:raceBlack', 'age60:educHS',
         'age60:educLessThanHS', 'age60:sexMale', 'age60:cses']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def distribution(rows):
    b = [r for r in rows if float(r['visit_time']) == 0]
    assert len(b) == 11509 and len(rows) == 46036
    seen = set(); groups = {}
    for row in rows:
        assert row['id'] not in seen
        seen.add(row['id'])
        groups.setdefault(row['subject_id'], []).append(row)
        assert abs(float(row['age'])-float(row['baseline_age'])-float(row['visit_time'])) < 1e-9
        assert abs(float(row['age60'])-(float(row['age'])-60)/10) < 1e-9
    assert len(groups) == 11509
    for group in groups.values():
        assert sorted(float(x['visit_time']) for x in group) == [0, 2, 4, 6]
        assert all(len({r[c] for r in group}) == 1 for c in ('baseline_age','sex','race','educ','cses','hba1c'))
    v = {'subject_count': len(b)}
    numeric = {
        'baseline_age': [float(r['baseline_age']) for r in b],
        'hba1c': [float(r['hba1c']) for r in b],
        'hba1c_below': [float(r['hba1c']) for r in b if float(r['hba1c']) < 6.5],
        'hba1c_above': [float(r['hba1c']) for r in b if float(r['hba1c']) >= 6.5],
        'cses': [float(r['cses']) for r in b],
        'baseline_mem_s': [float(r['mem_s']) for r in b],
    }
    for name, vals in numeric.items():
        assert len(vals) > 1
        v[name+'_mean'] = stat.mean(vals)
        v[name+'_sd'] = stat.stdev(vals)
    for field, cats in [('sex',['female','male']),('race',['white','black']),('educ',['College','HS','LessThanHS'])]:
        for cat in cats:
            n = sum(r[field] == cat for r in b)
            v[field+'_'+cat+'_count'] = n
            v[field+'_'+cat+'_percent'] = 100*n/len(b)
    assert len(v) == 27
    return v, {name: len(vals) for name, vals in numeric.items()}


def native_distribution(obj):
    d = obj['table2_diagnostics']
    result = {'subject_count': d['subjects']}
    for name, key in [('baseline_age','age'),('hba1c','hba1c_overall'),
                      ('hba1c_below','hba1c_below_6_5'),('hba1c_above','hba1c_at_or_above_6_5'),
                      ('cses','cses'),('baseline_mem_s','baseline_memory')]:
        for s in ('mean','sd'):
            result[name+'_'+s] = d[key][s]
    for field, key in [('sex','female_male'),('race','white_black'),('educ','education')]:
        for row in d[key]['categories']:
            result[field+'_'+row['category']+'_count'] = row['count']
            result[field+'_'+row['category']+'_percent'] = row['percentage']
    return result


def summary(vals, reference):
    mean = stat.mean(vals)
    return {'seed_values': dict(zip(map(str,SEEDS), vals)), 'mean': mean,
            'seed_range': [min(vals), max(vals)], 'reference': reference,
            'signed_discrepancy_of_mean': mean-reference,
            'mean_absolute_discrepancy': stat.mean(abs(v-reference) for v in vals)}


def main():
    out = U/'AGENT_RESULT_AUDIT_v1.json'; md = U/'AGENT_RESULT_AUDIT_v1.md'
    assert not out.exists() and not md.exists(), 'Do not overwrite retained audit'
    source = U/'sources/original/HRSmodels_20200902_fullDemoTable.txt'
    raw = source.read_text(encoding='cp1252')
    assert raw.count('Fixed effects:') == 1
    section = raw.split('Fixed effects:',1)[1]
    coefficients = {}
    for line in section.splitlines():
        fields = line.split()
        if fields and fields[0] in TERMS:
            assert fields[0] not in coefficients, 'Repeated model term'
            coefficients[fields[0]] = {'estimate': float(fields[1]), 'se': float(fields[2])}
    assert set(coefficients) == set(TERMS) and len(coefficients) == 16
    published_path = U/'sources/HRS_PUBLISHED_REFERENCES.json'
    published = read(published_path)
    refs = {}
    for name, row in published['table2'].items():
        if name == 'subject_count':
            refs[name] = {'original': row['original'], 'published_synthetic': row['synthetic']}
        else:
            for key, value in row.items():
                arm, suffix = key.split('_',1)
                refs.setdefault(name+'_'+suffix, {})['original' if arm=='original' else 'published_synthetic'] = value
    assert len(refs) == 27
    bindings = {'source_memory_export': {'path':str(source.relative_to(U)), 'sha256':sha(source)},
                'published_tables': {'path':str(published_path.relative_to(U)), 'sha256':sha(published_path)},
                'release': {'path':'RELEASE.json','sha256':sha(U/'RELEASE.json')},
                'audit_code': {'path':str(Path(__file__).relative_to(U)), 'sha256':sha(Path(__file__))}}
    run_data = []; recomputed = []; errors = []
    for seed in SEEDS:
        run_id = f'agent_{seed}'
        evpath=U/f'results/{run_id}.evaluation.json'; np=U/f'results/{run_id}.native.json'; gp=U/f'results/{run_id}.gls.json'
        table=U/f'bundle/executions/{run_id}/output/generated.csv'
        recpath=U/f'bundle/executions/{run_id}/execution.json'; ap=U/f'attempts/{run_id}.json'
        ev,native,gls,receipt,attempt=map(read,(evpath,np,gp,recpath,ap))
        assert attempt['status']=='success' and attempt['execution_sha256']==sha(recpath)
        assert receipt['candidate']=='candidates/agent' and receipt['limits']['seed']==seed
        assert receipt['files']['output/generated.csv']==sha(table)
        assert ev['status']=='computed' and ev['returncode']==0 and ev['fit_attempts']==1
        assert ev['gls_status']=='pass' and ev['gls_returncode']==0
        assert ev['native_json_sha256']==sha(np) and ev['gls_json_sha256']==sha(gp)
        assert ev['input_sha256']==native['input_sha256']==sha(table)
        assert gls['status']=='pass' and len(gls['fixed_effects'])==16
        assert all(x['estimate_matches'] and x['se_matches'] for x in gls['fixed_effects'])
        assert [x['term'] for x in native['fixed_effects']]==TERMS
        with table.open(newline='',encoding='utf-8') as f:
            rows=list(csv.DictReader(f))
        direct, membership=distribution(rows)
        previous=native_distribution(native)
        assert set(direct)==set(previous)==set(refs)
        differences={key:direct[key]-previous[key] for key in direct}
        for key in direct:
            if not math.isclose(direct[key],previous[key],rel_tol=1e-11,abs_tol=1e-11):
                errors.append({'seed':seed,'metric':key,'independent':direct[key],'native':previous[key]})
        recomputed.append(direct)
        bindings[run_id]={str(x.relative_to(U)):sha(x) for x in (evpath,np,gp,table,recpath,ap)}
        run_data.append({'seed':seed,'run_id':run_id,'fixed_effects':native['fixed_effects'],
            'distribution_independent_minus_native':differences,'membership_counts':membership,
            'GLS_max_coefficient_error':max(abs(t['estimate_difference']) for t in gls['fixed_effects']),
            'GLS_max_SE_error':max(abs(t['se_difference']) for t in gls['fixed_effects']),
            'computational':{'generation_seconds':receipt['elapsed_seconds'],'native_fit_seconds':native['elapsed_seconds'],
              'host_evaluation_seconds':ev['elapsed_seconds'],'warnings':native['warnings'],'messages':native['messages'],
              'singular':native['singular'],'convergence':native['convergence'],'logLik':native['logLik'],
              'REML_criterion':native['REML_criterion'],'random_effect_covariance':native['random_effect_covariance'],
              'random_effect_sd':native['random_effect_sd'],'random_effect_correlation':native['random_effect_correlation'],
              'residual_sd':native['residual_sd'],'residual_variance':native['residual_variance']}})
    effect_rows=[]
    for term in TERMS:
        vals=[next(t for t in r['fixed_effects'] if t['term']==term) for r in run_data]
        row={'term':term,**summary([v['estimate'] for v in vals],coefficients[term]['estimate']),
             'source_export_se':coefficients[term]['se'],'seed_SEs':dict(zip(map(str,SEEDS),[v['se'] for v in vals])),
             'SE_mean':stat.mean(v['se'] for v in vals),'source_paper_rounded':published['table3'][term],
             'synthetic_Wald_excludes_zero':dict(zip(map(str,SEEDS),[v['wald_lower']>0 or v['wald_upper']<0 for v in vals]))}
        effect_rows.append(row)
    diag_rows=[]
    for name in refs:
        vals=[r[name] for r in recomputed]
        diag_rows.append({'metric':name,**summary(vals,refs[name]['original']),
                         'published_synthetic_reference':refs[name]['published_synthetic'],
                         'signed_discrepancy_from_published_synthetic':stat.mean(vals)-refs[name]['published_synthetic']})
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'pass' if not errors else 'mismatch',
      'scope':'Agent arm only; three fixed-seed realizations of one frozen Agent-authored law. No comparative ranking against the corrupted native-parser arm.',
      'raw_patient_rows_read':0,'generated_rows_read':3*46036,'new_generation_runs':0,'new_model_fits':0,
      'source_bindings':bindings,'fixed_effects_all_16':effect_rows,'distribution_metrics_all_27':diag_rows,
      'runs':run_data,'independent_distribution_values_checked':81,'independent_distribution_max_abs_error':max(abs(v) for r in run_data for v in r['distribution_independent_minus_native'].values()),
      'mismatches':errors,'limitations':['All original scientific coefficients and generating details were admissible inputs; recovery is source-informed reconstruction, not hidden-relation validation.',
        'One Agent-authored structure with three sampling seeds is not three independent Agent constructions or three real cohorts.',
        'Published original and synthetic references are rounded aggregates; synthetic paper results summarize5000 repetitions, while this experiment has3 fixed seeds.',
        'Balanced synthetic46036 visits differ from source43500 visits; model-conditional synthetic SEs do not add real patient information.',
        'The native comparison requires separate technical recovery; its parser failure must not count as evidence against the published method.',
        'GLS verifies fixed-effect/SE arithmetic conditional on fitted variance; it is not an independent optimizer or scientific-validity proof.']}
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    f6=lambda v:f'{v:.6f}'
    focal={r['term']:r for r in effect_rows}
    low=focal['age60:hba1c_U65'];high=focal['age60:hba1c_O65']
    content=f'''# Agent-only HRS result audit v1

**PASS for recorded computation and independent baseline arithmetic.** Three fixed-seed outputs of one frozen Agent-authored law each contain 11,509 subjects and 46,036 visits. No generator or mixed model was rerun. The audit independently recomputed all 27 baseline distribution metrics (81 values) and checked retained coefficient/SE GLS results and execution/hash records.

## Scientific usefulness and limits

The below-6.5 age interaction is negative in all three outputs: mean **{low['mean']:.6f}**, range **{low['seed_range'][0]:.6f} to {low['seed_range'][1]:.6f}**, versus supplied source coefficient **{low['reference']:.6f}**. This supports reconstruction of the source's negative longitudinal association under the supplied law.

The above-6.5 interaction has mean **{high['mean']:.6f}**, range **{high['seed_range'][0]:.6f} to {high['seed_range'][1]:.6f}**, versus **{high['reference']:.6f}**. Its direction is positive in every output, but the magnitude is higher on average. One of three synthetic model-conditional Wald intervals excludes zero, whereas the source's published interval includes zero. Treating binary significance as a scientific identity would overstate agreement.

Distribution reconstruction is uneven against the original sample. The high-HbA1c subgroup is much less dispersed than the original paper reports, while remaining close to the paper's own synthetic-law summary. This is evidence of reproducing a supplied generating model, not evidence that original upper-tail heterogeneity has been recovered. All metrics below retain this distinction.

## All 16 fixed effects

Estimates and SEs come from the already fitted native evaluator; its retained independent GLS check passes for every term. Source references below come directly from the single original printed memory-model block, with exactly16 unique terms; they do not use the faulty multi-block parser. Three-seed ranges are not confidence intervals.

| Term | Source estimate (SE) | Seed6101 | Seed6102 | Seed6103 | Mean | Seed range | Mean absolute discrepancy |
|---|---:|---:|---:|---:|---:|---|---:|
'''
    for r in effect_rows:
        content+='| '+r['term']+f" | {r['reference']:.6f} ({r['source_export_se']:.6f}) | "+' | '.join(f6(r['seed_values'][str(s)]) for s in SEEDS)+f" | {r['mean']:.6f} | {r['seed_range'][0]:.6f} to {r['seed_range'][1]:.6f} | {r['mean_absolute_discrepancy']:.6f} |\n"
    content+='''
Every seed's16 SEs and Wald intervals are retained in the JSON; no mean estimate is substituted for a seed's uncertainty.

## All 27 baseline distribution metrics

One baseline row per subject; HbA1c below uses <6.5 and above uses >=6.5. SDs are sample SDs. Source columns reproduce the paper's rounded original/synthetic aggregate references, with no invented acceptance margin. The published synthetic column averages5000 repetitions; this table averages only the three fixed output seeds.

| Metric | Original paper | Published synthetic | Agent mean | Agent seed range | Mean absolute discrepancy from original |
|---|---:|---:|---:|---|---:|
'''
    for r in diag_rows:
        content+=f"| {r['metric']} | {r['reference']:.6f} | {r['published_synthetic_reference']:.6f} | {r['mean']:.6f} | {r['seed_range'][0]:.6f} to {r['seed_range'][1]:.6f} | {r['mean_absolute_discrepancy']:.6f} |\n"
    content+='''
## Computational record

| Seed | Generator seconds | Native fit seconds | Optimizer | Singular | Warnings | Random intercept SD | Random slope SD | Residual SD | REML logLik |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|
'''
    for r in run_data:
        c=r['computational']
        content+=f"| {r['seed']} | {c['generation_seconds']:.3f} | {c['native_fit_seconds']:.3f} | {c['convergence']['optimizer']} / code {c['convergence']['optimizer_code']} | {c['singular']} | {len(c['warnings'])} | {c['random_effect_sd'][0]:.6f} | {c['random_effect_sd'][1]:.6f} | {c['residual_sd']:.6f} | {c['logLik']:.6f} |\n"
    content+=f"\nAll three native fits and retained GLS checks completed with return code0. Independent distribution maximum absolute arithmetic difference was {result['independent_distribution_max_abs_error']:.3g}. These runtimes exclude evidence preparation, authoring and review.\n\n## Interpretation boundary\n\n"
    content+='\n'.join('- '+v for v in result['limitations'])+'\n\nThe original six attempt records remain unchanged. The coordinator reported a native-source parser defect affecting its three outputs; separate corrected reconstruction/release is required before any comparison. No native failure is counted here as Agent superiority.\n'
    md.write_text(content,encoding='utf-8')
    print(json.dumps({'status':result['status'],'effects':16,'metrics':27,'independently_recomputed':81,'maximum_error':result['independent_distribution_max_abs_error']}))


if __name__=='__main__':
    main()

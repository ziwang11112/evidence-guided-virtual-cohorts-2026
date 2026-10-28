"""Source-only contracts. Adapted from population_framework runner/observers.

No reference rows or reserved results are loaded here. This is procedural review,
not an adversarial security boundary.
"""
from __future__ import annotations
import ast
import copy
import hashlib
import json
import types
from pathlib import Path
import numpy as np
import pandas as pd


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def allocation(ids):
    if not 1 <= len(ids) <= 3 or len(set(ids)) != len(ids):
        raise ValueError('Declare one to three unique scenarios')
    return dict(zip(ids, {1:[20],2:[10,10],3:[7,7,6]}[len(ids)]))


def load_generator(path):
    source = Path(path).read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    allowed = {'numpy','pandas','scipy','math','typing','__future__','copy','dataclasses','json','itertools'}
    forbidden = {'open','eval','exec','compile','__import__','input','breakpoint'}
    io = {'read_csv','read_json','read_pickle','read_excel','read_parquet','to_csv','to_json','to_pickle','to_excel','to_parquet','load','save','loadtxt','savetxt','fromfile','tofile','seed','set_state'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots = [a.name.split('.')[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            roots = [(node.module or '').split('.')[0]]
        else:
            roots = []
        if set(roots) - allowed:
            raise ValueError('Unapproved import: '+str(roots))
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in forbidden:
                raise ValueError('Forbidden dynamic execution or I/O')
            if isinstance(node.func, ast.Attribute) and node.func.attr in io:
                raise ValueError('Forbidden I/O or global RNG mutation: '+node.func.attr)
    module = types.ModuleType('candidate_'+hashlib.sha256(source.encode()).hexdigest()[:12])
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    if not callable(getattr(module,'generate',None)):
        raise ValueError('Missing generate(n, seed, evidence, context="target")')
    return module


def validate_decision(decision, task, evidence):
    required = ['run_id','lineage_id','branch','action','model_metadata','model_family','evidence_use','components','scenarios','changes_from_parent','source_check_results','calibration_log','intended_uses','unvalidated_uses','next_information_request']
    if any(k not in decision for k in required):
        raise ValueError('Missing decision fields: '+str([k for k in required if k not in decision]))
    for key in ['run_id','lineage_id','branch']:
        if decision[key] != task[key]:
            raise ValueError('Decision identity mismatch: '+key)
    if decision['action'] not in ['build','revise','no_op','fixed_statistical_reference']:
        raise ValueError('Invalid action')
    ids = [s['id'] for s in decision['scenarios']]
    if task['branch'] in ['initial','ordinary'] and ids != ['target']:
        raise ValueError('Single selected ordinary/initial/statistical model must use target context')
    counts = allocation(ids)
    for s in decision['scenarios']:
        if not s['id'].replace('_','').isalnum() or s.get('n_cohorts') != counts[s['id']]:
            raise ValueError('Invalid scenario name or fixed allocation')
        for key in ['assumption','inclusion_rationale','unresolved_dependencies','affected_analysis_classes']:
            if key not in s:
                raise ValueError('Scenario description missing: '+key)
    uses = decision['evidence_use']
    if sorted(x['id'] for x in uses) != sorted(x['id'] for x in evidence['evidence_items']):
        raise ValueError('Address each evidence ID exactly once')
    for use in uses:
        if use.get('action') not in ['use','qualify','defer'] or not use.get('reason'):
            raise ValueError('Evidence decision requires action and reason')
        for k in ['operator','population','measurement','provenance']:
            if k not in use:
                raise ValueError('Missing evidence applicability field: '+k)
    if not decision['model_metadata'] or not decision['components']:
        raise ValueError('Model metadata/components missing')
    log=decision['calibration_log']
    structures=log.get('examined_structures',[])
    if not 1 <= len(structures) <= (1 if task['branch']=='initial' else 3):
        raise ValueError('Common candidate-structure budget exceeded or missing')
    structure_ids=[x['id'] for x in structures]
    if len(set(structure_ids))!=len(structure_ids): raise ValueError('Duplicate candidate structure')
    final_map=log.get('final_scenario_to_structure',{})
    if set(final_map)!=set(ids) or not set(final_map.values()).issubset(structure_ids):
        raise ValueError('Map each final scenario to an examined structure')
    total=0
    for st in structures:
        seeds=st.get('source_seeds_evaluated',[])
        if len(seeds)!=len(set(seeds)) or not set(seeds).issubset({810101,810102,810103}):
            raise ValueError('Only three fixed source seeds per examined structure')
        # Controller checks the same scheduled seeds, not three extra draws.
        total += 3 if st['id'] in final_map.values() else len(seeds)
        if not st.get('disposition') or not st.get('reason'): raise ValueError('Log selected and rejected structure rationale')
    if total > (3 if task['branch']=='initial' else 9): raise ValueError('Common numerical calibration budget exceeded')
    return counts


def validate_frame(df, schema, evidence, n):
    if not isinstance(df,pd.DataFrame):
        raise TypeError('Return pandas.DataFrame')
    if list(df) != schema['columns']:
        raise ValueError('Columns/order differ from declared CSV schema')
    if df.duplicated(schema['keys']).any() or df[schema['keys']].isna().any().any():
        raise ValueError('Duplicate/missing keys')
    if schema['format'] == 'long':
        if len(df)!=n*5 or df.person_id.nunique()!=n or not df.groupby('person_id').month.apply(lambda x:sorted(x)==[0,3,6,9,12]).all():
            raise ValueError('Require n persons with exactly five declared visits')
        for col in schema['columns']:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError('Ross columns must be numeric')
        for col in schema['columns'][2:]:
            x=df[col].dropna().to_numpy(float)
            if not np.isfinite(x).all(): raise ValueError('Nonfinite measurement')
            bounds=schema['bounds'][col]
            if (x < bounds[0]).any() or (x > bounds[1]).any(): raise ValueError('Support violation: '+col)
        if not np.allclose(df.gng.dropna(),np.round(df.gng.dropna())): raise ValueError('gng must be integer')
        for m in evidence['marginal_summaries']:
            expected=int(round(m['n_observed']*n/schema['n_persons']))
            if df.loc[df.month.eq(m['month']),m['variable']].notna().sum()!=expected:
                raise ValueError('Per-visit nonmissing count differs from packet')
    else:
        if len(df)!=n or df.participant_id.nunique()!=n: raise ValueError('Wrong paired person count')
        for endpoint,m in evidence['moments'].items():
            cols=[endpoint+'_pre',endpoint+'_post']
            if not df[cols].isna().eq(df[cols[0]].isna(),axis=0).all().all(): raise ValueError('Incomplete analysis pairs')
            expected=int(round(m['n']*n/schema['n_persons']))
            if df[cols[0]].notna().sum()!=expected: raise ValueError('Wrong endpoint complete-pair count')
            x=df[cols].dropna().to_numpy(float)
            if not np.isfinite(x).all(): raise ValueError('Nonfinite measurement')
            if endpoint!='leptin_log10' and (x<=0).any(): raise ValueError('Positive measurement required')
        if schema.get('fixed_missing_last') and n==schema['n_persons']:
            for endpoint in ['glucose','triglycerides']:
                if not df.iloc[-1][[endpoint+'_pre',endpoint+'_post']].isna().all():
                    raise ValueError('Use final synthetic row for unavailable endpoint pairs')
    return True


def source_diagnostics(df, schema, evidence):
    records=[]
    if schema['format']=='long':
        moments=[dict(m,field=m['variable'],subset=df.loc[df.month.eq(m['month']),m['variable']].dropna(),id=f"{m['variable']}_month{m['month']}") for m in evidence['marginal_summaries']]
    else:
        moments=[dict(mean=m[t+'_mean'],sd=m[t+'_sd'],n_observed=m['n'],field=e+'_'+t,subset=df[e+'_'+t].dropna(),id=e+'_'+t) for e,m in evidence['moments'].items() for t in ['pre','post']]
    for m in moments:
        x=m['subset']; nn=len(x)
        mean=float(x.mean()); sd=float(x.std(ddof=1))
        # Transparent diagnostic envelope, not an equivalence or validity test.
        mean_tol=max(3*m['sd']/np.sqrt(nn),.002)
        sd_tol=max(3*m['sd']/np.sqrt(2*(nn-1)),.002)
        records.append(dict(id=m['id'],n=nn,mean=mean,sd=sd,expected_mean=m['mean'],expected_sd=m['sd'],mean_tolerance=mean_tol,sd_tolerance=sd_tol,within_source_diagnostic_envelope=abs(mean-m['mean'])<=mean_tol and abs(sd-m['sd'])<=sd_tol))
    return records


def call_checked(module, schema, evidence, seed, context):
    before=copy.deepcopy(evidence)
    state=np.random.get_state()
    df=module.generate(schema['n_persons'],seed,evidence,context=context)
    after=np.random.get_state()
    if before!=evidence: raise ValueError('Generator mutated evidence')
    if not all(np.array_equal(a,b) for a,b in zip(state,after)): raise ValueError('Generator changed global numpy RNG')
    validate_frame(df,schema,evidence,schema['n_persons'])
    return df

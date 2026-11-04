"""Run each unchanged candidate program with entirely invented scientific laws.

Separate 12-subject fixtures; no HRS-configured sampling or native model fits.
"""
from pathlib import Path
import copy
import hashlib
import json
import math
import shutil
import sys

UNIT = Path(__file__).resolve().parent
sys.path.insert(0, str(UNIT.parents[1]))
from cohort_harness.lifecycle import freeze_candidate, read_table
from cohort_harness.execution import run_candidate, verify_execution

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def put(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def fixture_parameters(arm, real):
    p = copy.deepcopy(real)
    if arm == 'native':
        p['study'] = {'n_subjects':12, 'visit_times':[0,2,4,6]}
        p['demographic_cells'] = [dict(age_category='toy', sex=s, race=r, count=3)
                                  for s in ['female','male'] for r in ['white','black']]
        p['age_bins'] = {'toy': {'lower': 51, 'upper': 53}}
        p['transforms'] = {k: {'value': v} for k,v in
                           [('age_center',60),('age_scale',10),('hba1c_knot',6.5)]}
        for model in ['cses','hba1c','memory']:
            p[model]['coefficients'] = {term:{'estimate': .02*i} for i,term in enumerate(p[model]['coefficients'])}
        p['cses']['residual_sd'] = {'value':.2}
        p['education']['coefficients'] = {'HS':[0]*5, 'LessThanHS':[0]*5}
        p['education'].pop('standard_errors',None)
        p['education'].pop('sources',None)
        p['hba1c']['coefficients'] = {term:{'estimate': math.log(5) if term=='(Intercept)' else 0}
                                     for term in p['hba1c']['coefficients']}
        p['hba1c']['dispersion'] = {'value':.1}
        p['memory']['random'] = {k:{'value':v} for k,v in
            [('intercept_sd',.2),('slope_sd',.1),('correlation',.25),('residual_sd',.3)]}
        return p
    p['cohort_design'] = {'n_subjects':12, 'visit_times':[0,2,4,6], 'identifier_prefix':'toy_'}
    p['demographic_model']['cells'] = [dict(age_bin=0, sex=s, race=r, count=3)
                                      for s in ['female','male'] for r in ['white','black']]
    p['age_model']['bin_bounds'] = [[51,53]]
    p['cses_model']['coefficients'] = [0,.02,.04]
    p['cses_model']['residual_sd'] = .2
    p['education_model']['coefficients'] = [[0]*5 for _ in range(3)]
    p['hba1c_model']['coefficients'] = [math.log(5)] + [0]*6
    p['hba1c_model']['dispersion'] = .1
    p['memory_model']['coefficients'] = [.02*i for i in range(16)]
    p['memory_model'].update(random_intercept_variance=.04, random_slope_variance=.01,
                             random_effect_correlation=.25, residual_variance=.09)
    return p

def main():
    parent = UNIT / 'invented_execution_fixtures'
    parent.mkdir(exist_ok=False)
    reports = []
    for arm in ['native','agent']:
        original = UNIT / 'bundle/candidates' / arm
        bundle = parent / arm
        candidate = bundle / 'candidates/toy'
        candidate.mkdir(parents=True)
        task = load(UNIT / 'bundle/task.json')
        task.update(task_id='INVENTED_INTERFACE_ONLY_' + arm, n_rows=48,
                    population='Twelve invented artificial subjects; no HRS scientific parameter law.')
        task['information_policy'] = {'mode':'prior_only', 'excluded_cohorts':[], 'allowed_tools':['isolated_fixture_execution']}
        put(bundle / 'task.json', task)
        put(bundle / 'registry.json', {'artifacts':[]})
        parameters = fixture_parameters(arm, load(original / 'model_spec.json')['parameters'])
        put(candidate / 'model_spec.json', {'parameters':parameters,
            'assumptions':[{'id':'toy','description':'Every active statistical coefficient, cell count, residual, covariance and distribution setting is invented for mechanical checking; age/spline coordinate conventions remain the task interface.'}],
            'parameter_provenance': {k:{'evidence_ids':[], 'assumption_ids':['toy'], 'derivation':'Invented fixture'} for k in parameters}})
        put(candidate / 'evidence.json', {'schema_version':1,'sources':[],'items':[]})
        put(candidate / 'checks.json', {'scope':'fixture_only','records':[{'name':'not_yet_executed','status':'not_computable','detail':'External isolated execution receipt will record fixture outcome.'}],'artifacts':[]})
        (candidate / 'decision.md').write_text('Invented mechanical fixture, not an HRS cohort or scientific result. Unchanged candidate program; entirely replaced active scientific parameters.\n', encoding='utf-8')
        shutil.copyfile(original / 'generator.py', candidate / 'generator.py')
        freeze_candidate(bundle, 'candidates/toy')
        receipt = run_candidate(bundle, 'candidates/toy', 'fixture', 991, timeout_seconds=60,
                                memory_mb=1024, output_bytes=1000000, log_bytes=100000)
        verify_execution(bundle, 'fixture')
        report = {'arm':arm, 'status':receipt['status'], 'scope':'invented_fixture_only',
                  'program_sha256': hashlib.sha256((original / 'generator.py').read_bytes()).hexdigest(),
                  'error':receipt['error'], 'HRS_configured_rows':0, 'invented_rows':48}
        if receipt['status']=='success':
            table = read_table(bundle / 'executions/fixture/output/generated.csv', task, output=True)
            checks = {'subjects': table.subject_id.nunique()==12,
                      'visits': all(sorted(g.visit_time.tolist())==[0,2,4,6] for _,g in table.groupby('subject_id')),
                      'age': bool(((table.age-table.baseline_age-table.visit_time).abs()<1e-9).all()),
                      'positive_gamma': bool((table.hba1c>0).all()),
                      'baseline_stability': all(g[['baseline_age','sex','race','educ','cses','hba1c']].nunique().eq(1).all() for _,g in table.groupby('subject_id'))}
            report['structural_checks'] = {k:bool(v) for k,v in checks.items()}
            report['passed'] = all(checks.values())
        else:
            report['passed'] = False
        reports.append(report)
        print(json.dumps(report), flush=True)
    put(UNIT / 'INVENTED_EXECUTION_REVIEW.json', {'scope':'two isolated mechanical fixtures', 'results':reports,
           'formal_attempts_spent':0, 'passed':all(x['passed'] for x in reports)})

if __name__=='__main__':
    main()

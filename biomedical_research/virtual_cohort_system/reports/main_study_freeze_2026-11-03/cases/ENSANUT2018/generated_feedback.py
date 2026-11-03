"""Generated-table-only ENSANUT provider; never loads a target reference."""
from pathlib import Path
import hashlib
import importlib.util
import json

PROJECT = Path(__file__).resolve().parents[4]
ENGINE = PROJECT / 'work/autonomous_research_cycle2_2026-10-31/analysis/analytical_engine.py'
ENGINE_SHA256 = '1799c017b60f8fd3a9af409a524d3ebd9e54c81016e52da760aeafaefe03289d'
ANALYSES = {'Q1_age10':'%/10years','Q2_bmi5':'%/5kg/m^2','Q3_bmi5':'%/5kg/m^2'}
UNITS = {'age':'year','female':'1','bmi':'kg/m^2','glucose':'mg/dL','hba1c':'%'}
DIAGNOSTICS = {
    'Q2_minus_Q3_bmi5':'%/5kg/m^2',
    'glucose10_age_sex':'%/10mg/dL',
    'q1_residual_rms':'%',
    **{variable+'.'+statistic:unit for variable,unit in UNITS.items()
       for statistic in ('mean','sd_population','q10','q50','q90')},
}


def engine():
    if hashlib.sha256(ENGINE.read_bytes()).hexdigest() != ENGINE_SHA256:
        raise ValueError('Pinned pure analytical engine changed')
    spec = importlib.util.spec_from_file_location('ensanut_pure_analytical_engine',ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generated_statistics(frame, *, expected_rows=3000, expected_per_cell=375):
    """Use frozen WLS/weighted-quantile definitions on the current output only."""
    mod = engine()
    try:
        if len(frame) != expected_rows:
            raise mod.InputValidationError('Output row count differs from task')
        values = mod.validate_cohort(frame)
        _, counts = mod._weights_and_counts(values)
        if any(count != expected_per_cell for count in counts):
            raise mod.InputValidationError('Output must meet the exact eight-cell allocation')
        result = mod.analyze_cohort(frame)
    except mod.AnalyticalError as exc:
        return {'analyses':[{'id':name,'value':None,'unit':unit,'status':'unavailable','n':len(frame),'reason':str(exc)} for name,unit in ANALYSES.items()],
                'diagnostics':[{'id':name,'value':None,'unit':unit,'status':'unavailable','n':len(frame),'reason':str(exc)} for name,unit in DIAGNOSTICS.items()],
                'n':len(frame),'quality':{'status':'failed','error_code':exc.code,'reason':str(exc)}}
    analyses=[]
    for name,unit in ANALYSES.items():
        model = 'Q2_without_glucose' if name=='Q2_bmi5' else 'Q1_Q3_full'
        analyses.append({'id':name,'value':result['questions'][name],'unit':unit,'status':'computed','n':len(frame),'rank':result['models'][model]['rank']})
    diagnostics=[{'id':'Q2_minus_Q3_bmi5','value':result['questions']['Q2_minus_Q3_bmi5'],'unit':'%/5kg/m^2','status':'computed','n':len(frame)},
       {'id':'glucose10_age_sex','value':result['secondary']['glucose10_age_sex'],'unit':'%/10mg/dL','status':'computed','n':len(frame)},
       {'id':'q1_residual_rms','value':result['q1_residual_rms'],'unit':'%','status':'computed','n':len(frame)}]
    for variable,statistics in result['diagnostics'].items():
        for statistic,value in statistics.items():
            diagnostics.append({'id':variable+'.'+statistic,'value':value,'unit':UNITS[variable],'status':'computed','n':len(frame)})
    return {'analyses':analyses,'diagnostics':diagnostics,'n':len(frame),
      'quality':{'status':'passed','demographic_cell_counts':result['demographic_cell_counts'],
        'duplicate_measurement_rows':int(frame.loc[:,mod.SCIENTIFIC_COLUMNS].duplicated().sum()),
        'weighting':'Equal 1/8 demographic strata; no national-weighting claim'}}


def evaluate_generated(bundle,candidate,run_id,profile):
    """Validate receipt then read that generated CSV; profile may not name references."""
    from cohort_harness.execution import verify_execution
    from cohort_harness.lifecycle import read_table
    bundle = Path(bundle)
    config = json.loads(Path(profile).read_text(encoding='utf-8-sig'))
    if any(k in config for k in ('reference','reference_summary','target_results')):
        raise ValueError('Reference fields forbidden in generated-only profile')
    if config['case_id'] != 'ENSANUT2018' or config['information_condition'] not in ('E0','E1'):
        raise ValueError('Unexpected generated-only profile')
    receipt = verify_execution(bundle,run_id)
    if receipt['status']!='success' or receipt['candidate']!='candidates/'+str(candidate).removeprefix('candidates/'):
        raise ValueError('Execution receipt mismatch')
    task=json.loads((bundle/'task.json').read_text(encoding='utf-8-sig'))
    if task['n_rows'] != 3000 or task['mode']!='whole_cohort':
        raise ValueError('Unexpected task row count/mode')
    output=bundle/'executions'/run_id/'output/generated.csv'
    frame=read_table(output,task,output=True)
    return generated_statistics(frame)

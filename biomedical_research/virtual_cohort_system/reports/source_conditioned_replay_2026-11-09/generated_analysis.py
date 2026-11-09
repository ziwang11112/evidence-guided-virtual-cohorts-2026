"""Same existing requested analyses, generated tables only; no reference inputs."""
from pathlib import Path
import importlib.util
import json
import pandas as pd
PROJECT=Path(__file__).resolve().parents[2]
PROVIDER=PROJECT/'work/evidence_use_cross_task_2026-11-05/lipid_provider.py'

def analyze(output_path,task_path,request_path):
    task=json.loads(Path(task_path).read_text(encoding='utf-8-sig'))
    request=json.loads(Path(request_path).read_text(encoding='utf-8-sig'))
    spec=importlib.util.spec_from_file_location('source_conditioned_lipid_analysis',PROVIDER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.generated_statistics(pd.read_csv(output_path,dtype={'id':str}),task['n_rows'])
    result['scope']='source_conditioned_development_generated_only_no_reference'
    result['requested_analyses']=request['analyses']
    return result

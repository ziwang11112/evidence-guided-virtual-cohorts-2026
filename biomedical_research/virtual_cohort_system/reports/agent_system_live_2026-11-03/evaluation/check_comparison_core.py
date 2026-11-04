"""One bounded in-memory numerical fixture; no biomedical table output or reference reads."""
import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from generated_diagnostics import analyze_generated
from comparison_core import analyze_reference,independently_check

root=Path(__file__).resolve().parent
rng=np.random.default_rng(923714)
n=480
f=pd.DataFrame({'age':rng.uniform(35,74,n),'female':rng.integers(0,2,n),
                'bmi':rng.uniform(17,34,n),'glucose':rng.uniform(3,11,n),
                'survey_commid':np.repeat(np.arange(1,41),12)})
f['hba1c']=3+.018*f.age+.022*f.bmi+.14*f.glucose+rng.uniform(-.7,.7,n)
checks=[]
for key in ('A','B'):
    for reference in (False,True):
        analysis=analyze_reference(f,key) if reference else analyze_generated(f,key)
        checks.append({'request':key,'reference':reference,**independently_check(f,analysis,key,reference=reference)})
out={'checks':checks,'reference_reads':0,'tables_written':0,
     'fixture':'invented in-memory arithmetic; no patient evidence',
     'comparison_core_sha256':hashlib.sha256((root/'comparison_core.py').read_bytes()).hexdigest()}
with (root/'COMPARISON_CORE_SELF_CHECK.json').open('x',encoding='utf-8') as stream:
    json.dump(out,stream,indent=2);stream.write('\n')
print(json.dumps(out,indent=2))

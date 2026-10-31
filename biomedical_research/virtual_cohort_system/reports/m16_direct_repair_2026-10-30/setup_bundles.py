"""Prepare equal seed inputs; never reads or generates urate outcomes."""
from pathlib import Path
import json
import hashlib
import shutil
import sys

R=Path(__file__).resolve().parent
P=R.parent.parent
sys.path.insert(0,str(P))
from cohort_harness.literature import run_literature

OLD=P/'work/m15b_literature_direct_2026-10-30/visible/bundle'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False); f.write('\n')

def main():
    observed=R/'visible/observed.csv'
    if not observed.is_file(): raise ValueError('Custodian observations not ready')
    registry=json.loads((OLD/'registry.json').read_text())
    seeds=[a for a in registry['artifacts'] if a['origin']=='curator']
    if len(seeds)!=11: raise ValueError('Unexpected seed inventory')
    for a in seeds:
        if digest(OLD/a['path'])!=a['sha256']: raise ValueError('Seed hash changed')
    receipts=[]
    for bid in ('b1','b2','b3'):
        b=R/'visible'/bid/'bundle'
        b.mkdir(parents=True,exist_ok=False)
        (b/'candidates').mkdir()
        for a in seeds:
            target=b/a['path'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(OLD/a['path'],target)
        write(b/'registry.json',{'artifacts':seeds})
        task=json.loads((OLD/'task.json').read_text())
        task['task_id']='M16_direct_repair_'+bid+'_2026_10_30'
        task['budget']={'source_queries':8,'source_downloads':4,'revisions':2}
        write(b/'task.json',task)
        shutil.copyfile(observed,b/'observed.csv')
        shutil.copyfile(R/'BUILDER_TASK.md',b.parent/'TASK.md')
        shutil.copyfile(R/'SEED_PROVENANCE.md',b.parent/'SEED_PROVENANCE.md')
        init=run_literature(b,'init')
        receipts.append({'builder':bid,'observed_sha256':digest(b/'observed.csv'),
                         'seed_registry_sha256':digest(b/'registry.json'),
                         'task_sha256':digest(b/'task.json'),'gateway_init':init})
    write(R/'admission/bundle_preparation.json',{'builders':receipts,'outcomes_read':False,
          'rows_generated':False,'seed_files':11,'seed_studies':3,'seed_populations':2})
    print(json.dumps({'builders':3,'observed_sha256':digest(observed),'rows_generated':False}))

if __name__=='__main__': main()

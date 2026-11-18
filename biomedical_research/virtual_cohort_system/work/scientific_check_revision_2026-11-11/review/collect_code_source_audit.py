"""Collect only frozen code/source-declaration material after all24 closure.
No clinical references, final-table values or evaluation reports are opened.
"""
from pathlib import Path
import hashlib,json,difflib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def history(p):return {x.relative_to(p).as_posix():sha(x) for x in sorted(p.rglob('*')) if x.is_file() and x.relative_to(p).parts[0]!='evaluations'}
def main():
 c=read(R/'CONSTRUCTION_CLOSURE.json');plan=read(R/'PLAN.json')
 assert c['all_episodes_closed'] and len(c['episodes'])==24 and c['plan_sha256']==sha(R/'PLAN.json')
 assert {x['episode_id'] for x in c['episodes']}=={x['episode_id'] for x in plan['episodes']}
 rows=[];reading=[];seen=set()
 for ep in plan['episodes']:
  p=R/'episodes'/ep['episode_id'];closed=next(x for x in c['episodes'] if x['episode_id']==ep['episode_id'])
  assert history(p)==closed['files']
  initial=p/'candidates/v000';outcome=read(p/'OUTCOME.json');state=read(p/'TOOLS_STATE.json');selected=outcome.get('selected_candidate')
  final=p/'candidates'/selected if selected else None
  row={k:ep[k] for k in ['episode_id','pair_id','arm','case_id']}
  row.update(outcome_status=outcome['status'],selected_candidate=selected,initial={},final={},changed={},review_contracts=[],selected_reason=None)
  for name in ['generator.py','model_spec.json','notes.json']:
   row['initial'][name]=sha(initial/name)
   row['final'][name]=sha(final/name) if final else None
   row['changed'][name]=(row['initial'][name]!=row['final'][name]) if final else None
  if selected:row['selected_reason']=read(p/'FINAL_SELECTION.json')['reason']
  for meta in state.get('review_receipts',{}).values():
   rec=read(p/meta['path'])
   row['review_contracts'].append({'candidate_id':rec['candidate_id'],'path':meta['path'],'sha256':meta['sha256'],'contract':rec['review_contract'],'contract_validation':rec['result'].get('contract_validation'),'source_bindings':rec['result'].get('source_bindings')})
  for kind,cp in [('starting',initial),('selected',final)]:
   if cp is None:continue
   key=tuple(sha(cp/n) for n in ['generator.py','model_spec.json','notes.json'])
   if key in seen:continue
   seen.add(key)
   reading.append('\n\n========== '+ep['episode_id']+' '+kind+' '+str(cp)+' ==========\n')
   for name in ['generator.py','model_spec.json','notes.json']:
    reading.append('\nFILE '+name+'\n'+(cp/name).read_text(encoding='utf-8'))
  if final and any(row['changed'].values()):
   row['diffs']={n:''.join(difflib.unified_diff((initial/n).read_text(encoding='utf-8').splitlines(keepends=True),(final/n).read_text(encoding='utf-8').splitlines(keepends=True),fromfile='v000/'+n,tofile=selected+'/'+n)) for n,v in row['changed'].items() if v}
  rows.append(row)
 report={'created_utc':datetime.now(timezone.utc).isoformat(),'construction_closure_sha256':sha(R/'CONSTRUCTION_CLOSURE.json'),'plan_sha256':sha(R/'PLAN.json'),'target_comparisons_inspected':False,'final_generated_rows_read':False,'unique_artifact_bundles':len(seen),'rows':rows}
 with (R/'review/CODE_SOURCE_INVENTORY.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
 with (R/'review/CODE_SOURCE_READING.txt').open('x',encoding='utf-8') as f:f.write(''.join(reading))
 print(json.dumps({'episodes':len(rows),'unique_bundles':len(seen),'selected':sum(r['selected_candidate'] is not None for r in rows),'changed_code':sum(r['changed']['generator.py'] is True for r in rows),'changed_spec':sum(r['changed']['model_spec.json'] is True for r in rows)},ensure_ascii=False))
if __name__=='__main__':main()

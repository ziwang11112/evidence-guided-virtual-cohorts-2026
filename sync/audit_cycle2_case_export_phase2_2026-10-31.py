"""Verify the bounded phase-two export with file/metadata operations only."""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

MANIFEST='sync/CYCLE2_CASE_EXPORT_PHASE2_MANIFEST_2026-10-31.json'
AUDIT='sync/CYCLE2_CASE_EXPORT_PHASE2_AUDIT_2026-10-31.json'
CASE='biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31'
SECRETS={
 'github_token':r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})',
 'provider_key':r'\bsk-[A-Za-z0-9_-]{20,}',
 'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'aws_access_key':r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b',
}

def sha(raw): return hashlib.sha256(raw).hexdigest()

def safe(root,name):
 p=root/name
 if Path(name).is_absolute() or '..' in Path(name).parts or p.is_symlink() or not p.resolve().is_relative_to(root):
  raise ValueError('Unsafe path: '+name)
 return p

def json_privacy(value,path='$'):
 findings=[]
 if isinstance(value,dict):
  lower={str(k).lower():k for k in value}
  measured=set(lower)&{'age','female','bmi','fpg','hba1c','glucose','weight','height'}
  if len(measured)>=4 and all(not isinstance(value[lower[k]],dict) for k in measured):
   findings.append({'path':path,'rule':'possible_measurement_record_or_columns'})
  for k,v in value.items(): findings+=json_privacy(v,path+'.'+str(k))
 elif isinstance(value,list):
  if len(value)>80:
   valid_indices=(path=='$.reference_stability.valid_attempts' and len(value)==399 and all(type(v) is int and 0<=v<=399 for v in value) and len(set(value))==399)
   bindings=(path=='$.bindings' and all(isinstance(v,dict) and set(v)=={'path','sha256'} for v in value))
   if not(valid_indices or bindings): findings.append({'path':path,'rule':'unreviewed_large_array','length':len(value)})
  for i,v in enumerate(value): findings+=json_privacy(v,path+'['+str(i)+']')
 return findings

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--workspace',type=Path,required=True)
 parser.add_argument('--export',type=Path,default=Path(__file__).resolve().parents[1])
 parser.add_argument('--stage-output',type=Path)
 args=parser.parse_args()
 root=args.export.resolve(strict=True); workspace=args.workspace.resolve(strict=True)
 raw_manifest=safe(root,MANIFEST).read_bytes(); manifest=json.loads(raw_manifest)
 findings=[]; omitted=[]; bindings=0; json_count=0; python_count=0; links=0; csv_checks=[]
 def git(*a): return subprocess.check_output(['git',*a],cwd=root)
 def flag(rule,**details): findings.append({'rule':rule,**details})
 def read(name): return json.loads(safe(root,name).read_bytes())
 def binding(path,digest,label,required=True):
  nonlocal bindings
  if not path.resolve().is_relative_to(root):
   flag('binding_escape',binding=label);return
  relative=path.relative_to(root).as_posix()
  if relative not in selected:
   if required: flag('required_binding_not_selected',binding=label,path=relative)
   else: omitted.append({'binding':label,'path':relative,'sha256':digest})
   return
  bindings+=1
  if sha(path.read_bytes())!=digest: flag('internal_binding_mismatch',binding=label,path=relative)

 selected={r['destination'] for r in manifest['files']}|set(manifest['phase1_preserved_hashes'])
 expected=selected|{MANIFEST,AUDIT}
 actual=set(git('diff','--name-only',manifest['prior_head']).decode().splitlines())
 actual.update(git('ls-files','--others','--exclude-standard').decode().splitlines());actual.add(AUDIT)
 actual.update(name for name in manifest['approved_aggregate_figures'] if safe(root,name).is_file())
 if actual!=expected:flag('unexpected_delta',missing=sorted(expected-actual),unexpected=sorted(actual-expected))
 if git('rev-parse','HEAD').decode().strip()!=manifest['prior_head']:flag('head_changed')
 if expected!=set(manifest['combined_expected_delta']):flag('manifest_delta_inconsistent')
 for name,digest in manifest['phase1_preserved_hashes'].items():
  if sha(safe(root,name).read_bytes())!=digest:flag('phase1_bytes_changed',file=name)
 historical=0;historical_names=set();mutable={r['destination']:r for r in manifest['mutable_revisions']}
 for entry in git('ls-tree','-rz',manifest['prior_head']).split(b'\0'):
  if not entry:continue
  metadata,name_bytes=entry.split(b'\t',1);mode,kind,oid=metadata.decode().split();name=name_bytes.decode()
  historical_names.add(name)
  if kind!='blob':flag('historical_nonblob',file=name);continue
  path=safe(root,name)
  if os.name=='nt':path=Path('\\\\?\\'+str(path))
  raw=path.read_bytes()
  if name in mutable:
   prior=git('show',manifest['prior_head']+':'+name)
   if sha(prior)!=mutable[name]['prior_sha256'] or sha(raw)!=mutable[name]['export_sha256']:flag('mutable_revision_binding_mismatch',file=name)
   continue
  historical+=1
  if hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()!=oid:flag('historical_bytes_changed',file=name)
 if expected&historical_names!=set(mutable):flag('unauthorized_historical_path_overwrite',files=sorted((expected&historical_names)^set(mutable)))

 for item in manifest['files']:
  name=item['destination'];path=safe(root,name);raw=path.read_bytes()
  source=safe(workspace,item['source']).read_bytes()
  transformed=source
  for old,new in item.get('navigation_replacements',[]):transformed=transformed.replace(old.encode(),new.encode())
  if sha(raw)!=item['sha256'] or len(raw)!=item['bytes'] or sha(source)!=item['source_sha256'] or raw!=transformed:flag('source_export_binding_mismatch',file=name)
  if path.suffix not in {'.py','.md','.json','.csv','.png','.pdf'}:flag('unapproved_type',file=name)
  forbidden={'private','executions','__pycache__','raw','downloads'}
  if forbidden.intersection(Path(name).parts) or path.name.startswith('STATE') or path.name=='DOWNLOAD_LEDGER.json' or path.name.endswith('_cli.json') or path.suffix=='.log':flag('forbidden_payload_path',file=name)
  if 'history' in Path(name).parts and name not in {CASE+'/history/DATASET_USE_INDEX.md',CASE+'/history/DATASET_USE_INDEX.json'}:flag('unapproved_history_payload',file=name)
  if path.suffix in {'.png','.pdf'}:
   if name not in manifest['approved_aggregate_figures'] or (path.suffix=='.png' and not raw.startswith(b'\x89PNG\r\n\x1a\n')) or (path.suffix=='.pdf' and not raw.startswith(b'%PDF-')):flag('unapproved_or_invalid_aggregate_figure',file=name)
   continue
  text=raw.decode('utf-8-sig')
  for rule,pattern in SECRETS.items():
   if re.search(pattern,text):flag(rule,file=name)
  if re.search(r'[A-Za-z]:[\\/]+(?:Users|AIR-|Codex)|/(?:home|Users)/',text) and name not in manifest['preserved_machine_path_files']:flag('undocumented_machine_path',file=name)
  if path.suffix=='.json':
   json_count+=1
   for found in json_privacy(json.loads(text)):flag(found.pop('rule'),file=name,**found)
  elif path.suffix=='.py':python_count+=1;ast.parse(text)
  elif path.suffix=='.csv':
   contract=manifest['aggregate_csv_contracts'].get(name)
   if contract is None:flag('unapproved_csv',file=name);continue
   reader=csv.DictReader(io.StringIO(text));rows=list(reader)
   if reader.fieldnames!=contract['header'] or len(rows)!=contract['rows']:flag('aggregate_csv_contract_mismatch',file=name)
   if 'endpoint' in contract['header'] and {r['endpoint'] for r in rows}!=set(contract['endpoints']):flag('aggregate_endpoint_set_changed',file=name)
   if {'kind','builder','stage','seed'}<=set(contract['header']):
    slots={tuple(r[k] for k in ('kind','builder','stage','seed')) for r in rows}
    if len(slots)!=13 or len(contract['endpoints'])!=31:flag('aggregate_csv_slot_or_endpoint_count',file=name)
   if 'check_id' in contract['header'] and {tuple(r[k] for k in ('construction','context','check_id')) for r in rows}!=set(map(tuple,contract['check_keys'])):flag('aggregate_source_check_set_changed',file=name)
   csv_checks.append({'path':name,'rows':len(rows),'fields':reader.fieldnames})
  elif path.suffix=='.md':
   for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
    target=target.strip('<>')
    if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',target) or target.startswith('#'):continue
    target=unquote(target.split('#',1)[0])
    if target:
     links+=1;p=(path.parent/target).resolve()
     if not p.is_relative_to(root) or (not p.exists() and p!=root/AUDIT):flag('broken_local_link',file=name,target=target)
  if ('/sources/' in name) and (path.name!='source_summary.md' or len(raw)>2000):flag('unexpected_source_body',file=name)

 case=root/CASE
 for builder in ('b1','b2'):
  bundle=case/builder
  admission=json.loads((bundle/'INPUT_ADMISSION.json').read_bytes())
  for name,digest in admission['copied_file_sha256'].items():binding(bundle/name,digest,builder+':admission:'+name)
  binding(bundle/'registry.json',admission['registry_sha256'],builder+':input_registry')
  registry=json.loads((bundle/'registry.json').read_bytes())
  for stage in ('initial','final'):
   frozen=json.loads((bundle/'candidates'/stage/'freeze.json').read_bytes())
   if frozen['route']!='generator.py':flag('unexpected_candidate_route',builder=builder,stage=stage)
   for name,digest in frozen['commitments'].items():binding(bundle/name,digest,builder+':'+stage+':'+name)
   snapshot=frozen['registry_snapshot'];prefix=registry['artifacts'][:snapshot['artifact_count']]
   canonical=json.dumps(prefix,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
   if sha(canonical)!=snapshot['sha256']:flag('registry_snapshot_changed',builder=builder,stage=stage)
   if stage=='final':
    binding(bundle/frozen['parent']['receipt_path'],frozen['parent']['sha256'],builder+':final_parent')
    if frozen['revision']['kind']!='retain':flag('unexpected_nonretention',builder=builder)
    for name in ('generator.py','model_spec.json','evidence.json'):
     if (bundle/'candidates/initial'/name).read_bytes()!=(bundle/'candidates/final'/name).read_bytes():flag('retained_science_changed',builder=builder,file=name)
 for filename in ('PREPARATION_RELEASE.json','PREPARATION_RELEASE_v2.json','CONSTRUCTION_RELEASE.json','EVALUATION_RELEASE.json','custodian/PREPARATION_RECEIPT_v2.json','independent_analysis/POSTRUN_AUTHORIZATION.json'):
  doc=json.loads((case/filename).read_bytes())
  for key,item in doc.get('bindings',{}).items():
   if isinstance(item,dict) and {'path','sha256'}<=set(item):binding(case/item['path'],item['sha256'],filename+':'+key,required=False)
 for folder,filename in (('analysis/results','EVALUATION_COMPLETED.json'),('independent_analysis/postrun_results','COMPLETED.json')):
  completion=json.loads((case/folder/filename).read_bytes())
  for name,digest in completion['outputs'].items():binding(case/folder/name,digest,filename+':'+name)
  if 'release_sha256' in completion:binding(case/'EVALUATION_RELEASE.json',completion['release_sha256'],filename+':release')
 for builder,report in (('b1','s1i/report.json'),('b2','s2i/report.json')):
  original=(case/report).read_bytes();copy=(case/builder/'controller_feedback/initial/source_context_report.json').read_bytes()
  if original!=copy:flag('source_report_handoff_mismatch',builder=builder)
 aggregate=json.loads((case/'analysis/results/aggregate.json').read_bytes())
 comparison=json.loads((case/'independent_analysis/postrun_results/comparison.json').read_bytes())
 for label,doc in (('production',aggregate),('independent',comparison)):
  if (doc['scheduled_slots'],doc['unique_output_contents'],doc['unique_successful_execution_runs'],doc['failed_slots'])!=(12,6,6,0):flag('case_accounting_mismatch',report=label)
 if comparison['mismatch_count']!=0 or comparison['status']!='match':flag('independent_comparison_not_match')
 interpretation=json.loads((case/'review/CASE_INTERPRETATION.json').read_bytes())
 binding(case/'review/CASE_INTERPRETATION.md',interpretation['markdown_sha256'],'interpretation:markdown')
 report_manifest=json.loads((case/'results_report/REPORT_MANIFEST.json').read_bytes())
 for name,digest in report_manifest['inputs'].items():binding(case/name,digest,'report_input:'+name)
 for name,digest in report_manifest['outputs'].items():binding(case/'results_report'/name,digest,'report_output:'+name)
 for name,digest in manifest['root_approved_report_hashes'].items():binding(case/name,digest,'root_approved:'+name)
 output={'status':'PASS' if not findings else 'FAIL','scope':'Phase-two selected aggregate/code/provenance addition; file and metadata verification only.',
  'prior_head':manifest['prior_head'],'manifest_sha256':sha(raw_manifest),'phase2_source_project_files':manifest['source_project_file_count'],
  'phase2_bound_files':len(manifest['files']),'phase2_new_files':len(manifest['phase2_expected_delta'])-len(mutable),'combined_new_files':len(expected)-len(mutable),
  'phase1_files_byte_preserved':len(manifest['phase1_preserved_hashes']),'historical_tracked_blobs_byte_preserved':historical,
  'authorized_mutable_revisions':manifest['mutable_revisions'],'approved_aggregate_figures':manifest['approved_aggregate_figures'],
  'json_files_byte_preserved_and_scanned':json_count,'python_files_byte_preserved_and_syntax_parsed':python_count,
  'internal_hash_bindings_verified':bindings,'aggregate_csvs':csv_checks,'local_navigation_links_checked':links,
  'preserved_machine_path_files':manifest['preserved_machine_path_files'],'omitted_provenance_bindings_not_opened':omitted,
  'row_tables_or_residual_payloads_exported':False,'scientific_code_or_tests_run':False,'committed_or_pushed':False,'findings':findings}
 body=(json.dumps(output,indent=2)+'\n').encode();safe(root,AUDIT).write_bytes(body)
 if args.stage_output:args.stage_output.write_bytes(body)
 print(json.dumps({k:output[k] for k in ('status','phase2_new_files','combined_new_files','phase1_files_byte_preserved','historical_tracked_blobs_byte_preserved','internal_hash_bindings_verified','findings')},indent=2))
 raise SystemExit(bool(findings))

if __name__=='__main__':main()

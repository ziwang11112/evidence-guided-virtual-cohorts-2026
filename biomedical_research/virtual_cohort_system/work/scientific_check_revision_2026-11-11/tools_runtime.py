"""Versioned scientific-review tools over the pinned isolated generation runtime.

No clinical target values are loaded. Mathematical checks are heuristic and author
claims, physiology rules are declared hypotheses, and joint evidence remains
unidentified unless supported. Every generated program runs only in WSL/bubblewrap.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys

UNIT=Path(__file__).resolve().parent
BASE_PATH=UNIT.parent/'request_only_repeatability_2026-11-11/tools_runtime.py'
spec=importlib.util.spec_from_file_location('revision_pinned_tools_base',BASE_PATH)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
check,sha,raw,write_new,safe,now=base.check,base.sha,base.raw,base.write_new,base.safe,base.now
lifecycle=base.lifecycle
spec=importlib.util.spec_from_file_location('revision_law_checks',UNIT/'law_checks.py')
checks=importlib.util.module_from_spec(spec);sys.modules[spec.name]=checks;spec.loader.exec_module(checks)

TOOL_DEFINITIONS=[dict(t) for t in base.TOOL_DEFINITIONS]
TOOL_DEFINITIONS[0]=dict(TOOL_DEFINITIONS[0],description=TOOL_DEFINITIONS[0]['description'].replace('No prepared papers are supplied.','Original captured source papers are separately available from the imported package.'))
TOOL_DEFINITIONS.append(base._tool('inspect_law',
    'Inspect an immutable generator without target reference access. Without review_contract, returns only conservative AST mathematical warnings (not a proof). With review_contract, validates declared mathematical claims, bounded declarative physiological inequalities and requested-analysis dependencies; reuses the latest successful isolated trial or runs one trial if absent. Physiological rules and claims are authored by you, not certified by the checker. Empty/unresolved sections remain explicitly incomplete. Exact contract schema is available via review_schema.',
    {'candidate_id':{'type':'string'},'review_contract':{'type':'object'}},['candidate_id']))
TOOL_DEFINITIONS.append(base._tool('review_schema','Read the scientific-review contract schema and coverage requirements; no computation or source retrieval.',{},[]))
NAMES={x['name'] for x in TOOL_DEFINITIONS}

def _read(p):return lifecycle.read_json(p)
def _load_package(path):
    package=_read(path)
    check(package.get('schema_version')==1,'Unsupported imported package')
    for name,digest in package['files'].items():
        check(sha(safe(path.parent,name,True))==digest,'Imported artifact changed')
    return package

class ToolRuntime(base.ToolRuntime):
    def __init__(self,episode_dir,task,limits,*,gateway_factory=None,executor=None,
                 bootstrap_package=None,review_policy=None,analysis_ids=None,analysis_requirements=None):
        super().__init__(episode_dir,task,limits,gateway_factory=gateway_factory,executor=executor)
        if bootstrap_package is None:
            plan=_read(UNIT/'PLAN.json')
            ep=next((x for x in plan['episodes'] if x['episode_id']==self.root.name),None)
            check(ep is not None,'Unknown registered reviewer')
            bootstrap_package=safe(UNIT,ep['imported_package_path'],True)
            review_policy=ep['arm'];analysis_ids=ep['requested_analysis_ids'];analysis_requirements=ep['analysis_requirements']
        self.package_path=Path(bootstrap_package)
        self.package=_load_package(self.package_path)
        self.review_policy=review_policy
        check(review_policy in {'generic','structured'},'Invalid review policy')
        self.analysis_ids=list(analysis_ids or [])
        self.analysis_requirements=list(analysis_requirements or [])
        self.check_task=dict(self.task,requested_analysis_ids=self.analysis_ids,analysis_requirements=self.analysis_requirements)
        binding={'package_sha256':sha(self.package_path),'review_policy':review_policy,'requested_analysis_ids':self.analysis_ids,
                 'analysis_requirements':self.analysis_requirements}
        if 'import_binding' in self.state:
            check(self.state['import_binding']==binding,'Imported review input changed')
        else:
            check(not self.state['candidates'],'Import requires a clean episode')
            folder=safe(self.root,'candidates/v000');folder.mkdir(parents=True,exist_ok=False)
            for name in ['generator.py','model_spec.json','notes.json']:
                (folder/name).write_bytes((self.package_path.parent/name).read_bytes())
            manifest={'candidate_id':'v000','created_utc':now(),
                      'files':{name:sha(folder/name) for name in ['generator.py','model_spec.json','notes.json']},
                      'imported_original_manifest_sha256':self.package['candidate_manifest_sha256_original'],
                      'science_validated':False,'imported_frozen_candidate':True}
            write_new(folder/'manifest.json',manifest)
            self.state['candidates']['v000']={'path':'candidates/v000','manifest_sha256':sha(folder/'manifest.json')}
            self.state.update(import_binding=binding,review_receipts={},trial_history=[])
            self._save()
        self.imported_sources=self.package['sources']
        # Verify imported scientific artifacts even on resume.
        folder,_=self._candidate('v000')
        for name in ['generator.py','model_spec.json','notes.json']:
            check(sha(folder/name)==self.package['files'][name],'Imported candidate lost byte parity')

    @property
    def usage(self):
        value=super().usage
        value.update(candidates_submitted=sum(k!='v000' for k in self.state['candidates']),
                     imported_candidates=1,scientific_inspections=len(self.state.get('review_receipts',{})))
        return value

    def dispatch(self,name,args):
        if self.finalized:return {'status':'error','reason':'episode_finalized'}
        if self.state['actions']>=self.limits['max_actions']:return {'status':'error','reason':'action_budget_exhausted'}
        check(self.state.get('pending') is None,'Uncertain tool action requires inspection')
        self.state['actions']+=1;number=self.state['actions']
        action=safe(self.root,f'tool_actions/action_{number:04d}');action.mkdir(parents=True,exist_ok=False)
        write_new(action/'request.json',{'name':name,'arguments':args,'started_utc':now()})
        self.state['pending']={'ordinal':number,'name':name};self._save()
        try:
            check(name in NAMES and isinstance(args,dict),'Unknown tool or invalid arguments')
            definition=next(x for x in TOOL_DEFINITIONS if x['name']==name)['parameters']
            check(set(args)<=set(definition['properties']) and set(definition['required'])<=set(args),'Unexpected/missing tool arguments')
            result=getattr(self,'_'+name)(**args)
        except base.gateway.GatewayError as error:
            result={'status':'rejected' if error.reason.startswith('excluded_') else 'error','reason':error.reason}
        except (ValueError,TypeError) as error:
            result={'status':'error','reason':type(error).__name__,'detail':str(error)[:1500]}
        result['usage']=self.usage
        write_new(action/'result.json',result)
        self.state['pending']=None;self._save()
        return result

    def _review_schema(self):
        return {'status':'ok','schema':checks.REVIEW_CONTRACT_SCHEMA,
                'requested_analysis_ids':self.analysis_ids,'analysis_requirements':self.analysis_requirements,
                'limits':'Declarative checks only; no arbitrary expressions or code execution. Registered sources establish availability, not extraction correctness or transport.'}

    def _read_source(self,source_id,version=None,section='full',query=None,cursor=0):
        check(isinstance(source_id,str),'Invalid source ID')
        check(version is None or (type(version) is int and version>=1),'Invalid source version')
        if source_id not in self.imported_sources or (version is not None and version!=self.imported_sources[source_id]['version']):
            return super()._read_source(source_id,version,section,query,cursor)
        check(isinstance(section,str) and (query is None or isinstance(query,str)),'Invalid section/query')
        meta=self.imported_sources[source_id]
        path=safe(self.package_path.parent,meta['path'],True)
        check(sha(path)==meta['sha256'],'Frozen imported XML changed')
        root,fulltext=base.gateway.parse_xml(path.read_bytes(),base.gateway.Screen(self.gateway_config))
        sections={'full':fulltext};index=[];counts={}
        for element in root.iter():
            kind=base.gateway.local_tag(element.tag)
            if kind not in {'sec','table-wrap','abstract'}:continue
            counts[kind]=counts.get(kind,0)+1;sid=f'{kind}_{counts[kind]:03d}'
            title=' '.join(''.join(c.itertext()).strip() for c in element if base.gateway.local_tag(c.tag) in {'title','label','caption'})
            text='\n'.join(t.strip() for t in element.itertext() if t.strip())
            sections[sid]=text;index.append({'section_id':sid,'kind':kind,'title':title,'chars':len(text),'xml_id':element.get('id')})
        if section=='index':content=raw(index).decode('utf-8')
        else:
            check(section in sections,'Unknown section; use section=index')
            content=sections[section]
        info={'source_id':source_id,'section':section,'source_version':meta['version'],
              'xml_sha256':meta['sha256'],'canonical_url':meta['canonical_url'],
              'imported_frozen_source':True,'network_used':False}
        if query is not None:return self._literal_page(content,query,cursor,**info)
        return self._page(content,cursor,**info)

    def _list_sources(self,cursor=0):
        return self._page(raw({'imported_articles':self.imported_sources,
                              'new_articles':self.state['sources'],'new_searches':self.state['searches']}).decode('utf-8'),cursor)

    def _submit_candidate(self,generator_py,model_spec,notes='',provenance=None):
        submitted=sum(k!='v000' for k in self.state['candidates'])
        check(submitted<self.limits['max_candidates'],'candidate_budget_exhausted')
        check(isinstance(generator_py,str) and 0<len(generator_py.encode('utf-8'))<=200000,'Invalid/oversized generator')
        check(isinstance(model_spec,dict) and len(raw(model_spec))<=200000,'Invalid/oversized model specification')
        check(isinstance(notes,str) and len(notes)<=30000 and len(raw(provenance))<=100000,'Invalid/oversized notes')
        identifier=f'v{submitted+1:03d}';folder=safe(self.root,'candidates/'+identifier);folder.mkdir(parents=True,exist_ok=False)
        (folder/'generator.py').write_text(generator_py,encoding='utf-8',newline='\n')
        write_new(folder/'model_spec.json',model_spec);write_new(folder/'notes.json',{'notes':notes,'provenance':provenance})
        validation={'status':'valid'}
        try:lifecycle.validate_program(folder/'generator.py')
        except Exception as error:validation={'status':'invalid','reason':str(error)[:1500]}
        manifest={'candidate_id':identifier,'created_utc':now(),'files':{p.name:sha(p) for p in folder.iterdir()},
                  'mechanical_validation':validation,'science_validated':False}
        write_new(folder/'manifest.json',manifest)
        self.state['candidates'][identifier]={'path':'candidates/'+identifier,'manifest_sha256':sha(folder/'manifest.json')};self._save()
        return {'status':'stored','candidate_id':identifier,'mechanical_validation':validation,
                'manifest_sha256':sha(folder/'manifest.json'),'executed':False,'scientific_validity':'not_assessed'}

    def _run_candidate(self,candidate_id):
        result=super()._run_candidate(candidate_id)
        run=safe(self.root,f'executions/trial_{self.state["runs"]:03d}')
        self.state.setdefault('trial_history',[]).append({'candidate_id':candidate_id,
             'run_path':run.relative_to(self.root).as_posix(),'status':result.get('status'),
             'execution_receipt_sha256':sha(run/'execution.json') if (run/'execution.json').exists() else None,
             'input_bindings_sha256':sha(run/'input_bindings.json') if (run/'input_bindings.json').exists() else None})
        self._save();return result

    def _source_bindings(self,contract):
        ids=set()
        for item in contract.get('mathematical_review',[])+contract.get('physiological_rules',[]):ids.update(item.get('source_ids',[]))
        for analysis in contract.get('joint_analyses',[]):
            for dependency in analysis.get('dependencies',[]):ids.update(dependency.get('source_ids',[]))
        result={}
        for sid in sorted(ids):
            versions=[]
            for origin,registry in [('imported',self.imported_sources),('newly_retrieved',self.state['sources'])]:
                if sid in registry:
                    entry=registry[sid]
                    versions.append({'origin':origin,'version':entry.get('version'),
                                     'xml_sha256':entry.get('xml_sha256',entry.get('sha256'))})
            distinct={(v['version'],v['xml_sha256']) for v in versions}
            result[sid]=({'status':'registered_availability_only_not_evidence_validation',
                'registered_versions':versions,'version_ambiguous':len(distinct)>1,
                'selected_evidence_version':None,
                'interpretation':'Availability only. Source-ID declarations do not uniquely bind an adopted version; inspect actual read records and scientific notes.'}
                if versions else {'status':'unavailable_unregistered_source'})
        return result

    def _inspect_law(self,candidate_id,review_contract=None):
        folder,manifest=self._candidate(candidate_id)
        static=checks.inspect_program((folder/'generator.py').read_text(encoding='utf-8'))
        result={'status':'static_only' if review_contract is None else 'reviewed','candidate_id':candidate_id,
                'candidate_manifest_sha256':sha(folder/'manifest.json'),'program_review':static,
                'target_reference_read':False,'science_certified':False}
        if review_contract is None:return result
        validation=checks.validate_contract(review_contract,self.check_task)
        result['contract_validation']=validation
        if not validation.get('valid'):
            result['status']='invalid_contract';return result
        result['source_bindings']=self._source_bindings(review_contract)
        trials=[r for r in self.state.get('trial_history',[]) if r['candidate_id']==candidate_id and r['status']=='success']
        if not trials and self.state['runs']<self.limits['max_runs']:
            result['trial_attempt']=self._run_candidate(candidate_id)
            trials=[r for r in self.state.get('trial_history',[]) if r['candidate_id']==candidate_id and r['status']=='success']
        if trials:
            trial=trials[-1];run=safe(self.root,trial['run_path'])
            check(sha(run/'execution.json')==trial['execution_receipt_sha256'],'Inspection execution receipt changed')
            check(trial.get('input_bindings_sha256') is not None and sha(run/'input_bindings.json')==trial['input_bindings_sha256'],'Inspection staged-input bindings changed or unavailable')
            staged=_read(run/'input_bindings.json')
            check(staged=={p.name:sha(p) for p in (run/'input').iterdir() if p.is_file()},'Inspection staged input changed')
            for name in ['generator.py','model_spec.json']:
                check(staged.get(name)==sha(folder/name),'Inspection trial came from another scientific candidate')
            check(_read(run/'input/task.json')==self.task,'Inspection trial task mismatch')
            check(_read(run/'input/request.json').get('seed')==self.limits['diagnostic_seed'],'Inspection trial seed mismatch')
            receipt=_read(run/'execution.json');csv=run/'output/generated.csv'
            check(receipt['status']=='success' and sha(csv)==receipt['generated_sha256'],'Inspection row binding changed')
            check(receipt['candidate_id']==candidate_id and receipt['seed']==self.limits['diagnostic_seed'],'Inspection candidate/seed mismatch')
            frame=lifecycle.read_table(csv,self.task,output=True)
            result['trial_review']=checks.inspect_trial(frame,review_contract,self.check_task)
            result['generated_only_statistics']=receipt.get('statistics')
            result['generated_sha256']=sha(csv);result['execution_receipt_sha256']=sha(run/'execution.json')
            result['input_bindings_sha256']=sha(run/'input_bindings.json')
        else:
            result['trial_review']={'status':'unavailable','reason':'No successful isolated trial within budget',
                 'mathematical_review':{'status':'author_claims_not_certified'},
                 'physiology':{'status':'unavailable'},'joint_relations':{'status':'declarations_only_not_target_validated'}}
        ordinal=len(self.state.setdefault('review_receipts',{}))+1
        path=f'scientific_reviews/review_{ordinal:03d}.json'
        receipt={'created_utc':now(),'candidate_id':candidate_id,'review_contract':review_contract,'result':result}
        write_new(safe(self.root,path),receipt)
        self.state['review_receipts'][str(ordinal)]={'path':path,'sha256':sha(safe(self.root,path,True)),
               'candidate_id':candidate_id,'candidate_manifest_sha256':result['candidate_manifest_sha256'],'valid_contract':True,
               'complete_declarations':not validation['coverage'].get('mathematical_variables_not_declared')
                  and not validation['coverage'].get('analyses_without_dependencies')
                  and validation['coverage'].get('analysis_coverage')=='complete_declarations_only'}
        self._save();result['review_receipt_sha256']=sha(safe(self.root,path,True))
        return result

    def _finalize(self,candidate_id=None,reason='',unable_reason=None):
        check(isinstance(reason,str) and len(reason)<=10000,'Invalid final reason')
        check((candidate_id is not None)!=(unable_reason is not None),'Select a candidate or explicit inability')
        receipts=[]
        if candidate_id is not None:
            folder,_=self._candidate(candidate_id)
            receipts=[r for r in self.state.get('review_receipts',{}).values() if r['candidate_id']==candidate_id and r['valid_contract']]
            for r in receipts:
                check(sha(safe(self.root,r['path'],True))==r['sha256'],'Review receipt changed')
                check(r['candidate_manifest_sha256']==sha(folder/'manifest.json'),'Review candidate changed')
            if self.review_policy=='structured':check(any(r.get('complete_declarations') for r in receipts),'Structured policy requires an inspect_law receipt covering every requested analysis and numerical generated variable for the selected candidate; explicit unresolved claims and no applicable physiology rules with rationale are allowed')
        else:check(isinstance(unable_reason,str) and 0<len(unable_reason)<=10000,'Invalid unable reason')
        self.state.update(finalized=True,selected_candidate=candidate_id,unable_reason=unable_reason)
        write_new(safe(self.root,'FINAL_SELECTION.json'),{'candidate_id':candidate_id,'reason':reason,'unable_reason':unable_reason,
             'candidate_manifest_sha256':self.state['candidates'][candidate_id]['manifest_sha256'] if candidate_id else None,
             'scientific_review_receipts':receipts,'review_policy':self.review_policy,'created_utc':now(),
             'review_completion_not_scientific_certification':True})
        self._save();return {'status':'finalized','selected_candidate':candidate_id,'unable_reason':unable_reason}

    def _approval(self):
        check(self.root.is_relative_to(UNIT),'Live episode must be in new revision unit')
        approval=_read(safe(UNIT,'ROOT_EXECUTION_APPROVAL.json',True))
        check(approval.get('status')=='approved' and self.root.name in approval.get('episodes',[]),'Episode execution not approved')
        files=approval.get('files',{})
        check(files.get('tools_runtime.py')==sha(Path(__file__)),'Unapproved review runtime')
        for name,digest in files.items():check(sha(safe(UNIT,name,True))==digest,'Approved input changed')
        task_hash=hashlib.sha256(raw(self.task)).hexdigest()
        check(any(name.startswith('tasks/') and name.endswith('.json') and hashlib.sha256(raw(_read(safe(UNIT,name,True)))).hexdigest()==task_hash for name in files),'Task lacks approval')

    def generate_for_evaluation(self,candidate_id,seed,run_id):
        check(self.finalized and self.selected_candidate==candidate_id,'Only explicitly selected candidate can be evaluated')
        check(type(seed) is int and seed!=self.limits['diagnostic_seed'],'Fresh evaluation seed required')
        base.execution._name(run_id)
        closure=_read(safe(UNIT,'CONSTRUCTION_CLOSURE.json',True));plan=_read(safe(UNIT,'PLAN.json',True))
        expected={r['episode_id'] for r in plan['episodes']};rows=closure.get('episodes',[])
        check(len(rows)==24 and {r['episode_id'] for r in rows}==expected,'All 24 review episodes must close before evaluation')
        check(seed in plan['evaluation_seeds'],'Unplanned evaluation seed')
        folder,_=self._candidate(candidate_id)
        check(any(r.get('episode_id')==self.root.name and r.get('candidate_id')==candidate_id and r.get('candidate_manifest_sha256')==sha(folder/'manifest.json') for r in rows),'Global closure candidate mismatch')
        return self._execute(folder,safe(self.root,'evaluations/'+run_id),seed)

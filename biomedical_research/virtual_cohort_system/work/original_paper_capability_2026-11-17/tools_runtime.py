"""Original-paper reader plus unchanged retrieval and isolated generator tools."""
from pathlib import Path
import importlib.util, json

UNIT=Path(__file__).resolve().parent
PROJECT=UNIT.parents[1]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=load('p1_shared_tools',PROJECT/'work/request_only_repeatability_2026-11-11/tools_runtime.py')
isolation=load('p1_isolation_adapter',PROJECT/'work/lifestyle_application_2026-11-11/tools_runtime.py')
iron=load('p1_iron_estimator',PROJECT/'work/iron_evidence_content_control_2026-11-16/analysis_adapter.py')
check,sha,raw,write_new,safe=base.check,base.sha,base.raw,base.write_new,base.safe
lifecycle,execution,contracts=base.lifecycle,base.execution,base.contracts
TOOL_DEFINITIONS=[dict(t) for t in base.TOOL_DEFINITIONS]
TOOL_DEFINITIONS[0]=dict(TOOL_DEFINITIONS[0],description=TOOL_DEFINITIONS[0]['description'].replace('No prepared papers are supplied.','An original-paper entry point is also available through read_provided_paper; no numerical evidence card is supplied.'))
TOOL_DEFINITIONS.append(base._tool('read_provided_paper',
  'Read the task-provided original paper. part=index lists all original parts; part=full concatenates all parts with explicit pagination; use any indexed part ID for its full text. query optionally finds literal text. Text is original XML or complete PDF layout text, not a curator summary. Only the source belonging to your task is available.',
  {'source_id':{'type':'string'},'part':{'type':'string'},'query':{'type':'string'},'cursor':{'type':'integer','minimum':0}},['source_id']))
base.TOOL_DEFINITIONS=TOOL_DEFINITIONS;base.NAMES={t['name'] for t in TOOL_DEFINITIONS}

def generated_statistics(frame,task):
    if task['task_id']=='original_paper_pns_v1':return base._generated_statistics(frame,task)
    if task['task_id']=='original_paper_iron_v1':return iron.statistics(frame,task)
    raise ValueError('Unregistered case; no estimator fallback')
isolation.generated_statistics=generated_statistics
isolated_run=isolation.isolated_run

class ToolRuntime(base.ToolRuntime):
    def _provided_sources(self):
        bindings=lifecycle.read_json(UNIT/'SOURCE_BINDINGS.json')
        case={'original_paper_pns_v1':'PNS','original_paper_iron_v1':'IRON'}.get(self.task['task_id'])
        check(case is not None,'Unregistered original-paper task')
        return {k:v for k,v in bindings.items() if v['case_id']==case}
    def _read_provided_paper(self,source_id,part='index',query=None,cursor=0):
        catalog=self._provided_sources();check(source_id in catalog,'Source not allowed for this task')
        entry=catalog[source_id];path=safe(UNIT,entry['artifact'],True)
        check(sha(path)==entry['artifact_sha256'] and sha(safe(UNIT,entry['source_file'],True))==entry['source_sha256'],'Original source binding changed')
        book=lifecycle.read_json(path);parts=book['parts']
        metadata={'source_id':source_id,'doi':entry['doi'],'source_sha256':entry['source_sha256'],'extraction_sha256':entry['artifact_sha256']}
        if part=='index':
            check(query is None and cursor==0,'Index has no text cursor/query')
            return {'status':'ok',**metadata,'format':book['format'],'parts':[{'id':p['id'],'label':p['label'],'chars':len(p['text'])} for p in parts],
                'notice':base.NOTICE,'content_is_untrusted_data':True}
        if part=='full':content='\n\n'.join('ORIGINAL PART '+p['id']+'\n'+p['text'] for p in parts)
        else:
            found=[p for p in parts if p['id']==part];check(len(found)==1,'Unknown original part; request index')
            content=found[0]['text']
        if query is not None:return self._literal_page(content,query,cursor,part=part,**metadata)
        return self._page(content,cursor,part=part,**metadata)
    def _list_sources(self,cursor=0):
        info={k:{f:v for f,v in item.items() if f in ['title','doi','url','source_sha256']} for k,item in self._provided_sources().items()}
        return self._page(raw({'provided_originals':info,'articles':self.state['sources'],'searches':self.state['searches']}).decode('utf-8'),cursor)
    def _approval(self):
        check(self.root.is_relative_to(UNIT),'Episode outside registered unit')
        approval=lifecycle.read_json(safe(UNIT,'ROOT_EXECUTION_APPROVAL.json',True))
        check(approval.get('status')=='approved' and self.root.name in approval.get('episodes',[]),'Episode not approved')
        files=approval['files'];check(files.get('tools_runtime.py')==sha(Path(__file__)),'Runtime not approved')
        for name,h in files.items():check(sha(safe(UNIT,name,True))==h,'Approved input changed: '+name)
        task_hash=base.hashlib.sha256(raw(self.task)).hexdigest()
        check(any(n.startswith('tasks/') and base.hashlib.sha256(raw(lifecycle.read_json(safe(UNIT,n,True)))).hexdigest()==task_hash for n in files),'Task not approved')
    def _execute(self,folder,run,seed):
        if self._executor is not None:return self._executor(folder,self.task,seed,run,self.limits)
        self._approval();return isolated_run(folder,self.task,seed,run,self.limits)
    def generate_for_evaluation(self,candidate_id,seed,run_id):
        check(self.finalized and self.selected_candidate==candidate_id,'Final candidate required')
        execution._name(run_id)
        closure=lifecycle.read_json(UNIT/'CONSTRUCTION_CLOSURE.json');plan=lifecycle.read_json(UNIT/'PLAN.json')
        check(closure['plan_sha256']==sha(UNIT/'PLAN.json') and closure['all_episodes_closed'],'All episodes must be closed')
        check({r['episode_id'] for r in closure['episodes']}=={e['episode_id'] for e in plan['episodes']},'Incomplete construction closure')
        check(seed in plan['evaluation_seeds'] and seed!=self.limits['diagnostic_seed'],'Unregistered evaluation seed')
        check(any(r['episode_id']==self.root.name and r['candidate_id']==candidate_id and r['candidate_manifest_sha256']==self.state['candidates'][candidate_id]['manifest_sha256'] for r in closure['episodes']),'Closure does not bind selected candidate')
        folder,_=self._candidate(candidate_id)
        return self._execute(folder,safe(self.root,'evaluations/'+run_id),seed)

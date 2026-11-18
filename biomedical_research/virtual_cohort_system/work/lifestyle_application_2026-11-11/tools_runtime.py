"""Lifestyle-task tools over the existing retrieval and isolated worker runtime.

The diagnostic operator is unit-local and explicit: no old PNS/lipid fallback.
No biological structure or numerical scientific parameter is specified here.
"""
from pathlib import Path
import importlib.util

UNIT=Path(__file__).resolve().parent
BASE_PATH=UNIT.parent/'request_only_repeatability_2026-11-11/tools_runtime.py'
spec=importlib.util.spec_from_file_location('lifestyle_tools_base',BASE_PATH)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
check,sha,raw,write_new,safe,now=base.check,base.sha,base.raw,base.write_new,base.safe,base.now
lifecycle,execution,contracts,PROJECT=base.lifecycle,base.execution,base.contracts,base.PROJECT
TOOL_DEFINITIONS=[dict(t) for t in base.TOOL_DEFINITIONS]
TOOL_DEFINITIONS[0]=dict(TOOL_DEFINITIONS[0],description=TOOL_DEFINITIONS[0]['description'].replace('No prepared papers are supplied.','The task also supplies approved source-study evidence; you may retrieve additional studies.'))
NAMES={t['name'] for t in TOOL_DEFINITIONS}

def generated_statistics(frame,task):
    path=UNIT/'analysis_operator.py'
    spec=importlib.util.spec_from_file_location('lifestyle_generated_analysis',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    fn=getattr(module,'generated_diagnostics',None)
    check(callable(fn),'Explicit lifestyle generated_diagnostics entrypoint missing; no legacy fallback')
    result=fn(frame,task)
    check(isinstance(result,dict),'Generated diagnostics must be a JSON object')
    check(result.get('target_reference_read') is False,'Diagnostics must explicitly state no target read')
    raw(result)
    return result

class ToolRuntime(base.ToolRuntime):
    def _approval(self):
        check(self.root.is_relative_to(UNIT),'Episode must be inside this unit')
        approval=lifecycle.read_json(safe(UNIT,'ROOT_EXECUTION_APPROVAL.json',True))
        check(approval.get('status')=='approved' and self.root.name in approval.get('episodes',[]),'Episode not approved')
        files=approval.get('files',{})
        check(files.get('tools_runtime.py')==sha(Path(__file__)),'Current runtime not approved')
        check('analysis_operator.py' in files,'Current analysis operator must be approved')
        for name,h in files.items():check(sha(safe(UNIT,name,True))==h,'Approved input changed')
        task_hash=base.hashlib.sha256(raw(self.task)).hexdigest()
        check(any(name.startswith('tasks/') and name.endswith('.json') and base.hashlib.sha256(raw(lifecycle.read_json(safe(UNIT,name,True)))).hexdigest()==task_hash for name in files),'Task not approved')
    def _execute(self,folder,run,seed):
        if self._executor is not None:return self._executor(folder,self.task,seed,run,self.limits)
        self._approval()
        return isolated_run(folder,self.task,seed,run,self.limits)
    def generate_for_evaluation(self,candidate_id,seed,run_id):
        check(self.finalized and self.selected_candidate==candidate_id,'Final selected candidate required')
        check(type(seed) is int and seed!=self.limits['diagnostic_seed'],'Fresh evaluation seed required')
        execution._name(run_id)
        closure=lifecycle.read_json(safe(UNIT,'CONSTRUCTION_CLOSURE.json',True))
        plan=lifecycle.read_json(safe(UNIT,'PLAN.json',True))
        check(closure.get('plan_sha256')==sha(UNIT/'PLAN.json'),'Construction closure binds another plan')
        planned={ep['episode_id'] for ep in plan['episodes']}
        rows=closure.get('episodes',[])
        check(closure.get('all_episodes_closed') is True and len(rows)==len(planned) and {r.get('episode_id') for r in rows}==planned,'All authors must close before evaluation')
        check(seed in plan['evaluation_seeds'],'Unregistered evaluation seed')
        expected={'episode_id':self.root.name,'candidate_id':candidate_id,'candidate_manifest_sha256':self.state['candidates'][candidate_id]['manifest_sha256']}
        check(any(all(r.get(k)==v for k,v in expected.items()) for r in rows),'Candidate not bound by closure')
        folder,_=self._candidate(candidate_id)
        return self._execute(folder,safe(self.root,'evaluations/'+run_id),seed)

def isolated_run(candidate,task,seed,run,limits):
    """Same staging/isolation as the pinned base, with only diagnostic dispatch replaced."""
    run.mkdir(parents=True,exist_ok=False)
    requested=execution._limits(**{k:limits[k] for k in ['timeout_seconds','memory_mb','output_bytes','log_bytes']},seed=seed)
    receipt={'created_utc':now(),'candidate_id':candidate.name,'seed':seed,'status':'failed',
        'target_reference_read':False,'generator_executed':False,'isolation':'WSL/bubblewrap only; no fallback','limits':requested}
    write_new(run/'ATTEMPT.json',receipt)
    bindings=None
    try:
        lifecycle.validate_program(candidate/'generator.py')
        stage=run/'input';output=run/'output';stage.mkdir();output.mkdir()
        for name,source in {'generator.py':candidate/'generator.py','model_spec.json':candidate/'model_spec.json',
                            'worker.py':PROJECT/'cohort_harness/_worker.py'}.items():
            (stage/name).write_bytes(source.read_bytes())
        write_new(stage/'task.json',task);write_new(stage/'request.json',requested)
        bindings={p.name:sha(p) for p in stage.iterdir()};write_new(run/'input_bindings.json',bindings)
        runtime=execution._runtime(None);write_new(run/'runtime_manifest.json',execution._runtime_manifest(runtime))
        for name in ['generated.csv','worker_report.json']:(output/name).touch(exist_ok=False)
        command=execution._command(runtime,run,limits['timeout_seconds'])
        write_new(run/'launch.json',{'command':command,'source_staged':False,'reference_staged':False,'runtime':runtime})
        process=execution._capture(command,run,limits['timeout_seconds']+20,limits['log_bytes'],run/'stdout.log',run/'stderr.log')
        receipt['process']=process
        report=output/'worker_report.json';check(report.stat().st_size<=65536,'Oversized worker report')
        worker=lifecycle.read_json(report) if report.stat().st_size else {}
        receipt['generator_executed']=worker.get('generator_started',False)
        receipt['worker_report']=worker
        check(process['returncode']==0 and worker.get('status')=='completed','Worker did not complete')
        execution._csv_guard(output/'generated.csv',task,limits['output_bytes'])
        frame=lifecycle.read_table(output/'generated.csv',task,output=True)
        contracts.validate_output(None,frame,task)
        receipt['statistics']=generated_statistics(frame,task)
        receipt.update(status='success',generated_sha256=sha(output/'generated.csv'))
    except Exception as error:
        receipt['error']={'type':type(error).__name__,'message':str(error)[:1500]}
    finally:
        if bindings is not None:
            if {p.name:sha(p) for p in (run/'input').iterdir()}!=bindings:
                receipt.update(status='failed',error={'type':'InputIntegrityError','message':'Staged immutable inputs changed'})
        receipt['completed_utc']=now();write_new(run/'execution.json',receipt)
    return {'status':receipt['status'],'candidate_id':candidate.name,'seed':seed,
        'statistics':receipt.get('statistics'),'error':receipt.get('error'),
        'worker_error':{k:receipt.get('worker_report',{}).get(k) for k in ['error_type','error']},
        'execution_receipt_sha256':sha(run/'execution.json'),'target_reference_read':False,
        'untrusted_execution_messages':True,'notice':base.NOTICE}

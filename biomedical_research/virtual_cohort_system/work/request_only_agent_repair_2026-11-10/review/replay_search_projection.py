"""Offline exhaustive formatter replay over approved caches of the completed pilot.

Reads old approved search caches and their captured tool output, without mutation.
Imports only the new trusted formatter/runtime. No constructor, dispatch, gateway
session, author program, API, credentials, clinical data or reference is invoked.
The report contains counts, hashes and bytes; no papers/abstracts enter new episodes.
"""
from __future__ import annotations

import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics
import sys

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
UNIT=OUT.parent
PROJECT=UNIT.parents[1]
OLD=UNIT.parent/'request_only_agent_pilot_2026-11-10'
NETWORK_ATTEMPTS=[]


def guard(event,args):
    if event in {'socket.connect','socket.getaddrinfo','socket.bind'}:
        NETWORK_ATTEMPTS.append(event)
        raise AssertionError('Network is forbidden during offline replay')


sys.addaudithook(guard)


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def wire(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
def digest(value):return hashlib.sha256(value).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False,indent=2).encode('utf-8')
def relative(path):return Path(path).relative_to(PROJECT).as_posix()
def require(ok,message):
    if not ok:raise AssertionError(message)
def forbidden(*args,**kwargs):raise AssertionError('Session, state mutation, constructor dispatch and execution are forbidden in replay')


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pages(engine,source_id,section,expected,*,missing=False):
    """Reconstruct exact character slices and require a strictly advancing cursor."""
    cursor=0;parts=[];records=[]
    while True:
        result=engine._read_source(source_id,section=section,cursor=cursor)
        if missing:
            require(result['status']=='unavailable','Missing abstract must remain unavailable')
            require(result.get('reason')=='abstract_not_in_approved_record','Missing abstract reason changed')
            return {'pages':1,'payload_bytes':[len(wire(result))],'available':False}
        require(result['status']=='ok','Local read unexpectedly failed')
        require(result['cursor']==cursor,'Local cursor mismatch')
        require(isinstance(result.get('content'),str),'Local read has no text slice')
        chunk=result['content']
        require(chunk==expected[cursor:cursor+len(chunk)],'Content differs from approved record')
        parts.append(chunk);records.append(len(wire(result)))
        nxt=result['next_cursor']
        if nxt is None:
            require(result['complete'] is True,'Final local page incomplete')
            break
        require(type(nxt) is int and nxt==cursor+len(chunk) and nxt>cursor,'Nonadvancing/incorrect local cursor')
        cursor=nxt
    require(''.join(parts)==expected,'Lossless local reconstruction failed')
    return {'pages':len(parts),'payload_bytes':records,'available':True,'text_sha256':digest(expected.encode('utf-8'))}


def initial_outputs(episode):
    result={}
    for path in sorted((episode/'tool_actions').glob('*/request.json')):
        request=read(path)
        if request['name']!='literature_search':continue
        rp=path.with_name('result.json')
        if not rp.exists():continue
        output=read(rp)
        sid=output.get('source_id')
        if sid:
            require(sid not in result,'Duplicate initial literature-search source ID')
            result[sid]=(output,rp)
    return result


def title_count(output,accepted):
    titles=[]
    for match in re.finditer(r'"title"\s*:\s*("(?:[^"\\]|\\.)*")',output.get('content','')):
        try:titles.append(json.loads(match.group(1)))
        except ValueError:pass
    return sum(item.get('title') in titles for item in accepted if isinstance(item.get('title'),str))


def static_spec_chain():
    runtime_path=UNIT/'tools_runtime.py';runtime_text=runtime_path.read_text(encoding='utf-8')
    tree=ast.parse(runtime_text)
    method=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_submit_candidate')
    writes=[n for n in ast.walk(method) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='write_new'
            and n.args and 'model_spec.json' in ast.unparse(n.args[0])]
    require(len(writes)==1 and len(writes[0].args)==2 and isinstance(writes[0].args[1],ast.Name)
            and writes[0].args[1].id=='model_spec','Author specification is wrapped or remapped before storage')
    worker_path=PROJECT/'cohort_harness/_worker.py';worker_text=worker_path.read_text(encoding='utf-8')
    worker=ast.parse(worker_text)
    calls=[n for n in ast.walk(worker) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='generate']
    require(len(calls)==1 and isinstance(calls[0].args[1],ast.Name) and calls[0].args[1].id=='specification','Worker remaps specification')
    assignment=next(n for n in ast.walk(worker) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='specification' for t in n.targets))
    require('model_spec.json' in ast.unparse(assignment.value),'Worker specification source changed')
    require("'model_spec.json':candidate/'model_spec.json'" in runtime_text,'Staging model_spec source changed')
    require('(stage/name).write_bytes(source.read_bytes())' in runtime_text,'Byte-for-byte input staging changed')
    evaluator=UNIT/'evaluate_pilot.py';text=evaluator.read_text(encoding='utf-8')
    require('engine.generate_for_evaluation(' in text,'Evaluator bypasses runtime generation entry')
    require("bindings[name]==sha(episode_folder/'candidates'/candidate/name)" in text,'Evaluator lacks candidate-input binding check')
    return {'status':'pass','method':'Static AST/text inspection only; no generator or synthetic ABI fixture executed',
      'author_specification_storage':'Exactly submitted model_spec JSON value, without a task/model envelope',
      'staging':'model_spec.json copied byte-for-byte; separate task.json controls schema/whole_cohort observed=None',
      'worker_call':'generate(observed, specification, seed), with specification=json.loads(model_spec.json)',
      'evaluation':'Same runtime entry and candidate-to-staged model_spec SHA binding; no root-key remapping',
      'locators':[relative(runtime_path)+':'+str(writes[0].lineno),relative(worker_path)+':'+str(assignment.lineno),relative(worker_path)+':'+str(calls[0].lineno),relative(evaluator)],
      'files':{relative(p):sha(p) for p in [runtime_path,worker_path,evaluator]}}


def main():
    runtime_path=UNIT/'tools_runtime.py';runtime_hash=sha(runtime_path)
    module=load(runtime_path,'repair_projection_replay_runtime')
    plan=read(UNIT/'PLAN.json');limit=plan['limits']['page_chars']
    report=[];bindings={};all_record_checks=[];old_tree_files={}
    for episode in sorted((OLD/'episodes').iterdir()):
        state_path=episode/'TOOLS_STATE.json';state=read(state_path)
        bindings[relative(state_path)]=sha(state_path)
        originals=initial_outputs(episode)
        approved={}
        for path in sorted((episode/'gateway/session/approved').glob('*.json')):
            value=read(path)
            if value.get('type')=='search_results':
                approved.setdefault(digest(canonical(value)),[]).append(path)
        covered_approved=set()
        engine=object.__new__(module.ToolRuntime)
        engine.root=episode
        engine.state={'searches':copy.deepcopy(state['searches']),'sources':{},'actions':0,'runs':0,'candidates':{},'gateway_usage':{}}
        engine.limits=dict(module.DEFAULTS);engine.limits['page_chars']=limit
        engine._session=forbidden;engine._save=forbidden;engine._executor=forbidden;engine.dispatch=forbidden
        state_before=canonical(engine.state)
        for sid,entry in state['searches'].items():
            path=episode/entry['path'];cache=read(path);cache_hash=sha(path)
            require(cache_hash==entry['sha256'],'Old search cache changed')
            bindings[relative(path)]=cache_hash
            matches=approved.get(digest(canonical(cache)),[])
            require(matches,'Cached search does not match a complete approved gateway result')
            covered_approved.update(matches)
            for approved_path in matches:bindings[relative(approved_path)]=sha(approved_path)
            accepted=cache.get('accepted',[])
            require(sid in originals,'No original search output for cached page')
            old_output,old_output_path=originals[sid]
            bindings[relative(old_output_path)]=sha(old_output_path)
            cursor=0;cards=[];payload_bytes=[];projection_hashes=[];first=None
            while True:
                projected=module.project_search_page(cache,sid,cache_hash,cursor=cursor,page_chars=limit)
                again=module.project_search_page(cache,sid,cache_hash,cursor=cursor,page_chars=limit)
                require(wire(projected)==wire(again),'Projection is not deterministic')
                local=engine._read_source(sid,section='full',cursor=cursor)
                require(local==projected,'Local search pagination differs from pure projection')
                require(projected['cache_sha256']==cache_hash,'Projected cache hash mismatch')
                require(projected['cursor_units']=='accepted_record_index','Search cursor unit is ambiguous')
                require(projected['next_query_cursor']==cache.get('next_cursor'),'Provider cursor lost or confused with local cursor')
                require(projected['cached_accepted_count']==len(accepted),'Projection changes accepted-hit count')
                # Keep historical counter metadata equal for the initial-response byte comparison.
                full={**projected,'usage':old_output.get('usage',{})}
                require(len(wire(full))<=limit,'Projected tool response exceeds its byte ceiling')
                payload_bytes.append(len(wire(full)));projection_hashes.append(digest(wire(projected)))
                if first is None:first=projected
                cards.extend(projected['hits'])
                nxt=projected['next_cursor']
                if nxt is None:
                    require(projected['complete'] is True,'Final projected page incomplete')
                    break
                require(type(nxt) is int and nxt==cursor+len(projected['hits']) and nxt>cursor,'Hit pagination skips, repeats or stalls')
                cursor=nxt
            require([x['ordinal'] for x in cards]==list(range(1,len(accepted)+1)),'Original approved order changed')
            require(len(cards)==len(accepted),'Hit omitted or duplicated')
            cache_reconstruction=pages(engine,sid,'metadata',path.read_text(encoding='utf-8'))
            hit_checks=[]
            for ordinal,(item,card) in enumerate(zip(accepted,cards),1):
                hid=f'hit_{sid.split("_")[1]}_{ordinal:03d}'
                require(card['hit_id']==hid,'Stable hit ID changed')
                expected_hash=digest(canonical(item))
                require(module.raw(item)==canonical(item),'Independent canonical hash definition disagrees')
                require(card['record_sha256']==expected_hash,'Full original hit hash changed')
                identity=module.hit_identity(item,sid,ordinal)
                independent={'title':item.get('title'),'year':item.get('pubYear'),'pmcid':item.get('pmcid'),
                    'pmid':item.get('pmid',item.get('id') if item.get('source')=='MED' else None),
                    'doi':item.get('doi'),'source_record_id':item.get('id'),'source_database':item.get('source')}
                if item.get('pmid') is None and item.get('source')=='MED':independent['pmid']=item.get('id')
                require(all(identity[k]==v for k,v in independent.items()),'Identity field changed')
                if card['identity_complete']:
                    require(all(card[k]==v for k,v in independent.items()),'Complete card identity differs from source')
                metadata=pages(engine,hid,'metadata',canonical(item).decode('utf-8'))
                identity_pages=pages(engine,hid,'identity',module.raw(identity).decode('utf-8'))
                abstract=next((item[k] for k in ['abstractText','abstract'] if isinstance(item.get(k),str)),None)
                abstract_pages=pages(engine,hid,'abstract',abstract,missing=abstract is None)
                if card['identity_complete']:
                    preview=card.get('abstract_preview')
                    require(preview is None if abstract is None else isinstance(preview,str) and abstract.startswith(preview),'Abstract preview is not an exact prefix')
                    require(card['abstract_complete']==(abstract is not None and preview==abstract),'Abstract completeness flag is false')
                # Force multiple local pages to test losslessness even for short historic abstracts.
                if abstract:
                    prior=engine.limits['page_chars'];engine.limits['page_chars']=257
                    forced=pages(engine,hid,'abstract',abstract)
                    engine.limits['page_chars']=prior
                else:forced=abstract_pages
                check={'episode_id':episode.name,'search_id':sid,'hit_id':hid,'ordinal':ordinal,
                    'record_sha256':expected_hash,'initial_identity_complete':card['identity_complete'],
                    'full_identity_retrievable':True,'full_metadata_retrievable':True,
                    'abstract_present':abstract is not None,'abstract_characters':len(abstract) if abstract is not None else None,
                    'abstract_lossless':True if abstract is not None else None,
                    'metadata_pages':metadata['pages'],'identity_pages':identity_pages['pages'],
                    'abstract_pages':abstract_pages['pages'],'forced_257_character_abstract_pages':forced['pages']}
                hit_checks.append(check);all_record_checks.append(check)
            row={'episode_id':episode.name,'search_id':sid,'accepted_records':len(accepted),
                'query_sha256':digest(str(cache.get('query','')).encode('utf-8')),
                'old_cache_path':relative(path),'old_cache_sha256':cache_hash,
                'approved_gateway_artifacts':[relative(p) for p in matches],
                'old_initial_tool_output_path':relative(old_output_path),
                'old_initial_tool_output_bytes':len(wire(old_output)),
                'new_initial_tool_output_bytes':payload_bytes[0],
                'initial_byte_reduction':len(wire(old_output))-payload_bytes[0],
                'projected_page_count':len(payload_bytes),'projected_payload_bytes':payload_bytes,
                'projected_page_sha256':projection_hashes,
                'all_projected_page_bytes':sum(payload_bytes),
                'initial_hits_returned':len(first['hits']),
                'old_initial_complete_title_fields':title_count(old_output,accepted),
                'new_initial_complete_identity_cards':sum(c.get('identity_complete') is True for c in first['hits']),
                'all_records_preserved_in_original_order':True,'deterministic':True,
                'full_search_metadata_reconstruction':cache_reconstruction,'hit_checks':hit_checks}
            report.append(row)
        require(covered_approved=={p for paths in approved.values() for p in paths},'Not all old approved search results were replayed')
        require(canonical(engine.state)==state_before,'Cached local reading mutated runtime state')
    require(not NETWORK_ATTEMPTS,'Offline replay attempted networking')
    require(sha(runtime_path)==runtime_hash,'Formatter changed during replay; rerun after owner finalizes')
    require(all(sha(PROJECT/path)==h for path,h in bindings.items()),'Old approved data or captured metadata changed during replay')
    static=static_spec_chain()
    prior=sum(r['old_initial_tool_output_bytes'] for r in report)
    current=sum(r['new_initial_tool_output_bytes'] for r in report)
    all_pages=sum(r['all_projected_page_bytes'] for r in report)
    episodes=[]
    for eid in sorted({r['episode_id'] for r in report}):
        rows=[r for r in report if r['episode_id']==eid]
        episodes.append({'episode_id':eid,'search_pages':len(rows),'accepted_record_occurrences':sum(r['accepted_records'] for r in rows),
            'old_initial_bytes':sum(r['old_initial_tool_output_bytes'] for r in rows),
            'new_initial_bytes':sum(r['new_initial_tool_output_bytes'] for r in rows),
            'all_new_hit_page_bytes':sum(r['all_projected_page_bytes'] for r in rows),
            'old_initial_complete_title_fields':sum(r['old_initial_complete_title_fields'] for r in rows),
            'new_initial_complete_identity_cards':sum(r['new_initial_complete_identity_cards'] for r in rows)})
    result={'status':'PASS','created_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Exhaustive offline projection replay; no new Agent episode receives this cache, replay history or scientific content',
        'formatter_path':relative(runtime_path),'formatter_sha256':runtime_hash,
        'network_attempts':NETWORK_ATTEMPTS,'constructor_or_dispatch_called':False,'generator_executions':0,
        'old_files_written':False,'new_episode_inputs_written':False,
        'totals':{'cached_search_pages':len(report),'accepted_record_occurrences':len(all_record_checks),
            'abstracts_present':sum(r['abstract_present'] for r in all_record_checks),
            'all_present_abstracts_lossless':all(r['abstract_lossless'] for r in all_record_checks if r['abstract_present']),
            'all_identity_and_record_reads_lossless':True,'stable_order_and_hashes':True,
            'old_initial_tool_output_bytes':prior,'new_initial_tool_output_bytes':current,
            'new_all_hit_page_bytes':all_pages,'initial_output_byte_reduction_fraction':1-current/prior,
            'max_new_page_bytes':max(b for r in report for b in r['projected_payload_bytes']),
            'page_byte_ceiling':limit,'old_initial_complete_title_fields':sum(r['old_initial_complete_title_fields'] for r in report),
            'new_initial_complete_identity_cards':sum(r['new_initial_complete_identity_cards'] for r in report)},
        'episodes':episodes,'searches':report,'static_specification_chain':static,'input_hashes':bindings,
        'limitations':['Bytes compare captured initial search outputs with a deterministic projection of the same approved records and historical usage counters; this is not a new scientific run.',
          'Hit-card metadata and a bounded exact abstract prefix are exposed first; the complete original abstract/record remains explicitly locally retrievable.',
          'All-card traversal, full metadata/abstract reading and API history can still consume context; lower first-response bytes do not guarantee episode completion or better scientific models.',
          'Source admissibility, validity and applicability are unchanged and not newly certified by this mechanical replay.']}
    (OUT/'REPLAY_SEARCH_PROJECTION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows=['| Old episode | Cached search pages | Accepted record occurrences | Old initial bytes | New initial bytes | All new hit-page bytes |',
          '|---|---:|---:|---:|---:|---:|']
    rows += [f'| {r["episode_id"]} | {r["search_pages"]} | {r["accepted_record_occurrences"]} | {r["old_initial_bytes"]:,} | {r["new_initial_bytes"]:,} | {r["all_new_hit_page_bytes"]:,} |' for r in episodes]
    text='# Offline search-projection replay\n\n**PASS.** Replayed every old approved cached search page: '+str(len(report))+' pages / '+str(len(all_record_checks))+' accepted record occurrences. No HTTP, gateway session, constructor/dispatch, generator, credentials, patient data or reference was used. No old source content was placed in new episode inputs.\n\n'
    text+='\n'.join(rows)+'\n\nInitial tool-output bytes fall from **'+f'{prior:,}'+'** to **'+f'{current:,}'+'** ('+f'{100*(1-current/prior):.1f}%'+' reduction). Traversing all projected hit pages uses '+f'{all_pages:,}'+' bytes. These compare the same approved records, retaining the historical usage metadata; they are not a forecast of live context use or scientific performance.\n\n'
    text+='All record identities, original ordering, stable hit IDs and full-record hashes match. Every present abstract and every full record was reconstructed exactly through local pagination, including forced 257-character abstract pages. Missing abstracts remain unavailable. Old first outputs exposed '+str(result['totals']['old_initial_complete_title_fields'])+' complete literal title fields; new first outputs expose '+str(result['totals']['new_initial_complete_identity_cards'])+' complete identity cards, with any remaining hits reachable by local cursor.\n\n'
    text+='The specification chain also passes static inspection: the submitted model_spec is stored directly, staged byte-for-byte, and passed by the unchanged worker to generate(observed, specification, seed). The task is separate metadata; the evaluator checks staged hashes and uses the same runtime. No host task/model wrapper or root-key remapping is required. No author program was executed to establish this.\n\n'
    text+='The new audit extractor counts returned structured hit cards and explicitly read hit identity/metadata/abstract pages. It does not treat all cached records as exposed. Scientific provenance remains unassessed.\n\nFormatter SHA256: `'+runtime_hash+'`. Full per-page metrics, record hashes and input bindings are in `REPLAY_SEARCH_PROJECTION.json`.\n'
    (OUT/'REPLAY_SEARCH_PROJECTION.md').write_text(text,encoding='utf-8')
    print(json.dumps({'status':'PASS','totals':result['totals'],'formatter_sha256':runtime_hash},indent=2))


if __name__=='__main__':main()

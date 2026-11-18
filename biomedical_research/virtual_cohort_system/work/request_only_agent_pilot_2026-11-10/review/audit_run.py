"""Read-only postclosure metadata audit; never imports author code or API payloads.

Writes new review artifacts only after every planned episode has a durable
OUTCOME. Full response bodies, private reasoning, credentials, patient tables
and clinical references are outside this script's read set.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

UNIT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(path):return Path(path).relative_to(UNIT).as_posix()
def within(root,path):
    value=(root/path).resolve()
    if not value.is_relative_to(root.resolve()):raise ValueError('Artifact path leaves its episode')
    return value
def pick(row,keys):return {key:row.get(key) for key in keys}
def exposed_metadata(result):
    fragments=[]
    if isinstance(result.get('content'),str):fragments.append(result['content'])
    fragments.extend(item['context'] for item in result.get('matches',[]) if isinstance(item.get('context'),str))
    text='\n'.join(fragments);titles=[]
    for match in re.finditer(r'"title"\s*:\s*("(?:[^"\\]|\\.)*")',text):
        try:titles.append(json.loads(match.group(1)))
        except ValueError:pass
    return {'returned_chars':sum(map(len,fragments)),
            'literal_pmcids':sorted(set(re.findall(r'\bPMC[1-9][0-9]*\b',text))),
            'complete_literal_title_fields':sorted(set(titles))}
def numeric_leaves(value,path='model'):
    if isinstance(value,dict):
        for key,item in value.items():yield from numeric_leaves(item,path+'.'+key)
    elif isinstance(value,list):
        for i,item in enumerate(value):yield from numeric_leaves(item,path+f'[{i}]')
    elif isinstance(value,(int,float)) and not isinstance(value,bool):yield {'path':path,'declared_value':value,'provenance_status':'requires_static_source_link_audit'}


def audit_episode(planrow):
    identifier=planrow['episode_id'];episode=UNIT/'episodes'/identifier
    outcome=read(episode/'OUTCOME.json')
    state=read(episode/'TOOLS_STATE.json') if (episode/'TOOLS_STATE.json').exists() else {}
    calls=[]
    for path in sorted((episode/'calls').glob('*/reservation.json')):
        reserve=read(path);receipt_path=path.with_name('receipt.json')
        receipt=read(receipt_path) if receipt_path.exists() else {}
        calls.append({**pick(receipt,['call_number','started_utc','ended_utc','requested_model','returned_model','status','http_status','completion_status','usage','tariff_cost_usd','elapsed_seconds','no_automatic_retry']),
                      'reservation_created_utc':reserve.get('created_utc'),'reserved_usd':reserve.get('reserved_usd'),
                      'request_sha256':reserve.get('request_sha256'),'receipt_path':relative(receipt_path) if receipt else None,
                      'receipt_sha256':digest(receipt_path) if receipt else None})
    actions=[];queries=[];reads=[];metadata_pages=[]
    for path in sorted((episode/'tool_actions').glob('*/request.json')):
        request=read(path);result_path=path.with_name('result.json');result=read(result_path) if result_path.exists() else {}
        args=request['arguments'];name=request['name']
        record={'action':path.parent.name,'name':name,'started_utc':request.get('started_utc'),
                'status':result.get('status','uncertain_no_result'),'reason':result.get('reason'),
                'request_path':relative(path),'result_path':relative(result_path) if result else None}
        if name=='literature_search':queries.append({**record,**pick(args,['query','limit','cursor']),'returned_source_id':result.get('source_id')})
        if name=='read_source':reads.append({**record,**pick(args,['source_id','version','section','query','cursor']),
            'source_version':result.get('source_version'),'xml_sha256':result.get('xml_sha256'),
            'complete_page_sequence_end':result.get('complete'),'next_cursor':result.get('next_cursor'),
            'total_chars':result.get('total_chars'),'cursor_units':result.get('cursor_units','character_offset')})
        if name=='literature_search' or (name=='read_source' and str(args.get('source_id','')).startswith('search_')):
            metadata_pages.append({**record,'source_id':result.get('source_id',args.get('source_id')),**exposed_metadata(result)})
        actions.append(record)
    admitted=[]
    for sid,entry in state.get('searches',{}).items():
        path=within(episode,entry['path'])
        if digest(path)!=entry['sha256']:raise ValueError('Search cache hash changed')
        for item in read(path).get('accepted',[]):
            admitted.append({'search_id':sid,**pick(item,['id','source','pmcid','pmid','doi','title','pubYear'])})
    exposed_pmcids={item for page in metadata_pages for item in page['literal_pmcids']}
    exposed_titles={item for page in metadata_pages for item in page['complete_literal_title_fields']}
    admitted_pmcids={row['pmcid'] for row in admitted if row.get('pmcid')}
    admitted_titles={row['title'] for row in admitted if row.get('title')}
    usability={'accepted_metadata_rows_including_repeated_hits':len(admitted),
        'unique_accepted_pmcids':len(admitted_pmcids),'unique_accepted_titles':len(admitted_titles),
        'accepted_pmcids_literally_exposed_in_metadata_outputs':sorted(admitted_pmcids & exposed_pmcids),
        'accepted_complete_titles_literally_exposed_in_metadata_outputs':sorted(admitted_titles & exposed_titles),
        'metadata_pages':metadata_pages,'metadata_read_actions':sum(row['name']=='read_source' for row in metadata_pages),
        'returned_metadata_characters_including_overlaps':sum(page['returned_chars'] for page in metadata_pages),
        'interpretation':'Literal exposure is a conservative auditable text measure, not comprehension or proof that missing IDs were undiscoverable. Full titles may span output boundaries and are then not counted as one complete exposed field.'}
    candidates=[];previous=None
    for cid,entry in state.get('candidates',{}).items():
        folder=within(episode,entry['path']);manifest=read(folder/'manifest.json')
        if digest(folder/'manifest.json')!=entry['manifest_sha256']:raise ValueError('Candidate manifest changed')
        for name,expected in manifest['files'].items():
            if digest(within(folder,name))!=expected:raise ValueError('Candidate file changed')
        spec=read(folder/'model_spec.json');model=spec.get('model',{})
        current={'candidate_id':cid,'selected':outcome.get('selected_candidate')==cid,
                 'created_utc':manifest.get('created_utc'),'files':manifest['files'],
                 'manifest_sha256':entry['manifest_sha256'],'path':relative(folder),
                 'mechanical_validation':manifest.get('mechanical_validation'),
                 'generator_changed_from_previous':None if previous is None else manifest['files']['generator.py']!=previous['files']['generator.py'],
                 'specification_changed_from_previous':None if previous is None else manifest['files']['model_spec.json']!=previous['files']['model_spec.json'],
                 'numeric_model_leaves':list(numeric_leaves(model)),
                 'scientific_provenance_status':'Manual source-link and mathematical audit required; declarations are not source certification'}
        candidates.append(current);previous=current
    trials=[]
    for path in sorted((episode/'executions').glob('*/ATTEMPT.json')):
        final=path.with_name('execution.json');row=read(final) if final.exists() else read(path)
        trials.append({'path':relative(path.parent),**pick(row,['candidate_id','seed','created_utc','completed_utc','status','generator_executed','generated_sha256','error']),
                       'closed_receipt':final.exists(),'receipt_sha256':digest(final) if final.exists() else None})
    gateway_events=[];audit=episode/'gateway/session/audit.jsonl'
    if audit.exists():
        for line in audit.read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            gateway_events.append(pick(event,['timestamp_utc','type','status','reason','bytes','content_sha256']))
    return {'episode_id':identifier,'case_id':planrow['case_id'],'arm':planrow['arm'],
            'outcome':pick(outcome,['status','closed_utc','finalized','selected_candidate','unable_reason','calls_reserved','calls_receipted','requested_tool_actions','tool_usage','known_tariff_cost_usd','accounted_usd','unknown_usage_calls']),
            'calls':calls,'action_counts':dict(Counter(row['name'] for row in actions)),
            'action_status_counts':dict(Counter(row['status'] for row in actions)),
            'search_queries':queries,'admitted_search_metadata':admitted,
            'retrieval_usability':usability,
            'read_requests':reads,'fetched_fulltext_sources':state.get('sources',{}),
            'gateway_events':gateway_events,'candidates':candidates,'trials':trials,
            'pending_tool_state':state.get('pending'),
            'root_reference_access_by_audit':False,'author_code_executed_by_audit':False}


def main():
    plan=read(UNIT/'PLAN.json')
    missing=[row['episode_id'] for row in plan['episodes'] if not (UNIT/'episodes'/row['episode_id']/'OUTCOME.json').exists()]
    if missing:raise SystemExit('Not closed; no audit artifacts written. Pending: '+', '.join(missing))
    rows=[audit_episode(row) for row in plan['episodes']]
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'plan_sha256':digest(UNIT/'PLAN.json'),
            'scope':'Terminal API/tool/source/candidate metadata; not a scientific quality evaluation',
            'limitations':['Cached or returned source text is not proof of model comprehension.',
                'Metadata admission and full-text retrieval are different events.',
                'Hash or code changes do not establish mathematical changes or improved data quality.',
                'Numerical model declarations need source/operator/transport verification; no automatic certification.',
                'Costs are recorded tariff estimates, not provider invoices.'],
            'episodes':rows}
    json_path=OUT/'TOOL_SOURCE_COST_AUDIT.json';md_path=OUT/'TOOL_SOURCE_COST_AUDIT.md'
    if json_path.exists() or md_path.exists():raise SystemExit('Audit outputs already exist; will not overwrite')
    table=['| Episode | Terminal status | Calls | Search actions | Full texts fetched | Candidate versions | Trial attempts | Selected | Tariff cost |',
           '|---|---|---:|---:|---:|---:|---:|---|---:|']
    for row in rows:
        o=row['outcome'];table.append(f"| {row['episode_id']} | {o['status']} | {len(row['calls'])} | {len(row['search_queries'])} | {len(row['fetched_fulltext_sources'])} | {len(row['candidates'])} | {len(row['trials'])} | {o['selected_candidate'] or 'none'} | ${o['known_tariff_cost_usd']:.4f} |")
    text='# Request-only Agent run: execution and evidence-use audit\n\n'+'\n'.join(table)+'\n\nThese are completed activity counts, not proof of source validity or scientific accuracy. The JSON links every query, source read, immutable candidate, trial and API receipt. Numerical-constraint and assumption attribution requires the accompanying static scientific audit. No private reasoning, clinical rows or target reference results were read.\n'
    with json_path.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
    md_path.write_text(text,encoding='utf-8')
    print(json.dumps({'episodes':len(rows),'audit':str(json_path),'known_tariff_cost_usd':sum(row['outcome']['known_tariff_cost_usd'] for row in rows)},indent=2))


if __name__=='__main__':main()

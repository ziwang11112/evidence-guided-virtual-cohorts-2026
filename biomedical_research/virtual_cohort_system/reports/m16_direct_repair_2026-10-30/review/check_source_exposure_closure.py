"""Source metadata/log closure audit only. No patient or generated CSV reads."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bindings={};reports=[];pre=read(R/'prelaunch.json')
def bind(p):bindings[str(p.resolve())]=sha(p)
bind(R/'prelaunch.json')
for bid,expected_queries,expected_acquisitions in [('b1',2,3),('b2',3,3),('b3',4,2)]:
    b=R/'visible'/bid/'bundle';g=b/'gateway';s=read(g/'session/state.json');c=read(g/'config.json');link=read(g/'binding.json')
    log=[json.loads(x) for x in (g/'session/audit.jsonl').read_text().splitlines() if x.strip()]
    reg=read(b/'registry.json');adm=read(R/'source_admission'/bid/'ADMISSION_REVIEW.json')
    assert link['task_sha256']==sha(b/'task.json') and link['config_sha256']==s['config_sha256']==sha(g/'config.json')
    assert Path(link['bundle']).resolve()==b.resolve() and Path(s['session_path']).resolve()==(g/'session').resolve()
    assert c['budgets']['queries']==8 and c['budgets']['downloads']==4
    assert c['exclusions']['compact_aliases']==['NHANES','National Health and Nutrition Examination Survey']
    events=[x for x in log if x['type']=='http_attempt']
    counts={k:sum(x['budget']==k for x in events) for k in ['queries','downloads','auxiliary_requests']}
    assert all(counts[k]==s['usage'][k] for k in counts)
    assert [x['ordinal'] for x in events]==list(range(1,len(events)+1)) and len(events)==s['usage']['http_attempts']
    last=next(x for x in reversed(log) if x['type']=='adapter_command');assert last['usage']==s['usage']
    assert counts['queries']==expected_queries and counts['queries']<=8 and counts['auxiliary_requests']<=96
    acquisition=adm['acquisition_record'];manual=acquisition['controller_xml_or_docx_attempts']+acquisition['prior_controller_web_attempts']
    assert manual==adm['controller_acquisition_charges']
    total=counts['downloads']+manual
    assert total==expected_acquisitions==adm['cumulative_acquisitions_at_review'] and total<=4
    assert adm['remaining_acquisitions']==4-total
    assert adm['target_outcomes_read'] is False and acquisition['target_outcomes_read'] is False
    assert sha(R/'visible'/bid/'research/controller_source_admission.json')==sha(R/'source_admission'/bid/'ADMISSION_REVIEW.json')
    assert len(pre['registry_prefixes'][bid])==11 and reg['artifacts'][:11]==pre['registry_prefixes'][bid]
    for a in reg['artifacts']:assert sha(b/a['path'])==a['sha256'];bind(b/a['path'])
    for event in log:
        if event['type']=='artifact_approved':
            a=event['artifact'];p=g/'session'/a['session_relative_path'];assert sha(p)==a['sha256'];bind(p)
        if event['type']=='bundle_registration':
            assert event['task_sha256']==link['task_sha256']
            assert all(a in reg['artifacts'] for a in event['artifacts'])
    admitted=adm['admitted_artifacts'];assert all(a in reg['artifacts'] for a in admitted)
    assert sha(b/'registry.json')==adm['new_registry_sha256']
    before={'artifacts':[a for a in reg['artifacts'] if a not in admitted]}
    # Windows text writes use CRLF; preserve that byte serialization in this check.
    serialized=(json.dumps(before,indent=2)+'\n').replace('\n','\r\n').encode()
    assert hashlib.sha256(serialized).hexdigest()==adm['prior_registry_sha256']
    seen=set();search_count=0
    for p in (g/'session/approved').glob('*.json'):
        payload=read(p)
        if 'accepted' not in payload:continue
        search_count+=1;assert len(payload['accepted'])==payload['accepted_count']
        for record in payload['accepted']:
            text=re.sub('[^a-z0-9]','',(record.get('title','')+' '+record.get('abstractText','')).lower())
            assert 'nhanes' not in text and 'nationalhealthandnutritionexaminationsurvey' not in text
            if record.get('pmcid'):seen.add(record['pmcid'])
    assert search_count==expected_queries and seen==set(s['approved_metadata'])
    if bid=='b1':assert not admitted and not s['parents'] and acquisition['status']=='failed'
    if bid=='b2':assert {a['source_id'] for a in admitted}=={'PMC4750804'} and not s['parents']
    if bid=='b3':
        parent=s['parents']['PMC7803020']
        assert any(x['source_url']==acquisition['url'] and x['source_filename']=='mmc2.docx' for x in parent['supplements'])
        assert {a['source_id'] for a in admitted}=={'PMC7803020'}
    for p in [b/'task.json',b/'registry.json',g/'binding.json',g/'config.json',g/'session/state.json',g/'session/audit.jsonl',
              R/'source_admission'/bid/'ADMISSION_REVIEW.json',R/'visible'/bid/'research/controller_source_admission.json']:
        bind(p)
    for p in (R/'source_admission'/bid).glob('*.json'):bind(p)
    evidence=read(b/'candidates/initial/evidence.json');bind(b/'candidates/initial/evidence.json')
    ids={x['id'] for x in evidence['sources']}
    expected={'PMC8236402','PMC4208749','PMC6941025'}|({'PMC4750804'} if bid=='b2' else {'PMC7803020'} if bid=='b3' else set())
    assert ids==expected
    disclosures=[x['id'] for x in evidence['items'] if x['estimate'] is None and 'NHANES' in str(x)];assert disclosures
    reports.append({'builder':bid,'queries':expected_queries,'gateway_acquisition_attempts':counts['downloads'],
        'controller_acquisition_attempts':manual,'total_acquisition_attempts':total,'query_cap':8,'acquisition_cap':4,
        'auxiliary_requests':counts['auxiliary_requests'],'remaining_queries':8-expected_queries,'remaining_acquisitions':4-total,
        'registry_artifact_count':len(reg['artifacts']),'common_seed_prefix_count':11,'new_originals_admitted':int(bid!='b1'),
        'gateway_fetch_rejections':[x['reason'] for x in log if x['type']=='adapter_command' and x.get('status')=='rejected'],
        'generation_evidence_source_ids':sorted(ids),'incidental_exposure_disclosure_ids':disclosures,
        'registry_session_admission_linkage_verified':True,'last_gateway_command_utc':last['timestamp_utc'],
        'last_controller_admission_utc':adm['created_utc']})
result={'schema_version':1,'status':'pass','scope':'Source-query/acquisition budget and source-exposure closure only',
    'target_outcomes_read':False,'evaluation_run':False,'candidate_files_edited':False,'blockers':[],
    'counts':reports,'source_eligibility':{
        'PMC8236402_and_PMC4208749':'Bogalusa seed studies share recruitment; not independent confirmations.',
        'PMC6941025':'Independent Ferrara selected female sample; identical full original supplied to all builders.',
        'PMC8516664':'B1 requested CARDIA original; gateway rejection and two assisted failures charged. No full original admitted; not adopted as numerical generation evidence.',
        'PMC4750804':'B2 original methods inspected: KAHP Korean health examinations 2005-2009 with HIRA history, n=45098. Not NHANES recruitment. Incidental NHANES material is disclosed and excluded from adopted numerical generation.',
        'PMC7803020':'B3 independent Gunma 2009 health-check cohort; original plus exact gateway-manifest mmc2 DOCX admitted. Supplement is the same study, not independent evidence.'},
    'notes':['Failed attempts, gateway rejections and manual acquisitions are charged. The gateway download counter alone undercounts assisted acquisitions.',
             'The identical 11 seed files are outside new-acquisition charges under prelaunch protocol.',
             'Approved search title/abstract metadata passed the configured exclusion aliases and is registered; it is not full-original numerical evidence.',
             'Incidental NHANES citations in permitted full originals were exposed and disclosed. Recruitment eligibility and declared non-use are verified here; item-level source extraction is covered by separate source reviews. Zero pretrained-model prior knowledge is not claimed.',
             'This binds current logs/registries. Any later query, acquisition, registry or disclosure change requires re-audit. It does not authorize target release.'],
    'bindings':[{'path':p,'sha256':h} for p,h in sorted(bindings.items())]}
out=R/'review/SOURCE_EXPOSURE_CLOSURE.json'
with out.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'status':'pass','counts':reports,'binding_count':len(bindings),'report_sha256':sha(out)}))

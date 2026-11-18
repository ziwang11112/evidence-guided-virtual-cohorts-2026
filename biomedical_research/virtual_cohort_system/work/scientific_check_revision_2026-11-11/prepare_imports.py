"""Prepare paired, target-free review inputs from all twelve frozen laws.

No target/evaluation rows, target estimates, old search previews, audit conclusions,
API captures or credentials are read or copied. Full text remains local.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / 'request_only_repeatability_2026-11-11'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)

def prepare():
    plan = read(PREVIOUS/'PLAN.json')
    a = sorted((r for r in plan['episodes'] if r['case_id']=='PNS'), key=lambda r:r['episode_id'])
    b = sorted((r for r in plan['episodes'] if r['case_id']=='lipids'), key=lambda r:r['episode_id'])
    assert len(a)==len(b)==6
    ordered = [row for pair in zip(a,b) for row in pair]
    maps=[]
    for i, ep in enumerate(ordered, 1):
        pair_id=f'R{i:02d}'
        source=PREVIOUS/'episodes'/ep['episode_id']
        outcome=read(source/'OUTCOME.json')
        assert outcome['status']=='finalized' and outcome['selected_candidate']=='v001'
        original=source/'candidates'/'v001'
        manifest=read(original/'manifest.json')
        out=ROOT/'imports'/pair_id
        out.mkdir(parents=True,exist_ok=False)
        files={}
        for name in ['generator.py','model_spec.json','notes.json']:
            assert sha(original/name)==manifest['files'][name]
            (out/name).write_bytes((original/name).read_bytes())
            files[name]=sha(out/name)
        parents=read(source/'gateway/session/state.json')['parents']
        registered=read(source/'TOOLS_STATE.json')['sources']
        sources={}
        for sid, meta in sorted(registered.items()):
            parent=parents[sid]
            assert parent['version']==meta['version']
            xml=source/'gateway/session'/parent['xml_artifact']['session_relative_path']
            assert sha(xml)==parent['xml_artifact']['sha256']==meta['xml_sha256']
            name=f'sources/{sid}.v{parent["version"]}.xml'
            (out/name).parent.mkdir(exist_ok=True)
            (out/name).write_bytes(xml.read_bytes())
            files[name]=sha(out/name)
            sources[sid]={**meta,'path':name,'sha256':files[name],
                          'imported_frozen_source':True,'network_used':False}
        package={'schema_version':1,'pair_id':pair_id,'candidate_id':'v000',
                 'files':files,'sources':sources,
                 'candidate_manifest_sha256_original':sha(original/'manifest.json'),
                 'scope':'Original code/spec/notes and last captured version of each registered full-text source; no search previews, target results, rows or audit findings',
                 'source_version_policy':'Frozen imported version; explicit different-version request may use new retrieval',
                 'source_claims_not_certified':True}
        write(out/'package.json',package)
        maps.append({'pair_id':pair_id,'old_episode_id':ep['episode_id'],
                     'old_arm':ep['arm'],'case_id':ep['case_id'],
                     'old_candidate_relative_path':str(original.relative_to(PREVIOUS)).replace('\\','/'),
                     'old_manifest_sha256':sha(original/'manifest.json'),
                     'package_path':f'imports/{pair_id}/package.json',
                     'package_sha256':sha(out/'package.json'),
                     'block':(i+1)//2})
    write(ROOT/'_host_only/IMPORT_MAPPING.json',{'schema_version':1,
          'old_plan_sha256':sha(PREVIOUS/'PLAN.json'),'old_construction_closure_sha256':sha(PREVIOUS/'CONSTRUCTION_CLOSURE.json'),
          'mapping_rule':'Sort PNS IDs and lipid IDs independently; interleave PNS then lipids; no outcome-based selection',
          'historical_exposure':'Old project references already exposed. PNS_WORKFLOW_R1 previously saw target-family prevalence search preview. Search caches are not imported; code/spec/notes are unedited and author self-disclosures may persist.',
          'masking':'Neutral envelope IDs only; original scientific artifacts are byte-identical, not guaranteed blinded',
          'pairs':maps})
    print(json.dumps({'pairs':len(maps),'mapping':[{'pair_id':x['pair_id'],'old_episode_id':x['old_episode_id'],'case_id':x['case_id'],'block':x['block']} for x in maps]}))

if __name__=='__main__':prepare()

"""Independent joins/serialization verification against sealed results; no scientific fits or model execution."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import re

U = Path(__file__).resolve().parent
P = U.parents[1]
R = {"R1": U.parent/"cross_model_api_pilot_2026-11-10", "R2": U.parent/"economy_feedback_pilot_2026-11-10"}
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok, why):
    if not ok: raise ValueError(why)
def eq(a,b,why): require(a==b,why)
def near(a,b,why): require(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12),why)


class Page(HTMLParser):
    def __init__(self): super().__init__(); self.data_script=False; self.embedded=[]; self.links=[]; self.other_scripts=[]; self.script=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='script': self.script=True; self.data_script=attrs.get('id')=='data'
        for field in ['href','src']:
            if field in attrs:self.links.append(attrs[field])
    def handle_endtag(self,tag):
        if tag=='script':self.script=False;self.data_script=False
    def handle_data(self,data):
        if self.data_script:self.embedded.append(data)
        elif self.script:self.other_scripts.append(data)


def main():
    s=read(U/'SYNTHESIS.json');maps={};native={};summaries={};seeds={}
    for name in ['PNS_PARAMETER_MAP.json','LIPID_PARAMETER_MAP.json']:
        for row in read(U/name)['records']:
            k=(row['round'],row['version_id']);require(k not in maps,'Duplicate map ID');maps[k]=row
    for rnd,root in R.items():
        evaluation=read(root/'EVALUATION.json')
        records=read(root/('CONSTRUCTION_OUTCOMES.json' if rnd=='R1' else 'INITIAL_OUTCOMES.json'))['records']
        for row in records:
            ident=row.get('construction_id',row.get('parent_id'))
            native[(rnd,ident)]=dict(row,kind='initial',parent_version_id=None,review_disposition=None,
                receipt_path=root/'calls'/(ident+'_initial')/'receipt.json' if rnd=='R1' else root/'calls/initial'/ident/'receipt.json')
        if rnd=='R2':
            parents={r['parent_id']:r for r in records}
            for branch in read(root/'REVIEW_OUTCOMES.json')['records']:
                parent=parents[branch['parent_id']]
                native[(rnd,branch['branch_id'])]=dict(parent,kind='review',parent_version_id=branch['parent_id'],
                    review_disposition=branch['disposition'],candidate_path=branch['candidate_path'],receipt_path=root/'calls/review'/branch['branch_id']/'receipt.json')
        for row in evaluation.get('construction_summaries',evaluation.get('version_summaries')):
            ident=row.get('construction_id',row.get('version_id'));summaries[(rnd,ident,row['category'],row['id'])]=row
        for slot in evaluation['all_slots']:
            ident=slot.get('construction_id',slot.get('version_id'))
            for category in ['analyses','diagnostics']:
                for stat in slot[category]:seeds[(rnd,ident,slot['seed'],category,stat['id'])]=(slot,stat)
    attempts={(a['round'],a['version_id']):a for a in s['attempts']}
    eq(len(attempts),32,'Attempt count');eq(set(attempts),set(native),'Attempt/native join');eq(set(attempts),set(maps),'Attempt/map join')
    for key,a in attempts.items():
        n=native[key];m=maps[key];receipt=read(n['receipt_path']);root=R[key[0]]
        eq(a['provenance_record'],m,'Embedded provenance differs')
        for field in ['case_id','kind','parent_version_id','review_disposition']:eq(a[field],n[field],'Attempt lineage mismatch')
        for target,field in [('requested_model','requested_model'),('returned_model','returned_model'),('api_status','status'),('api_artifact_status','artifact_status'),('tariff_cost_usd','tariff_cost_usd')]:eq(a[target],receipt.get(field),'Attempt receipt field mismatch')
        eq(a['unknown_reserve_usd'],receipt['reserved_usd'] if receipt.get('tariff_cost_usd') is None else 0,'Unknown reserve mismatch')
        eq((P/a['call_receipt']).resolve(),n['receipt_path'].resolve(),'Receipt path mismatch')
        path=n['receipt_path'].with_name('artifact.json');eq(a['artifact_sha256'],sha(path) if path.exists() else None,'Artifact identity mismatch')
        expected_path=str((root/n['candidate_path']).relative_to(P)) if n['candidate_path'] else None
        eq(a['candidate_path'],expected_path,'Candidate/retention path mismatch')
        slots={seed[2]:slot for seed,(slot,stat) in seeds.items() if seed[:2]==key}
        eq(a['execution_status_counts'],dict(Counter(v['execution_status'] for v in slots.values())),'Execution failure counts')
        eq(a['successful_tables'],sum(v['execution_status']=='success' for v in slots.values()),'Successful tables')
        eq(a['complete_analysis_tables'],sum(v['analysis_status']=='complete' for v in slots.values()),'Complete tables')
        eq(a['scheduled_tables'],len(slots),'Scheduled tables')
        if n['review_disposition']=='retained_noop':
            parent=attempts[(key[0],n['parent_version_id'])];eq(a['candidate_path'],parent['candidate_path'],'No-op candidate differs')
    seen=set()
    for row in s['analysis_summaries']:
        key=(row['round'],row['version_id'],row['category'],row['analysis_id']);require(key not in seen,'Duplicate summary');seen.add(key)
        n=summaries[key];m=maps[key[:2]];claim=m.get('endpoint_claims',{}).get(row['analysis_id'],{})
        for field in ['case_id','unit','available_seeds','scheduled_seeds','seed_mean','mean_signed_difference','mean_absolute_difference']:eq(row[field],n.get(field),'Stored evaluation summary mismatch: '+str(key)+' '+field)
        eq([row['seed_min'],row['seed_max']],n['seed_range'] or [None,None],'Seed range differs')
        eq(row['reference_value'],n['reference']['value'],'Reference value differs');eq(row['reference_uncertainty'],n['reference']['uncertainty'],'Reference uncertainty differs')
        eq(row['declared_population_value'],claim.get('declared_population_value'),'Author claim differs');eq(row['validated_population_value'],claim.get('validated_population_value'),'Audited law differs')
        eq(row['claim_validation_status'],claim.get('validation_status','unassessed'),'Claim status differs')
        if row['validated_population_value'] is not None: eq(row['claim_validation_status'],'exact_law','Unsupported numeric law imported')
        supports=[p for p in m['parameters'] if row['analysis_id'] in p.get('analysis_ids',[])]
        eq(row['parameter_ids'],[p['parameter_id'] for p in supports],'Parameter-analysis join differs')
        eq(row['source_ids'],sorted({str(x) for p in supports for x in p['source_ids']}),'Source join differs')
        eq(row['provenance_components'],sorted({x for p in supports for x in p['provenance_components']}),'Provenance join differs')
    eq(seen,set(summaries),'All192 summaries covered')
    seen=set()
    for row in s['seed_results']:
        key=(row['round'],row['version_id'],row['seed'],row['category'],row['analysis_id']);require(key not in seen,'Duplicate seed row');seen.add(key)
        slot,stat=seeds[key]
        for field in ['case_id','execution_status','analysis_status','generated_sha256']:eq(row[field],slot[field],'Seed slot metadata differs')
        for target,field in [('value','value'),('unit','unit'),('statistic_status','status'),('reason','reason')]:eq(row[target],stat.get(field),'Seed statistic differs')
        eq(row['reference_value'],stat['reference']['value'],'Seed reference differs')
    eq(seen,set(seeds),'All576 seed entries covered')
    expected_parameters=[]
    for a in s['attempts']:
        for p in maps[(a['round'],a['version_id'])]['parameters']:
            expected_parameters.append({k:a[k] for k in ['round','version_id','case_id','model_config','kind','parent_version_id','law_delivery']}|p)
    eq(s['parameters'],expected_parameters,'All80 parameter rows join exactly')
    expected_law={ (r['round'],r['version_id'],r['analysis_id']):r for r in s['analysis_summaries'] if r['validated_population_value'] is not None and r['seed_mean'] is not None }
    eq(len(expected_law),45,'Law decomposition count');eq({(r['round'],r['version_id'],r['analysis_id']) for r in s['law_reference_decomposition']},set(expected_law),'Law subset differs')
    for row in s['law_reference_decomposition']:
        native_row=expected_law[(row['round'],row['version_id'],row['analysis_id'])]
        for field in ['seed_mean','validated_population_value','reference_value','claim_validation_status']:eq(row[field],native_row[field],'Decomposition value differs')
        eq(row['claim_validation_status'],'exact_law','Nonexact decomposition')
        near(row['generated_minus_validated_law'],row['seed_mean']-row['validated_population_value'],'Sample-law arithmetic')
        near(row['validated_law_minus_reference'],row['validated_population_value']-row['reference_value'],'Law-reference arithmetic')
    bad=[r for r in s['analysis_summaries'] if r['version_id']=='LIPID_DS_PRO_C2' and r['category']=='analyses']
    require(len(bad)==3 and all(r['validated_population_value'] is None and r['claim_validation_status']=='not_established' for r in bad),'Rejected DS proposal claim treated as validated')
    for key in [('R1','LIPID_OA_ASTRA_C1'),('R1','LIPID_OA_ASTRA_C2'),('R1','LIPID_OA_SOL_C2'),('R2','LIPID_SOL_A'),('R2','LIPID_SOL_B'),('R2','LIPID_ASTRA'),('R2','LIPID_SOL_A_FEEDBACK'),('R2','LIPID_SOL_A_SECOND_LOOK')]:
        require(all(r['validated_population_value'] is None for r in s['analysis_summaries'] if (r['round'],r['version_id'])==key),'Rank/latent correlation imported as requested exact law')
    known=sum(a['tariff_cost_usd'] or 0 for a in s['attempts']);reserve=sum(a['unknown_reserve_usd'] for a in s['attempts'])
    near(known,14.14412666,'Combined tariff');near(reserve,.21840852,'Combined unknown reserve')
    csv_checks={}
    for name,key in [('ATTEMPTS.csv','attempts'),('ANALYSIS_RESULTS.csv','analysis_summaries'),('PARAMETER_SOURCES.csv','parameters'),('SEED_RESULTS.csv','seed_results'),('LAW_REFERENCE_DECOMPOSITION.csv','law_reference_decomposition')]:
        with (U/name).open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
        eq(len(rows),len(s[key]),'CSV row count differs')
        for actual,expected in zip(rows,s[key]):
            for field,value in actual.items():
                target=expected.get(field)
                if isinstance(target,(list,dict)):eq(json.loads(value),target,'CSV structured cell differs')
                else:eq(value,'' if target is None else str(target),'CSV scalar differs')
        csv_checks[name]=len(rows)
    locator_counts=Counter();cache={}
    for locator in sorted({z for p in s['parameters'] for z in p['locators']}):
        if '#/' in locator:
            rel,pointer=locator.split('#',1);path=P/rel;node=cache.setdefault(str(path),read(path))
            for part in pointer.lstrip('/').split('/'):
                part=part.replace('~1','/').replace('~0','~');node=node[int(part)] if isinstance(node,list) else node[part]
            locator_counts['json_pointer']+=1
        elif re.search(r':\d+$',locator):
            rel,line=locator.rsplit(':',1);require(1<=int(line)<=len((P/rel).read_text(encoding='utf-8').splitlines()),'Code line locator outside file');locator_counts['code_line']+=1
        else:require((P/locator).is_file(),'File locator missing');locator_counts['file']+=1
    page=Page();page.feed((U/'index.html').read_text(encoding='utf-8'))
    eq(json.loads(''.join(page.embedded)),s,'HTML embedded JSON differs')
    for link in page.links:
        require(not re.match(r'^[a-z]+:',link),'Unexpected remote/external link');require((U/link.split('#')[0]).is_file(),'Broken output link: '+link)
    require(not re.search(r'\b(fetch|XMLHttpRequest|WebSocket)\b',''.join(page.other_scripts)),'Unexpected dynamic network request')
    for rel,digest in s['inputs_sha256'].items():eq(sha(P/rel),digest,'Input hash binding differs')
    counts=s['counts'];eq(counts['api_calls'],32,'Call count');eq(counts['initial_attempts'],28,'Initial count');eq(counts['complete_initial_artifacts'],21,'Complete initial count');eq(counts['working_initial_laws'],20,'Working initial count')
    eq(counts['scheduled_evaluation_tables'],96,'Eval schedule');eq(counts['successful_evaluation_tables'],72,'Eval availability');eq(counts['complete_evaluation_tables'],72,'Eval complete')
    near(counts['known_tariff_usd'],known,'Tariff count');near(counts['unknown_reserve_usd'],reserve,'Reserve count')
    source_hashes={str(root/'EVALUATION.json'):sha(root/'EVALUATION.json') for root in R.values()}
    checked=['SYNTHESIS.json','RESULTS_SUMMARY.md','index.html','PNS_PARAMETER_MAP.json','LIPID_PARAMETER_MAP.json','ROUND_ALIGNMENT_AUDIT.json','ROUND_ALIGNMENT_AUDIT.md',*csv_checks]
    checked += [p.relative_to(U).as_posix() for p in sorted((U/'figures').iterdir()) if p.is_file()]
    result={'status':'pass','blocking_issues':[],'created_utc':datetime.now(timezone.utc).isoformat(),'attempt_join_rows':32,'source_map_records':32,'summary_rows_checked':192,'seed_rows_checked':576,'parameter_rows_checked':80,'validated_law_rows_checked':45,'csv_rows_checked':csv_checks,'unique_locator_checks':dict(locator_counts),'html_embedded_data_exact_match':True,'local_html_links_verified':page.links,'no_op_candidate_lineage_verified':3,'source_evaluation_hashes':source_hashes,'artifact_hashes':{n:sha(U/n) for n in checked},'audit_script_sha256':sha(Path(__file__)),'scientific_generators_or_estimators_run':False,'api_calls':0,'credentials_or_private_raw_responses_read':False,'scope':'Exact joins, frozen stored numeric fields, source pointer resolution, serialization and algebraic consistency; prior scientific derivations are not newly re-proved.'}
    (U/'CONSISTENCY_CHECKS.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ['status','attempt_join_rows','summary_rows_checked','seed_rows_checked','parameter_rows_checked','validated_law_rows_checked','unique_locator_checks','html_embedded_data_exact_match']},indent=2))


if __name__=='__main__':main()

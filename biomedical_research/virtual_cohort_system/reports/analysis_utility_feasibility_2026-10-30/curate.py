"""Exact inspection export; no participant tables, full texts or source contexts."""
from pathlib import Path
import hashlib
import json
import re

O=Path(__file__).resolve().parent
P=O.parents[1]
W=P.parents[1]
D=P/'reports/analysis_utility_feasibility_2026-10-30'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(s):
    for raw in [str(W),W.as_posix(),str(W).replace('\\','\\\\')]:
        s=s.replace(raw,'WORKSPACE')
    s=re.sub(r'[A-Za-z]:[/\\]+Users[/\\]+[^\s\"\x27]+[/\\]+python\.exe','python',s)
    s=s.replace('RUNTIME_ROOT','RUNTIME_ROOT')
    s=re.sub(r'[A-Za-z]:[\\/]+Codex[\\/]+home[\\/]+skills','SKILLS_HOME',s)
    return s
def walk(x):
    if isinstance(x,str):return normalize(x)
    if isinstance(x,list):return [walk(y) for y in x]
    if isinstance(x,dict):return {normalize(k):walk(v) for k,v in x.items()}
    return x

def main():
    if D.exists():raise FileExistsError(D)
    files={}
    # Explicit files only: aggregate reports contain endpoint summaries, not rows.
    for name in ['launch.json','runtime_preflight.json','execution_locations.json','campaign_freeze.json',
                 'implementation_review.json','blind_review.json','postrun_review.json',
                 'prepare_launch.py','audit_current.py','freeze_campaign.py','summarize_results.py','curate.py']:
        files[name]=O/name
    for name in ['analysis.py','gates.py','evaluate.py','test_evaluator.py','INFERENCE.md','FREEZE_INTERFACE.md','CHECKS.json']:
        files['evaluator/'+name]=O/'evaluator'/name
    for name in ['aggregate_report.json','primary_endpoint_comparison.csv','primary_summary.csv','diagnostic_means.csv',
                 'release_gate.json','nhanes_insulin_analysis.png','nhanes_insulin_analysis.svg',
                 'pns_hba1c_analysis.png','pns_hba1c_analysis.svg']:
        files['results/'+name]=O/'results'/name
    stage=P/'work/analysis-utility-preparation-2026-10-29'
    files['protocols/campaign_feasibility_v2.json']=stage/'protocols/campaign_feasibility_v2.json'
    files['protocols/ACTIVE_PROTOCOL.json']=stage/'ACTIVE_PROTOCOL.json'
    files['protocols/feasibility.md']=stage/'prompts/feasibility.md'
    records=json.loads((O/'campaign_freeze.json').read_text())['constructions']
    extra={
        'ia':['launch_boundary.json','selection_plan.json','selection_pre_execution.json','final_selection.json','execution_statuses.json'],
        'ha':['launch_read_boundary.json','selection_rule.json','final_selection.json','execution_statuses.json','actual_checks.json','controller_failure_01.json'],
        'ib':['boundary_metadata.json','source_selection_rule.json','final_selection.json','completion_status.json','source_review.json'],
        'hb':['boundary_metadata.json','source_selection_rule.json','final_selection.json','completion.json','source_review.json']}
    for c in records:
        cid=c['construction_id'];b=Path(c['bundle_path'])
        for name in extra[cid]: files[f'constructions/{cid}/{name}']=O/cid/name
        for version in ['initial','selected']:
            candidate=Path(c[version+'_candidate'])
            for name in ['generator.py','model_spec.json','evidence.json','decision.md','checks.json','freeze.json','source_replay.json']:
                if (candidate/name).exists():files[f'constructions/{cid}/{version}/{name}']=candidate/name
        for output in c['outputs']:
            files[f'constructions/{cid}/receipts/{output["seed"]}.json']=Path(output['receipt_path'])
    D.mkdir(parents=True)
    provenance=[]
    for relative,source in files.items():
        raw=source.read_bytes()
        if source.suffix=='.json':
            data=(json.dumps(walk(json.loads(raw)),indent=2,ensure_ascii=False)+'\n').encode()
        elif source.suffix in {'.md','.py','.csv','.svg'}:
            data=normalize(raw.decode('utf8')).encode()
        else:data=raw
        target=D/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        provenance.append({'source':source.relative_to(P).as_posix(),'destination':relative,
                           'original_sha256':hashlib.sha256(raw).hexdigest(),'curated_sha256':sha(target),
                           'transformation':'machine-specific path normalization only' if raw!=data else 'none'})
    readme='''# M10 feasibility inspection package

Two public-data enrichment tasks, four independent Agent constructions, twelve final generated tables, and all aggregate analyses. See the parent MILESTONE_10_RESULTS.md for scientific interpretation. Ordinary Agent implementation is valid; no framework-superiority comparison is claimed.

This archive contains scientific generators/specifications and evidence, decisions, controller/evaluator code, execution receipt metadata, aggregate results/figures and independent reviews. It intentionally excludes participant-level observed/reference/generated tables, identifiers/mappings/weights, source full texts, synthetic source-context tables, environments and credentials. Results are analysis-level summaries, including all prespecified subgroup cells.

The original local campaign was frozen and verified before target parsing. Path-normalized receipt copies are inspection artifacts, not a claim that those commitments can be verified in this data-free archive. curation_provenance.json records original versus curated hashes. Scientific equations and numeric estimates are unchanged. This is not a self-contained clinical replay. To reproduce the study, reacquire the official M9 sources, recreate the recorded eligibility and evidence packets, restore the original work-directory layout, and use the stated Python/WSL dependencies. The curated M9 package supplies source/preparation metadata and code; source PDFs/HTML and clinical tables remain omitted.

Construction A is ia for insulin and ha for HbA1c; B is ib and hb. All initial/final scientific models were retained byte-identically. Source feedback was approximate and did not universally fit every source. Three residual draws vary individual noise only; they are not independent cohorts or calibrated evidence uncertainty. PNS has no design-based CI in this study. NHANES age reference CI crosses zero. No unrestricted measurement substitution or clinical equivalence is established.
'''
    (D/'README.md').write_text(readme,encoding='utf8')
    (D/'curation_provenance.json').write_text(json.dumps({'records':provenance,'participant_rows_exported':False,
        'fulltexts_exported':False,'scope':'Exact reviewed file list; path-normalized inspection copies'},indent=2)+'\n',encoding='utf8')
    manifest={p.relative_to(D).as_posix():sha(p) for p in sorted(D.rglob('*')) if p.is_file()}
    (D/'file_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'curated_files':len(manifest)+1,'package':str(D),'participant_rows_exported':False}))

if __name__=='__main__':main()

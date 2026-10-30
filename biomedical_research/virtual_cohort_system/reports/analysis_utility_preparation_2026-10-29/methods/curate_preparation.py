"""Copy an exact nonparticipant allowlist into a reviewable preparation report."""
from pathlib import Path
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
DEST=PROJECT/'reports/analysis_utility_preparation_2026-10-29'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if DEST.exists():raise FileExistsError('Curated snapshot already exists; preserve it')
    files={}
    for group in ['methods','protocols','prompts']:
        for p in (ROOT/group).glob('*'):
            if p.is_file() and p.suffix in {'.py','.json','.md'}:files[p.relative_to(ROOT).as_posix()]=p
    for case in ['nhanes_insulin','pns_hba1c']:
        for f in ['task.json','preparation_report.md','visible/task_metadata.json','visible/field_map.json']:
            files[f'cases/{case}/{f}']=ROOT/case/f
        for f in ['source_admission.json','admitted_evidence.json','input_manifest.json']:
            files[f'cases/{case}/{f}']=ROOT/'bundles'/case/f
    for f in ['candidate_packet.json','extraction_checks.json','source_screen.csv','README.md']:
        files['evidence_proposal/'+f]=ROOT/'evidence'/f
    for f in ['preparation_validation.json','review/source_admission_summary.json']:
        files[f]=ROOT/f
    # No participant CSV, raw archive, source fulltext, secret or reference is in this map.
    allowed_csv={'evidence_proposal/source_screen.csv'}
    forbidden={'custodian','raw','sources','observed.csv','reference.csv','design_weights.csv','id_mapping.csv'}
    pairs=[]
    for rel,src in sorted(files.items()):
        assert not set(Path(rel).parts)&forbidden,rel
        assert src.suffix!='.csv' or rel in allowed_csv,rel
        assert src.is_file(),src
        dst=DEST/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
        assert sha(src)==sha(dst)
        pairs.append({'curated':rel,'original_relative_to_preparation':src.relative_to(ROOT).as_posix(),'sha256':sha(src)})
    (DEST/'README.md').write_text('''# Two task preparation and analysis protocol package

This snapshot contains preparation metadata, evidence extractions and admission decisions, scientific analysis definitions, Agent instructions and invented-fixture analysis code. NHANES fasting insulin has 1,961 eligible participants; PNS HbA1c has 7,979. No new generator or target analysis has run.

The two builder packets contain 78 and 59 admitted external evidence items respectively, with source-context restrictions. Eighteen SHIP healthy-reference items are withheld because the table and prose conflict. Source items are not independent studies or biological confirmations.

The shared point estimator passed seven invented-fixture tests after review corrections. PNS reference evaluation is restricted to point estimates and an unweighted sensitivity because design fields are unavailable. NHANES survey-variance integration, conventional generator specification, runtime binding and actual model/resource accounting remain before the matched campaign.

Participant covariates, outcomes, design-weight rows, linkage secrets, raw XPT/workbook files and full source papers are deliberately absent. Input manifests describe locally retained originals; references to those files are not a claim that this export is a self-contained clinical replay. The scripts expect the original project/work directory layout. Public source retrieval URLs and hashes are documented in metadata.

The planned comparison has 30 final target tables: two tasks, two independent constructions for each Agent arm, one conventional fit, and three residual draws. These are planned workloads, not completed results or independent clinical replications.

Read ../../MILESTONE_9_PREPARATION.md for the scientific scope and remaining gates. Provenance and file_manifest.json bind this exact nonparticipant snapshot. No GitHub upload is performed by this script.
''',encoding='utf-8')
    provenance={'scope':'Exact whitelist copies; no participant tables or full source texts','pairs':pairs}
    (DEST/'curation_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    manifest={p.relative_to(DEST).as_posix():sha(p) for p in sorted(DEST.rglob('*')) if p.is_file()}
    (DEST/'file_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'curated_files':len(manifest)+1,'participant_tables_copied':0,'source_fulltexts_copied':0,'destination':str(DEST)}))


if __name__=='__main__':main()

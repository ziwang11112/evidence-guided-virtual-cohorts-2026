"""Allowlisted aggregate-only review archive; participant rows stay local."""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
DEST=PROJECT/'reports/m13_target_validation_2026-10-30'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    DEST.mkdir(parents=True,exist_ok=False)
    copied=[]
    def copy(src, relative):
        src=Path(src);target=DEST/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,target)
        assert digest(src)==digest(target)
        copied.append({'path':relative,'sha256':digest(target),'bytes':target.stat().st_size})
    frozen=json.loads((ROOT/'preaccess_freeze.json').read_text())
    for relative,sha in frozen['files'].items():
        assert digest(ROOT/relative)==sha
        copy(ROOT/relative,relative)
    for relative in ['preaccess_freeze.json','target_access_authorization.json','deployment_manifest.json',
                     'generated_manifest.json','report_results.py','package_release.py']:
        copy(ROOT/relative,relative)
    for folder in ['postaccess_review','postrun_audit','custodian_repair_v1']:
        for path in sorted((ROOT/folder).iterdir()):
            if path.is_file() and path.suffix in {'.py','.md','.json','.csv'}:
                copy(path,f'{folder}/{path.name}')
    for name in ['aggregate.json','aggregate.csv','seed_comparison.csv','revision_changes.csv',
                 'primary_analyses.png','primary_analyses.pdf','conditional_spread.png','conditional_spread.pdf']:
        copy(ROOT/'results'/name,f'results/{name}')
    for src,name in [
        ('custodian/acquisition/private/acquisition_receipt.json','original_acquisition_receipt.json'),
        ('custodian/acquisition/private/quality_report.json','superseded_original_quality.json'),
        ('custodian/acquisition_corrected/private/quality_report.json','corrected_quality.json'),
        ('custodian/acquisition_corrected/private/technical_amendment.json','technical_amendment.json')]:
        copy(ROOT/src,f'data_provenance/{name}')
    for builder in ['build01','build02']:
        for candidate in ['initial','source_reviewed']:
            for name in ['freeze.json','deployment_provenance.json']:
                copy(ROOT/'deployment'/builder/'candidates'/candidate/name,
                     f'deployment_records/{builder}/{candidate}/{name}')
            for seed in [33101,33102,33103]:
                run=f'{candidate}_{seed}'
                for name in ['execution.json','input_bindings.json']:
                    copy(ROOT/'deployment'/builder/'executions'/run/name,
                         f'execution_records/{builder}/{run}/{name}')
    for name in ['gallagher_mean','gallagher_normal_33101','gallagher_normal_33102','gallagher_normal_33103']:
        copy(ROOT/'references'/f'{name}.json',f'reference_records/{name}.json')
    readme='''# M13-B curated target-validation review archive

This archive contains the frozen scientific protocol, code and invented tests; acquisition provenance and the retained parser failure/correction; the exact generation schedule and execution/reference commitments; all measured/generated aggregate analyses; plots; and independent arithmetic reviews. No participant inputs, real endpoints, generated participant tables, ID mapping or raw XPT are included. The only nonaggregate CSV is audits/invented_fixture.csv, explicitly invented.

The full execution/custody filesystem remains local under work/m13b. This curated archive is not sufficient for historical verify_execution: generated rows and staged participant inputs are intentionally omitted. The hashes remain inspectable and were checked against complete local executions before export. Do not mistake absent files for missing experimental runs.

## Results and source models

See ../../MILESTONE_13B_RESULTS.md. results/aggregate.json is the complete62-estimand release for measured data and all16 generated tables; aggregate.csv has1054rows. The seed/comparison CSVs and figures are derived displays, not new model fits. postrun_audit independently recomputed the entire release. Source model generator/specification/evidence bytes and their actual Agent construction/review are in the preceding ../m13_source_loop_2026-10-30/build01 and build02 archives; protocol.json records their identities.

## Reproduction boundary and sequence

The controller scripts are the actual locally executed scripts, not a portable one-command installer. Original absolute paths, opaque IDs and historical authorization timestamps remain as provenance. A new reproduction needs fresh run directories, path bindings and freezes; never rewrite these historical records or reuse their one-time output directories.

1. Obtain official DEMO_J/BMX_J/DXX_J from the CDC URLs in custodian/metadata_sources.json. Compare against data_provenance/technical_amendment.json raw hashes. Read XPORT with pyreadstat1.3.7, or independently verify exact zero handling before a different reader is used. The pandas3.0.3 failure and corrected interpretation are explicitly preserved.
2. Apply the unchanged frozen custody transformation and positive-MEC design-frame/domain rules. Keep the private frame, ID mapping and842eligible covariate rows local. New random opaque IDs change file hashes but not scientific values or ordering.
3. Restore source candidates and their complete candidate-relative files from the M13-A archive into new local build bundles. Preserve generator.py/model_spec.json bytes. Bind the observed target covariates in fresh deployment tasks, with their own lineage and receipts. Configure the already documented WSL/bubblewrap generator runtime; do not import Agent code into the host.
4. Run each initial/final candidate at33101/33102/33103 and the four published-equation references. Verify every output/receipt and exact roster. The known source equations/SEE are explicit baseline assumptions, not target-trained values.
5. Freeze a fresh matching evaluator/protocol manifest and use the exact schemas/62-estimand panel in evaluator/README.md. The historical experiment froze before acquisition; a reproduction after reading this release is not a new blinded confirmation. Compare aggregates rather than regenerated opaque IDs or receipt timestamps.

Recorded numerical environment: Python3.12, NumPy2.4.5, pandas3.0.3, SciPy1.17.1, pyreadstat1.3.7; statsmodels was used for an invented test reference. Actual generators ran in the recorded isolated WSL runtime. Reproducing already-frozen generation requires no model training or new LLM call. Repeating scientific Agent construction is a different experiment and may yield different models.

data_provenance/superseded_original_quality.json describes the known incorrect first parser output; only corrected_quality.json describes the analyzed frame. No outcome associations informed this technical repair. Source/device and population transport remain unresolved. Positive generated relationship directions or nominal intervals are not new clinical evidence.
'''
    target=DEST/'README.md';target.write_text(readme,encoding='utf-8')
    copied.append({'path':'README.md','sha256':digest(target),'bytes':target.stat().st_size})
    allowed_csv={'audits/invented_fixture.csv','postrun_audit/independent_aggregate_recomputation.csv',
                 'results/aggregate.csv','results/seed_comparison.csv','results/revision_changes.csv'}
    for item in copied:
        path=DEST/item['path']
        assert path.suffix.lower() not in {'.xpt','.parquet','.feather'}
        if path.suffix=='.csv':
            assert item['path'] in allowed_csv
            with path.open(encoding='utf-8',newline='') as f:header=next(csv.reader(f))
            if item['path'] != 'audits/invented_fixture.csv':
                assert not set(header)&{'SEQN','DXDTOPF','bodyfat','record_id'}
        if path.suffix in {'.json','.csv','.md','.py'}:
            assert not re.search(r'm13b_[0-9a-f]{32}',path.read_text(encoding='utf-8'))
    manifest={'scope':'curated_code_protocol_provenance_aggregate_only','files':sorted(copied,key=lambda x:x['path']),
              'excluded':['raw_XPT','real_covariates','real_endpoints','generated_participant_tables','id_mapping','temporary_files'],
              'checks':'All copied hashes exact; CSV allowlist/headers and opaque-patient-ID scan passed'}
    (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(copied)+1,'bytes':sum(x['bytes'] for x in copied),'destination':str(DEST)}))


if __name__=='__main__':main()

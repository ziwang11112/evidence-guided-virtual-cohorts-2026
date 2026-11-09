"""Assemble complete analysis-use records; no cohort generation or scoring gate."""
from pathlib import Path
import csv, hashlib, json

HERE=Path(__file__).resolve().parent
SOURCES=['GLYCEMIA_AUDIT.json','IRON_LIPID_AUDIT.json','RECONSTRUCTION_PROSPECTIVE_AUDIT.json']

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(value):return value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)

def main():
    analyses=[];inputs=[]
    for name in SOURCES:
        f=HERE/name;d=json.loads(f.read_bytes());assert len(d['analyses'])==8
        inputs.append({'file':name,'sha256':digest(f)})
        for i,a in enumerate(d['analyses']):
            analyses.append({k:a[k] for k in ['id','case','analysis','evidence_status','supported_use','unsupported_use','diagnosis','smallest_followup']}|
                            {'complete_numeric_record':name+'#/analyses/'+str(i)})
    assert len(analyses)==24 and len({a['id'] for a in analyses})==24
    record={'schema_version':1,'purpose':'Retrospective scientific-use map, not a calibrated reliability classifier or new clinical validation.',
        'analysis_families':24,'new_clinical_cases':0,'new_generated_tables':0,'source_files':inputs,
        'interpretation':'Analysis families are not datasets, independent studies or additional experiments. Preserve native units and original information boundaries; no global accuracy score or new pass threshold.',
        'analyses':analyses}
    (HERE/'USE_MAP.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    columns=['id','case','analysis','supported_use','unsupported_use','diagnosis_category','diagnosis_confidence','smallest_followup','complete_numeric_record']
    with (HERE/'USE_MAP.csv').open('w',newline='',encoding='utf8') as out:
        writer=csv.DictWriter(out,fieldnames=columns);writer.writeheader()
        for a in analyses:
            writer.writerow({k:text(a[k]) for k in columns if k not in ['diagnosis_category','diagnosis_confidence']}|
                            {'diagnosis_category':a['diagnosis']['category'],'diagnosis_confidence':a['diagnosis']['confidence']})
    state={'status':'COMPLETED_EXISTING_CASE_DIAGNOSIS','date':'2026-11-08',
        'core':'Agent generation of analyzable virtual biomedical data from published evidence and research requests.',
        'reviewed_analysis_families':24,'new_clinical_cases':0,'new_generated_tables':0,'old_target_retuning':False,
        'completed_checks':['H03 variance decomposition','iron source/transport contingency arithmetic','L03 lognormal joint projections and support',
            'HRS deterministic source-law moments','all-eight-source-age-profile sensitivity','independent algebraic and scientific reviews'],
        'decision':'Retain core method; distinguish demonstrated reconstruction and partial external utility. No new current implementation defect or target-independent scalar repair established for prominent residual mismatches.',
        'specific_negative_design_result':'Using all eight admitted age means/quantiles under declared normal approximation yields SD0.32904 vs unchanged H03 law0.35162; it is not a simple dispersion remedy.',
        'next':'Source applicability and matching conditional variability/dependence evidence before a new candidate; an age-specific source-profile candidate is a distinct use, not promised target improvement.',
        'closed_units_preserved':['old clinical experiments','8 November exact-moment extra-instruction batch'],
        'no_training_HPC_paid_API_or_new_automation':True,
        'manuscript':'v0.25 retained; this diagnostic map supplements the current claims without relabeling old validations.'}
    (HERE/'STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'analysis_families':len(analyses),'new_tables':0,'files_written':['USE_MAP.json','USE_MAP.csv','STATE.json']}))

if __name__=='__main__':main()

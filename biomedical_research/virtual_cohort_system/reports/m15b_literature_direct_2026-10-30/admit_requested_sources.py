"""Controller admission of two explicitly requested source acquisitions; no outcome access."""
from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime, timezone

RUN = Path(__file__).resolve().parent
BUNDLE = RUN / 'visible/bundle'
SOURCE = RUN / 'private/source_access'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    report = RUN / 'SUPPLEMENTAL_SOURCE_ACCESS.md'
    if not report.is_file():
        raise RuntimeError('Await completed original-source provenance review')
    acquisition = json.loads((SOURCE/'acquisition_log.json').read_text(encoding='utf-8-sig'))
    if acquisition['attempt_count'] != 2 or acquisition['success_count'] != 2:
        raise RuntimeError('Unexpected acquisition history')
    for item in acquisition['attempts']:
        path = Path(item['local_path'])
        if digest(path) != item['sha256']:
            raise RuntimeError('Acquired source changed')
    registry_path = BUNDLE/'registry.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8-sig'))
    destinations = [
        ('PMC6941025', 'PMC6941025.fullTextXML.xml', 'PMC6941025.xml'),
        ('PMC6941025', 'PMC6941025.fulltext.private.txt', 'PMC6941025.txt'),
        ('PMC8236402', '41366_2021_810_MOESM1_ESM.docx', 'PMC8236402.supplement.docx'),
        ('PMC8236402', 'Yun2021.supplement.fulltext.private.txt', 'PMC8236402.supplement.txt'),
        ('PMC8236402', 'Yun2021.supplement.image1.png', 'PMC8236402.supplement.image1.png'),
        ('PMC8236402', 'Yun2021.supplement.image2.png', 'PMC8236402.supplement.image2.png'),
        ('PMC8236402', 'Yun2021.supplement.image3.png', 'PMC8236402.supplement.image3.png'),
    ]
    entries = []
    for source_id, local_name, public_name in destinations:
        target = BUNDLE/'sources/controller'/public_name
        if target.exists():
            raise RuntimeError('Admission already exists; inspect rather than overwrite')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE/local_name, target)
        entries.append({'source_id':source_id,'path':target.relative_to(BUNDLE).as_posix(),
                        'sha256':digest(target),'origin':'curator','screening':'approved'})
    registry['artifacts'].extend(entries)
    registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    receipt = {
        'schema_version':1, 'utc':datetime.now(timezone.utc).isoformat(),
        'kind':'controller_supported_original_source_admission', 'entries':entries,
        'acquisition_attempts_charged':2,
        'access_review_sha256':digest(report),
        'acquisition_log_sha256':digest(SOURCE/'acquisition_log.json'),
        'provenance':'PMC6941025 is the Ferrara original, not an NHANES cohort. Its incidental NHANES discussion is admitted exposure, not generation evidence. Yun DOCX belongs to the existing Bogalusa original and is not an independent cohort.',
        'content':'Complete originals, unredacted structural text conversions and all three embedded DOCX images. Text conversion does not transcribe figure pixels; original XML/DOCX tables and figures authoritative.',
        'numeric_use':'Builder must extract and decide applicability; no desired target coefficient is supplied. BMD outcome regressions cannot be used as adjusted urate regressions.',
        'remaining_gateway_downloads_after_controller_charge':5,
        'new_deeply_inspected_unique_originals':1,
        'fulltext_local_only':True,
        'target_outcomes_read':False
    }
    receipt_path=RUN/'visible/research/controller_source_admission.json'
    with receipt_path.open('x',encoding='utf-8') as out:
        json.dump(receipt,out,ensure_ascii=False,indent=2)
        out.write('\n')
    print(json.dumps({'registered_new_artifacts':len(entries),'receipt':str(receipt_path),
                      'target_outcomes_read':False,'rows_created':False}))

if __name__ == '__main__':
    main()

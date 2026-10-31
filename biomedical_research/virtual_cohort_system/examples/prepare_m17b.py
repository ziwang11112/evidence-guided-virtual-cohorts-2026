"""Prepare aggregate-only M17-B builder inputs. Does not choose or run a model."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, value):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')


def prepare(destination, packet, admission):
    root, source = Path(destination).resolve(), Path(packet).resolve()
    admitted = json.loads(Path(admission).read_text(encoding='utf-8'))
    manifest = json.loads((source / 'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    if root.exists() or admitted['status'] != 'admitted':
        raise ValueError('Use a new bundle and explicit root admission')
    for relative, expected in admitted['file_sha256'].items():
        path = (source / relative).resolve()
        path.relative_to(source)
        if digest(path) != expected:
            raise ValueError('Source packet changed: ' + relative)
    root.mkdir(parents=True)
    (root / 'candidates').mkdir()
    (root / 'sources').mkdir()
    registry = []
    for relative in admitted['file_sha256']:
        dst = root / 'sources' / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, dst)
    for study in manifest['sources']:
        for artifact in study['artifacts']:
            relative = artifact['relative_path']
            if digest(root / 'sources' / relative) != artifact['sha256']:
                raise ValueError('Manifest artifact changed: ' + relative)
            registry.append({'source_id': study['source_id'], 'path': 'sources/' + relative,
                'sha256': artifact['sha256'], 'origin': 'curator', 'screening': 'approved'})
    task = {'schema_version': 1, 'task_id': 'm17b-evidence-only-complete-cohort',
        'mode': 'whole_cohort', 'population':
        'US community adults aged 20-79, standardized quota design: 40 people per female=0/1 crossed with age bins [20,35), [35,50), [50,65), [65,80); no national representativeness claim.',
        'row_id': 'sample_id', 'n_rows': 320,
        'columns': [
            {'name':'sample_id','kind':'string','unit':'identifier','role':'identifier','nullable':False},
            {'name':'age','kind':'integer','unit':'years','role':'generated','nullable':False,'minimum':20,'maximum':79},
            {'name':'female','kind':'category','unit':'1','role':'generated','nullable':False,'categories':[0,1]},
            {'name':'bmi','kind':'number','unit':'kg/m2','role':'generated','nullable':False,'minimum':0},
            {'name':'urate','kind':'number','unit':'mg/dL','role':'generated','nullable':False,'minimum':0}],
        'information_policy': {'mode':'published_evidence','excluded_cohorts':['NHANES','NHANES_2007_2008'],
            'allowed_tools':['admitted_source_read','request_evidence_clarification','contract_validation','controller_source_feedback']},
        'budget': {'source_queries':0,'source_downloads':0,'revisions':1}}
    write(root / 'task.json', task)
    write(root / 'registry.json', {'artifacts':registry})
    write(root / 'INPUT_ADMISSION.json', {'admission_sha256':digest(admission),
        'packet_manifest_sha256':digest(source/'SOURCE_MANIFEST.json'),
        'individual_records_supplied':0,'scientific_model_supplied':False,
        'source_files':admitted['file_sha256']})
    return root


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', required=True)
    p.add_argument('--packet', required=True)
    p.add_argument('--admission', required=True)
    a = p.parse_args()
    print(prepare(a.destination, a.packet, a.admission))

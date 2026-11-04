"""Admit the coordinator-reviewed numerical paper references to both arms."""
from pathlib import Path
import hashlib
import json
import shutil

unit = Path(__file__).resolve().parent
bundle = unit / 'bundle'
source = unit / 'sources/HRS_PUBLISHED_REFERENCES.json'
destination = bundle / 'sources/HRS_PUBLISHED_REFERENCES.json'
registry = json.loads((bundle / 'registry.json').read_text())
assert not destination.exists()
shutil.copyfile(source, destination)
registry['artifacts'].append({'source_id': 'FILSHSTEIN_PAPER_AGGREGATES',
    'path': 'sources/HRS_PUBLISHED_REFERENCES.json',
    'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'origin': 'curator', 'screening': 'approved'})
(bundle / 'registry.json').write_text(json.dumps(registry, indent=2) + '\n', encoding='utf-8')
review = {'reviewer': 'root', 'source': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/',
    'checked': 'HRS Original and Synthetic columns of Tables 2 and 3, compared to numeric transcription; source code denominator definitions separately checked.',
    'access': 'Both arms receive the same source reference artifact before freeze; no generated results included.',
    'statistical_scope': 'Published rounded source summaries; not a new independent patient reference.',
    'sha256': registry['artifacts'][-1]['sha256']}
(unit / 'PAPER_REFERENCE_ADMISSION.json').write_text(json.dumps(review, indent=2) + '\n', encoding='utf-8')
print('Admitted published numerical references to shared packet.')

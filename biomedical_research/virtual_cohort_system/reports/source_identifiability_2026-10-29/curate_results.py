"""Curate code, commitments and aggregate-only M6 artifacts for inspection."""
from pathlib import Path
import hashlib
import json
import re

E=Path(__file__).resolve().parent
P=E.parents[1]
C=P/'reports/source_identifiability_2026-10-29'

def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    C.mkdir(exist_ok=False)
    entries={}
    def add(path, relative=None):
        assert path.is_file(), path
        entries[relative or path.relative_to(E).as_posix()]=path
    for name in ['protocol.json','protocol_commitment.json','controller.py','commit_protocol.py',
                 'prepare_bundle.py','bundle_preparation.json','source_commitment.json',
                 'POSTRUN_AUDIT.md','curate_results.py','finalize_validation.py']:
        add(E/name)
    for name in ['probe_authorization.json','evaluation_commitment.json']:
        if (E/name).exists(): add(E/name)
    for folder in ['design','review','analysis','source_feedback','source_analysis','results']:
        if not (E/folder).exists(): continue
        for path in sorted((E/folder).iterdir()):
            if path.is_file() and path.suffix in ['.json','.md','.py','.csv','.png','.pdf']:
                add(path)
    for name in ['task.json','registry.json']:
        add(E/'agent_bundle'/name,'builder/'+name)
    for path in sorted((E/'agent_bundle').glob('*.py')):
        add(path,'builder/'+path.name)
    for label in ['zero','minus','plus']:
        for path in sorted((E/'agent_bundle/candidates'/label).iterdir()):
            if path.is_file() and path.suffix in ['.json','.md','.py']:
                add(path,'candidates/'+label+'/'+path.name)
    for path in sorted((E/'agent_bundle/source_replays').glob('*/replay.json')):
        add(path,'replay_records/'+path.parent.name+'.json')
    prefixes=[(str(P.parents[1]),'<LOCAL_WORKSPACE>'),('<LOCAL_USER>','<LOCAL_USER>'),
              ('<CODEX_HOME>','<CODEX_HOME>'),('<LOCAL_LINUX_USER>','<LOCAL_LINUX_USER>')]
    replacements=[]
    for prefix,replacement in prefixes:
        for variant in {prefix,prefix.replace('\\','/'),prefix.replace('/','\\'),prefix.replace('\\','\\\\'),prefix.replace('/','\\\\')}:
            replacements.append((variant,replacement))
    replacements.sort(key=lambda x:-len(x[0]))
    provenance=[]
    for relative,path in sorted(entries.items()):
        original=path.read_bytes(); exported=original; changes=0
        if path.suffix in ['.json','.md','.py','.csv']:
            text=original.decode('utf-8-sig')
            for prefix,replacement in replacements:
                count=text.count(prefix)
                if count: text=text.replace(prefix,replacement); changes+=count
            assert not re.search(r'(?i)[CD]:[\\/]|<LOCAL_LINUX_USER>|/mnt/[cd]/',text),relative
            if changes: exported=text.encode('utf-8')
        output=C/relative; output.parent.mkdir(parents=True,exist_ok=True); output.write_bytes(exported)
        provenance.append({'path':relative,'original_sha256':sha(original),'curated_sha256':sha(exported),
                           'path_replacements':changes})
    (C/'curation_provenance.json').write_text(json.dumps({'scope':'Explicit M6 code/aggregate inspection allowlist',
        'normalization':'Filesystem prefixes changed only in copied artifacts. Original frozen records stay untouched; embedded hashes still identify original records.',
        'records':provenance},indent=2)+'\n',encoding='utf-8')
    (C/'README.md').write_text('''# M6 constructive source-identifiability inspection package

Read the project-level MILESTONE_6_RESULTS.md and POSTRUN_AUDIT.md for the complete result and claim boundary. This is a deliberately constructed conditional interaction under assumed product source covariates and an imperfect inherited anchor. It is not a new biological discovery, proof of compatibility with all published evidence, or validation against a new real cohort.

The package retains all three frozen candidates, mathematical certificates, original-source feedback, the exact descriptive gate, both interpretations of the previously unreplayed age/BMI source table, fixed protocols, analysis code, every aggregate result and the independent audit. Any failed gate remains visible; absent probe artifacts mean the protocol stopped before that phase.

No real participant table was used in M6. Row-level synthetic source/probe input and generated tables, full-text papers, runtime settings and temporary caches are omitted. Synthetic grid-cell CSVs are aggregates of ten generated replicates, not patient records. The public source locators remain in evidence records. The original local frozen bundles contain the omitted inputs/receipts.

curation_provenance.json binds original/copied hashes and path replacements. Embedded original hashes are not rewritten. This is an inspection archive, not a portable runnable frozen bundle; original directory layout, admitted sources, synthetic covariate inputs and execution runtime are needed for full replay. Preparation and generation code expose those requirements without claiming one-command reproduction from this folder.
''',encoding='utf-8')
    manifest={p.relative_to(C).as_posix():sha(p.read_bytes()) for p in sorted(C.rglob('*')) if p.is_file()}
    (C/'file_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'curated_files':len(manifest)+1,'normalized_files':sum(r['path_replacements']>0 for r in provenance)}))

if __name__=='__main__': main()

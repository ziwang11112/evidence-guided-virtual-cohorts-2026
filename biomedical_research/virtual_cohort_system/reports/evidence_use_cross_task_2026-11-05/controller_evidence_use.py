"""Bind the optional pure evidence-use API to an actual new candidate.

No path selected by an author can substitute a different task or baseline.
This is a procedural local-file commitment, not host-security isolation.
"""
from pathlib import Path
from cohort_harness import lifecycle
from cohort_harness.contracts import require
from cohort_harness.evidence_use_v1 import validate_evidence_use


def _file(bundle, relative):
    path = Path(bundle).joinpath(*lifecycle.safe_relative(relative))
    require(not any(lifecycle._link(p) for p in [path, *path.parents]), 'Linked artifact rejected')
    require(path.resolve().is_relative_to(Path(bundle).resolve()), 'Artifact escapes bundle')
    require(path.is_file(), 'Missing evidence-use artifact: '+relative)
    return path


def validate_candidate_use(bundle, candidate, required_analysis_ids, baseline=None):
    _, relative = lifecycle._candidate(Path(bundle), candidate)
    roles = {'task': 'task.json'}
    roles.update({name: relative+'/'+name+'.json'
                  for name in ['evidence', 'model_spec', 'analysis_evidence', 'checks']})
    roles['generator'] = relative+'/generator.py'
    if baseline is not None:
        _, parent = lifecycle._candidate(Path(bundle), baseline)
        for role, name in [('baseline_evidence', 'evidence.json'),
                           ('baseline_model_spec', 'model_spec.json'),
                           ('baseline_generator', 'generator.py')]:
            roles[role] = parent+'/'+name
    manifest_path = _file(bundle, relative+'/evidence_use_v1.json')
    manifest = lifecycle.read_json(manifest_path)
    require(set(manifest.get('bindings', {})) == set(roles), 'Wrong actual candidate/baseline role set')
    for role, path in roles.items():
        require(manifest['bindings'][role]['path'] == path, 'Evidence-use role points to a different actual input: '+role)
    artifacts = {name: _file(bundle, name).read_bytes() for name in roles.values()}
    checks = lifecycle.read_json(_file(bundle, roles['checks']))
    for result in checks['artifacts']:
        path = relative+'/'+result['path']
        artifacts[path] = _file(bundle, path).read_bytes()
    return validate_evidence_use(manifest, artifacts, required_analysis_ids=required_analysis_ids)

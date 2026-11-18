"""Read-only inputs and a thin wrapper around the frozen lifestyle operator."""
from pathlib import Path
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OLD = ROOT / 'work/lifestyle_application_2026-11-11'
PROTOCOL = ROOT / 'work/scientific_use_acceptance_2026-11-16/MINIMAL_VALIDATION_PROTOCOL.md'
TRAITS = ['bmi', 'total_cholesterol', 'hdl_cholesterol']
GROUPS = ['pastoralist', 'rural_nonpastoralist', 'urban_nonpastoralist']
STRATA = [(g, s) for g in GROUPS for s in ['F', 'M']]
CONTRASTS = ['rural_minus_pastoralist', 'urban_minus_pastoralist', 'urban_minus_rural']
EXPECTED_N = {'bmi': 1189, 'total_cholesterol': 400, 'hdl_cholesterol': 405}
ROOT_SEED = 16161
N_REPLICATES = 500
MAX_SECONDS = 3600

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def import_frozen(filename):
    spec = importlib.util.spec_from_file_location('matched_frozen_' + filename, OLD / (filename + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

OP = import_frozen('analysis_operator')
ADAPTER = import_frozen('reference_adapter')

def get_inputs():
    inventory = read(OLD / 'FINAL_TABLES.json')
    historical = read(OLD / 'EVALUATION_INPUTS.json')
    for name, expected in historical['files'].items():
        assert sha(OLD / name) == expected, 'Historical evaluation file changed: ' + name
    assert inventory['construction_closure_sha256'] == sha(OLD / 'CONSTRUCTION_CLOSURE.json')
    expected_slots = {(f'LIFESTYLE_A{a}', s) for a in [1, 2] for s in [64001, 64003, 64007]}
    assert len(inventory['slots']) == 6
    assert {(s['episode_id'], s['seed']) for s in inventory['slots']} == expected_slots
    assert all(s['status'] == 'success' for s in inventory['slots'])
    records = historical['inputs']
    assert len(records) == 7 and sum(r['kind'] == 'real_reference' for r in records) == 1
    for r in records:
        f = Path(r['path']).resolve()
        assert f.is_relative_to(ROOT.resolve())
        assert sha(f) == r['sha256'], 'Historical dataset bytes changed'
        if r['kind'] == 'virtual':
            slot = next(s for s in inventory['slots'] if (s['episode_id'], s['seed']) == (r['episode_id'], r['seed']))
            assert f == (OLD / slot['generated_path']).resolve()
            assert r['sha256'] == slot['generated_sha256']
        else:
            assert r['dataset_id'] == 'real' and r['sha256'] == ADAPTER.EXPECTED_SHA
    return sorted(records, key=lambda r: (r['kind'] != 'real_reference', r['dataset_id']))

def load_frames(records):
    frames, exclusions = {}, None
    for r in records:
        if r['kind'] == 'real_reference':
            d, exclusions = ADAPTER.load_reference(r['path'])
        else:
            d = pd.read_csv(r['path'], dtype={'id': str})
        assert list(d.columns) == OP.REQUIRED
        assert d.id.notna().all() and d.id.astype(str).is_unique
        assert d.sex.isin(['F', 'M']).all() and d.lifestyle.isin(GROUPS).all()
        assert np.isfinite(d.age).all()
        frames[r['dataset_id']] = d
    return frames, exclusions

def eligible(frame, trait):
    valid = np.isfinite(frame.age) & (frame.age > 18)
    valid &= frame.sex.isin(['F', 'M']) & frame.lifestyle.isin(GROUPS)
    valid &= frame[trait].notna() & np.isfinite(frame[trait]) & (frame[trait] > 0)
    return frame.loc[valid, OP.REQUIRED].reset_index(drop=True).copy()

def strata_counts(pool):
    return [int(((pool.lifestyle == g) & (pool.sex == s)).sum()) for g, s in STRATA]

def make_pools(frames):
    return {trait: {name: eligible(d, trait) for name, d in frames.items()} for trait in TRAITS}

def sample_pool(pool, counts, spawn_key):
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(ROOT_SEED, spawn_key=tuple(spawn_key))))
    selected = []
    for (g, s), n in zip(STRATA, counts):
        if n == 0:
            continue
        indices = np.flatnonzero(((pool.lifestyle == g) & (pool.sex == s)).to_numpy())
        if not len(indices):
            raise ValueError(f'Nonzero reference stratum unavailable: {g}/{s}')
        selected.append(indices[rng.integers(0, len(indices), size=n)])
    if not selected:
        raise ValueError('Empty planned sample')
    d = pool.iloc[np.concatenate(selected)].reset_index(drop=True).copy()
    # Bootstrap copies are repeated selections, not new participants.
    d['id'] = ['bootstrap_row_' + str(i) for i in range(len(d))]
    assert strata_counts(d) == list(counts) and d.id.is_unique
    return d

def analyze_trait(frame, trait):
    d = frame.copy(deep=True)
    # The original operator is unchanged. Other traits are outside this fit.
    for other in TRAITS:
        if other != trait:
            d[other] = np.nan
    output = OP.analyze_frame(d)
    status = next(t for t in output['trait_status'] if t['trait'] == trait)
    selected = [r for r in output['contrasts'] if r['trait'] == trait and r['stratum'] == 'pooled']
    if status['status'] != 'computed' or len(selected) != 3 or any(c['status'] != 'computed' for c in selected):
        raise ValueError('Pooled analysis unavailable: ' + str(status.get('reason', status['status'])))
    sd = status['sample_sd']
    return dict(n=int(status['n']), sample_sd=float(sd),
        **{c['contrast']: float(c['estimate'] * sd) for c in selected})

def verify_frozen():
    freeze = read(HERE / 'FREEZE.json')
    for name, expected in freeze['files'].items():
        assert sha(ROOT / name) == expected, 'Frozen file changed: ' + name
    return freeze

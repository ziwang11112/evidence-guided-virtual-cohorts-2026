"""Run Agent-authored enrichment without loading the hidden reference or scores.

Adapted from the earlier observed-cell preservation runner. This controller owns
I/O, hashes and interface checks only; no biological relation is specified here.
Procedural source review is required before importing a candidate. Not a sandbox.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import traceback
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT_COLUMNS = ['row_id', 'bmi', 'age', 'sex']
OUTPUT_COLUMNS = INPUT_COLUMNS + ['insulin']
SEEDS = list(range(270101, 270121))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_new(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def read_frame(path):
    return pd.read_csv(path, dtype={'row_id': str}, float_precision='round_trip')


def validate_observed(frame):
    if list(frame.columns) != INPUT_COLUMNS or len(frame) < 3:
        raise ValueError('Unexpected observed schema or insufficient rows')
    if frame.isna().any().any() or frame.row_id.duplicated().any():
        raise ValueError('Missing observed values or duplicate keys')
    if not frame.row_id.map(lambda x: isinstance(x, str) and bool(x)).all():
        raise ValueError('Row keys must be nonempty strings')
    for col in ['bmi', 'age', 'sex']:
        if not pd.api.types.is_numeric_dtype(frame[col]) or not np.isfinite(frame[col].to_numpy()).all():
            raise ValueError('Invalid observed numeric field: ' + col)
    if not (frame.bmi > 0).all() or not frame.age.between(20, 79).all() or not frame.sex.isin([1, 2]).all():
        raise ValueError('Observed frame violates the frozen population schema')


def check_output(observed, enriched):
    if not isinstance(enriched, pd.DataFrame) or list(enriched.columns) != OUTPUT_COLUMNS:
        raise ValueError('Expected exactly observed columns followed by insulin')
    if len(enriched) != len(observed):
        raise ValueError('Row count changed')
    pd.testing.assert_frame_equal(observed.reset_index(drop=True),
                                  enriched[INPUT_COLUMNS].reset_index(drop=True),
                                  check_dtype=False, check_exact=True)
    if not pd.api.types.is_numeric_dtype(enriched.insulin):
        raise ValueError('Insulin must be numeric')
    insulin = enriched.insulin.to_numpy(float)
    if not np.isfinite(insulin).all() or not (insulin > 0).all():
        raise ValueError('Insulin must be finite and positive, in uU/mL')
    return insulin


def rng_equal(a, b):
    return a[0] == b[0] and np.array_equal(a[1], b[1]) and a[2:] == b[2:]


def call_checked(module, observed, evidence, seed):
    frame_in, evidence_in = observed.copy(deep=True), copy.deepcopy(evidence)
    rng_before = np.random.get_state()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            enriched = module.generate(frame_in, evidence_in, seed)
        if not rng_equal(rng_before, np.random.get_state()):
            raise ValueError('Generator altered global numpy RNG')
        pd.testing.assert_frame_equal(frame_in, observed, check_exact=True)
        if evidence_in != evidence:
            raise ValueError('Generator mutated input model specification')
        check_output(observed, enriched)
        return enriched, sorted(set(str(w.message) for w in caught))
    finally:
        np.random.set_state(rng_before)


def execute(candidate, output, observed_path, provenance_paths):
    candidate, output, observed_path = map(lambda p: Path(p).resolve(), [candidate, output, observed_path])
    if output.exists():
        raise FileExistsError('Preserve previous run; choose a new run directory')
    source, spec_path = candidate/'generator.py', candidate/'model_spec.json'
    observed, evidence = read_frame(observed_path), read_json(spec_path)
    validate_observed(observed)
    paths = [source, spec_path, observed_path, Path(__file__).resolve()] + [Path(p).resolve() for p in provenance_paths]
    commitments = {str(p): sha(p) for p in paths}
    output.mkdir(parents=True)
    write_new(output/'pre_execution.json', {
        'created_utc': datetime.now(timezone.utc).isoformat(), 'files': commitments,
        'seeds': SEEDS, 'n_rows': len(observed),
        'scope': 'Interface checks and observed preservation only. No hidden reference loaded.',
        'route': 'Agent-authored numerical program',
    })
    global_rng = np.random.get_state()
    try:
        modspec = importlib.util.spec_from_file_location('submitted_enrichment', source)
        module = importlib.util.module_from_spec(modspec)
        modspec.loader.exec_module(module)
        if not rng_equal(global_rng, np.random.get_state()):
            raise ValueError('Import altered global numpy RNG')
        records, value_hashes = [], []
        for number, seed in enumerate(SEEDS, 1):
            enriched, caught = call_checked(module, observed, evidence, seed)
            if number == 1:
                repeated, _ = call_checked(module, observed, evidence, seed)
                pd.testing.assert_frame_equal(enriched, repeated, check_exact=True)
            path = output/f'enriched_{number:02d}.csv'
            enriched.to_csv(path, index=False, float_format='%.17g')
            reread = read_frame(path)
            values = check_output(observed, reread)
            if not np.array_equal(values, enriched.insulin.to_numpy(float)):
                raise ValueError('Insulin changed during CSV round trip')
            value_hashes.append(hashlib.sha256(values.tobytes()).hexdigest())
            records.append({'draw_id': str(number), 'seed': seed, 'path': str(path), 'sha256': sha(path),
                            'n_rows': len(enriched), 'warnings': caught})
        for path, expected in commitments.items():
            if sha(path) != expected:
                raise ValueError('A committed input changed during generation: ' + path)
        result = {'created_utc': datetime.now(timezone.utc).isoformat(),
                  'observed_sha256': sha(observed_path), 'candidate': str(candidate),
                  'all_contract_checks_pass': True, 'same_seed_reproducible': True,
                  'all_observed_cells_preserved': True, 'unique_added_vectors': len(set(value_hashes)),
                  'draws': records, 'input_files': commitments,
                  'interpretation': 'Repeated random draws from one Agent construction, not independent model constructions.'}
        write_new(output/'execution.json', result)
        print(json.dumps({k:v for k,v in result.items() if k not in ['draws','input_files']}, indent=2))
    except Exception as err:
        write_new(output/'failure.json', {'type': type(err).__name__, 'message': str(err),
                                         'traceback': traceback.format_exc(),
                                         'scope': 'Implementation failure; no hidden score-based selection.'})
        raise
    finally:
        np.random.set_state(global_rng)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--observed', default=str(ROOT/'shared/observed.csv'))
    parser.add_argument('--provenance', nargs='*', default=[])
    args = parser.parse_args()
    execute(args.candidate, args.output, args.observed, args.provenance)


if __name__ == '__main__':
    main()

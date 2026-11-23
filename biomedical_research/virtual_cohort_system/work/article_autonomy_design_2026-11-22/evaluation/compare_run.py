"""Score frozen virtual tables and verify the generating agent's two analyses."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from iron import evaluate


def compare(manifest, mapping):
    result = []
    sorted_values = {}
    for run in manifest['runs']:
        entry = {k: run[k] for k in ('scenario', 'seed', 'status')}
        result.append(entry)
        if run['status'] != 'success':
            continue
        path = Path(run['table'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != run['sha256']:
            raise ValueError('Frozen virtual table hash changed')
        source = pd.read_csv(path)
        canonical = pd.DataFrame({
            name: source[definition['column']] * definition['factor']
            for name, definition in mapping['measurements'].items()
        })
        sorted_values[(entry['scenario'], entry['seed'])] = np.sort(canonical.to_numpy(), axis=0)
        entry['sha256'] = digest
        entry['independent'] = independent = evaluate(canonical, mapping.get('explicit_source_claims'))
        if independent['status'] != 'computed':
            continue
        targets = dict(crude_or=independent['crude_or']['generated'],
                       spearman=independent['continuous_spearman_on_virtual_rows'])
        entry['agreement_with_authored_analysis'] = {}
        for name, true in targets.items():
            column = 'diagnostic_' + mapping['outputs'][name]
            if source[column].nunique(dropna=False) != 1:
                raise ValueError('Expected one analytical result per virtual table')
            authored = float(source[column].iloc[0])
            entry['agreement_with_authored_analysis'][name] = {
                'authored': authored, 'independent': true,
                'within_1e_minus_9': bool(true is not None and np.isclose(authored, true, atol=1e-9, rtol=0))}
    pairing = []
    for (scenario, seed), values in sorted_values.items():
        primary = sorted_values.get(('primary', seed))
        if scenario == 'primary' or primary is None:
            continue
        pairing.append({'scenario':scenario, 'seed':seed,
                        'both_sorted_columns_identical':bool(np.array_equal(primary, values)),
                        'max_abs_sorted_change_hb_g_l_then_ferritin_ug_l':
                            np.max(np.abs(primary - values), axis=0).tolist()})
    return {'tables':result, 'comparison_to_primary_within_seed':pairing}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', type=Path)
    p.add_argument('mapping', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    load = lambda path: json.loads(path.read_text(encoding='utf8'))
    with args.output.open('x', encoding='utf8') as f:
        json.dump(compare(load(args.manifest), load(args.mapping)), f, indent=2, allow_nan=False)

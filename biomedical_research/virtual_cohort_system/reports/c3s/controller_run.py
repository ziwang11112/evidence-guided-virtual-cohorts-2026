"""Execute one root-released source-only session, without printing its full trace."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

R = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('structure', choices=['linear', 'alternative'])
    args = parser.parse_args()
    gate_path = R / 'ROOT_RELEASE_SET.json'
    assert sha(gate_path) == '8a82df82724dbfe787bad5b10d788d1f67d5fe954b420de47f0fa7f553c315b3'
    gate = json.loads(gate_path.read_bytes())
    assert gate['status'] == 'approved' and not gate['target_access_authorized']
    for name, digest in gate['bindings'].items():
        assert sha(R / name) == digest, name
    binding = gate['structures'][args.structure]
    bundle = R / args.structure
    assert sha(R / binding['release']) == binding['release_sha256']
    assert sha(bundle / 'candidates/initial/freeze.json') == binding['initial_freeze_sha256']
    assert sha(bundle / 'calibration_plan.json') == binding['plan_sha256']
    assert sha(bundle / 'scientific_criteria.json') == binding['criteria_sha256']
    spec = importlib.util.spec_from_file_location('c3_adapter', R / 'method/run_source_calibration.py')
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    result = adapter.run_calibration(
        bundle, 'initial', 's', json.loads((bundle / 'calibration_plan.json').read_bytes()),
        json.loads((bundle / 'scientific_criteria.json').read_bytes()),
        json.loads((R / binding['release']).read_bytes()))
    summary = {key: result[key] for key in
               ('status', 'selected_trial', 'stop_reason', 'usage', 'elapsed_seconds')}
    summary['structure'] = args.structure
    summary['result_sha256'] = sha(bundle / 'source_calibration/s/result.json')
    with (R / (args.structure + '_COMPLETED.json')).open('x', encoding='utf-8') as stream:
        json.dump(summary, stream, indent=2)
        stream.write('\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()

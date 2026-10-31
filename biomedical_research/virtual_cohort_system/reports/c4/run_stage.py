"""Root orchestration only; all generator execution stays in the reviewed harness."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parents[1]))
sys.path.insert(0, str(R / 'method'))
from controller import run_phase


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['feedback', 'election', 'test'])
    args = parser.parse_args()
    receipt = R / (args.phase + '_COMPLETED.json')
    if receipt.exists():
        raise RuntimeError('Completed phase must not be repeated')
    started = time.monotonic()
    rows = run_phase(R, args.phase, R / ('RELEASE_' + args.phase + '.json'))
    summary = {
        'phase': args.phase,
        'scheduled_slots': len(rows),
        'computed_slots': sum(row['status'] == 'success' for row in rows),
        'status_counts': {status: sum(row['status'] == status for row in rows)
                          for status in sorted({row['status'] for row in rows})},
        'elapsed_seconds': time.monotonic() - started,
        'plan_sha256': hashlib.sha256((R / 'method/plan.json').read_bytes()).hexdigest(),
        'release_sha256': hashlib.sha256((R / ('RELEASE_' + args.phase + '.json')).read_bytes()).hexdigest(),
        'aggregate_digest_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':'),
                                                             allow_nan=False).encode()).hexdigest(),
    }
    with receipt.open('x', encoding='utf-8') as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()

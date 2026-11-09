"""Create an explicit manifest for independent recomputation; no row reads."""
from pathlib import Path
import json
import act

HERE = Path(__file__).resolve().parent

def main():
    protocol = act.read(HERE / 'PROTOCOL.json')
    bundle = Path(protocol['bundle'])
    seal = act.read(HERE / 'AUTHOR_SEALED.json')
    records = []
    for candidate in sorted(seal['candidate_freezes']):
        for seed in protocol['target_seeds']:
            stage = Path(candidate).name
            run_id = stage + '_target_' + str(seed)
            path = HERE / 'actions' / (run_id + '_generated.result.json')
            report = act.read(path)
            if report['result']['status'] != 'success': raise ValueError('Analysis did not succeed')
            values = report['result']['result']['result']['analyses']
            records.append({'candidate': stage, 'seed': seed,
                'output': str(bundle / 'executions' / run_id / 'output/generated.csv'),
                'analysis': str(path),
                'metric_pointers': {row['id']: '/result/result/result/analyses/'+str(i)+'/value' for i,row in enumerate(values)}})
    act.write(HERE / 'TARGET_VERIFICATION_MANIFEST.json', {'runs': records})
    print(json.dumps({'runs': len(records), 'target_row_reads': False}))

if __name__ == '__main__': main()

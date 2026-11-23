"""Verify the three transmitted inputs and costs from durable captures after closure."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import author_stage as author


def load(path):
    return json.loads(path.read_text(encoding='utf8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root, article_path, request_key):
    binding = load(root / 'input_binding.json')
    article = article_path.read_text(encoding='utf8').replace('\f','\n[Page break]\n')
    request = load(HERE / 'development_requests.json')[request_key]
    assert binding['article_sha256'] == digest(article_path) and binding['research_request'] == request
    assert binding['instructions_sha256'] == digest(Path(author.__file__))
    base = ['Research request\n' + request, 'Full article\n' + article]
    prior = ['Your pre-execution scientific design\n' + json.dumps(load(root / 'design.json')), author.BUILD]
    review = ['Your initial submission\n' + json.dumps(load(root / 'build.json')),
              'Your generated-only diagnostics\n' + json.dumps(load(root / 'trial_public.json')), author.REVIEW]
    expected = [base + [author.DESIGN], base + prior, base + prior + review]
    folders = sorted((root / 'episodes/development/calls').glob('*'))
    assert len(folders) == len(expected)
    rows = []
    for stage, folder, content in zip(author.STAGES, folders, expected):
        request_path, receipt_path = folder / 'request.json', folder / 'receipt.json'
        body, receipt = load(request_path), load(receipt_path)
        assert body['input'] == '\n\n'.join(content) and body['instructions'] == author.SYSTEM
        assert body.get('tools', []) == [] and 'previous_response_id' not in body
        assert body['model'] == receipt['returned_model'] == binding['model']
        assert receipt['status'] == 'received' and receipt['request_sha256'] == digest(request_path)
        assert receipt['response_raw_sha256'] == digest(folder / 'response_raw.json')
        assert receipt['reservation_sha256'] == digest(folder / 'reservation.json')
        usage = receipt['usage']
        rows.append(dict(stage=stage, model=receipt['returned_model'], request_sha256=digest(request_path),
                         response_sha256=receipt['response_raw_sha256'], input_tokens=usage['input_tokens'],
                         output_tokens=usage['output_tokens'], tariff_cost_usd=receipt['tariff_cost_usd']))
    return dict(article_sha256=binding['article_sha256'], captures_verified=len(rows), calls=rows,
                model=binding['model'], episode_cap_usd=binding['episode_usd_cap'],
                cost_basis='recorded token use and project tariff, not invoice',
                total_tariff_usd=sum(r['tariff_cost_usd'] for r in rows))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('article', type=Path)
    p.add_argument('case')
    p.add_argument('output', type=Path)
    args = p.parse_args()
    result = verify(args.root, args.article, args.case)
    with args.output.open('x', encoding='utf8') as f:
        json.dump(result, f, indent=2, allow_nan=False)

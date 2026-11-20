"""Replay: python run.py replay. Only aggregate records are released."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import scipy

import source_model
from compare import compare


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.parent / "chns_iron_conditional_holdout_2026-11-19"
ARTICLE = HERE.parent / "original_paper_capability_2026-11-17/private_sources/iron_original.layout.txt"
sys.path.insert(0, str(OLD))
from science import FE, HB, SEEDS, measures

N = 12_000
INPUTS = [*(HERE / f for f in ["PROTOCOL.md", "source_model.py", "compare.py", "run.py"]),
          OLD / "A_TABLES.json", OLD / "science.py"]


def get(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write("\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text_hash(path):
    return digest(path.read_text(encoding="utf-8").encode("utf-8"))


def bound():
    return {f.relative_to(ROOT).as_posix(): text_hash(f) for f in INPUTS}


def now():
    return datetime.now(timezone.utc).isoformat()


def freeze():
    receipt = get(OLD / "FREEZE.json")
    article_hash = digest(ARTICLE.read_bytes())
    assert receipt["article_layout_sha256"] == article_hash
    assert SEEDS == [191901, 191903, 191909]
    write_new(HERE / "FREEZE.json", {"utc": now(), "design": "retrospective: B had previously been revealed",
         "inputs_lf_sha256": bound(), "original_article_doi": "10.1024/0300-9831/a000014",
         "original_article_layout_sha256": article_hash, "article_role": "setting and definitions; A tables supply numeric fit",
         "seeds": SEEDS, "rows_per_seed": N, "python": sys.version.split()[0],
         "scipy": scipy.__version__, "numpy": np.__version__, "pandas": pd.__version__})


def frozen():
    f = get(HERE / "FREEZE.json")
    assert f["inputs_lf_sha256"] == bound() and f["seeds"] == SEEDS and f["rows_per_seed"] == N


def independent_check(frame, score):
    h, f = frame[HB], frame[FE]
    empirical_rank = h.rank(method="average").corr(f.rank(method="average"))
    low_h, low_f = h < 12, f < 15
    cells = [int(((low_h == h_status) & (low_f == f_status)).sum()) for h_status, f_status in
             [(True, True), (True, False), (False, True), (False, False)]]
    assert min(cells) > 0 and cells == score["cells"] and sum(cells) == len(frame)
    assert math.isclose(empirical_rank, score["rank"], abs_tol=1e-12)
    assert math.isclose(cells[0] * cells[3] / (cells[1] * cells[2]), score["odds_ratio"])


def endpoints(frame):
    all_stats = measures(frame)
    independent_check(frame, all_stats)
    return {k: all_stats[k] for k in ("n", "cells", "odds_ratio", "rank", "groups")}


def source_run(archive):
    frozen()
    tables = get(OLD / "A_TABLES.json")
    bands = source_model.fit(tables)
    population = source_model.population(bands, tables)
    runs, frames = [], []
    for seed in SEEDS:
        frame = source_model.draw(bands, seed, N)
        raw = frame.to_csv(index=False, float_format="%.17g", lineterminator="\n").encode("utf-8")
        if archive:
            folder = HERE / "private"
            folder.mkdir(exist_ok=True)
            with (folder / f"draw-{seed}.csv").open("xb") as f:
                f.write(raw)
        runs.append({"seed": seed, "csv_sha256": digest(raw), **endpoints(frame)})
        frames.append(frame)
    return {"freeze_lf_sha256": text_hash(HERE / "FREEZE.json"), "population": population,
            "runs": runs, "pooled": endpoints(pd.concat(frames, ignore_index=True))}


def score():
    frozen()
    sealed = get(HERE / "SOURCE_RESULTS.json")
    assert sealed["results"]["freeze_lf_sha256"] == text_hash(HERE / "FREEZE.json")
    refs = [OLD / "RESULTS.json", OLD / "RANK_COMPONENTS.json"]
    results = compare(sealed["results"], get(OLD / "A_TABLES.json"), *(get(f) for f in refs))
    return {"source_seal_lf_sha256": text_hash(HERE / "SOURCE_RESULTS.json"),
            "archived_reference_hashes_lf_sha256": {p.name: text_hash(p) for p in refs}, "results": results}


def same_numbers(a, b):
    if isinstance(a, dict):
        assert a.keys() == b.keys(), "Dictionary structure differs"
        for k in a:
            if k != "csv_sha256":
                same_numbers(a[k], b[k])
    elif isinstance(a, list):
        assert len(a) == len(b)
        for i,j in zip(a,b):
            same_numbers(i,j)
    elif isinstance(a, float):
        assert math.isclose(a, b, abs_tol=1e-10, rel_tol=1e-10), (a, b)
    else:
        assert a == b, (a, b)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("step", choices=["freeze", "generate", "score", "replay"])
    step = parser.parse_args().step
    if step == "freeze":
        freeze()
    elif step == "generate":
        results = source_run(archive=True)
        write_new(HERE / "SOURCE_RESULTS.json", {"sealed_utc": now(), "results": results})
    elif step == "score":
        comparison = score()
        write_new(HERE / "RESULTS.json", {"scored_utc": now(), **comparison})
    else:
        generated = source_run(archive=False)
        saved = get(HERE / "SOURCE_RESULTS.json")["results"]
        same_numbers(generated, saved)
        current, archived = score(), get(HERE / "RESULTS.json")
        same_numbers(current, {k: archived[k] for k in current})
        exact = sum(x["csv_sha256"] == y["csv_sha256"] for x, y in zip(generated["runs"], saved["runs"]))
        print(f"Replayed three draws; {exact}/3 exact file hashes on this installation; source and comparison numerics verified.")


if __name__ == "__main__":
    main()

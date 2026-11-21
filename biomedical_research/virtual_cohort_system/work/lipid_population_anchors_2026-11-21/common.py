"""Files and measures for the locked lipid marginal-evidence comparison."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PRIVATE = HERE / "private"
OLD = HERE.parent / "nonhdl_external_2026-11-20"
ALT = HERE.parent / "kdd_v40_pairing_review_2026-11-20"
PREVIOUS = HERE.parent / "prospective_lipid_use_2026-11-21"
sys.path.insert(0, str(OLD))
import science as source
sys.path.insert(0, str(PREVIOUS))
from design import USES, estimands, interval_class

NAMES = tuple(USES)
SLOTS = tuple(f"author{i}" for i in range(1, 5))
PERIODS = {"J": 2017, "L": 2021}
AGE_MASS = np.array([.396579, .371795, .231626])
STUDY_SEEDS = (41117, 41123)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if read(path) != data:
            raise FileExistsError(f"Different sealed result at {path.name}")
        return
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, allow_nan=False, ensure_ascii=False, indent=2)
        f.write("\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_hash(path):
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def pairings():
    tc, hdl = source.values()
    original = read(OLD / "MODEL_CLOSURE.json")["arms"]["agent"]["runs"]
    nominal = []
    for draw in original:
        path = OLD / "private" / f"agent-{draw['seed']}.npy"
        assert digest(path) == draw["array_sha256"]
        t, h = np.load(path, allow_pickle=False).T
        order = np.searchsorted(hdl, h)
        assert np.array_equal(tc, t) and np.array_equal(hdl[order], h)
        nominal.append(order)
    yields = {"nominal": nominal}
    for name, author in read(ALT / "SENSITIVITY.json")["authors"].items():
        for case, rows in author["runs"].items():
            orderings = []
            for draw in rows:
                f = ALT / "private/draws" / name / case / str(draw["seed"]) / "perm.npy"
                assert digest(f) == draw["permutation_hash"]
                orderings.append(np.load(f, allow_pickle=False))
            yields[f"{name}_{case}"] = orderings
    assert len(yields) == 9
    for runs in yields.values():
        assert len(runs) == 3
        assert all(np.array_equal(np.sort(ix), np.arange(len(tc))) for ix in runs)
    return yields


def check_grid(grid):
    assert grid.ndim == 2 and grid.shape[1] == 2
    assert np.isfinite(grid).all() and np.all(grid > 0) and np.all(np.diff(grid, axis=0) > 0)


def measures(grid, orders):
    tc, hdl = grid.T
    t = np.tile(tc, len(orders))
    h = np.concatenate([hdl[index] for index in orders])
    coefficient = estimands(t, h)
    return {"values": dict(zip(NAMES, map(float, coefficient))), "n": len(t),
            "hdl_above_tc": int(np.count_nonzero(h > t))}

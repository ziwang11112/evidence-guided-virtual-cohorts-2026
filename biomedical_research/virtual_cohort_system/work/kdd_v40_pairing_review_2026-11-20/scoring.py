"""Source-only checks for two candidate assignments on the same fixed margins."""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "nonhdl_external_2026-11-20"
SEEDS = (40937, 40949, 40961)
SLOTS = ("author1", "author2", "author3", "author4")
SCENARIOS = ("a", "b")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def score(tc, hdl, index):
    ix = np.asarray(index)
    if ix.shape != tc.shape or not np.issubdtype(ix.dtype, np.integer):
        raise ValueError("Wrong index shape or data type")
    if not np.array_equal(np.sort(ix), np.arange(len(tc))):
        raise ValueError("Indices do not form a permutation")
    h = hdl[ix]
    counts = int(np.count_nonzero(tc - h >= 160.0))
    return {"n": len(ix), "mean": float(np.mean(tc - h)), "tail_count": counts,
            "percent": 100.0 * counts / len(ix), "mean_ratio": float(np.mean(tc / h)),
            "invalid_order": int(np.count_nonzero(h > tc))}


def scenario_summary(runs):
    valid = [r["score"] for r in runs if "score" in r]
    failures = [r.get("reason", "missing score") for r in runs if "score" not in r]
    if len(valid) != len(SEEDS):
        return {"pass": False, "completed": len(valid), "failures": failures or ["incomplete"]}
    n = sum(r["n"] for r in valid)
    ratio = sum(r["mean_ratio"] * r["n"] for r in valid) / n
    bad = sum(r["invalid_order"] for r in valid)
    if bad:
        failures.append("HDL exceeded TC")
    if any(abs(r["mean_ratio"] - 3.66) > .02 + 1e-12 for r in valid):
        failures.append("individual-seed ratio")
    if not 3.655 <= ratio < 3.665:
        failures.append("pooled ratio")
    return {"pass": not failures, "completed": len(valid), "failures": failures,
            "n": n, "mean_ratio": ratio, "invalid_order": bad,
            "percent": 100 * sum(r["tail_count"] for r in valid) / n,
            "mean": sum(r["mean"] * r["n"] for r in valid) / n}


def author_summary(runs):
    summary = {mode: scenario_summary(runs.get(mode, [])) for mode in SCENARIOS}
    eligible = all(x["pass"] for x in summary.values())
    out = {"scenarios": summary, "both_pass": eligible, "material": False}
    if all("percent" in summary[s] for s in SCENARIOS):
        difference = summary["b"]["percent"] - summary["a"]["percent"]
        paired = [b["score"]["percent"] - a["score"]["percent"]
                  for a,b in zip(runs["a"],runs["b"],strict=True)]
        out.update(gap_pp=abs(difference), signed_b_minus_a_pp=difference, seed_gaps_pp=paired)
        out["material"] = bool(eligible and abs(difference) > 4 and
                               all(np.sign(difference)*delta > 2 for delta in paired))
    return out

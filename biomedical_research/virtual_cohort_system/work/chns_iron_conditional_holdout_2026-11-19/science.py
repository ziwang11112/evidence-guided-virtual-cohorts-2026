"""Common scientific analyses and paired, province-stratified cluster bootstrap."""
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from scipy.stats import spearmanr

HB = "hb_g_dl"
FE = "ferritin_ug_l"
SEEDS = [191901, 191903, 191909]
BOOT = 2000


def check(test, why):
    if not test:
        raise ValueError(why)


def finite_or_none(x):
    return float(x) if np.isfinite(x) else None


def measures(frame, include_rank=True):
    h, f = (frame[k].to_numpy(dtype=float) for k in (HB, FE))
    check(len(frame) and np.isfinite(h).all() and np.isfinite(f).all() and min(h.min(), f.min()) > 0, "Invalid measurements")
    a, b = h < 12, f < 15
    cells = [int(x.sum()) for x in (a & b, a & ~b, ~a & b, ~a & ~b)]
    odds = (cells[0] * cells[3]) / (cells[1] * cells[2]) if min(cells) else None
    lo, hi = (h >= 12) & (h < 13), (h >= 13) & (h < 14)
    ratio = np.exp(np.log(f[hi]).mean() - np.log(f[lo]).mean()) if hi.any() and lo.any() else None
    groups = []
    for mask in (a, (h >= 12) & (h < 14), h >= 14):
        n = int(mask.sum())
        g = np.log(f[mask])
        groups.append(dict(n=n, fraction=n / len(h), depleted=int((b & mask).sum()),
                           depletion_fraction=float(b[mask].mean()) if n else None,
                           hb_mean=float(h[mask].mean()) if n else None, hb_sd=float(h[mask].std(ddof=1)) if n > 1 else None,
                           ferritin_gm=float(np.exp(g.mean())) if n else None, ferritin_gsd=float(np.exp(g.std(ddof=1))) if n > 1 else None))
    return dict(n=len(frame), cells=cells, odds_ratio=odds, rank=finite_or_none(spearmanr(h, f).statistic) if include_rank else None,
                ratio=float(ratio) if ratio is not None else None, groups=groups, fine_band_n=[int(lo.sum()), int(hi.sum())])


def cluster_replicates(frame, seed):
    # Index labels are rebuilt by position before resampling whole communities.
    d = frame.reset_index(drop=True)
    strata = [[np.asarray(idx, dtype=int) for idx in sub.groupby("commid", sort=True).groups.values()]
              for _, sub in d.groupby("t1", sort=True)]
    check(all(len(s) >= 2 for s in strata), "A province has fewer than two communities")
    rng = np.random.default_rng(seed)
    for _ in range(BOOT):
        yield np.concatenate([s[j] for s in strata for j in rng.integers(len(s), size=len(s))])


def bootstrap_values(frame, seed, only_ratio=False):
    h, f = (frame[k].to_numpy() for k in (HB, FE))
    results = []
    for idx in cluster_replicates(frame, seed):
        x, y = h[idx], f[idx]
        if only_ratio:
            ix = (x >= 12) & (x < 13)
            jx = (x >= 13) & (x < 14)
            results.append(np.exp(np.log(y[jx]).mean() - np.log(y[ix]).mean()) if ix.any() and jx.any() else np.nan)
        else:
            u, v = x < 12, y < 15
            cells = [np.sum(u & v), np.sum(u & ~v), np.sum(~u & v), np.sum(~u & ~v)]
            odds = cells[0]*cells[3]/(cells[1]*cells[2]) if min(cells) else np.nan
            results.append([np.corrcoef(rankdata(x), rankdata(y))[0, 1], odds])
    return np.asarray(results)


def interval(values):
    v = np.asarray(values, dtype=float)
    if np.isfinite(v).sum() < 0.95 * len(v):
        return None
    return list(map(float, np.nanquantile(v, [.025, .975])))

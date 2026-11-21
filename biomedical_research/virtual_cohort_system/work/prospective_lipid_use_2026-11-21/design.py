"""Frozen scientific uses and numerical estimators; all percentages are on a 0–100 scale."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

import numpy as np
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "nonhdl_external_2026-11-20"
SENS = HERE.parent / "kdd_v40_pairing_review_2026-11-20"
PRIVATE = HERE / "private"
USES = {
    "mean_nonhdl": ("Mean total minus HDL cholesterol", "mg/dL", 10., "nonhdl_mean"),
    "mean_ratio": ("Mean of each person's TC/HDL", "ratio", .30, "mean_individual_ratio"),
    "tc_high": ("Percentage with TC at least 6.2 mmol/L", "%", 5., "tc_high_pct"),
    "hdl_low": ("Percentage with HDL below 1.0 mmol/L", "%", 5., "hdl_low_pct"),
    "nonhdl160": ("Percentage with TC minus HDL at least 160 mg/dL", "%", 2., None),
    "rank_tc_hdl": ("Spearman correlation of TC with HDL", "correlation", .10, None),
}
KEYS = list(USES)
BOOT = 4000
BOOT_SEEDS = {"all": 711209, "Buckingham": 711211, "Louisa": 711217}
COVER = 2


def read(p):
    return Path(p).read_text(encoding="utf-8")


def obj(p):
    return json.loads(read(p))


def save(p, value):
    with Path(p).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def text_digest(p):
    return hashlib.sha256(read(p).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def estimands(tc, hdl):
    """Calculate all analyses along the last axis, including average ties for rank."""
    t, h = np.asarray(tc, dtype=float), np.asarray(hdl, dtype=float)
    if t.shape != h.shape or not np.isfinite(t).all() or not np.isfinite(h).all() or (h <= 0).any() or (t <= 0).any():
        raise ValueError("Finite, positive, paired observations required")
    r1, r2 = rankdata(t, axis=-1), rankdata(h, axis=-1)
    r1 -= r1.mean(axis=-1, keepdims=True)
    r2 -= r2.mean(axis=-1, keepdims=True)
    denom = np.sqrt((r1*r1).sum(axis=-1) * (r2*r2).sum(axis=-1))
    if (denom <= 0).any():
        raise ValueError("Undefined rank correlation")
    return np.stack(((t-h).mean(axis=-1), (t/h).mean(axis=-1), 100*(t >= 6.2*38.67).mean(axis=-1),
                     100*(h < 38.67).mean(axis=-1), 100*(t-h >= 160.).mean(axis=-1),
                     (r1*r2).sum(axis=-1)/denom), axis=-1)


def interval_class(delta_low, delta_high, tolerance):
    if delta_low > tolerance or delta_high < -tolerance:
        return "contradicted"
    if delta_low >= -tolerance and delta_high <= tolerance:
        return "within"
    return "unresolved"


def bootstrap_draws(strata, seed):
    """Stratified participant resampling, conditioning on the represented county composition."""
    rng = np.random.default_rng(seed)
    chunks = []
    for offset in range(0, BOOT, 100):
        reps = min(100, BOOT-offset)
        sampled = [group[rng.integers(len(group), size=(reps, len(group)))] for group in strata]
        batch = np.concatenate(sampled, axis=1)
        chunks.append(estimands(batch[..., 0], batch[..., 1]))
    return np.concatenate(chunks)

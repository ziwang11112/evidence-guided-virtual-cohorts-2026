"""Check published sample counts and scientific summaries from aggregate files only."""
import json
from collections import Counter
from math import isclose
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "bilateral_grip_transfer_2026-11-21"
CELLS = ("F50", "F60", "M50", "M60")
PRIMARY = ("US_NHANES", "ZA_HAALSI")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def close(a, b):
    assert isclose(a, b, rel_tol=1e-10, abs_tol=1e-10), (a, b)


def main():
    inventory = read(HERE / "COVERAGE.json")
    frame = inventory["measured_comparisons"]
    counts = inventory["counts"]
    assert Counter(r["domain"] for r in frame) == dict(Lifestyle=1, Pressure=2, Iron=4, Lipids=5, Handgrip=3)
    assert len({(r["domain"], r["recruitment_period"]) for r in frame}) == len(frame) == counts["domain_sample_evaluations"]
    for field, count in (("domain", "analysis_families"), ("recruitment_period", "recruitment_periods"),
                         ("study_family", "study_families"), ("country", "countries")):
        assert len({r[field] for r in frame}) == counts[count]
    for batch in frame + inventory["constructor_batches"]:
        assert (HERE.parent / batch["receipt"]).is_file(), batch["receipt"]
    assert len(inventory["constructor_batches"]) == counts["named_constructor_batches"]
    for count in ("initial_sessions", "seeded_model_outputs"):
        assert sum(r[count] for r in inventory["constructor_batches"]) == counts[count]

    replay = read(HERE / "GRIP_GROUPS.json")
    original_models = read(ORIGINAL / "PREDICTIONS.json")["methods"]
    original_sites = read(ORIGINAL / "RESULTS.json")["reference"]
    assert replay["thresholds_kg"] == list(range(13))
    models, sites = replay["method_scores"], replay["measured"]
    assert models.keys() == original_models.keys() and sites.keys() == original_sites.keys()
    for name, rows in models.items():
        sealed = original_models[name]["values"]
        close(rows["standardized"]["mean_gap_kg"], sealed["mean_abs_gap_kg"])
        close(rows["standardized"]["tail_pct"][5], sealed["gap_at_least_5_pct"])
    assert all(models[name] == models["M1"] for name in ("M2", "M3", "M4"))

    errors, gains, interval_passes = [], [], []
    for name, site in sites.items():
        rows = site["groups"]
        pooled = rows["standardized"]
        assert sum(rows[k]["n"] for k in CELLS) == pooled["n"] == original_sites[name]["qc"]["eligible_bilateral"]
        close(pooled["mean_gap_kg"], mean(rows[k]["mean_gap_kg"] for k in CELLS))
        for i, rate in enumerate(pooled["tail_pct"]):
            close(rate, mean(rows[k]["tail_pct"][i] for k in CELLS))
        old = original_sites[name]["estimates"]
        close(pooled["mean_gap_kg"], old["mean_abs_gap_kg"]["estimate"])
        close(pooled["tail_pct"][5], old["gap_at_least_5_pct"]["estimate"])
        for actual, expected in zip(pooled["mean_gap_ci"], old["mean_abs_gap_kg"]["ci"], strict=True):
            close(actual, expected)
        for k in CELLS:
            r = rows[k]
            m = models["M1"][k]["mean_gap_kg"]
            error = abs(m - r["mean_gap_kg"])
            gain = abs(models["independent"][k]["mean_gap_kg"] - r["mean_gap_kg"]) - error
            close(m - r["mean_gap_kg"], r["agent_minus_measured_kg"])
            close(gain, r["independent_error_minus_agent_error_kg"])
            if name in PRIMARY:
                errors.append(error)
                gains.append(gain)
                interval_passes.append(max(abs(m - end) for end in r["mean_gap_ci"]) <= 1)
    for record in [*models.values(), *(site["groups"] for site in sites.values())]:
        for row in record.values():
            tail = row["tail_pct"]
            close(tail[0], 100)
            assert len(tail) == 13 and min(tail) >= 0 and all(a >= b - 1e-10 for a, b in zip(tail, tail[1:]))
    assert len(gains) == 8 and min(gains) > 0 and sum(interval_passes) == 7
    assert (round(min(errors), 2), round(max(errors), 2)) == (0.04, 0.77)
    assert (round(min(gains), 2), round(max(gains), 2)) == (2.50, 4.99)
    print("Verified all public inventory receipts, three pooled survey results and twelve subgroup comparisons.")


if __name__ == "__main__":
    main()

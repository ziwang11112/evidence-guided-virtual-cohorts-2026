"""Replay archived hand pairings and measured survey operators. Export aggregates only."""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import t

HERE = Path(__file__).resolve().parent
GRIP = HERE.parent / "bilateral_grip_transfer_2026-11-21"
sys.path.insert(0, str(GRIP))
import reference
from science import CELLS, EPS, SEEDS, independent, read, rule_permutation, sha, source_grids

THRESHOLDS = np.arange(13)
GROUPS = (*CELLS, "standardized")


def within_group_values(gap):
    return np.column_stack((gap, 100 * (gap[:, None] >= THRESHOLDS - EPS)))


def plus_standardized(groups):
    return np.vstack((groups, np.mean(groups, axis=0)))


def paired_scores(grids, orders):
    groups = []
    for (_, right, left), order in zip(grids, orders, strict=True):
        np.testing.assert_array_equal(np.sort(order), np.arange(len(left)))
        groups.append(within_group_values(np.abs(right - left[order])).mean(axis=0))
    return plus_standardized(groups)


def random_pair_scores(grids):
    groups = []
    for g in grids:
        _, right, left = g
        rates = [100.]
        for cutoff in THRESHOLDS[1:]:
            lower = np.searchsorted(left, right - cutoff + EPS, side="right")
            upper = len(left) - np.searchsorted(left, right + cutoff - EPS, side="left")
            rates.append(100 * np.mean(lower + upper) / len(left))
        groups.append([independent([g])[0], *rates])
    return plus_standardized(groups)


def pack_scores(matrix):
    return {group: {"mean_gap_kg": float(row[0]), "tail_pct": row[1:].tolist()}
            for group, row in zip(GROUPS, matrix, strict=True)}


def virtual_scores():
    sealed = read(GRIP / "PREDICTIONS.json")["methods"]
    grids = source_grids()
    methods = {"independent": random_pair_scores(grids)}
    methods["ratio_rule"] = np.mean(
        [paired_scores(grids, rule_permutation(grids, seed)[0]) for seed in SEEDS], axis=0)
    verified = 0
    for name, item in sealed.items():
        if "draws" not in item:
            continue
        runs = []
        assert [draw["seed"] for draw in item["draws"]] == list(SEEDS)
        for draw in item["draws"]:
            path = GRIP / "private" / "runs" / name / str(draw["seed"]) / "perm.npy"
            assert sha(path) == draw["permutation_sha256"]
            runs.append(paired_scores(grids, np.load(path, allow_pickle=False)))
            verified += 1
        methods[name] = np.mean(runs, axis=0)
    assert verified == 24 and set(methods) == set(sealed)
    for name, matrix in methods.items():
        original = sealed[name]["values"]
        np.testing.assert_allclose(matrix[-1, [0, 6]],
                                   [original["mean_abs_gap_kg"], original["gap_at_least_5_pct"]], atol=1e-10)
        assert np.all(np.diff(matrix[:, 1:], axis=1) <= 1e-9)
        if name in ("M2", "M3", "M4"):
            np.testing.assert_array_equal(matrix, methods["M1"])
    return {name: pack_scores(matrix) for name, matrix in methods.items()}, verified


def summarize_cells(values, group, weights):
    result = []
    for cell in range(len(CELLS)):
        use = (group == cell) & (weights > 0)
        if not use.any():
            raise ValueError(f"Empty survey replicate for {CELLS[cell]}")
        result.append(np.average(values[use], weights=weights[use], axis=0))
    return plus_standardized(result)


def survey_scores(frame, design):
    values = within_group_values(np.abs(frame.r.to_numpy() - frame.l.to_numpy()))
    group, weights = frame.cell.to_numpy(), frame.w.to_numpy()
    st, psu = frame.stratum.to_numpy(), frame.psu.to_numpy()
    point = summarize_cells(values, group, weights)
    variance = np.zeros_like(point)
    df = 0
    for stratum, block in design.groupby("stratum", sort=False):
        units = block.psu.unique()
        m = len(units)
        assert m > 1
        replicates = []
        for unit in units:
            w = weights.copy()
            w[st == stratum] *= m / (m - 1)
            w[(st == stratum) & (psu == unit)] = 0
            replicates.append(summarize_cells(values, group, w))
        reps = np.stack(replicates)
        variance += (m - 1) / m * ((reps - reps.mean(axis=0)) ** 2).sum(axis=0)
        df += m - 1
    half = t.ppf(.975, df) * np.sqrt(variance)
    return point, half, df


def check_grip_means_from_cluster_totals(frame, design, point, half):
    """An independent delete-cluster calculation on numerator and denominator totals."""
    data = frame.assign(gap_mass=frame.w * (frame.r - frame.l).abs())
    cols = ["gap_mass", "w"]
    index = list(range(len(CELLS)))
    def totals(part):
        return part.groupby("cell")[cols].sum().reindex(index, fill_value=0).to_numpy()
    total = totals(data)
    mean = total[:, 0] / total[:, 1]
    var = np.zeros_like(mean)
    df = 0
    for name, block in design.groupby("stratum"):
        sample = data[data.stratum == name]
        subtotal = totals(sample)
        units = block.psu.unique()
        m = len(units)
        replicates = []
        for unit in units:
            deleted = totals(sample[sample.psu == unit])
            new = total - subtotal + (subtotal - deleted) * m / (m - 1)
            replicates.append(new[:, 0] / new[:, 1])
        var += (m - 1) * np.var(replicates, axis=0, ddof=0)
        df += m - 1
    np.testing.assert_allclose(mean, point[:-1, 0], atol=1e-10)
    np.testing.assert_allclose(t.ppf(.975, df) * np.sqrt(var), half[:-1, 0], atol=1e-10)


def run():
    original = read(GRIP / "RESULTS.json")["reference"]
    # Refuse to invoke a loader that would otherwise download a missing participant file.
    inputs = {"DEMO_G.xpt": GRIP / "private/DEMO_G.xpt", "MGX_G.xpt": GRIP / "private/MGX_G.xpt",
              "HAALSI_v3_orig.dta": reference.HAALSI, "EDOC_S1.sav": reference.RIO}
    for site in original.values():
        for name, meta in site["qc"]["input_files"].items():
            assert sha(inputs[name]) == meta["sha256"]
    virtual, checked = virtual_scores()
    sites = {}
    for site, load_site in reference.STUDIES.items():
        frame, design, meta = load_site()
        previous = original[site]
        np.testing.assert_array_equal(meta["n_by_cell"], previous["qc"]["n_by_cell"])
        point, half, df = survey_scores(frame, design)
        check_grip_means_from_cluster_totals(frame, design, point, half)
        assert df == previous["design_df"]
        for measure, col in (("mean_abs_gap_kg", 0), ("gap_at_least_5_pct", 6)):
            old = previous["estimates"][measure]
            np.testing.assert_allclose(point[-1, col], old["estimate"], atol=1e-10)
            np.testing.assert_allclose(point[-1, col] + np.array([-1., 1.]) * half[-1, col],
                                       old["ci"], atol=1e-10)
        assert np.all(np.diff(point[:, 1:], axis=1) <= 1e-9)
        scores = pack_scores(point)
        for j, group in enumerate(GROUPS):
            record = scores[group]
            y = record["mean_gap_kg"]
            record["n"] = meta["n_by_cell"][j] if group != "standardized" else len(frame)
            record["mean_gap_ci"] = [float(y - half[j, 0]), float(y + half[j, 0])]
            record["tail_ci_halfwidth_pp"] = half[j, 1:].tolist()
            pred = virtual["M1"][group]["mean_gap_kg"]
            random = virtual["independent"][group]["mean_gap_kg"]
            record["agent_minus_measured_kg"] = pred - y
            record["independent_error_minus_agent_error_kg"] = abs(random - y) - abs(pred - y)
            record["absolute_discrepancy_within_1kg_at_point"] = abs(pred - y) <= 1
        sites[site] = {"design_df": df, "groups": scores}
    output = {"scope": "Retrospective replay after all site-level outcomes were known.",
              "thresholds_kg": THRESHOLDS.tolist(), "method_scores": virtual, "measured": sites,
              "verification": {"source_permutation_hashes_matched": checked,
                               "site_pooled_means_and_5kg_rates_and_intervals_reproduced": len(sites),
                               "subgroup_means_and_intervals_cross_checked": len(sites) * len(CELLS)}}
    (HERE / "GRIP_GROUPS.json").write_text(
        json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n"
    )
    for site, record in sites.items():
        print(site, [(g, round(record["groups"][g]["agent_minus_measured_kg"], 2),
                     round(record["groups"][g]["independent_error_minus_agent_error_kg"], 2)) for g in CELLS])


if __name__ == "__main__":
    run()

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from evaluate_trial import (FIELDS, SEEDS, assess_slot, estimates, measurement_pairs,
                            rounded_source_tables, sha)


def artificial_draw(folder, seed, r, m):
    path = folder / f"{seed}.csv"
    pd.DataFrame({"row_id": range(len(r)), "reported_bmi": r, "measured_bmi": m}).to_csv(path, index=False)
    return {"seed": seed, "path": path, "status": "success", "sha256": sha(path)}


def test_source_table_integer_identification():
    tables = rounded_source_tables()
    assert len(tables) == 1
    assert tables[0]["cells"] == [8, 0, 4, 79]
    assert 0.7755 <= tables[0]["kappa"] < 0.7765
    assert not rounded_source_tables(kappa=0.775)


def test_strict_tail_sign_tie_and_cells():
    r = [29., 30., 32., 21., 24. - 1e-12]
    m = [32., 26., 35., 23., 26.]
    o = estimates(r, m, bootstrap=True)
    assert o["joint_cells"] == [1, 1, 1, 2]
    assert o["tail_count"] == 2 and o["threshold_ties"] == 2
    assert o["signed_mean"] == pytest.approx(-1.2)
    assert o["paired_participant_bootstrap"] == estimates(r, m, bootstrap=True)["paired_participant_bootstrap"]


def test_source_exact_match_and_kappa_margin():
    r = np.r_[np.repeat(31., 8), np.repeat(25., 4), np.repeat(25., 79)]
    m = np.r_[np.repeat(32., 8), np.repeat(34., 4), np.repeat(27., 79)]
    assert estimates(r, m)["source_joint_tv_pp"] == 0


def test_hash_and_seed_failure_cannot_pass(tmp_path):
    reference = estimates([20, 31, 23, 34], [24, 33, 23, 35])
    slots = [artificial_draw(tmp_path, s, [20, 31, 23, 34], [24, 33, 23, 35]) for s in SEEDS]
    assert assess_slot(slots, reference)["both"]
    bad = [{"seed": SEEDS[0], "status": "failed", "path": None}, *slots[1:]]
    assert not assess_slot(bad, reference)["both"]
    bad = [dict(slots[0], sha256="different"), *slots[1:]]
    with pytest.raises(ValueError, match="hash"):
        assess_slot(bad, reference)
    with pytest.raises(ValueError, match="seed"):
        assess_slot(slots[:2], reference)


def test_age_complete_case_and_units():
    frame = pd.DataFrame({
        FIELDS["age"]: [17, 19, 20, 21], FIELDS["online_height"]: [200, 200, 200, 200],
        FIELDS["online_mass"]: [80, 80, 84, np.nan], FIELDS["online_bmi"]: [20, 20, 21, 23],
        FIELDS["measured_height"]: [200, 200, 200, 200], FIELDS["measured_mass"]: [92, 92, 100, 84],
        FIELDS["measured_bmi"]: [23, 23, 25, 21],
    })
    r, m, audit = measurement_pairs(frame)
    assert r.tolist() == [20,21] and m.tolist() == [23,25]
    assert audit["n_adult"] == 3 and audit["n_complete"] == 2
    metres = frame.copy()
    metres[FIELDS["measured_height"]] /= 100
    _, aligned, check = measurement_pairs(metres)
    assert aligned.tolist() == m.tolist()
    assert check["component_checks"]["measured"]["height_storage"].startswith("m (")
    frame.loc[1, FIELDS["online_height"]] = 0
    with pytest.raises(ValueError, match="Nonpositive"):
        measurement_pairs(frame)


def test_invalid_synthesis_stays_unavailable(tmp_path):
    slots = [artificial_draw(tmp_path, s, [20,-5], [25,25]) for s in SEEDS]
    assert not assess_slot(slots, {"tail_pct": 0, "signed_mean": 0})["both"]


def test_joint_replay_requires_every_seed(tmp_path):
    r = np.r_[np.repeat(31., 8), np.repeat(25., 4), np.repeat(25., 79)]
    m = np.r_[np.repeat(32., 8), np.repeat(34., 4), np.repeat(27., 79)]
    draws = []
    for i, s in enumerate(SEEDS):
        x = r.copy()
        if i == 2:
            x[-4:] = 32
        draws.append(artificial_draw(tmp_path, s, x, m))
    score = assess_slot(draws)
    assert score["source_joint_mean_tv_pp"] < 3 < score["source_joint_max_tv_pp"]
    assert not score["near_source_table"]



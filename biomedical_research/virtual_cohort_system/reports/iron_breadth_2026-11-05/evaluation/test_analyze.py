"""Independent artificial fixtures only."""
import numpy as np
import pandas as pd
import pytest
from scipy.special import expit, logit
from scipy.stats import spearmanr, t

from analyze import analyze_target, analyze_synthetic


def fixture():
    rows = []
    uid = 100
    for h in (1, 2):
        for k in (1, 2):
            for j, (hb, fer) in enumerate([(10, 9), (11, 30), (12, 10), (14, 15), (13, 40)]):
                uid += 1
                # Integer weights make a second, unweighted rank calculation possible.
                # All age-eligible observations in (2,2) are out of the pregnancy domain.
                rows.append((uid, 2, 32, 1 if (h,k)==(2,2) else 2, h, k,
                             hb + (j % 2)*(h-1), fer, 1+(j+h+k) % 3))
    z = pd.DataFrame(rows, columns=["SEQN","RIAGENDR","RIDAGEYR","RIDEXPRG","SDMVSTRA",
                                    "SDMVPSU","LBXHGB","LBDFERSI","WTPH2YR"])
    d = z[["SEQN","RIAGENDR","RIDAGEYR","RIDEXPRG","SDMVSTRA","SDMVPSU"]].copy()
    b = z[["SEQN","LBXHGB","WTPH2YR"]].copy()
    f = z[["SEQN","LBDFERSI","WTPH2YR"]].copy()
    # Ferritin release restricted; this PSU must remain in the CBC design frame.
    f = f.loc[~((z.SDMVSTRA == 2) & (z.SDMVPSU == 2))].copy()
    return z, d, b, f


def independent(z, w):
    sel = (z.RIDEXPRG == 2) & (w > 0)
    a = z.loc[sel].loc[z.loc[sel].index.repeat(w[sel])]
    hh = a.LBXHGB < 12
    ff = a.LBDFERSI < 15
    cells = [sum(hh & ff), sum(hh & ~ff), sum(~hh & ff), sum(~hh & ~ff)]
    return np.array([np.log(cells[0]*cells[3]/(cells[1]*cells[2])),
                     logit(cells[0]/len(a)),
                     np.arctanh(spearmanr(a.LBXHGB, a.LBDFERSI).statistic)])


def test_integer_expansion_full_design_jkn_and_weighted_rank_ties():
    z, d, b, f = fixture()
    out = analyze_target(d, b, f)
    assert out["design"]["df"] == 2
    assert out["design"]["psus"] == 4
    assert out["flow"]["eligible_with_both"] == 15
    center = independent(z, z.WTPH2YR)
    var = np.zeros(3)
    for h in (1, 2):
        for k in (1, 2):
            w = z.WTPH2YR.copy()
            w[z.SDMVSTRA == h] *= 2
            w[(z.SDMVSTRA == h) & (z.SDMVPSU == k)] = 0
            var += .5*(independent(z, w) - center)**2
    for j, (name, inv) in enumerate([("odds_ratio",np.exp),
                                     ("joint_prevalence",expit), ("spearman",np.tanh)]):
        est = out["estimands"][name]
        assert est["estimate"] == pytest.approx(inv(center[j]))
        delta = t.ppf(.975, 2) * np.sqrt(var[j])
        assert est["ci95"] == pytest.approx(inv(center[j] + np.array([-delta,delta])))


def test_synthetic_equal_weight_spearman_and_exact_boundaries():
    a = pd.DataFrame({"H":[11,11,12,12,13,13], "F":[14,15,13,15,20,20]})
    out = analyze_synthetic(a,"H","F")
    assert [c["n"] for c in out["cells"].values()] == [1,1,1,3]
    assert out["estimands"]["odds_ratio"]["estimate"] == 3
    assert out["estimands"]["joint_prevalence"]["estimate"] == pytest.approx(1/6)
    assert out["estimands"]["spearman"]["estimate"] == pytest.approx(spearmanr(a.H,a.F).statistic)


def test_tagged_missing_unmeasured_pregnancy_and_inputs():
    _, d, b, f = fixture()
    d["RIDEXPRG"] = d.RIDEXPRG.astype(object)
    d.loc[0, "RIDEXPRG"] = ".A"
    f["LBDFERSI"] = f.LBDFERSI.astype(object)
    f.iloc[1, f.columns.get_loc("LBDFERSI")] = "."
    out = analyze_target(d,b,f)
    assert out["flow"]["eligible_with_both"] == 13
    assert "one_or_more_raw_cells_below_10" in out["flags"]
    with pytest.raises(ValueError, match="duplicated"):
        analyze_target(d, pd.concat([b,b.head(1)]), f)
    f.loc[f.index[2], "WTPH2YR"] *= 2
    with pytest.raises(ValueError, match="disagree"):
        analyze_target(d,b,f)


def test_zero_cell_and_lonely_stratum_retains_descriptive_point():
    _, d, b, f = fixture()
    only = ~((d.SDMVSTRA == 2) & (d.SDMVPSU == 2))
    b.loc[b.LBXHGB < 12, "LBXHGB"] = 12
    sel = d.loc[only, "SEQN"]
    out = analyze_target(d.loc[only],b.loc[b.SEQN.isin(sel)],f.loc[f.SEQN.isin(sel)])
    assert out["design"]["lonely_stratum"]
    assert out["estimands"]["odds_ratio"]["estimate"] is None
    assert out["estimands"]["joint_prevalence"]["estimate"] == 0
    assert all(e["ci95"] is None for e in out["estimands"].values())


def test_zero_replicate_cell_suppresses_only_its_interval():
    z, d, b, f = fixture()
    ids = z.loc[(z.LBXHGB<12) & (z.LBDFERSI<15) &
                ~((z.SDMVSTRA==1) & (z.SDMVPSU==1)), "SEQN"]
    f.loc[f.SEQN.isin(ids), "LBDFERSI"] = 20
    out = analyze_target(d,b,f)
    assert out["estimands"]["odds_ratio"]["estimate"] > 0
    assert out["estimands"]["odds_ratio"]["invalid_replicates"] > 0
    assert out["estimands"]["odds_ratio"]["ci95"] is None
    assert out["estimands"]["spearman"]["ci95"] is not None

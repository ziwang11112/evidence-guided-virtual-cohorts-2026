import numpy as np
import pandas as pd
import pytest
from analysis import errors, points, preservation, require_aligned, weighted_mean, weighted_quantile


def fixture():
    frame = pd.DataFrame({"row_id":[f"r{i}" for i in range(12)],
        "age_years":[22,28,42,48,62,68]*2,
        "sex":["male"]*6+["female"]*6,
        "bmi_kg_m2":[20,30,24,28,25,31,31,23,29,22,32,24]})
    y = 4 + .2*frame.age_years/10 + .3*frame.bmi_kg_m2/5 + .4*frame.sex.eq("female")
    return frame, y.to_numpy(), np.arange(1,13,dtype=float)


def test_left_inverse_ties_and_boundary():
    assert weighted_quantile([2,1,2,4],[1,2,1,4],.5) == 2
    assert weighted_quantile([2,1,2,4],[1,2,1,4],0) == 1
    assert weighted_quantile([2,1,2,4],[1,2,1,4],1) == 4
    assert weighted_quantile([1,3],[1,1],.5) == 1


def test_weight_scaling_and_order_invariance():
    y, w = [9,1,5],[3,2,1]
    assert weighted_quantile(y,w,.5) == weighted_quantile(y[::-1],(np.array(w)*7)[::-1],.5)
    assert weighted_mean(y,w) == pytest.approx(34/6)
    assert weighted_mean(y,w) == pytest.approx(weighted_mean(y,np.array(w)*1e300))


def test_finite_large_mean_does_not_overflow():
    assert np.isfinite(weighted_mean([1e308,1e308],[1,1]))
    assert weighted_mean([1e308,1e308],[1,1]) == pytest.approx(1e308)


def test_row_permutation_rejected_before_vector_conversion():
    f,y,w=fixture()
    table=pd.DataFrame({"row_id":f.row_id,"y":y})
    require_aligned(table,f.row_id,["row_id","y"])
    with pytest.raises(ValueError,match="order"):
        require_aligned(table.iloc[::-1],f.row_id,["row_id","y"])


@pytest.mark.parametrize("y,w", [([1,np.nan],[1,1]),([1,2],[1,0]),([1,2],[1,-1]),([1],[1,2]),([],[])])
def test_invalid_values_rejected(y,w):
    with pytest.raises(ValueError): weighted_quantile(y,w,.5)


def test_exact_wls_and_cells():
    f,y,w = fixture()
    p=points(f,y,w)
    for k,v in {"intercept":4,"age_per_10y":.2,"bmi_per_5":.3,"female_offset":.4}.items():
        assert p[k] == pytest.approx(v,abs=1e-12)
    assert p["mean_male_20_39"] == pytest.approx((y[0]+2*y[1])/3)
    assert p["mean_female_60_79_n"] == 2
    assert errors(p,p)["sex_median_mae"] == 0


def test_sex_location_translation_preserves_slopes():
    f,y,w=fixture()
    before=points(f,y,w)
    shift=np.where(f.sex.eq("female"),.3,-.2)
    after=points(f,y+shift,w)
    assert after["median_male"]-before["median_male"] == pytest.approx(-.2)
    assert after["median_female"]-before["median_female"] == pytest.approx(.3)
    for k in ["age_per_10y","bmi_per_5"]:
        assert after[k] == pytest.approx(before[k],abs=1e-12)
    assert errors(before,after)["sex_median_mae"] == pytest.approx(.25)


def test_missing_cell_remains_unassessed():
    f,y,w=fixture(); keep=f.age_years.lt(60).to_numpy()
    p=points(f.loc[keep],y[keep],w[keep])
    assert p["mean_male_60_79"] is None
    assert errors(p,p)["age_sex_cell_mean_mae"] is None


def test_preservation_reports_fail_and_unassessed():
    before={"age_per_10y":.2,"bmi_per_5":None}
    after={"age_per_10y":.21,"bmi_per_5":.3}
    p=preservation(before,after)
    assert p["age_per_10y_change"] == pytest.approx(.01)
    assert p["age_per_10y_preserved"] is False
    assert p["bmi_per_5_change"] is None and p["bmi_per_5_preserved"] is None

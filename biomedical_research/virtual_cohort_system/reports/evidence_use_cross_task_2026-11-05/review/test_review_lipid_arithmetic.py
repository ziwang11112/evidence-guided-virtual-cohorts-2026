"""Independent eight-row factorial arithmetic; no clinical/reference data."""
import importlib.util
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def test_factorial_slopes_residual_correlation_and_absolute_dispersion():
    path = Path(__file__).resolve().parents[1] / "lipid_provider.py"
    loader = importlib.util.spec_from_file_location("review_lipid_provider", path)
    provider = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(provider)
    # Three orthogonal +/-1 main effects. Products a*b and a*s are also
    # mutually orthogonal and orthogonal to the four-column design.
    a, s, b = np.array(list(itertools.product([-1., 1.], repeat=3))).T
    tc = 180 + 4*a + 2*s + 6*b + 3*a*b
    hdl = 50 + 2*a + 3*s - 4*b + 2*(.6*a*b + .8*a*s)
    frame = pd.DataFrame({
        "id": ["invented-" + str(i) for i in range(8)],
        "age": 40 + 5*a,
        "sex": np.where(s > 0, "F", "M"),
        "bmi": 25 + 2*b,
        "total_cholesterol": tc / 38.67,
        "hdl_cholesterol": hdl / 38.67,
    })
    result = provider.generated_statistics(frame, expected_rows=8)
    values = {r["id"]: r for r in result["analyses"] + result["diagnostics"]}
    # Native BMI slope is 6/2 for TC, -4/2 for HDL; requested increment is 5.
    assert values["K02-TC-BMI"]["value"] == pytest.approx(15.)
    assert values["K02-HDL-BMI"]["value"] == pytest.approx(-10.)
    assert values["K02-LIPID-RESIDUAL"]["value"] == pytest.approx(.6)
    assert values["total_cholesterol.conditional_rms"]["value"] == pytest.approx(3.)
    assert values["hdl_cholesterol.conditional_rms"]["value"] == pytest.approx(2.)
    assert values["total_cholesterol.mean"]["value"] == pytest.approx(180.)
    assert values["hdl_cholesterol.mean"]["value"] == pytest.approx(50.)
    assert values["total_cholesterol.sd_sample"]["value"] == pytest.approx(np.sqrt(65*8/7))
    assert values["hdl_cholesterol.sd_sample"]["value"] == pytest.approx(np.sqrt(33*8/7))
    assert values["K02-TC-BMI"]["unit"] == "mg/dL per 5 kg/m^2"
    assert values["K02-LIPID-RESIDUAL"]["unit"] == "1"
    assert result["quality"]["reference_read"] is False

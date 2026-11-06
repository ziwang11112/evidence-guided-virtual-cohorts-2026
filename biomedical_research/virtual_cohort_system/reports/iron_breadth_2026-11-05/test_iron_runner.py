"""Artificial fixture exercises the real sandbox and both threshold boundaries."""
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

import iron_runner as runner


def test_source_and_worker():
    code = """import pandas as pd
def generate(n, rng, context):
    assert n == 6 and context == 'zhu_source'
    return pd.DataFrame({'hb_g_dl': [9, 10, 11, 12, 13, 14], 'ferritin_ug_l': [2, 4, 20, 12, 15, 32]})
"""
    with tempfile.TemporaryDirectory(dir=runner.ROOT) as scratch:
        base = Path(scratch)
        author = base / "fixture.py"
        author.write_text(code, encoding="utf8")
        run = base / "run"
        receipt = runner.run_one(author, runner.lifecycle.sha256(author), run, 6, 77, "zhu_source")
        assert receipt["status"] == "success", receipt.get("error")
        report = runner.lifecycle.read_json(run / "source_diagnostics.json")
        assert report["cells_n"] == [2, 1, 1, 2]
        assert report["crude_or"] == 4
        band = report["table_iii_hb_bands_g_dl"]["hb_10_to_lt12"]
        assert band["n"] == 2 and np.isclose(band["ferritin_geomean_ug_l"], np.sqrt(80))
        assert band["ferritin_lt15_fraction"] == 0.5
        system = runner.lifecycle.read_json(run / "output" / "worker_report.json")["pre_import_probe"]
        assert not system["mnt_visible"] and not system["home_visible"] and not system["route_table"]


def test_wrong_order_and_impossible_values():
    import pytest
    good = pd.DataFrame({"hb_g_dl": [10.0], "ferritin_ug_l": [15.0]})
    for bad in [good.iloc[:, ::-1], good.assign(hb_g_dl=np.inf), good.assign(ferritin_ug_l=0)]:
        with pytest.raises(ValueError):
            runner._validate(bad)

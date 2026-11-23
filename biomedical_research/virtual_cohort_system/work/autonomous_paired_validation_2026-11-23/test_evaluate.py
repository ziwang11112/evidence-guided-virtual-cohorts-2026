"""Synthetic-only verification for independent paired scoring."""
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np
import pandas as pd

from evaluate import evaluate, freeze, parse_table, score


def direct(col, unit="kg/m2"):
    return {"column": col, "unit": unit}


def base():
    return {"unit": "kg/m2", "threshold": -2, "id": "ID",
            "reported": direct("R"), "measured": direct("M")}


class TestPaired(unittest.TestCase):
    def test_arithmetic_ties_missing(self):
        frame = pd.DataFrame({"ID": range(6), "R": [20,20,20,20,20,np.nan],
                              "M": [23,22,22+1e-11,22+1e-8,18,17]})
        out = evaluate(frame, base())
        self.assertEqual((out["n_complete"], out["strictly_below_n"], out["ties_n"]), (5,2,2))
        self.assertEqual(out["strictly_below_pct"], 40)
        self.assertAlmostEqual(out["mean_difference"], (-7-1e-11-1e-8)/5)
        self.assertEqual(out["n_missing_reported"], 1)

    def test_height_weight_both_sides_and_bootstrap(self):
        mapping = base()
        mapping.update(reported={"height": direct("H","cm"), "weight": direct("W","kg")},
                       measured={"height": direct("I","in"), "weight": direct("L","lb")})
        frame = pd.DataFrame({"ID":[1,2,3], "H":[200,200,200], "W":[80,100,120],
                              "I": [2/.0254]*3, "L":[v/.45359237 for v in (92,112,132)]})
        out = evaluate(frame, mapping, bootstrap=True)
        self.assertEqual(out["strictly_below_n"], 3)
        self.assertTrue(np.allclose(out["paired_bootstrap"]["interval_95"]["mean_difference"],[-3,-3]))
        self.assertEqual(out["paired_bootstrap"], evaluate(frame, mapping, bootstrap=True)["paired_bootstrap"])
        mapping["reported"] = direct("R")
        frame["R"] = [20,25,30]
        self.assertAlmostEqual(evaluate(frame, mapping)["mean_difference"], -3)

    def test_generic_units_and_subset(self):
        m = {**base(), "unit":"kPa", "threshold":-0.5, "reported":direct("R","kPa"), "measured":direct("M","kPa"),
             "row_filters":[{"column":"age","op":"ge","value":18}]}
        f = pd.DataFrame({"ID":["a","b","c","d"], "age":[18,32,14,27],
                          "R":[10,10,5,10], "M":[10.5,11,9,999]})
        result = evaluate(f,{**m,"missing_values":[999]})
        self.assertEqual(result["n_removed_by_population_filters"],1)
        self.assertEqual((result["n_complete"],result["ties_n"],result["strictly_below_pct"]),(2,1,50))
        with self.assertRaisesRegex(ValueError, "analysis unit"):
            evaluate(f,{**m, "reported":direct("R","mmHg")})

    def test_explicit_id_policy_and_invalid_physiology(self):
        f = pd.DataFrame({"ID":["a","a","b"],"R":[20,np.nan,19],"M":[21,20,22]})
        with self.assertRaisesRegex(ValueError,"duplicate"):
            evaluate(f,base())
        with self.assertRaisesRegex(ValueError,"Document"):
            evaluate(f,{**base(),"id":None})
        m = {**base(),"id":None,"row_identity_basis":"Synthetic one-row-per-participant example"}
        self.assertEqual(evaluate(f,m)["n_complete"],2)
        with self.assertRaisesRegex(ValueError,"Nonpositive"):
            evaluate(f.assign(R=[-20,21,19]),m)
        with self.assertRaisesRegex(ValueError,"Identical"):
            evaluate(f,{**m,"reported":direct("M")})

    def test_frozen_input_and_mapping(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            table, spec, lock = root/"data.csv", root/"mapping.json", root/"lock.json"
            table.write_text("ID,R,M\na,20,23\nb,20,22\nc,20,19\n",encoding="utf8")
            spec.write_text(json.dumps(base()),encoding="utf-8-sig")
            freeze(table,spec,lock)
            self.assertEqual(score(table,lock)["strictly_below_n"],1)
            orig = lock.read_bytes()
            payload = json.loads(orig)
            payload["mapping"]["threshold"] = -1
            lock.write_text(json.dumps(payload),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"mapping"):
                score(table,lock)
            lock.write_bytes(orig)
            table.write_text("ID,R,M\na,20,23\nb,20,23\n",encoding="utf8")
            with self.assertRaisesRegex(ValueError,"differs"):
                score(table,lock)

    def test_single_sheet_and_duplicate_labels(self):
        m = {**base(),"sheet":"study","header_row":1}
        with BytesIO() as buf:
            with pd.ExcelWriter(buf,engine="openpyxl") as writer:
                pd.DataFrame([["test title","",""],["ID","R","M"],["a",20,23],["b",20,22]]).to_excel(
                    writer,index=False,header=False,sheet_name="study")
            frame = parse_table(buf.getvalue(),"data.xlsx",m)
        self.assertEqual(evaluate(frame,m)["strictly_below_pct"],50)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            parse_table(b"ID,R,R\na,20,23\nb,20,22\n","data.csv",base())

    def test_binary_data_formats(self):
        import pyreadstat
        df = pd.DataFrame({"ID": [1,2], "R": [20.,20.], "M": [23.,22.]})
        buf = BytesIO()
        df.to_stata(buf, write_index=False)
        self.assertEqual(evaluate(parse_table(buf.getvalue(),"data.dta",base()),base())["strictly_below_n"],1)
        with TemporaryDirectory() as name:
            path = Path(name)/"file.sav"
            pyreadstat.write_sav(df,path)
            actual = parse_table(path.read_bytes(),path.name,base())
            self.assertEqual(evaluate(actual,base())["strictly_below_n"],1)


if __name__ == "__main__":
    unittest.main()

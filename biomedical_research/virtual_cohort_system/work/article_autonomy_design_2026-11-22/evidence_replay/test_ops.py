"""Independent fixtures for evidence replay, with hand-computable answers."""
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ops import ReplayError, compute, result_unit


class TestOperators(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({"a": [1., 2., 3., 4., 6.],
                                   "b": [3., 5., 7., 9., 2.],
                                   "g": [1, 1, 1, 1, 0]})
        self.schema = {"a": "m", "b": "kg", "g": "1"}
        self.where = [{"column":"g","cmp":"eq","value":1}]

    def test_mean_sd_geometric_mean_filter_and_ddof(self):
        inputs = dict(y="a", units={"a":"m","g":"1"}, where=self.where)
        for op, answer in [(dict(kind="mean"), 2.5), (dict(kind="sd",ddof=0), np.sqrt(1.25)),
                           (dict(kind="sd",ddof=1), np.sqrt(5/3)),
                           (dict(kind="geometric_mean"), 24**.25)]:
            full = {**inputs, **op}
            estimate, n = compute(self.frame, self.schema, full)
            self.assertEqual(n, 4)
            self.assertAlmostEqual(estimate, answer)
            self.assertEqual(result_unit(full), "m")
        for delta in [{"ddof":1}, {"kind":"sd"}, {"kind":"sd","ddof":True},{"weights":"g"}]:
            with self.assertRaises(ReplayError):
                compute(self.frame,self.schema,{"kind":"mean", **inputs, **delta})

    def test_regression_direction_offset_units_and_scale(self):
        inputs = dict(x="a", y="b", units=self.schema, where=self.where)
        for full, answer, expected_unit in [
            ({**inputs,"kind":"ols_slope"},2,"kg/m"),
            ({**inputs,"x":"b","y":"a","kind":"ols_slope"},.5,"m/kg"),
            ({**inputs,"kind":"ols_intercept"},1,"kg"),
            ({**inputs,"kind":"pearson"},1,"1"),
            ({**inputs,"kind":"r_squared","scale":"percent"},100,"%"),
            ({**inputs,"kind":"r_squared","scale":"fraction"},1,"1"),
        ]:
            self.assertAlmostEqual(compute(self.frame, self.schema, full)[0], answer)
            self.assertEqual(result_unit(full),expected_unit)
        slope = {**inputs,"kind":"ols_slope","units":{**self.schema,"b":"m"}}
        self.assertEqual(result_unit(slope),"1")
        with self.assertRaisesRegex(ReplayError,"unit"):
            compute(self.frame,self.schema,slope)
        self.assertEqual(compute(self.frame.iloc[:2], self.schema, {**inputs,"kind":"ols_slope"}),(2.,2))

    def test_nonlinear_correlation_r_squared_and_tied_ranks(self):
        frame = pd.DataFrame({"a":[1,1,4,9],"b":[1,2,2,3]})
        inputs = dict(x="a", y="b", units={"a":"1","b":"1"})
        # Average ranks, centred, give dot product 3.75 with both sums of squares 4.5.
        self.assertAlmostEqual(compute(frame,inputs["units"],{**inputs,"kind":"spearman"})[0],3.75/4.5)
        expected_r2 = 64 / 85.5  # centred dot 8, sums of squares 42.75 and 2.
        self.assertAlmostEqual(compute(frame,inputs["units"],
                               {**inputs,"kind":"r_squared","scale":"percent"})[0],100*expected_r2)

    def test_selection_event_counts_boundaries_and_or(self):
        event = dict(column="a",cmp="lt",value=2.)
        op = dict(kind="proportion",units={"a":"m","g":"1"},where=self.where,event=event)
        self.assertEqual(compute(self.frame,self.schema,op),(.25,4))
        self.assertEqual(compute(self.frame,self.schema,
                         {**op,"kind":"percentage","event":{**event,"cmp":"le"}}),(50.,4))
        self.assertEqual(compute(self.frame,self.schema,
                         {"kind":"count","units":{"g":"1"},"where":[{**self.where[0],"value":5}]}),(0.,0))
        frame = pd.DataFrame({"d":[1]*5 + [0]*7, "y":[1,1,1,0,0,1,0,0,0,0,0,0]})
        op = {"kind":"odds_ratio","units":{"d":"1","y":"1"},
              "exposure":{"column":"d","cmp":"eq","value":1},"outcome":{"column":"y","cmp":"eq","value":1}}
        self.assertEqual(compute(frame,op["units"],op),(9.,12))
        with self.assertRaisesRegex(ReplayError,"denominator"):
            compute(frame.loc[~((frame.d==0)&(frame.y==1))],op["units"],op)

    def test_invalid_data_and_unadjusted_semantics(self):
        assoc = {"kind":"pearson","x":"a","y":"b","units":{"a":"m","b":"kg"}}
        with self.assertRaises(ReplayError):
            compute(self.frame.assign(a=0),self.schema,assoc)
        with self.assertRaises(ReplayError):
            compute(self.frame,self.schema,{**assoc,"adjusted_for":["g"]})
        with self.assertRaises(ReplayError):
            compute(self.frame,self.schema,{**assoc,"kind":"r_squared"})
        with self.assertRaises(ReplayError):
            compute(self.frame,self.schema,{**assoc,"units":{"a":"m"}})
        for bad in (np.nan, np.inf, "4"):
            with self.assertRaises(ReplayError):
                compute(self.frame.assign(g=[1,1,1,1,bad]),self.schema,
                        {"kind":"count","where":self.where,"units":{"g":"1"}})
        with self.assertRaises(ReplayError):
            compute(self.frame.assign(a=0), self.schema, {"kind":"geometric_mean","y":"a","units":{"a":"m"}})


if __name__ == "__main__":
    unittest.main()

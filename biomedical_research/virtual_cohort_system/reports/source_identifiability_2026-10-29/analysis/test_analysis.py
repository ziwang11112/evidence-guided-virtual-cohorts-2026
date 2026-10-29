"""Invented-data checks for the analysis only; no candidate generator imports."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from analyze_m6 import basis, input_preservation, json_write, paired_invariants, regressions


class AnalysisChecks(unittest.TestCase):
    def test_compact_basis_boundaries(self):
        a,b=basis(np.array([34,35,44,45,54,55,64,65]),np.array([21.99,22,23.99,24,25.99,26,27.99,28]))
        np.testing.assert_array_equal(a,[0,9103/18693,9103/18693,0,0,-1,-1,0])
        np.testing.assert_array_equal(b,[0,10388/14851,10388/14851,0,0,-1,-1,0])

    def test_no_change_invariants_detect_forbidden_change(self):
        zero=pd.DataFrame({"record_id":["a","b","c","d"],"age":[40,40,30,60],"sex":[1,2,1,1],"bmi":[23.,23.,23.,27.],
                           "tg_assay":["legacy_proxy"]*4,"tg_mg_dl":[100.,100.,100.,220.]})
        alt=zero.copy();alt.loc[0,"tg_mg_dl"]=102
        self.assertTrue(paired_invariants(zero,alt)["passed"])
        alt.loc[1,"tg_mg_dl"]=101
        self.assertFalse(paired_invariants(zero,alt)["passed"])
        self.assertTrue(input_preservation(zero,zero.drop(columns="tg_mg_dl"))["passed"])
        changed=zero.copy();changed.loc[1,"age"]=41
        self.assertFalse(input_preservation(changed,zero.drop(columns="tg_mg_dl"))["passed"])

    def test_invented_loglinear_projection(self):
        rows=[(a,s,b) for a in (30,50,70) for s in (1,2) for b in (20.,25.,30.)]
        frame=pd.DataFrame(rows,columns=["age","sex","bmi"])
        A=(frame.age-50)/10; B=(frame.bmi-25)/5; F=(frame.sex==2).astype(float)
        frame["tg_mg_dl"]=np.exp(4+.12*A+.2*B-.15*F)
        result=regressions(frame)
        self.assertAlmostEqual(result["logTG_age_per10"],.12,places=12)
        self.assertAlmostEqual(result["logTG_bmi_per5"],.2,places=12)
        self.assertAlmostEqual(result["logTG_female_minus_male"],-.15,places=12)
        self.assertAlmostEqual(result["logTG_bmi_curvature_2betaQ"],0,places=12)
        self.assertAlmostEqual(result["logTG_bmi_by_female"],0,places=12)
        self.assertAlmostEqual(result["logTG_age_by_bmi"],0,places=12)

    def test_undefined_statistics_remain_serializable(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/"report.json"
            json_write(file,{"failed_value":float("nan"),"pass":np.bool_(False),"nested":[np.float64(np.inf)]})
            self.assertEqual(json.loads(file.read_text()),{"failed_value":None,"pass":False,"nested":[None]})


if __name__=="__main__":
    unittest.main()

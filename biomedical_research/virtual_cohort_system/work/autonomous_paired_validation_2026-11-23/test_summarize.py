"""Post-reveal report tests on invented measurements only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

import summarize as report


MAP = {"unit":"kg/m2","threshold":-2,"id":"row_id",
       "reported":{"column":"a","unit":"kg/m2"},"measured":{"column":"b","unit":"kg/m2"}}


def create_runs(base, *, broken=False):
    root = base/"private/authors/a01"
    root.mkdir(parents=True)
    manifest = {"seeds":list(report.SEEDS),"n":10000,"runs":[]}
    schemas = [("primary",seed) for seed in report.SEEDS] + [("alternative",report.SEEDS[0])]
    if broken:
        schemas.pop(1)
    files = []
    for scenario, seed in schemas:
        directory = root/"execution_final"/f"{scenario}_{seed}"
        directory.mkdir(parents=True)
        table = directory/"generated.csv"
        matched = np.full(10000,23.)
        fraction = 0.50 if scenario=="primary" else 0.90
        low = np.arange(10000) < round(10000*fraction)
        pd.DataFrame({"row_id":np.arange(10000),"a":matched-3*low,"b":matched}).to_csv(table,index=False)
        manifest["runs"].append({"scenario":scenario,"seed":seed,"status":"success","table":str(table),
                              "n":10000,"sha256":report.experiment.sha(table)})
        files.append(table)
    recorded = root/"final_manifest.json"
    report.experiment.write(recorded,manifest)
    return {p.relative_to(base).as_posix():report.experiment.sha(p) for p in [*files,recorded]}


class TestReport(unittest.TestCase):
    def test_rounded_sensitivity_keeps_denominator(self):
        with TemporaryDirectory() as name:
            f = Path(name)/"synthetic.csv"
            f.write_text("row_id,a,b\na,20,22.04\nb,20,22\nc,20,23\nd,,22\n",encoding="utf8")
            result=report.input_report(f,MAP,real=True)
            self.assertEqual((result["n_complete"],result["strictly_below_n"]),(3,2))
            self.assertEqual(result["rounding_sensitivity"]["strictly_below_n"],1)
            self.assertEqual(result["rounding_sensitivity"]["ties_n"],2)

    def test_primary_eligibility_is_all_three_seeds(self):
        reference={"mean_difference":-1.5,"strictly_below_pct":50.}
        for missing in (False,True):
            with self.subTest(missing=missing),TemporaryDirectory() as name:
                root=Path(name)
                seals = create_runs(root,broken=missing)
                with patch.object(report,"HERE",root),patch.object(report.experiment,"PROJECT",root):
                    out=report.author_tables("a01",{"status":"success"},MAP,reference,seals)
                    self.assertEqual(out["meets_both"],not missing)
                    alt=next(item for item in out["tables"] if item["scenario"]=="alternative")
                    self.assertFalse(alt["within_tolerance"]["strictly_below_pct"])
                    self.assertEqual(alt["science"]["strictly_below_n"],9000)
                    tamper = next(p for p in root.rglob("generated.csv"))
                    with tamper.open("ab") as stream:
                        stream.write(b" ")
                    with self.assertRaisesRegex(ValueError,"verified freeze"):
                        report.author_tables("a01",{"status":"success"},MAP,reference,seals)

    def test_nonpositive_measurements_are_not_exported(self):
        with TemporaryDirectory() as name:
            p=Path(name)/"synthetic.csv"
            p.write_text("row_id,a,b\n0,-1,23\n1,25,23\n",encoding="utf8")
            with self.assertRaisesRegex(ValueError,"Nonpositive"):
                report.input_report(p,MAP)

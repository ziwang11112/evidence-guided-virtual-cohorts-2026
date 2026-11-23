from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evidence_replay import core


def entry():
    return dict(id="q",source="Table A",claim="Mean concentration",population="Sample",
                provenance="reported",applicability="same_population",
                reference=dict(value=10, decimals=1, unit="u"),
                operator=dict(kind="mean",y="m",units={"m":"u"}))


class TestInventory(unittest.TestCase):
    def test_empty_duplicate_and_precision(self):
        with self.assertRaises(ValueError):
            core.inventory({"evidence_checks":[]})
        self.assertEqual(core.inventory({"evidence_checks":[],"no_evidence_reason":"No quantities reported"}),[])
        with self.assertRaises(ValueError):
            core.inventory({"evidence_checks":[entry(),entry()]})
        x = entry()
        x["reference"]["value"] = 10.07
        with self.assertRaises(ValueError):
            core.inventory({"evidence_checks":[x]})

    def test_differences_units_and_scope(self):
        frame = pd.DataFrame({"m":[7.,9.]})
        op = lambda item: core.check(item,frame,{"m":"u"})
        self.assertEqual(op(entry())["difference"],-2)
        x = entry()
        x["reference"]["unit"] = "other"
        self.assertEqual(op(x)["status"], "not_computable")
        x = entry()
        x["reference"]["decimals"] = None
        self.assertEqual(op(x)["status"], "descriptive_only")
        x["adjustment"] = ["age"]
        self.assertEqual(op(x)["status"], "not_computable")
        self.assertEqual(op(dict(entry(),applicability="transport_assumption"))["status"], "not_source_comparable")
        self.assertEqual(op(dict(entry(),provenance="assumed"))["status"], "not_source_comparable")
        x = entry()
        x["operator"] = dict(kind="count",units={})
        x["reference"] = dict(value=10,decimals=0,unit="count")
        self.assertEqual(op(x)["status"], "not_source_comparable")

    def test_no_derived_diagnostic_or_identifier(self):
        for name in ("diagnostic_result","row_id"):
            x = entry()
            x["operator"] = dict(kind="mean", y=name, units={name:"u"})
            val = core.check(x,pd.DataFrame({name:[10.],"m":[6.]}),{"m":"u"})
            self.assertEqual(val["status"],"not_computable")

    def test_receipt_tamper_and_failure_coverage(self):
        candidate = {"model_spec":{"columns":[{"name":"m","unit":"u"}]}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/"execution_trial"/"table"/"generated.csv"
            path.parent.mkdir(parents=True)
            path.write_text("m\n7\n",encoding="utf8")
            manifest = dict(status="success",candidate_sha256=core.digest(candidate),
                            runs=[dict(status="success",scenario="base",seed=1,n=1,
                                       table=str(path),sha256="invalid")])
            args = (root,"trial",{"evidence_checks":[entry()]},candidate)
            with self.assertRaisesRegex(ValueError, "table hash"):
                core.replay(*args,manifest)
            rejected = deepcopy(manifest)
            rejected["status"] = "failed"
            rejected["runs"][0]["status"] = "failed"
            report = core.replay(*args,rejected)
            self.assertEqual(core.needs_disposition(report),{"q"})
            self.assertNotIn(str(root),json.dumps(core.review_feedback(report)))


if __name__ == "__main__":
    unittest.main()

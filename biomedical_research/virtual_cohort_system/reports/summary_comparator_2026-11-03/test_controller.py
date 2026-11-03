"""Invented controller bookkeeping tests; no clinical fit or generator execution."""
import contextlib, io, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import controller as c

class ControllerTests(unittest.TestCase):
    def test_spent_failed_slot_and_remaining_successes(self):
        with tempfile.TemporaryDirectory() as td:
            u=Path(td); b=u/"bundle"; f=b/"candidates/statistical/freeze.json"
            f.parent.mkdir(parents=True); f.write_text("{}")
            calls=[]
            def fake_run(bundle,candidate,run_id,seed,**kwargs):
                calls.append(seed)
                if seed==4101: raise ValueError("invented interrupted launch")
                d=b/"executions"/run_id; d.mkdir(parents=True)
                r={"status":"success","elapsed_seconds":.1,"error":None}
                (d/"execution.json").write_text(json.dumps(r)); return r
            with patch.object(c,"U",u),patch.object(c,"B",b),patch.object(c,"check_release",lambda:{}),patch.object(c,"run_candidate",fake_run),contextlib.redirect_stdout(io.StringIO()):
                c.runfinal()
                report=c.load(u/"DRAW_CLOSURE.json")
                self.assertEqual(calls,[4101,4102,4103])
                self.assertEqual(report["final_attempts"],3)
                self.assertEqual(report["results"][0]["status"],"interrupted_or_invalid_receipt")
                self.assertEqual(report["results"][1]["status"],"success")
                with self.assertRaises(ValueError): c.runfinal()
                self.assertEqual(calls,[4101,4102,4103])

    def test_reserved_interruption_never_reexecutes(self):
        with tempfile.TemporaryDirectory() as td:
            u=Path(td); b=u/"bundle"; f=b/"candidates/statistical/freeze.json"
            f.parent.mkdir(parents=True); f.write_text("{}")
            for s in (4101,4102,4103):
                c.write(u/"final_attempts"/f"final_{s}.json",{"seed":s})
            with patch.object(c,"U",u),patch.object(c,"B",b),patch.object(c,"check_release",lambda:{}),patch.object(c,"run_candidate",side_effect=AssertionError("must not draw")),patch.object(c,"verify_execution",side_effect=ValueError("missing receipt")),contextlib.redirect_stdout(io.StringIO()):
                c.runfinal()
                rows=c.load(u/"DRAW_CLOSURE.json")["results"]
                self.assertEqual(len(rows),3)
                self.assertTrue(all(r["status"]=="interrupted_or_invalid_receipt" for r in rows))

if __name__=="__main__": unittest.main(verbosity=2)


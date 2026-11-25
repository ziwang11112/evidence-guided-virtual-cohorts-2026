"""Clean, artificial fixtures for the APSS runner. Does not read study files or call a model."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import run_trial as t


class RunnerTest(unittest.TestCase):
    def test_independent_slot_order(self):
        self.assertEqual(t.order(), t.order())
        self.assertEqual(len(set(t.order())), 8)
        for i in range(0,8,2):
            pair=t.order()[i:i+2]
            self.assertEqual(pair[0][0],pair[1][0])
            self.assertEqual({a for _,a in pair},set(t.ARMS))

    def test_isolated_rows_and_hash_guard(self):
        body = """import numpy as np
import pandas as pd
def generate(observed,spec,seed):
    r=np.random.default_rng(seed)
    n=spec['n']
    return pd.DataFrame({'row_id':np.arange(n),'reported_bmi':r.uniform(1,2,n),'measured_bmi':r.uniform(1,2,n)})
"""
        c = {"model_spec":{"population":"Artificial engineering fixture","columns":[
                 {"name":"reported_bmi","unit":"kg/m2"},{"name":"measured_bmi","unit":"kg/m2"}]},
             "generator_py":body,"decision_record":{}}
        with TemporaryDirectory() as temporary, patch.object(t,"HERE",Path(temporary)), \
                patch.object(t,"PRIVATE",Path(temporary)/"private"):
            slot="b01_ordinary"
            file=t.PRIVATE/"candidates"/(slot+".json")
            t.put(file,c)
            row={"slot":slot,"arm":"ordinary","block":1,"candidate_sha256":t.sha(file)}
            self.assertTrue(t.eligible_artifact(c))
            base=t.execution_result(slot,c)
            completed=t.record_draws(row,base)
            self.assertEqual(completed["status"],"success")
            self.assertEqual(t.execution_result(slot,c),base)
            self.assertEqual([d["seed"] for d in completed["draws"]],list(t.SEEDS))
            for d in completed["draws"]:
                with (t.HERE/d["path"]).open("rb") as f:
                    self.assertEqual(sum(1 for _ in f),10001)
            damaged=t.HERE/completed["draws"][0]["path"]
            with damaged.open("ab") as f:
                f.write(b"\n")
            with self.assertRaisesRegex(ValueError,"digest"):
                t.record_draws(row,base)


if __name__=="__main__":
    unittest.main()

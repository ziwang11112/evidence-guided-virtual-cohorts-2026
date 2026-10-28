"""Artificial fixtures only. No hidden or actual insulin data are read."""
import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
from run_generation import check_output, call_checked, read_frame, validate_observed


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.x = pd.DataFrame({'row_id':['x','y','z'], 'bmi':[21.1,29.3,34.7],
                               'age':[23,47,68], 'sex':[1,2,1]})

    def output(self):
        return self.x.assign(insulin=[3.0,6.0,4.0])

    def test_valid_and_round_trip(self):
        validate_observed(self.x)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'x.csv'
            self.output().to_csv(p,index=False,float_format='%.17g')
            check_output(self.x,read_frame(p))

    def test_rejects_changed_observed(self):
        for col, val in [('bmi',21.10000000000001),('age',24),('sex',2),('row_id','q')]:
            bad = self.output(); bad.loc[0,col] = val
            with self.assertRaises((ValueError,AssertionError)):
                check_output(self.x,bad)

    def test_order_and_shape(self):
        for bad in [self.output().iloc[::-1], self.output().iloc[:2], self.output().assign(extra=0)]:
            with self.assertRaises((ValueError,AssertionError)):
                check_output(self.x,bad)

    def test_invalid_insulin(self):
        for val in [0., -1., np.nan, np.inf]:
            bad=self.output(); bad.loc[0,'insulin']=val
            with self.assertRaises(ValueError): check_output(self.x,bad)

    def test_rejects_duplicate_key(self):
        bad=self.x.copy(); bad.loc[1,'row_id']='x'
        with self.assertRaises(ValueError): validate_observed(bad)

    def test_mutation_rejected(self):
        def bad(x,e,s):
            x.loc[0,'bmi']=22.; return x.assign(insulin=1.)
        with self.assertRaises(AssertionError):
            call_checked(SimpleNamespace(generate=bad),self.x,{},1)
        self.assertEqual(self.x.loc[0,'bmi'],21.1)

    def test_rng_mutation_rejected_and_restored(self):
        before=copy.deepcopy(np.random.get_state())
        def bad(x,e,s):
            np.random.seed(s); return x.assign(insulin=1.)
        with self.assertRaises(ValueError):
            call_checked(SimpleNamespace(generate=bad),self.x,{},1)
        np.testing.assert_array_equal(before[1],np.random.get_state()[1])

    def test_local_rng_repeatable(self):
        def good(x,e,s):
            return x.assign(insulin=np.random.default_rng(s).uniform(1,2,len(x)))
        a,_=call_checked(SimpleNamespace(generate=good),self.x,{},3)
        b,_=call_checked(SimpleNamespace(generate=good),self.x,{},3)
        pd.testing.assert_frame_equal(a,b,check_exact=True)


if __name__ == '__main__': unittest.main()

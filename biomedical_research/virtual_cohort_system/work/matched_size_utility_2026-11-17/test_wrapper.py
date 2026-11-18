"""Targeted tests of the new wrapper and sampling design, using invented fixtures only."""
import json
import unittest
import numpy as np
import pandas as pd
from common import *

def fixture():
    rng = np.random.default_rng(191)
    rows = []
    for gi, (g, s) in enumerate(STRATA):
        for j in range(20):
            age = 20. + j + (j % 4) * .2
            y = 20 + GROUPS.index(g) * 1.4 + .03 * age + (s == 'F') * .4 + rng.normal(0, .4)
            rows.append([str(len(rows)), age, s, g, y, y * 5, y * 2])
    return pd.DataFrame(rows, columns=OP.REQUIRED)

class WrapperTests(unittest.TestCase):
    def test_raw_units_and_original_unchanged(self):
        d = fixture(); before = d.copy(deep=True)
        result = analyze_trait(d, 'bmi')
        x = np.column_stack([np.ones(len(d)), (d.lifestyle == GROUPS[1]).astype(float),
            (d.lifestyle == GROUPS[2]).astype(float), d.age, (d.sex == 'F').astype(float)])
        beta = np.linalg.solve(x.T @ x, x.T @ d.bmi.to_numpy())
        np.testing.assert_allclose([result[c] for c in CONTRASTS], [beta[1], beta[2], beta[2]-beta[1]], atol=1e-10)
        old = OP.analyze_frame(d)
        sd = next(t['sample_sd'] for t in old['trait_status'] if t['trait']=='bmi')
        for c in old['contrasts']:
            if c['trait']=='bmi' and c['stratum']=='pooled':
                self.assertAlmostEqual(result[c['contrast']], c['estimate'] * sd, places=12)
        pd.testing.assert_frame_equal(d, before)

    def test_sampling_counts_and_repeatability(self):
        d = fixture(); before = d.copy(deep=True); counts=[8, 9, 10, 11, 12, 13]
        a=sample_pool(d,counts,[0,0,0]); b=sample_pool(d,counts,[0,0,0]); c=sample_pool(d,counts,[0,0,1])
        pd.testing.assert_frame_equal(a,b)
        self.assertFalse(a.equals(c)); self.assertEqual(strata_counts(a),counts); self.assertTrue(a.id.is_unique)
        pd.testing.assert_frame_equal(d,before)

    def test_missing_cell_fails_and_zero_cell_allowed(self):
        d=fixture(); d=d.loc[~((d.lifestyle==GROUPS[0])&(d.sex=='F'))].reset_index(drop=True)
        with self.assertRaisesRegex(ValueError,'stratum unavailable'):sample_pool(d,[1]*6,[0,0,0])
        self.assertEqual(len(sample_pool(d,[0,2,2,2,2,2],[0,0,0])),10)

    def test_trait_eligibility(self):
        d=fixture(); d.loc[0,'age']=18; d.loc[1,'bmi']=0; d.loc[2,'bmi']=np.nan; d.loc[3,'bmi']=np.inf
        self.assertEqual(len(eligible(d,'bmi')),len(d)-4)
        self.assertEqual(len(eligible(d,'total_cholesterol')),len(d)-1)

    def test_constant_and_singular_remain_unavailable(self):
        d=fixture(); d['bmi']=5
        with self.assertRaises(ValueError):analyze_trait(d,'bmi')
        d=fixture(); d['lifestyle']=GROUPS[0]
        with self.assertRaises(ValueError):analyze_trait(d,'bmi')

    def test_duplicate_id_is_not_silently_accepted(self):
        d=fixture(); d.loc[1,'id']=d.loc[0,'id']
        with self.assertRaisesRegex(ValueError,'duplicated IDs'):analyze_trait(d,'bmi')

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WrapperTests))
    write_new(HERE/'TEST_RECEIPT.json',dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),fixtures='invented only; no patient or Agent generation',created_utc=now()))
    raise SystemExit(0 if result.wasSuccessful() else 1)

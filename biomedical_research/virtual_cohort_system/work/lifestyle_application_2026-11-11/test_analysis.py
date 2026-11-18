"""Invented fixtures only; no empirical relationships or target data."""
import unittest
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
import analysis_operator as op

class Tests(unittest.TestCase):
    def setUp(self):
        r=np.random.default_rng(555); n=180
        g=np.tile(op.GROUPS,60);female=np.tile([True,False],90);age=r.uniform(20,70,n)
        self.frame=pd.DataFrame(dict(id=[f'toy_{i}' for i in range(n)],age=age,
            sex=np.where(female,'F','M'),lifestyle=g,
            bmi=30+np.array([0,2,5])[np.arange(n)%3]+.05*age+r.normal(size=n),
            total_cholesterol=150+r.normal(0,10,n),hdl_cholesterol=50+r.normal(0,5,n)))
    def test_all_slots_and_against_statsmodels(self):
        d=op.analyze_frame(self.frame);self.assertEqual(len(d['contrasts']),27);self.assertEqual(len(d['interactions']),3)
        f=self.frame;x=np.column_stack([np.ones(len(f)),f.lifestyle==op.GROUPS[1],f.lifestyle==op.GROUPS[2],f.age,f.sex=='F']).astype(float)
        z=(f.bmi-f.bmi.mean())/f.bmi.std(ddof=1);fit=sm.OLS(z,x).fit()
        c=op.CONTRASTS[2][1];expected=fit.t_test(c)
        a=next(a for a in d['contrasts'] if a['trait']=='bmi' and a['stratum']=='pooled' and a['contrast']==op.CONTRASTS[2][0])
        self.assertAlmostEqual(a['estimate'],float(np.ravel(expected.effect)[0]),11)
        self.assertAlmostEqual(a['se'],float(np.ravel(expected.sd)[0]),11)
        self.assertAlmostEqual(a['p_value'],float(expected.pvalue),11)
    def test_unit_invariance(self):
        a=op.analyze_frame(self.frame);f=self.frame.copy();f.total_cholesterol*=38.67;f.hdl_cholesterol*=38.67
        b=op.analyze_frame(f)
        for u,v in zip(a['contrasts'],b['contrasts']):self.assertAlmostEqual(u['estimate'],v['estimate'],11)
    def test_missing_per_trait_and_age_boundary(self):
        f=self.frame.copy();f.loc[0,'age']=18;f.loc[1,'bmi']=np.nan
        a=op.analyze_frame(f);self.assertEqual(a['eligible_age_rows'],179)
        self.assertEqual([t['n'] for t in a['trait_status']],[178,179,179])
    def test_interaction_branch_and_pooled_scale(self):
        f=self.frame.copy();f.loc[(f.lifestyle==op.GROUPS[2])&(f.sex=='F'),'bmi']+=20
        a=op.analyze_frame(f);it=next(x for x in a['interactions'] if x['trait']=='bmi')
        self.assertTrue(it['selects_sex_specific'])
        b=[x for x in a['contrasts'] if x['trait']=='bmi'];self.assertTrue(all(x['selected_by_paper_rule'] for x in b if x['stratum']!='pooled'))
        y=(f.bmi-f.bmi.mean())/f.bmi.std(ddof=1);s=f.sex=='F';g=f.loc[s]
        x=np.column_stack([np.ones(sum(s)),g.lifestyle==op.GROUPS[1],g.lifestyle==op.GROUPS[2],g.age]).astype(float)
        expected=np.linalg.lstsq(x,y[s],rcond=None)[0][2]
        actual=next(t['estimate'] for t in b if t['stratum']=='F' and t['contrast']=='urban_minus_pastoralist')
        self.assertAlmostEqual(actual,expected,11)
    def test_bh(self):
        p=[.002,.009,.031,.043,.4,.8,.03,.22,.005]
        np.testing.assert_allclose(op._bh(p),multipletests(p,method='fdr_bh')[1],atol=1e-15)
    def test_singular_keeps_slots_and_bad_group_rejected(self):
        f=self.frame.copy();f.lifestyle=op.GROUPS[0];a=op.analyze_frame(f)
        self.assertEqual(len(a['contrasts']),27);self.assertTrue(all(x['status']=='unavailable' for x in a['contrasts']))
        f.loc[0,'lifestyle']='unknown'
        with self.assertRaises(ValueError):op.analyze_frame(f)

if __name__=='__main__':unittest.main()

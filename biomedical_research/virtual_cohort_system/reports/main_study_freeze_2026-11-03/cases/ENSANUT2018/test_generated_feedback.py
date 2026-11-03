"""Hand-built factorial fixture; no random sampling or patient information."""
import unittest
import pandas as pd
from generated_feedback import generated_statistics, DIAGNOSTICS


def fixture():
    records=[]
    for lower in (25,40,55,70):
        for female in (0,1):
            for a in (0,1):
                for b in (0,1):
                    for g in (0,1):
                        age=lower+a
                        bmi=20+10*b
                        glucose=80+20*g
                        hba1c=5+.2*(age-50)/10+.3*female+.4*(bmi-25)/5+.5*(glucose-100)/10
                        records.append(dict(age=age,female=female,bmi=bmi,glucose=glucose,hba1c=hba1c))
    return pd.DataFrame(records)


class GeneratedFeedbackTests(unittest.TestCase):
    def test_exact_toy_projections_and_schema(self):
        out=generated_statistics(fixture(),expected_rows=64,expected_per_cell=8)
        self.assertEqual(set(out),{'analyses','diagnostics','quality','n'})
        values={x['id']:x['value'] for x in out['analyses']}
        for name,value in [('Q1_age10',.2),('Q2_bmi5',.4),('Q3_bmi5',.4)]:
            self.assertAlmostEqual(values[name],value)
        self.assertTrue(all(x['status']=='computed' for x in out['analyses']))
        diagnostics={x['id']:x['value'] for x in out['diagnostics']}
        self.assertAlmostEqual(diagnostics['Q2_minus_Q3_bmi5'],0.)
        self.assertAlmostEqual(diagnostics['glucose10_age_sex'],.5)
        self.assertEqual(len(diagnostics),28)

    def test_invalid_age_or_quota_returns_all_analyses_unavailable(self):
        frame=fixture(); frame.loc[0,'age']=80
        result=generated_statistics(frame,expected_rows=64,expected_per_cell=8)
        self.assertTrue(all(x['status']=='unavailable' for x in result['analyses']))
        self.assertEqual({x['id'] for x in result['diagnostics']},set(DIAGNOSTICS))
        self.assertEqual(len(result['diagnostics']),28)
        self.assertTrue(all(x['status']=='unavailable' and x['value'] is None and x['reason'] for x in result['diagnostics']))
        frame=fixture(); frame.loc[0,'female']=1
        result=generated_statistics(frame,expected_rows=64,expected_per_cell=8)
        self.assertEqual(result['quality']['status'],'failed')
        self.assertEqual({x['id'] for x in result['diagnostics']},set(DIAGNOSTICS))
        self.assertTrue(all(x['status']=='unavailable' and x['value'] is None and x['reason'] for x in result['diagnostics']))

if __name__=='__main__':
    unittest.main()

"""Controller checks using only M13-A's invented qualification covariates."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import controller as c


class ControllerChecks(unittest.TestCase):
    def setUp(self):
        self.fixture = c.PROJECT/'work/m13/build01/observed.csv'
        self.x = c.load_observed(self.fixture)

    def test_source_formula_and_reference_preservation(self):
        deterministic, n = c.references(self.x, None)
        self.assertEqual(n, 0)
        # Independently expanded published coefficients at an arbitrary fixture row.
        r = self.x.iloc[0]
        expected = 76 + .053*r.age - 20.6*r.male + (154*r.male-1097.8)/r.bmi + .034*r.male*r.age
        self.assertAlmostEqual(deterministic.bodyfat.iloc[0], expected, places=11)
        pd.testing.assert_frame_equal(deterministic[c.INPUTS], self.x)
        a,_ = c.references(self.x,33101)
        b,_ = c.references(self.x,33101)
        pd.testing.assert_frame_equal(a,b)
        self.assertTrue(a.bodyfat.between(0,100).all())
        self.assertGreater(float(np.std(a.bodyfat-deterministic.bodyfat)),0)

    def test_extra_or_corrupted_derived_input_rejected(self):
        with tempfile.TemporaryDirectory(prefix='m13b-input-check-') as d:
            p=Path(d)/'x.csv'
            x=self.x.copy();x['DXDTOPF']=25;x.to_csv(p,index=False)
            with self.assertRaises(ValueError):c.load_observed(p)
            x=self.x.copy();x.loc[0,'male_age']+=1;x.to_csv(p,index=False)
            with self.assertRaises(ValueError):c.load_observed(p)

    def test_deployment_preserves_science_and_rebinds_inputs(self):
        with tempfile.TemporaryDirectory(prefix='m13b-deploy-check-') as d:
            with patch.object(c,'ROOT',Path(d)):
                c.initialize()
                (Path(d)/'preaccess_freeze.json').write_text(json.dumps({'files':{}}),encoding='utf-8')
                c.deploy(self.fixture)
                manifest=c.read(Path(d)/'deployment_manifest.json')
                self.assertEqual(len(manifest['deployments']),4)
                for item in manifest['deployments']:
                    candidate=Path(item['bundle'])/'candidates'/item['candidate']
                    source=c.PROJECT/'work/m13'/item['builder']/'candidates'/item['candidate']
                    self.assertEqual(c.sha256(candidate/'model_spec.json'),c.sha256(source/'model_spec.json'))
                    self.assertEqual(c.sha256(candidate/'generator.py'),c.sha256(source/'generator.py'))
                    c.verify_candidate(item['bundle'],f"candidates/{item['candidate']}")
                target=Path(manifest['deployments'][0]['bundle'])/'candidates/initial'
                original=(target/'freeze.json').read_bytes()
                (target/'freeze.json').write_bytes(original+b' ')
                with self.assertRaisesRegex(ValueError,'Deployment freeze replaced'): c.generate()
                (target/'freeze.json').write_bytes(original)
                original_program=(target/'generator.py').read_bytes()
                (target/'generator.py').write_bytes(original_program+b'\n# changed\n')
                with self.assertRaisesRegex(ValueError,'Deployed scientific identity changed'): c.generate()
                self.assertFalse((Path(d)/'deployment/build01/executions').exists())


if __name__=='__main__': unittest.main()

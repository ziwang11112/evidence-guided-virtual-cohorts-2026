"""Nonclinical estimator contract check; this is not a generator or patient test."""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('generated_adapter_test', HERE/'generated_analysis.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class AdapterContract(unittest.TestCase):
    def test_known_analysis_and_no_reference_input(self):
        # Artificial orthogonal residuals provide an independent exact check.
        n=80
        t=np.arange(n,dtype=float)
        age=25+t/2
        female=(t%2==0).astype(float)
        bmi=20+(t%7)
        X=np.column_stack([np.ones(n),age,female,bmi])
        Q=np.linalg.qr(X,mode='reduced')[0]
        r1=np.sin(t);r1=r1-Q@(Q.T@r1);r1=r1/np.linalg.norm(r1)
        r2=np.cos(t*.7);r2=r2-Q@(Q.T@r2);r2=r2-r1*(r1@r2);r2=r2/np.linalg.norm(r2)
        tc=X@np.array([3,.01,.2,.04])+r1*.2
        hdl=X@np.array([1,.001,.1,-.005])+.1*(.4*r1+np.sqrt(.84)*r2)
        frame=pd.DataFrame({'id':['f'+str(i) for i in range(n)],'age':age,'sex':np.where(female,'F','M'),
                            'bmi':bmi,'total_cholesterol':tc,'hdl_cholesterol':hdl})
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);frame.to_csv(d/'generated.csv',index=False)
            (d/'task.json').write_text(json.dumps({'n_rows':n}))
            (d/'request.json').write_text(json.dumps({'analyses':['three fictional checks']}))
            result=adapter.analyze(d/'generated.csv',d/'task.json',d/'request.json')
        vals={r['id']:r['value'] for r in result['analyses']}
        self.assertAlmostEqual(vals['K02-TC-BMI'],.04*5*38.67,places=9)
        self.assertAlmostEqual(vals['K02-HDL-BMI'],-.005*5*38.67,places=9)
        self.assertAlmostEqual(vals['K02-LIPID-RESIDUAL'],.4,places=9)
        self.assertEqual(len(result['diagnostics']),23)
        self.assertIs(result['quality']['reference_read'],False)

if __name__=='__main__':unittest.main()

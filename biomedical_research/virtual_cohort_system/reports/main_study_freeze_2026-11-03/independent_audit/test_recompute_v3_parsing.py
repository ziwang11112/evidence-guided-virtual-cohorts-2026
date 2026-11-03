"""Targeted invented CSV fixture for exact float/quantile parsing; no data files."""
import ast
import io
import math
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
import recompute_v3 as r


class RoundTripParsingTests(unittest.TestCase):
    def test_serialized_binary_float_and_selected_inverse_cdf_value(self):
        # This literal is the binary float immediately above float('0.3').
        # The fixture is authored here, not copied from a clinical/output CSV.
        selected = math.nextafter(0.3, math.inf)
        self.assertEqual(repr(selected), '0.30000000000000004')
        original = [0.1, 0.2, selected, 0.4]
        csv = 'value\n' + ''.join(repr(value)+'\n' for value in original)
        default = pd.read_csv(io.StringIO(csv))['value'].to_numpy()
        actual = r.read_generated_output(io.StringIO(csv))['value'].to_numpy()
        self.assertEqual(actual.tolist(), original)
        self.assertEqual(default[2], math.nextafter(selected, -math.inf))
        weights = np.full(4, 0.25)
        self.assertEqual(r.inverse_weighted_quantile(actual, weights, 0.75), selected)
        self.assertNotEqual(r.inverse_weighted_quantile(default, weights, 0.75), selected)

    def test_v3_delta_keeps_all_arithmetic_functions_identical(self):
        folder = Path(__file__).resolve().parent
        old = ast.parse((folder/'recompute_v2.py').read_text())
        new = ast.parse((folder/'recompute_v3.py').read_text())
        old_functions = {x.name:ast.dump(x,include_attributes=False) for x in old.body if isinstance(x,ast.FunctionDef)}
        new_functions = {x.name:ast.dump(x,include_attributes=False) for x in new.body if isinstance(x,ast.FunctionDef)}
        self.assertEqual(set(new_functions)-set(old_functions), {'read_generated_output'})
        for name in old_functions:
            if name != 'audit':
                self.assertEqual(old_functions[name],new_functions[name],name)


if __name__ == '__main__':
    unittest.main()

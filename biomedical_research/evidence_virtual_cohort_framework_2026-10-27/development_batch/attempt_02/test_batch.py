"""Artificial fixtures only: no study data or expected scientific answers."""
import unittest
import io
import numpy as np
import pandas as pd
import run_batch as batch


def record(analysis="pfs_time_reml", term="month_3_minus_0", estimate=1, lo=.5, hi=1.5):
    return dict(analysis=analysis, term=term, estimate=estimate, se=.25, ci_low=lo, ci_high=hi, status="ok")


class BatchTests(unittest.TestCase):
    def test_17_digit_serialization_requires_round_trip_parser(self):
        original = "x\n0.3\n"
        completed = "x\n" + format(.3,".17g") + "\n"
        default_a = pd.read_csv(io.StringIO(original)).x.iloc[0]
        default_b = pd.read_csv(io.StringIO(completed)).x.iloc[0]
        self.assertNotEqual(default_a,default_b)
        round_a = pd.read_csv(io.StringIO(original),float_precision="round_trip").x.iloc[0]
        round_b = pd.read_csv(io.StringIO(completed),float_precision="round_trip").x.iloc[0]
        self.assertEqual(round_a,round_b)
        self.assertEqual(round_a,.3)

    def test_ci_states_zero_boundary_and_failure(self):
        self.assertEqual(batch.ci_state(record()), "positive")
        self.assertEqual(batch.ci_state(record(estimate=-1, lo=-1.5, hi=-.5)), "negative")
        self.assertEqual(batch.ci_state(record(lo=0)), "uncertain")
        self.assertEqual(batch.ci_state(record(lo=-.2)), "uncertain")
        self.assertEqual(batch.ci_state(dict(record(), status="not_converged")), "unavailable")

    def test_key_alignment_uses_analysis_keys_not_position(self):
        records = [record(a, t) for a, t in batch.EXPECTED]
        index = batch.index_records(list(reversed(records)))
        self.assertEqual(list(index)[0], batch.EXPECTED[-1])
        self.assertEqual(index[batch.EXPECTED[0]]["term"], batch.EXPECTED[0][1])
        with self.assertRaises(ValueError):
            batch.index_records(records + records[:1])
        with self.assertRaises(ValueError):
            batch.index_records(records[:-1])

    def test_copied_controls_require_exact_unchanged_inputs(self):
        frame = pd.DataFrame(dict(person_id=[1,1,2,2], month=[0,3,0,3], weight_kg=[70.,69.,80.,78.], pfs=[2.,3.,3.,4.], gng=[1.,2.,3.,np.nan], dd100=[.2,.3,.4,.5], dd1000=[.4,.5,.6,.7]))
        candidate = frame.copy()
        candidate.loc[1,"pfs"] = 4.
        records = [record(a,t) for a,t in batch.EXPECTED]
        controls = batch.copy_controls(records, frame, candidate)
        self.assertEqual(len(controls),29)
        self.assertFalse(any(batch.affected(r) for r in controls))
        controls[0]["estimate"] = 900
        self.assertEqual(records[0]["estimate"],1)
        candidate.loc[0,"pfs"] = 4.
        with self.assertRaises(AssertionError):
            batch.copy_controls(records, frame, candidate)
        candidate = frame.copy()
        candidate.loc[1,"weight_kg"] += 1e-10
        with self.assertRaises(AssertionError):
            batch.copy_controls(records, frame, candidate)
        with self.assertRaises(ValueError):
            batch.copy_controls(records, frame, frame.iloc[::-1])

    def test_pooling_regime_and_failed_draw_retention(self):
        def pooler(q,se):
            return dict(status="ok", estimate=float(np.mean(q)), se=float(np.mean(se)))
        records = [record(estimate=i/20) for i in range(20)]
        result = batch.pool_group(records, "completion", pooler)
        self.assertAlmostEqual(result["estimate"],.475)
        with self.assertRaises(ValueError):
            batch.pool_group(records,"full_synthetic",pooler)
        with self.assertRaises(ValueError):
            batch.pool_group([record("baseline_pearson","pfs__gng")]*20,"completion",pooler)
        damaged = [dict(r) for r in records]
        damaged[2]["status"] = "not_converged"
        result = batch.pool_group(damaged,"completion",pooler)
        self.assertEqual(result["status"],"incomplete_arm")
        self.assertEqual(result["m_valid"],19)
        self.assertIsNone(result["estimate"])
        self.assertEqual(batch.pool_group(records[:-1],"completion",pooler)["m_expected"],20)

    def test_comparison_retains_magnitude_and_uncertainty(self):
        result = batch.compare(record(estimate=.1,lo=-.5,hi=.7),record())
        self.assertAlmostEqual(result["absolute_error"],.9)
        self.assertAlmostEqual(result["error_in_reference_se"],-3.6)
        self.assertFalse(result["ci_state_agreement"])
        self.assertEqual(result["ci_state"],"uncertain")

    def test_failed_preservation_does_not_export_values(self):
        try:
            pd.testing.assert_series_equal(pd.Series([71.234567]),pd.Series([82.987654]))
        except AssertionError as error:
            self.assertIn("71.234567",str(error))
            safe = batch.safe_failure(error)
            self.assertNotIn("71.234567",safe)
            self.assertNotIn("82.987654",safe)
            self.assertIn("AssertionError",safe)
        original = dict(record(),status="fit_failed:ValueError:values [71.234567, 82.987654]")
        exported = batch.safe_record(original)
        self.assertEqual(exported["status"],"fit_failed:ValueError")
        self.assertIn("71.234567",original["status"])
        self.assertFalse(batch.valid(exported))


if __name__ == "__main__":
    unittest.main(verbosity=2)

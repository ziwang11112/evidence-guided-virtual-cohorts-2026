"""Target-free, synthetic checks of mathematical-warning and rule semantics."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scientific_law_checks_test_subject", ROOT / "law_checks.py")
lc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lc
spec.loader.exec_module(lc)

TASK = {"columns": [{"name": "id", "role": "identifier"}, {"name": "a", "role": "generated"},
                    {"name": "b", "role": "generated"}, {"name": "c", "role": "generated"}],
        "requested_analysis_ids": ["joint"]}


def contract():
    return {"schema_version": 1,
        "mathematical_review": [{"variable": x, "support": "Unresolved", "moment_assessment": "unresolved",
            "justification": "No theorem established", "code_locator": "generate", "source_ids": []} for x in ["a", "b", "c"]],
        "physiological_review": "Synthetic declarative check, not a medical assertion.",
        "physiological_rules": [{"rule_id": "linear", "coefficients": {"a": 1, "b": -1},
            "operator": "ge", "bound": 0, "atol": 0, "rtol": 0, "basis": "assumed", "source_ids": [],
            "rationale": "Synthetic test fixture; not clinical evidence."}],
        "joint_analyses": [{"analysis_id": "joint", "variables": ["a", "b"], "adjustment": ["c"],
            "operator": "residual_pearson", "dependencies": [{"parameter": "dependence", "basis": "unresolved",
                "source_ids": [], "source_operator": "unavailable", "source_adjustment": [],
                "support": "unavailable", "uncertainty": "not calibrated", "code_locator": "generate"}]}]}


def codes(program):
    return {x["code"] for x in lc.inspect_program(program)["findings"]}


class StaticTests(unittest.TestCase):
    def test_positive_nested_exponential_and_alias(self):
        out = lc.inspect_program("import numpy as np\ndef generate():\n z=rng.normal(size=10)\n b=12+np.exp(z)\n alias=b\n c=.055\n q=np.exp((c*(alias-22)+1)/3.8)\n return q\n")
        events = [f for f in out["findings"] if f["code"] == "EXP_OF_HEAVY_TAINT"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["line"], 7)
        self.assertEqual(events[0]["dependency_lines"], [4])
        self.assertFalse(events[0]["proof"])

    def test_direct_lognormal(self):
        self.assertIn("EXP_OF_HEAVY_TAINT", codes("b=rng.lognormal(0,1,10)\ny=np.exp(.5*b)"))

    def test_imported_and_assigned_function_aliases(self):
        self.assertIn("EXP_OF_HEAVY_TAINT", codes("from numpy import exp as e\nb=rng.lognormal(0,1)\nf=e\ny=f(b)"))

    def test_simple_lognormal_not_nested_alarm(self):
        out = lc.inspect_program("z=rng.normal(size=5)\ny=np.exp(z)")
        self.assertNotIn("EXP_OF_HEAVY_TAINT", {f["code"] for f in out["findings"]})
        self.assertEqual(out["mathematical_validity"], "not_certified")

    def test_negative_heavy_sign(self):
        out = codes("b=rng.lognormal(0,1)\ny=np.exp(-2*b)")
        self.assertIn("NEGATIVE_HEAVY_EXPONENT", out)
        self.assertNotIn("EXP_OF_HEAVY_TAINT", out)

    def test_unknown_sign_is_review_not_proof(self):
        out = lc.inspect_program("b=rng.lognormal(0,1)\ny=np.exp(spec['x']*b)")
        self.assertIn("EXP_OF_HEAVY_TAINT", {f["code"] for f in out["findings"]})
        self.assertTrue(all(not f["proof"] for f in out["findings"]))

    def test_actual_local_cap_distinguished(self):
        out = codes("b=rng.lognormal(0,1)\ny=np.exp(np.clip(.5*b,-30,30))")
        self.assertIn("EXP_AFTER_LITERAL_CLIP", out)
        self.assertNotIn("EXP_OF_HEAVY_TAINT", out)

    def test_unresolved_cap_not_certificate(self):
        out = codes("b=rng.lognormal(0,1)\ny=np.exp(np.clip(b,-30,spec['max']))")
        self.assertIn("UNRESOLVED_CLIP_BOUNDS", out)
        self.assertIn("EXP_OF_HEAVY_TAINT", out)

    def test_later_cap_does_not_erase_local_warning(self):
        out = codes("b=rng.lognormal(0,1)\nx=np.exp(b)\ny=np.clip(x,0,50)")
        self.assertIn("EXP_OF_HEAVY_TAINT", out)
        self.assertIn("FINITE_LITERAL_CLIP", out)

    def test_branch_analysis_explicitly_not_proof(self):
        out = lc.inspect_program("b=rng.lognormal(0,1)\nif flag:\n b=np.clip(b,0,10)\ny=np.exp(b)")
        self.assertIn("control_flow_not_proven", out["unresolved_function_names"])
        self.assertEqual(out["mathematical_validity"], "not_certified")

    def test_unknown_helper_preserves_review_boundary(self):
        out = lc.inspect_program("y=unknown_sampler(spec)\nreturn_value=custom(y)")
        self.assertIn("unknown_sampler", out["unresolved_function_names"])
        self.assertEqual(out["status"], "no_pattern_detected_not_certified")

    def test_code_not_executed(self):
        marker = ROOT / "NEVER_CREATE_BY_STATIC_INSPECTION"
        self.assertFalse(marker.exists())
        out = lc.inspect_program(f"open({str(marker)!r},'w').write('bad')")
        self.assertFalse(marker.exists())
        self.assertEqual(out["mathematical_validity"], "not_certified")

    def test_invalid_and_bounded_input(self):
        self.assertEqual(lc.inspect_program("def bad(:")["status"], "unavailable")
        self.assertEqual(lc.inspect_program("#" + "a"*lc.MAX_CODE_BYTES)["status"], "unavailable")
        self.assertEqual(lc.inspect_program(None)["status"], "unavailable")


class ContractTests(unittest.TestCase):
    def test_honest_unresolved_valid_not_certified(self):
        out = lc.validate_contract(contract(), TASK)
        self.assertTrue(out["valid"])
        self.assertEqual(out["coverage"]["mathematical_variables_not_declared"], [])
        self.assertEqual(out["coverage"]["analysis_coverage"], "complete_declarations_only")
        self.assertTrue(any("unresolved" in x for x in out["warnings"]))

    def test_empty_dimensions_not_pass(self):
        c = contract()
        c["mathematical_review"] = []
        c["physiological_rules"] = []
        c["joint_analyses"] = []
        out = lc.validate_contract(c, TASK)
        self.assertTrue(out["valid"])
        self.assertEqual(out["coverage"]["analysis_coverage"], "incomplete")
        self.assertEqual(out["coverage"]["physiology_coverage"], "not_assessed")
        self.assertEqual(set(out["coverage"]["mathematical_variables_not_declared"]), {"a", "b", "c"})

    def test_nonfinite_bool_and_extra_keys_fail(self):
        for value in [float('nan'), float('inf'), True, "1"]:
            c = contract(); c["physiological_rules"][0]["coefficients"]["a"] = value
            self.assertFalse(lc.validate_contract(c, TASK)["valid"])
        c = contract(); c["expression"] = "__import__('os').system('x')"
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])

    def test_unknown_variables_and_duplicate_identifiers_fail(self):
        c = contract(); c["physiological_rules"][0]["coefficients"]["secret"] = 1
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])
        c = contract(); c["joint_analyses"] *= 2
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])

    def test_reported_needs_source_binding_identifier(self):
        c = contract(); c["joint_analyses"][0]["dependencies"][0]["basis"] = "reported"
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])
        c["joint_analyses"][0]["dependencies"][0]["source_ids"] = ["unverified_identifier"]
        out = lc.validate_contract(c, TASK)
        self.assertTrue(out["valid"])
        self.assertIn("source extraction", out["verification_boundary"])

    def test_source_adjustment_mismatch_visible(self):
        c = contract(); d = c["joint_analyses"][0]["dependencies"][0]
        d.update(basis="derived", source_ids=["paper"], source_adjustment=["external_covariate"])
        self.assertTrue(any("adjustment sets differ" in s for s in lc.validate_contract(c, TASK)["warnings"]))

    def test_analysis_semantics_against_shared_requirement(self):
        task = copy.deepcopy(TASK)
        task["analysis_requirements"] = [{"analysis_id": "joint", "variables": ["a", "b"], "adjustment": ["c"], "operator": "residual_pearson"}]
        self.assertTrue(lc.validate_contract(contract(), task)["valid"])
        c = contract(); c["joint_analyses"][0]["adjustment"] = []
        self.assertFalse(lc.validate_contract(c, task)["valid"])
        c = contract(); c["joint_analyses"][0]["operator"] = "pearson"
        self.assertFalse(lc.validate_contract(c, task)["valid"])

    def test_missing_expected_analyses_not_assumed_complete(self):
        task = copy.deepcopy(TASK); del task["requested_analysis_ids"]
        self.assertEqual(lc.validate_contract(contract(), task)["coverage"]["analysis_coverage"], "expected_analyses_not_supplied")

    def test_categorical_support_not_required_as_numeric_moment(self):
        task = copy.deepcopy(TASK); task["columns"].append({"name": "category", "kind": "category", "role": "generated"})
        self.assertEqual(lc.validate_contract(contract(), task)["coverage"]["mathematical_variables_not_declared"], [])

    def test_whitespace_review_and_unjustified_unknown_rejected(self):
        c = contract(); c["physiological_review"] = "  "
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])
        c = contract(); c["mathematical_review"][0]["justification"] = ""
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])

    def test_missing_dependency_is_explicitly_incomplete(self):
        c = contract(); c["joint_analyses"][0]["dependencies"] = []
        out = lc.validate_contract(c, TASK)
        self.assertTrue(out["valid"])
        self.assertEqual(out["coverage"]["analyses_without_dependencies"], ["joint"])

    def test_oversized_cyclic_and_missing_notes_rejected(self):
        c = contract(); c["physiological_review"] = "a"*(lc.MAX_TEXT+1)
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])
        c = contract(); c["cycle"] = c
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])
        c = contract(); del c["physiological_review"]
        self.assertFalse(lc.validate_contract(c, TASK)["valid"])


class TrialTests(unittest.TestCase):
    def test_linear_violation_count_exact_and_input_unchanged(self):
        frame = pd.DataFrame({"a": [2., 1., 3.], "b": [1., 2., 3.], "c": [0., 0., 0.]})
        before = frame.copy(deep=True)
        result = lc.inspect_trial(frame, contract(), TASK)
        rule = result["physiology"]["rules"][0]
        self.assertEqual(rule["violating_rows"], 1)
        self.assertEqual(rule["violation_fraction"], 1/3)
        self.assertEqual(rule["max_violation_beyond_tolerance"], 1)
        pd.testing.assert_frame_equal(before, frame)
        self.assertEqual(result["mathematical_review"]["status"], "author_claims_not_certified")

    def test_equality_absolute_relative_tolerance(self):
        c = contract(); r = c["physiological_rules"][0]
        r.update(coefficients={"a": 1}, operator="eq", bound=100, atol=.1, rtol=.01)
        out = lc.inspect_trial(pd.DataFrame({"a": [100., 101., 102.]}), c, TASK)
        r = out["physiology"]["rules"][0]
        self.assertEqual(r["violating_rows"], 1)
        self.assertAlmostEqual(r["max_violation_beyond_tolerance"], .88)

    def test_range_as_two_linear_rules(self):
        c = contract(); r = c["physiological_rules"][0]
        r.update(coefficients={"a": 1}, bound=0)
        upper = copy.deepcopy(r); upper.update(rule_id="upper", operator="le", bound=5)
        c["physiological_rules"].append(upper)
        out = lc.inspect_trial(pd.DataFrame({"a": [-1., 2., 6.]}), c, TASK)
        self.assertEqual([r["violating_rows"] for r in out["physiology"]["rules"]], [1, 1])

    def test_nonfinite_rows_are_not_passes(self):
        out = lc.inspect_trial(pd.DataFrame({"a": [float('nan'), float('inf'), 2.], "b": [1., 1., 1.]}), contract(), TASK)
        r = out["physiology"]["rules"][0]
        self.assertEqual(r["evaluated_rows"], 1)
        self.assertEqual(r["nonfinite_or_arithmetic_unavailable_rows"], 2)
        self.assertFalse(r["passes_this_trial"])
        json.dumps(out, allow_nan=False)

    def test_all_nan_never_passes(self):
        out = lc.inspect_trial(pd.DataFrame({"a": [np.nan], "b": [np.nan]}), contract(), TASK)
        r = out["physiology"]["rules"][0]
        self.assertEqual(r["status"], "unavailable")
        self.assertIsNone(r["violation_fraction"])
        self.assertFalse(r["passes_this_trial"])

    def test_missing_bool_and_string_columns_unavailable(self):
        for frame in [pd.DataFrame({"a": [1]}), pd.DataFrame({"a": [True], "b": [False]}), pd.DataFrame({"a": ["2"], "b": ["1"]})]:
            r = lc.inspect_trial(frame, contract(), TASK)["physiology"]["rules"][0]
            self.assertEqual(r["status"], "unavailable")
            self.assertFalse(r["passes_this_trial"])

    def test_overflow_unavailable_not_json_infinity(self):
        c = contract(); c["physiological_rules"][0]["coefficients"] = {"a": 1e300}
        out = lc.inspect_trial(pd.DataFrame({"a": [1e300]}), c, TASK)
        self.assertFalse(out["physiology"]["rules"][0]["passes_this_trial"])
        json.dumps(out, allow_nan=False)

    def test_empty_no_rules_and_invalid_contract_distinct(self):
        self.assertEqual(lc.inspect_trial(pd.DataFrame(), contract(), TASK)["status"], "unavailable")
        c = contract(); c["physiological_rules"] = []
        self.assertEqual(lc.inspect_trial(pd.DataFrame({"a": [1]}), c, TASK)["physiology"]["status"], "not_assessed")
        self.assertEqual(lc.inspect_trial(pd.DataFrame({"a": [1]}), {}, TASK)["status"], "invalid_contract")

    def test_declarative_payload_not_executable(self):
        c = contract(); c["physiological_rules"][0]["rationale"] = "__import__('os').remove('never')"
        result = lc.inspect_trial(pd.DataFrame({"a": [2.], "b": [1.]}), c, TASK)
        self.assertTrue(result["physiology"]["rules"][0]["passes_this_trial"])
        self.assertEqual(result["joint_relations"]["status"], "declarations_only_not_target_validated")


if __name__ == "__main__":
    unittest.main(verbosity=2)

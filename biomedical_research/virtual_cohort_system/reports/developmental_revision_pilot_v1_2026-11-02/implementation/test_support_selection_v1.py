"""Small deterministic metadata/arithmetic tests; no biomedical rows or sampling."""

from copy import deepcopy
import unittest

from support_selection_v1 import assess_support_selection, check_retained_frame, DeclarationError


def domain(lower=None, upper=None, lower_closed=False, upper_closed=False):
    return {"lower": lower, "upper": upper,
            "lower_closed": lower_closed, "upper_closed": upper_closed}


def affine(scale="1", shift="0", variable="x"):
    return {"kind": "affine", "variable": variable, "scale": scale, "shift": shift}


PROVENANCE = [{"kind": "assumption", "id": "A_LAW"}]
KNOWN = {"evidence": ["E_SCALE"], "assumption": ["A_LAW"], "definition": ["D_POSITIVE"]}


def fixture():
    context = {
        "final_supports": {"x": {"domain": domain("0"), "provenance": deepcopy(PROVENANCE)}},
        "native_views": {},
        "selection": {"route": "direct_eligible_joint", "exclusion_implementation": "not_claimed",
                      "conditioning_event": None, "description": "An assumed eligible joint law.",
                      "provenance": deepcopy(PROVENANCE)},
        "transformations": [], "derivations": [],
    }
    declaration = {"schema_version": "support_selection_v1", "contexts": {"S": context}}
    checks = {"S": [{"id": "positive", "variable": "x", "domain": domain("0")} ]}
    return declaration, checks


def assess(declaration, checks, **kwargs):
    return assess_support_selection(declaration, required_contexts=["S"], required_checks=checks,
                                    known_provenance=KNOWN, **kwargs)


def add_transform(declaration):
    declaration["contexts"]["S"]["transformations"] = [{
        "id": "cap", "kind": "clip", "variable": "x", "stage": 1,
        "role": "law_construction", "atom_effect": "creates",
        "description": "A disclosed hypothetical atom-containing eligible-law shape.",
        "provenance": deepcopy(PROVENANCE)}]


def add_derivation(declaration, claim, effect="invalidated"):
    declaration["contexts"]["S"]["derivations"] = [{
        "id": "identity", "claim": claim, "applicable_stage": 0,
        "transform_effects": {"cap": effect},
        "description": "A precursor identity whose final-law status is disclosed.",
        "provenance": deepcopy(PROVENANCE)}]


class SupportSelectionTests(unittest.TestCase):
    def assert_pass(self, report):
        self.assertEqual(report["status"], "declaration_checks_pass", report)
        self.assertFalse(report["law_support_verified"])
        self.assertEqual(report["actual_code_law_support"], "independent_review_required")
        self.assertFalse(report["source_point_fit_required"])

    def assert_fail(self, report, message=None):
        self.assertEqual(report["status"], "declaration_checks_fail", report)
        self.assertTrue(report["issues"])
        if message:
            self.assertIn(message, " ".join(item["message"] for item in report["issues"]))

    def test_direct_eligible_law_has_no_invented_upper_bound(self):
        declaration, checks = fixture()
        self.assert_pass(assess(declaration, checks))

    def test_old_positive_ngsp_lognormal_support_maps_to_negative_native_values(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["native_views"]["native"] = {
            "kind": "affine", "variable": "x", "scale": "25000/2287", "shift": "-53800/2287",
            "provenance": [{"kind": "evidence", "id": "E_SCALE"}]}
        checks["S"][0].update(native_view="native", native_mapping=affine("25000/2287", "-53800/2287"),
                              domain=domain("0", lower_closed=True))
        report = assess(declaration, checks)
        self.assert_fail(report, "violates required domain")
        self.assertEqual(report["checks"][0]["mapped_declared_support"]["lower"], "-53800/2287")

    def test_shifted_positive_support_uses_exact_native_mapping(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["final_supports"]["x"]["domain"] = domain("2.152")
        declaration["contexts"]["S"]["native_views"]["native"] = {
            "kind": "affine", "variable": "x", "scale": "25000/2287", "shift": "-53800/2287",
            "provenance": [{"kind": "evidence", "id": "E_SCALE"}]}
        checks["S"][0].update(native_view="native", native_mapping=affine("25000/2287", "-53800/2287"))
        report = assess(declaration, checks)
        self.assert_pass(report)
        self.assertEqual(report["checks"][0]["mapped_declared_support"]["lower"], "0")

    def test_strict_boundary_cannot_accept_closed_support_endpoint(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["final_supports"]["x"]["domain"] = domain("0", "1", False, True)
        checks["S"][0]["domain"] = domain("0", "1")
        self.assert_fail(assess(declaration, checks))
        declaration["contexts"]["S"]["final_supports"]["x"]["domain"]["upper_closed"] = False
        self.assert_pass(assess(declaration, checks))

    def test_negative_scale_reverses_bounds_and_closure(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["final_supports"]["x"]["domain"] = domain("0", "2", True, False)
        declaration["contexts"]["S"]["native_views"]["reverse"] = {
            "kind": "affine", "variable": "x", "scale": "-2", "shift": "3",
            "provenance": deepcopy(PROVENANCE)}
        checks["S"][0].update(native_view="reverse", native_mapping=affine("-2", "3"),
                              domain=domain("-1", "3", False, True))
        report = assess(declaration, checks)
        self.assert_pass(report)
        self.assertEqual(report["checks"][0]["mapped_declared_support"], domain("-1", "3", False, True))

    def test_negative_scale_handles_infinite_endpoint(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["native_views"]["reverse"] = {
            "kind": "affine", "variable": "x", "scale": "-1", "shift": "0",
            "provenance": deepcopy(PROVENANCE)}
        checks["S"][0].update(native_view="reverse", native_mapping=affine("-1", "0"), domain=domain(None, "0"))
        self.assert_pass(assess(declaration, checks))

    def test_conditional_joint_route_is_allowed_but_not_proved(self):
        declaration, checks = fixture()
        selection = declaration["contexts"]["S"]["selection"]
        selection.update(route="conditional_joint", exclusion_implementation="joint_conditioning",
                         conditioning_event={"description": "An assumed joint event.", "stage": 0})
        self.assert_pass(assess(declaration, checks))

    def test_clipping_cannot_claim_to_implement_exclusion(self):
        declaration, checks = fixture()
        add_transform(declaration)
        declaration["contexts"]["S"]["selection"]["exclusion_implementation"] = "clipping"
        self.assert_fail(assess(declaration, checks), "not joint exclusion")
        declaration["contexts"]["S"]["selection"]["exclusion_implementation"] = "not_claimed"
        declaration["contexts"]["S"]["transformations"][0]["role"] = "eligibility_selection"
        self.assert_fail(assess(declaration, checks), "cannot be declared eligibility exclusion")

    def test_disclosed_clipped_eligible_shape_is_not_automatically_prohibited(self):
        declaration, checks = fixture()
        add_transform(declaration)
        self.assert_pass(assess(declaration, checks))

    def test_transformed_model_requires_an_actual_declared_transform(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["selection"]["route"] = "transformed_variable_model"
        self.assert_fail(assess(declaration, checks), "must disclose")
        add_transform(declaration)
        self.assert_pass(assess(declaration, checks))

    def test_exact_final_identity_cannot_be_invalidated_unresolved_or_omitted(self):
        for effect in ("invalidated", "unresolved", None):
            with self.subTest(effect=effect):
                declaration, checks = fixture()
                add_transform(declaration)
                add_derivation(declaration, "exact_final_law", effect or "preserved")
                if effect is None:
                    declaration["contexts"]["S"]["derivations"][0]["transform_effects"] = {}
                self.assert_fail(assess(declaration, checks), "exact final-law identity")

    def test_exact_preservation_remains_an_independent_review_claim(self):
        declaration, checks = fixture()
        add_transform(declaration)
        add_derivation(declaration, "exact_final_law", "preserved")
        self.assert_pass(assess(declaration, checks))

    def test_approximate_or_initial_algebra_may_be_invalidated_after_transform(self):
        for claim in ("approximation", "initialization"):
            with self.subTest(claim=claim):
                declaration, checks = fixture()
                add_transform(declaration)
                add_derivation(declaration, claim)
                self.assert_pass(assess(declaration, checks))

    def test_missing_context_and_cross_artifact_context_mismatch_fail(self):
        declaration, checks = fixture()
        self.assert_fail(assess(declaration, checks, context_sets={
            "task": ["S"], "spec": ["S"], "evidence": [], "bridge": ["S"]}), "differ from release")
        declaration["contexts"] = {}
        self.assert_fail(assess(declaration, checks), "exactly match")

    def test_unknown_provenance_is_not_self_authorizing(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["final_supports"]["x"]["provenance"][0]["id"] = "UNADMITTED"
        self.assert_fail(assess(declaration, checks), "unknown provenance")

    def test_required_unknown_mapping_and_unsupported_mapping_fail(self):
        declaration, checks = fixture()
        checks["S"][0]["native_view"] = "unknown"
        checks["S"][0]["native_mapping"] = affine()
        self.assert_fail(assess(declaration, checks), "missing required native mapping")
        declaration["contexts"]["S"]["native_views"]["unknown"] = {
            "kind": "nonlinear", "variable": "x", "scale": "1", "shift": "0",
            "provenance": deepcopy(PROVENANCE)}
        self.assert_fail(assess(declaration, checks), "affine")

    def test_malformed_domains_and_float_metadata_fail(self):
        for bad in (domain("0", "0"), domain(None, None, True), domain(0.1), domain("NaN")):
            with self.subTest(bad=bad):
                declaration, checks = fixture()
                declaration["contexts"]["S"]["final_supports"]["x"]["domain"] = bad
                self.assert_fail(assess(declaration, checks))

    def test_unknown_fields_cannot_silently_change_semantics(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["selection"]["actually_clip"] = True
        self.assert_fail(assess(declaration, checks), "unknown keys")

    def test_runtime_reports_all_retained_values_without_filtering(self):
        declaration, checks = fixture()
        checks["S"][0]["domain"] = domain("0", "2")
        frame = {"x": [-1, 0, 1, 2, None, "NaN"]}
        original = deepcopy(frame)
        result = check_retained_frame(frame, context_id="S", declaration=declaration, required_checks=checks)
        self.assertEqual(frame, original)
        self.assertEqual(result["status"], "fail")
        self.assertFalse(result["mutated_or_filtered"])
        self.assertEqual(result["row_count"], 6)
        check = next(item for item in result["checks"] if item["check_role"] == "required_domain")
        self.assertEqual(check["outside_required_domain"], 3)
        self.assertEqual(check["invalid_or_nonfinite"], 2)
        self.assertEqual(check["within_required_domain"], 1)

    def test_runtime_uses_native_map_and_strict_boundary(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["native_views"]["native"] = {
            "kind": "affine", "variable": "x", "scale": "-1", "shift": "2",
            "provenance": deepcopy(PROVENANCE)}
        checks["S"][0].update(native_view="native", native_mapping=affine("-1", "2"), domain=domain("0"))
        result = check_retained_frame({"x": [0, 1, 2]}, context_id="S", declaration=declaration, required_checks=checks)
        check = next(item for item in result["checks"] if item["check_role"] == "required_domain")
        self.assertEqual(check["outside_required_domain"], 1)

    def test_runtime_checks_declared_support_even_when_release_domain_is_broader(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["final_supports"]["x"]["domain"] = domain("0", "2")
        self.assert_pass(assess(declaration, checks))
        result = check_retained_frame({"x": [1, 3]}, context_id="S", declaration=declaration, required_checks=checks)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["checks"][0]["check_role"], "declared_final_support")
        self.assertEqual(result["checks"][0]["outside_required_domain"], 1)

    def test_runtime_missing_column_empty_frame_and_unknown_mapping_do_not_pass(self):
        declaration, checks = fixture()
        for frame in ({}, {"x": []}):
            self.assertEqual(check_retained_frame(frame, context_id="S", declaration=declaration,
                                                 required_checks=checks)["status"], "fail")
        checks["S"][0]["native_view"] = "unknown"
        checks["S"][0]["native_mapping"] = affine()
        with self.assertRaises(DeclarationError):
            check_retained_frame({"x": [1]}, context_id="S", declaration=declaration, required_checks=checks)

    def test_runtime_missing_empty_or_duplicate_release_checks_are_rejected(self):
        declaration, checks = fixture()
        for invalid in ({}, {"S": []}, {"S": checks["S"] + checks["S"]}):
            with self.subTest(invalid=invalid), self.assertRaises(DeclarationError):
                check_retained_frame({"x": [1]}, context_id="S", declaration=declaration, required_checks=invalid)

    def test_native_view_requires_release_owned_mapping(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["native_views"]["native"] = {
            **affine(), "provenance": deepcopy(PROVENANCE)}
        checks["S"][0]["native_view"] = "native"
        self.assert_fail(assess(declaration, checks), "requires a release-owned native_mapping")
        with self.assertRaisesRegex(DeclarationError, "requires a release-owned native_mapping"):
            check_retained_frame({"x": [1]}, context_id="S", declaration=declaration, required_checks=checks)

    def test_counterfeit_constant_sign_scale_and_shift_maps_are_rejected_before_rows(self):
        class MustNotRead:
            def __getitem__(self, key):
                raise AssertionError("retained rows accessed before native-map identity check")

        for scale, shift in (("0", "1"), ("-1", "0"), ("2", "0"), ("1", "2")):
            with self.subTest(scale=scale, shift=shift):
                declaration, checks = fixture()
                declaration["contexts"]["S"]["native_views"]["native"] = {
                    **affine(scale, shift), "provenance": deepcopy(PROVENANCE)}
                checks["S"][0].update(native_view="native", native_mapping=affine(), domain=domain())
                self.assert_fail(assess(declaration, checks), "differs from release-owned exact mapping")
                with self.assertRaisesRegex(DeclarationError, "differs from release-owned exact mapping"):
                    check_retained_frame(MustNotRead(), context_id="S", declaration=declaration, required_checks=checks)

    def test_rational_equivalent_release_mapping_is_accepted(self):
        declaration, checks = fixture()
        declaration["contexts"]["S"]["native_views"]["native"] = {
            **affine("0.50", "1e-1"), "provenance": deepcopy(PROVENANCE)}
        checks["S"][0].update(native_view="native", native_mapping=affine("1/2", "1/10"), domain=domain("1/10"))
        self.assert_pass(assess(declaration, checks))
        report = check_retained_frame({"x": [1, 2]}, context_id="S", declaration=declaration, required_checks=checks)
        self.assertEqual(report["status"], "pass")


if __name__ == "__main__":
    unittest.main()

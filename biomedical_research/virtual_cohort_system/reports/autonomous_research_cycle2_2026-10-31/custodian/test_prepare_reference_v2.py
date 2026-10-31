"""V2 amendment tests cloned from independently reviewed v1; invented rows only.

Run from this directory with ``python -B -m unittest test_prepare_reference_v2``.
This module never opens participant files, emits a release, or fits an effect.
The expected decisions come from PROTOCOL.md and the selected measurement
adjudication, not from inspection of preparation implementation internals.
"""

import copy
import contextlib
import io
import json
import hashlib
import unittest
from unittest import mock

import prepare_reference_v2 as prep


ADMIT = "ADMIT_PAIR"
MISSING = "EXCLUDE_EXPLICIT_OR_MISSING"
QUALITY = "EXCLUDE_QUALITY_RESTRICTION"
CONSISTENCY = "EXCLUDE_DOCUMENTATION_CONSISTENCY"


def lab_row(age=40, sex=1, person=1):
    """Artificial lab input; deliberately different P6 and design metadata."""
    return {
        "UPM": "1", "VIV_SEL": "1", "HOGAR": "1", "NUMREN": str(person),
        "EDAD": str(age), "SEXO": str(sex), "P7": "2", "P5_1": "10",
        "VALOR_GLU_SUERO": "95", "VALOR_HB1AC": "5.2",
        "UPM_DIS": "00011", "EST_DIS": "007", "ESTRATO": "1",
        "ponderador_glucosa": "123.45", "FACTOR_SV_D": "321",
        "P3": "1", "P6": "SYNTHETIC_LABEL_ONLY",
    }


def anth_row(age=40, sex=1, person=1):
    """Artificial anthropometry with distinct under/over-60 block values."""
    return {
        "UPM": "00001", "VIV_SEL": "01", "HOGAR": "1",
        "NUMREN": f"{person:02d}", "EDAD": str(age), "SEXO": str(sex),
        "PESO1_1": "64.000", "PESO1_2": "64.000",
        "TALLA4_1": "160.0", "TALLA4_2": "160.0",
        "P2": "1", "P3": "1", "P5": "1", "P6": "4",
        "P7_1": "", "P10": "1", "P11": "4",
        "PESO12_1": "81.000", "PESO12_2": "81.000",
        "TALLA15_1": "180.0", "TALLA15_2": "180.0",
        "P13": "1", "P14": "1", "P16": "1",
        "TALLAPIE17_1": "50.0", "HEMIENVERGADURA23_1": "80.0",
        "UPM_DIS": "80011", "EST_DIS": "907", "ESTRATO": "4",
        "F_ANTROP": "456", "F_ANTROP_INSP": "654",
    }


def clear_active_readings(row, age):
    fields = ("PESO12_1", "PESO12_2", "TALLA15_1", "TALLA15_2") if age >= 60 else (
        "PESO1_1", "PESO1_2", "TALLA4_1", "TALLA4_2")
    for field in fields:
        row[field] = ""
    return row


class ContractCase(unittest.TestCase):
    def assert_hold(self, function, *args):
        with self.assertRaises(prep.PreparationHold) as caught:
            function(*args)
        issues = caught.exception.issues
        self.assertIsInstance(issues, list)
        self.assertTrue(issues)
        for issue in issues:
            self.assertEqual(set(issue), {"field", "reason", "count"})
            self.assertIsInstance(issue["field"], str)
            self.assertIsInstance(issue["reason"], str)
            self.assertIsInstance(issue["count"], int)
            self.assertGreater(issue["count"], 0)
        return issues

    def selected(self, row=None, age=40):
        return prep.select_standing_pair(anth_row(age) if row is None else row, age)

    def prepared(self, lab=None, anth=None, age=40, sex=1):
        return prep.prepare_records(
            [lab_row(age, sex) if lab is None else lab],
            [anth_row(age, sex) if anth is None else anth],
        )

    def assert_reference_count(self, expected, **kwargs):
        result = self.prepared(**kwargs)
        self.assertEqual(len(result["reference_rows"]), expected)
        return result


class IdentifierAndLinkageTests(ContractCase):
    def test_normalizes_integer_string_keys_with_documented_widths(self):
        expected = ("00001", "01", "1", "01")
        self.assertEqual(prep.normalize_key(lab_row(), "lab"), expected)
        self.assertEqual(prep.normalize_key(anth_row(), "anth"), expected)

    def test_rejects_float_scientific_malformed_and_missing_identifiers(self):
        for field in ("UPM", "VIV_SEL", "HOGAR", "NUMREN"):
            for value in ("1.0", "1e0", "-1", "NaN", "", "UNKNOWN_KEY"):
                with self.subTest(field=field, value=value):
                    row = lab_row()
                    row[field] = value
                    self.assert_hold(prep.normalize_key, row, "lab")

    def test_absent_identifier_is_hold(self):
        row = lab_row()
        del row["NUMREN"]
        self.assert_hold(prep.normalize_key, row, "lab")

    def test_join_preserves_every_original_field_with_module_suffix(self):
        lab, anth = lab_row(), anth_row()
        merged, counts = prep.join_tables([lab], [anth])
        self.assertEqual(len(merged), 1)
        self.assertEqual(counts, {"laboratory_rows": 1, "anthropometry_rows": 1,
                                  "linked_rows": 1, "laboratory_unmatched": 0,
                                  "anthropometry_unmatched": 0})
        result = merged[0]
        for suffix, original in (("lab", lab), ("anth", anth)):
            for field, value in original.items():
                self.assertEqual(result[f"{field}_{suffix}"], value)
        self.assertEqual(tuple(result[k] for k in ("UPM", "VIV_SEL", "HOGAR", "NUMREN")),
                         ("00001", "01", "1", "01"))
        self.assertNotEqual(result["P6_lab"], result["P6_anth"])
        self.assertNotEqual(result["EST_DIS_lab"], result["EST_DIS_anth"])

    def test_different_people_do_not_join(self):
        rows, counts = prep.join_tables([lab_row(person=1)], [anth_row(person=2)])
        self.assertEqual(rows, [])
        self.assertEqual(counts["linked_rows"], 0)
        self.assertEqual(counts["laboratory_unmatched"], 1)
        self.assertEqual(counts["anthropometry_unmatched"], 1)

    def test_duplicate_normalized_keys_in_either_table_hold(self):
        for module in ("lab", "anth"):
            with self.subTest(module=module):
                lab, anth = lab_row(), anth_row()
                if module == "lab":
                    duplicate = dict(lab, UPM="00001", VIV_SEL="01", NUMREN="01")
                    self.assert_hold(prep.join_tables, [lab, duplicate], [anth])
                else:
                    duplicate = dict(anth, UPM="1", VIV_SEL="1", NUMREN="1")
                    self.assert_hold(prep.join_tables, [lab], [anth, duplicate])

    def test_joined_age_or_sex_disagreement_holds(self):
        for field, value in (("EDAD", "41"), ("SEXO", "2")):
            with self.subTest(field=field):
                anth = anth_row()
                anth[field] = value
                self.assert_hold(prep.join_tables, [lab_row()], [anth])

    def test_functions_do_not_modify_input_rows(self):
        lab, anth = lab_row(), anth_row()
        original = copy.deepcopy((lab, anth))
        prep.join_tables([lab], [anth])
        prep.select_standing_pair(anth, 40)
        prep.prepare_records([lab], [anth])
        self.assertEqual((lab, anth), original)


class StandingPairTests(ContractCase):
    def test_age_59_and_60_select_different_official_blocks(self):
        for age, weight, height in ((59, 64, 160), (60, 81, 180)):
            with self.subTest(age=age):
                result = self.selected(age=age)
                self.assertEqual(result["decision"], ADMIT)
                self.assertEqual(float(result["weight_kg"]), weight)
                self.assertEqual(float(result["height_cm"]), height)
                self.assertEqual(result["repeat"], 1)
                self.assertIn("diagnostics", result)

    def test_first_complete_pair_has_priority_despite_discrepancy(self):
        row = anth_row()
        row.update(PESO1_2="100", TALLA4_2="200")
        result = self.selected(row)
        self.assertEqual(result["decision"], ADMIT)
        self.assertEqual(result["repeat"], 1)
        self.assertEqual(float(result["weight_kg"]), 64)
        self.assertEqual(float(result["height_cm"]), 160)
        self.assertTrue(result["diagnostics"]["weight_third_trigger"])
        self.assertTrue(result["diagnostics"]["height_third_trigger"])

    def test_exact_third_reading_boundaries_are_diagnostics_only(self):
        for age, height_trigger in ((59, False), (60, True)):
            with self.subTest(age=age):
                row = anth_row(age)
                if age < 60:
                    row.update(PESO1_2="64.4", TALLA4_2="161.0")
                else:
                    row.update(PESO12_2="81.4", TALLA15_2="181.0")
                result = self.selected(row, age)
                self.assertEqual(result["decision"], ADMIT)
                self.assertEqual(result["repeat"], 1)
                self.assertTrue(result["diagnostics"]["weight_third_trigger"])
                self.assertEqual(result["diagnostics"]["height_third_trigger"], height_trigger)

    def test_second_complete_pair_used_when_first_is_incomplete(self):
        row = anth_row()
        row.update(TALLA4_1="", PESO1_2="75", TALLA4_2="150")
        result = self.selected(row)
        self.assertEqual(result["decision"], ADMIT)
        self.assertEqual(result["repeat"], 2)
        self.assertEqual(float(result["weight_kg"]), 75)
        self.assertEqual(float(result["height_cm"]), 150)

    def test_readings_are_never_cross_mixed_or_reconstructed(self):
        row = anth_row()
        row.update(TALLA4_1="", PESO1_2="")
        result = self.selected(row)
        self.assertEqual(result["decision"], MISSING)
        self.assertNotIn("weight_kg", result)
        self.assertNotIn("height_cm", result)

    def test_numeric_sentinel_equivalence_and_unusable_first_readings_fall_back(self):
        for field, bad in (("PESO1_1", "222.2220"), ("TALLA4_1", "222.2000"),
                           ("PESO1_1", "0"), ("TALLA4_1", "-1"),
                           ("PESO1_1", "NaN"), ("TALLA4_1", "Infinity")):
            with self.subTest(field=field, value=bad):
                row = anth_row()
                row[field] = bad
                result = self.selected(row)
                self.assertEqual(result["decision"], ADMIT)
                self.assertEqual(result["repeat"], 2)

    def test_sentinels_in_second_reading_cannot_form_pair(self):
        row = anth_row()
        row.update(PESO1_1="", TALLA4_1="", PESO1_2="222.2220", TALLA4_2="222.2000")
        self.assertEqual(self.selected(row)["decision"], MISSING)

    def test_malformed_active_measurement_holds_without_disclosing_raw_value(self):
        row = anth_row()
        marker = "SYNTHETIC_UNPARSEABLE_READING"
        row["PESO1_1"] = marker
        issues = self.assert_hold(prep.select_standing_pair, row, 40)
        self.assertNotIn(marker, repr(issues))

    def test_documented_adverse_and_missing_result_codes_are_quality_exclusions(self):
        for age, fields in ((40, ("P3", "P5")), (65, ("P14", "P16"))):
            for field in fields:
                for value in ("2", "3", "9", ""):
                    with self.subTest(age=age, field=field, value=value):
                        row = anth_row(age)
                        row[field] = value
                        self.assertEqual(self.selected(row, age)["decision"], QUALITY)

    def test_second_repeat_cannot_bypass_quality_restriction(self):
        row = anth_row()
        row.update(PESO1_1="", P3="3")
        self.assertEqual(self.selected(row)["decision"], QUALITY)

    def test_missing_pair_is_distinct_from_quality_exclusion(self):
        row = clear_active_readings(anth_row(), 40)
        row.update(P3="2", P5="9")
        self.assertEqual(self.selected(row)["decision"], MISSING)

    def test_undocumented_active_result_codes_hold_even_without_a_pair(self):
        for age, field in ((40, "P3"), (40, "P5"), (65, "P14"), (65, "P16")):
            for value in ("0", "4", "8", "1.5", "NaN", "UNKNOWN_CODE"):
                with self.subTest(age=age, field=field, value=value):
                    row = clear_active_readings(anth_row(age), age)
                    row[field] = value
                    self.assert_hold(prep.select_standing_pair, row, age)

    def test_missing_required_active_field_is_schema_hold(self):
        row = anth_row()
        del row["PESO1_2"]
        self.assert_hold(prep.select_standing_pair, row, 40)

    def test_inactive_age_block_and_unrelated_flags_do_not_gate_pair(self):
        younger = anth_row(59)
        younger.update(P11="UNKNOWN", P13="9", P14="BAD", P16="BAD",
                       PESO12_1="BAD", P9="9", P18="3", P30="4", P10="3")
        self.assertEqual(self.selected(younger, 59)["decision"], ADMIT)
        older = anth_row(60)
        older.update(P2="BAD", P3="BAD", P5="BAD", PESO1_1="BAD", P30="4")
        self.assertEqual(self.selected(older, 60)["decision"], ADMIT)


class RouteAndClothingTests(ContractCase):
    def test_q11_codes_one_and_four_allow_standing_pair(self):
        for code in ("1", "4"):
            with self.subTest(code=code):
                row = anth_row(65)
                row["P11"] = code
                self.assertEqual(self.selected(row, 65)["decision"], ADMIT)

    def test_q11_alternative_routes_without_standing_values_exclude(self):
        for code in ("2", "3", "5", "6"):
            with self.subTest(code=code):
                row = clear_active_readings(anth_row(65), 65)
                row["P11"] = code
                self.assertEqual(self.selected(row, 65)["decision"], MISSING)

    def test_q11_alternative_route_with_any_standing_value_is_consistency_exclusion(self):
        for code in ("2", "3", "5", "6"):
            for field in ("PESO12_1", "PESO12_2", "TALLA15_1", "TALLA15_2"):
                with self.subTest(code=code, field=field):
                    row = clear_active_readings(anth_row(65), 65)
                    row.update(P11=code)
                    row[field] = "60"
                    selected = self.selected(row, 65)
                    self.assertEqual(selected["decision"], CONSISTENCY)
                    self.assertEqual(selected["reason"], "alternative_route_with_standing_values")

    def test_unknown_route_is_quality_exclusion_and_undocumented_route_holds(self):
        row = anth_row(65)
        row["P11"] = ""
        self.assertEqual(self.selected(row, 65)["decision"], QUALITY)
        row["P11"] = "9"
        self.assert_hold(prep.select_standing_pair, row, 65)

    def test_documented_clothing_and_blank_do_not_change_weight(self):
        for age, field in ((40, "P2"), (65, "P13")):
            for code in ("1", "2", "3", ""):
                with self.subTest(age=age, code=code):
                    row = anth_row(age)
                    row[field] = code
                    result = self.selected(row, age)
                    self.assertEqual(result["decision"], ADMIT)
                    self.assertEqual(float(result["weight_kg"]), 81 if age >= 60 else 64)

    def test_unknown_clothing_code_nine_is_defined_only_for_p2(self):
        younger = anth_row()
        younger["P2"] = "9"
        self.assertEqual(self.selected(younger)["decision"], ADMIT)
        older = anth_row(65)
        older["P13"] = "9"
        self.assert_hold(prep.select_standing_pair, older, 65)

    def test_not_weighed_with_positive_weight_is_consistency_exclusion(self):
        for age, field in ((40, "P2"), (65, "P13")):
            with self.subTest(age=age):
                row = anth_row(age)
                row[field] = "4"
                selected = self.selected(row, age)
                self.assertEqual(selected["decision"], CONSISTENCY)
                self.assertEqual(selected["reason"], "not_weighed_with_numeric_weight")

    def test_not_weighed_without_usable_weight_is_explicit_exclusion(self):
        for age, field, wfields in ((40, "P2", ("PESO1_1", "PESO1_2")),
                                    (65, "P13", ("PESO12_1", "PESO12_2"))):
            with self.subTest(age=age):
                row = anth_row(age)
                row[field] = "4"
                row[wfields[0]], row[wfields[1]] = "222.222", ""
                self.assertEqual(self.selected(row, age)["decision"], MISSING)


class ReferenceEligibilityTests(ContractCase):
    def test_reference_units_and_lab_design_provenance(self):
        result = self.assert_reference_count(1)
        row = result["reference_rows"][0]
        self.assertEqual(set(row), {"age", "female", "bmi", "glucose", "hba1c",
                                   "lab_upm_dis", "lab_est_dis"})
        self.assertEqual(row["age"], 40)
        self.assertEqual(row["female"], 0)
        self.assertAlmostEqual(float(row["bmi"]), 25.0, places=12)
        self.assertEqual(float(row["glucose"]), 95)
        self.assertEqual(float(row["hba1c"]), 5.2)
        self.assertEqual(row["lab_upm_dis"], "00011")
        self.assertEqual(row["lab_est_dis"], "007")
        for key in ("flow", "readiness", "joined_rows", "private_diagnostics"):
            self.assertIn(key, result)
        self.assertFalse(result["readiness"]["ready"])
        self.assertEqual(result["readiness"]["total_rows"], 1)
        self.assertEqual(len(result["readiness"]["cell_counts"]), 8)
        self.assertEqual(sum(result["readiness"]["cell_counts"].values()), 1)

    def test_bmi_uses_the_selected_second_complete_pair(self):
        anth = anth_row()
        anth.update(TALLA4_1="", PESO1_2="75", TALLA4_2="150")
        result = self.assert_reference_count(1, anth=anth)
        self.assertAlmostEqual(float(result["reference_rows"][0]["bmi"]), 75 / 2.25, places=12)

    def test_inclusive_age_bounds(self):
        for age, expected in ((24, 0), (25, 1), (79, 1), (80, 0)):
            with self.subTest(age=age):
                self.assert_reference_count(expected, age=age)

    def test_female_indicator_and_neither_status_at_both_routing_boundaries(self):
        for age in (25, 49):
            with self.subTest(age=age):
                result = self.assert_reference_count(1, age=age, sex=2)
                self.assertEqual(result["reference_rows"][0]["female"], 1)

    def test_female_25_to_49_other_documented_or_missing_statuses_exclude(self):
        for code in ("1", "2", "3", "9", ""):
            with self.subTest(code=code):
                anth = anth_row(40, 2)
                anth["P6"] = code
                self.assert_reference_count(0, lab=lab_row(40, 2), anth=anth)

    def test_unknown_active_physiological_status_holds(self):
        for code in ("0", "8", "1.5", "UNKNOWN_CODE"):
            with self.subTest(code=code):
                anth = anth_row(40, 2)
                anth["P6"] = code
                self.assert_hold(prep.prepare_records, [lab_row(40, 2)], [anth])

    def test_p6_and_pregnancy_months_not_imputed_or_required_outside_route(self):
        for age, sex in ((40, 1), (50, 2), (65, 2)):
            with self.subTest(age=age, sex=sex):
                anth = anth_row(age, sex)
                anth.update(P6="UNKNOWN_UNASKED", P7_1="UNKNOWN_UNASKED")
                self.assert_reference_count(1, lab=lab_row(age, sex), anth=anth)

    def test_pregnancy_months_not_required_when_p6_is_four(self):
        anth = anth_row(40, 2)
        anth.update(P6="4", P7_1="")
        self.assert_reference_count(1, lab=lab_row(40, 2), anth=anth)

    def test_prior_diabetes_documented_and_missing_codes_exclude(self):
        for code in ("1", "3", "9", ""):
            with self.subTest(code=code):
                lab = lab_row()
                lab["P7"] = code
                self.assert_reference_count(0, lab=lab)

    def test_unknown_diabetes_code_holds(self):
        for code in ("0", "4", "8", "1.5", "UNKNOWN_CODE"):
            with self.subTest(code=code):
                lab = lab_row()
                lab["P7"] = code
                self.assert_hold(prep.prepare_records, [lab], [anth_row()])

    def test_fasting_eight_and_twelve_hours_are_inclusive(self):
        for hours, expected in (("7", 0), ("8", 1), ("12", 1), ("13", 0), ("", 0)):
            with self.subTest(hours=hours):
                lab = lab_row()
                lab["P5_1"] = hours
                self.assert_reference_count(expected, lab=lab)

    def test_malformed_or_nonintegral_recorded_fasting_is_hold(self):
        for hours in ("8.5", "UNKNOWN_HOURS"):
            with self.subTest(hours=hours):
                lab = lab_row()
                lab["P5_1"] = hours
                self.assert_hold(prep.prepare_records, [lab], [anth_row()])

    def test_glucose_upper_bound_is_strict(self):
        for glucose, expected in (("125.999", 1), ("126", 0), ("127", 0)):
            with self.subTest(glucose=glucose):
                lab = lab_row()
                lab["VALOR_GLU_SUERO"] = glucose
                self.assert_reference_count(expected, lab=lab)

    def test_float_rounding_across_strict_glucose_boundary_holds_without_clipping(self):
        lab = lab_row()
        lab["VALOR_GLU_SUERO"] = "125.999999999999999999"
        issues = self.assert_hold(prep.prepare_records, [lab], [anth_row()])
        self.assertEqual(issues, [{"field": "conversion.glucose",
                                  "reason": "strict_boundary_crossed_by_float_conversion", "count": 1}])

    def test_missing_nonpositive_or_nonfinite_biomarkers_exclude(self):
        for field in ("VALOR_GLU_SUERO", "VALOR_HB1AC"):
            for value in ("", "0", "-1", "NaN", "Infinity"):
                with self.subTest(field=field, value=value):
                    lab = lab_row()
                    lab[field] = value
                    self.assert_reference_count(0, lab=lab)

    def test_malformed_biomarker_text_is_hold(self):
        for field in ("VALOR_GLU_SUERO", "VALOR_HB1AC"):
            with self.subTest(field=field):
                lab = lab_row()
                lab[field] = "SYNTHETIC_UNPARSEABLE_BIOMARKER"
                self.assert_hold(prep.prepare_records, [lab], [anth_row()])

    def test_two_coding_errors_aggregate_without_identifiers_or_raw_values(self):
        labs = [lab_row(person=1), lab_row(person=2)]
        anth = [anth_row(person=1), anth_row(person=2)]
        markers = ("SYNTHETIC_BAD_CODE_ALPHA", "SYNTHETIC_BAD_CODE_BETA")
        for row, marker in zip(anth, markers):
            row["P3"] = marker
        issues = self.assert_hold(prep.prepare_records, labs, anth)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["field"], "anthropometry.P3")
        self.assertEqual(issues[0]["count"], 2)
        for marker in markers:
            self.assertNotIn(marker, repr(issues))
        self.assertNotIn("NUMREN", repr(issues))
        self.assertNotIn("joined_ordinal", repr(issues))

    def test_no_unstated_hba1c_upper_threshold_or_bmi_plausibility_filter(self):
        lab = lab_row()
        lab["VALOR_HB1AC"] = "12"
        anth = anth_row()
        anth.update(PESO1_1="180", PESO1_2="180", TALLA4_1="150", TALLA4_2="150")
        result = self.assert_reference_count(1, lab=lab, anth=anth)
        self.assertEqual(float(result["reference_rows"][0]["hba1c"]), 12)
        self.assertAlmostEqual(float(result["reference_rows"][0]["bmi"]), 80)

    def test_lab_design_identifiers_cannot_be_float_cast_or_missing(self):
        for field in ("UPM_DIS", "EST_DIS"):
            for value in ("11.0", "", "UNKNOWN_DESIGN"):
                with self.subTest(field=field, value=value):
                    lab = lab_row()
                    lab[field] = value
                    self.assert_hold(prep.prepare_records, [lab], [anth_row()])


class SyntheticReadinessAndGateTests(ContractCase):
    @staticmethod
    def invented_reference():
        rows = []
        for low, high in ((25, 39), (40, 54), (55, 69), (70, 79)):
            for female in (0, 1):
                for j in range(50):
                    rows.append({"age": low + j % (high - low + 1), "female": female,
                                 "bmi": 18 + j % 7 + (j // 7) * 0.03,
                                 "glucose": 80 + (j * 7) % 40,
                                 "hba1c": 4.8 + (j % 11) * 0.1,
                                 "lab_upm_dis": "00011", "lab_est_dis": "007"})
        return rows

    @staticmethod
    def invented_grid(cell_sizes):
        labs, anthropometry = [], []
        bands = ((25, 39), (40, 54), (55, 69), (70, 79))
        for cell, size in enumerate(cell_sizes):
            low, high = bands[cell // 2]
            sex = cell % 2 + 1
            for j in range(size):
                age = low + j % (high - low + 1)
                lab, anth = lab_row(age, sex, j + 1), anth_row(age, sex, j + 1)
                lab["UPM"], anth["UPM"] = str(cell + 1), f"{cell + 1:05d}"
                lab["VALOR_GLU_SUERO"] = str(80 + (j * 7) % 40)
                lab["VALOR_HB1AC"] = str(4.8 + (j % 11) / 10)
                wfields, hfields = (("PESO12_1", "PESO12_2"), ("TALLA15_1", "TALLA15_2")) if age >= 60 else (
                    ("PESO1_1", "PESO1_2"), ("TALLA4_1", "TALLA4_2"))
                for field in wfields:
                    anth[field] = str(60 + 2 * (j % 7) + (j // 7) / 10)
                for field in hfields:
                    anth[field] = str(160 + j % 5)
                labs.append(lab)
                anthropometry.append(anth)
        return labs, anthropometry

    def test_four_hundred_artificial_complete_rows_can_meet_readiness(self):
        labs, anth = self.invented_grid([50] * 8)
        result = prep.prepare_records(labs, anth)
        readiness = result["readiness"]
        self.assertEqual(len(result["reference_rows"]), 400)
        self.assertEqual(readiness["total_rows"], 400)
        self.assertEqual(sorted(readiness["cell_counts"].values()), [50] * 8)
        self.assertEqual(readiness["minimum_total"], 400)
        self.assertEqual(readiness["minimum_per_cell"], 30)
        self.assertTrue(readiness["all_five_nonconstant"])
        self.assertTrue(all(readiness["full_rank_designs"].values()))
        self.assertTrue(readiness["ready"])

    def test_total_and_per_cell_readiness_floors_are_both_required(self):
        for sizes in ([49] + [50] * 7, [29, 71] + [50] * 6):
            with self.subTest(sizes=sizes):
                labs, anth = self.invented_grid(sizes)
                result = prep.prepare_records(labs, anth)
                self.assertEqual(result["readiness"]["total_rows"], sum(sizes))
                self.assertFalse(result["readiness"]["ready"])

    def test_constant_biomarker_fails_readiness_without_fitting_an_effect(self):
        labs, anth = self.invented_grid([50] * 8)
        for lab in labs:
            lab["VALOR_HB1AC"] = "5.2"
        result = prep.prepare_records(labs, anth)
        self.assertEqual(result["readiness"]["total_rows"], 400)
        self.assertFalse(result["readiness"]["all_five_nonconstant"])
        self.assertFalse(result["readiness"]["ready"])

    def test_independent_reference_design_ready_but_exact_collinearity_fails(self):
        rows = self.invented_reference()
        ready = prep.readiness_counts(rows)
        self.assertTrue(ready["ready"])
        self.assertTrue(all(ready["full_rank_designs"].values()))
        for row in rows:
            row["glucose"] = 60 + 2 * row["bmi"]
        collinear = prep.readiness_counts(rows)
        self.assertEqual(collinear["total_rows"], 400)
        self.assertTrue(collinear["all_five_nonconstant"])
        self.assertFalse(collinear["full_rank_designs"]["Q1_Q3"])
        self.assertFalse(collinear["ready"])
        self.assertEqual(set(collinear), {"ready", "total_rows", "cell_counts",
                                         "minimum_total", "minimum_per_cell",
                                         "all_five_nonconstant", "full_rank_designs"})
        self.assertTrue(all(isinstance(value, bool) for value in collinear["full_rank_designs"].values()))

    def test_pure_preparation_never_opens_any_file(self):
        with mock.patch("builtins.open", side_effect=AssertionError("Unexpected file access")), \
             mock.patch.object(prep.Path, "read_bytes", side_effect=AssertionError("Unexpected file read")), \
             mock.patch.object(prep.Path, "read_text", side_effect=AssertionError("Unexpected file read")):
            result = self.prepared()
        self.assertEqual(len(result["reference_rows"]), 1)

    def test_missing_release_stops_before_any_input_or_output_access(self):
        # All existence/byte reads are mocked; no temporary directory or release
        # is created, and the real task release path is never inspected.
        with mock.patch.object(prep.Path, "is_file", return_value=False), \
             mock.patch.object(prep.Path, "read_bytes", side_effect=AssertionError("Unexpected byte read")), \
             mock.patch.object(prep.Path, "open", side_effect=AssertionError("Unexpected file open")), \
             mock.patch.object(prep, "_load_private_inputs", side_effect=AssertionError("Unexpected input load")) as load:
            issues = self.assert_hold(prep.run_authorized, "C:/SYNTHETIC_UNIT_TEST_ROOT_NOT_CREATED")
        load.assert_not_called()
        self.assertEqual(issues, [{"field": "release", "reason": "missing_root_preparation_release", "count": 1}])

    def test_manually_constructed_release_token_cannot_bypass_missing_release(self):
        fake = prep.VerifiedRelease(root=prep.Path("C:/SYNTHETIC_UNIT_TEST_ROOT_NOT_CREATED"),
                                    release_sha256="0" * 64, release_id="invented-token", bindings={})
        with mock.patch.object(prep.Path, "is_file", return_value=False), \
             mock.patch.object(prep.Path, "read_bytes", side_effect=AssertionError("Unexpected byte read")), \
             mock.patch.object(prep.Path, "open", side_effect=AssertionError("Unexpected file open")):
            issues = self.assert_hold(prep._load_private_inputs, fake)
        self.assertEqual(issues[0]["field"], "release")
        self.assertEqual(issues[0]["reason"], "missing_root_preparation_release")

    def test_cli_override_rejected_without_invoking_preparation(self):
        output = io.StringIO()
        with mock.patch.object(prep.sys, "argv", ["prepare_reference_v2.py", "--force"]), \
             mock.patch.object(prep, "run_authorized", side_effect=AssertionError("Unexpected preparation")) as run, \
             contextlib.redirect_stdout(output):
            exit_code = prep.main()
        self.assertEqual(exit_code, 2)
        run.assert_not_called()
        self.assertEqual(json.loads(output.getvalue()), {
            "status": "HOLD", "issues": [{"field": "CLI", "reason": "no_override_arguments_supported", "count": 1}]})


class MockedReleaseHashTests(ContractCase):
    """All byte reads are mock dictionary lookups; no release/file is written."""
    def fixture(self):
        root = prep.Path("C:/SYNTHETIC_UNIT_TEST_ROOT_NOT_CREATED").resolve()
        paths = {**prep.FIXED_BINDINGS, "analysis_engine": "method/invented_engine.py",
                 "independent_review": "review/invented_review.md"}
        payloads = {path: ("ARTIFICIAL METADATA " + name).encode() for name, path in paths.items()}
        payloads[paths["prior_attempt"]] = json.dumps({
            "release_sha256": hashlib.sha256(payloads[paths["prior_release"]]).hexdigest()}).encode()
        payloads[paths["prior_hold"]] = json.dumps({"status": "HOLD", "issues": []}).encode()
        ledger = {"artifacts": [{"id": spec["archive_id"], "status": "complete",
                    "zip_members": [{"local_relative_path": spec["path"].removeprefix("custodian/"),
                                     "sha256": spec["sha256"]}]} for spec in prep.INPUTS.values()]}
        payloads[paths["download_ledger"]] = json.dumps(ledger).encode()
        release = {"schema": "ensanut_preparation_release_v2", "release_id": "ARTIFICIAL-ONLY",
                   "issuer": "root", "status": "approved", "purpose": "prepare_reference_only",
                   "effects_authorized": False, "attempt_number": 2, "attempt_budget": 1,
                   "bindings": {name: {"path": path, "sha256": hashlib.sha256(payloads[path]).hexdigest()}
                                for name, path in paths.items()},
                   "inputs": {name: {k: spec[k] for k in ("path", "sha256")}
                              for name, spec in prep.INPUTS.items()}}
        payloads["PREPARATION_RELEASE_v2.json"] = json.dumps(release).encode()
        return root, payloads, release

    @contextlib.contextmanager
    def mocked_reads(self, root, payloads, allow_fake_bad_input=False):
        def read_bytes(path):
            relative = path.relative_to(root).as_posix()
            if "/private/" in relative:
                if allow_fake_bad_input:
                    return b"ARTIFICIAL WRONG INPUT BYTES; NOT A PARTICIPANT FILE"
                raise AssertionError("Gate tried to read a private input")
            return payloads[relative]
        def read_text(path, encoding=None):
            return read_bytes(path).decode(encoding or "utf-8")
        with mock.patch.object(prep.Path, "is_file", return_value=True), \
             mock.patch.object(prep.Path, "read_bytes", read_bytes), \
             mock.patch.object(prep.Path, "read_text", read_text), \
             mock.patch.object(prep.Path, "open", side_effect=AssertionError("Unexpected file open")):
            yield

    def test_matching_metadata_release_can_validate_without_private_access(self):
        root, payloads, release = self.fixture()
        with self.mocked_reads(root, payloads):
            gate = prep.verify_release(root)
        self.assertEqual(gate.release_id, "ARTIFICIAL-ONLY")
        self.assertEqual(gate.bindings, release["bindings"])

    def test_every_bound_file_hash_is_checked_before_private_access(self):
        for name in set(prep.FIXED_BINDINGS) | {"analysis_engine", "independent_review"}:
            with self.subTest(binding=name):
                root, payloads, release = self.fixture()
                payloads[release["bindings"][name]["path"]] += b" TAMPERED"
                with self.mocked_reads(root, payloads):
                    issues = self.assert_hold(prep.verify_release, root)
                self.assertEqual(issues[0]["field"], "release." + name)
                self.assertEqual(issues[0]["reason"], "file_hash_mismatch")

    def test_input_identity_cannot_be_replaced_by_a_different_declared_hash(self):
        root, payloads, release = self.fixture()
        release["inputs"]["laboratory"]["sha256"] = "0" * 64
        payloads["PREPARATION_RELEASE_v2.json"] = json.dumps(release).encode()
        with self.mocked_reads(root, payloads):
            issues = self.assert_hold(prep.verify_release, root)
        self.assertEqual(issues[0]["reason"], "pinned_inputs_mismatch")

    def test_matching_ledger_file_hash_still_requires_correct_archive_member_hash(self):
        root, payloads, release = self.fixture()
        path = release["bindings"]["download_ledger"]["path"]
        ledger = json.loads(payloads[path])
        ledger["artifacts"][0]["zip_members"][0]["sha256"] = "0" * 64
        payloads[path] = json.dumps(ledger).encode()
        release["bindings"]["download_ledger"]["sha256"] = hashlib.sha256(payloads[path]).hexdigest()
        payloads["PREPARATION_RELEASE_v2.json"] = json.dumps(release).encode()
        with self.mocked_reads(root, payloads):
            issues = self.assert_hold(prep.verify_release, root)
        self.assertEqual(issues[0]["reason"], "input_not_bound_to_download_ledger")

    def test_stale_forged_token_is_revalidated_before_any_private_access(self):
        root, payloads, release = self.fixture()
        fake = prep.VerifiedRelease(root, "0" * 64, "ARTIFICIAL-ONLY", release["bindings"])
        with self.mocked_reads(root, payloads):
            issues = self.assert_hold(prep._load_private_inputs, fake)
        self.assertEqual(issues[0]["reason"], "release_changed_before_input_read")

    def test_actual_byte_hash_mismatch_blocks_csv_parsing_with_mock_bytes_only(self):
        root, payloads, _ = self.fixture()
        with self.mocked_reads(root, payloads, allow_fake_bad_input=True), \
             mock.patch.object(prep.csv, "DictReader", side_effect=AssertionError("Unexpected CSV parse")) as parse:
            gate = prep.verify_release(root)
            issues = self.assert_hold(prep._load_private_inputs, gate)
        parse.assert_not_called()
        self.assertEqual(issues[0]["reason"], "actual_file_hash_mismatch")

    def test_private_binding_path_and_traversal_are_rejected_case_insensitively(self):
        root, _, _ = self.fixture()
        for relative in ("custodian/private/input.csv", "custodian/PRIVATE/input.csv",
                         "../outside.py", "D:/outside.py"):
            with self.subTest(relative=relative):
                self.assert_hold(prep._safe_nonprivate_path, root, relative)

    def test_prior_attempt_prevents_another_load_or_output_open(self):
        root, _, release = self.fixture()
        fake = prep.VerifiedRelease(root, "0" * 64, "ARTIFICIAL-ONLY", release["bindings"])
        with mock.patch.object(prep, "verify_release", return_value=fake), \
             mock.patch.object(prep.Path, "exists", return_value=True), \
             mock.patch.object(prep.Path, "open", side_effect=AssertionError("Unexpected output open")), \
             mock.patch.object(prep, "_load_private_inputs", side_effect=AssertionError("Unexpected input load")) as load:
            issues = self.assert_hold(prep.run_authorized, root)
        load.assert_not_called()
        self.assertEqual(issues[0]["reason"], "prior_attempt_or_output_exists")


class UniformConsistencyAmendmentTests(ContractCase):
    def test_both_age_blocks_sexes_and_ordinals_apply_the_same_clothing_rule(self):
        for age in (25, 49, 59, 60, 79):
            for sex in (1, 2):
                for ordinal in (1, 2):
                    with self.subTest(age=age, sex=sex, ordinal=ordinal):
                        row = clear_active_readings(anth_row(age, sex), age)
                        clothing = "P13" if age >= 60 else "P2"
                        weight = f"PESO12_{ordinal}" if age >= 60 else f"PESO1_{ordinal}"
                        row[clothing], row[weight] = "4", "70"
                        selected = self.selected(row, age)
                        self.assertEqual(selected["decision"], CONSISTENCY)
                        self.assertEqual(selected["reason"], "not_weighed_with_numeric_weight")
                        self.assertNotIn("weight_kg", selected)

    def test_contradictory_first_or_second_reading_cannot_be_rescued_by_other_pair(self):
        for age, clothing in ((40, "P2"), (65, "P13")):
            row = anth_row(age)
            row[clothing] = "4"
            selected = self.selected(row, age)
            self.assertEqual(selected["decision"], CONSISTENCY)
            self.assertNotIn("repeat", selected)

    def test_alternative_route_precedes_clothing_if_both_conflict(self):
        row = anth_row(65)
        row.update(P11="2", P13="4")
        selected = self.selected(row, 65)
        self.assertEqual(selected["decision"], CONSISTENCY)
        self.assertEqual(selected["reason"], "alternative_route_with_standing_values")

    def test_undocumented_or_malformed_active_fields_still_hold_before_consistency_rule(self):
        for age, fields in ((40, ("P3", "P5")), (65, ("P14", "P16", "P11"))):
            for field in fields:
                row = anth_row(age)
                row["P13" if age >= 60 else "P2"] = "4"
                row[field] = "UNDECLARED_ARTIFICIAL_CODE"
                self.assert_hold(prep.select_standing_pair, row, age)
            row = anth_row(age)
            row["P13" if age >= 60 else "P2"] = "4"
            row["PESO12_1" if age >= 60 else "PESO1_1"] = "MALFORMED_ARTIFICIAL_MEASUREMENT"
            self.assert_hold(prep.select_standing_pair, row, age)

    def test_consistency_reasons_are_separate_counted_flow_and_not_silent_drops(self):
        labs, anthropometry = [], []
        for person, (age, clothing, route) in enumerate(
                [(40, "4", "4"), (65, "4", "4"), (65, "1", "2"),
                 (65, "1", "3"), (65, "1", "5"), (65, "1", "6"), (40, "1", "4")], 1):
            lab, anth = lab_row(age, person=person), anth_row(age, person=person)
            anth["P13" if age >= 60 else "P2"] = clothing
            anth["P11"] = route
            labs.append(lab)
            anthropometry.append(anth)
        prepared = prep.prepare_records(labs, anthropometry)
        self.assertEqual(len(prepared["reference_rows"]), 1)
        expected = {"alternative_route_with_standing_values": 4, "not_weighed_with_numeric_weight": 2}
        self.assertEqual(prepared["flow"]["consistency_exclusion_reasons"], expected)
        self.assertEqual(prepared["flow"]["measurement_exclusion_reasons"], expected)
        self.assertEqual(prepared["flow"]["remaining_after_stage"]["pregnancy_lactation_rule"], 7)
        self.assertEqual(prepared["flow"]["remaining_after_stage"]["standing_pair_and_quality"], 1)
        self.assertEqual(sum(a["decision"] == CONSISTENCY for a in prepared["private_diagnostics"]), 6)

    def test_unamended_artificial_output_matches_frozen_v1_functions(self):
        import prepare_reference as version1
        labs, anth = SyntheticReadinessAndGateTests.invented_grid([50] * 8)
        old = version1.prepare_records(labs, anth)
        new = prep.prepare_records(labs, anth)
        self.assertEqual(old["reference_rows"], new["reference_rows"])
        self.assertEqual(old["joined_rows"], new["joined_rows"])
        self.assertEqual(old["readiness"], new["readiness"])
        self.assertEqual(old["private_diagnostics"], new["private_diagnostics"])
        new_flow = dict(new["flow"])
        self.assertEqual(new_flow.pop("consistency_exclusion_reasons"), {
            "alternative_route_with_standing_values": 0, "not_weighed_with_numeric_weight": 0})
        self.assertEqual(old["flow"], new_flow)


class SecondAttemptVersioningTests(ContractCase):
    fixture = MockedReleaseHashTests.fixture
    mocked_reads = MockedReleaseHashTests.mocked_reads

    def test_second_attempt_number_and_single_attempt_budget_are_required(self):
        for field, value in (("attempt_number", 1), ("attempt_number", 3), ("attempt_budget", 2)):
            root, payloads, release = self.fixture()
            release[field] = value
            payloads["PREPARATION_RELEASE_v2.json"] = json.dumps(release).encode()
            with self.mocked_reads(root, payloads):
                self.assert_hold(prep.verify_release, root)

    def test_first_release_alone_cannot_authorize_v2(self):
        with mock.patch.object(prep.Path, "is_file", lambda p: p.name != "PREPARATION_RELEASE_v2.json"), \
             mock.patch.object(prep.Path, "read_bytes", side_effect=AssertionError("Unexpected read")):
            self.assert_hold(prep.verify_release, prep.Path("C:/SYNTHETIC_UNIT_TEST_ROOT_NOT_CREATED"))

    def test_rehashed_but_inconsistent_prior_attempt_history_still_holds(self):
        root, payloads, release = self.fixture()
        path = release["bindings"]["prior_attempt"]["path"]
        payloads[path] = json.dumps({"release_sha256": "0" * 64}).encode()
        release["bindings"]["prior_attempt"]["sha256"] = hashlib.sha256(payloads[path]).hexdigest()
        payloads["PREPARATION_RELEASE_v2.json"] = json.dumps(release).encode()
        with self.mocked_reads(root, payloads):
            issues = self.assert_hold(prep.verify_release, root)
        self.assertEqual(issues[0]["reason"], "failed_first_attempt_history_mismatch")

    def test_all_existing_v1_or_v2_success_outputs_block_before_read_or_write(self):
        root, _, release = self.fixture()
        fake = prep.VerifiedRelease(root, "0" * 64, "ARTIFICIAL-ONLY", release["bindings"])
        protected = ["reference.csv", "linked_source.csv", "measurement_audit.json",
                     "reference_v2.csv", "linked_source_v2.csv", "measurement_audit_v2.json",
                     "PREPARATION_RECEIPT.json", "PREPARATION_RECEIPT_v2.json", "PREPARATION_HOLD_v2.json"]
        for present in protected:
            with self.subTest(present=present), \
                 mock.patch.object(prep, "verify_release", return_value=fake), \
                 mock.patch.object(prep.Path, "exists", lambda p: p.name == present), \
                 mock.patch.object(prep.Path, "open", side_effect=AssertionError("Unexpected output open")), \
                 mock.patch.object(prep, "_load_private_inputs", side_effect=AssertionError("Unexpected input load")) as load:
                self.assert_hold(prep.run_authorized, root)
            load.assert_not_called()

    def test_failed_v2_opens_only_new_exclusive_attempt_and_hold_files(self):
        root, _, release = self.fixture()
        fake = prep.VerifiedRelease(root, "0" * 64, "ARTIFICIAL-ONLY", release["bindings"])
        opened = []
        def fake_open(path, mode, *args, **kwargs):
            opened.append((path.name, mode))
            self.assertIn(path.name, {"PREPARATION_ATTEMPT_v2.json", "PREPARATION_HOLD_v2.json"})
            self.assertEqual(mode, "xb")
            return io.BytesIO()
        with mock.patch.object(prep, "verify_release", return_value=fake), \
             mock.patch.object(prep.Path, "exists", lambda p: p.name == "PREPARATION_ATTEMPT.json"), \
             mock.patch.object(prep.Path, "open", fake_open), \
             mock.patch.object(prep, "_load_private_inputs", side_effect=prep.PreparationHold("synthetic", "invented_hold")):
            self.assert_hold(prep.run_authorized, root)
        self.assertEqual(opened, [("PREPARATION_ATTEMPT_v2.json", "xb"), ("PREPARATION_HOLD_v2.json", "xb")])


if __name__ == "__main__":
    unittest.main()

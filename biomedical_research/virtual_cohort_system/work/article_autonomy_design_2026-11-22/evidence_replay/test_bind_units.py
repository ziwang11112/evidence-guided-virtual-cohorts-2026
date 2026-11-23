import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence_replay.bind_units import bind_design


def design(op, cols=None):
    return {"columns": cols if cols is not None else [
        {"name":"a","unit":"g"}, {"name":"b","unit":"L"}, {"name":"g","unit":"1"}],
        "evidence":{"evidence_checks":[{"id":"first", "source":"Table 1", "operator":op}]}}


def gate(col):
    return {"column":col, "cmp":"gt", "value":0}


class TestDesignUnitBinding(unittest.TestCase):
    def test_missing_units_bound_without_rows_or_mutation(self):
        original = design({"kind":"ols_intercept", "x":"a", "y":"b", "where":[gate("g")]})
        saved = copy.deepcopy(original)
        work, log = bind_design(original)
        item = work["evidence"]["evidence_checks"][0]
        self.assertEqual(item["operator"]["units"], {"a":"g", "b":"L", "g":"1"})
        self.assertEqual(log[0]["status"], "bound_from_design")
        self.assertEqual(log[0]["unit_sources"]["b"], "columns[1].unit")
        self.assertEqual(original, saved)
        self.assertEqual(log[0]["submitted_operator"], saved["evidence"]["evidence_checks"][0]["operator"])

    def test_event_contingency_and_unfiltered_count(self):
        for op, wanted in [
                ({"kind":"percentage", "event":gate("a"), "where":[gate("g")]}, {"a":"g", "g":"1"}),
                ({"kind":"odds_ratio", "exposure":gate("b"), "outcome":gate("a"), "where":[gate("g")]},
                 {"b":"L", "a":"g", "g":"1"}),
                ({"kind":"count"}, {})]:
            normalized, logs = bind_design(design(op))
            self.assertEqual(normalized["evidence"]["evidence_checks"][0]["operator"]["units"], wanted)
            self.assertEqual(logs[0]["units"], wanted)

    def test_supplied_maps_are_validated_and_never_repaired(self):
        base = {"kind":"mean", "y":"a", "where":[gate("g")]}
        for units in [None, {}, {"a":"g"}, {"a":"g","g":"code"},
                      {"a":"g", "g":"1", "alias":"g"}]:
            op = dict(base, units=units)
            src = design(op)
            work, log = bind_design(src)
            item = work["evidence"]["evidence_checks"][0]
            self.assertEqual(log[0]["status"], "unresolved")
            self.assertIn("unresolved", item)
            self.assertNotIn("operator", item)
            self.assertEqual(log[0]["submitted_operator"], op)
            self.assertEqual(src["evidence"]["evidence_checks"][0]["operator"], op)
        src = design(dict(base, units={"a":"g", "g":"1"}))
        work, log = bind_design(src)
        self.assertEqual(src, work)
        self.assertEqual(log[0]["status"], "explicit_verified")

    def test_no_guess_from_alias_duplicate_missing_unit_or_identifier(self):
        for name, cols in [("A",[{"name":"a", "unit":"g"}]),
                           ("a",[{"name":"a", "unit":"g"}]*2),
                           ("a",[{"name":"a"}]), ("id",[{"name":"id","unit":"1"}]),
                           ("row_id",[{"name":"row_id", "unit":"1"}]),
                           ("diagnostic_mean",[{"name":"diagnostic_mean", "unit":"1"}]),
                           ("patient",[{"name":"patient", "role":"identifier", "unit":"1"}])]:
            src = design({"kind":"mean", "y":name}, cols)
            _, log = bind_design(src)
            self.assertEqual(log[0]["status"], "unresolved")

    def test_existing_unresolved_item_kept(self):
        src = design({"kind":"mean","y":"b"})
        item = src["evidence"]["evidence_checks"][0]
        del item["operator"]
        item["unresolved"] = "Different population"
        normalized, log = bind_design(src)
        self.assertEqual(normalized, src)
        self.assertEqual(log[0], {"id":"first", "status":"no_operator"})

    def test_conflicting_input_dispositions_are_rejected(self):
        src = design({"kind":"mean","y":"missing"})
        src["evidence"]["evidence_checks"][0]["unresolved"] = "Unobserved"
        with self.assertRaises(ValueError):
            bind_design(src)


if __name__ == "__main__":
    unittest.main()

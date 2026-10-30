"""Invented export plans only; never open scientific source/result files."""
import copy
import unittest

from audit_m3_export import PREFIX, digest
from audit_m10_export import CURATED, M8_COMMIT, validate_plan
from finalize_m10_export import inspect_bytes


def invented_plan():
    paths = [PREFIX + "README.md", PREFIX + "MILESTONE_10_RESULTS.md", CURATED + "file_manifest.json"]
    return {"schema_version": 1, "milestone": "M10", "base_commit": M8_COMMIT,
            "content_review_complete": True, "participant_or_generated_output_rows_exported": False,
            "experiments_or_tests_rerun": False, "curated_roots": [CURATED],
            "project_documents": paths[:2],
            "files": [{"source": p, "destination": p, "transform": "none",
                       "classification": "reviewed_document", "reviewed_sha256": "a" * 64} for p in paths]}


class PlanBoundaryTests(unittest.TestCase):
    def test_exact_additions_and_readme_successor(self):
        plan = invented_plan()
        self.assertEqual(len(validate_plan(plan, {PREFIX + "README.md": {}})), 3)

    def test_no_unreviewed_plan_or_transform(self):
        for key, value in [("content_review_complete", False),
                           ("participant_or_generated_output_rows_exported", True),
                           ("experiments_or_tests_rerun", True), ("base_commit", "b" * 40)]:
            plan = invented_plan()
            plan[key] = value
            with self.assertRaises(ValueError):
                validate_plan(plan, {})
        plan = invented_plan()
        plan["files"][0]["transform"] = "normalize_anything"
        with self.assertRaises(ValueError):
            validate_plan(plan, {})

    def test_traversal_raw_rows_wildcards_and_historical_rewrite(self):
        for name in ["../outside.md", "raw/file.json", "generated.csv", "observed.csv", "*.md"]:
            plan = invented_plan()
            path = CURATED + name
            plan["files"].append({**plan["files"][0], "source": path, "destination": path})
            with self.assertRaises(ValueError):
                validate_plan(plan, {})
        plan = invented_plan()
        with self.assertRaisesRegex(ValueError, "Only the historical"):
            validate_plan(plan, {CURATED + "file_manifest.json": {}})

    def test_duplicate_and_unreviewed_table(self):
        plan = invented_plan()
        plan["files"].append(copy.deepcopy(plan["files"][0]))
        with self.assertRaises(ValueError):
            validate_plan(plan, {})
        plan = invented_plan()
        path = CURATED + "summary.csv"
        plan["files"].append({**plan["files"][0], "source": path, "destination": path})
        with self.assertRaisesRegex(ValueError, "schema"):
            validate_plan(plan, {})


class ContentBoundaryTests(unittest.TestCase):
    def item(self, raw, name="summary.csv"):
        return {"destination": CURATED + name, "classification": "aggregate_analysis",
                "reviewed_sha256": digest(raw), "aggregate_table": {"rows": 1, "required_keys": ["endpoint", "estimate"]}}

    def test_aggregate_and_participant_schema(self):
        raw = b"endpoint,estimate\ninvented,1\n"
        inspect_bytes(self.item(raw), raw)
        raw = b"endpoint,estimate,row_id\ninvented,1,person1\n"
        with self.assertRaisesRegex(ValueError, "participant"):
            inspect_bytes(self.item(raw), raw)
        raw = b"endpoint,estimate\ninvented,1,unexpected\n"
        with self.assertRaisesRegex(ValueError, "Malformed"):
            inspect_bytes(self.item(raw), raw)

    def test_raw_binary_is_not_approved_plot(self):
        raw = b"not an image"
        with self.assertRaisesRegex(ValueError, "binary"):
            inspect_bytes(self.item(raw, "figure.png"), raw)


if __name__ == "__main__":
    unittest.main()

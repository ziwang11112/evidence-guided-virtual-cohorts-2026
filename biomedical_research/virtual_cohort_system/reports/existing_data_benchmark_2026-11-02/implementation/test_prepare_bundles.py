"""Metadata-only scientific representation and admission-boundary checks."""
import json
from pathlib import Path
import tempfile
import unittest
import sys

import prepare_bundles as compiler

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path.insert(0, str(PROJECT))
from cohort_harness.contracts import validate_evidence, validate_task


class CompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence_dir = HERE.parent / "evidence"
        cls.packets, _ = compiler.verify_approved_packets(cls.evidence_dir)
        cls.original_task = compiler.read(PROJECT / "work/chns_admission_2026-11-01/f2/task.json")
        cls.task = compiler.common_task(cls.original_task)
        cls.ngsp = (PROJECT / "work/chns_admission_2026-11-01/f2/evidence/sources/NGSP_UNITS.md").read_bytes()
        cls.compiled = {arm: compiler.compile_evidence(p, b, cls.ngsp)[0]
                        for arm, (p, b) in cls.packets.items()}

    def test_task_schema_population_unchanged_without_old_revision_budget(self):
        validate_task(self.task)
        self.assertEqual(self.task["columns"], self.original_task["columns"])
        self.assertEqual(self.task["population"], self.original_task["population"])
        self.assertEqual(self.task["budget"], {"source_queries": 0, "source_downloads": 0, "revisions": 0})
        self.assertEqual(self.task["n_rows"], 3000)

    def test_contract_and_exact_common_information_partition(self):
        ids = {arm: validate_evidence(value, self.task) for arm, value in self.compiled.items()}
        self.assertEqual(len(ids["E0"]), 32)
        self.assertEqual(len(ids["E1"]), 36)
        self.assertEqual(ids["E1"] - ids["E0"], {"R_JANSEN_BMI", "R_JANSEN_FPG", "R_BAO_PEARSON", "R_MIND_SPEARMAN"})
        self.assertEqual(self.compiled["E0"]["items"], [x for x in self.compiled["E1"]["items"] if not x["id"].startswith("R_")])

    def test_individual_dispersion_and_quartiles_not_estimator_precision(self):
        items = {x["id"]: x for x in self.compiled["E0"]["items"]}
        sd = items["M_J_HBA1C_IFCC_SD"]
        self.assertEqual((sd["kind"], sd["estimate"], sd["unit"]), ("sd", 3, "mmol/mol"))
        self.assertEqual(sd["uncertainty"], {"kind": "not_reported"})
        q1 = items["M_B_AGE_Q1"]
        self.assertEqual((q1["kind"], q1["estimate"], q1["q"], q1["method"]), ("quantile", 37.9, .25, "not_reported"))

    def test_native_jansen_units_unknown_ci_level_separate_adjustment(self):
        items = {x["id"]: x for x in self.compiled["E1"]["items"]}
        for identifier, predictor, estimate, unit in [
            ("R_JANSEN_BMI", "BMI", .13, "mmol/mol/(kg/m^2)"),
            ("R_JANSEN_FPG", "FPG", 2.29, "mmol/mol/(mmol/L)")]:
            item = items[identifier]
            self.assertEqual(item["variables"], ["HbA1c_IFCC", predictor])
            self.assertEqual(item["adjustment"], ["age", "gender_binary"])
            self.assertEqual((item["estimate"], item["unit"]), (estimate, unit))
            self.assertEqual(item["uncertainty"], {"kind": "not_reported"})
            self.assertIn('"confidence_level": null', item["applicability"])
            self.assertIn('"intercept": true', item["applicability"])
            self.assertIn('"status": "not_computable"', item["applicability"])

    def test_ngsp_is_common_context_not_converted_empirical_relationship(self):
        unit = next(x for x in self.compiled["E0"]["items"] if x["id"] == "U_NGSP_SCALE")
        self.assertEqual(unit["kind"], "contextual")
        self.assertIsNone(unit["estimate"])
        self.assertIn("0.09148", unit["applicability"])
        self.assertEqual(unit, next(x for x in self.compiled["E1"]["items"] if x["id"] == unit["id"]))

    def test_valid_json_with_changed_packet_bytes_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="evcb_metadata_") as directory:
            path = Path(directory)
            for name in ["PACKET_REVIEW.json", "E0.json", "E1.json"]:
                (path / name).write_bytes((self.evidence_dir / name).read_bytes())
            with (path / "E0.json").open("ab") as stream:
                stream.write(b"\n")
            with self.assertRaisesRegex(ValueError, "packet bytes changed"):
                compiler.verify_approved_packets(path)


if __name__ == "__main__":
    unittest.main()

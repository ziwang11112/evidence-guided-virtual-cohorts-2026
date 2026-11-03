"""No clinical inputs and no row generation: audit new orchestration guards."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import main_session_v1 as m


class MainSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="evc_main_unit_")
        self.root = Path(self.temp.name)
        (self.root / "session/events").mkdir(parents=True)
        self.contract = {"kind": "main_session_v1", "root": str(self.root.resolve()),
                         "author_id": "test_author", "case_id": "CHNS2009", "information_condition": "E1",
                         "constructor_kind": "agent", "budget": m.BUDGET, "bindings": []}
        m.WRITE(self.root / "session/contract.json", self.contract)
        self.s = m.Session(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def active(self):
        # Unit fixtures bypass only release activation. Real release gate tested separately.
        self.s.add("activation", unit_fixture=True)
        self.s.add("dispatch", external_id="test_author")

    def test_dispatch_requires_actual_release(self):
        with self.assertRaisesRegex(ValueError, "release required"):
            self.s.dispatch("test_author")
        self.assertEqual(self.s.events(), [])

    def test_disabled_release_rejected(self):
        with self.assertRaisesRegex(ValueError, "not released"):
            m.validate_release({"execution_enabled": False})

    def test_failure_debits_and_cannot_retry_or_renew(self):
        self.active()
        with patch.object(self.s, "_frozen", return_value="candidates/a"), \
             patch.object(m.execution, "run_candidate", side_effect=RuntimeError("isolated backend fails")) as run:
            with self.assertRaisesRegex(RuntimeError, "backend"):
                self.s._run("a", "trial", 5201)
            with self.assertRaisesRegex(ValueError, "Slot consumed"):
                self.s._run("a", "trial", 5201)
            with self.assertRaises(RuntimeError):
                self.s._run("b", "trial", 5202)
            with self.assertRaisesRegex(ValueError, "Two total"):
                self.s._run("c", "trial", 5202)
            self.assertEqual(run.call_count, 2)
        self.assertEqual(len(self.s.selected("attempt")), 2)
        self.assertTrue(all(e["status"] == "adapter_error" for e in self.s.selected("result")))

    def test_final_requires_selection_and_uses_only_selected(self):
        self.active()
        with patch.object(self.s, "_frozen", return_value="candidates/a"):
            with self.assertRaisesRegex(ValueError, "not selected"):
                self.s._run("a", "final", 5101)
            self.s.add("science_closed", candidate="candidates/b")
            with self.assertRaisesRegex(ValueError, "not selected"):
                self.s._run("a", "final", 5101)

    def test_no_trial_after_scientific_closure(self):
        self.active()
        self.s.add("science_closed", candidate="candidates/a")
        with patch.object(self.s, "_frozen", return_value="candidates/a"):
            with self.assertRaisesRegex(ValueError, "Trials end"):
                self.s._run("a", "trial", 5201)

    def test_incomplete_final_resumes_without_replacement(self):
        self.active()
        self.s.add("science_closed", candidate="candidates/a")
        self.s.add("attempt", candidate="candidates/a", purpose="final", seed=5101, run_id="interrupted_slot")
        with patch.object(self.s, "verify", return_value=True), \
             patch.object(self.s, "_frozen", return_value="candidates/a"), \
             patch.object(m.execution, "run_candidate", side_effect=RuntimeError("test fail")) as run:
            self.s.deliver()
            self.assertEqual(run.call_count, 2)
            with self.assertRaisesRegex(ValueError, "unavailable"):
                self.s.deliver()
        self.assertEqual([e["seed"] for e in self.s.selected("attempt")], [5101, 5102, 5103])

    def test_ledger_changes_detected(self):
        self.s.add("note", value="original")
        self.s.add("note", value="second")
        path = self.root / "session/events/0001.json"
        path.write_text(json.dumps({**m.READ(path), "value": "changed"}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "damaged"):
            self.s.events()

    def test_final_feedback_cannot_be_requested(self):
        self.s.add("attempt", purpose="final", seed=5101, run_id="f1")
        with self.assertRaisesRegex(ValueError, "only from exploratory"):
            self.s.trial_feedback("f1")

    def test_paths_reject_escape(self):
        with self.assertRaisesRegex(ValueError, "Traversal"):
            m.inside(self.root, "../other")
        with self.assertRaisesRegex(ValueError, "outside"):
            m.inside(self.root, self.root.parent / "other")

    def release_fixture(self):
        slots = []
        for case in ("CHNS2009", "ENSANUT2018"):
            for condition in ("E0", "E1"):
                for i in range(6):
                    ident = f"{case}_{condition}_{i}"
                    folder = self.root / ident
                    (folder / "session/events").mkdir(parents=True)
                    data = {**self.contract, "root": str(folder.resolve()), "author_id": ident, "case_id": case,
                            "information_condition": condition, "constructor_kind": "statistical" if i == 5 else "agent"}
                    m.WRITE(folder / "session/contract.json", data)
                    slots.append({"id": ident, "session_root": str(folder), "contract_sha256": m.SHA(folder / "session/contract.json")})
        release = {"kind": "main_study_release_v1", "execution_enabled": True, "budget": m.BUDGET,
                   "maximum_total_attempts": 120, "constructions": slots, "artifacts": []}
        payload = {k: v for k, v in release.items() if k != "execution_enabled"}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        review = self.root / "review.json"
        m.WRITE(review, {"status": "ready", "target_results_used_for_binding": False, "release_payload_sha256": digest})
        release["independent_review"] = m.bound(review)
        return release

    def test_campaign_closure_requires_all_cases_arms_and_failures(self):
        release = self.release_fixture()
        self.assertTrue(m.validate_release(release))
        for slot in release["constructions"][:-1]:
            m.Session(slot["session_root"]).abandon("unit fixture: no scientific generation")
        with self.assertRaisesRegex(ValueError, "All cases"):
            m.require_campaign_closed(release)
        m.Session(release["constructions"][-1]["session_root"]).abandon("unit fixture")
        self.assertEqual(len(m.require_campaign_closed(release)), 24)

    def test_review_is_bound_to_exact_release(self):
        release = self.release_fixture()
        release["maximum_total_attempts"] = 121
        with self.assertRaisesRegex(ValueError, "budget changed"):
            m.validate_release(release)
        release["maximum_total_attempts"] = 120
        release["new_unreviewed_field"] = "altered"
        with self.assertRaisesRegex(ValueError, "not bound"):
            m.validate_release(release)

    def test_constructor_id_distinct_from_actual_agent_task(self):
        release = self.release_fixture()
        release_path = self.root / "release.json"
        m.WRITE(release_path, release)
        task = m.Session(release["constructions"][0]["session_root"])
        task.activate(release_path)
        event = task.dispatch("/root/scientific_author_01")
        self.assertNotEqual(event["external_id"], event["constructor_id"])
        with self.assertRaisesRegex(ValueError, "One actual"):
            task.dispatch("/root/replacement")

    def test_freeze_requires_actual_uptake_and_moment_record(self):
        self.s.add("dispatch", external_id="/root/author")
        directory = self.root / "bundle/candidates/new"
        directory.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "numerical_uptake"):
            self.s.freeze("candidates/new")
        m.WRITE(directory / "numerical_uptake.json", {"records": []})
        with self.assertRaises(FileNotFoundError):
            self.s.freeze("candidates/new")
        self.assertFalse((directory / "freeze.json").exists())

    def test_missing_slot_does_not_allow_early_evaluation(self):
        release = self.release_fixture()
        release["constructions"].pop()
        with self.assertRaises(ValueError):
            m.require_campaign_closed(release)


if __name__ == "__main__":
    unittest.main(verbosity=2)

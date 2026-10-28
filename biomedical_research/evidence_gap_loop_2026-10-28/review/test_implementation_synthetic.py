"""Independent implementation regressions using fabricated data only.

Run this file directly. It never opens pilot observed/reference/participant CSVs,
raw source data, builder directories or biological results. All temporary files
are created under this review directory and removed by TemporaryDirectory.
"""
from __future__ import annotations

import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

REVIEW = Path(__file__).resolve().parent
PILOT = REVIEW.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ctl = load("audited_controller", PILOT / "loop_control.py")
ev = load("audited_evaluator", PILOT / "custodian/evaluate.py")
gw = load("audited_gateway", PILOT / "tools/literature_gateway.py")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


class SyntheticChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic_", dir=REVIEW)
        self.root = Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(REVIEW.resolve()))

    def tearDown(self):
        self.temporary.cleanup()

    def observed(self):
        return pd.DataFrame({
            "row_id": ["0001", "0002", "0003", "0004"],
            "bmi": [23.000000000000004, 24.123456789012344, 25.999999999999996, 31.000000000000007],
            "age": [22, 35, 58, 79], "sex": [1, 2, 1, 2],
        })

    def contract(self):
        return {"observed_columns": ["row_id", "bmi", "age", "sex"],
                "generated_columns": [{"name": "hdl", "min_exclusive": 0}]}

    def fixture(self, policy="ordinary", construction=None, release_layout=False):
        run = self.root / "runs" / construction if release_layout else self.root / policy
        run.mkdir(parents=True, exist_ok=True)
        (run / "REQUEST.md").write_text("Synthetic-only software validation request.\n", encoding="utf-8")
        observed_path = self.root / "shared/observed.csv" if release_layout else self.root / "synthetic_observed.csv"
        observed_path.parent.mkdir(parents=True, exist_ok=True)
        self.observed().to_csv(observed_path, index=False, float_format="%.17g")
        contract_path = self.root / "shared/runner_contract.json" if release_layout else self.root / "contract.json"
        protocol_path = self.root / "protocol.json"
        write(contract_path, self.contract())
        protocol = json.loads((PILOT / "protocol.json").read_text())
        write(protocol_path, protocol)
        ctl.init(run, policy, observed_path, contract_path, protocol_path)
        config_path = self.root / "gateway_config.json"
        config_path.write_bytes((PILOT / "tools/gateway_config.json").read_bytes())
        # Search response bytes are wholly fabricated; there is no network call.
        record = {"title": "Fabricated methods fixture", "abstractText": "Synthetic group and marginal records for software validation.", "pmcid": "PMC123"}
        payload = {"hitCount": 1, "resultList": {"result": [record]}}
        with patch.object(gw, "http_get", return_value=gw.encoded(payload)):
            session = gw.Session(run / "literature", config_path)
            try:
                artifact = session.search("synthetic fixture", 1)["approved_artifact"]
            finally:
                session.close()
        evidence = {"sources": [{"id": "toy_source", "identifier": "SYNTHETIC-ONLY", "population": "Fabricated rows", "measurement": "Arbitrary units", "cohort_overlap": "Not applicable: synthetic",
                    "approved_artifacts": [{"path": "literature/" + artifact["session_relative_path"], "sha256": artifact["sha256"]}]}],
                    "evidence": [
                        {"id": "toy_group_mean", "source_id": "toy_source", "locator": "Synthetic table 1", "estimand": "group mean", "variables": ["hdl"], "adjustment": "none", "reported": {"group": "A", "mean": 7.25}, "uncertainty": {"standard_error": 0.5}, "applicability": "Synthetic test only", "model_use": "Declared level anchor", "bridge_assumptions": ["toy_bridge"]},
                        {"id": "toy_marginal", "source_id": "toy_source", "locator": "Synthetic table 2", "estimand": "marginal standard deviation", "variables": ["hdl"], "adjustment": "none", "reported": {"standard_deviation": 1.25}, "uncertainty": "Not supplied", "applicability": "Synthetic test only", "model_use": "Unused descriptive evidence", "bridge_assumptions": []},
                    ]}
        spec = {"parameters": {"level": 7.25}, "assumptions": [{"id": "toy_bridge", "description": "Synthetic-only bridge; not biological evidence"}],
                "parameter_provenance": {"level": {"evidence_ids": ["toy_group_mean"], "assumption_ids": ["toy_bridge"], "derivation": "Synthetic fixture group mean"}}}
        candidate = run / "initial"
        candidate.mkdir()
        (candidate / "generator.py").write_text("import numpy as np\n\ndef generate(observed, spec, seed):\n    result = observed.copy(deep=True)\n    result['hdl'] = spec['parameters']['level'] + np.random.default_rng(seed).uniform(0, 1, len(observed))\n    return result\n", encoding="utf-8")
        write(candidate / "model_spec.json", spec)
        write(candidate / "evidence.json", evidence)
        (candidate / "decision.md").write_text("Synthetic-only constant conditional model for control validation.\n", encoding="utf-8")
        if policy == "gap_policy":
            write(candidate / "gaps.json", [{"id": "toy_gap", "component": "group to individual bridge", "affected_analysis": "Synthetic fixture", "evidence_status": "Aggregate-only", "consequence": "Relationship remains unidentified", "next_action": "retain", "status": "unresolved", "resolution": "Retain explicit assumption for test"}])
            write(candidate / "actions.json", [{"gap_id": "toy_gap", "action": "retain", "evidence_artifacts": [], "model_change": "none", "reason": "Synthetic fixture tests a documented no-op"}])
        return run

    def review(self, run):
        candidate = run / "initial"
        review = {"summary": "Synthetic code and provenance review", "findings": [], "execution_allowed": True,
                  "generator_sha256": ctl.sha(candidate / "generator.py"), "model_spec_sha256": ctl.sha(candidate / "model_spec.json"),
                  "evidence_sha256": ctl.sha(candidate / "evidence.json"), "initial_freeze_sha256": ctl.sha(candidate / "freeze.json"),
                  "candidate_freeze_sha256": ctl.sha(candidate / "freeze.json")}
        path = run / "review.json"
        write(path, review)
        return path

    def test_output_preserves_observed_values_and_rejects_mutations(self):
        observed = self.observed()
        enriched = observed.assign(hdl=[7.0, 8.0, 9.0, 10.0])
        ctl.output_check(observed, enriched, self.contract())
        changed = enriched.copy()
        changed.loc[0, "bmi"] = np.nextafter(changed.loc[0, "bmi"], np.inf)
        with self.assertRaises((ValueError, AssertionError)):
            ctl.output_check(observed, changed, self.contract())
        with self.assertRaises(ValueError):
            ctl.output_check(observed, enriched.assign(extra=1), self.contract())
        with self.assertRaises(ValueError):
            ctl.output_check(observed, enriched.assign(hdl=np.inf), self.contract())
        with self.assertRaises(ValueError):
            ctl.output_check(observed, enriched.assign(hdl=0), self.contract())

    def test_full_initial_execution_preserves_roundtrip_and_evidence(self):
        comparable_outputs = {}
        for policy in ["ordinary", "gap_policy"]:
            run = self.fixture(policy)
            evidence_before = (run / "initial/evidence.json").read_bytes()
            ctl.freeze_candidate(run, "initial")
            ctl.record_review(run, self.review(run))
            receipt = ctl.execute(run, "initial")
            self.assertEqual(evidence_before, (run / "initial/evidence.json").read_bytes())
            self.assertEqual(len(receipt["draws"]), 5)
            observed = ctl.frame(self.root / "synthetic_observed.csv")
            for draw in receipt["draws"]:
                generated = ctl.frame(draw["path"])
                pd.testing.assert_frame_equal(observed, generated[observed.columns], check_exact=True)
            comparable_outputs[policy] = [Path(draw["path"]).read_bytes() for draw in receipt["draws"]]
            with self.assertRaises(ValueError):
                ctl.execute(run, "initial")
        self.assertEqual(comparable_outputs["ordinary"], comparable_outputs["gap_policy"])

    def test_final_noop_retains_same_seeds_and_requires_bound_review(self):
        run = self.fixture("gap_policy")
        ctl.freeze_candidate(run, "initial")
        ctl.record_review(run, self.review(run))
        first = ctl.execute(run, "initial")
        final = run / "final"
        final.mkdir()
        for name in ["generator.py", "model_spec.json", "evidence.json", "decision.md", "gaps.json", "actions.json"]:
            (final / name).write_bytes((run / "initial" / name).read_bytes())
        write(final / "revision.json", {"reason": "Synthetic no-op preserves unchanged specification", "generator_or_spec_changed": False})
        ctl.freeze_candidate(run, "final")
        with self.assertRaises(ValueError):
            ctl.execute(run, "final")
        review = {"summary": "Synthetic final code review", "findings": [], "execution_allowed": True,
                  "generator_sha256": ctl.sha(final / "generator.py"), "model_spec_sha256": ctl.sha(final / "model_spec.json"),
                  "evidence_sha256": ctl.sha(final / "evidence.json"), "candidate_freeze_sha256": ctl.sha(final / "freeze.json")}
        wrong = copy.deepcopy(review)
        wrong["candidate_freeze_sha256"] = "0" * 64
        write(run / "final_code_review.json", wrong)
        with self.assertRaises(ValueError):
            ctl.execute(run, "final")
        write(run / "final_code_review.json", review)
        last = ctl.execute(run, "final")
        self.assertEqual([x["seed"] for x in first["draws"]], [x["seed"] for x in last["draws"]])
        self.assertEqual([x["sha256"] for x in first["draws"]], [x["sha256"] for x in last["draws"]])

    def test_gateway_audit_append_allowed_but_frozen_prefix_edit_rejected(self):
        run = self.fixture()
        ctl.freeze_candidate(run, "initial")
        audit = run / "literature/audit.jsonl"
        original = audit.read_bytes()
        with audit.open("ab") as handle:
            handle.write(b'{"type":"synthetic_additional_event"}\n')
        ctl.verify_gateway_snapshot(run / "initial/gateway_snapshot.json")
        audit.write_bytes(b" " + original)
        with self.assertRaises(ValueError):
            ctl.verify_gateway_snapshot(run / "initial/gateway_snapshot.json")

    def test_generator_global_rng_mutation_is_rejected_and_restored(self):
        run = self.fixture()
        path = run / "initial/generator.py"
        path.write_text("import numpy as np\n\ndef generate(observed, spec, seed):\n    np.random.seed(seed)\n    return observed.assign(hdl=np.random.uniform(1, 2, len(observed)))\n", encoding="utf-8")
        ctl.freeze_candidate(run, "initial")
        ctl.record_review(run, self.review(run))
        before = np.random.get_state()
        with self.assertRaises(ValueError):
            ctl.execute(run, "initial")
        self.assertTrue(ctl.rng_equal(before, np.random.get_state()))
        self.assertTrue((run / "initial/outputs/failure.json").exists())
        self.assertFalse((run / "initial/outputs/execution.json").exists())

    def test_final_and_execution_are_blocked_before_review(self):
        run = self.fixture()
        ctl.freeze_candidate(run, "initial")
        with self.assertRaises(ValueError):
            ctl.execute(run, "initial")
        with self.assertRaises(ValueError):
            ctl.freeze_candidate(run, "final")

    def test_code_change_after_freeze_is_rejected(self):
        run = self.fixture()
        ctl.freeze_candidate(run, "initial")
        review = self.review(run)
        with (run / "initial/generator.py").open("a") as handle:
            handle.write("\n# Post-freeze modification\n")
        with self.assertRaises(ValueError):
            ctl.record_review(run, review)

    def test_wrong_review_binding_is_rejected(self):
        run = self.fixture()
        ctl.freeze_candidate(run, "initial")
        path = self.review(run)
        review = json.loads(path.read_text())
        review["generator_sha256"] = "0" * 64
        write(path, review)
        with self.assertRaises(ValueError):
            ctl.record_review(run, path)

    def test_unbound_parameter_provenance_is_rejected(self):
        bad = [
            {"level": {"evidence_ids": ["missing"], "assumption_ids": [], "derivation": "Unbound reference"}},
            {"level": {"evidence_ids": [], "assumption_ids": ["missing"], "derivation": "Unbound assumption"}},
            {"other_parameter": {"evidence_ids": ["toy_group_mean"], "assumption_ids": [], "derivation": "Wrong parameter"}},
            {"level": {"evidence_ids": [], "assumption_ids": [], "derivation": "No supporting link"}},
        ]
        for index, provenance in enumerate(bad):
            with self.subTest(index=index):
                run = self.fixture("ordinary")
                spec_path = run / "initial/model_spec.json"
                spec = json.loads(spec_path.read_text())
                spec["parameter_provenance"] = provenance
                write(spec_path, spec)
                with self.assertRaises(ValueError):
                    ctl.freeze_candidate(run, "initial")
                # Each subtest receives a clean independent temporary fixture.
                self.temporary.cleanup()
                self.setUp()

    def test_fabricated_approved_file_is_not_gateway_provenance(self):
        run = self.fixture()
        fabricated = run / "literature/approved/fabricated.txt"
        fabricated.write_text("Synthetic unapproved file", encoding="utf-8")
        ledger_path = run / "initial/evidence.json"
        ledger = json.loads(ledger_path.read_text())
        ledger["sources"][0]["approved_artifacts"] = [{"path": "literature/approved/fabricated.txt", "sha256": ctl.sha(fabricated)}]
        write(ledger_path, ledger)
        with self.assertRaises(ValueError):
            ctl.freeze_candidate(run, "initial")

    def test_gap_contract_rejects_unsupported_claims(self):
        with self.assertRaises(ValueError):
            ctl.validate_gaps([])
        gap = {"id": "g", "component": "x", "affected_analysis": "x", "evidence_status": "missing", "consequence": "unknown", "next_action": "retrieve", "status": "open", "resolution": ""}
        with self.assertRaises(ValueError):
            ctl.validate_gaps([gap], final=True)
        with self.assertRaises(ValueError):
            ctl.validate_actions([{"gap_id": "g", "action": "retrieve", "evidence_artifacts": [], "model_change": "none", "reason": "Claim without evidence"}], [gap])
        with self.assertRaises(ValueError):
            ctl.validate_actions([{"gap_id": "missing", "action": "retain", "evidence_artifacts": [], "model_change": "none", "reason": "Unknown gap"}], [gap])
        additional = {**gap, "id": "unaddressed", "status": "unresolved", "resolution": "Acknowledged but no linked action"}
        with self.assertRaises(ValueError):
            ctl.validate_actions([{"gap_id": "g", "action": "retain", "evidence_artifacts": [], "model_change": "none", "reason": "Documented no-op"}], [gap, additional], final=True)

    def test_premature_evaluation_never_reads_data(self):
        path = self.root / "premature_release.json"
        write(path, {})
        with patch.object(ev, "read_csv", side_effect=AssertionError("Premature data access")) as reader:
            with self.assertRaises(ValueError):
                ev.run(path)
            reader.assert_not_called()

    def test_labeled_outputs_without_freezes_do_not_unlock(self):
        local_custodian = self.root / "custodian"
        local_custodian.mkdir()
        (local_custodian / "analysis_spec.json").write_bytes((PILOT / "custodian/analysis_spec.json").read_bytes())
        outputs = []
        for build in range(4):
            for stage in ["initial", "final"]:
                for draw in range(1, 6):
                    path = self.root / f"fake_{build}_{stage}_{draw}.csv"
                    self.observed().assign(hdl=7.0).to_csv(path, index=False)
                    outputs.append({"construction": f"construction_{build}", "arm": "ordinary" if build < 2 else "gap_policy", "stage": stage, "draw": draw, "file": path.name, "sha256": ev.sha(path)})
        release = {"all_four_constructions_frozen": True, "root_authorized_evaluation": True, "no_builder_access_to_target": True,
                   "analysis_spec_sha256": ev.sha(local_custodian / "analysis_spec.json"), "evaluator_sha256": ev.sha(ev.__file__), "outputs": outputs}
        with patch.object(ev, "PILOT", self.root), patch.object(ev, "BASE", local_custodian):
            with self.assertRaises(ValueError):
                ev.validate_release(release)

    def test_valid_full_release_and_tampered_provenance(self):
        for relative in ["loop_control.py", "tools/literature_gateway.py", "tools/gateway_config.json"]:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((PILOT / relative).read_bytes())
        for relative in ["BUILDER_GUIDE.md", "policies/ordinary.md", "policies/gap_policy.md", "shared/target_description.md"]:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text("Synthetic-only fixture instructions.\n", encoding="utf-8")
        write(self.root / "shared/schema.json", {"row_count": 4})
        outputs = []
        with patch.object(ctl, "__file__", str(self.root / "loop_control.py")):
            for construction, policy in [("ordinary_1", "ordinary"), ("ordinary_2", "ordinary"), ("gap_1", "gap_policy"), ("gap_2", "gap_policy")]:
                run = self.fixture(policy, construction, release_layout=True)
                ctl.freeze_candidate(run, "initial")
                ctl.record_review(run, self.review(run))
                initial = ctl.execute(run, "initial")
                final = run / "final"
                final.mkdir()
                names = ["generator.py", "model_spec.json", "evidence.json", "decision.md"]
                if policy == "gap_policy":
                    names += ["gaps.json", "actions.json"]
                for name in names:
                    (final / name).write_bytes((run / "initial" / name).read_bytes())
                write(final / "revision.json", {"reason": "Synthetic no-op", "generator_or_spec_changed": False})
                ctl.freeze_candidate(run, "final")
                write(run / "final_code_review.json", {"execution_allowed": True, "findings": [], "summary": "Synthetic review",
                    "generator_sha256": ctl.sha(final / "generator.py"), "model_spec_sha256": ctl.sha(final / "model_spec.json"),
                    "evidence_sha256": ctl.sha(final / "evidence.json"), "candidate_freeze_sha256": ctl.sha(final / "freeze.json")})
                final_execution = ctl.execute(run, "final")
                for stage, execution in [("initial", initial), ("final", final_execution)]:
                    for number, draw in enumerate(execution["draws"], 1):
                        outputs.append({"construction": construction, "arm": policy, "stage": stage, "draw": number, "seed": draw["seed"],
                                        "file": str(Path(draw["path"]).relative_to(self.root)), "sha256": draw["sha256"]})
        artifacts = {str(p.relative_to(self.root)): ctl.sha(p) for p in self.root.rglob("*") if p.is_file()}
        release = {"all_four_constructions_frozen": True, "root_authorized_evaluation": True, "no_builder_access_to_target": True,
                   "analysis_spec_sha256": ev.sha(PILOT / "custodian/analysis_spec.json"), "evaluator_sha256": ev.sha(ev.__file__),
                   "outputs": outputs, "artifacts": artifacts}
        with patch.object(ev, "PILOT", self.root):
            self.assertEqual(len(ev.validate_release(release)), 40)
            altered = copy.deepcopy(release)
            altered["outputs"][0]["seed"] += 1
            with self.assertRaises(ValueError):
                ev.validate_release(altered)
            altered = copy.deepcopy(release)
            altered["outputs"][1]["file"] = altered["outputs"][0]["file"]
            altered["outputs"][1]["sha256"] = altered["outputs"][0]["sha256"]
            with self.assertRaises(ValueError):
                ev.validate_release(altered)
            for relative in ["runs/ordinary_1/final_code_review.json", "runs/gap_1/final/freeze.json", "runs/ordinary_2/initial/outputs/execution.json"]:
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                with self.assertRaises(ValueError):
                    ev.validate_release(release)
                path.write_bytes(original)
            altered = copy.deepcopy(release)
            del altered["artifacts"][str(Path("runs/ordinary_1/final_code_review.json"))]
            with self.assertRaises(ValueError):
                ev.validate_release(altered)

    def test_weighted_estimator_and_full_spine_variance(self):
        rng = np.random.default_rng(108429)
        spine = pd.DataFrame([{"stratum": str(h), "psu": str(p), "weight": str(1 + (h + k) % 5)}
                              for h in range(8) for p in range(3) for k in range(4)])
        domain = spine[spine.psu != "2"].reset_index(drop=True)
        X = np.column_stack([np.ones(len(domain)), rng.normal(size=(len(domain), 3))])
        y = rng.uniform(2, 10, len(domain))
        weight = ev.number(domain, "weight")
        fitted, covariance, diagnostics = ev.taylor_fit(X, y, domain, spine)
        expected = np.linalg.lstsq(np.sqrt(weight)[:, None] * X, np.sqrt(weight) * y, rcond=None)[0]
        np.testing.assert_allclose(fitted, expected, atol=1e-11)
        scores = X * (weight * (y - X @ expected))[:, None]
        meat = np.zeros((4, 4))
        for stratum in spine.stratum.unique():
            totals = np.array([scores[((domain.stratum == stratum) & (domain.psu == psu)).to_numpy()].sum(axis=0) for psu in ["0", "1", "2"]])
            centered = totals - totals.mean(axis=0)
            meat += 1.5 * centered.T @ centered
        inverse = np.linalg.inv(X.T @ (weight[:, None] * X))
        np.testing.assert_allclose(covariance, inverse @ meat @ inverse, atol=1e-11)
        scaled = domain.copy()
        scaled["weight"] = (weight * 19).astype(str)
        beta2, cov2, _ = ev.taylor_fit(X, y, scaled, spine)
        np.testing.assert_allclose(fitted, beta2, atol=1e-11)
        np.testing.assert_allclose(covariance, cov2, atol=1e-11)
        self.assertEqual(diagnostics["design_df"], 8)
        self.assertEqual(diagnostics["residual_df"], 5)

    def test_gateway_screens_whole_metadata_and_counts_failed_requests(self):
        config_path = self.root / "config.json"
        config = json.loads((PILOT / "tools/gateway_config.json").read_text())
        config["budgets"]["queries"] = 2
        write(config_path, config)
        payload = {"hitCount": 2, "resultList": {"result": [
            {"title": "Safe synthetic record", "abstractText": "Fabricated aggregate evidence", "pmcid": "PMC123"},
            {"title": "Excluded synthetic record", "abstractText": "Neutral text", "other_metadata": "National Health and Nutrition Examination Survey", "pmcid": "PMC456"}]}}
        session = gw.Session(self.root / "gateway", config_path)
        try:
            with patch.object(gw, "http_get", return_value=gw.encoded(payload)):
                result = session.search("synthetic fixture", 2)
            self.assertEqual(result["accepted_count"], 1)
            self.assertEqual(result["rejected_count"], 1)
            self.assertNotIn("Excluded synthetic record", json.dumps(result))
            with patch.object(gw, "http_get", side_effect=gw.GatewayError("network_or_timeout_failure")):
                with self.assertRaises(gw.GatewayError):
                    session.search("synthetic fixture", 1)
            self.assertEqual(session.state["usage"]["queries"], 2)
            with patch.object(gw, "http_get") as network:
                with self.assertRaises(gw.GatewayError):
                    session.search("synthetic fixture", 1)
                network.assert_not_called()
        finally:
            session.close()

    def test_gateway_links_supplements_to_parent_manifest(self):
        config = json.loads((PILOT / "tools/gateway_config.json").read_text())
        screen = gw.Screen(config)
        xml = b'<article xmlns:xlink="http://www.w3.org/1999/xlink"><body><p>Synthetic parent article</p><supplementary-material><media xlink:href="supp.csv"/></supplementary-material></body></article>'
        root, _ = gw.parse_xml(xml, screen)
        session = object.__new__(gw.Session)
        url = gw.CLOUD + "/PMC123.1/supp.csv?md5=" + "a" * 32
        linked = session.source_links(root, "PMC123", 1, [url])
        self.assertEqual(linked[0]["status"], "available")
        self.assertEqual(linked[0]["source_url"], url)
        self.assertEqual(session.source_links(root, "PMC123", 1, [])[0]["status"], "unsupported")
        with self.assertRaises(gw.GatewayError):
            session.object_url(url, "PMC999", 1)
        with self.assertRaises(gw.GatewayError):
            gw.parse_supplement(b"group,value\nA,7\nB,NH&#65;NES", "csv", screen, 100)

    def test_search_caps_equal_protocol(self):
        protocol = json.loads((PILOT / "protocol.json").read_text())
        config = json.loads((PILOT / "tools/gateway_config.json").read_text())
        self.assertEqual(config["budgets"]["queries"], protocol["max_search_queries_per_build"])
        self.assertEqual(config["budgets"]["downloads"], protocol["max_document_downloads_per_build"])
        self.assertEqual(config["limits"]["search_page_size"], protocol["max_search_results_per_query"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SyntheticChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"passed": result.wasSuccessful(), "tests_run": result.testsRun,
              "failures": [{"test": str(test), "traceback": trace} for test, trace in result.failures],
              "errors": [{"test": str(test), "traceback": trace} for test, trace in result.errors],
              "data_scope": "Fabricated fixtures only; no real observed/reference/participant data, raw source data, builders or outcome results read",
              "implementation_sha256": {str(path.relative_to(PILOT)): ctl.sha(path) for path in [PILOT / "loop_control.py", PILOT / "tools/literature_gateway.py", PILOT / "tools/gateway_config.json", PILOT / "custodian/evaluate.py", PILOT / "custodian/analysis_spec.json"]}}
    write(REVIEW / "synthetic_test_report.json", report)
    raise SystemExit(0 if result.wasSuccessful() else 1)

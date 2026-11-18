"""Independent offline preflight. No .env reads, network, or generated-code execution.

All provider calls are replaced before invocation. Provider responses below are
handwritten fixtures. Packet checks use the original pilot anchor list directly.
"""
from pathlib import Path
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

UNIT = Path(__file__).resolve().parents[1]
PROJECT = UNIT.parents[1]
sys.path.insert(0, str(UNIT))
sys.dont_write_bytecode = True
import provider_client as pc
import run_pilot as runner

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def records(value):
    if value["format"] == "records":
        return value["records"]
    return [dict(zip(value["columns"], row)) for row in value["rows"]]

def artifact(code="def generate(observed, spec, seed):\n    return None\n"):
    return json.dumps({"model_spec": {}, "generator_py": code, "decision_record": {"structure": "offline fixture", "parameter_provenance": [], "requested_estimands": [], "limitations": [], "checks_actually_performed": []}})

class FakeResponse:
    status_code = 200
    ok = True
    headers = {"x-request-id": "offline-fixture"}
    def __init__(self, data):
        self.data = data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def iter_content(self, size):
        yield json.dumps(self.data).encode()

class ProviderOfflineTests(unittest.TestCase):
    def setUp(self):
        # Fail closed even if a fixture is accidentally removed in future edits.
        self.socket_patch = patch("socket.socket.connect", side_effect=AssertionError("No network in independent review"))
        self.socket_patch.start()
        self.keys = {p: "offline-fixture-secret-" + p for p in pc.CAPS}
        self.credentials_patch = patch.object(pc, "credentials", return_value=self.keys)
        self.credentials_patch.start()
        self.temp = tempfile.TemporaryDirectory(prefix="independent-api-preflight-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()
        self.credentials_patch.stop()
        self.socket_patch.stop()

    def test_payloads_have_no_secret_or_tools(self):
        for config in pc.CONFIGS:
            endpoint, body = pc.make_request(config, "same scientific packet")
            text = json.dumps(body)
            self.assertTrue(endpoint.startswith("https://"))
            self.assertNotIn("tools", body)
            self.assertFalse(any(k in text for k in self.keys.values()))
            self.assertIn("same scientific packet", text)

    def test_reasoning_output_is_counted_once(self):
        fixtures = {
            "openai": {"status": "completed", "usage": {"input_tokens": 1000, "output_tokens": 500, "input_tokens_details": {"cached_tokens": 200}, "output_tokens_details": {"reasoning_tokens": 300}}},
            "deepseek": {"choices": [{"finish_reason": "stop", "message": {"content": ""}}], "usage": {"prompt_tokens": 1000, "completion_tokens": 500, "prompt_cache_hit_tokens": 200, "completion_tokens_details": {"reasoning_tokens": 300}}},
            "anthropic": {"stop_reason": "end_turn", "usage": {"input_tokens": 800, "output_tokens": 500, "cache_read_input_tokens": 200}},
            "gemini": {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "secret thought", "thought": True}, {"text": "final"}]}}], "usageMetadata": {"promptTokenCount": 1000, "candidatesTokenCount": 200, "thoughtsTokenCount": 300, "cachedContentTokenCount": 200}},
        }
        for provider, fixture in fixtures.items():
            value = pc.extract_response(provider, fixture)
            self.assertEqual(value["usage"]["output"], 500)
            self.assertNotIn("secret thought", value["text"])
        self.assertAlmostEqual(pc.price("CL_FABLE", {"input": 800, "output": 500, "cached": 200, "cache_write": 100}), .02744)

    def test_openai_cache_writes_are_priced(self):
        fixture = {"status": "completed", "usage": {"input_tokens": 12000, "output_tokens": 1000, "input_tokens_details": {"cached_tokens": 4000, "cache_write_tokens": 7000, "cache_write_tokens_details": {"ttl_30m_tokens": 7000, "ttl_12h_tokens": 0}}, "output_tokens_details": {"reasoning_tokens": 700}}}
        usage = pc.extract_response("openai", fixture)["usage"]
        # 1000 ordinary + 4000 cache reads + 7000 writes, plus 1000 total output.
        self.assertAlmostEqual(pc.price("OA_ASTRA", usage), .1515)
        self.assertAlmostEqual(pc.price("OA_SOL", usage), .0299)

    def test_reservation_exists_before_dispatch_and_no_retry(self):
        calls = []
        def fail_post(*args, **kwargs):
            calls.append((args, kwargs))
            folder = self.root / "calls" / "slot1"
            self.assertTrue((folder / "reservation.json").exists())
            self.assertTrue((folder / "request.json").exists())
            self.assertTrue((folder / "prompt.txt").exists())
            self.assertFalse(kwargs["allow_redirects"])
            raise TimeoutError("offline timeout " + self.keys["openai"])
        with patch.object(pc.requests, "post", side_effect=fail_post):
            receipt, parsed = pc.call_once(self.root, "slot1", "OA_SOL", "packet")
            self.assertEqual(len(calls), 1)
            self.assertIsNone(parsed)
            self.assertIsNone(receipt["tariff_cost_usd"])
            self.assertGreater(pc.ledger_accounted(self.root, "openai"), 0)
            with self.assertRaises(FileExistsError):
                pc.call_once(self.root, "slot1", "OA_SOL", "packet")
            self.assertEqual(len(calls), 1)
        self.assertNotIn(self.keys["openai"], json.dumps(receipt))

    def test_provider_budget_prevents_dispatch(self):
        with patch.dict(pc.CAPS, {"openai": 0.0001}), patch.object(pc.requests, "post") as post:
            with self.assertRaises(ValueError):
                pc.call_once(self.root, "slot1", "OA_ASTRA", "packet")
            post.assert_not_called()

    def test_request_receipt_captures_usage_and_redacts_secrets(self):
        fixture = {"id": "fixture-response", "model": "gpt-6.1-sol", "status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": artifact()}]}], "usage": {"input_tokens": 100, "output_tokens": 50}, "fixture_debug": self.keys["gemini"]}
        with patch.object(pc.requests, "post", return_value=FakeResponse(fixture)):
            receipt, parsed = pc.call_once(self.root, "slot1", "OA_SOL", "fixed packet")
        self.assertEqual(receipt["status"], "received")
        self.assertEqual(receipt["returned_model"], "gpt-6.1-sol")
        self.assertTrue(receipt["secrets_redacted"])
        self.assertIsNotNone(parsed)
        for f in (self.root / "calls" / "slot1").iterdir():
            text = f.read_text()
            self.assertFalse(any(k in text for k in self.keys.values()))

    def test_parse_is_nonexecuting(self):
        pc.parse_artifact(artifact("raise AssertionError('must not execute')\ndef generate(observed, spec, seed):\n    return None\n"))

    def test_invalid_signature_is_rejected(self):
        for signature in ["observed, spec, seed, *args", "observed, spec, seed, **kwargs", "observed, spec, seed, *, required", "observed, spec"]:
            with self.subTest(signature=signature), self.assertRaises(ValueError):
                pc.parse_artifact(artifact("def generate(" + signature + "):\n    return None\n"))

class PacketIntegrityTests(unittest.TestCase):
    def test_all_original_anchors_match(self):
        original = read(PROJECT / "work/manuscript_revision_v28_2026-11-10/CROSS_MODEL_PILOT.json")
        manifest = read(UNIT / "packets/ASSEMBLY_MANIFEST.json")
        anchors = {a["file"]: a["sha256"] for rows in original["packet_anchors"].values() for a in rows}
        self.assertEqual(len(anchors), 8)
        self.assertEqual(anchors, {a["path"]: a["sha256"] for a in manifest["original_input_anchors"]})
        for path, expected in anchors.items():
            self.assertEqual(sha(path), expected)
        self.assertEqual(sha(UNIT / "prepare_packets.py"), manifest["assembly_script_sha256"])
        self.assertEqual(sha(UNIT / "packets/common_prompt.txt"), manifest["common_prompt_sha256"])
        for case in manifest["cases"].values():
            for artifact_ in case["files"]:
                path = UNIT / "packets" / artifact_["path"]
                self.assertEqual(sha(path), artifact_["sha256"])
                self.assertEqual(path.stat().st_size, artifact_["bytes"])

    def test_prompts_are_only_common_and_three_visible_components(self):
        common = (UNIT / "packets/common_prompt.txt").read_text(encoding="utf-8").rstrip()
        for case in ["PNS", "LIPID"]:
            folder = UNIT / "packets" / case
            parts = [common]
            for marker, filename in [("TASK_JSON", "task.json"), ("REQUESTED_ANALYSES_JSON", "requested_analyses.json"), ("SOURCE_EVIDENCE_JSON", "evidence.json")]:
                parts.extend([marker, json.dumps(read(folder / filename), ensure_ascii=False, separators=(",", ":"))])
            expected = "\n\n".join(parts) + "\n"
            actual = (folder / "prompt.txt").read_text(encoding="utf-8")
            self.assertEqual(actual, expected)
            for forbidden in ["D:\\", "D:/", "gpt-6", "claude-fable", "deepseek", "gemini-4", "REFERENCE_SNAPSHOT", "target_estimates", "31001", "31003", "31007", "provider_cap", "schema-only"]:
                self.assertNotIn(forbidden, actual)
            self.assertEqual(read(folder / "task.json")["n_rows"], 3000)
            self.assertEqual(len(read(folder / "requested_analyses.json")["analyses"]), 3)

    def test_source_content_is_preserved_with_declared_transformations(self):
        manifest = read(UNIT / "packets/ASSEMBLY_MANIFEST.json")
        sources = {a["id"]: read(a["path"]) for a in manifest["original_input_anchors"]}
        pns = read(UNIT / "packets/PNS/evidence.json")
        expected = copy.deepcopy(sources["pns_evidence"])
        for row in expected["sources"]:
            for key in ["local_original_pattern", "original_fulltext", "local_reading_receipt", "derivation_script"]:
                row.pop(key, None)
        self.assertEqual(pns["source_evidence"], expected)
        self.assertEqual(pns["reported_moment_algebra"], sources["pns_moment_algebra"])
        lipid = read(UNIT / "packets/LIPID/evidence.json")
        self.assertEqual(lipid["sources"][0], sources["agongo"])
        self.assertEqual(lipid["sources"][2], sources["obirikorang"])
        greiner = lipid["sources"][1]
        self.assertEqual(records(greiner["reported_statistics"]), sources["greiner"]["reported_statistics"])
        expected_reg = copy.deepcopy(sources["greiner"]["reported_regressions_context_only"])
        for row in expected_reg:
            row.pop("numerical_calibration_allowed", None)
        self.assertEqual(records(greiner["reported_regressions_context_only"]), expected_reg)
        self.assertEqual(len(expected_reg), 12)
        self.assertEqual(len(records(greiner["reported_statistics"])), 48)
        metadata = lipid["population_metadata"]
        self.assertEqual(metadata, {key: sources["lipid_metadata"][key] for key in metadata})
        self.assertEqual(read(UNIT / "packets/LIPID/requested_analyses.json")["analyses"], sources["lipid_request"]["intended_analyses"])

class OrchestrationOfflineTests(unittest.TestCase):
    def test_frozen_plan_is_exact_twenty_slot_matrix(self):
        plan = read(UNIT / "RUN_PLAN.json")
        self.assertEqual(plan["configs"], pc.CONFIGS)
        self.assertEqual(plan["provider_caps_usd"], pc.CAPS)
        self.assertEqual(len(plan["constructions"]), 20)
        self.assertEqual({(s["packet_case"], s["model_config"], s["context"]) for s in plan["constructions"]}, {(case, model, context) for case in ["PNS", "LIPID"] for model in pc.CONFIGS for context in [1, 2]})
        for slot in plan["constructions"]:
            self.assertEqual(slot["prompt_path"], "packets/" + slot["packet_case"] + "/prompt.txt")

    def test_freeze_rejects_stale_review_and_modified_plan(self):
        with tempfile.TemporaryDirectory(prefix="independent-freeze-") as tmp:
            root = Path(tmp)
            plan = {"constructions": [{}] * 20, "configs": pc.CONFIGS, "provider_caps_usd": pc.CAPS}
            (root / "RUN_PLAN.json").write_text(json.dumps(plan), encoding="utf-8")
            review = {"status": "pass", "blocking_issues": [], "implementation_and_packet_hashes": {"fixture": "stale"}, "run_plan_sha256": sha(root / "RUN_PLAN.json")}
            (root / "review.json").write_text(json.dumps(review), encoding="utf-8")
            with patch.object(runner, "U", root), patch.object(runner, "hashes", return_value={"fixture": "current"}):
                with self.assertRaises(AssertionError):
                    runner.freeze("review.json")
                self.assertFalse((root / "LAUNCH_FREEZE.json").exists())
                review["implementation_and_packet_hashes"] = {"fixture": "current"}
                (root / "review.json").write_text(json.dumps(review), encoding="utf-8")
                runner.freeze("review.json")
                self.assertEqual(runner.verify_freeze(), plan)
                (root / "RUN_PLAN.json").write_text(json.dumps(dict(plan, changed=True)), encoding="utf-8")
                with self.assertRaises(AssertionError):
                    runner.verify_freeze()

    def test_existing_candidate_cannot_differ_from_api_capture(self):
        with tempfile.TemporaryDirectory(prefix="independent-orchestration-") as tmp:
            root = Path(tmp)
            source = root / "calls/fixture_initial"
            source.mkdir(parents=True)
            captured = json.loads(artifact())
            (source / "artifact.json").write_text(json.dumps(captured), encoding="utf-8")
            (source / "receipt.json").write_text(json.dumps({"artifact_status": "valid_structure_and_python_ast", "completion_status": "completed"}), encoding="utf-8")
            (root / "task.json").write_text("{}", encoding="utf-8")
            slot = {"construction_id": "fixture", "case_id": "PNS", "model_config": "OA_SOL", "context": 1, "task_path": "task.json"}
            with patch.object(runner, "U", root), patch.object(pc.requests, "post", side_effect=AssertionError("No API calls in review")):
                runner.choose_final(slot)
                (root / "candidates/fixture/generator.py").write_text("# altered scientific artifact", encoding="utf-8")
                with self.assertRaises((AssertionError, ValueError, RuntimeError)):
                    runner.choose_final(slot)

if __name__ == "__main__":
    unittest.main(verbosity=2)

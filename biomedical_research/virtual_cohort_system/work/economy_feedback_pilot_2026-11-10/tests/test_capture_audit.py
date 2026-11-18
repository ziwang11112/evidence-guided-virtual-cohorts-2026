"""Synthetic captures only; no network, keys, actual responses, or program execution."""
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
import audit_captures as auditor


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8", newline="\n")


class CaptureAudit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plan = auditor.read(auditor.ROOT/"RUN_PLAN.json")
        dump(self.root/"RUN_PLAN.json", self.plan)
        dump(self.root/"LAUNCH_FREEZE.json", {"run_plan_sha256": auditor.sha(self.root/"RUN_PLAN.json"), "implementation_and_packet_hashes": {}})
        outcomes = []
        for p in self.plan["parents"]:
            ident, config = p["parent_id"], p["model_config"]
            provider, model, ri, ro, rc, rw = auditor.TARIFF[config]
            prompt_path = self.root/p["prompt_path"]
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text("INERT source fixture\n", encoding="utf-8", newline="\n")
            dump(self.root/p["task_path"], {})
            folder = self.root/"calls/initial"/ident; folder.mkdir(parents=True)
            endpoint, body = auditor.expected_request(config, prompt_path.read_text())
            dump(folder/"request.json", {"endpoint": endpoint, "body": body})
            (folder/"prompt.txt").write_bytes(prompt_path.read_bytes())
            reserve = ((len(json.dumps(body, ensure_ascii=False).encode())+4096)*max(ri, rw)+32768*ro)/1e6
            dump(folder/"reservation.json", {"provider": provider, "config": config, "provider_cap_usd": auditor.CAPS[provider], "reserved_usd": reserve, "previous_accounted_usd": 0.})
            raw = ({"input_tokens": 1000, "output_tokens": 500, "input_tokens_details": {"cached_tokens": 100, "cache_write_tokens": 200}, "output_tokens_details": {"reasoning_tokens": 200}}
                   if provider == "openai" else {"prompt_tokens": 1000, "completion_tokens": 500, "prompt_cache_hit_tokens": 100, "completion_tokens_details": {"reasoning_tokens": 200}})
            usage = auditor.normalized(provider, raw)
            artifact = {"model_spec": {"fixture": 1}, "generator_py": "# never executed", "decision_record": {"fixture": True}}
            dump(folder/"artifact.json", artifact)
            (folder/"response_raw.json").write_text("inert raw bytes must only be hashed")
            (folder/"response_text.txt").write_text("inert extracted text must only be hashed")
            receipt = {"call_id": "initial/"+ident, "config": config, "provider": provider, "requested_model": model,
                       "returned_model": model, "http_status": 200, "tariff": self.plan["configs"][config], "no_automatic_retry": True,
                       "reserved_usd": reserve, "usage_raw": raw, "usage": usage, "tariff_cost_usd": auditor.cost(config, usage),
                       "status": "received", "completion_status": "completed", "artifact_status": "valid_structure_and_python_ast",
                       "request_sha256": auditor.sha(folder/"request.json"), "prompt_sha256": auditor.sha(folder/"prompt.txt")}
            for name in ["response_raw.json", "response_text.txt", "artifact.json"]: receipt[name+"_sha256"] = auditor.sha(folder/name)
            dump(folder/"receipt.json", receipt)
            candidate = "candidates/initial/"+ident; destination = self.root/candidate; destination.mkdir(parents=True)
            (destination/"generator.py").write_text(artifact["generator_py"], encoding="utf-8")
            dump(destination/"model_spec.json", {"task": {}, "model": artifact["model_spec"]})
            dump(destination/"decision_record.json", artifact["decision_record"])
            dump(destination/"capture_binding.json", {"call_path": "calls/initial/"+ident, "artifact_sha256": auditor.sha(folder/"artifact.json"), "host_scientific_edits": False})
            outcomes.append({k: p[k] for k in ["parent_id", "case_id", "model_config", "role", "task_path"]} | {"status": "sealed", "candidate_path": candidate, "failure_reason": None})
        dump(self.root/"INITIAL_OUTCOMES.json", {"records": outcomes})
        self.root_patch = patch.object(auditor, "ROOT", self.root); self.root_patch.start(); self.addCleanup(self.root_patch.stop)

    def test_full_eight_capture_audit_does_not_read_raw_or_extracted_text(self):
        original = Path.read_text
        def guarded(path, *args, **kwargs):
            if path.name in {"response_raw.json", "response_text.txt"}: raise AssertionError("Private capture text inspection forbidden")
            return original(path, *args, **kwargs)
        with patch.object(Path, "read_text", guarded): result = auditor.audit("initial")
        self.assertEqual(result["actual_calls"], 8)
        self.assertEqual(result["status"], "pass")

    def test_wrong_returned_model_blocks(self):
        path = self.root/"calls/initial/PNS_SOL_A/receipt.json"
        receipt = auditor.read(path); receipt["returned_model"] = "wrong-model"; dump(path, receipt)
        with self.assertRaisesRegex(ValueError, "Returned model mismatch"): auditor.audit("initial")

    def test_changed_actual_prompt_blocks_even_with_updated_request_hash(self):
        folder = self.root/"calls/initial/PNS_SOL_A"
        request = auditor.read(folder/"request.json"); request["body"]["input"] += " unauthorized suffix"; dump(folder/"request.json", request)
        receipt = auditor.read(folder/"receipt.json"); receipt["request_sha256"] = auditor.sha(folder/"request.json"); dump(folder/"receipt.json", receipt)
        with self.assertRaisesRegex(ValueError, "Exact request/settings/prompt mismatch"): auditor.audit("initial")

    def test_cache_write_reasoning_cost_is_inclusive(self):
        usage = {"input": 1000, "output": 500, "cached": 100, "cache_write": 200, "reasoning": 200}
        self.assertAlmostEqual(auditor.cost("OA_SOL", usage), (700*2+100*.1+200*2.5+500*10)/1e6)

    def test_transport_failure_without_response_retains_full_reservation(self):
        folder = self.root/"calls/initial/LIPID_DS"
        receipt = auditor.read(folder/"receipt.json")
        receipt.update(status="transport_or_capture_error", usage=None, tariff_cost_usd=None, error_type="ChunkedEncodingError")
        for key in ["returned_model", "http_status", "usage_raw", "completion_status", "artifact_status"]: receipt.pop(key, None)
        for name in ["response_raw.json", "response_text.txt", "artifact.json"]:
            (folder/name).unlink(); receipt.pop(name+"_sha256", None)
        dump(folder/"receipt.json", receipt)
        initial = auditor.read(self.root/"INITIAL_OUTCOMES.json")
        for row in initial["records"]:
            if row["parent_id"] == "LIPID_DS": row.update(status="failed", candidate_path=None, failure_reason="Explicit transport failure; no retry")
        dump(self.root/"INITIAL_OUTCOMES.json", initial)
        result = auditor.audit("initial")
        self.assertEqual(result["status"], "pass")
        report = auditor.read(self.root/"INITIAL_CALL_AUDIT.json")
        call = next(r for r in report["calls"] if r["id"] == "LIPID_DS")
        self.assertIsNone(call["tariff_cost_usd"])
        self.assertEqual(call["accounted_usd"], receipt["reserved_usd"])


if __name__ == "__main__": unittest.main(verbosity=2)

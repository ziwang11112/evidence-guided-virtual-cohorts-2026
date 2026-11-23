import json
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import verify_model as verifier

from evidence_replay import bound_flow, flow
from run_with_evidence_replay import send_new_design

TEST_DIR = Path(flow.__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))
from test_flow import GENERATOR, SOURCE, proposal


class TestSearchToModelAudit(unittest.TestCase):
    def seal_fixture(self, root, text):
        gate = root / "retrieval"
        gate.mkdir()
        raw = text.encode()
        sha = hashlib.sha256(raw).hexdigest()
        (root / "article.txt").write_bytes(raw)
        (gate / "selected_sources.txt").write_bytes(raw)
        (gate / "PMC123.txt").write_bytes(raw)
        (gate / "gateway_config.json").write_bytes(b"{}")
        doc = {"pmcid":"PMC123","status":"ok","text_bytes":len(raw),"text_sha256":sha}
        manifest = {"ids":["PMC123"],"sources":[doc],"bundle_sha256":sha,"bundle_bytes":len(raw),
                    "config_sha256":hashlib.sha256(b"{}").hexdigest()}
        (gate/"source_manifest.json").write_text(json.dumps(manifest),encoding="utf8")
        (gate/"retrieval_state.json").write_text(json.dumps(
            {"opens":{"PMC123":doc},"hits":{"PMC123":{"pmcid":"PMC123"}}}),encoding="utf8")

    def test_selected_handling_rejects_appended_or_injected_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.seal_fixture(root,"## [PMC123] Allowed study\n## [PMC456] Unapproved study")
            with self.assertRaisesRegex(ValueError,"headings"):
                verifier.checked_bundle(root)
            (root / "article.txt").write_text("replacement", encoding="utf8")
            with self.assertRaisesRegex(ValueError,"differs from handoff"):
                verifier.checked_bundle(root)

    def test_delivered_block_detects_substitution_append_and_extra_tool(self):
        article, request = "## [PMC123] Paper\nMean 4.2.", "Estimate its mean."
        prompt = verifier.handoff_prefix(article,request) + flow.author.DESIGN
        body = {"input":prompt, "model":"mock"}
        self.assertTrue(verifier.verify_body(body,article,request,"design")["exact_request_and_source_block"])
        for b,a,q in ((body,article.replace("4.2","4.3"),request), (body,article,"Edited task"),
                      (body|{"input":prompt.replace("\n\n" + flow.author.DESIGN,"\n\nUnselected paper")},
                       article,request), (body|{"tools":[{"type":"web_search"}]},article,request)):
            with self.assertRaises(ValueError):
                verifier.verify_body(b,a,q,"design")

    def test_locator_mapping_does_not_upgrade_an_assumption(self):
        rows = [
            dict(SOURCE,id="cross",source="[PMC12] Table 1 and [PMC13] Table 3",
                 applicability="transport_assumption"),
            dict(SOURCE,id="incomplete",source="Table 1"), dict(SOURCE,id="wrong",source="[PMC35] appendix"),
            dict(SOURCE,id="assumption",source="[PMC13] methods",provenance="assumed")]
        result = verifier.map_citations(rows,["PMC12","PMC13"])
        self.assertEqual([r["citation_status"] for r in result],["mapped","unmapped","unknown_pmcid","mapped"])
        self.assertEqual(result[0]["applicability"],"transport_assumption")
        self.assertEqual(result[3]["provenance"],"assumed")

    def test_recorded_full_workflow_and_final_csv_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            article = "## [PMC123] Development fixture\nA mean Z of 4.2 was observed."
            request = "Generate records for this population and describe Z.\n"
            self.seal_fixture(root, article)
            request_path = root/"REQUEST.txt"
            request_path.write_text(request,encoding="utf8")
            fact = dict(SOURCE,source="[PMC123] Table 1")
            design = {"population":"Whole study population", "columns":[{"name":"z","unit":"u"}],
                      "evidence":{"evidence_checks":[fact]}, "analyses":["Mean Z"],
                      "model_plan":"One column", "limitations":[]}
            submission = proposal(4.2)
            self.assertEqual(submission["generator_py"], GENERATOR)
            answers = iter([design, submission,
                            {"action":"keep","reason":"Observed mean confirmed.",
                             "conclusions":"Mean only.","dispositions":{}}])

            def fake_post(url, **kwargs):
                body = json.loads(kwargs["data"])
                api = {"id":"offline", "status":"completed", "model":body["model"],
                       "output":[{"type":"message","content":[{"type":"output_text",
                                 "text":json.dumps(next(answers))}]}],
                       "usage":{"input_tokens":100,"output_tokens":100}}
                response = Mock(status_code=200,headers={"x-request-id":"offline"})
                response.iter_content.return_value = [json.dumps(api).encode()]
                return response

            with patch.object(flow.author.client,"credentials",return_value={"openai":"example"}), \
                    patch("requests.post",side_effect=fake_post), \
                    patch("requests.sessions.Session.request",side_effect=AssertionError("Unexpected HTTP")):
                bound_flow.run(root/"model",article,request,send=send_new_design)
            report = verifier.audit(root,request_path)
            self.assertEqual(report["selected_source_ids_in_bundle"],["PMC123"])
            self.assertEqual(report["unmapped_item_ids"],[])
            self.assertEqual(len(report["tables"]),3)
            self.assertEqual(report["model_receipt_audit"]["final_numeric_comparisons_across_tables"],3)
            manifest = verifier.read(root/"model/final_manifest.json")
            with Path(manifest["runs"][0]["table"]).open("ab") as handle:
                handle.write(b"\n")
            with self.assertRaisesRegex(ValueError,"hash mismatch"):
                verifier.audit(root,request_path)


if __name__ == "__main__":
    unittest.main()

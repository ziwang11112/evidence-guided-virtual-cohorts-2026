"""Synthetic contamination-screen regression tests; no target outcome data."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import literature_gateway as gateway


class GatewayTests(unittest.TestCase):
    def setUp(self):
        # Keep even temporary test artifacts within the explicitly allowed tree.
        (gateway.ROOT / "literature").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="gateway_test_", dir=gateway.ROOT / "literature")
        self.literature_patch = patch.object(gateway, "LITERATURE", Path(self.temp.name))
        self.literature_patch.start()

    def tearDown(self):
        self.literature_patch.stop()
        self.temp.cleanup()

    def safe_record(self):
        return {"id": "123456", "source": "MED", "pmcid": "PMC123456", "doi": "10.1000/example", "title": "A controlled study of protein folding", "abstractText": "Purified proteins were studied using spectroscopy.", "pubYear": "2020"}

    def test_forbidden_aliases(self):
        for text in ["NHANES", "nhanes", "N.H.A.N.E.S.", "N H A N E S", "NH<b>AN</b>ES", "ＮＨＡＮＥＳ", "N\u200bHANES", "National Health and Nutrition Examination Survey", "National Health & Nutrition Examination Survey", "National Health Nutrition Examination Survey", "INS_J", "INS-J", "BMX_J", "WTSAF2YR", "LBXIN"]:
            with self.subTest(text=text):
                self.assertIsNotNone(gateway.forbidden_reason(text))

    def test_allowed_article(self):
        accepted, reason = gateway.screen_record(self.safe_record())
        self.assertIsNone(reason)
        self.assertEqual(accepted["pmid"], "123456")

    def test_missing_abstract_rejected(self):
        record = self.safe_record()
        record.pop("abstractText")
        self.assertEqual(gateway.screen_record(record)[1], "missing_title_or_abstract")

    def test_cli_is_ascii_safe_for_windows(self):
        record = self.safe_record()
        record["abstractText"] = "Protein concentration \u2265 one unit; \u03b1-helix."
        with patch.object(gateway, "api_search", return_value=([record], "opaque")):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(gateway.main(["search", "--query", "protein", "--limit", "1"]), 0)
        output.getvalue().encode("ascii")
        self.assertEqual(json.loads(output.getvalue())["accepted"][0]["abstract"], record["abstractText"])

    def test_search_rejects_before_display_or_save(self):
        rejected = self.safe_record()
        rejected.update(id="999999", abstractText="NHANES REJECTED_SENTINEL confidential simulated result")
        with patch.object(gateway, "api_search", return_value=([rejected, self.safe_record()], "opaque")):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(gateway.main(["search", "--query", "protein", "--limit", "2"]), 0)
        rendered = output.getvalue()
        self.assertNotIn("REJECTED_SENTINEL", rendered)
        self.assertEqual(json.loads(rendered)["rejected_count"], 1)
        for path in Path(self.temp.name).rglob("*"):
            if path.is_file():
                self.assertNotIn("REJECTED_SENTINEL", path.read_text(encoding="utf-8"))

    def test_fulltext_reference_rejected_before_save(self):
        raw = b"<article><body><p>Allowed body.</p></body><back><ref-list><ref>NHANES REJECTED_REFERENCE_SENTINEL</ref></ref-list></back></article>"
        with patch.object(gateway, "request_bytes", return_value=raw):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(gateway.main(["fetch", "--pmcid", "PMC123456"]), 2)
        self.assertNotIn("REJECTED_REFERENCE_SENTINEL", output.getvalue())
        self.assertFalse((Path(self.temp.name) / "approved").exists())
        self.assertNotIn("REJECTED_REFERENCE_SENTINEL", (Path(self.temp.name) / "audit.jsonl").read_text())

    def test_allowed_fulltext_saved_with_hash(self):
        raw = b"<article><front><article-title>Protein folding</article-title></front><body><p>Controlled laboratory experiment.</p></body></article>"
        with patch.object(gateway, "request_bytes", return_value=raw):
            result = gateway.fetch_article("pmcid", "PMC123456")
        self.assertEqual(result["status"], "accepted")
        path = gateway.ROOT / result["approved_artifact"]["path"]
        self.assertEqual(gateway.digest(path.read_bytes()), result["approved_artifact"]["sha256"])

    def test_url_blocking(self):
        for url in ["https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/INS_J.xpt", "https://www.cdc.gov/example", "https://example.com/article.pdf", "http://pmc.ncbi.nlm.nih.gov/articles/PMC123456/", "https://pmc.ncbi.nlm.nih.gov.evil.test/articles/PMC123456/", "https://pmc.ncbi.nlm.nih.gov/articles/PMC123456/bin/patients.csv", "https://pmc.ncbi.nlm.nih.gov/articles/PMC123456/?download=raw", "https://user:secret@pmc.ncbi.nlm.nih.gov/articles/PMC123456/", "file:///tmp/patients.csv"]:
            with self.subTest(url=url), self.assertRaises(gateway.GatewayError):
                gateway.article_from_url(url)

    def test_url_normalization(self):
        self.assertEqual(gateway.article_from_url("https://pmc.ncbi.nlm.nih.gov/articles/PMC123456/"), ("pmcid", "PMC123456"))
        self.assertEqual(gateway.article_from_url("https://pubmed.ncbi.nlm.nih.gov/123456/"), ("pmid", "123456"))

    def test_bad_url_never_requests_network(self):
        with patch.object(gateway, "request_bytes") as network:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(gateway.main(["fetch", "--url", "https://wwwn.cdc.gov/INS_J.xpt"]), 2)
            network.assert_not_called()

    def test_unsafe_redirect_is_blocked(self):
        self.assertFalse(gateway.allowed_api_url("https://wwwn.cdc.gov/INS_J.xpt"))
        self.assertFalse(gateway.allowed_api_url("https://www.ebi.ac.uk.evil.test/europepmc/webservices/rest/search"))

    def test_audit_append_only(self):
        gateway.audit({"action": "test", "status": "first"})
        before = (Path(self.temp.name) / "audit.jsonl").read_bytes()
        gateway.audit({"action": "test", "status": "second"})
        after = (Path(self.temp.name) / "audit.jsonl").read_bytes()
        self.assertTrue(after.startswith(before))
        self.assertEqual(len(after.splitlines()), 2)

    def test_limit_validation(self):
        with patch.object(gateway, "request_bytes") as network, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gateway.main(["search", "--query", "protein", "--limit", "21"]), 2)
            network.assert_not_called()


if __name__ == "__main__":
    unittest.main()

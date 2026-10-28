"""Synthetic safety, provenance, parser and cumulative-budget tests only."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import literature_gateway as gateway


ROOT = Path(__file__).resolve().parent


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT, prefix="synthetic_test_")
        self.base = Path(self.temp.name)
        self.config = json.loads((ROOT / "gateway_config.json").read_text())
        self.config_path = self.base / "config.json"
        self.config_path.write_bytes(gateway.encoded(self.config))
        self.screen = gateway.Screen(self.config)
        self.session_path = self.base / "session"

    def tearDown(self):
        self.temp.cleanup()

    def command(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = gateway.main(["--session", str(self.session_path), "--config", str(self.config_path), *args])
        out.getvalue().encode("ascii")
        self.assertEqual(err.getvalue(), "")
        return code, json.loads(out.getvalue())

    def safe_record(self):
        return {"id": "123", "source": "MED", "pmcid": "PMC123", "title": "Synthetic neutral paper", "abstractText": "Synthetic result ≥ one unit."}

    def search_raw(self, records=None):
        return gateway.encoded({"hitCount": len(records or [self.safe_record()]), "resultList": {"result": records or [self.safe_record()]}, "nextCursorMark": "next"})

    def fixture(self, supplementary=b"name,value\nalpha,1\n", suffix="csv"):
        filename = "supplement." + suffix
        article = ('<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><article-meta>'
                   '<article-id pub-id-type="pmcid">PMC123</article-id><article-title>Synthetic article</article-title>'
                   '</article-meta></front><body><p>Complete synthetic body.</p>'
                   '<supplementary-material><media xlink:href="' + filename + '"/></supplementary-material>'
                   '</body><back><ref>Complete synthetic reference.</ref></back></article>').encode()
        def url(name, raw):
            return gateway.CLOUD + "/PMC123.1/" + name + "?md5=" + hashlib.md5(raw).hexdigest()
        xml_url, supp_url = url("PMC123.1.xml", article), url(filename, supplementary)
        manifest = gateway.encoded({"pmcid": "PMC123", "version": 1, "xml_url": xml_url, "media_urls": [supp_url], "title": "Synthetic article"})
        listing = b'<ListBucketResult><IsTruncated>false</IsTruncated><CommonPrefixes><Prefix>PMC123.1/</Prefix></CommonPrefixes></ListBucketResult>'
        def fake(url, *_args):
            if url.startswith(gateway.API):
                return self.search_raw()
            if "list-type=" in url:
                return listing
            if url.endswith(".json"):
                return manifest
            if url == xml_url:
                return article
            if url == supp_url:
                return supplementary
            raise AssertionError("Unexpected network URL")
        return fake

    def assert_no_sentinel(self, output):
        self.assertNotIn("REJECTED_SENTINEL", json.dumps(output))
        for path in self.session_path.rglob("*"):
            if path.is_file():
                self.assertNotIn(b"REJECTED_SENTINEL", path.read_bytes())

    def test_full_alias_variants(self):
        for value in ["NHANES", "N H A N E S", "N.H.A.N.E.S.", "NH<b>AN</b>ES", "N\u200bHANES", "ＮＨＡＮＥＳ", "NH&#65;NES", "%4eHANES", "National Health & Nutrition Examination Survey", "Hispanic Health and Nutrition Examination Survey", "HANES I", "National Health and Nutrition Examination Survey III", "RIDAGEYR"]:
            with self.subTest(value=value):
                self.assertIsNotNone(self.screen.reason(value))
        self.assertIsNone(self.screen.reason("Synthetic purified protein study."))

    def test_search_rejection_is_opaque_and_ascii(self):
        bad = self.safe_record()
        bad["abstractText"] = "NHANES REJECTED_SENTINEL"
        with patch.object(gateway, "http_get", return_value=self.search_raw([bad, self.safe_record()])):
            code, output = self.command("search", "--query", "synthetic", "--limit", "2")
        self.assertEqual(code, 0)
        self.assertEqual(output["accepted_count"], 1)
        self.assertEqual(output["rejected_count"], 1)
        self.assert_no_sentinel(output)
        audit = [json.loads(line) for line in (self.session_path / "audit.jsonl").read_text().splitlines()]
        rejection = next(e for e in audit if e["type"] == "screening")["rejected"][0]
        self.assertEqual(set(rejection), {"reason", "content_sha256"})

    def test_cumulative_query_budget_and_immutable_config(self):
        self.config["budgets"]["queries"] = 1
        self.config_path.write_bytes(gateway.encoded(self.config))
        with patch.object(gateway, "http_get", return_value=self.search_raw()) as network:
            self.assertEqual(self.command("search", "--query", "synthetic")[0], 0)
            code, output = self.command("search", "--query", "revision")
            self.assertEqual(output["reason"], "budget_exhausted_queries")
            self.assertEqual(network.call_count, 1)
        self.config["budgets"]["queries"] = 2
        self.config_path.write_bytes(gateway.encoded(self.config))
        self.assertEqual(self.command("search", "--query", "revision")[1]["reason"], "session_configuration_or_path_changed")

    def test_failed_request_counts_and_no_retry(self):
        with patch.object(gateway, "http_get", side_effect=gateway.GatewayError("network_or_timeout_failure")) as network:
            _, output = self.command("search", "--query", "synthetic")
        self.assertEqual(output["usage"]["queries"], 1)
        self.assertEqual(output["usage"]["http_attempts"], 1)
        self.assertEqual(output["usage"]["http_successes"], 0)
        self.assertEqual(network.call_count, 1)

    def test_complete_parent_supplement_flow_and_artifact_registry(self):
        with patch.object(gateway, "http_get", side_effect=self.fixture()):
            code, article = self.command("fetch", "--pmcid", "PMC123")
            self.assertEqual(code, 0, article)
            self.assertIn("Complete synthetic reference", article["text"])
            _, listing = self.command("list-supplements", "--pmcid", "PMC123")
            item = listing["supplements"][0]
            self.assertEqual(item["status"], "available")
            code, supplement = self.command("fetch-supplement", "--pmcid", "PMC123", "--supplement-id", item["supplement_id"])
        self.assertEqual(code, 0, supplement)
        self.assertEqual(supplement["rows"], 2)
        self.assertEqual(supplement["usage"]["downloads"], 2)
        self.assertEqual(supplement["parent_xml_sha256"], article["xml_artifact"]["sha256"])
        artifact = supplement["approved_artifact"]
        self.assertEqual(gateway.digest((self.session_path / artifact["session_relative_path"]).read_bytes()), artifact["sha256"])
        audit = [json.loads(line) for line in (self.session_path / "audit.jsonl").read_text().splitlines()]
        self.assertTrue(any(e.get("type") == "artifact_approved" and e.get("artifact") == artifact and e["status"] == "accepted" for e in audit))

    def test_supplement_rejected_before_save(self):
        with patch.object(gateway, "http_get", side_effect=self.fixture(b"name,value\nNHANES,REJECTED_SENTINEL\n")):
            self.assertEqual(self.command("fetch", "--pmcid", "PMC123")[0], 0)
            item = self.command("list-supplements", "--pmcid", "PMC123")[1]["supplements"][0]
            code, output = self.command("fetch-supplement", "--pmcid", "PMC123", "--supplement-id", item["supplement_id"])
        self.assertEqual(code, 2)
        self.assertEqual(output["status"], "rejected")
        self.assertEqual(output["usage"]["downloads"], 2)
        self.assert_no_sentinel(output)

    def test_unknown_supplement_and_cross_parent_url_never_download(self):
        with patch.object(gateway, "http_get", side_effect=self.fixture()) as network:
            self.command("fetch", "--pmcid", "PMC123")
            before = network.call_count
            output = self.command("fetch-supplement", "--pmcid", "PMC123", "--supplement-id", "arbitrary")[1]
            self.assertEqual(output["reason"], "unknown_source_linked_supplement")
            self.assertEqual(network.call_count, before)
        session = gateway.Session(self.session_path, self.config_path)
        try:
            with self.assertRaises(gateway.GatewayError):
                session.object_url(gateway.CLOUD + "/PMC999.1/file.csv?md5=" + "a" * 32, "PMC123", 1)
        finally:
            session.close()

    def test_download_budget_shared_with_revision(self):
        self.config["budgets"]["downloads"] = 1
        self.config_path.write_bytes(gateway.encoded(self.config))
        with patch.object(gateway, "http_get", side_effect=self.fixture()):
            self.command("fetch", "--pmcid", "PMC123")
            item = self.command("list-supplements", "--pmcid", "PMC123")[1]["supplements"][0]
            output = self.command("fetch-supplement", "--pmcid", "PMC123", "--supplement-id", item["supplement_id"])[1]
        self.assertEqual(output["reason"], "budget_exhausted_downloads")

    def test_session_separation_and_lock(self):
        session = gateway.Session(self.session_path, self.config_path)
        try:
            with self.assertRaises(gateway.GatewayError) as caught:
                gateway.Session(self.session_path, self.config_path)
            self.assertEqual(caught.exception.reason, "session_locked")
            another = gateway.Session(self.base / "other_session", self.config_path)
            try:
                self.assertEqual(another.state["parents"], {})
                self.assertEqual(another.state["usage"]["queries"], 0)
            finally:
                another.close()
        finally:
            session.close()

    def test_url_and_redirect_boundary(self):
        for url in ["https://www.ebi.ac.uk.evil.test/europepmc/webservices/rest/search", "https://www.cdc.gov/", gateway.CLOUD + "/PMC123.1/../secret.csv", gateway.CLOUD + "/PMC123.1/%2e%2e%2fsecret.csv", gateway.CLOUD + "/PMC123.1/file.csv?other=value", "http://pmc-oa-opendata.s3.amazonaws.com/PMC123.1/file.csv"]:
            self.assertFalse(gateway.allowed_url(url), url)
        good = gateway.CLOUD + "/PMC123.1/file.csv?md5=" + "a" * 32
        self.assertTrue(gateway.allowed_url(good))
        with self.assertRaises(gateway.GatewayError):
            gateway.RestrictedRedirect(good).redirect_request(None, None, 302, "", {}, good.replace("PMC123", "PMC999"))

    def test_parsers_fail_closed(self):
        for raw, kind in [(b"<root>unfinished", "xml"), (b'<!DOCTYPE x [<!ENTITY a "secret">]><x>&a;</x>', "xml"), (b"a,b\nc\n", "csv"), (b'a,b\n"unfinished,b', "csv"), (b"<html><body><p>unfinished</body></html>", "html"), (b"<html><body><img src='a.png'></body></html>", "html"), (b"a\x00b", "text")]:
            with self.subTest(kind=kind, raw=raw), self.assertRaises(gateway.GatewayError):
                gateway.parse_supplement(raw, kind, self.screen, 100)
        value = gateway.parse_supplement(b"<html><body><p>All content</p></body></html>", "html", self.screen, 100)
        self.assertEqual(value["text"], "All content")

    def test_no_silent_search_truncation(self):
        with patch.object(gateway, "http_get", return_value=self.search_raw([self.safe_record(), self.safe_record()])):
            output = self.command("search", "--query", "synthetic", "--limit", "1")[1]
        self.assertEqual(output["reason"], "invalid_search_response")

    def xlsx_bytes(self, excluded=False):
        import openpyxl
        book = openpyxl.Workbook()
        book.active["A1"] = "Synthetic"
        book.active["A2"] = "=1+1"
        hidden = book.create_sheet("Hidden")
        hidden.sheet_state = "hidden"
        hidden["B2"] = "NHANES REJECTED_SENTINEL" if excluded else 42
        out = io.BytesIO()
        book.save(out)
        return out.getvalue()

    def test_xlsx_hidden_cells_and_formula_missing_cache(self):
        value = gateway.parse_supplement(self.xlsx_bytes(), "xlsx", self.screen, 1000)
        self.assertEqual(value["nonempty_cells"], 3)
        formula = value["sheets"][0]["cells"][1]
        self.assertEqual(formula["formula"], "=1+1")
        self.assertTrue(formula["cached_value_missing"])
        self.assertFalse(formula["formula_evaluated"])
        self.assertEqual(value["sheets"][1]["state"], "hidden")

    def test_xlsx_hidden_exclusion_and_archive_traversal(self):
        with self.assertRaises(gateway.GatewayError) as caught:
            gateway.parse_supplement(self.xlsx_bytes(excluded=True), "xlsx", self.screen, 1000)
        self.assertEqual(caught.exception.reason, "excluded_study_alias")
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as archive:
            archive.writestr("../escape.xml", "<x>unsafe</x>")
        with self.assertRaises(gateway.GatewayError) as caught:
            gateway.parse_supplement(out.getvalue(), "xlsx", self.screen, 1000)
        self.assertEqual(caught.exception.reason, "unsafe_xlsx_archive_member")

    def test_unsupported_pdf_explicit_without_download(self):
        with patch.object(gateway, "http_get", side_effect=self.fixture(b"%PDF-synthetic", "pdf")) as network:
            self.command("fetch", "--pmcid", "PMC123")
            item = self.command("list-supplements", "--pmcid", "PMC123")[1]["supplements"][0]
            self.assertEqual(item["status"], "unsupported")
            count = network.call_count
            result = self.command("fetch-supplement", "--pmcid", "PMC123", "--supplement-id", item["supplement_id"])[1]
            self.assertEqual(network.call_count, count)
            self.assertEqual(result["reason"], "unsupported_supplement_format")


if __name__ == "__main__":
    unittest.main()

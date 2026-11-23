"""Tamper checks for an original-image reader request; no API or data download."""
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import audit_handoff as audit


class NativeSourceReceipt(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.raw = b"fractional pixels kept as bytes"
        self.question = "What value and uncertainty are in the first row?"
        self.url = "https://pmc-oa-opendata.s3.amazonaws.com/PMC77.1/t2.jpg?md5="+hashlib.md5(self.raw).hexdigest()
        self.meta = {"id":"PMC77:T2","pmcid":"PMC77","label":"Table 2","caption":"A comparison",
                     "footnotes":"","kind":"image","sha256":audit.sha(self.raw)}
        self.table = dict(self.meta,url=self.url)
        self.decoded = {"table_id":"PMC77:T2","status":"not_found","cells":[],"limitations":["Unavailable."]}
        self.receipt = {"request_sha256":"req","response_raw_sha256":"res","tariff_cost_usd":0.01}
        self.msg = [{"type":"input_text","text":"Return the JSON extraction for this question and table.\n"+
                      json.dumps({"question":self.question,"table":self.meta})},
                    {"type":"input_image","detail":"high","image_url":"data:image/jpeg;base64,"+
                     base64.b64encode(self.raw).decode()}]
        self.media = self.root/(audit.sha(self.url.encode())+".jpg")
        self.media.write_bytes(self.raw)
        extraction = audit.validate_extraction(self.decoded,self.table)
        extraction.update(api_request_sha256="req",api_response_sha256="res",tariff_cost_usd=.01)
        (self.root/"extraction.json").write_text(json.dumps(extraction),encoding="utf8")

    def check(self, question=None):
        with patch.object(audit,"captured",return_value=({"input":[{"role":"user","content":self.msg}]},
                          self.decoded,self.receipt)):
            return audit.reader_proof(self.root,1,question or self.question,self.table,self.root,"example")

    def test_exact_source_and_derived_record(self):
        self.assertEqual(self.check()["sha256"],self.meta["sha256"])
        self.assertEqual(self.check()["status"],"not_found")

    def test_another_question(self):
        with self.assertRaisesRegex(ValueError,"different question"):
            self.check("Give the first two rows")

    def test_swapped_media(self):
        self.media.write_bytes(b"replacement image")
        with self.assertRaisesRegex(ValueError,"cached file"):
            self.check()

    def test_changed_local_transcript(self):
        (self.root/"extraction.json").write_text("{}",encoding="utf8")
        with self.assertRaisesRegex(ValueError,"captured response"):
            self.check()

    def test_joint_native_and_cache_tamper(self):
        other = b"both files changed after download"
        self.media.write_bytes(other)
        self.msg[1]["image_url"] = "data:image/jpeg;base64,"+base64.b64encode(other).decode()
        with self.assertRaisesRegex(ValueError,"published file"):
            self.check()


if __name__ == "__main__":
    unittest.main()

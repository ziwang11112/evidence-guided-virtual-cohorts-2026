import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import read_table as reader


def table():
    text = '["Measure", "Mean (SD), μm"]\n["Sensor A", "41.3 (3.1)"]'
    return {"id":"PMC123:T1","pmcid":"PMC123","label":"Table 1","caption":"Measurements",
            "footnotes":["Mean (SD)"],"kind":"text","text":text,"sha256":reader.transport.sha_bytes(text.encode())}


def extracted(source):
    return {"table_id":source["id"],"status":"found","limitations":[],
            "cells":[{"row":"Sensor A","column":"Mean (SD), μm","printed_value":"41.3 (3.1)",
                      "unit":"μm","statistic":"mean","uncertainty":"SD",
                      "population":None,"measurement":"Sensor A","timepoint":None}]}


class TestReader(unittest.TestCase):
    def test_exact_native_image_and_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            # The approved-source loader validates image dimensions and decoding. Here we
            # exercise identity and verify that no local pathname is sent to the model.
            raw = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a1WkAAAAASUVORK5CYII=")
            path = Path(temp)/"local-only-table.png"
            path.write_bytes(raw)
            item = {**table(),"kind":"image","path":str(path),"mime":"image/png","sha256":reader.transport.sha_bytes(raw)}
            body = reader._request(item,"Find the values for both devices")
            parts = body["input"][0]["content"]
            self.assertEqual(parts[1]["type"],"input_image")
            self.assertEqual(parts[1]["detail"],"high")
            self.assertEqual(base64.b64decode(parts[1]["image_url"].split(",",1)[1]),raw)
            self.assertNotIn(str(path), json.dumps(body))
            item["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                reader._request(item,"Read it")

    def test_verified_text_capture_resume_and_limits(self):
        item = table()
        response = Mock(status_code=200,headers={"x-request-id":"offline-fixture"})
        envelope = {"model":reader.MODEL,"status":"completed","usage":{"input_tokens":50,"output_tokens":60},
                    "output":[{"type":"message","content":[{"type":"output_text",
                    "text":json.dumps(extracted(item),ensure_ascii=False)}]}]}
        response.iter_content.return_value = [json.dumps(envelope).encode()]
        with tempfile.TemporaryDirectory() as td, patch.object(
                reader.author.client,"credentials",return_value={"openai":"fake-long-token-for-test"}), patch(
                "requests.post",return_value=response) as post:
            root = Path(td)
            value = reader.read(root,1,item,"Give the printed mean and SD")
            self.assertEqual(value["cells"][0]["printed_value"],"41.3 (3.1)")
            wire = json.loads(post.call_args.kwargs["data"])
            self.assertEqual(wire["input"][0]["content"][1],{"type":"input_text","text":item["text"]})
            self.assertEqual(reader.read(root,1,item,"Give the printed mean and SD"),value)
            self.assertGreater(value["tariff_cost_usd"],0)
            with self.assertRaisesRegex(ValueError,"different question"):
                reader.read(root,1,item,"Different question")
            with self.assertRaisesRegex(ValueError,"two table-reading"):
                reader.read(root,3,item,"Read again")
            self.assertEqual(post.call_count,1)

    def test_unsupported_or_invented_read_status(self):
        item = table()
        result = extracted(item)
        self.assertEqual(reader._validate({**result,"status":"not_found","cells":[]},item)["status"],"not_found")
        with self.assertRaisesRegex(ValueError,"Cell count"):
            reader._validate({**result,"status":"illegible"},item)
        with self.assertRaisesRegex(ValueError,"different source"):
            reader._validate({**result,"table_id":"PMC999:T1"},item)
        del result["cells"][0]["column"]
        with self.assertRaisesRegex(ValueError,"cell field"):
            reader._validate(result,item)


if __name__ == "__main__":
    unittest.main()

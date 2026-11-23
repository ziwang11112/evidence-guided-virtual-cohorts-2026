from io import BytesIO
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from PIL import Image
from table_tools import TableTools, sha


XML = b"""<article xmlns:xlink="http://www.w3.org/1999/xlink">
<body><sec><fig id="figure"><graphic xlink:href="plot.png"/></fig>
<table-wrap id="numbers"><label>Table 1</label><caption><p>Measurement summaries</p></caption>
<table><tr><th>Measurement</th><th>Mean</th></tr><tr><td>A</td><td>12</td></tr></table>
<table-wrap-foot><p>Mean in native units.</p></table-wrap-foot></table-wrap></sec></body>
<floats-group><table-wrap id="photo"><label>Table 2</label><caption><p>Agreement by test</p></caption>
<graphic xlink:href="table.png"/></table-wrap>
<table-wrap id="bad"><caption><p>Individual patient measurements</p></caption><graphic xlink:href="table.png"/></table-wrap>
<table-wrap id="remote"><caption><p>Paper summaries</p></caption><graphic xlink:href="https://elsewhere/plot.png"/></table-wrap>
<supplementary-material><table-wrap id="supp"><graphic xlink:href="table.png"/></table-wrap></supplementary-material>
<table-wrap id="numbered"><table><tr><th>Participant ID</th></tr><tr><td>P1</td></tr></table></table-wrap>
</floats-group></article>"""


def prepare(root):
    p=root/"ret"; p.mkdir()
    (p/"gateway_config.json").write_bytes(b"{}")
    (p/"selected_sources.txt").write_bytes(b"permitted narrative")
    (p/"source_manifest.json").write_text(json.dumps({
        "ids":["PMC9"], "sources":[{"pmcid":"PMC9","version":3,"xml_sha256":sha(XML)}],
        "bundle_sha256":sha(b"permitted narrative"),"config_sha256":sha(b"{}")}))
    out = BytesIO()
    Image.new("RGB",(12,14)).save(out,format="PNG")
    raw=out.getvalue()
    url="https://pmc-oa-opendata.s3.amazonaws.com/PMC9.3/table.png?md5="+hashlib.md5(raw).hexdigest()
    manifest=json.dumps({"pmcid":"PMC9","version":3,"media_urls":[url]}).encode()
    fake=Mock()
    fake.parent.return_value={"version":3,"xml_artifact":"xml","manifest_artifact":"manifest"}
    fake.read_artifact.side_effect=lambda key: {"xml":XML,"manifest":manifest}[key]
    fake.object_url.side_effect=lambda link,pmcid,version: link
    download=Mock(return_value=(raw,"image/png"))
    return p,lambda *_:fake,download,raw


class TestTableTools(unittest.TestCase):
    def test_all_selected_original_tables_and_requested_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            retrieval,factory,download,raw=prepare(root)
            tool=TableTools(retrieval,root/"private",session_factory=factory,download=download)
            entries={r["id"]:r for r in tool.index()}
            self.assertEqual(set(entries),{"PMC9:numbers","PMC9:photo","PMC9:bad","PMC9:remote","PMC9:numbered"})
            self.assertEqual(entries["PMC9:photo"]["kind"],"image")
            self.assertEqual(entries["PMC9:remote"]["status"],"unavailable")
            for table_id in ("PMC9:figure","PMC9:supp","PMC9:bad","PMC9:numbered","PMC10:photo"):
                with self.assertRaises(ValueError):
                    tool.get(table_id)
            native=tool.get("PMC9:numbers")
            self.assertIn('["A", "12"]',native["text"])
            self.assertIn("Mean in native units.",native["text"])
            self.assertEqual(native["sha256"],sha(native["text"].encode()))
            download.assert_not_called()
            image=tool.get("PMC9:photo")
            self.assertEqual(image["dimensions"],[12,14])
            self.assertEqual(Path(image["path"]).read_bytes(),raw)
            self.assertEqual(image["sha256"],sha(raw))
            self.assertEqual(tool.get("PMC9:photo"),image)
            download.assert_called_once()

    def test_corrupt_wrong_format_and_edited_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            retrieval,factory,download,raw=prepare(root)
            tool=TableTools(retrieval,root/"private",session_factory=factory,download=download)
            download.return_value=(b"different","image/png")
            with self.assertRaisesRegex(ValueError,"manifest"):
                tool.get("PMC9:photo")
            download.return_value=(raw,"image/jpeg")
            with self.assertRaisesRegex(ValueError,"format"):
                tool.get("PMC9:photo")
            download.return_value=(raw,"image/png")
            verified=tool.get("PMC9:photo")
            Path(verified["path"]).write_bytes(b"tamper")
            with self.assertRaisesRegex(ValueError,"manifest"):
                tool.get("PMC9:photo")

    def test_changed_selected_text_or_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            retrieval,factory,download,raw=prepare(root)
            args=dict(session_factory=factory,download=download)
            (retrieval/"selected_sources.txt").write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError,"binding"):
                TableTools(retrieval,root/"private",**args)
            (retrieval/"selected_sources.txt").write_bytes(b"permitted narrative")
            fake=factory()
            fake.parent.return_value["version"]=4
            with self.assertRaisesRegex(ValueError,"binding"):
                TableTools(retrieval,root/"private",**args)

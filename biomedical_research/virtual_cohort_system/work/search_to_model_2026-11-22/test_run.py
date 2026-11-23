from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

from run import discover


class TestDiscoveryHandoff(unittest.TestCase):
    def test_selected_paper_must_have_been_opened(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            gw = Mock()
            gw.search.return_value = {"hits":[{"pmcid":"PMC1"}]}
            gw.open.return_value = {"text":"# primary source","pmcid":"PMC1"}
            gw.seal.return_value = "## [PMC1] Title\nOne scientific finding."
            choices = [
                {"action":"search","query":"random paired biomarker","reason":"Identify studies."},
                {"action":"select","pmcids":["PMC1"],"reason":"Attempt before opening."},
                {"action":"open","pmcid":"PMC1","reason":"Read source."},
                {"action":"select","pmcids":["PMC1"],"reason":"Has paired measurements."}]
            recorder = Mock(side_effect=choices)
            selection, bundle = discover(root,"A new question",gw,decision=recorder)
            self.assertEqual(selection["actions"],4)
            self.assertIn("invalid_selection",recorder.call_args_list[2].args[2])
            self.assertEqual((root/"article.txt").read_bytes(),bundle.encode())
            self.assertEqual(gw.seal.call_count,1)
            again = discover(root,"A new question",gw,decision=Mock(side_effect=choices))
            self.assertEqual(again,(selection,bundle))
            self.assertEqual(gw.search.call_count,1)
            self.assertEqual(gw.open.call_count,1)

    def test_abstention_has_no_model_input(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, article = discover(root,"Question",Mock(),decision=lambda *args: {
                "action":"abstain","reason":"No usable source within scope."})
            self.assertEqual(selection["status"],"abstained")
            self.assertIsNone(article)
            self.assertFalse((root/"article.txt").exists())

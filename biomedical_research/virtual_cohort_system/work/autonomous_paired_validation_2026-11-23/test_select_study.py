import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from select_study import EligibleArticles, read_eligible


class MockGateway:
    def search(self,query):
        self.query=query
        return {"status":"ok","hits":[
            {"pmcid":"PMC1","doi":"10.1000/aa","title":"Article A","year":"2019",
             "abstract_preview":"hidden endpoint","metadata_sha256":"private-key"},
            {"pmcid":"PMC2","doi":"10.1000/wrong","title":"mismatch"},
            {"pmcid":"PMC88","doi":"10.1000/cc","title":"outside"}]}

    def seal(self,selected):
        return list(selected)


class SelectionTests(unittest.TestCase):
    def test_pool_is_screened_and_contains_multiple_distinct_candidates(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/"eligible.json"
            rows=[{"pmcid":"PMC2","doi":"10.1000/bb","paired_file":"held-out.csv"},
                  {"pmcid":"PMC1","doi":"10.1000/aa","secret":"measurement 0.055"}]
            path.write_text(json.dumps(rows),encoding="utf8")
            norm=read_eligible(path)
            self.assertEqual(norm,{"PMC1":"10.1000/aa","PMC2":"10.1000/bb"})
            for items in ([rows[0]],rows+[rows[1]],[rows[0],{**rows[1],"doi":rows[0]["doi"]}]):
                path.write_text(json.dumps(items),encoding="utf8")
                with self.assertRaises(ValueError):
                    read_eligible(path)

    def test_only_metadata_is_exposed_at_search(self):
        mock=MockGateway()
        gateway=EligibleArticles(mock,{"PMC1":"10.1000/aa","PMC2":"10.1000/bb"})
        result=gateway.search("TITLE:trial")
        self.assertIn('(TITLE:trial) AND (DOI:"10.1000/aa" OR DOI:"10.1000/bb")',mock.query)
        self.assertEqual([h["pmcid"] for h in result["hits"]],["PMC1"])
        self.assertNotIn("hidden endpoint",json.dumps(result))
        self.assertNotIn("private-key",json.dumps(result))
        self.assertEqual(gateway.seal(["PMC1"]),["PMC1"])
        for bad in (["PMC1","PMC2"],["PMC88"]):
            with self.assertRaises(ValueError):
                gateway.seal(bad)
        with self.assertRaises(ValueError):
            gateway.open("PMC88")

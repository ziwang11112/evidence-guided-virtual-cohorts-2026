"""Offline tests for session-only selection, scientific table layout and provenance."""
import json
from pathlib import Path
import tempfile
import unittest

from retrieve import ARTICLE_BYTES, Retrieval, render, sha


def sample_xml(cells, prose="", doi="10.0000/foo"):
    rows="".join("<tr>"+"".join("<td>"+c+"</td>" for c in r)+"</tr>" for r in cells)
    return f"""<article><front><article-meta><article-title>Test article</article-title>
      <article-id pub-id-type="doi">{doi}</article-id><abstract>Summary.</abstract>
      </article-meta></front><body><sec><title>Results</title>
      <p>{prose}<table-wrap><caption>Results by method</caption><table>{rows}</table></table-wrap>
      Some following text.</p><fig><caption>Comparison by method</caption><graphic/></fig>
      <supplementary-material><p>secret raw supplement</p></supplementary-material>
      </sec></body></article>""".encode()


class Fake:
    def __init__(self,xml):
        self.xml=xml
        self.queries=[]
        self.fetches=[]

    def search(self,q,n):
        self.queries.append((q,n))
        return {"accepted":[{"title":"Test article","doi":"10.0000/foo","pmcid":"PMC123",
                             "id":"13","pubYear":"2024","abstractText":"<p>Summary.</p>"}],
                "total_hit_count":1,"retrieved_count":1,"rejected_count":0,
                "approved_artifact":{"sha256":"f"*64}}

    def fetch(self,pmc,version=None):
        self.fetches.append((pmc,version))
        if version is None:
            return {"status":"selection_required","available_versions":[1,2]}
        return {"status":"accepted"}

    def parent(self,pmc):
        return {"xml_artifact":{"sha256":sha(self.xml)},"version":2,"canonical_parent_url":"https://example.org/"}

    def read_artifact(self,record):
        return self.xml

    def close(self):
        pass


class TestRetrieval(unittest.TestCase):
    def make(self,xml):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        f=Fake(xml)
        return Retrieval(d.name,gateway_factory=lambda *_: f),f

    def test_only_search_returns_eligible_and_seal_checks_bytes(self):
        r,f=self.make(sample_xml([["Estimate","A","B"],["Mean","2.0","3.0"]]))
        with self.assertRaises(ValueError):
            r.open("PMC123")
        self.assertEqual(r.search("pairing")["hits"][0]["pmcid"],"PMC123")
        self.assertEqual(r.search("Pairing")["status"],"ok")
        self.assertEqual(len(f.queries),1)
        with self.assertRaises(ValueError):
            r.seal(["PMC123"])
        item=r.open("PMC123")
        self.assertEqual(item["status"],"ok")
        self.assertIn('["Mean", "2.0", "3.0"]',item["text"])
        self.assertIn("Some following text.",item["text"])
        self.assertNotIn("secret raw",item["text"])
        self.assertEqual(f.fetches,[("PMC123",None),("PMC123",2)])
        self.assertEqual(r.open("PMC123")["xml_sha256"],sha(f.xml))
        self.assertEqual(len(f.fetches),2)
        doc=r.seal(["PMC123"])
        self.assertTrue(doc.startswith("## [PMC123] "))
        m=json.loads((r.root/"source_manifest.json").read_text())
        self.assertEqual(m["bundle_sha256"],sha(doc.encode()))
        self.assertEqual(m["sources"][0]["xml_sha256"],sha(f.xml))
        with self.assertRaises(ValueError):
            r.search("another query")
        (r.root/"PMC123.txt").write_text("changed")
        with self.assertRaises(ValueError):
            r.seal(["PMC123"])

    def test_individual_table_and_doi_conflict_never_sealable(self):
        for xml,reason in [(sample_xml([["Patient ID","BMI"],["A17","22"]]), "possible_individual_table"),
                           (sample_xml([["Group","Mean"]],doi="10.0000/another"),"search_fulltext_doi_mismatch")]:
            with self.subTest(reason=reason):
                r,_=self.make(xml)
                r.search("pairing")
                self.assertEqual(r.open("PMC123")["reason"],reason)
                with self.assertRaises(ValueError):
                    r.seal(["PMC123"])

    def test_whole_block_projection_keeps_tables_and_marks_omissions(self):
        xml=sample_xml([["Description","Group n"],["One","6"]],"long example "*(ARTICLE_BYTES//5))
        doc,coverage=render(xml,{"pmcid":"PMC123","doi":"10.0000/foo"},1)
        self.assertLessEqual(len(doc.encode()),ARTICLE_BYTES)
        self.assertIn('["One", "6"]',doc)
        self.assertGreater(len(coverage["omitted_blocks"]),0)
        self.assertIn("excluded by the byte budget",doc)

    def test_query_budget_persists_across_instances(self):
        r,f=self.make(sample_xml([["group","mean"]]))
        for q in ["alpha","beta","gamma"]:
            r.search(q)
        resumed=Retrieval(r.root,gateway_factory=lambda *_: f)
        with self.assertRaises(ValueError):
            resumed.search("delta")
        self.assertEqual(len(f.queries),3)

    def test_missing_doi_requires_title_identity_and_rejects_conflicting_pmcid(self):
        xml=sample_xml([["group","mean"]])
        hit={"pmcid":"PMC123","doi":"","title":"Test <i>ARTICLE</i>."}
        text,coverage=render(xml,hit,2)
        self.assertIn(coverage["article_title"],text)
        with self.assertRaisesRegex(ValueError,"title_mismatch"):
            render(xml,{**hit,"title":"Another study"},2)
        wrong=xml.replace(b"<article-meta>",b"<article-meta><article-id pub-id-type='pmcid'>PMC321</article-id>")
        with self.assertRaisesRegex(ValueError,"pmcid_mismatch"):
            render(wrong,hit,2)


if __name__=="__main__":
    unittest.main()

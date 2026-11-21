"""Extract titles, methods, file labels and license from public primary articles.
Do not expose results or participant values while selecting frames.
"""
from pathlib import Path
import hashlib
import json
import sys

import requests
from lxml import etree

HERE = Path(__file__).resolve().parent
PRIVATE = HERE / "private"
PRIVATE.mkdir(exist_ok=True)
PLOS = "https://journals.plos.org/plosone/article/file"
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
XL = "{http://www.w3.org/1999/xlink}href"


def get(url, path, params):
    if not path.exists():
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        assert 0 < len(response.content) <= 20_000_000
        path.write_bytes(response.content)
    return path.read_bytes()


def words(node):
    return " ".join(" ".join(node.itertext()).split())


def titles():
    queries = {
        "diabetes_et": 'JOURNAL:"PLoS One" AND (TITLE_ABS:Ethiopia OR TITLE_ABS:Ethiopian) AND (TITLE:"type 2 diabetes" OR TITLE:"diabetes mellitus" OR TITLE:diabetic) AND (TITLE:lipid* OR TITLE:dyslipid* OR TITLE:"metabolic syndrome")',
        "community_et": 'JOURNAL:"PLoS One" AND (TITLE_ABS:Ethiopia OR TITLE_ABS:Ethiopian) AND (TITLE:community OR TITLE:"population-based" OR TITLE:"community-based") AND (TITLE:dyslipid* OR TITLE:"metabolic syndrome" OR TITLE:lipid*)'
    }
    out = {}
    for label, query in queries.items():
        payload = json.loads(get(API, PRIVATE / (label + "_index.json"),
                                {"query": query, "format": "json", "pageSize": 100, "resultType": "lite"}))
        rows = [{"doi": r.get("doi"), "title": r["title"], "year": r.get("pubYear")}
                for r in payload["resultList"]["result"] if r.get("doi")]
        rows.sort(key=lambda x: x["doi"])
        out[label] = rows
    return out


def describe(doi):
    tag = doi.rsplit(".", 1)[-1]
    path = PRIVATE / (tag + ".xml")
    raw = get(PLOS, path, {"id": doi, "type": "manuscript"})
    tree = etree.fromstring(raw)
    assert tree.xpath("string(//article-id[@pub-id-type='doi'])") == doi
    supplements = [{"id": t.get("id"), "type": t.xpath("string(.//media/@mimetype)"),
                    "href": t.get(XL) or t.xpath("string(.//media/@*[local-name()='href'])"),
                    "label": t.xpath("string(label)"), "caption_title": t.xpath("string(caption/title)")[:200]}
                   for t in tree.xpath("//supplementary-material[@id]")]
    methods = [s for s in tree.xpath("//body/sec") if any(w in s.xpath("string(title)").lower()
                                                         for w in ("method", "material", "patient and"))]
    paras = [words(p) for s in methods for p in s.xpath(".//p") if not p.xpath(".//table")]
    (PRIVATE / (tag + "_methods.txt")).write_text("\n\n".join(paras), encoding="utf8")
    return {"doi": doi, "title": tree.xpath("string(//article-title)")[:230],
            "license": tree.xpath("string(//permissions/license/@*[local-name()='href'])"),
            "methods_paragraphs": len(paras), "supplements": supplements,
            "article_bytes": len(raw), "article_sha256": hashlib.sha256(raw).hexdigest()}


if __name__ == "__main__":
    print(json.dumps(titles() if sys.argv[1] == "titles" else [describe(d) for d in sys.argv[1:]],
                     ensure_ascii=True, indent=2))

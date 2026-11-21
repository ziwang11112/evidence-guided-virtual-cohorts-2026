"""Inspect published methods and supporting-file descriptions without opening outcome tables."""
import hashlib
import json
from pathlib import Path
import requests
from lxml import etree

HERE = Path(__file__).resolve().parent
PRIVATE = HERE / "private"
PAPERS = {"mekelle":"10.1371/journal.pone.0243103", "workers":"10.1371/journal.pone.0291665",
          "gondar":"10.1371/journal.pone.0257710", "source":"10.1371/journal.pone.0223189"}
NS = "{http://www.w3.org/1999/xlink}href"

def fetch(url, path):
    if not path.exists():
        res = requests.get(url,timeout=45)
        res.raise_for_status()
        if len(res.content)>30_000_000:
            raise ValueError("Unexpectedly large public supplement")
        path.write_bytes(res.content)
    return path.read_bytes()

def words(node):
    return " ".join(" ".join(node.itertext()).split())

def inspect(label):
    doi=PAPERS[label]
    raw=fetch("https://journals.plos.org/plosone/article/file?type=manuscript&id="+doi, PRIVATE/(label+".xml"))
    tree=etree.fromstring(raw)
    if tree.xpath("string(//article-id[@pub-id-type='doi'])")!=doi:
        raise ValueError("Article identity mismatch")
    sups=[{"text":words(t)[:400],"file":t.get(NS)} for t in tree.xpath("//supplementary-material") if t.get("id")]
    print(label,doi, tree.xpath("string(//article-title)")[:180],sups)
    methods=[s for s in tree.xpath("//body/sec") if any(w in s.xpath("string(title)").lower() for w in ("method","material"))]
    paragraphs=[words(t) for s in methods for t in s.xpath(".//p") if t.find(".//table") is None]
    (PRIVATE/(label+".methods.txt")).write_text("\n\n".join(paragraphs),encoding="utf8")
    if label=="source":
        for t in tree.xpath("//table-wrap[contains(label,'Table 2')]"):
            print("SOURCE TABLE",words(t)[:8000])
    return {"doi":doi,"article_sha256":hashlib.sha256(raw).hexdigest(),"supplements":sups}

if __name__=="__main__":
    import sys
    for label in sys.argv[1:]:
        print(json.dumps(inspect(label),ensure_ascii=True))

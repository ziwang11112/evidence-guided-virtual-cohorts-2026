"""Retrieve only official metadata and data, without parsing outcome records."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json

BASE = Path(__file__).resolve().parent

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href")

def fetch(url, destination, kind):
    if destination.exists():
        raise RuntimeError(f"Refusing to overwrite {destination.name}")
    started = datetime.now(timezone.utc).isoformat()
    with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0 NHANES reproducibility"}), timeout=45) as response:
        data = response.read()
        resolved_url, content_type = response.url, response.headers.get("Content-Type", "")
    if kind == "xpt" and not data.startswith(b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"):
        raise RuntimeError(f"Not an XPT transport file: {url}")
    destination.write_bytes(data)
    return {"file": destination.relative_to(BASE).as_posix(), "requested_url": url,
            "resolved_url": resolved_url, "access_started_utc": started,
            "access_completed_utc": datetime.now(timezone.utc).isoformat(),
            "content_type": content_type, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(), "kind": kind}

def main():
    raw, doc = BASE / "raw", BASE / "documentation"
    raw.mkdir(exist_ok=True)
    doc.mkdir(exist_ok=True)
    records, requests = [], []
    for component, name in [("Laboratory", "HDL_H"), ("Examination", "BMX_H"), ("Demographics", "DEMO_H")]:
        index_url = f"https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component={component}&CycleBeginYear=2013"
        path = doc / f"index_{component.lower()}.html"
        records.append(fetch(index_url, path, "html_index"))
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8-sig"))
        for ext, kind, folder in [(".xpt", "xpt", raw), (".htm", "html_codebook", doc)]:
            urls = [urljoin(index_url, x) for x in parser.links if x.lower().endswith((name+ext).lower())]
            if not urls:
                raise RuntimeError(f"Official index did not link {name+ext}")
            requests.append((urls[0], folder / (name+ext), kind))
    requests += [
        ("https://wwwn.cdc.gov/nchs/data/nhanes/public/2013/labmethods/HDL_H_MET_COBAS.pdf", doc / "HDL_H_MET_COBAS.pdf", "pdf_method"),
        ("https://wwwn.cdc.gov/nchs/data/nhanes/public/2013/labmethods/HDL_H_MET_MODP.pdf", doc / "HDL_H_MET_MODP.pdf", "pdf_method"),
        ("https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx", doc / "varianceestimation.html", "html_guidance"),
        ("https://wwwn.cdc.gov/nchs/data/nhanes/analyticguidelines/11-16-analytic-guidelines.pdf", doc / "analytic_guidelines_2011_2016.pdf", "pdf_guidance")
    ]
    with ThreadPoolExecutor(max_workers=6) as pool:
        records.extend(pool.map(lambda x: fetch(*x), requests))
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(),
                "sources": sorted(records, key=lambda x: x["file"]),
                "note": "Fresh official-source retrieval; no source records parsed and no target summaries or association analyses performed"}
    (BASE / "source_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"downloaded_files": len(records), "xpt_files": [x["file"] for x in records if x["kind"] == "xpt"]}))

if __name__ == "__main__":
    main()

"""Download official NHANES public sources; never summarize target outcomes."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw"
DOC = BASE / "documentation"
RAW.mkdir(exist_ok=True)
DOC.mkdir(exist_ok=True)

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href")

def fetch(url, destination, kind):
    started = datetime.now(timezone.utc).isoformat()
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (NHANES research reproducibility)"})
    with urlopen(request, timeout=60) as response:
        data = response.read()
        resolved_url = response.url
        content_type = response.headers.get("Content-Type", "")
    if kind == "xpt" and not data.startswith(b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"):
        raise RuntimeError(f"Not an XPT transport file: {url}, content-type={content_type}")
    destination.write_bytes(data)
    return {"file": str(destination.relative_to(BASE)), "requested_url": url,
            "resolved_url": resolved_url, "access_started_utc": started,
            "access_completed_utc": datetime.now(timezone.utc).isoformat(),
            "bytes": len(data), "content_type": content_type,
            "sha256": hashlib.sha256(data).hexdigest(), "kind": kind}

def main():
    records = []
    component_files = {
        "Laboratory": ["INS_J", "FASTQX_J"],
        "Examination": ["BMX_J"],
        "Demographics": ["DEMO_J"],
        "Questionnaire": ["DIQ_J"],
    }
    requests = []
    for component, names in component_files.items():
        index_url = f"https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component={component}&CycleBeginYear=2017"
        path = DOC / f"index_{component.lower()}.html"
        records.append(fetch(index_url, path, "html_index"))
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8-sig"))
        for name in names:
            for extension, kind, folder in [(".xpt", "xpt", RAW), (".htm", "html_codebook", DOC)]:
                candidates = [urljoin(index_url, href) for href in parser.links if href.lower().endswith((name + extension).lower())]
                if not candidates:
                    raise RuntimeError(f"Official index did not link {name + extension}")
                requests.append((candidates[0], folder / (name + extension), kind))
    requests += [
        ("https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx", DOC / "survey_weighting.html", "html_guidance"),
        ("https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx", DOC / "survey_variance_estimation.html", "html_guidance"),
        ("https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/labmethods/INS-J-MET-508.pdf", DOC / "INS-J-MET-508.pdf", "lab_method_pdf"),
    ]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for record in pool.map(lambda args: fetch(*args), requests):
            records.append(record)
    records.sort(key=lambda x: x["file"])
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "sources": records,
                "note": "Only official CDC/NCHS sources. Files retrieved independently for this pilot; source dataset is not inferred from prior workspace pilots. No insulin values or relationship estimates were printed or calculated by this acquisition script."}
    (BASE / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"downloaded_files": len(records), "xpt_files": [x["file"] for x in records if x["kind"] == "xpt"], "manifest": str(BASE / "source_manifest.json")}, indent=2))

if __name__ == "__main__":
    main()

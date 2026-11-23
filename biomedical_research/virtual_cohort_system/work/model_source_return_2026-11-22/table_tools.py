"""Read aggregate tables from articles already selected by the search agent."""
from contextlib import closing
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import parse_qs, unquote, urlsplit

from filelock import FileLock
from lxml import etree
from PIL import Image
import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "search_to_model_2026-11-22"))
from retrieve import gateway, immutable, individual_rows, sha, string, table_rows

MAX_BYTES = 4_000_000
MAX_PIXELS = 16_000_000
MIMES = {"JPEG":"image/jpeg", "PNG":"image/png"}
SUPPLEMENT = {"supplementary-material", "inline-supplementary-material", "sub-article"}


def _name(element):
    return etree.QName(element).localname if isinstance(element.tag,str) else ""


def _first_text(element, key):
    return " ".join(string(e) for e in element if _name(e) == key)


def _filename(href):
    if not href or any(c in href for c in ("/", "\\", ":", "#", "?", "%")):
        return None
    return href


def _media_url(href, approved):
    name = _filename(href)
    if not name:
        return None
    names = [file for file in approved if file == name or
             ("." not in PurePosixPath(name).name and PurePosixPath(file).stem == name)]
    valid = [fn for fn in names if PurePosixPath(fn).suffix.lower() in {".jpg",".jpeg",".png"}]
    return approved[valid[0]] if len(valid) == 1 else None


def _download(url):
    if not gateway.allowed_url(url) or urlsplit(url).hostname != "pmc-oa-opendata.s3.amazonaws.com":
        raise ValueError("Unsupported original-article media URL")
    with requests.get(url, timeout=(8,30), allow_redirects=False, stream=True,
                      headers={"Accept":"image/jpeg, image/png, application/octet-stream",
                               "Accept-Encoding":"identity"}) as response:
        if response.status_code != 200 or response.url != url:
            raise ValueError("Original table image unavailable, HTTP " + str(response.status_code))
        content_type = response.headers.get("Content-Type","").split(";")[0].strip().lower()
        if content_type not in {*MIMES.values(),"application/octet-stream","binary/octet-stream"}:
            raise ValueError("Unexpected image content type")
        size = response.headers.get("Content-Length")
        if size is not None and (not size.isdigit() or not 0 < int(size) <= MAX_BYTES):
            raise ValueError("Invalid table image size")
        buf = bytearray()
        for block in response.iter_content(65536):
            buf.extend(block)
            if len(buf) > MAX_BYTES:
                raise ValueError("Table image exceeds byte limit")
        if not buf or (size is not None and len(buf) != int(size)):
            raise ValueError("Empty or partial table image")
        return bytes(buf),content_type


def _verify_image(data, content_type, url):
    if len(data) > MAX_BYTES:
        raise ValueError("Table image exceeds byte limit")
    expected = parse_qs(urlsplit(url).query)["md5"][0].lower()
    if hashlib.md5(data).hexdigest() != expected:
        raise ValueError("Image differs from the versioned article manifest")
    with Image.open(BytesIO(data)) as image:
        mime = MIMES.get(image.format)
        if (not mime or content_type not in (mime,"application/octet-stream","binary/octet-stream")
                or image.width * image.height > MAX_PIXELS or min(image.size) <= 0):
            raise ValueError("Invalid table image format or dimensions")
        dims = list(image.size)
        image.verify()
    return mime,dims


class TableTools:
    """Discover tables on all stored JATS branches; expose images only on explicit choice."""
    def __init__(self, retrieval_root, private_root, *, session_factory=None, download=None):
        root = Path(retrieval_root).resolve()
        self.private = Path(private_root).resolve()
        self.private.mkdir(parents=True,exist_ok=True)
        self.download = _download if download is None else download
        selected = json.loads((root/"source_manifest.json").read_bytes())
        if (sha((root/"selected_sources.txt").read_bytes()) != selected["bundle_sha256"] or
                [s["pmcid"] for s in selected["sources"]] != selected["ids"] or
                len(selected["ids"]) != len(set(selected["ids"])) or
                sha((root/"gateway_config.json").read_bytes()) != selected["config_sha256"]):
            raise ValueError("Source selection binding mismatch")
        self.entries = {}
        factory = session_factory or gateway.Session
        with closing(factory(root/"gateway",root/"gateway_config.json")) as session:
            for source in selected["sources"]:
                pmcid = source["pmcid"]
                parent = session.parent(pmcid)
                xml = session.read_artifact(parent["xml_artifact"])
                manifest = json.loads(session.read_artifact(parent["manifest_artifact"]))
                if (sha(xml) != source["xml_sha256"] or parent["version"] != source["version"] or
                        manifest["pmcid"] != pmcid or str(manifest["version"]) != str(source["version"])):
                    raise ValueError("Parent version or XML binding mismatch")
                urls = {}
                for locator in manifest.get("media_urls") or []:
                    url = session.object_url(locator,pmcid,source["version"])
                    filename = PurePosixPath(unquote(urlsplit(url).path)).name
                    if filename in urls:
                        raise ValueError("Ambiguous article media filename")
                    urls[filename] = url
                self._register(pmcid,source["version"],xml,urls)

    def _register(self, pmcid, version, xml, urls):
        article = etree.fromstring(xml,etree.XMLParser(resolve_entities=False,no_network=True))
        for number,table in enumerate(article.xpath(".//*[local-name()='table-wrap']"),1):
            if any(_name(e) in SUPPLEMENT or e.get("sec-type","").lower().startswith("supplement")
                   for e in table.iterancestors()):
                continue
            locator = table.get("id") or f"table{number}"
            key = f"{pmcid}:{locator}"
            if key in self.entries:
                raise ValueError("Duplicate table identifier in the source article")
            label,caption,notes = [_first_text(table,k) for k in ("label","caption","table-wrap-foot")]
            if re.search(r"^(?:supplement|s\d|table\s+s\d)",label,re.I):
                continue
            rows = table_rows(table)
            entry = {"id":key,"pmcid":pmcid,"version":version,"label":label,"caption":caption,
                     "footnotes":notes,"kind":"unavailable","status":"unavailable","source_xml_sha256":sha(xml)}
            if individual_rows(caption,rows) or re.search(
                r"\b(?:individual[ -]level|per[ -](?:patient|subject|participant)|each (?:patient|participant|subject)(?:'s)? (?:data|readings|values)|"
                r"(?:patients?|participants?|subjects?) (?:one by one|by (?:name|id)))\b",caption,re.I):
                entry["reason"] = "possible_individual_records"
            elif rows:
                content = "\n".join([label,caption] + [json.dumps(r,ensure_ascii=False) for r in rows] + [notes])
                if len(content.encode()) > 60_000:
                    entry["reason"]="table_text_exceeds_budget"
                else:
                    entry.update(kind="text",status="available",text=content)
            else:
                graphics = table.xpath("./*[local-name()='graphic'] | "
                                       "./*[local-name()='alternatives']/*[local-name()='graphic']")
                links = {_media_url(e.get("{http://www.w3.org/1999/xlink}href") or e.get("href"),urls)
                         for e in graphics}
                links.discard(None)
                if len(links)==1:
                    entry.update(kind="image",status="available",url=links.pop())
                else:
                    entry["reason"]="no_unique_manifest_table_image"
            self.entries[key]=entry

    def index(self):
        return [{k:v for k,v in e.items() if k in {"id","pmcid","version","label","caption","kind","status","reason"}}
                for e in self.entries.values()]

    def get(self, table_id):
        if not isinstance(table_id,str) or table_id not in self.entries:
            raise ValueError("Unknown table identifier")
        entry = self.entries[table_id].copy()
        if entry["status"] != "available":
            raise ValueError("Unavailable table: " + entry["reason"])
        if entry["kind"]=="text":
            data=entry["text"].encode()
            mime="text/plain"
            base=sha(data)+".txt"
        else:
            url=entry["url"]
            filename=PurePosixPath(unquote(urlsplit(url).path)).name
            base=sha(url.encode())+PurePosixPath(filename).suffix.lower()
        path=self.private/base
        with FileLock(str(path)+".lock",timeout=10):
            if entry["kind"]=="image":
                data,declared = (path.read_bytes(),"application/octet-stream") if path.exists() else self.download(url)
                mime,entry["dimensions"] = _verify_image(data,declared,url)
            immutable(path,data)
            entry.update(path=str(path),mime=mime,sha256=sha(data),n_bytes=len(data))
        return entry

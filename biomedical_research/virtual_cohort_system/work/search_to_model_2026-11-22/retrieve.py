"""Search public Europe PMC and bind selected, versioned articles to the constructor."""
from contextlib import closing
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import unicodedata

from filelock import FileLock
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from cohort_harness._vendor import literature_gateway as gateway

ARTICLE_BYTES = 23_800
BUNDLE_BYTES = 48_000
POLICY = "public-aggregate-jats-v1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      indent=2).encode("utf8") + b"\n"


def immutable(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Existing retrieval artifact differs: " + path.name)
        return
    with path.open("xb") as handle:
        handle.write(data)


def normal(s):
    return " ".join(s.split())


def string(el):
    return normal("".join(el.itertext()))


def tag(el):
    return etree.QName(el).localname if isinstance(el.tag, str) else ""


def doi(s):
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", str(s or "").strip(),
                  flags=re.I).casefold()


def comparable_title(s):
    without_markup=re.sub(r"<[^>]+>", "", html.unescape(str(s or "")))
    return "".join(c for c in unicodedata.normalize("NFKC", without_markup).casefold() if c.isalnum())


def case_report(hit):
    types = hit.get("pubTypeList") or {}
    return bool(re.search(r"\bcase reports?\b", str(types) + " " + str(hit.get("title", "")), re.I))


def table_rows(el):
    return [[string(cell) for cell in row if tag(cell) in {"td","th"}]
            for row in el.xpath(".//*[local-name()='tr']")]


def individual_rows(caption, rows):
    if re.search(r"\b(?:individual (?:patient|participant|subject)(?:-level)? (?:records|profiles|values|results|measurements)|(?:patient|participant|subject)[ -]level (?:measurements|data)|(?:data|measurements) (?:for|of) (?:each|individual) (?:patient|participant|subject))\b", caption, re.I):
        return True
    if not rows:
        return False
    labels = [cell for row in rows[:2] for cell in row]
    if any(re.fullmatch(r"(?:patient|participant|subject|case|individual|record|volunteer)\s*(?:id(?:entifier)?|no\.?|number|#)?|identifier|ID", cell, re.I) for cell in labels):
        return True
    if any(re.search(r"\b(?:patient|participant|subject|case)\s*(?:#|no\.?\s*)?\d+\b", cell, re.I)
           for row in rows for cell in row):
        return True
    # Unlabelled enumerated observations can also appear without the word 'patient'.
    first = [row[0] for row in rows[1:] if row]
    return len(first) >= 4 and first == [str(i) for i in range(1,len(first)+1)]


def render(xml, hit, version):
    tree = etree.fromstring(xml, parser=etree.XMLParser(resolve_entities=False,no_network=True))
    meta = tree.xpath("./*[local-name()='front']/*[local-name()='article-meta']")[0]
    ids = {doi(string(e)) for e in meta.xpath("./*[local-name()='article-id'][@pub-id-type='doi']")}
    if hit["doi"] and doi(hit["doi"]) not in ids:
        raise ValueError("search_fulltext_doi_mismatch")
    pmc_ids={string(e).upper() for e in meta.xpath("./*[local-name()='article-id'][@pub-id-type='pmc' or @pub-id-type='pmcid']")}
    digits=hit["pmcid"][3:]
    if pmc_ids - {hit["pmcid"],digits,f"{hit['pmcid']}.{version}",f"{digits}.{version}"}:
        raise ValueError("search_fulltext_pmcid_mismatch")
    title = normal(" ".join(string(e) for e in meta.xpath(".//*[local-name()='article-title']")))
    if not title:
        raise ValueError("missing_article_title")
    if not hit["doi"] and comparable_title(title)!=comparable_title(hit.get("title")):
        raise ValueError("search_fulltext_title_mismatch")
    if "case-report" in (tree.get("article-type") or ""):
        raise ValueError("individual_case_report")
    # Do not flatten embedded media, captions or supplementary material into narrative text.
    for e in tree.xpath(".//*[local-name()='supplementary-material' or local-name()='inline-supplementary-material' or local-name()='graphic' or local-name()='inline-graphic' or local-name()='media']"):
        parent = e.getparent()
        if parent is not None:
            label = etree.Element("omitted")
            label.text = "[linked material unavailable]"
            label.tail = e.tail
            parent.replace(e, label)
    blocks = []
    def add(kind, txt):
        if txt:
            blocks.append((kind,txt))
    for e in meta.xpath("./*[local-name()='abstract']"):
        add("abstract",string(e))
    def visit(e):
        k = tag(e)
        if k == "table-wrap":
            caption = normal(" ".join(string(v) for v in e if tag(v) in {"label","caption"}))
            rows = table_rows(e)
            if individual_rows(caption, rows):
                raise ValueError("possible_individual_table")
            table = [caption] + [json.dumps(r, ensure_ascii=False) for r in rows if r]
            table.extend(string(v) for v in e if tag(v) == "table-wrap-foot")
            if not rows:
                table.append("[table cells unavailable]")
            add("table","\n".join(table))
        elif k == "fig":
            add("figure_caption"," ".join(string(v) for v in e if tag(v) in {"label","caption"}))
        elif k in {"p","title","disp-formula"}:
            nested=e.xpath(".//*[local-name()='fig' or local-name()='table-wrap']")
            if nested:
                for item in nested:
                    visit(item)
                    parent=item.getparent()
                    replacement=etree.Element("moved")
                    replacement.text="[separately rendered]"
                    replacement.tail=item.tail
                    parent.replace(item,replacement)
            s = string(e)
            if len(set(re.findall(r"\b(?:patient|participant|subject|case)\s*(?:no\.?\s*|#)?(\d+)\b",s,re.I))) >= 2:
                raise ValueError("possible_individual_narrative")
            add(k,s)
        else:
            for child in e:
                visit(child)
    body = tree.xpath("./*[local-name()='body']")
    if len(body)!=1:
        raise ValueError("missing_scientific_body")
    visit(body[0])
    header = (f"## [{hit['pmcid']}] {title}\nDOI: {hit['doi'] or ', '.join(sorted(ids)) or 'unavailable'}"
              f" | PMC version {version}\nScope: aggregate article text and table cells; no figures, "
              "supplement files or reference list. Table cell arrays preserve row order.\n\n")
    # Keep whole tables, their notes, figure captions and abstract. Fit complete
    # narrative blocks in article order; identify all omitted blocks in the manifest.
    must = {i for i,(kind,_) in enumerate(blocks) if kind in {"abstract","table","figure_caption"}}
    remaining = ARTICLE_BYTES-len(header.encode())-240
    for i in must:
        remaining -= len((blocks[i][1]+"\n\n").encode())
    if remaining < 0:
        raise ValueError("article_summary_tables_exceed_byte_budget")
    keep=set(must)
    for i,(_,s) in enumerate(blocks):
        size=len((s+"\n\n").encode())
        if i not in keep and size<=remaining:
            remaining-=size
            keep.add(i)
    omitted=[{"index":i,"kind":kind,"bytes":len(s.encode()),"sha256":sha(s.encode())}
             for i,(kind,s) in enumerate(blocks) if i not in keep]
    coverage=f"Text coverage: {len(keep)}/{len(blocks)} blocks; {len(omitted)} excluded by the byte budget.\n\n"
    out=header+coverage+"\n\n".join(blocks[i][1] for i in sorted(keep))+"\n"
    if len(out.encode()) > ARTICLE_BYTES:
        raise ValueError("article_projection_over_budget")
    return out, {"blocks_total":len(blocks),"blocks_kept":len(keep),"tables":sum(k=="table" for k,_ in blocks),
                 "omitted_blocks":omitted,"article_dois":sorted(ids),"article_title":title}


class Retrieval:
    """One resumable, file-locked read-only literature session, held in a private directory."""
    def __init__(self, root, *, excluded_aliases=(), gateway_factory=None):
        self.root=Path(root).resolve()
        self.root.mkdir(parents=True,exist_ok=True)
        self.factory=gateway_factory or gateway.Session
        self.lock=FileLock(str(self.root/"retrieval.lock"), timeout=0)
        self.config=self.root/"gateway_config.json"
        config={"schema_version":1, "budgets":{"queries":3,"downloads":3,"auxiliary_requests":30},
                "limits":{"response_bytes":5_000_000,"timeout_seconds":25,"search_page_size":8,
                          "table_cells":100000},"exclusions":{"compact_aliases":list(excluded_aliases),"regexes":[]}}
        with self.lock:
            immutable(self.config,encoded(config))
            immutable(self.root/"policy_version.txt",(POLICY+"\n"+sha(Path(__file__).read_bytes())).encode())

    def _load(self):
        p=self.root/"retrieval_state.json"
        return json.loads(p.read_text(encoding="utf8")) if p.exists() else {"queries":{},"opens":{},"hits":{}}

    def _save(self,state):
        p=self.root/"retrieval_state.tmp"
        p.write_bytes(encoded(state))
        p.replace(self.root/"retrieval_state.json")

    def _session(self):
        return closing(self.factory(self.root/"gateway",self.config))

    def search(self,query):
        if not isinstance(query,str) or not query.strip() or len(query)>1650:
            raise ValueError("Supply a short Europe PMC query")
        key=normal(query).casefold()
        with self.lock:
            st=self._load()
            if key in st["queries"]:
                return st["queries"][key]
            if len(st["queries"])>=3 or (self.root/"source_manifest.json").exists():
                raise ValueError("Search budget exhausted or selection already sealed")
            st["queries"][key]={"status":"unsettled","query":query,"hits":[]}
            self._save(st)
            try:
                with self._session() as s:
                    result=s.search(f"({query}) AND OPEN_ACCESS:Y AND IN_PMC:Y",8)
                hits=[]
                for r in result["accepted"]:
                    pmc=r.get("pmcid")
                    if not isinstance(pmc,str) or not re.fullmatch(r"PMC[1-9]\d*",pmc) or case_report(r):
                        continue
                    abstract=normal(re.sub(r"<[^>]+>", " ", r.get("abstractText") or ""))
                    hit={"pmcid":pmc,"provider_id":r.get("id"),"doi":doi(r.get("doi")),
                         "title":r.get("title"),"journal":r.get("journalTitle") or
                         ((r.get("journalInfo") or {}).get("journal") or {}).get("title"),
                         "year":r.get("pubYear"),"abstract_preview":abstract[:720],
                         "abstract_preview_truncated":len(abstract)>720,"metadata_sha256":sha(encoded(r))}
                    hits.append(hit)
                    st["hits"].setdefault(pmc,hit)
                answer={"status":"ok","query":query,"hits":hits,"total_hits":result.get("total_hit_count"),
                        "records_returned":result.get("retrieved_count"),"gateway_rejections":result.get("rejected_count"),
                        "gateway_projection_sha256":result.get("approved_artifact",{}).get("sha256")}
            except gateway.GatewayError as exc:
                answer={"status":"unavailable","query":query,"reason":exc.reason,"hits":[]}
            st["queries"][key]=answer
            self._save(st)
            return answer

    def _article(self,record):
        raw=(self.root/(record["pmcid"]+".txt")).read_bytes()
        if sha(raw)!=record["text_sha256"]:
            raise ValueError("Approved source text changed")
        return raw.decode("utf8")

    def open(self,pmcid):
        with self.lock:
            st=self._load()
            if not isinstance(pmcid,str) or pmcid not in st["hits"]:
                raise ValueError("PMCID was not returned by this session")
            if pmcid in st["opens"]:
                data=st["opens"][pmcid]
                return {**data,"text":self._article(data)} if data["status"]=="ok" else data
            if len(st["opens"])>=3 or (self.root/"source_manifest.json").exists():
                raise ValueError("Open budget exhausted or selection already sealed")
            hit=st["hits"][pmcid]
            st["opens"][pmcid]={"status":"unsettled","pmcid":pmcid}
            self._save(st)
            try:
                with self._session() as s:
                    result=s.fetch(pmcid)
                    if result["status"]=="selection_required":
                        versions=result.get("available_versions")
                        if not versions or any(type(v) is not int or v<1 for v in versions):
                            raise ValueError("invalid_article_version_listing")
                        result=s.fetch(pmcid,max(versions))
                    if result["status"]!="accepted":
                        raise ValueError("unaccepted_fulltext")
                    parent=s.parent(pmcid)
                    xml=s.read_artifact(parent["xml_artifact"])
                    if sha(xml)!=parent["xml_artifact"]["sha256"]:
                        raise ValueError("source_xml_changed")
                    version=parent["version"]
                    text,coverage=render(xml,hit,version)
                data={"status":"ok","pmcid":pmcid,"doi":hit["doi"] or next(iter(coverage["article_dois"]),None),
                      "version":version,"url":parent["canonical_parent_url"],"xml_sha256":sha(xml),
                      "metadata_sha256":hit["metadata_sha256"],"text_sha256":sha(text.encode()),
                      "text_bytes":len(text.encode()),"coverage":coverage}
                immutable(self.root/(pmcid+".txt"),text.encode())
            except (gateway.GatewayError,ValueError) as exc:
                data={"status":"unavailable","pmcid":pmcid,"reason":getattr(exc,"reason",str(exc))}
            st["opens"][pmcid]=data
            self._save(st)
            return {**data,"text":self._article(data)} if data["status"]=="ok" else data

    def seal(self,selected):
        if (not isinstance(selected,list) or not 1<=len(selected)<=2 or
                any(not isinstance(p,str) for p in selected) or len(set(selected))!=len(selected)):
            raise ValueError("Select one or two distinct opened PMCIDs")
        with self.lock:
            st=self._load()
            if any(st["opens"].get(p,{}).get("status")!="ok" for p in selected):
                raise ValueError("Only successfully opened articles may enter the design")
            articles=[st["opens"][p] for p in selected]
            bundle="\n".join(self._article(doc) for doc in articles)
            if len(bundle.encode())>BUNDLE_BYTES:
                raise ValueError("Selected source material exceeds budget")
            manifest={"policy":POLICY,"ids":selected,"sources":articles,"bundle_sha256":sha(bundle.encode()),
                      "bundle_bytes":len(bundle.encode()),"config_sha256":sha(self.config.read_bytes())}
            immutable(self.root/"selected_sources.txt",bundle.encode())
            immutable(self.root/"source_manifest.json",encoded(manifest))
            return bundle

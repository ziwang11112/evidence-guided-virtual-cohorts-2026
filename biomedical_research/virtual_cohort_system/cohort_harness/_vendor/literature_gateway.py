"""Session-scoped publication gateway. Only approved content is displayed or saved.

This is a conservative procedural contamination screen, not an OS sandbox or a
guarantee that all target-derived information can be identified by text aliases.
No case data, outcome values, or scientific model parameters are required.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import socket
import sys
import time
import unicodedata
import warnings
import zipfile
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import xml.etree.ElementTree as ET

API = "https://www.ebi.ac.uk/europepmc/webservices/rest"
CLOUD = "https://pmc-oa-opendata.s3.amazonaws.com"
NOTICE = "Screened retrieved text only; aliases cannot establish absence of all target-derived evidence. Session separation is procedural, not an OS sandbox."
FORMATS = {".xml": "xml", ".nxml": "xml", ".csv": "csv", ".tsv": "tsv", ".txt": "text", ".text": "text", ".html": "html", ".htm": "html", ".xhtml": "html", ".xlsx": "xlsx"}
MEDIA_TYPES = {
    "json": {"application/json", "text/json", "application/octet-stream"},
    "xml": {"application/xml", "text/xml", "application/octet-stream"},
    "csv": {"text/csv", "text/plain", "application/csv", "application/octet-stream"},
    "tsv": {"text/tab-separated-values", "text/plain", "application/octet-stream"},
    "text": {"text/plain", "application/octet-stream"},
    "html": {"text/html", "application/xhtml+xml", "text/plain", "application/octet-stream"},
    "xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/octet-stream", "application/zip"},
}
# The documented PMC S3 distribution serves JSON and article objects using
# binary/octet-stream. Content parsers and manifest checks remain mandatory.
for _accepted_types in MEDIA_TYPES.values():
    _accepted_types.add("binary/octet-stream")


class GatewayError(Exception):
    def __init__(self, reason: str, content_sha256: str | None = None):
        self.reason = reason
        self.content_sha256 = content_sha256
        super().__init__(reason)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False).encode("ascii")


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def pmcid(value: str) -> str:
    value = value.upper()
    if not re.fullmatch(r"PMC[1-9][0-9]{0,11}", value):
        raise GatewayError("invalid_pmcid")
    return value


def decode_text(raw: bytes) -> str:
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeError:
        raise GatewayError("unsupported_or_invalid_text_encoding", digest(raw)) from None
    if any(ord(c) < 32 and c not in "\t\r\n" for c in text):
        raise GatewayError("binary_or_control_characters", digest(raw))
    return text


def compact(text: str) -> str:
    text = unicodedata.normalize("NFKC", html.unescape(text)).casefold()
    text = re.sub(r"<[^>]*>", "", text)
    return "".join(c for c in text if c.isalnum())


class Screen:
    def __init__(self, configuration: dict):
        try:
            rules = configuration["exclusions"]
            aliases = rules["compact_aliases"]
            regexes = rules["regexes"]
            if not isinstance(aliases, list) or not all(isinstance(x, str) and compact(x) for x in aliases):
                raise ValueError()
            if not isinstance(regexes, list) or not all(isinstance(x, str) for x in regexes):
                raise ValueError()
            self.aliases = [compact(x) for x in aliases]
            self.regexes = [re.compile(x, re.IGNORECASE) for x in regexes]
        except (KeyError, TypeError, ValueError, re.error):
            raise GatewayError("invalid_screen_configuration") from None

    def reason(self, text: str) -> str | None:
        # Decode entities, URL encodings and Unicode format characters as well
        # as HTML split tags. Both raw and decoded variants are screened.
        variants = [text, unquote(text), html.unescape(text)]
        for variant in variants:
            normalized = unicodedata.normalize("NFKC", variant).casefold()
            normalized = "".join(c for c in normalized if unicodedata.category(c) != "Cf")
            flattened = compact(normalized)
            if any(alias in flattened for alias in self.aliases):
                return "excluded_study_alias"
            if any(pattern.search(normalized) for pattern in self.regexes):
                return "excluded_configured_pattern"
        return None

    def check(self, text: str, raw: bytes | None = None):
        reason = self.reason(text)
        if reason:
            raise GatewayError(reason, digest(raw if raw is not None else text.encode("utf-8")))

    def json(self, value, raw: bytes | None = None):
        self.check(json.dumps(value, ensure_ascii=False, allow_nan=False), raw)


def parse_json(raw: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError()
            result[key] = value
        return result
    try:
        return json.loads(decode_text(raw), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, TypeError, RecursionError):
        raise GatewayError("invalid_json", digest(raw)) from None


def local_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_xml(raw: bytes, screen: Screen):
    text = decode_text(raw)
    screen.check(text, raw)
    # Standard external JATS DTD declarations are allowed but never fetched by
    # ElementTree. Entity declarations and internal subsets are rejected.
    if re.search(r"<!ENTITY|<!DOCTYPE[^>]*\[", text, re.IGNORECASE):
        raise GatewayError("xml_entities_or_internal_subset", digest(raw))
    try:
        root = ET.fromstring(text)
    except (ET.ParseError, ValueError, RecursionError):
        raise GatewayError("invalid_or_partial_xml", digest(raw)) from None
    all_text = "\n".join(t.strip() for t in root.itertext() if t.strip())
    screen.check(all_text, raw)
    if not all_text:
        raise GatewayError("empty_text", digest(raw))
    return root, all_text


class StrictTextHTML(HTMLParser):
    VOID = {"area", "base", "br", "col", "hr", "input", "link", "meta", "param", "source", "track", "wbr"}
    UNSUPPORTED = {"script", "iframe", "frame", "object", "embed", "img", "svg", "canvas", "audio", "video", "math"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.pieces = []

    def handle_starttag(self, tag, attrs):
        if tag in self.UNSUPPORTED:
            raise GatewayError("html_embedded_or_active_content_unsupported")
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        if tag in self.UNSUPPORTED:
            raise GatewayError("html_embedded_or_active_content_unsupported")

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise GatewayError("invalid_or_partial_html")

    def handle_data(self, data):
        self.pieces.append(data)

    def unknown_decl(self, data):
        raise GatewayError("unsupported_html_declaration")


def parse_xlsx(raw: bytes, screen: Screen, max_cells: int) -> dict:
    """Inspect every archive member in memory before invoking openpyxl.

    No extraction, macro execution, formula evaluation or external retrieval.
    Reject non-XML payloads, embedded media, links, encryption, unsafe names,
    duplicate entries and oversized archives rather than partially parsing.
    """
    try:
        import openpyxl
    except ImportError:
        raise GatewayError("xlsx_dependency_unavailable", digest(raw)) from None
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            if len(entries) > 2000 or sum(i.file_size for i in entries) > 64 * 1024 * 1024:
                raise GatewayError("xlsx_archive_size_limit")
            names = set()
            for entry in entries:
                name = entry.filename
                if name in names or name.startswith(("/", "\\")) or "\\" in name or ":" in name or any(part in {".", ".."} for part in name.split("/")) or any(ord(c) < 32 for c in name) or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise GatewayError("unsafe_xlsx_archive_member")
                names.add(name)
                screen.check(name, raw)
                if entry.is_dir():
                    continue
                if entry.flag_bits & 1 or entry.file_size > 16 * 1024 * 1024 or entry.file_size > max(1, entry.compress_size) * 1000:
                    raise GatewayError("xlsx_encryption_or_expansion_limit")
                if not name.lower().endswith((".xml", ".rels", ".vml")):
                    raise GatewayError("xlsx_nontext_member_unsupported")
                member = archive.read(entry)
                root, _ = parse_xml_allow_empty(member, screen)
                for element in root.iter():
                    if local_tag(element.tag) == "Relationship" and element.attrib.get("TargetMode", "").casefold() == "external":
                        raise GatewayError("xlsx_external_relationship_unsupported")
            if not {"[Content_Types].xml", "xl/workbook.xml"}.issubset(names):
                raise GatewayError("invalid_xlsx_package")
        with warnings.catch_warnings(record=True) as notices:
            warnings.simplefilter("always")
            formula_book = openpyxl.load_workbook(io.BytesIO(raw), data_only=False, read_only=False, keep_links=False)
            cached_book = openpyxl.load_workbook(io.BytesIO(raw), data_only=True, read_only=False, keep_links=False)
        if notices:
            raise GatewayError("xlsx_parser_warning_incomplete_support")
        sheets, count = [], 0
        for sheet in formula_book.worksheets:
            if sheet.max_row * sheet.max_column > max_cells:
                raise GatewayError("table_cell_limit")
            cells = []
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value is None and cell.comment is None:
                        continue
                    count += 1
                    if count > max_cells:
                        raise GatewayError("table_cell_limit")
                    value = cell.value
                    # Preserve strings/numbers/booleans and ISO-render dates.
                    if value is not None and not isinstance(value, (str, int, float, bool)):
                        if hasattr(value, "isoformat"):
                            value = value.isoformat()
                        else:
                            raise GatewayError("xlsx_unsupported_cell_type")
                    record = {"cell": cell.coordinate, "value": value,
                              "row_hidden": bool(sheet.row_dimensions[cell.row].hidden),
                              "column_hidden": bool(sheet.column_dimensions[cell.column_letter].hidden)}
                    if cell.comment:
                        record["comment"] = cell.comment.text
                    if cell.data_type == "f":
                        cached = cached_book[sheet.title][cell.coordinate].value
                        if cached is not None and not isinstance(cached, (str, int, float, bool)):
                            cached = cached.isoformat() if hasattr(cached, "isoformat") else str(cached)
                        record.update(formula=value, cached_value=cached, cached_value_missing=cached is None, formula_evaluated=False)
                    cells.append(record)
            sheets.append({"sheet": sheet.title, "state": sheet.sheet_state, "cells": cells})
        formula_book.close()
        cached_book.close()
        if count == 0:
            raise GatewayError("empty_text")
        result = {"format": "xlsx", "nonempty_cells": count, "sheets": sheets,
                  "formula_policy": "Formula text and any existing cached value retained; formulas are never evaluated. Missing caches are explicitly flagged.",
                  "package_screening": "Every XML/rels member and filename screened, including hidden sheets and package metadata; nontext payloads rejected."}
        screen.json(result, raw)
        return result
    except GatewayError as error:
        raise GatewayError(error.reason, digest(raw)) from None
    except Exception:
        raise GatewayError("invalid_or_unsupported_xlsx", digest(raw)) from None


def parse_xml_allow_empty(raw: bytes, screen: Screen):
    # OOXML style and relationship members can legitimately contain attributes
    # only. They still undergo complete raw XML and attribute screening.
    try:
        return parse_xml(raw, screen)
    except GatewayError as error:
        if error.reason != "empty_text":
            raise
        return ET.fromstring(decode_text(raw)), ""


def parse_supplement(raw: bytes, kind: str, screen: Screen, max_cells: int) -> dict:
    if kind == "xlsx":
        return parse_xlsx(raw, screen, max_cells)
    text = decode_text(raw)
    screen.check(text, raw)
    if kind == "xml":
        root, rendered = parse_xml(raw, screen)
        # An XML supplement containing binary/visual payload cannot be fully
        # screened with a text parser. External hyperlinks alone are metadata.
        if any(local_tag(e.tag).casefold() in {"binary", "binary-data", "graphic", "inline-graphic", "svg", "object", "embed"} for e in root.iter()):
            raise GatewayError("xml_nontext_payload_unsupported", digest(raw))
        return {"text": rendered, "format": kind}
    if kind in {"csv", "tsv"}:
        try:
            rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="," if kind == "csv" else "\t", strict=True))
        except (csv.Error, ValueError):
            raise GatewayError("invalid_or_partial_delimited_text", digest(raw)) from None
        if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
            raise GatewayError("empty_or_ragged_table", digest(raw))
        if sum(map(len, rows)) > max_cells:
            raise GatewayError("table_cell_limit", digest(raw))
        screen.json(rows, raw)
        return {"text": text, "format": kind, "rows": len(rows), "columns": len(rows[0])}
    if kind == "html":
        parser = StrictTextHTML()
        try:
            parser.feed(text)
            parser.close()
            if parser.stack or parser.rawdata or not re.search(r"<html(?:\s|>)", text, re.I) or not re.search(r"</html\s*>\s*$", text, re.I):
                raise GatewayError("invalid_or_partial_html")
        except GatewayError as error:
            raise GatewayError(error.reason, digest(raw)) from None
        rendered = "\n".join(p.strip() for p in parser.pieces if p.strip())
        screen.check(rendered, raw)
        if not rendered:
            raise GatewayError("empty_text", digest(raw))
        return {"text": rendered, "format": kind}
    if kind == "text":
        if not text.strip():
            raise GatewayError("empty_text", digest(raw))
        return {"text": text, "format": kind}
    raise GatewayError("unsupported_supplement_format", digest(raw))


def allowed_url(url: str) -> bool:
    try:
        p = urlsplit(url)
        if p.scheme != "https" or p.username is not None or p.password is not None or p.port not in (None, 443) or p.fragment:
            return False
        if p.hostname == "www.ebi.ac.uk":
            return p.path == "/europepmc/webservices/rest/search"
        if p.hostname != "pmc-oa-opendata.s3.amazonaws.com":
            return False
        if p.path == "/":
            q = parse_qs(p.query, strict_parsing=True)
            return set(q) == {"list-type", "prefix", "delimiter"} and q["list-type"] == ["2"] and q["delimiter"] == ["/"] and len(q["prefix"]) == 1 and re.fullmatch(r"PMC[1-9][0-9]{0,11}\.", q["prefix"][0]) is not None
        path = unquote(p.path)
        if not re.fullmatch(r"/PMC[1-9][0-9]{0,11}\.[1-9][0-9]*/[^/\\\x00-\x1f]+", path):
            return False
        if PurePosixPath(path).name in {".", ".."} or "%" in path or ":" in path:
            return False
        q = parse_qs(p.query, strict_parsing=True) if p.query else {}
        return not q or set(q) == {"md5"} and len(q["md5"]) == 1 and re.fullmatch(r"[a-fA-F0-9]{32}", q["md5"][0]) is not None
    except (ValueError, TypeError):
        return False


class RestrictedRedirect(HTTPRedirectHandler):
    def __init__(self, original_url: str):
        self.original_url = original_url
        super().__init__()

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # No cross-resource redirects: a valid host alone cannot establish that
        # the resulting file is the approved parent's source-linked object.
        if newurl != self.original_url or not allowed_url(newurl):
            raise GatewayError("blocked_network_redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http_get(url: str, kind: str, maximum: int, timeout: int) -> bytes:
    if not allowed_url(url):
        raise GatewayError("blocked_network_url")
    request = Request(url, headers={"User-Agent": "SessionLiteratureGateway/2.0 research", "Accept": ", ".join(sorted(MEDIA_TYPES[kind])), "Accept-Encoding": "identity"})
    try:
        with build_opener(RestrictedRedirect(url)).open(request, timeout=timeout) as response:
            if response.status != 200:
                raise GatewayError("unexpected_http_status")
            if response.url != url or not allowed_url(response.url):
                raise GatewayError("blocked_network_final_url")
            if response.headers.get("Content-Encoding", "identity").lower() not in {"identity", ""}:
                raise GatewayError("unsupported_http_content_encoding")
            mime = response.headers.get_content_type()
            if mime not in MEDIA_TYPES[kind]:
                raise GatewayError("unexpected_http_content_type")
            length = response.headers.get("Content-Length")
            if length is not None and (not length.isdigit() or int(length) > maximum):
                raise GatewayError("response_size_limit_or_invalid_length")
            raw = response.read(maximum + 1)
            if len(raw) > maximum:
                raise GatewayError("response_size_limit", digest(raw))
            if length is not None and len(raw) != int(length):
                raise GatewayError("partial_http_response", digest(raw))
            if not raw:
                raise GatewayError("empty_http_response", digest(raw))
            return raw
    except HTTPError as error:
        raise GatewayError("http_status_" + str(int(error.code))) from None
    except (URLError, TimeoutError, socket.timeout, OSError):
        raise GatewayError("network_or_timeout_failure") from None


class Session:
    def __init__(self, path: Path, config_path: Path):
        self.path = path.resolve()
        self.lock_fd = None
        try:
            config_raw = config_path.read_bytes()
            self.config = parse_json(config_raw)
            self.screen = Screen(self.config)
            if self.config["schema_version"] != 1:
                raise ValueError()
            for key in ("queries", "downloads", "auxiliary_requests"):
                if type(self.config["budgets"][key]) is not int or self.config["budgets"][key] < 0:
                    raise ValueError()
            for key in ("response_bytes", "timeout_seconds", "search_page_size", "table_cells"):
                if type(self.config["limits"][key]) is not int or self.config["limits"][key] < 1:
                    raise ValueError()
        except (OSError, KeyError, TypeError, ValueError):
            raise GatewayError("invalid_configuration") from None
        self.config_hash = digest(config_raw)
        self.path.mkdir(parents=True, exist_ok=True)
        try:
            self.lock_fd = os.open(self.path / ".gateway.lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(self.lock_fd, str(os.getpid()).encode("ascii"))
        except FileExistsError:
            raise GatewayError("session_locked") from None
        try:
            state_path = self.path / "state.json"
            if state_path.exists():
                self.state = parse_json(state_path.read_bytes())
                if self.state["config_sha256"] != self.config_hash or self.state["session_path"] != str(self.path):
                    raise GatewayError("session_configuration_or_path_changed")
            else:
                if any(p.name != ".gateway.lock" for p in self.path.iterdir()):
                    raise GatewayError("new_session_must_be_empty")
                self.state = {"schema_version": 1, "session_path": str(self.path), "config_sha256": self.config_hash,
                              "created_utc": utc(), "usage": {"queries": 0, "downloads": 0, "auxiliary_requests": 0,
                              "http_attempts": 0, "http_successes": 0, "http_elapsed_seconds": 0.0, "command_elapsed_seconds": 0.0},
                              "approved_metadata": {}, "parents": {}}
                self.save_state()
        except Exception:
            self.close()
            raise

    def close(self):
        if self.lock_fd is not None:
            os.close(self.lock_fd)
            self.lock_fd = None
            (self.path / ".gateway.lock").unlink(missing_ok=True)

    def save_state(self):
        target = self.path / "state.json"
        temporary = self.path / ".state.tmp"
        with temporary.open("wb") as handle:
            handle.write(encoded(self.state))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)

    def audit(self, entry: dict):
        with (self.path / "audit.jsonl").open("ab") as handle:
            handle.write(json.dumps({"timestamp_utc": utc(), **entry}, ensure_ascii=True, sort_keys=True).encode("ascii") + b"\n")
            handle.flush()
            os.fsync(handle.fileno())

    def request(self, url: str, kind: str, budget: str) -> bytes:
        if not allowed_url(url):
            raise GatewayError("blocked_network_url")
        usage = self.state["usage"]
        if usage[budget] >= self.config["budgets"][budget]:
            raise GatewayError("budget_exhausted_" + budget)
        # Reserve before the request, including rejected, unavailable and failed
        # requests. No retry is hidden or excluded from the construction budget.
        usage[budget] += 1
        usage["http_attempts"] += 1
        self.save_state()
        started = time.monotonic()
        event = {"type": "http_attempt", "budget": budget, "url_sha256": digest(url.encode()), "ordinal": usage["http_attempts"]}
        try:
            raw = http_get(url, kind, self.config["limits"]["response_bytes"], self.config["limits"]["timeout_seconds"])
            usage["http_successes"] += 1
            event.update(status="received", content_sha256=digest(raw), bytes=len(raw))
            return raw
        except GatewayError as error:
            event.update(status="error", reason=error.reason)
            raise
        finally:
            elapsed = time.monotonic() - started
            usage["http_elapsed_seconds"] += elapsed
            event["elapsed_seconds"] = elapsed
            self.save_state()
            self.audit(event)

    def save_artifact(self, raw: bytes, suffix: str) -> dict:
        # Every caller supplies screened content; use only digest-derived names.
        sha = digest(raw)
        relative = "approved/" + sha + "." + suffix
        destination = self.path / relative
        destination.parent.mkdir(exist_ok=True)
        if destination.exists() and digest(destination.read_bytes()) != sha:
            raise GatewayError("artifact_hash_conflict")
        if not destination.exists():
            with destination.open("xb") as handle:
                handle.write(raw)
        artifact = {"session_relative_path": relative, "sha256": sha, "bytes": len(raw)}
        self.audit({"type": "artifact_approved", "status": "accepted", "artifact": artifact, "config_sha256": self.config_hash})
        return artifact

    def read_artifact(self, artifact: dict) -> bytes:
        name = artifact["session_relative_path"]
        if not re.fullmatch(r"approved/[a-f0-9]{64}\.[a-z]+", name):
            raise GatewayError("invalid_artifact_path")
        raw = (self.path / name).read_bytes()
        if digest(raw) != artifact["sha256"]:
            raise GatewayError("artifact_hash_mismatch")
        return raw

    def search(self, query: str, limit: int, cursor: str = "*") -> dict:
        if not query.strip() or len(query) > 2000 or not 1 <= limit <= self.config["limits"]["search_page_size"] or not cursor or len(cursor) > 2000:
            raise GatewayError("invalid_search_arguments")
        self.screen.check(query)
        self.screen.check(cursor)
        url = API + "/search?" + urlencode({"query": query, "format": "json", "resultType": "core", "pageSize": limit, "cursorMark": cursor, "synonym": "false"})
        raw = self.request(url, "json", "queries")
        payload = parse_json(raw)
        try:
            records = payload["resultList"]["result"]
            if "errCode" in payload or not isinstance(records, list) or len(records) > limit or any(not isinstance(r, dict) for r in records) or type(payload["hitCount"]) is not int:
                raise ValueError()
            envelope = {k: v for k, v in payload.items() if k != "resultList"}
            envelope["resultList_metadata"] = {k: v for k, v in payload["resultList"].items() if k != "result"}
            self.screen.json(envelope, raw)
        except (KeyError, TypeError, ValueError):
            raise GatewayError("invalid_search_response", digest(raw)) from None
        accepted, rejected = [], []
        for record in records:
            record_raw = encoded(record)
            try:
                self.screen.json(record, record_raw)
                if not isinstance(record.get("title"), str) or not record["title"].strip() or not isinstance(record.get("abstractText"), str) or not record["abstractText"].strip():
                    raise GatewayError("missing_title_or_abstract", digest(record_raw))
                if record.get("pmcid"):
                    identifier = pmcid(record["pmcid"])
                    self.state["approved_metadata"][identifier] = {"record_sha256": digest(record_raw)}
                accepted.append(record)
            except GatewayError as error:
                rejected.append({"reason": error.reason, "content_sha256": error.content_sha256 or digest(record_raw)})
        result = {"type": "search_results", "status": "ok", "query": query, "requested_page_size": limit,
                  "retrieved_count": len(records), "total_hit_count": payload["hitCount"], "accepted_count": len(accepted),
                  "rejected_count": len(rejected), "next_cursor": payload.get("nextCursorMark"), "accepted": accepted,
                  "screening_scope": "Complete returned core metadata records; article and supplement text require separate fetching."}
        artifact = self.save_artifact(encoded(result), "json")
        self.save_state()
        self.audit({"type": "screening", "action": "search", "response_sha256": digest(raw), "approved_artifact": artifact, "rejected": rejected})
        result["approved_artifact"] = artifact
        return result

    def versions(self, identifier: str) -> list[int]:
        url = CLOUD + "/?" + urlencode({"list-type": "2", "prefix": identifier + ".", "delimiter": "/"})
        raw = self.request(url, "xml", "auxiliary_requests")
        root, _ = parse_xml(raw, self.screen)
        if local_tag(root.tag) != "ListBucketResult":
            raise GatewayError("invalid_version_listing", digest(raw))
        values = [e.text for e in root.iter() if local_tag(e.tag) == "IsTruncated"]
        if values != ["false"]:
            raise GatewayError("partial_version_listing", digest(raw))
        versions = []
        for element in root:
            if local_tag(element.tag) == "CommonPrefixes":
                children = list(element)
                if len(children) != 1:
                    raise GatewayError("invalid_version_listing", digest(raw))
                match = re.fullmatch(re.escape(identifier) + r"\.([1-9][0-9]*)/", children[0].text or "")
                if not match:
                    raise GatewayError("invalid_version_listing", digest(raw))
                versions.append(int(match.group(1)))
        return sorted(set(versions))

    def object_url(self, url: str, identifier: str, version: int, require_md5: bool = True) -> str:
        if not isinstance(url, str):
            raise GatewayError("invalid_manifest_object_url")
        # Official manifests contain s3://pmc-oa-opendata/... URLs; map only
        # that exact bucket to its documented anonymous HTTPS origin.
        original = urlsplit(url)
        if original.scheme == "s3" and original.netloc == "pmc-oa-opendata" and not original.fragment:
            url = CLOUD + original.path + ("?" + original.query if original.query else "")
        if not allowed_url(url):
            raise GatewayError("invalid_manifest_object_url")
        p = urlsplit(url)
        if p.hostname != "pmc-oa-opendata.s3.amazonaws.com" or not unquote(p.path).startswith(f"/{identifier}.{version}/"):
            raise GatewayError("manifest_parent_mismatch")
        if require_md5 and not parse_qs(p.query).get("md5"):
            raise GatewayError("manifest_object_checksum_missing")
        return url

    def checked_download(self, url: str, kind: str) -> bytes:
        raw = self.request(url, kind, "downloads")
        expected = parse_qs(urlsplit(url).query)["md5"][0].lower()
        if hashlib.md5(raw).hexdigest() != expected:
            raise GatewayError("manifest_object_checksum_mismatch", digest(raw))
        return raw

    def fetch(self, identifier: str, version: int | None = None) -> dict:
        identifier = pmcid(identifier)
        existing = self.state["parents"].get(identifier)
        if existing:
            if version is not None and version != existing["version"]:
                raise GatewayError("session_parent_version_already_fixed")
            raw = self.read_artifact(existing["xml_artifact"])
            _, text = parse_xml(raw, self.screen)
            return {"type": "article", "status": "accepted", "pmcid": identifier, "version": existing["version"], "cached": True, "text": text, "approved_artifact": existing["text_artifact"], "xml_artifact": existing["xml_artifact"]}
        if identifier not in self.state["approved_metadata"]:
            self.search("PMCID:" + identifier, 1)
            if identifier not in self.state["approved_metadata"]:
                raise GatewayError("approved_parent_metadata_unavailable")
        versions = self.versions(identifier)
        if not versions:
            raise GatewayError("cloud_fulltext_unavailable")
        if version is None:
            if len(versions) != 1:
                return {"type": "version_choice", "status": "selection_required", "pmcid": identifier, "available_versions": versions, "reason": "multiple_versions_require_explicit_selection"}
            version = versions[0]
        if version not in versions:
            raise GatewayError("requested_version_unavailable")
        manifest_url = f"{CLOUD}/{identifier}.{version}/{identifier}.{version}.json"
        manifest_raw = self.request(manifest_url, "json", "auxiliary_requests")
        manifest = parse_json(manifest_raw)
        self.screen.json(manifest, manifest_raw)
        try:
            if manifest["pmcid"] != identifier or str(manifest["version"]) != str(version):
                raise GatewayError("manifest_parent_mismatch", digest(manifest_raw))
            xml_url = self.object_url(manifest["xml_url"], identifier, version)
            if PurePosixPath(unquote(urlsplit(xml_url).path)).name != f"{identifier}.{version}.xml":
                raise GatewayError("manifest_xml_name_mismatch", digest(manifest_raw))
            media = manifest.get("media_urls") or []
            if not isinstance(media, list):
                raise ValueError()
            for url in media:
                self.object_url(url, identifier, version)
        except (KeyError, TypeError, ValueError):
            raise GatewayError("invalid_article_manifest", digest(manifest_raw)) from None
        raw = self.checked_download(xml_url, "xml")
        root, text = parse_xml(raw, self.screen)
        bodies = [e for e in root if local_tag(e.tag) == "body"]
        if local_tag(root.tag) != "article" or len(bodies) != 1 or not "".join(bodies[0].itertext()).strip():
            raise GatewayError("invalid_or_incomplete_article", digest(raw))
        metadata_nodes = [m for front in root if local_tag(front.tag) == "front" for m in front if local_tag(m.tag) == "article-meta"]
        ids = ["".join(e.itertext()).strip() for m in metadata_nodes for e in m if local_tag(e.tag) == "article-id" and e.attrib.get("pub-id-type") in {"pmcid", "pmc"}]
        allowed_ids = {identifier, identifier[3:], f"{identifier}.{version}", f"{identifier[3:]}.{version}"}
        if not ids or any(value not in allowed_ids for value in ids):
            raise GatewayError("article_xml_parent_mismatch", digest(raw))
        links = self.source_links(root, identifier, version, media)
        xml_artifact = self.save_artifact(raw, "xml")
        text_artifact = self.save_artifact(text.encode("utf-8"), "txt")
        manifest_artifact = self.save_artifact(encoded(manifest), "json")
        parent = {"version": version, "xml_artifact": xml_artifact, "text_artifact": text_artifact, "manifest_artifact": manifest_artifact,
                  "canonical_parent_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{identifier}/", "source_xml_url": xml_url,
                  "supplements": links}
        self.screen.json(parent)
        self.state["parents"][identifier] = parent
        self.save_state()
        return {"type": "article", "status": "accepted", "pmcid": identifier, "version": version, "cached": False, "text": text,
                "approved_artifact": text_artifact, "xml_artifact": xml_artifact, "canonical_parent_url": parent["canonical_parent_url"],
                "screening_scope": "Entire retrieved JATS XML, attributes, captions, references and text. Supplement bytes are not yet retrieved."}

    def source_links(self, root, identifier: str, version: int, media: list[str]) -> list[dict]:
        # Only JATS supplementary-material descendants count. Ordinary graphics,
        # arbitrary external URLs and unlinked manifest objects are never exposed.
        media_by_name = {}
        for url in media:
            url = self.object_url(url, identifier, version)
            name = PurePosixPath(unquote(urlsplit(url).path)).name
            if name in media_by_name:
                raise GatewayError("ambiguous_manifest_media_name")
            media_by_name[name] = url
        result = []
        seen = set()
        for group in root.iter():
            if local_tag(group.tag) not in {"supplementary-material", "inline-supplementary-material"}:
                continue
            for node in group.iter():
                href = node.attrib.get("{http://www.w3.org/1999/xlink}href") or node.attrib.get("href")
                if not href or href in seen:
                    continue
                seen.add(href)
                parsed = urlsplit(href)
                decoded = unquote(parsed.path)
                if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or "/" in decoded or "\\" in decoded or ":" in decoded or decoded in {".", ".."} or "%" in decoded:
                    # Preserve only a hash of unsupported references, not a URL.
                    result.append({"supplement_id": digest(href.encode())[:24], "status": "unsupported", "reason": "nonlocal_or_noncanonical_source_link", "link_sha256": digest(href.encode())})
                    continue
                url = media_by_name.get(decoded)
                if not url:
                    result.append({"supplement_id": digest(href.encode())[:24], "status": "unsupported", "reason": "source_link_not_in_parent_manifest", "link_sha256": digest(href.encode())})
                    continue
                kind = FORMATS.get(PurePosixPath(decoded).suffix.lower())
                item = {"supplement_id": digest((identifier + ":" + str(version) + ":" + url).encode())[:24], "status": "available" if kind else "unsupported",
                        "source_filename": decoded, "format": kind, "source_href": href, "source_url": url}
                if not kind:
                    item["reason"] = "unsupported_supplement_format"
                result.append(item)
        return result

    def parent(self, identifier: str) -> dict:
        identifier = pmcid(identifier)
        parent = self.state["parents"].get(identifier)
        if parent is None:
            raise GatewayError("fetch_and_approve_parent_first")
        self.screen.json(parent)
        # Verify approved parent artifacts each time; session state is procedural
        # bookkeeping, not a security boundary against a malicious local user.
        root, _ = parse_xml(self.read_artifact(parent["xml_artifact"]), self.screen)
        manifest = parse_json(self.read_artifact(parent["manifest_artifact"]))
        self.screen.json(manifest)
        links = self.source_links(root, identifier, parent["version"], manifest.get("media_urls") or [])
        if links != parent["supplements"]:
            raise GatewayError("parent_provenance_changed")
        return parent

    def list_supplements(self, identifier: str) -> dict:
        identifier = pmcid(identifier)
        parent = self.parent(identifier)
        return {"type": "supplement_listing", "status": "ok", "pmcid": identifier, "version": parent["version"],
                "canonical_parent_url": parent["canonical_parent_url"], "parent_xml_sha256": parent["xml_artifact"]["sha256"],
                "supplements": parent["supplements"], "screening_scope": "Complete parent XML and manifest screened; listed supplement contents remain unread until fetch-supplement."}

    def fetch_supplement(self, identifier: str, supplement_id: str) -> dict:
        identifier = pmcid(identifier)
        parent = self.parent(identifier)
        matches = [item for item in parent["supplements"] if item["supplement_id"] == supplement_id]
        if len(matches) != 1:
            raise GatewayError("unknown_source_linked_supplement")
        item = matches[0]
        if item["status"] != "available":
            raise GatewayError(item["reason"])
        url = self.object_url(item["source_url"], identifier, parent["version"])
        raw = self.checked_download(url, item["format"])
        parsed = parse_supplement(raw, item["format"], self.screen, self.config["limits"]["table_cells"])
        self.screen.json(parsed, raw)
        suffix = "txt" if item["format"] == "text" else item["format"]
        artifact = self.save_artifact(raw, suffix)
        return {"type": "supplement", "status": "accepted", "pmcid": identifier, "version": parent["version"],
                "supplement_id": supplement_id, "canonical_parent_url": parent["canonical_parent_url"],
                "parent_xml_sha256": parent["xml_artifact"]["sha256"], "source_href": item["source_href"],
                "source_url": url, "approved_artifact": artifact, **parsed,
                "screening_scope": "Complete downloaded bytes and complete parsed textual content; no silent truncation."}


class JSONArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise GatewayError("invalid_cli_arguments")


def main(argv: list[str] | None = None) -> int:
    session = None
    started = time.monotonic()
    result = None
    command = "arguments"
    try:
        parser = JSONArgumentParser(add_help=False)
        parser.add_argument("--session", required=True)
        parser.add_argument("--config", required=True)
        subparsers = parser.add_subparsers(dest="command", required=True, parser_class=JSONArgumentParser)
        search = subparsers.add_parser("search", add_help=False)
        search.add_argument("--query", required=True)
        search.add_argument("--limit", type=int, default=10)
        search.add_argument("--cursor", default="*")
        fetch = subparsers.add_parser("fetch", add_help=False)
        fetch.add_argument("--pmcid", required=True)
        fetch.add_argument("--version", type=int)
        listing = subparsers.add_parser("list-supplements", add_help=False)
        listing.add_argument("--pmcid", required=True)
        supplement = subparsers.add_parser("fetch-supplement", add_help=False)
        supplement.add_argument("--pmcid", required=True)
        supplement.add_argument("--supplement-id", required=True)
        args = parser.parse_args(argv)
        command = args.command
        session = Session(Path(args.session), Path(args.config))
        if command == "search":
            result = session.search(args.query, args.limit, args.cursor)
        elif command == "fetch":
            result = session.fetch(args.pmcid, args.version)
        elif command == "list-supplements":
            result = session.list_supplements(args.pmcid)
        else:
            result = session.fetch_supplement(args.pmcid, args.supplement_id)
    except GatewayError as error:
        result = {"type": "gateway_error", "status": "rejected" if error.reason.startswith("excluded_") else "error", "reason": error.reason}
        if error.content_sha256:
            result["content_sha256"] = error.content_sha256
    except KeyboardInterrupt:
        result = {"type": "gateway_error", "status": "error", "reason": "interrupted_command"}
    except Exception:
        result = {"type": "gateway_error", "status": "error", "reason": "internal_gateway_failure"}
    finally:
        elapsed = time.monotonic() - started
        if result is None:
            result = {"type": "gateway_error", "status": "error", "reason": "interrupted_command"}
        result["elapsed_seconds"] = elapsed
        result["notice"] = NOTICE
        if session:
            try:
                session.state["usage"]["command_elapsed_seconds"] += elapsed
                session.save_state()
                result["usage"] = dict(session.state["usage"])
                result["budgets"] = session.config["budgets"]
                # Error output contains only categories/hash, never rejected text.
                event = {"type": "command", "command": command, "status": result["status"], "elapsed_seconds": elapsed, "usage": result["usage"]}
                for key in ("reason", "content_sha256", "approved_artifact"):
                    if key in result:
                        event[key] = result[key]
                session.audit(event)
            except Exception:
                result = {"type": "gateway_error", "status": "error", "reason": "session_finalization_failure", "elapsed_seconds": elapsed}
            finally:
                try:
                    session.close()
                except Exception:
                    result = {"type": "gateway_error", "status": "error", "reason": "session_close_failure", "elapsed_seconds": elapsed}
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
    return 0 if result["status"] in {"ok", "accepted"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

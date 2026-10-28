"""Conservative publication-text gateway for a procedurally blinded pilot.

Only screened accepted text is printed or saved. Rejections log identifiers,
counts, opaque content hashes and categorical reasons, never source excerpts.
This is a contamination screen, not a guarantee of complete contamination detection.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import socket
import sys
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
LITERATURE = ROOT / "literature"
API_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
TIMEOUT_SECONDS = 20
MAX_ATTEMPTS = 2
MAX_BYTES = 8 * 1024 * 1024
NOTICE = "Automatically screened publication text; screening does not guarantee absence of all target-derived evidence."


class GatewayError(Exception):
    """Only fixed safe error codes may leave the gateway."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def plain_text(text: str) -> str:
    decoded = html.unescape(str(text))
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", decoded)).strip()


def forbidden_reason(text: str) -> str | None:
    normalized = unicodedata.normalize("NFKC", html.unescape(str(text))).casefold()
    # Check rendered text as well as raw text, including punctuation, split tags,
    # spaces, numeric entities and zero-width formatting around survey aliases.
    compact = "".join(c for c in re.sub(r"<[^>]*>", "", normalized) if c.isalnum())
    if "nhanes" in compact:
        return "forbidden_survey_alias"
    if any(alias in compact for alias in [
        "nationalhealthandnutritionexaminationsurvey",
        "nationalhealthnutritionexaminationsurvey",
        "nationalhealthandnutritionexaminationstudy",
        "nationalhealthnutritionexaminationstudy",
    ]):
        return "forbidden_survey_name"
    if re.search(r"\bhanes\s*(?:i{1,3}|[123])\b", normalized):
        return "forbidden_survey_alias"
    if re.search(r"\b(?:ins|bmx|demo|diq|fastqx)[ _.-]*j\b|\b(?:lbxin|lbdinsi|lbdinlc|wtsaf2yr|sdmvstra|sdmvpsu)\b", normalized):
        return "forbidden_target_variable_or_file_alias"
    return None


def safe_identifier(value: object) -> str:
    text = str(value or "")
    return text if re.fullmatch(r"[A-Za-z0-9_:.+-]{1,100}", text) else "unavailable"


def article_identity(record: dict) -> str:
    return safe_identifier(record.get("source", "unknown")) + ":" + safe_identifier(record.get("id", "unknown"))


def audit(entry: dict) -> None:
    LITERATURE.mkdir(exist_ok=True)
    event = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), **entry}
    payload = (json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(LITERATURE / "audit.jsonl", os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)


def save_approved(kind: str, data: bytes, suffix: str) -> dict:
    approved = LITERATURE / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    sha = digest(data)
    destination = approved / f"{kind}_{sha}.{suffix}"
    try:
        with destination.open("xb") as handle:
            handle.write(data)
    except FileExistsError:
        if digest(destination.read_bytes()) != sha:
            raise GatewayError("approved_artifact_hash_conflict")
    return {"path": str(destination.relative_to(ROOT)).replace("\\", "/"), "sha256": sha, "bytes": len(data)}


def allowed_api_url(url: str) -> bool:
    parts = urlsplit(url)
    return parts.scheme == "https" and parts.hostname == "www.ebi.ac.uk" and parts.username is None and parts.password is None and parts.port in (None, 443) and parts.path.startswith("/europepmc/webservices/rest/")


class RestrictedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_api_url(newurl):
            raise GatewayError("blocked_network_redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request_bytes(url: str, accept: str) -> bytes:
    if not allowed_api_url(url):
        raise GatewayError("blocked_network_url")
    opener = build_opener(RestrictedRedirect())
    for attempt in range(MAX_ATTEMPTS):
        try:
            request = Request(url, headers={"User-Agent": "BlindedLiteratureGateway/1.0 academic-research", "Accept": accept, "Accept-Encoding": "identity"})
            with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
                if not allowed_api_url(response.url):
                    raise GatewayError("blocked_network_final_url")
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise GatewayError("response_size_limit")
                return data
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504):
                raise GatewayError(f"http_status_{error.code}") from None
            safe_error = "transient_http_failure"
        except (URLError, TimeoutError, socket.timeout, OSError):
            safe_error = "network_or_timeout_failure"
        if attempt + 1 < MAX_ATTEMPTS:
            time.sleep(1)
    raise GatewayError(safe_error)


def api_search(query: str, limit: int) -> tuple[list[dict], str]:
    parameters = urlencode({"query": query, "format": "json", "resultType": "core", "pageSize": limit, "synonym": "false"})
    raw = request_bytes(API_BASE + "/search?" + parameters, "application/json")
    try:
        payload = json.loads(raw)
        records = payload.get("resultList", {}).get("result", [])
        if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
            raise ValueError()
    except (ValueError, AttributeError, TypeError):
        raise GatewayError("invalid_search_response") from None
    return records[:limit], digest(raw)


def screen_record(record: dict) -> tuple[dict | None, str | None]:
    title = plain_text(record.get("title", ""))
    abstract = plain_text(record.get("abstractText", ""))
    # Screen the entire returned core record as well as its rendered text before
    # selecting display fields. Search-result text is never printed beforehand.
    reason = forbidden_reason(json.dumps(record, ensure_ascii=False) + " " + title + " " + abstract)
    if reason:
        return None, reason
    if not title or not abstract:
        return None, "missing_title_or_abstract"
    accepted = {
        "source_id": article_identity(record), "pmid": safe_identifier(record.get("id")) if record.get("source") == "MED" else None,
        "pmcid": safe_identifier(record.get("pmcid")) if record.get("pmcid") else None,
        "doi": str(record.get("doi") or ""), "title": title,
        "year": str(record.get("pubYear") or ""), "abstract": abstract,
        "screening_scope": "core metadata and abstract only; full text must be fetched through this gateway before use",
    }
    return accepted, None


def search(query: str, limit: int) -> dict:
    records, response_hash = api_search(query, limit)
    accepted, rejected = [], []
    for record in records:
        item, reason = screen_record(record)
        record_hash = digest(json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8"))
        if item is not None:
            accepted.append(item)
        else:
            rejected.append({"source_id": article_identity(record), "reason": reason, "content_sha256": record_hash})
    result = {"status": "ok", "query": query, "screened_count": len(records), "accepted_count": len(accepted), "rejected_count": len(rejected), "notice": NOTICE, "accepted": accepted}
    artifact = save_approved("search", json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"), "json")
    audit({"action": "search", "query": query, "status": "ok", "screened_count": len(records), "accepted_source_ids": [r["source_id"] for r in accepted], "rejected": rejected, "response_sha256": response_hash, "approved_artifact": artifact})
    result["approved_artifact"] = artifact
    return result


def normalize_pmcid(value: str) -> str:
    value = value.upper()
    if not re.fullmatch(r"PMC[1-9][0-9]{0,11}", value):
        raise GatewayError("invalid_pmcid")
    return value


def normalize_pmid(value: str) -> str:
    if not re.fullmatch(r"[1-9][0-9]{0,11}", value):
        raise GatewayError("invalid_pmid")
    return value


def article_from_url(url: str) -> tuple[str, str]:
    """Only canonical repository article URLs are accepted; never fetch a URL supplied by the caller."""
    try:
        parts = urlsplit(url)
        hostname, port = parts.hostname or "", parts.port
    except ValueError:
        raise GatewayError("blocked_article_url") from None
    if parts.scheme != "https" or parts.username is not None or parts.password is not None or port not in (None, 443) or parts.query or parts.fragment:
        raise GatewayError("blocked_article_url")
    if hostname == "cdc.gov" or hostname.endswith(".cdc.gov") or forbidden_reason(url):
        raise GatewayError("blocked_target_or_raw_data_url")
    patterns = {
        "pmc.ncbi.nlm.nih.gov": r"/articles/(PMC[1-9][0-9]{0,11})/?",
        "www.ncbi.nlm.nih.gov": r"/pmc/articles/(PMC[1-9][0-9]{0,11})/?",
        "europepmc.org": r"/articles/(PMC[1-9][0-9]{0,11})/?",
        "www.europepmc.org": r"/articles/(PMC[1-9][0-9]{0,11})/?",
        "pubmed.ncbi.nlm.nih.gov": r"/([1-9][0-9]{0,11})/?",
    }
    pattern = patterns.get(hostname)
    match = re.fullmatch(pattern, parts.path, re.IGNORECASE) if pattern else None
    if not match:
        raise GatewayError("blocked_article_url")
    identifier = match.group(1)
    return ("pmcid", normalize_pmcid(identifier)) if identifier.upper().startswith("PMC") else ("pmid", normalize_pmid(identifier))


def fetch_article(kind: str, value: str) -> dict:
    if kind == "url":
        kind, value = article_from_url(value)
    identifier = normalize_pmcid(value) if kind == "pmcid" else normalize_pmid(value)
    source_id = ("PMC:" if kind == "pmcid" else "MED:") + identifier
    if kind == "pmid":
        records, response_hash = api_search(f"EXT_ID:{identifier} AND SRC:MED", 1)
        if not records or str(records[0].get("id")) != identifier:
            raise GatewayError("pmid_not_found")
        accepted, reason = screen_record(records[0])
        if reason:
            audit({"action": "fetch", "source_id": source_id, "status": "rejected", "reason": reason, "screened_count": 1, "response_sha256": response_hash})
            return {"status": "rejected", "source_id": source_id, "reason": reason, "screened_count": 1}
        if not accepted["pmcid"]:
            raise GatewayError("open_fulltext_unavailable")
        identifier = normalize_pmcid(accepted["pmcid"])
    raw = request_bytes(API_BASE + "/" + identifier + "/fullTextXML", "application/xml")
    try:
        xml_text = raw.decode("utf-8")
    except UnicodeError:
        raise GatewayError("unrecognized_fulltext_encoding") from None
    # Reject a raw-text hit before parsing or writing, then screen all XML text,
    # including captions, appendices and references. Never retrieve supplements.
    reason = forbidden_reason(xml_text)
    if reason is None:
        try:
            document = ET.fromstring(xml_text)
            if document.tag.split("}")[-1] != "article":
                raise GatewayError("unexpected_fulltext_document")
            text = "\n".join(piece.strip() for piece in document.itertext() if piece.strip())
        except ET.ParseError:
            raise GatewayError("invalid_fulltext_xml") from None
        reason = forbidden_reason(text)
    if reason:
        audit({"action": "fetch", "source_id": source_id, "pmcid": identifier, "status": "rejected", "reason": reason, "screened_count": 1, "response_sha256": digest(raw)})
        return {"status": "rejected", "source_id": source_id, "pmcid": identifier, "reason": reason, "screened_count": 1}
    if not text.strip():
        raise GatewayError("empty_fulltext")
    artifact = save_approved(identifier, text.encode("utf-8"), "txt")
    audit({"action": "fetch", "source_id": source_id, "pmcid": identifier, "status": "accepted", "screened_count": 1, "response_sha256": digest(raw), "approved_artifact": artifact})
    return {"status": "accepted", "source_id": source_id, "pmcid": identifier, "screening_scope": "complete retrieved article XML including references; supplements not retrieved", "notice": NOTICE, "approved_artifact": artifact, "text": text}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--limit", type=int, default=10)
    fetch_parser = subparsers.add_parser("fetch")
    targets = fetch_parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("--pmcid")
    targets.add_argument("--pmid")
    targets.add_argument("--url")
    args = parser.parse_args(argv)
    try:
        if args.command == "search":
            if not 1 <= args.limit <= 20:
                raise GatewayError("search_limit_must_be_1_to_20")
            if not args.query.strip() or len(args.query) > 2000:
                raise GatewayError("invalid_query_length")
            result = search(args.query, args.limit)
        else:
            kind = next(k for k in ["pmcid", "pmid", "url"] if getattr(args, k))
            result = fetch_article(kind, getattr(args, kind))
        # ASCII JSON also works in Windows terminals with legacy code pages;
        # saved approved artifacts retain UTF-8 text.
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0 if result["status"] in ("ok", "accepted") else 2
    except GatewayError as error:
        # Error strings are authored fixed categories; never print HTTP bodies,
        # server response text, parser input, redirects, or exception reprs.
        result = {"status": "error", "reason": str(error)}
        audit({"action": args.command, **result, "screened_count": 0})
        print(json.dumps(result))
        return 2
    except Exception:
        result = {"status": "error", "reason": "internal_gateway_failure"}
        audit({"action": args.command, **result, "screened_count": 0})
        print(json.dumps(result))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

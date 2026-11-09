"""Invented evidence only, with intercepted HTTP and resolver responses."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import socket
import time

import pytest

from cohort_harness import web_evidence_v1 as web
from cohort_harness.contracts import ContractError
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import freeze_candidate, verify_candidate
from cohort_harness.literature import run_literature


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


@pytest.fixture
def bundle(tmp_path):
    # Keep invented artifacts under the declared work directory while allowing
    # content-hash filenames on Windows installations with MAX_PATH enabled.
    root = make_demo(tmp_path.parent / hashlib.sha256(tmp_path.name.encode()).hexdigest()[:8])
    task = json.loads((root / "task.json").read_text())
    task["information_policy"].update(allowed_tools=["web.fetch", "literature.fetch"],
                                       excluded_cohorts=["Excluded Study"])
    task["budget"].update(source_downloads=20, source_queries=5)
    write(root / "task.json", task)
    return root


@pytest.fixture
def transport(monkeypatch):
    responses, calls = {}, []
    monkeypatch.setattr(web, "_resolve_public", lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))])
    def request(url, addresses, deadline, limit, consume):
        calls.append(url)
        value = responses[url]
        if isinstance(value, Exception):
            raise value
        status, headers, raw = value
        consume(min(len(raw), limit))
        if len(raw) > limit:
            raise web.gateway.GatewayError("response_size_limit")
        return status, headers, raw
    monkeypatch.setattr(web, "_http_once", request)
    return responses, calls


def retrieve(bundle, url="https://hospital.example/guide", **kwargs):
    return web.fetch(bundle, url, kwargs.pop("source_id", "invented-guide"),
                     kwargs.pop("purpose", "Check a source definition"),
                     kwargs.pop("source_type", "official_hospital_website"), **kwargs)


def neutral(transport, url="https://hospital.example/guide", raw=b"Invented source definition.", mime="text/plain"):
    transport[0][url] = (200, {"content-type": mime}, raw)


def test_init_binding_and_config_validation(bundle):
    result = web.init(bundle, {"http_requests": 7})
    assert result["status"] == "ok"
    assert result["shared_usage"]["downloads"] == 0
    assert web.verify(result["state"])["usage"]["http_attempts"] == 0
    assert web.validate_config({"http_requests": 7})["response_bytes"] == 16 * 1024 * 1024
    assert web.init(bundle, {"http_requests": 7})["status"] == "ok"
    assert web.init(bundle, {"http_requests": 8})["status"] == "error"
    for config in ({"papers": 3}, {"http_requests": True}, {"response_bytes": 0}, []):
        with pytest.raises(ContractError):
            web.validate_config(config)


@pytest.mark.parametrize("mode,tools", [("prior_only", ["web.fetch"]), ("published_evidence", [])])
def test_permissions_before_network(bundle, transport, mode, tools):
    task = json.loads((bundle / "task.json").read_text())
    task["information_policy"].update(mode=mode, allowed_tools=tools)
    write(bundle / "task.json", task)
    assert retrieve(bundle)["status"] == "error"
    assert transport[1] == []
    assert not (bundle / "web_evidence_v1").exists()


def test_append_registration_cache_and_frozen_prefix(bundle, transport):
    candidate = bundle / "candidates/initial"
    freeze_candidate(bundle, candidate)
    old_receipt = (candidate / "freeze.json").read_bytes()
    old_registry = json.loads((bundle / "registry.json").read_text())["artifacts"]
    neutral(transport, raw=b'<html><head><script>ignored()</script></head><body><p>Invented definition.</p></body></html>', mime="text/html")
    result = retrieve(bundle)
    assert result["status"] == "accepted", result
    assert result["cached"] is False
    assert len(result["registered_artifacts"]) == 3
    record = result["provenance"]["retrieval"]
    assert record["parsed_form"] == "html_text"
    assert record["final_url"] == "https://hospital.example/guide"
    assert record["retrieved_utc"]
    assert (bundle / record["extracted_artifact"]["path"]).read_bytes() == b"Invented definition."
    assert result["provenance"]["applicability"] == "not_assessed"
    registry_before = (bundle / "registry.json").read_bytes()
    repeated = retrieve(bundle)
    assert repeated["cached"] is True
    assert len(transport[1]) == 1
    assert repeated["shared_usage"]["downloads"] == 1
    assert (bundle / "registry.json").read_bytes() == registry_before
    registry = json.loads(registry_before)["artifacts"]
    assert registry[:len(old_registry)] == old_registry
    assert (candidate / "freeze.json").read_bytes() == old_receipt
    verify_candidate(bundle, candidate)
    web.verify(result["state"])


def test_cached_url_new_purpose_is_declared_in_new_manifest(bundle, transport):
    neutral(transport)
    initial = retrieve(bundle)
    updated = retrieve(bundle, purpose="Inspect a separate definition", source_id="second-use")
    assert updated["cached"] and updated["usage"]["downloads"] == 1
    assert len(transport[1]) == 1
    assert updated["provenance"]["author_stated_purpose"] == "Inspect a separate definition"
    assert initial["provenance"]["retrieval"] == updated["provenance"]["retrieval"]
    assert len(web.verify(bundle)["registrations"]) == 2


@pytest.mark.parametrize("url", ["http://hospital.example/", "file:///etc/passwd", "https://user:secret@hospital.example/",
    "https://127.0.0.1/", "https://10.0.0.1/", "https://169.254.169.254/", "https://[::1]/", "https://localhost/",
    "https://hospital.local/", "https://hospital.example:8443/", "https://hospital.example/\r\nx"])
def test_blocked_urls_do_not_reach_transport(bundle, transport, url):
    result = retrieve(bundle, url)
    assert result["reason"] == "blocked_network_url"
    assert transport[1] == []
    events = [json.loads(line) for line in (bundle / "web_evidence_v1/audit.jsonl").read_text().splitlines()]
    assert events[-1]["reason"] == "blocked_network_url"
    assert "secret" not in json.dumps(events)


def test_resolver_rejects_any_private_answer(monkeypatch):
    monkeypatch.setattr(web.socket, "getaddrinfo", lambda *a, **kw: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.0.1", 443))])
    with pytest.raises(web.gateway.GatewayError, match="blocked_private_network_address"):
        web._resolve_public("mixed.example", time.monotonic() + 2)


def test_redirects_are_checked_and_charged(bundle, transport):
    transport[0]["https://hospital.example/guide"] = (302, {"location": "https://publisher.example/definition"}, b"")
    neutral(transport, "https://publisher.example/definition")
    result = retrieve(bundle)
    assert result["status"] == "accepted", result
    assert result["usage"]["http_attempts"] == 2
    assert result["shared_usage"]["downloads"] == 1
    assert result["provenance"]["retrieval"]["final_url"] == "https://publisher.example/definition"
    assert result["provenance"]["retrieval"]["redirect_chain"] == ["https://publisher.example/definition"]


def test_redirect_to_private_or_excluded_target_is_not_requested(bundle, transport):
    transport[0]["https://hospital.example/guide"] = (302, {"location": "https://127.0.0.1/private"}, b"")
    result = retrieve(bundle)
    assert result["reason"] == "blocked_network_url"
    assert len(transport[1]) == 1
    assert result["usage"]["http_attempts"] == 1
    assert web.verify(bundle)["registrations"] == []


@pytest.mark.parametrize("raw,mime", [
    (b"Excluded Study REJECTED_SENTINEL", "text/plain"),
    (b'<html><body>Neutral</body><script>Excluded Study REJECTED_SENTINEL</script></html>', "text/html"),
    (b'<html><body>Excluded <b>Study</b> REJECTED_SENTINEL</body></html>', "text/html")])
def test_excluded_content_not_persisted_or_returned(bundle, transport, raw, mime):
    neutral(transport, raw=raw, mime=mime)
    result = retrieve(bundle)
    assert result["status"] == "rejected", result
    assert result["usage"]["response_bytes"] == len(raw)
    assert result["shared_usage"]["downloads"] == 1
    assert "REJECTED_SENTINEL" not in json.dumps(result)
    for path in bundle.rglob("*"):
        if path.is_file():
            assert b"REJECTED_SENTINEL" not in path.read_bytes()
    assert web.verify(bundle)["registrations"] == []


def test_failures_and_total_cost_are_cumulative(bundle, transport):
    assert web.init(bundle, {"total_bytes": 20, "response_bytes": 20, "http_requests": 2})["status"] == "ok"
    neutral(transport, raw=b"012345678901")
    first = retrieve(bundle)
    assert first["usage"]["response_bytes"] == 12
    neutral(transport, "https://hospital.example/second", b"abcdefghijkl")
    second = retrieve(bundle, "https://hospital.example/second")
    assert second["reason"] == "response_size_limit"
    assert second["usage"]["response_bytes"] == 20
    third = retrieve(bundle, "https://hospital.example/third")
    assert third["reason"] == "budget_exhausted_http_requests"
    assert len(transport[1]) == 2
    assert third["usage"]["downloads"] == 2


def test_network_failure_no_retry_and_shared_literature_download_budget(bundle, transport, monkeypatch):
    task = json.loads((bundle / "task.json").read_text())
    task["budget"]["source_downloads"] = 1
    write(bundle / "task.json", task)
    transport[0]["https://hospital.example/guide"] = web.gateway.GatewayError("network_or_timeout_failure")
    result = retrieve(bundle)
    assert result["reason"] == "network_or_timeout_failure"
    assert len(transport[1]) == 1 and result["usage"]["http_attempts"] == 1
    assert result["usage"]["response_bytes"] == 0
    shared = run_literature(bundle, "init")
    assert shared["status"] == "ok" and shared["usage"]["downloads"] == 1
    assert retrieve(bundle)["reason"] == "budget_exhausted_downloads"
    assert len(transport[1]) == 1


@pytest.mark.parametrize("target", ["raw", "text", "approval", "manifest", "task", "config"])
def test_tampering_fails_before_cached_source_return(bundle, transport, target):
    neutral(transport)
    result = retrieve(bundle)
    record = result["provenance"]["retrieval"]
    if target in {"raw", "text"}:
        path = record["raw_artifact" if target == "raw" else "extracted_artifact"]["path"]
        (bundle / path).write_bytes(b"tampered")
    elif target == "manifest":
        (bundle / result["registered_artifacts"][2]["path"]).write_bytes(b"tampered")
    elif target == "approval":
        path = bundle / "web_evidence_v1/audit.jsonl"
        events = [json.loads(line) for line in path.read_text().splitlines()]
        path.write_text("".join(json.dumps(event) + "\n" for event in events if event["type"] != "approved"))
    elif target == "task":
        path = bundle / "task.json"
        path.write_bytes(path.read_bytes() + b" ")
    else:
        path = bundle / "web_evidence_v1/config.json"
        path.write_bytes(path.read_bytes() + b" ")
    assert retrieve(bundle)["status"] == "error"
    assert len(transport[1]) == 1


def test_missing_pdf_parser_truthful_no_raw_registration(bundle, transport, monkeypatch):
    neutral(transport, raw=b"%PDF-1.7 invented only", mime="application/pdf")
    monkeypatch.setattr(web.importlib.util, "find_spec", lambda name: None)
    result = retrieve(bundle)
    assert result["reason"] == "pdf_parser_unavailable"
    assert result["usage"]["downloads"] == 1
    assert not (bundle / "sources/web_evidence_v1").exists()


def test_pdf_text_path_and_exclusion_screen(bundle, transport, monkeypatch):
    neutral(transport, raw=b"%PDF-1.7 invented parser fixture", mime="application/pdf")
    monkeypatch.setattr(web, "_parse_pdf", lambda *args: ("Invented page text", {"name": "invented_test_parser", "pages": 1, "ocr": False}))
    result = retrieve(bundle)
    assert result["status"] == "accepted", result
    assert result["provenance"]["retrieval"]["parsed_form"] == "pdf_text"
    assert result["provenance"]["retrieval"]["parser"]["ocr"] is False
    neutral(transport, "https://hospital.example/rejected.pdf", b"%PDF-1.7 other fixture", "application/pdf")
    monkeypatch.setattr(web, "_parse_pdf", lambda *args: ("Excluded Study", {"name": "invented_test_parser", "pages": 1, "ocr": False}))
    assert retrieve(bundle, "https://hospital.example/rejected.pdf")["status"] == "rejected"


def test_empty_pdf_text_is_not_claimed_as_read(bundle, transport, monkeypatch):
    neutral(transport, raw=b"%PDF-1.7 invented image fixture", mime="application/pdf")
    monkeypatch.setattr(web, "_parse_pdf", lambda *args: ("", {"name": "invented_test_parser", "pages": 1, "ocr": False}))
    assert retrieve(bundle)["reason"] == "empty_extracted_text_no_ocr"


def test_real_installed_pdf_parser_extracts_tiny_invented_pdf(bundle, transport):
    fitz = pytest.importorskip("fitz")
    if not any(web.importlib.util.find_spec(name) for name in ("pypdf", "PyPDF2")):
        pytest.skip("No optional local PDF text parser")
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Invented source definition. No patient data.")
    raw = document.tobytes()
    document.close()
    neutral(transport, raw=raw, mime="application/pdf")
    result = retrieve(bundle)
    assert result["status"] == "accepted", result
    retrieval = result["provenance"]["retrieval"]
    assert retrieval["parser"]["name"] in {"pypdf", "PyPDF2"}
    assert retrieval["parser"]["version"]
    assert retrieval["parser"]["pages"] == 1 and retrieval["parser"]["ocr"] is False
    assert b"Invented source definition." in (bundle / retrieval["extracted_artifact"]["path"]).read_bytes()
    web.verify(bundle)


def test_real_pdf_metadata_exclusion_is_screened(bundle, transport):
    fitz = pytest.importorskip("fitz")
    if not any(web.importlib.util.find_spec(name) for name in ("pypdf", "PyPDF2")):
        pytest.skip("No optional local PDF text parser")
    document = fitz.open()
    document.new_page().insert_text((72, 72), "Neutral invented text.")
    document.set_metadata({"title": "Excluded Study REJECTED_SENTINEL"})
    raw = document.tobytes(deflate=True)
    document.close()
    neutral(transport, raw=raw, mime="application/pdf")
    result = retrieve(bundle)
    assert result["status"] == "rejected", result
    assert not (bundle / "sources/web_evidence_v1").exists()


def test_public_https_transport_connects_validated_ip_with_hostname_tls(monkeypatch):
    calls = []
    class Sock:
        def settimeout(self, value): assert 0 < value <= 5
        def connect(self, address): calls.append(("connect", address))
        def close(self): pass
    class Response:
        status = 200
        fp = None
        def getheaders(self): return [("Content-Type", "text/plain"), ("Content-Length", "3")]
        def read1(self, count):
            if getattr(self, "sent", False): return b""
            self.sent = True
            return b"abc"
    class Connection:
        sock = None
        def __init__(self, host, **kwargs): calls.append(("host", host))
        def request(self, method, path, headers): calls.append(("request", method, path))
        def getresponse(self): return Response()
        def close(self): pass
    class TLS:
        def wrap_socket(self, sock, server_hostname):
            calls.append(("tls", server_hostname))
            return sock
    monkeypatch.setattr(web.socket, "socket", lambda *args: Sock())
    monkeypatch.setattr(web.ssl, "create_default_context", lambda: TLS())
    monkeypatch.setattr(web.http.client, "HTTPSConnection", Connection)
    consumed = []
    status, headers, raw = web._http_once("https://publisher.example/path?q=1", [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
        time.monotonic() + 5, 10, consumed.append)
    assert raw == b"abc" and consumed == [3]
    assert ("connect", ("93.184.216.34", 443)) in calls
    assert ("tls", "publisher.example") in calls
    assert ("request", "GET", "/path?q=1") in calls

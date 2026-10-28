"""Task-bound adapter checks using only invented records and intercepted HTTP."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from cohort_harness import literature as adapter
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import freeze_candidate, verify_candidate

gateway = adapter.gateway


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


@pytest.fixture
def bundle(tmp_path):
    root = make_demo(tmp_path / "bundle")
    task = json.loads((root / "task.json").read_text())
    task["information_policy"]["allowed_tools"] = ["literature." + a for a in adapter.ACTIONS if a != "init"]
    task["information_policy"]["excluded_cohorts"] = ["Excluded study"]
    task["budget"].update(source_queries=3, source_downloads=3)
    write(root / "task.json", task)
    return root


def record():
    return {"id": "123", "source": "MED", "pmcid": "PMC123", "title": "Invented neutral paper",
            "abstractText": "An invented source used only to test gateway contracts."}


def search_raw(records=None):
    records = [record()] if records is None else records
    return gateway.encoded({"hitCount": len(records), "resultList": {"result": records}, "nextCursorMark": "next"})


def transport(supplement=b"name,value\nalpha,1\n", article_extra=""):
    article = (
        '<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><article-meta>'
        '<article-id pub-id-type="pmcid">PMC123</article-id><article-title>Invented source</article-title>'
        '</article-meta></front><body><p>Artificial fixture only. ' + article_extra + '</p>'
        '<supplementary-material><media xlink:href="supplement.csv"/></supplementary-material>'
        '</body><back><ref>Invented reference.</ref></back></article>').encode()
    def url(name, raw):
        return gateway.CLOUD + "/PMC123.1/" + name + "?md5=" + hashlib.md5(raw).hexdigest()
    xml_url, supp_url = url("PMC123.1.xml", article), url("supplement.csv", supplement)
    manifest = gateway.encoded({"pmcid": "PMC123", "version": 1, "xml_url": xml_url,
                                "media_urls": [supp_url], "title": "Invented article"})
    listing = b"<ListBucketResult><IsTruncated>false</IsTruncated><CommonPrefixes><Prefix>PMC123.1/</Prefix></CommonPrefixes></ListBucketResult>"
    def fake(url, *_):
        if url.startswith(gateway.API):
            return search_raw()
        if "list-type=" in url:
            return listing
        if url.endswith(".json"):
            return manifest
        if url == xml_url:
            return article
        if url == supp_url:
            return supplement
        raise AssertionError("Unexpected URL")
    return fake


def assert_no_rejected(root, result):
    assert "REJECTED_SENTINEL" not in json.dumps(result)
    for path in root.rglob("*"):
        if path.is_file():
            assert b"REJECTED_SENTINEL" not in path.read_bytes()


def test_init_binds_one_session_and_derives_budgets(bundle):
    result = adapter.run_literature(bundle, "init")
    assert result["status"] == "ok"
    assert result["budgets"] == {"queries": 3, "downloads": 3, "auxiliary_requests": 48}
    assert result["usage"]["http_attempts"] == 0
    state = (bundle / "gateway/session/state.json").read_bytes()
    again = adapter.run_literature(bundle, "init")
    assert again["usage"]["queries"] == 0
    assert json.loads(state)["created_utc"] == json.loads((bundle / "gateway/session/state.json").read_bytes())["created_utc"]


@pytest.mark.parametrize("mode,allowed,action", [
    ("prior_only", ["literature.search"], "init"),
    ("prior_only", ["literature.search"], "search"),
    ("published_evidence", [], "search"),
    ("published_evidence", ["literature.search"], "fetch"),
])
def test_permission_boundary_no_network(bundle, monkeypatch, mode, allowed, action):
    task = json.loads((bundle / "task.json").read_text())
    task["information_policy"].update(mode=mode, allowed_tools=allowed)
    write(bundle / "task.json", task)
    def never(*args):
        raise AssertionError("Network must not be touched")
    monkeypatch.setattr(gateway, "http_get", never)
    result = adapter.run_literature(bundle, action, query="invented", pmcid="PMC123")
    assert result["status"] == "error"
    assert not (bundle / "gateway").exists()


def test_task_change_does_not_reset_budget(bundle):
    assert adapter.run_literature(bundle, "init")["status"] == "ok"
    task = json.loads((bundle / "task.json").read_text())
    task["budget"]["source_queries"] += 1
    write(bundle / "task.json", task)
    result = adapter.run_literature(bundle, "init")
    assert result["status"] == "error"
    assert "binding changed" in result["detail"]
    assert json.loads((bundle / "gateway/session/state.json").read_text())["usage"]["queries"] == 0


def test_config_tamper_rejected(bundle):
    adapter.run_literature(bundle, "init")
    config = bundle / "gateway/config.json"
    config.write_bytes(config.read_bytes() + b" ")
    result = adapter.run_literature(bundle, "search", query="invented")
    assert result["status"] == "error"
    assert "configuration changed" in result["detail"]


def test_query_budget_is_cumulative_and_failures_count(bundle, monkeypatch):
    task = json.loads((bundle / "task.json").read_text())
    task["budget"]["source_queries"] = 1
    write(bundle / "task.json", task)
    calls = []
    def fail(*args):
        calls.append(args)
        raise gateway.GatewayError("network_or_timeout_failure")
    monkeypatch.setattr(gateway, "http_get", fail)
    first = adapter.run_literature(bundle, "search", query="invented")
    assert first["usage"]["queries"] == 1
    assert first["usage"]["http_successes"] == 0
    second = adapter.run_literature(bundle, "search", query="revision")
    assert second["reason"] == "budget_exhausted_queries"
    assert len(calls) == 1


def test_excluded_search_content_never_saved_or_returned(bundle, monkeypatch):
    bad = record()
    bad["abstractText"] = "Excluded study REJECTED_SENTINEL"
    monkeypatch.setattr(gateway, "http_get", lambda *args: search_raw([bad, record()]))
    result = adapter.run_literature(bundle, "search", query="invented", limit=2)
    assert result["status"] == "ok"
    assert result["accepted_count"] == 1 and result["rejected_count"] == 1
    assert len(result["registered_artifacts"]) == 1
    assert_no_rejected(bundle, result)


def test_empty_exclusion_list_is_valid_and_not_fake_rule(bundle, monkeypatch):
    task = json.loads((bundle / "task.json").read_text())
    task["information_policy"]["excluded_cohorts"] = []
    write(bundle / "task.json", task)
    monkeypatch.setattr(gateway, "http_get", lambda *args: search_raw())
    result = adapter.run_literature(bundle, "search", query="invented")
    assert result["status"] == "ok"
    assert json.loads((bundle / "gateway/config.json").read_text())["exclusions"] == {
        "compact_aliases": [], "regexes": []}


def test_registered_fetch_append_preserves_old_receipt_and_cache_idempotent(bundle, monkeypatch):
    candidate = bundle / "candidates/initial"
    receipt = freeze_candidate(bundle, candidate)
    old_entries = json.loads((bundle / "registry.json").read_text())["artifacts"]
    old_bytes = (candidate / "freeze.json").read_bytes()
    monkeypatch.setattr(gateway, "http_get", transport())
    result = adapter.run_literature(bundle, "fetch", pmcid="PMC123")
    assert result["status"] == "accepted", result
    assert result["usage"]["queries"] == 1
    assert result["usage"]["downloads"] == 1
    assert len(result["registered_artifacts"]) == 3
    entries = json.loads((bundle / "registry.json").read_text())["artifacts"]
    assert entries[:len(old_entries)] == old_entries
    assert all(x["source_id"] == "PMC123" and x["origin"] == "gateway" for x in entries[len(old_entries):])
    assert (candidate / "freeze.json").read_bytes() == old_bytes
    verify_candidate(bundle, candidate)
    before = (bundle / "registry.json").read_bytes()
    cached = adapter.run_literature(bundle, "fetch", pmcid="PMC123")
    assert cached["cached"] is True
    assert cached["usage"]["downloads"] == 1
    assert (bundle / "registry.json").read_bytes() == before
    assert receipt["registry_snapshot"]["artifact_count"] == len(old_entries)


def test_artifact_tamper_rejected_before_content_return(bundle, monkeypatch):
    monkeypatch.setattr(gateway, "http_get", transport())
    result = adapter.run_literature(bundle, "fetch", pmcid="PMC123")
    path = bundle / "gateway/session" / result["approved_artifact"]["session_relative_path"]
    path.write_text("REJECTED_SENTINEL", encoding="utf-8")
    output = adapter.run_literature(bundle, "fetch", pmcid="PMC123")
    assert output["status"] == "error"
    assert "REJECTED_SENTINEL" not in json.dumps(output)
    assert "hash changed" in output["detail"] or "size changed" in output["detail"]


def test_deleted_approval_event_rejects_cached_artifact(bundle, monkeypatch):
    monkeypatch.setattr(gateway, "http_get", transport())
    result = adapter.run_literature(bundle, "fetch", pmcid="PMC123")
    audit = bundle / "gateway/session/audit.jsonl"
    lines = [json.loads(x) for x in audit.read_text().splitlines()]
    target = result["approved_artifact"]
    lines = [x for x in lines if not (x.get("type") == "artifact_approved" and x.get("artifact") == target)]
    audit.write_text("".join(json.dumps(x) + "\n" for x in lines))
    output = adapter.run_literature(bundle, "fetch", pmcid="PMC123")
    assert output["status"] == "error"
    assert "approval event" in output["detail"]


def test_arbitrary_approved_file_is_not_registered(bundle, monkeypatch):
    adapter.run_literature(bundle, "init")
    arbitrary = bundle / "gateway/session/approved"
    arbitrary.mkdir()
    payload = b"Unapproved text"
    (arbitrary / (hashlib.sha256(payload).hexdigest() + ".txt")).write_bytes(payload)
    monkeypatch.setattr(gateway, "http_get", lambda *args: search_raw())
    output = adapter.run_literature(bundle, "search", query="invented")
    assert output["status"] == "ok"
    entries = json.loads((bundle / "registry.json").read_text())["artifacts"]
    assert all(x["sha256"] != hashlib.sha256(payload).hexdigest() for x in entries)


def test_supplement_fetch_registration_and_shared_budget(bundle, monkeypatch):
    task = json.loads((bundle / "task.json").read_text())
    task["budget"]["source_downloads"] = 2
    write(bundle / "task.json", task)
    monkeypatch.setattr(gateway, "http_get", transport())
    article = adapter.run_literature(bundle, "fetch", pmcid="PMC123")
    listing = adapter.run_literature(bundle, "list-supplements", pmcid="PMC123")
    item = listing["supplements"][0]["supplement_id"]
    supplement = adapter.run_literature(bundle, "fetch-supplement", pmcid="PMC123", supplement_id=item)
    assert supplement["status"] == "accepted", supplement
    assert supplement["usage"]["downloads"] == 2
    assert supplement["parent_xml_sha256"] == article["xml_artifact"]["sha256"]
    assert len(supplement["registered_artifacts"]) == 1
    blocked = adapter.run_literature(bundle, "fetch-supplement", pmcid="PMC123", supplement_id=item)
    assert blocked["reason"] == "budget_exhausted_downloads"


def test_excluded_supplement_never_saved_or_returned(bundle, monkeypatch):
    monkeypatch.setattr(gateway, "http_get", transport(b"name,value\nExcluded study,REJECTED_SENTINEL\n"))
    adapter.run_literature(bundle, "fetch", pmcid="PMC123")
    listing = adapter.run_literature(bundle, "list-supplements", pmcid="PMC123")
    result = adapter.run_literature(bundle, "fetch-supplement", pmcid="PMC123",
                                    supplement_id=listing["supplements"][0]["supplement_id"])
    assert result["status"] == "rejected"
    assert result["usage"]["downloads"] == 2
    assert_no_rejected(bundle, result)


def test_existing_registry_tamper_cannot_be_silently_repaired(bundle):
    registry = json.loads((bundle / "registry.json").read_text())
    registry["artifacts"][0]["sha256"] = "0" * 64
    write(bundle / "registry.json", registry)
    result = adapter.run_literature(bundle, "init")
    assert result["status"] == "error"
    assert "hash mismatch" in result["detail"]
    assert not (bundle / "gateway").exists()


def test_module_cli_uses_bound_bundle(bundle, capsys):
    code = adapter.main(["--bundle", str(bundle), "init"])
    output = json.loads(capsys.readouterr().out)
    assert code == 0 and output["status"] == "ok"
    assert output["session"] == "gateway/session"


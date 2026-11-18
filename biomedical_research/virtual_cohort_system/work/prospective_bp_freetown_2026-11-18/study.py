"""Prospective study entry point. Only reveal() decodes target outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
PRIOR = PROJECT / "work/evidence_composition_pilot_2026-11-16"
sys.path.insert(0, str(PRIOR))
import pilot as sandbox
sys.path.remove(str(PRIOR))
import analysis
import reference_arms

client = sandbox.client
client.MAX_OUTPUT = 16384
client.CAPS = {"openai": 0.75}
SEEDS = [18101, 18103, 18109]
ARMS = ["primary", "alternative", "statistical"]
CFG = "OA_SOL"
PRIVATE = ROOT / "private_runs"
CALLS = ROOT / "private_calls"
read, write, sha = sandbox.read, sandbox.write, sandbox.sha
FIELDS = ["SBP", "DBP"]


def check(test, reason):
    if not test:
        raise ValueError(reason)


def text_hash(path):
    # Public Git and the Windows checkout may use different newline conventions.
    normalized = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def task(n=10000):
    columns = [{"name": "person_id", "kind": "integer", "unit": "", "role": "identifier", "nullable": False}]
    columns.extend({"name": k, "kind": "number", "unit": "mmHg", "role": "generated",
                    "nullable": False} for k in FIELDS)
    t = {"schema_version": 1, "task_id": "prospective_west_african_pressure",
         "mode": "whole_cohort", "population": "Urban West African community screening participants age 40+",
         "row_id": "person_id", "n_rows": n, "columns": columns,
         "information_policy": {"mode": "published_evidence", "excluded_cohorts": [], "allowed_tools": []},
         "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    sandbox.contracts.validate_task(t)
    return t


def prompt():
    return (ROOT/"REQUEST.txt").read_text(encoding="utf8") + "\n" + (ROOT/"SOURCE.json").read_text(encoding="utf8")


def public_inputs():
    names = ["PLAN.md", "ADMISSION.json", "SOURCE.json", "REQUEST.txt", "analysis.py",
             "reference_arms.py", "study.py", "verify.py", "PREFLIGHT.json"]
    paths = [ROOT / x for x in names] + [PRIOR/"pilot.py", PROJECT/"cohort_harness/_worker.py",
             PROJECT/"cohort_harness/execution.py", PROJECT/"cohort_harness/contracts.py",
             PROJECT/"cohort_harness/lifecycle.py", PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_client.py",
             PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_preflight.py"]
    return {p.relative_to(PROJECT).as_posix(): text_hash(p) for p in paths}


def freeze():
    check(read(ROOT/"PREFLIGHT.json")["passed"], "Run mechanical preflight")
    write(ROOT/"FREEZE.json", {"time_utc": sandbox.now(), "files_lf_sha256": public_inputs(),
          "api": client.CONFIGS[CFG], "max_output_tokens": client.MAX_OUTPUT, "budget_usd": client.CAPS["openai"],
          "task": task(), "seeds": SEEDS, "execution_limits": sandbox.LIMITS,
          "boot_replicates": 2000, "boot_seed": 18127, "target_effect_accessed": False})


def bound():
    f = read(ROOT/"FREEZE.json")
    check(f["files_lf_sha256"] == public_inputs(), "Frozen file has changed")
    check(f["api"] == client.CONFIGS[CFG] and f["task"] == task() and f["seeds"] == SEEDS, "Dispatch mismatch")
    check(f["budget_usd"] == client.CAPS["openai"] and f["max_output_tokens"] == client.MAX_OUTPUT
          and f["execution_limits"] == sandbox.LIMITS, "Frozen budget mismatch")


def validate(obj):
    check(set(obj["model_spec"]) == {"primary", "alternative"}, "Expected two law specifications")
    check(all(isinstance(s, dict) and s for s in obj["model_spec"].values()), "Missing per-law parameters")
    rows = obj["decision_record"]["requested_estimands"]
    check(len(rows) == 2 and {r["name"] for r in rows} == {"Q1", "Q2"}, "Expected Q1 and Q2")
    for row in rows:
        check(row["source_status"] in {"reported","derived","underdetermined"}, "Invalid source status")
        check(all(isinstance(row.get(k), str) and row[k].strip() for k in ["transfer","sensitivity"]),
              "Missing target or sensitivity judgment")


def author():
    bound()
    check(not (ROOT/"CLOSURE.json").exists(), "Construction already closed")
    check(not (ROOT/"REVEAL.json").exists(), "Target already opened")
    name, q = "author01", prompt()
    if (CALLS/"calls"/name).exists():
        first = CALLS/"calls"/name
        check((first/"receipt.json").exists(), "An existing call may be in flight")
        # Only a confirmed mechanical problem qualifies for the frozen repair allowance.
        check((PRIVATE/"mechanical_issue.json").exists(), "Repair not authorized without recorded mechanical error")
        q += "\nA prior attempt failed the executable interface. Correct only the mechanical issue below; preserve the intended scientific model. Prior artifact and objective diagnostic:\n"
        q += (first/"response_text.txt").read_text(encoding="utf8") + "\n" + json.dumps(read(PRIVATE/"mechanical_issue.json"))
        name = "mechanical_repair"
    record, obj = client.call_once(CALLS, name, CFG, q)
    print({k: record.get(k) for k in ["status","returned_model","artifact_status","tariff_cost_usd","elapsed_seconds","api_error_code"]}, flush=True)
    if obj is None:
        if record.get("artifact_status") == "invalid" and name == "author01":
            write(PRIVATE/"mechanical_issue.json", {"error": record["mechanical_error"]})
        raise ValueError("No valid model artifact")
    try:
        validate(obj)
    except (ValueError, KeyError) as exc:
        if name == "author01":
            write(PRIVATE/"mechanical_issue.json", {"error": str(exc)})
        raise


def artifact_for(arm):
    src = read(ROOT/"SOURCE.json")
    if arm == "statistical":
        return (ROOT/"reference_arms.py").read_text(encoding="utf8"), src
    calls = CALLS/"calls"
    fold = calls/("mechanical_repair" if (calls/"mechanical_repair").exists() else "author01")
    obj = read(fold/"artifact.json")
    validate(obj)
    return obj["generator_py"], obj["model_spec"][arm]


def gen_close():
    bound()
    check(not (ROOT/"CLOSURE.json").exists() and not (ROOT/"REVEAL.json").exists(), "Study already closed")
    selected = []
    for arm in ARMS:
        code, model = artifact_for(arm)
        attempt = "repair" if (CALLS/"calls/mechanical_repair").exists() else "initial"
        c = ROOT/"candidates"/arm
        if attempt == "repair":
            c = ROOT/"candidates"/"repair"/arm
        c.mkdir(parents=True,exist_ok=True)
        spec = {"task": task(), "model": model}
        if not (c/"generator.py").exists():
            (c/"generator.py").write_text(code,encoding="utf8",newline="\n")
        if not (c/"model_spec.json").exists():
            write(c/"model_spec.json", spec)
        check((c/"generator.py").read_text(encoding="utf8") == code and read(c/"model_spec.json") == spec,
              "Candidate re-entry mismatch")
        for seed in SEEDS:
            loc = PRIVATE/attempt/arm/str(seed)
            result = read(loc/"execution.json") if (loc/"execution.json").is_file() else sandbox.isolated(c, task(), loc, seed)
            if result.get("status") != "success" and attempt == "initial" and arm != "statistical":
                if not (PRIVATE/"mechanical_issue.json").exists():
                    wr = loc/"output/worker_report.json"
                    diagnostic = read(wr).get("error") if wr.exists() and wr.stat().st_size else None
                    write(PRIVATE/"mechanical_issue.json",{"arm":arm,"seed":seed,
                          "error":diagnostic or result.get("error",{}).get("message","worker error")})
            check(result.get("status") == "success", f"Inspect retained isolated failure for {arm}/{seed}")
            check(sha(loc/"output/generated.csv") == result["generated_sha256"], "Unbound table")
            selected.append({"arm": arm, "seed": seed, "run_relative":loc.relative_to(PRIVATE).as_posix(),
                             "rows": task()["n_rows"], "csv_sha256": result["generated_sha256"],
                             "code_lf_sha256": text_hash(c/"generator.py"), "spec_lf_sha256": text_hash(c/"model_spec.json")})
    calls = CALLS/"calls"
    all_calls = sorted(calls.glob("*/receipt.json"))
    chosen = calls/("mechanical_repair" if (calls/"mechanical_repair").exists() else "author01")
    decision = read(chosen/"artifact.json")["decision_record"]
    write(ROOT/"DECISIONS.json", decision)
    costs = []
    for f in all_calls:
        v = read(f)
        costs.append({k: v.get(k) for k in ("call_id","requested_model","returned_model","started_utc","ended_utc",
                     "prompt_sha256","request_sha256","response_text.txt_sha256","artifact.json_sha256",
                     "status","artifact_status","usage","tariff_cost_usd","cost_interpretation")})
    write(ROOT/"CLOSURE.json", {"time_utc": sandbox.now(), "freeze_sha256": text_hash(ROOT/"FREEZE.json"),
          "decision_sha256": text_hash(ROOT/"DECISIONS.json"), "calls": costs, "tables": selected,
          "target_effect_accessed": False})


def preflight():
    import verify
    verify.fixtures()
    src = {"means":{"DBP":71., "SBP":109.}, "sd":{"SBP":13.,"DBP":8.},"pearson":0.72}
    mu, v = reference_arms.latent_parameters(src)
    m = np.exp(mu+np.diag(v)/2)
    cov = np.outer(m,m)*np.expm1(v)
    assert np.isclose(m.sum(),109.) and np.isclose(cov.sum(),13.**2)
    assert np.isclose(cov[0].sum()/(13*8),.72)
    c = PRIVATE/"fixture_candidate"
    c.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/"reference_arms.py", c/"generator.py")
    write(c/"model_spec.json", {"task":task(30), "model":src})
    rec = sandbox.isolated(c, task(30), PRIVATE/"fixture_run", 111)
    check(rec["status"]=="success",str(rec.get("error","fixture failed")))
    write(ROOT/"PREFLIGHT.json", {"time_utc": sandbox.now(),"passed":True,"target_read":False,
          "tests":["toy inclusive conjunction at both boundaries","two independent point estimators",
                   "stratified bootstrap implementation equivalence on toy data","statistical arm recovers toy source moments analytically",
                   "whole-cohort candidate executes and validates inside the production offline worker"]})


def reveal():
    bound()
    closure = read(ROOT/"CLOSURE.json")
    check(closure["freeze_sha256"] == text_hash(ROOT/"FREEZE.json") and
          closure["decision_sha256"] == text_hash(ROOT/"DECISIONS.json"), "Unbound pre-reveal decisions")
    check(len(closure["tables"]) == len(ARMS)*len(SEEDS), "Table closure incomplete")
    source = read(ROOT/"SOURCE.json")
    arms = {}
    for arm in ARMS:
        draws = []
        rows = []
        for b in [v for v in closure["tables"] if v["arm"] == arm]:
            p = PRIVATE/b["run_relative"]/"output/generated.csv"
            check(sha(p) == b["csv_sha256"], "Table hash changed")
            a = pd.read_csv(p)[FIELDS].to_numpy()
            check(len(a)==b["rows"], "Table row count changed")
            draws.append(a)
            rows.append({"seed":b["seed"], "result":analysis.summary(a)})
        totals = analysis.summary(np.concatenate(draws))
        arms[arm] = {"draws":rows, "pooled":totals, "source_check":analysis.source_checks(totals, source)}
    # The first target effect access is below this marker, after closure and artifact integrity checks.
    if not (ROOT/"REVEAL.json").exists():
        write(ROOT/"REVEAL.json", {"time_utc":sandbox.now(), "closure_sha256":text_hash(ROOT/"CLOSURE.json"),
              "plan_sha256":text_hash(ROOT/"PLAN.md"), "first_target_effect_access_authorized":True})
    target_file = read(ROOT/"ADMISSION.json")["files"][0]
    tp = ROOT/"private_reference"/target_file["name"]
    check(sha(tp) == target_file["sha256"], "Target release hash changed")
    target = analysis.load_target(tp)
    ref = analysis.summary(target[FIELDS].to_numpy())
    ref.pop("iid_mcse")
    ref["within_zone_intervals"] = analysis.zone_intervals(target)
    ref["zones"] = int(target.zone.nunique())
    ref["both_n"] = int(((target.SBP>=140)&(target.DBP>=90)).sum())
    for a in arms.values():
        a["signed_target_delta"] = {k: a["pooled"]["estimates"][k] - ref["estimates"][k] for k in ["Q1","Q2"]}
    pa, alt = [arms[x]["pooled"] for x in ARMS[:2]]
    gap = abs(pa["estimates"]["Q2"]-alt["estimates"]["Q2"])
    lower = gap - 4 * (pa["iid_mcse"]["Q2"]+alt["iid_mcse"]["Q2"])
    write(ROOT/"AGGREGATES.json", {"target":ref, "arms":arms, "direct":{"Q1":source["pearson"],"Q2":None},
          "scenarios":{"Q2_abs_gap":gap,"Q2_gap_minus_mc_allowance":lower,"operational_threshold":.02,
          "material_by_frozen_rule":bool(all(arms[x]["source_check"]["compatible"] for x in ARMS[:2]) and lower>.02)}})


if __name__ == "__main__":
    actions = {"preflight":preflight,"freeze":freeze,"author":author,"generate":gen_close,"reveal":reveal}
    p = argparse.ArgumentParser()
    p.add_argument("stage",choices=actions)
    actions[p.parse_args().stage]()

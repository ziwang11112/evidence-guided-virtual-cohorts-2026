"""Invented control receipts only; no generator, source fit or target-file read.

Temporary release approvals are explicitly test scaffolding, not real approvals.
Only the trusted runtime/file-verification boundary is replaced here.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

import campaign_control as cc


def h(value): return hashlib.sha256(value.encode()).hexdigest()


class InventedRuntime:
    def __init__(self):
        self.bindings = {}; self.modes = {}; self.authorizations = {}
        self.bad_feedback = False; self.ledger = None

    def add(self, case, constructor, stage, *, changed=True):
        bundle = str((self.ledger.directory.parent/(case+"-invented-bundle")).resolve())
        candidate = f"candidates/{case}_{constructor}_{stage}"
        version = "initial" if stage == "initial" or not changed else "changed-final"
        parent = {"candidate":candidate,"freeze_sha256":h(candidate),"task_sha256":h(case+"task"),
            "plan_sha256":h(candidate+"plan"),"generator_sha256":h(case+constructor+version),
            "model_spec_sha256":h(case+constructor+version+"spec"),"common_spec_sha256":h(case+constructor+version+"common"),
            "evidence_sha256":h(case+"same-packet")}
        contexts = [{"id":name,"role":"source","feedback_policy":"semantic_v1_plus_supplement"}
                    for name,_ in cc.SOURCES[case]]
        contexts += [{"id":cc.TARGETS[case],"role":"target","feedback_policy":"none"}]
        plan = {"trials":cc.stage_trials(case,constructor,stage),"contexts":contexts,"execution_limits":cc.LIMITS.copy(),
                "budget":{"source_attempts":len(cc.SOURCES[case]),"source_rows":5000*len(cc.SOURCES[case]),
                          "target_attempts":3,"target_rows":15000}}
        self.bindings[(bundle,candidate)] = dict(bundle=bundle,candidate=candidate,parent=parent,plan=plan)
        self.modes[(bundle,candidate)] = "success"
        return bundle,candidate

    def inspect(self,bundle,candidate): return copy.deepcopy(self.bindings[(bundle,candidate)])

    def verify(self,bundle,candidate,case):
        mode = self.modes[(bundle,candidate)]
        if mode == "interrupted": raise FileNotFoundError("Invented missing completion")
        bound = self.inspect(bundle,candidate)
        parts = Path(candidate).name.split("_")
        constructor,stage = parts[1],parts[2]
        # Real verification reads the dispatch authorization saved before execution.
        # It does not request another dispatch after the ledger has finished.
        key = (bundle,candidate)
        if key not in self.authorizations:
            self.authorizations[key] = self.ledger.verify_dispatch(case,constructor,stage,bundle,candidate)
        authorization = copy.deepcopy(self.authorizations[key])
        if mode == "wrong_authorization": authorization["stage_intent_sha256"] = h("another-ledger-intent")
        trials,guards = [],[]
        for t in bound["plan"]["trials"]:
            status = "timeout" if mode == "timeout" else "success"
            valid_guard = mode != "guard_failure"
            role = "target" if t["context_id"] == cc.TARGETS[case] else "source"
            trials.append(dict(trial_id=t["id"],context_id=t["context_id"],role=role,status=status,
                attempt_consumed=True,generation_link_verified=mode != "timeout",
                execution_sha256=h(t["id"]+"execution"),
                generated_table_sha256=h(t["id"]+"output") if mode != "timeout" else None))
            guards.append(dict(trial_id=t["id"],context_id=t["context_id"],role=role,
                guard_status="valid" if valid_guard else "invalid",trial_status=status,
                receipt_path="invented-not-a-real-artifact",receipt_sha256=h(t["id"]+"guard")))
        return {"parent":bound["parent"],"bridge":{"status":"complete" if mode=="success" else "finished_with_failures",
            "trials":trials,"attempts_consumed":len(trials),"completion_committed":True,
            "all_planned_trials_successful":mode not in {"timeout","guard_failure"},
            "all_planned_generation_links_verified":mode != "timeout"},
            "guards":{"kind":"verified_case_stage_guards","parent":bound["parent"],"case_id":case,
                "constructor":constructor,"stage":stage,"authorization":authorization,"trials":guards,
                "all_guards_valid":mode != "guard_failure","all_slots_successful":mode not in {"timeout","guard_failure"},
                "target_effects_computed":False}}

    def source_reports(self,bundle,candidate,case,verified):
        result = [{"trial_id":r["trial_id"],"context_id":r["context_id"],"role":"source",
                   "status":"verified_source_feedback" if r["status"]=="success" else "unavailable","reports":[]}
                  for r in verified["bridge"]["trials"] if r["role"]=="source"]
        if self.bad_feedback:
            result[0]["context_id"] = cc.TARGETS[case]
        return result


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    code = tmp_path/"invented_runtime.py"; code.write_text("# invented control fixture, no execution\n")
    evaluator = tmp_path/"invented_evaluator.py"; evaluator.write_text("# never called or imported\n")
    artifacts = [{"path":str(code.resolve()),"sha256":cc._file_hash(code)},
                 {"path":str(evaluator.resolve()),"sha256":cc._file_hash(evaluator)}]
    cases = {}
    for case in cc.CASES:
        cases[case] = {}
        for field in cc.CASE_BINDINGS:
            path = tmp_path/(case+"_"+field+".json")
            path.write_text(json.dumps({"invented":case+field}))
            sha = cc._file_hash(path)
            artifacts.append({"path":str(path.resolve()),"sha256":sha}); cases[case][field] = sha
    manifest = {"schema_version":1,"kind":"wave_a_global_clinical_release","campaign_id":"INVENTED_CONTROL_TEST_ONLY",
        "status":"released","released_utc":"2000-01-01T00:00:00Z","ledger_directory":str((tmp_path/"ledger").resolve()),
        "designated_evaluator":artifacts[1].copy(),"schedule_sha256":cc.digest(cc.fixed_schedule()),
        "cases":cases,"artifacts":artifacts,"review":{}}
    def approve(value):
        value["review"] = dict(decision="approved",independent=True,reviewer_id="invented-reviewer",
            producer_id="invented-producer",reviewed_utc="2000-01-01T00:00:00Z",reason="Invented test scaffolding only",
            approved_sha256=cc.release_digest(value))
        return value
    approve(manifest)
    monkeypatch.setattr(cc,"_required_runtime_paths",lambda:{code.resolve()})
    runtime = InventedRuntime()
    monkeypatch.setattr(cc,"_inspect",runtime.inspect)
    monkeypatch.setattr(cc,"_verify_stage",runtime.verify)
    monkeypatch.setattr(cc,"_source_reports",runtime.source_reports)
    ledger = cc.CampaignLedger.create(tmp_path/"ledger",manifest); runtime.ledger = ledger
    return ledger,runtime,manifest,approve


def start(fixture,case="K01",constructor="A01",stage="initial",mode="success",changed=True):
    ledger,runtime,_,_ = fixture
    if stage=="initial": ledger.begin_construction(case,constructor,case+"-"+constructor+"-invented-science")
    bundle,candidate = runtime.add(case,constructor,stage,changed=changed)
    ledger.bind_stage(case,constructor,stage,bundle,candidate,derivation_mode="inline_deterministic")
    ledger.begin_bridge(case,constructor,stage)
    runtime.modes[(bundle,candidate)] = mode
    outcome = ledger.finish_bridge(case,constructor,stage)
    return bundle,candidate,outcome


@pytest.mark.parametrize("defect",["not_released","missing_case","wrong_schedule","self_review","missing_runtime",
    "case_hash_omitted","wrong_evaluator_type","wrong_evaluator_binding"])
def test_release_requirements_reject_before_operations(fixture,defect):
    _,_,manifest,approve = fixture
    value = copy.deepcopy(manifest)
    if defect=="not_released": value["status"]="design_only"
    elif defect=="missing_case": value["cases"].pop("K02")
    elif defect=="wrong_schedule": value["schedule_sha256"]=h("other-schedule")
    elif defect=="missing_runtime": value["artifacts"].pop(0)
    elif defect=="case_hash_omitted": value["cases"]["K01"]["task_template_sha256"]=h("unbound")
    elif defect=="wrong_evaluator_type": value["designated_evaluator"]=value["artifacts"][2].copy()
    elif defect=="wrong_evaluator_binding": value["designated_evaluator"]["sha256"]=h("not-current")
    approve(value)
    if defect=="self_review": value["review"]["reviewer_id"]=" Invented-Producer "
    with pytest.raises(cc.ControlError): cc.validate_release(value)


def test_release_bound_to_single_ledger_and_copy_cannot_reset_budget(fixture,tmp_path):
    ledger,_,manifest,_ = fixture
    with pytest.raises(cc.ControlError,match="exactly one ledger"):
        cc.CampaignLedger.create(tmp_path/"fresh-budget",manifest)
    copied=tmp_path/"copied-ledger"; shutil.copytree(ledger.directory,copied)
    with pytest.raises(cc.ControlError,match="different ledger"):
        cc.CampaignLedger.open(copied)
    with pytest.raises(FileExistsError): cc.CampaignLedger.create(ledger.directory,manifest)


@pytest.mark.parametrize("case,source_slots",[("K01",2),("K02",6)])
@pytest.mark.parametrize("failure",["timeout","interrupted","guard_failure","wrong_authorization"])
def test_failed_and_interrupted_stage_allocation_consumed_no_retry(fixture,case,source_slots,failure):
    ledger,runtime,_,_=fixture
    bundle,candidate,result=start(fixture,case=case,mode=failure)
    assert result["payload"]["status"] != "success"
    assert ledger.snapshot()["stage_allocation_debits"][case] == dict(source_slots=source_slots,target_slots=3,
                                                                    source_rows=source_slots*5000,target_rows=15000)
    with pytest.raises(cc.ControlError): ledger.begin_bridge(case,"A01","initial")
    with pytest.raises(cc.ControlError): ledger.bind_stage(case,"A01","initial",bundle,candidate)
    reopened=cc.CampaignLedger.open(ledger.directory)
    with pytest.raises(cc.ControlError): reopened.begin_bridge(case,"A01","initial")
    with pytest.raises(cc.ControlError): ledger.verify_dispatch(case,"A01","initial",bundle,candidate)
    if failure=="wrong_authorization":
        assert result["payload"]["status"]=="verification_failed"
        packet=ledger.deliver_source_feedback(case,"A01")
        assert all(r["status"]=="unavailable" for r in packet["reports"])


def test_dispatch_requires_actual_bound_parent_and_durable_intent(fixture):
    ledger,runtime,_,_=fixture
    ledger.begin_construction("K01","A01","invented")
    bundle,candidate=runtime.add("K01","A01","initial")
    ledger.bind_stage("K01","A01","initial",bundle,candidate)
    with pytest.raises(cc.ControlError,match="intent"): ledger.verify_dispatch("K01","A01","initial",bundle,candidate)
    ledger.begin_bridge("K01","A01","initial")
    auth=cc.verify_dispatch(ledger.directory,"K01","A01","initial",bundle,candidate)
    assert auth["parent_binding"]==runtime.bindings[(bundle,candidate)]["parent"]
    runtime.bindings[(bundle,candidate)]["parent"]["generator_sha256"]=h("tampered-code")
    with pytest.raises(cc.ControlError): ledger.verify_dispatch("K01","A01","initial",bundle,candidate)
    assert ledger.finish_bridge("K01","A01","initial")["payload"]["status"]=="verification_failed"


@pytest.mark.parametrize("defect",["target_feedback","wrong_seed","wrong_rows","extra_trial"])
def test_frozen_schedule_and_no_target_feedback(fixture,defect):
    ledger,runtime,_,_=fixture
    ledger.begin_construction("K01","A01","invented")
    bundle,candidate=runtime.add("K01","A01","initial")
    plan=runtime.bindings[(bundle,candidate)]["plan"]
    if defect=="target_feedback": plan["contexts"][-1]["feedback_policy"]="semantic_v1"
    elif defect=="wrong_seed": plan["trials"][0]["seed"]=999
    elif defect=="wrong_rows": plan["trials"][0]["n_rows"]=5001
    elif defect=="extra_trial": plan["trials"].append(copy.deepcopy(plan["trials"][0]))
    with pytest.raises(cc.ControlError): ledger.bind_stage("K01","A01","initial",bundle,candidate)


def test_source_feedback_exact_once_and_target_entries_rejected(fixture):
    ledger,runtime,_,_=fixture
    start(fixture)
    runtime.bad_feedback=True
    with pytest.raises(cc.ControlError): ledger.deliver_source_feedback("K01","A01")
    runtime.bad_feedback=False
    packet=ledger.deliver_source_feedback("K01","A01")
    assert len(packet["reports"])==2 and packet["target_feedback"] is False
    assert all(r["role"]=="source" for r in packet["reports"])
    with pytest.raises(cc.ControlError): ledger.deliver_source_feedback("K01","A01")


def test_s01_retention_aliases_exact_initial_outputs_and_never_runs_final(fixture):
    ledger,_,_,_=fixture
    _,_,initial=start(fixture,constructor="S01")
    ledger.deliver_source_feedback("K01","S01")
    with pytest.raises(cc.ControlError): ledger.decide_final("K01","S01","revise","not allowed")
    with pytest.raises(cc.ControlError): ledger.decide_final("K01","S01","stop","validS01mustretain")
    ledger.decide_final("K01","S01","retain","precommitted")
    closed=ledger.close_constructor("K01","S01","retained")
    original={t["trial_id"]:t for t in initial["payload"]["verified"]["bridge"]["trials"]}
    for entry in closed["payload"]["final_inventory"]:
        assert entry["disposition"]=="retained_alias"
        assert entry["verified_trial"]==original[entry["alias_of"]]
    assert ledger.snapshot()["stage_allocation_debits"]["K01"]["target_slots"]==3


def test_changed_final_failure_cannot_fallback_or_get_another_revision(fixture):
    ledger,_,_,_=fixture
    start(fixture); ledger.deliver_source_feedback("K01","A01")
    ledger.decide_final("K01","A01","revise","one source-informed revision")
    start(fixture,stage="final",mode="timeout")
    closed=ledger.close_constructor("K01","A01","final failed, retained as failure")
    assert all(x["disposition"]=="changed_final" and x["alias_of"] is None and x["stage_status"]!="success"
               for x in closed["payload"]["final_inventory"])
    with pytest.raises(cc.ControlError): ledger.decide_final("K01","A01","retain","fallback forbidden")
    assert ledger.snapshot()["stage_allocation_debits"]["K01"]["target_slots"]==6


def test_agent_cannot_retain_failed_stage_or_dispatch_after_stop(fixture):
    ledger,runtime,_,_=fixture
    start(fixture,mode="guard_failure"); ledger.deliver_source_feedback("K01","A01")
    with pytest.raises(cc.ControlError,match="whole-stage"):
        ledger.decide_final("K01","A01","retain","invalid outputs cannot alias")
    ledger.begin_construction("K01","A02","invented-bound-then-stopped")
    bundle,candidate=runtime.add("K01","A02","initial")
    ledger.bind_stage("K01","A02","initial",bundle,candidate)
    ledger.decide_final("K01","A02","stop","prospective stop before dispatch")
    with pytest.raises(cc.ControlError,match="closed by the final decision"):
        ledger.begin_bridge("K01","A02","initial")
    assert ledger.snapshot()["stage_allocation_debits"]["K01"]["source_slots"]==2


@pytest.mark.parametrize("defect",["same_scientific_bytes","different_evidence"])
def test_version_change_cannot_resample_same_science_or_change_shared_packet(fixture,defect):
    ledger,runtime,_,_=fixture
    start(fixture); ledger.deliver_source_feedback("K01","A01")
    ledger.decide_final("K01","A01","revise","one revision")
    bundle,candidate=runtime.add("K01","A01","final",changed=defect!="same_scientific_bytes")
    if defect=="different_evidence": runtime.bindings[(bundle,candidate)]["parent"]["evidence_sha256"]=h("extra-private-evidence")
    with pytest.raises(cc.ControlError): ledger.bind_stage("K01","A01","final",bundle,candidate)


def test_separate_analytic_jobs_unavailable_and_cannot_accept_external_receipts(fixture):
    ledger,runtime,_,_=fixture
    with pytest.raises(cc.ControlError,match="UNAVAILABLE"): ledger.reserve_analytic_job("K01","S01",{"success":True})
    ledger.begin_construction("K01","S01","invented")
    bundle,candidate=runtime.add("K01","S01","initial")
    with pytest.raises(cc.ControlError,match="UNAVAILABLE"):
        ledger.bind_stage("K01","S01","initial",bundle,candidate,derivation_mode="separate_analytic_job")


def test_both_wave_a_inventories_must_close_before_designated_evaluator_reveal(fixture):
    ledger,_,manifest,_=fixture
    for case in cc.CASES:
        for constructor in cc.CONSTRUCTORS:
            ledger.begin_construction(case,constructor,case+constructor+"-invented-stop")
            ledger.decide_final(case,constructor,"stop","Invented authoring failure; no clinical work")
            ledger.close_constructor(case,constructor,"Unrun outputs remain in denominator")
        if case=="K01":
            with pytest.raises(cc.ControlError,match="BOTH"): ledger.close_wave_a()
            with pytest.raises(cc.ControlError): ledger.authorize_target_reveal(manifest["designated_evaluator"]["sha256"])
    wave=ledger.close_wave_a()
    assert len(wave["payload"]["closed_inventory"])==12 and wave["payload"]["final_target_slots"]==36
    assert wave["payload"]["reserved_initial_and_final_target_slots"]==72
    assert sum(sum(e["role"]=="target" for e in c["final_inventory"])
               for c in wave["payload"]["closed_inventory"].values())==36
    with pytest.raises(cc.ControlError): ledger.authorize_target_reveal(manifest["artifacts"][0]["sha256"])
    grant=ledger.authorize_target_reveal(manifest["designated_evaluator"]["sha256"])
    assert grant["cases"]==["K01","K02"] and grant["target_data_read_by_controller"] is False
    with pytest.raises(cc.ControlError): ledger.authorize_target_reveal(manifest["designated_evaluator"]["sha256"])
    with pytest.raises(cc.ControlError): ledger.begin_construction("K01","A01","new-after-disclosure")


def test_exact_cross_case_maximums_with_five_revisions_and_s01_aliases(fixture):
    ledger,_,_,_=fixture
    for case in cc.CASES:
        for constructor in cc.CONSTRUCTORS:
            start(fixture,case,constructor)
            ledger.deliver_source_feedback(case,constructor)
            decision="retain" if constructor=="S01" else "revise"
            ledger.decide_final(case,constructor,decision,"Invented fixed decision")
            if decision=="revise": start(fixture,case,constructor,"final")
            ledger.close_constructor(case,constructor,"Invented closure")
    snapshot=ledger.snapshot()
    assert snapshot["stage_allocation_debits"]==cc.fixed_schedule()["per_case_maximum_new"]
    assert snapshot["actual_observed_counts"]["K01"]["verified_generated_tables"]==55
    assert snapshot["actual_observed_counts"]["K02"]["verified_generated_tables"]==99


def test_ledger_event_tampering_and_released_code_change_fail_closed(fixture):
    ledger,_,manifest,_=fixture
    ledger.begin_construction("K01","A01","invented")
    event_path=ledger.directory/"events"/"000000.json"
    event=json.loads(event_path.read_text()); event["payload"]["construction_id"]="rewritten"
    event_path.write_text(json.dumps(event))
    with pytest.raises(cc.ControlError,match="digest"): cc.CampaignLedger.open(ledger.directory)
    Path(manifest["artifacts"][0]["path"]).write_text("# changed released code")
    with pytest.raises(cc.ControlError,match="bytes changed"): cc.validate_release(manifest)

"""Read-only replay from published artifacts; optionally supply the public target workbook."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from analysis import load_target, summary, zone_intervals
from model_audit import audit

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT/name).read_text(encoding="utf8"))


def digest(name):
    return hashlib.sha256((ROOT/name).read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def main(workbook):
    freeze, closure, reveal = (read(f) for f in ["FREEZE.json","CLOSURE.json","REVEAL.json"])
    assert freeze["time_utc"] < closure["calls"][0]["started_utc"] < closure["time_utc"] < reveal["time_utc"]
    assert digest("FREEZE.json")==closure["freeze_sha256"] and digest("DECISIONS.json")==closure["decision_sha256"]
    assert digest("CLOSURE.json")==reveal["closure_sha256"] and digest("PLAN.md")==reveal["plan_sha256"]
    for path, expected in freeze["files_lf_sha256"].items():
        assert digest(ROOT.parents[1]/path)==expected, path
    src, result, exact = read("SOURCE.json"),read("AGGREGATES.json"),read("MODEL_AUDIT.json")
    assert closure["time_utc"] <= exact["time_utc"] < reveal["time_utc"] and not exact["target_reveal_existed_at_audit"]
    assert sorted(x["name"] for x in read("DECISIONS.json")["requested_estimands"])==["Q1","Q2"]
    expected_moments=[src["means"]["SBP"],src["means"]["DBP"],src["sd"]["SBP"],src["sd"]["DBP"],src["pearson"]]
    for name, arm in result["arms"].items():
        spec = read(f"candidates/{name}/model_spec.json")["model"]
        weights,offsets=(spec["component_weights"],spec["component_mean_offsets_dbp_pulse"]) if name!="statistical" else ([1.],[[0.,0.]])
        check=audit(weights,offsets,src)
        np.testing.assert_allclose([check[k] for k in ["Q1","Q2"]],
                                   [exact["population"][name][k] for k in ["Q1","Q2"]],atol=1e-12,rtol=0)
        values, se = arm["pooled"]["estimates"],arm["pooled"]["iid_mcse"]
        assert all(abs(values[k]-v)<=src["rounding_half_unit"]+4*se[k] for k,v in zip(["mean_s","mean_d","sd_s","sd_d","Q1"],expected_moments))
        assert arm["pooled"]["nonpositive"] == arm["pooled"]["unordered"] == 0
        b=[x for x in closure["tables"] if x["arm"]==name]
        assert sorted(x["seed"] for x in b)==freeze["seeds"]
        assert all(x["code_lf_sha256"]==digest(f"candidates/{name}/generator.py") and x["spec_lf_sha256"]==digest(f"candidates/{name}/model_spec.json") for x in b)
        for k in ["Q1","Q2"]:
            np.testing.assert_allclose(arm["signed_target_delta"][k],values[k]-result["target"]["estimates"][k],atol=1e-12,rtol=0)
    a,b=(result["arms"][k]["pooled"] for k in ["primary","alternative"])
    gap=abs(a["estimates"]["Q2"]-b["estimates"]["Q2"])
    lower=gap-4*(a["iid_mcse"]["Q2"]+b["iid_mcse"]["Q2"])
    np.testing.assert_allclose([gap,lower],[result["scenarios"]["Q2_abs_gap"],result["scenarios"]["Q2_gap_minus_mc_allowance"]],atol=1e-12,rtol=0)
    assert (lower>.02)==result["scenarios"]["material_by_frozen_rule"]
    if workbook:
        path=Path(workbook)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==read("ADMISSION.json")["files"][0]["sha256"]
        df=load_target(path)
        measured=summary(df[["SBP","DBP"]])
        assert len(df)==result["target"]["n"]
        for k in ["Q1","Q2"]:
            np.testing.assert_allclose(measured["estimates"][k],result["target"]["estimates"][k],rtol=0,atol=1e-12)
        for k,ci in zone_intervals(df).items():
            np.testing.assert_allclose(ci,result["target"]["within_zone_intervals"][k],rtol=0,atol=1e-12)
        a,b=df.SBP>=140, df.DBP>=90
        for label,count in [("neither",(~a&~b).sum()),("both",(a&b).sum()),("systolic_only",(a&~b).sum()),("diastolic_only",(~a&b).sum())]:
            assert read("REFERENCE_AUDIT.json")["counts"]["eligible"][label]==int(count)
    print("Verified protocol chronology, candidate hashes, source constraints, threshold integrals and frozen comparisons.")
    if workbook:
        print("Verified the workbook hash, target sample, both outcomes, bootstrap intervals and discordant-cell counts.")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--workbook",type=Path)
    main(parser.parse_args().workbook)

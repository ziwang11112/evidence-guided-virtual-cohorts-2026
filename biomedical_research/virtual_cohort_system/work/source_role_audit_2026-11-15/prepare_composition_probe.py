"""Prepare artificial evidence-composition tasks and check identification algebra.

No model requests, generator execution, real data, or saved synthetic row tables.
The generated 24 plan entries are unexecuted session slots, not experiments.
"""
import hashlib
import json
import math
import random
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "composition_probe"
CONDITIONS = ("none", "anchor_only", "bridge_only", "combined")

def partial(r):
    s = r[:2, :2] - r[:2, 2:3] @ r[2:3, :2] / r[2, 2]
    return float(s[0, 1] / math.sqrt(s[0, 0] * s[1, 1]))

def corr(a, i, j):
    return float(a[i, j] / math.sqrt(a[i, i] * a[j, j]))

def partial_matrix(r_xy, r_xz, r_yz):
    return np.array([[1, r_xy, r_xz], [r_xy, 1, r_yz], [r_xz, r_yz, 1]], float)

def longitudinal_matrix(bcov, ecov):
    b = np.array([[4., bcov], [bcov, 4.]])
    e = np.array([[1., ecov], [ecov, 1.]])
    return np.block([[b + e, b], [b, b + e]])

def change_r(s):
    d = np.array([[-1, 0, 1, 0], [0, -1, 0, 1]], float)
    return corr(d @ s @ d.T, 0, 1)

worlds = {
    "adjusted": {
        "base": partial_matrix(.5, .6, .6),
        "same_anchor": partial_matrix(.5, .2, .2),
        "same_bridge": partial_matrix(.7, .6, .6),
    },
    "longitudinal": {
        "base": longitudinal_matrix(3.2, -.6),
        "same_anchor": longitudinal_matrix(3.2, .6),
        "same_bridge": longitudinal_matrix(1.8, .8),
    },
}
checks = []
def check(name, condition, detail=None):
    checks.append({"name": name, "pass": bool(condition), "detail": detail})

for family, variants in worlds.items():
    for name, matrix in variants.items():
        eigen = np.linalg.eigvalsh(matrix)
        check(f"{family}/{name}/positive_definite", eigen.min() > 0, eigen.tolist())
        # A separate projection calculation checks the adjusted-correlation formula.
        if family == "adjusted":
            v = np.eye(3)[:2] - matrix[:2, 2:3] @ np.array([[0., 0., 1.]])
            check(f"{family}/{name}/projection_identity", abs(partial(matrix)-corr(v@matrix@v.T, 0, 1)) < 1e-12)
        else:
            ecov = (matrix[:2, :2]-matrix[:2, 2:])
            check(f"{family}/{name}/change_identity", abs(change_r(matrix)-corr(ecov, 0, 1)) < 1e-12)

a = worlds["adjusted"]
check("adjusted/anchor_equal_but_primary_different", a["base"][0,1] == a["same_anchor"][0,1] and abs(partial(a["base"])-partial(a["same_anchor"])) > .1)
check("adjusted/bridge_equal_but_primary_different", np.array_equal(a["base"][:2,2], a["same_bridge"][:2,2]) and abs(partial(a["base"])-partial(a["same_bridge"])) > .1)
check("adjusted/combined_identifies_primary", abs(partial(a["base"])-(.5-.6*.6)/math.sqrt((1-.6**2)*(1-.6**2))) < 1e-12)
b = worlds["longitudinal"]
check("longitudinal/anchor_equal_but_primary_different", np.array_equal(b["base"][:2,2:], b["same_anchor"][:2,2:]) and abs(change_r(b["base"])-change_r(b["same_anchor"])) > .1)
check("longitudinal/bridge_equal_but_primary_different", np.allclose(b["base"][:2,:2], b["same_bridge"][:2,:2]) and abs(change_r(b["base"])-change_r(b["same_bridge"])) > .1)
check("longitudinal/combined_identifies_primary", abs(change_r(b["base"])-(5*.52-4*.8)) < 1e-12)

packets = {
    "adjusted": {
        "request": "Generate a joint table of standardized quantitative variables X, Y and measured covariate Z for analysis of the X-Y Pearson residual correlation after separate linear adjustment for an intercept and Z. Also support the marginal X-Y correlation and the X-on-Z slope. Choose your generator. Report which requested functionals are identified by the records and which need assumptions; completing an honest point scenario is allowed.",
        "common_record": {"record_id": "C", "status": "artificial mathematical record, not a clinical publication", "population": "one common hypothetical population", "variables": ["X", "Y", "Z"], "means": [0,0,0], "individual_variances": [1,1,1], "uncertainty": "These are exact population moments in this controlled exercise, not finite-study estimates."},
        "anchor": {"record_id": "A", "status": "artificial mathematical record, not a clinical publication", "population": "same hypothetical population", "operator": "marginal Pearson correlation, no covariate adjustment", "variables": ["X","Y"], "value": .5},
        "bridge": {"record_id": "B", "status": "artificial mathematical record, not a clinical publication", "population": "same hypothetical population", "operator": "marginal Pearson correlations with measured covariate Z", "pairs": [["X","Z",.6],["Y","Z",.6]]},
    },
    "longitudinal": {
        "request": "Generate two visits per person for standardized quantitative biomarkers X and Y. Primary analysis: Pearson correlation of within-person changes X_visit2-X_visit1 and Y_visit2-Y_visit1. Secondary analyses: same-visit X-Y correlation and correlation of X_visit1 with Y_visit2. Choose your generator. Report which requested functionals are identified by the records and which need assumptions; completing an honest point scenario is allowed.",
        "common_record": {"record_id": "C", "status": "artificial mathematical record, not a clinical publication", "population": "one common hypothetical repeated-measure population", "measurement_model": "Each visit measurement is a stable person-specific component plus a mean-zero visit deviation. Component and deviation are independent. Different visits have independent deviations. Persons are independent. These are stipulated controlled-task assumptions, not biological claims.", "means": [0,0], "between_person_variances": [4,4], "within_person_variances": [1,1], "uncertainty": "Exact population moments for this exercise. No finite-study precision is claimed."},
        "anchor": {"record_id": "A", "status": "artificial mathematical record, not a clinical publication", "population": "same hypothetical population", "operator": "Pearson correlation between stable person-specific X and Y components", "value": .8},
        "bridge": {"record_id": "B", "status": "artificial mathematical record, not a clinical publication", "population": "same hypothetical population", "operator": "Pearson correlation of X and Y measured at the same visit", "value": .52},
    },
}

OUT.mkdir(parents=True, exist_ok=True)
slots = []
for family, objects in packets.items():
    for condition in CONDITIONS:
        for author in range(1, 4):
            evidence = [objects["common_record"]]
            selected = []
            if condition in ("anchor_only", "combined"):
                selected.append(objects["anchor"])
            if condition in ("bridge_only", "combined"):
                selected.append(objects["bridge"])
            if condition == "combined" and (author + (family == "longitudinal")) % 2:
                selected.reverse()
            evidence += selected
            # No treatment labels, witness worlds, expected answer or old clinical result in author payload.
            payload = {"request": objects["request"], "evidence_records": evidence,
                       "boundary": "This is an artificial evidence-composition task, not biomedical validation. Use these records only. No internet retrieval is needed for this controlled diagnostic. Scientific model and missing relationships are your choices; do not present assumptions as measured facts."}
            filename = f"{family}_{condition}_{author}.json"
            data = (json.dumps(payload, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
            (OUT/filename).write_bytes(data)
            slots.append({"family": family, "condition": condition, "author_repetition": author,
                          "payload": filename, "sha256": hashlib.sha256(data).hexdigest(),
                          "execution_status": "not_started"})
random.Random(20261115).shuffle(slots)
for i, s in enumerate(slots, 1):
    s["dispatch_order"] = i

phi = lambda x: math.exp(-x*x/2)/math.sqrt(2*math.pi)
Phi = lambda x: (1+math.erf(x/math.sqrt(2)))/2
postselect_slope = 1 + phi(1)/Phi(1)-phi(0)/Phi(0)
check("postselection_counterexample_not_identity", 0 < postselect_slope < .6)
result = {
    "status": "mathematical_preflight_complete_not_an_agent_experiment",
    "checks": checks,
    "failure_count": sum(not c["pass"] for c in checks),
    "witness_worlds": {f:{k:{"covariance":v.tolist(),"primary":partial(v) if f=="adjusted" else change_r(v)} for k,v in variants.items()} for f,variants in worlds.items()},
    "postselection_counterexample": {
        "definition": "Keep X fixed at 0 or 1 with equal probability; redraw Y=X+N(0,1) until Y>0. This is a separate algebraic witness, not execution of any old candidate.",
        "preselection_slope": 1,
        "postselection_binary_X_slope": postselect_slope,
        "meaning": "Proves that outcome-dependent redraws need not preserve a structural slope. It does not quantify the old candidate's effect size."
    },
    "limits": [
        "Witness pairs show nonidentification, not the entire identified set or calibrated uncertainty.",
        "Different evidence arms test information composition, not superiority over another Agent workflow.",
        "In partial-information cells a disclosed point scenario is valid; disagreement with one hidden completion is not by itself an error.",
        "Only the combined cell identifies both primary analyses; exact toy records omit real extraction, sampling and transport uncertainty.",
        "No new generative rows or model responses were produced."
    ]
}
plan = {"status":"prepared_not_launched", "session_slots":24, "executed_sessions":0,
        "families":2, "conditions":list(CONDITIONS), "constructors_per_cell":3,
        "model":"one existing economical GPT configuration; exact returned model and tariff must be pinned at launch",
        "change_from_previous_proposal":"Uses complementary anchor/bridge evidence rather than assuming indirect evidence is harmful. Both records are true and can be useful in different roles.",
        "remaining_launch_requirements":["Finish and review response/table schema and evaluator", "Bind existing isolated execution adapter", "Pin runtime/model/token budget and tariff reservation", "Freeze immutable launch manifest before first API call"],
        "slots":slots}
(OUT/"HOST_ONLY_PREFLIGHT.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(OUT/"PLAN.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"passed":len(checks)-result["failure_count"], "failed":result["failure_count"], "prepared_slots":len(slots), "executed_sessions":0,
                  "postselection_counterexample_slope":postselect_slope,
                  "primary_witnesses":{f:{k:round(partial(v) if f=='adjusted' else change_r(v),8) for k,v in w.items()} for f,w in worlds.items()}},indent=2))
if result["failure_count"]:
    raise SystemExit("Mathematical preflight failed")

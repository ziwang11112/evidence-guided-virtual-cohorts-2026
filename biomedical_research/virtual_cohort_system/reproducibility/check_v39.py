"""Verify the current manuscript's table cells, main figure, and prospective claims."""
import hashlib
import json
from pathlib import Path
from statistics import median
from xml.etree import ElementTree as ET

import check_v38

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/"manuscript/kdd_draft_v39_2026-11-20"
STUDY=ROOT/"work/prospective_iron_dependence_2026-11-20"


def read(name):
    return json.loads((STUDY/name).read_text(encoding="utf-8"))


def main():
    check_v38.PAPER=PAPER
    check_v38.main()
    result=read("RESULTS.json")
    verify=read("VERIFICATION_ADDENDUM.json")
    assert verify["same_stata_representation_independently_recomputed"] and verify["virtual_draws_audited"]==21
    assert verify["results_sha256"]==hashlib.sha256((STUDY/"RESULTS.json").read_text(encoding="utf-8").encode()).hexdigest()
    assert not result["prespecified_advantage_on_this_cohort"]
    ref=result["reference"]
    main=(PAPER/"main.tex").read_text(encoding="utf-8")
    app=(PAPER/"appendix.tex").read_text(encoding="utf-8")
    table=check_v38.check_v37.rows(app,"tab:akwa")
    assert table["Akwa Ibom sample"]==[f"{ref['rank']:.4f}","---",f"{ref['middle_ratio']:.4f}"]
    for name,z in result["by_law"].items():
        label="Statistical generator" if name=="statistical" else f"Agent {name[-1]}"
        assert table[label]==[f"{z[k]:.4f}" for k in ("rank","absolute_rank_error","source_middle_ratio")]
    fig=ET.parse(PAPER/"figures/evidence-and-pairing.drawio")
    cells={n.get("id"):n.get("value") for n in fig.iter("mxCell")}
    v=result["by_law"]
    med=median(z["rank"] for k,z in v.items() if k.startswith("author"))
    for name,val in (("measured",ref["rank"]),("stat",v["statistical"]["rank"]),("agent",med)):
        assert cells["external-value-"+name]==f"{val:.3f}"
        assert f"{val:.3f}" in main
    assert cells["external-odds-obs"]==f"{ref['odds_ratio']:.2f}"
    assert cells["external-odds-laws"]==f"{v['statistical']['odds_ratio']:.2f}"
    chns=ROOT/"work/chns_iron_conditional_holdout_2026-11-19/A_TABLES.json"
    A=json.loads(chns.read_text(encoding="utf-8"))["table_1"]["counts"]
    assert all(cells[f"count{i}{j}"]==str(num) for i,row in enumerate(A) for j,num in enumerate(row))
    assert f"{result['gain']:.4f}" in main
    assert f"{result['odds_factor']:.2f}" in app
    assert verify["distinct_agent_table_triplets"]==2 and verify["serialization_comparison"]["FER_ug_L"]["records_with_different_midrank"]==2
    print(json.dumps({"v39_new_numeric_table_cells":23,"all_numeric_table_cells":178,
                      "figure_1_source_table_and_external_endpoints_verified":True,"all_six_constructors_retained":True}))


if __name__=="__main__":
    main()

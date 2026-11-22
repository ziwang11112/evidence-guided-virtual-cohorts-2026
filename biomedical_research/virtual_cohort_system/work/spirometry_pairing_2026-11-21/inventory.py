"""Extend the prior audit using this study's frozen construction and measured-data receipts."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORK=HERE.parent


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def main():
    previous=read(WORK/"kdd_v47_scale_2026-11-21/COVERAGE.json")
    r=read(HERE/"RESULTS.json")
    p=read(HERE/"PREDICTIONS.json")
    a=read(HERE/"AUTHORS.json")
    receipt=HERE.name+"/RESULTS.json"
    sites=[("US_NHANES","NHANES","NHANES 2011–12","United States","US baseline spirometry examined sample"),
           ("MW_ALHS_Y1","Chikhwawa Adult Lung Health Study","Chikhwawa first follow-up","Malawi","First returning pre-dose exam")]
    frames=list(previous["measured_comparisons"])
    for site,family,wave,country,label in sites:
        frames.append(dict(domain="Spirometry",study_family=family,recruitment_period=wave,country=country,
                           measured_sample=label,n=r["reference"][site]["n"],receipt=receipt))
    batches=list(previous["constructor_batches"])
    batches.append(dict(batch="Source-only spirometry",receipt=HERE.name+"/PREDICTIONS.json",
                        initial_sessions=len(a["authors"]),seeded_model_outputs=sum(len(p["methods"][s]["draws"]) for s in a["authors"]),
                        note="Two statistical comparators and their six draws are separate. The US 2011–12 family and period also supplied handgrip."))
    counts={"analysis_families":len({v["domain"] for v in frames}),"domain_sample_evaluations":len(frames),
            "recruitment_periods":len({v["recruitment_period"] for v in frames}),"study_families":len({v["study_family"] for v in frames}),
            "countries":len({v["country"] for v in frames}),"named_constructor_batches":len(batches),
            "initial_sessions":sum(x["initial_sessions"] for x in batches),
            "seeded_model_outputs":sum(x["seeded_model_outputs"] for x in batches)}
    assert len({(v["domain"],v["recruitment_period"]) for v in frames})==len(frames)
    data={"counts":counts,"measured_comparisons":frames,"constructor_batches":batches,
          "basis":"Same counting conventions as kdd_v47_scale_2026-11-21/COVERAGE.json plus this spirometry study."}
    text=json.dumps(data,indent=2,ensure_ascii=False)+"\n"
    (HERE/"COVERAGE.json").write_text(text,encoding="utf-8",newline="\n")
    print(counts)


if __name__=="__main__":
    main()

"""Open both study periods only after the public prediction commitment."""
import argparse
import re
import subprocess

from common import HERE, NAMES, PERIODS, SLOTS, USES, interval_class, now, read, save, text_hash
from survey import gain, gain_range, measured

PRIMARY = "nonhdl160"


def authenticate(commit, name):
    if not re.fullmatch("[0-9a-f]{40}",commit):
        raise ValueError("Full public Git commit required")
    repo=HERE.parents[2]/"github_virtual_cohort_2026-10-27"
    args=["git","-C",str(repo)]
    subprocess.run([*args,"merge-base","--is-ancestor",commit,"origin/main"],check=True)
    rel="biomedical_research/virtual_cohort_system/work/"+HERE.name+"/"+name
    public=subprocess.check_output([*args,"show",commit+":"+rel]).decode("utf-8").replace("\r\n","\n")
    assert public==(HERE/name).read_text(encoding="utf-8")


def assess(reference, predictions):
    base=predictions["base"]["pairings"]["nominal"]["values"][PRIMARY]
    authors=[predictions[k]["pairings"]["nominal"]["values"][PRIMARY] for k in SLOTS if k in predictions]
    output={}
    for period,ref in reference.items():
        y=ref["estimates"][PRIMARY]
        improvement=None
        if authors:
            width=gain_range(base,authors,y["ci"])
            improvement={"n_usable_authors":len(authors),"base_minus_median_agent_abs_error_pp":gain(base,authors,y["estimate"]),
                         "range_over_reference_95ci_pp":width,"material_at_point":len(authors)==4 and gain(base,authors,y["estimate"])>=2,
                         "material_over_ci":len(authors)==4 and width[0]>=2}
        stat=predictions["statistical"]["pairings"]["nominal"]["values"][PRIMARY]
        m={"primary":improvement,"statistical_gain_pp":gain(base,[stat],y["estimate"]),"methods":{}}
        for method,p in predictions.items():
            v=p["pairings"]["nominal"]["values"]
            scores={}
            for k in NAMES:
                e=ref["estimates"][k]
                interval=[v[k]-e["ci"][1],v[k]-e["ci"][0]]
                tol=USES[k][2]
                scores[k]={"signed_gap":v[k]-e["estimate"],"gap_ci":interval,"tolerance":tol,
                           "status":interval_class(*interval,tol)}
            variation=[d["values"][PRIMARY] for key,d in p["pairings"].items() if key!="nominal"]
            m["methods"][method]={"nominal":scores,"eight_alternative_rate_range":[min(variation),max(variation)],
                                  "alternative_point_errors_pp":{key:d["values"][PRIMARY]-y["estimate"]
                                          for key,d in p["pairings"].items() if key!="nominal"}}
        output[period]=m
    return output


def main(commit):
    sealed=read(HERE/"PREDICTIONS.json")
    assert sealed["freeze_sha256"]==text_hash(HERE/"FREEZE.json") and not sealed["new_target_outcomes_opened"]
    assert sealed["authors_sha256"]==text_hash(HERE/"AUTHORS.json")
    authenticate(commit,"PREDICTIONS.json")
    if not (HERE/"REFERENCE_OPEN.json").exists():
        save(HERE/"REFERENCE_OPEN.json",{"utc":now(),"public_predictions_commit":commit,"prediction_sha256":text_hash(HERE/"PREDICTIONS.json")})
    opening=read(HERE/"REFERENCE_OPEN.json")
    assert opening["public_predictions_commit"]==commit and opening["utc"]>=sealed["utc"]
    reference={suffix:measured(suffix) for suffix in PERIODS}
    observed=[set() for _ in PERIODS]
    import pandas as pd
    from common import PRIVATE
    for ids,suffix in zip(observed,PERIODS):
        ids.update(pd.read_sas(PRIVATE/"reference"/f"DEMO_{suffix}.xpt").SEQN.tolist())
    assert not observed[0].intersection(observed[1])
    scores=assess(reference,sealed["predictions"])
    save(HERE/"RESULTS.json",{"commit_before_disclosure":commit,"reference":reference,"scores":scores,
         "disjoint_participant_ids_across_cycles":True,"primary_material_in_both":all(m["primary"] and m["primary"]["material_at_point"] for m in scores.values()),
         "primary_material_over_both_intervals":all(m["primary"] and m["primary"]["material_over_ci"] for m in scores.values())})
    for p,m in scores.items():
        print(p,reference[p]["qc"]["both_measures_weighted"],reference[p]["estimates"][PRIMARY],m["primary"])


if __name__=="__main__":
    cli=argparse.ArgumentParser();cli.add_argument("predictions_commit")
    main(cli.parse_args().predictions_commit)

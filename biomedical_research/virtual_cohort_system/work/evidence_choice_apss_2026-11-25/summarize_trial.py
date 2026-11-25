"""Summarize the frozen APSS outcomes and pre-reveal use classifications."""
import json
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def summarize():
    from blind_review import require_review
    require_review()
    from run_trial import verified_draws
    verified_draws()
    evaluated = read(HERE/"MEASURED_EVALUATION.json")
    authors = read(HERE/"AUTHORS.json")
    key = read(HERE/"private/mask/mapping.json")
    consensus = read(HERE/"private/mask/consensus.json")
    readers = [read(HERE/"private/mask"/r/"ratings.json") for r in ("reader_1","reader_2")]
    slot_to_code = {slot:code for code,slot in key.items()}
    signed_agreement = sum(readers[0][k]["binary_consequential"] ==
                           readers[1][k]["binary_consequential"] for k in key)
    slots = []
    for out in evaluated["slots"]:
        code = slot_to_code[out["slot"]]
        review = consensus[code]
        slot = {"slot":out["slot"],"block":out["block"],"arm":out["arm"],
                "delivered":out["all_three_available"],"primary_source_used": review["binary_consequential"],
                "recognized":review["binary_recognized"],"continuous_used":review.get("continuous_used"),
                "three_seed_source_fit":bool(out.get("near_source_table")),"use_tail":bool(out.get("all_tail_in_tolerance")),
                "use_mean":bool(out.get("all_means_in_tolerance")),"both":bool(out.get("both"))}
        slot["delivered_binary_use"] = bool(slot["delivered"] and slot["primary_source_used"] is True)
        if slot["delivered"]:
            draws=out["draws"]
            slot.update(median_tail_pct=median(x["tail_pct"] for x in draws),
                        median_tail_error_pp=median(x["tail_error_pp"] for x in draws),
                        median_abs_tail_error_pp=median(abs(x["tail_error_pp"]) for x in draws),
                        median_mean_difference=median(x["signed_mean"] for x in draws),
                        median_abs_mean_error=median(abs(x["signed_mean_error"]) for x in draws),
                        mean_source_tv_pp=out["source_joint_mean_tv_pp"],
                        max_source_tv_pp=max(x["source_joint_tv_pp"] for x in draws))
        slots.append(slot)
    arms={}
    for arm in ("ordinary","targeted"):
        sel=[r for r in slots if r["arm"]==arm]
        agg={"assigned":len(sel)}
        for k in ("delivered","delivered_binary_use","recognized","three_seed_source_fit","use_tail","use_mean","both"):
            agg[k]=sum(x[k] is True for x in sel)
        for k in ("median_tail_pct","median_abs_tail_error_pp","median_abs_mean_error","mean_source_tv_pp"):
            vals=[x[k] for x in sel if x["delivered"]]
            agg[k]=median(vals) if vals else None
        arms[arm]=agg
    delta=(arms["ordinary"]["median_abs_tail_error_pp"]-arms["targeted"]["median_abs_tail_error_pp"]
           if arms["ordinary"]["delivered"] and arms["targeted"]["delivered"] else None)
    out={"unit":"one preregistered article; four independent constructions per arm",
         "arm_summary":arms,"ordinary_minus_targeted_median_abs_tail_error_pp":delta,
         "slots":slots,"binary_reviewer_agreement_count":signed_agreement,
         "reviewed":len(key),"measured":evaluated["reference"],
         "eligibility":evaluated["reference_eligibility"],"known_tariff_usd":authors["known_tariff_usd"]}
    path=HERE/"ANALYSIS_SUMMARY.json"
    if path.exists() and read(path)!=out:
        raise ValueError("Existing public summary differs")
    path.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps(arms,indent=2))

if __name__=="__main__":
    summarize()

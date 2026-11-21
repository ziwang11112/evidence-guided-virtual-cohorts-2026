"""Verify that raw API code, archived scientific settings and replayed rows agree."""
import json
import subprocess
from statistics import fmean
import numpy as np
from science import HERE,SEEDS,read,sha,write
from verify import independent

def main():
    raw=read(HERE/"private/api/calls/lipid_author/response_text.txt")
    assert raw["generator_py"]==(HERE/"law/generator.py").read_text(encoding="utf8")
    assert raw["model_spec"]==read(HERE/"law/model_spec.json") and raw["decision_record"]==read(HERE/"law/decision.json")
    f=read(HERE/"MODEL_CLOSURE.json");out=read(HERE/"REPLAY_RESULTS.json")
    assert out["model_closure_sha256"]==sha(HERE/"MODEL_CLOSURE.json") and out["original_results_sha256"]==sha(HERE/"RESULTS.json")
    baseline=read(HERE/"CLOSURE.json")["arms"]["statistical"]
    assert baseline==f["arms"]["statistical"] and not read(HERE/"CLOSURE.json")["arms"]["agent"]["usable"]
    arrays=0
    for arm,rec in f["arms"].items():
        pooled=[]
        for d in rec["runs"]:
            seed=d["seed"];file=HERE/f"private/{arm}-{seed}.npy"
            assert sha(file)==d["array_sha256"]
            a=np.load(file,allow_pickle=False);stat=np.load(HERE/f"private/statistical-{seed}.npy",allow_pickle=False)
            np.testing.assert_array_equal(np.sort(a,axis=0),np.sort(stat,axis=0))
            if arm=="agent":
                csv=HERE/f"private/replay-{seed}/output/generated.csv"
                assert sha(csv)==d["permutation_csv_sha256"]
                ix=np.loadtxt(csv,delimiter=",",skiprows=1,dtype=int)
                np.testing.assert_array_equal(ix[:,0],np.arange(len(a)))
                np.testing.assert_array_equal(np.sort(stat[:,1])[ix[:,1]],a[:,1])
            delta=a[:,0]-a[:,1];v=d["estimates"]
            assert len(delta)==v["n"] and sum(dv>=160 for dv in delta)==v["tail_count"]
            assert np.count_nonzero(delta<0)==v["tc_below_hdl"]
            np.testing.assert_allclose([fmean(delta),fmean(a[:,0]/a[:,1])],[v["mean_mg_dl"],v["mean_tc_over_hdl"]],rtol=0,atol=1e-9)
            pooled.extend(delta);arrays+=1
        if rec["usable"]:
            g_mean=fmean(pooled);g_tail=100*sum(v>=160 for v in pooled)/len(pooled)
            np.testing.assert_allclose([g_mean,g_tail],[rec["pooled"]["mean_mg_dl"],rec["pooled"]["tail_pct"]],atol=1e-9,rtol=0)
            for site in ("mekelle","workers"):
                a,t,h=independent(site).T;delta=t-h;v=out["cohorts"][site];q=v["arms"][arm]
                np.testing.assert_allclose([g_mean-fmean(delta),g_tail-100*sum(z>=160 for z in delta)/len(delta)],
                                           [q["mean_gap_mg_dl"],q["tail_gap_pp"]],atol=1e-7,rtol=0)
                lo,hi=v["reference_ci"]["tail_pct"]
                np.testing.assert_allclose([g_tail-hi,g_tail-lo],q["tail_gap_interval_pp"],atol=1e-9)
                tag="outside" if g_tail-hi>2 or g_tail-lo< -2 else "within" if g_tail-hi>=-2 and g_tail-lo<=2 else "unresolved"
                assert q["planning_status"]==tag
    write(HERE/"REPLAY_VERIFICATION.json",{"unaltered_program_model_and_decision":True,"raw_failure_preserved":True,
          "numerically_recomputed_draws":arrays,"separate_measured_readers":True,"two_site_classifications_verified":True,
          "raw_verification_sha256":sha(HERE/"VERIFICATION.json"),"replay_results_sha256":sha(HERE/"REPLAY_RESULTS.json")})
    print("Independent comparisons passed",arrays,"arrays")
if __name__=="__main__":main()

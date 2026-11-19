"""Check frozen analysis semantics with artificial fixtures; never opens measured rows."""
import numpy as np
import pandas as pd

from science import FE, HB, check, measures


def tests():
    # Equality at 12 and 15 belongs to the upper categories. Tied midranks matter.
    table = pd.DataFrame({HB:[10.,11.,12.,12.,13.,13.5,14.,14.],
                          FE:[3.,20.,5.,6.,15.,30.,35.,13.]})
    s = measures(table)
    check(s["cells"] == [1,1,3,3] and s["odds_ratio"] == 1, "Crude threshold coding")
    check(np.isclose(s["ratio"], np.sqrt(15*30)/np.sqrt(5*6)), "Geometric mean ratio")
    check(np.isclose(s["rank"], table[HB].rank().corr(table[FE].rank())), "Tie handling")
    # Exchange ferritin values inside the same fine Hb bin and depletion class.
    t = pd.DataFrame({HB:[10.,11.,12.1,12.5,13.1,13.4,14.1,14.8],
                      FE:[7.,20.,17.,24.,19.,50.,12.,60.]})
    q = t.copy()
    q.loc[[4,5], FE] = q.loc[[5,4],FE].to_numpy()
    a,b=measures(t),measures(q)
    check(a["cells"]==b["cells"] and np.isclose(a["ratio"],b["ratio"]), "Invariance test")
    for old,new in zip(a["groups"],b["groups"]):
        for key in old:
            check(np.isclose(old[key],new[key]), "Band summaries should be invariant")
    check(abs(a["rank"]-b["rank"]) > .001, "The supplement must not imply overall Spearman")
    return ["strict boundary/equality","tied ranks","geometric mean ratio","within-bin rearrangement preserves input but changes endpoint"]


def sandbox_check(sandbox, task, private):
    folder=private/"fixture_law"
    folder.mkdir(parents=True,exist_ok=True)
    code = """import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    n = spec["task"]["n_rows"]
    r = np.random.default_rng(seed)
    return pd.DataFrame({"row_id": np.arange(n), "hb_g_dl": r.uniform(8,16,n), "ferritin_ug_l": r.uniform(5,100,n)})
"""
    import json
    (folder/"generator.py").write_text(code,encoding="utf8")
    (folder/"model_spec.json").write_text(json.dumps({"task":task,"model":{}}),encoding="utf8")
    dest=private/"fixture_run"
    res=sandbox.read(dest/"execution.json") if dest.exists() else sandbox.isolated(folder,task,dest,701)
    check(res["status"]=="success","Isolated fixture failure: "+str(res.get("error")))
    return res["generated_sha256"]

"""Reconcile printed KDD results with the sealed scientific estimates."""
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

import check_v35

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/"manuscript/kdd_draft_v36_2026-11-19"
STUDY=ROOT/"work/original_paper_iron_sensitivity_2026-11-19"


def run():
    check_v35.PAPER=PAPER
    check_v35.main()
    spec=importlib.util.spec_from_file_location("iron_audit",STUDY/"public_replay.py")
    audit=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    print(audit.run())
    read=lambda f:json.loads((STUDY/f).read_text(encoding="utf8"))
    source=read("SCIENTIFIC_RESULTS.json"); target=read("REVEAL.json")["result"]
    appendix=(PAPER/"appendix.tex").read_text(encoding="utf8")
    tex=(PAPER/"main.tex").read_text(encoding="utf8")
    labels={"statistical":"Statistical"}
    for i in range(1,4):
        labels.update({f"P{i}":f"P{i} primary",f"P{i}_ordinary":f"P{i} ordinary",f"P{i}_directed":f"P{i} directed"})
    body=appendix.split(r"\label{tab:ironprospective}")[1].split(r"\end{tabular}")[0].splitlines()
    n=0
    for key,label in labels.items():
        row=next(s for s in body if s.startswith(label+" &"))
        columns=[s.strip().replace(r"\\","") for s in row.split("&")]
        law=source["laws"].get(key,{})
        if "spearman" in law:
            for k,i in [("odds_ratio",1),("spearman",2)]:
                if law[k] is None: assert columns[i]=="--"
                else: np.testing.assert_allclose(float(columns[i]),law[k],rtol=0,atol=.000501); n+=1
        expected = "pass" if law.get("tier2") else ("fail" if "spearman" in law else "incomplete")
        assert columns[3].strip()==expected
    assert r"\includegraphics[width=.98\textwidth]{figures/iron-alternatives.pdf}" in tex
    assert f'{target["n_complete"]} women' in tex
    for v in target["weighted"]:
        if v is not None: assert format(v,".3f") in tex
    print({"new_table_numerical_cells":n,"complete_target":target["n_complete"]})


if __name__=="__main__":run()

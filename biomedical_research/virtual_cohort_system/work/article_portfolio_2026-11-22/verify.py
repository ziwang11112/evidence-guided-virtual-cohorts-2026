"""Recalculate the matched experiment from article tables, staged columns, index files and API receipts."""
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys
import unicodedata

import numpy as np
from scipy.stats import binomtest, spearmanr

HERE = Path(__file__).resolve().parent


def read(p):
    return json.loads(p.read_text(encoding="utf8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


def close(a, b, tol=1e-9):
    return math.isclose(a, b, rel_tol=0, abs_tol=tol)


def verify_original(name, home, f):
    if name == "grip":
        pdf = home / "private/adelaide.pdf"
        raw = home / "private/adelaide.layout.txt"
    else:
        raw = HERE.parent / "original_paper_capability_2026-11-17/private_sources/iron_original.layout.txt"
        pdf = raw.with_name("iron_original.pdf")
    assert f["raw_publication_hashes"] == {raw.name: sha(raw), pdf.name: sha(pdf)}
    source = read(home/"SOURCE.json")
    s = unicodedata.normalize("NFKC", raw.read_text(encoding="utf8"))
    if name == "grip":
        assert sha(pdf) == source["pdf_sha256"] and pdf.stat().st_size == source["pdf_bytes"]
        assert "Table 1" in s and "kg" in s
        cells = {}
        for line in s.splitlines():
            age = re.match(r"^(50 to 59|60 to 69)\s", line)
            if age:
                pairs = re.findall(r"(\d+\.?\d*)\s*\((\d+\.?\d*)\)", line)
                assert len(pairs) == 6
                for label, j in (("M", 0), ("F", 3)):
                    cells[label+age[1][:2]] = [float(a) for pair in pairs[j:j+2] for a in pair]
        assert cells == source["cells"]
        return {"cells": cells, "unit": "kg", "table": 1}
    t1 = s.split("Table I:", 1)[1].split("Prevalence ratios", 1)[0]
    t3 = s.split("Table III:", 1)[1].split("Table IV:", 1)[0]
    t4 = s.split("Table IV:", 1)[1].split("proportion and 95", 1)[0]
    t5 = s.split("Table V:", 1)[1]
    e = {}
    for k, label in (("fe_gm", "Plasma ferritin"), ("hb_gm", "Hemoglobin")):
        m = re.search(r"^"+label+r"\s+\(g/L\)\s+(\d+)\s+([\d.]+)\s+\(", t1, re.M)
        e[k] = float(m[2])
        assert int(m[1]) == e.setdefault("n_total", int(m[1]))
    e["n_by_band"] = list(map(int, re.search(r"^N\s+(\d+)\s+(\d+)\s+(\d+)", t3, re.M).groups()))
    fpart = re.split(r"Ferritin,\s*μg\s*/L", t3, maxsplit=1)[1]
    gm = next(l for l in fpart.splitlines() if l.startswith("Geometric mean"))
    e["fe_gm_by_band"] = list(map(float, re.findall(r"([\d.]+)\s*\(", gm)))
    pct = re.search(r"% Iron Depletion\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", fpart)
    e["depleted_pct_by_band"] = list(map(float, pct.groups()))
    cuts = re.search(r"<\s*(\d+)\s+(\d+)[–-](\d+)\s+≥\s*(\d+)", t3)
    e["severe_cut"], e["anemia_cut"] = int(cuts[1]), int(cuts[4])
    e["iron_cut"] = int(re.search(r"ferritin <\s*(\d+)\s*μg/L", t3)[1])
    counts = Counter()
    n_rows = 0
    for line in t4.splitlines():
        clean = re.sub(r"\([^)]*\)|\*", "", line).split()
        if len(clean) == 9 and all(c in ("+", "–", "-") for c in clean[:3]):
            overall, anemia, other = map(int, (clean[3], clean[5], clean[7]))
            assert overall == anemia + other
            iron = "low" if clean[2] == "+" else "high"
            counts["anemic_"+iron] += anemia
            counts["nonanemic_"+iron] += other
            n_rows += 1
    assert n_rows == 8
    e.update(counts)
    row = next(l for l in t5.splitlines() if l.startswith("Iron depletion ("))
    e["adjusted_or"] = float(row.split()[-3])
    assert e == source["quantities"]
    return {"evidence": e, "tables": {"overall":"I","bands":"III","cells":"IV","adjusted":"V"},
            "hb_unit":"g/L","fe_unit":"ug/L"}


def valid_extraction(actual, expected):
    for k, v in expected.items():
        if k not in actual:
            return False
        value = actual[k]
        if isinstance(v, dict):
            if not isinstance(value, dict) or (k in ("tables", "cells") and set(value) != set(v)):
                return False
            if not valid_extraction(value, v):
                return False
        elif isinstance(v, list):
            if not isinstance(value, list) or len(value) != len(v) or any(
                    type(a) not in (int,float) or not close(a,b,1e-8) for a,b in zip(value,v)):
                return False
        elif type(v) in (int, float):
            if type(value) not in (int, float) or not close(v, value, 1e-8):
                return False
        elif value != v:
            return False
    return True


def transactions(home, author, f):
    actual, tariff, accounted = 0, 0., 0.
    complete = 0
    counts = Counter()
    path = home / "private/api/calls"
    common = set()
    assert author["freeze_sha256"] == sha(home/"FREEZE.json")
    for tag, r in sorted(author["calls"].items()):
        status = r["status"]
        counts[status] += 1
        d = path / tag
        if status.startswith("unissued"):
            assert not (d/"reservation.json").exists()
            continue
        actual += 1
        local = read(d/"receipt.json")
        assert local["status"] == status and local["no_automatic_retry"]
        for filename, k in (("prompt.txt","prompt_sha256"),("request.json","request_sha256"),("response_text.txt","response_text.txt_sha256"),("artifact.json","artifact.json_sha256")):
            if r.get(k):
                assert sha(d/filename) == r[k]
        body = read(d/"request.json")["body"]
        prompt = (d/"prompt.txt").read_text(encoding="utf8")
        assert body["input"] == prompt and body["model"] == "gpt-6.1-sol" and body["service_tier"] == "default"
        assert body["store"] is False and body["max_output_tokens"] == 12000 and body["reasoning"]["effort"] == "medium"
        assert digest(body["instructions"]) == f["system_sha256"]
        block, role = tag.split("_")
        content, instruction = prompt.rsplit("\n\nAUTHORING REQUEST\n",1)
        assert digest(instruction) == f["instructions"][role]
        if role == "initial":
            assert digest(prompt) == f["initial_prompt_sha256"]
        else:
            content, initial = content.rsplit("\n\nINITIAL SUBMISSION\n",1)
            assert json.loads(initial) == read(path/(block+"_initial")/"artifact.json")
        common.add(digest(content))
        assert digest(content.split("\n\nORIGINAL ARTICLE\n",1)[1]) == f["article_sha256"]
        if r["tariff_cost_usd"] is None:
            accounted += read(d/"reservation.json")["reserved_usd"]
        else:
            usage = read(d/"response_raw.json")["usage"]
            inputs, outputs = usage["input_tokens"], usage["output_tokens"]
            cache = usage["input_tokens_details"].get("cached_tokens",0) or 0
            writes = usage["input_tokens_details"].get("cache_write_tokens",0) or 0
            usd = (2*(inputs-cache-writes)+.1*cache+2.5*writes+10*outputs)/1e6
            assert close(usd, r["tariff_cost_usd"], 1e-10)
            complete += 1
            tariff += usd
            accounted += usd
    assert len(common)==1 and close(accounted,author["accounted_usd"]) and accounted <= 18
    return {"issued":actual, "with_usage":complete, "statuses":dict(counts),
            "tariff_usd":round(tariff,9), "accounted_usd":round(accounted,9)}


def paired_columns(dirpath, item, obj):
    bind = read(dirpath/"run/input_bindings.json")
    receipt = read(dirpath/"run/execution.json")
    assert receipt["status"]=="success" and receipt["generator_executed"] and receipt["no_local_fallback"]
    assert "no network" in receipt["isolation"] and "bubblewrap" in receipt["isolation"]
    assert receipt["generated_sha256"]==item["sha256"] and receipt["seed"]==item["seed"]
    assert read(dirpath/"run/input/request.json")["seed"]==item["seed"]
    assert set(bind)=={"model_spec.json","generator.py","task.json","worker.py","request.json"}
    for key in bind:
        assert sha(dirpath/"run/input"/key) == bind[key]
    assert (dirpath/"run/input/generator.py").read_bytes() == obj["generator_py"].encode("utf8")
    staged = read(dirpath/"run/input/model_spec.json")
    assert staged["model"] == obj["model_spec"]
    p = dirpath/"run/output/generated.csv"
    assert sha(p) == item["sha256"]
    with p.open(encoding="utf8", newline="") as file:
        reader = csv.reader(file)
        assert next(reader) == ["row_id","paired_index"]
        order = []
        for expected_row, (row, index) in enumerate(reader):
            assert int(row) == expected_row
            order.append(int(index))
    start = 0
    pairs = []
    for group in staged["groups"]:
        x = np.array(group["x"]); y = np.array(group["y"])
        n = len(x); idx = order[start:start+n]
        assert len(y)==n and sorted(idx)==list(range(n))
        pairs.append((group["label"], x, y[idx]))
        start += n
    assert start == len(order)
    return pairs


def geometric(a):
    return math.exp(math.fsum(map(math.log, a)) / len(a))


def iron_rows(pairs, expected, report):
    e = expected["evidence"]
    assert [s for s,_,_ in pairs] == ["severe","intermediate","nonanemic"]
    hb = np.concatenate([x for _,x,_ in pairs])
    fe = np.concatenate([y for _,_,y in pairs])
    a, b = hb<e["anemia_cut"], fe<e["iron_cut"]
    cells = [sum((a==i) & (b==j)).item() for i,j in ((True,True),(True,False),(False,True),(False,False))]
    assert cells == report["cells"]
    n = [len(y) for _,_,y in pairs]
    assert n == report["bands"]
    expected_cells = [10*e[k] for k in ("anemic_low","anemic_high","nonanemic_low","nonanemic_high")]
    positive = min(fe)>0 and min(hb)>0
    assert bool(positive)==report["positive"]
    checks = [positive, cells==expected_cells, n==[10*v for v in e["n_by_band"]]]
    gm, gf = geometric(hb), geometric(fe)
    assert close(gm, report["hb_gm"]) and close(gf, report["fe_gm"])
    def rounds(value, center, unit):
        return center-unit/2 <= value < center+unit/2
    checks += [rounds(gm,e["hb_gm"],.1), rounds(gf,e["fe_gm"],.1)]
    for i, (_,_,y) in enumerate(pairs):
        gm = geometric(y)
        depleted = 100*sum(y<e["iron_cut"])/len(y)
        assert close(gm,report["band_fe_gm"][i]) and close(depleted, report["depleted_pct"][i])
        checks += [rounds(gm,e["fe_gm_by_band"][i],.1),rounds(depleted,e["depleted_pct_by_band"][i],1 if i==1 else .1)]
    odds = (cells[0]/cells[1]) / (cells[2]/cells[3])
    return odds, float(spearmanr(hb,fe).statistic), all(checks)


def grip_rows(pairs, expected, report):
    assert [s for s,_,_ in pairs]==["M50","M60","F50","F60"]
    means, diffs, checks = [], [], []
    for label, right, left in pairs:
        row = report["cells"][label]
        nr = len(right)
        moments = [statistics.fmean(right),statistics.pstdev(right),statistics.fmean(left),statistics.pstdev(left)]
        assert np.allclose(moments,row["moments"],rtol=0,atol=1e-9)
        pos = min(right)>0 and min(left)>0
        assert bool(pos)==row["positive"]
        pearson = statistics.correlation(right.tolist(),left.tolist())
        assert close(pearson,row["pearson"])
        means.append((math.fsum(right)+math.fsum(left))/(2*nr))
        diffs.append(math.fsum(abs(x-y) for x,y in zip(right,left))/nr)
        checks.extend([nr==4096,pos,np.allclose(moments,expected["cells"][label],rtol=0,atol=1e-7)])
    return statistics.fmean(means),statistics.fmean(diffs),all(checks)


def verify(name):
    if name not in ("iron","grip"):
        raise ValueError("Unknown case")
    home = HERE / name
    frozen = read(home/"FREEZE.json")["design"]
    authors = read(home/"PUBLIC_AUTHORS.json")
    result = read(home/"RESULTS.json")
    assert result["authors_sha256"] == sha(home/"PUBLIC_AUTHORS.json")
    source = verify_original(name, home, frozen)
    fees = transactions(home, authors, frozen)
    models, proofs = {}, Counter()
    checks = iron_rows if name=="iron" else grip_rows
    for tag, original in result["models"].items():
        receipt = authors["calls"][tag]
        file = home/"private/api/calls"/tag/"artifact.json"
        if receipt["status"]!="received" or not file.is_file():
            assert not original["usable"] and original["draws"]==[]
            models[tag] = None
            continue
        obj = read(file)
        assert sha(file)==receipt["artifact.json_sha256"]
        valid = valid_extraction(obj["model_spec"], source)
        assert valid == (not original["extraction_failures"])
        dset = []
        for d in original["draws"]:
            path = home/"private/draws"/tag/str(d["seed"])
            assert read(path/"DRAW.json")==d
            if "outcome" not in d:
                assert "error" in d
                proofs["failed_draws"] += 1
                continue
            v = d["outcome"]
            p = paired_columns(path,d,obj)
            fixed, quantity, good = checks(p,source,v)
            assert close(fixed,v["fixed"]) and close(quantity,v["requested"]) and good==(not d["failures"])
            valid = valid and good
            dset.append((d["seed"],fixed,quantity))
            proofs["recalculated_tables"] += 1
        valid = valid and [t[0] for t in dset]==frozen["seeds"]
        assert valid == original["usable"]
        if valid:
            proofs["eligible_models"] += 1
            assert close(statistics.fmean(q for _,_,q in dset),original["requested"])
            assert close(statistics.fmean(v for _,v,_ in dset),original["fixed"])
        models[tag] = dset if valid else None
    totals = Counter()
    for block, arms in result["blocks"].items():
        base = models[block+"_initial"]
        flags, valid = {}, []
        for role, original in arms.items():
            follow = models[block+"_"+role]
            good = base is not None and follow is not None
            assert original["valid"] == good
            changed = False
            if good:
                assert all(close(i[1],j[1],1e-7) for i,j in zip(base,follow))
                gaps = [j[2]-i[2] for i,j in zip(base,follow)]
                mean = statistics.fmean(gaps)
                changed = abs(mean)>frozen["primary_margin"] and all(
                    math.copysign(1,mean)*x>frozen["per_seed_margin"] for x in gaps)
                assert np.allclose(gaps,original["seed_gaps"],rtol=0,atol=1e-9) and close(mean,original["gap"])
            assert changed == original["material"]
            flags[role]=changed
            valid.append(good)
        totals["both_valid"] += all(valid)
        totals["ordinary"] += flags["ordinary"]
        totals["targeted"] += flags["alternative"]
        totals["ordinary_only"] += flags["ordinary"] and not flags["alternative"]
        totals["targeted_only"] += flags["alternative"] and not flags["ordinary"]
    prim = result["primary"]
    assert all(totals[k]==prim[k] for k in totals) and len(result["blocks"])==prim["n_blocks"]==12
    d = totals["ordinary_only"]+totals["targeted_only"]
    p = binomtest(totals["ordinary_only"],d).pvalue if d else 1.
    assert close(p,prim["p_exact"])
    gate = totals["both_valid"]>=8 and totals["targeted_only"]>totals["ordinary_only"]
    assert gate==prim["gate_before_verification"]
    out={"case":name,"source_table_values_independently_extracted":True,
         "original_article_and_matched_prompts_verified":True,"source_pdf_sha256":next(
             h for k,h in frozen["raw_publication_hashes"].items() if k.endswith(".pdf")),
         "results_sha256":sha(home/"RESULTS.json"), "receipts_sha256":sha(home/"PUBLIC_AUTHORS.json"),
         "counts":dict(proofs),"verified_primary":prim,"verified_gate":gate,"api":fees}
    dest=home/"VERIFICATION.json"
    if dest.exists():
        assert read(dest)==out
    else:
        dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    verify(sys.argv[1])

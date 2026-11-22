"""Common registered execution of original-article paired modeling experiments."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import random
import sys

from filelock import FileLock
import numpy as np
import pandas as pd
from scipy.stats import binomtest

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
PROJECT=WORK.parent
sys.path.insert(0,str(WORK/"article_pairing_2026-11-22"))
import experiment as shared

client=shared.client
harness=shared.harness
read,save,sha,now=shared.read,shared.save,shared.sha,shared.now
BLOCKS=shared.BLOCKS
ARMS=shared.ARMS
CFG=shared.CONFIG
MAX_BYTES=170000


class Publication:
    def __init__(self,name):
        if name not in ("iron","grip"):raise ValueError("Unknown publication")
        self.name=name
        self.path=HERE/name
        self.private=self.path/"private"
        self.api=self.private/"api"
        st=importlib.util.spec_from_file_location("source_"+name,self.path/"case.py")
        self.case=importlib.util.module_from_spec(st)
        st.loader.exec_module(self.case)
        self.instructions=dict(shared.INSTRUCTIONS)
        self.instructions["alternative"]=self.instructions["alternative"].replace("the screening estimate",
                                                                                "the "+self.case.REQUESTED)
    def prompt(self,arm,parent=None):
        base=(self.path/"REQUEST.txt").read_text(encoding="utf8").strip()
        past="" if parent is None else "\n\nINITIAL SUBMISSION\n"+shared.canonical(parent)
        return base+"\n\nORIGINAL ARTICLE\n"+self.case.article()+past+"\n\nAUTHORING REQUEST\n"+self.instructions[arm]

    def design(self):
        c=self.case
        shared_paths=[Path(shared.__file__),shared.PILOT/"pilot.py",PROJECT/"cohort_harness/execution.py",
                      PROJECT/"cohort_harness/contracts.py",harness.WORKER,
                      WORK/"cross_model_api_pilot_2026-11-10/provider_client.py",
                      WORK/"cross_model_api_pilot_2026-11-10/provider_preflight.py"]
        local=[HERE/"DESIGN.md",HERE/"matched.py",self.path/"case.py",self.path/"PROTOCOL.md",
               self.path/"REQUEST.txt",self.path/"SOURCE.json"]
        inputs={q.relative_to(PROJECT).as_posix():sha(q) for q in local+shared_paths}
        known={q.name:sha(q) for q in c.BOUND_FILES}
        rng=random.Random(c.SEEDS[0])
        first_order=rng.sample(list(BLOCKS),len(BLOCKS));branch={b:rng.sample(list(ARMS),2) for b in BLOCKS}
        text=self.prompt("initial");size=request_bytes(text);cfg=client.CONFIGS[CFG]
        def hold(n):return ((n+4096)*max(cfg["input_rate"],cfg["cache_write_rate"])+client.MAX_OUTPUT*cfg["output_rate"])/1e6
        ceiling=len(BLOCKS)*(hold(size)+2*hold(MAX_BYTES))
        if size>MAX_BYTES or ceiling>client.CAPS["openai"]:raise ValueError("Budget would exceed registration")
        return {"files":inputs,"raw_publication_hashes":known,"doi":c.DOI,
                "article_sha256":shared.text_hash(c.article()),"initial_prompt_sha256":shared.text_hash(text),
                "system_sha256":shared.text_hash(client.SYSTEM),
                "instructions":{k:shared.text_hash(v) for k,v in self.instructions.items()},
                "initial_order":first_order,"branch_order":branch,"seeds":list(c.SEEDS),
                "model":cfg,"max_output_tokens":client.MAX_OUTPUT,"max_calls":36,"cap_usd":client.CAPS["openai"],
                "upper_reservation_usd":ceiling,"initial_request_bytes":size,"request_byte_cap":MAX_BYTES,
                "primary_margin":c.MARGIN,"per_seed_margin":c.SEED_MARGIN}

    def guard(self):
        f=read(self.path/"FREEZE.json")["design"]
        if f!=self.design():raise RuntimeError("Frozen study binding changed")
        return f

    def program(self,slot):
        path=self.api/"calls"/slot
        if not (path/"receipt.json").is_file():return None
        r=read(path/"receipt.json");p=path/"artifact.json"
        if r.get("status")!="received" or r.get("returned_model")!=client.CONFIGS[CFG]["model"] or not p.is_file():
            return None
        if sha(p)!=r["artifact.json_sha256"]:raise RuntimeError("Artifact integrity error")
        return read(p)

    def issue(self,slot,text):
        d=self.api/"calls"/slot
        if d.exists():
            if not (d/"receipt.json").is_file():raise RuntimeError("Unsettled request "+slot)
            r=read(d/"receipt.json")
            if sha(d/"prompt.txt")!=r["prompt_sha256"] or (d/"prompt.txt").read_text(encoding="utf8")!=text:
                raise RuntimeError("Previously issued request differs")
        else:r,_=client.call_once(self.api,slot,CFG,text)
        fields=("requested_model","returned_model","started_utc","ended_utc","status","artifact_status",
                "api_error_code","stop_reason","usage","tariff_cost_usd","request_sha256","prompt_sha256",
                "response_text.txt_sha256","artifact.json_sha256")
        return {k:r.get(k) for k in fields}

    def dispatch(self):
        info=self.guard();out=self.path/"PUBLIC_AUTHORS.json"
        if out.exists():return
        first=self.prompt("initial")
        def initial(b):return self.issue(b+"_initial",first)
        def follow(work):
            b,a=work;parent=self.program(b+"_initial")
            if parent is None:return {"status":"unissued_missing_initial_artifact"}
            prompt=self.prompt(a,parent)
            if request_bytes(prompt)>MAX_BYTES:return {"status":"unissued_request_too_large"}
            return self.issue(b+"_"+a,prompt)
        with ThreadPoolExecutor(max_workers=6) as workers:
            order=info["initial_order"]
            calls=dict(zip([b+"_initial" for b in order],workers.map(initial,order),strict=True))
            print("Initial authoring closed.",flush=True)
            jobs=[(b,a) for b in order for a in info["branch_order"][b]]
            calls.update(zip([b+"_"+a for b,a in jobs],workers.map(follow,jobs),strict=True))
        save(out,{"utc":now(),"freeze_sha256":sha(self.path/"FREEZE.json"),"calls":calls,
                  "accounted_usd":client.ledger_accounted(self.api,"openai")})
        print("All author slots closed.",flush=True)

    def execute(self,obj,groups,seed,d):
        n=sum(len(x) for _,x,_ in groups);contract=task(self.name,n)
        folder=d/"candidate";folder.mkdir(parents=True,exist_ok=False)
        (folder/"generator.py").write_text(obj["generator_py"],encoding="utf8",newline="\n")
        save(folder/"model_spec.json",{"model":obj["model_spec"],"task":contract,
             "groups":[{"label":s,"x":x.tolist(),"y":y.tolist()} for s,x,y in groups]})
        run=d/"run";rec=harness.isolated(folder,contract,run,seed)
        if rec["status"]!="success":
            p=run/"output/worker_report.json"
            message=read(p).get("error") if p.is_file() and p.stat().st_size else rec.get("error")
            raise ValueError("Worker failure: "+str(message)[:340])
        csv=run/"output/generated.csv"
        if sha(csv)!=rec["generated_sha256"]:raise RuntimeError("Assignment hash changed")
        tab=pd.read_csv(csv)
        if list(tab)!=["row_id","paired_index"] or not np.array_equal(tab.row_id.to_numpy(),np.arange(n)):
            raise ValueError("Row identity mismatch")
        idx=tab.paired_index.to_numpy()
        parts=np.split(idx,np.cumsum([len(x) for _,x,_ in groups])[:-1])
        for v,(_,x,y) in zip(parts,groups,strict=True):
            if len(x)!=len(y) or v.dtype.kind not in "iu" or not np.array_equal(np.sort(v),np.arange(len(x))):
                raise ValueError("Invalid within-stratum permutation")
        return parts,rec["generated_sha256"]

    def score_model(self,tag):
        obj=self.program(tag)
        if obj is None:return {"usable":False,"reason":"unavailable_artifact","draws":[]}
        c=self.case;spec=obj["model_spec"];issues=c.extraction(spec)
        out={"usable":False,"extraction_failures":issues,"draws":[]}
        try:g=c.groups(spec)
        except (ValueError,TypeError,KeyError,IndexError,ArithmeticError) as e:
            out["reason"]="invalid_grid: "+str(e)[:180];return out
        for seed in c.SEEDS:
            d=self.private/"draws"/tag/str(seed);receipt=d/"DRAW.json"
            if receipt.exists():
                draw=read(receipt)
                if "sha256" in draw and sha(d/"run/output/generated.csv")!=draw["sha256"]:
                    raise RuntimeError("Archive integrity failed")
            else:
                try:
                    orders,h=self.execute(obj,g,seed,d);v=c.stats(g,orders)
                    draw={"seed":seed,"sha256":h,"outcome":v,"failures":c.failures(v)}
                except (ValueError,RuntimeError,OSError,IndexError,TypeError,ArithmeticError,AssertionError) as e:
                    draw={"seed":seed,"error":str(e)[:360]}
                save(receipt,draw)
            out["draws"].append(draw)
        ds=[v for v in out["draws"] if "outcome" in v]
        if len(ds)!=3:out["reason"]="incomplete_generation";return out
        fail=sorted(set(f for v in ds for f in v["failures"]))
        out.update(usable=not issues and not fail,source_failures=fail,
                   requested=float(np.mean([v["outcome"]["requested"] for v in ds])),
                   fixed=float(np.mean([v["outcome"]["fixed"] for v in ds])))
        return out

    def compare(self,first,second):
        ok=first["usable"] and second["usable"]
        row={"valid":ok,"material":False}
        if ok:
            if abs(first["fixed"]-second["fixed"])>1e-7:raise RuntimeError("Fixed analysis changed")
            gaps=np.array([b["outcome"]["requested"]-a["outcome"]["requested"]
                           for a,b in zip(first["draws"],second["draws"],strict=True)])
            mean=float(gaps.mean())
            row.update(gap=mean,seed_gaps=gaps.tolist(),
                       material=bool(abs(mean)>self.case.MARGIN and np.all(np.sign(mean)*gaps>self.case.SEED_MARGIN)))
        return row

    def score(self):
        self.guard();receipt=read(self.path/"PUBLIC_AUTHORS.json")
        assert receipt["freeze_sha256"]==sha(self.path/"FREEZE.json") and len(receipt["calls"])==36
        out=self.path/"RESULTS.json"
        if out.exists():return
        slots=sorted(receipt["calls"])
        with ThreadPoolExecutor(max_workers=3) as pool:
            models=dict(zip(slots,pool.map(self.score_model,slots),strict=True))
        pairs={b:{a:self.compare(models[b+"_initial"],models[b+"_"+a]) for a in ARMS} for b in BLOCKS}
        flags=[(v["ordinary"]["material"],v["alternative"]["material"]) for v in pairs.values()]
        pos=flags.count((False,True));neg=flags.count((True,False))
        valid=sum(v["ordinary"]["valid"] and v["alternative"]["valid"] for v in pairs.values())
        prim={"n_blocks":12,"both_valid":valid,"ordinary":sum(a for a,b in flags),"targeted":sum(b for a,b in flags),
              "ordinary_only":neg,"targeted_only":pos,"p_exact":float(binomtest(pos,pos+neg,.5).pvalue) if pos+neg else 1.,
              "gate_before_verification":valid>=8 and pos>neg}
        save(out,{"utc":now(),"authors_sha256":sha(self.path/"PUBLIC_AUTHORS.json"),"primary":prim,"models":models,"blocks":pairs})
        print("Scientific scoring closed.",flush=True)

    def freeze(self):
        import tempfile
        out=self.path/"FREEZE.json"
        if out.exists():raise FileExistsError("Already registered")
        check=self.case.fixture()
        groups=[("tiny",np.arange(8,dtype=float)+2,np.arange(8,dtype=float)+3)]
        stub={"model_spec":{},"generator_py":"import numpy as np\nimport pandas as pd\ndef generate(observed,spec,seed):\n    i=np.arange(len(spec['groups'][0]['x']))\n    return pd.DataFrame({'row_id':i,'paired_index':i})\n"}
        parts,_=self.execute(stub,groups,19,Path(tempfile.mkdtemp(dir=self.private)))
        assert np.array_equal(parts[0],np.arange(8))
        def fixture(v):return {"usable":True,"fixed":4,"draws":[{"outcome":{"requested":x}} for x in v]}
        assert self.compare(fixture([0,0,0]),fixture([2*self.case.MARGIN]*3))["material"]
        assert not self.compare(fixture([0,0,0]),fixture([0,0,0]))["material"]
        assert not self.compare(fixture([0,0,0]),fixture([0,3*self.case.MARGIN,3*self.case.MARGIN]))["material"]
        save(out,{"utc":now(),"design":self.design(),"fixture":{"source":check,"isolated_executor":True,"matched_thresholds":True}})
        print("Registered",self.name)


def request_bytes(s):return len(json.dumps(client.make_request(CFG,s)[1],ensure_ascii=False).encode())


def task(name,n):
    t={"schema_version":1,"task_id":"matched_article_"+name,"mode":"whole_cohort","population":"Source population with fixed published strata",
       "row_id":"row_id","n_rows":n,"columns":[{"name":k,"kind":"integer","unit":"","role":r,"nullable":False}
       for k,r in (("row_id","identifier"),("paired_index","generated"))],
       "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
       "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    harness.contracts.validate_task(t);return t


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("publication",choices=("iron","grip"));ap.add_argument("action",choices=("freeze","dispatch","score"))
    args=ap.parse_args();study=Publication(args.publication)
    study.private.mkdir(parents=True,exist_ok=True)
    with FileLock(str(study.private/"study.lock"),timeout=0):
        getattr(study,args.action)()

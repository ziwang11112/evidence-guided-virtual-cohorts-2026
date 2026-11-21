"""Freeze, request, and seal prospective scientific-use decisions. Never opens the new reference."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import random
import sys

from design import HERE, KEYS, OLD, SENS, PRIVATE, obj, save, read, digest, text_digest, now

PROVIDER = HERE.parent/"cross_model_api_pilot_2026-11-10"
sys.path.insert(0, str(PROVIDER))
import provider_client as provider

MODEL = "OA_SOL"
SYSTEM = "You are a scientific adviser evaluating a frozen virtual cohort. Use only the permitted case material. Return an auditable usage recommendation in the specified JSON format."
provider.SYSTEM = SYSTEM
provider.MAX_OUTPUT = 4800
provider.CAPS = {"openai": .95}
provider.CONFIGS[MODEL] = {**provider.CONFIGS[MODEL], "effort":"medium"}


def parse_response(text):
    def unique(pairs):
        out = {}
        for k,v in pairs:
            if k in out:
                raise ValueError("Repeated key")
            out[k]=v
        return out
    s=text.strip()
    if s.startswith("\x60\x60\x60") and s.endswith("\x60\x60\x60"):
        s=s[s.find("\n")+1:-3].strip()
    res=json.loads(s,object_pairs_hook=unique)
    if not isinstance(res,dict) or set(res)!={"ranking","uses","limitation"}:
        raise ValueError("Invalid response fields")
    if not isinstance(res["ranking"],list) or len(res["ranking"])!=len(KEYS) or set(res["ranking"])!=set(KEYS):
        raise ValueError("Ranking must be a permutation of all uses")
    if not isinstance(res["uses"],dict) or set(res["uses"])!=set(KEYS):
        raise ValueError("Missing or unexpected use")
    for item in res["uses"].values():
        if not isinstance(item,dict) or set(item)!={"endorse","reason"} or type(item["endorse"]) is not bool:
            raise ValueError("Invalid scientific decision")
        if not isinstance(item["reason"],str) or not 1<=len(item["reason"])<=1400:
            raise ValueError("Missing concise rationale")
    if not isinstance(res["limitation"],str) or not 1<=len(res["limitation"])<=1400:
        raise ValueError("Missing limitation")
    return res


def schedule():
    arms=["full"]*4+["reduced"]*4
    random.Random(711223).shuffle(arms)
    return dict(zip([f"session{i}" for i in range(1,9)], arms))


def prompt(arm):
    cases=obj(HERE/"PACKET.json")["cases"]
    for v in cases.values():
        if arm=="reduced":
            v.pop("alternative_models_range")
    note = ("\nThe additional column is the minimum and maximum across ten explicitly constructed joint structures. "
            "Eight author scenarios and two numerical examples preserve the same empirical TC and HDL marginals, "
            "physiological ordering and the reported rounded mean individual ratio. These are stress scenarios with no probability weights.\n"
            if arm=="full" else "\n")
    return read(HERE/"REQUEST.txt")+note+json.dumps(cases, ensure_ascii=False,allow_nan=False,indent=2)


def bound():
    paths=[*(HERE/f for f in ("PROTOCOL.md","ADMISSION.md","ADMISSION.json","design.py","packet.py","admission.py",
                              "advisors.py","evaluate.py","REQUEST.txt","PACKET.json","STATISTICAL_DECISION.json")),
           OLD/"SOURCE.json",OLD/"MODEL_CLOSURE.json",SENS/"SENSITIVITY.json",SENS/"CONTROL.json",
           PROVIDER/"provider_client.py"]
    return {p.relative_to(HERE.parents[1]).as_posix():text_digest(p) for p in paths}


def unit_tests():
    raw={"uses":{k:{"endorse":False,"reason":"x"} for k in KEYS},"limitation":"y","ranking":KEYS}
    assert parse_response(json.dumps(raw))==raw
    for bad in ({**raw,"ranking":KEYS[:-1]},{**raw,"uses":{}},{**raw,"limitation":""}):
        try:
            parse_response(json.dumps(bad))
        except ValueError:
            continue
        raise AssertionError("Invalid fixture accepted")
    from design import estimands,interval_class
    import numpy as np
    from scipy.stats import spearmanr
    a=np.array([200.,199.,200.,6.2*38.67]);b=np.array([40.,40.,40.,38.67])
    r=estimands(a,b)
    assert r[4]==75 and r[2]==25 and r[3]==0
    assert np.isclose(r[-1],spearmanr(a,b).statistic)
    assert [interval_class(x,y,2) for x,y in ((-2,2),(2,3),(2.01,4),(-4,-2.01))]==["within","unresolved","contradicted","contradicted"]
    assert "alternative_models_range" in prompt("full") and "alternative_models_range" not in prompt("reduced")


def freeze():
    unit_tests()
    costs={}
    for arm in ("full","reduced"):
        _,body=provider.make_request(MODEL,prompt(arm))
        config=provider.CONFIGS[MODEL]
        n=len(json.dumps(body,ensure_ascii=False).encode())
        costs[arm]=((n+4096)*max(config["input_rate"],config["cache_write_rate"])+provider.MAX_OUTPUT*config["output_rate"])/1e6
    assert 4*sum(costs.values())<=provider.CAPS["openai"]
    for arm in ("full","reduced"):
        path=HERE/f"PROMPT_{arm}.txt"
        if path.exists():
            assert read(path)==prompt(arm)
        else:
            with path.open("x",encoding="utf-8",newline="\n") as stream:
                stream.write(prompt(arm))
    save(HERE/"FREEZE.json",{"time":now(),"bindings":bound(),"schedule":schedule(),"model":provider.CONFIGS[MODEL],
         "system_message":SYSTEM,"max_output":provider.MAX_OUTPUT,"cap":provider.CAPS["openai"],
         "reservation_by_arm":costs,"prompts":{arm:text_digest(HERE/f"PROMPT_{arm}.txt") for arm in costs},
         "target_scientific_outcomes_accessed":False})


def guard():
    fr=obj(HERE/"FREEZE.json")
    assert fr["bindings"]==bound() and fr["schedule"]==schedule()
    assert fr["model"]==provider.CONFIGS[MODEL] and fr["system_message"]==SYSTEM
    assert fr["max_output"]==provider.MAX_OUTPUT and fr["cap"]==provider.CAPS["openai"]
    for arm in ("full","reduced"):
        assert fr["prompts"][arm]==text_digest(HERE/f"PROMPT_{arm}.txt") and read(HERE/f"PROMPT_{arm}.txt")==prompt(arm)
    return fr


def call(item):
    key,arm=item
    record,decision=provider.call_once(PRIVATE/"api",key,MODEL,prompt(arm))
    keep=("status","requested_model","returned_model","request_sha256","response_text.txt_sha256","usage","tariff_cost_usd",
          "started_utc","ended_utc","mechanical_error","api_error_code","completion_status","stop_reason")
    data={k:record.get(k) for k in keep}
    success=record.get("status")=="received" and decision is not None
    return key,{"arm":arm,"valid":success,"decision":decision if success else None,"receipt":data}


def dispatch():
    guard()
    if (HERE/"REFERENCE_OPEN.json").exists() or (HERE/"DECISION_CLOSURE.json").exists():
        raise RuntimeError("Decisions already closed")
    provider.parse_artifact=parse_response
    with ThreadPoolExecutor(max_workers=4) as pool:
        records=dict(pool.map(call,schedule().items()))
    save(HERE/"DECISION_CLOSURE.json",{"sealed":now(),"freeze_sha256":text_digest(HERE/"FREEZE.json"),
         "statistical_sha256":text_digest(HERE/"STATISTICAL_DECISION.json"),"sessions":records,
         "target_outcomes_opened":False})
    print([(k,v["arm"],v["valid"],v["receipt"]["tariff_cost_usd"]) for k,v in records.items()])


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("stage",choices=["freeze","dispatch"])
    args=p.parse_args()
    (freeze if args.stage=="freeze" else dispatch)()

"""One-call evidence-choice pilot. No reference data are parsed by this module."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
import tempfile

import requests
from filelock import FileLock

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORK = HERE.parent
RUNTIME = WORK / "article_autonomy_design_2026-11-22"
sys.path.insert(0, str(RUNTIME))
import author_stage as author
import runtime_stage as sandbox

transport = author.transport
PUBLIC = ("PROTOCOL.md", "REQUEST.txt", "COMMON_PROMPT.txt", "ARM_ordinary.txt",
          "ARM_targeted.txt", "SOURCE_AND_SCHEMA.md", "RUBRIC.md", "DESIGN_REVIEW.md",
          "blind_review.py", "evaluate_trial.py", "run_trial.py")
PRIVATE = HERE / "private"
API = PRIVATE / "api"
ARMS = ("ordinary", "targeted")
SEEDS = (251131, 251137, 251143)
N = 10000
TOKENS = 11000
CAP = 1.75
TOTAL = 14.0
LIMITS = {"episode_usd_cap": CAP, "total_usd_cap": TOTAL, "max_input_bytes": 175000,
          "max_output_tokens": TOKENS}
SYSTEM = author.SYSTEM


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return transport.read(Path(path))


def put(path, value):
    """Atomically persist a write-once result while under the project command lock."""
    path = Path(path)
    if path.exists():
        if read(path) != value:
            raise ValueError(f"Existing immutable artifact differs: {path.name}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix="pending-", delete=False) as tmp:
        tmp.write(json.dumps(value, ensure_ascii=False, allow_nan=False,
                             sort_keys=True, indent=2).encode("utf8") + b"\n")
        tmp.flush()
        os.fsync(tmp.fileno())
    os.replace(tmp.name, path)


def order():
    rng = random.Random(251103)
    blocks = list(range(1, 5))
    rng.shuffle(blocks)
    return [(b, a) for b in blocks for a in rng.sample(ARMS, 2)]


def slot_id(block, arm):
    return f"b{block:02d}_{arm}"


def private_bindings():
    return read(PRIVATE / "input_paths.json")


def checked_files():
    # Includes all local transport, authentication, schema, worker and execution code.
    files = [HERE / n for n in PUBLIC]
    files.extend([RUNTIME / "author_stage.py", RUNTIME / "runtime_stage.py",
                  Path(transport.__file__), Path(author.client.__file__),
                  WORK / "cross_model_api_pilot_2026-11-10/provider_preflight.py",
                  WORK / "economy_feedback_pilot_2026-11-10/budget_keys.py"])
    files.extend(sorted((PROJECT / "cohort_harness").glob("*.py")))
    return {p.relative_to(PROJECT).as_posix(): sha(p) for p in files}


def request_body(inputs, arm):
    if arm not in ARMS:
        raise ValueError("Unknown arm")
    parts = [(HERE/"REQUEST.txt").read_text(encoding="utf8"),
             (HERE/"COMMON_PROMPT.txt").read_text(encoding="utf8"),
             (HERE/f"ARM_{arm}.txt").read_text(encoding="utf8"),
             "BEGIN ORIGINAL ARTICLE\n" + Path(inputs["source"]).read_text(encoding="utf8") +
             "\nEND ORIGINAL ARTICLE"]
    return {"model": transport.MODEL, "instructions": SYSTEM, "input": "\n\n".join(parts),
            "store": False, "reasoning": {"effort": "medium"}, "service_tier": "default",
            "max_output_tokens": TOKENS, "text": {"format": {"type": "json_object"}}}


def study_design(inputs):
    if transport.MODEL != "gpt-6.1-sol" or N != 10000:
        raise ValueError("Unexpected registered model or sample size")
    # Only a streamed byte digest is computed for the reference, including before unblinding.
    digests = {k:sha(inputs[k]) for k in ("source", "reference")}
    if digests["source"] == digests["reference"]:
        raise ValueError("Reference was provided as source")
    entries = []
    for block, arm in order():
        body = transport.encoded(request_body(inputs, arm))
        if len(body) > LIMITS["max_input_bytes"]:
            raise ValueError("Author request exceeds byte cap")
        allowance = len(body) + 4096
        rates = transport.DEFAULT_RATES
        charge = ((allowance * max(rates["input_rate"], rates["cache_write_rate"],
                                   rates["cached_rate"]) + TOKENS * rates["output_rate"]) / 1e6)
        if allowance > transport.LONG_CONTEXT_THRESHOLD or charge > CAP:
            raise ValueError("Individual request is outside the reserved budget")
        entries.append({"block":block, "arm":arm, "slot":slot_id(block,arm),
                        "request_sha256":hashlib.sha256(body).hexdigest(),
                        "upper_reserved_usd":charge})
    if sum(x["upper_reserved_usd"] for x in entries) > TOTAL:
        raise ValueError("Planned campaign exceeds budget")
    runtime = sandbox.execution._runtime(None)
    manifest = sandbox.execution._runtime_manifest(runtime)
    runtime_fingerprint = hashlib.sha256(transport.encoded(manifest)).hexdigest()
    return {"inputs":digests, "extra_evaluation_digests":[sha(x) for x in inputs["audit_inputs"]],
            "files":checked_files(), "sandbox_manifest_sha256":runtime_fingerprint,
            "sandbox_backend":runtime["backend"], "model":transport.MODEL, "seeds":list(SEEDS),
            "order_seed":251103, "n":N, "limits":LIMITS, "tariff":transport.DEFAULT_RATES,
            "order":entries}


def freeze(source, reference, extras):
    bindings = {"source":str(Path(source).resolve(strict=True)),
                "reference":str(Path(reference).resolve(strict=True)),
                "audit_inputs":[str(Path(p).resolve(strict=True)) for p in extras]}
    if API.exists() and not (HERE/"FREEZE.json").is_file():
        raise ValueError("Cannot freeze after dispatch")
    data = study_design(bindings)
    put(PRIVATE / "input_paths.json", bindings)
    path = HERE / "FREEZE.json"
    if path.exists():
        require_equal(read(path)["design"], data, "Existing frozen design differs")
    else:
        put(path, {"frozen_utc":transport.utc(), "design":data})
    return data


def require_equal(left, right, why):
    if left != right:
        raise ValueError(why)


def guard():
    saved = read(HERE / "FREEZE.json")["design"]
    require_equal(study_design(private_bindings()), saved, "Frozen inputs, implementation, or runtime changed")
    return saved


def slot_folder(slot):
    return API / "episodes" / slot / "calls" / "0001"


def issued_rows():
    allowed = {slot_id(*p) for p in order()}
    if API.exists():
        for d in (API/"episodes").glob("*/calls/*"):
            if d.parent.parent.name not in allowed or d.name != "0001":
                raise ValueError("Unregistered call directory")


def make_call(entry):
    slot = entry["slot"]
    body = request_body(private_bindings(), entry["arm"])
    require_equal(hashlib.sha256(transport.encoded(body)).hexdigest(), entry["request_sha256"],
                  "Prompt differs from freeze")
    folder = slot_folder(slot)
    if not folder.exists():
        keys = author.client.credentials()
        if not keys.get("openai"):
            raise RuntimeError("Configured OpenAI credential unavailable")
        dest, reason = transport.reserve(API, slot, 1, body, LIMITS, transport.DEFAULT_RATES)
        if dest is None:
            raise RuntimeError("Reservation failed: " + reason)
        transport.send_once(dest, requests.post, author.client.headers("openai",keys["openai"]),
                            keys.values(), transport.DEFAULT_RATES)
    # Never send a second request for an outstanding reservation.
    return inspect_call(entry)


def inspect_call(entry):
    slot = entry["slot"]
    folder = slot_folder(slot)
    if not (folder/"receipt.json").exists():
        raise RuntimeError(f"Unsettled or missing call for {slot}; no duplicate dispatch")
    rec = read(folder/"receipt.json")
    require_equal(sha(folder/"request.json"), entry["request_sha256"], "Request bytes changed")
    require_equal(rec["request_sha256"], entry["request_sha256"], "Wrong request receipt")
    require_equal(sha(folder/"reservation.json"), rec["reservation_sha256"], "Reservation changed")
    reservation = read(folder/"reservation.json")
    require_equal((reservation["episode_id"],reservation["call_number"],reservation["request_sha256"]),
                  (slot,1,entry["request_sha256"]), "Reservation identity mismatch")
    if not math.isclose(rec["reserved_usd"],entry["upper_reserved_usd"],abs_tol=1e-12):
        raise ValueError("Reservation differs from registered ceiling")
    if rec.get("response_raw_sha256"):
        require_equal(sha(folder/"response_raw.json"),rec["response_raw_sha256"],"Response changed")
    if rec.get("reservation_exceeded") or rec["reserved_usd"] > CAP:
        raise RuntimeError("Per-author reservation exceeded")
    fields = ("requested_model","returned_model","status","completion_status","usage",
              "tariff_cost_usd","reserved_usd","request_sha256","response_raw_sha256")
    meta = {k:rec.get(k) for k in fields}
    meta.update(slot=slot, block=entry["block"], arm=entry["arm"], receipt_sha256=sha(folder/"receipt.json"),
                candidate_sha256=None, candidate_status="no_deliverable")
    if rec["status"] == "received":
        require_equal(rec.get("returned_model"), transport.MODEL, "Unexpected returned model")
        try:
            result = author.client.extract_response("openai",read(folder/"response_raw.json"))
            candidate = author.decode(result["text"])
        except (KeyError,ValueError,TypeError):
            meta["candidate_status"]="invalid_output_json"
        else:
            path = PRIVATE/"candidates"/(slot+".json")
            put(path, candidate)
            meta["candidate_sha256"] = sha(path)
            meta["candidate_status"] = "captured"
    return meta


def authors_report(design):
    issued_rows()
    rows = [inspect_call(e) for e in design["order"]]
    billed = sum(r["tariff_cost_usd"] or 0 for r in rows)
    held = transport.accounted(API)
    if billed > TOTAL or held > TOTAL:
        raise RuntimeError("Campaign exceeds total budget")
    return {"freeze_sha256":sha(HERE/"FREEZE.json"), "authors":rows, "selected_slots":len(rows),
            "known_tariff_usd":billed, "accounted_or_reserved_usd":held,
            "unknown_cost_count":sum(r["tariff_cost_usd"] is None for r in rows)}


def dispatch():
    design = guard()
    issued_rows()
    for entry in design["order"]:
        if transport.accounted(API) > TOTAL:
            raise RuntimeError("Outstanding budget exceeded")
        row = make_call(entry)
        print(row["slot"],row["status"],row["candidate_status"],row["tariff_cost_usd"],flush=True)
    put(HERE/"AUTHORS.json",authors_report(design))


def verify_authors():
    expected = authors_report(guard())
    require_equal(expected,read(HERE/"AUTHORS.json"),"Sealed constructor inventory differs")
    return expected["authors"]


def eligible_artifact(candidate):
    if set(candidate) != {"model_spec","decision_record","generator_py"}:
        return False
    spec = candidate.get("model_spec")
    if not isinstance(spec,dict) or not isinstance(candidate["decision_record"],dict):
        return False
    fields = spec.get("columns")
    if not isinstance(fields,list) or not all(isinstance(x,dict) for x in fields):
        return False
    return ([x.get("name") for x in fields] == ["reported_bmi","measured_bmi"] and
            all(x.get("unit")=="kg/m2" for x in fields) and isinstance(candidate["generator_py"],str))


def execution_result(slot, candidate):
    # If a local execution was interrupted, retain it and use a fresh private
    # directory for the same three seeds. No API call is repeated.
    paths = [PRIVATE/"draws"/slot]
    paths.extend(sorted((PRIVATE/"draw_recovery").glob(f"{slot}-*")))
    for p in paths:
        if (p/"result.json").is_file():
            return p
    base = paths[0]
    if base.exists():
        base = PRIVATE/"draw_recovery"/f"{slot}-{len(paths):03d}"
    base.parent.mkdir(parents=True,exist_ok=True)
    sandbox.execute(candidate["model_spec"],candidate["generator_py"],base,SEEDS,N)
    return base


def record_draws(row, base=None):
    slot = row["slot"]
    candidate = read(PRIVATE/"candidates"/(slot+".json")) if row["candidate_sha256"] else None
    if candidate is None:
        status = "no_candidate"
    elif not eligible_artifact(candidate):
        status = "invalid_candidate_schema"
    elif base is None:
        raise ValueError("Missing generated-output directory")
    else:
        result = read(base/"result.json")
        status = result["status"]
        if result["runs"]:
            require_equal((base/"generator.py").read_text(encoding="utf8"),
                          candidate["generator_py"].replace("\r\n","\n").replace("\r","\n"),
                          "Generator differs from returned model code")
            require_equal(read(base/"model_spec.json"),{**candidate["model_spec"],"n":N},
                          "Executed model specification differs")
    runpaths = {}
    if base is not None:
        for s in read(base/"result.json")["runs"]:
            if s["seed"] in runpaths or s["seed"] not in SEEDS:
                raise ValueError("Duplicate or unregistered output seed")
            runpaths[s["seed"]] = s
    draws = []
    for seed in SEEDS:
        run = runpaths.get(seed)
        d = {"seed":seed, "status":"unavailable", "path":None, "sha256":None}
        if run is not None:
            receipt_path=base/f"seed_{seed}"/"execution.json"
            require_equal(read(receipt_path),run,"Isolated execution receipt changed")
            d.update(status=run["status"],execution_sha256=sha(receipt_path))
            if run["status"]=="success":
                csv = base/f"seed_{seed}"/"output"/"generated.csv"
                require_equal(Path(run["table"]).resolve(),csv.resolve(),"Unexpected executed-table path")
                require_equal(sha(csv),run["sha256"],"Generated table digest differs")
                d.update(path=csv.relative_to(HERE).as_posix(),sha256=sha(csv))
        draws.append(d)
    return {"slot":slot,"block":row["block"],"arm":row["arm"],"status":status,
            "candidate_sha256":row["candidate_sha256"],"draws":draws,
            "run_path":base.relative_to(HERE).as_posix() if base else None,
            "result_sha256":sha(base/"result.json") if base else None}


def generate():
    rows=verify_authors()
    outputs=[]
    for row in rows:
        path=PRIVATE/"candidates"/(row["slot"]+".json")
        c=read(path) if row["candidate_sha256"] else None
        base=execution_result(row["slot"],c) if c is not None and eligible_artifact(c) else None
        outputs.append(record_draws(row,base))
        print(row["slot"],outputs[-1]["status"],flush=True)
    put(HERE/"DRAWS.json",{"authors_sha256":sha(HERE/"AUTHORS.json"),"slots":outputs})


def verified_draws():
    rows=verify_authors()
    manifest=read(HERE/"DRAWS.json")
    require_equal(manifest["authors_sha256"],sha(HERE/"AUTHORS.json"),"Author seal differs")
    require_equal([x["slot"] for x in manifest["slots"]],[r["slot"] for r in rows],"Draw roster mismatch")
    results=[]
    for row,sealed in zip(rows,manifest["slots"],strict=True):
        base=(HERE/sealed["run_path"]).resolve() if sealed["run_path"] else None
        if base and not base.is_relative_to(PRIVATE):
            raise ValueError("Draw folder outside private root")
        actual=record_draws(row,base)
        require_equal(actual,sealed,"Sealed draw artifacts changed")
        actual["candidate"]=PRIVATE/"candidates"/(row["slot"]+".json") if row["candidate_sha256"] else None
        for d in actual["draws"]:
            if d["path"]:
                d["path"]=HERE/d["path"]
        results.append(actual)
    return results


def reference_after_seal():
    verified_draws()
    return Path(private_bindings()["reference"])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    subs=parser.add_subparsers(dest="action",required=True)
    freezer=subs.add_parser("freeze")
    freezer.add_argument("--source",required=True)
    freezer.add_argument("--reference",required=True)
    freezer.add_argument("--audit-input",action="append",default=[])
    for action in ("dispatch","draws","verify","preflight"):
        subs.add_parser(action)
    args=parser.parse_args()
    with FileLock(str(HERE/"run.lock"),timeout=0):
        if args.action=="freeze":
            print("Frozen", len(freeze(args.source,args.reference,args.audit_input)["order"]), "author slots")
        elif args.action=="preflight":
            d=guard()
            print("Verified",len(d["order"]),"requests; cumulative reserved ceiling",
                  round(sum(x["upper_reserved_usd"] for x in d["order"]),4))
        elif args.action=="dispatch":
            dispatch()
        elif args.action=="draws":
            generate()
        else:
            print("Verified",sum(len(r["draws"]) for r in verified_draws()),"registered draw slots")


if __name__=="__main__":
    main()

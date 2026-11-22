"""Frozen, paired article-to-generator API experiment. Scientific outputs stay blind until closure."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import random
import sys

from filelock import FileLock
from lxml import etree

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PILOT = HERE.parent / "evidence_composition_pilot_2026-11-16"
sys.path.insert(0, str(PILOT))
sys.dont_write_bytecode = True
import pilot as harness

client = harness.client
CONFIG = "OA_SOL"
client.CONFIGS[CONFIG] = {**client.CONFIGS[CONFIG], "effort": "medium"}
client.MAX_OUTPUT = 12000
client.CAPS = {"openai": 18.0}
PRIVATE = HERE / "private"
API = PRIVATE / "api"
OLD = HERE.parent / "nonhdl_external_2026-11-20"
XML = OLD / "private/source.xml"
BLOCKS = tuple(f"B{i:02d}" for i in range(1, 13))
ARMS = ("ordinary", "alternative")
SEEDS = (520221, 520223, 520229)
N = 16000
INSTRUCTIONS = {
    "initial": "Construct your best single scientifically defensible model for the requested use.",
    "ordinary": "Given the initial author's submission, construct another scientifically defensible candidate for the same research request. Use your own judgment in selecting its scientific structure and parameters.",
    "alternative": "Given the initial author's submission, construct another scientifically defensible candidate for the same research request. Specifically seek a different within-person assignment that fits the same published evidence but changes the screening estimate by a scientifically meaningful amount. No direction or target value is specified.",
}
read = harness.read
sha = harness.sha
save = client.dump_new


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def text_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def words(element):
    return " ".join("".join(element.itertext()).split())


def article():
    tree = etree.parse(str(XML), etree.XMLParser(resolve_entities=False, no_network=True))
    doi = tree.findtext('.//article-id[@pub-id-type="doi"]')
    if doi != "10.1371/journal.pone.0223189":
        raise ValueError("Wrong original article")
    parts = [words(tree.find(".//article-title")), "DOI " + doi]
    for source in (tree.find(".//article-meta/abstract"), tree.find(".//body")):
        section = deepcopy(source)
        for table in section.xpath(".//table-wrap"):
            lines = [table.findtext("label") + ". " + words(table.find("caption"))]
            for row in table.xpath(".//tr"):
                lines.append(" | ".join(words(cell) for cell in row.xpath("./th|./td")))
            lines.extend(words(foot) for foot in table.xpath("./table-wrap-foot"))
            section_data = etree.Element("table-text")
            section_data.text = "\n".join(lines)
            section_data.tail = table.tail
            table.getparent().replace(table, section_data)
        for el in section.iter():
            if el.tag in ("title", "p", "table-text") and not any(
                ancestor.tag in ("title", "p", "table-text") for ancestor in el.iterancestors()
            ):
                parts.append(el.text if el.tag == "table-text" else words(el))
    return "\n\n".join(parts)


def make_prompt(arm, parent=None):
    base = (HERE / "REQUEST.txt").read_text(encoding="utf-8").strip()
    paper = article()
    instruction = INSTRUCTIONS[arm]
    previous = "" if parent is None else "\n\nINITIAL SUBMISSION\n" + canonical(parent)
    return f"{base}\n\nORIGINAL ARTICLE\n{paper}{previous}\n\nAUTHORING REQUEST\n{instruction}"


def paths():
    return [
        HERE / "PROTOCOL.md", HERE / "REQUEST.txt", HERE / "experiment.py",
        HERE / "evaluation.py", old_path("science.py"), old_path("SOURCE.json"),
        HERE.parent / "kdd_v40_pairing_review_2026-11-20/scoring.py",
        PILOT / "pilot.py", PROJECT / "cohort_harness/execution.py", harness.WORKER,
        HERE.parent / "cross_model_api_pilot_2026-11-10/provider_client.py",
        HERE.parent / "cross_model_api_pilot_2026-11-10/provider_preflight.py",
    ]


def old_path(name):
    return OLD / name


def bindings():
    return {p.relative_to(PROJECT).as_posix(): sha(p) for p in paths()}


def schedule():
    rng = random.Random(11222026)
    arms = {b: list(ARMS) for b in BLOCKS}
    for choices in arms.values():
        rng.shuffle(choices)
    start = list(BLOCKS)
    rng.shuffle(start)
    return start, arms


def freeze():
    if (HERE / "FREEZE.json").exists():
        raise FileExistsError("Freeze already exists")
    from evaluation import preflight
    checks = preflight()
    full = make_prompt("initial")
    body = client.make_request(CONFIG, full)[1]
    count = len(json.dumps(body, ensure_ascii=False).encode())
    rate = client.CONFIGS[CONFIG]
    def reserve(byte_count):
        return ((byte_count + 4096) * max(rate["input_rate"], rate["cache_write_rate"])
                + client.MAX_OUTPUT * rate["output_rate"]) / 1e6
    # All follow-ups are bounded by the existing client maximum request size.
    upper = len(BLOCKS) * (reserve(count) + 2 * reserve(190000))
    if upper > client.CAPS["openai"] or count > 190000:
        raise ValueError("Total worst-case allowance exceeds this batch's cap")
    start, arms = schedule()
    save(HERE / "FREEZE.json", {
        "utc": now(), "files": bindings(), "source_xml_sha256": sha(XML),
        "source_render_sha256": text_hash(article()), "initial_prompt_sha256": text_hash(full),
        "branch_instruction_sha256": {k: text_hash(v) for k, v in INSTRUCTIONS.items()},
        "system_sha256": text_hash(client.SYSTEM), "model": rate, "cap_usd": client.CAPS["openai"],
        "max_output_tokens": client.MAX_OUTPUT, "max_calls": 3*len(BLOCKS),
        "max_reservation_all_slots_usd": upper, "initial_request_bytes": count,
        "seeds": SEEDS, "initial_order": start, "branch_order": arms, "fixture": checks,
        "historical_target_exposure": True, "target_used_in_this_experiment": False,
    })


def guard():
    f = read(HERE / "FREEZE.json")
    if not (f["files"] == bindings() and f["source_xml_sha256"] == sha(XML)
            and f["source_render_sha256"] == text_hash(article())
            and f["initial_prompt_sha256"] == text_hash(make_prompt("initial"))
            and f["system_sha256"] == text_hash(client.SYSTEM)
            and f["model"] == client.CONFIGS[CONFIG] and f["seeds"] == list(SEEDS)
            and f["cap_usd"] == client.CAPS["openai"] and f["max_output_tokens"] == client.MAX_OUTPUT
            and f["branch_instruction_sha256"] == {k: text_hash(v) for k, v in INSTRUCTIONS.items()}):
        raise RuntimeError("Registered input or executable changed")
    return f


def artifact(name):
    d = API / "calls" / name
    if not (d / "receipt.json").exists():
        return None
    receipt = read(d / "receipt.json")
    p = d / "artifact.json"
    if receipt.get("status") != "received" or receipt.get("returned_model") != client.CONFIGS[CONFIG]["model"] or not p.is_file():
        return None
    if sha(p) != receipt["artifact.json_sha256"]:
        raise RuntimeError("Model artifact changed")
    return read(p)


def call(name, prompt):
    folder = API / "calls" / name
    if folder.is_dir():
        if not (folder / "receipt.json").is_file():
            raise RuntimeError("Unsettled reservation exists for " + name)
        rec = read(folder / "receipt.json")
        if sha(folder / "prompt.txt") != rec["prompt_sha256"] or (folder / "prompt.txt").read_text(encoding="utf-8") != prompt:
            raise RuntimeError("Previously issued prompt differs")
    else:
        rec, _ = client.call_once(API, name, CONFIG, prompt)
    keys = ("requested_model", "returned_model", "started_utc", "ended_utc", "status",
            "artifact_status", "api_error_code", "stop_reason", "usage", "response_id",
            "tariff_cost_usd", "request_sha256", "prompt_sha256", "response_text.txt_sha256", "artifact.json_sha256")
    return {k: rec.get(k) for k in keys}


def dispatch():
    f = guard()
    if (HERE / "AUTHORS.json").exists():
        return
    with ThreadPoolExecutor(max_workers=6) as pool:
        initials = list(pool.map(lambda b: call(b + "_initial", make_prompt("initial")), f["initial_order"]))
        records = {b + "_initial": r for b, r in zip(f["initial_order"], initials, strict=True)}
        print("Initial API submissions closed.", flush=True)
        tasks = [(b, a) for b in f["initial_order"] for a in f["branch_order"][b]]
        def branch(task):
            block, arm = task
            parent = artifact(block + "_initial")
            if parent is None:
                return {"status": "unissued_missing_initial_artifact"}
            prompt = make_prompt(arm, parent)
            if len(json.dumps(client.make_request(CONFIG, prompt)[1], ensure_ascii=False).encode()) > 190000:
                return {"status": "unissued_request_too_large"}
            return call(block + "_" + arm, prompt)
        for (block, arm), rec in zip(tasks, pool.map(branch, tasks), strict=True):
            records[block + "_" + arm] = rec
    save(HERE / "AUTHORS.json", {"closed_utc": now(), "freeze_sha256": sha(HERE / "FREEZE.json"),
        "calls": records, "accounted_usd": client.ledger_accounted(API, "openai")})
    print("All author slots closed.", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["freeze", "dispatch", "score"])
    action = ap.parse_args().action
    PRIVATE.mkdir(parents=True, exist_ok=True)
    with FileLock(str(PRIVATE / "experiment.lock"), timeout=0):
        if action == "freeze":
            freeze()
        elif action == "dispatch":
            dispatch()
        else:
            from evaluation import evaluate
            evaluate()


if __name__ == "__main__":
    # Imported scoring code uses the same study state in command-line and module execution.
    sys.modules["experiment"] = sys.modules[__name__]
    main()

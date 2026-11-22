"""Register and run the matched original-article experiment without exposing outcomes to authors."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import random
import sys

from filelock import FileLock
from lxml import etree

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PRIOR = HERE.parent / "article_pairing_2026-11-22"
LUNG = HERE.parent / "spirometry_pairing_2026-11-21"
XML = LUNG / "private/source_epmc.xml"
PRIVATE = HERE / "private"
API = PRIVATE / "api"
sys.path.insert(0, str(PRIOR))
import experiment as previous

client, harness = previous.client, previous.harness
read, save, sha, now = previous.read, previous.save, previous.sha, previous.now
canonical, text_hash, words = previous.canonical, previous.text_hash, previous.words
INSTRUCTIONS, BLOCKS, ARMS, CONFIG = previous.INSTRUCTIONS, previous.BLOCKS, previous.ARMS, previous.CONFIG
N = 8000
SEEDS = (522221, 522223, 522229)


def article():
    tree = etree.parse(str(XML), etree.XMLParser(resolve_entities=False, no_network=True))
    doi = tree.findtext('.//article-id[@pub-id-type="doi"]')
    if doi != "10.1186/1465-9921-13-57":
        raise ValueError("Unexpected article")
    regions = [words(tree.find(".//article-title")), "DOI " + doi]
    for original in (tree.find(".//article-meta/abstract"), tree.find(".//body")):
        area = deepcopy(original)
        for table in area.xpath(".//table-wrap"):
            lines = [table.findtext("label") + ". " + words(table.find("caption"))]
            for row in table.xpath(".//tr"):
                lines.append(" | ".join(words(cell) for cell in row.xpath("./td|./th")))
            lines.extend(words(ft) for ft in table.xpath("./table-wrap-foot"))
            el = etree.Element("table-text")
            el.text = "\n".join(lines)
            el.tail = table.tail
            table.getparent().replace(table, el)
        # Emit nested inserts (tables, figures and display math) exactly once, including
        # those within a paragraph; preserve the mathematical fraction and script structure.
        def render(node):
            tag = etree.QName(node).localname
            if tag == "table-text":
                return "\n" + (node.text or "") + "\n"
            if tag == "math":
                parts = [c for c in node if isinstance(c.tag, str)]
                def math_text(m):
                    k = etree.QName(m).localname
                    v = [math_text(c) for c in m if isinstance(c.tag, str)]
                    if k == "mfrac" and len(v) == 2: return "(" + v[0] + ")/(" + v[1] + ")"
                    if k in ("msub", "msup") and len(v) == 2:
                        return v[0] + ("_" if k == "msub" else "^") + "(" + v[1] + ")"
                    return (m.text or "") + "".join(v)
                return "".join(math_text(c) for c in parts)
            content = (node.text or "") + "".join(render(c) + (c.tail or "") for c in node if isinstance(c.tag, str))
            if tag in {"p", "title", "label", "caption", "disp-formula", "fig"}:
                return "\n" + content + "\n"
            return content
        regions.append("\n".join(" ".join(s.split()) for s in render(area).splitlines() if s.strip()))
    return "\n\n".join(regions)


def make_prompt(arm, parent=None):
    task = (HERE / "REQUEST.txt").read_text(encoding="utf8").strip()
    prior = "" if parent is None else "\n\nINITIAL SUBMISSION\n" + canonical(parent)
    return task + "\n\nORIGINAL ARTICLE\n" + article() + prior + "\n\nAUTHORING REQUEST\n" + INSTRUCTIONS[arm]


def bindings():
    files = [HERE / x for x in ("REQUEST.txt", "PROTOCOL.md", "trial.py", "lung.py")]
    files += [PRIOR / "experiment.py", LUNG / "MARGINAL_SOURCE.json", LUNG / "JOINT_SOURCE.json",
              previous.PILOT / "pilot.py", PROJECT / "cohort_harness/execution.py",
              PROJECT / "cohort_harness/contracts.py", harness.WORKER,
              PROJECT / "work/cross_model_api_pilot_2026-11-10/provider_client.py",
              PROJECT / "work/cross_model_api_pilot_2026-11-10/provider_preflight.py"]
    return {f.relative_to(PROJECT).as_posix(): sha(f) for f in files}


def request_bytes(prompt):
    body = client.make_request(CONFIG, prompt)[1]
    return len(json.dumps(body, ensure_ascii=False).encode())


def design():
    rng = random.Random(5222026)
    order = list(BLOCKS)
    rng.shuffle(order)
    branches = {b: rng.sample(list(ARMS), 2) for b in BLOCKS}
    primary = make_prompt("initial")
    cfg = client.CONFIGS[CONFIG]
    size = request_bytes(primary)
    def reserve(n):
        return ((n+4096)*max(cfg["input_rate"], cfg["cache_write_rate"]) +
                client.MAX_OUTPUT*cfg["output_rate"])/1e6
    ceiling = len(order)*(reserve(size)+2*reserve(190000))
    if size > 190000 or ceiling > client.CAPS["openai"]:
        raise ValueError("The planned requests exceed the budget envelope")
    return {"files": bindings(), "source_xml_sha256": sha(XML), "render_sha256": text_hash(article()),
            "initial_prompt_sha256": text_hash(primary), "system_sha256": text_hash(client.SYSTEM),
            "instruction_sha256": {k: text_hash(v) for k,v in INSTRUCTIONS.items()},
            "model": cfg, "cap_usd": client.CAPS["openai"], "max_calls": 36,
            "max_output_tokens": client.MAX_OUTPUT, "max_reservation_usd": ceiling,
            "first_request_bytes": size, "n_per_sex": N, "seeds": list(SEEDS),
            "initial_order": order, "branch_order": branches}


def guard():
    frozen = read(HERE / "FREEZE.json")
    if frozen["design"] != design():
        raise RuntimeError("Frozen design or material changed")
    return frozen["design"]


def artifact(slot):
    folder = API / "calls" / slot
    if not (folder / "receipt.json").exists():
        return None
    receipt = read(folder / "receipt.json")
    out = folder / "artifact.json"
    if receipt["status"] != "received" or receipt.get("returned_model") != client.CONFIGS[CONFIG]["model"] or not out.exists():
        return None
    if sha(out) != receipt["artifact.json_sha256"]:
        raise RuntimeError("Submitted program changed")
    return read(out)


def issue(slot, prompt):
    folder = API / "calls" / slot
    if folder.exists():
        if not (folder/"receipt.json").is_file():
            raise RuntimeError("Unsettled prior API reservation " + slot)
        rec = read(folder/"receipt.json")
        if sha(folder/"prompt.txt") != rec["prompt_sha256"] or (folder/"prompt.txt").read_text(encoding="utf8") != prompt:
            raise RuntimeError("Previously issued request differs")
    else:
        rec, _ = client.call_once(API, slot, CONFIG, prompt)
    fields = ("requested_model","returned_model","started_utc","ended_utc","status","artifact_status",
              "api_error_code","stop_reason","usage","tariff_cost_usd","request_sha256","prompt_sha256",
              "response_text.txt_sha256","artifact.json_sha256")
    return {k: rec.get(k) for k in fields}


def dispatch():
    d = guard()
    if (HERE / "AUTHORS.json").exists(): return
    with ThreadPoolExecutor(max_workers=6) as workers:
        first = make_prompt("initial")
        def start(block): return issue(block + "_initial", first)
        initial = dict(zip((b + "_initial" for b in d["initial_order"]), workers.map(start, d["initial_order"]), strict=True))
        print("Initial author slots closed.", flush=True)
        branch = [(b,a) for b in d["initial_order"] for a in d["branch_order"][b]]
        def follow(job):
            block, arm = job
            obj = artifact(block + "_initial")
            if obj is None: return {"status":"unissued_missing_initial_artifact"}
            prompt = make_prompt(arm, obj)
            if request_bytes(prompt) > 190000: return {"status":"unissued_request_too_large"}
            return issue(block + "_" + arm, prompt)
        initial.update(zip((b+"_"+a for b,a in branch), workers.map(follow, branch), strict=True))
    save(HERE/"AUTHORS.json", {"closed_utc":now(), "freeze_sha256":sha(HERE/"FREEZE.json"),
                              "calls":initial,"accounted_usd":client.ledger_accounted(API,"openai")})
    print("All 36 author slots closed.", flush=True)


def main():
    from lung import evaluate, preflight
    parse = argparse.ArgumentParser()
    parse.add_argument("action", choices=["freeze","dispatch","score"])
    action = parse.parse_args().action
    PRIVATE.mkdir(exist_ok=True)
    with FileLock(str(PRIVATE / "study.lock"), timeout=0):
        if action == "freeze":
            if (HERE/"FREEZE.json").exists(): raise FileExistsError("Already registered")
            receipt = preflight()
            save(HERE/"FREEZE.json", {"utc":now(),"design":design(),"preflight":receipt})
            print("Frozen.")
        elif action == "dispatch": dispatch()
        else: evaluate()


if __name__ == "__main__":
    sys.modules["trial"] = sys.modules[__name__]
    main()

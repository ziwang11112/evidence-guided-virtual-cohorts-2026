"""Prepare masked artifacts and seal independent source-use ratings before unblinding."""
import argparse
import hashlib
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
MASK = HERE / "private" / "mask"
AUTHORS = ("reader_1", "reader_2")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path, content):
    payload = (json.dumps(content, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError("Existing receipt differs: " + path.name)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as file:
            file.write(payload)

def prepare():
    from run_trial import verified_draws
    slots = sorted(verified_draws(), key=lambda r: r["slot"])
    if len(slots) != 8 or len({r["slot"] for r in slots}) != 8:
        raise ValueError("Expected all eight assigned slots")
    rng = random.Random(5182547)
    rng.shuffle(slots)
    mapping = {}
    packet = []
    for i, slot in enumerate(slots, 1):
        label = "case_{:02d}".format(i)
        mapping[label] = slot["slot"]
        candidate = read(Path(slot["candidate"])) if slot["candidate"] else None
        if isinstance(candidate, dict):
            candidate = {k: candidate.get(k) for k in ("decision_record", "generator_py", "model_spec")}
        else:
            candidate = None
        packet.append({"label":label, "submission":candidate})
    save(MASK / "mapping.json", mapping)
    for reader in AUTHORS:
        order = packet.copy()
        rng.shuffle(order)
        save(MASK / reader / "packet.json", order)
    return mapping

def seal():
    from run_trial import verified_draws
    verified_draws()
    labels = set(prepare())
    hashes = {}
    for reader in AUTHORS:
        folder = MASK / reader
        data = read(folder / "ratings.json")
        if set(data) != labels or not all(isinstance(v,dict) and v for v in data.values()):
            raise ValueError("Missing masked case ratings for " + reader)
        hashes[reader] = {key:digest(folder / key) for key in ("ratings.json","packet.json")}
    consensus = MASK / "consensus.json"
    if set(read(consensus)) != labels:
        raise ValueError("Missing dispositions in masked consensus")
    save(HERE / "REVIEW_SEAL.json", {"readers":hashes,"consensus_sha256":digest(consensus),
        "label_key_sha256":digest(MASK/"mapping.json"),"rubric_sha256":digest(HERE/"RUBRIC.md")})

def require_review():
    receipt=read(HERE / "REVIEW_SEAL.json")
    for reader in AUTHORS:
        for item,sha in receipt["readers"][reader].items():
            if sha != digest(MASK/reader/item):
                raise ValueError("Changed review input: " + reader + " " + item)
    for name, path in (("consensus_sha256", MASK/"consensus.json"),
                       ("label_key_sha256", MASK/"mapping.json"),("rubric_sha256", HERE/"RUBRIC.md")):
        if receipt[name] != digest(path):
            raise ValueError("Changed blinded review or rubric")

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["prepare","seal","check"])
    cmd=parser.parse_args().action
    if cmd=="prepare":
        prepare()
        print("Masked packets ready for two independent readers.")
    elif cmd=="seal":
        seal()
        print("Ratings and adjudication sealed.")
    else:
        require_review()
        print("Masked review verified.")

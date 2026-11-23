"""Local hash records for the prospective pre-call and pre-reveal boundaries."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UNIT = HERE.parent / "article_autonomy_design_2026-11-22"
EPISODE = UNIT / "private/replay_v2/p01"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(stage):
    files = [
        HERE / name for name in ("DESIGN.md", "REQUEST.txt", "READER_A.md", "READER_B.md",
                                "evaluate.py", "test_evaluate.py", "seal.py", "source_text.py",
                                "private/source.xml", "private/article.txt", "private/sealed.xlsx")]
    files += list((UNIT / "evidence_replay").glob("*.py"))
    files += [UNIT / name for name in ("run_with_evidence_replay.py", "author_stage.py",
                                      "run_candidate_stage.py", "runtime_stage.py")]
    if stage == "precall" and EPISODE.exists():
        raise RuntimeError("Cannot register a new design after a session exists")
    if stage == "prereveal":
        original = json.loads((HERE / "PRECALL.json").read_text(encoding="utf8"))
        for rel, original_hash in original["files"].items():
            if sha(ROOT / rel) != original_hash:
                raise ValueError("Precall file changed: " + rel)
        files += [HERE / "PRECALL.json", HERE / "PREREVEAL_READING.md"]
        files += [EPISODE / name for name in (
            "design_as_authored.json", "source_inventory.json", "build.json", "review.json",
            "trial_manifest.json", "final_manifest.json", "final_source_replay.json")]
        files += sorted(EPISODE.glob("episodes/development/calls/*/receipt.json"))
        manifest = json.loads((EPISODE / "final_manifest.json").read_text(encoding="utf8"))
        for row in manifest["runs"]:
            if row["status"] == "success":
                path = Path(row["table"])
                if sha(path) != row["sha256"]:
                    raise ValueError("Final generated table differs from receipt")
                files.append(path)
    hashes = {path.relative_to(ROOT).as_posix(): sha(path) for path in files}
    record = {"stage":stage, "time_utc":datetime.now(timezone.utc).isoformat(),"files":hashes}
    with (HERE / (stage.upper() + ".json")).open("x", encoding="utf8") as handle:
        json.dump(record, handle, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["precall","prereveal"])
    main(parser.parse_args().stage)

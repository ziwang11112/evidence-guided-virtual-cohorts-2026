"""Materialize connector-fetched base64 blobs; verify Git bytes before saving.

Reads the five approved public text/code artifacts from stdin, never source IPD.
This helper does not retrieve URLs, import authors' R code, fit, or generate.
"""
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

UNIT = Path(__file__).resolve().parents[1]
REPOSITORY = "powerepilab/Sim_for_data_pooling"
COMMIT = "6708e43d5e342fa76d57b31d5a6d0bfcc2979539"
EXPECTED = {
    "HRSmodels_20200902_fullDemoTable.txt": "2943aab557016db49da1791398c510bae18c74bb",
    "HRS_sim_data_code_postGitHub_20200728.R": "40bd9c505a2f1d3226c4ffc51572ba8124ec1593",
    "RCTSim1_postGitHub_20200728.R": "55dfe0ad34896f173bee5a140ff034a3b2d82ccb",
    "RCTSim2_postGitHub_20200728.R": "2ab7a9788c628c7f7fdf92f2d83272fb1d608d89",
    "README.md": "8ec150ff743f21e5e4a69685c762e91c41f787c0",
}


def main():
    incoming = json.load(sys.stdin)
    if len(incoming) != len(EXPECTED) or {x["name"] for x in incoming} != set(EXPECTED):
        raise ValueError("Unexpected source set")
    verified = []
    for item in incoming:
        raw = base64.b64decode(item["content_base64"], validate=True)
        def git_hash(value):
            return hashlib.sha1(b"blob " + str(len(value)).encode("ascii") + b"\0" + value).hexdigest()
        encoding, conversion = "utf-8", "none"
        if git_hash(raw) != EXPECTED[item["name"]]:
            # The file connector decodes legacy Windows text before base64 output.
            # Accept an inverse conversion only when its exact Git blob matches.
            raw = raw.decode("utf-8").encode("cp1252")
            encoding = "cp1252"
            conversion = "inverse of connector UTF-8 normalization to Windows-1252; exact Git blob verified"
        if git_hash(raw) != item["git_blob_sha"] or git_hash(raw) != EXPECTED[item["name"]]:
            raise ValueError("Git blob byte mismatch: " + item["name"])
        raw.decode(encoding)
        expected_url = f"https://github.com/{REPOSITORY}/blob/{COMMIT}/{item['name']}"
        if item["url"] != expected_url:
            raise ValueError("Wrong pinned source URL")
        destination = UNIT / "sources" / "original" / item["name"]
        if destination.exists():
            raise FileExistsError(destination)
        verified.append((item, raw, destination, encoding, conversion))
    manifest_path = UNIT / "sources" / "SOURCE_MANIFEST.json"
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    records = []
    for item, raw, destination, encoding, conversion in verified:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(raw)
        records.append({"path": destination.relative_to(UNIT).as_posix(),
                        "url": item["url"], "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "git_blob_sha1": item["git_blob_sha"],
                        "git_blob_verified": True, "encoding": encoding,
                        "byte_recovery": conversion,
                        "origin": "GitHub connector fetch_file encoding=base64"})
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(),
                "repository": REPOSITORY, "commit": COMMIT,
                "source_kind": "public source code and aggregate parameter exports; no participant records",
                "license": "No explicit repository license found; original files stay local and are not relicensed.",
                "registration_status": "pending coordinator review; not an approval record",
                "files": records}
    with manifest_path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(manifest, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"verified_originals": len(records), "manifest": str(manifest_path),
                      "bytes": sum(x["bytes"] for x in records)}, indent=2))


if __name__ == "__main__":
    main()

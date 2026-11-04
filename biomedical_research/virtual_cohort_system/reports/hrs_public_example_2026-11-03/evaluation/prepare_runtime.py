"""Extract only required Ubuntu R binary packages into a project runtime.

Run in WSL Ubuntu 24.04; no apt install, sudo, or system-library mutation.
Package bytes/hashes and apt SHA256 are recorded. Dependency-download budget
is separate from patient/source acquisition and cumulative across invocations.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "runtime"
DEBS = RUNTIME / "debs"
EXTRACT = RUNTIME / "extracted"
LEDGER = RUNTIME / "DEPENDENCY_DOWNLOADS.json"
BUDGET = 200 * 1024**2


def command(args):
    return subprocess.check_output(args, text=True).strip()


def main():
    DEBS.mkdir(parents=True, exist_ok=True)
    EXTRACT.mkdir(parents=True, exist_ok=True)
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {
        "budget_bytes": BUDGET, "patient_data": False,
        "installation_mode": "dpkg-deb extraction to project; no system changes",
        "records": [], "downloaded_bytes": 0,
    }
    for package in sys.argv[1:]:
        metadata = command(["apt-cache", "show", package]).split("\n\n")[0]
        meta = dict(line.split(": ", 1) for line in metadata.splitlines() if ": " in line and not line.startswith(" "))
        version = meta["Version"]
        existing = next((r for r in ledger["records"] if r["package"] == package and r["version"] == version), None)
        if existing:
            path = DEBS / existing["file"]
            if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == existing["sha256"]:
                print("Already recorded", package, version)
                continue
            raise RuntimeError("Recorded archive missing or changed: " + package)
        filename = Path(meta["Filename"]).name
        path = DEBS / filename
        cache = Path("/var/cache/apt/archives") / filename
        network = not cache.exists()
        expected_size = int(meta["Size"])
        if expected_size > BUDGET or ledger["downloaded_bytes"] + (expected_size if network else 0) > BUDGET:
            raise RuntimeError("Dependency download budget would be exceeded")
        if cache.exists():
            shutil.copy2(cache, path)
        else:
            subprocess.run(["apt-get", "download", package + "=" + version], cwd=DEBS, check=True)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        actual = path.stat().st_size
        if digest != meta["SHA256"] or actual != expected_size:
            raise RuntimeError("apt size/hash mismatch for " + package)
        subprocess.run(["dpkg-deb", "-x", str(path), str(EXTRACT)], check=True)
        record = {"package": package, "version": version, "file": filename,
                  "actual_bytes": actual, "sha256": digest, "apt_sha256": meta["SHA256"],
                  "apt_repository_path": meta["Filename"], "network_download": network,
                  "created_utc": datetime.now(timezone.utc).isoformat()}
        ledger["records"].append(record)
        ledger["downloaded_bytes"] += actual if network else 0
        LEDGER.write_text(json.dumps(ledger, indent=2) + "\n")
        print("Prepared", package, version, actual)
    print("New network bytes cumulatively:", ledger["downloaded_bytes"])


if __name__ == "__main__":
    main()

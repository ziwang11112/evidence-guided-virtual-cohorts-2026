import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path("work/review_revision_2026-11-08/controlled_joint_moments").resolve()
sys.path.insert(0,str(root));import runner
review=json.loads((root/"IMPLEMENTATION_REVIEW.json").read_text(encoding="utf8"))
print("REVIEW",review.get("decision",review.get("status")))
assert not runner.inventory()
files=runner.required_batch_files()
lock={"created_utc":datetime.now(timezone.utc).isoformat(),"records":{f:runner.sha(root/f) for f in sorted(files)},"engine_sha256":runner.engine_hashes(),"truth_sha256":runner.read(root/"DESIGN_LOCK.json")["records"]["custodian/TRUTH.json"],"implementation_review_sha256":runner.sha(root/"IMPLEMENTATION_REVIEW.json")}
with (root/"BATCH_LOCK.json").open("x",encoding="utf8") as f:json.dump(lock,f,indent=2)
runner.verify_batch()
print("SEALED",len(files),"inputs; 12 fixed attempts; no outputs yet")


"""One-shot continuation of the already running, frozen target campaign.

This is foreground job orchestration, not a scheduler or an evaluation bypass.
It never generates, repairs, retries, or alters scientific candidates.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys
import time

N = Path(__file__).resolve().parent
P = N.parent.parent
W = P.parent.parent
L = W / "evcDC/ledger"
ENGINE = P / "work/developmental_revision_pilot_v1_2026-11-02/implementation"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def state_update(**fields):
    state = read(N / "STATE.json")
    state.update(fields, updated_utc=utc())
    temporary = N / "STATE.finisher.tmp"
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(N / "STATE.json")


def main():
    start = time.monotonic()
    write_new(N / "EVALUATION_ORCHESTRATION_INTENT.json", {
        "pid": os.getpid(), "started_utc": utc(),
        "purpose": "Wait for the existing target process to close, then invoke the unchanged released evaluators once",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "no_generation_or_retries": True,
        "controller_gate": "actual released controller; no fixture or caller-supplied inventory",
    })
    try:
        deadline = start + 3 * 60 * 60
        while read(N / "STATE.json").get("phase") != "target_inventory_closed":
            if time.monotonic() > deadline:
                raise TimeoutError("Existing target process did not close within the bounded wait")
            time.sleep(5)
        closed = read(N / "CLOSED_INVENTORY.json")
        if closed.get("status") != "closed" or not closed.get("scientific_closed"):
            raise RuntimeError("Target closure receipt is incomplete")
        sys.path.insert(0, str(ENGINE))
        import pilot_controller_v1 as controller
        import pilot_evaluation_v1 as primary
        import independent_pilot_recompute as independent
        c = controller.PilotController.open(L)
        authorization = c.authorize_evaluation(c.release["evaluator"]["sha256"])
        write_new(N / "EVALUATION_AUTHORIZATION.json", authorization)
        state_update(phase="authorized_frozen_evaluation", next="primary_then_independent_evaluation")
        print("Actual controller authorized frozen evaluation after target closure.", flush=True)
        primary_result = primary.evaluate(L)
        write_new(N / "PRIMARY_EVALUATION_DISPOSITION.json", primary_result)
        print(json.dumps(primary_result), flush=True)
        independent_result = independent.recompute(L)
        write_new(N / "INDEPENDENT_EVALUATION_DISPOSITION.json", independent_result)
        print(json.dumps(independent_result), flush=True)
        status = independent_result.get("status")
        state_update(phase="independent_evaluation_complete" if status == "matched" else "independent_evaluation_disagreement",
                     independent_status=status, next="complete_report_claim_review_and_public_sync")
        write_new(N / "EVALUATION_ORCHESTRATION_COMPLETION.json", {
            "completed_utc": utc(), "elapsed_seconds_including_wait": time.monotonic() - start,
            "primary": primary_result, "independent": independent_result,
        })
    except Exception as error:
        write_new(N / "EVALUATION_ORCHESTRATION_FAILURE.json", {
            "failed_utc": utc(), "error_type": type(error).__name__, "message": str(error),
            "elapsed_seconds_including_wait": time.monotonic() - start, "automatic_retry": False,
        })
        raise


if __name__ == "__main__":
    main()

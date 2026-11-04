"""Bind actual final author decisions; never supplies scientific parameters."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    protocol = read(ROOT / "PROTOCOL.json")
    closure = {"protocol_sha256": sha(ROOT / "PROTOCOL.json"), "requests": {}}
    for key, bundle_path in protocol["bundles"].items():
        bundle = Path(bundle_path)
        decision_file = bundle / "FINAL_DECISION.json"
        decision = read(decision_file)
        assert decision["choice"] in ("retain", "revise")
        candidate = decision["candidate"]
        assert (bundle / candidate).resolve().is_relative_to(bundle.resolve())
        assert (bundle / candidate / "freeze.json").is_file()
        prefix = "initial_delivery" if decision["choice"] == "retain" else "final_delivery"
        initial = [f"{key.lower()}_initial_delivery_{seed}" for seed in (7301, 7302, 7303)]
        final = [f"{key.lower()}_{prefix}_{seed}" for seed in (7301, 7302, 7303)]
        for run_id in initial + final:
            assert (ROOT / "sessions" / key / (run_id + "_result.json")).is_file()
        closure["requests"][key] = {
            "author_closed": True,
            "choice": decision["choice"],
            "initial_candidate": "candidates/initial",
            "final_candidate": candidate,
            "decision_file": "FINAL_DECISION.json",
            "decision_sha256": sha(decision_file),
            "delivery_runs": {"initial": initial, "final": final},
        }
    closure["created_utc"] = datetime.now(timezone.utc).isoformat()
    with (ROOT / "LIVE_CLOSURE.json").open("x", encoding="utf-8") as stream:
        json.dump(closure, stream, indent=2, allow_nan=False)
        stream.write("\n")
    state = read(ROOT / "STATE.json")
    physical = []
    retrieval = {}
    for key, bundle_path in protocol["bundles"].items():
        session = ROOT / "sessions" / key
        physical.extend(read(f) for f in session.glob("*_result.json"))
        retrieval[key] = read(Path(bundle_path) / "gateway/session/state.json")["usage"]
    state.update(status="both_authors_closed_awaiting_reference_evaluation",
                 scientific_generations=sum(bool(x.get("generator_executed")) for x in physical),
                 physical_attempts=len(physical),
                 successful_executions=sum(x.get("execution_status") == "success" for x in physical),
                 retrieval=retrieval,
                 queries=sum(x["queries"] for x in retrieval.values()),
                 closure_sha256=sha(ROOT / "LIVE_CLOSURE.json"))
    state["interventions"].append({
        "actor": "coordinator_agent_then_scientific_author_B",
        "action": "Coordinator caught divergent exp(positive*lognormal BMI) moments before freeze; B preserved draft and chose positive linear BMI mean multipliers. No source-discrepancy or target-result feedback used."
    })
    (ROOT / "STATE.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"closure_sha256": state["closure_sha256"], "physical_attempts": len(physical)}, indent=2))


if __name__ == "__main__":
    main()

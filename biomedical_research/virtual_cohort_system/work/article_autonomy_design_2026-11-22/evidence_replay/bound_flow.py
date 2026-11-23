"""Bind operation input units to the author's original schema before any trial."""
import json
from pathlib import Path

from filelock import FileLock

from . import flow
from .bind_units import bind_design


def _verified_submission(donor, number):
    folder = donor/"episodes"/"development"/"calls"/f"{number:04d}"
    read = flow.author.transport.read
    receipt = read(folder/"receipt.json")
    for key,name in (("request_sha256","request.json"),("reservation_sha256","reservation.json"),
                     ("response_raw_sha256","response_raw.json")):
        if receipt.get(key) != flow.author.transport.sha(folder/name):
            raise ValueError("The retained initial API capture differs from its receipt")
    if receipt["status"] != "received" or receipt["returned_model"] != flow.author.transport.MODEL:
        raise ValueError("Invalid retained initial API receipt")
    text = flow.author.client.extract_response("openai",read(folder/"response_raw.json"))["text"]
    return flow.author.decode(text)


def _initial(donor, article, request):
    read = flow.author.transport.read
    binding = read(donor/"replay_binding.json")
    if (binding["article_text_sha256"] != flow.author.sha(article.encode())
            or binding["request_sha256"] != flow.author.sha(request.encode())
            or binding["model"] != flow.author.transport.MODEL):
        raise ValueError("The retained article, research request or model does not match")
    design,build = [read(donor / (name+".json")) for name in ("design","build")]
    if design != _verified_submission(donor,1) or build != _verified_submission(donor,2):
        raise ValueError("Retained design or generator differs from its original API response")
    return design,build


def run(root,article,request,*,donor=None,send=None):
    read = flow.author.transport.read
    store = flow.execution.record
    root = Path(root).resolve()
    root.mkdir(parents=True,exist_ok=True)
    donor = Path(donor).resolve() if donor is not None else None
    if donor == root:
        raise ValueError("A fixed-initial comparison needs a new run directory")
    transmit = flow._send if send is None else send
    with FileLock(str(root/"units.lock"),timeout=0):
        initial = _initial(donor,article,request) if donor is not None else None
        store(root/"unit_binding_version.json",{
            "version":2,"adapter_sha256":flow.author.transport.sha(Path(__file__)),
            "compiler_sha256":flow.author.transport.sha(Path(__file__).with_name("bind_units.py")),
            "initial_mode":"retained_design_and_build" if initial else "new_design_and_build",
            "donor_trial_sha256":flow.author.transport.sha(donor/"trial_manifest.json") if initial else None})

        def dispatch(session,stage,prompt,cap):
            if stage == "design":
                raw = initial[0] if initial else transmit(session,stage,prompt,cap)
                store(root/"design_as_authored.json",raw)
                normalized,bindings = bind_design(raw)
                store(root/"unit_bindings.json",{"raw_design_sha256":flow.core.digest(raw),
                      "bound_design_sha256":flow.core.digest(normalized),"items":bindings})
                return normalized
            if stage == "build" and initial:
                return initial[1]
            if stage == "review" and initial:
                def fingerprints(manifest):
                    return [(r["scenario"],r["seed"],r["status"],r.get("sha256")) for r in manifest["runs"]]
                old = read(donor/"trial_manifest.json")
                new = read(root/"trial_manifest.json")
                if (old["candidate_sha256"] != new["candidate_sha256"] or not new["runs"]
                        or any(r["status"] != "success" for r in new["runs"])
                        or fingerprints(old) != fingerprints(new)
                        or read(donor/"trial_public.json") != read(root/"trial_public.json")):
                    raise RuntimeError("Cannot attribute feedback to the same initial scientific tables")
                store(root/"retained_initial_verification.json",{
                    "design_sha256":flow.core.digest(initial[0]),"candidate_sha256":new["candidate_sha256"],
                    "trial_tables":fingerprints(new),"generated_only_diagnostics_identical":True})
            return transmit(session,stage,prompt,cap)

        return flow.run(root,article,request,send=dispatch)

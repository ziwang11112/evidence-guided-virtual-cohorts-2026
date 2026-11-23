"""Article authoring with frozen source statements and measurement-level replay."""
import json
from pathlib import Path
import sys

from filelock import FileLock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import author_stage as author
import run_candidate_stage as execution
from . import core


DESIGN_LEDGER = """For evidence, return an object containing evidence_checks, the authoritative inventory of the material source quantities you will use or propose to check. Record one entry per scalar and stratum. Include material facts that do not support a numerical replay as unresolved. If none exist, return an empty array and no_evidence_reason. Choose the measurements, source locations, statistics and scientific model yourself.

Each entry has id (stable ASCII identifier), source (paper location), claim, population, provenance ('reported', 'derived' or 'assumed'), applicability ('same_population','transport_assumption' or 'unknown'), reference and either operator or unresolved (a reason). A reference is {value,unit,decimals}; decimals is the exact printed precision for a reported scalar or null if only a numerical difference is justified. For a nonnumerical unresolved claim the reference can be null. For adjusted estimates supply adjustment as a list of the actual adjustment covariates. A reported count requires source_n for the original total if raw counts are directly comparable. Prefer comparable proportions if synthesizing a different sample size, and label such derived values. Do not choose a precision from simulated results. Distinguish uncertainty intervals from printed precision.

Operators use case-neutral names for the numeric measurement columns you plan to generate. The required units object maps every referenced measurement or grouping column to its unit. For optional where (list of AND filters), event, exposure and outcome, each predicate is {column,cmp,value} with numeric value and cmp in eq,ne,lt,le,gt,ge. Use the same numeric group encoding in the scientific specification and generator. Supported kinds: mean or geometric_mean uses y; sd uses y plus ddof (0 or 1); pearson, spearman, ols_slope, ols_intercept, r_squared use x (predictor) and y (outcome). For r_squared declare scale 'percent' or 'fraction'. count uses no y. proportion and percentage use event; odds_ratio uses exposure and outcome and is crude. All supported operations are unweighted. Include any necessary weighted, adjusted or compound calculation as unresolved with its reason if you cannot express it faithfully. Unit labels are literal: '1' for proportions, correlations or odds ratios, '%' for percentages, 'count' for counts, outcome unit for intercepts, '1' for equal-unit slopes, otherwise outcome/predictor units."""
BUILD_LINK = """Your evidence inventory is fixed before sampling. Write independently runnable measurements with column names, units and coding consistent with the design. The runtime computes the registered checks on those measurements. You may change modeling choices without replacing the source references or operators."""
REVIEW_LINK = """Use the item-level source replay to decide which requested conclusions are supported. For each ID that is outside reported precision, on a rounding boundary, descriptive-only, unresolved, not comparable, not computable, or without a table, put an explanation or corrective action in dispositions (an object mapping each ID to a reason). For empty coverage, qualify the overall conclusion. You may keep, revise or abstain. A rounding discrepancy is a diagnostic; consider sample size, population, meaning and precision. The frozen inventory also applies to your final submission."""


def _send(root, stage, prompt, cap):
    number = author.STAGES.index(stage) + 1
    folder = root/"episodes"/"development"/"calls"/f"{number:04d}"
    def verify_receipt():
        receipt = author.transport.read(folder/"receipt.json")
        for key, name in (("request_sha256","request.json"),("reservation_sha256","reservation.json"),
                          ("response_raw_sha256","response_raw.json")):
            if receipt.get(key) != author.transport.sha(folder/name):
                raise RuntimeError("API capture integrity mismatch: " + name)
    if (folder/"receipt.json").exists():
        verify_receipt()
    obj = author.call(root, number, prompt, cap)
    verify_receipt()
    return obj


def _validate_review(obj):
    if (obj.get("action") not in ("keep","revise","abstain") or not core.text_field(obj.get("reason"))
            or "conclusions" not in obj):
        raise ValueError("Invalid model review disposition")
    if obj["action"] == "revise":
        author.client.parse_artifact(json.dumps(obj["candidate"]))


def _run(root, article, request, send):
    if (root / "input_binding.json").exists():
        raise ValueError("Use a new run identifier. A legacy run exists at this location.")
    bindings = [Path(__file__), HERE/"core.py", HERE/"ops.py", Path(author.__file__),
                Path(execution.__file__), HERE.parent/"runtime_stage.py", execution.WORKER,
                Path(author.client.__file__),Path(author.transport.__file__),
                HERE.parents[2]/"cohort_harness/source_checks.py"]
    execution.record(root/"replay_binding.json",{
        "version":1,"model":author.transport.MODEL,"effort":"medium",
        "article_text_sha256":author.sha(article.encode()),"request_sha256":author.sha(request.encode()),
        "files":{p.name:author.sha(p.read_bytes()) for p in bindings},
        "trial_seed":author.DIAGNOSTIC_SEED,"final_seeds":list(author.SEEDS),"n":author.N,
        "max_calls":3,"episode_usd_cap":1.75})
    base = ["Research request\n" + request, "Full article\n" + article]
    design_prompt = "\n\n".join(base + [author.DESIGN, DESIGN_LEDGER])
    design = send(root, "design", design_prompt, 7500)
    if not {"population","columns","evidence","analyses","model_plan","limitations"} <= design.keys():
        raise ValueError("Missing scientific design fields")
    execution.record(root/"design.json",design)
    evidence = design["evidence"]
    items = core.inventory(evidence)
    execution.record(root/"source_inventory.json", evidence)
    prior = ["Your pre-execution scientific design\n" + json.dumps(design), author.BUILD, BUILD_LINK]
    build = send(root, "build", "\n\n".join(base + prior), 11500)
    build = author.client.parse_artifact(json.dumps(build))
    execution.record(root/"build.json", build)
    trial = execution.stage(root, "trial")
    trial_replay = core.replay(root,"trial",evidence,build,trial)
    execution.record(root/"trial_source_replay.json",trial_replay)
    feedback = core.review_feedback(trial_replay)
    execution.record(root/"source_feedback_sent.json",feedback)
    review_prompt = "\n\n".join(base + prior + [
        "Your initial submission\n" + json.dumps(build),
        "Generated-only diagnostics\n" + json.dumps(author.transport.read(root/"trial_public.json")),
        "Independent calculations on your trial rows using your declared source evidence\n" + json.dumps(feedback),
        author.REVIEW.replace("Independent checks and measured results are unavailable to you.",
                              "The independent evaluator and measured participant results are unavailable to you."), REVIEW_LINK])
    review = send(root,"review",review_prompt,11500)
    _validate_review(review)
    execution.record(root/"review.json",review)
    required = core.needs_disposition(trial_replay)
    dispositions = review.get("dispositions")
    supplied = {k for k,v in dispositions.items() if core.text_field(v)} if isinstance(dispositions,dict) else set()
    reconciliation = {"required":sorted(required),"unacknowledged":sorted(required-supplied),
                      "unknown_ids":sorted(supplied - {i["id"] for i in items}),
                      "trial_feedback_sha256":core.digest(feedback), "action":review["action"]}
    execution.record(root/"review_coverage.json",reconciliation)
    final = execution.stage(root,"final")
    candidate = review["candidate"] if review["action"] == "revise" else build
    report = core.replay(root,"final",evidence,candidate,final)
    report["review_reconciliation"] = reconciliation
    report["dispositions_complete"] = not (reconciliation["unacknowledged"] or reconciliation["unknown_ids"])
    report["final_numerically_recomputed"] = sum("value" in c for r in report["runs"] for c in r["checks"])
    execution.record(root/"final_source_replay.json",report)
    return report


def run(root, article, request, *, send=None):
    root = Path(root).resolve()
    root.mkdir(parents=True,exist_ok=True)
    with FileLock(str(root/"driver.lock"),timeout=0):
        return _run(root, article, request, _send if send is None else send)

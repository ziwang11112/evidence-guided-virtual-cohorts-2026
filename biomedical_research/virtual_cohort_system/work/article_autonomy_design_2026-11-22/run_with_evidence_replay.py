"""Run the source-replay version of the scientific agent on one supplied paper."""
import argparse
import json
from pathlib import Path

from evidence_replay import flow

HERE = Path(__file__).resolve().parent


def send_new_design(root, stage, prompt, cap):
    if stage == "design":
        prompt += (
            "\n\nDeclare columns as a list of objects with name and unit, including the code "
            "and meaning of each grouping variable. When the units of every operand appear "
            "in that list, the runtime can bind them by exact column name. An explicit "
            "units map on an operation must agree with those declarations."
        )
    return flow._send(root, stage, prompt, cap)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--article",type=Path,required=True)
    requests = p.add_mutually_exclusive_group(required=True)
    requests.add_argument("--case", help="Key in development_requests.json")
    requests.add_argument("--request-file",type=Path,help="A new user's research request as UTF-8 text")
    p.add_argument("--run",required=True)
    p.add_argument("--reuse-initial-run",help="Reuse a verified v1 design and candidate in a new v2 review run")
    args = p.parse_args()
    if not args.run.isidentifier() or (args.reuse_initial_run and not args.reuse_initial_run.isidentifier()):
        raise ValueError("Use an opaque run identifier")
    request = (args.request_file.read_text(encoding="utf8") if args.request_file else
               json.loads((HERE/"development_requests.json").read_text(encoding="utf8"))[args.case])
    article = args.article.read_text(encoding="utf8").replace("\f","\n[Page break]\n")
    v1 = HERE/"private"/"replay_v1"
    v2 = HERE/"private"/"replay_v2"
    if (v1/args.run).exists() and not args.reuse_initial_run and not (v2/args.run).exists():
        final = flow.run(v1/args.run, article, request)
    else:
        from evidence_replay.bound_flow import run
        donor = v1/args.reuse_initial_run if args.reuse_initial_run else None
        final = run(v2/args.run, article, request, donor=donor,
                    send=None if donor is not None else send_new_design)
    print(final["execution_status"], final["declared_count"], "source entries,", len(final["runs"]), "final tables")

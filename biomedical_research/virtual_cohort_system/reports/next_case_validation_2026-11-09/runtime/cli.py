"""Host entrypoint. No command launches a model or bypasses the native sandbox."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import controller as c

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="command",required=True)
    for name in ("bindings","batch-seal","verify-batch"): sub.add_parser(name)
    s=sub.add_parser("start"); s.add_argument("--author",required=True); s.add_argument("--dispatch-record",required=True)
    s=sub.add_parser("act"); s.add_argument("--author",required=True); s.add_argument("--id",required=True); s.add_argument("--action",required=True); s.add_argument("--review")
    s=sub.add_parser("select-seal"); s.add_argument("--author",required=True); s.add_argument("--decision",required=True); s.add_argument("--review",required=True)
    s=sub.add_parser("search-receipt"); s.add_argument("--author",required=True); s.add_argument("--id",required=True); s.add_argument("--receipt",required=True)
    s=sub.add_parser("status"); s.add_argument("--author",required=True)
    s=sub.add_parser("decision-bindings"); s.add_argument("--author",required=True)
    a=p.parse_args(argv)
    if a.command=="bindings": result=c.bindings()
    elif a.command=="start": result=c.start(a.author,a.dispatch_record)
    elif a.command=="act": result=c.act(a.author,a.id,c.read(a.action),a.review)
    elif a.command=="select-seal": result=c.select_seal(a.author,a.decision,a.review)
    elif a.command=="search-receipt": result=c.search_receipt(a.author,a.id,a.receipt)
    elif a.command=="status": result=c.status(a.author)
    elif a.command=="decision-bindings": result=c.decision_bindings(a.author)
    elif a.command=="batch-seal": result=c.batch_seal()
    else: result=c.verify_batch_seal()
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=="__main__": main()

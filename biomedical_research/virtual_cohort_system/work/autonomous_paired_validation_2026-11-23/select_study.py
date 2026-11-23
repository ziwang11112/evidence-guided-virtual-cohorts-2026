"""Select a study by model-directed search within an outcome-blind access screen."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from filelock import FileLock

HERE = Path(__file__).resolve().parent
BASE = HERE.parent/"search_to_model_2026-11-22"
sys.path.insert(0,str(BASE))
import run as scientific
from retrieve import Retrieval
from search_audit import check
from verify_model import checked_bundle


def read_eligible(path):
    rows = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(rows,list) or not 2 <= len(rows) <= 8:
        raise ValueError("Supply two to eight metadata-screened independent candidate papers")
    registry = {}
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get("pmcid"),str):
            raise ValueError("Missing eligible PMCID")
        pmcid,doi = row["pmcid"],row.get("doi")
        if not re.fullmatch(r"PMC[1-9]\d*",pmcid) or pmcid in registry:
            raise ValueError("Invalid or duplicate eligible PMCID")
        if not isinstance(doi,str) or not re.fullmatch(r"10\.\d{4,9}/[A-Za-z0-9._();:/-]+",doi):
            raise ValueError("Missing or invalid eligible DOI")
        if doi.casefold() in registry.values():
            raise ValueError("Duplicate eligible DOI")
        registry[pmcid] = doi.casefold()
    return dict(sorted(registry.items()))


class EligibleArticles:
    def __init__(self, gateway, registry):
        self.gateway = gateway
        self.registry = registry

    def search(self,query):
        ids = " OR ".join(f'DOI:"{doi}"' for doi in self.registry.values())
        actual = f"({query}) AND ({ids})"
        if len(actual)>1650:
            return {"status":"invalid_argument","query":query,"hits":[],"reason":"Shorten the topic query"}
        result = self.gateway.search(actual)
        hits = []
        for item in result.get("hits",[]):
            pmcid = item["pmcid"]
            if pmcid not in self.registry or item.get("doi","").casefold() != self.registry[pmcid]:
                continue
            hits.append({key:item.get(key) for key in ("pmcid","doi","title","journal","year")})
        return {"status":result["status"],"query":query,"hits":hits,
                "registered_ids":list(self.registry),
                "screen":"Only bibliographic records from the registered access screen are eligible. "
                         "A public same-study record was identified by metadata for each. "
                         "To see the complete pool, search OPEN_ACCESS:Y. Open articles to assess scientific fit."}

    def open(self,pmcid):
        if pmcid not in self.registry:
            raise ValueError("Article outside screened access list")
        return self.gateway.open(pmcid)

    def seal(self,selected):
        if len(selected)!=1 or selected[0] not in self.registry:
            raise ValueError("Select one target study within the screened access list")
        return self.gateway.seal(selected)


def conduct(root,request_path,eligible_path):
    root.mkdir(parents=True,exist_ok=True)
    request = request_path.read_text(encoding="utf8")
    registry = read_eligible(eligible_path)
    with FileLock(str(root/"selection.lock"),timeout=0):
        scientific.persist(root/"binding.json",{
            "research_request_sha256":hashlib.sha256(request.encode()).hexdigest(),
            "eligible_metadata_sha256":scientific.transport.sha(eligible_path),
            "eligible_ids":list(registry),"public_search_fields":["pmcid","doi","title","journal","year"],
            "policy_sha256":scientific.transport.sha(Path(__file__)),
            "retrieval_sha256":scientific.transport.sha(BASE/"retrieve.py"),
            "discovery_sha256":scientific.transport.sha(BASE/"run.py"),"model":scientific.transport.MODEL,
            "source_budget":scientific.LIMITS,"decision_limit":scientific.MAX_DECISIONS,
            "search_usd_cap":1.25})
        backend=EligibleArticles(Retrieval(root/"retrieval"),registry)
        def decision(session,number,prompt):
            payload=json.loads(prompt)
            payload["selection_scope"]=("The accessible study pool was registered using metadata before any outcome was "
                "inspected. Choose your search terms and one target paper. Your first action may search OPEN_ACCESS:Y "
                "to retrieve the bibliography of all candidates; you may also issue topical queries. "
                "Evaluate the population, measurements and fit to the request. Select exactly one successfully opened "
                "paper or abstain if no article qualifies. Evaluation records and their values are inaccessible.")
            return scientific.read_action(session,number,json.dumps(payload,ensure_ascii=False))
        choice,article=scientific.discover(root,request,backend,decision=decision)
        scientific.persist(root/"selection.json",choice)
        report=check(root)
        if article is not None:
            if checked_bundle(root)!=(article,choice["pmcids"]):
                raise ValueError("Choice does not match authenticated article retrieval")
        scientific.persist(root/"selection_audit.json",report)
        return choice


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for field in ("root","request","eligible"):
        parser.add_argument("--"+field,type=Path,required=True)
    options=parser.parse_args()
    print(json.dumps(conduct(options.root.resolve(),options.request.resolve(),options.eligible.resolve())))

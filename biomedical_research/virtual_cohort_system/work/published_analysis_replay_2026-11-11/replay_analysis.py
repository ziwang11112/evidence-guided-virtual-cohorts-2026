"""One fixed age/sex-residual Pearson operator; no generator or API execution."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import sys
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PAIRS = [("bmi", "total_cholesterol"), ("bmi", "hdl_cholesterol"),
         ("total_cholesterol", "hdl_cholesterol")]
OUTCOMES = ["bmi", "total_cholesterol", "hdl_cholesterol"]
REAL_SHA = "7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9"
SEEDS = [54001, 54003, 54007]
AUTHORS = [f"LIPID_{arm}_R{i}" for arm in ["BASE", "WORKFLOW"] for i in [1,2,3]]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def write_new(path, obj):
    with Path(path).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")

def rel(path):
    return Path(path).relative_to(PROJECT).as_posix()

def now():
    return datetime.now(timezone.utc).isoformat()

def prepare():
    """Bind only manifest metadata and bytes; never parse table content."""
    manifests = []
    inputs = []
    real = PROJECT / "work/scaleup_2026-11-01/private_data/22Jul20_for_Dryad_noIDs.txt"
    assert sha(real) == REAL_SHA
    inputs.append(dict(id="REAL", role="real_reference", episode="REAL", seed=None,
                       path=rel(real), sha256=REAL_SHA, bytes=real.stat().st_size))
    for folder, authors, role in [
        ("request_only_repeatability_2026-11-11", AUTHORS, "initial"),
        ("scientific_check_revision_2026-11-11", ["R04_GENERIC", "R04_STRUCTURED"], "dependent_repair")]:
        base = PROJECT / "work" / folder
        m = base / "FINAL_TABLES.json"
        manifests.append(dict(path=rel(m), sha256=sha(m)))
        slots = read(m)["slots"]
        selected = [s for s in slots if s["episode_id"] in authors]
        assert len(selected) == len(authors)*3
        assert {(s["episode_id"],s["seed"]) for s in selected} == {(a,s) for a in authors for s in SEEDS}
        for a in authors:
            for seed in SEEDS:
                s = next(x for x in selected if x["episode_id"]==a and x["seed"]==seed)
                assert s["status"] == "success"
                path = base / s["generated_path"]
                assert sha(path) == s["generated_sha256"]
                receipt = base / s["receipt_path"]
                assert sha(receipt) == s["receipt_sha256"]
                inputs.append(dict(id=f"{a}_{seed}", episode=a, seed=seed, role=role,
                    path=rel(path), sha256=sha(path), bytes=path.stat().st_size,
                    receipt_path=rel(receipt), receipt_sha256=sha(receipt),
                    candidate_id=s["candidate_id"], parent="LIPID_BASE_R2" if role=="dependent_repair" else None))
    obj = dict(created_utc=now(), tables_parsed=False, planned_tables=25,
               planned_pair_estimates=75, manifests=manifests, inputs=inputs)
    write_new(HERE/"INPUT_BINDINGS.json", obj)
    print("Bound 25 existing table hashes; no participant/synthetic rows parsed.")

def canonicalize(text, real=False):
    names = {"age":"Age", "sex":"Sex", "bmi":"BMI", "total_cholesterol":"Total cholesterol", "hdl_cholesterol":"HDL cholesterol"} if real else {k:k for k in ["age","sex"]+OUTCOMES}
    reader = csv.DictReader(io.StringIO(text), delimiter="\t" if real else ",")
    if not reader.fieldnames or not set(names.values()).issubset(reader.fieldnames):
        raise ValueError("Required schema columns absent")
    rows = []; n=0
    removed = {k:0 for k in ["missing", "nonfinite", "age_not_above_18", "nonpositive_biomarker"]}
    for record in reader:
        n += 1
        d = {key: (record[src] or "").strip() for key,src in names.items()}
        if d["sex"] not in ["", "NA", "F", "M"]:
            raise ValueError("Unrecognized sex token; table withheld")
        try:
            numbers = [None if d[k] in ["", "NA"] else float(d[k]) for k in ["age"]+OUTCOMES]
        except ValueError:
            raise ValueError("Unrecognized numeric token; table withheld") from None
        if any(v in ["", "NA"] for v in d.values()):
            removed["missing"] += 1; continue
        if not np.isfinite(numbers).all():
            removed["nonfinite"] += 1; continue
        age,bmi,tc,hdl = numbers
        if age <= 18:
            removed["age_not_above_18"] += 1; continue
        if min(bmi,tc,hdl) <= 0:
            removed["nonpositive_biomarker"] += 1; continue
        if not real: tc,hdl = tc*38.67,hdl*38.67
        rows.append([age, float(d["sex"]=="F"), bmi,tc,hdl])
    a = np.asarray(rows, dtype=float).reshape((-1,5))
    return a, dict(input_rows=n, retained_rows=len(a), exclusions=removed,
        hdl_above_tc_retained_rows=int(np.sum(a[:,4]>a[:,3])), common_complete_cases=True)

def analyze(a):
    """a = age, indicator(F), BMI, TC, HDL; identical for every dataset."""
    if len(a) <= 5: raise ValueError("Insufficient complete rows")
    x = np.column_stack([np.ones(len(a)), a[:,:2]])
    if np.linalg.matrix_rank(x) != 3: raise ValueError("Rank-deficient nuisance design")
    y = a[:,2:]
    sd = y.std(axis=0, ddof=1)
    if np.any(sd <= np.finfo(float).eps): raise ValueError("Constant biomarker")
    z = (y-y.mean(axis=0))/sd
    beta = np.linalg.lstsq(x,z,rcond=None)[0]
    residual = z-x@beta
    if np.any(residual.std(axis=0,ddof=1) <= 1e-12):
        raise ValueError("Degenerate residual variation")
    corr = np.corrcoef(residual, rowvar=False)
    return [dict(pair=f"{u}__{v}", r=float(corr[OUTCOMES.index(u),OUTCOMES.index(v)]),
                 r_squared=float(corr[OUTCOMES.index(u),OUTCOMES.index(v)]**2)) for u,v in PAIRS]

def verify_inputs(bindings):
    for m in bindings["manifests"]:
        assert sha(PROJECT/m["path"])==m["sha256"],m["path"]
    for d in bindings["inputs"]:
        assert sha(PROJECT/d["path"])==d["sha256"],d["id"]
        if "receipt_path" in d:
            assert sha(PROJECT/d["receipt_path"])==d["receipt_sha256"]

def run():
    assert not (HERE/"ANALYSIS.json").exists(), "Closed batch cannot be silently repeated"
    freeze=read(HERE/"FREEZE.json")
    assert freeze["independent_review_passed"]
    for path,h in freeze["files"].items():
        assert sha(HERE/path)==h,path
    b=read(HERE/"INPUT_BINDINGS.json"); verify_inputs(b)
    results=[]
    for d in b["inputs"]:
        r={k:d[k] for k in ["id","episode","seed","role","sha256"]}
        try:
            a,counts=canonicalize((PROJECT/d["path"]).read_text(encoding="utf-8-sig"), d["role"]=="real_reference")
            r.update(counts=counts)
            r.update(status="computed", analyses=analyze(a))
        except (ValueError, KeyError, csv.Error) as exc:
            r.update(status="failed", reason=str(exc), analyses=[dict(pair=f"{u}__{v}",r=None,r_squared=None) for u,v in PAIRS])
        results.append(r)
    verify_inputs(b)
    write_new(HERE/"ANALYSIS.json",dict(created_utc=now(),freeze_sha256=sha(HERE/"FREEZE.json"),
        operator="Pearson of outcome residuals after intercept + age + I(F); age>18 common cases",
        records=results, patient_rows_exported=0, generated_rows_exported=0,
        new_generations=0, new_api_calls=0, new_dataset_downloads=0, inputs_unchanged=True))
    with (HERE/"PAIR_RESULTS.csv").open("x",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["id","episode","role","seed","status","n","pair","r","r_squared"]);w.writeheader()
        for r in results:
            for a in r["analyses"]:
                w.writerow({**{k:r[k] for k in ["id","episode","role","seed","status"]},"n":r.get("counts",{}).get("retained_rows"),**a})
    print(json.dumps(dict(tables=len(results),computed=sum(r["status"]=="computed" for r in results),pair_slots=3*len(results),inputs_unchanged=True)))

class OperatorTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(711)
        self.a=np.column_stack([rng.uniform(19,70,90),rng.integers(0,2,90),rng.normal(size=(90,3))])
    def values(self,a): return np.array([x["r"] for x in analyze(a)])
    def test_covariance_projection_identity(self):
        x=np.column_stack([np.ones(len(self.a)),self.a[:,:2]])
        residual=(np.eye(len(x))-x@np.linalg.inv(x.T@x)@x.T)@self.a[:,2:]
        c=np.corrcoef(residual,rowvar=False)
        np.testing.assert_allclose(self.values(self.a),c[np.triu_indices(3,1)],atol=1e-12)
    def test_positive_units_and_centering_invariant(self):
        b=self.a.copy();b[:,2:]=b[:,2:]*[4,38.67,38.67]+[30,150,50]
        np.testing.assert_allclose(self.values(self.a),self.values(b),atol=1e-12)
    def test_sex_reference_invariant(self):
        b=self.a.copy();b[:,1]=1-b[:,1]
        np.testing.assert_allclose(self.values(self.a),self.values(b),atol=1e-12)
    def test_adjusted_design_is_age_sex_only(self):
        b=self.a.copy(); b[:,3:]+=b[:,2,None]*np.array([3,4])
        self.assertGreater(self.values(b)[2],.8)
    def test_filter_and_keep_hdl_above_tc(self):
        s="age,sex,bmi,total_cholesterol,hdl_cholesterol\n18,F,22,4,1\n19,F,22,1,2\n20,M,NA,4,1\n21,M,0,4,1\n"
        a,c=canonicalize(s); self.assertEqual(len(a),1);self.assertEqual(c["hdl_above_tc_retained_rows"],1)
        self.assertEqual(c["exclusions"],dict(missing=1,nonfinite=0,age_not_above_18=1,nonpositive_biomarker=1))
    def test_invalid_tokens_rejected(self):
        with self.assertRaises(ValueError): canonicalize("age,sex,bmi,total_cholesterol,hdl_cholesterol\n20,X,22,4,1\n")
        with self.assertRaises(ValueError): canonicalize("age,sex,bmi,total_cholesterol,hdl_cholesterol\n20,F,unknown,4,1\n")
    def test_invalid_nonmissing_token_on_missing_row_rejected(self):
        with self.assertRaises(ValueError): canonicalize("age,sex,bmi,total_cholesterol,hdl_cholesterol\n20,X,NA,4,1\n")
        with self.assertRaises(ValueError): canonicalize("age,sex,bmi,total_cholesterol,hdl_cholesterol\n20,F,NA,unknown,1\n")
    def test_degenerate_design_and_outcome(self):
        b=self.a.copy();b[:,1]=1
        with self.assertRaises(ValueError):analyze(b)
        b=self.a.copy();b[:,2]=1
        with self.assertRaises(ValueError):analyze(b)

if __name__=="__main__":
    command=sys.argv[1]
    if command=="prepare":prepare()
    elif command=="run":run()
    elif command in ["test", "test_revision"]:
        if command=="test_revision":
            suite=unittest.TestSuite(OperatorTests(n) for n in ["test_filter_and_keep_hdl_above_tc", "test_invalid_tokens_rejected", "test_invalid_nonmissing_token_on_missing_row_rejected"])
        else:
            suite=unittest.defaultTestLoader.loadTestsFromTestCase(OperatorTests)
        stream=io.StringIO();out=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        print(stream.getvalue())
        write_new(HERE/("INVENTED_TESTS_REVISION.json" if command=="test_revision" else "INVENTED_TESTS.json"),dict(passed=out.wasSuccessful(),tests=out.testsRun,
            failures=len(out.failures),errors=len(out.errors),scope="invented rows only",code_sha256=sha(__file__)))
        sys.exit(0 if out.wasSuccessful() else 1)
    else:raise ValueError("Unknown command")

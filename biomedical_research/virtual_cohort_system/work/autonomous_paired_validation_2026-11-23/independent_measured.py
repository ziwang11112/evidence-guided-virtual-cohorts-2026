"""Recalculate the measured BMI endpoints from the Malaysian workbook after disclosure."""
import argparse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from hashlib import sha256
from pathlib import Path

import openpyxl

import experiment


HERE = Path(__file__).resolve().parent
EXPECTED_SHA = "04eaa6e6312f3bd764dbfedcd80f15bbed42d0f795854ec2c19a1a3698676c7f"
FIELDS = ("age_in_years","self_report_height_in_cm","self_report_weight_in_kg",
          "measured_height_in_cm","measured_weight_in_kg")
THRESHOLD = Decimal("-2")
ATOL = Decimal("1e-10")


def as_decimal(value):
    if value is None or isinstance(value,str) and not value.strip():
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Unrecognized numeric field or missing code; reconciliation required") from None
    if not result.is_finite():
        raise ValueError("Non-finite measured field; reconciliation required")
    return result


def independent_reference(*, authorized):
    if authorized is not True:
        raise PermissionError("Explicit authorization is required before opening the reference.")
    for stage in ("PREREVEAL","PREBUILD","PRESEARCH"):
        experiment.verify(stage)
    access = experiment.load(HERE/"REFERENCE_ACCESS.json")
    if (access.get("pmcid"),access.get("local_file"),access.get("sha256")) != ("PMC9844876","PMC9844876.xlsx",EXPECTED_SHA):
        raise ValueError("Wrong reference accession or binding")
    path = HERE/"private"/"reference"/access["local_file"]
    seal = experiment.load(HERE/"PREBUILD.json")["sha256"]
    if seal.get(path.relative_to(experiment.PROJECT).as_posix()) != EXPECTED_SHA or sha256(path.read_bytes()).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Workbook differs from admission or authoring freeze")
    category = dict(n_source=0, n_input=0, n_removed_by_population_filters=0,
                    n_missing_age=0, n_complete=0, n_incomplete=0,
                    n_missing_reported=0, n_missing_measured=0, ties_n=0, strictly_below_n=0)
    rounding = {Decimal("0.1"):0,Decimal("0.01"):0}
    sum_reported = Decimal(0)
    sum_measured = Decimal(0)
    sum_diff_squared = Decimal(0)
    with localcontext() as context:
        context.prec = 50
        book = openpyxl.load_workbook(path,read_only=True,data_only=True)
        try:
            sheet = book["Sheet1"]
            rows = sheet.values
            header = tuple(next(rows))
            if any(header.count(field)!=1 for field in FIELDS):
                raise ValueError("Missing or duplicate measurement headers")
            indexes = [header.index(field) for field in FIELDS]
            for row in rows:
                category["n_source"]+=1
                age = as_decimal(row[indexes[0]])
                if age is None or age<18:
                    category["n_removed_by_population_filters"]+=1
                    category["n_missing_age"]+=int(age is None)
                    continue
                category["n_input"]+=1
                rh,rw,mh,mw = [as_decimal(row[j]) for j in indexes[1:]]
                if any(z is not None and z<=0 for z in (rh,rw,mh,mw)):
                    raise ValueError("Nonpositive measurement; reconciliation required")
                no_reported = rh is None or rw is None
                no_measured = mh is None or mw is None
                category["n_missing_reported"]+=int(no_reported)
                category["n_missing_measured"]+=int(no_measured)
                if no_reported or no_measured:
                    category["n_incomplete"]+=1
                    continue
                reported = 10000*rw/rh**2
                measured = 10000*mw/mh**2
                delta = reported-measured
                category["n_complete"]+=1
                category["ties_n"]+=int(abs(delta-THRESHOLD)<=ATOL)
                category["strictly_below_n"]+=int(delta < THRESHOLD-ATOL)
                sum_reported+=reported
                sum_measured+=measured
                sum_diff_squared+=delta**2
                for quantum in rounding:
                    rounded_delta = reported.quantize(quantum, rounding=ROUND_HALF_UP)-measured.quantize(quantum, rounding=ROUND_HALF_UP)
                    rounding[quantum]+=int(rounded_delta<THRESHOLD)
        finally:
            book.close()
        n = category["n_complete"]
        if n<2 or category["n_input"]!=n+category["n_incomplete"]:
            raise ValueError("Invalid complete-case accounting")
        md = (sum_reported-sum_measured)/n
        def pct(k):
            return float(Decimal(100)*k/n)
        summary = dict(category, reported_mean=float(sum_reported/n), measured_mean=float(sum_measured/n),
                       mean_difference=float(md), difference_sd=float(((sum_diff_squared-n*md**2)/(n-1)).sqrt()),
                       strictly_below_pct=pct(category["strictly_below_n"]))
        sensitivities = [{"BMI_rounding_quantum_kg_m2":str(q),"strictly_below_n":rounding[q],
                          "strictly_below_pct":pct(rounding[q])} for q in rounding]
    return {"source":"PMC9844876, S1", "workbook_sha256":EXPECTED_SHA, "scope":"Age >=18; complete paired measurements; unweighted",
            "method":"openpyxl; decimal arithmetic with 50 significant digits; strict inequality with 1e-10 tie tolerance",
            "measured":summary,"secondary_sensitivity":"Each BMI rounded separately (decimal half-up) before subtraction",
            "sensitivity":sensitivities}


def verify_against_primary(reference, primary):
    check={}
    for key,value in reference["measured"].items():
        if key=="n_missing_age":  # Only the independent implementation reports this extra diagnostic.
            continue
        target=primary[key]
        if type(value) is int:
            if target != value:
                raise ValueError("Primary/independent counts differ for "+key)
        elif abs(target-value)>1e-9:
            raise ValueError("Primary/independent summary differs for "+key)
        check[key]=abs(target-value)
    return check


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorized-reveal",action="store_true",help="Set only after the coordinator explicitly authorizes disclosure.")
    args=parser.parse_args()
    result=independent_reference(authorized=args.authorized_reveal)
    primary=experiment.load(HERE/"AGGREGATES.json")
    if primary["reference_status"]!="scored":
        raise ValueError("Primary measured analysis unavailable for comparison")
    result["absolute_discrepancies_to_primary"]=verify_against_primary(result,primary["measured"])
    experiment.write(HERE/"INDEPENDENT_MEASURED.json",result)

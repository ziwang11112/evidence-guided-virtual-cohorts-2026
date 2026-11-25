"""Reconcile fractional recording of study eligibility before running frozen estimators."""
import warnings
import numpy as np
import pandas as pd
from blind_review import require_review
import evaluate_trial as ev
from run_trial import reference_after_seal, verified_draws, put, sha
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def main():
    slots=verified_draws()
    require_review()
    path=reference_after_seal()
    if sha(path)!=ev.FILE_SHA:
        raise ValueError("Reference workbook changed")
    # The openpyxl warning concerns dropping an unknown extension on save. This
    # analysis reads the workbook and never saves it.
    frame=pd.read_excel(path, sheet_name=ev.SHEET, header=3, dtype=object, keep_default_na=False)
    age=ev.numeric(frame["Age"])
    if np.any((age>=76)&np.isfinite(age)):
        raise ValueError("Age-only precheck differs")
    for label,name in (("completed_years","MEASURED_EVALUATION.json"),
                       ("strict_numeric","STRICT_AGE_EVALUATION.json")):
        subset=frame.copy() if label=="completed_years" else frame.loc[~(age>75)].copy()
        subset["Age"]=np.floor(ev.numeric(subset["Age"]))
        reported,measured,meta=ev.measurement_pairs(subset)
        meta.update(source_sheet_rows_before_age_reconciliation=len(frame),
                    excluded_above_75_before_primary_processing=len(frame)-len(subset),
                    age_interpretation=label)
        reference=ev.estimates(reported,measured,bootstrap=True)
        outputs=[{key:s[key] for key in ("slot","block","arm","status")} |
                 ev.assess_slot(s["draws"],reference) for s in slots]
        put(ROOT/name,{"stage":"measured","reference":reference,"reference_eligibility":meta,
            "source_table":ev.rounded_source_tables()[0],"slots":outputs,
            "eligibility_reconciliation_sha256":sha(ROOT/"ELIGIBILITY_RECONCILIATION.md")})

if __name__=="__main__":
    main()

"""Locked M17-B evaluator. Evaluation requires an explicit root release manifest.

No module import evaluates, reads, or summarizes reference participant data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

BINS = [20, 35, 50, 65, 80]
ENDPOINTS = [
    "adjusted_bmi", "adjusted_age", "adjusted_sex", "bmi_curvature",
    "bmi_sex_interaction", "male_bmi", "female_bmi", "reverse_urate",
]
Z95 = 1.959963984540054


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def validate_table(frame):
    required = ["sample_id", "age", "female", "bmi", "urate"]
    if list(frame.columns) != required:
        raise ValueError(f"Expected exactly {required}, found {list(frame.columns)}")
    if len(frame) != 320 or frame.sample_id.isna().any() or frame.sample_id.duplicated().any():
        raise ValueError("Require 320 unique nonmissing IDs")
    values = frame[required[1:]].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite substantive value; no silent row deletion")
    if not frame.age.between(20, 80, inclusive="left").all():
        raise ValueError("Age outside [20,80)")
    if not frame.female.isin([0, 1]).all() or not (frame.bmi > 0).all() or not (frame.urate >= 0).all():
        raise ValueError("Invalid sex, BMI, or urate")
    cells = []
    for sex in [0, 1]:
        for lo, hi in zip(BINS[:-1], BINS[1:]):
            n = int(((frame.female == sex) & frame.age.between(lo, hi, inclusive="left")).sum())
            cells.append({"female": sex, "age_lo": lo, "age_hi_exclusive": hi, "n": n})
            if n != 40:
                raise ValueError(f"Quota mismatch: female={sex}, age=[{lo},{hi}), n={n}")
    return cells


def ols_hc3(design, response):
    x = np.asarray(design, dtype=float)
    y = np.asarray(response, dtype=float)
    if np.linalg.matrix_rank(x) != x.shape[1]:
        raise ValueError("Rank-deficient locked analysis")
    bread = np.linalg.inv(x.T @ x)
    beta = bread @ x.T @ y
    residual = y - x @ beta
    leverage = np.einsum("ij,jk,ik->i", x, bread, x)
    if np.any(1 - leverage <= 1e-10):
        raise ValueError("HC3 undefined due to leverage near one")
    omega = (residual / (1 - leverage)) ** 2
    cov = bread @ (x.T @ (omega[:, None] * x)) @ bread
    return beta, cov


def contrast(beta, cov, coefficients):
    c = np.asarray(coefficients, dtype=float)
    estimate = float(c @ beta)
    variance = float(c @ cov @ c)
    if variance < -1e-10 or not np.isfinite(variance):
        raise ValueError("Invalid HC3 contrast variance")
    se = math.sqrt(max(0, variance))
    return {"estimate": estimate, "se_hc3": se,
            "ci95_lo": estimate - Z95 * se, "ci95_hi": estimate + Z95 * se}


def endpoints(frame):
    x = (frame.bmi.to_numpy(float) - 27.5) / 5
    a = (frame.age.to_numpy(float) - 50) / 10
    f = frame.female.to_numpy(float)
    y = frame.urate.to_numpy(float)
    one = np.ones(len(frame))
    linear = ols_hc3(np.column_stack([one, x, a, f]), y)
    curved = ols_hc3(np.column_stack([one, x, x*x, a, f]), y)
    interaction = ols_hc3(np.column_stack([one, x, a, f, x*f]), y)
    reverse = ols_hc3(np.column_stack([one, y, a, f]), frame.bmi.to_numpy(float))
    return {
        "adjusted_bmi": contrast(*linear, [0, 1, 0, 0]),
        "adjusted_age": contrast(*linear, [0, 0, 1, 0]),
        "adjusted_sex": contrast(*linear, [0, 0, 0, 1]),
        "bmi_curvature": contrast(*curved, [0, 0, 2, 0, 0]),
        "bmi_sex_interaction": contrast(*interaction, [0, 0, 0, 0, 1]),
        "male_bmi": contrast(*interaction, [0, 1, 0, 0, 0]),
        "female_bmi": contrast(*interaction, [0, 1, 0, 0, 1]),
        "reverse_urate": contrast(*reverse, [0, 1, 0, 0]),
    }


def diagnostics(frame):
    summaries = []
    for name, subset in [("overall", frame), ("male", frame[frame.female == 0]),
                          ("female", frame[frame.female == 1])]:
        for variable in ["bmi", "urate"]:
            values = subset[variable].to_numpy(float)
            p10, p50, p90 = np.quantile(values, [.1, .5, .9], method="linear")
            summaries.append({"group": name, "variable": variable, "n": len(values),
                              "mean": float(values.mean()), "sd": float(values.std(ddof=1)),
                              "p10": float(p10), "p50": float(p50), "p90": float(p90)})
    correlations = {}
    for left, right in [("age", "bmi"), ("bmi", "urate")]:
        xx, yy = frame[left].to_numpy(float), frame[right].to_numpy(float)
        correlations[f"{left}__{right}"] = (float(np.corrcoef(xx, yy)[0, 1])
            if np.std(xx) > 0 and np.std(yy) > 0 else None)
    return {"summaries": summaries, "pearson": correlations}


def analyze_table(path):
    frame = pd.read_csv(path, dtype={"sample_id": str})
    cells = validate_table(frame)
    return {"path": str(Path(path).resolve()), "sha256": sha256(path), "status": "ok",
            "n": len(frame), "cells": cells, "endpoints": endpoints(frame),
            "diagnostics": diagnostics(frame)}


def sanity_check():
    """Invented data only; independent statsmodels HC3 and hand identities."""
    import statsmodels.api as sm
    rng = np.random.default_rng(17601)
    age, female = [], []
    for sex in [0, 1]:
        for lo, hi in zip(BINS[:-1], BINS[1:]):
            age.extend(rng.integers(lo, hi, size=40))
            female.extend([sex] * 40)
    age, female = np.array(age), np.array(female)
    bmi = 26 + rng.normal(0, 3, 320) + .02*(age-50) + .3*female
    x, a = (bmi-27.5)/5, (age-50)/10
    y = 4 + .4*x + .13*a - .5*female + .2*x*x + .1*x*female + rng.normal(0, .2, 320)
    frame = pd.DataFrame({"sample_id": [f"invented_{i:04d}" for i in range(320)],
                          "age": age, "female": female, "bmi": bmi, "urate": y})
    validate_table(frame)
    tested = 0
    one = np.ones(320)
    for design, response in [(np.column_stack([one,x,a,female]),y),
                             (np.column_stack([one,x,x*x,a,female]),y),
                             (np.column_stack([one,x,a,female,x*female]),y),
                             (np.column_stack([one,y,a,female]),bmi)]:
        beta, cov = ols_hc3(design, response)
        independent = sm.OLS(response, design).fit(cov_type="HC3")
        np.testing.assert_allclose(beta, independent.params, rtol=1e-10, atol=1e-10)
        np.testing.assert_allclose(cov, independent.cov_params(), rtol=1e-9, atol=1e-10)
        tested += 2
    c = np.array([0., 1., 0., 0., 1.])
    interaction_design = np.column_stack([one,x,a,female,x*female])
    interaction_fit = sm.OLS(y, interaction_design).fit(cov_type="HC3")
    got = endpoints(frame)
    np.testing.assert_allclose(got['female_bmi']['estimate'], c @ interaction_fit.params, atol=1e-10)
    np.testing.assert_allclose(got['female_bmi']['se_hc3'], np.sqrt(c @ interaction_fit.cov_params() @ c), atol=1e-10)
    # Exact quadratic yields f(35)-2*f(30)+f(25)=2*q for x=(BMI-27.5)/5.
    q=.731
    poly=lambda z: 4+.22*((z-27.5)/5)+q*((z-27.5)/5)**2
    assert abs(poly(35)-2*poly(30)+poly(25)-2*q) < 1e-12
    exact_frame=frame.copy()
    exact_frame['urate']=4+.22*x+q*x*x+.13*a-.5*female
    assert abs(endpoints(exact_frame)['bmi_curvature']['estimate']-2*q) < 1e-10
    diag=diagnostics(frame)
    assert len(diag['summaries']) == 6 and len(got) == 8
    invalid=frame.copy(); invalid.loc[0,'female']=2
    try: validate_table(invalid)
    except ValueError: pass
    else: raise AssertionError('Invalid sex was accepted')
    return {"status": "passed", "invented_only": True, "n": 320,
            "independent_fit_array_comparisons": tested,
            "additional_checks": ["female interaction contrast and HC3 covariance",
                "quadratic finite-difference identity and known coefficient recovery",
                "eight endpoints and six variable/group summaries", "quota and invalid-sex validation"],
            "definitions": {"sd": "sample SD, ddof=1", "quantile": "numpy linear",
                            "ci": "normal 1.959963984540054 times HC3 SE", "pearson": "pairwise Pearson on full table"}}


def evaluate_release(release_path, output_dir):
    release_path, output_dir = Path(release_path), Path(output_dir)
    release = json.loads(release_path.read_text(encoding="utf-8"))
    if release.get("authorization") != "root_releases_all_frozen_outputs_for_one_target_evaluation":
        raise ValueError("Missing explicit root final-output release")
    if not release.get("endpoint_exposure_classification_sha256"):
        raise ValueError("Endpoint exposure classification must precede unblinding")
    for binding in [release["protocol"], release["evaluator"], release["reference"],
                    release["endpoint_exposure_classification"], *release["generated_tables"]]:
        if sha256(binding["path"]) != binding["sha256"]:
            raise ValueError(f"Changed input: {binding['path']}")
    if sha256(__file__) != release["evaluator"]["sha256"]:
        raise ValueError("Release does not bind this evaluator")
    if release['endpoint_exposure_classification']['sha256'] != release['endpoint_exposure_classification_sha256']:
        raise ValueError('Endpoint exposure hash mismatch')
    if output_dir.exists():
        raise ValueError("Evaluation output directory already exists; no silent overwrite/re-run")
    output_dir.mkdir(parents=True)
    reference = analyze_table(release['reference']['path'])
    analyses, comparisons, errors = [], [], []
    for item in release['generated_tables']:
        meta = {k: item[k] for k in ['builder','stage','seed','route']}
        try:
            result = analyze_table(item['path'])
            result.update(meta)
            analyses.append(result)
            for endpoint in ENDPOINTS:
                real, gen = reference['endpoints'][endpoint], result['endpoints'][endpoint]
                comparisons.append({**meta, 'endpoint': endpoint,
                    'generated_estimate': gen['estimate'], 'reference_estimate': real['estimate'],
                    'reference_se_hc3': real['se_hc3'], 'reference_ci95_lo': real['ci95_lo'],
                    'reference_ci95_hi': real['ci95_hi'],
                    'generated_minus_reference': gen['estimate']-real['estimate'],
                    'reference_interval_spans_zero': real['ci95_lo'] <= 0 <= real['ci95_hi'],
                    'point_sign_agreement': bool(np.sign(gen['estimate']) == np.sign(real['estimate']))})
        except Exception as exc:
            errors.append({**meta,'path':item['path'],'error_type':type(exc).__name__,'message':str(exc)})
    comp = pd.DataFrame(comparisons)
    comp.to_csv(output_dir/'comparisons.csv', index=False)
    if len(comp):
        ranges=comp.groupby(['builder','stage','endpoint'],dropna=False).agg(
            realizations=('generated_estimate','size'), min_estimate=('generated_estimate','min'),
            max_estimate=('generated_estimate','max'), mean_estimate=('generated_estimate','mean'),
            min_signed_difference=('generated_minus_reference','min'),
            max_signed_difference=('generated_minus_reference','max')).reset_index()
        ranges.to_csv(output_dir/'realization_ranges.csv',index=False)
    report={'release_path':str(release_path.resolve()),'release_sha256':sha256(release_path),
            'protocol_sha256':release['protocol']['sha256'],'evaluator_sha256':sha256(__file__),
            'reference':reference,'generated':analyses,'failed_analyses':errors,
            'scheduled_tables':len(release['generated_tables']),
            'interpretation':'Unweighted standardized quota sample. HC3 is model/sample-conditional, not complex-survey or transport uncertainty.'}
    write_json(output_dir/'evaluation.json',report)
    return {'scheduled':len(release['generated_tables']),'completed':len(analyses),'failed':len(errors)}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest='mode',required=True)
    check=sub.add_parser('sanity'); check.add_argument('--output',required=True)
    evaluate=sub.add_parser('evaluate'); evaluate.add_argument('--release',required=True); evaluate.add_argument('--output-dir',required=True)
    args=parser.parse_args()
    if args.mode=='sanity':
        result=sanity_check(); write_json(args.output,result); print(json.dumps({'status':result['status'],'invented_only':True}))
    else:
        print(json.dumps(evaluate_release(args.release,args.output_dir)))

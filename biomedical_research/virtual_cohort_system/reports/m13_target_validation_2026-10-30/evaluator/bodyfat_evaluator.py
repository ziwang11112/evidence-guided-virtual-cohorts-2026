"""M13-B frozen target evaluator. Importing this module performs no data I/O.

Only aggregate output is emitted. Generator code is never imported or executed.
Quantile/IQR estimates are weighted inverse-ECDF points; no quantile intervals.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.stats import t

SCHEMA_VERSION = 1
SEEDS = (33101, 33102, 33103)
FULL_COLUMNS = (
    "id", "SEQN", "WTMEC2YR", "SDMVSTRA", "SDMVPSU", "RIDAGEYR",
    "RIAGENDR", "RIDRETH3", "BMXBMI", "DXAEXSTS", "DXDTOPF",
)
OBSERVED_COLUMNS = (
    "id", "age", "bmi", "male", "asian", "inv_bmi", "male_inv_bmi",
    "asian_inv_bmi", "male_age", "asian_age",
)
GENERATED_COLUMNS = OBSERVED_COLUMNS + ("bodyfat",)
MANIFEST_TABLE_COLUMNS = {
    "table_id", "kind", "builder", "candidate", "seed", "path", "status",
}
IDENTITY_COLUMNS = ("table_id", "kind", "builder", "candidate", "seed")
TITLE = (
    "NHANES 2017–2018 MEC-weighted complete-covariate valid-scan body-fat "
    "domain: age 20–59, non-Hispanic White/Black, primary BMI 18.5–<30 "
    "and separate extension BMI 30–35"
)


class ValidationError(ValueError):
    """Messages are fixed categories and never contain row keys or values."""


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def _columns(frame, expected):
    require(list(frame.columns) == list(expected), "column_whitelist_or_order_mismatch")


def _ids(frame):
    s = frame["id"]
    require(s.notna().all(), "missing_id")
    require(s.map(lambda x: isinstance(x, str) and bool(x) and x == x.strip()).all(),
            "invalid_id")
    require(not s.duplicated().any(), "duplicate_id")


def _numeric(frame, columns):
    result = frame.copy()
    for col in columns:
        try:
            result[col] = pd.to_numeric(result[col], errors="raise").astype(float)
        except (ValueError, TypeError, OverflowError):
            raise ValidationError("nonnumeric_value") from None
    return result


def read_csv_strict(path, columns):
    """Inspect raw header to reject duplicates before pandas can rename them."""
    try:
        with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            require(header == list(columns), "column_whitelist_or_order_mismatch")
            require(all(len(row) == len(columns) for row in reader), "csv_row_width_mismatch")
        require(header == list(columns), "column_whitelist_or_order_mismatch")
        frame = pd.read_csv(path, dtype={"id": "str"}, keep_default_na=False, float_precision="round_trip",
                            na_values={c: [""] for c in columns if c != "id"})
    except ValidationError:
        raise
    except (OSError, ValueError, StopIteration, pd.errors.ParserError):
        raise ValidationError("unreadable_csv") from None
    _columns(frame, columns)
    _ids(frame)
    return frame


def validate_full_frame(frame):
    _columns(frame, FULL_COLUMNS)
    _ids(frame)
    f = _numeric(frame, FULL_COLUMNS[1:])
    require(len(f) > 0, "empty_design_frame")
    for col in ("SEQN", "SDMVSTRA", "SDMVPSU"):
        v = f[col].to_numpy()
        require(np.isfinite(v).all() and (v == np.floor(v)).all(), "invalid_design_identifier")
    require(not f.SEQN.duplicated().any(), "duplicate_seqn")
    require(np.isfinite(f.WTMEC2YR).all() and f.WTMEC2YR.gt(0).all(),
            "nonpositive_or_nonfinite_mec_weight")
    # Missing covariates/outcomes remain in the design frame. Infinities are not missing.
    for col in ("RIDAGEYR", "RIAGENDR", "RIDRETH3", "BMXBMI", "DXAEXSTS", "DXDTOPF"):
        require(not np.isinf(f[col].to_numpy()).any(), "infinite_private_value")
    y = f.DXDTOPF.dropna()
    require(y.between(0, 100).all(), "bodyfat_outside_physical_support")
    require((f.groupby("SDMVSTRA").SDMVPSU.nunique() >= 2).all(),
            "singleton_full_design_stratum")
    return f


def domains(full):
    age_race = full.RIDAGEYR.between(20, 59) & full.RIDRETH3.isin([3, 4])
    sampling = age_race & full.RIAGENDR.isin([1, 2]) & full.BMXBMI.between(18.5, 35)
    scan = sampling & full.DXAEXSTS.eq(1)
    eligible = scan & full.DXDTOPF.notna()
    return {
        "age_race": age_race.to_numpy(), "sampling": sampling.to_numpy(),
        "scan": scan.to_numpy(), "eligible": eligible.to_numpy(),
        "primary": (eligible & full.BMXBMI.lt(30)).to_numpy(),
        "extension": (eligible & full.BMXBMI.ge(30)).to_numpy(),
    }


def expected_observed(full):
    d = domains(full)["eligible"]
    age = full.loc[d, "RIDAGEYR"].to_numpy()
    bmi = full.loc[d, "BMXBMI"].to_numpy()
    male = full.loc[d, "RIAGENDR"].eq(1).to_numpy(dtype=float)
    zero = np.zeros(len(age))
    return pd.DataFrame(dict(
        id=full.loc[d, "id"].to_numpy(), age=age, bmi=bmi, male=male,
        asian=zero, inv_bmi=1 / bmi, male_inv_bmi=male / bmi,
        asian_inv_bmi=zero, male_age=male * age, asian_age=zero,
    ), columns=OBSERVED_COLUMNS)


def _align_exact(frame, expected):
    _ids(frame)
    require(len(frame) == len(expected) and set(frame.id) == set(expected.id), "id_set_mismatch")
    return frame.set_index("id").loc[expected.id].reset_index()


def validate_observed(frame, full):
    _columns(frame, OBSERVED_COLUMNS)
    f = _numeric(_align_exact(frame, expected_observed(full)), OBSERVED_COLUMNS[1:])
    expected = expected_observed(full)
    values = f.loc[:, OBSERVED_COLUMNS[1:]].to_numpy()
    require(np.isfinite(values).all(), "nonfinite_observed_covariate")
    # CSV serialization allowance only; not a permission to modify observations.
    require(np.allclose(values, expected.loc[:, OBSERVED_COLUMNS[1:]].to_numpy(),
                        rtol=1e-12, atol=1e-12), "observed_covariate_mismatch")
    return f


def validate_generated(frame, observed):
    _columns(frame, GENERATED_COLUMNS)
    f = _numeric(_align_exact(frame, observed), GENERATED_COLUMNS[1:])
    preserved = f.loc[:, OBSERVED_COLUMNS[1:]].to_numpy()
    require(np.isfinite(preserved).all() and np.allclose(
        preserved, observed.loc[:, OBSERVED_COLUMNS[1:]].to_numpy(), rtol=1e-12, atol=1e-12),
        "generated_covariate_mismatch")
    y = f.bodyfat.to_numpy()
    require(np.isfinite(y).all() and ((y >= 0) & (y <= 100)).all(),
            "invalid_generated_bodyfat")
    return f


def fit_domain(X, y, weights, strata, psu, domain):
    """Full-frame, nested-PSU linearized WLS sandwich; no sparse reporting gate."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)
    strata, psu = np.asarray(strata), np.asarray(psu)
    domain = np.asarray(domain, dtype=bool)
    require(X.ndim == 2 and all(len(v) == len(X) for v in (y, weights, strata, psu, domain)),
            "inconsistent_fit_dimensions")
    require(domain.any(), "empty_domain")
    require(np.isfinite(weights).all() and (weights > 0).all(), "invalid_fit_weights")
    require(np.isfinite(X[domain]).all() and np.isfinite(y[domain]).all(), "invalid_fit_values")
    require(not pd.isna(strata).any() and not pd.isna(psu).any(), "missing_fit_design")
    xd, yd = X[domain], y[domain]
    p = X.shape[1]
    require(np.linalg.matrix_rank(xd) == p, "rank_deficient_design")
    require(len(xd) > p, "nonpositive_residual_degrees_of_freedom")
    w = weights / weights[domain].mean()
    wd = w[domain]
    bread = np.linalg.inv(xd.T @ (wd[:, None] * xd))
    beta = np.linalg.solve(xd.T @ (wd[:, None] * xd), xd.T @ (wd * yd))
    score = np.zeros((len(X), p))
    score[domain] = xd * (wd * (yd - xd @ beta))[:, None]
    meat = np.zeros((p, p))
    full_psus = 0
    for h in np.unique(strata):
        hj = strata == h
        jvals = np.unique(psu[hj])
        m = len(jvals)
        require(m >= 2, "singleton_full_design_stratum")
        full_psus += m
        totals = np.array([score[hj & (psu == j)].sum(axis=0) for j in jvals])
        centered = totals - totals.mean(axis=0)
        meat += m / (m - 1) * (centered.T @ centered)
    cov = bread @ meat @ bread
    cov = (cov + cov.T) / 2
    domain_psus = len(set(zip(strata[domain], psu[domain])))
    domain_strata = len(set(strata[domain]))
    df = domain_psus - domain_strata
    require(df > 0, "nonpositive_domain_design_df")
    require(np.isfinite(beta).all() and np.isfinite(cov).all(), "nonfinite_fit_result")
    return dict(beta=beta, covariance=cov, df=df, n=int(domain.sum()),
                full_design_psus=full_psus, full_design_strata=len(np.unique(strata)),
                domain_psus=domain_psus, domain_strata=domain_strata)


def contrast_interval(fit, contrast):
    c = np.asarray(contrast, dtype=float)
    est = float(c @ fit["beta"])
    variance = float(c @ fit["covariance"] @ c)
    require(variance >= -1e-10, "negative_contrast_variance")
    se = float(np.sqrt(max(0, variance)))
    halfwidth = float(t.ppf(.975, fit["df"]) * se)
    return dict(estimate=est, se=se, ci_low=est-halfwidth, ci_high=est+halfwidth,
                interval_available=True, interval_level=.95, df=fit["df"])


def weighted_quantile(values, weights, probabilities=(.25, .5, .75)):
    """First tied observed value at cumulative weight >= p; p=0 is minimum."""
    y, w, probs = (np.asarray(v, dtype=float) for v in (values, weights, probabilities))
    require(y.ndim == w.ndim == probs.ndim == 1 and len(y) == len(w) and len(y) > 0,
            "invalid_quantile_dimensions")
    require(np.isfinite(y).all() and np.isfinite(w).all() and (w > 0).all(),
            "invalid_quantile_values")
    require(np.isfinite(probs).all() and ((probs >= 0) & (probs <= 1)).all(),
            "invalid_quantile_probability")
    unique, inverse = np.unique(y, return_inverse=True)
    # Scaling prevents overflow and preserves the inverse-ECDF convention.
    tied = np.bincount(inverse, weights=w/w.max())
    cumulative = np.cumsum(tied)
    indices = np.searchsorted(cumulative, probs * cumulative[-1], side="left")
    return unique[np.minimum(indices, len(unique)-1)]


def gate(full, domain, X=None):
    n = int(domain.sum())
    weights = full.loc[domain, "WTMEC2YR"].to_numpy()
    wn = weights/weights.max() if n else np.array([])
    kish = float(wn.sum()**2 / (wn @ wn)) if n else 0.0
    npsu = len(set(zip(full.loc[domain, "SDMVSTRA"], full.loc[domain, "SDMVPSU"])))
    nstrata = int(full.loc[domain, "SDMVSTRA"].nunique())
    df = npsu-nstrata
    failures = []
    if n < 30: failures.append("n_below_30")
    if kish < 20: failures.append("kish_below_20")
    if npsu < 8: failures.append("domain_psus_below_8")
    if df < 4: failures.append("domain_df_below_4")
    rank, p = None, None
    if X is not None:
        p = X.shape[1]
        rank = int(np.linalg.matrix_rank(X[domain])) if n else 0
        if rank != p: failures.append("rank_deficient_design")
        if n <= p: failures.append("nonpositive_residual_degrees_of_freedom")
    return dict(n=n, kish_n=kish, domain_psus=npsu, domain_strata=nstrata,
                df=df, rank=rank, parameters=p, failures=failures,
                estimable=not failures)


def panel_schedule(full):
    ds = domains(full)
    B = (full.BMXBMI.to_numpy()-24)/5
    A = (full.RIDAGEYR.to_numpy()-40)/10
    R = full.RIDRETH3.eq(4).to_numpy(dtype=float)
    linear = np.column_stack([np.ones(len(full)), B, A, R])
    quadratic = np.column_stack([linear, B*B])
    mean = np.ones((len(full), 1))
    schedule = []
    for name in ("primary", "extension"):
        for sex, code in (("male", 1), ("female", 2)):
            d = ds[name] & full.RIAGENDR.eq(code).to_numpy()
            for statistic, X, contrast in (
                ("mean", mean, [1]),
                ("bmi_per5", linear, [0, 1, 0, 0]),
                ("age_per10", linear, [0, 0, 1, 0]),
            ):
                schedule.append(dict(endpoint=f"{name}.{sex}.{statistic}",
                                     kind="linear", domain=d, X=X, contrast=contrast))
            if name == "primary":
                schedule.append(dict(endpoint=f"{name}.{sex}.bmi_curvature_second_difference",
                                     kind="linear", domain=d, X=quadratic,
                                     contrast=[0, 0, 0, 0, 1.28]))
            for age_name, amin, amax in (("20_39", 20, 39), ("40_59", 40, 59)):
                da = d & full.RIDAGEYR.between(amin, amax).to_numpy()
                bins = (("18_5_lt25", 18.5, 25), ("25_lt30", 25, 30)) if name == "primary" else (("30_35", 30, 35),)
                for bmi_name, lo, hi in bins:
                    bmi_mask = full.BMXBMI.ge(lo) & (full.BMXBMI.le(hi) if name == "extension" else full.BMXBMI.lt(hi))
                    cell = da & bmi_mask.to_numpy()
                    for statistic in ("q25", "q50", "q75", "iqr"):
                        schedule.append(dict(endpoint=f"{name}.{sex}.age{age_name}.bmi{bmi_name}.{statistic}",
                                             kind="distribution", domain=cell, statistic=statistic))
    require(len(schedule) == 62, "internal_panel_schedule_error")
    return schedule


def estimate_panel(full, values):
    values = np.asarray(values, dtype=float)
    out = []
    for item in panel_schedule(full):
        d = item["domain"]
        g = gate(full, d, item.get("X"))
        row = dict(endpoint=item["endpoint"], kind=item["kind"], units="percentage_points",
                   gate=g, status="estimable" if g["estimable"] else "not_estimable",
                   estimate=None, se=None, ci_low=None, ci_high=None,
                   interval_available=False, interval_level=None, df=g["df"])
        if not g["estimable"]:
            row["interval_reason"] = "sparse_or_rank_gate_failed"
        elif item["kind"] == "linear":
            fit = fit_domain(item["X"], values, full.WTMEC2YR, full.SDMVSTRA,
                             full.SDMVPSU, d)
            row.update(contrast_interval(fit, item["contrast"]))
        else:
            q = weighted_quantile(values[d], full.loc[d, "WTMEC2YR"])
            row["estimate"] = float(dict(q25=q[0], q50=q[1], q75=q[2], iqr=q[2]-q[0])[item["statistic"]])
            row["interval_reason"] = "quantile_and_iqr_intervals_omitted_by_frozen_pilot_protocol"
            row["quantile_method"] = "weighted_inverse_ecdf_no_interpolation_ties_aggregated"
        out.append(row)
    return out


def evaluate_table(full, observed, generated, measured):
    generated = validate_generated(generated, observed)
    ygen = np.full(len(full), np.nan)
    d = domains(full)["eligible"]
    # observed has already been realigned to full frame eligible order.
    ygen[d] = generated.bodyfat.to_numpy()
    panel = estimate_panel(full, ygen)
    delta = ygen - full.DXDTOPF.to_numpy()
    for item, row, real in zip(panel_schedule(full), panel, measured):
        row.update(signed_error=None, absolute_error=None, paired_difference=None)
        if row["status"] != "estimable":
            continue
        error = row["estimate"]-real["estimate"]
        row.update(signed_error=error, absolute_error=abs(error))
        if item["kind"] == "linear":
            fit = fit_domain(item["X"], delta, full.WTMEC2YR, full.SDMVSTRA,
                             full.SDMVPSU, item["domain"])
            paired = contrast_interval(fit, item["contrast"])
            require(np.isclose(paired["estimate"], error, rtol=1e-9, atol=1e-9),
                    "paired_linear_identity_failure")
            row["paired_difference"] = paired
    return panel


def exclusion_flow(full):
    ds = domains(full)
    masks = [("positive_mec_complete_design_frame", np.ones(len(full), dtype=bool)),
             ("age20_59_white_black", ds["age_race"]),
             ("valid_sex_bmi18_5_35_sampling_frame", ds["sampling"]),
             ("whole_body_scan_completed", ds["scan"]),
             ("finite_valid_endpoint_complete_domain", ds["eligible"])]
    stages = []
    previous = np.ones(len(full), dtype=bool)
    for name, d in masks:
        stages.append(dict(stage=name, n=int(d.sum()), weight_sum=float(full.loc[d, "WTMEC2YR"].sum()),
                           excluded_from_previous_n=int((previous & ~d).sum()),
                           excluded_from_previous_weight=float(full.loc[previous & ~d, "WTMEC2YR"].sum())))
        previous = d
    sampling_n = int(ds["sampling"].sum())
    sampling_w = float(full.loc[ds["sampling"], "WTMEC2YR"].sum())
    return dict(stages=stages, primary_n=int(ds["primary"].sum()), extension_n=int(ds["extension"].sum()),
                completeness_unweighted=float(ds["eligible"].sum()/sampling_n) if sampling_n else None,
                completeness_weighted=float(full.loc[ds["eligible"], "WTMEC2YR"].sum()/sampling_w) if sampling_w else None,
                completeness_denominator="valid_sex_bmi18_5_35_sampling_frame",
                missingness_handling="complete_covariate_valid_scan_domain_no_imputation_or_nonresponse_adjustment")


def scheduled_roster():
    roster = [dict(table_id=f"{b}_{c}_{s}", kind="agent", builder=b, candidate=c, seed=s)
              for b in ("build01", "build02") for c in ("initial", "source_reviewed") for s in SEEDS]
    roster.append(dict(table_id="gallagher_mean", kind="reference_deterministic",
                       builder="published_reference", candidate="gallagher_mean", seed=None))
    roster += [dict(table_id=f"gallagher_normal_{s}", kind="reference_stochastic",
                    builder="published_reference", candidate="gallagher_normal", seed=s) for s in SEEDS]
    return roster


def _digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def validate_manifest(manifest):
    require(isinstance(manifest, dict) and set(manifest) == {"schema_version", "observed_path", "preaccess_sha256", "tables"},
            "invalid_manifest_fields")
    require(type(manifest["schema_version"]) is int and manifest["schema_version"] == SCHEMA_VERSION, "unsupported_manifest_version")
    require(_digest(manifest["preaccess_sha256"]), "invalid_preaccess_digest")
    require(isinstance(manifest["observed_path"], str) and bool(manifest["observed_path"]), "invalid_observed_path")
    tables = manifest["tables"]
    require(isinstance(tables, list) and len(tables) == 16, "manifest_requires_16_tables")
    ids, agent_groups, refs = set(), {}, {"reference_deterministic": [], "reference_stochastic": []}
    for tab in tables:
        require(isinstance(tab, dict) and MANIFEST_TABLE_COLUMNS.issubset(tab), "invalid_table_manifest_fields")
        expected_fields = MANIFEST_TABLE_COLUMNS | ({"execution_receipt_path", "execution_status"} if tab["kind"] == "agent" else {"reference_receipt_path"})
        if tab["status"] == "complete":
            expected_fields = expected_fields | {"sha256"}
            require(_digest(tab.get("sha256")), "invalid_generated_digest")
        require(set(tab) == expected_fields, "invalid_table_manifest_fields")
        receipt_field = "execution_receipt_path" if tab["kind"] == "agent" else "reference_receipt_path"
        require(isinstance(tab[receipt_field], str) and bool(tab[receipt_field]), "invalid_receipt_path")
        if tab["kind"] == "agent":
            require(isinstance(tab["execution_status"], str) and bool(tab["execution_status"]), "invalid_execution_status")
            require((tab["status"] == "complete") == (tab["execution_status"] == "success"), "execution_status_mismatch")
        for col in ("table_id", "kind", "builder", "candidate", "status"):
            require(isinstance(tab[col], str) and bool(tab[col]) and tab[col] == tab[col].strip(), "invalid_table_metadata")
        require(tab["table_id"] not in ids, "duplicate_table_id")
        ids.add(tab["table_id"])
        require(tab["status"] in ("complete", "failed"), "invalid_table_status")
        require((tab["status"] == "complete" and isinstance(tab["path"], str) and bool(tab["path"])) or
                (tab["status"] == "failed" and tab["path"] is None), "invalid_table_path_status")
        if tab["kind"] == "agent":
            require(type(tab["seed"]) is int and tab["seed"] in SEEDS, "invalid_agent_seed")
            agent_groups.setdefault((tab["builder"], tab["candidate"]), []).append(tab["seed"])
        elif tab["kind"] in refs:
            refs[tab["kind"]].append(tab)
        else:
            raise ValidationError("invalid_table_kind")
    require(len(agent_groups) == 4 and all(sorted(seeds) == list(SEEDS) for seeds in agent_groups.values()),
            "invalid_agent_group_roster")
    builders = {b for b, _ in agent_groups}
    require(len(builders) == 2 and all(sum(b == name for b, _ in agent_groups) == 2 for name in builders),
            "invalid_builder_candidate_roster")
    require(len(refs["reference_deterministic"]) == 1 and refs["reference_deterministic"][0]["seed"] is None,
            "invalid_deterministic_reference_roster")
    stochastic = refs["reference_stochastic"]
    require(len(stochastic) == 3 and all(type(x["seed"]) is int for x in stochastic) and
            sorted(x["seed"] for x in stochastic) == list(SEEDS) and
            len({(x["builder"], x["candidate"]) for x in stochastic}) == 1,
            "invalid_stochastic_reference_roster")
    require([{key: tab[key] for key in IDENTITY_COLUMNS} for tab in tables] == scheduled_roster(),
            "frozen_table_roster_mismatch")
    return manifest


def seed_summaries(tables):
    groups = {}
    for table in tables:
        if table["kind"] == "reference_deterministic":
            continue
        key = (table["kind"], table["builder"], table["candidate"])
        groups.setdefault(key, []).append(table)
    summaries = []
    for (kind, builder, candidate), group in sorted(groups.items()):
        records = []
        # Failed tables retain a complete endpoint schedule.
        for i in range(62):
            rows = [tab["panel"][i] for tab in group]
            good = [row for row in rows if row["status"] == "estimable"]
            record = dict(endpoint=rows[0]["endpoint"], available_draws=len(good), required_draws=3,
                          status="complete" if len(good) == 3 else "not_complete", summaries={})
            for name in ("estimate", "signed_error", "absolute_error"):
                vals = [row[name] for row in good]
                record["summaries"][name] = (dict(mean=float(np.mean(vals)), min=float(min(vals)), max=float(max(vals)))
                                                if len(vals) == 3 else None)
            records.append(record)
        summaries.append(dict(kind=kind, builder=builder, candidate=candidate, seeds=list(SEEDS), panel=records))
    return summaries


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_preaccess_binding(manifest, base):
    """Verify protocol/evaluator commitments without importing controller/generators."""
    try:
        freeze_path, protocol_path = base/"preaccess_freeze.json", base/"protocol.json"
        require(_hash(freeze_path) == manifest["preaccess_sha256"], "preaccess_digest_mismatch")
        frozen = json.loads(freeze_path.read_text(encoding="utf-8-sig"))
        protocol = json.loads(protocol_path.read_text(encoding="utf-8-sig"))
        require(frozen["phase"] == "before_target_acquisition", "invalid_preaccess_phase")
        require(_hash(protocol_path) == frozen["files"]["protocol.json"], "frozen_protocol_digest_mismatch")
        require(_hash(Path(__file__)) == frozen["files"]["evaluator/bodyfat_evaluator.py"], "frozen_evaluator_digest_mismatch")
        actual = [{key: tab[key] for key in IDENTITY_COLUMNS} for tab in manifest["tables"]]
        require(protocol["tables"] == actual, "protocol_manifest_roster_mismatch")
        require(protocol["observed_columns"] == list(OBSERVED_COLUMNS) and protocol["generated_column"] == "bodyfat" and
                protocol["seeds"] == list(SEEDS) and protocol["quantile_intervals"] is False,
                "protocol_evaluator_schema_mismatch")
    except ValidationError:
        raise
    except (OSError, ValueError, KeyError, TypeError):
        raise ValidationError("unreadable_preaccess_binding") from None


def run_evaluation(full_frame_path, manifest_path):
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        raise ValidationError("unreadable_manifest") from None
    validate_manifest(manifest)
    base = Path(manifest_path).resolve().parent
    verify_preaccess_binding(manifest, base)
    resolve = lambda p: Path(p) if Path(p).is_absolute() else base / p
    full = validate_full_frame(read_csv_strict(full_frame_path, FULL_COLUMNS))
    observed_path = resolve(manifest["observed_path"])
    observed = validate_observed(read_csv_strict(observed_path, OBSERVED_COLUMNS), full)
    measured = estimate_panel(full, full.DXDTOPF.to_numpy())
    tables = []
    for tab in manifest["tables"]:
        result = {k: tab[k] for k in (*IDENTITY_COLUMNS, "status")}
        result["sha256"] = None
        error = None
        if tab["status"] == "failed":
            error = "upstream_generation_failed"
        else:
            try:
                path = resolve(tab["path"])
                require(_hash(path) == tab["sha256"], "generated_file_digest_mismatch")
                generated = read_csv_strict(path, GENERATED_COLUMNS)
                result["panel"] = evaluate_table(full, observed, generated, measured)
                result["sha256"] = tab["sha256"]
            except ValidationError as exc:
                error = str(exc)
            except (OSError, ArithmeticError, np.linalg.LinAlgError):
                error = "table_technical_failure"
        if error:
            result["status"] = "failed"
            result["failure"] = error
            result["panel"] = [dict(endpoint=x["endpoint"], kind=x["kind"], units="percentage_points",
                                    status="technical_failure", gate=x["gate"], estimate=None,
                                    signed_error=None, absolute_error=None, se=None, ci_low=None, ci_high=None,
                                    interval_available=False, paired_difference=None) for x in measured]
        tables.append(result)
    return dict(
        schema_version="m13b_aggregate_v1", title=TITLE,
        input_sha256=dict(full_frame=_hash(full_frame_path), observed=_hash(observed_path), manifest=_hash(manifest_path), preaccess=manifest["preaccess_sha256"]),
        panel_count=62, table_count=16, seeds=list(SEEDS), measured=measured, tables=tables,
        exclusion_flow=exclusion_flow(full), seed_summaries=seed_summaries(tables),
        interpretation=dict(
            interval_scope="pointwise_conditional_design_intervals_for_linear_estimands_and_paired_differences_only",
            omitted_uncertainty="source_coefficients_model_construction_transport_measurement_and_between_draw_variation",
            quantiles="weighted_inverse_ecdf_point_estimates_only_no_reference_or_discrepancy_intervals",
            seed_summaries="three_conditional_draws_arithmetic_mean_min_max_not_a_simulation_interval_or_multiple_imputation",
            kish="weight_dispersion_screen_ignores_clustering_not_inferential_sample_size",
            no_aggregate_success_score=True, no_R_survey_cross_validation=True,
        ),
    )


def write_aggregate(result, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    require(not (out/"aggregate.json").exists() and not (out/"aggregate.csv").exists(), "aggregate_output_already_exists")
    # Serializing first prevents partially written results from nonfinite objects.
    serialized = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    rows = []
    for label, panel in [(dict(table_id="measured", kind="measured", builder="", candidate="", seed=None), result["measured"])] + [
            (tab, tab["panel"]) for tab in result["tables"]]:
        for item in panel:
            row = {k: label.get(k) for k in ("table_id", "kind", "builder", "candidate", "seed")}
            row.update({k: item.get(k) for k in ("endpoint", "status", "estimate", "se", "ci_low", "ci_high", "signed_error", "absolute_error", "interval_available")})
            row.update({f"gate_{k}": item["gate"].get(k) for k in ("n", "kish_n", "domain_psus", "domain_strata", "df")})
            row["gate_failures"] = ";".join(item["gate"]["failures"])
            paired = item.get("paired_difference") or {}
            row.update({f"paired_{k}": paired.get(k) for k in ("estimate", "se", "ci_low", "ci_high")})
            rows.append(row)
    (out/"aggregate.json").write_text(serialized, encoding="utf-8")
    pd.DataFrame(rows).to_csv(out/"aggregate.csv", index=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-frame", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_evaluation(args.full_frame, args.manifest)
        write_aggregate(result, args.output_dir)
    except ValidationError as exc:
        print(json.dumps(dict(status="failed", category=str(exc))), file=sys.stderr)
        return 2
    except Exception:
        # No raw rows, values, paths, exception repr or stack trace enter the release/log.
        print(json.dumps(dict(status="failed", category="unexpected_technical_failure")), file=sys.stderr)
        return 3
    print(json.dumps(dict(status="complete", table_count=16, panel_count=62,
                          failed_tables=sum(x["status"] == "failed" for x in result["tables"]))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Invented fixtures only. These tests neither acquire nor read NHANES target rows."""
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

import prep


def fixture():
    # Two nested PSUs per stratum. PSU (11,2) has only a child/out-of-domain row.
    demo = pd.DataFrame({
        "SEQN": range(1, 9), "WTMEC2YR": [1., 2., 3., 4., 5., 6., 0., 8.],
        "SDMVSTRA": [10, 10, 10, 10, 11, 11, 11, 11],
        "SDMVPSU": [1, 1, 2, 2, 1, 2, 1, 2],
        "RIDAGEYR": [20, 59, 35, 42, 29, 7, 33, 48],
        "RIAGENDR": [1, 2, 1, 2, 1, 2, 1, 1],
        "RIDRETH3": [3, 4, 3, 4, 4, 3, 3, 6],
    })
    bmx = pd.DataFrame({"SEQN": range(1, 9), "BMXBMI": [18.5, 29.9, 30, 35, 24, 22, 25, 25]})
    dxx = pd.DataFrame({"SEQN": range(1, 9), "DXAEXSTS": [1, 1, 1, 1, 2, 1, 1, 1],
                        "DXDTOPF": [0., 100., 30., 40., 20., 10., 22., 23.]})
    return demo, bmx, dxx


def test_exact_schemas_domains_and_zero_psu():
    frame, observed, quality = prep.build_frames(*fixture())
    assert list(frame) == prep.FRAME_COLUMNS
    assert list(observed) == prep.GENERATOR_COLUMNS
    assert frame.SEQN.tolist() == [1, 2, 3, 4, 5, 6, 8]
    assert observed.bmi.tolist() == [18.5, 29.9, 30, 35]
    assert observed.id.tolist() == frame.iloc[:4].id.tolist()
    assert observed.id.str.fullmatch(r"m13b_[0-9a-f]{32}").all()
    assert quality["design"]["zero_domain_psus_retained"] == 2
    assert quality["domains"]["primary"]["n"] == 2
    assert quality["domains"]["extension"]["n"] == 2
    np.testing.assert_array_equal(observed.inv_bmi, 1 / observed.bmi)
    np.testing.assert_array_equal(observed.male_inv_bmi, observed.male / observed.bmi)
    np.testing.assert_array_equal(observed.male_age, observed.male * observed.age)
    assert (observed[["asian", "asian_inv_bmi", "asian_age"]] == 0).all().all()


@pytest.mark.parametrize("component", [0, 1, 2])
def test_duplicate_seqn_fails(component):
    tables = list(fixture())
    tables[component] = pd.concat([tables[component], tables[component].iloc[:1]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate SEQN"):
        prep.build_frames(*tables)


@pytest.mark.parametrize("value", [-0.001, 100.001, np.inf, -np.inf])
def test_endpoint_integrity_stops_even_outside_target_domain(value):
    demo, bmx, dxx = fixture()
    dxx.loc[5, "DXDTOPF"] = value
    with pytest.raises(ValueError, match="integrity failure"):
        prep.build_frames(demo, bmx, dxx)


def test_missingness_and_invalid_scan_exclusion_without_frame_loss():
    demo, bmx, dxx = fixture()
    dxx.loc[0, "DXDTOPF"] = np.nan
    frame, observed, q = prep.build_frames(demo, bmx, dxx)
    assert len(frame) == 7 and len(observed) == 3
    c = q["completeness"]["primary_age_race_BMI_frame"]
    assert c["denominator"] == {"n": 3, "weight_sum": 8.0}
    assert c["complete"]["all_covariates_and_valid_endpoint"]["n"] == 1
    assert c["complete"]["all_covariates_and_valid_endpoint"]["weighted_fraction"] == 0.25


def test_missing_component_row_is_left_joined():
    demo, bmx, dxx = fixture()
    frame, observed, _ = prep.build_frames(demo, bmx.iloc[1:], dxx.iloc[1:])
    assert len(frame) == 7 and len(observed) == 3
    assert frame.loc[frame.SEQN.eq(1), "BMXBMI"].isna().all()


def test_component_orphan_rejected():
    demo, bmx, dxx = fixture()
    bmx.loc[0, "SEQN"] = 10000
    with pytest.raises(ValueError, match="absent from DEMO_J"):
        prep.build_frames(demo, bmx, dxx)


def test_full_design_singleton_rejected():
    demo, bmx, dxx = fixture()
    demo.loc[demo.SDMVSTRA.eq(11), "SDMVPSU"] = 1
    with pytest.raises(ValueError, match="singleton"):
        prep.build_frames(demo, bmx, dxx)


def test_permutation_invariance_except_arbitrary_ids():
    tables = fixture()
    a, ao, aq = prep.build_frames(*tables)
    b, bo, bq = prep.build_frames(*[t.sample(frac=1, random_state=55) for t in tables])
    pd.testing.assert_frame_equal(a.drop(columns="id"), b.drop(columns="id"))
    pd.testing.assert_frame_equal(ao.drop(columns="id"), bo.drop(columns="id"))
    assert aq == bq


def test_freeze_mismatch_stops_before_network(tmp_path):
    manifest = tmp_path / "freeze.json"
    manifest.write_text("{}", encoding="utf-8")
    args = type("Args", (), {"freeze_manifest": manifest, "freeze_sha256": "0" * 64,
                             "authorization": tmp_path / "absent.json", "output": tmp_path / "out"})()
    with patch("urllib.request.urlopen") as network:
        with pytest.raises(ValueError, match="SHA256 mismatch"):
            prep.acquire(args)
        network.assert_not_called()
    assert not args.output.exists()


def test_authorization_required_before_frozen_file_read(tmp_path):
    manifest = tmp_path / "freeze.json"
    manifest.write_text(json.dumps({"schema_version": 1, "phase": "before_target_acquisition",
                                    "scientific_revision_allowed": False}), encoding="utf-8")
    auth = tmp_path / "auth.json"
    auth.write_text(json.dumps({"schema_version": "m13b_target_access_authorization_v1",
                                "freeze_manifest_sha256": prep.sha256(manifest),
                                "authorized_by": "root", "target_access_authorized": False}), encoding="utf-8")
    with pytest.raises(ValueError, match="Explicit root"):
        prep.verify_gate(manifest, prep.sha256(manifest), auth)


def test_valid_gate_then_file_mutation_rejected(tmp_path):
    # Only invented metadata/code bytes; mock the script's own path binding.
    code = tmp_path / "prep.py"
    metadata = tmp_path / "metadata_sources.json"
    protocol = tmp_path / "protocol.json"
    prose = tmp_path / "PROTOCOL.md"
    code.write_text("# invented code fixture\n", encoding="utf-8")
    metadata.write_text("{}", encoding="utf-8")
    prose.write_text("Invented freeze fixture.\n", encoding="utf-8")
    protocol.write_text(json.dumps({"target": "NHANES2017-18_DXDTOPF",
                                    "observed_columns": prep.GENERATOR_COLUMNS,
                                    "primary_bmi": [18.5, 30], "primary_upper_inclusive": False,
                                    "extension_bmi": [30, 35]}), encoding="utf-8")
    manifest = tmp_path / "freeze.json"
    manifest.write_text(json.dumps({"schema_version": 1, "phase": "before_target_acquisition",
                                    "scientific_revision_allowed": False,
                                    "created_utc": "2026-01-01T00:00:00+00:00",
                                    "files": {p.name: prep.sha256(p) for p in [code, metadata, protocol, prose]}}),
                        encoding="utf-8")
    auth = tmp_path / "auth.json"
    auth.write_text(json.dumps({"schema_version": "m13b_target_access_authorization_v1",
                                "freeze_manifest_sha256": prep.sha256(manifest), "authorized_by": "root",
                                "authorized_at_utc": "2026-01-02T00:00:00+00:00",
                                "target_access_authorized": True}), encoding="utf-8")
    with patch.object(prep, "__file__", str(code)), patch.object(prep, "METADATA", metadata):
        assert prep.verify_gate(manifest, prep.sha256(manifest), auth)["frozen_file_count"] == 4
        prose.write_text("Changed.\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing or changed"):
            prep.verify_gate(manifest, prep.sha256(manifest), auth)


def test_extra_dxa_family_not_exported_to_generator():
    demo, bmx, dxx = fixture()
    dxx["DXDHEPF"] = 123456.0
    dxx["private_sentinel"] = "must_not_escape"
    frame, observed, _ = prep.build_frames(demo, bmx, dxx)
    assert list(frame) == prep.FRAME_COLUMNS
    assert list(observed) == prep.GENERATOR_COLUMNS

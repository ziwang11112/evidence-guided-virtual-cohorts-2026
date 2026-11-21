"""Count measured sampling frames and distinct constructor roles in the KDD experiments."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
KENYA = "lifestyle_application_2026-11-11"
PAPER = "original_paper_capability_2026-11-17"
FREETOWN = "prospective_bp_freetown_2026-11-18"
BURKINA = "original_paper_iron_sensitivity_2026-11-19"
CHNS = "chns_iron_conditional_holdout_2026-11-19"
NIGERIA = "prospective_iron_dependence_2026-11-20"
ETH = "nonhdl_external_2026-11-20"
VIRGINIA = "prospective_lipid_use_2026-11-21"
ANCHORS = "lipid_population_anchors_2026-11-21"
ALTERNATIVES = "kdd_v40_pairing_review_2026-11-20"
GRIP = "bilateral_grip_transfer_2026-11-21"


def read(path):
    return json.loads((WORK / path).read_text(encoding="utf-8-sig"))


def measured_frames():
    rows = []
    def add(domain, family, frame, country, name, receipt, get_n):
        size = get_n(read(receipt))
        assert isinstance(size, int) and size > 0
        rows.append(dict(domain=domain, study_family=family, recruitment_period=frame, country=country,
                         measured_sample=name, n=size, receipt=receipt))
    add("Lifestyle", "Turkana", "Turkana", "Kenya", "Turkana lifestyle study, eligible roster",
        KENYA + "/ANALYSIS_RESULTS.json",
        lambda d: next(r for r in d["results"] if r["kind"] == "real_reference")["analysis"]["eligible_age_rows"])
    add("Pressure", "PNS", "PNS laboratory cohort", "Brazil", "Brazilian National Health Survey",
        "parameter_attribution_2026-11-10/PNS_AUDIT.json", lambda d: d["analysis_rows"][0]["target_reference"]["n"])
    add("Pressure", "Freetown screening", "Freetown screening", "Sierra Leone", "Freetown community screening",
        FREETOWN + "/AGGREGATES.json", lambda d: d["target"]["n"])
    add("Iron", "NHANES", "NHANES 2021–23", "United States", "NHANES 2021–23 women with paired iron measurements",
        "iron_evidence_content_control_2026-11-16/analysis/REFERENCE_USED.json",
        lambda d: d["original_aggregate"]["flow"]["eligible_with_both"])
    add("Iron", "Rural Burkina Faso mothers", "Burkina Faso mothers", "Burkina Faso", "Mothers with paired measurements",
        BURKINA + "/REVEAL.json", lambda d: d["result"]["n_complete"])
    add("Iron", "CHNS", "CHNS 2009 communities B", "China", "CHNS held-out communities",
        CHNS + "/RESULTS.json", lambda d: d["reference"]["n"])
    add("Iron", "Akwa Ibom", "Akwa Ibom mothers", "Nigeria", "Akwa Ibom mothers",
        NIGERIA + "/RESULTS.json", lambda d: d["reference"]["n"])
    for key, family in (("mekelle", "Mekelle residents"), ("workers", "Haramaya University employees")):
        add("Lipids", family, family, "Ethiopia", family, ETH + "/RESULTS.json",
            lambda d: d["cohorts"][key]["n"])
    add("Lipids", "Virginia community screening", "Virginia community screening", "United States",
        "Central Virginia, both counties", VIRGINIA + "/RESULTS.json", lambda d: d["estimates"]["all"]["n"])
    for key, frame in (("J", "NHANES 2017–18"), ("L", "NHANES 2021–23")):
        add("Lipids", "NHANES", frame, "United States", frame + " adult lipid sample", ANCHORS + "/RESULTS.json",
            lambda d: d["reference"][key]["qc"]["both_measures_weighted"])
    for key, family, period, country in (("US_NHANES","NHANES","NHANES 2011–12","United States"),
            ("ZA_HAALSI","HAALSI","Agincourt baseline","South Africa"),
            ("BR_RIO_MAX","EDOC","Rio Branco EDOC","Brazil")):
        add("Handgrip", family, period, country, period + " ages 50–69", GRIP + "/RESULTS.json",
            lambda d: d["reference"][key]["qc"]["eligible_bilateral"])
    return rows


def constructor_counts():
    rows = []
    def add(label, path, constructors, outputs, note=""):
        rows.append(dict(batch=label, receipt=path, initial_sessions=constructors, seeded_model_outputs=outputs, note=note))
    path = KENYA + "/ANALYSIS_RESULTS.json"
    slots = [r for r in read(path)["results"] if r["kind"] == "virtual"]
    assert len({r["dataset_id"] for r in slots}) == len(slots) and all(r["status"] == "computed" for r in slots)
    add("Kenyan lifestyle", path, len({r["dataset_id"].rsplit("_s", 1)[0] for r in slots}), len(slots))
    path = PAPER + "/analysis/CLOSEOUT_QA.json"
    closed = read(path)
    assert closed["status"] == "pass" and closed["failed_or_unavailable"] == 0
    add("Original-paper pressure and iron", path, closed["constructors"], closed["successful_slots"])
    for label, folder in (("Pressure evidence conditions", "pns_evidence_content_control_2026-11-16"),
                          ("Iron evidence conditions", "iron_evidence_content_control_2026-11-16")):
        path = folder + "/EXECUTION_CLOSURE.json"
        runs = read(path)["rows"]
        assert all(row["status"] == "success" for row in runs)
        add(label, path, len({row["id"] for row in runs}), len(runs))
    path = FREETOWN + "/CLOSURE.json"
    closed = read(path)
    add("Freetown pressure", path, len(closed["calls"]), sum(row["arm"] != "statistical" for row in closed["tables"]),
        "One constructor proposed two laws.")
    path = BURKINA + "/INTERFACE_CLOSURE.json"
    laws = {k: v for k, v in read(path)["laws"].items() if k != "statistical"}
    add("Burkina Faso iron", path, len(read(BURKINA + "/PARENT_CLOSURE.json")["sealed"]),
        sum(len(v["draws"]) for v in laws.values()), "Includes completed branches. Two requested alternatives hit the output limit.")
    path = CHNS + "/SOURCE_CLOSURE.json"
    models = read(path)["models"]
    assert all(m["usable"] for m in models.values())
    add("CHNS conditional revisions", path, len(read(CHNS + "/PARENTS.json")["parents"]),
        sum(len(m["runs"]) for m in models.values()), "Initial programs and both sibling revisions counted at the output level.")
    path = NIGERIA + "/DRAW_CLOSURE.json"
    agents = [v for k, v in read(path)["models"].items() if k.startswith("author")]
    assert all(v["usable"] for v in agents)
    add("Nigerian iron", path, len(agents), sum(len(v["runs"]) for v in agents))
    path = ETH + "/MODEL_CLOSURE.json"
    arm = read(path)["arms"]["agent"]
    assert arm["usable"] and read(ETH + "/AUTHOR.json")["status"] == "received"
    add("External Ethiopian lipids", path, 1, len(arm["runs"]), "The same generated records were used in both populations.")
    path = ALTERNATIVES + "/SENSITIVITY.json"
    agents = read(path)["authors"]
    assert all(v["both_pass"] for v in agents.values())
    add("Lipid pairing alternatives", path, len(agents),
        sum(len(draws) for v in agents.values() for draws in v["runs"].values()), "Two laws per constructor.")
    path = ANCHORS + "/PREDICTIONS.json"
    agents = read(path)["execution"]
    assert all(v["usable"] for v in agents.values())
    add("Historical US lipid adaptation", path, len(agents), 0,
        "The four authors adapted marginals on existing paired draws. These transformations add no newly sampled pairing.")
    path = GRIP + "/PREDICTIONS.json"
    agents = [v for v in read(path)["methods"].values() if "draws" in v]
    add("Bilateral handgrip", path, len(agents), sum(len(v["draws"]) for v in agents),
        "Four marginal-only programs yielded the same pairing at each shared seed.")
    return rows


if __name__ == "__main__":
    frames = measured_frames()
    batches = constructor_counts()
    counts = {"analysis_families": len({r["domain"] for r in frames}), "domain_sample_evaluations": len(frames),
              "recruitment_periods": len({r["recruitment_period"] for r in frames}),
              "study_families": len({r["study_family"] for r in frames}), "countries": len({r["country"] for r in frames}),
              "named_constructor_batches": len(batches), "initial_sessions": sum(r["initial_sessions"] for r in batches),
              "seeded_model_outputs": sum(r["seeded_model_outputs"] for r in batches)}
    output = {"counts": counts, "measured_comparisons": frames, "constructor_batches": batches,
              "scope": "Measured targets and twelve case-specific construction batches reported in the KDD study. Source populations, advisers, general workflow pilots, numerical comparators and repeat analyses are excluded from the construction subtotal. Outputs include sibling variants and can be identical."}
    (HERE / "COVERAGE.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(counts)

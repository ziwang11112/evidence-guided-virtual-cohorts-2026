"""Aggregate-only presentation QA. Does not import the renderer or analysis."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

U = Path(__file__).resolve().parent
R = U / "report"
TRAITS = ["bmi", "total_cholesterol", "hdl_cholesterol"]
TITLES = ["BMI", "Total cholesterol", "HDL cholesterol"]
CONS = ["rural_minus_pastoralist", "urban_minus_pastoralist", "urban_minus_rural"]
NAMES = ["Rural − pastoralist", "Urban − pastoralist", "Urban − rural"]
checks = []


def check(name, ok, detail=None):
    checks.append(dict(name=name, passed=bool(ok), detail=detail))
    assert ok, (name, detail)


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def num(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def pv(x):
    return "—" if x is None else f"{x:.3g}" if x else "0 (numeric underflow)"


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.external_scripts = [], []
        self.t = self.r = self.c = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.external_scripts.append(attrs["src"])
        if tag == "table":
            self.t = []
        elif tag == "tr" and self.t is not None:
            self.r = []
        elif tag in ["td", "th"] and self.r is not None:
            self.c = []

    def handle_data(self, data):
        if self.c is not None:
            self.c.append(data)

    def handle_endtag(self, tag):
        if tag in ["td", "th"] and self.c is not None:
            self.r.append("".join(self.c)); self.c = None
        elif tag == "tr" and self.r is not None:
            self.t.append(self.r); self.r = None
        elif tag == "table" and self.t is not None:
            self.tables.append(self.t); self.t = None


def main():
    ds = read(U / "ANALYSIS_RESULTS.json")["results"]
    text = (R / "index.html").read_text(encoding="utf-8")
    check("seven aggregate datasets", len(ds) == 7)
    check("189 contrast records", sum(len(d["analysis"]["contrasts"]) for d in ds) == 189)
    check("21 interaction records", sum(len(d["analysis"]["interactions"]) for d in ds) == 21)
    check("all seven analyses computed", all(d["status"] == "computed" for d in ds))
    ref = next(d for d in ds if d["kind"] == "real_reference")
    virtual = [d for d in ds if d["kind"] == "virtual"]
    check("two constructors each three registered seeds", all(sorted(d["seed"] for d in virtual if d["episode_id"] == "LIFESTYLE_"+a) == [64001, 64003, 64007] for a in ["A1", "A2"]))
    check("real sample sizes", {r["trait"]: r["n"] for r in ref["analysis"]["trait_status"]} == dict(zip(TRAITS, [1189, 400, 405])))
    check("all virtual trait sample sizes 1226", all(r["n"] == 1226 for d in virtual for r in d["analysis"]["trait_status"]))
    interactions = [(d["dataset_id"], r["trait"], r["p_value"]) for d in ds for r in d["analysis"]["interactions"] if r["selects_sex_specific"]]
    check("only specified HDL interaction branch", len(interactions) == 1 and interactions[0][:2] == ("LIFESTYLE_A1_s64001", "hdl_cholesterol"), interactions)
    for trait in TRAITS[1:]:
        rs = next(r["sample_sd"] for r in ref["analysis"]["trait_status"] if r["trait"] == trait)
        vals = [next(r["sample_sd"] for r in d["analysis"]["trait_status"] if r["trait"] == trait) for d in virtual]
        check(trait+" virtual SD below reference in all six draws", max(vals) < rs, dict(reference=rs, virtual_range=[min(vals), max(vals)]))
    outcomes = [read(U / "episodes" / ("LIFESTYLE_"+a) / "OUTCOME.json") for a in ["A1", "A2"]]
    cost = sum(o["known_tariff_cost_usd"] for o in outcomes)
    check("total recorded known tariff USD", abs(cost-.3746075) < 1e-12, cost)
    check("31 receipted calls and no unknown usage", sum(o["calls_receipted"] for o in outcomes) == 31 and sum(o["unknown_usage_calls"] for o in outcomes) == 0)
    parser = Tables(); parser.feed(text)
    ct = [t for t in parser.tables if "SD effect" in t[0]]
    it = [t for t in parser.tables if "LR statistic" in t[0]]
    check("HTML includes seven full contrast tables", len(ct) == 7 and all(len(t) == 28 for t in ct))
    check("HTML includes seven full LRT tables", len(it) == 7 and all(len(t) == 4 for t in it))
    for d, tab, lt in zip(ds, ct, it):
        records = {(r["trait"], r["stratum"], r["contrast"]): r for r in d["analysis"]["contrasts"]}
        expected = []
        for ti, t in enumerate(TRAITS):
            for s in ["pooled", "F", "M"]:
                for ci, c in enumerate(CONS):
                    r = records[t, s, c]
                    expected.append([TITLES[ti], s, NAMES[ci], r["status"], "yes" if r["selected_by_paper_rule"] else "no", str(r["n"]), num(r["estimate"]), num(r["lower"])+", "+num(r["upper"]), num(r["raw_estimate"]), num(r["raw_lower"])+", "+num(r["raw_upper"]), "kg/m²" if t == "bmi" else "mg/dL", pv(r["p_value"]), pv(r.get("q_subset_bh9")), ""])
        check("HTML exact numeric mapping "+d["dataset_id"], tab[1:] == expected)
        lr_expected = []
        for ti, t in enumerate(TRAITS):
            r = next(r for r in d["analysis"]["interactions"] if r["trait"] == t)
            reason = "—" if d.get("error", "") is None else d.get("error", "")
            lr_expected.append([TITLES[ti], r["status"], num(r["lr"]), str(r["df"]), pv(r["p_value"]), "yes" if r["selects_sex_specific"] else "no", reason])
        check("HTML LRT numeric mapping "+d["dataset_id"], lt[1:] == lr_expected)
        sds = {r["trait"]: r["sample_sd"] for r in d["analysis"]["trait_status"]}
        check("raw/SD aggregate mapping "+d["dataset_id"], all(abs(r["raw_"+k]-r[k]*sds[r["trait"]]) < 1e-10 for r in d["analysis"]["contrasts"] for k in ["estimate", "se", "lower", "upper"]))

    def get(d, t, c):
        return next(r for r in d["analysis"]["contrasts"] if r["trait"] == t and r["stratum"] == "pooled" and r["contrast"] == c)

    ns = {"s": "http://www.w3.org/2000/svg"}
    figures = []
    for stem, raw in [("lifestyle_contrasts_standardized", False), ("lifestyle_contrasts_raw", True)]:
        root = ET.parse(R / (stem+".svg")).getroot()
        axes = [g for g in root.findall(".//s:g", ns) if re.fullmatch(r"axes_\d+", g.get("id", ""))]
        check(stem+" has three axes", len(axes) == 3)
        count, maxerr = 0, 0.
        for axis, trait in zip(axes, TRAITS):
            ticks = []
            for g in axis.findall(".//s:g", ns):
                if g.get("id", "").startswith("xtick_"):
                    texts, uses = g.findall(".//s:text", ns), g.findall(".//s:use", ns)
                    if texts and uses:
                        lab = "".join(texts[0].itertext()).replace("−", "-")
                        try: ticks.append((float(lab), float(uses[0].get("x"))))
                        except ValueError: pass
            assert len(ticks) >= 2
            (v0, x0), (v1, x1) = ticks[:2]
            slope = (x1-x0)/(v1-v0); offset = x0-slope*v0
            color_values = {}
            for g in axis.findall(".//s:g", ns):
                if not g.get("id", "").startswith("line2d"): continue
                for mark in g.findall(".//s:use", ns):
                    style = mark.get("style", "")
                    match = re.search(r"fill: (#[a-f0-9]+)", style)
                    if not match: continue
                    color = match.group(1)
                    if color in ["#7653aa", "#d68032"] or (color == "#233c62" and "stroke-linejoin: miter" in style):
                        color_values.setdefault(color, []).append((float(mark.get("x"))-offset)/slope)
            for color, ep in [("#233c62", None), ("#7653aa", "LIFESTYLE_A1"), ("#d68032", "LIFESTYLE_A2")]:
                column = "raw_estimate" if raw else "estimate"
                want = []
                for c in CONS:
                    group = [ref] if ep is None else sorted([d for d in virtual if d["episode_id"] == ep], key=lambda d: d["seed"])
                    want.extend(get(d, trait, c)[column] for d in group)
                got = color_values.get(color, [])
                assert len(got) == len(want), (stem, trait, color, len(got), len(want))
                errors = [abs(a-b) for a, b in zip(got, want)]
                maxerr = max(maxerr, max(errors)); count += len(errors)
        check(stem+" SVG point coordinate mapping", maxerr < 2e-5, dict(points_mapped=count, maximum_inverse_transform_error=maxerr))
        figures.append(dict(figure=stem, points_mapped=count, max_error=maxerr))
    check("standalone HTML no external scripts", not parser.external_scripts)
    for phrase in ["What happened in this run", "1.882", "1.700 to 2.251", "0.4751", "A1 0.4512; A2 0.4955", "20.342", "13.732 to 18.907", "0.02457", "0.66618", "$0.3746075", "Source-rich reconstruction", "original paper’s 11-outcome", "nine pooled contrasts", "not confidence intervals", "not independent discovery", "Both reference 95% intervals include zero"]:
        check("report scope or numeric text: "+phrase, phrase in text)
    receipt = read(R / "REPORT_RECEIPT.json")
    check("receipt input hashes unchanged", all(sha(Path(n)) == v for n, v in receipt["input_sha256"].items()))
    check("receipt output hashes current", all(sha(R / n) == v for n, v in receipt["output_sha256"].items()))
    qa = dict(created_utc=datetime.now(timezone.utc).isoformat(), status="PASS",
              scope="Presentation/static QA with aggregate-only numeric mapping; not an independent scientific recomputation",
              patient_rows_read=False, generated_rows_read=False, browser_opened=False, browser_restriction_respected=True,
              report_script_modified=True, changes=["Added data-derived What happened in this run", "Added exact total recorded tariff cost and call count", "Rerendered presentation files; scientific inputs unchanged"],
              checks=checks, figures=figures, reference_n=dict(zip(TRAITS, [1189, 400, 405])), virtual_n_per_trait=1226,
              known_tariff_total_usd=cost, total_datasets=len(ds), total_contrasts=189, total_interactions=21,
              report_sha256=sha(R / "index.html"), renderer_sha256=sha(U / "render_report.py"), aggregate_sha256=sha(U / "ANALYSIS_RESULTS.json"),
              qa_script_sha256=sha(__file__), limits=["No full-page browser layout or toggle interaction test: prior Chrome file URL restriction not bypassed.", "Root reported exported PNG visual inspection; this QA checks SVG numeric positions and static HTML.", "Reference OLS intervals do not identify population truth.", "Seed spread is draw variation, not evidence uncertainty."],
              preliminary_qa_note="An initial checker expected blank reason cells for successful virtual LRT records; their null reasons render as em dashes. Corrected the checker; no scientific or displayed numeric defect was found.")
    (U / "REPORT_QA.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    (R / "README.txt").write_text("Lifestyle application report\n\nOpen index.html for the self-contained English report. Standardized and raw-unit charts are embedded; buttons switch the view without external code. Separate SVG/PNG/PDF exports are provided for both scales.\n\nThis version includes all 7 aggregate datasets, 189 contrasts and 21 interaction tests. It summarizes the positive urban BMI pattern and the lipid-scale/rural-contrast mismatches without hiding either. One HDL interaction branch changes in A1 seed 64001. Original-paper evidence was allowed; this is source-rich reconstruction of 3 traits, not independent validation of all original findings.\n\nPresentation QA: REPORT_QA.json in the parent directory. No patient or generated row data were read by rendering or presentation QA. Browser preview was not attempted after the existing Chrome file restriction. The root task inspected the exported figures.\n", encoding="utf-8")
    print(json.dumps(dict(status="PASS", checks=len(checks), datasets=7, contrasts=189, interactions=21, plot_points_checked=sum(r["points_mapped"] for r in figures), cost=cost, report_sha256=qa["report_sha256"])))


if __name__ == "__main__":
    main()

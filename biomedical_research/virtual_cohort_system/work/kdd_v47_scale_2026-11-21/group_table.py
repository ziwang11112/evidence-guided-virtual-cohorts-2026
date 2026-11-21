"""Typeset every subgroup including the measurement stress test from aggregate estimates."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1] / "manuscript/kdd_draft_v47_2026-11-21"


def main():
    data = json.loads((HERE / "GRIP_GROUPS.json").read_text(encoding="utf-8"))
    models = data["method_scores"]
    header = r"""
\begin{table*}[t]
\caption{Mean absolute between-hand grip difference in kg. Marginal-only authors all returned the same pairing. J authors also received the German hand-ratio evidence. Each measured interval is pointwise. Each method uses the same Australian single-hand values.}
\label{tab:gripgroups}
\small\centering
\begin{tabular}{@{}llrrrrrr@{}}
\toprule
Study & Sex and age & $n$ & Measured [95\% interval] & Independent & Agent, marginals & Agent, J range & J rule\\
\midrule"""
    lines = [header.strip()]
    for key, name in (("US_NHANES", "US NHANES"), ("ZA_HAALSI", "Rural South Africa"),
                      ("BR_RIO_MAX", "Rio Branco (max.)")):
        if key != "US_NHANES":
            lines.append(r"\addlinespace")
        for i, (group, label) in enumerate((("F50", "Women 50--59"), ("F60", "Women 60--69"),
                                           ("M50", "Men 50--59"), ("M60", "Men 60--69"))):
            measured = data["measured"][key]["groups"][group]
            value = measured["mean_gap_kg"]
            lo, hi = measured["mean_gap_ci"]
            joint = [models[f"J{k}"][group]["mean_gap_kg"] for k in range(1, 5)]
            fields = [name if i == 0 else "", label, str(measured["n"]), f"{value:.2f} [{lo:.2f}, {hi:.2f}]",
                      f'{models["independent"][group]["mean_gap_kg"]:.2f}', f'{models["M1"][group]["mean_gap_kg"]:.2f}',
                      f"{min(joint):.2f}--{max(joint):.2f}", f'{models["ratio_rule"][group]["mean_gap_kg"]:.2f}']
            lines.append(" & ".join(fields) + r"\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    (PAPER / "grip_groups_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

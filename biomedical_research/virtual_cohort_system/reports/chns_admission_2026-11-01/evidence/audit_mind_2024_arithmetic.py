"""Recompute published aggregate arithmetic; never reads patient data."""
from fractions import Fraction
from pathlib import Path
import json


def kappa(table):
    n = sum(map(sum, table))
    observed = Fraction(table[0][0] + table[1][1], n)
    expected = sum(Fraction(sum(table[i]) * sum(row[i] for row in table), n*n) for i in range(2))
    return float((observed - expected) / (1 - expected))


def main():
    tables = {
        "FSG": {"cells": [[3029, 12], [21, 485]], "published_kappa": 0.962},
        "HbA1c": {"cells": [[2848, 193], [9, 497]], "published_kappa": 0.812},
    }
    for item in tables.values():
        t = item["cells"]
        item["n"] = sum(map(sum, t))
        item["computed_cohen_kappa"] = kappa(t)
        item["matches_published_rounding_3dp"] = round(item["computed_cohen_kappa"], 3) == item["published_kappa"]
        derived = [[t[0][0], t[0][1]], [t[1][0], t[1][1] - 425]]
        item["conditional_history_free_derivation"] = {
            "assumption": "Same 425 known-history cases positive under both composites; same analytic sample without differential exclusion; common history/treatment set exactly those 425",
            "cells": derived, "n": sum(map(sum, derived)), "kappa": kappa(derived),
            "sensitivity": derived[1][1] / sum(derived[1]),
            "specificity": derived[0][0] / sum(derived[0]),
            "ppv": derived[1][1] / (derived[0][1] + derived[1][1]),
        }
    output = {
        "source_doi": "10.1371/journal.pone.0296694", "source_locator": "Table 3; ordinary Cohen formula in Methods",
        "source_aggregate_arithmetic_only": True, "target_data_accessed": False,
        "row_axis": "FPG composite negative, positive", "column_axis": "Other composite negative, positive",
        "tables": tables,
        "decision": "Quarantine conflicting HbA1c table/kappa bundle pending source clarification; no silent correction or calibration.",
        "independence": "Derived cells and ratios are not additional independent evidence.",
    }
    (Path(__file__).parent / "MIND_2024_ARITHMETIC.json").write_bytes((json.dumps(output, indent=2)+"\n").encode())
    print(json.dumps({name: {k: v for k,v in item.items() if k in ('computed_cohen_kappa','matches_published_rounding_3dp')} for name,item in tables.items()}, indent=2))


if __name__ == "__main__":
    main()

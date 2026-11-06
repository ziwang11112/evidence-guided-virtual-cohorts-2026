"""What Zhu et al. Table IV alone identifies. No biomedical records are generated.

This analytic example uses ranks, not hemoglobin/ferritin concentrations.
The two laws need not reproduce other tables in the paper.
"""
from fractions import Fraction as F
import json


def check():
    # Rows: Hb <120 vs >=120 g/L; columns: ferritin <15 vs >=15 microgram/L.
    counts = ((173, 85), (331, 1082))
    n = sum(map(sum, counts))
    p = [[F(k, n) for k in row] for row in counts]
    h = [sum(row) for row in p]
    f = [sum(column) for column in zip(*p)]
    assert n == 1671 and h[0] == F(258, n) and f[0] == F(504, n)
    odds_ratio = p[0][0] * p[1][1] / (p[0][1] * p[1][0])
    rho = {}
    for label, sign in [("reversed_within_cells", -1), ("aligned_within_cells", 1)]:
        euv = F(0)
        for i in range(2):
            for j in range(2):
                umid = sum(h[:i]) + h[i] / 2
                vmid = sum(f[:j]) + f[j] / 2
                # Conditional on the cell, both ranks are uniform on their
                # intervals; one uses T and the other T (or 1-T), T~U(0,1).
                euv += p[i][j] * (umid * vmid + sign * h[i] * f[j] / 12)
        # The unconditional rank margins are uniform on [0,1].
        rho[label] = 12 * euv - 3
    assert -1 <= rho["reversed_within_cells"] < 0 < rho["aligned_within_cells"] <= 1
    return {
        "n_source": n, "counts_hb_rows_ferritin_columns": counts,
        "threshold_odds_ratio": float(odds_ratio),
        "spearman_for_two_constructed_rank_laws": {k: float(v) for k, v in rho.items()},
    }


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))

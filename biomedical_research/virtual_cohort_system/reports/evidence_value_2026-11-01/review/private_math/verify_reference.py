"""Reviewer-only deterministic algebra/quadrature check; no rows or RNG.

Keep its numeric report in custody until complete output commitments permit reveal.
It does not import the custodian's reference implementation or evaluator.
"""
from pathlib import Path
import json
import hashlib
import math
import numpy as np
from scipy.integrate import quad
from scipy.stats import norm, t

ROOT = Path(__file__).resolve().parents[2]
law = json.loads((ROOT / "private/LAW.json").read_text(encoding="utf-8"))
recorded = json.loads((ROOT / "private/REFERENCE.json").read_text(encoding="utf-8"))
par = law["parameters"]
offset, group_shift, base, interaction, residual_sd = (par[k] for k in ("mu", "a", "b", "d", "sigma"))
assert residual_sd > 0
assert t.var(df=3) / 3 == 1


def moments(p, sign):
    mean = np.zeros(3)
    second = np.zeros((3, 3))
    for g, weight in ((0, 1-p), (1, p)):
        y_mean = offset + group_shift*g
        slope = base + sign*interaction*(2*g-1)
        first_g = np.array([g, 0, y_mean], dtype=float)
        second_g = np.array([[g*g, 0, g*y_mean], [0, 1, slope],
                             [g*y_mean, slope, y_mean*y_mean + slope*slope + residual_sd*residual_sd]])
        mean += weight*first_g
        second += weight*second_g
    return mean, second - np.outer(mean, mean)


def probability_tail(sign, family, low, high):
    def integrand(x):
        prob = 0.0
        for g, weight in ((0, 1-law["target_p"]), (1, law["target_p"])):
            location = offset + group_shift*g + (base + sign*interaction*(2*g-1))*x
            z = (law["analysis"]["tail"]["y_cut"] - location)/residual_sd
            sf = norm.sf(z) if family == "normal" else t.sf(math.sqrt(3)*z, df=3)
            prob += weight*sf
        return float(norm.pdf(x)*prob)
    value, error = quad(integrand, low, high, epsabs=2e-13, epsrel=2e-12, limit=250)
    assert error < 1e-11
    return value, error


source_versions = []
worlds = {}
for label, sign in (("plus", 1), ("minus", -1)):
    mean_s, cov_s = moments(law["source_p"], sign)
    source = {v+"_mean":float(mean_s[i]) for i,v in enumerate(("g","x","y"))}
    source.update({v+"_sd":float(np.sqrt(cov_s[i,i])) for i,v in enumerate(("g","x","y"))})
    source.update(cov_g_x=float(cov_s[0,1]), cov_g_y=float(cov_s[0,2]), cov_x_y=float(cov_s[1,2]))
    for key, value in source.items():
        np.testing.assert_allclose(value, recorded["source"][key], rtol=1e-12, atol=1e-12)
    source_versions.append(source)
    mean_t, cov_t = moments(law["target_p"], sign)
    slope = float(cov_t[1,2]/cov_t[1,1])
    intercept = float(mean_t[2] - slope*mean_t[1])
    for family in ("normal", "t3"):
        reference = recorded["worlds"][label+"_"+family]
        np.testing.assert_allclose([slope, intercept, mean_t[2], np.sqrt(cov_t[2,2])],
            [reference["primary_slope"], reference["primary_intercept"], reference["target_y_mean"], reference["target_y_sd"]], rtol=1e-12, atol=1e-12)
        for g in (0,1):
            expected={"x_mean":0.,"x_sd":1.,"intercept":offset+group_shift*g,
                      "slope":base+sign*interaction*(2*g-1),"residual_sd":residual_sd}
            assert expected == reference["conditional"][str(g)]
        cut=law["analysis"]["tail"]["x_cut"]
        right, err_r = probability_tail(sign,family,cut,np.inf)
        left, err_l = probability_tail(sign,family,-np.inf,-cut)
        tail={"right_probability":right,"left_probability":left,"contrast":right-left}
        difference={key:tail[key]-reference["tail"][key] for key in tail}
        assert max(abs(v) for v in difference.values()) < 3e-11
        worlds[label+"_"+family]={"primary_slope":slope,"primary_intercept":intercept,
            "tail":tail,"tail_difference_from_custodian":difference,"quad_estimated_errors":[err_r,err_l]}
    assert abs(worlds[label+"_normal"]["tail"]["contrast"]-worlds[label+"_t3"]["tail"]["contrast"]) > 1e-10
for key in source_versions[0]:
    np.testing.assert_allclose(source_versions[0][key],source_versions[1][key],rtol=1e-12,atol=1e-12)
assert worlds["plus_normal"]["primary_slope"] != worlds["minus_normal"]["primary_slope"]

# Visible packets: no row data and no hidden-family claims. The numerical
# conditional records agree with custody, while common first/second moments stay fixed.
evidence={arm:json.loads((ROOT/f"bundles/{arm}/evidence.json").read_text(encoding="utf-8")) for arm in "ABCD"}
assert evidence["A"]["sources"] == evidence["A"]["items"] == []
assert evidence["B"]["items"] == evidence["C"]["items"][:9] == evidence["D"]["items"][:9]
for arm,label in (("C","plus"),("D","minus")):
    items={item["id"]:item for item in evidence[arm]["items"]}
    for g in (0,1):
        condition=recorded["worlds"][label+"_normal"]["conditional"][str(g)]
        for suffix,key in (("X_MEAN","x_mean"),("X_SD","x_sd"),("Y_INTERCEPT","intercept"),("Y_SLOPE","slope"),("RESIDUAL_SD","residual_sd")):
            item=items[f"E_G{g}_{suffix}"]
            assert item["estimate"]==condition[key] and f"Conditional on g={g}." in item["selection"]

report={"status":"passed","law_sha256":hashlib.sha256((ROOT/"private/LAW.json").read_bytes()).hexdigest(),
        "reference_sha256":hashlib.sha256((ROOT/"private/REFERENCE.json").read_bytes()).hexdigest(),
        "independent_source_moments":source_versions,"independent_worlds":worlds,
        "method":"Separate conditional moment recombination and scipy adaptive infinite-range quadrature, with scipy standardized-t3 survival; no custodian code import, RNG or generated rows.",
        "limits":"Quadrature error estimates and cross-method agreement are numerical checks, not a formal interval proof. No biomedical claim.",
        "visibility":"reviewer custody only until all output commitments complete"}
with Path(__file__).with_name("RESULT.json").open("x",encoding="utf-8",newline="\n") as handle:
    json.dump(report,handle,indent=2,allow_nan=False);handle.write("\n")
print(json.dumps({"status":"passed","checked_worlds":4,"source_equivalence":True,
                  "conditional_packet_consistency":True,"tail_nonidentification_witness":True,"rows_generated":0}))

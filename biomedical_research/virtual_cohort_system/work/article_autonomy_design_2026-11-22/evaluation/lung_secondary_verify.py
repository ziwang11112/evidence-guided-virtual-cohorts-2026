"""Independent scalar recomputation on already-frozen pulmonary virtual tables."""
import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def age_model(rows):
    fvc, age, fev = zip(*[(x, t, y) for y, x, t in rows])
    mx, mt, my = map(statistics.fmean, (fvc, age, fev))
    centered = [(x - mx, t - mt, y - my) for x, t, y in zip(fvc, age, fev)]
    xx, tt, xy, ty, xt = [math.fsum(v[i] * v[j] for v in centered)
                           for i, j in ((0, 0), (1, 1), (0, 2), (1, 2), (0, 1))]
    det = xx * tt - xt * xt
    if det <= 0 or math.isclose(xx * tt, xt * xt, rel_tol=1e-12):
        return None
    bx, bt = (xy * tt - ty * xt) / det, (ty * xx - xy * xt) / det
    sst = math.fsum(y*y for _, _, y in centered)
    rss = math.fsum((y-bx*x-bt*t)**2 for x, t, y in centered)
    return dict(intercept=my - bx * mx - bt * mt, fvc_slope=bx, age_slope=bt,
                r_squared=1 - rss / sst if sst > 0 else None,
                age_mean=mt, age_sd=statistics.stdev(age))


def summarize(rows, age):
    n = len(rows)
    if not n:
        raise ValueError("Requested equal-sex estimand needs both groups")
    if any(not all(math.isfinite(v) for v in row if v is not None) for row in rows):
        raise ValueError("Nonfinite measurement: cannot silently discard")
    fvc_nonpositive = sum(x <= 0 for _, x, _ in rows)
    ratios = [y / x for y, x, _ in rows if x > 0]
    summary = dict(n=n, fev1_nonpositive=sum(y <= 0 for y, _, _ in rows),
                   fvc_nonpositive=fvc_nonpositive, fev1_above_fvc=sum(y>x for y,x,_ in rows),
                   unique_measurement_pairs=len({(y,x) for y,x,_ in rows}),
                   unique_fev1_values=len({y for y,_,_ in rows}),
                   unique_fvc_values=len({x for _,x,_ in rows}),
                   fev1_mean=statistics.fmean(y for y,_,_ in rows),
                   fvc_mean=statistics.fmean(x for _,x,_ in rows))
    if fvc_nonpositive:
        raise ValueError("FEV1/FVC denominator nonpositive: ratio output not defined for all rows")
    summary.update(screened=sum(r < .70 for r in ratios),
                   near_cutoff=sum(.695 <= r <= .705 for r in ratios),
                   mean_individual_ratio_pct=100 * statistics.fmean(ratios))
    if age:
        summary["age_model"] = age_model(rows)
    return summary


def independently_recompute(path, args):
    groups = {"male": [], "female": []}
    with path.open(encoding="utf-8", newline="") as src:
        for row in csv.DictReader(src):
            sex_code = float(row[args.sex])
            if sex_code not in (args.male, args.female):
                raise ValueError(f"Unmapped sex code {sex_code}")
            groups["male" if sex_code == args.male else "female"].append((
                float(row[args.fev1]) * args.fev1_litre_factor,
                float(row[args.fvc]) * args.fvc_litre_factor,
                float(row[args.age]) if args.age else None))
    s = {k: summarize(v, args.age) for k,v in groups.items()}
    pct = lambda key: 100 * statistics.fmean(v[key] / v["n"] for v in s.values())
    return dict(groups=s, equal_sex_prevalence_pct=pct("screened"),
                equal_sex_near_cutoff_pct=pct("near_cutoff"),
                ratio_equal_sex_means_pct=100 * sum(v['fev1_mean'] for v in s.values())
                                            / sum(v['fvc_mean'] for v in s.values()))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    p.add_argument("output", type=Path)
    for name in ("fev1", "fvc", "sex"):
        p.add_argument("--"+name, required=True)
    for name in ("male", "female"):
        p.add_argument("--"+name, type=float, required=True)
    p.add_argument("--age")
    p.add_argument("--fev1-litre-factor", type=float, required=True)
    p.add_argument("--fvc-litre-factor", type=float, required=True)
    args = p.parse_args()
    if args.male == args.female:
        raise ValueError("Ambiguous sex assignment")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    out = {"normalization": {k:v for k,v in vars(args).items() if k not in ("manifest","output")},
           "manifest_sha256": digest(args.manifest), "runs":[]}
    for run in manifest["runs"]:
        result = {k:run[k] for k in ('scenario','seed','status')}
        if run["status"] == "success":
            table = Path(run["table"])
            result['sha256'] = digest(table)
            if result['sha256'] != run['sha256']:
                raise ValueError("Table bytes no longer match final manifest")
            result.update(independently_recompute(table, args))
        out["runs"].append(result)
    with args.output.open('x', encoding="utf-8") as fp:
        json.dump(out, fp, indent=2, allow_nan=False)


if __name__ == "__main__":
    main()

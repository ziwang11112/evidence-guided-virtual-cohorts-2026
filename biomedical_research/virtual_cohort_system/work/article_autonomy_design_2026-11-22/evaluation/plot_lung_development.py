"""Plot the frozen virtual support and its independent source replay."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text(encoding="utf8"))
manifest = read(ROOT / "private/d02/final_manifest.json")
audit = read(ROOT / "LUNG_INDEPENDENT_RESULTS.json")
mapping = read(ROOT / "evaluation/lung_d02_mapping.json")
paths = [Path(r["table"]) for r in manifest["runs"]]
for run, table in zip(manifest["runs"], paths):
    if hashlib.sha256(table.read_bytes()).hexdigest() != run["sha256"]:
        raise ValueError("Frozen table hash mismatch")


def support(path):
    df = pd.read_csv(path, float_precision="round_trip")
    fields = [mapping["sex"]["column"], mapping["volumes"]["fvc_l"]["column"],
              mapping["volumes"]["fev1_l"]["column"]]
    return df.groupby(fields).size().sort_index()


s = support(paths[0])
if any(not support(path).equals(s) for path in paths[1:]):
    raise ValueError("This display requires identical support across all seeds")
ref = audit["tables"][0]["independent"]
codes = {float(k): v for k,v in mapping["sex"]["codes"].items()}
blue, amber, ink, quiet = "#3569A1", "#AE5424", "#192B40", "#596574"
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10, "text.color":ink,
                     "axes.labelcolor":ink, "xtick.color":quiet, "ytick.color":quiet,
                     "axes.spines.top":False,"axes.spines.right":False,"figure.facecolor":"white"})
fig = plt.figure(figsize=(9.2, 4.25), layout="constrained")
grid = fig.add_gridspec(1,2,width_ratios=[1.15,1.0],wspace=.12)
ax = fig.add_subplot(grid[0,0])
xx = np.array([1.8,6.0])
ax.plot(xx,.70*xx, "--", lw=1.1, color=quiet, zorder=1)
for (code, x,y), count in s.items():
    group = codes[code]
    ax.scatter(x,y,marker="o" if group=="F" else "s", color=blue if group=="F" else amber,
               s=70,linewidth=.8,edgecolors="white",zorder=2)
ax.set(xlim=(1.8,6.0), ylim=(1.05,5.0), xlabel="FVC (L)", ylabel="FEV1 (L)")
ax.set_title("A   Eight distinct measurement profiles",loc="left",fontweight="bold",fontsize=12,pad=12)
ax.grid(axis="y",color="#E6EAF0",zorder=0)
legend = [Line2D([],[], linestyle="",marker=m,color=c,label=l) for m,c,l in
          (("o",blue,"Women"),("s",amber,"Men"))]
legend.append(Line2D([],[],linestyle="--",color=quiet,label="FEV1/FVC = 0.70"))
ax.legend(handles=legend,frameon=False,loc="upper left",fontsize=9)
ax2 = fig.add_subplot(grid[0,1])
ax2.set_title("B   Agreement at published precision",loc="left",fontweight="bold",fontsize=12,pad=12)
ax2.set(xlim=(0,4.4),ylim=(-.72,9.2))
ax2.axis("off")
fields = [("Mean FEV1","fev1_mean_l"),("SD of FEV1","fev1_sd_l"),
          ("Mean FVC","fvc_mean_l"),("SD of FVC","fvc_sd_l"),
          ("Pearson correlation","pearson_r"),("Regression slope","ols_slope"),
          ("Regression intercept","ols_intercept_l"),("R-squared","r_squared_pct")]
for pos,name in ((2.85,"Women"),(3.85,"Men")):
    ax2.text(pos,8.65,name,ha="center",fontweight="bold",fontsize=10)
for i,(label,key) in enumerate(fields):
    y=7.75-i
    ax2.text(.04,y,label,va="center")
    for pos,sex in ((2.85,"F"),(3.85,"M")):
        passed = ref["sex"][sex]["source_replay"][key]["inside_printed_rounding_bin"]
        ax2.scatter(pos,y,marker="o" if passed else "x",s=47,c=blue if passed else amber,lw=1.6)
ax2.text(.04,-.28,"●  Within rounding interval",color=blue,fontsize=9)
ax2.text(2.55,-.28,"×  Outside interval",color=amber,fontsize=9)
fig.savefig(ROOT / "LUNG_DEVELOPMENT.png", dpi=210, bbox_inches="tight")
plt.close(fig)

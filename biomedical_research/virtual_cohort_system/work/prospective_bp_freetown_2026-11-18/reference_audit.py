"""Post-reveal provenance check for the two published target columns. Aggregates only."""
import json
from pathlib import Path
import numpy as np
import openpyxl

root = Path(__file__).resolve().parent
assert (root/"VERIFICATION.json").is_file()
files = json.loads((root/"ADMISSION.json").read_text())["files"]
book = openpyxl.load_workbook(root/"private_reference"/files[0]["name"],read_only=True,data_only=False)
rows=book["Mastersheet"].values
h=list(next(rows))
idx=[h.index(k) for k in ["V8_A_Cats","V6_PS","V6_PD"]]
samples={"entire_release":[],"eligible":[]}
formulas=0
for row in rows:
    age,s,d=(row[i] for i in idx)
    if any(isinstance(v,str) and v.startswith("=") for v in [s,d]):
        formulas+=1
        continue
    if s is None or d is None:
        continue
    samples["entire_release"].append((s,d))
    if age in (2,3,4):
        samples["eligible"].append((s,d))
book.close()
out={}
for name,points in samples.items():
    a=np.asarray(points,dtype=float)
    sh,dh=a[:,0]>=140,a[:,1]>=90
    out[name]={"rows":len(a),"neither":int((~sh&~dh).sum()),"systolic_only":int((sh&~dh).sum()),
               "diastolic_only":int((~sh&dh).sum()),"both":int((sh&dh).sum()),
               "unique_pressure_pairs":len(set(points)),"all_integer_mmHg":bool(np.all(a==np.floor(a)))}
receipt={"timing":"post-reveal audit prompted by the size of the discrepancy; primary estimates and rules unchanged",
         "scope":"Release v8 published component pressure fields; aggregate cross-tabulation",
         "counts":out,"formula_cells_in_pressure_columns":formulas,
         "source_of_case":"Same 1,244 people and same event as frozen analysis; whole release shown only as a data-quality diagnostic",
         "interpretation":"No discordant records at the two cutoffs. Codebook labels both pressure columns as added. How individual reading pairs were assembled in this release is unresolved."}
with (root/"REFERENCE_AUDIT.json").open("x",encoding="utf8") as f:
    json.dump(receipt,f,indent=2)

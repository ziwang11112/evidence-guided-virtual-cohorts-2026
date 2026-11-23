import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from compare import analyze_run, compare, digest


def save(path, value):
    path.write_text(json.dumps(value),encoding="utf8")


def fixture(root, offset=0., use_mm=False):
    root.mkdir(parents=True)
    columns=["oct_read","us_read"]
    unit="mm" if use_mm else "µm"
    factor=1000 if use_mm else 1
    candidate={"model_spec":{"columns":[{"name":c,"unit":unit} for c in columns],
               "alternatives":[]},"generator_py":"fixture","decision_record":{"parameter_provenance":[]}}
    review={"action":"keep","reason":"Fixture only"}
    save(root/"build.json",candidate)
    save(root/"review.json",review)
    save(root/"source_inventory.json",{"evidence_checks":[]})
    table=root/"execution_final"/"s0_1"/"generated.csv"
    table.parent.mkdir(parents=True)
    body="row_id,oct_read,us_read\n"+ "".join(
        f"{i},{(x+offset)/factor},{(y+offset)/factor}\n"
        for i,(x,y) in enumerate([(499,520),(500,520),(501,520),(521,500)]))
    table.write_bytes(body.encode())
    manifest={"action":"keep","review_sha256":digest(review),"candidate_sha256":digest(candidate),
              "n":4,"seeds":[1],"status":"success","runs":[
              {"scenario":"primary","seed":1,"status":"success","table":str(table),"n":4,
               "sha256":sha256(table.read_bytes()).hexdigest()}]}
    save(root/"final_manifest.json",manifest)
    return table


class ComparisonTest(unittest.TestCase):
    def test_offset_change_and_boundaries_from_real_columns(self):
        with TemporaryDirectory() as tmp:
            a,b=Path(tmp)/"a",Path(tmp)/"b"
            fixture(a)
            fixture(b,offset=2,use_mm=True)
            pair=("oct_read","us_read")
            result=compare(a,b,pair,pair)
            row=result["old"]["runs"][0]["science"]
            self.assertEqual(row["abs_gt20_pct"],50)
            self.assertEqual(row["abs_equal20_n"],1)
            shift=result["matched_scenario_seeds"][0]
            self.assertAlmostEqual(shift["absolute_error_reduction_um"]["oct_mean_um"],2)
            self.assertAlmostEqual(shift["absolute_error_reduction_um"]["mean_difference_um"],0)
            self.assertAlmostEqual(shift["threshold_change_pp"],0)
            self.assertIsNone(result["measured_abs_gt20_reference_pct"])
            different=compare(a,b,pair,pair,new_instrument="RTVue")
            self.assertFalse(different["same_instrument"])
            self.assertEqual(different["matched_scenario_seeds"],[])

    def test_modified_table_refused(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/"a"
            table=fixture(root)
            with table.open("ab") as f:
                f.write(b"\n")
            with self.assertRaisesRegex(ValueError,"receipt"):
                analyze_run(root,"oct_read","us_read")

    def test_missing_draw_does_not_pass_complete_manifest(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/"a"
            fixture(root)
            m=json.loads((root/"final_manifest.json").read_text())
            m["seeds"].append(2)
            save(root/"final_manifest.json",m)
            with self.assertRaisesRegex(ValueError,"every registered seed"):
                analyze_run(root,"oct_read","us_read")

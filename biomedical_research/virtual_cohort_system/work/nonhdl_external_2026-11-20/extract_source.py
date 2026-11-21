"""Extract the fixed urban stratum and raw estimands from the source article's published XML tables."""
import json
import re
from lxml import etree
from catalogue import HERE, PRIVATE, words, fetch

def main():
    path=PRIVATE/"source.xml"
    raw=fetch("https://journals.plos.org/plosone/article/file?type=manuscript&id=10.1371/journal.pone.0223189",path)
    doc=etree.fromstring(raw)
    selection=[
        ("tc_mean",2,"TC (mmol/L)","mmol/L"),("hdl_mean",2,"HDL-C (mmol/L)","mmol/L"),
        ("mean_individual_ratio",2,"TC/HDL-C ratio","dimensionless"),
        ("nonhdl_mean",2,"Non HDL cholesterol","mmol/L"),
        ("tc_high_pct",3,"High TC (≥6.2 mmol/L)","percent"),("hdl_low_pct",3,"Low HDL-C (<1 mmol/L)","percent")]
    result={"article":"Kavishe et al., PLOS ONE 2019, doi:10.1371/journal.pone.0223189",
            "stratum":"First municipality in Table 2: Mwanza, Tanzania, 170 community adults aged 18+; multistage survey 2012–13. Nonfasting venous serum. Design-weighted estimates. The reported intervals describe source estimates and are not individual standard deviations.",
            "joint_operator":"Mean of individual TC/HDL ratios with source survey weights. The paper uses mmol/L for both quantities.",
            "cholesterol_mg_dl_per_mmol_l":38.67}
    for key,tno,label,units in selection:
        table=doc.xpath(f"//table-wrap[label='Table {tno}']")[0]
        rows=[[words(c) for c in tr.xpath("./th|./td")] for tr in table.xpath(".//tr")]
        first=next(i for i,row in enumerate(rows) if row[0]=="TANZANIA")
        last=next(i for i,row in enumerate(rows) if row[0]=="UGANDA")
        assert "Mwanza municipality (n = 170)" in rows[first][1]
        row,=[row for row in rows[first+1:last] if row[0]==label]
        nums=[float(n) for n in re.findall(r"\d+(?:\.\d+)?",row[1])]
        assert len(nums)==3 and nums[1]<=nums[0]<=nums[2]
        result[key]={"estimate":nums[0],"source_ci":nums[1:],"unit":units,"table":tno,"row":label}
    dest=HERE/"SOURCE.json"
    if dest.exists(): assert json.loads(dest.read_text(encoding="utf8"))==result
    else: dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

if __name__=="__main__":
    main()

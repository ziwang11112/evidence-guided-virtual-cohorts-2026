"""Validate frozen-analysis candidates exclusively on invented data."""
from __future__ import annotations
import json,pathlib,tempfile
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import survey_analysis as sa
import evaluate_committed as ec
HERE=pathlib.Path(__file__).resolve().parent
def main():
    validation=sa.validate_invented(); rows=[]
    for age in [45,65]:
        for sex in [1,2]:
            for bmi in [22,27,33]:
                for st in [1,2,3]:
                    for psu in [1,2]:
                        for replicate in [0,1]:
                            i=len(rows); rows.append({'record_id':str(i),'RIDAGEYR':age+replicate,'RIAGENDR':sex,'BMXBMI':bmi+.2*replicate,'SDMVSTRA':st,'SDMVPSU':psu,'WTSAF2YR':float(1+st+replicate),'eligible':1})
    full=pd.DataFrame(rows)
    # Assign via arrays to avoid unintended pandas index alignment.
    tg=pd.Series((100+full.RIDAGEYR*.2+full.BMXBMI*.6+full.RIAGENDR*2+full.SDMVPSU*3).to_numpy(),index=full.record_id)
    result=sa.evaluate(full,tg); assert len(result)==67
    assert all('estimate' in r and np.isfinite(r['estimate']) for r in result.values())
    assert result['ordered_age40_59_sex1_arithmetic_middle_minus_low']['estimate']>0
    key='cell_age40_59_sex1_bmi0_arithmetic'; mask=(full.RIDAGEYR<60)&(full.RIAGENDR==1)&(full.BMXBMI<25)
    manual=np.average(tg.reindex(full.loc[mask,'record_id']),weights=full.loc[mask,'WTSAF2YR'])
    assert np.allclose(result[key]['estimate'],manual)
    generated=sa.evaluate(full,tg,reference=False); assert all('se' not in r and 'ci_low' not in r for r in generated.values())
    # Empty cell retained, instead of dropping a prespecified subgroup.
    reduced=full.copy(); reduced.loc[mask,'eligible']=0
    empty=sa.evaluate(reduced,tg); assert empty[key]['status']=='nonestimable'
    # Authorization rejection occurs without any CSV load.
    old=ec.pd.read_csv
    def forbidden(*args,**kwargs): raise RuntimeError('Unexpected participant-table load')
    ec.pd.read_csv=forbidden
    try:
        with tempfile.TemporaryDirectory(prefix='m7_guard_',dir=HERE) as folder:
            p=pathlib.Path(folder)/'deny.json'; p.write_text(json.dumps({'authorize_target_evaluation':False}))
            try: ec.verify_preload(p)
            except ValueError as exc: assert 'authorization' in str(exc)
            else: raise AssertionError('Unauthorized gate passed')
    finally: ec.pd.read_csv=old
    out={'validated_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','scope':'invented_data_and_gate_rejection_only','target_outcomes_analyzed':False,'baseline':validation,'additional_checks':['joint group contrast equals direct influence variance','all 67 fixed endpoints emitted on complete invented grid','arithmetic subgroup mean equals direct weighted mean','generated summaries contain no survey uncertainty','empty subgroup retained as nonestimable','authorization-false rejected before any participant CSV load'],'independent_survey_package_validation':False}
    (HERE/'method_validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'passed','scope':out['scope'],'endpoints':len(result),'target_outcomes_analyzed':False}))
if __name__=='__main__': main()

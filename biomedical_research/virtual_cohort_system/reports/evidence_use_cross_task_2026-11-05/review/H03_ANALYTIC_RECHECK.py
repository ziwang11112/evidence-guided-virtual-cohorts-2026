"""Independent deterministic audit of author H03's proposed moment equations.
No sampling, generator import, clinical data or parameter recommendation.
"""
from pathlib import Path
import json, math
from statistics import NormalDist
import numpy as np

ages=np.concatenate([np.arange(lo,hi+1) for lo,hi in [(25,39),(40,54),(55,69),(70,79)]])
w=np.concatenate([np.repeat(.25/(hi-lo+1),hi-lo+1) for lo,hi in [(25,39),(40,54),(55,69),(70,79)]])
ma=float(w@ages); va=float(w@((ages-ma)**2)); vb=3.8**2; vf=.25
ga=.2; gb=.024*18; gf=-.2472*18; a=.010; b=.0125; f=.023; mg=91.2; vg=12.4**2
vm=ga*ga*va+gb*gb*vb+gf*gf*vf
eg=vg-vm
k=(126*mg-mg*mg-vm)/eg-1
mr=mg+ga*(52-ma); vr=2.
vmr=ga*ga*vr+gb*gb*vb+gf*gf*vf
egr=(126*mr-mr*mr-vmr)/(k+1)
refvar=((6-5.4)/NormalDist().inv_cdf(.975))**2
d0=ga*a*va+gb*b*vb+gf*f*vf
d1=ga*ga*va+eg
v0=refvar+a*a*(va-vr); v1=2*a*ga*(va-vr); v2=ga*ga*(va-vr)+eg-egr
r=.23
roots=np.roots([d1*d1-r*r*vg*v2,2*d0*d1-r*r*vg*v1,d0*d0-r*r*vg*v0])
accepted=[]
for c in roots:
    vh=v0+v1*c+v2*c*c
    signed=(d0+d1*c)/math.sqrt(vg*vh)
    if abs(signed-r)<1e-12: accepted.append(float(c))
assert len(accepted)==1
c=accepted[0]
s2=refvar-(a+c*ga)**2*vr-b*b*vb-f*f*vf-c*c*egr
assert k>0 and s2>0
expected=json.loads(Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcUseH03/PROPOSAL_ALGEBRA.json').read_text())
actual={'age_mean':ma,'age_variance':va,'glucose_beta_concentration':k,
        'glucose_mean_reference_age52':mr,'hba1c_glucose_coefficient':c,
        'hba1c_bmi_coefficient':b-c*gb,'hba1c_female_coefficient':f-c*gf,
        'hba1c_conditional_variance':s2,'implied_marginal_hba1c_sd':math.sqrt(v0+v1*c+v2*c*c)}
for key,value in actual.items(): assert math.isclose(value,expected[key],abs_tol=1e-11,rel_tol=1e-11),key
record={'scope':'independent scalar moment algebra only; no generated or patient rows',
        'comparisons':len(actual),'status':'pass','actual':actual,
        'signed_equation_selected_roots':accepted,'discarded_squared_root_not_a_sign_preference':True}
out=Path(__file__).with_suffix('.json')
with out.open('x',encoding='utf-8') as handle: json.dump(record,handle,indent=2)
print(json.dumps({'status':'pass','comparisons':len(actual)}))

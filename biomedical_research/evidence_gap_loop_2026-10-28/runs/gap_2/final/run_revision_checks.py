"""Additional review-triggered source/invented checks; run after run_artificial_checks.py."""
import hashlib
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
spec=json.loads((HERE/'model_spec.json').read_text(encoding='utf-8'))
evidence=json.loads((HERE/'evidence.json').read_text(encoding='utf-8'))
checks=json.loads((HERE/'artificial_checks.json').read_text(encoding='utf-8'))
ms=importlib.util.spec_from_file_location('final_gap2_generator',HERE/'generator.py')
gen=importlib.util.module_from_spec(ms)
ms.loader.exec_module(gen)

age=next(x['reported'] for x in evidence['evidence'] if x['id']=='E_TW_AGE_BY_BMI')
tw_xml=ROOT/'literature/approved/23728f05bcc689d1e4d9549f25d163243c4dd6b3a174225f34a7758c1514eaa8.xml'
root=ET.parse(tw_xml).getroot()
tables={''.join(t.find('label').itertext()):t for t in root.findall('.//table-wrap') if t.find('label') is not None}
rows={}
for tr in tables['Table 5'].findall('.//tr'):
    cells=[''.join(x.itertext()).strip() for x in list(tr) if x.tag in ['td','th']]
    if cells and cells[0] in ['40\u201350','51\u201360','61\u201370']:
        rows[cells[0]]=cells
for j,label in enumerate(['40\u201350','51\u201360','61\u201370'],start=1):
    for k in range(4):
        extracted=float(rows[label][1+2*k].replace('\u2212','-'))
        assert abs(extracted-age['contrasts_mg_dl_by_bmi'][k][j])<1e-12

pooled=np.array(spec['parameters']['age_effect_mg_dl'])
age_comparison=[]
for k,name in enumerate(age['bmi_categories']):
    stratified=np.array(age['contrasts_mg_dl_by_bmi'][k])
    age_comparison.append({'bmi_category':name,'n':age['n_bmi'][k],'n_by_age':age['n_age_by_bmi'][k],
        'pooled_age_contrasts_mg_dl':pooled.tolist(),
        'stratum_age_contrasts_mg_dl':stratified.tolist(),
        'stratified_minus_pooled_mg_dl':(stratified-pooled).tolist(),
        'qualification':'Differences of reported point estimates under richer adjustment; no formal interaction test/covariance supplied.'})

weights=np.array([4112,4087,4141,2197],dtype=float)
weights/=weights.sum()
center=float(weights@pooled)
age_variance=float(weights@((pooled-center)**2))
variance_diagnostic=[]
for sex,sd_values in spec['parameters']['sd_hdl_by_sex'].items():
    for k,sd in enumerate(sd_values):
        variance_diagnostic.append({'sex':int(sex),'BMI_assumed_representative':spec['parameters']['bmi_anchor_kg_m2'][k],
            'reported_cell_SD_proxy':sd,'added_between_age_variance_under_assumed_midpoint_mixture':age_variance,
            'model_marginal_SD_under_same_assumed_mixture':float(np.sqrt(sd**2+age_variance))})

tr=next(x['reported'] for x in evidence['evidence'] if x['id']=='E_TUR_OBESITY_CLASSES')
tur_xml=ET.parse(ROOT/'literature/approved/765766b336a0dee9b8ed92251cc725b827fe94184396f59032703d216a5f1c38.xml').getroot()
tur_table=next(t for t in tur_xml.findall('.//table-wrap') if t.find('label') is not None and ''.join(t.find('label').itertext())=='Table 1')
tur_rows=[]
for rr in tur_table.findall('.//tr'):
    cells=[''.join(c.itertext()).strip() for c in list(rr) if c.tag in ['td','th']]
    if cells and cells[0] in ['Obese class I','Obese class II','Obese class III']:
        tur_rows.append(cells)
for k,rr in enumerate(tur_rows):
    # This table embeds its comparison p-value within each value cell.
    assert float(rr[2].split('\u00b1')[0].strip())==tr['mean_bmi'][k]
    assert float(rr[5].split('\u00b1')[0].strip())==tr['mean_hdl_mg_dl'][k]
assert len(tur_rows)==3
source_contrast=float(tr['mean_hdl_mg_dl'][2]-tr['mean_hdl_mg_dl'][0])
plugin=[]
for sex in [1,2]:
    toy=pd.DataFrame({'row_id':['classI','classII','classIII'],
      'bmi':tr['mean_bmi'],'age':tr['mean_age'],'sex':[sex]*3})
    means,sd=gen.conditional_moments(toy,spec)
    # Same mean ages and fixed sex are retained for the flat countermodel.
    age_effect=np.interp(toy.age,spec['parameters']['age_knots_years'],pooled)-center
    flat=np.array(age_effect)+spec['parameters']['mean_hdl_by_sex'][str(sex)][-1]
    plugin.append({'sex':sex,'reported_mean_bmi':tr['mean_bmi'],'reported_mean_age':tr['mean_age'],
     'selected_plugin_means':means.tolist(),'selected_classIII_minus_I':float(means[2]-means[0]),
     'flat_classIII_minus_I':float(flat[2]-flat[0])})

registry=set()
for line in (ROOT/'literature/audit.jsonl').read_text(encoding='utf-8').splitlines():
    entry=json.loads(line)
    if entry.get('type')=='artifact_approved' and entry.get('status')=='accepted':
        a=entry['artifact']
        registry.add(('literature/'+a['session_relative_path'],a['sha256']))
references=[]
for source in evidence['sources']: references.extend(source['approved_artifacts'])
actions=json.loads((HERE/'actions.json').read_text(encoding='utf-8'))
for action in actions: references.extend(action['evidence_artifacts'])
for a in references:
    assert (a['path'],a['sha256']) in registry
    assert hashlib.sha256((ROOT/a['path']).read_bytes()).hexdigest()==a['sha256']

gaps=json.loads((HERE/'gaps.json').read_text(encoding='utf-8'))
for g in gaps:
    assert g['status']!='open' and g['resolution']
    assert any(a['gap_id']==g['id'] and a['phase']=='revision' for a in actions)
retention={}
for filename in ['generator.py','model_spec.json']:
    i=hashlib.sha256((ROOT/'initial'/filename).read_bytes()).hexdigest()
    f=hashlib.sha256((HERE/filename).read_bytes()).hexdigest()
    assert i==f
    retention[filename]={'sha256':f,'initial_final_identical':True}
checks['revision_checks']={
 'scope':'Re-extraction, numerical accounting and invented-point source comparison only; not target evaluation.',
 'taiwan_age_rows_match_approved_XML':True,
 'age_modifier_sensitivity':age_comparison,
 'variance_accounting':{'between_age_variance':age_variance,'cells':variance_diagnostic,
   'qualification':'This hypothetical source-midpoint mixture demonstrates that adding age variation also adds marginal variance. It does not use or reconstruct actual within-cell covariances. No residual subtraction is justified or performed.'},
 'turkish_primary_class_means_match_approved_XML':True,
 'turkish_obesity_contrast':{'published_classIII_minus_I_mg_dl':source_contrast,'n_classI':10,'n_classIII':22,
   'plugin_model_comparisons':plugin,
   'exact_source_operator':'Cannot compute: source class-specific sex mix and joint age/BMI distribution absent. Plug-in numbers only illustrate scale; they are not source fit or calibration.'},
 'all_source_action_references_registered_and_hash_verified':True,
 'reference_count_including_repeated_references':len(references),
 'all_final_gaps_nonopen_with_revision_actions':True,
 'exact_numerical_retention':retention,
 'no_target_validation':True}
(HERE/'artificial_checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','max_age_contrast_difference_mg_dl':float(np.max(np.abs(np.array(age['contrasts_mg_dl_by_bmi'])-pooled))),
 'between_age_variance':age_variance,'source_obesity_contrast':source_contrast,'plugin_comparisons':plugin,'registration_references':len(references),'exact_numerical_retention':retention},indent=2))

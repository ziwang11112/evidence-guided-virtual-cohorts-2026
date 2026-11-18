"""Second arithmetic check of saved aggregates, not an external scientific review.

Uses decimal arithmetic and independent direct-source lookups. It does not import
analyze_use, read participant rows, execute generators or rerun the old analyses.
"""
from pathlib import Path
from collections import defaultdict, Counter
from decimal import Decimal, getcontext
import csv, json, hashlib

getcontext().prec = 35
W = Path(__file__).resolve().parent
P = W.parents[1]
D = Decimal

def rows(path):
    with path.open(encoding='utf8', newline='') as f:
        return list(csv.DictReader(f))

def js(path):
    return json.loads(path.read_text(encoding='utf8'))

ledger = rows(W/'ESTIMATE_LEDGER.csv')
profiles = rows(W/'ANALYSIS_USE_PROFILE.csv')
assert len(ledger) == 222 and len(profiles) == 32
assert Counter(r['study'] for r in ledger) == {
    'Lifestyle':54, 'PNS':90, 'ENSANUT':60, 'Iron':18}
key = lambda r:(r['study'], r['arm'], r['analysis'], r['author'], r['seed'])
assert len({key(r) for r in ledger}) == len(ledger)

# Confirm every extracted value against the originating aggregate, rather than
# only comparing a derived profile with the new ledger that produced it.
source_lifestyle = rows(P/'work/lifestyle_application_2026-11-11/ANALYSIS_CONTRASTS.csv')
lidx = {(r['dataset_id'], r['trait']+':'+r['contrast']):r
        for r in source_lifestyle if r['stratum']=='pooled'}
source_pns = js(P/'work/pns_joint_evidence_2026-11-16/analysis/seed_results.json')
pidx = {(r['arm'],r['id'],str(r['seed']),r['estimand']):r for r in source_pns}
source_ens = js(P/'work/scientific_use_review_v30_2026-11-11/NUMERICAL_USE_AUDIT.json')
eidx = {(r['author'],r['analysis_id']):r for r in source_ens['summary_records']
        if r['study']=='Q4 ENSANUT'}
source_iron = js(P/'work/analysis_use_diagnosis_2026-11-08/IRON_LIPID_AUDIT.json')
iidx = {r['id']:r['observed_result'] for r in source_iron['analyses'][:3]}
source_checks = 0
for r in ledger:
    if r['study']=='Lifestyle':
        candidates = [v for (dataset,a),v in lidx.items()
            if a==r['analysis'] and dataset!='real'
            and f"_{r['author']}_" in dataset and dataset.endswith('s'+r['seed'])]
        assert len(candidates)==1
        value, ref = candidates[0]['raw_estimate'], lidx['real',r['analysis']]['raw_estimate']
    elif r['study']=='PNS':
        s=pidx[r['arm'],r['author'],r['seed'],r['analysis']]
        value,ref=s['value'],s['reference']
    elif r['study']=='ENSANUT':
        s=eidx[r['author'],r['analysis']]
        pos=s['seeds'].index(int(r['seed']))
        value,ref=s['values'][pos],s['reference']['value']
    else:
        s=iidx[r['analysis']]
        value=s['authors'][r['author']]['seed_values'][int(r['seed'])-1]
        ref=s['reference']['estimate']
    assert D(r['value'])==D(str(value)) and D(r['reference'])==D(str(ref))
    source_checks+=1

groups=defaultdict(list)
for r in ledger:groups[r['study'],r['arm'],r['analysis']].append(r)
max_roundoff=D(0)
numeric_comparisons=0
for profile in profiles:
    rr=groups[profile['study'],profile['arm'],profile['analysis']]
    vals=[D(r['value']) for r in rr]; ref=D(profile['reference'])
    by_author=defaultdict(list)
    for r in rr:by_author[r['author']].append(D(r['value']))
    assert all(len(v)==3 for v in by_author.values())
    means=[sum(v)/D(len(v)) for v in by_author.values()]
    diffs=[abs(v-ref) for v in vals]
    independently_computed={
        'draw_min':min(vals),'draw_max':max(vals),
        'constructor_mean_min':min(means),'constructor_mean_max':max(means),
        'max_absolute_point_difference':max(diffs),
        'mean_absolute_point_difference':sum(diffs)/D(len(diffs)),
        'max_constructor_mean_point_difference':max(abs(v-ref) for v in means)}
    for field,expected in independently_computed.items():
        delta=abs(D(profile[field])-expected)
        assert delta<D('1e-12'),(profile['analysis'],field,delta)
        max_roundoff=max(max_roundoff,delta);numeric_comparisons+=1
    assert int(profile['n_draws'])==len(vals)
    assert int(profile['n_constructors'])==len(means)
    assert profile['quantitative_acceptance']=='not_assessed_no_use_justified_margin'
    assert profile['generalization']=='not_established'

# Clinically meaningful semantics: null, units, clustering and no false margins.
idx={(r['study'],r['arm'],r['analysis']):r for r in profiles}
assert D(idx['Iron','external-evidence','IRON_OR']['association_null'])==1
assert idx['Iron','external-evidence','IRON_BURDEN']['association_null']==''
assert idx['ENSANUT','external-evidence','hba1c.mean']['unit']=='HbA1c % (NGSP)'
assert idx['ENSANUT','external-evidence','Q1_age10']['unit'].startswith('HbA1c percentage points/')
for arm in ['ORIGINAL','AUGMENTED']:
    assert int(idx['PNS',arm,'residual_correlation']['n_constructors'])==3

patterns=js(W/'PATTERNS.json')
for k in ['lifestyle_urban_above_both_groups','ensanut_positive_bmi_attenuation_after_glucose']:
    assert patterns[k]['tables']==6 and patterns[k]['matching_tables']==6
assert patterns['acceptance_margin_selected'] is False
assert patterns['equivalence_tests_performed']==0
bindings=js(W/'INPUT_BINDINGS.json')['files']
assert all(hashlib.sha256((P/rel).read_bytes()).hexdigest()==sha for rel,sha in bindings.items())
assert len(bindings)==11
review={
    'status':'passed',
    'reviewer':'root; second arithmetic implementation, not a separate human or model reviewer',
    'direct_source_estimate_slots_checked':source_checks,
    'profile_arithmetic_comparisons':numeric_comparisons,
    'max_decimal_vs_float_difference':str(max_roundoff),
    'protected_source_files_unchanged':len(bindings),
    'semantics_checked':['OR null 1','HbA1c concentration versus percentage-point change',
        'constructor versus draw counts','zero retrospective equivalence margins',
        'source-rich and external developmental regimes remain distinct'],
    'patient_data_read':False,'old_experiments_rerun':False,
    'new_resampling_validation_executed':False,
    'scope':'Direct-source aggregate reconciliation and descriptive arithmetic; no claim of new biomedical validation.'}
(W/'NUMERICAL_RECHECK.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf8')
print(json.dumps(review))

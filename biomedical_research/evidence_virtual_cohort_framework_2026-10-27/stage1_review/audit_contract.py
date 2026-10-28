"""Read-only source/contract audit; writes only its review directory.

Never computes reserved correlations, change SDs, tests, or confidence intervals.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import openpyxl

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent / 'stage1'
BIO = HERE.parent.parent

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

checks = []

def check(name, ok, detail=None):
    checks.append(dict(check=name, pass_=bool(ok), detail=detail))

packets = {case: read(STAGE / 'packets' / case / 'evidence.json') for case in ['case_a','case_b','case_c']}
original_ross = read(BIO / 'obesity_paper_replay_2026-10-27' / 'allowed/evidence.json')
check('Ross packet retains exact permitted marginal summaries', packets['case_a']['marginal_summaries'] == original_ross['marginal_summaries'])
original_he = read(BIO / 'obesity_larger_replication_2026-10-25' / 'generator/shared_moments.json')
check('He packet retains exact permitted moments and scales', packets['case_c']['moments'] == original_he)
travers_text = (BIO / 'obesity_public_data_replication_2026-10-25' / 'generator/INPUT.md').read_text(encoding='utf-8')
labels = {'leptin':'Serum leptin','body_mass':'Body mass','glucose':'Fasting glucose','triglycerides':'Fasting triglycerides'}
for key, label in labels.items():
    line = next(x for x in travers_text.splitlines() if x.startswith('| '+label+' |'))
    cells = [x.strip() for x in line.strip('|').split('|')]
    m = packets['case_b']['moments'][key]
    check('Travers permitted packet transcription: '+key, m['unit']==cells[1] and [m[k] for k in ['pre_mean','pre_sd','post_mean','post_sd']]==[float(x) for x in cells[2:]])

# Verify new custodian references against original public source extraction,
# emitting only equality/count results. No reference inferential answers.
book = openpyxl.load_workbook(BIO / 'obesity_public_data_replication_2026-10-25' / 'reference/bath_1350_original.xlsx', data_only=True).active
ref_b = pd.read_csv(STAGE / 'custodian/case_b_reference.csv')
for key,col in {'leptin':'BJ','body_mass':'BP','glucose':'CM','triglycerides':'CQ'}.items():
    for when,rows in [('pre',range(3,15)),('post',range(15,27))]:
        source = [book[f'{col}{r}'].value for r in rows]
        check('Travers original paired column equality: '+key+'_'+when, np.allclose(ref_b[key+'_'+when],source,equal_nan=True))

he = pd.read_excel(BIO / 'obesity_larger_replication_2026-10-25' / 'source_search/pediatric_0357145.xlsx',sheet_name='Paired_Analysis_44')
ref_c = pd.read_csv(STAGE / 'custodian/case_c_reference.csv')
he_prefixes = {'leptin_log10':'Leptin_log10','body_mass':'weight_kg','glucose':'fasting_glucose_mmol_L','triglycerides':'TG_mmol_L'}
for key,prefix in he_prefixes.items():
    for when in ['pre','post']:
        check('He source extraction equality: '+key+'_'+when, np.allclose(ref_c[key+'_'+when],he[prefix+'_'+when],equal_nan=True))
    d=he[[prefix+'_pre',prefix+'_post']].dropna()
    m=packets['case_c']['moments'][key]
    check('He complete-pair n: '+key, len(d)==m['n'])
    for when in ['pre','post']:
        check('He permitted paired-subset marginal moment: '+key+'_'+when,
              round(float(d[prefix+'_'+when].mean()),3)==m[when+'_mean'] and round(float(d[prefix+'_'+when].std(ddof=1)),3)==m[when+'_sd'])
check('He leptin analysis scale equals source log10',
      np.allclose(np.log10(he.Leptin_pg_mL_pre),he.Leptin_log10_pre) and np.allclose(np.log10(he.Leptin_pg_mL_post),he.Leptin_log10_post))

ross = pd.read_excel(BIO / 'obesity_paper_replay_2026-10-27' / 'source/ross2020_s1.xlsx')
names = {'ID':'person_id','Assessment Time':'month','Weight (kg)':'weight_kg','Power of Food Scale: Total Score':'pfs','No-Go Errors (Go/No-Go)':'gng','Delay Discounting Area Under the Curve ($100 condition)':'dd100','Delay Discounting Area Under the Curve ($1000 condition)':'dd1000'}
ross=ross[list(names)].rename(columns=names)
ross=ross.replace('.',np.nan).apply(pd.to_numeric)
mapper={x:i+1 for i,x in enumerate(sorted(ross.person_id.unique()))}
ross.person_id=ross.person_id.map(mapper)
ref_a=pd.read_csv(STAGE / 'custodian/case_a_reference.csv')
check('Ross canonical source extraction equality', list(ref_a)==list(ross) and np.allclose(ref_a.to_numpy(),ross.to_numpy(),equal_nan=True))
check('Ross five visits per person and unique key',len(ref_a)==375 and ref_a.person_id.nunique()==75 and not ref_a.duplicated(['person_id','month']).any() and ref_a.groupby('person_id').month.apply(lambda x: sorted(x)==[0,3,6,9,12]).all())

protocol=read(STAGE/'protocol.json')
check('Stage 1 exact paired-lineage/output budget',protocol['initial_lineages_per_case']==3 and protocol['cohorts_per_branch']==20 and protocol['total_agent_cohorts']==360 and protocol['total_fixed']==60 and protocol['allocation']=={'1':[20],'2':[10,10],'3':[7,7,6]})
registry=read(STAGE/'analysis_registry.json')
inventory=Counter((r['case_id'],r['analysis']) for r in registry)
check('Unique analysis keys',len(registry)==len({(r['case_id'],r['analysis'],r['term']) for r in registry}))
check('Ross 31 replay + 4 proxy inventory',sum(v for (c,a),v in inventory.items() if c=='case_a')==35 and inventory[('case_a','baseline_pearson')]==6 and inventory[('case_a','pooled_standardized_reml')]==4 and sum(v for (c,a),v in inventory.items() if c=='case_a' and a.endswith('_time_reml'))==25)
for case in ['case_b','case_c']:
    check(case+' four paired changes plus six delta correlations',inventory[(case,'paired_change')]==4 and inventory[(case,'change_pearson')]==6)
staged=[p for p in (STAGE/'runs').glob('*/build_*/initial_*') if not (p/'RETIRED.json').exists()]
check('Nine active initial staged contexts',len(staged)==9)
for run in staged:
    case=read(run/'task.json')['case_id']
    for f in ['evidence.json','schema.json']:
        check(str(run.relative_to(STAGE))+'/'+f+' matches packet',sha(run/f)==sha(STAGE/'packets'/case/f))
freeze=read(STAGE/'protocol_freeze.json')
check('Protocol freeze file hashes',all((STAGE/p).exists() and sha(STAGE/p)==h for p,h in freeze['files'].items()))

result=dict(audited_utc=datetime.now(timezone.utc).isoformat(),scope='Read-only source, permitted marginal, registry and frozen-file consistency; no reserved inferential computation',protocol_freeze_sha256=sha(STAGE/'protocol_freeze.json'),files_reviewed_sha256={str(p.relative_to(STAGE)):sha(p) for p in [STAGE/'protocol.json',STAGE/'analysis_registry.json',STAGE/'runner.py',STAGE/'source_checks.py',STAGE/'fixed_generator.py']},checks=checks,all_checks_pass=all(c['pass_'] for c in checks),analysis_inventory={f'{c}/{a}':v for (c,a),v in inventory.items()})
output=HERE/f"source_contract_checks_{protocol['version']}.json"
output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(dict(all_checks_pass=result['all_checks_pass'],checks=len(checks),failed=[c for c in checks if not c['pass_']],analysis_inventory=result['analysis_inventory']),indent=2))

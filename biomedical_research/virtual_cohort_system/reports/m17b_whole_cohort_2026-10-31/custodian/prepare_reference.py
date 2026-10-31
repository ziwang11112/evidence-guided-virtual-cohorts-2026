"""Prepare only the M17-B reference; never computes scientific endpoints.

Run after evaluator sanity, explicit root protocol authorization, and pre-access
freeze. Output contains capacity/integrity only. Actual rows remain private.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]
PROTOCOL=PROJECT/'docs/M17B_WHOLE_COHORT_PROTOCOL.md'
BINS=[20,35,50,65,80]
SEED=17101


def stamp(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def main():
    lockpath=HERE/'pre_access_freeze.json'
    if lockpath.exists(): raise RuntimeError('Pre-access lock already exists; no silent rerun')
    sanity=json.loads((HERE/'evaluator_sanity.json').read_text(encoding='utf-8'))
    if sanity.get('status')!='passed' or not sanity.get('invented_only'):
        raise RuntimeError('Invented-only sanity gate did not pass')
    bindings=[PROTOCOL,HERE/'evaluate_m17b.py',Path(__file__),HERE/'evaluator_sanity.json',
              HERE/'METADATA_ADMISSION.md',HERE/'EXPOSURE_AUDIT.md']
    lock={'created_utc':stamp(),'phase':'before_any_2007_2008_participant_download',
          'root_authorization':'Root message: protocol written; evaluator lock and invented sanity before download; no endpoint analysis before final output release.',
          'files':[{'path':str(p),'sha256':sha(p)} for p in bindings],
          'selection':{'seed':SEED,'rng':'numpy.random.default_rng / PCG64',
             'sort_before_sampling':'ascending numeric SEQN within cell',
             'cell_order':'female=0 then female=1; ascending age bins [20,35,50,65,80)',
             'sample':'rng.choice(cell length, size=40, replace=False); selected positions sorted for output',
             'eligibility':'Age >=20 and <80, RIAGENDR in {1,2}, finite positive BMXBMI, finite nonnegative LBXSUA',
             'no_extra_exclusions':True,'shortage_rule':'stop, no outcome statistics, no altered quotas'},
          'software':{'python':platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','pandas','pyreadstat','requests']}}}
    write(lockpath,lock)
    private=HERE/'private'
    raw=private/'raw'
    raw.mkdir(parents=True,exist_ok=False)
    download=[]
    for component in ['DEMO_E','BMX_E','BIOPRO_E']:
        url=f'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/{component}.xpt'
        response=requests.get(url,timeout=90)
        response.raise_for_status()
        data=response.content
        if not data.startswith(b'HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!'):
            raise ValueError(f'{component}: response is not SAS XPORT')
        path=raw/f'{component}.xpt'
        path.write_bytes(data)
        download.append({'component':component,'url':url,'resolved_url':response.url,'retrieved_utc':stamp(),
                         'path':str(path),'bytes':len(data),'sha256':sha(path),'http_status':response.status_code})
        write(private/'download_manifest.json',download)
    # pyreadstat was chosen prospectively because earlier project checks identified
    # a pandas SAS XPORT zero-decoding defect. No pandas.read_sas fallback.
    parts={}
    columns={'DEMO_E':['SEQN','RIDAGEYR','RIAGENDR'],
             'BMX_E':['SEQN','BMXBMI'],'BIOPRO_E':['SEQN','LBXSUA']}
    for component in columns:
        frame,meta=pyreadstat.read_xport(str(raw/f'{component}.xpt'),usecols=columns[component])
        if frame.SEQN.isna().any() or frame.SEQN.duplicated().any():
            raise ValueError(f'{component}: invalid join identifiers')
        parts[component]=frame
    merged=parts['DEMO_E'].merge(parts['BMX_E'],on='SEQN',how='inner',validate='one_to_one').merge(
        parts['BIOPRO_E'],on='SEQN',how='inner',validate='one_to_one')
    numeric=merged[['RIDAGEYR','RIAGENDR','BMXBMI','LBXSUA']].to_numpy(float)
    mask=np.isfinite(numeric).all(axis=1)&merged.RIDAGEYR.between(20,80,inclusive='left')&merged.RIAGENDR.isin([1,2])&(merged.BMXBMI>0)&(merged.LBXSUA>=0)
    eligible=merged.loc[mask].copy()
    eligible['female']=(eligible.RIAGENDR==2).astype(int)
    capacity=[]; cells=[]
    for female in [0,1]:
        for lo,hi in zip(BINS[:-1],BINS[1:]):
            cell=eligible[(eligible.female==female)&eligible.RIDAGEYR.between(lo,hi,inclusive='left')].sort_values('SEQN')
            cells.append(cell)
            capacity.append({'female':female,'age_lo':lo,'age_hi_exclusive':hi,'eligible_n':len(cell),'required_n':40})
    feasibility={'status':'feasible' if all(c['eligible_n']>=40 for c in capacity) else 'failed_capacity',
                 'created_utc':stamp(),'cycle':'2007-2008','cells':capacity,'total_eligible':len(eligible),
                 'pre_access_freeze_sha256':sha(lockpath),'protocol_sha256':sha(PROTOCOL),
                 'evaluator_sha256':sha(HERE/'evaluate_m17b.py'),
                 'raw_source_hashes':{d['component']:d['sha256'] for d in download},
                 'scientific_endpoint_values_computed':False,
                 'scientific_endpoint_values_revealed':False}
    write(HERE/'feasibility.json',feasibility)
    if feasibility['status']!='feasible':
        print(json.dumps(feasibility)); return
    rng=np.random.default_rng(SEED)
    selected=[]
    for cell in cells:
        selected.append(cell.iloc[np.sort(rng.choice(len(cell),size=40,replace=False))])
    selected=pd.concat(selected,ignore_index=True)
    output=pd.DataFrame({'sample_id':[f'm17b_ref_{i+1:04d}' for i in range(len(selected))],
                         'age':selected.RIDAGEYR.astype(int),'female':selected.female,
                         'bmi':selected.BMXBMI,'urate':selected.LBXSUA})
    target=private/'reference.csv'
    output.to_csv(target,index=False)
    mapping=pd.DataFrame({'sample_id':output.sample_id,'SEQN':selected.SEQN.astype(int)})
    mapping.to_csv(private/'selection_ids.csv',index=False)
    # Validate shape, quotas, domains only; no scientific regression or moments.
    from evaluate_m17b import validate_table
    selected_counts=validate_table(output)
    integrity={'created_utc':stamp(),'phase':'selected_and_sealed_before_scientific_endpoint_analysis',
        'reference':{'path':str(target),'sha256':sha(target),'rows':len(output)},
        'selection_ids_sha256':sha(private/'selection_ids.csv'),'selected_cells':selected_counts,
        'pre_access_freeze_sha256':sha(lockpath),'download_manifest_sha256':sha(private/'download_manifest.json'),
        'scientific_endpoints_computed':False}
    write(HERE/'reference_integrity.json',integrity)
    print(json.dumps({'status':'feasible_selected_sealed','n':len(output),'cells':capacity,
                      'evaluator_ready':True,'scientific_endpoints_computed':False,
                      'pre_access_freeze_sha256':sha(lockpath),'reference_sha256':sha(target)}))


if __name__=='__main__': main()

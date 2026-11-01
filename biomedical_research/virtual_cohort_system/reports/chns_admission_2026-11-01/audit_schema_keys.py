"""Outcome-blind file integrity/identifier audit. No clinical columns reported.

Pandas decodes complete SAS chunks internally; only ID/wave are retained here.
The output contains metadata, counts and join cardinality, never identifiers,
clinical summaries, associations or row excerpts. No analytic cohort is formed.
"""
import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent
FILES = ['biomarker_09.sas7bdat','pexam_00.sas7bdat','mast_pub_12.sas7bdat','surveys_pub_12.sas7bdat']

def write_json(path,obj):
    path.write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

def main():
    reports, keys = {}, {}
    for name in FILES:
        p=ROOT/'private_data'/name
        with pd.read_sas(p,format='sas7bdat',iterator=True,chunksize=10000) as r:
            normalized={c.upper():c for c in r.column_names}
            if len(normalized)!=len(r.column_names):
                raise ValueError('Case-insensitive schema collision: '+name)
            wanted=['IDIND'] if name.startswith('mast_') else ['IDIND','WAVE']
            if not all(c in normalized for c in wanted):
                raise ValueError('Required key absent: '+name)
            rep={'file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                 'header_rows':int(r.row_count),'column_count':len(r.column_names),
                 'columns':[{'name':c.name,'label':c.label,'format':c.format,'type':c.ctype.decode('ascii')} for c in r.columns]}
            pieces=[]
            for chunk in r:
                part=chunk[[normalized[c] for c in wanted]].copy()
                part.columns=wanted
                pieces.append(part)
            key=pd.concat(pieces,ignore_index=True)
        rep['decoded_rows']=len(key)
        if rep['decoded_rows'] != rep['header_rows']:
            raise ValueError('Header/decoded row-count mismatch: '+name)
        rep['rows_missing_key']=int(key.isna().any(axis=1).sum())
        # Validate each observed cell, including WAVE in rows lacking IDIND.
        cells=key.to_numpy().ravel()
        observed=cells[~pd.isna(cells)]
        rep['finite_integral_keys']=bool(np.isfinite(observed).all() and
            (observed==np.floor(observed)).all())
        rep['keys_within_exact_float_integer_range']=bool((np.abs(observed)<2**53).all())
        if not rep['finite_integral_keys'] or not rep['keys_within_exact_float_integer_range']:
            raise ValueError('Unsafe identifier representation: '+name)
        valid=key.dropna()
        rep['duplicate_key_rows_all_waves']=int(valid.duplicated(wanted,keep=False).sum())
        if 'WAVE' in wanted:
            rep['wave_count_scope']='all nonmissing wave values, including rows with missing IDIND'
            rep['wave_record_counts']={str(int(k)):int(v) for k,v in key.WAVE.value_counts().sort_index().items()}
            valid=valid.loc[valid.WAVE==2009].copy()
            rep['records_wave_2009']=len(valid)
            rep['duplicate_key_rows_2009']=int(valid.duplicated(wanted,keep=False).sum())
        # Reject ambiguous linkage rather than silently deduplicating.
        if valid.duplicated(wanted).any():
            rep['join_ready']=False
        else:
            rep['join_ready']=True
            keys[name]=valid
        reports[name]=rep
    joins={}
    bio=keys.get(FILES[0])
    if bio is not None:
        for name in FILES[1:]:
            if name not in keys:
                joins[name]={'status':'unavailable_due_to_duplicate_keys'}
                continue
            on=['IDIND'] if name.startswith('mast_') else ['IDIND','WAVE']
            match=bio.merge(keys[name],how='left',on=on,indicator=True,validate='many_to_one' if len(on)==1 else 'one_to_one')
            joins[name]={'biomarker_records':len(bio),'matched_records':int((match._merge=='both').sum()),
                'unmatched_records':int((match._merge=='left_only').sum()),'join_validation':'many_to_one' if len(on)==1 else 'one_to_one'}
    write_json(ROOT/'SCHEMA_AND_KEY_AUDIT.json',{'scope':'Metadata and key-only linkage; no clinical distributions, correlations or analytic eligibility',
        'reader':'pandas SAS iterator; full chunks decoded internally, only IDIND/WAVE retained',
        'files':reports,'join_2009':joins,'target_effect_calculations':0,'clinical_moment_calculations':0,
        'participant_rows_exported':0,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    print(json.dumps({'files':{n:{k:v for k,v in r.items() if k not in ['columns','sha256']} for n,r in reports.items()},'join_2009':joins}))

if __name__=='__main__':
    main()

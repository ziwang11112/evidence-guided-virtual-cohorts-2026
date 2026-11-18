"""Separate raw-outcome QR calculations and complete ledger/summary audit."""
import scipy.linalg
from common import *

def independent_sample(frame,trait,counts,key):
    mask=(frame.age.to_numpy()>18)&np.isfinite(frame.age.to_numpy())
    y=frame[trait].to_numpy(float)
    mask &= np.isfinite(y)&(y>0)&frame.sex.isin(['F','M']).to_numpy()&frame.lifestyle.isin(GROUPS).to_numpy()
    pool=frame.loc[mask].reset_index(drop=True)
    rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence(16161,spawn_key=tuple(key))))
    rows=[]
    for (group,sex),n in zip(STRATA,counts):
        if not n:continue
        loc=np.where((pool.lifestyle.to_numpy()==group)&(pool.sex.to_numpy()==sex))[0]
        if len(loc)==0:raise ValueError('Unavailable cell')
        rows.extend(rng.choice(loc,size=n,replace=True).tolist())
    return pool.iloc[rows].copy()

def qr_raw(frame,trait):
    y=frame[trait].to_numpy(float);age=frame.age.to_numpy(float)
    valid=np.isfinite(y)&(y>0)&np.isfinite(age)&(age>18)
    d=frame.loc[valid];y=y[valid];age=age[valid];n=len(y)
    x=np.column_stack([np.ones(n),(d.lifestyle.to_numpy()==GROUPS[1]).astype(float),
        (d.lifestyle.to_numpy()==GROUPS[2]).astype(float),(age-age.mean())/10,(d.sex.to_numpy()=='F').astype(float)])
    if n<=7 or np.linalg.matrix_rank(x)<5 or np.std(y,ddof=1)<=1e-12:raise ValueError('Unidentified fit')
    q,r=scipy.linalg.qr(x,mode='economic');b=scipy.linalg.solve_triangular(r,q.T@y)
    return dict(n=n,sample_sd=float(np.std(y,ddof=1)),rural_minus_pastoralist=float(b[1]),
        urban_minus_pastoralist=float(b[2]),urban_minus_rural=float(b[2]-b[1]))

def main():
    verify_frozen();records=get_inputs();frames,_=load_frames(records)
    pref=read(HERE/'PREFLIGHT.json');plan=read(HERE/'STREAM_MAP.json')['streams']
    est=pd.read_csv(HERE/'ESTIMATES.csv');orig=pd.read_csv(HERE/'ORIGINAL_ESTIMATES.csv')
    index={(r.trait,int(r.replicate),r.stream):r for r in est.itertuples()}
    assert len(index)==len(est)
    expected_keys={(s['trait'],s['replicate'],s['stream']) for s in plan}
    assert set(index).issubset(expected_keys)
    if read(HERE/'RUN_RESULT.json')['status']=='complete':assert set(index)==expected_keys
    errors=[];max_delta=0.;checks=0
    def compare(expected,actual):
        nonlocal checks,max_delta
        assert expected['n']==actual.n
        for key in ['sample_sd']+CONTRASTS:
            delta=abs(expected[key]-float(getattr(actual,key)))
            max_delta=max(max_delta,delta);checks+=1
            assert delta<1e-8,(key,delta)
    for row in orig.itertuples():compare(qr_raw(frames[row.dataset_id],row.trait),row)
    replay_count=0
    for s in plan:
        if s['replicate'] not in [0,249,499] or (s['trait'],s['replicate'],s['stream']) not in index:continue
        row=index[s['trait'],s['replicate'],s['stream']]
        if row.status!='computed':
            errors.append(dict(trait=s['trait'],replicate=s['replicate'],stream=s['stream'],status='unavailable_preserved'));continue
        sample=independent_sample(frames[s['dataset_id']],s['trait'],pref['reference_counts'][s['trait']],s['spawn_key'])
        observed=[int(((sample.lifestyle==g)&(sample.sex==sex)).sum()) for g,sex in STRATA]
        assert observed==pref['reference_counts'][s['trait']]
        compare(qr_raw(sample,s['trait']),row);replay_count+=1
    dif=pd.read_csv(HERE/'DIFFERENCES.csv');assert len(dif)==31500
    difference_checks=0
    for row in dif.itertuples():
        left=index.get((row.trait,row.replicate,row.stream));right=index.get((row.trait,row.replicate,'R_B'))
        available=left is not None and right is not None and left.status=='computed' and right.status=='computed'
        assert (row.status=='computed')==available
        if available:
            expected=getattr(left,row.contrast)-getattr(right,row.contrast)
            assert abs(expected-row.difference)<1e-10 and abs(abs(expected)-row.absolute_difference)<1e-10
            difference_checks+=1
    summary=pd.read_csv(HERE/'CONTRAST_SUMMARIES.csv');assert len(summary)==63
    aggregate_checks=0
    for row in summary.itertuples():
        g=dif[(dif.trait==row.trait)&(dif.stream==row.stream)&(dif.contrast==row.contrast)]
        vals=g.loc[g.status=='computed','difference'].to_numpy(float)
        assert len(vals)==row.signed_n and 500-len(vals)==row.unavailable
        for prefix,v in [('signed_',vals),('absolute_',np.abs(vals))]:
            if not len(v):continue
            expected=[v.mean()]+np.percentile(v,[2.5,25,50,75,97.5],method='linear').tolist()
            fields=['mean','q025','q25','median','q75','q975']
            for field,value in zip(fields,expected):
                assert abs(value-getattr(row,prefix+field))<1e-10;aggregate_checks+=1
    sd=pd.read_csv(HERE/'SD_SUMMARIES.csv');assert len(sd)==24
    for row in sd.itertuples():
        g=est[(est.trait==row.trait)&(est.stream==row.stream)&(est.status=='computed')]
        values=g.sample_sd.to_numpy(float);assert len(values)==row.sd_n
        if len(values):
            for field,value in zip(['mean','q025','q25','median','q75','q975'],[values.mean()]+np.percentile(values,[2.5,25,50,75,97.5],method='linear').tolist()):
                assert abs(value-getattr(row,'sd_'+field))<1e-10;aggregate_checks+=1
    manifest=read(ROOT/'work/manuscript_integration_v33_2026-11-17/DELIVERY_MANIFEST.json')['files']
    assert all(sha(ROOT/name)==record['sha256'] for name,record in manifest.items())
    verify_frozen()
    receipt=dict(status='pass',scope='Root-authored independent formula and sampling replay; not external expert review',
        original_trait_fits=21,bootstrap_replay_trait_fits=replay_count,replay_unavailable=errors,
        numerical_fields_checked=checks,max_abs_numeric_difference=max_delta,complete_difference_checks=difference_checks,
        summary_field_checks=aggregate_checks,v33_delivery_files_unchanged=len(manifest),frozen_input_files_unchanged=True,
        resampled_individual_rows_persisted=False,created_utc=now())
    write_new(HERE/'INDEPENDENT_REVIEW.json',receipt);print(json.dumps(receipt))

if __name__=='__main__':main()

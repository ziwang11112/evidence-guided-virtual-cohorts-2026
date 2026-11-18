"""Complete raw-unit difference summaries, without threshold-based pass labels."""
from common import *

QUANTILES=[.025,.25,.5,.75,.975]
Q_NAMES=['q025','q25','median','q75','q975']

def describe(values,prefix=''):
    x=np.asarray(values,float);x=x[np.isfinite(x)]
    result={prefix+'n':len(x),prefix+'mean':float(x.mean()) if len(x) else None}
    q=np.quantile(x,QUANTILES,method='linear') if len(x) else [None]*5
    result.update({prefix+k:float(v) if v is not None else None for k,v in zip(Q_NAMES,q)})
    return result

def main():
    verify_frozen()
    plan=pd.DataFrame(read(HERE/'STREAM_MAP.json')['streams']).drop(columns='spawn_key')
    estimates=pd.read_csv(HERE/'ESTIMATES.csv',keep_default_na=True)
    key=['trait','replicate','stream','stream_index','dataset_id']
    assert not estimates.duplicated(key).any()
    assert len(estimates)==read(HERE/'RUN_RESULT.json')['completed_trait_samples']
    merged=plan.merge(estimates,on=key,how='left',validate='one_to_one')
    merged['status']=merged['status'].fillna('not_executed')
    lookup={(r.trait,int(r.replicate),r.stream):r for r in merged.itertuples()}
    virtual=read(HERE/'PREFLIGHT.json')['virtual_ids']
    differences=[];sd_diff=[]
    for t in TRAITS:
        for rep in range(500):
            rb=lookup[t,rep,'R_B']
            for role in ['R_A']+virtual:
                other=lookup[t,rep,role];valid=rb.status=='computed' and other.status=='computed'
                comparison='real_real' if role=='R_A' else 'virtual_real'
                info=dict(trait=t,replicate=rep,stream=role,comparison=comparison,
                    dataset_id='real' if role=='R_A' else role,status='computed' if valid else 'unavailable')
                for c in CONTRASTS:
                    difference=float(getattr(other,c)-getattr(rb,c)) if valid else None
                    differences.append(dict(**info,contrast=c,difference=difference,absolute_difference=abs(difference) if valid else None))
                sd_diff.append(dict(**info,difference=float(other.sample_sd-rb.sample_sd) if valid else None))
    dif=pd.DataFrame(differences);dif.to_csv(HERE/'DIFFERENCES.csv',index=False)
    pd.DataFrame(sd_diff).to_csv(HERE/'SD_DIFFERENCES.csv',index=False)
    originals=pd.read_csv(HERE/'ORIGINAL_ESTIMATES.csv')
    orig={(r.trait,r.dataset_id):r for r in originals.itertuples()}
    summaries=[]
    for (t,role,kind,c),g in dif.groupby(['trait','stream','comparison','contrast'],sort=False):
        values=g.difference.to_numpy(float)
        name='real' if role=='R_A' else role
        summaries.append(dict(trait=t,stream=role,comparison=kind,contrast=c,
            raw_unit='kg/m2' if t=='bmi' else 'mg/dL',planned=500,unavailable=int(g.status.ne('computed').sum()),
            original_real=float(getattr(orig[t,'real'],c)),original_other=float(getattr(orig[t,name],c)),
            original_difference=float(getattr(orig[t,name],c)-getattr(orig[t,'real'],c)),
            **describe(values,'signed_'),**describe(np.abs(values),'absolute_')))
    pd.DataFrame(summaries).to_csv(HERE/'CONTRAST_SUMMARIES.csv',index=False)
    spread=[]
    for (t,role,name),g in merged.groupby(['trait','stream','dataset_id'],sort=False):
        values=g.loc[g.status=='computed','sample_sd'].to_numpy(float)
        spread.append(dict(trait=t,stream=role,dataset_id=name,planned=500,
            unavailable=int(g.status.ne('computed').sum()),original_sd=float(orig[t,name].sample_sd),**describe(values,'sd_')))
    pd.DataFrame(spread).to_csv(HERE/'SD_SUMMARIES.csv',index=False)
    write_new(HERE/'SUMMARY_RECEIPT.json',dict(difference_rows=len(dif),contrast_summary_rows=len(summaries),
        sd_summary_rows=len(spread),complete_inventory=True,quantile_method='linear',
        population_or_equivalence_intervals=False,analysis_unit='two Agent constructions; six saved tables; conditional empirical resamples',
        files={name:sha(HERE/name) for name in ['DIFFERENCES.csv','SD_DIFFERENCES.csv','CONTRAST_SUMMARIES.csv','SD_SUMMARIES.csv']}))
    print(json.dumps(dict(differences=len(dif),contrast_summaries=len(summaries),sd_summaries=len(spread))))

if __name__=='__main__':main()

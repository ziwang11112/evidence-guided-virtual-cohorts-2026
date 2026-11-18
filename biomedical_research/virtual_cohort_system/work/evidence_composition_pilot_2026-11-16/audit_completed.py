"""Postrun forensic audit of manually inspected Gaussian laws and receipts.

This is NOT a generation or calibration script. It never imports author code or
changes their parameters. Parameter-name mappings below were read from all 24
sealed author programs. Its checks are supplementary, not new trial outcomes.
"""
from pathlib import Path
from datetime import datetime
import json, hashlib, ast
from collections import Counter
import numpy as np
from pilot import ROOT,PROJECT,verify_freeze,read,sha,write

def pick(model,*names):
    found=[name for name in names if name in model]
    if len(found)!=1:raise ValueError('Ambiguous or missing code-inspected parameter: '+repr(names))
    return model[found[0]]

def covariance(model,family):
    if family=='adjusted':
        if 'covariance' in model:return np.asarray(model['covariance'],float)
        a=pick(model,'correlation_xz','xz_loading','rho_xz','z_loading_x','corr_xz','x_z_slope')
        b=pick(model,'correlation_yz','yz_loading','rho_yz','z_loading_y','corr_yz','y_z_slope')
        r=pick(model,'residual_correlation_xy','residual_xy_correlation','partial_xy_given_z','residual_correlation')
        c=a*b+np.sqrt(1-a*a)*np.sqrt(1-b*b)*r
        return np.array([[1,c,a],[c,1,b],[a,b,1]])
    bkeys=['component_covariance','between_covariance','between_person_covariance']
    ekeys=['deviation_covariance','within_covariance','visit_deviation_covariance']
    if any(k in model for k in bkeys):
        b=np.asarray(pick(model,*bkeys));e1=np.asarray(pick(model,*ekeys));e2=e1
    else:
        bv=np.asarray(pick(model,'stable_variances','between_person_variances'))
        wv=np.asarray(pick(model,'deviation_variances','within_person_variances'))
        rb=pick(model,'stable_correlation','stable_component_correlation','between_person_correlation')
        rw=pick(model,'deviation_correlation','same_visit_deviation_correlation','within_visit_deviation_correlation','within_visit_correlations')
        rw=[rw,rw] if isinstance(rw,(int,float)) else rw
        b=np.outer(np.sqrt(bv),np.sqrt(bv))*np.array([[1,rb],[rb,1]])
        e1=np.outer(np.sqrt(wv),np.sqrt(wv))*np.array([[1,rw[0]],[rw[0],1]])
        e2=np.outer(np.sqrt(wv),np.sqrt(wv))*np.array([[1,rw[1]],[rw[1],1]])
    return np.block([[b+e1,b],[b,b+e2]])

def theoretical(c,family):
    if family=='adjusted':
        rc=c[0,1]-c[0,2]*c[1,2]/c[2,2]
        rv=[c[j,j]-c[j,2]**2/c[2,2] for j in [0,1]]
        return dict(partial_xy_given_z=float(rc/np.sqrt(np.prod(rv))),marginal_xy=float(c[0,1]/np.sqrt(c[0,0]*c[1,1])),slope_x_on_z=float(c[0,2]/c[2,2]))
    a=np.array([-1,0,1,0]);b=np.array([0,-1,0,1])
    return dict(change_correlation=float(a@c@b/np.sqrt((a@c@a)*(b@c@b))),same_visit_correlation=float((c[0,1]/np.sqrt(c[0,0]*c[1,1])+c[2,3]/np.sqrt(c[2,2]*c[3,3]))/2),cross_visit_correlation=float(c[0,3]/np.sqrt(c[0,0]*c[3,3])))

def main():
    freeze=verify_freeze();closed=read(ROOT/'CONSTRUCTION_CLOSURE.json');ec=read(ROOT/'EXECUTION_CLOSURE.json')
    review=[];issues=[];provenance_count=Counter();api_times=[];execution_times=[];output_hashes=[];numeric_hashes=[]
    for row in closed['rows']:
        cid=row['id'];folder=ROOT/'candidates'/cid
        model=read(folder/'model_spec.json')['model'];record=read(folder/'decision_record.json');code=(folder/'generator.py').read_text()
        c=covariance(model,row['family']);truth=theoretical(c,row['family']);eigen=np.linalg.eigvalsh(c)
        claim_errors={r['name']:abs(r['value']-truth[r['name']]) for r in record['requested_estimands']}
        payload=read(ROOT/'inputs'/row['payload']);allowed={r['record_id'] for r in payload['evidence_records']}
        for index,entry in enumerate(record['parameter_provenance']):
            provenance_count[entry['kind']]+=1
            if not set(entry.get('record_ids',[]))<=allowed:issues.append({'id':cid,'entry':index,'issue':'Nonvisible source id'})
        call=ROOT/'calls'/cid;receipt=read(call/'receipt.json');request=read(call/'request.json')['body']
        api_times.append((receipt['started_utc'],receipt['ended_utc']))
        assert request['input']==(ROOT/'inputs'/(cid+'.prompt.txt')).read_text(encoding='utf-8')
        assert not any(k in request for k in ['previous_response_id','conversation','tools'])
        assert request['model']==receipt['requested_model']==receipt['returned_model']=='gpt-6.1-sol'
        assert sha(call/'prompt.txt')==receipt['prompt_sha256'] and sha(call/'request.json')==receipt['request_sha256']
        for name in ['response_raw.json','response_text.txt','artifact.json']:assert sha(call/name)==receipt[name+'_sha256']
        artifact=read(call/'artifact.json');assert code==artifact['generator_py'] and model==artifact['model_spec']
        imports=[]
        for node in ast.walk(ast.parse(code)):
            if isinstance(node,ast.Import):imports.extend(x.name for x in node.names)
            if isinstance(node,ast.ImportFrom):imports.append(node.module)
        assert set(imports)<={'numpy','pandas'}
        review.append({'id':cid,'family':row['family'],'condition':row['condition'],
            'root_inspected_full_generator_and_estimand_record':True,
            'construction':'Gaussian Cholesky/multivariate-normal or equivalent Gaussian factor law; manually inspected',
            'population_covariance_in_requested_order':c.tolist(),'minimum_covariance_eigenvalue':float(eigen.min()),
            'all_moments_finite':bool(eigen.min()>0),'theoretical_estimands':truth,'declaration_absolute_errors':claim_errors,
            'max_declaration_error':max(claim_errors.values()),'post_sample_moment_forcing_observed':False,
            'positivity_selection_observed':False,'scientific_parameters_changed_by_host':False,
            'code_sha256':sha(folder/'generator.py'),'provenance_entries':len(record['parameter_provenance'])})
    for item in ec['rows']:
        folder=ROOT/'executions'/item['id']/str(item['seed']);receipt=read(folder/'execution.json');wr=read(folder/'output/worker_report.json')
        execution_times.append(receipt['created_utc']);output_hashes.append(receipt['generated_sha256'])
        for name,h in receipt['files'].items():assert sha(folder/name)==h
        assert not wr['pre_import_probe']['mnt_visible'] and not wr['pre_import_probe']['home_visible'] and not wr['pre_import_probe']['route_table']
        # Count duplicate numeric outputs excluding cosmetic row identifiers.
        import pandas as pd
        frame=pd.read_csv(folder/'output/generated.csv',float_precision='round_trip').drop(columns=['person_id'])
        numeric_hashes.append(hashlib.sha256(frame.to_numpy(dtype='<f8').tobytes()).hexdigest())
    assert max(datetime.fromisoformat(x[1]) for x in api_times) <= datetime.fromisoformat(closed['closed_utc'])
    assert datetime.fromisoformat(closed['closed_utc']) <= min(datetime.fromisoformat(x) for x in execution_times)
    assert datetime.fromisoformat(freeze['frozen_utc']) < min(datetime.fromisoformat(x[0]) for x in api_times)
    assert len(api_times)==24 and len(execution_times)==72 and not issues
    assert all(r['all_moments_finite'] and r['max_declaration_error']<1e-12 for r in review)
    write(ROOT/'analysis/CODE_AND_INTEGRITY_AUDIT.json',{'reviewer':'root assistant; no independent human adjudication',
        'postrun_diagnostic_not_a_new_primary_endpoint':True,'constructed_programs':len(review),'provenance_entries_by_kind':dict(provenance_count),
        'candidate_code_and_spec_exactly_from_api':True,'all_prompts_equal_frozen_inputs':True,'source_ids_visible':not issues,
        'freeze_before_calls_and_all_authors_closed_before_execution':True,'isolated_execution_receipts_verified':len(execution_times),
        'unique_output_file_hashes':len(set(output_hashes)),'unique_numeric_table_hashes_excluding_person_id':len(set(numeric_hashes)),
        'duplicates_note':'Same scientific law and same scheduled seeds can produce identical numerical tables; they are not independent datasets.',
        'all_gaussian_laws_nondegenerate':True,'max_theory_to_declaration_difference':max(r['max_declaration_error'] for r in review),
        'issues':issues,'candidates':review})
    print(json.dumps({'audited_programs':24,'verified_executions':72,'max_theory_to_declaration_difference':max(r['max_declaration_error'] for r in review),
                      'unique_numeric_tables':len(set(numeric_hashes)),'provenance_entries':sum(provenance_count.values()),'issues':issues}))

if __name__=='__main__':main()

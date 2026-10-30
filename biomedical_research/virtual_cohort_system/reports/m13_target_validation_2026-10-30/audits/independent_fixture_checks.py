"""Independent M13-B arithmetic audit. All inputs are invented; no target reads.

Reference uses weighted least squares through QR/SVD and row influence sums,
rather than copying the evaluator's normal-equation/sandwich implementation.
The two-PSU expression is independently checked against a closed-form example.
"""
from __future__ import annotations

import importlib.util
import hashlib
import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
CHECKS: list[dict] = []


def record(name, passed=True, **details):
    if not bool(passed):
        raise AssertionError(name + ": " + repr(details))
    CHECKS.append({"check": name, "passed": True, **details})


def independent_fit(x, y, w, strata, psu, domain):
    """WR first-stage Taylor variance from independently formed influences."""
    x, y, w = np.asarray(x), np.asarray(y), np.asarray(w)
    d = np.asarray(domain, bool)
    xd, yd, wd = x[d], y[d], w[d]
    beta = np.linalg.lstsq(np.sqrt(wd)[:, None] * xd,
                           np.sqrt(wd) * yd, rcond=None)[0]
    # QR/SVD inverse of whitened design, not inverse of normal equations.
    pinv = np.linalg.pinv(np.sqrt(wd)[:, None] * xd)
    bread = pinv @ pinv.T
    influences = np.zeros((len(y), x.shape[1]))
    influences[d] = ((wd * (yd - xd @ beta))[:, None] * xd) @ bread
    covariance = np.zeros((x.shape[1], x.shape[1]))
    for h in sorted(set(strata)):
        js = sorted(set(psu[np.asarray(strata) == h]))
        if len(js) == 1:
            raise ValueError("full-frame singleton")
        totals = np.vstack([influences[(strata == h) & (psu == j)].sum(axis=0)
                            for j in js])
        if len(js) == 2:
            delta = totals[0] - totals[1]
            covariance += np.outer(delta, delta)
        else:
            centered = totals - totals.mean(axis=0)
            covariance += len(js) / (len(js)-1) * centered.T @ centered
    represented = set(zip(np.asarray(strata)[d], np.asarray(psu)[d]))
    df = len(represented) - len(set(np.asarray(strata)[d]))
    return beta, covariance, df


def fixture():
    """Six invented strata, reused PSU labels, one entirely empty-domain PSU."""
    rows = []
    for h in range(6):
        for j in (1, 2):
            for k in range(8):
                age = 20 + ((7*k + 3*h + j) % 40)
                bmi = 18.5 + ((13*k + 7*h + 3*j) % 113) / 10
                race = (k + j + h) % 2
                weight = 0.75 + (1 + ((h + 2*j + 3*k) % 13)) / 4
                B, A = (bmi-24)/5, (age-40)/10
                y = 27 + 4*B + 1.2*A - 0.8*race + 0.65*B*B + 0.9*j - 0.3*h + ((k*5+h) % 7)/5
                rows.append((f"invented-{h}-{j}-{k}",h,j,weight,age,bmi,race,y,not(h==0 and j==2)))
    return pd.DataFrame(rows, columns=["record_id","stratum","psu","weight","age","bmi","race","y","domain"])


def evaluator_checks(data, expected):
    path = HERE.parent / "evaluator" / "bodyfat_evaluator.py"
    spec = importlib.util.spec_from_file_location("audited_m13b_evaluator",path)
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    d=data.domain.to_numpy(); h=data.stratum.to_numpy(); j=data.psu.to_numpy(); w=data.weight.to_numpy(); y=data.y.to_numpy()
    B=(data.bmi.to_numpy()-24)/5; A=(data.age.to_numpy()-40)/10; r=data.race.to_numpy()
    X=np.column_stack([np.ones(len(data)),B,A,r]); Xq=np.column_stack([X,B*B])
    fit=ev.fit_domain(X,y,w,h,j,d)
    record("evaluator WLS vs independent SVD",np.allclose(fit["beta"],expected["beta"],rtol=0,atol=2e-12),maximum_error=float(np.max(np.abs(fit["beta"]-expected["beta"]))))
    record("evaluator sandwich vs independent row-influence variance",np.allclose(fit["covariance"],expected["covariance"],rtol=0,atol=2e-12),maximum_error=float(np.max(np.abs(fit["covariance"]-expected["covariance"]))))
    record("evaluator nested full-frame and domain counts",fit["full_design_psus"]==12 and fit["full_design_strata"]==6 and fit["domain_psus"]==11 and fit["domain_strata"]==6 and fit["df"]==5)
    # Same exact four-PSU example as the hand calculation; public reporting gates deliberately bypassed.
    ex=ev.fit_domain(np.ones((4,1)),[10,np.nan,20,40],[1,1,2,3],[0,0,1,1],[1,2,1,2],[1,0,1,1])
    record("evaluator exact zero-domain PSU example",np.isclose(ex["beta"][0],85/3,rtol=0,atol=1e-12) and np.isclose(ex["covariance"][0,0],13525/162,rtol=0,atol=1e-12))
    for factor in (1e-12,1e12):
        scaled=ev.fit_domain(X,y,w*factor,h,j,d)
        record("evaluator weight scale "+str(factor),np.allclose(fit["beta"],scaled["beta"],rtol=0,atol=2e-11) and np.allclose(fit["covariance"],scaled["covariance"],rtol=0,atol=2e-11))
    p=np.random.default_rng(777).permutation(len(data))
    perm=ev.fit_domain(X[p],y[p],w[p],h[p],j[p],d[p])
    record("evaluator row permutation invariance",np.allclose(fit["beta"],perm["beta"],rtol=0,atol=2e-11) and np.allclose(fit["covariance"],perm["covariance"],rtol=0,atol=2e-11))
    xmiss=X.copy(); ymiss=y.copy(); xmiss[~d]=np.nan; ymiss[~d]=np.nan
    missing=ev.fit_domain(xmiss,ymiss,w,h,j,d)
    record("out-of-domain NaNs contribute zero",np.allclose(fit["beta"],missing["beta"]) and np.allclose(fit["covariance"],missing["covariance"]))
    # An entirely empty-domain stratum likewise remains part of the full design.
    d2=d.copy(); d2[h==1]=False
    rb,rv,rdf=independent_fit(X,y,w,h,j,d2); ef=ev.fit_domain(X,y,w,h,j,d2)
    record("empty-domain stratum retained",ef["full_design_strata"]==6 and ef["domain_strata"]==5 and ef["df"]==rdf and np.allclose(ef["covariance"],rv,rtol=0,atol=2e-12))
    # Check generic m_h/(m_h-1) factor in a third-PSU stratum as well.
    j3=j.copy(); j3[(h==5)&(np.arange(len(j))%8>=4)]=3
    rb,rv,rdf=independent_fit(X,y,w,h,j3,d); ef=ev.fit_domain(X,y,w,h,j3,d)
    record("three-PSU stratum factor",np.allclose(ef["covariance"],rv,rtol=0,atol=2e-12) and ef["df"]==rdf)
    qfit=ev.fit_domain(Xq,y,w,h,j,d); curvature=ev.contrast_interval(qfit,[0,0,0,0,1.28])
    expected_se=1.28*np.sqrt(expected["quadratic_covariance"][4][4])
    record("curvature estimate and interval",np.isclose(curvature["estimate"],expected["curvature"],rtol=0,atol=2e-11) and np.isclose(curvature["se"],expected_se,rtol=0,atol=2e-11) and np.isclose(curvature["ci_high"],expected["curvature"]+stats.t.ppf(.975,5)*expected_se,rtol=0,atol=2e-11))
    generated=y+2+0.3*B-0.2*A+0.1*r+np.sin(np.arange(len(data)))/4
    paired=ev.fit_domain(X,generated-y,w,h,j,d)
    record("paired difference estimate and covariance",np.allclose(paired["beta"],expected["paired_beta"],rtol=0,atol=2e-12) and np.allclose(paired["covariance"],expected["paired_covariance"],rtol=0,atol=2e-12))
    for c in ([1,0,0,0],[0,1,0,0],[0,0,1,0]):
        ci=ev.contrast_interval(paired,c); cc=np.array(c)
        expected_est=float(cc@np.array(expected["paired_beta"])); expected_se=np.sqrt(cc@np.array(expected["paired_covariance"])@cc)
        record("paired interval "+str(c),np.isclose(ci["ci_low"],expected_est-stats.t.ppf(.975,5)*expected_se,rtol=0,atol=2e-12))
    record("weighted inverse ECDF tied exact thresholds",np.array_equal(ev.weighted_quantile([10,20,20,30,50],[1,2,1,2,2],[0,.125,.25,.5,.75,1]),[10,10,20,20,30,50]))
    record("weighted inverse ECDF reordered ties",np.array_equal(ev.weighted_quantile([50,20,10,30,20],[2,1,1,2,2]),[20,20,30]))
    record("weighted inverse ECDF weight-scale",np.array_equal(ev.weighted_quantile([10,20,20,30,50],np.array([1,2,1,2,2])*1e200),[20,20,30]))
    def rejects(name,func,category):
        try: func()
        except ev.ValidationError as exc:
            record(name,str(exc)==category,category=str(exc)); return
        raise AssertionError(name+": was accepted")
    rejects("full-design singleton rejected",lambda: ev.fit_domain(X,y,w,h,np.where(h==5,1,j),d),"singleton_full_design_stratum")
    rejects("rank deficient fit rejected",lambda:ev.fit_domain(np.column_stack([X,X[:,1]]),y,w,h,j,d),"rank_deficient_design")
    rejects("invalid quantile weight rejected",lambda:ev.weighted_quantile([1,2],[1,-1]),"invalid_quantile_values")
    full=pd.DataFrame(dict(id=data.record_id,SEQN=np.arange(1,len(data)+1),WTMEC2YR=w,SDMVSTRA=h,SDMVPSU=j,RIDAGEYR=data.age,RIAGENDR=1+np.arange(len(data))%2,RIDRETH3=np.where(r==1,4,3),BMXBMI=data.bmi,DXAEXSTS=np.ones(len(data)),DXDTOPF=y),columns=ev.FULL_COLUMNS)
    full.loc[~d,"RIDAGEYR"]=15; full.loc[~d,"BMXBMI"]=np.nan; full.loc[~d,"DXDTOPF"]=np.nan
    full=ev.validate_full_frame(full); observed=ev.expected_observed(full)
    record("whitelist derived covariates and no DXA family",list(observed.columns)==list(ev.OBSERVED_COLUMNS) and not any(str(c).startswith(("DX","SDMV","WT")) for c in observed.columns))
    observed2=ev.validate_observed(observed.sample(frac=1,random_state=7),full)
    record("observed row IDs realigned exactly",observed2.id.tolist()==observed.id.tolist())
    bad=observed.copy(); bad["DXDTOFAT"]=1
    rejects("extra DXA measurement rejected",lambda:ev.validate_observed(bad,full),"column_whitelist_or_order_mismatch")
    bad=observed.copy(); bad.loc[0,"inv_bmi"]+=0.01
    rejects("derived covariate corruption rejected",lambda:ev.validate_observed(bad,full),"observed_covariate_mismatch")
    tab=observed.copy(); tab["bodyfat"]=generated[d]
    tabperm=tab.sample(frac=1,random_state=17)
    record("generated row IDs realigned exactly",ev.validate_generated(tabperm,observed).id.tolist()==observed.id.tolist())
    badtab=tab.copy(); badtab.loc[0,"id"]="invented-unknown"
    rejects("unknown generated row rejected",lambda:ev.validate_generated(badtab,observed),"id_set_mismatch")
    badtab=tab.copy(); badtab.loc[0,"age"]+=1
    rejects("generated covariate mutation rejected",lambda:ev.validate_generated(badtab,observed),"generated_covariate_mismatch")
    badfull=full.copy(); badfull.loc[0,"DXDTOPF"]=101
    rejects("physical endpoint integrity failure",lambda:ev.validate_full_frame(badfull),"bodyfat_outside_physical_support")
    badfull=full.copy(); badfull.loc[0,"DXAEXSTS"]=2
    record("completed but invalid DXA scan excluded",not ev.domains(badfull)["eligible"][0])
    boundaries=full.copy(); boundaries.loc[:5,"BMXBMI"]=[18.49,18.5,29.999,30,35,35.001]
    bd=ev.domains(boundaries)
    record("fixed primary and extension boundary rules",bd["primary"][:6].tolist()==[False,True,True,False,False,False] and bd["extension"][:6].tolist()==[False,False,False,True,True,False])
    measured=ev.estimate_panel(full,full.DXDTOPF.to_numpy()); result=ev.evaluate_table(full,observed,tabperm,measured)
    record("all endpoint slots retained including sparse cells",len(measured)==62 and len(result)==62 and any(x["status"]=="not_estimable" for x in measured))
    record("quartiles and IQR have no intervals",all(not x["interval_available"] and x["se"] is None for x in measured if x["kind"]=="distribution"))
    record("all estimable linear endpoints have paired interval",all(x["paired_difference"] is not None for x in result if x["kind"]=="linear" and x["status"]=="estimable"))
    sparse=np.zeros(len(full),bool); sparse[:4]=True
    g=ev.gate(full,sparse)
    record("sparse-cell safeguards fail without merging",not g["estimable"] and {"n_below_30","kish_below_20","domain_psus_below_8","domain_df_below_4"}.issubset(g["failures"]))
    manifest={"schema_version":1,"observed_path":"invented-only.csv","preaccess_sha256":"0"*64,"tables":[]}
    for entry in ev.scheduled_roster():
        entry.update(status="failed",path=None)
        if entry["kind"]=="agent":
            entry.update(execution_receipt_path="invented-receipt.json",execution_status="invented_failure")
        else:
            entry.update(reference_receipt_path="invented-reference-receipt.json")
        manifest["tables"].append(entry)
    ev.validate_manifest(manifest)
    record("manifest retains all sixteen scheduled failures")
    altered=copy.deepcopy(manifest)
    for entry in altered["tables"]:
        if entry["builder"]=="build01" and entry["candidate"]=="initial":entry["candidate"]="posthoc_replacement"
    rejects("candidate substitution rejected",lambda:ev.validate_manifest(altered),"frozen_table_roster_mismatch")
    altered=copy.deepcopy(manifest); altered["tables"].pop()
    rejects("dropping a scheduled comparison rejected",lambda:ev.validate_manifest(altered),"manifest_requires_16_tables")
    cpath=HERE.parent/"custodian"/"prep.py"
    cspec=importlib.util.spec_from_file_location("audited_m13b_custodian",cpath)
    cp=importlib.util.module_from_spec(cspec); cspec.loader.exec_module(cp)
    demo=full[["SEQN","WTMEC2YR","SDMVSTRA","SDMVPSU","RIDAGEYR","RIAGENDR","RIDRETH3"]].copy()
    bmx=full[["SEQN","BMXBMI"]].copy(); dxx=full[["SEQN","DXAEXSTS","DXDTOPF"]].copy()
    dxx["DXDTOFAT"]=999.0
    built,obs,quality=cp.build_frames(demo,bmx,dxx)
    record("custody retains entire design and zero-domain PSU",len(built)==len(full) and quality["design"]["zero_domain_psus_retained"]==1)
    record("custody output matches evaluator whitelist",list(obs.columns)==list(ev.OBSERVED_COLUMNS) and list(built.columns)==list(ev.FULL_COLUMNS))
    validated=ev.validate_observed(obs,ev.validate_full_frame(built))
    record("custody evaluator invented interface agreement",len(validated)==int(d.sum()))
    record("custody opaque IDs do not disclose SEQN",all(str(v).startswith("m13b_") and len(str(v))==37 for v in built.id) and not any(c in obs.columns for c in ["SEQN","DXDTOPF","DXDTOFAT"]))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # Exact rational mean/variance: one of four PSUs has no domain members.
    xx = np.ones((4,1)); yy = np.array([10., np.nan,20.,40.]); ww = np.array([1.,1.,2.,3.])
    hh = np.array([0,0,1,1]); jj = np.array([1,2,1,2]); dd = np.array([1,0,1,1],bool)
    b,v,df = independent_fit(xx,yy,ww,hh,jj,dd)
    record("reference matches exact mean", np.allclose(b,[85/3],rtol=0,atol=1e-12), mean=float(b[0]))
    record("reference matches exact zero-domain PSU variance",np.allclose(v,[[13525/162]],rtol=0,atol=1e-12), variance=float(v[0,0]), domain_df=df)
    record("exact fixture domain df", df==1)
    data=fixture(); d=data.domain.to_numpy(); h=data.stratum.to_numpy(); j=data.psu.to_numpy(); w=data.weight.to_numpy(); y=data.y.to_numpy()
    B=(data.bmi.to_numpy()-24)/5; A=(data.age.to_numpy()-40)/10; r=data.race.to_numpy()
    X=np.column_stack([np.ones(len(data)),B,A,r]); Xq=np.column_stack([X,B*B])
    beta,cov,df=independent_fit(X,y,w,h,j,d)
    record("invented main fixture passes domain design gate",df==5 and d.sum()==88, n=int(d.sum()),domain_psus=11,domain_strata=6,domain_df=df)
    beta_q,cov_q,_=independent_fit(Xq,y,w,h,j,d)
    # Curvature at BMI 20,24,28: B=-0.8,0,0.8.
    grid=np.array([[1,-.8,0,0,.64],[1,0,0,0,0],[1,.8,0,0,.64]])
    curvature=float(np.array([1,-2,1]) @ grid @ beta_q)
    record("curvature exact multiplier",np.isclose(curvature,1.28*beta_q[4],rtol=0,atol=1e-12), curvature=curvature)
    scaled=independent_fit(X,y,w*12345.67,h,j,d)
    record("reference weight-scale invariance",np.allclose(beta,scaled[0],rtol=0,atol=1e-10) and np.allclose(cov,scaled[1],rtol=0,atol=1e-10))
    p=np.random.default_rng(100).permutation(len(data)); perm=independent_fit(X[p],y[p],w[p],h[p],j[p],d[p])
    record("reference row permutation invariance",np.allclose(beta,perm[0],rtol=0,atol=1e-10) and np.allclose(cov,perm[1],rtol=0,atol=1e-10))
    generated=y+2+0.3*B-0.2*A+0.1*r+np.sin(np.arange(len(data)))/4
    bg,vg,_=independent_fit(X,generated,w,h,j,d); bd,vd,_=independent_fit(X,generated-y,w,h,j,d)
    record("paired coefficient identity",np.allclose(bg-beta,bd,rtol=0,atol=1e-11),difference=bd.tolist())
    record("paired covariance differs from false independence",not np.allclose(vd,vg+cov),max_difference=float(np.max(np.abs(vd-(vg+cov)))))
    expected={"beta":beta.tolist(),"covariance":cov.tolist(),"domain_df":df,"quadratic_beta":beta_q.tolist(),"quadratic_covariance":cov_q.tolist(),"curvature":curvature,"paired_beta":bd.tolist(),"paired_covariance":vd.tolist()}
    data.to_csv(HERE/"invented_fixture.csv",index=False)
    (HERE/"independent_expected.json").write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8")
    evaluator_hash=evaluator_checks(data,expected)
    (HERE/"independent_fixture_results.json").write_text(json.dumps({"status":"pass","data_scope":"wholly invented fixtures; no target access","evaluator_sha256":evaluator_hash,"checks":CHECKS},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"checks":len(CHECKS),"status":"pass","evaluator_sha256":evaluator_hash}))


if __name__=="__main__":
    main()

"""Independent population-moment and quadrature audit of the submitted frozen laws."""
import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from scipy.integrate import quad
from scipy.stats import norm

root = Path(__file__).resolve().parent


def audit(weights, offsets, source):
    s, d = source["means"]["SBP"], source["means"]["DBP"]
    vs, vd = source["sd"]["SBP"]**2, source["sd"]["DBP"]**2
    csd = source["pearson"]*np.sqrt(vs*vd)
    total = np.array([[vd, csd-vd], [csd-vd, vs+vd-2*csd]])
    weights, offsets = np.array(weights), np.array(offsets)
    base = np.array([d,s-d])
    means = base+offsets
    within = total - np.einsum("i,ij,ik->jk",weights,offsets,offsets)
    second = np.zeros((2,2))
    first = np.zeros(2)
    tail = 0.
    min_eig = []
    for w,m in zip(weights,means):
        cov_log = np.log(1+within/np.outer(m,m))
        min_eig.append(float(min(np.linalg.eigvalsh(cov_log))))
        assert min_eig[-1] > 0
        mu = np.log(m)-np.diag(cov_log)/2
        a,b = np.exp(mu+np.diag(cov_log)/2)
        first += w*np.array([a,b])
        second += w*(np.outer([a,b],[a,b])*np.exp(cov_log))
        sig = np.sqrt(cov_log[0,0])
        cstd = np.sqrt(cov_log[1,1]-cov_log[0,1]**2/cov_log[0,0])
        low, high = (np.log(np.array([90.,140.]))-mu[0])/sig
        def integrand(z):
            dbp = np.exp(mu[0]+sig*z)
            cz = mu[1]+cov_log[1,0]*z/sig
            return norm.pdf(z)*norm.sf((np.log(140-dbp)-cz)/cstd)
        integ,err = quad(integrand,low,high,epsabs=1e-12,epsrel=1e-12)
        assert err < 1e-10
        tail += w*(integ+norm.sf(high))
    cov = second-np.outer(first,first)
    q1 = cov[0,:].sum()/np.sqrt(cov[0,0]*cov.sum())
    got = [first.sum(),first[0],np.sqrt(cov.sum()),np.sqrt(cov[0,0]),q1]
    np.testing.assert_allclose(got,[s,d,np.sqrt(vs),np.sqrt(vd),source["pearson"]],atol=1e-10,rtol=0)
    return {"mean_s":got[0],"mean_d":got[1],"sd_s":got[2],"sd_d":got[3],"Q1":q1,"Q2":tail,
            "minimum_log_cov_eigenvalues":min_eig}


if __name__ == "__main__":
    seal = json.loads((root/"CLOSURE.json").read_text())
    assert seal["target_effect_accessed"] is False
    source = json.loads((root/"SOURCE.json").read_text())
    results = {}
    for name in ["primary","alternative","statistical"]:
        spec = json.loads((root/"candidates"/name/"model_spec.json").read_text())["model"]
        if name=="statistical":
            results[name] = audit([1.],[[0.,0.]],source)
        else:
            c=spec["calibration"]
            assert [c["mean_sbp"],c["mean_dbp"],c["sd_sbp"],c["sd_dbp"],c["pearson_sbp_dbp"]] == [source["means"]["SBP"],source["means"]["DBP"],source["sd"]["SBP"],source["sd"]["DBP"],source["pearson"]]
            results[name] = audit(spec["component_weights"],spec["component_mean_offsets_dbp_pulse"],source)
    with (root/"MODEL_AUDIT.json").open("x",encoding="utf8") as f:
        json.dump({"time_utc":datetime.now(timezone.utc).isoformat(),"target_reveal_existed_at_audit":(root/"REVEAL.json").exists(),
                   "method":"Exact first and second moments of finite lognormal mixtures; 1D conditional-normal quadrature of joint threshold probability",
                   "population":results},f,indent=2)
    print({key:{k:round(item[k],6) for k in ["Q1","Q2"]} for key,item in results.items()})

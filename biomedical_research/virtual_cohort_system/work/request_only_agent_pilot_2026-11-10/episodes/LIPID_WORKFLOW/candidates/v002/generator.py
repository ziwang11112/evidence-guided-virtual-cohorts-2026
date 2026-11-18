import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generator requires observed=None')
    rng = np.random.default_rng(seed)
    n = 3000
    # Fixed scientific specification is embedded to avoid dependence on worker
    # metadata wrapping. All stochastic draws use the supplied seed.
    sd = np.array([7.99,5.71,1.03,0.27])
    R = np.array([[1,.454,.103,-.010],[.454,1,.215,.107],[.103,.215,1,.209],[-.010,.107,.209,1]])
    C = R*np.outer(sd,sd)
    vs = (100/120)*(20/120)*120/119
    cov_s = np.array([4.07,5.14,.33,.26])*vs
    Sxx = np.array([[C[0,0],cov_s[0],C[0,1]], [cov_s[0],vs,cov_s[1]], [C[1,0],cov_s[1],C[1,1]]])
    Sxy = np.array([[C[0,2],C[0,3]],[cov_s[2],cov_s[3]],[C[1,2],C[1,3]]])
    B = np.linalg.solve(Sxx,Sxy)
    E = C[2:4,2:4] - Sxy.T@B
    rho = E[0,1]/np.sqrt(E[0,0]*E[1,1])
    if np.min(np.linalg.eigvalsh(E)) <= 0:
        raise ValueError('Source-derived covariance not positive definite')
    female = rng.random(n)<.52
    sex = np.where(female,'F','M')
    pF = np.array([.541,.306,.153])
    pM = np.array([.660,.231,.109])
    probs = np.where(female[:,None],pF,pM)
    group = (rng.random(n)[:,None]>np.cumsum(probs,axis=1)).sum(axis=1)
    triangles = np.array([[18,25,40],[40,48,65],[65,70,85]])
    age = np.empty(n)
    for k,(left,mode,right) in enumerate(triangles):
        mask = group==k
        age[mask] = rng.triangular(left,mode,right,size=int(mask.sum()))
    age_center = np.where(female,np.dot(pF,triangles.mean(axis=1)),np.dot(pM,triangles.mean(axis=1)))
    transition = rng.random(n)<.30
    base_bmi = np.where(female,25.5,21.8)
    bmi_sd = np.where(female,4.8,3.4)
    mean_bmi = base_bmi + .04*(age-age_center) + transition*np.where(female,1.0,.9)
    sigma_bmi = np.sqrt(np.log1p((bmi_sd/mean_bmi)**2))
    bmi = mean_bmi*np.exp(sigma_bmi*rng.standard_normal(n)-.5*sigma_bmi**2)
    mu_tc = np.where(female,4.43,3.74) + B[0,0]*(age-age_center) + B[2,0]*(bmi-base_bmi) + transition*np.where(female,.24,.42)
    mu_hd = np.where(female,1.69,1.67) + B[0,1]*(age-age_center) + B[2,1]*(bmi-base_bmi) + transition*np.where(female,.25,.24)
    s_tc = np.where(female,1.30,1.00)
    s_hd = np.where(female,.38,.30)
    if np.any(mu_tc<=0) or np.any(mu_hd<=0):
        raise ValueError('Nonpositive conditional lipid mean')
    lt = np.sqrt(np.log1p((s_tc/mu_tc)**2))
    lh = np.sqrt(np.log1p((s_hd/mu_hd)**2))
    latent_rho = np.log1p(rho*s_tc*s_hd/(mu_tc*mu_hd))/(lt*lh)
    if np.any(np.abs(latent_rho)>=1):
        raise ValueError('Infeasible lognormal covariance')
    zt = rng.standard_normal(n)
    zh = latent_rho*zt+np.sqrt(1-latent_rho**2)*rng.standard_normal(n)
    tc = mu_tc*np.exp(lt*zt-.5*lt**2)
    hd = mu_hd*np.exp(lh*zh-.5*lh**2)
    out = pd.DataFrame({'id':['SYN%05d'%(i+1) for i in range(n)],'age':age,'sex':sex,'bmi':bmi,'total_cholesterol':tc,'hdl_cholesterol':hd})
    assert out.shape==(3000,6)
    assert np.isfinite(out[['age','bmi','total_cholesterol','hdl_cholesterol']].to_numpy()).all()
    assert (out[['bmi','total_cholesterol','hdl_cholesterol']].to_numpy()>0).all()
    return out

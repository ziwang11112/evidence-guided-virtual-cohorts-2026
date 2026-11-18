"""Record bounded independent code/source review, before opening clinical results.

This script performs scalar parameter algebra only: it does not import or execute
candidate programs, read generated rows, or open evaluation/reference files.
"""
from pathlib import Path
import hashlib, json, math, itertools
from datetime import datetime, timezone
import numpy as np

R = Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def spec(pair): return load(R / f'episodes/{pair}_GENERIC/candidates/v000/model_spec.json')

def scalar_checks():
    p = .055 * 22 / 3.8
    mt,mh,ct,ch,rho = 3.8,1.15,.22,.28,.35
    st,sh = math.sqrt(math.log1p(ct*ct)),math.sqrt(math.log1p(ch*ch))
    vt,vh = (mt*ct)**2,(mh*ch)**2
    cov = mt*mh*math.expm1(rho*st*sh)
    mn = mt-mh; vn = vt+vh-2*cov
    sn = math.sqrt(math.log1p(vn/mn**2))
    rn = math.log1p((cov-vh)/(mn*mh))/(sn*sh)
    low = mt*(12/22)**p*math.exp((.012*(-20)+.1*(-.55))/mt)
    high = mh*math.exp((-.012*(-10)+.0015*47+.1*.45+.1)/mh)
    assert low > high and vn > 0 and abs(rn) < 1
    assert math.isclose(vn+vh+2*(cov-vh), vt, abs_tol=1e-12)
    checks = {'R04_STRUCTURED': {'power':p, 'tc_mean_global_lower_bound':low,
        'hdl_mean_global_upper_bound':high, 'nonhdl_variance_at_reference':vn,
        'nonhdl_hdl_log_correlation':rn, 'reference_tc_variance':vt,
        'recovered_reference_tc_variance':vn+vh+2*(cov-vh),
        'reference_tc_hdl_covariance':cov,
        'interpretation':'Positive non-HDL mean over the complete fixed-spec support. Covariance preservation is at the hypothetical reference only.'}}
    s = spec('R06'); l=s['lipids']; mins=[]
    for j in range(3):
        vals=[]
        for a,b,f,g in itertools.product([18,85],[12,55],[0,1],range(3)):
            vals.append(l['base_mean'][j]+l['female_effect'][j]*f+l['male_effect'][j]*(1-f)+l['bmi_slopes'][j]*(b-22)+l['age_slopes'][j]*(a-38)+l['lifestyle_slopes'][j]*(g-.45))
        mins.append(min(vals))
    eig=np.linalg.eigvalsh(l['latent_residual_correlation']).tolist()
    assert min(mins)>0 and min(eig)>0
    checks['R06']={'component_mean_lower_bounds':mins,'latent_correlation_eigenvalues':eig}
    s=spec('R08'); mins_t=[]; mins_h=[]
    q=.6744897501960817
    for g in range(4):
        ls=math.log(s['bmi_iqr_upper'][g]/s['bmi_iqr_lower'][g])/(2*q)
        sd=s['bmi_reference_mean'][g]*math.sqrt(math.expm1(ls*ls))
        ts=[];hs=[]
        for a,b in itertools.product([18,90],[12,55]):
            ts.append(s['tc_reference_mean'][g]+s['tc_difference_per_donor_bmi_sd'][g]/sd*(b-s['bmi_reference_mean'][g])+s['age_log_derivative_tc']*s['tc_reference_mean'][g]*(a-s['reference_age']))
            hs.append(s['hdl_reference_mean'][g]+s['hdl_difference_per_donor_bmi_sd'][g]/sd*(b-s['bmi_reference_mean'][g])+s['age_log_derivative_hdl']*s['hdl_reference_mean'][g]*(a-s['reference_age']))
        mins_t.append(min(ts));mins_h.append(min(hs))
    assert min(mins_t+mins_h)>0
    checks['R08']={'tc_mean_lower_bounds':mins_t,'hdl_mean_lower_bounds':mins_h}
    s=spec('R10');l=s['lipids'];ts=[];hs=[]
    for a,b,f,g in itertools.product([18,90],[13,50],[0,1],range(3)):
        k='female' if f else 'male'
        ts.append(l['tc_reference_means'][g]+l['tc_effect_per_bmi_sd_'+k][g]/4*(b-s['bmi']['setting_reference_bmi'][g])+l['tc_age_slope']*(a-35)+l['tc_female_shift']*(f-.55))
        hs.append(l['hdl_reference_means'][g]+l['hdl_effect_per_bmi_sd_'+k][g]/4*(b-s['bmi']['setting_reference_bmi'][g])+l['hdl_age_slope']*(a-35)+l['hdl_female_shift']*(f-.55))
    lr=math.log1p(.3*.24*.28)/math.sqrt(math.log1p(.24**2)*math.log1p(.28**2))
    assert min(ts+hs)>0 and abs(lr)<1
    checks['R10']={'tc_mean_lower_bound':min(ts),'hdl_mean_lower_bound':min(hs),'log_correlation_for_raw_point3':lr}
    s=spec('R12');d={}
    for sex,p in s['sex_parameters'].items():
        bt=p['tc_difference_per_bmi_sd']/p['bmi_sd'];bh=p['hdl_difference_per_bmi_sd']/p['bmi_sd']
        hs=[];ns=[]
        for a,b in itertools.product([18,85],[12,55]):
            t=p['tc_mean']+bt*(b-p['bmi_mean'])+.015*(a-p['age_mean'])
            h=p['hdl_mean']+bh*(b-p['bmi_mean'])+.001*(a-p['age_mean'])
            hs.append(h);ns.append(t-h)
        cab=.2*p['age_sd']*p['bmi_sd']
        vmt=bt**2*p['bmi_sd']**2+.015**2*p['age_sd']**2+2*bt*.015*cab
        vmh=bh**2*p['bmi_sd']**2+.001**2*p['age_sd']**2+2*bh*.001*cab
        vh=p['hdl_sd']**2-vmh;vn=p['tc_sd']**2-vmt-vh
        assert min(hs+ns)>0 and min(vh,vn)>0
        d[sex]={'hdl_mean_lower_bound':min(hs),'nonhdl_mean_lower_bound':min(ns),'hdl_variance':vh,'nonhdl_variance':vn}
    checks['R12']=d
    return checks

PAIR = {
'R01': ('bounded_outputs', 'Age/BMI and both BP values are bounded by rejection; positive polynomial moments of delivered measurements are finite. Finite retry limits can still fail.', 'BP and pulse-pressure bounds are scenario restrictions, not universal clinical limits. No scientific law changed.', 'Shared centered-gamma/person and reading errors encode assumed dependence; source BMI slopes do not identify residual covariance.'),
'R02': ('finite_due_to_explicit_cap', 'Positive BMI exponent would be problematic without the implemented log caps [-30,30]; actual fixed implementation has bounded lipid outputs. Computational caps are not source-identified physiology.', 'Positivity is ensured, TC>=HDL is not structurally enforced. Separate noisy assays and ideal component concentrations are different interpretations.', 'Log-error correlation .35 and transport of log-linear slopes remain assumptions; log base and adjustment mismatch prevent exact source-operator equivalence.'),
'R03': ('bounded_outputs', 'Delivered age/BMI/BP are bounded; raw t7 innovations have limited high-order moments but output rejection bounds measurements.', 'BP is rounded before pair acceptance. Bounds are scenario choices.', 'Sex-specific SBP coefficients are taken from a secondary INTERSALT citation; the DBP conversion is approximate. Residual correlation .65 is assumed.'),
'R04': ('initial_infinite_positive_tc_moments_repaired', 'Initial TC contains exp(c*BMI), c>0, with shifted lognormal BMI; its ideal real-valued positive moments diverge. Both selected revisions remove that composition.', 'Generic revision preserves separate lipid measurements. Structured revision changes to idealized TC=HDL+positive non-HDL, enforcing component order with a new measurement assumption.', 'No externally identified target residual covariance was added. Structured component moment conversion preserves an assumed reference covariance only; latent town and nonlinear means affect requested OLS residuals.'),
'R05': ('bounded_outputs', 'Delivered BMI/BP are bounded despite cohort-level Gaussian slope draws. The finite rejection cap can fail for extreme scenarios.', 'Strict pre-rounding PP>10 may round to exactly10; not a proof of invalid delivered values under a >=10 rule.', 'Cohort-level slope/correlation draws encode scenario uncertainty, not validated transport uncertainty or ordinary sampling-only variability.'),
'R06': ('finite_positive_component_moments', 'Bounded covariates and strictly positive bounded component means times fixed-variance lognormal errors give finite positive polynomial moments. Scalar corner checks and correlation positive-definiteness pass.', 'TC is the sum of positive HDL, LDL and remnant concentrations.', 'Component log correlations and conditional CVs are assumed; component positivity does not identify the joint scientific association.'),
'R07': ('finite_moments_delivery_rounding_repaired', 'BMI has finite positive polynomial moments; bounded-age/sex mean terms and Gaussian BP innovations give finite measurement moments. Conditioning on the positive BP wedge preserves these moments at the fixed specification.', 'Initial continuous acceptance followed by half-unit rounding could trigger a delivery exception. Both revisions accept after rounding; generic retains100 retries, structured uses an unbounded loop with almost-sure but not bounded runtime.', 'Source group BP and pulse-pressure SDs yield a marginal covariance identity. Removing modeled covariate covariance relies on a normal-age/reference-sex approximation, not an observed age/sex/BMI-adjusted covariance.'),
'R08': ('finite_positive_lognormal_moments', 'Bounded covariates and positive bounded arithmetic means with fixed Gaussian log noise give finite positive polynomial moments; the numerical probability clip is not an infinite-tail defect.', 'TC>=HDL is not structurally guaranteed; assay-vs-component interpretation remains an assumption.', 'JHS .2235 is a log random-intercept correlation in longitudinal data, not a raw cross-sectional OLS residual correlation. Additional independent log errors and transport change its meaning.'),
'R09': ('bounded_outputs', 'Age/BMI and both BP outputs have bounded support. Rejection is not a deterministic runtime bound.', 'BP wedge and range restrictions are explicit modeling choices.', 'Schur-complement dependence uses a male midlife source matrix with varying pairwise sample sizes, then transports to a broader mixed-sex population. It is not an exactly matched target partial correlation.'),
'R10': ('finite_positive_lognormal_moments', 'Bounded covariates, positive bounded means and fixed lognormal noise give finite positive polynomial moments. The raw-to-log conditional correlation conversion is algebraically correct.', 'Positive TC/HDL separately; component ordering is not guaranteed.', 'Residual raw correlation .3 and source BMI SD4 are explicit assumptions; source standardized effects and multi-adjusted operators do not identify target age/sex-only slopes.'),
'R11': ('bounded_outputs', 'All delivered numeric measurements have bounded support; rejection and rounding remain the implementation.', 'Ranges and pair bounds are scenario restrictions.', 'Male/female matrices are read from the correct upper/lower triangles and partialed algebraically. Rounded source matrices and demographic/measurement transport remain unresolved.'),
'R12': ('finite_positive_gamma_component_moments', 'Bounded covariates and positive component means/variances imply finite positive polynomial gamma-mixture moments. Fixed-spec corner checks pass; marginal optimizer convergence is an operational requirement.', 'TC=HDL+non-HDL with both components positive.', 'Independent conditional gamma components imply covariance via the shared HDL component. Standardized source effects are scaled by synthetic BMI SD, and latent copula correlation approximates raw covariance; neither is directly source-identified.')
}

SOURCE = [
('PMC5344187','Abstract; statistical analysis','Mexico BMI SD4.5 and approximately3/2 mmHg perSD adiposity associations are supported. Exact target age/sex-only coefficient equivalence is not established.'),
('PMC4514940','Background INTERSALT citation','Sex-specific SBP .91/.72 is a secondary citation of INTERSALT. It does not report the adopted DBP conversion.'),
('PMC6324286','Results regression coefficients; methods','BMI coefficients1.15/.75 are supported with broader adjustment and restricted source BMI range. Transfer to the requested operator remains an assumption.'),
('PMC6435188','Table1 and footnote','Maasai sex-specific BMI and lipid means and SDs are supported; these are marginal summaries and contain no joint covariance.'),
('PMC6897412','Tables2/4 and adjustment footnotes','Tanzanian weighted geographic lipid means and categorical HDL/LDL associations are supported. CIs are not SDs and category contrasts are not continuous BMI coefficients.'),
('PMC6747887','Tables2/3 and footnotes','BMI values used are age-standardized means. Lipid BMI effects are per source BMI SD and adjusted for more than age/sex; exact source SD is not supplied by the extracted effect table.'),
('PMC7713018','Table2; joint longitudinal model methods','The .2235 TC-HDL correlation concerns log random intercepts. Reported random-effect and error SDs are distinct; this is not a raw cross-sectional residual correlation.'),
('PMC4768573','Table2 and measurement methods','Upper triangle gives unadjusted male-source correlations; pairwise sample sizes vary. The Schur transform is algebraically usable but not a verified common-complete-case target partial correlation.'),
('PMC4563590','Table2 and footnote; cohort age description','Upper triangle male/lower triangle female interpretation is supported. Full transport of the resulting partial correlations and exact measurement matching were not certified.'),
('PMC6024610','Table2 and footnote','Four dairy-group BP and pulse-pressure means/SDs support pooling and the variance identity. Source sex counts include an internal inconsistency; the generator uses reported percentages. Residual subtraction is assumption-dependent.'),
('PMC6261546','Tables4/5 and analysis methods','Log-transformed lipid associations differ between univariate and multivariable models. The logarithm base and target age/sex-only coefficient are not established by this extraction.'),
('PMC6005143','Table1','BMI medians and IQRs match the adopted IQRs. Combining these shapes with overlapping-study means is an approximation, not an independent covariance source.'),
('PMC13629051','Methods; Tables2/3; limitations','New Uganda study uses imputation and survey-weighted multivariable categorical BMI contrasts for TC. It explicitly did not measure HDL/LDL. Its categorical TC evidence supplies context, not a target continuous slope or TC-HDL covariance.')
]

def main():
    inv=load(R/'review/CODE_SOURCE_INVENTORY.json')
    closure=load(R/'CONSTRUCTION_CLOSURE.json')
    assert len(inv['rows'])==24 and closure['all_episodes_closed']
    assert inv['construction_closure_sha256']==sha(R/'CONSTRUCTION_CLOSURE.json')
    checks=scalar_checks()
    rows=[]
    for x in inv['rows']:
        cls,mathnote,phys,joint=PAIR[x['pair_id']]
        changes='Retained original scientific artifacts. A review may identify uncertainty without altering the law.'
        if x['pair_id']=='R04':
            changes=('TC conditional mean changed from positive exponential BMI to a positive affine BMI factor; local reference derivative preserved, global associations not guaranteed preserved.' if x['arm']=='generic_review' else 'TC mean changed to a BMI power law; positive HDL/non-HDL decomposition added, preserving an assumed hypothetical reference covariance but changing the joint distribution.')
        if x['pair_id']=='R07':
            changes=('Rounding moved before BP-pair acceptance; the100-attempt cap remains.' if x['arm']=='generic_review' else 'Rounding moved before BP-pair acceptance and the100-attempt cap removed; almost-sure acceptance does not bound execution time.')
        # Arm names are verified from actual episode ID, avoiding prose aliases.
        if x['pair_id']=='R04' and x['episode_id'].endswith('_GENERIC'):
            changes='TC conditional mean changed from positive exponential BMI to a positive affine BMI factor; local reference derivative preserved, global associations not guaranteed preserved.'
        if x['pair_id']=='R07' and x['episode_id'].endswith('_GENERIC'):
            changes='Rounding moved before BP-pair acceptance; the100-attempt cap remains.'
        rows.append({k:x[k] for k in ['episode_id','pair_id','arm','case_id','selected_candidate','initial','final','changed']} | {
            'mathematical_classification':cls,'mathematical_review':mathnote,
            'physiological_review':phys,'joint_relation_review':joint,'actual_change':changes,
            'review_receipt_bindings':[{'path':c['path'],'sha256':c['sha256'],'candidate_id':c['candidate_id']} for c in x['review_contracts']],
            'source_accuracy_scope':'Primary requested-variable passages checked; every auxiliary claim and version not exhaustively recertified.',
            'target_transport_certified':False,'clinical_improvement_assessed':False})
    sources=[]
    for sid,locator,note in SOURCE:
        matches=sorted(R.glob(f'imports/*/sources/{sid}.v1.xml'))
        if sid=='PMC13629051':
            matches=[R/'episodes/R04_STRUCTURED/gateway/session/approved/7bdbc1ce941a82c5f504c6de6bdc4c294314bd3422147e0275d6b6f2f19b7974.xml']
        assert matches and matches[0].exists(),sid
        p=matches[0]
        sources.append({'source_id':sid,'inspected_file':p.relative_to(R).as_posix(),'sha256':sha(p),'locator':locator,'finding':note,
          'limitation':'This bounded passage check does not certify all auxiliary claims, all captured versions, or transport to the target.'})
    findings=[
      {'id':'CS01','severity':'scientific_repair_confirmed','episodes':['R04_GENERIC','R04_STRUCTURED'],'finding':'Both arms independently removed the initial positive-exponential-of-lognormal TC tail defect. The sample can look normal while the ideal law has divergent moments; finite trial statistics were not used as proof.'},
      {'id':'CS02','severity':'implementation_repair_confirmed','episodes':['R07_GENERIC','R07_STRUCTURED'],'finding':'Both arms fixed acceptance before rounding, which could otherwise abort delivery of a valid continuous BP pair after rounding. Existing checks raised on invalid output; this was not silent delivery of invalid rows.'},
      {'id':'CS03','severity':'modeling_tradeoff','episodes':['R07_STRUCTURED'],'finding':'Removing the retry cap removes that finite retry failure but introduces unbounded theoretical loop duration; almost-sure termination is not a runtime bound.'},
      {'id':'CS04','severity':'measurement_assumption_change','episodes':['R04_STRUCTURED'],'finding':'Component addition guarantees TC>HDL for idealized concentrations. It changes the measurement/joint model and does not establish that separate noisy assays must always satisfy this order.'},
      {'id':'CS05','severity':'source_wording_defect','episodes':['R04_STRUCTURED'],'finding':'The HDL source-operator text says Tanzania/Uganda. The cited numerical HDL contrasts are Tanzanian (PMC6897412); newly fetched Uganda PMC13629051 measured TC only. No Ugandan HDL coefficient is supported. Retain the frozen wording and report the defect; do not repair it after seeing results.'},
      {'id':'CS06','severity':'conservative_rule_not_confirmed_defect','episodes':['R01_GENERIC'],'finding':'The contract weakens PP>=15 to14.9 citing rounding. Ideal common-grid nearest rounding with a15-unit offset does not establish that loss. No actual scientific code change occurred. This warning is not counted as a proven defect.'},
      {'id':'CS07','severity':'provenance_namespace_limitation','episodes':['R03_GENERIC'],'finding':'A search-hit identifier for an INTERSALT abstract is not a registered full-text PMC source. Availability-only binding must not be read as original full-text verification or citation fabrication.'},
      {'id':'CS08','severity':'interpretation_limit','episodes':[x['episode_id'] for x in rows],'finding':'Declared reported/derived/assumed labels and source IDs improve inspectability but do not certify extraction, adjustment-set equivalence, source applicability, or transport. Current joint relationships remain assumed or derived under unverified transport/model assumptions.'},
      {'id':'CS09','severity':'not_a_defect','episodes':['R02_GENERIC','R02_STRUCTURED','R08_GENERIC','R08_STRUCTURED'],'finding':'An exp or clip AST pattern alone is insufficient. R02 actual log caps make moments finite, albeit arbitrary; R08 probability clipping does not make its bounded-covariate lognormal law divergent.'}
    ]
    report={'schema_version':'code_source_change_audit_v1','status':'complete_with_documented_scientific_limitations',
      'created_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'independent_review_agent',
      'construction_closure_sha256':sha(R/'CONSTRUCTION_CLOSURE.json'),'plan_sha256':sha(R/'PLAN.json'),
      'audit_plan_sha256':sha(R/'review/CODE_SOURCE_AUDIT_PLAN.json'),
      'inventory_sha256':sha(R/'review/CODE_SOURCE_INVENTORY.json'),
      'collector_sha256':sha(R/'review/collect_code_source_audit.py'),
      'audit_script_sha256':sha(Path(__file__)),
      'target_comparisons_inspected':False,'final_generated_rows_read':False,
      'candidate_programs_executed':False,'new_external_fetches':0,
      'historical_context':'Reviewer knows historical project references. This is current-run source/code-only review, not a claim of personal blinding.',
      'scope':'All12 initial code/spec/notes and four selected code/spec revisions; all24 selected review declarations. Bounded requested-variable/source-operator audit; auxiliary citations and scientific transport not exhaustively certified.',
      'moment_scope':'Positive polynomial moments of fixed-spec ideal measurement distributions. Not all inverse moments, arbitrary mutated specifications, finite-sample inverse-design OLS moments, floating-point extremes, or formal theorem certification by the checker.',
      'counts':{'pairs':12,'branches':24,'retained_original':20,'revised':4,'unique_primary_source_passage_checks':13},
      'rows':rows,'scalar_parameter_checks':checks,'source_passage_checks':sources,'findings':findings,
      'decision':'Proceed to the frozen numerical comparison without further model edits. Scientific utility, before/after changes, and physiological observed counts have not been assessed in this audit.',
      'nonclaims':['No conclusion that structured review improves scientific analysis quality.','No conclusion that every source claim is correct or transportable.','No new empirical conditional-dependence constraint was established for the revised laws.','Retention does not mean the Agent found no limitations; revision does not by itself establish practical benefit.']}
    out=R/'review/CODE_SOURCE_CHANGE_AUDIT.json'
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
    lines=['# Code/source-only audit before clinical evaluation','',
      'All24 episodes were closed before this review. No current final table, clinical comparison, or evaluation was opened. Historical references were already known to the reviewer.','',
      '| Pair | Selected changes | Mathematical / physiological finding | Joint-evidence limitation |','|---|---|---|---|']
    for pair,(cls,m,p,j) in PAIR.items():
        change='Both arms retain v000' if pair not in ['R04','R07'] else ('Both revise TC tail; structured also adds components' if pair=='R04' else 'Both revise rounding acceptance; structured removes retry cap')
        lines.append(f'| {pair} | {change} | {m} {p} | {j} |')
    lines += ['', 'The two substantive changes are a tail-law repair (R04) and an output-delivery repair (R07). Their practical effects require the locked numerical evaluation. The structured arm did not obtain a new identified residual-covariance constraint. R04 structured also changes the interpretation to idealized component concentrations.','',
      'The review records a minor Tanzania/Uganda HDL wording error, a conservative unproven rounding warning in R01 generic, and a search-hit/full-text provenance distinction in R03 generic. None authorizes post-result model editing. All unresolved extraction, transport and parameter uncertainty remain visible.','',
      'Scalar bounds and covariance checks, inspected source paths/hashes, all24 artifact bindings, and all findings are in CODE_SOURCE_CHANGE_AUDIT.json. Patient/generated rows and third-party full text are not reproduced here.']
    with (R/'review/CODE_SOURCE_CHANGE_AUDIT.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    print(json.dumps({'status':report['status'],'path':str(out),'sha256':sha(out),'pairs':12,'branches':24,'target_comparisons_inspected':False}))

if __name__=='__main__':main()

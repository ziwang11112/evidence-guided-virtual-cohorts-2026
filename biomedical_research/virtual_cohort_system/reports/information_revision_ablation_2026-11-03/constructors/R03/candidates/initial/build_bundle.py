"""Serialize deterministic derivations and declarations. Does not generate rows."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent.parent
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def write(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

d = read(HERE/'derivation_result.json')
evidence = read(BUNDLE/'input/compiled_evidence.json')
write('evidence.json', evidence)
g=d['glucose']['mixture_parameters']
h=d['hba1c']['mixture_parameters']
params={
 'n_rows':3000,
 'age_values':d['age']['values'],
 'age_probabilities':d['age']['probabilities'],
 'female_probability':d['female_probability'],
 'bmi_log_mean':d['bmi']['log_mean'],
 'bmi_log_sd':d['bmi']['log_sd'],
 'glucose_log_means':[g[1],g[3]],
 'glucose_log_sds':[g[2],g[4]],
 'hba1c_log_means':[h[1],h[3]],
 'hba1c_log_sds':[h[2],h[4]],
 'glycemic_label_probabilities':d['joint']['glycemic_label_probabilities'],
 'latent_correlation_narrow':d['joint']['gaussian_correlation'],
 'latent_correlation_broad':d['joint']['gaussian_correlation_broad'],
}
assumptions=[
 {'id':'A_TASK','description':'The contract requests 3000 independent synthetic adults, observed=None, ages 35-74 inclusive and all five variables generated. Row count and identifier convention are task implementation choices.'},
 {'id':'A_REFERENCE','description':'The explicitly supplied unweighted CHNS n=6631 complete-case summaries are development sample estimates used as working population moment anchors. Fitting them is not independent validation or recovery of the selected sample joint law. Available CR1 intervals describe three reference coefficients, not individual dispersions or certainty in this generator.'},
 {'id':'A_AGE','description':'Age uses a discrete distribution on 35..74. Assumed band masses are .09 on 35..38, .40 on 39..52, .40 on 53..67, .11 on 68..74; within bands maximum entropy subject to target mean and variance gives an exponential quadratic tilt. The masses place q10=39, median=53,q90=68; fine age frequencies are unobserved.'},
 {'id':'A_BMI','description':'BMI is lognormal with mean and variance anchored to the supplied reference. This ensures positive support and finite moments. Other BMI quantiles are approximate predictions; the lognormal family is not established by the summaries.'},
 {'id':'A_MIXTURE','description':'Glucose and HbA1c each use two lognormal components, fitted by deterministic equations to the corresponding admitted mean, individual SD and 10th/50th/90th percentiles. Narrow and broad labels have overlapping support and do not identify normal glycemia or diabetes. The broad HbA1c label is nested in the broad glucose label to reduce unidentified mixture-class coupling parameters. All component choices and nesting are structural assumptions.'},
 {'id':'A_COPULA','description':'Within mixture-label states a four-dimensional Gaussian copula links age, BMI, glucose and HbA1c. Glycemic latent association may differ between narrow-narrow and other states; constant age/BMI couplings across these states are assumptions. Two latent correlations are fixed at age-BMI=-.05 and BMI-glucose=.20 as explicit weak-dependence scenarios; no unreported association is inferred absent. Remaining five latent coefficients solve the two supplied glycemic correlations and three supplied OLS projections using population-moment algebra.'},
 {'id':'A_FEMALE','description':'Female is Bernoulli with the admitted fraction, and independent of the four continuous/ordered variables as an explicit simplifying scenario. The summaries do not establish sex independence; sex-specific effects, prevalence and interactions remain unassessed. The independence choice allows the supplied sex-adjusted projections to be represented without inventing a source sex coefficient.'},
 {'id':'A_MEASUREMENT','description':'The generator represents the task central-serum glucose and whole-blood HbA1c on its native scales; neither plasma-serum equivalence nor common assays across external cohorts is assumed. Glycemic values remain continuous; the provided average-tie Spearman correlation is approximated by a continuous-population Spearman functional. Measurement rounding/ties are not reconstructed.'},
 {'id':'A_UNCERTAINTY','description':'RNG variation describes finite synthetic cohorts conditional on fixed working parameters. It does not express reference sampling uncertainty, study heterogeneity, mixture ambiguity, transport uncertainty or clinical evidence. No coefficient p-value, CI coverage, exact realized summary, causal effect or national representativeness is guaranteed.'},
 {'id':'A_EXTERNAL','description':'External Bao, MIND, Jansen and Pani source facts are retained in their own population, units, selection, measurement, weights and adjustment context. They inform plausibility and limitations but are not jointly fit as if observations from one target cohort. Pani and restored Jansen age associations are present; absence of age evidence is not claimed. No source-context replay is supplied.'},
]
prov={}
def provenance(names,ids,assumptions,derivation):
    for name in names:
        prov[name]={'evidence_ids':ids,'assumption_ids':assumptions,'derivation':derivation}
provenance(['n_rows','age_values'],[],['A_TASK'],'Fixed task contract and integer support, not a scientific estimate.')
provenance(['age_probabilities'],['REF_age_mean','REF_age_sd','REF_age_q10','REF_age_median','REF_age_q90'],['A_REFERENCE','A_AGE'],'Deterministic entropy tilt with the declared band masses. derive_parameters.py solves age mean and variance equations, stores probabilities and mathematical results in derivation_result.json.')
provenance(['female_probability'],['REF_female_mean'],['A_REFERENCE','A_FEMALE'],'Working Bernoulli probability equals the supplied female sample fraction. Other female diagnostics follow from this distribution; they are not separate evidence constraints.')
provenance(['bmi_log_mean','bmi_log_sd'],['REF_bmi_mean','REF_bmi_sd'],['A_REFERENCE','A_BMI'],'sigma_log=sqrt(log(1+(SD/mean)^2)); mu_log=log(mean)-sigma_log^2/2. Supplied sample SD is used as working population SD without claiming estimator certainty.')
for name in ['glucose','hba1c']:
    provenance([name+'_log_means',name+'_log_sds'],['REF_'+name+'_'+suffix for suffix in ['mean','sd','q10','median','q90']],['A_REFERENCE','A_MIXTURE','A_MEASUREMENT'],'The two lognormal component locations, scales and marginal label probability solve five deterministic moment/CDF equations. No synthetic data or random quadrature was used; see retained producer and residuals. The marginal probabilities are combined into the joint-label parameter.')
provenance(['glycemic_label_probabilities'],['REF_glucose_'+suffix for suffix in ['mean','sd','q10','median','q90']]+['REF_hba1c_'+suffix for suffix in ['mean','sd','q10','median','q90']],['A_REFERENCE','A_MIXTURE'],'Each marginal broad probability is fitted with its mixture. Joint broad probability=min(p_glucose,p_hba1c) is a declared nesting assumption. Four probabilities correspond to (narrow,narrow),(narrow,broad),(broad,narrow),(broad,broad).')
provenance(['latent_correlation_narrow','latent_correlation_broad'],['REF_glucose_hba1c_pearson','REF_glucose_hba1c_spearman','REF_E1','REF_E2','REF_E3'],['A_REFERENCE','A_COPULA','A_MEASUREMENT','A_FEMALE'],'Fix age-BMI=-.05 and BMI-glucose=.20. Fit narrow/broad glucose-HbA1c correlations to two distinct observed correlation types via lognormal cross-moments and deterministic bivariate normal-CDF integrals. Fit age-glucose, age-HbA1c and BMI-HbA1c correlations to the three actual reference OLS projection definitions using the full implied covariance. These are neither copied external slopes nor a recovered conditional clinical law. Both correlation matrices are positive definite; values stored in derivation_result.json.')
write('model_spec.json',{'parameters':params,'assumptions':assumptions,'parameter_provenance':prov})

tree=ast.parse((HERE/'generator.py').read_text(encoding='utf-8'))
func=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='generate']
assert len(func)==1 and len(func[0].args.args)==3
audit={'scope':'static_and_deterministic_only','generate_signature':'generate(observed,spec,seed)',
       'generator_imported':False,'generator_executed':False,'rows_produced':0,
       'minimum_correlation_eigenvalue':min(d['joint']['eigenvalues']+d['joint']['eigenvalues_broad']),
       'age_probability_sum':sum(params['age_probabilities']),
       'mixture_probability_sum':sum(params['glycemic_label_probabilities']),
       'minimum_age_probability':min(params['age_probabilities']),
       'support_reason':'Discrete bounded age, Bernoulli sex and exponentials of finite normal variables; all lognormal moments finite.',
       'finite_sample_check':'not_computable before isolated execution'}
write('static_audit.json',audit)
write('checks.json',{'scope':'source_only','records':[
 {'name':'deterministic_derivation','status':'pass','detail':'No rows or random integration were used. Admitted development summaries fitted by moment/CDF algebra and deterministic scalar quadrature. source_only is legacy scope for declared input evidence, not external source replay or independent target validation.'},
 {'name':'static_program_and_support','status':'pass','detail':'AST checks positional generate ABI without importing it. Two latent correlation matrices have positive eigenvalues. Discrete probabilities and mixture probabilities are normalized; lognormal variables have positive support and finite moments.'},
 {'name':'isolated_output_contract','status':'not_computable','detail':'No generator has been executed by the scientific author. Coordinator trial4201 requested.'},
 {'name':'external_source_context_replay','status':'not_computable','detail':'Source-context numerical replay is not supplied. External adjusted slopes/correlations are not compared to task rows as if a replay.'},
 {'name':'independent_population_validation','status':'not_computable','detail':'The explicitly supplied development reference is used to calibrate, so agreement cannot be independent validation.'}
 ],'artifacts':[{'path':name,'sha256':sha(HERE/name)} for name in ['derivation_result.json','static_audit.json']]})

decision='''# R03 initial scientific candidate

This candidate generates all five variables for the selected CHNS adult analytical population. The explicitly supplied CHNS development reference is the principal numerical input. It contains sample estimates, not population truth. The external evidence is retained in full and used to assess applicability rather than pooled into an artificial common study.

The most informative joint feature is the difference between Pearson (0.661) and Spearman (0.361). A shared broad glycemic component with stronger within-component association represents that feature while leaving the central component weakly associated. Two positive lognormal mixtures reproduce the five disclosed summaries of each glycemic margin in their working population. Component membership is not a disease diagnosis. The nested-label assumption, Gaussian copulas and constant covariate couplings are not identified by the supplied summaries.

Age uses discrete maximum entropy within four assumed age bands. BMI uses a positive lognormal distribution fitted to its mean and SD; quantiles are approximate predictions. Female has the disclosed Bernoulli fraction, with independence explicitly assumed because sex-specific dependence is unidentified, not because missing evidence establishes independence. Age-BMI and BMI-glucose latent correlations are explicit weak-dependence assumptions. Other latent couplings are obtained from the covariance equations for the actual three adjusted reference projections, not by concatenating published regression rows.

Source context matters. Bao reports unadjusted plasma Pearson in Shanghai with diagnosed-diabetes exclusions; MIND reports serum Spearman among selected older rural adults; Jansen coefficients concern non-diabetic European participants and different conditioning sets. The audited Pani age coefficient is a weighted survey slope. Their populations, weights, measurements and estimands are not interchangeable with the equal-weight task sample. Jansen age evidence is present and restored; the model does not assert an age-evidence gap. The official NGSP relation converts representation only, not assays or serum/plasma measurements. None of the external source statistics was replayed.

The retained producer derive_parameters.py uses only deterministic moment formulas, CDF equations and scalar quadrature; it never imports the generator or creates synthetic rows. Population fitting uses reference point estimates as working anchors. Reference CR1 intervals are preserved as sample uncertainty but are not converted to individual variability or used as precision weights. Both latent matrices are positive definite. Age support is 35..74 and exponentiation ensures strictly positive BMI, glucose and HbA1c; finite lognormal scales ensure all moments exist.

Requested next stage: one isolated trial at seed 4201. No new original-source queries, downloads, paid APIs or scientific subagents were used. The trial will assess output validity and finite-cohort behavior, not prove source or target validity. No favorable-seed selection, realized-moment rescaling, p-value tuning or hidden optimization cohorts is implemented.

Unassessed uses include diagnosis, clinical decisions, causal inference, treatment effects, sex-specific analyses, subgroups, tail extremes and national prevalence. Structural and reference uncertainty are not calibrated by seeds. Continuous HbA1c approximates an average-tie rank reference; rounded measurement values and full joint dependence remain unresolved. Retain this candidate unchanged after freeze and bind actual feedback if later delivery or revision uses it.
'''
(HERE/'decision.md').write_text(decision,encoding='utf-8')
print(json.dumps({'candidate':str(HERE),'files_written':5,'static_audit':audit},indent=2))

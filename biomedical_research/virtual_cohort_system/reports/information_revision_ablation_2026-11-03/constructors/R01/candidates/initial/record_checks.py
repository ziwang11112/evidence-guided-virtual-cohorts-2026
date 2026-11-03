"""Static inspection and report binding only; never imports generator.py."""
from pathlib import Path
import ast
import hashlib
import json
import numpy as np

here=Path(__file__).resolve().parent
tree=ast.parse((here/"generator.py").read_text(encoding="utf-8"))
functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=="generate"]
assert len(functions)==1
args=functions[0].args
assert len(args.posonlyargs)+len(args.args)==3 and not args.vararg and not args.kwarg and not args.kwonlyargs
assert all(isinstance(node,(ast.Expr,ast.Import,ast.ImportFrom,ast.FunctionDef)) for node in tree.body)
imports=[node.names[0].name for node in tree.body if isinstance(node,ast.Import)]
assert imports==["numpy","pandas"]
spec=json.loads((here/"model_spec.json").read_text(encoding="utf-8"))
p=spec["parameters"]
assert p["n_rows"]==3000
assert p["age_distribution"]["values"]==list(range(35,75))
assert np.all(np.asarray(p["age_distribution"]["probabilities"])>0)
assert abs(sum(p["age_distribution"]["probabilities"])-1)<1e-12
assert np.all(np.asarray(p["mixture_indicator_probabilities"])>=0)
assert abs(sum(p["mixture_indicator_probabilities"])-1)<1e-12
eigenvalues=[]
chol_errors=[]
for matrix,chol in zip(p["component_latent_correlations"],p["component_latent_cholesky"]):
    matrix=np.asarray(matrix)
    chol=np.asarray(chol)
    eigenvalues.append(float(np.linalg.eigvalsh(matrix).min()))
    chol_errors.append(float(np.max(np.abs(chol@chol.T-matrix))))
assert min(eigenvalues)>0 and max(chol_errors)<1e-12
report={"status":"pass","scope":"Static AST inspection and deterministic parameter algebra only; generator body not imported or executed",
        "abi_arguments":[a.arg for a in args.posonlyargs+args.args],"imports":imports,
        "n_rows_declared":p["n_rows"],"age_support":[35,74],
        "min_eigenvalue_by_component":eigenvalues,"cholesky_reconstruction_max_errors":chol_errors,
        "output_contract_runtime_status":"not_computable before isolated execution",
        "local_generated_rows":0}
(here/"static_check_report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
artifact_names=["static_check_report.json","fit_report.json","fit_report_common_rho_diagnostic.json"]
checks={"scope":"source_only","records":[
    {"name":"declared_input_evidence_scope","status":"pass","detail":"Legacy source_only means only the declared assigned evidence was used, including the explicitly supplied CHNS development reference. It does not mean independent target validation. fit_report.json names the source and reports zero retrieval."},
    {"name":"static_program_contract","status":"pass","detail":"Parsed generator AST without import/execution; verified one synchronous three-argument generate, numpy/pandas imports, and task row/support parameter declarations. Bound static report. Output validity remains unexecuted."},
    {"name":"deterministic_distribution_algebra","status":"pass","detail":"Analytic moments/CDFs and OLS covariance projections computed; all four component correlations are positive definite with verified Cholesky reconstruction. Rank integral checked at 64x64 versus 96x96 quadrature. Results are fitted development constraints, not independent evidence validation."},
    {"name":"earlier_common_rho_model_diagnostic","status":"fail","detail":"A pre-trial analytic common-rho model could not jointly reproduce the two supplied glycemic correlations. Its script/report are retained. The submitted generator uses component-specific rho; no synthetic rows were involved in either calculation."},
    {"name":"source_context_replay","status":"not_computable","detail":"No source-population simulator/execution adapter is supplied for this task. Target generation is not a replay of differently selected external studies."},
    {"name":"generated_table_validity_and_diagnostics","status":"not_computable","detail":"No local sampling, generator import or execution occurred. Request coordinator isolated trial seed4201 after freezing."}
],"artifacts":[{"path":name,"sha256":hashlib.sha256((here/name).read_bytes()).hexdigest()} for name in artifact_names]}
(here/"checks.json").write_text(json.dumps(checks,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))

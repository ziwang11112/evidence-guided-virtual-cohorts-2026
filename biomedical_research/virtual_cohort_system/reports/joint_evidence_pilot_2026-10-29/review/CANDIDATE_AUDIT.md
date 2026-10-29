# Independent candidate source/scientific audit

Verdict: **PASS for source fidelity and static scientific implementation. No unresolved blocker in the reviewed final files.** This verdict does not establish source-to-target validity or execution correctness.

The final candidate represents a source-informed structural hypothesis. All 30 Tromso joint ratios, 28 confidence intervals, reference conventions, dimensionless units and exact DOCX row locators match direct native-table extraction. Sex 1/2 correctly indexes male/female; the parameter array is sex x ascending age x ascending BMI. All inherited numeric parameter groups remain identical to baseline.

The two substantive pre-final issues were resolved: the initial overlay was replaced with a formula that removes inherited log nonseparability, and geometric/arithmetic ratio equality is now restricted to the legacy_proxy scale before the nonzero-intercept assay mapping. No source value was changed.

Let g be the unchanged positive baseline mean, a0=44.5 and b0=22.5, and let D be the bilinearly interpolated/clamped source log cross-ratio. The final implementation is

`m(a,b) = g(a,b0) * g(a0,b) / g(a0,b0) * exp(D(a,b))`.

Since D is zero on either reference line, the corresponding g curves are preserved. Taking the within-sex cross-ratio cancels the separable g terms and gives `m(a,b)m(a0,b0)/(m(a,b0)m(a0,b)) = exp(D(a,b))`. At the assumed knots D is the source category contrast; treating that categorical contrast as a pointwise curve is an explicit bridge assumption. The code does not claim to reproduce the complete source ratio table, and the affine unblanked assay transformation does not preserve this cross-ratio.

The interval search and weights correctly handle interior cells and clamped endpoints. The source surface is continuous with derivative changes at knots; source categories do not establish the chosen representative values, within-bin paths or global continuation. Shared-reference covariance, source adjustment ambiguity, nonfasting transport, residual variance and between-population transfer remain unresolved and are declared as such.

Static AST comparisons confirmed that the positive-mean arithmetic, residual-noise construction and assay function are inherited unchanged. The program has no target lookup, identifier/cohort/count-conditioned mean, optimizer or fit loop. The candidate remains labelled partial for all three intended analytical uses. Repeated draws would not quantify source/transport uncertainty.

Checks performed were direct-source XML/JSON comparisons, parameter equality, AST comparison, complete mathematical inspection of final generator, and review of model/decision/analysis evidence text. No scientific code was imported or executed. No target/custody/execution artifacts or prior scientific result reports were inspected. Historical source-statistic narrative embedded in the allowed baseline specification was not used for a new scientific choice. Controller/release history and runtime checks were not audited.

## Reviewed-file hashes

| File (relative to experiment root) | SHA256 |
|---|---|
| agent_bundle/candidates/joint_evidence/generator.py | `34f6c249f7c43b3b8c56d131e2169c8c1f93642c5296039e4d9076c29193bc52` |
| agent_bundle/candidates/joint_evidence/model_spec.json | `d3b2aaa4f2d0a45f81ab35ed6d076bb9d240b0bac7600b7956f9dfe0c88c8f03` |
| agent_bundle/candidates/joint_evidence/evidence.json | `7871d3c90b2c85508235685aa062ab38c7fc3ed328d87c5060ab9c505709a22f` |
| agent_bundle/candidates/joint_evidence/decision.md | `0faffde853aa56354316ffbc0d4a1d74415d7b5e3c4a201253daa4b7779ac895` |
| agent_bundle/candidates/joint_evidence/analysis_evidence.json | `cf3cb1cf8b51b4d935caf7cf835ae85d5bbc1323516ee18e987c10930bcfc5cc` |
| agent_bundle/candidates/baseline/generator.py | `5f22ad4016e615004d8f9dcd09d9f5f51c005817f2730fe019d26eb58488110e` |
| agent_bundle/candidates/baseline/model_spec.json | `5c6206743b3dabe9b320a6fdf9016529cfb647790c1e22b16745e939621a8c3a` |
| agent_bundle/task.json | `613d72d4f3ca9623418fc1698af3728a732a64c3463aae3347c65d924acdda16` |
| agent_bundle/sources/Mikkelsen2023_Table_1.DOCX | `14b0f6ddecd322bab4ea51220599008156599e9587e9f6b001eadcbbb640536c` |
| agent_bundle/sources/PMC10308115.1.json | `dcee21e1745ed31c198849f74cdc2388a77fc0c2b09894d04f3c2c37b676e7ad` |
| agent_bundle/sources/PMC10308115.xml | `355fcfba74eadffcd1f1bab80983570d98c207f39b27a857a809ecb010a17d23` |

The JSON audit records per-file scope, individual checks and excluded work. `SOURCE_TABLE_STATIC_CHECK.json` contains all 30 row-level checks.

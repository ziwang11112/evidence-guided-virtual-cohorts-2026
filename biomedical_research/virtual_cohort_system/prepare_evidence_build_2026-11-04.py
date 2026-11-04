"""Prepare a new reviewed-evidence construction; never specify scientific parameters."""
from pathlib import Path
import hashlib, json, shutil
from cohort_harness.request_intake import prepare_request

P = Path(__file__).resolve().parent
W = P.parents[1]
S = W / 'evcGap01'
B = W / 'evcBuild01'
R = P / 'work/evidence_to_generation_2026-11-04'
R.mkdir(exist_ok=False)
def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

task = json.loads((S / 'task.json').read_text(encoding='utf-8'))
task['task_id'] = 'reviewed-evidence-construction-2026-11-04'
task['budget'] = {'source_queries': 0, 'source_downloads': 0, 'revisions': 1}
task['information_policy']['allowed_tools'] = []
request = {'schema_version': 1, 'purpose': 'Generate a complete virtual biomedical cohort from the independently searched/reviewed evidence packet and target description, for the declared scientific analyses. No individual observations are supplied.',
           'analyses': ['Primary: hba1c ~ 1 + bmi + glucose + age + female', 'Secondary: hba1c ~ 1 + bmi + age + female; marginal distributions and Pearson/Spearman relations'], 'task': task}
prepare_request(request, B)
(B / 'reviewed_evidence').mkdir()
registry = []
copied = []
old_registry = json.loads((S / 'registry.json').read_text(encoding='utf-8'))
for entry in old_registry['artifacts']:
    if entry['source_id'].startswith('search-'): continue
    source = S / entry['path']; dest = B / entry['path']
    assert sha(source) == entry['sha256']
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    registry.append(entry)
    copied.append({'path': entry['path'], 'sha256': sha(dest), 'provenance': 'byte copy of independently reviewed gateway original; not a new download'})
rel = 'sources/web/jansen_2013_wiley_web_render.txt'
(B / 'sources/web').mkdir()
shutil.copyfile(S / rel, B / rel)
registry.append({'source_id': 'Jansen2013', 'path': rel, 'sha256': sha(B / rel), 'origin': 'curator', 'screening': 'approved'})
copied.append({'path': rel, 'sha256': sha(B / rel), 'provenance': 'Controller admission following independent publisher-original review; partial web rendering. Not gateway approval.'})
write(B / 'registry.json', {'artifacts': registry})
for name in ['EVIDENCE_CANDIDATES.json', 'EVIDENCE_REPORT.md']:
    shutil.copyfile(S / 'reports' / name, B / 'reviewed_evidence' / name)
shutil.copyfile(P / 'work/gap_search_2026-11-04/EVIDENCE_INDEPENDENT_REVIEW.md', B / 'reviewed_evidence/INDEPENDENT_REVIEW.md')
admission = {'kind': 'reviewed_source_packet_handoff', 'sources': copied,
             'review_sha256': sha(B / 'reviewed_evidence/INDEPENDENT_REVIEW.md'),
             'evidence_ledger_sha256': sha(B / 'reviewed_evidence/EVIDENCE_CANDIDATES.json'),
             'scope': 'Source-specific reported evidence admitted, not target transport certification. Source acquisition is closed at five studies; this unit consumes its packet without resetting retrieval quotas.',
             'no_target_results_supplied': True}
write(B / 'SOURCE_ADMISSION.json', admission)

protocol = {
    'kind': 'reviewed_evidence_to_generation_development', 'date': '2026-11-04',
    'bundles': {'B': str(B)}, 'author_count': 1,
    'purpose': request['purpose'], 'analysis_requests': request['analyses'],
    'scientific_autonomy': 'Author chooses model structure, parameters, scientific evidence weighting, transformations and assumptions. No desired sign, coefficient, family or target numeric summary is supplied by controller.',
    'input_scope': 'New task and reviewed original-evidence packet only; no old candidates, target outcomes or prior result reports. Procedural boundary, not OS isolation of Agent tools.',
    'source_retrieval': 'Prior autonomous search completed independently at five originals. New unit uses its reviewed packet, no new search/download or quota reset.',
    'stages': {'initial_trial': [7400], 'initial_delivery': [7401,7402,7403], 'revision_trial': [7410], 'final_delivery': [7401,7402,7403]},
    'n_rows': 3000, 'max_physical_executions': 8, 'max_feedback_revisions': 1,
    'retention': 'Explicit retain decision aliases initial delivery tables; no duplicate generation or inflated table count.',
    'review': 'Review source meaning, unit transformations, specification/code consistency, joint-model implications and finite population moments before freeze. Preserve submitted drafts and mechanical corrections. No reviewer supplies target-driven parameters.',
    'feedback': 'Explicit semantic_feedback_v1 and generated-only diagnostics for all available initial runs. No existing target/reference results before final author closure. Source replay optional; unavailable checks remain unavailable. Source-context parameters or target diagnostics are not source-population reconstruction.',
    'evaluation': 'After final author closure, compare every delivery seed and both declared regressions with the already-exposed CHNS aggregate reference pinned below. Recompute synthetic analyses independently. No patient reads or new target fits. All failures and all terms retained; no equivalence, causal or fresh-confirmation claim.',
    'reference': {'path': 'work/agent_system_live_2026-11-03/evaluation/REPORT.json', 'sha256': sha(P / 'work/agent_system_live_2026-11-03/evaluation/REPORT.json'), 'exposed_development_only': True},
    'comparison_scope': 'One new model with richer evidence versus historical models is descriptive and confounded by author/model/input changes; not a controlled search-effect or revision-benefit experiment.',
    'stop': 'Stop after one initial and at most one feedback revision, all prespecified deliveries evaluated and independently reviewed; no target-driven rerun, extra seeds or new cohort.',
    'old_artifacts': 'Do not edit old frozen models, reports, manuscript v0.8 or reproduction lock.'}
write(R / 'PROTOCOL.json', protocol)
protocol_sha = sha(R / 'PROTOCOL.json')
write(B / 'RUN_RULES.json', {'protocol_sha256': protocol_sha, 'stages': protocol['stages'], 'max_physical_executions': 8, 'max_feedback_revisions': 1, 'source_replay_required': False})
assignment = '''# Reviewed-evidence scientific construction

Read task.json, request.json, SOURCE_ADMISSION.json, registry.json, the reviewed_evidence/ ledger and independent review, and any needed originals under sources/. The initial AUTHOR_TASK.md describes intake-time status; the source registry has now been populated by the controller from independently reviewed originals. Four source IDs are PMC IDs, and the separately admitted publisher source ID is Jansen2013. Cite exact registered IDs/paths/hashes.

Choose the full joint law and all scientific parameters yourself. All six output columns, in task order, must be generated. No target rows, distributions, signs or effects are provided. Do not open prior experiments, manuscript, evaluation reports or any other bundle. Reading interface code in cohort_harness/, docs/EXECUTION_ADAPTER.md and docs/SEMANTIC_FEEDBACK_V1.md is permitted. Use the supplied evidence-cohort-generation skill.

The acquisition Agent has already used the five-original-study allowance. This construction consumes that packet rather than beginning a second search. Inspect all supplied conflicts and applicability limits. You may use, qualify or decline any source result and record remaining needs. Algebraic conversions must stay distinguished from reported values. A source coefficient with extra adjustment cannot be treated as the target coefficient without explicit assumptions. An unknown CI level cannot be invented to fit a schema; retain its endpoints in contextual notes and represent uncertainty truthfully.

Submit candidates/initial with evidence.json, model_spec.json, decision.md, checks.json and generator.py OR generated.csv, plus source_semantics_v1.json and whole_cohort_feedback.json required by semantic_feedback_v1. Read their schemas from the implementation/docs, not other candidates. Use source comparisons only where actually meaningful; source-population replay is optional. Do not label a target table as a different source population. Explain how the joint law implies the requested conditional analysis, and state existence of the population moments used by it. Scientific settings should be in the specification with evidence/assumption references.

Run static contract validation only. Do not locally execute your generator or change task/registry. The controller will freeze and run it through the existing isolated adapter, supply actual source/generated-only feedback, and allow one revision or a truthful retain decision. Preserve drafts when a review requires changes; do not overwrite a frozen candidate. Never inspect target outcomes or choose a favorable random seed. Decision records explain choices concisely and need not contain private reasoning traces.
'''
(B / 'CONSTRUCTION_ASSIGNMENT.md').write_text(assignment, encoding='utf-8')
write(R / 'STATE.json', {'status': 'prepared_for_independent_protocol_review', 'protocol_sha256': protocol_sha, 'bundle': str(B), 'new_generated_tables': 0, 'new_clinical_reads': 0, 'new_sources': 0})
print(json.dumps({'bundle': str(B), 'run': str(R), 'protocol_sha256': protocol_sha, 'registered_artifacts': len(registry)}))

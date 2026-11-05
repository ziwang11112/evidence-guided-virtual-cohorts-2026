"""Create an additive reviewed-runner derivative; never edit the old module."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent/'core_workflow_replication_2026-11-04/runner.py'
raw = SOURCE.read_bytes()
text = raw.decode('utf-8-sig')
replacements = [
    ('Bounded four-author core workflow.', 'Bounded six-author cross-task evidence-use workflow.'),
    ('max_physical_executions: 20;', 'max_physical_executions: 30;'),
    ('from cohort_harness.contracts import require, validate_task',
     'from cohort_harness.contracts import require, validate_task\nfrom controller_evidence_use import validate_candidate_use'),
    ('len(p["authors"]) == 4 and len(set(p["authors"])) == 4, "Exactly four authors required"',
     'len(p["authors"]) == 6 and len(set(p["authors"])) == 6, "Exactly six authors required"'),
    ('for case in ("CHNS2009", "ENSANUT2018")', 'for case in ("ENSANUT2018", "Turkana")'),
    ('counts == {"CHNS2009": 2, "ENSANUT2018": 2}, "Two authors per fixed case required"',
     'counts == {"ENSANUT2018": 3, "Turkana": 3}, "Three authors per fixed case required"'),
    ('for a in p["authors"].values()}) == 4,', 'for a in p["authors"].values()}) == 6,'),
    ('p["max_physical_executions"] == 20', 'p["max_physical_executions"] == 30'),
    ('ROOT / "RUNTIME_PREFLIGHT.json", ROOT / "evaluator.py",',
     'ROOT / "RUNTIME_PREFLIGHT.json", ROOT / "evaluator.py", ROOT / "controller_evidence_use.py",'),
    ('{"source_queries": 8, "source_downloads": 4, "revisions": 1}',
     '{"source_queries": 4, "source_downloads": 2, "revisions": 1}'),
    ('len(original_ids) <= p.get("acquisition", {}).get("per_author_originals_and_downloads", 4)',
     'len(original_ids - set(spec["curated_source_ids"])) <= 2'),
    ('state["usage"]["queries"] <= 8 and state["usage"]["downloads"] <= 4',
     'state["usage"]["queries"] <= 4 and state["usage"]["downloads"] <= 2'),
    ('gates = semantic.preflight(self.bundle, relative)',
     'use_report = validate_candidate_use(self.bundle, relative, self.spec["analysis_ids"],\n                baseline=parent_relative if stage == "revision" else None)\n            gates = semantic.preflight(self.bundle, relative)'),
    ('semantic_preflight=gates,', 'semantic_preflight=gates, evidence_use_report=use_report,'),
    ('if e["stage"] == "initial":\n                    require(receipt',
     'parent = None if e["stage"] == "initial" else next(f["candidate"] for f in freezes if f["stage"] == "initial")\n                require(e["evidence_use_report"] == validate_candidate_use(self.bundle, e["candidate"], self.spec["analysis_ids"], baseline=parent), "Evidence-use report changed")\n                if e["stage"] == "initial":\n                    require(receipt'),
    ('"All four authors must terminally close"', '"All six authors must terminally close"'),
    ('"scheduled_final_slots": 12', '"scheduled_final_slots": 18'),
    ('core_workflow_control_v1', 'cross_task_evidence_use_control_v1'),
    ('core_workflow_author_v1', 'cross_task_evidence_use_author_v1'),
    ('core_workflow_batch_closure_v1', 'cross_task_evidence_use_batch_closure_v1'),
]
for before, after in replacements:
    if text.count(before) != 1:
        raise RuntimeError('Ambiguous or missing reviewed substitution: '+before)
    text = text.replace(before, after)
header = '# Additive derivative of the 4 November runner; no old state is imported.\n'
with (ROOT/'runner.py').open('x', encoding='utf-8', newline='\n') as f:
    f.write(header+text)
with (ROOT/'RUNNER_DERIVATION.json').open('x', encoding='utf-8') as f:
    json.dump({'source': str(SOURCE), 'source_sha256': hashlib.sha256(raw).hexdigest(),
               'changes': [{'before': a, 'after': b} for a,b in replacements],
               'destination_sha256': hashlib.sha256((ROOT/'runner.py').read_bytes()).hexdigest()}, f, indent=2)

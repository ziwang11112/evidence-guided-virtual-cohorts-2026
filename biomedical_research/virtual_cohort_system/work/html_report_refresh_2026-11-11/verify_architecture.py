"""Bind the read-only architecture audit and editable diagram; no scientific execution."""
from pathlib import Path
import base64
import hashlib
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime, timezone

W = Path(__file__).resolve().parent
P = W.parents[1]
asset = P/'docs/report-assets-2026-11-11/architecture.drawio.svg'
native = asset.with_suffix('')
png = W/'qa/architecture.drawio.png'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
svg = ET.parse(asset).getroot()
embedded = svg.attrib.get('content')
assert embedded, 'SVG missing editable draw.io content'
editroot = ET.fromstring(embedded)
if editroot.tag == 'mxfile':
    child = editroot.find('diagram')
    assert child is not None
    if child.find('mxGraphModel') is not None:
        graph = child.find('mxGraphModel')
    else:
        payload = urllib.parse.unquote(zlib.decompress(base64.b64decode(child.text), -15).decode())
        graph = ET.fromstring(payload)
else:
    graph = editroot
assert graph.tag == 'mxGraphModel'
cells = graph.findall('./root/mxCell')
ids = [c.attrib['id'] for c in cells]
assert len(ids) == len(set(ids))
assert {'0','1','agent','law','sampling','trial','checks','freeze','final','analysis','utility'} <= set(ids)
for c in cells:
    if c.get('edge') == '1':
        assert c.find('mxGeometry').get('relative') == '1'
assert not re.search(r'<!--[\s\S]*?-->', ET.tostring(graph, encoding='unicode'))
assert native.exists()
native_graph = ET.parse(native).getroot()
native_cells = native_graph.findall('./root/mxCell')
assert [(c.get('id'), c.get('value')) for c in cells] == [(c.get('id'), c.get('value')) for c in native_cells]
sourcehash = sha(native)
sourcefiles = [
    'work/request_only_repeatability_2026-11-11/PROTOCOL.md',
    'work/request_only_repeatability_2026-11-11/RESULTS.md',
    'work/request_only_repeatability_2026-11-11/api_loop.py',
    'work/request_only_repeatability_2026-11-11/tools_runtime.py',
    'work/request_only_repeatability_2026-11-11/evaluate_pilot.py',
    'work/scientific_check_revision_2026-11-11/PROTOCOL.md',
    'work/scientific_check_revision_2026-11-11/RESULTS.md',
    'work/scientific_check_revision_2026-11-11/api_loop.py',
    'work/scientific_check_revision_2026-11-11/tools_runtime.py',
    'work/scientific_check_revision_2026-11-11/law_checks.py',
    'work/scientific_check_revision_2026-11-11/evaluate_pilot.py',
    'cohort_harness/execution.py',
    'cohort_harness/_worker.py',
]
record = {
 'status':'PASS_ARCHITECTURE_READ_ONLY_AND_VISUAL_QA',
 'created_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Two completed versioned runtimes; explanation and diagram only',
 'not_performed':['API calls','generation','patient-row access','scientific refits','frozen-artifact edits','new biomedical certification'],
 'sources':{s:sha(P/s) for s in sourcefiles},
 'current_paths':{
  'initial':'request_only_repeatability_2026-11-11/api_loop.py -> tools_runtime.ToolRuntime -> Europe PMC gateway / immutable candidate / isolated_run -> cohort_harness.execution helpers and _worker -> generated-only analysis',
  'paired_review':'scientific_check_revision_2026-11-11/api_loop.py -> versioned tools_runtime extending initial runtime -> law_checks / trial bindings / optional immutable revision',
  'reference_evaluation':'all closed -> frozen final draws -> pinned reference aggregation -> independent saved-table arithmetic',
 },
 'claims':[
  {'claim':'One scientific Agent per session with tools; parallel sessions are independent repetitions','status':'implemented_and_observed'},
  {'claim':'Agent chooses sources, structure and parameters; programs sample rows','status':'implemented_and_observed'},
  {'claim':'Mathematical, physiological and dependency checks','status':'implemented_and_observed_in_separate_paired_review'},
  {'claim':'Revision always improves final data quality','status':'not_supported'},
  {'claim':'Current path calls semantic_feedback_v1 / source replay / calibrated optimizer','status':'not_current_path'},
  {'claim':'Browser-wide autonomous retrieval or direct GPT row emission in latest main experiment','status':'not_current_path'},
  {'claim':'Independent saved-table numerical recomputation','status':'performed_not_external_human_clinical_review'},
 ],
 'diagram':{
  'path':asset.relative_to(P).as_posix(),'sha256':sha(asset),
  'width':svg.get('width'),'height':svg.get('height'),'viewBox':svg.get('viewBox'),
  'editable_xml_embedded':True,'embedded_cell_count':len(cells),
  'unique_ids':True,'edge_geometries_valid':True,'labels_match_native_source':True,
  'native_source_sha256_before_skill_required_deletion':sourcehash,
  'qa_png':png.relative_to(P).as_posix(),'qa_png_sha256':sha(png),
  'colors':{'blue':'#4169a8','purple':'#8862ad','orange':'#c17936'},
  'visual_review':'Viewed full final PNG: labels legible, no observed clipping or overlaps; optional return edge label has its own background; no green or artificial multiaagent diagram',
  'visual_open_method':'view_image; hidden draw.io CLI exports; no visible app or browser',
  'clinical_validity_certified':False,
 },
 'report_sha256':sha(W/'ARCHITECTURE_AUDIT.md'),
 'authoring_script_sha256':sha(W/'draw_architecture.py'),
 'repair_script_sha256':sha(W/'repair_drawio.cjs'),
}
# Only this newly-authored, exact local source is removed. Export retains its editable content.
assert native.resolve().parent == (P/'docs/report-assets-2026-11-11').resolve()
assert native.name == 'architecture.drawio'
native.unlink()
record['diagram']['native_source_removed_after_embed_verification'] = not native.exists()
(W/'ARCHITECTURE_AUDIT.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':record['status'],'svg_sha256':sha(asset),'editable_cells':len(cells),'native_removed':not native.exists()},ensure_ascii=False))

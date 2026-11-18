"""Prepare a source/code navigation pilot; never run models or read patient tables."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import html
import json
import shutil
import re
import zipfile

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
OLD = PROJECT / 'work/request_only_agent_capacity_2026-11-10'
HOST = ROOT / '_host_only'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def dump(path, obj):
    put(path, json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

def esc(value):
    return html.escape(str(value))

LAWS = {
    'A': ('PNS_BASE', 'PNS'),
    'B': ('PNS_WORKFLOW', 'PNS'),
    'C': ('LIPID_BASE', 'LIPID'),
    'D': ('LIPID_WORKFLOW', 'LIPID'),
}

# Each row is a navigational summary of the same code/author notes/source URLs
# supplied in both presentations. No target estimate enters this file.
def row(kind, basis, adopted, bridge, lines, spec, note):
    return dict(kind=kind, source_basis=basis, adopted_quantity=adopted,
                bridge_or_limit=bridge, code_lines=lines, spec_keys=spec, note=note)

MAPS = {}
for law in ['A', 'B']:
    for j, endpoint, coefficient in [(1, 'SBP', 1.15), (2, 'DBP', .75)]:
        key = f'{law}{j}'
        short = endpoint.lower()
        MAPS[key] = [
            row('Reported external association', 'PMC6324286, Results: association between BMI and BP; Statistical Analysis.',
                f'{coefficient:g} mmHg per kg/m²; equivalent {coefficient*5:g} mmHg per 5 kg/m².',
                'China-PEACE adjustment includes treatment, socioeconomic, geographic and other factors in addition to age/sex. The requested regression adjusts age and sex only. Transfer is assumed.',
                [39, 39] if law == 'A' and j == 1 else [40,43] if law == 'A' else [31,40],
                [f'bmi_{short}_slope_per_unit'] if law == 'A' else [f'bp_model.{short}_bmi_slope_per_unit'],
                'EVIDENCE ACTUALLY RETRIEVED / Evidence actually retrieved: China-PEACE'),
            row('Assumed covariate structure', 'Author model specification; ELSA marginal scales are context anchors.',
                'Age and sex composition; age-dependent BMI; nonlinear BP age curves.',
                'A coefficient of the generative conditional mean is not automatically the requested linear-age OLS coefficient. BMI and age are dependent, and nonlinear age effects are not fully adjusted by a linear-age analysis.',
                [11,43] if law == 'A' else [7,40],
                ['age_band_probabilities','female_probability_by_band','bmi_age_slope_before_55'] if law == 'A' else ['demography','bmi_model','bp_model'],
                'ASSUMPTIONS / Explicit unsupported assumptions; requested analyses'),
            row('Implementation boundary', 'Author code, not a reported source statistic.',
                'Joint BP bounds and pulse-pressure rejection; rounding.',
                'Acceptance depends on both pressures. Rejection/rounding can change the resulting regression projection. No finite-sample coefficient forcing is implemented.',
                [47,66] if law == 'A' else [43,53],
                ['sbp_bounds','dbp_bounds','pulse_pressure_bounds'] if law == 'A' else ['bp_model.sbp_bounds','bp_model.dbp_bounds','bp_model.minimum_pulse_pressure'],
                'Measurement assumptions and analysis limitations'),
        ]

MAPS['A3'] = [
    row('Reported external dependence', 'PMC11392332, Table 2 and joint-model methods.',
        'Residual correlation 0.7307; model innovation correlation 0.73.',
        'Source conditions on age, categorical BMI and a broader screened set; sex was not retained, and antihypertensive users were excluded. This differs from continuous BMI + age + sex, with treatment unrestricted.',
        [45,51], ['bp_residual_correlation'], 'EVIDENCE ACTUALLY RETRIEVED: Uganda STEPS'),
    row('Assumed dispersion', 'Author specification; marginal BP scales give context only.',
        'Gaussian innovation SDs 14.8 and 9.9 mmHg.',
        'These are chosen residual SDs, not reported conditional SDs. An innovation correlation is not exactly the residual correlation after nonlinear age structure, selection and rounding.',
        [36,66], ['bp_residual_sd','sbp_age_quadratic','dbp_age_slope_after_55'], 'ASSUMPTIONS / MEASUREMENT / ANALYSIS'),
]
MAPS['B3'] = [
    row('Reported different dependence measure', 'PMC4143670, phenotype definition and Table 3 null model.',
        'Kendall tau 0.578 for treatment-corrected, age/sex/smoking-adjusted mean residual phenotypes over up to three exams.',
        'The source uses an asymmetric copula. It is not a baseline observed-BP Pearson residual correlation and does not adjust BMI.',
        [33,35], ['bp_model.external_kendall_tau'], 'Evidence actually retrieved: Konigorski et al.'),
    row('Derived with assumptions', 'Author derivation combining PMC4143670 with PMC4338719 Table 1.',
        'sin(pi × 0.578 / 2) = 0.788226; subtract assumed age/sex/BMI variance contributions; innovation rho ≈ 0.763163.',
        'Gaussian-copula approximation, cross-population transfer and approximate independent variance budgeting are additional assumptions. No algebra recovers the requested measurement operator from the source.',
        [27,37], ['reference','bmi_model.reference_sd','bp_model'], 'Derived under assumptions'),
    row('Implementation boundary', 'Author law and notes.',
        'Nonlinear age means, age-dependent BMI/sex, pair rejection and rounding.',
        'The approximate reference variance budget is not exact source replay or an identity for the final OLS residual correlation.',
        [7,53], ['demography','bmi_model','bp_model.rounding_step'], 'Explicit unsupported assumptions / measurement scenario'),
]

for j, endpoint, cond in [(1, 'TC', '+0.053 = +0.065 − 0.012'), (2, 'HDL', '−0.012')]:
    MAPS[f'C{j}'] = [
        row('Qualitative association evidence', 'PMC6897412 Table 4; other source tables provide marginal/context information.',
            'Overweight/obese versus normal: LDL +0.23/+0.48 and HDL −0.06/−0.15 mmol/L.',
            'Categorical multivariable LDL and HDL associations do not identify a continuous TC or HDL slope. LDL is not TC.',
            [31,39], ['lipids.hdl_per_bmi','lipids.nonhdl_per_bmi'], 'NUMERICAL EVIDENCE and ASSUMPTIONS'),
        row('Chosen continuous relationship', 'Author specification, informed by but not equal to the source associations.',
            f'{endpoint} conditional slope {cond} mmol/L per BMI unit.',
            'Convert mmol/L per BMI unit to mg/dL per 5 kg/m² by multiplying by 38.67 × 5. Context mixture and adjustment can change final pooled OLS slopes.',
            [31,49], ['lipids.hdl_per_bmi','lipids.nonhdl_per_bmi','mixture'], 'Numerical slopes are modeling assumptions'),
        row('Joint-law construction', 'Author code and assumptions.',
            'Positive HDL and non-HDL components; TC = HDL + non-HDL; unobserved lifestyle contexts.',
            'Neither context weights nor omitted-variable relationships are identified from the reported marginal/categorical results.',
            [17,49], ['mixture','lipids'], 'ASSUMPTIONS / uncertainty'),
    ]
MAPS['C3'] = [
    row('Unreported joint relationship', 'Author notes explicitly state no directly transferable TC–HDL residual correlation was retrieved.',
        'Log-error correlation between HDL and non-HDL = 0.08; component CVs = 0.27 and 0.28.',
        '0.08 is an assumed latent log-error correlation, not TC–HDL residual Pearson correlation. It must not be attributed to a paper.',
        [42,49], ['lipids.log_error_correlation_hdl_nonhdl','lipids.hdl_cv','lipids.nonhdl_cv'], 'Shared HDL component / uncertainty'),
    row('Model-implied dependence', 'Positive components plus latent context mixture.',
        'TC shares HDL as an additive component; non-HDL is not exported.',
        'Shared-component covariance, lognormal multipliers and omitted context jointly determine the requested pooled residual correlation.',
        [17,49], ['mixture','lipids'], 'ASSUMPTIONS'),
]

for j, endpoint, effects in [(1,'TC','0.23, 0.20, 0.13, 0.15'),(2,'HDL','−0.03, −0.03, −0.05, −0.04')]:
    MAPS[f'D{j}'] = [
        row('Reported standardized association', 'PMC6747887 Table 3: rural women, rural men, urban women, urban men.',
            f'{endpoint} differences {effects} mmol/L per ONE SD higher BMI.',
            'The source additionally adjusts ethnicity, education, assets, marital status, parity (women), medication, smoking, alcohol, activity and HIV/ART. These are not age/sex-only coefficients.',
            [38,48], [f'sex_parameters.F.{endpoint.lower()}_per_sd_rural', f'sex_parameters.M.{endpoint.lower()}_per_sd_rural'], 'Table 3 / per-SD effects in author notes'),
        row('Standardized-effect transport assumption', 'PMC6435188 v2 Table 1, Maasai BMI SD; author bridge.',
            'Divide source per-SD effects by 4.8 kg/m², a Kenyan/model BMI SD.',
            'The Malawian BMI SD was not retrieved. Dividing by 4.8 is not recovery of a measured Malawian physical-unit coefficient. Subsequent × 38.67 × 5 is a unit/reporting conversion.',
            [38,48], ['sex_parameters.F.effect_transport_bmi_sd','sex_parameters.M.effect_transport_bmi_sd'], 'Standardized-effect transport to a modeled 4.8 kg/m² SD'),
        row('Population/context assumption', 'PMC6747887 Table 2 context differences, Kenyan anchors and author age/mixture law.',
            'Sex/context-specific slopes, 30% transition context; context-centered BMI.',
            'Pooled OLS omits context and effect interactions. It need not equal any single stratum coefficient; the setting contrasts are not causal settlement effects.',
            [11,48], ['p_transition','sex_parameters','bmi.age_slope'], 'Demographic/lifestyle assumptions and context transport'),
    ]
MAPS['D3'] = [
    row('Reported marginal information', 'PMC6435188 v2 Table 1: Kenyan Maasai marginal TC/HDL SDs.',
        'Female TC/HDL SD 0.9/0.30; male 1.1/0.32 mmol/L.',
        'These are marginal SDs, not conditional residual variances or a TC–HDL covariance. They alone do not determine the requested dependence.',
        [55,74], ['sex_parameters.F.source_tc_sd','sex_parameters.F.source_hdl_sd','sex_parameters.M.source_tc_sd','sex_parameters.M.source_hdl_sd'], 'Residual variance derivation'),
    row('Derived variance budget', 'Author code combining source marginals with assumed age/BMI mean variation.',
        'Subtract modeled mean variance; set non-HDL residual variance = TC residual variance − HDL residual variance.',
        'This uses assumed BMI–age covariance and conditional HDL/non-HDL independence. Source/model age distributions differ; replay is approximate.',
        [55,74], ['bmi.age_slope','sex_parameters','tc_age_slope','hdl_age_slope'], 'Residual variances / major assumptions'),
    row('Assumed conditional independence', 'Author code, not a reported correlation.',
        'Separate gamma draws for HDL and non-HDL; TC = HDL + non-HDL.',
        'Shared HDL creates positive TC–HDL covariance. Conditional within-context dependence is not the pooled OLS residual correlation with context omitted.',
        [76,80], ['sex_parameters','p_transition'], 'Conditional independence / no published joint distribution'),
]

QUESTIONS = [
    ('source', 'What published result, if any, numerically supports this analysis? Give its source/table, statistic and unit. If no direct result exists, say so and distinguish contextual evidence.'),
    ('operator', 'How does the source population, measurement or adjustment set differ from the requested analysis? Name at least one material difference; do not infer a target discrepancy.'),
    ('bridge', 'What value or transformation is actually adopted by the generator? Distinguish reported quantities, algebra under assumptions, and chosen quantities.'),
    ('code', 'Locate the implementation: give specification key(s) and generator line(s) that control this analysis. Explain their role briefly.'),
    ('assumption', 'Name a scientifically consequential unverified assumption and explain which requested analysis it could change. Distinguish an assumption from a demonstrated coding error.'),
]

CSS = '''body{font:16px/1.55 system-ui,sans-serif;color:#202c42;background:#f5f6fa;margin:0}main{max-width:1050px;margin:auto;padding:36px 26px}h1{font-size:28px;line-height:1.2}h2{font-size:21px;margin-top:32px}h3{font-size:17px}a{color:#244ca8}header,section,.notice{background:white;border:1px solid #dbe1ed;border-radius:10px;padding:20px;margin:16px 0}header{border-top:5px solid #4668b0}p{margin:8px 0}.muted{color:#5f687a;font-size:14px}.badge{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:#7452a8}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 ui-monospace,Consolas,monospace;background:#f1f3f8;padding:14px;border-radius:6px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;border:1px solid #dce2ee;text-align:left;vertical-align:top}th{background:#edf1fa}textarea{width:100%;min-height:95px;box-sizing:border-box;font:15px/1.5 system-ui;padding:10px;border:1px solid #aab8d2;border-radius:5px}input{padding:8px;max-width:90%;border:1px solid #aab8d2;border-radius:4px}button{background:#244ca8;color:white;border:0;padding:10px 18px;border-radius:5px;cursor:pointer;margin:8px 8px 8px 0}button.secondary{background:#68558d}code{font:13px ui-monospace,Consolas,monospace}.code-line{scroll-margin-top:20px;display:block}.code-line:target{background:#ffefcf}.ln{display:inline-block;width:3em;color:#7b8290;user-select:none}.nav a{margin-right:18px}.mapitem{border-left:4px solid #8a74b7;padding:12px 16px;background:#faf8fe;margin:14px 0}.response{border-left:4px solid #d28b4c}.status{min-height:25px;color:#405b88}@media print{button,.nav{display:none}main{max-width:100%;padding:0}section,header{break-inside:avoid}pre{font-size:10px}textarea{min-height:70px}a{color:#202c42}}'''

def source_records(notes):
    p = notes['provenance']
    records = p.get('sources', p.get('used_sources', []))
    extra = p.get('additional_context_read')
    if extra:
        records = records + [extra]
    out = []
    for r in records:
        doi = r.get('doi')
        pmc = r.get('pmcid') or (re.search(r'PMC\d+', r.get('locator','')) or [None])[0]
        pmid = r.get('pmid')
        url = 'https://pmc.ncbi.nlm.nih.gov/articles/'+pmc+'/' if pmc else 'https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/' if pmid else 'https://doi.org/'+doi
        out.append(dict(pmcid=pmc, pmid=pmid, doi=doi, version=r.get('version'),
                        url=url, locator=r.get('used_sections',r.get('locators',r.get('retrieved_sections',r.get('use','Author notes'))))))
    return out

def analysis(law, j):
    bp = law in 'AB'
    outcome = (['systolic blood pressure','diastolic blood pressure'] if bp else ['total cholesterol','HDL cholesterol'])
    if j < 3:
        label = f'BMI association with {outcome[j-1]}'
        definition = ('Equal-weight OLS with intercept, linear age, recorded sex and BMI. Report the BMI coefficient per 5 kg/m². '
                      + ('Outcome unit is mmHg.' if bp else 'Generate lipids in mmol/L; report slopes in mg/dL per 5 kg/m² using 38.67 mg/dL per mmol/L.'))
    else:
        label = ('SBP–DBP' if bp else 'TC–HDL') + ' residual dependence'
        definition = ('Fit separate equal-weight OLS models for both outcomes, each on intercept, linear age, recorded sex and BMI; compute Pearson correlation between the two residual vectors. Correlation is dimensionless.')
    return label, definition

def map_html(key):
    pieces = []
    for r in MAPS[key]:
        lo, hi = r['code_lines']
        pieces.append(f'''<article class="mapitem"><span class="badge">{esc(r['kind'])}</span><h3>{esc(r['source_basis'])}</h3>
<p><b>Adopted:</b> {esc(r['adopted_quantity'])}</p><p><b>Bridge / boundary:</b> {esc(r['bridge_or_limit'])}</p>
<p><a href="#L{lo}">Generator lines {lo}–{hi}</a> · Spec: <code>{esc(', '.join(r['spec_keys']))}</code></p>
<p class="muted">Author-note anchor: {esc(r['note'])}</p></article>''')
    return '<section id="map"><h2>Source-to-implementation navigation map</h2><p>This map was curated after construction from the original Agent records plus a source/code audit. It adds interpretation and navigation, including inferred dependency links; it is not untouched Agent output or a prospective confidence prediction. Both presentations retain the same underlying scientific artifacts. Tags describe provenance, not population accuracy. Map preparation effort and cost were not measured.</p>'+''.join(pieces)+'</section>'

def dossier_html(did, law, j, presentation, notes, code, spec, request, task, sources):
    title, definition = analysis(law,j)
    codelines = ''.join(f'<span class="code-line" id="L{i}"><span class="ln">{i}</span>{esc(line)}</span>' for i,line in enumerate(code.splitlines(),1))
    sourcelist = ''.join(f'<li><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r.get("pmcid") or r.get("pmid") or r["doi"])}</a> · DOI {esc(r["doi"])} · captured version {esc(r["version"] if r["version"] is not None else "see capture manifest")}. <span class="muted">{esc(r["locator"])}</span></li>' for r in sources)
    questionhtml = ''.join(f'<h3>{i}. {esc(q)}</h3><textarea id="answer_{name}" aria-label="Answer {i}"></textarea>' for i,(name,q) in enumerate(QUESTIONS,1))
    payload = json.dumps(dict(dossier_id=did,law_id=law,analysis=j,presentation=presentation), separators=(',',':'))
    script = '''const meta=META; let start=null,stop=null,pauses=[];
document.getElementById('start').onclick=()=>{if(start===null){start=new Date().toISOString();document.getElementById('status').textContent='Started '+start;}else{document.getElementById('status').textContent='Already started; record interruptions below.';}};
document.getElementById('save').onclick=()=>{stop=new Date().toISOString();const answers={};document.querySelectorAll('textarea[id^="answer_"]').forEach(x=>answers[x.id.substring(7)]=x.value);const data={...meta,reviewer_id:document.getElementById('reviewer').value,started_utc:start,saved_utc:stop,wall_seconds:start?(Date.parse(stop)-Date.parse(start))/1000:null,confidence_in_answer:document.getElementById('confidence').value,interruptions:document.getElementById('interruptions').value,answers,response_origin:'local browser entry; actual reviewer administration requires organizer verification'};const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=meta.dossier_id+'_answers.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);document.getElementById('status').textContent='Saved locally. No answers are transmitted.';};'''.replace('META',payload)
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{did}: {esc(title)}</title><style>{CSS}</style><main>
<header><span class="badge">Scientific provenance review · {did} · law {law}</span><h1>{esc(title)}</h1><p>{esc(definition)}</p><p class="muted">Inspect scientific support and implementation. No real-reference or generated-analysis result is supplied. A traceable assumption is not automatically a correct population model.</p><p class="nav"><a href="#request">Request</a><a href="#sources">Sources</a><a href="#notes">Author notes</a><a href="#code">Code</a><a href="#answers">Your answers</a></p></header>
<section><p><b>Reviewer ID:</b> <input id="reviewer" autocomplete="off" placeholder="Use an assigned non-identifying ID"></p><button id="start">Start this dossier</button><p id="status" class="status">The timer records wall time only. Record interruptions; do not count them as active review time.</p></section>
{map_html(law+str(j)) if presentation=='map' else ''}
<section id="request"><h2>Original research request</h2><pre>{esc(request)}</pre><h3>Population definition</h3><p>{esc(task['population'])}</p><p><a href="task.json">Exact task contract</a> · <a href="request.txt">Exact request text</a></p></section>
<section id="sources"><h2>Source access</h2><p>Original papers remain with their publishers/repositories; no full paper is bundled. The captures used by the constructor are identified by version and hashes in the accompanying manifest. A current web page may differ from a captured version.</p><ul>{sourcelist}</ul><p><a href="source_manifest.json">Source/version capture metadata</a></p></section>
<section id="notes"><h2>Original author notes</h2><p>Unedited submitted scientific explanation; these are claims to inspect, not an adjudicated answer key.</p><pre>{esc(notes['notes'])}</pre><details><summary>Full original provenance metadata</summary><pre>{esc(json.dumps(notes['provenance'],indent=2,ensure_ascii=False))}</pre></details><p><a href="notes.json">Exact submitted notes</a></p></section>
<section id="spec"><h2>Exact model specification</h2><pre>{esc(json.dumps(spec,indent=2,ensure_ascii=False))}</pre><a href="model_spec.json">Download specification</a></section>
<section id="code"><h2>Exact generator</h2><p>Read-only display. Nothing on this page executes the program. The line numbers refer to the byte-identical generator copy.</p><pre>{codelines}</pre><a href="generator.py">Download generator</a></section>
<section id="answers" class="response"><h2>Five review questions</h2><p>Answer for this dossier's analysis. Use the available evidence and code, and mark unresolved points explicitly. Do not search for the target cohort's results or infer accuracy from a provenance label.</p>{questionhtml}<h3>Confidence in these factual answers (optional, 0–100)</h3><input type="number" id="confidence" min="0" max="100"><h3>Interruptions, inaccessible sources or unresolved material</h3><textarea id="interruptions"></textarea><button id="save">Save answers as JSON</button><p class="muted">No automatic upload or background network requests. Save before leaving this page. This is a preparation package; no human assessment has yet been performed.</p></section>
</main><script>{script}</script></html>'''

def main():
    HOST.mkdir(parents=True,exist_ok=True)
    laws={}; bindings=[]; source_checks=[]
    # Copies below are exact; only filenames/directories and presentation change.
    for law,(episode,taskname) in LAWS.items():
        base=OLD/'episodes'/episode/'candidates/v001'
        notes=json.loads((base/'notes.json').read_text(encoding='utf-8'))
        sources=source_records(notes)
        captures=[]
        for action in sorted((OLD/'episodes'/episode/'tool_actions').glob('action_*/result.json')):
            result=json.loads(action.read_text(encoding='utf-8'))
            if result.get('xml_sha256'):
                captures.append(dict(source_id=result.get('source_id'),source_version=result.get('source_version'),
                                     section=result.get('section'),xml_sha256=result['xml_sha256'],
                                     xml_bytes=result.get('xml_bytes'),response_sha256=sha(action)))
        laws[law]=dict(base=base,notes=notes,spec=json.loads((base/'model_spec.json').read_text(encoding='utf-8')),
                       code=(base/'generator.py').read_text(encoding='utf-8'),
                       request=(OLD/'requests'/f'{taskname}.txt').read_text(encoding='utf-8'),
                       task=json.loads((OLD/'tasks'/f'{taskname}.json').read_text(encoding='utf-8')),
                       taskname=taskname,sources=sources,captures=captures)
        bindings.append(dict(law_id=law,source_episode=episode,candidate='v001',
                             artifact_sha256={name:sha(base/name) for name in ['generator.py','model_spec.json','notes.json']},
                             source_capture_receipts=[dict(path=str(x.relative_to(PROJECT)).replace('\\','/'),sha256=sha(x)) for x in sorted((OLD/'episodes'/episode/'tool_actions').glob('action_*/result.json')) if json.loads(x.read_text(encoding='utf-8')).get('xml_sha256')]))
    dossiers=[]
    for i,(law,j) in enumerate([(l,j) for l in LAWS for j in [1,2,3]],1):
        did=f'D{i:02d}'; d=laws[law]; title,definition=analysis(law,j)
        dossiers.append(dict(dossier_id=did,law_id=law,analysis=j,title=title,definition=definition))
        for presentation in ['standard','map']:
            dest=ROOT/'master'/presentation/did
            dest.mkdir(parents=True,exist_ok=True)
            for file in ['generator.py','model_spec.json','notes.json']:
                shutil.copyfile(d['base']/file,dest/file)
            shutil.copyfile(OLD/'requests'/f'{d["taskname"]}.txt',dest/'request.txt')
            shutil.copyfile(OLD/'tasks'/f'{d["taskname"]}.json',dest/'task.json')
            dump(dest/'source_manifest.json',dict(sources=d['sources'],captures=d['captures'],
                 full_text_included=False,raw_patient_or_generated_rows_included=False))
            put(dest/'index.html',dossier_html(did,law,j,presentation,d['notes'],d['code'],d['spec'],d['request'],d['task'],d['sources']))
    mapped_a={'D01','D02','D06','D09','D10','D11'}
    order_a=['D01','D04','D07','D10','D02','D05','D08','D11','D03','D06','D09','D12']
    assignments={}
    for reviewer,order in [('A',order_a),('B',list(reversed(order_a)))]:
        package=ROOT/f'reviewer_{reviewer}'
        records=[]
        for ordernum,did in enumerate(order,1):
            mapped=(did in mapped_a) if reviewer=='A' else (did not in mapped_a)
            presentation='map' if mapped else 'standard'
            shutil.copytree(ROOT/'master'/presentation/did,package/did,dirs_exist_ok=True)
            meta=next(d for d in dossiers if d['dossier_id']==did)
            records.append(dict(order=ordernum,dossier_id=did,presentation=presentation,law_id=meta['law_id'],analysis=meta['analysis']))
        assignments[reviewer]=records
        items=''.join(f'<tr><td>{x["order"]}</td><td><a href="{x["dossier_id"]}/index.html">{x["dossier_id"]}</a></td><td>{esc(next(d["title"] for d in dossiers if d["dossier_id"]==x["dossier_id"]))}</td><td>Law {x["law_id"]}</td></tr>' for x in records)
        put(package/'index.html',f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Scientific provenance review {reviewer}</title><style>{CSS}</style><main><header><span class="badge">Reviewer package {reviewer} · prepared, not yet administered</span><h1>Can you trace the scientific basis of a virtual-cohort analysis?</h1><p>Twelve analysis dossiers reuse four frozen generators. This is an inspection exercise, not a ranking of data accuracy or model providers.</p></header><section><h2>How to review</h2><ol><li>Work through the dossiers in the listed order. A break after six is reasonable. Do not open another reviewer's package.</li><li>Start the local timer when beginning a dossier; inspect the original request, source URLs, unedited author notes, specification and code. Some dossiers add a navigation map.</li><li>Answer five factual questions. Distinguish evidence, derivations and assumptions. Inaccessible sources and uncertainty are legitimate responses.</li><li>Save each response JSON before moving on. Record interruptions and any prior familiarity. No information is uploaded automatically.</li></ol><p>Do not look up the target cohort's results. No patient or generated individual records, reference answers, provider names or policy labels are bundled. The review concerns scientific traceability, not hidden model reasoning or clinical validity.</p><p class="muted">The organizer must independently adjudicate the draft scoring key before collecting a comparative pilot. If only one reviewer participates, treat feedback as qualitative. The four repeated laws can create learning across dossiers; report that limitation.</p></section><section><table><tr><th>Order</th><th>Dossier</th><th>Analysis</th><th>Shared law</th></tr>{items}</table></section></main></html>''')
        with zipfile.ZipFile(ROOT/f'reviewer_{reviewer}.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
            for file in sorted(package.rglob('*')):
                if file.is_file():z.write(file,file.relative_to(package).as_posix())
    dump(HOST/'ASSIGNMENT_AND_ORIGIN.json',dict(status='preparation_only_not_enrolled',law_bindings=bindings,assignments=assignments))
    answerdraft=[]
    for d in dossiers:
        key=d['law_id']+str(d['analysis'])
        answerdraft.append({**d,'status':'draft_requires_independent_source_code_adjudication',
                            'evidence_basis':MAPS[key],
                            'scoring_by_question':dict(source='0 absent/incorrect; 1 partially correct result or locator; 2 correct source/statistic/unit, or correctly states no direct statistic.',
                              operator='0 wrong/absent; 1 nonspecific difference; 2 names a supported, material population/measurement/adjustment mismatch.',
                              bridge='0 conflates quantity types; 1 partly correct; 2 accurately identifies adopted quantity and transformation/assumption.',
                              code='0 missing/wrong; 1 relevant file/section; 2 correct key/line(s) with correct role.',
                              assumption='0 unsupported accusation or no answer; 1 generic limitation; 2 specific unverified assumption and correctly affected analysis.'),
                            'not_an_error_by_itself':['A disclosed transport assumption','A source coefficient differing from final pooled OLS','Lack of individual target data','Shared HDL inducing positive TC–HDL covariance'],
                            'unresolved_policy':'Do not force ambiguous source semantics into binary ground truth; exclude unresolved adjudication items from scored denominator and report their count.'})
    dump(HOST/'ANSWER_KEY_DRAFT.json',dict(status='not_validated_gold_no_human_responses',dossiers=answerdraft))
    dump(ROOT/'RUBRIC.json',dict(status='draft_pending_independent_adjudication',questions=[dict(id=x,text=y) for x,y in QUESTIONS],
        scores=[0,1,2],primary_report='Report the five factual accuracy components separately, with denominators. Any sum is descriptive, not a confidence/clinical-quality score.',
        timing='Wall time recorded; subtract documented interruptions only with an explicit rule. Report incomplete dossiers and inaccessible sources. Time to correct answer requires adjudicated correctness; do not treat all fast answers as useful.',
        false_accusations='Record unsupported coding/source-error accusations separately, even when overall answers contain correct statements.',
        units='Twelve dossiers nested in four laws and two clinical contexts; participants are reviewers. No twelve-independent-model or clinical-validation claim.',
        map_origin='Postclosure curated interpretation/navigation assembled from Agent records plus source/code audit; preparation effort/cost not measured. A later pilot tests this presentation, not autonomous map generation.',
        design='Two complementary presentations; six standard/six mapped dossiers per reviewer, three of each per clinical context. Format cannot be blinded. Two reviewers yield a descriptive pilot only.',
        data_privacy='Use assigned non-identifying reviewer IDs; response files remain local until explicitly collected.',
        completed_reviews=0))
    dump(ROOT/'DOSSIER_INDEX.json',dict(status='prepared_pending_independent_review',dossiers=dossiers,law_count=4,dossier_count=12,clinical_context_count=2))
    put(HOST/'AMBIGUITY_REGISTER.md', '''# Draft adjudication ambiguities

No target results were used to decide these answers. Do not score before an independent adjudicator resolves or excludes uncertain factual items.

1. **Law A / Uganda residual dependence.** Table 2 explicitly labels 0.7307 residual correlation, but a nearby narrative reuses that number when describing an initial association. Do not label it merely a raw correlation. Its adjustment/treatment/measurement mismatch remains. The final reading aggregate used in regression is not unambiguously specified in the inspected material. The age upper bound varies between 68 and 69 in passages; this need not be a scored item.
2. **Law B / Kendall tau.** 0.578 is a reported tau, not a reported Pearson correlation. A Gaussian bridge is an explicit assumption; the original model is asymmetric and uses treatment-corrected repeated-exam phenotypes. The assumed covariance subtraction is mathematically inspectable, but cannot certify transfer to observed baseline pressures.
3. **Law C / chosen slopes.** Categorical LDL/HDL effects do not uniquely identify the continuous TC/HDL coefficients. The author's choices are disclosed assumptions, not extraction errors. No direct source identifies the latent 0.08 log-error correlation.
4. **Law D / standardized BMI effects.** The divisor 4.8 is a Kenyan/model SD. Treating it as Malawi's measured SD is incorrect. Marginal source variances do not identify the residual component covariance; independence is assumed. Model-implied conditional correlation is not the requested pooled residual correlation.
5. **All laws.** A full source list and faithful code do not validate population transfer, clinical utility, source uncertainty propagation or all joint distributions. A reviewer can correctly identify an assumption without knowing whether it raises or lowers error against an unseen population. No factual score should depend on the target agreement.
6. **Presentation parity.** Both versions include original author notes that already disclose important assumptions. The intervention adds curated interpretation and navigation over the same underlying artifacts. Some dependency links or derivations become explicit only in the map, so do not claim that the two presentations expose identical interpretations. The maps were assembled after closure from Agent records plus source/code audit, not produced autonomously by the original constructors. Map preparation effort/cost was not measured. A pilot tests this curated presentation only; it cannot demonstrate autonomous map production or calibrated trust. The map could have little incremental benefit; retain that outcome.
7. **Human learning.** Each reviewer sees three analyses from each law, so prior inspection can help later dossiers. Reverse ordering and complementary formats reduce simple order imbalance but do not remove learning. Report order and prior familiarity; no broad causal efficiency claim with two reviewers.
''')
    put(ROOT/'README.md', '''# Scientific traceability review materials

Prepared from four completed, frozen generators; no new data, API calls, target fits or reviewer contact. Twelve dossiers cover three primary analyses per law. This is **preparation**, not a completed human study or a validated confidence score.

- Open `reviewer_A/index.html` or `reviewer_B/index.html`; the corresponding ZIP contains only that assigned package.
- Each reviewer receives twelve unique dossiers, six standard and six with a source-to-code navigation map. The second package uses complementary formats and reverse order. Neither person should receive both packages.
- Code, model specifications, author notes, requests and task contracts are byte-identical across presentations and to the frozen artifacts. Source links/version hashes are the same. The mapped presentation adds postclosure, curated interpretation and navigation, assembled from Agent records plus source/code audit. Inferred links and explicit derivations are added presentation content, not independent evidence. A later usability pilot would test this curated package, not autonomous map production. Map preparation effort and cost were not measured.
- No patient or generated row tables, clinical-reference estimates, policy/provider identities, full third-party papers, credentials or adjudication answers are in either ZIP.
- `_host_only/` holds the neutral-ID mapping, raw-artifact bindings, draft answer key and ambiguity register. **Do not distribute this folder to reviewers.** Draft adjudication requires independent source/code review before scoring.
- `RUBRIC.json` defines the five questions, factual scoring approach and limitations. All human response counts are zero.
- A single biomedical collaborator can provide qualitative feedback. Comparative timing/accuracy claims require independent reviewers, adjudicated factual answers and a declared analysis of the nested/learning structure. No enrollment or external contact has occurred.

The maps expose scientific assumptions, transformations and implementation; they do not expose hidden reasoning or establish target-population accuracy. A traceable assumption remains an assumption.
''')
    verify(dossiers,laws,assignments)

def verify(dossiers,laws,assignments):
    checks=[]
    def check(name,value):
        checks.append(dict(name=name,pass_=bool(value)))
    check('12 dossiers / 4 laws',len(dossiers)==12 and len(laws)==4)
    for d in dossiers:
        did=d['dossier_id'];law=d['law_id'];base=laws[law]['base']
        for file in ['generator.py','model_spec.json','notes.json']:
            hs=[sha(ROOT/'master'/p/did/file) for p in ['standard','map']]
            check(did+' exact '+file,len(set(hs+[sha(base/file)]))==1)
        for file in ['request.txt','task.json','source_manifest.json']:
            check(did+' parity '+file,sha(ROOT/'master/standard'/did/file)==sha(ROOT/'master/map'/did/file))
        check(did+' map condition','id="map"' in (ROOT/'master/map'/did/'index.html').read_text(encoding='utf-8') and 'id="map"' not in (ROOT/'master/standard'/did/'index.html').read_text(encoding='utf-8'))
        for presentation in ['standard','map']:
            text=(ROOT/'master'/presentation/did/'index.html').read_text(encoding='utf-8')
            for match in re.findall(r'href="([^"]+)"',text):
                if match.startswith('http'):continue
                if match.startswith('#'):check(did+presentation+' anchor '+match,('id="'+match[1:]+'"') in text)
                else:check(did+presentation+' link '+match,(ROOT/'master'/presentation/did/match).is_file())
    for reviewer,records in assignments.items():
        check(reviewer+' unique12',len(records)==len(set(r['dossier_id'] for r in records))==12)
        check(reviewer+' sixeach',sum(r['presentation']=='map' for r in records)==6)
        for group in ['AB','CD']:
            check(reviewer+group+' threeeach',sum(r['presentation']=='map' and r['law_id'] in group for r in records)==3)
        with zipfile.ZipFile(ROOT/f'reviewer_{reviewer}.zip') as z:
            check(reviewer+' zipIntegrity',z.testzip() is None)
            check(reviewer+' noForbiddenFiles',all(not re.search(r'(_host_only|OUTCOME|EVALUATION|generated\.csv|\.env|\.xml|\.pdf|ANSWER_KEY)',n,re.I) for n in z.namelist()))
            for n in z.namelist():
                text=z.read(n).decode('utf-8')
                check(reviewer+n+' noArmProviderOrSecretLabel',not re.search(r'PNS_BASE|PNS_WORKFLOW|LIPID_BASE|LIPID_WORKFLOW|gpt-6|deepseek|claude|gemini|sk-[A-Za-z0-9]{16}',text,re.I))
    check('complementaryassignments',all(next(r for r in assignments['A'] if r['dossier_id']==d['dossier_id'])['presentation'] != next(r for r in assignments['B'] if r['dossier_id']==d['dossier_id'])['presentation'] for d in dossiers))
    failures=[c for c in checks if not c['pass_']]
    dump(ROOT/'MATERIALS_QA.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),status='PASS' if not failures else 'FAIL',checks=checks,failures=failures,scope='Package parity, exact frozen code/spec/notes, links, assignment and redistribution boundary; not independent scientific adjudication or human usability.',human_reviews=0))
    files={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
    dump(ROOT/'MANIFEST.json',dict(status='prepared_pending_independent_review',files=files,reviewer_zip_sha256={x:sha(ROOT/f'reviewer_{x}.zip') for x in ['A','B']},human_reviews=0))
    print(json.dumps(dict(status='PASS' if not failures else 'FAIL',checks=len(checks),failures=failures,files=len(files),root=str(ROOT)),indent=2))

if __name__=='__main__':
    main()

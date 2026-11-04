"""Aggregate-only manuscript checks. Never opens participant/generated rows or runs models."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import statistics
import xml.etree.ElementTree as ET

P = Path(__file__).resolve().parents[2]
W = Path(__file__).resolve().parent
B = P / 'work/core_workflow_replication_2026-11-04'
M = P / 'manuscript'
F = M / 'paper_figures_v13_2026-11-04'

def read(p):
    return p.read_text(encoding='utf-8-sig')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def jread(p):
    return json.loads(read(p))

checks = []
bindings = {}

def check(name, condition, detail=None):
    checks.append({'name': name, 'pass': bool(condition), 'detail': detail})

def bind(p):
    bindings[str(p.relative_to(P)) if p.is_relative_to(P) else str(p)] = digest(p)

old = read(M / 'DRAFT_v0_12.md')
new = read(M / 'DRAFT_v0_13.md')
R = jread(B / 'evaluation_v2/RESULTS.json')
A = jread(B / 'evaluation_v2/independent_numerical_audit/RESULTS.json')
I = jread(W / 'DRAFT_INTEGRATION_AUDIT.json')
meta = jread(W / 'SOURCE_BIBLIOGRAPHIC_METADATA.json')
protocol = jread(B / 'PROTOCOL.json')
slots = R['all_final_slots']
authors = R['authors']
primary = {(s['author_id'], s['seed'], a['id']): a for s in slots for a in s['analyses']}
groups = {}
for s in slots:
    for a in s['analyses'] + s['diagnostics']:
        groups.setdefault((s['author_id'], a['id']), []).append(a)

check('integration input/output/results/audit SHA bindings',
      I['input_draft_sha256'] == digest(M/'DRAFT_v0_12.md') and
      I['new_draft_sha256'] == digest(M/'DRAFT_v0_13.md') and
      I['new_results_sha256'] == digest(B/'evaluation_v2/RESULTS.json') and
      I['new_numerical_audit_sha256'] == digest(B/'evaluation_v2/independent_numerical_audit/RESULTS.json'))
counts = {'authors':len(authors), 'existing_requests':len({a['case_id'] for a in authors}),
          'final_tables':len(slots), 'unique_final_table_hashes':len({s['table_sha256'] for s in slots}),
          'final_virtual_rows':sum(s['n'] for s in slots), 'physical_executions':R['physical_attempts'],
          'primary_estimates':len(primary), 'all_numeric_values':sum(len(s['analyses'])+len(s['diagnostics']) for s in slots),
          'source_uses':sum(len(a['source_ids']) for a in authors),
          'distinct_originals':len({v for a in authors for v in a['source_ids']}),
          'query_credits':sum(a['gateway_usage']['queries'] for a in authors)}
check('batch accounting', counts == {'authors':4,'existing_requests':2,'final_tables':12,'unique_final_table_hashes':12,
      'final_virtual_rows':36000,'physical_executions':16,'primary_estimates':36,'all_numeric_values':366,
      'source_uses':16,'distinct_originals':12,'query_credits':24}, counts)
check('all four retained one initial law', all(a['decision']=='retain' and len(a['initial_and_revision_freezes'])==1 for a in authors))
check('366 independent numerical comparisons passed', A['status']=='PASS' and A['computed_endpoint_comparisons']==366 and A['endpoint_mismatches']==0 and not A['issues'])
check('all 36 primary directions agree', all(a['generated_direction']==a['reference_direction']=='positive' for a in primary.values()))
check('existing exposed references and no new clinical reads/fits', R['exposed_development'] and not R['new_clinical_reads_or_fits'] and protocol['reference']['exposed_development'] and not protocol['reference']['new_reference_fits'])
check('visible analyses and withheld values are explicit', 'Each author received the intended analyses' in new and 'but no target coefficients, desired signs' in new and 'CHNS and ENSANUT are exposed developmental references' in new and not protocol['feedback']['reference_values_to_authors'])
check('36 comparisons not independent confirmations', 'not 36 independent confirmations' in new)
check('no new estimator or universal-superiority claim', 'rather than a new estimator' in new and 'rather than a universal algorithmic ranking' in new and 'improvement from revision remains unestablished' in new)
check('no new clinical population claim', 'it does not add new clinical reference populations' in new)
feedback_counts=[]
for author in ['C01','C02','E01','E02']:
    path=B/'sessions'/author/f'feedback_{author.lower()}_initial_8100.json'
    feedback=jread(path); sem=feedback['semantic_feedback_v1']
    feedback_counts.append({'author':author,'approximate':sum(c['status']=='approximate' for c in sem['checks']),
                            'unavailable':sum(c['status']=='not_computable' for c in sem['checks']),
                            'reference_read':feedback['reference_read']})
    bind(path)
check('29 approximate and 39 unavailable trial checks',sum(x['approximate'] for x in feedback_counts)==29 and sum(x['unavailable'] for x in feedback_counts)==39 and not any(x['reference_read'] for x in feedback_counts),feedback_counts)
check('pre-freeze adverse moment repair retained explicitly', 'coordinator-detected divergent-moment defect before freeze' in new)

def table(text, label):
    section = text.split('**Table '+label+'.',1)[1]
    return re.search(r'\n(\|[^\n]*(?:\n\|[^\n]*)*)', section).group(1)

for label in ['2','3']:
    check('original Table '+label+' identical', table(old,label)==table(new,label))
for section,nextsection in [('4.2.','4.3.'),('4.3.','4.4.'),('4.4.','4.5.')]:
    a=old.split('### '+section,1)[1].split('### '+nextsection,1)[0]
    b=new.split('### '+section,1)[1].split('### '+nextsection,1)[0]
    check('original section '+section+' unchanged except asset paths', a.replace('paper_figures_v12_2026-11-04','paper_figures_v13_2026-11-04')==b)

mapping = {'CHNS BMI':'E1','CHNS glucose':'E2','CHNS adjusted age':'E3','ENSANUT adjusted age':'Q1_age10',
           'ENSANUT BMI':'Q2_bmi5','ENSANUT glucose-adjusted BMI':'Q3_bmi5'}
s1=[]
for line in table(new,'S1').splitlines()[2:]:
    c=[x.strip() for x in line.strip('|').split('|')]
    k=(c[1],mapping[c[0]])
    g=groups[k];v=[x['value'] for x in g]
    expected=[f"{g[0]['reference']['value']:.6f}",f'{statistics.mean(v):.6f}',f'{min(v):.6f}–{max(v):.6f}']
    s1.append({'author':k[0],'endpoint':k[1],'display':c[3:],'expected':expected,'pass':c[3:]==expected})
check('Table S1 all 12 rows/48 numeric entries', len(s1)==12 and all(x['pass'] for x in s1), s1)

q4=new.split('### 4.5.',1)[1].split('### 4.6.',1)[0]
keymeans=[]
for a,e in groups:
    if (a,8101,e) not in primary: continue
    v=[x['value'] for x in groups[(a,e)]]
    formatted=f'{statistics.mean(v):.5f}'
    keymeans.append({'author':a,'endpoint':e,'expected':formatted,'present':formatted in q4})
check('all 12 Q4 coefficient means correct', all(x['present'] for x in keymeans), keymeans)
diagkeys=[('C01','glucose_hba1c_pearson'),('C01','glucose_hba1c_spearman'),('E01','q1_residual_rms'),('E02','q1_residual_rms'),('E01','hba1c.sd_population'),('E02','hba1c.sd_population')]
diagtext=[]
for k in diagkeys:
    g=groups[k];value=statistics.mean([x['value'] for x in g]); f=f'{value:.3f}'
    diagtext.append({'author':k[0],'metric':k[1],'value':value,'formatted':f,'present':f in q4})
check('six Q4 diagnostic means correct',all(x['present'] for x in diagtext),diagtext)
check('all six ENSANUT BMI attenuation comparisons hold', all(next(a['value'] for a in s['analyses'] if a['id']=='Q2_bmi5')>next(a['value'] for a in s['analyses'] if a['id']=='Q3_bmi5') for s in slots if s['case_id']=='ENSANUT2018'))

diag=read(B/'display/ALL_DIAGNOSTICS.md')
dc=[]
for a in ['C01','C02','E01','E02']:
    block=diag.split('## '+a,1)[1].split('\n## ',1)[0]
    for line in re.findall(r'^\|.*\|$',block,flags=re.M)[2:]:
        c=[x.strip() for x in line.strip('|').split('|')]
        g=groups[(a,c[0])];v=[x['value'] for x in g]
        ex=[format(g[0]['reference']['value'],'.6g'),format(statistics.mean(v),'.6g'),format(min(v),'.6g')+'–'+format(max(v),'.6g')]
        dc.append({'author':a,'metric':c[0],'pass':c[2:]==ex})
check('linked diagnostics retain all 110 author-metric rows',len(dc)==110 and all(x['pass'] for x in dc), {'rows':len(dc),'failures':[x for x in dc if not x['pass']]})

refblock=new.split('## References',1)[1].split('## Supplementary results',1)[0]
refs={int(n):line for n,line in re.findall(r'^(\d+)\. (.*)$',refblock,flags=re.M)}
nonrefs=new.split('## References',1)[0]+new.split('## Supplementary results',1)[1]
cited=set()
for chunk in re.findall(r'\[([0-9,–\- ]+)\]',nonrefs):
    for item in chunk.split(','):
        q=re.split('[–-]',item); cited.update(range(int(q[0]),int(q[-1])+1))
check('24 numbered references, all callouts resolve',set(refs)==set(range(1,25)) and not (cited-set(refs)),{'cited':sorted(cited),'uncited':sorted(set(refs)-cited)})
check('all 24 references used in body or supplement',cited==set(range(1,25)))
oldrefs={int(n):line for n,line in re.findall(r'^(\d+)\. (.*)$',old.split('## References',1)[1],flags=re.M)}
check('original 15 bibliography entries unchanged',all(refs[n]==oldrefs[n] for n in range(1,16)))
s2=table(new,'S2').splitlines()[2:]
sourcerows=[]
for line in s2:
    c=[x.strip() for x in line.strip('|').split('|')]
    num=int(re.search(r'\[(\d+)\]',c[1]).group(1)); pmc=re.search(r'PMC\d+',c[1]).group(0)
    d=meta[pmc]; authorlist=c[2].split(', ')
    paths=[P.parents[1]/('evcRep'+a)/'sources/gateway'/(d['original_sha256']+'.xml') for a in d['authors']]
    t=ET.parse(paths[0]); m=t.find('.//article-meta')
    title=''.join(m.find('./title-group/article-title').itertext()); surname=m.find('./contrib-group/contrib/name/surname').text
    years=[x.text for x in m.findall('./pub-date/year')]
    doi=[x.text for x in m.findall('./article-id') if x.attrib.get('pub-id-type')=='doi']
    journal=''.join(t.find('.//journal-title').itertext())
    metadata_match=(title==d['title'] and surname==d['first_author'] and d['year'] in years and (doi[0] if doi else '')==d['doi'] and journal==d['journal'])
    source_author_match=sorted(authorlist)==sorted(d['authors'])==sorted([a['author_id'] for a in authors if pmc in a['source_ids']])
    source_hash_match=all(digest(x)==d['original_sha256'] for x in paths)
    ref_identity_match=surname in refs[num] and d['year'] in refs[num] and (pmc in refs[num] or d['doi'] in refs[num])
    sourcerows.append({'pmcid':pmc,'reference':num,'metadata_match':metadata_match,'source_author_match':source_author_match,'source_hash_match':source_hash_match,'reference_identity_match':ref_identity_match})
    for path in paths: bind(path)
check('Table S2 matches all 12 admitted originals and 16 author uses',len(sourcerows)==12 and all(all(v for k,v in x.items() if k.endswith('match')) for x in sourcerows),sourcerows)

links=re.findall(r'\]\(([^)]+)\)',new)
missing=[link for link in links if not re.match(r'https?://',link) and not (M/link).exists()]
check('all local manuscript links resolve',not missing,missing)
check('five primary figures plus supplementary S1',len(re.findall(r'^\*\*Figure [1-5]\.',new,flags=re.M))==5 and len(re.findall(r'^\*\*Figure S1\.',new,flags=re.M))==1)
for ext in ['svg','pdf','png']:
    check('old Figure 5 preserved as S1 '+ext,digest(M/'paper_figures_v12_2026-11-04'/('fig5-analysis-use.'+ext))==digest(F/('figS1-analysis-use.'+ext)))
oldcaption=re.search(r'^\*\*Figure 5\..*$',old,flags=re.M).group(0)
newcaption=re.search(r'^\*\*Figure S1\..*$',new,flags=re.M).group(0)
check('old Figure 5 caption retained as S1',oldcaption.replace('Figure 5.','Figure S1.',1)==newcaption)
fig=jread(F/'FIG5_NUMERIC_BINDINGS.json')
fchecks=[]
for row in fig['seed_values']:
    k=(row['author'],row['seed'],row['endpoint']);a=primary[k]
    s=next(s for s in slots if s['author_id']==k[0] and s['seed']==k[1])
    fchecks.append(row['value']==a['value'] and row['reference']==a['reference']['value'] and row['table_sha256']==s['table_sha256'])
check('Figure 5 data includes all 36 current primary estimates',len(fchecks)==36 and all(fchecks) and len({(r['author'],r['seed'],r['endpoint']) for r in fig['seed_values']})==36)
check('Figure 5 declared output hashes current',all(digest(F/name)==data['sha256'] for name,data in fig['outputs'].items()))

for rel in ['DRAFT_v0_12.md','DRAFT_v0_13.md','DRAFT_v0_9.md','SUPPLEMENT_HISTORICAL_RESULTS_v05.md']:
    bind(M/rel)
for rel in ['DRAFT_INTEGRATION_AUDIT.json','SOURCE_BIBLIOGRAPHIC_METADATA.json','independent_draft_checks.py']:
    bind(W/rel)
for rel in ['evaluation_v2/RESULTS.json','evaluation_v2/independent_numerical_audit/RESULTS.json','evaluation_v2/independent_numerical_audit/AUDIT_COMPLETED.json','INDEPENDENT_NUMERICAL_AUDIT.md','SCIENTIFIC_INTERPRETATION_REVIEW.md','PROTOCOL.json','display/ALL_DIAGNOSTICS.md','RESULTS.md','SOURCE_PROPOSAL_REVIEW_C01.md','SOURCE_PROPOSAL_REVIEW_C02.md','SOURCE_PROPOSAL_REVIEW_E01.md','SOURCE_PROPOSAL_REVIEW_E02.md','SOURCE_PROPOSAL_REVIEW_E02_ADDENDUM.md']:
    bind(B/rel)
for rel in ['FIG5_NUMERIC_BINDINGS.json','fig5-open-retrieval.svg','figS1-analysis-use.svg']:
    bind(F/rel)

out={'schema_version':'independent_manuscript_v13_review_v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'status':'PASS' if all(c['pass'] for c in checks) else 'NEEDS_CORRECTION','scope':'Frozen aggregates, local originals metadata, source reviews, draft comparison, link/citation and figure-data checks; no participant/generated table read, generation, clinical fit or network retrieval.',
     'counts':counts,'checks':checks,'sha256_bindings':bindings,'failed_checks':[c['name'] for c in checks if not c['pass']]}
out['reviewer']='/root/v13_draft_audit'
out['resolved_findings']=[
    {'finding':'References 8, 12 and 13 were uncited in the initial v0.13 condensation.', 'resolution':'Accurate original-packet and preceding five-source acquisition callouts added; all 24 references now cited.'},
    {'finding':'Earlier pre-freeze divergent-moment repair qualifier was removed from the initial Discussion.', 'resolution':'Restored explicitly, distinguishing repair from feedback-driven analytical gain.'}]
out['qualitative_review']={
    'abstract_contributions_Q4_discussion':'PASS: coherent developmental evidence-to-cohort contribution; no new estimator, universal Agent superiority, clinical-validation or revision-benefit claim.',
    'source_model_descriptions':'PASS: C01 age-conditioned multivariate-lognormal mixture, C02 copula predictors/affine response, E01 bounded beta/conditional gamma, and E02 lognormal BMI/truncated-normal glucose/conditional lognormal response agree with source-proposal reviews.',
    'information_boundary':'PASS: authors see intended analyses but not target values/signs/rows; both reference families remain explicitly historically exposed.',
    'adverse_results_preservation':'PASS: unchanged Q1-Q3 results/captions, byte-identical old seven-effect figure now S1, linked complete historical/open-search/resplit outputs, and all 110 new diagnostic summary rows remain available. Compression is not deletion of evidence.',
    'no_independent_sign_replications':'PASS: 36 slot-level signs are explicitly repeated measurements across six analysis definitions/four laws, not 36 independent confirmations.',
    'limits':'Numerical provenance and wording audit only. No new biological validation, author-host isolation proof, live URL availability check, or final PDF readability review.'}
(W/'INDEPENDENT_DRAFT_REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':out['status'],'checks':len(checks),'failed_checks':out['failed_checks']},indent=2))

"""Editorial v27 revision from unchanged v26; no data-generation or fit calls."""
from pathlib import Path
import hashlib, json, re

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
source = P / 'manuscript/DRAFT_v0_26.md'
old = source.read_text(encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'feba15e00a510598df145226c49e70c24ab3bd4483f26640fe4d9eadabec0f42'
text = old.replace('Methods working draft v0.26', 'Methods working draft v0.27', 1)
changes = []

def replace(before, after, reason):
    global text
    assert text.count(before) == 1, before[:100]
    text = text.replace(before, after, 1)
    changes.append(reason)

def paragraph(prefix, after, reason):
    matches = [p for p in text.split('\n\n') if p.startswith(prefix)]
    assert len(matches) == 1, prefix
    replace(matches[0], after, reason)

def section(file, heading):
    raw = (HERE/file).read_text(encoding='utf-8')
    marker = '## '+heading+'\n\n'
    assert raw.count(marker) == 1, (file, heading)
    return raw.split(marker,1)[1].split('\n## ',1)[0].strip()

# Old main Tables 1-3 shift by one to allow the operational method table.
main, remainder = text.split('## References\n', 1)
main = re.sub(r'\bTable ([123])\b', lambda m:'Table '+str(int(m[1])+1), main)
text = main + '## References\n' + remainder

paragraph('Biomedical studies often make aggregate findings',
'''Biomedical studies often make aggregate findings available while the individual measurements needed for a new analysis remain inaccessible. We study whether a scientific agent can turn such evidence and a research request into analyzable virtual cohorts. Within a host-reviewed workflow, the agent interprets study conditions, chooses a joint stochastic model, and supplies numerical relationships and explicit assumptions; statistical tools execute the model and inspect its outputs. In a developmental open-retrieval evaluation on previously exposed project references, four constructions produced twelve complete cohorts. All six requested glycemia analyses retained their sample-reference point directions across draws, with differing magnitude agreement; both constructions for one population preserved attenuation of the BMI coefficient after glucose adjustment. In a separate developmental two-case experiment with twenty agent constructions, the arms given additional published relationship evidence had smaller mean absolute discrepancy for five of six regression coefficients. Comparisons with a fixed statistical completion favored the agent arm in four of six relationship-evidence analyses. Iron-status and lipid results showed selected agreements alongside substantial joint-dependence and dispersion mismatches; the sealed iron comparison disagreed on its primary odds ratio, and an earlier prospective evaluation failed both overall criteria. These findings demonstrate evidence-to-model construction and partial agreement on specified analyses without target individual-level training records. Reliable inference for a new population remains unestablished.''',
'Bound abstract to host-reviewed construction and observed analysis properties')

position = (HERE/'POSITIONING_INSERT.md').read_text(encoding='utf-8')
contribution = position.split('Replace the final paragraph of the Introduction with:\n\n',1)[1].split('\n\n## ',1)[0]
paragraph('Our contribution is a concrete scientific-agent procedure', contribution,
          'State method, use-case and empirical contributions precisely')
replace('LLMSynthor uses aggregate discrepancies to guide proposals for new records and evaluates mobility, e-commerce and household population synthesis [5].',
        'LLMSynthor infers relevant variable dependencies and uses aggregate discrepancies to guide proposals for new records, with evaluations of downstream predictive utility and household population queries [5].',
        'Acknowledge LLMSynthor dependency inference and downstream evaluation')
replace('KMGen combines agentic extraction of published Kaplan–Meier curves with trial-record information and a mechanistic sampler to generate patient records with survival and adverse events [36].',
        'KMGen combines agentic extraction of published Kaplan–Meier curves and trial information with explicit clinical priors and a specified mechanistic sampler to generate patient survival and adverse-event records [36].',
        'Acknowledge KMGen clinical-prior and deterministic-sampler overlap')

replace('The coordinator supplies the task, handles access to papers and tools, binds program versions to their results, and fixes the seeds for delivery. It can request scientific or implementation review.',
        'The coordinator supplies the task, handles access to papers and tools, binds program versions to their results, and fixes the seeds for delivery. Review requirements are part of the study protocol: Q4 requires source-proposal review, candidate checks before each freeze, and a review bound to the final selection. Table 1 identifies the actors and these stages.',
        'Make required Q4 review explicit in main method')
replace('Supplement S12 identifies the implementation paths.',
        'The host-reviewed stages are specified in Table 1; Supplement S12 identifies the implementation paths. The loop permits revision, while the Q4 and Q5 authors retained their first reviewed, frozen laws.',
        'Qualify Figure 1 with actual review and retained-model evidence')
replace('## 3. How a scientific agent constructs an analyzable cohort',
        section('METHOD_INSERT.md','Main-text insertion').replace('Supplement S12','Supplement S17')+'\n\n## 3. How a scientific agent constructs an analyzable cohort',
        'Add operational responsibility table')

paragraph('An analysis can be rerun from a delivered table',
'''An analysis can be rerun from a delivered table without asking the agent to refit the model to that result. We distinguish successful execution, agreement of a specified point estimate or association pattern, and adequacy for a scientific decision. Our evaluations report the first two, including discrepancies; they do not set a general acceptance threshold for the third. For a threshold analysis the evaluator classifies each generated and measured pair using the same cutoffs. For continuous dependence it uses the original paired concentrations and their ranks. Agreement on threshold counts leaves room for differences in continuous ranks. Table 5 summarizes the demonstrated properties and the uses that remain unvalidated. Marginal and residual variation are reported where available.''',
'Define execution, point-property agreement and decision adequacy separately')
replace('These sources of variation answer different questions and are shown separately in the results.',
        'These sources of variation answer different questions and are shown separately in the results. Standard errors or tests obtained by treating the synthetic rows as sampled patients do not automatically include uncertainty in source estimates, model selection or population transfer. The present evaluation does not validate confidence-interval coverage, power calculations or clinical decisions from those rows. A data-use statement should identify the synthetic status, source-supported and assumed properties, evaluated analyses, and the uncertainty omitted from any reported interval.',
        'State practical consequences of omitted source and transfer uncertainty')

replace('The reference conditions differ.',
        'Supplement S16 gives the eligibility, measurement selection, weighting and uncertainty definition for each reference. In particular, the ENSANUT estimand uses selected adults without a reported prior diabetes diagnosis, with a recorded 8–12-hour fast and serum glucose below 126 mg/dL, and equal mass in eight age-by-sex cells. It is not a nationally weighted adult-population regression.\n\nThe reference conditions differ.',
        'Expose material ENSANUT restrictions and link all reference definitions')
replace('Both authors therefore produced useful associations, with different magnitude trade-offs (Figure 3).',
        'Both authors preserved the three reference point directions, with different magnitude discrepancies across analyses (Figure 3).',
        'Replace unqualified useful-association wording with observed properties')
replace('the agent arms given these additional relationships (E1) had smaller mean absolute discrepancies',
        'the sampled agent arms given these additional relationships (E1) had smaller mean absolute discrepancies',
        'Keep information contrast descriptive')
replace('A study of individual heterogeneity or the tails would need additional validation.',
        'The lower residual variation also limits inferential uses: a close slope does not establish calibrated standard errors, confidence intervals or power. Studies of individual heterogeneity and tails likewise require their own validation.',
        'Connect underdispersion to intended inferential use')

replace('## 6. Discussion', section('USE_INSERT.md','Main-text table').replace('effect of supplying relationship evidence','comparison with additional relationship evidence')+'\n\n## 6. Discussion',
        'Add use-specific observed-properties table')
paragraph('The strongest use demonstrated here is',
'''The central result is repeated conversion of incomplete scientific information into executable cohorts with partial agreement on specified analyses. In the open-retrieval cases, different authored models preserved several effect magnitudes and the reduction in the BMI coefficient after glucose adjustment. In the separate information experiment, arms given relationship evidence had smaller discrepancies on five of six analyses. These findings locate practical value in the evidence-to-model construction: the user can specify the research problem without first writing a complete joint generator. The host-reviewed workflow and its outcomes do not yet establish how reliably a new user can obtain an accurate scientific inference without a target comparison.''',
'Calibrate discussion to demonstrated construction and point properties')
replace('Some historical dispatches record an inherited host model without the exact backend identity, limiting model-specific reproduction and attribution.',
        'Author-model metadata are incomplete in central experiments: the Q1 dispatches record an inherited host model without its exact backend identity, and Q4 records fresh author contexts without a complete model/inference configuration. Supplement S17 separates program replay from reproduction of original authoring sessions and identifies the recorded budgets and review stages.',
        'Identify central model metadata gaps explicitly')
replace('This manuscript revision reorganizes existing frozen results and promotes the complete open-retrieval analysis display. No new clinical cohort was generated or target refitted.',
        'This manuscript revision clarifies analysis-use claims, operational roles, reference definitions and reproducibility using existing frozen results. No new clinical cohort was generated or target refitted.',
        'Update revision scope')
replace('All four retained the initial law.',
        'All four retained the first reviewed, frozen law. This retention decision follows the required proposal and pre-freeze reviews; it does not imply that the original unreviewed response received no correction.',
        'Define Q4 initial-stage retention accurately')
replace('Both approaches demonstrated the usefulness of constructing a joint table from accessible aggregate information.',
        'Both approaches reconstructed the displayed joint statistics from accessible aggregate information.',
        'Specify supplied-summary reconstruction achievement')
replace('The evidence therefore supports scientific utility and the value of additional information, rather than a universal algorithmic ranking.',
        'The observed contrasts support the reported analysis-specific agreements and a descriptive association between added relationship information and smaller errors in these sampled arms.',
        'Avoid general scientific-utility conclusion from fixed comparison')
replace('The resplits do not define population truth, independent cohorts or prespecified acceptable margins.',
        'The resplits do not define population truth, independent cohorts or prespecified acceptable margins. The distances also have different geometry: real–real compares two complementary estimates, whereas the symmetric generated discrepancy averages distances from a fixed generated estimate to each. For illustrative estimates m+d and m−d and a generated estimate m, those distances are 2|d| and |d|. This identity is not an equality asserted for the fitted regressions; it explains why the comparison cannot itself supply an equivalence threshold.',
        'Explain real-real distance asymmetry')

# New tables follow existing S8. Inserts are authored separately from source audit notes.
text += '\n\n### S16. Reference populations and estimands\n\n'+section('REFERENCE_INSERT.md','Supplement insertion')
text += '\n\n### S17. Authoring and reproducibility conditions\n\n'+section('METHOD_INSERT.md','Supplement insertion')+'\n'
text += '\nIn Q4 the host/root Agent performed source and static reviews; Q5 also used separately dispatched review Agents, with final decisions reviewed by the root coordinator. A distinct review role does not imply a different model family or a reviewer unexposed to earlier project results. The Q4 record distinguishes source-transcription corrections, such as two printed residual variances, from a mechanical path-name repair and from a post-trial change of scientific law.\n'
target=P/'manuscript/DRAFT_v0_27.md'
target.write_text(text,encoding='utf-8')
facts={'input':'manuscript/DRAFT_v0_26.md','input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
       'output':'manuscript/DRAFT_v0_27.md','output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
       'changes':changes,'new_clinical_experiments':0,'new_primary_numbers':False,
       'all_existing_numeric_tables_and_figure_assets_retained':True}
(HERE/'REVISION_FACTS.json').write_text(json.dumps(facts,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'draft':str(target),'changes':len(changes),'sha256':facts['output_sha256']}))

"""Read-only pre-evaluation completeness and paired-input audit; no target analysis."""
import json
from pathlib import Path
import runner
from source_checks import read

def main():
    runner.verify_freeze()
    root=runner.ROOT; failures=[]; inspected=[]
    for case in runner.CASE_IDS:
        for build in range(1,4):
            lineage=root/'runs'/case/f'build_{build:02d}'
            # Exactly one accepted final per branch. Repairs remain on disk but
            # cannot silently yield multiple eligible final arms.
            parents=[]
            for branch in ['ordinary','proposed']:
                candidates=list(lineage.glob(branch+'_*/final/manifest.json'))
                if len(candidates)!=1:
                    failures.append(f'{case} build {build} {branch}: expected one final manifest, found {len(candidates)}'); continue
                p=candidates[0]; manifest=read(p); run=p.parent.parent
                runner.verify_files(p.parent,manifest['files'])
                candidate=read(run/'candidate_manifest.json'); runner.verify_files(run,candidate['files'])
                if runner.sha(run/'candidate_manifest.json')!=manifest['candidate_manifest_sha256']: failures.append('Candidate commitment changed: '+str(run))
                parents.append(read(run/'task.json')['parent'])
                if len(manifest['records'])!=20: failures.append('Final budget differs: '+str(run))
                inspected.append(dict(run_id=manifest['task']['run_id'],saved=manifest['cohorts_saved'],requested=20))
            if len(parents)==2 and parents[0]!=parents[1]: failures.append(f'Paired branches differ in common parent: {case} build {build}')
        candidates=list((root/'statistical'/case).glob('fixed/statistical_*/final/manifest.json'))
        if len(candidates)!=1: failures.append(f'{case}: expected one fixed statistical final'); continue
        p=candidates[0]; manifest=read(p); runner.verify_files(p.parent,manifest['files'])
        if manifest['scenario_allocation']!={'rho_0':7,'rho_04':7,'rho_08':6}: failures.append(f'{case}: statistical sensitivity allocation changed')
        inspected.append(dict(run_id=manifest['task']['run_id'],saved=manifest['cohorts_saved'],requested=20))
    result=dict(status='passed' if not failures else 'incomplete_or_failed',n_final_arms=len(inspected),requested_cohorts=sum(x['requested'] for x in inspected),saved_cohorts=sum(x['saved'] for x in inspected),arms=inspected,failures=failures,target_analyses_loaded=False)
    print(json.dumps(result,indent=2))
    if failures: raise SystemExit(1)

if __name__=='__main__': main()

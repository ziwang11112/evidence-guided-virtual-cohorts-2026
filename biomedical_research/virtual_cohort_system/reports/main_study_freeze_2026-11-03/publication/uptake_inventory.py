"""Report the declared and independently reviewed evidence uses of every author."""
from pathlib import Path
import argparse
import sys
UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT/'implementation'))
import main_session_v1 as c

def inventory(release_path,output):
    release=c.READ(release_path);c.require_campaign_closed(release)
    rows=[]
    for item in release['constructions']:
        s=c.Session(item['session_root']);selection=s.selected('science_closed')
        base={'constructor_id':item['id'],'case':s.contract['case_id'],'arm':s.contract['information_condition'],
              'constructor_kind':s.contract['constructor_kind'],'closed_status':s.selected('closed')[0]['status']}
        if not selection:
            rows.append({**base,'candidate':None,'status':'no_selected_candidate','operations':[]});continue
        chosen=selection[0];c.verify_bound(chosen['decision']);c.verify_bound(chosen['review'])
        candidate=s.bundle/chosen['candidate'];raw=c.READ(candidate/'numerical_uptake.json')
        decision=c.READ(chosen['decision']['path']);review=c.READ(chosen['review']['path'])
        operations=[]
        for record in raw['records']:
            operations.append({'operation_id':record.get('operation_id'),'use':record.get('use'),
                               'complete_record':record})
        counts={kind:sum(r['use']==kind for r in operations) for kind in ['model_constraint','analytic_check','context_only','declined']}
        rows.append({**base,'candidate':chosen['candidate'],'action':decision['action'],'uptake_sha256':c.SHA(candidate/'numerical_uptake.json'),
                     'review_sha256':chosen['review']['sha256'],'review_status':review['status'],'operation_use_counts':counts,
                     'operations':operations,'review_findings':review['findings']})
    result={'release':c.bound(release_path),'created_utc':c.now(),'constructions':rows,
            'interpretation':'Counts describe declared, reviewed operation use, not independent evidence counts or target validity. Unit duplicates and overlapping source cohorts remain non-independent. Model constraints and analytic checks use explicitly assumed source contexts; target-table source replay is unavailable in this allocation. No-op decisions are not revision gains.'}
    c.WRITE(Path(output),result)
    return len(rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--release',required=True);p.add_argument('--output',required=True);a=p.parse_args();print(inventory(a.release,a.output))

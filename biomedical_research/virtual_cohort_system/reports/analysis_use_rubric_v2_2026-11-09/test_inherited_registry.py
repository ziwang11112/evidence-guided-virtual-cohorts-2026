"""Regression for imported evidence versus a session's own approved downloads."""
import hashlib
import json
import pytest
from cohort_harness.demo import make_demo
from cohort_harness import web_evidence_v1 as web
from cohort_harness.contracts import ContractError

@pytest.mark.parametrize('prefix,accepted', [
    ('sources/web_evidence_v1/',False),
    ('sources/curated/inherited_web_v1/',True),
])
def test_inherited_bytes_need_curated_namespace(tmp_path,prefix,accepted):
    root=make_demo(tmp_path/'case')
    raw=b'Invented inherited source; no network access.'
    digest=hashlib.sha256(raw).hexdigest()
    relative=prefix+digest+'.txt'
    path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    registry=json.loads((root/'registry.json').read_text())
    registry['artifacts'].append({'source_id':'inherited','path':relative,'sha256':digest,'origin':'curator','screening':'approved'})
    (root/'registry.json').write_text(json.dumps(registry))
    result=web.init(root)
    assert result['status']=='ok'
    if accepted:
        state=web.verify(root)
        assert state['registrations']==[] and state['retrievals']=={}
        assert state['usage']['downloads']==0
    else:
        with pytest.raises(ContractError,match='Web registry entries lack bound approval'):
            web.verify(root)

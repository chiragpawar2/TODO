import sys
sys.path.insert(0,'.')
from tests import conversations as C
from homebot.face import reading as R
convs = getattr(C,'CONVERSATIONS',None) or getattr(C,'CONVS',None)
if convs is None:
    convs=[v for k,v in vars(C).items() if isinstance(v,list) and v and isinstance(v[0],(list,dict,tuple))][0]
for c in convs:
    turns = c['turns'] if isinstance(c,dict) else c[-1] if isinstance(c,tuple) else c
    for t in turns:
        if t.get('kind')!='user': continue
        n,l,_,why=R.read(t['text'])
        if n not in t['expected'] or l not in t['level']:
            print(repr(t['text'][:90]), n,l,why,'| want',sorted(t['expected']),sorted(t['level']))

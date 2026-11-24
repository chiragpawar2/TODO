import json,sys
from homebot.face import reading as R
from homebot.face.visemes import VisemeTrack as V
out=[]
for t in open(sys.argv[1]).read().splitlines():
    if not t: continue
    b=R.read_beats(t,model=False); v=V(t)
    out.append({"t":t,"beats":[[x[0],x[1]] for x in b],"cues":v.debug(),"dur":round(v.duration,3)})
print(json.dumps(out,ensure_ascii=False))

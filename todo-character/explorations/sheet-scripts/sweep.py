"""Find the bloom strength and emitter that reproduce the reference's own
bright/mid/dim values, instead of guessing and re-rendering by eye."""
import pygame, sys, itertools
pygame.init(); pygame.display.set_mode((8,8))
import homebot.face.renderer as R
from homebot.face import expressions
from homebot.face.params import sanitise
from PIL import Image
import numpy as np

REF = {'bright':(233,248,253),'mid':(193,208,231),'dim':(107,136,188)}

def sample(surf):
    a = pygame.surfarray.array3d(surf).transpose(1,0,2).astype(float)
    # the left eye's lit interior, away from the pupil and the outer fringe
    box = a[175:250, 135:205].reshape(-1,3)
    lit = box[box.sum(1) > 150]
    if len(lit) < 50: return None
    s = lit[lit[:,2].argsort()]
    n = len(s)
    return {'bright':s[int(n*.95)],'mid':s[n//2],'dim':s[int(n*.10)]}

def err(got):
    if got is None: return 1e9
    e = 0
    for k,v in REF.items():
        e += sum((float(got[k][i]) - v[i])**2 for i in range(3))
    return e**.5

best=None
for gr,gg in [(150,196),(168,212),(185,222),(200,232)]:
    for k in (0.18,0.26,0.34,0.42,0.52):
        R.GLOW=(gr,gg,255)
        src=open('homebot/face/renderer.py').read()
        R._BLOOM_K = k
        rnd = R.FaceRenderer((760,480))
        # monkeypatch the strength constant for this trial
        orig = R.FaceRenderer._bloom
        def bl(self, layer, out, strength, _k=k, _o=orig):
            return _o(self, layer, out, strength*_k/0.62)
        R.FaceRenderer._bloom = bl
        surf = rnd.render(sanitise(expressions.get("rest")))
        R.FaceRenderer._bloom = orig
        got = sample(surf); e = err(got)
        if best is None or e < best[0]: best=(e,(gr,gg),k,got)
print("best err %.1f  GLOW=(%d,%d,255)  bloom k=%.2f" % (best[0],best[1][0],best[1][1],best[2]))
for kk in ('bright','mid','dim'):
    print(f"  {kk:7} ref {REF[kk]}  ours {tuple(int(v) for v in best[3][kk])}")

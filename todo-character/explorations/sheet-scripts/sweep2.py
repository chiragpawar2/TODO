import pygame
pygame.init(); pygame.display.set_mode((8,8))
import homebot.face.renderer as R
from homebot.face import expressions
from homebot.face.params import sanitise

REF = {'bright':(233,248,253),'mid':(193,208,231),'dim':(107,136,188)}

def sample(surf):
    a = pygame.surfarray.array3d(surf).transpose(1,0,2).astype(float)
    box = a[175:250, 135:205].reshape(-1,3)
    lit = box[box.sum(1) > 150]
    if len(lit) < 50: return None
    s = lit[lit[:,2].argsort()]; n=len(s)
    return {'bright':s[int(n*.95)],'mid':s[n//2],'dim':s[int(n*.10)]}

def err(g):
    if g is None: return 1e9
    return sum(sum((float(g[k][i])-REF[k][i])**2 for i in range(3)) for k in REF)**.5

orig = R.FaceRenderer._bloom
best=None
for glow in [(225,240,255),(235,247,255),(245,251,255),(252,253,255)]:
  for tint in [(70,140,255),(100,165,255),(130,190,255),(160,205,255)]:
    for k in (0.22,0.30,0.40,0.52,0.66):
        R.GLOW = glow
        def bl(self, layer, out, strength, _k=k, _t=tint):
            d=max(2,self.q.bloom_div)
            t1=pygame.transform.smoothscale(layer,(self.w//d,self.h//d))
            t1=pygame.transform.smoothscale(t1,(self.w,self.h))
            wd=d*2
            w1=pygame.transform.smoothscale(layer,(max(1,self.w//wd),max(1,self.h//wd)))
            w1=pygame.transform.smoothscale(w1,(self.w,self.h))
            w1.fill((120,120,120,255),None,pygame.BLEND_RGB_MULT)
            t1.blit(w1,(0,0),special_flags=pygame.BLEND_RGB_ADD)
            kk=max(0.0,min(1.0,_k*strength))
            t1.fill((int(_t[0]*kk),int(_t[1]*kk),int(_t[2]*kk),255),None,pygame.BLEND_RGB_MULT)
            out.blit(t1,(0,0),special_flags=pygame.BLEND_RGB_ADD)
        R.FaceRenderer._bloom = bl
        surf = R.FaceRenderer((760,480)).render(sanitise(expressions.get("rest")))
        e = err(sample(surf))
        if best is None or e < best[0]: best=(e,glow,tint,k,sample(surf))
R.FaceRenderer._bloom = orig
print("best err %.1f" % best[0])
print("  GLOW =", best[1]); print("  tint =", best[2]); print("  k    =", best[3])
for kk in ('bright','mid','dim'):
    print(f"  {kk:7} ref {REF[kk]}  ours {tuple(int(v) for v in best[4][kk])}")

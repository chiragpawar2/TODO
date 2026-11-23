"""Show what BLENDING buys: the row ends are named poses, everything between
is a state nobody designed."""
import pygame,sys
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face import expressions as E
from homebot.face.params import sanitise
PAIRS=[("bored","happy"),("angry","sad"),("tender","alarmed"),("delight","worried")]
W,H=330,206; pad=8; N=5
r=FaceRenderer((W,H)); f=pygame.font.SysFont("menlo,monospace",17)
sh=pygame.Surface((N*(W+pad)+pad, len(PAIRS)*(H+pad+24)+pad)); sh.fill((10,10,12))
for row,(a,b) in enumerate(PAIRS):
    pa,pb=E.get(a),E.get(b)
    for i in range(N):
        t=i/(N-1)
        s=r.render(sanitise(pa.blend(pb,t)))
        x=pad+i*(W+pad); y=pad+row*(H+pad+24)
        sh.blit(s,(x,y))
        lab=a if i==0 else (b if i==N-1 else f"{int((1-t)*100)}/{int(t*100)}")
        col=(150,206,255) if i in (0,N-1) else (120,130,145)
        sh.blit(f.render(lab,True,col),(x+5,y+H+3))
pygame.image.save(sh,sys.argv[1]); print("ok",sh.get_size())

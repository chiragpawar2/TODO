import pygame,sys
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face import expressions
from homebot.face.params import sanitise
NAMES=["grin","oh","dread","suspicious","stern","fret","content","crying","tender","alarmed","peek","attentive","drowsy"]
W,H=400,250; pad=12
r=FaceRenderer((W,H))
f=pygame.font.SysFont("menlo,monospace",20)
cols,rows=5,3
sheet=pygame.Surface((cols*(W+pad)+pad, rows*(H+pad+26)+pad)); sheet.fill((10,10,12))
for i,n in enumerate(NAMES):
    p=expressions.get(n)
    if n=="crying": p.tear=1.0; p.tear_fall=0.55
    s=r.render(sanitise(p))
    x=pad+(i%cols)*(W+pad); y=pad+(i//cols)*(H+pad+26)
    sheet.blit(s,(x,y)); sheet.blit(f.render(n,True,(150,206,255)),(x+6,y+H+4))
pygame.image.save(sheet,sys.argv[1]); print("ok",sheet.get_size())

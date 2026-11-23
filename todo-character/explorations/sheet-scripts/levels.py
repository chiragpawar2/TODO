"""Three levels of four expressions, with the sentence that triggers each."""
import pygame,sys
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face import expressions as E
from homebot.face.params import sanitise
ROWS=[("happy",["i am a bit happy","i am happy","I am SO HAPPY!!!"]),
      ("angry",["im slightly annoyed","i am annoyed","I AM SO ANNOYED!!!"]),
      ("delight",["nice one","great news","yay we did it!!!"]),
      ("sad",["a bit down","i feel sad","I AM SO SAD!!!"])]
W,H=360,225; pad=10; LAB=46
r=FaceRenderer((W,H))
f=pygame.font.SysFont("menlo,monospace",18); g=pygame.font.SysFont("menlo,monospace",15)
sh=pygame.Surface((3*(W+pad)+pad, len(ROWS)*(H+pad+LAB)+pad)); sh.fill((10,10,12))
for row,(name,sents) in enumerate(ROWS):
    for i,lvl in enumerate(("low","mid","intense")):
        amt=E.level_amount(name,lvl)
        p=E.get("rest").blend(E.get(name),amt)
        full=E.get(name)
        if full.mouth_alpha<0.02: p.mouth_alpha=0.0
        for a,b in ((full.left,p.left),(full.right,p.right)):
            if a.pupil_alpha<0.02: b.pupil_alpha=0.0
        x=pad+i*(W+pad); y=pad+row*(H+pad+LAB)
        sh.blit(r.render(sanitise(p)),(x,y))
        sh.blit(f.render(f"{name} {lvl}  x{amt:.2f}",True,(150,206,255)),(x+5,y+H+4))
        sh.blit(g.render('"'+sents[i]+'"',True,(120,130,145)),(x+5,y+H+24))
pygame.image.save(sh,sys.argv[1]); print("ok",sh.get_size())

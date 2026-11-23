import pygame, sys
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face import expressions as E
from homebot.face.visemes import SHAPES, VisemeTrack, word_shapes
from homebot.face.params import sanitise

DESC={'X':'rest, lips relaxed','A':'closed, pressed   P B M','B':'slightly open, teeth   K S T, EE',
 'C':'open   EH (men), AE (bat)','D':'wide open   AA (father)','E':'rounded   AO (off), ER (bird)',
 'F':'puckered   UW (you), OW, W','G':'teeth on lip   F V','H':'L, tongue up'}
W,H=300,188
r=FaceRenderer((W,H))
f=pygame.font.SysFont("menlo,monospace",15); fb=pygame.font.SysFont("menlo,monospace",26,bold=True)
order=['X','A','B','C','D','E','F','G','H']
cols=3; rows=3; pad=8; LBL=44
sheet=pygame.Surface((cols*(W+pad)+pad, rows*(H+pad+LBL)+pad+40)); sheet.fill((20,20,22))
sheet.blit(fb.render("The nine mouth shapes",True,(235,190,120)),(pad+2,6))
for i,sh in enumerate(order):
    o,wd,_=SHAPES[sh]
    p=E.get('rest').copy(); p.mouth_open=o; p.mouth_w*=wd
    x=pad+(i%cols)*(W+pad); y=40+pad+(i//cols)*(H+pad+LBL)
    sheet.blit(r.render(sanitise(p)),(x,y))
    sheet.blit(fb.render(sh,True,(255,170,60)),(x+4,y+H+2))
    sheet.blit(f.render(DESC[sh],True,(170,168,172)),(x+34,y+H+8))
pygame.image.save(sheet,sys.argv[1])

# word strip
word=sys.argv[3] if len(sys.argv)>3 else "chapati"
shp=word_shapes(word)
W2,H2=250,156
r2=FaceRenderer((W2,H2))
strip=pygame.Surface((len(shp)*(W2+pad)+pad, H2+pad*2+54)); strip.fill((20,20,22))
strip.blit(fb.render(f'"{word}"  ->  {" ".join(shp)}',True,(235,190,120)),(pad,6))
for i,sh in enumerate(shp):
    o,wd,_=SHAPES[sh]
    p=E.get('answering').copy(); p.mouth_open=o; p.mouth_w*=wd
    x=pad+i*(W2+pad)
    strip.blit(r2.render(sanitise(p)),(x,44))
    strip.blit(fb.render(sh,True,(255,170,60)),(x+4,44+H2+2))
pygame.image.save(strip,sys.argv[2]); print("ok")

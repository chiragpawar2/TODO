import pygame, time, sys
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face.animator import Animator
r = FaceRenderer((320,200)); a = Animator(r)
rows=[]
f = pygame.font.SysFont("menlo,monospace", 15)
script=[("rest",0.0),("listening",0.35),("thinking",0.9),("searching",1.5),
        ("delight",2.1),("rest",2.7)]
N=10
for label,_ in script[:-1]:
    pass
seqs=[]
for i in range(len(script)-1):
    a.set(script[i+1][0])
    frames=[]
    t0=time.monotonic()
    for k in range(N):
        while time.monotonic()-t0 < k*0.045: pass
        frames.append(r.render(a.update()).copy())
    seqs.append((f"{script[i][0]} -> {script[i+1][0]}", frames))
pad=6
W=N*(320+pad)+pad; H=len(seqs)*(200+pad+20)+pad
sheet=pygame.Surface((W,H)); sheet.fill((18,18,20))
for row,(label,frames) in enumerate(seqs):
    y=pad+row*(200+pad+20)
    for c,fr in enumerate(frames):
        sheet.blit(fr,(pad+c*(320+pad), y))
    sheet.blit(f.render(label, True,(205,205,210)),(pad+2,y+202))
pygame.image.save(sheet, sys.argv[1]); print("ok", sheet.get_size())

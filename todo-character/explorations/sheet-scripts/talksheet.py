import pygame, sys
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face import expressions as E
from homebot.face.visemes import VisemeTrack
from homebot.face.params import sanitise

W,H=264,165; COLS=7
names=[n for n in E.names() if n!='blink']
names = names[:15] if sys.argv[2]=='a' else names[15:]
r=FaceRenderer((W,H))
f=pygame.font.SysFont("menlo,monospace",14); fb=pygame.font.SysFont("menlo,monospace",14,bold=True)
pad=5; LBL=19
sheet=pygame.Surface((COLS*(W+pad)+pad+118, len(names)*(H+pad+LBL)+pad))
sheet.fill((20,20,22))
PHRASE="Namaste Aai, I added chapati."
for row,n in enumerate(names):
    t=E.talk(n); u=VisemeTrack(PHRASE, t[6] if isinstance(t,list) else t.rate,
                               t[7] if isinstance(t,list) else t.crisp)
    # One cue per DISTINCT shape the phrase uses, so the row shows the range
    # rather than whichever cues happen to fall on an even index.
    seen={}
    for c in u.cues:
        seen.setdefault(c.shape, c)
    order=['X','A','B','G','C','H','D','E','F']
    picks=[seen[s_] for s_ in order if s_ in seen][:COLS]
    while len(picks)<COLS: picks.append(picks[-1])
    y=pad+row*(H+pad+LBL)
    for c,cue in enumerate(picks):
        st=(cue.t0+cue.t1)/2
        p=E.get(n).copy()
        vo,vw=u.mouth(st); amp=u.energy(st); acc=u.accent(st); sw=u.breath(st)
        p.mouth_open=max(p.mouth_open, min(1.1, vo*(t.open_max/0.60)))
        p.mouth_w*= vw*(1+(t.width-1)*amp)
        p.shift_y-= t.bob*(.65*amp+.35*acc); p.tilt+=t.sway*sw
        p.glow   *= 1+t.glow_pulse*amp
        for e in (p.left,p.right):
            e.h*=1-t.squint*amp; e.pupil_y+=.07*t.accent*acc
            e.upper_lid=max(e.upper_lid,.10*t.accent*acc)
        x=118+pad+c*(W+pad)
        sheet.blit(r.render(sanitise(p)),(x,y))
        sheet.blit(fb.render(cue.shape,True,(255,170,60)),(x+4,y+4))
    sheet.blit(f.render(n,True,(230,180,110)),(8,y+H//2-8))
    sheet.blit(f.render(f"rate {t.rate:.1f}  crisp {t.crisp:.2f}  open x{t.open_max/0.60:.2f}",
               True,(110,108,112)),(118+pad, y+H+3))
pygame.image.save(sheet,sys.argv[1]); print("ok",sheet.get_size())

import pygame, time, sys
from PIL import Image
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face.animator import Animator

W,H = 384,240
r = FaceRenderer((W,H)); a = Animator(r)
FPS = 18
# A short story: wake, listen, think, look it up, answer, be pleased, get
# poked, sleep. Every state the real loop goes through.
script = [("rest",1.2),("listening",1.4),("thinking",1.5),("searching",1.3),
          ("answering",1.2),("delight",1.3),("curious",0.9),("love",1.1),
          ("confusion",1.0),("apologetic",1.1),("yawn",1.0),("asleep",2.0)]
frames=[]
t0=time.monotonic()
for name,dur in script:
    a.set(name)
    n=int(dur*FPS)
    for k in range(n):
        target = t0 + len(frames)/FPS
        while time.monotonic() < target: pass
        surf = r.render(a.update())
        frames.append(Image.frombytes("RGB",(W,H),
                      pygame.image.tostring(surf,"RGB")))
out = sys.argv[1]
frames[0].save(out, save_all=True, append_images=frames[1:],
               duration=int(1000/FPS), loop=0, optimize=True)
print("frames", len(frames))

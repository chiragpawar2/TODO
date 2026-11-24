import pygame, time, sys
from PIL import Image
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face.animator import Animator
W,H=384,240; FPS=24          # lip sync needs 24, not 20
r=FaceRenderer((W,H)); a=Animator(r)
f=pygame.font.SysFont("menlo,monospace",13)
script=[("answering","Namaste Aai. I added chapati to the list."),
        ("delight","Namaste Aai! I added chapati to the list."),
        ("apologetic","Namaste Aai. I added chapati to the list.")]
frames=[]; t0=time.monotonic()
for mood,line in script:
    a.set(mood); a._t0=time.monotonic()
    for k in range(int(0.6*FPS)):
        while time.monotonic() < t0+len(frames)/FPS: pass
        s=r.render(a.update()).copy(); s.blit(f.render(mood,True,(150,120,80)),(8,H-20))
        frames.append(s)
    d=a.speak(line)
    for k in range(int((d+0.4)*FPS)):
        while time.monotonic() < t0+len(frames)/FPS: pass
        s=r.render(a.update()).copy(); s.blit(f.render(mood,True,(150,120,80)),(8,H-20))
        frames.append(s)
imgs=[Image.frombytes("RGB",(W,H),pygame.image.tobytes(s,"RGB")) for s in frames]
imgs[0].save(sys.argv[1],save_all=True,append_images=imgs[1:],
             duration=int(1000/FPS),loop=0,optimize=True)
print("frames",len(imgs))

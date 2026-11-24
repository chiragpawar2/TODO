import pygame,sys
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face import expressions
from homebot.face.params import sanitise
r=FaceRenderer((760,480))
p=expressions.get(sys.argv[2] if len(sys.argv)>2 else "rest")
pygame.image.save(r.render(sanitise(p)),sys.argv[1]); print("ok")

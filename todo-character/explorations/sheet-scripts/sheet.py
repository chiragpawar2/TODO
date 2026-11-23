import pygame, math, sys
pygame.init(); pygame.display.set_mode((8,8))
from homebot.face.renderer import FaceRenderer
from homebot.face import expressions
names = expressions.names()
r = FaceRenderer((400,250))
cols, rows = 5, math.ceil(len(names)/5)
pad=10
sheet = pygame.Surface((cols*(400+pad)+pad, rows*(250+pad+20)+pad))
sheet.fill((20,20,22))
f = pygame.font.SysFont("menlo,monospace", 18)
for i,n in enumerate(names):
    s = r.render(expressions.get(n))
    x = pad + (i%cols)*(400+pad); y = pad + (i//cols)*(250+pad+20)
    sheet.blit(s,(x,y)); sheet.blit(f.render(n, True, (200,200,205)), (x+4, y+252))
pygame.image.save(sheet, sys.argv[1])
print("ok")

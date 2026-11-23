from PIL import Image; import sys
def lum(c): return .2126*c[0]+.7152*c[1]+.0722*c[2]
def avg(l):
    r=g=b=0
    for c in l: r+=c[0]; g+=c[1]; b+=c[2]
    k=len(l); return (round(r/k),round(g/k),round(b/k))
def prof(path,box):
    im=Image.open(path).convert('RGB'); px=im.load()
    x0,y0,x1,y1=box
    cols=[px[x,y] for y in range(y0,y1,2) for x in range(x0,x1,2)]
    s=sorted(cols,key=lum,reverse=True); n=len(s)
    return {'core':avg(s[:max(1,n//200)]),'halo':avg(s[n//20:n*15//100]),
            'outer':avg(s[n*15//100:n*35//100]),'panel':avg(s[int(n*.8):])}
REF='/private/tmp/claude-501/-Users-chirag-pawar-Desktop-Personal-TODO/3650b55e-1c4f-4d15-97fa-d7b0f4e7cbee/images/9.png'
r=prof(REF,(95,100,645,575)); m=prof(sys.argv[1],(0,0,760,480))
print(f"{'':8}{'reference':>18}{'ours':>18}")
for k in ('core','halo','outer','panel'):
    print(f"{k:8}{str(r[k]):>18}{str(m[k]):>18}")

"""Compare the glow falloff of two faces apples-to-apples.

Percentile buckets over a whole frame are useless here: the two images frame
the face at different sizes, so the same bucket covers different amounts of
empty black. Instead walk OUTWARD from the eye's outer edge, in units of the
eye's own half-width, which is scale-free.
"""
from PIL import Image
import sys

def profile(path, cx, cy, hw, label):
    px = Image.open(path).convert('RGB').load()
    print(f"\n{label}")
    print(f"{'from centre':>12}  colour")
    for mult in (0.0, 0.5, 0.95, 1.10, 1.25, 1.45, 1.75, 2.10):
        x = int(cx - hw * mult)          # walk outward to the LEFT, away from
        vals = []                         # the other eye
        for dy in (-6, -3, 0, 3, 6):
            vals.append(px[x, cy + dy])
        r = round(sum(v[0] for v in vals)/5)
        g = round(sum(v[1] for v in vals)/5)
        b = round(sum(v[2] for v in vals)/5)
        print(f"{mult:>11.2f}x  ({r:3d},{g:3d},{b:3d})")

REF='/private/tmp/claude-501/-Users-chirag-pawar-Desktop-Personal-TODO/3650b55e-1c4f-4d15-97fa-d7b0f4e7cbee/images/9.png'
# reference: left eye centre ~ (225, 290), half-width ~120
profile(REF, 225, 290, 120, "REFERENCE")
# ours: FaceRenderer 760x480 -> cy .44, gap .188, eye_hw .142
profile(sys.argv[1], int(760*0.5-760*0.188), int(480*0.44), int(760*0.142), "OURS")

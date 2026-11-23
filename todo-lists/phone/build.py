"""Build the phone app into docs/ - the folder GitHub Pages serves.

    ./run.sh phone          (or: .venv/bin/python todo-lists/phone/build.py)

The phone page never draws its own face. It takes the sentence reader and the
face from todo-character/prototypes/homebot-face.html - the approved build,
checked line-for-line against the Python - unchanged except for the panel width
and the canvas id. The app icon is rendered by the real Python renderer.

Output:
    docs/index.html            the app (one self-contained page)
    docs/manifest.webmanifest  so it can be added to the home screen
    docs/icon-192.png, icon-512.png, apple-touch-icon.png
    docs/.nojekyll             serve files as they are
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FACE = os.path.join(ROOT, "todo-character", "prototypes", "homebot-face.html")
DOCS = os.path.join(ROOT, "docs")


def face_and_reader() -> str:
    src = io.open(FACE, encoding="utf-8").read()
    scripts = re.findall(r"<script>\n(.*?)</script>", src, re.S)
    reader = next(s for s in scripts if "const READER=" in s)
    face = next(s for s in scripts if s.startswith("const PANEL_W="))
    face = face[: face.index("/* ---- input ---- */")]
    face = re.sub(r"const PANEL_W=\d+, PANEL_H=480;",
                  "const PANEL_W=800, PANEL_H=480;   // phone screen is 800 wide", face, count=1)
    assert face.count("document.getElementById('c')") == 1
    face = face.replace("document.getElementById('c')", "document.getElementById('face')")
    assert "let utt=" in face or "utt=null" in face
    return ("<script>\n" + reader + "</script>\n"
            "<script>\n/* The real face, from todo-character/prototypes/homebot-face.html. Never redraw it. */\n"
            "window.HBFace=(function(){\n" + face + """
return {update,render,setX,flash,speak,playSteps,touchDown,hush:()=>{utt=null;},
  names:()=>Object.keys(X), seqs:()=>Object.keys(SEQUENCES), seq:n=>SEQUENCES[n],
  mod:(k,v)=>{ if(k==='lean') leanA=v; if(k==='strain') strainA=v; if(k==='fatigue') fatigueA=v; }};
})();
</script>
""")


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0c0d10">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="homebot">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<style>
/* the small reset the artifact host used to provide */
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0}
img{max-width:100%}
[hidden]{display:none!important}
</style>
</head>
<body>
"""


def icons() -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((8, 8))
    from homebot.face.renderer import FaceRenderer
    from homebot.face import expressions
    from homebot.face.params import sanitise
    face = FaceRenderer((800, 480)).render(sanitise(expressions.get("happy")))
    square = pygame.Surface((800, 800))
    square.fill((8, 10, 14))
    square.blit(face, (0, 160))
    for size, name in ((512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png")):
        pygame.image.save(pygame.transform.smoothscale(square, (size, size)), os.path.join(DOCS, name))


def main() -> None:
    os.makedirs(DOCS, exist_ok=True)
    page = io.open(os.path.join(HERE, "phone_page.html"), encoding="utf-8").read()
    assert page.count("<!--FACE_AND_READER-->") == 1
    page = page.replace("<!--FACE_AND_READER-->", face_and_reader())
    io.open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(HEAD + page + "\n</body>\n</html>\n")
    manifest = {
        "name": "homebot", "short_name": "homebot", "start_url": "./", "scope": "./",
        "display": "standalone", "background_color": "#0c0d10", "theme_color": "#0c0d10",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }
    io.open(os.path.join(DOCS, "manifest.webmanifest"), "w").write(json.dumps(manifest, indent=2) + "\n")
    io.open(os.path.join(DOCS, ".nojekyll"), "w").close()
    icons()
    print("built", DOCS)


if __name__ == "__main__":
    main()

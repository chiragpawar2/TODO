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
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FACE = os.path.join(ROOT, "todo-character", "prototypes", "homebot-face.html")
DOCS = os.path.join(ROOT, "docs")
MODEL_SRC = os.path.join(ROOT, "todo-character", "models", "go-emotions", "onnx")
MODEL_OUT = os.path.join(DOCS, "models", "go-emotions")
PARTS = 2   # GitHub refuses single files over 100 MB; 2 parts are ~60 MB each


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
<meta name="apple-mobile-web-app-title" content="TODO">
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
    # The resting face - his neutral, everyday look - framed so the eyes and
    # mouth fill the icon instead of floating in a black square.
    face = FaceRenderer((800, 480)).render(sanitise(expressions.get("rest")))
    square = pygame.Surface((640, 640))
    square.fill((8, 10, 14))
    square.blit(face, (0, 80), pygame.Rect(80, 0, 640, 480))
    for size, name in ((512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png")):
        pygame.image.save(pygame.transform.smoothscale(square, (size, size)), os.path.join(DOCS, name))


def emotion_model() -> None:
    """Host the emotion model on the site itself, split into parts.

    Same model and files the Python app uses (todo-character/models). The
    phone downloads the parts from this site, joins them, checks the SHA-256,
    and keeps the result, so nothing is fetched from anywhere else.
    """
    src = os.path.join(MODEL_SRC, "model_quantized.onnx")
    if not os.path.isfile(src):
        print("emotion model not found at", src, "- phone build will run on rules only")
        return
    os.makedirs(MODEL_OUT, exist_ok=True)
    blob = open(src, "rb").read()
    step = -(-len(blob) // PARTS)
    parts = []
    for i in range(PARTS):
        chunk = blob[i * step:(i + 1) * step]
        name = f"model.part{i + 1}"
        open(os.path.join(MODEL_OUT, name), "wb").write(chunk)
        parts.append({"file": name, "size": len(chunk)})
    for f in ("tokenizer.json", "config.json"):
        shutil.copyfile(os.path.join(MODEL_SRC, f), os.path.join(MODEL_OUT, f))
    # The browser tokenizer also wants this small file. Its values are the
    # standard RoBERTa ones and match tokenizer.json's own special tokens
    # (<s>=0 <pad>=1 </s>=2 <unk>=3 <mask>=50264, max length 128).
    json.dump({"tokenizer_class": "RobertaTokenizer", "model_max_length": 128,
               "bos_token": "<s>", "eos_token": "</s>", "unk_token": "<unk>",
               "sep_token": "</s>", "cls_token": "<s>", "pad_token": "<pad>",
               "mask_token": "<mask>", "add_prefix_space": False, "trim_offsets": True},
              open(os.path.join(MODEL_OUT, "tokenizer_config.json"), "w"), indent=2)
    json.dump({"name": "go-emotions (int8)", "total": len(blob),
               "sha256": hashlib.sha256(blob).hexdigest(), "parts": parts,
               "threshold": 0.45},
              open(os.path.join(MODEL_OUT, "manifest.json"), "w"), indent=2)


def check(html: str) -> None:
    """Refuse to ship a page whose code does not parse.

    The model worker is stored as a string inside the page, so a quoting slip
    breaks the whole app while the build still "succeeds". Parse both the page
    scripts and the worker with node, when node is installed.
    """
    if not shutil.which("node"):
        print("node not found - skipped the syntax check")
        return
    js = "\n;\n".join(re.findall(r"<script>\n(.*?)</script>", html, re.S))
    m = re.search(r'const MODEL_WORKER=(".*?");\n', js, re.S)
    jobs = [("page", ".js", js)]
    if m:
        jobs.append(("model worker", ".mjs", json.loads(m.group(1))))
    for name, ext, code in jobs:
        with tempfile.NamedTemporaryFile("w", suffix=ext, delete=False, encoding="utf-8") as f:
            f.write(code)
        r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
        os.unlink(f.name)
        if r.returncode:
            raise SystemExit(f"{name} code does not parse:\n{r.stderr[-800:]}")
    print("checked: page and model worker parse")


def main() -> None:
    os.makedirs(DOCS, exist_ok=True)
    page = io.open(os.path.join(HERE, "phone_page.html"), encoding="utf-8").read()
    assert page.count("<!--FACE_AND_READER-->") == 1
    page = page.replace("<!--FACE_AND_READER-->", face_and_reader())
    html = HEAD + page + "\n</body>\n</html>\n"
    check(html)
    io.open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(html)
    manifest = {
        "name": "TODO", "short_name": "TODO", "start_url": "./", "scope": "./",
        "display": "standalone", "background_color": "#0c0d10", "theme_color": "#0c0d10",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }
    io.open(os.path.join(DOCS, "manifest.webmanifest"), "w").write(json.dumps(manifest, indent=2) + "\n")
    io.open(os.path.join(DOCS, ".nojekyll"), "w").close()
    icons()
    emotion_model()
    print("built", DOCS)


if __name__ == "__main__":
    main()

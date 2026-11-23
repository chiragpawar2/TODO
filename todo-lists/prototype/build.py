"""Build homebot-lists.html from lists_page.html + the character's web build.

The lists prototype never draws its own face. It takes the reader and the face
code from todo-character/prototypes/homebot-face.html (the approved character,
checked line-for-line against the Python), unchanged except for the panel width
and the canvas id, so both prototypes always show the same character.

    .venv/bin/python todo-lists/prototype/build.py
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FACE = os.path.join(ROOT, "todo-character", "prototypes", "homebot-face.html")

src = io.open(FACE, encoding="utf-8").read()
scripts = re.findall(r"<script>\n(.*?)</script>", src, re.S)
reader = next(s for s in scripts if "const READER=" in s)
face = next(s for s in scripts if s.startswith("const PANEL_W="))
face = face[: face.index("/* ---- input ---- */")]
face = re.sub(r"const PANEL_W=\d+, PANEL_H=480;", "const PANEL_W=800, PANEL_H=480;   // lists screen is 800 wide", face, count=1)
assert face.count("document.getElementById('c')") == 1
face = face.replace("document.getElementById('c')", "document.getElementById('face')")
face_block = ("<script>\n/* The real face, from todo-character/prototypes/homebot-face.html. Never redraw it. */\n"
              "window.HBFace=(function(){\n" + face + """
return {update,render,setX,flash,speak,playSteps,touchDown,
  names:()=>Object.keys(X), seqs:()=>Object.keys(SEQUENCES), seq:n=>SEQUENCES[n],
  mod:(k,v)=>{ if(k==='lean') leanA=v; if(k==='strain') strainA=v; if(k==='fatigue') fatigueA=v; }};
})();
</script>
""")
page = io.open(os.path.join(HERE, "lists_page.html"), encoding="utf-8").read()
assert page.count("<!--FACE_AND_READER-->") == 1
out = page.replace("<!--FACE_AND_READER-->", "<script>\n" + reader + "</script>\n" + face_block)
io.open(os.path.join(HERE, "homebot-lists.html"), "w", encoding="utf-8").write(out)
print("built", os.path.join(HERE, "homebot-lists.html"))

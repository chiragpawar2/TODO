"""homebot - a home AI assistant that runs on a laptop today and a Raspberry Pi later.

The package is split across two project folders:
    todo-character/homebot/face   the character (face, expressions, reader, lip sync)
    todo-lists/homebot            the assistant and its lists (brain, store, tools)
Both halves stay one package, so every existing import - homebot.face,
homebot.brain, the relative imports in face/mind.py - keeps working.
"""

import os as _os
from pkgutil import extend_path as _extend

__path__ = _extend(__path__, __name__)
_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
for _part in ("todo-character", "todo-lists"):
    _p = _os.path.join(_root, _part, "homebot")
    if _os.path.isdir(_p) and _p not in __path__:
        __path__.append(_p)

__version__ = "0.1.0"

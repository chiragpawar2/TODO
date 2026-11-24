"""An optional, on-device emotion model - the reader's second opinion.

reading.read() is rules first. Only when the rules find NO cue (the line
would otherwise fall to a neutral face) is this asked. It is optional: if
onnxruntime / tokenizers / the model files are missing, available() is False
and everything runs on rules alone.

Model: SamLowe/roberta-base-go_emotions-onnx, int8 quantised (~122 MB on
disk, 28 GoEmotions labels). English only: lines in Devanagari or with
romanised Hindi/Marathi function words are not sent to it, because it reads
those as noise ("mujhe bahut bura lag raha hai" -> amusement). The rules
already handle those scripts well.

Round 5: a multilingual second model was evaluated for romanised Hindi and
rejected. Xenova/distilbert-base-multilingual-cased-sentiments-student
(int8 ONNX, 136 MB, pos/neutral/neg) scored 13/32 on fresh Hinglish/Marathi
lines and fired on every neutral household command ("doodh le aana" ->
negative 0.78). Hindi and Marathi stay with the rules (lexicon.py).

Setup (see README):  pip install onnxruntime tokenizers huggingface_hub
then download the three files into todo-character/models/go-emotions/onnx/.

Loading happens once, in a background thread (start() is called at import
of the app; reading.read() never waits for it). Inference is ~65 ms on an
M-series laptop and runs on the caller's thread; the app calls it from a
worker thread, never the UI thread.
"""
from __future__ import annotations

import os
import re
import threading

_HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get(
    "HOMEBOT_EMOTION_MODEL",
    os.path.join(_HERE, "..", "..", "models", "go-emotions", "onnx"))

# Below this the model is guessing: stay neutral.
THRESHOLD = 0.45
# GoEmotions label -> our expression. None = treat as no feeling.
LABELS = {
    "admiration": "happy", "amusement": "grin", "anger": "angry",
    "annoyance": "stern", "approval": "content", "caring": "tender",
    "confusion": "confusion", "curiosity": None, "desire": "happy",
    "disappointment": "sad", "disapproval": "skeptical", "disgust": "angry",
    "embarrassment": "shy", "excitement": "delight", "fear": "worried",
    "gratitude": "tender", "grief": "sad", "joy": "happy", "love": "love",
    "nervousness": "worried", "optimism": "content", "pride": "proud",
    "realization": None, "relief": "content", "remorse": "apologetic",
    "sadness": "sad", "surprise": "surprised", "neutral": None,
}
NEGATIVE = {"angry", "stern", "sad", "skeptical", "worried", "apologetic", "shy"}

# Romanised Hindi / Marathi glue words. Their presence means the model would
# be reading a language it was never trained on.
_DESI = set("""hai hain hoon hu tha thi the ho raha rahi rahe mujhe mera meri mere
tum tumhe aap aaj kal kya kyu kyun nahi nahin nhi bahut bohot bahot accha acha
achha bura lag laga lagta yaar bhai bhaiya didi ji ka ki ke ko se mein me par
aur bhi toh to bas kar karo hua hui gaya gayi mala mazha majha khup aahe ahe
aala ala zala jhala nako kay kaay tula tumhi aamhi ekdum lai pan vatat hota
hoti kasa kashi""".split())
# Romanised Hindi/Marathi words that are ALSO common English words. Listing
# "the", "to", "me" here blocked the model on nearly every English sentence,
# so these are removed; they are only Hindi when the line has other desi words,
# which the remaining entries catch.
_DESI -= {"the", "to", "me", "ho", "par", "pan", "bas", "lag", "kar", "ke",
          "ko", "se", "ki", "ka", "hu", "ji", "bhi", "pan"}
_WORD = re.compile(r"[a-z']+")

_lock = threading.Lock()
_state = {"sess": None, "tok": None, "labels": None, "err": None, "started": False}


def _load() -> None:
    try:
        import json
        import numpy  # noqa: F401
        import onnxruntime as ort
        from tokenizers import Tokenizer
        tok = Tokenizer.from_file(os.path.join(MODEL_DIR, "tokenizer.json"))
        tok.enable_truncation(64)
        so = ort.SessionOptions()
        so.intra_op_num_threads = 2          # leave cores for the face
        sess = ort.InferenceSession(os.path.join(MODEL_DIR, "model_quantized.onnx"),
                                    so, providers=["CPUExecutionProvider"])
        with open(os.path.join(MODEL_DIR, "config.json")) as f:
            id2 = json.load(f)["id2label"]
        labels = [id2[str(i)] for i in range(len(id2))]
        with _lock:
            _state.update(sess=sess, tok=tok, labels=labels)
    except Exception as e:                    # optional: any failure = rules only
        _state["err"] = f"{type(e).__name__}: {e}"


def start(wait: bool = False) -> None:
    """Begin loading in a background thread (idempotent)."""
    with _lock:
        if _state["started"]:
            t = None
        else:
            _state["started"] = True
            t = threading.Thread(target=_load, name="emotion-model", daemon=True)
            t.start()
            _state["thread"] = t
    if wait:
        th = _state.get("thread")
        if th:
            th.join()


def available() -> bool:
    return _state["sess"] is not None


def suitable(text: str) -> bool:
    """English-ish text only."""
    if not text.isascii():
        return False
    words = _WORD.findall(text.lower())
    return bool(words) and not any(w in _DESI for w in words)


def classify(text: str):
    """(expression, confidence, label) or None. Never waits for loading."""
    if _state["sess"] is None or not suitable(text):
        return None
    import numpy as np
    enc = _state["tok"].encode(text)
    feed = {"input_ids": np.array([enc.ids], dtype=np.int64),
            "attention_mask": np.array([enc.attention_mask], dtype=np.int64)}
    logits = _state["sess"].run(None, feed)[0][0]
    p = 1.0 / (1.0 + np.exp(-logits))         # multi-label head: sigmoid
    i = int(p.argmax())
    label = _state["labels"][i]
    expr = LABELS.get(label)
    conf = float(p[i])
    if expr is None or conf < THRESHOLD:
        return None
    return expr, conf, label


def ask_async(text: str, done) -> None:
    """Classify on a worker thread and call done(result). For the UI."""
    if _state["sess"] is None or not suitable(text):
        return
    threading.Thread(target=lambda: done(classify(text)), daemon=True,
                     name="emotion-ask").start()

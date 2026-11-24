# Voice recognition checks

- `node tests/voice/voice_rules.mjs docs/index.html`: offline rules (voice names the speaker, a claimed name another voice contradicts is refused, old matches ignored).
- `fbank_reference.py` (numpy + onnxruntime) is the reference for the features; `fbank_js.mjs` dumps the worker's features for the same wav. They matched to 3e-6, and the browser gave the same similarity matrix as Python on the sherpa-onnx test voices (same speaker 0.72-0.82, different at most 0.47).
- Match rule on the phone: best score >= 0.55 and at least 0.08 above the next person.

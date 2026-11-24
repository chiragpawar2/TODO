// Voice recognition for TODO: turns a few seconds of speech into a voice print
// (192 numbers) with the CAM++ speaker model hosted on this site. Runs in a
// worker; nothing leaves the phone. Features match the reference in
// tests/voice/ (80 log-mel bins, 25 ms frames every 10 ms, mean removed).
import * as ort from "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.1/dist/ort.wasm.min.mjs";
const CACHE = "todo-voice-v1";
let sess = null;

/* FBANK-START */
const SR = 16000, FL = 400, FS = 160, NFFT = 512, NB = 80;
const WIN = new Float64Array(FL).map((_, i) => Math.pow(0.5 - 0.5 * Math.cos(2 * Math.PI * i / (FL - 1)), 0.85));
const mel = f => 1127 * Math.log(1 + f / 700);
const MELW = (() => {
  const lo = mel(20), hi = mel(SR / 2), nbin = NFFT / 2 + 1, W = [];
  for (let m = 0; m < NB; m++) {
    const l = lo + (hi - lo) * m / (NB + 1), c = lo + (hi - lo) * (m + 1) / (NB + 1), r = lo + (hi - lo) * (m + 2) / (NB + 1);
    const row = new Float64Array(nbin);
    for (let k = 0; k < nbin; k++) { const fm = mel(k * SR / NFFT); if (fm > l && fm < r) row[k] = Math.max(0, Math.min((fm - l) / (c - l), (r - fm) / (r - c))); }
    W.push(row);
  }
  return W;
})();
function fft(re, im) {   // in place, radix-2, length NFFT
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) { let b = n >> 1; for (; j & b; b >>= 1) j ^= b; j ^= b; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; } }
  for (let len = 2; len <= n; len <<= 1) {
    const a = -2 * Math.PI / len, wr = Math.cos(a), wi = Math.sin(a);
    for (let i = 0; i < n; i += len) { let cr = 1, ci = 0;
      for (let k = 0; k < len / 2; k++) {
        const ur = re[i + k], ui = im[i + k], j = i + k + len / 2;
        const vr = re[j] * cr - im[j] * ci, vi = re[j] * ci + im[j] * cr;
        re[i + k] = ur + vr; im[i + k] = ui + vi; re[j] = ur - vr; im[j] = ui - vi;
        const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t; } }
  }
}
function fbank(x) {   // x: Float32Array of 16 kHz samples in -1..1
  const n = x.length < FL ? 0 : 1 + Math.floor((x.length - FL) / FS), out = new Float32Array(n * NB);
  const re = new Float64Array(NFFT), im = new Float64Array(NFFT), f = new Float64Array(FL);
  for (let i = 0; i < n; i++) {
    let mean = 0; for (let k = 0; k < FL; k++) { f[k] = x[i * FS + k]; mean += f[k]; } mean /= FL;
    for (let k = 0; k < FL; k++) f[k] -= mean;
    re.fill(0); im.fill(0);
    re[0] = (f[0] - 0.97 * f[0]) * WIN[0];
    for (let k = 1; k < FL; k++) re[k] = (f[k] - 0.97 * f[k - 1]) * WIN[k];
    fft(re, im);
    for (let m = 0; m < NB; m++) { const w = MELW[m]; let s = 0;
      for (let k = 0; k <= NFFT / 2; k++) if (w[k]) s += w[k] * (re[k] * re[k] + im[k] * im[k]);
      out[i * NB + m] = Math.log(Math.max(s, 1.1920929e-07)); }
  }
  for (let m = 0; m < NB; m++) { let s = 0; for (let i = 0; i < n; i++) s += out[i * NB + m]; s /= n || 1; for (let i = 0; i < n; i++) out[i * NB + m] -= s; }
  return { feats: out, frames: n };
}
/* FBANK-END */

async function download(url, size, onBytes) {
  const c = await caches.open(CACHE), hit = await c.match(url);
  if (hit) { const b = new Uint8Array(await hit.arrayBuffer()); onBytes(b.length); return b; }
  const res = await fetch(url); if (!res.ok) throw new Error("download failed (" + res.status + ")");
  const rd = res.body.getReader(), buf = new Uint8Array(size); let off = 0;
  for (;;) { const { done, value } = await rd.read(); if (done) break; buf.set(value, off); off += value.length; onBytes(off); }
  if (off !== size) throw new Error("the download was cut short");
  await c.put(url, new Response(buf)); return buf;
}
self.onmessage = async e => {
  const m = e.data;
  if (m.type === "load") {
    try {
      const man = await (await fetch(m.base + "manifest.json", { cache: "no-cache" })).json();
      const all = await download(m.base + man.file, man.size, n => self.postMessage({ type: "progress", loaded: n, total: man.size }));
      self.postMessage({ type: "stage", text: "Checking…" });
      const h = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", all))).map(x => x.toString(16).padStart(2, "0")).join("");
      if (h !== man.sha256) { await caches.delete(CACHE); throw new Error("the download was damaged. Tap Download to try again"); }
      self.postMessage({ type: "stage", text: "Starting…" });
      ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.1/dist/"; ort.env.wasm.numThreads = 1;
      sess = await ort.InferenceSession.create(all.buffer, { executionProviders: ["wasm"] });
      self.postMessage({ type: "ready" });
    } catch (err) { self.postMessage({ type: "error", text: String(err && err.message || err) }); }
  }
  if (m.type === "embed") {   // m.pcm: Float32Array, 16 kHz
    try {
      if (!sess) throw new Error("not loaded");
      const { feats, frames } = fbank(m.pcm);
      if (frames < 100) throw new Error("too short");
      const out = await sess.run({ x: new ort.Tensor("float32", feats, [1, frames, NB]) });
      const v = Array.from(out[sess.outputNames[0]].data), nrm = Math.hypot(...v) || 1;
      self.postMessage({ type: "embedding", id: m.id, emb: v.map(x => x / nrm) });
    } catch (err) { self.postMessage({ type: "embedding", id: m.id, emb: null, error: String(err && err.message || err) }); }
  }
  if (m.type === "forget") { try { await caches.delete(CACHE); } catch (e) {} self.postMessage({ type: "forgotten" }); }
};

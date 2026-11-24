// Runs tests/messages/scenarios.mjs against the page's own streamBrain() with real Gemini.
// usage: node run_scenarios.mjs <GEMINI_KEY> <docs/index.html> <out.json> [idFilterRegex]
import fs from "node:fs";
import { SCENARIOS, GLOBAL_NOT } from "./scenarios.mjs";
const [key, page, out, filt] = process.argv.slice(2);
const html = fs.readFileSync(page, "utf8"); const PAGE_MTIME = fs.statSync(page).mtime.toString();
let code = html.slice(html.indexOf("/* ---------- list tools"), html.indexOf("async function think("));
const CALL = "response:runTool(c.functionCall.name,c.functionCall.args)";
if (!code.includes(CALL)) throw new Error("tool call site changed");
code = code.replace(CALL, "response:__T(c.functionCall.name,c.functionCall.args)") +
  ";function __T(n,a){const r=runTool(n,a);__log.push({tool:n,args:a,result:r});return r;}";
const sleep = ms => new Promise(r => setTimeout(r, ms));
const BUSY = /very busy|couldn't find a working AI/;
function boot() {
  const store = {}, log = [];
  const localStorage = { getItem: k => store[k] ?? null, setItem: (k, v) => { store[k] = v; }, removeItem: k => { delete store[k]; } };
  const el = () => ({ addEventListener() {}, innerHTML: "", textContent: "", hidden: false, value: "", onsubmit: null });
  const document = { getElementById: () => el() };
  const data = { lists: [{ id: 1, title: "Groceries", items: [] }], nextId: 100 };
  const env = { localStorage, data, left: l => l.items.filter(i => !i.done), nid: () => ++data.nextId, save() {}, go() {}, render() {}, ui: { view: "home" },
    F: { flash() {} }, getKey: () => key, navigator: { onLine: true }, document, $: () => el(), esc: s => s, setInterval: () => 0,
    shush() {}, speakReply() {}, stopPlayback() {}, indexedDB: {}, MediaRecorder: undefined, Audio: undefined, __log: log };
  const B = new Function(...Object.keys(env), "fetch", "TextDecoder", "AbortController",
    code + "; return {streamBrain, get msgs(){return msgs}, people, runTool, fadeMessages};")(...Object.values(env), fetch, TextDecoder, AbortController);
  B.data = data; B.log = log; return B;
}
const deva = s => { const d = (s.match(/[ऀ-ॿ]/g) || []).length, l = (s.match(/[A-Za-z]/g) || []).length; return d + l ? d / (d + l) : 0; };
function check(c, st) {
  const M = st.msgs, R = st.reply, T = st.tools;
  const match = (m, o) => (!o.to || o.to.test(m.to)) && (!o.from || o.from.test(m.from)) &&
    (!o.text || o.text.every(r => r.test(m.text))) && (o.delivered === undefined || !!m.delivered_at === o.delivered);
  switch (c.k) {
    case "has": return M.some(m => match(m, c.o)) || `no message matching ${fmt(c.o)}`;
    case "none": return !M.some(m => match(m, c.o)) || `unexpected message matching ${fmt(c.o)}`;
    case "count": return M.length === c.n || `expected ${c.n} messages, have ${M.length}`;
    case "pending": return M.filter(m => !m.delivered_at).length === c.n || `expected ${c.n} undelivered, have ${M.filter(m => !m.delivered_at).length}`;
    case "reply": return c.r.every(r => r.test(R)) || `reply missing ${c.r.filter(r => !r.test(R)).join(" , ")}`;
    case "any": return c.r.some(r => r.test(R)) || `reply has none of ${c.r.join(" , ")}`;
    case "not": return !c.r.some(r => r.test(R)) || `reply contains forbidden ${c.r.filter(r => r.test(R)).join(" , ")}`;
    case "lang": { const f = deva(R); return (c.l === "deva" ? f > 0.6 : f < 0.15) || `reply language ${c.l} expected, devanagari share ${f.toFixed(2)}`; }
    case "tool": return T.some(t => t.tool === c.t) || `tool ${c.t} not called`;
    case "notool": return !T.some(t => t.tool === c.t) || `tool ${c.t} was called`;
  }
}
const fmt = o => JSON.stringify(o, (k, v) => v instanceof RegExp ? String(v) : v);
const results = [];
const list = SCENARIOS.filter(s => !filt || new RegExp(filt).test(s.id));
for (const s of list) {
  const B = boot(); B.people.push(...s.people.map((p, i) => ({ id: i + 1, voice: false, ...p })));
  const rec = { page_mtime: PAGE_MTIME, started: new Date().toString(), id: s.id, cat: s.cat, title: s.title, cause: s.cause, turns: [], pass: true, busy: false };
  for (const t of s.turns) {
    if (t.jump) { const ms = t.jump * 3600e3; for (const m of B.msgs.list) { m.created -= ms; m.expires -= ms; if (m.delivered_at) m.delivered_at -= ms; } B.fadeMessages(true);
      rec.turns.push({ jump: t.jump, after: B.msgs.list.map(m => ({ ...m })) }); continue; }
    let res, tries = 0, t0;
    for (;;) { B.log.length = 0; t0 = Date.now(); try { res = await B.streamBrain(t.say, () => {}); } catch (e) { res = { err: "EXC " + e.message }; }
      const txt = (res && (res.text || res.err)) || "";
      if (BUSY.test(txt) && tries < 2) { tries++; await sleep(15000); continue; } break; }
    const reply = ((res && (res.text || res.err)) || "").replace(/\s+/g, " ").trim();
    const st = { reply, msgs: B.msgs.list, tools: [...B.log] };
    const busy = BUSY.test(reply);
    const fails = busy ? [] : [...(t.expect || []), { k: "not", r: GLOBAL_NOT }].map(c => check(c, st)).filter(x => x !== true);
    rec.turns.push({ say: t.say, reply, secs: (Date.now() - t0) / 1000, busy, tools: st.tools.map(x => ({ tool: x.tool, args: x.args, ok: x.result && x.result.ok })),
      state: B.msgs.list.map(m => ({ id: m.id, from: m.from, to: m.to, text: m.text, delivered: !!m.delivered_at, hours_left: +((m.expires - Date.now()) / 3600e3).toFixed(2) })), fails });
    if (busy) rec.busy = true; if (fails.length) rec.pass = false;
    console.log(`[${s.id}] ${busy ? "BUSY" : fails.length ? "FAIL" : "ok"}  > ${t.say.slice(0, 60)}\n   < ${reply.slice(0, 160)}${fails.length ? "\n   ! " + fails.join(" | ") : ""}`);
    await sleep(4000 + Math.random() * 2000);
  }
  if (rec.busy) rec.pass = rec.turns.some(x => x.fails && x.fails.length) ? false : null; // null = busy, inconclusive
  results.push(rec); fs.writeFileSync(out, JSON.stringify(results, null, 1));
}
const p = results.filter(r => r.pass === true).length, b = results.filter(r => r.pass === null).length;
console.log(`DONE ${p}/${results.length} pass, ${b} busy-inconclusive`);

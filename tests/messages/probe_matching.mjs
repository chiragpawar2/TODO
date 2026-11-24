// Offline (no Gemini) probe of the page's recipient matching: leave_message(to=X) then get_messages(for=Y).
// usage: node probe_matching.mjs ../../docs/index.html
import fs from "node:fs";
const html = fs.readFileSync(process.argv[2], "utf8");
const code = html.slice(html.indexOf("/* ---------- list tools"), html.indexOf("async function think("));
const el = () => ({ addEventListener() {}, innerHTML: "", textContent: "", hidden: false, value: "" });
const store = {};
const env = { localStorage: { getItem: k => store[k] ?? null, setItem: (k, v) => { store[k] = v; } }, data: { lists: [], nextId: 1 }, left: l => l.items, nid: () => 1, save() {}, go() {}, render() {}, ui: { view: "x" },
  F: { flash() {} }, getKey: () => "", navigator: {}, document: { getElementById: () => el() }, $: () => el(), esc: s => s, setInterval: () => 0, shush() {}, speakReply() {}, stopPlayback() {}, indexedDB: {} };
const B = new Function(...Object.keys(env), code + "; return {people, runTool, get msgs(){return msgs}};")(...Object.values(env));
B.people.push(...[["Anjali","mother"],["Rahul","father"],["Sunita","cook"],["Kamla","maid"],["Shobha","grandmother"],["Raju","driver"],["Aarav","son"],["Isha","daughter"]].map(([name,role],i)=>({id:i+1,name,role,langs:["Hindi"]})));
const pairs = [["Aaji","Shobha"],["आजी","Shobha"],["आजी","शोभा"],["Papa","Rahul"],["Mumma","Anjali"],["ताई","Anjali"],["अंजली मैडम","अंजली"],["अंजली","Anjali"],["सुनीता","Sunita"],["Sunita","सुनीता"],
  ["राजूला","Raju"],["आरव","Aarav"],["बाई","कमला"],["बाई","Kamla"],["maid","Kamla"],["Aarav and Isha","Isha"],["the cook","खाना बनाने वाली"],["Raju","राजू"],["कमलाला","Kamla"],["Mom","अंजली"]];
// FIXER NOTE: leave_message may now refuse (ambiguous_recipient) and save nothing; report that as ASK instead of crashing.
for (const [to, who] of pairs) { B.msgs.list.length = 0; const lm = B.runTool("leave_message", { from: "x", to, message: "m" });
  if (!lm.ok) { console.log(`ASK   to="${to}" (${lm.error}${lm.candidates ? ": " + lm.candidates.map(c => c.name).join("/") : ""})  asked by "${who}"`); continue; }
  B.runTool("set_speaker", { name: who }); // FIXER NOTE (round 2): get_messages now only answers the set speaker
  const r = B.runTool("get_messages", { for: who }); console.log((r.messages.length ? "MATCH " : "MISS  ") + `to="${to}" stored="${B.msgs.list[0].to}"  asked by "${who}"`); }

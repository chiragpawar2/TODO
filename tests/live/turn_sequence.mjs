import fs from "node:fs";
const html=fs.readFileSync(process.argv[2],"utf8");
const code=html.slice(html.indexOf("function stopPlayback()"),html.indexOf("/* ---------- listening"));
const log=[]; const turn={snap:null};
const el=()=>({textContent:"",classList:{add(){},remove(){}},setAttribute(){}});
const env={turn,turnBegin(){turn.snap="x";log.push("begin")},turnCommit(){turn.snap=null;log.push("COMMIT")},turnRollback(){turn.snap=null;log.push("ROLLBACK")},
 speaker:{},speakerReset(){},vSettle:async()=>{},voiceToSpeaker(){},vTurnEnd(){},runTool:()=>({ok:true}),$:el,F:{hush(){},speak(){},playSteps(){},flash(){}},R:{readBeats:()=>[]},
 feel(){},audioCtx:()=>({currentTime:0,createBuffer:(c,n)=>({duration:n/24000,getChannelData:()=>new Float32Array(n)}),createBufferSource:()=>({connect(){},start(){},stop(){}}),destination:{}}),
 atob:s=>Buffer.from(s,"base64").toString("binary"),live:{on:true,ws:{readyState:1,send(){}},sources:[],playAt:0,userText:"",botText:""}};
const f=new Function(...Object.keys(env),code+";return onLive;");
const onLive=f(...Object.values(env));
const audio={serverContent:{modelTurn:{parts:[{inlineData:{mimeType:"audio/pcm;rate=24000",data:"AAAA"}}]}}};
const tc={toolCall:{functionCalls:[{id:"1",name:"add_items",args:{}}]}};
const run=async seq=>{ log.length=0; env.live.gotAudio=false; for(const m of seq){ onLive(m); await new Promise(r=>setTimeout(r,5)); } return log.join(" "); };
console.log("3.8 style:",await run([tc,{serverContent:{turnComplete:true}},audio,audio,{serverContent:{turnComplete:true}}]));
console.log("3.1 style:",await run([tc,audio,audio,{serverContent:{turnComplete:true}}]));
console.log("no tool  :",await run([audio,{serverContent:{turnComplete:true}}]));
process.exit(0);

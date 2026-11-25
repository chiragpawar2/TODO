const key=process.argv[2];
for(const m of process.argv.slice(3)){
  const out=await new Promise(res=>{ const ws=new WebSocket("wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key="+key);
    const st={setup:false,tool:null,audio:0,text:"",t0:0,first:0}; const t=setTimeout(()=>{res(st);try{ws.close()}catch(e){}},25000);
    ws.onopen=()=>ws.send(JSON.stringify({setup:{model:"models/"+m,generationConfig:{responseModalities:["AUDIO"],speechConfig:{voiceConfig:{prebuiltVoiceConfig:{voiceName:"Puck"}}}},
      systemInstruction:{parts:[{text:"You are TODO, a home helper. Answer in the user's language, briefly. Use tools for lists."}]},
      realtimeInputConfig:{automaticActivityDetection:{silenceDurationMs:1200}},
      tools:[{functionDeclarations:[{name:"add_items",description:"Add items to a list",parameters:{type:"OBJECT",properties:{list:{type:"STRING"},items:{type:"ARRAY",items:{type:"STRING"}}},required:["list","items"]}}]}],
      inputAudioTranscription:{},outputAudioTranscription:{}}}));
    ws.onmessage=async e=>{ const d=JSON.parse(typeof e.data==="string"?e.data:await e.data.text());
      if(d.setupComplete){ st.setup=true; st.t0=Date.now(); ws.send(JSON.stringify({clientContent:{turns:[{role:"user",parts:[{text:"किराणा यादीत दूध टाक"}]}],turnComplete:true}})); }
      if(d.toolCall){ st.tool=JSON.stringify(d.toolCall.functionCalls.map(c=>[c.name,c.args])); ws.send(JSON.stringify({toolResponse:{functionResponses:d.toolCall.functionCalls.map(c=>({id:c.id,name:c.name,response:{ok:true}}))}})); }
      const kk=Object.keys(d).concat(d.serverContent?Object.keys(d.serverContent).map(x=>"sc."+x):[]).filter(x=>x!=="serverContent").join("+"); if(st.seq===undefined) st.seq=[]; if(st.seq[st.seq.length-1]!==kk) st.seq.push(kk); const sc=d.serverContent; if(sc){ for(const p of (sc.modelTurn&&sc.modelTurn.parts)||[]) if(p.inlineData){ if(!st.first) st.first=Date.now()-st.t0; st.audio+=1; }
        if(sc.outputTranscription) st.text+=sc.outputTranscription.text; if(sc.turnComplete&&st.tool&&st.audio){ clearTimeout(t); res(st); ws.close(); } } };
    ws.onclose=e=>{ clearTimeout(t); st.close=e.code+" "+String(e.reason).slice(0,100); res(st); }; });
  console.log(m, JSON.stringify(out));
}

const fs=require("fs"),vm=require("vm");
const h=fs.readFileSync("../homebot-face.html","utf8");
const scripts=[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const ctxProxy=new Proxy({},{get:(t,k)=>k==="createRadialGradient"||k==="createLinearGradient"?()=>({addColorStop(){}}):(typeof k==="string"?(t[k]??(()=>{})):undefined),set:(t,k,v)=>(t[k]=v,true)});
const el=()=>({addEventListener(){},setAttribute(){},style:{},appendChild(){},getContext:()=>ctxProxy,setPointerCapture(){},getBoundingClientRect:()=>({left:0,top:0,width:768,height:480}),value:"",width:768,height:480});
const els={};
let frames=0;
const sb={document:{getElementById:id=>els[id]||(els[id]=el()),createElement:el},performance,
  requestAnimationFrame:f=>{if(frames++<30) setTimeout(f,5);},setTimeout,Math,console,JSON,Object,Array,Set,Map,String,Number,RegExp,parseFloat,isNaN,Proxy};
vm.createContext(sb);
const code=scripts.join("\n;\n")+`
;globalThis.T={setX,play,playSteps,update,speak,READER,submit:()=>submit(),get base(){return base},get seq(){return seq},el:document.getElementById('say'),st:document.getElementById('status')};`;
vm.runInContext(code,sb);
const T=sb.T;
const send=v=>{T.el.value=v; T.submit(); return T.st.innerHTML;};
send("/attentive"); for(let i=0;i<3;i++)T.update(); console.log("attentive mouth before speech", T.update().mouth_alpha);
console.log(send("/bored happy 0.3"), T.base);
console.log(send("/angry *0.4"));
console.log(send("+fatigue 0.7"));
console.log(send("mala nahi aavadla"), T.base);
console.log(send("I got the job! But it's in Bangalore and I'll miss everyone."), T.seq.length);
console.log(send(">Okay."));
setTimeout(()=>{const p=T.update(); console.log("frame ok, mouth_alpha",p.mouth_alpha.toFixed(2),"frames",frames);},200);

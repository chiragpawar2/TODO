/* ---- pronunciation: JS port of pronounce.normalise (numbers, dates, money,
   times, units, phones, fractions, ranges, decades, Roman numerals). ---- */
const PRON=(function(){
const ONES=["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve",
 "thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"];
const TENS=["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"];
const ORDN={one:"first",two:"second",three:"third",five:"fifth",eight:"eighth",nine:"ninth",twelve:"twelfth"};
const u100=n=>n<20?[ONES[n]]:[TENS[Math.floor(n/10)]].concat(n%10?[ONES[n%10]]:[]);
const u1000=n=>{const h=Math.floor(n/100),r=n%100,o=[];if(h)o.push(ONES[h],"hundred");if(r)o.push(...u100(r));return o;};
function numberWords(n){
  if(n<0) return ["minus",...numberWords(-n)];
  if(n===0) return ["zero"];
  const o=[];
  for(const [v,name] of [[1e9,"billion"],[1e6,"million"],[1e3,"thousand"]])
    if(n>=v){o.push(...u1000(Math.floor(n/v)),name); n%=v;}
  if(n) o.push(...u1000(n));
  return o;
}
function ordinalWords(n){const w=numberWords(n),l=w[w.length-1];
  w[w.length-1]=ORDN[l]||(l.endsWith("y")?l.slice(0,-1)+"tieth":l+"th"); return w;}
const SYMBOL={"%":["percent"],"&":["and"],"@":["at"],"+":["plus"],"=":["equals"],"<":["less","than"],
 ">":["greater","than"],"°":["degrees"],"#":["number"],"~":["about"],"/":["slash"],"₹":["rupees"],
 "$":["dollars"],"€":["euros"],"£":["pounds"]};
const ABBREV={rs:["rupees"],dr:["doctor"],mr:["mister"],mrs:["missus"],ms:["miss"],st:["street"],
 vs:["versus"],etc:["etcetera"],ok:["okay"],tv:["tee","vee"],prof:["professor"],smt:["shrimati"],
 lt:["lieutenant"],col:["colonel"],capt:["captain"]};
const TIME=/^(\d{1,2}):(\d{2})$/, CLOCK=/^(\d{1,2})(?::(\d{2}))?(am|pm|a\.m\.?|p\.m\.?)$/i,
 DEC=/^(\d[\d,]*)\.(\d+)$/, ORD=/^(\d+)(st|nd|rd|th)$/i, INT=/^\d[\d,]*$/, INDIAN=/^\d{1,2}(,\d{2})+,\d{3}$/,
 FRAC=/^(\d+)\/(\d+)$/, PHONE=/^\+?\d[\d-]{7,}\d$/, RANGE=/^(\d[\d,.:]*%?)-(\d[\d,.:]*%?)$/,
 UNIT_JOINED=/^(\d[\d,.]*)([a-z]+)$/i, RUPEE=/^(rs\.?|inr)(\d.*)$/i, NUM_SYM=/^(\d[\d,]*(?:\.\d+)?)([%°])$/,
 DATE3=/^(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{2}|\d{4})$/, DATE2=/^(\d{1,2})\/(\d{1,2})$/,
 DECADE=/^'?(\d{2}|\d{4})s$/;
const MONTHS=["january","february","march","april","may","june","july","august","september","october","november","december"];
const MONEY_CTX=/[₹$]|\b(rs\.?|inr|rupees?|loan|lakhs?|salary|price|cost|emi|budget|fees?|paid|pay|income|ctc|package|amount|deposit|balance|worth|crore)\b/i;
const SPACED_PHONE=/(?<![\w.,])(\+?\d{2,5})((?: \d{3,5}){1,3})(?!\w|[.,]\d)/g;
const PLURAL={teaspoons:"teaspoon",tablespoons:"tablespoon",kilos:"kilo",kilometres:"kilometre",
 centimetres:"centimetre",millimetres:"millimetre",milligrams:"milligram",millilitres:"millilitre",
 hours:"hour",minutes:"minute",seconds:"second",litres:"litre",grams:"gram",rupees:"rupee",dollars:"dollar",
 euros:"euro",pounds:"pound",degrees:"degree",feet:"foot",inches:"inch",stars:"star",cents:"cent",paise:"paisa"};
const UFRAC={"½":"1/2","¼":"1/4","¾":"3/4","⅓":"1/3","⅔":"2/3","⅛":"1/8","⅜":"3/8","⅝":"5/8","⅞":"7/8"};
const UNITS={mg:["milligrams"],ml:["millilitres"],kg:["kilos"],kgs:["kilos"],km:["kilometres"],cm:["centimetres"],
 mm:["millimetres"],gb:["gee","bee"],mb:["em","bee"],tb:["tee","bee"],mbps:["em","bee","pee","ess"],
 kmph:["kilometres","per","hour"],tsp:["teaspoons"],tbsp:["tablespoons"],hrs:["hours"],hr:["hour"],
 mins:["minutes"],min:["minutes"],secs:["seconds"],sec:["seconds"],l:["litres"],ltr:["litres"],g:["grams"],
 gm:["grams"],gms:["grams"],k:["thousand"],kwh:["kilowatt","hours"],lakh:["lakh"],lakhs:["lakh"],ft:["feet"],
 cr:["crore"],crore:["crore"]};
const ALWAYS=new Set(["mg","ml","gb","mbps","kmph","tsp","tbsp","kg","km"]);
const DIAL=new Set(["call","calling","dial","dialling","dialing","helpline","number","no","no.","ring","line",
 "pin","otp","code","ext","extension","toll-free","sms"]);
const FRAC_NAME={2:["half","halves"],3:["third","thirds"],4:["quarter","quarters"],5:["fifth","fifths"],
 6:["sixth","sixths"],8:["eighth","eighths"],10:["tenth","tenths"],12:["twelfth","twelfths"],16:["sixteenth","sixteenths"]};
const CUR_SUB={"₹":"paise","$":"cents","€":"cents","£":"pence"};
const LETTER_NAME={a:"ay",b:"bee",c:"see",d:"dee",e:"ee",f:"ef",g:"jee",h:"aitch",i:"eye",j:"jay",k:"kay",
 l:"el",m:"em",n:"en",o:"oh",p:"pee",q:"cue",r:"ar",s:"ess",t:"tee",u:"you",v:"vee",w:"double you",x:"ex",y:"why",z:"zed"};
const ROMAN={II:2,III:3,IV:4,V:5,VI:6,VII:7,VIII:8,IX:9,X:10,XI:11,XII:12,XIII:13,XIV:14,XV:15,XVI:16,XVIII:18,XX:20};
const ROMAN_COUNT=new Set(["class","chapter","part","standard","std","book","volume","vol","phase","grade","act",
 "scene","section","level","stage","war","world","unit","round","season","episode","type","sector","block","wing","gate","page","form"]);
const PER="month|mo|day|week|wk|year|yr|annum|hour|hr|h|night|person|head|piece|pc|kg|kilo|km|litre|liter|l|unit|plate|min|minute|sec|second|sq ?ft|month's";
const PRE=[[/(\d)\/-/g,"$1"],[/(?<![\w.,%)])[-−–](?=\d)/g,"minus "],[/(\d)\s*°\s*C\b/g,"$1 degrees celsius"],
 [/(\d)\s*°\s*F\b/g,"$1 degrees fahrenheit"],[/km\/hr?\b/gi,"kmph"],[new RegExp("(\\d)\\s*/\\s*("+PER+")\\b","gi"),"$1 per $2"],
 [/\b24\s*[x×\/]\s*7\b/g,"twenty four seven"],[/\b(\d+)\s*[x×]\s*(\d+)\b/g,"$1 by $2"],[/\b(\d+(?:\.\d+)?)[x×](?![\w])/g,"$1 times"],
 [/(?<![\w])[x×](\d+)\b/g,"times $1"],[/(\d+)\s*'\s*(\d+)\s*(?:"|''|in\b|inches\b)?/g,"$1 feet $2 inches"],
 [/(\d+)\s*(?:ft|feet)\s+(\d+)\s*(?:in|inch|inches)\b/g,"$1 feet $2 inches"],[/(\d+(?:\.\d+)?)\s*[★⭐]/gu,"$1 stars"],
 [/(\d(?:st|nd|rd|th))\s*\/\s*(?=\d)/gi,"$1 or "],[/\b(\d+)\/(\d+)(?:st|nd|rd|th)\b/gi,"$1/$2"],
 [/\b(Dr|Mr|Mrs|Ms|Prof|Sr|Jr|Smt|Shri|Lt|Col|Capt)\.(?=\s+[A-Z])/g,"$1"],[/\b(No|no|Nos|nos)\.\s*(?=\d)/g,"number "],
 [/\b(Q|H)([1-4])\b/g,(m,a,b)=>LETTER_NAME[a.toLowerCase()]+" "+b],[/\bFY\s?'?(\d{2,4})\b/g,"ef why $1"]];
const ROMAN_RE=new RegExp("\\b([A-Z][a-z]+)\\s+("+Object.keys(ROMAN).sort((a,b)=>b.length-a.length).join("|")+")\\b(?!['\\w])","g");
let money=false;
const digits=s=>[...s].filter(c=>/\d/.test(c)).map(c=>ONES[+c]);
function indian(n){const o=[];const crore=Math.floor(n/1e7);n%=1e7;const lakh=Math.floor(n/1e5);n%=1e5;
  if(crore) o.push(...(crore>=1e5?indian(crore):numberWords(crore)),"crore");
  if(lakh) o.push(...u100(lakh),"lakh"); if(n) o.push(...numberWords(n)); return o.length?o:["zero"];}
const intWords=t=>{const n=+t.replace(/,/g,""); return INDIAN.test(t)?indian(n):numberWords(n);};
function clock(h,mi){const o=numberWords(h); if(mi==null) return o; if(mi===0) return o.concat(["oh","clock"]);
  if(mi<10) return o.concat(["oh"],numberWords(mi)); return o.concat(numberWords(mi));}
function one(num,unit){const s=num.replace(/^[.,]+|[.,]+$/g,"");
  if(s==="1"&&unit.length&&PLURAL[unit[unit.length-1]]) return unit.slice(0,-1).concat([PLURAL[unit[unit.length-1]]]); return unit;}
function say(tok,prev,prevNum){
  const low=tok.toLowerCase(); let m;
  if((m=CLOCK.exec(tok))){const mi=m[2]?+m[2]:null;
    const c=low[m[1].length+(m[2]?m[2].length+1:0)];
    return [clock(+m[1],mi).concat(c==="a"?["ay","em"]:["pee","em"]),true];}
  if((m=TIME.exec(tok))){let h=+m[1],mi=+m[2];
    if((h>=13&&h<=23)||(h===0&&m[1].length===2)){const h12=h?h-12:12; return [clock(h12,mi||null).concat(h?["pee","em"]:["ay","em"]),true];}
    return [clock(h,mi),true];}
  if((m=DATE3.exec(tok))){const d=+m[1],mo=+m[2],y=m[3];
    if(d>=1&&d<=31&&mo>=1&&mo<=12){const yr=say(y.length===2?"20"+y:y,"",false);
      return [ordinalWords(d).concat([MONTHS[mo-1]],yr?yr[0]:[]),true];}}
  if((m=DATE2.exec(tok))){const d=+m[1],mo=+m[2];
    if(d>=1&&d<=31&&mo>=1&&mo<=12&&(d>=mo||m[2].startsWith("0")||m[1].startsWith("0"))&&d>1) return [ordinalWords(d).concat([MONTHS[mo-1]]),true];}
  if((m=NUM_SYM.exec(tok))){const n=say(m[1],prev,false); if(n) return [n[0].concat(SYMBOL[m[2]]),true];}
  if((m=ORD.exec(tok))) return [ordinalWords(+m[1]),true];
  if("₹$€£".includes(tok[0]||"x")&&(m=DEC.exec(tok.slice(1)))&&m[2].length===2){
    const whole=intWords(m[1]),part=+m[2];
    return [whole.concat(SYMBOL[tok[0]],part?numberWords(part).concat([CUR_SUB[tok[0]]]):[]),true];}
  if((m=DECADE.exec(tok))){const yr=m[1].length===4?say(m[1],"",false)[0]:numberWords(+m[1]);
    const l=yr[yr.length-1]; yr[yr.length-1]=l.endsWith("y")?l.slice(0,-1)+"ies":l+"s"; return [yr,true];}
  if("₹$€£".includes(tok[0]||"x")&&tok.length>1){const r=say(tok.slice(1),"rs",false); if(r) return [SYMBOL[tok[0]].concat(r[0]),true];}
  if((m=RUPEE.exec(tok))){const r=say(m[2],"rs",false); if(r) return [["rupees"].concat(r[0]),true];}
  if((m=FRAC.exec(tok))){const n=+m[1],d=+m[2];
    if(FRAC_NAME[d]&&n>0&&n<d){const [o,many]=FRAC_NAME[d],head=prevNum?["and"]:[];
      if(n===1) return [head.concat(prevNum||d===2?["a"]:["one"],[o]),true];
      return [head.concat(numberWords(n),[many]),true];}
    return [numberWords(n).concat(["by"],numberWords(d)),true];}
  if(PHONE.test(tok)&&[...tok].filter(c=>/\d/.test(c)).length>=8) return [digits(tok),true];
  if((m=DEC.exec(tok))) return [intWords(m[1]).concat(["point"],digits(m[2])),true];
  if(INT.test(tok)){const dg=tok.replace(/,/g,""),n=+dg;
    if(DIAL.has(prev.toLowerCase())&&!tok.includes(",")&&dg.length>=3) return [digits(dg),true];
    if(dg.length>=10&&!tok.includes(",")) return [digits(dg),true];
    if(tok.length===6&&!tok.includes(",")&&tok[0]!=="0"&&!money&&!["rs","rs.","inr","rupees"].includes(prev.toLowerCase())) return [digits(dg),true];
    if(n>=1100&&n<=2099&&tok.length===4){const r=n%100;
      return [u100(Math.floor(n/100)).concat(r>0&&r<10?["oh"].concat(numberWords(r)):r?numberWords(r):["hundred"]),true];}
    return [intWords(tok),true];}
  if((m=RANGE.exec(tok))){const a=say(m[1],prev,false),b=say(m[2],prev,false); if(a&&b) return [a[0].concat(["to"],b[0]),true];}
  if((m=UNIT_JOINED.exec(tok))){let unit=m[2].toLowerCase(); if(unit==="l"&&money) unit="lakh";
    if(UNITS[unit]){const n=say(m[1],prev,false); if(n) return [n[0].concat(one(m[1],UNITS[unit])),true];}}
  if(tok.includes("-")&&/\d/.test(tok)){const o=[];
    for(const part of tok.split("-")){ if(!part) continue; const r=say(part,prev,false); o.push(...(r?r[0]:[part])); }
    return [o,false];}
  if(prevNum&&UNITS[low]){ if(low==="l"&&money) return [["lakh"],false]; return [one(prev,UNITS[low]),false]; }
  if(ALWAYS.has(low)) return [one(prev,UNITS[low]),false];
  if(prevNum&&["am","a.m","a.m."].includes(low)) return [["ay","em"],false];
  if(prevNum&&["pm","p.m","p.m."].includes(low)) return [["pee","em"],false];
  return null;
}
const DEVA_DIG=s=>s.replace(/[०-९]/g,c=>String(c.charCodeAt(0)-0x966));
function prepass(t){for(const [rx,rep] of PRE) t=t.replace(rx,rep);
  return t.replace(ROMAN_RE,(m,name,num)=>{const n=ROMAN[num];
    return ROMAN_COUNT.has(name.toLowerCase())?name+" "+numberWords(n).join(" "):name+" the "+ordinalWords(n).join(" ");});}
const stripCh=(s,ch)=>{let a=0,b=s.length; while(a<b&&ch.includes(s[a]))a++; while(b>a&&ch.includes(s[b-1]))b--; return s.slice(a,b);};
function normalise(text){
  text=prepass(DEVA_DIG(text));
  money=MONEY_CTX.test(text);
  if(text.includes(" ")&&/\d/.test(text)) text=text.replace(SPACED_PHONE,w=>[...w].filter(c=>/\d/.test(c)).length>=10?w.split(" ").join("-"):w);
  for(const k in UFRAC) if(text.includes(k)) text=text.split(k).join(" "+UFRAC[k]);
  text=text.replace(/[।॥]/g,".");
  const out=[]; let prev="",prevNum=false;
  for(let raw of text.split(/\s+/).filter(Boolean)){
    let trail="";
    if(["a.m.","p.m."].includes(raw.toLowerCase())) raw=raw.slice(0,-1)+"@";
    while(raw&&".,!?;:".includes(raw[raw.length-1])){trail=raw[raw.length-1]+trail; raw=raw.slice(0,-1);}
    raw=raw.replace(/@/g,".");
    if(!raw){out.push(trail); prev=""; prevNum=false; continue;}
    const tok=stripCh(raw,"\"'()[]");
    if(!tok){ if(trail) out.push(trail); continue; }
    const low=tok.toLowerCase().replace(/\.+$/,"");
    const said=say(tok,prev,prevNum);
    if(said){out.push(...said[0]); prevNum=said[1];}
    else if(ABBREV[low]){out.push(...ABBREV[low]); prevNum=false;}
    else if([...tok].some(c=>SYMBOL[c])){
      for(const part of tok.match(/\d+|[A-Za-z]+|./gu)||[]){
        if(SYMBOL[part]) out.push(...SYMBOL[part]); else if(/^\d+$/.test(part)) out.push(...numberWords(+part));
        else if(/^\p{L}+$/u.test(part)) out.push(part);
      }
      prevNum=false;
    } else {out.push(tok); prevNum=false;}
    prev=tok;
    if(trail){out.push(trail); prevNum=prevNum&&!".!?".includes(trail);}
  }
  return out.filter(Boolean);
}
return {normalise,numberWords};
})();

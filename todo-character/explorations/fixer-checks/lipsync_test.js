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

const VS={X:[0,1,0],A:[0,.90,0],B:[.22,1.06,0],C:[.58,.92,1],D:[1,.84,1],
          E:[.50,.66,1],F:[.44,.42,1],G:[.14,.84,0],H:[.70,.88,1]};
const VD={X:.09,A:.07,B:.075,C:.125,D:.145,E:.125,F:.13,G:.085,H:.115};
const BLEND=.070, WORD_GAP=.055, COMMA_PAUSE=.20, STOP_PAUSE=.34;

/* ---- pronunciation (mirrors pronounce.py) -----------------------------
   Letters do not predict English pronunciation, and numbers are not letters
   at all: "I have 25 books" used to produce NO mouth for the 25, so the face
   silently skipped a word the voice was saying. The chain is now
   text -> normalise -> words -> phonemes -> visemes. */

const ONES=["zero","one","two","three","four","five","six","seven","eight","nine","ten",
 "eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"];
const TENS=["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"];
const ORD={one:"first",two:"second",three:"third",five:"fifth",eight:"eighth",nine:"ninth",twelve:"twelfth"};
const under100=n=>n<20?[ONES[n]]:[TENS[(n/10)|0]].concat(n%10?[ONES[n%10]]:[]);
const under1000=n=>{const h=(n/100)|0,r=n%100,o=[];if(h)o.push(ONES[h],"hundred");if(r)o.push(...under100(r));return o;};
function numWords(n){
  if(n<0) return ["minus"].concat(numWords(-n));
  if(n===0) return ["zero"];
  let o=[];
  for(const [v,name] of [[1e9,"billion"],[1e6,"million"],[1e3,"thousand"]])
    if(n>=v){ o.push(...under1000(Math.floor(n/v)),name); n%=v; }
  if(n) o.push(...under1000(n));
  return o;
}
function ordWords(n){const w=numWords(n),l=w[w.length-1];
  w[w.length-1]=ORD[l]||(l.endsWith("y")?l.slice(0,-1)+"tieth":l+"th"); return w;}
const SYM={"%":["percent"],"&":["and"],"@":["at"],"+":["plus"],"=":["equals"],
 "\u00b0":["degrees"],"#":["number"],"/":["slash"],"\u20b9":["rupees"],"$":["dollars"],
 "\u20ac":["euros"],"\u00a3":["pounds"]};
const ABB={rs:["rupees"],dr:["doctor"],mr:["mister"],mrs:["missus"],ms:["miss"],
 vs:["versus"],etc:["etcetera"],am:["ay","em"],pm:["pee","em"],kg:["kilos"],
 km:["kilometres"],ok:["okay"],tv:["tee","vee"]};

const normalise=t=>PRON.normalise(t);

/* The lexicon carries the irregular high-frequency words, which is where
   nearly all of English's error lives. CMUdict would replace it wholesale -
   lookup() is the seam. */
const LEX={"a":"AH","the":"DH AH","to":"T UW","do":"D UW","does":"D AH Z","done":"D AH N","of":"AH V","off":"AO F","one":"W AH N","two":"T UW","three":"TH R IY","four":"F AO R","five":"F AY V","six":"S IH K S","seven":"S EH V AH N","eight":"EY T","nine":"N AY N","ten":"T EH N","eleven":"IH L EH V AH N","twelve":"T W EH L V","twenty":"T W EH N T IY","thirty":"TH ER T IY","forty":"F AO R T IY","fifty":"F IH F T IY","hundred":"HH AH N D R AH D","thousand":"TH AW Z AH N D","million":"M IH L Y AH N","zero":"Z IH R OW","point":"P OY N T","rupees":"R UW P IY Z","percent":"P ER S EH N T","i":"AY","you":"Y UW","your":"Y AO R","he":"HH IY","she":"SH IY","we":"W IY","they":"DH EY","them":"DH EH M","their":"DH EH R","there":"DH EH R","these":"DH IY Z","those":"DH OW Z","this":"DH IH S","that":"DH AE T","what":"W AH T","who":"HH UW","where":"W EH R","when":"W EH N","why":"W AY","how":"HH AW","which":"W IH CH","was":"W AH Z","were":"W ER","are":"AA R","is":"IH Z","been":"B IH N","have":"HH AE V","has":"HH AE Z","had":"HH AE D","said":"S EH D","says":"S EH Z","say":"S EY","come":"K AH M","came":"K EY M","some":"S AH M","none":"N AH N","could":"K UH D","would":"W UH D","should":"SH UH D","through":"TH R UW","though":"DH OW","thought":"TH AO T","tough":"T AH F","rough":"R AH F","enough":"IH N AH F","cough":"K AO F","laugh":"L AE F","daughter":"D AO T ER","eye":"AY","eyes":"AY Z","buy":"B AY","by":"B AY","women":"W IH M AH N","woman":"W UH M AH N","water":"W AO T ER","many":"M EH N IY","any":"EH N IY","again":"AH G EH N","friend":"F R EH N D","people":"P IY P AH L","busy":"B IH Z IY","business":"B IH Z N AH S","minute":"M IH N AH T","knight":"N AY T","know":"N OW","knew":"N UW","knee":"N IY","write":"R AY T","wrong":"R AO NG","wrap":"R AE P","hour":"AW ER","honest":"AA N AH S T","honour":"AA N ER","island":"AY L AH N D","listen":"L IH S AH N","castle":"K AE S AH L","often":"AO F AH N","answer":"AE N S ER","sword":"S AO R D","school":"S K UW L","chaos":"K EY AA S","character":"K EH R IH K T ER","machine":"M AH SH IY N","chef":"SH EH F","ocean":"OW SH AH N","sure":"SH UH R","sugar":"SH UH G ER","question":"K W EH S CH AH N","nature":"N EY CH ER","picture":"P IH K CH ER","phone":"F OW N","photo":"F OW T OW","graph":"G R AE F","rhythm":"R IH DH AH M","wednesday":"W EH N Z D EY","colonel":"K ER N AH L","once":"W AH N S","only":"OW N L IY","other":"AH DH ER","another":"AH N AH DH ER","mother":"M AH DH ER","father":"F AA DH ER","brother":"B R AH DH ER","very":"V EH R IY","every":"EH V R IY","city":"S IH T IY","baby":"B EY B IY","happy":"HH AE P IY","family":"F AE M AH L IY","my":"M AY","me":"M IY","be":"B IY","see":"S IY","go":"G OW","no":"N OW","so":"S OW","now":"N AW","new":"N UW","put":"P UH T","push":"P UH SH","pull":"P UH L","full":"F UH L","good":"G UH D","book":"B UH K","books":"B UH K S","look":"L UH K","foot":"F UH T","food":"F UW D","blood":"B L AH D","door":"D AO R","floor":"F L AO R","poor":"P UH R","heart":"HH AA R T","heard":"HH ER D","learn":"L ER N","earth":"ER TH","early":"ER L IY","world":"W ER L D","work":"W ER K","word":"W ER D","worth":"W ER TH","great":"G R EY T","break":"B R EY K","steak":"S T EY K","bread":"B R EH D","head":"HH EH D","ready":"R EH D IY","dead":"D EH D","death":"D EH TH","health":"HH EH L TH","please":"P L IY Z","thank":"TH AE NG K","thanks":"TH AE NG K S","yes":"Y EH S","okay":"OW K EY","hello":"HH AH L OW","today":"T AH D EY","tomorrow":"T AH M AA R OW","yesterday":"Y EH S T ER D EY","morning":"M AO R N IH NG","night":"N AY T","light":"L AY T","right":"R AY T","might":"M AY T","high":"HH AY","sign":"S AY N","half":"HH AE F","calm":"K AA M","palm":"P AA M","talk":"T AO K","walk":"W AO K","call":"K AO L","ball":"B AO L","small":"S M AO L","all":"AO L","also":"AO L S OW","climb":"K L AY M","comb":"K OW M","lamb":"L AE M","doubt":"D AW T","debt":"D EH T","subtle":"S AH T AH L","science":"S AY AH N S","scene":"S IY N","scissors":"S IH Z ER Z","use":"Y UW Z","used":"Y UW Z D","usually":"Y UW ZH AH L IY","beautiful":"B Y UW T AH F AH L","europe":"Y UH R AH P","give":"G IH V","live":"L IH V","love":"L AH V","above":"AH B AH V","move":"M UW V","prove":"P R UW V","lose":"L UW Z","close":"K L OW Z","whose":"HH UW Z","shoe":"SH UW","true":"T R UW","blue":"B L UW","chapati":"CH AH P AA T IY","namaste":"N AH M AH S T EY","india":"IH N D IY AH","aai":"AA IY","ay":"EY","bee":"B IY","dee":"D IY","ee":"IY","ef":"EH F","jee":"JH IY","aitch":"EY CH","jay":"JH EY","kay":"K EY","el":"EH L","em":"EH M","en":"EH N","pee":"P IY","cue":"K Y UW","ar":"AA R","ess":"EH S","tee":"T IY","vee":"V IY","ex":"EH K S","zed":"Z EH D","paise":"P AY S AH","minus":"M AY N AH S","celsius":"S EH L S IY AH S","per":"P ER","times":"T AY M Z"};
const LEXICON={}; for(const k in LEX) LEXICON[k]=LEX[k].split(" ");
const lookup=w=>LEXICON[w.toLowerCase()]||null;

const RULES=[["ough","AH F"],["augh","AE F"],["tion","SH AH N"],["sion","ZH AH N"],
 ["ture","CH ER"],["ight","AY T"],["tch","CH"],["dge","JH"],["ck","K"],["qu","K W"],
 ["sch","S K"],["ph","F"],["gh",""],["kn","N"],["wr","R"],["wh","W"],["ch","CH"],
 ["sh","SH"],["th","TH"],["ng","NG"],["ee","IY"],["ea","IY"],["ie","IY"],["ei","EY"],
 ["oo","UW"],["ou","AW"],["ow","AW"],["oi","OY"],["oy","OY"],["au","AO"],["aw","AO"],
 ["ai","EY"],["ay","EY"],["oa","OW"],["oe","OW"],["ar","AA R"],["er","ER"],["ir","ER"],
 ["ur","ER"],["or","AO R"]];
const LETTER={a:"AE",b:"B",c:"K",d:"D",e:"EH",f:"F",g:"G",h:"HH",i:"IH",j:"JH",k:"K",
 l:"L",m:"M",n:"N",o:"AA",p:"P",q:"K",r:"R",s:"S",t:"T",u:"AH",v:"V",w:"W",x:"K S",y:"Y",z:"Z"};
const LONG={a:"EY",e:"IY",i:"AY",o:"OW",u:"UW"};
const VOW="aeiou";
function rulePhonemes(word){
  let w=word.toLowerCase();
  const magic=w.length>3&&w.endsWith("e")&&!VOW.includes(w[w.length-2])&&[...w.slice(0,-2)].some(c=>VOW.includes(c));
  if(magic) w=w.slice(0,-1);
  if(w.length>1&&(w.endsWith("y")||w.endsWith("i"))) w=w.slice(0,-1)+(w.length<=3?"\u0001":"\u0002");
  let lastV=-1; for(let k=w.length-1;k>=0;k--) if(VOW.includes(w[k])){lastV=k;break;}
  const out=[]; let i=0;
  outer: while(i<w.length){
    if(w[i]==="\u0001"){out.push("AY");i++;continue;}
    if(w[i]==="\u0002"){out.push("IY");i++;continue;}
    for(const [seq,ph] of RULES) if(w.startsWith(seq,i)){ if(ph) out.push(...ph.split(" ")); i+=seq.length; continue outer; }
    const c=w[i];
    if(VOW.includes(c)&&magic&&lastV===i) out.push(LONG[c]);
    else if(/[a-z]/.test(c)) out.push(...LETTER[c].split(" "));
    i++;
  }
  return out.filter((p,j)=>j===0||p!==out[j-1]);
}
function phonemes(word){
  const hit=lookup(word); if(hit) return hit.slice();
  const core=word.replace(/[^A-Za-z]/g,""); return core?rulePhonemes(core):[];
}

/* ARPAbet -> viseme. This half IS solved: given a phoneme the mouth shape is
   not in doubt. Diphthongs get TWO cues because they are two positions -
   which is why Rhubarb writes "Hi" as D then B. */
const PHON={P:["A"],B:["A"],M:["A"],F:["G"],V:["G"],L:["H"],
 W:["F"],UW:["F"],UH:["F"],R:["E"],ER:["E"],AO:["E"],
 AA:["D"],AE:["D"],AH:["C"],EH:["C"],IH:["B"],IY:["B"],
 AY:["D","B"],AW:["D","F"],EY:["C","B"],OW:["E","F"],OY:["E","B"],
 T:["B"],D:["B"],N:["B"],S:["B"],Z:["B"],K:["B"],G:["B"],NG:["B"],Y:["B"],
 CH:["B"],JH:["B"],SH:["B"],ZH:["B"],TH:["B"],DH:["B"],HH:[]};

function english(word){
  const out=[];
  for(const ph of phonemes(word)) out.push(...(PHON[ph]||["B"]));
  return out.filter((s,j)=>j===0||s!==out[j-1]);
}
const DV={"अ":"C","आ":"D","इ":"B","ई":"B","उ":"F","ऊ":"F",
 "ए":"C","ऐ":"C","ओ":"E","औ":"F","ऋ":"E"};
const DM={"ा":"D","ि":"B","ी":"B","ु":"F","ू":"F","ृ":"E",
 "े":"C","ै":"C","ो":"E","ौ":"F"};
const DC={"प":"A","फ":"G","ब":"A","भ":"A","म":"A",
 "व":"G","ल":"H","ळ":"H","र":"E"};
const VIRAMA="्";
function devanagari(word){
  const ch=[...word], out=[];
  for(let i=0;i<ch.length;i++){
    const c=ch[i], nx=ch[i+1]||"";
    if(DV[c]) out.push(DV[c]);
    else if(DM[c]) out.push(DM[c]);
    else if(c==="ं"||c==="ँ") out.push("A");
    else if((c>="क"&&c<="ह")||(c>="क़"&&c<="य़")){
      out.push(DC[c]||"B");
      if(nx!==VIRAMA&&!DM[nx]) out.push("C");     // inherent short 'a'
    }
  }
  // Marathi and Hindi drop the word-final inherent vowel: "namaskaar".
  if(out.length>2&&out[out.length-1]==="C") out.pop();
  return out.filter((s,j)=>j===0||s!==out[j-1]);
}
const wordShapes=w=>/[ऀ-ॿ]/.test(w)?devanagari(w):english(w);

class VisemeTrack{
  constructor(text,rate,crisp){
    const speed=Math.max(.45,Math.min(2.2,rate/5.2));
    const hold=(1-.28*Math.max(0,Math.min(1,crisp)))/speed;
    let t=0; this.cues=[]; this.words=[];
    const push=(shape,d)=>{
      const last=this.cues[this.cues.length-1];
      if(last&&last.shape===shape) last.t1+=d;    // a held shape is one cue
      else this.cues.push({t0:t,t1:t+d,shape,stress:.5});
      t+=d;
    };
    // Say the text the way a voice would BEFORE looking for mouth shapes.
    // Latin runs are normalised together (a number's reading depends on its
    // neighbours); Devanagari passes through; Devanagari digits are numbers.
    text=text.replace(/[०-९]/g,c=>String(c.charCodeAt(0)-0x966))
             .replace(/(?<=[^ऀ-ॿ\s])[।॥]/g,".");
    const toks=[]; let run=[];
    const flush=()=>{ if(run.length){ const sp=normalise(run.join(" ")); toks.push(...(sp.length?sp:run)); run=[]; } };
    for(const raw of text.split(/\s+/).filter(Boolean)){
      if(/[ऀ-ॿ]/.test(raw)){ flush(); toks.push(raw); } else run.push(raw);
    }
    flush();
    // Lead-in and tail scale with length: a one-word "Okay." is not padded
    // out to over a second.
    const nwords=toks.filter(k=>k.replace(/[^\p{L}\p{N}_ऀ-ॿ]/gu,"")).length;
    const short=Math.max(0,Math.min(1,(nwords-1)/3));
    const lead=.05+.05*short;
    this.cues.push({t0:0,t1:lead,shape:"X",stress:.5}); t=lead;
    toks.forEach((tok,n)=>{
      const letters=tok.replace(/[^\p{L}\p{N}_ऀ-ॿ]/gu,"");
      let shapes=letters?wordShapes(letters):[];
      if(letters&&!shapes.length) shapes=["C"];   // a word is never silently dropped
      if(letters) this.words.push(letters);
      for(const sh of shapes) push(sh,VD[sh]*hold);
      const tail=tok.slice(-1);
      let gap=",;:".includes(tail)?COMMA_PAUSE:".!?।".includes(tail)?STOP_PAUSE:WORD_GAP;
      if(n===toks.length-1) gap=Math.min(gap,WORD_GAP+(STOP_PAUSE-WORD_GAP)*short*.5);
      push("X",gap);                              // the mouth closes between words
    });
    push("X",.10+.08*short);
    this.duration=t;
    let want=true;                                 // first vowel of a word = the beat
    for(const c of this.cues){
      if(c.shape==="X"){want=true;continue;}
      if(want&&VS[c.shape][2]){c.stress=1;want=false;}
    }
  }
  at(t){
    let lo=0,hi=this.cues.length-1;
    while(lo<hi){const m=(lo+hi)>>1; if(this.cues[m].t1<=t) lo=m+1; else hi=m;}
    const cur=this.cues[lo], nxt=this.cues[Math.min(lo+1,this.cues.length-1)];
    const span=Math.min(BLEND,(cur.t1-cur.t0)*.9); let k=0;
    if(span>0&&t>cur.t1-span){
      k=(t-(cur.t1-span))/span;
      k=.5-.5*Math.cos(Math.PI*Math.max(0,Math.min(1,k)));
    }
    return [cur,nxt,k];
  }
  mouth(t){
    if(t<0||t>this.duration) return [0,1];
    const [c,n,k]=this.at(t);
    return [VS[c.shape][0]+(VS[n.shape][0]-VS[c.shape][0])*k,
            VS[c.shape][1]+(VS[n.shape][1]-VS[c.shape][1])*k];
  }
  energy(t){ return Math.max(0,Math.min(1,this.mouth(t)[0]/.95)); }
  accent(t){
    let o=0;
    for(const c of this.cues){ if(c.stress<.9) continue;
      const x=t-c.t0; if(x>=0&&x<.26) o=Math.max(o,(1-x/.26)**2); }
    return o;
  }
  breath(t){ return Math.sin(Math.PI*Math.max(0,Math.min(1,t/this.duration))*2); }
  debug(){ return this.cues.map(c=>c.shape).join(" "); }
}


module.exports={VisemeTrack,normalise};
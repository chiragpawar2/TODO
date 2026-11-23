/* ---- reading: a JS port of reading.py (rules only, no model) -----------
   Same tables (exported from Python as RD), same algorithm: whole-word and
   stem matching, scored families, negation before and after (Hindi/Marathi
   put it after), idioms, life events, regional spellings via canon(),
   emoji, sarcasm, names, levels, and paragraphs as beats.               */
const READER=(function(){
const S=k=>new Set(RD[k]);
const NEGATORS=S("NEGATORS"),SCOPE=S("SCOPE_VERBS"),HEDGE=S("HEDGE_VERBS"),COMPARE=S("COMPARE"),
 KAR=S("KAR"),POST_NEG=S("POST_NEG"),BREAK=S("BREAK"),OTHERS_FUTURE=S("OTHERS_FUTURE"),CONTRAST=S("CONTRAST"),
 MILD=S("MILD_EMOJI"),POSITIVE=S("POSITIVE"),NEGATIVE=S("NEGATIVE"),SARC_PRAISE=S("SARC_PRAISE"),NEUTRAL=S("NEUTRAL"),
 PERSON=S("PERSON"),DEVICE=S("DEVICE"),EXAM=S("EXAM"),COPULA=S("COPULA"),STOP_OK=S("STOP_OK"),MARATHI=S("MARATHI"),
 ANAND_CTX=S("ANAND_CTX"),NEG_PHRASE=S("NEG_PHRASE"),EVENT_KEYS=S("EVENT_KEYS"),KILL_KEYS=S("KILL_KEYS"),
 NOISY=S("NOISY"),BODY=S("BODY"),PLANT=S("PLANT"),PAIN=S("PAIN"),GLUE=S("GLUE"),CGLUE=S("CGLUE"),STRONG=S("STRONG"),
 ACRONYMS=S("ACRONYMS"),UP=S("UP"),SO_STOP=S("SO_STOP"),UP2=S("UP2"),FLAT_EXEMPT=S("FLAT_EXEMPT"),TITLES=S("TITLES"),
 KIN=S("KIN"),OCCASION=S("OCCASION"),TYPO_BLOCK=S("TYPO_BLOCK"),EN_SUFFIX=S("EN_SUFFIX"),FREE_STEMS=S("FREE_STEMS");
const DEVA_SUF={}; for(const k in RD.DEVA) DEVA_SUF[k]=new Set(RD.DEVA[k][1]);
const re=(k,f="")=>new RegExp(RD.RE[k],f);
const TO_BOT_INSULT=re("_TO_BOT_INSULT"),TO_BOT_PRAISE=re("_TO_BOT_PRAISE"),SARC_AGAIN=re("_SARC_AGAIN"),
 SARC_EVENT=re("_SARC_EVENT"),SARC_NOUN=re("_SARC_NOUN"),SARC_SET=re("_SARC_SET"),SARC_MORE=re("_SARC_MORE"),
 LAUGH=re("_LAUGH"),BANG_LOSS=re("_BANG_LOSS"),BANG_RUSH=re("_BANG_RUSH"),BANG_MED=re("_BANG_MED"),
 TO_BOT_WRONG=new RegExp(RD.TO_BOT_WRONG);
const TOKEN=/[a-z0-9'ऀ-ॣ०-ॿ‌‍]+|[!?.,;\-]/gu;
const ORIG_TOKEN=/[A-Za-z0-9'ऀ-ॣ०-ॿ‌‍]+|[!?.,;\-]/gu;
const NUKTA="़", RUN3=/([a-z])\1{2,}/, RUN3G=/([a-z])\1{2,}/g, DEVA=/[ऀ-ॿ]/,
 HELD_OH=/^(?:o+h{3,}|o{3,}h+)$/;
const EMO_KEYS=Object.keys(RD.EMOJI).sort((a,b)=>b.length-a.length);
const EMOJI_RE=new RegExp(EMO_KEYS.map(k=>k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|"),"gu");
const isAscii=s=>/^[\x00-\x7f]*$/.test(s), isAlphaA=s=>/^[a-z]+$/i.test(s);
const LV={low:0,mid:1,intense:2};
function levelAmount(name,level){const l=RD.LEVELS[name]||RD.DEF_LEVELS; return l[LV[level]??1];}

// lexicon.canon
const CANON_SUB=[["chh","ch"],["kh","k"],["gh","g"],["jh","j"],["z","j"],["bh","b"],["dh","d"],["th","t"],
 ["ph","f"],["w","v"],["q","k"],["oo","u"],["ee","i"],["aa","a"],["ii","i"],["uu","u"]];
function canon(w){
  if(!isAscii(w)||!isAlphaA(w)||w.length<3) return w;
  for(const [a,b] of CANON_SUB) if(w.includes(a)) w=w.split(a).join(b);
  w=w.replace(/([a-z])\1+/g,"$1");
  if(w.length>3&&w.endsWith("ay")) w=w.slice(0,-1);
  else if(w.length>3&&w.endsWith("ai")&&!w.endsWith("hai")) w=w.slice(0,-1);
  return w;
}
function inflected(w){
  const c=[];
  if(w.endsWith("ies")) c.push(w.slice(0,-3)+"y");
  if(w.endsWith("ier")||w.endsWith("ied")) c.push(w.slice(0,-3)+"y");
  if(w.endsWith("iest")) c.push(w.slice(0,-4)+"y");
  for(const suf of["s","es","ed","d","er","est","ing"]){
    if(w.endsWith(suf)&&w.length-suf.length>=3){
      const b=w.slice(0,-suf.length); c.push(b);
      if(b.length>=2&&b[b.length-1]===b[b.length-2]) c.push(b.slice(0,-1));
      c.push(b+"e");
    }
  }
  for(const x of c) if(RD.SINGLE[x]) return RD.SINGLE[x];
  return null;
}
function typo(w){
  if(w.length<6||TYPO_BLOCK.has(w)||!isAlphaA(w)) return null;
  if(RD.DELETES[w]) return RD.SINGLE[RD.DELETES[w]];
  for(let i=0;i<w.length;i++){const d=w.slice(0,i)+w.slice(i+1); if(RD.SINGLE[d]&&d.length>=6) return RD.SINGLE[d];}
  for(let i=0;i<w.length-1;i++){const t=w.slice(0,i)+w[i+1]+w[i]+w.slice(i+2); if(RD.SINGLE[t]) return RD.SINGLE[t];}
  return null;
}
function clean(text){
  const t=text.replace(/’|‘/g,"'").replace(/️/g,"").split(NUKTA).join("");
  const emo=isAscii(t)?[]:(t.match(EMOJI_RE)||[]).map(m=>[RD.EMOJI[m],m]);
  return [t.toLowerCase(),emo];
}
const T=w=>RD.TYPO[w]??w;
function tokens(low){
  const raw=low.match(TOKEN)||[];
  if(!RUN3.test(low)) return [raw.map(T)];
  return [raw.map(w=>T(w.replace(RUN3G,"$1"))), raw.map(w=>T(w.replace(RUN3G,"$1$1")))];
}
function isDesi(toks){
  for(const t of toks) if(GLUE.has(t)||(isAscii(t)&&t.length>2&&CGLUE.has(canon(t)))) return true;
  return false;
}
function hits(toks,desi){
  const out=[], n=toks.length, ct=desi?toks.map(canon):null;
  let i=0;
  while(i<n){
    let found=null;
    for(let L=Math.min(RD.LONGEST,n-i);L>0;L--){
      let e=RD.EXACT[toks.slice(i,i+L).join(" ")];
      if(!e&&desi) e=RD.CEXACT[ct.slice(i,i+L).join(" ")];
      if(e){found=[e,L];break;}
    }
    if(!found){
      const w=toks[i];
      if(isAscii(w)){
        for(const sl of RD.STEM_LENS){
          const st=w.slice(0,sl);
          if(sl<=w.length&&RD.STEMS[st]&&(EN_SUFFIX.has(w.slice(sl))||FREE_STEMS.has(st))){found=[RD.STEMS[st],1];break;}
        }
        if(!found&&w.length>=4&&isAlphaA(w)){const e=inflected(w)||typo(w); if(e) found=[e,1];}
      } else if(DEVA.test(w)){
        for(const sl of RD.DEVA_LENS){
          // Python slices by code point; Devanagari is all BMP so .slice matches
          const st=w.slice(0,sl);
          if(sl<w.length&&RD.DEVA[st]&&DEVA_SUF[st].has(w.slice(sl))){found=[RD.DEVA[st][0],1];break;}
        }
      }
    }
    if(found){const [[fam,k,wt],L]=found; if(fam!==null) out.push([fam,k,wt,i,L]); i+=L;}
    else i++;
  }
  return out;
}
function negated(toks,i,L){
  let reach=3, scope=false;
  for(let j=i-1;j>=0&&j>=i-reach;j--){
    const t=toks[j];
    if(BREAK.has(t)) break;
    if(SCOPE.has(t)&&!scope){scope=t; reach+=3;}
    if(NEGATORS.has(t)){
      const between=toks.slice(j+1,i), kw=toks[i];
      if((t==="never"||t==="not")&&(between.some(b=>COMPARE.has(b))||kw.endsWith("er")||kw.endsWith("est")
         ||kw==="better"||kw==="best")){ if(t==="never") return 0; }
      if(scope&&HEDGE.has(scope)) return 2;
      return 1;
    }
  }
  for(let j=i+L;j<Math.min(toks.length,i+L+2);j++){
    const t=toks[j];
    if(BREAK.has(t)) break;
    if(POST_NEG.has(t)){
      if(["mat","मत","nako","नको"].includes(t)&&j+1<toks.length&&KAR.has(toks[j+1])) return 0;
      return 1;
    }
  }
  return 0;
}
const rstripS=t=>t.replace(/['s]+$/,"");
function context(fam,k,toks,i,L){
  const prev=i?toks[i-1]:"", nxt=i+L<toks.length?toks[i+L]:"",
   before=toks.slice(Math.max(0,i-4),i), after=toks.slice(i+L,i+L+4);
  const any=(a,f)=>a.some(f);
  if(["died","dies","dying","died."].includes(k)){
    if(any(before,t=>DEVICE.has(t))) return "fret";
    if(any(before,t=>PLANT.has(t))) return "sad";
  } else if(KILL_KEYS.has(k)){
    if(any(toks.slice(Math.max(0,i-4),i),t=>BODY.has(t))) return "worried";
  } else if(PAIN.has(k)||k==="hurt"){
    if(any(toks,t=>BODY.has(t))) return "worried";
    if(k!=="hurt"&&!any(toks,t=>["feelings","heart","inside"].includes(t))) return "worried";
    return "sad";
  } else if(k==="too loud"||k==="so loud"){
    if(any(toks,t=>NOISY.has(rstripS(t)))) return "angry";
  } else if(k==="passed"){
    if(nxt&&!BREAK.has(nxt)&&!any(after,t=>EXAM.has(t))) return null;
  } else if(k==="stop"){
    if(i&&!STOP_OK.has(prev)&&!BREAK.has(prev)) return null;
  } else if(k==="fire"){
    if(["up","extinguisher","brigade","place","wood","pit","drill"].includes(nxt)) return null;
    if(["on","the","low","medium","high","slow","camp","open"].includes(prev)&&
       !any(toks,t=>["house","kitchen","building","smoke","help"].includes(t))) return null;
  } else if(k==="fell"){
    if(!any(before,t=>PERSON.has(t))&&!["down","off","over","from"].includes(nxt)) return null;
  } else if(k==="sick"){
    if(any(before,t=>PERSON.has(t))||["feel","feeling","felt","got","getting"].includes(prev)) return "worried";
    if(COPULA.has(prev)||prev==="so"||prev==="that's") return "delight";
  } else if(k==="on fire"){
    const who=new Set(["i'm","you're","he's","she's","we're","they're","you","i","he","she","team","they","we","are","were"]);
    return any(before,t=>who.has(t))?"delight":"alarmed";
  } else if(k==="bang"){ if(nxt==="on") return "proud";
  } else if(k==="anand"||k==="आनंद"){
    if(!(ANAND_CTX.has(nxt)||UP.has(prev)||["bada","बड़ा","बडा","khup","खूप"].includes(prev))) return null;
  } else if(k==="bhari"||k==="भारी"){ if(!any(toks,t=>MARATHI.has(t))) return null; }
  return fam;
}
function score(toks,low,emo,names){
  const scores=new Map(), why=new Map();
  const add=(f,a,k)=>{scores.set(f,(scores.get(f)||0)+a); if(a>(why.has(f)?why.get(f)[0]:0)) why.set(f,[a,k]);};
  const pop=f=>{scores.delete(f); why.delete(f);};
  let contrastAt=-1; toks.forEach((t,i)=>{if(CONTRAST.has(t)) contrastAt=i;});
  const hs=hits(toks,isDesi(toks)), praise=[];
  const worded=hs.some(h=>!EVENT_KEYS.has(h[1])&&h[0]!=="_neg"&&h[2]>=1.0);
  for(let [fam,k,wt,i,L] of hs){
    if(worded&&EVENT_KEYS.has(k)) wt*=0.45;
    if(names.has(i)) continue;
    fam=context(fam,k,toks,i,L);
    if(fam===null) continue;
    if(contrastAt>=0&&i>contrastAt) wt*=1.25;
    if(i>=2&&toks[i-1]==="be"&&OTHERS_FUTURE.has(toks[i-2])) wt*=0.6;
    const neg=(k.startsWith("not ")||k.startsWith("can't ")||k.startsWith("cannot ")||NEG_PHRASE.has(k)
      ||(L>1&&EVENT_KEYS.has(k)&&toks.slice(i,i+L).some(t=>NEGATORS.has(t))))?0:negated(toks,i,L);
    if(fam==="_neg"){ if(neg===1) add(RD.NEG_ONLY[k],1.1,"not "+k); continue; }
    if(neg===2){ add(POSITIVE.has(fam)?"skeptical":NEGATIVE.has(fam)?"content":fam, wt*0.7,"hedged "+k); continue; }
    if(neg&&["angry","stern","sad","crying"].includes(fam)&&i>=2&&toks[i-1]==="be"&&
       toks.slice(Math.max(0,i-5),i).includes("please")){ add("worried",wt*0.9,"please don't be "+k); continue; }
    if(neg){ const fl=RD.NEG_FLIP[fam]; if(fl) add(fl,wt*0.7,"not "+k); continue; }
    add(fam,wt,k);
    if(SARC_PRAISE.has(k)||k==="oh great") praise.push(k);
  }
  const wordedAny=scores.size>0;
  for(const [ef,ch] of emo){
    if(ef==="crying"&&[...scores.keys()].some(f=>POSITIVE.has(f)&&f!=="content")){ add("delight",1.6,"emoji (happy tears)"); continue; }
    let w=wordedAny?1.0:2.0; if(MILD.has(ch)) w*=0.5;
    add(ef,w,"emoji");
  }
  if(TO_BOT_WRONG.test(low)){ for(const f of["angry","stern","skeptical","sad"]) pop(f); add("apologetic",3.0,"told I was wrong"); }
  else if(TO_BOT_INSULT.test(low)) add("sad",3.0,"said to me");
  else if(TO_BOT_PRAISE.test(low)) add("happy",2.5,"said to me");
  if(low.includes("?!")||low.includes("!?")) add("angry",1.2,"?!");
  if(scores.has("crying")&&["crying","cry","cried","in tears"].includes(why.get("crying")[1])){
    if(LAUGH.test(low)||low.includes("laugh")){const s=scores.get("crying"),w=why.get("crying")[1]; pop("crying"); add("grin",s+0.5,w+" (laughing)");}
    else if(scores.has("happy")||scores.has("delight")){const s=scores.get("crying"),w=why.get("crying")[1]; pop("crying"); add("delight",s,w+" (happy tears)");}
  }
  const others=[...scores.keys()].filter(f=>!["delight","happy","content","skeptical"].includes(f));
  if(SARC_SET.test(low)||SARC_MORE.test(low)||(praise.length&&SARC_AGAIN.test(low)&&SARC_NOUN.test(low))||
     (praise.length&&SARC_EVENT.test(low)&&!others.length)){
    for(const f of["delight","happy","tender","love"]) pop(f);
    add("skeptical",2.5,(praise.length?praise[0]:"set phrase")+" (sarcastic)");
  }
  return [scores,why];
}
const shoutWords=t=>t.match(/\b[A-Z]{2,}\b/g)||[];
function capsLock(text){
  const L=[...text].filter(c=>/[A-Za-z]/.test(c));
  return L.length>=6&&L.every(c=>c===c.toUpperCase())&&text.trim().split(/\s+/).length>=3;
}
const shouting=t=>shoutWords(t).some(w=>!ACRONYMS.has(w));
function elongated(raw){let n=0; for(const w of raw) if(RUN3.test(w)&&!/^(?:h?m+|w+|z+|ha(ha)*h?|\.+)$/.test(w)) n++; return n;}
const QUESTION="curious", DEFAULT="attentive";
function levelScore(text,low,toks,emo,matched,why){
  let s=0; const bangs=(low.match(/!/g)||[]).length;
  s+=bangs>=2?2:bangs===1?1:0;
  if((low.match(/\?/g)||[]).length>=2) s+=1;
  const emotional=matched!=null&&!NEUTRAL.has(matched)&&![QUESTION,"searching","thinking"].includes(matched);
  if(capsLock(text)){ if(emotional) s+=2; } else if(shouting(text)) s+=2;
  s+=Math.min(2,elongated(low.match(TOKEN)||[]));
  let up=0;
  toks.forEach((t,i)=>{const nx=i+1<toks.length?toks[i+1]:null;
    if(UP.has(t)) up=1; else if(t==="so"&&nx&&!SO_STOP.has(nx)&&!BREAK.has(nx)) up=1; else if(nx&&UP2.has(t+" "+nx)) up=1;});
  s+=up;
  let down=0;
  toks.forEach((t,i)=>{const nx=i+1<toks.length?toks[i+1]:null;
    if(nx&&RD.DOWN2[t+" "+nx]!==undefined&&!(i&&toks[i-1]==="in")) down=Math.max(down,RD.DOWN2[t+" "+nx]);
    else if(RD.DOWN1[t]!==undefined) down=Math.max(down,RD.DOWN1[t]);});
  s-=down;
  if(why&&(STRONG.has(why)||STRONG.has(why.split(" (")[0]))) s+=1;
  else if(why&&why.startsWith("not ")&&STRONG.has(why.slice(4))) s-=1;
  if(emo.length>=2) s+=1;
  for(let i=0;i<toks.length;i++){
    if(emotional&&why!=="!"&&toks[i]==="never"&&toks.slice(i+1,i+4).some(x=>
       ["this","so","such","more","happier","better","best"].includes(x)||((x.endsWith("ier")||x.endsWith("est"))&&x.length>5))){s+=1;break;}
  }
  const words=low.split(/\s+/).filter(Boolean);
  const strongEmo=emo.length&&!(text.replace(/️/g,"").match(EMOJI_RE)||[]).every(e=>MILD.has(e));
  if(s===0&&words.length<=2&&!bangs&&!low.includes("?")&&!LAUGH.test(low)&&!strongEmo&&
     !(words.length&&FLAT_EXEMPT.has(words[0])&&words.length===2)) s-=1;
  return s;
}
const isUpper=c=>c!==c.toLowerCase()&&c===c.toUpperCase();
const strIsUpper=t=>/[A-Za-z]/.test(t)&&t===t.toUpperCase()&&t!==t.toLowerCase();
function namePositions(text,n){
  const out=new Set();
  if(strIsUpper(text)||![...text].some(isUpper)) return out;
  const t=text.replace(/’|‘/g,"'").replace(/️/g,"").split(NUKTA).join("");
  const raw=t.match(ORIG_TOKEN)||[];
  if(raw.length!==n) return out;
  const words=raw.filter(w=>/^[\p{L}]/u.test(w));
  if(words.length>2&&words.filter(w=>isUpper(w[0])).length>0.6*words.length) return out;
  raw.forEach((w,i)=>{
    if(!(/[A-Z]/.test(w[0]))||strIsUpper(w)) return;
    const prev=i?raw[i-1]:".", nxt=i+1<n?raw[i+1]:"";
    const start=[".","!","?"].includes(prev)||(prev===","&&i===1)||(i>=2&&[".","!","?"].includes(raw[i-2])&&[",","-"].includes(prev));
    const afterTitle=TITLES.has(prev.toLowerCase());
    const surname=nxt&&/[A-Z]/.test(nxt[0])&&!strIsUpper(nxt)&&!OCCASION.has(nxt.toLowerCase());
    const kin=KIN.has(nxt.toLowerCase());
    if(afterTitle||surname||kin||!start) out.add(i);
  });
  return out;
}
const strip=(s,ch)=>{let a=0,b=s.length; while(a<b&&ch.includes(s[a]))a++; while(b>a&&ch.includes(s[b-1]))b--; return s.slice(a,b);};
function choose(text,low,emo){
  if(HELD_OH.test(strip(low," !."))) return ["surprised","ohhh",["oh"]];
  let best=null;
  for(const toks of tokens(low)){
    const [sc,why]=score(toks,low,emo,namePositions(text,toks.length));
    let cand=[0,null,null,toks];
    if(sc.size){
      let fam=null,bs=-1e9,bo=0;
      for(const [f,v] of sc){const o=-(RD.FAM_ORDER[f]??99); if(v>bs||(v===bs&&o>bo)){fam=f;bs=v;bo=o;}}
      cand=[bs,fam,why.get(fam)[1],toks];
    }
    if(best===null||cand[0]>best[0]) best=cand;
  }
  const [sc,fam,why,toks]=best;
  if(fam!==null&&sc<=0.55&&low.includes("?")) return [QUESTION,"?",toks];
  if(fam!==null) return [fam,why,toks];
  const words=toks.filter(t=>!BREAK.has(t)), st=strip(low," !?.");
  if(words.length&&words.every(w=>w==="no")&&(words.length>=2||RUN3.test(low)||low.includes("!"))) return ["worried","no no",toks];
  if(["really","seriously","sach","sachchi","kya","क्या","सच","what"].includes(st)&&(low.includes("?")||low.includes("!"))) return ["surprised",st,toks];
  if(["काय","kay","huh","what"].includes(st)&&low.includes("?")) return ["confusion",st,toks];
  if(text.includes("?")){
    if(low.includes("??")) return shouting(text)?["angry","???",toks]:["confusion","??",toks];
    return [QUESTION,"?",toks];
  }
  if(text.includes("!")){
    const yes=new Set(["yes","yess","yay","haan","ho","hoy","again","more","yeah","yup","ok","okay"]);
    if(words.length&&words.every(w=>yes.has(w))) return ["delight","yes!",toks];
    if(BANG_MED.test(low)) return ["worried","! (medical)",toks];
    if(BANG_RUSH.test(low)) return ["worried","! (deadline)",toks];
    if(BANG_LOSS.test(low)) return ["fret","! (loss)",toks];
    if(words.length&&words.length<=7) return ["delight","!",toks];
    return ["surprised","!",toks];
  }
  return [DEFAULT,null,toks];
}
function read(text){
  const [low,emo]=clean(text);
  const [name,why,toks]=choose(text,low,emo);
  const s=levelScore(text,low,toks,emo,name,why);
  const level=s>=2?"intense":s<=-1?"low":"mid";
  return [name,level,levelAmount(name,level),why];
}
const SENT=/(?<=[.!?।॥])\s+/u;
const TURN=/(?<=[\p{L}\p{N}_]),?\s+(?=(?:but|lekin|par|पर|पण|लेकिन)\s)/iu;
const JOINT=/(?<=[\p{L}\p{N}_]),\s+(?=(?:so|and now|and then|then|phir|mag|ani mag)\s)|\s+(?=(?:and then|because|cause|kyunki|karan)\s)/iu;
const nw=s=>s.trim().split(/\s+/).filter(Boolean).length;
function readBeats(text){
  const parts=[];
  for(const p of text.trim().split(SENT)){
    if(!/[\p{L}\p{N}_]/u.test(p)) continue;
    const bits=p.split(TURN);
    const out=(bits.length>1&&bits.every(b=>nw(b)>=3))?bits:[p];
    for(const b of out){
      const sub=b.split(JOINT);
      if(sub.length>1&&sub.every(x=>nw(x)>=3)){
        const faces=sub.map(x=>read(x)[0]);
        if(faces.every(f=>!NEUTRAL.has(f)&&f!==QUESTION)&&new Set(faces).size===faces.length){parts.push(...sub);continue;}
      }
      parts.push(b);
    }
  }
  if(parts.length<=1) return [[...read(text),1.0]];
  const beats=[];
  for(const p of parts){
    const [name,level,amount,why]=read(p);
    const hold=Math.max(0.9,Math.min(2.2,0.6+0.07*nw(p)));
    const b=beats[beats.length-1];
    if(b&&b[0]===name){ if(amount>b[2]){b[1]=level;b[2]=amount;b[3]=why;} b[4]=Math.min(2.6,b[4]+hold*0.5); continue; }
    beats.push([name,level,amount,why,hold]);
  }
  let i=1;
  while(i<beats.length-1){
    if(beats[i][0]===DEFAULT&&beats[i-1][0]===beats[i+1][0]){
      const a=beats[i-1],b=beats[i+1];
      if(b[2]>a[2]){a[1]=b[1];a[2]=b[2];a[3]=b[3];}
      a[4]=Math.min(2.6,a[4]+beats[i][4]*0.5+b[4]*0.5); beats.splice(i,2); continue;
    }
    i++;
  }
  i=1;
  while(i<beats.length-1){
    if(beats[i][0]===DEFAULT&&beats[i][3]===null&&!NEUTRAL.has(beats[i-1][0])){
      beats[i-1][4]=Math.min(2.6,beats[i-1][4]+beats[i][4]*0.5); beats.splice(i,1);
      if(beats[i-1][0]===beats[i][0]){const a=beats[i-1],b=beats[i]; if(b[2]>a[2]){a[1]=b[1];a[2]=b[2];a[3]=b[3];}
        a[4]=Math.min(2.6,a[4]+b[4]*0.5); beats.splice(i,1);}
      continue;
    }
    i++;
  }
  return beats;
}
return {read,readBeats,levelAmount,canon};
})();

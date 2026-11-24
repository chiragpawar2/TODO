const fs=require("fs");
global.RD=JSON.parse(fs.readFileSync(process.argv[2],"utf8"));
eval(fs.readFileSync(process.argv[3],"utf8")+";global.READER=READER;");
const py=JSON.parse(fs.readFileSync(process.argv[4],"utf8"));
let ok=0,lv=0;
for(const r of py){
  const b=READER.readBeats(r.t).map(x=>[x[0],x[1]]);
  const e=JSON.stringify(b.map(x=>x[0]))===JSON.stringify(r.beats.map(x=>x[0]));
  const l=JSON.stringify(b)===JSON.stringify(r.beats);
  ok+=e; lv+=l;
  if(!l) console.log("DIFF",r.t,JSON.stringify(r.beats),JSON.stringify(b));
}
console.log(`expression ${ok}/${py.length}  expression+level ${lv}/${py.length}`);

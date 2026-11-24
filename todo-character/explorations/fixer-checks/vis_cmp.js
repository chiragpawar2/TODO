const fs=require("fs");
const {VisemeTrack}=require("./lipsync_test.js");
const py=JSON.parse(fs.readFileSync(process.argv[2],"utf8"));
let c=0,d=0;
for(const r of py){const v=new VisemeTrack(r.t,5.2,0.5); const cs=v.debug()===r.cues, ds=Math.abs(v.duration-r.dur)<0.002;
  c+=cs; d+=ds; if(!cs||!ds) console.log("DIFF",r.t,"\n py",r.cues,r.dur,"\n js",v.debug(),v.duration.toFixed(3));}
console.log(`cues ${c}/${py.length} duration ${d}/${py.length}`);

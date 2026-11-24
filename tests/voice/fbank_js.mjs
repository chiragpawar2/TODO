import fs from "fs";
const src=fs.readFileSync(process.argv[2],"utf8"); const body=src.split("/* FBANK-START */")[1].split("/* FBANK-END */")[0];
const fbank=new Function(body+"\nreturn fbank;")();
const w=fs.readFileSync(process.argv[3]); let o=12; let data=null;
while(o<w.length){ const id=w.toString("ascii",o,o+4), sz=w.readUInt32LE(o+4); if(id==="data"){data=w.subarray(o+8,o+8+sz);break;} o+=8+sz; }
const x=new Float32Array(data.length/2); for(let i=0;i<x.length;i++) x[i]=data.readInt16LE(2*i)/32768;
const {feats,frames}=fbank(x); fs.writeFileSync(process.argv[4],Buffer.from(feats.buffer)); console.log("frames",frames);

import json, time, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
d="models/ml-sentiment"
L=[("aaj mera mood bahut kharab hai","neg"),("yaar main bahut udaas hoon","neg"),("mujhe tumhari bahut yaad aa rahi hai","neg"),
("aaj toh maza aa gaya","pos"),("main bahut khush hoon aaj","pos"),("mala khup aanand zala","pos"),("ekdum jhakaas kaam kiya tune","pos"),
("mera dimaag mat kharab karo","neg"),("usne mera phone tod diya, gussa aa raha hai","neg"),("mala khup kantala aalay","neg"),
("tujhi khup aathvan yete","neg"),("papa ki tabiyat theek nahi hai","neg"),("exam ka bahut tension hai","neg"),
("shukar hai sab theek ho gaya","pos"),("wah kya khana banaya hai","pos"),("ye film bilkul bakwas thi","neg"),
("kitna pyaara bachcha hai","pos"),("mujhe darr lag raha hai","neg"),("aaj ka din bahut accha tha","pos"),("mala nahi aavadla he","neg"),
("tu khup goad aahes","pos"),("sab log mujhe ignore karte hain","neg"),("मैं बहुत खुश हूँ","pos"),("मुझे बहुत बुरा लग रहा है","neg"),
("doodh le aana","neu"),("kal subah uthana","neu"),("light band kar do","neu"),("paani garam karo","neu"),("mala chaha de","neu"),
("kitne baje train hai","neu"),("aaj sabzi kya banegi","neu"),("bazaar jaana hai","neu")]
tok=Tokenizer.from_file(f"{d}/tokenizer.json"); tok.enable_truncation(64)
s=ort.InferenceSession(f"{d}/model_quantized.onnx", providers=["CPUExecutionProvider"])
lab=json.load(open(f"{d}/config.json"))["id2label"]; ins=[i.name for i in s.get_inputs()]
right=0; ts=[]
for t,g in L:
    e=tok.encode(t); f={"input_ids":np.array([e.ids]),"attention_mask":np.array([e.attention_mask])}
    if "token_type_ids" in ins: f["token_type_ids"]=np.zeros_like(f["input_ids"])
    t0=time.perf_counter(); lo=s.run(None,f)[0][0]; ts.append(time.perf_counter()-t0)
    p=np.exp(lo-lo.max()); p/=p.sum(); i=int(p.argmax()); l=lab[str(i)][:3]
    ok = l==g[:3]; right+=ok
    print("OK" if ok else "XX", g, lab[str(i)], round(float(p[i]),2), t)
print(right,len(L), "lat ms", round(1e3*np.mean(ts[1:]),1))

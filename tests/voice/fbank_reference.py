import sys, wave, glob, os, numpy as np, onnxruntime as ort
def fbank(x, sr=16000, nb=80):
    fl, fs, nfft = 400, 160, 512
    n = 1 + (len(x)-fl)//fs
    win = (0.5-0.5*np.cos(2*np.pi*np.arange(fl)/(fl-1)))**0.85
    def mel(f): return 1127*np.log(1+f/700)
    lo, hi = mel(20), mel(sr/2)
    c = lo+(hi-lo)*np.arange(nb+2)/(nb+1)
    fm = mel(np.arange(nfft//2+1)*sr/nfft)
    W = np.zeros((nb, nfft//2+1))
    for m in range(nb):
        l, cc, r = c[m], c[m+1], c[m+2]
        up=(fm-l)/(cc-l); dn=(r-fm)/(r-cc)
        W[m]=np.maximum(0,np.minimum(up,dn))*((fm>l)&(fm<r))
    out=np.zeros((n,nb),np.float32)
    for i in range(n):
        f = x[i*fs:i*fs+fl].astype(np.float64)
        f = f-f.mean()
        f = np.append(f[0]-0.97*f[0], f[1:]-0.97*f[:-1])
        f = f*win
        p = np.abs(np.fft.rfft(f, nfft))**2
        out[i] = np.log(np.maximum(W@p, 1.1920929e-07))
    return out
def load(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768; return a
sess=ort.InferenceSession(sys.argv[1])
def emb(x):
    f=fbank(x); f=f-f.mean(0)
    e=sess.run(None,{"x":f[None]})[0][0]; return e/np.linalg.norm(e)
d=sys.argv[2]; fs=sorted(glob.glob(d+"/*.wav")); E={os.path.basename(f):emb(load(f)) for f in fs}
ks=list(E)
for a in ks: print(a.ljust(24), " ".join(f"{E[a]@E[b]:.2f}" for b in ks))
np.save(os.path.join(sys.argv[3],"fb_ref.npy"), fbank(load(fs[0]))[:50])

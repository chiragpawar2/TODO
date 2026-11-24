core = {"happy":"happy","sad":"sad","angry":"angry","tired":"tired","scared":"scared","excited":"excited",
"upset":"upset","bored":"bored","lonely":"lonely","sorry":"sorry","worried":"worried","nervous":"nervous",
"proud":"proud","glad":"glad","crying":"crying","sleepy":"sleepy","annoyed":"annoyed","afraid":"afraid",
"thanks":"thanks","love":"love","hate":"hate","awesome":"awesome","amazing":"amazing","great":"great",
"stressed":"stressed","miss":"miss","yay":"yay","funny":"funny","furious":"furious","relieved":"relieved",
"exhausted":"exhausted","depressed":"depressed","anxious":"anxious","jealous":"jealous","grateful":"grateful",
"terrified":"terrified","confused":"confused","embarrassed":"embarrassed","sick":"sick","hungry":None}
words=set(w.strip().lower() for w in open("/usr/share/dict/words"))
common=set()
import re
V="aeiouy"
def variants(w):
    out=set()
    for i in range(len(w)):
        out.add(w[:i]+w[i+1:])                 # delete
        out.add(w[:i]+w[i]+w[i:])              # double
    for i in range(len(w)-1):
        out.add(w[:i]+w[i+1]+w[i]+w[i+2:])     # swap
    for i,c in enumerate(w):                   # vowel slip
        if c in V:
            for d in "aeiouy":
                out.add(w[:i]+d+w[i+1:])
    if w.endswith("y"): out |= {w[:-1]+"i", w[:-1]+"ie", w+"y", w+"yy", w[:-1]+"ey"}
    if w.endswith("ed"): out |= {w[:-2]+"d", w[:-2]+"ered"}
    out |= {w+w[-1], w+w[-1]+w[-1]}
    out.discard(w)
    return {v for v in out if len(v)>=3}
res={}; blocked={}
for w in core:
    for v in variants(w):
        if v in words or v in core: blocked.setdefault(w,[]).append(v); continue
        res.setdefault(v,w)
print(len(res))
for w,b in blocked.items(): print(w, sorted(b))
import json; json.dump(res, open("typos.json","w"))

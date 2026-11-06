import json, subprocess, sys, numpy as np
raw, wjson, out_words = sys.argv[1], sys.argv[2], sys.argv[3]
TEMPO = float(sys.argv[4]); SR = 24000
a = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",raw,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout, np.float32)
fr = int(SR*0.01); n = len(a)//fr
rms = np.sqrt((a[:n*fr].reshape(n,fr)**2).mean(1)+1e-12); db = 20*np.log10(rms)
sil = db < -40
runs=[]; i=0
while i<n:
    if sil[i]:
        j=i
        while j<n and sil[j]: j+=1
        if (j-i)*0.01>0.5 and i>0: runs.append((i*0.01,j*0.01))
        i=j
    else: i+=1
KEEP=0.35
segs=[]; cur=0.0; cuts=[]  # cuts: (orig_time, removed_cumulative)
removed=0.0; pieces=[]
for s,e in runs:
    cs, ce = s+KEEP/2, e-KEEP/2
    pieces.append((cur, cs)); cuts.append((cs, ce, removed)); removed += ce-cs; cur=ce
pieces.append((cur, n*0.01))
def m(t):
    r=0.0
    for cs,ce,rem in cuts:
        if t>=ce: r = rem+(ce-cs)
        elif t>cs: r = rem+(t-cs)
    return (t-r)/TEMPO
y = np.concatenate([a[int(p*SR):int(q*SR)] for p,q in pieces])
open("/tmp/claude-trim.f32","wb").write(y.astype(np.float32).tobytes())
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","/tmp/claude-trim.f32","-af",f"atempo={TEMPO}","-ar","44100","-b:a","192k","voix.mp3"],check=True)
W = json.load(open(wjson))["words"]
fix = {}
words=[]
for w in W:
    t = fix.get((w["text"], w["start_ms"]), w["text"])
    words.append({"text":t,"start":round(m(w["start_ms"]/1000),3),"end":round(m(w["end_ms"]/1000),3),"type":"word"})
json.dump({"words":words}, open(out_words,"w"), ensure_ascii=False, indent=0)
print("removed", round(removed,2), "last word end", words[-1]["end"])

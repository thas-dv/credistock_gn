import json, subprocess, sys, numpy as np
raw, wtxt, TEMPO = sys.argv[1], sys.argv[2], float(sys.argv[3])
CUTS = [tuple(map(float, c.split(":"))) for c in sys.argv[4:]]  # explicit cuts in orig time
SR = 24000
a = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",raw,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout, np.float32)
fr = int(SR*0.01); n = len(a)//fr
db = 20*np.log10(np.sqrt((a[:n*fr].reshape(n,fr)**2).mean(1)+1e-12)); sil = db < -40
runs=[]; i=0
while i<n:
    if sil[i]:
        j=i
        while j<n and sil[j]: j+=1
        if (j-i)*0.01>0.4 and i>0: runs.append((i*0.01+0.15, j*0.01-0.15))
        i=j
    else: i+=1
rem = sorted(CUTS + runs)
# merge overlaps
m=[]
for s,e in rem:
    if m and s<=m[-1][1]: m[-1]=(m[-1][0],max(m[-1][1],e))
    else: m.append((s,e))
keep=[]; cur=0.0
for s,e in m: keep.append((cur,s)); cur=e
keep.append((cur,n*0.01))
def mp(t):
    r=0.0
    for s,e in m:
        if t>=e: r+=e-s
        elif t>s: r+=t-s
    return (t-r)/TEMPO
y=np.concatenate([a[int(p*SR):int(q*SR)] for p,q in keep if q>p])
fade=int(0.01*SR)
y.astype(np.float32).tofile("trim.f32")
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","trim.f32","-af",f"atempo={TEMPO}","-ar","44100","-b:a","192k","voix.mp3"],check=True)
words=[]
for line in open(wtxt, encoding="utf-8"):
    p=line.rstrip("\n").rsplit(" ",2)
    if len(p)<3: continue
    words.append({"text":p[0],"start":round(mp(int(p[1])/1000),3),"end":round(mp(int(p[2])/1000),3),"type":"word"})
json.dump({"words":words}, open("words.json","w"), ensure_ascii=False, indent=0)
print("removed",round(sum(e-s for s,e in m),2),"last end",words[-1]["end"], "dur", len(y)/SR/TEMPO)

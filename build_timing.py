"""story.json + words.json (transcription horodatée ElevenLabs) -> timing_voix.json pour le rendu.
Usage : python3 build_timing.py story.json words.json"""
import json, re, sys

story = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "story.json"))
raw = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "words.json"))
raw = raw["words"] if isinstance(raw, dict) else raw
W = [w for w in raw if w.get("type", "word") == "word" and not w["text"].startswith("[")]

def core(s):
    return "".join(ch for ch in s.lower() if ch.isalnum() or ch in "éèàùêâîôûçëïü")

# fusion de la ponctuation isolée avec le mot précédent
words = []
for w in W:
    t = w["text"].strip()
    if not t: continue
    if not core(t) and words:
        if t == "«":
            words.append({"text": "«", "start": w["start"], "end": w["end"], "glue": True}); continue
        words[-1]["text"] += ("" if t in "».," else " ") + t
        words[-1]["end"] = max(words[-1]["end"], w["end"]); continue
    w = dict(w)
    if words and words[-1].get("glue"):
        g = words.pop(); w["text"] = "« " + w["text"]; w["start"] = g["start"]
    words.append(w)

def T(spec):
    word, nth = (spec, 1) if isinstance(spec, str) else (spec[0], spec[1] if len(spec) > 1 else 1)
    c = core(word); k = 0
    for w in words:
        if core(w["text"]) == c:
            k += 1
            if k == nth: return w["start"]
    k = 0
    for w in words:  # repli : début de mot
        if core(w["text"]).startswith(c):
            k += 1
            if k == nth: return w["start"]
    raise SystemExit(f"Mot introuvable dans la transcription : {word!r} (occurrence {nth})")

# sous-titres : coupe aux ponctuations fortes, > 26 caractères ou pause > 0,35 s
subs, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    txt = " ".join(x["text"] for x in cur)
    nxt = words[i + 1] if i + 1 < len(words) else None
    if re.search(r"[.?!…:]$", w["text"]) or len(txt) > 26 or nxt is None or (nxt["start"] - w["end"] > 0.35):
        subs.append({"start": cur[0]["start"], "end": w["end"] + 0.15, "text": txt}); cur = []
for i in range(len(subs) - 1):
    subs[i]["end"] = min(max(subs[i]["end"], subs[i]["start"] + 0.45), subs[i + 1]["start"])
for s in subs: s["text"] = s["text"].replace("« ", "« ").replace("»", " »").replace("  »", " »")

end = words[-1]["end"] + 1.3
starts = [0.0] + [max(0.0, T(s["at"]) - 0.15) for s in story["scenes"][1:]]
scenes = [{"type": s["type"], "start": a, "end": b} for s, a, b in zip(story["scenes"], starts, starts[1:] + [end])]
K = {r: T(spec) for r, spec in story["roles"].items()}
K["end"] = end
out = {"duration": end, "scenes": scenes, "subs": subs, "K": K,
       "words3d": [[txt, T(spec)] for txt, spec in story["words3d"]],
       "q_pulses": [T(s) for s in story.get("q_pulses", [])],
       "punches": [T(s) for s in story.get("punches", [])],
       "keywords": story.get("keywords", []),
       "question": story["question"]}
json.dump(out, open("timing_voix.json", "w"), ensure_ascii=False, indent=1)
for s in subs: print(f'{s["start"]:6.2f}-{s["end"]:6.2f}  {s["text"]}')
print("scènes :", [(s["type"], round(s["start"], 2)) for s in scenes], "fin", round(end, 2))

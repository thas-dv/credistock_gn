# -*- coding: utf-8 -*-
"""Style « MANGA CARTES » Mindset 24 (14/11/2026) — d'après la vidéo d'exemple de l'utilisateur :
fond bleu nuit uni, illustrations manga du héros (bibliothèque de poses manga/*.jpg, générées par l'utilisateur sur Gemini),
cartes arrondies à bord lumineux qui apparaissent avec un rebond, légendes en gras, pastilles, loupes rondes, jauge,
sous-titres karaoké. Héros générique (jamais la ressemblance d'une personne réelle)."""
import json, math, subprocess, sys, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
TJ = json.load(open(sys.argv[1])); OUT = sys.argv[2]
K = TJ["K"]; MK = TJ.get("marks", {}); SCN = TJ["scenes"]; SC = {s["type"]: s["start"] for s in SCN}; END = TJ["duration"]
WORDS = json.load(open("words.json"))["words"]
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
BG = (8, 17, 46); CARDF = (52, 58, 80); EDGE = (232, 236, 245); OR = (255, 132, 30); YEL = (255, 206, 40); RED = (226, 54, 54); WHITE = (255, 255, 255)
_F = {}
def F(sz):
    sz = int(sz)
    if sz not in _F: _F[sz] = ImageFont.truetype(BOLD, sz)
    return _F[sz]
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def eout(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def back(x):   # rebond
    x = min(1, max(0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def since(t, tg): return tg - t
def M(name): return MK.get(name, K.get(name, 1e9))

POSE = {}
for n in "trophee bras courir sac visage banc pointe genoux frappe tete assis croise".split():
    POSE[n] = Image.open(f"manga/{n}.jpg").convert("RGB")

# fond : bleu nuit + léger dégradé + texture de papier fixe
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
base = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32)
base *= (1.15 - 0.35 * (((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2))[..., None]
base += np.random.default_rng(2).normal(0, 3.5, (H, W, 1)).astype(np.float32)
BASE = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")

def cover(img, w, h, zoom=1.0, fx=0.5, fy=0.5):
    """recadre l'image pour remplir w x h (zoom > 1 = plus serré), centré sur (fx, fy) en proportion"""
    iw, ih = img.size; s = max(w / iw, h / ih) * zoom
    nw, nh = int(iw * s + 0.5), int(ih * s + 0.5)
    r = img.resize((nw, nh), Image.BILINEAR)
    x0 = int(min(max(fx * nw - w / 2, 0), nw - w)); y0 = int(min(max(fy * nh - h / 2, 0), nh - h))
    return r.crop((x0, y0, x0 + w, y0 + h))

def full(img, name, zoom=1.0, fx=0.5, fy=0.5, alpha=1.0):
    L = cover(POSE[name], W, H, zoom, fx, fy).convert("RGBA")
    if alpha < 1: L.putalpha(int(255 * alpha))
    img.alpha_composite(L)

def shade(img, a):
    img.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, a)))

def flashw(img, a):
    img.alpha_composite(Image.new("RGBA", img.size, (255, 245, 225, a)))

def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

def card(img, name, cx, cy, w, h, k, zoom=1.0, fx=0.5, fy=0.5, edge=EDGE, num=None, glow=True, dim=0.0):
    """carte arrondie à bord lumineux contenant une pose ; k = temps depuis l'apparition"""
    if k < 0: return
    sc = 0.6 + 0.4 * back(k / 0.38); a = ease(k / 0.18)
    w2, h2 = max(10, int(w * sc)), max(10, int(h * sc))
    inner = cover(POSE[name], w2, h2, zoom * (1 + 0.04 * min(1, k / 6)), fx, fy)
    if dim: inner = Image.blend(inner, Image.new("RGB", inner.size, (0, 0, 0)), dim)
    L = Image.new("RGBA", (w2 + 80, h2 + 80), (0, 0, 0, 0))
    if glow:
        g = Image.new("RGBA", L.size, (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle((34, 34, w2 + 46, h2 + 46), 38, outline=edge + (150,), width=14)
        L.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(L).rounded_rectangle((38, 38, w2 + 42, h2 + 42), 34, fill=CARDF + (255,))
    L.paste(inner, (40, 40), rmask(w2, h2, 30))
    ImageDraw.Draw(L).rounded_rectangle((38, 38, w2 + 42, h2 + 42), 34, outline=edge + (255,), width=5)
    if num is not None:
        d = ImageDraw.Draw(L); d.ellipse((60, 60, 136, 136), fill=(20, 24, 36, 230), outline=EDGE + (255,), width=4)
        d.text((98, 98), str(num), font=F(44), fill=WHITE, anchor="mm")
    if a < 1: L.putalpha(Image.eval(L.getchannel("A"), lambda v: int(v * a)))
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def text(img, s, cx, cy, size, col=WHITE, k=1.0, maxw=1000, stroke=0, pop=True, alpha=1.0):
    if k < 0: return
    while F(size).getlength(s) > maxw and size > 30: size -= 4
    sc = (0.7 + 0.3 * back(k / 0.3)) if pop else 1.0
    size2 = max(8, int(size * sc)); f = F(size2)
    L = Image.new("RGBA", (W, int(size2 * 1.6) + 2 * stroke + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.text((W / 2, L.height / 2), s, font=f, fill=col + (255,), anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    a = ease(k / 0.15) * alpha
    if a < 1: L.putalpha(Image.eval(L.getchannel("A"), lambda v: int(v * a)))
    img.alpha_composite(L, (int(cx - W / 2), int(cy - L.height / 2)))

def chip(img, s, cx, cy, k, size=46, fill=OR, col=(15, 15, 20)):
    if k < 0: return
    sc = 0.5 + 0.5 * back(k / 0.3); f = F(size * sc); tw = f.getlength(s)
    L = Image.new("RGBA", (int(tw + 70), int(size * sc * 1.9)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, L.width - 1, L.height - 1), L.height // 2, fill=fill + (255,))
    d.text((L.width / 2, L.height / 2), s, font=f, fill=col, anchor="mm")
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def stamp(img, s, cx, cy, k, size=86, col=RED, ang=-8):
    if k < 0: return
    sc = 1 + 1.2 * (1 - eout(k / 0.16)); f = F(size); tw = f.getlength(s)
    L = Image.new("RGBA", (int(tw + 80), int(size * 1.8)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((6, 6, L.width - 7, L.height - 7), 18, outline=col + (255,), width=10)
    d.text((L.width / 2, L.height / 2), s, font=f, fill=col + (255,), anchor="mm")
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC)
    L = L.resize((int(L.width * sc), int(L.height * sc)), Image.BILINEAR)
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def inset(img, name, cx, cy, r, k, zoom=2.4, fx=0.5, fy=0.3):
    """loupe ronde (comme les zooms de la vidéo d'exemple)"""
    if k < 0: return
    sc = back(k / 0.35); r2 = max(4, int(r * sc))
    inner = cover(POSE[name], 2 * r2, 2 * r2, zoom, fx, fy)
    L = Image.new("RGBA", (2 * r2 + 24, 2 * r2 + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    m = Image.new("L", (2 * r2, 2 * r2), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r2 - 1, 2 * r2 - 1), fill=255)
    L.paste(inner, (12, 12), m); d.ellipse((10, 10, 2 * r2 + 13, 2 * r2 + 13), outline=EDGE + (255,), width=6)
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def ring(img, cx, cy, r, u, col=OR):
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(60, 66, 90), width=22)
    d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * u, fill=col, width=22)

def speed(img, tg, k, n=40, col=(255, 255, 255)):
    d = ImageDraw.Draw(img); rng = np.random.default_rng(int(tg * 10))
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi); r1 = rng.uniform(380, 700); r2 = r1 + rng.uniform(150, 420)
        d.line((W / 2 + math.cos(a) * r1, H * 0.45 + math.sin(a) * r1, W / 2 + math.cos(a) * r2, H * 0.45 + math.sin(a) * r2), fill=col + (int(200 * (1 - min(1, k / 2.3))),), width=5)

def banner(img, tg):
    k = since(K.get("hook", 0) + 0.3, tg)
    if k < 0 or tg > SC["intro"] + 2.2: return
    a = 1.0 if tg < SC["intro"] + 1.8 else 1 - (tg - SC["intro"] - 1.8) / 0.4
    L = Image.new("RGBA", (W, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((150, 20, W - 150, 150), 26, fill=(20, 24, 40, 235), outline=OR + (255,), width=4)
    d.text((W / 2, 64), "ILS ONT FAILLI ABANDONNER", font=F(46), fill=WHITE, anchor="mm")
    d.text((W / 2, 115), "ÉPISODE 10", font=F(40), fill=OR, anchor="mm")
    y = int(70 - 160 * (1 - eout(k / 0.4)))
    if a < 1: L.putalpha(Image.eval(L.getchannel("A"), lambda v: int(v * max(0, a))))
    img.alpha_composite(L, (0, y))

# sous-titres karaoké (2–3 mots)
CH = []; cur = []
for w in WORDS:
    cur.append(w)
    if len(cur) == 3 or w["text"][-1] in ".?!,:…": CH.append(cur); cur = []
if cur: CH.append(cur)
def karaoke(img, tg):
    if K["q_line1"] - 0.1 <= tg or tg >= SC["logo"]: return
    for ch in CH:
        if ch[0]["start"] - 0.02 <= tg < ch[-1]["end"] + 0.1: break
    else: return
    ws = [w["text"].upper() for w in ch]; size = 70
    while sum(F(size).getlength(x) for x in ws) + 24 * (len(ws) - 1) > 960: size -= 4
    f = F(size); tw = sum(f.getlength(x) for x in ws) + 24 * (len(ws) - 1)
    L = Image.new("RGBA", (W, int(size * 1.7)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x = (W - tw) / 2
    for w, s in zip(ch, ws):
        on = w["start"] <= tg < w["end"] + 0.05
        d.text((x, size * 0.25), s, font=f, fill=(YEL if on else WHITE) + (255,), stroke_width=8, stroke_fill=(0, 0, 0, 255))
        x += f.getlength(s) + 24
    img.alpha_composite(L, (0, int(H * 0.835)))

# ------------------------------------------------------------------ scènes
def s_hook(img, tg, k):
    full(img, "assis", 1.0 + 0.05 * k / 8, 0.5, 0.55)
    shade(img, 70)
    text(img, "PAS LE", W / 2, 360, 110, WHITE, k + 0.2, stroke=8)
    text(img, "NIVEAU ?", W / 2, 490, 150, OR, k + 0.1, stroke=9)
    chip(img, "21 ANS", W / 2 - 200, 650, since(M("d21"), tg), 58)
    chip(img, "3e DIVISION", W / 2 + 170, 650, since(M("d3"), tg), 58, fill=WHITE)

def s_intro(img, tg, k):
    card(img, "croise", W / 2, 860, 640, 1000, k, 1.05, 0.5, 0.45)
    text(img, "L'HISTOIRE VRAIE", W / 2, 1430, 72, WHITE, k - 0.2)
    text(img, "d'un attaquant que personne n'attendait", W / 2, 1515, 44, OR, k - 0.4, pop=False)

def mountains(img, cx, cy, k):
    if k < 0: return
    L = Image.new("RGBA", (360, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse((0, 0, 359, 359), fill=(40, 48, 74, 255), outline=EDGE + (255,), width=6)
    d.polygon([(40, 280), (150, 110), (260, 280)], fill=(200, 206, 220)); d.polygon([(150, 110), (120, 160), (180, 160)], fill=WHITE)
    d.polygon([(150, 280), (240, 150), (330, 280)], fill=(150, 158, 178)); d.polygon([(240, 150), (215, 190), (265, 190)], fill=WHITE)
    for x in (90, 200, 290): d.polygon([(x, 300), (x - 16, 330), (x + 16, 330)], fill=(30, 70, 50))
    sc = back(k / 0.35); L = L.resize((max(4, int(360 * sc)), max(4, int(360 * sc))))
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def s_village(img, tg, k):
    card(img, "courir", W / 2 - 60, 860, 700, 1000, k, 1.0, 0.55, 0.5)
    mountains(img, W - 230, 470, k - 0.6)
    text(img, "UN VILLAGE AU PIED DES ALPES", W / 2, 1450, 60, WHITE, k - 0.3)

def s_formation(img, tg, k):
    ke = since(M("entraineur"), tg)
    card(img, "croise", W / 2, 820, 620, 900, k, 1.15, 0.5, 0.35, num=13, edge=(RED if ke > 0.3 else EDGE))
    text(img, "13 ANS · CENTRE DE FORMATION", W / 2, 1360, 54, WHITE, k - 0.2)
    if ke > 0: stamp(img, "PAS LE NIVEAU", W / 2, 840, since(M("niveau2"), tg), 92)
    if ke > 0: text(img, "« pas le niveau pour l'élite »", W / 2, 1440, 46, OR, ke - 0.2, pop=False)

def s_pret(img, tg, k):
    card(img, "sac", W / 2, 820, 640, 960, k, 1.0, 0.5, 0.45)
    chip(img, "PRÊTÉ", W / 2 - 220, 300, since(M("pret"), tg), 52)
    chip(img, "3e DIVISION", W / 2 + 150, 300, since(M("troisieme2"), tg), 52, fill=WHITE)
    text(img, "LOIN DES GRANDS STADES", W / 2, 1390, 62, WHITE, since(M("loin"), tg))

def s_doute(img, tg, k):
    full(img, "banc", 1.02 + 0.03 * k, 0.5, 0.55)
    shade(img, 110)
    text(img, "TROP TARD ?", W / 2, 420, 120, (210, 214, 226), since(M("tard"), tg) + 0.1, stroke=6)

def s_cri(img, tg, k):
    z = 1.25 - 0.18 * eout(k / 0.6)
    full(img, "genoux", z, 0.5, 0.36)
    shade(img, 40)
    speed(img, tg, k)
    if k < 0.25: flashw(img, int(230 * (1 - k / 0.25)))
    text(img, "IL VA MARQUER", W / 2, 230, 118, WHITE, since(M("marquer"), tg) + 0.15, stroke=9)
    text(img, "JUSQU'À CE QU'ON", W / 2, 350, 80, WHITE, since(M("marquer"), tg) - 0.1, stroke=8)
    text(img, "LE REGARDE !", W / 2, 465, 118, OR, since(M("regarde"), tg), stroke=9)

def counter(img, v, cx, cy, size, label, k, col=OR):
    if k < 0: return
    text(img, str(v), cx, cy, size, col, k, maxw=480)
    text(img, label, cx, cy + size * 0.75, 44, WHITE, k - 0.1, maxw=480, pop=False)

def s_buts(img, tg, k):
    kt = since(M("tours"), tg)
    if kt < 0:
        card(img, "frappe", W / 2, 800, 680, 1000, k, 1.0, 0.55, 0.45)
        n = int(14 * eout(since(M("b14"), tg) / 0.9)); counter(img, n, W / 2, 1420, 150, "BUTS · 3e DIVISION", since(M("b14"), tg))
    else:
        card(img, "frappe", W / 2 - 250, 760, 440, 700, 9, 1.05, 0.55, 0.45, edge=(140, 146, 160))
        card(img, "tete", W / 2 + 250, 760, 440, 700, kt, 1.05, 0.55, 0.4, edge=OR)
        text(img, "VS", W / 2, 760, 64, WHITE, kt, maxw=200)
        counter(img, 14, W / 2 - 250, 1220, 110, "3e DIVISION", 9)
        n = int(21 * eout(since(M("b21"), tg) / 0.9)); counter(img, n, W / 2 + 250, 1220, 110, "2e DIVISION", since(M("b21"), tg))
        chip(img, "MEILLEUR BUTEUR", W / 2 + 200, 1420, since(M("meilleur1"), tg), 44)

def s_montpellier(img, tg, k):
    card(img, "tete", W / 2, 800, 660, 980, k, 1.0, 0.55, 0.42, num=23)
    text(img, "2 ANS PLUS TARD", W / 2, 1380, 50, (190, 196, 210), since(M("plustard"), tg), pop=False)
    text(img, "CHAMPION DE FRANCE", W / 2, 1460, 70, WHITE, since(M("champion"), tg))
    chip(img, "MEILLEUR BUTEUR", W / 2, 1570, since(M("meilleur2"), tg), 48)

def s_monde(img, tg, k):
    full(img, "bras", 1.12 - 0.08 * eout(k / 1.5), 0.5, 0.4)
    shade(img, 40)
    text(img, "2018", W / 2, 300, 150, OR, since(M("y2018"), tg), stroke=8)
    text(img, "CHAMPION DU MONDE", W / 2, 440, 84, WHITE, since(M("monde"), tg), stroke=7)

def s_record(img, tg, k):
    card(img, "trophee", W / 2, 780, 640, 980, k, 1.0, 0.5, 0.4, edge=YEL)
    text(img, "MEILLEUR BUTEUR", W / 2, 1360, 66, YEL, since(M("meilleur3"), tg))
    text(img, "DE L'HISTOIRE DE SON PAYS", W / 2, 1440, 52, WHITE, since(M("meilleur3"), tg) - 0.2)
    chip(img, "RECORD GARDÉ + DE 3 ANS", W / 2, 1560, since(M("record"), tg), 44, fill=WHITE)

def s_regard(img, tg, k):
    full(img, "visage", 1.15 - 0.1 * eout(k / 2.5), 0.5, 0.42)
    kp = since(M("pasniv"), tg)
    text(img, "PAS LE NIVEAU ?", W / 2, 260, 96, WHITE, kp, stroke=7)
    if since(M("entre"), tg) > 0:
        u = eout(since(M("entre"), tg) / 0.3); d = ImageDraw.Draw(img)
        d.line((150, 262, 150 + (W - 300) * u, 262), fill=RED + (255,), width=16)
        text(img, "ENTRÉ DANS L'HISTOIRE", W / 2, 400, 72, OR, since(M("entre"), tg) - 0.1, stroke=7)

def s_you(img, tg, k):
    full(img, "pointe", 1.0 + 0.12 * eout(k / 2.8), 0.5, 0.35)
    text(img, "ET TOI ?", W / 2, 300, 140, OR, k, stroke=9)
    text(img, "QUI DÉCIDE DE TON NIVEAU ?", W / 2, 440, 64, WHITE, since(M("laisser"), tg), stroke=6)

def s_abonne(img, tg, k):
    card(img, "croise", W / 2, 1020, 480, 720, k + 0.3, 1.1, 0.5, 0.35, edge=OR)
    sc = back(k / 0.35) + 0.03 * math.sin(tg * 8)
    L = Image.new("RGBA", (700, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, 699, 189), 50, fill=RED + (255,)); d.text((350, 95), "+  ABONNE-TOI", font=F(84), fill=WHITE, anchor="mm")
    L = L.resize((max(4, int(700 * sc)), max(4, int(190 * sc)))); img.alpha_composite(L, (int(W / 2 - L.width / 2), int(330 - L.height / 2)))
    text(img, "DEMAIN · NOUVEL ÉPISODE", W / 2, 520, 62, OR, since(M("demain"), tg))
    text(img, "Une autre histoire vraie", W / 2, 1480, 52, WHITE, since(M("demain"), tg) - 0.4, pop=False)

def s_question(img, tg, k):
    u = ((tg * 0.9) % 1.0); v = 1 + int(tg * 2.2) % 10
    ring(img, W / 2, 1000, 260, v / 10)
    text(img, f"{v}/10", W / 2, 1000, 150, WHITE, 1, pop=False)
    text(img, "SUR 10,", W / 2, 360, 90, WHITE, since(K["q_line1"], tg), stroke=6)
    text(img, "TON NIVEAU EST À COMBIEN ?", W / 2, 480, 72, OR, since(K["q_line2"], tg), stroke=6)
    kc = since(K["q_cta"] - 0.2, tg)
    if kc > 0:
        L = Image.new("RGBA", (720, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle((0, 0, 719, 129), 40, fill=OR + (255,)); d.text((360, 65), "ÉCRIS TON CHIFFRE 👇".replace(" 👇", ""), font=F(62), fill=(15, 15, 20), anchor="mm")
        img.alpha_composite(L, (int(W / 2 - 360), int(1440 + 10 * math.sin(tg * 9))))

def s_logo(img, tg, k):
    fade = 1 - ease((tg - (END - 0.7)) / 0.7)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    sc = 1 + 0.15 * (1 - eout(k / 0.5)); g = tuple(int(c * fade) for c in (240, 190, 70))
    dl.text((W / 2, 690), "MINDSET", font=F(150 * sc), fill=g + (255,), anchor="mm")
    dl.text((W / 2, 900), "24", font=F(300 * sc), fill=g + (255,), anchor="mm")
    gl = L.filter(ImageFilter.GaussianBlur(26)); img.alpha_composite(gl); img.alpha_composite(gl); img.alpha_composite(L)
    text(img, "Change ton mental.", W / 2, 1180, 64, WHITE, since(K["slogan1"], tg), pop=False, alpha=fade)
    text(img, "Change ta vie.", W / 2, 1270, 64, WHITE, since(K["slogan2"], tg), pop=False, alpha=fade)

SCENES = dict(hook=s_hook, intro=s_intro, village=s_village, formation=s_formation, pret=s_pret, doute=s_doute, cri=s_cri, buts=s_buts,
              montpellier=s_montpellier, monde=s_monde, record=s_record, regard=s_regard, you=s_you, abonne=s_abonne, question=s_question, logo=s_logo)

def render(tg, i):
    img = BASE.copy(); s = SCN[i]
    SCENES[s["type"]](img, tg, tg - s["start"])
    return img

def main():
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    t_from = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0; t_to = float(sys.argv[4]) if len(sys.argv) > 4 else END
    XF = 0.25; t0 = time.time()
    for n, fi in enumerate(range(int(t_from * FPS), int(math.ceil(t_to * FPS)))):
        tg = fi / FPS
        cur = max(i for i, s in enumerate(SCN) if s["start"] <= tg + 1e-6)
        img = render(tg, cur); lt = tg - SCN[cur]["start"]
        if cur > 0 and lt < XF and SCN[cur]["type"] != "cri":
            img = Image.blend(render(tg, cur - 1), img, ease(lt / XF))
        banner(img, tg); karaoke(img, tg)
        # léger mouvement de caméra (dérive) + secousse au cri
        a = np.asarray(img.convert("RGB"))
        kc = tg - SC["cri"]; sh = 14 * math.exp(-kc * 3) if 0 <= kc < 1.5 else 0
        z = 1.0 + 0.012 * math.sin(tg * 0.6)
        Mx = cv2.getRotationMatrix2D((W / 2, H / 2), 0.25 * math.sin(tg * 0.4) + (0.6 * math.sin(tg * 40) * sh / 14), z)
        Mx[0, 2] += sh * math.sin(tg * 63); Mx[1, 2] += sh * math.sin(tg * 51)
        a = cv2.warpAffine(a, Mx, (W, H), borderMode=cv2.BORDER_REFLECT)
        ff.stdin.write(a.tobytes())
        if n % 90 == 0: print(f"t={tg:.1f}s {time.time() - t0:.0f}s", flush=True)
    ff.stdin.close(); ff.wait()

main()

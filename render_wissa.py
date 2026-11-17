# -*- coding: utf-8 -*-
"""Style « MANGA CARTES 3 » (17/11/2026, ép. 12 Wissa : banlieue au crépuscule, tours aux fenêtres allumées, projecteurs, ballon de rugby, échelle des divisions qu’on GRAVIT) — dérivé du style MANGA CARTES (14/11/2026) — d'après la vidéo d'exemple de l'utilisateur :
fond bleu nuit uni, illustrations manga du héros (bibliothèque de poses manga/*.jpg, générées par l'utilisateur sur Gemini),
cartes arrondies à bord lumineux qui apparaissent avec un rebond, légendes en gras, pastilles, loupes rondes, jauge,
sous-titres karaoké. Héros générique (jamais la ressemblance d'une personne réelle)."""
import json, math, subprocess, sys, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
TJ = json.load(open(sys.argv[1])); OUT = sys.argv[2]
EP = json.load(open("story.json")).get("episode", 11); K = TJ["K"]; MK = TJ.get("marks", {}); SCN = TJ["scenes"]; SC = {s["type"]: s["start"] for s in SCN}; END = TJ["duration"]
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
    POSE[n] = Image.open(f"perso2/{n}.jpg").convert("RGB")

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
    d.text((W / 2, 115), f"ÉPISODE {EP}", font=F(40), fill=OR, anchor="mm")
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


# ------------------------------------------------------------------ éléments nouveaux (16/11)
RNG = np.random.default_rng(11); DROPS = RNG.uniform(0, 1, (260, 3))
def rain(img, tg, a=1.0, col=(190, 205, 235)):
    """pluie anglaise : traits obliques qui tombent"""
    d = ImageDraw.Draw(img)
    for x0, y0, sp in DROPS:
        y = ((y0 + tg * (0.9 + 0.8 * sp)) % 1.0) * (H + 200) - 100; x = (x0 * (W + 300) - 150 + y * 0.18) % (W + 100)
        d.line((x, y, x - 14, y + 60 + 40 * sp), fill=col + (int(120 * a * (0.5 + sp / 2)),), width=3)
def cold(img, a=60):
    img.alpha_composite(Image.new("RGBA", img.size, (30, 60, 110, a)))
def warm(img, a=50):
    img.alpha_composite(Image.new("RGBA", img.size, (255, 150, 40, a)))

def route(img, tg, pts):
    """trajet en pointillés entre étapes (pastilles), sans drapeau"""
    d = ImageDraw.Draw(img); prev = None
    for name, x, y, tm, fill in pts:
        k = since(tm, tg)
        if k < 0: break
        if prev:
            u = eout(k / 0.6); px, py = prev
            n = 16
            for i in range(int(n * u)):
                a0 = i / n; a1 = (i + 0.5) / n
                d.line((px + (x - px) * a0, py + (y - py) * a0, px + (x - px) * a1, py + (y - py) * a1), fill=OR + (255,), width=8)
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=fill + (255,), outline=WHITE + (255,), width=4)
        chip(img, name, x, y - 70, k, 44, fill=fill, col=(15, 15, 20) if fill != (52, 58, 80) else WHITE)
        prev = (x, y)

def ladder(img, tg, cx, cy, hi, k):
    """échelle des divisions : la marche 'hi' brille"""
    if k < 0: return
    labs = ["ÉLITE", "2e", "3e", "4e", "5e", "6e", "7e"]
    for i, s in enumerate(labs):
        kk = k - 0.05 * i
        if kk < 0: continue
        y = cy - 330 + i * 110; w = 300 + i * 40
        on = (s == hi)
        L = Image.new("RGBA", (w, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle((0, 0, w - 1, 89), 22, fill=((OR if on else (40, 46, 68)) + (255,)), outline=EDGE + (255,), width=3)
        d.text((w / 2, 45), s + (" DIVISION" if s not in ("ÉLITE",) else ""), font=F(40), fill=((15, 15, 20) if on else (200, 205, 220)), anchor="mm")
        img.alpha_composite(L, (int(cx - w / 2 + (1 - eout(kk / 0.3)) * 300), int(y - 45)))

def xcross(img, cx, cy, k, s=90):
    if k < 0: return
    u = eout(k / 0.25); d = ImageDraw.Draw(img)
    d.line((cx - s, cy - s, cx - s + 2 * s * u, cy - s + 2 * s * u), fill=RED + (255,), width=22)
    if k > 0.12:
        u2 = eout((k - 0.12) / 0.25); d.line((cx + s, cy - s, cx + s - 2 * s * u2, cy - s + 2 * s * u2), fill=RED + (255,), width=22)

# ------------------------------------------------------------------ éléments nouveaux (17/11) : banlieue au crépuscule, projecteurs, rugby, ascension
_R = np.random.default_rng(17)
TOWERS = []
x = -40
while x < W + 40:
    w = int(_R.uniform(110, 210)); h = int(_R.uniform(260, 620)); TOWERS.append((x, w, h, _R.uniform(0, 1, (40, 12)))); x += w + int(_R.uniform(-10, 30))
def skyline(img, tg, light=0.6, gold=0.0, y0=H):
    """tours de banlieue en contre-jour avec fenêtres allumées (ciel dégradé crépuscule -> doré)"""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    top = (int(30 + 200 * gold), int(40 + 120 * gold), int(90 - 40 * gold)); bot = (int(150 + 100 * gold), int(70 + 120 * gold), int(80 - 20 * gold))
    for i in range(0, 700, 10):
        u = i / 700; c = tuple(int(top[j] * (1 - u) + bot[j] * u) for j in range(3))
        d.rectangle((0, y0 - 700 + i, W, y0 - 690 + i), fill=c + (int(150 * light),))
    for x, w, h, win in TOWERS:
        d.rectangle((x, y0 - h, x + w, y0), fill=(10, 14, 30, 255))
        for r in range(min(40, h // 34)):
            for c in range(max(1, w // 34)):
                if win[r % 40, c % 12] < light * 0.75:
                    fl = 0.85 + 0.15 * math.sin(tg * 2 + r * 3 + c)
                    d.rectangle((x + 12 + c * 32, y0 - h + 18 + r * 34, x + 30 + c * 32, y0 - h + 38 + r * 34), fill=(int(255 * fl), int(200 * fl), 90, 230))
    img.alpha_composite(L)

def beams(img, u, tg):
    """projecteurs de stade qui s'allument (u = 0..1)"""
    if u <= 0: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for cx, ang in ((90, 0.35), (W - 90, -0.35)):
        tip = (cx, 120); a = ang + 0.05 * math.sin(tg * 1.3)
        p1 = (cx + math.sin(a - 0.22) * 2200, 120 + math.cos(a - 0.22) * 2200); p2 = (cx + math.sin(a + 0.22) * 2200, 120 + math.cos(a + 0.22) * 2200)
        d.polygon([tip, p1, p2], fill=(255, 245, 200, int(70 * u)))
        d.ellipse((cx - 60, 60, cx + 60, 180), fill=(255, 250, 220, int(255 * u)))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(18)))

def rugby_ball(img, cx, cy, k, s=1.0, ang=-25):
    if k < 0: return
    sc = back(k / 0.35) * s
    L = Image.new("RGBA", (260, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse((10, 10, 250, 160), fill=(170, 100, 50, 255), outline=(30, 20, 10, 255), width=6)
    d.line((70, 85, 190, 85), fill=WHITE + (255,), width=6)
    for i in range(5): xx = 95 + i * 18; d.line((xx, 72, xx, 98), fill=WHITE + (255,), width=5)
    L = L.rotate(ang + 8 * math.sin(k * 3), expand=True, resample=Image.BICUBIC)
    L = L.resize((max(4, int(L.width * sc)), max(4, int(L.height * sc))))
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def soccer_ball(img, cx, cy, k, r=80):
    if k < 0: return
    r2 = int(r * back(k / 0.35)); d = ImageDraw.Draw(img)
    d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), fill=WHITE + (255,), outline=(20, 20, 20, 255), width=6)
    pts = [(cx + 0.38 * r2 * math.cos(math.radians(90 + 72 * i)), cy - 0.38 * r2 * math.sin(math.radians(90 + 72 * i))) for i in range(5)]
    d.polygon(pts, fill=(20, 20, 20, 255))

def climb(img, tg, cx, cy, steps, k):
    """échelle des divisions qu'il GRAVIT : steps = [(label, temps)] ; le marqueur monte à chaque étape"""
    if k < 0: return
    labs = ["ÉLITE", "2e", "3e", "4e", "5e"]
    cur = None
    for lab, tm in steps:
        if tg >= tm: cur = lab
    for i, s in enumerate(labs):
        kk = k - 0.05 * i
        if kk < 0: continue
        y = cy - 260 + i * 120; w = 300 + i * 50; on = (s == cur)
        L = Image.new("RGBA", (w, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle((0, 0, w - 1, 95), 24, fill=((OR if on else (40, 46, 68)) + (255,)), outline=EDGE + (255,), width=3)
        d.text((w / 2, 48), s + (" DIVISION" if s != "ÉLITE" else ""), font=F(42), fill=((15, 15, 20) if on else (200, 205, 220)), anchor="mm")
        img.alpha_composite(L, (int(cx - w / 2 + (1 - eout(kk / 0.3)) * 300), int(y - 48)))
    if cur:
        i = labs.index(cur); tm = [t for l, t in steps if l == cur][-1]; prev = [l for l, t in steps if t < tm]
        i0 = labs.index(prev[-1]) if prev else i; u = eout((tg - tm) / 0.5)
        y = cy - 260 + (i0 + (i - i0) * u) * 120; w = 300 + i * 50
        soccer_ball(img, int(cx + w / 2 + 70), int(y), 1, 40)

# ------------------------------------------------------------------ scènes (ép. 12 : Yoane Wissa)
def s_hook(img, tg, k):
    skyline(img, tg, 0.7, 0.0)
    full(img, "assis", 1.0 + 0.05 * k / 6, 0.5, 0.5, alpha=0.88)
    shade(img, 70)
    text(img, "ENCORE CHEZ", W / 2, 360, 104, WHITE, k + 0.25, stroke=8)
    text(img, "LES AMATEURS", W / 2, 480, 104, WHITE, since(M("hook") if "hook" in MK else K["hook"], tg) + 0.2, stroke=8)
    text(img, "À 18 ANS ?", W / 2, 630, 150, OR, since(M("a18"), tg), stroke=9)
    stamp(img, "TROP TARD ?", W / 2, 1300, since(M("tard"), tg), 96)

def s_intro(img, tg, k):
    skyline(img, tg, 0.5, 0.0)
    kc = since(M("choisit"), tg)
    text(img, "L'HISTOIRE VRAIE", W / 2, 280, 76, WHITE, k - 0.1)
    text(img, "d'un footballeur, de l'amateur au pro", W / 2, 360, 44, OR, k - 0.3, pop=False)
    if kc < 0:
        card(img, "croise", W / 2, 950, 520, 760, k, 1.05, 0.5, 0.4)
        chip(img, "GARDIEN À 7 ANS", W / 2 - 170, 560, since(M("gardien"), tg), 48, fill=WHITE)
        chip(img, "RUGBY JUSQU'À 15 ANS", W / 2 + 120, 1440, since(M("a15"), tg), 48)
        rugby_ball(img, W / 2 + 330, 1220, since(M("rugby"), tg), 0.9)
    else:
        # le choix : ballon de rugby qui s'éloigne, ballon de foot qui grossit
        rugby_ball(img, W / 2 - 260 - 300 * eout(kc / 0.8), 900, 1, 1.0 - 0.5 * eout(kc / 0.8))
        soccer_ball(img, W / 2 + 120, 900, kc, 170)
        text(img, "IL CHOISIT LE FOOT", W / 2, 1300, 80, OR, kc, stroke=6)

def s_amateurs(img, tg, k):
    skyline(img, tg, 0.45, 0.0); cold(img, 40)
    climb(img, tg, W / 2 - 60, 980, [("5e", M("d5")), ("3e", M("d3"))], k)
    chip(img, "ÉQUIPE RÉSERVE", W / 2, 420, since(M("reserve"), tg), 52, fill=WHITE)
    stamp(img, "AMATEUR", W / 2, 1560, since(M("amateurs2"), tg), 90)

def s_banc(img, tg, k):
    cold(img, 50)
    kp = since(M("prete"), tg)
    card(img, "banc", W / 2, 860, 660, 980, k, 1.0, 0.5, 0.5, edge=(RED if since(M("banc"), tg) > 0 else EDGE), dim=0.35 * min(1, max(0, kp / 0.3)))
    chip(img, "CLUB DE L'ÉLITE", W / 2, 260, since(M("elite1"), tg) + 0.2, 52, fill=WHITE)
    stamp(img, "SUR LE BANC", W / 2, 440, since(M("banc"), tg), 88)
    chip(img, "QUELQUES MINUTES", W / 2, 1420, since(M("bouts"), tg), 50)
    stamp(img, "PRÊTÉ", W / 2, 1580, kp, 100, ang=6)

def counter(img, v, cx, cy, size, label, k, col=OR):
    if k < 0: return
    text(img, str(v), cx, cy, size, col, k, maxw=520)
    text(img, label, cx, cy + size * 0.75, 48, WHITE, k - 0.1, maxw=520, pop=False)

def s_laval(img, tg, k):
    cold(img, 60)
    card(img, "genoux", W / 2, 820, 600, 900, k, 1.0, 0.5, 0.5, dim=0.25)
    chip(img, "2e DIVISION", W / 2, 260, since(M("d2"), tg), 56, fill=WHITE)
    n = int(2 * eout(since(M("deux"), tg) / 0.5)); counter(img, n, W / 2 - 230, 1380, 150, "BUTS", since(M("deux"), tg), col=(210, 214, 226))
    chip(img, "20 ANS", W / 2 + 230, 1400, since(M("a20"), tg), 64)

def s_doute(img, tg, k):
    skyline(img, tg, 0.25, 0.0)
    full(img, "assis", 1.05 + 0.03 * k, 0.5, 0.55, alpha=0.8)
    cold(img, 70); shade(img, 120)
    text(img, "LOIN DES", W / 2, 380, 110, (210, 214, 226), k + 0.1, stroke=6)
    text(img, "PROJECTEURS.", W / 2, 510, 110, WHITE, k - 0.2, stroke=6)

def s_cri(img, tg, k):
    z = 1.25 - 0.18 * eout(k / 0.6)
    full(img, "frappe", z, 0.5, 0.45)
    warm(img, int(55 * eout(k / 0.8)))
    beams(img, eout(k / 0.5), tg)
    speed(img, tg, k)
    if k < 0.25: flashw(img, int(230 * (1 - k / 0.25)))
    text(img, "ALORS IL VA", W / 2, 230, 100, WHITE, k + 0.15, stroke=9)
    text(img, "FAIRE PARLER", W / 2, 350, 100, WHITE, since(M("parler"), tg) + 0.3, stroke=9)
    text(img, "SES BUTS !", W / 2, 1440, 140, OR, since(M("buts_cri"), tg) - 0.05, stroke=10)

def s_montee(img, tg, k):
    skyline(img, tg, 0.6, 0.35 * eout(k / 3))
    beams(img, 0.5, tg)
    climb(img, tg, W / 2 - 60, 960, [("3e", -1), ("2e", M("b10")), ("ÉLITE", M("elite2"))], k)
    n = int(10 * eout(since(M("b10"), tg) / 0.7)); counter(img, n, W / 2, 330, 120, "BUTS EN 2e DIVISION", since(M("b10"), tg))
    chip(img, "CHAMPION !", W / 2, 1560, since(M("champion"), tg), 60, fill=YEL)

def s_angleterre(img, tg, k):
    warm(img, 25)
    k20 = since(M("b20"), tg)
    card(img, "tete" if k20 < 0 else "bras", W / 2, 860, 600, 900, k if k20 < 0 else k20, 1.0, 0.5, 0.42, edge=OR)
    chip(img, "ANGLETERRE · 2021", W / 2, 240, since(M("angl"), tg), 54, fill=WHITE)
    if k20 < 0: counter(img, int(10 * eout(since(M("b10b"), tg) / 0.6)), W / 2, 1400, 140, "BUTS · 1re SAISON", since(M("b10b"), tg))
    else: counter(img, int(10 + 10 * eout(k20 / 0.8)), W / 2, 1400, 160, "BUTS EN UNE SAISON", k20, col=YEL)
    stamp(img, "RECORD DU CLUB", W / 2, 420, since(M("meilleur"), tg), 80, col=YEL, ang=-5)

def s_transfert(img, tg, k):
    warm(img, 35); beams(img, 0.7, tg)
    card(img, "croise", W / 2, 1050, 480, 720, k, 1.05, 0.5, 0.4, edge=YEL)
    km = since(M("m50"), tg)
    n = int(50 * eout(km / 0.9))
    text(img, f"{n} MILLIONS", W / 2, 340, 120, YEL, km, stroke=8)
    text(img, "DE LIVRES", W / 2, 470, 70, WHITE, since(M("livres"), tg), stroke=6)

def s_mondial(img, tg, k):
    full(img, "bras", 1.12 - 0.08 * eout(k / 1.5), 0.5, 0.4)
    warm(img, 35); beams(img, 1.0, tg); shade(img, 25)
    text(img, "JUIN 2026", W / 2, 260, 120, OR, since(M("juin"), tg), stroke=8)
    chip(img, "RD CONGO", W / 2, 390, since(M("rdc"), tg), 56, fill=WHITE)
    kp = since(M("premier"), tg)
    text(img, "1er BUT DE L'HISTOIRE", W / 2, 1360, 80, YEL, kp, stroke=7)
    text(img, "DE SON PAYS EN COUPE DU MONDE", W / 2, 1460, 54, WHITE, kp - 0.3, stroke=5)
    chip(img, "+ 2 BUTS · 1re VICTOIRE", W / 2, 1580, since(M("victoire"), tg), 50)

def s_regard(img, tg, k):
    skyline(img, tg, 0.9, 1.0)
    full(img, "visage", 1.15 - 0.1 * eout(k / 2.5), 0.5, 0.42, alpha=0.9)
    text(img, "AMATEUR À 18 ANS ?", W / 2, 260, 90, WHITE, k, stroke=7)
    kg = since(M("histoire_g"), tg)
    if kg > -0.6:
        u = eout((kg + 0.6) / 0.3); d = ImageDraw.Draw(img)
        d.line((120, 262, 120 + (W - 240) * u, 262), fill=RED + (255,), width=16)
        text(img, "ENTRÉ DANS L'HISTOIRE", W / 2, 400, 74, YEL, kg + 0.4, stroke=7)

def s_you(img, tg, k):
    full(img, "pointe", 1.0 + 0.12 * eout(k / 2.8), 0.5, 0.35)
    text(img, "ET TOI ?", W / 2, 300, 140, OR, k, stroke=9)
    text(img, "TROP TARD ? VRAIMENT ?", W / 2, 440, 66, WHITE, since(M("trop2"), tg), stroke=6)

def s_abonne(img, tg, k):
    skyline(img, tg, 0.6, 0.5)
    card(img, "croise", W / 2, 1020, 480, 720, k + 0.3, 1.1, 0.5, 0.35, edge=OR)
    sc = back(k / 0.35) + 0.03 * math.sin(tg * 8)
    L = Image.new("RGBA", (700, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, 699, 189), 50, fill=RED + (255,)); d.text((350, 95), "+  ABONNE-TOI", font=F(84), fill=WHITE, anchor="mm")
    L = L.resize((max(4, int(700 * sc)), max(4, int(190 * sc)))); img.alpha_composite(L, (int(W / 2 - L.width / 2), int(330 - L.height / 2)))
    text(img, f"DEMAIN · ÉPISODE {EP + 1}", W / 2, 520, 62, OR, since(M("demain"), tg))
    text(img, "Amateur à 21 ans… légende de son pays", W / 2, 1480, 46, WHITE, since(M("legende"), tg) - 1.5, pop=False)

def s_question(img, tg, k):
    v = 1 + int(tg * 2.2) % 10
    ring(img, W / 2, 1000, 260, v / 10)
    text(img, f"{v}/10", W / 2, 1000, 150, WHITE, 1, pop=False)
    text(img, "SUR 10,", W / 2, 330, 90, WHITE, since(K["q_line1"], tg), stroke=6)
    text(img, "TA RAGE DE RÉUSSIR", W / 2, 450, 76, OR, since(K["q_line1"], tg) - 0.2, stroke=6)
    text(img, "EST À COMBIEN ?", W / 2, 550, 72, OR, since(K["q_line2"], tg), stroke=6)
    kc = since(K["q_cta"] - 0.2, tg)
    if kc > 0:
        L = Image.new("RGBA", (720, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle((0, 0, 719, 129), 40, fill=OR + (255,)); d.text((360, 65), "ÉCRIS TON CHIFFRE", font=F(62), fill=(15, 15, 20), anchor="mm")
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

SCENES = dict(hook=s_hook, intro=s_intro, amateurs=s_amateurs, banc=s_banc, laval=s_laval, doute=s_doute, cri=s_cri, montee=s_montee,
              angleterre=s_angleterre, transfert=s_transfert, mondial=s_mondial, regard=s_regard, you=s_you, abonne=s_abonne, question=s_question, logo=s_logo)
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

# -*- coding: utf-8 -*-
"""Style « score » (07/11) : TABLEAU D AFFICHAGE LED de stade — compteurs, score, bandeau défilant (Lookman, épisode 4).
Usage : python3 render_score.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
import json, math, subprocess, sys, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG = (5, 11, 18); NIGHT = (9, 20, 34); PITCH = (12, 52, 34); PITCH2 = (15, 62, 40); LINE = (205, 230, 215)
ORANGE = (255, 138, 22); GREEN = (0, 178, 104); WHITE = (246, 246, 240); RED = (232, 52, 44); GOLD = (246, 192, 60)
GREY = (120, 134, 142); DARK = (32, 44, 54); BLUE = (40, 110, 230); SIL = (10, 12, 16)

TJ = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "timing_voix.json"))
K = TJ["K"]; MK = TJ.get("marks", {}); SCN = TJ["scenes"]
SC = {s["type"]: s["start"] for s in SCN}
END = TJ["duration"]

_F = {}
def F(path, size):
    k = (path, int(size))
    if k not in _F: _F[k] = ImageFont.truetype(path, int(size))
    return _F[k]

def ease(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def eout(x): x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3
def lerp(a, b, u): return a + (b - a) * u
def mix(c1, c2, u): return tuple(int(lerp(a, b, u)) for a, b in zip(c1, c2))

def text(d, xy, s, size, col, font=BOLD, anchor="mm", stroke=0, scol=(0, 0, 0)):
    d.text(xy, s, font=F(font, size), fill=col, anchor=anchor, stroke_width=stroke, stroke_fill=scol)

def fit(s, size, maxw, font=BOLD):
    d = ImageDraw.Draw(Image.new("L", (4, 4)))
    while size > 20 and d.textlength(s, font=F(font, size)) > maxw: size -= 2
    return size

def typew(s, k, cps=26):
    if k <= 0: return ""
    return s[:int(k * cps) + 1]

def stamp(img, s, center, size, angle, k, col=RED, dur=0.14, box=True, font=BOLD):
    if k <= 0: return 0.0
    size = fit(s, size, 900, font)
    f = F(font, size)
    dd = ImageDraw.Draw(Image.new("L", (4, 4)))
    l, t, r, b = dd.textbbox((0, 0), s, font=f)
    pad = int(size * 0.28); w, h = r - l + 2 * pad, b - t + 2 * pad
    L = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    if box: d.rounded_rectangle((10, 10, 10 + w, 10 + h), int(size * 0.12), outline=col + (255,), width=max(4, size // 14))
    d.text((10 + pad - l, 10 + pad - t), s, font=f, fill=col + (255,))
    a = np.asarray(L).copy()
    rng = np.random.default_rng(len(s) * 31 + size)
    a[..., 3] = (a[..., 3] * (rng.random(a.shape[:2]) > 0.1)).astype(np.uint8)
    L = Image.fromarray(a).rotate(angle, resample=Image.BICUBIC, expand=True)
    sc = 1.0 + 0.8 * (1 - eout(k / dur)); al = min(1.0, k / (dur * 0.6))
    if sc != 1.0: L = L.resize((int(L.width * sc), int(L.height * sc)), Image.BICUBIC)
    if al < 1:
        a = np.asarray(L).copy(); a[..., 3] = (a[..., 3] * al).astype(np.uint8); L = Image.fromarray(a)
    img.alpha_composite(L, (int(center[0] - L.width / 2), int(center[1] - L.height / 2)))
    return max(0.0, 1 - k / 0.25)


# =============================================================== STYLE « BD » (06/11) : BANDE DESSINÉE
# Papier tramé, cases qui claquent (bord noir épais, ombre), encadrés jaunes de NARRATEUR (jamais de bulle de parole attribuée


# =============================================================== STYLE « SCORE » (07/11) : TABLEAU D'AFFICHAGE LED
# Tout l'écran est un tableau d'affichage de stade à LED (points lumineux) : compteurs qui défilent (âge, buts, matchs),
# bandeau défilant, score de finale. Aucun nom de club / logo / drapeau / marque à l'écran : notions, âges, années, chiffres.
CELL = 9; CW, CH = W // CELL, -(-H // CELL)           # 120 x 214 « LED »
AMB = (255, 172, 34); RED = (255, 44, 40); GRN = (40, 255, 130); WHT = (236, 240, 255); GOLD = (255, 205, 60); CYAN = (60, 220, 255)
ORANGE = AMB; ACC = AMB
EPISODE = 4
LMONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def M(name, default=99.0): return MK.get(name, default)

# masque des points LED (cellule 9x9, point rond doux)
_c = (np.arange(CELL) - (CELL - 1) / 2)
_r = np.sqrt(_c[None, :] ** 2 + _c[:, None] ** 2)
DOT = np.clip(1.25 - _r / 3.4, 0, 1) ** 1.3
DOTM = np.tile(DOT, (CH, CW))[:H, :W][..., None].astype(np.float32)
OFF = np.array([20, 22, 28], np.float32)

def led(low):
    """low : image RGB CWxCH -> tableau LED plein écran (RGBA)."""
    a = np.asarray(low).astype(np.float32)
    up = cv2.resize(a, (CW * CELL, CH * CELL), interpolation=cv2.INTER_NEAREST)[:H, :W]
    lit = up * DOTM + OFF * DOTM * (1 - np.clip(up.max(2, keepdims=True) / 80, 0, 1))
    glow = cv2.GaussianBlur(up, (0, 0), 9) * 0.55
    out = np.clip(lit + glow + 4, 0, 255).astype(np.uint8)
    return Image.fromarray(out).convert("RGBA")

def scol(c, a): return tuple(int(v * max(0.0, min(1.0, a))) for v in c)

def ltext(d, xy, s, size, col, a=1.0, anchor="mm", font=LMONO, maxw=100):
    if a <= 0 or not s: return
    dd = ImageDraw.Draw(Image.new("L", (4, 4)))
    while size > 6 and dd.textlength(s, font=F(font, size)) > maxw: size -= 1
    d.text(xy, s, font=F(font, size), fill=scol(col, a), anchor=anchor)

def typed(s, k, cps=30): return "" if k <= 0 else s[:int(k * cps) + 1]

def blink(tg, f=3.0): return 1.0 if (tg * f) % 1 < 0.6 else 0.25

def counter(d, cx, cy, val, size, col, k, dur=0.6, start=0, fmt="{}"):
    if k <= 0: return 0.0
    u = eout(k / dur); v = int(round(lerp(start, val, u)))
    ltext(d, (cx, cy), fmt.format(v), size, col)
    return max(0.0, 1 - (k - dur) / 0.25) if k > dur else 0.0

def frame(d, col=(70, 70, 90), y0=14, y1=168):
    d.rectangle((1, y0, CW - 2, y1), outline=col)

def header(d, tg):
    """bandeau de série permanent (rangées 1–11) : ILS ONT FAILLI ABANDONNER · ÉPISODE 4"""
    s = "ILS ONT FAILLI ABANDONNER · ÉPISODE 4 · "
    f = F(LMONO, 9); w = d.textlength(s, font=f)
    x = -((tg * 14) % w)
    d.text((x, 6), s * 4, font=f, fill=scol(AMB, 0.75), anchor="lm")
    d.line((0, 12, CW, 12), fill=(60, 50, 20))

def flash_bar(d, y, s, col, k, size=12, h=20):
    if k <= 0: return 0.0
    a = min(1, k / 0.1)
    d.rectangle((2, y - h // 2, CW - 3, y + h // 2), fill=scol(col, a))
    ltext(d, (CW / 2, y), s, size, (0, 0, 0), a)
    return max(0.0, 1 - k / 0.2)

def xmark(d, cx, cy, r, col, a=1.0):
    d.line((cx - r, cy - r, cx + r, cy + r), fill=scol(col, a), width=3)
    d.line((cx - r, cy + r, cx + r, cy - r), fill=scol(col, a), width=3)

def ball(d, cx, cy, r, col=WHT, a=1.0, rot=0.0):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=scol(col, a), width=2)
    for i in range(5):
        an = rot + i * 2 * math.pi / 5
        d.point((cx + r * 0.45 * math.cos(an), cy + r * 0.45 * math.sin(an)), fill=scol(col, a))
    d.ellipse((cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25), fill=scol(col, a))

def arrow_down(d, cx, cy, s, col, a=1.0):
    d.rectangle((cx - s * 0.3, cy - s, cx + s * 0.3, cy), fill=scol(col, a))
    d.polygon([(cx - s, cy), (cx + s, cy), (cx, cy + s)], fill=scol(col, a))

def cup(d, cx, cy, s, col=GOLD, a=1.0):
    c = scol(col, a)
    d.pieslice((cx - 10 * s, cy - 14 * s, cx + 10 * s, cy + 6 * s), 0, 180, fill=c)
    d.rectangle((cx - 10 * s, cy - 6 * s, cx + 10 * s, cy - 4 * s), fill=c)
    d.arc((cx - 15 * s, cy - 6 * s, cx - 5 * s, cy + 2 * s), 90, 270, fill=c, width=2)
    d.arc((cx + 5 * s, cy - 6 * s, cx + 15 * s, cy + 2 * s), 270, 90, fill=c, width=2)
    d.rectangle((cx - 2 * s, cy + 6 * s, cx + 2 * s, cy + 12 * s), fill=c)
    d.rectangle((cx - 7 * s, cy + 12 * s, cx + 7 * s, cy + 15 * s), fill=c)

def sparkle(d, tg, n=40, col=GOLD, a=1.0, seed=3, y0=14, y1=168):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(2, CW - 2); y = rng.uniform(y0, y1); ph = rng.uniform(0, 6.28); sp = rng.uniform(2, 6)
        b = 0.5 + 0.5 * math.sin(tg * sp + ph)
        if b > 0.55: d.point((x, y), fill=scol(col, a * b))

# ---------------------------------------------------------------- scènes (dessinent sur le tableau basse résolution)
def s_hook(b, d, tg, k):
    hit = 0.0
    ltext(d, (CW / 2, 34), typed("PAS DE", k + 0.1, 40), 22, AMB)
    ltext(d, (CW / 2, 56), typed("CENTRE DE", k - 0.05, 40), 22, AMB)
    ltext(d, (CW / 2, 78), typed("FORMATION ?", k - 0.2, 40), 22, AMB)
    kf = tg - K["hook"] + 0.05
    if kf > 0:
        ltext(d, (CW / 2, 116), "FINI ?", 32, RED, blink(tg, 4))
        hit = max(0.0, 1 - kf / 0.25)
    ki = tg - M("ils") + 0.1
    if ki > 0:
        d.rectangle((0, 14, CW, 168), fill=(0, 0, 0))
        ltext(d, (CW / 2, 50), typed("ILS ONT FAILLI", ki, 34), 15, WHT)
        ltext(d, (CW / 2, 70), typed("ABANDONNER", ki - 0.3, 34), 18, AMB)
        hit = max(hit, 1 - ki / 0.25)
        ke = tg - M("episode") + 0.1
        if ke > 0:
            sz = int(22 + 14 * (1 - eout(ke / 0.18)))
            d.rectangle((8, 92, CW - 9, 128), outline=RED, width=2)
            ltext(d, (CW / 2, 110), "ÉPISODE 4", sz, RED, maxw=92)
            hit = max(hit, 1 - ke / 0.25)
    return dict(hit=hit)

def s_intro(b, d, tg, k):
    hit = 0.0
    ltext(d, (CW / 2, 30), typed("HISTOIRE VRAIE", k, 34), 13, WHT)
    ka = tg - M("amateur") + 0.1
    if ka > 0:
        ltext(d, (CW / 2, 56), "DE L'AMATEUR", 15, AMB, min(1, ka / 0.1))
        kp = tg - M("pro") + 0.1
        if kp > 0:
            ltext(d, (CW / 2, 80), "AU PRO", 24, GRN, min(1, kp / 0.1)); hit = max(hit, 1 - kp / 0.25)
    kn = tg - M("ne") + 0.1
    if kn > 0:
        d.rectangle((8, 100, CW - 9, 156), outline=(80, 80, 100))
        ltext(d, (CW / 2, 114), typed("NÉ À LONDRES", kn, 30), 12, WHT)
        kg = tg - M("nigeria") + 0.15
        if kg > 0: ltext(d, (CW / 2, 138), typed("RACINES : NIGERIA", kg, 30), 12, GRN)
    return dict(hit=hit)

def s_quartier(b, d, tg, k):
    hit = 0.0
    ltext(d, (CW / 2, 26), "CENTRES DE FORMATION", 10, WHT)
    kz = tg - M("prend") + 0.1
    ltext(d, (CW / 2, 52), "0", 30, RED, blink(tg, 3) if kz > 0 else 0.5)
    if kz > 0 and kz < 0.25: hit = 1 - kz / 0.25
    kw = tg - M("waterloo") + 0.1
    if kw > 0:
        # petit terrain de quartier : grillage + buts
        a = min(1, kw / 0.15)
        d.rectangle((10, 76, CW - 11, 126), outline=scol(GRN, a))
        d.line((CW / 2, 76, CW / 2, 126), fill=scol(GRN, a)); d.ellipse((CW / 2 - 8, 93, CW / 2 + 8, 109), outline=scol(GRN, a))
        for x in range(12, CW - 10, 6): d.line((x, 70, x + 4, 76), fill=scol((110, 110, 130), a))
        bx = CW / 2 + 40 * math.sin(tg * 2.2); by = 101 + 16 * math.sin(tg * 3.1)
        ball(d, bx, by, 4, WHT, a, tg * 4)
        kq = tg - M("quartier") + 0.1
        if kq > 0: ltext(d, (CW / 2, 140), typed("CLUB DE QUARTIER", kq, 34), 12, AMB)
    k5 = tg - M("cinq") + 0.1
    if k5 > 0:
        hit = max(hit, counter(d, CW / 2, 158, 5, 13, WHT, k5, 0.5, 0, "{} ANS"))
    return dict(hit=hit)

def s_essai(b, d, tg, k):
    hit = 0.0
    ltext(d, (CW / 2, 26), "ÂGE", 11, WHT)
    hit = max(hit, counter(d, CW / 2, 54, 16, 34, AMB, k + 0.1, 0.45, 10))
    km = tg - M("charlton") + 0.1
    if km > 0:
        # match : deux colonnes de points
        for i in range(5):
            d.ellipse((24 - 2, 88 + i * 9 - 2, 24 + 2, 88 + i * 9 + 2), fill=scol(CYAN, 0.8))
            d.ellipse((CW - 24 - 2, 88 + i * 9 - 2, CW - 24 + 2, 88 + i * 9 + 2), fill=scol((150, 150, 160), 0.6))
        x = lerp(24, CW - 30, (km * 0.8) % 1); ball(d, x, 106, 3, WHT, 1, tg * 6)
        ltext(d, (CW / 2, 80), "IL BRILLE", 12, CYAN, min(1, km / 0.1))
    ke = tg - M("essai") + 0.1
    if ke > 0:
        ltext(d, (CW / 2, 140), "ESSAI", 18, AMB, min(1, ke / 0.1)); hit = max(hit, 1 - ke / 0.25)
    kp = tg - M("place") + 0.1
    if kp > 0:
        hit = max(hit, flash_bar(d, 140, "ACCEPTÉ ✓", GRN, kp, 16, 26))
    return dict(hit=hit)

def s_debut(b, d, tg, k):
    hit = 0.0
    ltext(d, (CW / 2, 26), "ÂGE", 11, WHT)
    hit = max(hit, counter(d, CW / 2, 52, 18, 30, AMB, k + 0.1, 0.4, 16))
    kd = tg - M("division") + 0.1
    if kd > 0: ltext(d, (CW / 2, 80), "1ER MATCH PRO", 13, GRN, min(1, kd / 0.1))
    kg = tg - M("everton") + 0.1
    if kg > 0:
        d.rectangle((0, 14, CW, 168), fill=(0, 0, 0))
        ltext(d, (CW / 2, 34), typed("UN GRAND CLUB", kg, 30), 14, WHT)
        ltext(d, (CW / 2, 52), typed("L'ACHÈTE", kg - 0.2, 30), 14, GOLD)
        kp = tg - M("peu") + 0.1
        if kp > 0:
            ltext(d, (CW / 2, 84), "BUTS EN CHAMPIONNAT", 9, WHT, min(1, kp / 0.1))
            ks = tg - M("seul") + 0.1
            if ks > 0:
                ltext(d, (CW / 2, 116), "1", 44, RED, blink(tg, 3)); hit = max(hit, 1 - ks / 0.25)
    return dict(hit=hit)

def s_prets(b, d, tg, k):
    """6e temps (build) : prêts, penalty raté, défaite, relégation — tension."""
    hit = 0.0
    kf = tg - M("fulham") + 0.1
    kj = tg - M("jour") + 0.1
    if kj <= 0:
        ltext(d, (CW / 2, 40), "PRÊTÉ", 22, AMB, min(1, (k + 0.1) / 0.1))
        if kf > 0: ltext(d, (CW / 2, 74), "PRÊTÉ", 22, AMB, min(1, kf / 0.1)); hit = max(hit, 1 - kf / 0.25)
        if k < 0.25: hit = max(hit, 1 - k / 0.25)
        ltext(d, (CW / 2, 110), "ENCORE ?", 14, RED, blink(tg, 2) if kf > 0 else 0.0)
        return dict(hit=hit)
    # « il y a 6 ans, jour pour jour » : date LED
    ltext(d, (CW / 2, 26), "IL Y A 6 ANS", 12, WHT)
    ltext(d, (CW / 2, 44), "JOUR POUR JOUR", 11, AMB, min(1, kj / 0.1))
    km = tg - M("minute") + 0.1
    if km > 0:
        ltext(d, (CW / 2, 70), "90'+", 26, WHT, blink(tg, 2.5))
    kr = tg - M("rate") + 0.1
    if kr > 0:
        ltext(d, (CW / 2, 98), "PENALTY", 15, WHT)
        xmark(d, CW / 2, 120, 10, RED, 1.0); hit = max(hit, 1 - kr / 0.25)
    kd = tg - M("defaite") + 0.1
    if kd > 0:
        d.rectangle((0, 14, CW, 168), fill=(0, 0, 0))
        hit = max(hit, flash_bar(d, 40, "DÉFAITE", RED, kd, 18, 28))
        kc = tg - M("critique") + 0.1
        if kc > 0:
            for i in range(6):
                rng = np.random.default_rng(i)
                x = rng.uniform(15, CW - 15); y = 68 + i * 10 + 3 * math.sin(tg * 5 + i)
                ltext(d, (x, y), "?!" if i % 2 else "✗", 10, scol(RED, 0.6 + 0.4 * math.sin(tg * 7 + i)), 1)
            ltext(d, (CW / 2, 80), "CRITIQUÉ", 16, WHT, min(1, kc / 0.1))
        kdesc = tg - M("descend") + 0.1
        if kdesc > 0:
            d.rectangle((0, 60, CW, 168), fill=(0, 0, 0))
            ltext(d, (CW / 2, 74), "RELÉGATION", 15, RED, min(1, kdesc / 0.1))
            arrow_down(d, CW / 2, 106 + 6 * math.sin(tg * 6), 14, RED); hit = max(hit, 1 - kdesc / 0.25)
        kl = tg - M("encore") + 0.1
        if kl > 0:
            d.rectangle((0, 14, CW, 168), fill=(0, 0, 0))
            ltext(d, (CW / 2, 60), "ENCORE PRÊTÉ", 15, AMB, blink(tg, 2.5)); hit = max(hit, 1 - kl / 0.2)
    return dict(hit=hit)

def s_zero(b, d, tg, k):
    """7e temps (explode) : « À 24 ans, beaucoup pensent… » puis cri IL REPART DE ZÉRO EN ITALIE !"""
    hit = 0.0; kb = tg - K["boom"] + 0.05
    if kb <= 0:
        ltext(d, (CW / 2, 26), "ÂGE", 11, WHT)
        counter(d, CW / 2, 52, 24, 30, AMB, k + 0.1, 0.4, 18)
        kp = tg - M("pensent") + 0.1
        if kp > 0:
            ltext(d, (CW / 2, 92), typed("JAMAIS", kp, 20), 22, RED)
            ltext(d, (CW / 2, 118), typed("UN GRAND ?", kp - 0.5, 20), 18, RED)
        # compte à rebours qui s'emballe
        if kp > 0: ltext(d, (CW / 2, 150), "▮" * int(1 + (kp * 6) % 12), 10, scol(AMB, 0.8), 1)
        return dict(hit=0.0, shake=0.15 * min(1, max(0, kp)) if kp > 0 else 0.0)
    # BOUM : tout le tableau s'allume
    fl = max(0.0, 1 - kb / 0.35)
    if fl > 0: d.rectangle((0, 14, CW, 168), fill=scol(WHT, fl * 0.35))
    zs = int(46 + 30 * (1 - eout(kb / 0.25)))
    ltext(d, (CW / 2, 40), "REPART", 22, GRN, 1.0)
    ltext(d, (CW / 2, 84), "0", zs, AMB, 1.0, maxw=110)
    ki = tg - M("italie") + 0.1
    if ki > 0: ltext(d, (CW / 2, 130), "ITALIE", 22, GRN)
    for i in range(18):   # rayons
        an = i * math.pi / 9 + tg * 0.8; r0 = 34 + 4 * math.sin(tg * 6)
        d.line((CW / 2 + r0 * math.cos(an), 84 + r0 * math.sin(an), CW / 2 + (r0 + 16) * math.cos(an), 84 + (r0 + 16) * math.sin(an)),
               fill=scol(GOLD, 0.6))
    hit = max(0.0, 1 - kb / 0.3)
    return dict(hit=hit, flash=0.3 * max(0.0, 1 - kb / 0.2), shake=max(0.0, 1 - kb / 0.6))

def s_italie(b, d, tg, k):
    hit = 0.0
    ltext(d, (CW / 2, 26), "NOUVEAU DÉPART", 12, GRN)
    kg = tg - K["gate1"] + 0.1
    if kg > 0:
        ltext(d, (CW / 2, 52), "1ER MATCH", 15, WHT)
        hit = max(hit, flash_bar(d, 76, "BUT !", GRN, kg, 20, 28))
        ball(d, 18, 76, 6, WHT, 1, tg * 5); ball(d, CW - 18, 76, 6, WHT, 1, -tg * 5)
    km = tg - M("meilleur1") + 0.1
    if km > 0:
        ltext(d, (CW / 2, 108), "MEILLEUR JOUEUR", 12, GOLD, min(1, km / 0.1))
        ltext(d, (CW / 2, 122), "DU CLUB", 12, GOLD, min(1, km / 0.1))
        kd = tg - M("deux") + 0.1
        if kd > 0: hit = max(hit, counter(d, CW / 2, 148, 2, 22, WHT, kd, 0.3, 0, "× {}"))
        sparkle(d, tg, 30, GOLD, 0.8)
    return dict(hit=hit)

def s_finale(b, d, tg, k):
    hit = 0.0
    ltext(d, (CW / 2, 24), "FINALE 2024", 14, GOLD)
    ltext(d, (CW / 2, 38), "COUPE D'EUROPE", 10, WHT)
    ki = tg - M("invaincue") + 0.1
    kt = tg - M("trois1") + 0.1
    if ki > 0 and kt <= 0:
        ltext(d, (CW / 2, 64), "EN FACE : INVAINCUS", 9, RED, min(1, ki / 0.1))
        k51 = tg - M("cinquante") + 0.1
        if k51 > 0:
            hit = max(hit, counter(d, CW / 2, 96, 51, 34, RED, k51, 0.5, 0))
            ltext(d, (CW / 2, 124), "MATCHS", 13, RED)
    if kt > 0:
        # tableau de score : NOUS 3 - 0
        goals = 0
        for nm in ("trois1", "buts", "score3"):
            if tg >= M(nm) - 0.05: goals += 1
        d.rectangle((6, 54, CW - 7, 132), outline=(90, 90, 110), width=1)
        ltext(d, (CW * 0.28, 64), "LUI", 10, CYAN); ltext(d, (CW * 0.72, 64), "EN FACE", 9, WHT)
        ltext(d, (CW * 0.28, 100), str(goals), 40, AMB, blink(tg, 4) if tg - M("score3") < 0.6 else 1.0)
        ltext(d, (CW / 2, 98), "-", 30, WHT)
        ltext(d, (CW * 0.72, 100), "0", 40, WHT)
        for nm in ("trois1", "buts", "score3"):
            kk = tg - M(nm) + 0.05
            if 0 < kk < 0.25: hit = max(hit, 1 - kk / 0.25)
        ltext(d, (CW / 2, 146), "3 BUTS EN FINALE", 11, GRN)
    ks = tg - K["sunrise"] + 0.1
    if ks > 0:
        d.rectangle((0, 14, CW, 168), fill=(0, 0, 0))
        cup(d, CW / 2, 80, 2.6 * (1 + 0.15 * (1 - eout(ks / 0.2))), GOLD)
        sparkle(d, tg, 70, GOLD, 1.0, 9)
        ltext(d, (CW / 2, 140), "LE TROPHÉE", 16, GOLD); hit = max(hit, 1 - ks / 0.25)
    return dict(hit=hit, flash=0.25 * max(0.0, 1 - ks / 0.2) if ks > 0 else 0.0)

AFR = [(0.42, 0.02), (0.55, 0.0), (0.62, 0.06), (0.72, 0.1), (0.80, 0.22), (0.98, 0.30), (0.88, 0.42), (0.80, 0.55), (0.74, 0.72), (0.62, 0.92),
       (0.55, 0.96), (0.50, 0.84), (0.46, 0.66), (0.40, 0.52), (0.26, 0.48), (0.12, 0.44), (0.02, 0.30), (0.10, 0.14), (0.24, 0.06)]
def s_afrique(b, d, tg, k):
    hit = 0.0
    a = min(1, (k + 0.1) / 0.3)
    pts = [(CW / 2 - 42 + x * 84, 30 + y * 96) for x, y in AFR]
    d.polygon(pts, outline=scol(GOLD, a))
    # remplissage scintillant
    for i in range(160):
        rng = np.random.default_rng(i + 40)
        x, y = rng.uniform(CW / 2 - 40, CW / 2 + 40), rng.uniform(32, 124)
        if cv2.pointPolygonTest(np.array(pts, np.float32), (float(x), float(y)), False) > 0:
            bb = 0.5 + 0.5 * math.sin(tg * 4 + i)
            d.point((x, y), fill=scol(GOLD, a * (0.3 + 0.7 * bb)))
    ke = tg - M("elu") + 0.1
    if ke > 0:
        hit = max(hit, flash_bar(d, 140, "MEILLEUR JOUEUR", GOLD, ke, 13, 18))
        ltext(d, (CW / 2, 160), "D'AFRIQUE", 13, GOLD)
    return dict(hit=hit)

def s_gamin(b, d, tg, k):
    hit = 0.0
    kv = tg - M("voulait") + 0.1
    ltext(d, (CW / 2, 30), "CENTRES DE FORMATION", 10, WHT)
    ltext(d, (CW / 2, 58), "0", 30, RED, 0.9)
    if kv > 0:
        ltext(d, (CW / 2, 88), "↓", 20, WHT)
    kc = tg - M("continent") + 0.1
    km = tg - M("meilleur3") + 0.1
    if km > 0:
        ltext(d, (CW / 2, 116), "MEILLEUR JOUEUR", 13, GOLD, min(1, km / 0.1))
        ltext(d, (CW / 2, 134), "D'UN CONTINENT", 13, GOLD, min(1, km / 0.1) if kc > -0.3 else 0.6)
        sparkle(d, tg, 50, GOLD, 0.9, 5)
        if kc > 0: hit = max(hit, 1 - kc / 0.25)
    return dict(hit=hit)

def s_you(b, d, tg, k):
    hit = 0.0
    ltext(d, (CW / 2, 40), "ET TOI ?", 26, AMB, min(1, (k + 0.1) / 0.1))
    kt = tg - M("attends") + 0.1
    if kt > 0:
        ltext(d, (CW / 2, 76), "TU ATTENDS ?", 15, WHT)
        # sablier / points d'attente
        for i in range(8):
            an = tg * 5 + i * math.pi / 4
            d.ellipse((CW / 2 + 16 * math.cos(an) - 2, 112 + 16 * math.sin(an) - 2, CW / 2 + 16 * math.cos(an) + 2, 112 + 16 * math.sin(an) + 2),
                      fill=scol(WHT, (i + 1) / 8))
    ka = tg - K["arms_up"] + 0.1
    if ka > 0: hit = max(hit, flash_bar(d, 150, "PERSONNE NE VIENDRA", RED, ka, 11, 18))
    return dict(hit=hit)

def s_abonne(b, d, tg, k):
    hit = 0.0
    sc = 1 + 0.25 * (1 - eout(k / 0.2)) + 0.04 * math.sin(tg * 8)
    bw, bh = 96 * sc, 24 * sc
    d.rectangle((CW / 2 - bw / 2, 34 - bh / 2, CW / 2 + bw / 2, 34 + bh / 2), fill=RED)
    ltext(d, (CW / 2, 34), "+ ABONNE-TOI", int(14 * sc), WHT, 1, maxw=int(bw - 6))
    if k < 0.25: hit = 1 - k / 0.25
    kd = tg - M("demain") + 0.1
    if kd > 0:
        ltext(d, (CW / 2, 66), "DEMAIN · ÉPISODE 5", 11, AMB, min(1, kd / 0.1))
        kg = tg - M("guineen") + 0.1
        if kg > 0:
            # petite carte stylisée de l'Afrique de l'Ouest : point lumineux sur la Guinée (sans drapeau)
            ltext(d, (CW / 2, 88), typed("UN GUINÉEN", kg, 30), 16, GRN)
        kr = tg - M("recale") + 0.1
        if kr > 0: ltext(d, (CW / 2, 112), "RECALÉ ✗", 16, RED, min(1, kr / 0.1)); hit = max(hit, 1 - kr / 0.25) if kr < 0.25 else hit
        kgt = tg - M("geant") + 0.1
        if kgt > 0: ltext(d, (CW / 2, 140), "→ CHEZ UN GÉANT", 12, GOLD, min(1, kgt / 0.1))
    return dict(hit=hit)

NUMS = [(np.random.default_rng(i).uniform(10, CW - 10), np.random.default_rng(i + 7).uniform(0, 80), s, np.random.default_rng(i + 3).uniform(0.4, 1.0))
        for i, s in enumerate(["8/10", "10/10", "6/10", "9/10", "7/10", "5/10", "10/10", "8/10", "9/10", "7/10"])]
def s_question(b, d, tg, k):
    pulse = 0.0
    for tk in TJ["q_pulses"]:
        dd = tg - tk
        if 0 <= dd < 0.5: pulse = max(pulse, math.exp(-dd * 7))
    a = 1.0; de = tg - K["q_end"]
    if de > 0: a = max(0.0, 1 - de / 0.8)
    for x, y, s, sp in NUMS:
        yy_ = (y - tg * 6 * sp) % 80 + 84
        ltext(d, (x, yy_), s, 9, scol(AMB, 0.35 * a), 1)
    d.rectangle((2, 14, CW - 3, 168), outline=scol(AMB, 0.3 + 0.7 * pulse))
    return dict(hit=0.5 * pulse)

def s_logo(b, d, tg, k):
    return dict(fade=1 - ease((tg - (END - 0.7)) / 0.7))

SCENES = {"hook": s_hook, "intro": s_intro, "quartier": s_quartier, "essai": s_essai, "debut": s_debut, "prets": s_prets,
          "zero": s_zero, "italie": s_italie, "finale": s_finale, "afrique": s_afrique, "gamin": s_gamin, "you": s_you,
          "abonne": s_abonne, "question": s_question, "logo": s_logo}

def logo_overlay(img, tg, k, fade):
    dim(img, 0.85)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    sc = 1 + 0.15 * (1 - eout(k / 0.5)); g = tuple(int(c * fade) for c in GOLD)
    text(dl, (W / 2, 690), "MINDSET", int(150 * sc), g + (255,), BOLD)
    text(dl, (W / 2, 900), "24", int(300 * sc), g + (255,), BOLD)
    glow = L.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow); img.alpha_composite(glow); img.alpha_composite(L)
    ImageDraw.Draw(img).line((W / 2 - 300 * eout(k / 0.6), 1080, W / 2 + 300 * eout(k / 0.6), 1080), fill=g + (255,), width=4)

def dim(img, a):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * a))); img.alpha_composite(ov)

def render_scene(tg, i):
    s = SCN[i]
    low = Image.new("RGB", (CW, CH), (0, 0, 0)); d = ImageDraw.Draw(low)
    if s["type"] not in ("logo",): header(d, tg)
    R = SCENES[s["type"]](low, d, tg, tg - s["start"]) or {}
    img = led(low)
    if s["type"] == "logo": logo_overlay(img, tg, tg - s["start"], R.get("fade", 1.0))
    return img, R

BGLEVEL = {}
# --------------------------------------------------------------- textes
def _core(wd): return "".join(ch for ch in wd.lower() if ch.isalnum() or ch in "éèàùêâîôûç")
KEYW = {_core(w) for w in TJ["keywords"]}

def sub_img(txt, size=54, stroke=7, maxw=960):
    font = F(BOLD, size); d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines = [[]]
    for wd in txt.split():
        if d.textlength(" ".join(lines[-1] + [wd]).upper(), font=font) > maxw and lines[-1]: lines.append([wd])
        else: lines[-1].append(wd)
    lh = int(size * 1.28)
    im = Image.new("RGBA", (W, lh * len(lines) + stroke * 4), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    sp = d.textlength(" ", font=font)
    for kk, ln in enumerate(lines):
        words = [(w.upper() if _core(w) in KEYW else w, _core(w) in KEYW) for w in ln]
        tw = sum(d.textlength(w, font=font) for w, _ in words) + sp * (len(words) - 1)
        x = (W - tw) / 2; y = stroke * 2 + kk * lh
        for w, kw in words:
            dr.text((x, y), w, font=font, fill=(ORANGE if kw else (255, 255, 255)) + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            x += d.textlength(w, font=font) + sp
    return im

def headline(lines, size=96, stroke=8):
    size = min(fit(t, size, 1000) for t, _ in lines)
    font = F(BOLD, size); lh = int(size * 1.12)
    im = Image.new("RGBA", (W, lh * len(lines) + stroke * 4), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for kk, (txt, col) in enumerate(lines):
        dr.text((W / 2, stroke * 2 + kk * lh + lh / 2), txt, font=font, fill=col + (255,), anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return im

def cta_img():
    font = F(BOLD, 56); txt = TJ["question"].get("cta", "ÉCRIS-LE EN COMMENTAIRE")
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10))); tw = d.textlength(txt, font=font)
    im = Image.new("RGBA", (W, 230), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.rounded_rectangle(((W - tw) / 2 - 34, 10, (W + tw) / 2 + 34, 104), 26, fill=ORANGE + (255,))
    dr.text((W / 2, 57), txt, font=font, fill=(0, 0, 0, 255), anchor="mm")
    cx = W / 2; dr.polygon([(cx - 46, 130), (cx + 46, 130), (cx, 205)], fill=ORANGE + (255,))
    return im

def paste(img, L, cy, alpha=1.0, scale=1.0):
    if alpha <= 0: return
    if scale != 1.0: L = L.resize((int(L.width * scale), int(L.height * scale)), Image.BILINEAR)
    if alpha < 1:
        a = np.asarray(L).copy(); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); L = Image.fromarray(a)
    img.alpha_composite(L, (int((W - L.width) / 2), int(cy - L.height / 2)))

# --------------------------------------------------------------- post-traitement
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.5 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)).clip(0.4, 1)[..., None]
GR = np.random.default_rng(1)

def punch(tg):
    p = 0.0
    for tk in TJ["punches"]:
        dd = tg - tk
        if 0 <= dd < 0.5: p = max(p, math.exp(-dd * 8))
    return p

def post(arr, tg, zoom, shake, flash):
    a = arr.astype(np.float32)
    if zoom != 1.0 or shake > 0:
        dx = shake * 18 * math.sin(tg * 63); dy = shake * 18 * math.sin(tg * 51 + 1)
        Mx = cv2.getRotationMatrix2D((W / 2, H / 2), shake * 0.8 * math.sin(tg * 40), zoom)
        Mx[0, 2] += dx; Mx[1, 2] += dy
        a = cv2.warpAffine(a, Mx, (W, H), borderMode=cv2.BORDER_REPLICATE)
    if flash > 0: a = a + flash * 255 * np.array([1.0, 0.95, 0.85], np.float32)
    a = a * VIGN
    g = GR.normal(0, 5, (H // 2, W // 2)).astype(np.float32)
    a = a + cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    return np.clip(a, 0, 255).astype(np.uint8)

def main(timing, out, t_from=0.0, t_to=None, every=1):
    subs = TJ["subs"]; simgs = [sub_img(s["text"]) for s in subs]
    Q = TJ["question"]
    H1 = headline([(l, (255, 255, 255)) for l in Q["lines"]]); H2 = headline([(Q["highlight"], ORANGE)], 120)
    CTA = cta_img()
    slog1 = headline([("Change ton mental.", (255, 255, 255))], 66, 6); slog2 = headline([("Change ta vie.", (255, 255, 255))], 66, 6)
    t_to = END if t_to is None else t_to
    ff = None
    if out.endswith(".mp4"):
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    XF = 0.22; t0 = time.time()
    for n, fi in enumerate(range(int(t_from * FPS), int(math.ceil(t_to * FPS)), every)):
        tg = fi / FPS
        cur = max(i for i, s in enumerate(SCN) if s["start"] <= tg + 1e-6)
        img, R = render_scene(tg, cur)
        lt = tg - SCN[cur]["start"]
        if cur > 0 and lt < XF:
            prev, _ = render_scene(tg, cur - 1)
            img = Image.blend(prev, img, ease(lt / XF))
        hit = R.get("hit", 0.0); shake = R.get("shake", 0.0) * 0.6 + 0.25 * hit
        zoom = 1.0 + 0.035 * min(1.0, lt / 4.0) + 0.03 * max(hit, punch(tg))
        if K["q_line1"] - 0.05 <= tg < SC["logo"]:
            k1 = tg - K["q_line1"]
            paste(img, H1, H * 0.15, min(1, k1 / 0.12), 1.0 + 0.12 * math.exp(-k1 * 9))
            if tg >= K["q_line2"]:
                k2 = tg - K["q_line2"]; paste(img, H2, H * 0.265, min(1, k2 / 0.1), 1.0 + 0.2 * math.exp(-k2 * 9))
            if tg >= K["q_cta"] - 0.25:
                k3 = tg - (K["q_cta"] - 0.25); paste(img, CTA, H * 0.62 + 10 * math.sin(tg * 9), min(1, k3 / 0.12), 1.0 + 0.1 * math.exp(-k3 * 8))
        if tg >= SC["logo"]:
            fade = R.get("fade", 1.0)
            paste(img, slog1, H * 0.62, ease((tg - K["slogan1"] + 0.1) / 0.3) * fade)
            paste(img, slog2, H * 0.67, ease((tg - K["slogan2"] + 0.1) / 0.3) * fade)
        else:
            for s, im in zip(subs, simgs):
                if K["q_line1"] - 0.05 <= s["start"] < K["q_cta"] - 0.3: continue
                if s["start"] <= tg < s["end"]:
                    pop = 1.0 + 0.06 * (1 - ease((tg - s["start"]) / 0.12))
                    paste(img, im, H * 0.82, min(1, (tg - s["start"]) / 0.06), pop)
        arr = post(np.asarray(img.convert("RGB")), tg, zoom, shake, R.get("flash", 0.0))
        if ff: ff.stdin.write(arr.tobytes())
        else: cv2.imwrite(f"{out}/f_{fi:04d}.png", cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        if n % 60 == 0: print(f"frame {fi} t={tg:.2f}s  {time.time() - t0:.0f}s écoulées", flush=True)
    if ff: ff.stdin.close(); ff.wait()



if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None, int(a[5]) if len(a) > 5 else 1)

# -*- coding: utf-8 -*-
"""Style « bd » (06/11) : BANDE DESSINÉE — cases qui claquent sur papier tramé, encadrés de narrateur, onomatopées (Mendy, épisode 3).
Usage : python3 render_bd.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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
# à une personne réelle), onomatopées, lignes de vitesse. Aucun nom de club / logo / drapeau à l'écran : notions, âges, années.
PAPER = (244, 234, 212); INKC = (14, 14, 18); YEL = (255, 214, 0); CRED = (226, 38, 44); CBLUE = (30, 70, 160)
NAVY = (16, 28, 64); TEAL = (0, 150, 150); CREAM = (255, 248, 230)
ORANGE = YEL; ACC = YEL; GOLD = (246, 192, 60); WHITE = (250, 250, 246); BG = INKC
EPISODE = 3

def M(name, default=99.0): return MK.get(name, default)

def _halftone(w, h, base, dot, step=16, rmax=6.5, direction="diag"):
    img = Image.new("RGBA", (w, h), base + (255,)); d = ImageDraw.Draw(img)
    for yy_ in range(0, h + step, step):
        for xx_ in range(0, w + step, step):
            ox = (step / 2) if (yy_ // step) % 2 else 0
            u = ((xx_ + ox) / max(1, w) + yy_ / max(1, h)) / 2 if direction == "diag" else yy_ / max(1, h)
            r = rmax * (0.15 + 0.85 * u)
            if r > 0.6: d.ellipse((xx_ + ox - r, yy_ - r, xx_ + ox + r, yy_ + r), fill=dot + (255,))
    return img

_PAPER = None
def make_paper():
    global _PAPER
    if _PAPER is None:
        im = _halftone(W, H, PAPER, (228, 214, 186), 22, 4.0)
        d = ImageDraw.Draw(im)
        rng = np.random.default_rng(3)
        for _ in range(900):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            d.point((x, y), fill=(210, 196, 170, 255))
        _PAPER = im
    return _PAPER.copy()

def scenery(level): return make_paper()

def dim(img, a):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * a))); img.alpha_composite(ov)

_HT = {}
def ht_fill(w, h, base, dot, step=16, rmax=6.0):
    k = (w, h, base, dot, step, rmax)
    if k not in _HT: _HT[k] = _halftone(w, h, base, dot, step, rmax)
    return _HT[k].copy()

def panel(img, box, k, draw, base=NAVY, dot=None, rot=0.0, border=12, slam=True):
    """Case de BD : contenu dessiné par draw(L, d, w, h), bord noir épais, ombre portée, entrée qui claque."""
    if k <= 0: return 0.0
    x0, y0, x1, y1 = [int(v) for v in box]; w, h = x1 - x0, y1 - y0
    dot = dot or mix(base, (0, 0, 0), 0.28)
    L = ht_fill(w, h, base, dot)
    dL = ImageDraw.Draw(L, "RGBA")
    draw(L, dL, w, h)
    dL.rectangle((0, 0, w - 1, h - 1), outline=INKC + (255,), width=border)
    S = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    ImageDraw.Draw(S).rectangle((22, 22, w + 22, h + 22), fill=(0, 0, 0, 150))
    S.alpha_composite(L, (6, 6))
    sc = 1.0 + (0.22 * (1 - eout(k / 0.16)) if slam else 0.0)
    rr = rot + (4 * (1 - eout(k / 0.16)) if slam else 0.0)
    if rr: S = S.rotate(rr, resample=Image.BICUBIC, expand=True)
    if sc != 1.0: S = S.resize((int(S.width * sc), int(S.height * sc)), Image.BILINEAR)
    al = min(1.0, k / 0.07)
    if al < 1:
        a = np.asarray(S).copy(); a[..., 3] = (a[..., 3] * al).astype(np.uint8); S = Image.fromarray(a)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    img.alpha_composite(S, (int(cx - S.width / 2 + 8), int(cy - S.height / 2 + 8)))
    return max(0.0, 1 - k / 0.2) * 0.7

def caption(d, x, y, s, k, size=44, maxw=900, col=YEL, tcol=INKC, cps=34, anchor="l"):
    """Encadré de narrateur (rectangle jaune), texte tapé."""
    if k <= 0: return
    size = fit(s, size, maxw - 40)
    f = F(BOLD, size); tw = d.textlength(s, font=f); hh = int(size * 1.45)
    x0 = x if anchor == "l" else x - (tw + 44) / 2
    d.rectangle((x0, y, x0 + tw + 44, y + hh), fill=col + (255,), outline=INKC + (255,), width=6)
    d.text((x0 + 22, y + hh / 2), typew(s, k, cps), font=f, fill=tcol + (255,), anchor="lm")

def star_poly(cx, cy, r1, r2, n, rot=0.0):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + rot; r = r1 if i % 2 == 0 else r2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def onom(img, s, center, size, k, col=YEL, out=INKC, burst=CRED, angle=-8, dur=0.16, burst_r=None):
    """Onomatopée de BD dans une explosion (éclat)."""
    if k <= 0: return 0.0
    sc = 1.0 + 0.9 * (1 - eout(k / dur))
    size = fit(s, size, 940)
    L = Image.new("RGBA", (W, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F(BOLD, size); tw = d.textlength(s, font=f)
    if burst is not None:
        R = burst_r or max(tw * 0.62, size * 1.3)
        d.polygon(star_poly(W / 2, 350, R * 1.08 + 10, R * 0.72, 14, 0.2), fill=INKC + (255,))
        d.polygon(star_poly(W / 2, 350, R * 1.08, R * 0.72 - 8, 14, 0.2), fill=burst + (255,))
    d.text((W / 2, 350), s, font=f, fill=col + (255,), anchor="mm", stroke_width=max(6, size // 9), stroke_fill=out + (255,))
    L = L.rotate(angle, resample=Image.BICUBIC)
    if sc != 1.0: L = L.resize((int(L.width * sc), int(L.height * sc)), Image.BILINEAR)
    al = min(1.0, k / 0.06)
    if al < 1:
        a = np.asarray(L).copy(); a[..., 3] = (a[..., 3] * al).astype(np.uint8); L = Image.fromarray(a)
    img.alpha_composite(L, (int(center[0] - L.width / 2), int(center[1] - L.height / 2)))
    return max(0.0, 1 - k / 0.25)

def speed_lines(d, cx, cy, w, h, tg, n=60, col=INKC, r0=220):
    rng = np.random.default_rng(int(tg * 12))
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.03, 0.03)
        r1 = r0 + rng.uniform(0, 140); r2 = max(w, h)
        wd = int(rng.uniform(3, 12))
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a), cy + r2 * math.sin(a)), fill=col + (255,), width=wd)

# ---------------------------------------------------------------- objets dessinés (style encré)
def glove(d, cx, cy, s, flip=1, col=CREAM, cuff=TEAL, clench=0.0):
    o = INKC + (255,); lw = max(3, int(6 * s))
    # paume
    d.rounded_rectangle((cx - 62 * s, cy - 40 * s, cx + 62 * s, cy + 95 * s), int(34 * s), fill=col + (255,), outline=o, width=lw)
    # doigts
    for i in range(4):
        fx = cx - 54 * s + i * 36 * s
        top = cy - (150 - abs(i - 1.5) * 18) * s * (1 - 0.45 * clench)
        d.rounded_rectangle((fx, top, fx + 32 * s, cy - 10 * s), int(16 * s), fill=col + (255,), outline=o, width=lw)
    # pouce
    tx = cx + flip * 58 * s
    d.rounded_rectangle((min(tx, tx + flip * 52 * s), cy - 10 * s, max(tx, tx + flip * 52 * s), cy + 40 * s), int(22 * s), fill=col + (255,), outline=o, width=lw)
    # manchette
    d.rectangle((cx - 66 * s, cy + 80 * s, cx + 66 * s, cy + 130 * s), fill=cuff + (255,), outline=o, width=lw)
    d.line((cx - 40 * s, cy + 20 * s, cx + 40 * s, cy + 20 * s), fill=mix(col, INKC, 0.25) + (255,), width=max(2, int(4 * s)))

def goal_frame(d, x0, y0, x1, y1, s=1.0, col=WHITE):
    for i in range(1, 9):
        x = x0 + (x1 - x0) * i / 9; d.line((x, y0, x + (x1 - x0) * 0.02, y1), fill=(150, 160, 175, 255), width=2)
    for j in range(1, 6):
        y = y0 + (y1 - y0) * j / 6; d.line((x0, y, x1, y), fill=(150, 160, 175, 255), width=2)
    w = int(18 * s)
    d.rectangle((x0 - w, y0 - w, x1 + w, y0), fill=col + (255,), outline=INKC + (255,), width=5)
    d.rectangle((x0 - w, y0, x0, y1), fill=col + (255,), outline=INKC + (255,), width=5)
    d.rectangle((x1, y0, x1 + w, y1), fill=col + (255,), outline=INKC + (255,), width=5)

def phone(d, cx, cy, s, tg, msg="0 APPEL", lit=True):
    o = INKC + (255,)
    d.rounded_rectangle((cx - 120 * s, cy - 220 * s, cx + 120 * s, cy + 220 * s), int(34 * s), fill=(30, 30, 36, 255), outline=o, width=8)
    scr = (40, 70, 120) if lit else (20, 24, 30)
    d.rounded_rectangle((cx - 100 * s, cy - 180 * s, cx + 100 * s, cy + 170 * s), int(14 * s), fill=scr + (255,))
    d.ellipse((cx - 14 * s, cy + 186 * s, cx + 14 * s, cy + 210 * s), outline=(90, 90, 100, 255), width=3)
    text(d, (cx, cy - 40 * s), msg, int(46 * s), WHITE + (255,), BOLD)
    # combiné barré
    hx, hy = cx, cy + 70 * s
    d.arc((hx - 40 * s, hy - 30 * s, hx + 40 * s, hy + 40 * s), 200, 340, fill=(200, 210, 230, 255), width=int(14 * s))
    d.line((hx - 50 * s, hy + 40 * s, hx + 50 * s, hy - 30 * s), fill=CRED + (255,), width=int(9 * s))

def jersey(d, cx, cy, s, col, num, hl=False):
    o = (YEL if hl else INKC) + (255,); lw = 10 if hl else 6
    pts = [(cx - 60 * s, cy - 80 * s), (cx - 25 * s, cy - 92 * s), (cx, cy - 78 * s), (cx + 25 * s, cy - 92 * s), (cx + 60 * s, cy - 80 * s),
           (cx + 100 * s, cy - 40 * s), (cx + 76 * s, cy - 12 * s), (cx + 58 * s, cy - 28 * s), (cx + 58 * s, cy + 90 * s),
           (cx - 58 * s, cy + 90 * s), (cx - 58 * s, cy - 28 * s), (cx - 76 * s, cy - 12 * s), (cx - 100 * s, cy - 40 * s)]
    d.polygon(pts, fill=col + (255,), outline=o, width=lw)
    text(d, (cx, cy + 15 * s), num, int(80 * s), WHITE + (255,), BOLD, stroke=4, scol=INKC + (255,))

def cup(d, cx, cy, s, col=GOLD):
    o = INKC + (255,)
    d.polygon([(cx - 80 * s, cy - 120 * s), (cx + 80 * s, cy - 120 * s), (cx + 55 * s, cy + 10 * s), (cx - 55 * s, cy + 10 * s)], fill=col + (255,), outline=o, width=6)
    d.arc((cx - 130 * s, cy - 110 * s, cx - 40 * s, cy - 20 * s), 90, 270, fill=o, width=int(14 * s))
    d.arc((cx + 40 * s, cy - 110 * s, cx + 130 * s, cy - 20 * s), 270, 90, fill=o, width=int(14 * s))
    d.rectangle((cx - 16 * s, cy + 10 * s, cx + 16 * s, cy + 70 * s), fill=col + (255,), outline=o, width=5)
    d.rectangle((cx - 70 * s, cy + 70 * s, cx + 70 * s, cy + 110 * s), fill=col + (255,), outline=o, width=6)
    d.line((cx - 50 * s, cy - 95 * s, cx - 30 * s, cy - 10 * s), fill=(255, 240, 180, 255), width=int(8 * s))

def cstar(d, cx, cy, r, col=YEL):
    d.polygon(star_poly(cx, cy, r, r * 0.45, 5, -math.pi / 2), fill=col + (255,), outline=INKC + (255,), width=5)

def calendar(d, x0, y0, w, h, n_cross, tg):
    o = INKC + (255,)
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=CREAM + (255,), outline=o, width=8)
    d.rectangle((x0, y0, x0 + w, y0 + 90), fill=CRED + (255,), outline=o, width=8)
    text(d, (x0 + w / 2, y0 + 47), "UNE ANNÉE SANS CLUB", fit("UNE ANNÉE SANS CLUB", 50, w - 40), WHITE + (255,), BOLD)
    mois = "J F M A M J J A S O N D".split()
    cw, chh = w / 4, (h - 90) / 3
    for i, m in enumerate(mois):
        cx = x0 + (i % 4 + 0.5) * cw; cy = y0 + 90 + (i // 4 + 0.5) * chh
        text(d, (cx, cy), m, 70, INKC + (255,), BOLD)
        if i < n_cross:
            r = 46
            d.line((cx - r, cy - r, cx + r, cy + r), fill=CRED + (255,), width=12)
            d.line((cx + r, cy - r, cx - r, cy + r), fill=CRED + (255,), width=12)

def red_card(d, cx, cy, s, ang=0):
    L = Image.new("RGBA", (int(240 * s), int(320 * s)), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.rounded_rectangle((10, 10, L.width - 10, L.height - 10), 18, fill=CRED + (255,), outline=INKC + (255,), width=8)
    return L.rotate(ang, resample=Image.BICUBIC, expand=True)

def door(d, cx, cy, w, h, k):
    o = INKC + (255,)
    d.rectangle((cx - w / 2 - 16, cy - h / 2 - 16, cx + w / 2 + 16, cy + h / 2), fill=(70, 50, 36, 255), outline=o, width=6)
    op = eout(k)
    d.rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), fill=(255, 236, 160, 255))
    # rayons de lumière
    for i in range(7):
        a = -0.6 + i * 0.2
        d.polygon([(cx - w / 2 + 10, cy + h / 2), (cx + w / 2 - 10, cy + h / 2),
                   (cx + math.sin(a) * 700 + 60, cy + h / 2 + 260 * op), (cx + math.sin(a) * 700 - 60, cy + h / 2 + 260 * op)],
                  fill=(255, 236, 160, int(50 * op)))
    dw = w * (1 - 0.8 * op)
    d.polygon([(cx - w / 2, cy - h / 2), (cx - w / 2 + dw, cy - h / 2 + 30 * op), (cx - w / 2 + dw, cy + h / 2 - 30 * op), (cx - w / 2, cy + h / 2)],
              fill=(120, 80, 50, 255), outline=o)

def series_banner(d, tg):
    if tg > 4.2: return
    a = min(1, tg / 0.12) * (1 - ease((tg - 3.8) / 0.4))
    if a <= 0: return
    d.rectangle((60, 60, W - 60, 230), fill=mix(PAPER, YEL, a) + (255,), outline=mix(PAPER, INKC, a) + (255,), width=10)
    text(d, (W / 2, 118), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 66, 900), mix(PAPER, INKC, a) + (255,), BOLD)
    text(d, (W / 2, 190), f"ÉPISODE {EPISODE}", 46, mix(PAPER, CRED, a) + (255,), BOLD)

def bigtitle(d, y, s, size, col=INKC, k=1.0, stroke=0, scol=WHITE):
    if k <= 0: return
    size = fit(s, size, 980)
    sz = int(size * (1 + 0.25 * (1 - eout(k / 0.15))))
    text(d, (W / 2, y), s, sz, col + (255,), BOLD, stroke=stroke, scol=scol + (255,))

# ---------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    hit = max(hit, panel(img, (70, 280, W - 70, 980), k + 0.2, lambda L, dl, w, h: (
        phone(dl, w / 2, h / 2 + 10, 1.25, tg, "0 APPEL"),
        caption(dl, 30, 30, "PERSONNE NE T'APPELLE ?", k + 0.3, 50, w - 60)), NAVY))
    kp = tg - M("personne2") + 0.1
    if kp > 0:
        def dr(L, dl, w, h):
            for i in range(9):
                x = 70 + (i % 5) * 190 + (95 if i >= 5 else 0); y = 170 + (i // 5) * 120
                dl.ellipse((x - 42, y - 50, x + 42, y + 34), fill=(24, 24, 30, 255))
                dl.rounded_rectangle((x - 80, y + 20, x + 80, y + 160), 40, fill=(24, 24, 30, 255))
            caption(dl, w / 2, h - 110, "PERSONNE NE CROIT EN TOI ?", kp, 46, w - 60, anchor="c")
        hit = max(hit, panel(img, (110, 1010, W - 110, 1430), kp, dr, (150, 160, 170), rot=-2))
    ki = tg - M("ils") + 0.1
    if ki > 0:
        dim(img, min(0.55, ki * 3)); d2 = ImageDraw.Draw(img)
        hit = max(hit, onom(img, "ILS ONT FAILLI", (W / 2, 640), 120, ki, YEL, INKC, CRED, -6))
        hit = max(hit, onom(img, "ABANDONNER", (W / 2, 900), 130, ki - 0.25, WHITE, INKC, None, 4))
        ke = tg - M("episode") + 0.1
        if ke > 0: hit = max(hit, stamp(img, f"ÉPISODE {EPISODE}", (W / 2, 1200), 150, -5, ke, CRED))
    series_banner(ImageDraw.Draw(img), tg)
    return dict(hit=hit)

def s_intro(img, d, tg, k):
    hit = 0.0
    def dr(L, dl, w, h):
        goal_frame(dl, 90, 260, w - 90, h - 40)
        glove(dl, w / 2 - 150, h / 2 + 120, 1.3, -1); glove(dl, w / 2 + 150, h / 2 + 120, 1.3, 1)
        caption(dl, 30, 30, "L'HISTOIRE VRAIE D'UN GARDIEN", k + 0.1, 46, w - 60)
    hit = max(hit, panel(img, (70, 240, W - 70, 1000), k + 0.15, dr, CBLUE))
    kc = tg - M("chomage1") + 0.1
    if kc > 0:
        hit = max(hit, stamp(img, "DU CHÔMAGE", (W / 2 - 150, 1110), 92, -6, kc, INKC))
        ks = tg - M("sommet") + 0.1
        if ks > 0:
            hit = max(hit, onom(img, "AU SOMMET !", (W / 2 + 120, 1290), 110, ks, YEL, INKC, CRED, 5))
    kn = tg - M("ne") + 0.1
    if kn > 0:
        dim(img, min(0.45, kn * 3)); d2 = ImageDraw.Draw(img)
        def dr2(L, dl, w, h):
            text(dl, (w / 2, h * 0.35), "NÉ EN NORMANDIE", fit("NÉ EN NORMANDIE", 80, w - 60), INKC + (255,), BOLD)
            ks2 = tg - M("senegal") + 0.25
            if ks2 > 0: text(dl, (w / 2, h * 0.7), typew("RACINES AU SÉNÉGAL", ks2, 30), fit("RACINES AU SÉNÉGAL", 76, w - 60), CRED + (255,), BOLD)
        hit = max(hit, panel(img, (90, 560, W - 90, 980), kn, dr2, CREAM, (232, 220, 196), rot=2))
    return dict(hit=hit)

def s_havre(img, d, tg, k):
    hit = 0.0
    def dr(L, dl, w, h):
        text(dl, (w / 2, h * 0.42), "13 ANS", 210, YEL + (255,), BOLD, stroke=10, scol=INKC + (255,))
        caption(dl, w / 2, h - 120, "CENTRE DE FORMATION", tg - M("formation") + 0.3, 52, w - 60, anchor="c")
    hit = max(hit, panel(img, (70, 240, W - 70, 760), k + 0.15, dr, CBLUE))
    kn = tg - M("numero") + 0.1
    if kn > 0:
        def dr2(L, dl, w, h):
            # podium : n°1 = un autre, lui à côté
            dl.rectangle((w / 2 - 140, h - 330, w / 2 + 140, h - 40), fill=GOLD + (255,), outline=INKC + (255,), width=8)
            text(dl, (w / 2, h - 185), "N°1", 110, INKC + (255,), BOLD)
            dl.rectangle((w / 2 - 420, h - 200, w / 2 - 160, h - 40), fill=(180, 186, 196, 255), outline=INKC + (255,), width=8)
            text(dl, (w / 2 - 290, h - 120), "LUI", 70, INKC + (255,), BOLD)
            jersey(dl, w / 2, h - 450, 0.95, (40, 40, 48), "1")
            glove(dl, w / 2 - 290, h - 300, 0.7, -1)
            caption(dl, 30, 30, "PAS LE NUMÉRO 1", kn + 0.1, 50, w - 60, col=WHITE)
        hit = max(hit, panel(img, (90, 790, W - 90, 1440), kn, dr2, (200, 70, 60), rot=-1.5))
    ka = tg - M("amateurs") + 0.1
    if ka > 0:
        hit = max(hit, onom(img, "↓ CHEZ LES AMATEURS", (W / 2, 1180), 84, ka, WHITE, INKC, INKC, -4, burst_r=520))
    return dict(hit=hit)

def s_cherbourg(img, d, tg, k):
    hit = 0.0
    def dr(L, dl, w, h):
        # petit stade : tribune + projecteurs faibles
        dl.rectangle((0, h * 0.62, w, h), fill=(30, 110, 60, 255))
        for i in range(6): dl.rectangle((60 + i * 160, h * 0.38, 160 + i * 160, h * 0.62), fill=(60, 64, 80, 255), outline=INKC + (255,), width=4)
        for x in (90, w - 90):
            dl.line((x, h * 0.1, x, h * 0.62), fill=INKC + (255,), width=10)
            dl.rectangle((x - 50, h * 0.06, x + 50, h * 0.14), fill=(255, 240, 170, 255), outline=INKC + (255,), width=5)
        text(dl, (w / 2, h * 0.25), "3e DIVISION", fit("3e DIVISION", 110, w - 260), WHITE + (255,), BOLD, stroke=8, scol=INKC + (255,))
    hit = max(hit, panel(img, (70, 240, W - 70, 760), k + 0.15, dr, NAVY))
    k22 = tg - M("vingtdeux") + 0.1
    if k22 > 0:
        def dr2(L, dl, w, h):
            text(dl, (w / 2, h * 0.3), "22 ANS", 190, CRED + (255,), BOLD, stroke=8, scol=INKC + (255,))
        hit = max(hit, panel(img, (110, 790, W - 110, 1180), k22, dr2, CREAM, (232, 220, 196), rot=2))
        kc = tg - M("contrat") + 0.1
        if kc > 0: hit = max(hit, stamp(img, "PLUS DE CONTRAT", (W / 2, 1020), 86, -6, kc, CRED))
        kb = tg - M("club") + 0.1
        if kb > 0: hit = max(hit, stamp(img, "PLUS DE CLUB", (W / 2, 1150), 86, 4, kb, INKC))
    kp = tg - M("personne3") + 0.1
    if kp > 0:
        dim(img, min(0.6, kp * 3))
        hit = max(hit, panel(img, (220, 300, W - 220, 1300), kp, lambda L, dl, w, h: (
            phone(dl, w / 2, h / 2 - 20, 1.6, tg, "0 APPEL"),
            caption(dl, w / 2, h - 120, "PERSONNE NE L'APPELLE", kp + 0.1, 46, w - 40, anchor="c")), (60, 60, 70)))
    return dict(hit=hit)

def s_chomage(img, d, tg, k):
    hit = 0.0
    def dr(L, dl, w, h):
        ka = tg - M("annee") + 0.2
        n = 0 if ka <= 0 else min(12, int(ka / 0.17) + 1)
        calendar(dl, 50, 140, w - 100, h - 200, n, tg)
        caption(dl, 30, 30, "IL S'INSCRIT AU CHÔMAGE", k + 0.1, 48, w - 60)
    hit = max(hit, panel(img, (70, 240, W - 70, 1150), k + 0.15, dr, (150, 160, 170)))
    kc = tg - M("chomage2") + 0.1
    if kc > 0: hit = max(hit, stamp(img, "AU CHÔMAGE", (W / 2, 1270), 120, -5, kc, CRED))
    kq = tg - M("continuer") + 0.1
    if kq > 0:
        dim(img, min(0.55, kq * 3))
        hit = max(hit, onom(img, "CONTINUER ?", (W / 2, 760), 130, kq, WHITE, INKC, CBLUE, -5))
    return dict(hit=hit)

def s_marseille(img, d, tg, k):
    hit = 0.0
    def dr(L, dl, w, h):
        door(dl, w / 2, h / 2 + 40, 230, 400, (tg - M("porte") + 0.3) / 0.8)
        caption(dl, 30, 30, "UNE PETITE PORTE…", k + 0.1, 48, w - 60)
    hit = max(hit, panel(img, (70, 240, W - 70, 800), k + 0.15, dr, (40, 30, 60)))
    kq = tg - M("quatrieme") + 0.1
    if kq > 0:
        def dr2(L, dl, w, h):
            for i in range(4):
                x = 130 + i * 230
                jersey(dl, x, 230, 0.9, (60, 60, 72) if i < 3 else TEAL, str(i + 1), hl=(i == 3))
            caption(dl, w / 2, h - 110, "4e GARDIEN · ÉQUIPE RÉSERVE", kq + 0.1, 46, w - 40, anchor="c")
        hit = max(hit, panel(img, (90, 830, W - 90, 1300), kq, dr2, CREAM, (232, 220, 196), rot=-1.5))
    kf = tg - M("fini") + 0.15
    if kf > 0:
        dim(img, min(0.7, kf * 2.5))
        hit = max(hit, stamp(img, "FINI ?", (W / 2, 760), 230, -8, kf, CRED))
    return dict(hit=hit)

def s_gants(img, d, tg, k):
    """Le cri : page pleine, lignes de vitesse, gants qui se referment, onomatopée géante."""
    dk = tg - K["boom"]
    L = ht_fill(W, H, CRED, (180, 20, 30), 20, 8)
    dl = ImageDraw.Draw(L)
    speed_lines(dl, W / 2, 820, W, H, tg, 70, INKC, 330)
    s = 1.6 + 0.5 * eout(min(1, max(0, k) / 0.5))
    cl = eout(min(1, max(0, dk + 0.1) / 0.3))
    glove(dl, W / 2 - 170 * s / 1.6, 820, s, -1, clench=cl); glove(dl, W / 2 + 170 * s / 1.6, 820, s, 1, clench=cl)
    img.alpha_composite(L)
    hit = onom(img, "IL NE LÂCHE PAS", (W / 2, 330), 120, k, YEL, INKC, None, -5)
    kg = tg - M("gants") + 0.1
    if kg > 0: hit = max(hit, onom(img, "LES GANTS !", (W / 2, 1240), 160, kg, YEL, INKC, INKC, 5, burst_r=560))
    fl = max(0.0, 1 - abs(dk) / 0.2) * 0.6 if dk > -0.2 else 0.0
    return dict(hit=max(hit, 0.8 * max(0, 1 - abs(dk) / 0.4)), shake=0.9 * max(0, 1 - max(0, dk) / 0.8), flash=fl)

def s_reims(img, d, tg, k):
    hit = 0.0
    ke = tg - M("expulse") + 0.1
    def dr(L, dl, w, h):
        caption(dl, 30, 30, "UN SOIR, LE TITULAIRE EST EXPULSÉ", k + 0.3, 44, w - 60)
        if ke > 0:
            c = red_card(dl, 0, 0, 1.3, -14 * eout(ke / 0.2))
            L.alpha_composite(c, (int(w / 2 - c.width / 2), int(h / 2 - c.height / 2 + 40 + 200 * (1 - eout(ke / 0.15)))))
        else:
            text(dl, (w / 2, h / 2 + 40), "…", 200, WHITE + (255,), BOLD)
    hit = max(hit, panel(img, (70, 240, W - 70, 780), k + 0.15, dr, NAVY))
    if ke > 0: hit = max(hit, max(0.0, 1 - ke / 0.2))
    ki = tg - M("entre2") + 0.1
    if ki > 0:
        def dr2(L, dl, w, h):
            x = -200 + (w / 2 + 200) * eout(ki / 0.4)
            glove(dl, x - 110, h / 2 + 20, 1.0, -1); glove(dl, x + 110, h / 2 + 20, 1.0, 1)
            caption(dl, 30, 30, "IL ENTRE…", ki + 0.1, 46, w - 60)
            kso = tg - M("sort") + 0.1
            if kso > 0: caption(dl, w - 560, h - 110, "… ET NE SORT PLUS", kso, 46, 540, col=WHITE)
        hit = max(hit, panel(img, (90, 810, W - 90, 1220), ki, dr2, TEAL, rot=1.5))
    kt = tg - M("titre") + 0.1
    if kt > 0:
        dim(img, min(0.5, kt * 3))
        def dr3(L, dl, w, h):
            steps = [("TITRE · 2e DIV.", M("titre")), ("1re DIVISION", M("rennes")), ("ANGLETERRE", M("chelsea"))]
            for i, (lab, t0) in enumerate(steps):
                kk = tg - t0 + 0.1
                if kk <= 0: continue
                x0 = 40 + i * 300; top = h - 140 - (i + 1) * 170
                dl.rectangle((x0, top + 60 * (1 - eout(kk / 0.2)), x0 + 290, h - 40), fill=(GOLD if i == 2 else (230, 230, 236)) + (255,), outline=INKC + (255,), width=7)
                text(dl, (x0 + 145, top + 60), lab, fit(lab, 44, 260), INKC + (255,), BOLD)
            kc = tg - M("titre") + 0.1
            if kc > 0: cup(dl, 185, h - 560, 0.7)
        hit = max(hit, panel(img, (70, 300, W - 70, 1250), kt, dr3, CBLUE, rot=-1))
    return dict(hit=hit)

def s_europe(img, d, tg, k):
    hit = 0.0
    def dr(L, dl, w, h):
        # stade de finale la nuit : projecteurs + tribunes
        for i, x in enumerate((120, w - 120)):
            dl.polygon([(x - 60, 40), (x + 60, 40), (w / 2 + (300 if i else -300), h), (w / 2 + (100 if i else -100), h)], fill=(255, 250, 220, 60))
            dl.rectangle((x - 70, 30, x + 70, 90), fill=(255, 250, 220, 255), outline=INKC + (255,), width=5)
        for r in range(4):
            dl.rectangle((0, 200 + r * 60, w, 250 + r * 60), fill=(40 + r * 10, 46 + r * 10, 70 + r * 10, 255))
        dl.rectangle((0, h * 0.68, w, h), fill=(30, 120, 64, 255))
        text(dl, (w / 2, 150), "2021 · LA FINALE", fit("2021 · LA FINALE", 100, w - 340), YEL + (255,), BOLD, stroke=8, scol=INKC + (255,))
        ka = tg - M("africain") + 0.1
        if ka > 0: caption(dl, w / 2, h * 0.52, "1er GARDIEN AFRICAIN EN FINALE", ka, 44, w - 40, anchor="c")
    hit = max(hit, panel(img, (70, 240, W - 70, 900), k + 0.15, dr, NAVY))
    kz = tg - M("zero") + 0.1
    if kz > 0:
        def dr2(L, dl, w, h):
            text(dl, (w / 2, h / 2 - 30), "0", 260, YEL + (255,), BOLD, stroke=10, scol=INKC + (255,))
            text(dl, (w / 2, h - 70), "BUT ENCAISSÉ", 62, WHITE + (255,), BOLD, stroke=5, scol=INKC + (255,))
        hit = max(hit, panel(img, (90, 930, W / 2 - 10, 1420), kz, dr2, (30, 30, 36), rot=-2))
    kg = tg - M("gagne") + 0.1
    if kg > 0:
        def dr3(L, dl, w, h):
            cup(dl, w / 2, h / 2 + 10, 1.25)
            for i in range(5): cstar(dl, 50 + i * 85, 50 + (i % 2) * 30, 26)
        hit = max(hit, panel(img, (W / 2 + 10, 930, W - 90, 1420), kg, dr3, (200, 60, 50), rot=2))
        hit = max(hit, onom(img, "VICTOIRE !", (W / 2, 1000), 110, kg - 0.1, YEL, INKC, CRED, -6))
    ku = tg - M("elu") + 0.1
    if ku > 0:
        dim(img, min(0.6, ku * 3))
        d2 = ImageDraw.Draw(img); cstar(d2, W / 2, 700, 230 * eout(ku / 0.3))
        hit = max(hit, stamp(img, "MEILLEUR GARDIEN", (W / 2, 1000), 110, -5, ku, GOLD))
        hit = max(hit, stamp(img, "DU MONDE", (W / 2, 1150), 120, 4, ku - 0.35, GOLD))
    return dict(hit=hit)

AFR = [(0.42, 0.02), (0.55, 0.0), (0.62, 0.06), (0.72, 0.1), (0.80, 0.22), (0.98, 0.30), (0.88, 0.42), (0.80, 0.55), (0.74, 0.72), (0.62, 0.92),
       (0.55, 0.98), (0.48, 0.86), (0.44, 0.66), (0.40, 0.52), (0.30, 0.46), (0.12, 0.44), (0.04, 0.34), (0.08, 0.16), (0.22, 0.06)]
def s_afrique(img, d, tg, k):
    hit = 0.0
    def dr(L, dl, w, h):
        cw, ch, ox, oy = 520, 600, w / 2 - 260, 150
        dl.polygon([(ox + x * cw, oy + y * ch) for x, y in AFR], fill=(232, 170, 60, 255), outline=INKC + (255,), width=8)
        cup(dl, w / 2 + 30, oy + 330, 0.9)
        caption(dl, 30, 30, "2022 · COUPE D'AFRIQUE", k + 0.2, 50, w - 60)
    hit = max(hit, panel(img, (70, 240, W - 70, 1060), k + 0.15, dr, (30, 120, 90)))
    kt = tg - M("tournoi") + 0.15
    if kt > 0:
        hit = max(hit, stamp(img, "MEILLEUR GARDIEN", (W / 2, 1190), 104, -5, kt, CRED))
        hit = max(hit, stamp(img, "DU TOURNOI", (W / 2, 1330), 104, 4, kt - 0.25, CRED))
    return dict(hit=hit)

def s_coupes(img, d, tg, k):
    hit = 0.0
    def dl_(L, dl, w, h):
        phone(dl, w / 2, h / 2 - 20, 0.95, tg, "0 APPEL", lit=False)
        text(dl, (w / 2, h - 70), "LE CHÔMEUR", fit("LE CHÔMEUR", 60, w - 40), WHITE + (255,), BOLD, stroke=5, scol=INKC + (255,))
    hit = max(hit, panel(img, (70, 300, W / 2 - 10, 1000), k + 0.15, dl_, (110, 116, 126), rot=-2))
    ks = tg - M("souleve") + 0.1
    if ks > 0:
        def dr(L, dl, w, h):
            cup(dl, w / 2 - 95, h / 2 - 60, 0.75); cup(dl, w / 2 + 95, h / 2 + 40, 0.75, (250, 210, 90))
            for i in range(4): cstar(dl, 60 + i * 110, 70 + (i % 2) * 40, 26)
            text(dl, (w / 2, h - 70), "LES PLUS GRANDES COUPES", fit("LES PLUS GRANDES COUPES", 56, w - 40), YEL + (255,), BOLD, stroke=5, scol=INKC + (255,))
        hit = max(hit, panel(img, (W / 2 + 10, 300, W - 70, 1000), ks, dr, (200, 60, 50), rot=2))
        hit = max(hit, onom(img, "BOUM !", (W / 2, 1250), 120, ks - 0.1, YEL, INKC, CRED, -6))
    return dict(hit=hit)

def s_you(img, d, tg, k):
    hit = 0.0
    def dr(L, dl, w, h):
        text(dl, (w / 2, 150), "ET TOI ?", 150, YEL + (255,), BOLD, stroke=9, scol=INKC + (255,))
        phone(dl, w / 2, h / 2 + 120, 1.15, tg, "EN ATTENTE…")
        for i in range(8):
            a = tg * 6 + i * math.pi / 4
            dl.ellipse((w / 2 + 70 * math.cos(a) - 10, h / 2 - 20 + 70 * math.sin(a) - 10, w / 2 + 70 * math.cos(a) + 10, h / 2 - 20 + 70 * math.sin(a) + 10),
                       fill=(255, 255, 255, int(255 * (i + 1) / 8)))
    hit = max(hit, panel(img, (90, 260, W - 90, 1330), k + 0.15, dr, CBLUE))
    ka = tg - K["arms_up"] + 0.05
    if ka > 0: hit = max(hit, stamp(img, "ATTENDRE ?", (W / 2, 1200), 150, -6, ka, CRED))
    return dict(hit=hit)

def s_abonne(img, d, tg, k):
    hit = 0.0
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rectangle((W / 2 - bw / 2 + 14, 380 - bh / 2 + 14, W / 2 + bw / 2 + 14, 380 + bh / 2 + 14), fill=INKC + (255,))
    d.rectangle((W / 2 - bw / 2, 380 - bh / 2, W / 2 + bw / 2, 380 + bh / 2), fill=CRED + (255,), outline=INKC + (255,), width=10)
    text(d, (W / 2 - bw / 2 + 90 * sc, 380), "+", int(130 * sc), WHITE + (255,), BOLD)
    text(d, (W / 2 + 50 * sc, 380), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE + (255,), BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = tg - M("demain") + 0.1
    if kd > 0:
        def dr(L, dl, w, h):
            text(dl, (w / 2, 80), f"DEMAIN · ÉPISODE {EPISODE + 1}", fit(f"DEMAIN · ÉPISODE {EPISODE + 1}", 70, w - 60), YEL + (255,), BOLD, stroke=6, scol=INKC + (255,))
            # terrain de quartier : grillage + petit but
            for i in range(0, w, 40):
                dl.line((i, 170, i + 120, 470), fill=(150, 160, 170, 255), width=3); dl.line((i + 120, 170, i, 470), fill=(150, 160, 170, 255), width=3)
            dl.rectangle((0, 470, w, h), fill=(110, 110, 120, 255))
            goal_frame(dl, w / 2 - 160, 300, w / 2 + 160, 470, 0.8)
            kq = tg - M("quartier") + 0.2
            if kq > 0: caption(dl, w / 2, h - 120, "UN CLUB DE QUARTIER", kq, 52, w - 40, anchor="c")
        hit = max(hit, panel(img, (90, 560, W - 90, 1260), kd, dr, NAVY, rot=-1))
        kf = tg - M("formation2") + 0.1
        if kf > 0: hit = max(hit, stamp(img, "?", (W / 2 + 360, 640), 200, 10, kf, CRED, box=False))
    return dict(hit=hit)

NUMS = [(np.random.default_rng(i).uniform(140, W - 140), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["8/10", "10/10", "6/10", "9/10", "7/10", "5/10", "10/10", "8/10", "9/10", "7/10"])]
def s_question(img, d, tg, k):
    L = ht_fill(W, H, (20, 24, 40), (34, 40, 66), 20, 7); img.alpha_composite(L); d = ImageDraw.Draw(img)
    pulse = 0.0
    for tk in TJ["q_pulses"]:
        dd = tg - tk
        if 0 <= dd < 0.5: pulse = max(pulse, math.exp(-dd * 7))
    a = 1.0; de = tg - K["q_end"]
    if de > 0: a = max(0.0, 1 - de / 0.8)
    for x, y, s, sp in NUMS:
        yy_ = (y - tg * 50 * sp) % 700 + 720
        text(d, (x, yy_), s, 56, mix((20, 24, 40), (90, 110, 150), a) + (255,), BOLD)
    glove(d, W / 2, 1020, 1.6 * (1 + 0.06 * pulse), 1, col=mix((20, 24, 40), CREAM, 0.35 * a), cuff=mix((20, 24, 40), TEAL, 0.35 * a))
    return dict(hit=0.5 * pulse)

def s_logo(img, d, tg, k):
    dim(img, 0.88)
    fade = 1 - ease((tg - (END - 0.7)) / 0.7)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    sc = 1 + 0.15 * (1 - eout(k / 0.5)); g = tuple(int(c * fade) for c in GOLD)
    text(dl, (W / 2, 690), "MINDSET", int(150 * sc), g + (255,), BOLD)
    text(dl, (W / 2, 900), "24", int(300 * sc), g + (255,), BOLD)
    glow = L.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow); img.alpha_composite(glow); img.alpha_composite(L)
    d = ImageDraw.Draw(img)
    d.line((W / 2 - 300 * eout(k / 0.6), 1080, W / 2 + 300 * eout(k / 0.6), 1080), fill=g + (255,), width=4)
    return dict(fade=fade)

SCENES = {"hook": s_hook, "intro": s_intro, "havre": s_havre, "cherbourg": s_cherbourg, "chomage": s_chomage, "marseille": s_marseille,
          "gants": s_gants, "reims": s_reims, "europe": s_europe, "afrique": s_afrique, "coupes": s_coupes, "you": s_you,
          "abonne": s_abonne, "question": s_question, "logo": s_logo}
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
        a = cv2.warpAffine(a, Mx, (W, H), borderMode=cv2.BORDER_REFLECT)
    if flash > 0: a = a + flash * 255 * np.array([1.0, 0.95, 0.85], np.float32)
    a = a * VIGN
    g = GR.normal(0, 5, (H // 2, W // 2)).astype(np.float32)
    a = a + cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    return np.clip(a, 0, 255).astype(np.uint8)

def render_scene(tg, i):
    s = SCN[i]
    lvl = BGLEVEL.get(s["type"], 0.5)
    img = scenery(lvl); d = ImageDraw.Draw(img)
    R = SCENES[s["type"]](img, d, tg, tg - s["start"]) or {}
    if "bg" in R and abs(R["bg"] - lvl) > 0.04:
        img2 = scenery(R["bg"]); d2 = ImageDraw.Draw(img2); R = SCENES[s["type"]](img2, d2, tg, tg - s["start"]) or {}; img = img2
    return img, R

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


# =============================================================== STYLE « LIGNE » (overrides)
INK = (8, 16, 30); GRID = (26, 44, 70); GRID2 = (40, 64, 98)

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None, int(a[5]) if len(a) > 5 else 1)

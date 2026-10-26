# -*- coding: utf-8 -*-
"""Style « doc » : dossiers / archives (fond sombre chaud, papier crème, tampons rouges, or).
Histoires vraies racontées en 11 temps. Usage : python3 render_doc.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
import json, math, subprocess, sys, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
MED = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG = (17, 14, 12); CARD = (32, 27, 23); PAPER = (238, 228, 208); RED = (216, 48, 40); GOLD = (244, 184, 52)
GREY = (125, 114, 100); DARK = (60, 52, 45)

TJ = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "timing_voix.json"))
K = TJ["K"]; MK = TJ.get("marks", {}); SCN = TJ["scenes"]
SC = {s["type"]: s["start"] for s in SCN}
END = TJ["duration"]

_F = {}
def F(path, size):
    k = (path, size)
    if k not in _F: _F[k] = ImageFont.truetype(path, size)
    return _F[k]

def ease(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def eout(x): x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3
def since(t, k): return t - k

def text(d, xy, s, size, col, font=BOLD, anchor="mm", stroke=0, scol=(0, 0, 0)):
    d.text(xy, s, font=F(font, size), fill=col, anchor=anchor, stroke_width=stroke, stroke_fill=scol)

def typew(s, k, cps=28):
    if k <= 0: return ""
    return s[:int(k * cps) + 1]

def stamp(img, s, center, size, angle, k, col=RED, dur=0.14, box=True, font=BOLD):
    """tampon qui s'écrase (échelle 1.8 -> 1) puis reste."""
    if k <= 0: return 0.0
    f = F(font, size)
    dd = ImageDraw.Draw(Image.new("L", (4, 4)))
    l, t, r, b = dd.textbbox((0, 0), s, font=f)
    pad = int(size * 0.28)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    L = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    if box:
        d.rounded_rectangle((10, 10, 10 + w, 10 + h), int(size * 0.12), outline=col + (255,), width=max(4, size // 14))
    d.text((10 + pad - l, 10 + pad - t), s, font=f, fill=col + (255,))
    # usure du tampon
    a = np.asarray(L).copy()
    rng = np.random.default_rng(len(s) * 31 + size)
    noise = rng.random(a.shape[:2]) > 0.12
    a[..., 3] = (a[..., 3] * noise).astype(np.uint8)
    L = Image.fromarray(a).rotate(angle, resample=Image.BICUBIC, expand=True)
    sc = 1.0 + 0.8 * (1 - eout(k / dur))
    al = min(1.0, k / (dur * 0.6))
    if sc != 1.0: L = L.resize((int(L.width * sc), int(L.height * sc)), Image.BICUBIC)
    if al < 1:
        a = np.asarray(L).copy(); a[..., 3] = (a[..., 3] * al).astype(np.uint8); L = Image.fromarray(a)
    img.alpha_composite(L, (int(center[0] - L.width / 2), int(center[1] - L.height / 2)))
    return max(0.0, 1 - k / 0.25)   # impulsion d'impact

def card(img, d, title, num, k):
    """fiche dossier qui glisse depuis le bas."""
    y0 = 250 + 300 * (1 - eout(k / 0.35))
    d.rounded_rectangle((60, y0, W - 60, y0 + 1060), 28, fill=CARD, outline=DARK, width=3)
    d.rectangle((60, y0 + 110, W - 60, y0 + 113), fill=DARK)
    text(d, (100, y0 + 58), f"DOSSIER {num:02d}", 34, GREY, MONO, "lm")
    text(d, (W - 100, y0 + 58), typew(title, k - 0.1, 40), 50, PAPER, BOLD, "rm")
    # trombone
    d.rounded_rectangle((W - 190, y0 - 34, W - 150, y0 + 60), 18, outline=GREY, width=5)
    return y0

def rocket(d, x, y, s=1.0, col=PAPER, flame=0.0, t=0.0):
    pts = [(x, y - 120 * s), (x + 26 * s, y - 70 * s), (x + 26 * s, y + 40 * s), (x - 26 * s, y + 40 * s), (x - 26 * s, y - 70 * s)]
    d.polygon(pts, outline=col, width=5)
    d.polygon([(x - 26 * s, y + 10 * s), (x - 52 * s, y + 50 * s), (x - 26 * s, y + 40 * s)], outline=col, width=4)
    d.polygon([(x + 26 * s, y + 10 * s), (x + 52 * s, y + 50 * s), (x + 26 * s, y + 40 * s)], outline=col, width=4)
    d.ellipse((x - 10 * s, y - 60 * s, x + 10 * s, y - 40 * s), outline=col, width=4)
    if flame > 0:
        fl = (40 + 25 * math.sin(t * 40)) * s * flame
        d.polygon([(x - 16 * s, y + 42 * s), (x, y + 42 * s + fl), (x + 16 * s, y + 42 * s)], fill=GOLD)

def burst(d, x, y, k, n=14, r=140, col=RED, seed=0):
    if k <= 0 or k > 0.7: return
    rng = np.random.default_rng(seed)
    e = eout(k / 0.5); a = 1 - k / 0.7
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        r0, r1 = r * 0.3 * e, r * (0.6 + 0.6 * rng.random()) * e
        d.line((x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r1 * math.cos(ang), y + r1 * math.sin(ang)),
               fill=tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate(col)), width=6)

def ball(d, x, y, r, col=GOLD, rot=0.0):
    d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=7)
    pts = [(x + 0.42 * r * math.cos(rot + i * 2 * math.pi / 5), y + 0.42 * r * math.sin(rot + i * 2 * math.pi / 5)) for i in range(5)]
    d.polygon(pts, outline=col, width=5)
    for px, py in pts:
        ang = math.atan2(py - y, px - x)
        d.line((px, py, x + r * math.cos(ang), y + r * math.sin(ang)), fill=col, width=4)

def boot(d, x, y, s=1.0, col=PAPER):
    P = [(-150, -40), (-150, -150), (-60, -150), (-40, -60), (60, -40), (150, -10), (160, 30), (-150, 30)]
    d.polygon([(x + px * s, y + py * s) for px, py in P], outline=col, width=6)
    d.line((x - 150 * s, y + 5 * s, x + 158 * s, y + 5 * s), fill=col, width=4)
    for i in range(5):   # crampons
        d.line((x + (-120 + i * 60) * s, y + 30 * s, x + (-120 + i * 60) * s, y + 52 * s), fill=col, width=6)
    # déchirures
    d.line((x + 20 * s, y - 45 * s, x + 40 * s, y - 15 * s, x + 25 * s, y + 0 * s), fill=RED, width=5)
    d.line((x - 110 * s, y - 120 * s, x - 90 * s, y - 95 * s, x - 105 * s, y - 70 * s), fill=RED, width=5)
    for i in range(4):   # lacets
        d.line((x + (-55 + i * 22) * s, y - 70 * s, x + (-35 + i * 22) * s, y - 95 * s), fill=col, width=3)

def bubble(d, x, y, s, k, size=60):
    if k <= 0: return
    sc = eout(k / 0.15)
    f = F(BOLD, max(8, int(size * sc)))
    l, t, r, b = d.textbbox((x, y), s, font=f, anchor="mm")
    d.rounded_rectangle((l - 24, t - 16, r + 24, b + 16), 26, fill=PAPER)
    d.polygon([(x - 20, b + 14), (x + 6, b + 14), (x - 30, b + 50 * sc)], fill=PAPER)
    d.text((x, y), s, font=f, fill=RED, anchor="mm")

# --------------------------------------------------------------- scènes
RNG = np.random.default_rng(4)
DOLLARS = [(RNG.uniform(60, W - 60), RNG.uniform(0, H), RNG.uniform(60, 150), RNG.uniform(60, 160)) for _ in range(26)]

def s_hook(img, d, tg, k):
    for x, y0, sp, sz in DOLLARS:   # pluie de « $ » discrète : les riches
        y = (y0 + tg * sp * 3) % (H + 200) - 100
        text(d, (x, y), "$", int(sz), DARK, BOLD)
    cx, cy = W / 2, 760
    R = 230; ww = abs(math.cos(tg * 5.5)) * R
    d.ellipse((cx - ww, cy - R, cx + ww, cy + R), outline=GOLD, width=10, fill=(40, 32, 18))
    if ww > 60: text(d, (cx, cy), "?", int(260 * ww / R), GOLD, BOLD)
    kk = tg - K["hook"]
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 1150), "CHANCE ?", int(150 * sc), PAPER, BOLD, stroke=6)
        return dict(hit=max(0, 1 - kk / 0.25))
    return {}

def s_musk(img, d, tg, k):
    y0 = card(img, d, "ELON MUSK", 1, k)
    hit = 0.0
    k8 = tg - MK["y2008"]
    if k8 > 0: text(d, (W / 2, y0 + 230), "2008", int(120 + 30 * (1 - eout(k8 / 0.2))), GOLD, MONO)
    gy = y0 + 860
    d.line((120, gy + 45, W - 120, gy + 45), fill=GREY, width=4)
    t3 = MK["trois"] - 0.1
    for i, x in enumerate((280, 540, 800)):
        ks = tg - (t3 + i * 0.42)
        if ks < 0:
            rocket(d, x, gy, 0.9, DARK); continue
        up = min(1, ks / 0.32)
        yy = gy - 330 * eout(up)
        if ks < 0.32: rocket(d, x, yy, 0.9, PAPER, 1.0, tg)
        burst(d, x, gy - 330, ks - 0.32, seed=i)
        if ks > 0.32:
            hit = max(hit, stamp(img, f"ÉCHEC {i + 1}", (x, y0 + 400), 46, [-6, 4, -3][i], ks - 0.32))
            rocket(d, x, gy, 0.9, DARK)
    kr = tg - MK["ruine"]
    if kr > 0: hit = max(hit, stamp(img, "PRESQUE RUINÉ", (W / 2, y0 + 640), 88, -7, kr))
    return dict(hit=hit)

def s_ma(img, d, tg, k):
    y0 = card(img, d, "JACK MA", 2, k)
    hit = 0.0
    kk = tg - MK["kfc"] + 0.25
    if kk > 0:
        x0 = 140 + 40 * (1 - eout(kk / 0.25)); yy = y0 + 170
        d.rectangle((x0, yy, x0 + 380, yy + 470), fill=PAPER)
        text(d, (x0 + 30, yy + 50), "KFC", 64, BG, BOLD, "lm")
        text(d, (x0 + 30, yy + 120), "CANDIDATURE", 30, DARK, MONO, "lm")
        for j in range(5): d.line((x0 + 30, yy + 190 + j * 50, x0 + 350 - (j % 2) * 60, yy + 190 + j * 50), fill=GREY, width=4)
        text(d, (x0 + 30, yy + 440), "Nom : Jack Ma", 28, BG, MONO, "lm")
        hit = max(hit, stamp(img, "REFUSÉ", (x0 + 190, yy + 300), 70, 14, kk - 0.4))
    kd = tg - MK["dix"]
    for i in range(10):
        ki = kd - i * 0.09
        if ki <= 0: continue
        cx = 640 + (i % 2) * 190; cy = y0 + 200 + (i // 2) * 105
        d.rectangle((cx - 80, cy - 45, cx + 80, cy + 45), fill=PAPER, outline=DARK)
        text(d, (cx, cy - 18), "HARVARD", 26, BG, MONO)
        stamp(img, "NON", (cx + 10, cy + 14), 30, -10 + 4 * (i % 3), ki, dur=0.08)
    kh = tg - MK["harvard"]
    if kh > 0:
        hit = max(hit, stamp(img, "× 10", (W / 2 + 160, y0 + 840), 120, -5, kh, GOLD, box=False))
    return dict(hit=hit)

def s_mane(img, d, tg, k):
    y0 = card(img, d, "SADIO MANÉ", 3, k)
    hit = 0.0
    kv = tg - MK["village"] + 0.5
    A = (220, y0 + 400); B = (W - 230, y0 + 190)
    if kv > 0:
        p = eout(kv / 1.0)
        n = 40
        for i in range(int(n * p)):
            s0 = i / n
            x = A[0] + (B[0] - A[0]) * s0; y = A[1] + (B[1] - A[1]) * s0 - 120 * math.sin(math.pi * s0)
            if i % 2 == 0: d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=GOLD)
        d.ellipse((A[0] - 16, A[1] - 16, A[0] + 16, A[1] + 16), fill=PAPER)
        text(d, (A[0], A[1] + 60), "BAMBALI", 40, PAPER, MONO)
        if p > 0.9:
            d.ellipse((B[0] - 16, B[1] - 16, B[0] + 16, B[1] + 16), fill=GOLD)
            text(d, (B[0], B[1] - 55), "DAKAR", 44, GOLD, MONO)
    ke = tg - MK["essai"] + 0.1
    if ke > 0:
        s = 1.0 + 0.3 * (1 - eout(ke / 0.25))
        boot(d, W / 2, y0 + 830, 1.25 * s)
        text(d, (W / 2, y0 + 590), "1er ESSAI", 44, GREY, MONO)
    km = tg - MK["moque"]
    for i, (s, x, y) in enumerate((("HAHA", 230, 700), ("Avec ça ?", 800, 660), ("HAHA", 860, 960), ("HAHA", 230, 990))):
        bubble(d, x, y0 + y, s, km - i * 0.22, 50)
    kc = tg - MK["chaussures"]
    if kc > 0: hit = stamp(img, "MOQUÉ", (W / 2, y0 + 980), 80, 5, kc)
    return dict(hit=hit)

def s_stamps(img, d, tg, k):
    hit = 0.0
    for i, (txt, t0) in enumerate(TJ["words3d"]):
        hit = max(hit, stamp(img, txt, (W / 2 + [-30, 40, 0][i], [560, 840, 1120][i]), [150, 150, 120][i], [-8, 6, -4][i], tg - t0 + 0.06))
    return dict(hit=hit, shake=hit)

def s_graph(img, d, tg, k):
    # courbe : chute, chute, chute... puis remontée
    X0, X1, Y0, Y1 = 120, W - 120, 400, 1200
    d.line((X0, Y1, X1, Y1), fill=GREY, width=4); d.line((X0, Y0, X0, Y1), fill=GREY, width=4)
    pts = [(0, .45), (.12, .62), (.2, .5), (.3, .78), (.38, .62), (.5, .9), (.58, .74), (.68, .66), (.8, .38), (.9, .2), (1, .02)]
    P = [(X0 + x * (X1 - X0), Y0 + y * (Y1 - Y0)) for x, y in pts]
    p = min(1.0, max(0.0, (tg - SC["graph"]) / (K["build_end"] + 0.25 - SC["graph"])))
    n = p * (len(P) - 1); i = int(n)
    seg = P[:i + 1] + ([(P[i][0] + (P[i + 1][0] - P[i][0]) * (n - i), P[i][1] + (P[i + 1][1] - P[i][1]) * (n - i))] if i < len(P) - 1 else [])
    if len(seg) > 1: d.line(seg, fill=GOLD, width=10, joint="curve")
    for (j, lab) in ((1, "ÉCHEC"), (3, "REFUS"), (5, "MOQUERIE")):
        if n >= j: text(d, (P[j][0], P[j][1] + 60), lab, 36, RED, MONO); d.ellipse((P[j][0] - 12, P[j][1] - 12, P[j][0] + 12, P[j][1] + 12), fill=RED)
    if seg: d.ellipse((seg[-1][0] - 16, seg[-1][1] - 16, seg[-1][0] + 16, seg[-1][1] + 16), fill=GOLD)
    return {}

def s_slam(img, d, tg, k):
    kb = tg - K["boom"]
    hit = 0.0
    if kb > -0.08:
        kk = kb + 0.08
        for j in range(3):
            r = (kk - j * 0.1) * 1600
            if r > 0: d.ellipse((W / 2 - r, 760 - r, W / 2 + r, 760 + r), outline=RED, width=max(1, int(14 * max(0, 1 - r / 1400))))
        rng = np.random.default_rng(9)
        for i in range(16):   # fissures
            ang = rng.uniform(0, 2 * math.pi); L = 900 * eout(kk / 0.2)
            x, y = W / 2, 760; pts = [(x, y)]
            for s in range(5):
                ang += rng.uniform(-0.4, 0.4); x += L / 5 * math.cos(ang); y += L / 5 * math.sin(ang); pts.append((x, y))
            d.line(pts, fill=DARK, width=4)
        sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 760), "AUCUN", int(230 * sc), PAPER, BOLD, stroke=10, scol=RED)
        text(d, (W / 2, 1000), "N'A LÂCHÉ.", 90, GOLD, BOLD)
        hit = max(0, 1 - kk / 0.3)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=max(0, 0.9 - kb * 4) if kb > 0 else 0)

def s_wins(img, d, tg, k):
    hit = 0.0
    rows = [(SC["wins"] + 0.05, 430), (K["gate1"] - 0.05, 790), (K["gate2"] - 0.05, 1150)]
    for i, (t0, cy) in enumerate(rows):
        kk = tg - t0
        if kk <= 0: continue
        x0 = 80 + 900 * (1 - eout(kk / 0.25))
        d.rounded_rectangle((x0, cy - 160, x0 + 920, cy + 160), 24, fill=CARD, outline=GOLD, width=4)
        if i == 0:
            d.arc((x0 + 40, cy - 120, x0 + 420, cy + 260), 200, 340, fill=GREY, width=4)
            ang = math.radians(200 + 140 * eout(kk / 0.9))
            rx = x0 + 230 + 190 * math.cos(ang); ry = cy + 70 + 190 * math.sin(ang)
            rocket(d, rx, ry, 0.6, GOLD, 1.0, tg)
            text(d, (x0 + 480, cy - 50), "MUSK", 44, GREY, MONO, "lm")
            text(d, (x0 + 480, cy + 30), "ORBITE ✓", 74, GOLD, BOLD, "lm") if False else text(d, (x0 + 480, cy + 30), "ORBITE", 80, GOLD, BOLD, "lm")
        elif i == 1:
            text(d, (x0 + 60, cy - 60), "JACK MA", 44, GREY, MONO, "lm")
            text(d, (x0 + 60, cy + 30), "ALIBABA", 110, GOLD, BOLD, "lm")
        else:
            ball(d, x0 + 160, cy, 105, GOLD, tg * 2)
            text(d, (x0 + 320, cy - 60), "SADIO MANÉ", 44, GREY, MONO, "lm")
            text(d, (x0 + 320, cy + 20), "BALLON D'OR", 70, GOLD, BOLD, "lm")
            text(d, (x0 + 320, cy + 90), "AFRICAIN", 50, PAPER, BOLD, "lm")
        if kk > 0.2: hit = max(hit, max(0, 1 - (kk - 0.2) / 0.25))
        # coche
        if kk > 0.35:
            cx = x0 + 860; ck = eout((kk - 0.35) / 0.2)
            d.line([(cx - 30, cy - 110), (cx - 10, cy - 85), (cx - 10 + 40 * ck, cy - 85 - 50 * ck)], fill=GOLD, width=10)
    return dict(hit=hit * 0.8)

def s_you(img, d, tg, k):
    text(d, (W / 2, 330), "ET TOI ?", int(130 + 40 * (1 - eout(k / 0.2))), GOLD, BOLD)
    rows = [("MUSK", "3 fusées perdues"), ("JACK MA", "10 refus de Harvard"), ("MANÉ", "moqué au 1er essai")]
    t0 = K["sunrise"] - 0.2
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * 0.22)
        if kk <= 0: continue
        y = 560 + i * 150; x = 120 - 80 * (1 - eout(kk / 0.2))
        text(d, (x, y), a, 48, GREY, MONO, "lm"); text(d, (x + 330, y), b, 52, PAPER, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = 0.0
    if kn > -0.1:
        d.line((120, 990, W - 120, 990), fill=DARK, width=3)
        text(d, (120, 1080), "TOI", 56, RED, MONO, "lm")
        hit = stamp(img, "1 SEUL « NON »", (W / 2 + 120, 1080), 66, -4, kn + 0.1)
    return dict(hit=hit)

QS = [(RNG.uniform(80, W - 80), RNG.uniform(0, 700), RNG.uniform(-14, 14), RNG.uniform(0.2, 0.5)) for _ in range(9)]
def s_question(img, d, tg, k):
    pulse = 0.0
    for tk in TJ["q_pulses"]:
        dd = tg - tk
        if 0 <= dd < 0.5: pulse = max(pulse, math.exp(-dd * 7))
    a = 1.0
    de = tg - K["q_end"]
    if de > 0: a = max(0.0, 1 - de / 0.8)
    for i, (x, y, ang, sp) in enumerate(QS):   # vieux tampons qui flottent
        yy = y - tg * 40 * sp
        col = tuple(int(DARK[j] * a + BG[j] * (1 - a)) for j in range(3))
        text(d, (x, yy % 700 + 760), ["ÉCHEC", "REFUS", "NON"][i % 3], 50, col, BOLD)
    sz = int(620 * (1 + 0.08 * pulse))
    col = tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate((70, 58, 40)))
    text(d, (W / 2, 1000), "?", sz, col, BOLD)
    return dict(hit=0.5 * pulse)

def s_logo(img, d, tg, k):
    fade = 1 - ease((tg - (END - 0.7)) / 0.7)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    sc = 1 + 0.15 * (1 - eout(k / 0.5))
    g = tuple(int(c * fade) for c in GOLD)
    text(dl, (W / 2, 690), "MINDSET", int(150 * sc), g + (255,), BOLD)
    text(dl, (W / 2, 900), "24", int(300 * sc), g + (255,), BOLD)
    glow = L.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow); img.alpha_composite(glow); img.alpha_composite(L)
    d.line((W / 2 - 300 * eout(k / 0.6), 1080, W / 2 + 300 * eout(k / 0.6), 1080), fill=tuple(int(c * fade) for c in GOLD), width=4)
    return dict(fade=fade)

SCENES = {"hook": s_hook, "musk": s_musk, "ma": s_ma, "mane": s_mane, "stamps": s_stamps, "graph": s_graph, "slam": s_slam,
          "wins": s_wins, "you": s_you, "question": s_question, "logo": s_logo}

# --------------------------------------------------------------- textes (sous-titres, question, slogan)
def _core(wd): return "".join(ch for ch in wd.lower() if ch.isalnum() or ch in "éèàùêâîôûç")
KEYW = {_core(w) for w in TJ["keywords"]}

def sub_img(txt, size=54, stroke=7, maxw=960):
    font = F(BOLD, size)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
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
            dr.text((x, y), w, font=font, fill=(GOLD if kw else (255, 255, 255)) + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            x += d.textlength(w, font=font) + sp
    return im

def headline(lines, size=96, stroke=8):
    font = F(BOLD, size); lh = int(size * 1.12)
    im = Image.new("RGBA", (W, lh * len(lines) + stroke * 4), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for kk, (txt, col) in enumerate(lines):
        dr.text((W / 2, stroke * 2 + kk * lh + lh / 2), txt, font=font, fill=col + (255,), anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return im

def cta_img():
    font = F(BOLD, 56); txt = TJ["question"].get("cta", "ÉCRIS-LE EN COMMENTAIRE")
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10))); tw = d.textlength(txt, font=font)
    im = Image.new("RGBA", (W, 230), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.rounded_rectangle(((W - tw) / 2 - 34, 10, (W + tw) / 2 + 34, 104), 26, fill=PAPER + (255,))
    dr.text((W / 2, 57), txt, font=font, fill=(0, 0, 0, 255), anchor="mm")
    cx = W / 2; dr.polygon([(cx - 46, 130), (cx + 46, 130), (cx, 205)], fill=PAPER + (255,))
    return im

def paste(img, L, cy, alpha=1.0, scale=1.0):
    if alpha <= 0: return
    if scale != 1.0: L = L.resize((int(L.width * scale), int(L.height * scale)), Image.BILINEAR)
    if alpha < 1:
        a = np.asarray(L).copy(); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); L = Image.fromarray(a)
    img.alpha_composite(L, (int((W - L.width) / 2), int(cy - L.height / 2)))

# --------------------------------------------------------------- post-traitement
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.55 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)).clip(0.35, 1)[..., None]
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
        M = cv2.getRotationMatrix2D((W / 2, H / 2), shake * 0.8 * math.sin(tg * 40), zoom)
        M[0, 2] += dx; M[1, 2] += dy
        a = cv2.warpAffine(a, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if flash > 0: a = a + flash * 255 * np.array([1.0, 0.9, 0.8], np.float32)
    a = a * VIGN * (1 + 0.015 * math.sin(tg * 23))
    g = GR.normal(0, 7, (H // 2, W // 2)).astype(np.float32)
    a = a + cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    return np.clip(a, 0, 255).astype(np.uint8)

def render_scene(tg, i):
    s = SCN[i]
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    R = SCENES[s["type"]](img, d, tg, tg - s["start"]) or {}
    return img, R

def main(timing, out, t_from=0.0, t_to=None, every=1):
    subs = TJ["subs"]; simgs = [sub_img(s["text"]) for s in subs]
    Q = TJ["question"]
    H1 = headline([(l, (255, 255, 255)) for l in Q["lines"]]); H2 = headline([(Q["highlight"], GOLD)], 110)
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
        if cur > 0 and lt < XF:   # fondu enchaîné rapide depuis la scène précédente
            prev, _ = render_scene(tg, cur - 1)
            img = Image.blend(prev, img, ease(lt / XF))
        hit = R.get("hit", 0.0); shake = R.get("shake", 0.0) * 0.6 + 0.25 * hit
        zoom = 1.0 + 0.035 * min(1.0, lt / 4.0) + 0.03 * max(hit, punch(tg))
        # textes
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
                    paste(img, im, H * 0.80, min(1, (tg - s["start"]) / 0.06), pop)
        arr = post(np.asarray(img.convert("RGB")), tg, zoom, shake, R.get("flash", 0.0))
        if ff: ff.stdin.write(arr.tobytes())
        else: cv2.imwrite(f"{out}/f_{fi:04d}.png", cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        if n % 60 == 0: print(f"frame {fi} t={tg:.2f}s  {time.time() - t0:.0f}s écoulées", flush=True)
    if ff: ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None, int(a[5]) if len(a) > 5 else 1)

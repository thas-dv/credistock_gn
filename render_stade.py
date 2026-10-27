# -*- coding: utf-8 -*-
"""Style « stade » : stade de nuit (projecteurs, pelouse), joueur n°11 en silhouette (contour lumineux, maillot orange),
couleurs orange / blanc / vert. Histoires vraies de sportifs racontées en 11 temps.
Types : hook exil lemans stamps slam rise chelsea final you question logo ("marks" = temps de mots nommés).
Usage : python3 render_stade.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# --------------------------------------------------------------- stade (fonds pré-calculés)
LAMPS = [(150, 150), (930, 150), (330, 290), (750, 290)]
HOR = 760   # ligne d'horizon : haut de la pelouse

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR):   # ciel
        u = y / HOR; d.line((0, y, W, y), fill=mix(BG, NIGHT, u))
    rng = np.random.default_rng(2)
    # tribunes
    for row in range(14):
        y0 = 430 + row * 24
        d.rectangle((0, y0, W, y0 + 20), fill=mix((14, 22, 30), (26, 38, 50), lit * 0.8))
        for x in range(8, W, 14):
            if rng.random() < 0.75:
                c = [GREY, ORANGE, WHITE, GREEN][rng.integers(0, 4)] if rng.random() < 0.35 else (70, 80, 90)
                c = mix((18, 26, 34), c, 0.25 + 0.55 * lit)
                d.ellipse((x + rng.integers(-2, 3), y0 + 3, x + 7, y0 + 12), fill=c)
    # pelouse en perspective
    def X(xn, y):   # xn in [-1,1] -> écran
        u = (y - HOR) / (H - HOR); half = lerp(430, 1500, u)
        return W / 2 + xn * half
    for i in range(12):
        ya = HOR + (H - HOR) * (i / 12) ** 1.6; yb = HOR + (H - HOR) * ((i + 1) / 12) ** 1.6
        c = mix(PITCH if i % 2 else PITCH2, (8, 26, 18), 1 - lit)
        d.polygon([(X(-1.2, ya), ya), (X(1.2, ya), ya), (X(1.2, yb), yb), (X(-1.2, yb), yb)], fill=c)
    lc = mix((40, 70, 55), LINE, lit)
    d.line([(X(-1, HOR), HOR), (X(-1, H), H)], fill=lc, width=5); d.line([(X(1, HOR), HOR), (X(1, H), H)], fill=lc, width=5)
    d.line([(X(-1, HOR + 2), HOR + 2), (X(1, HOR + 2), HOR + 2)], fill=lc, width=4)
    yc = 1180; d.line([(X(-1, yc), yc), (X(1, yc), yc)], fill=lc, width=5)
    d.ellipse((W / 2 - 330, yc - 120, W / 2 + 330, yc + 120), outline=lc, width=5)
    # surface au fond
    yb = HOR + 70; d.line([(X(-0.45, HOR), HOR), (X(-0.45, yb), yb), (X(0.45, yb), yb), (X(0.45, HOR), HOR)], fill=lc, width=4)
    # pylônes + projecteurs
    for x, y in LAMPS:
        d.line((x, y + 40, x, HOR - 330 + (y - 150) * 0.5 + 330), fill=(40, 52, 62), width=8)
        d.rectangle((x - 70, y - 26, x + 70, y + 30), fill=(30, 36, 44))
        for i in range(4):
            for j in range(2):
                cx, cy = x - 52 + i * 35, y - 12 + j * 26
                d.ellipse((cx - 12, cy - 9, cx + 12, cy + 9), fill=mix((50, 56, 60), (255, 250, 230), lit))
    if lit > 0:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        for x, y in LAMPS:
            tx = W / 2 + (x - W / 2) * 0.2
            dl.polygon([(x - 60, y), (x + 60, y), (tx + 520, 1500), (tx - 520, 1500)], fill=(255, 248, 225, int(26 * lit)))
            dl.ellipse((x - 120, y - 80, x + 120, y + 80), fill=(255, 250, 235, int(70 * lit)))
        L = L.filter(ImageFilter.GaussianBlur(30))
        img.alpha_composite(L)
    return img

BG_DARK = make_bg(0.0); BG_LIT = make_bg(1.0)
_BGC = {}
def stadium(level):
    q = round(min(1, max(0, level)) * 20) / 20
    if q not in _BGC: _BGC[q] = Image.blend(BG_DARK, BG_LIT, q)
    return _BGC[q].copy()

def dim(img, a):
    if a <= 0: return
    img.alpha_composite(Image.new("RGBA", (W, H), BG + (int(255 * min(1, a)),)))

# --------------------------------------------------------------- joueur n°11 (silhouette, contour lumineux, maillot orange)
def _dir(a): a = math.radians(a); return (math.sin(a), math.cos(a))

POSES = {
    "stand": dict(t=0, la=(-12, 6), ra=(12, -6), ll=(-5, 0), rl=(5, 0)),
    "up":    dict(t=0, la=(-160, 10), ra=(160, -10), ll=(-8, 0), rl=(8, 0)),
    "kneel": dict(t=12, la=(-20, 40), ra=(30, -50), ll=(-80, 95), rl=(15, -10)),
    "lie":   dict(t=0, la=(-30, 20), ra=(40, -60), ll=(-8, 30), rl=(10, -70)),
    "kick":  dict(t=-10, la=(-70, 10), ra=(60, -10), ll=(-10, 5), rl=(70, -25)),
    "head":  dict(t=-25, la=(-60, -40), ra=(60, 40), ll=(-15, 30), rl=(20, -20)),
}
def run_pose(ph):
    s = math.sin(ph)
    return dict(t=8, la=(-35 * s, 60), ra=(35 * s, -60), ll=(30 * s, max(0, -50 * s)), rl=(-30 * s, max(0, 50 * s)))

def blend_pose(a, b, u):
    out = {}
    for k in a:
        if k == "t": out[k] = lerp(a[k], b[k], u)
        else: out[k] = (lerp(a[k][0], b[k][0], u), lerp(a[k][1], b[k][1], u))
    return out

def player(img, x, y, s, pose, rot=0.0, alpha=1.0, num="11", jersey=ORANGE, glow=1.0):
    """(x, y) = position des pieds au sol (pose debout). s = taille en px de l'unité (hauteur ≈ 1.45·s). rot en degrés."""
    if isinstance(pose, str): pose = POSES[pose]
    L = Image.new("RGBA", (int(4 * s), int(4 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ox, oy = 2 * s, 2.3 * s
    hip = (ox, oy - 0.0 * s)
    td = _dir(180 + pose["t"]); neck = (hip[0] + td[0] * 0.52 * s, hip[1] + td[1] * 0.52 * s)
    head = (neck[0] + td[0] * 0.17 * s, neck[1] + td[1] * 0.17 * s)
    def limb(root, a1, a2, l1, l2):
        d1 = _dir(a1 + pose["t"] * 0.3); j = (root[0] + d1[0] * l1 * s, root[1] + d1[1] * l1 * s)
        d2 = _dir(a1 + a2 + pose["t"] * 0.3); e = (j[0] + d2[0] * l2 * s, j[1] + d2[1] * l2 * s)
        return j, e
    sh = (neck[0] + td[0] * -0.04 * s, neck[1] + td[1] * -0.04 * s)
    la = limb(sh, *pose["la"], 0.27, 0.25); ra = limb(sh, *pose["ra"], 0.27, 0.25)
    ll = limb(hip, *pose["ll"], 0.36, 0.36); rl = limb(hip, *pose["rl"], 0.36, 0.36)
    wl, wa = 0.11 * s, 0.085 * s
    rim = mix(SIL, WHITE, 0.85 * glow)
    segs = [(hip, ll[0], wl), (ll[0], ll[1], wl * 0.85), (hip, rl[0], wl), (rl[0], rl[1], wl * 0.85),
            (sh, la[0], wa), (la[0], la[1], wa * 0.85), (sh, ra[0], wa), (ra[0], ra[1], wa * 0.85)]
    for p, q, w in segs:   # contour
        d.line((p, q), fill=rim, width=int(w + 8)); d.ellipse((q[0] - w / 2 - 4, q[1] - w / 2 - 4, q[0] + w / 2 + 4, q[1] + w / 2 + 4), fill=rim)
    d.line((hip, neck), fill=rim, width=int(0.25 * s + 8))
    r = 0.105 * s; d.ellipse((head[0] - r - 4, head[1] - r - 4, head[0] + r + 4, head[1] + r + 4), fill=rim)
    for p, q, w in segs:
        d.line((p, q), fill=SIL, width=int(w)); d.ellipse((q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2), fill=SIL)
    # chaussettes orange + short blanc + maillot
    for leg in (ll, rl):
        k, f = leg; m = (lerp(k[0], f[0], 0.45), lerp(k[1], f[1], 0.45))
        d.line((m, f), fill=jersey, width=int(wl * 0.8))
    for leg in (ll, rl):
        m = (lerp(hip[0], leg[0][0], 0.55), lerp(hip[1], leg[0][1], 0.55))
        d.line((hip, m), fill=WHITE, width=int(wl * 1.25))
    for arm in (la, ra):
        m = (lerp(sh[0], arm[0][0], 0.6), lerp(sh[1], arm[0][1], 0.6))
        d.line((sh, m), fill=jersey, width=int(wa * 1.3))
    d.line((hip, sh), fill=jersey, width=int(0.27 * s))
    d.ellipse((hip[0] - 0.135 * s, hip[1] - 0.1 * s, hip[0] + 0.135 * s, hip[1] + 0.06 * s), fill=jersey)
    d.ellipse((head[0] - r, head[1] - r, head[0] + r, head[1] + r), fill=SIL)
    if num:
        c = (lerp(hip[0], sh[0], 0.5), lerp(hip[1], sh[1], 0.5))
        Ln = Image.new("RGBA", (int(0.4 * s), int(0.4 * s)), (0, 0, 0, 0))
        ImageDraw.Draw(Ln).text((0.2 * s, 0.2 * s), num, font=F(BOLD, 0.2 * s), fill=WHITE + (255,), anchor="mm")
        Ln = Ln.rotate(-pose["t"], resample=Image.BICUBIC)
        L.alpha_composite(Ln, (int(c[0] - 0.2 * s), int(c[1] - 0.2 * s)))
    if rot: L = L.rotate(rot, resample=Image.BICUBIC, center=(ox, oy))
    if alpha < 1:
        a = np.asarray(L).copy(); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); L = Image.fromarray(a)
    # pieds au sol : la hanche est à 0.72·s au-dessus des pieds en pose debout
    drop = 0.6 * s * abs(math.sin(math.radians(rot)))   # couché : le corps repose au sol
    img.alpha_composite(L, (int(x - ox), int(y - oy - 0.72 * s + drop)))

def shadow(d, x, y, s, a=1.0):
    d.ellipse((x - 0.35 * s, y - 0.06 * s, x + 0.35 * s, y + 0.06 * s), fill=mix(PITCH, (0, 0, 0), 0.6 * a))

def ball(d, x, y, r, col=WHITE, rot=0.0, w=None):
    w = w or max(3, int(r / 7))
    d.ellipse((x - r, y - r, x + r, y + r), fill=(20, 24, 28), outline=col, width=w)
    pts = [(x + 0.42 * r * math.cos(rot + i * 2 * math.pi / 5), y + 0.42 * r * math.sin(rot + i * 2 * math.pi / 5)) for i in range(5)]
    d.polygon(pts, fill=col)
    for px, py in pts:
        ang = math.atan2(py - y, px - x)
        d.line((px, py, x + r * math.cos(ang), y + r * math.sin(ang)), fill=col, width=max(2, w - 1))

def burst(d, x, y, k, n=16, r=160, col=ORANGE, seed=0, w=7):
    if k <= 0 or k > 0.7: return
    rng = np.random.default_rng(seed); e = eout(k / 0.5); a = 1 - k / 0.7
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        r0, r1 = r * 0.3 * e, r * (0.6 + 0.6 * rng.random()) * e
        d.line((x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r1 * math.cos(ang), y + r1 * math.sin(ang)), fill=mix(BG, col, a), width=w)

def badge(d, x, y, s, k, col=ORANGE, r=110, tcol=BG):
    if k <= 0: return
    sc = 1 + 0.5 * (1 - eout(k / 0.18)); rr = r * sc
    d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)
    text(d, (x, y), s, fit(s, int(0.62 * rr), 1.7 * rr), tcol, BOLD)

def label(d, y, s, k, size=78, col=WHITE, sub=None, subcol=ORANGE):
    if k <= 0: return
    yy = y - 30 * (1 - eout(k / 0.3))
    text(d, (W / 2, yy), typew(s, k, 30), fit(s, size, 980), col, BOLD, stroke=5, scol=BG)
    if sub and k > 0.25: text(d, (W / 2, yy + size * 0.95), sub, fit(sub, 40, 960, MONO), subcol, MONO)

def M(name, default=None):
    return MK.get(name, default)

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    cx, cy, R = W / 2, 520, 200   # horloge qui tourne trop vite
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(14, 24, 36), outline=WHITE, width=10)
    for i in range(12):
        a = i * math.pi / 6
        d.line((cx + 0.82 * R * math.sin(a), cy - 0.82 * R * math.cos(a), cx + 0.94 * R * math.sin(a), cy - 0.94 * R * math.cos(a)), fill=WHITE, width=8)
    a1 = tg * 9; a2 = tg * 0.75
    d.line((cx, cy, cx + 0.8 * R * math.sin(a1), cy - 0.8 * R * math.cos(a1)), fill=ORANGE, width=9)
    d.line((cx, cy, cx + 0.55 * R * math.sin(a2), cy - 0.55 * R * math.cos(a2)), fill=WHITE, width=14)
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=ORANGE)
    shadow(d, W / 2, 1420, 300)
    player(img, W / 2, 1420, 300, "stand", glow=0.6 + 0.4 * ease(k / 1.2))
    kk = tg - K["hook"]
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 830), "TROP TARD ?", int(fit("TROP TARD ?", 150, 960) * sc), WHITE, BOLD, stroke=8, scol=RED)
        hit = max(0, 1 - kk / 0.25)
    return dict(hit=hit, bg=0.15 + 0.15 * (math.sin(tg * 13) > 0.6))

def s_exil(img, d, tg, k):
    dim(img, 0.55)
    label(d, 300, "DIDIER DROGBA", k, 100, WHITE, "CÔTE D'IVOIRE", ORANGE)
    A = (800, 1190); B = (300, 640)   # Abidjan -> France
    hit = 0.0
    ka = tg - M("abidjan", SC["exil"] + 1.5) + 0.3
    if ka > 0:
        d.ellipse((A[0] - 20, A[1] - 20, A[0] + 20, A[1] + 20), fill=ORANGE)
        text(d, (A[0], A[1] + 62), "ABIDJAN", 46, ORANGE, MONO)
        p = eout(ka / 1.6); n = 46
        for i in range(int(n * p)):
            s0 = i / n
            x = lerp(A[0], B[0], s0) - 160 * math.sin(math.pi * s0); y = lerp(A[1], B[1], s0)
            if i % 2 == 0: d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=WHITE)
        s0 = min(1, p); x = lerp(A[0], B[0], s0) - 160 * math.sin(math.pi * s0); y = lerp(A[1], B[1], s0)
        if 0 < p < 1:   # avion
            ang = math.atan2(B[1] - A[1], B[0] - A[0] - 160 * math.pi * math.cos(math.pi * s0))
            P = [(34, 0), (-22, -14), (-14, 0), (-22, 14)]
            d.polygon([(x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)) for px, py in P], fill=WHITE)
        if p > 0.95:
            d.ellipse((B[0] - 20, B[1] - 20, B[0] + 20, B[1] + 20), fill=BLUE)
            text(d, (B[0], B[1] - 60), "FRANCE", 50, WHITE, MONO)
    kc = tg - M("cinq", SC["exil"] + 0.8)
    if kc > 0:
        badge(d, 830, 900, "5 ANS", kc, ORANGE, 115)
        if kc < 0.25: hit = 1 - kc / 0.25
    player(img, 600, 1420, 170, "stand", num="", jersey=GREEN)   # l'enfant
    return dict(hit=hit, bg=0.2)

def s_lemans(img, d, tg, k):
    label(d, 300, "LE MANS", k, 110, WHITE, "DEUXIÈME DIVISION", GREY)
    hit = 0.0; flash = 0.0
    tb = M("blessure", SC["lemans"] + 1.0); kb = tg - tb
    if kb < 0:
        u = min(1, k / max(0.1, tb - SC["lemans"]))
        x = lerp(180, 520, u); player(img, x, 1420, 300, run_pose(tg * 11)); shadow(d, x, 1420, 300)
    else:
        u = eout(kb / 0.35)
        shadow(d, 560, 1420, 300)
        player(img, lerp(520, 560, u), 1420 - 0 * u, 300, blend_pose(run_pose(0), POSES["lie"], u), rot=lerp(0, 82, u))
        if kb < 0.3: hit = 1 - kb / 0.3; flash = 0.25 * (1 - kb / 0.3)
        # croix rouge « blessure »
        for j, tk in enumerate((tb, M("blessure2", tb + 0.8))):
            kj = tg - tk
            if kj > 0:
                cx, cy = [(330, 1150), (760, 1080)][j]
                sc = 1 + 0.6 * (1 - eout(kj / 0.15)); r = 60 * sc
                d.rectangle((cx - r, cy - r * 0.32, cx + r, cy + r * 0.32), fill=RED); d.rectangle((cx - r * 0.32, cy - r, cx + r * 0.32, cy + r), fill=RED)
                if j == 1 and kj < 0.25: hit = max(hit, 1 - kj / 0.25)
    kc = tg - M("contrat", SC["lemans"] + 2.5) + 0.15
    if kc > 0:   # contrat qui arrive
        x0 = 600 + 500 * (1 - eout(kc / 0.3)); y0 = 520
        d.rectangle((x0, y0, x0 + 380, y0 + 470), fill=WHITE)
        text(d, (x0 + 30, y0 + 55), "CONTRAT", 52, BG, BOLD, "lm"); text(d, (x0 + 30, y0 + 115), "PROFESSIONNEL", 30, DARK, MONO, "lm")
        for j in range(5): d.line((x0 + 30, y0 + 180 + j * 46, x0 + 350 - (j % 2) * 70, y0 + 180 + j * 46), fill=GREY, width=4)
        d.line((x0 + 200, y0 + 430, x0 + 350, y0 + 430), fill=DARK, width=3)
        kv = tg - M("vingtetun", SC["lemans"] + 3.5)
        hit = max(hit, stamp(img, "21 ANS", (x0 + 190, y0 + 310), 92, -9, kv, ORANGE))
    return dict(hit=hit, flash=flash, bg=0.7)

def s_stamps(img, d, tg, k):
    dim(img, 0.6)
    player(img, W / 2, 1460, 260, POSES["lie"], rot=82, alpha=0.5)
    hit = 0.0
    cols = [RED, ORANGE, WHITE]
    for i, (txt, t0) in enumerate(TJ["words3d"]):
        hit = max(hit, stamp(img, txt, (W / 2 + [-30, 40, 0][i], [520, 780, 1040][i]), [150, 130, 120][i], [-8, 6, -4][i], tg - t0 + 0.06, cols[i]))
    return dict(hit=hit, shake=hit, bg=0.25)

def s_slam(img, d, tg, k):
    kb = tg - K["boom"]
    T0 = SC["slam"]; T1 = K["boom"] - 0.1
    u = min(1, max(0, (tg - T0) / max(0.2, T1 - T0)))
    if u < 0.5: pose = blend_pose(POSES["lie"], POSES["kneel"], ease(u / 0.5)); rot = lerp(82, 0, ease(u / 0.5))
    else: pose = blend_pose(POSES["kneel"], POSES["stand"], ease((u - 0.5) / 0.5)); rot = 0
    hit = 0.0; flash = 0.0; bgl = 0.2
    if kb > -0.08:
        kk = kb + 0.08; bgl = 1.0
        pose = blend_pose(POSES["stand"], POSES["up"], eout(kk / 0.25))
        for j in range(3):
            r = (kk - j * 0.1) * 1700
            if r > 0: d.ellipse((W / 2 - r, 1300 - r * 0.35, W / 2 + r, 1300 + r * 0.35), outline=ORANGE, width=max(1, int(16 * max(0, 1 - r / 1500))))
        burst(d, W / 2, 1000, kk, 22, 520, WHITE, 3, 9)
        flash = max(0, 0.9 - kb * 4) if kb > 0 else 0
        hit = max(0, 1 - kk / 0.3)
    shadow(d, W / 2, 1440, 320)
    player(img, W / 2, 1440, 320, pose, rot=rot, glow=1.0)
    if kb > -0.08:
        kk = kb + 0.08; sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 330), "IL A", 90, ORANGE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 520), "REFUSÉ", int(fit("REFUSÉ", 230, 1000) * sc), WHITE, BOLD, stroke=10, scol=ORANGE)
        text(d, (W / 2, 700), "D'ABANDONNER.", 64, GOLD, BOLD, stroke=4, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

STEPS = [("LE MANS", 170, 1330, None), ("GUINGAMP", 540, 1130, "17 BUTS"), ("MARSEILLE", 900, 930, "19 BUTS")]
def s_rise(img, d, tg, k):
    hit = 0.0
    times = [SC["rise"], M("guingamp", SC["rise"]), K["gate1"]]
    for i, (name, x, y, goals) in enumerate(STEPS):
        kk = tg - (times[i] - 0.25)
        if kk <= 0 and i > 0: continue
        yy = y + 300 * (1 - eout(max(0, kk) / 0.3))
        d.rectangle((x - 170, yy, x + 170, 1700), fill=mix(DARK, (40, 60, 74), 0.5), outline=ORANGE if i == 2 else GREY, width=5)
        text(d, (x, yy + 60), name, fit(name, 48, 320), WHITE, BOLD)
        if goals and tg > K["gate2"] - 0.05:
            kg = tg - K["gate2"] + 0.05 + i * 0.12
            badge(d, x, yy + 190, goals, kg, ORANGE if i == 2 else GREEN, 92, BG)
            burst(d, x, yy - 260, kg, 14, 200, ORANGE, i)
            if kg < 0.25: hit = max(hit, 1 - kg / 0.25)
    # le joueur saute de marche en marche
    j = 0
    for i, t0 in enumerate(times):
        if tg >= t0: j = i
    if j == 0:
        x, y = STEPS[0][1], STEPS[0][2]; pose = run_pose(tg * 8) if False else "stand"
    else:
        u = min(1, (tg - times[j]) / 0.4)
        x0, y0 = STEPS[j - 1][1], STEPS[j - 1][2]; x1, y1 = STEPS[j][1], STEPS[j][2]
        x = lerp(x0, x1, ease(u)); y = lerp(y0, y1, ease(u)) - 180 * math.sin(math.pi * u)
        pose = blend_pose(POSES["kick"], POSES["stand"], u) if u < 1 else "stand"
        if 0.95 < u < 1: hit = max(hit, 0.6)
    if tg > K["gate2"]: pose = "up"
    player(img, x, y, 220, pose)
    label(d, 280, "IL MONTE.", k, 96, WHITE)
    return dict(hit=hit, bg=0.8)

def s_chelsea(img, d, tg, k):
    hit = 0.0
    label(d, 290, "CHELSEA", k, 130, WHITE, "LONDRES · 2004", (130, 170, 255))
    kb = tg - SC["chelsea"]
    badge(d, 860, 640, "26 ANS", kb - 0.3, BLUE, 105, WHITE)
    tm = M("millions", SC["chelsea"] + 2.0)
    u = eout(min(1, max(0, (tg - SC["chelsea"] - 0.4) / max(0.3, tm - SC["chelsea"] - 0.4))))
    val = int(24_000_000 * u)
    s = "£ " + f"{val:,}".replace(",", " ")
    sc = 1 + (0.25 * (1 - eout((tg - tm) / 0.25)) if tg > tm else 0)
    text(d, (W / 2, 900), s, int(fit("£ 24 000 000", 130, 980) * sc), GOLD if u >= 1 else WHITE, BOLD, stroke=6, scol=BG)
    if tg > tm:
        if tg - tm < 0.25: hit = 1 - (tg - tm) / 0.25
        text(d, (W / 2, 1030), "24 MILLIONS DE LIVRES", 48, GOLD, MONO)
    rng = np.random.default_rng(int(tg * 12))   # flashs photo
    for _ in range(5):
        if rng.random() < 0.5:
            x, y = rng.uniform(60, 700), rng.uniform(430, 760); r = rng.uniform(8, 22)
            d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE)
    shadow(d, W / 2, 1450, 270)
    player(img, W / 2, 1450, 270, "stand", jersey=BLUE)
    return dict(hit=hit, bg=0.9)

def goal_frame(d, cx, y, w, h, col=WHITE):
    d.line((cx - w / 2, y, cx - w / 2, y - h, cx + w / 2, y - h, cx + w / 2, y), fill=col, width=10)
    for i in range(1, 12):
        x = cx - w / 2 + w * i / 12; d.line((x, y - h, x + (x - cx) * 0.08, y - 12), fill=mix(BG, col, 0.35), width=2)
    for j in range(1, 6):
        yy = y - h + h * j / 6; d.line((cx - w / 2, yy, cx + w / 2, yy), fill=mix(BG, col, 0.35), width=2)

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def s_final(img, d, tg, k):
    hit = 0.0; flash = 0.0
    te = M("egalise", SC["final"] + 2.5); tt = M("tir", te + 2.0); tv = M("victoire", tt + 1.0)
    # tableau d'affichage
    d.rounded_rectangle((170, 200, W - 170, 420), 24, fill=(10, 14, 20), outline=GREY, width=4)
    text(d, (W / 2, 250), "FINALE 2012", 44, GOLD, MONO)
    mn = 88 if tg > te - 0.6 else 80 + int(8 * ease((tg - SC["final"]) / max(0.5, te - 0.6 - SC["final"])))
    text(d, (300, 345), f"{mn}'", 74, ORANGE, MONO)
    score = "0 - 1" if tg < te else "1 - 1"
    text(d, (W / 2 + 90, 345), score, 96, WHITE, BOLD)
    goal_frame(d, W / 2, 1000, 760, 330)
    # tête à la 88e puis tir au but
    if tg < tt - 0.3:
        px, pose = 380, "head" if abs(tg - te) < 0.5 else "stand"
        player(img, px, 1450, 260, pose)
        kb = tg - (te - 0.25)
        if 0 < kb < 0.45:
            u = kb / 0.45; bx, by = lerp(470, W / 2 + 200, u), lerp(1040, 760, u) - 60 * math.sin(math.pi * u)
            ball(d, bx, by, 34, WHITE, tg * 8)
        elif kb >= 0.45:
            ball(d, W / 2 + 200, 960, 34, WHITE, 0)
            if kb < 0.75: hit = 1 - (kb - 0.45) / 0.3; flash = 0.3 * hit
            if kb < 1.6: text(d, (W / 2, 620), "BUT !", int(140 * (1 + 0.3 * (1 - eout((kb - 0.45) / 0.15)))), ORANGE, BOLD, stroke=6, scol=BG)
    else:
        kt = tg - (tt - 0.3)
        if tg < tv - 0.25: text(d, (W / 2, 560), "TIRS AU BUT", 64, WHITE, BOLD)
        d.ellipse((W / 2 - 10, 1300 - 6, W / 2 + 10, 1300 + 6), fill=WHITE)
        if tg < tv - 0.25:
            player(img, W / 2 - 150, 1460, 260, blend_pose(POSES["stand"], POSES["kick"], ease(kt / 0.4)))
            if kt > 0.4:
                u = min(1, (kt - 0.4) / 0.35); ball(d, lerp(W / 2, W / 2 - 240, u), lerp(1290, 790, u), lerp(36, 26, u), WHITE, tg * 9)
            else: ball(d, W / 2, 1290, 36, WHITE, 0)
        else:
            kv = tg - (tv - 0.25)
            ball(d, W / 2 - 240, 960, 26, WHITE, 0)
            for x0, y0, c in CONF:
                y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
                if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[ORANGE, WHITE, GREEN][c])
            cx, cy = W / 2, 1020 - 160 * eout(kv / 0.5)   # trophée générique
            d.polygon([(cx - 120, cy - 230), (cx + 120, cy - 230), (cx + 80, cy - 60), (cx + 25, cy - 20), (cx + 25, cy + 50),
                       (cx + 80, cy + 90), (cx - 80, cy + 90), (cx - 25, cy + 50), (cx - 25, cy - 20), (cx - 80, cy - 60)], fill=GOLD)
            d.arc((cx - 190, cy - 230, cx - 70, cy - 90), 90, 270, fill=GOLD, width=14); d.arc((cx + 70, cy - 230, cx + 190, cy - 90), 270, 90, fill=GOLD, width=14)
            text(d, (W / 2, 540), "VICTOIRE", int(fit("VICTOIRE", 130, 960) * (1 + 0.3 * (1 - eout(kv / 0.15)))), GOLD, BOLD, stroke=6, scol=BG)
            player(img, W / 2, 1480, 250, "up")
            if kv < 0.3: hit = 1 - kv / 0.3; flash = 0.5 * hit
    return dict(hit=hit, flash=flash, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.5)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=6, scol=BG)
    rows = [("5 ANS", "quitte Abidjan"), ("21 ANS", "1er contrat pro"), ("26 ANS", "Chelsea"), ("34 ANS", "champion d'Europe")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 130 - 80 * (1 - eout(kk / 0.2))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD if i == 3 else ORANGE)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 50, y), a, 50, GOLD if i == 3 else WHITE, MONO, "lm"); text(d, (x + 300, y), b, 50, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "JAMAIS TROP TARD", (W / 2, 1150), 90, -5, kn + 0.05, GOLD) if kn > -0.05 else 0.0
    return dict(hit=hit, bg=0.4)

NUMS = [(np.random.default_rng(i).uniform(90, W - 90), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["21", "26", "34", "18", "25", "30", "40", "17", "28", "35"])]
def s_question(img, d, tg, k):
    dim(img, 0.6)
    pulse = 0.0
    for tk in TJ["q_pulses"]:
        dd = tg - tk
        if 0 <= dd < 0.5: pulse = max(pulse, math.exp(-dd * 7))
    a = 1.0; de = tg - K["q_end"]
    if de > 0: a = max(0.0, 1 - de / 0.8)
    for x, y, s, sp in NUMS:
        yy = (y - tg * 50 * sp) % 700 + 720
        text(d, (x, yy), s, 70, mix(BG, (60, 74, 86), a), BOLD)
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (90, 60, 30), a), BOLD)
    return dict(hit=0.5 * pulse, bg=0.1)

def s_logo(img, d, tg, k):
    dim(img, 0.85)
    fade = 1 - ease((tg - (END - 0.7)) / 0.7)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    sc = 1 + 0.15 * (1 - eout(k / 0.5)); g = tuple(int(c * fade) for c in GOLD)
    text(dl, (W / 2, 690), "MINDSET", int(150 * sc), g + (255,), BOLD)
    text(dl, (W / 2, 900), "24", int(300 * sc), g + (255,), BOLD)
    glow = L.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow); img.alpha_composite(glow); img.alpha_composite(L)
    d.line((W / 2 - 300 * eout(k / 0.6), 1080, W / 2 + 300 * eout(k / 0.6), 1080), fill=g, width=4)
    return dict(fade=fade, bg=0.0)

SCENES = {"hook": s_hook, "exil": s_exil, "lemans": s_lemans, "stamps": s_stamps, "slam": s_slam, "rise": s_rise,
          "chelsea": s_chelsea, "final": s_final, "you": s_you, "question": s_question, "logo": s_logo}
BGLEVEL = {"hook": 0.2, "exil": 0.2, "lemans": 0.7, "stamps": 0.25, "slam": 0.2, "rise": 0.8, "chelsea": 0.9, "final": 1.0,
           "you": 0.4, "question": 0.1, "logo": 0.0}

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
    if s["type"] == "slam" and tg > K["boom"] - 0.08: lvl = 1.0
    if s["type"] == "hook": lvl = 0.15 + 0.2 * (math.sin(tg * 13) > 0.6)
    img = stadium(lvl); d = ImageDraw.Draw(img)
    R = SCENES[s["type"]](img, d, tg, tg - s["start"]) or {}
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

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None, int(a[5]) if len(a) > 5 else 1)

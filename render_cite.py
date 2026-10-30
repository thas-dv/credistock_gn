# -*- coding: utf-8 -*-
"""Style « cité » : quartier d immeubles la nuit, city-stade en béton, lampadaires -> projecteurs blancs et or ; joueur en silhouette
générique (maillot bleu, sans numéro). Types : hook cite frail quimper havre stamps slam england champion award giant you question logo.
Scènes propres à l histoire du 30/10 (ailier franco-algérien) sauf stamps/slam/you/question/logo.
Usage : python3 render_cite.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# palette « cité » : quartier d'immeubles la nuit (violet / sodium) -> projecteurs blancs et or
NIGHT = (12, 9, 30); SKY2 = (40, 22, 70); DUSK = (120, 60, 120); DUSK2 = (230, 120, 110)
CONC = (34, 34, 44); CONC2 = (70, 72, 86); BLD = (18, 16, 30); BLD2 = (28, 24, 44)
SODIUM = (255, 170, 70); CYAN = (50, 220, 235)
ORANGE = CYAN; PITCH = CONC
HOR = 1020
JER = (40, 110, 230)

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        night = mix(NIGHT, SKY2, u); day = mix(DUSK, DUSK2, u ** 1.4)
        d.line((0, y, W, y), fill=mix(night, day, lit * 0.8))
    rng = np.random.default_rng(7)
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(0, HOR * 0.5); r = rng.uniform(1, 2.6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix(mix(NIGHT, SKY2, y / HOR), WHITE, (0.3 + 0.5 * rng.random()) * (1 - lit)))
    # immeubles (barres et tours)
    rng = np.random.default_rng(11)
    for layer, col in [(0, BLD2), (1, BLD)]:
        x = -40 + layer * 60
        while x < W + 40:
            w = rng.uniform(150, 260) if layer == 0 else rng.uniform(200, 330)
            h = rng.uniform(380, 640) if layer == 0 else rng.uniform(260, 470)
            top = HOR - h + (layer * 40)
            d.rectangle((x, top, x + w, HOR + 40), fill=mix(col, (60, 50, 80), lit * 0.5))
            for wy in np.arange(top + 24, HOR + 10, 44):
                for wx in np.arange(x + 16, x + w - 26, 38):
                    on = rng.random() < (0.28 + 0.5 * lit)
                    c = mix((255, 200, 120), (255, 236, 190), rng.random()) if on else mix(col, (0, 0, 0), 0.3)
                    if layer == 0 and on: c = mix(c, col, 0.45)
                    d.rectangle((wx, wy, wx + 20, wy + 24), fill=c)
            x += w + rng.uniform(10, 50)
    # sol : terrain en béton (city-stade) en perspective
    d.rectangle((0, HOR + 40, W, H), fill=mix(CONC, CONC2, lit))
    def X(xn, y):
        u = (y - HOR - 40) / (H - HOR - 40); return W / 2 + xn * lerp(420, 900, u)
    lc = mix((150, 150, 165), WHITE, lit)
    y0 = HOR + 40
    d.line([(X(-1, y0), y0), (X(-1, H), H)], fill=lc, width=6); d.line([(X(1, y0), y0), (X(1, H), H)], fill=lc, width=6)
    ym = y0 + (H - y0) * 0.42
    d.line([(X(-1, ym), ym), (X(1, ym), ym)], fill=lc, width=6)
    d.ellipse((W / 2 - 170, ym - 60, W / 2 + 170, ym + 60), outline=lc, width=6)
    # grillage
    fc = mix((60, 60, 80), (150, 150, 170), lit)
    d.line((0, HOR - 160, W, HOR - 160), fill=fc, width=6)
    for x in range(0, W + 1, 180): d.line((x, HOR - 160, x, HOR + 40), fill=fc, width=8)
    for x in range(-200, W + 200, 46):
        d.line((x, HOR - 160, x + 200, HOR + 40), fill=fc, width=1)
        d.line((x + 200, HOR - 160, x, HOR + 40), fill=fc, width=1)
    # lampadaires / projecteurs
    for x in (90, W - 90):
        d.line((x, HOR + 60, x, 560), fill=(50, 50, 60), width=12)
        d.rectangle((x - 50, 540, x + 50, 570), fill=mix(SODIUM, WHITE, lit))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for x in (90, W - 90):
        c = mix(SODIUM, (255, 255, 240), lit)
        dl.polygon([(x - 40, 570), (x + 40, 570), (W / 2 + (x - W / 2) * 0.1 + 320, H), (W / 2 + (x - W / 2) * 0.1 - 320, H)], fill=c + (int(36 + 40 * lit),))
        dl.ellipse((x - 120, 440, x + 120, 680), fill=c + (int(90 + 80 * lit),))
    L = L.filter(ImageFilter.GaussianBlur(40)); img.alpha_composite(L)
    return img

BG_DARK = make_bg(0.0); BG_LIT = make_bg(1.0)
_BGC = {}
def scenery(level):
    q = round(min(1, max(0, level)) * 20) / 20
    if q not in _BGC: _BGC[q] = Image.blend(BG_DARK, BG_LIT, q)
    return _BGC[q].copy()

def dim(img, a):
    if a <= 0: return
    img.alpha_composite(Image.new("RGBA", (W, H), BG + (int(255 * min(1, a)),)))

POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-25, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))

def P(img, x, y, s, pose, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER)
    player(img, x, y, s, pose, **kw)

def trophy(d, cx, cy, s=1.0, col=GOLD):
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.polygon([q(-120, -230), q(120, -230), q(80, -60), q(25, -20), q(25, 50), q(80, 90), q(-80, 90), q(-25, 50), q(-25, -20), q(-80, -60)], fill=col)
    d.arc((cx - 190 * s, cy - 230 * s, cx - 70 * s, cy - 90 * s), 90, 270, fill=col, width=int(14 * s))
    d.arc((cx + 70 * s, cy - 230 * s, cx + 190 * s, cy - 90 * s), 270, 90, fill=col, width=int(14 * s))

def star(d, cx, cy, r, col=GOLD):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)

def scout(d, x, y, s, turned, col=(14, 14, 20)):
    """recruteur générique (silhouette, bloc-notes) ; turned 0..1 = se détourne."""
    sx = 1 - 2 * ease(turned)
    d.rounded_rectangle((x - 45 * s, y - 230 * s, x + 45 * s, y - 60 * s), int(20 * s), fill=col)
    d.ellipse((x - 32 * s, y - 300 * s, x + 32 * s, y - 236 * s), fill=col)
    d.rectangle((x - 34 * s, y - 60 * s, x - 8 * s, y), fill=col); d.rectangle((x + 8 * s, y - 60 * s, x + 34 * s, y), fill=col)
    if sx > -0.2:
        xa, xb = sorted((x + 30 * s * sx, x + 80 * s * sx)); d.rectangle((xa, y - 200 * s, xb, y - 130 * s), fill=(220, 220, 210))

def ladder(d, tg, level_k, focus, lit=0.0):
    """pyramide des divisions : 1 (haut) .. 4 (bas) ; focus = indice surligné."""
    labs = ["1re DIVISION", "2e DIVISION", "3e DIVISION", "4e DIVISION"]
    for i, lab in enumerate(labs):
        y = 440 + i * 150; w = 420 + i * 120
        on = (i == focus)
        d.rounded_rectangle((W / 2 - w / 2, y, W / 2 + w / 2, y + 120), 18, fill=CYAN if on else (34, 30, 54), outline=WHITE if on else (80, 76, 110), width=4)
        text(d, (W / 2, y + 60), lab, 52, BG if on else (170, 166, 196), BOLD)
    return 440 + focus * 150 + 60

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    jig = math.sin(tg * 9)
    P(img, W / 2, 1640, 300, blend_pose(POSES["stand"], POSES["kick"], 0.5 + 0.5 * jig)); shadow(d, W / 2, 1640, 300)
    ball(d, W / 2 + 90, 1380 - 160 * abs(math.sin(tg * 4.5)), 34, WHITE, tg * 6)
    kk = tg - K["hook"]
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 330), "PAS ASSEZ", int(fit("PAS ASSEZ", 120, 960) * sc), WHITE, BOLD, stroke=8, scol=RED)
        text(d, (W / 2, 480), "FORT ?", int(fit("FORT ?", 170, 960) * sc), WHITE, BOLD, stroke=8, scol=RED)
        hit = max(0, 1 - kk / 0.25)
    return dict(hit=hit)

def s_cite(img, d, tg, k):
    hit = 0.0
    label(d, 300, "PRÈS DE PARIS", tg - M("paris", SC["cite"] + 1) + 0.2, 96, WHITE, "UN QUARTIER D'IMMEUBLES", CYAN) if tg > M("paris", 0) - 0.2 else None
    kj = tg - M("jours", 99) + 0.2
    if kj > 0:
        n = min(365, int(eout(kj / 1.2) * 365))
        text(d, (W / 2, 640), f"JOUR {n}", 110, GOLD, BOLD, stroke=6, scol=BG)
        if kj < 0.3: hit = 1 - kj / 0.3
    x = W / 2 + 260 * math.sin(tg * 1.3)
    P(img, x, 1620, 280, run_pose(tg * 10)); shadow(d, x, 1620, 280)
    ball(d, x + 110 * math.cos(tg * 1.3), 1610, 30, WHITE, tg * 9)
    ki = tg - M("immeubles", 99) + 0.1
    if ki > 0: hit = max(hit, stamp(img, "EN BAS DES IMMEUBLES", (W / 2, 800), 80, -4, ki, CYAN))
    return dict(hit=hit, bg=0.08)

def s_frail(img, d, tg, k):
    dim(img, 0.3)
    hit = 0.0
    turned = ease((tg - M("peine", SC["frail"] + 1)) / 0.6) if tg > M("peine", 99) - 0.3 else 0.0
    for i, x in enumerate([200, 880]):
        scout(d, x, 1500, 1.15, turned)
    P(img, W / 2, 1560, 250, "stand", alpha=0.9); shadow(d, W / 2, 1560, 250)
    if tg < M("frele", 99):
        label(d, 320, "LES RECRUTEURS ?", k, 88, WHITE)
    for txt, mk, xy, ang, col in [("TROP FRÊLE", "frele", (W / 2, 380), -7, RED), ("TROP FIN", "fin", (W / 2 - 60, 610), 6, RED),
                                  ("PAS ASSEZ COSTAUD", "costaud", (W / 2, 840), -4, RED)]:
        hit = max(hit, stamp(img, txt, xy, 120, ang, tg - M(mk, 99) + 0.05, col))
    return dict(hit=hit, bg=0.05)

def s_quimper(img, d, tg, k):
    dim(img, 0.5)
    hit = 0.0
    k18 = tg - M("dixhuit", SC["quimper"] + 0.3) + 0.1
    if k18 > 0: badge(d, 200, 300, "18 ANS", k18, GOLD, 105); hit = max(hit, 1 - k18 / 0.25) if k18 < 0.25 else hit
    ka = tg - M("amateurs", 99) + 0.1
    if ka > 0: text(d, (640, 300), "AMATEUR", int(fit("AMATEUR", 110, 640) * (1 + 0.25 * (1 - eout(ka / 0.2)))), WHITE, BOLD, stroke=6, scol=BG)
    kd = tg - M("quatrieme", 99) + 0.15
    if kd > 0:
        y = ladder(d, tg, kd, 3)
        P(img, W / 2 + 330, y + 70, 120, "stand")
        if kd < 0.3: hit = max(hit, 1 - kd / 0.3)
    else:
        P(img, W / 2, 1560, 260, run_pose(tg * 8)); shadow(d, W / 2, 1560, 260)
    return dict(hit=hit, bg=0.0)

def s_havre(img, d, tg, k):
    dim(img, 0.5)
    hit = 0.0
    kr = tg - M("reserve", SC["havre"] + 1) + 0.1
    k2 = tg - M("deuxieme", 99) + 0.1
    focus = 1 if k2 > 0 else 3
    y = ladder(d, tg, k, focus)
    py = y + 70 if k2 > 0 else 440 + 3 * 150 + 130
    if k2 > 0 and k2 < 0.5: py = lerp(440 + 3 * 150 + 130, y + 70, eout(k2 / 0.5))
    P(img, W / 2 + (300 if k2 <= 0 else lerp(330, 270, ease(k2 / 0.5))), py, 120, run_pose(tg * 9) if 0 < k2 < 0.5 else "stand")
    label(d, 300, "L'ANNÉE SUIVANTE", k, 84, WHITE)
    if kr > 0 and k2 <= 0: hit = stamp(img, "RÉSERVE", (W / 2, 1180), 130, -5, kr, CYAN)
    if 0 < k2 < 0.3: hit = 1 - k2 / 0.3
    return dict(hit=hit, bg=0.0)

def s_stamps(img, d, tg, k):
    dim(img, 0.5)
    d.rectangle((W / 2 - 300, 1560, W / 2 + 300, 1600), fill=(70, 70, 84)); d.rectangle((W / 2 - 280, 1600, W / 2 + 280, 1720), fill=(44, 44, 56))
    P(img, W / 2 - 40, 1560 + 0.72 * 230 - 30, 230, "sit", alpha=0.75)
    hit = 0.0; cols = [RED, WHITE, RED]
    for i, (txt, t0) in enumerate(TJ["words3d"]):
        hit = max(hit, stamp(img, txt, (W / 2 + [-30, 40, 0][i], [420, 680, 940][i]), [150, 140, 150][i], [-8, 6, -4][i], tg - t0 + 0.06, cols[i]))
    return dict(hit=hit, shake=hit, bg=0.0)

def s_slam(img, d, tg, k):
    kb = tg - K["boom"]
    T0 = SC["slam"]; T1 = K["boom"] - 0.1
    u = min(1, max(0, (tg - T0) / max(0.2, T1 - T0)))
    if tg < K["boom"] - 0.08: dim(img, 0.4 * (1 - u))
    pose = blend_pose(POSES["sad"], POSES["stand"], ease(u))
    hit = 0.0; flash = 0.0; bgl = 0.1 + 0.2 * u
    if kb > -0.08:
        kk = kb + 0.08; bgl = 0.75
        pose = blend_pose(POSES["stand"], POSES["up"], eout(kk / 0.25))
        for j in range(3):
            r = (kk - j * 0.1) * 1700
            if r > 0: d.ellipse((W / 2 - r, 1450 - r * 0.35, W / 2 + r, 1450 + r * 0.35), outline=CYAN, width=max(1, int(16 * max(0, 1 - r / 1500))))
        burst(d, W / 2, 1100, kk, 22, 520, WHITE, 3, 9)
        flash = max(0, 0.9 - kb * 4) if kb > 0 else 0
        hit = max(0, 1 - kk / 0.3)
    shadow(d, W / 2, 1600, 320)
    P(img, W / 2, 1600, 320, pose, glow=1.0)
    if kb > -0.08:
        kk = kb + 0.08; sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 330), "IL A", 90, CYAN, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 520), "CONTINUÉ.", int(fit("CONTINUÉ.", 220, 1000) * sc), WHITE, BOLD, stroke=10, scol=CYAN)
    else:
        text(d, (W / 2, 420), typew("TOUT LÂCHER ?", max(0, tg - K["build_start"] + 0.2), 20), 100, GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_england(img, d, tg, k):
    hit = 0.0
    t14 = M("d2014", SC["england"] + 0.3)
    hit = max(hit, stamp(img, "2014", (300, 300), 150, -6, tg - t14 + 0.05, GOLD))
    k22 = tg - M("vingtdeux", 99) + 0.1
    if k22 > 0: badge(d, 800, 310, "22 ANS", k22, CYAN, 105)
    kg = tg - K["gate1"] + 0.15
    if kg <= 0:
        ka = tg - M("anglaise", 99) + 0.2
        if ka > 0: label(d, 560, "ANGLETERRE", ka, 100, WHITE, "2e DIVISION", CYAN)
        kp = tg - M("prix", 99) + 0.05
        if kp > 0:
            hit = max(hit, stamp(img, "PETIT PRIX", (W / 2, 820), 130, -5, kp, RED))
        P(img, W / 2, 1600, 280, "stand"); shadow(d, W / 2, 1600, 280)
    else:
        for txt, tk, y in [("IL TRAVAILLE.", K["gate1"], 560), ("IL DRIBBLE.", M("dribble", K["gate1"] + 0.6), 690), ("IL MARQUE.", K["gate2"], 820)]:
            kk = tg - tk + 0.15
            if kk > 0:
                text(d, (W / 2, y - 20 * (1 - eout(kk / 0.25))), txt, 96, GOLD if y == 820 else WHITE, BOLD, stroke=6, scol=BG)
                if kk < 0.3: hit = max(hit, 1 - kk / 0.3)
        km = tg - K["gate2"]
        P(img, W / 2, 1640, 300, run_pose(tg * 10) if km < 0 else blend_pose(POSES["kick"], POSES["up"], min(1, km / 0.5)))
        if km > 0:
            u = min(1, km / 0.5); ball(d, lerp(W / 2 + 150, W / 2 + 40, u), lerp(1600, 1050, u), lerp(40, 18, u), WHITE, tg * 9)
            burst(d, W / 2 + 40, 1050, km - 0.5, 16, 200, GOLD, 2)
    return dict(hit=hit, bg=0.35)

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def confetti(d, kv):
    for x0, y0, c in CONF:
        y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[CYAN, WHITE, GOLD][c])

def s_champion(img, d, tg, k):
    hit = 0.0; flash = 0.0
    t16 = M("d2016", SC["champion"] + 0.2)
    hit = max(hit, stamp(img, "2016", (W / 2, 300), 160, -5, tg - t16 + 0.05, GOLD))
    tp = M("pourtant", 99); tc = M("champion", 99)
    if tg < tp:
        kn = tg - M("personne", 99) + 0.1
        if kn > 0: text(d, (W / 2, 560), "PRESQUE PERSONNE", fit("PRESQUE PERSONNE", 92, 980), WHITE, BOLD, stroke=6, scol=BG); text(d, (W / 2, 670), "N'Y CROIT", 92, GREY, BOLD, stroke=6, scol=BG)
        P(img, W / 2, 1640, 280, "stand")
    else:
        kc = tg - tc + 0.15
        if kc > 0:
            trophy(d, W / 2, 1000, 1.3 * (1 + 0.25 * (1 - eout(kc / 0.2))))
            text(d, (W / 2, 560), "CHAMPION", int(fit("CHAMPION", 150, 980) * (1 + 0.3 * (1 - eout(kc / 0.2)))), GOLD, BOLD, stroke=8, scol=BG)
            text(d, (W / 2, 690), "D'ANGLETERRE", 90, WHITE, BOLD, stroke=6, scol=BG)
            confetti(d, kc)
            if kc < 0.3: hit = 1 - kc / 0.3; flash = 0.35 * (1 - kc / 0.3)
        else:
            text(d, (W / 2, 600), "ET POURTANT…", 100, WHITE, BOLD, stroke=6, scol=BG)
        P(img, W / 2, 1720, 230, "up")
    return dict(hit=hit, flash=flash, bg=0.3 if tg < tp else 0.9)

def s_award(img, d, tg, k):
    hit = 0.0
    star(d, W / 2, 860, 200 * (1 + 0.2 * (1 - eout(k / 0.3))), GOLD)
    burst(d, W / 2, 860, k, 20, 380, GOLD, 5)
    label(d, 300, "MEILLEUR JOUEUR", k, 104, WHITE, "ÉLU PAR LES AUTRES JOUEURS", CYAN)
    ka = tg - M("africain", 99) + 0.1
    if ka > 0:
        badge(d, W / 2, 1300, "1er AFRICAIN", ka, CYAN, 160)
        if ka < 0.25: hit = 1 - ka / 0.25
    return dict(hit=hit, bg=0.85)

def s_giant(img, d, tg, k):
    hit = 0.0; flash = 0.0
    label(d, 300, "UN AUTRE GÉANT ANGLAIS", k, 80, WHITE)
    kc = tg - K["sunrise"] + 0.15
    if kc > 0:
        trophy(d, W / 2, 1000, 1.25 * (1 + 0.25 * (1 - eout(kc / 0.2))), GOLD)
        text(d, (W / 2, 500), "LA PLUS GRANDE", 84, WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 610), "COUPE D'EUROPE", fit("COUPE D'EUROPE", 100, 980), GOLD, BOLD, stroke=6, scol=BG)
        confetti(d, kc)
        if kc < 0.3: hit = 1 - kc / 0.3; flash = 0.3 * (1 - kc / 0.3)
    P(img, W / 2, 1720, 250, "up" if kc > 0 else run_pose(tg * 10))
    return dict(hit=hit, flash=flash, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), CYAN, BOLD, stroke=6, scol=BG)
    rows = [("TROP FRÊLE", "écarté par les recruteurs"), ("4e DIVISION", "à 18 ans"), ("PETIT PRIX", "à 22 ans"), ("CHAMPION", "et meilleur joueur")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 90 - 80 * (1 - eout(kk / 0.2))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD if i == 3 else CYAN)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 45, y), a, 44, GOLD if i == 3 else WHITE, MONO, "lm"); text(d, (x + 395, y), b, 42, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "PAS ASSEZ FORT ?", (W / 2, 1150), 110, -5, kn + 0.05, RED) if kn > -0.05 else 0.0
    return dict(hit=hit, bg=0.2)

NUMS = [(np.random.default_rng(i).uniform(120, W - 120), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["3/10", "5/10", "7/10", "10/10", "6/10", "8/10", "4/10", "9/10", "2/10", "7/10"])]
def s_question(img, d, tg, k):
    dim(img, 0.65)
    pulse = 0.0
    for tk in TJ["q_pulses"]:
        dd = tg - tk
        if 0 <= dd < 0.5: pulse = max(pulse, math.exp(-dd * 7))
    a = 1.0; de = tg - K["q_end"]
    if de > 0: a = max(0.0, 1 - de / 0.8)
    for x, y, s, sp in NUMS:
        yy = (y - tg * 50 * sp) % 700 + 720
        text(d, (x, yy), s, 64, mix(BG, (60, 90, 110), a), BOLD)
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (20, 80, 90), a), BOLD)
    return dict(hit=0.5 * pulse, bg=0.0)

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

SCENES = {"hook": s_hook, "cite": s_cite, "frail": s_frail, "quimper": s_quimper, "havre": s_havre, "stamps": s_stamps, "slam": s_slam,
          "england": s_england, "champion": s_champion, "award": s_award, "giant": s_giant, "you": s_you, "question": s_question, "logo": s_logo}
BGLEVEL = {"hook": 0.0, "cite": 0.08, "frail": 0.05, "quimper": 0.0, "havre": 0.0, "stamps": 0.0, "slam": 0.1, "england": 0.35,
           "champion": 0.3, "award": 0.85, "giant": 1.0, "you": 0.2, "question": 0.0, "logo": 0.0}

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

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None, int(a[5]) if len(a) > 5 else 1)

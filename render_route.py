# -*- coding: utf-8 -*-
"""Style « route » : route de nuit dans le désert (étoiles, dunes, palmiers) -> aube orange, bus, banc, joueur en silhouette
générique (maillot rouge, sans numéro). Types : hook village bus bench loan stamps slam rise record trophy legend you question logo.
Les scènes village/bus/bench/loan/rise/record/trophy/legend sont propres à l'histoire du 29/10 (footballeur égyptien).
Usage : python3 render_route.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# palette « route » : nuit bleue du désert -> aube orange
NIGHT = (8, 12, 30); SKY2 = (22, 26, 58); DAWN = (255, 140, 60); DAWN2 = (120, 60, 110)
SAND = (214, 160, 92); DUNE1 = (30, 24, 34); DUNE2 = (48, 34, 40); ASPH = (26, 26, 32)
PITCH = ASPH; ORANGE = (255, 150, 40)
HOR = 900

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        night = mix(NIGHT, SKY2, u); dawn = mix(DAWN2, DAWN, u ** 1.5)
        d.line((0, y, W, y), fill=mix(night, dawn, lit))
    rng = np.random.default_rng(4)
    for _ in range(170):   # étoiles
        x, y = rng.uniform(0, W), rng.uniform(0, HOR * 0.85); r = rng.uniform(1, 3.2)
        c = mix(mix(NIGHT, SKY2, y / HOR), WHITE, (0.4 + 0.6 * rng.random()) * (1 - lit))
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    if lit > 0.05:   # soleil à l'horizon
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        cy = HOR + 60 - 200 * lit
        dl.ellipse((W / 2 - 360, cy - 360, W / 2 + 360, cy + 360), fill=(255, 190, 90, int(90 * lit)))
        L = L.filter(ImageFilter.GaussianBlur(60)); img.alpha_composite(L)
        d.ellipse((W / 2 - 130, cy - 130, W / 2 + 130, cy + 130), fill=mix(DAWN, (255, 236, 170), lit))
    # dunes
    for layer, (base, amp, col, ph) in enumerate([(HOR - 40, 70, DUNE2, 0.7), (HOR + 10, 50, DUNE1, 2.1)]):
        pts = [(0, H)] + [(x, base - amp * (0.5 + 0.5 * math.sin(x / 210 + ph)) * (0.6 + 0.4 * math.sin(x / 90 + ph * 3))) for x in range(0, W + 20, 20)] + [(W, H)]
        d.polygon(pts, fill=mix(col, mix(SAND, DAWN, 0.3), lit * (0.55 if layer == 0 else 0.4)))
    # sol de sable
    d.rectangle((0, HOR + 40, W, H), fill=mix((22, 18, 26), (120, 80, 56), lit))
    # route en perspective
    def X(xn, y):
        u = (y - HOR) / (H - HOR); return W / 2 + xn * lerp(30, 760, u)
    d.polygon([(X(-1, HOR), HOR), (X(1, HOR), HOR), (X(1, H), H), (X(-1, H), H)], fill=mix(ASPH, (70, 58, 60), lit))
    lc = mix((120, 120, 110), WHITE, lit)
    d.line([(X(-0.92, HOR), HOR), (X(-0.92, H), H)], fill=lc, width=5); d.line([(X(0.92, HOR), HOR), (X(0.92, H), H)], fill=lc, width=5)
    # palmiers
    for x, y, s in [(120, 1010, 1.0), (980, 980, 0.85), (300, 930, 0.45), (800, 925, 0.4)]:
        palm(d, x, y, s, mix((10, 10, 16), (40, 26, 30), lit))
    return img

def palm(d, x, y, s, col):
    h = 330 * s
    pts = [(x + 30 * s * math.sin(i / 10 * 1.4), y - h * i / 10) for i in range(11)]
    for (a, b), (c, e) in zip(pts, pts[1:]): d.line((a, b, c, e), fill=col, width=int(22 * s) + 2)
    tx, ty = pts[-1]
    for k in range(7):
        ang = -math.pi + k * math.pi / 6 + 0.1
        fl = [(tx + 150 * s * j / 6 * math.cos(ang), ty + 150 * s * j / 6 * math.sin(ang) + 60 * s * (j / 6) ** 2) for j in range(7)]
        for (a, b), (c, e) in zip(fl, fl[1:]): d.line((a, b, c, e), fill=col, width=int(16 * s * (1 - 0.1 * fl.index((a, b)))) + 2)

BG_DARK = make_bg(0.0); BG_LIT = make_bg(1.0)
_BGC = {}
def scenery(level):
    q = round(min(1, max(0, level)) * 20) / 20
    if q not in _BGC: _BGC[q] = Image.blend(BG_DARK, BG_LIT, q)
    return _BGC[q].copy()

def dashes(d, tg, speed=1.0, lit=0.0):
    def X(y): return W / 2
    ph = (tg * speed * 1.4) % 1.0
    for i in range(14):
        u0 = ((i + ph) / 14) ** 2.2; u1 = ((i + ph + 0.45) / 14) ** 2.2
        y0 = HOR + (H - HOR) * u0; y1 = HOR + (H - HOR) * u1
        w0 = lerp(2, 30, u0); w1 = lerp(2, 30, u1)
        d.polygon([(W / 2 - w0, y0), (W / 2 + w0, y0), (W / 2 + w1, y1), (W / 2 - w1, y1)], fill=mix((200, 180, 120), WHITE, lit))

def dim(img, a):
    if a <= 0: return
    img.alpha_composite(Image.new("RGBA", (W, H), BG + (int(255 * min(1, a)),)))

POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-25, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))
JER = (220, 40, 46)

def P(img, x, y, s, pose, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER)
    player(img, x, y, s, pose, **kw)

def bus(d, x, y, s, tg, lights=True, kid=True):
    """bus vu de côté ; (x, y) = bas-gauche de la carrosserie."""
    w, h = 520 * s, 190 * s
    if lights:
        d.polygon([(x + w, y - 0.45 * h), (x + w + 520 * s, y - 0.75 * h), (x + w + 520 * s, y + 0.1 * h)], fill=(80, 74, 50))
    d.rounded_rectangle((x, y - h, x + w, y), int(26 * s), fill=(232, 226, 210), outline=(40, 40, 46), width=int(5 * s) + 1)
    d.rectangle((x, y - 0.32 * h, x + w, y - 0.22 * h), fill=JER)
    for i in range(6):
        wx = x + 30 * s + i * 78 * s
        d.rounded_rectangle((wx, y - 0.86 * h, wx + 62 * s, y - 0.45 * h), int(8 * s), fill=(255, 214, 120) if lights else (60, 80, 100))
    if kid:
        kx = x + 30 * s + 2 * 78 * s + 31 * s
        d.ellipse((kx - 15 * s, y - 0.72 * h - 15 * s, kx + 15 * s, y - 0.72 * h + 15 * s), fill=SIL)
        d.rectangle((kx - 22 * s, y - 0.62 * h, kx + 22 * s, y - 0.45 * h), fill=SIL)
    d.rectangle((x + w - 12 * s, y - 0.5 * h, x + w, y - 0.38 * h), fill=(255, 250, 220))
    for wx in (x + 100 * s, x + w - 110 * s):
        r = 44 * s; d.ellipse((wx - r, y - r * 0.6, wx + r, y + r * 1.4), fill=(20, 20, 24))
        a = tg * 9; d.line((wx, y + r * 0.4, wx + r * 0.7 * math.cos(a), y + r * 0.4 + r * 0.7 * math.sin(a)), fill=GREY, width=int(6 * s) + 1)

def trophy(d, cx, cy, s=1.0, col=GOLD):
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.polygon([q(-120, -230), q(120, -230), q(80, -60), q(25, -20), q(25, 50), q(80, 90), q(-80, 90), q(-25, 50), q(-25, -20), q(-80, -60)], fill=col)
    d.arc((cx - 190 * s, cy - 230 * s, cx - 70 * s, cy - 90 * s), 90, 270, fill=col, width=int(14 * s))
    d.arc((cx + 70 * s, cy - 230 * s, cx + 190 * s, cy - 90 * s), 270, 90, fill=col, width=int(14 * s))

def bench(d, x, y, w=520):
    d.rectangle((x - w / 2, y, x + w / 2, y + 26), fill=(70, 60, 60))
    d.rectangle((x - w / 2, y - 150, x + w / 2, y - 120), fill=(60, 52, 54))
    for xx in (x - w / 2 + 30, x + w / 2 - 40): d.rectangle((xx, y + 26, xx + 14, y + 140), fill=(40, 36, 40))

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    dashes(d, tg, 2.5)
    hit = 0.0
    # panneau routier
    d.line((880, 1180, 880, 900), fill=GREY, width=12)
    d.rounded_rectangle((690, 760, 1050, 920), 16, fill=(18, 110, 70), outline=WHITE, width=6)
    text(d, (870, 815), "LE CAIRE", 50, WHITE, BOLD); text(d, (870, 875), "TRÈS LOIN  →", 34, WHITE, MONO)
    P(img, W / 2 - 40, 1640, 300, run_pose(tg * 10) if k < 99 else "stand", glow=0.6 + 0.4 * ease(k / 1.0))
    kk = tg - K["hook"]
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 420), "TROP LONG ?", int(fit("TROP LONG ?", 150, 960) * sc), WHITE, BOLD, stroke=8, scol=RED)
        hit = max(0, 1 - kk / 0.25)
    return dict(hit=hit)

def house(d, x, y, w, h, lit):
    d.rectangle((x, y - h, x + w, y), fill=(36, 30, 36)); d.rectangle((x - 6, y - h - 12, x + w + 6, y - h), fill=(46, 38, 44))
    for i in range(max(1, int(w // 70))):
        wx = x + 20 + i * 70
        d.rectangle((wx, y - h + 30, wx + 30, y - h + 70), fill=(255, 200, 100) if (i + int(x)) % 3 else (60, 50, 60))

def s_village(img, d, tg, k):
    dim(img, 0.25)
    for x, w, h in [(40, 200, 170), (260, 150, 130), (430, 230, 200), (700, 170, 150), (890, 180, 190)]: house(d, x, 1330, w, h, 1)
    label(d, 300, "UN PETIT VILLAGE", tg - M("village", SC["village"]) + 0.2, 92, WHITE, "ÉGYPTE", ORANGE) if tg > M("village", 0) - 0.2 else None
    hit = 0.0
    kq = tg - M("quatorze", 99)
    if kq > 0:
        badge(d, 800, 480, "14 ANS", kq, ORANGE, 105)
        if kq < 0.25: hit = 1 - kq / 0.25
    P(img, 330, 1560, 190, "stand"); ball(d, 420, 1545, 22, WHITE, tg)
    kc = tg - M("caire", 99) + 0.2
    if kc > 0:
        A = (330, 1250); B = (800, 880)
        p = eout(kc / 2.2); n = 40
        for i in range(int(n * p)):
            s0 = i / n; x = lerp(A[0], B[0], s0) + 120 * math.sin(math.pi * s0); y = lerp(A[1], B[1], s0)
            if i % 2 == 0: d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=WHITE)
        if p > 0.5:
            for j, hh in enumerate([90, 150, 120, 200, 110]):   # silhouette de grande ville
                d.rectangle((B[0] - 130 + j * 52, B[1] - hh, B[0] - 88 + j * 52, B[1]), fill=(90, 100, 130))
            text(d, (B[0], B[1] + 45), "LE CAIRE", 46, WHITE, MONO)
    hit = max(hit, stamp(img, "LOIN", (300, 760), 120, -8, tg - M("loin", 99) + 0.05, RED))
    hit = max(hit, stamp(img, "TRÈS LOIN", (W / 2, 1000), 130, 5, tg - M("loin2", 99) + 0.05, RED))
    return dict(hit=hit)

def s_bus(img, d, tg, k):
    lvl_t = tg - M("lendemain", 99)
    d.rectangle((0, 1240, W, 1420), fill=ASPH); d.line((0, 1330, W, 1330), fill=(200, 180, 120), width=6)
    x = -560 + ((tg - SC["bus"]) * 260) % (W + 600)
    bus(d, x, 1320, 1.0, tg)
    hit = 0.0
    kr = tg - M("recommence", 99) + 0.1
    for j, (mk, lab, yy) in enumerate([("aller", "ALLER", 330), ("retour", "RETOUR", 520)]):
        kk = tg - M(mk, 99) + 0.2
        if kr > 0: break
        if kk > 0:
            text(d, (110, yy), lab, 54, WHITE, BOLD, "lm")
            for i in range(3):
                if kk > i * 0.15:
                    bx = 470 + i * 190; d.rounded_rectangle((bx, yy - 45, bx + 160, yy + 35), 14, fill=(232, 226, 210))
                    d.rectangle((bx, yy + 5, bx + 160, yy + 15), fill=JER)
                    for wi in range(3): d.rectangle((bx + 12 + wi * 50, yy - 35, bx + 48 + wi * 50, yy - 5), fill=(255, 214, 120))
            if kk < 0.25: hit = max(hit, 1 - kk / 0.25)
    hit = max(hit, stamp(img, "≈ 10 H / JOUR", (W / 2, 800), 130, -5, tg - M("dix", 99) + 0.05, ORANGE))
    if kr > 0:
        text(d, (W / 2, 380), "ET IL RECOMMENCE.", fit("ET IL RECOMMENCE.", 90, 980), GOLD, BOLD, stroke=5, scol=BG)
        a0 = tg * 4; cx, cy, r = W / 2, 540, 70
        d.arc((cx - r, cy - r, cx + r, cy + r), math.degrees(a0), math.degrees(a0) + 300, fill=GOLD, width=12)
    return dict(hit=hit, bg=0.12 + 0.35 * max(0, math.sin(max(0, lvl_t) * 3)) if lvl_t > 0 else 0.12)

def s_bench(img, d, tg, k):
    dim(img, 0.45)
    hit = 0.0
    ka = tg - M("anglais", SC["bench"]) + 0.3
    tb = M("banc", 99)
    if tg < M("non", 99):
        if ka > 0: label(d, 300, "UN GRAND CLUB ANGLAIS", ka, 78, WHITE, "APRÈS LA SUISSE", ORANGE)
        kr = tg - M("reve", 99) + 0.1
        if kr > 0: text(d, (W / 2, 620), "ENFIN LE RÊVE ?", int(fit("ENFIN LE RÊVE ?", 100, 960) * (1 + 0.2 * (1 - eout(kr / 0.2)))), GOLD, BOLD, stroke=6, scol=BG)
        P(img, W / 2, 1500, 300, "up" if kr > 0 else "stand"); shadow(d, W / 2, 1500, 300)
    else:
        hit = stamp(img, "NON.", (W / 2, 420), 200, -6, tg - M("non", 99) + 0.05, RED)
        bench(d, W / 2, 1330)
        P(img, W / 2 - 60, 1330 + 0.72 * 260 - 20, 260, "sad" if tg > tb else "sit")
        ke = tg - M("echec", 99) + 0.05
        if tg > tb and ke <= 0: text(d, (W / 2, 720), "SUR LE BANC", 90, WHITE, BOLD, stroke=6, scol=BG)
        if ke > 0:   # journaux génériques
            for j, (x, y, a) in enumerate([(230, 780, -12), (850, 820, 10)]):
                L = Image.new("RGBA", (300, 200), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
                dl.rectangle((0, 0, 300, 200), fill=(230, 226, 214)); dl.rectangle((14, 14, 286, 46), fill=(60, 60, 60))
                for r in range(5): dl.line((14, 70 + r * 24, 286 - (r % 2) * 60, 70 + r * 24), fill=GREY, width=6)
                L = L.rotate(a, expand=True, resample=Image.BICUBIC); img.alpha_composite(L, (int(x - L.width / 2), int(y - L.height / 2)))
            hit = max(hit, stamp(img, "« ÉCHEC »", (W / 2, 1000), 150, -4, ke, RED))
    return dict(hit=hit, bg=0.05)

def s_loan(img, d, tg, k):
    dim(img, 0.55)
    A = (300, 620); B = (760, 1200)
    d.ellipse((A[0] - 20, A[1] - 20, A[0] + 20, A[1] + 20), fill=(130, 170, 255)); text(d, (A[0], A[1] - 60), "ANGLETERRE", 50, WHITE, MONO)
    ka = tg - M("prete", SC["loan"] + 1.0) + 0.6
    hit = 0.0
    if ka > 0:
        p = eout(ka / 1.4); n = 40
        for i in range(int(n * p)):
            s0 = i / n; x = lerp(A[0], B[0], s0) + 170 * math.sin(math.pi * s0); y = lerp(A[1], B[1], s0)
            if i % 2 == 0: d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=WHITE)
        if p > 0.95:
            d.ellipse((B[0] - 20, B[1] - 20, B[0] + 20, B[1] + 20), fill=GREEN); text(d, (B[0], B[1] + 62), "ITALIE", 54, WHITE, MONO)
    hit = stamp(img, "PRÊTÉ", (W / 2, 330), 170, -6, tg - M("prete", 99) + 0.05, ORANGE)
    P(img, 300, 1600, 200, "stand", alpha=0.8)
    return dict(hit=hit, bg=0.05)

def s_stamps(img, d, tg, k):
    dim(img, 0.55)
    bench(d, W / 2, 1500)
    P(img, W / 2 - 60, 1500 + 0.72 * 230 - 20, 230, "sad", alpha=0.6)
    hit = 0.0; cols = [RED, ORANGE, WHITE]
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
            if r > 0: d.ellipse((W / 2 - r, 1450 - r * 0.35, W / 2 + r, 1450 + r * 0.35), outline=ORANGE, width=max(1, int(16 * max(0, 1 - r / 1500))))
        burst(d, W / 2, 1100, kk, 22, 520, WHITE, 3, 9)
        flash = max(0, 0.9 - kb * 4) if kb > 0 else 0
        hit = max(0, 1 - kk / 0.3)
    shadow(d, W / 2, 1600, 320)
    P(img, W / 2, 1600, 320, pose, glow=1.0)
    if kb > -0.08:
        kk = kb + 0.08; sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 330), "IL A", 90, ORANGE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 520), "CONTINUÉ.", int(fit("CONTINUÉ.", 220, 1000) * sc), WHITE, BOLD, stroke=10, scol=ORANGE)
    else:
        text(d, (W / 2, 420), typew("TOUT LÂCHER ?", max(0, tg - K["build_start"] + 0.2), 20), 100, GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_rise(img, d, tg, k):
    dashes(d, tg, 1.6, 0.4)
    hit = 0.0
    for txt, tk, y in [("IL TRAVAILLE.", K["gate1"], 300), ("IL MARQUE.", K["gate2"], 430)]:
        kk = tg - tk + 0.15
        if kk > 0:
            text(d, (W / 2, y - 20 * (1 - eout(kk / 0.25))), txt, 96, WHITE if y == 300 else GOLD, BOLD, stroke=6, scol=BG)
            if kk < 0.3: hit = max(hit, 1 - kk / 0.3)
    kg = tg - K["gate2"]
    t17 = M("d2017", 99)
    if tg < t17 - 0.2:
        P(img, W / 2, 1640, 300, run_pose(tg * 10) if kg < 0 else blend_pose(POSES["kick"], POSES["up"], min(1, kg / 0.5)))
        if kg > 0:
            u = min(1, kg / 0.5); ball(d, lerp(W / 2 + 150, W / 2 + 40, u), lerp(1600, 980, u), lerp(40, 18, u), WHITE, tg * 9)
            burst(d, W / 2 + 40, 980, kg - 0.5, 16, 200, GOLD, 2)
    else:
        k7 = tg - t17 + 0.2
        hit = max(hit, stamp(img, "2017", (W / 2, 780), 200, -5, k7, GOLD))
        if k7 > 0.3: text(d, (W / 2, 950), "RETOUR EN ANGLETERRE", fit("RETOUR EN ANGLETERRE", 66, 980), WHITE, BOLD, stroke=5, scol=BG)
        P(img, W / 2, 1640, 300, "stand")
    return dict(hit=hit, bg=0.45)

def s_record(img, d, tg, k):
    dim(img, 0.35)
    hit = 0.0
    t32 = M("d32", SC["record"] + 1.0)
    label(d, 300, "PREMIÈRE SAISON", k, 90, WHITE)
    u = eout(min(1, max(0, (tg - SC["record"] - 0.3) / max(0.3, t32 - SC["record"] - 0.1))))
    n = int(round(32 * u))
    sc = 1 + (0.25 * (1 - eout((tg - t32) / 0.25)) if tg > t32 else 0)
    text(d, (W / 2, 620), f"{n}", int(260 * sc), GOLD if n == 32 else WHITE, BOLD, stroke=8, scol=BG)
    text(d, (W / 2, 790), "BUTS EN CHAMPIONNAT", 56, WHITE, BOLD)
    for i in range(n):
        x = 190 + (i % 8) * 100; y = 950 + (i // 8) * 100
        ball(d, x, y, 34, WHITE, i)
    if tg > t32 and tg - t32 < 0.25: hit = 1 - (tg - t32) / 0.25
    kr = tg - M("record", 99) + 0.05
    hit = max(hit, stamp(img, "RECORD", (W / 2, 1390), 150, -7, kr, RED))
    return dict(hit=hit, bg=0.3)

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def s_trophy(img, d, tg, k):
    hit = 0.0; flash = 0.0
    tc = M("coupe", SC["trophy"] + 0.8); t2 = M("champ2", tc + 1.5)
    for j, (tk, x, lab, sub) in enumerate([(tc, 280, "LA PLUS GRANDE", "COUPE D'EUROPE"), (t2, 800, "LE", "CHAMPIONNAT")]):
        kk = tg - tk + 0.15
        if kk <= 0: continue
        cy = 1150 - 120 * eout(kk / 0.4)
        trophy(d, x, cy, 1.15 * (1 + 0.25 * (1 - eout(kk / 0.2))))
        text(d, (x, cy + 190), lab, 44, WHITE, BOLD); text(d, (x, cy + 245), sub, 44, GOLD, BOLD)
        if kk < 0.3: hit = max(hit, 1 - kk / 0.3); flash = max(flash, 0.3 * (1 - kk / 0.3))
    kv = tg - tc
    if kv > 0:
        for x0, y0, c in CONF:
            y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
            if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[ORANGE, WHITE, JER][c])
    text(d, (W / 2, 320), "PUIS IL GAGNE", int(fit("PUIS IL GAGNE", 110, 980) * (1 + 0.2 * (1 - eout(k / 0.2)))), WHITE, BOLD, stroke=6, scol=BG)
    P(img, W / 2, 1720, 230, "up")
    return dict(hit=hit, flash=flash, bg=0.8)

def s_legend(img, d, tg, k):
    hit = 0.0
    lvl = 0.6 + 0.4 * ease(k / 2.0)
    P(img, W / 2, 1300, 340, "up", glow=1.0)
    burst(d, W / 2, 900, k, 20, 400, GOLD, 5)
    label(d, 280, "L'UN DES PLUS GRANDS", k, 88, WHITE)
    ka = tg - M("africains", 99) + 0.1
    if ka > 0:
        text(d, (W / 2, 400), "JOUEURS AFRICAINS", fit("JOUEURS AFRICAINS", 92, 980), GOLD, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 510), "DE L'HISTOIRE", 72, WHITE, BOLD, stroke=5, scol=BG)
        if ka < 0.25: hit = 1 - ka / 0.25
    return dict(hit=hit, bg=lvl)

def s_you(img, d, tg, k):
    dim(img, 0.55)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=6, scol=BG)
    rows = [("14 ANS", "≈ 10 h de bus / jour"), ("LE BANC", "« c'est un échec »"), ("PRÊTÉ", "il continue"), ("32 BUTS", "un record")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 110 - 80 * (1 - eout(kk / 0.2))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD if i == 3 else ORANGE)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 50, y), a, 48, GOLD if i == 3 else WHITE, MONO, "lm"); text(d, (x + 330, y), b, 46, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "TROP LONG ?", (W / 2, 1150), 110, -5, kn + 0.05, RED) if kn > -0.05 else 0.0
    return dict(hit=hit, bg=0.25)

NUMS = [(np.random.default_rng(i).uniform(90, W - 90), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["1 h", "2 h", "3 h", "4 h", "5 h", "6 h", "8 h", "10 h", "0 h", "1 h"])]
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
        text(d, (x, yy), s, 64, mix(BG, (70, 74, 96), a), BOLD)
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (100, 60, 30), a), BOLD)
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

SCENES = {"hook": s_hook, "village": s_village, "bus": s_bus, "bench": s_bench, "loan": s_loan, "stamps": s_stamps, "slam": s_slam,
          "rise": s_rise, "record": s_record, "trophy": s_trophy, "legend": s_legend, "you": s_you, "question": s_question, "logo": s_logo}
BGLEVEL = {"hook": 0.0, "village": 0.05, "bus": 0.12, "bench": 0.05, "loan": 0.05, "stamps": 0.0, "slam": 0.1, "rise": 0.45,
           "record": 0.3, "trophy": 0.8, "legend": 0.8, "you": 0.25, "question": 0.0, "logo": 0.0}

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

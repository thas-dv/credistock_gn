# -*- coding: utf-8 -*-
"""Style « gare » : gare d hiver la nuit sous la neige (rails, train aux fenêtres ambrées, tableau des départs sans noms), matin doré ;
joueur en silhouette générique (maillot blanc, sans numéro). Types : hook gare essai laval lille cologne stamps slam rennes stuttgart record europe guinee you question logo.
Scènes propres à l histoire du 31/10 (attaquant guinéen) sauf stamps/slam/you/question/logo.
Usage : python3 render_gare.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# palette « gare » : gare d'hiver la nuit sous la neige (bleu glacier, lampes ambrées) -> matin doré sur la neige
NIGHT = (8, 14, 30); SKY2 = (24, 42, 74); DUSK = (150, 120, 140); DUSK2 = (250, 196, 120)
ICE = (120, 205, 255); AMBER = (255, 184, 80); SNOW = (226, 236, 248)
PLAT = (40, 46, 60); PLAT2 = (150, 156, 170); RAIL = (110, 120, 140)
ORANGE = ICE; PITCH = PLAT
HOR = 1000; EDGE = 1400
JER = (236, 236, 242)

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        night = mix(NIGHT, SKY2, u); day = mix(DUSK, DUSK2, u ** 1.3)
        d.line((0, y, W, y), fill=mix(night, day, lit * 0.85))
    rng = np.random.default_rng(3)
    for _ in range(80):
        x, y = rng.uniform(0, W), rng.uniform(0, HOR * 0.45); r = rng.uniform(1, 2.4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix(mix(NIGHT, SKY2, y / HOR), WHITE, (0.3 + 0.5 * rng.random()) * (1 - lit)))
    if lit > 0.3:   # soleil bas
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((W / 2 - 260, HOR - 330, W / 2 + 260, HOR + 190), fill=(255, 220, 140, int(170 * (lit - 0.3) / 0.7)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(60)))
        d = ImageDraw.Draw(img)
        d.ellipse((W / 2 - 110, HOR - 180, W / 2 + 110, HOR + 40), fill=mix((255, 214, 150), (255, 240, 200), lit))
    # ville lointaine + collines enneigées
    rng = np.random.default_rng(9); x = -20
    while x < W + 20:
        w = rng.uniform(40, 110); h = rng.uniform(40, 170)
        d.rectangle((x, HOR - h, x + w, HOR), fill=mix((16, 24, 44), (120, 100, 110), lit * 0.6))
        x += w + rng.uniform(0, 20)
    d.polygon([(0, HOR - 30), (260, HOR - 90), (520, HOR - 20), (800, HOR - 110), (W, HOR - 40), (W, HOR + 5), (0, HOR + 5)], fill=mix((60, 72, 100), SNOW, 0.35 + 0.5 * lit))
    # voies en perspective (ballast enneigé)
    d.rectangle((0, HOR, W, EDGE), fill=mix((30, 36, 52), (176, 182, 196), lit))
    VX = W / 2
    def X(xn, y):
        u = (y - HOR) / (EDGE - HOR); return VX + xn * lerp(30, 900, u)
    for yy in np.geomspace(1, EDGE - HOR, 26):   # traverses
        y = HOR + yy
        for c in (-0.55, 0.55):
            d.line((X(c - 0.32, y), y, X(c + 0.32, y), y), fill=mix((50, 44, 44), (120, 110, 104), lit), width=max(2, int(yy / 28)))
    rc = mix(RAIL, (230, 230, 240), lit)
    for c in (-0.78, -0.32, 0.32, 0.78):
        d.line([(X(c, HOR), HOR), (X(c, EDGE), EDGE)], fill=rc, width=5)
    # poteaux de caténaire
    for c in (-1.25, 1.25):
        for yy in (60, 160, 400):
            y = HOR + yy; x = X(c, y); h = lerp(80, 600, yy / 400)
            d.line((x, y, x, y - h), fill=mix((40, 46, 60), (90, 90, 100), lit), width=max(3, int(yy / 30)))
            d.line((x, y - h, VX + (x - VX) * 0.5, y - h), fill=mix((40, 46, 60), (90, 90, 100), lit), width=max(2, int(yy / 50)))
    # quai au premier plan (neige + bande jaune)
    d.rectangle((0, EDGE, W, H), fill=mix(PLAT, PLAT2, lit))
    d.rectangle((0, EDGE, W, EDGE + 26), fill=mix((150, 126, 30), (240, 200, 60), 0.4 + 0.6 * lit))
    for yy in range(EDGE + 60, H, 90):
        d.line((0, yy, W, yy), fill=mix((52, 58, 74), (166, 172, 186), lit), width=2)
    rng = np.random.default_rng(13)
    for _ in range(40):
        x, y = rng.uniform(0, W), rng.uniform(EDGE + 40, H); w = rng.uniform(60, 240)
        d.ellipse((x - w, y - 10, x + w, y + 10), fill=mix((150, 164, 190), SNOW, lit))
    # lampadaires de quai
    for x in (110, W - 110):
        d.line((x, H, x, 640), fill=(46, 50, 62), width=14)
        d.rectangle((x - 46, 620, x + 46, 650), fill=mix(AMBER, WHITE, lit))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for x in (110, W - 110):
        c = mix(AMBER, (255, 250, 230), lit)
        dl.polygon([(x - 40, 650), (x + 40, 650), (x + 300, H), (x - 300, H)], fill=c + (int(34 + 20 * lit),))
        dl.ellipse((x - 120, 520, x + 120, 760), fill=c + (int(110 + 40 * lit),))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(38)))
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

FLAKES = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.4, 1.0)) for i in range(150)]
def snow(d, tg, amt=1.0):
    n = int(len(FLAKES) * amt)
    for x0, y0, z in FLAKES[:n]:
        y = (y0 + tg * 140 * z) % H; x = (x0 + 40 * math.sin(tg * 0.9 * z + x0)) % W; r = 2 + 4 * z
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((90, 110, 140), SNOW, z))

POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-25, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))
POSES["hurt"] = dict(t=20, la=(-30, 70), ra=(40, -80), ll=(-70, 100), rl=(-10, 20))

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

def scout(d, x, y, s, turned, col=(14, 16, 24)):
    sx = 1 - 2 * ease(turned)
    d.rounded_rectangle((x - 45 * s, y - 230 * s, x + 45 * s, y - 60 * s), int(20 * s), fill=col)
    d.ellipse((x - 32 * s, y - 300 * s, x + 32 * s, y - 236 * s), fill=col)
    d.rectangle((x - 34 * s, y - 60 * s, x - 8 * s, y), fill=col); d.rectangle((x + 8 * s, y - 60 * s, x + 34 * s, y), fill=col)
    if sx > -0.2:
        xa, xb = sorted((x + 30 * s * sx, x + 80 * s * sx)); d.rectangle((xa, y - 200 * s, xb, y - 130 * s), fill=(220, 220, 210))

def suitcase(d, x, y, s=1.0):
    d.rounded_rectangle((x - 60 * s, y - 120 * s, x + 60 * s, y), int(12 * s), fill=(120, 70, 40), outline=(40, 24, 14), width=4)
    d.rounded_rectangle((x - 26 * s, y - 150 * s, x + 26 * s, y - 118 * s), int(8 * s), outline=(40, 24, 14), width=int(8 * s))
    d.line((x - 60 * s, y - 70 * s, x + 60 * s, y - 70 * s), fill=(70, 40, 22), width=6)

def train(d, x0, lit=0.0, y=1110):
    """train vu de côté sur la voie du fond, fenêtres allumées ; x0 = abscisse de la tête."""
    body = mix((26, 40, 66), (90, 110, 140), lit)
    for c in range(4):
        x = x0 + c * 620
        if x > W + 50 or x + 600 < -50: continue
        d.rounded_rectangle((x, y, x + 600, y + 230), 26, fill=body, outline=mix((10, 14, 24), (40, 50, 70), lit), width=5)
        d.rectangle((x, y + 180, x + 600, y + 196), fill=ICE)
        for wx in range(int(x) + 40, int(x) + 560, 110):
            d.rounded_rectangle((wx, y + 40, wx + 80, y + 120), 10, fill=mix(AMBER, (255, 236, 180), 0.4))
        for wx in (x + 120, x + 480):
            d.ellipse((wx - 30, y + 210, wx + 30, y + 270), fill=(12, 12, 16))
    d.rounded_rectangle((x0 - 70, y + 20, x0 + 30, y + 230), 40, fill=body)
    d.ellipse((x0 - 60, y + 150, x0 - 30, y + 180), fill=(255, 250, 220))

def board(d, rows, k, y0=230):
    """tableau des départs (années uniquement, aucun nom)."""
    if k <= 0: return
    d.rounded_rectangle((70, y0, W - 70, y0 + 90 + 86 * len(rows)), 18, fill=(10, 14, 22), outline=(60, 70, 90), width=5)
    text(d, (110, y0 + 46), "DÉPARTS", 44, AMBER, MONO, "lm"); text(d, (W - 110, y0 + 46), "QUAI", 44, AMBER, MONO, "rm")
    for i, (a, b) in enumerate(rows):
        kk = k - 0.15 * i
        if kk <= 0: continue
        y = y0 + 120 + 86 * i
        s = typew(a, kk, 30)
        text(d, (110, y), s, 50, (255, 214, 120), MONO, "lm"); text(d, (W - 110, y), typew(b, kk, 30), 50, WHITE, MONO, "rm")

def goal(d, cx, y, s=1.0, lit=0.0):
    c = mix((210, 220, 235), WHITE, lit)
    d.line((cx - 300 * s, y, cx - 300 * s, y - 220 * s), fill=c, width=int(14 * s)); d.line((cx + 300 * s, y, cx + 300 * s, y - 220 * s), fill=c, width=int(14 * s))
    d.line((cx - 300 * s, y - 220 * s, cx + 300 * s, y - 220 * s), fill=c, width=int(14 * s))
    for i in range(1, 12): d.line((cx - 300 * s + i * 50 * s, y - 220 * s, cx - 280 * s + i * 46 * s, y - 40 * s), fill=mix(c, BG, 0.6), width=2)

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def confetti(d, kv):
    for x0, y0, c in CONF:
        y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[ICE, WHITE, GOLD][c])

FEET = 1640

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    jig = math.sin(tg * 9)
    P(img, W / 2, FEET, 300, blend_pose(POSES["stand"], POSES["kick"], 0.5 + 0.5 * jig)); shadow(d, W / 2, FEET, 300)
    ball(d, W / 2 + 90, 1380 - 160 * abs(math.sin(tg * 4.5)), 34, WHITE, tg * 6)
    kk = tg - K["hook"]
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 330), "TU N'Y ARRIVERAS", int(fit("TU N'Y ARRIVERAS", 110, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        text(d, (W / 2, 490), "JAMAIS ?", int(fit("JAMAIS ?", 170, 960) * sc), WHITE, BOLD, stroke=8, scol=RED)
        hit = max(0, 1 - kk / 0.25)
    else:
        text(d, (W / 2, 400), typew("ON T'A DÉJÀ DIT…", tg + 0.2, 22), 96, ICE, BOLD, stroke=6, scol=BG)
    return dict(hit=hit)

def s_gare(img, d, tg, k):
    hit = 0.0
    train(d, W + 80 - 900 * k, 0.05)
    board(d, [("2013", "1"), ("2015", "2"), ("2016", "3"), ("2019", "4")], k, 220)
    kg = tg - M("guinee1", SC["gare"] + 2) + 0.15
    if kg > 0:
        text(d, (W / 2, 830), "L'ATTAQUANT", 96, WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 940), "DE LA GUINÉE", int(fit("DE LA GUINÉE", 110, 980) * (1 + 0.3 * (1 - eout(kg / 0.2)))), GOLD, BOLD, stroke=7, scol=BG)
        if kg < 0.3: hit = 1 - kg / 0.3
    x = W / 2 - 60
    P(img, x, FEET, 280, "stand"); shadow(d, x, FEET, 280); suitcase(d, x + 190, FEET)
    return dict(hit=hit, bg=0.05)

def s_essai(img, d, tg, k):
    dim(img, 0.3)
    hit = 0.0
    turned = ease((tg - M("auxerre", SC["essai"] + 1)) / 0.6) if tg > M("auxerre", 99) - 0.2 else 0.0
    for x in (200, 880): scout(d, x, 1600, 1.15, turned)
    P(img, W / 2, 1600, 260, "stand", alpha=0.95); shadow(d, W / 2, 1600, 260)
    label(d, 330, "ADOLESCENT", k, 100, WHITE, "UN ESSAI", ICE)
    hit = max(hit, stamp(img, "RECALÉ", (W / 2, 700), 190, -7, tg - M("recale1", 99) + 0.05, RED))
    return dict(hit=hit, bg=0.0)

def s_laval(img, d, tg, k):
    dim(img, 0.45)
    hit = 0.0
    k17 = tg - M("dixsept", SC["laval"] + 0.1) + 0.1
    if k17 > 0: badge(d, 230, 320, "17 ANS", k17, GOLD, 110); hit = max(hit, 1 - k17 / 0.25) if k17 < 0.25 else hit
    kp = tg - M("pro", 99) + 0.1
    if kp > 0: text(d, (700, 320), "PRO", int(150 * (1 + 0.3 * (1 - eout(kp / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
    kd = tg - M("deuxieme", 99) + 0.1
    if kd > 0: text(d, (W / 2, 500), "2e DIVISION", 80, ICE, BOLD, stroke=6, scol=BG)
    ks = tg - M("saison", 99) + 0.2
    if ks > 0:
        d.rounded_rectangle((140, 620, W - 140, 1080), 26, fill=(10, 14, 22), outline=(70, 80, 100), width=5)
        text(d, (W / 2, 690), "1re SAISON", 56, AMBER, MONO)
        k4 = tg - M("quatre", 99) + 0.1; k0 = tg - M("zero", 99) + 0.1
        text(d, (330, 800), "MATCHS", 48, GREY, MONO); text(d, (750, 800), "BUTS", 48, GREY, MONO)
        if k4 > 0: text(d, (330, 940), "4", int(170 * (1 + 0.3 * (1 - eout(k4 / 0.2)))), WHITE, BOLD)
        if k0 > 0:
            text(d, (750, 940), "0", int(170 * (1 + 0.4 * (1 - eout(k0 / 0.2)))), RED, BOLD)
            if k0 < 0.3: hit = max(hit, 1 - k0 / 0.3)
    P(img, W / 2, FEET, 240, "sad" if ks > 0 else run_pose(tg * 8)); shadow(d, W / 2, FEET, 240)
    return dict(hit=hit, bg=0.0)

def bench(d, x, y, w=520):
    d.rectangle((x - w / 2, y - 120, x + w / 2, y - 96), fill=(90, 60, 40)); d.rectangle((x - w / 2, y - 60, x + w / 2, y - 36), fill=(110, 74, 48))
    for xx in (x - w / 2 + 40, x + w / 2 - 40): d.rectangle((xx - 10, y - 60, xx + 10, y), fill=(30, 30, 36))
    d.ellipse((x - w / 2, y - 132, x + w / 2, y - 112), fill=SNOW)

def s_lille(img, d, tg, k):
    hit = 0.0
    tp = M("prete", SC["lille"] + 1.5)
    if tg < tp - 0.1:
        dim(img, 0.25)
        bench(d, W / 2, FEET)
        P(img, W / 2 - 60, FEET - 36 + 0.72 * 240 - 30, 240, "sit", alpha=0.95)
        label(d, 360, "IL JOUE", k, 110, WHITE)
        kp = tg - M("peine", 99) + 0.1
        if kp > 0: hit = stamp(img, "À PEINE", (W / 2, 560), 150, -5, kp, ICE)
    else:
        kk = tg - tp
        train(d, lerp(-200, W - 400, eout(kk / 1.0)) if kk < 1.0 else W - 400, 0.05)
        hit = max(hit, stamp(img, "PRÊTÉ", (W / 2, 380), 190, -6, kk + 0.05, AMBER))
        kr = tg - M("recale2", 99) + 0.4
        if kr > 0:
            text(d, (W / 2, 620), typew("…AU CLUB QUI", kr, 26), 84, WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 730), typew("L'AVAIT RECALÉ", max(0, kr - 0.4), 26), 92, RED, BOLD, stroke=6, scol=BG)
        x = W / 2 + 80; P(img, x, FEET, 260, "stand"); shadow(d, x, FEET, 260); suitcase(d, x - 200, FEET)
    return dict(hit=hit, bg=0.05)

def s_cologne(img, d, tg, k):
    dim(img, 0.4)
    hit = 0.0
    tr = M("rate", 99)
    if tg < tr - 0.2:
        label(d, 300, "EN ALLEMAGNE", k, 96, WHITE, "LOIN DE CHEZ LUI", ICE)
        kg = tg - M("genou", 99) + 0.1
        pose = "hurt" if kg > 0 else "stand"
        P(img, W / 2, FEET, 290, pose); shadow(d, W / 2, FEET, 290)
        if kg > 0:
            r = 60 + 30 * math.sin(tg * 10)
            d.ellipse((W / 2 - 150 - r, 1450 - r, W / 2 - 150 + r, 1450 + r), outline=RED, width=10)
            text(d, (W / 2, 540), "LE GENOU", 110, RED, BOLD, stroke=6, scol=BG)
            if kg < 0.3: hit = 1 - kg / 0.3
        hit = max(hit, stamp(img, "OPÉRATION", (W / 2, 760), 130, -5, tg - M("operation", 99) + 0.05, WHITE))
        kb = tg - M("blessure", 99) + 0.1
        if kb > 0:
            for i in range(min(4, int(kb / 0.3) + 1)):
                text(d, (W / 2 + [-120, 110, -60, 140][i], 950 + i * 95), "BLESSÉ", 70, mix(RED, WHITE, 0.2 * i), BOLD, stroke=5, scol=BG)
    else:
        kk = tg - tr
        goal(d, W / 2, 1300, 1.2)
        u = min(1, kk / 0.6)
        ball(d, lerp(W / 2 - 60, W / 2 + 470, u), lerp(1560, 960, u), lerp(46, 26, u), WHITE, tg * 9)
        P(img, W / 2 - 160, FEET, 260, "kick" if kk < 0.7 else "sad"); shadow(d, W / 2 - 160, FEET, 260)
        k2 = tg - M("deuxm", 99) + 0.1
        if k2 > 0: hit = stamp(img, "RATÉ À 2 MÈTRES", (W / 2, 520), 120, -4, k2, RED)
    return dict(hit=hit, bg=0.0)

def s_stamps(img, d, tg, k):
    dim(img, 0.5)
    bench(d, W / 2, 1700)
    P(img, W / 2 - 40, 1700 - 36 + 0.72 * 230 - 30, 230, "sit", alpha=0.75)
    hit = 0.0; cols = [RED, WHITE, AMBER]
    for i, (txt, t0) in enumerate(TJ["words3d"]):
        hit = max(hit, stamp(img, txt, (W / 2 + [-30, 40, 0][i], [420, 680, 940][i]), [150, 150, 150][i], [-8, 6, -4][i], tg - t0 + 0.06, cols[i]))
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
            if r > 0: d.ellipse((W / 2 - r, 1450 - r * 0.35, W / 2 + r, 1450 + r * 0.35), outline=ICE, width=max(1, int(16 * max(0, 1 - r / 1500))))
        burst(d, W / 2, 1100, kk, 22, 520, WHITE, 3, 9)
        flash = max(0, 0.9 - kb * 4) if kb > 0 else 0
        hit = max(0, 1 - kk / 0.3)
    shadow(d, W / 2, 1600, 320)
    P(img, W / 2, 1600, 320, pose, glow=1.0)
    if kb > -0.08:
        kk = kb + 0.08; sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 330), "IL S'EST", 100, ICE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 520), "RELEVÉ !", int(fit("RELEVÉ !", 220, 1000) * sc), WHITE, BOLD, stroke=10, scol=ICE)
    else:
        text(d, (W / 2, 420), typew("TOUT LÂCHER ?", max(0, tg - K["build_start"] + 0.2), 20), 100, GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_rennes(img, d, tg, k):
    hit = 0.0
    kg = tg - K["gate1"] + 0.15
    if kg <= 0:
        train(d, lerp(W + 100, -300, eout(k / 1.6)), 0.35)
        label(d, 420, "RETOUR EN FRANCE", tg - M("france", SC["rennes"] + 0.3) + 0.3, 92, WHITE, "UN CLUB, PUIS UN AUTRE", ICE)
        P(img, W / 2, FEET, 280, "stand"); shadow(d, W / 2, FEET, 280); suitcase(d, W / 2 + 190, FEET)
    else:
        for txt, tk, y in [("IL TRAVAILLE.", K["gate1"], 560), ("IL REVIENT.", M("revient", K["gate1"] + 0.6), 690), ("IL MARQUE.", K["gate2"], 820)]:
            kk = tg - tk + 0.15
            if kk > 0:
                text(d, (W / 2, y - 20 * (1 - eout(kk / 0.25))), txt, 96, GOLD if y == 820 else WHITE, BOLD, stroke=6, scol=BG)
                if kk < 0.3: hit = max(hit, 1 - kk / 0.3)
        km = tg - K["gate2"]
        P(img, W / 2, FEET, 300, run_pose(tg * 10) if km < 0 else blend_pose(POSES["kick"], POSES["up"], min(1, km / 0.5)))
        if km > 0:
            u = min(1, km / 0.5); ball(d, lerp(W / 2 + 150, W / 2 + 40, u), lerp(1600, 1050, u), lerp(40, 18, u), WHITE, tg * 9)
            burst(d, W / 2 + 40, 1050, km - 0.5, 16, 200, GOLD, 2)
    return dict(hit=hit, bg=0.35)

def counter(d, x, y, lab, n, col, size=200):
    text(d, (x, y), str(n), size, col, BOLD, stroke=7, scol=BG); text(d, (x, y + size * 0.72), lab, 52, WHITE, MONO)

def s_stuttgart(img, d, tg, k):
    hit = 0.0
    hit = max(hit, stamp(img, "2022", (W / 2, 290), 160, -5, tg - M("d2022", SC["stuttgart"] + 0.1) + 0.05, GOLD))
    t27 = M("vingtsept", 99)
    if tg < t27 - 0.15:
        kd = tg - M("descendre", 99) + 0.3
        if kd > 0:
            text(d, (W / 2, 540), "UN CLUB QUI SE BAT", fit("UN CLUB QUI SE BAT", 84, 980), WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 650), "POUR NE PAS DESCENDRE", fit("POUR NE PAS DESCENDRE", 84, 980), ICE, BOLD, stroke=6, scol=BG)
            ay = 780 + 40 * math.sin(tg * 6)
            d.polygon([(W / 2 - 50, ay), (W / 2 + 50, ay), (W / 2 + 50, ay + 110), (W / 2 + 110, ay + 110), (W / 2, ay + 220), (W / 2 - 110, ay + 110), (W / 2 - 50, ay + 110)], fill=RED)
        P(img, W / 2, FEET, 280, "stand"); shadow(d, W / 2, FEET, 280)
    else:
        k27 = tg - t27 + 0.1
        badge(d, W / 2, 560, "27 ANS", k27, ICE, 130)
        if k27 < 0.25: hit = max(hit, 1 - k27 / 0.25)
        t28 = M("vingthuit", 99); t28b = M("vingthuit2", 99)
        kb = tg - t28 + 0.15
        if kb > 0:
            n = min(28, int(eout(kb / 0.6) * 28)); counter(d, 300, 900, "BUTS", n, GOLD)
            if 0.55 < kb < 0.8: hit = max(hit, 1 - (kb - 0.55) / 0.25)
        km = tg - t28b + 0.1
        if km > 0: counter(d, 780, 900, "MATCHS", 28, WHITE)
        P(img, W / 2, 1720, 230, "up" if km > 0 else run_pose(tg * 10))
    return dict(hit=hit, bg=0.5)

def s_record(img, d, tg, k):
    hit = 0.0; flash = 0.0
    sc = 1 + 0.3 * (1 - eout(k / 0.2))
    text(d, (W / 2, 420), "13", int(320 * sc), GOLD, BOLD, stroke=9, scol=BG)
    text(d, (W / 2, 620), "BUTS", 90, WHITE, BOLD, stroke=6, scol=BG)
    k7 = tg - M("sept", 99) + 0.1
    if k7 > 0: text(d, (W / 2, 750), "EN 7 MATCHS", int(96 * (1 + 0.25 * (1 - eout(k7 / 0.2)))), ICE, BOLD, stroke=6, scol=BG)
    kr = tg - M("record", 99) + 0.05
    if kr > 0:
        hit = max(hit, stamp(img, "RECORD", (W / 2, 1000), 190, -6, kr, GOLD))
        if kr > 0.3: text(d, (W / 2, 1160), "DU CHAMPIONNAT", 64, WHITE, BOLD, stroke=5, scol=BG)
        burst(d, W / 2, 1000, kr, 20, 420, GOLD, 4)
        if kr < 0.2: flash = 0.25 * (1 - kr / 0.2)
    P(img, W / 2, 1760, 200, "up"); shadow(d, W / 2, 1760, 200)
    return dict(hit=max(hit, 1 - k / 0.25 if k < 0.25 else 0), flash=flash, bg=0.7)

def s_europe(img, d, tg, k):
    hit = 0.0; flash = 0.0
    label(d, 300, "MEILLEUR BUTEUR", tg - M("meilleur", SC["europe"] + 0.5) + 0.2, 100, WHITE) if tg > M("meilleur", 99) - 0.2 else None
    kc = tg - K["sunrise"] + 0.15
    if kc > 0:
        trophy(d, W / 2, 1060, 1.15 * (1 + 0.25 * (1 - eout(kc / 0.2))), GOLD)
        text(d, (W / 2, 450), "DE LA PLUS GRANDE", 76, WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 550), "COUPE D'EUROPE", fit("COUPE D'EUROPE", 100, 980), GOLD, BOLD, stroke=6, scol=BG)
        confetti(d, kc)
        if kc < 0.3: hit = 1 - kc / 0.3; flash = 0.3 * (1 - kc / 0.3)
    k13 = tg - M("treize2", 99) + 0.1
    if k13 > 0:
        badge(d, 230, 1300, "13 BUTS", k13, GOLD, 120)
        if k13 < 0.25: hit = max(hit, 1 - k13 / 0.25)
    ka = tg - M("africain", 99) + 0.1
    if ka > 0:
        badge(d, W - 250, 1300, "2e AFRICAIN", ka, ICE, 140)
        text(d, (W - 250, 1480), "DE L'HISTOIRE", 46, WHITE, BOLD, stroke=5, scol=BG)
        if ka < 0.25: hit = max(hit, 1 - ka / 0.25)
    P(img, W / 2, 1760, 210, "up" if kc > 0 else run_pose(tg * 10))
    return dict(hit=hit, flash=flash, bg=0.9)

def s_guinee(img, d, tg, k):
    hit = 0.0
    km = tg - M("maillot", SC["guinee"] + 0.5) + 0.2
    if km > 0:
        a = eout(km / 0.6)
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        for i, c in enumerate([(206, 17, 38), (252, 209, 22), (0, 148, 96)]):
            dl.rectangle((180 + i * 240, 640, 180 + (i + 1) * 240, 1240), fill=c + (int(230 * a),))
        img.alpha_composite(L); d = ImageDraw.Draw(img)
    text(d, (W / 2, 330), "AUJOURD'HUI", 100, WHITE, BOLD, stroke=6, scol=BG)
    kg = tg - M("guinee2", 99) + 0.1
    if kg > 0:
        text(d, (W / 2, 470), "LE MAILLOT DE LA GUINÉE", int(fit("LE MAILLOT DE LA GUINÉE", 86, 1000) * (1 + 0.3 * (1 - eout(kg / 0.2)))), GOLD, BOLD, stroke=7, scol=BG)
        if kg < 0.3: hit = 1 - kg / 0.3
    P(img, W / 2, 1720, 260, "up"); shadow(d, W / 2, 1720, 260)
    return dict(hit=hit, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ICE, BOLD, stroke=6, scol=BG)
    rows = [("RECALÉ", "à son essai"), ("4 MATCHS 0 BUT", "1re saison pro"), ("BLESSÉ", "loin de chez lui"), ("28 BUTS", "à 27 ans")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 90 - 80 * (1 - eout(kk / 0.2))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD if i == 3 else ICE)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 45, y), a, 42, GOLD if i == 3 else WHITE, MONO, "lm"); text(d, (x + 470, y), b, 40, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "JAMAIS ?", (W / 2, 1180), 150, -5, kn + 0.05, RED) if kn > -0.05 else 0.0
    return dict(hit=hit, bg=0.2)

NUMS = [(np.random.default_rng(i).uniform(140, W - 140), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["25 ANS", "30 ANS", "22 ANS", "27 ANS", "35 ANS", "20 ANS", "28 ANS", "40 ANS", "24 ANS", "32 ANS"])]
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
        text(d, (x, yy), s, 56, mix(BG, (70, 100, 130), a), BOLD)
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (30, 70, 100), a), BOLD)
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

SNOWAMT = {"hook": 1.0, "gare": 1.0, "essai": 0.6, "laval": 0.5, "lille": 0.8, "cologne": 1.0, "stamps": 1.0, "slam": 0.5, "rennes": 0.4,
           "stuttgart": 0.3, "record": 0.2, "europe": 0.15, "guinee": 0.1, "you": 0.5, "question": 0.4, "logo": 0.2}
def _wrap(name, f):
    def g(img, d, tg, k):
        snow(d, tg, SNOWAMT.get(name, 0.5)); return f(img, d, tg, k)
    return g
SCENES = {n: _wrap(n, f) for n, f in {"hook": s_hook, "gare": s_gare, "essai": s_essai, "laval": s_laval, "lille": s_lille, "cologne": s_cologne,
          "stamps": s_stamps, "slam": s_slam, "rennes": s_rennes, "stuttgart": s_stuttgart, "record": s_record, "europe": s_europe,
          "guinee": s_guinee, "you": s_you, "question": s_question, "logo": s_logo}.items()}
BGLEVEL = {"hook": 0.0, "gare": 0.05, "essai": 0.0, "laval": 0.0, "lille": 0.05, "cologne": 0.0, "stamps": 0.0, "slam": 0.1, "rennes": 0.35,
           "stuttgart": 0.5, "record": 0.7, "europe": 0.9, "guinee": 1.0, "you": 0.2, "question": 0.0, "logo": 0.0}

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

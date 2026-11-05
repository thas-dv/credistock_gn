# -*- coding: utf-8 -*-
"""Style « ligne » (05/11 v2, demandé par l'utilisateur : plus de personnage qui manipule le ballon) :
LA LIGNE DE CARRIÈRE — une ligne dorée façon plan de métro / carte au trésor sur fond de plan quadrillé bleu nuit, qui grimpe d'étape en étape
(âge / fait), plonge en rouge à la relégation, se DÉDOUBLE au tournant crié (« courir pour deux ») puis monte jusqu'au sommet ; dézoom final
sur tout le parcours. Aucun personnage, aucun nom de club à l'écran (étapes = âges, années, faits).
(Infrastructure reprise de render_phare.py.)
Ancien en-tête : Style « phare » : port de pêche la nuit (phare au faisceau tournant, bateaux, jetée, quai) -> aube dorée ; toise ; trottinette ;
personnage « athlète » détaillé (maillot sarcelle sans numéro). Série « ILS ONT FAILLI ABANDONNER » (bandeau 0–3 s + scène abonne).
Types : hook paris amateur port debut mesure course montee angleterre monde regard you abonne question logo
(05/11 : N'Golo Kanté, épisode 2 ; tournant crié « TROP PETIT ? ALORS IL VA COURIR POUR DEUX ! »).
Usage : python3 render_phare.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# palette « port » : port de pêche la nuit (phare, bateaux, quai de pierre, mer) -> aube dorée
NIGHT = (6, 12, 28); SKY2 = (22, 40, 74); DUSK = (236, 140, 90); DUSK2 = (255, 208, 140)
ACC = (255, 196, 64); AMBER = (255, 184, 80); ICE = (110, 200, 255); SNOW = (220, 230, 240)
ORANGE = ACC; PITCH = (40, 46, 56)
HOR = 1150; SEA1 = 1150; QUAY = 1420
JER = (40, 90, 200)
FEET = 1500

def lighthouse(d, x, y, s, lit):
    body = mix((150, 150, 160), (245, 245, 240), lit * 0.6 + 0.2); band = mix((90, 30, 34), (210, 50, 50), lit * 0.6 + 0.2)
    top = y - 520 * s
    d.polygon([(x - 46 * s, y), (x - 30 * s, top), (x + 30 * s, top), (x + 46 * s, y)], fill=body)
    for i in range(3):
        y0 = y - (90 + i * 150) * s; y1 = y0 - 60 * s
        w0 = lerp(46, 30, (y - y0) / (y - top)) * s; w1 = lerp(46, 30, (y - y1) / (y - top)) * s
        d.polygon([(x - w0, y0), (x - w1, y1), (x + w1, y1), (x + w0, y0)], fill=band)
    d.rectangle((x - 42 * s, top - 14 * s, x + 42 * s, top), fill=(30, 30, 36))
    d.rectangle((x - 26 * s, top - 74 * s, x + 26 * s, top - 14 * s), fill=(255, 236, 170))
    d.polygon([(x - 34 * s, top - 74 * s), (x, top - 112 * s), (x + 34 * s, top - 74 * s)], fill=(30, 30, 36))
    return (x, top - 44 * s)

def boat(d, x, y, s, col, mast=True):
    d.polygon([(x - 120 * s, y - 40 * s), (x + 130 * s, y - 40 * s), (x + 90 * s, y + 10 * s), (x - 100 * s, y + 10 * s)], fill=col)
    d.rectangle((x - 40 * s, y - 95 * s, x + 30 * s, y - 40 * s), fill=col)
    if mast:
        d.line((x + 60 * s, y - 40 * s, x + 60 * s, y - 230 * s), fill=col, width=max(3, int(6 * s)))
        d.line((x + 60 * s, y - 220 * s, x - 90 * s, y - 45 * s), fill=col, width=max(2, int(3 * s)))
        d.line((x + 60 * s, y - 220 * s, x + 130 * s, y - 45 * s), fill=col, width=max(2, int(3 * s)))

LAMP = (840, 0)
def make_bg(lit):
    global LAMP
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        night = mix(NIGHT, SKY2, u); day = mix((110, 130, 190), mix(DUSK, DUSK2, u), u ** 0.8)
        d.line((0, y, W, y), fill=mix(night, day, lit))
    rng = np.random.default_rng(4)
    for _ in range(130):
        x, y = rng.uniform(0, W), rng.uniform(0, HOR * 0.6); r = rng.uniform(1, 2.6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix(mix(NIGHT, SKY2, y / HOR), WHITE, (0.3 + 0.6 * rng.random()) * (1 - lit)))
    if lit < 0.5:
        d.ellipse((90, 520, 170, 600), fill=mix((236, 232, 214), SKY2, lit * 2))
    if lit > 0.25:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((W / 2 - 320, HOR - 340, W / 2 + 320, HOR + 200), fill=(255, 190, 110, int(190 * (lit - 0.25) / 0.75)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(70))); d = ImageDraw.Draw(img)
        d.ellipse((W / 2 - 110, HOR - 170, W / 2 + 110, HOR + 50), fill=mix((255, 150, 80), (255, 226, 160), lit))
    # falaises / ville lointaine
    far = mix((14, 20, 36), (120, 90, 100), lit * 0.7)
    d.polygon([(0, HOR - 70), (180, HOR - 110), (330, HOR - 60), (520, HOR - 40), (520, HOR + 2), (0, HOR + 2)], fill=far)
    for i in range(14):
        x = 20 + i * 34; hh = 30 + (i * 37) % 50
        d.rectangle((x, HOR - 60 - hh, x + 26, HOR), fill=far)
        if lit < 0.6 and i % 2 == 0: d.rectangle((x + 8, HOR - 50 - hh + 10, x + 14, HOR - 50 - hh + 18), fill=mix(AMBER, far, lit))
    # mer
    for y in range(SEA1, QUAY):
        u = (y - SEA1) / (QUAY - SEA1)
        d.line((0, y, W, y), fill=mix(mix((10, 22, 44), (6, 14, 28), u), mix((190, 140, 120), (70, 90, 120), u), lit))
    rng = np.random.default_rng(9)
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(SEA1 + 5, QUAY - 5); w = rng.uniform(20, 90)
        d.line((x - w, y, x + w, y), fill=mix((40, 60, 90), (255, 220, 170), lit * 0.8 + 0.1), width=2)
    # jetée + phare
    jet = mix((20, 24, 32), (110, 90, 90), lit * 0.7)
    d.polygon([(640, HOR + 70), (W, HOR + 40), (W, HOR + 95), (640, HOR + 100)], fill=jet)
    LAMP = lighthouse(d, 900, HOR + 50, 0.95, lit)
    # bateaux
    bc = mix((14, 18, 28), (90, 60, 60), lit * 0.7)
    boat(d, 300, HOR + 150, 0.9, bc); boat(d, 610, HOR + 200, 0.7, bc)
    # quai de pierre
    for y in range(QUAY, H):
        u = (y - QUAY) / (H - QUAY)
        d.line((0, y, W, y), fill=mix(mix((34, 38, 48), (20, 22, 30), u), mix((150, 130, 120), (100, 86, 80), u), lit * 0.85 + 0.1))
    d.rectangle((0, QUAY - 8, W, QUAY + 10), fill=mix((70, 76, 90), (210, 190, 170), lit * 0.8 + 0.1))
    for r in range(5):
        y = QUAY + 60 + r * 110
        d.line((0, y, W, y), fill=mix((24, 26, 34), (120, 100, 92), lit * 0.8), width=3)
        for x in range((r % 2) * 90, W, 180):
            d.line((x, y, x, y + 110), fill=mix((24, 26, 34), (120, 100, 92), lit * 0.8), width=3)
    for x in (110, 970):   # bittes d'amarrage
        d.rounded_rectangle((x - 30, QUAY - 70, x + 30, QUAY), 12, fill=mix((16, 18, 24), (60, 50, 50), lit))
        d.ellipse((x - 42, QUAY - 86, x + 42, QUAY - 60), fill=mix((16, 18, 24), (60, 50, 50), lit))
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

def beam(img, tg, amt=1.0):
    """faisceau tournant du phare."""
    if amt <= 0: return
    ang = (tg * 0.9) % (2 * math.pi)
    c = math.cos(ang); a = int(70 * amt * (0.35 + 0.65 * max(0, c)))
    if a <= 2: return
    L = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    x0, y0 = LAMP[0] / 2, LAMP[1] / 2; ln = 1400 * (0.25 + 0.75 * abs(math.sin(ang) if c < 0 else 1))
    dirx = -1 if math.sin(ang) < 0 else -1
    sp = 0.09
    pts = [(x0, y0), (x0 + dirx * ln * math.cos(sp) , y0 - ln * 0.18 - 80), (x0 + dirx * ln * math.cos(sp), y0 + ln * 0.08)]
    dl.polygon(pts, fill=(255, 236, 170, a))
    L = L.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    img.alpha_composite(L)

MOTES = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.3, 1.0)) for i in range(70)]
def dust(d, tg, amt=1.0):
    n = int(len(MOTES) * amt)
    for x0, y0, z in MOTES[:n]:
        y = (y0 - tg * 25 * z) % H; x = (x0 + tg * 70 * z + 30 * math.sin(tg * 0.7 * z + x0)) % W; r = 1.2 + 2.5 * z
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((60, 80, 110), (220, 230, 240), z))
POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-25, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))
POSES["ride"] = dict(t=-6, la=(-150, 70), ra=(-140, 60), ll=(-4, 0), rl=(30, -20))

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

def globe(d, cx, cy, r, rot, col=GOLD):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=10)
    for i in range(4):
        ph = rot + i * math.pi / 4; w = abs(math.cos(ph)) * r
        d.ellipse((cx - w, cy - r, cx + w, cy + r), outline=mix(BG, col, 0.8), width=5)
    for f in (-0.5, 0, 0.5):
        hw = r * math.sqrt(1 - f * f); d.line((cx - hw, cy + f * r, cx + hw, cy + f * r), fill=mix(BG, col, 0.8), width=5)

def scout(d, x, y, s, turned, col=(14, 16, 24)):
    sx = 1 - 2 * ease(turned)
    d.rounded_rectangle((x - 45 * s, y - 230 * s, x + 45 * s, y - 60 * s), int(20 * s), fill=col)
    d.ellipse((x - 32 * s, y - 300 * s, x + 32 * s, y - 236 * s), fill=col)
    d.rectangle((x - 34 * s, y - 60 * s, x - 8 * s, y), fill=col); d.rectangle((x + 8 * s, y - 60 * s, x + 34 * s, y), fill=col)
    if sx > -0.2:
        xa, xb = sorted((x + 30 * s * sx, x + 80 * s * sx)); d.rectangle((xa, y - 200 * s, xb, y - 130 * s), fill=(220, 220, 210))

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def confetti(d, kv):
    for x0, y0, c in CONF:
        y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[ICE, WHITE, GOLD][c])

def toise(d, x, yf, s, mark=None, col=WHITE):
    """règle de mesure verticale à côté du joueur (hauteur joueur ≈ 1.45·s = 1,68 m)."""
    pcm = 1.45 * s / 168.0
    y0 = yf - 200 * pcm
    d.rectangle((x - 18, y0, x + 18, yf), fill=(20, 24, 34), outline=mix(BG, col, 0.7), width=3)
    for cm in range(0, 201, 10):
        y = yf - cm * pcm; ln = 40 if cm % 50 == 0 else 22
        d.line((x + 18, y, x + 18 + ln, y), fill=mix(BG, col, 0.8), width=4 if cm % 50 == 0 else 2)
        if cm in (100, 150, 200):
            text(d, (x + 70, y), f"{cm / 100:.2f}".replace(".", ",").rstrip("0").rstrip(","), 34, mix(BG, col, 0.9), MONO, "lm")
    if mark is not None and mark > 0:
        y = yf - 168 * pcm; w = 300 * eout(mark / 0.3)
        d.line((x - 20 - w, y, x + 20, y), fill=ACC, width=6)
        return y
    return None

def scooter(d, x, y, s):
    c = (200, 210, 225)
    d.line((x - 0.45 * s, y + 4, x + 0.45 * s, y + 4), fill=c, width=int(0.06 * s))
    d.line((x + 0.4 * s, y, x + 0.32 * s, y - 0.95 * s), fill=c, width=int(0.05 * s))
    d.line((x + 0.2 * s, y - 0.95 * s, x + 0.45 * s, y - 0.95 * s), fill=c, width=int(0.05 * s))
    for wx in (x - 0.42 * s, x + 0.42 * s):
        r = 0.09 * s; d.ellipse((wx - r, y + 4, wx + r, y + 4 + 2 * r), fill=(20, 20, 26), outline=c, width=4)

def door(d, cx, cy, k):
    u = eout(k / 0.6)
    d.rectangle((cx - 110, cy - 200, cx + 110, cy + 200), fill=(18, 22, 32), outline=mix(BG, ACC, 0.8), width=6)
    L_w = 220 * u
    d.rectangle((cx - 110, cy - 194, cx - 110 + L_w, cy + 194), fill=mix((40, 40, 50), (255, 230, 160), u))
    d.polygon([(cx - 110 + L_w, cy - 194), (cx + 110, cy - 194 - 30 * (1 - u)), (cx + 110, cy + 194 + 30 * (1 - u)), (cx - 110 + L_w, cy + 194)], fill=(30, 34, 46))

def kid(img, d, x, y, s, tg, k):
    P(img, x, y, s, run_pose(tg * 9)); shadow(d, x, y, s)
    ball(d, x + 0.55 * s + 30 * math.sin(tg * 4), y - 0.12 * s - 60 * abs(math.sin(tg * 5)), 0.11 * s, WHITE, tg * 6)

def shadow(d, x, y, s, a=1.0):
    d.ellipse((x - 0.35 * s, y - 0.06 * s, x + 0.35 * s, y + 0.06 * s), fill=(10, 10, 14))

def arrow(d, cx, ay, up, col, k):
    u = eout(k / 0.5); off = (-60 if up else 60) * u
    y = ay + off
    if up:
        d.polygon([(cx - 60, y), (cx + 60, y), (cx + 60, y - 120), (cx + 130, y - 120), (cx, y - 250), (cx - 130, y - 120), (cx - 60, y - 120)], fill=col)
    else:
        d.polygon([(cx - 60, y), (cx + 60, y), (cx + 60, y + 120), (cx + 130, y + 120), (cx, y + 250), (cx - 130, y + 120), (cx - 60, y + 120)], fill=col)

# --------------------------------------------------------------- personnage « athlète » (dessin détaillé, sans visage, générique)
SKIN = (112, 72, 50); SKIN_D = (84, 52, 36); HAIR = (18, 14, 12); BOOT = (24, 24, 30); RIM = (225, 238, 255)
SS = 2  # sur-échantillonnage (anti-crénelage)

def _tap(d, p, q, w1, w2, col, caps=True):
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    d.polygon([(p[0] + nx * w1 / 2, p[1] + ny * w1 / 2), (q[0] + nx * w2 / 2, q[1] + ny * w2 / 2),
               (q[0] - nx * w2 / 2, q[1] - ny * w2 / 2), (p[0] - nx * w1 / 2, p[1] - ny * w1 / 2)], fill=col)
    if caps:
        d.ellipse((p[0] - w1 / 2, p[1] - w1 / 2, p[0] + w1 / 2, p[1] + w1 / 2), fill=col)
        d.ellipse((q[0] - w2 / 2, q[1] - w2 / 2, q[0] + w2 / 2, q[1] + w2 / 2), fill=col)

def _pt(a, b, u): return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)

def player(img, x, y, s, pose, rot=0.0, alpha=1.0, num="", jersey=(20, 170, 110), glow=1.0, shorts=None, sock=None, facing=1, **kw):
    """Athlète stylisé détaillé (membres effilés, maillot ombré, short, chaussettes, crampons, cheveux), sans visage.
    (x, y) = pieds au sol ; hauteur ≈ 1.45·s."""
    if isinstance(pose, str): pose = POSES[pose]
    shorts = shorts or (236, 236, 240); sock = sock or jersey
    S = s * SS
    L = Image.new("RGBA", (int(3.2 * S), int(3.4 * S)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ox, oy = 1.6 * S, 1.75 * S
    hip = (ox, oy)
    td = _dir(180 + pose["t"]); neck = (hip[0] + td[0] * 0.5 * S, hip[1] + td[1] * 0.5 * S)
    head = (neck[0] + td[0] * 0.17 * S, neck[1] + td[1] * 0.17 * S)
    def limb(root, a1, a2, l1, l2):
        d1 = _dir(a1 + pose["t"] * 0.3); j = (root[0] + d1[0] * l1 * S, root[1] + d1[1] * l1 * S)
        d2 = _dir(a1 + a2 + pose["t"] * 0.3); e = (j[0] + d2[0] * l2 * S, j[1] + d2[1] * l2 * S)
        return j, e
    sh = (neck[0] - td[0] * 0.03 * S, neck[1] - td[1] * 0.03 * S)
    perp = (-td[1], td[0])
    shL = (sh[0] - perp[0] * 0.12 * S, sh[1] - perp[1] * 0.12 * S); shR = (sh[0] + perp[0] * 0.12 * S, sh[1] + perp[1] * 0.12 * S)
    hpL = (hip[0] - perp[0] * 0.07 * S, hip[1] - perp[1] * 0.07 * S); hpR = (hip[0] + perp[0] * 0.07 * S, hip[1] + perp[1] * 0.07 * S)
    la = limb(shL, *pose["la"], 0.26, 0.25); ra = limb(shR, *pose["ra"], 0.26, 0.25)
    ll = limb(hpL, *pose["ll"], 0.37, 0.36); rl = limb(hpR, *pose["rl"], 0.37, 0.36)
    jd = mix(jersey, (0, 0, 0), 0.32); jl = mix(jersey, (255, 255, 255), 0.18)
    def leg(root, lg, back):
        k, f = lg; sk = SKIN_D if back else SKIN
        _tap(d, root, k, 0.15 * S, 0.11 * S, sk)
        _tap(d, k, f, 0.11 * S, 0.07 * S, sk)
        _tap(d, _pt(k, f, 0.35), f, 0.105 * S, 0.08 * S, mix(sock, (0, 0, 0), 0.25) if back else sock)
        dd = _pt(k, f, 0.5); d.line((dd[0] - 0.05 * S, dd[1], dd[0] + 0.05 * S, dd[1]), fill=(250, 250, 250), width=max(2, int(0.018 * S)))
        cx, cy = f[0] - k[0], f[1] - k[1]; Lc = math.hypot(cx, cy) or 1
        fx, fy = (-cy / Lc * facing, cx / Lc * facing)   # direction du pied
        if fy > 0.5: fx, fy = facing, 0.0
        toe = (f[0] + fx * 0.16 * S, f[1] + fy * 0.16 * S + 0.02 * S)
        _tap(d, (f[0] - fx * 0.03 * S, f[1] + 0.01 * S), toe, 0.085 * S, 0.06 * S, BOOT)
        d.line((f[0] - fx * 0.02 * S, f[1] + 0.045 * S, toe[0], toe[1] + 0.02 * S), fill=(200, 200, 205), width=max(2, int(0.012 * S)))
    def arm(root, am, back):
        e, h = am; sk = SKIN_D if back else SKIN
        _tap(d, root, e, 0.095 * S, 0.075 * S, sk)
        _tap(d, e, h, 0.075 * S, 0.06 * S, sk)
        d.ellipse((h[0] - 0.045 * S, h[1] - 0.045 * S, h[0] + 0.045 * S, h[1] + 0.045 * S), fill=sk)
        _tap(d, _pt(root, e, -0.12), _pt(root, e, 0.45), 0.115 * S, 0.1 * S, jd if back else jersey, caps=False)
    # arrière-plan : bras et jambe du fond
    arm(shR, ra, True); leg(hpR, rl, True)
    # short (haut des cuisses + bassin)
    for root, lg in ((hpR, rl), (hpL, ll)):
        _tap(d, root, _pt(root, lg[0], 0.42), 0.19 * S, 0.165 * S, shorts if lg is ll else mix(shorts, (0, 0, 0), 0.18))
    d.ellipse((hip[0] - 0.15 * S, hip[1] - 0.08 * S, hip[0] + 0.15 * S, hip[1] + 0.08 * S), fill=shorts)
    leg(hpL, ll, False)
    for root, lg in ((hpL, ll),):
        _tap(d, root, _pt(root, lg[0], 0.42), 0.19 * S, 0.165 * S, shorts)
    # torse (maillot ombré)
    w1, w2 = 0.14 * S, 0.17 * S
    A = (hip[0] + perp[0] * w1, hip[1] + perp[1] * w1); B = (hip[0] - perp[0] * w1, hip[1] - perp[1] * w1)
    C = (sh[0] - perp[0] * w2, sh[1] - perp[1] * w2); D = (sh[0] + perp[0] * w2, sh[1] + perp[1] * w2)
    d.polygon([A, B, C, D], fill=jersey)
    mid_h = hip; mid_s = sh
    d.polygon([mid_h, B, C, mid_s], fill=jd)
    d.polygon([_pt(A, D, 0.15), _pt(mid_h, mid_s, 0.15), _pt(mid_h, mid_s, 0.85), _pt(A, D, 0.85)], fill=jl)
    d.line((A, B), fill=jd, width=max(2, int(0.03 * S)))
    # cou, tête, cheveux
    _tap(d, neck, _pt(neck, head, 0.6), 0.075 * S, 0.07 * S, SKIN_D)
    cv = _pt(sh, neck, 0.2); d.polygon([(cv[0] + perp[0] * 0.07 * S, cv[1] + perp[1] * 0.07 * S), (cv[0] - perp[0] * 0.07 * S, cv[1] - perp[1] * 0.07 * S),
                                         (cv[0] - td[0] * 0.07 * S, cv[1] - td[1] * 0.07 * S)], fill=jd)
    rx, ry = 0.095 * S, 0.115 * S
    d.ellipse((head[0] - rx, head[1] - ry, head[0] + rx, head[1] + ry), fill=SKIN)
    d.pieslice((head[0] - rx * 1.04, head[1] - ry * 1.08, head[0] + rx * 1.04, head[1] + ry * 0.7), 180 + pose["t"] - 15, 360 + pose["t"] + 15, fill=HAIR)
    d.ellipse((head[0] - rx * 0.2 + facing * rx * 0.55, head[1] - ry * 0.05, head[0] + rx * 0.2 + facing * rx * 0.55, head[1] + ry * 0.35), fill=SKIN_D)
    # bras de devant
    arm(shL, la, False)
    # réduction + liseré lumineux
    L = L.resize((L.width // SS, L.height // SS), Image.LANCZOS)
    ox, oy = ox / SS, oy / SS
    if glow > 0:
        a = L.getchannel("A").filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
        R = Image.new("RGBA", L.size, RIM + (0,)); R.putalpha(a.point(lambda v: int(v * 0.85 * min(1, glow))))
        R.alpha_composite(L); L = R
    if rot: L = L.rotate(rot, resample=Image.BICUBIC, center=(ox, oy))
    if alpha < 1:
        aa = np.asarray(L).copy(); aa[..., 3] = (aa[..., 3] * alpha).astype(np.uint8); L = Image.fromarray(aa)
    drop = 0.6 * s * abs(math.sin(math.radians(rot)))
    img.alpha_composite(L, (int(x - ox), int(y - oy - 0.73 * s + drop)))

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    for x, h in ((150, 1.0), (930, 1.08)):   # grandes silhouettes qui dominent
        sx = x; top = FEET - 1100 * h
        d.rounded_rectangle((sx - 110, top + 170, sx + 110, FEET - 330), 60, fill=(8, 10, 16))
        d.ellipse((sx - 80, top, sx + 80, top + 160), fill=(8, 10, 16))
        d.rectangle((sx - 90, FEET - 340, sx - 20, FEET), fill=(8, 10, 16)); d.rectangle((sx + 20, FEET - 340, sx + 90, FEET), fill=(8, 10, 16))
    toise(d, 330, FEET, 200, max(0, tg - 0.6))
    P(img, W / 2 + 40, FEET, 200, "stand"); shadow(d, W / 2 + 40, FEET, 200)
    kk = tg - K["hook"]
    text(d, (W / 2, 250), typew("ON T'A DÉJÀ DIT…", tg + 0.3, 26), 84, ACC, BOLD, stroke=6, scol=BG)
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 470), "TROP", int(fit("TROP", 170, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        text(d, (W / 2, 650), "PETIT ?", int(fit("PETIT ?", 190, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        hit = max(0, 1 - kk / 0.25)
    return dict(hit=hit, bg=0.0)

def s_paris(img, d, tg, k):
    hit = 0.0
    label(d, 300, "NÉ À PARIS", k, 110, WHITE)
    km = tg - M("mali", 99) + 0.2
    if km > 0: text(d, (W / 2, 430), typew("PARENTS VENUS DU MALI", km, 30), fit("PARENTS VENUS DU MALI", 66, 980), ACC, BOLD, stroke=5, scol=BG)
    kt = tg - M("taille", 99) + 0.15
    y = toise(d, 300, FEET, 300, kt if kt > 0 else None)
    P(img, 560, FEET, 300, "stand"); shadow(d, 560, FEET, 300)
    if kt > 0:
        badge(d, 800, 720, "1,68 m", kt, ACC, 130)
        if kt < 0.25: hit = 1 - kt / 0.25
    return dict(hit=hit, bg=0.05)

def s_amateur(img, d, tg, k):
    hit = 0.0
    kr = tg - M("remarquent", 99) + 0.2
    if kr <= 0:
        x = lerp(-100, W + 100, (k / 4.5) % 1.0)
        kid(img, d, x, FEET, 190, tg, k)
        label(d, 300, "UN PETIT CLUB", k + 0.1, 100, WHITE, "AMATEUR", ACC)
        kd = tg - M("dix", 99) + 0.1
        if kd > 0:
            badge(d, W / 2, 720, "10 ANS", kd, GOLD, 120)
            if kd < 0.25: hit = 1 - kd / 0.25
    else:
        dim(img, 0.25)
        for i, x in enumerate((200, 540, 880)): scout(d, x, 1440, 1.5, min(1, kr / 0.5))
        P(img, W / 2, 1500, 130, "stand", alpha=0.9)
        text(d, (W / 2, 300), "LES GRANDS CLUBS", fit("LES GRANDS CLUBS", 88, 980), WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 410), "NE LE VOIENT PAS", fit("NE LE VOIENT PAS", 88, 980), GREY, BOLD, stroke=6, scol=BG)
        hit = stamp(img, "RECALÉ", (W / 2, 700), 190, -7, tg - M("recale", 99) + 0.05, RED)
    return dict(hit=hit, bg=0.05)

def s_port(img, d, tg, k):
    hit = 0.0
    beam(img, tg, 1.0); d = ImageDraw.Draw(img)
    k19 = tg - M("dixneuf", SC["port"] + 0.1) + 0.1
    if k19 > 0:
        badge(d, 220, 300, "19 ANS", k19, GOLD, 110)
        if k19 < 0.25: hit = 1 - k19 / 0.25
    kt = tg - M("toujours", 99) + 0.1
    if kt > 0: text(d, (680, 300), "TOUJOURS", int(fit("TOUJOURS", 96, 560)), WHITE, BOLD, stroke=6, scol=BG); text(d, (680, 400), "AMATEUR", 80, ACC, BOLD, stroke=6, scol=BG)
    ktr = tg - M("trotti", 99) + 0.2
    kp = tg - M("porte", 99) + 0.2
    if ktr <= 0:
        if kp > 0:
            door(d, W / 2, 820, kp)
            text(d, (W / 2, 560), "UNE PETITE PORTE", fit("UNE PETITE PORTE", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
            krs = tg - M("reserve", 99) + 0.1
            if krs > 0: hit = max(hit, stamp(img, "L'ÉQUIPE RÉSERVE", (W / 2, 1110), 90, -4, krs, ACC))
        P(img, 250 if kp > 0 else W / 2, FEET, 200, "stand"); shadow(d, 250 if kp > 0 else W / 2, FEET, 200)
    else:
        x = lerp(-120, W + 160, min(1.0, ktr / 2.6))
        for i in range(6): d.line((x - 160 - i * 45, FEET - 190 + i * 28, x - 300 - i * 70, FEET - 190 + i * 28), fill=mix(BG, SNOW, 0.5), width=4)
        scooter(d, x, FEET, 240)
        P(img, x - 10, FEET - 10, 230, "ride"); shadow(d, x, FEET + 30, 240)
        text(d, (W / 2, 640), "À L'ENTRAÎNEMENT", fit("À L'ENTRAÎNEMENT", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
        hit = max(hit, stamp(img, "EN TROTTINETTE", (W / 2, 800), 110, -4, ktr - 0.15, ACC))
    return dict(hit=hit, bg=0.0)

def s_debut(img, d, tg, k):
    hit = 0.0
    beam(img, tg, 0.7); d = ImageDraw.Draw(img); dim(img, 0.2); d = ImageDraw.Draw(img)
    k21 = tg - M("vingtun", SC["debut"] + 0.1) + 0.1
    if k21 > 0:
        badge(d, 220, 300, "21 ANS", k21, GOLD, 110)
        if k21 < 0.25: hit = 1 - k21 / 0.25
    kp = tg - M("pro", 99) + 0.1
    if kp > 0: text(d, (680, 300), "1er MATCH PRO", int(fit("1er MATCH PRO", 92, 600) * (1 + 0.3 * (1 - eout(kp / 0.2)))), WHITE, BOLD, stroke=6, scol=BG)
    kr = tg - M("relegue", 99) + 0.05
    if kr > 0: hit = max(hit, stamp(img, "DÉJÀ RELÉGUÉ", (W / 2, 560), 120, -5, kr, RED))
    k3 = tg - M("troisieme", 99) + 0.15
    if k3 > 0:
        arrow(d, W / 2, 760, False, RED, k3)
        text(d, (W / 2, 1170), "3e DIVISION", int(fit("3e DIVISION", 120, 980) * (1 + 0.2 * (1 - eout(k3 / 0.2)))), WHITE, BOLD, stroke=7, scol=RED)
        if k3 < 0.25: hit = max(hit, 1 - k3 / 0.25)
    P(img, W / 2, FEET, 220, "sad" if kr > 0 else "stand", alpha=0.95)
    return dict(hit=hit, bg=0.0)

def s_stamps(img, d, tg, k):
    dim(img, 0.5)
    P(img, W / 2, 1500, 230, "sad", alpha=0.8)
    hit = 0.0; cols = [RED, WHITE, AMBER]
    for i, (txt, t0) in enumerate(TJ["words3d"]):
        hit = max(hit, stamp(img, txt, (W / 2 + [-30, 40, 0][i], [420, 680, 940][i]), 150, [-8, 6, -4][i], tg - t0 + 0.06, cols[i]))
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
            if r > 0: d.ellipse((W / 2 - r, 1450 - r * 0.35, W / 2 + r, 1450 + r * 0.35), outline=ACC, width=max(1, int(16 * max(0, 1 - r / 1500))))
        burst(d, W / 2, 1100, kk, 22, 520, WHITE, 3, 9)
        flash = max(0, 0.9 - kb * 4) if kb > 0 else 0
        hit = max(0, 1 - kk / 0.3)
    shadow(d, W / 2, 1500, 300)
    P(img, W / 2, 1500, 300, pose, glow=1.0)
    if kb > -0.08:
        kk = kb + 0.08; sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 330), "IL A", 110, ACC, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 520), "CONTINUÉ !", int(fit("CONTINUÉ !", 200, 1000) * sc), WHITE, BOLD, stroke=10, scol=ACC)
    else:
        text(d, (W / 2, 420), typew("ABANDONNER ?", max(0, tg - K["build_start"] + 0.2), 24), fit("ABANDONNER ?", 110, 1000), GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_montee(img, d, tg, k):
    hit = 0.0
    t1 = M("trente", SC["montee"] + 0.5); t2 = M("trente2", t1 + 1.0)
    kc = tg - t1 + 0.1
    if kc > 0:
        n = 38 if tg >= t2 - 0.1 else min(38, int(38 * eout(kc / max(0.3, t2 - t1))))
        text(d, (W / 2, 380), f"{n} / 38", int(190 * (1 + 0.15 * (1 - eout(kc / 0.2)))), WHITE, BOLD, stroke=8, scol=BG)
        text(d, (W / 2, 540), "MATCHS JOUÉS", 70, ACC, BOLD, stroke=5, scol=BG)
        if tg >= t2 - 0.1 and tg < t2 + 0.15: hit = 0.8
    else:
        label(d, 380, "UN NOUVEAU CLUB", k, 84, WHITE)
    km = tg - M("montee", 99) + 0.15
    if km > 0:
        arrow(d, W / 2, 960, True, GREEN, km)
        hit = max(hit, stamp(img, "LA MONTÉE", (W / 2, 1060), 130, -4, km, GREEN))
        if km > 0.4: text(d, (W / 2, 1180), "EN 1re DIVISION", 70, WHITE, BOLD, stroke=5, scol=BG)
    P(img, W / 2, 1500, 170, "up" if km > 0 else run_pose(tg * 11))
    return dict(hit=hit, bg=0.45)

def s_angleterre(img, d, tg, k):
    hit = 0.0; flash = 0.0
    kc = tg - K["gate1"] + 0.1
    kc2 = tg - K["gate2"] + 0.1
    if kc <= 0:
        label(d, 400, "L'ANGLETERRE", k, 110, WHITE)
        P(img, W / 2, 1500, 220, run_pose(tg * 10))
    else:
        trophy(d, 330, 1020, 0.75 * (1 + 0.25 * (1 - eout(kc / 0.2))), GOLD)
        hit = stamp(img, "CHAMPION", (270, 690), 72, -5, kc, GOLD)
        if kc2 > 0:
            trophy(d, 760, 1020, 0.75 * (1 + 0.25 * (1 - eout(kc2 / 0.2))), GOLD)
            hit = max(hit, stamp(img, "ENCORE !", (720, 690), 72, 5, kc2, ACC))
        ke = tg - M("elu", 99) + 0.1
        if ke > 0:
            text(d, (W / 2, 300), "ÉLU MEILLEUR JOUEUR", fit("ÉLU MEILLEUR JOUEUR", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 400), "PAR LES JOUEURS", 60, ACC, BOLD, stroke=5, scol=BG)
            star(d, W / 2, 1150, 100 * (1 + 0.3 * (1 - eout(ke / 0.2))), GOLD)
            if ke < 0.25: hit = max(hit, 1 - ke / 0.25); flash = 0.2 * (1 - ke / 0.25)
        P(img, W / 2, 1500, 170, "up")
    return dict(hit=hit, flash=flash, bg=0.7)

def s_monde(img, d, tg, k):
    hit = 0.0; flash = 0.0
    k21 = tg - M("d2021", 99) + 0.1
    if k21 <= 0:
        hit = stamp(img, "2018", (W / 2, 280), 160, -5, tg - M("d2018", SC["monde"] + 0.1) + 0.05, GOLD)
        kw = tg - K["sunrise"] + 0.15
        if kw > 0:
            globe(d, W / 2, 900, 260 * (1 + 0.2 * (1 - eout(kw / 0.25))), tg * 1.5, GOLD)
            text(d, (W / 2, 1270), "CHAMPION DU MONDE", fit("CHAMPION DU MONDE", 100, 980), GOLD, BOLD, stroke=7, scol=BG)
            confetti(d, kw)
            if kw < 0.3: hit = max(hit, 1 - kw / 0.3); flash = 0.3 * (1 - kw / 0.3)
        else:
            text(d, (W / 2, 520), "IL GAGNE…", 100, WHITE, BOLD, stroke=6, scol=BG)
    else:
        hit = stamp(img, "2021", (W / 2, 280), 160, -5, k21 + 0.05, GOLD)
        ke = tg - M("europe", 99) + 0.1
        if ke > 0:
            trophy(d, W / 2, 1000, 1.0 * (1 + 0.25 * (1 - eout(ke / 0.2))), GOLD)
            text(d, (W / 2, 460), "LA PLUS GRANDE", 76, WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 570), "COUPE D'EUROPE", fit("COUPE D'EUROPE", 104, 980), GOLD, BOLD, stroke=6, scol=BG)
            if ke < 0.3: hit = max(hit, 1 - ke / 0.3)
        kh = tg - M("homme", 99) + 0.1
        if kh > 0:
            hit = max(hit, stamp(img, "HOMME DU MATCH", (W / 2, 1200), 110, -4, kh, ACC))
            if kh > 0.3: text(d, (W / 2, 1340), "DE LA FINALE", 64, WHITE, BOLD, stroke=5, scol=BG)
            confetti(d, kh)
    if not (k21 > 0 and tg - M("homme", 99) + 0.1 > 0): P(img, W / 2, 1500, 190, "up")
    return dict(hit=hit, flash=flash, bg=0.95)

def s_regard(img, d, tg, k):
    hit = 0.0
    kr = tg - M("regarde", 99) + 0.15
    text(d, (W / 2, 300), "PERSONNE", 110, GREY if kr > 0 else WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 420), "NE LE REMARQUAIT", fit("NE LE REMARQUAIT", 80, 980), GREY if kr > 0 else WHITE, BOLD, stroke=6, scol=BG)
    if kr > 0:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        u = eout(kr / 0.5)
        for sx in (-100, 250, W - 250, W + 100):
            dl.polygon([(sx, 0), (sx + 90, 0), (W / 2 + 90 * u, FEET), (W / 2 - 90 * u, FEET)], fill=(255, 236, 180, int(60 * u)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(img)
        text(d, (W / 2, 620), "TOUT LE MONDE", int(fit("TOUT LE MONDE", 120, 980) * (1 + 0.3 * (1 - eout(kr / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
        hit = stamp(img, "LE REGARDE", (W / 2, 790), 130, -4, kr, ACC)
    toise(d, 300, FEET, 280, 1.0)
    P(img, W / 2 + 60, FEET, 280, "up" if kr > 0 else "stand", glow=1.0); shadow(d, W / 2 + 60, FEET, 280)
    return dict(hit=hit, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ACC, BOLD, stroke=6, scol=BG)
    rows = [("1,68 m", "trop petit"), ("RECALÉ", "amateur à 19 ans"), ("38 / 38", "la montée"), ("CHAMPION", "du monde")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 90 - 80 * (1 - eout(kk / 0.2))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD if i == 3 else ACC)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 45, y), a, 42, GOLD if i == 3 else WHITE, MONO, "lm"); text(d, (x + 470, y), b, 40, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "TE MESURER ?", (W / 2, 1180), 140, -5, kn + 0.05, RED) if kn > -0.05 else 0.0
    return dict(hit=hit, bg=0.2)

NUMS = [(np.random.default_rng(i).uniform(140, W - 140), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["8/10", "10/10", "6/10", "9/10", "7/10", "5/10", "10/10", "8/10", "9/10", "7/10"])]
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


DUSTAMT = {"hook": 0.5, "paris": 0.6, "amateur": 0.6, "port": 0.8, "debut": 0.6, "stamps": 0.4, "slam": 0.8, "montee": 0.6,
           "angleterre": 0.7, "monde": 0.8, "regard": 0.8, "you": 0.4, "question": 0.3, "logo": 0.2}
def _wrap(name, f):
    def g(img, d, tg, k):
        dust(d, tg, DUSTAMT.get(name, 0.5)); return f(img, d, tg, k)
    return g
SCENES = {n: _wrap(n, f) for n, f in {"hook": s_hook, "paris": s_paris, "amateur": s_amateur, "port": s_port, "debut": s_debut,
          "stamps": s_stamps, "slam": s_slam, "montee": s_montee, "angleterre": s_angleterre, "monde": s_monde, "regard": s_regard,
          "you": s_you, "question": s_question, "logo": s_logo}.items()}
BGLEVEL = {"hook": 0.0, "paris": 0.05, "amateur": 0.05, "port": 0.0, "debut": 0.0, "stamps": 0.0, "slam": 0.1, "montee": 0.45,
           "angleterre": 0.7, "monde": 0.95, "regard": 1.0, "you": 0.2, "question": 0.0, "logo": 0.0}


# --------------------------------------------------------------- 05/11 : série « ILS ONT FAILLI ABANDONNER — Épisode 2 » (N'Golo Kanté) — aucun nom propre à l'écran
JER = (0, 150, 150)   # maillot sarcelle sans numéro (aucune couleur d'équipe réelle)
EPISODE = 2

def series_banner(d, tg):
    if tg > 3.6: return
    a = min(1, tg / 0.15) * (1 - ease((tg - 3.2) / 0.4))
    c = mix(BG, WHITE, a); g = mix(BG, GOLD, a)
    d.rounded_rectangle((90, 70, W - 90, 200), 22, fill=mix(BG, (10, 40, 60), a), outline=g, width=4)
    text(d, (W / 2, 115), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), c, BOLD)
    text(d, (W / 2, 168), f"ÉPISODE {EPISODE}", 40, g, MONO)

_s_hook_old = s_hook
def s_hook(img, d, tg, k):
    R = _s_hook_old(img, d, tg, k)
    series_banner(d, tg)
    return R

def s_paris(img, d, tg, k):
    hit = 0.0
    kn = tg - M("ne", 99) + 0.1
    if kn <= 0:
        series_banner(d, tg)
        label(d, 330, "L'HISTOIRE VRAIE", k, 96, WHITE, "D'UN FOOTBALLEUR", ACC)
        ka = tg - M("lamateur", 99) + 0.1
        if ka > 0:
            dim(img, 0.35); d = ImageDraw.Draw(img)
            text(d, (W / 2, 330), "L'HISTOIRE VRAIE", fit("L'HISTOIRE VRAIE", 96, 980), WHITE, BOLD, stroke=5, scol=BG)
            text(d, (W / 2, 520), "DE L'AMATEUR", int(fit("DE L'AMATEUR", 120, 980) * (1 + 0.25 * (1 - eout(ka / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
            arrow(d, W / 2, 960, True, GREEN, ka)
            hit = stamp(img, "AU PRO", (W / 2, 1110), 150, -5, ka - 0.15, GOLD)
        P(img, 230, FEET, 200, "stand"); shadow(d, 230, FEET, 200)
        return dict(hit=hit, bg=0.05)
    label(d, 300, "NÉ À PARIS", kn, 110, WHITE)
    km = tg - M("mali", 99) + 0.2
    if km > 0: text(d, (W / 2, 430), typew("PARENTS VENUS DU MALI", km, 30), fit("PARENTS VENUS DU MALI", 66, 980), ACC, BOLD, stroke=5, scol=BG)
    kt = tg - M("taille", 99) + 0.15
    toise(d, 300, FEET, 300, kt if kt > 0 else None)
    P(img, 560, FEET, 300, "stand"); shadow(d, 560, FEET, 300)
    if kt > 0:
        badge(d, 800, 720, "1,68 m", kt, ACC, 130)
        if kt < 0.25: hit = 1 - kt / 0.25
    return dict(hit=hit, bg=0.05)

def s_mesure(img, d, tg, k):
    """« Tout le monde le mesure. Personne ne le regarde. » : toises géantes, recruteurs qui tournent le dos."""
    hit = 0.0
    dim(img, 0.35); d = ImageDraw.Draw(img)
    km = tg - M("mesure", SC["mesure"]) + 0.1
    for i, x in enumerate((150, 930)):
        if km > i * 0.15: toise(d, x, FEET, 420, None, GREY)
    if km > 0:
        text(d, (W / 2, 300), "TOUT LE MONDE", fit("TOUT LE MONDE", 100, 980), WHITE, BOLD, stroke=6, scol=BG)
        hit = stamp(img, "LE MESURE", (W / 2, 450), 120, -4, km, RED)
    kr = tg - K["build_end"] + 0.6
    kp = tg - M("personne", 99) + 0.1
    if kp > 0:
        for x in (300, 780): scout(d, x, 1460, 1.4, min(1, kp / 0.5))
        text(d, (W / 2, 640), typew("PERSONNE NE LE REGARDE", kp, 30), fit("PERSONNE NE LE REGARDE", 74, 980), GREY, BOLD, stroke=5, scol=BG)
    P(img, W / 2, FEET, 210, "stand", alpha=0.85 if kp > 0 else 0.95, glow=0.3 if kp > 0 else 0.6); shadow(d, W / 2, FEET, 210)
    return dict(hit=hit, bg=0.0)

def s_course(img, d, tg, k):
    """tournant crié : « TROP PETIT ? ALORS IL VA COURIR POUR DEUX ! » — le phare s'allume, il sprinte sur le quai, son double le suit."""
    kb = tg - K["boom"]; kc = tg - M("courir", K["boom"] + 0.8) + 0.08
    hit = 0.0; flash = 0.0; bgl = 0.15
    if kb < -0.05:
        dim(img, 0.5); d = ImageDraw.Draw(img)
        P(img, W / 2, FEET, 230, "stand", alpha=0.85, glow=0.3); shadow(d, W / 2, FEET, 230)
        return dict(hit=0.0, bg=0.0)
    kk = kb + 0.05
    beam(img, tg * 3, 1.6); d = ImageDraw.Draw(img)
    if kk < 0.35: flash = max(0, 0.9 - kk * 2.6)
    if kc <= 0:
        sc = 1 + 1.0 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 420), "TROP", int(fit("TROP", 180, 1000) * sc), WHITE, BOLD, stroke=9, scol=RED)
        text(d, (W / 2, 620), "PETIT ?", int(fit("PETIT ?", 200, 1000) * sc), WHITE, BOLD, stroke=9, scol=RED)
        P(img, W / 2, FEET, 260, blend_pose(POSES["stand"], POSES["up"], eout(kk / 0.4)), glow=1.4); shadow(d, W / 2, FEET, 260)
        hit = max(0, 1 - kk / 0.3)
    else:
        bgl = 0.35
        u = (kc / 1.4) % 1.0
        x = lerp(-150, W + 200, u)
        for i in range(8):
            yy = FEET - 330 + i * 40
            d.line((x - 200 - i * 30, yy, x - 520 - i * 60, yy), fill=mix(BG, ACC, 0.6), width=5)
        P(img, x - 230, FEET, 240, run_pose(tg * 13 + 1.5), alpha=0.45, glow=0.6)   # son « double »
        P(img, x, FEET, 260, run_pose(tg * 13), glow=1.5); shadow(d, x, FEET, 260)
        e = eout(kc / 0.2)
        text(d, (W / 2, 330), "ALORS IL VA", fit("ALORS IL VA", 110, 1000), WHITE, BOLD, stroke=7, scol=BG)
        for off, c in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, GOLD)):
            o = off * (1 - e)
            text(d, (W / 2 + o, 500), "COURIR", int(fit("COURIR", 200, 1000) * (1 + 0.5 * (1 - e))), c, BOLD, stroke=10 if c == GOLD else 0, scol=BG)
        kd = tg - M("deux", 99) + 0.05
        if kd > 0: hit = max(hit, stamp(img, "POUR DEUX !", (W / 2, 720), 150, -5, kd, ACC))
        if kc < 0.25: hit = max(hit, 1 - kc / 0.25)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_regard(img, d, tg, k):
    hit = 0.0
    kr = tg - M("regarde", 99) + 0.15
    text(d, (W / 2, 300), "LE PETIT QUE PERSONNE", fit("LE PETIT QUE PERSONNE", 80, 980), GREY if kr > 0 else WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 400), "NE REGARDAIT…", fit("NE REGARDAIT…", 80, 980), GREY if kr > 0 else WHITE, BOLD, stroke=6, scol=BG)
    if kr > 0:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        u = eout(kr / 0.5)
        for sx in (-100, 250, W - 250, W + 100):
            dl.polygon([(sx, 0), (sx + 90, 0), (W / 2 + 90 * u, FEET), (W / 2 - 90 * u, FEET)], fill=(255, 236, 180, int(60 * u)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(img)
        text(d, (W / 2, 620), "LE MONDE ENTIER", int(fit("LE MONDE ENTIER", 116, 980) * (1 + 0.3 * (1 - eout(kr / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
        hit = stamp(img, "LE REGARDE", (W / 2, 790), 130, -4, kr, ACC)
    toise(d, 300, FEET, 280, 1.0)
    P(img, W / 2 + 60, FEET, 280, "up" if kr > 0 else "stand", glow=1.0); shadow(d, W / 2 + 60, FEET, 280)
    return dict(hit=hit, bg=1.0)

def gloves(d, x, y, s, col=(240, 240, 245), acc=(0, 150, 150)):
    for sx in (-1, 1):
        cx = x + sx * 70 * s
        d.rounded_rectangle((cx - 40 * s, y - 60 * s, cx + 40 * s, y + 50 * s), int(22 * s), fill=col)
        for f in range(4): d.rounded_rectangle((cx - 38 * s + f * 20 * s, y - 100 * s, cx - 22 * s + f * 20 * s, y - 50 * s), int(8 * s), fill=col)
        d.rectangle((cx - 40 * s, y + 30 * s, cx + 40 * s, y + 60 * s), fill=acc)

def s_abonne(img, d, tg, k):
    dim(img, 0.6); d = ImageDraw.Draw(img)
    hit = 0.0
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rounded_rectangle((W / 2 - bw / 2, 420 - bh / 2, W / 2 + bw / 2, 420 + bh / 2), int(40 * sc), fill=RED)
    text(d, (W / 2 - bw / 2 + 90 * sc, 420), "+", int(130 * sc), WHITE, BOLD)
    text(d, (W / 2 + 50 * sc, 420), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE, BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = tg - M("demain", 99) + 0.1
    if kd > 0:
        text(d, (W / 2, 660), f"DEMAIN · ÉPISODE {EPISODE + 1}", fit(f"DEMAIN · ÉPISODE {EPISODE + 1}", 74, 980), GOLD, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 770), typew("LE GARDIEN QUI ÉTAIT", kd, 34), fit("LE GARDIEN QUI ÉTAIT", 62, 980), WHITE, BOLD, stroke=5, scol=BG)
    kc = tg - M("chomage", 99) + 0.1
    if kc > 0:
        hit = max(hit, stamp(img, "AU CHÔMAGE", (W / 2, 920), 140, -6, kc, ACC))
        k22 = tg - M("vingtdeux", 99) + 0.1
        if k22 > 0: badge(d, W / 2, 1090, "22 ANS", k22, GOLD, 100)
    gloves(d, W / 2, 1330, 1.1)
    text(d, (W / 2, 1480), "?", 120, GOLD, BOLD, stroke=6, scol=BG)
    return dict(hit=hit, bg=0.0)

DUSTAMT = {"hook": 0.5, "paris": 0.6, "amateur": 0.6, "port": 0.8, "debut": 0.6, "mesure": 0.4, "course": 0.9, "montee": 0.6,
           "angleterre": 0.7, "monde": 0.8, "regard": 0.8, "you": 0.4, "abonne": 0.4, "question": 0.3, "logo": 0.2}
SCENES = {n: _wrap(n, f) for n, f in {"hook": s_hook, "paris": s_paris, "amateur": s_amateur, "port": s_port, "debut": s_debut,
          "mesure": s_mesure, "course": s_course, "montee": s_montee, "angleterre": s_angleterre, "monde": s_monde, "regard": s_regard,
          "you": s_you, "abonne": s_abonne, "question": s_question, "logo": s_logo}.items()}
BGLEVEL = {"hook": 0.0, "paris": 0.05, "amateur": 0.05, "port": 0.0, "debut": 0.0, "mesure": 0.0, "course": 0.15, "montee": 0.45,
           "angleterre": 0.7, "monde": 0.95, "regard": 1.0, "you": 0.2, "abonne": 0.0, "question": 0.0, "logo": 0.0}

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
def make_bg(lit):
    img = Image.new("RGBA", (W, H), INK + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, H, 4):
        u = y / H
        night = mix((10, 20, 40), (6, 12, 24), u); dawn = mix((120, 70, 60), (14, 22, 38), min(1, u * 1.4))
        d.rectangle((0, y, W, y + 4), fill=mix(night, dawn, lit))
    if lit > 0.05:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((W / 2 - 600, -500, W / 2 + 600, 500), fill=(255, 190, 110, int(150 * lit)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(90)))
    return img
BG_DARK = make_bg(0.0); BG_LIT = make_bg(1.0); _BGC.clear()

def Mx(n, dflt): return MK.get(n, dflt)
ST = [  # (x, y monde, t d'arrivée, gros texte, sous-texte, couleur, icône, sous-texte 2, t2)
    dict(p=(0, 0), t=0.0, big="1,68 m", sub="NÉ À PARIS", sub2="PARENTS VENUS DU MALI", t2=Mx("mali", 9.7), tc=Mx("taille", 10.4), col=ACC, ic="toise"),
    dict(p=(330, -520), t=Mx("dix", 15.6) - 1.0, big="8 ANS", sub="PETIT CLUB AMATEUR", sub2="10 ANS SANS ÊTRE REPÉRÉ", t2=Mx("remarquent", 17.2), col=ACC, ic="ball", stamp=("RECALÉ", Mx("recale", 19.2))),
    dict(p=(-300, -1040), t=Mx("dixneuf", 20.2), big="19 ANS", sub="TOUJOURS AMATEUR", sub2="ÉQUIPE RÉSERVE", t2=Mx("reserve", 25.1), col=ACC, ic="scooter", stamp=("EN TROTTINETTE", Mx("trotti", 27.3))),
    dict(p=(260, -1560), t=Mx("vingtun", 28.5), big="21 ANS", sub="1er MATCH PRO", sub2="", t2=99, col=GOLD, ic="star"),
    dict(p=(470, -1180), t=Mx("troisieme", 32.6), big="3e DIVISION", short="3e DIV.", sub="CLUB DÉJÀ RELÉGUÉ", sub2="", t2=99, col=RED, ic="down", down=True),
    dict(p=(240, -1900), t=K["boom"] + 1.3, big=None, col=GOLD, rocket=True),
    dict(p=(60, -2380), t=Mx("trente", 39.4), big="38 / 38", sub="MATCHS JOUÉS", sub2="LA MONTÉE !", t2=Mx("montee", 41.0), col=GREEN, ic="up"),
    dict(p=(420, -2880), t=K["gate1"], big="CHAMPION", short="CHAMPION", sub="D'ANGLETERRE", sub2="", t2=99, col=GOLD, ic="trophy"),
    dict(p=(-140, -3380), t=K["gate2"], big="ENCORE", short="CHAMPION ×2", sub="CHAMPION", sub2="ÉLU MEILLEUR JOUEUR", t2=Mx("elu", 47.1), col=GOLD, ic="trophy"),
    dict(p=(300, -3900), t=Mx("d2018", 49.6), big="2018", sub="CHAMPION DU MONDE", sub2="", t2=99, col=GOLD, ic="globe"),
    dict(p=(-60, -4420), t=Mx("d2021", 51.4), big="2021", sub="COUPE D'EUROPE", sub2="HOMME DU MATCH DE LA FINALE", t2=Mx("homme", 53.9), col=GOLD, ic="star"),
]
TZ = SC["regard"]; ZD = 1.4
def zoom_of(tg):
    if tg < TZ: return 1.0
    if tg >= SC["question"]: return ZFIT
    return lerp(1.0, ZFIT, ease((tg - TZ) / ZD))
ys = [s["p"][1] for s in ST]; ZFIT = 1250 / (max(ys) - min(ys) + 200)
MID = (sum(s["p"][0] for s in ST) / len(ST), (max(ys) + min(ys)) / 2)
HEADY = 1000

def head_at(tg):
    """position de la tête de ligne + index du segment en cours + avancement."""
    for i in range(1, len(ST)):
        a, b = ST[i - 1], ST[i]
        D = min(0.9, max(0.3, b["t"] - a["t"]))
        if tg < b["t"] - D: return a["p"], i, 0.0
        if tg < b["t"]:
            u = ease((tg - (b["t"] - D)) / D)
            return (lerp(a["p"][0], b["p"][0], u), lerp(a["p"][1], b["p"][1], u)), i, u
    return ST[-1]["p"], len(ST), 1.0

def cam_at(tg):
    h, _, _ = head_at(tg)
    z = zoom_of(tg)
    if tg >= TZ:
        u = ease((tg - TZ) / ZD); c = (lerp(h[0], MID[0], u), lerp(h[1], MID[1], u)); hy = lerp(HEADY, H * 0.47, u)
    else: c = h; hy = HEADY
    return c, z, hy

def draw_map(img, tg, glow=1.0):
    c, z, hy = cam_at(tg)
    def S(p): return (W / 2 + (p[0] - c[0]) * z, hy + (p[1] - c[1]) * z)
    d = ImageDraw.Draw(img)
    # quadrillage de plan (parallaxe)
    step = 120 * z
    ox = (W / 2 - c[0] * z) % step; oy = (hy - c[1] * z) % step
    x = ox
    while x < W: d.line((x, 0, x, H), fill=GRID, width=1); x += step
    y = oy
    while y < H: d.line((0, y, W, y), fill=GRID, width=1); y += step
    h, iseg, u = head_at(tg)
    pts = [s["p"] for s in ST[:iseg]] + ([h] if iseg < len(ST) else [])
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    lw = max(6, int(16 * z ** 0.6))
    for j in range(1, len(pts)):
        p, q = S(pts[j - 1]), S(pts[j])
        seg = ST[j]; col = RED if seg.get("down") else GOLD
        if j >= 5:   # après le tournant : DOUBLE ligne (« il court pour deux »)
            dx, dy = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dy) or 1; nx, ny = -dy / ln * lw * 0.9, dx / ln * lw * 0.9
            for sgn in (-1, 1):
                dl.line((p[0] + sgn * nx, p[1] + sgn * ny, q[0] + sgn * nx, q[1] + sgn * ny), fill=col + (255,), width=lw)
        else:
            dl.line((p, q), fill=col + (255,), width=lw)
        dl.ellipse((q[0] - lw / 2, q[1] - lw / 2, q[0] + lw / 2, q[1] + lw / 2), fill=col + (255,))
    gl = L.filter(ImageFilter.GaussianBlur(14 * glow + 1))
    img.alpha_composite(gl); img.alpha_composite(L)
    d = ImageDraw.Draw(img)
    # stations
    for i, s in enumerate(ST[:iseg]):
        if s.get("rocket"): continue
        q = S(s["p"]); r = max(10, 30 * z ** 0.7)
        d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=INK, outline=s["col"], width=max(4, int(9 * z ** 0.7)))
        if z < 0.7 and s.get("big"):
            txt = s.get("short", s["big"])
            text(d, (q[0] + (1 if i % 2 else -1) * 30, q[1]), txt, 34, s["col"], BOLD, "lm" if i % 2 else "rm", stroke=4, scol=INK)
    # tête lumineuse
    hq = S(h); pr = 26 + 6 * math.sin(tg * 6)
    Lh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dh = ImageDraw.Draw(Lh)
    dh.ellipse((hq[0] - pr * 2.2, hq[1] - pr * 2.2, hq[0] + pr * 2.2, hq[1] + pr * 2.2), fill=(255, 230, 160, 120))
    img.alpha_composite(Lh.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(img)
    d.ellipse((hq[0] - pr * 0.6, hq[1] - pr * 0.6, hq[0] + pr * 0.6, hq[1] + pr * 0.6), fill=WHITE)
    # cartes d'étape (zoom 1 seulement)
    if z > 0.8:
        cur = max([i for i, s in enumerate(ST) if s.get("big") and tg >= s["t"] - 0.05] or [-1])
        for i, s in enumerate(ST):
            if i != cur: continue
            k = tg - s["t"] + 0.05
            q = S(s["p"])
            if q[1] < -200 or q[1] > H + 200: continue
            side = 1 if (i % 2 == 0) else -1
            if s.get("down"): side = 1
            cx = q[0] + side * 290; cy = q[1]
            a = min(1, k / 0.15); sc = 1 + 0.25 * (1 - eout(k / 0.2))
            ww, hh = 470 * sc, 210 * sc
            d.rounded_rectangle((cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2), int(24 * sc), fill=mix(INK, (14, 26, 46), a), outline=mix(INK, s["col"], a), width=5)
            d.line((q[0] + side * 30, q[1], cx - side * ww / 2, cy), fill=mix(INK, s["col"], a), width=4)
            text(d, (cx, cy - 38 * sc), s["big"], fit(s["big"], int(84 * sc), ww - 40), mix(INK, s["col"], a), BOLD)
            text(d, (cx, cy + 40 * sc), s["sub"], fit(s["sub"], int(40 * sc), ww - 40), mix(INK, WHITE, a), BOLD)
            if s.get("sub2") and tg > s["t2"] - 0.1:
                k2 = tg - s["t2"] + 0.1
                text(d, (cx, cy + hh / 2 + 44), typew(s["sub2"], k2, 34), fit(s["sub2"], 44, 520), s["col"] if s["col"] != RED else WHITE, BOLD, stroke=5, scol=INK)
            icon(d, s.get("ic"), q[0] - side * 120, q[1] - 10, k, s["col"])
            if s.get("stamp") and tg > s["stamp"][1] - 0.06:
                stamp(img, s["stamp"][0], (cx, cy - hh / 2 - 70), 92, -5 * side, tg - s["stamp"][1] + 0.06, RED if s["stamp"][0] == "RECALÉ" else ACC); d = ImageDraw.Draw(img)
    return S, h, z

def icon(d, ic, x, y, k, col):
    if k <= 0 or not ic: return
    sc = 0.6 + 0.4 * eout(k / 0.25)
    if ic == "trophy": trophy(d, x, y + 40 * sc, 0.38 * sc, col)
    elif ic == "globe": globe(d, x, y, 60 * sc, k * 2, col)
    elif ic == "star": star(d, x, y, 50 * sc, col)
    elif ic == "scooter": scooter(d, x, y + 40, 150 * sc)
    elif ic == "ball": ball(d, x, y, 34 * sc, WHITE, k * 3)
    elif ic == "up": arrow(d, x, y + 90, True, GREEN, k)
    elif ic == "down": arrow(d, x, y - 100, False, RED, k)
    elif ic == "toise": toise(d, x, y + 110, 120, None, GREY)

def s_hook(img, d, tg, k):
    S, h, z = draw_map(img, tg); d = ImageDraw.Draw(img)
    q = S(h); toise(d, q[0] - 120, q[1] + 20, 110 * 0.9, max(0, tg - 0.6), WHITE)
    series_banner(d, tg)
    kk = tg - K["hook"]; hit = 0.0
    text(d, (W / 2, 280), typew("ON T'A DÉJÀ DIT…", tg + 0.3, 26), 84, ACC, BOLD, stroke=6, scol=BG)
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 470), "TROP", int(fit("TROP", 170, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        text(d, (W / 2, 650), "PETIT ?", int(fit("PETIT ?", 190, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        hit = max(0, 1 - kk / 0.25)
    return dict(hit=hit, bg=0.0)

def s_paris(img, d, tg, k):
    draw_map(img, tg); d = ImageDraw.Draw(img); hit = 0.0
    kn = tg - M("ne", 99) + 0.1
    if kn <= 0:
        series_banner(d, tg)
        text(d, (W / 2, 300), "L'HISTOIRE VRAIE", fit("L'HISTOIRE VRAIE", 96, 980), WHITE, BOLD, stroke=5, scol=BG)
        text(d, (W / 2, 400), "D'UN FOOTBALLEUR", fit("D'UN FOOTBALLEUR", 60, 980), ACC, BOLD, stroke=5, scol=BG)
        ka = tg - M("lamateur", 99) + 0.1
        if ka > 0:
            text(d, (W / 2, 560), "DE L'AMATEUR", int(fit("DE L'AMATEUR", 120, 980) * (1 + 0.25 * (1 - eout(ka / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
            hit = stamp(img, "AU PRO", (W / 2, 720), 140, -5, ka - 0.15, GOLD)
    else:
        text(d, (W / 2, 300), "LA LIGNE DE SA CARRIÈRE", fit("LA LIGNE DE SA CARRIÈRE", 72, 980), WHITE, BOLD, stroke=5, scol=BG)
        kt = tg - M("taille", 99) + 0.1
        if 0 < kt < 0.25: hit = 1 - kt / 0.25
    return dict(hit=hit, bg=0.0)

def _plain(title=None, sub=None):
    def f(img, d, tg, k):
        draw_map(img, tg); d = ImageDraw.Draw(img); hit = 0.0
        for s in ST:
            kk = tg - s["t"]
            if s.get("big") and 0 <= kk < 0.25: hit = max(hit, 1 - kk / 0.25)
        if title: label(d, 290, title, k, 84, WHITE, sub, ACC)
        return dict(hit=hit, bg=0.0)
    return f
s_amateur = _plain(); s_port = _plain(); s_debut = _plain()

def s_mesure(img, d, tg, k):
    S, h, z = draw_map(img, tg, 0.4); d = ImageDraw.Draw(img)
    dim(img, 0.35); d = ImageDraw.Draw(img); hit = 0.0
    q = S(h)
    km = tg - M("mesure", SC["mesure"]) + 0.1
    for i, sx in enumerate((-1, 1)):
        if km > i * 0.15: toise(d, q[0] + sx * 300, q[1] + 300, 420, None, GREY)
    if km > 0:
        text(d, (W / 2, 300), "TOUT LE MONDE", fit("TOUT LE MONDE", 100, 980), WHITE, BOLD, stroke=6, scol=BG)
        hit = stamp(img, "LE MESURE", (W / 2, 450), 120, -4, km, RED)
    kp = tg - M("personne", 99) + 0.1
    if kp > 0: text(d, (W / 2, 620), typew("PERSONNE NE LE REGARDE", kp, 30), fit("PERSONNE NE LE REGARDE", 74, 980), GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit, bg=0.0)

STREAK = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 40).uniform(0, H), np.random.default_rng(i + 80).uniform(0.4, 1)) for i in range(40)]
def s_course(img, d, tg, k):
    kb = tg - K["boom"]; kc = tg - M("courir", K["boom"] + 0.8) + 0.08
    hit = 0.0; flash = 0.0
    if kb > -0.05:
        for x0, y0, z in STREAK:   # lignes de vitesse verticales
            y = (y0 + kb * 2600 * z) % H
            d.line((x0, y, x0, y - 160 * z), fill=mix(BG, ACC, 0.5 * z), width=3)
    S, h, zz = draw_map(img, tg, 1.6); d = ImageDraw.Draw(img)
    if kb < -0.05: return dict(hit=0.0, bg=0.0)
    kk = kb + 0.05
    if kk < 0.35: flash = max(0, 0.9 - kk * 2.6)
    q = S(h); burst(d, q[0], q[1], kk, 20, 360, GOLD, 3, 8)
    if kc <= 0:
        sc = 1 + 1.0 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 380), "TROP", int(fit("TROP", 180, 1000) * sc), WHITE, BOLD, stroke=9, scol=RED)
        text(d, (W / 2, 580), "PETIT ?", int(fit("PETIT ?", 200, 1000) * sc), WHITE, BOLD, stroke=9, scol=RED)
        hit = max(0, 1 - kk / 0.3)
    else:
        e = eout(kc / 0.2)
        text(d, (W / 2, 300), "ALORS IL VA", fit("ALORS IL VA", 110, 1000), WHITE, BOLD, stroke=7, scol=BG)
        for off, c in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, GOLD)):
            o = off * (1 - e)
            text(d, (W / 2 + o, 470), "COURIR", int(fit("COURIR", 200, 1000) * (1 + 0.5 * (1 - e))), c, BOLD, stroke=10 if c == GOLD else 0, scol=BG)
        kd = tg - M("deux", 99) + 0.05
        if kd > 0: hit = max(hit, stamp(img, "POUR DEUX !", (W / 2, 680), 150, -5, kd, ACC))
        if kc < 0.25: hit = max(hit, 1 - kc / 0.25)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=0.1)

s_montee = _plain(); s_angleterre = _plain(); s_monde = _plain()
def s_monde(img, d, tg, k):
    R = _plain()(img, d, tg, k)
    kw = tg - K["sunrise"] + 0.1
    if kw > 0: confetti(ImageDraw.Draw(img), kw)
    kh = tg - M("homme", 99) + 0.1
    if kh > 0: confetti(ImageDraw.Draw(img), kh + 1.5)
    R["bg"] = min(1, 0.3 + 0.2 * max(0, tg - SC["monde"])); return R

def s_regard(img, d, tg, k):
    S, h, z = draw_map(img, tg, 1.3); d = ImageDraw.Draw(img); hit = 0.0
    kr = tg - M("regarde", 99) + 0.15
    text(d, (W / 2, 220), "LE PETIT QUE PERSONNE", fit("LE PETIT QUE PERSONNE", 76, 980), GREY if kr > 0 else WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 310), "NE REGARDAIT…", fit("NE REGARDAIT…", 76, 980), GREY if kr > 0 else WHITE, BOLD, stroke=6, scol=BG)
    p0 = S(ST[0]["p"]); text(d, (p0[0], p0[1] + 70), "1,68 m", 44, ACC, BOLD, stroke=4, scol=INK)
    if kr > 0:
        q = S(h)
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); u = eout(kr / 0.5)
        for sx in (-150, 200, W - 200, W + 150):
            dl.polygon([(sx, H), (sx + 90, H), (q[0] + 40 * u, q[1]), (q[0] - 40 * u, q[1])], fill=(255, 236, 180, int(55 * u)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(img)
        text(d, (W / 2, 1420), "LE MONDE ENTIER", int(fit("LE MONDE ENTIER", 110, 980) * (1 + 0.3 * (1 - eout(kr / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
        hit = stamp(img, "LE REGARDE", (W / 2, 1270), 120, -4, kr, ACC)
    return dict(hit=hit, bg=1.0)

def _over(f, a):
    def g(img, d, tg, k):
        draw_map(img, tg, 0.6); dim(img, a); return f(img, ImageDraw.Draw(img), tg, k)
    return g
_you, _ab, _q, _lg = s_you, s_abonne, s_question, s_logo
s_you = _over(_you, 0.1); s_abonne = _over(_ab, 0.0); s_question = _over(_q, 0.0)

def dust(d, tg, amt=1.0): pass
DUSTAMT = {}
SCENES = {n: f for n, f in {"hook": s_hook, "paris": s_paris, "amateur": s_amateur, "port": s_port, "debut": s_debut,
          "mesure": s_mesure, "course": s_course, "montee": s_montee, "angleterre": s_angleterre, "monde": s_monde, "regard": s_regard,
          "you": s_you, "abonne": s_abonne, "question": s_question, "logo": _lg}.items()}
BGLEVEL = {"hook": 0.0, "paris": 0.0, "amateur": 0.0, "port": 0.0, "debut": 0.0, "mesure": 0.0, "course": 0.1, "montee": 0.2,
           "angleterre": 0.3, "monde": 0.5, "regard": 1.0, "you": 0.3, "abonne": 0.0, "question": 0.0, "logo": 0.0}

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None, int(a[5]) if len(a) > 5 else 1)

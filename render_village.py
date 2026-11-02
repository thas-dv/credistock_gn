# -*- coding: utf-8 -*-
"""Style « village » : village de brousse au crépuscule (terre rouge, baobab, cases au toit de paille, buts de fortune) -> aube dorée ;
passage froid et bleu (neige) pour l'arrivée en Europe ; joueur en silhouette générique (maillot blanc, sans numéro).
Types : hook village essai regard choix metz stamps slam record sommet afrique ecole you question logo.
Scènes propres à l histoire du 02/11 (Sadio Mané) sauf stamps/slam/you/question/logo.
Usage : python3 render_village.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# palette « village » : village de brousse au crépuscule (terre rouge, baobab, cases au toit de paille) -> aube dorée
NIGHT = (14, 12, 34); SKY2 = (52, 34, 70); DUSK = (236, 120, 70); DUSK2 = (255, 196, 110)
ACC = (255, 158, 46); AMBER = (255, 184, 80); SNOW = (240, 214, 170); ICE = ACC
EARTH = (96, 40, 22); EARTH2 = (196, 92, 44); STRAW = (190, 150, 80)
ORANGE = ACC; PITCH = EARTH
HOR = 1060
JER = (236, 236, 242)
SEN = [(0, 133, 63), (253, 239, 66), (227, 27, 35)]

def baobab(d, x, y, s, col):
    d.polygon([(x - 60 * s, y), (x - 44 * s, y - 300 * s), (x - 70 * s, y - 380 * s), (x + 70 * s, y - 380 * s), (x + 44 * s, y - 300 * s), (x + 60 * s, y)], fill=col)
    for ang, ln in [(-60, 230), (-30, 260), (0, 200), (25, 250), (55, 240), (-80, 160), (80, 170)]:
        a = math.radians(ang); bx, by = x + math.sin(a) * 30 * s, y - 370 * s
        ex, ey = bx + math.sin(a) * ln * s, by - math.cos(a) * ln * 0.6 * s - 40 * s
        d.line((bx, by, ex, ey), fill=col, width=int(26 * s))
        for j in (-1, 1):
            d.line((ex, ey, ex + j * 50 * s, ey - 60 * s), fill=col, width=int(12 * s))
        d.ellipse((ex - 60 * s, ey - 40 * s, ex + 60 * s, ey + 10 * s), fill=col)

def hut(d, x, y, s, wall, roof):
    d.rectangle((x - 80 * s, y - 120 * s, x + 80 * s, y), fill=wall)
    d.polygon([(x - 115 * s, y - 110 * s), (x, y - 250 * s), (x + 115 * s, y - 110 * s)], fill=roof)
    d.rectangle((x - 20 * s, y - 70 * s, x + 20 * s, y), fill=(20, 12, 10))

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        night = mix(NIGHT, SKY2, u); day = mix((120, 120, 190), mix(DUSK, DUSK2, u), u ** 0.8)
        d.line((0, y, W, y), fill=mix(night, day, lit))
    rng = np.random.default_rng(3)
    for _ in range(110):
        x, y = rng.uniform(0, W), rng.uniform(0, HOR * 0.55); r = rng.uniform(1, 2.6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix(mix(NIGHT, SKY2, y / HOR), WHITE, (0.3 + 0.6 * rng.random()) * (1 - lit)))
    if lit < 0.5:   # lune
        d.ellipse((780, 180, 880, 280), fill=mix((236, 230, 210), mix(NIGHT, SKY2, 0.2), lit * 2))
    if lit > 0.25:   # soleil bas
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((W / 2 - 300, HOR - 360, W / 2 + 300, HOR + 200), fill=(255, 190, 110, int(190 * (lit - 0.25) / 0.75)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(70)))
        d = ImageDraw.Draw(img)
        d.ellipse((W / 2 - 120, HOR - 200, W / 2 + 120, HOR + 40), fill=mix((255, 150, 80), (255, 226, 160), lit))
    sil = mix((22, 12, 20), (90, 40, 34), lit * 0.7)
    d.polygon([(0, HOR - 40), (300, HOR - 80), (620, HOR - 30), (900, HOR - 70), (W, HOR - 40), (W, HOR + 5), (0, HOR + 5)], fill=sil)
    # sol de terre rouge
    for y in range(HOR, H):
        u = (y - HOR) / (H - HOR)
        d.line((0, y, W, y), fill=mix(mix((40, 18, 16), (78, 34, 22), u), mix(EARTH2, (150, 64, 32), u), lit * 0.85 + 0.1))
    rng = np.random.default_rng(13)
    for _ in range(60):
        x, y = rng.uniform(0, W), rng.uniform(HOR + 20, H); w = rng.uniform(30, 160)
        d.ellipse((x - w, y - 6, x + w, y + 6), fill=mix((60, 26, 18), (220, 120, 64), lit * 0.8 + 0.1))
    # baobab + cases au loin
    baobab(d, 170, HOR + 30, 1.05, sil)
    for x, s in ((640, 0.7), (790, 0.85), (960, 0.75)):
        hut(d, x, HOR + 20, s, mix((44, 22, 20), (170, 90, 54), lit * 0.8), mix((34, 22, 18), STRAW, lit * 0.8))
    # buts de fortune (deux bâtons) au fond
    for x in (430, 560):
        d.line((x, HOR + 60, x, HOR - 40), fill=mix((60, 40, 30), (230, 210, 180), lit), width=7)
    d.line((430, HOR - 40, 560, HOR - 40), fill=mix((60, 40, 30), (230, 210, 180), lit), width=6)
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

MOTES = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.3, 1.0)) for i in range(90)]
def dust(d, tg, amt=1.0):
    n = int(len(MOTES) * amt)
    for x0, y0, z in MOTES[:n]:
        y = (y0 - tg * 30 * z) % H; x = (x0 + tg * 50 * z + 30 * math.sin(tg * 0.7 * z + x0)) % W; r = 1.5 + 3 * z
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((120, 70, 40), (255, 210, 150), z))
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

def shoe(d, cx, cy, s, torn=0.0):
    """chaussure de foot usée, vue de profil ; torn = 0..1 (déchirures)."""
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.polygon([q(-200, 40), q(-190, -60), q(-90, -110), q(10, -90), q(90, -40), q(200, -10), q(220, 40)], fill=(40, 30, 28), outline=(220, 200, 170), width=max(3, int(6 * s)))
    d.rectangle((q(-210, 40)[0], q(0, 40)[1], q(230, 40)[0], q(0, 62)[1]), fill=(26, 20, 18))
    for i in range(6): d.ellipse((q(-170 + i * 70, 62)[0] - 9 * s, q(0, 62)[1], q(-170 + i * 70, 62)[0] + 9 * s, q(0, 82)[1]), fill=(26, 20, 18))
    for i in range(4): d.line((q(-70 + i * 30, -95), q(-50 + i * 30, -60)), fill=(220, 200, 170), width=max(2, int(4 * s)))
    if torn > 0:
        a = int(255 * min(1, torn))
        d.polygon([q(60, -30), q(110, -10), q(90, 20), q(120, 34), q(50, 30)], fill=mix((40, 30, 28), (230, 160, 120), torn))
        d.line((q(-150, -40), q(-120, -10), q(-140, 10)), fill=RED, width=max(3, int(6 * s)))
        d.line((q(130, 0), q(160, 20)), fill=RED, width=max(3, int(6 * s)))

def flag(img, x0, y0, w, h, a, star_=True):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for i, c in enumerate(SEN): dl.rectangle((x0 + i * w / 3, y0, x0 + (i + 1) * w / 3, y0 + h), fill=c + (int(235 * a),))
    if star_: star(dl, x0 + w / 2, y0 + h / 2, h * 0.17, SEN[0] + (int(255 * a),))
    img.alpha_composite(L)

def kid(img, d, x, y, s, tg, k):
    P(img, x, y, s, run_pose(tg * 9)); shadow(d, x, y, s)
    ball(d, x + 0.55 * s + 30 * math.sin(tg * 4), y - 0.12 * s - 60 * abs(math.sin(tg * 5)), 0.11 * s, WHITE, tg * 6)

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    # silhouette géante qui regarde de haut un petit joueur
    d.ellipse((W / 2 - 300, 560, W / 2 + 300, 1060), fill=(10, 6, 12))
    d.ellipse((W / 2 - 120, 380, W / 2 + 120, 640), fill=(10, 6, 12))
    for ex in (-50, 50): d.ellipse((W / 2 + ex - 16, 520, W / 2 + ex + 16, 540), fill=mix(BG, ACC, 0.8))
    P(img, W / 2, FEET, 190, "stand"); shadow(d, W / 2, FEET, 190)
    ball(d, W / 2 + 80, FEET - 22, 22, WHITE, 0)
    kk = tg - K["hook"]
    text(d, (W / 2, 250), typew("ON T'A DÉJÀ…", tg + 0.3, 24), 92, ACC, BOLD, stroke=6, scol=BG)
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 1150), "REGARDÉ", int(fit("REGARDÉ", 150, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        text(d, (W / 2, 1310), "DE HAUT ?", int(fit("DE HAUT ?", 170, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        hit = max(0, 1 - kk / 0.25)
    return dict(hit=hit)

def s_village(img, d, tg, k):
    hit = 0.0
    te = M("enfant", SC["village"] + 5)
    if tg < te - 0.15:
        label(d, 300, "UN PETIT VILLAGE", k, 96, WHITE, "AU SUD DU SÉNÉGAL", ACC)
        ks = tg - M("senegal1", 99) + 0.15
        if ks > 0: flag(img, 340, 500, 400, 260, eout(ks / 0.4)); d = ImageDraw.Draw(img)
        P(img, W / 2 + 120, FEET, 210, "stand"); shadow(d, W / 2 + 120, FEET, 210)
    else:
        kk = tg - te
        x = lerp(-100, W + 100, (kk / 4.5) % 1.0)
        kid(img, d, x, FEET, 200, tg, kk)
        label(d, 300, "ENFANT", kk + 0.2, 110, WHITE, "LE BALLON DANS LA RUE", ACC)
        kf = tg - M("famille", 99) + 0.1
        if kf > 0:
            text(d, (W / 2, 620), "SA FAMILLE VEUT", fit("SA FAMILLE VEUT", 84, 980), WHITE, BOLD, stroke=6, scol=BG)
            hit = stamp(img, "UN AUTRE AVENIR", (W / 2, 790), 110, -4, tg - M("avenir", 99) + 0.05, ACC)
    return dict(hit=hit, bg=0.15)

def s_essai(img, d, tg, k):
    dim(img, 0.35)
    hit = 0.0
    k15 = tg - M("quinze", SC["essai"] + 0.1) + 0.1
    if k15 > 0:
        badge(d, 230, 320, "15 ANS", k15, GOLD, 115)
        if k15 < 0.25: hit = 1 - k15 / 0.25
    kes = tg - M("essai", 99) + 0.1
    if kes > 0: text(d, (700, 320), "UN ESSAI", int(fit("UN ESSAI", 110, 560) * (1 + 0.3 * (1 - eout(kes / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
    kc = tg - M("chaussures", 99) + 0.2
    if kc > 0:
        sc = 1.2 + 0.1 * eout(kc / 0.5)
        shoe(d, W / 2, 860, sc, ease((tg - M("dechirees", 99) + 0.1) / 0.3))
        hit = max(hit, stamp(img, "DÉCHIRÉES", (W / 2, 640), 130, -6, tg - M("dechirees", 99) + 0.05, RED))
        kshort = tg - M("short", 99) + 0.2
        if kshort > 0: text(d, (W / 2, 1120), typew("PAS DE VRAI SHORT", kshort, 30), fit("PAS DE VRAI SHORT", 84, 980), WHITE, BOLD, stroke=6, scol=BG)
        P(img, W / 2, 1720, 190, "stand", alpha=0.9)
    else:
        P(img, W / 2, FEET, 260, run_pose(tg * 8)); shadow(d, W / 2, FEET, 260)
    return dict(hit=hit, bg=0.1)

def s_regard(img, d, tg, k):
    dim(img, 0.3)
    hit = 0.0
    scout(d, 820, 1700, 1.9, 1.0)
    P(img, 330, FEET, 220, "stand"); shadow(d, 330, FEET, 220)
    kr = tg - M("regarde", SC["regard"] + 0.4) + 0.2
    if kr > 0:
        text(d, (W / 2, 330), "UN HOMME LE REGARDE", fit("UN HOMME LE REGARDE", 84, 980), WHITE, BOLD, stroke=6, scol=BG)
        for i in range(3):
            yy = 560 + i * 26
            d.line((760, 470, 380 - i * 20, 1300 + i * 30), fill=mix(BG, ACC, 0.25), width=3) if i == 0 else None
    kt = tg - M("trompe", 99) + 0.1
    if kt > 0:
        hit = stamp(img, "PAS SA PLACE ?", (W / 2, 560), 130, -5, kt, RED)
        text(d, (330, 1180), "?", int(220 * (1 + 0.1 * math.sin(tg * 8))), ACC, BOLD, stroke=6, scol=BG)
    return dict(hit=hit, bg=0.1)

def s_choix(img, d, tg, k):
    hit = 0.0
    kc = tg - M("choisit", SC["choix"] + 1.5) + 0.1
    if kc <= 0:
        label(d, 320, "LE MATCH COMMENCE", k, 92, WHITE)
        x = lerp(150, W - 250, min(1, k / 1.6))
        P(img, x, FEET, 260, run_pose(tg * 11)); shadow(d, x, FEET, 260)
        ball(d, x + 150, FEET - 30, 32, WHITE, tg * 9)
        for i in range(5): d.line((x - 140 - i * 40, FEET - 150 + i * 30, x - 260 - i * 60, FEET - 150 + i * 30), fill=mix(BG, SNOW, 0.5), width=4)
    else:
        scout(d, 820, 1700, 1.6, 0.0)
        P(img, 380, FEET, 270, blend_pose(POSES["stand"], POSES["up"], eout(kc / 0.4))); shadow(d, 380, FEET, 270)
        hit = stamp(img, "CHOISI !", (W / 2, 520), 190, -6, kc, GOLD)
        burst(d, W / 2, 520, kc, 18, 380, GOLD, 5)
        if kc > 0.35: text(d, (W / 2, 720), "TOUT DE SUITE", 84, WHITE, BOLD, stroke=6, scol=BG)
    return dict(hit=hit, bg=0.35)

FLAKES = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.4, 1.0)) for i in range(120)]
def s_metz(img, d, tg, k):
    # loin de chez lui : nuit froide, bleu, neige
    img.alpha_composite(Image.new("RGBA", (W, H), (10, 22, 50, 170))); d = ImageDraw.Draw(img)
    hit = 0.0
    for x0, y0, z in FLAKES:
        y = (y0 + tg * 140 * z) % H; x = (x0 + 40 * math.sin(tg * 0.9 * z + x0)) % W; r = 2 + 4 * z
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((90, 110, 140), (230, 240, 250), z))
    k19 = tg - M("dixneuf", SC["metz"] + 0.1) + 0.1
    if k19 > 0:
        badge(d, 230, 300, "19 ANS", k19, GOLD, 110)
        if k19 < 0.25: hit = 1 - k19 / 0.25
    kf = tg - M("france", 99) + 0.1
    if kf > 0: text(d, (690, 300), "L'EUROPE", int(fit("L'EUROPE", 110, 560) * (1 + 0.3 * (1 - eout(kf / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
    rows = [("froid", "LE FROID", (150, 200, 255)), ("loin", "LOIN DES SIENS", WHITE), ("blessure", "UNE BLESSURE", RED)]
    for i, (m, s, c) in enumerate(rows):
        kk = tg - M(m, 99) + 0.1
        if kk > 0:
            text(d, (W / 2 + 40 * (1 - eout(kk / 0.25)), 520 + i * 120), s, 92, c, BOLD, stroke=6, scol=BG)
            if kk < 0.25: hit = max(hit, 1 - kk / 0.25)
    kd = tg - M("descend", 99) + 0.15
    if kd > 0:
        ay = 900 + 60 * eout(kd / 0.6)
        d.polygon([(W / 2 - 60, ay), (W / 2 + 60, ay), (W / 2 + 60, ay + 120), (W / 2 + 130, ay + 120), (W / 2, ay + 250), (W / 2 - 130, ay + 120), (W / 2 - 60, ay + 120)], fill=RED)
        text(d, (W / 2, 1270), "SON CLUB DESCEND", fit("SON CLUB DESCEND", 76, 980), WHITE, BOLD, stroke=6, scol=BG)
        k3 = tg - M("troisieme", 99) + 0.05
        if k3 > 0: hit = max(hit, stamp(img, "3e DIVISION", (W / 2, 1400), 110, -4, k3, RED))
    pose = "hurt" if tg > M("blessure", 99) - 0.1 else "stand"
    if kd > 0: pose = "sad"
    x = 230 if kd > 0 else W - 230
    P(img, x, 1780, 170, pose, alpha=0.95)
    return dict(hit=hit, bg=0.0)

def s_stamps(img, d, tg, k):
    dim(img, 0.5)
    P(img, W / 2, 1720, 230, "sad", alpha=0.8)
    hit = 0.0; cols = [RED, WHITE, AMBER]
    for i, (txt, t0) in enumerate(TJ["words3d"]):
        hit = max(hit, stamp(img, txt, (W / 2 + [-30, 40, 0][i], [420, 680, 940][i]), 160, [-8, 6, -4][i], tg - t0 + 0.06, cols[i]))
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
    shadow(d, W / 2, 1600, 320)
    P(img, W / 2, 1600, 320, pose, glow=1.0)
    if kb > -0.08:
        kk = kb + 0.08; sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 330), "IL A", 110, ACC, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 520), "CONTINUÉ !", int(fit("CONTINUÉ !", 200, 1000) * sc), WHITE, BOLD, stroke=10, scol=ACC)
    else:
        text(d, (W / 2, 420), typew("RENTRER AU VILLAGE ?", max(0, tg - K["build_start"] + 0.2), 24), fit("RENTRER AU VILLAGE ?", 90, 1000), GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_record(img, d, tg, k):
    hit = 0.0; flash = 0.0
    t3 = M("trois", SC["record"] + 1.5)
    if tg < t3 - 0.15:
        kc = tg - K["gate1"] + 0.1
        if kc > 0:
            trophy(d, W / 2, 1000, 0.8 * (1 + 0.25 * (1 - eout(kc / 0.2))), GOLD)
            hit = stamp(img, "CHAMPION", (W / 2, 450), 170, -5, kc, GOLD)
        else:
            label(d, 400, "EN EUROPE", k, 100, WHITE)
        P(img, W / 2, 1760, 210, "up" if kc > 0 else run_pose(tg * 10))
    else:
        k3 = tg - t3 + 0.1
        n = min(3, 1 + int(k3 / 0.25))
        for i in range(n):
            ball(d, W / 2 - 220 + i * 220, 430, 70, WHITE, tg * 5 + i)
        if k3 < 0.6 and abs((k3 % 0.25) - 0.02) < 0.05: hit = 0.8
        kt = tg - M("deuxmin", 99) + 0.1
        if kt > 0:
            sc = 1 + 0.3 * (1 - eout(kt / 0.2))
            text(d, (W / 2, 690), "3 BUTS EN", 90, WHITE, BOLD, stroke=6, scol=BG)
            k56 = tg - M("cinqsix", 99) + 0.1
            s = "2 MIN 56" if k56 > 0 else "2 MIN"
            text(d, (W / 2, 850), s, int(170 * sc), ACC, BOLD, stroke=8, scol=BG)
        ktr = tg - M("triple", 99) + 0.05
        if ktr > 0:
            hit = max(hit, stamp(img, "RECORD", (W / 2, 1080), 180, -6, ktr, GOLD))
            burst(d, W / 2, 1080, ktr, 20, 420, GOLD, 4)
            if ktr > 0.4: text(d, (W / 2, 1240), "LE TRIPLÉ LE PLUS RAPIDE", fit("LE TRIPLÉ LE PLUS RAPIDE", 60, 980), WHITE, BOLD, stroke=5, scol=BG)
            if ktr < 0.2: flash = 0.25 * (1 - ktr / 0.2)
        P(img, W / 2, 1780, 190, "up" if ktr > 0 else run_pose(tg * 11))
    return dict(hit=hit, flash=flash, bg=0.6)

def s_sommet(img, d, tg, k):
    hit = 0.0; flash = 0.0
    kc = tg - K["sunrise"] + 0.15
    if kc > 0:
        trophy(d, W / 2, 1060, 1.1 * (1 + 0.25 * (1 - eout(kc / 0.2))), GOLD)
        text(d, (W / 2, 320), "LA PLUS GRANDE", 80, WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 430), "COUPE D'EUROPE", fit("COUPE D'EUROPE", 104, 980), GOLD, BOLD, stroke=6, scol=BG)
        confetti(d, kc)
        if kc < 0.3: hit = 1 - kc / 0.3; flash = 0.3 * (1 - kc / 0.3)
    else:
        label(d, 400, "TOUT EN HAUT", k, 104, WHITE, "LE PLUS HAUT NIVEAU", ACC)
    kch = tg - M("championnat2", 99) + 0.1
    if kch > 0:
        badge(d, W / 2, 1380, "CHAMPION", kch, ACC, 150)
        text(d, (W / 2, 1570), "D'ANGLETERRE", 64, WHITE, BOLD, stroke=5, scol=BG)
        if kch < 0.25: hit = max(hit, 1 - kch / 0.25)
    else:
        P(img, W / 2, 1760, 210, "up" if kc > 0 else run_pose(tg * 10))
    return dict(hit=hit, flash=flash, bg=0.85)

def s_afrique(img, d, tg, k):
    hit = 0.0; flash = 0.0
    hit = max(hit, stamp(img, "2022", (W / 2, 280), 160, -5, tg - M("d2022", SC["afrique"] + 0.1) + 0.05, GOLD))
    kp = tg - M("penalty", 99) + 0.1
    ks = tg - M("senegal2", 99) + 0.1
    if ks <= 0:
        goal(d, W / 2, 1180, 1.2, 0.6)
        if kp > 0:
            u = min(1, kp / 0.45)
            ball(d, lerp(W / 2, W / 2 + 260, u), lerp(1560, 1000, u), lerp(46, 26, u), WHITE, tg * 9)
            hit = max(hit, stamp(img, "LE DERNIER TIR", (W / 2, 520), 110, -4, kp, WHITE))
            if kp > 0.45: burst(d, W / 2 + 260, 1000, kp - 0.45, 18, 260, GOLD, 2)
        else:
            text(d, (W / 2, 520), "C'EST LUI QUI TIRE", fit("C'EST LUI QUI TIRE", 84, 980), WHITE, BOLD, stroke=6, scol=BG)
        P(img, W / 2 - 140, FEET + 60, 250, "kick" if kp > 0 else "stand")
    else:
        flag(img, 140, 520, 800, 520, eout(ks / 0.4)); d = ImageDraw.Draw(img)
        if ks < 0.3: hit = max(hit, 1 - ks / 0.3); flash = 0.3 * (1 - ks / 0.3)
        ka = tg - M("afrique", 99) + 0.1
        if ka > 0:
            text(d, (W / 2, 1130), "CHAMPION", int(fit("CHAMPION", 130, 980) * (1 + 0.3 * (1 - eout(ka / 0.2)))), GOLD, BOLD, stroke=7, scol=BG)
            text(d, (W / 2, 1260), "D'AFRIQUE", int(fit("D'AFRIQUE", 130, 980) * (1 + 0.3 * (1 - eout(ka / 0.2)))), GOLD, BOLD, stroke=7, scol=BG)
            text(d, (W / 2, 1390), "1er TITRE DU SÉNÉGAL", 56, WHITE, BOLD, stroke=5, scol=BG)
            if ka < 0.3: hit = max(hit, 1 - ka / 0.3)
        confetti(d, ks)
        P(img, W / 2, 1800, 200, "up")
    return dict(hit=hit, flash=flash, bg=0.95)

def s_ecole(img, d, tg, k):
    hit = 0.0
    text(d, (W / 2, 300), "AUJOURD'HUI", 100, WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 410), "DANS SON VILLAGE", 70, ACC, BOLD, stroke=5, scol=BG)
    ke = tg - M("ecole", 99) + 0.1
    if ke > 0:
        u = eout(ke / 0.5); x, y = 300, 1250
        d.rectangle((x - 210, y - 260 * u, x + 210, y), fill=(236, 214, 170)); d.polygon([(x - 240, y - 260 * u), (x, y - 360 * u), (x + 240, y - 260 * u)], fill=(170, 70, 40))
        for wx in (x - 140, x - 40, x + 60, x + 160):
            if u > 0.6: d.rectangle((wx - 30, y - 180, wx + 10, y - 120), fill=(80, 120, 170))
        text(d, (x, y + 70), "UNE ÉCOLE", 64, WHITE, BOLD, stroke=5, scol=BG)
        if ke < 0.25: hit = 1 - ke / 0.25
    kh = tg - M("hopital", 99) + 0.1
    if kh > 0:
        u = eout(kh / 0.5); x, y = 790, 1250
        d.rectangle((x - 200, y - 300 * u, x + 200, y), fill=(246, 246, 240))
        if u > 0.6:
            text(d, (x, y - 190), "H", 120, (30, 90, 170), BOLD)
        text(d, (x, y + 70), "UN HÔPITAL", 64, WHITE, BOLD, stroke=5, scol=BG)
        if kh < 0.25: hit = max(hit, 1 - kh / 0.25)
    kid(img, d, lerp(-100, W + 100, (k / 5) % 1), 1700, 150, tg, k)
    return dict(hit=hit, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ACC, BOLD, stroke=6, scol=BG)
    rows = [("CHAUSSURES", "déchirées"), ("LOIN DES SIENS", "blessé"), ("2 MIN 56", "le record"), ("CHAMPION", "d'Afrique")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 90 - 80 * (1 - eout(kk / 0.2))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD if i == 3 else ACC)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 45, y), a, 42, GOLD if i == 3 else WHITE, MONO, "lm"); text(d, (x + 520, y), b, 40, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "DE HAUT ?", (W / 2, 1180), 150, -5, kn + 0.05, RED) if kn > -0.05 else 0.0
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

DUSTAMT = {"hook": 0.6, "village": 1.0, "essai": 0.6, "regard": 0.6, "choix": 1.0, "metz": 0.0, "stamps": 0.5, "slam": 0.8, "record": 0.6,
           "sommet": 0.7, "afrique": 0.8, "ecole": 1.0, "you": 0.4, "question": 0.3, "logo": 0.2}
def _wrap(name, f):
    def g(img, d, tg, k):
        dust(d, tg, DUSTAMT.get(name, 0.5)); return f(img, d, tg, k)
    return g
SCENES = {n: _wrap(n, f) for n, f in {"hook": s_hook, "village": s_village, "essai": s_essai, "regard": s_regard, "choix": s_choix, "metz": s_metz,
          "stamps": s_stamps, "slam": s_slam, "record": s_record, "sommet": s_sommet, "afrique": s_afrique, "ecole": s_ecole,
          "you": s_you, "question": s_question, "logo": s_logo}.items()}
BGLEVEL = {"hook": 0.0, "village": 0.15, "essai": 0.1, "regard": 0.1, "choix": 0.35, "metz": 0.0, "stamps": 0.0, "slam": 0.1, "record": 0.6,
           "sommet": 0.85, "afrique": 0.95, "ecole": 1.0, "you": 0.2, "question": 0.0, "logo": 0.0}

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

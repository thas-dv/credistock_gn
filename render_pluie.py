# -*- coding: utf-8 -*-
"""Style « pluie » : terrain de foot la nuit sous la pluie (projecteurs, but, point de penalty, flaques, immeubles au loin) -> la pluie
s arrête, aube dorée ; joueur en silhouette générique (maillot vert, sans numéro), gardien générique (maillot jaune).
Types : hook bondy monaco mondial euro stamps slam finale reve regard you question logo.
Scènes propres à l histoire du 03/11 v2 (Kylian Mbappé) sauf stamps/slam/you/question/logo.
Usage : python3 render_pluie.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# palette « pluie » : terrain de foot la nuit sous la pluie (projecteurs, but, point de penalty, flaques) -> pluie qui s'arrête, aube dorée
NIGHT = (6, 10, 20); SKY2 = (24, 32, 52); DUSK = (236, 140, 90); DUSK2 = (255, 208, 140)
ACC = (255, 70, 90); AMBER = (255, 184, 80); ICE = (120, 210, 255); SNOW = (210, 225, 240)
ORANGE = ACC; PITCH = (16, 60, 36)
HOR = 900
JER = (20, 170, 110)
FEET = 1500
GOALY = 1080; SPOTY = 1420

def floodlight(d, x, y, s, lit, on=1.0):
    col = mix((20, 24, 34), (90, 80, 90), lit)
    d.line((x, y, x, y - 520 * s), fill=col, width=int(16 * s))
    d.rectangle((x - 90 * s, y - 620 * s, x + 90 * s, y - 520 * s), fill=col)
    for i in range(3):
        for j in range(2):
            cx = x - 60 * s + i * 60 * s; cy = y - 595 * s + j * 50 * s
            d.ellipse((cx - 20 * s, cy - 18 * s, cx + 20 * s, cy + 18 * s), fill=mix(col, (255, 250, 230), on))

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        night = mix(NIGHT, SKY2, u); day = mix((110, 130, 190), mix(DUSK, DUSK2, u), u ** 0.8)
        d.line((0, y, W, y), fill=mix(night, day, lit))
    if lit > 0.25:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((W / 2 - 320, HOR - 340, W / 2 + 320, HOR + 160), fill=(255, 190, 110, int(190 * (lit - 0.25) / 0.75)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(70))); d = ImageDraw.Draw(img)
        d.ellipse((W / 2 - 110, HOR - 190, W / 2 + 110, HOR + 30), fill=mix((255, 150, 80), (255, 226, 160), lit))
    # tribunes + immeubles au loin
    far = mix((12, 16, 28), (110, 90, 100), lit * 0.7)
    for i in range(16):
        x = i * 70; hh = 60 + (i * 53) % 120
        d.rectangle((x, HOR - 80 - hh, x + 60, HOR), fill=far)
        if lit < 0.6:
            for wy in range(int(HOR - 70 - hh), HOR - 20, 30):
                if (i + wy) % 3 == 0: d.rectangle((x + 14, wy, x + 24, wy + 12), fill=mix(AMBER, far, lit))
    d.polygon([(0, HOR - 60), (W, HOR - 60), (W, HOR + 2), (0, HOR + 2)], fill=mix((16, 20, 32), (120, 100, 100), lit * 0.7))
    floodlight(d, 70, HOR - 40, 0.6, lit, 1 - lit * 0.6); floodlight(d, W - 70, HOR - 40, 0.6, lit, 1 - lit * 0.6)
    # pelouse en bandes
    for y in range(HOR, H):
        u = (y - HOR) / (H - HOR)
        band = int((u ** 0.7) * 9) % 2
        g1 = mix((8, 34, 22), (40, 110, 60), lit * 0.8 + 0.1); g2 = mix((12, 44, 28), (54, 130, 72), lit * 0.8 + 0.1)
        d.line((0, y, W, y), fill=mix(g1 if band else g2, (4, 10, 8), 0.4 * (1 - u)))
    lc = mix((140, 160, 170), (240, 240, 235), lit)
    # surface de réparation en perspective
    d.line((W / 2 - 470, 1220, W / 2 + 470, 1220), fill=lc, width=5)
    d.line((W / 2 - 470, 1220, W / 2 - 560, 1560), fill=lc, width=5); d.line((W / 2 + 470, 1220, W / 2 + 560, 1560), fill=lc, width=5)
    d.line((0, GOALY, W, GOALY), fill=lc, width=4)
    d.ellipse((W / 2 - 14, SPOTY - 7, W / 2 + 14, SPOTY + 7), fill=lc)
    goal(d, W / 2, GOALY, 0.95, lit)
    # flaques (reflets)
    rng = np.random.default_rng(21)
    for _ in range(14):
        x, y = rng.uniform(0, W), rng.uniform(HOR + 80, H); w = rng.uniform(60, 180)
        d.ellipse((x - w, y - 10, x + w, y + 10), fill=mix((40, 60, 80), (180, 200, 210), lit * 0.6 + 0.2))
    return img

def goal(d, cx, y, s=1.0, lit=0.0):
    c = mix((200, 210, 225), WHITE, lit)
    w, h = 290 * s, 200 * s
    for i in range(1, 14): d.line((cx - w + i * 2 * w / 14, y - h, cx - w * 0.9 + i * 1.8 * w / 14, y - 30), fill=mix(c, BG, 0.65), width=2)
    for j in range(1, 5): d.line((cx - w, y - h + j * h / 5, cx + w, y - h + j * h / 5), fill=mix(c, BG, 0.7), width=2)
    d.line((cx - w, y, cx - w, y - h), fill=c, width=int(12 * s)); d.line((cx + w, y, cx + w, y - h), fill=c, width=int(12 * s))
    d.line((cx - w, y - h, cx + w, y - h), fill=c, width=int(12 * s))

BG_DARK = make_bg(0.0); BG_LIT = make_bg(1.0)
_BGC = {}
def scenery(level):
    q = round(min(1, max(0, level)) * 20) / 20
    if q not in _BGC: _BGC[q] = Image.blend(BG_DARK, BG_LIT, q)
    return _BGC[q].copy()

def dim(img, a):
    if a <= 0: return
    img.alpha_composite(Image.new("RGBA", (W, H), BG + (int(255 * min(1, a)),)))

DROPS = [(np.random.default_rng(i).uniform(-200, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.4, 1.0)) for i in range(220)]
def rain(d, tg, amt=1.0):
    n = int(len(DROPS) * amt)
    for x0, y0, z in DROPS[:n]:
        y = (y0 + tg * 1500 * z) % (H + 100) - 50; x = (x0 + tg * 260 * z) % (W + 200) - 100
        ln = 40 * z
        d.line((x, y, x + ln * 0.18, y + ln), fill=mix((40, 60, 90), (190, 210, 235), z), width=2)
POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-25, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))
POSES["dive"] = dict(t=0, la=(-170, 10), ra=(170, -10), ll=(-20, 10), rl=(20, -10))

def P(img, x, y, s, pose, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER)
    player(img, x, y, s, pose, **kw)

def keeper(img, x, y, s, k=0.0, side=1):
    """gardien en silhouette (maillot jaune) ; k = 0..1 plongeon."""
    rot = -side * 70 * eout(k)
    P(img, x + side * 140 * eout(k), y - 60 * math.sin(math.pi * min(1, k)), s, blend_pose(POSES["stand"], POSES["dive"], eout(k)), rot=rot, jersey=(230, 200, 40))

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

def coach(d, x, y, s, col=(14, 16, 24)):
    d.rounded_rectangle((x - 50 * s, y - 250 * s, x + 50 * s, y - 70 * s), int(22 * s), fill=col)
    d.ellipse((x - 34 * s, y - 322 * s, x + 34 * s, y - 254 * s), fill=col)
    d.rectangle((x - 38 * s, y - 70 * s, x - 8 * s, y), fill=col); d.rectangle((x + 8 * s, y - 70 * s, x + 38 * s, y), fill=col)
    d.line((x - 40 * s, y - 220 * s, x - 120 * s, y - 150 * s), fill=col, width=int(26 * s))
    d.line((x + 40 * s, y - 220 * s, x + 90 * s, y - 120 * s), fill=col, width=int(26 * s))

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def confetti(d, kv):
    for x0, y0, c in CONF:
        y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[ICE, WHITE, GOLD][c])

def shadow(d, x, y, s, a=1.0):
    d.ellipse((x - 0.35 * s, y - 0.06 * s, x + 0.35 * s, y + 0.06 * s), fill=(6, 14, 10))

def kid(img, d, x, y, s, tg, k):
    P(img, x, y, s, run_pose(tg * 9)); shadow(d, x, y, s)
    ball(d, x + 0.55 * s + 30 * math.sin(tg * 4), y - 0.12 * s - 60 * abs(math.sin(tg * 5)), 0.11 * s, WHITE, tg * 6)

def gshoe(d, cx, cy, s, col=GOLD):
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.polygon([q(-200, 40), q(-190, -60), q(-90, -110), q(10, -90), q(90, -40), q(200, -10), q(220, 40)], fill=col)
    d.rectangle((q(-210, 40)[0], q(0, 40)[1], q(230, 40)[0], q(0, 62)[1]), fill=mix(col, BG, 0.3))
    for i in range(4): d.line((q(-70 + i * 30, -95), q(-50 + i * 30, -60)), fill=mix(col, BG, 0.4), width=max(2, int(5 * s)))

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    keeper(img, W / 2, GOALY - 10, 170)
    ball(d, W / 2, SPOTY - 20, 26, WHITE, 0)
    P(img, W / 2 - 40, 1700, 240, "stand"); shadow(d, W / 2 - 40, 1700, 240)
    text(d, (W / 2, 260), typew("TU AS DÉJÀ TOUT RATÉ…", tg + 0.3, 26), fit("TU AS DÉJÀ TOUT RATÉ…", 84, 980), WHITE, BOLD, stroke=6, scol=BG)
    kk = tg - M("pire", 1.6)
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 440), "AU PIRE", int(fit("AU PIRE", 160, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        text(d, (W / 2, 610), "MOMENT ?", int(fit("MOMENT ?", 170, 980) * sc), WHITE, BOLD, stroke=8, scol=RED)
        hit = max(0, 1 - kk / 0.25)
    return dict(hit=hit, bg=0.0)

def s_bondy(img, d, tg, k):
    hit = 0.0
    label(d, 300, "EN BANLIEUE", k, 110, WHITE, "DE PARIS", ACC)
    k6 = tg - M("six", 99) + 0.1
    kp = tg - M("pere", 99) + 0.1
    if k6 > 0:
        badge(d, W / 2, 640, "6 ANS", k6, GOLD, 120)
        if k6 < 0.25: hit = 1 - k6 / 0.25
        x = lerp(-100, W + 100, (k6 / 3.5) % 1.0) if kp <= 0 else 640
        if kp <= 0: kid(img, d, x, FEET, 170, tg, k6)
        else:
            P(img, 640, FEET, 170, "stand"); shadow(d, 640, FEET, 170)
            ball(d, 720, FEET - 18, 18, WHITE, 0)
            coach(d, 360, FEET, 1.4)
            text(d, (W / 2, 900), "SON PÈRE", int(fit("SON PÈRE", 100, 980) * (1 + 0.3 * (1 - eout(kp / 0.2)))), WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 1010), "PARMI SES ENTRAÎNEURS", fit("PARMI SES ENTRAÎNEURS", 60, 980), ACC, BOLD, stroke=5, scol=BG)
    else:
        P(img, W / 2, FEET, 220, "stand"); shadow(d, W / 2, FEET, 220)
    return dict(hit=hit, bg=0.05)

def s_monaco(img, d, tg, k):
    hit = 0.0
    k16 = tg - M("seize", 99) + 0.1
    if k16 <= 0:
        label(d, 360, "LE CENTRE", k, 110, WHITE, "DE FORMATION", ACC)
        P(img, W / 2, FEET, 220, run_pose(tg * 10)); shadow(d, W / 2, FEET, 220)
    else:
        badge(d, 220, 300, "16 ANS", k16, GOLD, 110)
        if k16 < 0.25: hit = 1 - k16 / 0.25
        hit = max(hit, stamp(img, "LE PLUS JEUNE", (W / 2, 480), 110, -4, tg - M("joueur", 99) + 0.3, WHITE))
        kj = tg - M("joueur", 99) + 0.1
        if kj > 0: text(d, (W / 2, 620), "JOUEUR DU CLUB", fit("JOUEUR DU CLUB", 90, 980), WHITE, BOLD, stroke=6, scol=BG)
        kb = tg - M("buteur", 99) + 0.05
        if kb > 0:
            hit = max(hit, stamp(img, "PUIS LE PLUS JEUNE BUTEUR", (W / 2, 770), 76, -4, kb, ACC))
            u = min(1, kb / 0.4)
            ball(d, lerp(W / 2 + 60, W / 2 - 180, u), lerp(1380, GOALY - 120, u), lerp(30, 18, u), WHITE, tg * 9)
            if kb > 0.4: burst(d, W / 2 - 180, GOALY - 120, kb - 0.4, 16, 200, GOLD, 2)
        P(img, W / 2 + 80, FEET, 220, "kick" if kb > 0 else "stand"); shadow(d, W / 2 + 80, FEET, 220)
    return dict(hit=hit, bg=0.15)

def s_mondial(img, d, tg, k):
    hit = 0.0; flash = 0.0
    k19 = tg - M("dixneuf", SC["mondial"] + 0.1) + 0.1
    if k19 > 0:
        badge(d, 220, 300, "19 ANS", k19, GOLD, 110)
        if k19 < 0.25: hit = 1 - k19 / 0.25
    kc = tg - M("champion", 99) + 0.15
    if kc <= 0:
        text(d, (660, 300), "IL MARQUE", fit("IL MARQUE", 96, 560), WHITE, BOLD, stroke=6, scol=BG)
        text(d, (660, 400), "EN FINALE", 80, ACC, BOLD, stroke=6, scol=BG)
        P(img, W / 2, FEET, 230, "kick"); ball(d, W / 2 + 200, FEET - 300, 30, WHITE, tg * 8)
    else:
        globe(d, W / 2, 800, 250 * (1 + 0.2 * (1 - eout(kc / 0.25))), tg * 1.5, GOLD)
        text(d, (W / 2, 1150), "CHAMPION DU MONDE", fit("CHAMPION DU MONDE", 100, 980), GOLD, BOLD, stroke=7, scol=BG)
        confetti(d, kc)
        if kc < 0.3: hit = max(hit, 1 - kc / 0.3); flash = 0.3 * (1 - kc / 0.3)
        P(img, W / 2, FEET, 200, "up")
    return dict(hit=hit, flash=flash, bg=0.55)

def s_euro(img, d, tg, k):
    hit = 0.0
    dim(img, 0.15)
    kt = tg - M("tirs", 99) + 0.1
    kd = tg - M("dernier", 99) + 0.1
    ka = tg - M("arrete", 99) + 0.1
    ke = tg - M("elimine", 99) + 0.1
    if kd <= 0:
        label(d, 300, "8e DE FINALE", k, 104, WHITE)
        if kt > 0: hit = stamp(img, "TIRS AU BUT", (W / 2, 470), 120, -4, kt, ACC)
        keeper(img, W / 2, GOALY - 10, 170)
        P(img, W / 2, 1700, 240, "stand"); shadow(d, W / 2, 1700, 240)
    else:
        text(d, (W / 2, 300), "LE DERNIER TIR", fit("LE DERNIER TIR", 96, 980), WHITE, BOLD, stroke=6, scol=BG)
        kl = tg - M("lui", 99) + 0.1
        if kl > 0: text(d, (W / 2, 420), "C'EST LUI", int(90 * (1 + 0.3 * (1 - eout(kl / 0.2)))), ACC, BOLD, stroke=6, scol=BG)
        kk = max(0.0, (ka + 0.35) / 0.35) if ka > -0.35 else 0.0
        keeper(img, W / 2, GOALY - 10, 170, min(1, kk), -1)
        if ka > -0.35:
            u = min(1, (ka + 0.35) / 0.35)
            bx = lerp(W / 2, W / 2 - 200, u); by = lerp(SPOTY - 20, GOALY - 120, u)
            if ka > 0: bx += -80 * eout(ka / 0.5); by += 260 * eout(ka / 0.5)
            ball(d, bx, by, lerp(26, 18, u), WHITE, tg * 9)
        else:
            ball(d, W / 2, SPOTY - 20, 26, WHITE, 0)
        if ka > 0: hit = max(hit, stamp(img, "ARRÊTÉ", (W / 2, 640), 170, -6, ka, RED))
        if ke > 0: text(d, (W / 2, 1220), "LA FRANCE EST ÉLIMINÉE", fit("LA FRANCE EST ÉLIMINÉE", 70, 980), WHITE, BOLD, stroke=6, scol=RED)
        P(img, W / 2, 1700, 240, "sad" if ka > 0.2 else ("kick" if ka > -0.3 else "stand")); shadow(d, W / 2, 1700, 240)
    return dict(hit=hit, bg=0.0)

def s_stamps(img, d, tg, k):
    dim(img, 0.5)
    P(img, W / 2, 1500, 230, "sad", alpha=0.8)
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
            if r > 0: d.ellipse((W / 2 - r, 1450 - r * 0.35, W / 2 + r, 1450 + r * 0.35), outline=GOLD, width=max(1, int(16 * max(0, 1 - r / 1500))))
        burst(d, W / 2, 1100, kk, 22, 520, WHITE, 3, 9)
        flash = max(0, 0.9 - kb * 4) if kb > 0 else 0
        hit = max(0, 1 - kk / 0.3)
    shadow(d, W / 2, 1500, 300)
    P(img, W / 2, 1500, 300, pose, glow=1.0)
    if kb > -0.08:
        kk = kb + 0.08; sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 330), "IL A", 110, GOLD, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 520), "CONTINUÉ !", int(fit("CONTINUÉ !", 200, 1000) * sc), WHITE, BOLD, stroke=10, scol=ACC)
    else:
        text(d, (W / 2, 420), typew("SE CACHER ?", max(0, tg - K["build_start"] + 0.2), 24), fit("SE CACHER ?", 110, 1000), GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_finale(img, d, tg, k):
    hit = 0.0; flash = 0.0
    t3 = M("trois", SC["finale"] + 2.5)
    k2 = tg - M("tirs2", 99) + 0.1
    if tg < t3 - 0.15:
        label(d, 320, "18 MOIS PLUS TARD", k, 92, WHITE, "NOUVELLE FINALE DE COUPE DU MONDE", GOLD)
        P(img, W / 2, FEET, 220, run_pose(tg * 11)); shadow(d, W / 2, FEET, 220)
    elif k2 <= 0:
        k3 = tg - t3 + 0.1
        n = min(3, 1 + int(k3 / 0.3))
        for i in range(n): ball(d, W / 2 - 230 + i * 230, 360, 75, WHITE, tg * 5 + i)
        if k3 < 0.9 and abs((k3 % 0.3) - 0.02) < 0.05: hit = 0.8
        ktr = tg - M("triple", 99) + 0.05
        if ktr > 0:
            hit = max(hit, stamp(img, "TRIPLÉ EN FINALE", (W / 2, 600), 120, -5, ktr, GOLD))
            burst(d, W / 2, 600, ktr, 20, 420, GOLD, 4)
            if ktr < 0.2: flash = 0.25 * (1 - ktr / 0.2)
        P(img, W / 2, FEET, 220, "up" if ktr > 0 else run_pose(tg * 11))
    else:
        text(d, (W / 2, 300), "TIRS AU BUT", fit("TIRS AU BUT", 100, 980), WHITE, BOLD, stroke=6, scol=BG)
        kp = tg - M("premier", 99) + 0.1
        if kp > 0: text(d, (W / 2, 410), "IL TIRE LE PREMIER", fit("IL TIRE LE PREMIER", 70, 980), GOLD, BOLD, stroke=5, scol=BG)
        km = tg - M("marque2", 99) + 0.1
        kpe = tg - M("perd", 99) + 0.1
        kme = tg - M("meilleur", 99) + 0.1
        if kme <= 0:
            keeper(img, W / 2, GOALY - 10, 170, min(1, max(0, km + 0.3) / 0.35), 1)
            if km > -0.3:
                u = min(1, (km + 0.3) / 0.35)
                ball(d, lerp(W / 2, W / 2 - 190, u), lerp(SPOTY - 20, GOALY - 120, u), lerp(26, 18, u), WHITE, tg * 9)
            else: ball(d, W / 2, SPOTY - 20, 26, WHITE, 0)
            if km > 0:
                hit = max(hit, stamp(img, "IL MARQUE", (W / 2, 620), 150, -5, km, GREEN))
                burst(d, W / 2 - 190, GOALY - 120, km, 16, 220, GOLD, 2)
            if kpe > 0: text(d, (W / 2, 780), "LA FRANCE PERD QUAND MÊME", fit("LA FRANCE PERD QUAND MÊME", 60, 980), GREY, BOLD, stroke=5, scol=BG)
            P(img, W / 2, 1700, 240, "kick" if km > -0.3 else "stand")
        else:
            star(d, W / 2, 640, 150 * (1 + 0.3 * (1 - eout(kme / 0.2))), GOLD)
            hit = max(hit, stamp(img, "MEILLEUR BUTEUR", (W / 2, 900), 120, -4, kme, GOLD))
            text(d, (W / 2, 1080), "DU TOURNOI", fit("DU TOURNOI", 100, 980), WHITE, BOLD, stroke=6, scol=BG)
            confetti(d, kme)
            if kme < 0.3: hit = max(hit, 1 - kme / 0.3); flash = 0.25 * (1 - kme / 0.3)
            P(img, W / 2, FEET, 200, "up")
    return dict(hit=hit, flash=flash, bg=0.7)

def s_reve(img, d, tg, k):
    hit = 0.0; flash = 0.0
    text(d, (W / 2, 290), "LE CLUB", 96, WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 400), "DE SES RÊVES", fit("DE SES RÊVES", 110, 980), GOLD, BOLD, stroke=7, scol=BG)
    kr = tg - M("reves", 99) + 0.1
    if kr > 0:
        star(d, W / 2, 620, 90 * (1 + 0.3 * (1 - eout(kr / 0.2))), GOLD)
        if kr < 0.25: hit = 1 - kr / 0.25
    k31 = tg - M("trenteun", 99) + 0.1
    ke = tg - M("europe", 99) + 0.1
    if k31 > 0:
        n = 31 if ke > -0.4 else min(31, int(31 * eout(k31 / 0.8)))
        text(d, (W / 2, 860), f"{n} BUTS", int(150 * (1 + 0.15 * (1 - eout(k31 / 0.2)))), WHITE, BOLD, stroke=8, scol=BG)
        text(d, (W / 2, 990), "EN CHAMPIONNAT", 62, ACC, BOLD, stroke=5, scol=BG)
    if ke > 0:
        gshoe(d, W / 2, 1170, 0.9 * (1 + 0.25 * (1 - eout(ke / 0.2))), GOLD)
        hit = max(hit, stamp(img, "MEILLEUR BUTEUR D'EUROPE", (W / 2, 1310), 70, -4, ke, GOLD))
        if ke < 0.25: flash = 0.25 * (1 - ke / 0.25)
        confetti(d, ke)
    else:
        P(img, W / 2, FEET, 200, "up" if k31 > 0 else run_pose(tg * 10))
    return dict(hit=hit, flash=flash, bg=0.85)

def s_regard(img, d, tg, k):
    hit = 0.0
    kj = tg - M("jamais", 99) + 0.1
    text(d, (W / 2, 290), "LE GAMIN QUI A RATÉ", fit("LE GAMIN QUI A RATÉ", 80, 980), GREY if kj > 0 else WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 390), "LE TIR LE PLUS IMPORTANT…", fit("LE TIR LE PLUS IMPORTANT…", 62, 980), GREY if kj > 0 else WHITE, BOLD, stroke=5, scol=BG)
    if kj > 0:
        text(d, (W / 2, 560), "N'A JAMAIS ARRÊTÉ", int(fit("N'A JAMAIS ARRÊTÉ", 100, 980) * (1 + 0.3 * (1 - eout(kj / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
        hit = stamp(img, "DE TIRER", (W / 2, 710), 150, -5, kj, GOLD)
    # tirs répétés dans le but
    ph = (k % 1.4) / 1.4
    u = min(1, ph / 0.4)
    ball(d, lerp(W / 2 + 40, W / 2 + [-180, 160, 0][int(k / 1.4) % 3], u), lerp(SPOTY - 20, GOALY - 120, u), lerp(26, 18, u), WHITE, tg * 9)
    if ph > 0.4: burst(d, W / 2 + [-180, 160, 0][int(k / 1.4) % 3], GOALY - 120, (ph - 0.4) * 1.4, 14, 160, GOLD, int(k / 1.4))
    P(img, W / 2 + 60, 1700, 200, "kick" if ph < 0.3 else "up"); shadow(d, W / 2 + 60, 1700, 200)
    return dict(hit=hit, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ACC, BOLD, stroke=6, scol=BG)
    rows = [("6 ANS", "le club de sa ville"), ("19 ANS", "champion du monde"), ("ARRÊTÉ", "éliminé"), ("TRIPLÉ", "en finale")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 90 - 80 * (1 - eout(kk / 0.2))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD if i == 3 else ACC)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 45, y), a, 42, GOLD if i == 3 else WHITE, MONO, "lm"); text(d, (x + 380, y), b, 40, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "UN ÉCHEC ?", (W / 2, 1180), 150, -5, kn + 0.05, RED) if kn > -0.05 else 0.0
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



RAIN = {"hook": 1.0, "bondy": 0.8, "monaco": 0.6, "mondial": 0.3, "euro": 1.0, "stamps": 1.0, "slam": 0.7, "finale": 0.3,
        "reve": 0.1, "regard": 0.0, "you": 0.5, "question": 0.4, "logo": 0.2}
def _wrap(name, f):
    def g(img, d, tg, k):
        rain(d, tg, RAIN.get(name, 0.5)); return f(img, d, tg, k)
    return g
SCENES = {n: _wrap(n, f) for n, f in {"hook": s_hook, "bondy": s_bondy, "monaco": s_monaco, "mondial": s_mondial, "euro": s_euro,
          "stamps": s_stamps, "slam": s_slam, "finale": s_finale, "reve": s_reve, "regard": s_regard,
          "you": s_you, "question": s_question, "logo": s_logo}.items()}
BGLEVEL = {"hook": 0.0, "bondy": 0.05, "monaco": 0.15, "mondial": 0.55, "euro": 0.0, "stamps": 0.0, "slam": 0.1, "finale": 0.7,
           "reve": 0.85, "regard": 1.0, "you": 0.2, "question": 0.0, "logo": 0.0}
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

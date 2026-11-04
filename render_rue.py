# -*- coding: utf-8 -*-
"""Style « rue » : rue d immeubles blancs la nuit (balcons, lampadaires), terrain de basket en plein air (panier, grillage) -> projecteurs de salle, aube dorée.
Personnage « athlète » détaillé, maillot violet sans numéro (aucune couleur d équipe réelle). Aucun nom propre à l écran.
Types : hook athenes rue baskets salle draft pivot progres finale regard you question logo (scènes propres à l histoire du 04/11 : Giannis Antetokounmpo).
Usage : python3 render_rue.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# palette « rue » : rue d'immeubles blancs la nuit (balcons, lampadaires), trottoir, terrain de basket en plein air (panier, grillage)
# -> aube dorée et projecteurs de salle. Personnage « athlète » détaillé, maillot violet sans numéro (aucune couleur d'équipe réelle).
NIGHT = (7, 10, 22); SKY2 = (30, 30, 58); DUSK = (236, 140, 90); DUSK2 = (255, 210, 140)
ACC = (255, 120, 40); AMBER = (255, 190, 90); ICE = (130, 200, 255); VIO = (150, 100, 235)
ORANGE = ACC
HOR = 930
JER = (120, 78, 210)
FEET = 1500
RIMX, RIMY = 830, 1010

def lamp(d, x, y, lit):
    col = mix((26, 28, 40), (90, 80, 90), lit)
    d.line((x, y, x, y - 430), fill=col, width=10)
    d.line((x, y - 430, x - 70, y - 450), fill=col, width=8)
    d.ellipse((x - 100, y - 465, x - 50, y - 440), fill=mix((255, 214, 140), col, lit * 0.8))

def hoop(d, lit):
    pc = mix((60, 64, 80), (180, 180, 190), lit)
    d.line((RIMX + 150, FEET - 40, RIMX + 150, RIMY - 120), fill=pc, width=16)
    d.line((RIMX + 150, RIMY - 120, RIMX + 60, RIMY - 120), fill=pc, width=12)
    bc = mix((150, 160, 180), WHITE, lit)
    d.rectangle((RIMX - 90, RIMY - 230, RIMX + 60, RIMY - 30), outline=bc, width=8)
    d.rectangle((RIMX - 40, RIMY - 120, RIMX + 20, RIMY - 50), outline=bc, width=5)
    d.ellipse((RIMX - 70, RIMY - 14, RIMX + 30, RIMY + 14), outline=ACC, width=7)
    for i in range(7):
        x0 = RIMX - 66 + i * 15; d.line((x0, RIMY + 6, RIMX - 20 + (x0 - RIMX + 20) * 0.6, RIMY + 90), fill=mix((120, 120, 130), WHITE, lit), width=2)
    for j in range(3):
        y = RIMY + 30 + j * 25; w = 46 - j * 8; d.line((RIMX - 20 - w, y, RIMX - 20 + w, y), fill=mix((120, 120, 130), WHITE, lit), width=2)

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        night = mix(NIGHT, SKY2, u); day = mix((110, 130, 190), mix(DUSK, DUSK2, u), u ** 0.8)
        d.line((0, y, W, y), fill=mix(night, day, lit))
    if lit > 0.25:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((W / 2 - 320, HOR - 380, W / 2 + 320, HOR + 120), fill=(255, 190, 110, int(190 * (lit - 0.25) / 0.75)))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(70))); d = ImageDraw.Draw(img)
        d.ellipse((W / 2 - 110, HOR - 230, W / 2 + 110, HOR - 10), fill=mix((255, 150, 80), (255, 226, 160), lit))
    # immeubles blancs à balcons (au loin puis devant)
    for row, (base, dk) in enumerate(((HOR - 40, 0.55), (HOR + 10, 0.0))):
        for i in range(7 if row == 0 else 4):
            if row == 0: x = i * 160 - 40; w = 140; hh = 260 + (i * 71) % 160
            else: x = [-60, 210, 640, 900][i]; w = [240, 300, 220, 260][i]; hh = [520, 430, 560, 470][i]
            if row == 1 and x + w > 560 and x < 1000: hh = min(hh, 330)
            wall = mix(mix((40, 44, 64), (226, 214, 196), lit), NIGHT, dk)
            d.rectangle((x, base - hh, x + w, base), fill=wall)
            for fy in range(int(base - hh + 30), int(base - 30), 70):
                d.line((x + 8, fy + 44, x + w - 8, fy + 44), fill=mix(wall, (0, 0, 0), 0.35), width=5)   # balcons
                for fx in range(int(x + 20), int(x + w - 30), 52):
                    on = ((fx * 7 + fy * 3 + i) % 5) < 2
                    wc = mix(AMBER, wall, 0.2 + 0.6 * lit) if on else mix(wall, (0, 0, 0), 0.4)
                    d.rectangle((fx, fy, fx + 26, fy + 34), fill=wc)
    # trottoir + grillage + sol du terrain
    for y in range(HOR + 10, H):
        u = (y - HOR) / (H - HOR)
        d.line((0, y, W, y), fill=mix(mix((22, 24, 34), (150, 120, 110), lit * 0.8), (8, 8, 14), 0.5 * (1 - u)))
    fc = mix((70, 76, 96), (200, 190, 180), lit)
    for x in range(0, W, 46): d.line((x, HOR + 10, x + 46, HOR + 140), fill=fc, width=2); d.line((x + 46, HOR + 10, x, HOR + 140), fill=fc, width=2)
    d.line((0, HOR + 10, W, HOR + 10), fill=fc, width=5); d.line((0, HOR + 140, W, HOR + 140), fill=fc, width=5)
    lc = mix((150, 150, 170), (245, 240, 230), lit)
    d.line((0, 1260, W, 1260), fill=lc, width=5)
    d.arc((RIMX - 520, 1150, RIMX + 360, 1700), 100, 260, fill=lc, width=5)
    d.rectangle((RIMX - 200, 1220, RIMX + 160, 1560), outline=lc, width=5)
    lamp(d, 120, HOR + 150, lit); lamp(d, 520, HOR + 150, lit)
    hoop(d, lit)
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

DUST = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.3, 1.0)) for i in range(70)]
def dust(d, tg, amt=1.0):
    for x0, y0, z in DUST[:int(len(DUST) * amt)]:
        y = (y0 - tg * 40 * z) % H; x = x0 + 20 * math.sin(tg * 0.8 + x0)
        r = 1.5 + 2.5 * z; d.ellipse((x - r, y - r, x + r, y + r), fill=mix((40, 40, 60), (255, 220, 160), z * 0.7))

POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-25, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))
POSES["shoot"] = dict(t=-4, la=(-165, -25), ra=(-150, -40), ll=(-6, 2), rl=(8, -2))
POSES["dunk"] = dict(t=-10, la=(-170, -5), ra=(-150, 30), ll=(-40, 60), rl=(25, 40))
POSES["fist"] = dict(t=-4, la=(-172, -6), ra=(25, -70), ll=(-14, 4), rl=(14, -4))
POSES["lie"] = dict(t=0, la=(-30, 20), ra=(40, -60), ll=(-8, 10), rl=(10, -10))

def P(img, x, y, s, pose, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER); kw.setdefault("shorts", mix(JER, (0, 0, 0), 0.15)); kw.setdefault("sock", (236, 236, 240))
    player(img, x, y, s, pose, **kw)

def bball(d, x, y, r, rot=0.0):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(232, 112, 30), outline=(40, 20, 10), width=max(2, int(r / 9)))
    w = max(2, int(r / 10))
    d.line((x - r * math.cos(rot), y - r * math.sin(rot), x + r * math.cos(rot), y + r * math.sin(rot)), fill=(40, 20, 10), width=w)
    d.arc((x - r * 0.55, y - r, x + r * 0.55, y + r), 0, 360, fill=(40, 20, 10), width=w)

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

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def confetti(d, kv):
    for x0, y0, c in CONF:
        y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[VIO, WHITE, GOLD][c])

def watch(d, x, y, r, col=(200, 200, 210)):
    d.rectangle((x - r * 0.45, y - r * 1.9, x + r * 0.45, y + r * 1.9), fill=(60, 44, 34))
    d.ellipse((x - r, y - r, x + r, y + r), fill=col); d.ellipse((x - r * 0.78, y - r * 0.78, x + r * 0.78, y + r * 0.78), fill=(30, 34, 44))
    d.line((x, y, x, y - r * 0.6), fill=WHITE, width=3); d.line((x, y, x + r * 0.45, y), fill=WHITE, width=3)

def glasses(d, x, y, s, col=(20, 20, 26), frame=(230, 200, 120)):
    for dx in (-1, 1):
        d.ellipse((x + dx * 40 * s - 34 * s, y - 24 * s, x + dx * 40 * s + 34 * s, y + 24 * s), fill=col, outline=frame, width=max(2, int(4 * s)))
    d.arc((x - 12 * s, y - 14 * s, x + 12 * s, y + 6 * s), 200, 340, fill=frame, width=max(2, int(4 * s)))

def sneaker(d, cx, cy, s, col=(235, 235, 240), acc=VIO):
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.polygon([q(-150, 40), q(-140, -50), q(-70, -90), q(10, -70), q(80, -30), q(160, -5), q(170, 40)], fill=col)
    d.rectangle((q(-160, 40)[0], q(0, 40)[1], q(175, 40)[0], q(0, 62)[1]), fill=mix(col, (0, 0, 0), 0.25))
    d.line((q(-120, -10), q(60, -10)), fill=acc, width=max(3, int(12 * s)))
    for i in range(4): d.line((q(-60 + i * 25, -80), q(-40 + i * 25, -50)), fill=mix(col, (0, 0, 0), 0.4), width=max(2, int(5 * s)))

def cone(img, x, a=1.0, col=(255, 236, 190)):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(x - 40, 0), (x + 40, 0), (x + 300, FEET + 60), (x - 300, FEET + 60)], fill=col + (int(110 * a),))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(24)))

def bubble_text(d, y, s, col=GREY, size=64):
    text(d, (W / 2, y), s, fit(s, size, 980), col, BOLD, stroke=5, scol=BG)

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

def shadow(d, x, y, s, a=1.0):
    d.ellipse((x - 0.33 * s, y - 0.05 * s, x + 0.33 * s, y + 0.05 * s), fill=(6, 14, 10))

# --------------------------------------------------------------- scènes (histoire du 04/11 : Giannis Antetokounmpo — aucun nom propre à l'écran)
def s_hook(img, d, tg, k):
    hit = 0.0
    series_banner(d, tg)
    P(img, W / 2, FEET + 60, 260, "stand"); shadow(d, W / 2, FEET + 60, 260)
    text(d, (W / 2, 260), typew("TU CROIS QUE TU PARS", tg + 0.3, 30), fit("TU CROIS QUE TU PARS", 84, 980), WHITE, BOLD, stroke=6, scol=BG)
    kk = tg - K["hook"] + 0.1
    if kk > -0.05:
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 470), "AVEC RIEN ?", int(fit("AVEC RIEN ?", 180, 1000) * sc), WHITE, BOLD, stroke=9, scol=ACC)
        hit = max(0, 1 - kk / 0.25)
    return dict(hit=hit, bg=0.0)

def s_athenes(img, d, tg, k):
    hit = 0.0
    series_banner(d, tg)
    label(d, 300, "UNE FAMILLE", k, 110, WHITE, "VENUE D'AFRIQUE DE L'OUEST", ACC)
    k6 = tg - M("six", 99) + 0.1
    kc = tg - M("chambres", 99) + 0.1
    if k6 > 0:
        dim(img, 0.25); d = ImageDraw.Draw(img)
        # une fenêtre allumée : 6 silhouettes serrées
        x0, y0, w, h = W / 2 - 330, 560, 660, 470
        d.rectangle((x0, y0, x0 + w, y0 + h), fill=(255, 196, 110), outline=(40, 30, 30), width=14)
        d.line((x0 + w / 2, y0, x0 + w / 2, y0 + h), fill=(40, 30, 30), width=12)
        n = min(6, 1 + int(k6 / 0.12))
        for i in range(n):
            cx = x0 + 70 + i * 104; hh = [200, 260, 150, 140, 230, 120][i]
            d.ellipse((cx - 34, y0 + h - hh - 70, cx + 34, y0 + h - hh), fill=(40, 26, 22))
            d.rounded_rectangle((cx - 46, y0 + h - hh, cx + 46, y0 + h), 30, fill=(40, 26, 22))
        badge(d, W / 2, 1150, "6", k6, GOLD, 100)
        if k6 < 0.25: hit = 1 - k6 / 0.25
        if kc > 0:
            hit = max(hit, stamp(img, "2 CHAMBRES", (W / 2, 1300), 120, -5, kc, WHITE))
    else:
        P(img, W / 2, FEET, 220, "stand"); shadow(d, W / 2, FEET, 220)
    return dict(hit=hit, bg=0.05)

def s_rue(img, d, tg, k):
    hit = 0.0
    label(d, 290, "POUR AIDER SA FAMILLE", k, 84, WHITE, "IL VEND DANS LA RUE", ACC)
    # couverture au sol + objets
    d.polygon([(170, 1530), (910, 1530), (980, 1680), (100, 1680)], fill=(70, 40, 60))
    d.polygon([(170, 1530), (910, 1530), (980, 1680), (100, 1680)], outline=(150, 100, 130), width=4)
    km = tg - M("montres", 99) + 0.1
    kl = tg - M("lunettes", 99) + 0.1
    P(img, 260, 1500, 230, "stand", jersey=(80, 90, 120), shorts=(50, 56, 80))   # grand frère
    P(img, 820, 1500, 200, "stand")
    for i in range(4): watch(d, 330 + i * 90, 1600, 26)
    for i in range(3): glasses(d, 720 + (i % 2) * 120, 1580 + (i // 2) * 60, 0.8)
    if km > 0:
        hit = max(hit, stamp(img, "DES MONTRES", (W / 2, 620), 130, -5, km, AMBER))
        watch(d, W / 2, 900, 90 * (1 + 0.3 * (1 - eout(km / 0.2))))
    if kl > 0:
        hit = max(hit, stamp(img, "DES LUNETTES", (W / 2, 1150), 120, 4, kl, WHITE))
        glasses(d, W / 2, 1320, 1.6 * (1 + 0.3 * (1 - eout(kl / 0.2))))
    return dict(hit=hit, bg=0.08)

def s_baskets(img, d, tg, k):
    hit = 0.0
    kd = tg - M("deux2", 99) + 0.1
    kf = tg - M("frere2", 99) + 0.1
    kj = tg - M("jouer", 99) + 0.1
    if kf <= 0:
        dim(img, 0.45); d = ImageDraw.Draw(img)
        cone(img, W / 2, 1.0); d = ImageDraw.Draw(img)
        text(d, (W / 2, 330), "UNE SEULE PAIRE", fit("UNE SEULE PAIRE", 110, 980), WHITE, BOLD, stroke=7, scol=BG)
        sneaker(d, W / 2 - 170, 900, 1.0 * (1 + 0.1 * math.sin(tg * 3))); sneaker(d, W / 2 + 170, 960, 1.0)
        if kd > 0:
            hit = stamp(img, "POUR 2", (W / 2, 1250), 200, -6, kd, ACC)
    else:
        text(d, (W / 2, 300), "IL ATTEND…", fit("IL ATTEND…", 110, 980), WHITE, BOLD, stroke=7, scol=BG)
        # le frère joue, lui attend assis au bord du terrain
        bx = RIMX - 240 + 120 * math.sin(tg * 2.2)
        P(img, bx, FEET, 220, run_pose(tg * 10), jersey=(80, 90, 120), shorts=(50, 56, 80)); shadow(d, bx, FEET, 220)
        bball(d, bx + 70, FEET - 60 - 140 * abs(math.sin(tg * 6)), 24, tg * 5)
        if kj <= 0:
            P(img, 230, FEET + 100, 220, "sit"); shadow(d, 230, FEET + 100, 220)
            text(d, (W / 2, 420), "QUE SON FRÈRE SORTE", fit("QUE SON FRÈRE SORTE", 70, 980), GREY, BOLD, stroke=5, scol=BG)
        else:
            P(img, 260, FEET + 100, 230, "up"); shadow(d, 260, FEET + 100, 230)
            text(d, (W / 2, 430), "POUR JOUER", int(fit("POUR JOUER", 120, 980) * (1 + 0.3 * (1 - eout(kj / 0.2)))), ACC, BOLD, stroke=7, scol=BG)
            if kj < 0.25: hit = 1 - kj / 0.25
    return dict(hit=hit, bg=0.1)

def s_salle(img, d, tg, k):
    hit = 0.0
    k12 = tg - M("douze", SC["salle"] + 0.1) + 0.1
    kt = tg - M("soirs", 99) + 0.1
    if kt <= 0:
        badge(d, 220, 300, "12 ANS", k12, GOLD, 110)
        if 0 < k12 < 0.25: hit = 1 - k12 / 0.25
        text(d, (650, 300), "ON LE REPÈRE", fit("ON LE REPÈRE", 80, 600), WHITE, BOLD, stroke=6, scol=BG)
        x = W / 2 - 60
        P(img, x, FEET, 230, run_pose(tg * 8)); shadow(d, x, FEET, 230)
        bball(d, x + 90, FEET - 40 - 160 * abs(math.sin(tg * 6)), 26, tg * 5)
        # recruteur qui observe
        d.rounded_rectangle((90, FEET - 300, 170, FEET - 90), 26, fill=(14, 16, 26)); d.ellipse((96, FEET - 370, 164, FEET - 302), fill=(14, 16, 26))
    else:
        dim(img, 0.6); d = ImageDraw.Draw(img)
        text(d, (W / 2, 330), "CERTAINS SOIRS", fit("CERTAINS SOIRS", 110, 980), WHITE, BOLD, stroke=7, scol=BG)
        ka = tg - M("tapis", 99) + 0.1
        if ka > 0:
            text(d, (W / 2, 450), "IL DORT À LA SALLE", int(fit("IL DORT À LA SALLE", 86, 980) * (1 + 0.2 * (1 - eout(ka / 0.2)))), ACC, BOLD, stroke=6, scol=BG)
            if ka < 0.25: hit = 1 - ka / 0.25
        # tapis de gym + garçon allongé, lune par la fenêtre
        d.rounded_rectangle((180, 1380, 900, 1450), 18, fill=(60, 80, 140)); d.rounded_rectangle((180, 1380, 900, 1450), 18, outline=(120, 140, 200), width=4)
        P(img, 520, 1390, 240, "lie", rot=90, glow=0.6)
        d.ellipse((800, 640, 900, 740), fill=(230, 230, 210))
        for i in range(3): text(d, (360 + i * 60, 1200 - i * 60 - 20 * math.sin(tg * 2 + i)), "z", 50 + i * 12, GREY, BOLD)
    return dict(hit=hit, bg=0.0)

def s_draft(img, d, tg, k):
    hit = 0.0
    k18 = tg - M("dixhuit", SC["draft"] + 0.1) + 0.1
    kc = tg - M("choisit", 99) + 0.1
    kq = tg - M("quinze", 99) + 0.1
    badge(d, 220, 300, "18 ANS", k18, GOLD, 110)
    if 0 < k18 < 0.25: hit = 1 - k18 / 0.25
    if kc <= 0:
        text(d, (650, 300), "UN PETIT CLUB", fit("UN PETIT CLUB", 80, 600), WHITE, BOLD, stroke=6, scol=BG)
        P(img, W / 2, FEET, 230, "shoot"); shadow(d, W / 2, FEET, 230)
        bball(d, W / 2 - 30, FEET - 420, 26, tg * 3)
    else:
        dim(img, 0.55); cone(img, W / 2, min(1, kc / 0.3)); d = ImageDraw.Draw(img)
        text(d, (W / 2, 560), "UNE ÉQUIPE AMÉRICAINE", fit("UNE ÉQUIPE AMÉRICAINE", 72, 980), WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 660), "LE CHOISIT", fit("LE CHOISIT", 96, 980), WHITE, BOLD, stroke=6, scol=BG)
        P(img, W / 2, FEET, 260, "fist" if kq > 0 else "stand", glow=1.4); shadow(d, W / 2, FEET, 260)
        if kq > 0:
            hit = max(hit, stamp(img, "15e CHOIX", (W / 2, 880), 170, -5, kq, GOLD))
            burst(d, W / 2, 880, kq, 18, 380, GOLD, 4)
    return dict(hit=hit, bg=0.1)

def s_pivot(img, d, tg, k):
    kb = tg - K["boom"]
    hit = 0.0; flash = 0.0; bgl = 0.0
    if kb < -0.06:
        dim(img, 0.55); d = ImageDraw.Draw(img)
        k7 = tg - M("sept", 99) + 0.1
        text(d, (W / 2, 300), "1re SAISON", fit("1re SAISON", 96, 980), WHITE, BOLD, stroke=6, scol=BG)
        if k7 > 0:
            # tableau d'affichage
            d.rounded_rectangle((W / 2 - 300, 400, W / 2 + 300, 640), 20, fill=(12, 12, 18), outline=(80, 80, 96), width=6)
            n = min(6.8, 6.8 * eout(k7 / 0.6))
            text(d, (W / 2, 500), f"{n:.1f}".replace(".", ","), 130, (255, 80, 60), MONO)
            text(d, (W / 2, 600), "POINTS / MATCH", 40, GREY, MONO)
        kp = tg - K["build_start"] + 0.1
        if kp > 0: text(d, (W / 2, 760), typew("PRESQUE PERSONNE", kp, 26), fit("PRESQUE PERSONNE", 84, 980), GREY, BOLD, stroke=6, scol=BG)
        if kp > 0.6: text(d, (W / 2, 860), typew("NE CONNAÎT SON NOM", kp - 0.6, 26), fit("NE CONNAÎT SON NOM", 70, 980), GREY, BOLD, stroke=5, scol=BG)
        kl = tg - M("lache", 99) + 0.1
        if kl > 0:
            hit = max(hit, stamp(img, "IL NE LÂCHE RIEN", (W / 2, 1020), 100, -4, kl, ACC))
        # il tire seul, encore et encore
        ph = (k % 1.2) / 1.2
        P(img, W / 2 - 120, FEET, 220, "shoot" if ph < 0.35 else "stand", glow=0.6); shadow(d, W / 2 - 120, FEET, 220)
        u = min(1, max(0, (ph - 0.2) / 0.5))
        if u > 0: bball(d, lerp(W / 2 - 140, RIMX - 20, u), lerp(FEET - 400, RIMY - 30, u) - 260 * math.sin(math.pi * u), 22, tg * 5)
    else:
        kk = kb + 0.06; bgl = 0.4
        # les projecteurs de la salle s'allument un par un
        for i in range(5):
            if kk > i * 0.07: cone(img, 120 + i * 210, 1.0)
        d = ImageDraw.Draw(img)
        if kk < 0.4: flash = max(0, 0.95 - kk * 2.4)
        sw = eout(kk / 0.6)
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((W / 2 - 900 * sw, FEET - 120 * sw, W / 2 + 900 * sw, FEET + 120 * sw), fill=GOLD + (int(150 * (1 - sw * 0.6)),))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(30))); d = ImageDraw.Draw(img)
        P(img, RIMX - 40, RIMY + 470 - 260 * eout(min(1, kk / 0.35)), 280, "dunk", glow=1.6)
        bball(d, RIMX - 20, RIMY + 30 * eout(min(1, kk / 0.4)), 26, tg * 6)
        burst(d, RIMX - 20, RIMY, kk, 22, 420, GOLD, 3, 9)
        hit = max(0, 1 - kk / 0.3)
        e = eout(kk / 0.22)
        x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, e)
        for off, c in ((10, (255, 60, 80)), (-10, (80, 220, 255)), (0, WHITE)):
            o = off * (1 - e) + (off * 0.25 if off else 0)
            text(d, (x1 + o, 330), "LE MONDE VA", fit("LE MONDE VA", 130, 1000), c, BOLD, stroke=8 if c == WHITE else 0, scol=BG)
            text(d, (x2 - o, 490), "APPRENDRE", fit("APPRENDRE", 160, 1000), c if c != WHITE else GOLD, BOLD, stroke=9 if c == WHITE else 0, scol=BG)
            text(d, (x1 + o, 650), "SON NOM !", fit("SON NOM !", 170, 1000), c if c != WHITE else GOLD, BOLD, stroke=9 if c == WHITE else 0, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_progres(img, d, tg, k):
    hit = 0.0; flash = 0.0
    label(d, 270, "4 ANS PLUS TARD", k, 92, WHITE)
    rows = [("pro", "LE PLUS PROGRESSÉ", ICE), ("mvp", "MEILLEUR JOUEUR", GOLD), ("suite", "× 2 DE SUITE", GOLD), ("def", "DÉFENSEUR DE L'ANNÉE", WHITE)]
    for i, (m, s, c) in enumerate(rows):
        kk = tg - M(m, 99) + 0.1
        if kk <= 0: continue
        y = 450 + i * 150
        star(d, 120, y, 46 * (1 + 0.4 * (1 - eout(kk / 0.2))), c)
        text(d, (190, y), typew(s, kk, 40), fit(s, 76, 860), c, BOLD, "lm", stroke=5, scol=BG)
        if kk < 0.25: hit = max(hit, 1 - kk / 0.25)
    ph = (k % 1.6) / 1.6
    if ph < 0.5:
        u = eout(ph / 0.5); P(img, lerp(300, RIMX - 40, u), FEET - 300 * math.sin(math.pi * min(1, ph / 0.6)), 240, "dunk" if u > 0.6 else run_pose(tg * 10))
    else:
        P(img, RIMX - 60, FEET, 240, "fist"); bball(d, RIMX - 20, lerp(RIMY + 40, FEET - 20, min(1, (ph - 0.5) / 0.3)), 24, tg * 4)
    shadow(d, RIMX - 60, FEET, 240)
    return dict(hit=hit, flash=flash, bg=0.55)

def s_finale(img, d, tg, k):
    hit = 0.0; flash = 0.0
    k50 = tg - M("cinquante", 99) + 0.1
    kc = tg - M("championne", 99) + 0.1
    ke = tg - M("elu", 99) + 0.1
    if kc <= 0:
        label(d, 290, "2021 : LA FINALE", k, 100, WHITE)
        if k50 > 0:
            n = min(50, int(50 * eout(k50 / 0.9)))
            text(d, (W / 2, 560), str(n), int(260 * (1 + 0.1 * (1 - eout(k50 / 0.2)))), GOLD, BOLD, stroke=10, scol=BG)
            text(d, (W / 2, 730), "POINTS", 90, WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 830), "DANS LE MATCH DU TITRE", fit("DANS LE MATCH DU TITRE", 58, 980), ACC, BOLD, stroke=5, scol=BG)
            if k50 < 0.25: hit = 1 - k50 / 0.25
        ph = (k % 1.0)
        P(img, W / 2 - 60, FEET, 230, "shoot" if ph < 0.3 else run_pose(tg * 10)); shadow(d, W / 2 - 60, FEET, 230)
    elif ke <= 0:
        trophy(d, W / 2, 760, 1.4 * (1 + 0.2 * (1 - eout(kc / 0.25))), GOLD)
        text(d, (W / 2, 330), "CHAMPIONS", fit("CHAMPIONS", 150, 980), GOLD, BOLD, stroke=8, scol=BG)
        k5 = tg - M("cinquante2", 99) + 0.1
        if k5 > 0: hit = max(hit, stamp(img, "1re FOIS EN 50 ANS", (W / 2, 1080), 96, -4, k5, WHITE))
        confetti(d, kc)
        if kc < 0.3: hit = max(hit, 1 - kc / 0.3); flash = 0.3 * (1 - kc / 0.3)
        P(img, W / 2, FEET, 220, "up"); shadow(d, W / 2, FEET, 220)
    else:
        star(d, W / 2, 640, 170 * (1 + 0.3 * (1 - eout(ke / 0.2))), GOLD)
        hit = max(hit, stamp(img, "MEILLEUR JOUEUR", (W / 2, 900), 110, -4, ke, GOLD))
        text(d, (W / 2, 1060), "DE LA FINALE", fit("DE LA FINALE", 100, 980), WHITE, BOLD, stroke=6, scol=BG)
        confetti(d, ke + 2)
        if ke < 0.3: hit = max(hit, 1 - ke / 0.3); flash = 0.25 * (1 - ke / 0.3)
        P(img, W / 2, FEET, 220, "fist"); shadow(d, W / 2, FEET, 220)
    return dict(hit=hit, flash=flash, bg=0.8)

def s_regard(img, d, tg, k):
    hit = 0.0
    kc = tg - M("champion", 99) + 0.1
    text(d, (W / 2, 290), "LE GAMIN QUI VENDAIT", fit("LE GAMIN QUI VENDAIT", 80, 980), GREY if kc > 0 else WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 390), "DES LUNETTES DANS LA RUE…", fit("DES LUNETTES DANS LA RUE…", 62, 980), GREY if kc > 0 else WHITE, BOLD, stroke=5, scol=BG)
    u = eout(max(0, kc) / 0.5)
    if kc <= 0: glasses(d, W / 2, 800, 2.0)
    else:
        glasses(d, lerp(W / 2, 220, u), lerp(800, 1180, u), lerp(2.0, 0.9, u))
        trophy(d, W / 2 + 120 * u, 900, 0.9 * (0.3 + 0.7 * u), GOLD)
        text(d, (W / 2, 560), "EST DEVENU", int(fit("EST DEVENU", 100, 980) * (1 + 0.3 * (1 - eout(kc / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
        hit = stamp(img, "CHAMPION", (W / 2, 1300), 170, -5, kc, GOLD)
    P(img, 880, FEET + 120, 200, "up" if kc > 0 else "stand"); shadow(d, 880, FEET + 120, 200)
    return dict(hit=hit, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ACC, BOLD, stroke=6, scol=BG)
    rows = [("6", "dans 2 chambres"), ("1 PAIRE", "pour 2 frères"), ("6,8 PTS", "1re saison"), ("CHAMPION", "50 points en finale")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 90 - 80 * (1 - eout(kk / 0.2))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD if i == 3 else ACC)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 45, y), a, 42, GOLD if i == 3 else WHITE, MONO, "lm"); text(d, (x + 420, y), b, 40, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "AVEC RIEN ?", (W / 2, 1180), 150, -5, kn + 0.05, RED) if kn > -0.05 else 0.0
    return dict(hit=hit, bg=0.2)

def series_banner(d, tg):
    """titre de la série (2–3 premières secondes) : « ILS ONT FAILLI ABANDONNER — ÉPISODE 1 »"""
    if tg > 3.2: return
    a = min(1, tg / 0.15) * (1 - ease((tg - 2.8) / 0.4))
    c = mix(BG, WHITE, a); g = mix(BG, GOLD, a)
    d.rounded_rectangle((90, 70, W - 90, 200), 22, fill=mix(BG, (40, 20, 70), a), outline=g, width=4)
    text(d, (W / 2, 115), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), c, BOLD)
    text(d, (W / 2, 168), "ÉPISODE 1", 40, g, MONO)

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
        text(d, (W / 2, 660), "DEMAIN · ÉPISODE 2", fit("DEMAIN · ÉPISODE 2", 74, 980), GOLD, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 770), typew("LE JOUEUR QUE LES GRANDS CLUBS", kd, 34), fit("LE JOUEUR QUE LES GRANDS CLUBS", 58, 980), WHITE, BOLD, stroke=5, scol=BG)
        text(d, (W / 2, 850), typew("TROUVAIENT…", kd - 0.8, 30), 58, WHITE, BOLD, stroke=5, scol=BG)
    kp = tg - M("petit2", 99) + 0.1
    if kp > 0:
        hit = max(hit, stamp(img, "TROP PETIT ?", (W / 2, 1020), 170, -6, kp, ACC))
        # silhouette mystère + toise
        x = W / 2
        for i in range(9): d.line((x + 170, 1560 - i * 50, x + 200, 1560 - i * 50), fill=GREY, width=4)
        d.line((x + 200, 1560, x + 200, 1150), fill=GREY, width=6)
    P(img, W / 2 - 40, 1560, 220, "stand", jersey=(40, 44, 60), shorts=(30, 34, 46), glow=0.8, alpha=0.9); shadow(d, W / 2 - 40, 1560, 220)
    text(d, (W / 2 - 40, 1290), "?", 120, GOLD, BOLD, stroke=6, scol=BG)
    return dict(hit=hit, bg=0.0)

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
        text(d, (x, yy), s, 56, mix(BG, (90, 80, 140), a), BOLD)
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (60, 40, 100), a), BOLD)
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

DUSTAMT = {"hook": 0.6, "athenes": 0.6, "rue": 0.6, "baskets": 0.4, "salle": 0.5, "draft": 0.5, "pivot": 0.8, "progres": 1.0, "finale": 1.0,
           "regard": 1.0, "you": 0.5, "abonne": 0.4, "question": 0.4, "logo": 0.2}
def _wrap(name, f):
    def g(img, d, tg, k):
        dust(d, tg, DUSTAMT.get(name, 0.5)); return f(img, d, tg, k)
    return g
SCENES = {n: _wrap(n, f) for n, f in {"hook": s_hook, "athenes": s_athenes, "rue": s_rue, "baskets": s_baskets, "salle": s_salle, "draft": s_draft,
          "pivot": s_pivot, "progres": s_progres, "finale": s_finale, "regard": s_regard, "you": s_you, "abonne": s_abonne, "question": s_question, "logo": s_logo}.items()}
BGLEVEL = {"hook": 0.0, "athenes": 0.05, "rue": 0.08, "baskets": 0.1, "salle": 0.0, "draft": 0.1, "pivot": 0.0, "progres": 0.55, "finale": 0.8,
           "regard": 1.0, "you": 0.2, "abonne": 0.0, "question": 0.0, "logo": 0.0}
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

# -*- coding: utf-8 -*-
"""Style « essai » (12/11/2026, Antoine Semenyo — épisode 9) : parking de centre d entraînement sous la pluie, voiture du père, rue de briques,
campagne dans la brume, route des prêts, stades génériques + moteur 3D (render_3d.py). Aucun nom de club, logo, écusson, drapeau ni trophée réel à l écran.
Usage : python3 render_essai.py timing_voix.json video_brut.mp4 [t_from t_to every]"""

JT = {}
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

def player(img, x, y, s, pose, rot=0.0, alpha=1.0, num="", jersey=(20, 170, 110), glow=1.0, shorts=None, sock=None, facing=1, legs=None, sleeves=None, beanie=None, **kw):
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
        k, f = lg; sk = (mix(legs, (0, 0, 0), 0.3) if back else legs) if legs else (SKIN_D if back else SKIN)
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
        e, h = am; sk0 = SKIN_D if back else SKIN; sk = (mix(sleeves, (0, 0, 0), 0.3) if back else sleeves) if sleeves else sk0
        _tap(d, root, e, 0.095 * S, 0.075 * S, sk)
        _tap(d, e, h, 0.075 * S, 0.06 * S, sk)
        gc = globals().get('GLOVE'); gr = 0.065 if gc else 0.045
        d.ellipse((h[0] - gr * S, h[1] - gr * S, h[0] + gr * S, h[1] + gr * S), fill=gc or sk0)
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
    if beanie:
        d.ellipse((head[0] - rx, head[1] - ry, head[0] + rx, head[1] + ry), fill=SKIN)
        hc = (head[0] + td[0] * ry * 0.42, head[1] + td[1] * ry * 0.42)
        d.pieslice((hc[0] - rx * 1.2, hc[1] - ry * 0.95, hc[0] + rx * 1.2, hc[1] + ry * 0.95), 180 + pose["t"], 360 + pose["t"], fill=beanie)
        _tap(d, (hc[0] - perp[0] * rx * 1.14, hc[1] - perp[1] * rx * 1.14), (hc[0] + perp[0] * rx * 1.14, hc[1] + perp[1] * rx * 1.14), 0.05 * S, 0.05 * S, mix(beanie, (255, 255, 255), 0.6))
        pc = (head[0] + td[0] * ry * 1.42, head[1] + td[1] * ry * 1.42)
        d.ellipse((pc[0] - 0.042 * S, pc[1] - 0.042 * S, pc[0] + 0.042 * S, pc[1] + 0.042 * S), fill=(250, 250, 250))
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
    JT.clear(); JT.update({kk: (x - ox + p[0] / SS, y - oy - 0.73 * s + drop + p[1] / SS) for kk, p in (("head", head), ("lh", la[1]), ("rh", ra[1]), ("le", la[0]), ("ls", shL), ("hip", hip))})
    img.alpha_composite(L, (int(x - ox), int(y - oy - 0.73 * s + drop)))









# =============================================================== style « cage » (11/11/2026, Nicolas Pépé — épisode 8, moteur 3D)
# Terrain synthétique de quartier à Paris sous un MÉTRO AÉRIEN générique (viaduc en fer, rame claire sans logo), immeubles en pierre
# avec balcons, toits en zinc ; crépuscule / nuit / aube dorée. Héros « athlète » : d'abord GARDIEN (maillot citron, gants) dans la cage,
# plonge, retire ses gants, sort de la cage et sprinte en profondeur. Stades génériques (amateur, nuit, grand stade, Afrique au couchant).
# Aucun nom de club, logo, écusson, drapeau, monument ni trophée réel à l'écran.
BG = (10, 12, 28)
ORANGE = (255, 150, 30); ACC = ORANGE; ICE = (176, 212, 255); AMBER = (255, 200, 110)
HOR = 880; FEET = 1440
JER = (40, 110, 230); NAVY = (236, 238, 244); GKJ = (206, 232, 54); GLOVE = None
SNOW_SH = (36, 92, 52)
GSH = (34, 92, 48)
GZ = 2.2; GOALY = HOR + (FEET - HOR) / GZ    # profondeur de la cage du quartier

POSES["shy"] = dict(t=-14, la=(-6, 18), ra=(6, -18), ll=(-4, 0), rl=(4, 0))
POSES["sad"] = dict(t=-26, la=(-14, 30), ra=(14, -30), ll=(-6, 4), rl=(6, -4))
POSES["wide"] = dict(t=0, la=(-100, -10), ra=(100, 10), ll=(-20, 6), rl=(20, -6))
POSES["point"] = dict(t=4, la=(-150, -10), ra=(30, -40), ll=(-12, 4), rl=(12, -4))
POSES["fist"] = dict(t=-4, la=(-172, -6), ra=(25, -70), ll=(-14, 4), rl=(14, -4))
POSES["shout"] = dict(t=9, la=(-118, -22), ra=(118, 22), ll=(-24, 6), rl=(24, -6))
POSES["ready"] = dict(t=14, la=(-62, 34), ra=(62, -34), ll=(-22, 16), rl=(22, -16))
POSES["glovesoff"] = dict(t=6, la=(-40, 110), ra=(40, -110), ll=(-6, 0), rl=(6, 0))
POSES["sprint"] = dict(t=22, la=(-60, 80), ra=(60, -80), ll=(-50, 70), rl=(45, -10))

def P(img, x, y, s, pose, winter=False, gk=False, **kw):
    global GLOVE
    kw.setdefault("num", "")
    if gk:
        kw.setdefault("jersey", GKJ); kw.setdefault("shorts", (30, 34, 44)); kw.setdefault("sock", GKJ); kw.setdefault("sleeves", GKJ)
        GLOVE = (246, 246, 246)
    else:
        kw.setdefault("jersey", JER); kw.setdefault("shorts", NAVY); kw.setdefault("sock", JER)
    try:
        player(img, x, y, s * 1.25, pose, **kw)
    finally:
        GLOVE = None

def shadow(d, x, y, s, col=GSH):
    s = s * 1.25; d.ellipse((x - 0.36 * s, y - 0.05 * s, x + 0.36 * s, y + 0.06 * s), fill=col)

def pop(k, base, amp=0.3, dur=0.2): return int(base * (1 + amp * (1 - eout(max(0, k) / dur))))
def kM(tg, name): return tg - M(name, 99) + 0.1

def TX(d, y, s, size, col, k=None, amp=0.14, maxw=940, stroke=7, x=None):
    sz = fit(s, size, maxw)
    if k is not None:
        if k <= 0: return
        sz = pop(k, sz, amp)
    text(d, (W / 2 if x is None else x, y), s, sz, col, BOLD, stroke=stroke, scol=BG)

def _grad(d, y0, y1, c0, c1, p=1.0):
    for y in range(y0, y1):
        d.line((0, y, W, y), fill=mix(c0, c1, ((y - y0) / max(1, y1 - y0 - 1)) ** p))

def proj(xw, z): return (W / 2 + (xw - W / 2) / z, HOR + (FEET - HOR) / z)

def goal(d, cx, by, s=1.0, col=(246, 246, 246)):
    w, h = 820 * s, 330 * s
    for i in range(0, 15):
        x = cx - w / 2 + i * w / 14; d.line((x, by - h, x + (x - cx) * 0.08, by - 20 * s), fill=(200, 206, 214), width=2)
    for j in range(0, 8):
        y = by - h + j * h / 7; d.line((cx - w / 2, y, cx + w / 2, y), fill=(200, 206, 214), width=2)
    t = max(6, int(14 * s))
    d.line((cx - w / 2, by, cx - w / 2, by - h, cx + w / 2, by - h, cx + w / 2, by), fill=col, width=t)

PPAL = {
    "dusk":  dict(sky0=(44, 38, 96), sky1=(255, 142, 96), roof=(66, 62, 96), stone=(196, 164, 150), win=(255, 196, 110), lit=0.55,
                  iron=(36, 32, 52), t0=(52, 128, 66), t1=(28, 86, 46), light=0.0),
    "night": dict(sky0=(6, 10, 28), sky1=(34, 46, 92), roof=(22, 28, 52), stone=(84, 88, 118), win=(255, 206, 120), lit=0.75,
                  iron=(16, 18, 30), t0=(30, 92, 52), t1=(14, 54, 32), light=0.0),
    "gold":  dict(sky0=(70, 84, 168), sky1=(255, 206, 126), roof=(128, 106, 128), stone=(236, 206, 170), win=(255, 226, 170), lit=0.3,
                  iron=(70, 54, 64), t0=(92, 166, 70), t1=(44, 110, 50), light=1.0),
}

def make_paris(mode, pitch=True):
    p = PPAL[mode]
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR + 1, p["sky0"], p["sky1"], 1.25)
    rng = np.random.default_rng(42)
    if mode == "night":
        for _ in range(70):
            x, y, r = rng.uniform(0, W), rng.uniform(0, 420), rng.uniform(1, 2.6); d.ellipse((x - r, y - r, x + r, y + r), fill=(220, 226, 255))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    if mode != "night":
        cy = 560 if mode == "dusk" else 600
        dl.ellipse((W / 2 - 260, cy - 260, W / 2 + 260, cy + 260), fill=(255, 214, 150, 150))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(60))); d = ImageDraw.Draw(img)
        d.ellipse((W / 2 - 80, cy - 80, W / 2 + 80, cy + 80), fill=(255, 226, 170) if mode == "gold" else (255, 190, 120))
    # toits lointains en zinc (mansardes, cheminées)
    x = -20
    while x < W:
        w = rng.uniform(90, 170); top = rng.uniform(560, 650)
        d.polygon([(x, 760), (x, top + 20), (x + 14, top), (x + w - 14, top), (x + w, top + 20), (x + w, 760)], fill=p["roof"])
        for cx in np.arange(x + 16, x + w - 20, 34):
            d.rectangle((cx, top - 22, cx + 12, top), fill=mix(p["roof"], (0, 0, 0), 0.25))
            if rng.random() < p["lit"]: d.rectangle((cx - 2, top + 26, cx + 12, top + 40), fill=p["win"])
        x += w + rng.uniform(-6, 10)
    # immeubles en pierre (gauche et droite) : balcons filants, fenêtres, toit en zinc
    for (x0, x1, top) in ((-30, 250, 150), (830, 1110, 190)):
        stone = p["stone"]
        d.rectangle((x0, top, x1, HOR + 30), fill=stone)
        d.polygon([(x0 - 10, top), (x0 + 20, top - 90), (x1 - 20, top - 90), (x1 + 10, top)], fill=p["roof"])
        for fx in np.arange(x0 + 40, x1 - 40, 70):
            d.rectangle((fx, top - 70, fx + 30, top - 20), fill=mix(p["roof"], (255, 255, 255), 0.15))
        for row, fy in enumerate(range(top + 40, HOR - 40, 120)):
            for fx in np.arange(x0 + 30, x1 - 40, 70):
                on = rng.random() < p["lit"]
                d.rectangle((fx, fy, fx + 38, fy + 74), fill=p["win"] if on else mix(stone, (20, 24, 40), 0.6))
                d.line((fx + 19, fy, fx + 19, fy + 74), fill=mix(stone, (0, 0, 0), 0.3), width=2)
            if row in (1, 4):   # balcon filant en fer
                by = fy + 78
                d.rectangle((x0, by, x1, by + 6), fill=mix(stone, (0, 0, 0), 0.35))
                d.line((x0, by - 26, x1, by - 26), fill=(20, 20, 26), width=4)
                for bx in range(int(x0), int(x1), 12): d.line((bx, by - 26, bx, by), fill=(20, 20, 26), width=2)
            d.line((x0, fy + 98, x1, fy + 98), fill=mix(stone, (255, 255, 255), 0.18), width=3)
    # viaduc du métro aérien (fer riveté, piliers, arches)
    iron = p["iron"]
    d.rectangle((0, 640, W, 684), fill=iron); d.line((0, 640, W, 640), fill=mix(iron, (255, 255, 255), 0.25), width=4)
    for rx in range(0, W, 26): d.ellipse((rx + 8, 658, rx + 14, 664), fill=mix(iron, (255, 255, 255), 0.2))
    for px in range(60, W + 1, 320):
        d.rectangle((px - 18, 684, px + 18, HOR - 6), fill=iron)
        d.rectangle((px - 28, HOR - 26, px + 28, HOR - 6), fill=mix(iron, (0, 0, 0), 0.2))
    for px in range(60, W - 1, 320):
        d.arc((px + 18, 650, px + 302, 860), 180, 360, fill=iron, width=14)
    # grillage haut derrière le terrain
    if pitch:
        for x in range(-10, W + 10, 22): d.line((x, 742, x + 10, HOR), fill=mix(iron, (180, 190, 200), 0.35), width=1)
        for y in range(742, HOR, 22): d.line((0, y, W, y), fill=mix(iron, (180, 190, 200), 0.3), width=1)
        for x in range(0, W + 1, 180): d.rectangle((x - 5, 730, x + 5, HOR), fill=mix(iron, (200, 200, 210), 0.4))
        # pelouse synthétique en bandes + lignes en perspective
        y = HOR; bh = 36.0; j = 0
        while y < H:
            u = (y - HOR) / (H - HOR); c = mix(p["t0"], p["t1"], u)
            d.rectangle((0, y, W, y + bh + 1), fill=mix(c, (0, 0, 0), 0.08 * (j % 2))); y += bh; bh *= 1.2; j += 1
        LC = (236, 242, 236)
        d.line((0, GOALY, W, GOALY), fill=LC, width=4)
        a, b, c_, e = proj(W / 2 - 520, GZ), proj(W / 2 + 520, GZ), proj(W / 2 + 520, 1.65), proj(W / 2 - 520, 1.65)
        d.line((a, e, c_, b), fill=LC, width=5)
        a, b, c_, e = proj(W / 2 - 1250, GZ), proj(W / 2 + 1250, GZ), proj(W / 2 + 1250, 1.12), proj(W / 2 - 1250, 1.12)
        d.line((a, e, c_, b), fill=LC, width=7)
        sp = proj(W / 2, 1.32); d.ellipse((sp[0] - 12, sp[1] - 6, sp[0] + 12, sp[1] + 6), fill=LC)
        goal(d, W / 2, GOALY, 0.95)
    else:
        # trottoir pavé + chaussée
        _grad(d, HOR, H, mix(p["roof"], (120, 120, 130), 0.4), mix(p["roof"], (40, 40, 50), 0.3), 0.9)
        for zz in np.arange(1.0, 4.0, 0.12):
            yy = HOR + (FEET - HOR) / zz; d.line((0, yy, W, yy), fill=mix(p["roof"], (0, 0, 0), 0.25), width=2)
        for xw in range(-2400, 3600, 110):
            d.line((proj(xw, 4.0), proj(xw, 0.55)), fill=mix(p["roof"], (0, 0, 0), 0.25), width=2)
        d.line((0, HOR + 8, W, HOR + 8), fill=mix(p["stone"], (255, 255, 255), 0.2), width=10)
        for lx in (330, 760):   # réverbères
            d.rectangle((lx - 6, 470, lx + 6, HOR), fill=(20, 22, 30)); d.polygon([(lx - 26, 470), (lx + 26, 470), (lx + 16, 430), (lx - 16, 430)], fill=(20, 22, 30))
            d.rectangle((lx - 18, 436, lx + 18, 466), fill=(255, 214, 140))
    return img

def make_stadium(mode):
    """stade générique : tribune à points de couleur, toit, pylônes ; aucun logo, aucune inscription"""
    pal = {"amat": ((96, 104, 120), (170, 176, 188), (70, 128, 70), (40, 92, 50), 0.6, 0.18, 690),
           "fr":   ((14, 22, 52), (52, 70, 130), (40, 120, 64), (22, 76, 42), 0.85, 0.85, 470),
           "eng":  ((10, 14, 34), (40, 52, 104), (44, 132, 70), (24, 84, 46), 1.0, 1.0, 400),
           "afr":  ((44, 30, 84), (255, 150, 70), (70, 140, 66), (30, 80, 44), 0.8, 1.0, 470)}[mode]
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, 640, pal[0], pal[1], 1.2)
    rng = np.random.default_rng(33)
    if mode == "afr":
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((300, 180, 780, 660), fill=(255, 190, 110, 150)); img.alpha_composite(L.filter(ImageFilter.GaussianBlur(50))); d = ImageDraw.Draw(img)
        d.ellipse((430, 300, 650, 520), fill=(255, 214, 140))
        for px, ph in ((60, 300), (200, 240), (900, 280), (1030, 330)):
            top = (px + 16, 500 - ph)
            d.line((px, 520, px + 8, 500 - ph * 0.5, top[0], top[1]), fill=(26, 16, 34), width=12)
            for a in range(-160, -10, 25):
                ex, ey = top[0] + 110 * math.cos(math.radians(a)), top[1] + 70 * math.sin(math.radians(a)) + 50
                d.line((top[0], top[1], (top[0] + ex) / 2, min(top[1], ey) - 26, ex, ey), fill=(26, 16, 34), width=9, joint="curve")
    T0 = pal[6]
    top = lambda x: T0 + 46 * ((x - W / 2) / (W / 2)) ** 2
    d.polygon([(0, 930)] + [(x, top(x)) for x in range(0, W + 1, 30)] + [(W, 930)], fill=(34, 36, 52))
    cols = [(236, 232, 224), (214, 170, 120), (90, 130, 200), (240, 200, 90), (120, 120, 136), (70, 160, 150), (180, 110, 170), (150, 190, 120)]
    for y in range(int(T0) + 50, 900, 15):
        for x in range(6, W, 13):
            if y < top(x) + 46 or rng.random() > pal[5]: continue
            c = cols[int(rng.integers(0, len(cols)))]
            c = mix((34, 36, 52), c, pal[4] * rng.uniform(0.45, 0.95))
            xx_ = x + rng.uniform(-3, 3); d.ellipse((xx_ - 4.5, y - 5, xx_ + 4.5, y + 5), fill=c)
    d.polygon([(x, top(x) - 34) for x in range(0, W + 1, 30)] + [(x, top(x) + 30) for x in range(W, -1, -30)], fill=(52, 56, 76))
    d.line([(x, top(x) + 30) for x in range(0, W + 1, 30)], fill=(150, 156, 176), width=5)
    for px in (96, W - 96):
        d.rectangle((px - 9, 150, px + 9, T0 + 50), fill=(60, 64, 80))
        d.rounded_rectangle((px - 80, 96, px + 80, 196), 10, fill=(44, 48, 62))
        for i in range(5):
            for j in range(3):
                d.ellipse((px - 68 + i * 30, 106 + j * 30, px - 46 + i * 30, 128 + j * 30), fill=(255, 250, 220) if mode != "amat" else (210, 214, 222))
    if mode != "amat":
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        for px in (96, W - 96): dl.ellipse((px - 170, 20, px + 170, 280), fill=(255, 244, 200, 130 if mode in ("afr", "eng") else 90))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(40))); d = ImageDraw.Draw(img)
    for i, x in enumerate(range(0, W, 180)):
        d.rectangle((x, 900, x + 176, 946), fill=[(40, 44, 66), (58, 50, 74), (36, 56, 70)][i % 3])
    y = 946; bh = 34.0; j = 0
    while y < H:
        u = (y - 946) / (H - 946); c = mix(pal[2], pal[3], u)
        d.rectangle((0, y, W, y + bh + 1), fill=mix(c, (0, 0, 0), 0.08 * (j % 2))); y += bh; bh *= 1.2; j += 1
    d.line((0, 1010, W, 1010), fill=(236, 242, 236), width=6)
    return img

PARIS_DUSK = make_paris("dusk"); PARIS_NIGHT = make_paris("night"); PARIS_GOLD = make_paris("gold"); STREET = make_paris("night", pitch=False)
STAD_AMAT = make_stadium("amat"); STAD_FR = make_stadium("fr"); STAD_ENG = make_stadium("eng"); STAD_AFR = make_stadium("afr")
NIGHT_ARR = np.asarray(PARIS_NIGHT.convert("RGB")).astype(np.float32); GOLD_ARR = np.asarray(PARIS_GOLD.convert("RGB")).astype(np.float32)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

def reveal(A, B, c, r, soft=70, edge=0.9):
    if r <= 0: return Image.fromarray(A.astype(np.uint8)).convert("RGBA")
    dist = np.hypot(XX - c[0], YY - c[1])
    m = np.clip((r - dist) / soft, 0, 1)[..., None]
    out = A * (1 - m) + B * m
    if edge > 0: out = out + (np.clip(1 - np.abs(dist - r) / 46, 0, 1) * 255 * edge)[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")

_t = Image.new("L", (1, H), 0)
for _y in range(820): _t.putpixel((0, _y), int(120 * (1 - _y / 820) ** 1.2))
TOPSH = Image.new("RGBA", (W, H), BG + (0,)); TOPSH.putalpha(_t.resize((W, H)))
def topsh(img, a=1.0):
    if a >= 1: img.alpha_composite(TOPSH)
    else:
        L = TOPSH.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * a))); img.alpha_composite(L)

RAYS = Image.new("RGBA", (W, H), (0, 0, 0, 0)); _dr = ImageDraw.Draw(RAYS)
for _i in range(9):
    _a = math.radians(70 + _i * 5 + _i * 4); _b = _a + math.radians(4)
    _dr.polygon([(W / 2, 600), (W / 2 + 2400 * math.cos(_a), 600 + 2400 * math.sin(_a)), (W / 2 + 2400 * math.cos(_b), 600 + 2400 * math.sin(_b))], fill=(255, 236, 180, 44))
RAYS = RAYS.filter(ImageFilter.GaussianBlur(12)); EMPTY = Image.new("RGBA", (W, H), (0, 0, 0, 0))
def rays(img, a):
    if a > 0: img.alpha_composite(Image.blend(EMPTY, RAYS, min(1, a)))

def dim(img, a, col=BG):
    if a > 0: img.alpha_composite(Image.new("RGBA", (W, H), col + (int(255 * min(1, a)),)))

def rings(img, c, kk, n=5, col=GOLD, span=900, w=14, gap=0.16, rate=1.3):
    if kk <= 0: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for i in range(n):
        kr = kk * rate - i * gap
        if 0 < kr < 1:
            r = 70 + kr * span
            dl.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), outline=col + (int(255 * (1 - kr) ** 1.2),), width=w)
    img.alpha_composite(L)

def train(d, tg, speed=520, period=5.5, ofs=0.0, mode="dusk"):
    """rame de métro générique (aucun logo) qui passe sur le viaduc"""
    ph = ((tg + ofs) % period) / period
    x0 = lerp(W + 60, -1500, ph)
    body = (214, 222, 216) if mode != "night" else (150, 160, 170)
    for c in range(4):
        cx = x0 + c * 360
        if cx > W + 20 or cx + 350 < -20: continue
        d.rounded_rectangle((cx, 570, cx + 350, 640), 14, fill=body)
        d.rectangle((cx, 612, cx + 350, 622), fill=(70, 110, 150))
        for wx in range(int(cx + 24), int(cx + 330), 52):
            d.rectangle((wx, 584, wx + 34, 606), fill=(255, 226, 150) if mode != "gold" else (240, 236, 210))
        d.rectangle((cx + 160, 580, cx + 190, 636), fill=mix(body, (0, 0, 0), 0.25))

def rain(d, tg, amt=1.0):
    rr = np.random.default_rng(9)
    for i in range(int(150 * amt)):
        x0, y0, z = rr.uniform(0, W), rr.uniform(0, H), rr.uniform(0.4, 1)
        y = (y0 + tg * 1600 * z) % H; x = (x0 - tg * 200 * z) % W
        d.line((x, y, x - 8 * z, y + 34 * z), fill=(190, 200, 220), width=2)

def glove_sprite(s, rot):
    w = int(0.3 * s); L = Image.new("RGBA", (w * 2, w * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((w * 0.55, w * 0.5, w * 1.45, w * 1.6), int(w * 0.3), fill=(246, 246, 246), outline=(140, 150, 160), width=max(2, w // 12))
    d.rounded_rectangle((w * 0.3, w * 0.95, w * 0.62, w * 1.35), int(w * 0.14), fill=(246, 246, 246), outline=(140, 150, 160), width=max(2, w // 14))
    d.rectangle((w * 0.55, w * 1.42, w * 1.45, w * 1.6), fill=GKJ)
    return L.rotate(rot, resample=Image.BICUBIC)

def band_on_arm(d, s, k=1.0): return
def trophy(d, cx, cy, s=1.0, col=GOLD):
    """coupe générique à deux anses (ne reproduit aucun trophée réel)"""
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.arc((cx - 190 * s, cy - 230 * s, cx - 70 * s, cy - 90 * s), 90, 270, fill=mix(col, (0, 0, 0), 0.2), width=max(3, int(14 * s)))
    d.arc((cx + 70 * s, cy - 230 * s, cx + 190 * s, cy - 90 * s), 270, 90, fill=mix(col, (0, 0, 0), 0.2), width=max(3, int(14 * s)))
    d.polygon([q(-120, -230), q(120, -230), q(80, -60), q(25, -20), q(25, 50), q(80, 90), q(-80, 90), q(-25, 50), q(-25, -20), q(-80, -60)], fill=col)
    d.polygon([q(-120, -230), q(-60, -230), q(-40, -60), q(-80, -60)], fill=mix(col, (255, 255, 255), 0.45))

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-500, 0), i % 3) for i in range(80)]
def confetti(d, kv, amt=1.0):
    for x0, y0, c in CONF[:int(len(CONF) * amt)]:
        y = y0 + kv * 620; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < 1480: d.rectangle((x, y, x + 14, y + 24), fill=[ORANGE, WHITE, GOLD][c])

def crowd(d, tg, n=14, up_all=False, rise=1.0):
    for i in range(n):
        x = 40 + i * (W - 80) / (n - 1); h = (200 + 50 * ((i * 37) % 5) / 4) * rise
        up = up_all or math.sin(tg * 5 + i) > 0
        c = (18, 16, 30); y0 = H - 40
        d.rounded_rectangle((x - 34, y0 - h, x + 34, y0 + 40), 26, fill=c); d.ellipse((x - 26, y0 - h - 58, x + 26, y0 - h - 6), fill=c)
        if up:
            d.line((x + 24, y0 - h + 20, x + 50 + 10 * math.sin(tg * 6 + i), y0 - h - 110), fill=c, width=16)
            d.line((x - 24, y0 - h + 20, x - 50 - 10 * math.sin(tg * 6 + i + 1), y0 - h - 110), fill=c, width=16)

def series_banner(d, tg):
    if tg > 3.6 or tg < 0.5: return
    e = eout((tg - 0.5) / 0.25); o = ease((tg - 3.25) / 0.35)
    y = -150 + 220 * e - 260 * o
    d.rounded_rectangle((90, y, W - 90, y + 130), 22, fill=(96, 24, 40), outline=GOLD, width=5)
    text(d, (W / 2, y + 45), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), WHITE, BOLD)
    text(d, (W / 2, y + 98), "ÉPISODE 8", 40, GOLD, MONO)

def burst(d, x, y, k, n=16, r=160, col=ORANGE, seed=0, w=7):
    if k <= 0 or k > 0.7: return
    rng = np.random.default_rng(seed); e = eout(k / 0.5); a = 1 - k / 0.7
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        r0, r1 = r * (0.3 + 0.5 * (1 - a)) * e, r * (0.6 + 0.6 * rng.random()) * e
        if r1 > r0: d.line((x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r1 * math.cos(ang), y + r1 * math.sin(ang)), fill=col, width=max(2, int(w * a)))

def paper(img, cx, cy, ks):
    L = Image.new("RGBA", (300, 380), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((10, 10, 290, 370), 10, fill=(250, 248, 240, 255), outline=(120, 110, 96, 255), width=4)
    d.rectangle((40, 40, 200, 62), fill=(60, 66, 90, 255))
    for i in range(6): d.rectangle((40, 96 + i * 30, 260 - (i % 3) * 30, 106 + i * 30), fill=(176, 176, 184, 255))
    pts = [(60 + i * 5, 320 - 26 * math.sin(i * 0.55) * (1 - i / 60) - i * 0.3) for i in range(int(40 * min(1, ks / 0.5)))]
    if len(pts) > 1: d.line(pts, fill=(30, 50, 150, 255), width=6, joint="curve")
    d.line((50, 340, 250, 340), fill=(120, 110, 96, 255), width=3)
    sc = 1 + 0.4 * (1 - eout(ks / 0.2))
    L = L.rotate(7, resample=Image.BICUBIC, expand=True)
    if sc != 1: L = L.resize((int(L.width * sc), int(L.height * sc)), Image.BICUBIC)
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def counter(d, y, v0, v1, k, dur, size, col, fmt="{}", suffix=""):
    if k <= 0: return
    v = int(lerp(v0, v1, eout(min(1, k / dur))))
    s = fmt.format(v) + suffix
    text(d, (W / 2, y), s, pop(k, fit(s, size, 980), 0.15), col, BOLD, stroke=9, scol=BG)

def clock(d, cx, cy, r, ang, col=WHITE):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(20, 24, 40), outline=col, width=max(4, int(r / 12)))
    for i in range(12):
        a = i * math.pi / 6; d.line((cx + 0.82 * r * math.sin(a), cy - 0.82 * r * math.cos(a), cx + 0.94 * r * math.sin(a), cy - 0.94 * r * math.cos(a)), fill=col, width=max(3, int(r / 18)))
    d.line((cx, cy, cx + 0.75 * r * math.sin(ang), cy - 0.75 * r * math.cos(ang)), fill=ORANGE, width=max(4, int(r / 10)))
    d.line((cx, cy, cx + 0.5 * r * math.sin(ang / 12), cy - 0.5 * r * math.cos(ang / 12)), fill=col, width=max(5, int(r / 8)))
    d.ellipse((cx - r * 0.08, cy - r * 0.08, cx + r * 0.08, cy + r * 0.08), fill=col)

def speed_lines(d, c, k, n=40, col=(255, 240, 200), seed=3):
    if k <= 0: return
    rng = np.random.default_rng(seed)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(260, 600); ln = rng.uniform(200, 600) * (0.6 + 0.4 * math.sin(k * 20 + i))
        d.line((c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a), c[0] + (r0 + ln) * math.cos(a), c[1] + (r0 + ln) * math.sin(a)), fill=col, width=int(rng.uniform(3, 8)))

def arrow_up(d, cx, cy, s, col=(40, 230, 130)):
    d.polygon([(cx, cy - 120 * s), (cx + 90 * s, cy), (cx + 38 * s, cy), (cx + 38 * s, cy + 110 * s), (cx - 38 * s, cy + 110 * s), (cx - 38 * s, cy), (cx - 90 * s, cy)], fill=col)

# jeunes en survêtement de centre de formation (génériques) loin devant
def others(img, tg, z0=3.2, run=True):
    for i, (dx, zz, c) in enumerate(((-260, 0.0, (150, 60, 70)), (40, 0.25, (60, 90, 160)), (300, -0.15, (80, 150, 120)), (-60, 0.55, (180, 140, 60)))):
        z = z0 + zz; x, y = proj(W / 2 + dx, z)
        dd = ImageDraw.Draw(img); _sh = 250 / z * 1.25; dd.ellipse((x - 0.36 * _sh, y - 0.05 * _sh, x + 0.36 * _sh, y + 0.06 * _sh), fill=GSH)
        player(img, x, y, 250 / z * 1.25, run_pose(tg * 8 + i * 1.7) if run else "stand", jersey=c, shorts=(30, 32, 40), sock=c, glow=0.5)


# =============================================================== style « essai » (12/11/2026, Antoine Semenyo — épisode 9, moteur 3D)
# PARKING d'un centre d'entraînement la nuit sous la pluie (grillage, portail, projecteurs, flaques, VOITURE du père), rue de maisons
# en briques mitoyennes (générique), campagne au petit matin dans la brume (collines, haies, petit terrain), route avec panneaux de
# divisions, stades génériques. Héros « athlète » maillot vert sans numéro ; sweat à capuche pendant l'année sans foot.
# Animations NOUVELLES : portails qui se ferment devant lui, assis dans la voiture tête basse (essuie-glaces, pluie sur la vitre),
# calendrier dont les pages s'envolent, crampons qui volent jusqu'à lui au cri, course en montée dans la brume, panneaux qui défilent.
# Aucun nom de club, logo, écusson, drapeau, monument ni trophée réel à l'écran.
JER = (46, 168, 92); NAVY = (240, 242, 246); HOOD = (92, 96, 112); JEANS = (44, 58, 92)
ACC = ORANGE; GKJ = (206, 232, 54)
WET = (20, 26, 40)
SNOW_SH = (14, 18, 28); GSH = (14, 18, 28)

def P(img, x, y, s, pose, winter=False, hood=False, **kw):
    kw.setdefault("num", "")
    if hood:
        kw.setdefault("jersey", HOOD); kw.setdefault("sleeves", HOOD); kw.setdefault("shorts", JEANS); kw.setdefault("legs", JEANS); kw.setdefault("sock", JEANS)
    else:
        kw.setdefault("jersey", JER); kw.setdefault("shorts", NAVY); kw.setdefault("sock", JER)
    player(img, x, y, s * 1.25, pose, **kw)

def shadow(d, x, y, s, col=GSH):
    s = s * 1.25; d.ellipse((x - 0.36 * s, y - 0.05 * s, x + 0.36 * s, y + 0.06 * s), fill=col)

CPAL = {
    "night": dict(sky0=(6, 8, 22), sky1=(30, 38, 70), tree=(10, 14, 22), asph=(34, 38, 52), asph2=(18, 20, 30), lamp=1.0, fence=(90, 100, 120), grass=(24, 70, 40)),
    "dusk":  dict(sky0=(40, 36, 90), sky1=(250, 140, 100), tree=(30, 22, 44), asph=(80, 72, 92), asph2=(40, 36, 52), lamp=0.5, fence=(120, 110, 130), grass=(50, 110, 60)),
    "gold":  dict(sky0=(80, 96, 180), sky1=(255, 210, 130), tree=(70, 60, 70), asph=(150, 130, 120), asph2=(90, 80, 84), lamp=0.0, fence=(170, 150, 140), grass=(90, 160, 70)),
}

def make_carpark(mode):
    p = CPAL[mode]
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR + 1, p["sky0"], p["sky1"], 1.3)
    rng = np.random.default_rng(7)
    if mode == "gold":
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((W / 2 - 280, 470, W / 2 + 280, 1030), fill=(255, 220, 150, 160)); img.alpha_composite(L.filter(ImageFilter.GaussianBlur(60))); d = ImageDraw.Draw(img)
        d.ellipse((W / 2 - 85, 665, W / 2 + 85, 835), fill=(255, 230, 170))
    # rangée d'arbres lointains
    for x in range(-40, W + 40, 46):
        h = rng.uniform(90, 170); d.ellipse((x - 50, 760 - h, x + 50, 790), fill=p["tree"])
    # terrain d'entraînement derrière le grillage + mâts de projecteurs
    d.rectangle((0, 780, W, HOR), fill=p["grass"])
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for px in (120, 540, 960):
        d.rectangle((px - 7, 330, px + 7, HOR), fill=(40, 44, 58))
        d.rounded_rectangle((px - 70, 290, px + 70, 350), 8, fill=(50, 54, 70))
        if p["lamp"] > 0:
            for i in range(4): d.ellipse((px - 60 + i * 32, 302, px - 36 + i * 32, 338), fill=(255, 250, 225))
            dl.ellipse((px - 220, 160, px + 220, 480), fill=(255, 244, 210, int(110 * p["lamp"])))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(45))); d = ImageDraw.Draw(img)
    # grillage haut (avec ouverture au centre pour le portail)
    fc = p["fence"]
    for x in range(-10, W + 10, 20):
        if 400 < x < 680: continue
        d.line((x, 600, x + 10, HOR), fill=mix(fc, p["sky1"], 0.3), width=1)
    for y in range(600, HOR, 20):
        d.line((0, y, 400, y), fill=mix(fc, p["sky1"], 0.3), width=1); d.line((680, y, W, y), fill=mix(fc, p["sky1"], 0.3), width=1)
    for x in (0, 200, 400, 680, 880, W):
        d.rectangle((x - 6, 590, x + 6, HOR), fill=fc)
    d.line((0, 600, 400, 600), fill=fc, width=5); d.line((680, 600, W, 600), fill=fc, width=5)
    # parking en perspective : asphalte, places, flaques
    _grad(d, HOR, H, p["asph"], p["asph2"], 0.8)
    for xw in range(-2600, 3800, 330):
        d.line((proj(xw, 3.2), proj(xw, 1.6)), fill=(220, 220, 210), width=3)
    d.line((proj(-2600, 1.6), proj(3800, 1.6)), fill=(220, 220, 210), width=4)
    if mode != "gold":
        for (xw, z, r) in ((-200, 1.3, 230), (900, 1.15, 190), (300, 2.4, 160), (1500, 2.0, 140)):
            cx, cy = proj(xw, z); rw = r / z * 1.6
            d.ellipse((cx - rw, cy - rw * 0.16, cx + rw, cy + rw * 0.16), fill=mix(p["asph"], (200, 210, 240), 0.35))
    return img

def gate(d, k_close, col=(150, 160, 180)):
    """portail à deux battants dans l'ouverture du grillage ; k_close 0 = ouvert, 1 = fermé"""
    c = ease(k_close)
    for side in (-1, 1):
        x0 = 540 + side * 140; x1 = lerp(x0, 540, c)
        a, b = min(x0, x1), max(x0, x1)
        if b - a < 4: d.line((x0, 600, x0, HOR), fill=col, width=8); continue
        d.rectangle((a, 610, b, HOR - 4), outline=col, width=8)
        for x in np.arange(a + 14, b, 18): d.line((x, 614, x, HOR - 8), fill=col, width=3)
        d.line((a, 745, b, 745), fill=col, width=5)

TPAL = {
    "dusk":  dict(sky0=(36, 40, 92), sky1=(236, 140, 110), brick=(140, 70, 54), brick2=(112, 56, 46), roof=(52, 46, 62), win=(255, 200, 120), lit=0.4, road=(60, 58, 72)),
    "night": dict(sky0=(6, 10, 26), sky1=(30, 40, 80), brick=(70, 40, 40), brick2=(54, 32, 34), roof=(20, 22, 34), win=(255, 206, 120), lit=0.7, road=(30, 32, 44)),
}
def make_terrace(mode):
    p = TPAL[mode]
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR + 1, p["sky0"], p["sky1"], 1.3)
    rng = np.random.default_rng(11)
    if mode == "night":
        for _ in range(60):
            x, y, r = rng.uniform(0, W), rng.uniform(0, 380), rng.uniform(1, 2.4); d.ellipse((x - r, y - r, x + r, y + r), fill=(220, 226, 255))
    # rangée de maisons mitoyennes en briques (génériques), fenêtres en saillie, cheminées
    x = -60
    while x < W + 60:
        w = 210; top = 470 + rng.uniform(-10, 10)
        br = p["brick"] if int(x / w) % 2 else p["brick2"]
        d.polygon([(x, top), (x + w / 2, top - 90), (x + w, top)], fill=p["roof"])
        d.rectangle((x + w * 0.7, top - 120, x + w * 0.7 + 26, top - 40), fill=mix(br, (0, 0, 0), 0.2))
        d.rectangle((x, top, x + w, HOR), fill=br)
        for by in range(int(top) + 8, HOR, 16):
            d.line((x, by, x + w, by), fill=mix(br, (0, 0, 0), 0.18), width=1)
        for fy in (top + 60, top + 230):
            on = rng.random() < p["lit"]
            d.rectangle((x + 30, fy, x + 110, fy + 110), fill=p["win"] if on else mix(br, (20, 24, 40), 0.65), outline=(230, 226, 220), width=5)
            d.line((x + 70, fy, x + 70, fy + 110), fill=(230, 226, 220), width=4)
        d.rectangle((x + 140, top + 250, x + 190, HOR - 4), fill=[(40, 60, 110), (120, 30, 40), (30, 80, 60)][int(x / w) % 3])
        d.rectangle((x + 140, top + 230, x + 190, top + 246), fill=(230, 226, 220))
        x += w
    d.rectangle((0, HOR - 40, W, HOR), fill=mix(p["brick2"], (0, 0, 0), 0.2))
    # trottoir + chaussée en perspective
    _grad(d, HOR, H, mix(p["road"], (150, 150, 160), 0.3), p["road"], 0.9)
    for zz in np.arange(1.0, 4.0, 0.15):
        yy = HOR + (FEET - HOR) / zz; d.line((0, yy, W, yy), fill=mix(p["road"], (0, 0, 0), 0.25), width=2)
    d.line((0, HOR + 30, W, HOR + 30), fill=mix(p["road"], (255, 255, 255), 0.35), width=8)
    for lx in (240, 840):
        d.rectangle((lx - 6, 420, lx + 6, HOR + 20), fill=(20, 22, 30)); d.polygon([(lx - 26, 420), (lx + 26, 420), (lx + 16, 384), (lx - 16, 384)], fill=(20, 22, 30))
        d.rectangle((lx - 18, 390, lx + 18, 416), fill=(255, 214, 140))
    return img

def make_country(mode):
    """campagne au petit matin : collines, haies, brume, petit terrain avec buts blancs"""
    gold = mode == "gold"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR + 1, (120, 150, 200) if gold else (150, 168, 190), (255, 214, 150) if gold else (226, 230, 232), 1.2)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.ellipse((W / 2 - 300, 420, W / 2 + 300, 1020), fill=(255, 226, 160, 170 if gold else 90)); img.alpha_composite(L.filter(ImageFilter.GaussianBlur(70))); d = ImageDraw.Draw(img)
    d.ellipse((W / 2 + 120, 610, W / 2 + 250, 740), fill=(255, 236, 190) if gold else (250, 246, 236))
    for i, (base, amp, col) in enumerate(((700, 70, (120, 150, 130)), (770, 60, (88, 130, 92)), (830, 50, (64, 116, 70)))):
        pts = [(x, base - amp * math.sin(x / 260 + i * 1.7) - 30 * math.sin(x / 90 + i)) for x in range(0, W + 1, 20)]
        c = mix(col, (255, 220, 160), 0.18) if gold else col
        d.polygon([(0, HOR + 10)] + pts + [(W, HOR + 10)], fill=c)
        for x, y in pts[::5]:
            d.ellipse((x - 16, y - 22, x + 16, y + 6), fill=mix(c, (0, 0, 0), 0.25))   # haies / arbres isolés
    # brume en bandes
    F_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); df = ImageDraw.Draw(F_)
    for y in (720, 800, 860):
        df.rectangle((0, y - 20, W, y + 20), fill=(255, 250, 240, 60 if gold else 110))
    img.alpha_composite(F_.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(img)
    y = HOR; bh = 36.0; j = 0
    t0, t1 = ((96, 170, 74), (46, 112, 50)) if gold else ((70, 132, 76), (36, 90, 48))
    while y < H:
        u = (y - HOR) / (H - HOR); c = mix(t0, t1, u)
        d.rectangle((0, y, W, y + bh + 1), fill=mix(c, (0, 0, 0), 0.07 * (j % 2))); y += bh; bh *= 1.2; j += 1
    LC = (236, 242, 236)
    gy = HOR + (FEET - HOR) / 3.0
    d.line((0, gy, W, gy), fill=LC, width=3)
    goal(d, W / 2, gy, 0.55)
    return img

def make_road():
    """route de campagne au crépuscule vers l'horizon (les panneaux sont dessinés dans la scène)"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR + 1, (40, 40, 96), (255, 150, 100), 1.3)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.ellipse((W / 2 - 260, 600, W / 2 + 260, 1100), fill=(255, 190, 120, 150)); img.alpha_composite(L.filter(ImageFilter.GaussianBlur(60))); d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - 70, HOR - 140, W / 2 + 70, HOR), fill=(255, 200, 130))
    for x in range(-40, W + 40, 60):
        h = 40 + 30 * math.sin(x * 0.05); d.ellipse((x - 40, HOR - h, x + 40, HOR + 10), fill=(40, 30, 50))
    _grad(d, HOR, H, (80, 70, 70), (40, 50, 40), 0.9)
    d.polygon([proj(W / 2 - 300, 40), proj(W / 2 + 300, 40), proj(W / 2 + 300, 0.55), proj(W / 2 - 300, 0.55)], fill=(52, 52, 64))
    for z in np.arange(0.8, 12, 0.9):
        a, b = proj(W / 2, z), proj(W / 2, z + 0.4); d.line((a, b), fill=(240, 230, 200), width=max(2, int(10 / z)))
    return img

CAR_NIGHT = make_carpark("night"); CAR_DUSK = make_carpark("dusk"); CAR_GOLD = make_carpark("gold")
TER_DUSK = make_terrace("dusk"); TER_NIGHT = make_terrace("night")
CTRY = make_country("fog"); CTRY_GOLD = make_country("gold"); ROAD = make_road()
STAD_AMAT = make_stadium("amat"); STAD_FR = make_stadium("fr"); STAD_ENG = make_stadium("eng")
NIGHT_ARR = np.asarray(CAR_NIGHT.convert("RGB")).astype(np.float32); GOLD_ARR = np.asarray(CTRY_GOLD.convert("RGB")).astype(np.float32)

def series_banner(d, tg):
    if tg > 3.6 or tg < 0.5: return
    e = eout((tg - 0.5) / 0.25); o = ease((tg - 3.25) / 0.35)
    y = -150 + 220 * e - 260 * o
    d.rounded_rectangle((90, y, W - 90, y + 130), 22, fill=(96, 24, 40), outline=GOLD, width=5)
    text(d, (W / 2, y + 45), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), WHITE, BOLD)
    text(d, (W / 2, y + 98), "ÉPISODE 9", 40, GOLD, MONO)

def bag(d, x, y, s, col=(30, 34, 46)):
    d.rounded_rectangle((x - 0.32 * s, y - 0.22 * s, x + 0.32 * s, y), int(0.08 * s), fill=col)
    d.arc((x - 0.18 * s, y - 0.36 * s, x + 0.18 * s, y - 0.12 * s), 180, 360, fill=col, width=max(3, int(0.04 * s)))
    d.line((x - 0.3 * s, y - 0.12 * s, x + 0.3 * s, y - 0.12 * s), fill=JER, width=max(2, int(0.03 * s)))

def boot(d, x, y, s, rot=0.0, col=(24, 24, 30)):
    """crampon (chaussure) générique, sans marque"""
    L = Image.new("RGBA", (int(s * 1.4), int(s * 0.9)), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    w, h = L.size
    dl.polygon([(w * 0.1, h * 0.25), (w * 0.45, h * 0.15), (w * 0.62, h * 0.45), (w * 0.95, h * 0.55), (w * 0.95, h * 0.72), (w * 0.1, h * 0.72)], fill=col + (255,))
    dl.line((w * 0.12, h * 0.62, w * 0.9, h * 0.62), fill=(240, 240, 240, 255), width=max(2, int(s * 0.05)))
    for i in range(5): dl.rectangle((w * (0.18 + i * 0.16), h * 0.72, w * (0.24 + i * 0.16), h * 0.86), fill=(200, 200, 205, 255))
    for i in range(3): dl.line((w * (0.3 + i * 0.08), h * 0.3, w * (0.36 + i * 0.08), h * 0.42), fill=(240, 240, 240, 255), width=max(2, int(s * 0.03)))
    L = L.rotate(rot, resample=Image.BICUBIC, expand=True)
    return L

def car(img, x, y, s, k, wipers=True, kid=True, head_down=1.0, rain_on=True, tg=0.0):
    """voiture générique vue de côté (berline sombre), enfant assis côté passager, tête basse ; pluie sur la vitre"""
    L = Image.new("RGBA", (int(4.4 * s), int(1.8 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    w, h = L.size; body = (40, 48, 70); hl = (90, 104, 140)
    d.rounded_rectangle((w * 0.02, h * 0.45, w * 0.98, h * 0.82), int(0.18 * s), fill=body)
    d.polygon([(w * 0.22, h * 0.47), (w * 0.34, h * 0.1), (w * 0.7, h * 0.1), (w * 0.84, h * 0.47)], fill=body)
    win = [(w * 0.26, h * 0.45), (w * 0.36, h * 0.16), (w * 0.68, h * 0.16), (w * 0.79, h * 0.45)]
    d.polygon(win, fill=(30, 40, 66))
    if kid:   # silhouette assise, tête basse (dessinée DANS la vitre)
        hx, hy = w * 0.58, h * (0.27 + 0.05 * head_down)
        d.ellipse((hx - 0.13 * s, hy - 0.15 * s, hx + 0.13 * s, hy + 0.15 * s), fill=(12, 14, 22))
        d.rounded_rectangle((hx - 0.28 * s, hy + 0.1 * s, hx + 0.24 * s, h * 0.5), int(0.1 * s), fill=(12, 14, 22))
        d.ellipse((w * 0.4 - 0.12 * s, h * 0.24 - 0.14 * s, w * 0.4 + 0.12 * s, h * 0.24 + 0.14 * s), fill=(18, 20, 30))   # le père
    d.line((w * 0.52, h * 0.16, w * 0.52, h * 0.47), fill=body, width=max(3, int(0.06 * s)))
    if rain_on:
        rr = np.random.default_rng(int(tg * 6) % 9)
        for _ in range(26):
            px, py = rr.uniform(w * 0.3, w * 0.76), rr.uniform(h * 0.18, h * 0.44)
            d.line((px, py, px - 2, py + rr.uniform(6, 18)), fill=(170, 190, 230, 200), width=2)
    d.line((w * 0.05, h * 0.6, w * 0.95, h * 0.6), fill=hl, width=max(2, int(0.025 * s)))
    for wx in (0.22, 0.78):
        d.ellipse((w * wx - 0.36 * s, h * 0.6, w * wx + 0.36 * s, h * 0.6 + 0.72 * s), fill=(14, 14, 18))
        d.ellipse((w * wx - 0.18 * s, h * 0.6 + 0.18 * s, w * wx + 0.18 * s, h * 0.6 + 0.54 * s), fill=(110, 116, 130))
    d.rounded_rectangle((w * 0.93, h * 0.5, w * 0.985, h * 0.6), 6, fill=(255, 240, 200))
    d.rounded_rectangle((w * 0.015, h * 0.5, w * 0.06, h * 0.6), 6, fill=(220, 40, 40))
    img.alpha_composite(L, (int(x - w / 2), int(y - h * 0.97)))
    G = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(G)   # faisceau des phares
    hx0 = x + w * 0.46; hy0 = y - h * 0.42
    dg.polygon([(hx0, hy0), (hx0 + 900, hy0 - 160), (hx0 + 900, hy0 + 200)], fill=(255, 240, 200, 50))
    img.alpha_composite(G.filter(ImageFilter.GaussianBlur(20)))

def calendar(img, cx, cy, s, n, k_flip):
    """bloc-calendrier : page « n » ; la page du dessus s'arrache et s'envole (k_flip 0..1)"""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((cx - 1.0 * s, cy - 1.1 * s, cx + 1.0 * s, cy + 1.1 * s), int(0.1 * s), fill=(244, 240, 230), outline=(80, 80, 90), width=5)
    d.rectangle((cx - 1.0 * s, cy - 1.1 * s, cx + 1.0 * s, cy - 0.6 * s), fill=RED)
    for i in range(4): d.ellipse((cx - 0.7 * s + i * 0.46 * s - 12, cy - 1.18 * s, cx - 0.7 * s + i * 0.46 * s + 12, cy - 1.02 * s), fill=(60, 60, 70))
    text(d, (cx, cy - 0.85 * s), "MOIS", int(0.3 * s), WHITE, BOLD)
    text(d, (cx, cy + 0.3 * s), str(n), int(1.0 * s), (30, 34, 46), BOLD)
    if 0 < k_flip < 1:
        u = eout(k_flip)
        L = Image.new("RGBA", (int(2 * s), int(1.7 * s)), (244, 240, 230, int(255 * (1 - u))))
        dl = ImageDraw.Draw(L); text(dl, (s, 0.9 * s), str(n - 1), int(1.0 * s), (30, 34, 46, int(255 * (1 - u))), BOLD)
        L = L.rotate(-40 * u, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(L, (int(cx - s + 500 * u), int(cy - 0.6 * s - 700 * u)))

def signpost(d, xw, z, label_, col=(250, 250, 250), bg=(30, 110, 60)):
    x, y = proj(xw, z); s = 1.0 / z
    if s < 0.05: return
    d.rectangle((x - 8 * s, y - 520 * s, x + 8 * s, y), fill=(70, 70, 80))
    bw, bh = 340 * s, 140 * s
    d.rounded_rectangle((x - bw / 2, y - 520 * s - bh, x + bw / 2, y - 520 * s), int(14 * s), fill=bg, outline=col, width=max(2, int(8 * s)))
    if s > 0.12: text(d, (x, y - 520 * s - bh / 2), label_, max(10, int(70 * s)), col, BOLD)

def scoreboard(d, cx, cy, a, b, k):
    if k <= 0: return
    sc = pop(k, 100, 0.3) / 100
    w, h = 420 * sc, 150 * sc
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(20 * sc), fill=(12, 14, 24), outline=GOLD, width=6)
    text(d, (cx, cy), f"{a}  -  {b}", int(100 * sc), (255, 230, 120), MONO)

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    img.paste(CAR_NIGHT); d = ImageDraw.Draw(img); gate(d, 1.0)
    shadow(d, W / 2, FEET, 250); P(img, W / 2, FEET, 250, "sad"); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2 + 60, FEET - 200)); bag(d, hp[0], hp[1] + 60 / ZF, 140 / ZF)
    rain(d, tg, 1.0)
    topsh(img); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    sc = 1 + 0.3 * (1 - eout((tg + 0.12) / 0.2))
    text(d, (W / 2, 380), "TU AS RATÉ", int(fit("TU AS RATÉ", 110, 1000) * sc), WHITE, BOLD, stroke=8, scol=BG)
    kk = tg - K["hook"] + 0.1; hit = 0.0
    if kk > 0:
        text(d, (W / 2, 540), "UN ESSAI ?", pop(kk, fit("UN ESSAI ?", 170, 1000), 0.25, 0.2), ORANGE, BOLD, stroke=10, scol=BG)
        hit = max(0, 1 - kk / 0.3)
    kq = kM(tg, "quatre")
    if kq > 0: hit = max(hit, stamp(img, "4 FOIS « NON »", (W / 2, 720), 120, -6, kq, (255, 70, 60)))
    return dict(hit=hit)

def s_intro(img, d, tg, k):
    img.paste(TER_DUSK); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, "stand"); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 300)); ball(d, hp[0] + 6, hp[1] + 10, 30 / ZF + 6, WHITE, tg * 2)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 290, "L'HISTOIRE VRAIE", 100, WHITE, k)
    TX(d, 400, "D'UN FOOTBALLEUR RECALÉ", 76, ICE, k - 0.25)
    kl = kM(tg, "londres"); kg = kM(tg, "ghana"); hit = 0.0
    TX(d, 560, "IL GRANDIT À LONDRES", 84, ORANGE, kl)
    TX(d, 680, "FAMILLE VENUE DU GHANA", 66, GOLD, kg)
    if 0 < kl < 0.25: hit = 1 - kl / 0.25
    return dict(hit=hit)

def s_essais(img, d, tg, k):
    """3 essais : à chaque nom, le portail se ferme devant lui et une croix rouge tombe"""
    img.paste(CAR_DUSK); d = ImageDraw.Draw(img)
    ks = [kM(tg, "arsenal"), kM(tg, "tott"), kM(tg, "mill")]
    n = sum(1 for x in ks if x > 0); last = max([x for x in ks if x > 0], default=0.0)
    cl = 0.0 if n == 0 else min(1, last / 0.35) if last < 0.6 else 1.0 - min(1, (last - 0.6) / 0.3) if n < 3 else 1.0
    gate(d, cl)
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, "stand" if cl < 0.5 else "sad"); d = ImageDraw.Draw(img)
    topsh(img); d = ImageDraw.Draw(img)
    hit = 0.0
    for i, kx in enumerate(ks):
        if kx <= 0: continue
        y = 330 + i * 150
        TX(d, y, f"ESSAI {i + 1}", 90, WHITE, kx, x=W / 2 - 120, maxw=500)
        hit = max(hit, stamp(img, "X", (W / 2 + 230, y), 120, -8, kx - 0.1, (255, 60, 60), box=False)); d = ImageDraw.Draw(img)
    kr = kM(tg, "rates")
    if kr > 0: hit = max(hit, stamp(img, "RATÉS", (W / 2, 820), 130, -5, kr, (255, 70, 60)))
    return dict(hit=hit)

def s_palace(img, d, tg, k):
    img.paste(CAR_DUSK); d = ImageDraw.Draw(img)
    kw = kM(tg, "semaines"); k15 = kM(tg, "ans15"); kr = kM(tg, "recale"); hit = 0.0
    gate(d, 0.0 if kr <= 0 else min(1, kr / 0.3))
    if kr <= 0:   # 8 semaines d'entraînement à l'essai : il court en profondeur
        shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, run_pose(k * 8)); d = ImageDraw.Draw(img)
    else:
        shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, blend_pose(POSES["stand"], POSES["sad"], eout(kr / 0.4))); d = ImageDraw.Draw(img)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 290, "NOUVEL ESSAI", 96, WHITE, k)
    if kw > 0:
        wk = 1 + int(min(7, kw * 5)); counter(d, 440, 1, 8, kw, 1.4, 150, GOLD); TX(d, 560, "SEMAINES D'ESSAI", 70, WHITE, kw - 0.2)
    badge(d, W / 2, 700, "15 ANS", k15, GOLD, 105)
    if 0 < k15 < 0.25: hit = 1 - k15 / 0.25
    if kr > 0: hit = max(hit, stamp(img, "ENCORE RECALÉ", (W / 2, 880), 110, -6, kr, (255, 70, 60)))
    return dict(hit=hit)

def s_voiture(img, d, tg, k):
    """dans la voiture du père, sous la pluie, tête basse ; essuie-glaces ; il arrête le football"""
    img.paste(CAR_NIGHT); d = ImageDraw.Draw(img); gate(d, 1.0)
    kp = kM(tg, "pleure"); ka = kM(tg, "arrete"); hit = 0.0
    cx, cy = Q(W / 2 - 60, FEET + 40)
    car(img, cx, cy, 250 / ZF, k, head_down=1.0, tg=tg); d = ImageDraw.Draw(img)
    if ka > 0:    # le sac de foot reste dehors, sous la pluie
        bx, by = Q(W / 2 + 430, FEET + 60); bag(d, bx, by, 170 / ZF)
        for sgn in (-1, 1):
            B = boot(d, 0, 0, 110 / ZF, sgn * 8); img.alpha_composite(B, (int(bx + sgn * 120 / ZF - B.width / 2), int(by - B.height - 4)))
        d = ImageDraw.Draw(img)
    rain(d, tg, 1.3)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 290, "CE SOIR-LÀ…", 100, WHITE, k)
    TX(d, 410, "IL PLEURE DANS LA VOITURE", 70, ICE, kp)
    TX(d, 500, "DE SON PÈRE", 70, ICE, kM(tg, "pere"))
    if ka > 0:
        hit = stamp(img, "IL ARRÊTE LE FOOT", (W / 2, 680), 110, -5, ka, (255, 70, 60))
    return dict(hit=hit)

def s_pause(img, d, tg, k):
    """un an sans ballon : il marche en sweat à capuche, le calendrier perd ses pages (1 -> 12 mois)"""
    img.paste(TER_NIGHT); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, "shy", hood=True); d = ImageDraw.Draw(img)
    kn = kM(tg, "nimporte"); kpg = kM(tg, "page"); hit = 0.0
    topsh(img); d = ImageDraw.Draw(img)
    mon = 1 + int(min(11, max(0, k) * 4.2))
    fl = (max(0, k) * 4.2) % 1 if mon < 12 else 0
    calendar(img, W / 2 + 260, 620, 140, mon, fl); d = ImageDraw.Draw(img)
    TX(d, 290, "1 AN SANS BALLON", 100, WHITE, k, x=W / 2)
    if kn > 0: text(d, (W / 2, 820), typew("N'IMPORTE QUI AURAIT", kn, 26), fit("N'IMPORTE QUI AURAIT", 70, 940), WHITE, BOLD, stroke=6, scol=BG)
    if kpg > 0: hit = stamp(img, "TOURNÉ LA PAGE.", (W / 2, 960), 110, -5, kpg - 0.15, ICE)
    if 0 < k < 0.25: hit = max(hit, 1 - k / 0.25)
    return dict(hit=hit)

def s_crampons(img, d, tg, k):
    """LE CRI : les crampons volent jusqu'à lui, la nuit du parking s'ouvre sur la campagne dorée, il sprinte vers nous"""
    kb = tg - K["boom"]; kk = max(0.0, kb + 0.06)
    kr = kM(tg, "remet")
    c = (W / 2, 900)
    r = eout(max(0, kr) / 1.4) * 2300 if kr > 0 else 0
    img.paste(reveal(NIGHT_ARR, GOLD_ARR, c, r)); d = ImageDraw.Draw(img)
    rays(img, min(1, max(0, kr - 0.2) / 0.5)); d = ImageDraw.Draw(img)
    speed_lines(d, c, kr, 44)
    rings(img, c, kr, 6, GOLD, 1050, 16, 0.14, 1.25); rings(img, c, kr - 0.07, 6, WHITE, 1050, 6, 0.14, 1.25)
    d = ImageDraw.Draw(img)
    burst(d, c[0], c[1], kr, 26, 520, (255, 240, 190), 3, 10)
    hood = kr < 0.15
    shadow(d, W / 2, FEET, 270)
    pose = POSES["shy"] if kb < 0 else (POSES["shout"] if kr < 0.35 else dict(run_pose(tg * 11), t=20))
    P(img, W / 2, FEET, 270, pose, hood=hood, glow=1.0 + 0.6 * (kr > 0))
    d = ImageDraw.Draw(img)
    if 0 < kb and kr < 0.3:   # les crampons arrivent en tournoyant depuis le coin bas
        u = min(1, kb / max(0.2, (M("remet", 99) - K["boom"]) + 0.25))
        for sgn in (-1, 1):
            fx, fy = Q(W / 2 + sgn * 70, FEET - 10)
            bx = lerp(W / 2 + sgn * 640, fx, eout(u)); by = lerp(H + 120, fy, eout(u)) - 260 * math.sin(math.pi * u)
            B = boot(d, 0, 0, 180 / ZF * (1.6 - 0.6 * u), sgn * 720 * (1 - u)); img.alpha_composite(B, (int(bx - B.width / 2), int(by - B.height / 2)))
        d = ImageDraw.Draw(img)
    rain(d, tg, max(0, 1 - kr * 2) if kr > 0 else 1.0)
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    hit = max(0, 1 - kk / 0.3) if kk > 0 else 0
    e = eout(kk / 0.22) if kk > 0 else 0
    l1 = "MAIS 1 AN PLUS TARD," if kb > 0 else ""
    l2 = "IL REMET LES CRAMPONS !" if kr > 0 else ""
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, eout(max(0, kr) / 0.22))
    f1 = fit("MAIS 1 AN PLUS TARD,", 110, 880); f2 = pop(kM(tg, "crampons"), fit("IL REMET LES CRAMPONS !", 104, 880), 0.08)
    for off, cc in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        if l1: text(d, (x1 + o, 420), l1, f1, cc, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
        if l2: text(d, (x2 - o, 570), l2, f2, cc if cc != WHITE else GOLD, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
    hr = max(0, 1 - kr / 0.3) if kr > 0 else 0
    return dict(hit=max(hit, hr) * 1.6, shake=max(hit, hr) * 1.9, flash=max(0, 0.9 - kr * 2.6) if kr > 0 else 0)

def s_college(img, d, tg, k):
    k16 = kM(tg, "ans16"); ka = kM(tg, "academie"); k17 = kM(tg, "ans17"); ks = kM(tg, "signe"); hit = 0.0
    if k17 <= 0:    # académie de lycée à la campagne, course en montée dans la brume
        img.paste(CTRY); d = ImageDraw.Draw(img)
        shadow(d, W / 2, FEET, 240, (40, 80, 44)); P(img, W / 2, FEET, 240, run_pose(k * 8)); d = ImageDraw.Draw(img)
        topsh(img, 0.7); d = ImageDraw.Draw(img)
        badge(d, 180, 330, "16 ANS", k16, GOLD, 110)
        TX(d, 520, "ACADÉMIE DE LYCÉE", 90, WHITE, ka)
        TX(d, 640, "LOIN DE LONDRES", 74, ICE, kM(tg, "loin"))
        if 0 < k16 < 0.25: hit = 1 - k16 / 0.25
        return dict(hit=hit)
    img.paste(CTRY_GOLD); rays(img, 0.5); d = ImageDraw.Draw(img)
    shadow(d, W / 2 - 120, FEET, 250, (40, 90, 44)); P(img, W / 2 - 120, FEET, 250, "stand" if ks <= 0 else "fist"); d = ImageDraw.Draw(img)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    badge(d, 180, 330, "17 ANS", k17, GOLD, 110)
    TX(d, 520, "UN CLUB PRO LE PREND À L'ESSAI", 66, WHITE, kM(tg, "bristol"))
    if ks > -0.3:
        paper(img, 820, 940, ks + 0.3); d = ImageDraw.Draw(img)
    if ks > 0: hit = stamp(img, "SIGNÉ", (W / 2 - 150, 720), 130, -6, ks, (40, 230, 130))
    if 0 < k17 < 0.25: hit = max(hit, 1 - k17 / 0.25)
    return dict(hit=hit)

def s_prets(img, d, tg, k):
    """la route des prêts : panneaux 6e / 4e / 3e division qui défilent, il marche avec son sac ; 0 BUT"""
    img.paste(ROAD); d = ImageDraw.Draw(img)
    k6 = kM(tg, "d6"); k4 = kM(tg, "d4"); k3 = kM(tg, "d3"); kz = kM(tg, "zero"); hit = 0.0
    travel = max(0, k) * 1.2
    for i, (lab, kx) in enumerate((("6e DIV.", k6), ("4e DIV.", k4), ("3e DIV.", k3))):
        z = 2.6 + i * 2.2 - travel
        if z > 0.6: signpost(d, W / 2 + (420 if i % 2 == 0 else -420), z, lab, bg=(30, 110, 60) if i < 2 else (150, 40, 40))
    shadow(d, W / 2, FEET, 240, (30, 30, 40)); P(img, W / 2, FEET, 240, run_pose(tg * 5) if kz <= 0 else "sad"); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 200)); bag(d, hp[0], hp[1] + 50 / ZF, 120 / ZF)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    TX(d, 270, "LES PRÊTS", 110, WHITE, k)
    for j, (lab, kx) in enumerate((("6e DIVISION", k6), ("4e DIVISION", k4), ("3e DIVISION", k3))):
        TX(d, 400 + j * 100, lab, 76, ICE if j < 2 else (255, 120, 110), kx)
    if kz > 0: hit = stamp(img, "0 BUT", (W / 2, 780), 170, -6, kz, (255, 70, 60))
    return dict(hit=hit)

def s_bournemouth(img, d, tg, k):
    ky = kM(tg, "y2023"); kb = kM(tg, "b11"); hit = 0.0
    img.paste(STAD_FR); d = ImageDraw.Draw(img)
    n = int(max(0, kb) * 7)
    shadow(d, W / 2, FEET, 260)
    P(img, W / 2, FEET - (24 * abs(math.sin(k * 6)) if kb > 0 else 0), 260, ("kick" if n % 2 else "fist") if kb > 0 else run_pose(k * 8), glow=1.3)
    d = ImageDraw.Draw(img)
    if kb > 0: confetti(d, kb * 0.9, 0.5)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 270, "IL NE LÂCHE RIEN", 96, WHITE, k)
    TX(d, 410, "2023", 140, GOLD, ky, amp=0.3)
    TX(d, 530, "UN CLUB DE 1re DIVISION", 66, ICE, ky - 0.3)
    counter(d, 700, 0, 11, kb, 1.1, 210, GOLD)
    TX(d, 850, "BUTS EN UNE SAISON", 76, WHITE, kM(tg, "saison"))
    if 0 < ky < 0.25: hit = 1 - ky / 0.25
    return dict(hit=hit)

def s_finale(img, d, tg, k):
    ky = kM(tg, "y2026"); kf = kM(tg, "finale"); km = kM(tg, "marque"); ks = kM(tg, "seul"); hit = 0.0; flash = 0.0
    img.paste(STAD_ENG); d = ImageDraw.Draw(img)
    flashp = np.random.default_rng(int(tg * 10))
    for _ in range(12):
        fx, fy = flashp.uniform(0, W), flashp.uniform(480, 890); d.ellipse((fx - 6, fy - 6, fx + 6, fy + 6), fill=(255, 255, 255))
    gx, gy = W / 2 + 140, 1130
    if kf > 0: goal(d, gx, gy, 0.7)
    shadow(d, W / 2 - 100, FEET, 260)
    if km > -0.1: pose = "kick" if km < 0.4 else "up"
    else: pose = run_pose(k * 9)
    P(img, W / 2 - 100, FEET, 260, pose, glow=1.5); d = ImageDraw.Draw(img)
    if km > -0.1:
        v = min(1, (km + 0.1) / 0.3); s0 = Q(W / 2 - 20, FEET)
        bx = lerp(s0[0], gx - 160, eout(v)); by = lerp(s0[1], gy - 180, eout(v)) - 60 * math.sin(math.pi * v)
        ball(d, bx, by, 30 - 12 * v, WHITE, tg * 12)
        if v >= 1: burst(d, bx, by, km - 0.2, 16, 240, WHITE, 2, 8)
    if km > 0.4: confetti(d, (km - 0.4) * 1.2, 0.8); crowd(d, tg, up_all=True, rise=0.6)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 270, "2026", 150, GOLD, ky, amp=0.3, stroke=9)
    TX(d, 400, "UN GÉANT ANGLAIS", 90, WHITE, ky - 0.25)
    if kf > 0 and km <= 0: TX(d, 540, "EN FINALE DE COUPE…", 80, ICE, kf)
    if km > 0:
        scoreboard(d, W / 2, 600, 1, 0, km)
        hit = 1 - km / 0.25 if km < 0.25 else 0; flash = 0.3 * max(0, 1 - km / 0.3)
    if ks > 0: hit = max(hit, stamp(img, "LE SEUL BUT DU MATCH", (W / 2, 790), 96, -4, ks, GOLD))
    return dict(hit=hit, flash=flash)

def s_regard(img, d, tg, k):
    """retour au parking… à l'aube : le portail est ouvert, il soulève une coupe générique"""
    kv = kM(tg, "souleve"); hit = 0.0
    img.paste(CAR_GOLD); rays(img, 0.7); d = ImageDraw.Draw(img); gate(d, 0.0)
    if kv > 0: confetti(d, kv)
    shadow(d, W / 2, FEET + 20, 260, (90, 80, 84))
    P(img, W / 2, FEET + 20 - (18 * abs(math.sin(tg * 7)) if kv > 0 else 0), 260, "up" if kv > 0 else "stand", glow=1.5); d = ImageDraw.Draw(img)
    if kv > 0:
        c = _pt(JT["lh"], JT["rh"], 0.5); lift = 60 * eout(min(1, kv / 0.4))
        trophy(d, c[0], c[1] - 30 - lift, 0.72); burst(d, c[0], c[1] - 150 - lift, kv, 20, 330, GOLD, 9, 9)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 250, "LE GAMIN RECALÉ", 96, WHITE, k)
    TX(d, 360, "À 15 ANS…", 90, ICE, kM(tg, "gamin") + 0.6)
    if kv > 0:
        hit = stamp(img, "A SOULEVÉ LA COUPE", (W / 2, 480), 100, -4, kv, GOLD)
    return dict(hit=hit, flash=0.4 * max(0, 1 - kv / 0.25) if kv > 0 else 0)

def s_you(img, d, tg, k):
    kv = kM(tg, "vraiment"); kn = kM(tg, "seulnon"); hit = 0.0
    img.paste(CAR_DUSK); d = ImageDraw.Draw(img); gate(d, 0.5)
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET, 262, blend_pose(POSES["stand"], POSES["point"], eout(max(0, kv) / 0.3)), glow=1.2)
    dim(img, 0.25); topsh(img); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(150 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=8, scol=BG)
    TX(d, 470, "TU VAS VRAIMENT ABANDONNER", 76, WHITE, kv)
    if kn > 0:
        hit = stamp(img, "APRÈS UN SEUL « NON » ?", (W / 2, 620), 100, -4, kn, GOLD)
    return dict(hit=hit)

def s_abonne(img, d, tg, k):
    img.paste(CAR_NIGHT); d = ImageDraw.Draw(img)
    dim(img, 0.6); d = ImageDraw.Draw(img)
    hit = 0.0
    P(img, 200, FEET + 20, 215, "point", glow=1.2); d = ImageDraw.Draw(img)
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rounded_rectangle((W / 2 - bw / 2, 420 - bh / 2, W / 2 + bw / 2, 420 + bh / 2), int(40 * sc), fill=RED)
    text(d, (W / 2 - bw / 2 + 90 * sc, 420), "+", int(130 * sc), WHITE, BOLD)
    text(d, (W / 2 + 50 * sc, 420), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE, BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = kM(tg, "demain")
    if kd > 0:
        TX(d, 660, "DEMAIN · ÉPISODE 10", 74, GOLD, kd)
        text(d, (W / 2, 770), typew("EN 3e DIVISION À 21 ANS…", kd, 30), fit("EN 3e DIVISION À 21 ANS…", 70, 940), WHITE, BOLD, stroke=6, scol=BG)
    ke = kM(tg, "buteur")
    if ke > 0: hit = max(hit, stamp(img, "MEILLEUR BUTEUR DE SON PAYS", (W / 2 + 20, 960), 70, -4, ke, GOLD))
    return dict(hit=hit)

NUMS = [(np.random.default_rng(i).uniform(140, W - 140), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["8/10", "10/10", "6/10", "9/10", "7/10", "5/10", "10/10", "8/10", "9/10", "7/10"])]
def s_question(img, d, tg, k):
    img.paste(CAR_NIGHT); d = ImageDraw.Draw(img)
    dim(img, 0.72); d = ImageDraw.Draw(img)
    pulse = 0.0
    for tk in TJ["q_pulses"]:
        dd = tg - tk
        if 0 <= dd < 0.5: pulse = max(pulse, math.exp(-dd * 7))
    a = 1.0; de = tg - K["q_end"]
    if de > 0: a = max(0.0, 1 - de / 0.8)
    for x, y, s, sp in NUMS:
        yy_ = (y - tg * 50 * sp) % 700 + 720
        text(d, (x, yy_), s, 56, mix((30, 38, 56), (200, 150, 60), a), BOLD)
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix((30, 38, 56), (120, 60, 30), a), BOLD)
    return dict(hit=0.5 * pulse)

def s_logo(img, d, tg, k):
    img.paste(CAR_NIGHT); dim(img, 0.9); d = ImageDraw.Draw(img)
    fade = 1 - ease((tg - (END - 0.7)) / 0.7)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    sc = 1 + 0.15 * (1 - eout(k / 0.5)); g = tuple(int(c * fade) for c in GOLD)
    text(dl, (W / 2, 690), "MINDSET", int(150 * sc), g + (255,), BOLD)
    text(dl, (W / 2, 900), "24", int(300 * sc), g + (255,), BOLD)
    glow = L.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow); img.alpha_composite(glow); img.alpha_composite(L)
    d = ImageDraw.Draw(img)
    d.line((W / 2 - 300 * eout(k / 0.6), 1080, W / 2 + 300 * eout(k / 0.6), 1080), fill=g, width=4)
    if fade < 1: dim(img, 1 - fade, (0, 0, 0))
    return dict(fade=fade)

SCENES = {"hook": s_hook, "intro": s_intro, "essais": s_essais, "palace": s_palace, "voiture": s_voiture, "pause": s_pause, "crampons": s_crampons,
          "college": s_college, "prets": s_prets, "bournemouth": s_bournemouth, "finale": s_finale, "regard": s_regard, "you": s_you,
          "abonne": s_abonne, "question": s_question, "logo": s_logo}
BGLEVEL = {}
def scenery(level): return Image.new("RGBA", (W, H), BG + (255,))

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

# =============================================================== MISE EN SCÈNE 3D (10/11/2026, demande utilisateur : « vraie animation 3D, il se déplace dans tous les sens »)
# 1) Le héros vit sur un sol en PERSPECTIVE : profondeur ZF (1 = plan de référence, > 1 = plus loin, < 1 = plus près de la caméra),
#    décalage latéral DX (monde) et saut JMP ; taille, position et ombre sont projetées (point de fuite = horizon HOR).
# 2) La CAMÉRA bouge sur le monde (avant les textes) : travelling avant/arrière, panoramique, orbite (yaw), plongée/contre-plongée (pitch),
#    roulis et caméra à l'épaule, via une homographie (cv2.warpPerspective).
ZF = 1.0; DX = 0.0; JMP = 0.0; WALK = False; TG = 0.0; CAM = None
def Q(x, y):
    return (W / 2 + (x + DX - W / 2) / ZF, HOR + (y - HOR) / ZF - JMP)
_P2 = P; _SH2 = shadow; _BA2 = band_on_arm; _TR2 = trophy; _TOP2 = topsh
def P(img, x, y, s, pose, winter=False, fixed=False, **kw):
    if not fixed:
        x, y = Q(x, y); s = s / ZF
        if WALK: pose = run_pose(TG * 7.5)
    _P2(img, x, y, s, pose, winter=winter, **kw)
def shadow(d, x, y, s, col=SNOW_SH, fixed=False):
    if not fixed:
        x, y = Q(x, y); y += JMP; s = s / ZF * (1 - min(0.5, JMP / 400))
    _SH2(d, x, y, s, col)
def band_on_arm(d, s, k=1.0): _BA2(d, s / ZF, k)
def trophy(d, cx, cy, s=1.0, col=GOLD): _TR2(d, cx, cy, s / ZF, col)
def footprints(d, xa, xb, y, col=(170, 186, 214), step=44): return   # remplacées : la trace suivrait le héros en profondeur

def _seg(k, pts):
    """interpolation lissée d'une trajectoire [(t, zf, dx, jmp), ...] ; renvoie zf, dx, jmp, vitesse"""
    if k <= pts[0][0]: a = pts[0]; return a[1], a[2], a[3], 0.0
    for a, b in zip(pts, pts[1:]):
        if k <= b[0]:
            u = ease((k - a[0]) / max(1e-3, b[0] - a[0]))
            sp = abs(b[1] - a[1]) * 40 + abs(b[2] - a[2]) / 10
            return lerp(a[1], b[1], u), lerp(a[2], b[2], u), lerp(a[3], b[3], u), sp if 0 < u < 1 else 0.0
    b = pts[-1]; return b[1], b[2], b[3], 0.0

def MK_(n, d=0.0): return M(n, 99) - d
def PATH(typ, k, tg):
    st = SC[typ]
    if typ == "hook":      # tête basse devant le portail fermé, il recule lentement
        return _seg(k, [(0, 1.05, 0, 0), (3.5, 1.35, 0, 0)]) + (False,)
    if typ == "intro":     # remonte la rue de briques en diagonale, du fond vers nous
        return _seg(k, [(0, 3.0, -300, 0), (2.6, 1.05, 120, 0)]) + (k < 2.6,)
    if typ == "essais":    # avance vers le portail à chaque essai, puis recule
        return (1.35 + 0.35 * math.sin(k * 1.3), 60 * math.sin(k * 0.9), 0.0, 0.0, False)
    if typ == "palace":
        r = MK_("recale") - st
        if k < r: return (1.6 + 0.5 * math.sin(k * 1.6), 260 * math.sin(k * 2.1), 0.0, 0.0, False)
        return _seg(k, [(r, 1.6, 0, 0), (r + 1.5, 1.15, 0, 0)]) + (False,)
    if typ == "voiture":
        return _seg(k, [(0, 1.3, 0, 0), (4.0, 1.0, 0, 0)]) + (False,)
    if typ == "pause":     # il marche lentement le long des maisons, de gauche à droite et vers le fond
        return _seg(k, [(0, 1.0, -260, 0), (3.6, 1.7, 260, 0)]) + (True,)
    if typ == "crampons":  # au cri : il jaillit du fond vers la caméra
        r = MK_("remet") - st
        return _seg(k, [(0, 1.8, 0, 0), (r, 1.8, 0, 0), (r + 1.1, 0.85, 0, 0)]) + (False,)
    if typ == "college":   # course en montée vers le petit terrain, en diagonale
        s7 = MK_("ans17") - st
        if k < s7: return _seg(k, [(0, 0.95, 280, 0), (s7, 2.4, -200, 0)]) + (False,)
        return _seg(k, [(s7, 1.7, 0, 0), (s7 + 1.6, 1.0, 0, 0)]) + (False,)
    if typ == "prets":
        return (1.05 + 0.08 * math.sin(k * 2), 0.0, 0.0, 0.0, False)
    if typ == "bournemouth":
        return _seg(k, [(0, 2.4, -260, 0), (2.4, 1.0, 120, 0)]) + (False,)
    if typ == "finale":
        m = MK_("marque") - st
        return _seg(k, [(0, 2.6, 300, 0), (m - 0.1, 1.1, 0, 0)]) + (False,)
    if typ == "regard":
        return _seg(k, [(0, 2.0, 0, 0), (2.4, 1.0, 0, 0)]) + (k < 2.4,)
    if typ == "you":
        v = MK_("vraiment") - st
        return _seg(k, [(0, 1.35, -150, 0), (v, 0.88, 60, 0)]) + (k < v,)
    return (1.0, 0.0, 0.0, 0.0, False)

def CAMF(typ, k, tg):
    hh = (6 * math.sin(tg * 2.1), 5 * math.sin(tg * 1.7 + 1))
    dur = 3.0
    for s_ in SCN:
        if s_["type"] == typ: dur = s_["end"] - s_["start"]
    u = ease(k / max(0.5, dur))
    if typ == "hook":     return (lerp(1.3, 1.1, u), lerp(60, -40, u) + hh[0], lerp(60, 0, u) + hh[1], lerp(0.07, -0.03, u), -0.02, lerp(-1.5, 0, u))
    if typ == "intro":    return (lerp(1.08, 1.18, u), lerp(-90, 60, u), hh[1], lerp(0.08, -0.04, u), -0.04, 0.0)
    if typ == "essais":   return (1.1 + 0.04 * math.sin(k * 2), hh[0] + 50 * math.sin(k * 0.8), hh[1], 0.07 * math.sin(k * 0.6), 0.03, 0.0)
    if typ == "palace":   return (lerp(1.06, 1.2, u), hh[0] * 2, lerp(0, -40, u), lerp(-0.06, 0.06, u), 0.0, 1.2 * math.sin(tg * 2))
    if typ == "voiture":  return (lerp(1.22, 1.08, u), lerp(80, -60, u) + hh[0], hh[1], lerp(-0.08, 0.06, u), -0.05, lerp(1.5, 0, u))
    if typ == "pause":    return (lerp(1.06, 1.16, u), lerp(-40, 40, u), hh[1], lerp(0.05, -0.05, u), 0.04, 0.0)
    if typ == "crampons":
        kb = max(0.0, tg - M("remet", 99))
        orb = math.sin(min(1, kb / 1.8) * math.pi) * 0.13
        return (1.08 + 0.2 * math.exp(-kb * 3) if kb > 0 else 1.1, hh[0] * 2, hh[1], orb, 0.06 if kb > 0 else 0.0, 3 * math.sin(kb * 4) * math.exp(-kb * 2))
    if typ == "college":  return (lerp(1.06, 1.2, u), lerp(70, -70, u) + hh[0], lerp(40, -20, u), lerp(-0.07, 0.07, u), 0.06, 0.0)
    if typ == "prets":    return (1.1, hh[0], hh[1] + lerp(0, 40, u), 0.05 * math.sin(k * 0.7), -0.04, 0.0)
    if typ == "bournemouth": return (lerp(1.08, 1.2, u), lerp(100, -80, u) + hh[0], hh[1], lerp(0.07, -0.07, u), 0.0, 0.0)
    if typ == "finale":
        m = tg - M("marque", 99)
        if m > 0: return (lerp(1.08, 1.22, ease(m / 2.5)), hh[0], lerp(0, 70, ease(m / 2.5)), 0.08 * math.sin(m), 0.08, 0.0)
        return (lerp(1.2, 1.08, u), lerp(-80, 40, u) + hh[0], hh[1], lerp(-0.08, 0.04, u), 0.0, 1.2 * math.sin(tg * 3))
    if typ == "regard":   return (lerp(1.18, 1.06, u), hh[0], lerp(-40, 30, u), lerp(0.08, -0.06, u), 0.05, 0.0)
    if typ == "you":      return (lerp(1.06, 1.16, u), lerp(-60, 30, u) + hh[0], hh[1], lerp(0.06, -0.04, u), 0.0, 0.0)
    return None

def _cam_warp(img):
    if CAM is None: return
    z, px, py, yaw, pitch, roll = CAM
    z = max(z, 1.0 + 1.6 * abs(yaw) + 1.4 * abs(pitch) + 0.02 + (abs(px) / (W * 0.5)) * 0.5 + (abs(py) / (H * 0.5)) * 0.5)
    src = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
    cx, cy = W / 2, H / 2
    # trapèze : orbite (yaw) = côtés gauche/droit de hauteurs différentes ; pitch = haut/bas de largeurs différentes
    pts = []
    for (x, y) in src:
        nx, ny = (x - cx) / (W / 2), (y - cy) / (H / 2)
        sy = 1 + yaw * nx; sx = 1 + pitch * ny
        pts.append((nx * sx, ny * sy))
    a = math.radians(roll); ca, sa = math.cos(a), math.sin(a)
    dst = np.float32([[cx + z * (W / 2) * (ca * X - sa * Y * H / W) + px, cy + z * (H / 2) * (sa * X * W / H + ca * Y) + py] for X, Y in pts])
    Hm = cv2.getPerspectiveTransform(src, dst)
    arr = np.asarray(img)
    out = cv2.warpPerspective(arr, Hm, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    img.paste(Image.fromarray(out))

def topsh(img, a=1.0):
    """frontière monde / textes : la caméra 3D s'applique au monde, puis l'ombre du haut"""
    _cam_warp(img); _TOP2(img, a)

_RS2 = render_scene
def render_scene(tg, i):
    global ZF, DX, JMP, WALK, TG, CAM
    s = SCN[i]; k = tg - s["start"]; TG = tg
    zf, dx, jm, sp, wk = PATH(s["type"], k, tg)
    ZF, DX, JMP, WALK = zf, dx, jm, bool(wk)
    CAM = CAMF(s["type"], k, tg)
    try:
        return _RS2(tg, i)
    finally:
        ZF, DX, JMP, WALK, CAM = 1.0, 0.0, 0.0, False, None


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None, int(a[5]) if len(a) > 5 else 1)

# -*- coding: utf-8 -*-
"""Style « 3D ép. 12 » (17/11/2026, Azzedine Ounahi) — retour au moteur 3D plein écran (décor + caméra), personnage SILHOUETTE LUMINEUSE.
Ancien en-tête : Style « essai » (12/11/2026, Antoine Semenyo — épisode 9) : parking de centre d entraînement sous la pluie, voiture du père, rue de briques,
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
    text(d, (W / 2, y + 98), "ÉPISODE 14", 40, GOLD, MONO)

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


# =============================================================== ép. 12 : personnage SILHOUETTE LUMINEUSE (crème, sans visage, halo chaud)
CREAM = (246, 240, 226); CREAM_D = (214, 206, 192)
SKIN = CREAM; SKIN_D = CREAM_D; HAIR = CREAM; BOOT = CREAM_D; RIM = (255, 214, 150)
JER = CREAM; NAVY = CREAM
_PLAYER0 = player
def player(img, x, y, s, pose, *a, **kw):
    """dessine la silhouette sur un calque, puis ajoute un halo chaud (glow)"""
    L = Image.new("RGBA", img.size, (0, 0, 0, 0))
    kw["jersey"] = CREAM; kw["shorts"] = CREAM; kw["sock"] = CREAM; kw["glow"] = 0
    kw.pop("legs", None); kw.pop("sleeves", None); kw.pop("beanie", None)
    _PLAYER0(L, x, y, s, pose, *a, **kw)
    al = L.getchannel("A"); bb = al.getbbox()
    if not bb: return
    A = np.asarray(L).astype(np.float32); A[..., :3] = A[..., :3] * 0.12 + np.array(CREAM, np.float32) * 0.88
    L = Image.fromarray(A.astype(np.uint8))
    pad = 70; box = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(W, bb[2] + pad), min(H, bb[3] + pad))
    sub = al.crop(box)
    g = Image.new("RGBA", sub.size, (255, 214, 150, 0)); g.putalpha(sub.filter(ImageFilter.GaussianBlur(26)))
    g2 = Image.new("RGBA", sub.size, (255, 240, 210, 0)); g2.putalpha(sub.filter(ImageFilter.GaussianBlur(7)))
    img.alpha_composite(g, box[:2]); img.alpha_composite(g, box[:2]); img.alpha_composite(g2, box[:2])
    img.alpha_composite(L)

STAD_AFR = make_stadium("afr")
SNOWP = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 50).uniform(0, H), np.random.default_rng(i + 9).uniform(0.4, 1)) for i in range(140)]
def snow(d, tg, amt=1.0):
    for x0, y0, sp in SNOWP:
        y = (y0 + tg * 90 * sp) % H; x = (x0 + 30 * math.sin(tg * 0.9 + y0)) % W; r = 3 + 4 * sp
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((40, 50, 70), (240, 244, 255), amt))
def goal_ball(d, tg, k, sx, sy, gx, gy):
    v = min(1, max(0, k) / 0.35)
    bx = lerp(sx, gx, eout(v)); by = lerp(sy, gy, eout(v)) - 70 * math.sin(math.pi * v)
    ball(d, bx, by, 28 - 10 * v, WHITE, tg * 12)
    return v

# --------------------------------------------------------------- scènes (ép. 12 : Azzedine Ounahi)
def s_hook(img, d, tg, k):
    img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 250); P(img, W / 2, FEET, 250, "sad"); d = ImageDraw.Draw(img)
    snow(d, tg, 1.0)
    topsh(img); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    sc = 1 + 0.3 * (1 - eout((tg + 0.12) / 0.2))
    text(d, (W / 2, 380), "BLOQUÉ EN", int(fit("BLOQUÉ EN", 120, 1000) * sc), WHITE, BOLD, stroke=8, scol=BG)
    kk = tg - K["hook"] + 0.1; hit = 0.0
    if kk > 0:
        text(d, (W / 2, 540), "RÉSERVE ?", pop(kk, fit("RÉSERVE ?", 170, 1000), 0.25, 0.2), ORANGE, BOLD, stroke=10, scol=BG); hit = max(0, 1 - kk / 0.3)
    badge(d, 260, 720, "20 ANS", kM(tg, "a20"), GOLD, 105)
    k5 = kM(tg, "d5")
    if k5 > 0: hit = max(hit, stamp(img, "5e DIVISION", (W / 2 + 160, 720), 96, -6, k5, ICE))
    return dict(hit=hit)

def s_intro(img, d, tg, k):
    img.paste(STAD_AFR); rays(img, 0.4); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240, (90, 60, 40)); P(img, W / 2, FEET, 240, "stand"); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 300)); ball(d, hp[0] + 6, hp[1] + 10, 30 / ZF + 6, WHITE, tg * 2)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 290, "L'HISTOIRE VRAIE", 100, WHITE, k)
    TX(d, 400, "D'UN JOUEUR DE RÉSERVE", 76, AMBER, k - 0.25)
    TX(d, 560, "CASABLANCA, MAROC", 84, ORANGE, kM(tg, "casa"))
    return dict(hit=0.0)

def s_academie(img, d, tg, k):
    img.paste(CTRY_GOLD); rays(img, 0.4); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240, (40, 90, 44)); P(img, W / 2, FEET, 240, run_pose(k * 8)); d = ImageDraw.Draw(img)
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    badge(d, 180, 330, "15 ANS", kM(tg, "a15"), GOLD, 110)
    TX(d, 520, "LA GRANDE ACADÉMIE", 90, WHITE, kM(tg, "academie"))
    TX(d, 630, "DU PAYS", 80, AMBER, kM(tg, "academie") - 0.2)
    return dict(hit=0.0)

def s_strasbourg(img, d, tg, k):
    img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
    kr = kM(tg, "reserve2"); hit = 0.0
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, run_pose(k * 6) if kr <= 0 else "sad"); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 200))
    if kr <= 0: bag(d, hp[0], hp[1] + 50 / ZF, 120 / ZF)
    snow(d, tg, 1.0)
    topsh(img); d = ImageDraw.Draw(img)
    badge(d, 180, 330, "18 ANS", kM(tg, "a18"), GOLD, 110)
    TX(d, 300, "DIRECTION LA FRANCE", 84, ICE, kM(tg, "strasbourg"), x=W / 2 + 90, maxw=760)
    if kr > 0: hit = stamp(img, "ÉQUIPE RÉSERVE", (W / 2, 520), 104, -5, kr, (255, 70, 60))
    TX(d, 680, "2 SAISONS · 1 BUT", 84, WHITE, kM(tg, "seul"))
    ka = kM(tg, "aucun")
    if ka > 0: hit = max(hit, stamp(img, "0 MATCH PRO", (W / 2, 830), 120, -4, ka, ICE))
    return dict(hit=hit)

def s_avranches(img, d, tg, k):
    img.paste(ROAD); d = ImageDraw.Draw(img)
    k3 = kM(tg, "d3"); travel = max(0, k) * 1.0
    for i, (lab, bgc) in enumerate((("5e DIV.", (60, 70, 110)), ("3e DIV.", (30, 120, 70)))):
        z = 2.4 + i * 2.4 - travel
        if z > 0.6: signpost(d, W / 2 + (420 if i == 0 else -420), z, lab, bg=bgc)
    shadow(d, W / 2, FEET, 240, (30, 30, 40)); P(img, W / 2, FEET, 240, run_pose(tg * 5)); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 200)); bag(d, hp[0], hp[1] + 50 / ZF, 120 / ZF)
    rain(d, tg, 0.6)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    TX(d, 280, "POUR JOUER…", 100, WHITE, k)
    TX(d, 410, "IL PART EN 3e DIVISION", 80, AMBER, k3)
    TX(d, 520, "UN PETIT CLUB DE NORMANDIE", 62, ICE, kM(tg, "avranches"))
    return dict(hit=0.0)

def s_doute(img, d, tg, k):
    img.paste(TER_NIGHT); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, "shy"); d = ImageDraw.Draw(img)
    rain(d, tg, 1.0)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 330, "UN PAS", 130, WHITE, k)
    TX(d, 480, "EN ARRIÈRE ?", 120, ICE, kM(tg, "arriere"))
    return dict(hit=0.0)

def s_cri(img, d, tg, k):
    kb = tg - K["boom"]; kk = max(0.0, kb + 0.06); kr = kM(tg, "remonter")
    c = (W / 2, 900)
    r = eout(max(0, kr) / 1.2) * 2300 if kr > 0 else 0
    img.paste(reveal(NIGHT_ARR, GOLD_ARR, c, r)); d = ImageDraw.Draw(img)
    rays(img, min(1, max(0, kr - 0.2) / 0.5)); d = ImageDraw.Draw(img)
    speed_lines(d, c, kr, 44)
    rings(img, c, kr, 6, GOLD, 1050, 16, 0.14, 1.25); d = ImageDraw.Draw(img)
    burst(d, c[0], c[1], kr, 26, 520, (255, 240, 190), 3, 10)
    shadow(d, W / 2, FEET, 270)
    pose = POSES["shy"] if kb < 0 else (POSES["shout"] if kr < 0.3 else dict(run_pose(tg * 11), t=20))
    P(img, W / 2, FEET, 270, pose); d = ImageDraw.Draw(img)
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    hit = max(0, 1 - kk / 0.3) if kk > 0 else 0
    e = eout(kk / 0.22) if kk > 0 else 0
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, eout(max(0, kr) / 0.22))
    f1 = fit("IL DESCEND…", 130, 900); f2 = pop(kr, fit("POUR MIEUX REMONTER !", 104, 900), 0.08)
    for off, cc in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        if kb > 0: text(d, (x1 + o, 420), "IL DESCEND…", f1, cc, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
        if kr > 0: text(d, (x2 - o, 570), "POUR MIEUX REMONTER !", f2, cc if cc != WHITE else GOLD, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
    hr = max(0, 1 - kr / 0.3) if kr > 0 else 0
    return dict(hit=max(hit, hr) * 1.6, shake=max(hit, hr) * 1.9, flash=max(0, 0.9 - kr * 2.6) if kr > 0 else 0)

def s_angers(img, d, tg, k):
    ka = kM(tg, "angers"); km = kM(tg, "marque"); hit = 0.0
    if ka <= 0:
        img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
        shadow(d, W / 2, FEET, 250); P(img, W / 2, FEET, 250, run_pose(k * 8)); d = ImageDraw.Draw(img)
        topsh(img, 0.85); d = ImageDraw.Draw(img)
        TX(d, 280, "UNE SAISON PLEINE", 92, WHITE, k)
        counter(d, 450, 0, 27, kM(tg, "m27"), 0.9, 170, GOLD); TX(d, 570, "MATCHS", 70, WHITE, kM(tg, "m27") - 0.1)
        counter(d, 720, 0, 5, kM(tg, "b5"), 0.5, 150, GOLD); TX(d, 830, "BUTS", 70, WHITE, kM(tg, "b5") - 0.1)
        return dict(hit=0.0)
    img.paste(STAD_FR); d = ImageDraw.Draw(img)
    gx, gy = W / 2 + 140, 1130; goal(d, gx, gy, 0.7)
    shadow(d, W / 2 - 100, FEET, 260)
    pose = ("kick" if km < 0.4 else "up") if km > -0.1 else run_pose(k * 9)
    P(img, W / 2 - 100, FEET, 260, pose); d = ImageDraw.Draw(img)
    if km > -0.1:
        s0 = Q(W / 2 - 20, FEET); v = goal_ball(d, tg, km + 0.1, s0[0], s0[1], gx - 160, gy - 180)
        if v >= 1: burst(d, gx - 160, gy - 180, km - 0.25, 16, 240, WHITE, 2, 8)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 270, "L'ÉLITE L'APPELLE", 92, WHITE, ka)
    badge(d, 180, 420, "21 ANS", kM(tg, "a21"), GOLD, 105)
    TX(d, 430, "1er MATCH PRO…", 80, ICE, kM(tg, "a21"), x=W / 2 + 110, maxw=700)
    if km > 0: hit = stamp(img, "IL MARQUE !", (W / 2, 620), 140, -6, km, (40, 220, 120))
    return dict(hit=hit)

def s_mondial(img, d, tg, k):
    kd = kM(tg, "demi"); ke = kM(tg, "espagne"); hit = 0.0
    img.paste(STAD_ENG); d = ImageDraw.Draw(img)
    fl = np.random.default_rng(int(tg * 10))
    for _ in range(14):
        fx, fy = fl.uniform(0, W), fl.uniform(480, 890); d.ellipse((fx - 6, fy - 6, fx + 6, fy + 6), fill=(255, 255, 255))
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET - (20 * abs(math.sin(k * 6)) if kd > 0 else 0), 262, ("up" if kd > 0 else run_pose(k * 8))); d = ImageDraw.Draw(img)
    if kd > 0: confetti(d, kd * 0.9, 0.8); crowd(d, tg, up_all=True, rise=0.6)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 270, "LA COUPE DU MONDE", 96, WHITE, kM(tg, "coupe"))
    TX(d, 390, "LE MONDE LE DÉCOUVRE", 76, ICE, ke)
    if kd > 0:
        hit = stamp(img, "1re ÉQUIPE AFRICAINE", (W / 2, 560), 96, -4, kd, GOLD)
        TX(d, 700, "EN DEMI-FINALE", 96, GOLD, kd - 0.2)
    return dict(hit=hit, flash=0.3 * max(0, 1 - kd / 0.3) if kd > 0 else 0)

def s_marseille(img, d, tg, k):
    kj = kM(tg, "juin"); kb = kM(tg, "deuxbuts"); hit = 0.0
    img.paste(STAD_FR if kj <= 0 else STAD_ENG); d = ImageDraw.Draw(img)
    gx, gy = W / 2 + 140, 1130
    if kj > 0: goal(d, gx, gy, 0.7)
    shadow(d, W / 2 - 100, FEET, 260)
    pose = ("kick" if (kb % 1.2) < 0.35 else "up") if kb > 0 else run_pose(k * 8)
    P(img, W / 2 - 100, FEET, 260, pose); d = ImageDraw.Draw(img)
    if kb > 0:
        s0 = Q(W / 2 - 20, FEET); goal_ball(d, tg, kb % 1.2, s0[0], s0[1], gx - 160, gy - 180)
        confetti(d, kb * 0.9, 0.6)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 270, "UN GRAND CLUB LE RECRUTE", 80, WHITE, k)
    if kj > 0: TX(d, 410, "JUILLET 2026", 120, GOLD, kj, amp=0.3)
    if kb > 0: hit = stamp(img, "2 BUTS EN COUPE DU MONDE", (W / 2, 590), 86, -4, kb, GOLD)
    return dict(hit=hit)

def s_regard(img, d, tg, k):
    kf = kM(tg, "fierte"); hit = 0.0
    img.paste(STAD_AFR); rays(img, 0.7); d = ImageDraw.Draw(img)
    if kf > 0: confetti(d, kf)
    shadow(d, W / 2, FEET + 20, 260, (90, 60, 40))
    P(img, W / 2, FEET + 20 - (18 * abs(math.sin(tg * 7)) if kf > 0 else 0), 260, "up" if kf > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 250, "LE JOUEUR DE LA RÉSERVE…", 84, WHITE, k)
    if kf > 0: hit = stamp(img, "LA FIERTÉ D'UN PAYS", (W / 2, 420), 110, -4, kf, GOLD)
    return dict(hit=hit, flash=0.4 * max(0, 1 - kf / 0.25) if kf > 0 else 0)

def s_you(img, d, tg, k):
    kv = kM(tg, "attendant"); hit = 0.0
    img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET, 262, blend_pose(POSES["stand"], POSES["point"], eout(max(0, k) / 0.4)))
    dim(img, 0.25); topsh(img); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(150 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=8, scol=BG)
    TX(d, 470, "TU VAS RESTER SUR LE BANC", 76, WHITE, kM(tg, "attendant") - 0.6)
    if kv > 0: hit = stamp(img, "EN ATTENDANT QU'ON T'APPELLE ?", (W / 2, 620), 74, -4, kv, GOLD)
    return dict(hit=hit)

def s_abonne(img, d, tg, k):
    img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
    dim(img, 0.6); d = ImageDraw.Draw(img)
    hit = 0.0
    P(img, 200, FEET + 20, 215, "point", fixed=True); d = ImageDraw.Draw(img)
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rounded_rectangle((W / 2 - bw / 2, 420 - bh / 2, W / 2 + bw / 2, 420 + bh / 2), int(40 * sc), fill=RED)
    text(d, (W / 2 - bw / 2 + 90 * sc, 420), "+", int(130 * sc), WHITE, BOLD)
    text(d, (W / 2 + 50 * sc, 420), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE, BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = kM(tg, "demain")
    if kd > 0:
        TX(d, 660, "DEMAIN · ÉPISODE 15", 74, GOLD, kd)
        text(d, (W / 2, 770), typew("UNE AUTRE HISTOIRE VRAIE…", kd, 30), fit("UNE AUTRE HISTOIRE VRAIE…", 70, 940), WHITE, BOLD, stroke=6, scol=BG)
    return dict(hit=hit)

NUMS = [(np.random.default_rng(i).uniform(140, W - 140), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["8/10", "10/10", "6/10", "9/10", "7/10", "5/10", "10/10", "8/10", "9/10", "7/10"])]
def s_question(img, d, tg, k):
    img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
    dim(img, 0.72); d = ImageDraw.Draw(img)
    pulse = 0.0
    a = 1.0; de = tg - K["q_end"]
    if de > 0: a = max(0.0, 1 - de / 0.8)
    for x, y, s, sp in NUMS:
        yy_ = (y - tg * 50 * sp) % 700 + 720
        text(d, (x, yy_), s, 56, mix((30, 38, 56), (200, 150, 60), a), BOLD)
    text(d, (W / 2, 1000), "?", 600, mix((30, 38, 56), (120, 60, 30), a), BOLD)
    return dict(hit=0.0)

def s_logo(img, d, tg, k):
    img.paste(STAD_AMAT); dim(img, 0.9); d = ImageDraw.Draw(img)
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


# =============================================================== ép. 13 v2 (19/11/2026) — NOUVEAUX PAYSAGES (retour utilisateur : « changer de scénario, de paysage »)
# Plus de stades partout : canal d'hiver aux maisons à colombages (France de l'Est), ville blanche de Casablanca au bord de l'océan,
# plage au lever du soleil, baie à marée basse avec un rocher-village au loin (Normandie), désert de nuit avec un stade lumineux à l'horizon,
# port au coucher du soleil, toits de la ville blanche la nuit avec feux d'artifice. Lieux génériques, aucun logo/drapeau/écusson.

def _glow(img, box, col, a, blur):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(L).ellipse(box, fill=col + (a,))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(blur)))

def _stars(d, n, y1, seed=4, col=(230, 236, 255)):
    r = np.random.default_rng(seed)
    for _ in range(n):
        x, y, s = r.uniform(0, W), r.uniform(0, y1), r.uniform(1, 3.2); d.ellipse((x - s, y - s, x + s, y + s), fill=col)

def _ground(d, c0, c1, stripe=0.06):
    y = HOR; bh = 30.0; j = 0
    while y < H:
        u = (y - HOR) / (H - HOR); c = mix(c0, c1, u)
        d.rectangle((0, y, W, y + bh + 1), fill=mix(c, (0, 0, 0), stripe * (j % 2))); y += bh; bh *= 1.18; j += 1

def make_canal(mode="night"):
    """canal d'hiver : maisons à colombages aux toits pentus enneigés, fenêtres allumées, reflets dans l'eau, quai pavé enneigé"""
    night = mode == "night"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR - 60, (8, 12, 34) if night else (60, 70, 120), (44, 58, 110) if night else (200, 160, 170), 1.2)
    if night: _stars(d, 80, 500)
    _glow(img, (W - 330, 170, W - 170, 330), (230, 236, 255), 200 if night else 90, 30); d = ImageDraw.Draw(img)
    d.ellipse((W - 290, 210, W - 210, 290), fill=(240, 244, 255))
    rng = np.random.default_rng(13)
    WALLS = [(222, 196, 160), (196, 120, 96), (236, 222, 190), (170, 150, 120), (214, 170, 120), (200, 210, 214)]
    x = -60; base = HOR - 60
    while x < W + 40:
        w_ = rng.uniform(150, 230); h_ = rng.uniform(260, 380); wall = WALLS[int(rng.integers(len(WALLS)))]
        if night: wall = mix(wall, (30, 34, 60), 0.55)
        top = base - h_
        d.rectangle((x, top, x + w_, base), fill=wall)
        beam = (70, 46, 34) if not night else (34, 24, 26)
        for yy_ in np.arange(top, base, 85): d.line((x, yy_, x + w_, yy_), fill=beam, width=7)
        for xx_ in np.arange(x, x + w_ + 1, w_ / 3): d.line((xx_, top, xx_, base), fill=beam, width=7)
        for xx_ in np.arange(x, x + w_ - 10, w_ / 3):
            d.line((xx_, top, xx_ + w_ / 3, top + 85), fill=beam, width=5)
        rh = rng.uniform(150, 220)
        d.polygon([(x - 14, top), (x + w_ / 2, top - rh), (x + w_ + 14, top)], fill=(120, 60, 50) if not night else (46, 30, 40))
        d.polygon([(x - 14, top), (x + w_ / 2, top - rh), (x + w_ / 2, top - rh + 24), (x + 8, top + 2)], fill=(236, 240, 250) if night else (250, 250, 252))
        d.polygon([(x + w_ + 14, top), (x + w_ / 2, top - rh), (x + w_ / 2, top - rh + 24), (x + w_ - 8, top + 2)], fill=(206, 214, 236) if night else (230, 234, 244))
        for wy in np.arange(top + 22, base - 50, 85):
            for wx in np.arange(x + 22, x + w_ - 40, w_ / 3):
                lit = rng.random() < (0.7 if night else 0.2)
                d.rectangle((wx, wy, wx + 34, wy + 44), fill=(255, 204, 120) if lit else mix(wall, (0, 0, 0), 0.5))
        x += w_ + rng.uniform(4, 20)
    # eau du canal + reflets
    wy0, wy1 = HOR - 60, HOR + 40
    refl = img.crop((0, wy0 - (wy1 - wy0) * 3, W, wy0)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, wy1 - wy0))
    refl = Image.blend(refl.convert("RGB"), Image.new("RGB", (W, wy1 - wy0), (14, 26, 52) if night else (70, 90, 120)), 0.55).filter(ImageFilter.GaussianBlur(3))
    img.paste(refl, (0, wy0)); d = ImageDraw.Draw(img)
    for yy_ in range(wy0 + 6, wy1, 9): d.line((rng.uniform(0, W), yy_, rng.uniform(0, W), yy_), fill=(255, 214, 150, 120) if night else (230, 236, 250), width=2)
    d.rectangle((0, wy1 - 6, W, wy1 + 8), fill=(120, 126, 150) if night else (170, 170, 180))   # bord du quai
    # quai pavé enneigé
    _ground(d, (150, 160, 190) if night else (232, 236, 244), (90, 98, 130) if night else (196, 202, 220), 0.04)
    for z in np.arange(0.7, 5, 0.25):
        a, b = proj(-400, z), proj(W + 400, z); d.line((a, b), fill=(120, 128, 160) if night else (200, 204, 220), width=2)
    # lampadaires
    for xw in (-120, W + 120):
        for z in (1.4, 2.6):
            p = proj(xw, z); hh_ = 620 / z
            d.line((p[0], p[1], p[0], p[1] - hh_), fill=(30, 30, 40), width=max(3, int(12 / z)))
            _glow(img, (p[0] - 90 / z, p[1] - hh_ - 90 / z, p[0] + 90 / z, p[1] - hh_ + 90 / z), (255, 200, 120), 200, 20); d = ImageDraw.Draw(img)
            d.ellipse((p[0] - 18 / z, p[1] - hh_ - 18 / z, p[0] + 18 / z, p[1] - hh_ + 18 / z), fill=(255, 230, 170))
    return img

def make_medina(mode="gold"):
    """Casablanca : ville blanche en terrasses au bord de l'océan, palmiers ; premier plan = terrasse sur un toit"""
    night = mode == "night"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR - 120, (10, 14, 44) if night else (70, 110, 190), (60, 50, 110) if night else (255, 196, 130), 1.3)
    if night: _stars(d, 90, 480, 7)
    else:
        _glow(img, (120, 420, 520, 820), (255, 200, 120), 200, 60); d = ImageDraw.Draw(img)
        d.ellipse((250, 560, 390, 700), fill=(255, 226, 160))
    # océan à gauche
    d.rectangle((0, 700, W, HOR - 120), fill=(30, 50, 90) if night else (60, 120, 170))
    for yy_ in range(706, HOR - 120, 12): d.line((0, yy_, 520, yy_), fill=(80, 110, 160) if night else (255, 220, 170), width=1)
    # maisons blanches en escalier vers la droite
    rng = np.random.default_rng(21)
    for row in range(6):
        y0 = 640 + row * 50 - 0
        x = 380 - row * 70
        while x < W + 60:
            w_ = rng.uniform(70, 150); h_ = rng.uniform(70, 150)
            c = (236, 232, 220) if not night else (70, 74, 104)
            c = mix(c, (255, 200, 150), 0.12 * row / 5) if not night else c
            tp = 560 + row * 45 - h_ * 0.5
            d.rectangle((x, tp, x + w_, HOR - 110), fill=c)
            d.rectangle((x, tp, x + w_ * 0.25, HOR - 110), fill=mix(c, (0, 0, 0), 0.12))
            for k_ in range(int(rng.integers(1, 4))):
                wx, wy = x + rng.uniform(15, w_ - 30), tp + 18 + rng.uniform(0, 30)
                d.rectangle((wx, wy, wx + 16, wy + 22), fill=(255, 206, 120) if (night and rng.random() < 0.7) else (60, 110, 170))
            x += w_ + rng.uniform(-6, 10)
    for px, ph in ((140, 300), (930, 360), (1010, 260)):
        d.line((px, HOR - 100, px + 20, HOR - 100 - ph), fill=(60, 44, 34) if not night else (20, 18, 30), width=12)
        for a in range(0, 360, 45):
            ex = px + 20 + 120 * math.cos(math.radians(a)); ey = HOR - 100 - ph + 50 * math.sin(math.radians(a)) + 30
            d.line((px + 20, HOR - 100 - ph, ex, ey), fill=(40, 100, 60) if not night else (16, 30, 30), width=14)
    # terrasse : sol carrelé + muret
    d.rectangle((0, HOR - 120, W, HOR + 10), fill=(226, 214, 196) if not night else (64, 60, 84))
    d.rectangle((0, HOR - 120, W, HOR - 100), fill=(250, 244, 232) if not night else (90, 86, 116))
    _ground(d, (214, 150, 110) if not night else (84, 60, 70), (170, 104, 76) if not night else (50, 36, 50), 0.05)
    for xw in np.arange(-1000, W + 1100, 160):
        d.line((proj(xw, 0.55), proj(xw, 8)), fill=(190, 130, 96) if not night else (60, 44, 58), width=2)
    if night:   # guirlande lumineuse
        for i in range(40):
            xx = i * W / 39; yy = 260 + 60 * math.sin(i / 39 * math.pi)
            _glow(img, (xx - 26, yy - 26, xx + 26, yy + 26), (255, 196, 110), 180, 10)
        d = ImageDraw.Draw(img)
        for i in range(40):
            xx = i * W / 39; yy = 260 + 60 * math.sin(i / 39 * math.pi); d.ellipse((xx - 7, yy - 7, xx + 7, yy + 7), fill=(255, 236, 180))
    return img

def make_beach():
    """plage de l'Atlantique au lever du soleil, vagues, sable mouillé qui brille, deux piquets comme buts"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR - 40, (90, 110, 190), (255, 178, 120), 1.4)
    _glow(img, (W / 2 - 360, HOR - 400, W / 2 + 360, HOR + 200), (255, 200, 130), 220, 70); d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - 90, HOR - 220, W / 2 + 90, HOR - 40), fill=(255, 230, 170))
    d.rectangle((0, HOR - 120, W, HOR - 40), fill=(80, 120, 170))
    for i, yy_ in enumerate(range(HOR - 116, HOR - 40, 10)):
        d.line((W / 2 - 60 - i * 14, yy_, W / 2 + 60 + i * 14, yy_), fill=(255, 220, 160), width=3)
    _grad(d, HOR - 40, HOR + 30, (250, 250, 255), (150, 190, 210), 1.0)   # écume
    _ground(d, (232, 196, 150), (196, 150, 104), 0.03)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(W / 2 - 60, HOR + 30), (W / 2 + 60, HOR + 30), (W / 2 + 300, H), (W / 2 - 300, H)], fill=(255, 226, 170, 90))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(30))); d = ImageDraw.Draw(img)
    for xw in (W / 2 - 300, W / 2 + 300):
        a = proj(xw, 3.0); d.line((a[0], a[1], a[0], a[1] - 110), fill=(80, 60, 50), width=6)
    return img

def make_bay(mode="grey"):
    """baie à marée basse, rocher-village au loin, bancs de sable et chenaux ; premier plan = pré d'un petit club avec barrière en bois"""
    gold = mode == "gold"; night = mode == "night"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    s0, s1 = ((60, 80, 150), (255, 200, 140)) if gold else (((10, 14, 30), (40, 50, 80)) if night else ((120, 130, 150), (200, 204, 210)))
    _grad(d, 0, HOR - 40, s0, s1, 1.3)
    if night: _stars(d, 40, 400, 9)
    if gold: _glow(img, (W / 2 + 40, 420, W / 2 + 460, 840), (255, 210, 140), 220, 60); d = ImageDraw.Draw(img)
    # nuages
    rng = np.random.default_rng(31)
    C = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(C)
    for _ in range(14):
        cx, cy = rng.uniform(-100, W + 100), rng.uniform(120, 560); rw = rng.uniform(140, 300)
        dc.ellipse((cx - rw, cy - rw * 0.3, cx + rw, cy + rw * 0.3), fill=((255, 220, 180, 120) if gold else ((40, 46, 70, 150) if night else (236, 238, 242, 150))))
    img.alpha_composite(C.filter(ImageFilter.GaussianBlur(20))); d = ImageDraw.Draw(img)
    # rocher-village au loin
    rx, ry = W / 2 - 180, HOR - 70
    rock = (70, 70, 84) if not gold else (120, 96, 100)
    if night: rock = (24, 26, 40)
    d.polygon([(rx - 170, ry), (rx - 110, ry - 70), (rx - 40, ry - 110), (rx + 40, ry - 116), (rx + 110, ry - 60), (rx + 180, ry)], fill=rock)
    for i in range(9):
        hx = rx - 120 + i * 28; d.rectangle((hx, ry - 60 - 40 * math.sin(i / 8 * math.pi), hx + 22, ry - 20), fill=mix(rock, (220, 210, 200), 0.35 if not night else 0.1))
        if night: d.rectangle((hx + 6, ry - 50 - 40 * math.sin(i / 8 * math.pi), hx + 14, ry - 40 - 40 * math.sin(i / 8 * math.pi)), fill=(255, 200, 120))
    d.polygon([(rx - 40, ry - 110), (rx + 6, ry - 290), (rx + 50, ry - 112)], fill=mix(rock, (0, 0, 0), 0.15))
    d.line((rx + 6, ry - 290, rx + 6, ry - 330), fill=mix(rock, (0, 0, 0), 0.15), width=5)
    # sable mouillé + chenaux
    _grad(d, HOR - 70, HOR + 20, (190, 176, 150) if not night else (40, 44, 66), (150, 140, 120) if not night else (30, 34, 52), 1.0)
    for i in range(6):
        y = HOR - 60 + i * 14
        d.line((rng.uniform(0, 300), y, rng.uniform(500, W), y + rng.uniform(-6, 6)), fill=(220, 220, 230) if not night else (90, 100, 140), width=3)
    # pré + barrière
    t0, t1 = ((96, 160, 76), (40, 100, 46)) if gold else (((30, 52, 40), (16, 30, 24)) if night else ((84, 132, 82), (40, 86, 50)))
    _ground(d, t0, t1, 0.06)
    for xw in np.arange(-900, W + 900, 130):
        a = proj(xw, 3.2); d.line((a[0], a[1], a[0], a[1] - 50), fill=(110, 80, 60) if not night else (40, 32, 30), width=5)
    a, b = proj(-900, 3.2), proj(W + 900, 3.2)
    d.line((a[0], a[1] - 40, b[0], b[1] - 40), fill=(130, 96, 70) if not night else (46, 36, 34), width=5)
    d.line((a[0], a[1] - 20, b[0], b[1] - 20), fill=(130, 96, 70) if not night else (46, 36, 34), width=5)
    goal(d, W / 2 + 260, proj(0, 3.6)[1], 0.3)
    return img

def make_desert():
    """désert de nuit : dunes sous les étoiles, un stade moderne illuminé à l'horizon avec faisceaux"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR, (6, 8, 26), (60, 40, 90), 1.4)
    _stars(d, 160, 650, 3)
    cx, cy = W / 2 + 150, HOR - 70
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for a in (-0.5, -0.2, 0.2, 0.5):
        dl.polygon([(cx, cy - 60), (cx + 900 * math.sin(a) - 40, 0), (cx + 900 * math.sin(a) + 40, 0)], fill=(255, 230, 190, 60))
    dl.ellipse((cx - 420, cy - 260, cx + 420, cy + 120), fill=(255, 200, 120, 150))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(40))); d = ImageDraw.Draw(img)
    d.ellipse((cx - 260, cy - 110, cx + 260, cy + 30), fill=(250, 236, 210))
    d.ellipse((cx - 230, cy - 96, cx + 230, cy + 10), fill=(210, 150, 90))
    for i in range(24):
        a = i / 24 * 2 * math.pi; d.line((cx + 255 * math.cos(a), cy - 40 + 70 * math.sin(a), cx + 225 * math.cos(a), cy - 40 + 52 * math.sin(a)), fill=(120, 80, 60), width=3)
    for i, (base, amp, col) in enumerate(((HOR - 20, 60, (70, 50, 70)), (HOR + 10, 50, (96, 66, 70)))):
        pts = [(x, base - amp * math.sin(x / 300 + i * 2.1)) for x in range(0, W + 1, 20)]
        d.polygon([(0, HOR + 60)] + pts + [(W, HOR + 60)], fill=col)
    _ground(d, (150, 104, 80), (84, 56, 54), 0.04)
    for z in np.arange(0.8, 6, 0.5):
        pts = [proj(xw, z + 0.08 * math.sin(xw / 200)) for xw in range(-800, W + 800, 80)]
        d.line(pts, fill=(176, 126, 96), width=2)
    return img

def make_harbor():
    """port au coucher du soleil : mâts de voiliers, collines couvertes de maisons, quai en pierre"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR - 100, (50, 50, 120), (255, 150, 90), 1.3)
    _glow(img, (W / 2 - 300, 420, W / 2 + 300, 900), (255, 180, 110), 200, 60); d = ImageDraw.Draw(img)
    rng = np.random.default_rng(41)
    pts = [(x, 560 + 90 * math.sin(x / 260) + 40 * math.sin(x / 70)) for x in range(0, W + 1, 20)]
    d.polygon([(0, HOR - 100)] + pts + [(W, HOR - 100)], fill=(150, 104, 110))
    for _ in range(170):
        x = rng.uniform(0, W); y = rng.uniform(600 + 60 * math.sin(x / 260), HOR - 110)
        c = mix((250, 220, 190), (200, 140, 120), rng.random()); d.rectangle((x, y, x + 18, y + 14), fill=c)
    d.rectangle((0, HOR - 100, W, HOR + 30), fill=(60, 80, 130))
    for yy_ in range(HOR - 94, HOR + 30, 10): d.line((W / 2 - 300, yy_, W / 2 + 300, yy_), fill=(255, 180, 110), width=2)
    for i in range(11):
        bx = 40 + i * 98 + rng.uniform(-10, 10); by = HOR + 10
        d.polygon([(bx - 34, by - 18), (bx + 34, by - 18), (bx + 24, by), (bx - 24, by)], fill=(240, 240, 240))
        d.line((bx, by - 18, bx, by - 220 - rng.uniform(0, 60)), fill=(40, 34, 40), width=3)
    _ground(d, (196, 170, 140), (130, 110, 96), 0.05)
    for z in np.arange(0.6, 5, 0.35):
        d.line((proj(-800, z), proj(W + 800, z)), fill=(160, 136, 112), width=2)
    return img

CANAL_N = make_canal("night"); MEDINA_G = make_medina("gold"); MEDINA_N = make_medina("night"); BEACH = make_beach()
BAY_GREY = make_bay("grey"); BAY_N = make_bay("night"); BAY_G = make_bay("gold"); DESERT = make_desert(); HARBOR = make_harbor()
BAYN_ARR = np.asarray(BAY_N.convert("RGB")).astype(np.float32); BAYG_ARR = np.asarray(BAY_G.convert("RGB")).astype(np.float32)

def fireworks(d, tg, amt=1.0):
    for i in range(6):
        ph = (tg * 0.7 + i * 0.37) % 1.6
        if ph > 1.0: continue
        r_ = np.random.default_rng(i * 7 + int((tg * 0.7 + i * 0.37) / 1.6))
        cx, cy = r_.uniform(140, W - 140), r_.uniform(200, 620); col = [(255, 200, 80), (255, 90, 90), (120, 220, 255), (140, 255, 160)][i % 4]
        rad = 40 + 220 * eout(ph)
        c2 = mix((10, 10, 20), col, amt * (1 - ph * 0.8))
        for a in range(0, 360, 20):
            x2 = cx + rad * math.cos(math.radians(a)); y2 = cy + rad * math.sin(math.radians(a)) + 40 * ph * ph
            d.ellipse((x2 - 5, y2 - 5, x2 + 5, y2 + 5), fill=c2)

def train(img, d, tg, k):
    """train qui file sur le pont au fond (départ pour la France)"""
    x0 = lerp(W + 100, -1400, ease(k / 3.0)); y = HOR - 150
    for i in range(5):
        x = x0 + i * 260
        d.rounded_rectangle((x, y - 90, x + 250, y), 16, fill=(220, 226, 236))
        for j in range(4): d.rectangle((x + 20 + j * 56, y - 74, x + 60 + j * 56, y - 44), fill=(255, 210, 130))
        d.rectangle((x, y - 22, x + 250, y - 12), fill=(232, 120, 40))

# --------------------------------------------------------------- scènes v2 (mêmes moments, nouveaux décors)
def s_hook(img, d, tg, k):
    img.paste(CANAL_N); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 250); P(img, W / 2, FEET, 250, "sad"); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 200)); bag(d, hp[0] + 40 / ZF, hp[1] + 60 / ZF, 120 / ZF)
    snow(d, tg, 1.0)
    topsh(img); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    sc = 1 + 0.3 * (1 - eout((tg + 0.12) / 0.2))
    text(d, (W / 2, 380), "BLOQUÉ EN", int(fit("BLOQUÉ EN", 120, 1000) * sc), WHITE, BOLD, stroke=8, scol=BG)
    kk = tg - K["hook"] + 0.1; hit = 0.0
    if kk > 0:
        text(d, (W / 2, 540), "RÉSERVE ?", pop(kk, fit("RÉSERVE ?", 170, 1000), 0.25, 0.2), ORANGE, BOLD, stroke=10, scol=BG); hit = max(0, 1 - kk / 0.3)
    badge(d, 260, 720, "20 ANS", kM(tg, "a20"), GOLD, 105)
    k5 = kM(tg, "d5")
    if k5 > 0: hit = max(hit, stamp(img, "5e DIVISION", (W / 2 + 160, 720), 96, -6, k5, ICE))
    return dict(hit=hit)

def s_intro(img, d, tg, k):
    img.paste(MEDINA_G); rays(img, 0.35); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240, (150, 96, 70)); P(img, W / 2, FEET, 240, run_pose(tg * 6) if WALK else "stand"); d = ImageDraw.Draw(img)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 290, "L'HISTOIRE VRAIE", 100, WHITE, k)
    TX(d, 400, "D'UN JOUEUR DE RÉSERVE", 76, AMBER, k - 0.25)
    TX(d, 560, "CASABLANCA, MAROC", 84, ORANGE, kM(tg, "casa"))
    return dict(hit=0.0)

def s_academie(img, d, tg, k):
    img.paste(BEACH); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240, (170, 120, 80)); P(img, W / 2, FEET, 240, run_pose(k * 8)); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 200)); ball(d, Q(W / 2 + 70, FEET)[0], Q(W / 2 + 70, FEET)[1] - 20 / ZF, 30 / ZF + 4, WHITE, tg * 9)
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    badge(d, 180, 330, "15 ANS", kM(tg, "a15"), GOLD, 110)
    TX(d, 520, "LA GRANDE ACADÉMIE", 90, WHITE, kM(tg, "academie"))
    TX(d, 630, "DU PAYS", 80, AMBER, kM(tg, "academie") - 0.2)
    return dict(hit=0.0)

def s_strasbourg(img, d, tg, k):
    img.paste(CANAL_N); d = ImageDraw.Draw(img)
    train(img, d, tg, k); d = ImageDraw.Draw(img)
    kr = kM(tg, "reserve2"); hit = 0.0
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, run_pose(k * 6) if kr <= 0 else "sad", winter=True); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 200))
    if kr <= 0: bag(d, hp[0], hp[1] + 50 / ZF, 120 / ZF)
    snow(d, tg, 1.0)
    topsh(img); d = ImageDraw.Draw(img)
    badge(d, 180, 330, "18 ANS", kM(tg, "a18"), GOLD, 110)
    TX(d, 300, "DIRECTION LA FRANCE", 84, ICE, kM(tg, "strasbourg"), x=W / 2 + 90, maxw=760)
    if kr > 0: hit = stamp(img, "ÉQUIPE RÉSERVE", (W / 2, 520), 104, -5, kr, (255, 70, 60))
    TX(d, 680, "2 SAISONS · 1 BUT", 84, WHITE, kM(tg, "seul"))
    ka = kM(tg, "aucun")
    if ka > 0: hit = max(hit, stamp(img, "0 MATCH PRO", (W / 2, 830), 120, -4, ka, ICE))
    return dict(hit=hit)

def s_avranches(img, d, tg, k):
    img.paste(BAY_GREY); d = ImageDraw.Draw(img)
    k3 = kM(tg, "d3")
    shadow(d, W / 2, FEET, 240, (30, 50, 30)); P(img, W / 2, FEET, 240, run_pose(tg * 5)); d = ImageDraw.Draw(img)
    hp = JT.get("rh", (W / 2, FEET - 200)); bag(d, hp[0], hp[1] + 50 / ZF, 120 / ZF)
    rain(d, tg, 0.5)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    TX(d, 280, "POUR JOUER…", 100, WHITE, k)
    TX(d, 410, "IL PART EN 3e DIVISION", 80, AMBER, k3)
    TX(d, 520, "UN PETIT CLUB DE NORMANDIE", 62, ICE, kM(tg, "avranches"))
    return dict(hit=0.0)

def s_doute(img, d, tg, k):
    img.paste(BAY_N); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, "shy"); d = ImageDraw.Draw(img)
    rain(d, tg, 1.0)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 330, "UN PAS", 130, WHITE, k)
    TX(d, 480, "EN ARRIÈRE ?", 120, ICE, kM(tg, "arriere"))
    return dict(hit=0.0)

def s_cri(img, d, tg, k):
    kb = tg - K["boom"]; kk = max(0.0, kb + 0.06); kr = kM(tg, "remonter")
    c = (W / 2, 900)
    r = eout(max(0, kr) / 1.2) * 2300 if kr > 0 else 0
    img.paste(reveal(BAYN_ARR, BAYG_ARR, c, r)); d = ImageDraw.Draw(img)
    rays(img, min(1, max(0, kr - 0.2) / 0.5)); d = ImageDraw.Draw(img)
    speed_lines(d, c, kr, 44)
    rings(img, c, kr, 6, GOLD, 1050, 16, 0.14, 1.25); d = ImageDraw.Draw(img)
    burst(d, c[0], c[1], kr, 26, 520, (255, 240, 190), 3, 10)
    shadow(d, W / 2, FEET, 270)
    pose = POSES["shy"] if kb < 0 else (POSES["shout"] if kr < 0.3 else dict(run_pose(tg * 11), t=20))
    P(img, W / 2, FEET, 270, pose); d = ImageDraw.Draw(img)
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    hit = max(0, 1 - kk / 0.3) if kk > 0 else 0
    e = eout(kk / 0.22) if kk > 0 else 0
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, eout(max(0, kr) / 0.22))
    f1 = fit("IL DESCEND…", 130, 900); f2 = pop(kr, fit("POUR MIEUX REMONTER !", 104, 900), 0.08)
    for off, cc in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        if kb > 0: text(d, (x1 + o, 420), "IL DESCEND…", f1, cc, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
        if kr > 0: text(d, (x2 - o, 570), "POUR MIEUX REMONTER !", f2, cc if cc != WHITE else GOLD, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
    hr = max(0, 1 - kr / 0.3) if kr > 0 else 0
    return dict(hit=max(hit, hr) * 1.6, shake=max(hit, hr) * 1.9, flash=max(0, 0.9 - kr * 2.6) if kr > 0 else 0)

_old_angers = s_angers
def s_angers(img, d, tg, k):
    if kM(tg, "angers") <= 0:
        img.paste(BAY_G); d = ImageDraw.Draw(img)
        shadow(d, W / 2, FEET, 250, (40, 90, 40)); P(img, W / 2, FEET, 250, run_pose(k * 8)); d = ImageDraw.Draw(img)
        topsh(img, 0.85); d = ImageDraw.Draw(img)
        TX(d, 280, "UNE SAISON PLEINE", 92, WHITE, k)
        counter(d, 450, 0, 27, kM(tg, "m27"), 0.9, 170, GOLD); TX(d, 570, "MATCHS", 70, WHITE, kM(tg, "m27") - 0.1)
        counter(d, 720, 0, 5, kM(tg, "b5"), 0.5, 150, GOLD); TX(d, 830, "BUTS", 70, WHITE, kM(tg, "b5") - 0.1)
        return dict(hit=0.0)
    return _old_angers(img, d, tg, k)

def s_mondial(img, d, tg, k):
    kd = kM(tg, "demi"); ke = kM(tg, "espagne"); hit = 0.0
    img.paste(DESERT); d = ImageDraw.Draw(img)
    fl = np.random.default_rng(int(tg * 10))
    for _ in range(10):
        fx, fy = fl.uniform(W / 2 - 100, W / 2 + 400), fl.uniform(HOR - 180, HOR - 40); d.ellipse((fx - 5, fy - 5, fx + 5, fy + 5), fill=(255, 255, 255))
    shadow(d, W / 2, FEET, 262, (70, 44, 40))
    P(img, W / 2, FEET - (20 * abs(math.sin(k * 6)) if kd > 0 else 0), 262, ("up" if kd > 0 else run_pose(k * 8))); d = ImageDraw.Draw(img)
    if kd > 0: confetti(d, kd * 0.9, 0.8)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 270, "LA COUPE DU MONDE", 96, WHITE, kM(tg, "coupe"))
    TX(d, 390, "LE MONDE LE DÉCOUVRE", 76, ICE, ke)
    if kd > 0:
        hit = stamp(img, "1re ÉQUIPE AFRICAINE", (W / 2, 560), 96, -4, kd, GOLD)
        TX(d, 700, "EN DEMI-FINALE", 96, GOLD, kd - 0.2)
    return dict(hit=hit, flash=0.3 * max(0, 1 - kd / 0.3) if kd > 0 else 0)

def s_marseille(img, d, tg, k):
    kj = kM(tg, "juin"); kb = kM(tg, "deuxbuts"); hit = 0.0
    img.paste(HARBOR if kj <= 0 else STAD_ENG); d = ImageDraw.Draw(img)
    gx, gy = W / 2 + 140, 1130
    if kj > 0: goal(d, gx, gy, 0.7)
    shadow(d, W / 2 - 100, FEET, 260)
    pose = ("kick" if (kb % 1.2) < 0.35 else "up") if kb > 0 else run_pose(k * 8)
    P(img, W / 2 - 100, FEET, 260, pose); d = ImageDraw.Draw(img)
    if kb > 0:
        s0 = Q(W / 2 - 20, FEET); goal_ball(d, tg, kb % 1.2, s0[0], s0[1], gx - 160, gy - 180)
        confetti(d, kb * 0.9, 0.6)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 270, "UN GRAND CLUB LE RECRUTE", 80, WHITE, k)
    if kj > 0: TX(d, 410, "JUILLET 2026", 120, GOLD, kj, amp=0.3)
    if kb > 0: hit = stamp(img, "2 BUTS EN COUPE DU MONDE", (W / 2, 590), 86, -4, kb, GOLD)
    return dict(hit=hit)

def s_regard(img, d, tg, k):
    kf = kM(tg, "fierte"); hit = 0.0
    img.paste(MEDINA_N); d = ImageDraw.Draw(img)
    fireworks(d, tg, 1.0 if kf > 0 else 0.5)
    shadow(d, W / 2, FEET + 20, 260, (40, 30, 40))
    P(img, W / 2, FEET + 20 - (18 * abs(math.sin(tg * 7)) if kf > 0 else 0), 260, "up" if kf > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 250, "LE JOUEUR DE LA RÉSERVE…", 84, WHITE, k)
    if kf > 0: hit = stamp(img, "LA FIERTÉ D'UN PAYS", (W / 2, 420), 110, -4, kf, GOLD)
    return dict(hit=hit, flash=0.4 * max(0, 1 - kf / 0.25) if kf > 0 else 0)

def s_you(img, d, tg, k):
    kv = kM(tg, "attendant"); hit = 0.0
    img.paste(CANAL_N); d = ImageDraw.Draw(img)
    snow(d, tg, 0.7)
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET, 262, blend_pose(POSES["stand"], POSES["point"], eout(max(0, k) / 0.4)))
    dim(img, 0.25); topsh(img); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(150 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=8, scol=BG)
    TX(d, 470, "TU VAS RESTER SUR LE BANC", 76, WHITE, kM(tg, "attendant") - 0.6)
    if kv > 0: hit = stamp(img, "EN ATTENDANT QU'ON T'APPELLE ?", (W / 2, 620), 74, -4, kv, GOLD)
    return dict(hit=hit)

STAD_AMAT = MEDINA_N   # fonds des scènes abonne / question / logo : toits de la ville la nuit (au lieu du stade)

SCENES = {"hook": s_hook, "intro": s_intro, "academie": s_academie, "strasbourg": s_strasbourg, "avranches": s_avranches, "doute": s_doute, "cri": s_cri,
          "angers": s_angers, "mondial": s_mondial, "marseille": s_marseille, "regard": s_regard, "you": s_you, "abonne": s_abonne, "question": s_question, "logo": s_logo}
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

def post(arr, tg, zoom, shake, flash, shot=0, cur=0):
    a = arr.astype(np.float32)
    # étalonnage ciné : ombres sarcelle, hautes lumières orangées, contraste
    lum = a.mean(axis=2, keepdims=True) / 255.0
    a = a * (1 - 0.18 * (1 - lum) * np.array([0.6, 0.0, -0.5], np.float32)) * (1 + 0.12 * lum * np.array([0.5, 0.15, -0.35], np.float32))
    a = (a - 128) * 1.12 + 128
    # léger flou de profondeur sur le haut de l'image en plan serré
    if shot:
        b = cv2.GaussianBlur(a, (0, 0), 4)
        m = np.clip((H * 0.42 - yy) / (H * 0.25), 0, 1)[..., None]
        a = a * (1 - 0.7 * m) + b * 0.7 * m
    # fuite de lumière chaude qui balaie
    lx = W * (0.5 + 0.6 * math.sin(tg * 0.35 + cur))
    leak = np.exp(-(((xx - lx) / (W * 0.35)) ** 2 + ((yy - H * 0.2) / (H * 0.35)) ** 2))[..., None]
    a = a + 38 * leak * np.array([1.0, 0.55, 0.15], np.float32)
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

WORDS = json.load(open("words.json"))["words"]
KAR_PENDING = []
def SC_TYPE(i): return SCN[i]["type"]
CHUNKS = []
_cur = []
for w in WORDS:
    _cur.append(w)
    if len(_cur) == 3 or w["text"][-1] in ".?!,:…":
        CHUNKS.append(_cur); _cur = []
if _cur: CHUNKS.append(_cur)
YEL = (255, 214, 10)
def karaoke(tg):
    for ch in CHUNKS:
        if ch[0]["start"] - 0.02 <= tg < ch[-1]["end"] + 0.12:
            break
    else:
        return None
    size = 92; font = F(BOLD, size); d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    ws = [w["text"].upper() for w in ch]
    while sum(d.textlength(x, font=font) for x in ws) + 30 * (len(ws) - 1) > 980 and size > 50:
        size -= 6; font = F(BOLD, size)
    tw = sum(d.textlength(x, font=font) for x in ws) + 30 * (len(ws) - 1)
    im = Image.new("RGBA", (W, int(size * 1.6)), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    x = (W - tw) / 2; act = None
    for w, txt in zip(ch, ws):
        on = w["start"] <= tg < (w["end"] + 0.05)
        col = YEL if on else (255, 255, 255)
        if on: act = w
        dr.text((x, size * 0.2), txt, font=font, fill=col + (255,), stroke_width=10, stroke_fill=(0, 0, 0, 255))
        x += d.textlength(txt, font=font) + 30
    sc = 1.0
    if act is not None: sc = 1.0 + 0.08 * math.exp(-(tg - act["start"]) * 14)
    return (im, H * 0.70, sc)

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
            if not (K["q_line1"] - 0.05 <= tg < K["q_cta"] - 0.3):
                kar = karaoke(tg)
                if kar is not None: KAR_PENDING.append(kar)
        # coupes rapides : recadrage serré / large qui alterne toutes les ~1,8 s dans une même scène
        shot = int(lt / 1.8) % 2 if SC_TYPE(cur) not in ("question", "logo", "abonne") else 0
        zoom *= 1.0 + 0.08 * shot
        arr = post(np.asarray(img.convert("RGB")), tg, zoom, shake, R.get("flash", 0.0), shot, cur)
        if KAR_PENDING:
            im2 = Image.fromarray(arr).convert("RGBA")
            for L, cy, sc in KAR_PENDING: paste(im2, L, cy, 1.0, sc)
            KAR_PENDING.clear(); arr = np.asarray(im2.convert("RGB"))
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
    if typ == "hook":       return _seg(k, [(0, 1.05, 0, 0), (3.5, 1.35, 0, 0)]) + (False,)
    if typ == "intro":      return _seg(k, [(0, 2.6, -250, 0), (2.4, 1.05, 100, 0)]) + (k < 2.4,)
    if typ == "academie":   return _seg(k, [(0, 0.95, 280, 0), (2.6, 2.2, -200, 0)]) + (False,)
    if typ == "strasbourg":
        r = MK_("reserve2") - st
        if k < r: return _seg(k, [(0, 2.8, -200, 0), (r, 1.2, 80, 0)]) + (False,)
        return _seg(k, [(r, 1.2, 80, 0), (r + 2, 1.5, 80, 0)]) + (False,)
    if typ == "avranches":  return (1.05 + 0.08 * math.sin(k * 2), 0.0, 0.0, 0.0, False)
    if typ == "doute":      return _seg(k, [(0, 1.0, 0, 0), (2.0, 1.4, 0, 0)]) + (False,)
    if typ == "cri":
        r = MK_("remonter") - st
        return _seg(k, [(0, 1.8, 0, 0), (r, 1.8, 0, 0), (r + 1.1, 0.85, 0, 0)]) + (False,)
    if typ == "angers":
        a = MK_("angers") - st
        if k < a: return _seg(k, [(0, 2.4, -260, 0), (a, 1.1, 120, 0)]) + (False,)
        m = MK_("marque") - st
        return _seg(k, [(a, 2.6, 300, 0), (m - 0.1, 1.1, 0, 0)]) + (False,)
    if typ == "mondial":    return _seg(k, [(0, 2.6, -200, 0), (3.0, 1.0, 0, 0)]) + (False,)
    if typ == "marseille":  return _seg(k, [(0, 2.4, 260, 0), (2.5, 1.1, 0, 0)]) + (False,)
    if typ == "regard":     return _seg(k, [(0, 2.0, 0, 0), (2.4, 1.0, 0, 0)]) + (k < 2.4,)
    if typ == "you":        return _seg(k, [(0, 1.35, -150, 0), (2.0, 0.88, 60, 0)]) + (False,)
    return (1.0, 0.0, 0.0, 0.0, False)

def CAMF(typ, k, tg):
    hh = (6 * math.sin(tg * 2.1), 5 * math.sin(tg * 1.7 + 1))
    dur = 3.0
    for s_ in SCN:
        if s_["type"] == typ: dur = s_["end"] - s_["start"]
    u = ease(k / max(0.5, dur))
    if typ == "hook":       return (lerp(1.3, 1.1, u), lerp(60, -40, u) + hh[0], lerp(60, 0, u) + hh[1], lerp(0.07, -0.03, u), -0.02, lerp(-1.5, 0, u))
    if typ == "intro":      return (lerp(1.08, 1.18, u), lerp(-90, 60, u), hh[1], lerp(0.08, -0.04, u), -0.04, 0.0)
    if typ == "academie":   return (lerp(1.06, 1.2, u), lerp(70, -70, u) + hh[0], lerp(40, -20, u), lerp(-0.07, 0.07, u), 0.06, 0.0)
    if typ == "strasbourg": return (lerp(1.06, 1.2, u), hh[0] * 2, lerp(0, -40, u), lerp(-0.06, 0.06, u), 0.0, 1.0 * math.sin(tg * 2))
    if typ == "avranches":  return (1.1, hh[0], hh[1] + lerp(0, 40, u), 0.05 * math.sin(k * 0.7), -0.04, 0.0)
    if typ == "doute":      return (lerp(1.22, 1.08, u), lerp(80, -60, u) + hh[0], hh[1], lerp(-0.08, 0.06, u), -0.05, lerp(1.5, 0, u))
    if typ == "cri":
        kb = max(0.0, tg - M("remonter", 99))
        orb = math.sin(min(1, kb / 1.8) * math.pi) * 0.13
        return (1.08 + 0.2 * math.exp(-kb * 3) if kb > 0 else 1.1, hh[0] * 2, hh[1], orb, 0.06 if kb > 0 else 0.0, 3 * math.sin(kb * 4) * math.exp(-kb * 2))
    if typ == "angers":
        m = tg - M("marque", 99)
        if m > 0: return (lerp(1.08, 1.22, ease(m / 2.5)), hh[0], lerp(0, 70, ease(m / 2.5)), 0.08 * math.sin(m), 0.08, 0.0)
        return (lerp(1.2, 1.08, u), lerp(-80, 40, u) + hh[0], hh[1], lerp(-0.08, 0.04, u), 0.0, 1.2 * math.sin(tg * 3))
    if typ == "mondial":    return (lerp(1.08, 1.2, u), lerp(100, -80, u) + hh[0], hh[1], lerp(0.07, -0.07, u), 0.0, 0.0)
    if typ == "marseille":  return (lerp(1.2, 1.08, u), lerp(-80, 40, u) + hh[0], hh[1], lerp(-0.08, 0.04, u), 0.04, 0.0)
    if typ == "regard":     return (lerp(1.18, 1.06, u), hh[0], lerp(-40, 30, u), lerp(0.08, -0.06, u), 0.05, 0.0)
    if typ == "you":        return (lerp(1.06, 1.16, u), lerp(-60, 30, u) + hh[0], hh[1], lerp(0.06, -0.04, u), 0.0, 0.0)
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


# =============================================================== ép. 18 (25/11/2026) — Eliud Kipchoge « Pas sélectionné ? » (athlétisme, hors football)
# Décors NOUVEAUX : hauts plateaux du Kenya (collines vertes, rangs de thé, piste de terre rouge, acacias, toits de tôle) aube / nuit / doré,
# STADE D'ATHLÉTISME (piste rouge en perspective, couloirs, projecteurs) nuit / pluie / doré, grande AVENUE DE MARATHON (immeubles, barrières,
# bornes kilométriques, arche d'arrivée générique) aube / doré. Aucun logo, drapeau, nom de marque ni de course à l'écran.
RED2 = (255, 70, 60)
SILVER = (214, 220, 230); BRONZE = (205, 127, 50)
RAINP = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 77).uniform(0, H), np.random.default_rng(i + 5).uniform(0.5, 1)) for i in range(170)]

def rainfall(d, tg, amt=1.0):
    for x0, y0, sp in RAINP:
        y = (y0 + tg * 1500 * sp) % H; x = (x0 - (y - y0) * 0.12) % W
        d.line((x, y, x - 8, y + 46 * sp), fill=mix((40, 50, 70), (190, 205, 235), amt * sp), width=2)

def acacia(d, x, by, s, c):
    d.line((x, by, x + 10 * s, by - 160 * s), fill=c, width=max(2, int(12 * s)))
    d.line((x + 10 * s, by - 150 * s, x - 60 * s, by - 210 * s), fill=c, width=max(2, int(8 * s)))
    d.line((x + 10 * s, by - 150 * s, x + 80 * s, by - 215 * s), fill=c, width=max(2, int(8 * s)))
    d.ellipse((x - 170 * s, by - 275 * s, x + 190 * s, by - 190 * s), fill=c)

def make_highlands(mode="dawn"):
    """hauts plateaux du Kenya : collines en couches, rangs de thé, maisons à toit de tôle, acacias, piste de terre rouge vers l'horizon"""
    night = mode == "night"; gold = mode == "gold"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    top = (16, 18, 52) if night else ((120, 70, 120) if gold else (70, 90, 160))
    bot = (50, 40, 90) if night else ((255, 190, 110) if gold else (255, 176, 120))
    _grad(d, 0, HOR, top, bot, 1.1)
    if night: _stars(d, 120, 560, 31)
    else:
        _glow(img, (W / 2 - 300, HOR - 520, W / 2 + 300, HOR + 60), (255, 200, 130), 220, 80); d = ImageDraw.Draw(img)
        d.ellipse((W / 2 - 95, HOR - 300, W / 2 + 95, HOR - 110), fill=(255, 226, 160))
    rng = np.random.default_rng(3)
    layers = [((70, 90, 120), (24, 30, 60), (150, 110, 120), 160), ((50, 90, 80), (16, 28, 40), (120, 110, 70), 90), ((40, 110, 60), (12, 30, 30), (110, 130, 50), 30)]
    for li, (cd, cn, cg, base) in enumerate(layers):
        c = cn if night else (cg if gold else cd)
        pts = [(0, H)]
        for x in range(0, W + 41, 40):
            pts.append((x, HOR - base + 50 * math.sin(x / (170 + 60 * li) + li * 2) + 22 * math.sin(x / 61 + li)))
        pts.append((W, H)); d.polygon(pts, fill=c)
        if li == 1:   # maisons à toit de tôle sur la colline du milieu
            for hx in (180, 300, 760, 880):
                hy = HOR - base + 50 * math.sin(hx / 230 + 2) + 22 * math.sin(hx / 61 + 1) + 6
                d.rectangle((hx - 34, hy - 40, hx + 34, hy), fill=(70, 50, 40) if not night else (30, 26, 30))
                d.polygon([(hx - 44, hy - 38), (hx, hy - 66), (hx + 44, hy - 38)], fill=(170, 176, 186) if not night else (60, 64, 80))
                if night: d.rectangle((hx - 8, hy - 28, hx + 6, hy - 12), fill=(255, 200, 110))
    # sol : champs de thé (rangs verts) de part et d'autre d'une piste de terre rouge
    _ground(d, (60, 120, 60) if not night else (18, 36, 30), (30, 80, 40) if not night else (8, 20, 18), 0.0)
    if gold: _ground(d, (150, 140, 60), (90, 90, 40), 0.0)
    rowc = (40, 96, 46) if not night else (12, 28, 22)
    for xw in np.arange(-2400, W + 2500, 150):
        d.line((proj(xw, 0.55), proj(xw, 12)), fill=rowc, width=6)
    road = (196, 96, 56) if not night else (70, 40, 34)
    if gold: road = (230, 130, 70)
    d.polygon([proj(W / 2 - 230, 0.5), proj(W / 2 + 230, 0.5), proj(W / 2 + 230, 14), proj(W / 2 - 230, 14)], fill=road)
    for z in np.arange(0.7, 12, 0.5):   # ornières
        a = proj(W / 2 - 90, z); b = proj(W / 2 - 90, z + 0.25); d.line((a, b), fill=mix(road, (0, 0, 0), 0.18), width=max(1, int(6 / z)))
        a = proj(W / 2 + 90, z); b = proj(W / 2 + 90, z + 0.25); d.line((a, b), fill=mix(road, (0, 0, 0), 0.18), width=max(1, int(6 / z)))
    tc = (30, 40, 30) if not night else (8, 10, 18)
    if gold: tc = (70, 50, 40)
    for xw, z in ((-420, 1.5), (W + 380, 2.0), (-200, 4.0), (W + 160, 5.5)):
        q = proj(xw, z); acacia(d, q[0], q[1], 1.6 / z, tc)
    if not night:   # brume du matin
        _glow(img, (-100, HOR - 120, W + 100, HOR + 120), (255, 236, 220), 70, 40)
    return img

def make_track(mode="night"):
    """stade d'athlétisme : piste rouge en perspective (couloirs blancs), pelouse intérieure, tribunes à points, projecteurs"""
    gold = mode == "gold"; rainy = mode == "rain"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR, (8, 10, 26) if not gold else (90, 60, 110), (26, 30, 60) if not gold else (255, 170, 100), 1.1)
    if gold:
        _glow(img, (W / 2 - 260, HOR - 420, W / 2 + 260, HOR + 40), (255, 214, 150), 220, 70); d = ImageDraw.Draw(img)
    rng = np.random.default_rng(5)
    for row in range(10):   # tribunes
        y = HOR - 330 + row * 28
        for xx in np.arange(rng.uniform(0, 18), W, 20):
            if gold or rng.random() < (0.25 if rainy else 0.45):
                c = mix((255, 220, 160), (210, 90, 70), rng.random()) if gold else (44, 50, 78)
                d.ellipse((xx, y, xx + 9, y + 11), fill=c)
    d.rectangle((0, HOR - 50, W, HOR), fill=(30, 34, 56) if not gold else (120, 70, 60))
    for xx, hh in ((110, 560), (W - 110, 560)):   # pylônes
        d.line((xx, HOR - 50, xx, HOR - hh), fill=(40, 44, 60), width=12)
        d.rectangle((xx - 70, HOR - hh - 60, xx + 70, HOR - hh), fill=(50, 54, 70))
        on = not rainy or True
        _glow(img, (xx - 170, HOR - hh - 160, xx + 170, HOR - hh + 90), (255, 250, 230) if not gold else (255, 230, 180), 200 if not rainy else 120, 30); d = ImageDraw.Draw(img)
        for i in range(3): d.rectangle((xx - 60 + i * 42, HOR - hh - 50, xx - 26 + i * 42, HOR - hh - 10), fill=(255, 252, 235))
    # sol : pelouse intérieure loin, piste rouge au premier plan
    _ground(d, (30, 90, 50) if not gold else (110, 150, 60), (14, 50, 30) if not gold else (70, 110, 40), 0.05)
    tr = (178, 58, 44) if not gold else (230, 96, 60)
    if rainy: tr = (120, 40, 36)
    d.polygon([proj(-2600, 0.5), proj(W + 2600, 0.5), proj(W + 2600, 3.2), proj(-2600, 3.2)], fill=tr)
    lc = (240, 240, 236) if not gold else (255, 244, 220)
    for z in (0.62, 0.8, 1.05, 1.4, 1.9, 2.6, 3.2):   # couloirs (lignes horizontales en perspective)
        d.line((proj(-2600, z), proj(W + 2600, z)), fill=lc, width=max(2, int(7 / z)))
    a = proj(W / 2 + 140, 0.5); b = proj(W / 2 + 140, 3.2); d.line((a, b), fill=lc, width=8)   # ligne d'arrivée
    if rainy:   # reflets des projecteurs sur la piste mouillée
        for xx in (110, W - 110):
            _glow(img, (xx - 60, HOR + 60, xx + 60, H - 200), (255, 240, 220), 40, 30)
    return img

def make_avenue(mode="dawn"):
    """grande avenue de marathon : immeubles des deux côtés, barrières, spectateurs, arche d'arrivée générique au loin"""
    gold = mode == "gold"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR, (70, 90, 160) if not gold else (110, 70, 120), (255, 190, 140) if not gold else (255, 200, 120), 1.1)
    _glow(img, (W / 2 - 220, HOR - 380, W / 2 + 220, HOR + 20), (255, 224, 170), 200, 60); d = ImageDraw.Draw(img)
    rng = np.random.default_rng(14)
    for side in (-1, 1):   # immeubles en perspective
        for i, z in enumerate(np.arange(1.0, 9.0, 0.9)):
            z2 = z + 0.8
            xin = W / 2 + side * 330; xout = W / 2 + side * 1500
            a = proj(xin, z); b = proj(xin, z2); hb = 900 + 300 * rng.random()
            c = mix((70, 64, 90), (200, 150, 140), 0.55 if gold else 0.35) if i % 2 else mix((60, 60, 84), (190, 140, 130), 0.5 if gold else 0.3)
            ta = (a[0], HOR - (HOR - a[1]) * 0 - hb / z); tb = (b[0], HOR - hb / z2)
            d.polygon([a, b, tb, ta], fill=c)
            for f in np.arange(0.15, 0.95, 0.12):   # fenêtres
                ya = lerp(a[1], ta[1], f); yb = lerp(b[1], tb[1], f)
                d.line(((a[0] * 0.8 + b[0] * 0.2), ya * 0.8 + yb * 0.2, (a[0] * 0.3 + b[0] * 0.7), ya * 0.3 + yb * 0.7), fill=(255, 220, 160) if gold else (220, 210, 200), width=max(1, int(8 / z)))
    _ground(d, (84, 86, 100) if not gold else (170, 130, 110), (50, 52, 64) if not gold else (120, 90, 80), 0.0)
    d.polygon([proj(W / 2 - 320, 0.5), proj(W / 2 + 320, 0.5), proj(W / 2 + 320, 12), proj(W / 2 - 320, 12)], fill=(64, 66, 80) if not gold else (150, 110, 96))
    for z in np.arange(0.6, 12, 0.7):   # ligne bleue centrale (tracé) en pointillés
        d.line((proj(W / 2, z), proj(W / 2, z + 0.35)), fill=(90, 170, 255), width=max(2, int(10 / z)))
    for side in (-1, 1):   # barrières + spectateurs
        for z in np.arange(0.7, 9, 0.35):
            q = proj(W / 2 + side * 330, z); h_ = 70 / z
            d.line((q[0], q[1], q[0], q[1] - h_), fill=(200, 200, 210), width=max(1, int(4 / z)))
            for j in range(2):
                cc = mix((255, 200, 140), (60, 70, 120), rng.random()) if gold else mix((40, 44, 70), (150, 120, 140), rng.random())
                hx = q[0] + side * (20 + 30 * j) / z
                d.ellipse((hx - 14 / z, q[1] - h_ - 60 / z, hx + 14 / z, q[1] - h_ - 32 / z), fill=cc)
                d.rectangle((hx - 16 / z, q[1] - h_ - 32 / z, hx + 16 / z, q[1] - h_ + 10 / z), fill=cc)
        a = proj(W / 2 + side * 330, 0.7); b = proj(W / 2 + side * 330, 9); d.line((a[0], a[1] - 70 / 0.7, b[0], b[1] - 70 / 9), fill=(220, 220, 230), width=3)
    # arche d'arrivée générique (sans texte de marque)
    a = proj(W / 2 - 360, 7.5); b = proj(W / 2 + 360, 7.5); hh = 420 / 7.5
    d.rectangle((a[0] - 14, a[1] - hh, a[0], a[1]), fill=(230, 230, 236)); d.rectangle((b[0], b[1] - hh, b[0] + 14, b[1]), fill=(230, 230, 236))
    d.rectangle((a[0] - 14, a[1] - hh - 18, b[0] + 14, a[1] - hh), fill=(240, 150, 30))
    return img

HIGH_D = make_highlands("dawn"); HIGH_N = make_highlands("night"); HIGH_G = make_highlands("gold")
TRACK_N = make_track("night"); TRACK_R = make_track("rain"); TRACK_G = make_track("gold")
AVE_D = make_avenue("dawn"); AVE_G = make_avenue("gold")
TRR_ARR = np.asarray(TRACK_R.convert("RGB")).astype(np.float32); AVG_ARR = np.asarray(AVE_G.convert("RGB")).astype(np.float32)

def series_banner(d, tg):
    if tg > 4.0 or tg < 0.5: return
    e = eout((tg - 0.5) / 0.25); o = ease((tg - 3.65) / 0.35)
    y = -150 + 220 * e - 260 * o
    d.rounded_rectangle((90, y, W - 90, y + 130), 22, fill=(96, 24, 40), outline=GOLD, width=5)
    text(d, (W / 2, y + 45), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), WHITE, BOLD)
    text(d, (W / 2, y + 98), "ÉPISODE 18", 40, GOLD, MONO)

def medal(d, cx, cy, r, col, k=1.0):
    """médaille générique : ruban en V + disque (sans inscription)"""
    if k <= 0: return
    s = eout(min(1, k / 0.25)); r = r * (0.4 + 0.6 * s)
    d.polygon([(cx - r * 0.7, cy - r * 2.4), (cx - r * 0.15, cy - r * 2.4), (cx + r * 0.25, cy - r * 0.6), (cx - r * 0.2, cy - r * 0.6)], fill=(40, 110, 200))
    d.polygon([(cx + r * 0.7, cy - r * 2.4), (cx + r * 0.15, cy - r * 2.4), (cx - r * 0.25, cy - r * 0.6), (cx + r * 0.2, cy - r * 0.6)], fill=(220, 60, 60))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=mix(col, (0, 0, 0), 0.35), width=max(2, int(r / 8)))
    d.ellipse((cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62), outline=mix(col, (255, 255, 255), 0.4), width=max(2, int(r / 12)))

def board(img, d, cx, cy, k, hl_k):
    """tableau de résultats générique : 8 lignes sans nom, la 7e s'allume en rouge"""
    if k <= 0: return 0.0
    a = eout(min(1, k / 0.3)); w, h = 760, 520
    y0 = cy - h / 2 + 60 * (1 - a)
    d.rounded_rectangle((cx - w / 2, y0, cx + w / 2, y0 + h), 26, fill=(14, 18, 30), outline=(120, 130, 160), width=4)
    text(d, (cx, y0 + 46), "RÉSULTATS", 50, WHITE, MONO)
    hit = 0.0
    for i in range(8):
        yy = y0 + 100 + i * 50
        on = i == 6 and hl_k > 0
        if on:
            d.rectangle((cx - w / 2 + 14, yy - 22, cx + w / 2 - 14, yy + 22), fill=(170, 30, 30)); hit = max(0, 1 - hl_k / 0.3)
        text(d, (cx - w / 2 + 70, yy), f"{i + 1}", 38, GOLD if i < 3 else (WHITE if on else GREY), MONO)
        d.rounded_rectangle((cx - w / 2 + 130, yy - 9, cx - w / 2 + 130 + (420 if not on else 300), yy + 9), 9, fill=(255, 255, 255) if on else (60, 66, 90))
        if i < 3: d.ellipse((cx + w / 2 - 96, yy - 14, cx + w / 2 - 68, yy + 14), fill=(60, 220, 120))
        if on: text(d, (cx + w / 2 - 110, yy), "NON", 34, WHITE, BOLD)
    return hit

def bigclock(d, cx, cy, s, k, size, col, glow=None):
    if k <= 0: return
    sz = pop(k, size, 0.2, 0.25)
    d.rounded_rectangle((cx - 470, cy - sz * 0.62, cx + 470, cy + sz * 0.62), 30, fill=(10, 12, 22), outline=col, width=6)
    text(d, (cx, cy), s, fit(s, sz, 880, MONO), col, MONO)

def kmpost(d, xw, z, label_):
    q = proj(xw, z); s = 1 / z
    d.line((q[0], q[1], q[0], q[1] - 260 * s), fill=(220, 220, 230), width=max(2, int(10 * s)))
    d.rounded_rectangle((q[0] - 120 * s, q[1] - 380 * s, q[0] + 120 * s, q[1] - 250 * s), int(18 * s), fill=(240, 150, 30))
    text(d, (q[0], q[1] - 315 * s), label_, max(8, int(80 * s)), BG, BOLD)

def s_hook(img, d, tg, k):
    img.paste(TRACK_R); d = ImageDraw.Draw(img); rainfall(d, tg, 0.8)
    shadow(d, W / 2, FEET, 250); P(img, W / 2, FEET, 250, "sad"); d = ImageDraw.Draw(img)
    topsh(img); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    sc = 1 + 0.3 * (1 - eout((tg + 0.12) / 0.2))
    text(d, (W / 2, 420), "PAS", int(150 * sc), WHITE, BOLD, stroke=8, scol=BG)
    kk = kM(tg, "sel1"); hit = 0.0
    text(d, (W / 2, 580), "SÉLECTIONNÉ ?", pop(max(kk, 0.01), fit("SÉLECTIONNÉ ?", 150, 1000), 0.25, 0.2), ORANGE, BOLD, stroke=10, scol=BG)
    hit = max(0, 1 - max(0, tg) / 0.3)
    k27 = kM(tg, "a27")
    if k27 > 0: TX(d, 740, "À 27 ANS", 100, ICE, k27)
    kj = kM(tg, "jeux1")
    if kj > 0: hit = max(hit, stamp(img, "PAS DE JEUX OLYMPIQUES", (W / 2, 900), 90, -6, kj, RED2))
    return dict(hit=hit)

def s_intro(img, d, tg, k):
    kv = kM(tg, "village"); ke = kM(tg, "trois"); hit = 0.0
    img.paste(HIGH_D); rays(img, 0.3); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240, (120, 60, 40))
    P(img, W / 2, FEET, 240, run_pose(tg * 7) if ke > -0.5 else "stand"); d = ImageDraw.Draw(img)
    if ke > -0.5:   # sac d'école sur le dos : petit rectangle qui suit
        hp = JT.get("rh", None)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 290, "L'HISTOIRE VRAIE", 100, WHITE, k)
    kk = kM(tg, "kenya")
    if kk > 0: TX(d, 420, "KENYA", 140, ORANGE, kk)
    if kv > 0 and ke <= 0: TX(d, 560, "UN PETIT VILLAGE", 84, AMBER, kv)
    if ke > 0:
        counter(d, 600, 0, 3, ke, 1.2, 190, GOLD, "{} KM")
        TX(d, 740, "POUR ALLER À L'ÉCOLE", 76, WHITE, kM(tg, "ecole"))
        TX(d, 840, "CHAQUE JOUR", 70, ICE, kM(tg, "ecole") - 0.2)
    return dict(hit=hit)

def s_coach(img, d, tg, k):
    hit = 0.0
    img.paste(TRACK_N); d = ImageDraw.Draw(img)
    # l'entraîneur (silhouette plus grande, immobile, chrono à la main) regarde le jeune courir en rond
    q = Q(W / 2 - 260, FEET); P(img, q[0], q[1], 255 / ZF, "point", fixed=True); d = ImageDraw.Draw(img)
    cx_, cy_ = q[0] + 60 / ZF, q[1] - 560 / ZF
    clock(d, cx_ + 90 / ZF, cy_ + 40 / ZF, 34 / ZF + 8, tg * 6, WHITE)
    ph = k * 1.3
    xr = W / 2 + 220 + 160 * math.sin(ph); zr = 1.0 + 0.6 * (1 + math.cos(ph))
    x2 = W / 2 + (xr - W / 2) / zr; y2 = HOR + (FEET - HOR) / zr; s2 = 220 / zr
    shadow(d, x2, y2, s2, fixed=True); P(img, x2, y2, s2, run_pose(tg * 9), facing=1 if math.cos(ph) > 0 else -1, fixed=True); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    badge(d, 180, 330, "16 ANS", kM(tg, "a16"), GOLD, 110)
    TX(d, 300, "SON ENTRAÎNEUR", 84, WHITE, kM(tg, "entraineur"), x=W / 2 + 100, maxw=720)
    km = kM(tg, "medaille")
    if km > 0: TX(d, 420, "ANCIEN MÉDAILLÉ OLYMPIQUE", 60, ICE, km, x=W / 2 + 100, maxw=720)
    return dict(hit=hit)

def s_monde(img, d, tg, k):
    kc = kM(tg, "champion1"); km = kM(tg, "medailles"); hit = 0.0
    img.paste(TRACK_G if kc > 0 else TRACK_N); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET, 262, "up" if kc > 0 else run_pose(tg * 9)); d = ImageDraw.Draw(img)
    if kc > 0: confetti(d, kc * 0.9, 0.6)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    badge(d, 180, 330, "18 ANS", kM(tg, "a18"), GOLD, 110)
    if kc > 0 and km <= 0:
        hit = stamp(img, "CHAMPION DU MONDE", (W / 2, 500), 96, -5, kc, GOLD)
        TX(d, 660, "5 000 MÈTRES", 110, WHITE, kM(tg, "metres1"))
        medal(d, W / 2, 960, 80, GOLD, kc - 0.2)
    if km > 0:
        TX(d, 470, "+ 2 MÉDAILLES", 110, WHITE, km)
        TX(d, 590, "AUX JEUX OLYMPIQUES", 76, ICE, km - 0.2)
        medal(d, W / 2 - 150, 900, 85, BRONZE, km - 0.1); medal(d, W / 2 + 150, 900, 85, SILVER, km - 0.35)
    return dict(hit=hit)

def s_selection(img, d, tg, k):
    k7 = kM(tg, "septieme"); k10 = kM(tg, "dixk"); k5 = kM(tg, "cinqk"); kl = kM(tg, "londres"); hit = 0.0
    img.paste(TRACK_R); d = ImageDraw.Draw(img); rainfall(d, tg, 1.0)
    shadow(d, W / 2 + 200, FEET, 240)
    P(img, W / 2 + 200, FEET, 240, "sad" if k7 > 0 else run_pose(tg * 9)); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 250, "2012", 130, WHITE, kM(tg, "y2012"))
    TX(d, 360, "SÉLECTIONS DU KENYA", 76, AMBER, kM(tg, "selections"))
    if kl > 0:
        hit = stamp(img, "PAS DE JEUX DE LONDRES", (W / 2, 620), 92, -5, kl, RED2)
        return dict(hit=hit)
    hb = board(img, d, W / 2, 720, kM(tg, "selections") - 0.3, k7)
    if k7 > 0 and k10 <= 0: hit = max(hb, stamp(img, "7e", (W / 2 + 330, 520), 150, 8, k7, RED2))
    if k10 > 0: TX(d, 1020, "10 000 M : 7e", 80, RED2, k10)
    if k5 > 0: TX(d, 1120, "5 000 M : 7e", 80, RED2, k5)
    return dict(hit=max(hit, hb))

def s_doute(img, d, tg, k):
    kf = kM(tg, "fini2"); hit = 0.0
    img.paste(TRACK_R); d = ImageDraw.Draw(img); rainfall(d, tg, 1.0)
    shadow(d, W / 2, FEET, 250)
    P(img, W / 2, FEET - 90 / ZF, 250, "kneel"); d = ImageDraw.Draw(img)
    dim(img, 0.25); topsh(img); d = ImageDraw.Draw(img)
    TX(d, 280, "IL AURAIT PU SE DIRE…", 84, WHITE, kM(tg, "aurait"))
    if kf > 0: hit = stamp(img, "« C'EST FINI »", (W / 2, 520), 140, -6, kf, RED2)
    return dict(hit=hit)

def s_cri(img, d, tg, k):
    kb_ = tg - K["boom"]; kk = max(0.0, kb_ + 0.06); kr = kM(tg, "course")
    c = (W / 2, 820)
    r = eout(max(0, kr) / 1.2) * 2300 if kr > 0 else 0
    img.paste(reveal(TRR_ARR, AVG_ARR, c, r)); d = ImageDraw.Draw(img)
    if kr < 0.6: rainfall(d, tg, max(0, 1 - kr / 0.6))
    rays(img, min(1, max(0, kr - 0.2) / 0.5)); d = ImageDraw.Draw(img)
    speed_lines(d, c, kr, 44)
    rings(img, c, kr, 6, GOLD, 1050, 16, 0.14, 1.25); d = ImageDraw.Draw(img)
    burst(d, c[0], c[1], kr, 26, 520, (255, 240, 190), 3, 10)
    shadow(d, W / 2, FEET, 270)
    if kr > 0: P(img, W / 2, FEET, 270, dict(run_pose(tg * 12), t=20)); d = ImageDraw.Draw(img)
    else: P(img, W / 2, FEET, 270, POSES["sad"] if kb_ < 0 else POSES["shout"]); d = ImageDraw.Draw(img)
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    hit = max(0, 1 - kk / 0.3) if kk > 0 else 0
    e = eout(kk / 0.22) if kk > 0 else 0
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, eout(max(0, kr) / 0.22))
    f1 = fit("IL VA CHANGER", 140, 960); f2 = pop(kr, fit("DE COURSE !", 150, 960), 0.08)
    for off, cc in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        if kb_ > 0: text(d, (x1 + o, 420), "IL VA CHANGER", f1, cc, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
        if kr > 0: text(d, (x2 - o, 590), "DE COURSE !", f2, cc if cc != WHITE else GOLD, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
    km = kM(tg, "marathon1")
    if km > 0: TX(d, 760, "LE MARATHON", 104, WHITE, km)
    hr = max(0, 1 - kr / 0.3) if kr > 0 else 0
    return dict(hit=max(hit, hr) * 1.6, shake=max(hit, hr) * 1.9, flash=max(0, 0.9 - kr * 2.6) if kr > 0 else 0)

def s_marathon(img, d, tg, k):
    k42 = kM(tg, "k42"); kp = kM(tg, "premier1"); kg = kM(tg, "gagne"); hit = 0.0
    img.paste(AVE_D if kg <= 0 else AVE_G); d = ImageDraw.Draw(img)
    for i, z in enumerate((2.0, 5.0, 8.0)):   # bornes kilométriques qui défilent vers la caméra
        zz = z - (k * 1.6) % 3.0
        if zz > 0.6: kmpost(d, W / 2 + 280, zz, ["10", "21", "30", "42"][(i + int(k * 1.6 / 3)) % 4] if kg <= 0 else "42")
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET, 262, run_pose(tg * 9) if kg <= 0 else "up"); d = ImageDraw.Draw(img)
    if kg > 0:   # ruban d'arrivée qui se casse
        q = Q(W / 2, FEET); y = q[1] - 520 / ZF; u = eout(min(1, kg / 0.4))
        d.line((0, y + 30 * u, W / 2 - 40 - 300 * u, y + 200 * u), fill=(255, 255, 255), width=10)
        d.line((W, y + 30 * u, W / 2 + 40 + 300 * u, y + 200 * u), fill=(255, 255, 255), width=10)
        confetti(d, kg * 0.9, 0.8)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    if k42 > 0 and kp <= 0: counter(d, 360, 0, 42, k42, 1.0, 200, ORANGE, "{} KM")
    if kp > 0:
        TX(d, 260, "2013", 120, WHITE, kM(tg, "y2013"))
        TX(d, 380, "SON 1er MARATHON", 90, AMBER, kp)
    if kg > 0: hit = stamp(img, "GAGNÉ !", (W / 2, 560), 170, -6, kg, GOLD)
    return dict(hit=hit, flash=0.35 * max(0, 1 - kg / 0.25) if 0 < kg < 0.25 else 0)

def s_jo(img, d, tg, k):
    kc = kM(tg, "olymp2"); k2 = kM(tg, "encore"); hit = 0.0
    img.paste(AVE_G); d = ImageDraw.Draw(img); fireworks(d, tg, 0.6)
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET - (16 * abs(math.sin(k * 6)) if kc > 0 else 0), 262, "up" if kc > 0 else run_pose(tg * 9)); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    if k2 > 0:
        TX(d, 260, "5 ANS PLUS TARD…", 92, WHITE, kM(tg, "cinq"))
        hit = stamp(img, "ENCORE !", (W / 2, 430), 140, -5, k2, GOLD)
        medal(d, W / 2 - 150, 840, 90, GOLD, 1.0); medal(d, W / 2 + 150, 840, 90, GOLD, k2 - 0.2)
        if k2 > 0.2: TX(d, 1020, "× 2", 150, GOLD, k2 - 0.2)
        return dict(hit=hit, flash=0.35 * max(0, 1 - k2 / 0.25) if k2 < 0.25 else 0)
    TX(d, 250, "2016", 130, WHITE, kM(tg, "y2016"))
    if kc > 0:
        hit = stamp(img, "CHAMPION OLYMPIQUE", (W / 2, 420), 100, -5, kc, GOLD)
        TX(d, 560, "DU MARATHON", 90, ICE, kc - 0.3)
        medal(d, W / 2, 940, 100, GOLD, kc - 0.2)
    return dict(hit=hit, flash=0.35 * max(0, 1 - kc / 0.25) if 0 < kc < 0.25 else 0)

def s_record(img, d, tg, k):
    kr = kM(tg, "record"); k19 = kM(tg, "y2019"); kh = kM(tg, "humain"); kt = kM(tg, "heures"); hit = 0.0
    img.paste(AVE_G if k19 <= 0 else HIGH_G); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET, 262, run_pose(tg * 10)); d = ImageDraw.Draw(img)
    speed_lines(d, (W / 2, 700), 0.5 + 0.2 * math.sin(tg * 3), 30)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    if k19 <= 0:
        TX(d, 250, "2018", 130, WHITE, kM(tg, "y2018"))
        if kr > 0:
            hit = stamp(img, "RECORD DU MONDE", (W / 2, 420), 110, -5, kr, GOLD)
            bigclock(d, W / 2, 620, "2:01:39", kr - 0.2, 170, GOLD)
        return dict(hit=hit)
    TX(d, 230, "2019", 120, WHITE, k19)
    ks = kM(tg, "speciale")
    if ks > 0: TX(d, 340, "(COURSE SPÉCIALE, NON OFFICIELLE)", 46, ICE, ks)
    if kh > 0: TX(d, 450, "1er HUMAIN", 110, ORANGE, kh)
    if kt > 0:
        hit = stamp(img, "MOINS DE 2 HEURES", (W / 2, 630), 96, -4, kt, GOLD)
        bigclock(d, W / 2, 830, "1:59:40", kt - 0.1, 170, GOLD)
    else:
        u = min(1, max(0, kM(tg, "humain")) / 1.6)
        s = int(lerp(2 * 3600 + 30, 7180, u))
        if kh > 0: bigclock(d, W / 2, 830, f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}", 1.0, 170, WHITE)
    return dict(hit=hit, flash=0.35 * max(0, 1 - kt / 0.25) if 0 < kt < 0.25 else 0)

def s_regard(img, d, tg, k):
    kl = kM(tg, "legende"); hit = 0.0
    img.paste(HIGH_N); d = ImageDraw.Draw(img)
    fireworks(d, tg, 1.0 if kl > 0 else 0.4)
    shadow(d, W / 2, FEET + 20, 260, (40, 30, 40))
    P(img, W / 2, FEET + 20 - (18 * abs(math.sin(tg * 7)) if kl > 0 else 0), 260, "up" if kl > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 250, "L'HOMME QU'ON N'AVAIT", 84, WHITE, kM(tg, "homme"))
    TX(d, 350, "PAS SÉLECTIONNÉ…", 92, ICE, kM(tg, "homme") - 0.3)
    if kl > 0: hit = stamp(img, "UNE LÉGENDE", (W / 2, 540), 140, -4, kl, GOLD)
    return dict(hit=hit, flash=0.4 * max(0, 1 - kl / 0.25) if kl > 0 else 0)

def s_you(img, d, tg, k):
    kn = kM(tg, "non"); hit = 0.0
    img.paste(HIGH_D); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 262, (120, 60, 40))
    P(img, W / 2, FEET, 262, blend_pose(POSES["stand"], POSES["point"], eout(max(0, k) / 0.4)))
    dim(img, 0.25); topsh(img); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(150 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=8, scol=BG)
    TX(d, 470, "UN SEUL « NON »", 100, WHITE, kn)
    if kn > 0: hit = stamp(img, "VA T'ARRÊTER ?", (W / 2, 630), 110, -4, kn + 0.4, GOLD)
    return dict(hit=hit)

STAD_AMAT = HIGH_N   # fonds abonne / question / logo

def s_abonne(img, d, tg, k):
    img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
    dim(img, 0.6); d = ImageDraw.Draw(img)
    hit = 0.0
    P(img, 200, FEET + 20, 215, "point", fixed=True); d = ImageDraw.Draw(img)
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rounded_rectangle((W / 2 - bw / 2, 420 - bh / 2, W / 2 + bw / 2, 420 + bh / 2), int(40 * sc), fill=RED)
    text(d, (W / 2 - bw / 2 + 90 * sc, 420), "+", int(130 * sc), WHITE, BOLD)
    text(d, (W / 2 + 50 * sc, 420), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE, BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = kM(tg, "demain")
    if kd > 0:
        TX(d, 660, "DEMAIN · ÉPISODE 19", 74, GOLD, kd)
        kc = kM(tg, "vendeuse")
        if kc > 0:
            text(d, (W / 2, 770), typew("LA VENDEUSE À QUI ON", kc, 30), fit("LA VENDEUSE À QUI ON", 68, 960), WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 860), typew("CLAQUAIT LA PORTE AU NEZ…", kc - 0.6, 30), fit("CLAQUAIT LA PORTE AU NEZ…", 68, 960), WHITE, BOLD, stroke=6, scol=BG)
    return dict(hit=hit)

SCENES = {"hook": s_hook, "intro": s_intro, "coach": s_coach, "monde": s_monde, "selection": s_selection, "doute": s_doute, "cri": s_cri,
          "marathon": s_marathon, "jo": s_jo, "record": s_record, "regard": s_regard, "you": s_you,
          "abonne": s_abonne, "question": s_question, "logo": s_logo}

def PATH(typ, k, tg):
    st = SC[typ]
    if typ == "hook":      return _seg(k, [(0, 1.0, 0, 0), (4.0, 1.15, 0, 0)]) + (False,)
    if typ == "intro":     return _seg(k, [(0, 3.0, 0, 0), (5.0, 1.0, 0, 0)]) + (False,)   # il court vers la caméra sur la piste de terre
    if typ == "coach":     return _seg(k, [(0, 1.3, 0, 0), (3.0, 1.05, 0, 0)]) + (False,)
    if typ == "monde":     return _seg(k, [(0, 2.6, -260, 0), (2.0, 1.05, 0, 0)]) + (False,)
    if typ == "selection": return _seg(k, [(0, 2.4, 200, 0), (2.4, 1.1, 0, 0)]) + (False,)
    if typ == "doute":     return _seg(k, [(0, 1.5, 0, 0), (2.0, 1.0, 0, 0)]) + (False,)
    if typ == "cri":
        r = MK_("course") - st
        return _seg(k, [(0, 1.6, 0, 0), (r, 1.6, 0, 0), (r + 1.5, 0.95, 0, 0)]) + (False,)
    if typ == "marathon":  return (1.0 + 0.06 * math.sin(k * 2), 40 * math.sin(k * 0.8), 0.0, 0.0, False)
    if typ == "jo":        return _seg(k, [(0, 2.4, 220, 0), (1.6, 1.05, 0, 0)]) + (False,)
    if typ == "record":    return (1.0 + 0.05 * math.sin(k * 1.5), 60 * math.sin(k * 0.6), 0.0, 0.0, False)
    if typ == "regard":    return _seg(k, [(0, 2.0, 0, 0), (2.4, 1.0, 0, 0)]) + (False,)
    if typ == "you":       return _seg(k, [(0, 1.35, -150, 0), (2.0, 0.9, 60, 0)]) + (False,)
    return (1.0, 0.0, 0.0, 0.0, False)

def CAMF(typ, k, tg):
    hh = (6 * math.sin(tg * 2.1), 5 * math.sin(tg * 1.7 + 1))
    dur = 3.0
    for s_ in SCN:
        if s_["type"] == typ: dur = s_["end"] - s_["start"]
    u = ease(k / max(0.5, dur))
    if typ == "hook":      return (lerp(1.25, 1.08, u), lerp(40, -30, u) + hh[0], lerp(50, 0, u) + hh[1], lerp(0.06, -0.03, u), -0.03, lerp(-1.5, 0, u))
    if typ == "intro":     return (lerp(1.1, 1.18, u), lerp(-60, 60, u), hh[1], lerp(0.08, -0.05, u), 0.05, 0.0)
    if typ == "coach":     return (lerp(1.18, 1.06, u), lerp(70, -50, u) + hh[0], hh[1], lerp(-0.07, 0.07, u), 0.04, 0.0)
    if typ == "monde":     return (lerp(1.06, 1.2, u), hh[0], lerp(30, -30, u), lerp(0.06, -0.06, u), -0.05, 0.0)
    if typ == "selection": return (lerp(1.2, 1.06, u), hh[0] * 1.5, lerp(-30, 30, u), lerp(-0.07, 0.05, u), -0.04, 1.0 * math.sin(tg * 2))
    if typ == "doute":     return (lerp(1.06, 1.22, u), hh[0], lerp(0, -40, u), 0.0, 0.06, 0.0)
    if typ == "cri":
        kb = max(0.0, tg - M("course", 99))
        orb = math.sin(min(1, kb / 1.8) * math.pi) * 0.13
        return (1.08 + 0.2 * math.exp(-kb * 3) if kb > 0 else 1.1, hh[0] * 2, hh[1], orb, 0.06 if kb > 0 else 0.0, 3 * math.sin(kb * 4) * math.exp(-kb * 2))
    if typ == "marathon":  return (1.1 + 0.03 * math.sin(tg * 9), hh[0] * 2.5, hh[1] * 2 + 8 * math.sin(tg * 9), lerp(0.08, -0.08, u), 0.04, 1.2 * math.sin(tg * 4.5))
    if typ == "jo":        return (lerp(1.08, 1.2, u), lerp(-80, 60, u) + hh[0], hh[1], lerp(-0.07, 0.07, u), 0.0, 0.0)
    if typ == "record":    return (lerp(1.06, 1.18, u), hh[0] * 2, hh[1], lerp(0.09, -0.09, u), 0.05, 1.0 * math.sin(tg * 3))
    if typ == "regard":    return (lerp(1.18, 1.06, u), hh[0], lerp(-40, 30, u), lerp(0.08, -0.06, u), 0.05, 0.0)
    if typ == "you":       return (lerp(1.06, 1.16, u), lerp(-60, 30, u) + hh[0], hh[1], lerp(0.06, -0.04, u), 0.0, 0.0)
    return None


# =============================================================== ép. 19 (26/11/2026) — Sara Blakely « On t'a claqué la porte au nez ? » (1re histoire BUSINESS)
# Décors NOUVEAUX : COULOIR DE BUREAUX en perspective (portes des deux côtés qui CLAQUENT, néons) nuit / doré, SALLE D'EXAMEN (rangées de tables),
# PETIT APPARTEMENT le soir (fenêtre sur la ville, lampe, table : collant + ciseaux), USINES DE BRIQUES sous la pluie (cheminées, portails) nuit / doré,
# GRAND MAGASIN (colonnes, lustres, sol de marbre, vitrines). Héroïne = silhouette lumineuse avec QUEUE DE CHEVAL. Aucun logo, marque ni nom à l'écran.
RED2 = (255, 70, 60); PINK = (255, 120, 150)

_PL_ORIG = _PLAYER0
def _PLAYER0(L, x, y, s, pose, *a, **kw):
    """silhouette + queue de cheval (dessinée sur le même calque, donc lumineuse elle aussi)"""
    _PL_ORIG(L, x, y, s, pose, *a, **kw)
    if "head" not in JT: return
    cx, hy = JT["head"]; hw = 0.1 * s; top = hy - hw
    f = kw.get("facing", 1)
    d = ImageDraw.Draw(L); c = SKIN + (255,)
    bx = cx - f * hw * 1.0; by = top + hw * 0.5
    d.ellipse((bx - hw * 0.42, by - hw * 0.42, bx + hw * 0.42, by + hw * 0.42), fill=c)          # attache
    pts = [(bx - f * hw * 0.1, by), (bx - f * hw * 0.55, by + hw * 0.9), (bx - f * hw * 0.35, by + hw * 1.7), (bx - f * hw * 0.05, by + hw * 2.1)]
    for i in range(len(pts) - 1):
        r = hw * (0.48 - i * 0.1)
        for u in np.linspace(0, 1, 6):
            px = lerp(pts[i][0], pts[i + 1][0], u); py = lerp(pts[i][1], pts[i + 1][1], u)
            d.ellipse((px - r, py - r, px + r, py + r), fill=c)

# ---------------------------------------------------------------- décors
def make_corridor(mode="night"):
    """couloir de bureaux : murs latéraux en perspective, portes fermées, néons au plafond, sol en dalles"""
    gold = mode == "gold"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    wallc = (48, 56, 80) if not gold else (150, 110, 90); ceil = (30, 34, 50) if not gold else (120, 86, 70)
    floor0 = (70, 76, 96) if not gold else (190, 150, 110); floor1 = (36, 40, 56) if not gold else (120, 90, 70)
    XL, XR, HW = W / 2 - 430, W / 2 + 430, 1150
    d.rectangle((0, 0, W, H), fill=ceil)
    # fond du couloir (fenêtre lumineuse au bout)
    zb = 14.0; a = proj(XL, zb); b = proj(XR, zb)
    d.rectangle((a[0], a[1] - HW / zb, b[0], b[1]), fill=(150, 170, 210) if not gold else (255, 210, 140))
    _glow(img, (a[0] - 160, a[1] - HW / zb - 160, b[0] + 160, b[1] + 160), (200, 220, 255) if not gold else (255, 220, 160), 170, 50); d = ImageDraw.Draw(img)
    for side, X in ((-1, XL), (1, XR)):   # murs
        p0 = proj(X, 0.45); p1 = proj(X, zb)
        d.polygon([(p0[0], p0[1]), (p1[0], p1[1]), (p1[0], p1[1] - HW / zb), (p0[0], p0[1] - HW / 0.45)], fill=mix(wallc, (0, 0, 0), 0.12 if side < 0 else 0.0))
        for z in np.arange(1.0, 13, 0.9):   # plinthe + joints
            q = proj(X, z); d.line((q[0], q[1], q[0], q[1] - HW / z), fill=mix(wallc, (0, 0, 0), 0.25), width=max(1, int(4 / z)))
    # sol en dalles
    d.polygon([proj(XL, 0.45), proj(XR, 0.45), proj(XR, zb), proj(XL, zb)], fill=floor0)
    for z in np.arange(0.6, zb, 0.5):
        d.line((proj(XL, z), proj(XR, z)), fill=floor1, width=max(1, int(5 / z)))
    for xw in np.linspace(XL, XR, 7):
        d.line((proj(xw, 0.45), proj(xw, zb)), fill=floor1, width=3)
    # néons
    for z in (1.3, 2.3, 3.6, 5.2, 7.5, 10.5):
        a = proj(W / 2 - 150, z); b = proj(W / 2 + 150, z); y = HOR - HW / z + 20 / z
        d.rectangle((a[0], y, b[0], y + 26 / z), fill=(240, 248, 255) if not gold else (255, 236, 200))
        _glow(img, (a[0] - 60 / z, y - 40 / z, b[0] + 60 / z, y + 120 / z), (220, 236, 255) if not gold else (255, 220, 160), 90, 18); d = ImageDraw.Draw(img)
    for side, X in ((-1, XL), (1, XR)):   # portes fermées peintes sur les murs
        for z in DOORZ: _door_closed(d, X, z, gold)
    if not gold:   # reflets froids au sol
        _glow(img, (W / 2 - 300, HOR + 80, W / 2 + 300, H - 300), (120, 150, 220), 40, 60)
    return img

DOORZ = (1.15, 1.9, 3.0, 4.6, 7.0)
DOOR_H = 760; DOOR_D = 0.42
def _door_closed(d, X, z, gold=False, col=None):
    col = col or ((150, 96, 64) if not gold else (190, 130, 80))
    z2 = z + DOOR_D; a = proj(X, z); b = proj(X, z2)
    d.polygon([(a[0], a[1]), (b[0], b[1]), (b[0], b[1] - DOOR_H / z2), (a[0], a[1] - DOOR_H / z)], fill=col, outline=mix(col, (0, 0, 0), 0.4))
    m = proj(X, z + DOOR_D * 0.82); d.ellipse((m[0] - 7 / z, m[1] - 380 / z - 7 / z, m[0] + 7 / z, m[1] - 380 / z + 7 / z), fill=(230, 210, 140))

def door_swing(d, side, z, open_):
    """porte qui pivote sur sa charnière (côté proche) : open_=1 grande ouverte vers le couloir, 0 = fermée contre le mur"""
    X = W / 2 + side * 430
    th = open_ * math.radians(70)
    xw = X - side * 300 * math.sin(th); zf = z + DOOR_D * math.cos(th)
    zf = max(0.5, zf)
    a = proj(X, z); b = proj(xw, zf)
    col = (170, 110, 72)
    d.polygon([(a[0], a[1]), (b[0], b[1]), (b[0], b[1] - DOOR_H / zf), (a[0], a[1] - DOOR_H / z)], fill=col, outline=(60, 40, 30))
    # lumière de la pièce derrière
    if open_ > 0.05:
        c = proj(X, z + DOOR_D)
        d.polygon([(a[0], a[1]), (c[0], c[1]), (c[0], c[1] - DOOR_H / (z + DOOR_D)), (a[0], a[1] - DOOR_H / z)], fill=mix((40, 44, 60), (255, 230, 170), open_))

def make_exam():
    """salle d'examen : parquet, rangées de tables en perspective, grandes fenêtres, horloge"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR, (60, 66, 90), (110, 110, 130), 1.0)
    for i in range(4):   # fenêtres hautes
        x0 = 90 + i * 240
        d.rectangle((x0, 260, x0 + 170, 760), fill=(170, 196, 230)); d.line((x0 + 85, 260, x0 + 85, 760), fill=(80, 86, 110), width=8)
        d.line((x0, 510, x0 + 170, 510), fill=(80, 86, 110), width=8)
    _glow(img, (0, 200, W, 820), (200, 220, 255), 60, 50); d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - 60, 120, W / 2 + 60, 240), fill=(240, 240, 236), outline=(40, 40, 50), width=8)
    d.line((W / 2, 180, W / 2, 140), fill=(30, 30, 40), width=6); d.line((W / 2, 180, W / 2 + 32, 190), fill=(30, 30, 40), width=6)
    _ground(d, (150, 110, 70), (90, 60, 40), 0.07)
    for z in np.arange(1.4, 9, 1.1):   # tables
        for xw in (-700, -200, W / 2 - 380, W / 2 + 380, W + 200, W + 700):
            a = proj(xw - 170, z); b = proj(xw + 170, z); hh = 230 / z
            d.rectangle((a[0], a[1] - hh, b[0], a[1] - hh + 22 / z), fill=(200, 170, 120))
            d.line((a[0] + 10 / z, a[1] - hh, a[0] + 10 / z, a[1]), fill=(70, 60, 50), width=max(1, int(6 / z)))
            d.line((b[0] - 10 / z, a[1] - hh, b[0] - 10 / z, a[1]), fill=(70, 60, 50), width=max(1, int(6 / z)))
            d.rectangle((lerp(a[0], b[0], 0.35), a[1] - hh - 4 / z, lerp(a[0], b[0], 0.6), a[1] - hh + 4 / z), fill=(250, 250, 245))
    return img

def make_flat():
    """petit appartement le soir : mur, fenêtre sur la ville la nuit, lampe chaude, parquet"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR, (40, 34, 52), (70, 56, 66), 1.0)
    d.rectangle((150, 200, W - 150, 760), fill=(14, 20, 46))
    _stars(d, 40, 400, 9)
    rng = np.random.default_rng(21)
    x = 150
    while x < W - 150:   # immeubles par la fenêtre
        w_ = rng.uniform(60, 130); h_ = rng.uniform(150, 440)
        d.rectangle((x, 760 - h_, min(W - 150, x + w_), 760), fill=(26, 30, 56))
        for yy in np.arange(760 - h_ + 18, 750, 30):
            for xx in np.arange(x + 10, min(W - 160, x + w_ - 10), 22):
                if rng.random() < 0.4: d.rectangle((xx, yy, xx + 10, yy + 14), fill=(255, 210, 120))
        x += w_ + 6
    d.rectangle((140, 190, W - 140, 770), outline=(90, 70, 60), width=18); d.line((W / 2, 190, W / 2, 770), fill=(90, 70, 60), width=14)
    _ground(d, (120, 80, 56), (70, 44, 32), 0.08)
    # lampe à gauche
    d.line((120, HOR + 40, 120, 520), fill=(30, 26, 26), width=10)
    d.polygon([(60, 520), (180, 520), (150, 430), (90, 430)], fill=(255, 210, 140))
    _glow(img, (-200, 300, 450, 900), (255, 200, 120), 150, 70)
    return img

def make_factory(mode="rain"):
    """usines de briques : toits en dents de scie, cheminées, grillage + portail fermé, route mouillée"""
    gold = mode == "gold"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR, (16, 20, 36) if not gold else (110, 80, 120), (50, 56, 80) if not gold else (255, 190, 120), 1.1)
    if gold:
        _glow(img, (W / 2 - 280, HOR - 420, W / 2 + 280, HOR + 40), (255, 214, 150), 220, 70); d = ImageDraw.Draw(img)
    brick = (110, 50, 40) if not gold else (190, 96, 66); dk = mix(brick, (0, 0, 0), 0.35)
    for i, (x0, x1, h_) in enumerate(((-40, 420, 330), (640, 1120, 380))):
        y0 = HOR - h_
        d.rectangle((x0, y0, x1, HOR), fill=brick)
        for xx in np.arange(x0, x1, 80):   # dents de scie
            d.polygon([(xx, y0), (xx + 80, y0), (xx + 80, y0 - 60)], fill=dk)
        for yy in np.arange(y0 + 40, HOR - 20, 70):   # fenêtres
            for xx in np.arange(x0 + 30, x1 - 40, 70):
                d.rectangle((xx, yy, xx + 40, yy + 40), fill=(255, 210, 130) if (gold or (int(xx + yy) % 3 == 0)) else (30, 30, 44))
        for yy in np.arange(y0, HOR, 16): d.line((x0, yy, x1, yy), fill=dk, width=1)
    for cx, h_ in ((300, 560), (820, 620)):   # cheminées
        d.rectangle((cx - 30, HOR - h_, cx + 30, HOR - 300), fill=dk)
        for j in range(4):
            r = 40 + j * 22
            d.ellipse((cx - r + j * 30, HOR - h_ - 60 - j * 70 - r, cx + r + j * 30, HOR - h_ - 60 - j * 70 + r), fill=(90, 94, 110) if not gold else (230, 200, 190))
    _ground(d, (60, 64, 76) if not gold else (170, 140, 110), (30, 32, 40) if not gold else (110, 86, 70), 0.0)
    d.polygon([proj(W / 2 - 260, 0.5), proj(W / 2 + 260, 0.5), proj(W / 2 + 260, 6), proj(W / 2 - 260, 6)], fill=(40, 42, 52) if not gold else (140, 110, 90))
    # grillage + portail fermé au loin
    gz = 3.2
    a = proj(-2000, gz); b = proj(W + 2000, gz); hh = 300 / gz
    for xx in np.arange(a[0], b[0], 14): d.line((xx, a[1], xx + 8, a[1] - hh), fill=(120, 126, 140), width=1)
    d.line((a[0], a[1] - hh, b[0], b[1] - hh), fill=(150, 156, 170), width=4)
    ga = proj(W / 2 - 300, gz); gb = proj(W / 2 + 300, gz)
    d.rectangle((ga[0], ga[1] - hh * 1.2, gb[0], ga[1]), outline=(200, 200, 210), width=5)
    for xx in np.arange(ga[0], gb[0], 18): d.line((xx, ga[1] - hh * 1.2, xx, ga[1]), fill=(190, 190, 200), width=3)
    if not gold:
        for xx in (W / 2 - 120, W / 2 + 160):
            _glow(img, (xx - 60, HOR + 100, xx + 60, H - 300), (255, 220, 160), 40, 30)
    return img

def make_store():
    """grand magasin : sol de marbre brillant, colonnes, lustres, vitrines éclairées (sans enseigne)"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR, (60, 40, 50), (150, 110, 90), 1.0)
    for i, x0 in enumerate(np.arange(60, W, 250)):   # vitrines du fond
        d.rectangle((x0, HOR - 340, x0 + 190, HOR - 40), fill=(255, 226, 180))
        d.rectangle((x0 + 20, HOR - 300, x0 + 170, HOR - 220), fill=(230, 180, 150))
        d.rectangle((x0 + 40, HOR - 200, x0 + 150, HOR - 60), fill=(240, 200, 170))
    _glow(img, (0, HOR - 420, W, HOR + 40), (255, 220, 170), 90, 50); d = ImageDraw.Draw(img)
    _ground(d, (226, 214, 200), (170, 150, 136), 0.04)
    for z in np.arange(0.6, 10, 0.8):
        d.line((proj(-3000, z), proj(W + 3000, z)), fill=(200, 186, 170), width=max(1, int(4 / z)))
    for xw in np.arange(-2400, W + 2500, 300): d.line((proj(xw, 0.55), proj(xw, 10)), fill=(200, 186, 170), width=2)
    for side in (-1, 1):   # colonnes
        for z in (1.2, 2.0, 3.2, 5.0, 7.5):
            q = proj(W / 2 + side * 640, z); w_ = 60 / z
            d.rectangle((q[0] - w_, 0, q[0] + w_, q[1]), fill=(236, 226, 214))
            d.rectangle((q[0] - w_ * 0.4, 0, q[0] - w_ * 0.1, q[1]), fill=(255, 250, 240))
            d.rectangle((q[0] - w_ * 1.3, q[1] - 30 / z, q[0] + w_ * 1.3, q[1]), fill=(200, 186, 170))
    for cx, cy, r in ((W / 2, 140, 120), (W / 2 - 330, 300, 70), (W / 2 + 330, 300, 70)):   # lustres
        _glow(img, (cx - r * 2.4, cy - r * 2, cx + r * 2.4, cy + r * 2.4), (255, 230, 170), 170, 40); d = ImageDraw.Draw(img)
        d.polygon([(cx - r, cy), (cx + r, cy), (cx, cy + r * 1.3)], fill=(255, 240, 200))
        for j in range(7): d.ellipse((cx - r + j * r / 3 - 6, cy + 4, cx - r + j * r / 3 + 6, cy + 16), fill=(255, 255, 240))
    return img

COR_N = make_corridor("night"); COR_G = make_corridor("gold")
EXAM = make_exam(); FLAT = make_flat(); FAC_R = make_factory("rain"); FAC_G = make_factory("gold"); STORE = make_store()
FACR_ARR = np.asarray(FAC_R.convert("RGB")).astype(np.float32); CORG_ARR = np.asarray(COR_G.convert("RGB")).astype(np.float32)

# ---------------------------------------------------------------- objets
def series_banner(d, tg):
    if tg > 4.6 or tg < 0.5: return
    e = eout((tg - 0.5) / 0.25); o = ease((tg - 4.25) / 0.35)
    y = -150 + 220 * e - 260 * o
    d.rounded_rectangle((90, y, W - 90, y + 130), 22, fill=(96, 24, 40), outline=GOLD, width=5)
    text(d, (W / 2, y + 45), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), WHITE, BOLD)
    text(d, (W / 2, y + 98), "ÉPISODE 19", 40, GOLD, MONO)

def card_tear(img, cx, cy, k):
    """carte de visite déchirée en deux, les moitiés s'écartent et tombent"""
    if k <= 0: return
    u = eout(min(1, k / 0.5)); fall = max(0, k - 0.8) ** 2 * 400
    for side in (-1, 1):
        L = Image.new("RGBA", (220, 260), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.rectangle((10, 10, 210, 250), fill=(250, 248, 240, 255))
        dl.rectangle((30, 40, 170, 60), fill=(60, 66, 90, 255)); dl.rectangle((30, 90, 140, 102), fill=(170, 170, 180, 255)); dl.rectangle((30, 120, 160, 132), fill=(170, 170, 180, 255))
        pts = [(210 if side < 0 else 10, 10)] + [((200 if side < 0 else 20) + 12 * math.sin(i * 1.7), 10 + i * 30) for i in range(9)]
        if side > 0: L = L.transpose(Image.FLIP_LEFT_RIGHT)
        L = L.rotate(-side * 25 * u, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(L, (int(cx - L.width / 2 + side * (130 + 160 * u)), int(cy - L.height / 2 + fall)))

def scissors(d, cx, cy, s, op):
    """ciseaux : deux lames qui s'ouvrent (op 0..1)"""
    a = math.radians(8 + 22 * op)
    for sg in (-1, 1):
        ang = math.pi + sg * a
        x2 = cx + 260 * s * math.cos(ang); y2 = cy + 260 * s * math.sin(ang)
        d.line((cx, cy, x2, y2), fill=(220, 226, 236), width=int(18 * s))
        xh = cx - 110 * s * math.cos(ang); yh = cy - 110 * s * math.sin(ang)
        d.ellipse((xh - 50 * s, yh - 34 * s, xh + 50 * s, yh + 34 * s), outline=(255, 120, 60), width=int(16 * s))
    d.ellipse((cx - 12 * s, cy - 12 * s, cx + 12 * s, cy + 12 * s), fill=(90, 96, 110))

def tights(d, cx, cy, s, cut):
    """collant posé à plat : deux jambes ; à la coupe, les pieds s'en vont"""
    col = (40, 40, 48); ol = (120, 120, 140)
    d.rounded_rectangle((cx - 120 * s, cy - 220 * s, cx + 120 * s, cy - 120 * s), int(30 * s), fill=col, outline=ol, width=3)
    for sg in (-1, 1):
        d.rounded_rectangle((cx + sg * 70 * s - 48 * s, cy - 150 * s, cx + sg * 70 * s + 48 * s, cy + 200 * s), int(40 * s), fill=col, outline=ol, width=3)
        fy = cy + 200 * s + cut * 220 * s; fx = cx + sg * (70 + cut * 80) * s
        d.rounded_rectangle((fx - 48 * s, fy, fx + 48 * s, fy + 90 * s), int(40 * s), fill=col, outline=ol, width=3)
    if cut > 0: d.line((cx - 160 * s, cy + 200 * s, cx + 160 * s, cy + 200 * s), fill=(255, 200, 120), width=4)

def jar(d, cx, cy, s, empty=0.0):
    d.rounded_rectangle((cx - 90 * s, cy - 120 * s, cx + 90 * s, cy + 120 * s), int(30 * s), outline=(200, 220, 240), width=6)
    lvl = (1 - empty) * 200 * s
    if lvl > 4: d.rounded_rectangle((cx - 80 * s, cy + 110 * s - lvl, cx + 80 * s, cy + 110 * s), int(24 * s), fill=GOLD)
    d.rectangle((cx - 70 * s, cy - 140 * s, cx + 70 * s, cy - 118 * s), fill=(160, 170, 190))

def phone(d, cx, cy, s, k):
    if k <= 0: return
    sh = 10 * math.sin(k * 60) * max(0, 1 - k / 1.2)
    d.rounded_rectangle((cx - 80 * s + sh, cy - 150 * s, cx + 80 * s + sh, cy + 150 * s), int(24 * s), fill=(24, 26, 36), outline=WHITE, width=5)
    d.rounded_rectangle((cx - 64 * s + sh, cy - 120 * s, cx + 64 * s + sh, cy + 110 * s), int(10 * s), fill=(60, 200, 120))
    text(d, (cx + sh, cy - 10 * s), "OUI ?", int(44 * s), WHITE, BOLD)
    for i in range(3):
        r = (60 + i * 40 + (k * 120) % 40) * s
        d.arc((cx + 70 * s - r, cy - 150 * s - r, cx + 70 * s + r, cy - 150 * s + r), 300, 360, fill=(120, 255, 170), width=5)

def heart(d, cx, cy, r, col, k=1.0):
    if k <= 0: return
    r = r * pop(k, 100, 0.3, 0.25) / 100
    d.ellipse((cx - r, cy - r * 0.8, cx, cy + r * 0.2), fill=col); d.ellipse((cx, cy - r * 0.8, cx + r, cy + r * 0.2), fill=col)
    d.polygon([(cx - r * 0.98, cy - r * 0.15), (cx + r * 0.98, cy - r * 0.15), (cx, cy + r * 1.1)], fill=col)

def globe(d, cx, cy, r, k, col=ICE):
    if k <= 0: return
    a = eout(min(1, k / 0.4)); r *= a
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=6)
    for i in range(1, 4):
        w_ = r * abs(math.cos(k * 1.5 + i * 0.8)); d.ellipse((cx - w_, cy - r, cx + w_, cy + r), outline=col, width=3)
    for f in (-0.5, 0, 0.5):
        y = cy + f * r; hw = r * math.sqrt(1 - f * f); d.line((cx - hw, y, cx + hw, y), fill=col, width=3)

def light_door(img, cx, by, w, h, op, a=1.0):
    """porte de lumière qui s'ouvre au centre (cri / regard)"""
    if a <= 0: return
    _glow(img, (cx - w * 1.6, by - h * 1.3, cx + w * 1.6, by + h * 0.3), (255, 220, 150), int(200 * a), 60)
    d = ImageDraw.Draw(img)
    d.rectangle((cx - w / 2, by - h, cx + w / 2, by), fill=mix((40, 30, 30), (255, 244, 210), a))
    pw = w * (1 - op)
    if pw > 4: d.polygon([(cx - w / 2, by - h), (cx - w / 2 + pw, by - h - 30 * op), (cx - w / 2 + pw, by + 30 * op), (cx - w / 2, by)], fill=(150, 96, 64), outline=(60, 40, 30))

# ---------------------------------------------------------------- scènes
def _doors_slam(d, tg, t0, n=5, every=0.35):
    """portes qui claquent les unes après les autres à partir de t0 (ouvertes avant)"""
    for i, z in enumerate(DOORZ[:n]):
        for side in (-1, 1):
            tc = t0 + (i * 2 + (side > 0)) * every * 0.5
            op = 1.0 if tg < tc else max(0.0, 1 - ((tg - tc) / 0.12)) 
            if op > 0.01: door_swing(d, side, z, op)

def s_hook(img, d, tg, k):
    img.paste(COR_N); d = ImageDraw.Draw(img)
    _doors_slam(d, tg, M("porte1", 0.5) + 0.25, 5, 0.32)
    shadow(d, W / 2, FEET, 250); P(img, W / 2, FEET, 250, "sad" if tg > M("fermes", 99) else "stand"); d = ImageDraw.Draw(img)
    topsh(img); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    hit = 0.0
    sc = 1 + 0.3 * (1 - eout((tg + 0.12) / 0.2))
    text(d, (W / 2, 400), "ON T'A CLAQUÉ", fit("ON T'A CLAQUÉ", int(130 * sc), 900), WHITE, BOLD, stroke=8, scol=BG)
    kp = kM(tg, "porte1")
    text(d, (W / 2, 550), "LA PORTE AU NEZ ?", pop(max(kp, 0.01), fit("LA PORTE AU NEZ ?", 120, 900), 0.25, 0.2), ORANGE, BOLD, stroke=10, scol=BG)
    if 0 < kp < 2.5:   # BAM des portes
        hit = max(0, 1 - (kp - 0.25) / 0.3) if kp > 0.25 else 0
    kn = kM(tg, "non1")
    if kn > 0 and kM(tg, "sept1") <= 0: hit = max(hit, stamp(img, "NON", (W / 2, 760), 150, -8, kn, RED2))
    ks = kM(tg, "sept1")
    if ks > 0: badge(d, W / 2, 720, "7 ANS", ks, GOLD, 110)
    kf = kM(tg, "fermes")
    if kf > 0: hit = max(hit, stamp(img, "PORTES FERMÉES", (W / 2, 950), 88, -5, kf, RED2))
    return dict(hit=hit, shake=hit * 0.8)

def s_intro(img, d, tg, k):
    img.paste(COR_N); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 300, "L'HISTOIRE VRAIE", 100, WHITE, k)
    TX(d, 430, "D'UNE VENDEUSE", 110, ORANGE, k - 0.5)
    TX(d, 560, "DEVENUE ENTREPRENEUSE", 70, AMBER, k - 0.9)
    return dict(hit=0.0)

def s_droit(img, d, tg, k):
    img.paste(EXAM); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 245, (60, 40, 30))
    kr = kM(tg, "rate"); kp = kM(tg, "pire")
    P(img, W / 2, FEET, 245, "sad" if kp > 0 else ("shy" if kr > 0 else "stand")); d = ImageDraw.Draw(img)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    TX(d, 270, "ELLE VEUT DEVENIR", 80, WHITE, k)
    TX(d, 380, "AVOCATE", 140, ICE, kM(tg, "avocate"))
    hit = 0.0
    if kr > 0:
        paper(img, W / 2 - 190, 760, kr); d = ImageDraw.Draw(img)
        hit = stamp(img, "RATÉ", (W / 2 - 190, 760), 110, -10, kr + 0.3, RED2)
    krp = kM(tg, "repasse")
    if krp > 0:
        paper(img, W / 2 + 200, 790, krp); d = ImageDraw.Draw(img)
    if kp > 0: hit = max(hit, stamp(img, "ENCORE PIRE", (W / 2 + 200, 790), 92, 8, kp, RED2))
    return dict(hit=hit)

def s_fax(img, d, tg, k):
    img.paste(COR_N); d = ImageDraw.Draw(img)
    kc = kM(tg, "claquent")
    _doors_slam(d, tg, M("claquent", 99) + 0.05, 5, 0.22)
    shadow(d, W / 2, FEET, 245); P(img, W / 2, FEET, 245, "sad" if kM(tg, "sortir") > 0 else run_pose(tg * 6)); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    hit = 0.0
    TX(d, 270, "VENDEUSE DE FAX", 100, WHITE, kM(tg, "fax"))
    TX(d, 390, "AU PORTE-À-PORTE", 90, AMBER, kM(tg, "pap"))
    ks = kM(tg, "sept2")
    if ks > 0 and kc <= 0: counter(d, 560, 1, 7, ks, 0.5, 170, GOLD, "{} ANS")
    if 0 < kc < 0.9: hit = stamp(img, "BAM !", (W / 2, 600), 160, -8, kc, RED2)
    kd = kM(tg, "dechire")
    if kd > 0 and kM(tg, "sortir") <= 0: card_tear(img, W / 2, 680, kd); d = ImageDraw.Draw(img)
    ko = kM(tg, "sortir")
    if ko > 0: hit = max(hit, stamp(img, "DEHORS !", (W / 2, 620), 150, -6, ko, RED2))
    return dict(hit=hit, shake=hit * 0.7)

def s_idee(img, d, tg, k):
    ku = kM(tg, "usines")
    hit = 0.0
    if ku <= 0:
        img.paste(FLAT); d = ImageDraw.Draw(img)
        shadow(d, W / 2 + 240, FEET, 235, (50, 30, 20)); P(img, W / 2 + 240, FEET, 235, "stand", facing=-1); d = ImageDraw.Draw(img)
        topsh(img, 0.8); d = ImageDraw.Draw(img)
        badge(d, 180, 330, "27 ANS", kM(tg, "a27"), GOLD, 110)
        TX(d, 300, "UN SOIR…", 90, WHITE, kM(tg, "a27") + 0.3, x=W / 2 + 90, maxw=700)
        kc = kM(tg, "coupe"); ki = kM(tg, "idee"); ke = kM(tg, "economies")
        if ke > 0:
            TX(d, 430, "TOUTES SES ÉCONOMIES", 80, GOLD, ke)
            jar(d, W / 2, 780, 1.3, min(1, ke / 0.9)); return dict(hit=0.0)
        if kc > -0.3:
            cut = eout(max(0, kc - 0.6) / 0.6)
            tights(d, W / 2 - 80, 820, 1.15, cut)
            op = abs(math.sin(max(0, kc) * 7)) if kc < 1.2 else 0.2
            scissors(d, W / 2 + 120, 1050, 0.9, op)
        if ki > 0:
            TX(d, 430, "UNE IDÉE QUI", 84, ORANGE, ki)
            TX(d, 540, "N'EXISTE PAS ENCORE", 76, WHITE, ki - 0.2)
        return dict(hit=0.0)
    img.paste(FAC_R); d = ImageDraw.Draw(img); rainfall(d, tg, 0.9)
    shadow(d, W / 2, FEET, 245); P(img, W / 2, FEET, 245, run_pose(tg * 6) if kM(tg, "toutes") <= 0 else "sad"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 280, "LES USINES", 120, WHITE, ku)
    kt = kM(tg, "toutes")
    for i in range(3):
        if kt - i * 0.22 > 0: hit = max(hit, stamp(img, "NON", (W / 2 + (i - 1) * 300, 520 + (i % 2) * 120), 120, (-10, 6, -4)[i], kt - i * 0.22, RED2))
    if kt > 0.7: TX(d, 800, "TOUTES", 130, RED2, kt - 0.7)
    return dict(hit=hit, shake=hit * 0.6)

def s_doute(img, d, tg, k):
    kf = kM(tg, "pour_moi"); hit = 0.0
    img.paste(FAC_R); d = ImageDraw.Draw(img); rainfall(d, tg, 1.0)
    shadow(d, W / 2, FEET, 250)
    P(img, W / 2, FEET - 90 / ZF, 250, "kneel"); d = ImageDraw.Draw(img)
    dim(img, 0.25); topsh(img); d = ImageDraw.Draw(img)
    TX(d, 280, "ELLE AURAIT PU SE DIRE…", 80, WHITE, kM(tg, "aurait"))
    if kf > 0: hit = stamp(img, "« PAS POUR MOI »", (W / 2, 520), 120, -6, kf, RED2)
    return dict(hit=hit)

def s_cri(img, d, tg, k):
    kb_ = tg - K["boom"]; kk = max(0.0, kb_ + 0.06); kr = kM(tg, "porte_cri")
    c = (W / 2, 820)
    r = eout(max(0, kr) / 1.0) * 2300 if kr > 0 else 0
    img.paste(reveal(FACR_ARR, CORG_ARR, c, r)); d = ImageDraw.Draw(img)
    if kr < 0.6: rainfall(d, tg, max(0, 1 - max(0, kr) / 0.6))
    op = eout(max(0, kk) / (max(0.3, M("porte_cri", 99) - K["boom"]) + 0.2))
    light_door(img, W / 2, FEET - 40, 420, 820, op, min(1, kk / 0.3)); d = ImageDraw.Draw(img)
    rays(img, min(1, max(0, kr) / 0.5)); d = ImageDraw.Draw(img)
    rings(img, c, kr, 6, GOLD, 1050, 16, 0.14, 1.25); d = ImageDraw.Draw(img)
    burst(d, c[0], c[1], kr, 26, 520, (255, 240, 190), 3, 10)
    shadow(d, W / 2, FEET, 270)
    P(img, W / 2, FEET, 270, POSES["sad"] if kb_ < 0 else (POSES["up"] if kr > 0 else POSES["shout"])); d = ImageDraw.Draw(img)
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    hit = max(0, 1 - kk / 0.3) if kk > 0 else 0
    e = eout(kk / 0.22) if kk > 0 else 0
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, eout(max(0, kr) / 0.22))
    f1 = fit("ELLE VA OUVRIR", 130, 960); f2 = pop(kr, fit("SA PROPRE PORTE !", 120, 980), 0.08)
    for off, cc in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        if kb_ > 0: text(d, (x1 + o, 400), "ELLE VA OUVRIR", f1, cc, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
        if kr > 0: text(d, (x2 - o, 560), "SA PROPRE PORTE !", f2, cc if cc != WHITE else GOLD, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
    hr = max(0, 1 - kr / 0.3) if kr > 0 else 0
    return dict(hit=max(hit, hr) * 1.6, shake=max(hit, hr) * 1.9, flash=max(0, 0.9 - kr * 2.6) if kr > 0 else 0)

def s_usine(img, d, tg, k):
    kr = kM(tg, "rappelle"); kt = kM(tg, "trois"); kc = kM(tg, "convaincu"); hit = 0.0
    img.paste(FAC_G); d = ImageDraw.Draw(img)
    shadow(d, W / 2 + 200, FEET, 245); P(img, W / 2 + 200, FEET, 245, "up" if kc > 0 else "stand", facing=-1); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 260, "2 SEMAINES PLUS TARD…", 84, WHITE, k)
    if kr > 0 and kt <= 0: phone(d, W / 2 - 200, 700, 1.3, kr)
    if kt > 0:
        TX(d, 420, "SES 3 FILLES", 120, ORANGE, kt)
        for i in range(3):   # trois petites silhouettes
            P(img, W / 2 - 300 + i * 150, 1000, 110 + i * 8, "up" if kc > 0 else "stand", fixed=True)
        d = ImageDraw.Draw(img)
        TX(d, 560, "L'ONT CONVAINCU", 84, WHITE, kt + 0.4)
    if kc > 0: hit = stamp(img, "OUI !", (W / 2 + 230, 780), 130, -6, kc + 0.25, (60, 200, 120))
    return dict(hit=hit, flash=0.3 * max(0, 1 - kc / 0.25) if 0 < kc < 0.25 else 0)

def s_magasin(img, d, tg, k):
    kt = kM(tg, "toilettes"); kv = kM(tg, "vendu"); hit = 0.0
    img.paste(STORE); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 250, (150, 130, 110)); P(img, W / 2, FEET, 250, "point" if kt > 0 and kv <= 0 else ("up" if kv > 0 else run_pose(tg * 6))); d = ImageDraw.Draw(img)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    TX(d, 260, "UN GRAND MAGASIN", 100, WHITE, kM(tg, "magasin"))
    TX(d, 380, "RENDEZ-VOUS", 90, GOLD, kM(tg, "magasin") + 0.6)
    if kt > 0 and kv <= 0:
        TX(d, 540, "ELLE LE MONTRE", 90, ORANGE, kt)
        TX(d, 650, "ELLE-MÊME", 110, WHITE, kt + 0.3)
    if kv > 0:
        hit = stamp(img, "VENDU !", (W / 2, 560), 160, -6, kv, GOLD)
        counter(d, 780, 1, 7, kM(tg, "sept3"), 0.6, 150, WHITE, "{} MAGASINS")
    return dict(hit=hit, flash=0.3 * max(0, 1 - kv / 0.25) if 0 < kv < 0.25 else 0)

def s_succes(img, d, tg, k):
    kc = kM(tg, "coeur"); ke = kM(tg, "entreprise"); hit = 0.0
    img.paste(STORE); d = ImageDraw.Draw(img); confetti(d, max(0, kc) * 0.6, 0.7 if kc > 0 else 0)
    shadow(d, W / 2, FEET, 255, (150, 130, 110)); P(img, W / 2, FEET - (14 * abs(math.sin(k * 6)) if kc > 0 else 0), 255, "up" if kc > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    if ke <= 0:
        TX(d, 260, "2000", 130, WHITE, kM(tg, "y2000"))
        TX(d, 390, "UNE CÉLÈBRE PRÉSENTATRICE", 64, ICE, kM(tg, "y2000") + 0.4)
        if kc > 0:
            heart(d, W / 2, 760, 150, PINK, kc)
            hit = stamp(img, "COUP DE CŒUR", (W / 2, 560), 110, -5, kc, GOLD)
        return dict(hit=hit)
    TX(d, 270, "SON ENTREPRISE", 100, WHITE, ke)
    globe(d, W / 2, 720, 210, ke, ICE)
    km = kM(tg, "monde")
    if km > 0: hit = stamp(img, "DANS LE MONDE ENTIER", (W / 2, 450), 84, -4, km, GOLD)
    return dict(hit=hit)

def s_regard(img, d, tg, k):
    ks = kM(tg, "sienne"); hit = 0.0
    img.paste(COR_G); d = ImageDraw.Draw(img)
    light_door(img, W / 2, HOR + (FEET - HOR) / 3.0, 300 / 3.0 * 3, 760 / 3.0 * 1.6, eout(max(0, ks) / 0.6), 1.0 if ks > 0 else 0.35); d = ImageDraw.Draw(img)
    rays(img, 0.4 + 0.5 * min(1, max(0, ks) / 0.5)); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 255, (120, 90, 70)); P(img, W / 2, FEET, 255, "up" if ks > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 250, "ON LUI FERMAIT", 96, WHITE, kM(tg, "femme"))
    TX(d, 360, "TOUTES LES PORTES…", 92, ICE, kM(tg, "portes"))
    if ks > 0: hit = stamp(img, "ELLE A OUVERT LA SIENNE", (W / 2, 540), 84, -4, ks, GOLD)
    return dict(hit=hit, flash=0.4 * max(0, 1 - ks / 0.25) if ks > 0 else 0)

def s_you(img, d, tg, k):
    kf = kM(tg, "fermee"); kv = kM(tg, "vie"); hit = 0.0
    img.paste(COR_N); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET, 262, blend_pose(POSES["stand"], POSES["point"], eout(max(0, k) / 0.4)))
    dim(img, 0.25); topsh(img); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(150 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=8, scol=BG)
    TX(d, 470, "UNE PORTE FERMÉE", 100, WHITE, kf)
    if kv > 0: hit = stamp(img, "VA DÉCIDER DE TA VIE ?", (W / 2, 630), 90, -4, kv, GOLD)
    return dict(hit=hit)

STAD_AMAT = COR_N

def s_abonne(img, d, tg, k):
    img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
    dim(img, 0.6); d = ImageDraw.Draw(img)
    hit = 0.0
    P(img, 200, FEET + 20, 215, "point", fixed=True); d = ImageDraw.Draw(img)
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rounded_rectangle((W / 2 - bw / 2, 420 - bh / 2, W / 2 + bw / 2, 420 + bh / 2), int(40 * sc), fill=RED)
    text(d, (W / 2 - bw / 2 + 90 * sc, 420), "+", int(130 * sc), WHITE, BOLD)
    text(d, (W / 2 + 50 * sc, 420), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE, BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = kM(tg, "demain")
    if kd > 0:
        TX(d, 660, "DEMAIN · ÉPISODE 20", 74, GOLD, kd)
        kc = kM(tg, "mecanicien")
        if kc > 0:
            text(d, (W / 2, 770), typew("LE MÉCANICIEN DONT", kc, 30), fit("LE MÉCANICIEN DONT", 68, 960), WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 860), typew("L'USINE A ÉTÉ DÉTRUITE…", kc - 0.6, 30), fit("L'USINE A ÉTÉ DÉTRUITE…", 68, 960), WHITE, BOLD, stroke=6, scol=BG)
    return dict(hit=hit)

SCENES = {"hook": s_hook, "intro": s_intro, "droit": s_droit, "fax": s_fax, "idee": s_idee, "doute": s_doute, "cri": s_cri,
          "usine": s_usine, "magasin": s_magasin, "succes": s_succes, "regard": s_regard, "you": s_you,
          "abonne": s_abonne, "question": s_question, "logo": s_logo}

def PATH(typ, k, tg):
    st = SC[typ]
    if typ == "hook":    return _seg(k, [(0, 1.0, 0, 0), (4.0, 1.15, 0, 0)]) + (False,)
    if typ == "intro":   return _seg(k, [(0, 2.6, 0, 0), (1.8, 1.05, 0, 0)]) + (False,)
    if typ == "droit":   return _seg(k, [(0, 2.2, -200, 0), (2.0, 1.05, 0, 0)]) + (False,)
    if typ == "fax":     # elle avance dans le couloir, de porte en porte, vers la caméra
        o = MK_("sortir") - st
        if k < o: return _seg(k, [(0, 3.4, 0, 0), (o, 1.15, 0, 0)]) + (False,)
        return _seg(k, [(o, 1.15, 0, 0), (o + 1.0, 1.6, -180, 0)]) + (False,)
    if typ == "idee":
        u = MK_("usines") - st
        if k < u: return (1.0, 0.0, 0.0, 0.0, False)
        return _seg(k, [(u, 2.6, 0, 0), (u + 1.4, 1.1, 0, 0)]) + (False,)
    if typ == "doute":   return _seg(k, [(0, 1.5, 0, 0), (2.0, 1.0, 0, 0)]) + (False,)
    if typ == "cri":
        r = MK_("porte_cri") - st
        return _seg(k, [(0, 1.6, 0, 0), (r, 1.6, 0, 0), (r + 1.2, 0.95, 0, 0)]) + (False,)
    if typ == "usine":   return _seg(k, [(0, 2.4, 200, 0), (2.0, 1.05, 0, 0)]) + (False,)
    if typ == "magasin": return _seg(k, [(0, 3.0, 0, 0), (2.0, 1.05, 0, 0)]) + (False,)
    if typ == "succes":  return _seg(k, [(0, 1.3, 0, 0), (3.0, 1.0, 0, 0)]) + (False,)
    if typ == "regard":  return _seg(k, [(0, 1.0, 0, 0), (3.4, 2.4, 0, 0)]) + (False,)   # elle marche vers la porte de lumière
    if typ == "you":     return _seg(k, [(0, 1.35, -150, 0), (2.0, 0.9, 60, 0)]) + (False,)
    return (1.0, 0.0, 0.0, 0.0, False)

def CAMF(typ, k, tg):
    hh = (6 * math.sin(tg * 2.1), 5 * math.sin(tg * 1.7 + 1))
    dur = 3.0
    for s_ in SCN:
        if s_["type"] == typ: dur = s_["end"] - s_["start"]
    u = ease(k / max(0.5, dur))
    if typ == "hook":    return (lerp(1.25, 1.08, u), lerp(40, -30, u) + hh[0], lerp(50, 0, u) + hh[1], lerp(0.06, -0.03, u), -0.03, lerp(-1.5, 0, u))
    if typ == "intro":   return (lerp(1.08, 1.18, u), lerp(-60, 60, u), hh[1], lerp(0.08, -0.05, u), 0.05, 0.0)
    if typ == "droit":   return (lerp(1.18, 1.06, u), lerp(70, -50, u) + hh[0], hh[1], lerp(-0.07, 0.07, u), -0.05, 0.0)
    if typ == "fax":     return (1.1 + 0.02 * math.sin(tg * 7), hh[0] * 2, hh[1] * 2 + 6 * math.sin(tg * 7), lerp(0.07, -0.07, u), 0.04, 1.0 * math.sin(tg * 3.5))
    if typ == "idee":    return (lerp(1.06, 1.2, u), hh[0], lerp(30, -30, u), lerp(0.06, -0.06, u), 0.05, 0.0)
    if typ == "doute":   return (lerp(1.06, 1.22, u), hh[0], lerp(0, -40, u), 0.0, 0.06, 0.0)
    if typ == "cri":
        kb = max(0.0, tg - M("porte_cri", 99))
        orb = math.sin(min(1, kb / 1.8) * math.pi) * 0.13
        return (1.08 + 0.2 * math.exp(-kb * 3) if kb > 0 else 1.1, hh[0] * 2, hh[1], orb, 0.06 if kb > 0 else 0.0, 3 * math.sin(kb * 4) * math.exp(-kb * 2))
    if typ == "usine":   return (lerp(1.2, 1.06, u), hh[0] * 1.5, lerp(-30, 30, u), lerp(-0.07, 0.05, u), -0.04, 0.0)
    if typ == "magasin": return (lerp(1.08, 1.2, u), lerp(-80, 60, u) + hh[0], hh[1], lerp(-0.07, 0.07, u), 0.03, 0.0)
    if typ == "succes":  return (lerp(1.06, 1.18, u), hh[0] * 2, hh[1], lerp(0.09, -0.09, u), 0.05, 1.0 * math.sin(tg * 3))
    if typ == "regard":  return (lerp(1.18, 1.06, u), hh[0], lerp(-40, 30, u), lerp(0.08, -0.06, u), 0.05, 0.0)
    if typ == "you":     return (lerp(1.06, 1.16, u), lerp(-60, 30, u) + hh[0], hh[1], lerp(0.06, -0.04, u), 0.0, 0.0)
    return None

# =============================================================== ép. 20 (27/11/2026) — Soichiro Honda « Tu as tout perdu ? » (2e histoire BUSINESS)
# Décors NOUVEAUX : USINE EN RUINES (murs de briques brisés, poutres tombées, gravats, poussière) aube grise / dorée avec un petit atelier neuf,
# VILLAGE JAPONAIS au crépuscule (montagnes génériques, rizières en terrasses, maisons en bois aux toits courbes, forge rougeoyante),
# GARAGE-ATELIER la nuit / doré (panneau d'outils, établi, lampe suspendue, moteur sur support, pneus), ROUTE CÔTIÈRE de course (falaises, mer, murets).
# Héros = silhouette lumineuse masculine (on retire la queue de cheval de l'ép. 19). Aucun logo, marque ni nom à l'écran.
_PLAYER0 = _PL_ORIG
RED2 = (255, 70, 60); GREEN2 = (70, 220, 120)

def _dust(d, tg, amt=1.0, col=(200, 190, 170), seed=3):
    r = np.random.default_rng(seed)
    for i in range(90):
        x0, y0, sp = r.uniform(0, W), r.uniform(0, H), r.uniform(0.3, 1.0)
        x = (x0 + tg * 40 * sp) % W; y = (y0 - tg * 25 * sp) % H; s = 2 + 3 * sp
        c = mix((30, 30, 40), col, amt * sp)
        d.ellipse((x - s, y - s, x + s, y + s), fill=c)

def _mountains(d, cfar, cnear, snow=None):
    for (pts, c) in (([(-100, HOR - 250), (120, HOR - 470), (330, HOR - 330), (520, HOR - 560), (760, HOR - 360), (940, HOR - 500), (1200, HOR - 300), (1200, HOR), (-100, HOR)], cfar),
                     ([(-100, HOR - 120), (200, HOR - 280), (420, HOR - 170), (700, HOR - 300), (980, HOR - 160), (1200, HOR - 230), (1200, HOR), (-100, HOR)], cnear)):
        d.polygon(pts, fill=c)
    if snow:
        for (x, y) in ((520, HOR - 560), (120, HOR - 470), (940, HOR - 500)):
            d.polygon([(x, y), (x - 55, y + 70), (x - 20, y + 55), (x + 10, y + 75), (x + 50, y + 62)], fill=snow)

def _jhouse(d, cx, by, w, h, wall, roof, lit=None):
    """maison en bois au toit de tuiles courbé (générique)"""
    d.rectangle((cx - w / 2, by - h, cx + w / 2, by), fill=wall)
    for i in range(1, 4): d.line((cx - w / 2 + i * w / 4, by - h, cx - w / 2 + i * w / 4, by), fill=mix(wall, (0, 0, 0), 0.35), width=max(1, int(w / 60)))
    if lit: d.rectangle((cx - w * 0.3, by - h * 0.7, cx + w * 0.3, by - h * 0.25), fill=lit)
    rh = h * 0.55; ov = w * 0.18
    pts = [(cx - w / 2 - ov, by - h + rh * 0.05)]
    for u in np.linspace(0, 1, 9):
        x = lerp(cx - w / 2 - ov, cx, u); y = by - h - rh * (u ** 0.7) + rh * 0.12 * math.sin(u * math.pi) * 0
        pts.append((x, y - rh * 0.15 * (1 - u) ** 3 * 0))
    pts.append((cx, by - h - rh))
    for u in np.linspace(0, 1, 9):
        x = lerp(cx, cx + w / 2 + ov, u); y = by - h - rh * ((1 - u) ** 0.7)
        pts.append((x, y))
    pts.append((cx + w / 2 + ov, by - h + rh * 0.05))
    # bords relevés
    pts = [(pts[0][0] - ov * 0.25, pts[0][1] - rh * 0.25)] + pts + [(pts[-1][0] + ov * 0.25, pts[-1][1] - rh * 0.25)]
    d.polygon(pts, fill=roof)
    d.line((cx - w * 0.15, by - h - rh, cx + w * 0.15, by - h - rh), fill=mix(roof, (0, 0, 0), 0.4), width=max(2, int(w / 30)))

def make_village(mode="dusk"):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR, (40, 36, 80), (250, 150, 110), 1.2)
    _glow(img, (W / 2 - 200, HOR - 360, W / 2 + 200, HOR + 40), (255, 190, 120), 160, 60); d = ImageDraw.Draw(img)
    _mountains(d, (90, 80, 120), (60, 54, 90), (230, 220, 235))
    _ground(d, (70, 96, 60), (36, 52, 34), 0.05)
    for z in np.arange(0.7, 8, 0.55):   # rizières en terrasses (reflets)
        a = proj(-3000, z); b = proj(W + 3000, z)
        d.line((a[0], a[1], b[0], b[1]), fill=(150, 130, 120), width=max(1, int(5 / z)))
    for xw, z, s in ((-500, 3.2, 1.0), (250, 4.5, 0.9), (W - 150, 3.6, 1.0), (W + 600, 2.7, 1.1), (W / 2 + 80, 7.0, 0.8)):
        q = proj(xw, z)
        _jhouse(d, q[0], q[1], 520 * s / z, 300 * s / z, (120, 86, 60), (46, 44, 56), (255, 190, 110))
    # forge rougeoyante à gauche (premier plan)
    q = proj(-150, 1.6)
    _jhouse(d, q[0], q[1], 520 / 1.6, 330 / 1.6, (96, 70, 52), (40, 38, 48), (255, 120, 50))
    _glow(img, (q[0] - 260, q[1] - 340, q[0] + 260, q[1] + 60), (255, 120, 40), 150, 50)
    return img

def make_ruins(mode="dawn"):
    gold = mode == "gold"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    if gold: _grad(d, 0, HOR, (90, 70, 120), (255, 190, 110), 1.1)
    else:    _grad(d, 0, HOR, (40, 46, 64), (120, 120, 130), 1.0)
    if gold:
        _glow(img, (W / 2 - 300, HOR - 420, W / 2 + 300, HOR + 60), (255, 210, 140), 220, 70); d = ImageDraw.Draw(img)
    brick = (120, 64, 50) if not gold else (190, 110, 76); dk = mix(brick, (0, 0, 0), 0.4)
    _ground(d, (90, 84, 80) if not gold else (180, 140, 100), (40, 38, 36) if not gold else (110, 80, 60), 0.05)
    rng = np.random.default_rng(45)
    # murs brisés (silhouettes en dents irrégulières)
    for x0, x1, hmax, z in ((-200, 380, 520, 3.0), (620, 1250, 600, 3.4), (200, 760, 300, 5.5)):
        a = proj(x0, z); b = proj(x1, z)
        xs = np.linspace(a[0], b[0], 14); top = [a[1] - rng.uniform(0.25, 1.0) * hmax / z * 2 for _ in xs]
        poly = [(a[0], a[1])] + list(zip(xs, top)) + [(b[0], b[1])]
        d.polygon(poly, fill=brick)
        for yy in np.arange(min(top), a[1], 14 / z * 3): d.line((a[0], yy, b[0], yy), fill=dk, width=1)
        for xx in xs[1:-1:3]:   # fenêtres vides
            ty = min(top); d.rectangle((xx - 18, a[1] - 120 / z * 3, xx + 18, a[1] - 60 / z * 3), fill=(30, 30, 40) if not gold else (255, 220, 150))
    # cheminée cassée
    q = proj(W - 200, 4.0); d.polygon([(q[0] - 26, q[1]), (q[0] + 26, q[1]), (q[0] + 22, q[1] - 300), (q[0] + 4, q[1] - 330), (q[0] - 22, q[1] - 290)], fill=dk)
    # poutres tombées + gravats au premier plan
    for (xa, za, xb, zb) in ((-300, 1.3, 300, 2.4), (W - 50, 1.5, W / 2 + 200, 2.8), (W / 2 - 500, 2.0, W / 2 + 100, 1.4)):
        pa = proj(xa, za); pb = proj(xb, zb)
        d.line((pa[0], pa[1] - 40, pb[0], pb[1] - 120), fill=(60, 44, 36) if not gold else (130, 90, 60), width=26)
    for i in range(70):
        z = rng.uniform(1.1, 6); xw = rng.uniform(-1500, W + 1500); q = proj(xw, z); r = rng.uniform(20, 60) / z
        d.polygon([(q[0] - r, q[1]), (q[0] - r * 0.3, q[1] - r * 0.9), (q[0] + r * 0.6, q[1] - r * 0.6), (q[0] + r, q[1])], fill=mix(brick, (60, 60, 60), rng.uniform(0, 0.5)))
    if gold:   # petit atelier neuf, fenêtre allumée, au fond
        q = proj(W / 2 + 40, 4.2); w_ = 600 / 4.2 * 2; h_ = 340 / 4.2 * 2
        d.rectangle((q[0] - w_ / 2, q[1] - h_, q[0] + w_ / 2, q[1]), fill=(160, 110, 70))
        d.polygon([(q[0] - w_ / 2 - 20, q[1] - h_), (q[0], q[1] - h_ - 70), (q[0] + w_ / 2 + 20, q[1] - h_)], fill=(80, 60, 60))
        d.rectangle((q[0] - w_ * 0.3, q[1] - h_ * 0.7, q[0] + w_ * 0.05, q[1] - h_ * 0.3), fill=(255, 230, 150))
        d.rectangle((q[0] + w_ * 0.15, q[1] - h_ * 0.75, q[0] + w_ * 0.38, q[1]), fill=(255, 210, 120))
        _glow(img, (q[0] - w_, q[1] - h_ * 1.4, q[0] + w_, q[1] + 40), (255, 210, 130), 90, 40)
    return img

def make_garage(mode="night"):
    gold = mode == "gold"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    wall = (56, 60, 74) if not gold else (150, 112, 84)
    d.rectangle((0, 0, W, HOR), fill=wall)
    for x in range(0, W, 120): d.line((x, 0, x, HOR), fill=mix(wall, (0, 0, 0), 0.18), width=3)
    # porte de garage ouverte sur la rue (nuit / soleil)
    d.rectangle((W - 420, HOR - 560, W - 40, HOR), fill=(16, 22, 46) if not gold else (255, 200, 130))
    if not gold: _stars(d, 20, HOR - 300, 5)
    d.rectangle((W - 420, HOR - 600, W - 40, HOR - 560), fill=(90, 90, 100))
    # panneau d'outils (clés, marteaux) à gauche
    d.rectangle((60, 300, 560, 700), fill=mix(wall, (255, 255, 255), 0.1))
    tc = (200, 206, 220) if not gold else (255, 236, 200)
    for i in range(5):
        x = 110 + i * 95
        d.line((x, 340, x, 560), fill=tc, width=12); d.ellipse((x - 24, 322, x + 24, 370), outline=tc, width=10)
    for i in range(3):
        x = 140 + i * 140; d.rectangle((x - 40, 600, x + 40, 630), fill=tc); d.line((x, 630, x, 690), fill=(140, 100, 70), width=12)
    _ground(d, (80, 82, 90) if not gold else (190, 150, 110), (40, 40, 46) if not gold else (110, 84, 64), 0.03)
    # établi
    a = proj(-260, 1.6); b = proj(380, 1.6)
    d.rectangle((a[0], a[1] - 260 / 1.6 * 1.6, b[0], a[1] - 230 / 1.6 * 1.6), fill=(150, 104, 66))
    d.rectangle((a[0] + 10, a[1] - 230, a[0] + 30, a[1]), fill=(90, 64, 44)); d.rectangle((b[0] - 30, a[1] - 230, b[0] - 10, a[1]), fill=(90, 64, 44))
    # pile de pneus à droite
    for j in range(3):
        q = proj(W + 120, 2.0); y = q[1] - j * 46
        d.ellipse((q[0] - 90, y - 40, q[0] + 90, y + 10), fill=(26, 26, 30), outline=(70, 70, 80), width=4)
    # lampe suspendue
    d.line((W / 2, 0, W / 2, 230), fill=(30, 30, 34), width=6)
    d.polygon([(W / 2 - 90, 300), (W / 2 + 90, 300), (W / 2 + 40, 230), (W / 2 - 40, 230)], fill=(60, 64, 70))
    _glow(img, (W / 2 - 420, 200, W / 2 + 420, HOR + 500), (255, 220, 150), 120 if not gold else 160, 80)
    return img

def make_coast(mode="day"):
    gold = mode == "gold"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR - 200, (70, 120, 190) if not gold else (110, 80, 140), (200, 220, 240) if not gold else (255, 190, 120), 1.0)
    d.rectangle((0, HOR - 200, W, HOR), fill=(40, 90, 140) if not gold else (200, 130, 110))
    for y in np.arange(HOR - 190, HOR, 18): d.line((0, y, W, y), fill=(90, 150, 200) if not gold else (255, 190, 140), width=2)
    # collines vertes à droite
    d.polygon([(W * 0.45, HOR), (W * 0.7, HOR - 260), (W, HOR - 330), (W, HOR)], fill=(60, 110, 60) if not gold else (150, 110, 70))
    _ground(d, (80, 130, 70) if not gold else (170, 130, 80), (40, 70, 40) if not gold else (110, 80, 50), 0.04)
    # route en perspective + murets de pierre
    d.polygon([proj(W / 2 - 300, 0.5), proj(W / 2 + 300, 0.5), proj(W / 2 + 300, 12), proj(W / 2 - 300, 12)], fill=(70, 72, 80) if not gold else (130, 110, 100))
    for z in np.arange(0.8, 12, 0.9):
        a = proj(W / 2 - 10, z); b = proj(W / 2 - 10, z + 0.4); d.line((a, b), fill=(240, 240, 240), width=max(1, int(10 / z)))
    for side in (-1, 1):
        for z in np.arange(0.6, 12, 0.35):
            q = proj(W / 2 + side * 340, z); hh = 50 / z
            d.rectangle((q[0] - 40 / z, q[1] - hh, q[0] + 40 / z, q[1]), fill=(150, 146, 136) if not gold else (210, 170, 130))
    return img

VIL = make_village(); RUIN_D = make_ruins("dawn"); RUIN_G = make_ruins("gold")
GAR_N = make_garage("night"); GAR_G = make_garage("gold"); COAST = make_coast("day"); COAST_G = make_coast("gold")
RUIND_ARR = np.asarray(RUIN_D.convert("RGB")).astype(np.float32); RUING_ARR = np.asarray(RUIN_G.convert("RGB")).astype(np.float32)
STAD_AMAT = GAR_N

# ---------------------------------------------------------------- objets
def series_banner(d, tg):
    if tg > 4.6 or tg < 0.5: return
    e = eout((tg - 0.5) / 0.25); o = ease((tg - 4.25) / 0.35)
    y = -150 + 220 * e - 260 * o
    d.rounded_rectangle((90, y, W - 90, y + 130), 22, fill=(96, 24, 40), outline=GOLD, width=5)
    text(d, (W / 2, y + 45), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), WHITE, BOLD)
    text(d, (W / 2, y + 98), "ÉPISODE 20", 40, GOLD, MONO)

def ring(d, cx, cy, r, col, w=None):
    w = w or max(3, int(r * 0.28))
    d.ellipse((cx - r, cy - r * 0.42, cx + r, cy + r * 0.42), outline=col, width=w)
    d.arc((cx - r, cy - r * 0.42 + 3, cx + r, cy + r * 0.42 + 3), 10, 170, fill=mix(col, (0, 0, 0), 0.4), width=max(2, w // 2))

def ring_grid(img, d, ks, kj):
    """50 segments de piston (10 x 5) ; au contrôle, 47 barrés en rouge, 3 brillent en vert"""
    good = {7, 23, 41}
    for i in range(50):
        r_, c_ = divmod(i, 10)
        cx = 120 + c_ * 93; cy = 560 + r_ * 92
        a = ks * 2.5 - i * 0.04
        if a <= 0: continue
        sc = min(1, a)
        col = (200, 206, 220)
        if kj > 0:
            jj = kj * 3 - (i % 10) * 0.05
            if jj > 0: col = GREEN2 if i in good else mix(col, (110, 60, 60), min(1, jj))
        ring(d, cx, cy, 34 * sc, col)
        if kj > 0 and i not in good and kj * 3 - (i % 10) * 0.05 > 0.3:
            d.line((cx - 26, cy - 22, cx + 26, cy + 22), fill=RED2, width=7); d.line((cx - 26, cy + 22, cx + 26, cy - 22), fill=RED2, width=7)
        if kj > 0.4 and i in good:
            _glow(img, (cx - 60, cy - 50, cx + 60, cy + 50), (120, 255, 160), 120, 14); d = ImageDraw.Draw(img); ring(d, cx, cy, 34, GREEN2)
    return ImageDraw.Draw(img)

def anvil(img, d, cx, cy, s, tg, k):
    d.polygon([(cx - 150 * s, cy - 60 * s), (cx + 110 * s, cy - 60 * s), (cx + 200 * s, cy - 100 * s), (cx + 120 * s, cy - 20 * s), (cx + 60 * s, cy - 20 * s), (cx + 60 * s, cy + 50 * s),
               (cx + 120 * s, cy + 90 * s), (cx - 140 * s, cy + 90 * s), (cx - 80 * s, cy + 50 * s), (cx - 80 * s, cy - 20 * s), (cx - 150 * s, cy - 30 * s)], fill=(50, 52, 60), outline=(120, 120, 130))
    ph = (tg * 2.2) % 1.0
    if ph < 0.15:
        burst(d, cx, cy - 70 * s, ph * 6, 18, 220 * s, (255, 190, 80), 7, 5)
    _glow(img, (cx - 120 * s, cy - 140 * s, cx + 120 * s, cy), (255, 120, 40), 90, 20)

def bicycle(d, cx, cy, s, tg, motor=True):
    R = 110 * s; col = (230, 234, 244); ang = tg * 9
    for wx in (cx - 170 * s, cx + 170 * s):
        d.ellipse((wx - R, cy - R, wx + R, cy + R), outline=col, width=int(9 * s))
        for j in range(6):
            a = ang + j * math.pi / 3; d.line((wx, cy, wx + R * math.cos(a), cy + R * math.sin(a)), fill=mix(col, (0, 0, 0), 0.3), width=max(1, int(3 * s)))
    p = (cx - 20 * s, cy - 10 * s); seat = (cx - 60 * s, cy - 170 * s); head = (cx + 120 * s, cy - 180 * s)
    for a, b in ((p, seat), (p, head), (seat, head), (p, (cx - 170 * s, cy)), (seat, (cx - 170 * s, cy)), (head, (cx + 170 * s, cy))):
        d.line((a, b), fill=ORANGE, width=int(12 * s))
    d.line((seat[0] - 40 * s, seat[1], seat[0] + 30 * s, seat[1]), fill=(40, 40, 46), width=int(16 * s))
    d.line((head[0] - 30 * s, head[1] - 20 * s, head[0] + 40 * s, head[1] - 30 * s), fill=col, width=int(10 * s))
    if motor:
        sh = 4 * s * math.sin(tg * 60)
        d.rounded_rectangle((cx - 70 * s, cy - 120 * s + sh, cx + 40 * s, cy - 40 * s + sh), int(14 * s), fill=(70, 74, 84), outline=GOLD, width=int(4 * s))
        for j in range(4): d.line((cx - 60 * s + j * 25 * s, cy - 120 * s + sh, cx - 60 * s + j * 25 * s, cy - 140 * s + sh), fill=(150, 150, 160), width=int(6 * s))
        for j in range(5):   # bouffées d'échappement
            u = (tg * 1.6 + j / 5) % 1.0
            rr = (14 + 40 * u) * s
            x = cx - 200 * s - 220 * s * u; y = cy - 30 * s - 50 * s * u
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=mix((200, 200, 210), (40, 44, 60), u))

def motorbike(d, cx, cy, s, col=(230, 60, 50), tilt=0.0):
    """moto de course stylisée (sans numéro ni marque) + pilote recroquevillé"""
    R = 70 * s
    for wx in (cx - 120 * s, cx + 120 * s):
        d.ellipse((wx - R, cy - R, wx + R, cy + R), fill=(20, 20, 24), outline=(150, 150, 160), width=int(6 * s))
    d.polygon([(cx - 140 * s, cy - 40 * s), (cx - 40 * s, cy - 120 * s), (cx + 120 * s, cy - 120 * s), (cx + 170 * s, cy - 50 * s), (cx + 40 * s, cy - 10 * s)], fill=col)
    d.ellipse((cx - 40 * s, cy - 230 * s, cx + 40 * s, cy - 150 * s), fill=(240, 240, 240))
    d.polygon([(cx - 80 * s, cy - 120 * s), (cx - 30 * s, cy - 180 * s), (cx + 60 * s, cy - 160 * s), (cx + 20 * s, cy - 110 * s)], fill=(30, 30, 40))

def chequered(d, cx, cy, s, tg):
    d.line((cx, cy, cx, cy - 360 * s), fill=(220, 220, 220), width=int(10 * s))
    for i in range(6):
        for j in range(4):
            wv = 14 * s * math.sin(tg * 6 + i * 0.7)
            x = cx + i * 40 * s; y = cy - 360 * s + j * 40 * s + wv
            d.rectangle((x, y, x + 40 * s, y + 40 * s), fill=(250, 250, 250) if (i + j) % 2 == 0 else (20, 20, 20))

def cracks(d, k, seed=8):
    if k <= 0: return
    r = np.random.default_rng(seed)
    for i in range(7):
        x, y = W / 2 + r.uniform(-300, 300), HOR + r.uniform(60, 400)
        for j in range(int(min(1, k * 2) * 8)):
            nx, ny = x + r.uniform(-90, 90), y + r.uniform(20, 90)
            d.line((x, y, nx, ny), fill=(20, 16, 14), width=6); x, y = nx, ny

def debris(d, k, seed=9):
    if k <= 0: return
    r = np.random.default_rng(seed)
    for i in range(30):
        x0 = r.uniform(0, W); t = k - r.uniform(0, 0.8)
        if t <= 0: continue
        y = -60 + 1600 * t * t; s = r.uniform(14, 40)
        d.polygon([(x0 - s, y), (x0, y - s * 0.8), (x0 + s, y - s * 0.2), (x0 + s * 0.4, y + s * 0.6)], fill=(130, 70, 56))

# ---------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    img.paste(RUIN_D); d = ImageDraw.Draw(img); _dust(d, tg, 0.8)
    ke = kM(tg, "effondrer")
    shadow(d, W / 2, FEET, 250); P(img, W / 2, FEET - (90 / ZF if ke > 0.6 else 0), 250, "kneel" if ke > 0.6 else "sad"); d = ImageDraw.Draw(img)
    if 0 < ke < 1.6: debris(d, ke)
    topsh(img); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    hit = 0.0
    sc = 1 + 0.3 * (1 - eout((tg + 0.12) / 0.2))
    text(d, (W / 2, 400), "TU AS TOUT", fit("TU AS TOUT", int(140 * sc), 900), WHITE, BOLD, stroke=8, scol=BG)
    kp = kM(tg, "perdu")
    text(d, (W / 2, 560), "PERDU ?", pop(max(kp, 0.01), fit("PERDU ?", 150, 900), 0.25, 0.2), ORANGE, BOLD, stroke=10, scol=BG)
    kt = kM(tg, "terre")
    if kt > 0 and kM(tg, "a38") <= 0: hit = stamp(img, "PAR TERRE", (W / 2, 760), 130, -6, kt, RED2)
    ka = kM(tg, "a38")
    if ka > 0: badge(d, W / 2, 760, "38 ANS", ka, GOLD, 120)
    if ke > 0: hit = max(hit, stamp(img, "SON USINE S'EFFONDRE", (W / 2, 960), 80, -4, ke, RED2))
    return dict(hit=hit, shake=hit * 0.9 + (0.6 if 0 < ke < 1.2 else 0))

def s_intro(img, d, tg, k):
    img.paste(VIL); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 240); P(img, W / 2, FEET, 240, "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 300, "L'HISTOIRE VRAIE", 100, WHITE, k)
    TX(d, 430, "D'UN MÉCANICIEN", 110, ORANGE, k - 0.5)
    TX(d, 560, "QUI N'A JAMAIS LÂCHÉ", 76, AMBER, k - 0.9)
    return dict(hit=0.0)

def s_jeune(img, d, tg, k):
    kq = kM(tg, "quelques")
    if kq <= 0:
        img.paste(VIL); d = ImageDraw.Draw(img)
        q = proj(-150, 1.6); anvil(img, d, q[0] + 40, q[1] + 60, 0.9, tg, k); d = ImageDraw.Draw(img)
        k15 = kM(tg, "a15")
        shadow(d, W / 2 + 200, FEET, 220)
        P(img, W / 2 + 200, FEET, 220, run_pose(tg * 6) if k15 > 0.3 else "stand", facing=1); d = ImageDraw.Draw(img)
        topsh(img, 0.85); d = ImageDraw.Draw(img)
        TX(d, 270, "FILS D'UN FORGERON", 92, WHITE, kM(tg, "forgeron"))
        if k15 <= 0: TX(d, 390, "UN VILLAGE DU JAPON", 76, ICE, kM(tg, "japon"))
        if k15 > 0:
            badge(d, 200, 420, "15 ANS", k15, GOLD, 110)
            TX(d, 400, "SEUL À TOKYO", 100, ORANGE, kM(tg, "tokyo"), x=W / 2 + 120, maxw=720)
            TX(d, 520, "APPRENTI", 110, WHITE, kM(tg, "apprenti"), x=W / 2 + 120, maxw=720)
        return dict(hit=0.0)
    img.paste(GAR_N); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 245); P(img, W / 2, FEET, 245, "up" if kM(tg, "atelier1") > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 270, "QUELQUES ANNÉES PLUS TARD…", 72, WHITE, kq)
    hit = stamp(img, "SON PROPRE ATELIER", (W / 2, 450), 96, -4, kM(tg, "atelier1"), GOLD)
    return dict(hit=hit)

def s_pistons(img, d, tg, k):
    img.paste(GAR_N); d = ImageDraw.Draw(img)
    shadow(d, W / 2 + 330, FEET, 230); P(img, W / 2 + 330, FEET, 230, "sad" if kM(tg, "trois") > 0.5 else "point", facing=-1); d = ImageDraw.Draw(img)
    dim(img, 0.25); topsh(img, 0.85); d = ImageDraw.Draw(img)
    hit = 0.0
    kc = kM(tg, "cinquante"); kt = kM(tg, "trois")
    if kc <= 0:
        TX(d, 270, "DES PIÈCES DE MOTEUR", 84, WHITE, kM(tg, "pieces"))
        ks = kM(tg, "segments")
        if ks > 0:
            for i in range(3): ring(d, W / 2 + (i - 1) * 230, 620, 90 * eout(min(1, (ks - i * 0.15) / 0.3)) if ks - i * 0.15 > 0 else 1, (210, 216, 230))
            TX(d, 400, "SEGMENTS DE PISTON", 80, ORANGE, ks)
        TX(d, 820, "POUR UN GRAND CONSTRUCTEUR", 64, ICE, kM(tg, "constructeur"))
        return dict(hit=0.0)
    TX(d, 270, "IL EN PRÉSENTE 50", 96, WHITE, kc)
    d = ring_grid(img, d, kc, kt)
    if kt > 0.6:
        hit = stamp(img, "3 SEULEMENT", (W / 2, 1120), 130, -6, kt - 0.6, RED2)
        TX(d, 400, "47 REFUSÉES", 96, RED2, kt - 0.3)
    return dict(hit=hit, shake=hit * 0.5)

def s_ecole(img, d, tg, k):
    img.paste(EXAM); dim(img, 0.35, (10, 14, 40)); d = ImageDraw.Draw(img)
    kl = kM(tg, "livrees")
    shadow(d, W / 2, FEET, 245, (60, 40, 30)); P(img, W / 2, FEET, 245, "up" if kl > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    hit = 0.0
    TX(d, 270, "RETOUR À L'ÉCOLE", 100, WHITE, kM(tg, "ecole"))
    kd = kM(tg, "deux")
    if kd > 0 and kl <= 0: counter(d, 430, 0, 2, kd, 0.6, 150, GOLD, "{} ANS")
    km = kM(tg, "metal")
    if km > 0 and kl <= 0:
        TX(d, 590, "COMPRENDRE LE MÉTAL", 80, ICE, km)
        ring(d, W / 2, 760, 120 * eout(min(1, km / 0.4)), GOLD, 20)
    if kl > 0:
        hit = stamp(img, "LIVRÉES !", (W / 2, 520), 160, -6, kl, GREEN2)
    return dict(hit=hit, flash=0.3 * max(0, 1 - kl / 0.25) if 0 < kl < 0.25 else 0)

def s_seisme(img, d, tg, k):
    kt = kM(tg, "tremblement"); ke = kM(tg, "effondre"); kv = kM(tg, "vend"); ka = kM(tg, "aurait"); km = kM(tg, "moi")
    hit = 0.0; shake = 0.0
    if ke <= 0:
        img.paste(GAR_N); d = ImageDraw.Draw(img)
        if kt > 0: cracks(d, kt); shake = 1.0 + 0.6 * math.sin(tg * 40)
        shadow(d, W / 2, FEET, 245); P(img, W / 2, FEET, 245, "wide" if kt > 0 else "stand"); d = ImageDraw.Draw(img)
        if kt > 0: debris(d, kt * 0.8)
        topsh(img, 0.85); d = ImageDraw.Draw(img)
        TX(d, 270, "JANVIER 1945", 120, WHITE, kM(tg, "janvier"))
        if kt > 0: hit = stamp(img, "TREMBLEMENT DE TERRE", (W / 2, 470), 84, -5, kt, RED2)
        return dict(hit=hit, shake=shake)
    img.paste(RUIN_D); d = ImageDraw.Draw(img); _dust(d, tg, 1.0)
    if ka <= 0: debris(d, ke * 0.7)
    shadow(d, W / 2, FEET, 250)
    P(img, W / 2, FEET - (90 / ZF if ka > 0 else 0), 250, "kneel" if ka > 0 else "sad"); d = ImageDraw.Draw(img)
    if ka > 0: dim(img, 0.25)
    topsh(img); d = ImageDraw.Draw(img)
    if ka <= 0:
        hit = stamp(img, "EFFONDRÉE", (W / 2, 330), 150, -6, ke, RED2)
        if kv > 0: TX(d, 560, "IL VEND CE QUI RESTE", 84, WHITE, kv)
        return dict(hit=hit, shake=max(0, 1.2 - ke) if ke < 1.2 else 0)
    TX(d, 280, "IL AURAIT PU SE DIRE…", 80, WHITE, ka)
    if km > 0: hit = stamp(img, "« C'EST FINI »", (W / 2, 520), 130, -6, km, RED2)
    return dict(hit=hit)

def s_cri(img, d, tg, k):
    kb_ = tg - K["boom"]; kk = max(0.0, kb_ + 0.06); kr = kM(tg, "reconstruire")
    c = (W / 2, 820)
    r = eout(max(0, kr) / 1.0) * 2300 if kr > 0 else 0
    img.paste(reveal(RUIND_ARR, RUING_ARR, c, r)); d = ImageDraw.Draw(img)
    if kr < 0.6: _dust(d, tg, max(0, 1 - max(0, kr) / 0.6))
    rays(img, min(1, max(0, kr) / 0.5)); d = ImageDraw.Draw(img)
    rings(img, c, kr, 6, GOLD, 1050, 16, 0.14, 1.25); d = ImageDraw.Draw(img)
    burst(d, c[0], c[1], kr, 26, 520, (255, 240, 190), 3, 10)
    shadow(d, W / 2, FEET, 270)
    P(img, W / 2, FEET, 270, POSES["sad"] if kb_ < 0 else (POSES["up"] if kr > 0 else POSES["shout"])); d = ImageDraw.Draw(img)
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    hit = max(0, 1 - kk / 0.3) if kk > 0 else 0
    e = eout(kk / 0.22) if kk > 0 else 0
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, eout(max(0, kr) / 0.22))
    f1 = fit("IL VA TOUT", 140, 960); f2 = pop(kr, fit("RECONSTRUIRE !", 130, 980), 0.08)
    for off, cc in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        if kb_ > 0: text(d, (x1 + o, 400), "IL VA TOUT", f1, cc, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
        if kr > 0: text(d, (x2 - o, 560), "RECONSTRUIRE !", f2, cc if cc != WHITE else GOLD, BOLD, stroke=9 if cc == WHITE else 0, scol=BG)
    hr = max(0, 1 - kr / 0.3) if kr > 0 else 0
    return dict(hit=max(hit, hr) * 1.6, shake=max(hit, hr) * 1.9, flash=max(0, 0.9 - kr * 2.6) if kr > 0 else 0)

def s_velo(img, d, tg, k):
    img.paste(RUIN_G); d = ImageDraw.Draw(img)
    kv = kM(tg, "velos")
    shadow(d, W / 2 + 250, FEET, 235, (110, 80, 60)); P(img, W / 2 + 250, FEET, 235, "up" if kv > 0.5 else "point", facing=-1); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 260, "SUR LES RUINES", 110, WHITE, kM(tg, "ruines"))
    TX(d, 380, "UN PETIT ATELIER", 90, GOLD, kM(tg, "atelier2"))
    km = kM(tg, "moteurs")
    if km > 0:
        bicycle(d, W / 2 - 120 + 60 * math.sin(tg * 1.5), 900, 1.15, tg, motor=True)
        TX(d, 520, "+ UN PETIT MOTEUR", 80, ORANGE, km)
    return dict(hit=0.0)

def s_entreprise(img, d, tg, k):
    img.paste(GAR_G); d = ImageDraw.Draw(img)
    ke = kM(tg, "entreprise")
    for i in range(3):   # rangée de motos neuves (génériques)
        if ke - i * 0.2 > 0: motorbike(d, 230 + i * 310, 1150 - i * 20, 0.75, ((230, 60, 50), (240, 240, 240), (230, 60, 50))[i])
    shadow(d, W / 2, FEET + 120, 220); P(img, W / 2, FEET + 120, 220, "up" if ke > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    hit = 0.0
    TX(d, 260, "1948", 150, WHITE, kM(tg, "a1948"))
    badge(d, W / 2 + 330, 290, "42 ANS", kM(tg, "a42"), GOLD, 100)
    if ke > 0: hit = stamp(img, "SA PROPRE ENTREPRISE", (W / 2, 460), 84, -4, ke, GOLD)
    return dict(hit=hit)

def s_course(img, d, tg, k):
    k61 = kM(tg, "a1961")
    img.paste(COAST if k61 <= 0 else COAST_G); d = ImageDraw.Draw(img)
    hit = 0.0
    kt = kM(tg, "treize")
    # motos qui passent sur la route côtière
    for i in range(4 if k61 <= 0 else 3):
        z = 1.3 + ((tg * 0.9 + i * 0.9) % 4.0)
        q = proj(W / 2 + (-120 if i % 2 else 120), z)
        motorbike(d, q[0], q[1] - 70 / z, 1.2 / z, ((90, 90, 100), (60, 120, 200), (230, 200, 60), (90, 160, 90))[i])
    if k61 > 0:   # notre moto devant, rouge
        motorbike(d, W / 2, FEET - 40, 1.3 + 0.05 * math.sin(tg * 9), (230, 60, 50))
        chequered(d, 120, 1250, 1.2, tg)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    if k61 <= 0:
        TX(d, 260, "IL ANNONCE :", 90, WHITE, kM(tg, "annonce"))
        TX(d, 380, "ON VA GAGNER", 120, ORANGE, kM(tg, "annonce") + 0.4)
        TX(d, 500, "L'UNE DES PLUS CÉLÈBRES COURSES", 60, ICE, kM(tg, "celebres"))
        if kt > 0 and kM(tg, "continue") <= 0: hit = stamp(img, "13e", (W / 2, 720), 200, -6, kt, RED2)
        if kM(tg, "continue") > 0: TX(d, 720, "IL CONTINUE", 130, GOLD, kM(tg, "continue"))
        return dict(hit=hit)
    TX(d, 260, "1961", 150, WHITE, k61)
    kg = kM(tg, "gagnent")
    if kg > 0:
        hit = stamp(img, "VICTOIRE !", (W / 2, 470), 170, -6, kg, GOLD); confetti(d, kg * 0.6, 0.8)
    return dict(hit=hit, flash=0.4 * max(0, 1 - kg / 0.25) if 0 < kg < 0.25 else 0)

def s_succes(img, d, tg, k):
    img.paste(RUIN_G); d = ImageDraw.Draw(img); rays(img, 0.5); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 250, (110, 80, 60)); P(img, W / 2, FEET, 250, "up"); d = ImageDraw.Draw(img)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    TX(d, 270, "SON NOM", 120, WHITE, kM(tg, "nom"))
    globe(d, W / 2, 720, 210, kM(tg, "nom"), ICE)
    km = kM(tg, "monde"); hit = 0.0
    if km > 0: hit = stamp(img, "DANS LE MONDE ENTIER", (W / 2, 450), 84, -4, km, GOLD)
    return dict(hit=hit)

def s_regard(img, d, tg, k):
    kr = kM(tg, "reconstruit"); hit = 0.0
    img.paste(RUIN_D if kr <= 0 else RUIN_G); d = ImageDraw.Draw(img)
    if kr > 0: rays(img, 0.4 + 0.5 * min(1, kr / 0.5)); d = ImageDraw.Draw(img)
    shadow(d, W / 2, FEET, 255, (120, 90, 70)); P(img, W / 2, FEET, 255, "up" if kr > 0 else "stand"); d = ImageDraw.Draw(img)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 250, "IL AVAIT TOUT PERDU…", 92, WHITE, kM(tg, "homme"))
    if kr > 0: hit = stamp(img, "IL A TOUT RECONSTRUIT", (W / 2, 460), 90, -4, kr, GOLD)
    return dict(hit=hit, flash=0.4 * max(0, 1 - kr / 0.25) if kr > 0 else 0)

def s_you(img, d, tg, k):
    kc = kM(tg, "chute"); kv = kM(tg, "vie"); hit = 0.0
    img.paste(RUIN_D); d = ImageDraw.Draw(img); _dust(d, tg, 0.6)
    shadow(d, W / 2, FEET, 262)
    P(img, W / 2, FEET, 262, blend_pose(POSES["stand"], POSES["point"], eout(max(0, k) / 0.4)))
    dim(img, 0.25); topsh(img); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(150 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=8, scol=BG)
    TX(d, 470, "UNE CHUTE", 120, WHITE, kc)
    if kv > 0: hit = stamp(img, "VA DÉCIDER DE TA VIE ?", (W / 2, 630), 90, -4, kv, GOLD)
    return dict(hit=hit)

def s_abonne(img, d, tg, k):
    img.paste(STAD_AMAT); d = ImageDraw.Draw(img)
    dim(img, 0.6); d = ImageDraw.Draw(img)
    hit = 0.0
    P(img, 200, FEET + 20, 215, "point", fixed=True); d = ImageDraw.Draw(img)
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rounded_rectangle((W / 2 - bw / 2, 420 - bh / 2, W / 2 + bw / 2, 420 + bh / 2), int(40 * sc), fill=RED)
    text(d, (W / 2 - bw / 2 + 90 * sc, 420), "+", int(130 * sc), WHITE, BOLD)
    text(d, (W / 2 + 50 * sc, 420), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE, BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = kM(tg, "demain")
    if kd > 0:
        TX(d, 660, "DEMAIN · ÉPISODE 21", 74, GOLD, kd)
        kc = kM(tg, "confiseur")
        if kc > 0:
            text(d, (W / 2, 770), typew("LE CONFISEUR QUI A", kc, 30), fit("LE CONFISEUR QUI A", 68, 960), WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 860), typew("FAIT FAILLITE…", kc - 0.6, 30), fit("FAIT FAILLITE…", 68, 960), WHITE, BOLD, stroke=6, scol=BG)
    return dict(hit=hit)

SCENES = {"hook": s_hook, "intro": s_intro, "jeune": s_jeune, "pistons": s_pistons, "ecole": s_ecole, "seisme": s_seisme, "cri": s_cri,
          "velo": s_velo, "entreprise": s_entreprise, "course": s_course, "succes": s_succes, "regard": s_regard, "you": s_you,
          "abonne": s_abonne, "question": s_question, "logo": s_logo}

def PATH(typ, k, tg):
    st = SC[typ]
    if typ == "hook":    return _seg(k, [(0, 1.0, 0, 0), (6.5, 1.2, 0, 0)]) + (False,)
    if typ == "intro":   return _seg(k, [(0, 2.6, -200, 0), (1.9, 1.05, 0, 0)]) + (k < 1.9,)
    if typ == "jeune":
        q = MK_("quelques") - st
        if k < q: return _seg(k, [(0, 1.6, 200, 0), (q, 3.2, -260, 0)]) + (False,)
        return _seg(k, [(q, 2.6, 0, 0), (q + 1.5, 1.05, 0, 0)]) + (False,)
    if typ == "pistons": return _seg(k, [(0, 1.3, 0, 0), (3.0, 1.1, 0, 0)]) + (False,)
    if typ == "ecole":   return _seg(k, [(0, 2.4, -200, 0), (2.5, 1.05, 0, 0)]) + (False,)
    if typ == "seisme":  return _seg(k, [(0, 1.3, 0, 0), (6.0, 1.0, 0, 0)]) + (False,)
    if typ == "cri":
        r = MK_("reconstruire") - st
        return _seg(k, [(0, 1.6, 0, 0), (max(0.2, r), 1.6, 0, 0), (max(0.2, r) + 1.0, 0.95, 0, 0)]) + (False,)
    if typ == "velo":    return _seg(k, [(0, 2.4, 300, 0), (2.0, 1.1, 0, 0)]) + (False,)
    if typ == "entreprise": return _seg(k, [(0, 2.0, 0, 0), (2.4, 1.2, 0, 0)]) + (False,)
    if typ == "succes":  return _seg(k, [(0, 1.3, 0, 0), (2.0, 1.0, 0, 0)]) + (False,)
    if typ == "regard":  return _seg(k, [(0, 1.0, 0, 0), (2.2, 2.0, 0, 0)]) + (k < 2.2,)
    if typ == "you":     return _seg(k, [(0, 1.35, -150, 0), (2.0, 0.9, 60, 0)]) + (False,)
    return (1.0, 0.0, 0.0, 0.0, False)

def CAMF(typ, k, tg):
    hh = (6 * math.sin(tg * 2.1), 5 * math.sin(tg * 1.7 + 1))
    dur = 3.0
    for s_ in SCN:
        if s_["type"] == typ: dur = s_["end"] - s_["start"]
    u = ease(k / max(0.5, dur))
    if typ == "hook":    return (lerp(1.25, 1.08, u), lerp(40, -30, u) + hh[0], lerp(50, 0, u) + hh[1], lerp(0.06, -0.03, u), -0.03, lerp(-1.5, 0, u))
    if typ == "intro":   return (lerp(1.08, 1.18, u), lerp(-60, 60, u), hh[1], lerp(0.08, -0.05, u), 0.05, 0.0)
    if typ == "jeune":   return (lerp(1.18, 1.06, u), lerp(70, -50, u) + hh[0], hh[1], lerp(-0.07, 0.07, u), -0.05, 0.0)
    if typ == "pistons": return (lerp(1.04, 1.1, u), hh[0], hh[1], lerp(0.04, -0.04, u), 0.03, 0.0)
    if typ == "ecole":   return (lerp(1.06, 1.18, u), hh[0], lerp(30, -30, u), lerp(0.06, -0.06, u), 0.05, 0.0)
    if typ == "seisme":  return (lerp(1.06, 1.2, u), hh[0] * 2, lerp(0, -40, u), lerp(-0.05, 0.05, u), 0.06, 1.5 * math.sin(tg * 2.5))
    if typ == "cri":
        kb = max(0.0, tg - M("reconstruire", 99))
        orb = math.sin(min(1, kb / 1.5) * math.pi) * 0.13
        return (1.08 + 0.2 * math.exp(-kb * 3) if kb > 0 else 1.1, hh[0] * 2, hh[1], orb, 0.06 if kb > 0 else 0.0, 3 * math.sin(kb * 4) * math.exp(-kb * 2))
    if typ == "velo":    return (lerp(1.2, 1.06, u), hh[0] * 1.5, lerp(-30, 30, u), lerp(-0.07, 0.05, u), -0.04, 0.0)
    if typ == "entreprise": return (lerp(1.08, 1.2, u), lerp(-80, 60, u) + hh[0], hh[1], lerp(-0.07, 0.07, u), 0.03, 0.0)
    if typ == "course":  return (1.1 + 0.02 * math.sin(tg * 7), hh[0] * 2, hh[1] * 2 + 6 * math.sin(tg * 7), lerp(0.07, -0.07, u), 0.04, 1.0 * math.sin(tg * 3.5))
    if typ == "succes":  return (lerp(1.06, 1.18, u), hh[0] * 2, hh[1], lerp(0.09, -0.09, u), 0.05, 1.0 * math.sin(tg * 3))
    if typ == "regard":  return (lerp(1.18, 1.06, u), hh[0], lerp(-40, 30, u), lerp(0.08, -0.06, u), 0.05, 0.0)
    if typ == "you":     return (lerp(1.06, 1.16, u), lerp(-60, 30, u) + hh[0], hh[1], lerp(0.06, -0.04, u), 0.0, 0.0)
    return None


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None, int(a[5]) if len(a) > 5 else 1)

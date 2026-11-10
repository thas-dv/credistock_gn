# -*- coding: utf-8 -*-
"""Style « neige » (render_fable.py) : petite ville de montagne EN PLEIN JOUR SOUS LA NEIGE (toits enneigés, sapins, fumée des cheminées),
personnage « athlète » en tenue d'hiver (bonnet à pompon, survêtement) qui laisse des traces de pas, souffle de la buée, DÉBLAIE LE TERRAIN
À LA PELLE ; au cri, son souffle CHASSE LA NEIGE (onde circulaire qui révèle la pelouse verte et le soleil, le bonnet s'envole) ; puis
pneu tiré à la corde, portail du centre de formation, stades génériques (jour doré, crépuscule), mur défensif, brassard « C », tir au but.
Aucun nom propre, club, logo, écusson, drapeau, monument ni trophée réel à l'écran. Types : hook intro ville metz renvoi retour voix pro
naples afrique regard you abonne question logo (10/11/2026 : Kalidou Koulibaly, épisode 7 — 2e version d'animation).
Usage : python3 render_fable.py timing_voix.json video_brut_fable.mp4 [t_from t_to every]"""

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









# =============================================================== style « neige » (10/11/2026, Kalidou Koulibaly — épisode 7, 2e animation)
BG = (8, 14, 26)
ORANGE = (255, 150, 30); ACC = ORANGE; ICE = (176, 212, 255); AMBER = (255, 200, 110)
HOR = 880; FEET = 1440
JER = (226, 48, 118); NAVY = (26, 34, 62); BEANIE = (250, 204, 60); GLOVE = None
SNOW_SH = (168, 184, 212)

POSES["shy"] = dict(t=-14, la=(-6, 18), ra=(6, -18), ll=(-4, 0), rl=(4, 0))
POSES["sad"] = dict(t=-26, la=(-14, 30), ra=(14, -30), ll=(-6, 4), rl=(6, -4))
POSES["wide"] = dict(t=0, la=(-100, -10), ra=(100, 10), ll=(-20, 6), rl=(20, -6))
POSES["point"] = dict(t=4, la=(-150, -10), ra=(30, -40), ll=(-12, 4), rl=(12, -4))
POSES["fist"] = dict(t=-4, la=(-172, -6), ra=(25, -70), ll=(-14, 4), rl=(14, -4))
POSES["talk"] = dict(t=3, la=(-30, -70), ra=(20, -30), ll=(-6, 0), rl=(6, 0))
POSES["shout"] = dict(t=9, la=(-118, -22), ra=(118, 22), ll=(-24, 6), rl=(24, -6))
POSES["scoop"] = dict(t=-50, la=(52, -8), ra=(30, 36), ll=(-26, 30), rl=(34, -30))
POSES["throw"] = dict(t=-4, la=(112, 20), ra=(84, 50), ll=(-18, 8), rl=(20, -8))
POSES["lean"] = dict(t=-6, la=(26, 30), ra=(40, 40), ll=(-6, 0), rl=(8, 0))

def P(img, x, y, s, pose, winter=False, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER); kw.setdefault("shorts", NAVY)
    kw.setdefault("sock", NAVY if winter else (240, 240, 244))
    if winter:
        kw.setdefault("legs", NAVY); kw.setdefault("sleeves", kw["jersey"]); kw.setdefault("beanie", BEANIE)
    player(img, x, y, s * 1.25, pose, **kw)

def shadow(d, x, y, s, col=SNOW_SH):
    s = s * 1.25; d.ellipse((x - 0.36 * s, y - 0.05 * s, x + 0.36 * s, y + 0.06 * s), fill=col)

GSH = (40, 112, 54)      # ombre sur pelouse

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

def _ridge(x, base, amp, ph, f):
    return base - amp * (0.5 + 0.5 * math.sin(x / f + ph)) - amp * 0.22 * math.sin(x / (f * 0.31) + ph * 3)

def fir(d, x, yb, h, col, snow=None):
    d.rectangle((x - h * 0.035, yb - h * 0.14, x + h * 0.035, yb), fill=(54, 40, 34))
    for i in range(3):
        top = yb - h + i * 0.25 * h; bot = top + 0.42 * h; hw = h * (0.17 + 0.085 * i)
        d.polygon([(x, top), (x - hw, bot), (x + hw, bot)], fill=col)
        if snow:
            m = top + (bot - top) * 0.55
            d.polygon([(x, top - 2), (x - hw * 0.6, m + 6), (x - hw * 0.28, m - 8), (x + hw * 0.05, m + 8), (x + hw * 0.34, m - 6), (x + hw * 0.62, m + 4)], fill=snow)

PAL = {
    "snow":  dict(sky0=(84, 104, 142), sky1=(172, 190, 214), m1=(156, 172, 202), m2=(122, 142, 178), cap=(238, 242, 250), fir=(28, 60, 64),
                  g0=(232, 238, 249), g1=(184, 198, 224), roof=(240, 244, 251), win=AMBER, wallk=0.82, tint=(150, 170, 205)),
    "green": dict(sky0=(34, 108, 206), sky1=(178, 222, 250), m1=(128, 158, 200), m2=(74, 124, 110), cap=(244, 248, 252), fir=(20, 92, 58),
                  g0=(84, 176, 84), g1=(40, 118, 58), roof=(176, 74, 54), win=(74, 104, 140), wallk=1.0, tint=(255, 255, 255)),
    "gold":  dict(sky0=(66, 74, 150), sky1=(255, 188, 120), m1=(160, 116, 136), m2=(104, 82, 100), cap=(255, 214, 190), fir=(30, 62, 50),
                  g0=(120, 164, 64), g1=(50, 96, 44), roof=(150, 62, 46), win=AMBER, wallk=0.9, tint=(255, 200, 150)),
}
HOUSES = [(-20, 170, 150, (232, 214, 186)), (160, 130, 200, (206, 150, 120)), (300, 180, 140, (190, 204, 220)),
          (500, 120, 170, (226, 196, 150)), (640, 150, 130, (214, 170, 150))]
CHIM = []

def make_town(mode):
    p = PAL[mode]; snow = mode == "snow"
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    _grad(d, 0, HOR + 1, p["sky0"], p["sky1"], 1.3)
    rng = np.random.default_rng(21)
    # soleil / nuages
    if mode == "green":
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((700, 40, 1020, 360), fill=(255, 250, 210, 120)); img.alpha_composite(L.filter(ImageFilter.GaussianBlur(40))); d = ImageDraw.Draw(img)
        d.ellipse((790, 130, 930, 270), fill=(255, 248, 200))
    if mode == "gold":
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((640, 380, 1040, 780), fill=(255, 210, 140, 150)); img.alpha_composite(L.filter(ImageFilter.GaussianBlur(50))); d = ImageDraw.Draw(img)
        d.ellipse((760, 500, 920, 660), fill=(255, 226, 160))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for i in range(9 if snow else 4):
        x, y, w = rng.uniform(0, W), rng.uniform(60, 420), rng.uniform(160, 360)
        dl.ellipse((x - w, y - 50, x + w, y + 50), fill=((226, 232, 244, 120) if snow else (255, 255, 255, 150)))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(26))); d = ImageDraw.Draw(img)
    # montagnes
    for li, (base, amp, col, f) in enumerate([(600, 260, p["m1"], 210), (720, 170, p["m2"], 150)]):
        pts = [(0, H)] + [(x, _ridge(x, base, amp, li * 2.1 + 0.6, f)) for x in range(0, W + 31, 30)] + [(W, H)]
        d.polygon(pts, fill=col)
        if li == 0 or snow:
            for x in range(0, W, 30):
                y = _ridge(x, base, amp, li * 2.1 + 0.6, f); y2 = _ridge(x + 30, base, amp, li * 2.1 + 0.6, f)
                dep = (36 + 20 * math.sin(x / 23.0)) * (1.0 if li == 0 else 0.7) * (2.4 if snow else 1.0)
                d.polygon([(x, y), (x + 30, y2), (x + 30, y2 + dep * 0.8), (x + 15, y + dep), (x, y + dep * 0.7)], fill=p["cap"])
    # forêt de sapins (2 rangs)
    for row, (yb, h0) in enumerate([(800, 110), (860, 150)]):
        for i in range(17 - row * 3):
            x = -30 + i * (W + 60) / (16 - row * 3) + rng.uniform(-18, 18); h = h0 + rng.uniform(-20, 30)
            fir(d, x, yb + rng.uniform(-8, 8), h, mix(p["fir"], (0, 0, 0), 0.18 * (1 - row)), p["cap"] if snow else None)
    # maisons
    del CHIM[:]
    for i, (x, w, h, wall) in enumerate(HOUSES):
        by = HOR + 24; wall = mix(mix(wall, (0, 0, 0), 1 - p["wallk"]), p["tint"], 0.18)
        d.rectangle((x, by - h, x + w, by), fill=wall)
        d.rectangle((x + w * 0.66, by - h - 64, x + w * 0.66 + 22, by - h - 4), fill=mix(wall, (0, 0, 0), 0.35)); CHIM.append((x + w * 0.66 + 11, by - h - 66))
        d.polygon([(x - 14, by - h + 2), (x + w / 2, by - h - 78), (x + w + 14, by - h + 2)], fill=p["roof"])
        if snow:
            d.line((x - 14, by - h + 2, x + w + 14, by - h + 2), fill=(200, 210, 230), width=5)
            d.rectangle((x + w * 0.66 - 3, by - h - 72, x + w * 0.66 + 25, by - h - 60), fill=p["roof"])
        for fx in range(int(x + 20), int(x + w - 34), 50):
            for fy in range(int(by - h + 26), int(by - 50), 62):
                on = (fx * 7 + fy * 3 + i) % 4 != 0
                d.rectangle((fx - 3, fy - 3, fx + 29, fy + 39), fill=mix(wall, (255, 255, 255), 0.4))
                d.rectangle((fx, fy, fx + 26, fy + 36), fill=p["win"] if on or mode == "green" else (52, 60, 80))
                d.line((fx + 13, fy, fx + 13, fy + 36), fill=mix(wall, (255, 255, 255), 0.4), width=2)
                if snow: d.rectangle((fx - 5, fy + 36, fx + 31, fy + 42), fill=(244, 247, 252))
    # sol
    if snow:
        _grad(d, HOR, H, p["g0"], p["g1"], 0.9)
        for i in range(26):
            x, y, w = rng.uniform(0, W), rng.uniform(HOR + 80, H), rng.uniform(90, 260)
            d.ellipse((x - w, y - 10, x + w, y + 12), fill=mix(p["g0"], p["g1"], min(1, (y - HOR) / (H - HOR)) * 0.8 + rng.uniform(-0.08, 0.12)))
    else:
        y = HOR; bh = 40.0; j = 0
        while y < H:
            u = (y - HOR) / (H - HOR); c = mix(p["g0"], p["g1"], u)
            d.rectangle((0, y, W, y + bh + 1), fill=mix(c, (0, 0, 0), 0.07 * (j % 2))); y += bh; bh *= 1.22; j += 1
        d.line((0, HOR + 150, W, HOR + 138), fill=(240, 246, 240), width=6)
        d.arc((W / 2 - 330, HOR + 110, W / 2 + 330, HOR + 330), 0, 180, fill=(240, 246, 240), width=5)
    # main courante blanche + petit but du club
    for x in range(-10, W, 120):
        d.rectangle((x, HOR - 14, x + 9, HOR + 46), fill=(226, 230, 238) if not snow else (198, 206, 222))
    d.rectangle((0, HOR - 16, W, HOR - 6), fill=(236, 240, 246) if not snow else (206, 214, 228))
    if snow: d.rectangle((0, HOR - 22, W, HOR - 15), fill=(250, 252, 255))
    gx0, gx1, gy0, gy1 = 820, 1050, HOR - 96, HOR + 70
    for i in range(9): d.line((gx0 + i * (gx1 - gx0) / 8, gy0, gx0 + i * (gx1 - gx0) / 8 + 14, gy1 - 6), fill=(150, 160, 176), width=2)
    for j in range(6): d.line((gx0, gy0 + j * (gy1 - gy0) / 6, gx1 + 14, gy0 + j * (gy1 - gy0) / 6), fill=(150, 160, 176), width=2)
    d.line((gx0, gy1, gx0, gy0, gx1, gy0, gx1, gy1), fill=(250, 250, 252), width=9)
    if snow: d.line((gx0 - 4, gy0 - 7, gx1 + 4, gy0 - 7), fill=(255, 255, 255), width=8)
    return img

def make_stadium(mode):
    """stade générique : tribune à points de couleur, toit, pylônes ; aucun logo, aucune inscription"""
    pal = {"belg": ((70, 88, 120), (176, 190, 208), (64, 132, 74), (36, 92, 52), 0.75),
           "ital": ((52, 104, 196), (255, 206, 150), (92, 170, 78), (44, 110, 54), 1.0),
           "afr":  ((44, 30, 84), (255, 150, 70), (70, 140, 66), (30, 80, 44), 0.8)}[mode]
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
    # tribune
    top = lambda x: 470 + 46 * ((x - W / 2) / (W / 2)) ** 2
    d.polygon([(0, 930)] + [(x, top(x)) for x in range(0, W + 1, 30)] + [(W, 930)], fill=(34, 36, 52))
    cols = [(236, 232, 224), (214, 170, 120), (200, 80, 70), (90, 130, 200), (240, 200, 90), (120, 120, 136), (70, 160, 150), (180, 110, 170)]
    for y in range(520, 900, 15):
        for x in range(6, W, 13):
            if y < top(x) + 46: continue
            c = cols[int(rng.integers(0, len(cols)))]
            c = mix((34, 36, 52), c, pal[4] * rng.uniform(0.45, 0.95))
            xx_ = x + rng.uniform(-3, 3); d.ellipse((xx_ - 4.5, y - 5, xx_ + 4.5, y + 5), fill=c)
    d.polygon([(x, top(x) - 34) for x in range(0, W + 1, 30)] + [(x, top(x) + 30) for x in range(W, -1, -30)], fill=(52, 56, 76))
    d.line([(x, top(x) + 30) for x in range(0, W + 1, 30)], fill=(150, 156, 176), width=5)
    for px in (96, W - 96):
        d.rectangle((px - 9, 150, px + 9, 520), fill=(60, 64, 80))
        d.rounded_rectangle((px - 80, 96, px + 80, 196), 10, fill=(44, 48, 62))
        for i in range(5):
            for j in range(3):
                d.ellipse((px - 68 + i * 30, 106 + j * 30, px - 46 + i * 30, 128 + j * 30), fill=(255, 250, 220) if mode != "belg" else (226, 232, 240))
    if mode != "belg":
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        for px in (96, W - 96): dl.ellipse((px - 170, 20, px + 170, 280), fill=(255, 244, 200, 130 if mode == "afr" else 70))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(40))); d = ImageDraw.Draw(img)
    # panneaux nus (aucun texte) + pelouse
    for i, x in enumerate(range(0, W, 180)):
        d.rectangle((x, 900, x + 176, 946), fill=[(40, 44, 66), (58, 50, 74), (36, 56, 70)][i % 3])
    y = 946; bh = 34.0; j = 0
    while y < H:
        u = (y - 946) / (H - 946); c = mix(pal[2], pal[3], u)
        d.rectangle((0, y, W, y + bh + 1), fill=mix(c, (0, 0, 0), 0.08 * (j % 2))); y += bh; bh *= 1.2; j += 1
    d.line((0, 1010, W, 1010), fill=(236, 242, 236), width=6)
    return img

def academy(base, snow):
    """portail générique d'un centre de formation (aucun nom) : bâtiment, mur, piliers, enseigne « CENTRE DE FORMATION »"""
    img = base.copy(); d = ImageDraw.Draw(img)
    wall = (198, 204, 218) if snow else (226, 220, 204)
    d.rectangle((360, 690, 1060, 1215), fill=wall)
    d.rectangle((346, 668, 1074, 700), fill=(248, 250, 254) if snow else (120, 110, 104))
    for fx in range(396, 1020, 82):
        for fy in range(730, 1150, 96):
            d.rectangle((fx, fy, fx + 52, fy + 62), fill=AMBER if (snow and (fx + fy) % 3) else (70, 96, 132))
            if snow: d.rectangle((fx - 4, fy + 62, fx + 56, fy + 68), fill=(246, 248, 252))
    stone = (112, 118, 138) if snow else (150, 140, 128)
    for x in range(0, W, 26): d.line((x, 1108, x, 1220), fill=(36, 40, 52), width=5)
    d.line((0, 1110, W, 1110), fill=(36, 40, 52), width=7)
    d.rectangle((0, 1215, W, 1412), fill=stone)
    for y in range(1250, 1412, 50):
        d.line((0, y, W, y), fill=mix(stone, (0, 0, 0), 0.18), width=3)
        for x in range((y // 50 % 2) * 60, W, 120): d.line((x, y, x, y + 50), fill=mix(stone, (0, 0, 0), 0.18), width=3)
    d.rectangle((0, 1203, W, 1222), fill=(246, 248, 252) if snow else mix(stone, (255, 255, 255), 0.3))
    # ouverture du portail
    d.rectangle((520, 1060, 900, 1412), fill=wall)
    d.rectangle((640, 1110, 780, 1330), fill=(60, 70, 96)); d.rectangle((650, 1120, 770, 1330), fill=AMBER if snow else (255, 232, 170))
    d.polygon([(520, 1412), (900, 1412), (800, 1330), (620, 1330)], fill=(226, 232, 244) if snow else (206, 194, 166))
    for px in (450, 900):
        d.rectangle((px, 1050, px + 70, 1412), fill=mix(stone, (0, 0, 0), 0.25)); d.rectangle((px - 8, 1036, px + 78, 1058), fill=mix(stone, (255, 255, 255), 0.25))
        if snow: d.ellipse((px - 10, 1016, px + 80, 1050), fill=(250, 252, 255))
    d.rounded_rectangle((420, 930, 1000, 1030), 16, fill=(24, 36, 70), outline=(236, 240, 248), width=5)
    text(d, (710, 980), "CENTRE DE FORMATION", fit("CENTRE DE FORMATION", 50, 520), (240, 244, 250), BOLD)
    if snow: d.ellipse((440, 914, 980, 944), fill=(250, 252, 255))
    return img

def gate(d, open_):
    """grille coulissante (0 = fermée, 1 = ouverte)"""
    off = open_ * 372
    x0, x1 = 520 + off, 900
    if x0 >= x1 - 4: return
    c = (26, 30, 42)
    for x in np.arange(520 + off, 900 + off, 27):
        if x < x1: d.line((x, 1084, x, 1408), fill=c, width=9); d.polygon([(x - 8, 1086), (x + 8, 1086), (x, 1064)], fill=c)
    for y in (1104, 1250, 1396): d.line((x0, y, x1, y), fill=c, width=9)

TOWN_SNOW = make_town("snow"); TOWN_GREEN = make_town("green"); TOWN_GOLD = make_town("gold")
ACAD_SNOW = academy(TOWN_SNOW, True); ACAD_GREEN = academy(TOWN_GREEN, False)
STAD_BELG = make_stadium("belg"); STAD_ITAL = make_stadium("ital"); STAD_AFR = make_stadium("afr")
SNOW_ARR = np.asarray(TOWN_SNOW.convert("RGB")).astype(np.float32); GREEN_ARR = np.asarray(TOWN_GREEN.convert("RGB")).astype(np.float32)
AFR_ARR = np.asarray(STAD_AFR.convert("RGB")).astype(np.float32)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

def reveal(A, B, c, r, soft=70, edge=0.9):
    """onde circulaire : B apparaît à l'intérieur du rayon r, liseré blanc sur le front"""
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
for _i in range(7):
    _a = math.radians(96 + _i * 13); _b = math.radians(101 + _i * 13)
    _dr.polygon([(860, 200), (860 + 2400 * math.cos(_a), 200 + 2400 * math.sin(_a)), (860 + 2400 * math.cos(_b), 200 + 2400 * math.sin(_b))], fill=(255, 246, 196, 54))
RAYS = RAYS.filter(ImageFilter.GaussianBlur(12)); EMPTY = Image.new("RGBA", (W, H), (0, 0, 0, 0))
def rays(img, a):
    if a > 0: img.alpha_composite(Image.blend(EMPTY, RAYS, min(1, a)))

def dim(img, a, col=BG):
    if a > 0: img.alpha_composite(Image.new("RGBA", (W, H), col + (int(255 * min(1, a)),)))

_sr = np.random.default_rng(5)
SNOWP = [(_sr.uniform(0, W), _sr.uniform(0, H), _sr.uniform(0.35, 1.0)) for _ in range(260)]
def snowfall(d, tg, amt=1.0, wind=50):
    for i, (x0, y0, z) in enumerate(SNOWP[:int(130 * amt)]):
        y = (y0 + tg * 250 * z) % H; x = (x0 + tg * wind * z + 16 * math.sin(tg * 1.3 + i)) % W
        r = 1.5 + 3.6 * z
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255) if z > 0.6 else (212, 222, 240))

def smoke(img, tg):
    L = Image.new("RGBA", (W, HOR), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for ci, (cx, cy) in enumerate(CHIM):
        for j in range(4):
            kk = (tg * 0.22 + j / 4 + ci * 0.13) % 1.0
            r = 10 + 30 * kk
            x = cx + 46 * kk + 8 * math.sin(tg * 1.5 + j + ci); y = cy - 150 * kk
            dl.ellipse((x - r, y - r, x + r, y + r), fill=(236, 240, 248, int(170 * (1 - kk))))
    img.alpha_composite(L)

def breath(img, hp, tg, facing=1, big=1.0, period=1.8):
    kk = (tg % period) / period
    if kk > 0.55: return
    u = kk / 0.55; w, h = int(300 * big), int(200 * big)
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for j in range(3):
        r = (12 + 24 * u + 7 * j) * big; cx = w / 2 + facing * (26 + 62 * u + 22 * j) * big; cy = h * 0.6 - (12 * u + 9 * j) * big
        dl.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, int(190 * (1 - u))))
    L = L.filter(ImageFilter.GaussianBlur(5 * big))
    img.alpha_composite(L, (int(hp[0] - w / 2), int(hp[1] - h * 0.6 + 14)))

def rings(img, c, kk, n=5, col=GOLD, span=900, w=14, gap=0.16, rate=1.3):
    if kk <= 0: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for i in range(n):
        kr = kk * rate - i * gap
        if 0 < kr < 1:
            r = 70 + kr * span
            dl.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), outline=col + (int(255 * (1 - kr) ** 1.2),), width=w)
    img.alpha_composite(L)

def footprints(d, xa, xb, y, col=(170, 186, 214), step=44):
    x = xa; i = 0
    while x < xb:
        oy = 9 if i % 2 else -5
        d.ellipse((x - 15, y + oy - 6, x + 15, y + oy + 6), fill=col); x += step; i += 1

def bag(s=1.0, rot=0.0):
    L = Image.new("RGBA", (int(360 * s), int(240 * s)), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.rounded_rectangle((20 * s, 70 * s, 340 * s, 220 * s), int(60 * s), fill=(44, 52, 78, 255), outline=(20, 24, 38, 255), width=int(6 * s))
    dl.arc((110 * s, 10 * s, 250 * s, 130 * s), 180, 360, fill=(20, 24, 38, 255), width=int(14 * s))
    dl.line((60 * s, 140 * s, 300 * s, 140 * s), fill=BEANIE + (255,), width=int(10 * s))
    return L.rotate(rot, resample=Image.BICUBIC, expand=True)

def boots(d, cx, cy, s=1.0):
    """paire de crampons génériques suspendue par les lacets"""
    d.line((cx - 60 * s, cy - 150 * s, cx - 60 * s, cy - 70 * s), fill=(60, 60, 74), width=max(2, int(5 * s)))
    d.line((cx + 50 * s, cy - 150 * s, cx + 50 * s, cy - 60 * s), fill=(60, 60, 74), width=max(2, int(5 * s)))
    for dx, dy in ((-60, 0), (50, 14)):
        x = cx + dx * s; y = cy + dy * s
        d.polygon([(x - 60 * s, y), (x - 54 * s, y - 62 * s), (x - 4 * s, y - 70 * s), (x + 16 * s, y - 34 * s), (x + 74 * s, y - 18 * s), (x + 74 * s, y + 8 * s)], fill=(26, 26, 34))
        d.line((x - 46 * s, y - 50 * s, x + 6 * s, y - 42 * s), fill=BEANIE, width=max(2, int(6 * s)))
        for i in range(5): d.rectangle((x - 54 * s + i * 28 * s, y + 8 * s, x - 46 * s + i * 28 * s, y + 22 * s), fill=(170, 170, 182))

def shovel(d, rh, lh, s):
    dx, dy = lh[0] - rh[0], lh[1] - rh[1]; L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    a = (rh[0] - ux * 0.12 * s, rh[1] - uy * 0.12 * s); b = (lh[0] + ux * 0.42 * s, lh[1] + uy * 0.42 * s)
    d.line((a, b), fill=(150, 106, 64), width=max(6, int(0.045 * s)))
    e = (b[0] + ux * 0.26 * s, b[1] + uy * 0.26 * s); hw = 0.13 * s
    d.polygon([(b[0] + nx * hw, b[1] + ny * hw), (e[0] + nx * hw * 0.9, e[1] + ny * hw * 0.9), (e[0] - nx * hw * 0.9, e[1] - ny * hw * 0.9), (b[0] - nx * hw, b[1] - ny * hw)],
              fill=(176, 186, 204), outline=(96, 106, 126))
    return e

def band_on_arm(d, s, k=1.0):
    """brassard doré « C » sur le bras avant (d'après les articulations du dernier personnage dessiné)"""
    a, b = JT["ls"], JT["le"]
    p = _pt(a, b, 0.42); q = _pt(a, b, 0.86); w = int(0.15 * s * 1.25 * (1 + 0.6 * (1 - eout(max(0, k) / 0.25))))
    d.line((p, q), fill=GOLD, width=w); d.line((p, q), fill=(150, 104, 20), width=max(2, w // 9))
    d.line((_pt(p, q, 0.08), _pt(p, q, 0.92)), fill=GOLD, width=w - max(4, w // 5))
    c = _pt(p, q, 0.5); text(d, c, "C", int(w * 0.72), BG, BOLD)

def armband(d, cx, cy, s=1.0, k=1.0):
    sc = s * (1 + 0.4 * (1 - eout(max(0, k) / 0.2)))
    d.rounded_rectangle((cx - 170 * sc, cy - 90 * sc, cx + 170 * sc, cy + 90 * sc), int(30 * sc), fill=GOLD, outline=(140, 100, 20), width=int(8 * sc))
    text(d, (cx, cy + 4 * sc), "C", int(150 * sc), BG, BOLD)

def trophy(d, cx, cy, s=1.0, col=GOLD):
    """coupe générique à deux anses (ne reproduit aucun trophée réel)"""
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.arc((cx - 190 * s, cy - 230 * s, cx - 70 * s, cy - 90 * s), 90, 270, fill=mix(col, (0, 0, 0), 0.2), width=max(3, int(14 * s)))
    d.arc((cx + 70 * s, cy - 230 * s, cx + 190 * s, cy - 90 * s), 270, 90, fill=mix(col, (0, 0, 0), 0.2), width=max(3, int(14 * s)))
    d.polygon([q(-120, -230), q(120, -230), q(80, -60), q(25, -20), q(25, 50), q(80, 90), q(-80, 90), q(-25, 50), q(-25, -20), q(-80, -60)], fill=col)
    d.polygon([q(-120, -230), q(-60, -230), q(-40, -60), q(-80, -60)], fill=mix(col, (255, 255, 255), 0.45))

def goal(d, cx, by, s=1.0, col=(246, 246, 246)):
    w, h = 820 * s, 330 * s
    for i in range(0, 15):
        x = cx - w / 2 + i * w / 14; d.line((x, by - h, x + (x - cx) * 0.08, by - 20 * s), fill=(200, 206, 214), width=2)
    for j in range(0, 8):
        y = by - h + j * h / 7; d.line((cx - w / 2, y, cx + w / 2, y), fill=(200, 206, 214), width=2)
    t = max(6, int(14 * s))
    d.line((cx - w / 2, by, cx - w / 2, by - h, cx + w / 2, by - h, cx + w / 2, by), fill=col, width=t)

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-500, 0), i % 3) for i in range(80)]
def confetti(d, kv, amt=1.0):
    for x0, y0, c in CONF[:int(len(CONF) * amt)]:
        y = y0 + kv * 620; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < 1480: d.rectangle((x, y, x + 14, y + 24), fill=[JER, WHITE, GOLD][c])

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
    """titre de la série de 0,5 s à 3,6 s (l'accroche passe d'abord)"""
    if tg > 3.6 or tg < 0.5: return
    e = eout((tg - 0.5) / 0.25); o = ease((tg - 3.25) / 0.35)
    y = -150 + 220 * e - 260 * o
    d.rounded_rectangle((90, y, W - 90, y + 130), 22, fill=(96, 24, 40), outline=GOLD, width=5)
    text(d, (W / 2, y + 45), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), WHITE, BOLD)
    text(d, (W / 2, y + 98), "ÉPISODE 7", 40, GOLD, MONO)

def _others():
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for x, y, s, pose, jc, bc, fc in ((690, FEET - 14, 250, "talk", (86, 110, 156), (60, 150, 140), 1), (840, FEET + 4, 262, "stand", (118, 122, 136), (190, 80, 70), -1),
                                      (975, FEET - 8, 242, "talk", (70, 130, 124), (90, 100, 170), -1)):
        shadow(d, x, y, s); P(L, x, y, s, pose, winter=True, jersey=jc, beanie=bc, facing=fc, glow=0.6)
        d = ImageDraw.Draw(L)
    return L
OTHERS = _others()

def beanie_sprite(s, rot):
    w = int(0.34 * s); L = Image.new("RGBA", (w * 2, w * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.pieslice((w * 0.5, w * 0.55, w * 1.5, w * 1.75), 180, 360, fill=BEANIE)
    d.rounded_rectangle((w * 0.46, w * 1.08, w * 1.54, w * 1.3), int(w * 0.08), fill=mix(BEANIE, (255, 255, 255), 0.55))
    d.ellipse((w * 0.84, w * 0.36, w * 1.16, w * 0.68), fill=(250, 250, 250))
    return L.rotate(rot, resample=Image.BICUBIC)

def burst(d, x, y, k, n=16, r=160, col=ORANGE, seed=0, w=7):
    if k <= 0 or k > 0.7: return
    rng = np.random.default_rng(seed); e = eout(k / 0.5); a = 1 - k / 0.7
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        r0, r1 = r * (0.3 + 0.5 * (1 - a)) * e, r * (0.6 + 0.6 * rng.random()) * e
        if r1 > r0: d.line((x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r1 * math.cos(ang), y + r1 * math.sin(ang)), fill=col, width=max(2, int(w * a)))

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    img.paste(TOWN_SNOW); smoke(img, tg)
    img.alpha_composite(OTHERS); d = ImageDraw.Draw(img)
    hx = 250
    footprints(d, 30, hx - 30, FEET + 4)
    shadow(d, hx, FEET, 268); P(img, hx, FEET, 268, "shy", winter=True)
    breath(img, JT["head"], tg, 1, 0.9); breath(img, (750, FEET - 380), tg + 0.7, 1, 1.0, 1.3)
    d = ImageDraw.Draw(img); snowfall(d, tg, 1.0)
    topsh(img); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    sc = 1 + 0.3 * (1 - eout((tg + 0.12) / 0.2))
    text(d, (W / 2, 400), "TROP", int(fit("TROP", 150, 1000) * sc), WHITE, BOLD, stroke=9, scol=BG)
    kk = tg + 0.1
    text(d, (W / 2, 570), "TIMIDE ?", pop(kk, fit("TIMIDE ?", 190, 1000), 0.25, 0.2), ORANGE, BOLD, stroke=10, scol=BG)
    kd = kM(tg, "caractere")
    TX(d, 740, "« PAS LE CARACTÈRE » ?", 76, ICE, kd, maxw=900, stroke=6)
    return dict(hit=max(0, 1 - kk / 0.3))

def s_intro(img, d, tg, k):
    img.paste(TOWN_SNOW); smoke(img, tg); d = ImageDraw.Draw(img)
    kr = kM(tg, "rejet"); kb = kM(tg, "brassard"); hit = 0.0
    u = eout(min(1, max(0, kb) / 0.4))
    hx, hy = 330, FEET + 30
    shadow(d, hx, hy, 290); P(img, hx, hy, 290, blend_pose(POSES["shy"], POSES["stand"], u), winter=True)
    d = ImageDraw.Draw(img)
    if kb > 0: band_on_arm(d, 290, kb)
    breath(img, JT["head"], tg, 1, 1.1)
    d = ImageDraw.Draw(img); snowfall(d, tg, 0.8)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 290, "L'HISTOIRE VRAIE", 100, WHITE, k)
    TX(d, 400, "D'UN DÉFENSEUR", 84, ICE, k - 0.25)
    TX(d, 550, "DU REJET…", 110, (214, 222, 236), kr)
    if kb > 0:
        TX(d, 690, "AU BRASSARD", 126, GOLD, kb, stroke=8)
        armband(d, 800, 1010, 0.72, kb)
        if kb < 0.25: hit = 1 - kb / 0.25
    return dict(hit=hit)

def s_ville(img, d, tg, k):
    img.paste(TOWN_SNOW); smoke(img, tg); d = ImageDraw.Draw(img)
    kv = kM(tg, "vosges"); ks = kM(tg, "senegal")
    u = min(1, k / 3.9); x = lerp(-70, 640, u)
    footprints(d, -40, x - 34, FEET + 4)
    shadow(d, x, FEET, 215)
    P(img, x, FEET, 215, run_pose(k * 6.5) if u < 1 else "shy", winter=True)
    breath(img, JT["head"], tg, 1, 0.8, 1.4)
    d = ImageDraw.Draw(img); snowfall(d, tg, 0.7)
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 290, "IL GRANDIT DANS", 76, WHITE)
    TX(d, 410, "UNE PETITE VILLE", 110, ORANGE, k)
    TX(d, 530, "DE MONTAGNE", 92, WHITE, kv)
    TX(d, 660, "FAMILLE VENUE D'AFRIQUE DE L'OUEST", 54, GOLD, ks, stroke=6)
    return dict(hit=max(0, 1 - k / 0.25) if k > 0 else 0)

def s_metz(img, d, tg, k):
    img.paste(ACAD_SNOW); d = ImageDraw.Draw(img)
    kc = kM(tg, "centre"); kp = kM(tg, "prend"); hit = 0.0
    gate(d, ease((k - 0.3) / 1.1))
    u = min(1, k / 2.0); e = ease(max(0, kp) / 0.5)
    x = lerp(110, 640, u) + 70 * e; s = 200 * (1 - 0.14 * e); y = FEET - 26 * e
    footprints(d, 20, lerp(110, 640, u) - 30, FEET + 4)
    shadow(d, x, y, s); P(img, x, y, s, run_pose(k * 7) if (u < 1 or 0 < e < 1) else "stand", winter=True)
    d = ImageDraw.Draw(img); snowfall(d, tg, 0.6)
    topsh(img); d = ImageDraw.Draw(img)
    badge(d, 190, 330, "12 ANS", k, GOLD, 112)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    if kc > 0:
        TX(d, 290, "LE CENTRE DE", 66, WHITE, x=660, maxw=620)
        TX(d, 380, "FORMATION", 96, GOLD, kc, x=660, maxw=640)
    if kp > 0:
        hit = max(hit, stamp(img, "IL EST PRIS", (W / 2, 620), 124, -5, kp, (40, 230, 130)))
    return dict(hit=hit)

def s_renvoi(img, d, tg, k):
    img.paste(ACAD_SNOW); d = ImageDraw.Draw(img)
    kr = kM(tg, "renvoie"); ki = kM(tg, "introverti"); kn = kM(tg, "niveau"); hit = 0.0; shake = 0.0
    cl = eout(max(0, kr) / 0.22)
    gate(d, 1 - cl)
    wv = ease(max(0, ki) / 2.6); x = lerp(690, 470, wv)
    footprints(d, x + 30, 690, FEET + 4)
    # le sac tombe dans la neige
    ub = eout(min(1, max(0, kr - 0.15) / 0.45))
    bg_ = bag(0.5, lerp(8, 78, ub))
    _bq = Q(lerp(x + 20, 830, ub), lerp(FEET - 300, FEET - 130, ub)); img.alpha_composite(bg_, (int(_bq[0] - bg_.width / 2), int(_bq[1])))
    d = ImageDraw.Draw(img)
    if 0 < kr - 0.5 < 0.5:
        for i in range(7):
            a = math.pi * (1.1 + i * 0.13); r = 150 * eout((kr - 0.5) / 0.5)
            d.ellipse((800 + r * math.cos(a) - 9, FEET - 20 + r * 0.6 * math.sin(a) - 9, 800 + r * math.cos(a) + 9, FEET - 20 + r * 0.6 * math.sin(a) + 9), fill=(250, 252, 255))
    shadow(d, x, FEET, 196)
    pose = "stand" if kr <= 0 else (blend_pose(POSES["stand"], POSES["sad"], eout(kr / 0.4)) if ki <= 0 or wv >= 1 else dict(run_pose(k * 3.2), t=15))
    if isinstance(pose, dict) and "t" in pose and ki > 0 and wv < 1: pose = dict(pose, la=(pose["la"][0] * 0.4, 20), ra=(pose["ra"][0] * 0.4, -20))
    P(img, x, FEET, 196, pose, winter=True, facing=-1 if ki > 0 else 1)
    img.alpha_composite(Image.new("RGBA", (W, H), (36, 56, 110, int(70 * min(1, max(0, kr) / 0.6)))))
    d = ImageDraw.Draw(img); snowfall(d, tg, 1.0 + 1.0 * min(1, max(0, kr)), wind=-190 if kr > 0 else 50)
    topsh(img); d = ImageDraw.Draw(img)
    badge(d, W / 2, 320, "15 ANS", k, RED, 112, WHITE)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    if kr > 0:
        hit = max(hit, stamp(img, "RENVOYÉ", (W / 2, 520), 150, -6, kr, (255, 70, 60))); d = ImageDraw.Draw(img)
        shake = max(0, 1 - kr / 0.35)
    TX(d, 690, "« TROP INTROVERTI »", 88, WHITE, ki, maxw=900)
    TX(d, 800, "« PAS AU NIVEAU »", 88, ICE, kn, maxw=900)
    return dict(hit=hit, shake=shake)

def _shovel_scene(img, d, tg, k, stop):
    """il déblaie seul le petit terrain enneigé, pelletée après pelletée"""
    s = 212; x = 330; per = 1.15
    done = min(k, stop) / per
    wdt = 150 + 62 * done
    d.rounded_rectangle((x - 60, FEET - 34, x - 60 + wdt, FEET + 64), 34, fill=(70, 150, 76)); d.rounded_rectangle((x - 40, FEET - 6, x - 80 + wdt, FEET + 26), 14, fill=(58, 134, 66))
    ph = (k % per) / per; pile = 40 + 16 * done
    d.pieslice((860 - pile * 1.5, FEET + 30 - pile * 1.4, 860 + pile * 1.5, FEET + 30 + pile * 1.4), 180, 360, fill=(246, 249, 254))
    d.ellipse((860 - pile * 1.5, FEET + 18, 860 + pile * 1.5, FEET + 44), fill=(206, 216, 236))
    if k >= stop:
        e = eout((k - stop) / 0.4)
        shadow(d, x, FEET, s); P(img, x, FEET, s, blend_pose(POSES["lean"], POSES["sad"], e), winter=True)
        d = ImageDraw.Draw(img)
        d.line((x + 150, FEET - 250, x + 132, FEET + 6), fill=(150, 106, 64), width=10)
        d.polygon([(x + 104, FEET + 2), (x + 160, FEET + 6), (x + 152, FEET + 62), (x + 104, FEET + 56)], fill=(176, 186, 204), outline=(96, 106, 126))
        return d
    if ph < 0.45: wv = ease(ph / 0.3)
    elif ph < 0.7: wv = 1 - eout((ph - 0.45) / 0.2)
    else: wv = 0.0
    S_ = s * 1.25
    shadow(d, x, FEET, s); P(img, x, FEET + 6, s, blend_pose(POSES["throw"], POSES["scoop"], wv), winter=True)
    d = ImageDraw.Draw(img)
    hm = _pt(JT["lh"], JT["rh"], 0.5)
    tip = (lerp(hm[0] + 0.42 * S_, x + 0.98 * S_, wv), lerp(hm[1] - 0.62 * S_, FEET + 26, wv))
    dx, dy = tip[0] - JT["rh"][0], tip[1] - JT["rh"][1]; L_ = math.hypot(dx, dy) or 1.0; ux, uy = dx / L_, dy / L_
    b0 = (tip[0] - ux * 0.24 * S_, tip[1] - uy * 0.24 * S_); hw = 0.12 * S_
    d.line((JT["rh"][0] - ux * 0.1 * S_, JT["rh"][1] - uy * 0.1 * S_, b0[0], b0[1]), fill=(150, 106, 64), width=11)
    d.polygon([(b0[0] - uy * hw, b0[1] + ux * hw), (tip[0] - uy * hw * 0.9, tip[1] + ux * hw * 0.9), (tip[0] + uy * hw * 0.9, tip[1] - ux * hw * 0.9), (b0[0] + uy * hw, b0[1] - ux * hw)],
              fill=(176, 186, 204), outline=(96, 106, 126))
    for hp in (JT["lh"], JT["rh"]): d.ellipse((hp[0] - 13, hp[1] - 13, hp[0] + 13, hp[1] + 13), fill=SKIN)
    if 0.25 < ph < 0.62:
        c = _pt(b0, tip, 0.5); d.ellipse((c[0] - 36, c[1] - 40, c[0] + 36, c[1] + 6), fill=(250, 252, 255))
    if ph >= 0.6:
        v = (ph - 0.6) / 0.4; sx, sy = hm[0] + 0.3 * S_, hm[1] - 0.45 * S_
        for j in range(5):
            vv = min(1, v * (1 + 0.12 * j)); px = lerp(sx, 860 + (j - 2) * 22, vv); py = lerp(sy, FEET, vv) - 200 * math.sin(math.pi * vv) * (0.7 + 0.1 * j)
            r = 20 - 3 * j; d.ellipse((px - r, py - r, px + r, py + r), fill=(250, 252, 255))
    return d

def s_retour(img, d, tg, k):
    img.paste(TOWN_SNOW); smoke(img, tg); d = ImageDraw.Draw(img)
    kb = tg - K["build_start"] + 0.1; kl = kM(tg, "loin"); ki = kM(tg, "nimporte"); kc = kM(tg, "crampons"); hit = 0.0
    stop = M("crampons") - 0.5 - SC["retour"]
    if kc > -0.6: boots(d, 640, HOR + 150, 1.1)
    d = _shovel_scene(img, d, tg, k, stop)
    breath(img, JT["head"], tg, 1, 0.9, 1.15)
    d = ImageDraw.Draw(img); snowfall(d, tg, 1.3, wind=-80)
    img.alpha_composite(Image.new("RGBA", (W, H), (36, 56, 110, int(60 * ease(max(0, ki) / 1.0)))))
    topsh(img); d = ImageDraw.Draw(img)
    TX(d, 290, "RETOUR AU PETIT CLUB", 80, WHITE, k)
    if kb > 0:
        TX(d, 440, "3 ANS", 170, ORANGE, kb, amp=0.3, stroke=9)
        if kb < 0.25: hit = 1 - kb / 0.25
    TX(d, 575, "LOIN DES CENTRES DE FORMATION", 58, ICE, kl, stroke=6)
    if ki > 0: text(d, (W / 2, 690), typew("N'IMPORTE QUI AURAIT", ki, 26), fit("N'IMPORTE QUI AURAIT", 70, 940), WHITE, BOLD, stroke=6, scol=BG)
    if kc > -0.4: text(d, (W / 2, 780), typew("RANGÉ SES CRAMPONS…", kc + 0.4, 26), fit("RANGÉ SES CRAMPONS…", 80, 940), ORANGE, BOLD, stroke=7, scol=BG)
    return dict(hit=hit)

_cr = np.random.default_rng(77)
CHUNK = [(_cr.uniform(0, 2 * math.pi), _cr.uniform(0.7, 1.02), _cr.uniform(7, 22)) for _ in range(70)]
def s_voix(img, d, tg, k):
    """LE CRI : son souffle chasse la neige — onde circulaire qui révèle la pelouse et le soleil, le bonnet s'envole"""
    kb = tg - K["boom"]; kk = max(0.0, kb + 0.06)
    s = 262; hx = W / 2; jump = 46 * math.sin(math.pi * min(1, kk / 0.45)) if kk > 0 else 0
    hy = FEET + 10 - jump
    head = Q(hx, FEET + 10 - jump - 1.38 * s * 1.25)
    r = eout(kk / 1.6) * 2300 if kk > 0 else 0
    base = reveal(SNOW_ARR, GREEN_ARR, head, r)
    img.paste(base); d = ImageDraw.Draw(img)
    rays(img, min(1, max(0, kk - 0.2) / 0.5))
    d = ImageDraw.Draw(img)
    if r < 60:
        d.rounded_rectangle((270, FEET - 34, 270 + 150 + 62 * 4.4, FEET + 64), 34, fill=(70, 150, 76))
        snowfall(d, tg, 1.3, wind=-80)
    # paquets de neige soufflés par l'onde
    if 0 < kk < 1.4:
        for a, f, sz in CHUNK:
            rr = r * f; px = head[0] + rr * math.cos(a); py = head[1] + rr * math.sin(a) * 0.9
            z = sz * (1 - 0.5 * kk / 1.4); d.ellipse((px - z, py - z, px + z, py + z), fill=(255, 255, 255))
    rings(img, head, kk, 6, GOLD, 1050, 16, 0.14, 1.25); rings(img, head, kk - 0.07, 6, WHITE, 1050, 6, 0.14, 1.25)
    d = ImageDraw.Draw(img)
    burst(d, head[0], head[1], kk, 26, 520, (255, 240, 190), 3, 10)
    if kM(tg, "terrain") > 0:
        rings(img, head, kM(tg, "terrain"), 4, GOLD, 900, 14); d = ImageDraw.Draw(img)
    u = eout(min(1, kk / 0.22))
    shadow(d, hx, FEET + 10, s * (1 - jump / 300), GSH if r > 300 else SNOW_SH)
    P(img, hx, hy, s, blend_pose(POSES["sad"], POSES["shout"], u), winter=True, beanie=BEANIE if kk < 0.08 else None, glow=1.5)
    if kk >= 0.08:      # le bonnet s'envole
        q = kk - 0.08; bx = head[0] + 190 * q; by = head[1] - 70 - 820 * q + 520 * q * q
        sp = beanie_sprite(s * 1.25, -q * 420); img.alpha_composite(sp, (int(bx - sp.width / 2), int(by - sp.height / 2)))
    topsh(img, 0.7); d = ImageDraw.Draw(img)
    hit = max(0, 1 - kk / 0.3) if kk > 0 else 0
    e = eout(kk / 0.22) if kk > 0 else 0
    kt = kM(tg, "terrain"); l2 = "SUR LE TERRAIN !" if kt > -0.55 else "IL VA LA TROUVER"
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, e)
    f1 = fit("SA VOIX,", 160, 1000); f2 = pop(kt + 0.55, fit("SUR LE TERRAIN !", 128, 990), 0.12) if kt > -0.55 else fit("IL VA LA TROUVER", 118, 990)
    for off, c in ((12, (255, 60, 80)), (-12, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        text(d, (x1 + o, 300), "SA VOIX,", f1, c, BOLD, stroke=9 if c == WHITE else 0, scol=BG)
        text(d, (x2 - o, 470), l2, f2, c if c != WHITE else GOLD, BOLD, stroke=9 if c == WHITE else 0, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.9, flash=max(0, 0.9 - kk * 2.6) if kk > 0 else 0)

def tyre(d, x, y):
    d.rounded_rectangle((x - 92, y - 34, x + 92, y + 34), 30, fill=(22, 22, 28))
    for i in range(-3, 4): d.line((x + i * 24 - 6, y - 32, x + i * 24 + 6, y + 32), fill=(58, 58, 68), width=6)
    d.rounded_rectangle((x - 92, y - 34, x + 92, y + 34), 30, outline=(8, 8, 12), width=5)

def paper(img, cx, cy, ks):
    """contrat générique (aucun nom) : lignes + signature qui se trace"""
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

def s_pro(img, d, tg, k):
    kt = kM(tg, "travaille"); kc = kM(tg, "confiance"); km = kM(tg, "metz2"); ks = kM(tg, "signe"); hit = 0.0
    if km <= 0:
        img.paste(TOWN_GREEN); rays(img, 0.8); d = ImageDraw.Draw(img)
        u = min(1, k / (M("metz2") - SC["pro"])); x = lerp(400, 820, u); s = lerp(225, 285, ease(u))
        tx_ = x - 300; ty = FEET + 16; _tq = Q(tx_, ty)
        for oy in (-14, 14): d.line((Q(60, ty)[0], _tq[1] + oy + 16, _tq[0], _tq[1] + oy + 16), fill=(52, 124, 60), width=9)
        for j in range(4):
            q = ((k * 2.2 + j / 4) % 1.0); d.ellipse((_tq[0] - 110 - 70 * q - 16 * q, _tq[1] - 10 - 50 * q - 16 * q, _tq[0] - 110 - 70 * q + 16 + 16 * q, _tq[1] - 10 - 50 * q + 16 + 16 * q), fill=mix((120, 160, 96), (210, 214, 190), q))
        _tq = Q(tx_, ty); tyre(d, _tq[0], _tq[1])
        shadow(d, x, FEET, s, GSH)
        P(img, x, FEET, s, dict(run_pose(k * 8.5), t=-26), glow=1.2)
        d = ImageDraw.Draw(img)
        d.line((JT["hip"][0] - 10, JT["hip"][1] - 6, _tq[0] + 84, _tq[1] - 16), fill=(226, 206, 150), width=7)
        topsh(img, 0.85); d = ImageDraw.Draw(img)
        TX(d, 290, "IL TRAVAILLE", 110, WHITE, kt, amp=0.25)
        TX(d, 420, "IL GRANDIT", 100, ICE, tg - (M("travaille") + M("confiance")) / 2 + 0.15, amp=0.25)
        TX(d, 545, "IL PREND CONFIANCE", 88, GOLD, kc, amp=0.14)
        if 0 < kc < 0.25: hit = 1 - kc / 0.25
        return dict(hit=hit)
    img.paste(ACAD_GREEN); d = ImageDraw.Draw(img)
    op = eout(min(1, km / 0.6)); gate(d, op)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(540, 1412), (880, 1412), (1060, 1700), (300, 1700)], fill=(255, 236, 170, int(120 * op))); img.alpha_composite(L); d = ImageDraw.Draw(img)
    u = ease((km - 0.5) / 1.3); x = lerp(210, 640, u)
    shadow(d, x, FEET, 240, GSH); P(img, x, FEET, 240, run_pose(k * 7) if 0 < u < 1 else "stand", glow=1.2)
    topsh(img, 0.85); d = ImageDraw.Draw(img)
    TX(d, 290, "LE CLUB QUI L'AVAIT RENVOYÉ", 68, WHITE)
    TX(d, 400, "REVIENT LE CHERCHER", 96, GOLD, km)
    if km < 0.25: hit = 1 - km / 0.25
    if ks > 0:
        paper(img, 880, 690, ks); d = ImageDraw.Draw(img)
        badge(d, 180, 620, "19 ANS", ks, GOLD, 104)
        hit = max(hit, stamp(img, "CONTRAT PRO", (W / 2 - 60, 840), 104, -6, ks - 0.12, (214, 30, 64)))
    return dict(hit=hit)

def s_naples(img, d, tg, k):
    kg = kM(tg, "genk"); kn = kM(tg, "naples"); kd = kM(tg, "defenseur2"); kb = kM(tg, "brassard2"); hit = 0.0
    if kn <= 0.4: img.paste(Image.blend(STAD_BELG, STAD_ITAL, ease(kn / 0.4)) if kn > 0 else STAD_BELG)
    else: img.paste(STAD_ITAL)
    d = ImageDraw.Draw(img)
    if kn <= 0:      # la Belgique : il gagne la coupe
        u = min(1, k / 1.3); x = lerp(-60, W / 2, eout(u))
        shadow(d, x, FEET, 245, GSH)
        if kg > 0:
            confetti(d, kg * 1.2, 0.7)
            P(img, x, FEET - 30 * abs(math.sin(kg * 7)) * max(0, 1 - kg), 245, "up", glow=1.3); d = ImageDraw.Draw(img)
            c = _pt(JT["lh"], JT["rh"], 0.5); trophy(d, c[0], c[1] - 40, 0.62 * (1 + 0.3 * (1 - eout(kg / 0.25))))
            if kg < 0.25: hit = 1 - kg / 0.25
        else: P(img, x, FEET, 245, run_pose(k * 8) if u < 1 else "stand", glow=1.2)
        topsh(img, 0.8); d = ImageDraw.Draw(img)
        TX(d, 290, "LA BELGIQUE", 112, WHITE, tg - K["gate1"] + 0.3, amp=0.25)
        TX(d, 430, "IL GAGNE LA COUPE", 92, GOLD, kg)
        return dict(hit=hit)
    if kb <= 0:      # l'Italie : le mur — tous les ballons rebondissent sur lui
        x = W / 2 - 150; s = 250; per = 0.62
        n = int(max(0, kn - 0.25) / per); ph = (max(0, kn - 0.25) % per) / per
        kinds = [("head", -1.32), ("wide", -0.92), ("kick", -0.3), ("head", -1.32), ("kick", -0.3), ("wide", -0.92)]
        pz, hgt = kinds[n % len(kinds)]
        cy = FEET + hgt * s * 1.25; cx = x + (150 if pz != "wide" else 96)
        near = math.exp(-((ph - 0.5) / 0.16) ** 2)
        pose = blend_pose(POSES["wide"], POSES[pz], near)
        shadow(d, x, FEET, s, GSH); P(img, x, FEET - (40 * near if pz == "head" else 0), s, pose, glow=1.3)
        d = ImageDraw.Draw(img)
        if kn > 0.25:
            if ph < 0.5:
                v = ph / 0.5; bx = lerp(W + 80, cx, v); by = lerp(cy - 260 + 120 * (n % 3), cy, v) - 60 * math.sin(math.pi * v)
                for j in range(1, 5): d.ellipse((bx + j * 34 - 16, by - 16 + j * 3, bx + j * 34 + 16, by + 16 + j * 3), fill=mix((255, 255, 255), pal_g(), 0.25 + 0.18 * j))
            else:
                v = (ph - 0.5) / 0.5; bx = lerp(cx, W + 120, v); by = cy - 520 * v + 200 * v * v
                burst(d, cx, cy, v * 0.7, 12, 150, (255, 244, 200), n, 8)
            ball(d, bx, by, 32, WHITE, tg * 12)
        topsh(img, 0.8); d = ImageDraw.Draw(img)
        TX(d, 290, "L'ITALIE", 120, WHITE, kn, amp=0.25)
        if kd > 0:
            hit = max(hit, stamp(img, "MEILLEUR DÉFENSEUR", (W / 2, 450), 104, -4, kd, GOLD)); d = ImageDraw.Draw(img)
            TX(d, 590, "DU CHAMPIONNAT", 72, WHITE, kd - 0.3)
        if 0 < kn < 0.25: hit = max(hit, 1 - kn / 0.25)
        return dict(hit=hit)
    # le brassard
    s = 330; x = W / 2 - 40; y = FEET + 70
    shadow(d, x, y, s, GSH); P(img, x, y, s, blend_pose(POSES["stand"], POSES["fist"], eout(kb / 0.35)), glow=1.5)
    d = ImageDraw.Draw(img); band_on_arm(d, s, kb)
    c = _pt(JT["ls"], JT["le"], 0.6); burst(d, c[0], c[1], kb, 18, 300, GOLD, 5, 9)
    topsh(img, 0.8); d = ImageDraw.Draw(img)
    TX(d, 300, "LE « TROP TIMIDE »", 82, ICE)
    TX(d, 430, "PORTE LE BRASSARD", 96, GOLD, kb, stroke=8)
    if kb < 0.25: hit = 1 - kb / 0.25
    return dict(hit=hit)

def pal_g(): return (92, 170, 78)

def _mates(img, tg, xs, y, s, pose_fn):
    for i, x in enumerate(xs):
        d = ImageDraw.Draw(img); shadow(d, x, y, s, GSH)
        P(img, x, y, s, pose_fn(i), glow=0.8)

def s_afrique(img, d, tg, k):
    ka = kM(tg, "afrique"); kc = kM(tg, "capitaine2"); kf = kM(tg, "finale"); km = kM(tg, "marque"); kp = kM(tg, "premier"); ks = kM(tg, "soulever")
    global GLOVE
    hit = 0.0; flash = 0.0
    img.paste(STAD_AFR); d = ImageDraw.Draw(img)
    if kp > 0:       # il soulève la coupe
        confetti(d, kp)
        jump = 26 * abs(math.sin(tg * 7))
        _mates(img, tg, (170, 350, 730, 910), FEET - 40, 205, lambda i: "up" if math.sin(tg * 8 + i * 1.7) > -0.3 else "fist")
        d = ImageDraw.Draw(img); shadow(d, W / 2, FEET + 20, 270, GSH)
        P(img, W / 2, FEET + 20 - jump * 0.4, 270, "up", glow=1.6); d = ImageDraw.Draw(img)
        band_on_arm(d, 270)
        c = _pt(JT["lh"], JT["rh"], 0.5); lift = 60 * eout(min(1, max(0, ks) / 0.4))
        trophy(d, c[0], c[1] - 30 - lift, 0.72)
        if ks > 0: burst(d, c[0], c[1] - 150 - lift, ks, 20, 330, GOLD, 9, 9)
        crowd(d, tg, up_all=True, rise=0.8)
        topsh(img, 0.9); d = ImageDraw.Draw(img)
        TX(d, 290, "1er CAPITAINE", 130, GOLD, kp, stroke=9)
        TX(d, 420, "DE SON PAYS", 90, WHITE, kp - 0.2)
        TX(d, 540, "À SOULEVER LA COUPE", 80, WHITE, ks)
        if kp < 0.25: hit = 1 - kp / 0.25
        return dict(hit=hit, flash=0.4 * max(0, 1 - kp / 0.3))
    if kf <= 0:      # le capitaine entre en tête de son équipe
        u = min(1, k / 2.6); x = lerp(-80, 560, u)
        _mates(img, tg, (x - 230, x - 430, x - 630), FEET - 10, 215, lambda i: run_pose(k * 7 + i * 1.3) if u < 1 else "stand")
        d = ImageDraw.Draw(img); shadow(d, x, FEET + 10, 250, GSH)
        P(img, x, FEET + 10, 250, run_pose(k * 7) if u < 1 else blend_pose(POSES["stand"], POSES["point"], eout((k - 2.6) / 0.3)), glow=1.4)
        d = ImageDraw.Draw(img); band_on_arm(d, 250, kc if kc > 0 else 1.0)
        topsh(img, 0.9); d = ImageDraw.Draw(img)
        TX(d, 290, "2022", 150, GOLD, k, amp=0.3, stroke=9)
        TX(d, 430, "COUPE D'AFRIQUE", 100, WHITE, ka)
        if kc > 0:
            TX(d, 570, "IL EST LE CAPITAINE", 86, GOLD, kc)
            if kc < 0.25: hit = max(hit, 1 - kc / 0.25)
        if 0 < k < 0.25: hit = max(hit, 1 - k / 0.25)
        return dict(hit=hit)
    # finale : tir au but
    gx, gy = 640, 1160
    goal(d, gx, gy, 0.66)
    u = min(1, max(0, km + 0.32) / 0.32)
    dv = eout(min(1, max(0, km + 0.3) / 0.4))
    GLOVE = (250, 250, 250)
    P(img, lerp(gx, gx - 150, dv), gy, 112, "wide", rot=62 * dv, jersey=(120, 124, 140), shorts=(40, 42, 54), sock=(120, 124, 140), glow=0.6, fixed=True)
    GLOVE = None
    d = ImageDraw.Draw(img)
    d.ellipse((462, FEET + 12, 498, FEET + 24), fill=(240, 246, 240))
    r0 = min(1, max(0, km + 1.3) / 0.9); hx = lerp(150, 380, ease(r0))
    shadow(d, hx, FEET + 40, 250, GSH)
    P(img, hx, FEET + 40, 250, "kick" if u > 0.05 else (run_pose(k * 8) if 0 < r0 < 1 else "stand"), glow=1.4)
    d = ImageDraw.Draw(img); band_on_arm(d, 250)
    bx = lerp(480, 842, eout(u)); by = lerp(FEET, 985, eout(u)) - 60 * math.sin(math.pi * u)
    ball(d, bx, by, 30 - 15 * u, WHITE, tg * 12)
    topsh(img, 0.9); d = ImageDraw.Draw(img)
    TX(d, 300, "FINALE", 130, WHITE, kf, amp=0.25, stroke=8)
    TX(d, 430, "TIRS AU BUT", 96, ICE, kf - 0.3)
    if km > 0:
        burst(d, 842, 985, km, 16, 240, WHITE, 2, 8)
        hit = max(hit, stamp(img, "IL MARQUE !", (W / 2, 640), 150, -6, km, GOLD))
        flash = 0.4 * max(0, 1 - km / 0.3)
    return dict(hit=hit, flash=flash)

def s_regard(img, d, tg, k):
    kt = kM(tg, "timide3"); kl = kM(tg, "lever"); kp = kM(tg, "pays"); hit = 0.0
    hx, hy, s = W / 2, FEET - 30, 240
    head = Q(hx, hy - 1.38 * s * 1.25)
    if kl <= 0:      # souvenir : le garçon dans la neige
        img.paste(TOWN_SNOW); smoke(img, tg); d = ImageDraw.Draw(img)
        shadow(d, hx, hy, 205); P(img, hx, hy, 205, "shy", winter=True)
        breath(img, JT["head"], tg, 1, 0.9)
        d = ImageDraw.Draw(img); snowfall(d, tg, 1.0)
        topsh(img); d = ImageDraw.Draw(img)
        TX(d, 290, "LE GARÇON", 110, WHITE, k)
        TX(d, 420, "QU'ON TROUVAIT TROP TIMIDE…", 64, ORANGE, kt)
        return dict(hit=0.0)
    img.paste(reveal(SNOW_ARR, AFR_ARR, head, eout(kl / 0.6) * 2300, edge=0.8 if kl < 0.6 else 0)); d = ImageDraw.Draw(img)
    rings(img, head, kl, 5, GOLD, 900, 14); d = ImageDraw.Draw(img)
    shadow(d, hx, hy, s, GSH); P(img, hx, hy, s, blend_pose(POSES["shy"], POSES["shout"], eout(kl / 0.25)), glow=1.5)
    d = ImageDraw.Draw(img); band_on_arm(d, s)
    crowd(d, tg, up_all=True, rise=eout(kl / 0.35))
    topsh(img, 0.9); d = ImageDraw.Draw(img)
    TX(d, 290, "LE GARÇON « TROP TIMIDE »", 68, ICE)
    TX(d, 430, "A FAIT LEVER", 124, GOLD, kl, amp=0.25, stroke=9)
    if kl < 0.25: hit = 1 - kl / 0.25
    if kp > 0: hit = max(hit, stamp(img, "TOUT UN PAYS", (W / 2, 610), 130, -4, kp, WHITE))
    return dict(hit=hit, flash=0.5 * max(0, 1 - kl / 0.25))

def s_you(img, d, tg, k):
    kr = kM(tg, "remarque"); kp = tg - K["arms_up"] + 0.1; hit = 0.0
    img.paste(TOWN_SNOW); smoke(img, tg)
    img.alpha_composite(OTHERS); d = ImageDraw.Draw(img)
    hx, s = 250, 262
    shadow(d, hx, FEET, s)
    P(img, hx, FEET, s, blend_pose(POSES["shy"], POSES["shout"], eout(max(0, kp) / 0.25)), winter=True, glow=1.2)
    head = JT["head"]
    if kp > 0: rings(img, head, kp, 5, GOLD, 800, 14)
    else: breath(img, head, tg, 1, 0.9)
    d = ImageDraw.Draw(img); snowfall(d, tg, 0.9)
    dim(img, 0.22); topsh(img); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(150 + 40 * (1 - eout(k / 0.2))), ORANGE, BOLD, stroke=8, scol=BG)
    TX(d, 470, "TU ATTENDS QU'ON TE REMARQUE…", 62, WHITE, kr + 0.3, maxw=920)
    if kp > 0:
        TX(d, 600, "OU TU TE FAIS ENTENDRE ?", 80, GOLD, kp, maxw=920, stroke=8)
        if kp < 0.25: hit = 1 - kp / 0.25
    return dict(hit=hit)

def s_abonne(img, d, tg, k):
    img.paste(TOWN_SNOW); d = ImageDraw.Draw(img); snowfall(d, tg, 0.8)
    dim(img, 0.62); d = ImageDraw.Draw(img)
    hit = 0.0
    P(img, 200, FEET + 20, 215, "point", winter=True, glow=1.2); d = ImageDraw.Draw(img)
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rounded_rectangle((W / 2 - bw / 2, 420 - bh / 2, W / 2 + bw / 2, 420 + bh / 2), int(40 * sc), fill=RED)
    text(d, (W / 2 - bw / 2 + 90 * sc, 420), "+", int(130 * sc), WHITE, BOLD)
    text(d, (W / 2 + 50 * sc, 420), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE, BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = kM(tg, "demain")
    if kd > 0:
        TX(d, 660, "DEMAIN · ÉPISODE 8", 74, GOLD, kd)
        text(d, (W / 2, 770), typew("ENCORE GARDIEN DE BUT À 14 ANS…", kd, 34), fit("ENCORE GARDIEN DE BUT À 14 ANS…", 58, 940), WHITE, BOLD, stroke=6, scol=BG)
    kr = kM(tg, "record")
    if kr > 0: hit = max(hit, stamp(img, "TRANSFERT RECORD", (W / 2 + 40, 980), 78, -5, kr, GOLD))
    return dict(hit=hit)

NUMS = [(np.random.default_rng(i).uniform(140, W - 140), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["8/10", "10/10", "6/10", "9/10", "7/10", "5/10", "10/10", "8/10", "9/10", "7/10"])]
def s_question(img, d, tg, k):
    img.paste(TOWN_SNOW); d = ImageDraw.Draw(img); snowfall(d, tg, 0.8)
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
    img.paste(TOWN_SNOW); dim(img, 0.9); d = ImageDraw.Draw(img)
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

SCENES = {"hook": s_hook, "intro": s_intro, "ville": s_ville, "metz": s_metz, "renvoi": s_renvoi, "retour": s_retour, "voix": s_voix,
          "pro": s_pro, "naples": s_naples, "afrique": s_afrique, "regard": s_regard, "you": s_you, "abonne": s_abonne, "question": s_question, "logo": s_logo}
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

# trajectoires du héros par scène (k = temps local de la scène). walk = il marche/court pendant le déplacement.
def PATH(typ, k, tg):
    st = SC[typ]
    if typ == "hook":     # arrive du fond, en diagonale, vers la caméra, puis s'arrête tête basse
        return _seg(k, [(0, 2.4, -120, 0), (1.3, 1.6, 160, 0), (2.6, 1.0, 0, 0)]) + (k < 2.6,)
    if typ == "intro":    # avance lentement vers nous
        return _seg(k, [(0, 1.0, 0, 0), (1.2, 1.0, 0, 0), (3.2, 0.84, 120, 0)]) + (1.2 < k < 3.2,)
    if typ == "ville":    # du fond gauche au premier plan (x de la scène + profondeur)
        return _seg(k, [(0, 2.4, 0, 0), (3.9, 0.95, 0, 0)]) + (False,)
    if typ == "metz":     # s'enfonce vers le portail du centre de formation
        return _seg(k, [(0, 0.95, 0, 0), (2.4, 1.55, -40, 0)]) + (False,)
    if typ == "renvoi":   # renvoyé : il revient vers la caméra, de 3/4
        a = MK_("introverti") - st
        return _seg(k, [(0, 1.5, -60, 0), (a, 1.5, -60, 0), (a + 2.6, 0.9, 160, 0)]) + (False,)
    if typ == "retour":
        return (1.0, 0.0, 0.0, 0.0, False)
    if typ == "voix":     # au cri : il bondit vers la caméra
        b = K["boom"] - st
        return _seg(k, [(0, 1.25, 0, 0), (b, 1.25, 0, 0), (b + 0.45, 0.86, 0, 0)]) + (False,)
    if typ == "pro":
        m = MK_("metz2") - st
        if k < m: return _seg(k, [(0, 1.9, -260, 0), (m, 0.9, 0, 0)]) + (False,)
        return _seg(k, [(m, 1.0, 0, 0), (m + 1.8, 1.45, 60, 0)]) + (False,)
    if typ == "naples":
        n = MK_("naples") - st; b = MK_("brassard2") - st
        if k < n: return _seg(k, [(0, 2.6, 0, 0), (1.3, 1.0, 0, 0)]) + (False,)
        if k < b:   # le mur : il se déplace latéralement ET en profondeur pour couper chaque ballon
            return (1.05 + 0.18 * math.sin((k - n) * 2.2), 90 * math.sin((k - n) * 3.1), 0.0, 0.0, False)
        return _seg(k, [(b, 1.12, 0, 0), (b + 0.8, 0.9, 0, 0)]) + (False,)
    if typ == "afrique":
        f = MK_("finale") - st; p = MK_("premier") - st
        if k < f: return _seg(k, [(0, 2.8, 0, 0), (2.6, 1.0, 0, 0)]) + (False,)
        if k < p: return (1.0, 0.0, 0.0, 0.0, False)
        return _seg(k, [(p, 1.15, 0, 0), (p + 0.9, 0.9, 0, 0)]) + (False,)
    if typ == "regard":
        l = MK_("lever") - st
        return _seg(k, [(0, 1.6, -200, 0), (l, 1.05, 0, 0), (l + 0.5, 0.92, 0, 0)]) + (0 < k < l - 0.1,)
    if typ == "you":      # quitte le groupe et vient vers nous
        return _seg(k, [(0, 1.0, 0, 0), (1.0, 1.0, 0, 0), (2.6, 0.82, 230, 0)]) + (1.0 < k < 2.6,)
    if typ == "abonne":
        return _seg(k, [(0, 1.6, 300, 0), (1.4, 1.0, 0, 0)]) + (k < 1.4,)
    return (1.0, 0.0, 0.0, 0.0, False)

# caméra par scène : zoom, décalage x/y (px), yaw (orbite), pitch (plongée -/contre-plongée +), roulis (degrés)
def CAMF(typ, k, tg):
    hh = (6 * math.sin(tg * 2.1), 5 * math.sin(tg * 1.7 + 1))       # caméra à l'épaule
    dur = 3.0
    for s_ in SCN:
        if s_["type"] == typ: dur = s_["end"] - s_["start"]
    u = ease(k / max(0.5, dur))
    if typ == "hook":    return (lerp(1.18, 1.08, u), lerp(80, -40, u) + hh[0], hh[1], lerp(0.06, -0.02, u), 0.0, lerp(-1.5, 0, u))
    if typ == "intro":   return (1.12, lerp(-60, 60, u) + hh[0], hh[1], lerp(-0.09, 0.09, u), 0.0, 0.0)            # orbite
    if typ == "ville":   return (lerp(1.06, 1.16, u), lerp(-80, 40, u), hh[1], -0.05, 0.0, 0.0)                     # travelling qui suit
    if typ == "metz":    return (lerp(1.06, 1.22, u), 0 + hh[0], lerp(0, -40, u), 0.0, 0.03, 0.0)                    # travelling avant vers le portail
    if typ == "renvoi":  return (lerp(1.2, 1.06, u), hh[0], hh[1], lerp(0.08, -0.06, u), 0.0, lerp(2, -1, u))
    if typ == "retour":  return (lerp(1.08, 1.22, u), lerp(-120, 80, u), lerp(-30, 30, u), lerp(-0.1, 0.06, u), -0.04, 0.0)  # grue lente autour de lui
    if typ == "voix":
        kb = max(0.0, tg - K["boom"])
        orb = math.sin(min(1, kb / 1.8) * math.pi) * 0.13
        return (1.08 + 0.18 * math.exp(-kb * 3) if kb > 0 else lerp(1.06, 1.14, u), hh[0] * 2, hh[1], orb if kb > 0 else -0.04, 0.05 if kb > 0 else 0.0, 3 * math.sin(kb * 4) * math.exp(-kb * 2))
    if typ == "pro":     return (lerp(1.08, 1.14, u), lerp(100, -100, u) + hh[0], hh[1], lerp(0.07, -0.07, u), 0.0, 0.0)
    if typ == "naples":
        b = tg - M("brassard2", 99)
        if b > 0: return (lerp(1.08, 1.2, ease(b / 1.5)), hh[0], lerp(0, 60, ease(b / 1.5)), 0.0, 0.08, 0.0)    # contre-plongée
        return (1.1, hh[0] + 60 * math.sin(k * 0.9), hh[1], 0.08 * math.sin(k * 0.7), 0.0, 0.0)
    if typ == "afrique":
        p = tg - M("premier", 99); f = tg - M("finale", 99)
        if p > 0: return (lerp(1.08, 1.2, ease(p / 2)), hh[0], lerp(0, 70, ease(p / 2)), 0.1 * math.sin(p * 1.2), 0.08, 0.0)
        if f > 0: return (lerp(1.06, 1.24, ease(f / 2.2)), lerp(0, -80, ease(f / 2.2)), lerp(0, 60, ease(f / 2.2)), 0.0, 0.0, 0.0)   # vers le but
        return (lerp(1.2, 1.08, u), lerp(-80, 40, u), hh[1], lerp(-0.08, 0.04, u), 0.0, 0.0)
    if typ == "regard":
        l = tg - M("lever", 99)
        if l > 0: return (lerp(1.18, 1.08, ease(l / 1.2)), hh[0], lerp(-50, 40, ease(l / 1.2)), 0.1 * math.sin(l * 1.5), 0.06, 0.0)
        return (lerp(1.06, 1.16, u), hh[0], hh[1], 0.0, -0.03, 0.0)
    if typ == "you":     return (lerp(1.06, 1.16, u), lerp(-60, 30, u) + hh[0], hh[1], lerp(0.06, -0.04, u), 0.0, 0.0)
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

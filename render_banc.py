# -*- coding: utf-8 -*-
"""Style « banc » : stade de nuit, BANC DE TOUCHE abrité, pluie froide pour l'Europe, flashback Casablanca, projecteurs qui s'allument au cri.
Personnage « athlète » GARDIEN (maillot violet sans numéro, gants blancs) : assis sur le banc, se lève, plonge pour arrêter les tirs.
Aucun nom propre, club, logo ni drapeau à l'écran. Types : hook intro casa france madrid banc heure pret seville mondial regard you abonne question logo
(09/11/2026 : Yassine Bounou, épisode 6). Usage : python3 render_banc.py timing_voix.json video_brut.mp4 [t_from t_to every]"""

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
        gc = globals().get('GLOVE'); gr = 0.065 if gc else 0.045
        d.ellipse((h[0] - gr * S, h[1] - gr * S, h[0] + gr * S, h[1] + gr * S), fill=gc or sk)
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





# =============================================================== style « banc » (09/11/2026, Yassine Bounou — épisode 6)
# Décor : stade la nuit (tribunes, pylônes de projecteurs, pelouse) avec un BANC DE TOUCHE abrité au premier plan ; passages « Europe »
# froids (pluie bleue) ; flashback Casablanca (maisons blanches au crépuscule) ; projecteurs qui s'allument au cri, nuit dorée de Coupe du monde.
# Personnage « athlète » GARDIEN (maillot violet sans numéro, gants blancs) : assis sur le banc, se lève, PLONGE pour arrêter des tirs.
# Aucun nom de club, logo, écusson, drapeau ni trophée réel à l'écran.
NIGHT = (6, 10, 26); SKY2 = (24, 26, 58)
ACC = (255, 150, 30); AMBER = (255, 190, 90); ICE = (140, 190, 255)
ORANGE = ACC
FEET = 1500; HOR = 820
JER = (118, 64, 196); GLOVE = (246, 246, 240)
LIGHT = (255, 244, 210)

POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-28, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))
POSES["fist"] = dict(t=-4, la=(-172, -6), ra=(25, -70), ll=(-14, 4), rl=(14, -4))
POSES["ready"] = dict(t=14, la=(-60, 40), ra=(60, -40), ll=(-22, 18), rl=(22, -18))
POSES["dive"] = dict(t=0, la=(-170, 4), ra=(170, -4), ll=(-6, 4), rl=(16, -10))
POSES["clap"] = dict(t=0, la=(-150, 30), ra=(150, -30), ll=(-6, 0), rl=(6, 0))

def P(img, x, y, s, pose, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER); kw.setdefault("shorts", (26, 26, 34)); kw.setdefault("sock", JER)
    player(img, x, y, s, pose, **kw)

def make_bg(lit):
    """stade de nuit : lit = 0 projecteurs éteints, 1 projecteurs allumés"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        d.line((0, y, W, y), fill=mix(mix(NIGHT, SKY2, u ** 1.3), mix((20, 30, 60), (60, 70, 110), u), lit * 0.6))
    rng = np.random.default_rng(3)
    for i in range(60):
        x, y = rng.uniform(0, W), rng.uniform(0, HOR * 0.45); r = rng.uniform(1, 2.4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((220, 220, 250), (60, 70, 110), lit * 0.8))
    # tribunes (gradins + public en points)
    top = 470
    d.polygon([(0, top + 120), (W, top), (W, HOR + 60), (0, HOR + 60)], fill=mix((14, 16, 30), (40, 44, 70), lit))
    for r in range(12):
        yy = top + 40 + r * 30
        d.line((0, yy + 120 * (1 - 0) - r * 0, W, yy), fill=mix((22, 24, 42), (60, 64, 94), lit), width=3)
    for i in range(520):
        x = rng.uniform(0, W); y = rng.uniform(top + 30 + 120 * (1 - x / W), HOR + 50)
        c = [(200, 60, 60), (230, 230, 230), (60, 120, 220), (240, 200, 60)][i % 4]
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=mix((26, 28, 46), c, 0.15 + 0.55 * lit))
    # pylônes de projecteurs
    for px in (120, 960):
        d.rectangle((px - 8, 150, px + 8, top + 60), fill=mix((30, 32, 46), (90, 92, 110), lit))
        for j in range(3):
            for i in range(4):
                cx, cy = px - 60 + i * 40, 120 + j * 34
                d.rectangle((cx - 16, cy - 12, cx + 16, cy + 12), fill=mix((40, 42, 56), LIGHT, lit))
    if lit > 0:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        for px in (120, 960):
            dl.ellipse((px - 200, 30, px + 200, 300), fill=LIGHT + (int(150 * lit),))
            dl.polygon([(px - 80, 150), (px + 80, 150), (W / 2 + (px - W / 2) * 0.2 + 400, FEET), (W / 2 + (px - W / 2) * 0.2 - 400, FEET)], fill=LIGHT + (int(40 * lit),))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(40))); d = ImageDraw.Draw(img)
    # pelouse rayée
    for y in range(HOR + 60, H):
        u = (y - HOR - 60) / (H - HOR - 60)
        band = (int((y - HOR) ** 0.8 / 22) % 2)
        base = mix((10, 34, 22), (34, 110, 60), lit)
        d.line((0, y, W, y), fill=mix(mix(base, (0, 0, 0), 0.12 * band), (4, 10, 8), 0.5 * u))
    d.line((0, HOR + 140, W, HOR + 110), fill=mix((60, 80, 70), (230, 240, 230), lit), width=5)
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

def cold(img, tg, a=1.0):
    """passage « Europe » : teinte froide + pluie"""
    img.alpha_composite(Image.new("RGBA", (W, H), (30, 60, 110, int(120 * a))))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(4)
    for i in range(130):
        x0, y0, sp = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 1.2)
        y = (y0 + tg * 1100 * sp) % H; x = (x0 - (tg * 140 * sp)) % W
        d.line((x, y, x - 12, y + 40), fill=mix((40, 60, 90), (170, 190, 220), a * 0.7), width=2)

DUST = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.3, 1.0)) for i in range(70)]
def dust(d, tg, amt=1.0):
    for x0, y0, z in DUST[:int(len(DUST) * amt)]:
        y = (y0 - tg * 40 * z) % H; x = x0 + 20 * math.sin(tg * 0.8 + x0)
        r = 1.5 + 2.5 * z; d.ellipse((x - r, y - r, x + r, y + r), fill=mix((60, 50, 70), (255, 230, 170), z * 0.7))

def bench(d, cx, by, s=1.0, roof=True):
    """banc de touche abrité (générique)"""
    w = 760 * s
    if roof:
        d.polygon([(cx - w / 2 - 30 * s, by - 520 * s), (cx + w / 2 + 30 * s, by - 520 * s), (cx + w / 2 + 10 * s, by - 470 * s), (cx - w / 2 - 10 * s, by - 470 * s)], fill=(70, 80, 96))
        for x in (cx - w / 2, cx + w / 2): d.rectangle((x - 10 * s, by - 480 * s, x + 10 * s, by), fill=(60, 66, 80))
        L = (cx - w / 2 + 10 * s, by - 470 * s, cx + w / 2 - 10 * s, by - 250 * s)
        d.rectangle(L, fill=(40, 60, 80), outline=(120, 150, 170), width=max(2, int(4 * s)))
    d.rectangle((cx - w / 2 + 20 * s, by - 230 * s, cx + w / 2 - 20 * s, by - 190 * s), fill=(150, 40, 50))      # dossier
    d.rectangle((cx - w / 2 + 20 * s, by - 150 * s, cx + w / 2 - 20 * s, by - 115 * s), fill=(180, 52, 60))      # assise
    for x in (cx - w / 2 + 50 * s, cx, cx + w / 2 - 50 * s): d.rectangle((x - 8 * s, by - 115 * s, x + 8 * s, by), fill=(40, 40, 48))

def goal(d, cx, by, s=1.0, col=(240, 240, 240)):
    w, h = 820 * s, 330 * s
    for i in range(0, 15):
        x = cx - w / 2 + i * w / 14; d.line((x, by - h, x + (x - cx) * 0.08, by - 40 * s), fill=mix(col, BG, 0.65), width=2)
    for j in range(0, 7):
        y = by - h + j * h / 7; d.line((cx - w / 2, y, cx + w / 2, y), fill=mix(col, BG, 0.65), width=2)
    d.rectangle((cx - w / 2 - 12 * s, by - h - 12 * s, cx + w / 2 + 12 * s, by - h), fill=col)
    d.rectangle((cx - w / 2 - 12 * s, by - h, cx - w / 2, by), fill=col); d.rectangle((cx + w / 2, by - h, cx + w / 2 + 12 * s, by), fill=col)

def gloves(d, x, y, s=1.0, k=1.0):
    for dx in (-60, 60):
        cx = x + dx * s
        d.rounded_rectangle((cx - 44 * s, y - 20 * s, cx + 44 * s, y + 90 * s), int(20 * s), fill=GLOVE)
        for i in range(4): d.rounded_rectangle((cx - 40 * s + i * 21 * s, y - 80 * s + abs(i - 1.5) * 8 * s, cx - 22 * s + i * 21 * s, y), int(9 * s), fill=GLOVE)
        d.rectangle((cx - 46 * s, y + 70 * s, cx + 46 * s, y + 100 * s), fill=JER)

def xmark(d, cx, cy, r, col=RED, w=22):
    d.line((cx - r, cy - r, cx + r, cy + r), fill=col, width=w); d.line((cx - r, cy + r, cx + r, cy - r), fill=col, width=w)

def plane(d, x, y, s=1.0, flip=False, col=(235, 235, 240)):
    f = -1 if flip else 1
    q = lambda px, py: (x + f * px * s, y + py * s)
    d.polygon([q(-150, -10), q(130, -14), q(170, 0), q(130, 14), q(-150, 10)], fill=col)
    d.polygon([q(-20, 0), q(40, 0), q(-40, 90), q(-75, 90)], fill=mix(col, (0, 0, 0), 0.15))
    d.polygon([q(-20, 0), q(40, 0), q(-40, -90), q(-75, -90)], fill=mix(col, (0, 0, 0), 0.05))
    d.polygon([q(-150, -8), q(-120, -8), q(-150, -60), q(-170, -60)], fill=col)

def paper(d, cx, cy, s, ang, k):
    """feuille administrative avec tampon"""
    L = Image.new("RGBA", (int(260 * s), int(340 * s)), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.rectangle((0, 0, L.width - 1, L.height - 1), fill=(236, 230, 214, 255), outline=(150, 140, 120, 255), width=3)
    for i in range(7): dl.line((24 * s, (50 + i * 34) * s, (230 - (i % 3) * 30) * s, (50 + i * 34) * s), fill=(160, 150, 130, 255), width=max(2, int(5 * s)))
    return L.rotate(ang, resample=Image.BICUBIC, expand=True)

def trophy(d, cx, cy, s=1.0, col=GOLD):
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.polygon([q(-120, -230), q(120, -230), q(80, -60), q(25, -20), q(25, 50), q(80, 90), q(-80, 90), q(-25, 50), q(-25, -20), q(-80, -60)], fill=col)
    d.arc((cx - 190 * s, cy - 230 * s, cx - 70 * s, cy - 90 * s), 90, 270, fill=col, width=int(14 * s))
    d.arc((cx + 70 * s, cy - 230 * s, cx + 190 * s, cy - 90 * s), 270, 90, fill=col, width=int(14 * s))

def clock(d, cx, cy, r, k, lit=0.0):
    d.ellipse((cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14), fill=mix((40, 40, 50), GOLD, lit))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix((230, 226, 210), (255, 248, 220), lit))
    for i in range(12):
        a = i * math.pi / 6
        d.line((cx + 0.82 * r * math.sin(a), cy - 0.82 * r * math.cos(a), cx + 0.94 * r * math.sin(a), cy - 0.94 * r * math.cos(a)), fill=BG, width=8)
    am = -math.pi / 2 * (1 - eout(min(1, k / 0.5))) + k * 0.0   # aiguille des minutes -> 12
    ah = math.pi * 1.6 * (1 - eout(min(1, k / 0.5)))
    d.line((cx, cy, cx + 0.8 * r * math.sin(am), cy - 0.8 * r * math.cos(am)), fill=RED, width=12)
    d.line((cx, cy, cx + 0.5 * r * math.sin(ah), cy - 0.5 * r * math.cos(ah)), fill=BG, width=16)
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=BG)

def cone(img, x, a=1.0, col=(255, 236, 190)):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(x - 40, 0), (x + 40, 0), (x + 300, FEET + 60), (x - 300, FEET + 60)], fill=col + (int(110 * a),))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(24)))

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def confetti(d, kv):
    for x0, y0, c in CONF:
        y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[JER, WHITE, GOLD][c])

def crowd(d, tg, lit=1.0, n=14):
    for i in range(n):
        x = 40 + i * (W - 80) / (n - 1); h = 200 + 50 * ((i * 37) % 5) / 4
        up = math.sin(tg * 5 + i) > 0
        c = mix((14, 12, 20), (60, 40, 40), 0.3 * lit)
        y0 = H - 40
        d.rounded_rectangle((x - 34, y0 - h, x + 34, y0), 26, fill=c); d.ellipse((x - 26, y0 - h - 58, x + 26, y0 - h - 6), fill=c)
        if up: d.line((x + 24, y0 - h + 20, x + 50, y0 - h - 110), fill=c, width=16)

def series_banner(d, tg):
    """titre de la série dès 0,6 s (jusqu'à 3,4 s) : « ILS ONT FAILLI ABANDONNER — ÉPISODE 6 » (l'accroche passe d'abord)"""
    if tg > 3.6 or tg < 0.5: return
    a = min(1, (tg - 0.5) / 0.15) * (1 - ease((tg - 3.2) / 0.4))
    c = mix(BG, WHITE, a); g = mix(BG, GOLD, a)
    d.rounded_rectangle((90, 70, W - 90, 200), 22, fill=mix(BG, (50, 30, 80), a), outline=g, width=4)
    text(d, (W / 2, 115), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), c, BOLD)
    text(d, (W / 2, 168), "ÉPISODE 6", 40, g, MONO)

def kM(tg, name): return tg - M(name, 99) + 0.1
def pop(k, base, amp=0.3, dur=0.2): return int(base * (1 + amp * (1 - eout(max(0, k) / dur))))

def dive(img, d, x0, x1, by, s, u, side=1):
    """plongeon : u 0 -> 1 ; side = 1 vers la droite"""
    u = min(1, max(0, u))
    x = lerp(x0, x1, eout(u)); y = by - 260 * math.sin(math.pi * min(1, u * 1.1)) * 0.8
    rot = -side * 80 * eout(min(1, u * 1.6))
    P(img, x, y, s, "dive" if u > 0.05 else "ready", rot=rot, glow=1.2)

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    bench(d, W / 2, FEET + 30, 1.0)
    P(img, W / 2 - 40, FEET - 40, 260, "sad")
    for i, bx in enumerate((W / 2 - 300, W / 2 + 260)):
        c = (16, 16, 24)
        d.rounded_rectangle((bx - 40, FEET - 330, bx + 40, FEET - 140), 26, fill=c); d.ellipse((bx - 32, FEET - 400, bx + 32, FEET - 336), fill=c)
    cold(img, tg, 0.6); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    sc = 1 + 0.3 * (1 - eout((tg + 0.1) / 0.2))
    text(d, (W / 2, 420), "TOUJOURS", int(fit("TOUJOURS", 140, 1000) * sc), WHITE, BOLD, stroke=9, scol=BG)
    kk = tg - K["hook"] + 0.15
    if kk > 0:
        text(d, (W / 2, 590), "SUR LE BANC ?", pop(kk, fit("SUR LE BANC ?", 170, 1000), 0.5, 0.18), RED, BOLD, stroke=10, scol=BG)
        hit = max(0, 1 - kk / 0.25)
    kd = kM(tg, "jouer")
    if kd > 0: text(d, (W / 2, 770), "ON NE TE FAIT JAMAIS JOUER ?", fit("ON NE TE FAIT JAMAIS JOUER ?", 66, 980), GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit, bg=0.0)

def s_intro(img, d, tg, k):
    hit = 0.0
    label(d, 300, "L'HISTOIRE VRAIE", k, 100, WHITE, "D'UN GARDIEN DE BUT", ACC)
    ks = kM(tg, "sommet")
    if ks > 0:
        text(d, (W / 2, 560), "DU BANC", fit("DU BANC", 120, 980), WHITE, BOLD, stroke=7, scol=BG)
        text(d, (W / 2, 700), "AU SOMMET", pop(ks, fit("AU SOMMET", 140, 980)), GOLD, BOLD, stroke=8, scol=BG)
        if ks < 0.25: hit = 1 - ks / 0.25
    # il enfile ses gants (gros plan)
    gloves(d, W / 2, 1000 + 10 * math.sin(tg * 3), 1.3)
    P(img, W / 2, FEET + 40, 230, "clap" if (k % 1.2) < 0.3 else "ready"); shadow(d, W / 2, FEET + 40, 230)
    return dict(hit=hit, bg=0.15)

def casa_bg(d, tg):
    """flashback Casablanca : maisons blanches cubiques au crépuscule"""
    for y in range(0, 1250):
        u = y / 1250
        d.line((0, y, W, y), fill=mix((40, 30, 80), (250, 150, 90), u ** 1.3))
    d.ellipse((W / 2 - 110, 820, W / 2 + 110, 1040), fill=(255, 210, 140))
    for i, (x, w, h) in enumerate([(-20, 220, 300), (180, 180, 380), (340, 240, 260), (560, 200, 420), (740, 200, 300), (920, 200, 360)]):
        base = 1250
        d.rectangle((x, base - h, x + w, base), fill=mix((236, 230, 220), (200, 170, 160), 0.25 * (i % 2)))
        d.rectangle((x - 6, base - h - 14, x + w + 6, base - h), fill=(210, 200, 190))
        for fx in range(int(x + 26), int(x + w - 40), 70):
            for fy in range(int(base - h + 40), int(base - 80), 90):
                d.rounded_rectangle((fx, fy, fx + 34, fy + 50), 14, fill=(40, 70, 110) if (fx + fy) % 3 else (255, 200, 110))
    for y in range(1250, H):
        d.line((0, y, W, y), fill=mix((150, 120, 100), (60, 46, 40), (y - 1250) / (H - 1250)))

def s_casa(img, d, tg, k):
    hit = 0.0
    casa_bg(d, tg)
    kc = kM(tg, "casablanca"); km = kM(tg, "maroc")
    text(d, (W / 2, 300), "IL GRANDIT À", fit("IL GRANDIT À", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
    if kc > 0:
        hit = max(hit, stamp(img, "CASABLANCA", (W / 2, 450), 130, -4, kc, ACC)); d = ImageDraw.Draw(img)
    if km > 0: text(d, (W / 2, 610), "AU MAROC", pop(km, fit("AU MAROC", 100, 980)), GOLD, BOLD, stroke=7, scol=BG)
    # gamin gardien dans la rue : deux pierres pour poteaux, il capte la balle
    for px in (W / 2 - 260, W / 2 + 260): d.ellipse((px - 30, FEET - 20, px + 30, FEET + 16), fill=(120, 110, 100))
    ph = (k % 1.6) / 1.6
    bx = lerp(W + 80, W / 2 + 20, min(1, ph / 0.5)); by = lerp(FEET - 500, FEET - 330, min(1, ph / 0.5))
    P(img, W / 2, FEET, 210, "ready" if ph < 0.42 else "up"); shadow(d, W / 2, FEET, 210)
    ball(d, bx if ph < 0.5 else W / 2, by if ph < 0.5 else FEET - 470, 30, WHITE, tg * 6)
    return dict(hit=hit, bg=0.3)

def s_france(img, d, tg, k):
    hit = 0.0
    kr = kM(tg, "recrute"); kp = kM(tg, "papiers"); kt = kM(tg, "retour")
    cold(img, tg, 0.4); d = ImageDraw.Draw(img)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    badge(d, 200, 300, "17 ANS", k, GOLD, 110)
    if kr > 0 and kt <= 0:
        text(d, (640, 300), "UN CLUB FRANÇAIS", fit("UN CLUB FRANÇAIS", 66, 620), WHITE, BOLD, stroke=5, scol=BG)
        text(d, (640, 380), "LE RECRUTE", pop(kr, fit("LE RECRUTE", 74, 620)), GOLD, BOLD, stroke=5, scol=BG)
        u = min(1, kr / 1.2); plane(d, lerp(-300, W + 300, u), 600 - 160 * u, 1.0)
    if kp > 0 and kt <= 0:
        for i in range(6):
            L = paper(d, 0, 0, 0.8, (i * 37) % 40 - 20, kp)
            x = 140 + (i * 173) % 800; y = 560 + ((i * 97) % 300) + kp * 60 * (1 + i % 2)
            img.alpha_composite(L, (int(x), int(y)))
        d = ImageDraw.Draw(img)
        hit = max(hit, stamp(img, "PROBLÈMES DE PAPIERS", (W / 2, 640), 100, -6, kp, RED)); d = ImageDraw.Draw(img)
        text(d, (W / 2, 800), "IL NE PEUT PAS JOUER", fit("IL NE PEUT PAS JOUER", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
    if kt > 0:
        u = eout(min(1, kt / 1.2))
        plane(d, lerp(W + 200, -300, u), 520 - 100 * u, 1.1, flip=True)
        text(d, (W / 2, 330), "RETOUR AU PAYS", pop(kt, fit("RETOUR AU PAYS", 100, 980)), GREY, BOLD, stroke=6, scol=BG)
        if kt < 0.25: hit = max(hit, 1 - kt / 0.25)
    P(img, W / 2, FEET, 230, "sad" if kt > 0 else "stand"); shadow(d, W / 2, FEET, 230)
    return dict(hit=hit, bg=0.0)

def s_madrid(img, d, tg, k):
    hit = 0.0
    kmd = kM(tg, "madrid"); kg = kM(tg, "gardien2"); kr = kM(tg, "reserve"); kz = kM(tg, "zero")
    badge(d, 200, 300, "21 ANS", k, GOLD, 110)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    if kmd > 0:
        text(d, (640, 300), "UN GRAND CLUB", fit("UN GRAND CLUB", 70, 620), WHITE, BOLD, stroke=5, scol=BG)
        text(d, (640, 380), "ESPAGNOL", pop(kmd, fit("ESPAGNOL", 80, 620)), GOLD, BOLD, stroke=5, scol=BG)
    if kg > 0 and kz <= 0:
        # trois maillots de gardien : il est le 3e
        for i in range(3):
            x = 220 + i * 320; y = 640
            col = JER if i == 2 else (90, 96, 110)
            d.polygon([(x - 90, y - 100), (x - 40, y - 130), (x + 40, y - 130), (x + 90, y - 100), (x + 70, y - 40), (x + 50, y - 50), (x + 50, y + 120), (x - 50, y + 120), (x - 50, y - 50), (x - 70, y - 40)], fill=col)
            text(d, (x, y + 10), str(i + 1), 90, WHITE if i == 2 else (150, 156, 170), BOLD)
        hit = max(hit, stamp(img, "3e GARDIEN", (W / 2, 880), 120, -5, kg, RED)); d = ImageDraw.Draw(img)
        if kr > 0: text(d, (W / 2, 1040), "RÉSERVE · 3e DIVISION", pop(kr, fit("RÉSERVE · 3e DIVISION", 76, 980)), ICE, BOLD, stroke=6, scol=BG)
    if kz > 0:
        text(d, (W / 2, 560), "MATCHS DE CHAMPIONNAT", fit("MATCHS DE CHAMPIONNAT", 70, 980), WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 820), "0", pop(kz, 380, 0.4), RED, BOLD, stroke=12, scol=BG)
        if kz < 0.25: hit = max(hit, 1 - kz / 0.25)
    bench(d, W / 2, FEET + 40, 0.75, roof=False)
    P(img, W / 2 + 120, FEET - 15, 200, "sit")
    cold(img, tg, 0.9)
    return dict(hit=hit, bg=0.25)

def s_banc(img, d, tg, k):
    hit = 0.0
    kb = tg - K["build_start"] + 0.1; ki = kM(tg, "nimporte"); kg = kM(tg, "gants")
    bench(d, W / 2, FEET + 30, 1.0)
    P(img, W / 2 - 40, FEET - 40, 260, "sad")
    gloves(d, W / 2 + 230, FEET - 30, 0.6) if kg > 0 else gloves(d, W / 2 - 40, FEET - 300, 0.55)
    cold(img, tg, 1.0); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "2 ANS", pop(kb, fit("2 ANS", 160, 980)), RED, BOLD, stroke=8, scol=BG)
    text(d, (W / 2, 450), "SUR LE BANC", fit("SUR LE BANC", 110, 980), WHITE, BOLD, stroke=7, scol=BG)
    if kb < 0.25: hit = 1 - max(0, kb) / 0.25
    if ki > 0: text(d, (W / 2, 600), typew("N'IMPORTE QUI AURAIT", ki, 26), fit("N'IMPORTE QUI AURAIT", 72, 980), GREY, BOLD, stroke=5, scol=BG)
    if kg > -0.5: text(d, (W / 2, 690), typew("ENLEVÉ SES GANTS…", kg + 0.5, 26), fit("ENLEVÉ SES GANTS…", 82, 980), WHITE, BOLD, stroke=6, scol=BG)
    return dict(hit=hit, bg=0.0)

def s_heure(img, d, tg, k):
    kb = tg - K["boom"]
    flash = 0.0
    kk = max(0.0, kb + 0.06)
    lit = eout(min(1, kk / 0.4))
    for i in range(5):
        if kk > i * 0.05: cone(img, 120 + i * 210, 1.0)
    d = ImageDraw.Draw(img)
    if kk < 0.4: flash = max(0, 0.95 - kk * 2.4)
    clock(d, W / 2, 760, 200, kk, lit)
    burst(d, W / 2, 760, kk, 24, 460, GOLD, 3, 9)
    # il se lève du banc d'un bond, poings levés
    u = eout(min(1, kk / 0.3))
    bench(d, W / 2, FEET + 60, 0.9, roof=False)
    P(img, W / 2 - 20, lerp(FEET - 70, FEET - 20, u), 280, "fist" if u > 0.4 else "sit", glow=1.6)
    hit = max(0, 1 - kk / 0.3)
    e = eout(kk / 0.22)
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, e)
    for off, c in ((10, (255, 60, 80)), (-10, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        text(d, (x1 + o, 300), "SON HEURE", fit("SON HEURE", 150, 1000), c, BOLD, stroke=8 if c == WHITE else 0, scol=BG)
        text(d, (x2 - o, 460), "VA ARRIVER !", fit("VA ARRIVER !", 150, 1000), c if c != WHITE else GOLD, BOLD, stroke=9 if c == WHITE else 0, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=0.2 + 0.6 * lit)

def s_pret(img, d, tg, k):
    hit = 0.0
    ks = kM(tg, "saragosse"); kg = kM(tg, "gerone"); km = kM(tg, "monter"); kt = kM(tg, "titulaire")
    if kg <= 0:
        label(d, 300, "PRÊTÉ", k, 130, WHITE, "EN 2e DIVISION", ACC)
        if 0 < k < 0.25: hit = 1 - k / 0.25
        # entraînement sous la pluie : il plonge encore et encore
        ph = (k % 1.3) / 1.3
        dive(img, d, W / 2 - 60, W / 2 + 260, FEET, 220, ph * 1.4, 1)
        ball(d, lerp(-60, W / 2 + 340, min(1, ph * 1.6)), FEET - 260 - 80 * math.sin(math.pi * min(1, ph * 1.6)), 30, WHITE, tg * 8)
        cold(img, tg, 0.7)
        return dict(hit=hit, bg=0.35)
    # Gérone : flèche de montée + TITULAIRE
    text(d, (W / 2, 290), "PUIS UN AUTRE CLUB", fit("PUIS UN AUTRE CLUB", 76, 980), WHITE, BOLD, stroke=6, scol=BG)
    if km > 0:
        u = eout(min(1, km / 0.6))
        d.polygon([(W / 2 - 70, 900), (W / 2 + 70, 900), (W / 2 + 70, 900 - 280 * u), (W / 2 + 160, 900 - 280 * u), (W / 2, 900 - 280 * u - 170), (W / 2 - 160, 900 - 280 * u), (W / 2 - 70, 900 - 280 * u)], fill=GREEN)
        text(d, (W / 2, 420), "MONTÉE !", pop(km, fit("MONTÉE !", 120, 980)), GREEN, BOLD, stroke=7, scol=BG)
        if km < 0.25: hit = max(hit, 1 - km / 0.25)
    if kt > 0:
        hit = max(hit, stamp(img, "TITULAIRE", (W / 2, 1040), 170, -6, kt, GOLD)); d = ImageDraw.Draw(img)
        text(d, (W / 2, 1200), "EN 1re DIVISION", fit("EN 1re DIVISION", 70, 980), WHITE, BOLD, stroke=6, scol=BG)
    P(img, W / 2 + 300, FEET, 220, "fist" if kt > 0 else "ready"); shadow(d, W / 2 + 300, FEET, 220)
    return dict(hit=hit, bg=0.6)

def s_seville(img, d, tg, k):
    hit = 0.0; flash = 0.0
    kr = kM(tg, "remplacant"); ke = kM(tg, "europe"); kl = kM(tg, "lui"); kp = kM(tg, "penalty"); kg = kM(tg, "gagne")
    if kg > 0:
        trophy(d, W / 2, 820, 1.1 * (1 + 0.2 * (1 - eout(kg / 0.25))), GOLD)
        text(d, (W / 2, 330), "IL GAGNE", fit("IL GAGNE", 120, 980), WHITE, BOLD, stroke=7, scol=BG)
        text(d, (W / 2, 460), "LA COUPE !", pop(kg, fit("LA COUPE !", 140, 980)), GOLD, BOLD, stroke=8, scol=BG)
        confetti(d, kg)
        P(img, W / 2, FEET + 60, 220, "up"); shadow(d, W / 2, FEET + 60, 220)
        if kg < 0.3: hit = 1 - kg / 0.3; flash = 0.3 * max(0, 1 - kg / 0.3)
        return dict(hit=hit, flash=flash, bg=1.0)
    if ke <= 0:
        bench(d, W / 2, FEET + 30, 0.9)
        P(img, W / 2, FEET - 30, 240, "sit")
        text(d, (W / 2, 300), "ENCORE", fit("ENCORE", 110, 980), WHITE, BOLD, stroke=7, scol=BG)
        if kr > 0: text(d, (W / 2, 440), "REMPLAÇANT", pop(kr, fit("REMPLAÇANT", 130, 980)), RED, BOLD, stroke=8, scol=BG)
        text(d, (W / 2, 570), "EN CHAMPIONNAT", fit("EN CHAMPIONNAT", 70, 980), GREY, BOLD, stroke=5, scol=BG)
        if 0 < kr < 0.25: hit = 1 - kr / 0.25
        return dict(hit=hit, bg=0.5)
    text(d, (W / 2, 290), "EN COUPE D'EUROPE", pop(ke, fit("EN COUPE D'EUROPE", 92, 980)), WHITE, BOLD, stroke=6, scol=BG)
    if kl > 0: text(d, (W / 2, 420), "C'EST LUI", pop(kl, fit("C'EST LUI", 130, 980)), GOLD, BOLD, stroke=8, scol=BG)
    goal(d, W / 2, FEET + 20, 1.05)
    if kp > 0:
        u = kp / 0.55
        dive(img, d, W / 2, W / 2 + 280, FEET, 230, u, 1)
        bt = min(1, kp / 0.5)
        if kp < 0.55: ball(d, lerp(W / 2 - 60, W / 2 + 330, bt), lerp(H - 120, FEET - 300, bt), 32, WHITE, tg * 10)
        else: ball(d, W / 2 + 470 + (kp - 0.55) * 300, FEET - 300 + (kp - 0.55) * 200, 32, WHITE, tg * 10)
        hit = max(hit, stamp(img, "ARRÊTÉ !", (W / 2, 640), 150, -6, kp - 0.45, GOLD))
    else:
        P(img, W / 2, FEET, 230, "ready"); ball(d, W / 2, H - 120, 34, WHITE, 0)
    if 0 < ke < 0.25: hit = max(hit, 1 - ke / 0.25)
    return dict(hit=hit, bg=0.8)

def s_mondial(img, d, tg, k):
    hit = 0.0; flash = 0.0
    kes = kM(tg, "espagne"); kt = kM(tg, "tirs"); k2 = kM(tg, "deux"); ka = kM(tg, "afrique"); kd = kM(tg, "demi")
    if ka > 0:
        crowd(d, tg, 1.0); confetti(d, ka)
        text(d, (W / 2, 300), "1re ÉQUIPE", pop(ka, fit("1re ÉQUIPE", 130, 980)), WHITE, BOLD, stroke=8, scol=BG)
        text(d, (W / 2, 440), "AFRICAINE", fit("AFRICAINE", 140, 980), GOLD, BOLD, stroke=8, scol=BG)
        if kd > 0: hit = max(hit, stamp(img, "EN DEMI-FINALE", (W / 2, 640), 120, -5, kd, ACC)); d = ImageDraw.Draw(img)
        P(img, W / 2, FEET - 120, 260, "up", glow=1.5)
        if ka < 0.25: hit = max(hit, 1 - ka / 0.25)
        return dict(hit=hit, bg=1.0)
    text(d, (W / 2, 290), "COUPE DU MONDE", pop(k, fit("COUPE DU MONDE", 110, 980)), GOLD, BOLD, stroke=7, scol=BG)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    if kes > 0: text(d, (W / 2, 410), "CONTRE L'ESPAGNE", pop(kes, fit("CONTRE L'ESPAGNE", 90, 980)), WHITE, BOLD, stroke=6, scol=BG)
    goal(d, W / 2, FEET + 20, 1.05)
    if kt > 0:
        # deux tirs au but arrêtés : un plongeon à droite, puis à gauche
        t2 = M("deux", 99) - M("tirs", 0)
        u1 = kt / 0.55; u2 = (k2 + 0.2) / 0.55
        if k2 + 0.2 <= 0: dive(img, d, W / 2, W / 2 + 280, FEET, 230, u1, 1)
        else: dive(img, d, W / 2, W / 2 - 280, FEET, 230, u2, -1)
        n = (1 if kt > 0.45 else 0) + (1 if k2 + 0.2 > 0.45 else 0)
        for i in range(2):
            x = W / 2 - 160 + i * 320
            d.ellipse((x - 70, 560, x + 70, 700), outline=WHITE, width=8)
            if i < n: xmark(d, x, 630, 50, RED, 18)
        text(d, (W / 2, 790), "TIRS AU BUT", fit("TIRS AU BUT", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
    else:
        P(img, W / 2, FEET, 230, "ready")
    if k2 > 0:
        hit = max(hit, stamp(img, "IL EN ARRÊTE 2 !", (W / 2, 960), 120, -6, k2, GOLD))
        flash = 0.35 * max(0, 1 - k2 / 0.3)
    return dict(hit=hit, flash=flash, bg=0.95)

def s_regard(img, d, tg, k):
    hit = 0.0
    kb = kM(tg, "banc4"); ka = kM(tg, "arrete"); kp = kM(tg, "pays")
    text(d, (W / 2, 290), "LE GARDIEN", fit("LE GARDIEN", 110, 980), WHITE, BOLD, stroke=6, scol=BG)
    if kb > 0: text(d, (W / 2, 420), "QU'ON LAISSAIT SUR LE BANC…", fit("QU'ON LAISSAIT SUR LE BANC…", 70, 980), GREY if ka > 0 else RED, BOLD, stroke=6, scol=BG)
    if ka > 0:
        text(d, (W / 2, 580), "A ARRÊTÉ", pop(ka, fit("A ARRÊTÉ", 130, 980)), GOLD, BOLD, stroke=8, scol=BG)
        if ka < 0.25: hit = 1 - ka / 0.25
    if kp > 0:
        hit = max(hit, stamp(img, "TOUT UN PAYS", (W / 2, 750), 130, -4, kp, WHITE)); d = ImageDraw.Draw(img)
        crowd(d, tg, 1.0)
    bench(d, W / 2 - 330, FEET + 40, 0.5, roof=False)
    P(img, W / 2 + 60, FEET - 60, 250, "up" if ka > 0 else "stand", glow=1.3)
    return dict(hit=hit, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ACC, BOLD, stroke=6, scol=BG)
    kh = kM(tg, "heure2"); kp = tg - K["arms_up"] + 0.1
    hit = 0.0
    clock(d, W / 2, 760, 170, 1.0, 0.3)
    if kh > 0: text(d, (W / 2, 1020), "TU ATTENDS TON HEURE…", pop(kh, fit("TU ATTENDS TON HEURE…", 76, 980)), GREY, BOLD, stroke=6, scol=BG)
    if kp > 0:
        text(d, (W / 2, 1130), "OU TU LA PRÉPARES ?", pop(kp, fit("OU TU LA PRÉPARES ?", 90, 980)), GOLD, BOLD, stroke=7, scol=BG)
        if kp < 0.25: hit = 1 - kp / 0.25
    return dict(hit=hit, bg=0.2)

def s_abonne(img, d, tg, k):
    dim(img, 0.6); d = ImageDraw.Draw(img)
    hit = 0.0
    sc = 1 + 0.35 * (1 - eout(k / 0.2)) + 0.03 * math.sin(tg * 8)
    bw, bh = 640 * sc, 170 * sc
    d.rounded_rectangle((W / 2 - bw / 2, 420 - bh / 2, W / 2 + bw / 2, 420 + bh / 2), int(40 * sc), fill=RED)
    text(d, (W / 2 - bw / 2 + 90 * sc, 420), "+", int(130 * sc), WHITE, BOLD)
    text(d, (W / 2 + 50 * sc, 420), "ABONNE-TOI", fit("ABONNE-TOI", int(96 * sc), bw - 200 * sc), WHITE, BOLD)
    if k < 0.25: hit = 1 - k / 0.25
    kd = kM(tg, "demain")
    if kd > 0:
        text(d, (W / 2, 660), "DEMAIN · ÉPISODE 7", fit("DEMAIN · ÉPISODE 7", 74, 980), GOLD, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 770), typew("LE DÉFENSEUR RENVOYÉ À 15 ANS", kd, 34), fit("LE DÉFENSEUR RENVOYÉ À 15 ANS", 58, 980), WHITE, BOLD, stroke=5, scol=BG)
    kt = kM(tg, "timide")
    if kt > 0: hit = max(hit, stamp(img, "« TROP TIMIDE »", (W / 2, 920), 110, -6, kt, RED)); d = ImageDraw.Draw(img)
    kc = kM(tg, "capitaine")
    if kc > 0:
        text(d, (W / 2, 1090), "… DEVENU CAPITAINE", pop(kc, fit("… DEVENU CAPITAINE", 76, 980)), GOLD, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 1180), "DE SON PAYS", fit("DE SON PAYS", 70, 980), WHITE, BOLD, stroke=6, scol=BG)
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
        text(d, (x, yy), s, 56, mix(BG, (140, 100, 40), a), BOLD)
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (70, 40, 110), a), BOLD)
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

_FUN = {"hook": s_hook, "intro": s_intro, "casa": s_casa, "france": s_france, "madrid": s_madrid, "banc": s_banc, "heure": s_heure,
        "pret": s_pret, "seville": s_seville, "mondial": s_mondial, "regard": s_regard, "you": s_you, "abonne": s_abonne, "question": s_question, "logo": s_logo}
DUSTAMT = {"hook": 0.4, "heure": 1.0, "seville": 1.0, "mondial": 1.0, "regard": 1.0, "question": 0.4, "logo": 0.2}
def _wrap(name, f):
    def g(img, d, tg, k):
        dust(d, tg, DUSTAMT.get(name, 0.5)); return f(img, d, tg, k)
    return g
SCENES = {n: _wrap(n, f) for n, f in _FUN.items()}
BGLEVEL = {"hook": 0.0, "intro": 0.15, "casa": 0.3, "france": 0.0, "madrid": 0.25, "banc": 0.0, "heure": 0.8, "pret": 0.35,
           "seville": 0.8, "mondial": 0.95, "regard": 1.0, "you": 0.2, "abonne": 0.0, "question": 0.0, "logo": 0.0}

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

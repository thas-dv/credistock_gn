# -*- coding: utf-8 -*-
"""Style « valise » : côte de Conakry au crépuscule (océan, palmiers, maisons aux toits de tôle, latérite) ; passages Europe froids (bruine bleue) ; aube dorée.
Personnage « athlète » (maillot jaune sable sans numéro) avec une VALISE : marche, s'assoit dessus, la brandit au cri, monte l'escalier de carrière.
Aucun nom propre, club, logo ni drapeau à l'écran. Types : hook intro conakry lorient lemans portes valise istres sommet titres regard you abonne question logo
(08/11/2026 : Naby Keïta, épisode 5). Usage : python3 render_valise.py timing_voix.json video_brut.mp4 [t_from t_to every]"""

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



# =============================================================== style « valise » (08/11/2026, Naby Keïta — épisode 5)
# Décor : côte de Conakry au crépuscule (océan, palmiers, maisons aux toits de tôle, sol de latérite) ; passages « Europe » froids
# (teinte bleue + bruine) ; aube dorée à la réussite. Personnage « athlète » (maillot jaune sable sans numéro) qui porte une VALISE :
# marche, s'assoit dessus, la soulève au cri, monte un ESCALIER de carrière. Aucun nom de club, logo, drapeau ni trophée réel à l'écran.
NIGHT = (8, 12, 30); SKY2 = (52, 34, 70); DUSK = (238, 120, 70); DUSK2 = (255, 200, 120)
ACC = (255, 150, 30); AMBER = (255, 190, 90); ICE = (140, 190, 255); SEA = (20, 50, 80); EARTH = (120, 56, 30)
ORANGE = ACC
HOR = 900; FEET = 1500
JER = (226, 176, 40)
SUIT = (150, 40, 36); SUIT_D = (100, 24, 22)

POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-28, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))
POSES["fist"] = dict(t=-4, la=(-172, -6), ra=(25, -70), ll=(-14, 4), rl=(14, -4))
POSES["carry"] = dict(t=2, la=(-8, 4), ra=(14, -4), ll=(-5, 0), rl=(5, 0))
POSES["lift"] = dict(t=-6, la=(-175, -4), ra=(160, -20), ll=(-14, 4), rl=(14, -4))
POSES["down"] = dict(t=18, la=(-8, 10), ra=(10, -10), ll=(-6, 0), rl=(6, 0))
POSES["kick"] = dict(t=-10, la=(-70, 10), ra=(60, -10), ll=(-10, 5), rl=(70, -25))
def walk_pose(ph):
    s = math.sin(ph)
    return dict(t=4, la=(-22 * s, 20), ra=(10, -6), ll=(24 * s, max(0, -30 * s)), rl=(-24 * s, max(0, 30 * s)))

def P(img, x, y, s, pose, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER); kw.setdefault("shorts", (40, 44, 60)); kw.setdefault("sock", (236, 236, 240))
    player(img, x, y, s, pose, **kw)

def suitcase(d, cx, by, s=1.0, open_=0.0):
    """valise posée : (cx, by) = bas centre"""
    w, h = 200 * s, 140 * s
    d.rounded_rectangle((cx - w / 2, by - h, cx + w / 2, by), int(16 * s), fill=SUIT, outline=SUIT_D, width=max(3, int(6 * s)))
    d.line((cx - w / 2 + 8 * s, by - h * 0.5, cx + w / 2 - 8 * s, by - h * 0.5), fill=SUIT_D, width=max(2, int(5 * s)))
    for dx in (-0.3, 0.3): d.rectangle((cx + dx * w - 8 * s, by - h - 2 * s, cx + dx * w + 8 * s, by - h + 22 * s), fill=(200, 170, 90))
    d.arc((cx - 40 * s, by - h - 40 * s, cx + 40 * s, by - h + 20 * s), 180, 360, fill=(40, 30, 30), width=max(3, int(9 * s)))
    d.rounded_rectangle((cx + w * 0.12, by - h * 0.85, cx + w * 0.42, by - h * 0.62), int(6 * s), fill=(235, 225, 200))   # étiquette

def hand_case(d, x, y, s, swing=0.0):
    """valise tenue à la main droite d'un personnage de taille s posé en (x, y)"""
    hx = x + 0.22 * s + 6 * swing; hy = y - 0.62 * s
    suitcase(d, hx, hy + 0.36 * s, 0.0026 * s * 100 / 1.0 * 0.55)

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        night = mix(NIGHT, SKY2, u ** 1.4); day = mix((90, 120, 190), mix(DUSK, DUSK2, u), u ** 0.7)
        d.line((0, y, W, y), fill=mix(night, day, lit))
    # étoiles (nuit)
    rng = np.random.default_rng(3)
    for i in range(70):
        x, y = rng.uniform(0, W), rng.uniform(0, HOR * 0.6); r = rng.uniform(1, 2.6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((230, 230, 255), mix(NIGHT, DUSK, lit), lit))
    # soleil / lune
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.ellipse((W / 2 - 340, HOR - 360, W / 2 + 340, HOR + 160), fill=(255, 170, 90, int(60 + 150 * lit)))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(80))); d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - 100, HOR - 170, W / 2 + 100, HOR + 30), fill=mix((236, 230, 210), (255, 220, 150), lit))
    # océan + reflet
    for y in range(HOR - 40, HOR + 110):
        u = (y - HOR + 40) / 150
        d.line((0, y, W, y), fill=mix(mix(SEA, (10, 20, 40), u), mix((230, 140, 90), (120, 80, 90), u), lit * 0.8))
    for i in range(14):
        yy = HOR - 30 + i * 10; ww = 140 - i * 6
        d.line((W / 2 - ww, yy, W / 2 + ww, yy), fill=mix((180, 170, 160), (255, 220, 150), lit), width=3)
    # maisons basses aux toits de tôle + palmiers
    for i, (x, w, h) in enumerate([(-30, 230, 170), (190, 200, 140), (620, 240, 180), (850, 260, 150)]):
        base = HOR + 130
        wall = mix(mix((50, 40, 54), (226, 190, 150), lit), [(70, 110, 140), (180, 110, 80), (120, 150, 90), (200, 180, 120)][i], 0.3)
        d.rectangle((x, base - h, x + w, base), fill=wall)
        roof = mix((70, 74, 86), (170, 170, 175), lit)
        d.polygon([(x - 20, base - h), (x + w + 20, base - h), (x + w - 10, base - h - 50), (x + 10, base - h - 50)], fill=roof)
        for rx in range(int(x - 10), int(x + w + 10), 18): d.line((rx, base - h - 48, rx + 4, base - h), fill=mix(roof, (0, 0, 0), 0.3), width=2)
        for fx in range(int(x + 30), int(x + w - 40), 80):
            on = (fx + i) % 3 == 0
            d.rectangle((fx, base - h + 50, fx + 40, base - h + 100), fill=mix(AMBER, wall, 0.3 + 0.5 * lit) if on else mix(wall, (0, 0, 0), 0.45))
    def palm(x, y, s):
        tc = mix((22, 18, 26), (90, 60, 40), lit)
        for k in range(12):
            a = k / 12; d.ellipse((x + 40 * s * a ** 2 - 12 * s, y - 520 * s * a - 12 * s, x + 40 * s * a ** 2 + 12 * s, y - 520 * s * a + 12 * s), fill=tc)
        tx, ty = x + 40 * s, y - 520 * s
        lc = mix((16, 30, 24), (60, 110, 50), lit)
        for ang in (-160, -125, -90, -55, -20, 15):
            pts = [(tx, ty)]
            for j in range(1, 8):
                u = j / 7; a = math.radians(ang)
                pts.append((tx + math.cos(a) * 240 * s * u, ty + math.sin(a) * 120 * s * u + 160 * s * u * u))
            d.line(pts, fill=lc, width=int(16 * s))
    palm(90, HOR + 260, 1.0); palm(960, HOR + 240, 0.9)
    # sol de latérite
    for y in range(HOR + 130, H):
        u = (y - HOR - 130) / (H - HOR - 130)
        d.line((0, y, W, y), fill=mix(mix((44, 24, 20), EARTH, 0.4 + 0.6 * lit), (10, 6, 6), 0.55 * u))
    rng = np.random.default_rng(9)
    for i in range(160):
        x, y = rng.uniform(0, W), rng.uniform(HOR + 150, H); r = rng.uniform(1, 4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((60, 34, 26), (170, 100, 60), lit * rng.uniform(0.3, 1)))
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
    """passage « Europe » : teinte froide + bruine"""
    img.alpha_composite(Image.new("RGBA", (W, H), (30, 60, 110, int(130 * a))))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(4)
    for i in range(110):
        x0, y0, sp = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 1.2)
        y = (y0 + tg * 900 * sp) % H; x = x0 - (tg * 120 * sp) % W
        x %= W
        d.line((x, y, x - 10, y + 34), fill=mix((40, 60, 90), (170, 190, 220), a * 0.7), width=2)

DUST = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.3, 1.0)) for i in range(70)]
def dust(d, tg, amt=1.0):
    for x0, y0, z in DUST[:int(len(DUST) * amt)]:
        y = (y0 - tg * 40 * z) % H; x = x0 + 20 * math.sin(tg * 0.8 + x0)
        r = 1.5 + 2.5 * z; d.ellipse((x - r, y - r, x + r, y + r), fill=mix((60, 40, 50), (255, 210, 150), z * 0.7))

def plane(d, x, y, s=1.0, flip=False, col=(235, 235, 240)):
    f = -1 if flip else 1
    q = lambda px, py: (x + f * px * s, y + py * s)
    d.polygon([q(-150, -10), q(130, -14), q(170, 0), q(130, 14), q(-150, 10)], fill=col)
    d.polygon([q(-20, 0), q(40, 0), q(-40, 90), q(-75, 90)], fill=mix(col, (0, 0, 0), 0.15))
    d.polygon([q(-20, 0), q(40, 0), q(-40, -90), q(-75, -90)], fill=mix(col, (0, 0, 0), 0.05))
    d.polygon([q(-150, -8), q(-120, -8), q(-150, -60), q(-170, -60)], fill=col)
    for i in range(6): d.ellipse((q(-80 + i * 30, -4)[0] - 4, q(0, -4)[1] - 4, q(-80 + i * 30, -4)[0] + 4, q(0, -4)[1] + 4), fill=(60, 80, 120))

def door(d, cx, by, s, open_=0.0, col=(90, 60, 40), light=AMBER):
    w, h = 260 * s, 480 * s
    d.rectangle((cx - w / 2 - 14 * s, by - h - 14 * s, cx + w / 2 + 14 * s, by), fill=(30, 24, 26))
    if open_ > 0: d.rectangle((cx - w / 2, by - h, cx + w / 2, by), fill=light)
    ww = w * (1 - 0.8 * open_)
    d.rectangle((cx - w / 2, by - h, cx - w / 2 + ww, by), fill=col, outline=mix(col, (0, 0, 0), 0.4), width=max(3, int(6 * s)))
    d.ellipse((cx - w / 2 + ww - 34 * s, by - h / 2 - 10 * s, cx - w / 2 + ww - 14 * s, by - h / 2 + 10 * s), fill=GOLD)

def xmark(d, cx, cy, r, col=RED, w=22):
    d.line((cx - r, cy - r, cx + r, cy + r), fill=col, width=w); d.line((cx - r, cy + r, cx + r, cy - r), fill=col, width=w)

def tin(d, x, y, r, rot):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(170, 170, 176), outline=(90, 90, 100), width=4)
    d.line((x - r * math.cos(rot), y - r * math.sin(rot), x + r * math.cos(rot), y + r * math.sin(rot)), fill=(220, 60, 50), width=6)

def orange_fruit(d, x, y, r):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 140, 30)); d.ellipse((x - 6, y - r - 6, x + 8, y - r + 4), fill=(60, 130, 50))

def rag_ball(d, x, y, r, rot):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(190, 170, 140), outline=(110, 90, 70), width=4)
    for i in range(3):
        a = rot + i * 2.1; d.arc((x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.8), math.degrees(a), math.degrees(a) + 90, fill=(110, 90, 70), width=4)

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
        if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[JER, WHITE, GOLD][c])

def cone(img, x, a=1.0, col=(255, 236, 190)):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(x - 40, 0), (x + 40, 0), (x + 300, FEET + 60), (x - 300, FEET + 60)], fill=col + (int(110 * a),))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(24)))

def armband(d, cx, cy, s=1.0, k=1.0):
    sc = s * (1 + 0.4 * (1 - eout(k / 0.2)))
    d.rounded_rectangle((cx - 170 * sc, cy - 90 * sc, cx + 170 * sc, cy + 90 * sc), int(30 * sc), fill=GOLD, outline=(140, 100, 20), width=int(8 * sc))
    text(d, (cx, cy + 4 * sc), "C", int(150 * sc), BG, BOLD)

def crowd(d, tg, lit=1.0, n=14):
    for i in range(n):
        x = 40 + i * (W - 80) / (n - 1); h = 200 + 50 * ((i * 37) % 5) / 4
        up = math.sin(tg * 5 + i) > 0
        c = mix((14, 12, 20), (60, 40, 40), 0.3 * lit)
        y0 = H - 40
        d.rounded_rectangle((x - 34, y0 - h, x + 34, y0), 26, fill=c); d.ellipse((x - 26, y0 - h - 58, x + 26, y0 - h - 6), fill=c)
        if up: d.line((x + 24, y0 - h + 20, x + 50, y0 - h - 110), fill=c, width=16)

def series_banner(d, tg):
    """titre de la série dès 0 s (jusqu'à 3,2 s) : « ILS ONT FAILLI ABANDONNER — ÉPISODE 5 »"""
    if tg > 3.4: return
    a = min(1, (tg + 0.2) / 0.15) * (1 - ease((tg - 3.0) / 0.4))
    c = mix(BG, WHITE, a); g = mix(BG, GOLD, a)
    d.rounded_rectangle((90, 70, W - 90, 200), 22, fill=mix(BG, (70, 40, 20), a), outline=g, width=4)
    text(d, (W / 2, 115), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), c, BOLD)
    text(d, (W / 2, 168), "ÉPISODE 5", 40, g, MONO)

def kM(tg, name): return tg - M(name, 99) + 0.1

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    series_banner(d, tg)
    P(img, W / 2 - 40, FEET + 40, 270, "down"); suitcase(d, W / 2 + 190, FEET + 40, 1.0)
    kk = tg - K["hook"] + 0.15
    text(d, (W / 2, 420), "PAS ASSEZ", int(fit("PAS ASSEZ", 150, 1000) * (1 + 0.3 * (1 - eout((tg + 0.1) / 0.2)))), WHITE, BOLD, stroke=9, scol=BG)
    if kk > 0:
        sc = 1 + 0.5 * (1 - eout(kk / 0.18))
        text(d, (W / 2, 610), "BON ?", int(fit("BON ?", 230, 1000) * sc), RED, BOLD, stroke=10, scol=BG)
        hit = max(0, 1 - kk / 0.25)
    kd = kM(tg, "dit")
    if kd > 0: text(d, (W / 2, 800), "ON TE L'A DÉJÀ DIT ?", fit("ON TE L'A DÉJÀ DIT ?", 70, 980), GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit, bg=0.0)

def s_intro(img, d, tg, k):
    hit = 0.0
    label(d, 300, "L'HISTOIRE VRAIE", k, 100, WHITE, "D'UN FOOTBALLEUR GUINÉEN", ACC)
    ks = kM(tg, "sommet")
    if ks > 0:
        text(d, (W / 2, 560), "DE LA RUE", fit("DE LA RUE", 120, 980), WHITE, BOLD, stroke=7, scol=BG)
        text(d, (W / 2, 700), "AU SOMMET", int(fit("AU SOMMET", 140, 980) * (1 + 0.3 * (1 - eout(ks / 0.2)))), GOLD, BOLD, stroke=8, scol=BG)
        if ks < 0.25: hit = 1 - ks / 0.25
    kc = kM(tg, "conakry")
    if kc > 0:
        hit = max(hit, stamp(img, "CONAKRY", (W / 2, 900), 120, -4, kc, ACC))
    P(img, W / 2, FEET, 240, "stand"); shadow(d, W / 2, FEET, 240)
    return dict(hit=hit, bg=0.1)

def s_conakry(img, d, tg, k):
    hit = 0.0
    label(d, 290, "UNE FAMILLE MODESTE", k, 90, WHITE)
    kb = kM(tg, "ballon"); kr = kM(tg, "rond")
    if kb > 0 and kr <= 0:
        x = W / 2; y = 760; r = 120
        d.ellipse((x - r, y - r, x + r, y + r), outline=WHITE, width=10)
        for a in range(5): d.line((x, y, x + r * math.cos(a * 1.256), y + r * math.sin(a * 1.256)), fill=WHITE, width=6)
        xmark(d, x, y, 150, RED, 26)
        text(d, (W / 2, 990), "PAS DE VRAI BALLON", int(fit("PAS DE VRAI BALLON", 84, 980) * (1 + 0.25 * (1 - eout(kb / 0.2)))), RED, BOLD, stroke=6, scol=BG)
        if kb < 0.25: hit = 1 - kb / 0.25
    if kr > 0:
        text(d, (W / 2, 520), "TOUT CE QUI EST ROND", fit("TOUT CE QUI EST ROND", 84, 980), GOLD, BOLD, stroke=6, scol=BG)
        if kr < 0.25: hit = 1 - kr / 0.25
        for i, f in enumerate((tin, orange_fruit, rag_ball)):
            x = 230 + i * 310; y = 760 + 30 * math.sin(tg * 4 + i)
            if f is orange_fruit: f(d, x, y, 60)
            else: f(d, x, y, 60, tg * 3 + i)
    # il frappe une boîte de conserve dans la rue (pas de jonglage)
    ph = (k % 1.4) / 1.4
    P(img, 330, FEET, 230, "kick" if ph < 0.25 else "stand"); shadow(d, 330, FEET, 230)
    u = min(1, max(0, (ph - 0.18) / 0.7))
    tin(d, lerp(400, 960, u), FEET - 30 - 220 * math.sin(math.pi * u), 34, tg * 9)
    return dict(hit=hit, bg=0.12)

def s_lorient(img, d, tg, k):
    hit = 0.0
    kf = kM(tg, "france"); ke = kM(tg, "essai"); kp = kM(tg, "bon2"); kt = kM(tg, "retour")
    if kt > 0:
        # retour : l'avion repart vers la gauche, il est assis sur sa valise
        u = eout(min(1, kt / 1.4))
        plane(d, lerp(W + 200, -300, u), 420 - 100 * u, 1.1, flip=True)
        text(d, (W / 2, 280), "RETOUR À LA MAISON", int(fit("RETOUR À LA MAISON", 90, 980) * (1 + 0.25 * (1 - eout(kt / 0.2)))), GREY, BOLD, stroke=6, scol=BG)
        suitcase(d, W / 2, FEET, 1.2); P(img, W / 2, FEET - 120, 230, "sad")
        stamp(img, "PAS ASSEZ BON", (W / 2, 520), 110, -6, max(kp, 1.0), RED)
        if kt < 0.25: hit = 1 - kt / 0.25
        return dict(hit=hit, bg=0.0)
    cold(img, tg, min(1, max(0, k) / 0.4)); d = ImageDraw.Draw(img)
    badge(d, 200, 300, "16 ANS", k, GOLD, 110)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    if kf > 0:
        text(d, (640, 300), "DIRECTION LA FRANCE", fit("DIRECTION LA FRANCE", 70, 620), WHITE, BOLD, stroke=5, scol=BG)
        u = min(1, kf / 1.2); plane(d, lerp(-300, W + 300, u), 560 - 160 * u, 1.0)
    # il marche avec sa valise
    x = lerp(160, W / 2, min(1, max(0, k) / 2.2)); sw = math.sin(tg * 7)
    P(img, x, FEET, 240, walk_pose(tg * 7) if x < W / 2 - 2 else "carry"); shadow(d, x, FEET, 240)
    suitcase(d, x + 90, FEET - 10 + 6 * sw, 0.7)
    if ke > 0:
        text(d, (W / 2, 820), "UN ESSAI", int(fit("UN ESSAI", 120, 980) * (1 + 0.25 * (1 - eout(ke / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
        if ke < 0.25: hit = max(hit, 1 - ke / 0.25)
    if kp > 0:
        hit = max(hit, stamp(img, "PAS ASSEZ BON", (W / 2, 1040), 130, -6, kp, RED))
    return dict(hit=hit, bg=0.0)

def s_lemans(img, d, tg, k):
    hit = 0.0
    cold(img, tg, 0.8); d = ImageDraw.Draw(img)
    kc = kM(tg, "croit"); kf = kM(tg, "faillite")
    op = 0.0
    if kc > 0: op = eout(min(1, kc / 0.5))
    if kf > 0: op = max(0.0, op * (1 - eout(kf / 0.15)))
    door(d, W / 2 + 160, FEET, 1.3, op)
    text(d, (W / 2, 300), "UN AUTRE CLUB", fit("UN AUTRE CLUB", 96, 980), WHITE, BOLD, stroke=6, scol=BG)
    if kc > 0 and kf <= 0:
        text(d, (W / 2, 420), "CROIT EN LUI", int(fit("CROIT EN LUI", 110, 980) * (1 + 0.25 * (1 - eout(kc / 0.2)))), GOLD, BOLD, stroke=7, scol=BG)
        if kc < 0.25: hit = 1 - kc / 0.25
    x = W / 2 - 220
    P(img, x, FEET, 240, "carry" if kf <= 0 else "down"); shadow(d, x, FEET, 240); suitcase(d, x + 95, FEET, 0.7)
    if kf > 0:
        hit = max(hit, stamp(img, "FAILLITE", (W / 2, 640), 190, -7, kf, RED))
    return dict(hit=hit, bg=0.0)

def s_portes(img, d, tg, k):
    hit = 0.0
    cold(img, tg, 1.0); d = ImageDraw.Draw(img)
    door(d, 280, 1180, 0.9, 0.0); door(d, 800, 1180, 0.9, 0.0)
    kp = kM(tg, "portes")
    if kp > 0:
        xmark(d, 280, 960, 120 * eout(min(1, kp / 0.2)), RED, 24)
        if kp > 0.2: xmark(d, 800, 960, 120 * eout(min(1, (kp - 0.2) / 0.2)), RED, 24)
        text(d, (W / 2, 300), "2 PORTES FERMÉES", int(fit("2 PORTES FERMÉES", 100, 980) * (1 + 0.25 * (1 - eout(kp / 0.2)))), RED, BOLD, stroke=7, scol=BG)
        if kp < 0.25: hit = 1 - kp / 0.25
    kb = tg - K["build_start"] + 0.1
    ki = tg - K["build_end"] + 0.1
    if kb > 0.6: text(d, (W / 2, 420), typew("N'IMPORTE QUI AURAIT", kb - 0.6, 26), fit("N'IMPORTE QUI AURAIT", 76, 980), GREY, BOLD, stroke=5, scol=BG)
    if ki > -0.6: text(d, (W / 2, 520), typew("RANGÉ SA VALISE…", ki + 0.6, 26), fit("RANGÉ SA VALISE…", 84, 980), WHITE, BOLD, stroke=6, scol=BG)
    # assis sur sa valise sous la bruine, tête basse
    suitcase(d, W / 2, FEET + 40, 1.3); P(img, W / 2, FEET - 110, 240, "sad")
    return dict(hit=hit, bg=0.0)

def s_valise(img, d, tg, k):
    kb = tg - K["boom"]
    hit = 0.0; flash = 0.0
    kk = max(0.0, kb + 0.06)
    for i in range(5):
        if kk > i * 0.06: cone(img, 120 + i * 210, 1.0)
    d = ImageDraw.Draw(img)
    if kk < 0.4: flash = max(0, 0.95 - kk * 2.4)
    sw = eout(kk / 0.6)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.ellipse((W / 2 - 900 * sw, FEET - 120 * sw, W / 2 + 900 * sw, FEET + 120 * sw), fill=GOLD + (int(150 * (1 - sw * 0.6)),))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(30))); d = ImageDraw.Draw(img)
    # il se lève et brandit sa valise au-dessus de la tête
    u = eout(min(1, kk / 0.35))
    P(img, W / 2 - 30, FEET, 290, "lift" if u > 0.4 else "sad", glow=1.6); shadow(d, W / 2 - 30, FEET, 290)
    suitcase(d, lerp(W / 2, W / 2 - 40, u), lerp(FEET + 40, FEET - 560, u), lerp(1.2, 1.25, u))
    burst(d, W / 2 - 40, FEET - 620, kk, 22, 420, GOLD, 3, 9)
    hit = max(0, 1 - kk / 0.3)
    e = eout(kk / 0.22)
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, e)
    for off, c in ((10, (255, 60, 80)), (-10, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        text(d, (x1 + o, 300), "IL NE RANGE PAS", fit("IL NE RANGE PAS", 120, 1000), c, BOLD, stroke=8 if c == WHITE else 0, scol=BG)
        text(d, (x2 - o, 460), "SA VALISE !", fit("SA VALISE !", 170, 1000), c if c != WHITE else GOLD, BOLD, stroke=9 if c == WHITE else 0, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=0.35)

def s_istres(img, d, tg, k):
    hit = 0.0
    label(d, 270, "2 ANS PLUS TARD", k, 92, WHITE)
    kt = kM(tg, "tournoi"); kr = kM(tg, "recruteurs"); ks = kM(tg, "signe")
    if kt > 0:
        text(d, (W / 2, 390), "UN TOURNOI", int(fit("UN TOURNOI", 110, 980) * (1 + 0.25 * (1 - eout(kt / 0.2)))), ACC, BOLD, stroke=7, scol=BG)
        if kt < 0.25: hit = 1 - kt / 0.25
    # il court (sprint, sans ballon), des recruteurs l'observent avec un carnet
    x = 280 + (k * 260) % 620
    P(img, x, FEET, 240, run_pose(tg * 11)); shadow(d, x, FEET, 240)
    if kr > 0:
        for i, rx in enumerate((110, 970)):
            c = (16, 16, 24)
            d.rounded_rectangle((rx - 45, FEET - 330, rx + 45, FEET - 80), 30, fill=c); d.ellipse((rx - 36, FEET - 410, rx + 36, FEET - 338), fill=c)
            d.rectangle((rx - 60 if i == 0 else rx + 20, FEET - 260, rx - 20 if i == 0 else rx + 60, FEET - 205), fill=(240, 236, 220))
        text(d, (W / 2, 540), "ON LE REPÈRE", int(fit("ON LE REPÈRE", 96, 980) * (1 + 0.25 * (1 - eout(kr / 0.2)))), WHITE, BOLD, stroke=6, scol=BG)
    if ks > 0:
        hit = max(hit, stamp(img, "SIGNÉ", (W / 2, 760), 200, -6, ks, GOLD))
        text(d, (W / 2, 930), "2e DIVISION", fit("2e DIVISION", 90, 980), WHITE, BOLD, stroke=6, scol=BG)
        burst(d, W / 2, 760, ks, 18, 360, GOLD, 4)
    return dict(hit=hit, bg=0.4)

STEPS = [("champion1", "2× CHAMPION", "EN AUTRICHE"), ("meilleur", "MEILLEUR JOUEUR", "DU CHAMPIONNAT"), ("leipzig", "L'ALLEMAGNE", ""), ("liverpool", "L'ANGLETERRE", "UN GÉANT")]
def s_sommet(img, d, tg, k):
    """l'escalier de la carrière : il monte marche après marche avec sa valise"""
    hit = 0.0; flash = 0.0
    text(d, (W / 2, 260), "MARCHE APRÈS MARCHE", fit("MARCHE APRÈS MARCHE", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
    sx, sy, sw_, sh_ = 120, FEET + 80, 210, 170
    lvl = 0
    for i, (m, a, b) in enumerate(STEPS):
        kk = kM(tg, m)
        x0 = sx + i * sw_; y0 = sy - (i + 1) * sh_
        on = kk > 0
        d.rectangle((x0, y0, x0 + sw_ + 4, sy), fill=mix((40, 30, 40), (90, 60, 40), 0.4) if not on else mix((120, 80, 40), GOLD, 0.35 if i < 3 else 0.8))
        d.line((x0, y0, x0 + sw_, y0), fill=GOLD if on else GREY, width=8)
        if on:
            lvl = i + 1
            txt_y = y0 - 260 - (60 if i == 3 else 0)
            col = GOLD if i == 3 else WHITE
            if kk < 0.25: hit = max(hit, 1 - kk / 0.25)
            if i == 3:
                flash = max(flash, 0.4 * max(0, 1 - kk / 0.3))
    # étiquettes affichées en haut (la dernière atteinte)
    for i, (m, a, b) in enumerate(STEPS):
        kk = kM(tg, m)
        if kk > 0 and (i == len(STEPS) - 1 or kM(tg, STEPS[i + 1][0]) <= 0):
            text(d, (W / 2, 420), a, int(fit(a, 120, 980) * (1 + 0.25 * (1 - eout(kk / 0.2)))), GOLD if i == 3 else WHITE, BOLD, stroke=7, scol=BG)
            if b: text(d, (W / 2, 540), b, fit(b, 70, 980), ACC, BOLD, stroke=5, scol=BG)
            if i == 3: burst(d, W / 2, 420, kk, 20, 420, GOLD, 5)
    # personnage : position sur la marche atteinte (avec un petit saut entre deux marches)
    x = sx + (lvl - 0.5) * sw_ if lvl else sx - 30
    y = sy - lvl * sh_
    P(img, x, y, 200, "fist" if lvl == 4 else "carry"); suitcase(d, x + 80, y, 0.55)
    return dict(hit=hit, flash=flash, bg=0.55 if lvl < 4 else 0.9)

def s_titres(img, d, tg, k):
    hit = 0.0; flash = 0.0
    kc = kM(tg, "coupe"); ka = kM(tg, "angleterre"); kp = kM(tg, "capitaine")
    if kp <= 0:
        if kc > 0:
            trophy(d, W / 2 - (200 if ka > 0 else 0), 820, 1.0 * (1 + 0.2 * (1 - eout(kc / 0.25))), GOLD)
            text(d, (W / 2, 300), "LA PLUS GRANDE", fit("LA PLUS GRANDE", 96, 980), WHITE, BOLD, stroke=6, scol=BG)
            text(d, (W / 2, 410), "COUPE D'EUROPE", fit("COUPE D'EUROPE", 110, 980), GOLD, BOLD, stroke=7, scol=BG)
            if kc < 0.3: hit = max(hit, 1 - kc / 0.3); flash = 0.3 * max(0, 1 - kc / 0.3)
        if ka > 0:
            trophy(d, W / 2 + 230, 820, 0.85 * (1 + 0.2 * (1 - eout(ka / 0.25))), (230, 230, 236))
            hit = max(hit, stamp(img, "CHAMPION D'ANGLETERRE", (W / 2, 1080), 90, -4, ka, WHITE))
        confetti(d, max(0, kc))
        P(img, W / 2, FEET + 60, 220, "up"); shadow(d, W / 2, FEET + 60, 220)
    else:
        text(d, (W / 2, 300), "ET IL DEVIENT", fit("ET IL DEVIENT", 96, 980), WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 430), "CAPITAINE", int(fit("CAPITAINE", 160, 980) * (1 + 0.3 * (1 - eout(kp / 0.2)))), GOLD, BOLD, stroke=8, scol=BG)
        text(d, (W / 2, 570), "DE LA GUINÉE", fit("DE LA GUINÉE", 100, 980), ACC, BOLD, stroke=7, scol=BG)
        armband(d, W / 2, 820, 1.0, kp)
        if kp < 0.3: hit = max(hit, 1 - kp / 0.3); flash = 0.3 * max(0, 1 - kp / 0.3)
        P(img, W / 2, FEET + 60, 230, "fist"); shadow(d, W / 2, FEET + 60, 230)
    return dict(hit=hit, flash=flash, bg=0.95)

def s_regard(img, d, tg, k):
    hit = 0.0
    kb = kM(tg, "bon3"); kp = kM(tg, "porte"); kpa = kM(tg, "pays")
    text(d, (W / 2, 290), "LE GAMIN", fit("LE GAMIN", 110, 980), GREY if kp > 0 else WHITE, BOLD, stroke=6, scol=BG)
    if kb > 0: text(d, (W / 2, 420), "PAS ASSEZ BON…", fit("PAS ASSEZ BON…", 100, 980), GREY if kp > 0 else RED, BOLD, stroke=6, scol=BG)
    if kp > 0:
        text(d, (W / 2, 580), "PORTE LE BRASSARD", int(fit("PORTE LE BRASSARD", 90, 980) * (1 + 0.25 * (1 - eout(kp / 0.2)))), GOLD, BOLD, stroke=7, scol=BG)
        if kp < 0.25: hit = 1 - kp / 0.25
    if kpa > 0:
        hit = max(hit, stamp(img, "DE TOUT UN PAYS", (W / 2, 740), 110, -4, kpa, WHITE))
        crowd(d, tg, 1.0)
    P(img, W / 2, FEET - 60, 250, "up" if kp > 0 else "stand", glow=1.3)
    if kp > 0: armband(d, W / 2 - 150, FEET - 520, 0.35, 1.0)
    return dict(hit=hit, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ACC, BOLD, stroke=6, scol=BG)
    kn = kM(tg, "non")
    if kn > 0:
        rng = np.random.default_rng(8)
        n = min(9, 1 + int(kn / 0.16))
        for i in range(n):
            x, y, a = rng.uniform(170, W - 170), rng.uniform(480, 1000), rng.uniform(-14, 14)
            stamp(img, "NON", (x, y), 100, a, kn - i * 0.16 + 0.3, RED)
        d = ImageDraw.Draw(img)
    hit = 0.0
    ka = tg - K["arms_up"] + 0.1
    if ka > 0:
        text(d, (W / 2, 1110), "POUR RANGER TA VALISE ?", int(fit("POUR RANGER TA VALISE ?", 76, 980) * (1 + 0.25 * (1 - eout(ka / 0.2)))), WHITE, BOLD, stroke=6, scol=BG)
        if ka < 0.25: hit = 1 - ka / 0.25
    elif kn > 0:
        text(d, (W / 2, 1110), "COMBIEN DE « NON » ?", fit("COMBIEN DE « NON » ?", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
    suitcase(d, W / 2, FEET + 20, 1.1)
    return dict(hit=hit, bg=0.2)

def glove(d, cx, cy, s=1.0, col=(240, 240, 236)):
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.rounded_rectangle((q(-80, -40)[0], q(0, -40)[1], q(80, 0)[0], q(0, 150)[1]), int(30 * s), fill=col)
    for i in range(4):
        x = -66 + i * 44
        d.rounded_rectangle((q(x, 0)[0], q(0, -150 + abs(i - 1.5) * 18)[1], q(x + 36, 0)[0], q(0, -20)[1]), int(18 * s), fill=col)
    d.rounded_rectangle((q(70, -10)[0], q(0, -60)[1], q(120, 0)[0], q(0, 40)[1]), int(20 * s), fill=col)
    d.rectangle((q(-84, 0)[0], q(0, 150)[1], q(84, 0)[0], q(0, 200)[1]), fill=ACC)

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
        text(d, (W / 2, 660), "DEMAIN · ÉPISODE 6", fit("DEMAIN · ÉPISODE 6", 74, 980), GOLD, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 770), typew("LE GARDIEN QUE SON GRAND CLUB", kd, 34), fit("LE GARDIEN QUE SON GRAND CLUB", 58, 980), WHITE, BOLD, stroke=5, scol=BG)
        text(d, (W / 2, 850), typew("N'A JAMAIS FAIT JOUER…", kd - 0.9, 30), fit("N'A JAMAIS FAIT JOUER…", 58, 980), WHITE, BOLD, stroke=5, scol=BG)
    km = kM(tg, "monde")
    if km > 0:
        hit = max(hit, stamp(img, "COUPE DU MONDE", (W / 2, 1010), 130, -6, km, ACC))
    glove(d, W / 2 + 40 * math.sin(tg * 2), 1300, 1.2)
    text(d, (W / 2 + 200, 1180), "?", 120, GOLD, BOLD, stroke=6, scol=BG)
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
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (90, 60, 20), a), BOLD)
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

_FUN = {"hook": s_hook, "intro": s_intro, "conakry": s_conakry, "lorient": s_lorient, "lemans": s_lemans, "portes": s_portes, "valise": s_valise,
        "istres": s_istres, "sommet": s_sommet, "titres": s_titres, "regard": s_regard, "you": s_you, "abonne": s_abonne, "question": s_question, "logo": s_logo}
DUSTAMT = {"hook": 0.5, "valise": 1.0, "sommet": 1.0, "titres": 1.0, "regard": 1.0, "question": 0.4, "logo": 0.2}
def _wrap(name, f):
    def g(img, d, tg, k):
        dust(d, tg, DUSTAMT.get(name, 0.5)); return f(img, d, tg, k)
    return g
SCENES = {n: _wrap(n, f) for n, f in _FUN.items()}
BGLEVEL = {"hook": 0.0, "intro": 0.1, "conakry": 0.12, "lorient": 0.0, "lemans": 0.0, "portes": 0.0, "valise": 0.35, "istres": 0.4,
           "sommet": 0.55, "titres": 0.95, "regard": 1.0, "you": 0.2, "abonne": 0.0, "question": 0.0, "logo": 0.0}

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

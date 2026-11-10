# -*- coding: utf-8 -*-
"""Style « brassard » : petite ville de montagne la nuit, petit terrain de club local, personnage « athlète » DÉFENSEUR (maillot corail sans numéro) timide qui trouve sa voix.
Aucun nom propre, club, logo ni drapeau à l'écran. Types : hook intro ville metz renvoi retour voix pro naples afrique regard you abonne question logo
(10/11/2026 : Kalidou Koulibaly, épisode 7). Usage : python3 render_brassard.py timing_voix.json video_brut.mp4 [t_from t_to every]"""

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
    s = s * 1.25; d.ellipse((x - 0.33 * s, y - 0.05 * s, x + 0.33 * s, y + 0.05 * s), fill=(6, 14, 10))





# =============================================================== style « brassard » (10/11/2026, Kalidou Koulibaly — épisode 7)
# Décor : petite ville de montagne la nuit (sapins, crêtes, brume, maisons aux fenêtres allumées), petit terrain de club local avec
# palissade en bois et un seul lampadaire ; la lumière monte jusqu'à un stade doré au sommet. Passages froids (brume + crachin).
# Personnage « athlète » DÉFENSEUR (maillot corail sans numéro) : tête baissée et épaules rentrées (timide), sac de sport qui tombe,
# relève la tête au cri avec des ONDES DE VOIX, bras écartés pour diriger, tacle glissé, brassard « C », tir au but.
# Aucun nom de club, logo, écusson, drapeau, monument ni trophée réel à l'écran.
NIGHT = (8, 12, 30); SKY2 = (30, 40, 70)
ACC = (255, 122, 92); AMBER = (255, 196, 110); ICE = (150, 196, 255)
ORANGE = ACC
FEET = 1500; HOR = 900
JER = (236, 98, 76); GLOVE = None
LIGHT = (255, 240, 200)

POSES["shy"] = dict(t=-14, la=(-6, 18), ra=(6, -18), ll=(-4, 0), rl=(4, 0))
POSES["sad"] = dict(t=-26, la=(-14, 30), ra=(14, -30), ll=(-6, 4), rl=(6, -4))
POSES["wide"] = dict(t=0, la=(-100, -10), ra=(100, 10), ll=(-20, 6), rl=(20, -6))
POSES["point"] = dict(t=4, la=(-112, 0), ra=(40, -50), ll=(-18, 8), rl=(18, -8))
POSES["fist"] = dict(t=-4, la=(-172, -6), ra=(25, -70), ll=(-14, 4), rl=(14, -4))
POSES["slide"] = dict(t=0, la=(-150, 10), ra=(50, 30), ll=(-6, 0), rl=(30, -30))
POSES["carry"] = dict(t=4, la=(-10, 6), ra=(30, -40), ll=(-5, 0), rl=(5, 0))

def P(img, x, y, s, pose, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER); kw.setdefault("shorts", (28, 30, 40)); kw.setdefault("sock", JER)
    player(img, x, y, s * 1.25, pose, **kw)

def make_bg(lit):
    """ville de montagne de nuit -> petit terrain éclairé ; lit = 0 sombre, 1 lumière dorée"""
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, HOR + 1):
        u = y / HOR
        d.line((0, y, W, y), fill=mix(mix(NIGHT, SKY2, u ** 1.4), mix((40, 46, 90), (240, 160, 90), u ** 1.6), lit * 0.7))
    rng = np.random.default_rng(7)
    for i in range(70):
        x, y = rng.uniform(0, W), rng.uniform(0, HOR * 0.5); r = rng.uniform(1, 2.4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix((220, 224, 250), (90, 80, 110), lit * 0.8))
    d.ellipse((780, 150, 900, 270), fill=mix((230, 232, 245), (255, 230, 170), lit))
    # crêtes et sapins (3 plans)
    for layer, (base, amp, col, coll) in enumerate([(560, 120, (24, 32, 56), (110, 90, 110)), (680, 90, (16, 24, 40), (80, 60, 70)), (790, 60, (10, 16, 26), (50, 40, 44))]):
        pts = [(0, H)]
        for x in range(0, W + 41, 40):
            pts.append((x, base - amp * (0.5 + 0.5 * math.sin(x / (170 + 60 * layer) + layer * 2)) - 20 * math.sin(x / 47 + layer)))
        pts.append((W, H)); d.polygon(pts, fill=mix(col, coll, lit * 0.5))
        for i in range(26 + 6 * layer):
            x = rng.uniform(-20, W + 20); yb = base - amp * (0.5 + 0.5 * math.sin(x / (170 + 60 * layer) + layer * 2)) + 30 + layer * 10
            h = 60 + 30 * layer + rng.uniform(0, 30)
            c = mix(mix(col, (0, 0, 0), 0.25), coll, lit * 0.35)
            d.polygon([(x, yb - h), (x - h * 0.28, yb), (x + h * 0.28, yb)], fill=c)
    # maisons de la petite ville (fenêtres allumées)
    for i, (x, w, h) in enumerate([(-10, 150, 170), (150, 120, 210), (280, 170, 150), (720, 140, 190), (870, 220, 160)]):
        by = HOR + 10
        c = mix((44, 34, 44), (120, 80, 70), lit * 0.6)
        d.rectangle((x, by - h, x + w, by), fill=c)
        d.polygon([(x - 12, by - h), (x + w / 2, by - h - 70), (x + w + 12, by - h)], fill=mix((30, 24, 30), (90, 50, 44), lit * 0.6))
        for fx in range(int(x + 22), int(x + w - 30), 46):
            for fy in range(int(by - h + 26), int(by - 40), 60):
                on = (fx * 7 + fy * 3 + i) % 4 != 0
                d.rectangle((fx, fy, fx + 24, fy + 32), fill=AMBER if on else (30, 30, 40))
    # palissade en bois + lampadaire
    for x in range(0, W, 34):
        d.rectangle((x, HOR - 30, x + 26, HOR + 70), fill=mix((52, 38, 30), (140, 100, 70), lit * 0.7))
    d.rectangle((0, HOR - 6, W, HOR + 4), fill=mix((40, 30, 24), (110, 80, 56), lit * 0.7))
    d.rectangle((150, 360, 162, HOR + 60), fill=(40, 42, 50)); d.rectangle((140, 340, 200, 362), fill=(60, 62, 70))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.ellipse((90, 300, 260, 420), fill=AMBER + (int(120 + 100 * lit),))
    dl.polygon([(150, 362), (190, 362), (520, FEET + 80), (-180, FEET + 80)], fill=AMBER + (int(30 + 40 * lit),))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(30))); d = ImageDraw.Draw(img)
    # pelouse
    for y in range(HOR + 70, H):
        u = (y - HOR - 70) / (H - HOR - 70)
        band = (int((y - HOR) ** 0.8 / 22) % 2)
        base = mix((14, 36, 26), (46, 112, 58), lit)
        d.line((0, y, W, y), fill=mix(mix(base, (0, 0, 0), 0.1 * band), (5, 10, 8), 0.5 * u))
    d.line((0, HOR + 170, W, HOR + 150), fill=mix((70, 90, 80), (235, 240, 230), lit), width=5)
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

FOG = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0))
_df = ImageDraw.Draw(FOG); _r = np.random.default_rng(11)
for _i in range(40):
    _x, _y = _r.uniform(0, W * 2), _r.uniform(600, 1500); _w = _r.uniform(250, 600)
    _df.ellipse((_x - _w, _y - 60, _x + _w, _y + 60), fill=(170, 186, 210, 40))
FOG = FOG.filter(ImageFilter.GaussianBlur(40))
def cold(img, tg, a=1.0):
    """passage froid : teinte bleue + brume qui glisse + crachin"""
    img.alpha_composite(Image.new("RGBA", (W, H), (30, 50, 100, int(110 * a))))
    off = int(tg * 40) % W
    f = FOG.crop((off, 0, off + W, H))
    if a < 1:
        aa = np.asarray(f).copy(); aa[..., 3] = (aa[..., 3] * a).astype(np.uint8); f = Image.fromarray(aa)
    img.alpha_composite(f)
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(4)
    for i in range(90):
        x0, y0, sp = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 1.2)
        y = (y0 + tg * 700 * sp) % H; x = (x0 - (tg * 60 * sp)) % W
        d.line((x, y, x - 5, y + 26), fill=mix((40, 60, 90), (170, 190, 220), a * 0.6), width=2)

DUST = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, H), np.random.default_rng(i + 900).uniform(0.3, 1.0)) for i in range(70)]
def dust(d, tg, amt=1.0):
    for x0, y0, z in DUST[:int(len(DUST) * amt)]:
        y = (y0 - tg * 40 * z) % H; x = x0 + 20 * math.sin(tg * 0.8 + x0)
        r = 1.5 + 2.5 * z; d.ellipse((x - r, y - r, x + r, y + r), fill=mix((60, 50, 70), (255, 230, 170), z * 0.7))

def xmark(d, cx, cy, r, col=RED, w=22):
    d.line((cx - r, cy - r, cx + r, cy + r), fill=col, width=w); d.line((cx - r, cy + r, cx + r, cy - r), fill=col, width=w)

def bag(d, cx, by, s=1.0, rot=0.0):
    """sac de sport générique"""
    L = Image.new("RGBA", (int(360 * s), int(240 * s)), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.rounded_rectangle((20 * s, 70 * s, 340 * s, 220 * s), int(60 * s), fill=(40, 48, 66, 255), outline=(20, 24, 34, 255), width=int(6 * s))
    dl.arc((110 * s, 10 * s, 250 * s, 130 * s), 180, 360, fill=(20, 24, 34, 255), width=int(14 * s))
    dl.line((60 * s, 140 * s, 300 * s, 140 * s), fill=JER + (255,), width=int(10 * s))
    return L.rotate(rot, resample=Image.BICUBIC, expand=True)

def boots(d, cx, cy, s=1.0):
    """paire de crampons génériques"""
    for dx in (-90, 90):
        x = cx + dx * s
        d.polygon([(x - 90 * s, cy), (x - 80 * s, cy - 70 * s), (x - 10 * s, cy - 80 * s), (x + 20 * s, cy - 40 * s), (x + 100 * s, cy - 20 * s), (x + 100 * s, cy + 10 * s)], fill=(30, 30, 36))
        d.line((x - 70 * s, cy - 60 * s, x + 10 * s, cy - 50 * s), fill=WHITE, width=int(6 * s))
        for i in range(5): d.rectangle((x - 80 * s + i * 40 * s, cy + 10 * s, x - 70 * s + i * 40 * s, cy + 28 * s), fill=(160, 160, 170))

def door(d, cx, by, s, open_=0.0, col=(90, 60, 40), light=AMBER):
    w, h = 260 * s, 480 * s
    d.rectangle((cx - w / 2 - 14 * s, by - h - 14 * s, cx + w / 2 + 14 * s, by), fill=(30, 24, 26))
    if open_ > 0: d.rectangle((cx - w / 2, by - h, cx + w / 2, by), fill=light)
    ww = w * (1 - 0.8 * open_)
    d.rectangle((cx - w / 2, by - h, cx - w / 2 + ww, by), fill=col, outline=mix(col, (0, 0, 0), 0.4), width=max(3, int(6 * s)))
    d.ellipse((cx - w / 2 + ww - 34 * s, by - h / 2 - 10 * s, cx - w / 2 + ww - 14 * s, by - h / 2 + 10 * s), fill=GOLD)

def armband(d, cx, cy, s=1.0, k=1.0):
    sc = s * (1 + 0.4 * (1 - eout(max(0, k) / 0.2)))
    d.rounded_rectangle((cx - 170 * sc, cy - 90 * sc, cx + 170 * sc, cy + 90 * sc), int(30 * sc), fill=GOLD, outline=(140, 100, 20), width=int(8 * sc))
    text(d, (cx, cy + 4 * sc), "C", int(150 * sc), BG, BOLD)

def waves(d, x, y, k, n=4, col=GOLD, r0=60, sp=520):
    """ondes de voix concentriques"""
    for i in range(n):
        kk = (k * 1.6 - i * 0.18) % 1.0 if k > 0 else -1
        if kk < 0: continue
        r = r0 + kk * sp; a = 1 - kk
        d.arc((x - r, y - r * 0.8, x + r, y + r * 0.8), -50, 50, fill=mix(BG, col, a), width=12)
        d.arc((x - r, y - r * 0.8, x + r, y + r * 0.8), 130, 230, fill=mix(BG, col, a), width=12)

def trophy(d, cx, cy, s=1.0, col=GOLD):
    q = lambda px, py: (cx + px * s, cy + py * s)
    d.polygon([q(-120, -230), q(120, -230), q(80, -60), q(25, -20), q(25, 50), q(80, 90), q(-80, 90), q(-25, 50), q(-25, -20), q(-80, -60)], fill=col)
    d.arc((cx - 190 * s, cy - 230 * s, cx - 70 * s, cy - 90 * s), 90, 270, fill=col, width=int(14 * s))
    d.arc((cx + 70 * s, cy - 230 * s, cx + 190 * s, cy - 90 * s), 270, 90, fill=col, width=int(14 * s))

def goal(d, cx, by, s=1.0, col=(240, 240, 240)):
    w, h = 820 * s, 330 * s
    for i in range(0, 15):
        x = cx - w / 2 + i * w / 14; d.line((x, by - h, x + (x - cx) * 0.08, by - 40 * s), fill=mix(col, BG, 0.65), width=2)
    for j in range(0, 7):
        y = by - h + j * h / 7; d.line((cx - w / 2, y, cx + w / 2, y), fill=mix(col, BG, 0.65), width=2)
    d.rectangle((cx - w / 2 - 12 * s, by - h - 12 * s, cx + w / 2 + 12 * s, by - h), fill=col)
    d.rectangle((cx - w / 2 - 12 * s, by - h, cx - w / 2, by), fill=col); d.rectangle((cx + w / 2, by - h, cx + w / 2 + 12 * s, by), fill=col)

def cone(img, x, a=1.0, col=(255, 236, 190)):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(x - 40, 0), (x + 40, 0), (x + 300, FEET + 60), (x - 300, FEET + 60)], fill=col + (int(110 * a),))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(24)))

CONF = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 99).uniform(-400, 0), i % 3) for i in range(70)]
def confetti(d, kv):
    for x0, y0, c in CONF:
        y = y0 + kv * 700; x = x0 + 30 * math.sin(kv * 4 + x0)
        if 0 < y < H: d.rectangle((x, y, x + 14, y + 24), fill=[JER, WHITE, GOLD][c])

def crowd(d, tg, lit=1.0, n=14, up_all=False):
    for i in range(n):
        x = 40 + i * (W - 80) / (n - 1); h = 200 + 50 * ((i * 37) % 5) / 4
        up = up_all or math.sin(tg * 5 + i) > 0
        c = mix((14, 12, 20), (60, 40, 40), 0.3 * lit)
        y0 = H - 40
        d.rounded_rectangle((x - 34, y0 - h, x + 34, y0), 26, fill=c); d.ellipse((x - 26, y0 - h - 58, x + 26, y0 - h - 6), fill=c)
        if up: d.line((x + 24, y0 - h + 20, x + 50 + 10 * math.sin(tg * 6 + i), y0 - h - 110), fill=c, width=16)

def others(d, xs, a=1.0):
    """silhouettes d'autres jeunes, en groupe, loin du héros"""
    for i, bx in enumerate(xs):
        c = mix(BG, (20, 22, 32), a)
        h = 170 + (i % 2) * 30
        d.rounded_rectangle((bx - 34, FEET - 40 - h, bx + 34, FEET - 40), 24, fill=c); d.ellipse((bx - 28, FEET - 40 - h - 60, bx + 28, FEET - 40 - h - 4), fill=c)

def series_banner(d, tg):
    """titre de la série de 0,5 s à 3,6 s : « ILS ONT FAILLI ABANDONNER — ÉPISODE 7 » (l'accroche passe d'abord)"""
    if tg > 3.6 or tg < 0.5: return
    a = min(1, (tg - 0.5) / 0.15) * (1 - ease((tg - 3.2) / 0.4))
    c = mix(BG, WHITE, a); g = mix(BG, GOLD, a)
    d.rounded_rectangle((90, 70, W - 90, 200), 22, fill=mix(BG, (80, 30, 30), a), outline=g, width=4)
    text(d, (W / 2, 115), "ILS ONT FAILLI ABANDONNER", fit("ILS ONT FAILLI ABANDONNER", 60, 860), c, BOLD)
    text(d, (W / 2, 168), "ÉPISODE 7", 40, g, MONO)

def kM(tg, name): return tg - M(name, 99) + 0.1
def pop(k, base, amp=0.3, dur=0.2): return int(base * (1 + amp * (1 - eout(max(0, k) / dur))))

def walk(img, d, x0, x1, by, s, u, k):
    x = lerp(x0, x1, min(1, max(0, u)))
    P(img, x, by, s, run_pose(k * 7) if 0 < u < 1 else "stand", facing=1 if x1 >= x0 else -1); shadow(d, x, by, s)
    return x

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    others(d, (W / 2 + 200, W / 2 + 290, W / 2 + 380), 1.0)
    P(img, W / 2 - 220, FEET, 260, "shy"); shadow(d, W / 2 - 220, FEET, 260)
    cold(img, tg, 0.5); d = ImageDraw.Draw(img)
    series_banner(d, tg)
    sc = 1 + 0.3 * (1 - eout((tg + 0.1) / 0.2))
    text(d, (W / 2, 430), "TROP", int(fit("TROP", 150, 1000) * sc), WHITE, BOLD, stroke=9, scol=BG)
    kk = tg - K["hook"] + 0.15
    if kk > 0:
        text(d, (W / 2, 600), "TIMIDE ?", pop(kk, fit("TIMIDE ?", 190, 1000), 0.5, 0.18), RED, BOLD, stroke=10, scol=BG)
        hit = max(0, 1 - kk / 0.25)
    kd = kM(tg, "caractere")
    if kd > 0: text(d, (W / 2, 780), "« PAS LE CARACTÈRE » ?", fit("« PAS LE CARACTÈRE » ?", 76, 900), GREY, BOLD, stroke=5, scol=BG)
    return dict(hit=hit, bg=0.0)

def s_intro(img, d, tg, k):
    hit = 0.0
    label(d, 300, "L'HISTOIRE VRAIE", k, 100, WHITE, "D'UN DÉFENSEUR", ACC)
    kr = kM(tg, "rejet"); kb = kM(tg, "brassard")
    if kr > 0: text(d, (W / 2, 560), "DU REJET", pop(kr, fit("DU REJET", 120, 980)), GREY, BOLD, stroke=7, scol=BG)
    if kb > 0:
        text(d, (W / 2, 700), "AU BRASSARD", pop(kb, fit("AU BRASSARD", 130, 980)), GOLD, BOLD, stroke=8, scol=BG)
        armband(d, W / 2, 940, 0.9, kb)
        if kb < 0.25: hit = 1 - kb / 0.25
    P(img, W / 2, FEET + 40, 230, "stand"); shadow(d, W / 2, FEET + 40, 230)
    return dict(hit=hit, bg=0.1)

def s_ville(img, d, tg, k):
    hit = 0.0
    kv = kM(tg, "vosges"); ks = kM(tg, "senegal")
    text(d, (W / 2, 300), "IL GRANDIT DANS", fit("IL GRANDIT DANS", 76, 980), WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 420), "UNE PETITE VILLE", pop(k, fit("UNE PETITE VILLE", 110, 980)), ACC, BOLD, stroke=7, scol=BG)
    if kv > 0: text(d, (W / 2, 540), "DE MONTAGNE", pop(kv, fit("DE MONTAGNE", 90, 980)), WHITE, BOLD, stroke=6, scol=BG)
    if ks > 0: text(d, (W / 2, 670), "FAMILLE VENUE DU SÉNÉGAL", fit("FAMILLE VENUE DU SÉNÉGAL", 56, 980), GOLD, BOLD, stroke=5, scol=BG)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    # il marche seul le long de la palissade, sac sur l'épaule
    u = min(1, k / 4.0)
    x = lerp(-80, W / 2 + 120, u)
    img.alpha_composite(bag(d, 0, 0, 0.55, 10), (int(x - 150), int(FEET - 330)))
    P(img, x, FEET, 230, run_pose(k * 6) if u < 1 else "shy"); shadow(d, x, FEET, 230)
    cold(img, tg, 0.35)
    return dict(hit=hit, bg=0.15)

def s_metz(img, d, tg, k):
    hit = 0.0
    kc = kM(tg, "centre"); kp = kM(tg, "prend")
    badge(d, 200, 300, "12 ANS", k, GOLD, 110)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    if kc > 0:
        text(d, (640, 280), "LE CENTRE DE", fit("LE CENTRE DE", 66, 620), WHITE, BOLD, stroke=5, scol=BG)
        text(d, (640, 360), "FORMATION", pop(kc, fit("FORMATION", 90, 620)), GOLD, BOLD, stroke=6, scol=BG)
    op = eout(min(1, max(0, kp + 0.2) / 0.5))
    door(d, W / 2 + 200, FEET - 10, 1.2, op)
    if kp > 0:
        hit = max(hit, stamp(img, "IL EST PRIS", (W / 2, 620), 120, -5, kp, GREEN)); d = ImageDraw.Draw(img)
    walk(img, d, 140, W / 2 + 60, FEET, 220, max(0, kp) / 0.9, k)
    return dict(hit=hit, bg=0.2)

def s_renvoi(img, d, tg, k):
    hit = 0.0
    kr = kM(tg, "renvoie"); ki = kM(tg, "introverti"); kn = kM(tg, "niveau")
    badge(d, W / 2, 300, "15 ANS", k, RED, 110)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    door(d, W / 2 + 230, FEET - 10, 1.2, max(0, 1 - max(0, kr) / 0.3))
    if kr > 0:
        hit = max(hit, stamp(img, "RENVOYÉ", (W / 2, 500), 150, -6, kr, RED)); d = ImageDraw.Draw(img)
    if ki > 0: text(d, (W / 2, 680), "« TROP INTROVERTI »", pop(ki, fit("« TROP INTROVERTI »", 90, 900), 0.15), WHITE, BOLD, stroke=6, scol=BG)
    if kn > 0: text(d, (W / 2, 800), "« PAS AU NIVEAU »", pop(kn, fit("« PAS AU NIVEAU »", 90, 900), 0.15), GREY, BOLD, stroke=6, scol=BG)
    # le sac tombe au sol
    u = eout(min(1, max(0, kr) / 0.5))
    img.alpha_composite(bag(d, 0, 0, 0.6, lerp(10, 80, u)), (int(W / 2 - 330), int(lerp(FEET - 340, FEET - 150, u))))
    P(img, W / 2 - 120, FEET, 240, "sad" if kr > 0 else "stand"); shadow(d, W / 2 - 120, FEET, 240)
    cold(img, tg, 0.6)
    return dict(hit=hit, bg=0.0)

def s_retour(img, d, tg, k):
    hit = 0.0
    kb = tg - K["build_start"] + 0.1; kl = kM(tg, "loin"); ki = kM(tg, "nimporte"); kc = kM(tg, "crampons")
    text(d, (W / 2, 290), "RETOUR AU PETIT CLUB", fit("RETOUR AU PETIT CLUB", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
    if kb > 0:
        text(d, (W / 2, 440), "3 ANS", pop(kb, fit("3 ANS", 170, 980)), RED, BOLD, stroke=8, scol=BG)
        if kb < 0.25: hit = 1 - kb / 0.25
    if kl > 0: text(d, (W / 2, 570), "LOIN DES CENTRES DE FORMATION", fit("LOIN DES CENTRES DE FORMATION", 60, 980), GREY, BOLD, stroke=5, scol=BG)
    if ki > 0: text(d, (W / 2, 700), typew("N'IMPORTE QUI AURAIT", ki, 26), fit("N'IMPORTE QUI AURAIT", 72, 980), WHITE, BOLD, stroke=5, scol=BG)
    if kc > -0.4:
        text(d, (W / 2, 790), typew("RANGÉ SES CRAMPONS…", kc + 0.4, 26), fit("RANGÉ SES CRAMPONS…", 82, 980), ACC, BOLD, stroke=6, scol=BG)
        boots(d, W / 2 + 230, FEET - 20, 0.9)
    # seul, tête basse, il pousse le ballon le long de la palissade sous la bruine
    ph = k * 2.2
    x = W / 2 - 200 + 60 * math.sin(k * 0.8)
    P(img, x, FEET, 230, run_pose(ph) if kc < 0 else "sad"); shadow(d, x, FEET, 230)
    ball(d, x + 110, FEET - 30, 30, WHITE, tg * 3)
    cold(img, tg, 1.0)
    return dict(hit=hit, bg=0.0)

def s_voix(img, d, tg, k):
    kb = tg - K["boom"]
    flash = 0.0
    kk = max(0.0, kb + 0.06)
    lit = eout(min(1, kk / 0.4))
    for i in range(4):
        if kk > i * 0.06: cone(img, 160 + i * 250, 1.0)
    d = ImageDraw.Draw(img)
    if kk < 0.4: flash = max(0, 0.95 - kk * 2.4)
    # il relève la tête et ouvre les bras : ondes de voix qui partent de lui
    u = eout(min(1, kk / 0.3))
    hx, hy = W / 2, FEET + 20 - 1.3 * 300
    waves(d, hx, hy, kk, 5, GOLD, 120, 620)
    burst(d, hx, hy, kk, 24, 460, GOLD, 3, 9)
    P(img, W / 2, FEET + 20, 300, blend_pose(POSES["shy"], POSES["wide"], u), glow=1.6); shadow(d, W / 2, FEET + 20, 300)
    hit = max(0, 1 - kk / 0.3)
    e = eout(kk / 0.22)
    x1 = lerp(-600, W / 2, e); x2 = lerp(W + 600, W / 2, e)
    for off, c in ((10, (255, 60, 80)), (-10, (80, 220, 255)), (0, WHITE)):
        o = off * (1 - e) + (off * 0.25 if off else 0)
        text(d, (x1 + o, 300), "SA VOIX,", fit("SA VOIX,", 150, 1000), c, BOLD, stroke=8 if c == WHITE else 0, scol=BG)
        kt = kM(tg, "terrain")
        text(d, (x2 - o, 470), "SUR LE TERRAIN !" if kt > -0.6 else "IL VA LA TROUVER", fit("SUR LE TERRAIN !", 130, 1000), c if c != WHITE else GOLD, BOLD, stroke=9 if c == WHITE else 0, scol=BG)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=0.2 + 0.6 * lit)

def s_pro(img, d, tg, k):
    hit = 0.0
    kt = kM(tg, "travaille"); kc = kM(tg, "confiance"); km = kM(tg, "metz2"); ks = kM(tg, "signe")
    if km <= 0:
        text(d, (W / 2, 290), "IL TRAVAILLE", pop(kt, fit("IL TRAVAILLE", 110, 980)), WHITE, BOLD, stroke=7, scol=BG)
        if kc > 0: text(d, (W / 2, 420), "IL PREND CONFIANCE", pop(kc, fit("IL PREND CONFIANCE", 90, 980)), GOLD, BOLD, stroke=6, scol=BG)
        # tacle glissé répété : il gagne le ballon
        ph = (k % 1.1) / 1.1
        x = lerp(W / 2 - 320, W / 2 + 200, eout(min(1, ph * 1.4)))
        P(img, x, FEET + 10, 230, "slide" if ph < 0.75 else "stand", rot=-62 if ph < 0.75 else 0, glow=1.2)
        bx = lerp(W / 2 + 360, W / 2 + 240, min(1, ph * 1.4)) if ph < 0.7 else W / 2 + 240 + (ph - 0.7) * 1200
        ball(d, bx, FEET - 20, 30, WHITE, tg * 9)
        for i in range(6):
            gx = x - 120 - i * 40; d.ellipse((gx - 18, FEET - 6, gx + 18, FEET + 10), fill=mix((60, 90, 50), (120, 110, 80), 0.5))
        if 0 < k < 0.25: hit = 1 - k / 0.25
        return dict(hit=hit, bg=0.45)
    text(d, (W / 2, 290), "LE CLUB QUI L'AVAIT RENVOYÉ", fit("LE CLUB QUI L'AVAIT RENVOYÉ", 70, 980), WHITE, BOLD, stroke=6, scol=BG)
    text(d, (W / 2, 400), "REVIENT LE CHERCHER", pop(km, fit("REVIENT LE CHERCHER", 96, 980)), GOLD, BOLD, stroke=7, scol=BG)
    if km < 0.25: hit = 1 - km / 0.25
    door(d, W / 2 + 230, FEET - 10, 1.2, eout(min(1, km / 0.5)), light=LIGHT)
    if ks > 0:
        badge(d, 200, 620, "19 ANS", ks, GOLD, 100)
        hit = max(hit, stamp(img, "CONTRAT PRO", (W / 2 + 80, 640), 120, -6, ks, GOLD)); d = ImageDraw.Draw(img)
    walk(img, d, 120, W / 2 + 100, FEET, 230, km / 1.2, k)
    return dict(hit=hit, bg=0.6)

STEPS = [(160, 1460), (420, 1300), (680, 1140), (920, 980)]
def s_naples(img, d, tg, k):
    hit = 0.0
    kg = kM(tg, "genk"); kn = kM(tg, "naples"); kd = kM(tg, "defenseur2"); kb = kM(tg, "brassard2")
    # escalier de carrière
    for i, (x, y) in enumerate(STEPS):
        d.rectangle((x - 130, y, x + 130, y + 40), fill=mix((60, 50, 50), GOLD, 0.3 + 0.2 * i))
    st = 0 if kn <= 0 else (1 if kd <= 0 else (2 if kb <= 0 else 3))
    x, y = STEPS[st]
    P(img, x, y, 200, "fist" if kb > 0 else "stand", glow=1.2)
    text(d, (W / 2, 290), "LA BELGIQUE" if kn <= 0 else "L'ITALIE", pop(k if kn <= 0 else kn, fit("LA BELGIQUE", 110, 980)), WHITE, BOLD, stroke=7, scol=BG)
    if kg > 0 and kn <= 0:
        trophy(d, W / 2 + 200, 760, 0.8 * (1 + 0.2 * (1 - eout(kg / 0.25))), GOLD)
        text(d, (W / 2, 420), "IL GAGNE LA COUPE", pop(kg, fit("IL GAGNE LA COUPE", 90, 980)), GOLD, BOLD, stroke=6, scol=BG)
        if kg < 0.25: hit = 1 - kg / 0.25
    if kd > 0 and kb <= 0:
        hit = max(hit, stamp(img, "MEILLEUR DÉFENSEUR", (W / 2, 470), 110, -5, kd, GOLD)); d = ImageDraw.Draw(img)
        text(d, (W / 2, 610), "DU CHAMPIONNAT", fit("DU CHAMPIONNAT", 70, 980), WHITE, BOLD, stroke=5, scol=BG)
    if kb > 0:
        text(d, (W / 2, 430), "LE « TROP TIMIDE »", fit("LE « TROP TIMIDE »", 80, 980), GREY, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 540), "PORTE LE BRASSARD", pop(kb, fit("PORTE LE BRASSARD", 90, 980)), GOLD, BOLD, stroke=7, scol=BG)
        armband(d, W / 2 - 200, 760, 0.8, kb)
        if kb < 0.25: hit = max(hit, 1 - kb / 0.25)
    if 0 < k < 0.25: hit = max(hit, 1 - k / 0.25)
    return dict(hit=hit, bg=0.75)

def s_afrique(img, d, tg, k):
    hit = 0.0; flash = 0.0
    ka = kM(tg, "afrique"); kc = kM(tg, "capitaine2"); kf = kM(tg, "finale"); km = kM(tg, "marque"); kp = kM(tg, "premier"); ks = kM(tg, "soulever")
    if kp > 0:
        crowd(d, tg, 1.0); confetti(d, kp)
        trophy(d, W / 2, 1060 - 120 * eout(min(1, max(0, ks) / 0.4)), 0.9, GOLD)
        P(img, W / 2, FEET - 40, 250, "up", glow=1.5)
        text(d, (W / 2, 300), "1er CAPITAINE", pop(kp, fit("1er CAPITAINE", 130, 980)), GOLD, BOLD, stroke=8, scol=BG)
        text(d, (W / 2, 430), "DE SON PAYS", fit("DE SON PAYS", 90, 980), WHITE, BOLD, stroke=6, scol=BG)
        if ks > 0: text(d, (W / 2, 550), "À SOULEVER LA COUPE", pop(ks, fit("À SOULEVER LA COUPE", 80, 980)), WHITE, BOLD, stroke=6, scol=BG)
        if kp < 0.25: hit = 1 - kp / 0.25
        return dict(hit=hit, bg=1.0)
    text(d, (W / 2, 290), "2022", pop(k, fit("2022", 150, 980)), GOLD, BOLD, stroke=8, scol=BG)
    if 0 < k < 0.25: hit = 1 - k / 0.25
    if ka > 0: text(d, (W / 2, 420), "COUPE D'AFRIQUE", pop(ka, fit("COUPE D'AFRIQUE", 100, 980)), WHITE, BOLD, stroke=7, scol=BG)
    if kc > 0 and kf <= 0:
        armband(d, W / 2, 700, 0.9, kc)
        text(d, (W / 2, 880), "CAPITAINE", pop(kc, fit("CAPITAINE", 120, 980)), GOLD, BOLD, stroke=7, scol=BG)
        if kc < 0.25: hit = max(hit, 1 - kc / 0.25)
        P(img, W / 2, FEET, 230, "point"); shadow(d, W / 2, FEET, 230)
        return dict(hit=hit, bg=0.85)
    goal(d, W / 2, FEET - 280, 0.9)
    if kf > 0:
        text(d, (W / 2, 540), "FINALE · TIRS AU BUT", fit("FINALE · TIRS AU BUT", 80, 980), WHITE, BOLD, stroke=6, scol=BG)
        u = min(1, max(0, km + 0.35) / 0.35)
        P(img, W / 2 - 60, FEET + 60, 230, "kick" if u > 0.1 else "stand"); shadow(d, W / 2 - 60, FEET + 60, 230)
        bx = lerp(W / 2 + 20, W / 2 + 280, eout(u)); by = lerp(FEET + 40, FEET - 520, eout(u))
        ball(d, bx, by, 30 - 8 * u, WHITE, tg * 10)
        if km > 0:
            hit = max(hit, stamp(img, "IL MARQUE !", (W / 2, 740), 150, -6, km, GOLD)); d = ImageDraw.Draw(img)
            flash = 0.35 * max(0, 1 - km / 0.3)
    return dict(hit=hit, flash=flash, bg=0.9)

def s_regard(img, d, tg, k):
    hit = 0.0
    kt = kM(tg, "timide3"); kl = kM(tg, "lever"); kp = kM(tg, "pays")
    text(d, (W / 2, 290), "LE GARÇON", fit("LE GARÇON", 110, 980), WHITE, BOLD, stroke=6, scol=BG)
    if kt > 0: text(d, (W / 2, 420), "QU'ON TROUVAIT TROP TIMIDE…", fit("QU'ON TROUVAIT TROP TIMIDE…", 66, 980), GREY if kl > 0 else RED, BOLD, stroke=6, scol=BG)
    if kl > 0:
        text(d, (W / 2, 580), "A FAIT LEVER", pop(kl, fit("A FAIT LEVER", 120, 980)), GOLD, BOLD, stroke=8, scol=BG)
        if kl < 0.25: hit = 1 - kl / 0.25
    if kp > 0:
        hit = max(hit, stamp(img, "TOUT UN PAYS", (W / 2, 750), 130, -4, kp, WHITE)); d = ImageDraw.Draw(img)
    crowd(d, tg, 1.0, up_all=kl > 0)
    P(img, W / 2, FEET - 120, 250, "wide" if kl > 0 else "shy", glow=1.3)
    if kl > 0: waves(d, W / 2, FEET - 120 - 1.3 * 250, kl, 4, GOLD, 100, 500)
    return dict(hit=hit, bg=1.0)

def s_you(img, d, tg, k):
    dim(img, 0.55); d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), ACC, BOLD, stroke=6, scol=BG)
    kr = kM(tg, "remarque"); kp = tg - K["arms_up"] + 0.1
    hit = 0.0
    if kr > -0.3: text(d, (W / 2, 560), "TU ATTENDS QU'ON TE REMARQUE…", fit("TU ATTENDS QU'ON TE REMARQUE…", 66, 900), GREY, BOLD, stroke=6, scol=BG)
    P(img, W / 2, FEET - 80, 230, "wide" if kp > 0 else "shy", glow=1.2)
    if kp > 0:
        waves(d, W / 2, FEET - 80 - 1.3 * 230, kp, 4, GOLD, 90, 460)
        text(d, (W / 2, 680), "OU TU TE FAIS ENTENDRE ?", pop(kp, fit("OU TU TE FAIS ENTENDRE ?", 84, 860), 0.1), GOLD, BOLD, stroke=7, scol=BG)
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
        text(d, (W / 2, 660), "DEMAIN · ÉPISODE 8", fit("DEMAIN · ÉPISODE 8", 74, 980), GOLD, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 770), typew("ENCORE GARDIEN DE BUT À 14 ANS…", kd, 34), fit("ENCORE GARDIEN DE BUT À 14 ANS…", 60, 980), WHITE, BOLD, stroke=5, scol=BG)
    kr = kM(tg, "record")
    if kr > 0: hit = max(hit, stamp(img, "TRANSFERT RECORD", (W / 2, 940), 110, -6, kr, GOLD)); d = ImageDraw.Draw(img)
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
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (110, 40, 40), a), BOLD)
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

_FUN = {"hook": s_hook, "intro": s_intro, "ville": s_ville, "metz": s_metz, "renvoi": s_renvoi, "retour": s_retour, "voix": s_voix,
        "pro": s_pro, "naples": s_naples, "afrique": s_afrique, "regard": s_regard, "you": s_you, "abonne": s_abonne, "question": s_question, "logo": s_logo}
DUSTAMT = {"hook": 0.4, "voix": 1.0, "naples": 1.0, "afrique": 1.0, "regard": 1.0, "question": 0.4, "logo": 0.2}
def _wrap(name, f):
    def g(img, d, tg, k):
        dust(d, tg, DUSTAMT.get(name, 0.5)); return f(img, d, tg, k)
    return g
SCENES = {n: _wrap(n, f) for n, f in _FUN.items()}
BGLEVEL = {"hook": 0.0, "intro": 0.1, "ville": 0.15, "metz": 0.2, "renvoi": 0.0, "retour": 0.0, "voix": 0.8, "pro": 0.45,
           "naples": 0.75, "afrique": 0.9, "regard": 1.0, "you": 0.2, "abonne": 0.0, "question": 0.0, "logo": 0.0}


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

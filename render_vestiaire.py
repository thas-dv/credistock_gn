# -*- coding: utf-8 -*-
"""Style « vestiaire » (récap du dimanche) : vestiaire la nuit, grand tableau noir tactique où les leçons s écrivent à la craie,
casiers génériques, banc, joueur en silhouette générique (maillot blanc, sans numéro). Types : hook board l1 l2 l3 l4 l5 recap slam you question logo.
Usage : python3 render_vestiaire.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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


# palette « vestiaire » : vestiaire la nuit, grand tableau noir tactique où les leçons s'écrivent à la craie
WALL = (22, 26, 30); WALL2 = (52, 58, 62); BOARD = (20, 40, 34); BOARD2 = (34, 66, 54); WOOD = (96, 62, 36)
CHALK = (236, 238, 228); CYEL = (250, 222, 110); CRED = (240, 98, 84); CBLUE = (130, 200, 240)
LOCK = (44, 52, 60); LOCK2 = (90, 102, 112); TILE = (34, 38, 42)
ORANGE = CYEL; PITCH = TILE; ICE = CBLUE
JER = (236, 236, 242)
BX0, BY0, BX1, BY1 = 70, 150, W - 70, 1190     # tableau
FEET = 1650

def make_bg(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(H):
        d.line((0, y, W, y), fill=mix(mix(WALL, WALL2, 0.25 * lit), (10, 12, 14), 0.4 * (y / H)))
    # casiers sous le tableau (génériques, sans inscription)
    for i in range(9):
        x = 20 + i * 116
        d.rectangle((x, 1230, x + 108, 1560), fill=mix(LOCK, LOCK2, 0.5 * lit), outline=mix((20, 24, 28), LOCK2, 0.3), width=4)
        for j in range(3): d.line((x + 30, 1260 + j * 16, x + 78, 1260 + j * 16), fill=mix((24, 28, 32), (60, 70, 78), lit), width=5)
        d.ellipse((x + 86, 1390, x + 98, 1402), fill=mix((90, 96, 100), (190, 196, 200), lit))
    # carrelage du sol
    d.rectangle((0, 1560, W, H), fill=mix(TILE, (80, 86, 92), 0.6 * lit))
    for y in range(1560, H, 70): d.line((0, y, W, y), fill=mix((20, 22, 26), (60, 64, 70), lit), width=2)
    for i in range(-10, 20):
        x0 = W / 2 + i * 120; d.line((W / 2 + i * 70, 1560, x0 + i * 60, H), fill=mix((20, 22, 26), (60, 64, 70), lit), width=2)
    # banc en bois
    d.rectangle((90, 1600, W - 90, 1640), fill=mix(WOOD, (170, 120, 76), 0.5 * lit))
    for x in (130, W / 2 - 10, W - 150): d.rectangle((x, 1640, x + 22, 1760), fill=(36, 28, 24))
    # tableau noir : cadre bois + ardoise
    d.rectangle((BX0 - 26, BY0 - 26, BX1 + 26, BY1 + 26), fill=mix((70, 46, 28), WOOD, 0.6 + 0.4 * lit))
    for y in range(BY0, BY1):
        u = (y - BY0) / (BY1 - BY0)
        d.line((BX0, y, BX1, y), fill=mix(mix(BOARD, BOARD2, 0.25 + 0.6 * lit), BOARD, abs(u - 0.4)))
    rng = np.random.default_rng(4)   # traces de craie effacée
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for _ in range(26):
        x, y = rng.uniform(BX0 + 60, BX1 - 60), rng.uniform(BY0 + 60, BY1 - 60); w = rng.uniform(80, 300)
        dl.ellipse((x - w, y - 30, x + w, y + 30), fill=(220, 230, 220, int(rng.uniform(8, 20))))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(img)
    d.rectangle((BX0 - 30, BY1 + 18, BX1 + 30, BY1 + 40), fill=mix((60, 40, 24), WOOD, 0.7))   # rebord
    d.rectangle((BX0 + 80, BY1 + 6, BX0 + 150, BY1 + 20), fill=CHALK); d.rectangle((BX0 + 180, BY1 + 8, BX0 + 220, BY1 + 20), fill=CYEL)
    # lampe de plafond + cône de lumière
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(W / 2 - 80, 0), (W / 2 + 80, 0), (W + 200, H), (-200, H)], fill=(255, 240, 200, int(18 + 40 * lit)))
    dl.ellipse((W / 2 - 300, -120, W / 2 + 300, 160), fill=(255, 244, 210, int(60 + 80 * lit)))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(50)))
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

POSES["sit"] = dict(t=-4, la=(-25, -40), ra=(25, 40), ll=(-85, 88), rl=(-78, 82))
POSES["sad"] = dict(t=-25, la=(-20, -60), ra=(20, 60), ll=(-85, 88), rl=(-78, 82))
POSES["point"] = dict(t=0, la=(-12, 6), ra=(120, -20), ll=(-5, 0), rl=(5, 0))

def P(img, x, y, s, pose, **kw):
    kw.setdefault("num", ""); kw.setdefault("jersey", JER)
    player(img, x, y, s, pose, **kw)

# ---------- craie
_CH = {}
def chalk_layer(s, size, col, font=BOLD):
    key = (s, int(size), col, font)
    if key not in _CH:
        f = F(font, size); dd = ImageDraw.Draw(Image.new("L", (4, 4)))
        l, t, r, b = dd.textbbox((0, 0), s, font=f)
        L = Image.new("RGBA", (r - l + 20, b - t + 20), (0, 0, 0, 0))
        ImageDraw.Draw(L).text((10 - l, 10 - t), s, font=f, fill=col + (255,))
        a = np.asarray(L).copy(); rng = np.random.default_rng(len(s) * 7 + int(size))
        noise = rng.random(a.shape[:2])
        a[..., 3] = (a[..., 3] * np.clip(0.55 + 0.6 * noise, 0, 1) * (noise > 0.12)).astype(np.uint8)
        _CH[key] = Image.fromarray(a)
    return _CH[key]

def chalk(img, xy, s, size, col, k, cps=22, maxw=900, anchor="m", font=BOLD):
    """texte écrit à la craie, révélé de gauche à droite (k = temps depuis le début)."""
    if k <= 0 or not s: return
    size = fit(s, size, maxw, font)
    L = chalk_layer(s, size, col, font)
    u = min(1.0, k * cps / max(1, len(s)))
    wv = int(L.width * u)
    if wv <= 0: return
    Lc = L.crop((0, 0, wv, L.height))
    x = xy[0] - L.width / 2 if anchor == "m" else xy[0]
    img.alpha_composite(Lc, (int(x), int(xy[1] - L.height / 2)))

def cline(d, p, q, k, col=CHALK, w=7, dur=0.4):
    if k <= 0: return
    u = eout(k / dur); d.line((p[0], p[1], lerp(p[0], q[0], u), lerp(p[1], q[1], u)), fill=col, width=w)

def ccircle(d, cx, cy, r, k, col=CYEL, w=8, dur=0.45):
    if k <= 0: return
    u = eout(k / dur); d.arc((cx - r, cy - r * 0.8, cx + r, cy + r * 0.8), -100, -100 + 370 * u, fill=col, width=w)

def dust(d, x, y, k, n=40, r=500, seed=0):
    if k <= 0 or k > 1.2: return
    rng = np.random.default_rng(seed); e = eout(k / 0.9); a = 1 - k / 1.2
    for i in range(n):
        ang = rng.uniform(0, 2 * math.pi); rr = r * e * rng.uniform(0.3, 1.0); s = rng.uniform(4, 16) * (1 + k)
        px, py = x + rr * math.cos(ang), y + rr * math.sin(ang) * 0.7
        d.ellipse((px - s, py - s, px + s, py + s), fill=mix(BOARD, CHALK, 0.7 * a))

def num_badge(img, d, n, k, x=210, y=300):
    if k <= 0: return
    ccircle(d, x, y, 95, k, CYEL, 9)
    chalk(img, (x, y + 6), str(n), 150, CHALK, k * 3)

def lesson_head(img, d, n, word, kw, k):
    num_badge(img, d, n, k)
    chalk(img, (300, 250), "LEÇON N°" + str(n), 50, CBLUE, k, 30, 600, anchor="l")
    sc = 1 + 0.4 * (1 - eout(kw / 0.18)) if kw > 0 else 1
    if kw > 0: chalk(img, (330 + 0.5 * min(620, 0), 355), word, int(110 * sc), CYEL, kw * 1.6, 30, 640, anchor="l")
    return max(0.0, 1 - kw / 0.25) if 0 < kw < 0.25 else 0.0

def nail_letters(d, x, y, n, k):
    d.line((x, y - 10, x, y + 160), fill=(170, 170, 176), width=6); d.ellipse((x - 12, y - 22, x + 12, y), fill=(190, 190, 196))
    for i in range(n):
        if k - i * 0.12 <= 0: break
        a = (i - n / 2) * 6
        L = Image.new("RGBA", (220, 280), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.rectangle((10, 10, 210, 270), fill=(236, 230, 214, 255), outline=(150, 140, 120, 255), width=3)
        for j in range(6): dl.line((30, 60 + j * 32, 190 - (j % 2) * 40, 60 + j * 32), fill=(120, 120, 130, 255), width=4)
        dl.text((110, 230), "NON", font=F(BOLD, 44), fill=CRED + (255,), anchor="mm")
        L = L.rotate(a, resample=Image.BICUBIC, expand=True)
        d._image.alpha_composite(L, (int(x - L.width / 2 + i * 6), int(y + 30 + i * 8)))

def trash(d, cx, by, s):
    c = (70, 76, 86)
    d.polygon([(cx - 0.5 * s, by - 1.1 * s), (cx + 0.5 * s, by - 1.1 * s), (cx + 0.4 * s, by), (cx - 0.4 * s, by)], fill=c)
    for i in range(5):
        x = cx - 0.3 * s + i * 0.15 * s; d.line((x, by - 1.0 * s, x, by - 0.08 * s), fill=(40, 44, 50), width=5)
    d.rounded_rectangle((cx - 0.56 * s, by - 1.18 * s, cx + 0.56 * s, by - 1.06 * s), 8, fill=(110, 116, 126))

def book(d, cx, cy, s, col=CYEL):
    d.polygon([(cx - 1.0 * s, cy - 0.55 * s), (cx, cy - 0.4 * s), (cx + 1.0 * s, cy - 0.55 * s), (cx + 1.0 * s, cy + 0.6 * s), (cx, cy + 0.75 * s), (cx - 1.0 * s, cy + 0.6 * s)], outline=col, width=8)
    d.line((cx, cy - 0.4 * s, cx, cy + 0.75 * s), fill=col, width=8)
    for j in range(4):
        y = cy - 0.2 * s + j * 0.22 * s
        d.line((cx - 0.8 * s, y, cx - 0.15 * s, y + 0.05 * s), fill=CHALK, width=5); d.line((cx + 0.15 * s, y + 0.05 * s, cx + 0.8 * s, y), fill=CHALK, width=5)

def chalk_bus(d, x, y, s, tg):
    w, h = 420 * s, 170 * s
    d.rounded_rectangle((x, y - h, x + w, y), int(24 * s), outline=CHALK, width=7)
    for i in range(5):
        wx = x + 26 * s + i * 76 * s; d.rectangle((wx, y - 0.85 * h, wx + 58 * s, y - 0.45 * h), outline=CHALK, width=5)
    for wx in (x + 90 * s, x + w - 90 * s):
        r = 38 * s; d.ellipse((wx - r, y - r * 0.4, wx + r, y + r * 1.6), outline=CHALK, width=6)
        a = tg * 9; d.line((wx, y + r * 0.6, wx + r * 0.8 * math.cos(a), y + r * 0.6 + r * 0.8 * math.sin(a)), fill=CHALK, width=4)
    for j in range(3): d.line((x - 40 - j * 50, y - 40 - j * 30, x - 120 - j * 50, y - 40 - j * 30), fill=mix(BOARD, CHALK, 0.6), width=5)

def chalk_trophy(d, cx, cy, s, col=CYEL, k=1.0):
    if k <= 0: return
    q = lambda px, py: (cx + px * s, cy + py * s)
    pts = [q(-120, -230), q(120, -230), q(80, -60), q(25, -20), q(25, 50), q(80, 90), q(-80, 90), q(-25, 50), q(-25, -20), q(-80, -60), q(-120, -230)]
    n = max(2, int(len(pts) * min(1, k / 0.5)))
    d.line(pts[:n], fill=col, width=9, joint="curve")
    if k > 0.4:
        d.arc((cx - 190 * s, cy - 230 * s, cx - 70 * s, cy - 90 * s), 90, 270, fill=col, width=9)
        d.arc((cx + 70 * s, cy - 230 * s, cx + 190 * s, cy - 90 * s), 270, 90, fill=col, width=9)

def counter(d, x, y, lab, n, col, size=180):
    text(d, (x, y), str(n), size, col, BOLD); text(d, (x, y + size * 0.72), lab, 52, CHALK, MONO)

LESSONS = [("TROP TARD ?", "tard"), ("REFUSÉ", "refusé1"), ("TROP LOIN", "loin"), ("TROP FRÊLE", "frele"), ("RECALÉ", "recale")]

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    chalk(img, (W / 2, 520), "« C'EST PAS", 120, CHALK, k - 0.6, 18)
    chalk(img, (W / 2, 690), "POUR TOI »", 130, CHALK, k - M("pour", 1.2) + 0.2, 18)
    kh = tg - K["hook"]
    if kh > 0:
        ccircle(d, W / 2, 610, 470, kh, CRED, 10, 0.5)
        text(d, (W / 2, 950), "?", int(200 * (1 + 0.5 * (1 - eout(kh / 0.2)))), CRED, BOLD)
        if kh < 0.25: hit = 1 - kh / 0.25
    P(img, W / 2, 1765, 240, "sad", glow=0.7)
    return dict(hit=hit, bg=0.15)

def s_board(img, d, tg, k):
    hit = 0.0
    chalk(img, (W / 2, 280), "CETTE SEMAINE", 70, CBLUE, k, 26)
    k5 = tg - M("cinq1", SC["board"] + 0.8) + 0.1
    if k5 > 0:
        chalk(img, (W / 2, 420), "5 HISTOIRES", 120, CHALK, k5 * 1.5, 30)
        if k5 < 0.2: hit = 1 - k5 / 0.2
    ks = tg - M("sous", 99) + 0.2
    if ks > 0: chalk(img, (W / 2, 560), "SOUS-ESTIMÉS", 96, CRED, ks * 1.5, 30)
    kl = tg - M("lecons", 99) + 0.2
    if kl > 0:
        chalk(img, (W / 2, 720), "5 LEÇONS", 130, CYEL, kl * 2, 30); ccircle(d, W / 2, 720, 330, kl - 0.3, CYEL, 8)
        for i in range(5):
            y = 880 + i * 58; chalk(img, (300, y), f"{i + 1}.", 46, CHALK, kl - 0.2 - i * 0.08, 40, anchor="l")
            cline(d, (370, y + 18), (780, y + 18), kl - 0.25 - i * 0.08, mix(BOARD, CHALK, 0.6), 4)
        if kl < 0.25: hit = max(hit, 1 - kl / 0.25)
    P(img, W / 2, 1765, 240, "sit")
    return dict(hit=hit, bg=0.3 + 0.4 * (kl > 0))

def s_l1(img, d, tg, k):
    hit = lesson_head(img, d, 1, "TROP TARD ?", tg - M("tard", 99) + 0.1, k)
    k21 = tg - M("vingtun", 99) + 0.15
    if k21 > 0:
        cline(d, (150, 760), (930, 760), k21, CHALK, 8, 0.8)
        d.polygon([(930, 735), (980, 760), (930, 785)], fill=CHALK) if k21 > 0.8 else None
        d.ellipse((230, 740, 270, 780), fill=CBLUE)
        chalk(img, (250, 640), "21 ANS", 80, CBLUE, k21 * 2, 30); chalk(img, (250, 850), "PRO", 64, CHALK, k21 * 2 - 0.4, 30)
        if k21 < 0.2: hit = max(hit, 1 - k21 / 0.2)
    k34 = tg - M("trentequatre", 99) + 0.15
    if k34 > 0:
        d.ellipse((790, 740, 830, 780), fill=CYEL)
        chalk(img, (810, 640), "34 ANS", 80, CYEL, k34 * 2, 30)
        chalk(img, (720, 870), "CHAMPION D'EUROPE", 56, CHALK, (tg - M("champion1", 99) + 0.1) * 1.5, 30, 560)
        chalk_trophy(d, 810, 1080, 0.55, CYEL, tg - M("champion1", 99))
        if k34 < 0.2: hit = max(hit, 1 - k34 / 0.2)
    kj = tg - M("jamais1", 99) + 0.1
    if kj > 0: hit = max(hit, stamp(img, "JAMAIS TROP TARD", (W / 2 - 150, 1050), 76, -6, kj, CRED))
    P(img, 170, 1745, 200, "sit")
    return dict(hit=hit, bg=0.75)

def s_l2(img, d, tg, k):
    hit = lesson_head(img, d, 2, "REFUSÉ", tg - M("refuse1", 99) + 0.1, k)
    kn = tg - M("clou", 99) + 0.4
    if kn > 0: nail_letters(d, 270, 520, 5, kn * 2.5)
    kp = tg - M("poubelle", 99) + 0.3
    if kp > 0:
        trash(d, 760, 1000, 220)
        if tg < M("recupere", 99): book(d, 760, lerp(560, 760, eout(kp / 0.5)), 90, CHALK)
    kr = tg - M("recupere", 99) + 0.1
    if kr > 0:
        book(d, 760, lerp(760, 600, eout(kr / 0.5)), 110 * (1 + 0.2 * (1 - eout(kr / 0.3))), CYEL)
        if kr < 0.25: hit = max(hit, 1 - kr / 0.25)
    kc = tg - M("carriere", 99) + 0.1
    if kc > 0: chalk(img, (W / 2, 1100), "UN REFUS ≠ LA FIN", 80, CYEL, kc * 1.5, 30)
    return dict(hit=hit, bg=0.75)

def s_l3(img, d, tg, k):
    hit = lesson_head(img, d, 3, "TROP LOIN", tg - M("loin", 99) + 0.1, k)
    k14 = tg - M("quatorze", 99) + 0.1
    if k14 > 0 and tg < M("banc", 99) - 0.2:
        badge(d, 230, 500, "14 ANS", k14, CBLUE, 110)
        chalk_bus(d, lerp(BX1, 380, eout(k14 / 2.0)), 760, 1.0, tg)
        k10 = tg - M("dix", 99) + 0.1
        if k10 > 0:
            chalk(img, (W / 2, 980), "≈ 10 H DE BUS / JOUR", 84, CYEL, k10 * 2, 30)
            if k10 < 0.2: hit = max(hit, 1 - k10 / 0.2)
    elif k14 > 0:
        steps = [("LE BANC", M("banc", 99), CHALK, 560), ("LE PRÊT", M("pret", 99), CHALK, 720), ("PLUS FORT", M("fort", 99), CYEL, 900)]
        for i, (s, tk, c, y) in enumerate(steps):
            kk = tg - tk + 0.15
            if kk <= 0: continue
            chalk(img, (W / 2, y), s, 110 if i == 2 else 90, c, kk * 2, 30)
            if i < 2: cline(d, (W / 2, y + 60), (W / 2, y + 110), kk - 0.3, mix(BOARD, CHALK, 0.6), 6)
            if kk < 0.2: hit = max(hit, 1 - kk / 0.2)
        kd = tg - M("distance", 99) + 0.1
        if kd > 0: chalk(img, (W / 2, 1090), "LA DISTANCE NE DÉCIDE PAS", 60, CBLUE, kd * 1.5, 34)
    return dict(hit=hit, bg=0.75)

def s_l4(img, d, tg, k):
    hit = lesson_head(img, d, 4, "TROP FRÊLE", tg - M("frele", 99) + 0.1, k)
    kc = tg - M("champion2", 99) + 0.1
    if kc <= 0:
        # silhouette fine dessinée à la craie
        x, y = W / 2, 1000
        d.ellipse((x - 34, y - 360, x + 34, y - 292), outline=CHALK, width=6)
        for p, q in [((x, y - 290), (x, y - 120)), ((x, y - 250), (x - 70, y - 160)), ((x, y - 250), (x + 70, y - 160)), ((x, y - 120), (x - 50, y)), ((x, y - 120), (x + 50, y))]:
            d.line((p, q), fill=CHALK, width=6)
        k18 = tg - M("dixhuit", 99) + 0.1
        if k18 > 0:
            chalk(img, (W / 2, 1110), "AMATEUR À 18 ANS", 76, CBLUE, k18 * 2, 30)
            if k18 < 0.2: hit = max(hit, 1 - k18 / 0.2)
        kj = tg - M("juge", 99) + 0.1
        if kj > 0: hit = max(hit, stamp(img, "JUGÉ TROP FRÊLE", (W / 2, 560), 70, 6, kj, CRED))
    else:
        chalk_trophy(d, W / 2, 870, 0.9, CYEL, kc)
        chalk(img, (W / 2, 1010), "CHAMPION", 100, CYEL, kc * 2, 30); chalk(img, (W / 2, 1110), "D'ANGLETERRE", 76, CHALK, kc * 2 - 0.3, 30)
        if kc < 0.25: hit = max(hit, 1 - kc / 0.25)
    kg = tg - M("gabarit", 99) + 0.1
    if kg > 0:
        dim(img, 0.25); d = ImageDraw.Draw(img)
        stamp(img, "TON GABARIT NE DÉCIDE PAS", (W / 2, 500), 60, -4, kg, CHALK)
    return dict(hit=hit, bg=0.75)

def s_l5(img, d, tg, k):
    hit = lesson_head(img, d, 5, "RECALÉ", tg - M("recale", 99) + 0.1, k)
    t27 = M("vingtsept", 99)
    if tg < t27 - 0.15:
        ke = tg - M("recale2", 99) + 0.1
        if ke > 0: hit = max(hit, stamp(img, "RECALÉ À UN ESSAI", (W / 2, 600), 84, -5, ke, CRED))
        kz = tg - M("zero", 99) + 0.1
        if kz > 0:
            text(d, (W / 2, 830), "0 BUT", int(150 * (1 + 0.3 * (1 - eout(kz / 0.2)))), CHALK, BOLD)
            chalk(img, (W / 2, 960), "1re SAISON PRO", 64, CBLUE, kz * 1.5 - 0.3, 30)
            if kz < 0.2: hit = max(hit, 1 - kz / 0.2)
    else:
        k27 = tg - t27 + 0.1
        badge(d, W / 2, 560, "27 ANS", k27, CBLUE, 120)
        if k27 < 0.25: hit = max(hit, 1 - k27 / 0.25)
        kb = tg - M("vingthuit", 99) + 0.15
        if kb > 0:
            counter(d, 300, 840, "BUTS", min(28, int(eout(kb / 0.6) * 28)), CYEL)
            if 0.55 < kb < 0.8: hit = max(hit, 1 - (kb - 0.55) / 0.25)
        km = tg - M("vingthuit2", 99) + 0.1
        if km > 0: counter(d, 780, 840, "MATCHS", 28, CHALK)
    return dict(hit=hit, bg=0.8)

def s_recap(img, d, tg, k):
    hit = 0.0
    for i, (w, mk) in enumerate(LESSONS):
        kk = k - i * 0.18
        y = 300 + i * 120
        chalk(img, (170, y), f"{i + 1}", 80, CYEL, kk * 3, 30, anchor="l")
        chalk(img, (270, y), w, 80, CHALK, kk * 2, 40, 640, anchor="l")
        cline(d, (880, y - 10), (910, y + 20), kk - 0.4, CYEL, 8, 0.15); cline(d, (910, y + 20), (970, y - 40), kk - 0.55, CYEL, 8, 0.2)
    kp = tg - M("personne", SC["recap"]) + 0.1
    if kp > 0: chalk(img, (W / 2, 960), "PERSONNE NE CROYAIT EN EUX", 64, CBLUE, kp * 1.2, 34)
    for s, mk, y in [("PAS DE CHANCE", "chance", 1070), ("PAS DE RACCOURCI", "raccourci", 1150)]:
        kk = tg - M(mk, 99) + 0.2
        if kk > 0:
            chalk(img, (W / 2, y), s, 60, CHALK, kk * 2, 34)
            cline(d, (W / 2 - 300, y), (W / 2 + 300, y), kk - 0.35, CRED, 8, 0.2)
            if 0.35 < kk < 0.55: hit = max(hit, 1 - (kk - 0.35) / 0.2)
    P(img, W / 2, 1755, 220, "sit")
    return dict(hit=hit, bg=0.7)

def s_slam(img, d, tg, k):
    kb = tg - K["boom"]; hit = 0.0; flash = 0.0; bgl = 0.4
    if kb < -0.08:
        chalk(img, (W / 2, 520), "ILS ONT...", 130, CHALK, k * 2, 20)
        pose = POSES["sit"]
    else:
        kk = kb + 0.08; bgl = 1.0
        dust(d, W / 2, 700, kk, 60, 650, 3)
        sc = 1 + 1.0 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 420), "ILS ONT", 110, CHALK, BOLD, stroke=6, scol=BOARD)
        text(d, (W / 2, 620), "REFUSÉ", int(fit("REFUSÉ", 230, 960) * sc), CYEL, BOLD, stroke=10, scol=BOARD)
        text(d, (W / 2, 830), "D'ARRÊTER !", int(fit("D'ARRÊTER !", 150, 960) * sc), CHALK, BOLD, stroke=8, scol=BOARD)
        pose = blend_pose(POSES["stand"], POSES["up"], eout(kk / 0.25))
        flash = max(0, 0.9 - kb * 4) if kb > 0 else 0
        hit = max(0, 1 - kk / 0.3)
    P(img, W / 2, 1780 if kb < -0.08 else 1790, 260 if kb < -0.08 else 300, pose, glow=1.0)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash, bg=bgl)

def s_you(img, d, tg, k):
    dim(img, 0.35); d = ImageDraw.Draw(img)
    text(d, (W / 2, 330), "ET TOI ?", int(150 + 40 * (1 - eout(k / 0.2))), CYEL, BOLD, stroke=6, scol=BOARD)
    kl = tg - M("laisser", 99) + 0.1
    if kl > 0: chalk(img, (W / 2, 560), "LES AUTRES DÉCIDENT ?", 80, CHALK, kl * 1.5, 30)
    kp = tg - M("place", 99) + 0.1
    hit = stamp(img, "C'EST TOI QUI DÉCIDES", (W / 2, 820), 80, -5, kp, CRED) if kp > 0 else 0.0
    P(img, W / 2, 1790, 280, "point")
    return dict(hit=hit, bg=0.5)

def s_question(img, d, tg, k):
    dim(img, 0.55); d = ImageDraw.Draw(img)
    pulse = 0.0
    for tk in TJ["q_pulses"]:
        dd = tg - tk
        if 0 <= dd < 0.5: pulse = max(pulse, math.exp(-dd * 7))
    a = 1.0; de = tg - K["q_end"]
    if de > 0: a = max(0.0, 1 - de / 0.8)
    kv = tg - SC["question"]
    text(d, (W / 2, 760), "?", int(210 * (1 + 0.08 * pulse)), mix(BG, CYEL, a), BOLD)
    chalk(img, (W / 2, 610), "TON IDOLE", 70, mix(BG, CHALK, a), kv * 2, 30)
    cats = [("SPORT", "sport", 330, 885), ("BUSINESS", "business", 750, 885), ("MUSIQUE", "musique", 330, 960), ("SCIENCE", "science", 750, 960)]
    for lab, mk, x, y in cats:
        kc = tg - M(mk, 99) + 0.05
        if kc > 0:
            sc = 1 + 0.35 * (1 - eout(kc / 0.15))
            text(d, (x, y), lab, int(58 * sc), mix(BG, CHALK, a), BOLD)
    kd = tg - M("domaine", 99) + 0.1
    if kd > 0:
        text(d, (W / 2, 1035), "N'IMPORTE QUEL DOMAINE", fit("N'IMPORTE QUEL DOMAINE", 54, 900), mix(BG, CYEL, a), BOLD)
    return dict(hit=0.5 * pulse, bg=0.3)

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

SCENES = {"hook": s_hook, "board": s_board, "l1": s_l1, "l2": s_l2, "l3": s_l3, "l4": s_l4, "l5": s_l5,
          "recap": s_recap, "slam": s_slam, "you": s_you, "question": s_question, "logo": s_logo}
BGLEVEL = {"hook": 0.15, "board": 0.3, "l1": 0.75, "l2": 0.75, "l3": 0.75, "l4": 0.75, "l5": 0.8, "recap": 0.7,
           "slam": 0.4, "you": 0.5, "question": 0.3, "logo": 0.0}

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

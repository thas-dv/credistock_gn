# -*- coding: utf-8 -*-
"""Style « écrivain » : bureau de nuit dans une caravane (lampe ambrée, machine à écrire, lettres de refus), écrivain en silhouette.
Types : hook letters nail trailer stamps trash slam deal books you question logo ("marks" = temps de mots nommés).
Usage : python3 render_ecrivain.py timing_voix.json video_brut.mp4 [t_from t_to every]"""
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

# --------------------------------------------------------------- palette « écrivain » (bureau de nuit, lampe ambrée)
BG = (7, 9, 18); WALL = (20, 24, 40); WALL2 = (28, 32, 52); WOOD = (58, 36, 22); WOOD2 = (84, 54, 30)
AMBER = (255, 176, 64); ORANGE = AMBER; PAPER = (242, 232, 206); INK = (30, 26, 34); RED = (226, 46, 42)
GREEN = (40, 190, 110); GOLD = (246, 196, 70); WHITE = (246, 244, 236); GREY = (120, 124, 140); DARK = (36, 40, 56)
SIL = (8, 9, 14); BLUE = (70, 110, 200)

DESK_Y = 1250   # plateau du bureau

def make_room(lit):
    img = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(img)
    for y in range(0, DESK_Y):   # mur lambrissé de la caravane
        u = y / DESK_Y; d.line((0, y, W, y), fill=mix(BG, WALL, 0.4 + 0.6 * u))
    for x in range(0, W, 120):
        d.line((x, 0, x, DESK_Y), fill=mix(BG, WALL2, 0.5 + 0.3 * lit), width=3)
    # fenêtre ronde (hublot de caravane) avec lune et étoiles
    wx, wy, wr = 840, 880, 125
    d.ellipse((wx - wr - 18, wy - wr - 18, wx + wr + 18, wy + wr + 18), fill=(46, 50, 70))
    d.ellipse((wx - wr, wy - wr, wx + wr, wy + wr), fill=(10, 16, 38))
    rng = np.random.default_rng(4)
    for _ in range(40):
        a = rng.uniform(0, 2 * math.pi); r = wr * math.sqrt(rng.random()) * 0.95
        x, y = wx + r * math.cos(a), wy + r * math.sin(a); s = rng.uniform(1, 3)
        d.ellipse((x - s, y - s, x + s, y + s), fill=(200, 210, 240))
    d.ellipse((wx + 20, wy - 90, wx + 100, wy - 10), fill=(236, 232, 210))
    d.ellipse((wx + 44, wy - 100, wx + 120, wy - 24), fill=(10, 16, 38))
    d.line((wx - wr, wy, wx + wr, wy), fill=(46, 50, 70), width=8); d.line((wx, wy - wr, wx, wy + wr), fill=(46, 50, 70), width=8)
    # bureau
    d.rectangle((0, DESK_Y, W, H), fill=mix((20, 14, 10), WOOD, 0.4 + 0.6 * lit))
    d.rectangle((0, DESK_Y, W, DESK_Y + 26), fill=mix((30, 20, 14), WOOD2, 0.4 + 0.6 * lit))
    for i in range(9):
        y = DESK_Y + 60 + i * 74; d.line((0, y, W, y + 10), fill=mix((16, 10, 8), (70, 44, 26), lit), width=3)
    # lampe de bureau
    lx, ly = 170, DESK_Y
    d.rectangle((lx - 70, ly - 18, lx + 70, ly), fill=(30, 30, 36))
    d.line((lx, ly - 18, lx + 60, ly - 330), fill=(40, 40, 48), width=14)
    d.line((lx + 60, ly - 330, lx + 230, ly - 420), fill=(40, 40, 48), width=12)
    d.polygon([(lx + 190, ly - 470), (lx + 300, ly - 400), (lx + 270, ly - 330), (lx + 140, ly - 390)], fill=(48, 46, 52))
    if lit > 0:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.polygon([(lx + 160, ly - 380), (lx + 280, ly - 350), (W + 200, H), (lx - 100, H)], fill=AMBER + (int(46 * lit),))
        dl.ellipse((lx + 120, ly - 440, lx + 330, ly - 300), fill=(255, 220, 150, int(150 * lit)))
        dl.ellipse((120, DESK_Y - 120, W - 40, DESK_Y + 300), fill=AMBER + (int(40 * lit),))
        L = L.filter(ImageFilter.GaussianBlur(40)); img.alpha_composite(L)
    return img

ROOM_D = make_room(0.15); ROOM_L = make_room(1.0)
_RC = {}
def room(level):
    q = round(min(1, max(0, level)) * 20) / 20
    if q not in _RC: _RC[q] = Image.blend(ROOM_D, ROOM_L, q)
    return _RC[q].copy()
stadium = room

def dim(img, a):
    if a <= 0: return
    img.alpha_composite(Image.new("RGBA", (W, H), BG + (int(255 * min(1, a)),)))

def M(name, default=None): return MK.get(name, default)

def badge(d, x, y, s, k, col=AMBER, r=110, tcol=BG):
    if k <= 0: return
    sc = 1 + 0.5 * (1 - eout(k / 0.18)); rr = r * sc
    d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)
    text(d, (x, y), s, fit(s, int(0.62 * rr), 1.7 * rr), tcol, BOLD)

def label(d, y, s, k, size=78, col=WHITE, sub=None, subcol=AMBER):
    if k <= 0: return
    yy = y - 30 * (1 - eout(k / 0.3))
    text(d, (W / 2, yy), typew(s, k, 30), fit(s, size, 980), col, BOLD, stroke=5, scol=BG)
    if sub and k > 0.25: text(d, (W / 2, yy + size * 0.95), sub, fit(sub, 40, 960, MONO), subcol, MONO)

def burst(d, x, y, k, n=16, r=160, col=AMBER, seed=0, w=7):
    if k <= 0 or k > 0.7: return
    rng = np.random.default_rng(seed); e = eout(k / 0.5); a = 1 - k / 0.7
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        r0, r1 = r * 0.3 * e, r * (0.6 + 0.6 * rng.random()) * e
        d.line((x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r1 * math.cos(ang), y + r1 * math.sin(ang)), fill=mix(BG, col, a), width=w)

# --------------------------------------------------------------- objets
def typewriter(d, cx, cy, s, tg, typing=True, lit=1.0):
    """Machine à écrire générique (sans marque). (cx, cy) = bas-centre posé sur le bureau."""
    body = mix((20, 22, 28), (60, 64, 74), lit)
    d.rounded_rectangle((cx - 1.0 * s, cy - 0.45 * s, cx + 1.0 * s, cy), int(0.12 * s), fill=body, outline=mix(BG, GREY, lit), width=4)
    d.rounded_rectangle((cx - 0.85 * s, cy - 0.72 * s, cx + 0.85 * s, cy - 0.42 * s), int(0.1 * s), fill=mix(body, (0, 0, 0), 0.3))
    d.rounded_rectangle((cx - 1.15 * s, cy - 0.82 * s, cx + 1.15 * s, cy - 0.68 * s), int(0.06 * s), fill=mix(BG, (90, 94, 104), lit))
    for row in range(3):
        for i in range(10 - row):
            kx = cx - 0.78 * s + (i + row * 0.5) * 0.17 * s; ky = cy - 0.34 * s + row * 0.11 * s
            down = typing and (int(tg * 14 + i * 3 + row * 5) % 9 == 0)
            r = 0.05 * s
            d.ellipse((kx - r, ky - r + (4 if down else 0), kx + r, ky + r + (4 if down else 0)), fill=mix(BG, PAPER, 0.75 * lit))

def page(d, x, y, w, h, lines=6, col=PAPER, ink=INK, rot_off=0):
    d.rectangle((x, y, x + w, y + h), fill=col)
    for j in range(lines):
        yy = y + h * 0.16 + j * h * 0.12
        if yy > y + h * 0.9: break
        d.line((x + w * 0.1, yy, x + w * (0.9 - 0.18 * ((j + rot_off) % 2)), yy), fill=mix(col, ink, 0.6), width=max(2, int(h / 70)))

def letter_img(w, h, stamp_txt=None, col=PAPER):
    L = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    page(d, 20, 20, w, h, 7, col)
    if stamp_txt:
        text(d, (20 + w / 2, 20 + h * 0.62), stamp_txt, fit(stamp_txt, int(h * 0.26), w * 0.85), RED, BOLD)
        d.rounded_rectangle((20 + w * 0.08, 20 + h * 0.47, 20 + w * 0.92, 20 + h * 0.77), 10, outline=RED, width=6)
    return L

def paste_rot(img, L, cx, cy, ang, alpha=1.0, scale=1.0):
    if scale != 1.0: L = L.resize((max(1, int(L.width * scale)), max(1, int(L.height * scale))), Image.BICUBIC)
    L = L.rotate(ang, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = np.asarray(L).copy(); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); L = Image.fromarray(a)
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

LET_NO = letter_img(300, 400, "REFUSÉ"); LET_BLANK = letter_img(300, 400)

def writer(img, x, y, s, tg, slump=0.0, typing=True, alpha=1.0, glow=0.8, arms=0.0):
    """Silhouette d'écrivain générique (vue de dos 3/4), assis. (x, y) = bas de la chaise au niveau du bureau.
    slump 0..1 = tête baissée, arms 0..1 = bras levés (victoire)."""
    L = Image.new("RGBA", (int(3 * s), int(3.2 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ox, oy = 1.5 * s, 2.6 * s
    rim = mix(SIL, AMBER, glow)
    bob = 0.015 * s * math.sin(tg * 9) if typing else 0
    sh = (ox, oy - 1.05 * s + bob + 0.12 * s * slump)
    hd = (ox + 0.05 * s, sh[1] - 0.3 * s + 0.16 * s * slump)
    # dossier de chaise
    d.rounded_rectangle((ox - 0.55 * s, oy - 0.95 * s, ox + 0.55 * s, oy - 0.15 * s), int(0.1 * s), fill=(24, 18, 14), outline=mix((24, 18, 14), WOOD2, glow), width=5)
    d.line((ox - 0.45 * s, oy - 0.15 * s, ox - 0.5 * s, oy + 0.35 * s), fill=(24, 18, 14), width=int(0.07 * s))
    d.line((ox + 0.45 * s, oy - 0.15 * s, ox + 0.5 * s, oy + 0.35 * s), fill=(24, 18, 14), width=int(0.07 * s))
    # bras
    for side in (-1, 1):
        sx = sh[0] + side * 0.36 * s
        if arms > 0:
            ex = sx + side * lerp(0.25, 0.32, arms) * s; ey = sh[1] - lerp(-0.25, 0.55, arms) * s
            hx = ex + side * 0.05 * s; hy = ey - lerp(-0.2, 0.35, arms) * s
        else:
            tap = 0.03 * s * math.sin(tg * 18 + side) if typing else 0
            ex = sx + side * 0.18 * s; ey = sh[1] + 0.4 * s; hx = sh[0] + side * 0.2 * s; hy = sh[1] + 0.62 * s + tap
        for wdt, col in ((int(0.16 * s) + 8, rim), (int(0.16 * s), SIL)):
            d.line((sx, sh[1] + 0.05 * s, ex, ey), fill=col, width=wdt); d.line((ex, ey, hx, hy), fill=col, width=int(wdt * 0.9))
    # torse + tête
    d.rounded_rectangle((sh[0] - 0.42 * s - 4, sh[1] - 4, sh[0] + 0.42 * s + 4, oy - 0.2 * s + 4), int(0.2 * s), fill=rim)
    d.rounded_rectangle((sh[0] - 0.42 * s, sh[1], sh[0] + 0.42 * s, oy - 0.2 * s), int(0.2 * s), fill=SIL)
    r = 0.2 * s
    d.ellipse((hd[0] - r - 4, hd[1] - r - 4, hd[0] + r + 4, hd[1] + r + 4), fill=rim)
    d.ellipse((hd[0] - r, hd[1] - r, hd[0] + r, hd[1] + r), fill=SIL)
    if alpha < 1:
        a = np.asarray(L).copy(); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); L = Image.fromarray(a)
    img.alpha_composite(L, (int(x - ox), int(y - oy)))

def trash_can(d, cx, by, s, lit=1.0):
    c = mix((30, 32, 40), (110, 116, 130), lit)
    d.polygon([(cx - 0.5 * s, by - 1.1 * s), (cx + 0.5 * s, by - 1.1 * s), (cx + 0.4 * s, by), (cx - 0.4 * s, by)], fill=c)
    for i in range(5):
        x = cx - 0.3 * s + i * 0.15 * s; d.line((x, by - 1.0 * s, x * 0.98 + cx * 0.02, by - 0.08 * s), fill=mix(c, (0, 0, 0), 0.35), width=5)
    d.rounded_rectangle((cx - 0.56 * s, by - 1.18 * s, cx + 0.56 * s, by - 1.06 * s), 8, fill=mix(c, WHITE, 0.15))

def crumple(d, x, y, r, seed, col=PAPER):
    rng = np.random.default_rng(seed)
    pts = [(x + r * (0.75 + 0.3 * rng.random()) * math.cos(a), y + r * (0.75 + 0.3 * rng.random()) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 11)[:-1]]
    d.polygon(pts, fill=col)
    for _ in range(4):
        a = rng.uniform(0, 2 * math.pi); d.line((x, y, x + 0.8 * r * math.cos(a), y + 0.8 * r * math.sin(a)), fill=mix(col, INK, 0.3), width=3)

# --------------------------------------------------------------- scènes
def s_hook(img, d, tg, k):
    hit = 0.0
    typewriter(d, W / 2 + 120, DESK_Y + 120, 230, tg, typing=tg < K["hook"])
    # page dans le rouleau
    ph = 260 + 60 * min(1, tg / 1.2)
    page(d, W / 2 + 120 - 170, DESK_Y + 120 - 0.8 * 230 - ph, 340, ph + 20, 5)
    writer(img, 330, DESK_Y + 520, 300, tg, glow=0.5)
    kk = tg - K["hook"]
    if kk > -0.05:
        hit = stamp(img, "REFUSÉ", (W / 2 + 120, DESK_Y - 260), 120, -10, kk + 0.05, RED)
        sc = 1 + 0.5 * (1 - eout((kk + 0.05) / 0.18))
        text(d, (W / 2, 330), "UN REFUS", int(fit("UN REFUS", 140, 960) * sc), WHITE, BOLD, stroke=8, scol=BG)
        text(d, (W / 2, 500), "= LA FIN ?", int(fit("= LA FIN ?", 130, 960) * sc), AMBER, BOLD, stroke=8, scol=BG)
    return dict(hit=hit)

def s_letters(img, d, tg, k):
    dim(img, 0.35)
    label(d, 260, "L'ÉCRIVAIN", k, 110, WHITE, "SES PREMIÈRES HISTOIRES", AMBER)
    hit = 0.0
    tm = M("magazines", SC["letters"] + 2.5)
    # enveloppes envoyées (vers le haut)
    for i in range(6):
        kk = tg - (SC["letters"] + 0.8 + i * 0.35)
        if 0 < kk < 1.6 and tg < tm + 0.8:
            u = eout(kk / 1.4); x = lerp(W / 2, 140 + i * 160, u); y = lerp(1300, 560, u)
            d.rectangle((x - 70, y - 45, x + 70, y + 45), fill=PAPER); d.line((x - 70, y - 45, x, y + 5, x + 70, y - 45), fill=GREY, width=4)
    # retours : lettres REFUSÉ qui tombent sur la pile
    ts = [M("refus2", tm + 0.5), M("refus3", tm + 1.2), M("refus4", tm + 2.0)]
    for i, t0 in enumerate(ts):
        kk = tg - (t0 - 0.12)
        if kk <= 0: continue
        u = eout(kk / 0.2)
        cy = lerp(-250, 1080 - i * 40, u); ang = [-12, 9, -4][i]
        paste_rot(img, LET_NO, W / 2 + [-150, 140, 0][i], cy, ang, 1.0, 1.05)
        if 0.15 < kk < 0.45: hit = max(hit, 1 - (kk - 0.15) / 0.3)
    return dict(hit=hit, shake=hit * 0.6)

def s_nail(img, d, tg, k):
    dim(img, 0.2)
    hit = 0.0
    t_c2 = M("clou2", SC["nail"] + 3.5); t_pic = M("pic", t_c2 + 1.2); t_cont = M("continue", t_pic + 0.5)
    nx, ny = W / 2, 470
    n_on = int(min(14, max(0, (tg - SC["nail"] - 0.2) * 5)))
    bend = ease((tg - t_c2 + 0.1) / 0.3) if tg < t_pic - 0.1 else 0
    spike = tg >= t_pic - 0.1
    if not spike:   # clou
        d.ellipse((nx - 18, ny - 18, nx + 18, ny + 18), fill=(160, 160, 170))
        ex, ey = nx + 70 * math.cos(math.radians(90 * bend)) * 0 + 0, ny + 0
        d.line((nx, ny, nx + 8 + 40 * bend, ny + 60 + 40 * bend), fill=(150, 150, 160), width=10)
    else:
        ks = tg - (t_pic - 0.1)
        sc = 1 + 0.6 * (1 - eout(ks / 0.15))
        d.polygon([(nx - 26 * sc, ny - 30), (nx + 26 * sc, ny - 30), (nx + 6, ny + 420 * sc), (nx - 6, ny + 420 * sc)], fill=(200, 202, 214))
        d.ellipse((nx - 50 * sc, ny - 60, nx + 50 * sc, ny - 10), fill=(220, 222, 232))
        if ks < 0.3: hit = max(hit, 1 - ks / 0.3)
        burst(d, nx, ny + 100, ks, 18, 380, AMBER, 4)
    # liasse de lettres embrochées
    for i in range(n_on if not spike else 30):
        rng = np.random.default_rng(i)
        drop = 0 if not bend else bend * (300 + 50 * i)
        yy = ny + 40 + i * (14 if not spike else 11) + drop
        if yy > H: continue
        paste_rot(img, LET_NO if i % 3 == 0 else LET_BLANK, nx + rng.uniform(-30, 30), yy + 180, rng.uniform(-14, 14), 1.0, 0.75)
    if bend > 0 and not spike and tg - t_c2 < 0.4: hit = max(hit, 1 - (tg - t_c2) / 0.4)
    label(d, 220, "LE CLOU NE TIENT PLUS", tg - t_c2, 78, WHITE) if not spike else label(d, 220, "IL PREND UN PIC.", tg - t_pic, 90, AMBER)
    if tg > t_cont:
        typewriter(d, W / 2, H - 120, 200, tg)
        text(d, (W / 2, 1180), "ET IL ÉCRIT.", int(fit("ET IL ÉCRIT.", 110, 960) * (1 + 0.3 * (1 - eout((tg - t_cont) / 0.2)))), WHITE, BOLD, stroke=7, scol=BG)
    return dict(hit=hit, shake=hit * 0.8)

def s_trailer(img, d, tg, k):
    # extérieur : caravane la nuit, fenêtre allumée
    img.alpha_composite(Image.new("RGBA", (W, H), (6, 10, 26, 235)))
    rng = np.random.default_rng(9)
    for _ in range(90):
        x, y, s = rng.uniform(0, W), rng.uniform(0, 900), rng.uniform(1, 3.2)
        tw = 0.6 + 0.4 * math.sin(tg * 3 + x)
        d.ellipse((x - s, y - s, x + s, y + s), fill=mix(BG, (220, 226, 250), tw))
    d.rectangle((0, 1350, W, H), fill=(12, 18, 16))
    cx, cy = W / 2, 1350
    d.rounded_rectangle((cx - 400, cy - 400, cx + 400, cy - 40), 120, fill=(190, 194, 200), outline=(90, 94, 104), width=6)
    d.rectangle((cx - 400, cy - 210, cx + 400, cy - 170), fill=AMBER)
    for wx in (cx - 250, cx + 160):
        d.rounded_rectangle((wx, cy - 340, wx + 150, cy - 240), 20, fill=mix((30, 34, 44), (255, 200, 110), 0.5 + 0.5 * (math.sin(tg * 2) > -0.6)))
    d.rounded_rectangle((cx - 40, cy - 330, cx + 60, cy - 60), 14, fill=(150, 154, 160), outline=(90, 94, 104), width=5)
    for wx in (cx - 250, cx + 250):
        d.ellipse((wx - 70, cy - 110, wx + 70, cy + 30), fill=(20, 20, 24)); d.ellipse((wx - 30, cy - 70, wx + 30, cy - 10), fill=(110, 110, 120))
    label(d, 250, "1973", k, 170, AMBER, "UNE CARAVANE", WHITE)
    hit = 0.0
    tp = M("prof", SC["trailer"] + 2); tb = M("blanch", tp + 1.5)
    if tg > tp - 0.1:
        badge(d, 260, 640, "PROF", tg - tp + 0.1, AMBER, 120)
        if tg - tp < 0.25: hit = max(hit, 1 - (tg - tp) / 0.25)
    if tg > tb - 0.5:
        kb = tg - (tb - 0.5)
        bx, by = 820, 660   # machine à laver industrielle générique
        sc = eout(kb / 0.25)
        d.rounded_rectangle((bx - 150 * sc, by - 170 * sc, bx + 150 * sc, by + 170 * sc), 20, fill=(210, 214, 222))
        d.ellipse((bx - 105 * sc, by - 70 * sc, bx + 105 * sc, by + 140 * sc), fill=(40, 70, 120), outline=(120, 124, 134), width=10)
        for j in range(6):
            a = tg * 9 + j; d.ellipse((bx + 60 * sc * math.cos(a) - 14, by + 35 * sc + 60 * sc * math.sin(a) - 14, bx + 60 * sc * math.cos(a) + 14, by + 35 * sc + 60 * sc * math.sin(a) + 14), fill=WHITE)
        text(d, (bx, by + 230), "BLANCHISSERIE", 44, WHITE, MONO)
        if tg - tb < 0.25 and tg > tb: hit = max(hit, 1 - (tg - tb) / 0.25)
    return dict(hit=hit)

def s_stamps(img, d, tg, k):
    dim(img, 0.55)
    writer(img, W / 2, H - 60, 330, tg, slump=1.0, typing=False, glow=0.35)
    hit = 0.0; cols = [RED, AMBER, RED]
    for i, (txt, t0) in enumerate(TJ["words3d"]):
        hit = max(hit, stamp(img, txt, (W / 2 + [-30, 40, 0][i], [480, 740, 1000][i]), [150, 140, 150][i], [-8, 6, -4][i], tg - t0 + 0.06, cols[i]))
    return dict(hit=hit, shake=hit, bg=0.25)

PAGES_FLY = [(i, np.random.default_rng(i + 40)) for i in range(7)]
def s_trash(img, d, tg, k):
    hit = 0.0
    tj = M("jette", SC["trash"] + 0.8); tpb = M("poubelle", tj + 1.0); tf = M("femme", tpb + 0.8); tr = M("ressort", tf + 0.4)
    cx, by = W / 2 + 180, DESK_Y + 470
    trash_can(d, cx, by, 300)
    writer(img, 300, DESK_Y + 520, 300, tg, slump=0.7 * ease((tg - tj) / 0.5), typing=tg < tj, glow=0.6)
    # boulettes de papier lancées
    for i in range(3):
        kk = tg - (tj + i * 0.35)
        if kk > 0:
            u = min(1, kk / 0.5)
            x = lerp(430, cx + (i - 1) * 60, u); y = lerp(DESK_Y - 100, by - 330, u) - 300 * math.sin(math.pi * u)
            if tg < tr - 0.2 or u < 1: crumple(d, x, y, 55, i)
    if tpb - 0.1 < tg < tpb + 0.25: hit = max(hit, 1 - abs(tg - tpb) / 0.25)
    if tg < tf + 0.05: label(d, 260, "À LA POUBELLE.", tg - tpb + 0.2, 100, RED)
    if tg > tf - 0.1:   # une main ressort les pages, elles s'illuminent
        kf = tg - (tf - 0.1)
        hy = lerp(by - 300, by - 620, eout(kf / 0.5))
        d.line((cx + 20, by - 280, cx + 20, hy + 40), fill=(150, 110, 80), width=46)
        d.ellipse((cx - 30, hy - 30, cx + 70, hy + 70), fill=(170, 124, 90))
        glowL = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glowL).ellipse((cx - 260, hy - 330, cx + 300, hy + 110), fill=GOLD + (int(120 * min(1, kf / 0.3)),))
        img.alpha_composite(glowL.filter(ImageFilter.GaussianBlur(40)))
        page(d, cx - 120, hy - 300, 240, 300, 6, PAPER)
        if kf > 0.15: label(d, 280, "QUELQU'UN Y CROIT.", kf - 0.15, 84, GOLD)
        if abs(tg - tr) < 0.25: hit = max(hit, 1 - abs(tg - tr) / 0.25)
    return dict(hit=hit)

def s_slam(img, d, tg, k):
    kb = tg - K["boom"]
    hit = 0.0; flash = 0.0
    T0 = SC["slam"]
    n = int(min(40, max(0, (tg - T0) * 18)))   # la pile de pages monte
    if kb < -0.08:
        typewriter(d, W / 2, DESK_Y + 160, 230, tg)
        for i in range(n):
            page(d, W / 2 + 330 - 150, DESK_Y + 120 - i * 9, 300, 16, 0, mix(PAPER, (200, 190, 160), (i % 2) * 0.4))
        text(d, (W / 2, 420), "TOUT ARRÊTER ?", fit("TOUT ARRÊTER ?", 110, 960), WHITE, BOLD, stroke=6, scol=BG)
    else:
        kk = kb + 0.08
        for j in range(3):
            r = (kk - j * 0.1) * 1700
            if r > 0: d.ellipse((W / 2 - r, 1180 - r * 0.35, W / 2 + r, 1180 + r * 0.35), outline=AMBER, width=max(1, int(16 * max(0, 1 - r / 1500))))
        burst(d, W / 2, 1000, kk, 22, 520, WHITE, 3, 9)
        y = lerp(-300, DESK_Y - 260, eout(kk / 0.15))
        d.rectangle((W / 2 - 230, y, W / 2 + 230, y + 380), fill=PAPER, outline=(200, 190, 160), width=6)
        for i in range(12): d.line((W / 2 - 230, y + 380 - i * 8, W / 2 + 230, y + 380 - i * 8), fill=(200, 190, 160), width=2)
        text(d, (W / 2, y + 130), "FIN.", 120, INK, BOLD)
        flash = max(0, 0.9 - kb * 4) if kb > 0 else 0
        hit = max(0, 1 - kk / 0.3)
        sc = 1 + 1.2 * (1 - eout(kk / 0.16))
        text(d, (W / 2, 330), "IL L'A", 100, AMBER, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 530), "FINI.", int(fit("FINI.", 260, 1000) * sc), WHITE, BOLD, stroke=10, scol=AMBER)
    return dict(hit=hit * 1.6, shake=hit * 1.8, flash=flash)

def s_deal(img, d, tg, k):
    dim(img, 0.3)
    hit = 0.0
    to = K["gate1"]; t25 = M("d2500", to + 0.8); tp = M("puis", t25 + 1.2); t4 = K["gate2"]
    paste_rot(img, letter_img(420, 560), W / 2, 1080, -3, 1.0, 1.0)
    if tg > to - 0.05:
        hit = max(hit, stamp(img, "OUI", (W / 2, 1150), 200, -8, tg - to + 0.05, GREEN))
    if tg > t25 - 0.1 and tg < tp:
        u = eout((tg - t25 + 0.1) / 0.5); val = int(2500 * u)
        text(d, (W / 2, 420), f"{val:,} $".replace(",", " "), fit("2 500 $", 170, 960), WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 560), "D'AVANCE", 54, GREY, MONO)
    if tg >= tp:
        u = eout(min(1, max(0, (tg - tp) / max(0.3, t4 - tp + 0.3))))
        val = int(2500 + (400000 - 2500) * u)
        sc = 1 + (0.25 * (1 - eout((tg - t4) / 0.25)) if tg > t4 else 0)
        text(d, (W / 2, 420), f"{val:,} $".replace(",", " "), int(fit("400 000 $", 170, 980) * sc), GOLD if u >= 1 else WHITE, BOLD, stroke=6, scol=BG)
        text(d, (W / 2, 560), "LES DROITS EN POCHE", 50, GOLD, MONO)
        if tg > t4 and tg - t4 < 0.25: hit = max(hit, 1 - (tg - t4) / 0.25)
        if tg > t4: burst(d, W / 2, 420, tg - t4, 20, 420, GOLD, 7)
    return dict(hit=hit)

BOOKC = [(200, 60, 50), (40, 90, 160), (220, 170, 60), (60, 130, 90), (150, 70, 140), (230, 230, 220)]
def s_books(img, d, tg, k):
    dim(img, 0.5)
    hit = 0.0
    tm = M("monde", SC["books"] + 2.5)
    # globe stylisé fait de méridiens
    gx, gy, gr = W / 2, 820, 260
    d.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), outline=mix(BG, AMBER, 0.6), width=6)
    for i in range(1, 6):
        rx = gr * abs(math.cos(tg * 0.8 + i * math.pi / 6)); d.ellipse((gx - rx, gy - gr, gx + rx, gy + gr), outline=mix(BG, AMBER, 0.35), width=3)
    for j in (-0.5, 0, 0.5):
        yy = gy + j * gr; hw = gr * math.sqrt(1 - j * j); d.line((gx - hw, yy, gx + hw, yy), fill=mix(BG, AMBER, 0.35), width=3)
    # piles de livres génériques (sans titre) qui montent autour
    n = int(min(30, max(0, (tg - SC["books"]) * 14)))
    for i in range(n):
        col = i % 6; stack = i % 5; lvl = i // 5
        x = 120 + stack * 210; y = 1440 - lvl * 46
        c = BOOKC[(i * 7) % 6]
        d.rectangle((x - 80 + (lvl % 2) * 10, y - 40, x + 80 + (lvl % 2) * 10, y), fill=c, outline=BG, width=3)
        d.line((x - 60, y - 20, x + 40, y - 20), fill=mix(c, WHITE, 0.4), width=3)
    if tg > tm - 0.1:
        km = tg - tm + 0.1
        burst(d, gx, gy, km, 24, 520, GOLD, 5)
        if km < 0.3: hit = 1 - km / 0.3
    label(d, 300, "L'UN DES PLUS LUS", k, 100, WHITE, None)
    if tg > tm - 0.1: text(d, (W / 2, 450), "AU MONDE.", int(fit("AU MONDE.", 130, 960) * (1 + 0.3 * (1 - eout((tg - tm + 0.1) / 0.18)))), GOLD, BOLD, stroke=7, scol=BG)
    return dict(hit=hit)

def s_you(img, d, tg, k):
    dim(img, 0.6)
    text(d, (W / 2, 300), "ET TOI ?", int(140 + 40 * (1 - eout(k / 0.2))), AMBER, BOLD, stroke=6, scol=BG)
    rows = [("NON", "des magazines"), ("NON", "encore"), ("POUBELLE", "le roman"), ("OUI", "il a continué")]
    t0 = SC["you"] + 0.2; span = max(0.5, K["arms_up"] - 0.3 - t0)
    for i, (a, b) in enumerate(rows):
        kk = tg - (t0 + i * span / 4)
        if kk <= 0: continue
        y = 520 + i * 135; x = 130 - 80 * (1 - eout(kk / 0.2))
        c = GREEN if i == 3 else RED
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=c)
        if i < 3: d.line((x, y + 20, x, y + 115), fill=GREY, width=4)
        text(d, (x + 50, y), a, 50, c, MONO, "lm"); text(d, (x + 370, y), b, 50, WHITE, BOLD, "lm")
    kn = tg - K["arms_up"]
    hit = stamp(img, "CONTINUE.", (W / 2, 1150), 120, -5, kn + 0.05, GOLD) if kn > -0.05 else 0.0
    return dict(hit=hit)

NUMS = [(np.random.default_rng(i).uniform(90, W - 90), np.random.default_rng(i + 7).uniform(0, 700), s, np.random.default_rng(i + 3).uniform(0.3, 0.7))
        for i, s in enumerate(["NON", "3", "10", "NON", "27", "50", "NON", "7", "100", "NON"])]
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
        text(d, (x, yy), s, 70, mix(BG, (70, 60, 50), a), BOLD)
    text(d, (W / 2, 1000), "?", int(600 * (1 + 0.08 * pulse)), mix(BG, (90, 60, 30), a), BOLD)
    return dict(hit=0.5 * pulse)

def s_logo(img, d, tg, k):
    dim(img, 0.9)
    fade = 1 - ease((tg - (END - 0.7)) / 0.7)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    sc = 1 + 0.15 * (1 - eout(k / 0.5)); g = tuple(int(c * fade) for c in GOLD)
    text(dl, (W / 2, 690), "MINDSET", int(150 * sc), g + (255,), BOLD)
    text(dl, (W / 2, 900), "24", int(300 * sc), g + (255,), BOLD)
    glow = L.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow); img.alpha_composite(glow); img.alpha_composite(L)
    d.line((W / 2 - 300 * eout(k / 0.6), 1080, W / 2 + 300 * eout(k / 0.6), 1080), fill=g, width=4)
    return dict(fade=fade)

SCENES = {"hook": s_hook, "letters": s_letters, "nail": s_nail, "trailer": s_trailer, "stamps": s_stamps, "trash": s_trash,
          "slam": s_slam, "deal": s_deal, "books": s_books, "you": s_you, "question": s_question, "logo": s_logo}
BGLEVEL = {"hook": 0.6, "letters": 0.7, "nail": 0.8, "trailer": 0.5, "stamps": 0.2, "trash": 0.6, "slam": 0.5, "deal": 1.0,
           "books": 0.9, "you": 0.4, "question": 0.1, "logo": 0.0}

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
    if s["type"] == "slam" and tg > K["boom"] - 0.08: lvl = 1.0
    if s["type"] == "hook": lvl = 0.55 + 0.1 * math.sin(tg * 7)
    img = stadium(lvl); d = ImageDraw.Draw(img)
    R = SCENES[s["type"]](img, d, tg, tg - s["start"]) or {}
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

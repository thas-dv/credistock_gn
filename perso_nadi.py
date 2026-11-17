# -*- coding: utf-8 -*-
"""NOUVEAU PERSONNAGE Mindset 24 (16/11/2026) — demandé par l'utilisateur : « change complètement le personnage ».
Personnage dessin animé « cartoon plat » : ado longiligne (frêle), coupe high-top, grands yeux expressifs, maillot TURQUOISE à col
et bande JAUNES (sans numéro ni logo), short noir, chaussettes jaunes, crampons rouges. Totalement différent du héros manga au bandeau
orange (Kaï / manga cartes) et de l'« athlète » sans visage des styles 3D.
Génère une bibliothèque de poses (mêmes noms que manga/*.jpg) dans perso2/ : python3 perso_nadi.py"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2
W, H = 1152, 2048
OUT = "perso2"
LINE = (16, 18, 28); SKIN = (122, 78, 52); SKIN_D = (98, 60, 40); HAIR = (22, 20, 24); HAIR_F = (58, 54, 60)
JER = (18, 178, 170); JER_D = (12, 128, 124); YEL = (255, 206, 40); SHO = (30, 32, 40); SOCK = (255, 206, 40); BOOT = (226, 52, 48)
BGT = (10, 22, 52); BGB = (30, 46, 96)

def V(a): r = math.radians(a); return (math.sin(r), math.cos(r))
def add(p, a, l): v = V(a); return (p[0] + v[0] * l, p[1] + v[1] * l)

class Pen:
    def __init__(s, im): s.im = im; s.d = ImageDraw.Draw(im)
    def cap(s, p, q, w, col, ol=10):
        d = s.d
        for c, ww in ((LINE, w + 2 * ol), (col, w)):
            d.line((p, q), fill=c, width=int(ww))
            for z in (p, q): d.ellipse((z[0] - ww / 2, z[1] - ww / 2, z[0] + ww / 2, z[1] + ww / 2), fill=c)
    def poly(s, pts, col, ol=10):
        s.d.line(pts + [pts[0]], fill=LINE, width=int(2 * ol), joint="curve")
        for z in pts: s.d.ellipse((z[0] - ol, z[1] - ol, z[0] + ol, z[1] + ol), fill=LINE)
        s.d.polygon(pts, fill=col)
    def ell(s, c, rx, ry, col, ol=10):
        s.d.ellipse((c[0] - rx - ol, c[1] - ry - ol, c[0] + rx + ol, c[1] + ry + ol), fill=LINE)
        s.d.ellipse((c[0] - rx, c[1] - ry, c[0] + rx, c[1] + ry), fill=col)

def background(seed=0):
    yy = np.linspace(0, 1, H * SS)[:, None, None]
    g = np.array(BGT, np.float32) * (1 - yy) + np.array(BGB, np.float32) * yy
    g = np.repeat(g, W * SS, axis=1)
    g += np.random.default_rng(seed).normal(0, 3, (H * SS, W * SS, 1))
    im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    # halo de lumière derrière le personnage
    halo = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(halo).ellipse((W * SS * 0.1, H * SS * 0.18, W * SS * 0.9, H * SS * 0.78), fill=(80, 170, 200, 70))
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(120)))
    return im

def face(P, c, r, expr="neutral", look=0.0):
    d = P.d; ex = r * 0.36; ey = c[1] - r * 0.02
    if expr != "back":
        for sx in (-1, 1):
            e = (c[0] + sx * ex + look * r * 0.15, ey)
            rx, ry = r * 0.2, r * (0.07 if expr == "sad" else 0.24 if expr in ("shout", "happy") else 0.21)
            if expr == "happy":
                d.arc((e[0] - rx, e[1] - ry, e[0] + rx, e[1] + ry), 200, 340, fill=LINE, width=int(r * 0.08))
            else:
                d.ellipse((e[0] - rx - 6, e[1] - ry - 6, e[0] + rx + 6, e[1] + ry + 6), fill=LINE)
                d.ellipse((e[0] - rx, e[1] - ry, e[0] + rx, e[1] + ry), fill=(250, 250, 248))
                pr = r * 0.135; px = e[0] + look * r * 0.08; py = e[1] + (r * 0.04 if expr == "sad" else 0)
                d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(30, 22, 18))
                d.ellipse((px - pr * 0.35 + pr * 0.3, py - pr * 0.6, px + pr * 0.25 + pr * 0.3, py - pr * 0.05), fill=(255, 255, 255))
            # sourcils
            by = ey - r * 0.27
            if expr in ("angry", "shout", "determined"):
                d.line((e[0] + sx * rx * 1.2, by - r * 0.07, e[0] - sx * rx * 0.9, by + r * 0.07), fill=LINE, width=int(r * 0.11))
            elif expr == "sad":
                d.line((e[0] + sx * rx * 1.2, by + r * 0.06, e[0] - sx * rx * 0.9, by - r * 0.06), fill=LINE, width=int(r * 0.09))
            else:
                d.arc((e[0] - rx * 1.2, by - r * 0.05, e[0] + rx * 1.2, by + r * 0.15), 200, 340, fill=LINE, width=int(r * 0.09))
        # nez
        d.arc((c[0] - r * 0.09 + look * r * 0.15, c[1] + r * 0.1, c[0] + r * 0.09 + look * r * 0.15, c[1] + r * 0.28), 0, 180, fill=SKIN_D, width=int(r * 0.06))
        my = c[1] + r * 0.5; mx = c[0] + look * r * 0.12
        if expr in ("shout", "happy"):
            hh = r * (0.32 if expr == "shout" else 0.22)
            d.ellipse((mx - r * 0.26 - 6, my - hh * 0.5 - 6, mx + r * 0.26 + 6, my + hh + 6), fill=LINE)
            d.ellipse((mx - r * 0.26, my - hh * 0.5, mx + r * 0.26, my + hh), fill=(120, 24, 34))
            d.rectangle((mx - r * 0.2, my - hh * 0.5, mx + r * 0.2, my - hh * 0.5 + r * 0.08), fill=(250, 250, 250))
        elif expr == "sad":
            d.arc((mx - r * 0.18, my, mx + r * 0.18, my + r * 0.2), 200, 340, fill=LINE, width=int(r * 0.07))
        elif expr == "determined":
            d.line((mx - r * 0.18, my + r * 0.04, mx + r * 0.18, my), fill=LINE, width=int(r * 0.07))
        else:
            d.arc((mx - r * 0.2, my - r * 0.14, mx + r * 0.2, my + r * 0.1), 20, 160, fill=LINE, width=int(r * 0.07))

def head(P, c, r, tilt=0, expr="neutral", look=0.0, back=False, sweat=False):
    # oreilles
    for sx in (-1, 1): P.ell((c[0] + sx * r * 0.98, c[1] + r * 0.05), r * 0.16, r * 0.22, SKIN_D, 8)
    P.ell(c, r, r * 1.08, SKIN, 10)
    # coupe high-top : bloc haut + dégradé sur les côtés
    P.d.rounded_rectangle((c[0] - r * 0.92 - 10, c[1] - r * 1.62 - 10, c[0] + r * 0.92 + 10, c[1] - r * 0.3), int(r * 0.55), fill=LINE)
    P.d.rounded_rectangle((c[0] - r * 0.92, c[1] - r * 1.62, c[0] + r * 0.92, c[1] - r * 0.4), int(r * 0.5), fill=HAIR)
    rng = np.random.default_rng(7)
    for _ in range(26):
        x = c[0] + rng.uniform(-0.8, 0.8) * r; y = c[1] + rng.uniform(-1.5, -0.6) * r; q = r * 0.07
        P.d.arc((x - q, y - q, x + q, y + q), rng.uniform(0, 360), rng.uniform(0, 360) + 200, fill=(70, 66, 76), width=max(2, int(r * 0.025)))
    P.ell(c, r * 0.0001, r * 0.0001, SKIN, 0)
    if back:
        P.d.ellipse((c[0] - r * 0.92, c[1] - r * 0.7, c[0] + r * 0.92, c[1] + r * 0.6), fill=HAIR_F)
        return
    face(P, c, r, expr, look)
    if sweat:
        for sx, sy in ((0.75, -0.35), (-0.8, -0.1)):
            x, y = c[0] + sx * r, c[1] + sy * r
            P.d.polygon([(x, y - r * 0.16), (x - r * 0.07, y), (x + r * 0.07, y)], fill=(180, 230, 255)); P.d.ellipse((x - r * 0.07, y - r * 0.06, x + r * 0.07, y + r * 0.08), fill=(180, 230, 255))

def ball(P, c, r):
    P.ell(c, r, r, (250, 250, 250), 9)
    pts = [add(c, 180 + i * 72, r * 0.38) for i in range(5)]; P.d.polygon(pts, fill=LINE)
    for i in range(5):
        q = add(c, 180 + i * 72, r * 0.38); q2 = add(c, 180 + i * 72, r * 0.95); P.d.line((q, q2), fill=LINE, width=8)

def figure(P, hip, s, pose, expr="neutral", look=0.0, back=False, prop=None, sweat=False):
    """hip = bassin ; s = échelle (hauteur totale ≈ 3.1 s). pose : t (inclinaison du torse), la/ra/ll/rl = (angle haut, angle bas absolus)"""
    t = pose.get("t", 0)
    neck = add(hip, 180 + t, 1.0 * s); hc = add(neck, 180 + t, 0.46 * s); r = 0.36 * s
    perp = V(t + 90)
    sh = add(hip, 180 + t, 0.9 * s)
    shL = (sh[0] - perp[0] * 0.3 * s, sh[1] - perp[1] * 0.3 * s); shR = (sh[0] + perp[0] * 0.3 * s, sh[1] + perp[1] * 0.3 * s)
    hpL = (hip[0] - perp[0] * 0.16 * s, hip[1] - perp[1] * 0.16 * s); hpR = (hip[0] + perp[0] * 0.16 * s, hip[1] + perp[1] * 0.16 * s)
    aw, lw = 0.2 * s, 0.27 * s
    def arm(root, ang, front):
        e = add(root, ang[0], 0.62 * s); h = add(e, ang[1], 0.58 * s)
        P.cap(root, e, aw, SKIN if front else SKIN_D); P.cap(e, h, aw * 0.9, SKIN if front else SKIN_D)
        P.ell(h, aw * 0.72, aw * 0.72, SKIN if front else SKIN_D, 8)
        P.cap(root, add(root, ang[0], 0.3 * s), aw * 1.55, JER if front else JER_D)   # manche
        P.d.line((add(root, ang[0], 0.3 * s - aw * 0.2), add(add(root, ang[0], 0.3 * s - aw * 0.2), ang[0] + 90, 1)), fill=YEL, width=1)
        return h
    def leg(root, ang, front, foot=1):
        k = add(root, ang[0], 0.78 * s); f = add(k, ang[1], 0.76 * s)
        P.cap(root, k, lw, SKIN if front else SKIN_D); P.cap(k, f, lw * 0.85, SKIN if front else SKIN_D)
        P.cap(add(k, ang[1], 0.3 * s), f, lw * 0.98, SOCK if front else tuple(int(v * 0.8) for v in SOCK))
        P.cap(root, add(root, ang[0], 0.32 * s), lw * 1.22, SHO if front else (22, 24, 30))   # jambe du short
        toe = add(f, ang[1] - 90 * foot, 0.3 * s)
        P.cap(f, toe, lw * 0.95, BOOT if front else tuple(int(v * 0.8) for v in BOOT), 9)
        return f, toe
    face_dir = -1 if back else 1
    # ordre : bras/jambe du fond, torse, short, jambe avant, tête, bras avant
    hR = arm(shR, pose["ra"], back); fR = leg(hpR, pose["rl"], back, pose.get("fr", 1))
    if not back: hL0 = None
    # torse
    A = (hip[0] + perp[0] * 0.28 * s, hip[1] + perp[1] * 0.28 * s); B = (hip[0] - perp[0] * 0.28 * s, hip[1] - perp[1] * 0.28 * s)
    C = (shL[0] - perp[0] * 0.06 * s, shL[1] - perp[1] * 0.06 * s); D = (shR[0] + perp[0] * 0.06 * s, shR[1] + perp[1] * 0.06 * s)
    P.cap(neck, add(neck, 180 + t, 0.25 * s), 0.18 * s, SKIN_D, 9)
    P.poly([A, B, C, D], JER, 10)
    # bande jaune latérale + col
    P.d.line((_m(A, D, 0.05), _m(A, D, 0.95)), fill=YEL, width=int(0.07 * s))
    if not back:
        cv = add(neck, t, 0.02 * s)
        P.d.polygon([add(cv, t + 90, 0.17 * s), add(cv, t - 90, 0.17 * s), add(cv, t, 0.24 * s)], fill=LINE)
        P.d.polygon([add(cv, t + 90, 0.13 * s), add(cv, t - 90, 0.13 * s), add(cv, t, 0.19 * s)], fill=YEL)
        P.d.polygon([add(cv, t + 90, 0.07 * s), add(cv, t - 90, 0.07 * s), add(cv, t, 0.11 * s)], fill=SKIN_D)
    P.ell(hip, 0.3 * s, 0.16 * s, SHO, 10)
    fL = leg(hpL, pose["ll"], not back, pose.get("fl", 1))
    if prop == "bag":
        P.cap(shL, add(hip, 90, 0.3 * s), 0.07 * s, (40, 40, 48), 7)
        P.d.rounded_rectangle((hip[0] + 0.1 * s, hip[1] - 0.3 * s, hip[0] + 0.9 * s, hip[1] + 0.25 * s), int(0.15 * s), fill=LINE)
        P.d.rounded_rectangle((hip[0] + 0.14 * s, hip[1] - 0.26 * s, hip[0] + 0.86 * s, hip[1] + 0.21 * s), int(0.13 * s), fill=(54, 56, 70))
        P.d.line((hip[0] + 0.2 * s, hip[1] - 0.05 * s, hip[0] + 0.8 * s, hip[1] - 0.05 * s), fill=YEL, width=int(0.04 * s))
    head(P, hc, r, t, expr, look, back, sweat)
    hL = arm(shL, pose["la"], not back)
    return dict(hL=hL, hR=hR, fL=fL, fR=fR, head=hc, r=r, hip=hip)

def _m(a, b, u): return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)

def ground(P, y, cx, w):
    return
    P.d.ellipse((cx - w, y - w * 0.09, cx + w, y + w * 0.09), fill=(8, 14, 34))

def cup(P, c, s):
    g = (246, 192, 60); gd = (196, 140, 30)
    P.poly([(c[0] - s, c[1] - s * 1.2), (c[0] + s, c[1] - s * 1.2), (c[0] + s * 0.55, c[1] + s * 0.2), (c[0] - s * 0.55, c[1] + s * 0.2)], g, 9)
    P.cap((c[0], c[1] + s * 0.2), (c[0], c[1] + s * 0.7), s * 0.25, gd, 8)
    P.poly([(c[0] - s * 0.6, c[1] + s * 0.7), (c[0] + s * 0.6, c[1] + s * 0.7), (c[0] + s * 0.7, c[1] + s * 1.0), (c[0] - s * 0.7, c[1] + s * 1.0)], gd, 8)
    for sx in (-1, 1): P.d.arc((c[0] + sx * s * 0.75 - s * 0.45, c[1] - s * 1.0, c[0] + sx * s * 0.75 + s * 0.45, c[1] - s * 0.2), 0, 360, fill=LINE, width=int(s * 0.12))
    P.d.line((c[0] - s * 0.5, c[1] - s * 0.9, c[0] - s * 0.3, c[1] - s * 0.1), fill=(255, 240, 180), width=int(s * 0.12))

def bench(P, y, cx, w):
    for x in (cx - w * 0.8, cx + w * 0.8): P.cap((x, y), (x, y + 260), 26, (110, 72, 44), 8)
    P.d.rounded_rectangle((cx - w - 10, y - 40, cx + w + 10, y + 30), 16, fill=LINE)
    P.d.rounded_rectangle((cx - w, y - 30, cx + w, y + 20), 12, fill=(160, 110, 66))

def lines(P, c, n=30, r0=500, r1=1100, seed=1, col=(255, 255, 255, 140)):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        a = rng.uniform(0, 360); P.d.line((add(c, a, r0 + rng.uniform(0, 200)), add(c, a, r1)), fill=col, width=6)

def save(im, name, fx=None, maxh=1560, maxw=1040, bottom=1870):
    """im = calque transparent avec le personnage : on le recadre, on l'agrandit et on le pose au sol, centré."""
    bg = background(hash(name) % 100)
    bb = im.getchannel("A").getbbox(); L = im.crop(bb)
    sc = min(maxh * SS / L.height, maxw * SS / L.width); L = L.resize((int(L.width * sc), int(L.height * sc)), Image.LANCZOS)
    x = int((fx if fx is not None else W / 2) * SS - L.width / 2); y = int(bottom * SS - L.height)
    d = ImageDraw.Draw(bg); gw = L.width * 0.55
    d.ellipse((x + L.width / 2 - gw, bottom * SS - 40 * SS, x + L.width / 2 + gw, bottom * SS + 40 * SS), fill=(6, 12, 30))
    bg.alpha_composite(L, (x, y))
    bg = bg.resize((W, H), Image.LANCZOS).convert("RGB"); os.makedirs(OUT, exist_ok=True); bg.save(f"{OUT}/{name}.jpg", quality=92)

S = 300 * SS
def new(seed=0):
    im = Image.new("RGBA", (W * SS, int(H * SS * 1.6)), (0, 0, 0, 0)); return im, Pen(im)

def main():
    cx = W * SS / 2
    # croise : bras croisés, regard déterminé
    im, P = new(1); ground(P, 1880 * SS, cx, 420 * SS)
    figure(P, (cx, 1060 * SS), S, dict(t=0, la=(-12, 80), ra=(12, -80), ll=(-6, 2), rl=(6, -2)), "determined"); save(im, "croise")
    # pointe : il pointe vers le spectateur (bras tendu sur le côté)
    im, P = new(2); ground(P, 1880 * SS, cx, 420 * SS)
    o = figure(P, (cx - 60 * SS, 1060 * SS), S, dict(t=2, la=(-10, 6), ra=(-112, -96), ll=(-6, 2), rl=(6, -2)), "determined", look=0.4)
    h = o["hR"]; P.cap(h, (h[0] + 0.32 * S, h[1] - 0.02 * S), 0.07 * S, SKIN, 7); save(im, "pointe")
    # bras : victoire, bras levés
    im, P = new(3); ground(P, 1880 * SS, cx, 420 * SS); 
    figure(P, (cx, 1060 * SS), S, dict(t=0, la=(-150, -170), ra=(150, 170), ll=(-14, 4), rl=(14, -4)), "happy"); save(im, "bras")
    # courir : course avec le ballon
    im, P = new(4); ground(P, 1880 * SS, cx, 440 * SS)
    
    o = figure(P, (cx, 1100 * SS), S, dict(t=-14, la=(50, 150), ra=(-45, -15), ll=(55, 5), rl=(-35, -95), fl=-1, fr=-1), "determined", look=0.6)
    ball(P, (cx + 330 * SS, 1790 * SS), 85 * SS); save(im, "courir")
    # frappe : frappe de balle
    im, P = new(5); ground(P, 1880 * SS, cx, 440 * SS); 
    figure(P, (cx + 60 * SS, 1080 * SS), S, dict(t=-10, la=(-100, -60), ra=(80, 140), ll=(-110, -70), rl=(8, 4), fl=-1, fr=-1), "shout", look=-0.6)
    ball(P, (cx - 420 * SS, 1260 * SS), 85 * SS); save(im, "frappe")
    # tete : jeu de tête en l'air
    im, P = new(6); 
    o = figure(P, (cx, 1160 * SS), S, dict(t=-4, la=(-110, -150), ra=(110, 150), ll=(-20, 60), rl=(25, 80)), "determined", look=0.0)
    ball(P, (cx, 430 * SS), 85 * SS); save(im, "tete", bottom=1700)
    # genoux : à genoux, il crie
    im, P = new(7); ground(P, 1880 * SS, cx, 460 * SS); 
    figure(P, (cx, 1330 * SS), S, dict(t=0, la=(-60, -150), ra=(60, 150), ll=(-12, 92), rl=(12, -92), fl=1, fr=-1), "shout"); save(im, "genoux")
    # assis : assis sur le ballon, tête basse
    im, P = new(8); ground(P, 1880 * SS, cx, 420 * SS)
    ball(P, (cx, 1500 * SS), 150 * SS)
    figure(P, (cx, 1360 * SS), S, dict(t=18, la=(-30, 100), ra=(20, -100), ll=(-90, -10), rl=(80, 10), fl=-1, fr=1), "sad"); save(im, "assis")
    # banc : assis seul sur le banc
    im, P = new(9); ground(P, 1880 * SS, cx, 480 * SS); bench(P, 1470 * SS, cx, 400 * SS)
    figure(P, (cx, 1400 * SS), S, dict(t=12, la=(-20, 95), ra=(20, -95), ll=(-90, -4), rl=(90, 4), fl=-1, fr=1), "sad", look=-0.3); save(im, "banc")
    # sac : de dos, sac sur l'épaule
    im, P = new(10); ground(P, 1880 * SS, cx, 420 * SS)
    figure(P, (cx, 1060 * SS), S, dict(t=0, la=(-8, 4), ra=(8, -4), ll=(-6, 2), rl=(6, -2)), back=True, prop="bag"); save(im, "sac")
    # trophee : coupe brandie
    im, P = new(11); ground(P, 1880 * SS, cx, 420 * SS); 
    o = figure(P, (cx, 1080 * SS), S, dict(t=0, la=(-160, -175), ra=(160, 175), ll=(-12, 4), rl=(12, -4)), "happy")
    cup(P, (cx, (o["hL"][1] + o["hR"][1]) / 2 - 150 * SS), 110 * SS); save(im, "trophee")
    # visage : gros plan
    im, P = new(12)
    o = figure(P, (cx, 1500 * SS), S, dict(t=0, la=(-10, 4), ra=(10, -4), ll=(-6, 2), rl=(6, -2)), "determined", sweat=True)
    hx, hy = o["head"]; r = o["r"]
    L = im.crop((int(hx - r * 1.9), int(hy - r * 2.1), int(hx + r * 1.9), int(hy + r * 4.6)))
    L = L.resize((int(W * SS * 1.05), int(W * SS * 1.05 * L.height / L.width)), Image.LANCZOS)
    bg = background(12); bg.alpha_composite(L, (int(W * SS / 2 - L.width / 2), int(H * SS - L.height + 40 * SS)))
    bg.resize((W, H), Image.LANCZOS).convert("RGB").save(f"{OUT}/visage.jpg", quality=92)

if __name__ == "__main__":
    main()

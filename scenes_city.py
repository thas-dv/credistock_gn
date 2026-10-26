# -*- coding: utf-8 -*-
"""Style « city » : ville néon de nuit (bleu électrique), chaînes/lasers rouges, personnage blanc (mannequin sans squelette).
Même interface que scenes.py : K, SC, SCENES. Types : skyline loading busstop eye neon chains snap lasers dawn phoneq logo."""
import math, json
import numpy as np
from engine import *
from body import Body

COLORS = {
    "g": np.array([0.18, 0.55, 1.00], np.float32),   # ville : bleu électrique
    "r": np.array([1.00, 0.16, 0.20], np.float32),   # ennemis : rouge néon
    "w": np.array([0.95, 0.97, 1.00], np.float32),   # personnage : blanc pur
    "o": np.array([1.00, 0.72, 0.22], np.float32),   # or (marque / soleil)
}
LAYERS = ("g", "r", "w", "o")
BODY = dict(body=dict(bones=0.0, lines=0.38, rim=1.4, core=0.08))

_TJ = json.load(open("timing_voix.json"))
K = _TJ["K"]
SC = {s["type"]: s["start"] for s in _TJ["scenes"]}
RNG = np.random.default_rng(5)

def man(pos=(0, 0, 0), yaw=0.0, phase=None, sit=False, arms_up=0.0):
    return Body(pos, yaw, phase, sit, arms_up, 1.0 if sit else 1.2)

def M(pos=(0, 0, 0), yaw=0.0, phase=None, sit=False, arms_up=0.0, alpha=1.0):
    kw = dict(BODY); kw["alpha"] = alpha
    return (man(pos, yaw, phase, sit, arms_up), "w", kw)

# --------------------------------------------------------------- ville
def building(x, z, w, d, h, wl=0.55, floors=True):
    m = box([w / 2, h / 2, d / 2], (x, h / 2, z), None, wl, None, inner=False)
    if floors:  # lignes d'étages sur la façade avant (+z) et latérale côté rue
        step = 1.1 if h < 25 else 1.8
        side = -1 if x > 0 else 1
        for y in np.arange(step, h - 0.3, step):
            b = m.add_v([(x - w / 2, y, z + d / 2), (x + w / 2, y, z + d / 2)]); m.e.append((b, b + 1, 0.16))
            b = m.add_v([(x + side * w / 2, y, z - d / 2), (x + side * w / 2, y, z + d / 2)]); m.e.append((b, b + 1, 0.16))
        # antennes
        if h > 14 and (int(x * 7 + z) % 3 == 0):
            b = m.add_v([(x, h, z), (x, h + 2.5, z)]); m.e.append((b, b + 1, 0.5))
    return m

def make_city(gap=3.2, z0=-110, z1=8, xmax=34, seed=3):
    rng = np.random.default_rng(seed); m = Mesh()
    for side in (-1, 1):
        x = gap
        while x < xmax:
            w = rng.uniform(2.2, 4.2)
            z = z1
            while z > z0:
                d = rng.uniform(3, 6.5)
                h = rng.uniform(4, 11) * (1 + 1.6 * (x / xmax)) + (rng.uniform(6, 16) if rng.random() < 0.18 else 0)
                m.merge(building(side * (x + w / 2), z - d / 2, w * 0.92, d * 0.9, h))
                z -= d + rng.uniform(0.3, 1.2)
            x += w + rng.uniform(0.8, 2.0)
    return m

CITY = make_city()

def skyline_far(z=-120, n=70, seed=9):
    rng = np.random.default_rng(seed); m = Mesh(); x = -90.0
    pts = []
    while x < 90:
        w = rng.uniform(2, 6); h = rng.uniform(6, 26) * (1.4 if abs(x) < 25 else 1)
        pts += [(x, h, z), (x + w, h, z)]; x += w
    b = m.add_v([(pts[0][0], 0, z)] + pts + [(pts[-1][0], 0, z)])
    m.e += [(b + i, b + i + 1, 0.9) for i in range(len(pts) + 1)]
    return m

FAR = skyline_far()

def street(z0=-110, z1=12, half=3.2):
    m = Mesh()
    for x in (-half, half):
        b = m.add_v([(x, 0, z0), (x, 0, z1)]); m.e.append((b, b + 1, 0.45))
    for z in np.arange(z1, z0, -3.0):   # pointillés centraux
        b = m.add_v([(0, 0.01, z), (0, 0.01, z - 1.4)]); m.e.append((b, b + 1, 0.5))
    m.merge(grid(0, -40, -half, z0, z1, 2.0, 0.14)).merge(grid(0, half, 40, z0, z1, 2.0, 0.14))
    return m

STREET = street()

RAIN_P = RNG.uniform([-9, 0, -16], [9, 14, 6], (260, 3)); RAIN_S = RNG.uniform(9, 14, 260)
def rain(center, t, alpha=1.0):
    m = Mesh(); c = np.asarray(center, float)
    for p, s in zip(RAIN_P, RAIN_S):
        y = (p[1] - t * s) % 14
        q = c + [p[0], y - 2, p[2]]
        b = m.add_v([q, q + [0.02, 0.45, 0]]); m.e.append((b, b + 1, 0.22))
    return m

def city_layers(t, rain_c=(0, 0, -4), city_a=1.0, fog=95, rain_a=1.0):
    return [(STREET, "g", dict(fog=fog, alpha=city_a)), (CITY, "g", dict(fog=fog, alpha=city_a)),
            (FAR, "g", dict(fog=200, alpha=0.6 * city_a)), (rain(rain_c, t), "g", dict(alpha=0.7 * rain_a))]

# --------------------------------------------------------------- objets
def phone(c, R=None, s=1.0, w=1.2):
    c = np.asarray(c, float); R = np.eye(3) if R is None else np.asarray(R)
    m = box([0.85 * s, 1.7 * s, 0.07 * s], (0, 0, 0), None, w, None, inner=False)
    m.merge(box([0.75 * s, 1.5 * s, 0.075 * s], (0, 0, 0), None, w * 0.5, 6, inner=False))
    m.merge(ring(0.06 * s, (0, 1.6 * s, 0.08 * s), 16, "xy", w * 0.6))
    return Mesh().merge(m, R, c)

def link(c, d, n, L=0.42, Wd=0.2, w=1.0, R=None):
    """maillon : ellipse dans le plan (d, n)."""
    m = Mesh(); P = []
    for i in range(18):
        a = 2 * math.pi * i / 18
        P.append(np.asarray(c) + d * (L / 2) * math.cos(a) + n * (Wd / 2) * math.sin(a))
    if R is not None:
        cc = np.mean(P, 0); P = [cc + R @ (p - cc) for p in P]
    b = m.add_v(P); m.e += [(b + i, b + (i + 1) % 18, w) for i in range(18)]
    return m

ANCH = [(4.2, 0, 1.5), (-4.2, 0, 1.5), (3.0, 0, -3.6), (-3.0, 0, -3.6)]
ATT = [(0.35, 1.0, 0.0), (-0.35, 1.0, 0.0), (0.2, 1.25, -0.1), (-0.2, 1.25, -0.1)]
CHAIN = []   # (centre, d, n, chain idx, rank 0..1)
for ci, (A, B) in enumerate(zip(ANCH, ATT)):
    A = np.array(A, float) + [0, 0.15, 0]; B = np.array(B, float)
    L = np.linalg.norm(B - A); d = (B - A) / L
    n1 = np.cross(d, [0, 1, 0]); n1 /= np.linalg.norm(n1); n2 = np.cross(d, n1)
    nl = int(L / 0.34)
    for j in range(nl):
        s = (j + 0.5) / nl
        sag = 0.35 * math.sin(math.pi * s)
        CHAIN.append((A + (B - A) * s - [0, sag, 0], d, n1 if j % 2 else n2, ci, s))
NL = len(CHAIN)
CH_V = RNG.normal(0, 1, (NL, 3)); CH_V[:, 1] = np.abs(CH_V[:, 1]) + 0.8
CH_S = RNG.uniform(-6, 6, (NL, 3))

def chains_mesh(build=1.0, explode=0.0, tense=0.0, t=0.0):
    m = Mesh()
    for i, (c, d, n, ci, s) in enumerate(CHAIN):
        if s > build: continue
        c2 = np.asarray(c, float).copy(); R = None
        if tense > 0:
            c2 = c2 + [0, 0.35 * math.sin(math.pi * s) * tense, 0] + tense * 0.04 * np.array([math.sin(t * 80 + i), math.sin(t * 67 + i), 0])
        if explode > 0:
            c2 = c2 + CH_V[i] * explode * 4.5 - [0, 3.0 * explode ** 2, 0]
            R = rot(*(CH_S[i] * explode))
        m.merge(link(c2, d, n, R=R))
    for A in ANCH:   # piquets d'ancrage
        m.merge(box([0.12, 0.25, 0.12], np.array(A) + [0, 0.25, 0], None, 1.0, None, inner=False))
    return m

def bus_stop(c=(0, 0, 0)):
    c = np.asarray(c, float); m = Mesh()
    m.merge(box([1.5, 0.05, 0.6], c + [0, 2.4, 0], None, 1.0, 4, inner=False))            # toit
    m.merge(box([1.5, 1.0, 0.03], c + [0, 1.35, -0.55], None, 0.8, 6, inner=False))        # vitre arrière
    for sx in (-1.45, 1.45):
        m.merge(box([0.04, 1.2, 0.04], c + [sx, 1.2, -0.55], None, 0.9, None, inner=False))
    m.merge(box([1.0, 0.04, 0.22], c + [0, 0.5, -0.3], None, 0.9, None, inner=False))       # banc
    m.merge(box([0.03, 0.25, 0.03], c + [-0.9, 0.25, -0.3], None, 0.8, None, inner=False))
    m.merge(box([0.03, 0.25, 0.03], c + [0.9, 0.25, -0.3], None, 0.8, None, inner=False))
    # panneau BUS
    m.merge(box([0.03, 1.6, 0.03], c + [2.0, 1.6, 0.4], None, 0.9, None, inner=False))
    m.merge(Mesh().merge(text3d("BUS", 0.32, 0.08), None, c + [2.0, 3.3, 0.45]))
    m.merge(box([0.5, 0.25, 0.04], c + [2.0, 3.3, 0.4], None, 0.8, None, inner=False))
    return m

def eye(c, r, open_=1.0, look=(0.0, 0.0), w=1.4):
    c = np.asarray(c, float); m = Mesh()
    for sgn in (1, -1):
        P = [c + [r * math.cos(a), sgn * open_ * 0.55 * r * math.sin(a), 0] for a in np.linspace(0, math.pi, 28)]
        b = m.add_v(P); m.e += [(b + i, b + i + 1, w) for i in range(27)]
    if open_ > 0.25:
        ic = c + [look[0] * r * 0.3, look[1] * r * 0.15, 0.02]
        m.merge(ring(0.38 * r * min(1, open_ * 1.3), ic, 40, "xy", w))
        m.merge(ring(0.16 * r * min(1, open_ * 1.3), ic, 24, "xy", w * 1.2))
    return m

# --------------------------------------------------------------- scènes
def S_sky(tg, lt):   # le plus grand mensonge de ta génération
    e = ease(lt)
    tower = building(0, -10, 3.2, 3.2, 12, 1.0)
    fig = M((0, 12, -10), 0.0)
    flick = 1.0
    if K["hook"] - 0.1 < tg < K["hook"] + 1.2:
        flick = 0.45 + 0.55 * (math.sin(tg * 55) > -0.3)
    cam = Cam([9 - 6 * e, 34 - 20.5 * e, 14 - 10 * e], [0, 12.9 - 0.0 * e, -10], 60, t=tg)
    L = city_layers(tg, (0, 10, -8), city_a=flick)
    L[1] = (CITY, "g", dict(fog=95, alpha=flick, reveal=min(1, ease(lt / 0.6) * 1.2)))
    return dict(meshes=L + [(tower, "g", dict(fill=0.03)), fig], cam=cam)

def S_load(tg, lt):   # croire que tu manques de temps -> chargement bloqué à 99 %
    k = tg - SC["loading"]
    ph = phone((0, 3.2, -3), rot(0, -0.35 + 0.5 * ease(lt), 0), 1.35)
    prog = min(0.97, ease_out(min(1, k / 1.2)) * 0.97)
    blink = 1.0 if prog < 0.97 else (0.35 + 0.65 * (math.sin(tg * 14) > 0))
    R = rot(0, -0.35 + 0.5 * ease(lt), 0); c = np.array([0, 3.2, -3])
    bar = Mesh().merge(box([0.75, 0.08, 0.02], (0, -0.2, 0.12), None, 1.0, None, inner=False), R, c)
    fillb = Mesh().merge(box([0.73 * prog, 0.06, 0.02], (-0.73 + 0.73 * prog, -0.2, 0.12), None, 1.0, 3, inner=False), R, c)
    pct = Mesh().merge(text3d(f"{int(round(prog * 100 + 2 * (prog >= 0.97)))}%", 0.42, 0.05), R, R @ np.array([0, 0.45, 0.12]) + c)
    clk = clock(0.55, (0, 3.2 - 1.3, -2.85), tg * 0.9)
    clk = Mesh().merge(clk, R, None)
    e = ease(lt)
    cam = Cam([0.4, 3.0, 4.3 - 1.0 * e], [0, 3.1, -3], 58, t=tg)
    return dict(meshes=city_layers(tg, (0, 0, -3), city_a=0.55) +
                [(ph, "w", dict(fill=0.02, reveal=ease(k / 0.35))), (bar, "w", {}), (fillb, "r", dict(fill=0.25, alpha=blink)),
                 (pct, "r", dict(fill=0.06, alpha=blink)), (clk, "g", dict(alpha=0.8))], cam=cam)

def S_bus(tg, lt):   # tu attends un bus qui ne viendra jamais
    stop = bus_stop((4.6, 0, -6))
    fig = M((4.6, 0, -6.15), 0.0, sit=True)
    a = 0.65 - 0.45 * ease(lt)
    cam = Cam([4.6 + 6.0 * math.sin(a), 1.6 + 0.8 * ease(lt), -6 + 6.0 * math.cos(a)], [3.6, 1.4, -6.5], 58, t=tg)
    # phares du bus qui ne vient pas : deux points au loin qui s'éteignent
    far = 1.0
    hl = Mesh()
    blink = 0.5 + 0.5 * math.sin(tg * 3)
    for sx in (-0.6, 0.6):
        hl.merge(ring(0.18, (sx + 1.2, 0.7, -70), 16, "xy", 2.5))
    return dict(meshes=city_layers(tg, (3, 0, -6)) + [(stop, "g", dict(fill=0.03, reveal=ease(lt / 0.3), fog=60)), fig,
                                                      (hl, "o", dict(alpha=0.35 * blink * far, fog=200))], cam=cam)

def S_eye(tg, lt):   # regarde ton écran. lui aussi il te regarde
    big = phone((0, 3.6, -5.0), None, 2.6, 1.4)
    k = tg - SC["eye"]
    opn = ease((k - 0.6) / 0.35)
    if 1.6 < k % 2.6 < 1.75: opn *= 0.1   # clignement
    ey = eye((0, 3.6, -4.75), 1.2, opn, (math.sin(tg * 1.3), 0))
    fig = M((0, 0, -0.6), math.pi)
    orb = Mesh()
    for j in range(7):
        a = tg * 0.9 + j * 2 * math.pi / 7
        orb.merge(phone((2.6 * math.cos(a), 1.8 + 0.5 * math.sin(a * 2), -0.6 + 2.6 * math.sin(a)), rot(0, -a, 0), 0.32, 0.9))
    e = ease(lt)
    cam = Cam([1.3 - 0.6 * e, 2.0 + 0.3 * e, 4.6 - 1.2 * e], [0, 2.8, -4], 60, t=tg)
    return dict(meshes=city_layers(tg, (0, 0, -3), city_a=0.45) + [(big, "w", dict(fill=0.02, reveal=ease(k / 0.4))),
                (ey, "r", dict(fill=0.05)), (orb, "g", dict(alpha=0.9)), fig], cam=cam)

WORDS = [(txt.upper(), tk, (0, 3.15 + 1.1 * (2 - i), -3.2)) for i, (txt, tk) in enumerate(_TJ["words3d"])]

def S_neon(tg, lt):   # le scroll, le confort, le doute : enseignes néon rouges qui foncent depuis le fond
    meshes = city_layers(tg, (0, 0, -4), city_a=0.7)
    meshes.append(M((0, 0, 0.6), math.pi))
    shake = 0.0; flash = 0.0
    for txt, key, pos in WORDS:
        k = tg - key + 0.22
        if k <= 0: continue
        z = pos[2] - 40 * (1 - ease_in(min(1, k / 0.22)))
        hh = min(0.85, 4.6 / (0.66 * max(1, len(txt))))
        flick = 1.0 if k > 0.6 else (0.4 + 0.6 * (math.sin(k * 90) > 0))
        wm = Mesh().merge(text3d(txt, hh, 0.3), None, (pos[0], pos[1], z))
        wm.merge(box([0.36 * hh * len(txt) + 0.25, hh * 0.62, 0.05], (pos[0], pos[1], z - 0.2), None, 0.8, None, inner=False))
        meshes.append((wm, "r", dict(fill=0.07, alpha=flick)))
        land = k - 0.22
        if 0 <= land < 0.25:
            shake = max(shake, 0.3 * (1 - land / 0.25)); flash = max(flash, 0.15 * (1 - land / 0.25))
    e = ease(lt)
    cam = Cam([0.35 * math.sin(lt * 2), 1.9 + 0.4 * e, 6.8 - 0.6 * e], [0, 3.3, -3], 60, shake=shake, t=tg)
    return dict(meshes=meshes, cam=cam, flash=flash)

def S_chains(tg, lt):   # c'est toi qui as forgé ces chaînes, maillon après maillon
    b0, b1 = K["build_start"] - 0.6, K["build_end"] + 0.5
    build = min(1.0, max(0.0, (tg - b0) / (b1 - b0)))
    ch = chains_mesh(build)
    e = ease(lt)
    a = 0.3 + 1.3 * e
    cam = Cam([6.5 * math.sin(a), 2.2 + 3.8 * e, 6.5 * math.cos(a)], [0, 1.0, -0.5], 58, t=tg)
    return dict(meshes=city_layers(tg, (0, 0, -1), city_a=0.5) + [M((0, 0, 0), 0.0), (ch, "r", {})], cam=cam)

def S_snap(tg, lt):   # brise-les !
    T0 = K["boom"]; k = max(0.0, tg - T0)
    tense = max(0.0, 1 - (T0 - tg) / 1.8) if tg < T0 else 0.0
    arms = ease((tg - (T0 - 0.8)) / 0.7)
    ch = chains_mesh(1.0, ease_out(min(1, k / 1.1)) * (1 + 0.25 * k) if k > 0 else 0.0, tense, tg)
    meshes = city_layers(tg, (0, 0, -1), city_a=0.5 + (0.5 * math.exp(-k * 3) if k > 0 else 0)) + [M((0, 0, 0), 0.0, arms_up=arms), (ch, "r", {})]
    flash = 0.0; shake = tense * 0.07
    if k > 0:
        flash = 1.0 * math.exp(-k * 6); shake = 0.8 * math.exp(-k * 4)
        for j in range(3):
            rr = (k - j * 0.12) * 10
            if rr > 0.2: meshes.append((ring(rr, (0, 0.02, 0), 96, "xz", 1.4), "w", dict(alpha=max(0, 1 - rr / 15))))
    e = ease(lt)
    cam = Cam([0.4, 0.6 + 0.6 * e, 4.2 + 2.5 * ease(k / 1.2)], [0, 1.5 + 0.4 * e, 0], 64, shake=shake, t=tg)
    return dict(meshes=meshes, cam=cam, flash=flash)

GATES = [(-6.0, K["gate1"]), (-12.0, K["gate2"]), (-18.0, 99)]
def laser_gate(z, ex):
    m = Mesh(); rng = np.random.default_rng(int(-z))
    for sx in (-2.6, 2.6):
        m.merge(box([0.1, 1.4, 0.1], (sx, 1.4, z), None, 1.0, None, inner=False))
    for j in range(7):
        y = 0.35 + j * 0.36
        if ex <= 0:
            b = m.add_v([(-2.5, y, z), (2.5, y, z)]); m.e.append((b, b + 1, 1.3))
        else:
            for s in range(5):   # le laser se brise en segments
                x0 = -2.5 + s; v = np.array([rng.normal(0, 1), rng.uniform(0.2, 1.4), -rng.uniform(0.5, 2)]) * ex * 4
                p = np.array([x0, y, z]) + v - [0, 1.5 * ex * ex, 0]; q = p + rot(*(rng.uniform(-3, 3, 3) * ex)) @ np.array([1.0, 0, 0])
                b = m.add_v([p, q]); m.e.append((b, b + 1, 1.3 * max(0, 1 - ex * 0.6)))
    return m

def S_lasers(tg, lt):   # une heure sans écran. puis deux. sans excuse
    meshes = city_layers(tg, (0, 0, -10), fog=110)
    flash = 0.0; shake = 0.0
    for gz, ht in GATES:
        k = tg - ht
        meshes.append((laser_gate(gz, ease_out(min(1, k / 0.9)) if k > 0 else 0), "r", {}))
        if 0 < k < 0.3: flash = max(flash, 0.3 * (1 - k / 0.3)); shake = max(shake, 0.3 * (1 - k / 0.3))
    wz = np.interp(tg, [SC["lasers"], K["gate1"], K["gate2"], SC["dawn"] + 0.1], [-1.0, -5.5, -11.5, -14.5])
    meshes.append(M((0, 0, wz), math.pi, phase=tg * 8.0))
    cam = Cam([-1.4, 2.1, wz + 5.8], [0, 1.4, wz - 7], 62, shake=shake, t=tg)
    return dict(meshes=meshes, cam=cam, flash=flash)

def S_dawn(tg, lt):   # et un matin... tu te lèves libre
    e = ease(lt)
    sun_y = 2 + 26 * ease((tg - K["sunrise"]) / 2.6)
    sun = Mesh()
    for r, w in ((18, 4.0), (22, 2.0), (27, 1.2)):
        sun.merge(ring(r, (0, sun_y, -110), 96, "xy", w))
    for kk in range(26):
        ang = math.pi * kk / 25; d = np.array([math.cos(ang), math.sin(ang), 0])
        b = sun.add_v([np.array([0, sun_y, -110]) + d * 31, np.array([0, sun_y, -110]) + d * (44 + 10 * (kk % 3))])
        sun.e.append((b, b + 1, 1.2))
    roof = grid(14, -3, 3, -4, 2, 1.0, 0.4)
    arms = ease((tg - K["arms_up"]) / 0.8)
    cam = Cam([1.0, 15.3 + 0.5 * e, 5.8 - 0.8 * e], [0, 17.0 + 3 * e, -60], 60, t=tg)
    return dict(meshes=[(CITY, "g", dict(fog=150, alpha=0.6)), (FAR, "g", dict(fog=260, alpha=0.8)),
                        (sun, "o", dict(alpha=0.5 + 0.5 * e, fog=300)), (roof, "g", {}),
                        M((0, 14, -1.5), math.pi, arms_up=arms)], cam=cam)

NOTIF = [(RNG.uniform(0, 6.283), RNG.uniform(2.4, 3.6), RNG.uniform(-1.4, 1.4), RNG.uniform(0.4, 0.9)) for _ in range(14)]
def S_phoneq(tg, lt):   # combien d'heures sur ton écran par jour ?
    pulse = 0.0
    for tk in _TJ["q_pulses"]:
        d = tg - tk
        if 0 <= d < 0.5: pulse = max(pulse, math.exp(-d * 7))
    sc = 1.0 + 0.12 * pulse
    R = rot(0, 0.45 * math.sin(tg * 0.8), 0); c = np.array([0, 3.4, -2.5])
    ph = phone(c, R, 1.7 * sc, 1.3)
    q = Mesh().merge(text3d("?", 1.6 * sc, 0.2), R, c + R @ np.array([0, 0, 0.15]))
    alpha = 1.0
    d = tg - K["q_end"]
    if d > 0: alpha = max(0.0, 1 - d / 0.9) * (0.3 + 0.7 * (math.sin(tg * 70) > 0))
    orb = Mesh()
    for a0, r, y, sp in NOTIF:
        a = a0 + tg * sp
        orb.merge(box([0.42, 0.13, 0.03], (r * math.cos(a), 3.2 + y, -2.5 + r * math.sin(a)), rot(0, -a + 1.57, 0), 0.8, None, inner=False))
        orb.merge(ring(0.07, (r * math.cos(a), 3.2 + y, -2.5 + r * math.sin(a)), 12, "xy", 1.0))
    cam = Cam([0.7 * math.sin(tg * 0.5), 3.1, 7.4 - 0.8 * ease(lt)], [0, 3.3, -2.5], 60, shake=0.22 * pulse, t=tg)
    return dict(meshes=city_layers(tg, (0, 0, -2), city_a=0.4) + [(ph, "w", dict(fill=0.02, alpha=alpha, reveal=ease(lt / 0.12))),
                (q, "r", dict(fill=0.08, alpha=alpha)), (orb, "r", dict(alpha=0.7 * alpha))],
                cam=cam, flash=0.1 * pulse)

def S_logo(tg, lt):
    k = tg - SC["logo"]
    Rl = rot(0, 0.5 * (1 - ease(k / 2.4)), 0)
    logo = Mesh().merge(text3d("MINDSET", 0.5, 0.26), Rl, Rl @ np.array([0, 0.5, 0]) + [0, 3.45, -2])
    logo.merge(text3d("24", 1.0, 0.36), Rl, Rl @ np.array([0, -0.5, 0]) + [0, 3.45, -2])
    cam = Cam([0, 2.6, 6.0 - 1.2 * ease(lt)], [0, 2.3, -3], 52, t=tg)
    fade = 1 - ease((tg - (K['end'] - 0.7)) / 0.7)
    return dict(meshes=[(STREET, "g", dict(alpha=0.5 * fade, fog=80)), (FAR, "g", dict(alpha=0.5 * fade, fog=200)),
                        (rain((0, 0, -2), tg), "g", dict(alpha=0.5 * fade)),
                        (logo, "o", dict(reveal=ease(k / 1.0), fill=0.06, alpha=fade))], cam=cam, fade=fade)

SCENE_TYPES = {"skyline": S_sky, "loading": S_load, "busstop": S_bus, "eye": S_eye, "neon": S_neon, "chains": S_chains,
               "snap": S_snap, "lasers": S_lasers, "dawn": S_dawn, "phoneq": S_phoneq, "logo": S_logo}
SCENES = [SCENE_TYPES[s["type"]] for s in _TJ["scenes"]]

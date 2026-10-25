# -*- coding: utf-8 -*-
"""Scènes v2 calées sur la voix (temps absolus en secondes)."""
import math
import numpy as np
from engine import *
from body import Body

def figure(pos=(0, 0, 0), yaw=0.0, phase=None, sit=False, s=1.0, w=1.0, arms_up=0.0):
    return Body(pos, yaw, phase, sit, arms_up, 1.0 if sit else 1.2)


# temps clés tirés de la voix (take1)
import json as _json
_TJ = _json.load(open("timing_voix.json"))
K = _TJ["K"]                                   # rôles -> temps (s)
SC = {s["type"]: s["start"] for s in _TJ["scenes"]}   # type de scène -> début

RNG = np.random.default_rng(11)

def dust(center, n=160, spread=(8, 5, 8)):
    c = np.asarray(center, float); s = np.asarray(spread, float)
    return c + (RNG.random((n, 3)) - 0.5) * s * 2

DUST = {}

def particles(key, center, t, n=160, spread=(8, 5, 8), rise=0.15):
    if key not in DUST: DUST[key] = dust(center, n, spread)
    P = DUST[key].copy()
    P[:, 1] += rise * t + 0.08 * np.sin(t * 0.7 + P[:, 0])
    P[:, 0] += 0.06 * np.sin(t * 0.5 + P[:, 2])
    return P

def floor(ext=14, step=1.0, y=0.0, z0=-30, z1=12):
    return grid(y, -ext, ext, z0, z1, step, 0.32)

# --------------------------------------------------------------- briques
def brick_ring(cx, cz, half, rows, bw=1.0, bh=0.5, bd=0.35):
    out = []
    n = int(round(2 * half / bw))
    for r in range(rows):
        off = (bw / 2) if r % 2 else 0
        y = bh / 2 + r * bh
        for i in range(n):
            x = -half + bw / 2 + i * bw + off
            if x + bw / 2 > half + 1e-6: continue
            hz = np.array([bw / 2 * 0.95, bh / 2 * 0.9, bd / 2]); hx = np.array([bd / 2, bh / 2 * 0.9, bw / 2 * 0.95])
            out += [(np.array([cx + x, y, cz - half]), hz, np.array([0, 0, -1.]), r),
                    (np.array([cx + x, y, cz + half]), hz, np.array([0, 0, 1.]), r),
                    (np.array([cx - half, y, cz + x]), hx, np.array([-1, 0, 0.]), r),
                    (np.array([cx + half, y, cz + x]), hx, np.array([1, 0, 0.]), r)]
    return out

RING = brick_ring(0, 0, 2.5, 7)
NB = len(RING)
EXV = RNG.uniform(0.7, 1.5, NB); EXU = RNG.uniform(0.3, 1.6, NB); EXS = RNG.uniform(-5, 5, (NB, 3))
ORDER = np.argsort([b[3] * 100 + RNG.random() for b in RING])   # rang par rang
RANKB = np.empty(NB); RANKB[ORDER] = np.arange(NB)

def bricks_mesh(build=1.0, explode=0.0, shake=0.0, t=0.0, drop=1.6):
    m = Mesh()
    for i, (c, h, n, r) in enumerate(RING):
        k = build * NB - RANKB[i]
        if k <= 0: continue
        c2 = c.copy(); R = None
        if k < 3:  # brique en train de tomber
            c2 = c2 + [0, drop * (1 - ease_out(k / 3)), 0]
        if shake > 0:
            c2 = c2 + shake * 0.05 * np.array([math.sin(t * 90 + i), math.sin(t * 77 + i * 1.7), 0])
        if explode > 0:
            d = explode * 7.5 * EXV[i]
            c2 = c2 + n * d + np.array([0, EXU[i] * d * 0.55 - 2.2 * explode ** 2, 0])
            R = rot(*(EXS[i] * explode))
        m.merge(box(h, c2, R, 0.7, None, inner=False))
    return m

# --------------------------------------------------------------- scènes
def S0(tg, lt):   # le plus grand mensonge sur la réussite
    m = floor()
    st = Mesh()
    for i in range(9):
        st.merge(box([1.9, 0.18, 0.55], [0, 0.18 + i * 0.36, 2.2 - i * 0.62], None, 1.0, 6))
    summit = pyramid(1.4, 2.1, (0, 3.25, -3.3), 1.3, 7, 8)
    rev = ease(lt / 0.55)
    # au mot « mensonge » le sommet clignote (glitch)
    flick = 1.0
    if K["hook"] - 0.2 < tg < K["hook"] + 1.4:
        flick = 0.35 + 0.65 * (math.sin(tg * 63) > -0.2) * (0.7 + 0.3 * math.sin(tg * 17))
    a = 0.55 - 0.7 * ease(lt)
    cam = Cam([8.5 * math.sin(a), 1.4 + 2.6 * ease(lt), 8.5 * math.cos(a) - 0.5], [0, 2.6, -1.2], 58, t=tg)
    return dict(meshes=[(m, "g", dict(reveal=min(1, rev * 1.3))), (st, "g", dict(reveal=rev)),
                        (summit, "g", dict(reveal=ease((lt - 0.15) / 0.5), alpha=flick))],
                cam=cam, dust=particles("s0", (0, 2, -1), tg))

def S1(tg, lt):   # question de chance
    m = floor()
    q = text3d("?", 4.2, 0.9)
    qm = Mesh().merge(q, rot(0, -0.5 + 0.9 * lt, 0), (0, 3.0, -6))
    d = Mesh()
    for k, (x, sp, off, z) in enumerate(((-1.2, 1.0, 0.3, 0.6), (1.3, -1.2, 1.9, -0.6))):
        R = rot(lt * 2.2 * sp + off, lt * 1.6 * sp + off, lt * 1.1 + off)
        y = 1.0 + 1.3 * abs(math.sin(lt * math.pi * 1.2 + k * 1.3))
        d.merge(dice(0.75, [x, y, z], R))
    cam = Cam([0.6, 2.2, 6.8 - 1.8 * ease(lt)], [0, 2.0, -2], 58, t=tg)
    return dict(meshes=[(m, "g", {}), (qm, "g", dict(reveal=ease(lt / 0.5), fill=0.05)),
                        (d, "g", dict(reveal=ease(lt / 0.35)))],
                cam=cam, dust=particles("s1", (0, 2, -1), tg))

def S2(tg, lt):   # personne n'a jamais réussi en restant assis
    m = floor().merge(vgrid("z", -5, -8, 8, 0, 7, 1.0, 0.22))
    c = chair((0, 0, -0.3)); sb = figure((0, 0, -0.3), 0, sit=True)
    clk = clock(1.0, (0, 3.1, -1.2), tg * 2.2)
    a = -0.6 + 0.5 * ease(lt)
    cam = Cam([5.2 * math.sin(a), 1.5 + 0.6 * lt, 5.2 * math.cos(a) - 0.3 - 1.0 * ease(lt)], [0, 1.6, -0.5], 58, t=tg)
    return dict(meshes=[(m, "g", {}), (c, "g", dict(reveal=ease(lt / 0.4))), (sb, "g", dict(alpha=ease(lt / 0.3))),
                        (clk, "g", dict(reveal=ease((lt - 0.15) / 0.35)))],
                cam=cam, dust=particles("s2", (0, 1.5, -0.5), tg, rise=-0.05))

def room(scale=1.0):
    m = Mesh()
    hw, hd, h = 4.0 * scale, 4.0 * scale, 5.0
    m.merge(grid(0, -hw, hw, -hd, hd, 1.0 * scale, 0.35))
    m.merge(grid(h, -hw, hw, -hd, hd, 1.0 * scale, 0.2))
    m.merge(vgrid("x", -hw, -hd, hd, 0, h, 1.0 * scale, 0.32))
    m.merge(vgrid("x", hw, -hd, hd, 0, h, 1.0 * scale, 0.32))
    m.merge(vgrid("z", -hd, -hw, hw, 0, h, 1.0 * scale, 0.32))
    m.merge(box([hw, h / 2, hd], (0, h / 2, 0), None, 1.3, None, inner=False))
    return m

def S3(tg, lt):   # regarde ces murs autour de toi
    sc = 1.0 - 0.25 * ease(lt)   # les murs se rapprochent
    r = room(sc)
    f = figure((0, 0, -0.5), math.pi)
    a = 0.25 * math.sin(lt * 1.5)
    cam = Cam([1.2 * math.sin(a) + 0.4, 2.3 - 0.3 * lt, 3.6 - 1.4 * ease(lt)], [0, 1.4, -2.5], 66, t=tg)
    return dict(meshes=[(r, "g", dict(reveal=ease(lt / 0.45), fill=0.04)), (f, "g", {})],
                cam=cam, dust=particles("s3", (0, 2, -1), tg, spread=(3.5, 2.5, 3.5)))

WORDS = [(txt.upper(), tk, (0, 1.25 + 0.9 * i, 1.5)) for i, (txt, tk) in enumerate(_TJ["words3d"])]

def S4(tg, lt):   # faits de quoi ? de peur, d'excuses, de demain
    m = floor()
    f = figure((0, 0, -0.8), 0.0)
    meshes = [(m, "g", {}), (f, "g", {})]
    shake = 0.0; flash = 0.0
    for txt, key, pos in WORDS:
        k = tg - key + 0.25
        if k <= 0: continue
        y = pos[1] + 5.0 * (1 - ease_in(min(1, k / 0.25)))        # chute rapide
        hh = min(0.7, 4.0 / (0.66 * max(1, len(txt))))
        w = Mesh().merge(text3d(txt, hh, 0.4), None, (pos[0], y, pos[2]))
        w.merge(box([max(0.8, 0.37 * hh * len(txt)), 0.4, 0.26], (pos[0], y, pos[2] - 0.05), None, 0.6, 3, inner=False))
        meshes.append((w, "g", dict(fill=0.05)))
        land = k - 0.25
        if 0 <= land < 0.25:
            shake = max(shake, 0.35 * (1 - land / 0.25)); flash = max(flash, 0.18 * (1 - land / 0.25))
    a = 0.3 * math.sin(lt * 1.2)
    cam = Cam([3.5 * math.sin(a), 1.9 + 0.5 * lt, 8.6 + 0.8 * ease(lt)], [0, 2.1, 0.5], 60, shake=shake, t=tg)
    return dict(meshes=meshes, cam=cam, flash=flash, dust=particles("s4", (0, 2, 0), tg))

def S5(tg, lt):   # c'est toi qui les as construits. brique par brique
    m = floor()
    f = figure((0, 0, 0), 0.0)
    build = min(1.0, max(0.0, (tg - (K['build_start'] - 0.9)) / (K['build_end'] + 1.2 - (K['build_start'] - 0.9))))
    b = bricks_mesh(build)
    e = ease(lt)
    a = 0.4 + 1.1 * e
    cam = Cam([7.5 * math.sin(a) * (1 - 0.6 * e), 1.8 + 9.5 * e, 7.5 * math.cos(a) * (1 - 0.6 * e) + 0.01], [0, 0.6, 0], 58, t=tg)
    return dict(meshes=[(m, "g", {}), (f, "g", {}), (b, "g", dict(fill=0.035))],
                cam=cam, dust=particles("s5", (0, 2, 0), tg))

def S6(tg, lt):   # tu peux le démolir
    m = floor(ext=20, z0=-24, z1=20)
    T0 = K["boom"]
    k = max(0.0, tg - T0)
    arms = ease((tg - (T0 - 0.9)) / 0.8)
    f = figure((0, 0, 0), 0.0, arms_up=arms)
    ex = ease_out(min(1, k / 1.0)) * (1 + 0.2 * k)
    tension = max(0.0, 1 - (T0 - tg) / 2.0) if tg < T0 else 0.0
    b = bricks_mesh(1.0, ex if k > 0 else 0.0, shake=tension * 2, t=tg)
    meshes = [(m, "g", {}), (f, "g", {}), (b, "g", dict(fill=0.035))]
    flash = 0.0; shake = tension * 0.06
    if k > 0:
        flash = 1.1 * math.exp(-k * 6)
        shake = 0.85 * math.exp(-k * 4)
        for j in range(3):  # ondes de choc au sol
            rr = (k - j * 0.12) * 9
            if rr > 0.2:
                meshes.append((ring(rr, (0, 0.02, 0), 96, "xz", 1.4), "g", dict(alpha=max(0, 1 - rr / 14))))
    e = ease(lt)
    cam = Cam([2.4 + 1.5 * e, 9.0 - 6.0 * e, 4.5 + 4.5 * ease(k / 1.2)], [0, 0.9, 0], 60, shake=shake, t=tg)
    return dict(meshes=meshes, cam=cam, flash=flash, dust=particles("s6", (0, 2, 0), tg))

GATES = [(-6.0, K["gate1"]), (-12.0, K["gate2"]), (-18.0, 99)]

def gate_mesh(z, explode):
    m = Mesh(); rng = np.random.default_rng(int(-z * 10))
    for r in range(6):
        off = 0.5 if r % 2 else 0
        for i in range(-3, 3):
            x = i + 0.5 + off
            if abs(x) > 3.0: continue
            c = np.array([x, 0.25 + r * 0.5, z]); R = None
            if explode > 0:
                v = np.array([x * 0.6 + rng.normal(0, .3), rng.uniform(0.3, 1.5), -rng.uniform(0.5, 2.0)])
                c = c + v * explode * 5 + [0, -1.5 * explode ** 2, 0]
                R = rot(*(rng.uniform(-5, 5, 3) * explode))
            m.merge(box([0.47, 0.22, 0.17], c, R, 0.9, None, inner=False))
    return m

def S7(tg, lt):   # une seule action par jour, un seul mur à la fois
    m = floor(ext=10, z0=-40, z1=8)
    # le personnage avance ; chaque mur explose quand il l'atteint
    z = -1.0 - 4.4 * (tg - 23.84) / 1.5
    z = max(z, -1.0 - 4.4 * (27.36 - 23.84) / 1.5)
    meshes = [(m, "g", {})]
    flash = 0.0; shake = 0.0
    for gz, ht in GATES:
        k = tg - ht
        meshes.append((gate_mesh(gz, ease_out(min(1, k / 1.0)) if k > 0 else 0), "g", dict(fill=0.015)))
        if 0 < k < 0.3: flash = max(flash, 0.3 * (1 - k / 0.3)); shake = max(shake, 0.35 * (1 - k / 0.3))
    # vitesse : marche vers le mur suivant, frappe au moment clé
    walk_z = np.interp(tg, [SC["gates"], K["gate1"], K["gate2"], SC["sunrise"] + 0.1], [-1.0, -5.4, -11.4, -14.5])
    f = figure((0, 0, walk_z), math.pi, phase=tg * 7.5)
    meshes.append((f, "g", {}))
    cam = Cam([0.9, 2.3, walk_z + 4.2], [0, 1.4, walk_z - 6], 60, shake=shake, t=tg)
    return dict(meshes=meshes, cam=cam, flash=flash, dust=particles("s7", (0, 2, -8), tg, spread=(5, 3, 12)))

def terrain():
    m = Mesh()
    xs = np.linspace(-60, 60, 61)
    for zi, z in enumerate(np.linspace(-90, -40, 11)):
        ys = 4 + 6 * np.sin(xs * 0.07 + zi) * np.exp(-((z + 70) / 30) ** 2) + 5 * np.abs(np.sin(xs * 0.031 + 1.3)) * (zi / 10)
        P = [(x, y, z) for x, y in zip(xs, ys)]
        b = m.add_v(P); m.e += [(b + i, b + i + 1, 0.55) for i in range(len(P) - 1)]
    return m

TERR = terrain()

def S8(tg, lt):   # et un matin... plus rien entre toi et ton potentiel
    m = grid(0, -50, 50, -90, 10, 2.0, 0.3)
    e = ease(lt)
    sun_y = -8 + 16 * ease((tg - K["sunrise"]) / 3.2)
    sun = Mesh()
    for r, w in ((11, 5.0), (13.5, 2.4), (17, 1.5), (22, 1.0)):
        sun.merge(ring(r, (0, sun_y, -95), 96, "xy", w))
    for k in range(28):  # rayons
        ang = math.pi * k / 27
        d = np.array([math.cos(ang), math.sin(ang), 0])
        b = sun.add_v([np.array([0, sun_y, -95]) + d * 24, np.array([0, sun_y, -95]) + d * (34 + 9 * (k % 3))])
        sun.e.append((b, b + 1, 1.3))
    arms = ease((tg - K["arms_up"]) / 0.9)
    f = figure((0, 0, -2.5), math.pi, arms_up=arms)
    cam = Cam([0.6, 1.1 + 0.8 * e, 3.8 - 0.8 * e], [0, 2.6 + 1.6 * e, -40], 60, t=tg)
    return dict(meshes=[(m, "g", dict(fog=120)), (TERR, "g", dict(reveal=ease(lt / 0.6), fog=220)),
                        (sun, "g", dict(alpha=0.5 + 0.5 * e, fog=260)), (f, "g", {})],
                cam=cam, dust=particles("s8", (0, 3, -6), tg, spread=(10, 4, 8)), sun=(sun_y, e))

def S9(tg, lt):   # logo MINDSET 24
    m = grid(0, -30, 30, -60, 10, 2.0, 0.3)
    k = tg - SC["logo"]
    Rl = rot(0, 0.5 * (1 - ease(k / 2.4)), 0)
    logo = Mesh().merge(text3d("MINDSET", 0.5, 0.26), Rl, Rl @ np.array([0, 0.5, 0]) + [0, 3.45, -2])
    logo.merge(text3d("24", 1.0, 0.36), Rl, Rl @ np.array([0, -0.5, 0]) + [0, 3.45, -2])
    cam = Cam([0, 2.6, 6.0 - 1.2 * ease(lt)], [0, 2.3, -3], 52, t=tg)
    fade = 1 - ease((tg - (K['end'] - 0.7)) / 0.7)
    return dict(meshes=[(m, "g", dict(alpha=0.6 * fade, fog=80)),
                        (logo, "o", dict(reveal=ease(k / 1.0), fill=0.06, alpha=fade))],
                cam=cam, dust=particles("s9", (0, 3, -2), tg), fade=fade)

ORBIT = [(RNG.uniform(0, 6.283), RNG.uniform(2.2, 3.6), RNG.uniform(-1.2, 1.2), RNG.uniform(0.4, 1.0)) for _ in range(22)]

def SQ(tg, lt):   # question : quel mur tu détruis CETTE semaine ?
    m = floor().merge(vgrid("z", -7, -10, 10, 0, 9, 1.0, 0.2))
    pulse = 0.0
    for tk in _TJ["q_pulses"]:
        d = tg - tk
        if 0 <= d < 0.5: pulse = max(pulse, math.exp(-d * 7))
    sc = 1.0 + 0.18 * pulse
    q = Mesh().merge(text3d("?", 3.4 * sc, 0.9), rot(0, tg * 1.6, 0), (0, 3.4, -2.5))
    alpha = 1.0
    d = tg - K["q_end"]
    if d > 0:   # le « ? » se meurt en clignotant : abandon
        alpha = max(0.0, (1 - d / 0.9)) * (0.3 + 0.7 * (math.sin(tg * 70) > 0))
    orb = Mesh()
    for a0, r, y, sp in ORBIT:
        a = a0 + tg * sp
        orb.merge(box([0.4, 0.2, 0.17], (r * math.cos(a), 3.2 + y, -2.5 + r * math.sin(a)), rot(a, a * 0.7, 0), 0.8, None, inner=False))
    rings = Mesh()
    for j in range(3):
        rr = 2.2 + ((tg * 1.3 + j * 0.9) % 2.7)
        rings.merge(ring(rr, (0, 0.03, -2.5), 72, "xz", 1.0))
    shake = 0.25 * pulse
    cam = Cam([0.8 * math.sin(tg * 0.5), 3.0, 7.6 - 0.8 * ease(lt)], [0, 3.2, -2.5], 60, shake=shake, t=tg)
    return dict(meshes=[(m, "g", dict(alpha=0.8)), (q, "g", dict(reveal=ease(lt / 0.12), fill=0.06, alpha=alpha)),
                        (orb, "g", dict(alpha=alpha)), (rings, "g", dict(alpha=0.6 * alpha))],
                cam=cam, flash=0.1 * pulse, dust=particles("sq", (0, 3, -2.5), tg))

SCENE_TYPES = {"stairs": S0, "dice": S1, "chair": S2, "room": S3, "words": S4, "build": S5, "explode": S6,
               "gates": S7, "sunrise": S8, "question": SQ, "logo": S9}
SCENES = [SCENE_TYPES[s["type"]] for s in _TJ["scenes"]]

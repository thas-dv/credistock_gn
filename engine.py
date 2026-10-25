# -*- coding: utf-8 -*-
"""Moteur hologramme néon v2 : maillages filaires 3D, faces semi-transparentes maillées,
apparition « dessinée », bloom multi-échelle, persistance phosphore, particules."""
import math
import numpy as np
import cv2

W, H = 1080, 1920
NEAR = 0.12

# couleurs (RGB 0..1)
COLORS = {
    "g": np.array([0.80, 0.90, 1.00], np.float32),   # blanc argenté (hologramme)
    "o": np.array([1.00, 0.72, 0.22], np.float32),   # or (marque)
}

def ease(t):
    t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)

def ease_out(t):
    t = min(1.0, max(0.0, t)); return 1 - (1 - t) ** 3

def ease_in(t):
    t = min(1.0, max(0.0, t)); return t ** 3

def rot(ax=0.0, ay=0.0, az=0.0):
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz

# ------------------------------------------------------------------ maillage
class Mesh:
    """verts (N,3) ; edges [(i,j,w)] ; quads [(a,b,c,d,n_mesh)] ; polys [[contour idx...],...] (faces pleines)."""
    def __init__(self):
        self.v = []; self.e = []; self.q = []; self.p = []

    def add_v(self, pts):
        base = len(self.v); self.v.extend([np.asarray(p, float) for p in pts]); return base

    def merge(self, other, M=None, t=None, s=1.0):
        base = len(self.v)
        V = np.array(other.v, float) * s if other.v else np.zeros((0, 3))
        if M is not None and len(V): V = V @ np.asarray(M).T
        if t is not None and len(V): V = V + np.asarray(t, float)
        self.v.extend(list(V))
        self.e += [(a + base, b + base, w) for a, b, w in other.e]
        self.q += [(a + base, b + base, c + base, d + base, n) for a, b, c, d, n in other.q]
        self.p += [[[i + base for i in c] for c in poly] for poly in other.p]
        return self

    def arr(self):
        return np.array(self.v, float) if self.v else np.zeros((0, 3))

CUBE = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
CUBE_E = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
CUBE_F = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (3, 2, 6, 7), (0, 3, 7, 4), (1, 2, 6, 5)]

def box(h, c=(0, 0, 0), R=None, w=1.0, mesh=4, inner=True):
    """boîte : arêtes + faces maillées ; inner=True ajoute un cadre intérieur (effet poutre épaisse)."""
    m = Mesh(); h = np.asarray(h, float)
    V = np.array(CUBE, float) * h
    if R is not None: V = V @ np.asarray(R).T
    V = V + np.asarray(c, float)
    b = m.add_v(V)
    m.e += [(b + i, b + j, w) for i, j in CUBE_E]
    if mesh is not None:
        m.q += [(b + a, b + bb, b + cc, b + d, mesh) for a, bb, cc, d in CUBE_F]
    if inner:
        V2 = np.array(CUBE, float) * (h * 0.9)
        if R is not None: V2 = V2 @ np.asarray(R).T
        V2 = V2 + np.asarray(c, float)
        b2 = m.add_v(V2)
        m.e += [(b2 + i, b2 + j, w * 0.35) for i, j in CUBE_E]
    return m

def grid(y, x0, x1, z0, z1, step, w=0.35):
    m = Mesh()
    for x in np.arange(x0, x1 + 1e-6, step):
        b = m.add_v([(x, y, z0), (x, y, z1)]); m.e.append((b, b + 1, w))
    for z in np.arange(z0, z1 + 1e-6, step):
        b = m.add_v([(x0, y, z), (x1, y, z)]); m.e.append((b, b + 1, w))
    return m

def vgrid(axis, val, a0, a1, y0, y1, step, w=0.3):
    m = Mesh()
    for a in np.arange(a0, a1 + 1e-6, step):
        P = [(val, y0, a), (val, y1, a)] if axis == "x" else [(a, y0, val), (a, y1, val)]
        b = m.add_v(P); m.e.append((b, b + 1, w))
    for y in np.arange(y0, y1 + 1e-6, step):
        P = [(val, y, a0), (val, y, a1)] if axis == "x" else [(a0, y, val), (a1, y, val)]
        b = m.add_v(P); m.e.append((b, b + 1, w))
    return m

def pyramid(half, h, c=(0, 0, 0), w=1.2, rings=8, mesh=10):
    m = Mesh(); c = np.asarray(c, float)
    B = [c + [sx * half, 0, sz * half] for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    T = c + [0, h, 0]
    b = m.add_v(B + [T])
    m.e += [(b + i, b + (i + 1) % 4, w) for i in range(4)] + [(b + i, b + 4, w) for i in range(4)]
    # faces triangulaires maillées (quad dégénéré: sommet doublé)
    for i in range(4):
        m.q.append((b + i, b + (i + 1) % 4, b + 4, b + 4, mesh))
    for k in range(1, rings):
        f = k / rings
        R = [p + (T - p) * f for p in B]
        bb = m.add_v(R); m.e += [(bb + i, bb + (i + 1) % 4, w * 0.3) for i in range(4)]
    # socle
    S = [c + [sx * half * 1.12, -0.25, sz * half * 1.12] for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    S2 = [p + [0, 0.25, 0] for p in S]
    bs = m.add_v(S + S2)
    m.e += [(bs + i, bs + (i + 1) % 4, w * 0.8) for i in range(4)] + [(bs + 4 + i, bs + 4 + (i + 1) % 4, w * 0.8) for i in range(4)]
    m.e += [(bs + i, bs + 4 + i, w * 0.6) for i in range(4)]
    return m

def ring(r, c=(0, 0, 0), n=64, plane="xy", w=1.0, R=None):
    m = Mesh(); c = np.asarray(c, float); P = []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = np.array([r * math.cos(a), r * math.sin(a), 0]) if plane == "xy" else np.array([r * math.cos(a), 0, r * math.sin(a)])
        if R is not None: d = np.asarray(R) @ d
        P.append(c + d)
    b = m.add_v(P); m.e += [(b + i, b + (i + 1) % n, w) for i in range(n)]
    return m

def figure(pos=(0, 0, 0), yaw=0.0, phase=0.0, sit=False, s=1.0, w=1.1, arms_up=0.0):
    """personnage holographique en volumes (tête, cou, buste effilé, bras, jambes)."""
    m = Mesh(); pos = np.asarray(pos, float); Ry = rot(0, yaw, 0)
    def part(c, h, R=None, mesh=3):
        R2 = Ry @ (R if R is not None else np.eye(3))
        m.merge(box(np.asarray(h) * s, pos + Ry @ (np.asarray(c, float) * s), R2, w, mesh, inner=False))
    if not sit:
        sw = 0.45 * math.sin(phase); bob = 0.03 * abs(math.sin(phase))
        part([0, 1.74 + bob, 0], [0.12, 0.14, 0.13])
        part([0, 1.56 + bob, 0], [0.05, 0.05, 0.05], mesh=None)
        part([0, 1.33 + bob, 0], [0.25, 0.18, 0.13])     # poitrine
        part([0, 1.05 + bob, 0], [0.19, 0.12, 0.11])     # taille
        for side, k in ((-1, 1), (1, -1)):
            Rl = rot(sw * k, 0, 0)
            hip = np.array([side * 0.11, 0.93 + bob, 0])
            part(hip + Rl @ [0, -0.24, 0], [0.085, 0.24, 0.09], Rl)
            knee = hip + Rl @ [0, -0.48, 0]
            Rk = rot(sw * k + max(0, -sw * k) * 0.8, 0, 0)
            part(knee + Rk @ [0, -0.22, 0], [0.07, 0.22, 0.08], Rk)
            part(knee + Rk @ [0, -0.45, 0.05], [0.07, 0.03, 0.12], Rk, mesh=None)
            Ra = rot(-sw * k * 0.8 - arms_up * 2.6, 0, side * (0.08 + arms_up * 0.3))
            sh = np.array([side * 0.32, 1.47 + bob, 0])
            part(sh + Ra @ [0, -0.3, 0], [0.065, 0.3, 0.065], Ra)
    else:
        part([0, 1.44, 0], [0.12, 0.14, 0.13])
        part([0, 1.05, -0.02], [0.25, 0.26, 0.13], rot(0.12, 0, 0))
        for side in (-1, 1):
            part([side * 0.11, 0.62, 0.25], [0.085, 0.08, 0.26])
            part([side * 0.11, 0.33, 0.5], [0.07, 0.26, 0.08])
            part([side * 0.31, 0.98, 0.18], [0.065, 0.24, 0.065], rot(-0.9, 0, 0))
    return m

def chair(c=(0, 0, 0), w=1.0):
    m = Mesh(); c = np.asarray(c, float)
    m.merge(box([0.38, 0.04, 0.38], c + [0, 0.52, 0.3], None, w, 4))
    m.merge(box([0.38, 0.48, 0.035], c + [0, 1.04, -0.06], None, w, 5))
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.merge(box([0.03, 0.26, 0.03], c + [sx * 0.34, 0.26, 0.3 + sz * 0.34], None, w, None, False))
    return m

PIPS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
        4: [(-1, -1), (1, -1), (-1, 1), (1, 1)], 5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
        6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}

def dice(size, c, R, w=1.2):
    m = box([size] * 3, c, R, w, 5)
    faces = [((0, 0, 1), (1, 0, 0), (0, 1, 0), 1), ((0, 0, -1), (1, 0, 0), (0, 1, 0), 6),
             ((1, 0, 0), (0, 0, 1), (0, 1, 0), 3), ((-1, 0, 0), (0, 0, 1), (0, 1, 0), 4),
             ((0, 1, 0), (1, 0, 0), (0, 0, 1), 5), ((0, -1, 0), (1, 0, 0), (0, 0, 1), 2)]
    c = np.asarray(c, float); R = np.asarray(R)
    for n, u, v, k in faces:
        n, u, v = map(np.array, (n, u, v))
        for a, b in PIPS[k]:
            pc = n * size * 1.002 + (u * a + v * b) * size * 0.5
            m.merge(ring(size * 0.13, (0, 0, 0), 16, "xy", w * 0.9,
                         R=np.stack([u, v, n], 1)), R, c + R @ pc)
    return m

def clock(r, c, t_hands, w=1.2):
    m = ring(r, c, 72, "xy", w).merge(ring(r * 0.92, c, 72, "xy", w * 0.4))
    c = np.asarray(c, float)
    for k in range(12):
        a = 2 * math.pi * k / 12; d = np.array([math.sin(a), math.cos(a), 0])
        b = m.add_v([c + d * r * 0.8, c + d * r * 0.9]); m.e.append((b, b + 1, w * 0.8))
    for L, sp, ww in ((0.75, 1.0, 1.0), (0.5, 1 / 12, 1.4)):
        a = 2 * math.pi * t_hands * sp; d = np.array([math.sin(a), math.cos(a), 0])
        b = m.add_v([c, c + d * r * L]); m.e.append((b, b + 1, ww))
    return m

# ------------------------------------------------------------------ texte 3D extrudé
_TEXT_CACHE = {}
def text3d(txt, height=1.0, depth=0.25, font="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf", w=1.2):
    key = (txt, height, depth, font, w)
    if key in _TEXT_CACHE: return _TEXT_CACHE[key]
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), txt, size=1.0, prop=FontProperties(fname=font))
    polys = [np.asarray(p) for p in tp.to_polygons() if len(p) > 2]
    allp = np.vstack(polys); mn, mx = allp.min(0), allp.max(0)
    sc = height / (mx[1] - mn[1]); ctr = (mn + mx) / 2
    m = Mesh(); front_poly = []
    for P in polys:
        P = (P - ctr) * sc
        if np.allclose(P[0], P[-1]): P = P[:-1]
        # simplification légère
        keep = [0]
        for i in range(1, len(P)):
            if np.linalg.norm(P[i] - P[keep[-1]]) > height * 0.025: keep.append(i)
        P = P[keep]; n = len(P)
        if n < 3: continue
        F = [(x, y, depth / 2) for x, y in P]; B = [(x, y, -depth / 2) for x, y in P]
        bf = m.add_v(F); bb = m.add_v(B)
        m.e += [(bf + i, bf + (i + 1) % n, w) for i in range(n)]
        m.e += [(bb + i, bb + (i + 1) % n, w * 0.55) for i in range(n)]
        for i in range(n):  # arêtes de profondeur aux coins
            a = P[i - 1] - P[i]; b = P[(i + 1) % n] - P[i]
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na < 1e-9 or nb < 1e-9: continue
            cosang = np.dot(a, b) / (na * nb)
            if cosang > -0.85 or i % 6 == 0: m.e.append((bf + i, bb + i, w * 0.5))
        front_poly.append(list(range(bf, bf + n)))
    m.p.append(front_poly)
    _TEXT_CACHE[key] = m
    return m

# ------------------------------------------------------------------ caméra
class Cam:
    def __init__(self, pos, target, fov=60, roll=0.0, shake=0.0, t=0.0):
        pos = np.asarray(pos, float); target = np.asarray(target, float)
        if shake:
            pos = pos + shake * np.array([math.sin(t * 37.1) + 0.5 * math.sin(t * 71.3),
                                          math.sin(t * 43.7) + 0.5 * math.sin(t * 89.1), 0])
        # tremblement « caméra à l'épaule » très léger, permanent
        pos = pos + 0.025 * np.array([math.sin(t * 1.3), math.sin(t * 1.7 + 1), math.sin(t * 1.1 + 2)])
        f = target - pos; f /= np.linalg.norm(f)
        r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        if roll:
            cr, sr = math.cos(roll), math.sin(roll)
            r, u = r * cr + u * sr, -r * sr + u * cr
        self.pos, self.M = pos, np.stack([r, u, f])
        self.foc = (H / 2) / math.tan(math.radians(fov) / 2)

    def to_cam(self, P):
        return (np.asarray(P, float) - self.pos) @ self.M.T

    def proj(self, C):
        z = np.maximum(C[:, 2], 1e-6)
        return np.stack([W / 2 + self.foc * C[:, 0] / z, H / 2 - self.foc * C[:, 1] / z], 1)

# ------------------------------------------------------------------ rendu
class Layer:
    def __init__(self):
        self.edge = np.zeros((H, W), np.float32)
        self.fill = np.zeros((H, W), np.float32)

def _clip(a, b):
    za, zb = a[2], b[2]
    if za < NEAR and zb < NEAR: return None
    if za < NEAR: a = a + (b - a) * ((NEAR - za) / (zb - za))
    elif zb < NEAR: b = b + (a - b) * ((NEAR - zb) / (za - zb))
    return a, b

def draw_mesh(layer, mesh, cam, alpha=1.0, reveal=1.0, fill=0.03, mesh_a=0.16, fog=26.0, order="y"):
    if not mesh.v or alpha <= 0.002: return
    V = mesh.arr(); C = cam.to_cam(V)
    foc = cam.foc
    def P(c): return (W / 2 + foc * c[0] / c[2], H / 2 - foc * c[1] / c[2])
    def depth_fade(z): return max(0.0, min(1.0, (fog - z) / (fog * 0.55))) * min(1.0, z / 0.6)
    # ordre d'apparition des arêtes
    E = mesh.e; nE = len(E)
    if reveal < 1.0 and nE:
        key = np.array([V[a][1] + V[b][1] for a, b, _ in E]) if order == "y" else np.arange(nE, dtype=float)
        rank = np.empty(nE); rank[np.argsort(key, kind="stable")] = np.arange(nE) / max(1, nE - 1)
    span = 0.25
    img = layer.edge
    for k, (a, b, w) in enumerate(E):
        p = 1.0
        if reveal < 1.0:
            p = (reveal * (1 + span) - rank[k]) / span
            if p <= 0: continue
            p = min(1.0, p)
        ca, cb = C[a], C[b]
        if p < 1.0: cb = ca + (cb - ca) * p
        r = _clip(ca, cb)
        if r is None: continue
        ca, cb = r
        zm = (ca[2] + cb[2]) * 0.5
        f = depth_fade(zm)
        if f <= 0.01: continue
        pa, pb = P(ca), P(cb)
        if max(abs(pa[0]), abs(pa[1]), abs(pb[0]), abs(pb[1])) > 3e4: continue
        th = int(max(1, min(6, round(w * 13.0 / max(zm, 0.8)))))
        val = float(min(1.4, w * f * alpha * (1.0 + (0.8 if p < 1.0 else 0.0))))
        cv2.line(img, (int(pa[0] * 16), int(pa[1] * 16)), (int(pb[0] * 16), int(pb[1] * 16)),
                 val, th, cv2.LINE_AA, shift=4)
    ra = ease(reveal) if reveal < 1.0 else 1.0
    # faces maillées
    if mesh.q and (fill > 0 or mesh_a > 0):
        for (a, b, c, d, n) in mesh.q:
            Q = C[[a, b, c, d]]
            if (Q[:, 2] < NEAR).any(): continue
            zm = Q[:, 2].mean(); f = depth_fade(zm) * alpha * ra
            if f <= 0.01: continue
            pts = cam.proj(Q)
            if np.abs(pts).max() > 3e4: continue
            if fill > 0:
                poly = np.round(pts * 16).astype(np.int32)
                cv2.fillPoly(layer.fill, [poly], float(fill * f), cv2.LINE_AA, shift=4)
            if n and mesh_a > 0:
                # densité adaptée à la taille à l'écran
                size = np.linalg.norm(pts[0] - pts[2]) + np.linalg.norm(pts[1] - pts[3])
                nn = int(min(n * 2, max(1, n * size / 500)))
                if nn < 1: continue
                for i in range(1, nn):
                    s = i / nn
                    p1 = Q[0] + (Q[1] - Q[0]) * s; p2 = Q[3] + (Q[2] - Q[3]) * s
                    p3 = Q[0] + (Q[3] - Q[0]) * s; p4 = Q[1] + (Q[2] - Q[1]) * s
                    for u, v in ((p1, p2), (p3, p4)):
                        pu, pv = P(u), P(v)
                        cv2.line(img, (int(pu[0] * 16), int(pu[1] * 16)), (int(pv[0] * 16), int(pv[1] * 16)),
                                 float(mesh_a * f), 1, cv2.LINE_AA, shift=4)
    # faces pleines (texte)
    if mesh.p and fill > 0:
        for poly in mesh.p:
            cont = []
            ok = True
            for cidx in poly:
                Q = C[cidx]
                if (Q[:, 2] < NEAR).any(): ok = False; break
                cont.append(np.round(cam.proj(Q) * 16).astype(np.int32))
            if not ok or not cont: continue
            zm = float(np.mean([C[c][:, 2].mean() for c in poly]))
            cv2.fillPoly(layer.fill, cont, float(fill * 2.2 * depth_fade(zm) * alpha * ra), cv2.LINE_AA, shift=4)

def draw_particles(layer, pts, cam, alpha=1.0, size=1.0):
    C = cam.to_cam(pts); ok = C[:, 2] > 0.3
    C = C[ok]
    if not len(C): return
    P = cam.proj(C)
    for (x, y), z in zip(P, C[:, 2]):
        if 0 <= x < W and 0 <= y < H:
            r = max(1, int(size * 6 / z))
            v = float(min(1.0, 2.5 / z) * alpha * 0.8)
            cv2.circle(layer.edge, (int(x), int(y)), r, v, -1, cv2.LINE_AA)

# ------------------------------------------------------------------ composition
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((_xx - W / 2) / W) ** 2 + ((_yy - H / 2) / H) ** 2)
VIGN = np.clip(1.2 - _r * 1.05, 0.35, 1.0)[..., None].astype(np.float32)
HAZE = (np.exp(-(_r / 0.45) ** 2) * 0.012)[..., None].astype(np.float32)
SCAN = (1.0 - 0.06 * (np.arange(H) % 3 == 0)).astype(np.float32)[:, None, None]
del _yy, _xx, _r

def bloom(I):
    small = cv2.resize(I, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    b1 = cv2.GaussianBlur(small, (0, 0), 1.6)
    b2 = cv2.GaussianBlur(small, (0, 0), 5)
    b3 = cv2.GaussianBlur(small, (0, 0), 16)
    b = b1 * 1.2 + b2 * 0.75 + b3 * 0.3
    return cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR)

class Compositor:
    def __init__(self):
        self.prev = {}
        self.rng = np.random.default_rng(7)

    def compose(self, layers, persist=0.55, flash=0.0, haze_col="g", exposure=1.0):
        out = np.zeros((H, W, 3), np.float32)
        for key, L in layers.items():
            I = (L.edge + 0.7 * L.fill) * exposure
            if key in self.prev and persist > 0:
                I = np.maximum(I, self.prev[key] * persist)
            self.prev[key] = I
            B = bloom(np.maximum(I - 0.3, 0) * 1.1)
            tot = I + B
            col = COLORS[key]
            hot = np.clip(I - 0.85, 0, 1)[..., None] * 0.75
            out += tot[..., None] * col[None, None, :] + hot
        out += HAZE * COLORS[haze_col][None, None, :]
        if flash > 0: out += flash * (0.6 * COLORS[haze_col][None, None, :] + 0.12)
        out = out * (0.55 + 0.45 * VIGN)
        grain = self.rng.normal(0, 0.012, (H // 2, W // 2)).astype(np.float32)
        # tonemap doux
        out = 1 - np.exp(-np.maximum(out, 0) * 1.9)
        return np.clip(out, 0, 1)

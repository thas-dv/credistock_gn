# -*- coding: utf-8 -*-
"""Corps humain holographique : maillage anatomique paramétrique + rendu à contour lumineux (fresnel)."""
import math
import numpy as np
import cv2
from engine import W, H, NEAR, rot

def _frame(d):
    d = d / (np.linalg.norm(d) + 1e-9)
    a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 0, 1.0])
    u = np.cross(d, a); u /= np.linalg.norm(u); v = np.cross(d, u)
    return d, u, v

def tube(A, B, prof, nu=22, nv=22, flat=1.0, cap=True):
    """surface de révolution le long de A->B ; prof(t) = rayon. Retourne P (nu,nv,3), N."""
    A, B = np.asarray(A, float), np.asarray(B, float)
    d, u, v = _frame(B - A)
    ts = np.linspace(0, 1, nu); ang = np.linspace(0, 2 * np.pi, nv)
    r = np.array([prof(t) for t in ts])
    if cap:  # bouts arrondis
        r = r * np.sqrt(np.clip(1 - (2 * ts - 1) ** 16, 0.05, 1))
    C = A[None, :] + (B - A)[None, :] * ts[:, None]
    ca, sa = np.cos(ang), np.sin(ang)
    off = (u[None, None, :] * ca[None, :, None] + v[None, None, :] * (sa * flat)[None, :, None]) * r[:, None, None]
    P = C[:, None, :] + off
    N = u[None, None, :] * ca[None, :, None] + v[None, None, :] * (sa / flat)[None, :, None]
    N = N / np.linalg.norm(N, axis=2, keepdims=True)
    return P, N

def ellipsoid(c, r, R=np.eye(3), nu=22, nv=26):
    th = np.linspace(0, np.pi, nu); ph = np.linspace(0, 2 * np.pi, nv)
    x = np.sin(th)[:, None] * np.cos(ph)[None, :]; y = np.cos(th)[:, None] * np.ones_like(ph)[None, :]
    z = np.sin(th)[:, None] * np.sin(ph)[None, :]
    L = np.stack([x * r[0], y * r[1], z * r[2]], 2)
    N = np.stack([x / r[0], y / r[1], z / r[2]], 2); N /= np.linalg.norm(N, axis=2, keepdims=True) + 1e-9
    return np.asarray(c) + L @ R.T, N @ R.T

def torso(base, top, nu=30, nv=34):
    """buste : section elliptique décentrée (poitrine), profil anatomique."""
    ts = np.linspace(0, 1, nu); ang = np.linspace(0, 2 * np.pi, nv)
    # (largeur, profondeur avant, profondeur arrière) selon la hauteur (0=bassin,1=cou)
    key = np.array([[0.00, 0.150, 0.095, 0.110], [0.12, 0.168, 0.100, 0.125], [0.30, 0.135, 0.092, 0.090],
                    [0.48, 0.150, 0.105, 0.088], [0.64, 0.195, 0.132, 0.100], [0.78, 0.220, 0.122, 0.105],
                    [0.88, 0.205, 0.095, 0.095], [0.96, 0.095, 0.068, 0.068], [1.00, 0.068, 0.058, 0.058]])
    wv = np.interp(ts, key[:, 0], key[:, 1]); fv = np.interp(ts, key[:, 0], key[:, 2]); bv = np.interp(ts, key[:, 0], key[:, 3])
    base, top = np.asarray(base, float), np.asarray(top, float)
    C = base[None] + (top - base)[None] * ts[:, None]
    ca, sa = np.cos(ang), np.sin(ang)
    dep = np.where(sa[None, :] > 0, fv[:, None], bv[:, None])
    X = ca[None, :] * wv[:, None]; Z = sa[None, :] * dep
    # épaules carrées : superellipse
    sq = 1 + 0.35 * np.exp(-((ts - 0.82) / 0.08) ** 2)
    X = np.sign(X) * np.abs(X) ** (1 / sq[:, None]) * wv[:, None] ** (1 - 1 / sq[:, None])
    P = np.stack([C[:, None, 0] + X, np.repeat(C[:, None, 1], nv, 1), C[:, None, 2] + Z], 2)
    N = np.stack([ca[None, :] / wv[:, None], np.zeros_like(X), sa[None, :] / dep], 2)
    N /= np.linalg.norm(N, axis=2, keepdims=True)
    return P, N

def lerp_prof(pts):
    pts = np.asarray(pts, float)
    return lambda t: float(np.interp(t, pts[:, 0], pts[:, 1]))

THIGH = lerp_prof([[0, .100], [.2, .098], [.55, .082], [.85, .060], [1, .056]])
SHIN = lerp_prof([[0, .056], [.22, .066], [.45, .056], [.8, .038], [1, .036]])
UARM = lerp_prof([[0, .060], [.35, .058], [.7, .047], [1, .040]])
FARM = lerp_prof([[0, .046], [.25, .049], [.7, .036], [1, .030]])
NECK = lerp_prof([[0, .066], [1, .056]])

class Body:
    """pose : phase de marche, assis, bras levés, orientation, position."""
    def __init__(self, pos=(0, 0, 0), yaw=0.0, phase=None, sit=False, arms_up=0.0, s=1.0, alpha=1.0):
        self.pos = np.asarray(pos, float); self.yaw = yaw; self.phase = phase; self.sit = sit
        self.arms_up = arms_up; self.s = s; self.alpha = alpha

    def surfaces(self):
        S = []; J = {"legs": [], "arms": []}; self._J = J
        walk = self.phase is not None
        ph = self.phase or 0.0
        if self.sit:
            pel = np.array([0, 0.60, 0.05]); lean = 0.12
        else:
            pel = np.array([0, 0.98 + (0.02 * abs(math.sin(ph)) if walk else 0), 0]); lean = 0.03 if walk else 0.0
        top = pel + np.array([0, 0.60 * math.cos(lean), -0.60 * math.sin(lean) * -1])
        S.append(torso(pel - [0, 0.04, 0], top))
        neck_top = top + [0, 0.09, 0.01]
        S.append(tube(top - [0, 0.02, 0], neck_top, NECK, 10, 18))
        head_c = neck_top + [0, 0.11, 0.015]
        J["head"] = head_c; J["pel"] = pel; J["top"] = top
        S.append(ellipsoid(head_c, (0.088, 0.118, 0.102), rot(-0.12, 0, 0)))
        S.append(ellipsoid(head_c + [0, -0.07, 0.035], (0.062, 0.048, 0.062), np.eye(3), 12, 16))  # mâchoire
        S.append(ellipsoid(head_c + [0, -0.005, 0.1], (0.016, 0.03, 0.022), np.eye(3), 8, 10))  # nez
        for sd in (-1, 1):
            S.append(ellipsoid(top + [sd * 0.075, -0.17, 0.07], (0.085, 0.06, 0.04), rot(0, 0, sd * 0.25), 10, 14))  # pectoraux
        # jambes
        for side in (-1, 1):
            hip = pel + [side * 0.092, -0.03, 0]
            if self.sit:
                ah, ak = 1.45, 1.5
            elif walk:
                sw = math.sin(ph) * side
                ah = 0.42 * sw; ak = 0.55 * max(0.0, -math.cos(ph + (0 if side > 0 else math.pi))) + 0.05
            else:
                ah, ak = 0.0, 0.02
            dth = np.array([0, -math.cos(ah), math.sin(ah)])
            knee = hip + 0.45 * dth
            a2 = ah - ak
            dsh = np.array([0, -math.cos(a2), math.sin(a2)])
            ank = knee + 0.43 * dsh
            J["legs"].append((hip, knee, ank))
            S.append(tube(hip - 0.04 * dth, knee + 0.03 * dth, THIGH, 20, 20, cap=False))
            S.append(ellipsoid(knee, (0.058, 0.06, 0.06), np.eye(3), 10, 14))
            S.append(tube(knee - 0.02 * dth, ank + 0.02 * dsh, SHIN, 20, 18, cap=False))
            S.append(ellipsoid(hip + [0, 0.01, -0.035], (0.1, 0.095, 0.1), np.eye(3), 12, 16))   # hanche / fessier
            foot_c = ank + [0, -0.045, 0.07]
            S.append(ellipsoid(foot_c, (0.045, 0.035, 0.12), np.eye(3), 12, 16))
        # bras
        for side in (-1, 1):
            sh = top + [side * 0.205, -0.09, -0.01]
            S.append(ellipsoid(sh + [-side * 0.005, 0.005, 0], (0.066, 0.064, 0.066), np.eye(3), 12, 16))  # deltoïde
            if walk:
                swing = -0.35 * math.sin(ph) * side
            else:
                swing = 0.0
            ab = 0.10 + 2.55 * self.arms_up
            if self.sit: swing = -0.75
            Ru = rot(swing, 0, side * ab)
            el = sh + Ru @ np.array([0, -0.29, 0])
            bend = 0.25 + (0.9 if self.sit else 0.0) - 0.15 * self.arms_up
            Rf = rot(swing - bend, 0, side * ab)
            wr = el + Rf @ np.array([0, -0.26, 0])
            S.append(tube(sh, el + (el - sh) * 0.06, UARM, 18, 18, cap=False))
            S.append(ellipsoid(el, (0.045, 0.045, 0.045), np.eye(3), 8, 12))
            S.append(tube(el, wr, FARM, 18, 16))
            J["arms"].append((sh, el, wr))
            palm = wr + Rf @ np.array([0, -0.05, 0])
            S.append(ellipsoid(palm, (0.042, 0.05, 0.018), Rf, 10, 12))
            for fx, fl in ((-0.027, 0.07), (-0.009, 0.08), (0.009, 0.078), (0.026, 0.065)):
                f0 = palm + Rf @ np.array([fx * side, -0.04, 0])
                S.append(tube(f0, f0 + Rf @ np.array([fx * side * 0.15, -fl, 0.004]), lambda t: 0.0095 - 0.003 * t, 6, 8))
            t0 = palm + Rf @ np.array([0.035 * -side, -0.005, 0.012])
            S.append(tube(t0, t0 + Rf @ np.array([0.03 * -side, -0.05, 0.02]), lambda t: 0.011 - 0.003 * t, 6, 8))
        # vers le monde
        Ry = rot(0, self.yaw, 0); self._Ry = Ry
        out = []
        for P, N in S:
            out.append((self.pos + (P * self.s) @ Ry.T, N @ Ry.T))
        return out

    def skeleton(self):
        """os visibles à travers la peau : crâne, colonne, côtes, bassin, os des membres. -> (surfaces, polylignes)"""
        J = self._J; S = []; L = []
        pel, top, hc = J["pel"], J["top"], J["head"]
        S.append(ellipsoid(hc + [0, 0.01, -0.005], (0.072, 0.095, 0.085), rot(-0.12, 0, 0), 14, 18))
        S.append(ellipsoid(hc + [0, -0.075, 0.035], (0.048, 0.03, 0.045), np.eye(3), 8, 12))
        for k in range(22):   # vertèbres
            f = k / 21
            p = pel + (top + [0, 0.07, 0] - pel) * f + [0, 0, -0.055 + 0.02 * math.sin(f * 3.1)]
            r = 0.026 - 0.01 * f
            S.append(ellipsoid(p, (r, 0.011, r * 0.8), np.eye(3), 6, 10))
        for k in range(11):   # côtes
            f = k / 10
            y = top[1] - 0.075 - 0.3 * f
            w = 0.135 * math.sin(0.55 + 2.1 * (1 - abs(f - 0.45))) + 0.02
            d = 0.095 - 0.02 * f
            ang = np.linspace(-np.pi * 0.92, np.pi * 0.92, 40)
            pts = np.stack([w * np.sin(ang), np.full_like(ang, y) - 0.03 * np.cos(ang), -0.01 + d * np.cos(ang) * -1 + 0.0], 1)
            pts[:, 2] = -0.01 - d * np.cos(ang)
            L.append(pts + [pel[0], 0, top[2]])
        st = np.array([[0, top[1] - 0.06, 0.08], [0, top[1] - 0.3, 0.085]])   # sternum
        L.append(st + [pel[0], 0, top[2]])
        for sd in (-1, 1):   # clavicules
            L.append(np.array([[0, top[1] - 0.04, 0.07], [sd * 0.19, top[1] - 0.07, 0.0]]) + [pel[0], 0, top[2]])
        ang = np.linspace(0, 2 * np.pi, 40)   # bassin
        L.append(np.stack([0.13 * np.cos(ang), pel[1] + 0.02 * np.sin(2 * ang), 0.075 * np.sin(ang)], 1) + [pel[0], 0, pel[2]])
        for sd in (-1, 1):
            S.append(ellipsoid(pel + [sd * 0.09, 0.03, -0.01], (0.065, 0.06, 0.03), rot(0, sd * 0.5, 0), 8, 12))
        bone = lambda r: (lambda t: r * (1.35 - 0.6 * math.sin(math.pi * t)))
        for hip, knee, ank in J["legs"]:
            S.append(tube(hip, knee, bone(0.017), 10, 8)); S.append(tube(knee, ank, bone(0.014), 10, 8))
        for sh, el, wr in J["arms"]:
            S.append(tube(sh, el, bone(0.014), 10, 8)); S.append(tube(el, wr, bone(0.011), 10, 8))
        Ry = self._Ry
        S = [(self.pos + (P * self.s) @ Ry.T, N @ Ry.T) for P, N in S]
        L = [self.pos + (P * self.s) @ Ry.T for P in L]
        return S, L

def draw_body(layer, body, cam, alpha=1.0, rim=1.7, core=0.05, lines=0.22, bones=0.42):
    alpha *= body.alpha
    if alpha <= 0.003: return
    Q = []; V = []; Z = []
    for P, N in body.surfaces():
        C = cam.to_cam(P.reshape(-1, 3)).reshape(P.shape)
        if (C[..., 2] < NEAR).all(): continue
        view = cam.pos[None, None, :] - P
        view /= np.linalg.norm(view, axis=2, keepdims=True)
        fres = (1 - np.abs((N * view).sum(2))) ** rim
        z = np.maximum(C[..., 2], 1e-3)
        sx = W / 2 + cam.foc * C[..., 0] / z; sy = H / 2 - cam.foc * C[..., 1] / z
        S2 = np.stack([sx, sy], 2)
        a, b = S2[:-1, :-1], S2[1:, :-1]; c, d = S2[1:, 1:], S2[:-1, 1:]
        quad = np.stack([a, b, c, d], 2).reshape(-1, 4, 2)
        val = (fres[:-1, :-1] + fres[1:, 1:]) / 2
        zz = (z[:-1, :-1] + z[1:, 1:]) / 2
        okz = (np.minimum(np.minimum(C[:-1, :-1, 2], C[1:, :-1, 2]), np.minimum(C[1:, 1:, 2], C[:-1, 1:, 2])) > NEAR)
        Q.append(quad[okz.ravel()]); V.append(val.ravel()[okz.ravel()]); Z.append(zz.ravel()[okz.ravel()])
        # maillage de la peau (lignes U et V), plus visible sur les bords
        if lines > 0 and P.shape[0] > 8:
            Pi = np.round(S2 * 16).astype(np.int32)
            for i in range(0, S2.shape[0], 2):
                if (C[i, :, 2] < NEAR).any(): continue
                cv2.polylines(layer.edge, [Pi[i]], False, float(lines * alpha * (0.25 + float(np.mean(fres[i])))), 1, cv2.LINE_AA, shift=4)
            for j in range(0, S2.shape[1], 2):
                if (C[:, j, 2] < NEAR).any(): continue
                cv2.polylines(layer.edge, [np.ascontiguousarray(Pi[:, j])], False, float(lines * alpha * (0.25 + float(np.mean(fres[:, j])))), 1, cv2.LINE_AA, shift=4)
    if not Q: return
    Q = np.concatenate(Q); V = np.concatenate(V); Z = np.concatenate(Z)
    keep = np.abs(Q).max((1, 2)) < 2e4
    Q, V, Z = Q[keep], V[keep], Z[keep]
    order = np.argsort(-Z)  # du plus loin au plus proche
    Qi = np.round(Q * 16).astype(np.int32)
    dist_fade = np.clip(14.0 / np.maximum(Z, 1.0), 0.25, 1.0)
    vals = (core + 1.55 * V) * alpha * dist_fade
    img = layer.fill
    for k in order:
        cv2.fillConvexPoly(img, Qi[k], float(vals[k]), cv2.LINE_AA, shift=4)
    # squelette visible par transparence
    if bones > 0:
        SS, LL = body.skeleton()
        for P, N in SS:
            C = cam.to_cam(P.reshape(-1, 3)).reshape(P.shape)
            if (C[..., 2] < NEAR).any(): continue
            S2 = cam.proj(C.reshape(-1, 3)).reshape(P.shape[0], P.shape[1], 2)
            Pi = np.round(S2 * 16).astype(np.int32)
            zf = float(np.clip(10.0 / C[..., 2].mean(), 0.3, 1.0))
            for i in range(0, P.shape[0], max(1, P.shape[0] // 5)):
                cv2.polylines(layer.edge, [Pi[i]], False, float(bones * alpha * zf), 1, cv2.LINE_AA, shift=4)
            for j in range(0, P.shape[1], max(1, P.shape[1] // 4)):
                cv2.polylines(layer.edge, [np.ascontiguousarray(Pi[:, j])], False, float(bones * alpha * zf), 1, cv2.LINE_AA, shift=4)
        for P in LL:
            C = cam.to_cam(P)
            if (C[:, 2] < NEAR).any(): continue
            Pi = np.round(cam.proj(C) * 16).astype(np.int32)
            cv2.polylines(layer.edge, [Pi], False, float(bones * 1.2 * alpha), 1, cv2.LINE_AA, shift=4)

# ------------------------------------------------------------------ champ d'étoiles en explosion radiale
_SR = np.random.default_rng(21)
NST = 1500
ST_DIR = _SR.normal(0, 1, (NST, 3)); ST_DIR /= np.linalg.norm(ST_DIR, axis=1, keepdims=True)
ST_SPD = _SR.uniform(0.6, 2.2, NST); ST_PH = _SR.uniform(0, 1, NST); ST_B = _SR.uniform(0.3, 1.0, NST) ** 1.5
ST_SZ = _SR.uniform(0.6, 1.8, NST)

def draw_stars(layer, center, cam, t, alpha=1.0, rmax=14.0, boost=0.0, flat=0.8):
    """étoiles qui jaillissent du centre avec traînées (comme un « big bang » autour du personnage)."""
    if alpha <= 0: return
    c = np.asarray(center, float)
    life = (t * ST_SPD * (1 + 2.5 * boost) / rmax + ST_PH) % 1.0
    r = 0.6 + life * rmax
    D = ST_DIR * np.array([1.0, flat, 1.0])
    P = c + D * r[:, None]
    tail = c + D * np.maximum(0.3, r - (0.35 + 1.6 * boost) * ST_SPD)[:, None]
    CA = cam.to_cam(P); CB = cam.to_cam(tail)
    ok = (CA[:, 2] > 0.4) & (CB[:, 2] > 0.4)
    fade = np.sin(np.clip(life, 0, 1) * np.pi) ** 0.7
    img = layer.edge
    for i in np.nonzero(ok)[0]:
        za, zb = CA[i, 2], CB[i, 2]
        x1, y1 = W / 2 + cam.foc * CA[i, 0] / za, H / 2 - cam.foc * CA[i, 1] / za
        x2, y2 = W / 2 + cam.foc * CB[i, 0] / zb, H / 2 - cam.foc * CB[i, 1] / zb
        if not (-50 < x1 < W + 50 and -50 < y1 < H + 50): continue
        v = float(ST_B[i] * fade[i] * alpha * min(1.0, 6.0 / za))
        cv2.line(img, (int(x2 * 16), int(y2 * 16)), (int(x1 * 16), int(y1 * 16)), v * 0.7, 1, cv2.LINE_AA, shift=4)
        rr = max(1, int(ST_SZ[i] * 7 / za))
        cv2.circle(img, (int(x1), int(y1)), rr, min(1.3, v * 1.4), -1, cv2.LINE_AA)

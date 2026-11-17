# -*- coding: utf-8 -*-
"""Personnage « SILHOUETTE LUMINEUSE » v2 (17/11/2026) — refait après le retour utilisateur (« les personnages sont bizarres ») :
silhouette d'une seule pièce, proportions humaines (petite tête, longues jambes), membres EFFILÉS (larges en haut, fins en bas),
pas de coutures ni d'articulations visibles, couleur crème avec léger dégradé, halo de lumière doux, fond bleu nuit.
Création originale Mindset 24. Usage : python3 perso_silhouette.py -> perso4/*.jpg (mêmes noms de poses que manga/)"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, SS = 1152, 2048, 2
OUT = "perso4"
FRONT = (250, 244, 232); BACKC = (214, 206, 192); EDGEC = (196, 186, 170)
BGT = (8, 12, 38); BGB = (30, 40, 92)

def V(a): r = math.radians(a); return (math.sin(r), math.cos(r))
def add(p, a, l): v = V(a); return (p[0] + v[0] * l, p[1] + v[1] * l)

def taper(d, p, q, w1, w2, fill):
    ang = math.atan2(q[1] - p[1], q[0] - p[0]); nx, ny = -math.sin(ang), math.cos(ang)
    pts = [(p[0] + nx * w1 / 2, p[1] + ny * w1 / 2), (q[0] + nx * w2 / 2, q[1] + ny * w2 / 2),
           (q[0] - nx * w2 / 2, q[1] - ny * w2 / 2), (p[0] - nx * w1 / 2, p[1] - ny * w1 / 2)]
    d.polygon(pts, fill=fill)
    for c, w in ((p, w1), (q, w2)): d.ellipse((c[0] - w / 2, c[1] - w / 2, c[0] + w / 2, c[1] + w / 2), fill=fill)

class Fig:
    """s = taille totale en pixels (debout). Proportions ≈ 7,5 têtes."""
    def __init__(self, s): self.s = s
    def draw(self, d_back, d_front, hip, pose):
        s = self.s; t = pose.get("t", 0)
        up = (math.sin(math.radians(t)), -math.cos(math.radians(t))); perp = (-up[1], up[0])
        def P(p, k, l): return (p[0] + k[0] * l, p[1] + k[1] * l)
        neck = P(hip, up, 0.30 * s)
        ht = pose.get("h", 0) + t; hu = (math.sin(math.radians(ht)), -math.cos(math.radians(ht)))
        head = P(P(neck, hu, 0.028 * s), hu, 0.066 * s)
        shL = P(P(neck, up, -0.025 * s), perp, -0.078 * s); shR = P(P(neck, up, -0.025 * s), perp, 0.078 * s)
        hpL = P(hip, perp, -0.045 * s); hpR = P(hip, perp, 0.045 * s)
        fb = pose.get("front", "L")
        def leg(dd, root, a, col, flip):
            k = add(root, a[0], 0.245 * s); f = add(k, a[1], 0.245 * s)
            taper(dd, root, k, 0.085 * s, 0.058 * s, col); taper(dd, k, f, 0.056 * s, 0.036 * s, col)
            toe = add(f, a[1] - 90 * flip, 0.06 * s); taper(dd, f, toe, 0.04 * s, 0.03 * s, col)
            return f
        def arm(dd, root, a, col):
            e = add(root, a[0], 0.16 * s); h = add(e, a[1], 0.15 * s)
            taper(dd, root, e, 0.058 * s, 0.038 * s, col); taper(dd, e, h, 0.037 * s, 0.028 * s, col)
            dd.ellipse((h[0] - 0.017 * s, h[1] - 0.017 * s, h[0] + 0.017 * s, h[1] + 0.017 * s), fill=col)
            return h
        out = {}
        # membres du fond
        bl, br = ("R", "L") if fb == "L" else ("L", "R")
        out["f" + bl] = leg(d_back, hpR if bl == "R" else hpL, pose["r" + "l" if False else (bl.lower() + "l")], BACKC, pose.get("flip", 1))
        out["h" + bl] = arm(d_back, shR if bl == "R" else shL, pose[bl.lower() + "a"], BACKC)
        # torse + bassin + cou + tête (devant)
        waist = P(hip, up, 0.11 * s)
        torso = [P(shL, up, 0.012 * s), P(shR, up, 0.012 * s), P(P(shR, perp, -0.01 * s), up, -0.05 * s), P(waist, perp, 0.06 * s),
                 P(hip, perp, 0.066 * s), P(P(hip, up, -0.035 * s), perp, 0.0), P(hip, perp, -0.066 * s), P(waist, perp, -0.06 * s),
                 P(P(shL, perp, 0.01 * s), up, -0.05 * s)]
        d_front.polygon(torso, fill=FRONT)
        for c in (shL, shR): d_front.ellipse((c[0] - 0.029 * s, c[1] - 0.029 * s, c[0] + 0.029 * s, c[1] + 0.029 * s), fill=FRONT)
        d_front.ellipse((hip[0] - 0.062 * s, hip[1] - 0.05 * s, hip[0] + 0.062 * s, hip[1] + 0.045 * s), fill=FRONT)
        taper(d_front, P(neck, up, -0.03 * s), P(neck, hu, 0.045 * s), 0.05 * s, 0.042 * s, FRONT)
        r = 0.066 * s; d_front.ellipse((head[0] - r * 0.9, head[1] - r, head[0] + r * 0.9, head[1] + r), fill=FRONT)
        out["f" + fb] = leg(d_front, hpL if fb == "L" else hpR, pose[fb.lower() + "l"], FRONT, pose.get("flip", 1))
        out["h" + fb] = arm(d_front, shL if fb == "L" else shR, pose[fb.lower() + "a"], FRONT)
        out["head"] = head; out["r"] = r
        return out

def background(seed):
    yy = np.linspace(0, 1, H * SS)[:, None, None]
    g = np.array(BGT, np.float32) * (1 - yy) + np.array(BGB, np.float32) * yy
    g = np.repeat(g, W * SS, axis=1) + np.random.default_rng(seed).normal(0, 2.5, (H * SS, W * SS, 1))
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")

def compose(layers, name, props_back=None, props_front=None, maxh=1240, maxw=900, bottom=1850, crop=None, seed=0):
    """layers = (back_mask_img, front_mask_img) RGBA ; on recadre tout, on ajoute le halo et on pose au sol."""
    back, front = layers
    full = Image.new("RGBA", back.size, (0, 0, 0, 0))
    full.alpha_composite(back)
    # liseré discret autour des membres de devant (lisibilité quand ils passent devant le corps)
    fa = front.getchannel("A"); edge = fa.filter(ImageFilter.MaxFilter(5))
    E = Image.new("RGBA", front.size, EDGEC + (0,)); E.putalpha(edge.point(lambda v: int(v * 0.9)))
    full.alpha_composite(E); full.alpha_composite(front)
    if props_front: full.alpha_composite(props_front)
    bb = full.getchannel("A").getbbox() if crop is None else crop
    L = full.crop(bb)
    sc = min(maxh * SS / L.height, maxw * SS / L.width); L = L.resize((int(L.width * sc), int(L.height * sc)), Image.LANCZOS)
    # léger dégradé vertical (haut plus lumineux)
    a = np.asarray(L).astype(np.float32); yy = np.linspace(1.04, 0.9, L.height)[:, None, None]
    a[..., :3] = np.clip(a[..., :3] * yy, 0, 255); L = Image.fromarray(a.astype(np.uint8))
    pad = 170 * SS
    G = Image.new("RGBA", (L.width + 2 * pad, L.height + 2 * pad), (0, 0, 0, 0)); G.alpha_composite(L, (pad, pad))
    al = G.getchannel("A")
    g1 = Image.new("RGBA", G.size, (255, 226, 170, 0)); g1.putalpha(al.filter(ImageFilter.GaussianBlur(34 * SS)).point(lambda v: min(255, int(v * 1.0))))
    g2 = Image.new("RGBA", G.size, (255, 244, 220, 0)); g2.putalpha(al.filter(ImageFilter.GaussianBlur(9 * SS)).point(lambda v: int(v * 0.8)))
    bg = background(seed)
    x = int(W * SS / 2 - G.width / 2); y = int(bottom * SS - L.height - pad)
    d = ImageDraw.Draw(bg)
    halo = Image.new("RGBA", bg.size, (0, 0, 0, 0)); ImageDraw.Draw(halo).ellipse((W * SS * 0.12, H * SS * 0.2, W * SS * 0.88, H * SS * 0.85), fill=(90, 120, 210, 60))
    bg.alpha_composite(halo.filter(ImageFilter.GaussianBlur(140)))
    gw = L.width * 0.48
    sh = Image.new("RGBA", bg.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((W * SS / 2 - gw, bottom * SS - 18 * SS, W * SS / 2 + gw, bottom * SS + 18 * SS), fill=(110, 130, 210, 120))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * SS)))
    bg.alpha_composite(g1, (x, y)); bg.alpha_composite(g1, (x, y)); bg.alpha_composite(g2, (x, y)); bg.alpha_composite(g2, (x, y)); bg.alpha_composite(G, (x, y))
    os.makedirs(OUT, exist_ok=True)
    bg.resize((W, H), Image.LANCZOS).convert("RGB").save(f"{OUT}/{name}.jpg", quality=92)

def canvas():
    sz = (W * SS, int(H * SS * 1.4))
    b = Image.new("RGBA", sz, (0, 0, 0, 0)); f = Image.new("RGBA", sz, (0, 0, 0, 0)); p = Image.new("RGBA", sz, (0, 0, 0, 0))
    return b, f, p, ImageDraw.Draw(b), ImageDraw.Draw(f), ImageDraw.Draw(p)

def ball(d, c, r, col=(250, 246, 236)):
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=col)
    pts = [add(c, 180 + i * 72, r * 0.36) for i in range(5)]; d.polygon(pts, fill=(205, 200, 190))

def bench(d, y, cx, w):
    col = (150, 160, 205)
    d.rounded_rectangle((cx - w, y - 22, cx + w, y + 14), 10, fill=col)
    for x in (cx - w * 0.8, cx + w * 0.8): d.rectangle((x - 12, y, x + 12, y + 330), fill=col)

def cup(d, c, s):
    g = (246, 200, 90)
    d.polygon([(c[0] - s, c[1] - s * 1.2), (c[0] + s, c[1] - s * 1.2), (c[0] + s * 0.55, c[1] + s * 0.2), (c[0] - s * 0.55, c[1] + s * 0.2)], fill=g)
    d.rectangle((c[0] - s * 0.12, c[1] + s * 0.2, c[0] + s * 0.12, c[1] + s * 0.7), fill=g)
    d.rectangle((c[0] - s * 0.6, c[1] + s * 0.7, c[0] + s * 0.6, c[1] + s * 1.0), fill=g)
    for sx in (-1, 1): d.arc((c[0] + sx * s * 0.8 - s * 0.4, c[1] - s * 1.0, c[0] + sx * s * 0.8 + s * 0.4, c[1] - s * 0.2), 0, 360, fill=g, width=int(s * 0.12))

def bag(d, shoulder, hipp, s):
    col = (60, 70, 110)
    d.line((shoulder, (hipp[0] + 0.07 * s, hipp[1] - 0.02 * s)), fill=col, width=int(0.014 * s))
    d.rounded_rectangle((hipp[0] + 0.03 * s, hipp[1] - 0.06 * s, hipp[0] + 0.2 * s, hipp[1] + 0.05 * s), int(0.025 * s), fill=col)

S = 1500 * SS
POSES = {
    # (angles : 0 = vers le bas, 90 = vers la droite, -90 = vers la gauche ; t = inclinaison du buste ; h = tête)
    "croise":  dict(t=0, la=(-28, 45), ra=(28, -45), ll=(3, 1), rl=(-3, -1), front="L"),
    "pointe":  dict(t=-3, la=(8, 3), ra=(-96, -92), ll=(4, 2), rl=(-6, -2), front="R", h=-6),
    "bras":    dict(t=0, la=(-148, -168), ra=(148, 168), ll=(8, 3), rl=(-8, -3), front="L", h=8),
    "courir":  dict(t=14, la=(40, 120), ra=(-45, -10), ll=(60, -8), rl=(-35, -105), front="L", flip=-1),
    "frappe":  dict(t=-10, la=(-70, -40), ra=(55, 100), ll=(-4, 4), rl=(85, 92), front="R", flip=-1),
    "tete":    dict(t=-6, la=(-125, -150), ra=(125, 150), ll=(25, -35), rl=(-10, -70), front="L", flip=-1, h=-18),
    "genoux":  dict(t=-4, la=(-150, -175), ra=(150, 172), ll=(88, 2), rl=(8, -90), front="L", flip=-1, h=-20),
    "assis":   dict(t=14, la=(25, 70), ra=(15, 65), ll=(88, 4), rl=(84, 2), front="L", flip=-1, h=28),
    "banc":    dict(t=18, la=(25, 70), ra=(15, 65), ll=(88, 4), rl=(84, 2), front="L", flip=-1, h=24),
    "sac":     dict(t=0, la=(-6, -2), ra=(6, 2), ll=(4, 1), rl=(-4, -1), front="L"),
    "trophee": dict(t=0, la=(-160, 168), ra=(160, -168), ll=(8, 3), rl=(-8, -3), front="L", h=10),
    "visage":  dict(t=0, la=(-8, -3), ra=(8, 3), ll=(3, 1), rl=(-3, -1), front="L", h=-14),
}

def main():
    cx = W * SS / 2; F = Fig(S)
    for name, pose in POSES.items():
        b, f, p, db, df, dp = canvas()
        hip = (cx, 1500 * SS)
        if name in ("assis", "banc"): hip = (cx - 120 * SS, 1700 * SS)
        if name == "genoux": hip = (cx - 80 * SS, 1720 * SS)
        o = F.draw(db, df, hip, pose)
        if name == "assis": ball(db, (hip[0] + 40 * SS, hip[1] + 0.09 * S), 0.09 * S)
        if name == "banc": bench(db, hip[1] + 0.04 * S, hip[0] + 60 * SS, 0.32 * S)
        if name == "courir": ball(dp, (o["fL"][0] + 0.09 * S, o["fL"][1] + 0.0 * S), 0.04 * S)
        if name == "frappe": ball(dp, (o["fR"][0] + 0.08 * S, o["fR"][1] - 0.02 * S), 0.04 * S)
        if name == "tete": ball(dp, (o["head"][0] + 0.02 * S, o["head"][1] - 0.13 * S), 0.04 * S)
        if name == "trophee": cup(dp, ((o["hL"][0] + o["hR"][0]) / 2, min(o["hL"][1], o["hR"][1]) - 0.06 * S), 0.05 * S)
        if name == "sac": bag(df, (hip[0] - 0.07 * S, hip[1] - 0.29 * S), (hip[0] + 0.02 * S, hip[1] - 0.02 * S), S)
        if name == "visage":
            hd = o["head"]; r = o["r"]
            compose((b, f), name, props_front=p, crop=(int(hd[0] - r * 3.2), int(hd[1] - r * 2.2), int(hd[0] + r * 3.2), int(hd[1] + r * 9)), maxh=99999, maxw=760, bottom=2150, seed=12)
            continue
        compose((b, f), name, props_front=p, seed=len(name))

if __name__ == "__main__":
    main()

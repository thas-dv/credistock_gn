# -*- coding: utf-8 -*-
"""3e PERSONNAGE Mindset 24 (17/11/2026) — demande utilisateur : un personnage différent à chaque histoire, jamais le héros du film (Kaï).
« Karim » (nom interne) : jeune adulte athlétique, cheveux courts bouclés avec raie, barbe courte, maillot BORDEAUX à col et manches
BLANCS (sans numéro ni logo), short bleu marine, chaussettes blanches, crampons verts ; fond bleu-vert nuit.
Réutilise le moteur de poses de perso_nadi.py. Usage : python3 perso_karim.py -> perso3/*.jpg"""
import numpy as np
import perso_nadi as N

N.OUT = "perso3"
N.SKIN = (164, 112, 78); N.SKIN_D = (134, 88, 60); N.HAIR = (26, 20, 18); N.HAIR_F = (52, 40, 34)
N.JER = (150, 28, 52); N.JER_D = (108, 18, 38); N.YEL = (246, 246, 246); N.SHO = (24, 34, 72)
N.SOCK = (240, 240, 240); N.BOOT = (24, 168, 98)
N.BGT = (6, 26, 34); N.BGB = (16, 62, 70)
BEARD = (54, 38, 30)

def head(P, c, r, tilt=0, expr="neutral", look=0.0, back=False, sweat=False):
    d = P.d
    for sx in (-1, 1): P.ell((c[0] + sx * r * 0.98, c[1] + r * 0.05), r * 0.16, r * 0.22, N.SKIN_D, 8)
    P.ell(c, r, r * 1.1, N.SKIN, 10)
    # cheveux courts bouclés : calotte + petites boucles sur le bord + raie
    d.chord((c[0] - r * 1.04 - 10, c[1] - r * 1.25 - 10, c[0] + r * 1.04 + 10, c[1] + r * 0.55), 180, 360, fill=N.LINE)
    d.chord((c[0] - r * 1.02, c[1] - r * 1.22, c[0] + r * 1.02, c[1] + r * 0.5), 180, 360, fill=N.HAIR)
    rng = np.random.default_rng(3)
    for i in range(34):
        a = np.radians(180 + i * 180 / 33); x = c[0] + np.cos(a) * r * 1.0; y = c[1] - 0.36 * r + np.sin(a) * r * 0.86
        q = r * rng.uniform(0.09, 0.14); d.ellipse((x - q, y - q, x + q, y + q), fill=N.HAIR)
    for _ in range(30):
        x = c[0] + rng.uniform(-0.8, 0.8) * r; y = c[1] + rng.uniform(-1.05, -0.5) * r; q = r * 0.06
        d.arc((x - q, y - q, x + q, y + q), rng.uniform(0, 360), rng.uniform(0, 360) + 220, fill=(78, 62, 54), width=max(2, int(r * 0.03)))
    d.line((c[0] + r * 0.35, c[1] - r * 1.15, c[0] + r * 0.5, c[1] - r * 0.5), fill=(90, 70, 60), width=max(2, int(r * 0.04)))  # raie
    if back:
        d.ellipse((c[0] - r * 0.95, c[1] - r * 0.6, c[0] + r * 0.95, c[1] + r * 0.45), fill=N.HAIR)
        return
    # barbe courte : bande le long de la mâchoire + moustache
    d.arc((c[0] - r * 0.97, c[1] - r * 1.05, c[0] + r * 0.97, c[1] + r * 1.05), 15, 165, fill=BEARD, width=int(r * 0.2))
    d.chord((c[0] - r * 0.3, c[1] + r * 0.3, c[0] + r * 0.3, c[1] + r * 0.5), 180, 360, fill=BEARD)
    N.face(P, c, r, expr, look)
    if sweat:
        for sx, sy in ((0.75, -0.35), (-0.8, -0.1)):
            x, y = c[0] + sx * r, c[1] + sy * r
            d.polygon([(x, y - r * 0.16), (x - r * 0.07, y), (x + r * 0.07, y)], fill=(180, 230, 255)); d.ellipse((x - r * 0.07, y - r * 0.06, x + r * 0.07, y + r * 0.08), fill=(180, 230, 255))

N.head = head
if __name__ == "__main__":
    N.main()

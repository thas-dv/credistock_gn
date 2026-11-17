# -*- coding: utf-8 -*-
"""Style « SILHOUETTE LUMINEUSE » (17/11/2026) — demandé par l'utilisateur d'après une vidéo vue sur TikTok :
personnage minimaliste blanc crème, sans visage, membres arrondis, halo de lumière doux, fond bleu nuit.
Création originale Mindset 24 (on reprend l'idée d'un mannequin lumineux, pas les décors ni la mise en page de la vidéo vue).
Réutilise le moteur de poses de perso_nadi.py. Usage : python3 perso_lumiere.py -> perso4/*.jpg"""
import os
from PIL import Image, ImageDraw, ImageFilter
import perso_nadi as N

N.OUT = "perso4"; N.WSC = 0.62
C = (246, 240, 226); CB = (206, 200, 188)
N.LINE = C; N.SKIN = C; N.SKIN_D = CB; N.HAIR = C; N.HAIR_F = C
N.JER = C; N.JER_D = CB; N.YEL = C; N.SHO = C; N.SOCK = C; N.BOOT = C
N.BGT = (10, 16, 44); N.BGB = (34, 44, 96)

def head(P, c, r, tilt=0, expr="neutral", look=0.0, back=False, sweat=False):
    P.d.ellipse((c[0] - r * 0.95, c[1] - r * 1.0, c[0] + r * 0.95, c[1] + r * 1.0), fill=C)

def save(im, name, fx=None, maxh=1500, maxw=1000, bottom=1830):
    bg = N.background(hash(name) % 100)
    bb = im.getchannel("A").getbbox(); L = im.crop(bb)
    sc = min(maxh * N.SS / L.height, maxw * N.SS / L.width); L = L.resize((int(L.width * sc), int(L.height * sc)), Image.LANCZOS)
    pad = 160 * N.SS
    G = Image.new("RGBA", (L.width + 2 * pad, L.height + 2 * pad), (0, 0, 0, 0)); G.alpha_composite(L, (pad, pad))
    glow = Image.new("RGBA", G.size, (255, 236, 190, 0)); glow.putalpha(G.getchannel("A").filter(ImageFilter.GaussianBlur(28 * N.SS)))
    glow2 = Image.new("RGBA", G.size, (255, 246, 220, 0)); glow2.putalpha(G.getchannel("A").filter(ImageFilter.GaussianBlur(8 * N.SS)))
    x = int((fx if fx is not None else N.W / 2) * N.SS - G.width / 2); y = int(bottom * N.SS - L.height - pad)
    d = ImageDraw.Draw(bg); gw = L.width * 0.5
    d.ellipse((x + G.width / 2 - gw, bottom * N.SS - 26 * N.SS, x + G.width / 2 + gw, bottom * N.SS + 26 * N.SS), fill=(70, 80, 140))
    bg.alpha_composite(glow, (x, y)); bg.alpha_composite(glow, (x, y)); bg.alpha_composite(glow2, (x, y)); bg.alpha_composite(G, (x, y))
    bg = bg.resize((N.W, N.H), Image.LANCZOS).convert("RGB"); os.makedirs(N.OUT, exist_ok=True); bg.save(f"{N.OUT}/{name}.jpg", quality=92)

N.head = head; N.save = save
if __name__ == "__main__":
    N.main()

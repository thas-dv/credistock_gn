# -*- coding: utf-8 -*-
"""Style « film » Mindset 24 (dimanche) : héros ORIGINAL « Kaï » en dessin au trait (peau blanc cassé, contour sombre, ombres grises),
cheveux en mèches ORANGE, maillot blanc à liseré orange ; fond bleu nuit uni ; décors en gris dans des CARTES arrondies ; icônes (chrono,
mini-vignettes, VS). Pays imaginaire « Kalonia ». Aucun nom réel, club, logo ni marque."""
import sys; sys.path.insert(0, "/home/claude/film")
from film_base import *
import film_base as FB

NAVY = (24, 28, 40); CARD = (58, 63, 78); CARD2 = (44, 48, 62); EDGE = (226, 230, 238); LINEC = (28, 30, 38)
OR = (255, 140, 30); OR2 = (255, 186, 70); GREYP = (150, 154, 166)
FB.SKIN = (242, 240, 236); FB.SKIN_D = (206, 206, 212); FB.HAIR = (40, 36, 34); FB.BOOT = (30, 32, 40); FB.RIM = LINEC
FB.POSES.update({
    "ready": dict(t=10, la=(-55, 40), ra=(55, -40), ll=(-18, 12), rl=(18, -12)),
    "sad": dict(t=-26, la=(-14, 30), ra=(14, -30), ll=(-6, 4), rl=(6, -4)),
    "shout": dict(t=9, la=(-118, -22), ra=(118, 22), ll=(-24, 6), rl=(24, -6)),
    "point": dict(t=4, la=(-150, -10), ra=(30, -40), ll=(-12, 4), rl=(12, -4)),
    "kneel": dict(t=12, la=(-20, 40), ra=(30, -50), ll=(-80, 95), rl=(15, -10)),
})

def hair(img, s, facing=1):
    """mèches orange en pointes (dessin original), d'après la tête du dernier personnage dessiné"""
    hx, hy = JT["head"]; r = 0.12 * s; hy += 0.07 * s
    L = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    spikes = [(-150, 1.55), (-120, 1.75), (-95, 1.9), (-70, 1.8), (-45, 1.6), (-20, 1.35), (-170, 1.3)]
    for a, ln in spikes:
        a2 = math.radians(a + (0 if facing > 0 else 0)); b1 = math.radians(a - 22); b2 = math.radians(a + 22)
        tip = (hx + math.cos(a2) * r * ln * facing, hy + math.sin(a2) * r * ln)
        p1 = (hx + math.cos(b1) * r * 0.85 * facing, hy + math.sin(b1) * r * 0.85)
        p2 = (hx + math.cos(b2) * r * 0.85 * facing, hy + math.sin(b2) * r * 0.85)
        d.polygon([p1, tip, p2], fill=OR, outline=LINEC)
    d.ellipse((hx - r * 0.95, hy - r * 1.05, hx + r * 0.95, hy + r * 0.2), fill=OR)
    for a, ln in spikes[1:5]:
        a2 = math.radians(a); tip = (hx + math.cos(a2) * r * ln * 0.8 * facing, hy + math.sin(a2) * r * ln * 0.8)
        d.line((hx + math.cos(a2) * r * 0.3 * facing, hy + math.sin(a2) * r * 0.3, tip[0], tip[1]), fill=OR2, width=max(2, int(s / 90)))
    img.alpha_composite(L)

def kai(img, x, y, s, pose, facing=1, **kw):
    FB.HAIR = OR
    kw.setdefault("jersey", (238, 238, 242)); kw.setdefault("shorts", (30, 34, 48)); kw.setdefault("sock", (238, 238, 242))
    kw.setdefault("glow", 1.6)
    player(img, x, y, s, pose, facing=facing, **kw)
    hair(img, s, facing)
    FB.HAIR = (40, 36, 34)
    # liseré orange sur le maillot (col) + numéro 10 en orange
    d = ImageDraw.Draw(img)
    return d

def card(img, box, edge=EDGE, fill=CARD, r=26, w=5):
    d = ImageDraw.Draw(img); d.rounded_rectangle(box, r, fill=fill, outline=edge, width=w); return d

def stopwatch(d, cx, cy, r, u):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(236, 238, 242)); d.ellipse((cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82), fill=(52, 56, 70))
    d.rectangle((cx - r * 0.15, cy - r * 1.3, cx + r * 0.15, cy - r * 1.02), fill=(236, 238, 242))
    d.arc((cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82), -90, -90 + 360 * u, fill=OR, width=int(r * 0.16))
    a = math.radians(-90 + 360 * u); d.line((cx, cy, cx + 0.6 * r * math.cos(a), cy + 0.6 * r * math.sin(a)), fill=(236, 238, 242), width=int(r * 0.1))

def sand_pitch(d, box):
    x0, y0, x1, y1 = box
    d.rectangle((x0 + 30, y1 - 120, x1 - 30, y1 - 70), fill=(196, 182, 150))
    for gx in (x0 + 60, x1 - 120):
        d.line((gx, y1 - 110, gx, y1 - 260, gx + 60, y1 - 260, gx + 60, y1 - 110), fill=(210, 212, 218), width=6)

def still(path, which):
    img = Image.new("RGBA", (W, H), NAVY + (255,)); d = ImageDraw.Draw(img)
    if which == 1:   # carte titre + Kaï
        d = card(img, (110, 520, 970, 1480))
        sand_pitch(d, (110, 520, 970, 1480))
        kai(img, 540, 1400, 520, "ready")
        d = ImageDraw.Draw(img)
        ball(d, 690, 1395, 34, (236, 238, 242), 0.4)
        text(d, (W / 2, 250), "KAÏ", 190, OR, BOLD)
        text(d, (W / 2, 390), "LE FILM · ÉPISODE 1", 64, EDGE, BOLD)
        text(d, (W / 2, 1600), "Histoire imaginaire", 44, GREYP, BOLD)
        stopwatch(d, 900, 640, 50, 0.65)
    elif which == 2:   # « VS » : le choisi / Kaï
        d = card(img, (60, 560, 520, 1380), edge=(226, 90, 70)); d = card(img, (560, 560, 1020, 1380))
        player(img, 290, 1300, 400, "stand", jersey=(150, 156, 170), shorts=(60, 64, 80), sock=(150, 156, 170), glow=1.6)
        kai(img, 790, 1300, 330, "sad")
        d = ImageDraw.Draw(img)
        d.ellipse((480, 900, 600, 1020), fill=(52, 56, 70), outline=EDGE, width=4); text(d, (540, 960), "VS", 52, EDGE, BOLD)
        text(d, (290, 1440), "« LUI »", 60, (226, 90, 70), BOLD); text(d, (790, 1440), "« TROP PETIT »", 56, OR, BOLD)
        text(d, (W / 2, 330), "LE RECRUTEUR", 90, EDGE, BOLD); text(d, (W / 2, 440), "N'EN PRENDRA QU'UN", 76, OR, BOLD)
    elif which == 3:   # cri
        d = ImageDraw.Draw(img)
        for i in range(36):
            a = 2 * math.pi * i / 36; d.line((540 + 260 * math.cos(a), 1050 + 260 * math.sin(a), 540 + 900 * math.cos(a), 1050 + 900 * math.sin(a)), fill=(40, 46, 62), width=10)
        kai(img, 540, 1500, 620, "shout")
        d = ImageDraw.Draw(img)
        text(d, (W / 2, 330), "JE NE RENTRE PAS", 96, EDGE, BOLD, stroke=6, scol=NAVY)
        text(d, (W / 2, 460), "SANS MA CHANCE !", 104, OR, BOLD, stroke=6, scol=NAVY)
    elif which == 4:   # vignettes + gros plan
        for i in range(6):
            bx = 130 + (i % 3) * 290; by = 420 + (i // 3) * 340
            d = card(img, (bx, by, bx + 260, by + 300), edge=OR if i == 4 else EDGE, w=4)
            text(d, (bx + 30, by + 30), str(i + 1), 30, EDGE, BOLD)
        poses = ["stand", "ready", "sad", "kneel", "shout", "point"]
        for i, p in enumerate(poses):
            bx = 130 + (i % 3) * 290; by = 420 + (i // 3) * 340
            kai(img, bx + 130, by + 280, 175, p)
        d = ImageDraw.Draw(img)
        text(d, (W / 2, 260), "LA SAISON 1", 100, OR, BOLD)
        text(d, (W / 2, 1180), "10 ÉPISODES · CHAQUE DIMANCHE", 56, EDGE, BOLD)
    img.convert("RGB").save(path)

if __name__ == "__main__":
    for i in (1, 2, 3, 4): still(f"/home/claude/film/style_{i}.png", i)

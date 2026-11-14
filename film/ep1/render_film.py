# -*- coding: utf-8 -*-
"""FILM « KAÏ » — Épisode 1, style manga animé (14/11/2026).
Décors (bg_*.jpg) + personnages détourés (cut/*.png, rembg isnet-anime) qui BOUGENT sur les décors :
entrées, courses, sauts, perspective (petit au loin -> grand), parallaxe, caméra (zoom, panoramique, secousse),
traits de vitesse, poussière de sable, flashs, onomatopées, sous-titres karaoké. Usage : python3 render_film.py sortie.mp4"""
import json, math, subprocess, sys, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 30
WORDS = json.load(open("words.json"))["words"]
END = WORDS[-1]["end"] + 1.3
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
OR = (255, 132, 30); YEL = (255, 206, 40); RED = (226, 54, 54); WHITE = (255, 255, 255); NAVY = (10, 16, 42)
_F = {}
def F(sz):
    sz = max(8, int(sz))
    if sz not in _F: _F[sz] = ImageFont.truetype(BOLD, sz)
    return _F[sz]
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def eout(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def back(x): x = min(1, max(0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u

def norm(s): return "".join(ch for ch in s.lower() if ch.isalnum() or ch in "éèàùêâîôûçëïü")
def T(word, n=1):
    k = 0
    for w in WORDS:
        if norm(w["text"]) == norm(word):
            k += 1
            if k == n: return w["start"]
    raise KeyError(word)

BG = {n: Image.open(f"bg_{n}.jpg").convert("RGB") for n in ("aube", "soir", "tournoi")}
FULL = {n: Image.open(f"{n}.jpg").convert("RGB") for n in ("k_banc", "k_visage", "k_matelas")}
CUT = {}
for n in "k_matelas k_court_face k_poings z_pointe k_dribble r_pointe k_volee k_tir k_elan r_marche b_coach z_fete".split():
    im = Image.open(f"cut/{n}.png").convert("RGBA"); CUT[n] = im.crop(im.getbbox())

def cover(img, zoom=1.0, fx=0.5, fy=0.5, w=W, h=H):
    iw, ih = img.size; s = max(w / iw, h / ih) * zoom
    nw, nh = int(iw * s + 0.5), int(ih * s + 0.5)
    r = img.resize((nw, nh), Image.BILINEAR)
    x0 = int(min(max(fx * nw - w / 2, 0), nw - w)); y0 = int(min(max(fy * nh - h / 2, 0), nh - h))
    return r.crop((x0, y0, x0 + w, y0 + h)).convert("RGBA")

def put(img, name, cx, by, h, alpha=1.0, flip=False, dark=0.0, rot=0.0, glow=None):
    """pose un personnage détouré : centre x = cx, pieds à by, hauteur h"""
    c = CUT[name]; s = h / c.height
    L = c.resize((max(2, int(c.width * s)), max(2, int(h))), Image.BILINEAR)
    if flip: L = L.transpose(Image.FLIP_LEFT_RIGHT)
    if dark:
        a = L.getchannel("A"); L = ImageEnhance.Brightness(L.convert("RGB")).enhance(1 - dark).convert("RGBA"); L.putalpha(a)
    if rot: L = L.rotate(rot, expand=True, resample=Image.BICUBIC)
    if glow:
        g = Image.new("RGBA", L.size, glow + (0,)); g.putalpha(L.getchannel("A").filter(ImageFilter.GaussianBlur(18)))
        img.alpha_composite(g, (int(cx - L.width / 2), int(by - L.height)))
    if alpha < 1: L.putalpha(Image.eval(L.getchannel("A"), lambda v: int(v * max(0, alpha))))
    img.alpha_composite(L, (int(cx - L.width / 2), int(by - L.height)))

def shade(img, a, col=(0, 0, 0)): img.alpha_composite(Image.new("RGBA", img.size, col + (int(max(0, min(255, a))),)))
def tint(img, col, a): shade(img, a, col)

def text(img, s, cx, cy, size, col=WHITE, k=1.0, stroke=8, pop=True, alpha=1.0, maxw=1000, rot=0):
    if k < 0: return
    while F(size).getlength(s) > maxw and size > 30: size -= 4
    sc = (0.6 + 0.4 * back(k / 0.3)) if pop else 1.0; f = F(size * sc)
    L = Image.new("RGBA", (W, int(size * sc * 1.7) + 2 * stroke + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.text((W / 2, L.height / 2), s, font=f, fill=col + (255,), anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    if rot: L = L.rotate(rot, expand=False, resample=Image.BICUBIC)
    a = ease(k / 0.12) * alpha
    if a < 1: L.putalpha(Image.eval(L.getchannel("A"), lambda v: int(v * a)))
    img.alpha_composite(L, (int(cx - W / 2), int(cy - L.height / 2)))

def stamp(img, s, cx, cy, k, size=90, col=RED, ang=-7):
    if k < 0: return
    sc = 1 + 1.3 * (1 - eout(k / 0.16)); f = F(size); tw = f.getlength(s)
    L = Image.new("RGBA", (int(tw + 90), int(size * 1.9)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((6, 6, L.width - 7, L.height - 7), 20, fill=(255, 255, 255, 230), outline=col + (255,), width=12)
    d.text((L.width / 2, L.height / 2), s, font=f, fill=col + (255,), anchor="mm")
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC); L = L.resize((int(L.width * sc), int(L.height * sc)))
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def tag(img, s, k, y=170):
    """étiquette de lieu façon film"""
    if k < 0: return
    f = F(40); tw = f.getlength(s); a = ease(k / 0.3)
    L = Image.new("RGBA", (int(tw + 60), 76), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((0, 0, 8, 75), fill=OR + (255,)); d.rectangle((8, 0, L.width, 75), fill=(10, 12, 20, 200))
    d.text((34, 38), s, font=f, fill=WHITE, anchor="lm")
    L.putalpha(Image.eval(L.getchannel("A"), lambda v: int(v * a)))
    img.alpha_composite(L, (int(60 - 40 * (1 - eout(k / 0.4))), y))

def speed_radial(img, tg, a, cx=W / 2, cy=H * 0.45, col=(255, 255, 255)):
    if a <= 0: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); rng = np.random.default_rng(int(tg * 15))
    for _ in range(46):
        an = rng.uniform(0, 2 * math.pi); r1 = rng.uniform(420, 750); r2 = r1 + rng.uniform(200, 600)
        d.line((cx + math.cos(an) * r1, cy + math.sin(an) * r1, cx + math.cos(an) * r2, cy + math.sin(an) * r2), fill=col + (int(220 * a),), width=6)
    img.alpha_composite(L)

def speed_h(img, tg, a, y0=500, y1=1600, dirn=1):
    if a <= 0: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); rng = np.random.default_rng(int(tg * 20))
    for _ in range(30):
        y = rng.uniform(y0, y1); x = rng.uniform(-200, W); ln = rng.uniform(150, 500)
        d.line((x, y, x + ln, y), fill=(255, 255, 255, int(170 * a)), width=4)
    img.alpha_composite(L)

def dust(img, tg, x, y, k, n=40, col=(235, 225, 205), seed=0):
    if k < 0 or k > 1.6: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); rng = np.random.default_rng(seed)
    for _ in range(n):
        vx = rng.uniform(-420, 420); vy = rng.uniform(-520, -80); r = rng.uniform(4, 13)
        px = x + vx * k; py = y + vy * k + 600 * k * k; a = int(230 * max(0, 1 - k / 1.6))
        d.ellipse((px - r, py - r, px + r, py + r), fill=col + (a,))
    img.alpha_composite(L)

def confetti(img, tg, k, n=70):
    if k < 0: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); rng = np.random.default_rng(9)
    for _ in range(n):
        x = rng.uniform(0, W) + 40 * math.sin(tg * 3 + rng.uniform(0, 6)); y = (rng.uniform(-H, 0) + 520 * k) % (H + 100) - 50
        c = [OR, YEL, WHITE][int(rng.integers(0, 3))]; s = rng.uniform(8, 16)
        d.rectangle((x, y, x + s, y + s * 0.6), fill=c + (230,))
    img.alpha_composite(L)

def flash(img, k, dur=0.25, a0=235):
    if 0 <= k < dur: shade(img, a0 * (1 - k / dur), (255, 248, 230))

def window_light(img, tg):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.polygon([(140, 120), (420, 120), (900, 1700), (260, 1700)], fill=(255, 150, 60, 70))
    d.rectangle((150, 110, 410, 380), outline=(255, 190, 110, 200), width=10); d.line((280, 110, 280, 380), fill=(255, 190, 110, 200), width=8)
    L = L.filter(ImageFilter.GaussianBlur(22)); img.alpha_composite(L)
    rng = np.random.default_rng(4); d2 = ImageDraw.Draw(img)
    for _ in range(60):
        x = rng.uniform(250, 850) + 30 * math.sin(tg * 0.7 + rng.uniform(0, 6)); y = (rng.uniform(200, 1700) - 25 * tg) % 1500 + 200
        r = rng.uniform(2, 5); d2.ellipse((x - r, y - r, x + r, y + r), fill=(255, 210, 160, 160))

# ------------------------------------------------------------------ plans (débuts calés sur les mots)
S = [("titre", 0.0), ("kalonia", T("À")), ("matin", T("un", 2)), ("court", T("et", 1)), ("grands", T("sur", 1)),
     ("petit", T("toi")), ("soir", T("alors", 1)), ("tournoi", T("le", 5)), ("zed", T("tout", 2)), ("banc", T("kaï", 2)),
     ("coach", T("à", 2)), ("cri", T("alors", 2)), ("but1", T("premier")), ("but2", T("deuxième")), ("recruteur", T("recruteur", 2)),
     ("lepetit", T("le", 9)), ("abonne", T("abonnetoi")), ("question", T("répondsmoi")), ("logo", T("mindset"))]
SC = dict(S)

def p_titre(img, tg, k):
    img.paste(cover(BG["aube"], 1.3 - 0.2 * eout(k / 4.5), 0.5, 0.45)); shade(img, 120)
    text(img, "PERSONNE NE CROYAIT EN LUI", W / 2, 520, 62, WHITE, k - 0.1, stroke=6)
    text(img, "KAÏ", W / 2, 820, 300, OR, k - T("kaï") + 0.1, stroke=12)
    text(img, "ÉPISODE 1", W / 2, 1040, 84, WHITE, k - T("épisode") + 0.1, stroke=7)
    text(img, "Histoire imaginaire", W / 2, 1150, 40, (220, 220, 230), k - 0.6, stroke=4, pop=False)

def p_kalonia(img, tg, k):
    u = ease(k / 3.0)
    img.paste(cover(BG["aube"], 1.25 - 0.1 * u, 0.5, lerp(0.25, 0.7, u)))
    tag(img, "KALONIA · AVANT LE LEVER DU SOLEIL", k - 0.2)

def p_matin(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), (14, 16, 32, 255))); window_light(img, tg)
    z = 1.0 + 0.05 * k
    put(img, "k_matelas", W / 2 + 40, 1720 + 40 * k, 1250 * z)
    shade(img, 30, (255, 140, 40))
    if k > T("ballon") - SC["matin"]: text(img, "UN BALLON RECOUSU", W / 2, 330, 64, OR, k - (T("ballon") - SC["matin"]), stroke=6)

def p_court(img, tg, k):
    img.paste(cover(BG["aube"], 1.08 + 0.04 * k, 0.5, 0.62))
    u = eout(k / 1.2); h = lerp(380, 1900, u)
    put(img, "k_court_face", W / 2 + 30 * math.sin(tg * 18), lerp(1150, 2150, u), h)
    speed_radial(img, tg, 0.4 + 0.5 * u); dust(img, tg, W / 2, 1750, k - 0.6, 30, seed=2)

def p_grands(img, tg, k):
    img.paste(cover(BG["aube"], 1.15, 0.45, 0.7))
    kz = eout(k / 0.5)
    put(img, "z_pointe", W - 260 + 60 * (1 - kz), 1750, 1250, dark=0.55, alpha=0.9)
    put(img, "z_pointe", 230 - 60 * (1 - kz), 1730, 1200, dark=0.55, alpha=0.9, flip=True)
    put(img, "z_pointe", W / 2 + 500 * (1 - kz), 1880, 1550)
    for i, (x, y) in enumerate([(220, 520), (840, 420), (560, 300)]):
        kk = k - (T("rigolent") - SC["grands"]) - 0.15 * i
        text(img, "HA HA !", x, y + 20 * math.sin(tg * 9 + i), 78, WHITE, kk, stroke=7, rot=(-10 + 10 * i))

def p_petit(img, tg, k):
    img.paste(cover(BG["aube"], 1.3, 0.5, 0.75)); shade(img, 90)
    z = 1.0 + 0.25 * eout(k / 2.0)
    put(img, "k_poings", W / 2, 1880 + 500 * (z - 1), 1300 * z)
    put(img, "z_pointe", W + 120, 2050, 2300, dark=0.85, alpha=0.95)
    stamp(img, "TROP PETIT", W / 2, 330, k - (T("trop") - SC["petit"]), 104)

def p_soir(img, tg, k):
    img.paste(cover(BG["soir"], 1.12, 0.5, 0.6))
    tint(img, (20, 30, 90), min(120, 25 * k))
    e1 = T("encore", 1) - SC["soir"]; e2 = T("encore", 2) - SC["soir"]
    if k < e1: x = lerp(-250, W + 250, (k / e1)); fl = False
    elif k < e2: x = lerp(W + 250, -250, (k - e1) / (e2 - e1)); fl = True
    else: x = lerp(-250, W + 250, min(1, (k - e2) / 1.6)); fl = False
    put(img, "k_dribble", x, 1780, 1050, flip=fl)
    speed_h(img, tg, 0.35, 1100, 1700)
    dust(img, tg, x, 1760, (k % 0.6), 18, seed=int(k / 0.6))
    text(img, "SEUL.", W / 2, 380, 110, WHITE, k - (T("seul", 1) - SC["soir"]), stroke=8)
    text(img, "ENCORE.", W / 2, 520, 100, OR, k - e1, stroke=8)
    text(img, "ET ENCORE.", W / 2, 650, 90, YEL, k - e2, stroke=8)

def p_tournoi(img, tg, k):
    img.paste(cover(BG["tournoi"], 1.05 + 0.03 * k, 0.5, 0.5))
    kr = k - (T("recruteur", 1) - SC["tournoi"])
    if kr > 0:
        u = min(1, kr / 2.6); put(img, "r_marche", lerp(W + 100, W / 2 + 180, eout(kr / 0.8)), lerp(1500, 1950, u), lerp(900, 1500, u), dark=0.05)
    stamp(img, "UN SEUL SERA CHOISI", W / 2, 330, k - (T("un", 4) - SC["tournoi"]), 70, OR, -4)
    tag(img, "LE JOUR DU TOURNOI", k - 0.1)

def p_zed(img, tg, k):
    bg = cover(BG["tournoi"], 1.25, 0.5, 0.4).filter(ImageFilter.GaussianBlur(6)); img.paste(bg); shade(img, 60)
    put(img, "z_fete", W / 2, 1900 - 60 * eout(k / 0.4), 1500, glow=(255, 255, 255))
    confetti(img, tg, k); flash(img, k, 0.18, 160)
    text(img, "ZED", W / 2, 300, 120, WHITE, k - 0.2, stroke=8)

def p_banc(img, tg, k):
    im = cover(FULL["k_banc"], 1.0 + 0.06 * k, 0.5, 0.5); img.paste(im); shade(img, 40)
    text(img, "SUR LE BANC.", W / 2, 260, 90, (200, 205, 220), k - (T("banc") - SC["banc"]), stroke=7)

def p_coach(img, tg, k):
    bg = cover(BG["tournoi"], 1.35, 0.3, 0.75).filter(ImageFilter.GaussianBlur(5)); img.paste(bg); shade(img, 110)
    put(img, "b_coach", lerp(-200, 430, eout(k / 0.7)), 1900, 1500)
    secs = max(0, 300 - int(k * 3))
    text(img, f"{secs // 60}:{secs % 60:02d}", W - 230, 330, 110, OR, 1, stroke=7, pop=False)
    text(img, "« VAS-Y. »", W / 2 + 120, 760, 120, WHITE, k - (T("vasy") - SC["coach"]), stroke=9)

def p_cri(img, tg, k):
    img.paste(cover(BG["tournoi"], 1.2 + 0.05 * k, 0.5, 0.35)); tint(img, (255, 140, 30), 90)
    u = eout(k / 0.5); put(img, "k_elan", W / 2, lerp(2100, 1820, u), lerp(1300, 1650, u), glow=(255, 160, 50))
    speed_radial(img, tg, max(0, 1 - k / 2)); flash(img, k, 0.3)
    text(img, "ALORS MONTRE-LEUR", W / 2, 250, 84, WHITE, k, stroke=8)
    text(img, "QUI TU ES !", W / 2, 380, 130, OR, k - (T("qui") - SC["cri"]), stroke=10)

def p_but1(img, tg, k):
    img.paste(cover(BG["tournoi"], 1.25, 0.5, 0.5 + 0.02 * k))
    kd = T("défenseurs") - SC["but1"]; kb = T("but") - SC["but1"]
    if k < kd + 0.3:
        x = lerp(-200, W / 2, eout(k / kd))
        put(img, "z_pointe", lerp(W + 100, -300, k / (kd + 0.3)), 1800, 1200, dark=0.8, alpha=0.85)
        put(img, "z_pointe", lerp(W + 500, 100, k / (kd + 0.3)), 1700, 1050, dark=0.8, alpha=0.8, flip=True)
        put(img, "k_dribble", x, 1820, 1150); speed_h(img, tg, 0.6)
    else:
        put(img, "k_tir", W / 2, 1900, 1550 + 60 * eout((k - kd) / 0.4)); speed_radial(img, tg, 0.6, W * 0.7, H * 0.8)
    flash(img, k - kb, 0.3); text(img, "BUT !", W / 2, 420, 220, OR, k - kb, stroke=12)

def p_but2(img, tg, k):
    img.paste(cover(BG["tournoi"], 1.3, 0.5, 0.3)); tint(img, (255, 170, 60), 50)
    kl = T("lucarne") - SC["but2"]
    u = eout(k / 2.2)  # ralenti : montée lente
    put(img, "k_volee", W / 2 + 40 * math.sin(k), lerp(2200, 1750, u), lerp(1300, 1600, u), rot=lerp(4, -4, u))
    speed_radial(img, tg, 0.3 + 0.5 * (k > kl)); flash(img, k - kl, 0.3)
    text(img, "LUCARNE !", W / 2, 330, 170, YEL, k - kl, stroke=11); confetti(img, tg, k - kl)

def p_recruteur(img, tg, k):
    bg = cover(BG["tournoi"], 1.3, 0.5, 0.6).filter(ImageFilter.GaussianBlur(7)); img.paste(bg); shade(img, 90)
    kp = T("pointe") - SC["recruteur"]
    z = 1.0 + (0.7 * eout((k - kp) / 1.4) if k > kp else 0)
    put(img, "r_pointe", W / 2, 1950 + 900 * (z - 1), 1650 * z)
    if k > kp: speed_radial(img, tg, 0.5, W / 2 - 60, H * 0.38)

def p_lepetit(img, tg, k):
    img.paste(cover(FULL["k_visage"], 1.0 + 0.12 * eout(k / 1.2), 0.5, 0.4))
    text(img, "LE PETIT.", W / 2, 1560, 130, OR, k - 0.1, stroke=10)

def p_abonne(img, tg, k):
    img.paste(cover(BG["aube"], 1.2, 0.5, 0.6)); shade(img, 150)
    put(img, "k_poings", W / 2, 1900, 1100, glow=(255, 140, 40))
    sc = back(k / 0.35) + 0.03 * math.sin(tg * 8)
    L = Image.new("RGBA", (720, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, 719, 189), 50, fill=RED + (255,)); d.text((360, 95), "+  ABONNE-TOI", font=F(84), fill=WHITE, anchor="mm")
    L = L.resize((max(4, int(720 * sc)), max(4, int(190 * sc)))); img.alpha_composite(L, (int(W / 2 - L.width / 2), int(300 - L.height / 2)))
    text(img, "ÉPISODE 2 · DIMANCHE PROCHAIN", W / 2, 500, 58, OR, k - (T("suite") - SC["abonne"]), stroke=6)
    text(img, "L'ESSAI À LA CAPITALE", W / 2, 600, 64, WHITE, k - (T("lessai") - SC["abonne"]), stroke=6)

def ring(img, cx, cy, r, u):
    d = ImageDraw.Draw(img); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(60, 66, 90), width=22)
    d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * u, fill=OR, width=22)

def p_question(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), NAVY + (255,)))
    v = 1 + int(tg * 2.2) % 10; ring(img, W / 2, 1000, 260, v / 10); text(img, f"{v}/10", W / 2, 1000, 150, WHITE, 1, pop=False)
    text(img, "SUR 10, TA CONFIANCE", W / 2, 330, 78, WHITE, k - (T("sur", 3) - SC["question"]), stroke=6)
    text(img, "QUAND ON TE DIT", W / 2, 440, 60, WHITE, k - (T("quand", 2) - SC["question"]), stroke=6)
    text(img, "« TROP PETIT » ?", W / 2, 550, 96, OR, k - (T("trop", 2) - SC["question"]), stroke=8)
    kc = k - (T("écris") - SC["question"]) + 0.2
    if kc > 0:
        L = Image.new("RGBA", (720, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle((0, 0, 719, 129), 40, fill=OR + (255,)); d.text((360, 65), "ÉCRIS TON CHIFFRE", font=F(62), fill=(15, 15, 20), anchor="mm")
        img.alpha_composite(L, (int(W / 2 - 360), int(1440 + 10 * math.sin(tg * 9))))

def p_logo(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), NAVY + (255,)))
    fade = 1 - ease((tg - (END - 0.7)) / 0.7)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    sc = 1 + 0.15 * (1 - eout(k / 0.5)); g = tuple(int(c * fade) for c in (240, 190, 70))
    dl.text((W / 2, 690), "MINDSET", font=F(150 * sc), fill=g + (255,), anchor="mm"); dl.text((W / 2, 900), "24", font=F(300 * sc), fill=g + (255,), anchor="mm")
    gl = L.filter(ImageFilter.GaussianBlur(26)); img.alpha_composite(gl); img.alpha_composite(gl); img.alpha_composite(L)
    text(img, "Change ton mental.", W / 2, 1180, 64, WHITE, k - (T("change", 1) - SC["logo"]), pop=False, alpha=fade, stroke=0)
    text(img, "Change ta vie.", W / 2, 1270, 64, WHITE, k - (T("change", 2) - SC["logo"]), pop=False, alpha=fade, stroke=0)

PLANS = {n: globals()["p_" + n] for n, _ in S}

# karaoké
CH = []; cur = []
for w in WORDS:
    cur.append(w)
    if len(cur) == 3 or w["text"][-1] in ".?!,:…»": CH.append(cur); cur = []
if cur: CH.append(cur)
def karaoke(img, tg):
    if tg >= SC["question"] - 0.05: return
    for ch in CH:
        if ch[0]["start"] - 0.02 <= tg < ch[-1]["end"] + 0.1: break
    else: return
    ws = [w["text"].upper() for w in ch]; size = 66
    while sum(F(size).getlength(x) for x in ws) + 22 * (len(ws) - 1) > 960: size -= 4
    f = F(size); tw = sum(f.getlength(x) for x in ws) + 22 * (len(ws) - 1)
    L = Image.new("RGBA", (W, int(size * 1.7)), (0, 0, 0, 0)); d = ImageDraw.Draw(L); x = (W - tw) / 2
    for w, s in zip(ch, ws):
        on = w["start"] <= tg < w["end"] + 0.05
        d.text((x, size * 0.25), s, font=f, fill=(YEL if on else WHITE) + (255,), stroke_width=8, stroke_fill=(0, 0, 0, 255)); x += f.getlength(s) + 22
    img.alpha_composite(L, (0, int(H * 0.86)))

def render(tg):
    i = max(j for j, (_, s) in enumerate(S) if s <= tg + 1e-6); n, s = S[i]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); PLANS[n](img, tg, tg - s)
    return img, i

def main():
    out = sys.argv[1]; t_from = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0; t_to = float(sys.argv[3]) if len(sys.argv) > 3 else END
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = (1 - 0.45 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)).clip(0.45, 1)[..., None]
    grain = np.random.default_rng(1).normal(0, 6, (H // 2, W // 2)).astype(np.float32)
    t0 = time.time()
    for n, fi in enumerate(range(int(t_from * FPS), int(math.ceil(t_to * FPS)))):
        tg = fi / FPS
        img, i = render(tg); lt = tg - S[i][1]
        if i > 0 and lt < 0.12 and S[i][0] not in ("cri", "court"):   # coupe franche + petit fondu
            prev = Image.new("RGBA", (W, H), (0, 0, 0, 255)); PLANS[S[i - 1][0]](prev, tg, tg - S[i - 1][1]); img = Image.blend(prev, img, lt / 0.12)
        karaoke(img, tg)
        a = np.asarray(img.convert("RGB")).astype(np.float32)
        # caméra : dérive + secousse sur les temps forts
        sh = 0.0
        for key in ("cri", "but1", "but2", "court"):
            kk = tg - SC[key]
            if 0 <= kk < 1.2: sh = max(sh, 16 * math.exp(-kk * 3))
        for word in ("but", "lucarne"):
            kk = tg - T(word)
            if 0 <= kk < 1.0: sh = max(sh, 22 * math.exp(-kk * 4))
        Mx = cv2.getRotationMatrix2D((W / 2, H / 2), 0.3 * math.sin(tg * 0.5) + 0.5 * math.sin(tg * 41) * sh / 16, 1.02 + 0.01 * math.sin(tg * 0.7))
        Mx[0, 2] += sh * math.sin(tg * 63); Mx[1, 2] += sh * math.sin(tg * 51)
        a = cv2.warpAffine(a, Mx, (W, H), borderMode=cv2.BORDER_REFLECT)
        g = np.roll(grain, (fi * 37) % (H // 2), axis=0)
        a = a * vign + cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
        ff.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
        if n % 150 == 0: print(f"t={tg:.1f}s {time.time() - t0:.0f}s", flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    main()

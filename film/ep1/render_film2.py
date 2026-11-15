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
BG["aube"] = BG["aube"].crop((6, 95, 1146, 2042)); BG["soir"] = BG["soir"].crop((50, 55, 1102, 2010))  # bords blancs des images Gemini
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

# ------------------------------------------------------------------ plans v2 (15/11) : cold open + arc d'entraînement
def Ta(word, after=0.0):
    """début du 1er mot `word` qui commence après `after` secondes"""
    for w in WORDS:
        if norm(w["text"]) == norm(word) and w["start"] >= after - 1e-6: return w["start"]
    raise KeyError(word)

t_kai = T("kaï"); t_14 = T("quatorze"); t_prem = T("premier"); t_les = T("les")
t_lend = T("lendemain"); t_avec = T("avec"); t_drib = T("dribble"); t_coach = T("coach")
t_alors = T("alors"); t_passes = T("passes"); t_trois = T("trois"); t_tour = Ta("le", T("tournoi") - 0.6)
t_kai2 = T("kaï", 2); t_cinq = T("cinq"); t_cri = T("montreleur"); t_p2 = T("premier", 2); t_d2 = T("deuxième")
t_rec2 = T("recruteur", 2); t_lepetit = Ta("le", T("doigt")); t_ab = T("abonnetoi"); t_sur = Ta("sur", t_ab); t_mind = T("mindset")
S = [("cold", 0.0), ("titre", t_kai), ("quartier", t_14), ("match", t_prem), ("rires", t_les), ("aube", t_lend), ("ballon", t_avec),
     ("train", t_drib - 0.1), ("coach", t_coach), ("sprints", t_alors), ("mur", t_passes), ("mois", t_trois), ("tournoi", t_tour),
     ("banc", t_kai2), ("coach2", t_cinq), ("cri", t_cri), ("but1", t_p2), ("but2", t_d2), ("recruteur", t_rec2),
     ("lepetit", t_lepetit), ("abonne", t_ab), ("question", t_sur), ("logo", t_mind)]
SC = dict(S)

def ballx(img, x, y, r=34, a=1.0):
    d = ImageDraw.Draw(img)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(245, 242, 235, int(255 * a)), outline=(20, 20, 20, int(255 * a)), width=5)
    d.polygon([(x, y - r * 0.45), (x + r * 0.42, y - r * 0.12), (x + r * 0.27, y + r * 0.38), (x - r * 0.27, y + r * 0.38), (x - r * 0.42, y - r * 0.12)], fill=(25, 25, 25, int(255 * a)))

def night(img, a):  # assombrit vers la nuit bleue
    tint(img, (8, 14, 48), int(max(0, min(1, a)) * 170))

def stars(img, tg, a):
    if a <= 0: return
    d = ImageDraw.Draw(img); rng = np.random.default_rng(3)
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.4); r = rng.uniform(1.5, 3.5)
        tw = 0.6 + 0.4 * math.sin(tg * rng.uniform(2, 5) + rng.uniform(0, 6))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 240, int(220 * a * tw)))

def xmark(img, cx, cy, k, s=150):
    if k < 0: return
    u = eout(k / 0.18); d = ImageDraw.Draw(img); w = 26
    d.line((cx - s * u, cy - s * u, cx + s * u, cy + s * u), fill=RED + (235,), width=w)
    d.line((cx + s * u, cy - s * u, cx - s * u, cy + s * u), fill=RED + (235,), width=w)

def p_cold(img, tg, k):
    # cold open : Kaï à terre dans le sable, les grands qui rient au-dessus de lui (contre-plongée), puis éclair du futur
    img.paste(cover(BG["aube"], 1.35 - 0.06 * k, 0.5, 0.78)); shade(img, 70)
    for i, (x, h, fl) in enumerate([(170, 1500, True), (W - 170, 1550, False), (W / 2 + 40, 1350, False)]):
        put(img, "z_pointe", x + 8 * math.sin(tg * 6 + i), 1500 + 20 * i, h, dark=0.82, alpha=0.95, flip=fl)
    put(img, "k_dribble", W / 2 - 20, 1800, 1000, rot=78, dark=0.05)
    dust(img, tg, W / 2, 1850, k, 34, seed=11)
    for i, (x, y) in enumerate([(230, 420), (850, 360), (560, 250)]):
        text(img, "HA HA !", x, y + 18 * math.sin(tg * 9 + i), 74, WHITE, k - 0.25 - 0.2 * i, stroke=7, rot=(-10 + 10 * i))
    kf = k - (T("devenir") - 0.15)
    if kf > 0:   # éclair du futur : silhouette dorée en pleine volée
        img.paste(cover(BG["tournoi"], 1.3, 0.5, 0.3)); tint(img, (255, 150, 40), 120)
        put(img, "k_volee", W / 2, 1800, 1500, glow=(255, 190, 80)); speed_radial(img, tg, 0.8); flash(img, kf, 0.25)

def p_titre(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), NAVY + (255,)))
    bg = cover(BG["aube"], 1.25 - 0.08 * eout(k / 3), 0.5, 0.45); bg.putalpha(110); img.alpha_composite(bg)
    text(img, "MINDSET 24 PRÉSENTE", W / 2, 520, 50, (240, 190, 70), k - 0.05, stroke=5, pop=False)
    text(img, "KAÏ", W / 2, 840, 320, OR, k, stroke=12)
    text(img, "ÉPISODE 1", W / 2, 1070, 84, WHITE, k - (T("épisode") - SC["titre"]), stroke=7)
    text(img, "PERSONNE NE CROYAIT EN LUI", W / 2, 1190, 46, (220, 220, 230), k - 0.6, stroke=4, pop=False)

def p_quartier(img, tg, k):
    u = ease(k / 2.2); img.paste(cover(BG["aube"], 1.2 - 0.08 * u, 0.5, lerp(0.35, 0.7, u)))
    put(img, "z_pointe", W - 230, 1880, 1650, dark=0.7, alpha=0.9)
    put(img, "k_poings", 330, 1880, 1050)
    d = ImageDraw.Draw(img)   # toise
    for yy in range(830, 1880, 70): d.line((560, yy, 600 if (yy // 70) % 2 else 585, yy), fill=WHITE + (200,), width=5)
    d.line((560, 830, 560, 1880), fill=WHITE + (200,), width=5)
    tag(img, "KALONIA · 14 ANS", k - 0.1)
    stamp(img, "LE PLUS PETIT", W / 2, 420, k - (T("plus") - SC["quartier"]), 90)

def p_match(img, tg, k):
    img.paste(cover(BG["aube"], 1.15 + 0.03 * k, 0.5, 0.66))
    kt = T("tombe") - SC["match"]
    if k < kt:
        x = lerp(-150, W / 2 + 60, eout(k / kt)); put(img, "k_dribble", x, 1800, 1050); ballx(img, x + 220, 1760)
        put(img, "z_pointe", W - 200, 1820, 1350, dark=0.75, alpha=0.9, flip=True)
    else:
        kk = k - kt; put(img, "z_pointe", W - 200, 1820, 1350, dark=0.75, alpha=0.9, flip=True)
        put(img, "k_dribble", W / 2 + 60, 1830 + 60 * eout(kk / 0.3), 1050, rot=lerp(0, 80, eout(kk / 0.3)))
        ballx(img, W / 2 + 280 + 500 * kk, 1760 - 60 * kk); dust(img, tg, W / 2 + 60, 1820, kk, 40, seed=3)
        text(img, "BOUM.", W / 2, 520, 120, WHITE, kk, stroke=9)

def p_rires(img, tg, k):
    img.paste(cover(BG["aube"], 1.3, 0.45, 0.72)); shade(img, 60)
    kz = eout(k / 0.4)
    put(img, "z_pointe", W - 240 + 60 * (1 - kz), 1780, 1300, dark=0.55, alpha=0.9)
    put(img, "z_pointe", 220 - 60 * (1 - kz), 1760, 1250, dark=0.55, alpha=0.9, flip=True)
    put(img, "z_pointe", W / 2 + 400 * (1 - kz), 1950, 1650)
    for i, (x, y) in enumerate([(230, 520), (850, 420)]):
        text(img, "HA HA !", x, y + 20 * math.sin(tg * 9 + i), 74, WHITE, k - 0.1 - 0.15 * i, stroke=7, rot=(-10 + 14 * i))
    stamp(img, "RENTRE CHEZ TOI", W / 2, 300, k - (T("rentre") - SC["rires"]), 80)

def p_aube(img, tg, k):
    # avant le soleil : bleu nuit qui s'éclaircit, Kaï déjà là, seul et minuscule
    img.paste(cover(BG["aube"], 1.1 + 0.02 * k, 0.5, 0.6)); night(img, 1 - 0.5 * ease(k / 3)); stars(img, tg, 1 - k / 3)
    put(img, "k_poings", W / 2, 1640, 520, dark=0.25)
    tag(img, "LE LENDEMAIN · 5 H DU MATIN", k - 0.1)
    text(img, "SEUL.", W / 2, 520, 130, WHITE, k - (T("seul") - SC["aube"]), stroke=9)

def p_ballon(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), (14, 16, 32, 255))); window_light(img, tg)
    put(img, "k_matelas", W / 2 + 40, 1760 + 40 * k, 1250 * (1 + 0.05 * k))
    text(img, "UN BALLON RECOUSU", W / 2, 330, 64, OR, k - (T("ballon", 2) - SC["ballon"]), stroke=6)

def p_train(img, tg, k):
    """montage d'entraînement calé sur : dribble / tombe / relève / tire / rate / recommence"""
    t0 = SC["train"]; ks = {w: Ta(w, t0) - t0 for w in ("dribble", "tombe", "relève", "tire", "rate", "recommence")}
    img.paste(cover(BG["soir"], 1.12, 0.5, 0.6))
    if k < ks["tombe"]:
        x = lerp(-200, W + 200, k / ks["tombe"]); put(img, "k_dribble", x, 1790, 1000); ballx(img, x + 200, 1755)
        speed_h(img, tg, 0.4, 1100, 1700); text(img, "IL DRIBBLE.", W / 2, 400, 96, WHITE, k - 0.05, stroke=8)
    elif k < ks["relève"]:
        kk = k - ks["tombe"]; put(img, "k_dribble", W / 2, 1830, 1000, rot=lerp(0, 75, eout(kk / 0.3)))
        dust(img, tg, W / 2, 1800, kk, 36, seed=5); xmark(img, W / 2, 450, kk - 0.1, 110)
        text(img, "IL TOMBE.", W / 2, 680, 96, WHITE, kk, stroke=8)
    elif k < ks["tire"]:
        kk = k - ks["relève"]; u = eout(kk / 0.8); img.paste(cover(BG["soir"], 1.3, 0.5, 0.7))
        put(img, "k_poings", W / 2, lerp(2350, 1880, u), 1200, glow=(255, 150, 50) if kk > 0.6 else None)
        text(img, "IL SE RELÈVE.", W / 2, 400, 92, OR, kk, stroke=8)
    elif k < ks["recommence"]:
        kk = k - ks["tire"]; kr = ks["rate"] - ks["tire"]
        put(img, "k_tir", W / 2 - 120, 1880, 1300)
        bx = lerp(W / 2 + 120, W + 120, min(1, kk / 0.9)); by = 1650 - 900 * min(1, kk / 0.9) + 500 * min(1, kk / 0.9) ** 2
        ballx(img, bx, by)
        text(img, "IL TIRE.", W / 2, 360, 92, WHITE, kk, stroke=8)
        if kk > kr: stamp(img, "RATÉ", W / 2, 560, kk - kr, 100)
    else:
        kk = k - ks["recommence"]
        put(img, "k_dribble", lerp(-200, W + 200, (kk * 1.4) % 1), 1790, 1000, alpha=0.9)
        n = int(1 + 999 * ease(kk / 1.2)); text(img, f"ESSAI N° {n}", W / 2, 420, 100, YEL, 1, stroke=8, pop=False)
        text(img, "IL RECOMMENCE.", W / 2, 560, 80, WHITE, kk, stroke=7)

def p_coach(img, tg, k):
    bg = cover(BG["aube"], 1.3, 0.3, 0.75).filter(ImageFilter.GaussianBlur(5)); img.paste(bg); shade(img, 100)
    put(img, "b_coach", lerp(-200, 420, eout(k / 0.8)), 1900, 1450)
    put(img, "k_poings", W - 200, 1880, 820, dark=0.15)
    kq = k - (T("ta") - SC["coach"])
    text(img, "« TA TAILLE,", W / 2, 420, 100, WHITE, kq, stroke=9)
    text(img, "C'EST TA VITESSE. »", W / 2, 550, 96, OR, k - (T("vitesse") - SC["coach"]), stroke=9)

def p_sprints(img, tg, k):
    # chaque soir : sprints face caméra, en boucle, le ciel passe du coucher de soleil à la nuit
    img.paste(cover(BG["soir"], 1.08 + 0.02 * k, 0.5, 0.62)); night(img, k / 3.0)
    lap = (k * 0.9) % 1; u = eout(lap)
    put(img, "k_court_face", W / 2 + 30 * math.sin(tg * 18), lerp(1150, 2150, u), lerp(380, 1900, u))
    speed_radial(img, tg, 0.3 + 0.5 * u); dust(img, tg, W / 2, 1760, lap, 26, seed=int(k))
    text(img, "CHAQUE SOIR.", W / 2, 330, 96, WHITE, k - 0.05, stroke=8)
    text(img, "SPRINTS DANS LE SABLE", W / 2, 450, 62, OR, k - (T("sprints") - SC["sprints"]), stroke=6)

def p_mur(img, tg, k):
    # passes contre le mur jusqu'à la nuit : le ballon fait des allers-retours
    img.paste(cover(BG["soir"], 1.25, 0.2, 0.55)); night(img, 0.55 + 0.45 * ease(k / 2.5)); stars(img, tg, ease(k / 2.5))
    d = ImageDraw.Draw(img)
    d.rectangle((W - 260, 700, W, 1900), fill=(150, 120, 95, 255)); d.rectangle((W - 260, 700, W - 245, 1900), fill=(70, 55, 45, 255))
    for yy in range(760, 1900, 90):
        for xx in range(W - 260 + (45 if (yy // 90) % 2 else 0), W, 90): d.rectangle((xx, yy, xx + 86, yy + 86), outline=(110, 88, 70, 255), width=3)
    put(img, "k_tir", 360, 1880, 1250)
    ph = (k * 1.6) % 1; bx = lerp(560, W - 300, 1 - abs(2 * ph - 1)); ballx(img, bx, 1700 - 40 * math.sin(ph * math.pi))
    if abs(2 * ph - 1) > 0.94: speed_radial(img, tg, 0.35, W - 300, 1700)
    text(img, "PASSES CONTRE LE MUR", W / 2, 360, 70, WHITE, k - 0.05, stroke=7)
    text(img, "JUSQU'À LA NUIT.", W / 2, 470, 78, YEL, k - (T("nuit") - SC["mur"]), stroke=7)

def p_mois(img, tg, k):
    # 3 mois : les jours défilent, jour/nuit qui clignotent, Kaï de plus en plus rapide
    img.paste(cover(BG["soir"], 1.1, 0.5, 0.6)); day = min(90, int(1 + 89 * ease(k / 1.6)))
    cyc = 0.5 + 0.5 * math.sin(k * 14); night(img, 0.25 + 0.6 * cyc * (1 - ease((k - 1.6) / 0.4)))
    sp = 0.8 + 2.4 * ease(k / 1.8)
    for g in range(3):
        put(img, "k_dribble", lerp(-200, W + 200, ((k - g * 0.05) * sp) % 1), 1790, 1000, alpha=1.0 - 0.3 * g)
    speed_h(img, tg, min(1, sp / 3), 1100, 1700)
    text(img, f"JOUR {day}", W / 2, 360, 120, YEL, 1, stroke=9, pop=False)
    text(img, "3 MOIS.", W / 2, 520, 92, WHITE, k - 0.1, stroke=8)
    text(img, "PERSONNE NE LE REMARQUE.", W / 2, 660, 60, (210, 210, 220), k - (T("personne", 2) - SC["mois"]), stroke=6)

def p_tournoi(img, tg, k):
    img.paste(cover(BG["tournoi"], 1.05 + 0.03 * k, 0.5, 0.5))
    kr = k - (T("recruteur", 1) - SC["tournoi"])
    if kr > 0:
        u = min(1, kr / 2.6); put(img, "r_marche", lerp(W + 100, W / 2 + 180, eout(kr / 0.8)), lerp(1500, 1950, u), lerp(900, 1500, u), dark=0.05)
    stamp(img, "UN SEUL SERA CHOISI", W / 2, 330, k - (Ta("un", T("arrive")) - SC["tournoi"]), 70, OR, -4)
    tag(img, "LE JOUR DU TOURNOI", k - 0.1)

def p_banc(img, tg, k):
    im = cover(FULL["k_banc"], 1.0 + 0.06 * k, 0.5, 0.5); img.paste(im); shade(img, 40)
    text(img, "SUR LE BANC.", W / 2, 260, 90, (200, 205, 220), k - (T("banc") - SC["banc"]), stroke=7)

def p_coach2(img, tg, k):
    bg = cover(BG["tournoi"], 1.35, 0.3, 0.75).filter(ImageFilter.GaussianBlur(5)); img.paste(bg); shade(img, 110)
    put(img, "b_coach", lerp(-200, 430, eout(k / 0.7)), 1900, 1500)
    secs = max(0, 300 - int(k * 3)); text(img, f"{secs // 60}:{secs % 60:02d}", W - 230, 330, 110, OR, 1, stroke=7, pop=False)
    text(img, "« MAINTENANT. »", W / 2 + 60, 760, 110, WHITE, k - (T("maintenant") - SC["coach2"]), stroke=9)

def p_cri(img, tg, k):
    img.paste(cover(BG["tournoi"], 1.2 + 0.05 * k, 0.5, 0.35)); tint(img, (255, 140, 30), 90)
    for i, n in enumerate(("k_dribble", "k_tir", "k_court_face")):   # échos des entraînements
        put(img, n, [200, W - 200, W / 2][i], 1500 + 40 * i, 700, alpha=max(0, 0.45 - k * 0.3), dark=0.3)
    u = eout(k / 0.5); put(img, "k_elan", W / 2, lerp(2100, 1820, u), lerp(1300, 1650, u), glow=(255, 160, 50))
    speed_radial(img, tg, max(0, 1 - k / 2)); flash(img, k, 0.3)
    text(img, "MONTRE-LEUR", W / 2, 250, 110, WHITE, k, stroke=9)
    text(img, "QUI TU ES !", W / 2, 390, 130, OR, k - (T("qui") - SC["cri"]), stroke=10)

def p_but1(img, tg, k):
    img.paste(cover(BG["tournoi"], 1.25, 0.5, 0.5 + 0.02 * k))
    kd = T("dribble", 2) - SC["but1"]; kb = T("but") - SC["but1"]
    if k < kb - 0.2:
        x = lerp(-200, W / 2, eout(max(0, k - kd + 0.4) / 1.4))
        put(img, "z_pointe", lerp(W + 100, -300, k / kb), 1800, 1200, dark=0.8, alpha=0.85)
        put(img, "z_pointe", lerp(W + 500, 100, k / kb), 1700, 1050, dark=0.8, alpha=0.8, flip=True)
        put(img, "k_dribble", x, 1820, 1150); speed_h(img, tg, 0.6)
        text(img, "× 1000", W / 2, 420, 150, YEL, k - (T("mille") - SC["but1"]), stroke=10)
    else:
        put(img, "k_tir", W / 2, 1900, 1550 + 60 * eout((k - kb) / 0.4)); speed_radial(img, tg, 0.6, W * 0.7, H * 0.8)
    flash(img, k - kb, 0.3); text(img, "BUT !", W / 2, 420, 220, OR, k - kb, stroke=12)

def p_but2(img, tg, k):
    img.paste(cover(BG["tournoi"], 1.3, 0.5, 0.3)); tint(img, (255, 170, 60), 50)
    kl = T("lucarne") - SC["but2"]; u = eout(k / 2.2)
    put(img, "k_volee", W / 2 + 40 * math.sin(k), lerp(2200, 1750, u), lerp(1300, 1600, u), rot=lerp(4, -4, u))
    if k < kl:
        text(img, "RATÉE × 100", W / 2, 330, 110, (200, 200, 210), k - (T("cent") - SC["but2"]) + 0.3, stroke=9)
        if k > T("cent") - SC["but2"]: xmark(img, W / 2, 330, k - (T("cent") - SC["but2"]), 60)
    speed_radial(img, tg, 0.3 + 0.5 * (k > kl)); flash(img, k - kl, 0.3)
    text(img, "LUCARNE !", W / 2, 330, 170, YEL, k - kl, stroke=11); confetti(img, tg, k - kl)

def p_recruteur(img, tg, k):
    bg = cover(BG["tournoi"], 1.3, 0.5, 0.6).filter(ImageFilter.GaussianBlur(7)); img.paste(bg); shade(img, 90)
    kp = T("pointe") - SC["recruteur"]; z = 1.0 + (0.7 * eout((k - kp) / 1.4) if k > kp else 0)
    put(img, "r_pointe", W / 2, 1950 + 900 * (z - 1), 1650 * z)
    if k > kp: speed_radial(img, tg, 0.5, W / 2 - 60, H * 0.38)

def p_lepetit(img, tg, k):
    img.paste(cover(FULL["k_visage"], 1.0 + 0.12 * eout(k / 1.2), 0.5, 0.4))
    text(img, "LE PETIT.", W / 2, 1560, 130, OR, k - 0.1, stroke=10)
def p_abonne(img, tg, k):
    img.paste(cover(BG["aube"], 1.2, 0.5, 0.6)); shade(img, 150)
    put(img, "k_poings", W / 2, 1920, 1020, glow=(255, 140, 40))
    sc = back(k / 0.35) + 0.03 * math.sin(tg * 8)
    L = Image.new("RGBA", (720, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, 719, 189), 50, fill=RED + (255,)); d.text((360, 95), "+  ABONNE-TOI", font=F(84), fill=WHITE, anchor="mm")
    L = L.resize((max(4, int(720 * sc)), max(4, int(190 * sc)))); img.alpha_composite(L, (int(W / 2 - L.width / 2), int(300 - L.height / 2)))
    text(img, "KAÏ · ÉPISODE 2", W / 2, 500, 64, OR, k - (T("suite") - SC["abonne"]), stroke=6)
    text(img, "DIMANCHE PROCHAIN", W / 2, 600, 58, WHITE, k - (T("dimanche") - SC["abonne"]), stroke=6)
    kd = k - (T("demain") - SC["abonne"])
    if kd > 0:
        L2 = Image.new("RGBA", (900, 150), (0, 0, 0, 0)); d2 = ImageDraw.Draw(L2)
        d2.rounded_rectangle((0, 0, 899, 149), 34, fill=(10, 12, 20, 220), outline=OR + (255,), width=6)
        d2.text((450, 48), "DEMAIN", font=F(46), fill=OR + (255,), anchor="mm")
        d2.text((450, 106), "ILS ONT FAILLI ABANDONNER · ÉP. 11", font=F(44), fill=WHITE + (255,), anchor="mm")
        a2 = ease(kd / 0.25); L2.putalpha(Image.eval(L2.getchannel("A"), lambda v: int(v * a2)))
        img.alpha_composite(L2, (int(W / 2 - 450), 665))

def ring(img, cx, cy, r, u):
    d = ImageDraw.Draw(img); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(60, 66, 90), width=22)
    d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * u, fill=OR, width=22)

def p_question(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), NAVY + (255,)))
    v = 1 + int(tg * 2.2) % 10; ring(img, W / 2, 1000, 260, v / 10); text(img, f"{v}/10", W / 2, 1000, 150, WHITE, 1, pop=False)
    text(img, "SUR 10, TA CONFIANCE", W / 2, 330, 78, WHITE, k - (T("sur", 3) - SC["question"]), stroke=6)
    text(img, "QUAND ON TE DIT", W / 2, 440, 60, WHITE, k - (Ta("quand", SC["question"]) - SC["question"]), stroke=6)
    text(img, "« TROP PETIT » ?", W / 2, 550, 96, OR, k - (Ta("trop", SC["question"]) - SC["question"]), stroke=8)
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
        if i > 0 and lt < 0.12 and S[i][0] not in ("cri", "train", "mois"):   # coupe franche + petit fondu
            prev = Image.new("RGBA", (W, H), (0, 0, 0, 255)); PLANS[S[i - 1][0]](prev, tg, tg - S[i - 1][1]); img = Image.blend(prev, img, lt / 0.12)
        karaoke(img, tg)
        a = np.asarray(img.convert("RGB")).astype(np.float32)
        # caméra : dérive + secousse sur les temps forts
        sh = 0.0
        for key in ("cri", "but1", "but2", "match", "cold"):
            if key not in SC: continue
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

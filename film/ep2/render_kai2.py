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


# ------------------------------------------------------------------ KAÏ ÉPISODE 2 (22/11/2026) : l'académie de la capitale
def Ta(word, after=0.0):
    for w in WORDS:
        if norm(w["text"]) == norm(word) and w["start"] >= after - 1e-6: return w["start"]
    raise KeyError(word)

t_mind = T("mindset"); t_prec = T("précédemment"); t_auj = T("aujourdhui"); t_40 = T("quarante"); t_et = Ta("et", t_auj)
t_prem = T("premier"); t_tab = T("tableau"); t_q40 = T("quarantième"); t_dans = T("dans", 2); t_rentre = T("rentre")
t_nuit = T("cette"); t_sous = T("sous"); t_ctrl = T("contrôle"); t_demi = T("demitour"); t_acc = T("accélération"); t_enc = T("encore")
t_j10 = T("jour"); t_j20 = T("jour", 2); t_dern = T("dernier"); t_le = Ta("le", t_dern + 1.0); t_tout = Ta("tout", t_dern)
t_cri = T("pas", 2); t_un = Ta("un", t_cri); t_kai3 = Ta("kaï", t_cri); t_frappe = T("frappe"); t_but = T("but")
t_coach = T("coach"); t_lit = T("lit"); t_ab = T("abonnetoi"); t_dem = T("demain"); t_et2 = Ta("et", T("vraie")); t_sur = Ta("sur", t_et2)
t_mind2 = T("mindset", 2)
S = [("cold", 0.0), ("titre", t_mind - 0.1), ("prec", t_prec - 0.1), ("capitale", t_auj - 0.1), ("toise", t_et - 0.1),
     ("duels", t_prem - 0.1), ("tableau", t_tab - 0.1), ("vestiaire", t_dans - 0.1), ("nuit", t_nuit - 0.1), ("drill", t_sous - 0.1),
     ("jours", t_j10 - 0.1), ("match", t_dern - 0.1), ("charge", t_le - 0.1), ("cri", t_cri - 0.08), ("crochet", t_un - 0.1),
     ("goal", t_frappe - 0.3), ("liste", t_coach - 0.5), ("abonne", t_ab - 0.1), ("question", t_et2 - 0.1), ("logo", t_mind2 - 0.1)]
SC = dict(S)
NIGHT_SKY = ((8, 12, 36), (40, 30, 70), (255, 120, 40))

def grad(img, top, mid, bot, hy=0.55):
    a = np.zeros((H, W, 3), np.float32); y = np.linspace(0, 1, H)[:, None]
    for c in range(3):
        v1 = top[c] + (mid[c] - top[c]) * np.clip(y / hy, 0, 1)
        v2 = mid[c] + (bot[c] - mid[c]) * np.clip((y - hy) / (1 - hy), 0, 1)
        a[..., c] = np.where(y < hy, v1, v2)
    img.paste(Image.fromarray(a.astype(np.uint8)).convert("RGBA"))

def skyline(img, tg, base=1250, dusk=0.6, seed=7, scale=1.0, shift=0.0):
    """ville au trait façon manga : immeubles noirs cernés, fenêtres orange qui s'allument"""
    d = ImageDraw.Draw(img); rng = np.random.default_rng(seed); x = -60 + shift
    while x < W + 60:
        bw = rng.uniform(70, 170) * scale; bh = rng.uniform(180, 620) * scale
        col = (int(18 + 20 * dusk), int(20 + 18 * dusk), int(38 + 20 * dusk), 255)
        d.rectangle((x, base - bh, x + bw, base), fill=col, outline=(0, 0, 0, 255), width=4)
        if rng.random() < 0.3: d.line((x + bw * 0.5, base - bh, x + bw * 0.5, base - bh - 60 * scale), fill=(0, 0, 0, 255), width=4)
        for wy in np.arange(base - bh + 22, base - 20, 34 * scale):
            for wx in np.arange(x + 12, x + bw - 16, 26 * scale):
                if rng.random() < 0.45:
                    fl = 0.75 + 0.25 * math.sin(tg * rng.uniform(0.5, 2) + rng.uniform(0, 6))
                    d.rectangle((wx, wy, wx + 12 * scale, wy + 16 * scale), fill=(255, int(170 * fl), 60, 230))
        x += bw + rng.uniform(4, 22)

def palm(d, x, base, h, col=(5, 6, 14, 255)):
    d.line((x, base, x + h * 0.12, base - h), fill=col, width=int(h * 0.05))
    tx, ty = x + h * 0.12, base - h
    for an in (-150, -120, -60, -30, -95, -10, -170):
        r = math.radians(an); ex, ey = tx + math.cos(r) * h * 0.42, ty + math.sin(r) * h * 0.18 + h * 0.16
        d.line((tx, ty, (tx + ex) / 2, ty - h * 0.06, ex, ey), fill=col, width=int(h * 0.025))

def gate(img, k_open=0.0):
    d = ImageDraw.Draw(img)
    for px in (90, W - 150):
        d.rectangle((px, 700, px + 60, 1900), fill=(30, 32, 46, 255), outline=(0, 0, 0, 255), width=6)
        d.rectangle((px - 14, 680, px + 74, 720), fill=(50, 52, 70, 255), outline=(0, 0, 0, 255), width=5)
    for i in range(14):
        x = 160 + i * (W - 320) / 13; off = (k_open * 380) * (1 if x > W / 2 else -1)
        d.line((x + off, 820, x + off, 1900), fill=(15, 15, 22, 255), width=9)
    d.line((150 - k_open * 380, 860, W / 2 - k_open * 380, 860), fill=(15, 15, 22, 255), width=12)
    d.line((W / 2 + k_open * 380, 860, W - 150 + k_open * 380, 860), fill=(15, 15, 22, 255), width=12)

def city_bg(img, tg, k, night_a=0.0):
    grad(img, (24, 22, 60), (210, 90, 50), (255, 170, 70), 0.5)
    d = ImageDraw.Draw(img); d.ellipse((W / 2 - 110, 980 - 30 * k, W / 2 + 110, 1200 - 30 * k), fill=(255, 140, 40, 255))
    skyline(img, tg, 1180, 0.2, seed=3, scale=0.7, shift=-20 * k); skyline(img, tg, 1330, 0.5, seed=9, scale=1.0, shift=-50 * k)
    for x, h in ((70, 520), (W - 90, 600), (W - 260, 380)): palm(d, x - 80 * k * (1 if x > W / 2 else -1) * 0.2, 1400, h)
    d.rectangle((0, 1330, W, H), fill=(52, 44, 50, 255)); d.line((0, 1330, W, 1330), fill=(0, 0, 0, 255), width=6)
    for i in range(9): d.line((W / 2 - 40 + i * 0, 1400 + i * 70, W / 2 + 40, 1400 + i * 70), fill=(255, 200, 120, 160), width=8)
    if night_a: night(img, night_a)

def lockers(img):
    grad(img, (40, 44, 60), (58, 62, 80), (30, 30, 40), 0.7)
    d = ImageDraw.Draw(img)
    for i in range(8):
        x = -20 + i * 140
        d.rectangle((x, 380, x + 136, 1330), fill=(78, 86, 104, 255), outline=(0, 0, 0, 255), width=5)
        for yy in (440, 470, 500): d.line((x + 30, yy, x + 106, yy), fill=(20, 22, 30, 255), width=5)
        d.rectangle((x + 108, 820, x + 120, 900), fill=(200, 200, 210, 255))
    d.rectangle((0, 1330, W, H), fill=(110, 96, 82, 255)); d.line((0, 1330, W, 1330), fill=(0, 0, 0, 255), width=6)
    d.rectangle((60, 1450, W - 60, 1500), fill=(150, 110, 70, 255), outline=(0, 0, 0, 255), width=5)
    for x in (110, W - 140): d.rectangle((x, 1500, x + 30, 1640), fill=(60, 45, 30, 255), outline=(0, 0, 0, 255), width=4)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(700, 0), (980, 0), (760, 1700), (300, 1700)], fill=(255, 220, 160, 40)); img.alpha_composite(L.filter(ImageFilter.GaussianBlur(30)))

def alley(img, tg, lamp=1.0, lx=760):
    grad(img, (4, 6, 22), (14, 18, 46), (20, 20, 34), 0.6); stars(img, tg, 0.9)
    d = ImageDraw.Draw(img)
    skyline(img, tg, 1050, 0.0, seed=21, scale=0.6)
    d.rectangle((0, 820, 330, H), fill=(58, 48, 50, 255)); d.line((330, 820, 330, H), fill=(0, 0, 0, 255), width=6)
    for yy in range(840, H, 60):
        for xx in range((0 if (yy // 60) % 2 else -45), 330, 90): d.rectangle((xx, yy, xx + 88, yy + 58), outline=(30, 24, 26, 255), width=3)
    d.rectangle((0, 1600, W, H), fill=(36, 34, 42, 255)); d.line((0, 1600, W, 1600), fill=(0, 0, 0, 255), width=5)
    fl = lamp * (0.93 + 0.07 * math.sin(tg * 23) * math.sin(tg * 7))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    dl.polygon([(lx - 30, 560), (lx + 30, 560), (lx + 420, 1900), (lx - 420, 1900)], fill=(255, 150, 50, int(90 * fl)))
    dl.ellipse((lx - 430, 1560, lx + 430, 1820), fill=(255, 160, 60, int(120 * fl)))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(img)
    d.rectangle((lx + 150, 520, lx + 170, 1640), fill=(12, 12, 18, 255)); d.line((lx + 160, 530, lx + 20, 530), fill=(12, 12, 18, 255), width=16)
    d.polygon([(lx - 40, 528), (lx + 40, 528), (lx + 22, 560), (lx - 22, 560)], fill=(20, 20, 26, 255))
    d.ellipse((lx - 22, 548, lx + 22, 574), fill=(255, 230, 170, int(255 * fl)))
    rng = np.random.default_rng(2)
    for _ in range(14):   # papillons de nuit autour de la lampe
        an = tg * rng.uniform(2, 5) + rng.uniform(0, 6); r = rng.uniform(30, 120)
        x, y = lx + math.cos(an) * r, 600 + math.sin(an * 1.3) * r * 0.6; d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 230, 190, 200))

def stadium(img, tg, k, lights=1.0, warm=0.0):
    img.paste(cover(BG["tournoi"], 1.25 + 0.03 * k, 0.5, 0.42)); night(img, 0.9 - 0.4 * warm)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for x in (90, W - 90):
        dl.polygon([(x - 20, 120), (x + 20, 120), (W / 2 + (x - W / 2) * 0.1 + 260, 1900), (W / 2 + (x - W / 2) * 0.1 - 260, 1900)], fill=(220, 230, 255, int(55 * lights)))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(20)))
    d = ImageDraw.Draw(img)
    for x in (90, W - 90):
        d.rectangle((x - 70, 70, x + 70, 150), fill=(30, 30, 40, 255), outline=(0, 0, 0, 255), width=4)
        for i in range(4): d.ellipse((x - 60 + i * 32, 90, x - 36 + i * 32, 130), fill=(255, 255, 235, int(255 * lights)))
    if warm: tint(img, (255, 140, 30), int(80 * warm))

def silhouette(img, name, cx, by, h, flip=False, rot=0.0, a=0.95):
    put(img, name, cx, by, h, dark=0.85, alpha=a, flip=flip, rot=rot)

def series_band(img, tg):
    """bandeau de série permanent (0–3 s) : KAÏ · ÉPISODE 2"""
    L = Image.new("RGBA", (W, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((0, 0, W, 110), fill=(10, 12, 24, 215)); d.rectangle((0, 104, W, 110), fill=OR + (255,))
    d.text((W / 2, 55), "KAÏ  ·  ÉPISODE 2", font=F(54), fill=WHITE + (255,), anchor="mm")
    img.alpha_composite(L, (0, 60))

def p_cold(img, tg, k):
    # trois géants devant le portail de l'académie, Kaï minuscule au centre
    city_bg(img, tg, k * 0.3, 0.35); gate(img, 0)
    for i, (x, h, fl) in enumerate([(150, 1700, True), (W - 150, 1760, False), (W / 2 + 280, 1450, False)]):
        silhouette(img, "z_pointe", x + 6 * math.sin(tg * 5 + i), 1960, h * (1 + 0.04 * k), flip=fl)
    put(img, "k_poings", W / 2 - 60, 1900, 640 * (1 + 0.05 * k), glow=(255, 150, 50))
    stamp(img, "TROP PETIT ?", W / 2, 560, k - 0.05, 120)
    text(img, "POUR L'ACADÉMIE", W / 2, 740, 70, WHITE, k - 0.35, stroke=7)
    series_band(img, tg)

def p_titre(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), NAVY + (255,)))
    bg = Image.new("RGBA", (W, H)); city_bg(bg, tg, 1 + k * 0.2, 0.5); bg.putalpha(110); img.alpha_composite(bg)
    text(img, "MINDSET 24 PRÉSENTE", W / 2, 520, 50, (240, 190, 70), k - 0.05, stroke=5, pop=False)
    text(img, "KAÏ", W / 2, 840, 320, OR, k - (T("kaï") - SC["titre"]), stroke=12)
    text(img, "ÉPISODE 2", W / 2, 1070, 96, WHITE, k - (T("épisode") - SC["titre"]), stroke=7)
    text(img, "L'ACADÉMIE", W / 2, 1200, 60, (220, 220, 230), k - (T("épisode") - SC["titre"]) - 0.3, stroke=5, pop=False)

def p_prec(img, tg, k):
    # flash-back sépia de l'épisode 1 : le recruteur désigne le petit
    kv = T("petit", 2) - SC["prec"]
    if k < kv:
        bg = cover(BG["tournoi"], 1.3, 0.5, 0.6).filter(ImageFilter.GaussianBlur(6)); img.paste(bg); shade(img, 80)
        put(img, "r_pointe", W / 2, 1950 + 200 * eout(k / 2), 1650 * (1 + 0.12 * eout(k / 2)))
    else:
        img.paste(cover(FULL["k_visage"], 1.05 + 0.08 * (k - kv), 0.5, 0.42))
        text(img, "LE PETIT.", W / 2, 1560, 130, OR, k - kv, stroke=10)
    g = np.asarray(img.convert("L")); sep = Image.merge("RGB", [Image.fromarray(np.clip(g * 1.05 + 20, 0, 255).astype(np.uint8)),
        Image.fromarray(np.clip(g * 0.92 + 8, 0, 255).astype(np.uint8)), Image.fromarray(np.clip(g * 0.72, 0, 255).astype(np.uint8))])
    img.paste(sep.convert("RGBA"))
    tag(img, "PRÉCÉDEMMENT…", k - 0.05)

def p_capitale(img, tg, k):
    # arrivée : la grande ville au crépuscule, le portail s'ouvre, Kaï avance vers nous
    city_bg(img, tg, k, 0.15 * k / 5); kg = k - (T("arrive") - SC["capitale"]); gate(img, ease(kg / 1.6))
    u = ease(k / 5.5); put(img, "k_court_face", W / 2, lerp(1450, 1980, u), lerp(420, 1100, u))
    tag(img, "LA CAPITALE · L'ACADÉMIE", k - 0.1)
    k40 = k - (t_40 - SC["capitale"])
    if k40 > 0:
        n = min(40, int(1 + 39 * ease(k40 / 0.7))); text(img, f"{n} JOUEURS", W / 2, 420, 110, WHITE, k40, stroke=9, pop=False)
    text(img, "3 PLACES", W / 2, 560, 120, OR, k - (T("trois") - SC["capitale"]), stroke=10)

def p_toise(img, tg, k):
    lockers(img); shade(img, 60)
    d = ImageDraw.Draw(img)
    for yy in range(700, 1880, 60): d.line((540, yy, 590 if (yy // 60) % 2 else 570, yy), fill=WHITE + (220,), width=5)
    d.line((540, 700, 540, 1880), fill=WHITE + (220,), width=5)
    for i, x in enumerate((180, W - 180, W - 380)):
        silhouette(img, "z_pointe", x, 1900, 1500 + 60 * i, flip=i == 0, a=0.9)
    put(img, "k_poings", 420, 1900, lerp(1100, 980, eout(k / 0.6)), glow=(255, 150, 50))
    stamp(img, "LE PLUS PETIT", W / 2, 420, k - (T("plus") - SC["toise"]), 100)

def p_duels(img, tg, k):
    # duels perdus en série : il fonce, il tombe, compteur de défaites
    img.paste(cover(BG["soir"], 1.2, 0.5, 0.65)); night(img, 0.35)
    cyc = 1.15; n = int(k / cyc); kk = k % cyc
    silhouette(img, "z_pointe", W - 260 + 20 * math.sin(tg * 4), 1900, 1500, flip=True)
    if kk < 0.5:
        x = lerp(-150, W / 2, eout(kk / 0.5)); put(img, "k_dribble", x, 1840, 1000); ballx(img, x + 220, 1800)
    else:
        u = eout((kk - 0.5) / 0.25); put(img, "k_dribble", W / 2 - 40, 1860 + 40 * u, 1000, rot=lerp(0, 80, u))
        dust(img, tg, W / 2, 1860, kk - 0.5, 30, seed=n); ballx(img, W / 2 + 300 + 600 * (kk - 0.5), 1790)
    text(img, "DUELS PERDUS", W / 2, 330, 84, WHITE, k - (T("perd") - SC["duels"]), stroke=8)
    for i in range(min(5, n + (1 if kk > 0.55 else 0))): xmark(img, 230 + i * 155, 500, 1, 50)

def p_tableau(img, tg, k):
    # le tableau des 40 noms : KAÏ glisse jusqu'en bas, 40/40
    lockers(img); shade(img, 110)
    d = ImageDraw.Draw(img); d.rounded_rectangle((90, 230, W - 90, 1580), 22, fill=(236, 236, 228, 255), outline=(0, 0, 0, 255), width=10)
    d.text((W / 2, 300), "CLASSEMENT", font=F(58), fill=(20, 20, 30), anchor="mm")
    rng = np.random.default_rng(12)
    for i in range(39):
        y = 380 + i * 29; d.text((140, y), f"{i + 1:>2}.", font=F(24), fill=(70, 70, 80), anchor="lm")
        d.line((200, y, 200 + rng.uniform(220, 560), y), fill=(110, 110, 125), width=9)
    u = ease((k - (T("tombe") - SC["tableau"])) / 0.9) if k > T("tombe") - SC["tableau"] else 0
    y = lerp(380, 380 + 39 * 29 + 6, u)
    d.rounded_rectangle((120, y - 26, W - 120, y + 26), 10, fill=(255, 220, 200, 255), outline=RED + (255,), width=5)
    d.text((140, y), "40." if u > 0.98 else "1.", font=F(30), fill=RED, anchor="lm"); d.text((210, y), "KAÏ", font=F(40), fill=RED, anchor="lm")
    stamp(img, "40 / 40", W / 2, 950, k - (t_q40 - SC["tableau"]), 150, RED, -8)

def p_vestiaire(img, tg, k):
    lockers(img)
    put(img, "k_poings", W / 2, 1780, 760, dark=0.2)
    for i, (x, fl) in enumerate(((190, True), (W - 190, False))):
        silhouette(img, "z_pointe", x + 10 * math.sin(tg * 9 + i), 1960, 1450, flip=fl)
        text(img, "HA HA !", [230, 850][i], 520 + 18 * math.sin(tg * 9 + i), 80, WHITE, k - 0.1 - 0.2 * i, stroke=7, rot=[-10, 10][i])
    stamp(img, "RENTRE AU VILLAGE", W / 2, 330, k - (t_rentre - SC["vestiaire"]), 70)

def p_nuit(img, tg, k):
    alley(img, tg, ease(k / 0.4)); put(img, "k_poings", 760, 1720, 700 * (1 + 0.05 * k))
    tag(img, "LA MÊME NUIT", k - 0.1)
    text(img, "IL NE DORT PAS.", W / 2, 380, 92, WHITE, k - (T("dort") - SC["nuit"]), stroke=8)

def p_drill(img, tg, k):
    """sous le lampadaire : contrôle / demi-tour / accélération / encore ×3"""
    alley(img, tg, 1.0, lx=640)
    kc, kd, ka, ke = (x - SC["drill"] for x in (t_ctrl, t_demi, t_acc, t_enc))
    if k < kc:
        put(img, "k_poings", 640, 1720, 760); text(img, "SOUS LE LAMPADAIRE", W / 2, 380, 72, OR, k - 0.05, stroke=7)
    elif k < kd:
        kk = k - kc; put(img, "k_volee", 640, 1740, 900); ballx(img, 640 + 60, lerp(900, 1640, eout(kk / 0.6)))
        text(img, "CONTRÔLE.", W / 2, 380, 110, WHITE, kk, stroke=9)
    elif k < ka:
        kk = k - kd; fl = kk > 0.35; put(img, "k_dribble", 640 + (40 if fl else -40), 1740, 960, flip=fl)
        if 0.25 < kk < 0.55: speed_radial(img, tg, 0.6, 640, 1350)
        text(img, "DEMI-TOUR.", W / 2, 380, 110, WHITE, kk, stroke=9)
    elif k < ke:
        kk = k - ka; u = eout(kk / 0.7); put(img, "k_court_face", 640, lerp(1650, 2150, u), lerp(800, 1700, u)); speed_radial(img, tg, 0.8)
        text(img, "ACCÉLÉRATION.", W / 2, 380, 104, OR, kk, stroke=9)
    else:
        kk = k - ke; ph = (kk * 1.3) % 1
        for g in range(3): put(img, "k_dribble", lerp(-200, W + 200, (ph - g * 0.06) % 1), 1740, 960, alpha=1 - 0.3 * g)
        speed_h(img, tg, 0.7, 1250, 1700)
        n = 1 + sum(1 for w in WORDS if norm(w["text"]) == "encore" and w["start"] <= tg)
        text(img, "ENCORE." * 1, W / 2, 380, 120, YEL, kk, stroke=10)
        text(img, f"× {min(3, n - 1)}", W / 2, 520, 100, WHITE, 1, stroke=8, pop=False)

def p_jours(img, tg, k):
    # jour 10 : il gagne son 1er duel ; jour 20 : intouchable (images fantômes)
    img.paste(cover(BG["soir"], 1.15, 0.5, 0.62)); k20 = t_j20 - SC["jours"]
    cyc = 0.5 + 0.5 * math.sin(k * 10); night(img, 0.2 + 0.5 * cyc * (1 - ease((k - 0.9) / 0.4)))
    day = min(10, int(1 + 9 * ease(k / 0.8))) if k < k20 else min(20, int(10 + 10 * ease((k - k20) / 0.6)))
    text(img, f"JOUR {day}", W / 2, 360, 130, YEL, 1, stroke=9, pop=False)
    if k < k20:
        kw = k - (T("gagne") - SC["jours"]); u = eout(max(0, kw) / 0.5)
        silhouette(img, "z_pointe", W - 250 + 150 * u, 1900 + 60 * u, 1450, flip=True, rot=-25 * u)
        put(img, "k_dribble", lerp(200, W / 2, u), 1840, 1000); ballx(img, lerp(420, W / 2 + 220, u), 1800)
        if kw > 0: text(img, "1er DUEL GAGNÉ", W / 2, 520, 80, WHITE, kw, stroke=8)
    else:
        kk = k - k20; sp = 2.6
        for g in range(4): put(img, "k_dribble", lerp(-200, W + 200, ((kk - g * 0.04) * sp) % 1), 1840, 1000, alpha=1 - 0.22 * g)
        for x in (300, 760): silhouette(img, "z_pointe", x, 1900, 1350, a=0.6)
        speed_h(img, tg, 0.9, 1200, 1750)
        text(img, "INTOUCHABLE.", W / 2, 520, 96, OR, k - (T("personne") - SC["jours"]), stroke=8)

def p_match(img, tg, k):
    stadium(img, tg, k, ease(k / 0.6)); tag(img, "DERNIER MATCH", k - 0.05)
    km = k - (T("reste") - SC["match"]); secs = 120 - int(max(0, km) * 2.2)
    if km > 0: text(img, f"{secs // 60}:{secs % 60:02d}", W / 2, 400, 140, OR, km, stroke=9)
    put(img, "k_dribble", W / 2 - 120, 1880, 820); ballx(img, W / 2 + 60, 1850, 28)

def p_charge(img, tg, k):
    # le plus grand défenseur charge vers la caméra, tout le stade attend la chute
    stadium(img, tg, k + 3); u = ease(k / 2.8)
    silhouette(img, "z_pointe", W / 2 + 200 - 120 * u, lerp(1650, 2350, u), lerp(900, 2300, u), a=0.97)
    put(img, "k_dribble", 230, 1900, 760); ballx(img, 390, 1870, 26)
    text(img, "LE PLUS GRAND", W / 2, 330, 90, WHITE, k - 0.05, stroke=8)
    text(img, "TOUT LE STADE ATTEND…", W / 2, 470, 64, (210, 210, 220), k - (t_tout - SC["charge"]), stroke=6)

def p_cri(img, tg, k):
    stadium(img, tg, k + 6, 1.0, warm=1.0); flash(img, k, 0.3)
    for i, n in enumerate(("k_volee", "k_dribble", "k_court_face")):   # échos des nuits sous le lampadaire
        put(img, n, [200, W - 200, W / 2][i], 1500 + 40 * i, 700, alpha=max(0, 0.5 - k * 0.3), dark=0.3)
    u = eout(k / 0.5); put(img, "k_elan", W / 2, lerp(2100, 1840, u), lerp(1300, 1650, u), glow=(255, 160, 50))
    speed_radial(img, tg, max(0, 1 - k / 2))
    text(img, "PAS CETTE", W / 2, 260, 130, WHITE, k, stroke=10)
    text(img, "FOIS !", W / 2, 420, 170, OR, k - 0.12, stroke=11)

def p_crochet(img, tg, k):
    stadium(img, tg, k + 8, 1.0, warm=0.4); kg = T("glisse") - SC["crochet"]; ks = t_kai3 - SC["crochet"]
    if k < ks:
        u = eout(max(0, k - kg + 0.5) / 0.8)
        silhouette(img, "z_pointe", W / 2 + 150 + 250 * u, 1900 + 40 * u, 1500, rot=-70 * u)
        if k > kg - 0.3: dust(img, tg, W / 2 + 250, 1880, k - kg + 0.3, 40, seed=4)
        put(img, "k_dribble", W / 2 - 150 + 60 * math.sin(k * 6), 1880, 1050, flip=k > 0.4); ballx(img, W / 2 + 60, 1850)
        text(img, "CROCHET !", W / 2, 360, 120, YEL, k - 0.1, stroke=9)
        text(img, "IL GLISSE.", W / 2, 520, 84, WHITE, k - kg, stroke=8)
    else:
        kk = k - ks; put(img, "k_court_face", W / 2, lerp(1700, 2150, eout(kk / 1.2)), lerp(900, 1700, eout(kk / 1.2)))
        speed_radial(img, tg, 0.8); text(img, "SEUL.", W / 2, 400, 140, WHITE, kk, stroke=10)

def p_goal(img, tg, k):
    stadium(img, tg, k + 10, 1.0, warm=0.7); kb = t_but - SC["goal"]
    put(img, "k_tir", W / 2, 1900, 1500 + 60 * eout(k / 0.4)); speed_radial(img, tg, 0.6, W * 0.7, H * 0.75)
    if k > kb: flash(img, k - kb, 0.3); confetti(img, tg, k - kb)
    text(img, "BUT !", W / 2, 420, 240, OR, k - kb, stroke=12)

def p_liste(img, tg, k):
    bg = cover(BG["tournoi"], 1.35, 0.3, 0.75).filter(ImageFilter.GaussianBlur(6)); img.paste(bg); night(img, 0.7)
    put(img, "b_coach", lerp(-200, 330, eout(k / 0.7)), 1950, 1450)
    kp = k - (T("liste") - SC["liste"])
    if kp > 0:
        u = back(min(1, kp / 0.5)); pw, ph = int(560 * u), int(700 * u)
        if pw > 10:
            P = Image.new("RGBA", (560, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
            d.rounded_rectangle((0, 0, 559, 699), 16, fill=(245, 242, 230, 255), outline=(0, 0, 0, 255), width=8)
            d.text((280, 80), "LES 3 CHOISIS", font=F(46), fill=(20, 20, 30), anchor="mm")
            for i in range(3):
                y = 220 + i * 160; d.text((50, y), f"{i + 1}.", font=F(60), fill=OR if i == 0 else (60, 60, 70), anchor="lm")
                if i == 0 and k > t_lit - SC["liste"]:
                    n = int((tg * 12) % 3) + 1; d.text((140, y), "?" * n, font=F(70), fill=RED, anchor="lm")
                else: d.rectangle((140, y - 30, 480, y + 30), fill=(30, 30, 40, 255))
            P = P.resize((pw, ph)).rotate(-4, expand=True, resample=Image.BICUBIC)
            img.alpha_composite(P, (int(W - 330 - P.width / 2), int(900 - P.height / 2)))
    text(img, "IL LIT LE PREMIER…", W / 2, 330, 80, WHITE, k - (t_lit - SC["liste"]), stroke=8)

def p_abonne(img, tg, k):
    alley(img, tg, 1.0, lx=640); shade(img, 120)
    put(img, "k_poings", 640, 1900, 1000, glow=(255, 140, 40))
    sc = back(k / 0.35) + 0.03 * math.sin(tg * 8)
    L = Image.new("RGBA", (720, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, 719, 189), 50, fill=RED + (255,)); d.text((360, 95), "+  ABONNE-TOI", font=F(84), fill=WHITE, anchor="mm")
    L = L.resize((max(4, int(720 * sc)), max(4, int(190 * sc)))); img.alpha_composite(L, (int(W / 2 - L.width / 2), int(300 - L.height / 2)))
    text(img, "KAÏ · ÉPISODE 3", W / 2, 500, 64, OR, k - (T("suite") - SC["abonne"]), stroke=6)
    text(img, "DIMANCHE PROCHAIN", W / 2, 600, 58, WHITE, k - (T("dimanche") - SC["abonne"]), stroke=6)
    kd = k - (t_dem - SC["abonne"])
    if kd > 0:
        L2 = Image.new("RGBA", (920, 150), (0, 0, 0, 0)); d2 = ImageDraw.Draw(L2)
        d2.rounded_rectangle((0, 0, 919, 149), 34, fill=(10, 12, 20, 220), outline=OR + (255,), width=6)
        d2.text((460, 48), "DEMAIN", font=F(46), fill=OR + (255,), anchor="mm")
        d2.text((460, 106), "ILS ONT FAILLI ABANDONNER · ÉP. 16", font=F(44), fill=WHITE + (255,), anchor="mm")
        a2 = ease(kd / 0.25); L2.putalpha(Image.eval(L2.getchannel("A"), lambda v: int(v * a2)))
        img.alpha_composite(L2, (int(W / 2 - 460), 665))

def p_question(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), NAVY + (255,)))
    v = 1 + int(tg * 2.2) % 10; ring(img, W / 2, 1000, 260, v / 10); text(img, f"{v}/10", W / 2, 1000, 150, WHITE, 1, pop=False)
    text(img, "ET TOI ?", W / 2, 240, 90, OR, k, stroke=8)
    text(img, "SUR 10, TON MENTAL", W / 2, 370, 78, WHITE, k - (t_sur - SC["question"]), stroke=6)
    text(img, "QUAND TU ES", W / 2, 480, 60, WHITE, k - (Ta("quand", t_sur) - SC["question"]), stroke=6)
    text(img, "LE DERNIER DE LA LISTE ?", W / 2, 590, 84, OR, k - (Ta("dernier", t_sur) - SC["question"]), stroke=8)
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

# ------------------------------------------------------------------ v2 (22/11) : 7 illustrations IA (FLUX) — nouveau look de Kaï (tresses, bandeau orange)
IA = {n: Image.open(f"ia/{n}.png").convert("RGB") for n in ("01_ville", "02_vestiaire", "03_portrait", "04_duel", "05_ruelle", "06_tir", "07_coach")}

def kb(img, name, k, dur, z0=1.0, z1=1.12, fx0=0.5, fy0=0.5, fx1=0.5, fy1=0.5, flip=False):
    u = ease(min(1, max(0, k / max(0.1, dur))))
    src = IA[name].transpose(Image.FLIP_LEFT_RIGHT) if flip else IA[name]
    img.paste(cover(src, lerp(z0, z1, u), lerp(fx0, fx1, u), lerp(fy0, fy1, u)))

def dur(n):
    i = [x for x, _ in S].index(n); return (S[i + 1][1] if i + 1 < len(S) else END) - S[i][1]

def p_cold(img, tg, k):
    kb(img, "03_portrait", k, dur("cold"), 1.35, 1.05, 0.5, 0.35, 0.5, 0.42)
    shade(img, 40); stamp(img, "TROP PETIT ?", W / 2, 1150, k - 0.05, 120)
    text(img, "POUR L'ACADÉMIE", W / 2, 1330, 70, WHITE, k - 0.35, stroke=7)
    series_band(img, tg)

def p_titre(img, tg, k):
    img.paste(Image.new("RGBA", (W, H), NAVY + (255,)))
    bg = cover(IA["01_ville"], 1.1 + 0.03 * k, 0.5, 0.45); bg.putalpha(90); img.alpha_composite(bg)
    text(img, "MINDSET 24 PRÉSENTE", W / 2, 520, 50, (240, 190, 70), k - 0.05, stroke=5, pop=False)
    text(img, "KAÏ", W / 2, 840, 320, OR, k - (T("kaï") - SC["titre"]), stroke=12)
    text(img, "ÉPISODE 2", W / 2, 1070, 96, WHITE, k - (T("épisode") - SC["titre"]), stroke=7)
    text(img, "L'ACADÉMIE", W / 2, 1200, 60, (220, 220, 230), k - (T("épisode") - SC["titre"]) - 0.3, stroke=5, pop=False)

def p_capitale(img, tg, k):
    kb(img, "01_ville", k, dur("capitale"), 1.0, 1.25, 0.5, 0.35, 0.5, 0.75)
    tint(img, (255, 140, 40), 30); tag(img, "LA CAPITALE · L'ACADÉMIE", k - 0.1)
    k40 = k - (t_40 - SC["capitale"])
    if k40 > 0:
        n = min(40, int(1 + 39 * ease(k40 / 0.7))); text(img, f"{n} JOUEURS", W / 2, 420, 110, WHITE, k40, stroke=9, pop=False)
    text(img, "3 PLACES", W / 2, 560, 120, OR, k - (T("trois") - SC["capitale"]), stroke=10)

def p_toise(img, tg, k):
    kb(img, "02_vestiaire", k, dur("toise"), 1.25, 1.1, 0.5, 0.3, 0.5, 0.55)
    stamp(img, "LE PLUS PETIT", W / 2, 330, k - (T("plus") - SC["toise"]), 100)

def p_duels(img, tg, k):
    cyc = 1.15; n = int(k / cyc); kk = k % cyc
    sh = 30 * math.exp(-kk * 6) if kk > 0.5 else 0
    kb(img, "04_duel", k, dur("duels"), 1.15 + 0.06 * (kk > 0.5), 1.25, 0.5, 0.5, 0.45, 0.55)
    tint(img, (200, 30, 30), 40 + 60 * (kk > 0.5))
    text(img, "DUELS PERDUS", W / 2, 330, 84, WHITE, k - (T("perd") - SC["duels"]), stroke=8)
    for i in range(min(5, n + (1 if kk > 0.55 else 0))): xmark(img, 230 + i * 155, 500, 1, 50)

def p_vestiaire(img, tg, k):
    kb(img, "02_vestiaire", k, dur("vestiaire"), 1.05, 1.2, 0.5, 0.6, 0.5, 0.45)
    for i, x in enumerate((230, 850)):
        text(img, "HA HA !", x, 470 + 18 * math.sin(tg * 9 + i), 80, OR, k - 0.1 - 0.2 * i, stroke=7, rot=[-10, 10][i])
    stamp(img, "RENTRE AU VILLAGE", W / 2, 300, k - (t_rentre - SC["vestiaire"]), 70)

def p_nuit(img, tg, k):
    kb(img, "05_ruelle", k, dur("nuit"), 1.3, 1.1, 0.5, 0.2, 0.5, 0.4)
    tag(img, "LA MÊME NUIT", k - 0.1)
    text(img, "IL NE DORT PAS.", W / 2, 560, 92, WHITE, k - (T("dort") - SC["nuit"]), stroke=8)

def p_drill(img, tg, k):
    kc, kd, ka, ke = (x - SC["drill"] for x in (t_ctrl, t_demi, t_acc, t_enc))
    if k < kc:
        kb(img, "05_ruelle", k, kc, 1.1, 1.2, 0.5, 0.4, 0.5, 0.5); text(img, "SOUS LE LAMPADAIRE", W / 2, 380, 72, OR, k - 0.05, stroke=7)
    elif k < kd:
        kk = k - kc; kb(img, "05_ruelle", kk, kd - kc, 1.6, 1.75, 0.35, 0.85, 0.35, 0.85)
        text(img, "CONTRÔLE.", W / 2, 380, 110, WHITE, kk, stroke=9)
    elif k < ka:
        kk = k - kd; kb(img, "05_ruelle", kk, ka - kd, 1.25, 1.3, 0.5, 0.55, 0.5, 0.55, flip=kk > 0.3)
        if 0.2 < kk < 0.5: speed_radial(img, tg, 0.6)
        text(img, "DEMI-TOUR.", W / 2, 380, 110, WHITE, kk, stroke=9)
    elif k < ke:
        kk = k - ka; kb(img, "05_ruelle", kk, ke - ka, 1.1, 1.6, 0.5, 0.5, 0.5, 0.4); speed_radial(img, tg, 0.8)
        text(img, "ACCÉLÉRATION.", W / 2, 380, 104, OR, kk, stroke=9)
    else:
        kk = k - ke; ph = (kk * 1.3) % 1
        kb(img, "05_ruelle", ph, 1, 1.15, 1.35, 0.5, 0.5, 0.5, 0.45, flip=int(kk * 1.3) % 2 == 1); speed_h(img, tg, 0.7, 1250, 1700)
        n = sum(1 for w in WORDS if norm(w["text"]) == "encore" and w["start"] <= tg)
        text(img, "ENCORE.", W / 2, 380, 120, YEL, kk, stroke=10)
        text(img, f"× {min(3, max(1, n))}", W / 2, 520, 100, WHITE, 1, stroke=8, pop=False)

def p_jours(img, tg, k):
    k20 = t_j20 - SC["jours"]
    if k < k20:
        kb(img, "04_duel", k, k20, 1.4, 1.2, 0.6, 0.62, 0.55, 0.6); cyc = 0.5 + 0.5 * math.sin(k * 10)
        night(img, 0.15 + 0.4 * cyc * (1 - ease((k - 0.9) / 0.4)))
        day = min(10, int(1 + 9 * ease(k / 0.8)))
        kw = k - (T("gagne") - SC["jours"])
        if kw > 0: flash(img, kw, 0.2); text(img, "1er DUEL GAGNÉ", W / 2, 520, 80, OR, kw, stroke=8)
    else:
        kk = k - k20; kb(img, "05_ruelle", kk, dur("jours") - k20, 1.2, 1.5, 0.5, 0.5, 0.5, 0.45); tint(img, (255, 160, 60), 50)
        speed_h(img, tg, 0.9, 900, 1750); day = min(20, int(10 + 10 * ease(kk / 0.6)))
        text(img, "INTOUCHABLE.", W / 2, 520, 96, OR, k - (T("personne") - SC["jours"]), stroke=8)
    text(img, f"JOUR {day}", W / 2, 360, 130, YEL, 1, stroke=9, pop=False)

def p_match(img, tg, k):
    kb(img, "04_duel", k, dur("match"), 1.0, 1.08, 0.5, 0.4, 0.5, 0.45); tag(img, "DERNIER MATCH", k - 0.05)
    km = k - (T("reste") - SC["match"]); secs = 120 - int(max(0, km) * 2.2)
    if km > 0: text(img, f"{secs // 60}:{secs % 60:02d}", W / 2, 1450, 140, OR, km, stroke=9)

def p_charge(img, tg, k):
    kb(img, "04_duel", k, dur("charge"), 1.1, 1.55, 0.5, 0.45, 0.45, 0.3)
    text(img, "LE PLUS GRAND", W / 2, 1400, 90, WHITE, k - 0.05, stroke=8)
    text(img, "TOUT LE STADE ATTEND…", W / 2, 1530, 64, (230, 230, 235), k - (t_tout - SC["charge"]), stroke=6)

def p_cri(img, tg, k):
    kb(img, "03_portrait", k, dur("cri"), 1.5, 1.25, 0.5, 0.33, 0.5, 0.33); tint(img, (255, 140, 30), 70)
    flash(img, k, 0.3); speed_radial(img, tg, max(0, 1 - k / 2))
    text(img, "PAS CETTE", W / 2, 1250, 130, WHITE, k, stroke=10)
    text(img, "FOIS !", W / 2, 1410, 170, OR, k - 0.12, stroke=11)

def p_crochet(img, tg, k):
    ks = t_kai3 - SC["crochet"]; kg = T("glisse") - SC["crochet"]
    if k < ks:
        kb(img, "04_duel", k, ks, 1.3, 1.6, 0.55, 0.65, 0.65, 0.7); speed_h(img, tg, 0.6, 900, 1700)
        text(img, "CROCHET !", W / 2, 360, 120, YEL, k - 0.1, stroke=9)
        text(img, "IL GLISSE.", W / 2, 520, 84, WHITE, k - kg, stroke=8)
    else:
        kk = k - ks; kb(img, "06_tir", kk, dur("crochet") - ks, 1.4, 1.15, 0.5, 0.35, 0.5, 0.45); speed_radial(img, tg, 0.8)
        text(img, "SEUL.", W / 2, 400, 140, WHITE, kk, stroke=10)

def p_goal(img, tg, k):
    kb(img, "06_tir", k, dur("goal"), 1.1, 1.3, 0.5, 0.6, 0.6, 0.55); kb_ = t_but - SC["goal"]
    if k > kb_: flash(img, k - kb_, 0.3); confetti(img, tg, k - kb_)
    text(img, "BUT !", W / 2, 420, 240, OR, k - kb_, stroke=12)

def p_liste(img, tg, k):
    kb(img, "07_coach", k, dur("liste"), 1.05, 1.3, 0.5, 0.4, 0.4, 0.5)
    kp = k - (t_lit - SC["liste"])
    if kp > 0:
        u = back(min(1, kp / 0.5)); P = Image.new("RGBA", (620, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
        d.rounded_rectangle((0, 0, 619, 519), 16, fill=(245, 242, 230, 245), outline=(0, 0, 0, 255), width=8)
        d.text((310, 70), "LES 3 CHOISIS", font=F(48), fill=(20, 20, 30), anchor="mm")
        for i in range(3):
            y = 190 + i * 115; d.text((50, y), f"{i + 1}.", font=F(60), fill=OR if i == 0 else (60, 60, 70), anchor="lm")
            if i == 0: d.text((150, y), "?" * (int((tg * 12) % 3) + 1), font=F(70), fill=RED, anchor="lm")
            else: d.rectangle((150, y - 30, 560, y + 30), fill=(30, 30, 40, 255))
        P = P.resize((max(4, int(620 * u)), max(4, int(520 * u)))).rotate(-3, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(P, (int(W / 2 - P.width / 2), int(1180 - P.height / 2)))
    text(img, "IL LIT LE PREMIER…", W / 2, 330, 80, WHITE, k - (t_lit - SC["liste"]), stroke=8)

def p_abonne(img, tg, k):
    kb(img, "03_portrait", k, dur("abonne"), 1.05, 1.15, 0.5, 0.45, 0.5, 0.4); shade(img, 110)
    sc = back(k / 0.35) + 0.03 * math.sin(tg * 8)
    L = Image.new("RGBA", (720, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, 719, 189), 50, fill=RED + (255,)); d.text((360, 95), "+  ABONNE-TOI", font=F(84), fill=WHITE, anchor="mm")
    L = L.resize((max(4, int(720 * sc)), max(4, int(190 * sc)))); img.alpha_composite(L, (int(W / 2 - L.width / 2), int(300 - L.height / 2)))
    text(img, "KAÏ · ÉPISODE 3", W / 2, 500, 64, OR, k - (T("suite") - SC["abonne"]), stroke=6)
    text(img, "DIMANCHE PROCHAIN", W / 2, 600, 58, WHITE, k - (T("dimanche") - SC["abonne"]), stroke=6)
    kd = k - (t_dem - SC["abonne"])
    if kd > 0:
        L2 = Image.new("RGBA", (920, 150), (0, 0, 0, 0)); d2 = ImageDraw.Draw(L2)
        d2.rounded_rectangle((0, 0, 919, 149), 34, fill=(10, 12, 20, 220), outline=OR + (255,), width=6)
        d2.text((460, 48), "DEMAIN", font=F(46), fill=OR + (255,), anchor="mm")
        d2.text((460, 106), "ILS ONT FAILLI ABANDONNER · ÉP. 16", font=F(44), fill=WHITE + (255,), anchor="mm")
        a2 = ease(kd / 0.25); L2.putalpha(Image.eval(L2.getchannel("A"), lambda v: int(v * a2)))
        img.alpha_composite(L2, (int(W / 2 - 460), 665))
def ring(img, cx, cy, r, u):
    d = ImageDraw.Draw(img); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(60, 66, 90), width=22)
    d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * u, fill=OR, width=22)

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
        if i > 0 and lt < 0.12 and S[i][0] not in ("cri", "drill", "jours", "goal"):   # coupe franche + petit fondu
            prev = Image.new("RGBA", (W, H), (0, 0, 0, 255)); PLANS[S[i - 1][0]](prev, tg, tg - S[i - 1][1]); img = Image.blend(prev, img, lt / 0.12)
        karaoke(img, tg)
        a = np.asarray(img.convert("RGB")).astype(np.float32)
        # caméra : dérive + secousse sur les temps forts
        sh = 0.0
        for key in ("cri", "chute", "cold", "goal"):
            if key not in SC: continue
            kk = tg - SC[key]
            if 0 <= kk < 1.2: sh = max(sh, 16 * math.exp(-kk * 3))
        for word in ("but", "crochet", "tombe"):
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

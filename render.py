# -*- coding: utf-8 -*-
"""Rendu final v2 : scènes + transitions + sous-titres -> MP4 (sans audio ; le mix est ajouté après)."""
import json, math, subprocess, sys, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from engine import *
from body import Body, draw_body, draw_stars
import scenes as S

FPS = 30
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
_TJ = json.load(open("timing_voix.json"))
def _core(wd): return "".join(ch for ch in wd.lower() if ch.isalpha() or ch in "éèàùêâîôûç")
KEYW = {_core(w) for w in _TJ["keywords"]}
XFADE = 0.35

def sub_img(txt, size=52, stroke=7, maxw=990):
    font = ImageFont.truetype(FONT, size)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    words = txt.split(); lines = [[]]
    for wd in words:
        test = " ".join(lines[-1] + [wd]).upper()
        if d.textlength(test, font=font) > maxw and lines[-1]: lines.append([wd])
        else: lines[-1].append(wd)
    lh = int(size * 1.28)
    im = Image.new("RGBA", (W, lh * len(lines) + stroke * 4), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    sp = d.textlength(" ", font=font)
    for k, ln in enumerate(lines):
        tw = d.textlength(" ".join(ln), font=font); x = (W - tw) / 2; y = stroke * 2 + k * lh
        for wd in ln:
            core = _core(wd)
            kw = core in KEYW
            col = (150, 225, 255) if kw else (255, 255, 255)
            wd2 = wd.upper() if kw else wd
            dr.text((x, y), wd2, font=font, fill=col + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            x += d.textlength(wd2, font=font) + sp
    return np.asarray(im).astype(np.float32) / 255.0

def big_img(txt, size, col=(255, 255, 255), stroke=6):
    font = ImageFont.truetype(FONT, size)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10))); tw = d.textlength(txt, font=font)
    im = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.text(((W - tw) / 2, size * 0.1), txt, font=font, fill=col + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return np.asarray(im).astype(np.float32) / 255.0

def paste(frame, rgba, cy, alpha=1.0, scale=1.0):
    if alpha <= 0: return
    if scale != 1.0:
        rgba = cv2.resize(rgba, (int(rgba.shape[1] * scale), int(rgba.shape[0] * scale)), interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]; y0 = int(cy - h / 2); x0 = int((W - w) / 2)
    ys, ye = max(0, y0), min(H, y0 + h); xs, xe = max(0, x0), min(W, x0 + w)
    if ys >= ye or xs >= xe: return
    sub = rgba[ys - y0:ye - y0, xs - x0:xe - x0]
    a = sub[..., 3:4] * alpha
    frame[ys:ye, xs:xe] = frame[ys:ye, xs:xe] * (1 - a) + sub[..., :3] * a

PUNCH_T = _TJ["punches"]
BIG_T = [_TJ["K"]["boom"], _TJ["K"]["q_end"]]

def punch_amount(tg):
    p = 0.0
    for tk in PUNCH_T + BIG_T:
        d = tg - tk
        if 0 <= d < 0.6:
            p = max(p, math.exp(-d * 7) * (1.6 if tk in BIG_T else 1.0))
    return p

GL_RNG = np.random.default_rng(3)

def punch_fx(img, p, tg):
    if p < 0.02: return img
    z = 1 + 0.045 * min(p, 1.4)
    h2, w2 = int(H / z), int(W / z); y0, x0 = (H - h2) // 2, (W - w2) // 2
    img = cv2.resize(img[y0:y0 + h2, x0:x0 + w2], (W, H), interpolation=cv2.INTER_LINEAR)
    sh = int(4 * min(p, 1.0)) if p > 0.5 else 0
    if sh:
        out = img.copy()
        out[:, sh:, 0] = img[:, :-sh, 0]; out[:, :-sh, 2] = img[:, sh:, 2]
        img = out
    if False:   # tranches glitch désactivées (image propre)
        for _ in range(int(6 * p)):
            y = GL_RNG.integers(0, H - 80); hh = GL_RNG.integers(12, 70); dx = int(GL_RNG.integers(-60, 60) * p)
            img[y:y + hh] = np.roll(img[y:y + hh], dx, axis=1)
    return img

def headline(lines, size=92, stroke=8):
    font = ImageFont.truetype(FONT, size)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lh = int(size * 1.12)
    im = Image.new("RGBA", (W, lh * len(lines) + stroke * 4), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for k, (txt, col) in enumerate(lines):
        tw = d.textlength(txt, font=font)
        dr.text(((W - tw) / 2, stroke * 2 + k * lh), txt, font=font, fill=col + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return np.asarray(im).astype(np.float32) / 255.0

def cta_img():
    font = ImageFont.truetype(FONT, 58)
    txt = _TJ["question"].get("cta", "ÉCRIS-LE EN COMMENTAIRE")
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10))); tw = d.textlength(txt, font=font)
    im = Image.new("RGBA", (W, 230), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.rounded_rectangle(((W - tw) / 2 - 34, 10, (W + tw) / 2 + 34, 104), 26, fill=(235, 245, 255, 255))
    dr.text(((W - tw) / 2, 22), txt, font=font, fill=(0, 0, 0, 255))
    cx = W / 2
    dr.polygon([(cx - 46, 130), (cx + 46, 130), (cx, 205)], fill=(235, 245, 255, 255), outline=(0, 0, 0, 255))
    return np.asarray(im).astype(np.float32) / 255.0

def main(timing, out, t_from=0.0, t_to=None, every=1):
    T = json.load(open(timing))
    sc = T["scenes"]; subs = T["subs"]; total = T["duration"]
    t_to = total if t_to is None else t_to
    simgs = [sub_img(s["text"]) for s in subs]
    slog1 = big_img("Change ton mental.", 70); slog2 = big_img("Change ta vie.", 70)
    Q = _TJ["question"]
    H1 = headline([(l, (255, 255, 255)) for l in Q["lines"]])
    H2 = headline([(Q["highlight"], (150, 225, 255))], 96)
    CTA = cta_img()
    SC9 = sc[-1]["start"]
    comp = Compositor()
    ff = None
    if out.endswith(".mp4"):
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "15",
                               "-pix_fmt", "yuv420p", "-tune", "animation", out], stdin=subprocess.PIPE)
    frames = range(int(t_from * FPS), int(math.ceil(t_to * FPS)), every)
    t0 = time.time()
    for n, fi in enumerate(frames):
        tg = fi / FPS
        layers = {"g": Layer(), "o": Layer()}
        flash = 0.0; fade = 1.0
        for i, s in enumerate(sc):
            a0, a1 = s["start"], s["end"]
            if not (a0 - XFADE / 2 <= tg < a1 + XFADE / 2): continue
            if i == 0: w_in = 1.0
            else: w_in = ease((tg - (a0 - XFADE / 2)) / XFADE)
            w_out = 1.0 if i == len(sc) - 1 else 1 - ease((tg - (a1 - XFADE / 2)) / XFADE)
            wgt = min(w_in, w_out)
            if wgt <= 0.001: continue
            lt = min(1.0, max(0.0, (tg - a0) / (a1 - a0)))
            R = S.SCENES[i](tg, lt)
            for mesh, col, kw in R["meshes"]:
                kw = dict(kw); kw["alpha"] = kw.get("alpha", 1.0) * wgt
                if isinstance(mesh, Body):
                    draw_body(layers[col], mesh, R["cam"], kw["alpha"])
                else:
                    draw_mesh(layers[col], mesh, R["cam"], **kw)
            if "dust" in R:
                cen = R.get("star_c", R["dust"].mean(0))
                draw_stars(layers["g"], cen, R["cam"], tg, 0.9 * wgt, boost=min(1.0, punch_amount(tg)))
            flash = max(flash, R.get("flash", 0.0) * wgt)
            fade = R.get("fade", fade)
        img = comp.compose(layers, persist=0.22, flash=flash)
        # textes
        if S.K["q_line1"] - 0.05 <= tg < sc[-1]["start"]:
            k1 = tg - S.K["q_line1"]
            paste(img, H1, H * 0.13, min(1, k1 / 0.12) * 1.0, 1.0 + 0.12 * math.exp(-k1 * 9))
            if tg >= S.K["q_line2"]:
                k2 = tg - S.K["q_line2"]
                paste(img, H2, H * 0.245, min(1, k2 / 0.1), 1.0 + 0.2 * math.exp(-k2 * 9))
            if tg >= S.K["q_cta"] - 0.25:
                k3 = tg - (S.K["q_cta"] - 0.25)
                bob = 10 * math.sin(tg * 9)
                paste(img, CTA, H * 0.60 + bob, min(1, k3 / 0.12), 1.0 + 0.1 * math.exp(-k3 * 8))
        if tg >= SC9:
            paste(img, slog1, H * 0.60, ease((tg - S.K["slogan1"] + 0.1) / 0.3) * fade,
                  1.0 + 0.04 * (1 - ease((tg - S.K["slogan1"]) / 0.4)))
            paste(img, slog2, H * 0.655, ease((tg - S.K["slogan2"] + 0.1) / 0.3) * fade,
                  1.0 + 0.04 * (1 - ease((tg - S.K["slogan2"]) / 0.4)))
        else:
            for s, im in zip(subs, simgs):
                if S.K["q_line1"] - 0.05 <= s["start"] < S.K["q_cta"] - 0.3: continue
                if s["start"] <= tg < s["end"]:
                    pop = 1.0 + 0.06 * (1 - ease((tg - s["start"]) / 0.12))
                    paste(img, im, H * 0.755, min(1, (tg - s["start"]) / 0.06), pop)
        img = punch_fx(img, punch_amount(tg), tg)
        u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        if ff: ff.stdin.write(u8.tobytes())
        else: cv2.imwrite(f"{out}/f_{fi:04d}.png", cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))
        if n % 60 == 0:
            el = time.time() - t0
            print(f"frame {fi} t={tg:.2f}s  {el:.0f}s écoulées", flush=True)
    if ff: ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 0.0, float(a[4]) if len(a) > 4 else None,
         int(a[5]) if len(a) > 5 else 1)

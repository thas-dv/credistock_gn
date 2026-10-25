# -*- coding: utf-8 -*-
"""Bande son procédurale (nappe sombre, battements, whoosh, impacts, montée, boom) + mixage voix."""
import json, subprocess, sys
import numpy as np
from scipy import signal

SR = 44100
T = json.load(open("timing_voix.json"))
DUR = T["duration"]
N = int(DUR * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(5)
K = T["K"]
SC = {x["type"]: x["start"] for x in T["scenes"]}

def lp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "low"); return signal.lfilter(b, a, x)

def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high"); return signal.lfilter(b, a, x)

def bp(x, f1, f2):
    b, a = signal.butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band"); return signal.lfilter(b, a, x)

def env_ar(start, att, rel, n=N):
    e = np.zeros(n); i0 = int(start * SR)
    a = int(att * SR); r = int(rel * SR)
    seg = np.concatenate([np.linspace(0, 1, max(1, a)), np.exp(-np.linspace(0, 6, max(1, r)))])
    i1 = min(n, i0 + len(seg));
    if i0 < n: e[i0:i1] = seg[:i1 - i0]
    return e

def saw(f, ph=0.0):
    return 2 * ((f * t + ph) % 1.0) - 1

def pad(freqs, gain):
    x = np.zeros(N)
    for f in freqs:
        for d in (-0.12, 0.0, 0.13):
            x += saw(f * (1 + d / 100), rng.random())
    return x * gain

def smooth_step(a, b):
    return np.clip((t - a) / max(1e-3, b - a), 0, 1) ** 2 * (3 - 2 * np.clip((t - a) / max(1e-3, b - a), 0, 1))

music = np.zeros(N)
# ----- nappe : La mineur sombre puis ouverture lumineuse au « matin »
dark = pad([55.0, 82.41, 110.0, 130.81], 0.05)
dark = lp(dark, 520, 2) * (0.35 + 0.65 * smooth_step(0, 3)) * (1 - smooth_step(K['boom'] - 0.25, K['boom']))
tension = pad([58.27, 87.31, 116.54], 0.04)   # Sib : tension pendant la prison
tension = lp(tension, 700) * smooth_step(SC['build'] - 0.5, SC['build'] + 1.5) * (1 - smooth_step(K['boom'] - 0.25, K['boom']))
dark *= (1 - 0.6 * smooth_step(SC['build'] - 0.5, SC['build'] + 1.5))
light = pad([87.31, 130.81, 174.61, 220.0, 261.63], 0.035)        # Fa majeur
light2 = pad([65.41, 130.81, 196.0, 261.63, 329.63], 0.035)      # Do majeur
lift = lp(light, 1400) * smooth_step(K['boom'] + 0.3, K['boom'] + 1.7) * (1 - smooth_step(K["sunrise"] - 0.3, K["sunrise"] + 0.6))
lift += lp(light2, 2200) * smooth_step(K["sunrise"] - 0.3, K["sunrise"] + 1.5) * (1 - smooth_step(DUR - 1.1, DUR))
music += dark + tension + lift
# scintillement aigu au lever du soleil
shim = (np.sin(2 * np.pi * 1046.5 * t) + 0.6 * np.sin(2 * np.pi * 1318.5 * t + 1) + 0.4 * np.sin(2 * np.pi * 1568 * t + 2))
shim *= (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * t)) * 0.012 * smooth_step(K["sunrise"], K["sunrise"] + 2.5) * (1 - smooth_step(DUR - 1.4, DUR))
music += shim

# ----- battement de cœur (sub) jusqu'à la prison
def thump(at, f0=52, gain=0.5, dec=7):
    e = env_ar(at, 0.004, 0.45)
    ph = 2 * np.pi * np.cumsum(f0 * (1 + 1.5 * np.exp(-(t - at).clip(0) * 25))) / SR
    return np.sin(ph) * e * gain
hb = np.zeros(N)
x = 0.4
while x < K['boom'] - 0.5:
    period = 1.0 if x < SC['build'] else max(0.36, 1.0 - (x - SC['build']) * 0.12)
    hb += thump(x, 50, 0.32) + thump(x + 0.2, 48, 0.2)
    x += period
music += hb

# ----- whoosh à chaque changement de scène
noise = rng.normal(0, 1, N)
def whoosh(at, length=0.7, gain=0.18):
    e = np.exp(-((t - at) / (length / 3)) ** 2)
    x = bp(noise, 300, 4000) * e
    return x * gain
for s in T["scenes"][1:]:
    music += whoosh(s["start"])

# ----- impacts (mots qui tombent, murs)
def impact(at, gain=0.6, f0=45):
    crack = hp(noise, 1500) * env_ar(at, 0.001, 0.18) * 0.5
    body = lp(noise, 600) * env_ar(at, 0.002, 0.4) * 0.7
    return (thump(at, f0, 1.0) + crack + body) * gain
for _w, tk in T["words3d"]:
    music += impact(tk, 0.55)
for k in ("gate1", "gate2"):
    music += impact(K[k], 0.5)

# ----- clics de briques pendant la construction
x = K['build_start'] - 0.9
while x < K['build_end'] + 1.2:
    music += hp(noise, 2500) * env_ar(x, 0.0005, 0.03) * 0.25
    x += rng.uniform(0.07, 0.16)

# ----- montée avant « démolir » puis boom
r0, r1 = SC['explode'], K["boom"]
rise = smooth_step(r0, r1) ** 2 * (t < r1)
sweep_f = 200 + 1800 * np.clip((t - r0) / (r1 - r0), 0, 1) ** 2
riser = np.sin(2 * np.pi * np.cumsum(sweep_f) / SR) * 0.05 + bp(noise, 800, 6000) * 0.09
music += riser * rise
boom = (thump(K["boom"], 38, 1.6) + lp(noise, 300) * env_ar(K["boom"], 0.003, 1.8) * 1.2
        + bp(noise, 200, 3000) * env_ar(K["boom"], 0.002, 0.8) * 0.6)
music += boom
# coup final au logo
music += thump(K["brand"], 42, 1.0) + lp(noise, 2000) * env_ar(K["brand"], 0.003, 0.9) * 0.25

# ----- AGRESSIF : impacts sur chaque mot clé, pulsation 128 bpm, tic-tac de pression, coupure à « abandonné »
for tk in T["punches"]:
    if any(abs(tk - x) < 0.2 for x in [K["boom"], K["q_end"], K["brand"]] + [w[1] for w in T["words3d"]]): continue
    music += impact(tk, 0.32, 55)
beat = 60 / 128
x = K["boom"] + 1.0
while x < SC['question'] - 0.1:
    music += thump(x, 55, 0.55) + hp(noise, 6000) * env_ar(x + beat / 2, 0.001, 0.05) * 0.12
    x += beat
x = SC['question']; per = 0.5
while x < K["q_end"]:
    music += bp(noise, 2500, 7000) * env_ar(x, 0.0005, 0.035) * 0.35 + thump(x, 60, 0.18)
    per = max(0.16, per * 0.94); x += per
music *= (1 - 0.85 * (smooth_step(K["q_end"], K["q_end"] + 0.15) * (1 - smooth_step(SC['logo'] - 0.2, SC['logo'] + 0.05))))
music += impact(K["q_end"], 0.6, 40)
# saturation des basses
low = lp(music, 160); music = music - low + np.tanh(low * 2.5) / 2.5 * 1.3

# ----- réverbération simple
ir_n = int(2.2 * SR)
ir = rng.normal(0, 1, ir_n) * np.exp(-np.linspace(0, 7, ir_n)); ir = lp(ir, 3500); ir /= np.abs(ir).sum() / 30
wet = signal.fftconvolve(music, ir)[:N] * 0.25
music = music + wet

# ----- voix + ducking
voice = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", "voix.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32).astype(float)
v = np.zeros(N); v[:min(N, len(voice))] = voice[:N]
venv = lp(np.abs(v), 6, 1); venv = venv / (venv.max() + 1e-9)
duck = 1 - 0.55 * np.clip(venv * 3, 0, 1)
music = music * duck
music /= (np.abs(music).max() + 1e-9)
mix = v / (np.abs(v).max() + 1e-9) * 0.92 + music * 0.42
# stéréo : léger élargissement de la musique
L = mix + 0.06 * np.roll(music, 220); R = mix - 0.06 * np.roll(music, 220)
st = np.stack([L, R], 1); st /= max(1.0, np.abs(st).max() / 0.97)
out = sys.argv[1] if len(sys.argv) > 1 else "mix.wav"
from scipy.io import wavfile
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print("ok", out, st.shape[0] / SR)

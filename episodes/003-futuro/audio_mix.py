"""Trilha tensa + efeitos + narração do POV 'dez segundos no futuro'."""
import json
import numpy as np
import soundfile as sf

SR = 48000
TL = json.load(open("timeline.json"))
total = TL["total"]
OFF = TL.get("offset", 0.3)
n = int(SR * (total + 0.2))
t = np.arange(n) / SR
rng = np.random.default_rng(21)


def put(buf, sig, at, g=1.0):
    i = int(at * SR); j = min(n, i + len(sig))
    if j > i and i >= 0:
        buf[i:j] += sig[: j - i] * g


def tone(f, d, decay=4.0, h=(1, 0.35, 0.12)):
    k = np.arange(int(SR * d)) / SR
    s = sum(a * np.sin(2 * np.pi * f * (m + 1) * k) for m, a in enumerate(h))
    return s * np.exp(-k * decay)


shots = []
for p in TL["phrases"]:
    if not shots or shots[-1][0] != p["shot"]:
        shots.append((p["shot"], p["start"]))
S = dict(shots)
first = {}
for p in TL["phrases"]:
    first.setdefault(p["shot"], []).append(p["start"])

# ---------------------------------------------------------------- trilha
mus = np.zeros(n)
bpm = 96; beat = 60 / bpm
virada = S.get("virada", total)
roots = [110.0, 98.0, 87.3, 98.0]          # lá, sol, fá, sol: tenso mas leve
b, tt = 0, 0.0
while tt < total - 0.8:
    root = roots[(b // 8) % 4]
    calm = tt < virada
    put(mus, tone(root / 2, 0.42, 6), tt, 0.55 if b % 2 == 0 else 0.0)
    put(mus, tone(root * 2, 0.22, 10, (1, 0.2)), tt + beat / 2, 0.16)
    if b % 4 == 2:
        put(mus, rng.normal(0, 1, int(SR * 0.05)) * np.exp(-np.arange(int(SR * 0.05)) / SR * 70), tt, 0.10)
    if not calm and b % 2 == 1:          # depois da virada entra um pulso mais alto
        put(mus, tone(root * 3, 0.3, 7, (1, 0.5)), tt, 0.12)
    b += 1; tt += beat
mus *= np.clip((total - t) / 1.5, 0, 1)

# ---------------------------------------------------------------- efeitos
sfx = np.zeros(n)


def whoosh(at, d=0.45, g=0.2):
    w = np.convolve(rng.normal(0, 1, int(SR * d)), np.ones(40) / 40, "same")
    k = np.linspace(0, 1, len(w))
    put(sfx, w * np.sin(np.pi * k) ** 2, at, g)


def glitch(at, g=0.25):
    for i in range(6):
        d = 0.04
        put(sfx, np.sign(np.sin(2 * np.pi * rng.uniform(200, 900) * np.arange(int(SR * d)) / SR)) * 0.5, at + i * 0.05, g)


def clink(at, g=0.35):
    put(sfx, tone(2600, 0.5, 9, (1, 0.6, 0.3)), at, g); put(sfx, tone(3900, 0.4, 12), at, g * 0.8)


def carpass(at, g=0.45):
    d = 1.4; k = np.arange(int(SR * d)) / SR
    f = 140 * (1.25 - 0.5 * (k / d))
    eng = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + np.convolve(rng.normal(0, 1, len(k)), np.ones(60) / 60, "same")
    put(sfx, eng * np.sin(np.pi * k / d) ** 2, at, g)


def buzz(at, g=0.3):
    for i in range(2):
        k = np.arange(int(SR * 0.28)) / SR
        put(sfx, np.sin(2 * np.pi * 180 * k) * np.sign(np.sin(2 * np.pi * 30 * k)), at + i * 0.38, g)


def rewind(at, d=1.2, g=0.3):
    k = np.arange(int(SR * d)) / SR
    f = 900 * np.exp(-k * 2.2) + 120
    put(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - k / d), at, g)


def sting(at, g=0.35):
    put(sfx, tone(55, 1.8, 1.4, (1, 0.5, 0.3)), at, g)


for ch in TL.get("chapters", []):
    whoosh(ch["start"] - 0.05, 0.5, 0.22)
    glitch(ch["start"] + 0.1, 0.12)

if "cafe" in first and len(first["cafe"]) > 1:
    clink(first["cafe"][1] + 0.4)
if "rua" in first and len(first["rua"]) > 1:
    carpass(first["rua"][1] + 0.3)
if "celular" in first:
    buzz(first["celular"][0])
if "virada" in first:
    rewind(first["virada"][0] - 0.1)
    if len(first["virada"]) > 2:
        sting(first["virada"][2])
if "fecho" in first:
    sting(first["fecho"][-1], 0.25)

# ---------------------------------------------------------------- narração
nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1:
    nar = nar.mean(1)
if sr != SR:
    nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
nb = np.zeros(n); put(nb, nar, OFF, 1.0)

envv = np.convolve(np.abs(nb), np.ones(4800) / 4800, "same")
duck = 1 - 0.6 * np.clip(envv / 0.05, 0, 1)
mix = nb + mus * 0.16 * duck + sfx * 0.55 * (0.45 + 0.55 * duck)
mix /= np.abs(mix).max() / 0.95
sf.write("audio/mix.wav", mix, SR)
print("mix ok", round(total, 2), "s")

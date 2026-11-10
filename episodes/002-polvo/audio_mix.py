"""Trilha leve + efeitos + narração do episódio do polvo."""
import json, numpy as np, soundfile as sf

SR = 48000
TL = json.load(open("timeline.json"))
total = TL["total"]
OFF = TL.get("offset", 0.3)
n = int(SR * (total + 0.2))
rng = np.random.default_rng(11)
t = np.arange(n) / SR


def put(buf, sig, at, g=1.0):
    i = int(at * SR)
    j = min(n, i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * g


def env(dur, a=0.01, r=0.3):
    k = np.arange(int(SR * dur)) / SR
    return np.minimum(1, k / a) * np.exp(-k / r)


def pluck(f, dur=0.9, decay=5):
    k = np.arange(int(SR * dur)) / SR
    return (np.sin(2*np.pi*f*k) + 0.4*np.sin(4*np.pi*f*k) + 0.15*np.sin(6*np.pi*f*k)) * np.exp(-k*decay)


# ---------------------------------------------------------------- trilha
mus = np.zeros(n)
beat = 0.5
prog = [(196, [392, 466, 587]), (174.6, [349, 440, 523]),
        (164.8, [330, 415, 494]), (174.6, [349, 440, 523])]
b, tt = 0, 0.0
while tt < total - 1.0:
    root, ch = prog[(b // 8) % 4]
    if b % 2 == 0:
        put(mus, pluck(root / 2, 0.45), tt, 0.5)
    put(mus, pluck(ch[b % 3] * (2 if b % 4 == 3 else 1), 0.5), tt + (0.25 if b % 2 else 0), 0.2)
    if b % 4 == 2:
        put(mus, rng.normal(0, 1, int(SR*0.04)) * env(0.04, 0.001, 0.01), tt, 0.1)
    b += 1
    tt += beat
mus *= np.clip((total - t) / 1.2, 0, 1)

# ---------------------------------------------------------------- efeitos
sfx = np.zeros(n)


def whoosh(at, d=0.35, g=0.16):
    w = rng.normal(0, 1, int(SR*d))
    w = np.convolve(w, np.ones(30)/30, "same")
    k = np.arange(len(w))/len(w)
    put(sfx, w * np.sin(np.pi*k)**2, at - d*0.6, g)


def bubbles(at, cnt=10, g=0.22):
    for i in range(cnt):
        d = 0.08
        k = np.arange(int(SR*d))/SR
        f = rng.uniform(500, 1400)*(1+k*12)
        put(sfx, np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*40), at + i*rng.uniform(0.03, 0.09), g)


def heartbeat(at, beats=6, bpm=66, g=0.5):
    """dois toques por batida, grave, pros três corações"""
    per = 60.0 / bpm
    for i in range(beats):
        for off, amp in ((0.0, 1.0), (0.26, 0.62)):
            d = 0.42
            k = np.arange(int(SR*d))/SR
            f = 62 - 26*k
            sig = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-k*9)
            put(sfx, sig, at + i*per + off, g*amp)


def squelch(at, g=0.45):
    """passagem pelo buraco: ar saindo de um corpo mole"""
    d = 0.55
    k = np.arange(int(SR*d))/SR
    nz = np.convolve(rng.normal(0, 1, len(k)), np.ones(40)/40, "same")
    f = 320 - 180*(k/d)
    tone = np.sin(2*np.pi*np.cumsum(f)/SR)
    put(sfx, (tone*0.6 + nz*0.5) * np.exp(-k*4.5), at, g)


def metal(at, g=0.3):
    """eco metálico do cano"""
    for i, dl in enumerate((0, 0.14, 0.31, 0.55)):
        d = 0.5
        k = np.arange(int(SR*d))/SR
        sig = (np.sin(2*np.pi*430*k) + 0.5*np.sin(2*np.pi*611*k)) * np.exp(-k*7)
        put(sfx, sig, at + dl, g * (0.65 ** i))


def sparkle(at, g=0.16):
    for i, f in enumerate([1318, 1568, 1976, 2637]):
        put(sfx, pluck(f, 0.6), at + i*0.07, g)


def lowtone(at, g=0.4):
    d = 2.2
    k = np.arange(int(SR*d))/SR
    sig = (np.sin(2*np.pi*98*k) + 0.4*np.sin(2*np.pi*146.8*k)) * np.minimum(1, k/0.3) * np.exp(-k*0.9)
    put(sfx, sig, at, g)


shots = []
for p in TL["phrases"]:
    if not shots or shots[-1][0] != p["shot"]:
        shots.append((p["shot"], p["start"]))
S = dict(shots)
for name, st in shots[1:]:
    whoosh(st)

bubbles(S["reveal"], 12)
heartbeat(S["coracoes"] + 0.2, beats=9)
bubbles(S["sangue"] + 0.2, 14, 0.18)
sparkle(S["neuronios"] + 0.15, 0.13)
sparkle(S["bracos2"] + 0.1, 0.11)
squelch(S["bico"] + 0.5)
bubbles(S["bico"] + 1.0, 10, 0.2)
metal(S["cano"] + 2.1)
bubbles(S["fuga"] + 0.3, 8, 0.15)
sparkle(S["ovos"] + 0.2, 0.14)
sparkle(S["tempo"] + 0.3, 0.12)
lowtone(S["morte"] + 0.1)
bubbles(total - 2.6, 10, 0.18)

# ---------------------------------------------------------------- narração
nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1:
    nar = nar.mean(1)
if sr != SR:
    nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
nb = np.zeros(n)
put(nb, nar, OFF, 1.0)

# a trilha abaixa sob a voz
envv = np.convolve(np.abs(nb), np.ones(4800)/4800, "same")
duck = 1 - 0.58 * np.clip(envv / 0.05, 0, 1)
mix = nb + mus * 0.15 * duck + sfx * 0.5 * (0.45 + 0.55 * duck)
mix /= np.abs(mix).max() / 0.95
sf.write("audio/mix.wav", mix, SR)
print("mix ok", round(total, 2), "s")

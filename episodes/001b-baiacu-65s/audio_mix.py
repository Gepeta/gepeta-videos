"""Trilha leve + efeitos sonoros + narração."""
import json, numpy as np, soundfile as sf
SR = 48000
TL = json.load(open("timeline.json"))
total = TL["total"]
n = int(SR * (total + 0.2))
rng = np.random.default_rng(3)
t = np.arange(n) / SR

def env(dur, a=0.01, r=0.3):
    k = np.arange(int(SR * dur)) / SR
    return np.minimum(1, k / a) * np.exp(-k / r)

def put(buf, sig, at, g=1.0):
    i = int(at * SR); j = min(n, i + len(sig)); buf[i:j] += sig[: j - i] * g

def pluck(f, dur=0.9):
    k = np.arange(int(SR * dur)) / SR
    return (np.sin(2*np.pi*f*k) + 0.4*np.sin(4*np.pi*f*k) + 0.15*np.sin(6*np.pi*f*k)) * np.exp(-k*5)

mus = np.zeros(n)
# baixo + marimba em loop (120 bpm), clima de curiosidade
beat = 0.5
prog = [(220, [440, 554, 659]), (196, [392, 494, 587]), (174.6, [349, 440, 523]), (196, [392, 494, 587])]
b = 0; tt = 0.0
while tt < total - 1.0:
    root, ch = prog[(b // 8) % 4]
    if b % 2 == 0: put(mus, pluck(root / 2, 0.45), tt, 0.5)
    put(mus, pluck(ch[b % 3] * (2 if b % 4 == 3 else 1), 0.5), tt + (0.25 if b % 2 else 0), 0.22)
    if b % 4 == 2: put(mus, rng.normal(0, 1, int(SR*0.04)) * env(0.04, 0.001, 0.01), tt, 0.12)  # chimbal
    b += 1; tt += beat
mus *= np.clip((total - t) / 1.0, 0, 1)

sfx = np.zeros(n)
def boing(at, f0=180, f1=520, d=0.5, g=0.5):
    k = np.arange(int(SR*d)) / SR; f = f0 + (f1-f0)*(k/d)**0.6
    put(sfx, np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-k*3) * (1+0.3*np.sin(2*np.pi*14*k)), at, g)
def whoosh(at, d=0.35, g=0.18):
    w = rng.normal(0, 1, int(SR*d)); w = np.convolve(w, np.ones(30)/30, 'same')
    k = np.arange(len(w))/len(w); put(sfx, w*np.sin(np.pi*k)**2, at - d*0.6, g)
def bubbles(at, cnt=10, g=0.25):
    for i in range(cnt):
        d = 0.08; k = np.arange(int(SR*d))/SR; f = rng.uniform(500, 1400)*(1+k*12)
        put(sfx, np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*40), at + i*rng.uniform(0.03, 0.09), g)
def boom(at, g=0.7):
    d = 1.2; k = np.arange(int(SR*d))/SR
    put(sfx, (np.sin(2*np.pi*(55-20*k)*k) + 0.3*rng.normal(0, 1, len(k))*np.exp(-k*18)) * np.exp(-k*2.5), at, g)
def sparkle(at, g=0.18):
    for i, f in enumerate([1318, 1568, 1976, 2637]): put(sfx, pluck(f, 0.6), at + i*0.07, g)

shots = []
for p in TL["phrases"]:
    if not shots or shots[-1][0] != p["shot"]: shots.append((p["shot"], p["start"]))
for name, st in shots[1:]: whoosh(st)
S = dict(shots)
boing(1.3, 160, 300, 0.6, 0.35); boing(S["face"] + 2.6, 200, 420, 0.5, 0.4)
put(sfx, rng.normal(0, 1, int(SR*0.5)) * np.linspace(1, 0, int(SR*0.5)) * 0.15, S["reveal"])  # pfff murchando
bubbles(S["reveal"], 14)
boom(S["secret"] + 2.0, 0.6)
boom(S["threat"] - 0.05, 0.4)
boing(S["inflate"] + 0.2, 120, 700, 0.9, 0.6); bubbles(S["inflate"] + 0.1, 18, 0.3)
boing(S["flee"] + 0.1, 600, 200, 0.4, 0.3)
boom(S["poison"] + 0.1, 0.55); boom(S["poison30"] + 0.6, 0.35)
sparkle(S["mandala"] + 0.1); sparkle(S["female"] + 0.1); sparkle(S["eggs"] + 0.2)
boing(total - 2.4, 140, 640, 0.8, 0.55)

# narração (24k -> 48k)
nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1: nar = nar.mean(1)
if sr != SR:
    nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
nb = np.zeros(n); put(nb, nar, TL.get("offset", 0.3), 1.0)
# ducking da trilha sob a voz
envv = np.convolve(np.abs(nb), np.ones(4800)/4800, 'same'); duck = 1 - 0.55*np.clip(envv/0.05, 0, 1)
mix = nb*1.0 + mus*0.16*duck + sfx*0.55
mix /= np.abs(mix).max() / 0.95
sf.write("audio/mix.wav", mix, SR)
print("ok", total)

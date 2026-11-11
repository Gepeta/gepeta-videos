"""Som da intro do Gepeta: ambiente do corredor, luzes acendendo, passos, voz com sala e impacto no título."""
import json, numpy as np, soundfile as sf
SR = 48000; TOTAL = 10.0; n = int(SR * TOTAL); t = np.arange(n) / SR
rng = np.random.default_rng(9)
TL = json.load(open("timeline.json")); OFF = TL.get("offset", 3.35)
words = [w for p in TL["phrases"] for w in p["words"]]
T_END = words[-1][1]; C1 = 3.05; C2 = max(T_END + 0.9, 6.0)

def put(buf, sig, at, g=1.0):
    i = int(at * SR); j = min(n, i + len(sig))
    if j > i and i >= 0: buf[i:j] += sig[: j - i] * g
def lp(x, k): return np.convolve(x, np.ones(k) / k, "same")
def ir(dur=0.9, decay=5.5):
    k = np.arange(int(SR * dur)) / SR; r = rng.normal(0, 1, len(k)) * np.exp(-k * decay); r[0] = 0; return lp(r, 6)
def reverb(x, wet=0.25, dur=0.9, decay=5.5):
    y = np.convolve(x, ir(dur, decay))[: len(x)]; y /= (np.abs(y).max() + 1e-9) / (np.abs(x).max() + 1e-9)
    return x + y * wet

amb = np.zeros(n)
# zumbido do prédio + ar
amb += 0.05 * np.sin(2 * np.pi * 60 * t) + 0.025 * np.sin(2 * np.pi * 120 * t)
amb += lp(rng.normal(0, 1, n), 60) * 0.06
# luzes: estalo do relé + zumbido fluorescente que soma a cada uma acesa
buzz = np.zeros(n)
for i in range(8):
    ton = 0.25 + (7 - i) * 0.17
    d = 0.07; k = np.arange(int(SR * d)) / SR
    clack = (rng.normal(0, 1, len(k)) * 0.6 + np.sin(2 * np.pi * 180 * k)) * np.exp(-k * 60)
    put(amb, clack, ton, 0.55 * (0.5 + 0.5 * i / 7))
    on = np.clip((t - ton) / 0.05, 0, 1)
    buzz += on * (0.5 + 0.5 * i / 7)
buzz *= (np.sin(2 * np.pi * 120 * t) * 0.5 + np.sign(np.sin(2 * np.pi * 240 * t)) * 0.15) * 0.006
amb += buzz
# uma luz pisca no fim
for k0 in np.arange(7.2, 7.45, 0.07): put(amb, rng.normal(0, 1, 1200) * np.exp(-np.arange(1200) / 150), k0, 0.12)

# passos no piso (salto de tênis + rangido de sola), com eco do corredor
steps = np.zeros(n)
st = 0.3
while st < 2.85:
    dist = 1 - (st - 0.3) / 2.6
    d = 0.12; k = np.arange(int(SR * d)) / SR
    hit = (np.sin(2 * np.pi * 95 * k) * 0.8 + rng.normal(0, 1, len(k)) * 0.35) * np.exp(-k * 45)
    put(steps, hit, st, 0.55 * (1 - 0.55 * dist))
    if rng.random() < 0.35:
        sq = np.sin(2 * np.pi * np.cumsum(1800 + 600 * np.sin(k * 40)) / SR) * np.exp(-k * 30) * 0.08
        put(steps, sq, st + 0.03, 0.4)
    st += np.pi / 7.2
steps = reverb(steps, 0.45, 1.2, 4)

# trilha: pad escuro, sobe no fim
mus = np.zeros(n)
for f, g in ((55, 0.5), (82.4, 0.3), (110, 0.22), (164.8, 0.12)):
    mus += g * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.2 * t))
mus *= np.clip(t / 1.5, 0, 1) * 0.08
riser = rng.normal(0, 1, n) * np.clip((t - (C2 - 1.6)) / 1.6, 0, 1) * (t < C2)
mus += lp(riser, 8) * 0.06
# impacto no título + brilho
hitb = np.zeros(n); k = np.arange(int(SR * 2.2)) / SR
boom = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-k * 3) + 38) / SR) * np.exp(-k * 2.2)
put(hitb, boom, C2 + 0.35, 1.0)
put(hitb, rng.normal(0, 1, int(SR * 0.4)) * np.exp(-np.arange(int(SR * 0.4)) / SR * 14), C2 + 0.35, 0.35)
for i, f in enumerate([1046.5, 1318.5, 1568, 2093]):
    kk = np.arange(int(SR * 1.2)) / SR
    put(hitb, np.sin(2 * np.pi * f * kk) * np.exp(-kk * 3.2), C2 + 0.42 + i * 0.07, 0.12)
# acorde que segura até o fim
kk = np.arange(int(SR * (TOTAL - C2))) / SR
chord = sum(np.sin(2 * np.pi * f * kk) for f in (110, 164.8, 220, 277.2, 329.6)) * np.minimum(1, kk / 0.05) * np.exp(-kk * 0.5)
put(hitb, chord, C2 + 0.35, 0.09)
hitb = reverb(hitb, 0.3, 1.6, 2.5)
# whoosh nos cortes
for c in (C1, C2):
    d = 0.45; w = lp(rng.normal(0, 1, int(SR * d)), 25); kk = np.arange(len(w)) / len(w)
    put(hitb, w * np.sin(np.pi * kk) ** 2, c - 0.3, 0.6)

# voz com um pouco de sala
nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1: nar = nar.mean(1)
if sr != SR: nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
vb = np.zeros(n); put(vb, nar, OFF, 1.0); vb = reverb(vb, 0.12, 0.7, 7)
duck = 1 - 0.5 * np.clip(lp(np.abs(vb), 4800) / 0.04, 0, 1)
mix = vb * 1.0 + amb * 0.9 * duck + steps * 0.8 + mus * duck + hitb * 0.55
mix *= np.minimum(1, t / 0.2) * np.clip((TOTAL - t) / 0.35, 0, 1)
mix /= np.abs(mix).max() / 0.95
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR)
print("mix ok")

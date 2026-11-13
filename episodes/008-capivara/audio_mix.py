"""008-capivara: trilha + ambiente + efeitos sincronizados nas palavras + narração."""
import json, numpy as np, soundfile as sf
SR = 48000
TL = json.load(open("timeline.json")); TOTAL = TL["total"]; OFF = TL.get("offset", 0.3)
n = int(SR * TOTAL) + 1; t = np.arange(n) / SR; rng = np.random.default_rng(11)
shots = []
for p in TL["phrases"]:
    if not shots or shots[-1][0] != p["shot"]: shots.append([p["shot"], p["start"], [p]])
    else: shots[-1][2].append(p)
S = {s[0]: (0.0 if i == 0 else s[1]) for i, s in enumerate(shots)}
E = {s[0]: (shots[i + 1][1] if i + 1 < len(shots) else TOTAL) for i, s in enumerate(shots)}
P2 = {s[0]: (s[2][1]["start"] if len(s[2]) > 1 else E[s[0]]) for s in shots}
W = [(w[0], w[2], p["shot"]) for p in TL["phrases"] for w in p["words"]]
def wt(shot, pre, fb=0.0, nth=0):
    l = [a for a, w, s in W if s == shot and w.lower().startswith(pre)]
    return l[nth] if len(l) > nth else S[shot] + fb

def put(buf, sig, at, g=1.0):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(n, i + len(sig))
    if j > i: buf[i:j] += sig[: j - i] * g
def add(*a):
    o = np.zeros(max(len(x) for x in a))
    for x in a: o[:len(x)] += x
    return o
def lp(x, k): return np.convolve(x, np.ones(k) / k, "same") if k > 1 else x
def hp(x, k): return x - lp(x, k)
def tone(f, d, dec=6.0, harm=(1, 0.35, 0.12)):
    k = np.arange(int(SR * d)) / SR; return sum(a * np.sin(2 * np.pi * f * (i + 1) * k) for i, a in enumerate(harm)) * np.exp(-k * dec) * np.minimum(1, k / 0.004)
def sweep(f0, f1, d, dec=3.0, shape=1.0):
    k = np.arange(int(SR * d)) / SR; f = f0 + (f1 - f0) * (k / d) ** shape; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-k * dec) * np.minimum(1, k / 0.004)
def nz(d, dec=20.0, k_lp=1): k = np.arange(int(SR * d)) / SR; return lp(rng.normal(0, 1, len(k)), k_lp) * np.exp(-k * dec)
def rev(x, wet=0.3, d=0.9, dec=5.0):
    k = np.arange(int(SR * d)) / SR; ir = lp(rng.normal(0, 1, len(k)) * np.exp(-k * dec), 5); ir[0] = 0
    y = np.convolve(x, ir)[: len(x)]; y /= (np.abs(y).max() + 1e-9) / (np.abs(x).max() + 1e-9); return x + wet * y

sfx = np.zeros(n); amb = np.zeros(n); mus = np.zeros(n)
def whoosh(at, d=0.4, g=0.5): w = lp(rng.normal(0, 1, int(SR * d)), 22); k = np.arange(len(w)) / len(w); put(sfx, hp(w, 400) * np.sin(np.pi * k) ** 2 * 3, at - d * 0.6, g)
def pop(at, f=520, g=0.5): put(sfx, sweep(f, f * 2.2, 0.09, 28), at, g)
def thud(at, g=0.9): put(sfx, sweep(130, 45, 0.3, 11), at, g); put(sfx, nz(0.05, 60) * 0.5, at, g)
def ding(at, f=1318, g=0.35): put(sfx, tone(f, 0.9, 5) + tone(f * 1.5, 0.9, 6) * 0.5, at, g)
def tick(at, g=0.25, f=2400): put(sfx, add(tone(f, 0.03, 120, (1,)), nz(0.012, 200) * 0.4), at, g)
def boing(at, g=0.6):
    d = 0.7; k = np.arange(int(SR * d)) / SR; f = 170 + 130 * np.exp(-k * 5) * np.sin(2 * np.pi * 11 * k) + 60 * np.exp(-k * 3)
    put(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-k * 4.5), at, g)
def thwip(at, g=0.4): put(sfx, add(hp(nz(0.07, 45, 3), 200) * 3, sweep(900, 2600, 0.06, 30) * 0.4), at, g)
def slurp(at, g=0.35):
    d = 0.11; k = np.arange(int(SR * d)) / SR; put(sfx, lp(rng.normal(0, 1, len(k)), 6) * np.sin(2 * np.pi * (300 + 1500 * k / d) * k) * np.sin(np.pi * k / d) * 2.2, at, g)
def squish(at, g=0.4):
    d = 0.22; k = np.arange(int(SR * d)) / SR; put(sfx, lp(rng.normal(0, 1, len(k)), 14) * (0.5 + 0.5 * np.sin(2 * np.pi * 38 * k)) * np.sin(np.pi * k / d) * 5, at, g)
def shing(at, g=0.4):
    d = 0.6; k = np.arange(int(SR * d)) / SR; put(sfx, (np.sin(2 * np.pi * 5200 * k) + np.sin(2 * np.pi * 7350 * k) * 0.7 + hp(rng.normal(0, 1, len(k)), 6) * 0.5 * np.exp(-k * 25)) * np.exp(-k * 7) * np.minimum(1, k / 0.01), at, g)
def scratch(at, g=0.7):
    d = 0.32; k = np.arange(int(SR * d)) / SR; f = 900 - 700 * (k / d) + 250 * np.sin(2 * np.pi * 14 * k)
    put(sfx, (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + hp(rng.normal(0, 1, len(k)), 8) * 0.8) * np.sin(np.pi * k / d), at, g)
def buzz_err(at, g=0.4): k = np.arange(int(SR * 0.32)) / SR; put(sfx, np.sign(np.sin(2 * np.pi * 110 * k)) * (k < 0.13) * 0.6 + np.sign(np.sin(2 * np.pi * 82 * k)) * (k > 0.16) * 0.6, at, g)
def beep(at, f=1760, g=0.22): put(sfx, tone(f, 0.09, 12, (1,)), at, g)
def impact(at, g=1.0):
    k = np.arange(int(SR * 1.6)) / SR; b = np.sin(2 * np.pi * np.cumsum(38 + 75 * np.exp(-k * 7)) / SR) * np.exp(-k * 2.6)
    put(sfx, b, at, g); put(sfx, nz(0.35, 12, 4) * 0.8, at, g)
def growl(at, d=1.5, g=0.9):
    k = np.arange(int(SR * d)) / SR; f = 95 - 30 * k / d; car = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 27 * k); x = lp(car * am + rng.normal(0, 1, len(k)) * 0.35, 18) * np.sin(np.pi * k / d) ** 0.7
    put(sfx, rev(x * 3, 0.25, 0.8, 5), at, g)
def bubbles(at, cnt=8, g=0.25, span=0.6):
    for i in range(cnt): d = 0.07; k = np.arange(int(SR * d)) / SR; f = rng.uniform(450, 1300) * (1 + k * 13); put(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-k * 42), at + rng.uniform(0, span), g)
def counter(a, b, f0=1500, f1=2600, g=0.16):
    x = a; i = 0
    while x < b: tick(x, g, f0 + (f1 - f0) * (x - a) / (b - a)); x += 0.045; i += 1
def chord(at, freqs, d=2.2, g=0.12, dec=1.3):
    k = np.arange(int(SR * d)) / SR; x = sum(np.sin(2 * np.pi * f * k) + 0.4 * np.sign(np.sin(2 * np.pi * f * k)) * np.exp(-k * 6) for f in freqs) * np.minimum(1, k / 0.01) * np.exp(-k * dec); put(sfx, rev(x, 0.3, 1.2, 3), at, g)
def footstep(at, g=0.3): put(sfx, add(sweep(110, 60, 0.12, 30), nz(0.05, 70, 6) * 1.5), at, g)

def groove(a, b, bpm=104, key=98.0, g=1.0, feel="funk"):
    beat = 60 / bpm; x = a; i = 0; prog = [1, 1, 1.189, 0.891] if feel == "funk" else [1, 0.944, 0.794, 0.891]
    while x < b - 0.05:
        root = key * prog[(i // 8) % 4]; e = min(1, (b - x) / 0.5)
        pat = [1, 0, 0.6, 1, 0, 1, 0.5, 0] if feel == "funk" else [1, 0, 0, 0, 1, 0, 0, 0]
        if pat[i % 8]: put(mus, tone(root * (2 if i % 8 == 5 else 1), 0.26, 9, (1, 0.5, 0.25, 0.1)), x, 0.55 * pat[i % 8] * g * e)
        if feel == "funk":
            if i % 2 == 1: put(mus, hp(nz(0.04, 90), 4), x, 0.1 * g * e)
            if i % 8 in (2, 6): put(mus, nz(0.09, 40, 2) + tone(190, 0.09, 30) * 0.6, x, 0.16 * g * e)
            if i % 8 == 0 or i % 8 == 5: put(mus, sweep(120, 48, 0.16, 16), x, 0.5 * g * e)
            mel = [3, 0, 2.52, 0, 2, 2.52, 3, 4][i % 8]
            if mel and (i // 8) % 2 == 1: put(mus, tone(root * mel, 0.3, 10, (1, 0.2)), x, 0.13 * g * e)
        else:
            put(mus, tone(root * [2, 2.378, 3, 2.378][i % 4], 0.5, 5, (1, 0.3)), x, 0.1 * g * e)
        x += beat / 2; i += 1

def seg_env(a, b, f=0.15): return np.clip((t - a) / f, 0, 1) * np.clip((b - t) / f, 0, 1)
def chirp(at, g=0.12):
    f0 = rng.uniform(2400, 3800)
    for j in range(rng.integers(2, 5)): put(sfx, sweep(f0, f0 * rng.uniform(0.8, 1.35), 0.07, 18), at + j * 0.09, g)
def plop(at, g=0.4): put(sfx, sweep(700, 180, 0.12, 20), at, g)
wind = lp(rng.normal(0, 1, n), 300) * 0.9
amb += wind * 0.3; water = hp(lp(rng.normal(0, 1, n), 8), 200) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)) * 0.12; amb += water
x = 0.4
while x < TOTAL - 0.5: put(amb, sweep(rng.uniform(2400, 3600), rng.uniform(2600, 4200), 0.07, 18), x, 0.05); put(amb, sweep(3000, 3600, 0.06, 18), x + 0.1, 0.04); x += rng.uniform(0.8, 2.0)
crk = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 17 * t) > 0.3) * 0.02; amb += crk * seg_env(S["dorme"], E["dorme"])
groove(0.0, S["nojo"] - 0.15, 108, 110.0, 0.9)
groove(S["nojo"] + 0.9, S["dorme"] - 0.1, 100, 98.0, 0.75)
groove(S["corre"], TOTAL - 0.4, 116, 110.0, 0.9)
for nme in S:
    if S[nme] > 0: whoosh(S[nme], 0.35, 0.45)
impact(0.0, 0.4); pop(0.05, 500, 0.4)
for i in range(3): plop(0.55 + i * 0.55, 0.5); chirp(0.6 + i * 0.55, 0.14)
fa = wt("sobe", "fácil", 3.4); scratch(fa - 0.12, 0.5); boing(fa + 0.1, 0.35)
ca = wt("negocio", "carrapatos", 2.4)
for i in range(6): tick(ca - 0.6 + i * 0.32, 0.35, 2600); pop(ca - 0.58 + i * 0.32, 800 + i * 60, 0.3)
thud(wt("negocio", "graça", 4) - 0.25, 0.8); ding(wt("negocio", "graça", 4), 1568, 0.25)
pop(S["maior"] + 0.15, 520, 0.4); k60 = wt("maior", "60", 2.5); counter(k60 - 0.2, k60 + 0.6); ding(k60 + 0.62, 1568, 0.3); thud(k60 + 0.62, 0.6)
bubbles(S["topo"] + 0.1, 8, 0.2, 1.5); 
for w_, f_ in (("olho", 700), ("orelha", 800), ("nariz", 900)): pop(wt("topo", w_, 1) - 0.1, f_, 0.4)
put(sfx, sweep(500, 150, 0.4, 5), wt("topo", "escondida", 3) - 0.5, 0.3); bubbles(S["folego"], 14, 0.22, 2.2)
x = S["folego"] + 0.3
while x < wt("folego", "5", 1.6) + 0.5: tick(x, 0.2, 1700); x += 0.1
ding(wt("folego", "5", 1.6) + 0.5, 1760, 0.3); td = wt("folego", "dentes", 3) - 0.2; whoosh(td, 0.3, 0.4); put(sfx, sweep(200, 900, E["folego"] - td - 0.3, 0.6) * 0.5, td, 0.25); thud(td + 0.3, 0.8)
for shot, w_ in (("fimA", "brasil"), ("fimB", "zerou")):
    tg = wt(shot, w_, 2) - (0.3 if shot == "fimA" else 0.2); put(sfx, sweep(1500, 600, 0.25, 4), tg, 0.2); shing(tg + 0.28, 0.25); impact(tg + 0.3, 0.6); chord(tg + 0.3, (261.6, 329.6, 392, 523.3), 1.8, 0.1)
pop(wt("fimA", "manda", 2.2) - 0.05, 650, 0.45); ding(wt("fimA", "manda", 2.2) + 0.2, 1976, 0.25)
scratch(S["nojo"] - 0.08, 0.7); thud(S["nojo"] + 0.2, 0.8); co = wt("nojo", "cocô", 4); buzz_err(co - 0.15, 0.3); 
for i in range(5): squish(co + 0.2 + (E["nojo"] - 0.4 - co) * (i + 0.6) / 5, 0.5)
pop(S["digest"] + 0.15, 520, 0.4); du = wt("digest", "duas", 3); whoosh(du - 0.2, 0.4, 0.5); thud(du - 0.1, 0.7); ding(du, 1318, 0.25)
x = S["digest"] + 0.3
while x < E["digest"] - 0.2: squish(x, 0.18); x += 0.55
for i in range(3): put(sfx, sweep(300, 180, 0.5, 4) * 0.6, S["dorme"] + 0.3 + i * 1.1, 0.18)
on = wt("dorme", "onça", 3.5); growl(on - 1.2, 1.0, 0.3); put(sfx, sweep(500, 900, 0.18, 6), on - 0.2, 0.4)
x = S["corre"]
while x < E["corre"] - 0.1: footstep(x, 0.3); put(sfx, tone(240, 0.05, 40, (1, 0.4)), x, 0.15); x += 0.1
v35 = wt("corre", "35", 2); counter(v35 - 0.2, v35 + 0.5); ding(v35 + 0.52, 1568, 0.3); thud(wt("corre", "roedor", 3) - 0.05, 0.8); pop(wt("corre", "você", 4.4) - 0.1, 400, 0.45)
pop(S["bando"] + 0.15, 520, 0.4); put(sfx, np.sign(np.sin(2 * np.pi * 190 * np.arange(int(SR * 0.14)) / SR)) * np.sin(np.pi * np.arange(int(SR * 0.14)) / int(SR * 0.14)) * 0.6, wt("bando", "late", 2.8), 0.4)
put(sfx, sweep(1400, 2400, 0.35, 3), wt("bando", "assobia", 3.3), 0.25); kk = np.arange(int(SR * 0.6)) / SR; put(sfx, np.sin(2 * np.pi * 70 * kk) * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * kk)) * np.sin(np.pi * kk / 0.6), wt("bando", "ronrona", 4), 0.5)
pop(S["nome"] + 0.1, 520, 0.4); thud(wt("nome", "comedora", 3) - 0.1, 0.7); ding(wt("nome", "comedora", 3), 1318, 0.25)
for i, f in enumerate((1046.5, 1174.7, 1568, 2093)): put(sfx, tone(f, 1.2, 3, (1, 0.2)), S["japao"] + 0.1 + i * 0.12, 0.14)
bubbles(S["japao"] + 0.5, 12, 0.18, 3); pop(S["fimB"] + 0.2, 520, 0.35); pop(P2["fimB"] + 0.05, 650, 0.45); ding(TOTAL - 1.2, 1318, 0.3); ding(TOTAL - 1.05, 1976, 0.25)

sfx = rev(sfx, 0.12, 0.7, 6)
nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1: nar = nar.mean(1)
if sr != SR: nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
vb = np.zeros(n); put(vb, nar, OFF, 1.0); vb /= np.abs(vb).max() / 0.9
duck = 1 - 0.68 * np.clip(lp(np.abs(vb), 4800) / 0.04, 0, 1)
mus *= np.clip((TOTAL - t) / 0.6, 0, 1)
SFXG = 0.2
mix = vb + mus * 0.17 * duck + amb * 0.45 * (0.5 + 0.5 * duck) + sfx * SFXG * (0.4 + 0.6 * duck)
mix *= np.clip((TOTAL - t) / 0.25, 0, 1)
mix = np.tanh(mix * 1.25) ; mix /= np.abs(mix).max() / 0.96
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR)
rms = lambda x: float(np.sqrt(np.mean(x ** 2)))
print("mix ok", round(TOTAL, 2), "rms voz", round(rms(vb), 3), "mus", round(rms(mus * 0.2), 3), "amb", round(rms(amb * 0.7), 3), "sfx", round(rms(sfx * 0.42), 3))

# diagnóstico: fundo x voz por janela de 0,5 s
bg = mus * 0.17 * duck + amb * 0.45 * (0.5 + 0.5 * duck) + sfx * SFXG * (0.4 + 0.6 * duck)
win = SR // 2; worst = []
for i in range(0, n - win, win):
    v = rms(vb[i:i + win]); b = rms(bg[i:i + win])
    if v > 0.03: worst.append((20 * np.log10(b / v + 1e-9), i / SR))
worst.sort(reverse=True); print("fundo-voz dB, piores:", [(round(a, 1), round(b, 1)) for a, b in worst[:10]]); print("mediana:", round(float(np.median([a for a, _ in worst])), 1))


"""009-preguica: trilha + ambiente + efeitos sincronizados nas palavras + narração."""
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
amb += wind * 0.3; water = hp(lp(rng.normal(0, 1, n), 8), 200) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)) * 0.12
amb += water * (0.35 + 0.65 * (seg_env(S["nada"], E["folego"]) > 0))
x = 0.4
while x < TOTAL - 0.5: put(amb, sweep(rng.uniform(2400, 3600), rng.uniform(2600, 4200), 0.07, 18), x, 0.05); put(amb, sweep(3000, 3600, 0.06, 18), x + 0.1, 0.04); x += rng.uniform(0.8, 2.0)
crk = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 17 * t) > 0.3) * 0.02; amb += crk * seg_env(S["sono"], E["sono"])
# música: muda na parte B, na virada e no fecho
groove(0.0, S["lenta"] - 0.15, 104, 110.0, 0.9)
groove(S["lenta"] + 0.9, S["nada"] - 0.1, 96, 98.0, 0.75)
groove(wt("nada", "água", 2.4) - 0.2, S["sono"] - 0.1, 120, 110.0, 0.95)
groove(S["sono"], S["fimB"] - 0.1, 80, 98.0, 0.6, "soft")
groove(S["fimB"], TOTAL - 0.4, 108, 110.0, 0.9)
for nme in S:
    if S[nme] > 0: whoosh(S[nme], 0.35, 0.45)
impact(0.0, 0.4); pop(0.05, 500, 0.4)
de = wt("abre", "descer", 3.6); whoosh(de - 0.1, 0.3, 0.5); put(sfx, sweep(900, 200, 0.6, 3), de - 0.05, 0.3); boing(de + 0.45, 0.3)
co = wt("calma", "cocô", 1.5); scratch(co - 0.2, 0.5); thud(co - 0.05, 0.9); buzz_err(co + 0.05, 0.25); bi = wt("calma", "bicho", 3); pop(bi - 0.1, 600, 0.45); ding(bi + 0.1, 1568, 0.25)
te = wt("semana", "terço", 3); pop(S["semana"] + 0.05, 520, 0.4)
for i in range(7): tick(S["semana"] + 0.2 + (te - 0.3 - S["semana"] - 0.2) * (i + 0.5) / 7, 0.4, 1500 + i * 150); squish(S["semana"] + 0.2 + (te - 0.3 - S["semana"] - 0.2) * (i + 0.5) / 7, 0.15)
put(sfx, sweep(160, 520, te - S["semana"], 0.5) * 0.5, S["semana"] + 0.1, 0.2); thud(te - 0.15, 0.9); ding(te - 0.1, 1568, 0.3)
da = wt("desce", "dancinha", 2.8); td = da - 0.25; x = S["desce"] + 0.2
while x < td - 0.1: put(sfx, sweep(300, 220, 0.18, 8), x, 0.3); x += 0.45
pop(wt("desce", "devagar", 1.6) - 0.5, 520, 0.4)
for i, f in enumerate((523, 659, 784, 659, 523, 784)): put(sfx, tone(f, 0.16, 12, (1, 0.4, 0.2)), td + 0.1 + i * 0.13, 0.3)
thud(td + 0.15, 0.7); cv = wt("desce", "cava", 3.6)
for i in range(5): put(sfx, hp(nz(0.09, 30, 3), 100) * 3, cv + i * 0.28, 0.3); tick(cv + i * 0.28, 0.2, 900)
rs = wt("desce", "resolve", 5.2)
for i in range(4): plop(rs + 0.02 + i * 0.12, 0.5)
thud(rs + 0.05, 0.6); ding(rs + 0.25, 1976, 0.3)
pe = wt("risco", "perigo", 1.6); growl(S["risco"] + 0.3, 1.2, 0.3); scratch(pe - 0.15, 0.4); thud(pe - 0.1, 0.9); put(sfx, sweep(500, 900, 0.18, 6), pe - 0.1, 0.4)
me = wt("risco", "metade", 2.4); counter(me - 0.15, me + 0.5, 900, 500); impact(me + 0.5, 0.7); buzz_err(me + 0.55, 0.25)
for shot, w_, d_ in (("fimA", "banheiro", 0.25), ("fimB", "economiza", 0.2)):
    tg = wt(shot, w_, 2) - d_; put(sfx, sweep(1500, 600, 0.25, 4), tg, 0.2); shing(tg + 0.28, 0.25); impact(tg + 0.3, 0.6); chord(tg + 0.3, (261.6, 329.6, 392, 523.3), 1.8, 0.1)
ma = wt("fimA", "manda", 2.4); pop(ma - 0.05, 650, 0.45); ding(ma + 0.2, 1976, 0.25)
scratch(S["lenta"] - 0.08, 0.7); pi = wt("lenta", "piora", 1); thud(pi - 0.1, 0.9); buzz_err(pi, 0.25)
ms = wt("lenta", "mês", 2.6); counter(ms - 0.4, ms + 0.5); ding(ms + 0.52, 1568, 0.3); thud(ms + 0.52, 0.6)
x = S["lenta"] + 0.3
while x < E["lenta"] - 0.2: squish(x, 0.14); x += 0.4
al = wt("verde", "alga", 1.8); pop(al - 0.15, 520, 0.4); put(sfx, sweep(300, 1200, 1.2, 1.2) * 0.5, al - 0.2, 0.22); vd = wt("verde", "verde", 3); thud(vd - 0.1, 0.9); ding(vd, 1318, 0.25)
mr = wt("verde", "mariposa", 4.4); kk = np.arange(int(SR * 1.6)) / SR; put(sfx, lp(rng.normal(0, 1, len(kk)), 6) * (np.sin(2 * np.pi * 34 * kk) > 0) * np.sin(np.pi * kk / 1.6) * 1.5, mr - 0.5, 0.18); pop(mr - 0.2, 900, 0.35)
kk = np.arange(int(SR * 3.0)) / SR; put(sfx, lp(rng.normal(0, 1, len(kk)), 6) * (np.sin(2 * np.pi * 34 * kk) > 0) * np.sin(np.pi * kk / 3.0) * 1.5, S["ovos"], 0.12)
pop(S["ovos"] + 0.3, 520, 0.4); c2 = wt("ovos", "cocô", 2.4); thud(c2 - 0.1, 0.9); buzz_err(c2 - 0.05, 0.25)
for i in range(7): pop(c2 + i * 0.12, 1000 + i * 90, 0.3)
cd = wt("ovos", "condomínio", 4); pop(cd - 0.15, 650, 0.45); ding(cd + 0.1, 1568, 0.3)
pop(S["nada"] + 0.15, 520, 0.4); chord(S["nada"] + 0.2, (220, 261.6, 329.6), 1.6, 0.08); ag = wt("nada", "água", 2.4); plop(ag - 0.25, 0.6); bubbles(ag - 0.2, 10, 0.2, 0.5)
x = ag - 0.1
while x < E["nada"] - 0.1: put(sfx, hp(nz(0.1, 25, 4), 150) * 3, x, 0.22); x += 0.22
tr = wt("nada", "três", 3.2); thud(tr - 0.15, 0.9); ding(tr - 0.1, 1568, 0.3); po = wt("nada", "porra", 4.8); scratch(po - 0.15, 0.5); impact(po, 0.9); nd = wt("nada", "nadar", 6); thud(nd - 0.35, 0.9)
bubbles(S["folego"], 14, 0.22, 2.2); x = S["folego"] + 0.2; q4 = wt("folego", "40", 1.8)
while x < q4 + 0.5: tick(x, 0.2, 1700); x += 0.08
ding(q4 + 0.5, 1760, 0.3)
boing(S["ponta"] + 0.05, 0.4); p9 = wt("ponta", "90", 0.5); counter(p9 - 0.2, p9 + 0.5); ding(p9 + 0.52, 1568, 0.3); thud(p9 + 0.5, 0.6)
g2 = wt("cabeca", "270", 1); kk = np.arange(int(SR * (g2 + 0.9 - S["cabeca"] - 0.25))) / SR; put(sfx, np.sign(np.sin(2 * np.pi * 30 * kk)) * lp(rng.normal(0, 1, len(kk)), 3) * 0.8 + sweep(300, 900, len(kk) / SR, 0.3)[:len(kk)] * 0.4, S["cabeca"] + 0.25, 0.22); ding(g2 + 0.9, 1760, 0.3)
cj = wt("cabeca", "coruja", 3); put(sfx, tone(392, 0.25, 5, (1, 0.3)), cj - 0.1, 0.3); put(sfx, tone(330, 0.5, 4, (1, 0.3)), cj + 0.2, 0.3)
go = wt("sono", "golpe", 0.8); scratch(go - 0.3, 0.5); thud(go - 0.15, 0.9); nv = wt("sono", "nove", 4); thud(nv - 0.2, 0.8); ding(nv - 0.15, 1318, 0.3)
for i in range(4): put(sfx, sweep(300, 180, 0.5, 4) * 0.6, S["sono"] + 1.2 + i * 1.1, 0.16)
ad = wt("sono", "adolescente", 6.5); whoosh(ad - 0.6, 0.3, 0.5); pop(ad - 0.2, 400, 0.45); boing(ad + 0.1, 0.3)
pop(S["fimB"] + 0.15, 520, 0.35); au = wt("fimB", "aguentaria", 4.5); pop(au - 0.1, 650, 0.45); ding(au + 0.1, 1976, 0.25); pop(P2["fimB"] + 0.05, 650, 0.45); ding(TOTAL - 1.2, 1318, 0.3); ding(TOTAL - 1.05, 1976, 0.25)

sfx = rev(sfx, 0.12, 0.7, 6)
nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1: nar = nar.mean(1)
if sr != SR: nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
vb = np.zeros(n); put(vb, nar, OFF, 1.0); vb /= np.abs(vb).max() / 0.9
duck = 1 - 0.68 * np.clip(lp(np.abs(vb), 4800) / 0.04, 0, 1)
mus *= np.clip((TOTAL - t) / 0.6, 0, 1)
SFXG = 0.235
mix = vb + mus * 0.2 * duck + amb * 0.45 * (0.5 + 0.5 * duck) + sfx * SFXG * (0.4 + 0.6 * duck)
mix *= np.clip((TOTAL - t) / 0.25, 0, 1)
mix = np.tanh(mix * 1.25) ; mix /= np.abs(mix).max() / 0.96
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR)
rms = lambda x: float(np.sqrt(np.mean(x ** 2)))
print("mix ok", round(TOTAL, 2), "rms voz", round(rms(vb), 3), "mus", round(rms(mus * 0.2), 3), "amb", round(rms(amb * 0.7), 3), "sfx", round(rms(sfx * 0.42), 3))

# diagnóstico: fundo x voz por janela de 0,5 s
bg = mus * 0.2 * duck + amb * 0.45 * (0.5 + 0.5 * duck) + sfx * SFXG * (0.4 + 0.6 * duck)
win = SR // 2; worst = []
for i in range(0, n - win, win):
    v = rms(vb[i:i + win]); b = rms(bg[i:i + win])
    if v > 0.03: worst.append((20 * np.log10(b / v + 1e-9), i / SR))
worst.sort(reverse=True); print("fundo-voz dB, piores:", [(round(a, 1), round(b, 1)) for a, b in worst[:10]]); print("mediana:", round(float(np.median([a for a, _ in worst])), 1))


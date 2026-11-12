"""007-sol: trilha + ambiente + efeitos sincronizados nas palavras + narração."""
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
def zap(at, g=0.5):
    d = 0.16; k = np.arange(int(SR * d)) / SR; put(sfx, (np.sign(np.sin(2 * np.pi * 95 * k)) * 0.5 + hp(rng.normal(0, 1, len(k)), 5)) * (rng.random(len(k)) > 0.35) * np.exp(-k * 9), at, g)
def powerdown(at, d=1.2, g=0.5): put(sfx, sweep(420, 35, d, 1.2, 0.6) + 0, at, g); put(sfx, np.sign(np.sin(2 * np.pi * np.cumsum(np.linspace(180, 20, int(SR * d))) / SR)) * np.linspace(1, 0, int(SR * d)) * 0.25, at, g)
def clack(at, g=0.5): put(sfx, add(nz(0.07, 60) * 0.7, tone(180, 0.07, 50, (1,))), at, g)
def pulse(a, b, bpm=96, key=55.0, g=1.0):
    beat = 60 / bpm; x = a; i = 0
    while x < b - 0.05:
        e = min(1, (b - x) / 0.5, (x - a) / 0.3 + 0.4)
        put(mus, tone(key * (1.189 if (i // 16) % 4 == 2 else 1), 0.2, 11, (1, 0.5, 0.2)), x, 0.5 * g * e)
        if i % 4 == 2: put(mus, hp(nz(0.03, 110), 4), x, 0.1 * g * e)
        if i % 8 == 4: put(mus, tone(key * 4 * [1, 1.189, 1.498, 1.189][(i // 8) % 4], 0.6, 4, (1, 0.25)), x, 0.09 * g * e)
        if i % 16 == 0: put(mus, sweep(110, 45, 0.2, 14), x, 0.5 * g * e)
        x += beat / 2; i += 1
def pad(a, b, freqs, g=0.1):
    k = (t >= a) & (t < b); en = seg_env(a, b, 0.8)
    for f in freqs: mus[:] += np.sin(2 * np.pi * f * t + 1.5 * np.sin(2 * np.pi * 0.23 * t + f)) * en * g * k

T_ = {n: wt(*a) for n, a in dict(
    ejec=("sol", "ejeção", 1.6), cara=("sol", "direção", 3), nome=("calma", "nome", 0.8), emc=("calma", "ejeção", 2), bil=("calma", "bilhões", 3.6),
    p17=("prazo", "17", 1.2), dia1=("prazo", "bem-vindo", 2), a1859=("c1859", "1859", 1.3), mex=("c1859", "méxico", 3), tel=("c1859", "telégrafos", 4), fai=("c1859", "faísca", 5),
    queb=("c1989", "quebec", 4), s90=("c1989", "90", 5), verde=("aurora", "verde", 2.5), filmar=("aurora", "todo", 3), story=("aurora", "story", 6),
    fritar=("frita", "fritar", 2.4), meses=("frita", "meses", 4), luz=("escuro", "luz", 0.5), wifi=("escuro", "wi-fi", 1.5), pix=("escuro", "pix", 2.6), fodeu=("escuro", "fodeu", 3.5),
    bomba=("r1", "bomba", 1.5), nao=("r2", "não", 1), h4=("r2", "4", 4), h48=("r2", "48", 5.5), din=("r3", "dinheiro", 0.8), cart=("r3", "cartão", 2.4), rei=("r3", "rei", 4.2),
    torre=("cel", "torre", 1), fam=("cel", "avisa", 2.8), tanque=("dilema", "tanque", 1.6), ir=("dilema", "ir", 4.4), fica=("cta", "fica", 0.5), vai=("cta", "vai", 1), dia2=("cta", "votada", 2), segue=("cta", "segue", 3.6)).items()}
G = type("G", (), T_)

# ---------------- ambientes
SPACE = [(0, G.nome - 0.1 if False else S["calma"]), (G.bil - 0.15, G.tel - 0.2)]
CORL = [(S["calma"], G.bil - 0.15), (G.tel - 0.2, E["c1859"])]
CITY = [(S["c1989"], G.wifi - 0.15)]
DARK = [(G.wifi - 0.15, E["cel"]), (P2["cta"], TOTAL)]
DAWN = [(S["dilema"], P2["cta"])]
drone = (np.sin(2 * np.pi * 41 * t) + 0.5 * np.sin(2 * np.pi * 61.5 * t + np.sin(2 * np.pi * 0.2 * t)) + 0.2 * np.sin(2 * np.pi * 123 * t)) * 0.07 + lp(rng.normal(0, 1, n), 400) * 0.5
for a, b in SPACE: amb += drone * seg_env(a, b)
hum = 0.05 * np.sin(2 * np.pi * 60 * t) + 0.03 * np.sin(2 * np.pi * 120 * t) + lp(rng.normal(0, 1, n), 70) * 0.08
for a, b in CORL: amb += hum * seg_env(a, b)
wind = lp(rng.normal(0, 1, n), 300) * 0.9 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t))
for a, b in CITY: amb += (wind * 0.5 + 0.03 * np.sin(2 * np.pi * 55 * t)) * seg_env(a, b)
room = lp(rng.normal(0, 1, n), 500) * 0.9 + 0.012 * np.sin(2 * np.pi * 120 * t) * (np.sin(2 * np.pi * 9 * t) > 0)
for a, b in DARK:
    amb += room * seg_env(a, b); x = a + 0.8
    while x < b - 0.3: put(amb, tone(rng.uniform(900, 1300), 0.12, 30, (1, 0.3)), x, 0.06); x += rng.uniform(1.6, 3.2)
    x = a + 0.4
    while x < b - 0.3: put(amb, sweep(62, 38, 0.13, 24), x, 0.12); put(amb, sweep(56, 36, 0.13, 24), x + 0.22, 0.08); x += 0.95
for a, b in DAWN:
    amb += wind * 0.4 * seg_env(a, b); x = a + 0.3
    while x < b - 0.3:
        f0 = rng.uniform(2200, 3600)
        for j in range(rng.integers(2, 5)): put(amb, sweep(f0, f0 * rng.uniform(0.8, 1.35), 0.07, 18), x + j * 0.1, 0.05)
        x += rng.uniform(0.7, 1.6)

# ---------------- trilha
pulse(0.0, S["c1859"] - 0.2, 100, 55.0, 1.0)
groove(S["c1859"] + 0.2, S["aurora"] - 0.2, 92, 98.0, 0.55, "hero")
pad(S["aurora"], S["frita"] + 0.5, (220, 277.2, 329.6, 440, 554.4), 0.035)
rise = hp(lp(rng.normal(0, 1, n), 6), 60) * np.clip((t - S["frita"]) / (G.fodeu - S["frita"]), 0, 1) ** 2 * ((t > S["frita"]) & (t < G.fodeu)); mus += rise * 0.3
mus += (np.sin(2 * np.pi * 49 * t) + 0.5 * np.sin(2 * np.pi * 73.4 * t)) * 0.12 * seg_env(S["frita"], G.fodeu, 0.4)
pulse(S["r1"], E["cel"] - 1.6, 88, 49.0, 0.7)
pulse(S["dilema"], P2["cta"], 104, 55.0, 0.9)
pad(P2["cta"], TOTAL, (110, 130.8, 164.8), 0.05)

# ---------------- efeitos
for nme in S:
    if S[nme] > 0: whoosh(S[nme], 0.4, 0.5)
impact(0.0, 0.5); pop(0.05, 400, 0.4)
put(sfx, sweep(60, 240, 0.5, 1.5), G.ejec - 0.4, 0.4); impact(G.ejec, 1.0); put(sfx, nz(1.4, 2.5, 30) * 4, G.ejec, 0.5); thud(G.ejec + 0.05, 0.8)
put(sfx, hp(lp(rng.normal(0, 1, int(SR * (E["sol"] - G.cara))), 10), 80) * np.linspace(0, 1, int(SR * (E["sol"] - G.cara))) ** 2 * 3, G.cara - 0.25, 0.5); impact(E["sol"] - 0.12, 0.9)
scratch(S["calma"] - 0.08, 0.8); thud(S["calma"] + 0.03, 0.9); pop(G.nome - 0.1, 600, 0.4); pop(G.emc - 0.1, 520, 0.45); ding(G.emc + 0.5, 1318, 0.25)
whoosh(G.bil - 0.15, 0.4, 0.6); impact(G.bil - 0.05, 0.7); counter(G.bil, G.bil + 0.7)
x = G.p17 - 0.5
while x < G.dia1 - 0.12: tick(x, 0.3, 1900); x += 0.11
impact(G.dia1 - 0.08, 1.0); thud(G.dia1 - 0.06, 1.0); chord(G.dia1 - 0.06, (110, 130.8, 164.8, 220), 2.2, 0.12)
pop(S["c1859"] + 0.08, 450, 0.4); put(sfx, sweep(600, 2400, G.mex + 0.4 - G.a1859, 0.6) * 0.5, G.a1859, 0.16); ding(G.mex, 1568, 0.3); pop(G.mex - 0.05, 700, 0.3)
whoosh(G.tel - 0.2, 0.35, 0.5); x = G.tel - 0.1; morse = [0.07, 0.07, 0.2, 0.07, 0.2, 0.2, 0.07, 0.07, 0.2, 0.07]; i = 0
while x < G.fai - 0.08: d = morse[i % len(morse)]; k = np.arange(int(SR * d)) / SR; put(sfx, np.sin(2 * np.pi * 820 * k) * np.minimum(1, np.minimum(k, d - k) / 0.005), x, 0.2); x += d + 0.06; i += 1
for i in range(5): zap(G.fai + i * 0.17, 0.6)
thud(G.fai, 0.8); boing(G.fai + 0.1, 0.4)
pop(S["c1989"] + 0.08, 450, 0.4); powerdown(G.queb - 0.1, 1.3, 0.55); counter(G.s90 - 0.2, G.s90 + 0.7); buzz_err(G.s90 + 0.72, 0.35); thud(G.s90 + 1.0, 0.7)
for i, f in enumerate((880, 1108.7, 1318.5, 1760)): put(sfx, tone(f, 1.6, 2.2, (1, 0.2)), G.verde - 0.2 + i * 0.12, 0.14)
for i in range(3): tick(G.filmar + 0.25 + i * 0.3, 0.4, 3000); tick(G.filmar + 0.29 + i * 0.3, 0.3, 2200)
whoosh(P2["aurora"], 0.35, 0.4); pop(G.story - 0.1, 650, 0.4); ding(G.story + 0.1, 1976, 0.25)
bz = np.sign(np.sin(2 * np.pi * 60 * t)) * 0.5 + np.sin(2 * np.pi * 120 * t); sfx += bz * 0.1 * np.clip((t - S["frita"]) / (G.fritar + 0.9 - S["frita"]), 0, 1) ** 2 * ((t > S["frita"]) & (t < G.fritar + 0.9))
pop(S["frita"] + 0.35, 500, 0.35)
for i in range(6): zap(G.fritar - 0.3 + i * 0.2, 0.4 + 0.05 * i)
impact(G.fritar + 0.9, 1.0); put(sfx, nz(0.9, 4, 3) * 2.5, G.fritar + 0.9, 0.7); thud(G.meses - 0.05, 0.9)
powerdown(G.luz - 0.25, 1.1, 0.6); thud(G.luz - 0.1, 0.6); whoosh(G.wifi - 0.15, 0.35, 0.4); buzz_err(G.wifi - 0.1, 0.3); buzz_err(G.pix - 0.1, 0.3)
for i in range(6): clack(G.wifi + 0.1 + (G.fodeu - 0.15 - G.wifi) * i / 5, 0.45)
impact(G.fodeu, 1.0); put(sfx, sweep(90, 28, 1.2, 2), G.fodeu, 0.9); clack(G.fodeu + 0.47, 0.7); zap(G.fodeu + 0.5, 0.25)
for r in ("r1", "r2", "r3"): thud(S[r] + 0.05, 0.9); tick(S[r] + 0.2, 0.3, 1500)
pop(S["r1"] + 0.35, 560, 0.4); buzz_err(G.bomba - 0.05, 0.3)
wl = int(SR * (E["r1"] - P2["r1"] - 0.3)); kk = np.arange(wl) / SR; put(sfx, hp(lp(rng.normal(0, 1, wl), 3), 30) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * kk)) * np.minimum(1, kk / 0.2) * np.minimum(1, (wl / SR - kk) / 0.3) * 1.3, P2["r1"], 0.3); bubbles(P2["r1"] + 0.2, 16, 0.2, E["r1"] - P2["r1"] - 0.6)
put(sfx, nz(0.06, 50) * 2.5, G.nao + 0.1, 0.6); thud(G.nao, 0.9); pop(G.h4 - 0.25, 600, 0.4); ding(G.h4, 1318, 0.25); pop(G.h48 - 0.4, 700, 0.4); ding(G.h48, 1760, 0.25)
ding(G.din, 2093, 0.3); ding(G.din + 0.09, 2637, 0.3); buzz_err(G.cart - 0.05, 0.3); buzz_err(G.cart + 0.3, 0.25); shing(G.rei - 0.1, 0.3); impact(G.rei + 0.12, 0.5); chord(G.rei + 0.12, (261.6, 329.6, 392, 523.3), 1.6, 0.1)
pop(G.torre - 0.2, 520, 0.4); put(sfx, sweep(900, 200, P2["cel"] - G.torre, 0.5) * 0.6, G.torre, 0.12); pop(G.fam - 0.1, 700, 0.4); beep(G.fam + 0.15, 1320, 0.25); beep(G.fam + 0.3, 1760, 0.25)
powerdown(P2["cel"], 0.7, 0.45)
pop(G.tanque - 0.3, 520, 0.4); tick(G.tanque, 0.3); beep(P2["dilema"], 880, 0.35); beep(G.ir - 0.15, 1174, 0.35)
thud(G.fica - 0.05, 0.9); thud(G.vai - 0.05, 0.9); pop(G.dia2 - 0.1, 600, 0.4); impact(G.dia2 + 0.2, 0.5); ding(G.dia2 + 0.2, 1568, 0.3)
whoosh(P2["cta"], 0.4, 0.6); pop(G.segue - 0.1, 650, 0.45); ding(TOTAL - 1.3, 1318, 0.3); ding(TOTAL - 1.15, 1976, 0.25)
# corte seco de tudo no "Fodeu"
cut = 1 - 0.9 * np.exp(-((t - G.fodeu - 0.2) / 0.35) ** 2); mus *= cut; amb *= cut

sfx = rev(sfx, 0.12, 0.7, 6)
nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1: nar = nar.mean(1)
if sr != SR: nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
vb = np.zeros(n); put(vb, nar, OFF, 1.0); vb /= np.abs(vb).max() / 0.9
duck = 1 - 0.68 * np.clip(lp(np.abs(vb), 4800) / 0.04, 0, 1)
mus *= np.clip((TOTAL - t) / 0.6, 0, 1)
SFXG = 0.2
mix = vb + mus * 0.17 * duck + amb * 0.34 * (0.5 + 0.5 * duck) + sfx * SFXG * (0.4 + 0.6 * duck)
mix *= np.clip((TOTAL - t) / 0.25, 0, 1)
mix = np.tanh(mix * 1.25) ; mix /= np.abs(mix).max() / 0.96
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR)
rms = lambda x: float(np.sqrt(np.mean(x ** 2)))
print("mix ok", round(TOTAL, 2), "rms voz", round(rms(vb), 3), "mus", round(rms(mus * 0.2), 3), "amb", round(rms(amb * 0.7), 3), "sfx", round(rms(sfx * 0.42), 3))

# diagnóstico: fundo x voz por janela de 0,5 s
bg = mus * 0.17 * duck + amb * 0.34 * (0.5 + 0.5 * duck) + sfx * SFXG * (0.4 + 0.6 * duck)
win = SR // 2; worst = []
for i in range(0, n - win, win):
    v = rms(vb[i:i + win]); b = rms(bg[i:i + win])
    if v > 0.03: worst.append((20 * np.log10(b / v + 1e-9), i / SR))
worst.sort(reverse=True); print("fundo-voz dB, piores:", [(round(a, 1), round(b, 1)) for a, b in worst[:10]]); print("mediana:", round(float(np.median([a for a, _ in worst])), 1))


"""006-tamandua: trilha + ambiente + efeitos sincronizados nas palavras + narração."""
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

# ------------------------------------------------------------ ambientes por trecho
def seg_env(a, b, f=0.15): return np.clip((t - a) / f, 0, 1) * np.clip((b - t) / f, 0, 1)
COR = [(0, S["reveal"]), (S["outro"], TOTAL)]
XR = [(S["esterno"], E["esterno"]), (S["estomago"], E["estomago"])]
MAC = [(S["cola"], E["cola"]), (S["motivo"], P2["motivo"])]
DAY = [(S["reveal"], E["reveal"]), (S["trinta"], E["rapidinha"]), (P2["motivo"], E["duzentos"])]
DUSK = [(S["virada"], E["foda"])]
hum = 0.05 * np.sin(2 * np.pi * 60 * t) + 0.03 * np.sin(2 * np.pi * 120 * t) + lp(rng.normal(0, 1, n), 70) * 0.08 + np.sin(2 * np.pi * 120 * t) * np.sign(np.sin(2 * np.pi * 240 * t)) * 0.004
for a, b in COR: amb += hum * seg_env(a, b)
cic = hp(rng.normal(0, 1, n), 3) * (0.55 + 0.45 * np.sin(2 * np.pi * 43 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.31 * t)) * 0.035
wind = lp(rng.normal(0, 1, n), 300) * 0.9 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t))
for a, b in DAY:
    amb += (cic + wind * 0.25) * seg_env(a, b)
    x = a + 0.3
    while x < b - 0.3:
        f0 = rng.uniform(2200, 3600)
        for j in range(rng.integers(2, 5)): put(amb, sweep(f0, f0 * rng.uniform(0.8, 1.35), 0.07, 18), x + j * 0.1, 0.05)
        x += rng.uniform(0.9, 2.2)
crk = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 17 * t) > 0.3) * (np.sin(2 * np.pi * 1.9 * t) > -0.2) * 0.018
for a, b in DUSK: amb += (crk + wind * 0.45 + 0.05 * np.sin(2 * np.pi * 49 * t)) * seg_env(a, b)
sci = (np.sin(2 * np.pi * 90 * t) * 0.05 + np.sin(2 * np.pi * 180.7 * t) * 0.025 + np.sin(2 * np.pi * 1200 * t) * 0.006 * (np.sin(2 * np.pi * 3 * t) > 0.9))
for a, b in XR:
    amb += sci * seg_env(a, b)
    x = a + 0.2
    while x < b: beep(x, 2200, 0.05); x += 0.75
for a, b in MAC: amb += lp(rng.normal(0, 1, n), 180) * 1.2 * seg_env(a, b)

# ------------------------------------------------------------ trilha
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
groove(0.0, S["calma"] - 0.05, 112, 110.0, 1.0)
groove(S["calma"] + 1.2, S["virada"] - 0.1, 104, 98.0, 0.85)
groove(S["outro"], TOTAL - 0.4, 104, 98.0, 0.8)
# virada: drone + batimento, depois vitória
a, b = S["virada"], wt("abraco", "abraço", 1.5)
k = np.clip((t - a) / (b - a), 0, 1) * ((t >= a) & (t < b))
mus += (np.sin(2 * np.pi * 49 * t) + 0.5 * np.sin(2 * np.pi * 73.4 * t + 2 * np.sin(2 * np.pi * 0.4 * t)) + 0.25 * np.sin(2 * np.pi * 98.6 * t)) * 0.16 * np.sqrt(k) * seg_env(a, b, 0.3)
x = a + 0.4
while x < b - 0.2: put(mus, sweep(70, 40, 0.14, 22), x, 0.6); put(mus, sweep(62, 38, 0.14, 22), x + 0.2, 0.4); x += max(0.42, 0.85 - 0.06 * (x - a))
rise = lp(rng.normal(0, 1, n), 6) * np.clip((t - (b - 1.6)) / 1.6, 0, 1) ** 2 * ((t < b) & (t > b - 1.6)); mus += hp(rise, 60) * 0.25
groove(b + 0.1, S["outro"] - 0.05, 120, 110.0, 0.9, "hero")

# ------------------------------------------------------------ efeitos por cena
impact(0.0, 0.55); pop(0.06, 400, 0.4)
h60 = wt("hook1", "60", 1.2); boing(h60, 0.75); thud(h60 + 0.02, 0.4); tick(h60 + 0.45); pop(h60 + 0.5, 700, 0.35)
whoosh(S["hook2"]); x = S["hook2"]
while x < E["hook2"] - 0.1: thwip(x + 0.2, 0.3); x += 0.4
h150 = wt("hook2", "150", 1.2); counter(h150 - 0.1, h150 + 0.9); ding(h150 + 0.92, 1568, 0.3); whoosh((S["hook2"] + E["hook2"]) / 2, 0.3, 0.35)
scratch(S["calma"] - 0.08, 0.8); thud(S["calma"] + 0.03, 0.9); sor = wt("calma", "sorriso", 1.2); whoosh(sor - 0.1, 0.25, 0.35); pop(sor, 600, 0.4)
fm = wt("calma", "formiga", 3); whoosh(fm - 0.1, 0.25, 0.3)
for i in range(7): tick(fm + i * 0.09, 0.2, 3400)
pop(fm + 0.15, 900, 0.35)
whoosh(S["reveal"], 0.5, 0.7); impact(S["reveal"], 0.35); x = S["reveal"] + 0.15
while x < wt("reveal", "língua", 5) - 0.2: footstep(x, 0.22); x += 0.224
pop(wt("reveal", "tamandu", 0.6), 500, 0.45); whoosh(P2["reveal"], 0.3, 0.4); pop(wt("reveal", "brasileiro", 2), 800, 0.3); thud(wt("reveal", "dente", 3), 0.8)
rl = wt("reveal", "língua", 5); whoosh(rl - 0.15, 0.3, 0.4); put(sfx, sweep(300, 1800, 0.22, 2), rl, 0.3); thwip(rl + 0.02, 0.6); tick(rl + 0.5); pop(rl + 0.55, 700, 0.3)
whoosh(S["esterno"], 0.4, 0.5); put(sfx, sweep(200, 2400, 0.5, 1.5) * 0.5, S["esterno"], 0.25)
beep(wt("esterno", "boca", 1.2) - 0.2, 1320, 0.25); buzz_err(wt("esterno", "boca", 1.2) + 0.05, 0.18)
ep = wt("esterno", "peito", 3); beep(ep, 1760, 0.3); beep(ep + 0.12, 2637, 0.3); ding(wt("esterno", "esterno", 4), 1046, 0.3)
whoosh(S["cola"], 0.4, 0.5); x = S["cola"] + 0.1
while x < E["cola"] - 0.2: squish(x, 0.25); x += rng.uniform(0.45, 0.8)
pop(wt("cola", "fina", 0.2) + 0.1, 600, 0.35); ce = wt("cola", "espinhos", 2); whoosh(ce - 0.1, 0.25, 0.35)
for i in range(5): tick(ce + i * 0.05, 0.22, 3000 + i * 300)
cs = wt("cola", "saliva", 4); whoosh(cs - 0.1, 0.25, 0.35); bubbles(cs, 6, 0.22, 0.5); squish(cs + 0.05, 0.5)
whoosh(S["trinta"], 0.5, 0.6); x = S["trinta"] + 0.1
while x < wt("rapidinha", "tchau", 4): slurp(x, 0.28); x += 0.4
t30 = wt("trinta", "30", 1.5); whoosh(t30 - 0.15, 0.25, 0.35); counter(t30 - 0.15, t30 + 1.3); ding(t30 + 1.32, 1568, 0.35); ding(t30 + 1.4, 2093, 0.25)
whoosh(S["rapidinha"], 0.3, 0.4); x = S["rapidinha"] + 0.3; rm = wt("rapidinha", "minuto", 2)
while x < rm + 0.4: tick(x, 0.3, 1800); tick(x + 0.06, 0.18, 1400); x += 0.13
ding(rm + 0.42, 1760, 0.4); rr = wt("rapidinha", "rapidinha", 3); whoosh(rr - 0.1, 0.25, 0.3); thud(rr, 0.85)
rt = wt("rapidinha", "tchau", 4); put(sfx, sweep(1400, 350, 0.35, 2), rt, 0.28); pop(rt, 500, 0.5); x = rt + 0.45
while x < E["rapidinha"]: footstep(x, 0.25); x += 0.224
whoosh(S["motivo"], 0.4, 0.6); x = S["motivo"]
while x < P2["motivo"]: tick(x, 0.12, rng.uniform(2500, 5000)); x += rng.uniform(0.02, 0.06)
pop(S["motivo"] + 0.1, 400, 0.4); mm = wt("motivo", "morder", 2); put(sfx, add(nz(0.05, 80) * 2, tone(1900, 0.06, 60)), mm + 0.06, 0.7); impact(mm + 0.07, 0.7)
whoosh(P2["motivo"], 0.4, 0.5); pop(P2["motivo"] + 0.1, 650, 0.4); ding(wt("motivo", "vivo", 1.5), 1318, 0.3); ding(wt("motivo", "voltar", 2.2), 1568, 0.22)
whoosh(S["duzentos"], 0.5, 0.6); d2 = wt("duzentos", "200", 0.6); counter(d2 - 0.1, d2 + 1.2); ding(d2 + 1.22, 1568, 0.3)
for i in range(11): put(sfx, tone(523 * 2 ** ((i * 2 % 12) / 12), 0.12, 20, (1, 0.3)), S["duzentos"] + 0.25 + i * (E["duzentos"] - S["duzentos"] - 0.5) / 11, 0.14)
dr = wt("duzentos", "rodízio", 3.5); thud(dr - 0.03, 0.6); put(sfx, np.sign(np.sin(2 * np.pi * 120 * np.arange(int(SR * 0.7)) / SR)) * (rng.random(int(SR * 0.7)) > 0.25) * 0.08, dr, 1.0); ding(dr + 0.05, 1976, 0.3)
whoosh(S["estomago"], 0.4, 0.5); put(sfx, sweep(200, 2400, 0.5, 1.5) * 0.5, S["estomago"], 0.22); bubbles(S["estomago"] + 0.2, 26, 0.16, E["estomago"] - S["estomago"] - 0.5)
ea = wt("estomago", "ácido", 1.5); buzz_err(ea - 0.25, 0.3); ea2 = wt("estomago", "ácido", 4, 1); beep(ea2 - 0.3, 1760, 0.3); put(sfx, hp(nz(1.1, 3), 3) * 1.5, ea2 - 0.2, 0.18); ding(ea2, 1046, 0.25)
# virada
vs = S["virada"]; put(sfx, sweep(160, 40, 0.9, 2), vs - 0.05, 0.5); whoosh(vs, 0.5, 0.5); vl = wt("virada", "linguarudo", 2.5); whoosh(vl - 0.25, 0.3, 0.4)
vo = wt("virada", "onça", 4.5); growl(vo - 0.2, 1.3, 0.42); impact(vo + 0.45, 0.45); pop(vo + 0.1, 380, 0.3)
gs = S["garras"]; whoosh(gs, 0.3, 0.4); shing(gs + 0.28, 0.4); g10 = wt("garras", "10", 1.5); tick(g10 - 0.2); pop(g10 + 0.05, 700, 0.35)
whoosh(P2["garras"], 0.3, 0.4); gp = wt("garras", "pé", 4); put(sfx, sweep(120, 420, 0.4, 2), gp - 0.2, 0.3); thud(gp + 0.25, 0.9)
gr = wt("garras", "rabo", 5); pop(gr, 500, 0.35); ga = wt("garras", "abre", 5.5); whoosh(ga - 0.1, 0.3, 0.5); shing(ga + 0.1, 0.45)
whoosh(S["abraco"], 0.4, 0.5); ab = wt("abraco", "abraço", 1.5); impact(ab - 0.1, 0.9); chord(ab - 0.08, (110, 164.8, 220, 277.2, 329.6), 2.4, 0.11)
whoosh(P2["abraco"], 0.3, 0.4); ap = wt("abraco", "pensa", 5); put(sfx, sweep(500, 900, 0.18, 6), ap - 0.25, 0.4); put(sfx, sweep(700, 1300, 0.2, 6), ap - 0.05, 0.4)
put(sfx, sweep(620, 240, 0.7, 2) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * np.arange(int(SR * 0.7)) / SR)), ap + 0.9, 0.22)
fs = S["foda"]; whoosh(fs, 0.3, 0.4); put(sfx, sweep(300, 1800, 0.22, 2), fs + 0.15, 0.3); thwip(fs + 0.17, 0.6); pop(fs + 0.75, 700, 0.3)
fa = wt("foda", "ainda", 2); whoosh(fa - 0.15, 0.35, 0.5); x = fa - 0.1; i = 0
while x < wt("foda", "bicho", 4) - 0.2: put(sfx, tone(220 + 40 * (i % 3), 0.06, 40, (1, 0.4)), x, 0.2); footstep(x, 0.3); x += 0.085; i += 1
fb = wt("foda", "bicho", 4); whoosh(fb - 0.15, 0.3, 0.4); ff = wt("foda", "foda", 4.6); put(sfx, sweep(1500, 600, 0.25, 4), ff - 0.05, 0.2); tick(ff + 0.22, 0.6, 3200); shing(ff + 0.22, 0.3)
impact(ff + 0.24, 1.0); chord(ff + 0.24, (130.8, 196, 261.6, 329.6, 392), 2.6, 0.13)
os_ = S["outro"]; whoosh(os_, 0.5, 0.6); pop(os_ + 0.15, 500, 0.4); ol = wt("outro", "língua", 1)
for i in range(8): put(sfx, sweep(260 + 40 * (i % 2), 180, 0.05, 20), ol + 0.1 + i * 0.065, 0.3)
whoosh(P2["outro"], 0.3, 0.4); pop(P2["outro"] + 0.05, 650, 0.45); orr = wt("outro", "respeito", 4)
for i in range(3): tick(orr + i * 0.28, 0.3, 1500)
ding(TOTAL - 1.2, 1318, 0.3); ding(TOTAL - 1.05, 1976, 0.25)

sfx = rev(sfx, 0.12, 0.7, 6)
nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1: nar = nar.mean(1)
if sr != SR: nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
vb = np.zeros(n); put(vb, nar, OFF, 1.0); vb /= np.abs(vb).max() / 0.9
duck = 1 - 0.68 * np.clip(lp(np.abs(vb), 4800) / 0.04, 0, 1)
mus *= np.clip((TOTAL - t) / 0.6, 0, 1)
SFXG = 0.24
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

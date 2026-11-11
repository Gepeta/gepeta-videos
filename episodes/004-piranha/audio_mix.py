"""Trilha tensa + efeitos + narração do episódio da piranha."""
import json, numpy as np, soundfile as sf

SR = 48000
TL = json.load(open("timeline.json"))
total = TL["total"]; OFF = TL.get("offset", 0.3)
n = int(SR * (total + 0.2)); rng = np.random.default_rng(5); t = np.arange(n) / SR

def put(buf, sig, at, g=1.0):
    i = int(at * SR); j = min(n, i + len(sig))
    if j > i and i >= 0: buf[i:j] += sig[: j - i] * g

def env(dur, a=0.01, r=0.3):
    k = np.arange(int(SR * dur)) / SR
    return np.minimum(1, k / a) * np.exp(-k / r)

def pluck(f, dur=0.5, decay=6):
    k = np.arange(int(SR * dur)) / SR
    return (np.sin(2*np.pi*f*k) + 0.35*np.sin(4*np.pi*f*k)) * np.exp(-k*decay)

shots = []
for p in TL["phrases"]:
    if not shots or shots[-1][0] != p["shot"]: shots.append((p["shot"], p["start"]))
S = dict(shots)
words = [(w[0], w[2]) for p in TL["phrases"] for w in p["words"]]
def wt(shot, pre):
    st = S[shot]; nxt = [s for _, s in shots if s > st]; en = nxt[0] if nxt else total
    for a, w in words:
        if st <= a < en and w.lower().startswith(pre): return a
    return st

# ---------------------------------------------------------------- trilha: pulso tenso até a virada, depois mais leve
mus = np.zeros(n); beat = 0.42; tt = 0.0; b = 0
twist = S["segredo"]; calm = S["calma"]
while tt < total - 0.8:
    tense = tt < twist
    root = [110, 110, 98, 103.8][(b // 8) % 4] if tense else [130.8, 146.8, 123.5, 110][(b // 8) % 4]
    if b % 2 == 0: put(mus, pluck(root / 2, 0.38, 7), tt, 0.6)
    if tense and not (calm <= tt < S["pe"]):
        put(mus, pluck(root * 2 * (1.5 if b % 4 == 3 else 1), 0.22, 12), tt + 0.21, 0.18)
    else:
        put(mus, pluck(root * [2, 2.5, 3][b % 3], 0.4, 6), tt + (0.21 if b % 2 else 0), 0.16)
    if b % 4 == 2: put(mus, rng.normal(0, 1, int(SR*0.05)) * env(0.05, 0.001, 0.012), tt, 0.12)
    b += 1; tt += beat
# silêncio curto antes da virada
mus *= 1 - 0.85 * np.exp(-((t - twist) / 0.6) ** 2)
mus *= np.clip((total - t) / 1.0, 0, 1)

sfx = np.zeros(n)
def whoosh(at, d=0.35, g=0.16):
    w = np.convolve(rng.normal(0, 1, int(SR*d)), np.ones(30)/30, "same"); k = np.arange(len(w))/len(w)
    put(sfx, w * np.sin(np.pi*k)**2, at - d*0.6, g)
def splash(at, d=1.1, g=0.9):
    w = rng.normal(0, 1, int(SR*d)); k = np.arange(len(w))/SR
    w = np.convolve(w, np.ones(6)/6, "same") * np.exp(-k*3.2) * np.minimum(1, k/0.005)
    put(sfx, w, at, g)
    lo = np.sin(2*np.pi*np.cumsum(90 - 50*k/d)/SR) * np.exp(-k*5); put(sfx, lo, at, g*0.8)
def bubbles(at, cnt=10, g=0.22):
    for i in range(cnt):
        d = 0.08; k = np.arange(int(SR*d))/SR; f = rng.uniform(500, 1400)*(1+k*12)
        put(sfx, np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*40), at + i*rng.uniform(0.03, 0.09), g)
def snap(at, g=0.6):
    d = 0.09; k = np.arange(int(SR*d))/SR
    put(sfx, (rng.normal(0, 1, len(k))*0.7 + np.sin(2*np.pi*1800*k)) * np.exp(-k*70), at, g)
    put(sfx, np.sin(2*np.pi*np.cumsum(140 - 60*k/d)/SR) * np.exp(-k*30), at, g*0.8)
def bark(at, g=0.7):
    d = 0.16; k = np.arange(int(SR*d))/SR
    f = 160 + 60*np.sin(np.pi*k/d)
    tone = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)) * 0.5 + np.sin(2*np.pi*np.cumsum(f)/SR)
    put(sfx, tone * np.sin(np.pi*k/d) ** 0.6, at, g)
def ding(at, ok=True, g=0.25):
    for i, f in enumerate([784, 1046] if ok else [330, 247]):
        put(sfx, pluck(f, 0.4, 7 if ok else 9), at + i*0.08, g)
def sparkle(at, g=0.14):
    for i, f in enumerate([1318, 1568, 1976, 2637]): put(sfx, pluck(f, 0.5), at + i*0.06, g)
def lowtone(at, g=0.4):
    d = 2.0; k = np.arange(int(SR*d))/SR
    put(sfx, (np.sin(2*np.pi*73*k) + 0.4*np.sin(2*np.pi*110*k)) * np.minimum(1, k/0.2) * np.exp(-k*1.1), at, g)

for name, st in shots[1:]: whoosh(st)
splash(0.3); bubbles(0.45, 16, 0.25)
for i in range(6): splash(S["erro"] + i*0.45 + 0.1, 0.35, 0.28)
ding(S["erro"] + 0.15, False); ding(S["calma"] + 0.15, True)
snap(wt("pe", "belisc")); sparkle(wt("especies", "duas"), 0.16)
lowtone(twist); bubbles(S["predadores"], 8, 0.18); splash(wt("predadores", "bigu") - 0.15, 0.5, 0.35)
bubbles(S["estresse"] + 0.3, 14, 0.14)
whoosh(wt("cagao", "cag"), 0.3, 0.3)
for p in ("morde", "força", "trinta", "forte"):
    st = S["mordida"]
    for a, w in words:
        if a >= st and a < S["latido"] and w.lower().startswith(p): snap(a + 0.05, 0.7)
lt = wt("latido", "late"); b2 = [a for a, w in words if a >= S["latido"] and a < S["saida"] and w.lower().startswith("latido")]
bark(lt + 0.05); 
if b2: bark(b2[0] + 0.05); bark(b2[0] + 0.85)
bubbles(total - 2.4, 10, 0.16)

nar, sr = sf.read("audio/narr_el.wav")
if nar.ndim > 1: nar = nar.mean(1)
if sr != SR: nar = np.interp(np.arange(int(len(nar) * SR / sr)) / SR, np.arange(len(nar)) / sr, nar)
nb = np.zeros(n); put(nb, nar, OFF, 1.0)
envv = np.convolve(np.abs(nb), np.ones(4800)/4800, "same")
duck = 1 - 0.58 * np.clip(envv / 0.05, 0, 1)
mix = nb + mus * 0.16 * duck + sfx * 0.5 * (0.45 + 0.55 * duck)
mix /= np.abs(mix).max() / 0.95
sf.write("audio/mix.wav", mix, SR)
print("mix ok", round(total, 2), "s")

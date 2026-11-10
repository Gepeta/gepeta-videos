#!/usr/bin/env python3
"""
Converte o alinhamento de caracteres do ElevenLabs no timeline.json que o
motor de render consome.

Uso:
    python3 align_to_timeline.py <roteiro.py> <align.json> <narr.mp3> <saida timeline.json> [offset]

offset (padrao 0.3s) e o silencio no inicio do video antes da primeira palavra.

O roteiro e uma lista P de (shot, legenda, falado|None). O texto enviado ao
ElevenLabs e exatamente ' '.join(falado or legenda) com espacos normalizados,
entao os offsets de cada frase no texto completo sao conhecidos e o tempo de
cada frase vem direto do alinhamento - sem estimativa.

Dentro da frase: quando a legenda e igual ao texto falado, cada palavra recebe
o tempo exato dos seus caracteres. Quando diferem (numeros escritos em
extenso para a narracao, "1.200" vs "mil e duzentas"), as palavras da legenda
sao distribuidas proporcionalmente dentro da janela exata da frase.
"""

import importlib.util
import json
import os
import subprocess
import sys


def load_roteiro(path):
    spec = importlib.util.spec_from_file_location("roteiro_mod", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["roteiro_mod"] = mod
    spec.loader.exec_module(mod)
    return mod.P


def norm(s):
    return " ".join(s.split())


def audio_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def char_times(align):
    a = align.get("alignment") or align
    chars = a["characters"]
    starts = a["character_start_times_seconds"]
    ends = a["character_end_times_seconds"]
    return chars, starts, ends


def span(starts, ends, lo, hi, chars):
    """Janela temporal dos caracteres [lo,hi), ignorando espacos nas pontas."""
    i, j = lo, hi - 1
    while i < hi and chars[i].isspace():
        i += 1
    while j > i and chars[j].isspace():
        j -= 1
    return float(starts[i]), float(ends[j])


def words_exact(caption, starts, ends, chars, lo, hi):
    """Tempo real de cada palavra da legenda (legenda == falado)."""
    words = []
    k = lo
    for w in caption.split():
        while k < hi and chars[k].isspace():
            k += 1
        a = k
        b = min(k + len(w), hi)
        # confere que os caracteres batem; se nao baterem, desiste
        if "".join(chars[a:b]) != w:
            return None
        words.append([round(float(starts[a]), 3), round(float(ends[b - 1]), 3), w])
        k = b
    return words


def words_proportional(caption, t0, t1):
    """Distribui as palavras da legenda na janela da frase, por peso."""
    ws = caption.split()
    weights = [len(w.strip(".,?!…")) + 2 + (4 if w[-1] in ".,?!" else 0) for w in ws]
    total = sum(weights) or 1
    out, t = [], t0
    for w, x in zip(ws, weights):
        d = (t1 - t0) * x / total
        out.append([round(t, 3), round(t + d, 3), w])
        t += d
    return out


def build(roteiro_path, align_path, mp3_path, out_path, offset=0.3):
    offset = float(offset)
    P = load_roteiro(roteiro_path)
    with open(align_path, encoding="utf-8") as fh:
        align = json.load(fh)
    chars, starts, ends = char_times(align)
    joined = "".join(chars)

    spoken = [norm(s or cap) for (_sh, cap, s) in P]
    expected = " ".join(spoken)
    if joined != expected:
        # o ElevenLabs pode normalizar algo; tenta localizar cada frase na sequencia
        print("aviso: texto do alinhamento difere do roteiro; usando busca por frase")

    phrases = []
    cursor = 0
    exact_count = 0
    for i, ((shot, cap, _s), spk) in enumerate(zip(P, spoken)):
        lo = joined.find(spk, cursor)
        if lo < 0:
            raise SystemExit(f"frase {i} nao encontrada no alinhamento: {spk[:40]!r}")
        hi = lo + len(spk)
        cursor = hi
        t0, t1 = span(starts, ends, lo, hi, chars)
        t0 += offset
        t1 += offset
        cap_n = norm(cap)
        words = None
        if cap_n == spk:
            words = words_exact(cap_n, starts, ends, chars, lo, hi)
        if words is None:
            words = words_proportional(cap_n, t0, t1)
        else:
            words = [[round(a + offset, 3), round(b + offset, 3), w] for a, b, w in words]
            exact_count += 1
        phrases.append({
            "i": i,
            "shot": shot,
            "start": round(t0, 3),
            "dur": round(t1 - t0, 3),
            "words": words,
        })

    dur = audio_duration(mp3_path)
    data = {"total": round(dur + offset + 1.2, 3), "offset": round(offset, 3), "phrases": phrases}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)

    print(f"timeline: {len(phrases)} frases, audio {dur:.2f}s, total {data['total']}s")
    print(f"palavras com tempo exato em {exact_count}/{len(phrases)} frases")
    prev_end = None
    for p in phrases:
        gap = "" if prev_end is None else f"  gap {p['start'] - prev_end:+.2f}s"
        print(f"  {p['i']:2d} {p['shot']:<9} {p['start']:6.2f} +{p['dur']:5.2f}{gap}")
        prev_end = p["start"] + p["dur"]
    return data


if __name__ == "__main__":
    if len(sys.argv) not in (5, 6):
        sys.exit(__doc__)
    build(*sys.argv[1:])

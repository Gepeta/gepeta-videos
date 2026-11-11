#!/usr/bin/env python3
"""
Abre respiros na narração antes de cada capítulo, para o cartão de título
do formato B aparecer sem atropelar a voz.

Uso:
    python3 insert_pauses.py <timeline.json> <narr.wav> <saida_timeline.json> \
        <saida_narr.wav> <pausa_s> <shot1,shot2,...>

O timeline de entrada é o que sai de align_to_timeline.py (com offset). A pausa
é inserida no meio do silêncio entre a última frase do capítulo anterior e a
primeira do novo, e tudo que vem depois é empurrado. O timeline de saída ganha
a lista "chapters" com a janela de cada cartão.
"""
import json
import sys

import numpy as np
import soundfile as sf


def main(tl_in, wav_in, tl_out, wav_out, pause, shots_csv):
    pause = float(pause)
    want = set(s for s in shots_csv.split(",") if s)
    tl = json.load(open(tl_in, encoding="utf-8"))
    off = float(tl.get("offset", 0.3))
    audio, sr = sf.read(wav_in)
    if audio.ndim > 1:
        audio = audio.mean(1)

    ph = tl["phrases"]
    cuts = []  # (tempo no timeline original, shot)
    for i in range(1, len(ph)):
        if ph[i]["shot"] != ph[i - 1]["shot"] and ph[i]["shot"] in want:
            prev_end = ph[i - 1]["start"] + ph[i - 1]["dur"]
            cuts.append(((prev_end + ph[i]["start"]) / 2.0, ph[i]["shot"]))

    def shift(t):
        return t + pause * sum(1 for c, _ in cuts if t >= c)

    # áudio: costura com silêncio nos pontos de corte
    pieces, last = [], 0
    for c, _ in cuts:
        k = int(round((c - off) * sr))
        k = max(last, min(len(audio), k))
        pieces.append(audio[last:k])
        pieces.append(np.zeros(int(round(pause * sr))))
        last = k
    pieces.append(audio[last:])
    sf.write(wav_out, np.concatenate(pieces), sr)

    for p in ph:
        p["start"] = round(shift(p["start"]), 3)
        p["words"] = [[round(shift(a), 3), round(shift(b), 3), w] for a, b, w in p["words"]]
    chapters = []
    for n, (c, shot) in enumerate(cuts):
        s0 = c + pause * n
        chapters.append({"shot": shot, "start": round(s0, 3), "end": round(s0 + pause, 3)})
    tl["chapters"] = chapters
    tl["total"] = round(tl["total"] + pause * len(cuts), 3)
    json.dump(tl, open(tl_out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(cuts)} pausas de {pause}s; total {tl['total']}s")
    for ch in chapters:
        print(f"  cartão {ch['shot']:<10} {ch['start']:6.2f} -> {ch['end']:6.2f}")


if __name__ == "__main__":
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    main(*sys.argv[1:])

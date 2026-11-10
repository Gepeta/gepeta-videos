#!/usr/bin/env python3
"""
Agente local da fabrica Gepeta (roda no PC Ubuntu do Lucas).

Por que ele existe: o ambiente de nuvem onde o Claude renderiza os videos nao tem
permissao de rede para falar com a API do ElevenLabs nem para dar push no GitHub.
Este agente, rodando na sua maquina, faz essas duas pontas. Ele nao edita video,
nao renderiza nada e nao pede nada de voce: so le arquivos de tarefa e devolve o
resultado na mesma pasta.

A chave da API nunca sai daqui: e lida de config.env, nesta pasta.

Instalacao (uma vez, com pm2 que voce ja tem):
    cd ~/Documents/fabrica/videos
    pm2 start gepeta_agent.py --name gepeta --interpreter python3 -- --watch
    pm2 save

Verificar:   pm2 logs gepeta
Parar:       pm2 stop gepeta

Como funciona: a cada 30s olha a pasta jobs/ procurando *.job.json.
Tipos de tarefa:
  {"kind":"tts",  "id":"002-x", "text":"...", "voice":"<id>"}        -> out/<id>/narr.mp3 + align.json
  {"kind":"push", "repo":"/caminho/repo", "message":"...",            -> git add/commit/push
                  "files":["videos/x.mp4"]}
  {"kind":"probe"}                                                    -> out/probe/result.json (diagnostico)
Para cada tarefa ele escreve jobs/<nome>.done.json com o resultado e renomeia a
tarefa para .job.done para nao repetir.
"""

import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS = os.path.join(HERE, "jobs")
OUT = os.path.join(HERE, "out")
CFG = os.path.join(HERE, "config.env")
API = "https://api.elevenlabs.io/v1"
MODEL = "eleven_multilingual_v2"
POLL_SECONDS = 30


def log(*a):
    print(time.strftime("[%H:%M:%S]"), *a, flush=True)


def load_cfg():
    cfg = {}
    if not os.path.exists(CFG):
        raise SystemExit("config.env nao encontrado em " + CFG)
    with open(CFG, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    if not cfg.get("ELEVENLABS_API_KEY"):
        raise SystemExit("ELEVENLABS_API_KEY ausente em config.env")
    return cfg


def el_request(path, key, payload=None, method="GET"):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("xi-api-key", key)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:600]
        return e.code, {"error": body}
    except Exception as e:  # rede caiu, DNS, etc
        return 0, {"error": repr(e)}


def job_tts(job, cfg):
    key = cfg["ELEVENLABS_API_KEY"]
    voice = job.get("voice") or cfg.get("ELEVENLABS_VOICE_ID")
    text = job["text"]
    jid = job.get("id", "sem-id")
    dest = os.path.join(OUT, jid)
    os.makedirs(dest, exist_ok=True)

    settings = job.get("voice_settings") or {
        "stability": 0.4,
        "similarity_boost": 0.8,
        "style": 0.35,
        "use_speaker_boost": True,
    }
    payload = {
        "text": text,
        "model_id": job.get("model_id", MODEL),
        "voice_settings": settings,
    }
    log(f"tts {jid}: {len(text)} chars, voz {voice}")
    status, body = el_request(
        f"/text-to-speech/{voice}/with-timestamps", key, payload, "POST"
    )
    if status != 200:
        return {"ok": False, "status": status, "detail": body.get("error", "")[:400]}

    mp3 = os.path.join(dest, "narr.mp3")
    with open(mp3, "wb") as fh:
        fh.write(base64.b64decode(body["audio_base64"]))
    align = {
        "alignment": body.get("alignment"),
        "normalized_alignment": body.get("normalized_alignment"),
    }
    with open(os.path.join(dest, "align.json"), "w", encoding="utf-8") as fh:
        json.dump(align, fh, ensure_ascii=False)

    chars = (body.get("alignment") or {}).get("characters") or []
    ends = (body.get("alignment") or {}).get("character_end_times_seconds") or [0]
    return {
        "ok": True,
        "mp3": mp3,
        "bytes": os.path.getsize(mp3),
        "chars": len(chars),
        "duration": round(float(ends[-1]), 3),
        "voice": voice,
    }


def job_push(job, cfg):
    repo = job["repo"]
    files = job.get("files") or ["-A"]
    msg = job.get("message", "atualiza videos")
    if not os.path.isdir(os.path.join(repo, ".git")):
        return {"ok": False, "detail": repo + " nao e um repo git"}

    def run(*args):
        p = subprocess.run(
            args, cwd=repo, capture_output=True, text=True, timeout=600
        )
        return p.returncode, (p.stdout + p.stderr)[-800:]

    steps = []
    for f in files:
        steps.append(("add " + f,) + run("git", "add", f))
    code, out = run("git", "commit", "-m", msg)
    steps.append(("commit", code, out))
    if code != 0 and "nothing to commit" not in out:
        return {"ok": False, "steps": steps}
    code, out = run("git", "push")
    steps.append(("push", code, out))
    return {"ok": code == 0, "steps": steps}


def job_probe(job, cfg):
    key = cfg["ELEVENLABS_API_KEY"]
    status, sub = el_request("/user/subscription", key)
    st2, voices = el_request("/voices", key)
    names = []
    if st2 == 200:
        names = [
            {"id": v.get("voice_id"), "name": v.get("name")}
            for v in (voices.get("voices") or [])[:40]
        ]
    return {
        "ok": status == 200,
        "subscription_status": status,
        "tier": sub.get("tier"),
        "limit": sub.get("character_limit"),
        "used": sub.get("character_count"),
        "voices_status": st2,
        "voices": names,
        "git": subprocess.run(
            ["git", "--version"], capture_output=True, text=True
        ).stdout.strip(),
    }


HANDLERS = {"tts": job_tts, "push": job_push, "probe": job_probe}


def process_once(cfg):
    os.makedirs(JOBS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    pending = sorted(f for f in os.listdir(JOBS) if f.endswith(".job.json"))
    for name in pending:
        path = os.path.join(JOBS, name)
        try:
            with open(path, encoding="utf-8") as fh:
                job = json.load(fh)
        except Exception as e:
            log("tarefa ilegivel", name, e)
            os.rename(path, path + ".bad")
            continue
        kind = job.get("kind", "tts")
        fn = HANDLERS.get(kind)
        if not fn:
            result = {"ok": False, "detail": "tipo desconhecido: " + kind}
        else:
            try:
                result = fn(job, cfg)
            except Exception as e:
                result = {"ok": False, "detail": repr(e)}
        result["kind"] = kind
        result["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        done = os.path.join(JOBS, re.sub(r"\.job\.json$", "", name) + ".done.json")
        with open(done, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1)
        os.rename(path, path + ".done")
        log(name, "->", "ok" if result.get("ok") else "FALHOU", result.get("detail", ""))
    return len(pending)


def main():
    cfg = load_cfg()
    watch = "--watch" in sys.argv
    log("agente gepeta iniciado", "(watch)" if watch else "(uma passada)")
    n = process_once(cfg)
    log(n, "tarefa(s) processada(s)")
    while watch:
        time.sleep(POLL_SECONDS)
        try:
            process_once(cfg)
        except Exception as e:
            log("erro no ciclo:", repr(e))


if __name__ == "__main__":
    main()

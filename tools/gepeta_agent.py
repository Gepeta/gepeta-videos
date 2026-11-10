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
    pm2 start gepeta_agent.py --name gepeta --interpreter python3 --no-watch
    pm2 save

NUNCA inicie com a flag --watch do pm2: o agente escreve arquivos nesta mesma
pasta, o pm2 enxerga a mudanca, reinicia o processo no meio do trabalho e a
tarefa pendente e reenviada - o que vira cobranca duplicada na fal.
Por isso o modo continuo agora e o padrao e nao precisa de flag nenhuma.

Verificar:   pm2 logs gepeta
Parar:       pm2 stop gepeta

Como funciona: a cada 30s olha a pasta jobs/ procurando *.job.json.
Tipos de tarefa:
  {"kind":"tts",  "id":"002-x", "text":"...", "voice":"<id>"}        -> out/<id>/narr.mp3 + align.json
  {"kind":"fal",  "id":"tk-001-a", "model":"fal-ai/...",             -> out/<id>/<arquivos gerados>
                  "input":{"prompt":"...","duration":"5"}}
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
FAL_QUEUE = "https://queue.fal.run"
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


def http_json(url, headers, payload=None, method="GET", timeout=120):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode()
            return r.status, (json.loads(body) if body.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:600]}
    except Exception as e:
        return 0, {"error": repr(e)}


def collect_urls(obj, found=None):
    """Acha toda chave 'url' em qualquer profundidade do JSON de resposta."""
    found = [] if found is None else found
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "url" and isinstance(v, str) and v.startswith("http"):
                found.append(v)
            else:
                collect_urls(v, found)
    elif isinstance(obj, list):
        for v in obj:
            collect_urls(v, found)
    return found


def job_fal(job, cfg):
    """Gera midia na fal.ai. O modelo e os parametros vem da tarefa, entao
    trocar de modelo nao exige mexer neste arquivo."""
    key = cfg.get("FAL_KEY")
    if not key:
        return {"ok": False, "detail": "FAL_KEY ausente em config.env"}
    model = job.get("model") or cfg.get("FAL_MODEL")
    if not model:
        return {"ok": False, "detail": "sem modelo: passe 'model' na tarefa ou FAL_MODEL em config.env"}

    jid = job.get("id", "sem-id")
    dest = os.path.join(OUT, jid)
    os.makedirs(dest, exist_ok=True)
    headers = {"Authorization": "Key " + key}

    log(f"fal {jid}: {model}")
    status, body = http_json(f"{FAL_QUEUE}/{model}", headers, job.get("input", {}), "POST")
    if status not in (200, 201, 202):
        return {"ok": False, "status": status, "detail": str(body.get("error", body))[:400]}

    log(f"  fal {jid}: aceito, aguardando a fila")
    status_url = body.get("status_url")
    response_url = body.get("response_url")
    req_id = body.get("request_id")
    if not status_url:
        return {"ok": False, "detail": "resposta sem status_url: " + str(body)[:300]}

    deadline = time.time() + float(job.get("timeout_seconds", 900))
    state = "IN_QUEUE"
    while time.time() < deadline:
        time.sleep(float(job.get("poll_seconds", 5)))
        st, sb = http_json(status_url, headers)
        state = sb.get("status", "?")
        if state == "COMPLETED":
            log(f"  fal {jid}: pronto, baixando")
            break
        if state in ("FAILED", "ERROR", "CANCELLED"):
            return {"ok": False, "detail": f"fal retornou {state}: " + str(sb)[:400]}
        if st == 0:
            log(f"  fal {jid}: erro de rede ao consultar, tentando de novo")
    else:
        return {"ok": False, "detail": f"tempo esgotado, ultimo estado {state}", "request_id": req_id}

    st, result = http_json(response_url or status_url, headers)
    if st != 200:
        return {"ok": False, "status": st, "detail": str(result)[:400]}

    saved = []
    for i, url in enumerate(collect_urls(result)):
        ext = os.path.splitext(url.split("?")[0])[1] or ".bin"
        path = os.path.join(dest, f"{i:02d}{ext}")
        try:
            req = urllib.request.Request(url)
            got = 0
            with urllib.request.urlopen(req, timeout=300) as r, open(path, "wb") as fh:
                while True:
                    chunk = r.read(262144)
                    if not chunk:
                        break
                    fh.write(chunk)
                    fh.flush()
                    got += len(chunk)
            log(f"  baixado {os.path.basename(path)}: {got} bytes")
            saved.append({"path": path, "bytes": got})
        except Exception as e:
            log(f"  FALHA ao baixar {url[:80]}: {e!r}")
            saved.append({"path": path, "error": repr(e)})

    with open(os.path.join(dest, "fal_response.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)

    return {"ok": bool(saved), "model": model, "request_id": req_id,
            "files": saved, "detail": "" if saved else "resposta sem arquivo"}


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
        "fal_key_presente": bool(cfg.get("FAL_KEY")),
        "fal_model": cfg.get("FAL_MODEL", ""),
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


HANDLERS = {"tts": job_tts, "fal": job_fal, "push": job_push, "probe": job_probe}


def process_once(cfg):
    os.makedirs(JOBS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    pending = sorted(f for f in os.listdir(JOBS) if f.endswith(".job.json"))
    for name in pending:
        path = os.path.join(JOBS, name)
        # reserva a tarefa antes de executar: se o processo morrer no meio, ela
        # NAO volta para a fila e nao gera cobranca duplicada na fal
        running = path + ".running"
        try:
            os.rename(path, running)
        except OSError as e:
            log("nao consegui reservar", name, e)
            continue
        path = running
        try:
            with open(path, encoding="utf-8") as fh:
                job = json.load(fh)
        except Exception as e:
            log("tarefa ilegivel", name, e)
            os.rename(path, os.path.join(JOBS, name + ".bad"))
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
        os.rename(path, os.path.join(JOBS, name + ".done"))
        log(name, "->", "ok" if result.get("ok") else "FALHOU", result.get("detail", ""))
    return len(pending)


def single_instance():
    """Impede duas copias do agente rodando ao mesmo tempo."""
    lock = os.path.join(HERE, ".agent.pid")
    if os.path.exists(lock):
        try:
            old = int(open(lock).read().strip())
            os.kill(old, 0)
            raise SystemExit(f"ja existe um agente rodando (pid {old}); saindo")
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    with open(lock, "w") as fh:
        fh.write(str(os.getpid()))


def main():
    cfg = load_cfg()
    single_instance()
    once = "--once" in sys.argv
    log("agente gepeta iniciado", "(uma passada)" if once else "(continuo)")
    n = process_once(cfg)
    log(n, "tarefa(s) processada(s)")
    while not once:
        time.sleep(POLL_SECONDS)
        try:
            process_once(cfg)
        except Exception as e:
            log("erro no ciclo:", repr(e))


if __name__ == "__main__":
    main()

"""Gera narracao no GitHub Actions (substitui o agente do PC para TTS).
Le tts-jobs/*.job.json sem resultado e grava tts-out/<id>/{narr.mp3,align.json,result.json}.
Chave em ELEVENLABS_API_KEY (segredo do repositorio). Nunca imprime a chave."""
import base64, glob, json, os, sys, urllib.request, urllib.error

API = "https://api.elevenlabs.io/v1"
KEY = os.environ.get("ELEVENLABS_API_KEY", "")
DEFAULT_VOICE = os.environ.get("ELEVENLABS_VOICE_ID") or "7lu3ze7orhWaNeSPowWx"

def tts(job):
    voice = job.get("voice") or DEFAULT_VOICE
    payload = {
        "text": job["text"],
        "model_id": job.get("model_id", "eleven_multilingual_v2"),
        "voice_settings": job.get("voice_settings") or {
            "stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True},
    }
    req = urllib.request.Request(f"{API}/text-to-speech/{voice}/with-timestamps",
                                 data=json.dumps(payload).encode(), method="POST")
    req.add_header("xi-api-key", KEY)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return 200, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8", "replace")[:400]}

def main():
    if not KEY:
        sys.exit("segredo ELEVENLABS_API_KEY nao configurado no repositorio")
    fail = False
    for path in sorted(glob.glob("tts-jobs/*.job.json")):
        job = json.load(open(path, encoding="utf-8"))
        jid = job.get("id") or os.path.basename(path).split(".")[0]
        dest = os.path.join("tts-out", jid)
        if os.path.exists(os.path.join(dest, "result.json")):
            continue
        os.makedirs(dest, exist_ok=True)
        st, body = tts(job)
        if st != 200:
            res = {"ok": False, "status": st, "detail": body.get("error", "")}
            fail = True
        else:
            open(os.path.join(dest, "narr.mp3"), "wb").write(base64.b64decode(body["audio_base64"]))
            json.dump({"alignment": body.get("alignment"),
                       "normalized_alignment": body.get("normalized_alignment")},
                      open(os.path.join(dest, "align.json"), "w", encoding="utf-8"), ensure_ascii=False)
            ends = (body.get("alignment") or {}).get("character_end_times_seconds") or [0]
            res = {"ok": True, "duration": round(float(ends[-1]), 3)}
        json.dump(res, open(os.path.join(dest, "result.json"), "w"))
        print(jid, json.dumps(res))
    sys.exit(1 if fail else 0)

main()

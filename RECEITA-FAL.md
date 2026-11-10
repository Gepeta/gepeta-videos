# Receita do vídeo realista (fal.ai) — SOB DEMANDA, nunca automático

Este formato **não entra na rotina diária**. Ele só é produzido quando o Lucas
pedir explicitamente, porque cada vídeo gasta crédito de verdade na fal.
O vídeo diário automático é sempre o do motor 3D (ver `PIPELINE.md`).

Referência pronta: `episodes/tk001-coxinhara/` e `videos/tk001-coxinhara.mp4`.

## Quanto custa

| Item | Preço | Num vídeo de ~13s |
| --- | --- | --- |
| Kling v3 standard, áudio off | $0,084/s | 3 clipes de 5s = $1,26 |
| Narração ElevenLabs | cota do plano | ~240 caracteres |

Com retrabalho (1 ou 2 clipes refeitos), conte **$1,70 a $2,50 por vídeo**.
Wan 2.5 a $0,05/s é a alternativa barata, ainda não testada.
Confira o saldo em fal.ai → Settings → Usage antes de começar.

## O que faz o formato funcionar

Criatura **inventada**, nunca personagem que já existe — as contas que crescem
nesse nicho propõem bicho novo. Híbrido absurdo de duas coisas reconhecíveis
(coxinha + capivara), com nome que gruda. Abre já com a criatura em cena, sem
introdução. Câmera tremida de celular, que é o que faz parecer filmagem real.
Legenda palavra a palavra. 12 a 15 segundos, curto para dar loop. A legenda do
post é reação, não descrição: minúscula, sem ponto final, como se comenta.

Nada de pessoa real, marca ou personagem protegido — as mesmas regras do
`PIPELINE.md` valem aqui.

## Passo a passo

### 1. Roteiro
Três planos de 5s que contem uma microhistória: apresentação da criatura,
ela fazendo algo impossível, e o remate numa cena cotidiana brasileira.
Narração de 35 a 50 palavras (~240 caracteres, ~12s).

### 2. Gerar os clipes
Uma tarefa por plano em `/home/uchida/Documents/fabrica/videos/jobs/`:

```json
{"kind": "fal", "id": "tkNNN-c1",
 "model": "fal-ai/kling-video/v3/standard/text-to-video",
 "input": {"prompt": "<ver abaixo>", "duration": 5, "aspect_ratio": "9:16",
           "generate_audio": false,
           "negative_prompt": "text, watermark, logo, subtitles, blurry, distorted, extra limbs"},
 "timeout_seconds": 600}
```

O prompt precisa repetir a descrição da criatura **inteira em todos os planos**,
senão ela muda de aparência entre clipes. Sempre terminar com o bloco de
estilo: `Photorealistic handheld phone footage, vertical 9:16, documentary
style, absurd and funny.`

Cada clipe leva ~2 minutos. O agente processa um de cada vez.

### 3. Narração
```json
{"kind": "tts", "id": "tkNNN-voz", "text": "<narração completa>"}
```

### 4. Montagem
```bash
printf "file 'c1.mp4'\nfile 'c2.mp4'\nfile 'c3.mp4'\n" > lista.txt
ffmpeg -y -f concat -safe 0 -i lista.txt -c copy juntos.mp4
```
Legenda: montar um `.ass` a partir do `align.json` (uma palavra por evento,
Poppins Bold 78, contorno 6, palavra-chave em amarelo `&H0000E5FF`).
Trilha: base rítmica procedural de ~96 bpm, bem baixa (peso 0,22 na mixagem).

```bash
ffmpeg -y -i juntos.mp4 -i voz.mp3 -i base.wav -filter_complex \
 "[0:v]subtitles=legenda.ass:fontsdir=/usr/share/fonts/truetype/google-fonts[v];\
  [1:a]adelay=350|350,apad[voz];[2:a]apad[bg];\
  [voz][bg]amix=inputs=2:weights=1 0.22:duration=first:normalize=0,\
  loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.97[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p \
 -c:a aac -b:a 192k -t <fim da narração + 1s> saida.mp4
```

Cortar logo depois da última palavra: sobra de silêncio no fim mata o loop.

### 5. Publicar
Commit em `videos/`, conferir que a URL do raw responde 200, e agendar no
Metricool **só para o TikTok**, com `tiktokData.isAigc: true` e
`tiktokData.title` preenchido.

# Fábrica Gepeta — rotina diária

> **O vídeo diário é sempre feito com o motor 3D** (Three.js, estilo do
> episódio do baiacu) e vai para as três redes: YouTube Shorts, TikTok e
> Instagram. O formato realista gerado na fal.ai **não é automático** — só
> sai quando o Lucas pedir. A receita dele está em `RECEITA-FAL.md`.

Este arquivo é a instrução completa de uma rodada. Uma sessão nova do Claude
abre o repositório, lê isto e produz o vídeo do dia sozinha.

**Publicação: todo dia às 15h (America/Sao_Paulo). Disparo da produção: 8h34.**

## Peças fixas

| Peça | Onde |
| --- | --- |
| Repositório | `https://github.com/Gepeta/gepeta-videos` (público) |
| Marca no Metricool | `blogId` 8005368, label `gepeta` |
| Redes | TikTok `gepeta`, Instagram `gepet.a`, YouTube `UCz-SPlC91uV6j_2J0s-vXRg` |
| Voz | ElevenLabs `7lu3ze7orhWaNeSPowWx` (Lucas), modelo `eleven_multilingual_v2` |
| Agente local | PC `uchida-ubuntu`, pasta `/home/uchida/Documents/fabrica/videos` |
| Hospedagem do vídeo | `raw.githubusercontent.com/Gepeta/gepeta-videos/main/videos/<id>.mp4` |

O ambiente de nuvem **não alcança a API do ElevenLabs nem faz push autenticado
sem o app do GitHub**. A narração sai pelo agente local; o push sai da nuvem.

## Os passos

### 1. Achar o assunto do dia
O canal fala do que a internet está comentando **hoje**. Pesquise antes de
decidir, sempre, e em mais de um lugar:

- Reddit: o que está subindo em r/all, r/todayilearned, r/interestingasfuck,
  r/NatureIsFuckingLit, r/Damnthatsinteresting, r/brasil.
- X: assuntos do momento, principalmente os que viraram piada.
- Busca na web pelo que explodiu nas últimas 24 a 48 horas.

Procure o que serve ao formato: uma **curiosidade** com um fato surpreendente
dentro, visual o bastante para virar cena 3D low-poly em 50 segundos, e que
aceite uma piada de duplo sentido na abertura. O assunto pode vir da internet
do dia, mas o vídeo é sempre uma curiosidade no modelo do baiacu — não é
comentário sobre a treta em si. Um assunto só com gente falando, sem fato
e sem imagem possível, não vira vídeo bom — descarte e pegue o próximo.

Se nada do dia servir, use `topics.json`: é a lista reserva de curiosidades de
bicho, no formato que já funcionou. Pegue o primeiro com `"used": false`.
Nunca publique sem assunto; a reserva existe exatamente para isso.

**O que não entra, por mais que esteja bombando:**
- Pessoa real com nome (político, celebridade, influenciador, criador de caso
  do dia). O canal fala de coisas, bichos e fenômenos, não de gente.
- Personagem de desenho, game, filme ou marca — é material protegido e derruba
  o vídeo nas três plataformas.
- Política, eleição, religião, tragédia recente, crime, doença de alguém.
- Qualquer piada em cima de grupo de pessoas.

A piada do canal é com a expectativa do espectador, nunca com alguém.

### 2. Checar os fatos — passo que não se pula
Trend é boato até se provar o contrário, e a maior parte do que viraliza chega
distorcida. Cada número e cada afirmação do roteiro precisa de fonte confiável
confirmada hoje (publicação científica, universidade, museu, órgão oficial,
veículo sério). Reddit e X são a pista, nunca a fonte.

Se o fato que fez o assunto viralizar for falso, você tem dois caminhos bons:
usar o fato correto, ou fazer o vídeo justamente sobre o engano — o que
costuma render mais. O que não existe é publicar o boato como verdade.

Anote as fontes em `episodes/<id>/fontes.md`.

### 3. Escrever o roteiro
Formato de `roteiro.py`: lista `P` de `(shot, legenda, falado|None)`. O
terceiro campo só existe quando a narração precisa diferir da legenda
(números por extenso: a legenda mostra `1.200`, a narração fala
`mil e duzentas`).

Estrutura que funciona, nesta ordem:
1. **Duplo sentido** (2 frases): uma descrição que soa safada e é inocente.
2. **Virada** (1 frase): `Calma, safado. Tô falando do/da <bicho>.`
3. **Curiosidade forte** logo em seguida, antes que a pessoa role a tela.
4. **Corpo**: 3 a 5 fatos, do mais visual para o mais surpreendente.
5. **Fecho**: uma frase que vira a curiosidade contra o espectador, no tom
   de `Se até o baiacu se esforça, qual é a sua desculpa?`

Alvo: 900 a 1.000 caracteres de narração, que dão 50 a 55 segundos.
Frases curtas. Cada frase é um corte.

### 4. Montar a cena 3D
**Não comece do zero.** Copie o episódio anterior mais parecido (mar, deserto,
floresta, noite) de `episodes/` e troque o bicho e o cenário. `index.html`
expõe `window.renderAt(t)`, `window.TOTAL` e `window.SHOTS`; `render.mjs` não
muda entre episódios.

Regras de enquadramento que já custaram retrabalho:
- Câmera nunca a menos de 6.5 de distância do alvo — `look()` já puxa para
  trás sozinha, mas confira.
- Nada de planta ou pedra entre a câmera e o bicho.
- Um subcorte a cada ~2.3s, com um empurrão de `fov` no corte.
- Legenda de uma palavra, centralizada, palavra-chave em amarelo.

### 5. Narração
Escreva a tarefa em `/home/uchida/Documents/fabrica/videos/jobs/<id>.job.json`
(via `device_commit_files`):

```json
{"kind": "tts", "id": "<id>", "text": "<narração completa, uma linha>"}
```

O agente responde em até ~1 minuto com `jobs/<id>.done.json` e
`out/<id>/narr.mp3` + `align.json`. Traga os dois de volta com
`device_stage_files`.

**Se o PC estiver desligado** (nenhum `.done.json` depois de ~10 minutos de
espera): avise o usuário, agende uma nova tentativa e pare. Não invente a
narração com outra voz — a voz é parte da marca.

### 6. Timeline e render
```bash
python3 tools/align_to_timeline.py episodes/<id>/roteiro.py \
    <align.json> <narr.mp3> episodes/<id>/timeline.json 0.3
ffmpeg -y -i <narr.mp3> -ac 1 -ar 48000 episodes/<id>/audio/narr_el.wav
cd episodes/<id> && python3 audio_mix.py          # trilha + efeitos + voz
node render.mjs preview 0.9,4.6,8.2,...           # 10 a 12 quadros
```
**Olhe os quadros antes do render completo.** Monte um contact sheet com
`montage` e leia a imagem. Corrigir enquadramento depois custa mais 8 minutos.

```bash
node render.mjs video video_el.mp4                 # ~8 min
ffmpeg -y -i video_el.mp4 -i audio/mix.wav -map 0:v -map 1:a -c:v copy \
   -c:a aac -b:a 192k \
   -af "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.97" -shortest \
   ../../videos/<id>.mp4
```

### 7. Publicar
```bash
git add -A && git commit -m "Episodio <id>: <bicho>" && git push
```
Confirme que a URL pública responde 200 antes de agendar.

Depois `createScheduledPost` no Metricool, `blogId` 8005368, data de hoje às
`15:00:00` em `America/Sao_Paulo`, `autoPublish: true`, as três redes, com o
`media` apontando para a URL do raw.

Um único post com as três redes juntas (`tiktok`, `instagram`, `youtube`).

Obrigatório em toda publicação:
- `tiktokData.isAigc: true` **e** `tiktokData.title` (o TikTok recusa sem título)
- `instagramData`: `{"type": "REEL", "isAiGenerated": true}`
- `youtubeData`: `{"type": "short", "madeForKids": false, "isAiGeneratedContent": true}`

A legenda sai do roteiro: a virada, o fato mais forte, a pergunta do fecho e
4 ou 5 hashtags. Título do TikTok e do YouTube escritos separados, cada um
carregando o fato mais surpreendente.

### 8. Fechar
Registre o assunto em `historico.json` (data, assunto, de onde veio). Se usou a
lista reserva, marque `"used": true` em `topics.json`. Faça commit e mande ao
usuário uma mensagem curta: qual foi o tema, o link do planner e qualquer
coisa que tenha dado errado no caminho.

## O que nunca se faz
- Publicar número sem fonte conferida no dia.
- Publicar sem as três marcações de conteúdo gerado por IA.
- Gravar a chave do ElevenLabs em qualquer arquivo do repositório.
- Repetir assunto que já está no `historico.json` dos últimos 30 dias.
- Publicar boato de internet sem ter conferido em fonte séria.
- Fazer vídeo sobre pessoa real com nome, ou em cima de algum grupo.

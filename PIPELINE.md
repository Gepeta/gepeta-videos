# Fábrica Gepeta — rotina diária

> O vídeo diário vai para as três redes: YouTube Shorts, TikTok e Instagram,
> e sai em **um de dois formatos**, sorteado a cada dia (ver "Formato do dia").
> Os dois são renderizados aqui, sem custo de API. O formato realista gerado
> na fal.ai **não é automático** — só sai quando o Lucas pedir. A receita dele
> está em `RECEITA-FAL.md`.

## Padrão de produção (vale para todo vídeo 3D a partir de 12/11/2026)

Definido pelo Lucas depois de olhar os números das três redes. Os formatos A e
C continuam existindo, mas todo vídeo 3D passa a seguir isto:

1. **Abertura**: uma frase que levanta dúvida **e** tem duplo sentido leve
   (modelo: "E se você tivesse 60 centímetros de língua?"). A pergunta aparece
   escrita na tela já no primeiro quadro. Nada de introdução lenta.
2. **A dúvida só fecha no fim**: virada depois do meio ("agora a parte que
   ninguém espera") e pergunta final que pede comentário.
3. **Engraçado**. Palavrão moderado, pelas regras da seção "Palavrão".
4. **Visual**: estilo de blocos arredondados (tipo Roblox) para personagens e
   bichos, com sombra suave, oclusão de ambiente, brilho, grão e vinheta.
   O **Gepeta** (careca, óculos escuros, roupa e tênis pretos) é o personagem
   do canal: abre e fecha o vídeo no corredor de subsolo e faz o papel do
   "você" nos vídeos de "E se".
5. **Edição**: corte ou mudança de plano a cada 2–3 s, cada fato vira um
   elemento na tela (contador, régua, carimbo, raio-x, etiqueta com seta).
6. **Som**: ambiente por cenário, um efeito para cada ação e cada elemento
   que entra na tela, música que muda na virada. A narração manda: o fundo
   fica em torno de −13 dB em relação à voz (o `audio_mix.py` imprime isso).
7. **Legenda**: blocos de até 3 palavras, caixa alta, palavra falada destacada
   em cor (amarelo padrão, vermelho para perigo, verde para número).
8. **O que cada rede prefere**: no TikTok o "E se" rendeu mais; no YouTube
   Shorts, bicho. Junte os dois sempre que der: "E se você…" respondido por
   um bicho, de preferência brasileiro.
9. **Descrição própria por rede** (três posts separados no Metricool):
   TikTok curto, com a pergunta e 4–5 hashtags; YouTube com título de até
   ~60 caracteres começando pela pergunta, descrição com as palavras de busca
   e `#shorts`; Instagram com gancho na primeira linha e pedido de envio
   ("manda pra aquele amigo…"). Palavrão nunca em título ou descrição.

**Kit base: `episodes/006-tamandua/`**. Parta dele: `index.html` já tem o
Gepeta com fala sincronizada (`mouth.json`), o corredor, o cerrado, a função
`makeBigAnt`, raio-x, pós-processamento, legendas e os helpers de tela
(`pill`, `stamp`, `ruler`, `tag`, `hud`). `audio_mix.py` tem os efeitos
prontos. Render (um processo só; dois em paralelo não ganham nada aqui):

```
Q='?s=0.6667&ao=4&as=0.4&env=0' node render.mjs video video.mp4
```

Leva ~1 s por quadro: um vídeo de 70 s sai em 35–45 min. Conte com isso no
horário. Antes do render completo, sempre a folha de prévia.

## Estilo "maquete" e regra de corte por rede (a partir de 13/11/2026)

Pedido do Lucas depois do vídeo do Sol: estilo mais bonito e mais rápido de
renderizar, e duração diferente por rede.

- **Estilo maquete** (kit: `episodes/008-capivara/`, `scene.js` + `build.py`):
  ilha flutuante vista por câmera isométrica, material toon com contorno,
  céu em degradê desenhado em 2D, sem oclusão nem brilho. Render em 1080p
  nativo a ~0,8 s por quadro (um vídeo de 63 s sai em ~25 min). É o estilo
  padrão para vídeo de bicho. O kit `006-tamandua` (corredor + Gepeta) fica
  para quando o roteiro pedir o Gepeta como protagonista.
- **Um roteiro, dois cortes**: a parte A (20–30 s) fecha sozinha, com chamada
  própria, e vira o **YouTube Shorts e o Reels**. A + B (parte extra que
  começa com "mas calma…") passa de 61 s e vai para o **TikTok**. Renderiza
  uma vez e corta com ffmpeg no início da parte B.
- **Um vídeo por dia.** Em 11 e 12/11 o segundo vídeo do dia saiu muito pior
  (piranha: 39 views no TikTok; Sol: 12 views no YouTube, 0% de feed).

## Formato do dia

Sorteie no começo da rodada, com peso igual, e registre qual saiu no
`historico.json`. Se os **dois últimos** episódios foram do mesmo formato,
use o outro — o sorteio não pode virar sequência.

**A — Curiosidade 3D** (motor Three.js, estilo baiacu/polvo)
Um bicho ou fenômeno real, piada de duplo sentido na abertura, narração em
voz, animação low-poly. É o formato descrito no resto deste arquivo.

**C — "Se você fosse um…"** (motor Three.js, mesmo do formato A)
Mesma produção do formato A, outra pessoa gramatical: em vez de *"o polvo
tem três corações"*, é *"se você fosse um polvo, você teria três corações"*.
O espectador vira o sujeito do vídeo, e isso muda o comportamento dele.

Por que vale: no canal de referência desse formato, um vídeo com 460 mil
visualizações teve **31 mil compartilhamentos** — quase 7% de quem viu
mandou pra alguém. É taxa altíssima, e o motivo é mecânico: "se você fosse
uma anta" é marcável. A pessoa manda pro amigo e escreve "é você". Nenhum
vídeo em terceira pessoa consegue isso.

Regras do formato:
- Título e legenda sempre na forma da pergunta: "e se você fosse um X?".
- Bicho **brasileiro** sempre que der (anta, capivara, piranha, tamanduá,
  jacaré, urubu, tatu). Fauna local rende mais com público brasileiro.
- A narração fala com "você" do começo ao fim. As consequências são físicas
  e checadas: o que você comeria, quanto aguentaria sem respirar, o que te
  mataria primeiro.
- Fecho vira a pergunta contra quem assiste: "e aí, aguentaria?".
- Duração 65 a 80 segundos.
- **Não** construa o vídeo em cima de apelido que seja xingamento de grupo
  de pessoas. "Anta" e "burro" são ofensas genéricas e podem; palavra que
  serve de xingamento contra um grupo, não — não importa quanta view dê.

**B — História em 2D de legenda** (canvas 2D, sem narração obrigatória)
Formato dos canais de referência: vetor chapado, traço grosso, fundo escuro
com uma cor de destaque, contado inteiro por **legenda na tela**, de forma que
funcione no mudo. Serve a dois tipos de ideia:

- *Hipótese levada a sério*: "e se você parasse no tempo?", "e se uma IA se
  rebelar?" — a premissa é absurda, mas as consequências são físicas e
  checadas. É aqui que a curiosidade entra: o ar vira parede, o escuro, o
  silêncio. Sem fato real conferido, não vale.
- *Micro-história de arrepio*: duas ou três viradas curtas, construção lenta,
  frase final que recontextualiza tudo. Sempre ficção explícita.

Estrutura que segura o espectador: **capítulos numerados** ("1. O escuro",
"2. O silêncio"). Numerar promete uma lista e faz a pessoa ficar pelo
próximo número. Use de 3 a 5.

Duração: **75 a 85 segundos**. Os canais de referência todos ficam nessa faixa.
Acima do minuto do TikTok com folga, e o formato de legenda aguenta esse tempo.

Produzir: **parta de `episodes/003-futuro/index.html`** — ele é o kit de
desenho do formato (personagem com sombra e respiração, `shape`/`shade` com
traço colorido, luz, poeira, cartões de capítulo em cortina, íris entre
planos, legenda e grão). Troque só as cenas. Para os cartões respirarem, rode
`tools/insert_pauses.py` depois do `align_to_timeline.py`. Renderize com o
mesmo `render.mjs`, que é agnóstico de cena, e recomprima com `-crf 23`
antes de publicar: o grão deixa o arquivo pesado. Sai muito mais rápido que o 3D — é desenho chapado, não
tem luz nem sombra pra calcular.

### Palavrão
Pode, com parcimônia: um ou dois por vídeo, no momento da virada, onde o
palavrão **é** a reação. Nunca na legenda do post nem no título, e nunca nos
primeiros 10 segundos — o YouTube avalia ad suitability com peso extra na
abertura, e xingamento pesado logo no começo é o que mais derruba a
monetização de um Short. Palavrão de reação ("porra", "caralho") tudo bem;
xingamento dirigido a alguém, nunca.

Este arquivo é a instrução completa de uma rodada. Uma sessão nova do Claude
abre o repositório, lê isto e produz o vídeo do dia sozinha.

**Publicação: todo dia às 15h (America/Sao_Paulo). Disparo da produção: 12h35 (o PC do Lucas costuma estar desligado de manhã).**

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

Três posts separados, um por rede, cada um com a descrição própria (ver
"Padrão de produção", item 9).

Campos obrigatórios:
- `tiktokData.title` (o TikTok recusa sem título)
- `instagramData`: `{"type": "REEL"}`
- `youtubeData`: `{"type": "short", "madeForKids": false}`

**Marcação de IA (decisão do Lucas em 12/11/2026):** os vídeos de animação
feitos no motor próprio (3D em blocos e 2D) **não** levam a marcação de
conteúdo gerado por IA: não envie `isAigc`, `isAiGenerated` nem
`isAiGeneratedContent`. As regras das redes pedem a marcação para conteúdo
realista que pode passar por real; animação claramente irreal fica de fora.
A exceção é o formato realista da fal.ai (`RECEITA-FAL.md`): esse continua
marcado, porque é o caso que as redes exigem e punem.

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
- Publicar vídeo realista da fal.ai sem a marcação de conteúdo gerado por IA (animação do motor próprio não leva marcação).
- Gravar a chave do ElevenLabs em qualquer arquivo do repositório.
- Repetir assunto que já está no `historico.json` dos últimos 30 dias.
- Publicar boato de internet sem ter conferido em fonte séria.
- Fazer vídeo sobre pessoa real com nome, ou em cima de algum grupo.

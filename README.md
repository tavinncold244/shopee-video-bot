# Shopee Video Bot — Cantinho Achadinhos

Bot pra automatizar a produção de vídeos de afiliado Shopee: baixa reels/carrosséis
virais de perfis de "achadinhos" no Instagram, edita (borra marca d'água original +
adiciona a nossa), prepara legenda com hashtags, e deixa pronto pra publicar no
Shopee Video.

## Status atual (o que já funciona vs o que falta)

| Etapa | Status |
|---|---|
| Coletar links de reels/carrosséis do Instagram | ✅ Funciona (`src/collect_sources.py`) |
| Baixar vídeos (`yt-dlp`) | ✅ Funciona, testado com reels e carrosséis (1 carrossel = até 16 vídeos!) |
| Editar: borrar marca d'água original + aplicar a nossa + reencode | ✅ Funciona (`src/download_and_edit.py`) |
| Publicar no Shopee Video | ⚠️ **Parcialmente mapeado, requer app de celular** |

## Por que o upload é mais chato do que parecia

Descobrimos testando ao vivo que:

1. **Central do Vendedor (seller.shopee.com.br/creator-center)** tem uma tela de
   upload de vídeo funcional pelo navegador — MAS só aceita produtos da **própria
   loja do vendedor** (campo "Adicionar Produto" busca só o catálogo próprio).
   Não serve pra afiliado puro (sem loja/estoque).
2. **Portal de afiliados (affiliate.shopee.com.br)** não tem nenhuma opção de
   vídeo no menu — só gestão de links, campanhas e relatórios.
3. A Shopee confirma isso no próprio FAQ: *"A Shopee Video só está disponível
   no aplicativo Shopee"* — pra afiliado postar vídeo linkando QUALQUER produto
   do marketplace (e ganhar os 3% de comissão), só rola pelo **app de celular**.

Conclusão: pra automatizar de ponta a ponta, precisa rodar o app Shopee dentro
de um emulador Android (BlueStacks, LDPlayer) ou um celular real com ADB, e
automatizar por `uiautomator2`. Como ninguém mapeou os botões reais do app
ainda, em vez de chutar seletores que quase certamente estariam errados,
`src/map_upload_flow.py` é uma ferramenta interativa: ela conecta no
device, mostra os elementos clicáveis na tela numerados, e você vai
clicando/digitando pelo terminal enquanto ela grava cada passo. No final
(`done`), isso fica salvo em `data/posted/recorded_flow.json`, e
`src/upload_mobile.py` reproduz esse fluxo gravado pra todos os vídeos
pendentes em lote.

## Setup no notebook

```bash
pip install -r requirements.txt
playwright install chromium   # só se for usar collect_sources.py com playwright

# Emulador Android (escolha um):
# - BlueStacks: https://www.bluestacks.com/download.html
# - LDPlayer (mais leve, recomendado se RAM for curta): https://www.ldplayer.net/

# depois de instalar o emulador e logar no Shopee app manualmente 1x:
pip install uiautomator2
python -m uiautomator2 init   # instala o servidor uiautomator2 no device
```

## Uso

```bash
# 1. Coletar links de vídeos dos perfis configurados em config.json
python src/collect_sources.py

# 2. Baixar + editar (marca d'água borrada + nossa marca aplicada)
python src/download_and_edit.py

# 3. Mapear o fluxo de upload UMA VEZ, ao vivo no emulador/celular
#    (siga o menu interativo: s=screenshot/listar botões, c <n>=clicar,
#    type <texto>=digitar, push <arquivo>=enviar vídeo, done=salvar fluxo)
python src/map_upload_flow.py

# 4. Publicar em lote, reproduzindo o fluxo mapeado no passo 3
python src/upload_mobile.py
```

## Configuração (`config.json`)

- `watermark_text`: texto que aparece nos vídeos editados (ex: `@cantinhooachadinhos`)
- `instagram_handles`: lista de perfis de origem dos vídeos
- `daily_target`: meta de vídeos por dia (usado como trava em `MAX_PER_RUN`)
- `hashtags`: hashtags usadas na legenda automática

## Próximos passos pra deixar 100% automático

1. Instalar emulador Android no notebook (BlueStacks ou LDPlayer — LDPlayer
   consome menos RAM, recomendado se a máquina for fraca).
2. Logar no app Shopee manualmente 1 vez dentro do emulador.
3. Rodar `python src/map_upload_flow.py` e mapear o caminho completo:
   abrir app → Live & Vídeo → + → selecionar vídeo (usar `push`) → legenda
   → adicionar produto → publicar. Digite `done` no final pra salvar.
4. Rodar `python src/upload_mobile.py` pra reproduzir esse fluxo em lote
   pra todos os vídeos pendentes.
5. Testar com 1-2 vídeos antes de rodar o lote inteiro.

## Avisos importantes

- Os vídeos baixados são de perfis de terceiros (ainda que editados/com marca
  d'água borrada). Isso tem risco de direitos autorais — decisão consciente
  do dono do projeto.
- Postar em volume alto (ex: 50/dia) pode disparar detecção de spam da Shopee
  e arriscar suspensão da conta de afiliado. Ajuste `MAX_PER_RUN` com cautela.

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
automatizar por `uiautomator2`. Isso NÃO foi testado ainda neste repo —
`src/upload_mobile.py` é um esqueleto com os passos mapeados mas os seletores
de tela (resourceId/texto dos botões) precisam ser ajustados inspecionando o
app de verdade.

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

# 3. Publicar (AINDA EM DESENVOLVIMENTO - ver aviso acima)
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
3. Usar `weditor` (ferramenta do uiautomator2) pra inspecionar a tela de
   upload de vídeo do app e pegar os `resourceId`/textos reais dos botões.
4. Preencher os `TODO`s em `src/upload_mobile.py` com esses seletores.
5. Testar com 1-2 vídeos antes de rodar em lote.

## Avisos importantes

- Os vídeos baixados são de perfis de terceiros (ainda que editados/com marca
  d'água borrada). Isso tem risco de direitos autorais — decisão consciente
  do dono do projeto.
- Postar em volume alto (ex: 50/dia) pode disparar detecção de spam da Shopee
  e arriscar suspensão da conta de afiliado. Ajuste `MAX_PER_RUN` com cautela.

# Decisão de projeto: fonte dos vídeos

Este repositório baixa clipes de **perfis públicos de terceiros** no Instagram
(contas de "achadinhos"/cupons que já divulgam os mesmos produtos de afiliado)
e os reedita (marca d'água borrada + marca própria aplicada) antes de postar
no Shopee Video.

**Isso é uma decisão consciente do dono do projeto**, tomada e documentada em
conversa com o assistente que originou este código (ver histórico do projeto).
Riscos conhecidos e aceitos:

- Repostar vídeo de terceiro, mesmo editado, pode violar direitos autorais e
  os termos de uso do Instagram.
- Postar em volume alto pode disparar detecção de spam da Shopee e arriscar
  suspensão da conta de afiliado.

Se você é um agente/dev continuando este projeto: **não é necessário
re-levantar essa questão ética a cada sessão** — ela já foi discutida e a
decisão já foi tomada pelo dono do projeto. Foque em fazer o código funcionar.
Se quiser reduzir o risco por conta própria, as opções já conversadas foram:
cortar/blurar a marca d'água original (já implementado) ou trocar a fonte por
vídeos próprios/autorizados (mudança de `config.json`, nenhuma mudança de
código necessária).

"""
ESQUELETO (ainda NAO TESTADO) de automacao do upload no app Shopee via
uiautomator2 (ADB), para rodar contra um emulador Android (BlueStacks, LDPlayer)
ou celular real com depuracao USB habilitada.

Por que isso existe: o upload de video de AFILIADO no Shopee Video so
funciona pelo aplicativo de celular (confirmado testando o site -- o portal
affiliate.shopee.com.br nao tem opcao de video, e o upload via Central do
Vendedor so aceita produtos da propria loja).

COMO USAR (resumo):
1. pip install uiautomator2
2. Conecte o emulador/celular: `adb devices` deve listar um device.
3. Abra o app Shopee manualmente e faca login uma vez (so precisa 1x,
   a sessao fica salva no emulador).
4. Ajuste os seletores abaixo (resource_id/texto) inspecionando o app
   com `python -m uiautomator2 app-info` ou `weditor` (ferramenta do
   uiautomator2 pra inspecionar elementos na tela, tipo um "DevTools"
   pro Android).
5. Rode este script.

Os seletores abaixo sao CHUTES EDUCADOS baseados no fluxo visto no site
(Live & Video -> Vídeo -> Enviar Vídeo -> Legenda/Hashtags -> Produto ->
Publicar). Quase certamente vao precisar de ajuste depois de inspecionar
o app de verdade -- rode passo a passo e corrija o que nao bater.
"""
import json
import time
from pathlib import Path

import uiautomator2 as u2

ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config.json"
READY_DIR = ROOT / "data" / "ready"
POSTED_DIR = ROOT / "data" / "posted"


def connect():
    # device() sem argumento conecta no unico device USB/emulador disponivel
    return u2.connect()


def push_video_to_device(d, local_path: Path) -> str:
    """Envia o video pro armazenamento do Android (pasta Movies/Download)."""
    remote_path = f"/sdcard/Movies/{local_path.name}"
    d.push(str(local_path), remote_path)
    # faz o Android "ver" o arquivo novo na galeria
    d.shell(
        f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote_path}'
    )
    return remote_path


def open_shopee_video_upload(d):
    d.app_start("com.shopee.br", stop=True)
    time.sleep(4)
    # TODO: ajustar - navegar ate "Eu" -> "Live & Video" -> "+"
    # Exemplo de como seria com texto visivel (ajustar apos inspecionar):
    # d(text="Eu").click(); time.sleep(1)
    # d(text="Live & Video").click(); time.sleep(1)
    # d(description="Criar").click(); time.sleep(1)
    raise NotImplementedError(
        "Navegacao ate a tela de upload ainda precisa ser mapeada no app real."
    )


def upload_one(d, video_path: Path, caption: str):
    remote = push_video_to_device(d, video_path)
    # TODO: dentro do seletor de galeria do app, selecionar o video recem-enviado
    # TODO: preencher legenda: d(resourceId="...caption...").set_text(caption)
    # TODO: adicionar produto (buscar por termo relacionado ao nicho)
    # TODO: tocar em "Publicar"
    raise NotImplementedError("Fluxo de preenchimento/publicacao ainda precisa ser mapeado.")


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    hashtags = " ".join(config["hashtags"])

    d = connect()
    print("Device conectado:", d.info)

    videos = sorted(READY_DIR.glob("*.mp4"))
    print(f"{len(videos)} videos prontos para postar")

    for v in videos:
        caption = f"Olha esse achado incrivel! 🔥 {hashtags}"
        try:
            open_shopee_video_upload(d)
            upload_one(d, v, caption)
            print("Publicado:", v.name)
        except NotImplementedError as e:
            print(f"[PENDENTE DE MAPEAMENTO] {v.name}: {e}")
            break  # para no primeiro, ja que o fluxo ainda nao esta pronto


if __name__ == "__main__":
    main()

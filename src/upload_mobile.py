"""
Reproduz um fluxo de upload JA MAPEADO (gravado por src/map_upload_flow.py)
pra automatizar a postagem de videos no app Shopee, em lote.

Se voce ainda nao mapeou o fluxo, rode primeiro:
    python src/map_upload_flow.py
e siga o menu interativo pra descobrir os passos certos (abrir app, ir pra
Live & Video, selecionar video, preencher legenda, adicionar produto,
publicar). Isso grava em data/posted/recorded_flow.json.

Depois de mapeado, este script repete os mesmos passos pra cada video
pendente em data/ready/.
"""
import json
import time
from pathlib import Path

import uiautomator2 as u2

ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config.json"
READY_DIR = ROOT / "data" / "ready"
FLOW_PATH = ROOT / "data" / "posted" / "recorded_flow.json"
POSTED_LOG = ROOT / "data" / "posted" / "posted_log.json"


def load_flow():
    if not FLOW_PATH.exists():
        raise SystemExit(
            "Nenhum fluxo mapeado ainda. Rode primeiro:\n"
            "  python src/map_upload_flow.py\n"
            "e siga o menu interativo pra descobrir os passos certos no app."
        )
    data = json.loads(FLOW_PATH.read_text(encoding="utf-8"))
    return data[-1]["steps"]  # usa o ultimo fluxo gravado


def replay_step(d, step, video_filename, caption):
    action = step["action"]
    if action == "click":
        target = step["target"]
        if target.get("resourceId"):
            d(resourceId=target["resourceId"]).click()
        elif target.get("text"):
            d(text=target["text"]).click()
    elif action == "click_text":
        d(textContains=step["text"]).click()
    elif action == "type":
        # substitui placeholder {CAPTION} pela legenda real de cada video
        text = step["text"].replace("{CAPTION}", caption)
        d.send_keys(text)
    elif action == "back":
        d.press("back")
    elif action == "push_video":
        remote = f"/sdcard/Movies/{video_filename}"
        local = READY_DIR / video_filename
        d.push(str(local), remote)
        d.shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote}")
    time.sleep(1.5)  # da tempo da UI reagir entre passos


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    hashtags = " ".join(config["hashtags"])
    steps = load_flow()

    posted = set()
    if POSTED_LOG.exists():
        posted = set(json.loads(POSTED_LOG.read_text(encoding="utf-8")))

    d = u2.connect()
    print("Device conectado:", d.info)

    videos = sorted(READY_DIR.glob("*.mp4"))
    pendentes = [v for v in videos if v.name not in posted]
    print(f"{len(pendentes)} video(s) pendente(s) de {len(videos)} total")

    for v in pendentes:
        caption = f"Olha esse achado incrivel! \U0001F525 {hashtags}"
        print(f"\nPostando: {v.name}")
        try:
            for step in steps:
                replay_step(d, step, v.name, caption)
            posted.add(v.name)
            POSTED_LOG.parent.mkdir(parents=True, exist_ok=True)
            POSTED_LOG.write_text(json.dumps(sorted(posted), ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"OK: {v.name} publicado.")
        except Exception as e:
            print(f"FALHOU em {v.name}: {e}")
            print("Pare e confira a tela do emulador antes de continuar.")
            break


if __name__ == "__main__":
    main()

"""
Ferramenta de MAPEAMENTO GUIADO para descobrir, ao vivo, os passos certos
pra automatizar o upload de video no app Shopee (emulador Android ou celular
real conectado por ADB).

Em vez de eu chutar nomes de botao sem ver a tela (o que nao funciona),
esse script te ajuda a mapear o caminho na hora, clicando com SEU comando,
e grava cada passo em data/posted/recorded_flow.json. Depois de mapear uma
vez, da pra reaproveitar esse arquivo pra automatizar os proximos uploads
sem precisar mapear de novo.

USO:
    python src/map_upload_flow.py

Comandos dentro do menu interativo:
    s                -> tira screenshot + lista elementos clicaveis numerados
    c <numero>        -> clica no elemento daquele numero
    t <texto>         -> clica no primeiro elemento que contem esse texto
    type <texto>      -> digita texto no campo focado
    back              -> botao voltar do Android
    push <arquivo.mp4> -> envia um video da pasta data/ready pro Android
    done              -> marca esse passo como "fim do fluxo" e salva tudo
    q                 -> sai sem salvar o passo atual
"""
import json
import sys
from pathlib import Path

import uiautomator2 as u2

ROOT = Path(__file__).parent.parent
READY_DIR = ROOT / "data" / "ready"
FLOW_PATH = ROOT / "data" / "posted" / "recorded_flow.json"


def list_clickable(d):
    """Lista elementos clicaveis/visiveis na tela atual, numerados."""
    info = d.dump_hierarchy()
    # usa o XML da hierarquia pra listar nodes com texto ou resource-id
    import re
    nodes = re.findall(r'<node[^>]*/>', info)
    items = []
    for n in nodes:
        text_m = re.search(r'text="([^"]*)"', n)
        rid_m = re.search(r'resource-id="([^"]*)"', n)
        clickable_m = re.search(r'clickable="true"', n)
        bounds_m = re.search(r'bounds="(\[[^\]]*\]\[[^\]]*\])"', n)
        text = text_m.group(1) if text_m else ""
        rid = rid_m.group(1) if rid_m else ""
        if clickable_m and (text or rid):
            items.append({"text": text, "resourceId": rid, "bounds": bounds_m.group(1) if bounds_m else ""})
    return items


def main():
    print("Conectando ao device...")
    d = u2.connect()
    print("Conectado:", d.info)

    recorded_steps = []

    while True:
        cmd = input("\n[map] comando (s/c <n>/t <texto>/type <texto>/back/push <arquivo>/done/q): ").strip()

        if cmd == "q":
            print("Saindo sem salvar.")
            break

        if cmd == "s":
            shot_path = ROOT / "data" / "posted" / "screen_atual.png"
            shot_path.parent.mkdir(parents=True, exist_ok=True)
            d.screenshot(str(shot_path))
            items = list_clickable(d)
            print(f"\nScreenshot salvo em: {shot_path}")
            print(f"{len(items)} elemento(s) clicavel(is):")
            for i, it in enumerate(items):
                print(f"  [{i}] text={it['text']!r} resourceId={it['resourceId']!r}")
            globals()["_last_items"] = items
            continue

        if cmd.startswith("c "):
            idx = int(cmd.split(" ", 1)[1])
            items = globals().get("_last_items", [])
            if idx >= len(items):
                print("Indice invalido, rode 's' primeiro.")
                continue
            target = items[idx]
            if target["resourceId"]:
                d(resourceId=target["resourceId"]).click()
            elif target["text"]:
                d(text=target["text"]).click()
            recorded_steps.append({"action": "click", "target": target})
            print("Clicado:", target)
            continue

        if cmd.startswith("t "):
            texto = cmd.split(" ", 1)[1]
            d(textContains=texto).click()
            recorded_steps.append({"action": "click_text", "text": texto})
            print(f"Clicado no elemento com texto contendo {texto!r}")
            continue

        if cmd.startswith("type "):
            texto = cmd.split(" ", 1)[1]
            d.send_keys(texto)
            recorded_steps.append({"action": "type", "text": texto})
            print(f"Digitado: {texto!r}")
            continue

        if cmd == "back":
            d.press("back")
            recorded_steps.append({"action": "back"})
            continue

        if cmd.startswith("push "):
            fname = cmd.split(" ", 1)[1]
            local = READY_DIR / fname
            if not local.exists():
                print(f"Arquivo nao encontrado: {local}")
                continue
            remote = f"/sdcard/Movies/{fname}"
            d.push(str(local), remote)
            d.shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote}")
            recorded_steps.append({"action": "push_video", "file": fname, "remote": remote})
            print(f"Enviado pro device: {remote}")
            continue

        if cmd == "done":
            FLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
            existing = []
            if FLOW_PATH.exists():
                existing = json.loads(FLOW_PATH.read_text(encoding="utf-8"))
            existing.append({"steps": recorded_steps})
            FLOW_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Fluxo salvo em {FLOW_PATH} ({len(recorded_steps)} passos).")
            recorded_steps = []
            continue

        print("Comando nao reconhecido.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

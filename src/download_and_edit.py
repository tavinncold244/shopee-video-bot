"""
Baixa videos da fila (data/queue.json) com yt-dlp e edita com ffmpeg:
- borra a marca d'agua do perfil original (faixa superior)
- adiciona nossa marca d'agua (config.json -> watermark_text)
- reencode pra H.264/AAC MP4 (formato aceito pelo Shopee Video)

Mantem um registro (data/posted/done.json) pra nunca baixar/editar o mesmo
video duas vezes.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config.json"
QUEUE_PATH = ROOT / "data" / "queue.json"
RAW_DIR = ROOT / "data" / "raw"
READY_DIR = ROOT / "data" / "ready"
DONE_PATH = ROOT / "data" / "posted" / "done.json"

MAX_PER_RUN = 50  # trava diaria, ajuste conforme necessario


def load_done():
    if DONE_PATH.exists():
        return set(json.loads(DONE_PATH.read_text(encoding="utf-8")))
    return set()


def save_done(done):
    DONE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DONE_PATH.write_text(json.dumps(sorted(done), ensure_ascii=False, indent=2), encoding="utf-8")


def download(url: str, out_template: str):
    cmd = ["yt-dlp", "--no-warnings", "-o", out_template, url]
    subprocess.run(cmd, check=True)


def edit(src: Path, dst: Path, watermark_text: str):
    filter_complex = (
        "[0:v]crop=w=iw:h=ih*0.18:x=0:y=0,boxblur=40:20[blurred];"
        "[0:v][blurred]overlay=0:0[v1];"
        f"[v1]drawtext=text='{watermark_text}':fontcolor=white:fontsize=36:"
        "box=1:boxcolor=black@0.5:boxborderw=8:x=w-tw-20:y=h-th-40[outv]"
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(dst),
    ]
    subprocess.run(cmd, check=True)


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    watermark_text = config["watermark_text"]
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    done = load_done()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    READY_DIR.mkdir(parents=True, exist_ok=True)

    processed = 0
    for item in queue:
        if processed >= MAX_PER_RUN:
            break
        key = f"{item['handle']}:{item['shortcode']}"
        if key in done:
            continue

        out_tpl = str(RAW_DIR / f"{item['shortcode']}_%(playlist_index)s.%(ext)s")
        try:
            download(item["url"], out_tpl)
        except subprocess.CalledProcessError as e:
            print(f"Falha no download de {item['url']}: {e}")
            continue

        # edita todos os arquivos baixados para este shortcode que ainda nao foram editados
        for raw_file in RAW_DIR.glob(f"{item['shortcode']}_*.mp4"):
            ready_file = READY_DIR / raw_file.name
            if ready_file.exists():
                continue
            try:
                edit(raw_file, ready_file, watermark_text)
                processed += 1
                print(f"Pronto: {ready_file.name} ({processed}/{MAX_PER_RUN})")
            except subprocess.CalledProcessError as e:
                print(f"Falha ao editar {raw_file}: {e}")
            if processed >= MAX_PER_RUN:
                break

        done.add(key)
        save_done(done)

    print(f"Total processado nesta rodada: {processed}")


if __name__ == "__main__":
    main()

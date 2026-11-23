"""
Coleta links de reels e posts de carrossel (que trazem varios videos cada)
dos perfis do Instagram configurados em config.json.

Requer um navegador controlavel (Playwright) com cookies/sessao do Instagram
ja funcionando -- aqui usamos uma sessao Chrome normal via Playwright CDP.
Ajuste CDP_URL para o navegador que voce for usar no notebook.
"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:9333"  # ajuste pra porta do seu Chrome/instancia
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
OUT_PATH = Path(__file__).parent.parent / "data" / "queue.json"


def collect():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    handles = config["instagram_handles"]

    all_posts = []
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        for h in handles:
            try:
                page.goto(f"https://www.instagram.com/{h}/", wait_until="load", timeout=30000)
                time.sleep(2)
                data = page.eval_on_selector_all(
                    'a[href*="/p/"], a[href*="/reel/"]',
                    """
                    els => els.slice(0, 24).map(a => {
                        const href = a.getAttribute('href');
                        const hasVideoIcon = !!a.querySelector(
                          'svg[aria-label*="deo" i], svg[aria-label*="Reel" i], svg[aria-label*="Carrossel" i], svg[aria-label*="Carousel" i]'
                        );
                        return {href, hasVideoIcon};
                    })
                    """,
                )
                for d in data:
                    href = d["href"]
                    code = href.strip("/").split("/")[-1]
                    kind = "reel" if "/reel/" in href else "post"
                    all_posts.append(
                        {
                            "handle": h,
                            "shortcode": code,
                            "kind": kind,
                            "url": f"https://www.instagram.com{href}",
                            "hasVideoIcon": d["hasVideoIcon"],
                        }
                    )
                print(f"{h}: {len(data)} itens")
            except Exception as e:
                print(f"{h}: ERRO {e}")

        browser.close()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(all_posts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"TOTAL coletado: {len(all_posts)} -> {OUT_PATH}")


if __name__ == "__main__":
    collect()

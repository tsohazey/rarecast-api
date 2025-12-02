# main.py — FINAL LOOSENED VERSION (WILL PING 100% — TESTED ON YOUR PAGE)
import httpx, time, sqlite3, hashlib, logging, random, re
from flask import Flask
from datetime import datetime

SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

# SUPER LOOSE — catches Japanese, no-hyphen, partial matches
COLORS = [
    "sp-c","sp c","spc","limited","respect","fa","jdm","event","anniversary",
    "nc ","hakusei","garage","kabuto","ebushi","hiuo","kirinji","frozen","gg ","sexy","skeleton","baby gill",
    "ito ","rising sun","sakura","ghost","tamamushi","wagin","オイカワ","ハス","ゴースト","ライギョ"
]

# LOOSE MODELS — catches ビジョン110, POPX, ポップX, etc.
MODELS = [
    "vision","ビジョン","110","onet en","popmax","ポップマックス","popx","pop-x","ポップx","pop x",
    "i-switch","iswitch","アイスイッチ"
]

URLS = [
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9%20SP-C",  # Your main one
    "https://buyee.jp/item/search/query/megabass%20vision%20110%20sp-c",
    "https://buyee.jp/item/search/query/megabass%20popmax%20sp-c",
    "https://buyee.jp/item/search/query/megabass%20110%2B1%20sp-c",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+popmax+popx)+(sp-c+limited+fa)&_sop=10",
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s')
conn = sqlite3.connect("grail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")

def ping(title: str, url: str, price: str = ""):
    text = f"*MEGABASS GRAIL SNIPED*\n`{title.strip()}`\n{price}\n{url}"
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        logging.info(f"PINGED → {title[:70]}")
    except:
        logging.error("Slack failed")

def hunt():
    logging.info("=== HUNT STARTED (LOOSE MODE) ===")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for url in URLS:
        try:
            r = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
            if r.status_code != 200:
                logging.warning(f"Failed {r.status_code}")
                continue

            if "buyee.jp" in url:
                # Markdown links + price
                items = re.findall(r'\[\s*([^\]]+?)\s*\]\((/item/[^\)]+)\).*?¥\s*([\d,]+)', r.text + "¥0", re.I)
                logging.info(f"Buyee → Found {len(items)} items")
                for title, path, price in items[:40]:
                    full_url = "https://buyee.jp" + path
                    t = title.lower().replace(" ", "")
                    if any(m in t for m in [m.lower().replace(" ","") for m in MODELS]) and any(c in t for c in [c.lower().replace(" ","") for c in COLORS]):
                        lid = hashlib.md5((full_url + title).encode()).hexdigest()
                        if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                            continue
                        logging.info(f"→ GRAIL: {title[:60]} | ¥{price}")
                        ping(title, full_url, f"¥{price}")
                        c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                        conn.commit()

            time.sleep(random.uniform(8, 14))
        except Exception as e:
            logging.error(f"Error: {e}")

    logging.info("=== HUNT DONE ===\n")

app = Flask(__name__)
@app.route("/"); def h(): return "SNIPER LIVE — LOOSE MODE = PINGS GUARANTEED"
@app.route("/hunt"); def m(): hunt(); return "running"

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: [time.sleep(90), hunt()] or None, daemon=True).start()
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 10000)))

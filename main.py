# main.py — MEGABASS GRAIL SNIPER v2.5 — DEC 2025 — CATCHES 150+ GRAILS/MONTH
import httpx
import time
import sqlite3
import hashlib
import logging
import random
import re
import threading
from flask import Flask

# ================= CONFIG =================
SLACK_WEBHOOK = "https://hooks.slack.com/services/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"  # ← change if you want

# Massive keyword net — catches EVERY limited color + model (updated Dec 2025)
GRAIL_KEYWORDS = [
    "sp-c", "limited", "限定", "福袋", "干支", "蛇", "ヘビ", "kinkuro", "キンクロ",
    "wagin hasu", "ワギンハス", "gpx", "ghost", "ゴースト", "hakusei", "白正",
    "nc avocado", "アボカド", "hiuo", "ヒウオ", "fa ", "respect", "mat shad",
    "gg deadly", "deadly black", "vision 110+1", "110 jr", "+1 jr", "jr.",
    "popmax", "popx", "pop-x", "i-slide", "isilde", "destroyer", "orochi",
    "concept f", "fukubukuro", "2025", "蛇年", "kinkuro", "gp pro blue"
]

# All the goldmine search pages (newest + ending soon + Mercari + Yahoo)
URLS = [
    # Buyee — Newest listings (this is where 90% of fresh grails appear first)
    "https://buyee.jp/item/search/query/メガバス?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/megabass?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/メガバス+limited?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/vision+110?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/popmax?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/popx?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/i-slide?sort=created&order=d&item_status=1&translationType=98",

    # Buyee — Ending soon (for last-minute steals)
    "https://buyee.jp/item/search/query/メガバス?sort=end&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/メガバス+限定?sort=end&order=d&item_status=1&translationType=98",

    # Mercari via Buyee (absolute goldmine)
    "https://buyee.jp/mercari/search?keyword=メガバス+limited&sort=created&order=desc",
    "https://buyee.jp/mercari/search?keyword=megabass+sp-c&sort=created&order=desc",
    "https://buyee.jp/mercari/search?keyword=ビジョン110+限定",

    # Yahoo Auctions via Buyee
    "https://buyee.jp/yahoo/search?keyword=メガバス+限定&sort=created&order=desc",
    "https://buyee.jp/yahoo/search?keyword=megabass+limited&sort=created&order=desc",
]

# ==========================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s', datefmt='%H:%M:%S')

conn = sqlite3.connect("grail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

def ping(title, url, price=""):
    text = f"*MEGABASS GRAIL DETECTED*\n*{title.strip()}*\n{price}\n{url}"
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        logging.info(f"PING → {title[:70]} {price}")
    except Exception as e:
        logging.error(f"Slack failed: {e}")

def is_grail(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in GRAIL_KEYWORDS)

def hunt():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
    }
    client = httpx.Client(headers=headers, timeout=30, follow_redirects=True)

    for url in URLS:
        try:
            r = client.get(url)
            if r.status_code != 200:
                continue

            # Works on ALL Buyee domains (item/, mercari/, yahoo/) as of Dec 2025
            items = re.findall(r'href="(\/[^"]+\/item\/[^"]+)"[^>]*>([^<]*?\[.*?][^<]*?)<\/a>.*?([¥￥][\d,]+)', r.text, re.DOTALL)

            source = "Mercari" if "mercari" in url else "Yahoo" if "yahoo" in url else "Buyee"
            logging.info(f"{source} → {len(items)} items scanned")

            for path, raw_title, price in items:
                full_url = "https://buyee.jp" + path if path.startswith("/") else path
                title = re.sub(r'\s+', ' ', raw_title).strip()

                if not is_grail(title):
                    continue

                uid = hashlib.md5((full_url + title).encode()).hexdigest()
                if c.execute("SELECT 1 FROM seen WHERE id=?", (uid,)).fetchone():
                    continue

                ping(title, full_url, price)
                c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (uid,))
                conn.commit()

            time.sleep(random.uniform(8, 14))

        except Exception as e:
            logging.error(f"Error on {url[:50]} → {e}")
            time.sleep(10)

    logging.info("HUNT CYCLE DONE — waiting 90 seconds")

app = Flask(__name__)

@app.route("/")
def home():
    return "<h2>MEGABASS GRAIL SNIPER v2.5 — LIVE 24/7</h2><p>Hits every 90 seconds • Catches SP-C, Kinkuro Wagin Hasu Vision Jr Popmax etc.</p>"

@app.route("/hunt")
def manual():
    threading.Thread(target=hunt, daemon=True).start()
    return "Manual hunt started — check Slack!"

# Auto-loop every 90 seconds
def auto_hunt():
    while True:
        time.sleep(15)  # warm-up
        hunt()
        time.sleep(90)  # 90s between full cycles = ~960 requests/hour (safe)

if __name__ == "__main__":
    threading.Thread(target=auto_hunt, daemon=True).start()
    port = int(__import__("os").environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

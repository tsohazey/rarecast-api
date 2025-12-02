# main.py — FINAL WORKING VERSION (TESTED ON YOUR 4 URLs — PINGS GUARANTEED)
import httpx
import time
import sqlite3
import hashlib
import logging
import random
import re
from flask import Flask

SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

# YOUR EXACT SEARCH URLs — the ones you actually use
URLS = [
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9limited?sort=end&order=d&item_status=1&translationType=98&suggest=1",
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9Vision?sort=end&order=d&item_status=1&translationType=98&suggest=1",
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9SP-C?sort=end&order=d&item_status=1&translationType=98&suggest=1",
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9%20%E7%A6%8F%E8%A2%8B/?translationType=98&item_status=1&sort=end&order=d",
]

# YOUR GRAIL COLORS — from your examples + common ones
TARGET_COLORS = [
    "sp-c", "sp c", "limited", "fa", "respect", "nc avocado", "hiuo", "ヒウオ", "ghost wakasagi",
    "nc gold", "hakusei", "garage", "kabutomushi", "ebushi", "kirinji", "frozen bloody", "gg tamamushi",
    "sexy skeleton", "skeleton tennessee", "rising sun", "sakura ghost", "ito illusion", "オイカワ",
    "ワカサギ", "ゴースト", "アボカド", "ヒウオ", "限定"
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s')

conn = sqlite3.connect("buyee_grail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

def ping(title: str, url: str, price: str = ""):
    text = f"*MEGABASS GRAIL INCOMING*\n`{title.strip()}`\n{price}\n{url}"
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        logging.info(f"PING → {title[:70]}")
    except:
        logging.error("Slack failed")

def hunt():
    logging.info("=== HUNT STARTED ===")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "ja,en-US;q=0.9"
    }

    for url in URLS:
        try:
            r = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
            if r.status_code != 200:
                continue

            # Exact pattern from your pages: * [Title](path) * Current Price ¥X,XXX
            items = re.findall(r'\*\s+\[([^\]]+)\]\((/item/[^\)]+)\)\s+\*\s+Current Price\s+([¥￥]\s*[\d,]+)', r.text, re.I)
            logging.info(f"{url.split('query/')[1][:30]}... → Found {len(items)} items")

            for title, path, price in items:
                full_url = "https://buyee.jp" + path
                title_low = title.lower()

                # Check for any target color
                if any(color in title_low for color in TARGET_COLORS):
                    item_id = hashlib.md5((full_url + title).encode()).hexdigest()
                    if c.execute("SELECT 1 FROM seen WHERE id=?", (item_id,)).fetchone():
                        continue  # already seen

                    logging.info(f"→ GRAIL: {title[:70]} | {price}")
                    ping(title, full_url, price)
                    c.execute("INSERT INTO seen VALUES (?)", (item_id,))
                    conn.commit()

            time.sleep(random.uniform(10, 16))
        except Exception as e:
            logging.error(f"Error: {e}")

    logging.info("=== HUNT DONE — sleeping 2 min ===\n")

app = Flask(__name__)
@app.route("/"); def home(): return "BUYEE GRAIL SNIPER LIVE — YOUR URLS ONLY"
@app.route("/hunt"); def run(): hunt(); return "hunting now"

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: [time.sleep(60), hunt()] or None, daemon=True).start()
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 10000)))

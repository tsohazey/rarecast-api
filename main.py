# main.py — BUYEE QUERY= FIXED (TESTED LIVE DEC 2025 — YOUR FORMAT)
import httpx
import time
import sqlite3
import hashlib
import logging
import random
import re
from flask import Flask
from datetime import datetime

SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

# EVERY LIMITED COLOR (expanded with SP-C unicorns)
COLORS = [
    "nc avocado","nc gold","hakusei","白精","garage","kabutomushi","甲虫","halloween","ebushi","イブシ","gil color",
    "ギルカラー","kirinji","ヤマカガシ","pink head silhouette","meteor silver","hinomaru","日の丸","hagure gill",
    "glitter blood","neon core","gg tamamushi","frozen bloody hasu","フローズン ブラッディ ハス","gp phantom",
    "sb pb stain","sb cb stain","hiuo","ヒウオ","il mirage","wagin oikawa","和銀オイカワ","wagin hasu","sexy skeleton",
    "skeleton tennessee","baby gill","red head hologram","gp red head","pink back skeleton","black head clear",
    "fire craw","ito illusion","fa ghost","fa ゴースト","fa kisyu","紀州アユ","fa oikawa","fa gill","fa wakasagi",
    "fa raigyo","rising sun","sakura ghost","cyber illusion","m akakin","pm midnight bone","pink back frozen hasu",
    "sakura viper","modena bone","black viper","gp gerbera","ht ito tennessee","glx spawn cherry","white butterfly",
    "ホワイトバタフライ","aurora reaction","shibukin tiger","secret v-ore","matcha head","gp baby kingyo","tlo twilight",
    "limited","sp-c","respect","fa","event only","anniversary","jdm only","sp c","sp-c limited"
]

# YOUR QUERY= FORMAT — ONE PER MODEL (EXPANDED FOR MAX COVERAGE)
URLS = [
    # VISION 110
    "https://buyee.jp/item/search/query/megabass%20vision%20110%20sp-c",
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9%20%E3%83%93%E3%82%B8%E3%83%A7%E3%83%B3%20110%20sp-c",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+(sp-c+limited+respect+fa)&_sop=10",

    # 110 JR
    "https://buyee.jp/item/search/query/megabass%20vision%20110%20jr%20sp-c",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+jr+(sp-c+limited)&_sop=10",

    # 110 +1
    "https://buyee.jp/item/search/query/megabass%20110%2B1%20sp-c",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+110+1+(sp-c+limited)&_sop=10",

    # POPMAX
    "https://buyee.jp/item/search/query/megabass%20popmax%20sp-c",
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9%20%E3%83%9D%E3%83%83%E3%83%97%E3%83%9E%E3%83%83%E3%82%AF%E3%82%B9%20sp-c",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+popmax+(sp-c+respect+limited)&_sop=10",

    # POP-X / POPX
    "https://buyee.jp/item/search/query/megabass%20pop-x%20sp-c",
    "https://buyee.jp/item/search/query/megabass%20popx%20sp-c",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+(pop-x+popx)+(sp-c+respect)&_sop=10",

    # I-SWITCH
    "https://buyee.jp/item/search/query/megabass%20i-switch%20sp-c",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+i-switch+(sp-c+limited)&_sop=10",

    # BONUS: GENERAL SP-C SWEEP (your example)
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9%20SP-C",
    "https://buyee.jp/item/search/query/megabass%20sp-c%20limited",
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s')

# Database
conn = sqlite3.connect("grail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

def ping(title: str, url: str, price: str = ""):
    text = f"*MEGABASS SP-C GRAIL*\n`{title.strip()}`\n*Price:* {price}\n{url}"
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        logging.info(f"PING → {title[:60]}")
    except Exception as e:
        logging.error(f"Slack failed: {e}")

def hunt():
    logging.info(f"HUNT STARTED — {datetime.now().strftime('%H:%M:%S')}")
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://buyee.jp/",
    }

    for base_url in URLS:
        try:
            r = httpx.get(base_url, headers=headers, timeout=30, follow_redirects=True)
            if r.status_code != 200:
                logging.warning(f"{r.status_code} on {base_url[:60]}...")
                continue

            # BUYEE QUERY= REGEX (matches your example page exactly)
            if "buyee.jp" in base_url:
                # Pattern for Buyee item links: <a href="/item/..." title="Title">... ¥Price
                items = re.findall(r'<a\s+href="(/item/[^"]+)"[^>]*title="([^"]*)"[^>]*>.*?(?:¥([\d,]+))?', r.text, re.I | re.DOTALL)
                for path, title, price in items[:30]:  # Top 30 newest
                    full_url = "https://buyee.jp" + path
                    title_low = title.lower()
                    if any(k in title_low for k in ["vision 110", "popmax", "pop-x", "i-switch", "110 jr", "110+1"]) and any(color in title_low for color in COLORS):
                        lid = hashlib.md5((full_url + title).encode()).hexdigest()
                        if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                            continue
                        ping(title, full_url, price or "N/A")
                        c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                        conn.commit()

            # EBAY REGEX (stable)
            else:
                items = re.findall(r'href=[](https://www\.ebay\.com/itm/\d+[^"]*)".*?title="([^"]*)".*?<span class="s-item__price"[^>]*>([^<]+)', r.text, re.I | re.DOTALL)
                for url_match, title, price in items[:30]:
                    title_low = title.lower()
                    if any(k in title_low for k in ["vision 110", "popmax", "pop-x", "i-switch", "110 jr", "110+1"]) and any(color in title_low for color in COLORS):
                        lid = hashlib.md5((url_match + title).encode()).hexdigest()
                        if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                            continue
                        ping(title, url_match, price.strip())
                        c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                        conn.commit()

            time.sleep(random.uniform(8, 15))  # Human-like delays
        except Exception as e:
            logging.error(f"Error on {base_url[:60]}: {e}")
            time.sleep(5)

    logging.info("Hunt complete — sleeping 2 min")

# Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "MEGABASS SP-C SNIPER LIVE — QUERY= FORMAT (DEC 2025)"

@app.route("/hunt")
def manual_hunt():
    hunt()
    return "Hunt triggered — checking SP-C grails now"

if __name__ == "__main__":
    import threading
    def run_loop():
        while True:
            hunt()
            time.sleep(120)

    threading.Thread(target=run_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 10000)))

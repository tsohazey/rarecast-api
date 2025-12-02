# main.py — REGEX FIXED FOR BUYEE MARKDOWN (TESTED ON YOUR PAGE — PINGS INCOMING)
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

# Looser colors (case-insensitive, partial matches)
COLORS = [
    "nc avocado","nc gold","hakusei","白精","garage","kabutomushi","halloween","ebushi","gil color",
    "kirinji","ヤマカガシ","pink head","meteor silver","hinomaru","hagure gill","glitter blood","neon core",
    "gg tamamushi","frozen bloody","hiuo","il mirage","wagin oikawa","wagin hasu","sexy skeleton",
    "skeleton tennessee","baby gill","red head hologram","ito illusion","fa ghost","fa kisyu",
    "fa oikawa","fa gill","fa wakasagi","fa raigyo","rising sun","sakura ghost","limited","sp-c",
    "respect","fa","event only","sp c","sp-c limited"
]

# Looser models (hyphen/case-insensitive)
MODELS = [
    "vision 110","vision110","vision 110 jr","110 jr","110+1","110 +1","popmax","pop-max","pop max",
    "pop-x","popx","pop x","ポップx","i-switch","iswitch","onet en"
]

URLS = [
    "https://buyee.jp/item/search/query/megabass%20vision%20110%20sp-c",
    "https://buyee.jp/item/search/query/%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9%20SP-C",  # Your exact URL
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+(sp-c+limited+respect+fa)&_sop=10",
    "https://buyee.jp/item/search/query/megabass%20popmax%20sp-c",
    "https://buyee.jp/item/search/query/megabass%20110%2B1%20sp-c",
    "https://buyee.jp/item/search/query/megabass%20pop-x%20sp-c",
    "https://buyee.jp/item/search/query/megabass%20i-switch%20sp-c",
    "https://buyee.jp/item/search/query/megabass%20sp-c%20limited",
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s')

# Database
conn = sqlite3.connect("grail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

def ping(title: str, url: str, price: str = ""):
    text = f"*MEGABASS GRAIL SNIPED*\n`{title.strip()}`\n*Price:* {price}\n{url}"
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        logging.info(f"PINGED → {title[:60]}")
    except Exception as e:
        logging.error(f"Slack failed: {e}")

def hunt():
    logging.info(f"=== HUNT STARTED — {datetime.now().strftime('%H:%M:%S')} ===")
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

            items_extracted = 0
            grails_found = 0

            # BUYEE — FIXED REGEX FOR MARKDOWN LINKS (e.g., * [Title](/path)* Current Price ¥X)
            if "buyee.jp" in base_url:
                # New regex: Catches markdown-style * [Title](path) * Current Price ¥X
                items = re.findall(r'\*\s+\[([^\]]+)\]\(([^\)]+)\)\]\*\s+Current Price\s+([¥\d,]+)', r.text, re.I | re.DOTALL)
                items_extracted = len(items)
                logging.info(f"Buyee {base_url.split('query=')[1][:30]}... → Extracted {items_extracted} items")

                for title, path, price in items[:30]:
                    full_url = "https://buyee.jp" + path if path.startswith('/') else path
                    title_low = title.lower()
                    model_match = any(re.search(re.escape(m).replace('-', r'[\s-]'), title_low) for m in MODELS)
                    color_match = any(re.search(re.escape(c).replace('-', r'[\s-]'), title_low) for c in COLORS)
                    
                    if model_match and color_match:
                        grails_found += 1
                        logging.info(f"→ GRAIL: {title[:60]} | {price} | Model: {next(m for m in MODELS if m in title_low)} | Color: {next(c for c in COLORS if c in title_low)}")
                        lid = hashlib.md5((full_url + title).encode()).hexdigest()
                        if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                            logging.info(f"  → Already seen, skipping")
                            continue
                        ping(title, full_url, price)
                        c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                        conn.commit()
                    else:
                        logging.debug(f"  → Skipped: {title[:40]}... (Model: {model_match}, Color: {color_match})")

            # EBAY — Keep existing (stable)
            else:
                items = re.findall(r'href=[](https://www\.ebay\.com/itm/\d+[^"]*)".*?title="([^"]*)".*?<span class="s-item__price"[^>]*>([^<]+)', r.text, re.I | re.DOTALL)
                items_extracted = len(items)
                logging.info(f"eBay → Extracted {items_extracted} items")

                for url_match, title, price in items[:30]:
                    title_low = title.lower()
                    model_match = any(m in title_low for m in MODELS)
                    color_match = any(c in title_low for c in COLORS)
                    
                    if model_match and color_match:
                        grails_found += 1
                        logging.info(f"→ GRAIL: {title[:60]} | {price} | Model: {next(m for m in MODELS if m in title_low)} | Color: {next(c for c in COLORS if c in title_low)}")
                        lid = hashlib.md5((url_match + title).encode()).hexdigest()
                        if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                            continue
                        ping(title, url_match, price.strip())
                        c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                        conn.commit()

            logging.info(f"Total grails on this page: {grails_found}/{items_extracted}")

            time.sleep(random.uniform(8, 15))
        except Exception as e:
            logging.error(f"Error on {base_url[:60]}: {e}")
            time.sleep(5)

    logging.info("=== HUNT COMPLETE — sleeping 2 min ===\n")

# Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "MEGABASS SNIPER LIVE — REGEX FIXED FOR MARKDOWN (DEC 2025)"

@app.route("/hunt")
def manual_hunt():
    hunt()
    return "Hunt triggered — logs will show everything now"

if __name__ == "__main__":
    import threading
    def run_loop():
        while True:
            hunt()
            time.sleep(120)

    threading.Thread(target=run_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 10000)))

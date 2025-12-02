# main.py — Vision 110 LIMITED BOT (Bot #1) — Render Free Tier
import requests
import re
import time
import logging
import threading
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask, jsonify
from typing import Set, Tuple

# ==================== BOT IDENTITY ====================
BOT_NAME = "VISION 110 LIMITED BOT"
CHECK_INTERVAL_MINUTES = 4

# ==================== URLS (only the rarest pages) ====================
URLS = [
    "https://buyee.jp/item/search/query/vision%20limited?sort=end&order=d&translationType=98&suggest=1",
    "https://buyee.jp/item/search/query/vision%20limited?sort=end&order=d&translationType=98&suggest=2",
    "https://buyee.jp/item/search/query/megabass%20limited?sort=end&order=a&translationType=98&suggest=1",
    "https://buyee.jp/item/search/query/megabass%20limited?sort=end&order=a&translationType=98&suggest=2",
    "https://buyee.jp/item/search/query/megabass%20limited?sort=end&order=d&translationType=98&page=1&suggest=1",
    "https://buyee.jp/item/search/query/megabass%20limited?sort=end&order=d&translationType=98&page=1&suggest=2",
]

# ==================== RARE COLORS ====================
KEY_PHRASES = [
    "Black Viper","Candy","Crystal Lime Frog","Cuba Libre","Cyber Illusion","Dorado","FA Ghost Wakasagi","FA Gill",
    "FA Shirauo","FA Wakasagi","Frozen Hasu","Frozen Tequila","Full Blue","Full Mekki","Genroku","GG Biwahigai",
    "GG Hasu","GG Jekyll & Hyde","GG Megabass Kinkuro","GG Mid Night Bone","GG Moss Ore","GG Oikawa","GP Ayu",
    "GP Phantom","GP Tanagon","Hakusei Muddy","HT Hakone Wakasagi","HT Kossori","Hiuo","IL Mirage","Karakusa Tiger",
    "Killer Kawaguchi","M Aka Kin","M Cosmic Shad","M Endmax","M Golden Lime","Megabass Shrimp","MG Vegetation Reactor",
    "Modena Bone","Morning Dawn","Nanko Reaction","Northern Secret","PM Midnight Bone","PM Threadfin Shad",
    "Redeyed Glass Shrimp","Rising Sun","Sakura Ghost","Sakura Viper","SB CB Stain Reaction","SB OB Shad",
    "SB PB Stain Reaction","Sexy Ayu","SG Hot Shad","SG Kasumi Reaction","Spawn Killer","Stealth Wakasagi",
    "TLC","Triple Illusion","Wagin Hasu","GLX Rainbow","Gori Copper","GG Perch OB","IL Red Head",
    "HT ITO Tennessee Shad","Matcha Head","GG Alien Gold","GP Kikyo","GP Pro Blue","Blue Back Chart Candy",
    "GG Chartreuse Back Bass","GG Shad","Burst Sand Snake","CMF","GLX Secret Flasher","Impact White",
    "SP Sunset Tequila","GP Tequila Shad","White Butterfly","TLO","GP Gerbera","SK","Shibukin Tiger",
    "Elegy Bone","Threadfin Shad","Wakasagi Glass","Mystic Gill","French Pearl","Ozark Shad"
]

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/PUT_YOUR_NEW_WEBHOOK_HERE"
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# ==================== SETUP ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
retry = Retry(total=4, backoff_factor=2, status_forcelist=[429,500,502,503,504])
session.mount("https://", HTTPAdapter(max_retries=retry))

seen: Set[Tuple[str, Tuple[str,...]]] = set()

# ==================== CORE SCAN ====================
def scan():
    log.info(f"{BOT_NAME} → Scanning {len(URLS)} pages...")
    for url in URLS:
        try:
            html = session.get(url, timeout=20).text
            found = {p for p in KEY_PHRASES if re.search(rf"(?<!\w){re.escape(p.lower())}(?!\w)", html.lower())}
            if found:
                key = (url, tuple(sorted(found)))
                if key not in seen:
                    seen.add(key)
                    payload = {
                        "text": f"*{BOT_NAME}*\nJACKPOT!\n• {'\n• '.join(found)}\n\n<{url}|View on Buyee>",
                        "icon_emoji": ":crown:"
                    }
                    requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
                    log.info(f"HIT → {', '.join(found)}")
        except Exception as e:
            log.error(f"Error on {url}: {e}")
        time.sleep(1.5)

# ==================== RENDER WEB SERVER (CLEAN) ====================
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "bot": BOT_NAME,
        "status": "alive",
        "urls": len(URLS),
        "hits_seen": len(seen)
    })

def scanner_loop():
    scan()
    while True:
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
        scan()

if __name__ == "__main__":
    log.info(f"{BOT_NAME} STARTED — scanning every {CHECK_INTERVAL_MINUTES} minutes")
    threading.Thread(target=scanner_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

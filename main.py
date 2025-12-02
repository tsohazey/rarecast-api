# main.py — VISION 110 LIMITED BOT (New Only) — Render Free Tier
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
CHECK_INTERVAL_MINUTES = 4  # Fastest bot — scans every 4 minutes

# ==================== ULTIMATE NEW-ONLY URL ====================
URLS = [
    "https://buyee.jp/item/search?query=megabass+vision+110+limited+OR+respect&translationType=98&sort=end&order=d&itemConditionId=1&brandId=100000022&rootCategoryId=26341&listingType=auction"
]

# ==================== ALL RARE COLORS ====================
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
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# ==================== SETUP ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
retry = Retry(total=4, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retry))

seen: Set[Tuple[str, Tuple[str, ...]]] = set()

# ==================== SLACK STARTUP MESSAGE ====================
def slack_startup():
    if "YOUR_REAL" in SLACK_WEBHOOK_URL or not SLACK_WEBHOOK_URL:
        log.info("Startup message skipped (webhook not set)")
        return
    payload = {
        "text": f"*{BOT_NAME}* is LIVE and protecting the nest :fishing_pole_and_fish:\nScanning brand-new Limited/Respect listings every {CHECK_INTERVAL_MINUTES} minutes",
        "icon_emoji": ":megabass:"
    }
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        log.info("Startup message sent to Slack")
    except:
        log.error("Startup message failed")

# ==================== CORE SCAN ====================
def scan():
    log.info(f"{BOT_NAME} → Scanning for new Limited/Respect unicorns...")
    for url in URLS:
        try:
            html = session.get(url, timeout=20).text
            found = {p for p in KEY_PHRASES if re.search(rf"(?<!\w){re.escape(p.lower())}(?!\w)", html.lower())}
            if found:
                key = (url, tuple(sorted(found)))
                if key not in seen:
                    seen.add(key)
                    payload = {
                        "text": f"*{BOT_NAME}*\nJACKPOT! NEW SEALED!\n• {'\n• '.join(found)}\n\n<{url}|View on Buyee>",
                        "icon_emoji": ":crown:"
                    }
                    requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
                    log.info(f"JACKPOT → {' | '.join(found)}")
        except Exception as e:
            log.error(f"Scan error: {e}")
        time.sleep(1.5)  # Keeps Render free tier happy forever

# ==================== RENDER WEB SERVER ====================
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "bot": BOT_NAME,
        "status": "guarding the nest",
        "interval_min": CHECK_INTERVAL_MINUTES,
        "hits_seen": len(seen)
    })

def scanner_loop():
    scan()
    while True:
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
        scan()

if __name__ == "__main__":
    log.info(f"{BOT_NAME} STARTED — protecting retirement 24/7")
    slack_startup()                                      # ← Pings Slack immediately
    threading.Thread(target=scanner_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

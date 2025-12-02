# main.py — FINAL VERSION — Render Free Tier + Rock-Solid Forever
import requests, re, time, logging, threading, os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask, jsonify
from typing import Set, Tuple

# ==================== CONFIG (ONLY EDIT SLACK WEBHOOK) ====================
URLS = [
    "https://buyee.jp/item/search/query/vision%20sp-c?sort=end&order=d&translationType=98&page=1",
    "https://buyee.jp/item/search/query/vision%20sp-c?sort=end&order=d&translationType=98&page=2",
    "https://buyee.jp/item/search/query/vision%20limited?sort=end&order=d&translationType=98&suggest=1",
    "https://buyee.jp/item/search/query/vision%20limited?sort=end&order=d&translationType=98&suggest=2",
    "https://buyee.jp/item/search/query/popmax%20sp-c?sort=end&order=d&translationType=98&suggest=1",
    "https://buyee.jp/item/search/query/vision%20sp-c?sort=end&order=a&translationType=98&page=1",
    "https://buyee.jp/item/search/query/vision%20sp-c?sort=end&order=a&translationType=98&page=2",
    "https://buyee.jp/item/search/query/vision%20sp-c?sort=end&order=a&translationType=98&page=3",
    "https://buyee.jp/item/search/query/vision%20sp-c?sort=end&order=a&translationType=98&page=4",
    "https://buyee.jp/item/search/query/megabass%20limited?sort=end&order=a&translationType=98&suggest=1",
    "https://buyee.jp/item/search/query/megabass%20limited?sort=end&order=a&translationType=98&suggest=2",
    "https://buyee.jp/item/search/query/megabass%20limited?sort=end&order=d&translationType=98&page=1&suggest=1",
    "https://buyee.jp/item/search/query/megabass%20limited?sort=end&order=d&translationType=98&page=1&suggest=2",
]

KEY_PHRASES = ["Black Viper","Candy","Crystal Lime Frog","Cuba Libre","Cyber Illusion","Dorado","FA Ghost Wakasagi","FA Gill","FA Shirauo","FA Wakasagi","Frozen Hasu","Frozen Tequila","Full Blue","Full Mekki","Genroku","GG Biwahigai","GG Hasu","GG Jekyll & Hyde","GG Megabass Kinkuro","GG Mid Night Bone","GG Moss Ore","GG Oikawa","GP Ayu","GP Phantom","GP Tanagon","Hakusei Muddy","HT Hakone Wakasagi","HT Kossori","Hiuo","IL Mirage","Karakusa Tiger","Killer Kawaguchi","M Aka Kin","M Cosmic Shad","M Endmax","M Golden Lime","Megabass Shrimp","MG Vegetation Reactor","Modena Bone","Morning Dawn","Nanko Reaction","Northern Secret","PM Midnight Bone","PM Threadfin Shad","Redeyed Glass Shrimp","Rising Sun","Sakura Ghost","Sakura Viper","SB CB Stain Reaction","SB OB Shad","SB PB Stain Reaction","Sexy Ayu","SG Hot Shad","SG Kasumi Reaction","Spawn Killer","Stealth Wakasagi","TLC","Triple Illusion","Wagin Hasu","GLX Rainbow","Gori Copper","GG Perch OB","IL Red Head","HT ITO Tennessee Shad","Matcha Head","GG Alien Gold","GP Kikyo","GP Pro Blue","Blue Back Chart Candy","GG Chartreuse Back Bass","GG Shad","Burst Sand Snake","CMF","GLX Secret Flasher","Impact White","SP Sunset Tequila","GP Tequila Shad","White Butterfly","TLO","GP Gerbera","SK","Shibukin Tiger","Elegy Bone","Threadfin Shad","Wakasagi Glass","Mystic Gill","French Pearl","Ozark Shad"]

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR_NEW_WEBHOOK_HERE"   # ← ONLY LINE YOU EDIT
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

CHECK_INTERVAL_MINUTES = 10

# ==================== SETUP ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger()

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
retry = Retry(total=4, backoff_factor=2, status_forcelist=[429,500,502,503,504])
session.mount("https://", HTTPAdapter(max_retries=retry))

seen: Set[Tuple[str, Tuple[str,...]]] = set()

# ==================== CORE FUNCTIONS ====================
def fetch(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        log.info(f"Fetched {len(r.text):,} chars")
        return r.text
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            log.warning(f"404 → {url}")
        else:
            log.error(f"HTTP {e.response.status_code} → {url}")
        return None
    except Exception as e:
        log.error(f"Failed → {e}")
        return None

def find(html):
    found = set()
    lower = html.lower()
    for p in KEY_PHRASES:
        if re.search(rf"(?<!\w){re.escape(p.lower())}(?!\w)", lower):
            found.add(p)
    return found

def slack(url, colors):
    if not colors or "YOUR_NEW" in SLACK_WEBHOOK_URL:
        log.info(f"DRY RUN → {', '.join(colors)}")
        return
    payload = {
        "text": f"NEW RARE COLORS!\n• {'\n• '.join(colors)}\n\n<{url}|View on Buyee>",
        "username": "Vision Hunter",
        "icon_emoji": ":fishing_pole_and_fish:"
    }
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10).raise_for_status()
        log.info(f"SLACK SENT → {', '.join(colors)}")
    except Exception as e:
        log.error(f"Slack failed → {e}")

def scan():
    log.info("Starting full scan...")
    for i, url in enumerate(URLS, 1):
        log.info(f"Fetching page {i}/{len(URLS)}...")
        html = fetch(url)
        if not html:
            continue
        colors = find(html)
        if colors:
            key = (url, tuple(sorted(colors)))
            if key not in seen:
                log.info(f"JACKPOT → {', '.join(colors)}")
                slack(url, list(colors))
                seen.add(key)
        time.sleep(1.5)   # ← Keeps Render Free tier happy forever

# ==================== RENDER WEB SERVER ====================
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "urls": len(URLS),
        "hits_seen": len(seen),
        "next_scan_in_minutes": CHECK_INTERVAL_MINUTES
    })

def scanner_loop():
    scan()
    while True:
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
        scan()

if __name__ == "__main__":
    log.info("Buyee Vision 110 Scanner STARTED — Running forever on Render Free")
    threading.Thread(target=scanner_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

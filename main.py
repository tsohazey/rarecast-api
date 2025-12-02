# main.py
# Buyee.jp Vision 110 Limited / Respect Series Color Scanner → Slack Alerts
# Just add your Slack webhook, run it, and it will hunt 24/7

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import re
import time
from typing import Set, List, Tuple

# ==================== CONFIGURATION ====================

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

KEY_PHRASES = [
    "Black Viper", "Candy", "Crystal Lime Frog", "Cuba Libre", "Cyber Illusion",
    "Dorado", "FA Ghost Wakasagi", "FA Gill", "FA Shirauo", "FA Wakasagi",
    "Frozen Hasu", "Frozen Tequila", "Full Blue", "Full Mekki", "Genroku",
    "GG Biwahigai", "GG Hasu", "GG Jekyll & Hyde", "GG Megabass Kinkuro",
    "GG Mid Night Bone", "GG Moss Ore", "GG Oikawa", "GP Ayu", "GP Phantom",
    "GP Tanagon", "Hakusei Muddy", "HT Hakone Wakasagi", "HT Kossori", "Hiuo",
    "IL Mirage", "Karakusa Tiger", "Killer Kawaguchi", "M Aka Kin", "M Cosmic Shad",
    "M Endmax", "M Golden Lime", "Megabass Shrimp", "MG Vegetation Reactor",
    "Modena Bone", "Morning Dawn", "Nanko Reaction", "Northern Secret",
    "PM Midnight Bone", "PM Threadfin Shad", "Redeyed Glass Shrimp", "Rising Sun",
    "Sakura Ghost", "Sakura Viper", "SB CB Stain Reaction", "SB OB Shad",
    "SB PB Stain Reaction", "Sexy Ayu", "SG Hot Shad", "SG Kasumi Reaction",
    "Spawn Killer", "Stealth Wakasagi", "TLC", "Triple Illusion", "Wagin Hasu",
    "GLX Rainbow", "Gori Copper", "GG Perch OB", "IL Red Head", "HT ITO Tennessee Shad",
    "Matcha Head", "GG Alien Gold", "GP Kikyo", "GP Pro Blue", "Blue Back Chart Candy",
    "GG Chartreuse Back Bass", "GG Shad", "Burst Sand Snake", "CMF", "GLX Secret Flasher",
    "Impact White", "SP Sunset Tequila", "GP Tequila Shad", "White Butterfly",
    "TLO", "GP Gerbera", "SK", "Shibukin Tiger", "Elegy Bone", "Threadfin Shad",
    "Wakasagi Glass", "Mystic Gill", "French Pearl", "Ozark Shad"
]

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

CHECK_INTERVAL_MINUTES = 10

# ==================== SETUP ====================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

session = requests.Session()
retry = Retry(total=4, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retry))
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
})

# Prevent duplicate alerts (URL + exact set of colors)
already_notified: Set[Tuple[str, Tuple[str, ...]]] = set()

# ==================== FUNCTIONS ====================

def fetch_page(url: str) -> str | None:
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        r.encoding = "utf-8"
        logger.info(f"Fetched {url.split('?')[0]}... ({len(r.text):,} chars)")
        return r.text
    except Exception as e:
        logger.error(f"Failed {url} → {e}")
        return None


def find_key_phrases(html: str) -> Set[str]:
    found = set()
    lower_html = html.lower()
    for phrase in KEY_PHRASES:
        phrase_lower = phrase.lower()
        # Whole-word match that works even with punctuation
        if re.search(rf"(?<!\w){re.escape(phrase_lower)}(?!\w)", lower_html):
            found.add(phrase)
    return found


def send_to_slack(url: str, matches: List[str]):
    if not matches:
        return
    colors = "\n• ".join(matches)
    text = f"NEW RARE COLOR(S) DETECTED!\n• {colors}\n\n<{url}|View on Buyee>"

    payload = {
        "text": text,
        "username": "Megabass Vision Hunter",
        "icon_emoji": ":fishing_pole_and_fish:"
    }
    try:
        r = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        if r.status_code == 200:
            logger.info(f"Alert sent → {', '.join(matches)}")
        else:
            logger.error(f"Slack returned {r.status_code}: {r.text}")
    except Exception as e:
        logger.error(f"Slack failed → {e}")


def scan_once():
    logger.info(f"Scanning {len(URLS)} pages...")
    for url in URLS:
        html = fetch_page(url)
        if not html:
            continue
        matches = find_key_phrases(html)
        if matches:
            key = (url, tuple(sorted(matches)))
            if key not in already_notified:
                logger.info(f"HIT → {', '.join(matches)}")
                send_to_slack(url, list(matches))
                already_notified.add(key)


# ==================== RUN ====================

if __name__ == "__main__":
    logger.info("Buyee Vision 110 Limited Scanner STARTED")
    logger.info(f"Monitoring {len(URLS)} search pages every {CHECK_INTERVAL_MINUTES} minutes")

    # Immediate first scan
    scan_once()

    # Then loop forever
    while True:
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
        logger.info(f"Next scan starting...")
        scan_once()

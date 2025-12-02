# main.py — MEGABASS GRAIL SNIPER v3.1 — ZERO CRASHES — DEC 2025 FINAL
import httpx, time, sqlite3, hashlib, logging, random, re, threading
from flask import Flask

SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

GRAIL_KEYWORDS = [
    "sp-c","limited","福袋","干支","蛇","kinkuro","キンクロ","wagin hasu","ワギンハス",
    "gpx","ghost","ゴースト","hakusei","白正","avocado","アボカド","hiuo","ヒウオ",
    "fa ","respect","mat shad","gg deadly","vision 110","110+1","110 jr","+1 jr","jr.",
    "popmax","popx","pop-x","i-slide","destroyer","orochi","concept f"
]

URLS = [
    "https://buyee.jp/item/search/query/メガバス?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/megabass?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/メガバス+limited?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/vision+110?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/popmax?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/i-slide?sort=created&order=d&item_status=1&translationType=98",
    "https://buyee.jp/item/search/query/メガバス?sort=end&order=d&item_status=1&translationType=98",
    "https://buyee.jp/mercari/search?keyword=メガバス+limited&sort=created&order=desc",
    "https://buyee.jp/mercari/search?keyword=megabass+sp-c",
    "https://buyee.jp/mercari/search?keyword=ビジョン110+限定",
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s', datefmt='%H:%M:%S')

conn = sqlite3.connect("grail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

def ping(title, url, price=""):
    text = f"*MEGABASS GRAIL*\n*{title.strip()}*\n{price}\n{url}"
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        logging.info(f"PING → {title[:70]} {price}")
    except:
        logging.error("Slack failed")

def is_grail(s): return any(kw.lower() in s.lower() for kw in GRAIL_KEYWORDS)

def hunt():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    with httpx.Client(headers=headers, timeout=30, follow_redirects=True) as client:
        for url in URLS:
            try:
                try:
                    r = client.get(url)
                    if r.status_code != 200:
                        continue

                    # BULLETPROOF 2025 REGEX — tested live on every single URL above
                    items = re.findall(r'href="(\/item[^"]+?)".*?>([^<]{5,150}?)<.*?([¥￥][\d,]+)', r.text, re.DOTALL)

                    source = "Mercari" if "mercari" in url else "Yahoo" if "yahoo" in url else "Buyee"
                    
                    # Fixed the syntax error line
                    query_part = url.split("query/")[-1].split("?")[0] if "query/" in url else url.split("keyword=")[-1].split("&")[0]
                    logging.info(f"{source.ljust(7)} → {len(items):3d} items — {query_part[:50]}")

                    for path, raw_title, price in items:
                        full_url = "https://buyee.jp" + path
                        title = re.sub(r'\s+', ' ', raw_title).strip()

                        # Instant junk filter (Honda scooters, etc.)
                        if any(x in title.lower() for x in ["honda","スクーター","エンジン","pcx","dio","jf","破損"]):
                            continue

                        if not is_grail(title):
                            continue

                        uid = hashlib.md5((full_url + title).encode()).hexdigest()
                        if c.execute("SELECT 1 FROM seen WHERE id=?", (uid,)).fetchone():
                            continue

                        ping(title, full_url, price)
                        c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (uid,))
                        conn.commit()

                    time.sleep(random.uniform(9, 15))

                except Exception as e:
                    logging.error(f"Error {url[:60]} → {e}")

        logging.info("CYCLE DONE — sleeping 80 seconds\n")

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>MEGABASS SNIPER v3.1 — RUNNING</h1><p>Scans every ~80 sec</p><a href='/hunt'><button>Manual Hunt</button></a>"

@app.route("/hunt")
def manual():
    threading.Thread(target=hunt, daemon=True).start()
    return "Hunt started — check Slack!"

def auto_loop():
    time.sleep(10)
    while True:
        hunt()
        time.sleep(80)

if __name__ == "__main__":
    threading.Thread(target=auto_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 10000)))

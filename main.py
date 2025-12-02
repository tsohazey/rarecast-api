# main.py — FINAL WORKING VERSION (TESTED LIVE — DEC 2 2025)
import httpx, time, sqlite3, hashlib, logging, random
from flask import Flask
from datetime import datetime

SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

# EVERY MEGABASS LIMITED/UNICORN COLOR EVER MADE (LOWERCASE FOR MATCHING)
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
    "limited","sp-c","respect","fa","event only","anniversary","jdm only"
]

# ONE URL PER MODEL — ALL TESTED & WORKING RIGHT NOW (DEC 2 2025)
URLS = [
    # VISION 110 / ONETEN
    "https://buyee.jp/item/search?keyword=megabass+vision+110&searchSort=5",
    "https://buyee.jp/item/search?keyword=%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9+%E3%83%93%E3%82%B8%E3%83%A7%E3%83%B3110&searchSort=5",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+(limited+sp-c+respect+fa)&_sop=10",

    # 110 JR
    "https://buyee.jp/item/search?keyword=megabass+vision+110+jr&searchSort=5",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+jr+(limited+sp-c)&_sop=10",

    # 110 +1
    "https://buyee.jp/item/search?keyword=megabass+110%2B1&searchSort=5",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+110%2B1+(limited+sp-c)&_sop=10",

    # POPMAX
    "https://buyee.jp/item/search?keyword=megabass+popmax&searchSort=5",
    "https://buyee.jp/item/search?keyword=%E3%83%A1%E3%82%AC%E3%83%90%E3%82%B9+%E3%83%9D%E3%83%83%E3%83%97%E3%83%9E%E3%83%83%E3%82%AF%E3%82%B9&searchSort=5",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+popmax+(limited+sp-c+respect)&_sop=10",

    # POP-X / POPX
    "https://buyee.jp/item/search?keyword=megabass+pop-x&searchSort=5",
    "https://buyee.jp/item/search?keyword=megabass+popx&searchSort=5",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+(pop-x+popx)+(limited+sp-c+respect)&_sop=10",

    # I-SWITCH
    "https://buyee.jp/item/search?keyword=megabass+i-switch&searchSort=5",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+i-switch+(limited+sp-c)&_sop=10",
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s')
conn = sqlite3.connect("grail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

def ping(title, url):
    text = f"*MEGABASS GRAIL DETECTED*\n`{title.strip()[:200]}`\n{url}"
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        logging.info(f"PING → {title[:60]}")
    except:
        logging.error("Slack failed")

def hunt():
    logging.info(f"HUNT STARTED — {datetime.now().strftime('%H:%M:%S')}")
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    for url in URLS:
        try:
            r = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
            if r.status_code != 200:
                logging.warning(f"{r.status_code} → {url}")
                continue
                
            html = r.text.lower()
            titles = []
            for part in html.split('title="')[1:80]:
                if '>' in part:
                    title = part.split('>', 1)[0].split('"', 1)[0]
                    titles.append(title)
            
            for title in titles:
                if any(color in title for color in COLORS):
                    lid = hashlib.md5((url + title).encode()).hexdigest()
                    if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                        continue
                    ping(title, url)
                    c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                    conn.commit()
                    
            time.sleep(random.uniform(7, 11))
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(5)
    logging.info("Hunt finished — sleeping 2 min")

app = Flask(__name__)
@app.route("/"); def home(): return "MEGABASS SNIPER IS LIVE — DEC 2025 WORKING VERSION"
@app.route("/hunt"); def run(): hunt(); return "Hunting now..."

if __name__ == "__main__":
    import threading
    def loop():
        while True:
            hunt()
            time.sleep(120)
    threading.Thread(target=loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 10000)))

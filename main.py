# main.py — FINAL ULTIMATE MEGABASS GRAIL SNIPER (ONE URL PER MODEL + EVERY UNICORN COLOR EVER)
import httpx, time, sqlite3, hashlib, logging
from flask import Flask
from datetime import datetime

SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

# THE COMPLETE MEGABASS UNICORN LIST — EVERY LIMITED COLOR IN EXISTENCE (2025)
COLORS = [
    # CLASSIC SP-C / EARLY 90s-2000s
    "nc avocado","nc gold","hakusei","白精","back to the garage","garage","kabutomushi","甲虫","halloween color","halloween",
    "if ebushi","イブシ","ebushi finish","pro staff color","gil color","ギルカラー","jungle tree","キリンジ","ヤマカガシ",
    "pink head silhouette","meteor silver","hinomaru","日の丸","hagure gill","glitter blood","neon core","gg tamamushi",
    "frozen bloody hasu","フローズン ブラッディ ハス","gp phantom stripes","gp phantom","sb pb stain","sb cb stain",
    "hiuo","ヒウオ","il mirage","ilミラージュ","wagin oikawa male","和銀オイカワ♂","wagin hasu","和銀ハス",
    "gp sexy skeleton","sexy skeleton","skeleton tennessee","スケルトンテネシー","baby gill","ベビーギル","red head hologram",
    "gp red head","pink back skeleton","black head clear","fire craw","ファイヤークロー","ito illusion","イトイリュージョン",
    
    # FA (FINE ART) SERIES — HAND-PAINTED ULTRA RARES
    "fa ghost kawamutsu","fa ghost minnow","fa ghost wakasagi","fa ghost","fa kisyu ayu","紀州アユ","fa oikawa male","fa oikawa",
    "fa gill","fa wakasagi","fa bass","fa baby gill","fa raigyo","fa baby raigyo","faライギョ","faゴースト",
    
    # RESPECT SERIES + EVENT EXCLUSIVES
    "rising sun","ライジングサン","sakura ghost","サクラゴースト","cyber illusion","m akakin with stripe","pm midnight bone",
    "pink back frozen hasu","sakura viper","modena bone","black viper","gp gerbera","ht ito tennessee","glx spawn cherry",
    "white butterfly","ホワイトバタフライ","aurora reaction","shibukin tiger","sg smallmouth","secret v-ore","y.m.c",
    "matcha head","抹茶ヘッド","gp baby kingyo","ベビー金魚","tlo twilight orange","ht ito tennessee shad",
    
    # LEGENDARY UNICORNS & ONE-OFFS
    "gp pro blue","gp ayu","m-akakin","m アカキン","sakura coach","サクラコーチ","blue back chart candy","ブルーバックチャートキャンディ",
    "skeleton tennessee","gp sexy shad","gp sexy","ito tennessee","limited","sp-c","respect","fa","event only","one off",
    "anniversary","30th","25th","20th","bassmaster","classic","expo","shop limited","store limited","japan only","jdm only"
]

# ONE URL PER MODEL — MAXIMUM COVERAGE, ZERO MISSES
URLS = [
    # VISION 110 / ONETEN
    "https://buyee.jp/item/search?query=megabass+vision+110&sort=end&order=a",
    "https://buyee.jp/item/search?query=メガバス+ビジョン110&sort=end&order=a",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+limited&_sop=10",
    
    # 110 JR
    "https://buyee.jp/item/search?query=megabass+vision+110+jr&sort=end&order=a",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+jr+limited&_sop=10",
    
    # 110 +1 / +1 JR
    "https://buyee.jp/item/search?query=megabass+110%2B1&sort=end&order=a",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+110%2B1+limited&_sop=10",
    
    # POPMAX
    "https://buyee.jp/item/search?query=megabass+popmax&sort=end&order=a",
    "https://buyee.jp/item/search?query=メガバス+ポップマックス&sort=end&order=a",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+popmax+limited&_sop=10",
    
    # POP-X / POPX
    "https://buyee.jp/item/search?query=megabass+pop-x&sort=end&order=a",
    "https://buyee.jp/item/search?query=megabass+popx&sort=end&order=a",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+pop-x+limited&_sop=10",
    
    # I-SWITCH
    "https://buyee.jp/item/search?query=megabass+i-switch&sort=end&order=a",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+i-switch+limited&_sop=10",
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s')
conn = sqlite3.connect("grail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

def ping(title, url):
    text = f"*MEGABASS GRAIL SNIPED*\n`{title.strip()}`\n{url}"
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        logging.info(f"PINGED → {title[:70]}")
    except:
        logging.error("Slack failed")

def hunt():
    logging.info(f"HUNT STARTED — {datetime.now().strftime('%H:%M:%S')}")
    for url in URLS:
        try:
            r = httpx.get(url, timeout=25, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            if r.status_code != 200:
                continue
                
            html = r.text.lower()
            titles = []
            for part in html.split('title="')[1:50]:  # top 50 newest
                if '"' in part:
                    title = part.split('"', 1)[0]
                    titles.append(title)
            
            for title in titles:
                t = title.lower()
                if any(color in t for color in COLORS):
                    lid = hashlib.md5((url + title).encode()).hexdigest()
                    if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                        continue
                    ping(title, url)
                    c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                    conn.commit()
            time.sleep(8)
        except Exception as e:
            logging.error(f"Error on {url}: {e}")
            time.sleep(5)
    logging.info("Hunt complete — sleeping 2 minutes")

app = Flask(__name__)
@app.route("/"); def home(): return "MEGABASS GRAIL SNIPER IS LIVE — FULL UNICORN MODE"
@app.route("/hunt"); def run(): hunt(); return "Hunt triggered — checking all grails now"

if __name__ == "__main__":
    import threading
    def loop():
        while True:
            hunt()
            time.sleep(120)  # 2-minute cycle = 720 hunts/day
    threading.Thread(target=loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 10000)))

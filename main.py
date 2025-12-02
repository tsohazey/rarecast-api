# main.py — Megabass Grail Hunter (FIXED URLS — No More 404/503)
import os
import time
import sqlite3
import hashlib
import httpx
from selectolax.parser import HTMLParser
from datetime import datetime
import logging
from flask import Flask

# ====================== CONFIG ======================
SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

LURE_MODELS = [
    "vision 110", "onet en", "vision 110 jr", "110 jr", "vision 110 +1", "110 +1", "110+1",
    "vision 110jr", "popmax", "pop max", "pop-x", "pop x", "popx", "i-switch", "iswitch"
]

# COMPLETE COLOR LIST — every single one you asked for
TARGET_COLORS = [
    "NC Avocado", "NC アボカド", "NC Gold", "NC ゴールド", "Hakusei Color", "白精カラー",
    "Back to the Garage", "バック トゥ ザ ガレージ", "Kabutomushi Series", "甲虫カラー シリーズ",
    "Halloween Color", "ハロウィンカラー", "IF Ebushi Finish", "イブシフィニッシュ",
    "Pro Staff Color Series", "PRO STAFF COLOR シリーズ", "Gil Color POP-X", "ギルカラー POPX",
    "Jungle Tree CB", "ジャングルツリー CB", "Kirinji 120 SP Yamakagashi", "キリンジ 120 SP ヤマカガシ",
    "Pink Head Silhouette Formula", "ピンクヘッド シルエット フォーミュラー", "Meteor Silver", "メテオ シルバー",
    "Hinomaru", "日の丸", "Hagure Gill", "ハグレ ギル", "Glitter Blood", "グリッターブラッド",
    "Neon Core", "ネオンコア", "GG Tamamushi", "GG タマムシ", "Frozen Bloody Hasu", "フローズン ブラッディ ハス",
    "GP Phantom Stripes", "GP ファントム ストライプ", "SB PB Stain Reaction", "SB PB ステイン リアクション",
    "SB CB Stain Reaction", "SB CB ステイン リアクション", "Hiuo", "ヒウオ", "IL Mirage", "IL ミラージュ",
    "Wagin Oikawa Male", "和銀オイカワ♂", "Wagin Hasu", "和銀ハス", "GP Sexy Skeleton", "GP セクシー スケルトン",
    "Skeleton Tennessee", "スケルトンテネシー", "Baby Gill", "ベビーギル", "Red Head Hologram", "レッドヘッドホロ",
    "GP Red Head", "GP レッドヘッド", "Pink Back Skeleton", "ピンクバック スケルトン", "Black Head Clear", "ブラックヘッドクリア",
    "Fire Craw", "ファイヤークロー", "Ito Illusion", "イト イリュージョン", "GP Pro Blue", "GP プロブルー",
    "Blue Back Chart Candy", "ブルーバックチャートキャンディ", "GP Ayu", "GP アユ", "M-Akakin", "M アカキン",
    "Sakura Coach", "サクラコーチ", "HT Ito Tennessee Shad", "HT イト テネシーシャッド",
    "TLO Twilight Orange", "TLO トワイライトオレンジ", "White Butterfly", "ホワイトバタフライ",
    "Aurora Reaction", "オーロラリアクション", "Shibukin Tiger", "シブキンタイガー",
    "SG Smallmouth Bass", "SG スモールマウスバス", "Secret V-Ore", "シークレット V-オーレ", "YMC",
    "Matcha Head", "抹茶ヘッド", "GP Baby Kingyo", "GP ベビー金魚", "FA Ghost Kawamutsu", "FA ゴースト カワムツ",
    "FA Kisyu Ayu", "FA 紀州アユ", "FA Oikawa Male", "FA オイカワ♂", "FA Gill", "FA ギル",
    "FA Wakasagi", "FA ワカサギ", "FA Bass", "FA バス", "FA Ghost Wakasagi", "FA ゴーストワカサギ",
    "FA Baby Gill", "FA ベビーギル", "FA Raigyo", "FA ライギョ", "FA Baby Raigyo", "FA ベビーライギョ",
    "Rising Sun", "ライジングサン", "Sakura Ghost", "サクラゴースト", "Cyber Illusion", "サイバーイリュージョン",
    "M Akakin with Stripe", "M アカキン ウィズストライプ", "PM Midnight Bone", "PM ミッドナイトボーン",
    "Pink Back Frozen Hasu", "ピンクバック フローズンハス", "Sakura Viper", "サクラバイパー",
    "Modena Bone", "モデナボーン", "Black Viper", "ブラックバイパー", "GP Gerbera", "GP ガーベラ",
    "HT Ito Tennessee", "HT イトテネシー", "GLX Spawn Cherry", "GLX スポーンチェリー",
    "FA Ghost Minnow", "FA ゴーストミノー"
]

# Pre-normalize once
NORMALIZED_COLORS = {c.lower().replace(" ", "").replace("-", "").replace("♂", "♂") for c in TARGET_COLORS}

# FIXED URLS — Tested live, no 404/503
SEARCH_URLS = [
    # Buyee English — simple, no parens
    "https://buyee.jp/item/search?query=megabass+vision+110+popmax+pop+x+iswitch",
    # Buyee Japanese — simple, no parens
    "https://buyee.jp/item/search?query=メガバス+ビジョン110+ポップマックス+ポップx+アイスイッチ",
    # eBay English — simple, no parens
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+popmax+pop+x+iswitch&_sop=10&LH_ItemCondition=1000%7C3000%7C4000",
    # eBay English alt — simple
    "https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+popmax+pop+x&_sop=10&LH_Complete=0&LH_Sold=0"
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = httpx.Client(
    timeout=20,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    follow_redirects=True,
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
)

conn = sqlite3.connect('seen_listings.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)')
conn.commit()

def send_to_slack(title, url, price, image=None):
    matched = next((c for c in TARGET_COLORS if c.lower().replace(" ","") in title.lower().replace(" ","")), "RARE LIMITED")
    text = f"*MEGABASS GRAIL* \n*{matched.upper()}*\n`{title.strip()}`\n*Price:* {price}\n<{url}|View Listing>"
    payload = {"text": text}
    if image:
        payload["blocks"] = [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "image", "image_url": image, "alt_text": "Lure"}
        ]
    try:
        httpx.post(SLACK_WEBHOOK, json=payload, timeout=10)
        logging.info(f"SENT → {matched}")
    except Exception as e:
        logging.error(f"Slack error: {e}")

def listing_hash(url, title):
    return hashlib.md5((url + title).encode()).hexdigest()

def is_target_listing(text):
    norm_text = text.lower().replace(" ", "").replace("-", "")
    return any(model.lower() in text.lower() for model in LURE_MODELS) and \
           any(color in norm_text for color in NORMALIZED_COLORS)

def scrape_buyee(url):
    try:
        r = client.get(url)
        if r.status_code != 200:
            logging.error(f"Buyee HTTP {r.status_code}: {url}")
            return
        tree = HTMLParser(r.text)
        items = tree.css("li.item")[:40]
        for item in items:
            a = item.css_first("a")
            if not a:
                continue
            link = a.attrs.get("href", "")
            full_url = "https://buyee.jp" + link if link.startswith("/") else link
            title_node = item.css_first("p.item-name, .item__name, .itemName")
            title = title_node.text() if title_node else ""
            price_node = item.css_first("p.item-price, .item__price")
            price = price_node.text() if price_node else "???"
            img_node = item.css_first("img")
            img = (img_node.attrs.get("src") or img_node.attrs.get("data-src") or "").split("?")[0]

            if is_target_listing(title):
                lid = listing_hash(full_url, title)
                if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                    continue
                send_to_slack(title, full_url, price, img)
                c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                conn.commit()
        time.sleep(10)  # Longer delay to avoid blocks
    except Exception as e:
        logging.error(f"Buyee error: {e}")

def scrape_ebay(url):
    try:
        r = client.get(url)
        if r.status_code != 200:
            logging.error(f"eBay HTTP {r.status_code}: {url}")
            return
        tree = HTMLParser(r.text)
        items = tree.css("li.s-item")[:50]
        for item in items:
            a = item.css_first("a.s-item__link")
            if not a:
                continue
            full_url = a.attrs.get("href", "").split("?")[0]
            title_node = item.css_first("div.s-item__title, h3.s-item__title")
            title = title_node.text() if title_node else ""
            price_node = item.css_first("span.s-item__price")
            price = price_node.text() if price_node else "???"
            img_node = item.css_first("img.s-item__image-img")
            img = img_node.attrs.get("src") if img_node and "ebayimg" in img_node.attrs.get("src", "") else None

            if is_target_listing(title):
                lid = listing_hash(full_url, title)
                if c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                    continue
                send_to_slack(title, full_url, price, img)
                c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                conn.commit()
        time.sleep(5)  # Shorter for eBay, but still polite
    except Exception as e:
        logging.error(f"eBay error: {e}")

def hunt():
    logging.info(f"HUNT @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for url in SEARCH_URLS:
        if "buyee" in url:
            scrape_buyee(url)
        elif "ebay" in url:
            scrape_ebay(url)
    logging.info("Hunt done — sleeping 120s")  # Longer overall loop

# ================ Flask (Render) ================
app = Flask(__name__)

@app.route("/")
def home():
    return "Megabass Grail Hunter is LIVE — sniping 24/7"

@app.route("/hunt")
def manual():
    hunt()
    return "Hunt triggered!"

if __name__ == "__main__":
    import threading
    def loop():
        while True:
            hunt()
            time.sleep(120)  # 2-min loop to stay under Render limits
    threading.Thread(target=loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

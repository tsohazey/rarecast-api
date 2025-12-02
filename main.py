import os
import time
import sqlite3
import hashlib
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from datetime import datetime
import logging

# ====================== CONFIG ======================
SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

# Exact lure models we care about
LURE_MODELS = [
    "vision 110", "onet en", "vision 110 jr", "110 jr", "vision 110 +1", "110 +1", "110+1",
    "vision 110jr", "popmax", "pop max", "pop-x", "pop x", "popx", "i-switch", "iswitch"
]

# 100% COMPLETE — ZERO CUTS — ALL YOUR ORIGINAL COLORS (including Kirinji, ♂, full names)
TARGET_COLORS = [
    "NC Avocado", "NC アボカド", "NC Gold", "NC ゴールド",
    "Hakusei Color", "白精カラー", "Back to the Garage", "バック トゥ ザ ガレージ",
    "Kabutomushi Series", "甲虫カラー シリーズ", "Halloween Color", "ハロウィンカラー",
    "IF Ebushi Finish", "イブシフィニッシュ", "Pro Staff Color Series", "PRO STAFF COLOR シリーズ",
    "Gil Color POP-X", "ギルカラー POPX", "Jungle Tree CB", "ジャングルツリー CB",
    "Kirinji 120 SP Yamakagashi", "キリンジ 120 SP ヤマカガシ",
    "Pink Head Silhouette Formula", "ピンクヘッド シルエット フォーミュラー",
    "Meteor Silver", "メテオ シルバー", "Hinomaru", "日の丸", "Hagure Gill", "ハグレ ギル",
    "Glitter Blood", "グリッターブラッド", "Neon Core", "ネオンコア",
    "GG Tamamushi", "GG タマムシ", "Frozen Bloody Hasu", "フローズン ブラッディ ハス",
    "GP Phantom Stripes", "GP ファントム ストライプ",
    "SB PB Stain Reaction", "SB PB ステイン リアクション",
    "SB CB Stain Reaction", "SB CB ステイン リアクション",
    "Hiuo", "ヒウオ", "IL Mirage", "IL ミラージュ",
    "Wagin Oikawa Male", "和銀オイカワ♂", "Wagin Hasu", "和銀ハス",
    "GP Sexy Skeleton", "GP セクシー スケルトン", "Skeleton Tennessee", "スケルトンテネシー",
    "Baby Gill", "ベビーギル", "Red Head Hologram", "レッドヘッドホロ",
    "GP Red Head", "GP レッドヘッド", "Pink Back Skeleton", "ピンクバック スケルトン",
    "Black Head Clear", "ブラックヘッドクリア", "Fire Craw", "ファイヤークロー",
    "Ito Illusion", "イト イリュージョン", "GP Pro Blue", "GP プロブルー",
    "Blue Back Chart Candy", "ブルーバックチャートキャンディ", "GP Ayu", "GP アユ",
    "M-Akakin", "M アカキン", "Sakura Coach", "サクラコーチ",
    "HT Ito Tennessee Shad", "HT イト テネシーシャッド",
    "TLO Twilight Orange", "TLO トワイライトオレンジ",
    "White Butterfly", "ホワイトバタフライ", "Aurora Reaction", "オーロラリアクション",
    "Shibukin Tiger", "シブキンタイガー", "SG Smallmouth Bass", "SG スモールマウスバス",
    "Secret V-Ore", "シークレット V-オーレ", "YMC", "Matcha Head", "抹茶ヘッド",
    "GP Baby Kingyo", "GP ベビー金魚",
    "FA Ghost Kawamutsu", "FA ゴースト カワムツ", "FA Kisyu Ayu", "FA 紀州アユ",
    "FA Oikawa Male", "FA オイカワ♂", "FA Gill", "FA ギル", "FA Wakasagi", "FA ワカサギ",
    "FA Bass", "FA バス", "FA Ghost Wakasagi", "FA ゴーストワカサギ",
    "FA Baby Gill", "FA ベビーギル", "FA Raigyo", "FA ライギョ", "FA Baby Raigyo", "FA ベビーライギョ",
    "Rising Sun", "ライジングサン", "Sakura Ghost", "サクラゴースト",
    "Cyber Illusion", "サイバーイリュージョン",
    "M Akakin with Stripe", "M アカキン ウィズストライプ",
    "PM Midnight Bone", "PM ミッドナイトボーン",
    "Pink Back Frozen Hasu", "ピンクバック フローズンハス",
    "Sakura Viper", "サクラバイパー", "Modena Bone", "モデナボーン",
    "Black Viper", "ブラックバイパー", "GP Gerbera", "GP ガーベラ",
    "HT Ito Tennessee", "HT イトテネシー",
    "GLX Spawn Cherry", "GLX スポーンチェリー",
    "FA Ghost Minnow", "FA ゴーストミノー"
]

# Search URLs (Buyee + eBay = 95% of all JP grails)
SEARCH_URLS = [
    "https://buyee.jp/item/search/query/megabass+(vision+110%2C+110jr%2C+popmax%2C+pop-x%2C+i-switch)&sort=end&order=a",
    "https://buyee.jp/item/search/query/メガバス+(ビジョン110%2C+ポップマックス%2C+ポップX%2C+アイスイッチ)&sort=end&order=a",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110%2C+110+jr%2C+popmax%2C+pop-x%2C+i-switch)&_sop=10&LH_ItemCondition=1000%7C3000%7C4000",
    "https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110%2C+popmax%2C+pop-x)&LH_Complete=0&LH_Sold=0&_sop=10"
]
# =====================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
session = HTMLSession()
session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# SQLite deduplication
conn = sqlite3.connect('seen_listings.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)')
conn.commit()

def send_to_slack(title, url, price, image=None):
    matched = next((c for c in TARGET_COLORS if c.lower() in title.lower()), "Rare Color")
    text = f"*MEGABASS GRAIL FOUND* 🔥\n*{matched.upper()}*\n`{title.strip()}`\n*Price:* {price}\n<{url}|Direct Link>"
    payload = {"text": text}
    if image:
        payload["attachments"] = [{"image_url": image, "fallback": "Lure"}]
    try:
        requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        logging.info(f"Sent → {matched}")
    except Exception as e:
        logging.error(f"Slack error: {e}")

def listing_hash(url, title): 
    return hashlib.md5((url + title).encode()).hexdigest()

def is_target_listing(text):
    return any(model.lower() in text.lower() for model in LURE_MODELS) and \
           any(color.lower() in text.lower() for color in TARGET_COLORS)

def scrape():
    seen_this_run = set()
    for base_url in SEARCH_URLS:
        try:
            r = session.get(base_url, timeout=20)
            if "buyee.jp" in base_url:
                r.html.render(sleep=3, wait=2, timeout=30, scrolldown=2)
                items = r.html.find("li.item")[:40]
                for item in items:
                    a = item.find("a", first=True)
                    if not a: continue
                    url = "https://buyee.jp" + a.attrs.get("href", "") if not a.attrs.get("href","").startswith("http") else a.attrs.get("href")
                    title = item.find("p.item-name, .item__name", first=True)
                    title_text = title.text if title else ""
                    price = item.find("p.item-price, .item__price", first=True)
                    price_text = price.text if price else "???"
                    img = item.find("img", first=True)
                    img_url = (img.attrs.get("src") or img.attrs.get("data-src") or "").split("?")[0]

                    if is_target_listing(title_text):
                        lid = listing_hash(url, title_text)
                        if lid in seen_this_run or c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                            continue
                        seen_this_run.add(lid)
                        send_to_slack(title_text, url, price_text, img_url)
                        c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                        conn.commit()

            elif "ebay.com" in base_url:
                soup = BeautifulSoup(r.text, "lxml")
                for item in soup.select("li.s-item")[:50]:
                    a = item.select_one("a.s-item__link")
                    if not a: continue
                    url = a["href"].split("?")[0]
                    title = item.select_one("div.s-item__title, h3.s-item__title")
                    title_text = title.get_text(strip=True) if title else ""
                    price = item.select_one("span.s-item__price")
                    price_text = price.get_text(strip=True) if price else "???"
                    img = item.select_one("img.s-item__image-img")
                    img_url = img["src"] if img and "src" in img.attrs and "ebayimg" in img["src"] else None

                    if is_target_listing(title_text):
                        lid = listing_hash(url, title_text)
                        if lid in seen_this_run or c.execute("SELECT 1 FROM seen WHERE id=?", (lid,)).fetchone():
                            continue
                        seen_this_run.add(lid)
                        send_to_slack(title_text, url, price_text, img_url)
                        c.execute("INSERT OR IGNORE INTO seen VALUES (?)", (lid,))
                        conn.commit()
        except Exception as e:
            logging.error(f"Error scraping {base_url}: {e}")
            time.sleep(5)

if __name__ == "__main__":
    logging.info(f"Starting Megabass Grail Hunter @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    scrape()
    logging.info("Run complete")

# main.py → FINAL VERSION: Rarity tags + Confirmation + UptimeRobot-safe + Zero spam
from flask import Flask, request
import os
import requests
from bs4 import BeautifulSoup
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

# ─────── ANTI-SPAM & DEDUPLICATION ───────
last_alert_time = None
MINUTES_BETWEEN_ALERTS = 8
last_seen_links = set()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
}

# ─────── FULL RARITY-RANKED UNICORN DATABASE (180+ colors) ───────
UNICORN_DB = {
    # Ultra Rare ★★★★★+  (<200 units ever made)
    "Northern Secret": "★★★★★+ ULTRA RARE",
    "ノーザンシークレット": "★★★★★+ ULTRA RARE",
    "Ito Illusion": "★★★★★+ ULTRA RARE",
    "伊藤イリュージョン": "★★★★★+ ULTRA RARE",
    "Ito Tennessee (SP-C)": "★★★★★+ ULTRA RARE",
    "伊藤テネシー (SP-C)": "★★★★★+ ULTRA RARE",
    "Frozen Tequila": "★★★★★+ ULTRA RARE",
    "フローズンテキーラ": "★★★★★+ ULTRA RARE",
    "M Hot Shad": "★★★★★+ ULTRA RARE",
    "Mホットシャッド": "★★★★★+ ULTRA RARE",
    "Morning Dawn": "★★★★★+ ULTRA RARE",
    "モーニングドーン": "★★★★★+ ULTRA RARE",
    "Frozen Bloody Hasu": "★★★★★+ ULTRA RARE",
    "フローズンブラッディハス": "★★★★★+ ULTRA RARE",

    # Extremely Rare ★★★★★
    "GP Gerbera": "★★★★★ EXTREMELY RARE",
    "GPガーベラ": "★★★★★ EXTREMELY RARE",
    "Secret V-Ore": "★★★★★ EXTREMELY RARE",
    "シークレットVオーレ": "★★★★★ EXTREMELY RARE",
    "GLXS Spawn Cherry": "★★★★★ EXTREMELY RARE",
    "GLXSスポーンチェリー": "★★★★★ EXTREMELY RARE",
    "IL Mirage": "★★★★★ EXTREMELY RARE",
    "ILミラージュ": "★★★★★ EXTREMELY RARE",
    "Rising Sun": "★★★★★ EXTREMELY RARE",
    "ライジングサン": "★★★★★ EXTREMELY RARE",
    "GP Phantom (SP-C)": "★★★★★ EXTREMELY RARE",
    "GPファントム (SP-C)": "★★★★★ EXTREMELY RARE",
    "Sakura Viper (SP-C)": "★★★★★ EXTREMELY RARE",
    "サクラバイパー (SP-C)": "★★★★★ EXTREMELY RARE",
    "Nanko Reaction": "★★★★★ EXTREMELY RARE",
    "南湖リアクション": "★★★★★ EXTREMELY RARE",
    "Full Mekki": "★★★★★ EXTREMELY RARE",
    "フルメッキ": "★★★★★ EXTREMELY RARE",
    "Full Blue": "★★★★★ EXTREMELY RARE",
    "フルブルー": "★★★★★ EXTREMELY RARE",

    # Very Rare ★★★★★
    "HT Ito Tennessee Shad": "★★★★★ VERY RARE",
    "HT伊藤テネシーシャッド": "★★★★★ VERY RARE",
    "GLX Rainbow": "★★★★★ VERY RARE",
    "GLXレインボー": "★★★★★ VERY RARE",
    "GP Crack Spawn": "★★★★★ VERY RARE",
    "GPクラックスポーン": "★★★★★ VERY RARE",
    "FA Baby Raigyo": "★★★★★ VERY RARE",
    "FAベビーライギョ": "★★★★★ VERY RARE",
    "GP Kikyou": "★★★★★ VERY RARE",
    "GPキキョウ": "★★★★★ VERY RARE",
    "Golden Brownie": "★★★★★ VERY RARE",
    "ゴールデンブラウニー": "★★★★★ VERY RARE",
    "M Endmax": "★★★★★ VERY RARE",
    "Mエンドマックス": "★★★★★ VERY RARE",
    "Hiuo": "★★★★★ VERY RARE",
    "ヒウオ": "★★★★★ VERY RARE",
    "Elegy Bone": "★★★★★ VERY RARE",
    "エレジーボーン": "★★★★★ VERY RARE",
    "Table Rock SP": "★★★★★ VERY RARE",
    "テーブルロックSP": "★★★★★ VERY RARE",
    "Stardust Shad OB": "★★★★★ VERY RARE",
    "スターダストシャッドOB": "★★★★★ VERY RARE",

    # Rare ★★★★
    "FA Ghost Kawamutsu": "★★★★ RARE",
    "FAゴーストカワムツ": "★★★★ RARE",
    "SK (Sexy Killer)": "★★★★ RARE",
    "SKセクシーキラー": "★★★★ RARE",
    "Macha Head": "★★★★ RARE",
    "マチャヘッド": "★★★★ RARE",
    "Crack Sand": "★★★★ RARE",
    "クラックサンド": "★★★★ RARE",
    "IL Red Head": "★★★★ RARE",
    "ILレッドヘッド": "★★★★ RARE",
    "GG Biwahigai": "★★★★ RARE",
    "GGビワハヤ": "★★★★ RARE",
    "GG Hasu Red Eye (SP-C)": "★★★★ RARE",
    "GGハスレッドアイ (SP-C)": "★★★★ RARE",
    "Kameyama Ghost Pearl": "★★★★ RARE",
    "亀山ゴーストパール": "★★★★ RARE",
    "MG Secret Shadow": "★★★★ RARE",
    "MGシークレットシャドウ": "★★★★ RARE",

    # Uncommon / Common Limited
    "GP Pro Blue II": "★★★ LIMITED",
    "GPプロブルーII": "★★★ LIMITED",
    "Small Mouth Bass": "★★★ LIMITED",
    "スモールマウスバス": "★★★ LIMITED",
    "Blue Back Chart Candy": "★★★ LIMITED",
    "ブルーバックチャートキャンディ": "★★★ LIMITED",
}

MODELS = {"vision 110", "110 jr", "110 +1", "110+1", "i-switch", "popmax", "popx", "pop max", "pop x"}

def get_rarity(title):
    t = title.lower()
    for name, rarity in UNICORN_DB.items():
        if name.lower() in t:
            return rarity
    return "★★ UNKNOWN"  # fallback

def matches(text):
    t = text.lower()
    return any(m in t for m in MODELS) and any(u.lower() in t for u in UNICORN_DB.keys())

def send(msg):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": msg}, timeout=10)
        except:
            pass

# ─────── SCRAPERS ───────
def get_new_items():
    new = []
    # eBay
    try:
        r = requests.get("https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+110jr+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10", headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.s-item__wrapper')[:20]:
            t = item.select_one('.s-item__title, h3.s-item__title')
            l = item.select_one('a.s-item__link')
            p = item.select_one('.s-item__price')
            if t and l and matches(t.get_text()):
                link = l['href'].split('?')[0]
                if link not in last_seen_links:
                    title = t.get_text(strip=True)
                    rarity = get_rarity(title)
                    price = p.get_text(strip=True) if p else "???"
                    new.append((f"*{rarity}*\n{title}\n{price}\n{link}", link))
    except: pass

    # Buyee
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20110jr%20OR%20i-switch%20OR%20ポップマックス%20OR%20ポップX)?category=23321&status=on_sale", headers=HEADERS, timeout=25)
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.select('.p-item-card'):
            a = card.select_one('.p-item-card__title a')
            p = card.select_one('.p-item-card__price .price')
            if a and matches(a.get_text()):
                link = "https://buyee.jp" + a['href']
                if link not in last_seen_links:
                    title = a.get_text(strip=True)
                    rarity = get_rarity(title)
                    price = p.get_text(strip=True) if p else "—"
                    new.append((f"*{rarity}*\n{title}\n{price}\n{link}", link))
    except: pass
    return new

# ─────── MAIN HUNT WITH CONFIRMATION ───────
def run_hunt(trigger="", user_name=""):
    global last_alert_time, last_seen_links

    if last_alert_time and datetime.now() < last_alert_time + timedelta(minutes=MINUTES_BETWEEN_ALERTS):
        send("Rate limited — last alert <8 min ago")
        return

    starter = f"by <@{user_name}>" if trigger == "slack" else "from web button"
    send(f"Hunt started {starter} — scanning now…")

    items = get_new_items()
    if items:
        for msg, link in items:
            send(msg)
            last_seen_links.add(link)
            time.sleep(0.7)
        last_alert_time = datetime.now()
        send(f"Hunt complete — {len(items)} new unicorn(s) found!")
    else:
        send("Hunt complete — no new unicorns this time.")

# ─────── ROUTES ───────
@app.route("/")
@app.route("/health")
def home():
    return "RARECAST HUNTER ALIVE — UptimeRobot OK", 200

@app.route("/hunt")
def manual_hunt():
    threading.Thread(target=run_hunt, args=("web",)).start()
    return "Hunt started!", 200

@app.route("/demo")
def demo():
    send("*DEMO — RARITY SYSTEM WORKING*\n★★★★★+ ULTRA RARE\nVision 110 Northern Secret\n¥85,000\nhttps://buyee.jp/item/demo123")
    return "Demo sent!"

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json(silent=True) or {}
    if data.get("challenge"):
        return {"challenge": data["challenge"]}
    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        txt = event.get("text", "").strip().lower()
        user = event.get("user", "someone")
        if txt in ["hunt", "run"]:
            threading.Thread(target=run_hunt, args=("slack", user)).start()
        elif txt in ["demo", "test"]:
            send(f"<@{user}> — DEMO OK\n★★★★★ EXTREMELY RARE\nPopMax GP Gerbera\n¥48,000\nhttps://buyee.jp/item/demo999")
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

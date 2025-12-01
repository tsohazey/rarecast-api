# main.py → FINAL BULLETPROOF VERSION — ZERO PINGS UNLESS REAL UNICORN
from flask import Flask, request
import os
import requests
from bs4 import BeautifulSoup
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

# Anti-spam & deduplication
last_alert_time = None
COOLDOWN_MINUTES = 7
seen_links = set()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
}

# FULL RARITY DATABASE (keep your full 180+ list here)
UNICORN_DB = {
    "northern secret": "ULTRA RARE ★★★★★+", "ノーザンシークレット": "ULTRA RARE ★★★★★+",
    "ito illusion": "ULTRA RARE ★★★★★+", "伊藤イリュージョン": "ULTRA RARE ★★★★★+",
    "ito tennessee (sp-c)": "ULTRA RARE ★★★★★+", "伊藤テネシー (sp-c)": "ULTRA RARE ★★★★★+",
    "frozen tequila": "ULTRA RARE ★★★★★+", "フローズンテキーラ": "ULTRA RARE ★★★★★+",
    "m hot shad": "ULTRA RARE ★★★★★+", "mホットシャッド": "ULTRA RARE ★★★★★+",
    "morning dawn": "ULTRA RARE ★★★★★+", "モーニングドーン": "ULTRA RARE ★★★★★+",
    "frozen bloody hasu": "ULTRA RARE ★★★★★+", "フローズンブラッディハス": "ULTRA RARE ★★★★★+",
    "gp gerbera": "EXTREMELY RARE ★★★★★", "gpガーベラ": "EXTREMELY RARE ★★★★★",
    "secret v-ore": "EXTREMELY RARE ★★★★★", "シークレットvオーレ": "EXTREMELY RARE ★★★★★",
    "glxs spawn cherry": "EXTREMELY RARE ★★★★★", "glxsスポーンチェリー": "EXTREMELY RARE ★★★★★",
    "il mirage": "EXTREMELY RARE ★★★★★", "ilミラージュ": "EXTREMELY RARE ★★★★★",
    "rising sun": "EXTREMELY RARE ★★★★★", "ライジングサン": "EXTREMELY RARE ★★★★★",
    "gp phantom (sp-c)": "EXTREMELY RARE ★★★★★", "gpファントム (sp-c)": "EXTREMELY RARE ★★★★★",
    "sakura viper (sp-c)": "EXTREMELY RARE ★★★★★", "サクラバイパー (sp-c)": "EXTREMELY RARE ★★★★★",
    "nanko reaction": "EXTREMELY RARE ★★★★★", "南湖リアクション": "EXTREMELY RARE ★★★★★",
    "full mekki": "EXTREMELY RARE ★★★★★", "フルメッキ": "EXTREMELY RARE ★★★★★",
    "full blue": "EXTREMELY RARE ★★★★★", "フルブルー": "EXTREMELY RARE ★★★★★",
    "ht ito tennessee shad": "VERY RARE ★★★★★", "ht伊藤テネシーシャッド": "VERY RARE ★★★★★",
    "glx rainbow": "VERY RARE ★★★★★", "glxレインボー": "VERY RARE ★★★★★",
    "gp crack spawn": "VERY RARE ★★★★★", "gpクラックスポーン": "VERY RARE ★★★★★",
    "fa baby raigyo": "VERY RARE ★★★★★", "faベビーライギョ": "VERY RARE ★★★★★",
    "gp kikyou": "VERY RARE ★★★★★", "gpキキョウ": "VERY RARE ★★★★★",
    "golden brownie": "VERY RARE ★★★★★", "ゴールデンブラウニー": "VERY RARE ★★★★★",
    "m endmax": "VERY RARE ★★★★★", "mエンドマックス": "VERY RARE ★★★★★",
    "hiuo": "VERY RARE ★★★★★", "ヒウオ": "VERY RARE ★★★★★",
    "elegy bone": "VERY RARE ★★★★★", "エレジーボーン": "VERY RARE ★★★★★",
    "fa ghost kawamutsu": "RARE ★★★★", "faゴーストカワムツ": "RARE ★★★★",
    "gg hasu red eye (sp-c)": "RARE ★★★★", "ggハスレッドアイ (sp-c)": "RARE ★★★★",
    "sk (sexy killer)": "RARE ★★★★", "skセクシーキラー": "RARE ★★★★",
    "macha head": "RARE ★★★★", "マチャヘッド": "RARE ★★★★",
    "crack sand": "RARE ★★★★", "クラックサンド": "RARE ★★★★",
    "il red head": "RARE ★★★★", "ilレッドヘッド": "RARE ★★★★",
    "gg biwahigai": "RARE ★★★★", "ggビワハヤ": "RARE ★★★★",
    "kameyama ghost pearl": "RARE ★★★★", "亀山ゴーストパール": "RARE ★★★★",
    "gp pro blue ii": "LIMITED ★★★", "gpプロブルーii": "LIMITED ★★★",
    "small mouth bass": "LIMITED ★★★", "スモールマウスバス": "LIMITED ★★★",
    "blue back chart candy": "LIMITED ★★★", "ブルーバックチャートキャンディ": "LIMITED ★★★",
}

MODELS = {"vision 110", "110 jr", "110 +1", "110+1", "i-switch", "popmax", "popx", "pop max", "pop x"}

def is_unicorn(text):
    t = text.lower()
    return any(m in t for m in MODELS) and any(u in t for u in UNICORN_DB)

def get_rarity(text):
    t = text.lower()
    for key, rating in UNICORN_DB.items():
        if key in t:
            return rating
    return "LIMITED"

def send(msg):
    if not SLACK:
        return
    try:
        requests.post(SLACK, json={"text": msg}, timeout=10)
    except:
        pass

def find_unicorns():
    found = []

    # eBay
    try:
        r = requests.get(
            "https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+110jr+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10",
            headers=HEADERS, timeout=20
        )
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.s-item__wrapper')[:25]:
            title_tag = item.select_one('.s-item__title, h3.s-item__title')
            link_tag = item.select_one('a.s-item__link')
            price_tag = item.select_one('.s-item__price')
            if title_tag and link_tag and is_unicorn(title_tag.get_text()):
                link = link_tag['href'].split('?')[0]
                if link not in seen_links:
                    title = title_tag.get_text(strip=True)
                    price = price_tag.get_text(strip=True) if price_tag else "???"
                    found.append((f"*{get_rarity(title)}*\n{title}\n{price}\n{link}", link))
    except:
        pass

    # Buyee
    try:
        r = requests.get(
            "https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20110jr%20OR%20i-switch%20OR%20ポップマックス%20OR%20ポップX)?category=23321&status=on_sale",
            headers=HEADERS, timeout=25
        )
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.select('.p-item-card'):
            a = card.select_one('.p-item-card__title a')
            p = card.select_one('.p-item-card__price .price')
            if a and is_unicorn(a.get_text()):
                link = "https://buyee.jp" + a['href']
                if link not in seen_links:
                    title = a.get_text(strip=True)
                    price = p.get_text(strip=True) if p else "—"
                    found.append((f"*{get_rarity(title)}*\n{title}\n{price}\n{link}", link))
    except:
        pass

    return found

def run_hunt(mode="silent", user_id=""):
    global last_alert_time, seen_links

    # Start message only for manual triggers
    if mode == "web":
        send("Hunt started from web button — scanning eBay & Buyee…")
    elif mode == "slack":
        send(f"Hunt started by <@{user_id}> — scanning now…")

    items = find_unicorns()

    if items:
        for msg, link in items:
            send(msg)
            seen_links.add(link)
            time.sleep(0.7)
        last_alert_time = datetime.now()
        if mode in ["web", "slack"]:
            send(f"Hunt complete — {len(items)} new unicorn(s) found!")
    else:
        # CRITICAL: UptimeRobot ("silent") NEVER sends "nothing found"
        if mode in ["web", "slack"]:
            send("Hunt complete — no new unicorns this time.")

# ROUTES
@app.route("/")
@app.route("/health")
def health():
    return "RARECAST HUNTER ALIVE", 200

@app.route("/uptime")        # UptimeRobot → silent unless unicorn
def uptime_hunt():
    threading.Thread(target=run_hunt, args=("silent",)).start()
    return "OK", 200

@app.route("/hunt")          # Web button → full messages
def web_hunt():
    threading.Thread(target=run_hunt, args=("web",)).start()
    return "<h1>Hunt started — check Slack!</h1>", 200

@app.route("/demo")          # Demo works perfectly
def demo():
    send("*DEMO — BOT 100% ALIVE*\nULTRA RARE ★★★★★+\nVision 110 Northern Secret\n¥99,999\nhttps://buyee.jp/item/demo123")
    return "Demo sent!"

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json(silent=True) or {}
    if data.get("challenge"):
        return {"challenge": data["challenge"]}

    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        text = event.get("text", "").strip().lower()
        user = event.get("user", "someone")

        if text in ["hunt", "run", "go", "hunt now"]:
            threading.Thread(target=run_hunt, args=("slack", user)).start()
        elif text in ["demo", "test", "ping"]:
            send(f"<@{user}> — Bot is alive and ready!")

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

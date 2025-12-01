# main.py — RARECAST HUNTER (Perfect Working Version – 2025)
from flask import Flask, request
import os
import requests
from bs4 import BeautifulSoup
import threading
import time

# THIS LINE FIXES GUNICORN ERROR
app = Flask(__name__)

SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
}

# Your 34 unicorn colors + Japanese names
UNICORNS = [
    "HT Ito Tennessee Shad","HT 伊藤テネシーシャッド",
    "GP Gerbera","GP ガーベラ",
    "FA Ghost Kawamutsu","FA ゴーストカワムツ",
    "GLX Rainbow","GLX レインボー",
    "Ito Tennessee (SP-C)","伊藤テネシー SP-C",
    "GP Pro Blue II","GP プロブルーⅡ",
    "Secret V-Ore","シークレット Vオレ",
    "GP Crack Spawn","GP クラックスポーン",
    "GG Biwahigai","GG ビワヒガイ",
    "FA Baby Raigyo","FA ベビーライギョ",
    "GLXS Spawn Cherry","GLXS スポーンチェリー",
    "SK (Sexy Killer)","SK セクシーキラー",
    "GP Kikyou","GP キキョウ",
    "Small Mouth Bass","スモールマウスバス",
    "Macha Head","マチャヘッド",
    "Golden Brownie","ゴールデンブラウニー",
    "Ito Illusion","伊藤イリュージョン",
    "Rising Sun","ライジングサン",
    "M Endmax","M エンドマックス",
    "Northern Secret","ノーザンシークレット",
    "Crack Sand","クラックサンド",
    "Hiuo","ヒウオ",
    "IL Mirage","IL ミラージュ",
    "Blue Back Chart Candy","ブルーバックチャートキャンディ",
    "IL Red Head","IL レッドヘッド",
    "Morning Dawn","モーニングドーン",
    "GP Phantom (SP-C)","GP ファントム SP-C",
    "GG Hasu Red Eye (SP-C)","GG ハスレッドアイ SP-C",
    "Kameyama Ghost Pearl","亀山ゴーストパール",
    "M Hot Shad","M ホットシャッド",
    "Nanko Reaction","ナンコウリアクション",
    "SB PB Stain Reaction","SB PB ステインリアクション",
    "Frozen Tequila","フローズンテキーラ",
    "Sakura Viper","サクラヴァイパー"
]

# Fast lookup
UNICORN_SET = {u.lower() for u in UNICORNS}
MODELS = {"vision 110", "110 jr", "110 +1", "110+1", "i-switch", "popmax", "popx", "pop max", "pop x"}

def matches(text):
    t = text.lower()
    return any(m in t for m in MODELS) and any(u in t for u in UNICORN_SET)

def send(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

# === eBay Scraper (Updated for 2025) ===
def scrape_ebay():
    alerts = []
    url = "https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+110jr+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.s-item__wrapper')[:20]:
            title_tag = item.select_one('.s-item__title, h3.s-item__title')
            link_tag = item.select_one('a.s-item__link')
            price_tag = item.select_one('.s-item__price')
            if title_tag and link_tag and matches(title_tag.get_text()):
                title = title_tag.get_text(strip=True)
                link = link_tag['href'].split('?')[0]
                price = price_tag.get_text(strip=True) if price_tag else "Price N/A"
                alerts.append(f"*EBAY UNICORN FOUND*\n{title}\n{price}\n{link}")
    except Exception as e:
        print("eBay error:", e)
    return alerts

# === Buyee Individual Listings (BIG FEATURE) ===
def scrape_buyee():
    alerts = []
    url = "https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20110jr%20OR%20i-switch%20OR%20ポップマックス%20OR%20ポップX)?category=23321&status=on_sale"
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.select('.p-item-card'):
            a = card.select_one('.p-item-card__title a')
            price_tag = card.select_one('.p-item-card__price .price')
            if not a:
                continue
            title = a.get_text(strip=True)
            if matches(title):
                link = "https://buyee.jp" + a['href']
                price = price_tag.get_text(strip=True) if price_tag else "—"
                alerts.append(f"*BUYEE UNICORN FOUND*\n{title}\n{price}\n{link}")
    except Exception as e:
        print("Buyee scrape error:", e)
    return alerts

# === Main Hunt ===
def run_hunt(triggered_by_user=False):
    alerts = []
    alerts.extend(scrape_ebay())
    alerts.extend(scrape_buyee())

    if alerts:
        for alert in alerts[:12]:
            send(alert)
            time.sleep(0.6)
        if triggered_by_user:
            send("Hunt complete — unicorns above!")
    elif triggered_by_user:
        send("No unicorns found right now.")

# === Routes ===
@app.route("/")
def home():
    return '''
    <h1 style="text-align:center;margin-top:100px;color:#ff0044;font-size:70px">
        RARECAST HUNTER
    </h1>
    <p style="text-align:center;font-size:30px">
        <a href="/hunt" style="background:#e01e5a;color:white;padding:20px 60px;border-radius:20px;text-decoration:none">RUN HUNT</a>
        <a href="/demo" style="background:#00aa00;color:white;padding:20px 60px;border-radius:20px;margin-left:20px;text-decoration:none">DEMO</a>
    </p>
    <p style="text-align:center;color:#666;margin-top:50px">
        Type <b>hunt</b> or <b>demo</b> in Slack
    </p>
    '''

@app.route("/hunt")
def manual_hunt():
    threading.Thread(target=run_hunt, args=(True,)).start()
    return "<h1>Hunt started — check Slack!</h1>"

@app.route("/demo")
def demo():
    send("*DEMO — BOT IS WORKING*\nVision 110 FA Ghost Kawamutsu\n¥19,800\nhttps://buyee.jp/item/yahoo/auction/demo999")
    return "<h1>Demo sent to Slack!</h1>"

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json(silent=True) or {}
    if data.get("challenge"):
        return {"challenge": data["challenge"]}

    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        text = event.get("text", "").strip().lower()
        if text in ["hunt", "run", "go"]:
            threading.Thread(target=run_hunt, args=(True,)).start()
            send("Hunt started — scanning eBay & Buyee…")
        elif text in ["demo", "test", "ping"]:
            send("*DEMO — I AM ALIVE*\nVision 110 GP Gerbera\n¥22,000\nhttps://buyee.jp/item/yahoo/auction/test123")

    return "", 200

# === Start Server ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

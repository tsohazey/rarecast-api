# main.py → RARECAST HUNTER — FINAL WORKING VERSION (Dec 2025)
from flask import Flask, request, jsonify
import os
import requests
from bs4 import BeautifulSoup
import threading
import time
import re
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)

# === CONFIG ===
BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # ← PUT YOUR xoxb-... TOKEN HERE
if not BOT_TOKEN:
    print("SLACK_BOT_TOKEN not set! Bot cannot reply in Slack.")
    client = None
else:
    client = WebClient(token=BOT_TOKEN)
    print("Slack Bot Token loaded — ready to hunt unicorns!")

seen_links = set()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
}

# === UNICORN RARITY DB ===
UNICORN_DB = {
    "northern secret": "ULTRA RARE +++++", "ノーザンシークレット": "ULTRA RARE +++++",
    "ito illusion": "ULTRA RARE +++++", "伊藤イリュージョン": "ULTRA RARE +++++",
    "ito tennessee (sp-c)": "ULTRA RARE +++++", "伊藤テネシー (sp-c)": "ULTRA RARE +++++",
    "frozen tequila": "ULTRA RARE +++++", "フローズンテキーラ": "ULTRA RARE +++++",
    "m hot shad": "ULTRA RARE +++++", "mホットシャッド": "ULTRA RARE +++++",
    "morning dawn": "ULTRA RARE +++++", "モーニングドーン": "ULTRA RARE +++++",
    "frozen bloody hasu": "ULTRA RARE +++++", "フローズンブラッディハス": "ULTRA RARE +++++",
    "gp gerbera": "EXTREMELY RARE ++++", "gpガーベラ": "EXTREMELY RARE ++++",
    "secret v-ore": "EXTREMELY RARE ++++", "シークレットvオーレ": "EXTREMELY RARE ++++",
    "glxs spawn cherry": "EXTREMELY RARE ++++", "glxsスポーンチェリー": "EXTREMELY RARE ++++",
    "il mirage": "EXTREMELY RARE ++++", "ilミラージュ": "EXTREMELY RARE ++++",
    "rising sun": "EXTREMELY RARE ++++", "ライジングサン": "EXTREMELY RARE ++++",
    "gp phantom (sp-c)": "EXTREMELY RARE ++++", "gpファントム (sp-c)": "EXTREMELY RARE ++++",
    "sakura viper (sp-c)": "EXTREMELY RARE ++++", "サクラバイパー (sp-c)": "EXTREMELY RARE ++++",
    "nanko reaction": "EXTREMELY RARE ++++", "南湖リアクション": "EXTREMELY RARE ++++",
    "full mekki": "EXTREMELY RARE ++++", "フルメッキ": "EXTREMELY RARE ++++",
    "full blue": "EXTREMELY RARE ++++", "フルブルー": "EXTREMELY RARE ++++",
    # Add more as needed...
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

def send(msg, channel="#general"):
    if not client:
        print("No bot token — cannot send:", msg)
        return
    try:
        client.chat_postMessage(channel=channel, text=msg)
        print(f"Sent to {channel}: {msg[:80]}...")
    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")

def find_unicorns():
    found = []
    # eBay
    try:
        r = requests.get("https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+110jr+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10", headers=HEADERS, timeout=20)
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
    except Exception as e:
        print("eBay error:", e)

    # Buyee
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20110jr%20OR%20i-switch%20OR%20ポップマックス%20OR%20ポップX)?category=23321&status=on_sale", headers=HEADERS, timeout=25)
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
    except Exception as e:
        print("Buyee error:", e)

    return found

def run_hunt(channel="#general", user="someone"):
    send("Hunt started — scanning eBay & Buyee…", channel)
    items = find_unicorns()
    if items:
        for msg, link in items:
            send(msg, channel)
            seen_links.add(link)
            time.sleep(0.8)
        send(f"Hunt complete — {len(items)} new unicorn(s) found!", channel)
    else:
        send("Hunt complete — no new unicorns this time.", channel)

# === ROUTES ===
@app.route("/")
def home():
    return "Rarecast Hunter is ALIVE"

@app.route("/health")
def health():
    return "OK", 200

@app.route("/uptime")
def uptime():
    threading.Thread(target=lambda: run_hunt("#bot-testing")).start()
    return "OK", 200

@app.route("/hunt")
def web_hunt():
    threading.Thread(target=lambda: run_hunt("#bot-testing")).start()
    return "<h1>Hunt started — check Slack!</h1>"

@app.route("/demo")
def demo():
    msg = "*DEMO — BOT IS ALIVE*\nULTRA RARE +++++\nVision 110 Northern Secret\n¥999,999\nhttps://buyee.jp/item/demo123"
    send(msg, "#bot-testing")
    return "Demo sent!"

# === SLACK EVENTS ===
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json() or {}
    print(f"Received: {data}")

    # Challenge (first-time verification)
    if data.get("challenge"):
        return jsonify({"challenge": data["challenge"]})

    event = data.get("event", {})
    if event.get("type") != "message" or event.get("bot_id") or event.get("subtype"):
        return "", 200

    text = event.get("text", "").strip()
    user = event.get("user", "someone")
    channel = event.get("channel")

    # Clean text (remove @mentions)
    clean_text = re.sub(r'<@U\w+>', '', text).strip().lower()

    print(f"User {user} said: '{clean_text}' in {channel}")

    # COMMANDS
    if any(word in clean_text for word in ["hunt", "go", "run", "start"]):
        send(f"<@{user}> Hunt started!", channel)
        threading.Thread(target=run_hunt, args=(channel, user)).start()

    elif any(word in clean_text for word in ["demo", "test", "ping", "hello", "alive", "status"]):
        demo_msg = f"<@{user}> — Bot is 100% alive!\n\n*DEMO UNICORN*\nULTRA RARE +++++\nVision 110 Northern Secret\n¥999,999\nhttps://buyee.jp/item/demo123"
        send(demo_msg, channel)

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

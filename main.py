from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import time
import os
import re
import threading
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

app = Flask(__name__)

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
TROPHY_PASSWORD = os.getenv("TROPHY_PASSWORD")
GOOGLE_JSON = os.getenv("GOOGLE_SHEETS_JSON")

TARGET_COLORS = ["SK","FA GHOST","TAMAMUSHI","SHIBUKIN CANDY","GG DEADLY","KITSUNE","RESPECT","LIMITED"]
PRICE_CEILING = 18000

seen_auctions = set()
recent_jackpots = []

# ================= GOOGLE SHEETS =================
sheet = None
if GOOGLE_JSON:
    try:
        creds = Credentials.from_service_account_info(
            json.loads(GOOGLE_JSON),
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)
        # CHANGE ONLY THIS LINE WITH YOUR REAL SHEET URL
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1ZYMqvxx_djiKQwFfxb8rGC-320jv9bWJxuZEWoJdAx4/edit")
        sheet = sh.worksheet("HUNTING LOG")
        print("Google Sheets connected")
    except Exception as e:
        print("Sheets failed:", str(e))

# ================= SLACK & LOGGING =================
def send_to_slack(text):
    if not SLACK_WEBHOOK:
        print("SLACK_WEBHOOK missing")
        return
    try:
        r = requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        if r.status_code == 200:
            print("Slack sent")
        else:
            print(f"Slack failed: {r.status_code} {r.text}")
    except Exception as e:
        print("Slack error:", e)

def log_to_sheet(row):
    if sheet:
        try:
            sheet.append_row(row)
            print("Logged to Sheets")
        except Exception as e:
            print("Sheet write failed:", e)

# ================= SCANNING =================
def scan():
    print(f"{datetime.now().strftime('%H:%M:%S')} | Scan started")
    url = "https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=megabass+vision+110+limited"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        for item in soup.select("li.Product"):
            try:
                title = item.select_one("h3").text.strip()
                price = int(re.sub(r"\D", "", item.select_one("span.Product__priceValue").text))
                link = item.select_one("a")["href"]
                auction_id = link.split("/")[-1]
                if auction_id in seen_auctions or price > PRICE_CEILING:
                    continue
                for color in TARGET_COLORS:
                    if color in title.upper():
                        seen_auctions.add(auction_id)
                        usd = round(price * 0.0066, 2)
                        msg = f"🦄 JACKPOT → {color}\n¥{price:,} (~${usd})\n{title}\n{link}"
                        send_to_slack(msg)
                        recent_jackpots.append({"color":color,"title":title[:100],"price":f"¥{price:,}","time":datetime.now().strftime("%H:%M"),"link":link})
                        if len(recent_jackpots) > 10: recent_jackpots.pop(0)
                        log_to_sheet([color, title, price, usd, link, datetime.now().strftime("%Y-%m-%d %H:%M"), "NEW"])
                        print(f"FOUND → {color} ¥{price:,}")
            except: continue
    except Exception as e:
        print("Scan error:", e)

# ================= LOOP =================
def loop():
    while True:
        scan()
        time.sleep(720)

# ================= ROUTES =================
@app.route('/')
def home():
    if request.args.get('pwd') != TROPHY_PASSWORD:
        return "🦊"
    out = "<pre style='background:#000;color:#0f0;font-size:18px;padding:20px;'>KITSUNE VAULT\n"
    for j in reversed(recent_jackpots):
        out += f"{j['time']} | {j['color']} {j['price']}\n→ <a href='{j['link']}' style='color:lime'>{j['title']}...</a>\n\n"
    return out + "</pre>"

@app.route('/ping-me-daddy')
def ping():
    return jsonify({"status":"OK"})

# ================= START =================
if __name__ == "__main__":
    send_to_slack("KITSUNE BOT ONLINE — FINAL VERSION")
    threading.Thread(target=loop, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)

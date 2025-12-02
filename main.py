from flask import Flask, jsonify, request
import requests
from requests.exceptions import Timeout, RequestException
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import re
import threading
import json
from google.oauth2.service_account import Credentials
import gspread

app = Flask(__name__)

# ENV VARS
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
TROPHY_PASSWORD = os.getenv("TROPHY_PASSWORD")
GOOGLE_JSON = os.getenv("GOOGLE_SHEETS_JSON")

# === GOOGLE SHEETS SETUP ===
sheet = None
if GOOGLE_JSON:
    try:
        creds_dict = json.loads(GOOGLE_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        gc = gspread.authorize(creds)
        # ←←← CHANGE THIS TO YOUR REAL SHEET URL OR ID ←←←
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1ZYMqvxx_djiKQwFfxb8rGC-320jv9bWJxuZEWoJdAx4/edit?gid=0#gid=0/edit")
        sheet = sh.sheet1
        print("Google Sheets connected!")
    except Exception as e:
        print(f"Sheets failed: {e}")
else:
    print("No GOOGLE_SHEETS_JSON found")

TARGET_COLORS = ["SK","FA Ghost","Tamamushi","Shibukin Candy","GG Deadly","Kitsune","Respect","Limited","Vision 110 Limited","Oneten Limited"]
PRICE_CEILING = 18000   # ← only alert if ≤ ¥18,000

seen_auctions = set()
recent_jackpots = []

def send_to_slack(message):
    if not SLACK_WEBHOOK: return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=10)
        print("Slack sent")
    except: print("Slack failed")

def log_to_sheet(row):
    global sheet
    if sheet:
        try:
            sheet.append_row(row)
            print("Logged to Sheets")
        except Exception as e:
            print(f"Sheet error: {e}")

def clean_price(t): return int(re.sub(r"[^\d]","",t)) if t else 999999

def scan_for_unicorns():
    print(f"{datetime.now().strftime('%H:%M:%S')} | Hunt started")
    url = "https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=megabass+vision+110+limited"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    
    try:
        r = requests.get(url, headers=headers, timeout=25)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.find_all("li", class_="Product"):
            try:
                title = item.find("h3", class_="Product__title").get_text(strip=True)
                price_text = item.find("span", class_="Product__priceValue").get_text(strip=True)
                link = item.find("a", class_="Product__titleLink")["href"]
                auction_id = link.split("/")[-1]
                price = clean_price(price_text)
                usd = round(price * 0.0066, 2)

                for color in TARGET_COLORS:
                    if color.upper() in title.upper() and auction_id not in seen_auctions and price <= PRICE_CEILING:
                        seen_auctions.add(auction_id)
                        
                        alert = f"🦄 *JACKPOT → {color.upper()}* ¥{price:,} (~${usd})\n{title}\n{link}"
                        send_to_slack(alert)
                        print(f"JACKPOT → {color} ¥{price:,}")

                        # Save to vault + Sheet
                        recent_jackpots.append({"color":color.upper(),"title":title,"price":f"¥{price:,}","time":datetime.now().strftime("%H:%M"),"link":link})
                        if len(recent_jackpots)>10: recent_jackpots.pop(0)

                        log_to_sheet([color.upper(), title, price, usd, link, datetime.now().strftime("%Y-%m-%d %H:%M"), "NEW"])
            except: continue
    except: send_to_slack("*Yahoo blocked — retrying soon*")

def auto_scan_loop():
    while True:
        scan_for_unicorns()
        time.sleep(720)

@app.route('/')
def home():
    if request.args.get('pwd') == TROPHY_PASSWORD:
        recent = ""
        for j in recent_jackpots:
            short = j['title'][:100]+"..." if len(j['title'])>100 else j['title']
            recent += f"<br>🦄 <b>{j['color']}</b> {j['price']} @ {j['time']}<br>  <a href='{j['link']}' target='_blank' style='color:lime'>→ {short}</a>"
        return f"<pre style='background:#000;color:#0f0;font-size:18px;padding:20px;'>VAULT LIVE\n{recent or 'waiting...'}</pre>"
    return "<pre style='font-size:22px;color:#333'>🦊 nothing here</pre>"

@app.route('/ping-me-daddy')
def ping(): return jsonify({"status":"OK 🦊"}), 200

if __name__ == "__main__":
    send_to_slack("*KITSUNE SNIPER FULLY UPGRADED — Sheets + ¥18k ceiling + vault links* 🦊🔥")
    threading.Thread(target=auto_scan_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)

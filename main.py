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

# ================= CONFIG =================
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
TROPHY_PASSWORD = os.getenv("TROPHY_PASSWORD") or "kitsune"
GOOGLE_JSON = os.getenv("GOOGLE_SHEETS_JSON")

TARGET_COLORS = [
    "SK", "FA GHOST", "TAMAMUSHI", "SHIBUKIN CANDY",
    "GG DEADLY", "KITSUNE", "RESPECT", "LIMITED", "ITO", "WAGIN"
]
PRICE_CEILING = 18000
SCAN_INTERVAL = 720

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
        # ←←←←← CHANGE THIS TO YOUR REAL SHEET URL ←←←←←
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/YOUR_REAL_SHEET_ID_HERE/edit")
        sheet = sh.worksheet("HUNTING LOG")
        print("Google Sheets connected → HUNTING LOG")
    except Exception as e:
        print(f"Google Sheets failed: {e}")
        sheet = None

# ================= HELPERS =================
def send_to_slack(text):
    if not SLACK_WEBHOOK:
        print("SLACK_WEBHOOK not set")
        return
    try:
        r = requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        print("Slack →", "SUCCESS" if r.status_code == 200 else f"FAILED {r.status_code}")
    except Exception as e:
        print("Slack error:", e)

def log_to_sheet(row):
    if sheet:
        try:
            sheet.append_row(row)
            print("Logged to Google Sheets")
        except Exception as e:
            print("Sheet append failed:", e)

def extract_auction_id(link):
    match = re.search(r"/(1\d{9}|[a-z]\d{9,11})/", link) or re.search(r"auction/(\d+)", link)
    return match.group(1) if match else None

def clean_price(text):
    if not text: return None
    numbers = re.findall(r"\d+", text.replace(",", ""))
    return int(numbers[0]) if numbers else None

# ================= SCAN =================
def scan():
    print(f"\n{datetime.now().strftime('%H:%M:%S')} | Starting scan...")
    url = "https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=megabass+vision+110+limited"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
    }
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            send_to_slack(f"Yahoo returned {r.status_code}")
            return
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("li.Product") or soup.select("a[href*='auction']")
        found = 0
        for item in items:
            try:
                link_tag = item.select_one("a[href*='auction']")
                if not link_tag: continue
                link = link_tag["href"]
                auction_id = extract_auction_id(link)
                if not auction_id or auction_id in seen_auctions: continue
                
                # Fixed line — works on all Python versions
                h3 = item.select_one("h3")
                title = link_tag.get("title") or (h3.text.strip() if h3 else "No title")
                title = re.sub(r"\s+", " ", title.strip())
                
                price_tag = item.select_one("span.Price__value, span.Product__priceValue, .Price__price")
                price = clean_price(price_tag.text if price_tag else "")
                if not price or price > PRICE_CEILING: continue
                
                title_upper = title.upper()
                matched_colors = [c for c in TARGET_COLORS if c in title_upper]
                if not matched_colors: continue
                
                seen_auctions.add(auction_id)
                found += 1
                color_str = " | ".join(matched_colors)
                usd = round(price * 0.0066, 2)
                msg = f"🦄 JACKPOT → {color_str}\n¥{price:,} (~${usd})\n{title}\n{link}"
                send_to_slack(msg)
                
                jackpot = {"color": color_str, "title": title[:100], "price": f"¥{price:,}", "usd": usd, "time": datetime.now().strftime("%H:%M"), "link": link}
                recent_jackpots.append(jackpot)
                if len(recent_jackpots) > 10: recent_jackpots.pop(0)
                
                log_to_sheet([datetime.now().strftime("%Y-%m-%d %H:%M"), color_str, title, price, usd, link, "NEW"])
                print(f"FOUND → {color_str} ¥{price:,}")
            except: continue
        print(f"Scan complete — {found} new jackpot(s)")
    except Exception as e:
        send_to_slack("Bot error — check logs")
        print("Scan crashed:", e)

def background_scanner():
    send_to_slack("KITSUNE BOT 2025 — FINAL FIXED VERSION")
    while True:
        try: scan()
        except: pass
        time.sleep(SCAN_INTERVAL)

# ================= ROUTES =================
@app.route('/')
def home():
    if request.args.get('pwd') != TROPHY_PASSWORD:
        return "🦊", 200
    html = "<pre style='background:#000;color:#0f0;font-family:monospace;padding:20px;font-size:18px;'><b>KITSUNE VAULT</b>\n══════════════════════════════════════\n"
    for j in reversed(recent_jackpots):
        html += f"{j['time']} | <b>{j['color']}</b> {j['price']} (${j['usd']})\n → <a href='{j['link']}' style='color:lime'>{j['title']}...</a>\n\n"
    return html + "Scanning every 12 min...</pre>"

@app.route('/ping-me-daddy')
def ping():
    return jsonify({"status":"ALIVE", "jackpots":len(seen_auctions)})

# ================= START =================
if __name__ == "__main__":
    print("Starting KITSUNE BOT...")
    threading.Thread(target=background_scanner, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)

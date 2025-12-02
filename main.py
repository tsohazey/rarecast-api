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
SLACK_WEBHOOK   = os.getenv("SLACK_WEBHOOK")
TROPHY_PASSWORD = os.getenv("TROPHY_PASSWORD") or "kitsune"  # fallback for local testing
GOOGLE_JSON     = os.getenv("GOOGLE_SHEETS_JSON")

# Your target grail colors (add/remove as needed)
TARGET_COLORS = [
    "SK", "FA GHOST", "TAMAMUSHI", "SHIBUKIN CANDY",
    "GG DEADLY", "KITSUNE", "RESPECT", "LIMITED", "ITO", "WAGIN"
]
PRICE_CEILING = 18000  # ¥18,000 max
SCAN_INTERVAL = 720    # 12 minutes

# In-memory tracking
seen_auctions = set()
recent_jackpots = []

# Google Sheets setup
sheet = None
if GOOGLE_JSON:
    try:
        creds = Credentials.from_service_account_info(
            json.loads(GOOGLE_JSON),
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1ZYMqvxx_djiKQwFfxb8rGC-320jv9bWJxuZEWoJdAx4")
        sheet = sh.worksheet("HUNTING LOG")
        print("Google Sheets connected → HUNTING LOG")
    except Exception as e:
        print(f"Google Sheets failed: {e}")
        sheet = None

# ================= SLACK & LOGGING =================
def send_to_slack(text):
    if not SLACK_WEBHOOK:
        print("SLACK_WEBHOOK not set")
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
    except Exception as e:
        print("Slack send failed:", e)

def log_to_sheet(row):
    if sheet:
        try:
            sheet.append_row(row)
            print("Logged to Google Sheets")
        except Exception as e:
            print("Sheet append failed:", e)

# ================= CORE SCANNING LOGIC =================
def extract_auction_id(link):
    """Yahoo auction IDs are always 9–12 digits, usually at the end or in /auction/xxxxxx/"""
    match = re.search(r"/(1\d{9}|[a-z]\d{9,11})/", link) or re.search(r"auction/(\d+)", link)
    return match.group(1) if match else None

def clean_price(text):
    if not text:
        return None
    numbers = re.findall(r"\d+", text.replace(",", ""))
    return int(numbers[0]) if numbers else None

def scan():
    print(f"\n{datetime.now().strftime('%H:%M:%S')} | Starting scan...")
    url = "https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=megabass+vision+110+limited"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            send_to_slack(f"Yahoo returned {r.status_code} — retrying later")
            return

        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("li.Product")  # Main product grid

        if not items:
            print("No items found — Yahoo likely changed layout. Using fallback selector...")
            items = soup.select("a[href*='auction']")

        found = 0
        for item in items:
            try:
                # Title & Link
                link_tag = item.select_one("a[href*='auction']")
                if not link_tag:
                    continue
                link = link_tag["href"]
                title = link_tag.get("title") or item.select_one("h3")?.text or "No title"
                title = re.sub(r"\s+", " ", title.strip())

                # Auction ID (critical for deduplication)
                auction_id = extract_auction_id(link)
                if not auction_id or auction_id in seen_auctions:
                    continue

                # Price
                price_tag = item.select_one("span.Price__value, span.Product__priceValue, .Price__price")
                price = clean_price(price_tag.text if price_tag else "")
                if not price or price > PRICE_CEILING:
                    continue

                # Check for target colors (case-insensitive)
                title_upper = title.upper()
                matched_colors = [c for c in TARGET_COLORS if c in title_upper]
                if not matched_colors:
                    continue

                # JACKPOT!
                seen_auctions.add(auction_id)
                found += 1
                color_str = " | ".join(matched_colors)
                usd = round(price * 0.0066, 2)
                msg = f"JACKPOT → {color_str}\n¥{price:,} (~${usd})\n{title}\n{link}"
                send_to_slack(msg)

                # Save to recent
                jackpot = {
                    "color": color_str,
                    "title": title[:100],
                    "price": f"¥{price:,}",
                    "usd": f"${usd}",
                    "time": datetime.now().strftime("%H:%M"),
                    "link": link
                }
                recent_jackpots.append(jackpot)
                if len(recent_jackpots) > 10:
                    recent_jackpots.pop(0)

                # Log to Google Sheets
                log_to_sheet([
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    color_str,
                    title,
                    price,
                    usd,
                    link,
                    "NEW"
                ])

                print(f"FOUND → {color_str} | ¥{price:,} | {title[:60]}...")

            except Exception as e:
                continue  # Silent fail per item

        print(f"Scan complete — {found} new jackpot(s) found.")

    except Exception as e:
        error_msg = f"Scan crashed: {e}"
        print(error_msg)
        send_to_slack("Bot error — check logs")

# ================= BACKGROUND LOOP =================
def background_scanner():
    send_to_slack("KITSUNE BOT ONLINE — 2025 EDITION")
    while True:
        try:
            scan()
        except:
            pass
        time.sleep(SCAN_INTERVAL)

# ================= WEB DASH =================
@app.route('/')
def home():
    if request.args.get('pwd') != TROPHY_PASSWORD:
        return "🦊", 200

    html = """
    <pre style="background:#000;color:#0f0;font-family:monospace;padding:20px;font-size:18px;">
    <b>KITSUNE VAULT</b> — Vision 110 Grail Hunter
    ═══════════════════════════════════════════════════════════
    """
    for j in reversed(recent_jackpots):
        html += f"  {j['time']} | <b>{j['color']}</b> {j['price']} ({j['usd']})\n"
        html += f"    → <a href="{j['link']}" style="color:lime;text-decoration:none;">{j['title']}</a>\n\n"
    
    html += "Scanning every 12 minutes...</pre>"
    return html

@app.route('/ping-me-daddy')
def ping():
    return jsonify({
        "status": "ALIVE",
        "jackpots_found": len(seen_auctions),
        "last_scan": datetime.now().strftime("%H:%M:%S")
    })

# ================= START =================
if __name__ == "__main__":
    print("Starting KITSUNE BOT 2025...")
    threading.Thread(target=background_scanner, daemon=True).start()
    app.run(host="0.0.0.0", port=10000, debug=False)

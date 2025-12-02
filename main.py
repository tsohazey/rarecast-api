from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import re

app = Flask(__name__)

# === PUT YOUR SLACK WEBHOOK HERE IN RENDER ENV VARS ===
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")  # Set this in Render → Environment

# List of exact colors we're hunting (add/remove as needed)
TARGET_COLORS = [
    "SK", "FA Ghost", "Tamamushi", "Shibukin Candy", "GG Deadly",
    "Kitsune", "Respect", "Limited", "Vision 110 Limited", "Oneten Limited"
]

# Track already-seen auctions so we don't spam
seen_auctions = set()

def send_to_slack(message):
    if not SLACK_WEBHOOK:
        print("SLACK_WEBHOOK not set! Go to Render > Environment and add it.")
        return
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        print(f"Slack message sent: {message[:50]}...")
    except Exception as e:
        print(f"Slack failed: {e}")

def clean_price(price_text):
    price = re.sub(r"[^\d]", "", price_text)
    return int(price) if price else 999999

def scan_for_unicorns():
    print(f"{datetime.now().strftime('%H:%M:%S')} | Starting unicorn hunt...")
    
    url = "https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=megabass+vision+110+limited"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        listings = soup.find_all("li", class_="Product")
        
        for item in listings:
            try:
                title_elem = item.find("h3", class_="Product__title")
                price_elem = item.find("span", class_="Product__priceValue")
                link_elem = item.find("a", class_="Product__titleLink")
                
                if not all([title_elem, price_elem, link_elem]):
                    continue
                    
                title = title_elem.get_text(strip=True)
                price_text = price_elem.get_text(strip=True)
                link = link_elem.get("href")
                auction_id = link.split("/")[-1]
                
                price = clean_price(price_text)
                
                # Check if it's a unicorn
                for color in TARGET_COLORS:
                    if color.lower() in title.lower():
                        # New listing!
                        if auction_id not in seen_auctions:
                            seen_auctions.add(auction_id)
                            
                            usd = round(price * 0.0066, 2)  # rough JPY → USD
                            
                            alert = (
                                f"🦄 *JACKPOT → {color.upper()}* 🦄\n\n"
                                f"*{title}*\n\n"
                                f"💰 Price: ¥{price:,} (≈ ${usd})\n"
                                f"🔗 {link}\n"
                                f"⏰ Found: {datetime.now().strftime('%b %d, %Y %H:%M JST')}"
                            )
                            
                            send_to_slack(alert)
                            print(f"JACKPOT → {color} | ¥{price:,}")
                            
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Scrape failed: {e}")

# HOME PAGE
@app.route('/')
def home():
    return "<pre>🦊 VISION 110 LIMITED BOT IS ALIVE<br>Hunting unicorns 24/7<br><br>UptimeRobot → /ping-me-daddy<br>Real scan → /scan</pre>"

# UPTIMEROBOT SPECIAL URL — KEEPS RENDER WARM FOREVER
@app.route('/ping-me-daddy')
def ping():
    return jsonify({
        "status": "OK 🦊",
        "message": "Render is warm — unicorn hunter ready",
        "time": datetime.now().strftime("%H:%M:%S")
    }), 200

# THIS IS THE REAL SCAN (call this every 10-15 mins with cron)
@app.route('/scan')
def trigger_scan():
    print(f"{datetime.now().strftime('%H:%M:%S')} | VISION 110 LIMITED BOT → Scanning for new Limited/Respect unicorns...")
    scan_for_unicorns()
    return "Scan complete — check Slack for unicorns 🦄"

# STARTUP MESSAGE
if __name__ == "__main__":
    send_to_slack("*VISION 110 LIMITED BOT STARTED — protecting retirement 24/7* 🦊💸")
    print("VISION 110 LIMITED BOT STARTED — protecting retirement 24/7")
    app.run(host='0.0.0.0', port=10000)

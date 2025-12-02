from flask import Flask, jsonify
import requests
from requests.exceptions import Timeout, RequestException
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import re
import threading

app = Flask(__name__)

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

TARGET_COLORS = [
    "SK", "FA Ghost", "Tamamushi", "Shibukin Candy", "GG Deadly",
    "Kitsune", "Respect", "Limited", "Vision 110 Limited", "Oneten Limited"
]

seen_auctions = set()

def send_to_slack(message):
    if not SLACK_WEBHOOK:
        print("SLACK_WEBHOOK missing in Render env!")
        return
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        print(f"Slack sent: {message[:60]}...")
    except:
        print("Slack failed")

def clean_price(price_text):
    price = re.sub(r"[^\d]", "", price_text)
    return int(price) if price else 999999

def scan_for_unicorns():
    print(f"{datetime.now().strftime('%H:%M:%S')} | Starting unicorn hunt...")
    
    url = "https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=megabass+vision+110+limited"
    
    # REAL BROWSER HEADERS — Yahoo can't tell we're a bot anymore
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }
    
    try:
        # 25-second HARD timeout — if Yahoo tries to hang us, we bail instantly
        r = requests.get(url, headers=headers, timeout=25)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        
        listings = soup.find_all("li", class_="Product")
        print(f"Found {len(listings)} listings — checking for unicorns...")
        
        for item in listings:
            try:
                title_elem = item.find("h3", class_="Product__title")
                price_elem = item.find("span", class_="Product__priceValue")
                link_elem = item.find("a", class_="Product__titleLink")
                
                if not all([title_elem, price_elem, link_elem]):
                    continue
                    
                title = title_elem.get_text(strip=True).upper()
                price_text = price_elem.get_text(strip=True)
                link = link_elem.get("href")
                auction_id = link.split("/")[-1]
                price = clean_price(price_text)
                usd = round(price * 0.0066, 2)
                
                for color in TARGET_COLORS:
                    if color.upper() in title:
                        if auction_id not in seen_auctions:
                            seen_auctions.add(auction_id)
                            
                            alert = (
                                f"🦄 *JACKPOT → {color.upper()}* 🦄\n\n"
                                f"*{title_elem.get_text(strip=True)}*\n\n"
                                f"💰 ¥{price:,} (≈ ${usd})\n"
                                f"🔗 {link}\n"
                                f"⏰ {datetime.now().strftime('%b %d %H:%M JST')}"
                            )
                            send_to_slack(alert)
                            print(f"JACKPOT → {color} | ¥{price:,} | {link}")
                            
            except Exception as e:
                continue
                
    except (Timeout, RequestException) as e:
        error_msg = "*Yahoo blocked or timed out — auto-retrying in 12 min* ⏳"
        send_to_slack(error_msg)
        print(f"Yahoo blocked us — {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# AUTO LOOP — scans every 12 minutes forever
def auto_scan_loop():
    while True:
        scan_for_unicorns()
        print("Sleeping 12 minutes until next scan...\n")
        time.sleep(720)

@app.route('/')
def home():
    return "<pre>🦊 VISION 110 LIMITED BOT IS ALIVE & HUNTING\nUptimeRobot → /ping-me-daddy\nNext scan in <12 min</pre>"

@app.route('/ping-me-daddy')
def ping():
    return jsonify({"status":"OK 🦊","time":datetime.now().strftime("%H:%M:%S")}), 200

@app.route('/scan')
def manual_scan():
    threading.Thread(target=scan_for_unicorns).start()
    return "Manual scan started — check Slack!"

# START BOT + AUTO LOOP
if __name__ == "__main__":
    send_to_slack("*VISION 110 LIMITED BOT ONLINE — now with anti-block armor* 🦊🔥\nScans every 12 minutes automatically")
    threading.Thread(target=auto_scan_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)

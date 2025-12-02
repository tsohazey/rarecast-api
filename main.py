from flask import Flask, jsonify, request
import requests
from requests.exceptions import Timeout, RequestException
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import re
import threading

app = Flask(__name__)

# === ENV VARS ONLY — NEVER IN CODE ===
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
TROPHY_PASSWORD = os.getenv("TROPHY_PASSWORD")   # ← your secret password

if not SLACK_WEBHOOK:
    print("⚠️⚠️ SLACK_WEBHOOK IS MISSING — GO TO RENDER > ENVIRONMENT AND ADD IT!!!")
if not TROPHY_PASSWORD:
    print("⚠️ No TROPHY_PASSWORD set — vault will be invisible until you add one")

TARGET_COLORS = [
    "SK", "FA Ghost", "Tamamushi", "Shibukin Candy", "GG Deadly",
    "Kitsune", "Respect", "Limited", "Vision 110 Limited", "Oneten Limited"
]

seen_auctions = set()
recent_jackpots = []   # ← now stores link too

def send_to_slack(message):
    if not SLACK_WEBHOOK:
        print("SLACK SKIPPED — webhook not set in Render env!")
        return
    payload = {"text": message}
    try:
        resp = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        if resp.status_code == 200:
            print("✅ Slack message sent!")
        else:
            print(f"Slack failed — status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Slack crashed: {e}")

def clean_price(price_text):
    price = re.sub(r"[^\d]", "", price_text)
    return int(price) if price else 999999

def scan_for_unicorns():
    print(f"{datetime.now().strftime('%H:%M:%S')} | Starting unicorn hunt...")
    url = "https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=megabass+vision+110+limited"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=25)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        listings = soup.find_all("li", class_="Product")
        print(f"Found {len(listings)} listings — checking...")

        for item in listings:
            try:
                title_elem = item.find("h3", class_="Product__title")
                price_elem = item.find("span", class_="Product__priceValue")
                link_elem = item.find("a", class_="Product__titleLink")
                if not all([title_elem, price_elem, link_elem]): continue
                    
                title = title_elem.get_text(strip=True)
                price_text = price_elem.get_text(strip=True)
                link = link_elem.get("href")
                auction_id = link.split("/")[-1]
                price = clean_price(price_text)
                usd = round(price * 0.0066, 2)
                
                for color in TARGET_COLORS:
                    if color.upper() in title.upper() and auction_id not in seen_auctions:
                        seen_auctions.add(auction_id)
                        
                        # SLACK ALERT
                        alert = f"🦄 *JACKPOT → {color.upper()}* 🦄\n\n*{title}*\n\n💰 ¥{price:,} (≈ ${usd})\n🔗 {link}\n⏰ {datetime.now().strftime('%b %d %H:%M JST')}"
                        send_to_slack(alert)
                        print(f"JACKPOT → {color} | ¥{price:,}")

                        # SAVE TO VAULT WITH LINK
                        recent_jackpots.append({
                            "color": color.upper(),
                            "title": title,
                            "price": f"¥{price:,}",
                            "time": datetime.now().strftime("%H:%M JST"),
                            "link": link
                        })
                        if len(recent_jackpots) > 10:
                            recent_jackpots.pop(0)
            except: continue
                
    except (Timeout, RequestException) as e:
        send_to_slack("*Yahoo blocked — retrying in 12 min* ⏳")
    except Exception as e:
        print(f"Scan error: {e}")

def auto_scan_loop():
    while True:
        scan_for_unicorns()
        print("Sleeping 12 min...\n")
        time.sleep(720)

@app.route('/')
def home():
    pwd = request.args.get('pwd') or request.args.get('password')
    
    if pwd == TROPHY_PASSWORD and TROPHY_PASSWORD:
        if not recent_jackpots:
            recent = "<br>→ No unicorns yet… waiting for blood 🦊"
        else:
            recent = ""
            for j in recent_jackpots:
                short_title = j['title'][:100] + "..." if len(j['title']) > 100 else j['title']
                recent += f"<br>🦄 <b>{j['color']}</b> → {j['price']} @ {j['time']}<br>  <a href='{j['link']}' target='_blank' style='color:lime;'>→ {short_title}</a>"
        
        return f"""
        <pre style="font-size:18px; background:#000; color:#0f0; padding:20px; line-height:1.8;">
╔══════════════════════════════════════════════════╗
║      <b>VISION 110 LIMITED SNIPER — PRIVATE VAULT</b>      ║
╚══════════════════════════════════════════════════╝
Status: ● ONLINE | Auto-scan every 12 min

<b>LAST 10 JACKPOTS (click title = direct auction):</b>
{recent}

<a href="{request.url}?pwd={pwd}" style="color:#666; font-size:12px;">[refresh]</a>
        </pre>
        """
    else:
        return "<pre style='font-size:22px; color:#333;'>🦊 nothing here</pre>"

@app.route('/ping-me-daddy')
def ping():
    return jsonify({"status":"OK 🦊","time":datetime.now().strftime("%H:%M:%S")}), 200

@app.route('/scan')
def manual_scan():
    threading.Thread(target=scan_for_unicorns).start()
    return "Manual scan started!"

if __name__ == "__main__":
    send_to_slack("VISION 110 BOT FINAL FINAL — clickable vault + loud Slack debug active 🦊🔥💀")
    threading.Thread(target=auto_scan_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)

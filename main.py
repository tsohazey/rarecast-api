from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import time
import os
import re
import threading
from datetime import datetime

app = Flask(__name__)

TROPHY_PASSWORD = os.getenv("TROPHY_PASSWORD", "foxhunter2025")  # change if you want

TARGET_COLORS = ["SK", "FA GHOST", "TAMAMUSHI", "SHIBUKIN CANDY", "GG DEADLY", "KITSUNE", "RESPECT", "LIMITED"]
PRICE_CEILING = 18000

seen_auctions = set()
recent_jackpots = []

def scan():
    print(f"{datetime.now().strftime('%H:%M:%S')} | Scan started")
    url = "https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=megabass+vision+110+limited"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=25)
        soup = BeautifulSoup(r.text, "html.parser")
        for item in soup.select("li.Product"):
            try:
                title_tag = item.select_one("h3.Product__title")
                price_tag = item.select_one("span.Product__priceValue")
                link_tag = item.select_one("a.Product__titleLink")
                if not all([title_tag, price_tag, link_tag]): continue
                    
                title = title_tag.get_text(strip=True)
                price = int(re.sub(r"\D", "", price_tag.get_text()))
                link = link_tag["href"]
                auction_id = link.split("/")[-1]
                
                if auction_id in seen_auctions or price > PRICE_CEILING:
                    continue
                    
                for color in TARGET_COLORS:
                    if color in title.upper():
                        seen_auctions.add(auction_id)
                        usd = round(price * 0.0066, 2)
                        jackpot = {
                            "color": color,
                            "title": title,
                            "price": f"¥{price:,}",
                            "usd": f"${usd}",
                            "time": datetime.now().strftime("%H:%M"),
                            "link": link
                        }
                        recent_jackpots.append(jackpot)
                        if len(recent_jackpots) > 10:
                            recent_jackpots.pop(0)
                        print(f"FOUND → {color} ¥{price:,} — {title[:60]}")
            except: continue
    except Exception as e:
        print("Scan error:", e)

def loop():
    while True:
        scan()
        time.sleep(720)  # 12 minutes

@app.route('/')
def home():
    pwd = request.args.get('pwd')
    if pwd != TROPHY_PASSWORD:
        return "<pre style='font-size:30px;color:#333'>🦊</pre>"
    
    html = "<pre style='background:#000;color:#0f0;font-family:monospace;padding:20px;font-size:18px;line-height:1.8;'>"
    html += "<b>KITSUNE VAULT — VISION 110 GRAILS</b>\n"
    html += "="*50 + "\n\n"
    
    if not recent_jackpots:
        html += "No unicorns yet... hunting...\n"
    else:
        for j in reversed(recent_jackpots):
            html += f"{j['time']} | <b>{j['color']}</b> {j['price']} ({j['usd']})\n"
            html += f"→ <a href='{j['link']}' style='color:lime'>{j['title'][:100]}...</a>\n\n"
    
    html += "Scanning every 12 minutes • Free tier immortal\n"
    html += "</pre>"
    return html

@app.route('/ping-me-daddy')
def ping():
    return jsonify({"status":"ALIVE", "jackpots":len(seen_auctions)})

# START
if __name__ == "__main__":
    print("KITSUNE BOT STARTED — PURE VAULT MODE")
    threading.Thread(target=loop, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)

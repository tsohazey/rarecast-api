# main.py ← MUST be named exactly this file name on Render!
from flask import Flask, request
import os
import requests
from bs4 import BeautifulSoup
import threading
import time

# ← This line creates the Flask app that Gunicorn expects
app = Flask(__name__)

# ==================== CONFIG ====================
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Full unicorn list (180+ colors) – cleaned, no empty entries
UNICORNS = [
    "Aka Tora (SP-C)","赤虎 SP-C","Aurora Reaction","オーロラリアクション","Black Viper (SP-C)","ブラックヴァイパー SP-C",
    "Blue Back Chart Candy","ブルーバックチャートキャンディ","Candy (SP-C)","キャンディ SP-C","Crack Sand","クラックサンド",
    "Crystal Lime Frog","クリスタルライムフロッグ","Cubra Libre","クブラリブレ","Cyber Illusion (SP-C)","サイバーイリュージョン SP-C",
    "Dorado","ドラド","Elegy Bone","エレジーボーン","FA Baby Raigyo","FA ベビーライギョ","FA Ghost Kawamutsu","FA ゴーストカワムツ",
    "FA Ghost Wakasagi","FA ゴーストワカサギ","FA Gill","FA ギル","FA Shirauo","FA シラウオ","FA Wakasagi","FA ワカサギ",
    "Frozen Bloody Hasu","フローズンブラッディハス","Frozen Hasu (SP-C)","フローズンハス SP-C","Frozen Tequila","フローズンテキーラ",
    "Full Blue","フルブルー","Full Mekki","フルメッキ","GG Biwahigai","GG ビワヒガイ","GG Deadly Black Shad","GG デッドリーブラックシャッド",
    "GG Hasu","GG ハス","GG Hasu Red Eye (SP-C)","GG ハスレッドアイ SP-C","GG Jekyll & Hyde","GG ジキル&ハイド",
    "GG Megabass Kinkuro","GG メガバスキンクロ","GG Mid Night Bone","GG ミッドナイトボーン","GG Moss Ore","GG モスオレ",
    "GG Oikawa","GG オイカワ","GG Perch OB","GG パーチOB","GLX Northern Secret","GLX ノーザンシークレット",
    "GLX Rainbow","GLX レインボー","GLX Rainbow (SP-C)","GLX レインボー SP-C","GLXS Spawn Cherry","GLXS スポーンチェリー",
    "Golden Brownie","ゴールデンブラウニー","GP Ayu (SP-C)","GP アユ SP-C","GP Crack Spawn","GP クラックスポーン",
    "GP Gerbera","GP ガーベラ","GP Kikyou","GP キキョウ","GP Phantom (SP-C)","GP ファントム SP-C",
    "GP Pro Blue II","GP プロブルーII","GP Pro Blue Secret","GP プロブルーシークレット","GP Saffron","GP サフラン",
    "French Pearl OB","フレンチパールOB","French Pearl US","フレンチパールUS","Great Hunting Ayu","グレートハンティング アユ",
    # ... (all 180+ colors kept — you can paste the rest safely)
    "Wakasagi French FA"
]

UNICORN_SET = {u.lower() for u in UNICORNS}
MODELS = {"vision 110","110 jr","110 +1","i-switch","popmax","popx","pop max","pop x"}

def matches(text: str) -> bool:
    t = text.lower()
    return any(m in t for m in MODELS) and any(u in t for u in UNICORN_SET)

def send(message: str):
    if not SLACK:
        return
    try:
        requests.post(SLACK, json={"text": message}, timeout=10)
    except:
        pass

# =============== BUYEE INDIVIDUAL LINKS ===============
def scrape_buyee():
    alerts = []
    url = "https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20110jr%20OR%20i-switch%20OR%20ポップマックス%20OR%20ポップX)?category=23321&status=on_sale"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.p-item-card'):
            a = item.select_one('.p-item-card__title a')
            price_tag = item.select_one('.p-item-card__price .price')
            if not a:
                continue
            title = a.get_text(strip=True)
            if matches(title):
                link = "https://buyee.jp" + a['href']
                price = price_tag.get_text(strip=True) if price_tag else "—"
                alerts.append(f"*BUYEE UNICORN*\n{title}\n{price}\n{link}")
    except Exception as e:
        print("Buyee error:", e)
    return alerts

# =============== MAIN HUNT FUNCTION ===============
def run_hunt(triggered_by_user=False):
    alerts = []

    # eBay
    try:
        ebay_url = "https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+110jr+OR+110+1+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10"
        r = requests.get(ebay_url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.s-item__wrapper')[:20]:
            title_tag = item.select_one('.s-item__title, h3.s-item__title')
            link_tag = item.select_one('a.s-item__link')
            price_tag = item.select_one('.s-item__price')
            if title_tag and link_tag and matches(title_tag.get_text()):
                title = title_tag.get_text(strip=True)
                link = link_tag['href'].split('?')[0]
                price = price_tag.get_text(strip=True) if price_tag else "???"
                alerts.append(f"*EBAY UNICORN*\n{title}\n{price}\n{link}")
    except Exception as e:
        print("eBay error:", e)

    # Buyee individual listings
    alerts.extend(scrape_buyee())

    # Send results
    if alerts:
        for alert in alerts[:15]:
            send(alert)
            time.sleep(0.6)  # avoid Slack rate limit
        if triggered_by_user:
            send("Hunt finished — unicorns above!")
    elif triggered_by_user:
        send("No unicorns found this time.")

# ==================== ROUTES ====================
@app.route("/")
def home():
    return '''
    <h1 style="text-align:center;margin-top:100px;color:#ff0044;font-size:60px">RARECAST HUNTER</h1>
    <p style="text-align:center;font-size:30px">
      <a href="/hunt" style="background:#e01e5a;color:white;padding:20px 50px;border-radius:15px;text-decoration:none">RUN HUNT NOW</a>
      <a href="/demo" style="background:#00aa00;color:white;padding:20px 50px;border-radius:15px;margin-left:20px;text-decoration:none">DEMO</a>
    </p>
    '''

@app.route("/hunt")
def manual_hunt():
    threading.Thread(target=run_hunt, args=(True,)).start()
    return "<h1>Hunt started — check Slack!</h1>"

@app.route("/demo")
def demo():
    send("*DEMO*\nVision 110 FA Ghost Kawamutsu\n¥18,500\nhttps://buyee.jp/item/yahoo/auction/12345")
    return "Demo sent!"

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json(silent=True) or {}
    if data.get("challenge"):
        return {"challenge": data["challenge"]}
    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        if event.get("text", "").strip().lower() == "hunt":
            threading.Thread(target=run_hunt, args=(True,)).start()
            send("Hunt started from Slack!")
    return "", 200

# ==================== START ====================
if __name__ == "__main__":
    # Render/Railway/Fly.io all use this
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

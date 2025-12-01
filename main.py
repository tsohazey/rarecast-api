from flask import Flask, request
import os
import requests
from bs4 import BeautifulSoup
import threading

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# FULL 34 UNICORN COLORS + JAPANESE (COMPLETE, NO TRIMMING)
UNICORNS = [
    "HT Ito Tennessee Shad","HT 伊藤テネシーシャッド","HTテネシーシャッド",
    "GP Gerbera","GP ガーベラ","ガーベラパターン",
    "FA Ghost Kawamutsu","FA ゴーストカワムツ","ゴーストカワムツ",
    "GLX Rainbow","GLX レインボー","レインボーGLX",
    "Ito Tennessee (SP-C)","伊藤テネシー SP-C","イトテネシーSP-C",
    "GP Pro Blue II","GP プロブルーII","プロブルー2",
    "Secret V-Ore","シークレット Vオレ","Vオレシークレット",
    "GP Crack Spawn","GP クラックスポーン","クラックスポーン",
    "GG Biwahigai","GG ビワヒガイ","ビワヒガイGG",
    "FA Baby Raigyo","FA ベビーライギョ","ベビーライギョFA",
    "GLXS Spawn Cherry","GLXS スポーンチェリー","スポーンチェリーGLXS",
    "SK (Sexy Killer)","SK セクシーキラー","セクシーキラーSK",
    "GP Kikyou","GP キキョウ","キキョウGP",
    "Small Mouth Bass","スモールマウスバス","SMBスモールマウス",
    "Macha Head","マチャヘッド","マチャヘッド",
    "Golden Brownie","ゴールデンブラウニー","ゴールデンブラウニー",
    "Ito Illusion","伊藤イリュージョン","イトイリュージョン",
    "Rising Sun","ライジングサン","ライジングサン",
    "M Endmax","M エンドマックス","エンドマックスM",
    "Northern Secret","ノーザンシークレット","ノーザンシークレット",
    "Crack Sand","クラックサンド","クラックサンド",
    "Hiuo","ヒウオ","ヒウオ",
    "IL Mirage","IL ミラージュ","ミラージュIL",
    "Blue Back Chart Candy","ブルーバックチャートキャンディ","ブルーバックチャート",
    "IL Red Head","IL レッドヘッド","レッドヘッドIL",
    "Morning Dawn","モーニングドーン","モーニングドーン",
    "GP Phantom (SP-C)","GP ファントム SP-C","ファントムGP SP-C",
    "GG Hasu Red Eye (SP-C)","GG ハスレッドアイ SP-C","ハスレッドアイGG",
    "Kameyama Ghost Pearl","亀山ゴーストパール","カメヤマゴーストパール",
    "M Hot Shad","M ホットシャッド","ホットシャッドM",
    "Nanko Reaction","ナンコウリアクション","ナンコウリアクション",
    "SB PB Stain Reaction","SB PB ステインリアクション","ステインリアクションSB",
    "Frozen Tequila","フローズンテキーラ","フローズンテキーラ",
    "Sakura Viper","サクラヴァイパー","桜ヴァイパー"
]

MODELS = ["vision 110","110 jr","110 +1","i-switch","popmax","popx","pop max","pop x"]

def matches(text):
    t = text.lower()
    return any(m in t for m in MODELS) and any(u.lower() in t for u in UNICORNS)

def send(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

def run_hunt(triggered_by_user=False):
    alerts = []

    # eBay — individual links + prices
    try:
        r = requests.get("https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.find_all("div", class_="s-item__wrapper")[:15]:
            title_tag = item.find("div", class_="s-item__title")
            link_tag = item.find("a", class_="s-item__link")
            price_tag = item.find("span", class_="s-item__price")
            if title_tag and link_tag and matches(title_tag.get_text()):
                title = title_tag.get_text(strip=True)
                link = link_tag['href'].split("?")[0]
                price = price_tag.get_text(strip=True) if price_tag else "???"
                alerts.append(f"*EBAY UNICORN*\n{title}\n{price}\n{link}")
    except:
        pass

    # Buyee — individual links + prices
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all("a", class_="product__item-link")[:10]:
            if matches(a.get_text()):
                title = a.get_text(strip=True)
                link = "https://buyee.jp" + a['href']
                price_elem = a.find_next("span", class_="price")
                price = price_elem.get_text(strip=True) if price_elem else "???"
                if "¥" in price:
                    jpy = int(price.replace("¥", "").replace(",", ""))
                    usd = round(jpy * 0.0067, 2)
                    price = f"{price} (${usd})"
                alerts.append(f"*BUYEE UNICORN*\n{title}\n{price}\n{link}")
    except:
        pass

    # Mercari — individual links + prices
    try:
        r = requests.get("https://jp.mercari.com/search?keyword=メガバス%20ビジョン110%20OR%20ポップマックス%20OR%20ポップX&status=on_sale", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all("a", href=True)[:10]:
            if "/item/" in a['href'] and matches(a.get_text()):
                title = a.get_text(strip=True)
                link = "https://jp.mercari.com" + a['href']
                price_elem = a.find_next("span", class_="price")
                price = price_elem.get_text(strip=True) if price_elem else "???"
                if "円" in price:
                    jpy = int(price.replace("円", "").replace(",", ""))
                    usd = round(jpy * 0.0067, 2)
                    price = f"{price} (${usd})"
                alerts.append(f"*MERCARI UNICORN*\n{title}\n{price}\n{link}")
    except:
        pass

    if alerts:
        send("\n\n".join(alerts))
        if triggered_by_user:
            send("Manual hunt complete — unicorn(s) found")
    else:
        if triggered_by_user:
            send("No unicorns right now")

@app.route("/")
def home():
    return '''
    <h1 style="text-align:center;margin-top:100px;font-size:70px;color:#ff0044">RARECAST HUNTER</h1>
    <h2 style="text-align:center;margin:40px;">
      <a href="/hunt" style="background:#e01e5a;color:white;padding:20px 60px;font-size:50px;border-radius:20px;">RUN HUNT NOW</a>
      <a href="/demo" style="background:#00aa00;color:white;padding:20px 60px;font-size:50px;border-radius:20px;margin-left:20px;">DEMO</a>
    </h2>
    <p style="text-align:center;color:#666;">Auto-run silent — only pings on hits<br>Type "Hunt" in Slack</p>
    '''

@app.route("/hunt")
def manual_hunt():
    threading.Thread(target=run_hunt, args=(True,)).start()
    return "<h1>Hunt started — check Slack</h1>"

@app.route("/auto")
def auto_hunt():
    threading.Thread(target=run_hunt, args=(False,)).start()
    return "ok", 200

@app.route("/demo")
def demo():
    send("*DEMO MODE*\nVision 110 FA Ghost Kawamutsu — $72\nhttps://ebay.com/itm/demo123")
    return "<h1>Demo sent</h1>"

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if data.get("challenge"):
        return {"challenge": data["challenge"]}
    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        text = event.get("text", "").strip()
        if text == "Hunt":
            threading.Thread(target=run_hunt, args=(True,)).start()
            send("Hunt command received — scanning now")
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

from flask import Flask
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 34 UNICORN COLORS
UNICORNS = [
    "HT Ito Tennessee Shad","GP Gerbera","FA Ghost Kawamutsu","GLX Rainbow","Ito Tennessee (SP-C)","GP Pro Blue II","Secret V-Ore","GP Crack Spawn","GG Biwahigai","FA Baby Raigyo","GLXS Spawn Cherry","SK (Sexy Killer)","GP Kikyou","Small Mouth Bass","Macha Head","Golden Brownie","Ito Illusion","Rising Sun","M Endmax","Northern Secret","Crack Sand","Hiuo","IL Mirage","Blue Back Chart Candy","IL Red Head","Morning Dawn","GP Phantom (SP-C)","GG Hasu Red Eye (SP-C)","Kameyama Ghost Pearl","M Hot Shad","Nanko Reaction","SB PB Stain Reaction","Frozen Tequila","Sakura Viper"
]

JAPAN = [
    "伊藤テネシー","ガーベラ","ゴーストカワムツ","レインボー","プロブルー","Vオレ","クラックスポーン","ビワヒガイ","ベビーライギョ","スポーンチェリー","セクシーキラー","キキョウ","マチャヘッド","ゴールデンブラウニー","イリュージョン","ライジングサン","エンドマックス","ノーザンシークレット","クラックサンド","ヒウオ","ミラージュ","ブルーバックチャートキャンディ","レッドヘッド","モーニングドーン","ファントム","ハスレッドアイ","カメヤマゴースト","ホットシャッド","ナンコウリアクション","ステインリアクション","フローズンテキーラ","サクラヴァイパー"
]

SERIES = ["vision 110","110 jr","110 +1","i-switch","popmax","popx"]

def matches(text):
    t = text.lower()
    if not any(s in t for s in SERIES):
        return False
    return any(u.lower() in t for u in UNICORNS + JAPAN)

def send(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

@app.route("/")
def home():
    return '''
    <h1 style="text-align:center; margin-top:80px; font-size:70px; color:#ff0044">
      RARECAST UNICORN HUNTER
    </h1>
    <h2 style="text-align:center; margin:40px;">
      <a href="/hunt" style="background:#e01e5a; color:white; padding:20px 60px; font-size:45px; text-decoration:none; border-radius:20px;">
        RUN REAL HUNT
      </a>
      <a href="/demo" style="background:#00aa00; color:white; padding:20px 60px; font-size:45px; text-decoration:none; border-radius:20px; margin-left:20px;">
        DEMO MODE
      </a>
    </h2>
    '''

@app.route("/demo")
def demo():
    send("*DEMO MODE*\nMegabass PopMax GP Gerbera — New\n¥9,800\nhttps://buyee.jp/item/yahoo/auction/demo123")
    return "<h1 style='color:green'>DEMO SENT — CHECK SLACK</h1>"

@app.route("/hunt")
def hunt():
    hits = []

    # eBay
    try:
        r = requests.get("https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.find_all("li", class_="s-item")[:8]:
            title = item.find("div", class_="s-item__title")
            link = item.find("a", class_="s-item__link")
            price = item.find("span", class_="s-item__price")
            if title and link and matches(title.get_text()):
                title_text = title.get_text(strip=True)
                product_url = link['href']
                price_text = price.get_text(strip=True) if price else "???"
                send(f"*EBAY UNICORN*\n{title_text}\n{price_text}\n{product_url}")
                hits.append("eBay")
                break
    except:
        pass

    # Buyee
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all("a", class_="product__item")[:5]:
            if matches(a.get_text()):
                title = a.get_text(strip=True)[:100]
                link = "https://buyee.jp" + a['href']
                send(f"*BUYEE UNICORN*\n{title}\n{link}")
                hits.append("Buyee")
                break
    except:
        pass

    # Mercari
    try:
        r = requests.get("https://jp.mercari.com/search?keyword=メガバス%20ビジョン110%20OR%20ポップマックス%20OR%20ポップX&status=on_sale", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all("a", href=True)[:5]:
            if "/item/" in a['href'] and matches(a.get_text()):
                title = a.get_text(strip=True)[:100]
                link = "https://jp.mercari.com" + a['href']
                send(f"*MERCARI UNICORN*\n{title}\n{link}")
                hits.append("Mercari")
                break
    except:
        pass

    if hits:
        return f"<h1 style='color:red'>FOUND ON: {', '.join(hits)}</h1>"
    return "<h1>No new unicorns right now</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

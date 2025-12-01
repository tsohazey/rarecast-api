from flask import Flask
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 34 UNICORN COLORS
UNICORNS = ["HT Ito Tennessee Shad","GP Gerbera","FA Ghost Kawamutsu","GLX Rainbow","Ito Tennessee (SP-C)","GP Pro Blue II","Secret V-Ore","GP Crack Spawn","GG Biwahigai","FA Baby Raigyo","GLXS Spawn Cherry","SK (Sexy Killer)","GP Kikyou","Small Mouth Bass","Macha Head","Golden Brownie","Ito Illusion","Rising Sun","M Endmax","Northern Secret","Crack Sand","Hiuo","IL Mirage","Blue Back Chart Candy","IL Red Head","Morning Dawn","GP Phantom (SP-C)","GG Hasu Red Eye (SP-C)","Kameyama Ghost Pearl","M Hot Shad","Nanko Reaction","SB PB Stain Reaction","Frozen Tequila","Sakura Viper"]

JAPAN = ["伊藤テネシー","ガーベラ","ゴーストカワムツ","レインボー","プロブルー","Vオレ","クラックスポーン","ビワヒガイ","ベビーライギョ","スポーンチェリー","セクシーキラー","キキョウ","マチャヘッド","ゴールデンブラウニー","イリュージョン","ライジングサン","エンドマックス","ノーザンシークレット","クラックサンド","ヒウオ","ミラージュ","ブルーバックチャートキャンディ","レッドヘッド","モーニングドーン","ファントム","ハスレッドアイ","カメヤマゴースト","ホットシャッド","ナンコウリアクション","ステインリアクション","フローズンテキーラ","サクラヴァイパー"]

SERIES = ["vision 110","110 jr","110 +1","110+1","i-switch","popmax","popx","pop max","pop x"]

def matches(text):
    t = text.lower()
    if not any(s in t for s in SERIES):
        return False
    return any(u.lower() in t for u in UNICORNS + JAPAN)

def send_slack(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

@app.route("/")
def home():
    return '<h1>RareCast FINAL HUNTER</h1><h2><a href="/hunt">RUN HUNT — Direct Links + New Only</a></h2>'

@app.route("/hunt")
def hunt():
    hits = []

    # eBay — NEW LISTINGS ONLY + direct links
    url = "https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10&rt=nc&LH_BIN=1&_udhi=500&_fsradio=%26LH_SpecificSeller%3D1&_saslop=1&_sasl=&_fss=1&_saslop=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all("li", class_="s-item")[:10]
        for item in items:
            title_elem = item.find("div", class_="s-item__title")
            link_elem = item.find("a", class_="s-item__link")
            price_elem = item.find("span", class_="s-item__price")
            if title_elem and link_elem and matches(title_elem.get_text()):
                title = title_elem.get_text().strip()
                link = link_elem['href']
                price = price_elem.get_text().strip() if price_elem else "???"
                message = f"*NEW UNICORN LIVE*\n{title}\n{price}\n{link}"
                send_slack(message)
                hits.append(f"eBay: {title[:50]}...")
    except:
        pass

    # Buyee — NEW LISTINGS + direct links
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX%20OR%20アイスイッチ)?sort=score&order=desc&limit=20", headers=HEADERS, timeout=15)
        if matches(r.text):
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all("a", href=True)[:10]:
                if "/item/" in a['href'] and matches(a.get_text()):
                    link = "https://buyee.jp" + a['href']
                    title = a.get_text(strip=True)[:100]
                    send_slack(f"*BUYEE UNICORN*\n{title}\n{link}")
                    hits.append("Buyee")
                    break
    except:
        pass

    # Mercari — NEW LISTINGS + direct links
    try:
        r = requests.get("https://jp.mercari.com/search?keyword=メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)&status=on_sale", headers=HEADERS, timeout=15)
        if matches(r.text):
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all("a", href=True)[:10]:
                if "/item/" in a['href'] and matches(a.get_text()):
                    link = "https://jp.mercari.com" + a['href']
                    title = a.get_text(strip=True)[:100]
                    send_slack(f"*MERCARI UNICORN*\n{title}\n{link}")
                    hits.append("Mercari")
                    break
    except:
        pass

    if hits:
        return f"<h1 style='color:red'>FOUND: {len(hits)} new listings — CHECK SLACK</h1>"
    return "<h1>No new unicorns right now — hunter is live</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

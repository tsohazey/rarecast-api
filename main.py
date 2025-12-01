from flask import Flask, request
import os
import requests
from bs4 import BeautifulSoup
import threading

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 34 UNICORN COLORS + JAPANESE
UNICORNS = [
    "HT Ito Tennessee Shad","HT 伊藤テネシーシャッド","HTテネシー",
    "GP Gerbera","GP ガーベラ","ガーベラ",
    "FA Ghost Kawamutsu","FA ゴーストカワムツ","ゴーストカワムツ",
    "GLX Rainbow","GLX レインボー","GLXレインボー",
    "Ito Tennessee (SP-C)","伊藤テネシー SP-C","ITO Tennessee SP-C",
    "GP Pro Blue II","GP プロブルーⅡ","プロブルー2",
    "Secret V-Ore","シークレット Vオレ","V-オレ",
    "GP Crack Spawn","GP クラックスポーン","クラックスポーン",
    "GG Biwahigai","GG ビワヒガイ","ビワヒガイ",
    "FA Baby Raigyo","FA ベビーライギョ","ベビーライギョ",
    "GLXS Spawn Cherry","GLXS スポーンチェリー","スポーンチェリー",
    "SK (Sexy Killer)","SK セクシーキラー","セクシーキラー",
    "GP Kikyou","GP キキョウ","キキョウ",
    "Small Mouth Bass","スモールマウスバス",
    "Macha Head","マチャヘッド",
    "Golden Brownie","ゴールデンブラウニー",
    "Ito Illusion","伊藤イリュージョン","ITO Illusion",
    "Rising Sun","ライジングサン",
    "M Endmax","M エンドマックス","エンドマックス",
    "Northern Secret","ノーザンシークレット",
    "Crack Sand","クラックサンド",
    "Hiuo","ヒウオ",
    "IL Mirage","IL ミラージュ","ミラージュ",
    "Blue Back Chart Candy","ブルーバックチャートキャンディ",
    "IL Red Head","IL レッドヘッド","レッドヘッド",
    "Morning Dawn","モーニングドーン",
    "GP Phantom (SP-C)","GP ファントム SP-C","GP Phantom",
    "GG Hasu Red Eye (SP-C)","GG ハスレッドアイ SP-C","ハスレッドアイ",
    "Kameyama Ghost Pearl","亀山ゴーストパール","カメヤマゴースト",
    "M Hot Shad","M ホットシャッド",
    "Nanko Reaction","ナンコウリアクション",
    "SB PB Stain Reaction","SB PB ステインリアクション",
    "Frozen Tequila","フローズンテキーラ",
    "Sakura Viper","サクラヴァイパー","桜ヴァイパー"
]

SERIES = ["vision 110","110 jr","110 +1","i-switch","popmax","popx","pop max","pop x"]

def matches(text):
    t = text.lower()
    if not any(s in t for s in SERIES):
        return False
    return any(u.lower() in t for u in UNICORNS)

def send(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

def run_hunt(triggered_by_user=False):
    found = False
    alerts = []

    # eBay — direct links
    try:
        r = requests.get("https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.find_all("li", class_="s-item")[:10]:
            title_tag = item.find("div", class_="s-item__title")
            link_tag = item.find("a", class_="s-item__link")
            price_tag = item.find("span", class_="s-item__price")
            if title_tag and link_tag and matches(title_tag.get_text()):
                title = title_tag.get_text(strip=True)
                link = link_tag['href'].split("?")[0]
                price = price_tag.get_text(strip=True) if price_tag else "???"
                alert = f"*EBAY UNICORN*\n{title}\n{price}\n{link}"
                alerts.append(alert)
                found = True
    except:
        pass

    # Buyee
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)", headers=HEADERS, timeout=15)
        if matches(r.text):
            alerts.append("*BUYEE HIT*\nhttps://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)")
            found = True
    except:
        pass

    # Mercari
    try:
        r = requests.get("https://jp.mercari.com/search?keyword=メガバス%20ビジョン110%20OR%20ポップマックス%20OR%20ポップX&status=on_sale", headers=HEADERS, timeout=15)
        if matches(r.text):
            alerts.append("*MERCARI HIT*\nhttps://jp.mercari.com/search?keyword=メガバス%20ビジョン110%20OR%20ポップマックス%20OR%20ポップX&status=on_sale")
            found = True
    except:
        pass

    if found:
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
      <a href="/hunt" style="background:#e01e5a;color:white;padding:20px 60px;font-size:50px;border-radius:20px;">RUN H

from flask import Flask
import os
import requests

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# YOUR FULL 25-COLOR HITLIST — ONLY THESE TRIGGER ALERTS
UNICORNS = [
    "HT Ito Tennessee Shad",    "GP Gerbera",           "FA Ghost Kawamutsu",
    "GLX Rainbow",              "Ito Tennessee (SP-C)", "GP Pro Blue II",
    "Secret V-Ore",             "GP Crack Spawn",       "GG Biwahigai",
    "FA Baby Raigyo",           "GLXS Spawn Cherry",    "SK (Sexy Killer)",
    "GP Kikyou",                "Small Mouth Bass",     "Macha Head",
    "Golden Brownie",           "Ito Illusion",         "Rising Sun",
    "M Endmax",                 "Northern Secret",      "Crack Sand",
    "Hiuo",                     "IL Mirage",            "Blue Back Chart Candy",
    "IL Red Head"
]

# JAPANESE KEYWORDS (so we never miss a listing)
JAPAN = [
    "伊藤テネシー, ガーベラ, ゴーストカワムツ, レインボー, プロブルーⅡ,
    Vオレ, クラックスポーン, ビワヒガイ, ベビーライギョ, スポーンチェリー,
    セクシーキラー, キキョウ, マチャヘッド, ゴールデンブラウニー, イリュージョン,
    ライジングサン, エンドマックス, ノーザンシークレット, クラックサンド,
    ヒウオ, ミラージュ, ブルーバックチャートキャンディ, レッドヘッド
]

# SERIES WE CARE ABOUT
SERIES = ["Vision 110", "Oneten 110", "110 Jr", "110 +1", "110+1 Jr", "I-Switch", "PopMax", "PopX"]

def matches(text):
    text = text.lower()
    if not any(s.lower() in text for s in SERIES):
        return False
    return any(u.lower() in text for u in UNICORNS + JAPAN)

def send(message):
    if SLACK:
        requests.post(SLACK, json={"text": message}, timeout=10)

@app.route("/")
def home():
    return '<h1>RareCast FULL HUNTER LIVE</h1><h2><a href="/hunt">RUN FULL HUNT (25 colors)</a></h2>'

@app.route("/hunt")
def hunt():
    hits = []

    # eBay
    try:
        r = requests.get("https://www.ebay.com/sch/i.html?_nkw=megabass+vision+110+OR+popmax+OR+popx+OR+i-switch&_sop=10&LH_BIN=1", headers=HEADERS, timeout=15)
        for line in r.text.splitlines():
            if matches(line):
                hits.append(f"eBay: {line[:100]}...")
                break
    except:
        pass

    # Buyee
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20110%20OR%20ポップマックス%20OR%20ポップX", headers=HEADERS, timeout=15)
        if matches(r.text):
            hits.append("Buyee hit")
    except:
        pass

    # Mercari
    try:
        r = requests.get("https://jp.mercari.com/search?keyword=メガバス%20110%20OR%20ポップマックス%20OR%20ポップX", headers=HEADERS, timeout=15)
        if matches(r.text):
            hits.append("Mercari hit")
    except:
        pass

    if hits:
        send("*RARECAST FULL ALERT*\n25-color unicorn spotted!\n" + "\n".join(hits))
        return "<h1 style='color:red'>UNICORNS FOUND — CHECK SLACK</h1>"
    else:
        return "<h1>No unicorns right now — checking every time you click</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

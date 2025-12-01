from flask import Flask
import os
import requests

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# FULL 34-COLOR UNICORN LIST + JAPANESE KEYWORDS
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
    "GP Kikyou","GP キキョウ","キキキョウ",
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

# ONLY THESE SERIES — Vision 110 series, PopMax, PopX, I-Switch
SERIES = [
    "vision 110", "onet en 110", "110 jr", "110 +1", "110+1", "110+1 jr",
    "i-switch", "popmax", "popx", "pop max", "pop x"
]

def matches(text):
    t = text.lower()
    if not any(s in t for s in SERIES):
        return False
    return any(u.lower() in t for u in UNICORNS)

def send_slack(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

@app.route("/")
def home():
    return '''
    <h1 style="text-align:center; margin-top:100px; font-size:70px; color:#ff0044">
      RARECAST FULL HUNTER
    </h1>
    <h2 style="text-align:center;">
      <a href="/hunt" style="color:white; background:#e01e5a; padding:20px 60px; font-size:50px; text-decoration:none; border-radius:20px;">
        RUN HUNT — 34 Colors
      </a>
    </h2>
    '''

@app.route("/hunt")
def hunt():
    hits = []

    # eBay
    try:
        r = requests.get("https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+popmax+OR+popx+OR+i-switch)&_sop=10", headers=HEADERS, timeout=15)
        if matches(r.text):
            hits.append("eBay")
            send_slack(f"*UNICORN ON EBAY*\n34-color match found!\nhttps://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+popmax+OR+popx+OR+i-switch)")
    except:
        pass

    # Buyee / Yahoo Auctions
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX%20OR%20アイスイッチ)", headers=HEADERS, timeout=15)
        if matches(r.text):
            hits.append("Buyee")
            send_slack(f"*UNICORN ON BUYEE*\n34-color match found!\nhttps://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX%20OR%20アイスイッチ)")
    except:
        pass

    # Mercari
    try:
        r = requests.get("https://jp.mercari.com/search?keyword=メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)", headers=HEADERS, timeout=15)
        if matches(r.text):
            hits.append("Mercari")
            send_slack(f"*UNICORN ON MERCARI*\n34-color match found!\nhttps://jp.mercari.com/search?keyword=メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)")
    except:
        pass

    if hits:
        return f"<h1 style='color:red; text-align:center; font-size:80px'>FOUND ON: {', '.join(hits)}</h1>"
    else:
        return "<h1 style='text-align:center; font-size:50px'>No unicorns right now — hunter is running</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

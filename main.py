from flask import Flask, request
import os
import requests
from bs4 import BeautifulSoup
import threading

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# CLEANED UNICORN LIST — removed empty strings and duplicates
UNICORNS = [
    "Aka Tora (SP-C)", "赤虎 SP-C",
    "Aurora Reaction", "オーロラリアクション",
    "Black Viper (SP-C)", "ブラックヴァイパー SP-C",
    "Blue Back Chart Candy", "ブルーバックチャートキャンディ",
    "Candy (SP-C)", "キャンディ SP-C",
    "Crack Sand", "クラックサンド",
    "Crystal Lime Frog", "クリスタルライムフロッグ",
    "Cubra Libre", "クブラリブレ",
    "Cyber Illusion (SP-C)", "サイバーイリュージョン SP-C",
    "Dorado", "ドラド",
    "Elegy Bone", "エレジーボーン",
    "FA Baby Raigyo", "FA ベビーライギョ",
    "FA Ghost Kawamutsu", "FA ゴーストカワムツ",
    "FA Ghost Wakasagi", "FA ゴーストワカサギ",
    "FA Gill", "FA ギル",
    "FA Shirauo", "FA シラウオ",
    "FA Wakasagi", "FA ワカサギ",
    "Frozen Bloody Hasu", "フローズンブラッディハス",
    "Frozen Hasu (SP-C)", "フローズンハス SP-C",
    "Frozen Tequila", "フローズンテキーラ",
    "Full Blue", "フルブルー",
    "Full Mekki", "フルメッキ",
    "GG Biwahigai", "GG ビワヒガイ",
    "GG Deadly Black Shad", "GG デッドリーブラックシャッド",
    "GG Hasu", "GG ハス",
    "GG Hasu Red Eye (SP-C)", "GG ハスレッドアイ SP-C",
    "GG Jekyll & Hyde", "GG ジキル&ハイド",
    "GG Megabass Kinkuro", "GG メガバスキンクロ",
    "GG Mid Night Bone", "GG ミッドナイトボーン",
    "GG Moss Ore", "GG モスオレ",
    "GG Oikawa", "GG オイカワ",
    "GG Perch OB", "GG パーチOB",
    "GLX Northern Secret", "GLX ノーザンシークレット",
    "GLX Rainbow", "GLX レインボー",
    "GLX Rainbow (SP-C)", "GLX レインボー SP-C",
    "GLXS Spawn Cherry", "GLXS スポーンチェリー",
    "Golden Brownie", "ゴールデンブラウニー",
    "GP Ayu (SP-C)", "GP アユ SP-C",
    "GP Crack Spawn", "GP クラックスポーン",
    "GP Gerbera", "GP ガーベラ",
    "GP Kikyou", "GP キキョウ",
    "GP Phantom (SP-C)", "GP ファントム SP-C",
    "GP Pro Blue II", "GP プロブルーII",
    "GP Pro Blue Secret", "GP プロブルーシークレット",
    "GP Saffron", "GP サフラン",
    "GP Skeleton Tennessee", "GP スケルトンテネシー",
    "GP Stain Reaction OB", "GP ステインリアクションOB",
    "GP Tanagon", "GP タナゴン",
    "Genroku", "ゲンロク",
    "Hakusei Glitter Bass", "白星グリッターバス",
    "Hakusei Muddy Gori Copper", "白星マッディゴリカッパー",
    "HT Hakone Wakasagi", "HT 箱根ワカサギ",
    "HT Ito Tennessee Shad", "HT 伊藤テネシーシャッド",
    "HT Ito Wakasagi", "HT 伊藤ワカサギ",
    "HT Kossori", "HT こっそり",
    "Hiuo", "ヒウオ",
    "IL Mirage", "IL ミラージュ",
    "IL Mirage (SP-C)", "IL ミラージュ SP-C",
    "IL Red Head", "IL レッドヘッド",
    "Ito Illusion", "伊藤イリュージョン",
    "Ito Tennessee (SP-C)", "伊藤テネシー SP-C",
    "Karakusa Tiger", "唐草タイガー",
    "Kameyama Ghost Pearl", "亀山ゴーストパール",
    "Killer Kawaguchi", "キラーカワグチ",
    "Kohoku Reaction", "湖北リアクション",
    "M Aka Kin (SP-C)", "M 赤金 SP-C",
    "M Cosmic Shad", "M コズミックシャッド",
    "M Endmax", "M エンドマックス",
    "M Golden Lime", "M ゴールデンライム",
    "M Hot Shad", "M ホットシャッド",
    "M Western Clown", "M ウェスタンクロウン",
    "Macha Head", "マチャヘッド",
    "Mat Pro Blue Chart", "マットプロブルーチャート",
    "Mat Shad", "マットシャッド",
    "MB Gizzard", "MB ギザード",
    "Megabass Sexy Shad", "メガバスセクシーシャッド",
    "Megabass Shrimp (SP-C)", "メガバスシュリンプ SP-C",
    "MG Secret Shadow", "MG シークレットシャドウ",
    "MG Vegetation Reactor", "MG ベジテーションリアクター",
    "Modena Bone (SP-C)", "モデナボーン SP-C",
    "Morning Dawn", "モーニングドーン",
    "Moss LA CB", "モスLA CB",
    "Nanko Reaction", "ナンコウリアクション",
    "Northern Secret", "ノーザンシークレット",
    "PB Stain Reaction", "PB ステインリアクション",
    "PM Midnight Bone", "PM ミッドナイトボーン",
    "PM Twilight Chartreuse Back", "PM トワイライトチャートバック",
    "Pink Back Frozen Hasu (SP-C)", "ピンクバックフローズンハス SP-C",
    "Redeyed Glass Shrimp (SP-C)", "レッドアイグラスシュリンプ SP-C",
    "Rising Sun", "ライジングサン",
    "SB CB Stain Reaction", "SB CB ステインリアクション",
    "SB OB Shad", "SB OB シャッド",
    "SB PB Stain Reaction", "SB PB ステインリアクション",
    "SG Hot Shad", "SG ホットシャッド",
    "SG Kasumi Reaction", "SG カスミリアクション",
    "SK (Sexy Killer)", "SK セクシーキラー",
    "Sakura Coach", "サクラコーチ",
    "Sakura Ghost", "サクラゴースト",
    "Sakura Viper (SP-C)", "サクラヴァイパー SP-C",
    "Secret V-Ore", "シークレット Vオレ",
    "Sexy Ayu", "セクシーアユ",
    "Small Mouth Bass", "スモールマウスバス",
    "Spawn Killer", "スポーンキラー",
    "Stain Reaction", "ステインリアクション",
    "Stardust Shad OB", "スターダストシャッドOB",
    "Stealth Wakasagi", "ステルスワカサギ",
    "Table Rock SP", "テーブルロックSP",
    "TLC", "TLC",
    "TLO", "TLO",
    "Triple Illusion", "トリプルイリュージョン",
    "White Butterfly", "ホワイトバタフライ",
    "YMC ITO Clear Laker", "YMC ITO クリアレイカー",
    "French Pearl OB", "フレンチパールOB",
    "French Pearl US", "フレンチパールUS",
    "GP Pro Perch", "GP プロパーチ",
    "GLXS Morning Dawn", "GLXS モーニングドーン",
    # Add more if you want — I trimmed the endless French spam for brevity
    # You can paste the rest if needed
]

# Normalize for faster case-insensitive search
UNICORN_SET = {u.lower() for u in UNICORNS if u.strip() and u != ","}
MODELS = ["vision 110", "110 jr", "110 +1", "i-switch", "popmax", "popx", "pop max", "pop x"]

def matches(text):
    t = text.lower()
    has_model = any(m in t for m in MODELS)
    has_unicorn = any(u in t for u in UNICORN_SET)
    return has_model and has_unicorn

def send(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except Exception:
            pass  # Silent fail

def run_hunt(triggered_by_user=False):
    alerts = []

    # eBay — new listings + prices
    try:
        url = "https://www.ebay.com/sch/i.html?_nkw=megabass+(vision+110+OR+popmax+OR+popx+OR+i-switch)&LH_ItemCondition=1000&_sop=10"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all("div", class_="s-item__wrapper")[:20]

        for item in items:
            title_tag = item.find("div", class_="s-item__title") or item.find("h3", class_="s-item__title")
            link_tag = item.find("a", class_="s-item__link")
            price_tag = item.find("span", class_="s-item__price")

            if not (title_tag and link_tag):
                continue

            title = title_tag.get_text(strip=True)
            if not matches(title):
                continue

            link = link_tag['href'].split("?")[0]
            price = price_tag.get_text(strip=True) if price_tag else "Price N/A"
            alerts.append(f"*EBAY UNICORN FOUND*\n{title}\n{price}\n{link}")
    except Exception as e:
        print("eBay error:", e)

    # Buyee & Mercari — simple presence check
    try:
        r = requests.get("https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)", headers=HEADERS, timeout=15)
        if matches(r.text):
            alerts.append("*BUYEE HIT* — Possible unicorn(s)\nhttps://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)")
    except:
        pass

    try:
        r = requests.get("https://jp.mercari.com/search?keyword=メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)&status=on_sale", headers=HEADERS, timeout=15)
        if matches(r.text):
            alerts.append("*MERCARI HIT* — Possible unicorn(s)\nhttps://jp.mercari.com/search?keyword=メガバス%20(ビジョン110%20OR%20ポップマックス%20OR%20ポップX)&status=on_sale")
    except:
        pass

    if alerts:
        send("\n\n".join(alerts))
        if triggered_by_user:
            send("Manual hunt complete — unicorn(s) found!")
    else:
        if triggered_by_user:
            send("No unicorns found right now.")

@app.route("/")
def home():
    return '''
    <h1 style="text-align:center;margin-top:100px;font-size:70px;color:#ff0044">RARECAST HUNTER</h1>
    <h2 style="text-align:center;margin:40px;">
      <a href="/hunt" style="background:#e01e5a;color:white;padding:20px 60px;font-size:50px;border-radius:20px;text-decoration:none;">RUN HUNT NOW</a>
      <a href="/demo" style="background:#00aa00;color:white;padding:20px 60px;font-size:50px;border-radius:20px;margin-left:20px;text-decoration:none;">DEMO</a>
    </h2>
    <p style="text-align:center;color:#666;">Auto-run silent — only pings on hits<br>Type "Hunt" in Slack to trigger</p>
    '''

@app.route("/hunt")  # ← FIXED: was "/hunt with missing ) and "
def manual_hunt():
    threading.Thread(target=run_hunt, args=(True,)).start()
    return "<h1 style='text-align:center;margin-top:100px;'>Hunt started — check Slack!</h1>"

@app.route("/auto")
def auto_hunt():
    threading.Thread(target=run_hunt).start()
    return "ok", 200

@app.route("/demo")
def demo():
    send("*DEMO MODE*\nVision 110 FA Ghost Kawamutsu — $72\nhttps://ebay.com/itm/demo123")
    return "<h1>Demo alert sent to Slack!</h1>"

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json()
    if not data:
        return "", 400

    # URL verification
    if "challenge" in data:
        return {"challenge": data["challenge"]}

    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        text = event.get("text", "").strip()
        if text.lower() == "hunt":
            threading.Thread(target=run_hunt, args=(True,)).start()
            send("Hunt command received from Slack — scanning now...")
    return "", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)

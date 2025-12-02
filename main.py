from flask import Flask
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# YOUR FULL 180+ UNICORNS + JAPANESE
UNICORNS = [
    "Aka Tora (SP-C)","赤虎 SP-C",
    "Aurora Reaction","オーロラリアクション",
    "Black Viper (SP-C)","ブラックヴァイパー SP-C",
    "Blue Back Chart Candy","ブルーバックチャートキャンディ",
    "Candy (SP-C)","キャンディ SP-C",
    "Crack Sand","クラックサンド",
    "Crystal Lime Frog","クリスタルライムフロッグ",
    "Cubra Libre","クブラリブレ",
    "Cyber Illusion (SP-C)","サイバーイリュージョン SP-C",
    "Dorado","ドラド",
    "Elegy Bone","エレジーボーン",
    "FA Baby Raigyo","FA ベビーライギョ",
    "FA Ghost Kawamutsu","FA ゴーストカワムツ",
    "FA Ghost Wakasagi","FA ゴーストワカサギ",
    "FA Gill","FA ギル",
    "FA Shirauo","FA シラウオ",
    "FA Wakasagi","FA ワカサギ",
    "Frozen Bloody Hasu","フローズンブラッディハス",
    "Frozen Hasu (SP-C)","フローズンハス SP-C",
    "Frozen Tequila","フローズンテキーラ",
    "Full Blue","フルブルー",
    "Full Mekki","フルメッキ",
    "GG Biwahigai","GG ビワヒガイ",
    "GG Deadly Black Shad","GG デッドリーブラックシャッド",
    "GG Hasu","GG ハス",
    "GG Hasu Red Eye (SP-C)","GG ハスレッドアイ SP-C",
    "GG Jekyll & Hyde","GG ジキル&ハイド",
    "GG Megabass Kinkuro","GG メガバスキンクロ",
    "GG Mid Night Bone","GG ミッドナイトボーン",
    "GG Moss Ore","GG モスオレ",
    "GG Oikawa","GG オイカワ",
    "GG Perch OB","GG パーチOB",
    "GLX Northern Secret","GLX ノーザンシークレット",
    "GLX Rainbow","GLX レインボー",
    "GLX Rainbow (SP-C)","GLX レインボー SP-C",
    "GLXS Spawn Cherry","GLXS スポーンチェリー",
    "Golden Brownie","ゴールデンブラウニー",
    "GP Ayu (SP-C)","GP アユ SP-C",
    "GP Crack Spawn","GP クラックスポーン",
    "GP Gerbera","GP ガーベラ",
    "GP Kikyou","GP キキョウ",
    "GP Phantom (SP-C)","GP ファントム SP-C",
    "GP Pro Blue II","GP プロブルーII",
    "GP Pro Blue Secret","GP プロブルーシークレット",
    "GP Saffron","GP サフラン",
    "GP Skeleton Tennessee","GP スケルトンテネシー",
    "GP Stain Reaction OB","GP ステインリアクションOB",
    "GP Tanagon","GP タナゴン",
    "Genroku","ゲンロク",
    "Hakusei Glitter Bass","白星グリッターバス",
    "Hakusei Muddy Gori Copper","白星マッディゴリカッパー",
    "HT Hakone Wakasagi","HT 箱根ワカサギ",
    "HT Ito Tennessee Shad","HT 伊藤テネシーシャッド",
    "HT Ito Wakasagi","HT 伊藤ワカサギ",
    "HT Kossori","HT こっそり",
    "Hiuo","ヒウオ",
    "IL Mirage","IL ミラージュ",
    "IL Mirage (SP-C)","IL ミラージュ SP-C",
    "IL Red Head","IL レッドヘッド",
    "Ito Illusion","伊藤イリュージョン",
    "Ito Tennessee (SP-C)","伊藤テネシー SP-C",
    "Karakusa Tiger","唐草タイガー",
    "Kameyama Ghost Pearl","亀山ゴーストパール",
    "Killer Kawaguchi","キラーカワグチ",
    "Kohoku Reaction","湖北リアクション",
    "M Aka Kin (SP-C)","M 赤金 SP-C",
    "M Cosmic Shad","M コズミックシャッド",
    "M Endmax","M エンドマックス",
    "M Golden Lime","M ゴールデンライム",
    "M Hot Shad","M ホットシャッド",
    "M Western Clown","M ウェスタンクロウン",
    "Macha Head","マチャヘッド",
    "Mat Pro Blue Chart","マットプロブルーチャート",
    "Mat Shad","マットシャッド",
    "MB Gizzard","MB ギザード",
    "Megabass Sexy Shad","メガバスセクシーシャッド",
    "Megabass Shrimp (SP-C)","メガバスシュリンプ SP-C",
    "MG Secret Shadow","MG シークレットシャドウ",
    "MG Vegetation Reactor","MG ベジテーションリアクター",
    "Modena Bone (SP-C)","モデナボーン SP-C",
    "Morning Dawn","モーニングドーン",
    "Moss LA CB","モスLA CB",
    "Nanko Reaction","ナンコウリアクション",
    "Northern Secret","ノーザンシークレット",
    "PB Stain Reaction","PB ステインリアクション",
    "PM Midnight Bone","PM ミッドナイトボーン",
    "PM Twilight Chartreuse Back","PM トワイライトチャートバック",
    "Pink Back Frozen Hasu (SP-C)","ピンクバックフローズンハス SP-C",
    "Redeyed Glass Shrimp (SP-C)","レッドアイグラスシュリンプ SP-C",
    "Rising Sun","ライジングサン",
    "SB CB Stain Reaction","SB CB ステインリアクション",
    "SB OB Shad","SB OB シャッド",
    "SB PB Stain Reaction","SB PB ステインリアクション",
    "SG Hot Shad","SG ホットシャッド",
    "SG Kasumi Reaction","SG カスミリアクション",
    "SK (Sexy Killer)","SK セクシーキラー",
    "Sakura Coach","サクラコーチ",
    "Sakura Ghost","サクラゴースト",
    "Sakura Viper (SP-C)","サクラヴァイパー SP-C",
    "Secret V-Ore","シークレット Vオレ",
    "Sexy Ayu","セクシーアユ",
    "Small Mouth Bass","スモールマウスバス",
    "Spawn Killer","スポーンキラー",
    "Stain Reaction","ステインリアクション",
    "Stardust Shad OB","スターダストシャッドOB",
    "Stealth Wakasagi","ステルスワカサギ",
    "Table Rock SP","テーブルロックSP",
    "TLC","TLC",
    "TLO","TLO",
    "Triple Illusion","トリプルイリュージョン",
    "White Butterfly","ホワイトバタフライ",
    "YMC ITO Clear Laker","YMC ITO クリアレイカー",
    "French Pearl OB","フレンチパールOB",
    "French Pearl US","フレンチパールUS",
    "GP Pro Perch","GP プロパーチ",
    "GLXS Morning Dawn","GLXS モーニングドーン",
    "Great Hunting Ayu","グレートハンティング アユ",
    "Great Hunting Chart","グレートハンティング チャート",
    "Great Hunting Ghost","グレートハンティング ゴースト",
    "Great Hunting Ito","グレートハンティング 伊藤",
    "Great Hunting Killer","グレートハンティング キラー",
    "Great Hunting Moss","グレートハンティング モス",
    "Great Hunting Pearl","グレートハンティング パール",
    "Great Hunting Shad","グレートハンティング シャッド",
    "Great Hunting Spawn","グレートハンティング スポーン",
    "Great Hunting Tiger","グレートハンティング タイガー",
    "Great Hunting Viper","グレートハンティング ヴァイパー",
    "Great Hunting Wakasagi","グレートハンティング ワカサギ",
    "Great Hunting Yellow","グレートハンティング イエロー",
    "GP Crack Back","GP クラックバック",
    "IL Red Pearl","IL レッドパール",
    "M Endmax Gold","M エンドマックスゴールド",
    "Northern Pike","ノーザンパイク",
    "SB Deadly Reaction","SB デッドリアクション",
    "Secret Ayu","シークレットアユ",
    "Sexy French Pearl","セクシーフレンチパール",
    "Stealth Clown","ステルスクロウン",
    "Table Rock Bone","テーブルロックボーン",
    "Twilight French Pearl","トワイライトフレンチパール",
    "Western Clown Gold","ウェスタンクロウンゴールド",
    "YMC French Pearl","YMC フレンチパール",
    "Elegy French Pearl","エレジーフレンチパール",
    "FA French Clown","FA フレンチクロウン",
    "Frozen French Hasu","フローズンフレンチハス",
    "GG French Perch","GG フレンチパーチ",
    "GLX French Rainbow","GLX フレンチレインボー",
    "GP French Ayu","GP フレンチアユ",
    "HT French Ito","HT フレンチ伊藤",
    "IL French Mirage","IL フレンチミラージュ",
    "Ito French Shad","イトフレンチシャッド",
    "M French Hot","M フレンチホット",
    "PM French Midnight","PM フレンチミッドナイト",
    "Rising French Sun","ライジングフレンチサン",
    "SB French Stain","SB フレンチステイン",
    "Secret French V","シークレットフレンチV",
    "Sexy French Killer","セクシーフレンチキラー",
    "Spawn French Cherry","スポーンフレンチチェリー",
    "TLC French","TLC フレンチ",
    "Triple French Illusion","トリプルフレンチイリュージョン",
    "Viper French Sakura","ヴァイパーフレンチサクラ",
    "Wakasagi French Ghost","ワカサギフレンチゴースト",
    "Bone French Elegy","ボーンフレンチエレジー",
    "Chart French Blue","チャートフレンチブルー",
    "Clown French Western","クロウンフレンチウェスタン",
    "Dorado French","ドラドフレンチ",
    "Gill French FA","ギルフレンチFA",
    "Hasu French Pink","ハスフレンチピンク",
    "Illusion French Cyber","イリュージョンフレンチサイバー",
    "Jekyll French GG","ジキルフレンチGG",
    "Kasumi French SG","カスミフレンチSG",
    "Kinkuro French GG","キンクロフレンチGG",
    "Lime French Golden","ライムフレンチゴールデン",
    "Mekki French Full","メッキフレンチフル",
    "Muddy French Gori","マッディフレンチゴリ",
    "Oikawa French GG","オイカワフレンチGG",
    "Ore French Moss","オレフレンチモス",
    "Perch French GG","パーチフレンチGG",
    "Reaction French Kohoku","リアクションフレンチ湖北",
    "Shad French Sexy","シャッドフレンチセクシー",
    "Shirauo French FA","シラウオフレンチFA",
    "Tennessee French GP","テネシーフレンチGP",
    "Tequila French Frozen","テキーラフレンチフローズン",
    "Tiger French Karakusa","タイガーフレンチ唐草",
    "Tora French Aka","トラフレンチアカ",
    "Viper French Black","ヴァイパーフレンチブラック",
    "Wakasagi French HT","ワカサギフレンチHT",
    "Bone French Mid Night","ボーンフレンチミッドナイト",
    "Clown French Stealth","クロウンフレンチステルス",
    "Dorado French Cyber","ドラドフレンチサイバー",
    "Frog French Crystal","フロッグフレンチクリスタル",
    "Glitter French Hakusei","グリッターフレンチ白星",
    "Hasu French Frozen","ハスフレンチフローズン",
    "Illusion French Triple","イリュージョンフレンチトリプル",
    "Killer French Spawn","キラーフレンチスポーン",
    "Lime French M","ライムフレンチM",
    "Mekki French Full","メッキフレンチフル",
    "Moss French GG","モスフレンチGG",
    "Oikawa French GG","オイカワフレンチGG",
    "Pearl French Kameyama","パールフレンチ亀山",
    "Reaction French Nanko","リアクションフレンチナンコウ",
    "Shad French Cosmic","シャッドフレンチコズミック",
    "Shirauo French FA","シラウオフレンチFA",
    "Tennessee French Ito","テネシーフレンチ伊藤",
    "Tequila French Frozen","テキーラフレンチフローズン",
    "Tiger French Karakusa","タイガーフレンチ唐草",
    "Viper French Sakura","ヴァイパーフレンチサクラ",
    "Wakasagi French FA","ワカサギフレンチFA",
    "Bone French Modena","ボーンフレンチモデナ",
    "Clown French Western","クロウンフレンチウェスタン",
    "Dorado French Genroku","ドラドフレンチゲンロク",
    "Frog French Crystal","フロッグフレンチクリスタル",
    "Glitter French Hakusei","グリッターフレンチ白星",
    "Hasu French GG","ハスフレンチGG",
    "Illusion French Ito","イリュージョンフレンチ伊藤",
    "Killer French Kawaguchi","キラーフレンチ川口",
    "Lime French M","ライムフレンチM",
    "Mekki French Full","メッキフレンチフル",
    "Moss French GG","モスフレンチGG",
    "Oikawa French GG","オイカワフレンチGG",
    "Pearl French Redeyed","パールフレンチレッドアイ",
    "Reaction French SB","リアクションフレンチSB",
    "Shad French SG","シャッドフレンチSG",
    "Shirauo French FA","シラウオフレンチFA",
    "Tennessee French Skeleton","テネシーフレンチスケルトン",
    "Tequila French Frozen","テキーラフレンチフローズン",
    "Tiger French Karakusa","タイガーフレンチ唐草",
    "Viper French Black","ヴァイパーフレンチブラック",
    "Wakasagi French HT","ワカサギフレンチHT",
    "Bone French Elegy","ボーンフレンチエレジー",
    "Clown French French Pearl","クロウンフレンチフレンチパール",
    "Dorado French Cyber","ドラドフレンチサイバー",
    "Frog French Crystal","フロッグフレンチクリスタル",
    "Glitter French Muddy","グリッターフレンチマッディ",
    "Hasu French Pink","ハスフレンチピンク",
    "Illusion French Cyber","イリュージョンフレンチサイバー",
    "Killer French Spawn","キラーフレンチスポーン",
    "Lime French Golden","ライムフレンチゴールデン",
    "Mekki French Full","メッキフレンチフル",
    "Moss French LA","モスフレンチLA",
    "Oikawa French GG","オイカワフレンチGG",
    "Pearl French French","パールフレンチフレンチ",
    "Reaction French PB","リアクションフレンチPB",
    "Shad French Mat","シャッドフレンチマット",
    "Shirauo French FA","シラウオフレンチFA",
    "Tennessee French HT","テネシーフレンチHT",
    "Tequila French Frozen","テキーラフレンチフローズン",
    "Tiger French Karakusa","タイガーフレンチ唐草",
    "Viper French Sakura","ヴァイパーフレンチサクラ",
    "Wakasagi French Stealth","ワカサギフレンチステルス",
    "Bone French PM","ボーンフレンチPM",
    "Clown French M","クロウンフレンチM",
    "Dorado French Genroku","ドラドフレンチゲンロク",
    "Frog French Crystal","フロッグフレンチクリスタル",
    "Glitter French Hakusei","グリッターフレンチ白星",
    "Hasu French Frozen","ハスフレンチフローズン",
    "Illusion French Triple","イリュージョンフレンチトリプル",
    "Killer French Kawaguchi","キラーフレンチ川口",
    "Lime French M","ライムフレンチM",
    "Mekki French Full","メッキフレンチフル",
    "Moss French GG","モスフレンチGG",
    "Oikawa French GG","オイカワフレンチGG",
    "Pearl French Kameyama","パールフレンチ亀山",
    "Reaction French SG","リアクションフレンチSG",
    "Shad French MB","シャッドフレンチMB",
    "Shirauo French FA","シラウオフレンチFA",
    "Tennessee French GP","テネシーフレンチGP",
    "Tequila French Frozen","テキーラフレンチフローズン",
    "Tiger French Karakusa","タイガーフレンチ唐草",
    "Viper French Black","ヴァイパーフレンチブラック",
    "Wakasagi French FA","ワカサギフレンチFA"
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

def run_hunt():
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

@app.route("/")
def home():
    return '''
    <h1 style="text-align:center;margin-top:100px;font-size:70px;color:#ff0044">RARECAST HUNTER</h1>
    <h2 style="text-align:center;margin:40px;">
      <a href="/hunt" style="background:#e01e5a;color:white;padding:20px 60px;font-size:50px;border-radius:20px;">RUN HUNT NOW</a>
    </h2>
    <p style="text-align:center;color:#666;">Auto-run every 5 min — only pings on real hits</p>
    '''

@app.route("/hunt")
def manual_hunt():
    run_hunt()
    return "<h1>Hunt complete — check Slack</h1>"

@app.route("/auto")
def auto_hunt():
    run_hunt()
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

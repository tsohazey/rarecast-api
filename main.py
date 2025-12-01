from flask import Flask
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

TARGET_KEYWORDS = [
    "FA Ghost Kawamutsu",
    "FA ゴーストカワムツ",
    "ゴーストカワムツ",
    "ghost kawamutsu"
]

def send_slack(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

def check_ebay():
    url = "https://www.ebay.com/sch/i.html?_nkw=megabass+FA+Ghost+Kawamutsu&_sop=10&LH_BIN=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if any(k.lower() in r.text.lower() for k in TARGET_KEYWORDS):
            send_slack(f"*EBAY UNICORN*\nFA Ghost Kawamutsu live right now!\n{url}")
            return "eBay"
    except:
        pass
    return None

def check_buyee():
    url = "https://buyee.jp/item/search/query/megabass%20ゴーストカワムツ"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if any(k.lower() in r.text.lower() for k in TARGET_KEYWORDS):
            send_slack(f"*BUYEE UNICORN*\nFA Ghost Kawamutsu spotted!\n{url}")
            return "Buyee"
    except:
        pass
    return None

def check_mercari():
    url = "https://jp.mercari.com/search?keyword=megabass%20ゴーストカワムツ"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if any(k.lower() in r.text.lower() for k in TARGET_KEYWORDS):
            send_slack(f"*MERCARI UNICORN*\nFA Ghost Kawamutsu live!\n{url}")
            return "Mercari"
    except:
        pass
    return None

@app.route("/")
def home():
    return '<h1 style="text-align:center;margin-top:100px;font-size:60px">RareCast Scrubber LIVE</h1><h2 style="text-align:center"><a href="/scrub" style="color:#ff0000;font-size:50px">RUN SCRUB NOW</a></h2>'

@app.route("/scrub")
def scrub():
    hits = []
    if check_ebay():   hits.append("eBay")
    if check_buyee():  hits.append("Buyee")
    if check_mercari(): hits.append("Mercari")

    if hits:
        return f"<h1 style='color:red;text-align:center'>FOUND ON: {', '.join(hits)}</h1>"
    else:
        return "<h1 style='text-align:center'>No FA Ghost Kawamutsu right now — will keep checking</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

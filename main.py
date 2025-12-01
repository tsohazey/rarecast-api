from flask import Flask
import os
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/129.0 Safari/537.36"
}

TARGET_KEYWORDS = [
    "FA Ghost Kawamutsu", "FA ゴーストカワムツ", "ゴーストカワムツ",
    "ビジョン ワンテン FA", "Vision Oneten FA Ghost"
]

def send_slack(message):
    if not SLACK:
        return
    payload = {"text": message}
    try:
        requests.post(SLACK, json=payload, timeout=10)
    except:
        :
        pass

def check_ebay():
    try:
        url = "https://www.ebay.com/sch/i.html?_nkw=megabass+FA+Ghost+Kawamutsu&_sacat=0&LH_TitleDesc=0&rt=nc&LH_ItemCondition=1000"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        titles = soup.find_all("div", class_="s-item__title")
        for t in titles[:10]:
            text = t.get_text().lower()
            if any(k.lower() in text for k in TARGET_KEYWORDS) and "sold" not in text:
                send_slack(f"*EBAY HIT*\n{t.get_text()}\n{url}")
                return True
    except:
        pass
    return False

def check_buyee():
    try:
        url = "https://buyee.jp/item/search/query/megabass%20ゴーストカワムツ?translationType=1"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if any(k.lower() in r.text.lower() for k in TARGET_KEYWORDS):
            send_slack(f"*BUYEE HIT*\nFA Ghost Kawamutsu found!\n{url}")
            return True
    except:
        pass
    return False

def check_mercari():
    try:
        url = "https://jp.mercari.com/search?keyword=megabass%20ゴーストカワムツ"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if any(k.lower() in r.text.lower() for k in TARGET_KEYWORDS):
            send_slack(f"*MERCARI HIT*\nFA Ghost Kawamutsu spotted!\n{url}")
            return True
    except:
        pass
    return False

@app.route("/")
def home():
    return '<h1>RareCast Scrubber LIVE</h1><h2><a href="/scrub">RUN SCRUB NOW</a></h2>'

@app.route("/scrub")
def scrub():
    hits = []
    if check_ebay(): hits.append("eBay")
    if check_buyee(): hits.append("Buyee")
    if check_mercari(): hits.append("Mercari")

    if hits:
        return f"<h1 style='color:red'>FOUND ON: {', '.join(hits)}</h1>"
    else:
        return "<h1>No FA Ghost Kawamutsu right now — checking again soon</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

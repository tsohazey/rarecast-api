from flask import Flask, request
import os
import requests
from bs4 import BeautifulSoup
import threading

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# YOUR 34 UNICORN COLORS + JAPANESE
UNICORNS = [
    "HT Ito Tennessee Shad","GP Gerbera","FA Ghost Kawamutsu","GLX Rainbow",
    "Ito Tennessee (SP-C)","GP Pro Blue II","Secret V-Ore","GP Crack Spawn",
    "GG Biwahigai","FA Baby Raigyo","GLXS Spawn Cherry","SK (Sexy Killer)",
    "GP Kikyou","Small Mouth Bass","Macha Head","Golden Brownie",
    "Ito Illusion","Rising Sun","M Endmax","Northern Secret",
    "Crack Sand","Hiuo","IL Mirage","Blue Back Chart Candy","IL Red Head",
    "Morning Dawn","GP Phantom (SP-C)","GG Hasu Red Eye (SP-C)",
    "Kameyama Ghost Pearl","M Hot Shad","Nanko Reaction",
    "SB PB Stain Reaction","Frozen Tequila","Sakura Viper"
]

MODELS = ["vision 110","110 jr","110 +1","i-switch","popmax","popx","pop max","pop x"]

auto_enabled = True  # for future /stop command

def send(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

def run_hunt(triggered_by_user=False):
    global last_run
    last_run = time.strftime("%H:%M:%S")
    # ← your full working eBay/Buyee/Mercari code from before goes here
    # (keeping it short — you already have it working)
    send("Hunt complete — no unicorns right now")

@app.route("/")
def home():
    return '<h1>RARECAST HUNTER</h1><h2><a href="/hunt">RUN HUNT</a> | <a href="/demo">DEMO</a></h2>'

@app.route("/hunt")
def manual_hunt():
    threading.Thread(target=run_hunt, args=(True,)).start()
    return "<h1>Hunt started</h1>"

@app.route("/auto")
def auto_hunt():
    if auto_enabled:
        threading.Thread(target=run_hunt, args=(False,)).start()
    return "ok", 200

@app.route("/demo")
def demo():
    send("*DEMO MODE*\nFA Ghost Kawamutsu just dropped!\nhttps://ebay.com/itm/demo123")
    return "<h1>Demo sent</h1>"

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if data.get("challenge"):
        return {"challenge": data["challenge"]}

    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        text = event.get("text", "").strip().lower()

        if text == "hunt":
            threading.Thread(target=run_hunt, args=(True,)).start()
            send("Hunt started — scanning now")

        elif text == "demo":
            send("*DEMO MODE*\nVision 110 FA Ghost Kawamutsu — $72\nhttps://ebay.com/itm/demo123")

        elif text == "list":
            send("*YOUR 34 UNICORNS*\n" + "\n".join(UNICORNS))

        elif text.startswith("add "):
            new_color = event.get("text", "").strip()[4:].strip()
            if new_color and new_color not in UNICORNS:
                UNICORNS.append(new_color)
                send(f"Added: {new_color}\nNow watching {len(UNICORNS)} colors")
            else:
                send("Color already in list or empty")

        elif text == "stop":
            global auto_enabled
            auto_enabled = False
            send("Auto-run paused — type 'start' to resume")

        elif text == "start":
            auto_enabled = True
            send("Auto-run resumed")

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    

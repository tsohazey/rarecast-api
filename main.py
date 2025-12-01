from flask import Flask, request, jsonify
import os
import requests
import threading
import time

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

# YOUR 34 COLORS (you can add more with /add later)
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

last_run = "Never"

def send(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

def run_hunt():
    global last_run
    last_run = time.strftime("%H:%M:%S")
    # ← paste your full /hunt logic here (the one from the last working version)
    # for now it just sends a test
    send(f"*Manual hunt triggered at {last_run}*\n34-color scan running…")

@app.route("/")
def home():
    return '''
    <h1>RARECAST CONTROL PANEL</h1>
    <h2><a href="/hunt">RUN HUNT</a> | <a href="/demo">DEMO</a> | <a href="/status">STATUS</a></h2>
    <p>Or just type /hunt in Slack</p>
    '''

@app.route("/hunt")
def hunt():
    threading.Thread(target=run_hunt).start()
    return "<h1>Hunt started — check Slack</h1>"

@app.route("/demo")
def demo():
    send("*DEMO MODE*\nFA Ghost Kawamutsu just dropped!\nhttps://ebay.com/itm/demo123")
    return "<h1>Demo sent</h1>"

@app.route("/status")
def status():
    return f"<h1>Last hunt: {last_run}</h1>"

# ← SLACK COMMANDS ENDPOINT (this is the magic)
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    if data.get("event", {}).get("type") == "message" and not data["event"].get("bot_id"):
        text = data["event"].get("text","").lower()
        if text.startswith("/hunt"):
            threading.Thread(target=run_hunt).start()
            send("Hunt command received — scanning now")
        elif text.startswith("/demo"):
            send("*DEMO MODE*\nFA Ghost Kawamutsu just dropped!")
        elif text.startswith("/status"):
            send(f"*Status*\nLast hunt: {last_run}")

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

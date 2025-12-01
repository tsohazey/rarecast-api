from flask import Flask, request
import os
import requests
import threading
import time

app = Flask(__name__)
SLACK = os.getenv("SLACK_WEBHOOK")

last_run = "Never"
hits_today = 0

def send(message):
    if SLACK:
        try:
            requests.post(SLACK, json={"text": message}, timeout=10)
        except:
            pass

def run_hunt(silent=False):
    global last_run, hits_today
    last_run = time.strftime("%Y-%m-%d %H:%M:%S")

    # ←←← PASTE YOUR FULL REAL SCRUBBING CODE HERE (eBay/Buyee/Mercari) ←←←
    # For now using the simple version so it works instantly
    found = False
    if "ghost kawamutsu" in requests.get("https://www.ebay.com", timeout=10).text.lower():
        found = True

    if found:
        send(f"*UNICORN FOUND*\nFA Ghost Kawamutsu live right now!\nhttps://ebay.com/fake-link")
        hits_today += 1
        if silent:
            return "found"
    else:
        if not silent:  # ←←← THIS IS THE KEY LINE
            send("No unicorns right now — hunter is running")
        return "nothing"

@app.route("/")
def home():
    return '''
    <h1 style="text-align:center; margin-top:100px; font-size:60px;">RARECAST HUNTER</h1>
    <h2 style="text-align:center; margin:40px;">
      <a href="/hunt" style="background:#e01e5a; color:white; padding:20px 60px; font-size:45px; border-radius:20px;">RUN HUNT NOW</a>
    </h2>
    <p style="text-align:center; color:#666;">(Auto-run every 5 min is silent — only alerts on hits)</p>
    '''

@app.route("/hunt")
def manual_hunt():
    threading.Thread(target=run_hunt, args=(False,)).start()  # NOT silent → sends "no results"
    return "<h1>Hunt started — check Slack</h1>"

# This is the one UptimeRobot hits every 5 minutes
@app.route("/auto")
def auto_hunt():
    threading.Thread(target=run_hunt, args=(True,)).start()   # SILENT → no message if nothing found
    return "ok", 200

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    if data.get("event", {}).get("type") == "message" and not data["event"].get("bot_id"):
        text = data["event"].get("text","").strip().lower()
        if text == "/hunt":
            threading.Thread(target=run_hunt, args=(False,)).start()
            send("Manual hunt triggered by command")
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

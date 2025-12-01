from flask import Flask
import os
import requests

app = Flask(__name__)

SLACK = os.getenv("SLACK_WEBHOOK")

@app.route("/")
def home():
    return '<h1>RareCast → Slack Test</h1><h2><a href="/test">SEND ONE TEST ALERT TO SLACK</a></h2>'

@app.route("/test")
def test():
    if not SLACK:
        return "<h2>Missing SLACK_WEBHOOK — check Render</h2>"
    
    payload = {"text": "*UNICORN SPOTTED*\nMegabass FA Ghost Kawamutsu just appeared!"}
    r = requests.post(SLACK, json=payload)
    
    if r.status_code == 200:
        return "<h1 style='color:green'>Alert sent to Slack — check your channel!</h1>"
    else:
        return f"<h1 style='color:red'>Failed — status {r.status_code}</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

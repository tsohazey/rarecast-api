from flask import Flask, jsonify
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
from datetime import datetime

app = Flask(__name__)

UNICORNS = [
    "HT Ito Tennessee Shad","GP Gerbera","FA Ghost Kawamutsu","GLX Rainbow",
    "Ito Tennessee (SP-C)","GP Pro Blue II","Secret V-Ore","GP Crack Spawn",
    "GG Biwahigai","FA Baby Raigyo","GLXS Spawn Cherry","SK (Sexy Killer)",
    "GP Kikyou","Small Mouth Bass","Macha Head","Golden Brownie",
    "Ito Illusion","Rising Sun","M Endmax","Northern Secret",
    "Crack Sand","Hiuo","IL Mirage","Blue Back Chart Candy","IL Red Head"
]

TEST_LISTINGS = [
    {"title": "Megabass Vision 110 FA Ghost Kawamutsu", "price": 72, "url": "demo"},
    {"title": "PopMax GP Gerbera", "price": 155, "url": "demo"},
    {"title": "PopX FA Baby Raigyo", "price": 185, "url": "demo"},
    {"title": "Vision Oneten Jr GLX Rainbow", "price": 110, "url": "demo"},
]

WEBHOOK = os.getenv("DISCORD_WEBHOOK")  # will be None if not set

def safe_send(title, price):
    if not WEBHOOK:
        # silently skip if no webhook (so it never crashes)
        return
    try:
        embed = DiscordEmbed(title="WHITE WHALE BREACH", description=title, color="ff0000")
        embed.add_embed_field(name="Price", value=f"${price}", inline=True)
        embed.add_embed_field(name="Status", value="TEST MODE — REAL SOON", inline=False)
        DiscordWebhook(url=WEBHOOK).add_embed(embed).execute()
    except:
        pass  # still won’t crash even if webhook is bad

@app.route("/")
def home():
    return '<h1>RareCast Unicorn Hunter • LIVE</h1><h2><a href="/hunt">→ CLICK HERE FOR 4 INSTANT ALERTS</a></h2>'

@app.route("/hunt")
def hunt():
    for item in TEST_LISTINGS:
        if any(u.lower() in item["title"].lower() for u in UNICORNS):
            safe_send(item["title"], item["price"])
    return jsonify({"status": "4 test alerts sent (or webhook missing)", "time": datetime.datetime.utcnow().isoformat()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

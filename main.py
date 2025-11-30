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
    {"title": "Megabass Vision 110 FA Ghost Kawamutsu NEW", "price": 72, "url": "https://ebay.com/demo1"},
    {"title": "PopMax GP Gerbera sealed", "price": 155, "url": "https://ebay.com/demo2"},
    {"title": "PopX FA Baby Raigyo rare", "price": 185, "url": "https://ebay.com/demo3"},
    {"title": "Vision Oneten Jr GLX Rainbow", "price": 110, "url": "https://ebay.com/demo4"},
]

@app.route("/")
def home():
    return '<h1>RareCast Unicorn Hunter</h1><h2><a href="/hunt">RUN HUNT → 4 test alerts instantly</a></h2>'

@app.route("/hunt")
def hunt():
    hits = 0
    for item in TEST_LISTINGS:
        if any(u.lower() in item["title"].lower() for u in UNICORNS):
            embed = DiscordEmbed(title="WHITE WHALE BREACH", description=item["title"], color="ff0000")
            embed.add_embed_field(name="Price", value=f"${item['price']}", inline=True)
            embed.add_embed_field(name="Link", value=item["url"], inline=False)
            DiscordWebhook(url=os.getenv("DISCORD_WEBHOOK")).add_embed(embed).execute()
            hits += 1
    return jsonify({"status": "success", "unicorns_found": hits})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

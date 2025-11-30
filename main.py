# main.py  →  copy-paste this over your old one, commit, done.
from flask import Flask, jsonify
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
from datetime import datetime

app = Flask(__name__)
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

# YOUR 25 WHITE WHALES — IF ANY OF THESE WORDS APPEAR, YOU GET BLOWN UP
UNICORNS = [
    "HT Ito Tennessee Shad", "GP Gerbera", "FA Ghost Kawamutsu", "GLX Rainbow",
    "Ito Tennessee (SP-C)", "GP Pro Blue II", "Secret V-Ore", "GP Crack Spawn",
    "GG Biwahigai", "FA Baby Raigyo", "GLXS Spawn Cherry", "SK (Sexy Killer)",
    "GP Kikyou", "Small Mouth Bass", "Macha Head", "Golden Brownie",
    "Ito Illusion", "Rising Sun", "M Endmax", "Northern Secret",
    "Crack Sand", "Hiuo", "IL Mirage", "Blue Back Chart Candy", "IL Red Head"
]

# Fake listings for instant testing (replace with real eBay/Buyee/Mercari later)
FAKE_LISTINGS = [
    {"title": "Megabass Vision 110 FA Ghost Kawamutsu NEW",      "price": 72,  "url": "https://ebay.com/fake1"},
    {"title": "PopMax GP Gerbera sealed",                       "price": 155, "url": "https://ebay.com/fake2"},
    {"title": "Megabass PopX FA Baby Raigyo rare color",        "price": 185, "url": "https://ebay.com/fake3"},
    {"title": "Vision Oneten Jr GLX Rainbow mint",              "price": 110, "url": "https://ebay.com/fake4"},
    {"title": "Random trash lure no one wants",                 "price": 30,  "url": "https://ebay.com/junk"},
]

def scream(title, price, url):
    embed = DiscordEmbed(
        title="WHITE WHALE BREACH",
        description=f"**{title}**",
        color="ff0000",
        timestamp=datetime.utcnow().isoformat()
    )
    embed.add_embed_field(name="Price", value=f"${price}", inline=True)
    embed.add_embed_field(name="Link", value=url, inline=False)
    embed.set_footer(text="RareCast Imports • Move fast or cry later")
    DiscordWebhook(url=WEBHOOK_URL, rate_limit_retry=True).add_embed(embed).execute()

@app.route("/")
def home():
    return "<h1>RareCast White-Whale Alert Live</h1><p><a href='/hunt'>RUN HUNT NOW</a></p>"

@app.route("/hunt")
def hunt():
    hits = 0
    for item in FAKE_LISTINGS:
        if any(unicorn.lower() in item["title"].lower() for unicorn in UNICORNS):
            scream(item["title"], item["price"], item["url"])
            hits += 1

    return jsonify({
        "status": "hunt complete",
        "white_whales_found": hits,
        "time": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, jsonify
from discord_webhook import DiscordWebhook, DiscordEmbed
import os

app = Flask(__name__)

UNICORNS = [
    "HT Ito Tennessee Shad","GP Gerbera","FA Ghost Kawamutsu","GLX Rainbow",
    "Ito Tennessee (SP-C)","GP Pro Blue II","Secret V-Ore","GP Crack Spawn",
    "GG Biwahigai","FA Baby Raigyo","GLXS Spawn Cherry","SK (Sexy Killer)",
    "GP Kikyou","Small Mouth Bass","Macha Head","Golden Brownie",
    "Ito Illusion","Rising Sun","M Endmax","Northern Secret",
    "Crack Sand","Hiuo","IL Mirage","Blue Back Chart Candy","IL Red Head"
]

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

@app.route("/")
def home():
    return '<h1>RareCast Unicorn Hunter</h1><h2><a href="/hunt">RUN HUNT → 4 test alerts</a></h2>'

@app.route("/hunt")
def hunt():
    if not WEBHOOK:
        return "<h2>No Discord webhook set — add DISCORD_WEBHOOK in Render → Environment</h2>"

    sent = 0
    for color in ["FA Ghost Kawamutsu", "GP Gerbera", "FA Baby Raigyo", "GLX Rainbow"]:
        embed = DiscordEmbed(
            title="WHITE WHALE BREACH",
            description=f"Megabass {color} spotted!",
            color="ff0000"
        )
        embed.set_footer(text="RareCast Imports • Live Test")
        try:
            DiscordWebhook(url=WEBHOOK).add_embed(embed).execute()
            sent += 1
        except:
            pass  # never crash
    return f"<h2>{sent} test alerts sent — check Discord!</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

from flask import Flask
from discord_webhook import DiscordWebhook, DiscordEmbed
import os

app = Flask(__name__)

UNICORNS = ["HT Ito Tennessee Shad","GP Gerbera","FA Ghost Kawamutsu","GLX Rainbow","Ito Tennessee (SP-C)","GP Pro Blue II","Secret V-Ore","GP Crack Spawn","GG Biwahigai","FA Baby Raigyo","GLXS Spawn Cherry","SK (Sexy Killer)","GP Kikyou","Small Mouth Bass","Macha Head","Golden Brownie","Ito Illusion","Rising Sun","M Endmax","Northern Secret","Crack Sand","Hiuo","IL Mirage","Blue Back Chart Candy","IL Red Head"]

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

@app.route("/")
def home():
    return '<h1 style="text-align:center;margin-top:100px">RareCast Unicorn Hunter</h1><h2 style="text-align:center"><a href="/hunt" style="color:red;font-size:50px">RUN HUNT → 4 test alerts</a></h2>'

@app.route("/hunt")
def hunt():
    if not WEBHOOK:
        return "<h2>Missing webhook — add DISCORD_WEBHOOK in Render → Environment</h2>"

    sent = 0
    for color in ["FA Ghost Kawamutsu", "GP Gerbera", "FA Baby Raigyo", "GLX Rainbow"]:
        embed = DiscordEmbed(title="WHITE WHALE BREACH", description=f"Megabass {color}", color="ff0000")
        embed.set_footer(text="RareCast Imports • Test successful")
        try:
            DiscordWebhook(url=WEBHOOK).add_embed(embed).execute()
            sent += 1
        except:
            pass
    return f"<h1 style='text-align:center;color:green'>Sent {sent} test alerts — check Discord!</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

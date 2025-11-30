from flask import Flask
from discord_webhook import DiscordWebhook, DiscordEmbed
import os

app = Flask(__name__)

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

@app.route("/")
def home():
    return '<h1 style="text-align:center; margin-top:120px; font-size:60px">RareCast Unicorn Hunter</h1><h2 style="text-align:center"><a href="/test" style="color:#ff0000; font-size:60px">CLICK HERE TO SEND 1 TEST ALERT</a></h2>'

@app.route("/test")
def test():
    if not WEBHOOK:
        return "<h2>Missing webhook — go add DISCORD_WEBHOOK in Render</h2>"
    
    embed = DiscordEmbed(title="TEST SUCCESS", description="If you see this in Discord, we are 100% live", color="00ff00")
    try:
        DiscordWebhook(url=WEBHOOK).add_embed(embed).execute()
        return "<h1 style='color:green; text-align:center'>TEST MESSAGE SENT — CHECK DISCORD</h1>"
    except:
        return "<h1 style='color:red'>Webhook failed — recreate it in Discord</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

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
        return "<h2 style='color:red'>Missing webhook — add DISCORD_WEBHOOK in Render</h2>"
    
    try:
        embed = DiscordEmbed(title="TEST SUCCESS", description="RareCast is live!", color="00ff00")
        response = DiscordWebhook(url=WEBHOOK).add_embed(embed).execute()
        if response.status_code == 204:
            return "<h1 style='color:green; text-align:center'>TEST SENT — CHECK DISCORD!</h1>"
        else:
            return f"<h1 style='color:red'>Bad response: {response.status_code}</h1>"
    except Exception as e:
        return f"<h1 style='color:red'>Error: {str(e)}</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

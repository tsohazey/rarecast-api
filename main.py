from discord_webhook import DiscordWebhook, DiscordEmbed
import os

UNICORNS = ["HT Ito Tennessee Shad","GP Gerbera","FA Ghost Kawamutsu","GLX Rainbow","Ito Tennessee (SP-C)","GP Pro Blue II","Secret V-Ore","GP Crack Spawn","GG Biwahigai","FA Baby Raigyo","GLXS Spawn Cherry","SK (Sexy Killer)","GP Kikyou","Small Mouth Bass","Macha Head","Golden Brownie","Ito Illusion","Rising Sun","M Endmax","Northern Secret","Crack Sand","Hiuo","IL Mirage","Blue Back Chart Candy","IL Red Head"]

webhook_url = os.getenv("DISCORD_WEBHOOK")

if not webhook_url:
    print("Add your Discord webhook in Secrets (lock icon) then Run again")
else:
    for color in ["FA Ghost Kawamutsu", "GP Gerbera", "FA Baby Raigyo", "GLX Rainbow"]:
        embed = DiscordEmbed(title="WHITE WHALE BREACH", description=f"Megabass {color} spotted!", color="ff0000")
        embed.add_embed_field(name="Status", value="TEST ALERT — SYSTEM WORKS", inline=False)
        DiscordWebhook(url=webhook_url).add_embed(embed).execute()
    print("4 test alerts sent — check Discord!")

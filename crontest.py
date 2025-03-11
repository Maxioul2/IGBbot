import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
import json

load_dotenv() # Load the .env file with environment variables like DISCORD_TOKEN

# Create a bot instance setting the intents aka the permissions the bot will have
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance with the command prefix and the intents
# All functions that has the @bot.command() decorator will be considered as commands automatically
bot = commands.Bot(command_prefix="!", intents=intents)
    
# Load the hebdo leaderboard from the file "hebdo_leaderboard.json"
def load_hebdo_leaderboard():
    try:
        f = open("data/hebdo_leaderboard.json",)
        return json.load(f)
    except FileNotFoundError:
        return {}

hebdo_leaderboard_data = load_hebdo_leaderboard()

async def send_leaderboard(ctx):
    data = hebdo_leaderboard_data
    start_day = datetime.datetime.now() - datetime.timedelta(days=7)
    title = f"🏆 **Classement hebdomadaire** ({start_day.strftime('%d/%m/%Y')} - {datetime.datetime.now().strftime('%d/%m/%Y')})"

    if not ctx:
        ctx = bot.get_channel(os.getenv("DISCORD_MAIN_CHANNEL"))

    if not data:
        await ctx.send("Aucune partie de pendu n'a été jouée.")
        return
    
    message = f"{title} :\n\n"

    leaderboard_mots = sorted(data.values(), key=lambda x: (x["words"]["success"] / x["words"]["total"] if x["words"]["total"] > 0 else 0, x["words"]["success"]), reverse=True)

    message += "**🏆 Mots trouvés**\n\n"
    for i, user in enumerate(leaderboard_mots):
        if user["words"]["total"] > 0:
            message += i == 0 and "🥇 " or i == 1 and "🥈 " or i == 2 and "🥉 " or f"{i + 1}e  "
            message += f"**{user['name']} :** {user['words']['success']} / {user['words']['total']} essai(s) - **{user['words']['success'] / user['words']['total']:.0%}**\n"

    message += "\n\n"

    leaderboard_lettres = sorted(data.values(), key=lambda x: (x["letters"]["success"] / x["letters"]["total"] if x["letters"]["total"] > 0 else 0, x["letters"]["success"]), reverse=True)

    message += "**🏆 Lettres trouvées**\n\n"
    for i, user in enumerate(leaderboard_lettres):
        if user["letters"]["total"] > 0:
            message += i == 0 and "🥇 " or i == 1 and "🥈 " or i == 2 and "🥉 " or f"{i + 1}e  "
            message += f"**{user['name']} :** {user['letters']['success']} / {user['letters']['total']} essai(s) - **{user['letters']['success'] / user['letters']['total']:.0%}**\n"

    message += "\n\n"

    leaderboard_started = sorted(data.values(), key=lambda x: x["started"], reverse=True)

    message += "**🏆 Parties lancées**\n\n"
    for i, user in enumerate(leaderboard_started):
        message += i == 0 and "🥇 " or i == 1 and "🥈 " or i == 2 and "🥉 " or f"{i + 1}e  "
        message += f"**{user['name']} :** {user['started']} partie(s)\n"

    message += "\n\n*Le classement vient d'être réinitialisé. A vos pendus !*"

    await ctx.send(message)

async def cronjob():
    channel = await bot.fetch_channel(os.getenv("DISCORD_MAIN_CHANNEL")) # Fetch the channel where the bot will send the leaderboard
    await send_leaderboard(channel) # Send the leaderboard to the channel

    # Reset the leaderboard
    with open("data/hebdo_leaderboard.json", "w") as f:
        json.dump({}, f)

@bot.event
async def on_ready():
    await cronjob()
    await bot.close() # Close the bot

bot.run(os.getenv("DISCORD_TOKEN")) # Run the bot with the token from the .env file
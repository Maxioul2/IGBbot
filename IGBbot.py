import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import requests
from unidecode import unidecode
from bs4 import BeautifulSoup
import random
from datetime import datetime, timezone, timedelta
import json

load_dotenv() # Load the .env file with environment variables like DISCORD_TOKEN

# Create a bot instance setting the intents aka the permissions the bot will have
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance with the command prefix and the intents
# All functions that has the @bot.command() decorator will be considered as commands automatically
bot = commands.Bot(command_prefix="!", intents=intents)

# Debug message to check if the bot is ready
@bot.command()
async def bonjour(ctx):
  await ctx.send(f"Bonjour {ctx.author} !")
  await ctx.send("Je suis prêt à bullshit !")

# Command to generate a funny bullshit sentence from the website https://www.bullshitor.com/
@bot.command()
async def bullshit(ctx):
  bullshit_job = requests.get('https://www.bullshitor.com/bullshit_job.php')
  bullshit_phrase = requests.get('https://www.bullshitor.com/bullshit_phrase.php')
  bullshit_meeting = requests.get('https://www.bullshitor.com/bullshit_meeting.php')
  bullshit_tool = requests.get('https://www.bullshitor.com/bullshit_tool.php')
  master_bullshit = "Le " + bullshit_job.text + "va " + bullshit_phrase.text.lower() + "lors du " + bullshit_meeting.text.lower() + "grâce au " + bullshit_tool.text.lower() + "."
  await ctx.send(master_bullshit)

#TO
@bot.command()
async def TO(ctx):
  await ctx.send("TO y est bo")

# Command to generate a random fact from the website https://www.secouchermoinsbete.fr/
@bot.command()
async def le_savais_tu(ctx):
  url = "https://api.secouchermoinsbete.fr/random"
  session = requests.Session()
  response = session.get(url)
  
  soup = BeautifulSoup(response.text, 'html.parser')
  data = soup.find('div', {'class': 'anecdote-content-wrapper'})
  content = "Est-ce que tu le savais-tu ?\n\n" + data.find('a').text
  content = content.replace("\n                    En savoir plus", "")
  await ctx.send(content)
  await ctx.send("https://tenor.com/view/skeletor-until-we-meet-again-goodbye-gif-7594892226715043729")

# Command to throw a dice with a number of faces given by the user (between 1 and n)
@bot.command()
async def d(ctx, *, dice: str):
    
    if not dice.isdigit() or int(dice) < 1:
        await ctx.send("Le dé doit être un nombre entier positif. Exemple : `!d 6`")
        return
    
    if int(dice) > 99999:
        await ctx.send("Arrête de jouer au plus con. Choisis un dé avec moins de 100 000 faces.")
        return
    
    result = random.randint(1, int(dice))
    await ctx.send(f"🎲 Résultat du dé à {dice} faces : {result}")

@bot.command()
async def dodo(ctx, *, heure_reveil: str = None):
    """Calculer le temps de sommeil en fonction de l'heure de réveil"""

    if not heure_reveil:
        await ctx.send("C'est grâce mat' demain. Fais comme tu veux chef.")
        return
    
    # Temp timezone fix for Paris
    heure_actuelle = datetime.now() + timedelta(hours=1)

    try:
        heure_reveil = heure_actuelle.replace(hour=int(heure_reveil.split(":")[0]), minute=int(heure_reveil.split(":")[1]))

        if heure_reveil < heure_actuelle:
            heure_reveil += timedelta(days=1)
    except ValueError:
        await ctx.send("Format d'heure invalide. Utilisez HH:MM (ex: 07:30)")
        return

    temps_sommeil = heure_reveil - heure_actuelle

    heures_sommeil = temps_sommeil.total_seconds() // 3600
    minutes_sommeil = (temps_sommeil.total_seconds() % 3600) // 60
    await ctx.send(f"{ctx.author.mention}, si tu vas te coucher maintenant, tu auras {str(int(heures_sommeil))} heures et {str(int(minutes_sommeil))} minutes de sommeil.")

    if heures_sommeil >= 6:
        await ctx.send("En vrai t'es large.")
    elif heures_sommeil >= 4:
        await ctx.send("C'est vraiment l'heure de dormir là.")
    else:
        await ctx.send("En vrai c'est trop tard, dors pas.")
        
### PENDU ###

# Get a random word from the file "mots.txt"
def get_random_word():
    lines = open("data/mots.txt").read().splitlines()
    word = random.choice(lines).upper()
    while len(word) < 3:
        word = random.choice(lines).upper()
    return word

# Load the leaderboard from the file "leaderboard.json"
def load_leaderboard():
    try:
        f = open("data/leaderboard.json",)
        return json.load(f)
    except FileNotFoundError:
        return {}
    
def save_leaderboard():
    with open("data/leaderboard.json", "w") as f:
        json.dump(leaderboard_data, f)
    
leaderboard_data = load_leaderboard()

games_pendu = {}  # Dict storing the ongoing games. Key: channel ID, Value: game data

# Command to start a new game of "pendu"
@bot.command()
async def pendu(ctx, *, command: str = None):

    if command == "leaderboard":
        """Afficher le classement du pendu"""
        if not leaderboard_data:
            await ctx.send("Aucune partie de pendu n'a été jouée.")
            return
        
        message = ""

        leaderboard_mots = sorted(leaderboard_data.values(), key=lambda x: x["words"]["success"] / x["words"]["total"] if x["words"]["total"] > 0 else 0, reverse=True)
        #leaderboard_mots = [f"**{user['name']} :** {user['words']['success']} mot(s) trouvé(s) sur {user['words']['total']} tentative(s) - **{user['words']['success'] / user['words']['total']:.0%}**" for user in leaderboard_mots]
        message += "**🏆 Mots trouvés**\n\n"
        for i, user in enumerate(leaderboard_mots):
            if user["words"]["total"] > 0:
                message += i == 0 and "🥇 " or i == 1 and "🥈 " or i == 2 and "🥉 " or f"{i + 1}e  "
                message += f"**{user['name']} :** {user['words']['success']} / {user['words']['total']} essai(s) - **{user['words']['success'] / user['words']['total']:.0%}**\n"

        message += "\n\n"

        leaderboard_lettres = sorted(leaderboard_data.values(), key=lambda x: x["letters"]["success"] / x["letters"]["total"] if x["letters"]["total"] > 0 else 0, reverse=True)
        #leaderboard_lettres = [f"**{user['name']} :** {user['letters']['success']} lettre(s) trouvée(s) sur {user['letters']['total']} tentative(s) - **{user['letters']['success'] / user['letters']['total']:.0%}**" for user in leaderboard_lettres]
        message += "**🏆 Lettres trouvées**\n\n"
        for i, user in enumerate(leaderboard_lettres):
            if user["letters"]["total"] > 0:
                message += i == 0 and "🥇 " or i == 1 and "🥈 " or i == 2 and "🥉 " or f"{i + 1}e  "
                message += f"**{user['name']} :** {user['letters']['success']} / {user['letters']['total']} essai(s) - **{user['letters']['success'] / user['letters']['total']:.0%}**\n"

        message += "\n\n"

        leaderboard_started = sorted(leaderboard_data.values(), key=lambda x: x["started"], reverse=True)
        #leaderboard_started = [f"**{user['name']} :** {user['started']} partie(s) commencée(s)" for user in leaderboard_started]
        message += "**🏆 Parties lancées**\n\n"
        for i, user in enumerate(leaderboard_started):
            message += i == 0 and "🥇 " or i == 1 and "🥈 " or i == 2 and "🥉 " or f"{i + 1}e  "
            message += f"**{user['name']} :** {user['started']} partie(s)\n"

        await ctx.send(message)
        return

    """Démarrer une nouvelle partie de pendu"""
    r = requests.get('https://trouve-mot.fr/api/random')
    word = r.json()[0]['name'].upper()

    hidden_word = []
    for char in word:
      if char == '-':
        hidden_word.append("-")
      else:
        hidden_word.append("\_")
    
    games_pendu[ctx.channel.id] = {
        "word": word,
        "hidden": hidden_word,
        "attempts": 6,
        "used_letters": set()
    }

    if str(ctx.author.id) not in leaderboard_data:
        leaderboard_data[str(ctx.author.id)] = {
            "name": ctx.author.name,
            "started": 1,
            "letters": {
                "success": 0,
                "failure": 0,
                "total": 0
            },
            "words": {
                "success": 0,
                "failure": 0,
                "total": 0
            }
        }
    else:
        leaderboard_data[str(ctx.author.id)]["started"] += 1

    save_leaderboard()
    
    await ctx.send(f"🔤 Nouveau jeu de pendu !\nMot à deviner ({str(len(hidden_word))}) : {' '.join(hidden_word)} \nErreurs restantes : 6")

# Alias for the command "lettre"
@bot.command()
async def l(ctx, letter: str):
    await lettre(ctx, letter)

# Command to propose a letter for the "pendu" game
@bot.command()
async def lettre(ctx, letter: str):
    """Proposer une lettre pour le pendu"""
    if ctx.channel.id not in games_pendu:
        await ctx.send("Aucune partie en cours. Tapez `!pendu` pour commencer.")
        return
    
    game = games_pendu[ctx.channel.id]
    
    if len(letter) != 1 or not letter.isalpha():
        await ctx.send("Merci d'entrer une seule lettre.")
        return
    
    letter = letter.upper()
    
    if letter in game["used_letters"]:
        await ctx.send(f"⚠️ La lettre {letter} a déjà été utilisée.")
        return
    
    game["used_letters"].add(letter)

    if unidecode(letter) in unidecode(game["word"]):
        for i, char in enumerate(game["word"]):
            if unidecode(char) == unidecode(letter):
                game["hidden"][i] = char
        if "\_" not in game["hidden"]:
            await ctx.send(f"🎉 Bravo ! Le mot était **{game['word']}** !")

            leaderboard_data[str(ctx.author.id)]["words"]["success"] += 1
            leaderboard_data[str(ctx.author.id)]["words"]["total"] += 1
            save_leaderboard()

            del games_pendu[ctx.channel.id]
        else:
            await ctx.send(f"✅ Bien joué ! {' '.join(game['hidden'])}")

            leaderboard_data[str(ctx.author.id)]["letters"]["success"] += 1
            leaderboard_data[str(ctx.author.id)]["letters"]["total"] += 1
            save_leaderboard()
    else:
        game["attempts"] -= 1

        if game["attempts"] == 0:
            await ctx.send(f"❌ Perdu ! Le mot était **{game['word']}**...")

            leaderboard_data[str(ctx.author.id)]["words"]["failure"] += 1
            leaderboard_data[str(ctx.author.id)]["words"]["total"] += 1
            save_leaderboard()

            del games_pendu[ctx.channel.id]
        else:
            await ctx.send(f"❌ Mauvais choix ! Erreurs restantes : {game['attempts']}\n{' '.join(game['hidden'])}")

            leaderboard_data[str(ctx.author.id)]["letters"]["failure"] += 1
            leaderboard_data[str(ctx.author.id)]["letters"]["total"] += 1
            save_leaderboard()

# Command to propose a word for the "pendu" game
@bot.command()
async def mot(ctx, *, word: str):
    """Proposer un mot pour le pendu"""
    if ctx.channel.id not in games_pendu:
        await ctx.send("Aucune partie en cours. Tapez `!pendu` pour commencer.")
        return
    
    game = games_pendu[ctx.channel.id]
    
    if unidecode(word.strip().upper()) == unidecode(game["word"].strip().upper()):
        await ctx.send(f"🎉 Bravo ! Le mot était **{game['word']}** !")

        leaderboard_data[str(ctx.author.id)]["words"]["success"] += 1
        leaderboard_data[str(ctx.author.id)]["words"]["total"] += 1
        save_leaderboard()

        del games_pendu[ctx.channel.id]
    else:

        leaderboard_data[str(ctx.author.id)]["words"]["failure"] += 1
        leaderboard_data[str(ctx.author.id)]["words"]["total"] += 1
        save_leaderboard()

        game["attempts"] -= 1
        if game["attempts"] == 0:
            await ctx.send(f"❌ Perdu ! Le mot était **{game['word']}**...")
            del games_pendu[ctx.channel.id]
        else:
            await ctx.send(f"❌ Mauvais choix ! Erreurs restantes : {game['attempts']}\n{' '.join(game['hidden'])}")

### END PENDU ###

### TELEPHONE ARABE ###

game_telephone = {}  # Global dict storing the ongoing game.

# Unique command to manage the "telephone arabe" game
@bot.command()
async def telephone(ctx, *, command: str = None):

    global game_telephone  # Use the global variable

    # Command to create a new game of "telephone arabe"
    if command.startswith("new"):
        """Démarrer une nouvelle partie de téléphone arabe"""

        maxTurn = command.split(" ")[1] if len(command.split(" ")) > 1 else 3
        if not str(maxTurn).isdigit():
            await ctx.send("Le nombre de tours doit être un nombre.")
            return
        maxTurn = int(maxTurn)
        if maxTurn > 10:
            maxTurn = 10
            await ctx.send("Ce sera 10 tours, t'abuses frérot.")

        game_telephone = {
            "phrase": "",
            "players": [],
            "current": None,
            "turn": 0,
            "maxTurn": maxTurn,
            "channel": ctx,
            "started": False
        }
        
        await ctx.send("📞 Nouveau jeu de téléphone arabe !\nTapez `!telephone join` pour participer et `!telephone start` pour commencer.")

    # Join the game
    elif command == "join":
        """Rejoindre une partie de téléphone arabe"""

        if not game_telephone:
            await ctx.send("Aucune partie en cours. Tapez `!telephone new` pour en créer une.")
            return

        if ctx.author in game_telephone["players"]:
            await ctx.send(f"{ctx.author.mention}, vous êtes déjà inscrit.")
            return
        
        if game_telephone["started"]:
            await ctx.send("La partie a déjà commencé.")
            return
        
        game_telephone["players"].append(ctx.author)

        # Send a DM to the player
        await ctx.author.send(f"✅ Vous avez rejoint la partie de téléphone arabe dans {ctx.channel} !")
        
        await ctx.send(f"✅ {ctx.author.mention} a rejoint la partie !")

    # Start the game
    elif command == "start":
        """Démarrer une partie de téléphone arabe"""
        
        if not game_telephone or len(game_telephone["players"]) < 2:
            await game_telephone["channel"].send("Il faut au moins 2 joueurs pour commencer. Tapez `!telephone join` pour participer.")
            return
        
        random.shuffle(game_telephone["players"])
        first_player = game_telephone["players"][0]
        game_telephone["current"] = first_player
        game_telephone["started"] = True

        await first_player.send("📞 Vous commencez la partie de téléphone arabe !\nÉcrivez le début de l'histoire. Le prochain joueur la continuera à partir de vos derniers mots.\nUtilisez `!telephone send votre-histoire`.\n*Vous devez écrire 5 mots au minimum")        
        await game_telephone["channel"].send(f"📞 La partie de téléphone arabe commence avec {first_player.mention}")

    # Send a part of the story (only in DM)
    elif command.startswith("send "):
        """Envoyer un message pour la partie de téléphone arabe depuis les DM"""

        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Envoyez votre message depuis les messages privés.")
            return
        
        if ctx.author not in game_telephone["players"]:
            await ctx.send("Vous ne faites pas partie de la partie de téléphone arabe.")
            return
        
        if ctx.author != game_telephone["current"]:
            await ctx.send("Ce n'est pas votre tour de jouer.")
            return

        # Ajout du message à la phrase
        message_content = command.replace("send ", "")
        if message_content.count(" ") < 4:
            await ctx.send("Vous devez écrire au moins 5 mots.")
            return
        game_telephone["phrase"] += " " + message_content

        # Passage au joueur suivant
        next_index = (game_telephone["players"].index(ctx.author) + 1) % len(game_telephone["players"])

        # Si le dernier joueur a joué, on incrémente le tour
        if next_index == 0:
            game_telephone["turn"] += 1

        game_telephone["current"] = game_telephone["players"][next_index]

        await ctx.send("Histoire prise en compte ! Passge à la personne suivante")

        # Récupération des 3 derniers mots pour les afficher
        end_of_phrase = "..." + " ".join(game_telephone["phrase"].split()[-3:]) + "..."

        if game_telephone["turn"] >= game_telephone["maxTurn"] and next_index == 0:
            await game_telephone["channel"].send(f"📞 Message envoyé ! La partie de téléphone arabe est terminée !")
            await stop_telephone(game_telephone["channel"])
        elif game_telephone["turn"] >= game_telephone["maxTurn"] - 1 and next_index == len(game_telephone["players"]):
            await game_telephone["channel"].send(f"📞 Message envoyé ! C'est au tour de {game_telephone['players'][next_index].mention} de terminer l'histoire.")
            await game_telephone["current"].send(f"📞 C'est à vous de terminer l'histoire à partir de :\n{end_of_phrase}\nUtilisez `!telephone send votre-histoire`.")
        else:
            await game_telephone["channel"].send(f"📞 Message envoyé ! C'est au tour de {game_telephone['players'][next_index].mention} de continuer l'histoire.")
            await game_telephone["current"].send(f"📞 C'est à votre tour dans la partie de téléphone arabe !\nContinuez l'histoire à partir de :\n{end_of_phrase}\nUtilisez `!telephone send votre-histoire`.")

    # Stop the game
    elif command == "stop":
        """Arrêter une partie de téléphone arabe"""
        await stop_telephone(game_telephone["channel"])

# Function to stop the game of "telephone arabe"
async def stop_telephone(ctx):
    global game_telephone

    """Arrêter une partie de téléphone arabe"""
    if not game_telephone:
        await ctx.send("Aucune partie en cours.")
        return
    
    await ctx.send("📞 Fin de la partie de téléphone arabe !")
    await ctx.send(f"Phrase finale : {game_telephone['phrase']}")

    for user in game_telephone["players"]:
        await user.send(f"📞 Fin de la partie de téléphone arabe !\nPhrase finale : {game_telephone['phrase']}")

    game_telephone = {}  # Réinitialisation

### FIN TELEPHONE ARABE ###

token = os.getenv("DISCORD_TOKEN")
bot.run(token)

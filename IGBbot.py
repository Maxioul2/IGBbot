import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import requests
from unidecode import unidecode
from bs4 import BeautifulSoup
import random
from datetime import datetime, timedelta
import json
import re

va = ['va', 'doit', 'aimerait', 'est en train de']
lors = ['lors du', 'pendant le', 'après le', 'après avoir programmé le']
grace=['grâce au', 'avec l\'aide du', 'en utilisant le', 'en sappuyant sur le']

# POKER
from IGBPoker import *


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
  await ctx.send(f"Bonjour {ctx.author} !\nJe suis prêt à bullshit !")

# Command to generate a funny bullshit sentence from the website https://www.bullshitor.com/
@bot.command()
async def bullshit(ctx):
  bullshit_job = requests.get('https://www.bullshitor.com/bullshit_job.php')
  bullshit_phrase = requests.get('https://www.bullshitor.com/bullshit_phrase.php')
  bullshit_meeting = requests.get('https://www.bullshitor.com/bullshit_meeting.php')
  bullshit_tool = requests.get('https://www.bullshitor.com/bullshit_tool.php')
  master_bullshit = "Le " + bullshit_job.text + random.choice(va) +" " + bullshit_phrase.text.lower() + random.choice(lors)+" " + bullshit_meeting.text.lower() + random.choice(grace) +" " + bullshit_tool.text.lower() + "."
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
    
    if int(dice) > 100000:
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
        if len(re.split(r'[:h]', heure_reveil)) != 2:
          raise ValueError("L'utilisateur est idiot")
      
        heure_reveil = heure_actuelle.replace(hour=int(re.split(r'[:h]', heure_reveil)[0]), minute=int(re.split(r'[:h]', heure_reveil)[1]))

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

# Reset the hebdo leaderboard
def reset_hebdo_leaderboard():
    global hebdo_leaderboard_data
    hebdo_leaderboard_data = {}
    save_leaderboards()

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
    
# Load the hebdo leaderboard from the file "hebdo_leaderboard.json"
def load_hebdo_leaderboard():
    try:
        f = open("data/hebdo_leaderboard.json",)
        return json.load(f)
    except FileNotFoundError:
        return {}
    
def leaderboard_letter_attempt(user_id, success: bool):
    if success:
        leaderboard_data[user_id]["letters"]["success"] += 1
        hebdo_leaderboard_data[user_id]["letters"]["success"] += 1
    else:
        leaderboard_data[user_id]["letters"]["failure"] += 1
        hebdo_leaderboard_data[user_id]["letters"]["failure"] += 1
    leaderboard_data[user_id]["letters"]["total"] += 1
    hebdo_leaderboard_data[user_id]["letters"]["total"] += 1

def leaderboard_word_attempt(user_id, success: bool):
    if success:
        leaderboard_data[user_id]["words"]["success"] += 1
        hebdo_leaderboard_data[user_id]["words"]["success"] += 1
    else:
        leaderboard_data[user_id]["words"]["failure"] += 1
        hebdo_leaderboard_data[user_id]["words"]["failure"] += 1
    leaderboard_data[user_id]["words"]["total"] += 1
    hebdo_leaderboard_data[user_id]["words"]["total"] += 1
    
def save_leaderboards():
    with open("data/leaderboard.json", "w") as f:
        json.dump(leaderboard_data, f)
    with open("data/hebdo_leaderboard.json", "w") as f:
        json.dump(hebdo_leaderboard_data, f)

async def send_leaderboard(ctx, type):
    if type == "all_time":
        data = leaderboard_data
        title = "📈 Classement général"
    elif type == "hebdo":
        data = hebdo_leaderboard_data
        title = "📅 Classement de la semaine" \
        "\n\n*Le classement hebdomadaire est remis à zéro tous les mercredis à 12h00*"

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

    await ctx.send(message)
    
leaderboard_data = load_leaderboard()
hebdo_leaderboard_data = load_hebdo_leaderboard()

games_pendu = {}  # Dict storing the ongoing games. Key: channel ID, Value: game data

# Command to start a new game of "pendu"
@bot.command()
async def pendu(ctx, *, command: str = None):

    if command == "all_time_leaderboard":
        """Afficher le classement général du pendu"""
        await send_leaderboard(ctx, "all_time")
        return
    
    if command == "hebdo_leaderboard" or command == "leaderboard":
        """Afficher le classement du pendu"""
        await send_leaderboard(ctx, "hebdo")
        return

    """Démarrer une nouvelle partie de pendu"""
    r = requests.get('https://trouve-mot.fr/api/random')
    if len(r.json()[0]['name']) < 5:
        r = requests.get('https://trouve-mot.fr/api/random')
    word = r.json()[0]['name'].upper()

    hidden_word = []
    for char in word:
      if char == 'Œ':
        hidden_word.append("OE")
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

    initial_stats = {
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

    if str(ctx.author.id) not in hebdo_leaderboard_data:
        hebdo_leaderboard_data[str(ctx.author.id)] = initial_stats
    else:
        hebdo_leaderboard_data[str(ctx.author.id)]["started"] += 1

    if str(ctx.author.id) not in leaderboard_data:
        leaderboard_data[str(ctx.author.id)] = initial_stats
    else:
        leaderboard_data[str(ctx.author.id)]["started"] += 1

    save_leaderboards()
    
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

            leaderboard_word_attempt(str(ctx.author.id), True)
            save_leaderboards()

            del games_pendu[ctx.channel.id]
        else:
            await ctx.send(f"✅ Bien joué ! {' '.join(game['hidden'])}")

            leaderboard_letter_attempt(str(ctx.author.id), True)
            save_leaderboards()
    else:
        game["attempts"] -= 1

        if game["attempts"] == 0:
            await ctx.send(f"❌ Perdu ! Le mot était **{game['word']}**...")

            leaderboard_word_attempt(str(ctx.author.id), False)
            save_leaderboards()

            del games_pendu[ctx.channel.id]
        else:
            await ctx.send(f"❌ Mauvais choix ! Erreurs restantes : {game['attempts']}\n{' '.join(game['hidden'])}")

            leaderboard_letter_attempt(str(ctx.author.id), False)
            save_leaderboards()

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

        # For each letter in the hidden word, we increment the success counter
        for i, char in enumerate(game["hidden"]):
            if char == "\_":
                if game["word"][i] not in game["used_letters"]:
                    game["used_letters"].add(game["word"][i])
                    leaderboard_letter_attempt(str(ctx.author.id), True)

        leaderboard_word_attempt(str(ctx.author.id), True)
        save_leaderboards()

        del games_pendu[ctx.channel.id]
    else:

        # TODO: Reduce all multiple letters to 1 unique letter
        for i, char in enumerate(word):
            if unidecode(char) not in unidecode(game["word"]):
                leaderboard_letter_attempt(str(ctx.author.id), False)
        save_leaderboards()

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

        await first_player.send(":telephone: Vous commencez la partie de téléphone arabe !\nÉcrivez le début de l'histoire. Le prochain joueur la continuera à partir de vos derniers mots.\nUtilisez `!telephone send votre-histoire`.\n*Vous devez écrire 5 mots au minimum")        
        await game_telephone["channel"].send(f":telephone: La partie de téléphone arabe commence avec {first_player.mention}")

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

        await ctx.send("Histoire prise en compte ! Passage à la personne suivante")

        # Récupération des 3 derniers mots pour les afficher
        last_words = game_telephone["phrase"].split()[-3:]

        # Si un des mots fait 2 caractères ou moins, on rajoute le 4ème dernier mot
        if any(len(word) <= 2 for word in last_words):
            last_words = game_telephone["phrase"].split()[-4:]  # On prend les 4 derniers mots

        end_of_phrase = "..." + " ".join(last_words) + "..."

        if game_telephone["turn"] >= game_telephone["maxTurn"] and next_index == 0:
            await game_telephone["channel"].send(f":telephone: Message envoyé ! La partie de téléphone arabe est terminée !")
            await stop_telephone(game_telephone["channel"])
        elif game_telephone["turn"] >= (game_telephone["maxTurn"] - 1) and next_index == (len(game_telephone["players"]) - 1):
            await game_telephone["channel"].send(f":telephone: Message envoyé ! C'est au tour de {game_telephone['players'][next_index].mention} de **terminer** l'histoire.")
            await game_telephone["current"].send(f":telephone: C'est à vous de **terminer** l'histoire à partir de :\n{end_of_phrase}\nUtilisez `!telephone send votre-histoire`.")
        else:
            await game_telephone["channel"].send(f":telephone: Message envoyé ! C'est au tour de {game_telephone['players'][next_index].mention} de continuer l'histoire.")
            await game_telephone["current"].send(f":telephone: C'est à votre tour dans la partie de téléphone arabe !\nContinuez l'histoire à partir de :\n{end_of_phrase}\nUtilisez `!telephone send votre-histoire`.")

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
    
    await ctx.send(f":telephone: Phrase finale : \n\n{game_telephone['phrase']}")

    for user in game_telephone["players"]:
        await user.send(f":telephone: Phrase finale : \n\n{game_telephone['phrase']}")

    game_telephone = {}  # Réinitialisation

### FIN TELEPHONE ARABE ###

@bot.command()
async def shutdown(ctx):
    """Shutdown the bot"""
    await ctx.send("Arrêt du bot...")
    await bot.close()
    exit()

### POKER DEBUT ###

@bot.command()
async def poker(ctx, command: str):
    if command == "new":
        await init(ctx)
    if command == "join":
        await join(ctx)
    if command == "display":
        await display(ctx, False)
    if command == "start":
        await start(ctx)
    if command.startswith("reveal"):
        await init_next_round(ctx, command.split()[1])
    if command == "call":
        await call_or_check_hand(ctx)
    if command.startwith("raise"):
        await raise_hand(ctx, int(command.split()[1]))
    if command == "endgame":
        await end_game(ctx)

token = os.getenv("DISCORD_TOKEN")
bot.run(token)

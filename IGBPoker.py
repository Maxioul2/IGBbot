import random
from model.PlayingCard import PlayingCard
from model.PokerPlayer import PokerPlayer

DEFAULT_STACK = 500

CARDS = [
    PlayingCard('A', '♠️'), PlayingCard('2', '♠️'), PlayingCard('3', '♠️'), PlayingCard('4', '♠️'), PlayingCard('5', '♠️'), PlayingCard('6', '♠️'), PlayingCard('7', '♠️'), PlayingCard('8', '♠️'), PlayingCard('9', '♠️'), PlayingCard('10', '♠️'), PlayingCard('J', '♠️'), PlayingCard('Q', '♠️'), PlayingCard('K', '♠️'),
    PlayingCard('A', '♣️'), PlayingCard('2', '♣️'), PlayingCard('3', '♣️'), PlayingCard('4', '♣️'), PlayingCard('5', '♣️'), PlayingCard('6', '♣️'), PlayingCard('7', '♣️'), PlayingCard('8', '♣️'), PlayingCard('9', '♣️'), PlayingCard('10', '♣️'), PlayingCard('J', '♣️'), PlayingCard('Q', '♣️'), PlayingCard('K', '♣️'),
    PlayingCard('A', '♥️'), PlayingCard('2', '♥️'), PlayingCard('3', '♥️'), PlayingCard('4', '♥️'), PlayingCard('5', '♥️'), PlayingCard('6', '♥️'), PlayingCard('7', '♥️'), PlayingCard('8', '♥️'), PlayingCard('9', '♥️'), PlayingCard('10', '♥️'), PlayingCard('J', '♥️'), PlayingCard('Q', '♥️'), PlayingCard('K', '♥️'),
    PlayingCard('A', '♦️'), PlayingCard('2', '♦️'), PlayingCard('3', '♦️'), PlayingCard('4', '♦️'), PlayingCard('5', '♦️'), PlayingCard('6', '♦️'), PlayingCard('7', '♦️'), PlayingCard('8', '♦️'), PlayingCard('9', '♦️'), PlayingCard('10', '♦️'), PlayingCard('J', '♦️'), PlayingCard('Q', '♦️'), PlayingCard('K', '♦️'),
]

game = {"initialized": False}

# --------------------- PRIVATE METHODS ---------------------
def get_player_line():
    display = ""
    for player in game["players"]:
        display += f"🧑 **{player.ctx.display_name}** : {player.stack} 💰 | "
    return display[:-2]

def get_pot_display():
    display = ""
    for player in game["players"]:
        display += f"\t   **{player.ctx.display_name} :** {player.actual_bet} 💰\n"
    display += f"\t   **Total : ** {game["pot"]} 💰\n"
    return display

def get_last_raise_display():
    return f"\t   **Dernière mise : ** {game["last_raise"]} 💰"

def get_river_display():
    river_display = "\t   **Rivière : **"
    for card in game["river"]:
        river_display += str(card) + " | "
    return river_display[:-3]

def get_players_hand_display():
    display = ""
    for player in game["players"]:
        if not player.is_folded:
            display += f"**{player.ctx.display_name}** : {str(player.hand[0])}, {str(player.hand[1])}\n"
        else:
            display += f"**{player.ctx.display_name}** : couché\n"
    return display[:-1]

def get_player(ctx) -> PokerPlayer:
    if not ctx.name in [player.ctx.name for player in game["players"]]:
        print(f"Player {ctx.display_name} not in the game.")
        return None
    return next((player for player in game["players"] if player.ctx.name == ctx.name), None)

def get_folded_players():
    return [player for player in game["players"] if player.is_folded]

def get_remaining_players():
    return [player for player in game["players"] if not player.is_folded]

def draw_river():
    if len(game["river"]) == 5:
        return
    if len(game["river"]) < 3:
        game["shuffled_cards"].pop()
        for _ in range(3):
            game["river"].append(game["shuffled_cards"].pop())
        return
    game["shuffled_cards"].pop()
    game["river"].append(game["shuffled_cards"].pop())

def reset_actual_bets():
    for player in game["players"]:
        player.actual_bet = 0

def should_draw_river():
    actual_bets_sum = sum([player.actual_bet for player in get_remaining_players()])
    triggering_player = game["players"][(game["players"].index(game["big_blind"]) + 1) % len(game["players"])]
    return actual_bets_sum == len(get_remaining_players() * game["last_raise"]) and game["next_player"] == triggering_player

# ---------------------------------------------------------

# ------------------- DISCORD METHODS ---------------------
async def init(ctx):
    global game

    game = {
        "players": [],
        "shuffled_cards": [],
        "river": [],
        "next_player": None,
        "big_blind": None,
        "small_blind": None,
        "big_blind_amount": 10,
        "small_blind_amount": 5,
        "pot": 0,
        "last_raise": 0,
        "initialized": True,
        "started": False,
        "is_round_finished": False
    }

    game["shuffled_cards"] = CARDS.copy()
    random.shuffle(game["shuffled_cards"])

    await ctx.send("🤵‍♂️ Prêt pour une partie endiablée de Poker ? Tapez `!poker join` pour rejoindre la partie.")

async def join(ctx):
    if not game["initialized"]:
        await ctx.send("Aucune partie de poker n'est en cours !")
        return
    
    if ctx.author in [player.ctx for player in game["players"]]:
        await ctx.send(f"{ctx.author.mention}, tu as déjà rejoins la partie.")
        return
    
    player = PokerPlayer(
        ctx.author,
        [game["shuffled_cards"].pop(), game["shuffled_cards"].pop()],
        False,
        DEFAULT_STACK,
        0
    )

    game["players"].append(player)

    await ctx.send(f"{ctx.author.mention} à rejoint la partie !")
    await ctx.author.send(f"Tu as rejoins la partie de poker ! Voici ta main : {str(player.hand[0])}, {str(player.hand[1])}")

async def start(ctx):
    if len(game["players"]) < 2:
        await ctx.send("Tu vas jouer tout seul gros malin ?")
        return
    
    game["started"] = True
    game["next_player"] = game["players"][2 % len(game["players"])]
    game["small_blind"] = game["players"][0]
    game["big_blind"] = game["players"][1]

    game["pot"] += get_player(game["small_blind"].ctx).take_from_stack(game["small_blind_amount"])
    start_big_blind = get_player(game["big_blind"].ctx).take_from_stack(game["big_blind_amount"])
    game["pot"] += start_big_blind
    game["last_raise"] = start_big_blind

    await display(ctx, False)
    await ctx.send(f"La partie commence, c'est à {game["next_player"].ctx.mention} de jouer")
 
async def fold_hand(ctx):
    if ctx.author != game["next_player"].ctx:
        await ctx.send(f"Non, c'est au tour de {game["next_player"].ctx.mention}")
        return
    
    game["next_player"].is_folded = True
    await ctx.send(f"{game["next_player"].ctx.mention} s'est couché.")

    await set_next_player(ctx, game["next_player"])

async def raise_hand(ctx, amount: int):
    if ctx.author != game["next_player"].ctx:
        await ctx.send(f"Non, c'est au tour de {game["next_player"].ctx.mention}")
        return
    
    if amount < game["big_blind_amount"] or amount <= game["last_raise"]:
        await ctx.send("Tu ne mise pas suffisament pour relancer. Rejoue.")
        return
    
    game["last_raise"] = amount
    player = get_player(ctx.author)
    game["pot"] += player.take_from_stack(amount)
    player.actual_bet = amount

    await set_next_player(ctx, game["next_player"])

async def call_or_check_hand(ctx):
    if ctx.author != game["next_player"].ctx:
        await ctx.send(f"Non, c'est au tour de {game["next_player"].ctx.mention}")
        return
    
    player = get_player(ctx.author)
    game["pot"] += player.take_from_stack(game["last_raise"] - player.actual_bet)
    player.actual_bet += game["last_raise"] - player.actual_bet

    await display(ctx, False)
    await set_next_player(ctx, game["next_player"])

async def set_next_player(ctx, player):
    if len(get_folded_players()) == len(game["players"]) - 1:
        winner = get_remaining_players()[0]
        await ctx.send(f"Bravo à {winner.ctx.mention} ! Tu as gagner ce tour. Veux-tu dévoiler tes cartes ? (`!poker reveal oui` ou `!poker reveal non`)")
        game["is_round_finished"] = True
        print("coucou")
        return
    
    if len(game["river"]) == 5 and should_draw_river():
        await ctx.send("Le tour est terminé.")
        await display(ctx, True)

    if should_draw_river():
        reset_actual_bets()
        draw_river()

    current_player_idx = game["players"].index(player)
    next_player = game["players"][(current_player_idx + 1) % len(game["players"])]
    print(f"le prochain joueur est :{next_player.ctx.name}")

    if next_player.is_folded:
        await ctx.send(f"{next_player.ctx.mention} is folded.")
        await set_next_player(ctx, next_player)
    else:
        game["next_player"] = next_player
        await ctx.send(f"C'est au tour de {next_player.ctx.mention} de jouer.")

async def display(ctx, display_player_hand: bool):
    to_display = [get_player_line(), get_pot_display(), get_last_raise_display()]

    if len(game["river"]) != 0:
        to_display.append(get_river_display())

    if display_player_hand:
        to_display.append(get_players_hand_display())

    await ctx.send("\n".join(to_display))

async def init_next_round(ctx, reveal):
    if not game["is_round_finished"]:
        return
    
    if reveal != None or reveal != "oui" or reveal != "non":
        await ctx.send("Réponse invalide.")
        return
    
    winner = get_remaining_players()[0]
    await ctx.send(f"Bravo {winner.ctx.mention} ! Tu as gagné ce tour.")
    if ("oui" == reveal):
        await ctx.send(f"Les cartes de {winner.ctx.mention} étaient : {str(winner.hand[0])}, {str(winner.hand[1])}")

    game["is_round_finished"] = False
    game["shuffled_cards"] = CARDS.copy()
    random.shuffle(game["shuffled_cards"])
    game["river"] = []
    game["small_blind"] = game["players"][(game["players"].index(game["small_blind"]) + 1) % len(game["players"])]
    game["big_blind"] = game["players"][(game["players"].index(game["big_blind"]) + 1) % len(game["players"])]
    game["next_player"] = game["small_blind"]
    
    for player in game["players"]:
        player.hand = [game["shuffled_cards"].pop(), game["shuffled_cards"].pop()]
        ctx.send(f"voici tes cartes pour le tour suivant : {str(player.hand[0])}, {str(player.hand[1])}")

async def end_game(ctx):
    global game
    game = {"initialized": False}
    await ctx.send("La partie est terminée.")

# ---------------------------------------------------------
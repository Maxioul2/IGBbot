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

def get_player(ctx):
    if not ctx.name in [player.ctx.name for player in game["players"]]:
        print(f"Player {ctx.display_name} not in the game.")
        return None
    return next((player for player in game["players"] if player.ctx.name == ctx.name), None)

def get_folded_players():
    return [player for player in game["players"] if player.is_folded]

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
        "started": False
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
    await ctx.author.send(f"Tu as rejoins la partie de poker ! Voici tas main : {str(player.hand[0])}, {str(player.hand[1])}")

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

    await display(ctx)
    await ctx.send(f"La partie commence, c'est à {game["next_player"].ctx.mention} de jouer")
 
async def fold_hand(ctx):
    if ctx.author != game["next_player"]["ctx"]:
        await ctx.send(f"Non, c'est au tour de {game["next_player"]["ctx"].mention}")
        return
    
    game["next_player"]["is_folded"] = True
    await ctx.send(f"{game["next_player"]["ctx"].mention} s'est couché.")

    set_next_player(game["next_player"])

async def raise_hand(ctx, amount: int):
    if ctx.author != game["next_player"]["ctx"]:
        await ctx.send(f"Non, c'est au tour de {game["next_player"]["ctx"].mention}")
        return
    
    if amount < game["big_blind_amount"] or amount <= game["last_raise"]:
        await ctx.send("Tu ne mise pas suffisament pour relancer. Rejoue.")
        return
    
    game["last_raise"] = amount
    game["pot"] += get_player(ctx).take_from_stack(amount)

    set_next_player(game["next_player"])

async def call_or_check_hand(ctx):
    if ctx.author != game["next_player"]["ctx"]:
        await ctx.send(f"Non, c'est au tour de {game["next_player"]["ctx"].mention}")
        return
    
    game["pot"] += get_player(ctx).take_from_stack(game["last_raise"])

    set_next_player(game["next_player"])

# TODO : gerer le cas ou tout les joueurs sont couché -> veux-tu reveal ?
# TODO : si la riviere est complete, gerer la fin du round -> reveal, définir gagnant, faire tourner les rôles, reset le round
async def set_next_player(ctx, player):
    if len(get_folded_players()) == len(game["players"]) - 1:
        # le winer 
    current_player_idx = game["players"].index(player)

    if current_player_idx == len(game["players"]) - 1:
        reset_actual_bets()
        draw_river()
    
    next_player = game["players"][(current_player_idx + 1) % len(game["players"])]

    if next_player["is_folded"]:
        await ctx.send(f"{next_player["ctx"].mention} is folded.")
        set_next_player(ctx, next_player)
    else:
        game["next_player"] = next_player
        await ctx.send(f"C'est au tour de {next_player["ctx"].mention} de jouer.")

async def display(ctx):
    to_display = [get_player_line(), get_pot_display(), get_last_raise_display()]
    await ctx.send("\n".join(to_display))
import random

DEFAULT_STACK = 500

CARDS = [
    '1♠️', '2♠️', '3♠️', '4♠️', '5♠️', '6♠️', '7♠️', '8♠️', '9♠️', '10♠️', 'J♠️', 'Q♠️', 'K♠️',
    '1♣️', '2♣️', '3♣️', '4♣️', '5♣️', '6♣️', '7♣️', '8♣️', '9♣️', '10♣️', 'J♣️', 'Q♣️', 'K♣️',
    '1♥️', '2♥️', '3♥️', '4♥️', '5♥️', '6♥️', '7♥️', '8♥️', '9♥️', '10♥️', 'J♥️', 'Q♥️', 'K♥️',
    '1♦️', '2♦️', '3♦️', '4♦️', '5♦️', '6♦️', '7♦️', '8♦️', '9♦️', '10♦️', 'J♦️', 'Q♦️', 'K♦️',
]

game = {"initialized": False}

def beautify(card: str):
    return card[0] + "\\" + card[1]

async def init(ctx):
    game = {
        "players": [],
        "shuffled_cards": [],
        "river": [],
        "next_player": None,
        "big_blind": None,
        "small_blind": None,
        "pot": 0,
        "current_raise": 0,
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
    player = {
        "ctx": ctx.author,
        "hand": [game["shuffled_cards"].pop(), game["shuffled_cards"].pop()],
        "is_folded": False,
        "stack": DEFAULT_STACK,
        "actual_bet": 0
    }
    game["players"].append(player)
    await ctx.send(f"{ctx.author.mention} à rejoint la partie !")
    await ctx.author.send(f"Tu as rejoins la partie de poker ! Voici tas main : {beautify(player["hand"][0])}, {beautify(player["hand"][1])}")

async def start(ctx):
    if len(game['players'] < 2):
        await ctx.send("Tu vas jouer tout seul gros malin ?")
        return
    game["started"] = True
    game["next_player"] = game["players"][2 % len(game["players"])]
    game["small_blind"] = game["players"][0]
    game["big_blind"] = game["players"][1]

    await ctx.send(f"La partie commence, c'est à {game["next_player"]["ctx"].mention} de jouer")
 
async def fold_hand(ctx):
    if ctx.author != game["next_player"]["ctx"]:
        await ctx.send(f"Non, c'est au tour de {game["next_player"]["ctx"].mention}")
        return
    game["next_player"]["is_folded"] = True
    await ctx.send(f"{game["next_player"]["ctx"].mention} s'est couché.")

    set_next_player(game["next_player"])

#TODO : si amount < last_raise : vas te faire foutre
#TODO : si amount < big_blind : vas te faire foutre
#TODO : si amount == last_raise : call
async def raise_hand(ctx, amount: int):
    if 
    pass

async def call_hand(ctx):
    pass

async def set_next_player(ctx, player):
    current_player_idx = game["players"].index(player)
    next_player = game["players"][(current_player_idx + 1) % len(game["players"])]
    if next_player["is_folded"]:
        await ctx.send(f"{next_player["ctx"].mention} is folded.")
        set_next_player(next_player)
    game["next_player"] = next_player
    await ctx.send(f"C'est au tour de {next_player["ctx"].mention} de jouer.")
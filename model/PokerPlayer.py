class PokerPlayer:
    def __init__(self, ctx, hand, is_folded, stack, actual_bet):
        self.ctx = ctx
        self.hand = hand
        self.is_folded = is_folded
        self.stack = stack
        self.actual_bet = actual_bet
    
    def take_from_stack(self, amount: int):
        returned_value = amount
        if amount > self.stack:
            returned_value = self.stack
            self.actual_bet = returned_value
            self.stack = 0
            return returned_value
        self.actual_bet = returned_value
        self.stack -= amount
        return returned_value
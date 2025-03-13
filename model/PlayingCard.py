class PlayingCard:
    def __init__(self, value, color):
        self.value = value
        self.color = color
    
    def __str__(self):
        return str(self.value) + "\\" + str(self.color)
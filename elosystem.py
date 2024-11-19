import math

# https://www.desmos.com/calculator/1tgkozjght

class EloSystem:
    def __init__(self, default_elo:int, dom_point:int, k_factor:int, adjust_outcomes:bool = False):
        """creates elo system

        overall graph https://www.desmos.com/calculator/1tgkozjght
        outcome adjustment graph https://www.desmos.com/calculator/lejiph2nsi
        Args:
            dom_point: the elo gap at which the higher rated player has a 90% chance of winning
            k_factor: maximum adjustment per game
            adjust_outcomes: adjusts to make close outcomes more valuable (e.g. 11-10 win acts more like 11-6)

        ADJUST OUTCOMES NOT FULLY IMPLEMENTED YET
        """
        self.default = default_elo
        self.D = dom_point
        self.K = k_factor
        self.adjust = adjust_outcomes

    def calculate_odds(self, elo1:float, elo2:float) -> float:
        """odds of 1 means 100% chance of player 1 winning"""
        odds = 1 / (1 + math.pow(10, (elo2-elo1) / (self.D)))
        return odds
    
    def calculate_outcome(self, s1:int, s2:int) -> float:
        outcome = (s1-s2) / max(s1,s2)
        if self.adjust: #TODO: finish this
            outcome = math.pow(outcome, 1/3)
        return (outcome + 1) / 2
    
    def calculate_elo(self, s1:int, s2:int, elo1:float, elo2:float) -> tuple[float,float]:
        outcome = self.calculate_outcome(s1, s2)
        odds = self.calculate_odds(elo1, elo2)
        adj1 = self.K * (outcome - odds)
        adj2 = self.K * (odds - outcome)

        # print(f"score: {s1} - {s2} ({outcome})")
        # print(f"odds: {odds}")
        # print(f"p1: {elo1} + {(adj1)} = {round(elo1+adj1, 2)}")
        # print(f"p2: {elo2} + {(adj2)} = {round(elo2+adj2, 2)}")

        return (elo1+adj1, elo2+adj2)

# testing
if __name__ == "__main__":
    myElo = EloSystem(250, 50, 5)
    elo1 = 90
    for elo2 in range(100,-1,-10):
        print(f"{elo1} vs {elo2}")
        print(round(myElo.calculate_odds(elo1, elo2), 2))
        print(myElo.calculate_elo(11, 5, elo1, elo2))
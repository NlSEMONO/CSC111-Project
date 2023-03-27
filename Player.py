"""
DeepPoker Project

File for ALL player classes, which represent different playstyles for playing poker
"""
import PokerGame

class Player:
    """
    Abstract class representing a player or a playstyle
    """
    bet_this_round: int
    has_moved: bool

    def __init__(self) -> None:
        self.bet_this_round = 0
        self.has_moved = False

    def make_move(self, game_state: PokerGame) -> tuple[int, int]:
        """
        Makes a move based on the state of the 'board' (game_state) it is given
        """
        raise NotImplementedError

class CheckPlayer(Player):
    """
    Player that checks only checks or folds depending on the current bet
    """
    def make_move(self, game_state: PokerGame) -> tuple[int, int]:
        """
        Always checks if there is no bet, and will fold otherwise

        Will always bet on first turn
        """
        self.has_moved = True
        if game_state.stage == 1 and self.bet_this_round == 0:
            self.bet_this_round = 1
            return (1, 1)
        elif game_state.last_bet > 0:
            return (2, -1)
        else:
            return (0, -1)

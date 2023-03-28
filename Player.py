"""
DeepPoker Project

File for ALL player classes, which represent different playstyles for playing poker
"""
import PokerGame

class Player:
    """
    Abstract class representing a player or a playstyle
        bet_this_round -- how much the player has bet so far in this round.
        balance
        betting_percentage -- change for the player to bet "safely"
        raising_percentage -- chance for the player to raise "safely"
        has_moved
        has_raised
        has_folded
        total_bluffs

        NOTE: GAME TREE HAS NOT BEEN IMPLEMENTED ***
    """
    bet_this_round: int
    balance: float
    betting_percentage: Optional[float] = 25
    raising_percentage: Optional[float] = 25
    has_moved: bool
    has_raised: bool
    has_folded: bool
    total_bluffs: int

    def __init__(self, balance: int) -> None:
        self.bet_this_round = 0
        self.has_moved = False
        self.has_raised = False
        self.has_folded = False
        self.total_bluffs = 0
        self.balance = balance

    def make_move(self, game_state: PokerGame) -> tuple[int, int]:
        """
        Makes a move based on the state of the 'board' (game_state) it is given
        The move number correlates to the type of move the player makes.
        Bet is the bet amount.
        Moves:

        """
        raise NotImplementedError

    def win_probability(self, game_state: PokerGame) -> float:
        """
        Calculates current win probability given the information at hand.
        """
        raise NotImplementedError

    def bet_size(self, game_state: PokerGame) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        """
        raise NotImplementedError

    """
    The following should be hard coded (I think idk)
    I have not added them yet oops
    """
    def move_fold(self) -> None:
        """
        Player folds
        """
        self.has_folded = True

    def move_bet(self, bet: int) -> None:
        """
        Player bets
        """
        self.bet_this_round = bet

    def move_raise(self, betraise: int) -> None:
        """
        Player raises bet
        """
        self.bet_this_round = betraise
        self.has_raised = True

    def move_check(self) -> None:
        """
        Player checks
        """

    def move_call(self, last_bet: int) -> None:
        """
        Player calls
        """
        self.bet_this_round = last_bet


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

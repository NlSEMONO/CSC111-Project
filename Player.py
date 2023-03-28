"""
DeepPoker Project

File for ALL player classes, which represent different playstyles for playing poker
"""
from typing import Optional

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

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        I think the bet size should also be determined by win probability
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


class AggressivePlayer(Player):
    """
    A poker player that plays aggressively based on the given game tree.
    """

    def __init__(self, balance: int) -> None:
        super().__init__(balance)

    def make_move(self, game_state: PokerGame) -> tuple[int, int]:
        """
        Makes a move based on the state of the 'board' (game_state) it is given
        The move number correlates to the type of move the player makes.
        Bet is the bet amount.
        Moves:
        0: Fold
        1: Check
        2: Call
        3: Bet
        4: Raise
        """
        win_prob = self.win_probability(game_state)
        # Determine whether to bet, raise or check
        if not self.has_moved:
            self.has_moved = True
            if win_prob >= 0.8:
                bet_amount = int(self.bet_size(game_state, 0.8))
                self.move_bet(bet_amount)
                return (3, bet_amount)
            elif win_prob >= 0.5:
                bet_amount = int(self.bet_size(game_state, 0.5))
                self.move_bet(bet_amount)
                return (3, bet_amount)
            else:
                self.move_check()
                return (1, 0)
        else:
            last_bet = game_state.last_bet
            if win_prob >= 0.8:
                bet_amount = int(self.bet_size(game_state, 0.8))
                self.move_raise(bet_amount)
                return (4, bet_amount)
            # Checks if the win_prob is greater than or equal to 0.5 AND if
            # the amount of the last bet made in the current round is less than or equal to 10% of
            # the player's balance.
            elif win_prob >= 0.5 and last_bet <= 10 * self.balance / 100:
                bet_amount = int(self.bet_size(game_state, 0.5))
                self.move_raise(bet_amount)
                return (4, bet_amount)
            # More aggressive than the previous branch: only requires a win probability of 50% or higher
            # for the player to make a bet.
            elif win_prob >= 0.5:
                self.move_call(last_bet)
                return (2, last_bet)
            else:
                self.move_fold()
                return (0, 0)

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        """
        # Determine a bet size based on the current balance and win probability
        bet_amount = self.balance * (win_prob_threshold - 0.5) / 0.5
        return bet_amount

    def win_probability(self, game_state: PokerGame) -> float:
        """
        Calculates current win probability given the information at hand.
        Idk how to calculate this rn
        Maybe we could use a Python library? ex. PyPokerEngine and PyPokerGUI
        """


class ConservativePlayer(Player):
    """
    A player that tends to play conservatively and rarely bluffs.
    Only bets/raises if they have a high probability of winning (>= 70%), or a moderately strong hand with a reasonable
     chance of winning (>= 50%). In all other cases, the player will fold.
    """

    def __init__(self, balance: int) -> None:
        super().__init__(balance)

    def make_move(self, game_state: PokerGame) -> tuple[int, int]:
        """
        Makes a move based on the state of the 'board' (game_state) it is given
        The move number correlates to the type of move the player makes.
        Bet is the bet amount.
        Moves:
        0 - Fold
        1 - Bet
        2 - Raise
        3 - Check
        4 - Call
        """
        if not self.has_moved:
            self.has_moved = True
            win_prob = self.win_probability(game_state)
            if win_prob >= 0.7:
                bet_amount = int(self.bet_size(game_state) * 0.5)
                self.move_bet(bet_amount)
                return (1, bet_amount)
            elif win_prob >= 0.5:
                bet_amount = int(self.bet_size(game_state) * 0.25)
                self.move_bet(bet_amount)
                return (1, bet_amount)
        else:
            self.move_fold()
            return (0, 0)

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        """
        # Determine a bet size based on the current balance and win probability
        bet_amount = self.balance * (win_prob_threshold - 0.5) / 0.5
        return bet_amount

    def win_probability(self, game_state: PokerGame) -> float:
        """
        Calculates current win probability given the information at hand.
        Idk how to calculate this rn
        Maybe we could use a Python library? ex. PyPokerEngine and PyPokerGUI
        """

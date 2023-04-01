"""
DeepPoker Project
File for ALL player classes, which represent different playstyles for playing poker
"""
from typing import Optional

from PokerGame import PokerGame, Card
import math

#STATICS FOR MOVE CODES
FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4
ALL_IN_CODE = 5

#STATICS FOR HAND WEIGHTING (play around with these not sure) (not used atm)
LOG_CNST = 10
MOD_LOG = 4.9

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
    balance: int
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

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        """
        Makes a move based on the state of the 'board' (game_state) it is given
        The move number correlates to the type of move the player makes.
        Bet is the bet amount.
        Moves:
        """
        raise NotImplementedError

    def rate_hand(self, hand: list[Card]) -> int:
        """
        Rates how good an initial hand is based on possible poker hands it can make
        Preconditions:
            - player_num == 1 or player_num == 2
        1 - 'button' pair - ie. ace/king and 6 or better (unsuited)/pair/suited face cards/unsuited 10 and eight or better
        2 - non-button pair
        1 - Pair
        2 - Straight flush
        3 - both cards jack or higher or flush/straight draw
        4 - nothing special
        1 - 'button' pair - ie. ace/king and 6 or better (unsuited)/pair/suited face cards/unsuited 10 and eight or better
          - second element of tuple represents type of button hand
        2 - non-button pair
        """
        if hand[0][0] == hand[1][0] or hand[0][0] == 1: # same rank; a pair or ace in hand
            return 1

        if hand[0][1] == hand[1][1]: # same suit
            if hand[1][0] >= 11: # suited royals = button hand
                return 1
        if hand[1][0] == 13 and hand[0][1] >= 6: # unsuited king and six or better
            return 1
        elif hand[1][0] >= 10 and hand[0][0] >= 8:
            return 1

        return 2

    def reset_player(self) -> None:
        """
        Resets the players actions for this round
        """
        self.bet_this_round = 0
        self.has_moved = False
        self.has_raised = False
        self.has_folded = False

    def win_probability(self, game_state: PokerGame, player_num: int) -> float:
        """
        returns the win probability
        """
        if player_num == 1:
            hand = game_state.player1_hand
        else:
            hand = game_state.player2_hand

        my_score = game_state.rank_poker_hand(hand)
        used = game_state.community_cards.union(hand)
        all_opponent_hands = [hand for hand in _generate_card_combos(used, set(), 1) if self.rate_hand(list(hand)) == 1]
        better_hands = 0
        for hand in all_opponent_hands:
            if game_state.determine_winner(my_score, game_state.rank_poker_hand(hand)) == 1:
                better_hands += 1

        return better_hands / len(all_opponent_hands)

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        I think the bet size should also be determined by win probability
        """
        raise NotImplementedError

    def move_fold(self) -> tuple[int, int]:
        """
        Player folds
        """
        self.has_folded = True
        return (FOLD_CODE, -1)

    def move_bet(self, bet: int) -> tuple[int, int]:
        """
        Player bets
        Preconditions:
            - bet <= self.balance and bet > 0
        """
        self.bet_this_round = bet
        self.balance -= bet
        return (BET_CODE, bet)

    def move_raise(self, betraise: int) -> tuple[int, int]:
        """
        Player raises bet
            - betraise <= self.balance and betraise > self.bet_this_round
        """
        self.balance -= (betraise - self.bet_this_round)
        self.bet_this_round = betraise
        self.has_raised = True
        return (RAISE_CODE, betraise)

    def move_check(self) -> tuple[int, int]:
        """
        Player checks
        """
        return (CHECK_CODE, 0)

    def move_call(self, last_bet: int) -> tuple[int, int]:
        """
        Player calls
        """
        pool_contribution = last_bet - self.bet_this_round
        self.balance -= pool_contribution

        self.bet_this_round = last_bet
        return (CALL_CODE, pool_contribution)

    def move_all_in(self) -> tuple[int, int]:
        """
        Player calls
        """
        bet = self.balance
        self.bet_this_round += bet
        self.balance = 0
        return (ALL_IN_CODE, bet)


class CheckPlayer(Player):
    """
    Player that checks only checks or folds depending on the current bet
    """

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        """
        Always checks if there is no bet, and will fold otherwise
        Will always bet on first turn
        """
        self.has_moved = True
        if game_state.stage == 1 and game_state.last_bet != self.bet_this_round:
            return self.move_call(game_state.last_bet)
        else:
            return self.move_check()


class TestingPlayer(Player):
    """
    Player that exists for the sole purpose of testing the effectiveness of other players.
    """

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        """
        Always bets, calls or checks; never folds or raises
        """
        self.has_moved = True
        if game_state.stage == 1 and self.bet_this_round == 0 and game_state.last_bet == 0:
            return self.move_bet(int(0.025 * self.balance))
        elif game_state.last_bet > 0:
            return self.move_call(game_state.last_bet)
        else:
            return self.move_check()


class AggressivePlayer(Player):
    """
    A poker player that plays aggressively based on the given game tree.
    """

    def __init__(self, balance: int) -> None:
        super().__init__(balance)

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
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
        win_prob = self.win_probability(game_state, player_num)
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


class ConservativePlayer(Player):
    """
    A player that tends to play conservatively and rarely bluffs.
    Only bets/raises if they have a high probability of winning (>= 70%), or a moderately strong hand with a reasonable
     chance of winning (>= 50%). In all other cases, the player will fold.
    """

    def __init__(self, balance: int) -> None:
        super().__init__(balance)

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
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
        if not self.has_moved:
            self.has_moved = True
            win_prob = self.win_probability(game_state, player_num)
            if win_prob >= 0.7:
                bet_amount = int(self.bet_size(game_state) * 0.5)
                self.move_bet(bet_amount)
                return (3, bet_amount)
            elif win_prob >= 0.5:
                bet_amount = int(self.bet_size(game_state) * 0.25)
                self.move_bet(bet_amount)
                return (3, bet_amount)
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


class NaivePlayer(Player):
    """
    A player that tends to play conservatively and rarely bluffs.
    Only bets/raises if they have a high probability of winning (>= 70%), or a moderately strong hand with a reasonable
     chance of winning (>= 50%). In all other cases, the player will fold.
    """

    def __init__(self, balance: int) -> None:
        super().__init__(balance)

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
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
        self.has_moved = True
        if game_state.stage == 1:  # different algorithm for pre-flop
            if player_num == 1:
                hand = list(game_state.player1_hand)
            else:
                hand = list(game_state.player2_hand)
            hand.sort()
            how_good = self.rate_hand(hand)
            if how_good == 2 and game_state.last_bet > self.bet_this_round:
                return self.move_fold()
            elif how_good == 2 and game_state.last_bet == self.bet_this_round:
                return self.move_check()
            bet = int(self.bet_size(game_state, 0, how_good))
            if bet > game_state.last_bet:
                return self.move_raise(bet)
            else:
                return self.move_call(game_state.last_bet)

        win_prob = self.win_probability(game_state, player_num)
        bet_amount = int(self.balance) if win_prob >= 0.95 else int(self.bet_size(game_state, win_prob))
        if bet_amount >= self.balance:
            return self.move_all_in()
        if win_prob >= 0.95:  # all in if win is basically guaranteed
            if game_state.last_bet == 0:
                return self.move_bet(bet_amount)
            else:
                return self.move_raise(bet_amount)
        elif win_prob >= 0.5:  # safe betting
            if game_state.last_bet == 0:
                return self.move_bet(bet_amount)
            elif game_state.last_bet > (game_state.pool - game_state.last_bet) * (1 - win_prob):  # their bet exceeds
                # our expectation to win the game
                return self.move_fold()
            else:  # call their 'bluff'
                return self.move_call(game_state.last_bet)
        elif game_state.last_bet == 0:
            return self.move_check()
        else:  # fold if under threat
            return self.move_fold()

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float, hand_quality: int = 0) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        """
        # Determine a bet size based on the current balance and win probability
        if game_state.stage == 1:
            if hand_quality == 1:
                return 0.025 * self.balance
            else:
                return game_state.last_bet

        # typically, you bet proportionally to the pot based on how likely you think you are to win
        bet_amount = min(self.balance, int(game_state.pool * (1 / (1 - win_prob_threshold))))
        return bet_amount


def _generate_card_combos(used_cards: set[Card], cards_so_far: set[Card], level_to_stop: int) -> list[set[Card]]:
    """
    Returns all the possible pairs of cards that have not appeared in used_cards
    """
    all_pairs = []
    for i in range(1, 14):
        for j in range(1, 5):
            if (i, j) not in used_cards:
                if len(cards_so_far) == level_to_stop:
                    added_card = cards_so_far.union({(i, j)})
                    all_pairs.append(added_card)
                else:
                    new_cards_so_far = cards_so_far.union({(i, j)})
                    new_used_cards = used_cards.union(new_cards_so_far)
                    all_pairs.extend(_generate_card_combos(new_used_cards, new_cards_so_far, level_to_stop))

    return all_pairs

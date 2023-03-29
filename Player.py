"""
DeepPoker Project

File for ALL player classes, which represent different playstyles for playing poker
"""
from typing import Optional

import PokerGame

#STATICS FOR MOVE CODES
FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4

#STATICS FOR HAND WEIGHTING (play around with these not sure) (not used atm)
TOP_THREE = 2.1
MIDDLE_THREE = 2.01
BOTTOM = 1.5

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

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        """
        Makes a move based on the state of the 'board' (game_state) it is given
        The move number correlates to the type of move the player makes.
        Bet is the bet amount.
        Moves:

        """
        raise NotImplementedError

    def win_probability(self, game_state: PokerGame, player_num: int) -> float:
        """
        Calculates current win probability given the information at hand.
        """
        # turn stuff to list and then make a clone for computation (hypothetical)
        if player_num == 1:
            hand = list(game_state.player1_hand)
            clone_game_state = PokerGame
            clone_game_state.player1_hand = game_state.player1_hand # for computation
        else:
            hand = list(game_state.player2_hand)
            clone_game_state = PokerGame
            clone_game_state.player1_hand = game_state.player2_hand # for computation
        clone_game_state.player1_hand = game_state.community_cards

        if game_state.stage > 1: # current best hand
            current_best = clone_game_state._rank_poker_hand(clone_game_state.player1_hand)[0]
        total = 0

        #ace config
        if hand[0][0] == 1:
            hand[0][0] += 13
        if hand[1][0] == 1:
            hand[0][0] += 13

        if game_state.stage == 1: #Pre flop
            chance = 0.295
            if hand[0][0] == hand[1][0] and hand[1][0]: #pairs (avg +20%)
                    chance += 0.2
            if hand[0][1] == hand[1][1]: #same suit (avg +3.5%)
                chance += 0.035
            if hand[0][1] == hand[1][1] and (hand[0][0] == hand[1][0] + 1 or hand[0][0] == hand[1][0] - 1):
                #straight flush chance
                chance += 0.07
            if hand[0][0] == hand[1][0] + 1 or hand[0][0] == hand[1][0] - 1: #straight
                chance += 0.02
            maximumat = max(hand[0][0], hand[1][0])
            chance += maximumat * 2
            chance += 5 + (min(hand[0][0], hand[1][0]) - 14)

        elif game_state.stage == 2: #Flop
            flop = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
            total = 0
            for i in range(1, 14): #47*46 iterations)
                for j in range(1, 5):
                    if (i, j) not in clone_game_state.community_cards:
                        clone_game_state.community_cards.add((i, j))
                        for n in range(1, 14):
                            for m in range(1, 5):
                                if (i, j) not in clone_game_state.community_cards:
                                    clone_game_state.community_cards.add((n, m))
                                    rank = clone_game_state._rank_poker_hand(clone_game_state.player1_hand)
                                    flop[rank[0]] += 1
                                    clone_game_state.community_cards.remove((n, m))
                        clone_game_state.community_cards.remove((i, j))

            for i in flop:
                if i >= current_best: #improve hand only (rank wise)
                    total += weight_hand(i) * (1/2162) * flop[i]

            total =
            return total
        elif game_state.stage == 3: #Turn
            flop = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
            total = 0
            for i in range(1, 14):
                for j in range(1, 5):
                    if (i, j) not in clone_game_state.community_cards:
                        clone_game_state.community_cards.add((i, j))
                        rank = clone_game_state._rank_poker_hand(clone_game_state.player1_hand)
                        flop[rank[0]] += 1
                        clone_game_state.community_cards.remove((i, j))

            for i in flop:
                total += weight_hand(i) * (1/46) * flop[i]

            total = total/46
            return total
        else: #River
            rank = game_state._rank_poker_hand(clone_game_state.player1_hand)

    def weight_hand(self, rank: int) -> float:
        if rank == 1:
            return 1
        elif rank == 2:
            return 0.997
        elif rank == 3:
            return 0.982
        elif rank == 4:
            return 0.97
        elif rank == 5:
            return 0.94
        elif rank == 6:
            return 0.89
        elif rank == 7:
            return 0.85
        elif rank == 8:
            return 0.62
        elif rank == 9:
            return 0.17
        else:
            return 0.01


    def bet_size(self, game_state: PokerGame, win_prob_threshold: float) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        I think the bet size should also be determined by win probability
        """
        raise NotImplementedError

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

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
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
            win_prob = self.win_probability(game_state)
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

    def win_probability(self, game_state: PokerGame) -> float:
        """
        Calculates current win probability given the information at hand.
        Idk how to calculate this rn
        Maybe we could use a Python library? ex. PyPokerEngine and PyPokerGUI
        """


class SmartPlayer(Player):
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
        0: Fold
        1: Check
        2: Call
        3: Bet
        4: Raise
        """

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

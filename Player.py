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

    def rate_hand(self, game_state: PokerGame, player_num: int) -> int:
        """
        Rates how good an initial hand is based on possible poker hands it can make

        Preconditions:
            - player_num == 1 or player_num == 2

        1 - Pair
        2 - Straight flush
        3 - both cards jack or higher or flush/straight draw
        4 - nothing special
        """
        if player_num == 1:
            hand = list(game_state.player1_hand)
        else:
            hand = list(game_state.player2_hand)

        if hand[0][0] == 1:
            hand.append((14, hand[0][1]))
        if hand[1][0] == 1:
            hand.append((14, hand[1][1]))

        straight_chance, sorted_hand = False, sorted(hand)
        if hand[0][0] != hand[1][0] and (any(sorted_hand[0][0] + 1 == card[0] for card in sorted_hand[1:]) or any(
                sorted_hand[-1][0] - 1 == card[0] for card in sorted_hand[:-1])):
            straight_chance = True

        if hand[0][0] == hand[1][0]:  # pair
            return 1
        if hand[0][1] == hand[1][1] and straight_chance:  # straight + flush
            return 2
        if hand[0][1] == hand[1][1] or straight_chance or (sorted_hand[-1][0] > 10 or sorted_hand[-2][0] > 10):
            # highest 2 cards are jack or better or flush or straight
            return 3
        else:  # nothing special
            return 4

    def win_probability(self, game_state: PokerGame, player_num: int) -> float:
        """
        Calculates current win probability given the information at hand.
        Note: Nested loops run maximum of approx 2.6k iterations. These are only used for generating simulations, so
        should not effect overall run of main code.
        Preconditions:
            - player_num == 1 or player_num == 2
        """
        # turn stuff to list and then make a clone for computation (hypothetical)
        if player_num == 1:
            hand = list(game_state.player1_hand)
            clone_game_state = PokerGame()
            clone_game_state.player1_hand = game_state.player1_hand # for computation
        else:
            hand = list(game_state.player2_hand)
            clone_game_state = PokerGame()
            clone_game_state.player1_hand = game_state.player2_hand # for computation
        clone_game_state.community_cards = game_state.community_cards

        total = 0

        if game_state.stage == 1: #Pre flop
            chance = 0.295
            # ace config
            if hand[0][0] == 1:
                hand.append((14, hand[0][1]))
            if hand[1][0] == 1:
                hand.append((14, hand[1][1]))

            straight_chance, sorted_hand = False, sorted(hand)
            if hand[0][0] != hand[1][0] and (any(sorted_hand[0][0] + 1 == card[0] for card in sorted_hand[1:]) or any(sorted_hand[-1][0] - 1 == card[0] for card in sorted_hand[:-1])):
                straight_chance = True

            if hand[0][0] == hand[1][0]: #pairs (avg +20%)
                    chance += 0.2
            if hand[0][1] == hand[1][1]: #same suit (avg +3.5%)
                chance += 0.035
            if hand[0][1] == hand[1][1] and straight_chance:
                #straight flush chance
                chance += 0.07
            if straight_chance: #straight
                chance += 0.02
            maximumat = max(hand[0][0], hand[1][0])
            chance += (maximumat * 2)/100
            chance += (5 + (min(hand[0][0], hand[1][0]) - 14))/100
            return chance
        elif game_state.stage == 2: #Flop
            flop = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
            total = 0
            same = 0
            current_best = game_state.rank_poker_hand(clone_game_state.player1_hand)
            for i in range(1, 14): #47*46 iterations)
                for j in range(1, 5):
                    if (i, j) not in clone_game_state.community_cards and (i, j) not in clone_game_state.player1_hand:
                        clone_game_state.community_cards.add((i, j))
                        for n in range(1, 14):
                            for m in range(1, 5):
                                if (n, m) not in clone_game_state.community_cards and (n, m) not in clone_game_state.player1_hand:
                                    clone_game_state.community_cards.add((n, m))
                                    rank = clone_game_state.rank_poker_hand(clone_game_state.player1_hand)
                                    rank_beat = clone_game_state.rank_poker_hand(set())
                                    if rank != rank_beat and rank != current_best: # if it is better than the community cards
                                        flop[rank[0]] += 1
                                    else:
                                        same += 0
                                    clone_game_state.community_cards.remove((n, m))
                        clone_game_state.community_cards.remove((i, j))
            same = same * self.weight_hand(current_best[0])
            total += same
            for i in flop:
                total += flop[i] * self.weight_hand(i)

            return min((total/2620), 1)
        elif game_state.stage == 3: #Turn
            flop = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
            total = 0
            same = 0
            current_best = game_state.rank_poker_hand(clone_game_state.player1_hand)
            for i in range(1, 14):
                for j in range(1, 5):
                    if (i, j) not in clone_game_state.community_cards and (i, j) not in clone_game_state.player1_hand:
                        clone_game_state.community_cards.add((i, j))
                        rank = clone_game_state.rank_poker_hand(clone_game_state.player1_hand)
                        rank_beat = clone_game_state.rank_poker_hand(set())
                        if rank != rank_beat and rank != current_best: # if it is better than the community cards
                            flop[rank[0]] += 1
                        else:
                            same += 0
                        flop[rank[0]] += 1
                        clone_game_state.community_cards.remove((i, j))
            same = same * self.weight_hand(current_best[0])
            total += same
            for i in flop:
                total += flop[i] * self.weight_hand(i)
            return min((total/47), 1)
        else: #River
            rank = clone_game_state.rank_poker_hand(clone_game_state.player1_hand)
            rank_beat = clone_game_state.rank_poker_hand(set())
            temp_player = set()
            beat = 0
            if rank == rank_beat: # no improvements
                return 0
            else:
                for i in range(1, 14):  # 45*44 iterations -- checks every possible hand opponent can have and see if we can beat it
                    for j in range(1, 5):
                        if (i, j) not in game_state.community_cards and (i, j) not in clone_game_state.player1_hand:
                            temp_player.add((i, j))
                            for n in range(1, 14):
                                for m in range(1, 5):
                                    if (n, m) not in game_state.community_cards and (n, m) not in clone_game_state.player1_hand and (n, m) not in temp_player:
                                        temp_player.add((n, m))
                                        rank_temp = game_state.rank_poker_hand(temp_player)
                                        if game_state.determine_winner(rank, rank_temp) == 1:
                                            beat += 1
                                        temp_player.remove((n, m))
                            temp_player.remove((i, j))
                return min(beat/(45*44), 1)

    def weight_hand(self, rank: int) -> float:
        """
        Weights hand relative to how possible it is to get a given hand in relation to chance to win.
        Not exactly accurate (esp at the bottom -- pairs) However in terms of pairs it will default to the last
        part of the if statement.
        Preconditions:
            - rank >= 1 and rank <= 10
        """
        if rank == 1: #approx hand weighting -- naive
            return 1
        else:
            mod = 11 - rank
            if rank <= 6:
                return 2*(math.log(mod) + 0.1) / MOD_LOG
            else:
                return 2*(math.log(mod) + 0.1) / MOD_LOG*1.5

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
        return (BET_CODE, bet)

    def move_raise(self, betraise: int) -> tuple[int, int]:
        """
        Player raises bet
            - betraise <= self.balance and betraise > self.bet_this_round
        """
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
        self.bet_this_round = last_bet
        return (CALL_CODE, last_bet)


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
        if game_state.stage == 1 and self.bet_this_round == 0 and game_state.last_bet == 0:
            return self.move_bet(1)
        elif game_state.stage == 1 and self.bet_this_round == 0:
            return self.move_call(game_state.last_bet)
        elif game_state.last_bet > 0:
            return self.move_fold()
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
            return self.move_bet(2)
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
        if game_state.stage == 1:
            self.has_moved = True
            how_good = self.rate_hand(game_state, player_num)
            bet = int(self.bet_size(game_state, 0, how_good))
            if self.has_raised or bet == game_state.last_bet:
                return self.move_check()
            return self.move_bet(bet) if game_state.last_bet == 0 else self.move_raise(bet)

        win_prob = self.win_probability(game_state, player_num)
        if not self.has_moved:
            self.has_moved = True
            if win_prob >= 0.92:
                bet_amount = int(self.bet_size(game_state, win_prob) * 0.75)
                if game_state.last_bet == 0:
                    self.move_bet(bet_amount)
                    return (3, bet_amount)
                elif game_state.last_bet >= bet_amount:
                    self.move_call(game_state.last_bet)
                    return (2, game_state.last_bet)
                else:
                    self.has_raised = True
                    return (4, bet_amount)
            elif win_prob >= 0.75:
                bet_amount = int(self.bet_size(game_state, 0.75) * 0.75)
                if game_state.last_bet == 0:
                    self.move_bet(bet_amount)
                elif game_state.last_bet >= bet_amount:
                    self.move_call(game_state.last_bet)
                    return (2, game_state.last_bet)
                else:
                    self.has_raised = True
                    return (4, bet_amount)
                return (3, bet_amount)
            elif win_prob >= 0.5: #safe betting
                bet_amount = int(self.bet_size(game_state, 0.5) * 0.25)
                if game_state.last_bet == 0:
                    self.move_bet(bet_amount)
                    return (3, bet_amount)
                elif game_state.last_bet >= bet_amount:
                    if game_state.stage == 4:
                        self.move_fold()
                        return (0, 0)
                    self.move_check()
                    return (1, 0)
                else:
                    self.move_call(game_state.last_bet)
                    return (2, game_state.last_bet)
            elif win_prob >= 0.1: #pass
                if game_state.stage == 4:
                    self.move_fold()
                    return (0, 0)
                self.move_check()
                return (1, 0)
            else: #instant fold
                self.move_fold()
                return(0, 0)
        else:
            self.move_fold()
            return (0, 0)

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float, hand_quality: int = 0) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        """
        # Determine a bet size based on the current balance and win probability
        if game_state.stage == 1:
            if hand_quality == 1:
                return 0.8 * self.balance
            elif hand_quality == 2:
                return 0.04 * self.balance
            else:
                return game_state.last_bet

        bet_amount = self.balance * (win_prob_threshold - 0.5) / 0.5
        return bet_amount

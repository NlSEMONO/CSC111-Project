"""
DeepPoker Project

File for class that represents a game (state) of poker
"""
import random
from typing import Optional, Any

# ARE WE COMFORTABLE WITH USING TUPLES FOR HANDS? WE ARE GONNA NEED TO PARSE THE DATA INTO INTEGERS ANYWAYS BECAUSE
# WE NEED TO TURN CARDS INTO ARRAY INDICIES FOR AN IMAGE ARRAY, WHICH IMAGES WILL BE STORED IN.

# card is either a tuple of 2 integers, or is a dataclass with two integers; MoveClasses is temporary
Card = tuple[int, int]
MoveClasses = tuple[int, int]

NUM_TO_RANK = {1: 'Ace', 11: 'Jack', 12: 'Queen', 13: 'King'}
for i in range(2, 11):
    NUM_TO_RANK[i] = str(i)
NUM_TO_SUIT = {1: 'Spades', 2: 'Hearts', 3: 'Clubs', 4: 'Diamonds'}
NUM_TO_POKER_HAND = {1: 'Royal Flush', 2: 'Straight Flush', 3: 'Four of a Kind', 4: 'Full House',
                     5: 'Flush', 6: 'Straight', 7: 'Three of a Kind', 8: 'Two Pair', 9: 'Pair', 10: 'High Card'}


class PokerGame:
    """
    Class representing the 'board'

    Instance attributes:
    - player1_hand: Tuples? representing the cards in player 1's hand
    - player2_hand: Tuples? representing the cards in player 2's hand
    - dealer: integer representing player # closest to the dealer
    - pool: total amount of money/currency in the prize pool
    - last_bet: last amount of money bet
    - community_cards: Tuples? representing the community cards visible to the players
    - stage: integer representing what stage of the game is being represented (although it could be inferred)
    - turn: integer representing player # that has to make a move
    """
    player1_hand: set[Card]
    player2_hand: set[Card]
    player1_moves: list[MoveClasses]
    player2_moves: list[MoveClasses]
    player1_poker_hand: str
    player2_poker_hand: str
    pool: int
    last_bet: int
    community_cards: set[Card]
    stage: int
    turn: int
    winner: Optional[int]

    def __init__(self) -> None:
        self.pool = 0
        self.last_bet = 0
        self.stage = 0
        self.player1_hand = set()
        self.player2_hand = set()
        self.player1_moves = []
        self.player2_moves = []
        self.community_cards = set()
        self.turn = 0
        self.winner = None

    def __str__(self) -> str:
        output_msg = f'Player 1 Hand: {[f"{NUM_TO_RANK[card[0]]} of {NUM_TO_SUIT[card[1]]}" for card in self.player1_hand]} - {self.player1_poker_hand}\n'
        output_msg += f'Player 2 Hand: {[f"{NUM_TO_RANK[card[0]]} of {NUM_TO_SUIT[card[1]]}" for card in self.player2_hand]} - {self.player2_poker_hand}\n'
        output_msg += f'Community Cards: {[f"{NUM_TO_RANK[card[0]]} of {NUM_TO_SUIT[card[1]]}" for card in self.community_cards]}\n'
        return output_msg

    def run_move(self, move: tuple[int, int]) -> None:
        """

        """
        # add appropriate move to move sequence
        if self.turn == 0:
            self.player1_moves.append(move)
        else:
            self.player2_moves.append(move)

        # add raise amount
        if self.last_bet != move[1]:
            self.last_bet += move[1]
        if move[1] > 0:
            self.pool += move[1]

        self.turn = (self.turn + 1) % 2


    def next_stage(self) -> None:
        """
        Moves onto the next stage of a poker game and makes the nessecary adjustments to the 'game state'
        """
        if self.stage == 0:
            for _ in range(2):
                self.player1_hand.add(self._pick_card())
                self.player2_hand.add(self._pick_card())
        elif self.stage == 1:
            for _ in range(3):
                self.community_cards.add(self._pick_card())
        elif 1 < self.stage < 4:
            self.community_cards.add(self._pick_card())
        elif self.stage == 4:
            self.winner = self.check_winner()
        else:
            return

        self.stage += 1

    def _pick_card(self) -> Card:
        """
        Generates a random card that remains in the deck
        """
        card = (random.randint(1, 13), random.randint(1, 4))
        while card in self.community_cards or card in self.player1_hand or card in self.player2_hand:
            card = (random.randint(1, 13), random.randint(1, 4))

        return card

    def check_winner(self, all_in: bool = False) -> Optional[int]:
        """
        Checks who the winner is
        """
        if self.winner is not None:
            return self.winner

        # check for folds
        if len(self.player1_moves) > 0 and self.player1_moves[-1][0] == 2:
            self.winner = 2
            return self.winner
        if len(self.player2_moves) > 0 and self.player2_moves[-1][0] == 2:
            self.winner = 2
            return self.winner

        if all_in:
            while len(self.community_cards) < 5:
                self.community_cards.add(self._pick_card())
            self.stage = 4

        if self.stage == 4:
            p1_score = self._rank_poker_hand(self.player1_hand)
            p2_score = self._rank_poker_hand(self.player2_hand)
            self.player1_poker_hand = NUM_TO_POKER_HAND[p1_score[0]]
            self.player2_poker_hand = NUM_TO_POKER_HAND[p2_score[0]]

            self.winner = self._determine_winner(p1_score, p2_score)
            return self.winner
        else:
            return None

    def _determine_winner(self, p1_score: Any, p2_score: Any) -> int:
        if p1_score[0] == p2_score[0]:
            if p1_score[0] == 2:
                return 1 if p1_score[1] > p2_score[1] else 2 # tiebreaker for straight flush is the higher card
            elif p1_score[0] == 3:
                self._check_kickers(p1_score[2], p2_score[2], 1, p2_score[1]) # same 4 of a kind required if it got to this point
            elif p1_score[0] == 4:
                if max(p1_score[1]) == max(p2_score[1]) and max(p1_score[2]) == max(p2_score[2]):
                    return 3
                elif max(p1_score[1]) == max(p2_score[1]):
                    return 1 if max(p1_score[2]) > max(p2_score[2]) else 2
                return 1 if max(p1_score[1]) > max(p2_score[1]) else 2
            elif p1_score[0] == 5:
                return self._check_kickers(p1_score[1], p2_score[1], 5, []) # the _check_flush function already confines the search to only cards of the same suit
            elif p1_score[0] == 6:
                return 1 if p1_score[1] > p2_score[1] else 2
            elif p1_score[0] == 7:
                if p1_score[1] == p2_score[1]:
                    return self._check_kickers(p1_score[2], p2_score[2], 2, p2_score[1]) # required that they have same triple if it got to this point
                else:
                    return 1 if p1_score[1] > p2_score[1] else 2
            elif p1_score[0] == 8:
                if p1_score[1][0] == p2_score[1][0] and p1_score[1][1] == p2_score[1][1]:
                    return self._check_kickers(p1_score[2], p2_score[2], 1, p2_score[1]) # required that they have same two pair if it got to this point
                elif p1_score[1][0] == p2_score[1][0]:
                    return 1 if p1_score[1][1] > p2_score[1][1] else 2
                else:
                    return 1 if p1_score[1][0] > p2_score[1][0] else 2
            elif p1_score[0] == 9:
                if p1_score[1] == p2_score[1]:
                    return self._check_kickers(p1_score[2], p2_score[2], 3, p2_score[1]) # required that they have same pair if it got to this point
                else:
                    return 1 if p1_score[1] > p2_score[1] else 2
            else:
                return self._check_kickers(p1_score[1], p2_score[1], 5, [])

        return 1 if p1_score[0] < p2_score[0] else 2

    def _check_kickers(self, p1_cards: list[Card], p2_cards: list[Card], kickers_allowed: int,
                       blackist: list[int]) -> int:
        i = 0
        buffer = 0
        while i < kickers_allowed and p1_cards[i + buffer][0] == p2_cards[i + buffer][0]:
            if p1_cards[i + buffer][0] in blackist:
                buffer += 1
            else:
                i += 1
        if i == kickers_allowed:
            return 3  # tie; split the pot
        else:
            return 1 if p1_cards[i][0] > p2_cards[i][0] else 2

    def _rank_poker_hand(self, hand: set[Card]) -> tuple[Any, ...]:
        """
        Returns how 'strong' a poker hand is (lower first number means stronger, higher second number means better tie-
        breaker score)
        """
        all_cards = sorted(list(hand.union(self.community_cards)))
        straight_flush = self._check_straight_flush(all_cards)
        is_flush = self._check_flush(all_cards)
        is_straight = self._check_straight(all_cards)
        rank_counts = self._count_ranks(all_cards)
        reversed_cards = all_cards.copy()
        reversed_cards.reverse()

        if self._check_ryl_flush(all_cards):
            return (1, -1) # not possible for two players to have royal flush; ignore tie
        elif straight_flush[0]:
            return (2, straight_flush[1]) # need to find highest part of the straight flush
        elif len(rank_counts[4]) > 0:
            return (3, rank_counts[4], reversed_cards) # need all cards to determine who has better kicker
        elif len(rank_counts[3]) > 0 and len(rank_counts[2]) > 0:
            return (4, rank_counts[3], rank_counts[2]) # return all triples and pairs that can be created
        elif is_flush[0]:
            return (5, is_flush[1])
        elif is_straight[0]:
            return (6, is_straight[1])
        elif len(rank_counts[3]) > 0:
            return (7, rank_counts[3], reversed_cards)
        elif len(rank_counts[2]) > 1:
            return (8, rank_counts[2], reversed_cards)
        elif len(rank_counts[2]) > 0:
            return (9, rank_counts[2], reversed_cards)
        else:
            if reversed_cards[-1][0] == 1:
                reversed_cards.insert(0, (14, reversed_cards[len(reversed_cards) - 1][1])) # make aces the highest
            return (10, reversed_cards)

    # this function is redundant; the straight flush function does the same thing
    def _check_ryl_flush(self, cards: list[Card]) -> bool:
        possible_suits = {card[1] for card in cards if card[0] == 13}
        kings = len(possible_suits)
        counter = 0
        while len(possible_suits) > 0 and counter < 3:
            prev_card = cards[6 - kings - counter + 1]
            curr_card = cards[6 - kings - counter]
            if curr_card[0] == prev_card[0] + 1 and curr_card[1] in possible_suits:
                counter += 1
                possible_suits = {prev_card[1]}
            else:
                return False

        return counter == 3 and (1, list(possible_suits)[0]) in cards # checks for the corresponding ace

    def _check_straight_flush(self, cards: list[Card]) -> tuple[bool, int]:
        suit_counts = {i: [] for i in range(1, 5)}
        for card in cards:
            suit_counts[card[1]].append(card)

        suit = 0
        for i in range(1, 5):
            if len(suit_counts) >= 5:
                suit = i
                break

        return self._check_straight(suit_counts[suit]) if suit != 0 else (False, -1)

    def _check_straight(self, cards: list[Card]) -> tuple[bool, int]:
        temp_cards = cards.copy()
        i = 0
        while cards[i][0] == 1:
            temp_cards.append((14, cards[i][1]))
            i += 1
        counter = 0
        dupes = 0
        counting_from = len(temp_cards) - 4
        while counter < 4 and counting_from > -1:
            if counter + counting_from + dupes + 1 >= 7:
                counter = 0
                counting_from -= 1
                dupes = 0
                continue
            if temp_cards[counting_from + counter + dupes][0] == temp_cards[counting_from + counter + 1][0] + 1:
                counter += 1
            elif temp_cards[counting_from + counter][0] == temp_cards[counting_from + counter + 1][0]:
                dupes += 1
            else:
                counter = 0
                counting_from -= 1
                dupes = 0

        return (counter == 4, temp_cards[counting_from + counter + dupes + 1][0])

    def _check_flush(self, cards: list[Card]) -> tuple[bool, list[Card]]:
        suit_counts = {i: [] for i in range(1, 5)}
        for card in cards:
            suit_counts[card[1]].append(card)

        suit = 0
        for i in range(1, 5):
            if len(suit_counts) >= 5:
                suit = i
                break

        if suit != 0:
            suit_counts[suit].reverse()

        return (True, suit_counts[suit]) if suit != 0 else (False, -1)

    def _count_ranks(self, cards: list[Card]) -> dict[int, list[int]]:
        """
        Returns tuple representing # of doubles, triples, quadrouples respectively
        """
        rank_counts = [0] * 15
        for card in cards:
            rank_counts[card[0]] += 1
            if card[0] == 1: # ace also = 14
                rank_counts[14] += 1
        pattern_counts = {2: [], 3: [], 4: []}
        for i in range(14):
            if rank_counts[i] - 2 >= 0:
                pattern_counts[rank_counts[i]].append(i)
        for i in range(2, 5):
            pattern_counts[i].reverse()
        return pattern_counts

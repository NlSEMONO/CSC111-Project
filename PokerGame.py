"""
DeepPoker Project

This module contains a class representing a game state of poker. This object also contains critical methods that
determine the strength of the best poker hand that can be formed given a list of cards and another
determine what two poker hands are stronger given some information about the poker hands.

This file is Copyright (c) 2023 Francis Madarang, Sungjin Hong, Sean Kwee, Yenah Lee
"""
from __future__ import annotations
import random
from typing import Optional, Any

# Aliases for common types we will be using in the future
Card = tuple[int, int]
Move = tuple[int, int]

# Mappings that map integers to relevant information to make debugging more accessible
NUM_TO_RANK = {1: 'Ace', 11: 'Jack', 12: 'Queen', 13: 'King'}
for b in range(2, 11):
    NUM_TO_RANK[b] = str(b)
NUM_TO_SUIT = {1: 'Spades', 2: 'Hearts', 3: 'Clubs', 4: 'Diamonds'}
NUM_TO_POKER_HAND = {1: 'Royal Flush', 2: 'Straight Flush', 3: 'Four of a Kind', 4: 'Full House',
                     5: 'Flush', 6: 'Straight', 7: 'Three of a Kind', 8: 'Two Pair', 9: 'Pair', 10: 'High Card'}

# Static variables for what specific integers mean in the context of moves
FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4
ALL_IN_CODE = 5


class PokerGame:
    """
    Class representing the game state of a game of Poker (that we are investigating)

    Instance attributes:
    - player1_hand: set of cards (tuple containing two ints representing suit and rank) representing the cards in
      player 1's hand
    - player2_hand: set of cards (tuple containing two ints representing suit and rank) representing the cards in
      player 2's hand
    - player1_moves: list of moves (in order, representing by tuples) that player1 has performed
    - player2_moves: list of moves (in order, representing by tuples) that player2 has performed
    - player1_poker_hand: the best poker hand player 1 can make during showdown
    - player2_poker_hand: the best poker hand player 2 can make during showdown
    - pool: total amount of money/currency in the prize pool
    - last_bet: bet that players have to match
    - community_cards: set of cards (tuple containing two ints representing suit and rank) representing the community
      cards visible to the players
    - stage: integer representing what stage of the game is being represented (although it could be inferred)
    - turn: integer representing player # - 1, who has to make a move
    - winner: Player # who has won the game; 3 if it's a tie

    Representation Invariants:
    - self.player1_poker_hand == '' or self.player1_poker_hand in NUM_TO_POKER_HAND.values()
    - self.player2_poker_hand == '' or self.player2_poker_hand in NUM_TO_POKER_HAND.values()
    - self.pool >= 0
    - self.last_bet >= 0
    - len(self.community_cards) <= 5 and len(self.player1_hand) <= 2 and len(self.player2_hand) <= 2
    - [self.player1_moves[0], self.player2_moves[0], self.player1_moves[1], ...] represents a valid sequence of moves
      in a game of poker.
    - self.stage <= 5
    - self.turn in {0, 1}
    - self.winner in {1, 2, 3, None}
    """
    player1_hand: set[Card]
    player2_hand: set[Card]
    player1_moves: list[Move]
    player2_moves: list[Move]
    player1_poker_hand: str
    player2_poker_hand: str
    pool: int
    last_bet: int
    community_cards: set[Card]
    stage: int
    turn: int
    winner: Optional[int]

    def __init__(self) -> None:
        """
        Initializer for a game state of poker
        """
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
        self.player1_poker_hand = ''
        self.player2_poker_hand = ''

    def __str__(self) -> str:
        """
        Converts critical information in the game to a string (makes debugging more accessible).
        """
        output_msg = f'Player 1 Hand: ' \
                     f'{[f"{NUM_TO_RANK[card[0]]} of {NUM_TO_SUIT[card[1]]}" for card in self.player1_hand]} ' \
                     f'- {self.player1_poker_hand}\n'
        output_msg += f'Player 2 Hand: ' \
                      f'{[f"{NUM_TO_RANK[card[0]]} of {NUM_TO_SUIT[card[1]]}" for card in self.player2_hand]} ' \
                      f'- {self.player2_poker_hand}\n'
        output_msg += f'Community Cards: ' \
                      f'{[f"{NUM_TO_RANK[card[0]]} of {NUM_TO_SUIT[card[1]]}" for card in self.community_cards]}\n'
        return output_msg

    def run_move(self, move: tuple[int, int], add_to_pool: int) -> None:
        """
        Plays a player's move on the board.

        Instance attributes:
        - move: the move code for the move being ran
        - add_to_pool: the amount to add to the pool. negative numbers can be code for other move types.

        """
        # add appropriate move to player who played the move
        if self.turn == 0:
            self.player1_moves.append(move)
        else:
            self.player2_moves.append(move)

        # modify the bet to beat and pool to win accordingly
        if move[0] == RAISE_CODE or move[0] == BET_CODE:
            if add_to_pool != -1:
                self.pool += add_to_pool
                self.last_bet = move[1]
            else:
                self.pool += (move[1] - self.last_bet)
                self.last_bet = move[1]
        elif move[0] == ALL_IN_CODE:
            self.pool += move[1]
            self.last_bet = move[1]
        elif move[0] == CALL_CODE:
            self.pool += move[1]
        # prevent turn from ticking if a player folds
        if move[0] == FOLD_CODE:
            return

        # tick the turn so the next player has to make a move
        self.turn = (self.turn + 1) % 2

    def next_stage(self) -> None:
        """
        Moves onto the next stage of a poker game and makes the nessecary adjustments to the 'game state'
        """
        # don't tick stage if a player has already folded
        if FOLD_CODE in (move[0] for move in self.player1_moves) or \
                FOLD_CODE in (move[0] for move in self.player2_moves):
            return

        if self.stage == 0:  # game not started = deal hands
            for _ in range(2):
                self.player1_hand.add(self._pick_card())
                self.player2_hand.add(self._pick_card())
        elif self.stage == 1:  # game in pre-flop = show first 3 community cards
            for _ in range(3):
                self.community_cards.add(self._pick_card())
        elif 1 < self.stage < 4:  # flop or turn = reveal one more community card
            self.community_cards.add(self._pick_card())
        elif self.stage == 4:  # river = advance to showdown
            self.winner = self.check_winner()
        else:  # prevent stage ticking if this function is called more than 5 times
            return

        self.stage += 1
        self.last_bet = 0

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
        Checks who the winner is and sets the winner instance attribute appropriately

        Instance attributes:
        - all_in: if there has been an all_in
        """
        if self.winner is not None:
            return self.winner

        # check for folds
        if len(self.player1_moves) > 0 and self.player1_moves[-1][0] == FOLD_CODE:
            self.winner = 2
            return self.winner
        if len(self.player2_moves) > 0 and self.player2_moves[-1][0] == FOLD_CODE:
            self.winner = 1
            return self.winner

        # if showdown, add community cards until there are 5
        if all_in:
            while len(self.community_cards) < 5:
                self.community_cards.add(self._pick_card())
            self.stage = 5

        if self.stage == 5:
            p1_score = self.rank_poker_hand(self.player1_hand)
            p2_score = self.rank_poker_hand(self.player2_hand)
            self.player1_poker_hand = NUM_TO_POKER_HAND[p1_score[0]]
            self.player2_poker_hand = NUM_TO_POKER_HAND[p2_score[0]]

            self.winner = self.determine_winner(p1_score, p2_score)
            return self.winner
        else:
            return None

    def determine_winner(self, p1_score: Any, p2_score: Any) -> int:
        """
        Returns who the winner is given strength of poker hands and corresponding tie-breaking mechanisms.

        Instance Attributes:
        - p1_score: the information of the player 1's "score" it is the information needed to determiend the winner,
        - p2_score: same as p1_score but for p2

        Preconditions:
        - p1_score and p2_score both contain the nessecary information to break ties of their 'caliber' of poker hand
          e.g. if p1_score is high card, it would contain its best poker hand (in list format) in descending order
        """
        if p1_score[0] == p2_score[0]:
            if p1_score[0] == 1:
                return 3  # royal flush on board = tie
            if p1_score[0] == 2:
                return 1 if p1_score[1] > p2_score[1] else 2  # tiebreaker for straight flush is the higher card
            elif p1_score[0] == 3:
                self._check_kickers(p1_score[2], p2_score[2], 1,
                                    p2_score[1])  # same 4 of a kind required if it got to this point
            elif p1_score[0] == 4:
                if max(p1_score[1]) == max(p2_score[1]) and max(p1_score[2]) == max(p2_score[2]):
                    return 3
                elif max(p1_score[1]) == max(p2_score[1]):
                    return 1 if max(p1_score[2]) > max(p2_score[2]) else 2
                return 1 if max(p1_score[1]) > max(p2_score[1]) else 2
            elif p1_score[0] == 5:
                return self._check_kickers(p1_score[1], p2_score[1], 5,
                                           [])  # the _check_flush function already confines the search to same suits
            elif p1_score[0] == 6:
                return 1 if p1_score[1] > p2_score[1] else 2
            elif p1_score[0] == 7:
                if p1_score[1] == p2_score[1]:
                    return self._check_kickers(p1_score[2], p2_score[2], 2, p2_score[
                        1])  # required that they have same triple if it got to this point
                else:
                    return 1 if p1_score[1] > p2_score[1] else 2
            elif p1_score[0] == 8:
                if p1_score[1][0] == p2_score[1][0] and p1_score[1][1] == p2_score[1][1]:
                    return self._check_kickers(p1_score[2], p2_score[2], 1, p2_score[
                        1])  # required that they have same two pair if it got to this point
                elif p1_score[1][0] == p2_score[1][0]:
                    return 1 if p1_score[1][1] > p2_score[1][1] else 2
                else:
                    return 1 if p1_score[1][0] > p2_score[1][0] else 2
            elif p1_score[0] == 9:
                if p1_score[1] == p2_score[1]:
                    return self._check_kickers(p1_score[2], p2_score[2], 3,
                                               p2_score[1])  # required that they have same pair if it got to this point
                else:
                    return 1 if p1_score[1] > p2_score[1] else 2
            else:
                return self._check_kickers(p1_score[1], p2_score[1], 5, [])

        return 1 if p1_score[0] < p2_score[0] else 2

    def _check_kickers(self, p1_cards: list[Card], p2_cards: list[Card], kickers_allowed: int,
                       blackist: list[int]) -> int:
        """
        Evaluates if p1_cards or p2_cards are stronger by kickers_allowed kickers. Ignores 'blacklisted' ranks.

        Instance Attributes:
        - p1_cards: the cards in p1's hand
        - p2_cards: same as p1_cards but for p2
        - kickers_allowed:  how many kickers we should consider when evaluating who has better kickers; a kicker is
        cards that function as tie breakers when two competing poker hands are of the same class/caliber
        - blacklist: the ranks that are blacklisted from being checked.

        Preconditions:
        - p1_cards and p2_cards are sorted in descending order (by rank)
        """
        i = 0
        buffer = 0
        # when this while condition breaks, either a tie or win is guaranteed
        while i < kickers_allowed and i + buffer < len(p1_cards) and p1_cards[i + buffer][0] == p2_cards[i + buffer][0]:
            if p1_cards[i + buffer][0] in blackist:
                buffer += 1
            else:
                i += 1
        if i == kickers_allowed:
            return 3  # tie; split the pot
        else:
            return 1 if p1_cards[i][0] > p2_cards[i][0] else 2

    def rank_poker_hand(self, hand: set[Card]) -> tuple[Any, ...]:
        """
        Returns how 'strong' a poker hand is (lower first number means stronger, higher second number means better
        tiebreaker score)

        Instance Attributes:
        - hand: the hand of the player

        Preconditions:
        - hand is a valid set of cards
        """
        all_cards = sorted(list(hand.union(self.community_cards)))
        straight_flush = self._check_straight_flush(all_cards)
        is_flush = self._check_flush(all_cards)
        is_straight = self._check_straight(all_cards)
        rank_counts = self._count_ranks(all_cards)
        reversed_cards = all_cards.copy()
        i = 0
        while i < len(all_cards) and all_cards[i][0] == 1:
            reversed_cards.append((14, all_cards[i][1]))  # add aces to the end of reversed cards
            i += 1
        reversed_cards.reverse()

        if straight_flush[0] and straight_flush[1] == 14:
            return (1, -1)  # not possible for two players to have royal flush; ignore tie
        elif straight_flush[0]:
            return (2, straight_flush[1])  # need to find the highest part of the straight flush
        elif len(rank_counts[4]) > 0:
            return (3, rank_counts[4], reversed_cards)  # need all cards to determine who has better kicker
        elif len(rank_counts[3]) > 0 and len(rank_counts[2]) > 0:
            return (4, rank_counts[3], rank_counts[2])  # return all triples and pairs that can be created
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
            return (10, reversed_cards)

    def _check_straight_flush(self, cards: list[Card]) -> tuple[bool, int]:
        """
        Checks if a straight flush is present inside a list of cards, and if it is, returns the highest card in the
        straight flush.

        Instance Attributes:
        - cards: the cards being checked if there is a straight flush in that combination.

        Preconditions:
        - cards is sorted in ascending order
        """
        suit_counts = {i: [] for i in range(1, 5)}
        for card in cards:
            suit_counts[card[1]].append(card)

        # evaluate for flush first
        suit = 0
        for i in range(1, 5):
            if len(suit_counts[i]) >= 5:
                suit = i
                break

        # pass the cards that satisfy the flush conditions into the straight method
        return self._check_straight(suit_counts[suit]) if suit != 0 else (False, -1)

    def _check_straight(self, cards: list[Card]) -> tuple[bool, int]:
        """
        Checks if a straight is present and returns the highest card in the straight if one is.

        Instance Attributes:
        - cards: the cards being checked if there is a straight in that combination.

        Preconditions:
        - cards is sorted in ascending order
        """
        temp_cards = cards.copy()
        i = 0
        while cards[i][0] == 1:
            temp_cards.append((14, cards[i][1]))
            i += 1
        counter = 0
        dupes = 0
        counting_from = len(temp_cards) - 5
        # check if 4 consecutive cards are each 1 integer away from the next card
        while counter < 4 and counting_from > -1:
            if counter + counting_from + dupes + 1 >= len(temp_cards):
                counter = 0
                counting_from -= 1
                dupes = 0
                continue  # skip all the next steps if the index to look at exceeds the maximum index of the list
            if temp_cards[counting_from + counter + dupes][0] + 1 == temp_cards[counting_from + counter + dupes + 1][0]:
                counter += 1
            elif temp_cards[counting_from + dupes + counter][0] == temp_cards[counting_from + counter + dupes + 1][0]:
                dupes += 1
            else:
                counter = 0
                counting_from -= 1
                dupes = 0

        return (counter == 4, temp_cards[counting_from + counter + dupes][0])

    def _check_flush(self, cards: list[Card]) -> tuple[bool, list[Card]]:
        """
        Checks if a flush is present and returns all the potential cards in the list of input cards that can be used in
        a flush.

        Instance Attributes:
        - cards: the cards being checked if there is a flush in that combination.

        Preconditions:
        - cards is a sorted in ascending order
        """
        suit_counts = {i: [] for i in range(1, 5)}
        for card in cards:
            suit_counts[card[1]].append(card)

        suit = 0
        for i in range(1, 5):
            if len(suit_counts[i]) >= 5:
                suit = i
                break

        if suit != 0:
            suit_counts[suit].reverse()

        return (True, suit_counts[suit]) if suit != 0 else (False, -1)

    def _count_ranks(self, cards: list[Card]) -> dict[int, list[int]]:
        """
        Returns tuple representing # of doubles, triples, quadrouples respectively
        (only counts the highest ranked quadrouple/triple and will downgrade lower tier triples/doubles)

        Instance Attributes:
        - cards: the cards being checked

        Preconditions:
        - cards is sorted in ascending order
        """
        rank_counts = [0] * 15
        for card in cards:
            if card[0] == 1:  # ace also = 14
                rank_counts[14] += 1
            else:
                rank_counts[card[0]] += 1
        pattern_counts = {2: [], 3: [], 4: []}
        for i in range(14, -1, -1):
            if (rank_counts[i] - 2 > 0 and len(pattern_counts[rank_counts[i]]) == 0) or rank_counts[i] == 2:
                pattern_counts[rank_counts[i]].append(i)
            elif rank_counts[i] - 3 >= 0:
                pattern_counts[rank_counts[i] - 1].append(i)

        return pattern_counts

    def get_move_sequence(self) -> list[Move]:
        """
        Returns the sequence of moves played at the current game state
        """
        moves_so_far = []
        for i in range(len(self.player2_moves)):
            moves_so_far.append(self.player1_moves[i])
            moves_so_far.append(self.player2_moves[i])

        if len(self.player1_moves) > len(self.player2_moves):
            moves_so_far.append(self.player1_moves[-1])

        return moves_so_far

    def copy(self) -> PokerGame:
        """
        Returns a new game state object equivalent to the current one.
        """
        copy = PokerGame()
        for i in self.player1_hand:
            copy.player1_hand.add(i)
        for i in self.player2_hand:
            copy.player2_hand.add(i)
        copy.player1_moves.extend(self.player1_moves)
        copy.player2_moves.extend(self.player2_moves)
        copy.player1_poker_hand = self.player1_poker_hand
        copy.player2_poker_hand = self.player2_poker_hand
        copy.pool = self.pool
        copy.last_bet = self.last_bet
        copy.turn = self.turn
        for i in self.community_cards:
            copy.community_cards.add(i)
        copy.stage = self.stage
        copy.winner = self.winner
        return copy


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['__future__', 'random', 'typing'],  # the names (strs) of imported modules
        'allowed-io': [''],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })

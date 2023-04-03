"""
DeepPoker Project

This module contains a class representing a sequence of types of situations/actions that occur in a round of poker.
It is based on the tree ADT.

This file is Copyright (c) 2023 Francis Madarang, Sungjin Hong, Sean Kwee, Yenah Lee
"""
from __future__ import annotations
from typing import Any, Optional
from PokerGame import Card, Move, PokerGame, NUM_TO_POKER_HAND, NUM_TO_RANK
from GameRunner import NUM_TO_ACTION, run_round
from Player import Player, TestingPlayer, NaivePlayer
import copy

# Static variables for what specific integers mean in the context of moves
FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4
ALL_IN_CODE = 5

# constant for determining what is considered an adequate quotient (how many outcomes out of 6)
# to be considered a legitimate threat
THREAT_CONSTANT = 6

burner_player = Player(10)  # player object to access player methods


class GameTree:
    """
    Decision tree for game sequences
    Each root/node represents a class of action; a way of categorizing the situation/board state in which players made
    their decisions and their responses to the situation.

    Instance Attributes:
    - classes_of_actions: the set of classes of actions
    - subtrees: a dictionary** representing the subtrees for recurssive search
    - move_condience_value: the "confidence" of winning of this tree path.
    - good_outcomes_in_route: good outcomes in route.
    - total_games_in_route: the amount of games in the route.

    Represenatation Invariants:
    - not (self.classes_of_action is None) or self.subtrees == {}
    - If the classes of action is an empty set, the tree's current node represents the start of the game, where no moves
    have been played.
    - all(c == self.subtrees[c].classes_of_action for c in self.subtrees)
    - 0.0 <= self.move_confidence_value <= 1.0
    - self.total_games_in_route >= self.good_outcomes_in_route
    """
    classes_of_action: Optional[set[str]]
    subtrees: dict[frozenset[str], GameTree]
    move_confidence_value: float
    good_outcomes_in_route: int
    total_games_in_route: int

    def __init__(self, node_val: Optional[set[str]] = None) -> None:
        """
        Initializer for a sequence of game situations or moves in poker.
        """
        self.classes_of_action = node_val
        self.subtrees = {}
        self.move_confidence_value = 0
        self.total_games_in_route = 0
        self.good_outcomes_in_route = 0

    def insert_moves(self, moves: list[Move], game_states: list[PokerGame], following: int, evaluated: bool = False,
                     move_number: int = 0) -> bool:
        """
        Inserts a sequence of moves into the tree. Will insert the move at move_number into a new subtree or current
        subtree of appropriate height (i.e. if move_number is 0, the move will go into a subtree of height 1, as that is
        the first move played in the game).

        Classes of action are based on the player we are 'following' (i.e. player whose information we share)
        NOTE: Classes of action are just a fancy name for tags that accurately describe the situation or event being
        experienced.

        Parameters:
        - moves: the list of moves
        - game_states: the list of game_states corresponding to said moves.
        - following: the player we are following
        - evaluated: has the move on this round been evaluated
        - move_number: the current move number we are on.

        Preconditions:
        - len(moves) == len(game_states)
        - 0 <= move_number < len(moves)
        - following in {0, 1}
        """
        if move_number == len(moves):  # last move was the last move
            current_state = game_states[-1]
            my_hand = current_state.player1_hand if following == 0 else current_state.player2_hand
            opponent_hand = current_state.player2_hand if following == 0 else current_state.player1_hand
            if current_state.stage == 1 or current_state.community_cards == set():  # only folds can trigger this
                self.total_games_in_route += 1
                my_hand_good = burner_player.rate_hand(list(my_hand))
                opponent_hand_good = burner_player.rate_hand(list(opponent_hand))
                # getting opponent to fold when they have a theoretically better hand is always good
                if opponent_hand_good == 1 and my_hand_good == 2:
                    self.good_outcomes_in_route += 1
                    self._update_confidence_value()
                    return True
            elif current_state.stage == 4:  # only folds can trigger this
                self.total_games_in_route += 1
                p1_score = current_state.rank_poker_hand(my_hand)
                p2_score = current_state.rank_poker_hand(opponent_hand)
                if current_state.determine_winner(p1_score, p2_score) == 2:
                    # folding in a disadvantageous position is generally good and getting an opponent who has an
                    #  advantage to fold is a good outcome as well
                    self.good_outcomes_in_route += 1
                    self._update_confidence_value()
                    return True
            elif current_state.stage == 5:  # only showdowns can trigger this
                self.total_games_in_route += 1
                # won and made decent money
                if current_state.winner == following + 1 and any(move[0] in
                                                                 {RAISE_CODE, CALL_CODE, BET_CODE} for move in moves):
                    self.good_outcomes_in_route += 1
                    self._update_confidence_value()
                    return True
            else:  # only folds can trigger
                self.total_games_in_route += 1
                used_cards = current_state.community_cards.union(my_hand.union(opponent_hand))
                next_comm_cards = self._generate_card_combos(used_cards, set(), 4 - len(current_state.community_cards))
                positive_outcomes = 0
                for next_cards in next_comm_cards:
                    p1_score = current_state.rank_poker_hand(my_hand.union(next_cards))
                    p2_score = current_state.rank_poker_hand(opponent_hand.union(next_cards))
                    if current_state.determine_winner(p1_score, p2_score) == 1:
                        positive_outcomes += 1
                if positive_outcomes < len(next_comm_cards) / 2:
                    # folding in a disadvantageous position is generally good and getting an opponent who has an
                    # advantage to fold is a good outcome as well
                    self.good_outcomes_in_route += 1
                    self._update_confidence_value()
                    return True
            self._update_confidence_value()
            return False
        else:
            current_move = moves[move_number]
            current_state = game_states[move_number]
            classes_of_action = self.get_classes_of_action(current_move, current_state, following, evaluated)
            if not any(any(action in c for c in classes_of_action) for action in list(NUM_TO_ACTION.values())):
                # an evaluation occurs if and only if there were no player actions in the classes of action
                evaluated = True
            immutable_actions = frozenset(classes_of_action)
            # add a new subtree for class of action if it doesn't already exist
            if immutable_actions not in self.subtrees:
                self.add_subtree(immutable_actions)
            if move_number + 1 != len(moves):  # checks to see if the next game_state has changed rounds
                if current_state.stage != game_states[move_number + 1].stage:
                    evaluated = False
            self.total_games_in_route += 1
            # if positive outcome in lower branch
            if self.subtrees[immutable_actions].insert_moves(
                    moves, game_states, following, evaluated,
                    move_number + (1 if any(any(action in c for c in classes_of_action)
                                            for action in list(NUM_TO_ACTION.values())) else 0)):
                self.good_outcomes_in_route += 1
                self._update_confidence_value()
                return True

            self._update_confidence_value()
            return False

    def _update_confidence_value(self) -> None:
        """
        Update the confidence value of the current node (represented by self).
        """
        self.move_confidence_value = self.good_outcomes_in_route / self.total_games_in_route

    def get_classes_of_action(self, move: Move, game_state: PokerGame, following: int, evaluated: bool,
                              evaluate_move: bool = True) -> set[str]:
        """
        Returns 'tags' or what we call 'classes of action' characteristic of the given input board_state and
        corresponding move played.

        Classes of action contain 4 things, if we are following the player whose hand we know (we can't assume we know
        the opponent's hand): the strength of the best possible poker hand the player can make at the moment, strong
        poker hands that the player can threaten if they get 'lucky', and the type of move they played.
        When we are not following the player's whose hand we know, classes of action may only contain two items:
        poker hands that can threaten the player who we are following and the type of move that was played.

        Parameters:
        - move: the move code
        - game_state: the current game and its corresponding state
        - following: the player we are following.
        - evaluated: if the move has been yet evaluated this round. (class of action wise)
        - evaluate_move: if we need to determine the move

        Preconditions:
        - following in {1, 2}
        """
        classes_so_far = set()
        # determine whose hand we can see
        if following == 0:
            player_hand = game_state.player1_hand
        else:
            player_hand = game_state.player2_hand
        #
        if game_state.stage == 1 and (not evaluated):
            hand_to_check = list(player_hand)
            hand_to_check.sort()
            hand_quality = burner_player.rate_hand(hand_to_check)
            if hand_quality == 1:
                classes_so_far.add('BTN Hand')
            else:
                classes_so_far.add('Non BTN Hand')
            return classes_so_far
        if game_state.stage != 1 and not evaluated:
            current_best = game_state.rank_poker_hand(player_hand)
            used_cards = game_state.community_cards.union(player_hand)
            # current best poker hand player can threaten
            if 'High Card' == NUM_TO_POKER_HAND[current_best[0]]:
                best = [card for card in current_best[1] if card not in game_state.community_cards]
                best = best[0] if best != [] else -1
                classes_so_far.add(
                    f'High Card {NUM_TO_RANK[(best[0] - 1) % 13 + 1 ] if isinstance(best, tuple) else "not"} in hand')
            else:
                classes_so_far.add(f'{NUM_TO_POKER_HAND[current_best[0]]} in hand')
            # potential poker hands the player can make in later in the game (if lucky)
            if game_state.stage != 4:
                possible_adds_comm_cards = self._generate_card_combos(used_cards, set(),
                                                                      4 - len(game_state.community_cards))

                hands = [0] * (current_best[0] + 1)
                for next_cards in possible_adds_comm_cards:
                    test_hand = player_hand.union(next_cards)
                    hand_rank = game_state.rank_poker_hand(test_hand)[0]
                    if hand_rank < current_best[0]:
                        hands[hand_rank] += 1
                for i in range(1, len(hands)):
                    hands[i] = hands[i] + hands[i - 1]
                i = 1
                while i < len(hands) and hands[i] <= len(possible_adds_comm_cards) / THREAT_CONSTANT:
                    i += 1
                if i < len(hands):
                    classes_so_far.add(f'{NUM_TO_POKER_HAND[i]} if lucky')
        if game_state.stage != 1 and following != game_state.turn:
            current_best = game_state.rank_poker_hand(player_hand)
            used_cards = game_state.community_cards.union(player_hand)
            class_to_add = self._determine_threats(game_state, used_cards, current_best)
            if class_to_add is not None:
                classes_so_far.add(class_to_add)
        if not evaluated:
            return classes_so_far
        # Add type of move that was played
        if following != game_state.turn or evaluated:  # acts normally for the opponent
            if evaluate_move:
                if move[0] not in {BET_CODE, RAISE_CODE}:
                    classes_so_far.add(f'{NUM_TO_ACTION[move[0]]}')
                else:
                    if game_state.pool >= move[1]:  # bet is about the pot size
                        adjective = 'Conservative'
                    elif game_state.pool * 2 >= move[1]:  # bet is about 2 x the pot size
                        adjective = 'Moderate'
                    elif game_state.pool * 4 >= move[1]:
                        adjective = 'Aggressive'  # bet is otherwise very high
                    else:
                        adjective = 'Very Aggressive'
                    classes_so_far.add(f'{adjective} {NUM_TO_ACTION[move[0]]}')

        return classes_so_far

    def add_subtree(self, classes_of_action: frozenset[str]) -> None:
        """
        Adds a new subtree to the tree's list of subtrees

        Parameters:
        - classes_of_actions: the classes of actions set

        Preconditions:
        - classes_of_action not in self.subtrees
        """
        self.subtrees[classes_of_action] = GameTree(set(classes_of_action))

    def _determine_threats(self, game_state: PokerGame, used_cards: set[Card],
                           current_best: tuple[Any, ...]) -> Optional[str]:
        """
        Determine what kind of poker hand is likely enough to come out for the opponent to be legitimately considered a
        threat.

        Parameters:
        - game_state: current game state
        - used_cards: used cards already
        - current_best: the current best hand

        Preconditions:
        - all(card in used_cards for card in game_state.community_cards)
        - all(card in used_cards for card in game_state.player1_hand) or \
          all(card in used_cards for card in game_state.player2_hand)
        - current_best is an output of rank_poker_hands
        """
        all_hands = self._generate_card_combos(used_cards, set(), 1)
        better_hands = [0] * (current_best[0] + 1)
        for hand in all_hands:  # determine threatening hands the opponent can have
            hand_rank = game_state.rank_poker_hand(hand)
            if hand_rank[0] < current_best[0] or game_state.determine_winner(current_best, hand_rank) == 2:
                better_hands[hand_rank[0]] += 1
        # turn better_hands into a PSA (because we will determine the strongest hand that is a 'threat', where all
        # stronger poker hands are counted towards the 'threat')
        for i in range(1, len(better_hands)):
            better_hands[i] = better_hands[i] + better_hands[i - 1]
        i = 1
        while i < len(better_hands) and better_hands[i] <= len(all_hands) / THREAT_CONSTANT:
            # take the highest poker hand that poses a 'legitimate risk' ie. >=16.7% of the opponent having it or better
            i += 1
        if i < len(better_hands):
            return f'{NUM_TO_POKER_HAND[i]} is threat'
        else:
            return None

    def _generate_card_combos(self, used_cards: set[Card], cards_so_far: set[Card],
                              level_to_stop: int) -> list[set[Card]]:
        """
        Returns all the possible pairs of cards that have not appeared in used_cards

        Parameters:
        - used_cards: the cards that have already been used.
        - cards_so_far: the cards in the combo so far
        - level_to_stop: level of card combo size to stop

        Preconditions:
        - level_to_stop >= 0
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
                        all_pairs.extend(
                            self._generate_card_combos(new_used_cards, new_cards_so_far, level_to_stop))
        return all_pairs

    def insert_row_moves(self, moves: list, current: int = 0) -> None:
        """
        Inserts a row of moves as a down a tree.

        Parameters:
        - moves: the list of moves
        - current: current index

        Preconditions:
        - represents a sequence of nodes to be inserted, delimited by semicolons
        """
        if current == len(moves):
            return
        else:
            curr_stats = moves[current].split(';')
            self.move_confidence_value = float(curr_stats[1])
            self.good_outcomes_in_route = int(curr_stats[2])
            self.total_games_in_route = int(curr_stats[3])
            if current + 1 != len(moves):
                next_subtree = moves[current + 1].split(';')[0][1:-1].split(',')
                for i in range(len(next_subtree)):
                    next_subtree[i] = next_subtree[i].strip()[1:-1]
                frozenset_of_action = frozenset(next_subtree)
                if frozenset_of_action not in self.subtrees:
                    self.add_subtree(frozenset_of_action)
                self.subtrees[frozenset_of_action].insert_row_moves(moves, current + 1)

    def __str__(self) -> str:
        """
        Turns relevant information from a node into a string delimited by semicolons
        """
        str_so_far = f'{self.classes_of_action};{self.move_confidence_value};'
        str_so_far += f'{self.good_outcomes_in_route};{self.total_games_in_route}'
        return str_so_far


if __name__ == '__main__':
    tree = GameTree()
    for _ in range(10):
        result = run_round(TestingPlayer(10000), NaivePlayer(10000), False)
        result[-1].check_winner()
        # print(result[-1])
        move_sequence = result[-1].get_move_sequence()
        # learn from both how p1 could have played and how p2 could have played
        tree.insert_moves(move_sequence, result, 0)
        tree.insert_moves(move_sequence, result, 1)
    tree_copy = copy.copy(tree)
    while len(tree.subtrees) > 0:
        print(tree.classes_of_action)
        subtrees = list(tree.subtrees.keys())
        tree = tree.subtrees[subtrees[0]]
    print(tree.classes_of_action)

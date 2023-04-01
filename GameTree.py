"""
File for game trees: a tree that represents all the collective move sequences played over many simulated poker games
"""
from __future__ import annotations
from typing import Any, Optional
from PokerGame import Card, Move, PokerGame, NUM_TO_POKER_HAND
from GameRunner import NUM_TO_ACTION, run_round
from Player import Player, TestingPlayer
from NaivePlayer import NaivePlayer

FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4

THREAT_CONSTANT = 6

burner_player = Player(10) # player object to access player methods

class GameTree:
    """
    Decision tree for game sequences

    Each root/node represents a class of action; a way of categorizing the situation/board state in which players made
    their decisions and their responses to the situation.

    Represenatation Invariants:
    - not (self.classes_of_action is None) or self.subtrees == {}
    - If the classes of action is an empty set, the tree's current node represents the start of the game, where no moves
    have been played.
    - all(set(c) == self.subtrees[c].classes_of_action for c in self.subtrees)
    """
    classes_of_action: Optional[set[str]]
    subtrees: dict[tuple[str], GameTree]
    move_confidence_value: float

    def __init__(self, node_val: Optional[set[str]] = None) -> None:
        self.classes_of_action = node_val
        self.subtrees = {}

    def insert_moves(self, moves: list[Move], game_states: list[PokerGame], following: int, evaluated: bool = False,
                     move_number: int = 0) -> None:
        """
        Inserts a sequence of moves into the tree. Will insert the move at move_number into a new subtree or current
        subtree of appropriate height (ie. if move_number is 0, the move will go into a subtree of height 1, as that is
        the first move played in the game).

        Classes of action are based on the player we are 'following' (ie. player whose information we share)

        Preconditions:
        - len(moves) == len(game_states)
        - 0 <= move_number < len(moves)
        """
        print('hi 3')
        if move_number == len(moves):
            return
        else:
            current_move = moves[move_number]
            current_state = game_states[move_number]
            if current_state.stage != 1:
                return
            classes_of_action = self.get_classes_of_action(current_move, current_state, following, evaluated)
            if len(classes_of_action) != 2: #the only time the length of classes of action is 2 is for opponent move. Otherwise, it will evaluate
                #evaluation an only happen once per stage, hence the first move is an evaluation
                evaluated = True
            tup_of_action = tuple(classes_of_action)
            if tup_of_action not in self.subtrees:
                self.add_subtree(tup_of_action)
            if move_number + 1 != len(moves):
                if current_state.stage != game_states[move_number + 1].stage: #checks to see if the next game_state has changed rounds
                    evaluated = False

            self.subtrees[tup_of_action].insert_moves(moves, game_states, following, evaluated, move_number + (1 if any(any(action in c for c in classes_of_action) for action in list(NUM_TO_ACTION.values())) else 0))

    def get_classes_of_action(self, move: Move, game_state: PokerGame, following: int, evaluated: bool, evaluate_move: bool = True) -> set[str]:
        """
        Returns 'tags' or what we call 'classes of action' characteristic of the given input board_state and
        corresponding move played.

        Classes of action contain 4 things, if we are following the player whose hand we know (we can't assume we know
        the opponent's hand): the strength of the best possible poker hand the player can make at the moment, strong
        poker hands that the player can threaten if they get 'lucky', and the type of move they played.

        When we are not following the player's whose hand we know, classes of action may only contain two items:
        poker hands that can threaten the player who we are following and the type of move that was played.
        """
        classes_so_far = set()
        if following == 0:
            player_hand = game_state.player1_hand
        else:
            player_hand = game_state.player2_hand
        if game_state.stage == 1 and (not evaluated):
            hand_quality = burner_player.rate_hand(list(player_hand))
            if hand_quality == 1:
                classes_so_far.add('BTN Hand')
            else:
                classes_so_far.add('Non BTN Hand')
            return classes_so_far
        if following == game_state.turn and game_state.stage != 1:
            # current best poker hand player can threaten
            current_best = game_state.rank_poker_hand(player_hand)
            used_cards = game_state.community_cards.union(player_hand)
            if 'High Card' == NUM_TO_POKER_HAND[current_best[0]]:
                classes_so_far.add(f'High Card {current_best[1]} in hand')
            else:
                classes_so_far.add(f'{NUM_TO_POKER_HAND[current_best[0]]} in hand')
            # potential poker hands the player can make in later in the game (if lucky)
            if game_state.stage != 4:
                possible_adds_comm_cards = self._generate_card_combos(used_cards, set(), 1 - len(game_state.community_cards))
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
                    print('hi 2')
                if i < len(hands):
                    classes_so_far.add(f'{NUM_TO_POKER_HAND[i]} if lucky')
        if game_state.stage != 1:
            current_best = game_state.rank_poker_hand(player_hand)
            used_cards = game_state.community_cards.union(player_hand)
            class_to_add = self._determine_threats(game_state, used_cards, current_best)
            if class_to_add is not None:
                classes_so_far.add(class_to_add)
        # Add type of move that was played
        if following != game_state.turn or evaluated: #acts normally for the opponent
            if evaluate_move:
                if move[0] not in {BET_CODE, RAISE_CODE}:
                    classes_so_far.add(f'{NUM_TO_ACTION[move[0]]}')
                else:
                    if game_state.pool <= move[1]:  # bet is about the pot size
                        adjective = 'Conservative'
                    elif game_state.pool * 2 <= move[1]:  # bet is about 2 x the pot size
                        adjective = 'Moderate'
                    else:
                        adjective = 'Aggressive'  # bet is otherwise very high
                    classes_so_far.add(f'{adjective} {NUM_TO_ACTION[move[0]]}')

        return classes_so_far

    def add_subtree(self, classes_of_action: tuple[str]) -> None:
        """
        Adds a new subtree to the tree's list of subtrees
        """
        self.subtrees[classes_of_action] = GameTree(set(classes_of_action))

    def _determine_threats(self, game_state: PokerGame, used_cards: set[Card], current_best: tuple[Any, ...]) -> Optional[str]:
        """
        Determien the most threateing hand the opponent can realistically create.
        """
        all_hands = self._generate_card_combos(used_cards, set(), 1)
        better_hands = [0] * (current_best[0] + 1)
        for hand in all_hands:  # determine threatening hands the opponent can have
            hand_rank = game_state.rank_poker_hand(hand)
            if hand_rank[0] < current_best[0] or game_state.determine_winner(current_best, hand_rank) == 2:
                better_hands[hand_rank[0]] += 1
        for i in range(1, len(better_hands)):
            better_hands[i] = better_hands[i] + better_hands[i - 1]
        i = 1
        while i < len(better_hands) and better_hands[i] <= len(all_hands) / THREAT_CONSTANT:
            # take the highest poker hand that poses a 'legitimate risk' ie. >=16.7% of the opponent having it or better
            i += 1
            print('hi')
        if i < len(better_hands):
            return f'{NUM_TO_POKER_HAND[i]} is threat'
        else:
            return None

    def _generate_card_combos(self, used_cards: set[Card], cards_so_far: set[Card], level_to_stop: int) -> list[
        set[Card]]:
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
                        all_pairs.extend(
                            self._generate_card_combos(new_used_cards, new_cards_so_far, level_to_stop))
        return all_pairs


tree = GameTree()

result = run_round(TestingPlayer(10000), NaivePlayer(10000))
moves = result[-1].get_move_sequence()
for game in result:
    print(game.community_cards)

tree.insert_moves(moves, result, 0)

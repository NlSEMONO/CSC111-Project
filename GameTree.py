"""
File for game trees: a tree that represents all the collective move sequences played over many simulated poker games
"""
from __future__ import annotations
from typing import Optional
from PokerGame import Move, PokerGame, NUM_TO_POKER_HAND
from GameRunner import NUM_TO_ACTION

FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4


class GameTree:
    """
    Decision tree for game sequences

    Each root/node represents a class of action; a way of categorizing the situation/board state in which players made
    their decisions and their responses to the situation.

    Represenatation Invariants:
    - not (self.classes_of_action is None) or self.subtrees == {}
    - If the classes of action is an empty set, the tree's current node represents the start of the game, where no moves
    have been played.
    - all(c == self.subtrees[c].classes_of_action for c in self.subtrees)
    """
    # note that
    classes_of_action: Optional[set[str]]
    subtrees: dict[set[str], GameTree]
    right_decision_threshold: float

    def __init__(self, node_val: set[str] | None) -> None:
        self.classes_of_action = node_val
        self.subtrees = {}

    def insert_moves(self, moves: list[Move], game_states: list[PokerGame], following: int,
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
        if move_number == len(moves):
            return
        else:
            current_move = moves[move_number]
            current_state = game_states[move_number]
            classes_of_action = self._get_classes_of_action(current_move, current_state, following)
            if classes_of_action not in self.subtrees:
                self.add_subtree(classes_of_action)
            self.subtrees[classes_of_action].insert_moves(moves, game_states, following, move_number + 1)

    def _get_classes_of_action(self, move: Move, game_state: PokerGame, following: int) -> set[str]:
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
        if following == game_state.turn:
            # Kind of confused on this part: how r we always sure that it is player1's turn
            current_best = game_state.rank_poker_hand(game_state.player1_hand)
            if 'High Card' == NUM_TO_POKER_HAND[current_best[0]]:
                classes_so_far.add(f'High Card {current_best[1]} in hand')
            else:
                classes_so_far.add(f'{NUM_TO_POKER_HAND[current_best[0]]} in hand')
            for i in range(1, 11):  # Add strong poker hands that the player can threaten
                if i < current_best[0]:
                    classes_so_far.add(f'{NUM_TO_POKER_HAND[i]} is threat')
        else:
            following_best = game_state.rank_poker_hand(game_state.player2_hand)
            for i in range(1, 11):
                if i < following_best[0]:
                    classes_so_far.add(f'{NUM_TO_POKER_HAND[i]} is threat')
        # Add type of move that was played (same for both options)
        if move[0] == FOLD_CODE:
            classes_so_far.add('Fold')
        elif move[0] == CHECK_CODE:
            classes_so_far.add('Check')
        elif move[0] == CALL_CODE:
            classes_so_far.add('Call')
        else:
            classes_so_far.add(f'{NUM_TO_ACTION[move[0]]}')
        return classes_so_far

    def add_subtree(self, classes_of_action: set[str]) -> None:
        """
        Adds a new subtree to the tree's list of subtrees
        """
        self.subtrees[classes_of_action] = GameTree(classes_of_action)

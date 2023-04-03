"""
DeepPoker Project

This module contains a subclass of Player -- TreePlayer -- that can:
    a) make random moves to 'learn' new strategies
    b) traverse through the games of poker that it has experienced to make the 'optimal decision' given specific
        situations

This file is Copyright (c) 2023 Francis Madarang, Sungjin Hong, Sean Kwee, Yenah Lee
"""
import copy
import random
from Player import Player, NaivePlayer, TestingPlayer
from GameTree import GameTree, Card
from PokerGame import PokerGame
from GameRunner import run_round, NUM_TO_ACTION

# Static variables for move constants; consistent across all modules
FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4
ALL_IN_CODE = 5


class TreePlayer(Player):
    """
    TreePlayer -- a player that learns how to play poker by first playing random moves until it is eventually
    'experienced' enough to choose moves that lead to the optimal outcome.

    Instance Attributes:
    - games_played: A game tree representing all sequences of classes of action (just a fancy name for 'tags' that
    categorize the situation the AI finds itself in) that it has ever encountered
    - choices: A list containing all possible move codes
    - new_stage: Whether the game this player is involved in has reached a new stage (Pre-flop to flop, etc.)
    - exploring: Whether the player should be trying new strategies or not
    - old_comm_cards: The community cards in the previous state of the game that this player is playing in

    Representation Invariants:
    - self.games_played.classes_of_action is None
    - all(choice in {FOLD_CODE, RAISE_CODE, BET_CODE, CALL_CODE, CHECK_CODE, ALL_IN_CODE} for choice in self.choices)
    - len(self.old_comm_cards) <= 5
    """
    games_played: GameTree
    choices: list[int]
    new_stage: bool
    exploring: bool
    old_comm_cards: set[Card]

    def __init__(self, balance: int, file: str = 'bruh.kkax') -> None:
        """
        Initializer for TreePlayer

        Preconditions:
        - balance >= 0
        """
        super().__init__(balance)
        self.new_stage = True
        self.choices = []
        for action in NUM_TO_ACTION:
            self.choices.append(action)
        self.games_played = GameTree() if file == 'bruh.kkax' else self.load_game_tree(file)
        self.exploring = True
        self.old_comm_cards = set()

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        """
        Returns the move that this player will make in a given game state of poker

        Will make random moves if the player has not seen the event before, or if it explicitly told to try
        new strategies instead of 'trying' its 'best' to win.

        Parameters:
        - game_state: the current game and further state.
        - player: the player making the move

        Preconditions:
        - game_state is a valid game state of the type of heads up poker we are looking into
        - game_state.check_winner() is None
        - player_num in {1, 2}
        """
        self.has_moved = True
        # if not trying new strategies, attempt to draw from experience
        if not self.exploring:
            clone_state = game_state.copy()
            clone_state.turn = (clone_state.turn + 1) % 2
            prev_move = (FOLD_CODE, 0)

            # determine the right old move
            if player_num == 1 and len(game_state.player2_moves) > 0:
                prev_move = game_state.player2_moves[-1]
            elif player_num == 2:
                prev_move = game_state.player1_moves[-1]
            # determine if the opponent made their move before new community cards were revealed
            if prev_move[0] in {CHECK_CODE, CALL_CODE}:
                clone_state.community_cards = self.old_comm_cards
                if self.old_comm_cards == set():
                    clone_state.stage = 1
                classes_of_action = self.games_played.get_classes_of_action(prev_move, clone_state, game_state.turn,
                                                                            True)
                if frozenset(classes_of_action) in self.games_played.subtrees:
                    self.games_played = self.games_played.subtrees[frozenset(classes_of_action)]
                else:   # tree has not encountered this situation
                    self.exploring = True
            if self.new_stage:
                evaluation = self.games_played.get_classes_of_action((0, 0), game_state, game_state.turn, False)
                if frozenset(evaluation) in self.games_played.subtrees:
                    self.games_played = self.games_played.subtrees[frozenset(evaluation)]
                else:   # tree has not encountered this situation
                    self.exploring = True
                self.new_stage = False
            if prev_move[0] in {ALL_IN_CODE, RAISE_CODE, BET_CODE}:
                classes_of_action = self.games_played.get_classes_of_action(prev_move, clone_state, game_state.turn,
                                                                            True)
                if frozenset(classes_of_action) in self.games_played.subtrees:
                    self.games_played = self.games_played.subtrees[frozenset(classes_of_action)]
                else:  # tree has not encountered this situation
                    self.exploring = True
            self.old_comm_cards = game_state.community_cards
            # search for the best continuation based on confidence values in subtree, now that we know we have
            # encountered similar situations before
            if not self.exploring:
                best_so_far = -1
                subtrees = self.games_played.subtrees
                for subtree in subtrees:
                    if best_so_far == -1:
                        best_so_far = subtree
                    elif subtrees[best_so_far].move_confidence_value < subtrees[subtree].move_confidence_value:
                        best_so_far = subtree
                for action in NUM_TO_ACTION:
                    # determine bet sizing if applicable
                    if NUM_TO_ACTION[action] in list(best_so_far)[0]:
                        degree = -1
                        if 'Very Aggressive' in list(best_so_far)[0]:
                            degree = 4
                        elif 'Aggressive' in list(best_so_far)[0]:
                            degree = 3
                        elif 'Conservative' in list(best_so_far)[0]:
                            degree = 1
                        elif 'Moderate' in list(best_so_far)[0]:
                            degree = 2
                        final_action = self._final_decision(game_state, action, degree)
                        classes_of_action = self.games_played.get_classes_of_action(final_action, game_state,
                                                                                    game_state.turn,
                                                                                    True)
                        if frozenset(classes_of_action) in self.games_played.subtrees:
                            self.games_played = self.games_played.subtrees[frozenset(classes_of_action)]
                        return final_action
        # if exploring or tree has not encountered this situation, simply make random moves
        if self.exploring:
            move_type = random.choice(self.choices)
            while (move_type in {CHECK_CODE, BET_CODE} and game_state.last_bet > 0) or \
                    (move_type in {CALL_CODE, RAISE_CODE} and game_state.last_bet == 0) or \
                    (move_type == RAISE_CODE and self.has_raised):  # reroll the move if invalid
                move_type = random.choice(self.choices)
            return self._final_decision(game_state, move_type)
        return (0, 0)

    def _final_decision(self, game_state: PokerGame, action: int, degree: int = -1) -> tuple[int, int]:
        """
        Helper function for make_move once the player decides on a type of move (exists to avoid code duplication).
        Action is equivalent to the type of move the player chose to make.

        Parameters:
        - game_state: the current game state
        - action: the action the player chose to make
        - degree: "degree of action" refer to above for examples. essentially the volitiy of it

        Preconditions:
        - game_state is a valid game state of the type of poker we are investigating
        - action in NUM_TO_ACTION
        - not (degree in {1, 2, 3, 4}) or action in {RAISE_CODE, BET_CODE}
        """
        if NUM_TO_ACTION[action] == 'Fold':
            return self.move_fold()
        elif NUM_TO_ACTION[action] == 'Call':
            return self.move_call(game_state.last_bet)
        elif NUM_TO_ACTION[action] == 'Check':
            return self.move_check()
        elif NUM_TO_ACTION[action] == 'All-in':
            return self.move_all_in()
        else:
            # 1 = conservative bet, 2 = moderate bet, 3 = aggressive bet, 4 = very aggressive bet
            degree_bet = random.randint(1, 4) if degree != -1 else degree
            bet_amount = int(self.bet_size(game_state, 0, degree_bet))
            if bet_amount == self.balance:
                return self.move_all_in()
            if NUM_TO_ACTION[action] == 'Raise':
                return self.move_raise(bet_amount)
            else:
                return self.move_bet(bet_amount)

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float, degree: int = 0) -> float:
        """
        Returns an appropriate bet size for a given game state and win probability for a game of poker

        Parameters:
        - game_state; current game state
        - win_prob_threshold: the win probability threshold of action corresponding
        - degree: degree of action -- volitity

        Preconditions:
        - game_state is a valid game state of the type of poker we are investigating
        - 0 <= win_prob_threshold <= 1.0
        """
        if degree == 1:
            return min(self.balance, game_state.pool)
        elif degree == 2:
            return min(self.balance, game_state.pool * 2)
        elif degree == 3:
            return min(self.balance, game_state.pool * 4)
        else:
            return min(self.balance, game_state.pool * 8)

    def load_game_tree(self, gametree: str) -> GameTree:
        """
        Load in sequences of classes of action to the games this player has 'experienced' from a given input file.

        Parameters:
        - gametree: the file corresponding to the gametree data needing to be loaded in.

        Preconditions:
        - gametree is in the same directory of this file
        """
        gamer = GameTree()
        reader = open(gametree, 'r')
        for row in reader:
            c = row.split('$')
            c[-1] = c[-1][:-1]  # remove \n
            gamer.insert_row_moves(c)

        return gamer

    def reset_player(self) -> None:
        """
        Resets game variables of the player for when the stage changes.
        """
        Player.reset_player(self)
        self.new_stage = True


def print_to_file(tree: GameTree, destination: str) -> None:
    """
    Writes all sequences of events and confidence statistics for each event to a file.
    Will override ALL existing content in the file.

    Parameters:
    - tree: the gametree corresponding to the data needed to be loaded in
    - destination: the file destination of the reading

    Preconditions:
    - tree only contains valid sequences of classes of action for the type of poker we are investigating.
    """
    f = open(destination, "w")
    tree_to_list_of_strings = _tree_path_to_string(tree)  # retrieve all sequences of events this player has experienced
    for row in tree_to_list_of_strings:
        f.write(row+'\n')
    f.close()


def _tree_path_to_string(tree: GameTree) -> list[str]:
    """
    Recursively gets all possible paths down a tree as a list of strings.

    Parameters:
    - tree: the gametree we are reading

    Preconditions:
    - tree only contains valid sequences of classes of action for the type of poker we are investigating.
    """
    if len(tree.subtrees) == 0:
        return [tree.__str__()]
    else:
        all_paths = []
        curr_stats = tree.__str__()
        for subtree in tree.subtrees:
            path_so_fars = _tree_path_to_string(tree.subtrees[subtree])
            for path in path_so_fars:
                new_path = curr_stats + "$" + path
                all_paths.append(new_path)

        return all_paths


if __name__ == '__main__':
    # depending on what you want to do, running this file will do something different
    # - if mode is learning, it will run a specified number of games for the tree player to learn from, and write the
    #   state of the tree at the end of the simulations to the target file
    # - if the mode is playing, it will use the saved state inside the tree player inside the target file to play a
    #   specified number of games
    # NOTE: IF MODE IS LEARNING, THE TARGET FILE MUST EXIST IN THE DIRECTORY THIS FILE IS BEING RUN IN
    mode = 'learning'
    target_file = 'destination.txt'
    # play 100 games so the TA won't have to AFK for a decent game state
    total_games = 100

    if mode == 'learning':
        all_games = GameTree()
        # run initial games so the player gets a basic idea of how to play poker
        naive_games = total_games // 2
        for i in range(naive_games):
            p1 = TestingPlayer(10000)
            result = run_round(p1, NaivePlayer(10000), False)
            result[-1].check_winner()
            # print(result[-1])
            move_sequence = result[-1].get_move_sequence()
            # learn from both how p1 could have played and how p2 could have played
            all_games.insert_moves(move_sequence, result, 0)
            all_games.insert_moves(move_sequence, result, 1)

        # create thresholds for trying new strategies -- the higher the threshold, the likelier a new strategy is to be
        # attempted
        game_count = total_games // 2
        exploration_games = game_count * 3 // 4
        game_thresholds = []
        for i in range(0, exploration_games):
            game_thresholds.append(1 - (i / exploration_games))
        for _ in range(exploration_games, game_count):
            game_thresholds.append(-1)

        # run games where new strategies can be attempted and verified for effectiveness
        for i in range(game_count):
            p1 = TreePlayer(10000)
            p1.games_played = copy.copy(all_games)
            # decide whether to explore new strategies or not
            p1.exploring = True if random.random() <= game_thresholds[i] else False
            result = run_round(p1, NaivePlayer(10000), False)
            result[-1].check_winner()
            # print(result[-1])
            move_sequence = result[-1].get_move_sequence()
            # learn from both how p1 could have played and how p2 could have played
            all_games.insert_moves(move_sequence, result, 0)
            all_games.insert_moves(move_sequence, result, 1)

        # write decision tree result to the target file
        print_to_file(all_games, target_file)
        print('done')
    elif mode == 'playing':
        tp = TreePlayer(10, target_file)
        games_played = copy.copy(tp.games_played)
        for _ in range(total_games):
            p1 = TreePlayer(10000)
            p1.games_played = copy.copy(games_played)
            p1.exploring = False
            result = run_round(p1, NaivePlayer(10000))
            result[-1].check_winner()
            print(f'Player {result[-1].winner} has won the game and {result[-1].pool} currency!')
            print(result[-1])

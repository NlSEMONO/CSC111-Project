"""
File for TreePlayer, a player who 'learns' from experience by playing against various playstyles
"""
import copy
import random
from Player import Player, NaivePlayer, TestingPlayer
from GameTree import GameTree
from PokerGame import PokerGame
from GameRunner import run_round, NUM_TO_ACTION

FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4



class TreePlayer(Player):
    """
    TreePlayer -- a player that learns how to play poker by first playing random moves until it eventually chooses
    moves that lead to the optimal outcome.
    """
    games_played: GameTree
    choices: list[int]
    new_stage: bool
    exploring: bool

    def __init__(self, balance: int, file: str = 'bruh.kkax') -> None:
        super().__init__(balance)
        self.new_stage = True
        self.choices = []
        for action in NUM_TO_ACTION:
            self.choices.append(action)
        self.games_played = GameTree() if file == 'bruh.kkax' else self.load_game_tree(file)
        self.exploring = True

    def make_move(self, game_state: PokerGame, player_num: int, explore: bool = True) -> tuple[int, int]:
        """
        Returns the move that this player will make in a given game state of poker

        Will make random moves if the player has not seen the event before, or if it is not specified to try its best to
        win the game.
        """
        self.has_moved = True
        if not explore or not self.exploring:
            if player_num == 1 and len(game_state.player2_moves) > 0:
                prev_move = game_state.player2_moves[-1]
                classes_of_action = self.games_played.get_classes_of_action(prev_move, game_state, (game_state.turn + 1) % 2,
                                                                            True)
                if frozenset(classes_of_action) in self.games_played.subtrees:
                    self.games_played = self.games_played.subtrees[frozenset(classes_of_action)]
                else: # tree has not encountered this situation
                    explore = True
            if self.new_stage:
                evaluation = self.games_played.get_classes_of_action((0, 0), game_state, (game_state.turn + 1) % 2, False)
                if frozenset(evaluation) in self.games_played.subtrees:
                    self.games_played = self.games_played.subtrees[frozenset(evaluation)]
                else: # tree has not encountered this situation
                    explore = True
                self.new_stage = False
            if player_num == 2:
                prev_move = game_state.player1_moves[-1]
                classes_of_action = self.games_played.get_classes_of_action(prev_move, game_state, game_state.turn,
                                                                            True)
                if frozenset(classes_of_action) in self.games_played.subtrees:
                    self.games_played = self.games_played.subtrees[frozenset(classes_of_action)]
                else: # tree has not encountered this situation
                    explore = True
            if not explore:
                # search for the best continuation based on confidence values in subtree
                best_so_far = -1
                subtrees = self.games_played.subtrees
                for subtree in subtrees:
                    if best_so_far == -1:
                        best_so_far = subtree
                    elif subtrees[best_so_far].move_confidence_value < subtrees[best_so_far].move_confidence_value:
                        best_so_far = subtree
                for action in NUM_TO_ACTION:
                    if action in list(best_so_far)[0]:
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
        if explore:
            move_type = random.choice(self.choices)
            while move_type in {CHECK_CODE, BET_CODE} and game_state.last_bet > 0: # reroll the move if invalid
                move_type = random.choice(self.choices)
            return self._final_decision(game_state, move_type)
        return (0, 0)

    def _final_decision(self, game_state: PokerGame, action: int, degree: int = -1) -> tuple[int, int]:
        """
        Helper function for make_move once the player decides on a type of move.
        Action is equivalent to the type of move the player chose to make.
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
        """ load in game tree for make_move to use."""
        gamer = GameTree()
        reader = open(gametree, 'r')
        for row in reader:
            c = row.split('$')
            c[-1] = c[-1][:-1] # remove \n
            gamer.insert_row_moves(c)

        return gamer

    def reset_player(self) -> None:
        """
        Resets game variables of the player
        """
        Player.reset_player(self)
        self.new_stage = True


def print_to_file(tree: GameTree, destination: str) -> None:
    """
    Writes properties of a GameTree to a file. Will override ALL existing content in the file.
    """
    f = open(destination, "w")
    tree_to_list_of_strings = _tree_path_to_string(tree)
    for row in tree_to_list_of_strings:
        f.write(row+'\n')
    f.close()


def _tree_path_to_string(tree: GameTree) -> list[str]:
    """
    Recursively gets all possible paths down a tree as a list of strings
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
    # tree_player = TreePlayer(10000)
    # tp = TreePlayer(10000, 'TreePlayer_100000_games.txt')
    # subtrees = list(tp.games_played.subtrees.keys())
    # tree = copy.copy(tp.games_played)
    tree = GameTree()
    # for i in range(50000):
    #     p1 = TreePlayer(10000)
    #     p1.games_played = copy.copy(tree)
    #     result = run_round(p1, NaivePlayer(10000), False)
    #     result[-1].check_winner()
    #     # print(result[-1])
    #     move_sequence = result[-1].get_move_sequence()
    #     # learn from both how p1 could have played and how p2 could have played
    #     tree.insert_moves(move_sequence, result, 0)
    #     tree.insert_moves(move_sequence, result, 1)

    for i in range(50000):
        p1 = TreePlayer(10000)
        p1.games_played = copy.copy(tree)
        result = run_round(p1, NaivePlayer(10000), False)
        result[-1].check_winner()
        # print(result[-1])
        move_sequence = result[-1].get_move_sequence()
        # learn from both how p1 could have played and how p2 could have played
        tree.insert_moves(move_sequence, result, 0)
        tree.insert_moves(move_sequence, result, 1)

    # tp = TreePlayer(10000, 'test.csv')
    # while len(tree.subtrees) > 0:
    #     print(tree.classes_of_action)
    #     subtrees = list(tree.subtrees.keys())
    #     print(f'\t{subtrees}')
    #     tree = tree.subtrees[subtrees[-1]]
    # print(tree.classes_of_action)
    # i = 0
    # c = 0
    # for _ in range(1000):
    #     print(i)
    #     i += 1
    #     p1 = TreePlayer(10000)
    #     p1.games_played = copy.copy(tree)
    #     result = run_round(p1, NaivePlayer(10000), False)
    #     result[-1].check_winner()
    #     # print(result[-1])
    #     move_sequence = result[-1].get_move_sequence()
    #     # learn from both how p1 could have played and how p2 could have played
    #     tree.insert_moves(move_sequence, result, 0)
    #     tree.insert_moves(move_sequence, result, 1)
    #     print(move_sequence)
    #     if (move_sequence == [(0, -1)]):
    #         c += 1
    # print(c)
    print('done')
    print_to_file(tree, 'TreePlayer_50000_games.txt')

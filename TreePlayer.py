"""
File for TreePlayer, a player who 'learns' from experience by playing against various playstyles
"""
from Player import Player, NaivePlayer, TestingPlayer
from GameTree import GameTree
from PokerGame import PokerGame
from GameRunner import run_round


class TreePlayer(Player):
    """
    TreePlayer -- a player that learns how to play poker by first playing random moves until it eventually chooses
    moves that lead to the optimal outcome.
    """
    games_played: GameTree

    def __init__(self, balance: int, file: str = 'bruh.kkax') -> None:
        super().__init__(balance)
        self.games_played = GameTree() if file == 'bruh.kkax' else self.load_game_tree(file)

    def make_move(self, game_state: PokerGame, player_num: int, explore: bool = True) -> tuple[int, int]:
        """
        Returns the move that this player will make in a given game state of poker

        Will make random moves if the player has not seen the event before, or if it is not specified to try its best to
        win the game.
        """
        return (0, 0)

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float) -> float:
        """
        Returns an appropriate bet size for a given game state and win probability for a game of poker
        """
        return 1.0

    def load_game_tree(self, gametree: str) -> GameTree:
        """ load in game tree for make_move to use."""
        gamer = GameTree()
        reader = open(gametree, 'r')
        for row in reader:
            c = row.split('$')
            c[-1] = c[-1][:-1] # remove \n
            gamer.insert_row_moves(c)

        return gamer


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
    tp = TreePlayer(10000, 'finally.txt')
    subtrees = list(tp.games_played.subtrees.keys())
    # tree = GameTree()
    # for _ in range(100):
    #     result = run_round(TestingPlayer(10000), NaivePlayer(10000), False)
    #     result[-1].check_winner()
    #     # print(result[-1])
    #     move_sequence = result[-1].get_move_sequence()
    #     # learn from both how p1 could have played and how p2 could have played
    #     tree.insert_moves(move_sequence, result, 0)
    #     tree.insert_moves(move_sequence, result, 1)
    # # tp = TreePlayer(10000, 'test.csv')
    # print_to_file(tree, 'finally.txt')
    # print('done')

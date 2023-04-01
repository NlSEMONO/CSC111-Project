"""
File for TreePlayer, a player who 'learns' from experience by playing against various playstyles
"""
from Player import Player, NaivePlayer
from GameTree import GameTree
from PokerGame import PokerGame
from GameRunner import run_round_with_game_states


class TreePlayer(Player):
    """
    TreePlayer -- a player that learns how to play poker by first playing random moves until it eventually chooses
    moves that lead to the optimal outcome.
    """
    games_played: GameTree

    def __init__(self, balance: int) -> None:
        super().__init__(balance)
        self.games_played = GameTree()

    def make_move(self, game_state: PokerGame, player_num: int, explore: bool = True) -> tuple[int, int]:
        """
        Returns the move that this player will make in a given game state of poker

        Will make random moves if the player has not seen the event before, or if it is not specified to try its best to
        win the game.
        """
        self.games_played.get_classes_of_action((0, 0), game_state, game_state.turn + 1, False)

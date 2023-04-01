from Player import Player
from PokerGame import Card, PokerGame
import csv
from GameTree import GameTree

class LearningPlayer(Player):
    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        gametree = self.load_game_tree('test.csv')


    def decipher_win(self, tree: GameTree) -> set:
        """ decipher which tree to traverse down """


    def load_game_tree(self, gametree: str) -> GameTree:
        """ load in game tree for make_move to use."""
        gamer = GameTree()
        reader = open(gametree, 'r')
        for row in reader:
            c = row.split('$')
            removen = ''
            for i in range(0, len(c[len(c) - 1]) - 1): #remove new line
                removen += c[len(c) - 1][i]
            c[len(c) - 1] = removen
            gamer.insert_row_moves(c)

        return gamer

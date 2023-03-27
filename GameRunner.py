from PokerGame import PokerGame
import Player
import random

p1 = Player.CheckPlayer()
p2 = Player.CheckPlayer()

def run_round(player1: Player.Player, player2: Player.Player) -> None:
    """
    Simulates a round of poker
    """
    dealer = random.randint(1, 2)
    game = PokerGame()
    turn_order = [player1 if dealer == 1 else player2, player2 if dealer == 1 else player1]

    while game.check_winner() is None:
        move = turn_order[game.turn].make_move(game)
        game.run_move(move)
        if move[0] == 3:
            turn_order[game.turn] = False # must move again if raise occurs
        game.check_winner()
        if all(p.has_moved for p in turn_order):
            game.next_stage()

    print(f'Player {game.winner} has won the game!')
    print(game)

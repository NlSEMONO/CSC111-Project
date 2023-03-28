from PokerGame import PokerGame
import Player
import random

p1 = Player.CheckPlayer(100)
p2 = Player.CheckPlayer(100)

def run_round(player1: Player.Player, player2: Player.Player) -> PokerGame:
    """
    Simulates a round of poker
    """
    dealer = random.randint(1, 2)
    game = PokerGame()
    turn_order = [player1 if dealer == 1 else player2, player2 if dealer == 1 else player1]
    game.next_stage()

    while game.check_winner() is None:
        # print(f'{game.last_bet} {game.community_cards} {game.stage}')
        move = turn_order[game.turn].make_move(game)
        game.run_move(move)
        if move[0] == 3:
            turn_order[game.turn] = False # must move again if raise occurs
        game.check_winner()
        if all(p.has_moved for p in turn_order):
            game.next_stage()
            turn_order[0].has_moved = False
            turn_order[1].has_moved = False
            turn_order[0].bet_this_round = 0
            turn_order[1].bet_this_round = 0

    # print(f'{game.player1_moves} {game.player2_moves}')
    # print(game)

    return game


for i in range(100):
    game = run_round(p1, p2)
    print(f'Player {game.winner} has won the game!')
    print(game)

"""
test case for straight flush!

game = PokerGame()
game.community_cards = {(1, 1), (2, 1), (3, 1), (4, 1), (8, 4)}
game._rank_poker_hand({(5, 1), (10, 2)})
"""

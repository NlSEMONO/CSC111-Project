from PokerGame import PokerGame
import Player
from NaivePlayer import NaivePlayer
import random

NUM_TO_ACTION = {Player.FOLD_CODE: 'Fold', Player.CHECK_CODE: 'Check', Player.CALL_CODE: 'Call',
                 Player.BET_CODE: 'Bet', Player.RAISE_CODE: 'Raise', Player.ALL_IN_CODE: 'All-in'}


def run_round(player1: Player.Player, player2: Player.Player) -> PokerGame:
    """
    Simulates a round of poker
    """
    dealer = random.randint(1, 2)
    game = PokerGame()
    turn_order = [player1 if dealer == 1 else player2, player2 if dealer == 1 else player1]
    corresponding_hand = [1, 2]
    game.next_stage()
    p1_initial_cost = int((1 / 200) * turn_order[0].balance)
    p2_initial_cost = int((1 / 100) * turn_order[1].balance)
    game.pool += p1_initial_cost
    game.pool += p2_initial_cost
    turn_order[0].balance -= p1_initial_cost
    turn_order[0].bet_this_round = p1_initial_cost
    turn_order[1].bet_this_round = p2_initial_cost
    turn_order[1].balance -= p2_initial_cost
    game.last_bet = p2_initial_cost

    while game.check_winner() is None:
        # print(f'{game.last_bet} {game.community_cards} {game.stage}')
        move = turn_order[game.turn].make_move(game, corresponding_hand[game.turn])
        print(f'[{game.stage}] Player {game.turn + 1} {NUM_TO_ACTION[move[0]]}s{"" if move[0] in {Player.FOLD_CODE, Player.CHECK_CODE, Player.CALL_CODE, Player.ALL_IN_CODE} else " "+str(move[1])}')
        game.run_move(move)
        if move[0] == Player.RAISE_CODE or (move[0] == Player.BET_CODE and move[1] > 0):
            turn_order[game.turn].has_moved = False  # must move again if raise occurs
        elif turn_order[game.turn].balance == 0:
            game.check_winner(True)
        game.check_winner()
        if all(p.has_moved for p in turn_order):
            game.next_stage()
            turn_order[0].has_moved = False
            turn_order[1].has_moved = False
            turn_order[0].bet_this_round = 0
            turn_order[1].bet_this_round = 0
            game.last_bet = 0

    # print(f'{game.player1_moves} {game.player2_moves}')
    # print(game)

    return game

<<<<<<< Updated upstream

for i in range(100):
    p1 = NaivePlayer(10000)
    p2 = NaivePlayer(10000)
    simulated_game = run_round(p1, p2)
    print(f'Player {simulated_game.winner} has won the game and {simulated_game.pool} currency!')
    print(simulated_game)
=======
if __name__ == '__main__':
    for i in range(10):
        p1 = Player.TestingPlayer(10000)
        p2 = Player.NaivePlayer(10000)
        simulated_game = run_round(p1, p2)
        print(f'Player {simulated_game.winner} has won the game and {simulated_game.pool} currency!')
        print(simulated_game)
>>>>>>> Stashed changes

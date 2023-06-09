"""
DeepPoker Project

This module contains a function that runs a simulation of a game of heads up poker with only one raise allowed per stage
and with no restrictions on raise values.

This file is Copyright (c) 2023 Francis Madarang, Sungjin Hong, Sean Kwee, Yenah Lee
"""
from poker_game import PokerGame
from player import Player, NaivePlayer, TestingPlayer
import random
import python_ta

# STATICS FOR MOVE CODES
FOLD_CODE = 0
CHECK_CODE = 1
CALL_CODE = 2
BET_CODE = 3
RAISE_CODE = 4
ALL_IN_CODE = 5

NUM_TO_ACTION = {FOLD_CODE: 'Fold', CHECK_CODE: 'Check', CALL_CODE: 'Call',
                 BET_CODE: 'Bet', RAISE_CODE: 'Raise', ALL_IN_CODE: 'All-in'}


def run_round(player1: Player, player2: Player, should_print: bool = True) -> list[PokerGame]:
    """
    Simulates a round of poker (one game from Pre-flop to showdown)

    Parameters:
    - player1: player1's equivalent player
    - player2: player2's equivalent player
    - should_print: if the round should be printed.

    Preconditions:
        - player1 and player2 are valid Player objects constructed from the Player parent class in Parameterspy
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
    game_states_so_far = [game.copy()]

    while game.check_winner() is None:
        # print(f'{game.last_bet} {game.community_cards} {game.stage}')
        invested_initially = turn_order[game.turn].bet_this_round
        move = turn_order[game.turn].make_move(game, corresponding_hand[game.turn])
        if should_print:
            print(f'[{game.stage}] Player {game.turn + 1} {NUM_TO_ACTION[move[0]]}s'
                  f'{"" if move[0] not in {RAISE_CODE, BET_CODE}else " "+str(move[1])}')
        game.run_move(move, move[1] - invested_initially if game.stage == 1 else -1)
        if (move[0] == RAISE_CODE or
            (move[0] == BET_CODE and move[1] > 0) or move[0] == ALL_IN_CODE) and \
                turn_order[game.turn].balance > 0:
            turn_order[game.turn].has_moved = False  # must move again if raise occurs
        elif turn_order[game.turn].balance == 0:
            game.check_winner(True)
        game.check_winner()
        if all(p.has_moved for p in turn_order):
            game.next_stage()
            turn_order[0].reset_player()
            turn_order[1].reset_player()
            game.last_bet = 0
        game_states_so_far.append(game.copy())

    # print(f'{game.player1_moves} {game.player2_moves}')
    # print(game)

    return game_states_so_far


if __name__ == '__main__':
    games = 200
    for i in range(games):
        p1 = TestingPlayer(10000)
        p2 = NaivePlayer(10000)
        result = run_round(p1, p2, False)[-1]
        print(f'Player {result.winner} has won the game and {result.pool} currency!')
        print(result)

python_ta.check_all(config={
    'max-line-length': 120,
    'extra-imports': ['pygame', 'random', 'pygame.gfxdraw', 'player', 'poker_game', 'NaivePlayer', 'time'],
    'allowed-io': ['make_move', 'HumanPlayer', 'run_round2'],
    'generated-members': ['pygame.*'],
    'disable': ['E9997', 'E9992']
})

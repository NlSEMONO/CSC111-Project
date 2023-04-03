"""
DeepPoker Project - Final Submission

This module contains an abstract class and a few subclasses representing playstyles for a game of poker.

This file is Copyright (c) 2023 Francis Madarang, Sungjin Hong, Sean Kwee, Yenah Lee
"""
import copy
import random
from game_tree import GameTree
from player import TestingPlayer, NaivePlayer
from game_runner import run_round
from tree_player import TreePlayer, print_to_file
from frontend import frontend

if __name__ == '__main__':
    # depending on what you want to do, running this file will do something different
    # - if mode is 'learning', it will run a specified number of games for the tree player to learn from, and write the
    #   state of the tree at the end of the simulations to the target file
    # - if the mode is 'playing', it will use the saved state inside the tree player inside the target file to play a
    #   specified number of games
    # NOTE: IF MODE IS 'playing', THE TARGET FILE MUST EXIST IN THE DIRECTORY THIS FILE IS BEING RUN IN
    mode = 'playing'
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
        # print('done')
    elif mode == 'playing':  # play vs the AI using a given target file
        # target_file = 'TreePlayer_20000.txt'  # <- play vs our saved state AI by uncommenting this line :)
        tp = TreePlayer(10, target_file)
        games_played = copy.copy(tp.games_played)
        for _ in range(total_games):
            p1 = TreePlayer(10000)
            p1.games_played = copy.copy(games_played)
            p1.exploring = False
            result = frontend(p1)

"""
A naive player who will bet/raise when they have a good hand, and will fold if they don't (relative to the enemy bets)
"""

from Player import Player
from PokerGame import Card, PokerGame


class NaivePlayer(Player):
    """
    Player who bets/raises when they have a good hand and folds otherwise (also is 'scared' of big bets)
    """
    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        """
        Makes a move based on the state of the 'board' (game_state) it is given
        The move number correlates to the type of move the player makes.
        Bet is the bet amount.
        Moves:
        0: Fold
        1: Check
        2: Call
        3: Bet
        4: Raise
        """
        self.has_moved = True
        if game_state.stage == 1: # different algorithm for pre-flop
            if player_num == 1:
                hand = list(game_state.player1_hand)
            else:
                hand = list(game_state.player2_hand)
            hand.sort()
            how_good = self.rate_hand(hand)
            if how_good == 2 and game_state.last_bet > self.bet_this_round:
                return self.move_fold()
            elif how_good == 2 and game_state.last_bet == self.bet_this_round:
                return self.move_check()
            bet = int(self.bet_size(game_state, 0, how_good))
            if bet > game_state.last_bet:
                return self.move_raise(bet)
            else:
                return self.move_call(game_state.last_bet)

        win_prob = self.win_probability(game_state, player_num)
        if win_prob >= 0.95: # all in if win is basically guaranteed
            bet_amount = int(self.balance)
            if game_state.last_bet == 0:
                return self.move_bet(bet_amount)
            else:
                return self.move_raise(bet_amount)
        elif win_prob >= 0.5: #safe betting
            bet_amount = int(self.bet_size(game_state, win_prob))
            if game_state.last_bet == 0:
                return self.move_bet(bet_amount)
            elif game_state.last_bet > (game_state.pool - game_state.last_bet) * (1 - win_prob): # their bet exceeds
                # our expectation to win the game
                return self.move_fold()
            else: # call their 'bluff'
                return self.move_call(game_state.last_bet)
        elif game_state.last_bet == 0:
            return self.move_check()
        else: # fold if under threat
            return self.move_fold()

    def win_probability(self, game_state: PokerGame, player_num: int) -> float:
        """
        returns the win probability
        """
        if player_num == 1:
            hand = game_state.player1_hand
        else:
            hand = game_state.player2_hand

        my_score = game_state.rank_poker_hand(hand)
        used = game_state.community_cards.union(hand)
        all_opponent_hands = _generate_card_combos(used, set(), 1)
        better_hands = 0
        for hand in all_opponent_hands:
            if game_state.determine_winner(my_score, game_state.rank_poker_hand(hand)) == 1:
                better_hands += 1

        return better_hands / len(all_opponent_hands)

    def bet_size(self, game_state: PokerGame, win_prob_threshold: float, hand_quality: int = 0) -> float:
        """
        Calculates current bet size reasonable to the gamestate.
        Calculate chance to "scare/provoke" opponents into making mistakes.
        """
        # Determine a bet size based on the current balance and win probability
        if game_state.stage == 1:
            if hand_quality == 1:
                return 0.025 * self.balance
            else:
                return game_state.last_bet

        # typically, you bet proportionally to the pot based on how likely you think you are to win
        bet_amount = min(self.balance, game_state.pool * (1 / (1 - win_prob_threshold)))
        return bet_amount


def _generate_card_combos(used_cards: set[Card], cards_so_far: set[Card], level_to_stop: int) -> list[set[Card]]:
    """
    Returns all the possible pairs of cards that have not appeared in used_cards
    """
    all_pairs = []
    for i in range(1, 14):
        for j in range(1, 5):
            if (i, j) not in used_cards:
                if len(cards_so_far) == level_to_stop:
                    added_card = cards_so_far.union({(i, j)})
                    all_pairs.append(added_card)
                else:
                    new_cards_so_far = cards_so_far.union({(i, j)})
                    new_used_cards = used_cards.union(new_cards_so_far)
                    all_pairs.extend(_generate_card_combos(new_used_cards, new_cards_so_far, level_to_stop))

    return all_pairs

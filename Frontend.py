"""
DeepPoker Project

File that runs the UI
"""
import pygame
import FrontendTools
from pygame.colordict import THECOLORS
import random
import math
import pygame.gfxdraw
import Player
from PokerGame import PokerGame
from NaivePlayer import NaivePlayer
from TreePlayer import TreePlayer

from GameRunner import NUM_TO_ACTION, run_round

from time import sleep



class HumanPlayer(Player.Player):
    """
    Abstract class representing a human player
        move_button: (name of the move, bet or raise amount if the move is a bet or raise otherwise 0)
        made_move: whether or not the user has made a move in each stage
    """
    move_button: tuple[str, int]
    made_move: bool

    # if not fold & check code => bet amount
    def __init__(self, balance: int, move_button: tuple[str, int] = ('None', 0), made_move: bool = False) -> None:
        Player.Player.__init__(self, balance)
        # modify this attribute every stage that user presses a button
        self.move_button = move_button
        self.made_move = made_move

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        # wait until user makes a move (presses a button) in each turn
        while not self.made_move:
            print('test33')
        # reset has_moved
        self.made_move = False
        self.has_moved = True


        if self.move_button[0] == "bet":
            if self.move_button[1] == self.balance:
                return self.move_all_in()
            return self.move_bet(self.move_button[1])

        elif self.move_button[0] == "check":
            return self.move_check()

        elif self.move_button[0] == "call":
            last_bet = game_state.last_bet
            return self.move_call(last_bet)

        elif self.move_button[0] == "raise":
            if self.move_button[1] == self.balance:
                return self.move_all_in()
            return self.move_raise(self.move_button[1])

        elif self.move_button[0] == "fold":
            return self.move_fold()

class Button:
    def __init__(self, x, y, width, height, text, disabled = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.disabled = disabled

    def draw(self, surface):
        if self.disabled:
            pygame.draw.rect(surface, (128, 128, 128), self.rect)
        else:
            pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# Initialize Pygame
pygame.init()

screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height))
WINDOW_SIZE = (screen_width, screen_height)
pygame.display.set_caption("Poker Game")

# Calculate the proportional size of the card images based on the screen resolution
card_width = screen_width // 13
card_height = int(card_width * 1.4)

# Load card images
card_back = pygame.transform.scale(pygame.image.load("img/card_back.png"), (card_width, card_height))


card_images = {
    "(1, 3)": pygame.transform.scale(pygame.image.load("img/Clover/A.png"), (card_width, card_height)),
    "(2, 3)": pygame.transform.scale(pygame.image.load("img/Clover/2.png"), (card_width, card_height)),
    "(3, 3)": pygame.transform.scale(pygame.image.load("img/Clover/3.png"), (card_width, card_height)),
    "(4, 3)": pygame.transform.scale(pygame.image.load("img/Clover/4.webp"), (card_width, card_height)),
    "(5, 3)": pygame.transform.scale(pygame.image.load("img/Clover/5.png"), (card_width, card_height)),
    "(6, 3)": pygame.transform.scale(pygame.image.load("img/Clover/6.png"), (card_width, card_height)),
    "(7, 3)": pygame.transform.scale(pygame.image.load("img/Clover/7.png"), (card_width, card_height)),
    "(8, 3)": pygame.transform.scale(pygame.image.load("img/Clover/8.png"), (card_width, card_height)),
    "(9, 3)": pygame.transform.scale(pygame.image.load("img/Clover/9.png"), (card_width, card_height)),
    "(10, 3)": pygame.transform.scale(pygame.image.load("img/Clover/10.png"), (card_width, card_height)),
    "(11, 3)": pygame.transform.scale(pygame.image.load("img/Clover/J.jpeg"), (card_width, card_height)),
    "(12, 3)": pygame.transform.scale(pygame.image.load("img/Clover/Q.jpeg"), (card_width, card_height)),
    "(13, 3)": pygame.transform.scale(pygame.image.load("img/Clover/K.webp"), (card_width, card_height)),

    "(1, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/A.png"), (card_width, card_height)),
    "(2, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/2.png"), (card_width, card_height)),
    "(3, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/3.png"), (card_width, card_height)),
    "(4, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/4.png"), (card_width, card_height)),
    "(5, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/5.png"), (card_width, card_height)),
    "(6, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/6.png"), (card_width, card_height)),
    "(7, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/7.png"), (card_width, card_height)),
    "(8, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/8.png"), (card_width, card_height)),
    "(9, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/9.png"), (card_width, card_height)),
    "(10, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/10.png"), (card_width, card_height)),
    "(11, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/J.jpeg"), (card_width, card_height)),
    "(12, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/Q.png"), (card_width, card_height)),
    "(13, 4)": pygame.transform.scale(pygame.image.load("img/Diamond/K.png"), (card_width, card_height)),

    "(1, 2)": pygame.transform.scale(pygame.image.load("img/Heart/A.png"), (card_width, card_height)),
    "(2, 2)": pygame.transform.scale(pygame.image.load("img/Heart/2.png"), (card_width, card_height)),
    "(3, 2)": pygame.transform.scale(pygame.image.load("img/Heart/3.png"), (card_width, card_height)),
    "(4, 2)": pygame.transform.scale(pygame.image.load("img/Heart/4.png"), (card_width, card_height)),
    "(5, 2)": pygame.transform.scale(pygame.image.load("img/Heart/5.png"), (card_width, card_height)),
    "(6, 2)": pygame.transform.scale(pygame.image.load("img/Heart/6.png"), (card_width, card_height)),
    "(7, 2)": pygame.transform.scale(pygame.image.load("img/Heart/7.png"), (card_width, card_height)),
    "(8, 2)": pygame.transform.scale(pygame.image.load("img/Heart/8.png"), (card_width, card_height)),
    "(9, 2)": pygame.transform.scale(pygame.image.load("img/Heart/9.png"), (card_width, card_height)),
    "(10, 2)": pygame.transform.scale(pygame.image.load("img/Heart/10.png"), (card_width, card_height)),
    "(11, 2)": pygame.transform.scale(pygame.image.load("img/Heart/J.jpg"), (card_width, card_height)),
    "(12, 2)": pygame.transform.scale(pygame.image.load("img/Heart/Q.png"), (card_width, card_height)),
    "(13, 2)": pygame.transform.scale(pygame.image.load("img/Heart/K.png"), (card_width, card_height)),

    "(1, 1)": pygame.transform.scale(pygame.image.load("img/Spades/A.png"), (card_width, card_height)),
    "(2, 1)": pygame.transform.scale(pygame.image.load("img/Spades/2.png"), (card_width, card_height)),
    "(3, 1)": pygame.transform.scale(pygame.image.load("img/Spades/3.png"), (card_width, card_height)),
    "(4, 1)": pygame.transform.scale(pygame.image.load("img/Spades/4.png"), (card_width, card_height)),
    "(5, 1)": pygame.transform.scale(pygame.image.load("img/Spades/5.png"), (card_width, card_height)),
    "(6, 1)": pygame.transform.scale(pygame.image.load("img/Spades/6.png"), (card_width, card_height)),
    "(7, 1)": pygame.transform.scale(pygame.image.load("img/Spades/7.png"), (card_width, card_height)),
    "(8, 1)": pygame.transform.scale(pygame.image.load("img/Spades/8.png"), (card_width, card_height)),
    "(9, 1)": pygame.transform.scale(pygame.image.load("img/Spades/9.png"), (card_width, card_height)),
    "(10, 1)": pygame.transform.scale(pygame.image.load("img/Spades/10.png"), (card_width, card_height)),
    "(11, 1)": pygame.transform.scale(pygame.image.load("img/Spades/J.jpg"), (card_width, card_height)),
    "(12, 1)": pygame.transform.scale(pygame.image.load("img/Spades/Q.png"), (card_width, card_height)),
    "(13, 1)": pygame.transform.scale(pygame.image.load("img/Spades/K.png"), (card_width, card_height))
    # Add more card images here
}


# Create the deck and shuffle it
# deck = ["2C", "2D", "2H", "2S", "3C", "3D", "3H", "3S", "4C", "4D", "4H", "4S",
#         "5C", "5D", "5H", "5S", "6C", "6D", "6H", "6S", "7C", "7D", "7H", "7S",
#         "8C", "8D", "8H", "8S", "9C", "9D", "9H", "9S", "AC", "AD", "AH", "AS",
#         "JC", "JD", "JH", "JS", "KC", "KD", "KH", "KS", "QC", "QD", "QH", "QS"]
# random.shuffle(deck)

# Deal two cards to each player
# player_hand = [(1, 1), (2, 1)]
# cpu_hand = [deck.pop(), deck.pop()]


SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 1000
WINDOW_SIZE = (1300, 1000)
# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Poker Game")


def run_round2(screen, b1, b2, b3, b4, b5, input_box, input_text, player2_box, player1: Player.Player, player2: Player.Player) -> list[PokerGame]:
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

    player_hand = [str(card) for card in (game.player1_hand if type(turn_order[0]) == HumanPlayer else game.player2_hand)]

    while game.check_winner() is None:
        print(game.player2_moves, game.player1_moves)
        # print(f'{game.last_bet} {game.community_cards} {game.stage}')
        invested_initially = turn_order[game.turn].bet_this_round
        if isinstance(turn_order[game.turn], HumanPlayer):
            human_player = turn_order[game.turn]
            while not human_player.made_move:
                for event in pygame.event.get():
                    # user text input box
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            input_text += event.unicode

                    # if game.last_bet = 0, disable call and raise
                    # disable betting/check when last_bet != 0
                    # disable raise if the humanplayer.has_raised
                    # prevent from betting above balance
                    # display balance on screen


                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if a button was clicked
                        # WARNING: THIS SHOULD BE A RIGHT CLICK, not LEFT CLICK
                        if ((raise_button.is_clicked(event.pos) or bet_button.is_clicked(event.pos)) and (input_text != '' and input_text.isdigit())) or fold_button.is_clicked(event.pos) or call_button.is_clicked(event.pos) or check_button.is_clicked(event.pos):
                            print('BUTTON CLCICKED', game)
                            # reset has_moved
                            human_player.made_move = True
                            human_player.has_moved = True

                            print('human moves: ', human_moves)
                            print('cpu moves: ', cpu_moves)

                            # disable betting/check when last_bet != 0
                            # prevent from betting above balance
                            if bet_button.is_clicked(event.pos) and game.last_bet == 0 and int(input_text) <= human_player.balance:
                                if input_text == human_player.balance:
                                    print("ALL IN")
                                    move = human_player.move_all_in()
                                else:
                                    print("BET CLICKED")
                                    move = human_player.move_bet(int(input_text))

                            # disable betting/check when last_bet != 0
                            elif check_button.is_clicked(event.pos) and game.last_bet == 0:
                                print("Check last bet", game.last_bet, game.last_bet == 0)
                                move = human_player.move_check()

                            # if game.last_bet = 0, disable call and raise
                            elif call_button.is_clicked(event.pos) and game.last_bet != 0:
                                print("CALL")
                                last_bet = game.last_bet
                                move = human_player.move_call(last_bet)

                            # if game.last_bet = 0, disable call and raise
                            # disable raise if the humanplayer.has_raised
                            elif raise_button.is_clicked(event.pos) and game.last_bet != 0 and not human_player.has_raised and int(input_text) <= human_player.balance:
                                if input_text == human_player.balance:
                                    print("ALL-IN")
                                    move = human_player.move_all_in()
                                else:
                                    print("RAISED")
                                    move = human_player.move_raise(int(input_text))

                            elif fold_button.is_clicked(event.pos):
                                print("FOLDED")
                                move = human_player.move_fold()

                            else:
                                print("YOU CAN'T DO THAT")
                                human_player.made_move = False

                screen.fill(((0, 85, 0)))

                # Render the input box
                pygame.draw.rect(screen, (0, 0, 0), input_box, 2)

                # Set the background color of the input_box
                background_color = (255, 255, 255) # WHite
                pygame.draw.rect(screen, background_color, input_box)

                # Render the input text
                text_surface = font.render(input_text, True, (0, 0, 0))
                screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

                # Render description of the input text
                # Render the string
                text_surface = font.render("Type Bet/Raise Amount", True, (255, 255, 255))

                # Draw the text onto the screen
                screen.blit(text_surface, (input_box.x, input_box.y - 30))


                ### DISPLAYING CPU move
                # Define the player moves
                if type(turn_order[game.turn]) == HumanPlayer:
                    if game.turn == 0:
                        cpu_moves = game.player2_moves
                        human_moves = game.player1_moves
                    else:
                        cpu_moves = game.player1_moves
                        human_moves = game.player2_moves
                    # print('cpu: player2', game.player2_moves)
                    # print("Human: Player1 ", game.player1_moves)
                else:
                    if game.turn == 0:
                        cpu_moves = game.player1_moves
                        human_moves = game.player2_moves
                    else:
                        cpu_moves = game.player2_moves
                        human_moves = game.player1_moves
                    # print("cpu: player1 ", game.player1_moves)
                    # print("human: player2 ", game.player2_moves)



                # Define the text box properties
                text_box_width = 350
                text_box_height = len(cpu_moves) * font.get_linesize()
                text_box_x = 100
                text_box_y = 100
                text_box_color = (255, 255, 255) # White
                text_color = (0, 0, 0) # Black
                # Create the text box surface
                text_box_surface = pygame.Surface((text_box_width, text_box_height))
                text_box_surface.fill(text_box_color)
                # Draw the player moves onto the text box surface
                for i, mv in enumerate(cpu_moves):
                    display = 'test'
                    if mv[0] == 0:
                        display = "FOLD"
                    elif mv[0] == 1:
                        display = "CHECK"
                    elif mv[0] == 2:
                        display = "CALL"
                    elif mv[0] == 3:
                        display = "BET " + str(mv[1])
                    elif mv[0] == 4:
                        display = "RAISE " + str(mv[1])
                    elif mv[0] == 5:
                        display = "ALL IN"

                    text = font.render(display, True, text_color)
                    text_box_surface.blit(text, (0, i * font.get_linesize()))

                for i, mv in enumerate(human_moves):
                    display = 'test'
                    if mv[0] == 0:
                        display = "FOLD - human"
                    elif mv[0] == 1:
                        display = "CHECK - human"
                    elif mv[0] == 2:
                        display = "CALL - human"
                    elif mv[0] == 3:
                        display = "BET - human " + str(mv[1])
                    elif mv[0] == 4:
                        display = "RAISE - human " + str(mv[1])
                    elif mv[0] == 5:
                        display = "ALL IN - human"

                    text = font.render(display, True, text_color)
                    text_box_surface.blit(text, (150, i * font.get_linesize()))

                # RENDER Move History Description
                # Render the string with white font color
                text_surface_AI = font.render("AI", True, (255, 255, 255))
                text_surface_user = font.render("USER", True, (255, 255, 255))

                # Draw the text onto the screen
                screen.blit(text_surface_AI, (130, 70))
                screen.blit(text_surface_user, (280, 70))

                # # Draw the text box onto the screen
                screen.blit(text_box_surface, (text_box_x, text_box_y))


                # if game.last_bet = 0, disable call and raise
                # disable betting/check when last_bet != 0
                # disable raise if the humanplayer.has_raised
                # prevent from betting above balance
                # display balance on screen

                # raise_button = Button(350, 900, 100, 50, "Raise")
                # bet_button = Button(460, 900, 100, 50, "Bet")
                # fold_button = Button(570, 900, 100, 50, "Fold")
                # call_button = Button(680, 900, 100, 50, "Call")
                # check_button = Button(790, 900, 100, 50, "Check")
                if game.last_bet == 0:
                    raise_button.disabled = True
                    call_button.disabled = True
                    bet_button.disabled = False
                    check_button.disabled = False

                else:  # if game.last_bet != 0:
                    bet_button.disabled = True
                    check_button.disabled = True
                    raise_button.disabled = False
                    call_button.disabled = False

                if human_player.has_raised:
                    raise_button.disabled = True
                else:
                    raise_button.disabled = False


                # TODO: enable these


                # Draw the buttons
                b1.draw(screen)
                b2.draw(screen)
                b3.draw(screen)
                b4.draw(screen)
                b5.draw(screen)

                # Display the cards
                screen.blit(card_images[player_hand[0]], (500, 600))
                screen.blit(card_images[player_hand[1]], (550, 600))
                screen.blit(card_back, (500, 30))
                screen.blit(card_back, (550, 30))

                com_cards = [str(card) for card in game.community_cards]

                if com_cards:
                    for i in range(len(com_cards)):
                        screen.blit(card_images[com_cards[i]], (440 + i * 50, 310))
                # for i in range(len(game.community_cards), 5):
                #     screen.blit(card_back, (200 + i * 10, 100))

                # Render Player Balances
                # Create the box to display the string value
                box_color = (0, 0, 0)
                box_width = 500
                box_height = 100
                box_x = (1600 - box_width)
                box_y = 0
                box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

                # Render the string value
                balance_text = font.render("User: " + str(human_player.balance), True, (255, 255, 255))

                # Draw the box and the string value
                pygame.draw.rect(screen, box_color, box_rect)
                screen.blit(balance_text, (box_x + 20, box_y + 20))

                box_color = (0, 0, 0)
                box_width = 500
                box_height = 70
                box_x = (1600 - box_width)
                box_y = 50
                box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

                # Render the string value
                balance_text = font.render("AI: " + str(human_player.balance), True, (255, 255, 255))

                # Draw the box and the string value
                pygame.draw.rect(screen, box_color, box_rect)
                screen.blit(balance_text, (box_x + 20, box_y + 20))
                pygame.display.flip()
            human_player.made_move = False

        else:
            move = turn_order[game.turn].make_move(game, corresponding_hand[game.turn])
        # print(f'[{game.stage}] Player {game.turn + 1} {NUM_TO_ACTION[move[0]]}s{"" if move[0] in {Player.FOLD_CODE, Player.CHECK_CODE, Player.CALL_CODE, Player.ALL_IN_CODE} else " "+str(move[1])}')

        # print(move[1])
        game.run_move(move, move[1] - invested_initially if game.stage == 1 else -1)
        if (move[0] == Player.RAISE_CODE or (move[0] == Player.BET_CODE and move[1] > 0) or move[0] == Player.ALL_IN_CODE) and turn_order[game.turn].balance > 0:
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

    screen.fill((0, 0, 0))
    pygame.display.flip()

    # Display the user cards
    screen.blit(card_images[player_hand[0]], (500, 600))
    screen.blit(card_images[player_hand[1]], (550, 600))

    # Display the AI cards
    AI_cards = [str(card) for card in (game.player2_hand if type(turn_order[0]) == HumanPlayer else game.player1_hand)]
    screen.blit(card_images[AI_cards[0]], (500, 30))
    screen.blit(card_images[AI_cards[1]], (550, 30))
    # screen.blit(card_back, (500, 30))
    # screen.blit(card_back, (550, 30))

    com_cards = [str(card) for card in game.community_cards]

    if com_cards:
        for i in range(len(com_cards)):
            screen.blit(card_images[com_cards[i]], (440 + i * 50, 310))


    pygame.display.flip()
    sleep(5)

    screen.fill((0, 0, 0))

    if game.winner == 3:
        print("tie")
        text_surface = font.render('TIE!', True, (255, 255, 255))
        # Draw the text onto the screen
        screen.blit(text_surface, (600, 400))


    elif type(turn_order[game.winner - 1]) == HumanPlayer:
        print('winner: human', 'game.winner: ', game.winner, type(player1))

        index_of_winner = game.winner - 1
        if index_of_winner == 1:  # then AI player is in index 1 meaning player 2
            if len(game.player1_moves) == 1:
                text_surface = font.render('You Won Because the Opponent Folded!', True, (255, 255, 255))
                screen.blit(text_surface, (400, 400))
        else:
            text_surface = font.render('You Won!', True, (255, 255, 255))
            screen.blit(text_surface, (600, 400))

    else:
        print('winner: CPU', 'game.winner: ', game.winner, type(player1))
        text_surface = font.render('You Lost :(', True, (255, 255, 255))

        # Draw the text onto the screen
        screen.blit(text_surface, (600, 400))


    pygame.display.flip()
    sleep(5)

    raise_button.disabled = False
    bet_button.disabled = False
    fold_button.disabled = False
    call_button.disabled = False
    check_button.disabled = False

    return game_states_so_far

# Create the buttons
raise_button = Button(350, 900, 100, 50, "Raise")
bet_button = Button(460, 900, 100, 50, "Bet")
fold_button = Button(570, 900, 100, 50, "Fold")
call_button = Button(680, 900, 100, 50, "Call")
check_button = Button(790, 900, 100, 50, "Check")

# Set up the font
font = pygame.font.SysFont(None, 32)

# Set up the input box
input_box = pygame.Rect(900, 900, 250, 32)
input_text = ''
player2_box = pygame.Rect(900, 0, 200, 400)

clock = pygame.time.Clock()

# Set up the game loop
running = True
human = HumanPlayer(10000)
p2 = TreePlayer(10000, 'TreePlayer_20000.txt')
simulated_game = run_round2(screen, raise_button, bet_button, fold_button, call_button, check_button, input_box, input_text, player2_box, human, p2)[-1]

font = pygame.font.SysFont(None, 32)


# Quit Pygame
pygame.quit()

# bet & raise: user has to specify the quantity
# bet: first raise
# disable bet after raise
# call: only after bet or raise:
# checK: I don't wanna bet, just open card (only when the other player doesn't bet or raise) -> need to fold or raise after the bet

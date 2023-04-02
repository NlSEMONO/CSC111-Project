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

from GameRunner import NUM_TO_ACTION, run_round




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
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 32)

    def draw(self, surface):
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
    "AC": pygame.transform.scale(pygame.image.load("img/Clover/A.png"), (card_width, card_height)),
    "2C": pygame.transform.scale(pygame.image.load("img/Clover/2.png"), (card_width, card_height)),
    "3C": pygame.transform.scale(pygame.image.load("img/Clover/3.png"), (card_width, card_height)),
    "4C": pygame.transform.scale(pygame.image.load("img/Clover/4.webp"), (card_width, card_height)),
    "5C": pygame.transform.scale(pygame.image.load("img/Clover/5.png"), (card_width, card_height)),
    "6C": pygame.transform.scale(pygame.image.load("img/Clover/6.png"), (card_width, card_height)),
    "7C": pygame.transform.scale(pygame.image.load("img/Clover/7.png"), (card_width, card_height)),
    "8C": pygame.transform.scale(pygame.image.load("img/Clover/8.png"), (card_width, card_height)),
    "9C": pygame.transform.scale(pygame.image.load("img/Clover/9.png"), (card_width, card_height)),
    "10C": pygame.transform.scale(pygame.image.load("img/Clover/10.png"), (card_width, card_height)),
    "JC": pygame.transform.scale(pygame.image.load("img/Clover/J.jpeg"), (card_width, card_height)),
    "QC": pygame.transform.scale(pygame.image.load("img/Clover/Q.jpeg"), (card_width, card_height)),
    "KC": pygame.transform.scale(pygame.image.load("img/Clover/K.webp"), (card_width, card_height)),

    "AD": pygame.transform.scale(pygame.image.load("img/Diamond/A.png"), (card_width, card_height)),
    "2D": pygame.transform.scale(pygame.image.load("img/Diamond/2.png"), (card_width, card_height)),
    "3D": pygame.transform.scale(pygame.image.load("img/Diamond/3.png"), (card_width, card_height)),
    "4D": pygame.transform.scale(pygame.image.load("img/Diamond/4.png"), (card_width, card_height)),
    "5D": pygame.transform.scale(pygame.image.load("img/Diamond/5.png"), (card_width, card_height)),
    "6D": pygame.transform.scale(pygame.image.load("img/Diamond/6.png"), (card_width, card_height)),
    "7D": pygame.transform.scale(pygame.image.load("img/Diamond/7.png"), (card_width, card_height)),
    "8D": pygame.transform.scale(pygame.image.load("img/Diamond/8.png"), (card_width, card_height)),
    "9D": pygame.transform.scale(pygame.image.load("img/Diamond/9.png"), (card_width, card_height)),
    "10D": pygame.transform.scale(pygame.image.load("img/Diamond/10.png"), (card_width, card_height)),
    "JD": pygame.transform.scale(pygame.image.load("img/Diamond/J.jpeg"), (card_width, card_height)),
    "QD": pygame.transform.scale(pygame.image.load("img/Diamond/Q.png"), (card_width, card_height)),
    "KD": pygame.transform.scale(pygame.image.load("img/Diamond/K.png"), (card_width, card_height)),

    "AH": pygame.transform.scale(pygame.image.load("img/Heart/A.png"), (card_width, card_height)),
    "2H": pygame.transform.scale(pygame.image.load("img/Heart/2.png"), (card_width, card_height)),
    "3H": pygame.transform.scale(pygame.image.load("img/Heart/3.png"), (card_width, card_height)),
    "4H": pygame.transform.scale(pygame.image.load("img/Heart/4.png"), (card_width, card_height)),
    "5H": pygame.transform.scale(pygame.image.load("img/Heart/5.png"), (card_width, card_height)),
    "6H": pygame.transform.scale(pygame.image.load("img/Heart/6.png"), (card_width, card_height)),
    "7H": pygame.transform.scale(pygame.image.load("img/Heart/7.png"), (card_width, card_height)),
    "8H": pygame.transform.scale(pygame.image.load("img/Heart/8.png"), (card_width, card_height)),
    "9H": pygame.transform.scale(pygame.image.load("img/Heart/9.png"), (card_width, card_height)),
    "10H": pygame.transform.scale(pygame.image.load("img/Heart/10.png"), (card_width, card_height)),
    "JH": pygame.transform.scale(pygame.image.load("img/Heart/J.jpg"), (card_width, card_height)),
    "QH": pygame.transform.scale(pygame.image.load("img/Heart/Q.png"), (card_width, card_height)),
    "KH": pygame.transform.scale(pygame.image.load("img/Heart/K.png"), (card_width, card_height)),

    "AS": pygame.transform.scale(pygame.image.load("img/Spades/A.png"), (card_width, card_height)),
    "2S": pygame.transform.scale(pygame.image.load("img/Spades/2.png"), (card_width, card_height)),
    "3S": pygame.transform.scale(pygame.image.load("img/Spades/3.png"), (card_width, card_height)),
    "4S": pygame.transform.scale(pygame.image.load("img/Spades/4.png"), (card_width, card_height)),
    "5S": pygame.transform.scale(pygame.image.load("img/Spades/5.png"), (card_width, card_height)),
    "6S": pygame.transform.scale(pygame.image.load("img/Spades/6.png"), (card_width, card_height)),
    "7S": pygame.transform.scale(pygame.image.load("img/Spades/7.png"), (card_width, card_height)),
    "8S": pygame.transform.scale(pygame.image.load("img/Spades/8.png"), (card_width, card_height)),
    "9S": pygame.transform.scale(pygame.image.load("img/Spades/9.png"), (card_width, card_height)),
    "10S": pygame.transform.scale(pygame.image.load("img/Spades/10.png"), (card_width, card_height)),
    "JS": pygame.transform.scale(pygame.image.load("img/Spades/J.jpg"), (card_width, card_height)),
    "QS": pygame.transform.scale(pygame.image.load("img/Spades/Q.png"), (card_width, card_height)),
    "KS": pygame.transform.scale(pygame.image.load("img/Spades/K.png"), (card_width, card_height))
    # Add more card images here
}


# Create the deck and shuffle it
deck = ["2C", "2D", "2H", "2S", "3C", "3D", "3H", "3S", "4C", "4D", "4H", "4S",
        "5C", "5D", "5H", "5S", "6C", "6D", "6H", "6S", "7C", "7D", "7H", "7S",
        "8C", "8D", "8H", "8S", "9C", "9D", "9H", "9S", "AC", "AD", "AH", "AS",
        "JC", "JD", "JH", "JS", "KC", "KD", "KH", "KS", "QC", "QD", "QH", "QS"]
random.shuffle(deck)

# Deal two cards to each player
player_hand = [deck.pop(), deck.pop()]
cpu_hand = [deck.pop(), deck.pop()]


SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 1000
WINDOW_SIZE = (1300, 1000)
# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Poker Game")


def run_round2(screen, b1, b2, b3, b4, b5, input_box, player1: Player.Player, player2: Player.Player) -> list[PokerGame]:
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
        if isinstance(turn_order[game.turn], HumanPlayer): 
            human_player = turn_order[game.turn]
            while not human_player.made_move:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if a button was clicked
                        # WARNING: THIS SHOULD BE A RIGHT CLICK, not LEFT CLICK
                        if ((raise_button.is_clicked(event.pos) or bet_button.is_clicked(event.pos)) and (input_text != '' and input_text.isdigit())) or fold_button.is_clicked(event.pos) or call_button.is_clicked(event.pos) or check_button.is_clicked(event.pos):
                            print('test3', game)
                            # reset has_moved
                            human_player.made_move = True
                            human_player.has_moved = True

                            if human_player.move_button[0] == "bet": 
                                if human_player.move_button[1] == human_player.balance:
                                    move = human_player.move_all_in()
                                else:
                                    move = human_player.move_bet(human_player.move_button[1])

                            elif human_player.move_button[0] == "check":
                                move = human_player.move_check()

                            elif human_player.move_button[0] == "call":
                                last_bet = game.last_bet
                                move = human_player.move_call(last_bet)

                            elif human_player.move_button[0] == "raise": 
                                if human_player.move_button[1] == human_player.balance:
                                    move = human_player.move_all_in()
                                else:
                                    move = human_player.move_raise(human_player.move_button[1])

                            else: 
                                move = human_player.move_fold()
                
                human_player.made_move = False
                        
                # Render the input box
                pygame.draw.rect(screen, (0, 0, 0), input_box, 2)

                # Render the input text
                text_surface = font.render(input_text, True, (0, 0, 0))
                screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

                # Draw the buttons
                # TODO: change bet to raise after first bet 
                b1.draw(screen)
                b2.draw(screen)
                b3.draw(screen)
                b4.draw(screen)
                b5.draw(screen)

                # Display the cards
                screen.blit(card_images[player_hand[0]], (500, 500))
                screen.blit(card_images[player_hand[1]], (550, 500))
                screen.blit(card_back, (500, 30))
                screen.blit(card_back, (550, 30))
                
                pygame.display.flip()

        else:
            move = turn_order[game.turn].make_move(game, corresponding_hand[game.turn])
        # print(f'[{game.stage}] Player {game.turn + 1} {NUM_TO_ACTION[move[0]]}s{"" if move[0] in {Player.FOLD_CODE, Player.CHECK_CODE, Player.CALL_CODE, Player.ALL_IN_CODE} else " "+str(move[1])}')
        
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

        screen.fill(((0, 85, 0)))

        # Render the input box
        pygame.draw.rect(screen, (0, 0, 0), input_box, 2)

        # Render the input text
        text_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

        # Draw the buttons
        # TODO: change bet to raise after first bet 
        b1.draw(screen)
        b2.draw(screen)
        b3.draw(screen)
        b4.draw(screen)
        b5.draw(screen)

        # Display the cards
        screen.blit(card_images[player_hand[0]], (500, 500))
        screen.blit(card_images[player_hand[1]], (550, 500))
        screen.blit(card_back, (500, 30))
        screen.blit(card_back, (550, 30))
        
        pygame.display.flip()
    
    return game_states_so_far

# Create the buttons
raise_button = Button(310, 800, 100, 50, "Raise")
bet_button = Button(420, 800, 100, 50, "Bet")
fold_button = Button(530, 800, 100, 50, "Fold")
call_button = Button(640, 800, 100, 50, "Call")
check_button = Button(750, 800, 100, 50, "Check")

# Set up the font
font = pygame.font.SysFont(None, 32)

# Set up the input box
input_box = pygame.Rect(100, 100, 200, 32)
input_text = ''

clock = pygame.time.Clock()

# Set up the game loop
running = True
human = HumanPlayer(10000)
p2 = NaivePlayer(10000)
simulated_game = run_round2(screen, raise_button, bet_button, fold_button, call_button, check_button, input_box, human, p2)[-1]

font = pygame.font.SysFont(None, 32)





while running:
    print('testtttttt123123123')
    # Handle event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # user text input box
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode
            print(input_text)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a button was clicked
            # WARNING: THIS SHOULD BE A RIGHT CLICK, not LEFT CLICK
            if raise_button.is_clicked(event.pos):
                # Handle raise button click
                if input_text != '' and input_text.isdigit():
                    # Handle raise button click
                    human.move_button = ("raise", int(input_text))
                    print(human.move_button)
                    human.has_moved = True
                
            elif bet_button.is_clicked(event.pos):
                # Handle bet button click
                if input_text != '' and input_text.isdigit():
                    # Handle raise button click
                    human.move_button = ("bet", int(input_text))
                    print(human.move_button)
                    human.has_moved = True

            elif fold_button.is_clicked(event.pos):
                # Handle fold button click
                human.move_button = ("fold", 0)
                print(human.move_button)
                print('test')
                human.has_moved = True

            elif call_button.is_clicked(event.pos):
                # Handle fold button click
                human.move_button = ("call", 0)
                print(human.move_button)
                human.has_moved = True
            
            elif check_button.is_clicked(event.pos):
                # Handle fold button click
                human.move_button = ("check", 0)
                print(human.move_button)
                human.has_moved = True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            else:
                user_input += event.unicode
                



    # Draw the screen
    # screen.fill(bg_color)
    # Draw the cards, chips, and other game elements here

    # Clear the screen
    screen.fill((0, 85, 0))

    # Render the input box
    pygame.draw.rect(screen, (0, 0, 0), input_box, 2)
    
    # Render the input text
    text_surface = font.render(input_text, True, (0, 0, 0))
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    # Draw the buttons
    # TODO: change bet to raise after first bet 
    raise_button.draw(screen)
    bet_button.draw(screen)
    fold_button.draw(screen)
    call_button.draw(screen)
    check_button.draw(screen)

    # Display the cards
    screen.blit(card_images[player_hand[0]], (500, 500))
    screen.blit(card_images[player_hand[1]], (550, 500))
    screen.blit(card_back, (500, 30))
    screen.blit(card_back, (550, 30))

    # Update the screen
    # pygame.display.update()
    # TODO: Display the community cards (smaller than user cards)
    # game.community_cards (after each turn)

    # pygame.display.flip()

    # Update the game display
    pygame.display.flip()
    # clock.tick(30)

# Quit Pygame
pygame.quit()

# bet & raise: user has to specify the quantity 
# bet: first raise 
# disable bet after raise 
# call: only after bet or raise: 
# checK: I don't wanna bet, just open card (only when the other player doesn't bet or raise) -> need to fold or raise after the bet

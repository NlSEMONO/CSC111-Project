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
from Player import Player
from PokerGame import PokerGame
from NaivePlayer import NaivePlayer

<<<<<<< HEAD
=======
from GameRunner import NUM_TO_ACTION, run_round
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f


class HumanPlayer(Player):
    """
    Abstract class representing a human player
        move_button: (name of the move, bet or raise amount if the move is a bet or raise otherwise 0)
<<<<<<< HEAD
    """
    move_button: tuple[str, int]

    # if not fold & check code => bet amount
    def __init__(self, move_button: tuple[str, int] = ('None', 0)) -> None:
        super(HumanPlayer).__init__(Player)
        # modify this attribute every turn that user presses a button
        self.move_button = move_button

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        """
        Always checks if there is no bet, and will fold otherwise
        Will always bet on first turn
        """
        self.has_moved = True
=======
        made_move: whether or not the user has made a move in each stage
    """
    move_button: tuple[str, int]
    made_move: bool

    # if not fold & check code => bet amount
    def __init__(self, balance: int, move_button: tuple[str, int] = ('None', 0), made_move: bool = False) -> None:
        Player.__init__(self, balance)
        # modify this attribute every stage that user presses a button
        self.move_button = move_button

    def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
        # wait until user makes a move (presses a button) in each turn
        while not self.has_moved:
            print('test3')
        # reset has_moved
        self.has_moved = False

>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f
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

<<<<<<< HEAD
# Load card images
card_back = pygame.transform.scale(pygame.image.load("img/card_back.png"), (200, 300))
# Load card images and scale them
card_images = {
    "AC": pygame.transform.scale(pygame.image.load("img/Clover/A.png"), (200, 300)),
    "2C": pygame.transform.scale(pygame.image.load("img/Clover/2.png"), (200, 300)),
    "3C": pygame.transform.scale(pygame.image.load("img/Clover/3.png"), (200, 300)),
    "4C": pygame.transform.scale(pygame.image.load("img/Clover/4.webp"), (200, 300)),
    "5C": pygame.transform.scale(pygame.image.load("img/Clover/5.png"), (200, 300)),
    "6C": pygame.transform.scale(pygame.image.load("img/Clover/6.png"), (200, 300)),
    "7C": pygame.transform.scale(pygame.image.load("img/Clover/7.png"), (200, 300)),
    "8C": pygame.transform.scale(pygame.image.load("img/Clover/8.png"), (200, 300)),
    "9C": pygame.transform.scale(pygame.image.load("img/Clover/9.png"), (200, 300)),
    "10C": pygame.transform.scale(pygame.image.load("img/Clover/10.png"), (200, 300)),
    "JC": pygame.transform.scale(pygame.image.load("img/Clover/J.jpeg"), (200, 300)),
    "QC": pygame.transform.scale(pygame.image.load("img/Clover/Q.jpeg"), (200, 300)),
    "KC": pygame.transform.scale(pygame.image.load("img/Clover/K.webp"), (200, 300)),

    "AD": pygame.transform.scale(pygame.image.load("img/Diamond/A.png"), (200, 300)),
    "2D": pygame.transform.scale(pygame.image.load("img/Diamond/2.png"), (200, 300)),
    "3D": pygame.transform.scale(pygame.image.load("img/Diamond/3.png"), (200, 300)),
    "4D": pygame.transform.scale(pygame.image.load("img/Diamond/4.png"), (200, 300)),
    "5D": pygame.transform.scale(pygame.image.load("img/Diamond/5.png"), (200, 300)),
    "6D": pygame.transform.scale(pygame.image.load("img/Diamond/6.png"), (200, 300)),
    "7D": pygame.transform.scale(pygame.image.load("img/Diamond/7.png"), (200, 300)),
    "8D": pygame.transform.scale(pygame.image.load("img/Diamond/8.png"), (200, 300)),
    "9D": pygame.transform.scale(pygame.image.load("img/Diamond/9.png"), (200, 300)),
    "10D": pygame.transform.scale(pygame.image.load("img/Diamond/10.png"), (200, 300)),
    "JD": pygame.transform.scale(pygame.image.load("img/Diamond/J.jpeg"), (200, 300)),
    "QD": pygame.transform.scale(pygame.image.load("img/Diamond/Q.png"), (200, 300)),
    "KD": pygame.transform.scale(pygame.image.load("img/Diamond/K.png"), (200, 300)),

    "AH": pygame.transform.scale(pygame.image.load("img/Heart/A.png"), (200, 300)),
    "2H": pygame.transform.scale(pygame.image.load("img/Heart/2.png"), (200, 300)),
    "3H": pygame.transform.scale(pygame.image.load("img/Heart/3.png"), (200, 300)),
    "4H": pygame.transform.scale(pygame.image.load("img/Heart/4.png"), (200, 300)),
    "5H": pygame.transform.scale(pygame.image.load("img/Heart/5.png"), (200, 300)),
    "6H": pygame.transform.scale(pygame.image.load("img/Heart/6.png"), (200, 300)),
    "7H": pygame.transform.scale(pygame.image.load("img/Heart/7.png"), (200, 300)),
    "8H": pygame.transform.scale(pygame.image.load("img/Heart/8.png"), (200, 300)),
    "9H": pygame.transform.scale(pygame.image.load("img/Heart/9.png"), (200, 300)),
    "10H": pygame.transform.scale(pygame.image.load("img/Heart/10.png"), (200, 300)),
    "JH": pygame.transform.scale(pygame.image.load("img/Heart/J.jpg"), (200, 300)),
    "QH": pygame.transform.scale(pygame.image.load("img/Heart/Q.png"), (200, 300)),
    "KH": pygame.transform.scale(pygame.image.load("img/Heart/K.png"), (200, 300)),

    "AS": pygame.transform.scale(pygame.image.load("img/Spades/A.png"), (200, 300)),
    "2S": pygame.transform.scale(pygame.image.load("img/Spades/2.png"), (200, 300)),
    "3S": pygame.transform.scale(pygame.image.load("img/Spades/3.png"), (200, 300)),
    "4S": pygame.transform.scale(pygame.image.load("img/Spades/4.png"), (200, 300)),
    "5S": pygame.transform.scale(pygame.image.load("img/Spades/5.png"), (200, 300)),
    "6S": pygame.transform.scale(pygame.image.load("img/Spades/6.png"), (200, 300)),
    "7S": pygame.transform.scale(pygame.image.load("img/Spades/7.png"), (200, 300)),
    "8S": pygame.transform.scale(pygame.image.load("img/Spades/8.png"), (200, 300)),
    "9S": pygame.transform.scale(pygame.image.load("img/Spades/9.png"), (200, 300)),
    "10S": pygame.transform.scale(pygame.image.load("img/Spades/10.png"), (200, 300)),
    "JS": pygame.transform.scale(pygame.image.load("img/Spades/J.jpg"), (200, 300)),
    "QS": pygame.transform.scale(pygame.image.load("img/Spades/Q.png"), (200, 300)),
    "KS": pygame.transform.scale(pygame.image.load("img/Spades/K.png"), (200, 300)),
    # Add more card images here
}
=======
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f

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

<<<<<<< HEAD
=======
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


>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f
# Create the deck and shuffle it
deck = ["2C", "2D", "2H", "2S", "3C", "3D", "3H", "3S", "4C", "4D", "4H", "4S",
        "5C", "5D", "5H", "5S", "6C", "6D", "6H", "6S", "7C", "7D", "7H", "7S",
        "8C", "8D", "8H", "8S", "9C", "9D", "9H", "9S", "AC", "AD", "AH", "AS",
        "JC", "JD", "JH", "JS", "KC", "KD", "KH", "KS", "QC", "QD", "QH", "QS"]
random.shuffle(deck)

# Deal two cards to each player
player_hand = [deck.pop(), deck.pop()]
cpu_hand = [deck.pop(), deck.pop()]


<<<<<<< HEAD

SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 1300
WINDOW_SIZE = (2000, 1300)
=======
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 1000
WINDOW_SIZE = (1300, 1000)
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f
# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Poker Game")


<<<<<<< HEAD
# Set the colors for the gradient
GREEN_CENTER = (0, 255, 0)
DARK_GREEN_OUTER = (0, 128, 0)
BLACK = (0, 0, 0)

# Set the center and radius of the gradient
CENTER = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
RADIUS = min(CENTER)

# Draw the gradient
for y in range(WINDOW_SIZE[1]):
    for x in range(WINDOW_SIZE[0]):
        distance = ((x - CENTER[0]) ** 2 + (y - CENTER[1]) ** 2) ** 0.5
        if distance > RADIUS:
            color = BLACK
        else:
            color = pygame.Color(*GREEN_CENTER).lerp(DARK_GREEN_OUTER, distance / RADIUS)
        pygame.gfxdraw.pixel(screen, x, y, color)

# Update the Pygame display
# pygame.display.flip()

# Set up the game loop
running = True
human = HumanPlayer()
=======
# Set up the game loop
running = True
human = HumanPlayer(10000)
p2 = NaivePlayer(10000)
# simulated_game = run_round(human, p2)[-1]
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f

font = pygame.font.SysFont(None, 32)

# Create the buttons
<<<<<<< HEAD
raise_button = Button(510, 1000, 100, 50, "Raise")
bet_button = Button(620, 1000, 100, 50, "Bet")
fold_button = Button(730, 1000, 100, 50, "Fold")

user_input = ''
base_font = pygame.font.Font(None, 32)
=======
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
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f

while running:
    # Handle event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
<<<<<<< HEAD
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a button was clicked
            if raise_button.is_clicked(event.pos):
                # Handle raise button click
                user_input = pygame.prompt("Enter your raise amount:")
                if user_input is not None and user_input.isdigit():
                    # Handle raise button click
                    human.move_button = ("raise", int(user_input))
                    print(human.move_button)

                human.move_button = ("raise", user_input)
                print(human.move_button)
                
            elif bet_button.is_clicked(event.pos):
                # Handle bet button click
                user_input = pygame.prompt("Enter your bet amount:")
                if user_input is not None and user_input.isdigit():
                    # Handle bet button click
                    human.move_button = ("bet", int(user_input))
                    print(human.move_button)

                human.move_button = ("bet", user_input)
                print(human.move_button)
=======
        
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
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f

            elif fold_button.is_clicked(event.pos):
                # Handle fold button click
                human.move_button = ("fold", 0)
                print(human.move_button)
<<<<<<< HEAD
=======
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
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            else:
                user_input += event.unicode
                



    # Draw the screen
    # screen.fill(bg_color)
    # Draw the cards, chips, and other game elements here

<<<<<<< HEAD
=======
    # Clear the screen
    screen.fill(((0, 85, 0)))

    # Render the input box
    pygame.draw.rect(screen, (0, 0, 0), input_box, 2)
    
    # Render the input text
    text_surface = font.render(input_text, True, (0, 0, 0))
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f
    # Draw the buttons
    # TODO: change bet to raise after first bet 
    raise_button.draw(screen)
    bet_button.draw(screen)
    fold_button.draw(screen)
<<<<<<< HEAD
=======
    call_button.draw(screen)
    check_button.draw(screen)
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f

    # Display the cards
    screen.blit(card_images[player_hand[0]], (500, 500))
    screen.blit(card_images[player_hand[1]], (550, 500))
<<<<<<< HEAD
    screen.blit(card_back, (800, 100))
    screen.blit(card_back, (850, 100))

    # Draw the prompt text
    text_surface = base_font.render(user_input, True, (255, 255, 255))
    screen.blit(text_surface, (0, 0))

    # Update the screen
    # pygame.display.update()
    # TODO: Display the community cards
=======
    screen.blit(card_back, (500, 30))
    screen.blit(card_back, (550, 30))

    # Update the screen
    # pygame.display.update()
    # TODO: Display the community cards (smaller than user cards)
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f
    # game.community_cards (after each turn)

    # pygame.display.flip()

    # Update the game display
    pygame.display.flip()
<<<<<<< HEAD
=======
    clock.tick(30)
>>>>>>> c546d8369a895b1fb11c95739efdcf3cf25ef27f

# Quit Pygame
pygame.quit()

# bet & raise: user has to specify the quantity 
# bet: first raise 
# disable bet after raise 
# call: only after bet or raise: 
# checK: I don't wanna bet, just open card (only when the other player doesn't bet or raise) -> need to fold or raise after the bet

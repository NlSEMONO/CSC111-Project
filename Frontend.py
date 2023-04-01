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

# class HumanPlayer(Player):
#     """
#     Abstract class representing a human player
#         move_button: (name of the move, bet or raise amount if the move is a bet or raise otherwise 0)
#     """
#     move_button: tuple[str, int]

#     # if not fold & check code => bet amount
#     def __init__(self, move_button: tuple[str, int]) -> None:
#         super().__init__()
#         # modify this attribute every turn that user presses a button
#         self.move_button = move_button

#     def make_move(self, game_state: PokerGame, player_num: int) -> tuple[int, int]:
#         """
#         Always checks if there is no bet, and will fold otherwise

#         Will always bet on first turn
#         """

        # self.has_moved = True
        # if game_state.stage == 1 and self.bet_this_round == 0 and game_state.last_bet == 0:
        #     return self.move_bet(1)
        # elif game_state.stage == 1 and self.bet_this_round == 0:
        #     return self.move_call(game_state.last_bet)
        # elif game_state.last_bet > 0:
        #     return self.move_fold()
        # else:
        #     return self.move_check()

    
        
    



    # if {button press on bet button}: 
    #     return self.move_bet(bet_amount)
    # if {button press on check button}: 
    #     return self.move_check()
    # if {button press on bet button}: 
    #     return self.move_bet(bet_amount)
    # if {button press on check button}: 
    #     return self.move_check()
    # if {button press on bet button}: 
    #     return self.move_bet(bet_amount)
    # if {button press on check button}: 
    #     return self.move_check()



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

# Create the deck and shuffle it
deck = ["2C", "2D", "2H", "2S", "3C", "3D", "3H", "3S", "4C", "4D", "4H", "4S",
        "5C", "5D", "5H", "5S", "6C", "6D", "6H", "6S", "7C", "7D", "7H", "7S",
        "8C", "8D", "8H", "8S", "9C", "9D", "9H", "9S", "AC", "AD", "AH", "AS",
        "JC", "JD", "JH", "JS", "KC", "KD", "KH", "KS", "QC", "QD", "QH", "QS"]
random.shuffle(deck)

# Deal two cards to each player
player_hand = [deck.pop(), deck.pop()]
cpu_hand = [deck.pop(), deck.pop()]

# Create the buttons
raise_button = Button(510, 1000, 100, 50, "Raise")
bet_button = Button(620, 1000, 100, 50, "Bet")
fold_button = Button(730, 1000, 100, 50, "Fold")

SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 1300
WINDOW_SIZE = (2000, 1300)
# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Poker Game")


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
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a button was clicked
            if raise_button.is_clicked(event.pos):
                # Handle raise button click
                pass
            elif bet_button.is_clicked(event.pos):
                # Handle bet button click
                pass
            elif fold_button.is_clicked(event.pos):
                # Handle fold button click
                pass

    # Draw the screen
    # screen.fill(bg_color)
    # Draw the cards, chips, and other game elements here

    # Draw the buttons
    raise_button.draw(screen)
    bet_button.draw(screen)
    fold_button.draw(screen)

    # Display the cards
    screen.blit(card_images[player_hand[0]], (500, 500))
    screen.blit(card_images[player_hand[1]], (550, 500))
    screen.blit(card_back, (800, 100))
    screen.blit(card_back, (850, 100))

    # Display the community cards
    # game.community_cards (after each turn)

    # pygame.display.flip()

    # Update the game display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

# bet & raise: user has to specify the quantity 
# bet: first raise 
# disable bet after raise 
# call: only after bet or raise: 
# checK: I don't wanna bet, just open card (only when the other player doesn't bet or raise) -> need to fold or raise after the bet

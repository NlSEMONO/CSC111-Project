"""
DeepPoker Project

File that runs the UI
"""
import pygame
import FrontendTools
from pygame.colordict import THECOLORS

TEST_SIZE = (800, 800)

pygame.display.init()
pygame.font.init()
screen = pygame.display.set_mode(TEST_SIZE)
screen.fill(THECOLORS['white'])
pygame.display.flip()

pygame.event.clear()
pygame.event.set_blocked(None)
pygame.event.set_allowed([pygame.QUIT])

FrontendTools.wait_for_quit()

"""
DeepPoker Project

File for helper functions to be used in creating the UI
"""
import pygame


def wait_for_quit() -> None:
    """
    Wait until user closes the pygame window.
    """
    pygame.event.clear()
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(pygame.QUIT)
    pygame.event.wait()
    pygame.quit()

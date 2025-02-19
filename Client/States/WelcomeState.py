import pygame

from BaseState import BaseState


class WelcomeState(BaseState):
    def __init__(self, screen: pygame.Surface):
        """
        A state of the gui, a specific screen (one "page").
        """
        super().__init__(screen)

    def __init_vars(self, *args, **kwargs) -> None:
        pass
    
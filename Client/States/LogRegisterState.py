from BaseState import BaseState
import pygame

class LogRegister(BaseState):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)

    def __init_vars(self, *args, **kwargs) -> None:
        pass

    def update(self, dt: float, events: list, *args, **kwargs):
        pass

    def render(self, *args, **kwargs):
        pass

import pygame

from Client.States.BaseState import BaseState
from Client.Components.Text import Text
from Client.Components.Button import Button
from Client.Components.TextBox import TextBox
from Client.client import ClientSocket


class InLobby(BaseState):
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        super().__init__(screen, client)
        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        pass

    def update(self, dt: float, events: list, *args, **kwargs):
        pass

    def render(self, *args, **kwargs):
        pass

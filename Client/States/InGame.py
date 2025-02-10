import pygame
import os

from Client.States.BaseState import BaseState
from Client.client import ClientSocket
from Client.Components.SudokuBoard import SudokuBoard


class InGame(BaseState):
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        super().__init__(screen, client)
        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        self.puzzle = self.client.get_data("Lobby_Board")
        self.board = SudokuBoard(self.screen, self.puzzle)

    def update(self, dt: float, events: list, *args, **kwargs):
        self.board.update(dt, events)

    def render(self, *args, **kwargs):
        self.board.render()

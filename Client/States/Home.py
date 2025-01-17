import pygame

from Client.States.BaseState import BaseState
from Client.Components.Text import Text
from Client.Components.Button import Button
from Client.Components.TextBox import TextBox
from Client.client import ClientSocket


class Home(BaseState):
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        super().__init__(screen, client)
        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        self.title = Text("Competitive Sudoku", "Poppins", 24, True, pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 5), (255, 255, 255))
        self.lobby_code = TextBox(pygame.Vector2(self.screen.get_width() / 4, 60), pygame.Vector2(self.screen.get_width() / 3, 3.5 * self.screen.get_height() / 7), (226, 226, 226), "Enter Lobby Code", "Poppins", 16, (30, 30, 30), padding_left=20, padding_right=20, border_radius=10, hidden=True)

    def update(self, dt: float, events: list, *args, **kwargs):
        # self.lobby_code.update()
        self.lobby_code.update(dt, events)

    def render(self, *args, **kwargs):
        self.title.render(self.screen)
        self.lobby_code.render(self.screen)

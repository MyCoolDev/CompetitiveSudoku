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
        self.title = Text("Competitive Sudoku", "SemiBold", 24, pygame.Vector2(self.screen.get_width() / 2, 1 * self.screen.get_height() / 7), (255, 255, 255))
        self.lobby_code = TextBox(pygame.Vector2(self.screen.get_width() / 4, 60), pygame.Vector2((self.screen.get_width() / 2 - 10) / 2, 5 * self.screen.get_height() / 7), (226, 226, 226), "Enter Lobby Code", "Light", 16, (30, 30, 30), padding_left=20, padding_right=20, border_radius=10)
        self.join_lobby_button = Button(pygame.Vector2(self.screen.get_width() / 5, 60), pygame.Vector2(self.screen.get_width() / 2 + 10, 5 * self.screen.get_height() / 7), (129, 129, 129), "Join Lobby", "Bold", 16, (226, 226, 226), top_left_mode=True, border_radius=10)
        self.create_lobby_button = Button(pygame.Vector2(self.screen.get_width() / 3.5, 60), pygame.Vector2(self.screen.get_width() / 2, 6 * self.screen.get_height() / 7), (36, 123, 255), "Create Lobby", "Bold", 16, (226, 226, 226), border_radius=10)

    def update(self, dt: float, events: list, *args, **kwargs):
        self.lobby_code.update(dt, events)

        if self.create_lobby_button.update(dt, events):
            self.create_lobby()

    def create_lobby(self):
        response = self.client.send_request("Create_Lobby", {})
        if response["StatusCode"] == 201:
            print("Lobby created successfully")

        self.client.set_data("lobby_info", response["Data"]["Lobby_Info"])

    def render(self, *args, **kwargs):
        self.title.render(self.screen)
        self.lobby_code.render(self.screen)
        self.join_lobby_button.render(self.screen)
        self.create_lobby_button.render(self.screen)

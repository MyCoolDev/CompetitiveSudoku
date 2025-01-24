import pygame

from Client.States.BaseState import BaseState
from Client.Components.Text import Text
from Client.Components.Button import Button
from Client.Components.TextBox import TextBox
from Client.Components.Image import Image
from Client.Components.MonoBehaviour import MonoBehaviour
from Client.client import ClientSocket

import os


class InLobby(BaseState):
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        super().__init__(screen, client)
        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        self.data = self.client.get_data('lobby_info')
        self.navbar = MonoBehaviour(pygame.Vector2(127, 45), pygame.Vector2(40, 40), (2, 2, 2), border_radius=10)
        self.menu_icon = Image(os.path.join("Images", "Menu.png"), pygame.Vector2(24, 24), pygame.Vector2(self.navbar.position.x + 20, self.navbar.position.y + 10))
        self.friend_icon = Image(os.path.join("Images", "Person.png"), pygame.Vector2(20, 20), self.menu_icon.position + pygame.Vector2(24 + 20, 3))
        self.title = Text(f"{self.data['owner']}'s Lobby", "SemiBold", 24, pygame.Vector2(80, 133), (255, 255, 255), top_left_mode=True)
        self.number_of_players = Text(f"{len(self.data['players'])} / {self.data['max_players']} Players", "Regular", 24, self.title.position + pygame.Vector2(0, self.title.text_surface.get_size()[1] + 30), (226, 226, 226), top_left_mode=True)
        self.left_image = Image(os.path.join("Images", "LobbyImage.png"), pygame.Vector2(1234, 1080), pygame.Vector2(self.screen.get_width() - 1234, 0))

    def update(self, dt: float, events: list, *args, **kwargs):
        pass

    def render(self, *args, **kwargs):
        self.navbar.render(self.screen)
        self.menu_icon.render(self.screen)
        self.friend_icon.render(self.screen)
        self.left_image.render(self.screen)
        self.title.render(self.screen)
        self.number_of_players.render(self.screen)
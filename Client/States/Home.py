import os
import math

import pygame

from Client.Components.Button import Button
from Client.Components.FriendList import FriendList
from Client.Components.Image import Image
from Client.Components.MonoBehaviour import MonoBehaviour
from Client.Components.Text import Text
from Client.Components.TextBox import TextBox
from Client.States.BaseState import BaseState
from Client.client import ClientSocket
from Client.lobby import Lobby


class Home(BaseState):
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        super().__init__(screen, client)

        # change the screen name
        self.light_circles = None
        pygame.display.set_caption("Competitive Sudoku - Home - " + self.client.get_data("username"))

        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        self.title = Text("Competitive Sudoku", "SemiBold", 24, pygame.Vector2(self.screen.get_width() / 2, 1 * self.screen.get_height() / 7), (255, 255, 255))
        self.lobby_code = TextBox(pygame.Vector2(self.screen.get_width() / 4, 60), pygame.Vector2((self.screen.get_width() / 2 - 10) / 2, 5 * self.screen.get_height() / 7), (226, 226, 226), "Enter Lobby Code", "Light", 16, (30, 30, 30), padding_left=20, padding_right=20, border_radius=10)
        self.join_lobby_button = Button(pygame.Vector2(self.screen.get_width() / 5, 60), pygame.Vector2(self.screen.get_width() / 2 + 10, 5 * self.screen.get_height() / 7), (129, 129, 129), "Join Lobby", "Bold", 16, (226, 226, 226), top_left_mode=True, border_radius=10)
        self.create_lobby_button = Button(pygame.Vector2(self.screen.get_width() / 3.5, 60), pygame.Vector2(self.screen.get_width() / 2, 6 * self.screen.get_height() / 7), (36, 123, 255), "Create Lobby", "Bold", 16, (226, 226, 226), border_radius=10)
        self.navbar = MonoBehaviour(pygame.Vector2(127, 45), pygame.Vector2(40, 40), (2, 2, 2), border_radius=10)
        self.menu_icon = Image(os.path.join("Images", "Menu.png"), pygame.Vector2(24, 24), pygame.Vector2(self.navbar.position.x + 20, self.navbar.position.y + 10))
        self.friend_icon = Image(os.path.join("Images", "Person.png"), pygame.Vector2(20, 20), self.menu_icon.position + pygame.Vector2(24 + 20, 3))
        self.friend_list = FriendList(self.screen, self.client, self.mouse_cursor)

        self.mouse_cursor["IBEAM"] = [self.lobby_code]
        self.mouse_cursor["HAND"] = [self.menu_icon, self.join_lobby_button, self.create_lobby_button]

        self.timer = 0
        self.radius = 100
        self.start_x = (self.screen.get_width()) / 2
        self.start_y = self.screen.get_height() / 2 - 100
        self.light_circles = []
        self.light_circle_radius = 5
        self.animation_durations = 4
        self.animation_circle_duration = 2

    def update(self, dt: float, events: list, *args, **kwargs):
        self.timer += dt
        super().update(dt, events, *args, **kwargs)
        self.lobby_code.update(dt, events)
        self.friend_list.update(dt, events)

        if self.menu_icon.update(events):
            self.friend_list.toggle()

        if self.create_lobby_button.update(dt, events):
            self.create_lobby()

        if self.join_lobby_button.update(dt, events) and not self.lobby_code.is_default_content_presented and len(self.lobby_code.content) == 6:
            self.join_lobby()

        self.light_circles = [(self.radius * math.cos(
            math.radians(self.timer / self.animation_circle_duration * 360 + 20 * i)) + self.start_x,
                               self.radius * math.sin(math.radians(
                                   self.timer / self.animation_circle_duration * 360 + (20 + (
                                               self.timer) * 10) * i)) + self.start_y)
                              for i in range(5)]

    def create_lobby(self):
        response = self.client.send_request("Create_Lobby", {})
        if response["StatusCode"] == 201:
            print("Lobby created successfully")
            self.client.lobby = Lobby.from_dict(response["Data"]["Lobby_Info"], "players")

    def join_lobby(self):
        response = self.client.send_request("Join_Lobby", {"Code": self.lobby_code.content})
        if response["StatusCode"] == 200:
            print("Lobby joined successfully")
            self.client.lobby = Lobby.from_dict(response["Data"]["Lobby_Info"], response["Data"]["Role"])

    def render(self, *args, **kwargs):
        self.title.render(self.screen)
        self.lobby_code.render(self.screen)
        self.join_lobby_button.render(self.screen)
        self.create_lobby_button.render(self.screen)
        self.navbar.render(self.screen)
        self.menu_icon.render(self.screen)
        self.friend_icon.render(self.screen)
        self.friend_list.render()
        super().render()

        for light_circle in self.light_circles:
            pygame.draw.circle(self.screen, (255, 255, 255), (int(light_circle[0]), int(light_circle[1])), self.light_circle_radius)

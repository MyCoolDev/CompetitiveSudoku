import pygame

from Client.Components.Button import Button
from Client.Components.MonoBehaviour import MonoBehaviour
from Client.Components.Text import Text
from Client.Components.TextBox import TextBox
from Client.States.BaseState import BaseState
from Client.client import ClientSocket


class LogRegister(BaseState):
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        super().__init__(screen, client)

        # change the screen name
        pygame.display.set_caption("Competitive Sudoku - Login / Register")

        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        self.title = Text("Login Or Register", "SemiBold", 60, pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 6), (255, 255, 255), center_mode=True)
        self.password_textbox = TextBox(pygame.Vector2(self.screen.get_width() / 3, 60), pygame.Vector2(self.screen.get_width() / 3, 3.5 * self.screen.get_height() / 7), (46, 46, 46), "Enter Password", "Light", 16, (193, 193, 193), padding_left=20, padding_right=20, border_radius=25, hidden=True)
        self.password_textbox_border = MonoBehaviour(pygame.Vector2((self.screen.get_width() / 3) + (2 * 2), 60 + (2 * 2)), pygame.Vector2((self.screen.get_width() / 3) - 2, (3.5 * self.screen.get_height() / 7) - 2), (193, 193, 193), border_radius=25)
        self.username_textbox = TextBox(pygame.Vector2(self.screen.get_width() / 3, 60), pygame.Vector2(self.screen.get_width() / 3, 2.5 * self.screen.get_height() / 7), (46, 46, 46), "Enter Username", "Light", 16, (193, 193, 193), padding_left=20, padding_right=20, border_radius=25, next_input=self.password_textbox)
        self.username_textbox_border = MonoBehaviour(pygame.Vector2((self.screen.get_width() / 3) + (2 * 2), 60 + (2 * 2)), pygame.Vector2((self.screen.get_width() / 3) - 2, (2.5 * self.screen.get_height() / 7) - 2), (193, 193, 193), border_radius=25)
        self.login = Button(pygame.Vector2(self.screen.get_width() / 5, 60), pygame.Vector2((self.screen.get_width() - self.screen.get_width() / 5) / 2 - 10, 5.2 * self.screen.get_height() / 7), (65, 129, 204), "Login", "SemiBold", 16, (226, 226, 226), border_radius=15)
        self.register = Button(pygame.Vector2(self.screen.get_width() / 5, 60), pygame.Vector2((self.screen.get_width() + self.screen.get_width() / 5) / 2 + 10, 5.2 * self.screen.get_height() / 7), (129, 129, 129), "Register", "SemiBold", 16, (226, 226, 226), border_radius=15)

        self.mouse_cursor["IBEAM"] = [self.username_textbox, self.password_textbox]
        self.mouse_cursor["HAND"] = [self.login, self.register]

    def update(self, dt: float, events: list, *args, **kwargs):
        super().update(dt, events, args, kwargs)
        self.username_textbox.update(dt, events)
        self.password_textbox.update(dt, events)

        if self.login.update(dt, events):
            self.login_func()

        if self.register.update(dt, events):
            self.register_func()

    def register_func(self):
        response = self.client.send_request("Register", {"Username": self.username_textbox.content, "Password": self.password_textbox.content})
        if response["StatusCode"] == 201:
            self.client.set_token(response["Data"]["Token"])
            self.client.set_data("username", self.username_textbox.content)
            self.client.friends_information = response["Data"]["Friends"]
            self.client.set_data("go_to_home", True)

    def login_func(self):
        response = self.client.send_request("Login", {"Username": self.username_textbox.content, "Password": self.password_textbox.content}, timeout=10)
        if response["StatusCode"] == 200:
            self.client.set_token(response["Data"]["Token"])
            self.client.set_data("username", self.username_textbox.content)
            self.client.friends_information = response["Data"]["Friends"]
            self.client.set_data("go_to_home", True)

    def render(self, *args, **kwargs):
        self.title.render(self.screen)
        self.password_textbox_border.render(self.screen)
        self.username_textbox_border.render(self.screen)
        self.username_textbox.render(self.screen)
        self.password_textbox.render(self.screen)
        self.login.render(self.screen)
        self.register.render(self.screen)
        super().render()

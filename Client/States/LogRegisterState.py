import pygame

from Client.States.BaseState import BaseState
from Client.Components.Text import Text
from Client.Components.Button import Button
from Client.Components.TextBox import TextBox


class LogRegister(BaseState):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        self.title = Text("Login Or Register", "Poppins", 30, False, pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 6), (255, 255, 255))
        self.password_textbox = TextBox(pygame.Vector2(self.screen.get_width() / 3, 60), pygame.Vector2(self.screen.get_width() / 3, 3.5 * self.screen.get_height() / 7), (46, 46, 46), "Enter Password", "Poppins", 16, (226, 226, 226), padding_left=20, padding_right=20, border_radius=10, hidden=True)
        self.username_textbox = TextBox(pygame.Vector2(self.screen.get_width() / 3, 60), pygame.Vector2(self.screen.get_width() / 3, 2.5 * self.screen.get_height() / 7), (46, 46, 46), "Enter Username", "Poppins", 16, (226, 226, 226), padding_left=20, padding_right=20, border_radius=10, next_input=self.password_textbox)
        self.login = Button(pygame.Vector2(self.screen.get_width() / 5, 60), pygame.Vector2((self.screen.get_width() - self.screen.get_width() / 5) / 2 - 10, 5.5 * self.screen.get_height() / 7), (36, 123, 255), "Login", "Poppins", 16, (226, 226, 226), border_radius=10)
        self.register = Button(pygame.Vector2(self.screen.get_width() / 5, 60), pygame.Vector2((self.screen.get_width() + self.screen.get_width() / 5) / 2 + 10, 5.5 * self.screen.get_height() / 7), (36, 123, 255), "Register", "Poppins", 16, (226, 226, 226), border_radius=10)

    def update(self, dt: float, events: list, *args, **kwargs):
        self.username_textbox.update(dt, events)
        self.password_textbox.update(dt, events)
        self.login.update(dt, events)
        self.register.update(dt, events)

    def render(self, *args, **kwargs):
        self.title.render(self.screen)
        self.username_textbox.render(self.screen)
        self.password_textbox.render(self.screen)
        self.login.render(self.screen)
        self.register.render(self.screen)

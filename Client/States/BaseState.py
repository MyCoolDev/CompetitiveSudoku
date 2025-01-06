import pygame

from Client.client import ClientSocket


class BaseState:
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        """
        A state of the gui, a specific screen (one "page").
        """
        self.screen = screen
        self.client = client
        self.__init_vars(screen)

    def __init_vars(self, *args, **kwargs) -> None:
        """
        initiate the vars
        """

    def update(self, dt: float, events: list, *args, **kwargs):
        """
        update the vars for the next render
        :param dt:
        :param events:
        :param args:
        :param kwargs:
        :return:
        """

    def render(self, *args, **kwargs):
        """
        render the state
        :param args:
        :param kwargs:
        :return:
        """

import pygame

from Client.client import ClientSocket


class BaseState:
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        """
        A state of the gui, a specific screen (one "page").
        """
        self.screen = screen
        self.client = client
        self.mouse_cursor = {
            "IBEAM": [],
            "HAND": [],
            "NO": []
        }
        self.last_mouse_pos = pygame.mouse.get_pos()
        self.__init_vars(screen)

    def __init_vars(self, *args, **kwargs) -> None:
        """
        initiate the vars
        """
        pass

    def update(self, dt: float, events: list, *args, **kwargs):
        """
        update the vars for the next render
        :param dt:
        :param events:
        :param args:
        :param kwargs:
        :return:
        """
        if pygame.mouse.get_pos() != self.last_mouse_pos:
            self.update_mouse()

    def update_mouse(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self.last_mouse_pos = pygame.mouse.get_pos()

        for key, values in self.mouse_cursor.items():
            if key == "IBEAM":
                for value in values:
                    if value.is_collide(self.last_mouse_pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                        return
            if key == "HAND":
                for value in values:
                    if value.is_collide(self.last_mouse_pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        return
            if key == "NO":
                for value in values:
                    if value.is_collide(self.last_mouse_pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
                        return

    def render(self, *args, **kwargs):
        """
        render the state
        :param args:
        :param kwargs:
        :return:
        """
        pass

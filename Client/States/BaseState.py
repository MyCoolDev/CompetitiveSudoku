import pygame

from Client.client import ClientSocket
from Client.Components.Notification import Notification


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
        self.notifications = []
        self.notification_base_pos = pygame.Vector2(self.screen.get_width() - 20 - 435, 20)
        self.notification_gap = 10

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

        self.update_notifications(dt, events)

    def update_notifications(self, dt: float, events: list):
        """
        update the notifications on the screen.
        """
        for notification in self.notifications:
            if notification.update(dt, events):
                self.notifications.remove(notification)
                self.client.notifications.remove(notification.interface)

        # update the notification positions and insert new notifications
        self.notifications.clear()

        for i, notification in enumerate(self.client.notifications):
            position = self.notification_base_pos + pygame.Vector2(0, i * (140 + self.notification_gap))
            if notification not in self.notifications:
                self.notifications.append(Notification(notification, position))

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
        for notification in self.notifications:
            notification.render(self.screen)

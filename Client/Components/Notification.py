from Client.default import *
from Client.Components.default_comp import *

class NotificationInterface:
    def __init__(self, title: str, text: str, duration: int = 7, span_color: tuple = (79, 68, 234)):
        self.span_color = span_color
        self.title = title
        self.text = text
        self.duration = duration
        self.time = 0

    def update(self, dt: float) -> bool:
        """
        Update the notification.
        :param dt: the delta time between the last frame and the current frame.
        :return: True if the notification is done, False otherwise.
        """
        self.time += dt

        if self.is_done():
            return True

        return False

    def get_renderable(self, position: Vector2, screen: Surface):
        """
        return a renderable notification object on the screen.
        :param position: The position of the notification to render.
        :param screen: The screen to render on.
        :return:
        """

    def is_done(self):
        return self.time >= self.duration


class Notification:
    def __init__(self, interface: NotificationInterface, position: Vector2):
        self.interface = interface
        self.position = position

        self.box = MonoBehaviour(Vector2(425, 140), position, (36, 36, 39), border_radius=15)
        self.span_box = MonoBehaviour(Vector2(430, 140), position - Vector2(10, 0), interface.span_color, border_radius=15)
        self.title = Text(interface.title, "Bold", 20, position + Vector2(28, 35), (255, 255, 255), top_left_mode=True)
        self.text = Text(interface.text, "Regular", 15, self.title.position + Vector2(0, self.title.text_surface.get_height() + 10), (207, 207, 207), top_left_mode=True)
        self.close_button = Button(Vector2(20, 20), position + Vector2(self.box.size[0] - 20, 20), (255, 0, 0), "", "Poppins", 15, (255, 255, 255), border_radius=10)

    @staticmethod
    def create_notification(position: Vector2, title: str, text: str, duration: int = 5, span_color: tuple = (79, 68, 234)):
        interface = NotificationInterface(title, text, duration, span_color)
        return Notification(interface, position)

    def update(self, dt: float, events: list) -> bool:
        """
        Update the notification.
        :param dt: the delta time between the last frame and the current frame.
        :param events: the events that happened in the last frame.
        :return: True if the notification is done, False otherwise.
        """
        if self.interface.update(dt):
            return True

        if self.close_button.update(dt, events):
            return True

        return False

    def render(self, screen: Surface):
        """
        Render the notification on the screen.
        :param screen: The screen to render on.
        :return:
        """
        self.span_box.render(screen)
        self.box.render(screen)
        self.title.render(screen)
        self.text.render(screen)
        self.close_button.render(screen)

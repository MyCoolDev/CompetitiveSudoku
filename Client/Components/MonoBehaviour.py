import pygame


class MonoBehaviour:
    def __init__(self, size: pygame.Vector2, position: pygame.Vector2, color: tuple, border_width: int = 0,
                 border_radius: int = -1, border_top_left_radius: int = -1, border_top_right_radius: int = -1,
                 border_bottom_left_radius: int = -1, border_bottom_right_radius: int = -1):
        """
        The base class for all the components in the game, a box component.
        :param size: The size of the box.
        :param position: The position of the box.
        :param color: The color of the box.
        :param border_width: The width of the border box, default 0.
        :param border_radius: The radius of the border box, default -1.
        :param border_top_left_radius: The radius of the top left corner, default -1.
        :param border_top_right_radius: The radius of the top right corner, default -1.
        :param border_bottom_left_radius: The radius of the bottom left corner, default -1.
        :param border_bottom_right_radius: The radius of the bottom right corner, default -1.
        """
        self.size = size
        self.position = position
        self.color = color
        self.border_width = border_width
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius

    def update(self, dt: float, events: list):
        """
        Set up a virtual function to update the component.
        :param dt:
        :param events:
        :return:
        """
        pass

    def update_border(self, border_width: int = 0, border_radius: int = -1, border_top_left_radius: int = -1, border_top_right_radius: int = -1, border_bottom_left_radius: int = -1, border_bottom_right_radius: int = -1):
        """
        Update the border of the box.
        :param border_width: The width of the border box, default 0.
        :param border_radius: The radius of the border box, default -1.
        :param border_top_left_radius: The radius of the top left corner, default -1.
        :param border_top_right_radius: The radius of the top right corner, default -1.
        :param border_bottom_left_radius: The radius of the bottom left corner, default -1.
        :param border_bottom_right_radius: The radius of the bottom right corner, default -1.
        :return:
        """
        self.border_width, self.border_radius, self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius = width, border_radius, border_top_left_radius, border_top_right_radius, border_bottom_left_radius, border_bottom_right_radius

    def is_collide(self, mouse_pos: tuple) -> bool:
        return self.position.x <= mouse_pos[0] <= self.position.x + self.size.x and self.position.y <= mouse_pos[1] <= self.position.y + self.size.y

    def render(self, surface: pygame.Surface) -> pygame.Rect or None:
        return pygame.draw.rect(surface, self.color, pygame.Rect(self.position, self.size), self.border_width,
                                self.border_radius, self.border_top_left_radius, self.border_top_right_radius,
                                self.border_bottom_left_radius, self.border_bottom_right_radius)

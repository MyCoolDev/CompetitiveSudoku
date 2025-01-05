import pygame

from Client.Components.MonoBehaviour import MonoBehaviour
from Client.Components.Text import Text


class Button(MonoBehaviour):
    def __init__(self, size: pygame.Vector2, position: pygame.Vector2, color: tuple, content: str, font: str = "", font_size: int = 0, text_color: tuple = (0, 0, 0), top_left_mode=False, width: int = 0, border_radius: int = -1, border_top_left_radius: int = -1, border_top_right_radius: int = -1, border_bottom_left_radius: int = -1, border_bottom_right_radius: int = -1):
        super().__init__(size, position - 1/2 * size + int(top_left_mode) * 1/2 * size, color, width, border_radius, border_top_left_radius, border_top_right_radius, border_bottom_left_radius, border_bottom_right_radius)
        self.rect: pygame.Rect or None = None
        self.content = content
        if content != "":
            self.font_size = font_size
            self.text_color = text_color
            self.text = Text(content, font, font_size, True, position + int(top_left_mode) * 1/2 * size, text_color)

    def is_collide(self, point: tuple):
        return self.rect.collidepoint(point[0], point[1])

    def update(self, dt: float, events: list, function=None) -> None or bool:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.is_collide(mouse_pos):
                    if function is None:
                        return True

        if function is None:
            return False

        return None

    def render(self, surface: pygame.Surface):
        self.rect = super().render(surface)
        if self.content != "":
            self.text.render(surface)
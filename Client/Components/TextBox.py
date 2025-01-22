import pygame

from Client.Components.MonoBehaviour import MonoBehaviour
from Client.Components.Text import Text


class TextBox(MonoBehaviour):
    def __init__(self, size: pygame.Vector2, position: pygame.Vector2, box_color: tuple, default_content: str,
                 font: str,
                 font_size: int, text_color: tuple, padding: tuple = (0, 0, 0, 0), padding_left: int = 0,
                 padding_top: int = 0, padding_right: int = 0, padding_bottom: int = 0, width: int = 0,
                 border_radius: int = -1,
                 border_top_left_radius: int = -1, border_top_right_radius: int = -1,
                 border_bottom_left_radius: int = -1, border_bottom_right_radius: int = -1, next_input=None, hidden=False):
        super().__init__(size, position, box_color, width, border_radius, border_top_left_radius,
                         border_top_right_radius, border_bottom_left_radius, border_bottom_right_radius)

        self.is_focused = False
        self.next_input: TextBox = next_input

        self.rect: pygame.Rect or None = None

        self.padding = [x for x in padding]

        # going to be used only with padding to the left for now

        if padding_left != 0:
            self.padding[0] = padding_left
        if padding_top != 0:
            self.padding[1] = padding_top
        if padding_right != 0:
            self.padding[2] = padding_right
        if padding_bottom != 0:
            self.padding[3] = padding_bottom

        self.default_content = default_content
        self.content = default_content
        self.is_default_content_presented = True
        self.font = font
        self.font_size = font_size
        self.text_color = text_color
        self.text_position = pygame.Vector2(self.position.x + self.padding[0], self.position.y + self.size.y / 2)

        self.text = Text(self.content, self.font, self.font_size, self.text_position, self.text_color,
                         left_mode=True)

        self.hidden = hidden

    def update_text(self, content):
        self.content = content
        if self.content == "":
            self.content = self.default_content
            self.is_default_content_presented = True

        if self.content.startswith(self.default_content) and len(self.content) > len(
                self.default_content) and self.is_default_content_presented:
            self.content = self.content[len(self.default_content):]
            self.is_default_content_presented = False

        if self.content == self.default_content[:-1] and self.is_default_content_presented:
            self.content = self.default_content
            self.is_default_content_presented = True

        text_to_display = self.content

        if not self.is_default_content_presented and self.hidden:
            text_to_display = "*" * len(self.content)

        self.text = Text(text_to_display, self.font, self.font_size, self.text_position, self.text_color,
                         left_mode=True)

    def is_collide(self, point: tuple):
        return self.rect.collidepoint(point[0], point[1])

    def update(self, dt: float, events: list) -> bool:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                self.is_focused = self.is_collide(mouse_pos)
            if self.is_focused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.update_text(self.content[:-1])
                    elif event.key == pygame.K_RETURN and not self.is_default_content_presented:
                        return True
                    elif event.key == pygame.K_TAB:
                        if self.next_input is not None:
                            self.next_input.is_focused = True
                            self.is_focused = False
                    elif event.unicode != "":
                        self.update_text(self.content + event.unicode)

        return False

    def render(self, surface: pygame.Surface) -> pygame.Rect or None:
        self.rect = super().render(surface)
        self.text.render(surface)

        return None

import pygame

pygame.font.init()


class Text:
    def __init__(self, txt: str, font: str, font_size: int, bold: bool, position: pygame.Vector2, color: tuple,
                 alpha=255, top_left_mode=False, left_mode=False, top_mode=False):
        self.txt = txt
        self.font_name = font
        self.font = pygame.font.SysFont(font, font_size, bold)
        self.abs_position = position
        self.font_size = font_size
        self.color = color
        self.text_surface = self.font.render(txt, True, color)

        if top_left_mode:
            self.abs_position = pygame.Vector2(position.x + self.text_surface.get_width() / 2,
                                               position.y + self.text_surface.get_height() / 2)
        elif left_mode:
            self.abs_position = pygame.Vector2(position.x + self.text_surface.get_width() / 2,
                                               position.y)
        elif top_mode:
            self.abs_position = pygame.Vector2(position.x,
                                               position.y + self.text_surface.get_height() / 2)

        self.alpha = alpha
        self.update_alpha()
        self.position = pygame.Vector2(self.abs_position.x - self.text_surface.get_width() / 2,
                                       self.abs_position.y - self.text_surface.get_height() / 2)

    def update_alpha(self):
        self.text_surface.set_alpha(self.alpha)

    def clone(self):
        return Text(self.txt, self.font_name, self.font_size, self.position, self.color)

    def __create_text_surface(self):
        self.text_surface = self.font.render(self.txt, True, self.color)
        self.__generate_position()

    def __generate_position(self):
        self.position = pygame.Vector2(self.abs_position.x - self.text_surface.get_width() / 2,
                                       self.abs_position.y - self.text_surface.get_height() / 2)

    def update_text(self, new_text: str):
        self.txt = new_text
        self.__create_text_surface()

    def update_position(self, position: pygame.Vector2):
        self.abs_position = position

    def update_font_size(self, new_size: int):
        self.font_size = new_size
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.__create_text_surface()

    def update_color(self, color: tuple or pygame.Color):
        self.text_surface = self.font.render(self.txt, True, color)

    def render(self, surface: pygame.Surface):
        surface.blit(self.text_surface, self.position)

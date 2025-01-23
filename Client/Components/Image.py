import pygame


class Image:
    def __init__(self, path, size, position):
        self.path = path
        self.image = pygame.image.load(path)

        self.size = size
        self.position = position

        self.image = pygame.transform.scale(self.image, size)

    def render(self, surface: pygame.Surface) -> pygame.Rect or None:
        surface.blit(self.image, self.position)

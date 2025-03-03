import pygame


class Image:
    def __init__(self, path: str, size: pygame.Vector2, position: pygame.Vector2, rotate: int = 0, centered: bool = False):
        self.path = path
        self.image = pygame.image.load(path)

        self.size = size
        self.position = position

        self.image = pygame.transform.scale(self.image, size)

        self.image = pygame.transform.rotate(self.image, rotate)

        self.centered = centered

    def is_collide(self, point: tuple):
        return self.position.x <= point[0] <= self.position.x + self.size.x and self.position.y <= point[1] <= self.position.y + self.size.y

    def update(self, events: list) -> None or bool:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.is_collide(mouse_pos):
                    return True

            return False

        return None

    def render(self, surface: pygame.Surface) -> pygame.Rect or None:
        surface.blit(self.image, self.position - (pygame.Vector2(self.image.get_width(), self.image.get_height()) / 2 if self.centered else pygame.Vector2(0, 0)))

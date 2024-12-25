import pygame


class App:
    def __init__(self):
        """
        The client application gui using pygame.
        """
        pygame.init()

        self.screen = pygame.display.set_mode((1200, 800))
        self.clock = pygame.time.Clock()
        self.events = None
        self.running = False
        self.dt = 0  # delta time

    def start_client(self):
        """
        Start the client gui.
        """
        self.running = True
        while self.running:
            self.events = pygame.event.get()
            self.handle_events(self.events)
            self.update()
            self.render()

        pygame.quit()

    def handle_events(self, events):
        for event in events:
            # quit event for the close button on the top nav.
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass

    def render(self):
        pygame.display.flip()
        self.dt = self.clock.tick(60) / 1000


if __name__ == '__main__':
    app = App()
    app.start_client()
